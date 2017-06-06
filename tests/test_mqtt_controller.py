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

        self.payload = {}
        self.payload['client'] = 'testClient'
        self.payload['password'] = Settings.QUERY_PASSWORD
        self.payload['topic'] = '/test/topic'
        self.payload['options'] = '25'
        self.msg = msg(topic=Settings.ROOT_TOPIC + 'topic/add', payload=json.dumps(self.payload))

    def test_on_connect(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.client.subscribed_topics = []
            Topic.create(name='/test/topic/test1')
            Topic.create(name='/test/topic/test2')
            Topic.create(name='/test/topic/test3')
            mqtt_controller = MqttController()
            mqtt_controller.on_connect(self.client)
            self.assertEqual(3, len(self.client.subscribed_topics))

    def test_on_message_add_topic(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.client.subscribed_topics = []
            self.client.subscribe('/test/topic/test1')
            self.client.subscribe('/test/topic/test2')
            self.client.subscribe('/test/topic/test3')

            self.payload['options'] = None
            self.payload['topic'] = '/test/valid_topic/to_add'
            self.payload['password'] = Settings.MANAGEMENT_PASSWORD
            self.msg = msg(topic=Settings.ROOT_TOPIC + 'topic/add', payload=json.dumps(self.payload))
            mqtt_controller = MqttController()
            result = mqtt_controller.on_message(self.client, self.msg)
            self.assertEqual(4, len(self.client.subscribed_topics))

    def test_on_message_remove_topic(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.client.subscribed_topics = []
            self.client.subscribe('/test/topic/test1')
            self.client.subscribe('/test/topic/test2')
            self.client.subscribe('/test/topic/test3')
            Topic.create(name='/test/topic/test1')
            Topic.create(name='/test/topic/test2')
            Topic.create(name='/test/topic/test3')

            self.payload['options'] = None
            self.payload['topic'] = '/test/topic/test3'
            self.payload['password'] = Settings.MANAGEMENT_PASSWORD
            self.msg = msg(topic=Settings.ROOT_TOPIC + 'topic/remove', payload=json.dumps(self.payload))
            mqtt_controller = MqttController()
            result = mqtt_controller.on_message(self.client, self.msg)
            self.assertEqual(2, len(self.client.subscribed_topics))
            self.assertEqual(2, Topic.select().count())

    def test_on_message_remove_not_valid_topic(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.client.subscribed_topics = []
            self.client.subscribe('/test/topic/test1')
            self.client.subscribe('/test/topic/test2')
            self.client.subscribe('/test/topic/test3')
            Topic.create(name='/test/topic/test1')
            Topic.create(name='/test/topic/test2')
            Topic.create(name='/test/topic/test3')

            self.payload['options'] = None
            self.payload['topic'] = '/test/topic/not_valid_topic'
            self.payload['password'] = Settings.MANAGEMENT_PASSWORD
            self.msg = msg(topic=Settings.ROOT_TOPIC + 'topic/remove', payload=json.dumps(self.payload))
            mqtt_controller = MqttController()
            result = mqtt_controller.on_message(self.client, self.msg)
            self.assertEqual(3, len(self.client.subscribed_topics))
            self.assertEqual('Topic not found', json.loads(self.client.last_publish)['error'])

    def test_on_message_list_topics_bad_password(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.client.subscribed_topics = []
            self.client.subscribe('/test/topic/test1')
            self.client.subscribe('/test/topic/test2')
            self.client.subscribe('/test/topic/test3')
            Topic.create(name='/test/topic/test1')
            Topic.create(name='/test/topic/test2')
            Topic.create(name='/test/topic/test3')

            self.payload['options'] = None
            self.payload['topic'] = '/test/topic/not_valid_topic'
            self.payload['password'] = 'badPassword'
            self.msg = msg(topic=Settings.ROOT_TOPIC + 'topic/list', payload=json.dumps(self.payload))
            mqtt_controller = MqttController()
            result = mqtt_controller.on_message(self.client, self.msg)
            self.assertFalse('topics' in json.loads(self.client.last_publish))
            self.assertEqual('Bad Password', json.loads(self.client.last_publish)['error'])

    def test_on_message_list_topics_bad_password(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.client.subscribed_topics = []
            self.client.subscribe('/test/topic/test1')
            self.client.subscribe('/test/topic/test2')
            self.client.subscribe('/test/topic/test3')
            Topic.create(name='/test/topic/test1')
            Topic.create(name='/test/topic/test2')
            Topic.create(name='/test/topic/test3')

            self.payload['options'] = None
            self.payload['password'] = Settings.QUERY_PASSWORD
            self.msg = msg(topic=Settings.ROOT_TOPIC + 'topic/list', payload=json.dumps(self.payload))
            mqtt_controller = MqttController()
            result = mqtt_controller.on_message(self.client, self.msg)
            self.assertTrue('OK', json.loads(self.client.last_publish)['result'])
            self.assertEqual(3, len(json.loads(self.client.last_publish)['topics']))
    # PENDING TESTS
    # TODO: test_on_message add log entry valid topics
    # TODO: test_on_message add log entry invalid topics
    # TODO: test_on_message get last log entry valid topics
    # TODO: test_on_message get last log entry invalid topics
    # TODO: test_on_message entries newer than x minutes from valid topic
    # TODO: test_on_message entries newer than x hours from valid topic
    # TODO: test_on_message entries newer than x days from valid topic
    # TODO: test_on_message entries newer than x days from invalid topic
    # TODO: test_on_message delete entries older than x minutes from valid topic
    # TODO: test_on_message delete entries older than x hours from valid topic
    # TODO: test_on_message delete entries older than x days from valid topic
    # TODO: test_on_message delete entries older than x days from invalid topic

if __name__ == '__main__':
    unittest.main()