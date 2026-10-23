#!/usr/bin/env python3
"""Prüft Me Goos-ta Deutsch automatisch auf echten GitHub-Rechnern (seit 2.2): Windows, macOS, Linux (x64 + ARM) und
ein schlankes Debian – Frischinstallation über die Startdatei, Oberfläche per API, beide Testreihen, Deinstallation –
und im Browser-Test Oberfläche, Web-App, Download-Seite und Anleitungen in WebKit, Firefox und Chromium.
Aufruf: python werkstatt/ci_lauf.py [<Ordner Me-Goos-ta-Deutsch>] [--probe] [--status] [--ohne-warten] [--nachlesen] [--zeit <min>]
                          [--release-pruefung]

--probe         ohne Netz und ohne Anmeldung: baut Release-Ordner, ZIP und Web-App (ohne Pyodide) im Temp-Ordner und zeigt
                den Plan (Branch, Dateien, Prüfsumme, Workflows) – schreibt nichts in den Arbeitsordner, pusht nichts
--status        die letzten Läufe auf Branch ci und der Release-Prüfung auf main (ohne zu pushen)
--ohne-warten   nur pushen, nicht auf den Lauf warten
--nachlesen     nicht pushen: den letzten Lauf auf ci für genau diesen Inhalt erneut auswerten (z. B. wenn Artefakte nicht ladbar waren)
--zeit <min>    höchstens so lange auf den Lauf warten (Standard 60)
--release-pruefung  Probe der Release-Prüfung (release_pruefung.yml testet das veröffentlichte Release): Branch ci nur
                mit diesem Workflow, Auslöser push auf ci statt auf main (ohne Warten auf ein passendes Release);
                ci_ergebnis.json bleibt unberührt

Ablauf: bau_release.py → Release-Ordner + ZIP im Temp-Ordner (Positivliste, keine Nutzerdaten), bau_webapp.py
--ohne-modelle --release-zip → web-app/ (Handy-App + Download-Seite für den Browser-Test) + .github/ des Quellbaums +
.gitattributes → ein verwaister Commit → Force-Push **nur** auf Branch ci (jeder andere Branch = Abbruch; main und
gh-pages bleiben unberührt) → warten, bis GitHub Actions fertig ist → Artefakte (ergebnis-<system>) laden → kurze
Zusammenfassung (≤ 30 Zeilen) + ci_ergebnis.json im Arbeitsordner (Inhalts-Prüfsumme des Release-Ordners, Lauf-Adresse,
Ergebnis je System) – veroeffentliche_release.py gibt ein Release nur für genau diesen grünen Inhalt frei. Anmeldung wie
veroeffentliche_webapp.py (GH_TOKEN → GitHub CLI → GitHub Desktop; der Schlüssel wird nie ausgegeben). Im Hintergrund
starten – ein Lauf dauert etwa 10–25 Minuten (je nach Warteschlange von GitHub)."""
import hashlib
import io
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

HIER = Path(__file__).resolve().parent                          # werkstatt/ (seit 2.5 G04)
ARBEIT = HIER.parent                                            # Wurzel des Quellbaums (Arbeitsordner)
sys.path.insert(0, str(HIER))
sys.dont_write_bytecode = True                                  # kein __pycache__ im Arbeitsordner
import veroeffentliche_webapp as vw  # noqa: E402  Anmeldung, GitHub-API, git

BRANCH = "ci"                                                   # der einzige Branch, den dieses Skript je schreibt
WORKFLOW = "tests.yml"
RELEASE_PRUEFUNG = "release_pruefung.yml"                       # läuft nach jedem Push auf main (seit 2.2, vorher wöchentlich)
QUELLE_GITHUB = ARBEIT / ".github"                              # → .github/ im Branch ci
ERGEBNIS = ARBEIT / "ci_ergebnis.json"
AUSFUEHRBAR = ("Me Goos-ta Deutsch - Mac.command", "Me Goos-ta Deutsch - Linux.sh")


def abbruch(text):
    sys.exit(f"✗ {text}")


