#!/usr/bin/env python3
"""CI-Bau (seit 2.5 G05): baut im Checkout des Quellbaums Release-Ordner, ZIP und Web-App genau wie werkstatt/ci_lauf.py
lokal (bau_release.py + --zip, bau_webapp.py --ohne-modelle --release-zip) und legt den Testbaum – Release-Inhalt +
.github/ + web-app/ + .gitattributes, dasselbe Layout wie bisher der Branch ci – als baum.tar ab. tar, weil Artefakte
die Unix-Rechte verlieren (Startdateien 0755). ergebnis.json trägt die Inhalts-Prüfsumme des Release-Ordners;
ci_lauf.py vergleicht sie mit der lokalen (Release-Schranke ci_ergebnis.json).
Aufruf: python .github/ci/bau.py --ergebnis ergebnis.json --tar baum.tar [--cache <Ordner für Pyodide-Downloads>]
Nur Standardbibliothek + die Programm-Pakete (Pillow/NumPy für Symbole und Modelle der Web-App, aus pakete.lock)."""
import json
import shutil
import sys
import tarfile
import tempfile
import time
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[2]                     # Checkout des Quellbaums
sys.path.insert(0, str(WURZEL / "werkstatt"))
sys.dont_write_bytecode = True
AUSFUEHRBAR = (".command", ".sh")


def wert(argv, name, standard=None):
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else standard


def tar_bauen(baum, ziel):
    """baum/ → ziel (Pfade „baum/…“); Startdateien oben 0755, sonst 0644 – unabhängig vom Dateisystem des Runners."""
    def rechte(info):
        oben = info.name.count("/") == 1
        info.mode = 0o755 if info.isdir() or (oben and info.name.endswith(AUSFUEHRBAR)) else 0o644
        info.uid = info.gid = 0
        info.uname = info.gname = ""
        return info
    with tarfile.open(ziel, "w", format=tarfile.PAX_FORMAT) as t:
        t.add(baum, arcname="baum", filter=rechte)


def main(argv):
    ergebnis = Path(wert(argv, "--ergebnis", "ergebnis.json"))
    tar = Path(wert(argv, "--tar", "baum.tar"))
    cache = wert(argv, "--cache")
    pruefungen, t0 = [], time.time()
    aus = dict(system="bau", ok=False, pruefungen=pruefungen)
    tmp = Path(tempfile.mkdtemp(prefix="mgd-bau-"))
    try:
        import ci_lauf                                          # werkstatt/ci_lauf.py: derselbe Bau wie lokal
        p, baum = ci_lauf.plan(WURZEL / "Me-Goos-ta-Deutsch", tmp, cache=cache)
        pruefungen.append(dict(name="Release-Ordner, ZIP und Web-App gebaut", ok=p["web_app"] >= 10,
                               grund=f"{p['dateien']} Dateien, web-app {p['web_app']} ({p['web_app_version']})"))
        tar_bauen(baum, tar)
        with tarfile.open(tar) as t:
            namen = {m.name: m for m in t.getmembers()}
        start = [m for n, m in namen.items() if n.count("/") == 1 and n.endswith(AUSFUEHRBAR)]
        pruefungen.append(dict(name="baum.tar mit Release, .github/ci, web-app und ausführbaren Startdateien",
                               ok=all(f"baum/{x}" in namen for x in ("Programm/starter.py", ".github/ci/frischtest.py",
                                                                    "web-app/sw.js", ".gitattributes"))
                               and len(start) == 2 and all(m.mode == 0o755 for m in start),
                               grund=f"{len(namen)} Einträge, Startdateien {[oct(m.mode) for m in start]}"))
        aus.update(pruefsumme=p["pruefsumme"], version=p["version"], dateien=p["dateien"],
                   web_app_version=p["web_app_version"])
    except SystemExit as e:                                     # abbruch() aus ci_lauf
        pruefungen.append(dict(name="Bau", ok=False, grund=str(e.code)[-500:]))
    except Exception as e:  # noqa: BLE001 – jeder Fehler landet im Ergebnis
        pruefungen.append(dict(name="Bau", ok=False, grund=f"{type(e).__name__}: {e}"[-500:]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    aus["ok"] = bool(pruefungen) and all(x["ok"] for x in pruefungen)
    aus["dauer"] = round(time.time() - t0)
    ergebnis.write_text(json.dumps(aus, ensure_ascii=False, indent=1), encoding="utf-8")
    for x in pruefungen:
        print(f"{'✓' if x['ok'] else '✗'} {x['name']} · {x['grund']}")
    print(f"Prüfsumme {aus.get('pruefsumme', '–')}")
    return 0 if aus["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
