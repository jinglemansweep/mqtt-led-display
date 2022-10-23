import json
from app.resources.pixelfont import PixelFont
from app.plugins._base import BasePlugin
from app.utils.system import uasyncio, utime
from app.utils.time import get_time


class DebugPlugin(BasePlugin):

    DEBUG_COLOR = (0, 0, 127)
    DEBUG_POSITION = (1, 0)

    async def loop(self):
        await self.render_debug()
        self.manager.display.render()

    async def render_debug(self):
        x, y = self.DEBUG_POSITION
        now = (year, month, day, hour, minute, second, weekday, _) = get_time()[:8]
        px_off = (0, 0, 0)
        self.manager.display.render_block(px_off * 30, 1, 30, x, y)
        self.manager.display.put_pixel(x + (second % 30), y, *self.DEBUG_COLOR)

    """
    render_block(self, data, rows, cols, x, y)
    """
