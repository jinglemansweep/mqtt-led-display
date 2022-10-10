import time
time.sleep(2)

import gc
import uasyncio as asyncio
from machine import Pin
from lib.mqttas import MQTTClient, config
from lib.stepper import create_stepper
from config import led_power, led_wifi, led_connected, led_mqtt_msg, motor_i1, motor_i2, motor_i3, motor_i4

gc.collect()

TOPIC_PREFIX = 'esp32/dev'

motor = create_stepper(motor_i1, motor_i2, motor_i3, motor_i4, delay=2)
motor.reset()

outages = 0

async def pulse():
    led_mqtt_msg(True)
    await asyncio.sleep(0.2)
    led_mqtt_msg(False)

async def motor_move(msg):
    try:
        angle = int(msg)
        print(f'Motor: Moving by {angle} degrees')
        motor.angle(angle)
    except Exception as e:
        print('Cannot parse angle from input')
        pass

def on_message(_topic, _msg, retained):
    topic = _topic.decode()
    msg = _msg.decode()
    print(f'Topic: "{topic}" Message: "{msg}" Retained: {retained}')
    if topic == f'{TOPIC_PREFIX}/motor/command':
        asyncio.create_task(motor_move(msg))
    asyncio.create_task(pulse())

async def handle_wifi(state):
    global outages
    led_wifi(state)
    if state:
        print('Status: Connected')
    else:
        outages += 1
        print('Status: Not Connected')
    await asyncio.sleep(1)

async def handle_connection(client):
    await client.subscribe(f'{TOPIC_PREFIX}/#', 1)

async def main(client):
    try:
        await client.connect()
    except OSError:
        print('Status: Connection Failed')
        led_connected(False)
        return
    led_connected(True)
    n = 0
    while True:
        await asyncio.sleep(5)
        # print('publish', n)
        # await client.publish(TOPIC_PREFIX, '{} repubs: {} outages: {}'.format(n, client.REPUB_COUNT, outages), qos = 1)
        n += 1

config['subs_cb'] = on_message
config['wifi_coro'] = handle_wifi
config['will'] = (TOPIC_PREFIX, 'GOODBYE', False, 0)
config['connect_coro'] = handle_connection
config['keepalive'] = 120

MQTTClient.DEBUG = True
client = MQTTClient(config)

try:
    asyncio.run(main(client))
finally:  # Prevent LmacRxBlk:1 errors.
    client.close()
    led_connected(False)
    led_mqtt_msg(False)
    asyncio.new_event_loop()

