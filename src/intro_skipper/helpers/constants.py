from pathlib import Path


class ApplicationConstants:
    LOGGER_NAME = "intro_skipper"
    POLLING_INTERVAL_SECONDS = 1.0
    DATA_DIRECTORY = Path.home() / "AppData" / "Local" / "IntroSkipper"
    LOG_DIRECTORY = DATA_DIRECTORY / "logs"
    LOG_FILE_NAME_TEMPLATE = "intro_skipper_{start_time}.log"
    LOG_TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"
    LOG_MESSAGE_FORMAT = "%(asctime)s  %(message)s"
    COMMAND_LINE_NAME_FOR_ALL_SERVICES = "all"
    # Whitespace, surrounding quotes from "copy as path" and the invisible
    # byte order mark (U+FEFF) that piped PowerShell input carries.
    TERMINAL_INPUT_CHARACTERS_TO_STRIP = chr(0xFEFF) + ' \t\r\n"'


class StreamingServiceHomepages:
    NETFLIX = "https://www.netflix.com"
    DISNEY_PLUS = "https://www.disneyplus.com"
    AMAZON_PRIME_VIDEO = "https://www.amazon.de/gp/video/storefront"


class SkipTargetDescriptions:
    SKIPPED_INTRO = "skipped the intro"
    SKIPPED_RECAP = "skipped the recap"
    SKIPPED_INTRO_OR_RECAP = "skipped the intro or recap"
    STARTED_NEXT_EPISODE = "started the next episode"
    CONFIRMED_STILL_WATCHING = "confirmed the still-watching prompt"


class ChromeConstants:
    EXECUTABLE_SEARCH_PATHS = (
        Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
        Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
        Path.home()
        / "AppData"
        / "Local"
        / "Google"
        / "Chrome"
        / "Application"
        / "chrome.exe",
    )
    DEBUGGING_PORT = 9222
    USER_PROFILE_DIRECTORY = ApplicationConstants.DATA_DIRECTORY / "ChromeProfile"
    HTTP_REQUEST_TIMEOUT_SECONDS = 2.0
    WEBSOCKET_TIMEOUT_SECONDS = 5.0
    JAVASCRIPT_EVALUATION_REQUEST_ID = 1
    STARTUP_TIMEOUT_SECONDS = 20.0
    STARTUP_POLL_INTERVAL_SECONDS = 0.5
    NEW_TAB_PAGE_URL = "chrome://newtab/"


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
