
import unittest
from playhouse.test_utils import test_database
from peewee import *
from datetime import datetime, timedelta
from mqttsqlite.orm.models import Log, Topic
from tests.utils import msg
from mqttsqlite.core.logs_controller import LogController
from mqttsqlite.core.utils import Time_Range
import mqttsqlite.settings.private_settings as Settings
import json


test_db = SqliteDatabase('test_database.db')


class TestLogsController(unittest.TestCase):
    def setUp(self):
        self.payload = {}
        self.payload['client'] = 'testClient'
        self.payload['password'] = Settings.QUERY_PASSWORD
        self.payload['topic'] = '/test/topic'
        self.payload['options'] = '25'
        self.msg = msg(topic=Settings.ROOT_TOPIC + '/topics/add', payload=json.dumps(self.payload))

    def test_add_log_entry_response_ok(self):
        message = msg(topic='/test/home/sensor', payload='123445')
        with test_database(test_db, (Log, Topic), create_tables=True):
            logs = LogController()
            result = logs.add_entry(message)
            parsedResponse = json.loads(result)
            self.assertEqual('OK', parsedResponse['result'])

    def test_add_log_entry(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            message = msg(topic='/test/home/sensor', payload='123445')
            logs = LogController()
            result = logs.add_entry(message)
            parsedResponse = json.loads(result)
            self.assertEqual('OK', parsedResponse['result'])
            self.assertEqual(1, Log.select().count())

    def test_private_method_get_log_newer_than(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            Log.create(timestamp=datetime.now() - timedelta(seconds=60), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(seconds=50), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(seconds=40), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(seconds=30), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(seconds=20), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(seconds=10), value="12", topic='/test/topic')
            logs = LogController()
            query_result = logs._LogController__get_logs_newer_than('/test/topic', 25)
            self.assertEqual(2, len(query_result))

    def test_private_method_get_log_from_desired_topic_newer_than(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            Log.create(timestamp=datetime.now() - timedelta(seconds=30), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(seconds=20), value="12", topic='/test/topic2')
            Log.create(timestamp=datetime.now() - timedelta(seconds=20), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(seconds=10), value="12", topic='/test/topic')
            logs = LogController()
            query_result = logs._LogController__get_logs_newer_than('/test/topic', 25)
            self.assertEqual(2, len(query_result))

    def test_private_method_get_last_entry_from_topic(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            Log.create(timestamp=datetime.now() - timedelta(seconds=30), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(seconds=20), value="12", topic='/test/topic2')
            Log.create(timestamp=datetime.now() - timedelta(seconds=20), value="12", topic='/test/topic')
            timestamp = datetime.now()
            Log.create(timestamp=timestamp, value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now(), value="12", topic='/test/topic2')
            Log.create(timestamp=datetime.now(), value="12", topic='/test/topic3')
            logs = LogController()
            query_result = logs._LogController__get_last_entry_from_topic('/test/topic')
            self.assertEqual(timestamp.strftime("%Y-%m-%d %H:%M:%S"), query_result['timestamp'])

    def test_private_method_get_last_entry_from_invalid_topic(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            Log.create(timestamp=datetime.now() - timedelta(seconds=30), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(seconds=20), value="12", topic='/test/topic2')
            Log.create(timestamp=datetime.now() - timedelta(seconds=20), value="12", topic='/test/topic')
            timestamp = datetime.now()
            Log.create(timestamp=timestamp, value="12", topic='/test/topic')
            logs = LogController()
            query_result = logs._LogController__get_last_entry_from_topic('/test/topic3')
            self.assertEqual({}, query_result)

    def test_private_method_get_last_entry_from_topic(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            Log.create(timestamp=datetime.now() - timedelta(seconds=30), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(seconds=20), value="12", topic='/test/topic2')
            Log.create(timestamp=datetime.now() - timedelta(seconds=20), value="12", topic='/test/topic')
            timestamp = datetime.now()
            Log.create(timestamp=timestamp, value="12", topic='/test/topic')
            logs = LogController()
            query_result = logs._LogController__get_last_entry_from_topic('/test/topic')
            self.assertEqual(timestamp.strftime("%Y-%m-%d %H:%M:%S"), query_result['timestamp'])

    def test_get_last_entry_from_topic(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.msg.topic = Settings.ROOT_TOPIC + '/log/last'
            Log.create(timestamp=datetime.now() - timedelta(seconds=30), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(seconds=20), value="12", topic='/test/topic2')
            Log.create(timestamp=datetime.now() - timedelta(seconds=20), value="12", topic='/test/topic')
            timestamp = datetime.now()
            Log.create(timestamp=timestamp, value="12", topic='/test/topic')
            logs = LogController()
            query_result = logs.get_topic_entries(self.msg)
            dic_result = json.loads(query_result)
            self.assertEqual(timestamp.strftime("%Y-%m-%d %H:%M:%S"), dic_result['values'][0]['timestamp'])

    def test_get_entries_newer_than_25_minutes(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.msg.topic = Settings.ROOT_TOPIC + '/log/minutes'
            Log.create(timestamp=datetime.now() - timedelta(minutes=30), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(minutes=20), value="12", topic='/test/topic2')
            Log.create(timestamp=datetime.now() - timedelta(minutes=20), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(minutes=10), value="12", topic='/test/topic')
            logs = LogController()
            query_result = logs.get_topic_entries(self.msg)
            dic_result = json.loads(query_result)
            self.assertEqual(2, len(dic_result['values']))

    def test_get_entries_newer_than_25_hours(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.msg.topic = Settings.ROOT_TOPIC + '/log/hours'
            Log.create(timestamp=datetime.now() - timedelta(hours=30), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(hours=20), value="12", topic='/test/topic2')
            Log.create(timestamp=datetime.now() - timedelta(hours=20), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(hours=10), value="12", topic='/test/topic')
            logs = LogController()
            query_result = logs.get_topic_entries(self.msg)
            dic_result = json.loads(query_result)
            self.assertEqual(2, len(dic_result['values']))

    def test_get_entries_newer_than_25_days(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.msg.topic = Settings.ROOT_TOPIC + '/log/days'
            Log.create(timestamp=datetime.now() - timedelta(days=30), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(days=20), value="12", topic='/test/topic2')
            Log.create(timestamp=datetime.now() - timedelta(days=20), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(days=10), value="12", topic='/test/topic')
            logs = LogController()
            query_result = logs.get_topic_entries(self.msg)
            dic_result = json.loads(query_result)
            self.assertEqual(2, len(dic_result['values']))

    def test_get_entries_newer_than_25_days_invalid_password(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.msg.topic = Settings.ROOT_TOPIC + '/log/days'
            self.payload['password'] = 'badPassword'
            self.msg.payload = json.dumps(self.payload)
            Log.create(timestamp=datetime.now() - timedelta(days=30), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(days=20), value="12", topic='/test/topic2')
            Log.create(timestamp=datetime.now() - timedelta(days=20), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(days=10), value="12", topic='/test/topic')
            logs = LogController()
            query_result = logs.get_topic_entries(self.msg)
            dic_result = json.loads(query_result)
            self.assertEqual('KO', dic_result['result'])
            self.assertFalse('values' in dic_result)

    def test_get_entries_newer_than_25_days_invalid_options(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            self.msg.topic = Settings.ROOT_TOPIC + '/log/days'
            self.payload['options'] = 'invalidOptions'
            self.msg.payload = json.dumps(self.payload)
            Log.create(timestamp=datetime.now() - timedelta(days=30), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(days=20), value="12", topic='/test/topic2')
            Log.create(timestamp=datetime.now() - timedelta(days=20), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(days=10), value="12", topic='/test/topic')
            logs = LogController()
            query_result = logs.get_topic_entries(self.msg)
            dic_result = json.loads(query_result)
            self.assertEqual('KO', dic_result['result'])
            self.assertFalse('values' in dic_result)

if __name__ == '__main__':
    unittest.main()
