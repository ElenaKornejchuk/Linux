
def pytest_addoption(parser):
    parser.addoption("--host", default="127.0.0.1")
    parser.addoption("--port", default="5000")


import threading
import time
import socket
import pytest
import echo_server


@pytest.fixture(scope='module')
def server():
    thread = threading.Thread(target=echo_server.run_server, daemon=True)
    thread.start()

    timeout = 5
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((echo_server.HOST, echo_server.PORT), timeout=1):
                break
        except (ConnectionRefusedError, OSError):
            if time.time() - start_time > timeout:
                pytest.fail("Сервер не запустился за 5 секунд")
            time.sleep(0.1)

    yield

@pytest.fixture
def host():
    return echo_server.HOST


@pytest.fixture
def port():
    return echo_server.PORT
