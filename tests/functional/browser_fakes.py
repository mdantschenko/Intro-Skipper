from intro_skipper.browser.browser_connection import (
    BrowserCommunicationError,
    BrowserConnection,
    BrowserTab,
    ScreencastHandle,
)


class FakeScreencastHandle(ScreencastHandle):
    def __init__(self, frame: bytes | None) -> None:
        self.frame = frame
        self.stopped = False

    def latest_frame(self) -> bytes | None:
        return self.frame

    def stop(self) -> None:
        self.stopped = True


class FakeBrowserTab(BrowserTab):
    def __init__(self, url: str, visible_css_selectors: set[str] | None = None) -> None:
        self._url = url
        self.visible_css_selectors = visible_css_selectors or set()
        self.clicked_css_selectors: list[str] = []
        self.javascript_result: object = None
        self.evaluated_javascript: list[str] = []
        self.screencast_frame: bytes | None = b"fake-jpeg-frame"
        self.opened_screencasts: list[FakeScreencastHandle] = []
        self.taps: list[tuple[float, float]] = []
        self.scroll_deltas: list[float] = []

    @property
    def url(self) -> str:
        return self._url

    @property
    def identifier(self) -> str:
        return self._url

    def click_first_visible_element(self, css_selector: str) -> bool:
        if css_selector not in self.visible_css_selectors:
            return False
        self.clicked_css_selectors.append(css_selector)
        return True

    def evaluate_javascript(self, javascript: str) -> object:
        self.evaluated_javascript.append(javascript)
        return self.javascript_result

    def capture_screenshot(self) -> bytes:
        return self.screencast_frame or b""

    def tap_at_fraction(self, x_fraction: float, y_fraction: float) -> None:
        self.taps.append((x_fraction, y_fraction))

    def scroll_by(self, delta_y: float) -> None:
        self.scroll_deltas.append(delta_y)

    def open_screencast(self) -> ScreencastHandle:
        screencast = FakeScreencastHandle(self.screencast_frame)
        self.opened_screencasts.append(screencast)
        return screencast


class FakeBrowserConnection(BrowserConnection):
    def __init__(
        self, open_tabs: list[BrowserTab] | None = None, reachable: bool = True
    ) -> None:
        self.open_tabs = open_tabs or []
        self.reachable = reachable

    def is_reachable(self) -> bool:
        return self.reachable

    def list_open_tabs(self) -> list[BrowserTab]:
        if not self.reachable:
            raise BrowserCommunicationError("Chrome does not answer.")
        return list(self.open_tabs)

    def open_new_tab(self, url: str = "") -> None:
        self.open_tabs.append(FakeBrowserTab(url or "chrome://newtab/"))
