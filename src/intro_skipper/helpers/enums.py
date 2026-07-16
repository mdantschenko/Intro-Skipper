from enum import StrEnum


class SkipKind(StrEnum):
    INTRO = "intro"
    RECAP = "recap"
    NEXT_EPISODE = "next_episode"
    STILL_WATCHING = "still_watching"
