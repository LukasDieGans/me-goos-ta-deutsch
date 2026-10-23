#!/usr/bin/env python3
"""Lädt das neueste veröffentlichte Release von Me Goos-ta Deutsch (seit 2.2, für die Release-Prüfung): ZIP und
SHA256SUMS.txt über die öffentlichen Adressen …/releases/latest/download/… (ohne Anmeldung, ohne API-Grenze), prüft ab
2.5 die Signatur SHA256SUMS.txt.minisig (Schlüssel aus Programm/signatur.py des Checkouts, „trusted comment“ = Version;
2.4 und älter: nur Prüfsumme, mit Hinweis), vergleicht die Prüfsumme und entpackt mit den Unix-Rechten aus dem ZIP
(Startdateien 0755). Nur Standardbibliothek.
    python neuestes_release.py [--ziel <Ordner>] [--repo <konto/repo>] [--passend <min>]
                                                                        → Zeile „#release {json}“, Exit-Code 0/1
--passend <min>  (Release veröffentlicht) höchstens so lange warten, bis das Release genau den Inhalt des Checkouts hat
                 (jede Datei gleich, keine fehlt oder ist zu viel; .github/, .gitattributes, __pycache__ zählen nicht) und
                 die Download-Seite seine Prüfsumme nennt – die Seite erscheint erst nach dem Release.
Checkout: seit 2.5 G06 der Quellbaum im Tag (Programm unter Me-Goos-ta-Deutsch/), bei der Probe auf ci der gebaute
Release-Baum (Programm an der Wurzel) – programm_wurzel() findet beides.
Konto/Repository: --repo, sonst GITHUB_REPOSITORY (GitHub Actions), sonst Programm/web_adresse.txt im Checkout."""
import hashlib
import importlib.util
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

sys.dont_write_bytecode = True                                  # signatur.py laden legt kein __pycache__ in den Checkout
ZIP_NAME = re.compile(r"^([0-9a-f]{64})  (Me-Goos-ta-Deutsch-(\d+(?:\.\d+)+)\.zip)$", re.M)


def holen(url, versuche=3):
    for i in range(versuche):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "me-goos-ta-deutsch-ci"}),
                                        timeout=300) as r:
                return r.read()
        except urllib.error.HTTPError as f:
            if f.code == 404 or i == versuche - 1:                  # fehlt wirklich – nicht dreimal fragen
                raise
            time.sleep(4 * (i + 1))
        except (urllib.error.URLError, OSError):
            if i == versuche - 1:
                raise
            time.sleep(4 * (i + 1))


def programm_wurzel(wurzel):
    """Ordner mit Programm/ im Checkout: Quellbaum (Me-Goos-ta-Deutsch/Programm, seit 2.5) oder Release-Baum (Programm)."""
    w = Path(wurzel)
    return w / "Me-Goos-ta-Deutsch" if (w / "Me-Goos-ta-Deutsch" / "Programm").is_dir() else w


def repo_von(wurzel, repo=None):
    if repo or os.environ.get("GITHUB_REPOSITORY"):
        return repo or os.environ["GITHUB_REPOSITORY"]
    zeile = (programm_wurzel(wurzel) / "Programm" / "web_adresse.txt").read_text(encoding="utf-8").strip().splitlines()[0]
    m = re.match(r"^https://([a-z0-9-]+)\.github\.io/([A-Za-z0-9._-]+)/$", zeile.strip())
    return f"{m.group(1)}/{m.group(2)}"


def signatur_modul(wurzel):
    pfad = programm_wurzel(wurzel) / "Programm" / "signatur.py"
    if not pfad.is_file():
        return None
    spec = importlib.util.spec_from_file_location("signatur_checkout", pfad)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def signatur_pruefen(basis, summen, version, wurzel):
    """Ab 2.5 Pflicht: SHA256SUMS.txt.minisig gültig für genau diese Version. → Text fürs Protokoll; sonst ValueError."""
    ab_25 = tuple(int(x) for x in version.split(".")) >= (2, 5)
    try:
        ms = holen(basis + "SHA256SUMS.txt.minisig")
    except urllib.error.HTTPError as f:
        if f.code == 404 and not ab_25:
            return "ohne Signatur (Release vor 2.5 – nur Prüfsumme)"
        raise ValueError(f"SHA256SUMS.txt.minisig fehlt (HTTP {f.code}) – ab 2.5 ist die Signatur Pflicht") from None
    mod = signatur_modul(wurzel) if wurzel else None
    if mod is None:
        if ab_25:
            raise ValueError("Programm/signatur.py fehlt im Checkout – Signatur nicht prüfbar")
        return "Signatur nicht geprüft (Checkout ohne Programm/signatur.py)"
    try:
        r = mod.pruefe(summen, ms, None, mod.KOMMENTAR.format(version=version))
    except ValueError as f:
        raise ValueError(f"Signatur von SHA256SUMS.txt ungültig ({f})") from None
    return f"Signatur gültig (Schlüssel {r['id']}, „{r['kommentar']}“)"


