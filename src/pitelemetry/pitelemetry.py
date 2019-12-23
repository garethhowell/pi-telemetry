#!/usr/env python3

"""
Raspberry Pi telemetry module
"""
# Standard libraries
import io, os, sys, glob, time
import logging, socket, traceback

# Specials
import RPi.GPIO as GPIO
from .mqtt import MQTTClient
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
        self.log=logging.getLogger(__name__)

        # unpack the config
        self.broker = broker
        self.sensor = sensor
        self.shutdown = shutdown


    # Private functions

    def _read_device(self,device):
        raise NotImplementedError("_read_device is implemented in the sub-classes")


    def connected(client, userdata, flags, rc):
        """Callback function for when the client receives a CONNACK response from the broker """
        self.log.debug("%s connected with result code %s", client, str(rc))
        self.connected = True

    def disconnected(client):
        """Callback function for when client disconnects from broker"""
        self.log.debug("Client disconnected from broker! Exiting")
        sys.exit(1)

    def message(client, userdata, msg):
        """Callback function for when the client receives a message from the broker"""
        self.log.debug("Message received from broker. topic: %s, message: %s", msg.topic, str(msg.payload))

    def run(self):
        """Connect to the broker and start reporting"""

        self.log = logging.getLogger("pitelemetry")
        self.log.debug("%s is running", __name__)

        # Setup parameters for connection to broker
        mqttClient = self.broker['mqtt_client']+'_'+self.name
        mqttBroker = self.broker['mqtt_broker']
        mqttUser = self.broker['mqtt_user']
        mqttPassword = self.broker['mqtt_password']

        # Setup topic and sensor
        mqttTopic = self.sensor['topic']
        self.log.debug("mqttClient = %s, mqttBroker=%s, mqttTopic=%s",mqttClient, mqttBroker,mqttTopic)
        w1Device = self.sensor['device']

        # Make sure we access the right device
        baseDir = '/sys/bus/w1/devices/'
        device = baseDir + w1Device + '/w1_slave'

        # Create an MQTT client instance
        client = MQTTClient(mqttUser, mqttPassword, mqttBroker, False) # Use insecure connection to this internal broker

        # Setup the callbacks
        client.on_connect = self.connected
        client.on_disconnect = self.disconnected
        client.on_message = self.message

        #Main Loop
        while not (self.shutdown.isSet()):
            #Connect to the broker
            client.connect()
            #Set the client to loop in the background
            client.loop_background()

            # Start reading device data and publishing to broker
            while True:
                data = self._read_device(device)
                client.publish(mqttTopic, data) # Publish
                self.log.debug("Published %s to %s", data, mqttTopic)
                time.sleep(self.broker['update_interval'])

        #Shutdown
        self.log.debug("Sensor shutting down")
