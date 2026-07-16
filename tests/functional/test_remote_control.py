import json
import urllib.error
import urllib.request
from typing import Any, Iterator

import pytest

from intro_skipper.helpers.enums import SkipKind
from intro_skipper.remote_control import RemoteControlServer
from intro_skipper.services.streaming_service_catalog import (
    build_all_streaming_services,
)
from intro_skipper.skipping_settings import SkippingSettings
from tests.functional.browser_fakes import FakeBrowserConnection, FakeBrowserTab

NETFLIX_EPISODE_URL = "https://www.netflix.com/watch/81091393"
PLAYING_VIDEO_STATE = {
    "paused": False,
    "position_seconds": 125.0,
    "duration_seconds": 2700.0,
    "volume": 0.8,
}


@pytest.fixture
def netflix_tab() -> FakeBrowserTab:
    browser_tab = FakeBrowserTab(NETFLIX_EPISODE_URL)
    browser_tab.javascript_result = PLAYING_VIDEO_STATE
    return browser_tab


RunningServer = tuple[RemoteControlServer, SkippingSettings]


@pytest.fixture
def running_server(
    netflix_tab: FakeBrowserTab,
) -> Iterator[RunningServer]:
    browser_connection = FakeBrowserConnection(open_tabs=[netflix_tab])
    skipping_settings = SkippingSettings()
    server = RemoteControlServer(
        browser_connection, build_all_streaming_services(), skipping_settings, port=0
    )
    server.start_in_background()
    yield server, skipping_settings
    server.shut_down()


def read_response(server: RemoteControlServer, path: str) -> bytes:
    address = f"http://127.0.0.1:{server.port}{path}"
    with urllib.request.urlopen(address) as response:  # skylos: ignore local server
        return response.read()


def read_json(server: RemoteControlServer, path: str) -> dict[str, Any]:
    return json.loads(read_response(server, path))


def post_command(server: RemoteControlServer, command: dict[str, Any]) -> int:
    request = urllib.request.Request(
        f"http://127.0.0.1:{server.port}/command",
        data=json.dumps(command).encode("utf-8"),
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:  # skylos: ignore local
            return response.status
    except urllib.error.HTTPError as error:
        return error.code


def test_the_remote_page_is_served(running_server: RunningServer) -> None:
    server, _ = running_server
    page = read_response(server, "/").decode("utf-8")
    assert "Intro Skipper" in page
    assert "seek-bar" in page
    assert "jump-back" in page
    assert "jump-forward" in page
    assert "volume-percent" in page
    assert "live-view" in page
    assert "restart-episode" in page
    assert "next-episode" in page
    assert "browse-button" in page


def test_the_state_reports_video_and_skipping(running_server: RunningServer) -> None:
    server, _ = running_server
    state = read_json(server, "/state")
    assert state["skipping"] == {
        "intro": True,
        "recap": True,
        "next_episode": True,
        "still_watching": True,
    }
    assert state["video"]["position_seconds"] == 125.0
    assert state["video"]["duration_seconds"] == 2700.0


def test_toggling_one_skip_kind_leaves_the_others_alone(
    running_server: RunningServer,
) -> None:
    server, skipping_settings = running_server
    post_command(server, {"action": "toggle_skipping", "kind": "intro"})
    assert skipping_settings.is_enabled_for_any((SkipKind.INTRO,)) is False
    skipping_state = read_json(server, "/state")["skipping"]
    assert skipping_state["intro"] is False
    assert skipping_state["recap"] is True


def test_an_unknown_skip_kind_is_rejected(running_server: RunningServer) -> None:
    server, _ = running_server
    assert post_command(server, {"action": "toggle_skipping", "kind": "ads"}) == 400


def test_playback_commands_reach_the_video_tab(
    running_server: RunningServer, netflix_tab: FakeBrowserTab
) -> None:
    server, _ = running_server
    post_command(server, {"action": "toggle_playback"})
    post_command(server, {"action": "jump", "seconds": -10})
    post_command(server, {"action": "seek", "position_seconds": 300})
    post_command(server, {"action": "volume_up"})
    executed = "".join(netflix_tab.evaluated_javascript)
    assert "video.play()" in executed
    assert "seekToSeconds(Math.max(0, video.currentTime + -10.0))" in executed
    assert "seekToSeconds(Math.max(0, 300.0))" in executed
    assert "getVideoPlayerBySessionId" in executed
    assert "video.volume" in executed


def test_an_unknown_action_is_rejected(running_server: RunningServer) -> None:
    server, _ = running_server
    assert post_command(server, {"action": "explode"}) == 400


def test_the_live_frame_is_served_from_the_screencast(
    running_server: RunningServer, netflix_tab: FakeBrowserTab
) -> None:
    server, _ = running_server
    assert read_response(server, "/screenshot") == b"fake-jpeg-frame"
    assert len(netflix_tab.opened_screencasts) == 1


def test_stop_live_view_ends_the_screencast(
    running_server: RunningServer, netflix_tab: FakeBrowserTab
) -> None:
    server, _ = running_server
    read_response(server, "/screenshot")
    post_command(server, {"action": "stop_live_view"})
    assert netflix_tab.opened_screencasts[0].stopped is True


def test_taps_and_scrolls_reach_the_service_tab(
    running_server: RunningServer, netflix_tab: FakeBrowserTab
) -> None:
    server, _ = running_server
    post_command(server, {"action": "tap", "x_fraction": 0.25, "y_fraction": 0.75})
    post_command(server, {"action": "scroll", "delta_y": 120})
    assert netflix_tab.taps == [(0.25, 0.75)]
    assert netflix_tab.scroll_deltas == [120.0]


def test_navigate_home_leads_back_to_the_service_homepage(
    running_server: RunningServer, netflix_tab: FakeBrowserTab
) -> None:
    server, _ = running_server
    post_command(server, {"action": "navigate_home"})
    assert any(
        "https://www.netflix.com" in javascript
        for javascript in netflix_tab.evaluated_javascript
    )


def test_episode_buttons_reach_the_video_tab(
    running_server: RunningServer, netflix_tab: FakeBrowserTab
) -> None:
    server, _ = running_server
    post_command(server, {"action": "next_episode"})
    post_command(server, {"action": "restart_episode"})
    executed = "".join(netflix_tab.evaluated_javascript)
    assert "control-next" in executed
    assert "seekToSeconds(Math.max(0, 0.0))" in executed
