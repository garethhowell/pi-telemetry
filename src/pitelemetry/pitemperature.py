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
from pitelemetry import PiTelemetry

class PiTemperature(PiTelemetry):
    """
    PiTelemetry - Threading Class to read the value of the DS18B120 thermometer connected to GPIO 4
    and send the value in Centigrade to the chosen mqtt topic
    """

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
