import os
from setuptools import setup
import sys

dependency_libraries = ['peewee', 'paho-mqtt']

setup(
    name="MqttSqliteLogger",
    packages=["mqttsqlite"],
    test_suite='tests',
    entry_points={
        'console_scripts': ['mqttsqlite = mqttsqlite.mqttsqlite:main']
    },
    version='1.0',
    description='Simple Sqlite logger for MQTT Brokers.',
    author='Roberto Diaz Ortega',
    author_email='info@rdiaz.es',
    url='https://github.com/rdiaz82/mqttSqlLite',
    install_requires=dependency_libraries,
    include_package_data=True,
)