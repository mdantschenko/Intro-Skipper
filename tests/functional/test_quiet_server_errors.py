from http.server import BaseHTTPRequestHandler
from typing import Iterator

import pytest

from intro_skipper.remote_control import QuietHTTPServer


@pytest.fixture
def quiet_server() -> Iterator[QuietHTTPServer]:
    server = QuietHTTPServer(("", 0), BaseHTTPRequestHandler)
    yield server
    server.server_close()


def report_error_for(
    server: QuietHTTPServer, exception: Exception, capsys: pytest.CaptureFixture[str]
) -> str:
    try:
        raise exception
    except Exception:
        server.handle_error(None, ("phone", 50848))
    return capsys.readouterr().err


def test_a_dropped_phone_connection_stays_silent(
    quiet_server: QuietHTTPServer, capsys: pytest.CaptureFixture[str]
) -> None:
    assert report_error_for(quiet_server, ConnectionResetError(), capsys) == ""


def test_real_errors_are_still_reported(
    quiet_server: QuietHTTPServer, capsys: pytest.CaptureFixture[str]
) -> None:
    assert "ValueError" in report_error_for(quiet_server, ValueError("real"), capsys)
