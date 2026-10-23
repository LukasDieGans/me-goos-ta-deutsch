#!/usr/bin/env python3
"""Arbeitsordner als Git-Quellbaum (seit 2.5 G04): einrichten, prüfen und signiert committen – nur lokal, nie pushen.
Aufruf: python werkstatt/quellbaum.py --status | --einrichten | --pruefen | --commit "Nachricht"

--einrichten  einmalig (wiederholbar): SSH-Signaturschlüssel ohne Passphrase in %USERPROFILE%\\MGD-Signatur\\git_ed25519
              (nur Benutzer-Rechte; liegt nie im Repo), git init (Branch main) mit lokaler Konfiguration (core.autocrlf=false,
              gpg.format=ssh, commit.gpgsign/tag.gpgsign, noreply-Identität aus dem Verlauf von main), origin = Repository
              aus web_adresse.txt; der Verlauf von main wird angehängt (fetch + reset, der Arbeitsbaum bleibt) – später
              Fast-Forward, nie Force-Push
--pruefen     was committet würde: keine Datei > 20 MB, keine Schlüssel/Tokens, Startdateien ausführbar, Nutzerdaten und
              private Notizen ignoriert, alle Release-Dateien versioniert (Ausgabe #pruefung {…}; Exit 1 bei Funden)
--commit      git add -A, Startdateien ausführbar, --pruefen, signierter Commit, Signatur gegenprüfen
--status      Branch, letzter Commit (Signatur), Änderungen, Abstand zu origin/main

Gepusht wird hier nie: main erst mit dem Release-Satz (G08), Branch ci nur über ci_lauf.py."""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent                          # werkstatt/
ARBEIT = HIER.parent                                            # Wurzel des Quellbaums
sys.path.insert(0, str(HIER))
sys.dont_write_bytecode = True
import veroeffentliche_webapp as vw  # noqa: E402  git aus PATH bzw. GitHub Desktop

SIGNATUR = Path(os.environ.get("MGD_SIGNATUR_ORDNER") or Path.home() / "MGD-Signatur")
SCHLUESSEL = SIGNATUR / "git_ed25519"
ERLAUBT = SIGNATUR / "git_allowed_signers"
PROJEKT = "Me-Goos-ta-Deutsch"
AUSFUEHRBAR = (f"{PROJEKT}/Me Goos-ta Deutsch - Mac.command", f"{PROJEKT}/Me Goos-ta Deutsch - Linux.sh")
MAX_GROESSE = 20 * 1024 * 1024
NOTIZEN = ("UEBERGABE.md", "FORTSETZUNG.md", "ARBEITSSTAND.md", "UMSETZUNGSPLAN.md", "HANDY_PLAN.md", "KI_BILD_RECHERCHE.md",
           "START_NEUES_PROJEKT.md", "PROMPT_NEUER_CHAT.txt")
# Beispiele, die nie ins Repo dürfen (Nutzerdaten wie aktualisieren.NUTZER, Archive, Proben, Ergebnisse)
NIE = NOTIZEN + tuple(f"{PROJEKT}/Programm/{n}" for n in (
    "karten.csv", "karten.bak.csv", "ui_einstellungen.json", "ideen.json", "lernstand.json", "lernstand.json.bak",
    "bilder/gans-x.png", "ideen/gans-x.png", "ausgabe/druck.pdf", "ausgabe/.verlauf/1/karten.csv", "_beispiele/karten.csv",
    "assets/gans_hintergrund.png", "assets/_alt/gans.png", "modelle/realesrgan-x4plus.npz", "modelle/realesrgan-x2plus.npz",
    "__pycache__/gans_ui.cpython-313.pyc")) + (
    "Me-Goos-ta-Deutsch-2.4.zip", "Release-2.5/Me-Goos-ta-Deutsch/README.md", "probe/daten/start.json", "ci_ergebnis.json",
    ".claude/launch.json", "werkstatt/__pycache__/ci_lauf.cpython-313.pyc")
# Pfade, die versioniert sein müssen (dazu jede Datei des Release-Ordners)
PFLICHT = (".gitignore", ".gitattributes", ".github/workflows/tests.yml", ".github/workflows/release_pruefung.yml",
           ".github/ci/frischtest.py", ".github/SECURITY.md", "web-app-quelle/sw.js", "werkstatt/bau_release.py",
           "werkstatt/bau_webapp.py", "werkstatt/bau_lock.py", "werkstatt/bau_lock_antworten.json", "werkstatt/ci_lauf.py",
           "werkstatt/quellbaum.py", "werkstatt/veroeffentliche_release.py", "werkstatt/signiere_release.py",
           f"{PROJEKT}/Programm/gans_ui.py", f"{PROJEKT}/Programm/pakete.lock", f"{PROJEKT}/Programm/beispiel-karten.csv")
