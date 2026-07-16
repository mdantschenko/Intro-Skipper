from intro_skipper.helpers.enums import SkipKind


class SkippingSettings:
    def __init__(self) -> None:
        self._enabled_kinds = {skip_kind: True for skip_kind in SkipKind}

    def is_enabled_for_any(self, kinds: tuple[SkipKind, ...]) -> bool:
        return any(self._enabled_kinds[skip_kind] for skip_kind in kinds)

    def toggle(self, kind: SkipKind) -> bool:
        self._enabled_kinds[kind] = not self._enabled_kinds[kind]
        return self._enabled_kinds[kind]

    def describe(self) -> dict[str, bool]:
        return {
            skip_kind.value: enabled
            for skip_kind, enabled in self._enabled_kinds.items()
        }
