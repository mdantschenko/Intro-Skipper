import logging
import sys

from intro_skipper.application import IntroSkipperApplication
from intro_skipper.browser.chrome_connection import ChromeConnection
from intro_skipper.browser.chrome_launcher import ChromeLauncher
from intro_skipper.chrome_executable_prompt import (
    resolve_chrome_executable_interactively,
)
from intro_skipper.command_line_arguments import parse_requested_streaming_services
from intro_skipper.helpers.constants import ApplicationConstants
from intro_skipper.logging_configuration import configure_logging
from intro_skipper.services.streaming_service_catalog import (
    build_all_streaming_services,
)


def main() -> None:
    requested_streaming_services = parse_requested_streaming_services(sys.argv[1:])
    log_file_path = configure_logging()
    logger = logging.getLogger(ApplicationConstants.LOGGER_NAME)

    chrome_connection = ChromeConnection()
    start_page_urls = tuple(
        streaming_service.homepage_url
        for streaming_service in requested_streaming_services
    )
    chrome_launcher = ChromeLauncher(
        chrome_connection,
        chrome_executable_provider=resolve_chrome_executable_interactively,
    )
    chrome_launcher.ensure_browser_is_running(start_page_urls)
    for streaming_service in requested_streaming_services:
        logger.info("Opened %s.", streaming_service.name)

    application = IntroSkipperApplication(
        chrome_connection, build_all_streaming_services()
    )
    logger.info(
        "Intro Skipper is running. Stream the series tab to the Chromecast "
        "via the Chrome menu, everything else happens automatically."
    )
    logger.info("Every event is also written to %s.", log_file_path)
    try:
        application.run_forever()
    except KeyboardInterrupt:
        pass
    logger.info("Intro Skipper stopped.")
