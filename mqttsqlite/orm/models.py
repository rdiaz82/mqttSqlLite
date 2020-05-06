from peewee import *

# todo: refactor to remove global variable and hard coded database name
database = SqliteDatabase('mqtt.db')


class BaseModel(Model):
    class Meta:
        database = database


class Log(BaseModel):
    timestamp = DateTimeField()
    topic = CharField()
    value = CharField()


class Topic(BaseModel):
    name = CharField()


class Setting(BaseModel):
    key = CharField()
    value = CharField()


def create_tables():
    print('Creating_tables')
    database = SqliteDatabase('mqtt.db')

    database.connection()
    database.create_tables([Log, Topic, Setting], safe=True)
    print('Populate Settings')
    Setting.create(key='mqtt_host', value='localhost')
    Setting.create(key='mqtt_port', value='1883')
    Setting.create(key='root_topic', value='logger/')
    Setting.create(key='management_password', value='admin1234')
    Setting.create(key='query_password', value='query1234')
