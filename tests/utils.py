
class msg:
    payload = None
    topic = None

    def __init__(self, topic, payload):
        self.payload = payload
        self.topic = topic