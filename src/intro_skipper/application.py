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
        self._unreachable_browser_already_reported = False

    def run_forever(self) -> None:
        while True:
            self.run_single_pass()
            time.sleep(ApplicationConstants.POLLING_INTERVAL_SECONDS)

    def run_single_pass(self) -> None:
        try:
            for browser_tab in self._browser_connection.list_open_tabs():
                self._skip_inside_tab(browser_tab)
            self._unreachable_browser_already_reported = False
        except BrowserCommunicationError:
            self._report_unreachable_browser_once()

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

    def _report_unreachable_browser_once(self) -> None:
        if not self._unreachable_browser_already_reported:
            self._logger.warning("Chrome is currently unreachable, retrying.")
            self._unreachable_browser_already_reported = True
