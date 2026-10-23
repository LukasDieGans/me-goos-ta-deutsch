#!/usr/bin/env python3
"""Veröffentlicht die gebaute Handy-App (Ordner web-app/ aus bau_webapp.py) auf GitHub Pages.
Aufruf: python veroeffentliche_webapp.py <Ordner web-app> [--repo me-goos-ta-deutsch] [--nachricht "Text"]

Ablauf: Anmeldung holen → öffentliches Repository anlegen (falls es fehlt) → Inhalt von web-app/ als Branch gh-pages
pushen (Verlauf bleibt, nur Geändertes wird übertragen) → GitHub Pages für gh-pages einschalten → warten, bis die Seite
mit der neuen Version ausgeliefert wird (und die Download-Seite download/, falls gebaut). Nur der App-Ordner geht hinaus –
keine Nutzerdaten (die baut bau_webapp.py nie ein). Das Programm-Release (Branch main, Tag, ZIP) macht
veroeffentliche_release.py.

Anmeldung (der Schlüssel wird nie ausgegeben oder gespeichert, git bekommt ihn nur über Umgebungsvariablen):
GH_TOKEN/GITHUB_TOKEN → `gh auth token` (GitHub CLI) → Anmeldung von GitHub Desktop (Windows-Anmeldeinformationen).
git: aus dem PATH, sonst das von GitHub Desktop mitgebrachte. Commits laufen unter der noreply-Adresse des Kontos."""
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com"


def token():
    for n in ("GH_TOKEN", "GITHUB_TOKEN"):
        if os.environ.get(n):
            return os.environ[n].strip(), n
    gh = shutil.which("gh")
    if gh:
        r = subprocess.run([gh, "auth", "token"], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip(), "GitHub CLI"
    if sys.platform == "win32":
        t = _github_desktop()
        if t:
            return t, "GitHub Desktop"
    sys.exit("Keine GitHub-Anmeldung gefunden: GitHub CLI (`gh auth login`) oder GitHub Desktop anmelden.")


def _github_desktop():
    """Schlüssel, den GitHub Desktop in den Windows-Anmeldeinformationen ablegt („GitHub - https://api.github.com/<konto>“)."""
    import ctypes
    from ctypes import wintypes

    class CRED(ctypes.Structure):
        _fields_ = [("Flags", wintypes.DWORD), ("Type", wintypes.DWORD), ("TargetName", wintypes.LPWSTR),
                    ("Comment", wintypes.LPWSTR), ("LastWritten", wintypes.FILETIME), ("CredentialBlobSize", wintypes.DWORD),
                    ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)), ("Persist", wintypes.DWORD),
                    ("AttributeCount", wintypes.DWORD), ("Attributes", ctypes.c_void_p), ("TargetAlias", wintypes.LPWSTR),
                    ("UserName", wintypes.LPWSTR)]
    adv = ctypes.WinDLL("advapi32", use_last_error=True)
    zahl, liste = wintypes.DWORD(), ctypes.POINTER(ctypes.POINTER(CRED))()
    if not adv.CredEnumerateW("GitHub - https://api.github.com/*", 0, ctypes.byref(zahl), ctypes.byref(liste)):
        return None
    try:
        for i in range(zahl.value):
            c = liste[i].contents
            roh = bytes(c.CredentialBlob[:c.CredentialBlobSize])
            if roh:
                return (roh.decode("utf-16-le") if b"\0" in roh else roh.decode("utf-8")).strip()
    finally:
        adv.CredFree(liste)
    return None


def api(methode, weg, tok, daten=None, ok=(200, 201, 204)):
    req = urllib.request.Request(API + weg, method=methode, data=json.dumps(daten).encode() if daten is not None else None,
                                 headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json",
                                          "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "me-goos-ta-deutsch"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            text = r.read().decode("utf-8")
            return r.status, json.loads(text) if text else {}
    except urllib.error.HTTPError as f:
        text = f.read().decode("utf-8", "replace")
        if f.code in ok:
            return f.code, {}
        return f.code, (json.loads(text) if text.startswith("{") else {"message": text})


def git_exe():
    g = shutil.which("git")
    if g:
        return g
    for d in sorted((Path(os.environ.get("LOCALAPPDATA", "")) / "GitHubDesktop").glob("app-*"), reverse=True):
        g = d / "resources" / "app" / "git" / "cmd" / "git.exe"
        if g.is_file():
            return str(g)
    sys.exit("git nicht gefunden (GitHub Desktop oder Git für Windows installieren).")


def git_umgebung(tok, ich):
    """Umgebung für git: Schlüssel nur als Kopfzeile (nie in Adresse/Konfiguration), Bytes 1:1, noreply-Adresse."""
    kopf = "AUTHORIZATION: basic " + base64.b64encode(f"x-access-token:{tok}".encode()).decode()
    konto = ich["login"]
    return dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never", GIT_CONFIG_COUNT="3",
                GIT_CONFIG_KEY_0="http.https://github.com/.extraheader", GIT_CONFIG_VALUE_0=kopf,
                GIT_CONFIG_KEY_1="credential.helper", GIT_CONFIG_VALUE_1="",
                GIT_CONFIG_KEY_2="core.autocrlf", GIT_CONFIG_VALUE_2="false",   # Bytes 1:1 (Prüfsummen im Service Worker)
                GIT_AUTHOR_NAME=konto, GIT_COMMITTER_NAME=konto,
                GIT_AUTHOR_EMAIL=f"{ich['id']}+{konto}@users.noreply.github.com",
                GIT_COMMITTER_EMAIL=f"{ich['id']}+{konto}@users.noreply.github.com")


