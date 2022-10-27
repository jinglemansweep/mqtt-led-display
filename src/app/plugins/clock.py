import json
import uasyncio as asyncio
import utime
from app.constants import UNIQUE_ID
from app.resources.pixelfont import PixelFont
from app.plugins._base import BasePlugin
from app.utils.helpers import rgb_dict_to_tuple, scale_brightness
from app.utils.time import get_time

fmt_string = "{:02d}"


class ClockPlugin(BasePlugin):

    CLOCK_DEFAULT_VISIBILITY = True
    CLOCK_DEFAULT_COLOR = dict(r=0x11, g=0x00, b=0x11)
    CLOCK_DEFAULT_BRIGHTNESS = 8
    CLOCK_DEFAULT_SHOW_SECONDS = True
    CLOCK_DEFAULT_SHOW_WEEKDAYS = True
    CLOCK_BRIGHTNESS_SCALE = 16
    CLOCK_OFFSET_X = 3
    CLOCK_OFFSET_Y = 2

    async def initialize(self):
        self.entities["clock_rgb"] = await self.manager.hass.add_entity(
            "clock_rgb",
            "light",
            dict(
                color_mode=True,
                supported_color_modes=["rgb"],
                brightness=True,
                brightness_scale=self.CLOCK_BRIGHTNESS_SCALE,
            ),
            dict(
                state="ON" if self.CLOCK_DEFAULT_VISIBILITY else "OFF",
                color=self.CLOCK_DEFAULT_COLOR,
                brightness=self.CLOCK_DEFAULT_BRIGHTNESS,
                color_mode="rgb",
            ),
        )
        self.entities["clock_show_seconds"] = await self.manager.hass.add_entity(
            "clock_show_seconds",
            "switch",
            dict(),
            dict(state="ON" if self.CLOCK_DEFAULT_SHOW_SECONDS else "OFF"),
        )
        self.entities["clock_show_weekdays"] = await self.manager.hass.add_entity(
            "clock_show_weekdays",
            "switch",
            dict(),
            dict(state="ON" if self.CLOCK_DEFAULT_SHOW_WEEKDAYS else "OFF"),
        )

    async def loop(self):
        self.render_clock()

    def on_mqtt_message(self, topic, msg, retain=False):
        # MESSAGE: CLOCK_RGB
        entity_clock_rgb = self.entities.get("clock_rgb")
        if topic == entity_clock_rgb.topic_command:
            asyncio.create_task(entity_clock_rgb.update(json.loads(msg)))
        # MESSAGE: CLOCK_SHOW_WEEKDAYS
        entity_clock_show_weekdays = self.entities.get("clock_show_weekdays")
        if topic == entity_clock_show_weekdays.topic_command:
            asyncio.create_task(
                entity_clock_show_weekdays.update(
                    dict(state="ON" if msg == "ON" else "OFF")
                )
            )
        # MESSAGE: CLOCK_SHOW_SECONDS
        entity_clock_show_seconds = self.entities.get("clock_show_seconds")
        if topic == entity_clock_show_seconds.topic_command:
            asyncio.create_task(
                entity_clock_show_seconds.update(
                    dict(state="ON" if msg == "ON" else "OFF")
                )
            )

    def render_clock(self):
        show_clock = self.entities.get("clock_rgb").get_state().get("state") == "ON"
        show_weekdays = (
            self.entities.get("clock_show_weekdays").get_state().get("state") == "ON"
        )
        show_seconds = (
            self.entities.get("clock_show_seconds").get_state().get("state") == "ON"
        )
        now = (year, month, day, hour, minute, second, weekday, _) = get_time()[:8]
        hour_even = hour % 2 == 0
        self._render_time(now, show=show_clock)
        self._render_weekday(now, x=0, show=show_weekdays)
        self._render_weekday(
            now, x=self.manager.display.columns - 1, show=show_weekdays
        )
        self._render_second_pulse(
            self.CLOCK_OFFSET_X + 9, invert=hour_even, show=show_clock
        )
        self._render_second_progress(now, 0, show=show_seconds)

    def _render_time(self, now, show=True):
        entity_clock_rgb = self.entities.get("clock_rgb")
        brightness = entity_clock_rgb.get_state().get("brightness")
        color = rgb_dict_to_tuple(entity_clock_rgb.get_state().get("color"))
        (r, g, b) = color
        (year, month, day, hour, minute, second, weekday, _) = now
        sr = scale_brightness(r, brightness, self.CLOCK_BRIGHTNESS_SCALE)
        sg = scale_brightness(g, brightness, self.CLOCK_BRIGHTNESS_SCALE)
        sb = scale_brightness(b, brightness, self.CLOCK_BRIGHTNESS_SCALE)
        self.manager.display.render_text(
            PixelFont,
            fmt_string.format(hour) if show else "  ",
            x=self.CLOCK_OFFSET_X,
            y=self.CLOCK_OFFSET_Y,
            center=False,
            color=(sr, sg, sb),
        )
        self.manager.display.render_text(
            PixelFont,
            fmt_string.format(minute) if show else "  ",
            x=self.CLOCK_OFFSET_X + 15,
            y=self.CLOCK_OFFSET_Y,
            center=False,
            color=(sr, sg, sb),
        )

    def _render_second_progress(self, now, y=0, show=True):
        entity_clock_rgb = self.entities.get("clock_rgb")
        brightness = entity_clock_rgb.get_state().get("brightness")
        (year, month, day, hour, minute, second, weekday, _) = now
        px_off = (0, 0, 0)
        sr = scale_brightness(0x00, brightness, self.CLOCK_BRIGHTNESS_SCALE)
        sg = scale_brightness(0x00, brightness, self.CLOCK_BRIGHTNESS_SCALE)
        sb = scale_brightness(0xAA, brightness, self.CLOCK_BRIGHTNESS_SCALE)
        self.manager.display.render_block(px_off * 30, 1, 30, 1, y)
        if show:
            self.manager.display.put_pixel(1 + (second % 30), y, sr, sg, sb)

    def _render_second_pulse(self, x, invert=False, show=True):
        brightness = self.entities.get("clock_rgb").get_state().get("brightness")
        tick_ms = utime.ticks_ms()
        div_y = int((tick_ms % 1000) / 200)  # 0-4 (1/5th sec)
        px_off = (0, 0, 0)
        self.manager.display.render_block(
            px_off * (5 * 2), 5, 2, self.CLOCK_OFFSET_X + x, self.CLOCK_OFFSET_Y
        )
        color = scale_brightness(0xFF, brightness, self.CLOCK_BRIGHTNESS_SCALE)
        if show:
            self.manager.display.put_pixel(
                self.CLOCK_OFFSET_X + x,
                self.CLOCK_OFFSET_Y + (div_y if not invert else 4 - div_y),
                color,
                color,
                color,
            )
            self.manager.display.put_pixel(
                self.CLOCK_OFFSET_X + x + 1,
                self.CLOCK_OFFSET_Y + (div_y if not invert else 4 - div_y),
                color,
                color,
                color,
            )

    def _render_weekday(self, now, x, y=0, show=True):
        brightness = self.entities.get("clock_rgb").get_state().get("brightness")
        (year, month, day, hour, minute, second, weekday, _) = now
        px_off = (0, 0, 0)
        px_dark = (0x11, 0, 0)
        r = scale_brightness(0xFF, brightness, self.CLOCK_BRIGHTNESS_SCALE)
        g = scale_brightness(0x00, brightness, self.CLOCK_BRIGHTNESS_SCALE)
        b = scale_brightness(0xFF, brightness, self.CLOCK_BRIGHTNESS_SCALE)
        self.manager.display.render_block((px_off) * 7, 7, 1, x, y)
        if show:
            self.manager.display.render_block(px_dark * 7, 7, 1, x, y)
            self.manager.display.put_pixel(
                x,
                y + weekday,
                r,
                g,
                b,
            )
