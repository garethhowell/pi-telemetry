#!/usr/bin/python -p

"""pitelemetry Raspberry Pi telemetry module

A systemd compliant daemon to read data from i2c sensors connected
to a Raspberry Pi and send via MQTT

"""
# Standard libraries
import io, os, sys, glob, time
import logging, socket, traceback

# Specials
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
from threading import Thread
import yaml

class PiTelemetry(threading.Thread):
    """
    PiTelemetry - Threading Class to read the value of the DS18B120 thermometer connected to GPIO 4
    and send the value in Centigrade to the chosen mqtt topic
    """

    broker = None
    source = None
    log = None

    def __init__(self, broker, source):
        self.log = logging.getLogger(__name__)
        self.log.debug("PiTelemetry.__init__()")

        # unpack the config
        self.broker = broker
        self.log.debug("broker = %s", broker)

        self.source = source
        self.log.debug("source = %s", source)


    # Private functions
    def _read_temp_raw(self,device):
        f = open(device, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def _read_temp(self,device):
        lines = self._read_temp_raw(device)
        while lines[0].strip()[-3] != 'Y':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            tempString = lines[1][equals_pos+2:]
            tempC = float(tempString) / 1000.0
            return tempC

    # Define MQTT callback functions
    def on_connect(client, userData, flags, rc):
        self.log.debug("%s, connected to broker", client)

    def on_log(client, obj, level, string):
        self.log.debug(string)

    def start(self):
        """Connect to the broker and start reporting"""

        self.log.debug("PiTelemetry.run()")

        #Setup
        mqttClient = broker['mqtt_client']
        mqttBroker = broker['mqtt_broker']

        mqttTopic = source['topic']
        self.log.debug("mqttClient = %s, mqttBroker=%s, mqttTopic=%s",mqttClient, mqttBroker,mqttTopic)

        w1Device = source['serial']
        self.log.debug("device = %s", w1Device)

        # Make sure we access the right thermometer
        baseDir = '/sys/bus/w1/devices/'
        device = baseDir + w1Device + '/w1_slave'

        # Setup the MQTT client
        client = mqtt.Client(mqttClient) #Create the client object
        client.on_log = self.on_log
        client.on_connect = self.on_connect
        try:
            client.connect(mqttBroker) #, config['mqtt_port'], 60) #Attempt to connect to the broker
        except:
            raise

        #Main Loop
        while True:
            temp = self.read_temp(device)
            self.log.debug("Current temp = %sC", temp)
            try:
                client.publish(mqttTopic, temp) # Publish
            except:
                raise
            time.sleep(broker['updateInterval'])

        #Shutdown
        self.log.debug("Shutting down")
