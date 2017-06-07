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

    def test_on_message_list_topics_good_password(self):
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

    def test_on_message_invalid_topic_action(self):
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
            self.msg = msg(topic=Settings.ROOT_TOPIC + 'topic/invalid_option', payload=json.dumps(self.payload))
            mqtt_controller = MqttController()
            result = mqtt_controller.on_message(self.client, self.msg)
            self.assertTrue('KO', json.loads(self.client.last_publish)['result'])
            self.assertEqual('Error: Invalid Topic Option', json.loads(self.client.last_publish)['error'])

    def test_on_message_add_log_entry_to_valid_topic(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.client.subscribed_topics = []
            self.client.subscribe('/test/topic/test1')
            Topic.create(name='/test/topic/test1')
            self.msg = msg(topic='/test/topic/test1', payload='12')
            mqtt_controller = MqttController()
            result = mqtt_controller.on_message(self.client, self.msg)
            self.assertEqual(1, Log.select().count())

    def test_on_message_add_log_entry_to_not_valid_topic(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.client.subscribed_topics = []
            self.client.subscribe('/test/topic/test1')
            Topic.create(name='/test/topic/test1')
            self.msg = msg(topic='/test/topic/test2', payload='12')
            mqtt_controller = MqttController()
            result = mqtt_controller.on_message(self.client, self.msg)
            self.assertEqual(0, Log.select().count())

    def test_on_message_get_last_entry_from_valid_topic(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.client.subscribed_topics = []
            self.client.subscribe('/test/topic/test1')
            self.client.subscribe('/test/topic/test2')
            self.client.subscribe('/test/topic/test3')
            Topic.create(name='/test/topic/test1')
            Topic.create(name='/test/topic/test2')
            Topic.create(name='/test/topic/test3')
            Log.create(timestamp=datetime.now(), topic='/test/topic/test1', value='10')
            Log.create(timestamp=datetime.now(), topic='/test/topic/test2', value='11')
            Log.create(timestamp=datetime.now(), topic='/test/topic/test1', value='12')

            self.payload['options'] = None
            self.payload['password'] = Settings.QUERY_PASSWORD
            self.payload['topic'] = '/test/topic/test1'
            self.msg = msg(topic=Settings.ROOT_TOPIC + 'log/query/last', payload=json.dumps(self.payload))
            mqtt_controller = MqttController()
            result = mqtt_controller.on_message(self.client, self.msg)
            self.assertTrue('OK', json.loads(self.client.last_publish)['result'])
            self.assertEqual('12', json.loads(self.client.last_publish)['values'][0]['value'])

    def test_on_message_get_last_entry_from_invalid_topic(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.client.subscribed_topics = []
            self.client.subscribe('/test/topic/test1')
            self.client.subscribe('/test/topic/test2')
            self.client.subscribe('/test/topic/test3')
            Topic.create(name='/test/topic/test1')
            Topic.create(name='/test/topic/test2')
            Topic.create(name='/test/topic/test3')
            Log.create(timestamp=datetime.now(), topic='/test/topic/test1', value='10')
            Log.create(timestamp=datetime.now(), topic='/test/topic/test2', value='11')
            Log.create(timestamp=datetime.now(), topic='/test/topic/test1', value='12')

            self.payload['options'] = None
            self.payload['password'] = Settings.QUERY_PASSWORD
            self.payload['topic'] = '/test/topic/test_invalid'
            self.msg = msg(topic=Settings.ROOT_TOPIC + 'log/query/last', payload=json.dumps(self.payload))
            mqtt_controller = MqttController()
            result = mqtt_controller.on_message(self.client, self.msg)
            self.assertTrue('OK', json.loads(self.client.last_publish)['result'])
            self.assertFalse(json.loads(self.client.last_publish)['values'][0])

    def test_get_entries_newer_than_25_minutes(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.client.subscribe('/test/topic/test1')
            self.client.subscribe('/test/topic/test2')
            self.client.subscribe('/test/topic/test3')
            Topic.create(name='/test/topic/test1')
            Topic.create(name='/test/topic/test2')
            Topic.create(name='/test/topic/test3')

            Log.create(timestamp=datetime.now() - timedelta(minutes=30), value="12", topic='/test/topic/test1')
            Log.create(timestamp=datetime.now() - timedelta(minutes=20), value="12", topic='/test/topic2/test2')
            Log.create(timestamp=datetime.now() - timedelta(minutes=20), value="12", topic='/test/topic/test1')
            Log.create(timestamp=datetime.now() - timedelta(minutes=10), value="12", topic='/test/topic/test1')
            self.payload['options'] = 25
            self.payload['password'] = Settings.QUERY_PASSWORD
            self.payload['topic'] = '/test/topic/test1'
            self.msg = msg(topic=Settings.ROOT_TOPIC + 'log/query/minutes', payload=json.dumps(self.payload))
            mqtt_controller = MqttController()
            result = mqtt_controller.on_message(self.client, self.msg)
            self.assertEqual(2, len(json.loads(self.client.last_publish)['values']))

    def test_get_entries_newer_than_25_hours(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.client.subscribe('/test/topic/test1')
            self.client.subscribe('/test/topic/test2')
            self.client.subscribe('/test/topic/test3')
            Topic.create(name='/test/topic/test1')
            Topic.create(name='/test/topic/test2')
            Topic.create(name='/test/topic/test3')

            Log.create(timestamp=datetime.now() - timedelta(hours=30), value="12", topic='/test/topic/test1')
            Log.create(timestamp=datetime.now() - timedelta(hours=20), value="12", topic='/test/topic2/test2')
            Log.create(timestamp=datetime.now() - timedelta(hours=20), value="12", topic='/test/topic/test1')
            Log.create(timestamp=datetime.now() - timedelta(hours=10), value="12", topic='/test/topic/test1')
            self.payload['options'] = 25
            self.payload['password'] = Settings.QUERY_PASSWORD
            self.payload['topic'] = '/test/topic/test1'
            self.msg = msg(topic=Settings.ROOT_TOPIC + 'log/query/hours', payload=json.dumps(self.payload))
            mqtt_controller = MqttController()
            result = mqtt_controller.on_message(self.client, self.msg)
            self.assertEqual(2, len(json.loads(self.client.last_publish)['values']))

    def test_get_entries_newer_than_25_days(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.client.subscribe('/test/topic/test1')
            self.client.subscribe('/test/topic/test2')
            self.client.subscribe('/test/topic/test3')
            Topic.create(name='/test/topic/test1')
            Topic.create(name='/test/topic/test2')
            Topic.create(name='/test/topic/test3')

            Log.create(timestamp=datetime.now() - timedelta(days=30), value="12", topic='/test/topic/test1')
            Log.create(timestamp=datetime.now() - timedelta(days=20), value="12", topic='/test/topic2/test2')
            Log.create(timestamp=datetime.now() - timedelta(days=20), value="12", topic='/test/topic/test1')
            Log.create(timestamp=datetime.now() - timedelta(days=10), value="12", topic='/test/topic/test1')
            self.payload['options'] = 25
            self.payload['password'] = Settings.QUERY_PASSWORD
            self.payload['topic'] = '/test/topic/test1'
            self.msg = msg(topic=Settings.ROOT_TOPIC + 'log/query/days', payload=json.dumps(self.payload))
            mqtt_controller = MqttController()
            result = mqtt_controller.on_message(self.client, self.msg)
            self.assertEqual(2, len(json.loads(self.client.last_publish)['values']))

    def test_get_entries_with_invalid_time_range(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.client.subscribe('/test/topic/test1')
            self.client.subscribe('/test/topic/test2')
            self.client.subscribe('/test/topic/test3')
            Topic.create(name='/test/topic/test1')
            Topic.create(name='/test/topic/test2')
            Topic.create(name='/test/topic/test3')

            Log.create(timestamp=datetime.now() - timedelta(days=30), value="12", topic='/test/topic/test1')
            Log.create(timestamp=datetime.now() - timedelta(days=20), value="12", topic='/test/topic2/test2')
            Log.create(timestamp=datetime.now() - timedelta(days=20), value="12", topic='/test/topic/test1')
            Log.create(timestamp=datetime.now() - timedelta(days=10), value="12", topic='/test/topic/test1')
            self.payload['options'] = 25
            self.payload['password'] = Settings.QUERY_PASSWORD
            self.payload['topic'] = '/test/topic/test1'
            self.msg = msg(topic=Settings.ROOT_TOPIC + 'log/query/invalid_time', payload=json.dumps(self.payload))
            mqtt_controller = MqttController()
            result = mqtt_controller.on_message(self.client, self.msg)
            self.assertEqual('KO', json.loads(self.client.last_publish)['result'])
            self.assertEqual('Invalid unit time', json.loads(self.client.last_publish)['error'])

    def test_on_message_delete_last_entry_from_topic(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.client.subscribed_topics = []
            self.client.subscribe('/test/topic/test1')
            self.client.subscribe('/test/topic/test2')
            self.client.subscribe('/test/topic/test3')
            Topic.create(name='/test/topic/test1')
            Topic.create(name='/test/topic/test2')
            Topic.create(name='/test/topic/test3')
            Log.create(timestamp=datetime.now(), topic='/test/topic/test1', value='10')
            Log.create(timestamp=datetime.now(), topic='/test/topic/test2', value='11')
            Log.create(timestamp=datetime.now(), topic='/test/topic/test1', value='12')

            self.payload['options'] = None
            self.payload['password'] = Settings.QUERY_PASSWORD
            self.payload['topic'] = '/test/topic/test1'
            self.msg = msg(topic=Settings.ROOT_TOPIC + 'log/delete/last', payload=json.dumps(self.payload))
            mqtt_controller = MqttController()
            result = mqtt_controller.on_message(self.client, self.msg)
            result_logs = Log.select().where(Log.topic == '/test/topic/test1')
            self.assertTrue('OK', json.loads(self.client.last_publish)['result'])
            self.assertEqual(1, result_logs.count())
            self.assertEqual('10', result_logs[0].value)

    def test_delete_entries_older_than_25_minutes(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.client.subscribe('/test/topic/test1')
            self.client.subscribe('/test/topic/test2')
            self.client.subscribe('/test/topic/test3')
            Topic.create(name='/test/topic/test1')
            Topic.create(name='/test/topic/test2')
            Topic.create(name='/test/topic/test3')

            Log.create(timestamp=datetime.now() - timedelta(minutes=40), value="12", topic='/test/topic/test1')
            Log.create(timestamp=datetime.now() - timedelta(minutes=30), value="12", topic='/test/topic/test1')
            Log.create(timestamp=datetime.now() - timedelta(minutes=20), value="12", topic='/test/topic2/test2')
            Log.create(timestamp=datetime.now() - timedelta(minutes=20), value="12", topic='/test/topic/test1')
            Log.create(timestamp=datetime.now() - timedelta(minutes=10), value="12", topic='/test/topic/test1')
            self.payload['options'] = 25
            self.payload['password'] = Settings.QUERY_PASSWORD
            self.payload['topic'] = '/test/topic/test1'
            self.msg = msg(topic=Settings.ROOT_TOPIC + 'log/delete/minutes', payload=json.dumps(self.payload))
            mqtt_controller = MqttController()
            result = mqtt_controller.on_message(self.client, self.msg)
            result_logs = Log.select().where(Log.topic == '/test/topic/test1')
            self.assertEqual(2, result_logs.count())

    def test_delete_entries_older_than_25_hours(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.client.subscribe('/test/topic/test1')
            self.client.subscribe('/test/topic/test2')
            self.client.subscribe('/test/topic/test3')
            Topic.create(name='/test/topic/test1')
            Topic.create(name='/test/topic/test2')
            Topic.create(name='/test/topic/test3')

            Log.create(timestamp=datetime.now() - timedelta(hours=40), value="12", topic='/test/topic/test1')
            Log.create(timestamp=datetime.now() - timedelta(hours=30), value="12", topic='/test/topic/test1')
            Log.create(timestamp=datetime.now() - timedelta(hours=20), value="12", topic='/test/topic2/test2')
            Log.create(timestamp=datetime.now() - timedelta(hours=20), value="12", topic='/test/topic/test1')
            Log.create(timestamp=datetime.now() - timedelta(hours=10), value="12", topic='/test/topic/test1')
            self.payload['options'] = 25
            self.payload['password'] = Settings.QUERY_PASSWORD
            self.payload['topic'] = '/test/topic/test1'
            self.msg = msg(topic=Settings.ROOT_TOPIC + 'log/delete/hours', payload=json.dumps(self.payload))
            mqtt_controller = MqttController()
            result = mqtt_controller.on_message(self.client, self.msg)
            result_logs = Log.select().where(Log.topic == '/test/topic/test1')
            self.assertEqual(2, result_logs.count())

    def test_delete_entries_older_than_25_days(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.client.subscribe('/test/topic/test1')
            self.client.subscribe('/test/topic/test2')
            self.client.subscribe('/test/topic/test3')
            Topic.create(name='/test/topic/test1')
            Topic.create(name='/test/topic/test2')
            Topic.create(name='/test/topic/test3')

            Log.create(timestamp=datetime.now() - timedelta(days=40), value="12", topic='/test/topic/test1')
            Log.create(timestamp=datetime.now() - timedelta(days=30), value="12", topic='/test/topic/test1')
            Log.create(timestamp=datetime.now() - timedelta(days=20), value="12", topic='/test/topic2/test2')
            Log.create(timestamp=datetime.now() - timedelta(days=20), value="12", topic='/test/topic/test1')
            Log.create(timestamp=datetime.now() - timedelta(days=10), value="12", topic='/test/topic/test1')
            self.payload['options'] = 25
            self.payload['password'] = Settings.QUERY_PASSWORD
            self.payload['topic'] = '/test/topic/test1'
            self.msg = msg(topic=Settings.ROOT_TOPIC + 'log/delete/days', payload=json.dumps(self.payload))
            mqtt_controller = MqttController()
            result = mqtt_controller.on_message(self.client, self.msg)
            result_logs = Log.select().where(Log.topic == '/test/topic/test1')
            self.assertEqual(2, result_logs.count())

    def test_delete_entries_older_than_25_days_from_invalid_topic(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.client.subscribe('/test/topic/test1')
            self.client.subscribe('/test/topic/test2')
            self.client.subscribe('/test/topic/test3')
            Topic.create(name='/test/topic/test1')
            Topic.create(name='/test/topic/test2')
            Topic.create(name='/test/topic/test3')

            Log.create(timestamp=datetime.now() - timedelta(days=40), value="12", topic='/test/topic/test1')
            Log.create(timestamp=datetime.now() - timedelta(days=30), value="12", topic='/test/topic/test1')
            Log.create(timestamp=datetime.now() - timedelta(days=20), value="12", topic='/test/topic2/test2')
            Log.create(timestamp=datetime.now() - timedelta(days=20), value="12", topic='/test/topic/test1')
            Log.create(timestamp=datetime.now() - timedelta(days=10), value="12", topic='/test/topic/test1')
            self.payload['options'] = 25
            self.payload['password'] = Settings.QUERY_PASSWORD
            self.payload['topic'] = '/test/topic/invalid_topic'
            self.msg = msg(topic=Settings.ROOT_TOPIC + 'log/delete/days', payload=json.dumps(self.payload))
            mqtt_controller = MqttController()
            result = mqtt_controller.on_message(self.client, self.msg)
            self.assertEqual('OK', json.loads(self.client.last_publish)['result'])
            self.assertEqual('0', json.loads(self.client.last_publish)['values'])

    def test_on_message_invalid_log_action(self):
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
            self.msg = msg(topic=Settings.ROOT_TOPIC + 'log/invalid_option', payload=json.dumps(self.payload))
            mqtt_controller = MqttController()
            result = mqtt_controller.on_message(self.client, self.msg)
            self.assertTrue('KO', json.loads(self.client.last_publish)['result'])
            self.assertEqual('Error: Invalid Log Option', json.loads(self.client.last_publish)['error'])


if __name__ == '__main__':
    unittest.main()
