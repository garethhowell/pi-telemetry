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
    mqttClient = None
    mqttBroker = None
    mqttBaseTopic = None

    def __init__(self, config):
        self.log = logging.getLogger(__name__)
        self.log.debug("PiTelemetry.__init__()")

        # Instantiate the local variables
        self.config = config
        self.log.debug("config = %s", config)
        self.mqttClient = config['mqtt_client']
        self.mqttBroker = config['mqtt_broker']
        self.mqttTopic = config['sources']['internal_temp']['topic']
        self.updateInterval = config['update_interval']
        self.log.debug("mqttClient = %s, mqttBroker=%s, mqttBaseTopic=%s",self.mqttClient, self.mqttBroker,self.mqttBaseTopic)

        self.w1Device = config['sources']['internal_temp']['serial']
        self.log.debug("device = %s", self.w1Device)

        # Make sure we have the right modules installed
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        # Make sure we access the right thermometer
        baseDir = '/sys/bus/w1/devices/'
        #deviceFolder = glob.glob(baseDir + '28*')[0]
        self.deviceFile = baseDir + self.w1Device + '/w1_slave'

        # Setup the MQTT client
        self.client = mqtt.Client(self.mqttClient) #Create the client object
        self.client.on_log = self.on_log
        self.client.on_connect = self.on_connect
        try:
            self.client.connect(self.mqttBroker) #, config['mqtt_port'], 60) #Attempt to connect to the broker
        except:
            raise

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

        #Main Loop
        while True:
            self.temp = self.read_temp()
            self.log.debug("Current temp = %sC", self.temp)
            try:
                self.client.publish(self.mqttTopic, self.temp) # Publish
            except:
                raise
            time.sleep(self.updateInterval)

        #Shutdown
        self.log.debug("Shutting down")

# Testing Code

def main(argv):
    if not argv or len(argv) != 1:
        print ('pi-telemetry <config file>')
    else:
        with open(argv[0], 'r') as configFile:
            try:
                config = yaml.safe_load(configFile)
            except yaml.YAMLError as exc:
                print(exc)
        # Initialise logging
        logging.basicConfig(level = {'info':logging.INFO, 'debug':logging.DEBUG}[config['log_level']])
        log = logging.getLogger("pi-telemetry")
        log.setLevel({'info':logging.INFO, 'debug':logging.DEBUG}[config['log_level']])
        log.info("pi-telemetry started")
        log.debug(config)

        # Instantiate the PiTelemetry object
        server = PiTelemetry(config)
        log.debug("server = " + str(server))

        # Off we go
        server.run()

if __name__ == "__main__":
    main(sys.argv[1:])
