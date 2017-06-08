import json
from mqttsqlite.settings.private_settings import MANAGEMENT_PASSWORD, QUERY_PASSWORD
from .utils import Payload, Utils
from mqttsqlite.orm.models import Log
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

    def __delete_entries_from_topic_older_than(self, topic, date):
        query = Log.delete().where((Log.timestamp <= datetime.now() - timedelta(seconds=date)) & (Log.topic == topic))
        result = query.execute()
        if result:
            return result
        else:
            return '0'

    def __delete_last_entry_from_topic(self, topic):
        try:
            last_entry = Log.select().where(Log.topic == topic).order_by(Log.id.desc()).get()
            result = last_entry.delete_instance()
            if result == 1:
                return '1'
            else:
                return '0'
        except Log.DoesNotExist:
            return '1'
        except:
            return '0'

    def __get_last_entry_from_topic(self, topic):
        try:
            result = Log.select().where(Log.topic == topic).order_by(Log.timestamp.desc()).get()
            return {'timestamp': result.timestamp.strftime("%Y-%m-%d %H:%M:%S"), 'value': result.value}
        except:
            return {}

    def __time_operations_with_topic_entries(self, operation, msg):
        if operation == 'delete':
            single = self.__delete_last_entry_from_topic
            multiple = self.__delete_entries_from_topic_older_than
        else:
            single = self.__get_last_entry_from_topic
            multiple = self.__get_logs_newer_than

        topic = msg.topic.split('/')
        payload = Payload()
        received_data = json.loads(msg.payload)
        if topic[-1] == 'last':
            payload = Utils().validate_data(received_data, QUERY_PASSWORD, ['password', 'client'])
            if payload.result == 'OK':
                payload.values = [single(received_data['topic'])]
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
                    payload.values = multiple(received_data['topic'], 60 * received_options)
                elif topic[-1] == 'hours':
                    payload.values = multiple(received_data['topic'], 3600 * received_options)
                elif topic[-1] == 'days':
                    payload.values = multiple(received_data['topic'], 86400 * received_options)
        else:
            payload.result = 'KO'
            payload.error = 'Invalid unit time'

        return payload.get_json()

    def get_topic_entries(self, msg):
        return self.__time_operations_with_topic_entries('get', msg)

    def delete_topic_entries(self, msg):
        return self.__time_operations_with_topic_entries('delete', msg)
