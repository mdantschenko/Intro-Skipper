import subprocess
import time
from typing import Callable, Sequence

from intro_skipper.browser.browser_connection import BrowserConnection
from intro_skipper.helpers.constants import ChromeConstants

ProcessStarter = Callable[[Sequence[str]], object]


class ChromeLauncher:
    def __init__(
        self,
        browser_connection: BrowserConnection,
        process_starter: ProcessStarter = subprocess.Popen,
    ) -> None:
        self._browser_connection = browser_connection
        self._process_starter = process_starter

    def ensure_browser_is_running(self, start_page_urls: Sequence[str] = ()) -> None:
        if self._browser_connection.is_reachable():
            self._open_start_pages_in_running_browser(start_page_urls)
            return
        self._process_starter(self._build_chrome_command(start_page_urls))
        self._wait_until_reachable()

    def _open_start_pages_in_running_browser(
        self, start_page_urls: Sequence[str]
    ) -> None:
        for start_page_url in start_page_urls:
            self._browser_connection.open_new_tab(start_page_url)
        if not start_page_urls and not self._browser_connection.list_open_tabs():
            # A leftover background Chrome answers on the port but has no
            # tabs; without a fresh tab no window would ever become visible.
            self._browser_connection.open_new_tab(ChromeConstants.NEW_TAB_PAGE_URL)

    @staticmethod
    def _build_chrome_command(start_page_urls: Sequence[str]) -> list[str]:
        return [
            str(ChromeConstants.EXECUTABLE_PATH),
            f"--remote-debugging-port={ChromeConstants.DEBUGGING_PORT}",
            f"--user-data-dir={ChromeConstants.USER_PROFILE_DIRECTORY}",
            "--no-first-run",
            "--no-default-browser-check",
            # Without this flag Chrome keeps running in the background after
            # the last window closes, blocks the debugging port and the next
            # launch silently opens no window.
            "--disable-background-mode",
            *start_page_urls,
        ]

    def _wait_until_reachable(self) -> None:
        waiting_deadline = time.monotonic() + ChromeConstants.STARTUP_TIMEOUT_SECONDS
        while time.monotonic() < waiting_deadline:
            if self._browser_connection.is_reachable():
                return
            time.sleep(ChromeConstants.STARTUP_POLL_INTERVAL_SECONDS)
        raise RuntimeError(
            "Chrome did not answer on the debugging port after starting."
        )
