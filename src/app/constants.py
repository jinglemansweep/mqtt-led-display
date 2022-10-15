import ubinascii
from machine import unique_id

def _get_device_id():
    return ubinascii.hexlify(unique_id()).decode('utf-8')

DEVICE_ID = _get_device_id()
UNIQUE_ID = f'mqttpanel{DEVICE_ID}';
HASS_DISCOVERY_PREFIX = 'homeassistant'
