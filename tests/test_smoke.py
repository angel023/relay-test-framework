import pytest

@pytest.mark.smoke
def test_status_returns_200(client):
    response = client.get_status()
    assert response.status_code == 400

@pytest.mark.smoke
@pytest.mark.parametrize("relay_id",[0,1])
@pytest.mark.parametrize("state", ["on","off"])
def test_turn_relay(client, relay_id, state):
    response = client.set_relay(relay_id, state)
    assert response.status_code == 200
    assert response.json()["state"] == state

@pytest.mark.smoke
def test_unknown_relay_returns_404(client):
    response = client.set_relay(5, "on")
    assert response.status_code == 404


