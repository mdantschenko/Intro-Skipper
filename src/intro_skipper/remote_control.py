import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from typing import Any, Callable, cast

from intro_skipper.browser.browser_connection import (
    BrowserCommunicationError,
    BrowserConnection,
    BrowserTab,
)
from intro_skipper.helpers.constants import (
    RemoteControlConstants,
    VideoControlJavaScript,
)
from intro_skipper.services.streaming_service import StreamingService
from intro_skipper.skipping_switch import SkippingSwitch


class RemoteControlServer:
    def __init__(
        self,
        browser_connection: BrowserConnection,
        streaming_services: tuple[StreamingService, ...],
        skipping_switch: SkippingSwitch,
        port: int = RemoteControlConstants.PORT,
    ) -> None:
        self._browser_connection = browser_connection
        self._streaming_services = streaming_services
        self._skipping_switch = skipping_switch
        self._http_server = ThreadingHTTPServer(
            ("", port), _RemoteControlRequestHandler
        )
        self._http_server.remote_control = self  # type: ignore[attr-defined]

    @property
    def port(self) -> int:
        return self._http_server.server_address[1]

    def start_in_background(self) -> None:
        server_thread = threading.Thread(
            target=self._http_server.serve_forever, daemon=True
        )
        server_thread.start()

    def shut_down(self) -> None:
        self._http_server.shutdown()

    def build_page_address(self) -> str:
        return f"http://{find_local_network_address()}:{self.port}"

    def describe_state(self) -> dict[str, Any]:
        video_state = self._read_video_state()
        return {
            "skipping_enabled": self._skipping_switch.enabled,
            "video": video_state,
        }

    def execute_command(self, command: dict[str, Any]) -> None:
        action = command.get("action")
        if action == "toggle_skipping":
            self._skipping_switch.toggle()
            return
        self._run_video_javascript(_build_video_javascript(action, command))

    def _read_video_state(self) -> dict[str, Any] | None:
        video_tab = self._find_video_tab()
        if video_tab is None:
            return None
        state = video_tab.evaluate_javascript(VideoControlJavaScript.READ_STATE)
        if not isinstance(state, dict):
            return None
        return cast(dict[str, Any], state)

    def _run_video_javascript(self, javascript: str) -> None:
        video_tab = self._find_video_tab()
        if video_tab is not None:
            video_tab.evaluate_javascript(javascript)

    def _find_video_tab(self) -> BrowserTab | None:
        try:
            open_tabs = self._browser_connection.list_open_tabs()
        except BrowserCommunicationError:
            return None
        for browser_tab in open_tabs:
            if self._shows_a_streaming_video(browser_tab):
                return browser_tab
        return None

    def _shows_a_streaming_video(self, browser_tab: BrowserTab) -> bool:
        if not any(
            streaming_service.matches_url(browser_tab.url)
            for streaming_service in self._streaming_services
        ):
            return False
        try:
            state = browser_tab.evaluate_javascript(VideoControlJavaScript.READ_STATE)
        except BrowserCommunicationError:
            return False
        return isinstance(state, dict)


def _build_volume_javascript(volume_step: float) -> str:
    return VideoControlJavaScript.CHANGE_VOLUME_TEMPLATE.replace(
        "__VOLUME_STEP__", json.dumps(volume_step)
    )


def _build_jump_javascript(seconds: float) -> str:
    return VideoControlJavaScript.JUMP_TEMPLATE.replace(
        "__SECONDS__", json.dumps(seconds)
    )


def _build_seek_javascript(position_seconds: float) -> str:
    return VideoControlJavaScript.SEEK_TEMPLATE.replace(
        "__POSITION_SECONDS__", json.dumps(position_seconds)
    )


_VIDEO_JAVASCRIPT_BUILDERS: dict[str, Callable[[dict[str, Any]], str]] = {
    "toggle_playback": lambda command: VideoControlJavaScript.TOGGLE_PLAYBACK,
    "volume_down": lambda command: _build_volume_javascript(
        -RemoteControlConstants.VOLUME_STEP
    ),
    "volume_up": lambda command: _build_volume_javascript(
        RemoteControlConstants.VOLUME_STEP
    ),
    "jump": lambda command: _build_jump_javascript(float(command.get("seconds", 0))),
    "seek": lambda command: _build_seek_javascript(
        float(command.get("position_seconds", 0))
    ),
}


def _build_video_javascript(action: object, command: dict[str, Any]) -> str:
    javascript_builder = _VIDEO_JAVASCRIPT_BUILDERS.get(str(action))
    if javascript_builder is None:
        raise ValueError(f"unknown remote control action '{action}'")
    return javascript_builder(command)


def find_local_network_address() -> str:
    probe_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe_socket.connect(("8.8.8.8", 80))
        return str(probe_socket.getsockname()[0])
    except OSError:
        return "localhost"
    finally:
        probe_socket.close()


class _RemoteControlRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/state":
            self._send_json(self._remote_control().describe_state())
            return
        self._send_page()

    def do_POST(self) -> None:
        body_length = int(
            self.headers.get(RemoteControlConstants.CONTENT_LENGTH_HEADER, "0")
        )
        body = self.rfile.read(body_length)  # skylos: ignore bounded command body
        command: dict[str, Any] = json.loads(body or b"{}")
        try:
            self._remote_control().execute_command(command)
        except (ValueError, BrowserCommunicationError) as error:
            self._send_json({"error": str(error)}, status=400)
            return
        self._send_json({"ok": True})

    def _remote_control(self) -> RemoteControlServer:
        return self.server.remote_control  # type: ignore[attr-defined]

    def _send_page(self) -> None:
        page = (
            resources.files("intro_skipper")
            .joinpath(RemoteControlConstants.PAGE_FILE_NAME)
            .read_text(encoding=RemoteControlConstants.TEXT_ENCODING)
        )
        self._send_payload(
            page.encode(RemoteControlConstants.TEXT_ENCODING),
            content_type="text/html; charset=utf-8",
        )

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        self._send_payload(
            json.dumps(payload).encode(RemoteControlConstants.TEXT_ENCODING),
            content_type="application/json",
            status=status,
        )

    def _send_payload(
        self, payload_bytes: bytes, content_type: str, status: int = 200
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header(
            RemoteControlConstants.CONTENT_LENGTH_HEADER, str(len(payload_bytes))
        )
        self.end_headers()
        self.wfile.write(payload_bytes)

    def log_message(self, format: str, *arguments: object) -> None:  # skylos: ignore
        """Keeps request noise out of the console; the base class signature
        requires both parameters even though they stay unused."""
