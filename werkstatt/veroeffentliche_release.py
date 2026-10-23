#!/usr/bin/env python3
"""Veröffentlicht ein Programm-Release von Me Goos-ta Deutsch auf GitHub (seit 2.1; seit 2.5 G06 aus einem signierten Tag).
Aufruf: python veroeffentliche_release.py <Release-Ordner Me-Goos-ta-Deutsch> <Me-Goos-ta-Deutsch-<Version>.zip>
                                          [--probe] [--ci-ergebnis <Datei>] [--ohne-ci "<Begründung>"]
                                          [--signatur-ordner <Ordner>] [--desktop-anmeldung]

--probe        ohne Netz und ohne Anmeldung: prüft Ordner, ZIP, CI-Schranke und Quellbaum und zeigt den ganzen Plan (Tag,
               Push, Assets, Prüfsummen, Reihenfolge, Hindernisse, Notizen) – Hindernisse brechen hier nicht ab
--ci-ergebnis  Ergebnis des CI-Laufs (Standard: ci_ergebnis.json im Arbeitsordner, geschrieben von ci_lauf.py)
--ohne-ci      Release ohne grünen CI-Lauf – nur mit Begründung (mind. 10 Zeichen); sie steht im Protokoll (Ausgabe,
               #plan), nie in den Release-Notizen
--signatur-ordner  Schlüsselordner von signiere_release.py (Standard %USERPROFILE%\\MGD-Signatur; Tests: eigener Ordner)
--desktop-anmeldung  ausnahmsweise mit der breiten Anmeldung von GitHub Desktop statt des Tokens MGD-Release-Token
--ersetzen     gibt es seit 2.5 nicht mehr: Releases sind unveränderlich, ein Fix wird eine neue Patch-Version (z. B. 2.5.1)

Voraussetzungen (vor jedem Netzverkehr, sonst Abbruch): Ordner = ZIP (jede Datei per CRC; .github/ im Ordner zählt nicht),
keine Nutzerdaten, Version = ZIP-Name; CI-Schranke (ci_ergebnis.json: grüner Lauf für genau diesen Release-Inhalt, gleiche
Inhalts-Prüfsumme wie ci_lauf.py); Quellbaum: Arbeitsbaum sauber, HEAD gültig signiert, Me-Goos-ta-Deutsch/ in HEAD = Release-
Ordner Datei für Datei, ein lokaler Tag v<Version> zeigt höchstens auf HEAD; Signatur: SHA256SUMS.txt wird mit dem Haupt-
Schlüssel signiert (signiere_release.py, minisign, „trusted comment“ me-goos-ta-deutsch v<Version>) und gegen
Programm/signatur.py des Release-Ordners geprüft; SHA256SUMS.txt + .minisig liegen danach neben der ZIP.
Ablauf: Anmeldung (veroeffentliche_webapp.token: GH_TOKEN → MGD-Release-Token; Rechte werden vorab gelesen) → gibt es
v<Version> schon veröffentlicht: Abbruch → signierter annotierter Tag v<Version> auf HEAD (git tag -s, Prüfung git tag -v)
→ ein atomarer Push: HEAD → main (nur Fast-Forward) + Tag – nie --force → Standard-Branch main, Beschreibung, Homepage =
Download-Seite → Release als Entwurf → ZIP, SHA256SUMS.txt, SHA256SUMS.txt.minisig hochladen → angemeldet laden und
vergleichen (Bytes + Signatur; sonst Entwurf löschen, Abbruch) → erst dann veröffentlichen („Latest“) → öffentlich laden und
vergleichen. Release-Notizen: Abschnitt „## [<Version>]“ aus CHANGELOG.md (sonst README „New in“), dazu Kurzanleitung
EN/DE/ES, SHA-256 und Signatur-Hinweis. Die Release-Prüfung (release_pruefung.yml) startet mit dem Veröffentlichen.
Konto und Repository stammen aus Programm/web_adresse.txt (https://<konto>.github.io/<repo>/). Handy-App und
Download-Seite (Branch gh-pages) veröffentlicht veroeffentliche_webapp.py."""
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import zlib
from pathlib import Path

HIER = Path(__file__).resolve().parent                          # werkstatt/ (seit 2.5 G04)
ARBEIT = HIER.parent                                            # Wurzel des Quellbaums (Arbeitsordner)
sys.path.insert(0, str(HIER))
import veroeffentliche_webapp as vw  # noqa: E402  Anmeldung, GitHub-API, git

QUELLE_GITHUB = ARBEIT / ".github"
CI_ERGEBNIS = ARBEIT / "ci_ergebnis.json"
PROJEKT = "Me-Goos-ta-Deutsch"

