import time

from flask import Flask, jsonify, request

app = Flask(__name__)

REBOOT_SECONDS = 3
RATE_LIMIT = 20  # max requests per second before we answer 503


def initial_state():
    return {
        "relays": {0: "off", 1: "off"},
        "temperature": 25.0,
        "firmware": "1.0.0",
        "config": {"device_name": "relay-sim", "auto_off_seconds": 0},
        "reboot_until": 0,
        "recent_requests": [],
    }


# The state of the "device" lives in memory
device = initial_state()


@app.before_request
def simulate_flakiness():
    """Runs before EVERY request. Returning a response here stops the request."""
    if request.path == "/_reset":
        return None

    now = time.time()
    recent = [t for t in device["recent_requests"] if now - t < 1]
    recent.append(now)
    device["recent_requests"] = recent

    if len(recent) > RATE_LIMIT:
        return jsonify(error="too many requests"), 503
    if now < device["reboot_until"]:
        return jsonify(error="device is rebooting"), 503
    return None


@app.get("/status")
def status():
    return jsonify(
        relays=device["relays"],
        temperature=device["temperature"],
        firmware=device["firmware"],
    )


@app.post("/relay/<int:relay_id>/set")
def set_relay(relay_id):
    if relay_id not in device["relays"]:
        return jsonify(error="relay not found"), 404

    body = request.get_json(silent=True) or {}
    state = body.get("state")
    if state not in ("on", "off"):
        return jsonify(error="invalid state"), 400

    device["relays"][relay_id] = state
    return jsonify(id=relay_id, state=state)


@app.get("/config")
def get_config():
    return jsonify(device["config"])


@app.post("/config")
def update_config():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify(error="invalid body"), 400

    for key in body:
        if key not in device["config"]:
            return jsonify(error=f"unknown setting: {key}"), 400

    if "auto_off_seconds" in body:
        value = body["auto_off_seconds"]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            return jsonify(error="auto_off_seconds must be an integer >= 0"), 400

    device["config"].update(body)
    return jsonify(device["config"])


@app.post("/reboot")
def reboot():
    device["relays"] = {0: "off", 1: "off"}
    device["reboot_until"] = time.time() + REBOOT_SECONDS
    return jsonify(message="rebooting"), 202


@app.post("/_reset")
def reset():
    """Test helper: restore the initial state."""
    device.clear()
    device.update(initial_state())
    return jsonify(message="reset done")


if __name__ == "__main__":
    app.run(port=5000)