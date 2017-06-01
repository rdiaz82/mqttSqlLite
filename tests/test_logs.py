
import unittest
from playhouse.test_utils import test_database
from peewee import *
from datetime import datetime, timedelta
from mqttsqlite.orm.models import Log, Topic
from tests.utils import msg
from mqttsqlite.core.logs_controller import LogController
import json


test_db = SqliteDatabase('test_database.db')


class TestLogsController(unittest.TestCase):
    def setUp(self):
        self.msg = msg(topic='/test/home/sensor', payload='123445')

    def test_add_log_entry_response_ok(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            logs = LogController()
            result = logs.add_entry(self.msg)
            parsedResponse = json.loads(result)
            self.assertEqual('OK', parsedResponse['result'])

    def test_add_log_entry_already_added(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            logs = LogController()
            result = logs.add_entry(self.msg)
            parsedResponse = json.loads(result)
            self.assertEqual('OK', parsedResponse['result'])
            self.assertEqual(1, Log.select().count())

    def test_get_log_newer_than(self):
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

    def test_get_log_from_desired_topic_newer_than(self):
        with test_database(test_db, (Log, Topic), create_tables=True):
            Log.create(timestamp=datetime.now() - timedelta(seconds=30), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(seconds=20), value="12", topic='/test/topic2')
            Log.create(timestamp=datetime.now() - timedelta(seconds=20), value="12", topic='/test/topic')
            Log.create(timestamp=datetime.now() - timedelta(seconds=10), value="12", topic='/test/topic')
            logs = LogController()
            query_result = logs._LogController__get_logs_newer_than('/test/topic', 25)
            self.assertEqual(2, len(query_result))
if __name__ == '__main__':
    unittest.main()