import json

from app.constants import HASS_DISCOVERY_PREFIX


class Entity:
    def __init__(
        self,
        host_id,
        name,
        device_class,
        hass_topic_prefix,
        client,
        options=None,
    ):
        if options is None:
            options = dict()
        self.name = f"{host_id}_{name}"
        self.device_class = device_class
        self.client = client
        self.options = options
        self.hass_topic_prefix = hass_topic_prefix
        topic_prefix = self._build_entity_topic_prefix()
        self.topic_config = f"{topic_prefix}/config"
        self.topic_command = f"{topic_prefix}/set"
        self.topic_state = f"{topic_prefix}/state"
        self.state = dict()

    async def configure(self):
        auto_config = dict(
            name=self.name,
            unique_id=self.name,
            device_class=self.device_class,
            schema="json",
            command_topic=self.topic_command,
            state_topic=self.topic_state,
        )
        config = auto_config.copy()
        config.update(self.options)
        print(f"hass.entity.configure: name={self.name} config={config}")
        await self.client.publish(
            self.topic_config, json.dumps(config), retain=True, qos=1
        )
        await self.client.subscribe(self.topic_command, 1)

    def get_state(self):
        return self.state

    async def update(self, new_state=None):
        if new_state is None:
            new_state = dict()
        self.state.update(new_state)
        print(f"hass.entity.update: name={self.name} config={self.state}")
        await self.client.publish(
            self.topic_state, json.dumps(self.state), retain=True, qos=1
        )

    def _build_entity_topic_prefix(self):
        return f"{self.hass_topic_prefix}/{self.device_class}/{self.name}"


class HASS:
    def __init__(self, host_id, client, topic_prefix=HASS_DISCOVERY_PREFIX):
        self.host_id = host_id
        self.client = client
        self.topic_prefix = topic_prefix
        self.entities = dict()
        print(f"hass: host_id={host_id} topic_prefix={topic_prefix}")
        pass

    async def add_entity(self, name, device_class, options=None, initial_state=None):
        entity = Entity(
            self.host_id,
            name,
            device_class,
            self.topic_prefix,
            self.client,
            options,
        )
        await entity.configure()
        await entity.update(initial_state)
        self.entities[name] = entity
        return entity