PFLICHT = ("Me Goos-ta Deutsch - Windows.cmd", "Me Goos-ta Deutsch - Mac.command", "Me Goos-ta Deutsch - Linux.sh",
           "LIES MICH ZUERST.html", "README.md", "LICENSE.txt", "Programm/gans_lernkarten.py", "Programm/web_adresse.txt")
AUSFUEHRBAR = ("Me Goos-ta Deutsch - Mac.command", "Me Goos-ta Deutsch - Linux.sh")
# was nie in ein öffentliches Repository gehört (eigene Karten, Bilder, Einstellungen, Lernstand, Zwischenspeicher)
NUTZERDATEN = re.compile(r"^Programm/(karten(\.bak)?\.csv|ideen\.json|ui_einstellungen\.json|tools\.json|uebersetzung(en)?\.json|"
                         r"lernstand[^/]*\.json|bilder/|ideen/|ausgabe/.|_beispiele/|assets/gans_hintergrund\.|assets/_alt/)"
                         r"|(^|/)__pycache__/|\.(pyc|bak|tmp)$")
ZIP_NAME = re.compile(r"^Me-Goos-ta-Deutsch-(\d+(?:\.\d+)+)\.zip$")
SUMMEN = "SHA256SUMS.txt"
SIGNATUR = SUMMEN + ".minisig"                                   # seit 2.5
MAX_DATEI = 5 * 1024 * 1024                                     # große Modelle lädt das Programm selbst
BESCHREIBUNG = ("Learn German with goose puns – picture flash cards to print and to study. Windows, macOS, Linux and a "
                "phone app. Free, offline, MIT.")
# Reihenfolge der Schritte (steht im Plan; E55 prüft sie gegen eine nachgebildete API)
REIHENFOLGE = ("tag", "push main + tag", "repo", "entwurf", "assets hochladen", "angemeldet pruefen", "veroeffentlichen",
               "oeffentlich pruefen")


def abbruch(text):
    sys.exit(f"✗ {text}")


def dateien(ordner):
    """Relative Pfade (posix) aller Dateien im Release-Ordner – ohne .github/ und .gitattributes (gehören nur zu den Branches)."""
    return sorted(n for n in (p.relative_to(ordner).as_posix() for p in ordner.rglob("*") if p.is_file())
                  if not n.startswith(".github/") and n != ".gitattributes")


def inhalt_pruefsumme(ordner, liste):
    """SHA-256 über alle Dateien (Pfad + Inhalt) – dieselbe Rechnung wie ci_lauf.inhalt_pruefsumme (E39 prüft das)."""
    h = hashlib.sha256()
    for n in liste:
        h.update(n.encode("utf-8") + b"\0")
        h.update(hashlib.sha256((ordner / n).read_bytes()).digest())
    return h.hexdigest()


def github_dateien():
    """Pfade unter .github/ des Quellbaums (Workflows, Test-Skripte) – kommen mit dem Quellbaum auf main, nie ins ZIP."""
    if not (QUELLE_GITHUB / "workflows").is_dir():
        abbruch(f".github/workflows fehlt: {QUELLE_GITHUB}")
    return sorted(".github/" + q.relative_to(QUELLE_GITHUB).as_posix() for q in QUELLE_GITHUB.rglob("*")
                  if q.is_file() and "__pycache__" not in q.parts and q.suffix != ".pyc")


