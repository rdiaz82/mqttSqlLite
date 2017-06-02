import json
from ..settings.private_settings import MANAGEMENT_PASSWORD, QUERY_PASSWORD
from utils import Payload, Utils, Time_Range
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
            query_logs.append({'timestamp': log.timestamp.strftime("%Y-%m-%d %H:%M:%S"), 'value': log.value})
        return query_logs

    def __get_last_entry_from_topic(self, topic):
        try:
            result = Log.select().where(Log.topic == topic).order_by(Log.timestamp.desc()).get()
            return {'timestamp': result.timestamp.strftime("%Y-%m-%d %H:%M:%S"), 'value': result.value}
        except:
            return {}

    def get_topic_entries(self, msg):
        topic = msg.topic.split('/')
        payload = Payload()
        received_data = json.loads(msg.payload)
        if topic[-1] == 'last':
            payload = Utils().validate_data(received_data, QUERY_PASSWORD, ['password', 'client'])
            if payload.result == 'OK':
                payload.values = [self.__get_last_entry_from_topic(received_data['topic'])]
        elif topic[-1] == 'minutes' or topic[-1] == 'hours' or topic[-1] == 'days':
            payload = Utils().validate_data(received_data, QUERY_PASSWORD, ['password', 'client'], options=True)
            if payload.result == 'OK':
                try:
                    received_options = int(received_data['options'])
                except:
                    payload.result = 'KO'
                    payload.error = 'Invalid Options Value'
                    return payload.get_json()

                if topic[-1] == 'minutes':
                    payload.values = self.__get_logs_newer_than(received_data['topic'], Time_Range.minutes.value * received_options)
                elif topic[-1] == 'hours':
                    payload.values = self.__get_logs_newer_than(received_data['topic'], Time_Range.hours.value * received_options)
                elif topic[-1] == 'days':
                    payload.values = self.__get_logs_newer_than(received_data['topic'], Time_Range.days.value * received_options)
        else:
            return 'error'
        return payload.get_json()


