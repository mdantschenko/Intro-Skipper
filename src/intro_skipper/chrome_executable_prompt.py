from pathlib import Path
from typing import Callable, Sequence

from intro_skipper.browser.chrome_launcher import find_chrome_executable
from intro_skipper.helpers.constants import ApplicationConstants, ChromeConstants


def resolve_chrome_executable_interactively(
    search_paths: Sequence[Path] = ChromeConstants.EXECUTABLE_SEARCH_PATHS,
    ask_for_input: Callable[[str], str] = input,
    write_message: Callable[[str], None] = print,
) -> Path:
    try:
        return find_chrome_executable(search_paths)
    except FileNotFoundError:
        _explain_missing_chrome(search_paths, write_message)
        return _ask_for_path_until_valid_or_abort(ask_for_input, write_message)


def _explain_missing_chrome(
    search_paths: Sequence[Path], write_message: Callable[[str], None]
) -> None:
    write_message("Google Chrome was not found in the standard install locations:")
    for search_path in search_paths:
        write_message(f"  - {search_path}")
    write_message(
        "If Chrome is installed somewhere else, enter the full path to your "
        "chrome.exe below. You can find it by right-clicking your Chrome "
        'shortcut and choosing Properties - the "Target" field shows the path.'
    )


def _ask_for_path_until_valid_or_abort(
    ask_for_input: Callable[[str], str], write_message: Callable[[str], None]
) -> Path:
    while True:
        try:
            answer = ask_for_input("Path to chrome.exe (leave empty to quit): ")
        except (EOFError, KeyboardInterrupt) as interruption:
            raise SystemExit(
                "Intro Skipper stopped: no Chrome path was provided."
            ) from interruption
        cleaned_answer = answer.strip(
            ApplicationConstants.TERMINAL_INPUT_CHARACTERS_TO_STRIP
        )
        if not cleaned_answer:
            raise SystemExit("Intro Skipper stopped: no Chrome path was provided.")
        candidate_path = Path(cleaned_answer)
        if candidate_path.is_file():
            return candidate_path
        write_message(f"There is no file at {candidate_path}, please try again.")
