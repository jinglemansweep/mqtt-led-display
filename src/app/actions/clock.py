import json
import utime
from app.constants import UNIQUE_ID, HASS_DISCOVERY_PREFIX
from app.resources.pixelfont import PixelFont
from app.utils.time import get_time
from app.state import STATE
from app.settings import UTC_OFFSET

MQTT_LIGHT_ID = f'{UNIQUE_ID}_rgb'
MQTT_LIGHT_PREFIX = f'{HASS_DISCOVERY_PREFIX}/light/{MQTT_LIGHT_ID}'

DEFAULT_STATE = True
DEFAULT_COLOR = (64, 0, 64)

async def setup_mqtt(client):
    # Subscriptions
    await client.subscribe(f'{MQTT_LIGHT_PREFIX}/set', 1)
    # Publications
    light_config = dict(
        name=MQTT_LIGHT_ID, unique_id=MQTT_LIGHT_ID, device_class='light',
        schema='json', color_mode=True, brightness=True,
        command_topic=f'{MQTT_LIGHT_PREFIX}/set', state_topic=f'{MQTT_LIGHT_PREFIX}/state',
    )
    await client.publish(f'{MQTT_LIGHT_PREFIX}/config', json.dumps(light_config), retain=True, qos=1)

async def init(display, client):
    await update_clock(display, client, DEFAULT_STATE, DEFAULT_COLOR)

async def update_clock(display, client, visible=None, color=None):
    print(f'Update Clock: visible:{visible}, color:{color}')
    if visible is None:
        if not 'clock.visible' in STATE:
            STATE['clock.visible'] = DEFAULT_STATE
    else:
        if not visible:
            display.clear()
            display.render()
        STATE['clock.visible'] = visible
    if color is None:
        if not 'clock.color' in STATE:
            STATE['clock.color'] = DEFAULT_COLOR
    else:
        STATE['clock.color'] = color
    (r, g, b) = STATE['clock.color']
    updates = { 
        'state': 'ON' if STATE['clock.visible'] else 'OFF',
        'color_mode': 'rgb',
        'color': { 'r': r, 'g': g, 'b': b },
        'brightness': 255
    }
    await client.publish(f'{MQTT_LIGHT_PREFIX}/state', json.dumps(updates), retain=True, qos=1)    

async def render_clock(display):
    if not STATE['clock.visible']: return    
    (year, month, day, hour, minute, second, weekday, _) = get_time(utc_offset=UTC_OFFSET)[:8]
    tick_ms = utime.ticks_ms()
    alt_second = second % 2 == 0
    fmt_string = '{:02d} {:02d}'
    now_fmt = fmt_string.format(hour, minute)    
    div_y = int((tick_ms % 1000) / 200) # 0-5 (1/5th sec)
    (r, g, b) = STATE['clock.color']
    display.clear()
    display.render_text(PixelFont, now_fmt, y=1, color=(int(r / 16), int(g / 16), int(b / 16))) # Temp Brightness Hack
    display.put_pixel(int(display.columns / 2) - 1, 1 + div_y, 1, 1, 1)
    display.render()