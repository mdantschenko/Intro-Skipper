import logging
from pathlib import Path

from intro_skipper.helpers.constants import ApplicationConstants
from intro_skipper.logging_configuration import configure_logging


def test_log_folder_and_file_are_created_when_log_files_are_enabled(
    tmp_path: Path,
) -> None:
    log_directory = tmp_path / "logs"
    log_file_path = configure_logging(write_log_file=True, log_directory=log_directory)

    logging.getLogger(ApplicationConstants.LOGGER_NAME).info("Netflix: skipped intro")

    assert log_file_path is not None
    assert log_file_path.parent == log_directory
    assert "Netflix: skipped intro" in log_file_path.read_text(encoding="utf-8")


def test_no_log_folder_or_file_is_created_by_default(tmp_path: Path) -> None:
    log_directory = tmp_path / "logs"
    log_file_path = configure_logging(write_log_file=False, log_directory=log_directory)

    logging.getLogger(ApplicationConstants.LOGGER_NAME).info("Netflix: skipped intro")

    assert log_file_path is None
    assert not log_directory.exists()
