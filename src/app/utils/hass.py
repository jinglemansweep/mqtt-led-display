import json

from app.constants import HASS_DISCOVERY_PREFIX


class HASS:
    def __init__(self, name, client, topic_prefix=HASS_DISCOVERY_PREFIX):
        self.name = name
        self.client = client
        self.topic_prefix = topic_prefix
        print(f"hass: name={name} topic_prefix={topic_prefix}")
        pass

    async def advertise_entity(self, entity_name, device_class="switch", options=None):
        if options is None:
            options = {}
        full_name = f"{self.name}_{entity_name}"
        topic = self._build_mqtt_topic(entity_name, device_class)
        command_topic = f"{topic}/set"
        state_topic = f"{topic}/state"
        auto_config = dict(
            name=full_name,
            unique_id=full_name,
            device_class=device_class,
            schema="json",
            command_topic=command_topic,
            state_topic=state_topic,
        )
        config = auto_config.copy()
        config.update(options)
        print(f"HASS Config: {full_name} [{device_class}] > {config}")
        await self.client.publish(
            f"{topic}/config", json.dumps(config), retain=True, qos=1
        )
        await self.client.subscribe(command_topic, 1)
        return (state_topic, command_topic)

    def _build_mqtt_topic(self, entity_name, device_class):
        return f"{self.topic_prefix}/{device_class}/{self.name}_{entity_name}"
