import logging
from pathlib import Path

from intro_skipper.helpers.constants import ApplicationConstants
from intro_skipper.logging_configuration import configure_logging


def test_log_folder_is_created_and_events_are_documented(tmp_path: Path) -> None:
    log_directory = tmp_path / "logs"
    log_file_path = configure_logging(log_directory)

    logging.getLogger(ApplicationConstants.LOGGER_NAME).info("Netflix: skipped intro")

    assert log_directory.is_dir()
    assert log_file_path.parent == log_directory
    assert "Netflix: skipped intro" in log_file_path.read_text(encoding="utf-8")
