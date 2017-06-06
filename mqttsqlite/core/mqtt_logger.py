import paho.mqtt.client as mqtt
import peewee
from models import Log
from datetime import datetime
from private_settings import *
from topics_controller import Topics
from mqtt_controller import MqttController
import re


def on_connect(client, userdata, flags, rc):
    mqtt_controller = MqttController()
    mqtt_controller.on_connect(client)


def on_message(client, userdata, msg):
        mqtt_controller.on_message(client, msg)

    # log_register = Log(timestamp=datetime.now(), topic=msg.topic, value=str(msg.payload))
    # log_register.save()
    # for log_entry in Log.select():
    #    print(log_entry.timestamp.isoformat() + " " + log_entry.topic + " " + log_entry.value)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT, 60)

client.loop_forever()