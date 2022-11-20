"""Init"""
import asyncio
import json
import logging
from datetime import timedelta
from typing import Any, Dict, Optional, List
from async_timeout import timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DATA_COORDINATOR
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .rohlik_api import RohlikApi
from .model import UpcomingOrder, upcoming_order_from_dict
from homeassistant.helpers.aiohttp_client import HassClientResponse


_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up rohlik integration from a config entry."""
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    """Set up platform from a ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass)
    api = RohlikApi(session, username, password)
    try:
        async with timeout(10):
            await api.login()
    except (asyncio.TimeoutError, ConnectionError) as ex:
        raise ConfigEntryNotReady from ex

    coordinator = RohlikDataUpdateCoordinator(hass, api)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {DATA_COORDINATOR: coordinator}

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class RohlikDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Rohlik data."""
    api: RohlikApi

    upcoming_orders: Optional[List[UpcomingOrder]] = None

    def __init__(
        self,
        hass,
        api: RohlikApi,
    ):
        self.api = api
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(minutes=10))

    async def _update_data(self) -> None:
        """Fetch data from Rohlik via sync functions."""
        response: HassClientResponse = await self.api.upcomming_orders()

        self.upcoming_orders = upcoming_order_from_dict(json.loads(await response.text()))
        _LOGGER.debug("Rohlik upcoming orders: %s", self.upcoming_orders)

    async def _async_update_data(self) -> None:
        """Fetch data from Rohlik."""
        try:
            async with timeout(10):
                await self._update_data()
        except ConnectionError as error:
            raise UpdateFailed(error) from error
