pitelemetry
============

Simple Python module to collect data from 1-wire sensors and send via mqtt

The main program, `pitelemetry` is designed to be run by `systemd` as a system daemon.
It takes just one (optional) argument - the yaml file that contains the configuration.
The default configuration file is `/etc/pitelemetry.yaml`

An example configuration is:
```
broker:
  mqtt_client: dellups
  mqtt_broker: mqtt.foo.bar
  mqtt_port: 1833
  update_interval: 60 # seconds
log_level: debug
sensors:
  - sensor:
    name: shed_temp
    type: temperature
    device: 28-0417c15da2ff
    topic: tel/baz/shed/temp
  - sensor:
    name: external_temp
    type: temperature
    device: 28-0417c15cf333
    topic: tel/baz/ext/temp
```

pitelemetry currently supports the following sensors:

* DS18B120 temperature sensor

TODO
====

Add other 1-wire sensors
