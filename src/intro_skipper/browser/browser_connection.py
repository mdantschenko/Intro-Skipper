from abc import ABC, abstractmethod


class BrowserCommunicationError(Exception):
    """Signals that the browser could not be reached or did not answer."""


class BrowserTab(ABC):
    @property
    @abstractmethod
    def url(self) -> str:
        """Address of the page currently shown in this tab."""

    @abstractmethod
    def click_first_visible_element(self, css_selector: str) -> bool:
        """Click the first visible matching element and report whether one was clicked."""


class BrowserConnection(ABC):
    @abstractmethod
    def is_reachable(self) -> bool:
        """Report whether the browser answers on its debugging interface."""

    @abstractmethod
    def list_open_tabs(self) -> list[BrowserTab]:
        """Return every page tab the browser currently has open."""

    @abstractmethod
    def open_new_tab(self, url: str = "") -> None:
        """Open a new tab (blank by default), creating a window if none exists."""
