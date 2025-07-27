"""
Tuya 8-in-1 Water Quality Tester - Custom Home Assistant Integration
Integration provides access to all device sensors.
"""

import logging
import asyncio
from datetime import timedelta

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_HOST,
    CONF_NAME,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_LOCAL_KEY,
    CONF_PROTOCOL_VERSION,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_PROTOCOL_VERSION,
    SENSOR_TYPES,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_DEVICE_ID): cv.string,
                vol.Required(CONF_LOCAL_KEY): cv.string,
                vol.Required(CONF_HOST): cv.string,
                vol.Optional(CONF_NAME, default="Tuya 8-in-1 Tester"): cv.string,
                vol.Optional(CONF_PROTOCOL_VERSION, default=DEFAULT_PROTOCOL_VERSION): vol.Coerce(float),
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up integration from configuration.yaml"""
    hass.data.setdefault(DOMAIN, {})
    
    if DOMAIN in config:
        conf = config[DOMAIN]
        # Create config entry from YAML data
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, 
                context={"source": "import"}, 
                data={
                    CONF_DEVICE_ID: conf[CONF_DEVICE_ID],
                    CONF_LOCAL_KEY: conf[CONF_LOCAL_KEY],
                    CONF_HOST: conf[CONF_HOST],
                    CONF_NAME: conf.get(CONF_NAME, "Tuya 8-in-1 Tester"),
                    CONF_PROTOCOL_VERSION: conf.get(CONF_PROTOCOL_VERSION, DEFAULT_PROTOCOL_VERSION),
                    CONF_SCAN_INTERVAL: conf.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                }
            )
        )
    
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration from config entry"""
    device_id = entry.data[CONF_DEVICE_ID]
    local_key = entry.data[CONF_LOCAL_KEY]
    host = entry.data[CONF_HOST]
    protocol_version = entry.data.get(CONF_PROTOCOL_VERSION, DEFAULT_PROTOCOL_VERSION)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    
    coordinator = TuyaDataUpdateCoordinator(
        hass, device_id, local_key, host, protocol_version, scan_interval
    )
    
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload integration"""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok

class TuyaDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for Tuya device"""
    
    def __init__(self, hass: HomeAssistant, device_id: str, local_key: str, host: str, 
                 protocol_version: float = DEFAULT_PROTOCOL_VERSION, 
                 scan_interval: int = DEFAULT_SCAN_INTERVAL):
        """Initialize coordinator"""
        self.device_id = device_id
        self.local_key = local_key
        self.host = host
        self.protocol_version = protocol_version
        self.device = None
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
    
    async def _setup_device(self):
        """Configure device connection"""
        if self.device is None:
            try:
                import tinytuya
                _LOGGER.info(f"Configuring Tuya device...")
                _LOGGER.info(f"Device ID: {self.device_id}")
                _LOGGER.info(f"Host: {self.host}")
                _LOGGER.info(f"Protocol: {self.protocol_version}")
                
                self.device = tinytuya.Device(
                    dev_id=self.device_id,
                    address=self.host,
                    local_key=self.local_key,
                    version=self.protocol_version  # Use configurable version
                )
                
                # Settings for problematic connections
                self.device.set_socketTimeout(15)  # 15s timeout
                self.device.set_socketRetryLimit(3)  # 3 attempts
                self.device.set_socketRetryDelay(2)  # 2s between attempts
                
                _LOGGER.info(f"✅ Configured Tuya device: {self.device_id} (protocol {self.protocol_version})")
                _LOGGER.info(f"🌐 Network: HA(192.168.20.174) -> Device({self.host}:6668)")
                
                # Connection test with additional diagnostics
                try:
                    _LOGGER.info("🔍 Testing connection...")
                    test_data = await self.hass.async_add_executor_job(self.device.status)
                    
                    if test_data and 'dps' in test_data:
                        _LOGGER.info(f"🎯 Connection test OK - received {len(test_data['dps'])} DPS")
                        _LOGGER.debug(f"📊 Test DPS data: {test_data['dps']}")
                    elif test_data and 'Error' in test_data:
                        error_code = test_data.get('Err', 'Unknown')
                        error_msg = test_data.get('Error', 'Unknown error')
                        _LOGGER.error(f"❌ Test - device error: {error_msg} (code: {error_code})")
                        # Don't raise exception, might work in actual use
                    else:
                        _LOGGER.warning(f"⚠️ Connection test - incomplete data: {test_data}")
                        
                except Exception as test_e:
                    _LOGGER.warning(f"⚠️ Connection test failed: {test_e}")
                    _LOGGER.warning(f"📋 Error type: {type(test_e).__name__}")
                    # Continue despite test error - might work in real use
                    
            except Exception as e:
                _LOGGER.error(f"❌ Device connection error: {e}")
                raise UpdateFailed(f"Connection error: {e}")
    
    async def _async_update_data(self):
        """Fetch data from device"""
        await self._setup_device()
        
        if self.device is None:
            raise UpdateFailed("Device was not configured")
        
        try:
            _LOGGER.debug(f"🔄 Attempting connection to {self.host} from HA IP...")
            
            # Additional settings before each connection
            self.device.set_socketTimeout(20)  # Even longer timeout
            self.device.set_socketRetryLimit(3)  # Fewer attempts, but faster
            
            # Add detailed logging before connection
            _LOGGER.info(f"🌐 Connecting: HA(192.168.20.174) -> Tuya({self.host}:6668)")
            _LOGGER.info(f"🔑 Device ID: {self.device_id}, Protocol: {self.protocol_version}")
            
            # Get device status
            data = await self.hass.async_add_executor_job(self.device.status)
            
            _LOGGER.debug(f"📦 Received response: {data}")
            
            if not data:
                _LOGGER.warning("❌ No response from device")
                raise UpdateFailed("No response from device")
            
            if 'Error' in data:
                error_msg = data.get('Error', 'Unknown error')
                error_code = data.get('Err', 'Unknown')
                _LOGGER.error(f"❌ Device error: {error_msg} (code: {error_code})")
                raise UpdateFailed(f"Device error: {error_msg}")
            
            if 'dps' not in data:
                _LOGGER.warning(f"⚠️ No DPS data from device. Received: {data}")
                raise UpdateFailed("No DPS data from device")
            
            # Map DPS data to sensor names
            mapped_data = {}
            dps_data = data['dps']
            
            _LOGGER.debug(f"📊 Received DPS data: {dps_data}")
            
            for sensor_key, sensor_config in SENSOR_TYPES.items():
                dps_id = sensor_config.get('dps_id')
                if dps_id and str(dps_id) in dps_data:
                    raw_value = dps_data[str(dps_id)]
                    
                    # Convert value if needed
                    if 'scale' in sensor_config:
                        value = raw_value / sensor_config['scale']
                    else:
                        value = raw_value
                    
                    mapped_data[sensor_key] = value
                    _LOGGER.debug(f"✅ Mapped {sensor_key}: {raw_value} -> {value}")
                else:
                    _LOGGER.warning(f"⚠️ Missing DPS {dps_id} for sensor {sensor_key}")
            
            _LOGGER.info(f"🎯 Fetched data: {mapped_data}")
            return mapped_data
            
        except Exception as e:
            _LOGGER.error(f"❌ Data fetch error: {e}")
            _LOGGER.error(f"📍 Host: {self.host}, Device ID: {self.device_id}")
            raise UpdateFailed(f"Update error: {e}")
