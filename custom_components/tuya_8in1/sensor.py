"""
Sensors for Tuya 8-in-1 Water Quality Tester integration
"""

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import TuyaDataUpdateCoordinator
from .const import DOMAIN, SENSOR_TYPES, DEVICE_INFO

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors"""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    device_id = config_entry.data[CONF_DEVICE_ID]
    device_name = config_entry.data.get(CONF_NAME, "Tuya 8-in-1 Tester")
    
    entities = []
    
    # Create sensor entities
    for sensor_key, sensor_config in SENSOR_TYPES.items():
        entities.append(
            Tuya8in1Sensor(
                coordinator,
                device_id,
                device_name,
                sensor_key,
                sensor_config,
            )
        )
    
    async_add_entities(entities)

class Tuya8in1Sensor(CoordinatorEntity, SensorEntity):
    """Representation of a Tuya 8-in-1 sensor"""
    
    def __init__(
        self,
        coordinator: TuyaDataUpdateCoordinator,
        device_id: str,
        device_name: str,
        sensor_key: str,
        sensor_config: dict,
    ) -> None:
        """Initialize the sensor"""
        super().__init__(coordinator)
        
        self._device_id = device_id
        self._device_name = device_name
        self._sensor_key = sensor_key
        self._sensor_config = sensor_config
        
        # Unique entity ID
        self._attr_unique_id = f"{device_id}_{sensor_key}"
        
        # Sensor name
        self._attr_name = f"{device_name} {sensor_config['name']}"
        
        # Unit of measurement
        self._attr_native_unit_of_measurement = sensor_config.get("unit")
        
        # Device class
        self._attr_device_class = sensor_config.get("device_class")
        
        # State class
        self._attr_state_class = sensor_config.get("state_class")
        
        # Icon
        self._attr_icon = sensor_config.get("icon")
        
        # Device information
        self._attr_device_info = DEVICE_INFO.copy()
        self._attr_device_info["identifiers"] = {(DOMAIN, device_id)}
        self._attr_device_info["name"] = device_name
    
    @property
    def native_value(self) -> Any:
        """Return the current sensor value"""
        if self.coordinator.data is None:
            return None
        
        return self.coordinator.data.get(self._sensor_key)
    
    @property
    def available(self) -> bool:
        """Return sensor availability information"""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self._sensor_key in self.coordinator.data
        )
    
    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes"""
        if not self.coordinator.data:
            return None
        
        attrs = {
            "device_id": self._device_id,
            "sensor_type": self._sensor_key,
            "dps_id": self._sensor_config.get("dps_id"),
        }
        
        # Add last update information
        if self.coordinator.last_update_success:
            attrs["last_update_success"] = self.coordinator.last_update_success
        
        return attrs
