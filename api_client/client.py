import logging
import time

import requests

logger = logging.getLogger("relay_client")


class RelayClient:
    def __init__(self, base_url, timeout=5):
        self.base_url = base_url
        self.timeout = timeout

    def _request(self, method, path, **kwargs):
        """The only place where an HTTP request leaves the client. Logs everything."""
        url = f"{self.base_url}{path}"
        body = kwargs.get("json")
        logger.info("-> %s %s body=%s", method, url, body)

        start = time.perf_counter()
        try:
            response = requests.request(method, url, timeout=self.timeout, **kwargs)
        except requests.RequestException as error:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.error("!! %s %s failed after %.0f ms: %s", method, url, elapsed_ms, error)
            raise

        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "<- %s %s status=%s time=%.0f ms body=%s",
            method, url, response.status_code, elapsed_ms, response.text.strip(),
        )
        return response

    def get_status(self):
        return self._request("GET", "/status")

    def set_relay(self, relay_id, state):
        return self._request("POST", f"/relay/{relay_id}/set", json={"state": state})

    def get_config(self):
        return self._request("GET", "/config")

    def update_config(self, settings):
        return self._request("POST", "/config", json=settings)

    def reboot(self):
        return self._request("POST", "/reboot")

    def reset(self):
        return self._request("POST", "/_reset")

    def wait_until_ready(self, timeout=10, interval=0.5):
        """Polls /status at short intervals until the device answers with 200.
        Raises TimeoutError if that does not happen within `timeout` seconds."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                if self.get_status().status_code == 200:
                    return
            except requests.RequestException:
                pass  # the device is not reachable yet, try again
            time.sleep(interval)
        raise TimeoutError(f"Device was not ready within {timeout} seconds")