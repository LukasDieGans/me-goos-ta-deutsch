#!/usr/bin/env python3
"""Veröffentlicht ein Programm-Release von Me Goos-ta Deutsch auf GitHub (seit 2.1).
Aufruf: python veroeffentliche_release.py <Release-Ordner Me-Goos-ta-Deutsch> <Me-Goos-ta-Deutsch-<Version>.zip>
                                          [--probe] [--ersetzen] [--ci-ergebnis <Datei>] [--ohne-ci "<Begründung>"]
                                          [--signatur-ordner <Ordner>]

--probe        ohne Netz und ohne Anmeldung: prüft Ordner, ZIP und CI-Schranke und zeigt den Plan (Tag, Assets,
               Prüfsummen, .github/, Notizen)
--ersetzen     ein vorhandenes Release bzw. einen vorhandenen Tag v<Version> ändern – sonst wird nichts überschrieben
--ci-ergebnis  Ergebnis des CI-Laufs (Standard: ci_ergebnis.json neben diesem Skript, geschrieben von ci_lauf.py)
--ohne-ci      Release ohne grünen CI-Lauf – nur mit Begründung (mind. 10 Zeichen); sie steht im Protokoll (Ausgabe,
               #plan), nie in den Release-Notizen
--signatur-ordner  Schlüsselordner von signiere_release.py (Standard %USERPROFILE%\MGD-Signatur; Tests: eigener Ordner)

Signatur (seit 2.5, Pflicht): SHA256SUMS.txt wird mit dem Haupt-Schlüssel signiert (signiere_release.py, minisign-Format,
„trusted comment“ me-goos-ta-deutsch v<Version>) und gegen die Schlüssel in Programm/signatur.py des Release-Ordners
geprüft – ohne Schlüssel oder mit einem fremden Abbruch vor jedem Netzverkehr. Asset SHA256SUMS.txt.minisig; beide
Dateien liegen danach auch neben der ZIP (für bau_webapp.py --release-zip). --probe liest nur den öffentlichen Schlüssel.

CI-Schranke (seit 2.2): ci_ergebnis.json muss einen grünen Lauf (alle Systeme + Browser) für **genau diesen**
Release-Inhalt haben – gleiche Inhalts-Prüfsumme wie ci_lauf.py, gleiche Version –, sonst Abbruch vor jedem Netzverkehr.
Ablauf: Ordner + ZIP prüfen (gleicher Inhalt, keine Nutzerdaten, Version passt; ein .github/ im Ordner zählt nicht mit) →
CI-Schranke → Anmeldung wie veroeffentliche_webapp.py (GH_TOKEN → GitHub CLI → GitHub Desktop; der Schlüssel wird nie
ausgegeben) → Branch main = Release-Ordner + .github/ des Quellbaums (Workflow release_pruefung.yml: prüft das Release nach jedem Push auf main; nie im ZIP) pushen
(Verlauf bleibt, Bytes 1:1, .command/.sh ausführbar, noreply-Adresse) → main als Standard-Branch, Beschreibung, Homepage =
Download-Seite → Release als Entwurf anlegen, ZIP + SHA256SUMS.txt + SHA256SUMS.txt.minisig hochladen, veröffentlichen
(„Latest“) → Assets über die öffentliche Adresse laden, SHA-256 vergleichen und Signatur prüfen (stimmt es nicht, wird das
Release wieder Entwurf).
Konto und Repository stammen aus Programm/web_adresse.txt (https://<konto>.github.io/<repo>/). Handy-App und
Download-Seite (Branch gh-pages) bleiben unberührt – die veröffentlicht veroeffentliche_webapp.py."""
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
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

QUELLE_GITHUB = ARBEIT / ".github"                              # → .github/ im Branch main (nie im ZIP)
CI_ERGEBNIS = ARBEIT / "ci_ergebnis.json"

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
    """{Pfad unter .github/: Quelldatei} aus .github/ des Quellbaums (Workflows + Test-Skripte für die Release-Prüfung)."""
    if not (QUELLE_GITHUB / "workflows").is_dir():
        abbruch(f".github/workflows fehlt: {QUELLE_GITHUB}")
    return {".github/" + q.relative_to(QUELLE_GITHUB).as_posix(): q for q in sorted(QUELLE_GITHUB.rglob("*"))
            if q.is_file() and "__pycache__" not in q.parts and q.suffix != ".pyc"}


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


