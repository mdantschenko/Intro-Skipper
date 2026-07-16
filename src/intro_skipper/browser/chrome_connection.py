import json
from typing import Any

import requests
from websocket import (
    WebSocket,
    WebSocketException,
    create_connection,  # pyright: ignore[reportUnknownVariableType]
)

from intro_skipper.browser.browser_connection import (
    BrowserCommunicationError,
    BrowserConnection,
    BrowserTab,
)
from intro_skipper.helpers.constants import ChromeConstants, JavaScriptSnippets

__all__ = ["ChromeConnection", "ChromeTab"]


class ChromeTab(BrowserTab):
    def __init__(self, url: str, websocket_debugger_url: str) -> None:
        self._url = url
        self._websocket_debugger_url = websocket_debugger_url

    @property
    def url(self) -> str:
        return self._url

    def click_first_visible_element(self, css_selector: str) -> bool:
        javascript = JavaScriptSnippets.CLICK_FIRST_VISIBLE_ELEMENT_TEMPLATE.replace(
            "__CSS_SELECTOR__", json.dumps(css_selector)
        )
        return self.evaluate_javascript(javascript) is True

    def evaluate_javascript(self, javascript: str) -> object:
        try:
            evaluation_result = self._evaluate_javascript(javascript)
        except (WebSocketException, OSError) as error:
            raise BrowserCommunicationError(str(error)) from error
        return evaluation_result.get("result", {}).get("value")

    def _evaluate_javascript(self, javascript: str) -> dict[str, Any]:
        # Chrome rejects websocket clients that send an Origin header (403),
        # so the header is suppressed entirely.
        connection = create_connection(
            self._websocket_debugger_url,
            timeout=ChromeConstants.WEBSOCKET_TIMEOUT_SECONDS,
            suppress_origin=True,
        )
        try:
            connection.send(json.dumps(self._build_evaluation_request(javascript)))
            return self._receive_evaluation_result(connection)
        finally:
            connection.close()

    @staticmethod
    def _build_evaluation_request(javascript: str) -> dict[str, object]:
        return {
            "id": ChromeConstants.JAVASCRIPT_EVALUATION_REQUEST_ID,
            "method": "Runtime.evaluate",
            "params": {"expression": javascript, "returnByValue": True},
        }

    @staticmethod
    def _receive_evaluation_result(connection: WebSocket) -> dict[str, Any]:
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
