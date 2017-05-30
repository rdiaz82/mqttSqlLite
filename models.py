from peewee import *

database = SqliteDatabase('mqtt.db')


class BaseModel(Model):
    class Meta:
        database = database


class Log(BaseModel):
    timestamp = DateTimeField()
    topic = CharField()
    value = CharField()


class topics(BaseModel):
    topic = CharField()


def create_tables():
    database.connect()
    database.create_tables([Log], True)