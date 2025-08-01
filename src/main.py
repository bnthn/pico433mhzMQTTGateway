import network
import time
from machine import Pin, reset
import asyncio

from umqtt.robust2 import MQTTClient

import rfdevice
import config

class Gateway:

    def __init__(self):
        
        wlan_retry_count = 0
    
        # Setup the onboard LED so we can turn it on/off
        self.led = Pin("LED", Pin.OUT)
        
        # Connect to WiFi
        self.wlan = network.WLAN(network.STA_IF)
        network.hostname(config.WIFI_HOSTNAME)
        self.wlan.active(True)
        self.wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        
        while self.wlan.isconnected() == False:
            if wlan_retry_count > 3:
                reset()
            print('Waiting for WLAN connection...')
            wlan_retry_count += 1
            asyncio.run(self.led_blink())
            time.sleep(3)
        
        try:
            self.mqtt_connect()
        except OSError as e:
            print("Initial Connection to MQTT Broker failed, resetting device...")
            asyncio.run(self.led_blink())
            time.sleep(3)
            reset()
        
        self.receiver = rfdevice.RFDevice()
        self.receiver.enable_rx()
        
    

    # some visual feedback. If the onboard LED blinks, device is trying to (re)connect.
    async def led_blink(self):
        self.led.value(1)
        await asyncio.sleep_ms(500)
        self.led.value(0)    


    def mqtt_connect(self):
        client = MQTTClient(client_id="433mhzpico", server=config.MQTT_BROKER, \
                            port=config.MQTT_PORT, user=config.MQTT_USER, \
                            password=config.MQTT_PASSWD, keepalive=3600)
        client.connect()
        print('Connecting to %s MQTT Broker'%(config.MQTT_BROKER))
        self.client = client
    
    def check_connection(self):
        if not self.wlan.isconnected():
            print("WLAN unreachable, resetting device...")
            asyncio.run(self.led_blink())
            time.sleep(3)
            reset()
            
        if self.client.is_conn_issue():
            MQTT_MAX_RETRIES = 3
            for i in range(MQTT_MAX_RETRIES):
                if self.client.is_conn_issue():
                    print(f"MQTT Broker could not be reached, trying to reconnect... ({str(i+1)}/{str(MQTT_MAX_RETRIES)})")
                    self.client.reconnect()
                    asyncio.run(self.led_blink())
                else:
                    print("MQTT reconnected.")
                    return
            print("MQTT unreachable, resetting device...")
            reset()
    
    
    def run(self):
        asyncio.run(self.led_blink())
            
        timestamp = None
        start = time.ticks_ms()
        while True:

            self.check_connection()
                
            # handling messages
            if self.receiver.rx_code_timestamp != timestamp:
                timestamp = self.receiver.rx_code_timestamp
                if timestamp != None:
                    #print('{ "code": "' + str(receiver.rx_code) + '", "pulselength": "' + str(receiver.rx_pulselength) + '", "protocol": "' + str(receiver.rx_proto) + '" }')
                    code = config.CODES.get(str(self.receiver.rx_code))
                    if code:
                        #print(code)
                        self.client.publish("%s/%s"%(config.MQTT_TOPIC, code.get("subtopic")), str(code.get("msg")))
                        asyncio.run(self.led_blink())
            
            time.sleep(0.2)
            
if __name__ == "__main__":
    Gateway().run()

