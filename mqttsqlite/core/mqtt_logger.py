import paho.mqtt.client as mqtt
import peewee
from models import Log
from datetime import datetime
from private_settings import *
from topics_controller import Topics


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    client.subscribe(ROOT_TOPIC + "topic/*")
    client.subscribe(ROOT_TOPIC + "log/*")
    client.subscribe(ROOT_TOPIC + "delete/*")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    if 'topic' in msg.topic:
        topics = Topics()
        response = topics.process_request(msg)
    elif 'log':
        

    #log_register = Log(timestamp=datetime.now(), topic=msg.topic, value=str(msg.payload))
    #log_register.save()
    #for log_entry in Log.select():
    #    print(log_entry.timestamp.isoformat() + " " + log_entry.topic + " " + log_entry.value)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT, 60)

client.loop_forever()