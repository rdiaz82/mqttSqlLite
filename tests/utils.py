
class msg(object):
    payload = None
    topic = None

    def __init__(self, topic, payload):
        self.payload = payload
        self.topic = topic


class Mock_Client(object):
    subscribed_topics = []
    last_publish = None

    def subscribe(self, topic):
        self.subscribed_topics.append(topic)

    def unsubscribe(self, topic):
        self.subscribed_topics.remove(topic)

    def publish(self, topic, payload):
        self.last_publish = payload
