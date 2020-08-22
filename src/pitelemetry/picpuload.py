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


class PiCPULoad(PiTelemetry):
    """
    Concrete class to read CPU load data from the RaspBerry Pi
    """

    def _read_sensor(self, sensor):
        self.log.debug("picpuload _read_sensor")
        p = subprocess.Popen("uptime", shell=True, stdout=subprocess.PIPE).communicate()[0]
        cores = subprocess.Popen("nproc", shell=True, stdout=subprocess.PIPE).communicate()[0]
        cpu_load = p.split("average:")[1].split(",")[0].replace(' ', '')
        cpu_load = float(cpu_load)/int(cores)*100
        cpu_load = round(float(cpu_load), 1)
        return cpu_load
