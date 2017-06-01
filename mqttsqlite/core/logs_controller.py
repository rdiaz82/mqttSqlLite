import json
from ..settings.private_settings import MANAGEMENT_PASSWORD, QUERY_PASSWORD
from utils import Payload, Utils
from ..orm.models import Log
from datetime import datetime, timedelta


class LogController(object):

    def add_entry(self, msg):
        payload = Payload()
        if hasattr(msg, 'topic') and hasattr(msg, 'payload'):
            log_register = Log.create(timestamp=datetime.now(), topic=msg.topic, value=str(msg.payload))
            payload.topic = 'topic'
            payload.result = 'OK'
        else:
            payload.result = 'KO'
        return payload.get_json()

    def __get_logs_newer_than(self, topic, date_initial):
        query = Log.select().where((Log.timestamp.between(datetime.now() - timedelta(seconds=date_initial), datetime.now())) & (Log.topic == topic))
        query_logs = []
        for log in query:
            query_logs.append({'timestamp': log.timestamp, 'value': log.value})
        return query_logs

    def __get_last_entry_from_topic(self, topic):
        try:
            result = Log.select().where(Log.topic == topic).order_by(Log.timestamp.desc()).get()
            return {'timestamp': result.timestamp, 'value': result.value}
        except:
            return {}

    def get_topic_entries(self, msg):
        topic = msg.topic.split('/')
        payload = Payload()
        received_data = json.loads(msg.payload)
        if topic[-1] == 'last':
            payload = Utils().validate_data(received_data, QUERY_PASSWORD, ['password', 'client'])
            if payload.result == 'OK':
                return 'last'
        elif topic[-1] == 'minutes' or topic[-1] == 'hours' or topic[-1] == 'days':
            return 'range'
        else:
            return 'error'



