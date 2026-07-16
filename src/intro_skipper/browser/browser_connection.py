from abc import ABC, abstractmethod


class BrowserCommunicationError(Exception):
    """Signals that the browser could not be reached or did not answer."""


class ScreencastHandle(ABC):
    @abstractmethod
    def latest_frame(self) -> bytes | None:
        """Return the most recent JPEG frame, or None before the first one."""

    @abstractmethod
    def stop(self) -> None:
        """End the screencast stream."""


class BrowserTab(ABC):  # skylos: ignore[SKY-Q702] interfaces share no state
    @property
    @abstractmethod
    def url(self) -> str:
        """Address of the page currently shown in this tab."""

    @abstractmethod
    def click_first_visible_element(self, css_selector: str) -> bool:
        """Click the first visible matching element and report whether one was clicked."""

    @abstractmethod
    def evaluate_javascript(self, javascript: str) -> object:
        """Run the expression in the tab and return its JSON value."""

    @abstractmethod
    def capture_screenshot(self) -> bytes:
        """Return the current tab content as a JPEG image."""

    @abstractmethod
    def tap_at_fraction(self, x_fraction: float, y_fraction: float) -> None:
        """Click the page at the given fractions of the viewport size."""

    @abstractmethod
    def scroll_by(self, delta_y: float) -> None:
        """Scroll the page vertically by the given amount of pixels."""

    @property
    @abstractmethod
    def identifier(self) -> str:
        """Stable identity of this tab across repeated tab listings."""

    @abstractmethod
    def open_screencast(self) -> ScreencastHandle:
        """Start a continuous frame stream of this tab."""


class BrowserConnection(ABC):  # skylos: ignore[SKY-Q702] interfaces share no state
    @abstractmethod
    def is_reachable(self) -> bool:
        """Report whether the browser answers on its debugging interface."""

    @abstractmethod
    def list_open_tabs(self) -> list[BrowserTab]:
        """Return every page tab the browser currently has open."""

    @abstractmethod
    def open_new_tab(self, url: str = "") -> None:
        """Open a new tab (blank by default), creating a window if none exists."""
