import logging
from .pitemperature import PiTemperature

class TelemetryFactory():
    """ Factory class to create the appropriate telemetry object"""

    def __init__(self):

        self.log = logging.getLogger('__name__')
        self.log.debug("telemetryFactory __init__")

    def create(self, typ, broker, discovery_prefix, sensor, shutdown):
        self.log.debug("telemetryFactory create")
        return globals()[typ](broker, discovery_prefix, sensor, shutdown)
