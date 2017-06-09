from ..orm.models import Setting


def get_query_pass():
    try:
        return Setting.get(Setting.key == 'query_password').value
    except:
        return 'query1234'


def set_query_pass(password):
    try:
        result = Setting.update(value=password).where(Setting.key == 'query_password').execute()
    except:
        pass


def get_management_pass():
    try:
        return Setting.get(Setting.key == 'management_password').value
    except:
        return 'admin1234'


def set_management_pass(password):
    try:
        result = Setting.update(value=password).where(Setting.key == 'management_password').execute()
    except:
        pass


def get_host():
    try:
        return Setting.get(Setting.key == 'mqtt_host').value
    except:
        return 'localhost'


def set_host(host):
    try:
        result = Setting.update(value=host).where(Setting.key == 'mqtt_host').execute()
    except:
        pass


def get_port():
    try:
        return int(Setting.get(Setting.key == 'mqtt_port').value)
    except:
        return 1883


def set_port(port):
    try:
        result = Setting.update(value=port).where(Setting.key == 'mqtt_port').execute()
    except:
        pass


def get_root_topic():
    try:
        return Setting.get(Setting.key == 'root_topic').value
    except:
        return 'logger/'


def set_root_topic(root_topic):
    try:
        result = Setting.update(value=root_topic).where(Setting.key == 'root_topic').execute()
    except:
        pass

# Sqlite database
DATABASE = 'mqtt.db'

# MQTT server settings
MQTT_HOST = get_host()
MQTT_PORT = get_port()

# Base logger topic
ROOT_TOPIC = get_root_topic()

# password for management options
MANAGEMENT_PASSWORD = get_management_pass()
QUERY_PASSWORD = get_query_pass()
