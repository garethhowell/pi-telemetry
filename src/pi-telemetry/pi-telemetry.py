#!/usr/bin/python -p

"""pi-telemetry Raspberry Pi telemetry module

A systemd compliant daemon to read data from i2c sensors connected
to a Raspberry Pi and send via MQTT

"""
# Standard libraries
import io, os, sys
from time import time, sleep
import logging

# Specials
import RPi.GPIO as GPIO

class PiTelemetry():
    """
    PiTelemetry -
    """
    def __init__(self, mqtt_broker, mqtt_base_topic):
        self.log = logging.getlogger(__name__)
        self.log.debug("PiTelemetry.__init__()")

        self.broker = mqtt_broker
        self.base_topic = mqtt_base_topic
        self.log.debug("broker=%s, base_topic=%s",self.broker,self.base_topic)

    def run(self):
        self.log.debug("PiTelemetry.run()")

        #Setup

        #Main Loop

        #Shutdown
        self.log.debug("Shutting down")
