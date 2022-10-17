import json
import uasyncio as asyncio
import utime
from app.resources.pixelfont import PixelFont
from app.plugins._base import BasePlugin
from app.settings import UTC_OFFSET
from app.utils.helpers import rgb_dict_to_tuple, scale_brightness
from app.utils.time import get_time

fmt_string = "{:02d}"


class ClockPlugin(BasePlugin):

    CLOCK_DEFAULT_VISIBILITY = True
    CLOCK_DEFAULT_COLOR = dict(r=255, g=0, b=255)
    CLOCK_DEFAULT_BRIGHTNESS = 3
    CLOCK_BRIGHTNESS_SCALE = 16
    CLOCK_OFFSET_X = 2
    CLOCK_OFFSET_Y = 1

    async def initialize(self):
        self.state = dict(
            clock_rgb=dict(
                state="ON" if self.CLOCK_DEFAULT_VISIBILITY else "OFF",
                color=self.CLOCK_DEFAULT_COLOR,
                brightness=self.CLOCK_DEFAULT_BRIGHTNESS,
                color_mode="rgb",
            )
        )
        self.topics["clock_rgb"] = await self.manager.hass.advertise_entity(
            "clock_rgb",
            "light",
            dict(
                color_mode=True,
                supported_color_modes=["rgb"],
                brightness=True,
                brightness_scale=self.CLOCK_BRIGHTNESS_SCALE,
            ),
        )
        await self.update_state_clock_rgb()

    async def loop(self):
        await self.render_clock()

    def on_mqtt_message(self, topic, msg, retain=False):
        # MESSAGE: CLOCK_RGB
        _, clock_rgb_command_topic = self.topics["clock_rgb"]
        if topic == f"{clock_rgb_command_topic}":
            try:
                obj = json.loads(msg)
                asyncio.create_task(self.update_state_clock_rgb(obj))
            except:
                print("mqtt: json parse error")

    async def update_state_clock_rgb(self, state=None):
        if state is not None:
            self.state["clock_rgb"].update(state)
        state_topic, _ = self.topics["clock_rgb"]
        await self.manager.client.publish(
            state_topic, json.dumps(self.state["clock_rgb"]), retain=True, qos=1
        )

    async def render_clock(self):
        state = self.state["clock_rgb"]["state"]
        if state == "OFF":
            self.manager.display.clear()
            return
        now = (year, month, day, hour, minute, second, weekday, _) = get_time(
            utc_offset=UTC_OFFSET
        )[:8]
        min_even = minute % 2 == 0
        self._render_time(now)
        self._render_weekday(now)
        self._render_second_pulse(8, invert=min_even)
        self._render_second_pulse(18, invert=not min_even)

    def _render_time(self, now):
        (year, month, day, hour, minute, second, weekday, _) = now
        brightness = self.state["clock_rgb"]["brightness"]
        color = rgb_dict_to_tuple(self.state["clock_rgb"]["color"])
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

    def _render_second_pulse(self, x, invert=False):
        brightness = self.state["clock_rgb"]["brightness"]
        tick_ms = utime.ticks_ms()
        div_y = int((tick_ms % 1000) / 200)  # 0-4 (1/5th sec)
        px_off = (0, 0, 0)
        self.manager.display.render_block(
            px_off * 5, 5, 1, self.CLOCK_OFFSET_X + x, self.CLOCK_OFFSET_Y
        )
        self.manager.display.put_pixel(
            self.CLOCK_OFFSET_X + x,
            self.CLOCK_OFFSET_Y + (div_y if not invert else 4 - div_y),
            scale_brightness(0xFF, brightness, self.CLOCK_BRIGHTNESS_SCALE),
            scale_brightness(0xFF, brightness, self.CLOCK_BRIGHTNESS_SCALE),
            scale_brightness(0xFF, brightness, self.CLOCK_BRIGHTNESS_SCALE),
        )

    def _render_weekday(self, now):
        (year, month, day, hour, minute, second, weekday, _) = now
        brightness = self.state["clock_rgb"]["brightness"]
        px_dark = (0x66, 0, 0)
        px_weekday = (0xFF, 0, 0xFF)
        self.manager.display.render_block(
            px_dark * 7, 7, 1, self.manager.display.columns - 1, 0
        )
        r, g, b = px_weekday
        self.manager.display.put_pixel(
            self.manager.display.columns - 1,
            weekday,
            scale_brightness(r, brightness, self.CLOCK_BRIGHTNESS_SCALE),
            scale_brightness(g, brightness, self.CLOCK_BRIGHTNESS_SCALE),
            scale_brightness(b, brightness, self.CLOCK_BRIGHTNESS_SCALE),
        )
