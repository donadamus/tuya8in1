"""
Config flow dla integracji Tuya 8-in-1 Water Quality Tester
"""

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_DEVICE_ID, CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_LOCAL_KEY

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_ID): cv.string,
        vol.Required(CONF_LOCAL_KEY): cv.string,
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_NAME, default="Tuya 8-in-1 Tester"): cv.string,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Waliduje dane wejściowe"""
    
    # Próba połączenia z urządzeniem
    try:
        import tinytuya
        
        device = tinytuya.Device(
            dev_id=data[CONF_DEVICE_ID],
            address=data[CONF_HOST],
            local_key=data[CONF_LOCAL_KEY],
            version=3.5  # ZAKTUALIZOWANE: Potwierdzona działająca wersja
        )
        
        # Test połączenia
        status = await hass.async_add_executor_job(device.status)
        
        if not status or 'dps' not in status:
            raise Exception("Brak odpowiedzi z urządzenia")
        
        _LOGGER.info(f"Pomyślnie połączono z urządzeniem: {data[CONF_DEVICE_ID]}")
        
    except Exception as e:
        _LOGGER.error(f"Błąd połączenia z urządzeniem: {e}")
        raise Exception(f"Nie można połączyć się z urządzeniem: {e}")
    
    return {"title": data[CONF_NAME]}

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow dla Tuya 8-in-1"""
    
    VERSION = 1
    
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Krok konfiguracji użytkownika"""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )
        
        errors = {}
        
        try:
            info = await validate_input(self.hass, user_input)
        except Exception as e:
            errors["base"] = "cannot_connect"
            _LOGGER.error(f"Błąd walidacji: {e}")
        else:
            # Sprawdza czy urządzenie już zostało dodane
            await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(title=info["title"], data=user_input)
        
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
    
    async def async_step_import(self, user_input: dict[str, Any]) -> FlowResult:
        """Import z configuration.yaml"""
        return await self.async_step_user(user_input)