def ci_schranke(ordner, liste, version, pfad, ohne_ci):
    """Release nur mit grünem CI-Lauf für genau diesen Inhalt. → Angaben für Plan/Protokoll; sonst Abbruch."""
    summe = inhalt_pruefsumme(ordner, liste)
    if ohne_ci is not None:
        if len(ohne_ci.strip()) < 10:
            abbruch("--ohne-ci braucht eine Begründung (mindestens 10 Zeichen), z. B. --ohne-ci \"GitHub Actions gestört, lokal geprüft\".")
        print(f"Achtung: Release ohne grünen CI-Lauf – Begründung: {ohne_ci.strip()}")
        return dict(ohne=ohne_ci.strip(), pruefsumme=summe)
    try:
        e = json.loads(Path(pfad).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        abbruch(f"CI-Schranke: kein CI-Ergebnis ({pfad}) – erst „python ci_lauf.py“ laufen lassen (bzw. --ohne-ci \"<Grund>\").")
    if not e.get("ok"):
        abbruch(f"CI-Schranke: letzter CI-Lauf nicht grün ({e.get('lauf')}) – Funde beheben, ci_lauf.py erneut.")
    if e.get("pruefsumme") != summe or e.get("version") != version:
        abbruch(f"CI-Schranke: der grüne CI-Lauf gilt für einen anderen Inhalt (Version {e.get('version')}, Prüfsumme "
                f"{str(e.get('pruefsumme'))[:12]}… statt {version}, {summe[:12]}…) – ci_lauf.py für diesen Stand laufen lassen.")
    systeme = e.get("systeme") or {}
    if not systeme or not all(s.get("ok") for s in systeme.values()):
        abbruch("CI-Schranke: nicht alle Systeme grün in ci_ergebnis.json.")
    print(f"✓ CI-Schranke: grüner Lauf für genau diesen Inhalt ({len(systeme)} Systeme, {e.get('zeit')}, {e.get('lauf')})")
    return dict(lauf=e.get("lauf"), zeit=e.get("zeit"), systeme=sorted(systeme), pruefsumme=summe)


def pruefen(ordner, zip_pfad):
    """Prüft Release-Ordner und ZIP; liefert (Version, ZIP-Bytes, Dateiliste, Konto, Repo)."""
    if not ordner.is_dir():
        abbruch(f"Release-Ordner fehlt: {ordner}")
    fehlt = [n for n in PFLICHT if not (ordner / n).is_file()]
    if fehlt:
        abbruch(f"Kein Release-Ordner (es fehlt {', '.join(fehlt)}): {ordner}")
    liste = dateien(ordner)
    privat = [n for n in liste if NUTZERDATEN.search(n)]
    gross = [n for n in liste if (ordner / n).stat().st_size > MAX_DATEI]
    if privat or gross:
        abbruch("Im Release-Ordner liegen Dinge, die nicht öffentlich gehören: " + ", ".join((privat + gross)[:8])
                + " – bitte mit bau_release.py neu bauen.")
    m = ZIP_NAME.match(zip_pfad.name)
    if not zip_pfad.is_file() or not m:
        abbruch(f"ZIP fehlt oder heißt nicht Me-Goos-ta-Deutsch-<Version>.zip: {zip_pfad}")
    version = m.group(1)
    v = re.search(r'^VERSION = "([\d.]+)', (ordner / "Programm" / "gans_lernkarten.py").read_text(encoding="utf-8"), re.M)
    if not v or v.group(1) != version:
        abbruch(f"Version passt nicht: ZIP {version}, Programm {v.group(1) if v else '?'}")
    daten = zip_pfad.read_bytes()
    with zipfile.ZipFile(zip_pfad) as z:
        im_zip = {i.filename.split("/", 1)[1]: i for i in z.infolist() if not i.is_dir() and "/" in i.filename}
    anders = sorted(set(im_zip) ^ set(liste))
    anders += [n for n in liste if n in im_zip and im_zip[n].CRC != zlib.crc32((ordner / n).read_bytes())]
    if anders:
        abbruch("ZIP und Release-Ordner passen nicht zusammen: " + ", ".join(anders[:8]))
    zeilen = (ordner / "Programm" / "web_adresse.txt").read_text(encoding="utf-8").strip().splitlines()
    adr = re.match(r"^https://([a-z0-9-]+)\.github\.io/([A-Za-z0-9._-]+)/$", zeilen[0].strip() if zeilen else "")
    if not adr:
        abbruch("Programm/web_adresse.txt nennt keine GitHub-Pages-Adresse (https://<konto>.github.io/<repo>/).")
    return version, daten, liste, adr.group(1), adr.group(2)


def _git(wurzel, *args, env=None):
    return subprocess.run([vw.git_exe(), *args], cwd=wurzel, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env or dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never"))


def git_blob(daten):
    """SHA-1 eines git-Blobs (Bytes 1:1 – .gitattributes `* -text`)."""
    return hashlib.sha1(b"blob %d\0" % len(daten) + daten).hexdigest()


def quellbaum_stand(ordner, liste, version, wurzel=ARBEIT):
    """Release kommt aus dem Quellbaum: Arbeitsbaum sauber, HEAD gültig signiert, Me-Goos-ta-Deutsch/ in HEAD = Release-
    Ordner (jede Datei, keine fehlt/zu viel), lokaler Tag v<V> fehlt oder zeigt auf HEAD. → dict(head, hindernisse, …)"""
    if not (Path(wurzel) / ".git").exists():
        return dict(head=None, tag_lokal=False, hindernisse=[f"kein Git-Quellbaum in {wurzel} (quellbaum.py --einrichten)"])
    hindernisse = []
    head = _git(wurzel, "rev-parse", "HEAD").stdout.strip()
    offen = [z[3:] for z in _git(wurzel, "status", "--porcelain").stdout.splitlines() if z.strip()]
    if offen:
        hindernisse.append(f"Arbeitsbaum nicht sauber ({len(offen)}: {', '.join(offen[:4])}) – erst quellbaum.py --commit")
    if _git(wurzel, "verify-commit", "HEAD").returncode:
        hindernisse.append(f"HEAD {head[:10]} nicht gültig signiert (quellbaum.py --commit signiert)")
    baum = {}
    for z in _git(wurzel, "ls-tree", "-r", "-z", "HEAD", "--", f"{PROJEKT}/").stdout.split("\0"):
        if "\t" in z:
            meta, pfad = z.split("\t", 1)
            baum[pfad[len(PROJEKT) + 1:]] = meta.split()[2]
    anders = sorted(set(baum) ^ set(liste)) + [n for n in liste if n in baum and baum[n] != git_blob((ordner / n).read_bytes())]
    if anders:
        hindernisse.append(f"Release-Ordner ≠ {PROJEKT}/ in HEAD ({len(anders)}: {', '.join(anders[:4])}) – Release aus "
                           "genau diesem Commit bauen")
    t = _git(wurzel, "rev-parse", "-q", "--verify", f"refs/tags/v{version}^{{commit}}")
    tag_lokal = t.stdout.strip() if t.returncode == 0 else None
    if tag_lokal and tag_lokal != head:
        hindernisse.append(f"Tag v{version} zeigt lokal auf {tag_lokal[:10]}, nicht auf HEAD – Tags werden nie verschoben "
                           "(Fix = neue Patch-Version)")
    return dict(head=head, tag_lokal=bool(tag_lokal), dateien=len(baum), hindernisse=hindernisse)


def tag_und_pushen(wurzel, remote, head, version, env, nachricht):
    """Signierter annotierter Tag v<V> auf HEAD (legt ihn an, falls er fehlt), dann ein atomarer Push: HEAD → main (nur
    Fast-Forward) + Tag – nie --force. Liegt derselbe Tag schon auf dem Server (abgebrochener Lauf), nur main nachziehen.
    → (Tag-Objekt-SHA, gepusht: Liste der Refs)."""
    tag = f"v{version}"

    def g(*args, netz=False, pruefen=True):
        r = _git(wurzel, *args, env=env if netz else None)
        if pruefen and r.returncode:
            abbruch(f"git {args[0]} fehlgeschlagen: {(r.stderr or r.stdout)[-600:]}"
                    + (" – Token-Rechte Contents + Workflows (Read and write)?" if args[0] == "push" else ""))
        return r
    da = g("rev-parse", "-q", "--verify", f"refs/tags/{tag}^{{commit}}", pruefen=False)
    if da.returncode:
        g("tag", "-s", "-a", tag, "-m", nachricht, head)
    elif da.stdout.strip() != head:
        abbruch(f"Tag {tag} zeigt lokal nicht auf HEAD – Tags werden nie verschoben (Fix = neue Patch-Version).")
    if g("cat-file", "-t", f"refs/tags/{tag}").stdout.strip() != "tag":
        abbruch(f"Tag {tag} ist nicht annotiert (leichter Tag) – nicht veröffentlicht.")
    if g("tag", "-v", tag, pruefen=False).returncode:
        abbruch(f"Signatur von Tag {tag} nicht prüfbar (quellbaum.py --einrichten, Signaturschlüssel?) – nichts gepusht.")
    objekt = g("rev-parse", f"refs/tags/{tag}").stdout.strip()
    refs = {}
    for z in g("ls-remote", remote, "refs/heads/main", f"refs/tags/{tag}", netz=True).stdout.splitlines():
        if "\t" in z:
            sha, ref = z.split("\t", 1)
            refs[ref] = sha
    ziele = []
    if f"refs/tags/{tag}" in refs:
        if refs[f"refs/tags/{tag}"] != objekt:
            abbruch(f"Tag {tag} gibt es auf GitHub schon (anderer Stand) – Releases sind unveränderlich; Fix = neue Patch-Version.")
    else:
        ziele.append(f"refs/tags/{tag}:refs/tags/{tag}")
    alt = refs.get("refs/heads/main")
    if alt != head:
        if alt:
            if g("cat-file", "-e", f"{alt}^{{commit}}", pruefen=False).returncode:
                g("fetch", "-q", remote, "main", netz=True)
            if g("merge-base", "--is-ancestor", alt, head, pruefen=False).returncode:
                abbruch(f"main auf GitHub ({alt[:10]}) ist kein Vorgänger von HEAD – nur Fast-Forward, nie Force.")
        ziele.insert(0, f"{head}:refs/heads/main")
    if ziele:
        g("push", "--atomic", "-q", remote, *ziele, netz=True)
    return objekt, [z.split(":", 1)[1] for z in ziele]


def signatur_modul(ordner):
    """Programm/signatur.py des Release-Ordners (seine SCHLUESSEL prüfen die nächsten Updates), sonst die des
    Arbeitsordners (Releases vor 2.5)."""
    for pfad in (ordner / "Programm" / "signatur.py", ARBEIT / PROJEKT / "Programm" / "signatur.py"):
        if pfad.is_file():
            spec = importlib.util.spec_from_file_location(f"signatur_{abs(hash(str(pfad)))}", pfad)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    abbruch("Programm/signatur.py fehlt – ohne Signatur kein Release (seit 2.5).")


def signatur_plan(ordner, signatur_ordner):
    """Für Plan/Probe: welcher Schlüssel signieren wird (nur der öffentliche Teil wird gelesen) und ob er vertraut ist."""
    import signiere_release as sr
    mod = signatur_modul(ordner)
    o = Path(signatur_ordner)
    pub = sr.oeffentlich(o, "haupt")
    if not pub or not (o / "haupt.dpapi").is_file():
        return dict(fehlt=f"kein Haupt-Schlüssel in {o}")
    vertraute = {sid for _, sid, _ in mod.vertraut()}
    return dict(schluessel=mod.schluessel_id(pub[0]), vertraut=pub[0] in vertraute)


def signieren(ordner, version, summen, signatur_ordner):
    """Signiert SHA256SUMS (Pflicht) und prüft gegen signatur.py des Release-Ordners → (minisig, Schlüssel-ID)."""
    import signiere_release as sr
    ms, sid = sr.signieren(summen, version, signatur_ordner)
    mod = signatur_modul(ordner)
    try:
        mod.pruefe(summen, ms, None, mod.KOMMENTAR.format(version=version))
    except ValueError as f:
        abbruch(f"Signatur mit Schlüssel {sid} passt nicht zu Programm/signatur.py des Releases ({f}) – Schlüssel nicht "
                "vertraut; nichts veröffentlicht.")
    return ms, sid


def changelog_abschnitt(ordner, version):
    """Abschnitt „## [<Version>] …“ aus CHANGELOG.md (Keep a Changelog, seit 2.5 G07) – Zeilen unverändert, ohne Überschrift."""
    pfad = ordner / "CHANGELOG.md"
    if not pfad.is_file():
        return ""
    m = re.search(rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|^\[[^\]]+\]: |\Z)", pfad.read_text(encoding="utf-8"),
                  re.M | re.S)
    return m.group(1).strip() if m else ""


