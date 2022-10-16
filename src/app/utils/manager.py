import uasyncio as asyncio
from app.lib.mqttas import MQTTClient, config
from app.utils.debug import led_log
from app.utils.time import ntp_update
from app.secrets import \
    WIFI_KEY, WIFI_SSID, \
    MQTT_HOST, MQTT_PORT, MQTT_SSL, MQTT_CLIENT_ID, \
    MQTT_USERNAME, MQTT_PASSWORD
from app.constants import HASS_DISCOVERY_PREFIX
from app.state import STATE

class Manager:
    loop_iterations = 0
    scenes = set()

    def __init__(self, name, display, hass_topic_prefix=HASS_DISCOVERY_PREFIX):
        self.name = name
        self.display = display
        self.client = self._build_client()
        self.scenes = set()
        self.state = dict()
        self.hass_topic_prefix = hass_topic_prefix

    def run(self):
        asyncio.run(self.loop())

    async def loop(self):
        try:
            await self.client.connect()
        except OSError:
            print('Status: Connection Failed')
            return
        self.loop_iterations = 0
        self.display.clear()
        for scene in self.scenes:
            asyncio.create_task(scene.initialize())        
        asyncio.create_task(ntp_update(self.display))
        while True:
            self.display.clear()
            for scene in self.scenes:
                asyncio.create_task(scene.loop())
            await asyncio.sleep(0.1)        
            self.loop_iterations += 1

    def add_scene(self, scene_cls):
        scene = scene_cls(self)
        self.scenes.add(scene)

    def _on_message(self, _topic, _msg, retained, _):
        topic = _topic.decode()
        msg = _msg.decode()
        print(f'mqtt_message: topic={topic} msg={msg} retained={retained}')
        for scene in self.scenes:
            scene.on_mqtt_message(topic, msg, retained)
       
        #if topic == f'{MQTT_TEXT_PREFIX}/set':
        #    asyncio.create_task(show_message(self.display, msg))   
        #if topic == f'{MQTT_TEXT_PREFIX}/flash':
        #    asyncio.create_task(flash_message(self.display, msg))   

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
        pass   
