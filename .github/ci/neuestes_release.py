#!/usr/bin/env python3
"""Lädt das neueste veröffentlichte Release von Me Goos-ta Deutsch (seit 2.2, für den wöchentlichen Lauf): ZIP und
SHA256SUMS.txt über die öffentlichen Adressen …/releases/latest/download/… (ohne Anmeldung, ohne API-Grenze), vergleicht
die Prüfsumme und entpackt mit den Unix-Rechten aus dem ZIP (Startdateien 0755). Nur Standardbibliothek.
    python neuestes_release.py [--ziel <Ordner>] [--repo <konto/repo>]   → Zeile „#release {json}“, Exit-Code 0/1
Konto/Repository: --repo, sonst GITHUB_REPOSITORY (GitHub Actions), sonst Programm/web_adresse.txt im Checkout."""
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ZIP_NAME = re.compile(r"^([0-9a-f]{64})  (Me-Goos-ta-Deutsch-(\d+(?:\.\d+)+)\.zip)$", re.M)


def holen(url, versuche=3):
    for i in range(versuche):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "me-goos-ta-deutsch-ci"}),
                                        timeout=300) as r:
                return r.read()
        except (urllib.error.URLError, OSError):
            if i == versuche - 1:
                raise
            time.sleep(4 * (i + 1))


def repo_von(wurzel, repo=None):
    if repo or os.environ.get("GITHUB_REPOSITORY"):
        return repo or os.environ["GITHUB_REPOSITORY"]
    zeile = (Path(wurzel) / "Programm" / "web_adresse.txt").read_text(encoding="utf-8").strip().splitlines()[0]
    m = re.match(r"^https://([a-z0-9-]+)\.github\.io/([A-Za-z0-9._-]+)/$", zeile.strip())
    return f"{m.group(1)}/{m.group(2)}"


def laden(ziel, repo):
    """→ dict(ordner, version, name, sha256, groesse, adresse). Wirft ValueError, wenn die Prüfsumme nicht stimmt."""
    basis = f"https://github.com/{repo}/releases/latest/download/"
    summen = holen(basis + "SHA256SUMS.txt").decode("utf-8")
    m = ZIP_NAME.search(summen)
    if not m:
        raise ValueError(f"SHA256SUMS.txt ohne Zeile „<sha>  Me-Goos-ta-Deutsch-<Version>.zip“: {summen[:200]!r}")
    sha, name, version = m.groups()
    daten = holen(basis + name)
    ist = hashlib.sha256(daten).hexdigest()
    if ist != sha:
        raise ValueError(f"Prüfsumme stimmt nicht: {name} hat {ist}, SHA256SUMS.txt nennt {sha}")
    ziel = Path(ziel)
    ziel.mkdir(parents=True, exist_ok=True)
    (ziel / name).write_bytes(daten)
    with zipfile.ZipFile(ziel / name) as z:
        for info in z.infolist():
            pfad = ziel / info.filename
            if not pfad.resolve().is_relative_to(ziel.resolve()):
                raise ValueError(f"unerwarteter Pfad im ZIP: {info.filename}")
            z.extract(info, ziel)
            rechte = (info.external_attr >> 16) & 0o777
            if rechte and not info.is_dir() and os.name != "nt":
                os.chmod(pfad, rechte)
    ordner = ziel / "Me-Goos-ta-Deutsch"
    if not (ordner / "Programm" / "gans_lernkarten.py").is_file():
        raise ValueError(f"Kein Release-Ordner im ZIP: {ordner}")
    return dict(ordner=str(ordner), version=version, name=name, sha256=sha, groesse=len(daten), adresse=basis + name)


def main(argv):
    def wert(n, standard=None):
        return argv[argv.index(n) + 1] if n in argv and argv.index(n) + 1 < len(argv) else standard
    wurzel = Path(__file__).resolve().parents[2]
    t0, r, grund = time.time(), None, ""
    try:
        r = laden(wert("--ziel", "release"), repo_von(wurzel, wert("--repo")))
    except (OSError, ValueError, KeyError, AttributeError) as f:
        grund = f"Release nicht geladen: {f}"
        print(f"✗ {grund}", flush=True)
    if r:
        print(f"✓ Release {r['version']} geladen: {r['name']} ({r['groesse'] / 1e6:.1f} MB), SHA-256 {r['sha256'][:16]}… "
              "= SHA256SUMS.txt", flush=True)
        print("#release " + json.dumps(r, ensure_ascii=False), flush=True)
    if wert("--ergebnis"):                                      # wie frischtest.py: ergebnis.json für ci_lauf.py
        name = (f"Neuestes Release {r['version']} geladen, SHA-256 = SHA256SUMS.txt, entpackt mit Unix-Rechten" if r
                else "Neuestes Release laden und gegen SHA256SUMS.txt prüfen")
        Path(wert("--ergebnis")).write_text(json.dumps(dict(
            system="release", ok=bool(r), version=r and r["version"], release=r, pruefungen=[dict(
                name=name, ok=bool(r), grund=grund[:600], dauer=round(time.time() - t0, 1))]), ensure_ascii=False, indent=1),
            encoding="utf-8")
    return 0 if r else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
