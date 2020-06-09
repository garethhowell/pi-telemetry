#!/usr/bin/env python3

# Standard libraries
import io, os, sys, glob, time
import logging, socket, traceback

# Specials
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
from threading import Thread
import yaml
from .pitelemetry import PiTelemetry
import json
import datetime


class PiTemperature(PiTelemetry):
    """
    Concrete class to read data from a DS18B120 sensor and return json structure
    """

    # Private functions
    def _read_temp_raw(self,device):
        f = open(device, 'r')
        lines = f.readlines()
        f.close()
        return lines


    def _read_sensor(self, sensor):
        self.log=loggin.getLogger(__name)
        self.log.debug("pitemperature _read_sensor")
        try:
            lines = self._read_temp_raw(sensor)
        except Exception as ex:
            self.log.error("Failed to read data from sensor", exc_info=True)
            self.log.debug("Exiting")
            sys.exit(1)
        while lines[0].strip()[-3] != 'Y':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_C = round((float(temp_string) / 1000.0),1)
            self.log.debug("Current temp = %sC", temp_C)
            timestamp = datetime.datetime.now()
            self.log.debug("Current time = "+str(timestamp))
            data = {
                    "sType": 9,
                    "nValue": 0,
                    #"sValue": '%i;%i;%i' % ( tempC, 42, 1 )
                    "sValue": temp_C
            }
            payload = json.dumps(data)
            self.log.debug("jsonified data = "+payload)

            return payload
