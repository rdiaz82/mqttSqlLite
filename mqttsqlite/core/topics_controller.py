from ..orm.models import Topic
import json
from ..settings.private_settings import MANAGEMENT_PASSWORD
from utils import Payload


class Topics_Controller:

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

    def add_topic(self, msg):
        payload = Payload()
        received_data = json.loads(msg.payload)

        missing_keys = self.__missing_keys(received_data)
        if missing_keys == '':
            if MANAGEMENT_PASSWORD == received_data['password']:
                payload.result = 'OK'
            else:
                payload.result = 'KO'
                payload.error = 'Bad Password'

            payload.client = str(received_data['client'])
            new_topic = Topic.create(name=str(received_data['topic']))
            new_topic.save()
            saved_topics = []
            for topic in Topic.select():
                saved_topics.append(topic.name)
            payload.topics = saved_topics
        else:
            payload.result = 'KO'
            payload.error = 'Missing key - ' + missing_keys

        return payload.get_json()

