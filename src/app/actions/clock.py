import utime
from app.constants import UNIQUE_ID, HASS_DISCOVERY_PREFIX
from app.resources.pixelfont import PixelFont
from app.utils.time import get_time
from app.state import STATE
from app.settings import UTC_OFFSET

MQTT_CLOCK_ID = f'{UNIQUE_ID}_clock'
MQTT_CLOCK_PREFIX = f'{HASS_DISCOVERY_PREFIX}/switch/{MQTT_CLOCK_ID}'

async def show_clock(display, client, visible=True):
    print(f'Clock Visible: {visible}')
    if not visible:
        display.clear()
        display.render()
    STATE['clock.visible'] = visible
    await client.publish(f'{MQTT_CLOCK_PREFIX}/state', 'ON' if STATE['clock.visible'] else 'OFF', retain=True, qos=1)    

async def render_clock(display):
    if not STATE['clock.visible']: return    
    (year, month, day, hour, minute, second, weekday, _) = get_time(utc_offset=UTC_OFFSET)[:8]
    tick_ms = utime.ticks_ms()
    alt_second = second % 2 == 0
    fmt_string = '{:02d} {:02d}'
    now_fmt = fmt_string.format(hour, minute)    
    div_y = int((tick_ms % 1000) / 200) # 0-5 (1/5th sec)
    display.clear()
    display.render_text(PixelFont, now_fmt, y=1, color=(3, 0, 3))    
    display.put_pixel(int(display.columns / 2) - 1, 1 + div_y, 1, 1, 1)
    display.render()