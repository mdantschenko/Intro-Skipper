# Intro Skipper

Automatically skips intros, recaps and credits while you watch Netflix, Disney+
or Amazon Prime Video in a Chrome tab and stream that tab to a Chromecast.
Netflix' "Are you still watching?" prompt is confirmed automatically as well.

## How it works

The script starts Chrome with a dedicated profile and an enabled DevTools
debugging port, watches every open tab once per second and clicks the skip
buttons of the streaming services as soon as they become visible. Because the
video runs inside the browser during tab streaming, every click takes effect
on the Chromecast immediately.

## Requirements

- Windows with Google Chrome (found automatically in the standard install
  locations)
- [uv](https://docs.astral.sh/uv/)

## Getting started

Install it as a tool straight from GitHub (no clone needed):

```
uv tool install git+https://github.com/mdantschenko/Intro-Skipper
intro-skipper
```

Or work from a clone:

```
uv sync
uv run python main.py
```

Streaming services can optionally be opened right at startup:

```
uv run python main.py netflix           # opens Netflix
uv run python main.py netflix disney    # opens Netflix and Disney+
uv run python main.py all               # opens all three services
```

Valid names: `netflix`, `disney`, `amazon` (or `prime`), `all`. When installed
as a tool, the same arguments work directly: `intro-skipper netflix disney`.

On the first start a fresh Chrome window opens with its own profile
(`%LOCALAPPDATA%\IntroSkipper\ChromeProfile`) — log in to Netflix, Disney+ and
Amazon there once. Since Chrome 136 the debugging port is no longer allowed on
the default profile, which is why the separate profile is required.

After that: start an episode in this Chrome window, pick "Cast…" from the
Chrome menu and send the tab to the Chromecast. Every skipped moment shows up
as a log line in the console and is also documented in a log file under
`%LOCALAPPDATA%\IntroSkipper\logs` (one file per run). The script stops automatically as soon as you
close the last Chrome window — even if Chrome keeps running invisibly in the
background; Ctrl+C keeps working too.

If a service changes its player, only the CSS selectors in
`src/intro_skipper/helpers/constants.py` need updating.

## Quality tools

```
uv run pytest
uv run black --check .
uv run ruff check .
uv run radon cc src main.py -s -a
uv run skylos . -a
uv run complexipy src main.py
uv run pydeps src/intro_skipper --noshow -o dependency_graph.svg
uv run --with pyright pyright
```

The full skylos scan (`-a`) checks security, secrets, code quality, AI defect
heuristics and known dependency vulnerabilities in addition to dead code; the
project-specific rules for it live in the `[tool.skylos]` section of
`pyproject.toml`.
