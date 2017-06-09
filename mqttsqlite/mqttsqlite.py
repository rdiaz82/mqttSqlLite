import paho.mqtt.client as mqtt
from .core.mqtt_controller import MqttController
from .orm.models import Setting, create_tables
import argparse
from .settings.private_settings import *


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


def init_settings(args):
    print('Checking Settings')
    try:
        settings = Setting.select()
        settings.count()
    except:
        create_tables()
        settings = Setting.select()
    if args.mqtt_host is not 'localhost':
        set_host(args.mqtt_host)
    if args.mqtt_port is not '1883':
        set_port(args.mqtt_port)
    if args.root_topic is not 'logger/':
        set_root_topic(args.mqtt_port)
    if args.management_password is not 'admin1234':
        set_management_pass(args.management_password)
    if args.query_password is not 'query1234':
        set_query_pass(args.query_password)


def main():
    parser = argparse.ArgumentParser(description='Sqlite Logger for MQTT broker')
    parser.add_argument('--host', dest='mqtt_host', default='localhost', help='Mqtt Broker URL')
    parser.add_argument('--port', dest='mqtt_port', default=1883, help='Mqtt Broker Port')
    parser.add_argument('--root', dest='root_topic', default='logger/', help='Root topic for logger commands')
    parser.add_argument('--mgpassword', dest='management_password', default='admin1234', help='password for management options')
    parser.add_argument('--qrpassword', dest='query_password', default='query1234', help='password for query options')

    init_settings(parser.parse_args())

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    print(get_host() + ':' + str(get_port()))
    client.connect(get_host(), int(get_port()), 60)

    client.loop_forever()