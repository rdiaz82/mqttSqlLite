import json


class Payload:
    password = None
    client = None
    result = None
    options = None
    error = None
    topic = None
    topics = None

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

        return payload

    def get_json(self):
        dict = self.get_dictionary()
        return json.dumps(dict)