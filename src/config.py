#TX_PIN=27
RX_PIN=22

WIFI_HOSTNAME="Pico433MhzGateway"
WIFI_SSID="<SSID>"
WIFI_PASSWORD="<PASSWORD>"

MQTT_BROKER="<IP>"
MQTT_PORT=1883
MQTT_USER="<USERNAME>"
MQTT_PASSWD="<PASSWORD>"

MQTT_TOPIC="pico433mhz"

# Run sniffer.py and edit the codes below to match the ones your remote sends.
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
