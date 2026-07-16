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
  locations; if Chrome lives somewhere else, the tool asks for the path to
  chrome.exe at startup)
- [uv](https://docs.astral.sh/uv/)

## Installation

Run this once in any terminal (PowerShell) — no clone, no setup, uv downloads
and builds everything by itself:

```
uv tool install git+https://github.com/mdantschenko/Intro-Skipper
```

If the installer warns that `...\.local\bin` is not on your PATH, run
`uv tool update-shell` once and open a new terminal afterwards.

## Usage

After the one-time installation the `intro-skipper` command is available in
every terminal, from any folder — starting it is all you ever do:

```
intro-skipper                   # watch Chrome tabs and skip
intro-skipper netflix           # additionally opens Netflix
intro-skipper netflix disney    # additionally opens Netflix and Disney+
intro-skipper all               # additionally opens all three services
intro-skipper netflix --log     # additionally saves a log file of the run
```

Valid service names: `netflix`, `disney`, `amazon` (or `prime`), `all`.

## Updates

Get the newest version at any time with:

```
uv tool upgrade intro-skipper
```

You do not need to check for updates yourself: on every start the tool
compares its own installed version with the newest one on GitHub and prints a
notice containing exactly this command when an update is available. Without
an internet connection the check is skipped silently.

## Development

Work from a clone of the repository:

```
uv sync
uv run python main.py netflix
```

On the first start a fresh Chrome window opens with its own profile
(`%LOCALAPPDATA%\IntroSkipper\ChromeProfile`) — log in to Netflix, Disney+ and
Amazon there once. Since Chrome 136 the debugging port is no longer allowed on
the default profile, which is why the separate profile is required.

After that: start an episode in this Chrome window, pick "Cast…" from the
Chrome menu and send the tab to the Chromecast. Every skipped moment shows up
as a log line in the console; when started with `--log`, it is additionally
documented in a log file under `%LOCALAPPDATA%\IntroSkipper\logs` (one file
per run). The script stops automatically as soon as you
close the last Chrome window — even if Chrome keeps running invisibly in the
background; Ctrl+C keeps working too.

If a service changes its player, only the CSS selectors in
`src/intro_skipper/helpers/constants.py` need updating.

## Phone remote

While the tool runs, it serves a remote control page for your phone. The
startup log shows the address, for example `Phone remote: http://192.168.1.23:8321`
— open it in the phone browser (same WLAN as the PC). The page offers
play/pause, a seek bar, volume, individual on/off switches for every skip
kind (intros, recaps, next episode, the "still watching?" prompt) and
10-second jumps by double-tapping the left or right half of the touch area.

Windows asks once for a firewall permission on the first start; note that
anyone on the same network can reach the page while the tool runs. If several
addresses are logged, use the one from your home network (usually starting
with 192.168.) — a VPN on the PC adds tunnel addresses that phones cannot
reach.

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
