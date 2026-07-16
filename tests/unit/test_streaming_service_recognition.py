from intro_skipper.services.streaming_service_catalog import (
    build_all_streaming_services,
)


def find_service_names_matching(url: str) -> list[str]:
    return [
        streaming_service.name
        for streaming_service in build_all_streaming_services()
        if streaming_service.matches_url(url)
    ]


def test_netflix_is_recognized_by_watch_url() -> None:
    assert find_service_names_matching("https://www.netflix.com/watch/81091393") == [
        "Netflix"
    ]


def test_disney_plus_is_recognized_by_video_url() -> None:
    assert find_service_names_matching("https://www.disneyplus.com/video/3e06e1e2") == [
        "Disney+"
    ]


def test_amazon_prime_is_recognized_by_german_store_url() -> None:
    assert find_service_names_matching(
        "https://www.amazon.de/gp/video/detail/B0DTLJ3K2M"
    ) == ["Amazon Prime Video"]


def test_amazon_prime_is_recognized_by_primevideo_url() -> None:
    assert find_service_names_matching(
        "https://www.primevideo.com/detail/B0DTLJ3K2M"
    ) == ["Amazon Prime Video"]


def test_unrelated_website_matches_no_service() -> None:
    assert find_service_names_matching("https://www.youtube.com/watch?v=abc") == []
