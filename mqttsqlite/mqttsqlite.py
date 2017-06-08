import paho.mqtt.client as mqtt
from .core.mqtt_controller import MqttController
from .settings.private_settings import MQTT_HOST, MQTT_PORT


def on_connect(client, userdata, flags, rc):
    print('connecting...')
    mqtt_controller = MqttController()
    mqtt_controller.on_connect(client)
    print('connected')


def on_message(client, userdata, msg):
    print('received message')
    print(msg.topic + ' : ' + str(msg.payload))
    mqtt_controller = MqttController()
    mqtt_controller.on_message(client, msg)
    print('proccessed Message')


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    print(MQTT_HOST + ':' + MQTT_PORT)
    client.connect(MQTT_HOST, int(MQTT_PORT), 60)

    client.loop_forever()