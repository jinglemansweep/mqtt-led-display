from sys import platform, implementation
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

led_power = Pin(21, Pin.OUT, value = 1)
led_wifi = Pin(22, Pin.OUT, value = 0)
led_connected = Pin(23, Pin.OUT, value = 0)
led_mqtt_msg = Pin(15, Pin.OUT, value = 0)

motor_i1 = Pin(26, Pin.OUT)
motor_i2 = Pin(25, Pin.OUT)
motor_i3 = Pin(33, Pin.OUT)
motor_i4 = Pin(32, Pin.OUT)