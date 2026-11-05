import pytest


@pytest.mark.negative
@pytest.mark.parametrize(
    "relay_id, state, expected_status",
    [
        (0, "banana", 400),
        (1, "", 400),
        (0, "ON", 400),
        (1, "1", 400),
        (5, "on", 404),
        (-1, "on", 404),
        (99, "off", 404),
    ],
)
def test_invalid_relay_requests(client, relay_id, state, expected_status):
    response = client.set_relay(relay_id, state)
    assert response.status_code == expected_status


@pytest.mark.negative
def test_invalid_request_does_not_change_state(client):
    client.set_relay(0, "on")
    client.set_relay(0, "banana")  # invalid req
    assert client.get_status().json()["relays"]["0"] == "on"
