#!/bin/sh
# ============================================================================
#  Me Goos-ta Deutsch – start for macOS                            Version 2.3
#
#  Just double-click. The first start sets everything up: a Python of its own
#  in your user folder (no administrator rights needed) and the packages
#  (tools only on request). Then the interface opens in the browser, and
#  “Me Goos-ta Deutsch” sits in the Applications folder (Launchpad).
#
#  Python: python-build-standalone (Astral, GitHub), SHA-256 is verified.
#  Location: ~/Library/Application Support/Me-Goos-ta-Deutsch/python
#  Everything else is done by Programm/starter.py.
#  Messages are in English; once a language is chosen in the program, they
#  follow that choice (German / English / Spanish).
#
#  Also runs on Linux:   sh "Me Goos-ta Deutsch - Mac.command"
#  If macOS refuses the double-click: open Terminal, type "sh ",
#  drag this file into the Terminal window, press Return.
# ============================================================================
PBS_TAG="20260924"
PY_VER="3.13.15"
SHA_aarch64_apple_darwin="064afb7c2fc0bbf511d886288adf98696af5105e36c138cdf2c199c0146fcf68"
SHA_x86_64_apple_darwin="327814efd865a0b6a99c149b12a261e9d0ad409183515c745d41bda2d07282e9"
SHA_aarch64_unknown_linux_gnu="5ad58156cbec94e5643c13caa792e92df72a23f33d3a6425d4cbff5c4b7a040c"
SHA_x86_64_unknown_linux_gnu="d0b640eed27fbdd6f5f2bd33444aee53df2c8863f8b2a96f4094717411e3de9c"

unset PYTHONHOME PYTHONPATH PYTHONSTARTUP
export PYTHONNOUSERSITE=1

# --- Sprache der Meldungen: Englisch, nach der ersten Wahl die im Programm gewählte (de / en / es) ---
SPR=en
EINST="$(dirname -- "$0")/Programm/ui_einstellungen.json"
if grep -q '"sprache": "de"' "$EINST" 2>/dev/null; then SPR=de
elif grep -q '"sprache": "es"' "$EINST" 2>/dev/null; then SPR=es; fi
case "$SPR" in
en)
  T_KOPF="Me Goos-ta Deutsch – printable flashcards"
  T_PY="First start: setting up Python (about 20 MB, no administrator rights needed) …"
  T_LADE="Downloading Python …"; T_PRUEFE="Checking the file …"; T_ENTPACKE="Unpacking Python …"; T_OK="Python is ready."
  T_ZIP="Please extract the ZIP file first (double-click it), then double-click “Me Goos-ta Deutsch - Mac” in the new folder."
  T_TCC="macOS does not allow access to this folder. Please answer “OK/Allow” when asked – or: System Settings → Privacy & Security → Files and Folders → allow Terminal. Then start again."
  T_SYSTEM="This system is not supported (only macOS and Linux on Intel/ARM)."
  T_ORDNER="This folder cannot be created or written:"
  T_NETZ="Python could not be downloaded – no internet connection? Internet is only needed on the first start. Please check the connection and start again."
  T_SUMME="The downloaded file is damaged (wrong checksum). Please start again."
  T_ENTPACKEN="Python could not be unpacked. Please start again."
  T_PYTHON="Python does not start on this computer."
  T_ENTER="Press Enter to close …" ;;
es)
  T_KOPF="Me Goos-ta Deutsch – tarjetas para imprimir"
  T_PY="Primer inicio: se instala Python (unos 20 MB, sin permisos de administrador) …"
  T_LADE="Descargando Python …"; T_PRUEFE="Revisando el archivo …"; T_ENTPACKE="Descomprimiendo Python …"; T_OK="Python está listo."
  T_ZIP="Primero descomprime el archivo ZIP (doble clic) y luego haz doble clic en «Me Goos-ta Deutsch - Mac» en la carpeta nueva."
  T_TCC="macOS no permite el acceso a esta carpeta. Responde «OK/Permitir» cuando lo pregunte, o: Configuración del Sistema → Privacidad y seguridad → Archivos y carpetas → permitir Terminal. Luego inicia otra vez."
  T_SYSTEM="Este sistema no es compatible (solo macOS y Linux en Intel/ARM)."
  T_ORDNER="No se puede crear o escribir esta carpeta:"
  T_NETZ="No se pudo descargar Python. ¿Hay internet? Solo el primer inicio lo necesita. Revisa la conexión e inicia otra vez."
  T_SUMME="El archivo descargado está dañado (suma de verificación incorrecta). Inicia otra vez."
  T_ENTPACKEN="No se pudo descomprimir Python. Inicia otra vez."
  T_PYTHON="Python no arranca en esta computadora."
  T_ENTER="Pulsa Intro para cerrar …" ;;
de)
  T_KOPF="Me Goos-ta Deutsch – Lernkarten zum Ausdrucken"
  T_PY="Erster Start: Python wird eingerichtet (ca. 20 MB, ohne Administratorrechte) …"
  T_LADE="Lade Python …"; T_PRUEFE="Prüfe die Datei …"; T_ENTPACKE="Entpacke Python …"; T_OK="Python ist bereit."
  T_ZIP="Bitte zuerst die ZIP-Datei entpacken (Doppelklick darauf) und dann im neuen Ordner „Me Goos-ta Deutsch - Mac“ doppelklicken."
  T_TCC="macOS erlaubt den Zugriff auf diesen Ordner nicht. Bitte bei der Rückfrage „OK/Erlauben“ wählen – oder: Systemeinstellungen → Datenschutz & Sicherheit → Dateien und Ordner → Terminal erlauben. Danach erneut starten."
  T_SYSTEM="Dieses System wird nicht unterstützt (nur macOS und Linux auf Intel/ARM)."
  T_ORDNER="Dieser Ordner kann nicht angelegt oder beschrieben werden:"
  T_NETZ="Python konnte nicht geladen werden – keine Internetverbindung? Internet wird nur beim ersten Start gebraucht. Bitte Verbindung prüfen und erneut starten."
  T_SUMME="Die geladene Datei ist beschädigt (Prüfsumme falsch). Bitte erneut starten."
  T_ENTPACKEN="Python konnte nicht entpackt werden. Bitte erneut starten."
  T_PYTHON="Python startet auf diesem Rechner nicht."
  T_ENTER="Zum Schließen die Eingabetaste drücken …" ;;
