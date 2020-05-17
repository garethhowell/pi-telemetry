pitelemetry
============

Collect data from 1-wire sensors connected to Raspberry Pi and send via mqtt

The main program, `/usr/local/bin/pitelemetry` is designed to be run by `systemd` as a 'simple' service.
It takes one argument - the yaml file that contains the configuration.
The default configuration file is `/etc/pitelemetry.yaml`

An example configuration is: ::

 broker:
    mqtt_client: mynode
    mqtt_broker: mqtt.foo.bar
    mqtt_port: 1833
    update_interval: 60 # seconds
  log_level: debug
  sensors:
    - sensor:
      name: baz_temp
      type: temperature
      device: 28-0417c15da2ae
      topic: tel/foo/baz/temp
    - sensor:
      name: external_temp
      type: temperature
      device: 28-0417c15cf333
      topic: tel/foo/ext/temp

RESTRICTIONS
============

Currently only supports DS18B120 temperature sensors,
but is easily extended to support other types.

INSTALLATION
============

Execute the following from a terminal ::

 sudo pip3 install pitelemetry
 sudo systemctl enable /etc/systemd/system/pitelemetry
 sudo systemctl start pitelemetry.service


pitelemetry currently supports the following sensors:

* DS18B120 temperature sensor

ADDING NEW SENSOR TYPES
=======================

To add a new sensor type:

* Clone the `PiTemperature` class
* Modify the `_read_device()` function as needed
* Add the new sensor to the `sensorTypes` list in `bin/pitelemetry`

TODO
====

Add other 1-wire sensors