# Schlüssel-/Token-Muster: nur echte Werte (Erwähnungen in Doku und Code schlagen nicht an)
GEHEIM = re.compile(rb"ghp_[A-Za-z0-9]{36}|gho_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{40,}|AKIA[0-9A-Z]{16}"
                    rb"|-----BEGIN [A-Z ]*PRIVATE KEY-----\r?\n[A-Za-z0-9+/=\r\n]{40,}"
                    rb"|minisign encrypted secret key\r?\n[A-Za-z0-9+/=]{100,}")
GEHEIM_ENDUNGEN = {".dpapi", ".key", ".pem", ".p12", ".pfx"}


def abbruch(text):
    sys.exit(f"✗ {text}")


def git(*args, pruefen=True, roh=False, cwd=None):
    r = subprocess.run([vw.git_exe(), *args], cwd=cwd or ARBEIT, capture_output=True,
                       env=dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never"))
    if pruefen and r.returncode:
        abbruch(f"git {args[0]} fehlgeschlagen: {(r.stderr or r.stdout).decode('utf-8', 'replace')[-800:]}")
    return r if roh else r.stdout.decode("utf-8", "replace")


def ssh_keygen():
    """ssh-keygen mit -Y sign (Windows: OpenSSH des Systems; sonst aus dem PATH)."""
    kandidaten = [Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "OpenSSH" / "ssh-keygen.exe"]
    import shutil
    if shutil.which("ssh-keygen"):
        kandidaten.append(Path(shutil.which("ssh-keygen")))
    for k in kandidaten:
        if k.is_file():
            return str(k)
    abbruch("ssh-keygen nicht gefunden (Windows: optionales Feature „OpenSSH-Client“).")


def repo_adresse():
    zeile = (ARBEIT / PROJEKT / "Programm" / "web_adresse.txt").read_text(encoding="utf-8").strip().splitlines()[0].strip()
    m = re.match(r"^https://([a-z0-9-]+)\.github\.io/([A-Za-z0-9._-]+)/$", zeile)
    if not m:
        abbruch("web_adresse.txt nennt keine GitHub-Pages-Adresse.")
    return f"https://github.com/{m.group(1)}/{m.group(2)}.git"


def schluessel_anlegen():
    """Ed25519 ohne Passphrase (sonst könnte Claude nicht committen); Schutz über Benutzer-Rechte. Nie überschreiben."""
    SIGNATUR.mkdir(parents=True, exist_ok=True)
    if not SCHLUESSEL.is_file():
        r = subprocess.run([ssh_keygen(), "-q", "-t", "ed25519", "-N", "", "-C", "me-goos-ta-deutsch git", "-f", str(SCHLUESSEL)],
                           capture_output=True, text=True)
        if r.returncode or not SCHLUESSEL.is_file():
            abbruch(f"ssh-keygen fehlgeschlagen: {r.stderr[-400:]}")
        print(f"✓ Signaturschlüssel angelegt: {SCHLUESSEL}.pub")
    if sys.platform == "win32":                                 # nur der eigene Benutzer (ssh-keygen verlangt das auch)
        benutzer = os.environ.get("USERNAME", "")
        subprocess.run(["icacls", str(SCHLUESSEL), "/inheritance:r", "/grant:r", f"{benutzer}:F"], capture_output=True)
    else:
        os.chmod(SCHLUESSEL, 0o600)
    return Path(f"{SCHLUESSEL}.pub").read_text(encoding="ascii").strip()


def einrichten():
    if not (ARBEIT / ".git").exists():
        git("init", "-q", "-b", "main")
        print(f"✓ git init {ARBEIT}")
    oeffentlich = schluessel_anlegen()
    adresse = repo_adresse()
    if "origin" in git("remote").split():
        git("remote", "set-url", "origin", adresse)
    else:
        git("remote", "add", "origin", adresse)
    git("fetch", "-q", "origin", "main")                         # öffentliches Repo: ohne Anmeldung
    autor = git("log", "-1", "--format=%an%n%ae", "origin/main").split("\n")
    if len(autor) < 2 or not autor[1].endswith("@users.noreply.github.com"):
        abbruch(f"Letzter Commit auf main ohne noreply-Adresse: {autor}")
    name, mail = autor[0], autor[1]
    for k, v in (("core.autocrlf", "false"), ("core.filemode", "false"), ("user.name", name), ("user.email", mail),
                 ("gpg.format", "ssh"), ("user.signingkey", f"{SCHLUESSEL}.pub"), ("gpg.ssh.program", ssh_keygen()),
                 ("gpg.ssh.allowedSignersFile", str(ERLAUBT)), ("commit.gpgsign", "true"), ("tag.gpgsign", "true"),
                 ("push.default", "nothing")):                  # nie versehentlich pushen
        git("config", "--local", k, v)
    ERLAUBT.write_text(f"{mail} {oeffentlich}\n", encoding="ascii")
    if git("rev-parse", "--verify", "-q", "HEAD", pruefen=False, roh=True).returncode:
        git("reset", "-q", "origin/main")                       # Verlauf anhängen, Arbeitsbaum bleibt
        print("✓ Verlauf von origin/main angehängt (Arbeitsbaum unverändert)")
    print(f"✓ eingerichtet · {name} <{mail}> · Signatur {SCHLUESSEL}.pub")
    print(f"Für Lukas: Inhalt von {SCHLUESSEL}.pub auf GitHub als „Signing Key“ hinterlegen.")


def _ignoriert(pfade):
    r = subprocess.run([vw.git_exe(), "check-ignore", "--no-index", "--stdin"], cwd=ARBEIT, capture_output=True,
                       input="\n".join(pfade).encode("utf-8"))
    return set(r.stdout.decode("utf-8").splitlines())


def release_dateien():
    """Pfade (unter Me-Goos-ta-Deutsch/), die bau_release.py ins Release nimmt – ohne zu bauen."""
    import importlib.util
    alt = sys.argv
    try:
        sys.argv = ["bau_release.py", str(ARBEIT / PROJEKT), str(ARBEIT / "_nie")]
        spec = importlib.util.spec_from_file_location("bau_release_qb", HIER / "bau_release.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        rein, _ = m.auswahl()
    finally:
        sys.argv = alt
    return [f"{PROJEKT}/{rel.as_posix()}" for _, rel in rein]


def pruefen(ausgeben=True):
    """Prüft den Stand, der committet würde (Index + nicht ignorierte neue Dateien). → (ok, Befund)."""
    if not (ARBEIT / ".git").is_dir():
        abbruch("Kein Git-Quellbaum – erst --einrichten.")
    im_index = [z for z in git("ls-files", "-z").split("\0") if z]
    neu = [z for z in git("ls-files", "-z", "--others", "--exclude-standard").split("\0") if z]
    dateien = sorted({p for p in im_index + neu if (ARBEIT / p).is_file()})
    gross = [p for p in dateien if (ARBEIT / p).stat().st_size > MAX_GROESSE]
    geheim = [p for p in dateien if Path(p).suffix.lower() in GEHEIM_ENDUNGEN or GEHEIM.search((ARBEIT / p).read_bytes())]
    modi = {z.split("\t", 1)[1]: z.split()[0] for z in git("ls-files", "-s").splitlines() if "\t" in z}
    nicht_ausfuehrbar = [p for p in AUSFUEHRBAR if modi.get(p) != "100755"]
    ign = _ignoriert(list(NIE))
    nicht_ignoriert = [p for p in NIE if p not in ign]
    rel = release_dateien()
    pflicht = list(PFLICHT) + rel
    ign2 = _ignoriert(pflicht)
    fehlt = [p for p in pflicht if p in ign2 or p not in set(dateien)]
    befund = dict(dateien=len(dateien), release=len(rel), gross=gross, geheim=geheim, nicht_ausfuehrbar=nicht_ausfuehrbar,
                  nicht_ignoriert=nicht_ignoriert, fehlt=fehlt, ignoriert_geprueft=len(NIE))
    ok = not (gross or geheim or nicht_ausfuehrbar or nicht_ignoriert or fehlt)
    if ausgeben:
        print(f"{'✓' if ok else '✗'} {len(dateien)} Dateien · Release {len(rel)} versioniert · {len(NIE)} Ignorier-Beispiele")
        for k in ("gross", "geheim", "nicht_ausfuehrbar", "nicht_ignoriert", "fehlt"):
            if befund[k]:
                print(f"  {k}: {', '.join(befund[k][:8])}")
        print("#pruefung " + json.dumps(befund, ensure_ascii=False))
    return ok, befund


def commit(nachricht):
    git("add", "-A")
    git("update-index", "--chmod=+x", "--", *AUSFUEHRBAR)
    ok, _ = pruefen()
    if not ok:
        abbruch("Prüfung nicht bestanden – nichts committet.")
    if git("diff", "--cached", "--quiet", pruefen=False, roh=True).returncode == 0:
        print("= nichts zu committen")
        return
    git("commit", "-q", "-S", "-m", nachricht)
    r = git("verify-commit", "HEAD", pruefen=False, roh=True)
    sha = git("rev-parse", "--short=10", "HEAD").strip()
    if r.returncode:
        abbruch(f"Commit {sha} angelegt, Signatur aber nicht prüfbar: {r.stderr.decode('utf-8', 'replace')[-300:]}")
    print(f"✓ signierter Commit {sha}: {nachricht}")


def status():
    print(git("log", "-1", "--format=%h %G? %s (%an, %ad)", "--date=short").strip(), "· Signatur G = gültig")
    print(git("status", "-sb").splitlines()[0])
    aenderungen = [z for z in git("status", "--porcelain").splitlines() if z]
    print(f"{len(aenderungen)} geänderte/neue Dateien" + ("" if not aenderungen else ": " + ", ".join(a[3:] for a in aenderungen[:6])))


def main(argv):
    if "--einrichten" in argv:
        einrichten()
    elif "--pruefen" in argv:
        return 0 if pruefen()[0] else 1
    elif "--commit" in argv and argv.index("--commit") + 1 < len(argv):
        commit(argv[argv.index("--commit") + 1])
    elif "--status" in argv:
        status()
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
