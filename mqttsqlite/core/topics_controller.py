from ..orm.models import Topic
import json
from ..settings.private_settings import MANAGEMENT_PASSWORD, READ_PASSWORD
from utils import Payload


class TopicsController (object):

    def __missing_keys(self, received_data, topic=True, options=False):
        keys = ['password', 'client']
        if topic:
            keys.append('topic')
        if options:
            keys.append('options')
        for key in keys:
            if key not in received_data:
                return key
        return ''

    def __validate_data(self, received_data, password, topic=True, options=False):
        payload = Payload()
        missing_keys = self.__missing_keys(received_data, topic, options)
        if missing_keys == '':
            if password == received_data['password']:
                payload.result = 'OK'
            else:
                payload.result = 'KO'
                payload.error = 'Bad Password'
            payload.client = str(received_data['client'])
        else:
            payload.result = 'KO'
            payload.error = 'Missing key - ' + missing_keys
        return payload

    def add_topic(self, msg):
        received_data = json.loads(msg.payload)
        payload = self.__validate_data(received_data, MANAGEMENT_PASSWORD)
        if payload.result == 'OK':
            new_topic, created = Topic.get_or_create(name=str(received_data['topic']))
            saved_topics = []
            for topic in Topic.select():
                saved_topics.append(topic.name)
            payload.topics = saved_topics
        return payload.get_json()

    def remove_topic(self, msg):
        received_data = json.loads(msg.payload)
        payload = self.__validate_data(received_data, MANAGEMENT_PASSWORD)
        if payload.result == 'OK':
            topic = Topic.select().where(Topic.name == str(received_data['topic']))
            if topic.count() > 0:
                topic[0].delete_instance()
            else:
                payload.result = 'KO'
                payload.error = 'Topic not found'
            saved_topics = []
            for topic in Topic.select():
                saved_topics.append(topic.name)
            payload.topics = saved_topics
        return payload.get_json()

    def list_topics(self, msg):
        received_data = json.loads(msg.payload)
        payload = self.__validate_data(received_data, READ_PASSWORD, topic=False)
        if payload.result == 'OK':
            saved_topics = []
            for topic in Topic.select():
                saved_topics.append(topic.name)
            payload.topics = saved_topics
        return payload.get_json()
