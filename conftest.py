import pytest
import config


from api_client.client import RelayClient


@pytest.fixture
def client():
    api = RelayClient(config.BASE_URL, timeout=config.REQUEST_TIMEOUT)
    api.wait_until_ready(timeout=config.READY_TIMEOUT)
    api.reset()
    return api


import logging
from pathlib import Path

LOG_DIR = Path("reports") / "logs"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Runs after each test phase. Saves the log to a file if the test failed."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        safe_name = item.nodeid.replace("/", "_").replace("::", "__")
        safe_name = "".join(c if c.isalnum() or c in "_-." else "_" for c in safe_name)

        log_text = "\n".join(
            text for name, text in report.sections if name.startswith("Captured log")
        )
        (LOG_DIR / f"{safe_name}.log").write_text(
            f"TEST: {item.nodeid}\n\n{log_text}\n", encoding="utf-8"
        )