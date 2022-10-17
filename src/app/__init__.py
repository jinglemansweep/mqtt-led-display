import utime

utime.sleep(2)

import gc
import json
import sys
import uasyncio as asyncio

from app.constants import DEVICE_ID, UNIQUE_ID
from app.lib.ledmatrix import create_display
from app.plugins.clock import ClockPlugin
from app.plugins.debug import DebugPlugin
from app.plugins.status import StatusPlugin
from app.resources.icons import SNAKE, POKEMON
from app.utils.helpers import led_log
from app.utils.manager import Manager

gc.collect()

print("MQTT LED DISPLAY")
print(f"Unique ID: {UNIQUE_ID}")

display = create_display()

display.clear()
display.render_block(SNAKE, 8, 8, 4, 0)
display.render_block(POKEMON, 8, 8, 19, 0)
display.render()
# led_log(display, "boot")

manager = Manager(UNIQUE_ID, display)
manager.add_plugin(StatusPlugin)
manager.add_plugin(ClockPlugin)
manager.add_plugin(DebugPlugin)

try:
    manager.run()
finally:  # Prevent LmacRxBlk:1 errors.
    manager.client.close()
    asyncio.new_event_loop()
