import pytest

from intro_skipper.application import IntroSkipperApplication
from intro_skipper.browser.browser_connection import BrowserTab
from intro_skipper.helpers.constants import (
    AmazonPrimeSelectors,
    ApplicationConstants,
    DisneyPlusSelectors,
    NetflixSelectors,
)
from intro_skipper.services.streaming_service_catalog import (
    build_all_streaming_services,
)
from intro_skipper.skipping_switch import SkippingSwitch
from tests.functional.browser_fakes import FakeBrowserConnection, FakeBrowserTab

NETFLIX_EPISODE_URL = "https://www.netflix.com/watch/81091393"


def run_single_pass_over(*browser_tabs: FakeBrowserTab) -> None:
    browser_connection = FakeBrowserConnection(open_tabs=list(browser_tabs))
    application = IntroSkipperApplication(
        browser_connection, build_all_streaming_services()
    )
    application.run_single_pass()


def test_visible_netflix_intro_button_is_clicked() -> None:
    netflix_tab = FakeBrowserTab(NETFLIX_EPISODE_URL, {NetflixSelectors.SKIP_INTRO})
    run_single_pass_over(netflix_tab)
    assert netflix_tab.clicked_css_selectors == [NetflixSelectors.SKIP_INTRO]


def test_visible_netflix_recap_button_is_clicked() -> None:
    netflix_tab = FakeBrowserTab(NETFLIX_EPISODE_URL, {NetflixSelectors.SKIP_RECAP})
    run_single_pass_over(netflix_tab)
    assert netflix_tab.clicked_css_selectors == [NetflixSelectors.SKIP_RECAP]


def test_netflix_next_episode_button_is_clicked() -> None:
    netflix_tab = FakeBrowserTab(NETFLIX_EPISODE_URL, {NetflixSelectors.NEXT_EPISODE})
    run_single_pass_over(netflix_tab)
    assert netflix_tab.clicked_css_selectors == [NetflixSelectors.NEXT_EPISODE]


def test_netflix_still_watching_dialog_is_confirmed() -> None:
    netflix_tab = FakeBrowserTab(
        NETFLIX_EPISODE_URL, {NetflixSelectors.CONTINUE_WATCHING}
    )
    run_single_pass_over(netflix_tab)
    assert netflix_tab.clicked_css_selectors == [NetflixSelectors.CONTINUE_WATCHING]


def test_disney_plus_skip_button_is_clicked() -> None:
    disney_plus_tab = FakeBrowserTab(
        "https://www.disneyplus.com/video/3e06e1e2",
        {DisneyPlusSelectors.SKIP_INTRO_OR_RECAP},
    )
    run_single_pass_over(disney_plus_tab)
    assert disney_plus_tab.clicked_css_selectors == [
        DisneyPlusSelectors.SKIP_INTRO_OR_RECAP
    ]


def test_amazon_prime_skip_button_is_clicked() -> None:
    amazon_prime_tab = FakeBrowserTab(
        "https://www.amazon.de/gp/video/detail/B0DTLJ3K2M",
        {AmazonPrimeSelectors.SKIP_INTRO_OR_RECAP},
    )
    run_single_pass_over(amazon_prime_tab)
    assert amazon_prime_tab.clicked_css_selectors == [
        AmazonPrimeSelectors.SKIP_INTRO_OR_RECAP
    ]


def test_tab_without_visible_buttons_stays_untouched() -> None:
    netflix_tab = FakeBrowserTab(NETFLIX_EPISODE_URL)
    run_single_pass_over(netflix_tab)
    assert netflix_tab.clicked_css_selectors == []


def test_unrelated_tab_stays_untouched() -> None:
    search_tab = FakeBrowserTab(
        "https://www.google.com/search?q=serien", {NetflixSelectors.SKIP_INTRO}
    )
    run_single_pass_over(search_tab)
    assert search_tab.clicked_css_selectors == []


class WindowClosingBrowserConnection(FakeBrowserConnection):
    """Answers on the port, but all tabs disappear after the first pass."""

    def list_open_tabs(self) -> list[BrowserTab]:
        open_tabs = super().list_open_tabs()
        self.open_tabs = []
        return open_tabs


def test_nothing_is_clicked_while_skipping_is_switched_off() -> None:
    netflix_tab = FakeBrowserTab(NETFLIX_EPISODE_URL, {NetflixSelectors.SKIP_INTRO})
    browser_connection = FakeBrowserConnection(open_tabs=[netflix_tab])
    skipping_switch = SkippingSwitch()
    skipping_switch.toggle()
    application = IntroSkipperApplication(
        browser_connection, build_all_streaming_services(), skipping_switch
    )
    application.run_single_pass()
    assert netflix_tab.clicked_css_selectors == []


def test_application_stops_when_chrome_is_closed() -> None:
    browser_connection = FakeBrowserConnection(reachable=False)
    application = IntroSkipperApplication(
        browser_connection, build_all_streaming_services()
    )
    application.run_forever()


def test_application_stops_when_the_last_chrome_window_was_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(ApplicationConstants, "POLLING_INTERVAL_SECONDS", 0.0)
    browser_connection = WindowClosingBrowserConnection(
        open_tabs=[FakeBrowserTab(NETFLIX_EPISODE_URL)]
    )
    application = IntroSkipperApplication(
        browser_connection, build_all_streaming_services()
    )
    application.run_forever()