def notizen(ordner, version, zip_name, sha, seite):
    """Release-Notizen: Englisch (Abschnitt aus CHANGELOG.md, sonst „New in …“ aus der README), kurz Deutsch und Spanisch."""
    neu = changelog_abschnitt(ordner, version)
    if not neu:
        readme = (ordner / "README.md").read_text(encoding="utf-8")
        m = re.search(rf"^## New in {re.escape(version)}[ \t]*\n(.*?)(?=^## |\Z)", readme, re.M | re.S)
        neu = " ".join(m.group(1).split()) if m else ""
    zeilen = [f"## Me Goos-ta Deutsch {version} 🪿", "",
              "Learn German with goose puns – picture flash cards to print and to study. "
              "**One package for Windows, macOS and Linux.**", ""]
    if neu:
        zeilen += [f"### New in {version}", "", neu, ""]
    zeilen += ["### Get started", "",
               f"1. Download **{zip_name}** below – or use the friendly download page: {seite}",
               "2. Windows 11: right-click the ZIP → Properties → tick “Unblock” → OK. Then extract it.",
               "3. Double-click the start file for your system. The first start sets everything up by itself "
               "(3–10 minutes, about 90 MB, no administrator rights).", "",
               "Already using version 2.4 or later? Tools → “Keep the program up to date” installs the new version right in "
               "the program, in the same folder. From older versions: extract the new one into a new folder and start it "
               "there – it offers to take over your cards, pictures and learning progress.", "",
               "**Deutsch:** Ein Paket für Windows, macOS und Linux: ZIP laden (Windows 11: Eigenschaften → „Zulassen“), "
               f"entpacken, Startdatei doppelklicken – die Gans richtet alles selbst ein. Anleitung mit Bildern: {seite}#de", "",
               "**Español:** Un solo paquete para Windows, macOS y Linux: descarga el ZIP (Windows 11: Propiedades → "
               "«Desbloquear»), descomprímelo y haz doble clic en el archivo de inicio; el ganso instala todo solo. Guía con "
               f"imágenes: {seite}#es", "",
               f"SHA-256 of `{zip_name}`: `{sha}` (also in `{SUMMEN}`)", ""]
    if (ordner / "Programm" / "signatur.py").is_file():
        mod = signatur_modul(ordner)
        haupt = next((k for k in mod.vertraut() if k[0] == "haupt"), None)
        if haupt:
            zeilen += [f"**Verify the signature (optional):** `{SUMMEN}` is signed with the Me Goos-ta Deutsch key "
                       f"(minisign, key ID `{mod.schluessel_id(haupt[1])}`): `minisign -Vm {SUMMEN} -P "
                       f"{mod.schluessel_text(haupt[1], haupt[2])}` – then compare the SHA-256 of the ZIP. The program checks "
                       "this signature by itself before every update. The tag is signed, the release is immutable.", ""]
    zeilen += ["MIT License · © Eine Gans namens Lukas · Have fun learning – you’re doing great!"]
    return "\n".join(zeilen) + "\n"


