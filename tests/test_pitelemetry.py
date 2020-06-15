import pytest
from ../src import pitelemetry, mqtt

class MockMQTTClient():

    # mock __init__
    @staticmethod
    def __init__(user, password, client, False):
        self.user=user

    def connect():
        return True

def test_connect(monkeypatch):

    def mock_init(*args, **kwargs):
        return MockMQTTClient()

    def mock_connect(*args, **kwargs):
        return True

    # apply the monkeypatches
    monkeypatch.setattr(MQTTClient, "__init__", mock_init)
    monkeypatch.setattr(MQTTClient, "connect", mock_connect)

    
