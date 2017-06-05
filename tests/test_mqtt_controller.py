import unittest
from playhouse.test_utils import test_database
from peewee import *
from datetime import datetime, timedelta
from mqttsqlite.orm.models import Log, Topic
from tests.utils import msg, Mock_Client
from mqttsqlite.core.logs_controller import LogController
from mqttsqlite.core.mqtt_controller import MqttController
from mqttsqlite.core.utils import Time_Range
import mqttsqlite.settings.private_settings as Settings
import json

test_db = SqliteDatabase('test_database.db')


class TestMqttController(unittest.TestCase):
    def setUp(self):
        self.client = Mock_Client()
        self.client.subscribe('/test/topic/test1')
        self.client.subscribe('/test/topic/test2')
        self.client.subscribe('/test/topic/test3')
        # self.payload = {}
        # self.payload['client'] = 'testClient'
        # self.payload['password'] = Settings.QUERY_PASSWORD
        # self.payload['topic'] = '/test/topic'
        # self.payload['options'] = '25'
        # self.msg = msg(topic=Settings.ROOT_TOPIC + '/topics/add', payload=json.dumps(self.payload))

    def test_on_connect(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.client.subscribed_topics = []
            Topic.create(name='/test/topic/test1')
            Topic.create(name='/test/topic/test2')
            Topic.create(name='/test/topic/test3')
            mqtt_controller = MqttController()
            mqtt_controller.on_connect(self.client)
            self.assertEqual(3, len(self.client.subscribed_topics))

    # PENDING TESTS
    # test_on_message add topic 
    # test_on_message remove valid topic
    # test_on_message remove invalid topic
    # test_on_message list topics
    # test_on_message list topics with wrong password
    # test_on_message add log entry valid topics
    # test_on_message add log entry invalid topics
    # test_on_message get last log entry valid topics
    # test_on_message get last log entry invalid topics
    # test_on_message entries newer than x minutes from valid topic
    # test_on_message entries newer than x hours from valid topic
    # test_on_message entries newer than x days from valid topic
    # test_on_message entries newer than x days from invalid topic
    # test_on_message delete entries older than x minutes from valid topic
    # test_on_message delete entries older than x hours from valid topic
    # test_on_message delete entries older than x days from valid topic
    # test_on_message delete entries older than x days from invalid topic

if __name__ == '__main__':
    unittest.main()