def plan(ordner, zip_pfad, ci_pfad=CI_ERGEBNIS, ohne_ci=None, signatur_ordner=None, wurzel=ARBEIT):
    import signiere_release as sr
    version, daten, liste, konto, repo = pruefen(ordner, zip_pfad)
    ci = ci_schranke(ordner, liste, version, ci_pfad, ohne_ci)
    sig = signatur_plan(ordner, signatur_ordner or sr.STANDARD_ORDNER)
    qb = quellbaum_stand(ordner, liste, version, wurzel)
    sha = hashlib.sha256(daten).hexdigest()
    seite = f"https://{konto}.github.io/{repo}/download/"
    hindernisse = list(qb["hindernisse"])
    if sig.get("fehlt") or not sig.get("vertraut", True):
        grund = sig.get("fehlt") or f"Haupt-Schlüssel {sig.get('schluessel')} nicht vertraut (nicht in Programm/signatur.py)"
        hindernisse.append(f"Signatur: {grund}")
    return dict(version=version, konto=konto, repo=repo, branch="main", tag=f"v{version}", ci=ci, github=github_dateien(),
                titel=f"Me Goos-ta Deutsch {version}", assets=[zip_pfad.name, SUMMEN, SIGNATUR], signatur=sig,
                groesse=len(daten), sha256=sha, quellbaum=qb, hindernisse=hindernisse, reihenfolge=list(REIHENFOLGE),
                summen=f"{sha}  {zip_pfad.name}\n", dateien=len(liste), ausfuehrbar=list(AUSFUEHRBAR), latest=True,
                unveraenderlich=True, push=dict(main="nur Fast-Forward", tag="signiert, annotiert", force=False),
                download=f"https://github.com/{konto}/{repo}/releases/download/v{version}/{zip_pfad.name}", seite=seite,
                notizen=notizen(ordner, version, zip_pfad.name, sha, seite)), daten


