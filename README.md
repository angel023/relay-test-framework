# Test framework for a simulated smart relay

A small, clean and extensible test framework built with **Python** and **pytest**. It tests the REST API of a smart relay. There is no physical device, so the tests run against a **simulator** (Flask) that imitates the device, including "capricious" behaviors (503 errors, reboot).

## What is inside

- Device simulator (Flask) with `/status`, `/relay/<id>/set`, `/config`, `/reboot`
- API client that wraps all HTTP requests (tests contain no `requests.get(...)` calls)
- Tests with fixtures, parametrization and markers (`smoke`, `regression`, `negative`)
- Waiting with a timeout after reboot (no fixed `sleep`)
- Logging of every request and response, plus a log file for every failed test
- HTML report (`pytest-html`)
- Configuration through environment variables
- CI with GitHub Actions (smoke on every push, full suite nightly or manually)

## Project structure

```
relay-test-framework/
├── .github/workflows/tests.yml   # CI pipeline
├── api_client/
│   └── client.py                 # RelayClient: the only place where requests leave the code
├── simulator/
│   └── app.py                    # Flask device simulator
├── tests/
│   ├── test_smoke.py
│   ├── test_relay_negative.py
│   ├── test_config_and_reboot.py
│   └── test_rate_limit.py
├── conftest.py                   # fixtures and the hook that saves log files
├── config.py                     # configuration (address, timeouts)
├── pytest.ini                    # markers, logging, HTML report
├── requirements.txt
└── README.md
```

## How to run

### 1. Setup (once)

```bash
python -m venv .venv
# Windows:      .venv\Scripts\activate
# Linux / Mac:  source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the simulator (first terminal)

```bash
python simulator/app.py
```

The simulator listens on `http://127.0.0.1:5000`. Leave it running.

### 3. Run the tests (second terminal, with the environment activated)

```bash
pytest                    # all tests
pytest -m smoke           # only the quick checks
pytest -m negative        # only the negative scenarios
pytest -m regression      # only the regression tests
pytest -v                 # more detailed output
```

The report is written automatically to `reports/report.html`. For every failed test a separate log file is saved in `reports/logs/`.

## Configuration

Values are read from environment variables. If a variable is not set, the default is used.

| Variable | Default | Meaning |
|---|---|---|
| `RELAY_BASE_URL` | `http://127.0.0.1:5000` | address of the device |
| `RELAY_REQUEST_TIMEOUT` | `5` | timeout of a single request (seconds) |
| `RELAY_READY_TIMEOUT` | `10` | how long to wait for the device after a reboot (seconds) |

Example (PowerShell) if the port is already in use:

```powershell
$env:RELAY_BASE_URL = "http://127.0.0.1:5001"
pytest
```

## Markers

| Marker | What it covers |
|---|---|
| `smoke` | quick checks that the device is alive and the main functions work |
| `regression` | the full set that protects existing behavior |
| `negative` | invalid inputs and expected errors (400, 404, 503) |

Markers are registered in `pytest.ini` with `--strict-markers`, so a typo in a marker name raises an error instead of being silently ignored.

## Design decisions

**Separation of responsibilities.** A test says *what* is checked ("turn on relay 0, expect `on`"), and `RelayClient` decides *how* (URL, method, body, timeout). If the API changes, only the client changes.

**All requests go through one method (`_request`).** This way logging (method, URL, body, status, response time) is in one place. Adding a new endpoint is one short method.

**Independent tests.** The `client` fixture waits until the device is ready and calls `/_reset` before every test. Every test starts from the initial state and does not depend on execution order. `/_reset` is a helper endpoint that exists only in the simulator.

**No `sleep` for reboot.** `wait_until_ready` polls `/status` at short intervals and continues as soon as the device answers with 200. If that does not happen within the given time, it raises `TimeoutError`. The test does not waste time when the device is fast, and does not fail falsely when it is slower.

**Diagnostics without rerunning.** When a test fails, the log of requests and responses is visible in `Captured log call`, in the HTML report, and in a separate file in `reports/logs/`.

**Configuration through environment variables.** They are easy to set in CI without changing files in the project. The values live in one place (`config.py`).

**Small but clean.** I preferred a clear structure over a large amount of functionality.

## CI (GitHub Actions)

The file `.github/workflows/tests.yml`:

- on every **push** it starts the simulator and runs the `smoke` tests
- **nightly** (02:00 UTC) and **manually** (Run workflow) it runs the full suite
- it uploads `reports/` and the simulator log as an **artifact** (even when tests fail)

## Limitations and possible improvements

- The simulator keeps its state in memory and it is shared by all tests, so the tests are **not suitable for parallel execution** (`pytest-xdist`) without a separate simulator instance per process.
- The request rate limit (20 per second) is checked with a fast burst of requests. On a very slow machine the number of requests may need to be increased.
- Ideas for extension: retry only for expected 503 responses (without hiding real bugs), contract tests of the response format with JSON Schema.