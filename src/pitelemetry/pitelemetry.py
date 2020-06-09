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

    def __init__(self, broker, discovery_prefix, sensor, shutdown):
        ''' 
        Constructor.
            :param broker: the address of the MQTT broker
            :param discovery_prefix: the prefix that Home Assistant will look for during MQTT Discovery
            :param sensor: yaml dictionary describing the 1-wire device we are addressing
            :param shutdown: the event used to end the thread
        '''
        self.log=logging.getLogger(__name__)
        self.log.debug('pitelemetry __init__')
        Thread.__init__(self)
        self.log.debug('broker = %s, discovery_prefix = %s, sensor = %s', broker, discovery_prefix, sensor)

        # unpack the config
        self.broker = broker
        self.discovery_prefix = discovery_prefix
        self.sensor = sensor
        self.shutdown = shutdown


    # Private functions

    def _register_device(self, sensor):
        """Register the sensor with Home Assistant"""
        self.log=logging.getLogger(__name__)
        self.log.debug("Registering sensor with Home Assistant. sensor: %s", sensor)

    def _read_sensor(self, sensor):
        raise NotImplementedError("_read_sensor is implemented in the sub-classes")

    def connected(client, userdata, flags, rc):
        """Callback function for when the client receives a CONNACK response from the broker """
        self.log=logging.getLogger(__name__)
        self.log.debug("%s connected with result code %s", client, str(rc))
        self.connected = True

    def disconnected(client):
        """Callback function for when client disconnects from broker"""
        self.log=logging.getLogger(__name__)
        self.log.debug("Client disconnected from broker! Exiting")
        sys.exit(1)

    def message(client, userdata, msg):
        """Callback function for when the client receives a message from the broker"""
        self.log=logging.getLogger(__name__)
        self.log.debug("Message received from broker. topic: %s, message: %s", msg.topic, str(msg.payload))

    def run(self):
        """Connect to the broker, register the sensor and start reporting"""
        self.log=logging.getLogger(__name__)
        self.log.debug("pitelemetry run")
        self.log.debug("%s is running", __name__)

        # Setup parameters for connection to broker
        mqtt_client = self.broker['mqtt_client']+'_'+self.name
        mqtt_broker = self.broker['mqtt_broker']
        mqtt_user = self.broker['mqtt_user']
        mqtt_password = self.broker['mqtt_password']

        # Setup topic and sensor
        mqtt_topic = self.sensor['state_topic']
        self.log.debug("mqtt_client = %s, mqtt_broker=%s, mqtt_topic=%s",mqtt_client, mqtt_broker,mqtt_topic)
        w1_device = self.sensor['device']

        # Make sure we access the right device
        base_dir = '/sys/bus/w1/devices/'
        sensor = base_dir + w1_device + '/w1_slave'

        # Create an MQTT client instance
        # client = MQTTClient(mqttUser, mqttPassword, mqttBroker, False) # Use insecure connection to this internal broker
        client = MQTTClient(mqtt_user, mqtt_password, mqtt_broker, False) # Use insecure connection to this internal broker

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

            # Register the sensor with Home Assistant (if used)
            if not self.discovery_prefix == "":
                self.log.debug("registering sensor with Home Assistant. sensor: %s, registration topic: %s, value: %s", sensor, topic, sensor_string)

            # Start reading device data and publishing to broker
            while True:
                data = self._read_sensor(sensor)
                client.publish(mqtt_topic, data) # Publish
                self.log.debug("Published %s to %s", data, mqtt_topic)
                time.sleep(self.broker['update_interval'])

        #Shutdown
        self.log.debug("Sensor shutting down")
