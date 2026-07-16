import base64
import json
import threading
from typing import Any, cast

import requests
from websocket import (
    WebSocket,
    WebSocketException,
    WebSocketTimeoutException,
    create_connection,  # pyright: ignore[reportUnknownVariableType]
)

from intro_skipper.browser.browser_connection import (
    BrowserCommunicationError,
    BrowserConnection,
    BrowserTab,
    ScreencastHandle,
)
from intro_skipper.helpers.constants import ChromeConstants, JavaScriptSnippets

__all__ = ["ChromeConnection", "ChromeTab"]


class ChromeScreencastHandle(ScreencastHandle):
    def __init__(self, websocket_debugger_url: str) -> None:
        self._websocket_debugger_url = websocket_debugger_url
        self._latest_frame: bytes | None = None
        self._frame_lock = threading.Lock()
        self._stop_requested = threading.Event()
        streaming_thread = threading.Thread(target=self._stream_frames, daemon=True)
        streaming_thread.start()

    def latest_frame(self) -> bytes | None:
        with self._frame_lock:
            return self._latest_frame

    def stop(self) -> None:
        self._stop_requested.set()

    def _stream_frames(self) -> None:
        try:
            connection = create_connection(
                self._websocket_debugger_url,
                timeout=ChromeConstants.WEBSOCKET_TIMEOUT_SECONDS,
                suppress_origin=True,
            )
        except (WebSocketException, OSError):
            return
        try:
            connection.send(
                json.dumps(
                    {
                        "id": ChromeConstants.JAVASCRIPT_EVALUATION_REQUEST_ID,
                        "method": "Page.startScreencast",
                        "params": {
                            "format": "jpeg",
                            "quality": ChromeConstants.SCREENSHOT_JPEG_QUALITY,
                            "maxWidth": ChromeConstants.SCREENCAST_MAX_WIDTH,
                            "maxHeight": ChromeConstants.SCREENCAST_MAX_HEIGHT,
                        },
                    }
                )
            )
            self._receive_frames(connection)
        except (WebSocketException, OSError, ValueError):
            return
        finally:
            connection.close()

    def _receive_frames(self, connection: WebSocket) -> None:
        while not self._stop_requested.is_set():
            try:
                message: dict[str, Any] = json.loads(connection.recv())
            except WebSocketTimeoutException:
                # A quiet page sends no frames; keep waiting until stopped.
                continue
            if message.get("method") == "Page.screencastFrame":
                self._store_frame_and_acknowledge(connection, message["params"])

    def _store_frame_and_acknowledge(
        self, connection: WebSocket, frame_parameters: dict[str, Any]
    ) -> None:
        with self._frame_lock:
            self._latest_frame = base64.b64decode(str(frame_parameters["data"]))
        connection.send(
            json.dumps(
                {
                    "id": ChromeConstants.JAVASCRIPT_EVALUATION_REQUEST_ID,
                    "method": "Page.screencastFrameAck",
                    "params": {"sessionId": frame_parameters["sessionId"]},
                }
            )
        )


