class TelemetryFactory():
    """ Factory class to create the appropriate telemetry object"""

    def __init(self):
        pass

    def create(self, typ):
        targetClass = type.capitalize()
        return globals()[targetClass]
