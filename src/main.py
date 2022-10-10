import time
time.sleep(2)

import gc
import uasyncio as asyncio

from lib.mqttas import MQTTClient, config
from lib.ledmatrix import LedMatrix
from lib.hal import HAL
from pixelfont import PixelFont
from utils import set_clock
from secrets import MQTT_HOST, MQTT_PORT, MQTT_SSL, MQTT_CLIENT_ID, MQTT_USERNAME, MQTT_PASSWORD, WIFI_KEY, WIFI_SSID

gc.collect()

print('MQTT LED DISPLAY')

GPIO_PIN = 16
DISPLAY_PIXEL_COUNT = 256
DISPLAY_ROWS = 8
DISPLAY_COLS = 32
DISPLAY_FPS = 10
DISPLAY_DEBUG = False
DISPLAY_INTENSITY = 2

MQTT_TOPIC_PREFIX = 'mqttled/test'

outages = 0

driver = HAL(gpio_pin=GPIO_PIN, pixel_count=DISPLAY_PIXEL_COUNT)

display = LedMatrix(driver, dict(
    debug=DISPLAY_DEBUG,
    columns=DISPLAY_COLS,
    stride=DISPLAY_ROWS,
    fps=DISPLAY_FPS
))

async def test_cb():
    print('Test Callback')
    await asyncio.sleep(0.2)

async def echo(msg):
    print(f'ECHO: {msg}')

async def handle_wifi(state):
    global outages
    if state:
        print('Status: Connected')
    else:
        outages += 1
        print('Status: Not Connected')
    await asyncio.sleep(1)

async def handle_connection(client):
    await client.subscribe(f'{MQTT_TOPIC_PREFIX}/#', 1)

def on_message(_topic, _msg, retained):
    topic = _topic.decode()
    msg = _msg.decode()
    print(f'Topic: "{topic}" Message: "{msg}" Retained: {retained}')
    if topic == f'{MQTT_TOPIC_PREFIX}/echo':
        asyncio.create_task(echo(msg))

async def main(client):
    try:
        await client.connect()
    except OSError:
        print('Status: Connection Failed')
        return
    set_clock()
    n = 0
    while True:
        await asyncio.sleep(5)
        # print('publish', n)
        # await client.publish(TOPIC_PREFIX, '{} repubs: {} outages: {}'.format(n, client.REPUB_COUNT, outages), qos = 1)
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
config['will'] = (MQTT_TOPIC_PREFIX, 'GOODBYE', False, 0)
config['connect_coro'] = handle_connection
config['keepalive'] = 120

MQTTClient.DEBUG = True
client = MQTTClient(config)

try:
    asyncio.run(main(client))
finally:  # Prevent LmacRxBlk:1 errors.
    client.close()
    asyncio.new_event_loop()

"""
while True:
    (year, month, day, hour, minute, second, weekday, _) = time.localtime()[:8]
    now_fmt = '{:02d}:{:02d}'.format(hour, minute)
    display.render_text(PixelFont, now_fmt, 0, 0, 10,0,5)
    display.render()
    time.sleep(2)
    display.hscroll(-1)
    time.sleep(1)
"""