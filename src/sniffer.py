import time

import rfdevice
import config

receiver = rfdevice.RFDevice()
receiver.enable_rx()

timestamp = None
start = time.ticks_ms()
while True:
    # handling messages
    if receiver.rx_code_timestamp != timestamp:
        timestamp = receiver.rx_code_timestamp
        if timestamp != None:
            print('{ "code": "' + str(receiver.rx_code) + '", "pulselength": "' + str(receiver.rx_pulselength) + '", "protocol": "' + str(receiver.rx_proto) + '", timestamp: "' + str(timestamp) + '" }')
    time.sleep(0.5)
