import json
import uasyncio as asyncio
import utime
from app.resources.pixelfont import PixelFont
from app.plugins._base import BasePlugin


class DebugPlugin(BasePlugin):

    DEBUG_COLOR = (255, 0, 0)
    DEBUG_POSITION = (0, 0)

    async def loop(self):
        await self.render_debug()

    async def render_debug(self):
        x, y = self.DEBUG_POSITION
        step = utime.time() % 3
        px_off = (0, 0, 0)
        self.manager.display.render_block(px_off * 3, 1, 3, 0, 0)
        self.manager.display.put_pixel(x + step, y, *self.DEBUG_COLOR)

    """
    render_block(self, data, rows, cols, x, y)
    """
