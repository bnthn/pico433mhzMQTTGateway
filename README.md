# Robust RPi Pico 433Mhz-to-MQTT Gateway for using 433Mhz Remotes in your Smart-Home Projects

Use common 433Mhz Remotes with your Smart Home Applications (e.g. via Home Assistant) by reacting to MQTT-Messages.

Device will automatically detect Connection loss from MQTT-Server or WiFi and react by reconnecting or resetting the device until the connection can be established again. This is indicated by the onboard LED blinking slowly.


![Endproduct with antenna attached next to remote controls](/pictures/final_product.jpg)

Thanks to:
- https://github.com/milaq/rpi-rf for the python code to receive and send 433Mhz codes on the Raspberry Pi
- https://github.com/AdrianCX/pico433mhz which this is a fork of (especially the pico edits)


# 1. How to set up

## 1.1 Basics

- Set up micropython on pico (use the firmware for **Raspberry Pi Pico W (with urequests and upip preinstalled)**). See https://www.raspberrypi.com/documentation/microcontrollers/micropython.html
- Make sure to install the umqtt.robust2 package, as this is needed for publishing MQTT-messages (easily doable in thonny IDE). See https://pypi.org/project/micropython-umqtt.robust2/
- Update `src/config.py` with your WiFi and MQTT Config. Also set the RX-Pin Number depending on which Pin you connected the Data Pin of your receiver. Copy all files from src to Pico, e.g. via thonny IDE.

Restarting the Pico (by plugging it in) will run the `main.py` script.

## 1.2. Sniffing 433Mhz traffic and editing topics/messages

Run `src/sniffer.py` and edit the codes in `src/config.py` according to your needs.

**IMPORTANT NOTE**: Codes (as well as pulselength and protocol) can vary depending on how long the button on your remote is pressed! This behaviour occurs with some types / brands of remote controls I used. Press and hold the button on your remote and observe which code is the right one (gets repeated over and over while button is pressed). The wrong config could yield messages for buttons you did not press.

### Sniffer output
```
[...]
{ "code": "1000002", "pulselength": "325", "protocol": "1" }
```

### Configuration
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

# 2. Notes on the Hardware

![The receiver inside its opened case](/pictures/hardware.jpg)

- Make sure to meet the [regulations regarding 433mhz](https://en.wikipedia.org/wiki/LPD433) in your country of use.
- For remotes [look e.g. here](https://github.com/sui77/rc-switch/wiki/List_KnownDevices). The ones i tested are the ones shown in the first picture above, from left to right:
    - **Sonoff RM433R2**: Has the most modern feel to it and is available to buy (at the time of writing this) for 5-10 bucks depending on the country / shop.
    - **Brennenstuhl RCS 1000 N Comfort**: This is a set of the remote and the power plugs it should be used with, but you can get the remote seperately on ebay etc. 
    - **Elro AB440R**: Pretty much identical to the Brennenstuhl above. Would not recommend buying these today, but i have been using two of these for 10 years in their intended use case and they are still going strong.
- You can use a coil loaded antenna, which is often sent along with the receiver, but for the best possible result it is advised to [build your own!](https://www.instructables.com/433-MHz-Coil-loaded-antenna/). I used the linked method and spun it around a toothpick using a hot glue gun and put heat shrinking tubes on top of it.
- Try to use the [best receiver module(s)](https://blog.thesen.eu/433mhz-empfaenger-fuer-arduino-co-rxb12-vs-xy-mk-5v/). Use **Superheterodyne like RXB12** instead of **XY-MK-5V**.