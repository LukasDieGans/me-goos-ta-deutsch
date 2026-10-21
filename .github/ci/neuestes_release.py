#!/usr/bin/env python3
"""Lädt das neueste veröffentlichte Release von Me Goos-ta Deutsch (seit 2.2, für die Release-Prüfung): ZIP und
SHA256SUMS.txt über die öffentlichen Adressen …/releases/latest/download/… (ohne Anmeldung, ohne API-Grenze), vergleicht
die Prüfsumme und entpackt mit den Unix-Rechten aus dem ZIP (Startdateien 0755). Nur Standardbibliothek.
    python neuestes_release.py [--ziel <Ordner>] [--repo <konto/repo>] [--passend <min>]
                                                                        → Zeile „#release {json}“, Exit-Code 0/1
--passend <min>  (Push auf main) höchstens so lange warten, bis das Release genau den Inhalt des Checkouts hat (jede Datei
                 gleich, keine fehlt oder ist zu viel; .github/ und .gitattributes gehören nur zum Branch) und die
                 Download-Seite seine Prüfsumme nennt – main wird vor dem Release-Asset und der Seite gepusht.
Konto/Repository: --repo, sonst GITHUB_REPOSITORY (GitHub Actions), sonst Programm/web_adresse.txt im Checkout."""
import hashlib
import json
import os
import re
import shutil
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


def abweichungen(zip_pfad, wurzel, ohne=()):
    """Release-ZIP gegen den Checkout: → Liste der Unterschiede (leer = gleicher Inhalt). Im Checkout zählen .git/,
    .github/, .gitattributes und die Ordner in `ohne` (z. B. das Ziel zum Entpacken) nicht mit."""
    wurzel = Path(wurzel).resolve()
    weg = [Path(o).resolve() for o in ohne]
    hier = {}
    for p in wurzel.rglob("*"):
        rel = p.relative_to(wurzel)
        if (not p.is_file() or rel.parts[0] in (".git", ".github") or rel.as_posix() == ".gitattributes"
                or any(p.resolve().is_relative_to(w) for w in weg)):
            continue
        hier[rel.as_posix()] = p
    aus = []
    with zipfile.ZipFile(zip_pfad) as z:
        drin = {i.filename[len("Me-Goos-ta-Deutsch/"):]: i for i in z.infolist()
                if not i.is_dir() and i.filename.startswith("Me-Goos-ta-Deutsch/")}
        for n in sorted(set(drin) | set(hier)):
            if n not in hier:
                aus.append(f"nur im Release: {n}")
            elif n not in drin:
                aus.append(f"nur auf main: {n}")
            elif z.read(drin[n]) != hier[n].read_bytes():
                aus.append(f"anders: {n}")
    return aus


def seite_nennt(wurzel, sha):
    """Nennt die Download-Seite (web_adresse.txt + download/) die Prüfsumme? Ohne Adresse: ja (nichts zu prüfen)."""
    pfad = Path(wurzel) / "Programm" / "web_adresse.txt"
    adresse = pfad.read_text(encoding="utf-8").strip().splitlines()[0].strip() if pfad.is_file() else ""
    if not adresse.startswith("https://"):
        return True
    return sha.encode("ascii") in holen(f"{adresse}download/?v={int(time.time())}")


def passend_laden(ziel, repo, wurzel, minuten):
    """Wie laden(), aber wartet (alle 60 s), bis das Release dem Checkout entspricht und die Download-Seite es nennt."""
    ende, grund = time.time() + minuten * 60, ""
    while True:
        shutil.rmtree(ziel, ignore_errors=True)
        try:
            r = laden(ziel, repo)
            unterschiede = abweichungen(Path(ziel) / r["name"], wurzel, ohne=[ziel])
            if unterschiede:
                grund = f"Release {r['version']} ≠ main ({len(unterschiede)}: {', '.join(unterschiede[:3])})"
            elif not seite_nennt(wurzel, r["sha256"]):
                grund = f"Download-Seite nennt SHA-256 {r['sha256'][:16]}… noch nicht"
            else:
                return r
        except (OSError, ValueError, KeyError, AttributeError) as f:
            grund = f"Release nicht geladen: {f}"
        if time.time() + 60 > ende:
            raise ValueError(f"nach {minuten:g} min nicht passend – {grund}")
        print(f"  … wartet: {grund}", flush=True)
        time.sleep(60)


def main(argv):
    def wert(n, standard=None):
        return argv[argv.index(n) + 1] if n in argv and argv.index(n) + 1 < len(argv) else standard
    wurzel = Path(__file__).resolve().parents[2]
    t0, r, grund = time.time(), None, ""
    passend = wert("--passend")
    try:
        if passend:
            r = passend_laden(wert("--ziel", "release"), repo_von(wurzel, wert("--repo")), wurzel, float(passend))
        else:
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
        if passend:
            name += " · Inhalt = main, Download-Seite nennt die Prüfsumme"
        Path(wert("--ergebnis")).write_text(json.dumps(dict(
            system="release", ok=bool(r), version=r and r["version"], release=r, pruefungen=[dict(
                name=name, ok=bool(r), grund=grund[:600], dauer=round(time.time() - t0, 1))]), ensure_ascii=False, indent=1),
            encoding="utf-8")
    return 0 if r else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
