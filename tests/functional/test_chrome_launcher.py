from typing import Sequence

from intro_skipper.browser.chrome_launcher import ChromeLauncher
from intro_skipper.helpers.constants import ChromeConstants
from tests.functional.browser_fakes import FakeBrowserConnection, FakeBrowserTab


class ChromeProcessRecorder:
    def __init__(self, browser_connection: FakeBrowserConnection) -> None:
        self._browser_connection = browser_connection
        self.started_commands: list[list[str]] = []

    def __call__(self, command: Sequence[str]) -> None:
        self.started_commands.append(list(command))
        self._browser_connection.reachable = True


def test_chrome_is_not_started_when_debugging_port_already_answers() -> None:
    browser_connection = FakeBrowserConnection(reachable=True)
    process_recorder = ChromeProcessRecorder(browser_connection)
    ChromeLauncher(browser_connection, process_recorder).ensure_browser_is_running()
    assert process_recorder.started_commands == []


def test_a_window_is_opened_when_chrome_runs_invisibly_without_tabs() -> None:
    browser_connection = FakeBrowserConnection(open_tabs=[], reachable=True)
    process_recorder = ChromeProcessRecorder(browser_connection)
    ChromeLauncher(browser_connection, process_recorder).ensure_browser_is_running()
    assert len(browser_connection.open_tabs) == 1


def test_no_extra_tab_is_opened_when_a_window_already_exists() -> None:
    browser_connection = FakeBrowserConnection(
        open_tabs=[FakeBrowserTab("https://www.netflix.com/browse")], reachable=True
    )
    process_recorder = ChromeProcessRecorder(browser_connection)
    ChromeLauncher(browser_connection, process_recorder).ensure_browser_is_running()
    assert len(browser_connection.open_tabs) == 1


def test_chrome_is_started_with_debugging_port_and_separate_profile() -> None:
    browser_connection = FakeBrowserConnection(reachable=False)
    process_recorder = ChromeProcessRecorder(browser_connection)
    ChromeLauncher(browser_connection, process_recorder).ensure_browser_is_running()
    (chrome_command,) = process_recorder.started_commands
    assert chrome_command[0] == str(ChromeConstants.EXECUTABLE_PATH)
    assert f"--remote-debugging-port={ChromeConstants.DEBUGGING_PORT}" in chrome_command
    assert any(argument.startswith("--user-data-dir=") for argument in chrome_command)
