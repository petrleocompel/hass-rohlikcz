"""GitHub sensor platform."""
from datetime import timedelta, datetime
import json
import logging
from typing import Any, Callable, Dict, List, Optional

import async_timeout
from homeassistant.core import HomeAssistant, callback
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant import config_entries, core
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity, SensorDeviceClass
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME, STATE_ON, STATE_OFF,
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
from . import RohlikDataUpdateCoordinator

from .const import (
    DOMAIN, DATA_COORDINATOR,
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
    entry: config_entries.ConfigEntry,
    async_add_entities,
):
    coordinator: RohlikDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    sensors = []
    await coordinator.async_request_refresh()
    sensors.append(UpcomingOrderPresenceSensor(coordinator))
    sensors.append(UpcomingOrderDateSensor(coordinator))
    async_add_entities(sensors, update_before_add=True)



ATTR_UPCOMING_ORDER = "upcoming_order"


class UpcomingOrderPresenceSensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True

    """Representation of Hikvision external magnet detector."""
    coordinator: RohlikDataUpdateCoordinator

    def __init__(self, coordinator: RohlikDataUpdateCoordinator) -> None:
        """Create the entity with a DataUpdateCoordinator."""
        super().__init__(coordinator)
        self._attr_unique_id = f"rohlik-upcoming-order-presence"
        self._attr_icon = "mdi:basket"
        self._device_class = BinarySensorDeviceClass.PRESENCE
        self.friendly_name = "Rohlík upcoming order presence"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
        if self.coordinator.upcoming_orders is not None:
            self._attr_is_on = len(self.coordinator.upcoming_orders) > 0
            if self._attr_is_on:
                self._attr_extra_state_attributes = {'id': self.coordinator.upcoming_orders[0].id}
        else:
            self._attr_is_on = None
            self._attr_extra_state_attributes = None


class UpcomingOrderDateSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    
    """Representation of Hikvision external magnet detector."""
    coordinator: RohlikDataUpdateCoordinator

    def __init__(self, coordinator: RohlikDataUpdateCoordinator) -> None:
        """Create the entity with a DataUpdateCoordinator."""
        super().__init__(coordinator)
        self._attr_unique_id = f"rohlik-upcoming-order-date"
        self._attr_icon = "mdi:clock"
        self._device_class = SensorDeviceClass.TIMESTAMP
        self.friendly_name = "Rohlík upcoming order date"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
        if self.coordinator.upcoming_orders is not None and len(self.coordinator.upcoming_orders) > 0 \
                and self.coordinator.upcoming_orders[0].delivery_slot is not None \
                and self.coordinator.upcoming_orders[0].delivery_slot.since is not None:
            self._attr_native_value = datetime.fromisoformat(
                self.coordinator.upcoming_orders[0].delivery_slot.since.split("+")[0]
            )
        else:
            self._attr_native_value = None
