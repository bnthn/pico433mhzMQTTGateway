import network
import time
from machine import Pin, reset

from umqtt.robust2 import MQTTClient

import rfdevice
import config

# Setup the onboard LED so we can turn it on/off
led = Pin("LED", Pin.OUT)

# some visual feedback. If the onboard LED blinks, device is trying to (re)connect.
def led_blink():
    led.value(1)
    time.sleep(0.5)
    led.value(0)
    
wlan_retry_count = 0
mqtt_retry_count = 0

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
network.hostname(config.WIFI_HOSTNAME)
wlan.active(True)
wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
while wlan.isconnected() == False:
    if wlan_retry_count > 6:
        reset()
    print('Waiting for connection...')
    wlan_retry_count += 1
    led_blink()
    time.sleep(5)
print("Connected to WiFi")

def mqtt_connect():
    client = MQTTClient(client_id="433mhzpico", server=config.MQTT_BROKER, \
                        port=config.MQTT_PORT, user=config.MQTT_USER, \
                        password=config.MQTT_PASSWD, keepalive=3600)
    client.connect()
    print('Connecting to %s MQTT Broker'%(config.MQTT_BROKER))
    return client


try:
    client = mqtt_connect()
except OSError as e:
    print("Initial Connection to MQTT Broker failed, resetting device...")
    led_blink()
    time.sleep(5)
    reset()

receiver = rfdevice.RFDevice()
receiver.enable_rx()

timestamp = None
start = time.ticks_ms()

while True:
    
    # handling connection errors
    if not wlan.isconnected():
        print("Wifi could not be reached, resetting device...")
        led_blink()
        time.sleep(5)
        reset()
        
    if client.is_conn_issue():
        if mqtt_retry_count > 6:
            reset()
        print("MQTT Broker could not be reached, trying to reconnect...")
        mqtt_retry_count += 1
        client.reconnect()
        led_blink()
        time.sleep(5)
        
    # handling messages
    if receiver.rx_code_timestamp != timestamp:
        timestamp = receiver.rx_code_timestamp
        if timestamp != None:
            code = config.CODES.get(str(receiver.rx_code))
            if code:
                client.publish("%s/%s"%(config.MQTT_TOPIC, code.get("subtopic")), str(code.get("msg")))
    
    time.sleep(0.5)
    




