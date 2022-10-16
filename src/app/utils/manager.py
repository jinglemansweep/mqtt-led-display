import json
import uasyncio as asyncio
from app.lib.mqttas import MQTTClient, config
from app.utils.debug import led_log
from app.utils.time import ntp_update
from app.actions.clock import \
    setup_mqtt as setup_mqtt_clock, init as init_clock, \
    update_clock, render_clock, MQTT_LIGHT_PREFIX
from app.actions.text import \
    setup_mqtt as setup_mqtt_text, init as init_text, \
        show_message, flash_message, MQTT_TEXT_PREFIX
from app.secrets import \
    WIFI_KEY, WIFI_SSID, \
    MQTT_HOST, MQTT_PORT, MQTT_SSL, MQTT_CLIENT_ID, \
    MQTT_USERNAME, MQTT_PASSWORD
from app.state import STATE

class Manager:
    loop_iterations = 0

    def __init__(self, display):
        self.display = display
        self.client = self._build_client()

    def run(self):
        asyncio.run(self.loop())

    async def loop(self):
        try:
            await self.client.connect()
        except OSError:
            print('Status: Connection Failed')
            return
        self.loop_iterations = 0
        asyncio.create_task(init_clock(self.display, self.client))
        asyncio.create_task(init_text(self.display, self.client))
        asyncio.create_task(ntp_update(self.display))    
        while True:
            asyncio.create_task(render_clock(self.display))
            await asyncio.sleep(0.1)        
            self.loop_iterations += 1

    def _on_message(self, _topic, _msg, retained, _):
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
            asyncio.create_task(update_clock(self.display, self.client, visible, color, brightness))    
        if topic == f'{MQTT_TEXT_PREFIX}/set':
            asyncio.create_task(show_message(self.display, msg))   
        if topic == f'{MQTT_TEXT_PREFIX}/flash':
            asyncio.create_task(flash_message(self.display, msg))   

    def _build_client(self):
        config['ssid'] = WIFI_SSID
        config['wifi_pw'] = WIFI_KEY
        config['server'] = MQTT_HOST
        config['port'] = MQTT_PORT
        config['ssl'] = MQTT_SSL
        config['client_id'] = MQTT_CLIENT_ID
        config['user'] = MQTT_USERNAME
        config['password'] = MQTT_PASSWORD
        config['keepalive'] = 120
        config['subs_cb'] = self._on_message
        config['connect_coro'] = self._on_connect
        config['wifi_coro'] = self._handle_connection
        # config['will'] = (MQTT_TOPIC_PREFIX, 'GOODBYE', False, 0)
        MQTTClient.DEBUG = True
        return MQTTClient(config)

    async def _handle_connection(self, state):
        if state:
            led_log(self.display, 'wifi')
            print('Status: Connected')
        else:
            STATE["connection.outages"] += 1
            print('Status: Not Connected')
        await asyncio.sleep(1)

    async def _on_connect(self, _):
        await setup_mqtt_clock(self.client)
        await setup_mqtt_text(self.client)        
