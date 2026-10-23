#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ME GOOS-TA DEUTSCH – Lade-Ente für die Konsole                      Version 2.4 (22.10.2026)
=============================================================================================
Eine Ente schwimmt hin und her, wippt im Wasser und dreht an den Enden um – das Ladesymbol der Einrichtung im
Konsolenfenster (dieselbe Animation zeigt die Oberfläche im Browser, siehe ui/index.html „Lade-Ente“).
Nur Standardbibliothek: läuft, bevor irgendein Paket installiert ist.

Benutzung:

    from duck_spinner import DuckSpinner

    with DuckSpinner("Lade Daten"):
        lange_aufgabe()

    spinner = DuckSpinner("Berechne").start()
    spinner.text = "Fast fertig"      # Text lässt sich live ändern
    spinner.zeile("✓ Schritt 1")      # bleibende Zeile über der Animation ausgeben
    spinner.stop("Fertig!")

Effizienz: alle Bilder werden einmal vorberechnet, pro Bild genau ein write() + flush() (10 Bilder/s), der Faden
schläft per Event.wait(). Ohne Terminal (Pipe, Protokolldatei) oder ohne ANSI-Unterstützung wird nur eine Textzeile
ausgegeben. Unter Windows wird die ANSI-Darstellung der Konsole per SetConsoleMode eingeschaltet (kein cmd.exe).
NO_COLOR wird beachtet.
"""

from __future__ import annotations

import atexit
import os
import shutil
import sys
import threading
import time
from math import gcd

# --- ANSI-Steuerzeichen -----------------------------------------------------
RESET = "\x1b[0m"
YELLOW = "\x1b[93m"
ORANGE = "\x1b[38;5;208m"
WHITE = "\x1b[1;97m"
CYAN = "\x1b[96m"
BLUE = "\x1b[34m"
HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"
CLEAR_EOL = "\x1b[K"

# --- Aussehen ---------------------------------------------------------------
DUCK_RIGHT = (
    "    __   ",
    "___( o)> ",
    "\\_____/  ",
)
WAVE_TOP = "~~-~~~-~"
WAVE_BOTTOM = "-.~-.~~ "
ROWS = 4  # 3 Zeilen Ente + Wasser


def _mirror(sprite):
    table = str.maketrans("()<>/\\", ")(><\\/")
    return tuple(row[::-1].translate(table) for row in sprite)


def _cell_color(ch):
    if ch in "<>":
        return ORANGE  # Schnabel
    if ch == "o":
        return WHITE  # Auge
    return YELLOW


def _lcm(*nums):
    result = 1
    for n in nums:
        result = result * n // gcd(result, n)
    return result


def _render_row(cells, color):
    if not color:
        return "".join(ch for ch, _ in cells)
    out, current = [], None
    for ch, col in cells:
        if col != current:
            out.append(col or RESET)
            current = col
        out.append(ch)
    out.append(RESET)
    return "".join(out)


def build_frames(width, color=True):
    """Berechnet alle Bilder einer kompletten, nahtlosen Animationsschleife."""
    sprites = (DUCK_RIGHT, _mirror(DUCK_RIGHT))
    sprite_w = len(DUCK_RIGHT[0])
    span = max(width - sprite_w, 1)

    # Ente schwimmt hin und her und dreht an den Enden kurz um
    path = [(x, 0) for x in range(span + 1)] + [(x, 1) for x in range(span, -1, -1)]
    total = _lcm(len(path), len(WAVE_TOP), 2 * len(WAVE_BOTTOM), 6)

    frames = []
    for k in range(total):
        x, direction = path[k % len(path)]
        bob = (k // 3) % 2  # Ente wippt im Wasser

        rows = [[(" ", "")] * width for _ in range(ROWS)]
        for i in range(width):
            rows[2][i] = (WAVE_TOP[(i + k) % len(WAVE_TOP)], CYAN)
            rows[3][i] = (WAVE_BOTTOM[(i - k // 2) % len(WAVE_BOTTOM)], BLUE)

        for r, line in enumerate(sprites[direction]):
            # nur Leerzeichen am Rand sind durchsichtig, im Inneren der Ente nicht
            start, end = len(line) - len(line.lstrip()), len(line.rstrip())
            for c in range(start, end):
                ch = line[c]
                rows[bob + r][x + c] = (ch, _cell_color(ch) if ch != " " else "")

        frames.append("".join(_render_row(row, color) + CLEAR_EOL + "\n" for row in rows))
    return tuple(frames)


def ansi_einschalten(stream=None) -> bool:
    """Schaltet unter Windows die ANSI-Darstellung der Konsole ein (ENABLE_VIRTUAL_TERMINAL_PROCESSING).
    True, wenn ANSI-Steuerzeichen sicher dargestellt werden."""
    if os.name != "nt":
        return True
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = k.GetStdHandle(-12 if stream is sys.stderr else -11)
        modus = ctypes.c_uint32()
        if not k.GetConsoleMode(h, ctypes.byref(modus)):
            return False
        if modus.value & 0x0004:
            return True
        return bool(k.SetConsoleMode(h, modus.value | 0x0004))
    except Exception:  # noqa: BLE001
        return False


class DuckSpinner:
    def __init__(self, text="Loading", width=32, fps=10, stream=None, color=None, done=None):
        self.text = text
        self.done = done
        self.stream = stream or sys.stdout
        try:
            tty = bool(self.stream and self.stream.isatty()) and os.environ.get("TERM") != "dumb"
        except (AttributeError, ValueError):
            tty = False
        self._animate = tty
        self._color = (tty and "NO_COLOR" not in os.environ) if color is None else color
        columns = shutil.get_terminal_size((80, 24)).columns
        self._width = max(14, min(width, columns - 1))
        self._interval = 1.0 / fps
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._thread = None
        self._drawn = False

    # -- Steuerung -----------------------------------------------------------
    def start(self):
        if self._thread is not None:
            return self
        if self._animate and not ansi_einschalten(self.stream):
            self._animate = self._color = False          # alte Konsole: lieber schlicht als Zeichensalat
        if not self._animate:
            self._schreibe(f"{self.text} ...\n")
            return self
        frames = build_frames(self._width, self._color)
        self._stop_event.clear()
        self._schreibe(HIDE_CURSOR)
        atexit.register(self._show_cursor)
        self._thread = threading.Thread(target=self._run, args=(frames,), daemon=True)
        self._thread.start()
        return self

    def zeile(self, text):
        """Gibt eine bleibende Zeile aus; die Animation läuft darunter weiter."""
        if not self._animate or self._thread is None:
            self._schreibe(text + "\n")
            return
        with self._lock:
            self._schreibe((f"\x1b[{ROWS + 1}F\x1b[J" if self._drawn else "") + text + "\n")
            self._drawn = False

    def stop(self, final_text=None):
        if self._thread is not None:
            self._stop_event.set()
            self._thread.join()
            self._thread = None
            with self._lock:
                self._schreibe((f"\x1b[{ROWS + 1}F\x1b[J" if self._drawn else "") + SHOW_CURSOR)  # Animation löschen
                self._drawn = False
            atexit.unregister(self._show_cursor)
        final_text = final_text or self.done
        if final_text:
            self._schreibe(final_text + "\n")

    def __enter__(self):
        return self.start()

    def __exit__(self, *exc):
        self.stop()
        return False

    # -- intern --------------------------------------------------------------
    def _schreibe(self, text):
        try:
            self.stream.write(text)
            self.stream.flush()
        except (OSError, ValueError, AttributeError):
            pass

    def _show_cursor(self):
        self._schreibe(SHOW_CURSOR)

    def _run(self, frames):
        up = f"\x1b[{ROWS + 1}F"
        count = len(frames)
        k = 0
        while True:
            dots = "." * ((k // 3) % 4)
            with self._lock:
                self._schreibe((up if self._drawn else "") + frames[k % count] + self.text + dots + CLEAR_EOL + "\n")
                self._drawn = True
            k += 1
            if self._stop_event.wait(self._interval):
                break


if __name__ == "__main__":
    with DuckSpinner("Lade Daten", done="Fertig!") as s:
        time.sleep(3)
        s.zeile("  ✓ Zwischenschritt erledigt")
        time.sleep(3)
