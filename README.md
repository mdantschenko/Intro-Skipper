# Intro Skipper

Überspringt automatisch Intros, Rückblicke und Abspänne, während du Netflix, Disney+
oder Amazon Prime Video im Chrome-Tab schaust und den Tab auf einen Chromecast streamst.
Netflix' „Weiterschauen?"-Nachfrage wird ebenfalls automatisch bestätigt.

## Funktionsweise

Das Skript startet Chrome mit einem eigenen Profil und aktiviertem
DevTools-Debugging-Port, beobachtet jede Sekunde alle offenen Tabs und klickt die
Skip-Buttons der Streaming-Dienste, sobald sie sichtbar werden. Da das Video beim
Tab-Streaming im Browser läuft, wirkt jeder Klick sofort auf dem Chromecast.

## Voraussetzungen

- Windows mit Google Chrome
- [uv](https://docs.astral.sh/uv/)

## Starten

```
uv sync
uv run python main.py
```

Beim ersten Start öffnet sich ein frisches Chrome-Fenster mit eigenem Profil
(`%LOCALAPPDATA%\IntroSkipper\ChromeProfile`) — dort einmalig bei Netflix, Disney+
bzw. Amazon einloggen. Seit Chrome 136 erlaubt Chrome den Debugging-Port nicht mehr
für das Standard-Profil, deshalb ist das separate Profil notwendig.

Danach: Serie in diesem Chrome-Fenster starten, im Chrome-Menü „Streamen…" wählen
und den Tab an den Chromecast senden. Jede übersprungene Stelle erscheint als
Log-Zeile in der Konsole und wird zusätzlich in einer Log-Datei unter `logs/`
dokumentiert (eine Datei pro Lauf). Das Skript beendet sich automatisch, sobald
du Chrome schließt; Strg+C funktioniert weiterhin.

Ändert ein Dienst seinen Player, müssen nur die CSS-Selektoren in
`src/intro_skipper/helpers/constants.py` angepasst werden.

## Qualitätswerkzeuge

```
uv run pytest
uv run black --check .
uv run radon cc src main.py -s -a
uv run skylos src
uv run complexipy src main.py
uv run pydeps src/intro_skipper --noshow -o dependency_graph.svg
```
