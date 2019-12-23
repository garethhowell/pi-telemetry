import logging
from .pitemperature import PiTemperature

class TelemetryFactory():
    """ Factory class to create the appropriate telemetry object"""

    def create(self, typ, broker, sensor, shutdown):
        return globals()[typ](broker, sensor, shutdown)
