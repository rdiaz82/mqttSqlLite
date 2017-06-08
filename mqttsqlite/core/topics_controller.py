from mqttsqlite.orm.models import Topic
import json
from mqttsqlite.settings.private_settings import MANAGEMENT_PASSWORD, QUERY_PASSWORD
from .utils import Payload, Utils


class TopicsController (object):

    def add_topic(self, msg):
        received_data = json.loads(msg.payload)
        payload = Utils().validate_data(received_data, MANAGEMENT_PASSWORD, ['password', 'client'])
        if payload.result == 'OK':
            new_topic, created = Topic.get_or_create(name=str(received_data['topic']))
            saved_topics = []
            for topic in Topic.select():
                saved_topics.append(topic.name)
            payload.topics = saved_topics
        return payload.get_json()

    def remove_topic(self, msg):
        received_data = json.loads(msg.payload)
        payload = Utils().validate_data(received_data, MANAGEMENT_PASSWORD, ['password', 'client'])
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
        payload = Utils().validate_data(received_data, QUERY_PASSWORD, ['password', 'client'], topic=False)
        if payload.result == 'OK':
            saved_topics = []
            for topic in Topic.select():
                saved_topics.append(topic.name)
            payload.topics = saved_topics
        return payload.get_json()

    def get_storaged_topics(self):
        return Topic.select()

    def is_topic_subscribed(self, topic):
        if Topic.select().where(Topic.name == topic).count():
            return True
        else:
            return False
