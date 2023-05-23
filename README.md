# Robust RPi Pico 433Mhz-to-MQTT Gateway for using 433Mhz Remotes in your Smart-Home Projects

![Endproduct with antenna attached next to remote control](/pictures/endproduct_unpacked.jpg)
![Endproduct inside a raspberry pi zero case next to remote control](/pictures/endproduct_insidecase.jpg)

Thanks to:
- https://github.com/milaq/rpi-rf for the python code to receive and send 433Mhz codes on the Raspberry Pi
- https://github.com/bnthn/pico433mhzMQTTGateway which this is a fork of (especially the pico edits)


# 1. How to set up

## 1.1 Basics

Set up micropython on pico (use the firmware for 'Raspberry Pi Pico W (with urequests and upip preinstalled)')
URL https://www.raspberrypi.com/documentation/microcontrollers/micropython.html

Update 'src/config.py' with your WiFi and MQTT Config. Also set the RX-Pin Number depending on which Pin you connected the Data Pin of your receiver.
Copy all files from src to Pico (you can use thonny for this). Also make sure to install the umqtt/robust2 package, as this is needed for publishing MQTT-messages.

Restarting the Pico (by plugging it in) will run the main.py script.

## 1.2. Sniffing 433Mhz traffic and editing topics/messages

Run sniffer.py and edit the codes in config.py according to your needs.

NOTE: Codes (as well as pulselength and protocol) could vary depending on how long the button on your remote is pressed! Press and hold the button on your remote and observe which code is the right one (gets repeated over and over while button is pressed). The wrong config yould yield buttons you did not press.

```
[...]
{ "code": "1234567", "pulselength": "325", "protocol": "1" }
```

```
MQTT_TOPIC="topic/you/wish/to/publish/to"

CODES = {
    "1000000": {"subtopic": "A", "msg": "ON"},
    "1000001": {"subtopic": "A", "msg": "OFF"},  
    "1000002": {"subtopic": "B", "msg": "ON"}, 
    "1000003": {"subtopic": "B", "msg": "OFF"}, 
    "1000004": {"subtopic": "C", "msg": "ON"}, 
    "1000005": {"subtopic": "C", "msg": "OFF"}, 
    "1000006": {"subtopic": "D", "msg": "ON"},
    "1000007": {"subtopic": "D", "msg": "OFF"},  
}
```

# 2. Notes on the Hardware (#TODO)

- regulations regarding 433mhz
- right receiver module 
- antenna (https://www.instructables.com/433-MHz-Coil-loaded-antenna/)
- 3.3V or 5V (USB-passthrough)

