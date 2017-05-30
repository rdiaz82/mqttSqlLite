# mqttSqLite logger
mqttSqLite logger is a lightweight logger for MQTT brokers. It allows you to log all the published data under spectific topics and retrieve them for posterior data analysis. 

The logger is totally managed over mqtt, so you can add, remove or query your topics without sql sintax.

## Installation
The mqttSqLite logger is developed in python and use the peewee package as database provider and paho as mqtt client. In order to install the libraries you will need to install both libraries with:

```
pip install paho-mqtt peewee
```
after the package installation you need to add a private_settings.py file to your mqttSqlite logger file with the following information:

```
# Sqlite database file
DATABASE = 'mqtt.db'

# MQTT server settings
MQTT_HOST = 'YOUR_MQTT_SERVER_HOST'
MQTT_PORT = 'YOUR_MQTT_SERVER_PORT'

# Base logger topic
ROOT_TOPIC = 'house/logger/'

# password for management options
MANAGEMENT_PASSWORD = 'YOUR_PASSWORD_FOR_MANAGEMENT_OPTIONS'

# password for query options
QUERY_PASSWORD = 'YOUR_PASSWORD_FOR_QUERY_THE_LOG'
```

In order to run the logger you only have to execute the following command:

```
python mqtt_logger.py
```

## Management commands (NOT IMPLEMENTED YET!!!)
In order to add or remove the topics to the logger you can execute the following commands from any mqtt client. 

The command structure is always the same, first the ```ROOT_TOPIC``` defined in your private settings followed by the desired command. For instance based on the provided private settings file a valid command could be: ```house/logger/topic/add```.

Included in the management commands payload should have included a json message with the following structure:

```
{
 "client" : "CLIENT_NAME_USED_TO_IDENTIFY_THE_RESPONSE"
 "password" : "YOUR_PASSWORD_FOR_MANAGEMENT_OPTIONS",
 "topic" : "TOPIC / ALL" #optional in some cases
 "option" : "COMMAND_OPTION" #optional in some cases
 }
```
The available commands related with topics managements are the following:

|Command                    | purpose          |
| ------------------------- |------------------|
| ROOT_TOPIC/topic/add      | add new topic to the logger |
| ROOT_TOPIC/topic/remove   | remove topic from to the logger |

With these commands a topic should be added in the json in the ```option``` field.

The commands related with logger content managements are the following:

 Command                      | purpose                              |
| --------------------------- |------------------|
| ROOT_TOPIC/delete/last      | remove last entry por a topic (if included) or all topics|
| ROOT_TOPIC/delete/older/minutes   | remove the log entries older than x minutes (included in options) for a topic (if included) or all |
| ROOT_TOPIC/delete/older/hours   | remove the log entries older than x hours (included in options) for a topic (if included) or all |
| ROOT_TOPIC/delete/older/days   | remove the log entries older than x days (included in options) for a topic (if included) or all |
| ROOT_TOPIC/delete/all   | remove all entries for a topic (if included) or all topics |

## Query Commands (NOT IMPLEMENTED YET!!!)
The query options structure are similar to the previous one. First the ```TOPIC_ROOT```followed by the desired command. In the payload should be included a json with the following structure:

```
{
 "client" : "CLIENT_NAME_USED_TO_IDENTIFY_THE_RESPONSE"
 "password" : "YOUR_PASSWORD_FOR_MANAGEMENT_OPTIONS",
 "topic" : "TOPIC"
 "option" : "COMMAND_OPTION" #optional in some cases
 }
```
The complete list of available query commands is the following:

| Command                 | purpose                                 |
| ------------------------|-----------------------------------------|
| ROOT_TOPIC/log/last     | get the last entry for a topic          |
| ROOT_TOPIC/log/minutes  | get the entries from the last x minutes |
| ROOT_TOPIC/log/hours    | get the entries from the last x hours   |
| ROOT_TOPIC/log/days     | get the entries from the last x days    |

The MqttSqlite logger will respond in the same topic with the required information with the following json format:

```
{
 "client" : "CLIENT_NAME_USED_TO_IDENTIFY_THE_RESPONSE"
 "topic" : "TOPIC"
 "values" : [
 	{"timestamp" : "YYYY-MM-ddTHH:mm:ss" , "value":"string_with_value"},
 	....]
 }
```