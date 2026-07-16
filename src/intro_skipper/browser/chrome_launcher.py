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

    def ensure_browser_is_running(self) -> None:
        if self._browser_connection.is_reachable():
            return
        self._process_starter(self._build_chrome_command())
        self._wait_until_reachable()

    @staticmethod
    def _build_chrome_command() -> list[str]:
        return [
            str(ChromeConstants.EXECUTABLE_PATH),
            f"--remote-debugging-port={ChromeConstants.DEBUGGING_PORT}",
            f"--user-data-dir={ChromeConstants.USER_PROFILE_DIRECTORY}",
            "--no-first-run",
            "--no-default-browser-check",
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
