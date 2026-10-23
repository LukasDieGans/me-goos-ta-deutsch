"""Probe-Server auf einer frischen Kopie (nichts Echtes wird berührt). Aufruf: python probe_server.py <Programm> <Arbeitsordner> <port>
Schreibt die Start-Adresse nach <Arbeitsordner>/adresse.txt und läuft, bis der Prozess beendet wird."""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

QUELLE, ARBEIT, PORT = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), sys.argv[3]
sys.path.insert(0, str(QUELLE))
import test_gans_lernkarten as tg  # noqa: E402

if (ARBEIT / "projekt").exists():
    shutil.rmtree(ARBEIT / "projekt")
p = tg.kopiere_projekt(ARBEIT / "projekt")
for f in QUELLE.glob("*.py"):
    if not (p / f.name).exists():
        shutil.copy2(f, p / f.name)
for name in ("web_adresse.txt", "DRITTLIZENZEN.md"):                      # Adresse der Handy-App (seit G14)
    if (QUELLE / name).exists():
        shutil.copy2(QUELLE / name, p / name)
for name in ("Me Goos-ta Deutsch - Linux.sh", "Me Goos-ta Deutsch - Android.html", "Me Goos-ta Deutsch - iPhone.html",
             "Me Goos-ta Deutsch - Google Pixel.html"):
    if (QUELLE.parent / name).exists():
        shutil.copy2(QUELLE.parent / name, p.parent / name)
(ARBEIT / "daten").mkdir(parents=True, exist_ok=True)
env = dict(os.environ, PYTHONIOENCODING="utf-8", MGD_DATEN=str(ARBEIT / "daten"), MGD_START_ID="probe")
proc = subprocess.Popen([sys.executable, "-u", str(p / "gans_ui.py"), "--kein-browser", "--port", PORT], cwd=p, env=env,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
for zeile in proc.stdout:
    m = re.search(r"http://127\.0\.0\.1:\d+/\?k=[A-Za-z0-9_-]+", zeile)
    if m:
        (ARBEIT / "adresse.txt").write_text(m.group(0), encoding="utf-8")
        print(m.group(0), flush=True)
proc.wait()
