import logging

from intro_skipper.application import IntroSkipperApplication
from intro_skipper.browser.chrome_connection import ChromeConnection
from intro_skipper.browser.chrome_launcher import ChromeLauncher
from intro_skipper.helpers.constants import ApplicationConstants
from intro_skipper.services.streaming_service_catalog import (
    build_all_streaming_services,
)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s")
    logger = logging.getLogger(ApplicationConstants.LOGGER_NAME)

    chrome_connection = ChromeConnection()
    ChromeLauncher(chrome_connection).ensure_browser_is_running()

    application = IntroSkipperApplication(
        chrome_connection, build_all_streaming_services()
    )
    logger.info(
        "Intro Skipper is running. Stream the series tab to the Chromecast "
        "via the Chrome menu, everything else happens automatically."
    )
    try:
        application.run_forever()
    except KeyboardInterrupt:
        logger.info("Intro Skipper stopped.")


if __name__ == "__main__":
    main()
