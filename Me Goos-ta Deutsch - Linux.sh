#!/bin/sh
# ============================================================================
#  Me Goos-ta Deutsch – start for Linux                            Version 2.1
#
#  In a terminal:  sh "Me Goos-ta Deutsch - Linux.sh"
#  In the file manager: right-click → “Run as a program” (without a terminal
#  one opens, so you can watch the setup).
#
#  The real work is done by “Me Goos-ta Deutsch - Mac.command” – it handles
#  Mac and Linux. Both files must sit side by side.
#  MGD_KEIN_TERMINAL=1 starts without an extra terminal window.
#  Messages are in English; once a language is chosen in the program, they
#  follow that choice (German / English / Spanish).
# ============================================================================
ORDNER=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P) || exit 1
SELBST="$ORDNER/$(basename -- "$0")"
START="$ORDNER/Me Goos-ta Deutsch - Mac.command"

if [ ! -f "$START" ]; then
  SPR=en
  if grep -q '"sprache": "de"' "$ORDNER/Programm/ui_einstellungen.json" 2>/dev/null; then SPR=de
  elif grep -q '"sprache": "es"' "$ORDNER/Programm/ui_einstellungen.json" 2>/dev/null; then SPR=es; fi
  case "$SPR" in
    de) T="Die Datei „Me Goos-ta Deutsch - Mac.command“ fehlt. Bitte die ZIP-Datei noch einmal vollständig entpacken." ;;
    es) T="Falta el archivo «Me Goos-ta Deutsch - Mac.command». Descomprime otra vez todo el archivo ZIP." ;;
    *) T="The file “Me Goos-ta Deutsch - Mac.command” is missing. Please extract the whole ZIP file again." ;;
  esac
  printf '\n  ! %s\n' "$T"
  if [ ! -t 1 ] && command -v zenity >/dev/null 2>&1; then zenity --error --no-wrap --text "$T" 2>/dev/null; fi
  exit 1
fi

# Ohne Terminal (Doppelklick im Dateimanager): eines öffnen – gleiche Liste wie LINUX_TERMINALS in starter.py
if [ ! -t 1 ] && [ -z "$MGD_KEIN_TERMINAL" ]; then
  q() { printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"; }
  for t in x-terminal-emulator gnome-terminal ptyxis kgx konsole xfce4-terminal mate-terminal terminator alacritty kitty xterm; do
    command -v "$t" >/dev/null 2>&1 || continue
    case "$t" in
      gnome-terminal|ptyxis) exec "$t" -- sh "$SELBST" "$@" ;;
      kgx) exec "$t" -e "sh $(q "$SELBST")" ;;
      xfce4-terminal|mate-terminal|terminator) exec "$t" -x sh "$SELBST" "$@" ;;
      kitty) exec "$t" sh "$SELBST" "$@" ;;
      *) exec "$t" -e sh "$SELBST" "$@" ;;
    esac
  done
fi
exec sh "$START" "$@"
