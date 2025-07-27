"""
Tuya 8-in-1 Water Quality Tester - Custom Home Assistant Integration
Integracja umożliwiająca dostęp do wszystkich czujników urządzenia.
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
    """Konfiguracja integracji z configuration.yaml"""
    hass.data.setdefault(DOMAIN, {})
    
    if DOMAIN in config:
        conf = config[DOMAIN]
        # Tworzymy config entry z danymi z YAML
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
    """Konfiguracja integracji z config entry"""
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
    """Usuwanie integracji"""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok

class TuyaDataUpdateCoordinator(DataUpdateCoordinator):
    """Koordynator aktualizacji danych z urządzenia Tuya"""
    
    def __init__(self, hass: HomeAssistant, device_id: str, local_key: str, host: str, 
                 protocol_version: float = DEFAULT_PROTOCOL_VERSION, 
                 scan_interval: int = DEFAULT_SCAN_INTERVAL):
        """Inicjalizacja koordynatora"""
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
        """Konfiguruje połączenie z urządzeniem"""
        if self.device is None:
            try:
                import tinytuya
                self.device = tinytuya.Device(
                    dev_id=self.device_id,
                    address=self.host,
                    local_key=self.local_key,
                    version=self.protocol_version  # Używa konfigurowalnej wersji
                )
                _LOGGER.info(f"Połączono z urządzeniem Tuya: {self.device_id} (protocol {self.protocol_version})")
            except Exception as e:
                _LOGGER.error(f"Błąd połączenia z urządzeniem: {e}")
                raise UpdateFailed(f"Błąd połączenia: {e}")
    
    async def _async_update_data(self):
        """Pobiera dane z urządzenia"""
        await self._setup_device()
        
        try:
            # Pobiera status urządzenia
            data = await self.hass.async_add_executor_job(self.device.status)
            
            if not data or 'dps' not in data:
                raise UpdateFailed("Brak danych z urządzenia")
            
            # Mapuje dane DPS na nazwy czujników
            mapped_data = {}
            dps_data = data['dps']
            
            for sensor_key, sensor_config in SENSOR_TYPES.items():
                dps_id = sensor_config.get('dps_id')
                if dps_id and str(dps_id) in dps_data:
                    raw_value = dps_data[str(dps_id)]
                    
                    # Konwersja wartości jeśli potrzebna
                    if 'scale' in sensor_config:
                        value = raw_value / sensor_config['scale']
                    else:
                        value = raw_value
                    
                    mapped_data[sensor_key] = value
            
            _LOGGER.debug(f"Pobrano dane: {mapped_data}")
            return mapped_data
            
        except Exception as e:
            _LOGGER.error(f"Błąd pobierania danych: {e}")
            raise UpdateFailed(f"Błąd aktualizacji: {e}")
