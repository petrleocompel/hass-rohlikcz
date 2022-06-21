
from config.custom_components.rohlik.const import DOMAIN
from custom_components.rohlikcz.sensor import RohlikApi
from homeassistant.const import CONF_AUTHENTICATION, CONF_PASSWORD, CONF_USERNAME
from homeassistant import config_entries, core
import homeassistant.helpers.config_validation as cv
import aiohttp

from typing import Any, Optional

import voluptuous as vol



CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)


class RohlikCustomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Rohlik Custom config flow."""

    data: Optional[dict[str, Any]]

    async def async_step_user(self, user_input: Optional[dict[str, Any]] = None):    
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                RohlikApi(aiohttp.ClientSession() , user_input[CONF_USERNAME], user_input[CONF_PASSWORD])
            except ValueError:
                errors["base"] = "auth"
            if not errors:
                self.data = user_input
                return self.async_create_entry(title="Rohlík", data=self.data, description=self.data[CONF_USERNAME])

        return self.async_show_form(
            step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
        )
