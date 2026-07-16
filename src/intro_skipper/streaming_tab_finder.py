from intro_skipper.browser.browser_connection import (
    BrowserCommunicationError,
    BrowserConnection,
    BrowserTab,
)
from intro_skipper.helpers.constants import VideoControlJavaScript
from intro_skipper.services.streaming_service import StreamingService


class StreamingTabFinder:
    def __init__(
        self,
        browser_connection: BrowserConnection,
        streaming_services: tuple[StreamingService, ...],
    ) -> None:
        self._browser_connection = browser_connection
        self._streaming_services = streaming_services

    def find_video_tab(self) -> BrowserTab | None:
        for browser_tab in self._list_tabs_or_none():
            if self._shows_a_streaming_video(browser_tab):
                return browser_tab
        return None

    def find_service_tab(self) -> BrowserTab | None:
        for browser_tab in self._list_tabs_or_none():
            if self._matches_any_service(browser_tab.url):
                return browser_tab
        return None

    def find_streaming_service_for(
        self, browser_tab: BrowserTab | None
    ) -> StreamingService | None:
        if browser_tab is None:
            return None
        for streaming_service in self._streaming_services:
            if streaming_service.matches_url(browser_tab.url):
                return streaming_service
        return None

    def _list_tabs_or_none(self) -> list[BrowserTab]:
        try:
            return self._browser_connection.list_open_tabs()
        except BrowserCommunicationError:
            return []

    def _matches_any_service(self, url: str) -> bool:
        return any(
            streaming_service.matches_url(url)
            for streaming_service in self._streaming_services
        )

    def _shows_a_streaming_video(self, browser_tab: BrowserTab) -> bool:
        if not self._matches_any_service(browser_tab.url):
            return False
        try:
            state = browser_tab.evaluate_javascript(VideoControlJavaScript.READ_STATE)
        except BrowserCommunicationError:
            return False
        return isinstance(state, dict)
