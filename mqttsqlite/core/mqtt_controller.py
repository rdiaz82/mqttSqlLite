from topics_controller import TopicsController
from ..settings.private_settings import ROOT_TOPIC
import topics_controller
import logs_controller
import re
import json


class MqttController(object):

    def on_connect(self, client):
        controller = TopicsController()
        storaged_topics = controller.get_storaged_topics()
        for topic in storaged_topics:
            client.subscribe(topic.name)
        return True

    def __process_topic(self, client, msg):
        action = re.findall(ROOT_TOPIC + 'topic/(\w*)', msg.topic)[0]
        controller = TopicsController()
        if action:
            if action == 'add':
                result = controller.add_topic(msg)
                result_dic = json.loads(result)
                if result_dic['result'] == 'OK':
                    client.subscribe(result_dic['topic'])
                client.publish(msg.topic, result)
            elif action == 'remove':
                result = controller.remove_topic(msg)
                result_dic = json.loads(result)
                if result_dic['result'] == 'OK':
                    client.unsubscribe(result_dic['topic'])
                client.publish(msg.topic, result)
            elif action == 'list':
                result = controller.list_topics(msg)
                result_dic = json.loads(result)
                client.publish(msg.topic, result)
            else:
                # TODO: return error
                print ('error')

    def on_message(self, client, msg):
        if re.search('^' + ROOT_TOPIC + 'topic/', msg.topic):
            self.__process_topic(client, msg)

        elif re.search('^' + ROOT_TOPIC + 'log/', msg.topic):
            # TODO: log with all variants
            print('logs')
        else:
            # TODO: check if the current topic is one of the topics storaged in the database
            print ('log?')

        return True
