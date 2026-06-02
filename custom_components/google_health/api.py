import aiohttp
import datetime
from homeassistant.helpers.config_entry_oauth2_flow import OAuth2Session

class GoogleHealthAPI:
    def __init__(self, websession: aiohttp.ClientSession, oauth_session: OAuth2Session):
        """Initialize the API client."""
        self.websession = websession
        self.oauth_session = oauth_session

    async def _request(self, method: str, url: str, **kwargs):
        """Make an authenticated request to the Google Health API."""
        await self.oauth_session.async_ensure_token_valid()
        token = self.oauth_session.token["access_token"]
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        kwargs["headers"] = headers

        async with self.websession.request(method, url, **kwargs) as resp:
            if resp.status >= 400:
                text = await resp.text()
                raise ValueError(f"Google Health API Error {resp.status}: {text}")
            
            # If the response is not empty, return the JSON
            # 204 No Content won't have a json
            if resp.status != 204:
                return await resp.json()
            return None

    def _get_sample_time(self, date_val: datetime.date, time_val: str) -> dict:
        """Construct the ObservationSampleTime dict."""
        dt = datetime.datetime.strptime(f"{date_val} {time_val}", "%Y-%m-%d %H:%M:%S")
        local_dt = dt.astimezone()
        utc_dt = local_dt.astimezone(datetime.timezone.utc)
        utc_offset_seconds = local_dt.utcoffset().total_seconds()
        
        return {
            "physicalTime": utc_dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "utcOffset": f"{int(utc_offset_seconds)}s"
        }

    async def async_log_weight(self, weight_grams: float, date: datetime.date, time: str):
        """Log weight to Google Health."""
        payload = {
            "weight": {
                "weightGrams": weight_grams,
                "sampleTime": self._get_sample_time(date, time)
            }
        }
        
        url = "https://health.googleapis.com/v4/users/me/dataTypes/weight/dataPoints"
        return await self._request("POST", url, json=payload)

    async def async_log_body_fat(self, percentage: float, date: datetime.date, time: str):
        """Log body fat percentage to Google Health."""
        payload = {
            "bodyFat": {
                "percentage": percentage,
                "sampleTime": self._get_sample_time(date, time)
            }
        }
        
        url = "https://health.googleapis.com/v4/users/me/dataTypes/body-fat/dataPoints"
        return await self._request("POST", url, json=payload)
