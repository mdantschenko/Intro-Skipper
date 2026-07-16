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


class RemoteControlConstants:
    PORT = 8321
    VOLUME_STEP = 0.1
    PAGE_FILE_NAME = "remote_page.html"
    TEXT_ENCODING = "utf-8"
    CONTENT_LENGTH_HEADER = "Content-Length"


class VideoControlJavaScript:
    READ_STATE = """
        (() => {
            const video = document.querySelector("video");
            if (video === null || !Number.isFinite(video.duration)) {
                return null;
            }
            return {
                paused: video.paused,
                position_seconds: video.currentTime,
                duration_seconds: video.duration,
                volume: video.volume,
            };
        })()
    """
    TOGGLE_PLAYBACK = """
        (() => {
            const video = document.querySelector("video");
            if (video === null) {
                return false;
            }
            if (video.paused) {
                video.play();
            } else {
                video.pause();
            }
            return true;
        })()
    """
    CHANGE_VOLUME_TEMPLATE = """
        (() => {
            const video = document.querySelector("video");
            if (video === null) {
                return false;
            }
            video.volume = Math.min(1, Math.max(0, video.volume + __VOLUME_STEP__));
            video.muted = false;
            return true;
        })()
    """
    # Netflix rejects direct changes to video.currentTime with error M7375;
    # its internal player API has to seek instead (in milliseconds).
    _SEEK_FUNCTION = """
            const seekToSeconds = (targetSeconds) => {
                if (typeof netflix !== "undefined") {
                    const videoPlayer =
                        netflix.appContext.state.playerApp.getAPI().videoPlayer;
                    const sessionId = videoPlayer.getAllPlayerSessionIds()[0];
                    videoPlayer
                        .getVideoPlayerBySessionId(sessionId)
                        .seek(targetSeconds * 1000);
                    return;
                }
                video.currentTime = targetSeconds;
            };
    """
    JUMP_TEMPLATE = (
        """
        (() => {
            const video = document.querySelector("video");
            if (video === null) {
                return false;
            }
    """
        + _SEEK_FUNCTION
        + """
            seekToSeconds(Math.max(0, video.currentTime + __SECONDS__));
            return true;
        })()
    """
    )
    SEEK_TEMPLATE = (
        """
        (() => {
            const video = document.querySelector("video");
            if (video === null) {
                return false;
            }
    """
        + _SEEK_FUNCTION
        + """
            seekToSeconds(Math.max(0, __POSITION_SECONDS__));
            return true;
        })()
    """
    )
    # Netflix unmounts its control bar while idle, so the next button may
    # not exist yet: click if present, otherwise wake the controls with a
    # mouse move and retry; as a last resort jump to the credits, where the
    # services advance to the next episode on their own.
    NEXT_EPISODE_TEMPLATE = (
        """
        (() => {
            const video = document.querySelector("video");
    """
        + _SEEK_FUNCTION
        + """
            const clickNextButton = () => {
                for (const selector of __CSS_SELECTORS__) {
                    const button = document.querySelector(selector);
                    if (button !== null) {
                        button.click();
                        return true;
                    }
                }
                return false;
            };
            if (clickNextButton()) {
                return true;
            }
            document.dispatchEvent(new MouseEvent("mousemove", { bubbles: true }));
            if (video !== null) {
                video.dispatchEvent(new MouseEvent("mousemove", { bubbles: true }));
            }
            setTimeout(() => {
                if (clickNextButton() || video === null) {
                    return;
                }
                if (Number.isFinite(video.duration)) {
                    seekToSeconds(Math.max(0, video.duration - 3));
                }
            }, 400);
            return true;
        })()
    """
    )


class UpdateCheckConstants:
    DISTRIBUTION_NAME = "intro-skipper"
    LATEST_COMMIT_URL = (
        "https://api.github.com/repos/mdantschenko/Intro-Skipper/commits/main"
    )
    REQUEST_TIMEOUT_SECONDS = 3.0
    UPDATE_COMMAND = "uv tool upgrade intro-skipper"


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
    SCREENSHOT_JPEG_QUALITY = 50
    SCREENCAST_MAX_WIDTH = 1024
    SCREENCAST_MAX_HEIGHT = 640


class JavaScriptSnippets:
    READ_VIEWPORT_SIZE = "({width: window.innerWidth, height: window.innerHeight})"
    NAVIGATE_TEMPLATE = "window.location.href = __TARGET_URL__"
    ENTER_FULLSCREEN = """
        (() => {
            if (document.fullscreenElement !== null) {
                return true;
            }
            document.documentElement.requestFullscreen().catch(() => {});
            return true;
        })()
    """
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


class PlayerControlSelectors:
    # The in-player next buttons of the three services; unlike the credit
    # overlays they exist during the whole episode.
    NEXT_EPISODE_BUTTONS = (
        '[data-uia="control-next"]',
        ".atvwebplayersdk-nexttitle-button",
        'button[aria-label="Next Episode"]',
    )


class DisneyPlusSelectors:
    SKIP_INTRO_OR_RECAP = "button.skip__button"
    NEXT_EPISODE = '[data-testid="up-next-play-button"]'


class AmazonPrimeSelectors:
    SKIP_INTRO_OR_RECAP = ".atvwebplayersdk-skipelement-button"
    NEXT_EPISODE = ".atvwebplayersdk-nextupcard-button"
