#!/usr/bin/python -p

"""pi-telemetry Raspberry Pi telemetry module

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

class PiTelemetry:
    """
    PiTelemetry - Class to read the value of the DS18B120 thermometer connected to GPIO 4
    and send the value in Centigrade to the chosen mqtt topic
    """

    config = None
    log = None
    updateInterval = None

    def __init__(self, config):
        self.log = logging.getLogger(__name__)
        self.log.debug("PiTelemetry.__init__()")

        # unpack the config
        self.config = config
        self.log.debug("config = %s", config)

        # Make sure we have the right modules installed
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')


    # Private functions
    def read_temp_raw(self):
        f = open(self.deviceFile, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self):
        lines = self.read_temp_raw()
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

    def run(self):
        self.log.debug("PiTelemetry.run()")

        #Setup
        broker = self.config['broker']
        mqttClient = broker['mqtt_client']
        mqttBroker = broker['mqtt_broker']
        updateInterval = broker['update_interval']
        sources = config['sources']
        mqttTopic = sources['internal_temp']['topic']
        self.log.debug("mqttClient = %s, mqttBroker=%s, mqttBaseTopic=%s",self.mqttClient, self.mqttBroker,self.mqttBaseTopic)

        w1Device = config['sources']['internal_temp']['serial']
        self.log.debug("device = %s", self.w1Device)

        # Make sure we access the right thermometer
        baseDir = '/sys/bus/w1/devices/'
        deviceFile = baseDir + self.w1Device + '/w1_slave'

        # Setup the MQTT client
        client = mqtt.Client(self.mqttClient) #Create the client object
        client.on_log = self.on_log
        client.on_connect = self.on_connect
        try:
            client.connect(self.mqttBroker) #, config['mqtt_port'], 60) #Attempt to connect to the broker
        except:
            raise

        #Main Loop
        while True:
            temp = self.read_temp()
            self.log.debug("Current temp = %sC", self.temp)
            try:
                client.publish(self.mqttTopic, self.temp) # Publish
            except:
                raise
            time.sleep(self.updateInterval)

        #Shutdown
        self.log.debug("Shutting down")
