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


    def _read_device(self,device):
        logger.debug("Entering _read_device")
        lines = self._read_temp_raw(device)
        while lines[0].strip()[-3] != 'Y':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            tempString = lines[1][equals_pos+2:]
            tempC = round((float(tempString) / 1000.0),1)
            logger.debug("Current temp = %sC", tempC)
            timestamp = datetime.datetime.now()
            logger.debug("Current time = "+str(timestamp))
            data = {
                "time": timestamp,
                "temp": tempC
            }
            payload = json.dumps(data)
            logger.debug("jsonified data = "+payload)
            
            return payload
