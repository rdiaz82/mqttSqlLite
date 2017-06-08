import json


class Payload:
    password = None
    client = None
    result = None
    options = None
    error = None
    topic = None
    topics = []
    values = None

    def get_dictionary(self):
        payload = {}
        if self.password:
            payload['password'] = self.password

        if self.client:
            payload['client'] = self.client

        if self.result:
            payload['result'] = self.result

        if self.options:
            payload['options'] = self.options

        if self.error:
            payload['error'] = self.error

        if self.topic:
            payload['topic'] = self.topic

        if self.topics:
            payload['topics'] = self.topics

        if self.values:
            payload['values'] = self.values

        return payload

    def get_json(self):
        dict = self.get_dictionary()
        return json.dumps(dict)


class Utils(object):
    def missing_keys(self, received_data, keys, topic=True, options=False):
        if topic:
            keys.append('topic')
        if options:
            keys.append('options')
        for key in keys:
            if key not in received_data:
                return key
        return ''

    def validate_data(self, received_data, password, keys, topic=True, options=False):
        payload = Payload()
        missing_keys = self.missing_keys(received_data, keys, topic, options)
        if missing_keys == '':
            if password == received_data['password']:
                payload.result = 'OK'
            else:
                payload.result = 'KO'
                payload.error = 'Bad Password'
        else:
            payload.result = 'KO'
            payload.error = 'Missing key - ' + missing_keys
        if 'client' in received_data:
            payload.client = received_data['client']
        if 'topic' in received_data:
            payload.topic = received_data['topic']
        return payload
