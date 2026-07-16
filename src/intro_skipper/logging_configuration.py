import logging
from datetime import datetime
from pathlib import Path

from intro_skipper.helpers.constants import ApplicationConstants


def configure_logging(
    log_directory: Path = ApplicationConstants.LOG_DIRECTORY,
) -> Path:
    log_directory.mkdir(parents=True, exist_ok=True)
    start_time = datetime.now().strftime(ApplicationConstants.LOG_TIMESTAMP_FORMAT)
    log_file_path = log_directory / ApplicationConstants.LOG_FILE_NAME_TEMPLATE.format(
        start_time=start_time
    )
    logging.basicConfig(
        level=logging.INFO,
        format=ApplicationConstants.LOG_MESSAGE_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file_path, encoding="utf-8"),
        ],
        force=True,
    )
    return log_file_path
