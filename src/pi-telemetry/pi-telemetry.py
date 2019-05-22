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
import paho.mqtt.publish as publish

class PiTelemetry():
    """
    PiTelemetry - Read the value of the DS18B120 thermometer connected to GPIO 4
    and send to the chosen mqtt topic
    """

    # Private functions
    def read_temp_raw(self):
        f = open(self.device_file, 'r')
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
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c

    def __init__(self, mqtt_broker, mqtt_base_topic, mqtt_username, mqtt_password):
        self.log = logging.getLogger(__name__)
        self.log.debug("PiTelemetry.__init__()")

        # Instantiate the local variable
        self.broker = mqtt_broker
        self.base_topic = mqtt_base_topic
        self.log.debug("broker=%s, base_topic=%s",self.broker,self.base_topic)

        # Make sure we have the right modules installed
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        # Make sure we access the right thermometer
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        self.device_file = device_folder + '/w1_slave'

        # Set up the MQTT client
        self.Broker = 'mqtt-host'
        self.auth = {
                'username': mqtt_username,
                'password': mqtt_password
        }


    def run(self):
        self.log.debug("PiTelemetry.run()")

        #Setup

        #Main Loop
        while True:
            print(self.read_temp())
            time.sleep(1)

        #Shutdown
        self.log.debug("Shutting down")

logging.basicConfig(level = logging.DEBUG)
log = logging.getLogger("pi-telemetry")
log.setLevel(logging.DEBUG)
log.info("pi-telemetry started")
mqtt_broker = 'mqtt.agdon.net'
mqtt_base_topic = 'dev/19c/shed/temp/'
mqtt_username = ''
mqtt_password = ''
pitelemetry = PiTelemetry(mqtt_broker, mqtt_base_topic, mqtt_username, mqtt_password)
log.debug("pitelemetry = " + str(pitelemetry))
pitelemetry.run()
