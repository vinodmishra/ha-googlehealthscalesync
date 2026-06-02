import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers import selector

from .const import DOMAIN, CONF_GENDER, CONF_DOB, CONF_HEIGHT, OAUTH2_SCOPES

from homeassistant.config_entries import SOURCE_REAUTH

from homeassistant.const import CONF_NAME

def _get_profile_schema(options: dict, is_setup: bool = False) -> vol.Schema:
    """Return the schema for the profile data."""
    schema = {}

    if is_setup:
        schema[vol.Required(CONF_NAME)] = selector.TextSelector()

    gender_key = vol.Required(CONF_GENDER, default=options[CONF_GENDER]) if CONF_GENDER in options else vol.Required(CONF_GENDER)
    schema[gender_key] = selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=[
                selector.SelectOptionDict(value="MALE", label="Male"),
                selector.SelectOptionDict(value="FEMALE", label="Female"),
            ],
            mode=selector.SelectSelectorMode.LIST,
        )
    )

    dob_key = vol.Required(CONF_DOB, default=options[CONF_DOB]) if CONF_DOB in options else vol.Required(CONF_DOB)
    schema[dob_key] = selector.TextSelector()

    height_key = vol.Required(CONF_HEIGHT, default=options[CONF_HEIGHT]) if CONF_HEIGHT in options else vol.Required(CONF_HEIGHT)
    schema[height_key] = selector.TextSelector(
        selector.TextSelectorConfig(type=selector.TextSelectorType.NUMBER)
    )

    return vol.Schema(schema)

class OAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Config flow to handle Google Health OAuth2 authentication."""

    DOMAIN = DOMAIN

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return logging.getLogger(__name__)

    @property
    def extra_authorize_data(self) -> dict:
        """Extra data that needs to be appended to the authorize url."""
        return {
            "scope": " ".join(OAUTH2_SCOPES),
            "access_type": "offline",
            "prompt": "consent",
        }

    async def async_oauth_create_entry(self, data: dict):
        """Intercept the entry creation to ask for profile data first."""
        if self.source == SOURCE_REAUTH:
            # We don't want to show the profile step on reauth.
            return self.async_create_entry(title=self.flow_impl.name, data=data)
        
        self.oauth_data = data
        return await self.async_step_profile()

    async def async_step_profile(self, user_input=None):
        """Handle the profile data step."""
        errors = {}
        if user_input is not None:
            import datetime
            try:
                datetime.datetime.strptime(user_input[CONF_DOB], "%Y-%m-%d")
                # Ensure height is saved as a float
                user_input[CONF_HEIGHT] = float(user_input[CONF_HEIGHT])
                account_name = user_input.pop(CONF_NAME)
                return self.async_create_entry(
                    title=account_name, 
                    data=self.oauth_data,
                    options=user_input
                )
            except ValueError:
                errors["base"] = "invalid_date"

        return self.async_show_form(
            step_id="profile",
            data_schema=_get_profile_schema({}, is_setup=True),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler()


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for Google Health."""

    def __init__(self) -> None:
        """Initialize options flow."""
        pass

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}
        if user_input is not None:
            import datetime
            try:
                datetime.datetime.strptime(user_input[CONF_DOB], "%Y-%m-%d")
                user_input[CONF_HEIGHT] = float(user_input[CONF_HEIGHT])
                return self.async_create_entry(title="", data=user_input)
            except ValueError:
                errors["base"] = "invalid_date"

        options = self.config_entry.options

        return self.async_show_form(
            step_id="init",
            data_schema=_get_profile_schema(options),
            errors=errors,
        )
