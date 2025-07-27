"""
Config flow for Tuya 8-in-1 Water Quality Tester integration
Enables configuration through user interface
"""

import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN, 
    CONF_DEVICE_ID, 
    CONF_LOCAL_KEY,
    CONF_PROTOCOL_VERSION,
    CONF_SCAN_INTERVAL,
    DEFAULT_PROTOCOL_VERSION,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_ID): cv.string,
        vol.Required(CONF_LOCAL_KEY): cv.string,
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_NAME, default="Tuya 8-in-1 Tester"): cv.string,
        vol.Optional(CONF_PROTOCOL_VERSION, default=DEFAULT_PROTOCOL_VERSION): vol.Coerce(float),
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
    }
)


async def validate_input(hass: HomeAssistant, data: Dict[str, Any]) -> Dict[str, str]:
    """Validate the user input allows us to connect."""
    try:
        import tinytuya
        
        device = tinytuya.Device(
            dev_id=data[CONF_DEVICE_ID],
            address=data[CONF_HOST],
            local_key=data[CONF_LOCAL_KEY],
            version=data.get(CONF_PROTOCOL_VERSION, DEFAULT_PROTOCOL_VERSION)
        )
        
        device.set_socketTimeout(10)
        device.set_socketRetryLimit(2)
        
        # Test connection
        _LOGGER.info(f"Testing connection to {data[CONF_HOST]}...")
        result = await hass.async_add_executor_job(device.status)
        
        if not result:
            raise CannotConnect("No response from device")
        
        if 'Error' in result:
            error_msg = result.get('Error', 'Unknown error')
            error_code = result.get('Err', 'Unknown')
            raise CannotConnect(f"Device error: {error_msg} (code: {error_code})")
        
        if 'dps' not in result:
            raise InvalidData("No DPS data from device")
            
        _LOGGER.info(f"✅ Connection OK - received {len(result['dps'])} DPS")
        return {"title": data.get(CONF_NAME, "Tuya 8-in-1 Tester")}
        
    except ImportError:
        raise CannotConnect("tinytuya library is not installed")
    except Exception as e:
        _LOGGER.error(f"Validation error: {e}")
        raise CannotConnect(f"Connection error: {str(e)}")


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tuya 8-in-1 Water Quality Tester."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                
                # Create unique ID based on device_id
                await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(title=info["title"], data=user_input)
                
            except CannotConnect as e:
                errors["base"] = "cannot_connect"
                _LOGGER.error(f"Cannot connect: {e}")
            except InvalidData as e:
                errors["base"] = "invalid_data"
                _LOGGER.error(f"Invalid data: {e}")
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", 
            data_schema=STEP_USER_DATA_SCHEMA, 
            errors=errors,
            description_placeholders={
                "device_example": "bf70d7388a31ac0421bfyi",
                "key_example": "(!9xO2G6myyUEz.&",
                "ip_example": "192.168.20.161"
            }
        )

    async def async_step_import(self, import_data: Dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        try:
            await validate_input(self.hass, import_data)
            
            # Create unique ID based on device_id
            await self.async_set_unique_id(import_data[CONF_DEVICE_ID])
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(
                title=import_data.get(CONF_NAME, "Tuya 8-in-1 Tester"), 
                data=import_data
            )
        except Exception:
            return self.async_abort(reason="import_failed")

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> "OptionsFlow":
        """Create the options flow."""
        return OptionsFlow(config_entry)


class OptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Tuya 8-in-1."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Manage the options."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            try:
                # Validate new configuration
                test_data = {**self.config_entry.data, **user_input}
                await validate_input(self.hass, test_data)
                
                # Update config entry with new data
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=test_data
                )
                return self.async_create_entry(title="", data={})
                
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidData:
                errors["base"] = "invalid_data"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Show form with current values
        current_data = self.config_entry.data
        options_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=current_data.get(CONF_HOST)): cv.string,
                vol.Required(CONF_DEVICE_ID, default=current_data.get(CONF_DEVICE_ID)): cv.string,
                vol.Required(CONF_LOCAL_KEY, default=current_data.get(CONF_LOCAL_KEY)): cv.string,
                vol.Optional(
                    CONF_PROTOCOL_VERSION, 
                    default=current_data.get(CONF_PROTOCOL_VERSION, DEFAULT_PROTOCOL_VERSION)
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_SCAN_INTERVAL, 
                    default=current_data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                ): cv.positive_int,
            }
        )

        return self.async_show_form(
            step_id="init", 
            data_schema=options_schema, 
            errors=errors,
            description_placeholders={
                "current_host": current_data.get(CONF_HOST, ""),
                "current_device": current_data.get(CONF_DEVICE_ID, "")
            }
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidData(HomeAssistantError):
    """Error to indicate there is invalid data."""