def main():
    if len(sys.argv) < 2 or not (Path(sys.argv[1]) / "sw.js").is_file():
        sys.exit(__doc__)
    quelle = Path(sys.argv[1]).resolve()
    repo = sys.argv[sys.argv.index("--repo") + 1] if "--repo" in sys.argv else "me-goos-ta-deutsch"
    version = json.loads((quelle / "manifest.webmanifest").read_text(encoding="utf-8")).get("x_version", "?")
    nachricht = sys.argv[sys.argv.index("--nachricht") + 1] if "--nachricht" in sys.argv else f"Web-App {version}"
    tok, woher = token()
    s, ich = api("GET", "/user", tok)
    if s != 200:
        sys.exit(f"Anmeldung ({woher}) abgelehnt: {s} {ich.get('message', '')}")
    konto = ich["login"]
    seite = f"https://{konto.lower()}.github.io/{repo}/"
    print(f"Konto {konto} (Anmeldung: {woher}) → {seite}")
    s, r = api("GET", f"/repos/{konto}/{repo}", tok)
    if s == 404:
        s, r = api("POST", "/user/repos", tok, dict(
            name=repo, private=False, auto_init=False, has_issues=True, has_wiki=False, has_projects=False, homepage=seite,
            description="Me Goos-ta Deutsch – Lernkarten mit Gänse-Wortwitz als Handy-App (Web-App, offline). "
                        "MIT · Eine Gans namens Lukas"))
        if s != 201:
            sys.exit(f"Repository anlegen fehlgeschlagen: {s} {r.get('message', '')}")
        print("✓ Repository angelegt (öffentlich)")
    elif s != 200:
        sys.exit(f"Repository nicht lesbar: {s} {r.get('message', '')}")
    git = git_exe()
    env = git_umgebung(tok, ich)
    arbeit = Path(tempfile.mkdtemp(prefix="mgd-pages-"))
    url = f"https://github.com/{konto}/{repo}.git"

    def g(*args, pruefen=True):
        r = subprocess.run([git, *args], cwd=arbeit, env=env, capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
        if pruefen and r.returncode:
            sys.exit(f"git {args[0]} fehlgeschlagen: {(r.stderr or r.stdout)[-800:]}")
        return r
    try:
        g("init", "-q", "-b", "gh-pages")
        g("remote", "add", "origin", url)
        if g("fetch", "-q", "--depth", "1", "origin", "gh-pages", pruefen=False).returncode == 0:
            g("update-ref", "refs/heads/gh-pages", "FETCH_HEAD")   # Index leer → Bau ersetzt alles, Verlauf bleibt
        for p in quelle.rglob("*"):
            if p.is_file():
                z = arbeit / p.relative_to(quelle)
                z.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(p, z)
        g("add", "-A")
        if g("diff", "--cached", "--quiet", pruefen=False).returncode == 0:
            print("= Inhalt unverändert – nichts zu pushen")
        else:
            g("commit", "-q", "-m", nachricht)
            g("push", "-q", "origin", "gh-pages")
            print(f"✓ gh-pages gepusht ({nachricht})")
    finally:
        shutil.rmtree(arbeit, ignore_errors=True)
    s, r = api("GET", f"/repos/{konto}/{repo}/pages", tok)
    if s == 404:
        s, r = api("POST", f"/repos/{konto}/{repo}/pages", tok, {"source": {"branch": "gh-pages", "path": "/"}})
        if s not in (201, 409):
            sys.exit(f"GitHub Pages einschalten fehlgeschlagen: {s} {r.get('message', '')}")
        print("✓ GitHub Pages eingeschaltet (Branch gh-pages)")
    else:
        api("POST", f"/repos/{konto}/{repo}/pages/builds", tok)          # neuen Bau anstoßen (falls nötig)
    ende = time.time() + 600
    if not warte(seite + "manifest.webmanifest", lambda d: json.loads(d.decode("utf-8")).get("x_version") == version, ende):
        sys.exit(f"Seite liefert nach 10 min noch nicht Version {version} – später {seite} prüfen.")
    print(f"✓ online: {seite}  (Version {version})")
    dl = quelle / "download" / "index.html"                        # Download-Seite (seit 2.1): gehört nicht zur App-Version
    if dl.is_file():
        soll = hashlib.sha256(dl.read_bytes()).hexdigest()
        if not warte(seite + "download/", lambda d: hashlib.sha256(d).hexdigest() == soll, ende):
            sys.exit(f"Download-Seite nach 10 min noch nicht neu – später {seite}download/ prüfen.")
        print(f"✓ Download-Seite online: {seite}download/")


def warte(url, passt, ende):
    """Fragt die Adresse (ohne Zwischenspeicher) alle 10 s ab, bis passt(Bytes) stimmt oder die Zeit um ist."""
    while time.time() < ende:
        try:
            with urllib.request.urlopen(urllib.request.Request(f"{url}?v={time.time()}", headers={"Cache-Control": "no-cache"}),
                                        timeout=30) as r:
                if passt(r.read()):
                    return True
        except (urllib.error.URLError, ValueError, OSError):
            pass
        time.sleep(10)
    return False


if __name__ == "__main__":
    main()
