import logging
from datetime import datetime
from pathlib import Path

from intro_skipper.helpers.constants import ApplicationConstants


def configure_logging(
    *,
    write_log_file: bool,
    log_directory: Path = ApplicationConstants.LOG_DIRECTORY,
) -> Path | None:
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    log_file_path = _prepare_log_file_path(log_directory) if write_log_file else None
    if log_file_path is not None:
        handlers.append(logging.FileHandler(log_file_path, encoding="utf-8"))
    logging.basicConfig(
        level=logging.INFO,
        format=ApplicationConstants.LOG_MESSAGE_FORMAT,
        handlers=handlers,
        force=True,
    )
    return log_file_path


def _prepare_log_file_path(log_directory: Path) -> Path:
    log_directory.mkdir(parents=True, exist_ok=True)
    start_time = datetime.now().strftime(ApplicationConstants.LOG_TIMESTAMP_FORMAT)
    return log_directory / ApplicationConstants.LOG_FILE_NAME_TEMPLATE.format(
        start_time=start_time
    )
