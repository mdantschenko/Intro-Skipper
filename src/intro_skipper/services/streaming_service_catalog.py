from intro_skipper.helpers.constants import (
    AmazonPrimeSelectors,
    DisneyPlusSelectors,
    NetflixSelectors,
)
from intro_skipper.services.streaming_service import SkipTarget, StreamingService


def build_netflix() -> StreamingService:
    return StreamingService(
        name="Netflix",
        url_fragments=("netflix.com",),
        skip_targets=(
            SkipTarget("skipped the intro", NetflixSelectors.SKIP_INTRO),
            SkipTarget("skipped the recap", NetflixSelectors.SKIP_RECAP),
            SkipTarget("started the next episode", NetflixSelectors.NEXT_EPISODE),
            SkipTarget(
                "confirmed the still-watching prompt",
                NetflixSelectors.CONTINUE_WATCHING,
            ),
        ),
    )


def build_disney_plus() -> StreamingService:
    return StreamingService(
        name="Disney+",
        url_fragments=("disneyplus.com",),
        skip_targets=(
            SkipTarget(
                "skipped the intro or recap",
                DisneyPlusSelectors.SKIP_INTRO_OR_RECAP,
            ),
            SkipTarget("started the next episode", DisneyPlusSelectors.NEXT_EPISODE),
        ),
    )


def build_amazon_prime() -> StreamingService:
    return StreamingService(
        name="Amazon Prime Video",
        url_fragments=("amazon.", "primevideo.com"),
        skip_targets=(
            SkipTarget(
                "skipped the intro or recap",
                AmazonPrimeSelectors.SKIP_INTRO_OR_RECAP,
            ),
            SkipTarget("started the next episode", AmazonPrimeSelectors.NEXT_EPISODE),
        ),
    )


def build_all_streaming_services() -> tuple[StreamingService, ...]:
    return (build_netflix(), build_disney_plus(), build_amazon_prime())