def zeige(p, probe):
    print(("Plan (Probe – ohne Netz, nichts wird verändert):" if probe else "Plan:"))
    q = p["quellbaum"]
    print(f"  Repository   {p['konto']}/{p['repo']} · main ← HEAD {str(q.get('head'))[:10]} des Quellbaums (nur Fast-Forward, "
          f"nie Force; {PROJEKT}/ = Release-Ordner, {p['dateien']} Dateien) · Standard-Branch main")
    print(f"  Tag          {p['tag']} signiert + annotiert" + (" (liegt lokal schon auf HEAD)" if q.get("tag_lokal") else "")
          + " · ein atomarer Push main + Tag")
    print(f"  .github/     {len(p['github'])} Dateien kommen mit dem Quellbaum (nicht im ZIP)")
    print("  CI           " + (f"ohne grünen Lauf – Begründung: {p['ci']['ohne']}" if p["ci"].get("ohne")
                              else f"grün: {p['ci']['lauf']} ({len(p['ci']['systeme'])} Systeme)"))
    print(f"  Release      {p['titel']} · Entwurf → hochladen → angemeldet prüfen → veröffentlichen (Latest) → öffentlich "
          "prüfen · danach unveränderlich")
    print(f"  Assets       {p['assets'][0]} ({p['groesse'] / 1e6:.1f} MB) · {p['assets'][1]} · {p['assets'][2]}")
    s = p["signatur"]
    print("  Signatur     " + (f"fehlt ({s['fehlt']})" if s.get("fehlt") else
                              f"Schlüssel {s['schluessel']}" + ("" if s["vertraut"] else " – nicht in signatur.py")))
    print(f"  SHA-256      {p['sha256']}")
    print(f"  Download     {p['download']}")
    print(f"  Seite        {p['seite']}")
    for h in p["hindernisse"]:
        print(f"  Hindernis    {h}" + (" (Veröffentlichen bricht hier ab)" if probe else ""))
    print("#plan " + json.dumps({k: v for k, v in p.items() if k != "notizen"}, ensure_ascii=False))
    if probe:
        print("\n--- " + SUMMEN + " ---\n" + p["summen"] + "--- Release-Notizen ---\n" + p["notizen"])


class _OhneWeiterleitung(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):              # Weiterleitung selbst folgen – ohne Anmeldung
        return None


