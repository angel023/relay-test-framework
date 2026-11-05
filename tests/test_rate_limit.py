import pytest


@pytest.mark.negative
def test_too_many_requests_returns_503(client):
    responses = client.get_status_burst(21)
    status_codes = [r.status_code for r in responses]

    assert 503 in status_codes
    limited = next(r for r in responses if r.status_code == 503)
    assert limited.json()["error"] == "too many requests"