import logging
import time

from intro_skipper.browser.browser_connection import (
    BrowserCommunicationError,
    BrowserConnection,
    BrowserTab,
)
from intro_skipper.helpers.constants import ApplicationConstants
from intro_skipper.services.streaming_service import StreamingService


class IntroSkipperApplication:
    def __init__(
        self,
        browser_connection: BrowserConnection,
        streaming_services: tuple[StreamingService, ...],
    ) -> None:
        self._browser_connection = browser_connection
        self._streaming_services = streaming_services
        self._logger = logging.getLogger(ApplicationConstants.LOGGER_NAME)

    def run_forever(self) -> None:
        while True:
            try:
                self.run_single_pass()
            except BrowserCommunicationError:
                if not self._browser_connection.is_reachable():
                    self._logger.info("Chrome was closed, stopping Intro Skipper.")
                    return
                self._logger.debug("Ignoring a transient communication error.")
            time.sleep(ApplicationConstants.POLLING_INTERVAL_SECONDS)

    def run_single_pass(self) -> None:
        for browser_tab in self._browser_connection.list_open_tabs():
            self._skip_inside_tab(browser_tab)

    def _skip_inside_tab(self, browser_tab: BrowserTab) -> None:
        streaming_service = self._find_streaming_service_for(browser_tab.url)
        if streaming_service is not None:
            self._click_skip_targets(browser_tab, streaming_service)

    def _find_streaming_service_for(self, url: str) -> StreamingService | None:
        for streaming_service in self._streaming_services:
            if streaming_service.matches_url(url):
                return streaming_service
        return None

    def _click_skip_targets(
        self, browser_tab: BrowserTab, streaming_service: StreamingService
    ) -> None:
        for skip_target in streaming_service.skip_targets:
            if browser_tab.click_first_visible_element(skip_target.css_selector):
                self._logger.info(
                    "%s: %s", streaming_service.name, skip_target.description
                )
