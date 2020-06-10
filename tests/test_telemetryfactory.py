import pytest

import threading

from .. import TelemetryFactory, PiTemperature


def test_creation():
    obj1 = TelemetryFactory()
    shutdown = threading.Event()
    obj2 = obj1.create("PiTemperature", "broker", "sensor", shutdown)
    assert isinstance(obj2, PiTemperature)
