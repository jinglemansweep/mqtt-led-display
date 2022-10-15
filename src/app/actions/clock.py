import json
import utime
from app.constants import UNIQUE_ID, HASS_DISCOVERY_PREFIX
from app.resources.pixelfont import PixelFont
from app.utils.time import get_time
from app.state import STATE
from app.settings import UTC_OFFSET

MQTT_LIGHT_ID = f'{UNIQUE_ID}_rgb'
MQTT_LIGHT_PREFIX = f'{HASS_DISCOVERY_PREFIX}/light/{MQTT_LIGHT_ID}'

DEFAULT_VISIBILITY = True
DEFAULT_COLOR = (255, 0, 255)
DEFAULT_BRIGHTNESS = 48

BRIGHTNESS_LIMITER = 0.2

async def setup_mqtt(client):
    # Subscriptions
    await client.subscribe(f'{MQTT_LIGHT_PREFIX}/set', 1)
    # Publications
    light_config = dict(
        name=MQTT_LIGHT_ID, unique_id=MQTT_LIGHT_ID, device_class='light',
        schema='json', color_mode=True, brightness=True, brightness_scale=255,
        command_topic=f'{MQTT_LIGHT_PREFIX}/set', state_topic=f'{MQTT_LIGHT_PREFIX}/state',
    )
    await client.publish(f'{MQTT_LIGHT_PREFIX}/config', json.dumps(light_config), retain=True, qos=1)

async def init(display, client):
    await update_clock(display, client, DEFAULT_VISIBILITY, DEFAULT_COLOR, DEFAULT_BRIGHTNESS)

async def update_clock(display, client, visible=None, color=None, brightness=None):
    print(f'Update Clock: visible:{visible}, color:{color}, brightness:{brightness}')
    if visible is None:
        if not 'clock.visible' in STATE:
            STATE['clock.visible'] = DEFAULT_VISIBILITY
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

    if brightness is None:
        if not 'clock.brightness' in STATE:
            STATE['clock.brightness'] = DEFAULT_BRIGHTNESS
    else:
        STATE['clock.brightness'] = brightness

    updates = { 
        'state': 'ON' if STATE['clock.visible'] else 'OFF',
        'color_mode': 'rgb',
        'color': { 'r': r, 'g': g, 'b': b },
        'brightness': STATE['clock.brightness']
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
    brightness = STATE['clock.brightness'] / 255
    adj_r = int((r * brightness) * BRIGHTNESS_LIMITER)
    adj_g = int((g * brightness) * BRIGHTNESS_LIMITER)
    adj_b = int((b * brightness) * BRIGHTNESS_LIMITER)
    display.clear()
    display.render_text(PixelFont, now_fmt, y=1, color=(adj_r, adj_g, adj_b)) # Temp Brightness Hack
    display.put_pixel(int(display.columns / 2) - 1, 1 + div_y, 1, 1, 1)
    display.render()