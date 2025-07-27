"""
Constants for Tuya 8-in-1 Water Quality Tester integration
"""

from homeassistant.const import (
    UnitOfTemperature,
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
)

# Fallback for older HA versions
try:
    from homeassistant.const import UnitOfElectricPotential
    MILLIVOLT = UnitOfElectricPotential.MILLIVOLT
except ImportError:
    MILLIVOLT = "mV"

DOMAIN = "tuya_8in1"

# Configuration
CONF_LOCAL_KEY = "local_key"
CONF_PROTOCOL_VERSION = "protocol_version"
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_PROTOCOL_VERSION = 3.5

# Sensor types - UPDATED based on real DPS codes
# Confirmed mappings from device:
SENSOR_TYPES = {
    "temperature": {
        "name": "Temperature",
        "dps_id": 8,  # temp_current: 238 = 23.8°C
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": "temperature",
        "state_class": "measurement",
        "scale": 10,  # Divide by 10
        "icon": "mdi:thermometer",
    },
    "ph": {
        "name": "pH",
        "dps_id": 106,  # ph_current: 790 = 7.90 pH
        "unit": "pH",
        "device_class": None,
        "state_class": "measurement",
        "scale": 100,  # Divide by 100
        "icon": "mdi:test-tube",
    },
    "tds": {
        "name": "TDS",
        "dps_id": 111,  # tds_current: 359 ppm
        "unit": CONCENTRATION_PARTS_PER_MILLION,
        "device_class": None,
        "state_class": "measurement",
        "scale": 1,  # Direct value
        "icon": "mdi:water-opacity",
    },
    "ec": {
        "name": "Conductivity",
        "dps_id": 116,  # ec_current: 718 μS/cm
        "unit": "μS/cm",
        "device_class": None,
        "state_class": "measurement",
        "scale": 1,  # Direct value
        "icon": "mdi:flash",
    },
    "salinity": {
        "name": "Salinity",
        "dps_id": 121,  # salinity_current: 418 = 4.18%
        "unit": PERCENTAGE,
        "device_class": None,
        "state_class": "measurement",
        "scale": 100,  # Divide by 100
        "icon": "mdi:shaker-outline",
    },
    "orp": {
        "name": "ORP",
        "dps_id": 131,  # orp_current: 518 mV
        "unit": MILLIVOLT,
        "device_class": "voltage",
        "state_class": "measurement",
        "scale": 1,  # Direct value
        "icon": "mdi:lightning-bolt",
    },
    "conductivity_factor": {
        "name": "Conductivity Factor",
        "dps_id": 136,  # cf_current: 718
        "unit": None,
        "device_class": None,
        "state_class": "measurement",
        "scale": 1,
        "icon": "mdi:chart-line",
    },
    "pro_sensor": {
        "name": "PRO Sensor",
        "dps_id": 126,  # pro_current: 997 (unknown unit)
        "unit": None,
        "device_class": None,
        "state_class": "measurement",
        "scale": 1,
        "icon": "mdi:help-circle",
    }
}

# Device information
DEVICE_INFO = {
    "identifiers": {(DOMAIN, "tuya_8in1_tester")},
    "name": "Tuya 8-in-1 Water Quality Tester",
    "manufacturer": "Tuya",
    "model": "8-in-1 Water Quality Tester",
    "sw_version": "1.0",
}
