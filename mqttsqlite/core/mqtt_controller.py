from topics_controller import TopicsController


class MqttController(object):

    def on_connect(self, client):
        controller = TopicsController()
        storaged_topics = controller.get_storaged_topics()
        for topic in storaged_topics:
            client.subscribe(topic.name)
        return True

    def on_message(self, client, msg):
        return True
