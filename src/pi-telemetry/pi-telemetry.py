#!/usr/bin/python -p

"""pi-telemetry Raspberry Pi telemetry module

A systemd compliant daemon to read data from i2c sensors connected
to a Raspberry Pi and send via MQTT

"""
# Standard libraries
import io, os, sys, glob, time
import logging

# Specials
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt

class PiTelemetry():
    """
    PiTelemetry - Class to read the value of the DS18B120 thermometer connected to GPIO 4
    and send the value in Centigrade to the chosen mqtt topic
    """

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


    def __init__(self, clientName, mqttBroker, mqttBaseTopic, mqttUsername, mqttPassword, frequency):
        self.log = logging.getLogger(__name__)
        self.log.debug("PiTelemetry.__init__()")

        # Instantiate the local variables
        self.clientName = clientName
        self.mqttBroker = mqttBroker
        self.mqttBaseTopic = mqttBaseTopic
        self.frequency = frequency
        self.log.debug("clientName = %s, mqttBroker=%s, mqttBaseTopic=%s",self.clientName, self.mqttBroker,self.mqttBaseTopic)

        # Make sure we have the right modules installed
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        # Make sure we access the right thermometer
        baseDir = '/sys/bus/w1/devices/'
        deviceFolder = glob.glob(baseDir + '28*')[0]
        self.deviceFile = deviceFolder + '/w1_slave'

        # Setup the MQTT client
        self.client = mqtt.Client(self.clientName) #Create the client object
        self.client.on_log = self.on_log
        self.client.on_connect = self.on_connect
        try:
            self.client.connect(self.mqttBroker, 1883, 60) #Attempt to connect to the broker
        except:
            raise
        
        # Define the topic on which to publish
        self.mqttTopic = self.mqttBaseTopic + "temp"

    def run(self):
        self.log.debug("PiTelemetry.run()")

        #Setup

        #Main Loop
        while True:
            self.temp = self.read_temp()
            print(self.temp)
            try:
                self.client.publish(self.mqttTopic, self.temp) # Publish
            except:
                raise

            time.sleep(frequency)

        #Shutdown
        self.log.debug("Shutting down")

logging.basicConfig(level = logging.DEBUG)
log = logging.getLogger("pi-telemetry")
log.setLevel(logging.DEBUG)
log.info("pi-telemetry started")
mqttClient = 'shed'
mqttBroker = 'mqtt.agdon.net'
mqttBaseTopic = 'tel/19c/shed/'
mqttUsername = ''
mqttPassword = ''
frequency = 60 # seconds between transmissions
pitelemetry = PiTelemetry(mqttClient, mqttBroker, mqttBaseTopic, mqttUsername, mqttPassword, frequency)
log.debug("pitelemetry = " + str(pitelemetry))
pitelemetry.run()
