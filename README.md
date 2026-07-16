# Intro Skipper

Automatically skips intros, recaps and credits while you watch Netflix, Disney+
or Amazon Prime Video in a Chrome tab and stream that tab to your TV — via
any cast-enabled device (a Chromecast, for example).
Netflix' "Are you still watching?" prompt is confirmed automatically as well.

## Why this exists

I wanted to watch a series with an audio language that is only available in
another region — that needs a VPN, and a TV cannot run one. A PC can: the
episode plays in Chrome on the PC (behind the VPN) and the tab is cast to
the TV, which simply shows what the PC fetches. This tool removes
the friction of that setup: it clicks "Skip intro", "Skip recap",
"Next episode" and the "Still watching?" prompt the moment they appear, and
it serves a remote control page so nobody has to walk to the PC between
episodes.

The remote is made for the phone, but it is just a web page — the startup log
prints the link, and the skip switches can be flipped from the PC browser
just as well. And if you only want the automatic skipping while watching
normally in a tab, the tool does that too; casting is entirely optional.

## How it works

The script starts Chrome with a dedicated profile and an enabled DevTools
debugging port, watches every open tab once per second and clicks the skip
buttons of the streaming services as soon as they become visible. Because the
video runs inside the browser during tab streaming, every click takes effect
on the TV immediately. Any way of mirroring the tab works — a Chromecast,
a TV with cast support built in, or even a plain HDMI cable.

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
Chrome menu and send the tab to your cast device. Every skipped moment shows up
as a log line in the console; when started with `--log`, it is additionally
documented in a log file under `%LOCALAPPDATA%\IntroSkipper\logs` (one file
per run). The script stops automatically as soon as you
close the last Chrome window — even if Chrome keeps running invisibly in the
background; Ctrl+C keeps working too.

If a service changes its player, only the CSS selectors in
`src/intro_skipper/helpers/constants.py` need updating.

### Casting with a VPN and the black-video fix

Always cast through the Chrome menu ("Cast… → sources → Cast tab"), never
through the cast icon inside the player: the in-player icon hands playback
over to the cast device, which then fetches from the service with its own
internet connection — bypassing the VPN and defeating the setup described
above. With tab casting the PC stays in charge of fetching.

If the TV shows only subtitles on a black screen, the GPU's content
protection is blocking the capture. Open `chrome://settings/system` in the
Intro Skipper Chrome window, switch off "Use graphics acceleration when
available", close the window and start the tool again — the setting is
stored permanently in the dedicated profile.

## Phone remote

While the tool runs, it serves a remote control page for your phone. The
startup log shows the address, for example `Phone remote: http://192.168.1.23:8321`
— open it in the phone browser (same WLAN as the PC). The page offers
play/pause, a seek bar, volume with a percentage display, individual on/off
switches for every skip kind (intros, recaps, next episode, the "still
watching?" prompt), restart-episode and next-episode buttons and 10-second
jumps via buttons or by double-tapping the touch area.

The "Browse" button opens a live view of the streaming tab on the phone
(about 10 to 20 frames per second): tap to click, drag to scroll — enough to
leave an episode, browse the catalog and start something new without walking
to the PC. As soon as an episode starts playing, the phone returns to the
control view automatically.

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