def signatur_modul(ordner):
    """Programm/signatur.py des Release-Ordners (seine SCHLUESSEL prüfen die nächsten Updates), sonst die des
    Arbeitsordners (Releases vor 2.5)."""
    for pfad in (ordner / "Programm" / "signatur.py", ARBEIT / "Me-Goos-ta-Deutsch" / "Programm" / "signatur.py"):
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


def notizen(ordner, version, zip_name, sha, seite):
    """Release-Notizen: Englisch (mit „New in …“ aus der README), kurz Deutsch und Spanisch."""
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
                       "this signature by itself before every update.", ""]
    zeilen += [
               "MIT License · © Eine Gans namens Lukas · Have fun learning – you’re doing great!"]
    return "\n".join(zeilen) + "\n"


def plan(ordner, zip_pfad, ci_pfad=CI_ERGEBNIS, ohne_ci=None, signatur_ordner=None):
    import signiere_release as sr
    version, daten, liste, konto, repo = pruefen(ordner, zip_pfad)
    ci = ci_schranke(ordner, liste, version, ci_pfad, ohne_ci)
    sig = signatur_plan(ordner, signatur_ordner or sr.STANDARD_ORDNER)
    sha = hashlib.sha256(daten).hexdigest()
    seite = f"https://{konto}.github.io/{repo}/download/"
    github = sorted(github_dateien())
    return dict(version=version, konto=konto, repo=repo, branch="main", tag=f"v{version}", ci=ci, github=github,
                titel=f"Me Goos-ta Deutsch {version}", assets=[zip_pfad.name, SUMMEN, SIGNATUR], signatur=sig,
                groesse=len(daten), sha256=sha,
                summen=f"{sha}  {zip_pfad.name}\n", dateien=len(liste) + 1 + len(github), ausfuehrbar=list(AUSFUEHRBAR), latest=True,
                download=f"https://github.com/{konto}/{repo}/releases/download/v{version}/{zip_pfad.name}", seite=seite,
                notizen=notizen(ordner, version, zip_pfad.name, sha, seite)), daten


def zeige(p, probe):
    print(("Plan (Probe – ohne Netz, nichts wird verändert):" if probe else "Plan:"))
    print(f"  Repository   {p['konto']}/{p['repo']} · Branch main ← Release-Ordner + .github/ ({p['dateien']} Dateien inkl. "
          f".gitattributes; ausführbar: {', '.join(p['ausfuehrbar'])}) · Standard-Branch main")
    print(f"  .github/     {', '.join(n[len('.github/'):] for n in p['github'])} (nicht im ZIP)")
    print("  CI           " + (f"ohne grünen Lauf – Begründung: {p['ci']['ohne']}" if p["ci"].get("ohne")
                              else f"grün: {p['ci']['lauf']} ({len(p['ci']['systeme'])} Systeme)"))
    print(f"  Release      {p['titel']} · Tag {p['tag']} · Latest")
    print(f"  Assets       {p['assets'][0]} ({p['groesse'] / 1e6:.1f} MB) · {p['assets'][1]} · {p['assets'][2]}")
    s = p["signatur"]
    print("  Signatur     " + (f"fehlt ({s['fehlt']}) – Veröffentlichen bricht ab" if s.get("fehlt") else
                              f"Schlüssel {s['schluessel']}" + ("" if s["vertraut"] else " – nicht in signatur.py: Veröffentlichen bricht ab")))
    print(f"  SHA-256      {p['sha256']}")
    print(f"  Download     {p['download']}")
    print(f"  Seite        {p['seite']}")
    print("#plan " + json.dumps({k: v for k, v in p.items() if k != "notizen"}, ensure_ascii=False))
    if probe:
        print("\n--- " + SUMMEN + " ---\n" + p["summen"] + "--- Release-Notizen ---\n" + p["notizen"])


