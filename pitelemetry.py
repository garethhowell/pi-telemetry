#!/usr/bin/env python3
"""
Main script for the PiTelemetry module.
Contains utility functions and main invocation code
Designed to be invoked from command line or from systemd
    :param -c --configfile: YAML configuration file (default: /etc/pitelemetry.yaml)
    :param -l --loglevel: logging level (default: INFO)
"""

import sys
# Change this to add more sensor types
from pitelemetry import TelemetryFactory, PiTemperature
from time import sleep
import argparse
import logging, logging.config
import yaml
import os
import threading
import signal
import keyboard, termios, tty

# Change this to add more sensor types
sensor_types = {'temperature': 'PiTemperature', 'humidity': 'PiHumidity'}
log = ""

def sigcatch(signum, frame):
    """Primitive Signal Handler """

    if signum == signal.SIGTERM:
        log.info("SIGTERM received, shutting down")
        shutdown.set()


def getchar():
    """ Utility function to read a character from the keyboard """

    ch = ' '
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main(argv):
    """ Create and run a thread for each sensor being monitored """

    # Set default arguments and overide with command line arguments if provided
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", default="/etc/pitelemetry.yaml",
            help="location of YAML configuration file (default: %(default)s")
    parser.add_argument("-l", "--loglevel", default="INFO",
            help="define logging level (default: %(default)s")

    args = parser.parse_args()

    # Initialise logging
    # Convert parser.loglevel to numeric logging level
    logging_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(logging_level, int):
        raise ValueError('Invalid logging level: %s', loglevel)

    # Create Logger object
    log = logging.getLogger("pitelemetry")
    log.setLevel(logging_level)
    fh = logging.FileHandler('pitelemetry.log')
    ch = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    #log.addHandler(fh)
    log.addHandler(ch)

    log.info("pitelemetry started")

    # Get telemetry configuration
    with open(args.configfile, 'r') as configFile:
        try:
            config =yaml.safe_load(configFile)
        except yaml.YAMLError as exc:
            print(exc)
            exit(1)

    # Make sure we have the right sensor modules installed
    # Change this to add more sensor types
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')

    # Set an event to catch a call to shutdown
    shutdown = threading.Event()
    shutdown.clear()

    #Catch SIGTERM
    signal.signal(signal.SIGTERM, sigcatch)

    # Parse the YAML config
    broker = config['broker']
    sensors = config['sensors']
    log.debug("sensors = %s", sensors)
    threads = {}
    telemetry_obj = TelemetryFactory()

    i =0
    # Instantiate a thread for each sensor
    for sensor_inst in sensors:
        log.debug("sensor_inst = %s", sensor_inst)
        # Check we have a real sensor
        if not (sensor_inst['sensor'] is None):

            # get the sensor dictionary
            new_sensor = sensor_inst['sensor']
            log.debug("new_sensor = %s", new_sensor)

            # get the type of sensor we are dealing with
            sensor_type = sensor_types[new_sensor['type']]
            log.debug('Creating new thread of class %s to deal with sensor: %s', sensor_type, new_sensor)

            # start a new thread to handle the sensor. using sensor_type to decide which class to instantiate
            threads[i] = telemetry_obj.create(sensor_type, broker, new_sensor, shutdown)
            threads[i].setName(new_sensor['name'])
            threads[i].setDaemon(True)
            threads[i].start()
            log.debug("Thread %s created and started", new_sensor['name'])
        # On to the next block
        i += 1

    # Loop until we are signalled to shutdown
    while not shutdown.isSet():
        if sys.stdin.isatty():
            char = getchar()
            if char == "q":
                log.debug("shut down signalled from keyboard")

                # Signal the threads to shutdown
                shutdown.set()

        sleep(1)

    # Shutdown
    log.debug("Shutting down")
    for j in range(0,i-1):
        threads[j].join()
    log.info("PiTelemetry Shutdown")

# Kick things off if we are invoked as a module `python -m pitelemetry`
if __name__ == "__main__":
    main(sys.argv[1:])