esac

fehler() {
  printf '\n  ! %s\n' "$@"
  if [ -t 0 ]; then printf '\n  %s ' "$T_ENTER"; read -r _; fi
  exit 1
}

pruefsumme() {
  if command -v shasum >/dev/null 2>&1; then LC_ALL=C shasum -a 256 "$1" | cut -d' ' -f1
  elif command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1
  else openssl dgst -sha256 "$1" | sed 's/.*= *//'
  fi
}

# --- Wo liegt das Programm? ---
ORDNER=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P) || fehler "$T_TCC"
PROGRAMM="$ORDNER/Programm"
ls "$ORDNER" >/dev/null 2>&1 || fehler "$T_TCC"
[ -f "$PROGRAMM/starter.py" ] || fehler "$T_ZIP"

case "$(uname -s)" in
  Darwin)
    BASIS="$HOME/Library/Application Support/Me-Goos-ta-Deutsch"; OS="apple-darwin"
    # Download-Quarantäne der eigenen Dateien entfernen (sonst fragt Gatekeeper bei jedem Start)
    xattr -dr com.apple.quarantine "$PROGRAMM" 2>/dev/null
    xattr -d com.apple.quarantine "$0" 2>/dev/null ;;
  Linux)
    BASIS="${XDG_DATA_HOME:-$HOME/.local/share}/me-goos-ta-deutsch"; OS="unknown-linux-gnu" ;;
  *) fehler "$T_SYSTEM" ;;
esac
ARCH=$(uname -m)
if [ "$OS" = apple-darwin ] && [ "$(sysctl -n hw.optional.arm64 2>/dev/null)" = 1 ]; then ARCH=aarch64; fi
case "$ARCH" in arm64|aarch64) ARCH=aarch64 ;; x86_64|amd64) ARCH=x86_64 ;; *) fehler "$T_SYSTEM" ;; esac
export MGD_DATEN="$BASIS"
PY="$BASIS/python/bin/python3"

# --- Erster Start: eigenes Python laden, prüfen, entpacken ---
if ! "$PY" -c 'import sys, ssl' >/dev/null 2>&1; then
  printf '\n  %s\n  %s\n\n' "$T_KOPF" "$T_PY"
  mkdir -p "$BASIS" 2>/dev/null || fehler "$T_ORDNER" "$BASIS"
  OS_VAR=$(printf '%s' "$OS" | tr '-' '_')
  eval "SOLL=\$SHA_${ARCH}_${OS_VAR}"
  NAME="cpython-$PY_VER+$PBS_TAG-$ARCH-$OS-install_only_stripped.tar.gz"
  URL="https://github.com/astral-sh/python-build-standalone/releases/download/$PBS_TAG/cpython-$PY_VER%2B$PBS_TAG-$ARCH-$OS-install_only_stripped.tar.gz"
  DATEI="$BASIS/$NAME"
  if [ ! -f "$DATEI" ] || [ "$(pruefsumme "$DATEI")" != "$SOLL" ]; then
    printf '  %s\n' "$T_LADE"
    rm -f "$DATEI.part"
    if command -v curl >/dev/null 2>&1; then
      curl -fL --retry 3 --retry-delay 3 --connect-timeout 30 --progress-bar -o "$DATEI.part" "$URL" \
        || { rm -f "$DATEI.part"; fehler "$T_NETZ"; }
    elif command -v wget >/dev/null 2>&1; then
      wget -q -O "$DATEI.part" "$URL" || { rm -f "$DATEI.part"; fehler "$T_NETZ"; }
    else
      fehler "$T_NETZ"
    fi
    mv -f "$DATEI.part" "$DATEI" || fehler "$T_ORDNER" "$BASIS"
  fi
  printf '  %s\n' "$T_PRUEFE"
  [ "$(pruefsumme "$DATEI")" = "$SOLL" ] || { rm -f "$DATEI"; fehler "$T_SUMME"; }
  printf '  %s\n' "$T_ENTPACKE"
  NEU="$BASIS/python-neu.$$"
  rm -rf "$NEU" && mkdir -p "$NEU" || fehler "$T_ORDNER" "$BASIS"
  tar -xzf "$DATEI" -C "$NEU" || { rm -rf "$NEU"; fehler "$T_ENTPACKEN"; }
  "$NEU/python/bin/python3" -c 'import sys, ssl' >/dev/null 2>&1 || { rm -rf "$NEU"; fehler "$T_PYTHON"; }
  rm -rf "$BASIS/python"
  mv "$NEU/python" "$BASIS/python" || fehler "$T_ORDNER" "$BASIS"
  rm -rf "$NEU" "$DATEI"
  printf '  %s\n' "$T_OK"
fi

# --- Start: starter.py erkennt den ersten Start und richtet den Rest ein ---
"$PY" "$PROGRAMM/starter.py" --konsole "$@"
RC=$?
if [ "$RC" -ne 0 ] && [ -t 0 ]; then printf '\n  %s ' "$T_ENTER"; read -r _; fi
exit "$RC"
