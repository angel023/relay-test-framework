import pytest
import config

@pytest.mark.regression
def test_get_config_returns_defaults(client):
    response = client.get_config()
    assert response.status_code == 200
    assert response.json()["device_name"] == "relay-sim"

@pytest.mark.regression
def test_update_device_name(client):
    response = client.update_config({"device_name": "kitchen"})
    assert response.status_code == 200
    assert client.get_config().json()["device_name"] == "kitchen"

@pytest.mark.negative
def test_unknown_setting_is_rejected(client):
    response = client.update_config({"banana": 1})
    assert response.status_code == 400

@pytest.mark.regression
def test_reboot_makes_device_unavailable_then_ready(client):
    response = client.reboot()
    assert response.status_code == 202

    # after restart the device should be unreachable
    assert client.get_status().status_code == 503

    # then it must be back in a working state within the configured time
    client.wait_until_ready(timeout=config.READY_TIMEOUT)
    assert client.get_status().status_code == 200

@pytest.mark.regression
def test_reboot_turns_relays_off(client):
    client.set_relay(0, "on")
    client.reboot()
    client.wait_until_ready(timeout=config.READY_TIMEOUT)
    assert client.get_status().json()["relays"]["0"] == "off"