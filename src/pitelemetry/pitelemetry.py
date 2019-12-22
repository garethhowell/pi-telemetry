#!/usr/env python3

"""
Raspberry Pi telemetry module
"""
# Standard libraries
import io, os, sys, glob, time
import logging, socket, traceback

# Specials
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
from threading import Thread
import yaml
import signal


class PiTelemetry(Thread):
    """
    Abstract Threading Class containing all but the details for each sensor.
    Sub-classed by concrete sensor-specific classes.
    """

    broker = None
    source = None
    log = None

    def __init__(self, broker, sensor, shutdown):
        ''' Constructor. '''
        Thread.__init__(self)

        # unpack the config
        self.broker = broker
        self.sensor = sensor
        self.shutdown = shutdown


    # Private functions

    def _read_device(self,device):
        raise NotImplementedError("_read_device is implemented in the sub-classes")


    def run(self):
        """Connect to the broker and start reporting"""

        self.log = logging.getLogger(self.getName())
        self.log.debug("%s is running", self.getName())

        #Setup
        mqttClient = self.broker['mqtt_client']+'_'+self.name
        mqttBroker = self.broker['mqtt_broker']

        mqttTopic = self.sensor['topic']
        self.log.debug("mqttClient = %s, mqttBroker=%s, mqttTopic=%s",mqttClient, mqttBroker,mqttTopic)

        w1Device = self.sensor['device']

        # Make sure we access the right device
        baseDir = '/sys/bus/w1/devices/'
        device = baseDir + w1Device + '/w1_slave'

        # Setup the MQTT client
        client = mqtt.Client(mqttClient) #Create the client object

        #Main Loop
        while not (self.shutdown.isSet()):
            try:
                data = self._read_device(device)
            except:
                self.log.error("Sensor %s is Trying to access invalid device: %s", self.sensor['name'], device)
                self.log.debug("Exiting")
                exit()

            try:
                client.connect(mqttBroker) #, config['mqtt_port'], 60) #Attempt to connect to the broker
                self.log.debug("Connected to broker")
            except:
                self.log.debug("Failed to connect to broker")
                self.log.debug("Exiting")
                raise

            try:
                client.publish(mqttTopic, data) # Publish
                self.log.debug("Published %s to %s", data, mqttTopic)
            except:
                self.log.debug("Failed to publish %s to %s", data, mqttTopic)
                self.log.debug("Exiting")
                raise

            time.sleep(self.broker['update_interval'])

        #Shutdown
        self.log.debug("Sensor shutting down")
