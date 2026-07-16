import logging
import sys
from pathlib import Path

from intro_skipper.application import IntroSkipperApplication
from intro_skipper.browser.browser_connection import BrowserConnection
from intro_skipper.browser.chrome_connection import ChromeConnection
from intro_skipper.browser.chrome_launcher import ChromeLauncher
from intro_skipper.chrome_executable_prompt import (
    resolve_chrome_executable_interactively,
)
from intro_skipper.command_line_arguments import parse_command_line_options
from intro_skipper.helpers.constants import ApplicationConstants
from intro_skipper.logging_configuration import configure_logging
from intro_skipper.services.streaming_service import StreamingService
from intro_skipper.remote_control import RemoteControlServer
from intro_skipper.services.streaming_service_catalog import (
    build_all_streaming_services,
)
from intro_skipper.skipping_switch import SkippingSwitch
from intro_skipper.update_notification import build_update_notification


def main() -> None:
    command_line_options = parse_command_line_options(sys.argv[1:])
    log_file_path = configure_logging(
        write_log_file=command_line_options.write_log_file
    )
    logger = logging.getLogger(ApplicationConstants.LOGGER_NAME)

    _report_startup_information(logger, log_file_path)
    chrome_connection = ChromeConnection()
    _open_chrome_with_requested_services(
        chrome_connection, command_line_options.streaming_services, logger
    )

    skipping_switch = SkippingSwitch()
    remote_control_server = RemoteControlServer(
        chrome_connection, build_all_streaming_services(), skipping_switch
    )
    remote_control_server.start_in_background()
    logger.info(
        "Phone remote: open %s in your phone browser (same WLAN).",
        remote_control_server.build_page_address(),
    )

    application = IntroSkipperApplication(
        chrome_connection, build_all_streaming_services(), skipping_switch
    )
    try:
        application.run_forever()
    except KeyboardInterrupt:
        pass
    remote_control_server.shut_down()
    logger.info("Intro Skipper stopped.")


def _report_startup_information(
    logger: logging.Logger, log_file_path: Path | None
) -> None:
    update_notification = build_update_notification()
    if update_notification is not None:
        logger.info(update_notification)
    logger.info(
        "Intro Skipper is running. Stream the series tab to the Chromecast "
        "via the Chrome menu, everything else happens automatically."
    )
    if log_file_path is not None:
        logger.info("Every event is also written to %s.", log_file_path)


def _open_chrome_with_requested_services(
    browser_connection: BrowserConnection,
    requested_streaming_services: tuple[StreamingService, ...],
    logger: logging.Logger,
) -> None:
    start_page_urls = tuple(
        streaming_service.homepage_url
        for streaming_service in requested_streaming_services
    )
    chrome_launcher = ChromeLauncher(
        browser_connection,
        chrome_executable_provider=resolve_chrome_executable_interactively,
    )
    chrome_launcher.ensure_browser_is_running(start_page_urls)
    for streaming_service in requested_streaming_services:
        logger.info("Opened %s.", streaming_service.name)