class ChromeTab(BrowserTab):
    def __init__(self, url: str, websocket_debugger_url: str) -> None:
        self._url = url
        self._websocket_debugger_url = websocket_debugger_url
        self._cached_viewport_size: dict[str, Any] | None = None

    @property
    def url(self) -> str:
        return self._url

    @property
    def identifier(self) -> str:
        return self._websocket_debugger_url

    def open_screencast(self) -> ScreencastHandle:
        return ChromeScreencastHandle(self._websocket_debugger_url)

    def click_first_visible_element(self, css_selector: str) -> bool:
        javascript = JavaScriptSnippets.CLICK_FIRST_VISIBLE_ELEMENT_TEMPLATE.replace(
            "__CSS_SELECTOR__", json.dumps(css_selector)
        )
        return self.evaluate_javascript(javascript) is True

    def evaluate_javascript(self, javascript: str) -> object:
        result = self._send_devtools_command(
            "Runtime.evaluate", {"expression": javascript, "returnByValue": True}
        )
        return result.get("result", {}).get("value")

    def capture_screenshot(self) -> bytes:
        result = self._send_devtools_command(
            "Page.captureScreenshot",
            {"format": "jpeg", "quality": ChromeConstants.SCREENSHOT_JPEG_QUALITY},
        )
        return base64.b64decode(str(result.get("data", "")))

    def tap_at_fraction(self, x_fraction: float, y_fraction: float) -> None:
        viewport = self._read_viewport_size()
        if viewport is None:
            return
        x = float(viewport["width"]) * x_fraction
        y = float(viewport["height"]) * y_fraction
        for event_type in ("mousePressed", "mouseReleased"):
            self._send_devtools_command(
                "Input.dispatchMouseEvent",
                {
                    "type": event_type,
                    "x": x,
                    "y": y,
                    "button": "left",
                    "clickCount": 1,
                },
            )

    def scroll_by(self, delta_y: float) -> None:
        viewport = self._read_viewport_size()
        if viewport is None:
            return
        self._send_devtools_command(
            "Input.dispatchMouseEvent",
            {
                "type": "mouseWheel",
                "x": float(viewport["width"]) / 2,
                "y": float(viewport["height"]) / 2,
                "deltaX": 0,
                "deltaY": delta_y,
            },
        )

    def _read_viewport_size(self) -> dict[str, Any] | None:
        if self._cached_viewport_size is not None:
            return self._cached_viewport_size
        viewport = self.evaluate_javascript(JavaScriptSnippets.READ_VIEWPORT_SIZE)
        if not isinstance(viewport, dict):
            return None
        self._cached_viewport_size = cast(dict[str, Any], viewport)
        return self._cached_viewport_size

    def _send_devtools_command(
        self, method: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        try:
            return self._exchange_devtools_message(method, params)
        except (WebSocketException, OSError) as error:
            raise BrowserCommunicationError(str(error)) from error

    def _exchange_devtools_message(
        self, method: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        # Chrome rejects websocket clients that send an Origin header (403),
        # so the header is suppressed entirely.
        connection = create_connection(
            self._websocket_debugger_url,
            timeout=ChromeConstants.WEBSOCKET_TIMEOUT_SECONDS,
            suppress_origin=True,
        )
        try:
            connection.send(
                json.dumps(
                    {
                        "id": ChromeConstants.JAVASCRIPT_EVALUATION_REQUEST_ID,
                        "method": method,
                        "params": params,
                    }
                )
            )
            return self._receive_devtools_result(connection)
        finally:
            connection.close()

    @staticmethod
    def _receive_devtools_result(connection: WebSocket) -> dict[str, Any]:
        while True:
            message: dict[str, Any] = json.loads(connection.recv())
            if message.get("id") == ChromeConstants.JAVASCRIPT_EVALUATION_REQUEST_ID:
                return message.get("result", {})


class ChromeConnection(BrowserConnection):
    def __init__(self, debugging_port: int = ChromeConstants.DEBUGGING_PORT) -> None:
        devtools_base_url = f"http://127.0.0.1:{debugging_port}"
        self._tab_list_url = f"{devtools_base_url}/json"
        self._new_tab_url = f"{devtools_base_url}/json/new"

    def is_reachable(self) -> bool:
        try:
            requests.get(
                self._tab_list_url,
                timeout=ChromeConstants.HTTP_REQUEST_TIMEOUT_SECONDS,
            )
        except requests.RequestException:
            return False
        return True

    def list_open_tabs(self) -> list[BrowserTab]:
        try:
            response = requests.get(
                self._tab_list_url,
                timeout=ChromeConstants.HTTP_REQUEST_TIMEOUT_SECONDS,
            )
        except requests.RequestException as error:
            raise BrowserCommunicationError(str(error)) from error
        return [
            ChromeTab(tab_description["url"], tab_description["webSocketDebuggerUrl"])
            for tab_description in response.json()
            if tab_description.get("type") == "page"
        ]

    def open_new_tab(self, url: str = "") -> None:
        new_tab_url = f"{self._new_tab_url}?{url}" if url else self._new_tab_url
        try:
            requests.put(
                new_tab_url,
                timeout=ChromeConstants.HTTP_REQUEST_TIMEOUT_SECONDS,
            )
        except requests.RequestException as error:
            raise BrowserCommunicationError(str(error)) from error
