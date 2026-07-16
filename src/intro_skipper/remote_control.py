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
    ScreencastHandle,
)
from intro_skipper.helpers.constants import (
    JavaScriptSnippets,
    PlayerControlSelectors,
    RemoteControlConstants,
    VideoControlJavaScript,
)
from intro_skipper.helpers.enums import SkipKind
from intro_skipper.services.streaming_service import StreamingService
from intro_skipper.skipping_settings import SkippingSettings
from intro_skipper.streaming_tab_finder import StreamingTabFinder


class RemoteControlServer:
    def __init__(
        self,
        browser_connection: BrowserConnection,
        streaming_services: tuple[StreamingService, ...],
        skipping_settings: SkippingSettings,
        port: int = RemoteControlConstants.PORT,
    ) -> None:
        self._tab_finder = StreamingTabFinder(browser_connection, streaming_services)
        self._skipping_settings = skipping_settings
        self._http_server = ThreadingHTTPServer(
            ("", port), _RemoteControlRequestHandler
        )
        self._http_server.remote_control = self  # type: ignore[attr-defined]
        self._screencast: ScreencastHandle | None = None
        self._live_tab: BrowserTab | None = None
        self._screencast_lock = threading.Lock()

    @property
    def port(self) -> int:
        return self._http_server.server_address[1]

    def start_in_background(self) -> None:
        server_thread = threading.Thread(
            target=self._http_server.serve_forever, daemon=True
        )
        server_thread.start()

    def shut_down(self) -> None:
        self._stop_screencast()
        self._http_server.shutdown()

    def build_page_addresses(self) -> list[str]:
        return [
            f"http://{address}:{self.port}"
            for address in find_local_network_addresses()
        ]

    def describe_state(self) -> dict[str, Any]:
        video_state = self._read_video_state()
        return {
            "skipping": self._skipping_settings.describe(),
            "video": video_state,
        }

    def execute_command(self, command: dict[str, Any]) -> None:
        action = str(command.get("action"))
        control_handler = self._control_handlers().get(action)
        if control_handler is not None:
            control_handler(command)
            return
        self._run_video_javascript(_build_video_javascript(action, command))

    def _control_handlers(self) -> dict[str, Callable[[dict[str, Any]], None]]:
        return {
            "toggle_skipping": self._toggle_skipping,
            "navigate_home": self._navigate_home,
            "tap": self._tap_on_service_tab,
            "scroll": self._scroll_service_tab,
            "stop_live_view": self._stop_live_view,
        }

    def _toggle_skipping(self, command: dict[str, Any]) -> None:
        self._skipping_settings.toggle(SkipKind(str(command.get("kind", ""))))

    def _navigate_home(self, _command: dict[str, Any]) -> None:  # skylos: ignore
        service_tab = self._tab_finder.find_service_tab()
        streaming_service = self._tab_finder.find_streaming_service_for(service_tab)
        if service_tab is None or streaming_service is None:
            return
        service_tab.evaluate_javascript(
            JavaScriptSnippets.NAVIGATE_TEMPLATE.replace(
                "__TARGET_URL__", json.dumps(streaming_service.homepage_url)
            )
        )

    def _tap_on_service_tab(self, command: dict[str, Any]) -> None:
        service_tab = self._live_tab_or_search()
        if service_tab is not None:
            service_tab.tap_at_fraction(
                float(command.get("x_fraction", 0.5)),
                float(command.get("y_fraction", 0.5)),
            )

    def _scroll_service_tab(self, command: dict[str, Any]) -> None:
        service_tab = self._live_tab_or_search()
        if service_tab is not None:
            service_tab.scroll_by(float(command.get("delta_y", 0)))

    def _stop_live_view(self, _command: dict[str, Any]) -> None:  # skylos: ignore
        self._stop_screencast()

    def read_live_frame(self) -> bytes | None:
        service_tab = self._live_tab_or_search()
        if service_tab is None:
            return None
        screencast = self._ensure_screencast(service_tab)
        return screencast.latest_frame() or service_tab.capture_screenshot()

    def _live_tab_or_search(self) -> BrowserTab | None:
        # The tab is cached while the live view runs, so frame, tap and
        # scroll requests skip the tab-list roundtrip to Chrome.
        with self._screencast_lock:
            if self._live_tab is not None:
                return self._live_tab
        return self._tab_finder.find_service_tab()

    def _ensure_screencast(self, service_tab: BrowserTab) -> ScreencastHandle:
        with self._screencast_lock:
            if self._screencast is None:
                self._screencast = service_tab.open_screencast()
                self._live_tab = service_tab
            return self._screencast

    def _stop_screencast(self) -> None:
        with self._screencast_lock:
            if self._screencast is not None:
                self._screencast.stop()
                self._screencast = None
            self._live_tab = None

    def _read_video_state(self) -> dict[str, Any] | None:
        video_tab = self._tab_finder.find_video_tab()
        if video_tab is None:
            return None
        state = video_tab.evaluate_javascript(VideoControlJavaScript.READ_STATE)
        if not isinstance(state, dict):
            return None
        return cast(dict[str, Any], state)

    def _run_video_javascript(self, javascript: str) -> None:
        video_tab = self._tab_finder.find_video_tab()
        if video_tab is not None:
            video_tab.evaluate_javascript(javascript)


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
    "restart_episode": lambda command: _build_seek_javascript(0.0),
    "next_episode": lambda command: JavaScriptSnippets.CLICK_FIRST_MATCH_TEMPLATE.replace(
        "__CSS_SELECTORS__",
        json.dumps(list(PlayerControlSelectors.NEXT_EPISODE_BUTTONS)),
    ),
}


def _build_video_javascript(action: object, command: dict[str, Any]) -> str:
    javascript_builder = _VIDEO_JAVASCRIPT_BUILDERS.get(str(action))
    if javascript_builder is None:
        raise ValueError(f"unknown remote control action '{action}'")
    return javascript_builder(command)


def find_local_network_addresses() -> list[str]:
    """Collects the machine's IPv4 addresses, home network (192.168.x) first,
    because a VPN tunnel address would be unreachable for the phone."""
    try:
        address_infos = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)
    except OSError:
        return ["localhost"]
    addresses = {str(address_info[4][0]) for address_info in address_infos}
    return _prefer_home_network_addresses(addresses) or ["localhost"]


def _prefer_home_network_addresses(addresses: set[str]) -> list[str]:
    usable_addresses = [
        address for address in addresses if not address.startswith(("127.", "169.254."))
    ]
    usable_addresses.sort(
        key=lambda address: (not address.startswith("192.168."), address)
    )
    return usable_addresses


class _RemoteControlRequestHandler(BaseHTTPRequestHandler):
    # Keep-alive spares the phone a new TCP connection per frame request.
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:
        if self.path == "/state":
            self._send_json(self._remote_control().describe_state())
            return
        if self.path.startswith("/screenshot"):
            self._send_live_frame()
            return
        self._send_page()

    def _send_live_frame(self) -> None:
        live_frame = self._remote_control().read_live_frame()
        if live_frame is None:
            self._send_json({"error": "no streaming tab open"}, status=404)
            return
        self._send_payload(live_frame, content_type="image/jpeg")

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
