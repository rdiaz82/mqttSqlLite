import paho.mqtt.client as mqtt
import peewee
from models import Log
from datetime import datetime
from private_settings import *


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe(ROOT_TOPIC + "topic/add")
    client.subscribe(ROOT_TOPIC + "topic/remove")
    client.subscribe(ROOT_TOPIC + "topic/list")

    client.subscribe(ROOT_TOPIC + "log/last")
    client.subscribe(ROOT_TOPIC + "log/lastMinutes")
    client.subscribe(ROOT_TOPIC + "log/lastHours")
    client.subscribe(ROOT_TOPIC + "log/lastDays")
    client.subscribe(ROOT_TOPIC + "log/lastWeeks")
    client.subscribe(ROOT_TOPIC + "log/lastMonths")

    client.subscribe(ROOT_TOPIC + "delete/last")
    client.subscribe(ROOT_TOPIC + "delete/older/minutes")
    client.subscribe(ROOT_TOPIC + "delete/older/hours")
    client.subscribe(ROOT_TOPIC + "delete/older/days")
    client.subscribe(ROOT_TOPIC + "delete/older/weeks")
    client.subscribe(ROOT_TOPIC + "delete/older/months")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    log_register = Log(timestamp=datetime.now(), topic=msg.topic, value=str(msg.payload))
    log_register.save()
    for log_entry in Log.select():
        print(log_entry.timestamp.isoformat() + " " + log_entry.topic + " " + log_entry.value)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT, 60)

client.loop_forever()