import json


class BasePlugin:
    def __init__(self, manager):
        self.manager = manager
        self.state = dict()
        self.topics = dict()

    async def initialize(self):
        # print("initialize")
        pass

    async def loop(self):
        # print("loop")
        pass

    def should_loop(self, manager_state):
        return True

    async def tick(self):
        if self.should_loop(self.manager.state):
            await self.loop()

    def on_mqtt_message(self, topic, msg, retain=False):
        # print("on_mqtt_message", topic, msg, retain)
        pass