class GitHub:
    """Die Schritte am Release über die API (E55 ersetzt die Klasse durch eine Nachbildung)."""

    def __init__(self, tok, weg):
        self.tok, self.weg = tok, weg

    def api(self, methode, rest, daten=None):
        return vw.api(methode, self.weg + rest, self.tok, daten)

    def hochladen(self, release, name, daten, typ):
        url = release["upload_url"].split("{", 1)[0] + "?name=" + urllib.parse.quote(name)
        req = urllib.request.Request(url, data=daten, method="POST", headers={
            "Authorization": f"Bearer {self.tok}", "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28", "Content-Type": typ, "User-Agent": "me-goos-ta-deutsch"})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as f:
            abbruch(f"Hochladen von {name} fehlgeschlagen: {f.code} {f.read().decode('utf-8', 'replace')[:300]}")

    def asset(self, asset):
        """Asset eines (Entwurfs-)Releases angemeldet laden; der Weiterleitung zum Speicher ohne Anmeldung folgen."""
        req = urllib.request.Request(asset["url"], headers={
            "Authorization": f"Bearer {self.tok}", "Accept": "application/octet-stream",
            "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "me-goos-ta-deutsch"})
        try:
            with urllib.request.build_opener(_OhneWeiterleitung).open(req, timeout=300) as r:
                return r.read()
        except urllib.error.HTTPError as f:
            ziel = f.headers.get("Location") if f.code in (301, 302, 303, 307, 308) else None
            if not ziel:
                return None
        except (urllib.error.URLError, OSError):
            return None
        return self.oeffentlich(ziel, 3)

    def oeffentlich(self, url, versuche=12):
        """Öffentliche Adresse ohne Anmeldung laden (folgt der Weiterleitung zum Speicher von GitHub)."""
        for _ in range(versuche):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "me-goos-ta-deutsch"}),
                                            timeout=300) as r:
                    return r.read()
            except (urllib.error.URLError, OSError):
                time.sleep(10)
        return None


def _echt(mod, summen, minisig, version):
    try:
        return bool(mod.pruefe(summen, minisig, None, mod.KOMMENTAR.format(version=version)))
    except (ValueError, TypeError):
        return False


def release_schritte(gh, p, daten, minisig, mod):
    """Entwurf → Assets hochladen → angemeldet laden und prüfen → veröffentlichen („Latest“) → öffentlich prüfen.
    Stimmt vor dem Veröffentlichen etwas nicht, wird der Entwurf gelöscht (Tag bleibt, ein neuer Lauf macht weiter)."""
    summen = p["summen"].encode("utf-8")
    soll = {p["assets"][0]: (daten, "application/zip"), SUMMEN: (summen, "text/plain"),
            SIGNATUR: (minisig, "application/octet-stream")}
    s, release = gh.api("POST", "/releases", dict(tag_name=p["tag"], name=p["titel"], body=p["notizen"], draft=True,
                                                  prerelease=False))
    if s != 201:
        abbruch(f"Release-Entwurf anlegen fehlgeschlagen: {s} {release.get('message', '')}")
    print(f"✓ Entwurf {p['titel']} angelegt")
    hoch = {name: gh.hochladen(release, name, d, typ) for name, (d, typ) in soll.items()}
    print(f"✓ Assets hochgeladen: {', '.join(hoch)}")
    zurueck = {name: gh.asset(a) for name, a in hoch.items()}
    falsch = [n for n in soll if zurueck.get(n) != soll[n][0]]
    if not falsch and not _echt(mod, zurueck[SUMMEN], zurueck[SIGNATUR], p["version"]):
        falsch.append("Signatur")
    if falsch:
        gh.api("DELETE", f"/releases/{release['id']}")
        abbruch(f"Entwurf geprüft: {', '.join(falsch)} stimmt nicht – Entwurf gelöscht, nichts veröffentlicht.")
    print("✓ Entwurf angemeldet geladen und geprüft (Bytes + Signatur)")
    s, release = gh.api("PATCH", f"/releases/{release['id']}", dict(draft=False, make_latest="true"))
    if s != 200:
        abbruch(f"Release veröffentlichen fehlgeschlagen: {s} {release.get('message', '')}")
    print(f"✓ Release veröffentlicht (unveränderlich): {release.get('html_url')}")
    basis = p["download"].rsplit("/", 1)[0] + "/"
    oeff = {n: gh.oeffentlich(basis + n, 12 if n == p["assets"][0] else 3) for n in soll}
    falsch = [n for n in soll if oeff.get(n) != soll[n][0]]
    if not falsch and not _echt(mod, oeff[SUMMEN], oeff[SIGNATUR], p["version"]):
        falsch.append("Signatur")
    if falsch:
        abbruch(f"Achtung: Release {p['tag']} ist veröffentlicht, aber öffentlich geladen stimmt {', '.join(falsch)} nicht – "
                "sofort von Hand prüfen; Releases sind unveränderlich, ein Fix wird eine neue Patch-Version.")
    print(f"✓ öffentlich geladen und geprüft: SHA-256 {p['sha256'][:16]}… stimmt, Signatur gültig")
    return release


