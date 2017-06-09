# mqttSqLite logger
mqttSqLite logger is a lightweight logger for MQTT brokers. It allows you to log all the published data under spectific topics and retrieve them for posterior data analysis. 

The logger is totally managed over mqtt, so you can add, remove or query your topics without sql sintax.

## Installation and run
The mqttSqLite logger is developed in python and use the peewee package as database provider and paho as mqtt client. In order to install the logger you need pip installed in your computer, and you only need to execute the following command:

```
pip install mqttsqlite
```
Mqttsqlite support some comand line arguments that allows the the logger configuration according to your needs. The supported commands are the following:

|Command                    | Default          | Purpose |
| ------------------------- |------------------|---------|
| --host      | localhost | mqtt broker host |
| --port   | 1883 | mqtt broker port|
| --root| logger/ | mqtt base topic for logger |
| --mgpassword | admin1234 | management options password |
| --qrpassword | query1234 | query options password | 

The logger can be started as:


```
mqttsqlite --host your_host --port your_port
```
Once you run the logger with the options, you can save them in next runs because the logger saves the options inside the database, so after configuration changed you can launch the mqttsqlite logger simply as: 

```
mqttsqlite
```

## Management commands
In order to add or remove the topics to the logger you can execute the following commands from any mqtt client. 

The command structure is always the same, first the ```ROOT_TOPIC``` defined through the root option when launch the logger followed by the desired command. For instance based a valid command could be: ```logger/topic/add```.

Included in the management commands payload should have included a json message with the following structure:

```
{
 "client" : "CLIENT_NAME_USED_TO_IDENTIFY_THE_RESPONSE"
 "password" : "YOUR_PASSWORD_FOR_MANAGEMENT_OPTIONS",
 "topic" : "TOPIC / ALL", #optional in some cases
 "option" : "COMMAND_OPTION", #optional in some cases
 }
```
The available commands related with topics managements are the following:

|Command                    | purpose          |
| ------------------------- |------------------|
| ROOT_TOPIC/topic/add      | add new topic to the logger |
| ROOT_TOPIC/topic/remove   | remove topic from to the logger |
| ROOT_TOPIC/topic/list   | remove topic from to the logger |

The MqttSQlite logger will respond in a new topic called ```ROOT_TOPIC/response``` with a json with the following format:

```
{
 "client" : "CLIENT_NAME_USED_TO_IDENTIFY_THE_RESPONSE",
 "result" : "OK/KO",
 "error" : "MESSAGE WITH ERROR WHEN RESULT IS KO",
 "topics" : [
 	"registered topic 1",
 	"registered topic2",
 	...
 	]
 }
```

The commands related with logger content managements are the following:

 Command                      | purpose                              |
| --------------------------- |------------------|
| ROOT_TOPIC/log/delete/last      | remove last entry por a topic (if included) or all topics|
| ROOT_TOPIC/log/delete/minutes   | remove the log entries older than x minutes (included in options) for a topic (if included) or all |
| ROOT_TOPIC/log/delete/hours   | remove the log entries older than x hours (included in options) for a topic (if included) or all |
| ROOT_TOPIC/log/delete/days   | remove the log entries older than x days (included in options) for a topic (if included) or all |

The MqttSqlite will respond in the topic ```ROOT_TOPIC/response``` with a json with the following structure:

```
{
 "client" : "CLIENT_NAME_USED_TO_IDENTIFY_THE_RESPONSE",
 "result" : "OK / KO"
 "error" : "MESSAGE WITH ERROR WHEN RESULT IS KO",
 }
```

## Query Commands
The query options structure are similar to the previous one. First the ```TOPIC_ROOT```followed by the desired command. In the payload should be included a json with the following structure:

```
{
 "client" : "CLIENT_NAME_USED_TO_IDENTIFY_THE_RESPONSE",
 "password" : "YOUR_PASSWORD_FOR_MANAGEMENT_OPTIONS",
 "topic" : "TOPIC"
 "option" : "COMMAND_OPTION" #optional in some cases
 }
```
The complete list of available query commands is the following:

| Command                       | purpose                                 |
| ------------------------------|-----------------------------------------|
| ROOT_TOPIC/log/query/last     | get the last entry for a topic          |
| ROOT_TOPIC/log/query/minutes  | get the entries from the last x minutes |
| ROOT_TOPIC/log/query/hours    | get the entries from the last x hours   |
| ROOT_TOPIC/log/query/days     | get the entries from the last x days    |

The MqttSqlite logger will respond in the topic ```ROOT_TOPIC/response``` with the required information with the following json format:

```
{
 "client" : "CLIENT_NAME_USED_TO_IDENTIFY_THE_RESPONSE",
 "topic" : "TOPIC",
 "result" : "OK/KO",
 "error" : "MESSAGE WITH ERROR WHEN RESULT IS KO",
 "values" : [
 	{"timestamp" : "YYYY-MM-ddTHH:mm:ss" , "value":"string_with_value"},
 	....]
 }
```

##Examples
Following is a python code using pahoo-mqtt client to communicate with the logger in order to add a new topic to be followed by the logger:

### Add topic

```
import paho.mqtt.client as mqtt
import json

MANAGEMENT_PASSWORD = 'YOUR PASSWORD'
MQTT_HOST = 'YOUR HOST'
MQTT_PORT = 'YOUR PORT'
ROOT_TOPIC = 'YOUR ROOT LOGGER TOPIC by default logger/'
desired_topic = 'desired/new/topic'

payload = {}
payload['client'] = 'simple_example'
payload['topic'] = desired_topic
payload['password'] = MANAGEMENT_PASSWORD


def on_connect(client, userdata, flags, rc):
    client_topic = ROOT_TOPIC + 'topic/add'
    client.subscribe(ROOT_TOPIC + 'response') #important subscribe to response topic to get the command result
    client.publish(client_topic, json.dumps(payload))



def on_message(client, userdata, msg):
    
    received_data = json.loads(msg.payload)
    print(received_data)
    if 'client' in received_data:
        if received_data['client'] == payload['client']:
            print('Received Meesage from Logger: ')
            print(received_data)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT, 60)

client.loop_forever()
```

Running this script you will get a similar output to the following:

```
Received Meesage from Logger:
{u'topic': u'desired_topic', u'topics': [u'desired_topic'], u'client': u'simple_exampl
e', u'result': u'OK'}
```

### Query Topic

In the following simple example, a topic query will be executed obtaining the topic information for the last 20 minutes:

```
import paho.mqtt.client as mqtt
import json
import mqttsqlite.settings.private_settings as Settings

QUERY_PASSWORD = 'YOUR PASSWORD'
MQTT_HOST = 'YOUR HOST'
MQTT_PORT = 'YOUR PORT'
ROOT_TOPIC = 'YOUR ROOT LOGGER TOPIC by default logger/'
desired_topic = 'desired/new/topic'

payload = {}
payload['client'] = 'simple_example'
payload['topic'] = desired_topic
payload['options'] = 20
payload['password'] = QUERY_PASSWORD


def on_connect(client, userdata, flags, rc):
    client_topic = ROOT_TOPIC + 'log/query/minutes'
    client.subscribe(ROOT_TOPIC + 'response') #importanat subscribe to response topic before request to the logger
    client.publish(client_topic, json.dumps(payload))


def on_message(client, userdata, msg):
    received_data = json.loads(msg.payload)
    if 'client' in received_data:
        if received_data['client'] == payload['client']:
            print('Received Meesage from Logger: ')
            print(received_data)
            client.disconnect()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT, 60)

client.loop_forever()
```

The response obtained could be similar to the following:

```
Received Meesage from Logger:
{u'topic': u'desired_topic', u'client': u'simple_example', u'values': [{u'timestamp':
u'2017-06-09 22:55:21', u'value': u'71'}, {u'timestamp': u'2017-06-09 22:56:14', u'val
ue': u'74'}, {u'timestamp': u'2017-06-09 22:56:15', u'value': u'74'}], u'result': u'OK
'}
```