import paho.mqtt.client as mqtt
import json
import mqttsqlite.settings.private_settings as Settings

MANAGEMENT_PASSWORD = Settings.QUERY_PASSWORD
MQTT_HOST = Settings.MQTT_HOST
MQTT_PORT = Settings.MQTT_PORT
ROOT_TOPIC = Settings.ROOT_TOPIC
desired_topic = 'salon/humedad'

payload = {}
payload['client'] = 'simple_example'
payload['topic'] = desired_topic
payload['options'] = 20
payload['password'] = MANAGEMENT_PASSWORD


def on_connect(client, userdata, flags, rc):
    client_topic = ROOT_TOPIC + 'log/query/minutes'
    client.subscribe(ROOT_TOPIC + 'response')
    client.publish(client_topic, json.dumps(payload))


def on_message(client, userdata, msg):
    received_data = json.loads(msg.payload)
    if 'client' in received_data:
        if received_data['client'] == payload['client']:
            print('Received Message from Logger: ')
            print(received_data)
            client.disconnect()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT, 60)

client.loop_forever()
