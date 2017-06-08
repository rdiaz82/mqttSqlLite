import os
from setuptools import setup
import sys

with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")

dependency_libraries = ['peewee', 'paho-mqtt']
if sys.version_info[0] == 2:
    dependency_libraries.append('enum')

setup(
    name="MqttSqlite Logger",
    packages=["mqttsqlite"],
    test_suite='tests',
    entry_points={
        'console_scripts': ['mqttsqlite = mqttsqlite.mqttsqlite:main']
    },
    version=1.0,
    description='Simple Sqlite logger for MQTT Brokers.',
    long_description=long_descr,
    author='Roberto Diaz Ortega',
    author_email='info@rdiaz.es',
    url='https://github.com/rdiaz82/mqttSqlLite',
    install_requires=dependency_libraries,
)