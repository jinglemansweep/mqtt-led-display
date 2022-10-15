import json
from app.actions.clock import show_clock, MQTT_CLOCK_ID, MQTT_CLOCK_PREFIX
from app.actions.text import show_message, MQTT_TEXT_PREFIX
from app.state import STATE

async def setup_mqtt(client):
    await client.subscribe(f'{MQTT_CLOCK_PREFIX}/set', 1)
    await client.subscribe(f'{MQTT_TEXT_PREFIX}/set', 1)
    await client.subscribe(f'{MQTT_TEXT_PREFIX}/flash', 1)

async def setup_hass(client):
    # Clock switch
    config = dict(
        name=MQTT_CLOCK_ID, unique_id=MQTT_CLOCK_ID, device_class='switch',
        command_topic=f'{MQTT_CLOCK_PREFIX}/set', state_topic=f'{MQTT_CLOCK_PREFIX}/state',
    )
    await client.publish(f'{MQTT_CLOCK_PREFIX}/config', json.dumps(config), retain=True, qos=1)
    await client.publish(f'{MQTT_CLOCK_PREFIX}/state', 'ON' if STATE['clock.visible'] else 'OFF', retain=True, qos=1)
    # Text switch
    # config = dict(
    #     name=MQTT_TEXT_ID, unique_id=MQTT_TEXT_ID, device_class='switch',
    #     command_topic=f'{MQTT_TEXT_PREFIX}/set', state_topic=f'{MQTT_TEXT_PREFIX}/state',
    # )
    # await client.publish(f'{MQTT_TEXT_PREFIX}/config', json.dumps(config), retain=True, qos=1)
    # await client.publish(f'{MQTT_TEXT_PREFIX}/state', 'ON' if clock_visible else 'OFF', retain=True, qos=1)
