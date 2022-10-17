import json
import uasyncio as asyncio
import utime
from app.resources.pixelfont import PixelFont
from app.plugins._base import BasePlugin
from app.settings import UTC_OFFSET
from app.utils.helpers import rgb_dict_to_tuple, scale_brightness
from app.utils.time import get_time


class ClockPlugin(BasePlugin):

    CLOCK_DEFAULT_VISIBILITY = True
    CLOCK_DEFAULT_COLOR = dict(r=255, g=0, b=255)
    CLOCK_DEFAULT_BRIGHTNESS = 3
    CLOCK_BRIGHTNESS_SCALE = 16
    CLOCK_OFFSET_X = 2
    CLOCK_OFFSET_Y = 1

    async def initialize(self):
        self.state = dict(
            state="ON" if self.CLOCK_DEFAULT_VISIBILITY else "OFF",
            color=self.CLOCK_DEFAULT_COLOR,
            brightness=self.CLOCK_DEFAULT_BRIGHTNESS,
            color_mode="rgb",
        )
        await self.configure_hass_entity(
            "clock_rgb",
            "light",
            dict(
                color_mode=True,
                supported_color_modes=["rgb"],
                brightness=True,
                brightness_scale=self.CLOCK_BRIGHTNESS_SCALE,
            ),
        )
        self.topic_clock_rgb = self.build_mqtt_topic("clock_rgb", "light")
        await self.manager.client.subscribe(f"{self.topic_clock_rgb}/set", 1)
        await self.update_clock()

    async def loop(self):
        await self.render_clock()

    def on_mqtt_message(self, topic, msg, retain=False):
        if topic == f"{self.topic_clock_rgb}/set":
            obj = json.loads(msg)
            self.state.update(obj)
            asyncio.create_task(self.update_clock())

    async def update_clock(self):
        state = self.state.get("state")
        color = self.state.get("color")
        brightness = self.state.get("brightness")
        print(f"update_clock: state={state} color={color} brightness={brightness}")
        await self.manager.client.publish(
            f"{self.topic_clock_rgb}/state", json.dumps(self.state), retain=True, qos=1
        )

    async def render_clock(self):
        state = self.state.get("state")
        if state == "OFF":
            self.manager.display.clear()
            return
        self._render_time()
        self._render_weekday()
        self._render_second_pulse(8)
        self._render_second_pulse(18)

    def _render_time(self):
        brightness = self.state.get("brightness")
        color = rgb_dict_to_tuple(self.state.get("color"))
        (year, month, day, hour, minute, second, weekday, _) = get_time(
            utc_offset=UTC_OFFSET
        )[:8]
        fmt_string = "{:02d}"
        (r, g, b) = color
        self.manager.display.render_text(
            PixelFont,
            fmt_string.format(hour),
            x=self.CLOCK_OFFSET_X,
            y=self.CLOCK_OFFSET_Y,
            center=False,
            color=(
                scale_brightness(r, brightness, self.CLOCK_BRIGHTNESS_SCALE),
                scale_brightness(g, brightness, self.CLOCK_BRIGHTNESS_SCALE),
                scale_brightness(b, brightness, self.CLOCK_BRIGHTNESS_SCALE),
            ),
        )
        self.manager.display.render_text(
            PixelFont,
            fmt_string.format(minute),
            x=self.CLOCK_OFFSET_X + 10,
            y=self.CLOCK_OFFSET_Y,
            center=False,
            color=(
                scale_brightness(r, brightness, self.CLOCK_BRIGHTNESS_SCALE),
                scale_brightness(g, brightness, self.CLOCK_BRIGHTNESS_SCALE),
                scale_brightness(b, brightness, self.CLOCK_BRIGHTNESS_SCALE),
            ),
        )
        self.manager.display.render_text(
            PixelFont,
            fmt_string.format(second),
            x=self.CLOCK_OFFSET_X + 20,
            y=self.CLOCK_OFFSET_Y,
            center=False,
            color=(
                scale_brightness(r, brightness, self.CLOCK_BRIGHTNESS_SCALE),
                scale_brightness(g, brightness, self.CLOCK_BRIGHTNESS_SCALE),
                scale_brightness(b, brightness, self.CLOCK_BRIGHTNESS_SCALE),
            ),
        )

    def _render_second_pulse(self, x):
        brightness = self.state.get("brightness")
        tick_ms = utime.ticks_ms()
        div_y = int((tick_ms % 1000) / 200)  # 0-5 (1/5th sec)
        for i in range(0, 5):
            self.manager.display.put_pixel(
                self.CLOCK_OFFSET_X + x, self.CLOCK_OFFSET_Y + i, 0x00, 0x00, 0x00
            )
        self.manager.display.put_pixel(
            self.CLOCK_OFFSET_X + x,
            self.CLOCK_OFFSET_Y + div_y,
            scale_brightness(0xFF, brightness, self.CLOCK_BRIGHTNESS_SCALE),
            scale_brightness(0xFF, brightness, self.CLOCK_BRIGHTNESS_SCALE),
            scale_brightness(0xFF, brightness, self.CLOCK_BRIGHTNESS_SCALE),
        )

    def _render_weekday(self):
        brightness = self.state.get("brightness")
        (year, month, day, hour, minute, second, weekday, _) = get_time(
            utc_offset=UTC_OFFSET
        )[:8]
        for i in range(0, 7):
            r = 0xFF if i == weekday else 0x66
            g = 0x00 if i == weekday else 0x00
            b = 0xFF if i == weekday else 0x00
            self.manager.display.put_pixel(
                self.manager.display.columns - 1,
                i,
                scale_brightness(r, brightness, self.CLOCK_BRIGHTNESS_SCALE),
                scale_brightness(g, brightness, self.CLOCK_BRIGHTNESS_SCALE),
                scale_brightness(b, brightness, self.CLOCK_BRIGHTNESS_SCALE),
            )
