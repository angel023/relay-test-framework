import os

BASE_URL = os.getenv("RELAY_BASE_URL", "http://127.0.0.1:5000")
REQUEST_TIMEOUT = float(os.getenv("RELAY_REQUEST_TIMEOUT", "5"))
READY_TIMEOUT = float(os.getenv("RELAY_READY_TIMEOUT", "10"))