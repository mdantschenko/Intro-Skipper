from pathlib import Path
from typing import Sequence

import pytest

from intro_skipper.browser.chrome_launcher import ChromeLauncher, find_chrome_executable
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


def test_the_regular_new_tab_page_is_opened_when_chrome_runs_invisibly() -> None:
    browser_connection = FakeBrowserConnection(open_tabs=[], reachable=True)
    process_recorder = ChromeProcessRecorder(browser_connection)
    ChromeLauncher(browser_connection, process_recorder).ensure_browser_is_running()
    assert [browser_tab.url for browser_tab in browser_connection.open_tabs] == [
        ChromeConstants.NEW_TAB_PAGE_URL
    ]


def test_no_extra_tab_is_opened_when_a_window_already_exists() -> None:
    browser_connection = FakeBrowserConnection(
        open_tabs=[FakeBrowserTab("https://www.netflix.com/browse")], reachable=True
    )
    process_recorder = ChromeProcessRecorder(browser_connection)
    ChromeLauncher(browser_connection, process_recorder).ensure_browser_is_running()
    assert len(browser_connection.open_tabs) == 1


def test_only_the_requested_start_pages_are_opened_in_a_running_browser() -> None:
    browser_connection = FakeBrowserConnection(open_tabs=[], reachable=True)
    process_recorder = ChromeProcessRecorder(browser_connection)
    ChromeLauncher(browser_connection, process_recorder).ensure_browser_is_running(
        ("https://www.netflix.com", "https://www.disneyplus.com")
    )
    assert [browser_tab.url for browser_tab in browser_connection.open_tabs] == [
        "https://www.netflix.com",
        "https://www.disneyplus.com",
    ]


def test_requested_start_pages_are_part_of_the_chrome_start_command() -> None:
    browser_connection = FakeBrowserConnection(reachable=False)
    process_recorder = ChromeProcessRecorder(browser_connection)
    ChromeLauncher(browser_connection, process_recorder).ensure_browser_is_running(
        ("https://www.netflix.com",)
    )
    (chrome_command,) = process_recorder.started_commands
    assert chrome_command[-1] == "https://www.netflix.com"


def test_chrome_is_started_with_debugging_port_and_separate_profile() -> None:
    browser_connection = FakeBrowserConnection(reachable=False)
    process_recorder = ChromeProcessRecorder(browser_connection)
    ChromeLauncher(browser_connection, process_recorder).ensure_browser_is_running()
    (chrome_command,) = process_recorder.started_commands
    assert chrome_command[0].endswith("chrome.exe")
    assert f"--remote-debugging-port={ChromeConstants.DEBUGGING_PORT}" in chrome_command
    assert any(argument.startswith("--user-data-dir=") for argument in chrome_command)


def test_chrome_is_found_in_the_first_existing_install_location(
    tmp_path: Path,
) -> None:
    chrome_executable = tmp_path / "chrome.exe"
    chrome_executable.touch()
    missing_location = tmp_path / "missing" / "chrome.exe"
    assert find_chrome_executable((missing_location, chrome_executable)) == (
        chrome_executable
    )


def test_a_missing_chrome_installation_is_reported(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        find_chrome_executable((tmp_path / "missing" / "chrome.exe",))
