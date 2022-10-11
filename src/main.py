import utime
utime.sleep(2)

import gc
import json
import machine
import uasyncio as asyncio

from lib.mqttas import MQTTClient, config
from lib.ledmatrix import LedMatrix
from lib.hal import HAL
from pixelfont import PixelFont
from utils import led_log, get_device_id, get_time, ntp_update
from secrets import WIFI_KEY, WIFI_SSID, MQTT_HOST, MQTT_PORT, MQTT_SSL, MQTT_CLIENT_ID, MQTT_USERNAME, MQTT_PASSWORD, UTC_OFFSET

gc.collect()

GPIO_PIN = 16
DISPLAY_ROWS = 8
DISPLAY_COLUMNS = 32
DISPLAY_FPS = 10
DISPLAY_DEBUG = False
DISPLAY_INTENSITY = 2

DEVICE_ID = get_device_id()
UNIQUE_ID = f'mqttpanel{DEVICE_ID}';
HASS_DISCOVERY_PREFIX = 'homeassistant'
MQTT_CLOCK_ID = f'{UNIQUE_ID}_clock'
MQTT_CLOCK_PREFIX = f'{HASS_DISCOVERY_PREFIX}/switch/{MQTT_CLOCK_ID}'
MQTT_TEXT_ID = f'{UNIQUE_ID}_text'
MQTT_TEXT_PREFIX = f'{HASS_DISCOVERY_PREFIX}/text/{MQTT_TEXT_ID}'

print('MQTT LED DISPLAY')
print(f'Device ID: {DEVICE_ID}')

driver = HAL(gpio_pin=GPIO_PIN, pixel_count=(DISPLAY_ROWS * DISPLAY_COLUMNS))

display = LedMatrix(
    driver,
    rows=DISPLAY_ROWS,
    columns=DISPLAY_COLUMNS,
    fps=DISPLAY_FPS,
    debug=DISPLAY_DEBUG
)

ntp_success = False
clock_visible = False
outages = 0

led_log(display, 'boot')

async def echo(msg):
    print(f'ECHO: {msg}')

async def show_clock(visible, client):
    global clock_visible
    print(f'Clock Visible: {visible}')
    if not visible:
        display.clear()
        display.render()
    clock_visible = visible
    await client.publish(f'{MQTT_CLOCK_PREFIX}/state', 'ON' if clock_visible else 'OFF', retain=True, qos=1)    

async def render_clock():
    global display, clock_visible
    if not clock_visible: return    
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

async def render_message(msg):
    global clock_visible
    print(f'RENDER MESSAGE: {msg}')
    clock_visible = False
    display.hscroll(-1)
    await asyncio.sleep(1)
    words = msg.split(' ')
    for i, word in enumerate(words):
        display.render_text(PixelFont, word, y=1)
        display.render()        
        if i < len(words) - 1:
            await asyncio.sleep(2)     
            display.fade()            
    await asyncio.sleep(2)
    display.hscroll(-1)
    await asyncio.sleep(1)
    clock_visible = True

async def handle_wifi(state):
    global outages
    if state:
        led_log(display, 'wifi')
        print('Status: Connected')
    else:
        outages += 1
        print('Status: Not Connected')
    await asyncio.sleep(1)


async def setup_hass(client):
    global clock_visible
    # Clock switch
    await client.subscribe(f'{MQTT_CLOCK_PREFIX}/set', 1)
    config = dict(
        name=MQTT_CLOCK_ID, unique_id=MQTT_CLOCK_ID, device_class='switch',
        command_topic=f'{MQTT_CLOCK_PREFIX}/set', state_topic=f'{MQTT_CLOCK_PREFIX}/state',
    )
    await client.publish(f'{MQTT_CLOCK_PREFIX}/config', json.dumps(config), retain=True, qos=1)
    await client.publish(f'{MQTT_CLOCK_PREFIX}/state', 'ON' if clock_visible else 'OFF', retain=True, qos=1)
    # Text switch
    await client.subscribe(f'{MQTT_TEXT_PREFIX}/set', 1)
    # config = dict(
    #     name=MQTT_TEXT_ID, unique_id=MQTT_TEXT_ID, device_class='switch',
    #     command_topic=f'{MQTT_TEXT_PREFIX}/set', state_topic=f'{MQTT_TEXT_PREFIX}/state',
    # )
    # await client.publish(f'{MQTT_TEXT_PREFIX}/config', json.dumps(config), retain=True, qos=1)
    # await client.publish(f'{MQTT_TEXT_PREFIX}/state', 'ON' if clock_visible else 'OFF', retain=True, qos=1)

async def handle_connection(client):
    await setup_hass(client)


def on_message(_topic, _msg, retained, client):
    topic = _topic.decode()
    msg = _msg.decode()
    print(f'Topic: "{topic}" Message: "{msg}" Retained: {retained}')
    if topic == f'{MQTT_CLOCK_PREFIX}/set':
        visible = 'on' in str(msg).lower()
        asyncio.create_task(show_clock(visible, client))
    if topic == f'{MQTT_TEXT_PREFIX}/set':
        asyncio.create_task(render_message(msg))        

async def main(client):
    global clock_visible
    try:
        await client.connect()
    except OSError:
        print('Status: Connection Failed')
        return
    n = 0
    clock_visible = True
    asyncio.create_task(ntp_update(display))    
    while True:
        asyncio.create_task(render_clock())
        await asyncio.sleep(0.1)        
        n += 1

config['ssid'] = WIFI_SSID
config['wifi_pw'] = WIFI_KEY
config['server'] = MQTT_HOST
config['port'] = MQTT_PORT
config['ssl'] = MQTT_SSL
config['client_id'] = MQTT_CLIENT_ID
config['user'] = MQTT_USERNAME
config['password'] = MQTT_PASSWORD
config['subs_cb'] = on_message
config['wifi_coro'] = handle_wifi
# config['will'] = (MQTT_TOPIC_PREFIX, 'GOODBYE', False, 0)
config['connect_coro'] = handle_connection
config['keepalive'] = 120

MQTTClient.DEBUG = True
client = MQTTClient(config)

try:
    asyncio.run(main(client))
finally:  # Prevent LmacRxBlk:1 errors.
    client.close()
    asyncio.new_event_loop()
