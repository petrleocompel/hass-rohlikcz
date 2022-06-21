"""GitHub sensor platform."""
from datetime import timedelta
import json
import logging
from typing import Any, Callable, Dict, List, Optional

import async_timeout
from custom_components.rohlik.rohlik_api import RohlikApi


#from aiohttp import ClientError
from homeassistant import config_entries, core
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
import voluptuous as vol


from .const import (
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=10)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)



async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    if config_entry.options:
        config.update(config_entry.options)
    session = async_get_clientsession(hass)
    sensors = []
    if config[CONF_USERNAME] is not None and config[CONF_PASSWORD] is not None:
        api = RohlikApi(session, config[CONF_USERNAME], config[CONF_PASSWORD])
        await api.login()
        sensors.append(RohlikSensor(api, config[CONF_USERNAME]))
    async_add_entities(sensors, update_before_add=True)


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    session = async_get_clientsession(hass)
    sensors = []
    if config[CONF_USERNAME] is not None and config[CONF_PASSWORD] is not None:
        api = RohlikApi(session, config[CONF_USERNAME], config[CONF_PASSWORD])
        await api.login()
        sensors.append(RohlikSensor(api, config[CONF_USERNAME]))
    async_add_entities(sensors, update_before_add=True)


ATTR_UPCOMING_ORDER = "upcoming_order"

class RohlikSensor(Entity):
    """Representation of a Rohlik sensor."""

    def __init__(self, api: RohlikApi, username: str):
        super().__init__()
        self._api = api
        self._user = username
        self._state = None
        self._api = api
        self.attrs = {}
        self._available = True
        self._attr_icon = "mdi:basket"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return "Rohlik upcoming order"

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return "rohlik_upcoming_order"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def device_state_attributes(self) -> dict[str, Any]:
        return self.attrs

    @property
    def extra_state_attributes(self):
        """Return attributes."""
        return self.attrs

    async def async_update(self):
        try:
            with async_timeout.timeout(30):
                resp = await self._api.upcomming_orders()
            if resp.status != 200:
                self._available = False
                _LOGGER.error("%s returned %s", resp.url, resp.status)
                return

            json_response: list = await resp.json()
            _LOGGER.debug("async_update: %s", resp.text)


            self._state = len(json_response) > 0
            self.attrs = {}
            if self._state:
                self.attrs['id'] = json_response[0]['id']
            self._available = True
        except Exception:
            self._available = False
            _LOGGER.exception(
                "Error retrieving data from Rohlik for sensor %s", self.name
            )