def hochladen(tok, release, name, daten, typ):
    url = release["upload_url"].split("{", 1)[0] + "?name=" + urllib.parse.quote(name)
    req = urllib.request.Request(url, data=daten, method="POST", headers={
        "Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": typ, "User-Agent": "me-goos-ta-deutsch"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as f:
        abbruch(f"Hochladen von {name} fehlgeschlagen: {f.code} {f.read().decode('utf-8', 'replace')[:300]}")


def laden(url, versuche=12):
    """Öffentliche Adresse ohne Anmeldung laden (folgt der Weiterleitung zum Speicher von GitHub)."""
    for i in range(versuche):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "me-goos-ta-deutsch"}), timeout=300) as r:
                return r.read()
        except (urllib.error.URLError, OSError):
            time.sleep(10)
    return None


def main_pushen(git, env, url, ordner, liste, version, nachricht=None, nur_github=False):
    """Branch main = Release-Ordner (Verlauf bleibt). Liefert (Commit, ob etwas neu war).
    nur_github: nur .github/ nachziehen (Tag/Release bleiben) – Abbruch vor dem Push, wenn sich sonst etwas ändern würde."""
    arbeit = Path(tempfile.mkdtemp(prefix="mgd-main-"))

    def g(*args, pruefen=True):
        r = subprocess.run([git, *args], cwd=arbeit, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if pruefen and r.returncode:
            abbruch(f"git {args[0]} fehlgeschlagen: {(r.stderr or r.stdout)[-800:]}")
        return r
    try:
        g("init", "-q", "-b", "main")
        g("remote", "add", "origin", url)
        if g("fetch", "-q", "--depth", "1", "origin", "main", pruefen=False).returncode == 0:
            g("update-ref", "refs/heads/main", "FETCH_HEAD")       # Index leer → Release ersetzt alles, Verlauf bleibt
        for n in liste:
            z = arbeit / n
            z.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ordner / n, z)
        for n, q in github_dateien().items():                   # Workflows (Release-Prüfung) + Test-Skripte
            z = arbeit / n
            z.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(q, z)
        (arbeit / ".gitattributes").write_bytes(b"* -text\n")    # nie Zeilenenden umschreiben (.cmd CRLF, .sh LF)
        g("add", "-A")
        g("update-index", "--chmod=+x", "--", *AUSFUEHRBAR)
        neu = g("diff", "--cached", "--quiet", pruefen=False).returncode != 0
        if nur_github:
            fremd = [n for n in g("diff", "--cached", "--name-only").stdout.splitlines() if not n.startswith(".github/")]
            if fremd:
                abbruch(f"nur .github/ sollte sich ändern, aber auch: {', '.join(fremd[:5])}")
        if neu:
            g("commit", "-q", "-m", nachricht or f"Me Goos-ta Deutsch {version}")
            g("push", "-q", "origin", "main")
        return g("rev-parse", "HEAD").stdout.strip(), neu
    finally:
        shutil.rmtree(arbeit, ignore_errors=True)


