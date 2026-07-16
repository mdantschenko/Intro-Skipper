from pathlib import Path

import pytest

from intro_skipper.chrome_executable_prompt import (
    resolve_chrome_executable_interactively,
)


class TerminalRecorder:
    def __init__(self, answers: list[str]) -> None:
        self._answers = answers
        self.written_messages: list[str] = []

    def ask_for_input(self, prompt: str) -> str:
        self.written_messages.append(prompt)
        return self._answers.pop(0)

    def write_message(self, message: str) -> None:
        self.written_messages.append(message)


def test_an_installed_chrome_is_used_without_any_interaction(tmp_path: Path) -> None:
    chrome_executable = tmp_path / "chrome.exe"
    chrome_executable.touch()
    terminal = TerminalRecorder(answers=[])

    resolved_path = resolve_chrome_executable_interactively(
        (chrome_executable,), terminal.ask_for_input, terminal.write_message
    )

    assert resolved_path == chrome_executable
    assert terminal.written_messages == []


def test_a_manually_entered_path_is_accepted_with_quotes_and_byte_order_mark(
    tmp_path: Path,
) -> None:
    chrome_executable = tmp_path / "chrome.exe"
    chrome_executable.touch()
    terminal = TerminalRecorder(answers=[f'{chr(0xFEFF)}"{chrome_executable}"'])

    resolved_path = resolve_chrome_executable_interactively(
        (tmp_path / "missing" / "chrome.exe",),
        terminal.ask_for_input,
        terminal.write_message,
    )

    assert resolved_path == chrome_executable


def test_a_wrong_path_can_be_corrected(tmp_path: Path) -> None:
    chrome_executable = tmp_path / "chrome.exe"
    chrome_executable.touch()
    terminal = TerminalRecorder(
        answers=[str(tmp_path / "wrong.exe"), str(chrome_executable)]
    )

    resolved_path = resolve_chrome_executable_interactively(
        (tmp_path / "missing" / "chrome.exe",),
        terminal.ask_for_input,
        terminal.write_message,
    )

    assert resolved_path == chrome_executable
    assert any("try again" in message for message in terminal.written_messages)


def test_empty_input_stops_the_program(tmp_path: Path) -> None:
    terminal = TerminalRecorder(answers=[""])

    with pytest.raises(SystemExit):
        resolve_chrome_executable_interactively(
            (tmp_path / "missing" / "chrome.exe",),
            terminal.ask_for_input,
            terminal.write_message,
        )
