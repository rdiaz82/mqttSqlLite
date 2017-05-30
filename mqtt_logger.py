import paho.mqtt.client as mqtt
import peewee
from models import Log
from datetime import datetime


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("casa/test")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    log_register = Log(timestamp=datetime.now(), topic=msg.topic, value=str(msg.payload))
    log_register.save()
    for log_entry in Log.select():
        print(log_entry.timestamp.isoformat() + " " + log_entry.topic + " " + log_entry.value)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.1.3", 1883, 60)

client.loop_forever()