from .topics_controller import TopicsController
from .logs_controller import LogController
from ..settings.private_settings import ROOT_TOPIC
from .utils import Payload
import re
import json


class MqttController(object):

    def on_connect(self, client):
        controller = TopicsController()
        storaged_topics = controller.get_storaged_topics()
        for topic in storaged_topics:
            client.subscribe(topic.name)
        client.subscribe(ROOT_TOPIC + 'topic/#')
        client.subscribe(ROOT_TOPIC + 'log/#')

    def __process_topic(self, client, msg):
        action = re.findall(ROOT_TOPIC + 'topic/(\w*)', msg.topic)[0]
        controller = TopicsController()
        if action:
            if action == 'add':
                result = controller.add_topic(msg)
                result_dic = json.loads(result)
                if result_dic['result'] == 'OK':
                    client.subscribe(result_dic['topic'])
                client.publish(ROOT_TOPIC + 'response', result)
            elif action == 'remove':
                result = controller.remove_topic(msg)
                result_dic = json.loads(result)
                if result_dic['result'] == 'OK':
                    client.unsubscribe(result_dic['topic'])
                client.publish(ROOT_TOPIC + 'response', result)
            elif action == 'list':
                result = controller.list_topics(msg)
                result_dic = json.loads(result)
                client.publish(ROOT_TOPIC + 'response', result)
            else:
                response = Payload()
                response.result = 'KO'
                response.error = 'Error: Invalid Topic Option'
                received_msg = json.loads(msg.payload)
                if 'client' in received_msg:
                    response.client = received_msg['client']
                client.publish(ROOT_TOPIC + 'response', response.get_json())

    def __process_log(self, client, msg):
        action = re.findall(ROOT_TOPIC + 'log/(\w*)', msg.topic)[0]
        if action == 'query':
            controller = LogController()
            result = controller.get_topic_entries(msg)
            client.publish(ROOT_TOPIC + 'response', result)
        elif action == 'delete':
            controller = LogController()
            result = controller.delete_topic_entries(msg)
            client.publish(ROOT_TOPIC + 'response', result)
        else:
            response = Payload()
            response.result = 'KO'
            response.error = 'Error: Invalid Log Option'
            received_msg = json.loads(msg.payload)
            if 'client' in received_msg:
                response.client = received_msg['client']
            client.publish(ROOT_TOPIC + 'response', response.get_json())

    def on_message(self, client, msg):
        if re.search('^' + ROOT_TOPIC + 'topic/', msg.topic):
            self.__process_topic(client, msg)

        elif re.search('^' + ROOT_TOPIC + 'log/', msg.topic):
            self.__process_log(client, msg)
        else:
            topic_controller = TopicsController()
            if topic_controller.is_topic_subscribed(msg.topic):
                controller = LogController()
                controller.add_entry(msg)
