import utime
utime.sleep(2)

import gc
import json
import uasyncio as asyncio

from app.lib.mqttas import MQTTClient, config
from app.lib.ledmatrix import create_display
from app.utils.debug import led_log
from app.utils.time import ntp_update
from app.actions.clock import \
    setup_mqtt as setup_mqtt_clock, init as init_clock, \
    update_clock, render_clock, MQTT_LIGHT_PREFIX
from app.actions.text import \
    setup_mqtt as setup_mqtt_text, init as init_text, \
        show_message, flash_message, MQTT_TEXT_PREFIX
from app.constants import DEVICE_ID
from app.settings import \
    GPIO_PIN, DISPLAY_ROWS, DISPLAY_COLUMNS, \
    DISPLAY_FPS, DISPLAY_DEBUG
from app.secrets import \
    WIFI_KEY, WIFI_SSID, \
    MQTT_HOST, MQTT_PORT, MQTT_SSL, MQTT_CLIENT_ID, \
    MQTT_USERNAME, MQTT_PASSWORD
from app.state import STATE

gc.collect()

print('MQTT LED DISPLAY')
print(f'Device ID: {DEVICE_ID}')

display = create_display(
    GPIO_PIN, 
    DISPLAY_ROWS, DISPLAY_COLUMNS, DISPLAY_FPS, DISPLAY_DEBUG
)

STATE["ntp.set"] = False
STATE["connection.outages"] = 0

led_log(display, 'boot')

async def on_mqtt_connect(client):
    await setup_mqtt_clock(client)
    await setup_mqtt_text(client)

def on_mqtt_message(_topic, _msg, retained, client):
    topic = _topic.decode()
    msg = _msg.decode()
    print(f'Topic: "{topic}" Message: "{msg}" Retained: {retained}')
    if topic == f'{MQTT_LIGHT_PREFIX}/set':        
        obj = json.loads(msg)
        visible = None
        color = None
        brightness = None
        if 'state' in obj:
            visible = 'on' in obj.get('state').lower()
        if 'color' in obj:
            rgb = obj.get('color')
            color = (rgb.get('r'), rgb.get('g'), rgb.get('b'))
        if 'brightness' in obj:
            brightness = obj.get('brightness')
        asyncio.create_task(update_clock(display, client, visible, color, brightness))    
    if topic == f'{MQTT_TEXT_PREFIX}/set':
        asyncio.create_task(show_message(display, msg))   
    if topic == f'{MQTT_TEXT_PREFIX}/flash':
        asyncio.create_task(flash_message(display, msg))   

async def handle_wifi(state):
    if state:
        led_log(display, 'wifi')
        print('Status: Connected')
    else:
        STATE["connection.outages"] += 1
        print('Status: Not Connected')
    await asyncio.sleep(1)

async def main(client):
    try:
        await client.connect()
    except OSError:
        print('Status: Connection Failed')
        return
    n = 0
    asyncio.create_task(init_clock(display, client))
    asyncio.create_task(init_text(display, client))
    asyncio.create_task(ntp_update(display))    
    while True:
        asyncio.create_task(render_clock(display))
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
config['subs_cb'] = on_mqtt_message
config['connect_coro'] = on_mqtt_connect
config['wifi_coro'] = handle_wifi
# config['will'] = (MQTT_TOPIC_PREFIX, 'GOODBYE', False, 0)

config['keepalive'] = 120

MQTTClient.DEBUG = True
client = MQTTClient(config)

try:
    asyncio.run(main(client))
finally:  # Prevent LmacRxBlk:1 errors.
    client.close()
    asyncio.new_event_loop()
