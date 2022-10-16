import json


class BasePlugin:
    def __init__(self, manager):
        self.manager = manager
        self.state = dict()

    async def initialize(self):
        # print("initialize")
        pass

    async def loop(self):
        # print("loop")
        pass

    def on_mqtt_message(self, topic, msg, retain=False):
        # print("on_mqtt_message", topic, msg, retain)
        pass

    def build_mqtt_topic(self, name, device_class="switch"):
        return f"{self.manager.hass_topic_prefix}/{device_class}/{self.manager.name}_{name}"

    async def configure_hass_entity(self, name, device_class="switch", options=None):
        if options is None:
            options = {}
        full_name = f"{self.manager.name}_{name}"
        topic = self.build_mqtt_topic(name, device_class)
        auto_config = dict(
            name=full_name,
            unique_id=full_name,
            device_class=device_class,
            schema="json",
            command_topic=f"{topic}/set",
            state_topic=f"{topic}/state",
        )
        config = auto_config.copy()
        config.update(options)
        print(f"HASS Config: {full_name} [{device_class}] > {config}")
        await self.manager.client.publish(
            f"{topic}/config", json.dumps(config), retain=True, qos=1
        )
