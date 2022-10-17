import uasyncio as asyncio
from app.utils.hass import HASS
from app.lib.mqttas import MQTTClient, config
from app.utils.time import ntp_update
from app.secrets import (
    WIFI_KEY,
    WIFI_SSID,
    MQTT_HOST,
    MQTT_PORT,
    MQTT_SSL,
    MQTT_CLIENT_ID,
    MQTT_USERNAME,
    MQTT_PASSWORD,
)


class Manager:
    plugins = set()

    def __init__(self, name, display):
        self.name = name
        self.display = display
        self.client = self._build_client()
        self.hass = self._build_hass_manager()
        self.plugins = set()
        self.state = dict(scene=0, status_wifi=False, status_mqtt=False)

    def run(self):
        asyncio.run(self.loop())

    async def loop(self):
        try:
            await self.client.connect()
        except OSError:
            print("Status: Connection Failed")
            return
        self.display.clear()
        for plugin in self.plugins:
            asyncio.create_task(plugin.initialize())
        asyncio.create_task(ntp_update())
        while True:
            for plugin in self.plugins:
                asyncio.create_task(plugin.tick())
            self.display.render()
            await asyncio.sleep(0.05)

    def add_plugin(self, plugin_cls):
        plugin = plugin_cls(self)
        self.plugins.add(plugin)

    def _on_message(self, _topic, _msg, retained, _):
        topic = _topic.decode()
        msg = _msg.decode()
        if not msg:
            return
        print(f"mqtt_message: topic={topic} msg={msg} retained={retained}")
        for plugin in self.plugins:
            plugin.on_mqtt_message(topic, msg, retained)

        # if topic == f'{MQTT_TEXT_PREFIX}/set':
        #    asyncio.create_task(show_message(self.display, msg))
        # if topic == f'{MQTT_TEXT_PREFIX}/flash':
        #    asyncio.create_task(flash_message(self.display, msg))

    def _build_client(self):
        config["ssid"] = WIFI_SSID
        config["wifi_pw"] = WIFI_KEY
        config["server"] = MQTT_HOST
        config["port"] = MQTT_PORT
        config["ssl"] = MQTT_SSL
        config["client_id"] = MQTT_CLIENT_ID
        config["user"] = MQTT_USERNAME
        config["password"] = MQTT_PASSWORD
        config["keepalive"] = 120
        config["subs_cb"] = self._on_message
        config["connect_coro"] = self._on_connect
        config["wifi_coro"] = self._handle_connection
        # config['will'] = (MQTT_TOPIC_PREFIX, 'GOODBYE', False, 0)
        MQTTClient.DEBUG = True
        return MQTTClient(config)

    async def _handle_connection(self, status):
        if status:
            print("Status: Connected")
        else:
            self.state["status_mqtt"] = False
            print("Status: Not Connected")
        self.state["status_wifi"] = status
        await asyncio.sleep(1)

    async def _on_connect(self, _):
        self.state["status_mqtt"] = True

    def _build_hass_manager(self):
        return HASS(self.name, self.client)
