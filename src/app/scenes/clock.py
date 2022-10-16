import json
import uasyncio as asyncio
import utime
from app.resources.pixelfont import PixelFont
from app.scenes._base import BaseScene
from app.settings import UTC_OFFSET
from app.utils.time import get_time


class ClockScene(BaseScene):

    CLOCK_DEFAULT_VISIBILITY = True
    CLOCK_DEFAULT_COLOR = (255, 0, 255)
    CLOCK_DEFAULT_BRIGHTNESS = 48
    CLOCK_BRIGHTNESS_LIMITER = 0.2

    async def initialize(self):
        self.topic_clock_rgb = self.build_mqtt_topic("clock_rgb", "light")
        await self.configure_hass_entity(
            "clock_rgb",
            "light",
            dict(
                color_mode=True,
                supported_color_modes=["rgb"],
                brightness=True,
                brightness_scale=255,
            ),
        )
        await self.manager.client.subscribe(f"{self.topic_clock_rgb}/set", 1)
        await self.update_clock()

    async def loop(self):
        await self.render_clock()

    def on_mqtt_message(self, topic, msg, retain=False):
        if topic == f"{self.topic_clock_rgb}/set":
            obj = json.loads(msg)
            visible = None
            color = None
            brightness = None
            if "state" in obj:
                visible = "on" in obj.get("state").lower()
            if "color" in obj:
                rgb = obj.get("color")
                color = (rgb.get("r"), rgb.get("g"), rgb.get("b"))
            if "brightness" in obj:
                brightness = obj.get("brightness")
            asyncio.create_task(self.update_clock(visible, color, brightness))

    async def update_clock(self, visible=None, color=None, brightness=None):
        print(
            f"update_clock: visible={visible} color={color} brightness={brightness}"
        )
        if visible is None:
            if not "clock.visible" in self.manager.state:
                self.manager.state["clock.visible"] = self.CLOCK_DEFAULT_VISIBILITY
        else:
            if not visible:
                self.manager.display.clear()
                self.manager.display.render()
            self.manager.state["clock.visible"] = visible

        if color is None:
            if not "clock.color" in self.manager.state:
                self.manager.state["clock.color"] = self.CLOCK_DEFAULT_COLOR
        else:
            self.manager.state["clock.color"] = color
        (r, g, b) = self.manager.state["clock.color"]

        if brightness is None:
            if not "clock.brightness" in self.manager.state:
                self.manager.state["clock.brightness"] = self.CLOCK_DEFAULT_BRIGHTNESS
        else:
            self.manager.state["clock.brightness"] = brightness

        updates = {
            "state": "ON" if self.manager.state["clock.visible"] else "OFF",
            "color_mode": "rgb",
            "color": {"r": r, "g": g, "b": b},
            "brightness": self.manager.state["clock.brightness"],
        }
        await self.manager.client.publish(
            f"{self.topic_clock_rgb}/state", json.dumps(updates), retain=True, qos=1
        )

    async def render_clock(self):
        if (
            "clock.visible" not in self.manager.state
            or not self.manager.state["clock.visible"]
        ):
            return
        (year, month, day, hour, minute, second, weekday, _) = get_time(
            utc_offset=UTC_OFFSET
        )[:8]
        tick_ms = utime.ticks_ms()
        alt_second = second % 2 == 0
        fmt_string = "{:02d} {:02d}"
        now_fmt = fmt_string.format(hour, minute)
        div_y = int((tick_ms % 1000) / 200)  # 0-5 (1/5th sec)
        (r, g, b) = self.manager.state["clock.color"]
        brightness = self.manager.state["clock.brightness"] / 255
        adj_r = int((r * brightness) * self.CLOCK_BRIGHTNESS_LIMITER)
        adj_g = int((g * brightness) * self.CLOCK_BRIGHTNESS_LIMITER)
        adj_b = int((b * brightness) * self.CLOCK_BRIGHTNESS_LIMITER)
        self.manager.display.clear()
        self.manager.display.render_text(
            PixelFont, now_fmt, y=1, color=(adj_r, adj_g, adj_b)
        )  # Temp Brightness Hack
        self.manager.display.put_pixel(
            int(self.manager.display.columns / 2) - 1, 1 + div_y, 1, 1, 1
        )
        self.manager.display.render()
