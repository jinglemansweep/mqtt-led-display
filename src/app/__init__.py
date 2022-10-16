import utime
utime.sleep(2)

import gc
import json
import uasyncio as asyncio

from app.constants import DEVICE_ID, UNIQUE_ID
from app.lib.ledmatrix import create_display
from app.scenes.clock import ClockScene
from app.settings import \
    GPIO_PIN, DISPLAY_ROWS, DISPLAY_COLUMNS, \
    DISPLAY_FPS, DISPLAY_DEBUG
from app.utils.debug import led_log
from app.utils.manager import Manager

gc.collect()

print('MQTT LED DISPLAY')
print(f'Unique ID: {UNIQUE_ID}')

display = create_display(
    GPIO_PIN, 
    DISPLAY_ROWS, DISPLAY_COLUMNS, DISPLAY_FPS, DISPLAY_DEBUG
)

led_log(display, 'boot')

manager = Manager(UNIQUE_ID, display)
manager.add_scene(ClockScene)

try:
    manager.run()
finally:  # Prevent LmacRxBlk:1 errors.
    manager.client.close()
    asyncio.new_event_loop()
