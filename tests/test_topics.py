
import unittest
from playhouse.test_utils import test_database
from peewee import *
from datetime import datetime
from mqttsqlite.orm.models import Log, Topic
from mqttsqlite.core.topics_controller import Topics_Controller
import json
import mqttsqlite.settings.private_settings as Settings
from tests.utils import msg

test_db = SqliteDatabase('test_database.db')


class TestTopicAdd(unittest.TestCase):
    def setUp(self):
        self.payload = {}
        self.payload['client'] = "testClient"
        self.payload['password'] = Settings.MANAGEMENT_PASSWORD
        self.payload['topic'] = "/test/topic/1"
        self.msg = msg(topic=Settings.ROOT_TOPIC + '/topics/add', payload=json.dumps(self.payload))

    def test_add_topic_response_ok(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            topic = Topics_Controller()
            result = topic.add_topic(self.msg)
            parsedResponse = json.loads(result)
            self.assertEqual('OK', parsedResponse['result'])

    def test_add_topic_correct_client(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            topic = Topics_Controller()
            result = topic.add_topic(self.msg)
            parsedResponse = json.loads(result)
            self.assertEqual(self.payload['client'], parsedResponse['client'])

    def test_add_topic_bad_pass(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.payload['password'] = "BadPass"
            self.msg.payload = json.dumps(self.payload)
            topic = Topics_Controller()
            result = topic.add_topic(self.msg)
            parsedResponse = json.loads(result)
            self.assertEqual('KO', parsedResponse['result'])
            self.assertEqual('Bad Password', parsedResponse['error'])

    def test_add_topic_missing_client(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.payload.pop('client', None)
            self.msg.payload = json.dumps(self.payload)
            topic = Topics_Controller()
            result = topic.add_topic(self.msg)
            parsedResponse = json.loads(result)
            self.assertEqual('KO', parsedResponse['result'])
            self.assertEqual('Missing key - client', parsedResponse['error'])

    def test_add_topic_missing_topic(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.payload.pop('topic', None)
            self.msg.payload = json.dumps(self.payload)
            topic = Topics_Controller()
            result = topic.add_topic(self.msg)
            parsedResponse = json.loads(result)
            self.assertEqual('KO', parsedResponse['result'])
            self.assertEqual('Missing key - topic', parsedResponse['error'])

    def test_add_topic_missing_password(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.payload.pop('password', None)
            self.msg.payload = json.dumps(self.payload)
            topic = Topics_Controller()
            result = topic.add_topic(self.msg)
            parsedResponse = json.loads(result)
            self.assertEqual('KO', parsedResponse['result'])
            self.assertEqual('Missing key - password', parsedResponse['error'])

    def test_add_topic_already_added(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            topic = Topics_Controller()
            result = topic.add_topic(self.msg)
            parsedResponse = json.loads(result)
            self.assertIn(self.payload['topic'], parsedResponse['topics'])

    def test_add_topic_multiple_saved_topics(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            topic = Topics_Controller()
            result = topic.add_topic(self.msg)
            result = topic.add_topic(self.msg)
            result = topic.add_topic(self.msg)
            parsedResponse = json.loads(result)
            print(result)
            self.assertEqual(3, len(parsedResponse['topics']))


class TestMissingKeys(unittest.TestCase):

    def test_valid_json(self):
        payload_dic = {}
        payload_dic['client'] = "testClient"
        payload_dic['password'] = "BadPass"
        payload_dic['topic'] = "/test/topic/1"
        topic = Topics_Controller()
        self.assertEqual('', topic._Topics_Controller__missing_keys(payload_dic))

    def test_missing_keys_missing_client(self):
        payload_dic = {}
        payload_dic['password'] = "BadPass"
        payload_dic['topic'] = "/test/topic/1"
        topic = Topics_Controller()
        self.assertEqual('client', topic._Topics_Controller__missing_keys(payload_dic))

    def test_missing_keys_missing_password(self):
        payload_dic = {}
        payload_dic['client'] = "testClient"
        payload_dic['topic'] = "/test/topic/1"
        topic = Topics_Controller()
        self.assertEqual('password', topic._Topics_Controller__missing_keys(payload_dic))

    def test_missing_keys_missing_topic(self):
        payload_dic = {}
        payload_dic['client'] = "testClient"
        payload_dic['password'] = "BadPass"
        topic = Topics_Controller()
        self.assertEqual('topic', topic._Topics_Controller__missing_keys(payload_dic))

    def test_missing_keys_missing_options(self):
        payload_dic = {}
        payload_dic['client'] = "testClient"
        payload_dic['password'] = "BadPass"
        payload_dic['topic'] = "/test/topic/1"
        topic = Topics_Controller()
        self.assertEqual('options', topic._Topics_Controller__missing_keys(payload_dic, options=True))

    def test_missing_keys_ignoring_topic(self):
        payload_dic = {}
        payload_dic['client'] = "testClient"
        payload_dic['password'] = "BadPass"
        payload_dic['topic'] = "/test/topic/1"
        topic = Topics_Controller()
        self.assertEqual('', topic._Topics_Controller__missing_keys(payload_dic, topic=False))

if __name__ == '__main__':
    unittest.main()