def veroeffentlichen(ordner, zip_pfad, ersetzen, ci_pfad=CI_ERGEBNIS, ohne_ci=None, signatur_ordner=None):
    import signiere_release as sr
    p, daten = plan(ordner, zip_pfad, ci_pfad, ohne_ci, signatur_ordner)
    zeige(p, False)
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
    weg = f"/repos/{konto}/{repo}"
    s, r = vw.api("GET", weg, tok)
    if s == 404:
        s, r = vw.api("POST", "/user/repos", tok, dict(name=repo, private=False, auto_init=False, has_issues=True,
                                                     has_wiki=False, has_projects=False, homepage=p["seite"],
                                                     description=BESCHREIBUNG))
        if s != 201:
            abbruch(f"Repository anlegen fehlgeschlagen: {s} {r.get('message', '')}")
        print("✓ Repository angelegt (öffentlich)")
    elif s != 200:
        abbruch(f"Repository nicht lesbar: {s} {r.get('message', '')}")
    s, release = vw.api("GET", f"{weg}/releases/tags/{tag}", tok)
    release = release if s == 200 else None
    s, ref = vw.api("GET", f"{weg}/git/ref/tags/{tag}", tok)
    tag_sha = ref.get("object", {}).get("sha") if s == 200 else None
    if (release or tag_sha) and not ersetzen:
        abbruch(f"{'Release' if release else 'Tag'} {tag} gibt es schon – zum Ändern --ersetzen angeben "
                f"({release['html_url'] if release else 'github.com/' + konto + '/' + repo + '/tags'}).")
    commit, neu = main_pushen(vw.git_exe(), vw.git_umgebung(tok, ich), f"https://github.com/{konto}/{repo}.git", ordner,
                              dateien(ordner), p["version"])
    print(f"✓ main {'gepusht' if neu else 'unverändert'} ({commit[:10]})")
    s, r = vw.api("PATCH", weg, tok, dict(default_branch="main", homepage=p["seite"], description=BESCHREIBUNG))
    if s != 200:
        abbruch(f"Standard-Branch/Beschreibung setzen fehlgeschlagen: {s} {r.get('message', '')}")
    print("✓ Standard-Branch main · Homepage = Download-Seite")
    if tag_sha and tag_sha != commit:                             # nur mit --ersetzen (oben geprüft)
        s, r = vw.api("PATCH", f"{weg}/git/refs/tags/{tag}", tok, dict(sha=commit, force=True))
        if s != 200:
            abbruch(f"Tag {tag} verschieben fehlgeschlagen: {s} {r.get('message', '')}")
        print(f"✓ Tag {tag} → {commit[:10]}")
    angaben = dict(tag_name=tag, target_commitish=commit, name=p["titel"], body=p["notizen"], prerelease=False)
    if release:
        s, release = vw.api("PATCH", f"{weg}/releases/{release['id']}", tok, angaben)
        if s != 200:
            abbruch(f"Release ändern fehlgeschlagen: {s} {release.get('message', '')}")
        for a in release.get("assets", []):
            if a["name"] in p["assets"]:
                vw.api("DELETE", f"{weg}/releases/assets/{a['id']}", tok)
    else:
        s, release = vw.api("POST", f"{weg}/releases", tok, dict(angaben, draft=True))
        if s != 201:
            abbruch(f"Release anlegen fehlgeschlagen: {s} {release.get('message', '')}")
    hochladen(tok, release, zip_pfad.name, daten, "application/zip")
    hochladen(tok, release, SUMMEN, p["summen"].encode("utf-8"), "text/plain")
    hochladen(tok, release, SIGNATUR, minisig, "application/octet-stream")
    print(f"✓ Assets hochgeladen: {', '.join(p['assets'])}")
    s, release = vw.api("PATCH", f"{weg}/releases/{release['id']}", tok, dict(draft=False, make_latest="true"))
    if s != 200:
        abbruch(f"Release veröffentlichen fehlgeschlagen: {s} {release.get('message', '')}")
    print(f"✓ Release veröffentlicht: {release['html_url']}")
    zurueck = laden(f"https://github.com/{konto}/{repo}/releases/download/{tag}/{zip_pfad.name}")
    summen = laden(f"https://github.com/{konto}/{repo}/releases/download/{tag}/{SUMMEN}", 3)
    sig_zurueck = laden(f"https://github.com/{konto}/{repo}/releases/download/{tag}/{SIGNATUR}", 3)
    mod = signatur_modul(ordner)
    try:
        echt = summen is not None and sig_zurueck == minisig and bool(mod.pruefe(summen, sig_zurueck, None,
                                                                              mod.KOMMENTAR.format(version=p["version"])))
    except ValueError:
        echt = False
    if zurueck is None or hashlib.sha256(zurueck).hexdigest() != p["sha256"] or summen != p["summen"].encode("utf-8") or not echt:
        vw.api("PATCH", f"{weg}/releases/{release['id']}", tok, dict(draft=True))
        abbruch("Heruntergeladene Assets stimmen nicht mit ZIP bzw. Signatur überein – Release wieder auf Entwurf gesetzt.")
    print(f"✓ Assets geladen und geprüft: SHA-256 {p['sha256'][:16]}… stimmt, Signatur gültig ({sid})")
    print(f"✓ fertig: {p['download']}\n  Seite: {p['seite']} (mit bau_webapp.py --release-zip bauen, veroeffentliche_webapp.py)")


def main(argv):
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
        veroeffentlichen(ordner, zip_pfad, "--ersetzen" in argv, ci_pfad, werte.get("--ohne-ci"), sig_ordner)


if __name__ == "__main__":
    main(sys.argv[1:])
