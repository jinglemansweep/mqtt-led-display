import utime
utime.sleep(2)

import gc
import json
import uasyncio as asyncio

from app.lib.ledmatrix import create_display
from app.utils.debug import led_log
from app.utils.manager import Manager

from app.constants import DEVICE_ID
from app.settings import \
    GPIO_PIN, DISPLAY_ROWS, DISPLAY_COLUMNS, \
    DISPLAY_FPS, DISPLAY_DEBUG
from app.state import STATE

gc.collect()

print('MQTT LED DISPLAY')
print(f'Device ID: {DEVICE_ID}')

display = create_display(
    GPIO_PIN, 
    DISPLAY_ROWS, DISPLAY_COLUMNS, DISPLAY_FPS, DISPLAY_DEBUG
)

STATE["ntp.set"] = False
STATE["connection.outages"] = 0

led_log(display, 'boot')

manager = Manager(display)

try:
    manager.run()
finally:  # Prevent LmacRxBlk:1 errors.
    manager.client.close()
    asyncio.new_event_loop()
