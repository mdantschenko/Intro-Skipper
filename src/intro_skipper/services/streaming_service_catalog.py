from intro_skipper.helpers.constants import (
    AmazonPrimeSelectors,
    DisneyPlusSelectors,
    NetflixSelectors,
    SkipTargetDescriptions,
    StreamingServiceHomepages,
)
from intro_skipper.services.streaming_service import SkipTarget, StreamingService


def build_netflix() -> StreamingService:
    return StreamingService(
        name="Netflix",
        url_fragments=("netflix.com",),
        homepage_url=StreamingServiceHomepages.NETFLIX,
        command_line_aliases=("netflix",),
        skip_targets=(
            SkipTarget(
                SkipTargetDescriptions.SKIPPED_INTRO,
                NetflixSelectors.SKIP_INTRO,
            ),
            SkipTarget(
                SkipTargetDescriptions.SKIPPED_RECAP,
                NetflixSelectors.SKIP_RECAP,
            ),
            SkipTarget(
                SkipTargetDescriptions.STARTED_NEXT_EPISODE,
                NetflixSelectors.NEXT_EPISODE,
            ),
            SkipTarget(
                SkipTargetDescriptions.CONFIRMED_STILL_WATCHING,
                NetflixSelectors.CONTINUE_WATCHING,
            ),
        ),
    )


def build_disney_plus() -> StreamingService:
    return StreamingService(
        name="Disney+",
        url_fragments=("disneyplus.com",),
        homepage_url=StreamingServiceHomepages.DISNEY_PLUS,
        command_line_aliases=("disney",),
        skip_targets=(
            SkipTarget(
                SkipTargetDescriptions.SKIPPED_INTRO_OR_RECAP,
                DisneyPlusSelectors.SKIP_INTRO_OR_RECAP,
            ),
            SkipTarget(
                SkipTargetDescriptions.STARTED_NEXT_EPISODE,
                DisneyPlusSelectors.NEXT_EPISODE,
            ),
        ),
    )


def build_amazon_prime() -> StreamingService:
    return StreamingService(
        name="Amazon Prime Video",
        url_fragments=("amazon.", "primevideo.com"),
        homepage_url=StreamingServiceHomepages.AMAZON_PRIME_VIDEO,
        command_line_aliases=("amazon", "prime"),
        skip_targets=(
            SkipTarget(
                SkipTargetDescriptions.SKIPPED_INTRO_OR_RECAP,
                AmazonPrimeSelectors.SKIP_INTRO_OR_RECAP,
            ),
            SkipTarget(
                SkipTargetDescriptions.STARTED_NEXT_EPISODE,
                AmazonPrimeSelectors.NEXT_EPISODE,
            ),
        ),
    )


def build_all_streaming_services() -> tuple[StreamingService, ...]:
    return (build_netflix(), build_disney_plus(), build_amazon_prime())
