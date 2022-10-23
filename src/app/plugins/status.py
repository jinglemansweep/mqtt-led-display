import json
from app.resources.pixelfont import PixelFont
from app.plugins._base import BasePlugin
from app.utils.system import uasyncio, utime


class StatusPlugin(BasePlugin):

    STATUS_WIFI_COLOR = (255, 0, 0)
    STATUS_WIFI_POSITION = (0, 8)
    STATUS_MQTT_COLOR = (255, 255, 0)
    STATUS_MQTT_POSITION = (0, 7)

    async def loop(self):
        if all(
            [
                self.manager.state.get("status_wifi"),
                self.manager.state.get("status_mqtt"),
            ]
        ):
            return
        await self.render_status()

    async def render_status(self):
        wifi = self.manager.state.get("status_wifi")
        mqtt = self.manager.state.get("status_mqtt")
        # print(f"render_status: wifi={wifi} mqtt={mqtt}")
        color_off = (0, 0, 0)
        color_wifi = self.STATUS_WIFI_COLOR if not wifi else color_off
        color_mqtt = self.STATUS_MQTT_COLOR if not mqtt else color_off
        (x_wifi, y_wifi) = self.STATUS_WIFI_POSITION
        (x_mqtt, y_mqtt) = self.STATUS_MQTT_POSITION
        self.manager.display.put_pixel(x_wifi, y_wifi, *color_wifi)
        self.manager.display.put_pixel(x_mqtt, y_mqtt, *color_mqtt)