def veroeffentlichen(ordner, zip_pfad, ci_pfad=CI_ERGEBNIS, ohne_ci=None, signatur_ordner=None):
    import signiere_release as sr
    p, daten = plan(ordner, zip_pfad, ci_pfad, ohne_ci, signatur_ordner)
    zeige(p, False)
    if p["hindernisse"]:
        abbruch("Nicht veröffentlicht – erst beheben: " + " · ".join(p["hindernisse"]))
    minisig, sid = signieren(ordner, p["version"], p["summen"].encode("utf-8"), signatur_ordner or sr.STANDARD_ORDNER)
    (zip_pfad.parent / SUMMEN).write_bytes(p["summen"].encode("utf-8"))      # für bau_webapp.py --release-zip
    (zip_pfad.parent / SIGNATUR).write_bytes(minisig)
    print(f"✓ {SUMMEN} signiert (Schlüssel {sid}, vertraut laut Programm/signatur.py)")
    tok, woher = vw.token()
    s, ich = vw.api("GET", "/user", tok)
    if s != 200:
        abbruch(f"Anmeldung ({woher}) abgelehnt: {s} {ich.get('message', '')}")
    konto, repo, tag = ich["login"], p["repo"], p["tag"]
    if konto.lower() != p["konto"]:
        abbruch(f"Angemeldet als {konto}, web_adresse.txt gehört zu {p['konto']} – bitte mit dem richtigen Konto anmelden.")
    print(f"Konto {konto} (Anmeldung: {woher})")
    vw.rechte_pruefen(tok, konto, repo, ("contents", "administration"))
    gh = GitHub(tok, f"/repos/{konto}/{repo}")
    s, liste = gh.api("GET", "/releases?per_page=30")
    for r in liste if s == 200 and isinstance(liste, list) else []:
        if r.get("tag_name") == tag and not r.get("draft"):
            abbruch(f"Release {tag} ist schon veröffentlicht ({r.get('html_url')}) – unveränderlich; Fix = neue Patch-Version.")
        if r.get("tag_name") == tag:
            gh.api("DELETE", f"/releases/{r['id']}")              # liegengebliebener Entwurf eines abgebrochenen Laufs
            print(f"= alter Entwurf {tag} gelöscht")
    objekt, gepusht = tag_und_pushen(ARBEIT, f"https://github.com/{konto}/{repo}.git", p["quellbaum"]["head"], p["version"],
                                     vw.git_umgebung(tok, ich), p["titel"])
    print(f"✓ Tag {tag} signiert ({objekt[:10]}) · gepusht: {', '.join(gepusht) or 'nichts (schon da)'}")
    s, r = gh.api("PATCH", "", dict(default_branch="main", homepage=p["seite"], description=BESCHREIBUNG))
    if s != 200:
        abbruch(f"Standard-Branch/Beschreibung setzen fehlgeschlagen: {s} {r.get('message', '')} – Token-Recht Administration?")
    print("✓ Standard-Branch main · Homepage = Download-Seite")
    release_schritte(gh, p, daten, minisig, signatur_modul(ordner))
    print(f"✓ fertig: {p['download']}\n  Seite: {p['seite']} (mit bau_webapp.py --release-zip bauen, veroeffentliche_webapp.py)")


def main(argv):
    if "--ersetzen" in argv:
        abbruch("--ersetzen gibt es seit 2.5 nicht mehr: veröffentlichte Releases und Tags sind unveränderlich – ein Fix "
                "wird eine neue Patch-Version (z. B. 2.5.1).")
    werte = {}
    pos, i = [], 0
    while i < len(argv):
        if argv[i] in ("--ci-ergebnis", "--ohne-ci", "--signatur-ordner") and i + 1 < len(argv):
            werte[argv[i]], i = argv[i + 1], i + 2
            continue
        if argv[i] == "--ohne-ci":
            werte[argv[i]], i = "", i + 1                       # ohne Text → Abbruch mit Hinweis
            continue
        if not argv[i].startswith("--"):
            pos.append(argv[i])
        i += 1
    if len(pos) != 2:
        sys.exit(__doc__)
    ordner, zip_pfad = Path(pos[0]).resolve(), Path(pos[1]).resolve()
    ci_pfad = Path(werte.get("--ci-ergebnis") or CI_ERGEBNIS).resolve()
    sig_ordner = Path(werte["--signatur-ordner"]).resolve() if werte.get("--signatur-ordner") else None
    if "--probe" in argv:
        zeige(plan(ordner, zip_pfad, ci_pfad, werte.get("--ohne-ci"), sig_ordner)[0], True)
    else:
        veroeffentlichen(ordner, zip_pfad, ci_pfad, werte.get("--ohne-ci"), sig_ordner)


if __name__ == "__main__":
    main(sys.argv[1:])