def pruefe_branch(name):
    """Harte Sperre: Force-Push nur auf Branch ci."""
    if name != BRANCH:
        abbruch(f"Branch „{name}“ verweigert – ci_lauf.py schreibt nur Branch {BRANCH}.")
    return f"refs/heads/{BRANCH}"


def inhalt_pruefsumme(ordner):
    """SHA-256 über alle Dateien (Pfad + Inhalt) – gleich für gleichen Release-Inhalt, egal wo er liegt."""
    h = hashlib.sha256()
    for p in sorted(ordner.rglob("*"), key=lambda x: x.relative_to(ordner).as_posix()):
        if p.is_file():
            h.update(p.relative_to(ordner).as_posix().encode("utf-8") + b"\0")
            h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()


def baue_release(projekt, ziel):
    """Release-Ordner wie für das ZIP (bau_release.py, Positivliste) → <ziel>/Me-Goos-ta-Deutsch."""
    r = subprocess.run([sys.executable, str(HIER / "bau_release.py"), str(projekt), str(ziel)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    ordner = ziel / projekt.name
    if r.returncode or not ordner.is_dir():
        abbruch(f"bau_release.py fehlgeschlagen: {(r.stderr or r.stdout)[-600:]}")
    return ordner


def baue_zip(projekt, ziel):
    """Release-ZIP (für den Direktlink der Download-Seite) → <ziel>/Me-Goos-ta-Deutsch-<Version>.zip."""
    r = subprocess.run([sys.executable, str(HIER / "bau_release.py"), str(projekt), str(ziel), "--zip"], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    zips = sorted(ziel.glob("Me-Goos-ta-Deutsch-*.zip"))
    if r.returncode or not zips:
        abbruch(f"bau_release.py --zip fehlgeschlagen: {(r.stderr or r.stdout)[-600:]}")
    return zips[0]


def baue_webapp(projekt, ziel, zip_pfad, ohne_pyodide=False):
    """Handy-App + Download-Seite wie für GitHub Pages (ohne Real-ESRGAN-Modell) → <ziel>/web-app."""
    befehl = [sys.executable, str(HIER / "bau_webapp.py"), str(projekt), str(ziel), "--ohne-modelle", "--release-zip",
              str(zip_pfad)] + (["--ohne-pyodide"] if ohne_pyodide else [])
    r = subprocess.run(befehl, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env=dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1"))
    m = re.search(r"Version ([\w.-]+),", r.stdout)
    if r.returncode or not (ziel / "web-app" / "sw.js").is_file():
        abbruch(f"bau_webapp.py fehlgeschlagen: {(r.stderr or r.stdout)[-600:]}")
    return ziel / "web-app", (m.group(1) if m else "?")


def konto_repo(release):
    zeile = (release / "Programm" / "web_adresse.txt").read_text(encoding="utf-8").strip().splitlines()[0].strip()
    m = re.match(r"^https://([a-z0-9-]+)\.github\.io/([A-Za-z0-9._-]+)/$", zeile)
    if not m:
        abbruch("Programm/web_adresse.txt nennt keine GitHub-Pages-Adresse.")
    return m.group(1), m.group(2)


RP_AUSLOESER = "on:\n  push:\n    branches: [main]\n  workflow_dispatch:\n"
RP_PROBE = "on:\n  push:\n    branches: [ci]\n  workflow_dispatch:\n"


def branch_inhalt(release, ziel, app=None, release_pruefung=False):
    """Inhalt des Branches ci: Release-Ordner + .github/ + web-app/ + .gitattributes (nie Zeilenenden umschreiben).
    release_pruefung: nur release_pruefung.yml, Auslöser push auf ci statt auf main (Probe)."""
    if not (QUELLE_GITHUB / "workflows" / WORKFLOW).is_file():
        abbruch(f"Workflow fehlt: {QUELLE_GITHUB / 'workflows' / WORKFLOW}")
    shutil.copytree(release, ziel)
    for p in QUELLE_GITHUB.rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
            z = ziel / ".github" / p.relative_to(QUELLE_GITHUB)
            z.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, z)
    if release_pruefung:
        (ziel / ".github" / "workflows" / WORKFLOW).unlink()
        w = ziel / ".github" / "workflows" / RELEASE_PRUEFUNG
        text = w.read_text(encoding="utf-8")
        if text.count(RP_AUSLOESER) != 1:
            abbruch(f"{RELEASE_PRUEFUNG}: Auslöser-Block nicht gefunden (on: push main + workflow_dispatch)")
        w.write_bytes(text.replace(RP_AUSLOESER, RP_PROBE).encode("utf-8"))
    elif app:
        shutil.copytree(app, ziel / "web-app")
    (ziel / ".gitattributes").write_bytes(b"* -text\n")
    return sorted(p.relative_to(ziel).as_posix() for p in ziel.rglob("*") if p.is_file())


def plan(projekt, tmp, probe=False, release_pruefung=False):
    release = baue_release(projekt, tmp / "release")
    konto, repo = konto_repo(release)
    app, app_version = (None, None) if release_pruefung else baue_webapp(projekt, tmp / "app", baue_zip(projekt, tmp / "zip"),
                                                                      ohne_pyodide=probe)
    inhalt = tmp / "branch"
    dateien = branch_inhalt(release, inhalt, app, release_pruefung)
    version = re.search(r'^VERSION = "([\d.]+)', (release / "Programm" / "gans_lernkarten.py").read_text("utf-8"), re.M)[1]
    workflows = sorted(p.name for p in (inhalt / ".github" / "workflows").glob("*.yml"))
    return dict(konto=konto, repo=repo, branch=BRANCH, version=version, pruefsumme=inhalt_pruefsumme(release),
                dateien=len(dateien), github=[d for d in dateien if d.startswith(".github/")], workflows=workflows,
                web_app=sum(1 for d in dateien if d.startswith("web-app/")), web_app_version=app_version,
                release_pruefung=release_pruefung), inhalt


def pushen(inhalt, konto, repo, tok, ich, nachricht, branch=BRANCH):
    """Ein verwaister Commit mit dem Inhalt → Force-Push nur auf refs/heads/ci. Liefert die Commit-SHA."""
    ziel_ref = pruefe_branch(branch)
    git, env = vw.git_exe(), vw.git_umgebung(tok, ich)
    url = f"https://github.com/{konto}/{repo}.git"

    def g(*args):
        r = subprocess.run([git, *args], cwd=inhalt, env=env, capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
        if r.returncode:
            abbruch(f"git {args[0]} fehlgeschlagen: {(r.stderr or r.stdout)[-800:]}")
        return r
    g("init", "-q", "-b", BRANCH)
    g("add", "-A")
    da = [n for n in AUSFUEHRBAR if (inhalt / n).is_file()]
    if da:
        g("update-index", "--chmod=+x", "--", *da)
    g("commit", "-q", "-m", nachricht)
    sha = g("rev-parse", "HEAD").stdout.strip()
    g("push", "-q", "--force", url, f"HEAD:{ziel_ref}")
    return sha


def finde_lauf(weg, tok, sha, ende, workflow=WORKFLOW):
    while time.time() < ende:
        s, r = vw.api("GET", f"{weg}/actions/runs?branch={BRANCH}&head_sha={sha}&per_page=5", tok)
        laeufe = [x for x in (r.get("workflow_runs") or []) if x.get("path", "").endswith(workflow)] if s == 200 else []
        if laeufe:
            return laeufe[0]
        time.sleep(15)
    return None


def warte(weg, tok, lauf, ende):
    gemeldet = None
    while time.time() < ende:
        s, r = vw.api("GET", f"{weg}/actions/runs/{lauf['id']}", tok)
        if s == 200:
            lauf = r
            if r.get("status") == "completed":
                return lauf
            s, j = vw.api("GET", f"{weg}/actions/runs/{lauf['id']}/jobs?per_page=50", tok)
            jobs = j.get("jobs") or [] if s == 200 else []
            stand = (sum(1 for x in jobs if x.get("status") == "completed"), len(jobs))
            if stand != gemeldet:
                print(f"  … {stand[0]}/{stand[1]} Systeme fertig ({time.strftime('%H:%M')})", flush=True)
                gemeldet = stand
        time.sleep(30)
    return lauf


class _OhneWeiterleitung(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def lade_artefakt(url, tok):
    """Artefakt-ZIP: GitHub leitet auf einen signierten Speicher-Link weiter – der bekommt den Schlüssel nicht."""
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json",
                                               "User-Agent": "me-goos-ta-deutsch"})
    try:
        with urllib.request.build_opener(_OhneWeiterleitung).open(req, timeout=60) as r:
            return r.read()
    except urllib.error.HTTPError as f:
        if f.code not in (301, 302, 303, 307, 308):
            raise
        ort = f.headers.get("Location")
    with urllib.request.urlopen(urllib.request.Request(ort, headers={"User-Agent": "me-goos-ta-deutsch"}), timeout=120) as r:
        return r.read()


def ergebnisse(weg, tok, lauf):
    """{system: ergebnis.json} aus den Artefakten + Jobs ohne Artefakt (z. B. abgebrochen)."""
    aus = {}
    s, r = vw.api("GET", f"{weg}/actions/runs/{lauf['id']}/artifacts?per_page=50", tok)
    for a in (r.get("artifacts") or []) if s == 200 else []:
        if not a["name"].startswith("ergebnis-") or a.get("expired"):
            continue
        for versuch in range(6):                       # 23.10.2026: „503 Egress is over the account limit“ kam sporadisch
            try:
                with zipfile.ZipFile(io.BytesIO(lade_artefakt(a["archive_download_url"], tok))) as z:
                    aus[a["name"][len("ergebnis-"):]] = json.loads(z.read("ergebnis.json").decode("utf-8"))
                break
            except (OSError, KeyError, ValueError, zipfile.BadZipFile, urllib.error.URLError) as e:
                aus[a["name"][len("ergebnis-"):]] = dict(ok=False, pruefungen=[], fehler=f"Artefakt nicht lesbar: {e}")
                if not (isinstance(e, urllib.error.HTTPError) and e.code in (429, 500, 502, 503, 504)) or versuch == 5:
                    break
                time.sleep(10 * (versuch + 1))
    s, j = vw.api("GET", f"{weg}/actions/runs/{lauf['id']}/jobs?per_page=50", tok)
    for job in (j.get("jobs") or []) if s == 200 else []:
        name = job.get("name", "?")
        if name not in aus:
            aus[name] = dict(ok=False, pruefungen=[], fehler=f"kein Ergebnis (Job: {job.get('conclusion') or job.get('status')})")
        aus[name]["job"] = dict(conclusion=job.get("conclusion"), url=job.get("html_url"),
                                dauer=_dauer(job.get("started_at"), job.get("completed_at")))
    return aus


def _dauer(a, b):
    try:
        t = [time.mktime(time.strptime(x, "%Y-%m-%dT%H:%M:%SZ")) for x in (a, b)]
        return round(t[1] - t[0])
    except (TypeError, ValueError):
        return None


def zusammenfassung(systeme, lauf):
    zeilen = [f"Lauf {lauf.get('html_url')} · {lauf.get('conclusion') or lauf.get('status')}"]
    for name in sorted(systeme):
        e = systeme[name]
        pr = e.get("pruefungen") or []
        ok = sum(1 for p in pr if p.get("ok"))
        bekannt = sum(1 for p in pr if p.get("bekannt"))
        dauer = (e.get("job") or {}).get("dauer")
        kopf = (f"{'✓' if e.get('ok') else '✗'} {name:<12} {ok}/{len(pr)}" + (f" (bekannt {bekannt})" if bekannt else "")
                + (f" · {dauer // 60} min" if dauer else ""))
        zeilen.append(kopf)
        if not e.get("ok"):
            if e.get("fehler"):
                zeilen.append(f"    {e['fehler'][:150]}")
            for p in [p for p in pr if not p.get("ok")][:3]:
                zeilen.append(f"    – {p.get('name')}: {str(p.get('grund') or '')[:130]}")
    return zeilen[:30]


def melde_status(weg, tok):
    s, r = vw.api("GET", f"{weg}/actions/runs?branch={BRANCH}&per_page=5", tok)
    print(f"Branch {BRANCH}:")
    for x in (r.get("workflow_runs") or []) if s == 200 else []:
        print(f"  {x['created_at']}  {x['status']:<10} {x.get('conclusion') or '':<10} {x['head_sha'][:10]}  {x['html_url']}")
    if s != 200:
        print(f"  Abfrage fehlgeschlagen: {s} {r.get('message', '')}")
    s, w = vw.api("GET", f"{weg}/actions/workflows/{RELEASE_PRUEFUNG}", tok)
    if s == 404:
        print(f"Release-Prüfung: noch nicht aktiv ({RELEASE_PRUEFUNG} liegt noch nicht auf main – kommt mit dem nächsten Push auf main)")
        return
    zustand = w.get("state", "?")
    text = {"active": "aktiv (nach jedem Push auf main)",
            "disabled_manually": "von Hand abgeschaltet (Actions → „Release-Pruefung“ → „Enable workflow“)"}.get(zustand, zustand)
    print(f"Release-Prüfung: {text}")
    s, r = vw.api("GET", f"{weg}/actions/workflows/{RELEASE_PRUEFUNG}/runs?per_page=3", tok)
    for x in (r.get("workflow_runs") or []) if s == 200 else []:
        print(f"  {x['created_at']}  {x['status']:<10} {x.get('conclusion') or '':<10} {x['event']:<17} {x['html_url']}")


def weg_damit(pfad):
    """Ordner löschen – auch die schreibgeschützten Dateien, die git unter Windows anlegt."""
    def frei(fn, p, _):
        os.chmod(p, stat.S_IWRITE)
        fn(p)
    try:
        shutil.rmtree(pfad, onexc=frei)
    except OSError:
        pass


def optionen(argv):
    """→ (Positionsargumente, {Schalter: Wert oder True})"""
    pos, opt, i = [], {}, 0
    while i < len(argv):
        a = argv[i]
        if a in ("--zeit", "--branch") and i + 1 < len(argv):
            opt[a], i = argv[i + 1], i + 2
            continue
        if a.startswith("--"):
            opt[a] = True
        else:
            pos.append(a)
        i += 1
    return pos, opt


def main(argv):
    pos, opt = optionen(argv)
    pruefe_branch(opt.get("--branch", BRANCH))
    projekt = Path(pos[0]).resolve() if pos else ARBEIT / "Me-Goos-ta-Deutsch"
    minuten = float(opt.get("--zeit", 60))
    if not (projekt / "Programm" / "starter.py").is_file():
        abbruch(f"Kein Projektordner: {projekt}")
    argv = list(opt)
    tmp = Path(tempfile.mkdtemp(prefix="mgd-ci-"))
    try:
        if "--status" in argv:
            konto, repo = konto_repo(projekt)
            tok, _ = vw.token()
            melde_status(f"/repos/{konto}/{repo}", tok)
            return 0
        woche = "--release-pruefung" in argv
        p, inhalt = plan(projekt, tmp, probe="--probe" in argv, release_pruefung=woche)
        print(("Plan (Probe – ohne Netz, nichts wird verändert):" if "--probe" in argv else "Plan:"))
        print(f"  Repository {p['konto']}/{p['repo']} · Branch {p['branch']} (verwaister Commit, Force-Push nur hier)")
        print(f"  Inhalt     Release {p['version']} · {p['dateien']} Dateien · Prüfsumme {p['pruefsumme'][:16]}…")
        print(f"  Workflows  {', '.join(p['workflows'])} · .github: {len(p['github'])} Dateien"
              + (" · Probe der Release-Prüfung (push auf ci, testet das veröffentlichte Release)" if woche
                 else f" · web-app: {p['web_app']} Dateien ({p['web_app_version']})"))
        print("#plan " + json.dumps(p, ensure_ascii=False))
        if "--probe" in argv:
            return 0
        tok, woher = vw.token()
        s, ich = vw.api("GET", "/user", tok)
        if s != 200:
            abbruch(f"Anmeldung ({woher}) abgelehnt: {s} {ich.get('message', '')}")
        if ich["login"].lower() != p["konto"]:
            abbruch(f"Angemeldet als {ich['login']}, web_adresse.txt gehört zu {p['konto']}.")
        konto, weg = ich["login"], f"/repos/{ich['login']}/{p['repo']}"
        nachricht = f"CI Release-Prüfung (Probe) {p['version']}" if woche else f"CI {p['version']} · {p['pruefsumme'][:12]}"
        ende = time.time() + minuten * 60
        if "--nachlesen" in argv:                               # letzten Lauf für genau diesen Inhalt erneut auswerten
            s, r = vw.api("GET", f"{weg}/actions/runs?branch={BRANCH}&per_page=20", tok)
            lauf = next((x for x in (r.get("workflow_runs") or []) if s == 200
                         and x.get("path", "").endswith(RELEASE_PRUEFUNG if woche else WORKFLOW)
                         and (x.get("head_commit") or {}).get("message") == nachricht), None)
            if not lauf:
                abbruch(f"Kein Lauf auf {BRANCH} für diesen Inhalt („{nachricht}“) – ohne --nachlesen neu starten.")
            sha = lauf["head_sha"]
        else:
            sha = pushen(inhalt, konto, p["repo"], tok, ich, nachricht)
            print(f"✓ Branch {BRANCH} gepusht ({sha[:10]})", flush=True)
            if "--ohne-warten" in argv:
                return 0
            lauf = finde_lauf(weg, tok, sha, min(ende, time.time() + 300), RELEASE_PRUEFUNG if woche else WORKFLOW)
            if not lauf:
                abbruch("Kein Workflow-Lauf gefunden (Actions abgeschaltet?).")
        print(f"  Lauf: {lauf['html_url']}" + (" (nachgelesen)" if "--nachlesen" in argv else ""), flush=True)
        lauf = warte(weg, tok, lauf, ende)
        fertig = lauf.get("status") == "completed"
        systeme = ergebnisse(weg, tok, lauf) if fertig else {}
        ok = fertig and lauf.get("conclusion") == "success" and bool(systeme) and all(e.get("ok") for e in systeme.values())
        if woche:                                               # Probe: nur zeigen, ci_ergebnis.json (Release-Schranke) bleibt
            for z in zusammenfassung(systeme, lauf) if fertig else [f"✗ Lauf nach {minuten:.0f} min nicht fertig"]:
                print(z)
            print(("✓ RELEASE-PRÜFUNG GRÜN" if ok else "✗ RELEASE-PRÜFUNG NICHT GRÜN") + " (Probe auf Branch ci)")
            return 0 if ok else 1
        ERGEBNIS.write_text(json.dumps(dict(
            zeit=time.strftime("%Y-%m-%d %H:%M:%S"), version=p["version"], pruefsumme=p["pruefsumme"], commit=sha,
            lauf=lauf.get("html_url"), conclusion=lauf.get("conclusion"), ok=ok,
            systeme={n: dict(ok=bool(e.get("ok")), bestanden=sum(1 for x in e.get("pruefungen") or [] if x.get("ok")),
                             gesamt=len(e.get("pruefungen") or []), fehler=e.get("fehler"),
                             nicht_ok=[dict(name=x.get("name"), grund=str(x.get("grund") or "")[:300])
                                       for x in e.get("pruefungen") or [] if not x.get("ok")][:10],
                             bekannt=[x.get("name") for x in e.get("pruefungen") or [] if x.get("bekannt")],
                             job=e.get("job")) for n, e in systeme.items()}),
            ensure_ascii=False, indent=1), encoding="utf-8")
        if not fertig:
            print(f"✗ Lauf nach {minuten:.0f} min nicht fertig – später: python ci_lauf.py --status")
            return 1
        for z in zusammenfassung(systeme, lauf):
            print(z)
        print(("✓ ALLE SYSTEME GRÜN" if ok else "✗ NICHT ALLE SYSTEME GRÜN") + f" · {ERGEBNIS.name}")
        return 0 if ok else 1
    finally:
        weg_damit(tmp)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
