from dataclasses import dataclass


@dataclass(frozen=True)
class SkipTarget:
    description: str
    css_selector: str


@dataclass(frozen=True)
class StreamingService:
    name: str
    url_fragments: tuple[str, ...]
    homepage_url: str
    command_line_aliases: tuple[str, ...]
    skip_targets: tuple[SkipTarget, ...]

    def matches_url(self, url: str) -> bool:
        return any(url_fragment in url for url_fragment in self.url_fragments)
