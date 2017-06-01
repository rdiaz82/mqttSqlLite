
import unittest
from playhouse.test_utils import test_database
from peewee import *
from datetime import datetime
from mqttsqlite.orm.models import Log, Topic
from mqttsqlite.core.topics_controller import TopicsController
import json
import mqttsqlite.settings.private_settings as Settings
from tests.utils import msg
from mqttsqlite.core.utils import Utils


test_db = SqliteDatabase('test_database.db')


class TestTopicsController(unittest.TestCase):
    def setUp(self):
        self.payload = {}
        self.payload['client'] = "testClient"
        self.payload['password'] = Settings.MANAGEMENT_PASSWORD
        self.payload['topic'] = "/test/topic/1"
        self.msg = msg(topic=Settings.ROOT_TOPIC + '/topics/add', payload=json.dumps(self.payload))

    def test_add_topic_response_ok(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            topic = TopicsController()
            result = topic.add_topic(self.msg)
            parsedResponse = json.loads(result)
            self.assertEqual('OK', parsedResponse['result'])

    def test_add_topic_correct_client(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            topic = TopicsController()
            result = topic.add_topic(self.msg)
            parsedResponse = json.loads(result)
            self.assertEqual(self.payload['client'], parsedResponse['client'])

    def test_add_topic_bad_pass(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.payload['password'] = "BadPass"
            self.msg.payload = json.dumps(self.payload)
            topic = TopicsController()
            result = topic.add_topic(self.msg)
            parsedResponse = json.loads(result)
            self.assertEqual('KO', parsedResponse['result'])
            self.assertEqual('Bad Password', parsedResponse['error'])

    def test_add_topic_missing_client(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.payload.pop('client', None)
            self.msg.payload = json.dumps(self.payload)
            topic = TopicsController()
            result = topic.add_topic(self.msg)
            parsedResponse = json.loads(result)
            self.assertEqual('KO', parsedResponse['result'])
            self.assertEqual('Missing key - client', parsedResponse['error'])

    def test_add_topic_missing_topic(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.payload.pop('topic', None)
            self.msg.payload = json.dumps(self.payload)
            topic = TopicsController()
            result = topic.add_topic(self.msg)
            parsedResponse = json.loads(result)
            self.assertEqual('KO', parsedResponse['result'])
            self.assertEqual('Missing key - topic', parsedResponse['error'])

    def test_add_topic_missing_password(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.payload.pop('password', None)
            self.msg.payload = json.dumps(self.payload)
            topic = TopicsController()
            result = topic.add_topic(self.msg)
            parsedResponse = json.loads(result)
            self.assertEqual('KO', parsedResponse['result'])
            self.assertEqual('Missing key - password', parsedResponse['error'])

    def test_add_topic_already_added(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            topic = TopicsController()
            result = topic.add_topic(self.msg)
            parsedResponse = json.loads(result)
            self.assertIn(self.payload['topic'], parsedResponse['topics'])

    def test_add_topic_multiple_saved_topics(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            fixture = Topic.create(name='test/topic/test/xx')
            fixture = Topic.create(name='test/topic/test/xxx')
            topic = TopicsController()
            result = topic.add_topic(self.msg)
            parsedResponse = json.loads(result)
            self.assertEqual(3, len(parsedResponse['topics']))

    def test_remove_topic_delete_existing_topic(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            fixture = Topic.create(name='/test/topic/1')
            fixture = Topic.create(name='/test/topic/2')
            fixture = Topic.create(name='/test/topic/3')
            fixture = Topic.create(name='/test/topic/4')
            topic = TopicsController()
            result = topic.remove_topic(self.msg)
            parsedResponse = json.loads(result)
            self.assertEqual(3, len(parsedResponse['topics']))

    def test_remove_topic_delete_non_existing_topic(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            fixture = Topic.create(name='/test/topic/2')
            fixture = Topic.create(name='/test/topic/3')
            fixture = Topic.create(name='/test/topic/4')
            fixture = Topic.create(name='/test/topic/5')
            topic = TopicsController()
            result = topic.remove_topic(self.msg)
            parsedResponse = json.loads(result)
            self.assertEqual('KO', parsedResponse['result'])
            self.assertEqual('Topic not found', parsedResponse['error'])
            self.assertEqual(4, len(parsedResponse['topics']))

    def test_list_topics(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.payload['password'] = Settings.QUERY_PASSWORD
            self.msg.payload = json.dumps(self.payload)
            fixture = Topic.create(name='/test/topic/2')
            fixture = Topic.create(name='/test/topic/3')
            fixture = Topic.create(name='/test/topic/4')
            fixture = Topic.create(name='/test/topic/5')
            topic = TopicsController()
            result = topic.list_topics(self.msg)
            parsedResponse = json.loads(result)
            self.assertEqual('OK', parsedResponse['result'])
            self.assertEqual(4, len(parsedResponse['topics']))


class TestMissingKeys(unittest.TestCase):

    def test_valid_json(self):
        payload_dic = {}
        payload_dic['client'] = "testClient"
        payload_dic['password'] = "BadPass"
        payload_dic['topic'] = "/test/topic/1"
        topic = TopicsController()
        self.assertEqual('', Utils().missing_keys(payload_dic, ['password', 'client']))

    def test_missing_keys_missing_client(self):
        payload_dic = {}
        payload_dic['password'] = "BadPass"
        payload_dic['topic'] = "/test/topic/1"
        topic = TopicsController()
        self.assertEqual('client', Utils().missing_keys(payload_dic, ['password', 'client']))

    def test_missing_keys_missing_password(self):
        payload_dic = {}
        payload_dic['client'] = "testClient"
        payload_dic['topic'] = "/test/topic/1"
        topic = TopicsController()
        self.assertEqual('password', Utils().missing_keys(payload_dic, ['password', 'client']))

    def test_missing_keys_missing_topic(self):
        payload_dic = {}
        payload_dic['client'] = "testClient"
        payload_dic['password'] = "BadPass"
        topic = TopicsController()
        self.assertEqual('topic', Utils().missing_keys(payload_dic, ['password', 'client']))

    def test_missing_keys_missing_options(self):
        payload_dic = {}
        payload_dic['client'] = "testClient"
        payload_dic['password'] = "BadPass"
        payload_dic['topic'] = "/test/topic/1"
        topic = TopicsController()
        self.assertEqual('options', Utils().missing_keys(payload_dic, ['password', 'client'], options=True))

    def test_missing_keys_ignoring_topic(self):
        payload_dic = {}
        payload_dic['client'] = "testClient"
        payload_dic['password'] = "BadPass"
        payload_dic['topic'] = "/test/topic/1"
        topic = TopicsController()
        self.assertEqual('', Utils().missing_keys(payload_dic, ['password', 'client'], topic=False))

if __name__ == '__main__':
    unittest.main()