from pathlib import Path


class ApplicationConstants:
    LOGGER_NAME = "intro_skipper"
    POLLING_INTERVAL_SECONDS = 1.0
    LOG_DIRECTORY = Path("logs")
    LOG_FILE_NAME_TEMPLATE = "intro_skipper_{start_time}.log"
    LOG_TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"
    LOG_MESSAGE_FORMAT = "%(asctime)s  %(message)s"


class ChromeConstants:
    EXECUTABLE_PATH = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")
    DEBUGGING_PORT = 9222
    USER_PROFILE_DIRECTORY = (
        Path.home() / "AppData" / "Local" / "IntroSkipper" / "ChromeProfile"
    )
    HTTP_REQUEST_TIMEOUT_SECONDS = 2.0
    WEBSOCKET_TIMEOUT_SECONDS = 5.0
    JAVASCRIPT_EVALUATION_REQUEST_ID = 1
    STARTUP_TIMEOUT_SECONDS = 20.0
    STARTUP_POLL_INTERVAL_SECONDS = 0.5


class JavaScriptSnippets:
    CLICK_FIRST_VISIBLE_ELEMENT_TEMPLATE = """
        (() => {
            for (const element of document.querySelectorAll(__CSS_SELECTOR__)) {
                if (element.getClientRects().length > 0) {
                    element.click();
                    return true;
                }
            }
            return false;
        })()
    """


class NetflixSelectors:
    SKIP_INTRO = '[data-uia="player-skip-intro"]'
    SKIP_RECAP = '[data-uia="player-skip-recap"]'
    NEXT_EPISODE = '[data-uia^="next-episode-seamless-button"]'
    CONTINUE_WATCHING = '[data-uia="interrupt-autoplay-continue"]'


class DisneyPlusSelectors:
    SKIP_INTRO_OR_RECAP = "button.skip__button"
    NEXT_EPISODE = '[data-testid="up-next-play-button"]'


class AmazonPrimeSelectors:
    SKIP_INTRO_OR_RECAP = ".atvwebplayersdk-skipelement-button"
    NEXT_EPISODE = ".atvwebplayersdk-nextupcard-button"
