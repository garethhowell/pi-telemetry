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

class PiTelemetry(Thread):
    """
    PiTelemetry - Threading Class to read the value of the DS18B120 thermometer connected to GPIO 4
    and send the value in Centigrade to the chosen mqtt topic
    """

    broker = None
    source = None
    log = None

    def __init__(self, broker, source):
        ''' Constructor. '''
        Thread.__init__(self)

        # unpack the config
        self.broker = broker
        self.source = source

    # Private functions
    def _read_temp_raw(self,device):
        f = open(device, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def _read_device(self,device):
        lines = self._read_temp_raw(device)
        while lines[0].strip()[-3] != 'Y':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            tempString = lines[1][equals_pos+2:]
            tempC = float(tempString) / 1000.0
            self.log.debug("Current temp = %sC", tempC)
            return tempC

    def run(self):
        """Connect to the broker and start reporting"""

        self.log = logging.getLogger(self.getName())
        self.log.debug("%s running", self.getName())

        #Setup
        mqttClient = self.broker['mqtt_client']+'_'+self.name
        mqttBroker = self.broker['mqtt_broker']

        mqttTopic = self.source['topic']
        self.log.debug("mqttClient = %s, mqttBroker=%s, mqttTopic=%s",mqttClient, mqttBroker,mqttTopic)

        w1Device = self.source['device']
        self.log.debug("device = %s", w1Device)

        # Make sure we access the right device
        baseDir = '/sys/bus/w1/devices/'
        device = baseDir + w1Device + '/w1_slave'

        # Setup the MQTT client
        client = mqtt.Client(mqttClient) #Create the client object
        try:
            client.connect(mqttBroker) #, config['mqtt_port'], 60) #Attempt to connect to the broker
        except:
            raise

        #Main Loop
        while True:
            try:
                data = self._read_device(device)
            except:
                self.log.error("Trying to access invalid device: %s", device)
                self.log.debug("Exiting")
                exit()

            try:
                client.publish(mqttTopic, data) # Publish
            except:
                raise
            time.sleep(self.broker['update_interval'])

        #Shutdown
        self.log.debug("Shutting down")
