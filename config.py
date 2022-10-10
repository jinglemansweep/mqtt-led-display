from machine import Pin
from lib.mqttas import config
from secrets import MQTT_HOST, MQTT_PORT, MQTT_SSL, MQTT_CLIENT_ID, MQTT_USERNAME, MQTT_PASSWORD, WIFI_KEY, WIFI_SSID

config['ssid'] = WIFI_SSID
config['wifi_pw'] = WIFI_KEY

config['server'] = MQTT_HOST
config['port'] = MQTT_PORT
config['ssl'] = MQTT_SSL
config['client_id'] = MQTT_CLIENT_ID
config['user'] = MQTT_USERNAME
config['password'] = MQTT_PASSWORD
