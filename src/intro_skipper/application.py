import logging
import time

from intro_skipper.browser.browser_connection import (
    BrowserCommunicationError,
    BrowserConnection,
    BrowserTab,
)
from intro_skipper.helpers.constants import ApplicationConstants
from intro_skipper.services.streaming_service import StreamingService
from intro_skipper.skipping_settings import SkippingSettings


class IntroSkipperApplication:
    def __init__(
        self,
        browser_connection: BrowserConnection,
        streaming_services: tuple[StreamingService, ...],
        skipping_settings: SkippingSettings | None = None,
    ) -> None:
        self._browser_connection = browser_connection
        self._streaming_services = streaming_services
        self._skipping_settings = skipping_settings or SkippingSettings()
        self._logger = logging.getLogger(ApplicationConstants.LOGGER_NAME)
        self._browser_had_open_tabs = False

    def run_forever(self) -> None:
        while self._execute_polling_pass():
            time.sleep(ApplicationConstants.POLLING_INTERVAL_SECONDS)

    def run_single_pass(self) -> int:
        open_tabs = self._browser_connection.list_open_tabs()
        for browser_tab in open_tabs:
            self._skip_inside_tab(browser_tab)
        return len(open_tabs)

    def _execute_polling_pass(self) -> bool:
        try:
            open_tab_count = self.run_single_pass()
        except BrowserCommunicationError:
            return self._handle_communication_error()
        if open_tab_count > 0:
            self._browser_had_open_tabs = True
            return True
        if self._browser_had_open_tabs:
            self._logger.info(
                "The last Chrome window was closed, stopping Intro Skipper."
            )
            return False
        return True

    def _handle_communication_error(self) -> bool:
        if self._browser_connection.is_reachable():
            return True
        self._logger.info("Chrome was closed, stopping Intro Skipper.")
        return False

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
            if not self._skipping_settings.is_enabled_for_any(skip_target.kinds):
                continue
            if browser_tab.click_first_visible_element(skip_target.css_selector):
                self._logger.info(
                    "%s: %s", streaming_service.name, skip_target.description
                )
