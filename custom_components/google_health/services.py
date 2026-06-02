"""Services for the Google Health integration."""

import datetime
import logging

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .body_fat_calculator import Gender, calculate_body_fat
from .const import DOMAIN, CONF_GENDER, CONF_DOB, CONF_HEIGHT

_LOGGER = logging.getLogger(__name__)

async def async_setup_services(hass: HomeAssistant) -> None:
    """Register services for Google Health."""

    async def _get_entry(hass: HomeAssistant, entry_id: str | None = None):
        """Get the config entry."""
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("No Google Health config entries found.")

        entry = None
        if entry_id:
            for e in entries:
                if getattr(e, "entry_id", None) == entry_id:
                    entry = e
                    break
            if entry is None:
                raise HomeAssistantError(
                    f"No Google Health config entry found with entry_id: {entry_id}"
                )
        else:
            entry = entries[0]

        if not hasattr(entry, "runtime_data") or entry.runtime_data is None:
            raise HomeAssistantError("Google Health integration not ready.")

        return entry

    async def log_body_measurements(call: ServiceCall) -> None:
        """Log body measurements (weight and/or fat)."""
        weight = call.data.get("weight")
        fat = call.data.get("fat")
        impedance = call.data.get("impedance")
        date = call.data.get("date", datetime.date.today())
        time = call.data.get("time", datetime.datetime.now().strftime("%H:%M:%S"))
        entry_id = call.data.get("entry_id")

        if isinstance(time, datetime.time):
            time = time.strftime("%H:%M:%S")

        entry = await _get_entry(hass, entry_id)
        api = entry.runtime_data

        if weight is not None:
            # We assume weight comes in kg from HA based on our services.yaml
            weight_grams = float(weight) * 1000.0
            _LOGGER.debug(
                "Logging weight: %s grams on %s at %s", weight_grams, date, time
            )
            await api.async_log_weight(weight_grams, date, time)

        if fat is None and impedance is not None and weight is not None:
            # Calculate body fat from impedance using local profile options
            options = entry.options
            gender_str = options.get(CONF_GENDER, "MALE")
            dob_str = options.get(CONF_DOB, "1990-01-01")
            height = options.get(CONF_HEIGHT, 175.0)

            birth_date = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()

            try:
                gender = Gender(gender_str.upper())
            except ValueError as exc:
                raise HomeAssistantError(
                    f"Invalid gender: {gender_str}. Must be MALE or FEMALE."
                ) from exc

            fat = calculate_body_fat(
                gender=gender,
                date_of_birth=birth_date,
                weight=float(weight),
                height=float(height),
                impedance=impedance,
            )

            if fat is None:
                raise HomeAssistantError(
                    "Body fat calculation returned None. Check input parameters."
                )

        if fat is not None:
            _LOGGER.debug("Logging body fat: %s on %s at %s", fat, date, time)
            await api.async_log_body_fat(float(fat), date, time)

    hass.services.async_register(DOMAIN, "log_body_measurements", log_body_measurements)
