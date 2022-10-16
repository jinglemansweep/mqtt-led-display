import json
import uasyncio as asyncio
import utime
from app.resources.pixelfont import PixelFont
from app.plugins._base import BasePlugin
from app.utils.helpers import rgb_dict_to_tuple


class StatusPlugin(BasePlugin):

    STATUS_WIFI_COLOR = dict(r=255, g=0, b=0)
    STATUS_WIFI_POSITION = (0, 8)
    STATUS_MQTT_COLOR = dict(r=255, g=255, b=0)
    STATUS_MQTT_POSITION = (0, 7)

    async def loop(self):
        await self.render_status()

    async def render_status(self):
        wifi = self.manager.state.get("status_wifi")
        mqtt = self.manager.state.get("status_mqtt")
        # print(f"render_status: wifi={wifi} mqtt={mqtt}")
        color_off = (0, 0, 0)
        color_wifi = (
            rgb_dict_to_tuple(self.STATUS_WIFI_COLOR) if not wifi else color_off
        )
        color_mqtt = (
            rgb_dict_to_tuple(self.STATUS_MQTT_COLOR) if not mqtt else color_off
        )
        self.manager.display.put_pixel(*self.STATUS_WIFI_POSITION, *color_wifi)
        self.manager.display.put_pixel(*self.STATUS_MQTT_POSITION, *color_mqtt)
        self.manager.display.render()