def laden(ziel, repo, wurzel=None):
    """→ dict(ordner, version, name, sha256, groesse, adresse, signatur). Wirft ValueError, wenn Signatur (ab 2.5) oder
    Prüfsumme nicht stimmen."""
    basis = f"https://github.com/{repo}/releases/latest/download/"
    summen_roh = holen(basis + "SHA256SUMS.txt")
    summen = summen_roh.decode("utf-8")
    m = ZIP_NAME.search(summen)
    if not m:
        raise ValueError(f"SHA256SUMS.txt ohne Zeile „<sha>  Me-Goos-ta-Deutsch-<Version>.zip“: {summen[:200]!r}")
    sha, name, version = m.groups()
    sig = signatur_pruefen(basis, summen_roh, version, wurzel)
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
    return dict(ordner=str(ordner), version=version, name=name, sha256=sha, groesse=len(daten), adresse=basis + name,
                signatur=sig)


def abweichungen(zip_pfad, wurzel, ohne=()):
    """Release-ZIP gegen den Checkout: → Liste der Unterschiede (leer = gleicher Inhalt). Im Checkout zählen .git/,
    .github/, .gitattributes und die Ordner in `ohne` (z. B. das Ziel zum Entpacken) nicht mit."""
    wurzel = programm_wurzel(Path(wurzel).resolve())
    weg = [Path(o).resolve() for o in ohne]
    hier = {}
    for p in wurzel.rglob("*"):
        rel = p.relative_to(wurzel)
        if (not p.is_file() or rel.parts[0] in (".git", ".github") or rel.as_posix() == ".gitattributes"
                or "__pycache__" in rel.parts or any(p.resolve().is_relative_to(w) for w in weg)):
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
                aus.append(f"nur im Checkout: {n}")
            elif z.read(drin[n]) != hier[n].read_bytes():
                aus.append(f"anders: {n}")
    return aus


def seite_nennt(wurzel, sha):
    """Nennt die Download-Seite (web_adresse.txt + download/) die Prüfsumme? Ohne Adresse: ja (nichts zu prüfen)."""
    pfad = programm_wurzel(wurzel) / "Programm" / "web_adresse.txt"
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
            r = laden(ziel, repo, wurzel)
            unterschiede = abweichungen(Path(ziel) / r["name"], wurzel, ohne=[ziel])
            if unterschiede:
                grund = f"Release {r['version']} ≠ Checkout ({len(unterschiede)}: {', '.join(unterschiede[:3])})"
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
            r = laden(wert("--ziel", "release"), repo_von(wurzel, wert("--repo")), wurzel)
    except (OSError, ValueError, KeyError, AttributeError) as f:
        grund = f"Release nicht geladen: {f}"
        print(f"✗ {grund}", flush=True)
    if r:
        print(f"✓ Release {r['version']} geladen: {r['name']} ({r['groesse'] / 1e6:.1f} MB), SHA-256 {r['sha256'][:16]}… "
              f"= SHA256SUMS.txt · {r['signatur']}", flush=True)
        print("#release " + json.dumps(r, ensure_ascii=False), flush=True)
    if wert("--ergebnis"):                                      # wie frischtest.py: ergebnis.json für ci_lauf.py
        name = (f"Neuestes Release {r['version']} geladen, {r['signatur']}, SHA-256 = SHA256SUMS.txt, entpackt mit Unix-Rechten"
                if r else "Neuestes Release laden, Signatur (ab 2.5) und SHA256SUMS.txt prüfen")
        if passend:
            name += " · Inhalt = Checkout (Tag), Download-Seite nennt die Prüfsumme"
        Path(wert("--ergebnis")).write_text(json.dumps(dict(
            system="release", ok=bool(r), version=r and r["version"], release=r, pruefungen=[dict(
                name=name, ok=bool(r), grund=grund[:600], dauer=round(time.time() - t0, 1))]), ensure_ascii=False, indent=1),
            encoding="utf-8")
    return 0 if r else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
