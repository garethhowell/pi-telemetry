from .. import MQTTClient
import pytest

# test_mqtt.py
#
mqtt_host = "dummy.com"
mqtt_key = "pass"
mqtt_user = "dummy"
mqtt_secure = True
def test_init():
    dummy = MQTTClient(mqtt_user, mqtt_key, mqtt_host, mqtt_secure)
    assert isinstance(dummy, MQTTClient)

def test_init_with_defaults():
    dummy = MQTTClient(mqtt_user, mqtt_key, mqtt_host)
    assert isinstance(dummy, MQTTClient)

@pytest.mark.parametrize("user, key, host, secure",
        [
            ("", mqtt_key, mqtt_host, mqtt_secure),
            (mqtt_user, "", mqtt_host, mqtt_secure),
            ("", "", "", "")
        ])

def test_catch_missing_parameters_in_init(user, key, host, secure):
    with pytest.raises(TypeError):
        dummy = MQTTClient(user, key, host, secure)
