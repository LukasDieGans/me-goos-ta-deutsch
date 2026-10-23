#!/usr/bin/env python3
"""Frischtest von Me Goos-ta Deutsch auf einem echten Rechner (seit 2.2) – wie ein Nutzer: Startdatei, Oberfläche per
API, beide Testreihen, zweiter Start, Update in einen neuen Ordner, Update direkt im Programm (seit 2.4: Version 9.9 von
einem Release-Server auf 127.0.0.1, Neustart über die Startdatei – nur auf GitHub-Rechnern), Deinstallation. Nur Standardbibliothek; läuft mit dem
Python des Runners als „Dirigent“ (das Programm richtet wie beim Nutzer sein eigenes Python ein).

GitHub Actions (Branch ci; Wegwerf-Rechner → echte Startdatei, echte Symbole, echter Datenordner):
    python .github/ci/frischtest.py --system <name> [--ergebnis ergebnis.json] [--neuestes-release] [--neueste-pakete]
    (--neuestes-release: Release-Prüfung nach dem Push auf main – statt des Checkouts das veröffentlichte Release-ZIP, gegen SHA256SUMS.txt geprüft;
     --neueste-pakete: Frühwarnung – der Starter nimmt die Spannen aus requirements.txt statt pakete.lock, MGD_PAKETE_NEUESTE=1)
Lokal (nur Windows – der bisherige Frischtest aus UEBERGABE §5: LOCALAPPDATA umgelenkt, Symbole im Testordner, keine
Programm-Deinstallation; Desktop-Symbol und Datenordner dieses Rechners bleiben unberührt):
    python frischtest.py --lokal <kurzer Testordner außerhalb von Temp> --quelle <Release-Ordner> [--ohne-tests]

Harte Sperre: ohne GITHUB_ACTIONS=true und ohne --lokal startet nichts – die echte Startdatei würde sonst Desktop-Symbol
und Datenordner dieses Rechners auf die Testkopie verbiegen. Ergebnis: ergebnis.json (Prüfungen mit Name, ok, Grund,
Dauer; bei Fehlern die letzten ≤ 40 Protokollzeilen) und Exit-Code 0/1. Schlüssel und Token kommen nie ins Protokoll."""
import http.client
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

WIN, MAC = os.name == "nt", sys.platform == "darwin"
ART = "win" if WIN else "mac" if MAC else "linux"
NAME = "Me-Goos-ta-Deutsch"
START = {"win": "Me Goos-ta Deutsch - Windows.cmd", "mac": "Me Goos-ta Deutsch - Mac.command",
         "linux": "Me Goos-ta Deutsch - Linux.sh"}
ZEIT_START = 20 * 60                       # Ersteinrichtung (Python, Pakete) höchstens
ZEIT_GESAMT = 41 * 60                      # Job-Zeitlimit 45 min – danach werden übrige Stufen übersprungen
# Prüfungen von test_gans_lernkarten.py (Referenz, nie ändern), die nur an einer Windows-Annahme **des Tests** scheitern:
# {(system, Name der Prüfung): Grund}. Programmfehler kommen hier nie hinein – die werden behoben.
BEKANNT: dict = {}

T0 = time.time()
ERG = []


class Stopp(Exception):
    """Eine Stufe ist so gescheitert, dass die folgenden keinen Sinn mehr haben."""


def log(text):
    print(text, flush=True)


def maskiere(text):
    """Start-Schlüssel (?k=…) und Cookies nie ins Protokoll."""
    text = re.sub(r"([?&]k=)[A-Za-z0-9_\-]+", r"\1…", str(text))
    return re.sub(r"(mgd_\d+=)[^;\s\"']+", r"\1…", text)


def ende(text, n=40):
    return maskiere("\n".join(str(text).replace("\r", "\n").splitlines()[-n:]))


def pruefe(name, ok, grund="", t0=None, protokoll=None, bekannt=None):
    e = dict(name=name, ok=bool(ok), grund=maskiere(grund)[:600], dauer=round(time.time() - t0, 1) if t0 else None)
    if bekannt:
        e["bekannt"] = bekannt
    if not ok and protokoll:
        e["protokoll"] = ende(protokoll)
    ERG.append(e)
    dauer = f" ({e['dauer']:.0f} s)" if e["dauer"] else ""
    log(f"{'✓' if ok else '✗'} {name}{dauer}" + ("" if ok else f" – {e['grund'][:300]}"))
    return bool(ok)


def version_von(ordner):
    m = re.search(r'^VERSION = "([^" ]+)', (ordner / "Programm" / "gans_lernkarten.py").read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else "?"


def lies_json(pfad):
    try:
        return json.loads(Path(pfad).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def gleich(a, b):
    return os.path.normcase(os.path.realpath(str(a))) == os.path.normcase(os.path.realpath(str(b)))


def schliesse_hinweis(titel):
    """Hinweisfenster des Startprogramms wie mit „OK“ schließen (niemand klickt auf dem Runner): Windows-Meldungsfenster
    per WM_CLOSE, macOS-Alert (osascript „display alert“) beenden. Linux-Runner haben weder zenity noch kdialog.
    → Anzahl geschlossener Fenster."""
    if WIN:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        gefunden = []

        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def je_fenster(hwnd, _):
            n = user32.GetWindowTextLengthW(hwnd)
            puffer = ctypes.create_unicode_buffer(n + 1)
            user32.GetWindowTextW(hwnd, puffer, n + 1)
            if puffer.value == titel:
                gefunden.append(hwnd)
            return True
        user32.EnumWindows(je_fenster, 0)
        for h in gefunden:
            user32.PostMessageW(h, 0x0010, 0, 0)               # WM_CLOSE → MessageBoxW kehrt mit IDOK zurück
        return len(gefunden)
    if MAC:
        return int(subprocess.run(["pkill", "-f", "display alert"], capture_output=True).returncode == 0)
    return 0


# =============================================================================================
# Oberfläche per API (wie die Seite: Cookie aus /?k=…, Token-Kopfzeile, Origin)
# =============================================================================================
class Oberflaeche:
    def __init__(self, instanz):
        self.port = int(instanz["port"])
        r, _ = self._roh("GET", "/?k=" + instanz["schluessel"], {})
        keks = (r.getheader("Set-Cookie") or "").split(";")[0]
        if r.status != 303 or "=" not in keks:
            raise Stopp(f"Startadresse antwortet {r.status} ohne Cookie")
        self.kopf = {"Cookie": keks, "X-GL-Token": keks.partition("=")[2], "Content-Type": "application/json",
                     "Origin": f"http://127.0.0.1:{self.port}"}

    def _roh(self, methode, weg, kopf, koerper=None, zeit=120):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=zeit)
        try:
            c.request(methode, weg, body=koerper, headers=kopf)
            r = c.getresponse()
            return r, r.read()
        finally:
            c.close()

    @staticmethod
    def _json(roh):
        try:
            return json.loads(roh.decode("utf-8")) if roh else {}
        except ValueError:
            return {"roh": roh[:300].decode("utf-8", "replace")}

    def get(self, weg, zeit=120):
        r, d = self._roh("GET", weg, self.kopf, zeit=zeit)
        return r.status, self._json(d)

    def post(self, weg, daten=None, zeit=300):
        r, d = self._roh("POST", weg, self.kopf, json.dumps(daten or {}).encode("utf-8"), zeit)
        return r.status, self._json(d)

    def post_roh(self, weg, inhalt, typ, zeit=300):
        r, d = self._roh("POST", weg, dict(self.kopf, **{"Content-Type": typ}), inhalt, zeit)
        return r.status, self._json(d)

    def warte_lauf(self, lid, zeit=900):
        """Wartet, bis der Auftrag der Warteschlange fertig ist → Status (mit allen Zeilen) oder None."""
        frist = time.time() + zeit
        while time.time() < frist:
            s, st = self.get(f"/api/lauf?id={lid}&ab=100000")
            if s == 200 and st.get("id") == lid and st.get("code") is not None:
                return self.get(f"/api/lauf?id={lid}")[1]
            time.sleep(2)
        return None


# =============================================================================================
# Ablauf
# =============================================================================================
class Frischtest:
    def __init__(self, system, quelle, lokal=None, ohne_tests=False, neueste=False):
        self.system, self.quelle, self.lokal, self.ohne_tests, self.neueste = system, quelle, lokal, ohne_tests, neueste
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith(("PYTHON", "MGD_")) and k not in ("VIRTUAL_ENV", "CONDA_PREFIX")}
        loc = os.environ.get("pythonLocation")                  # actions/setup-python: kein Python im PATH wie beim Nutzer
        if loc:
            self.env["PATH"] = os.pathsep.join(p for p in self.env.get("PATH", "").split(os.pathsep)
                                               if not p.startswith(loc))
        if lokal:
            basis = Path(lokal)
            self.o1, self.o2 = basis / "a" / NAME, basis / "b" / NAME
            self.env["LOCALAPPDATA"] = str(basis / "lad")
            self.symbole = basis / "symbole"
        else:
            basis = Path("C:/") if WIN else Path.home()
            self.o1, self.o2 = basis / "mgd" / NAME, basis / "mgd2" / NAME
            self.symbole = None
        if ART == "linux":
            self.env["MGD_KEIN_TERMINAL"] = "1"                 # ohne Terminalfenster (wie „sh …Linux.sh“ im Terminal)
        self.env["MGD_KEIN_BROWSER"] = "1"                      # Neustart nach dem Update im Programm: kein Browser
        if neueste:
            self.env["MGD_PAKETE_NEUESTE"] = "1"                # Starter: Spannen aus requirements.txt statt pakete.lock
        self.update_server = None
        self.signiert = False
        self.daten = self._daten_ordner()
        self.env_tests = None
        self.ui = None
        self.version = version_von(quelle)
        self.karten = 0
        self.lern_id = None
        self.ar_text = None

    def _daten_ordner(self):
        if WIN:
            return Path(self.env.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "Me-Goos-ta-Deutsch"
        if MAC:
            return Path.home() / "Library" / "Application Support" / "Me-Goos-ta-Deutsch"
        return Path(self.env.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "me-goos-ta-deutsch"

    def symbol_ziele(self):
        if self.lokal:
            return [self.symbole / "Me Goos-ta Deutsch.lnk"]
        if WIN:
            r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command",
                                "[Environment]::GetFolderPath('Desktop'); [Environment]::GetFolderPath('Programs')"],
                               capture_output=True, text=True, timeout=60)
            return [Path(z.strip()) / "Me Goos-ta Deutsch.lnk" for z in r.stdout.splitlines() if z.strip()]
        if MAC:
            return [Path.home() / "Applications" / "Me Goos-ta Deutsch.app"]
        return [Path(self.env.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "applications" /
                "me-goos-ta-deutsch.desktop"]

    # ---------- Hilfen ----------
    def kopieren(self, ziel):
        if ziel.parent.exists():
            shutil.rmtree(ziel.parent)
        weg = shutil.ignore_patterns(".git", ".github", ".gitattributes", "ergebnis*.json", "__pycache__")
        shutil.copytree(self.quelle, ziel, ignore=weg)
        dateien = [p for p in ziel.rglob("*") if p.is_file()]
        if WIN:                                                 # wie aus dem Internet geladen („Mark of the Web“)
            for p in dateien:
                with open(f"{p}:Zone.Identifier", "w", encoding="ascii") as f:
                    f.write("[ZoneTransfer]\r\nZoneId=3\r\nHostUrl=https://github.com/\r\n")
        elif MAC:                                               # wie mit Safari geladen (Gatekeeper-Quarantäne)
            subprocess.run(["xattr", "-r", "-w", "com.apple.quarantine", f"0083;{int(time.time()):x};Safari;",
                            str(ziel)], capture_output=True, timeout=120)
        return dateien

    def starte(self, ordner, *args, zeit=ZEIT_START):
        """Startdatei wie ein Nutzer (stdin geschlossen: Rückfragen → Standardantwort). → (Code, Protokoll, Sekunden)"""
        t0 = time.time()
        log_datei = ordner.parent / f"start-{int(t0)}.txt"
        datei = ordner / START[ART]
        if self.lokal:
            befehl = self._lokal_befehl(ordner, args)
        elif WIN:
            befehl = f'cmd.exe /d /s /c ""{datei}" {" ".join(args)}"'
        elif MAC:
            befehl = [str(datei), *args]                        # wie der Doppelklick (Startdatei ist ausführbar)
        else:
            befehl = ["sh", str(datei), *args]                  # wie im Leitfaden: sh "Me Goos-ta Deutsch - Linux.sh"
        kw = dict(creationflags=0x00000200) if WIN else dict(start_new_session=True)
        with open(log_datei, "wb") as f:
            p = subprocess.Popen(befehl, stdin=subprocess.DEVNULL, stdout=f, stderr=subprocess.STDOUT, cwd=str(Path.home()),
                                 env=self.env, **kw)
            try:
                code = p.wait(zeit)
            except subprocess.TimeoutExpired:
                if WIN:
                    subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
                else:
                    os.killpg(p.pid, 9)
                code = None
        text = log_datei.read_bytes().decode("utf-8", "replace")
        try:
            log_datei.unlink()
        except OSError:
            pass
        return code, text, time.time() - t0

    def _lokal_befehl(self, ordner, args):
        """Lokal: Startdatei nur mit --status (lädt das frische Python), sonst starter.py im Skript mit umgeleiteten
        Symbolen (UEBERGABE §5) – nie Lukas' echte Verknüpfungen."""
        py = self.daten / "python" / "python.exe"
        if "--status" in args or not py.is_file():
            return f'cmd.exe /d /s /c ""{ordner / START["win"]}" --status"'
        helfer = ordner.parent.parent / "starter_lokal.py"
        helfer.write_text(
            "import os, sys\nfrom pathlib import Path\nprog = Path(sys.argv[1])\nos.environ['MGD_PROGRAMM'] = str(prog)\n"
            "sys.path.insert(0, str(prog))\nimport starter\n"
            "starter.verknuepfungen_ziele = lambda: [Path(sys.argv[2]) / 'Me Goos-ta Deutsch.lnk']\n"
            "sys.exit(starter.main(['--konsole', *sys.argv[3:]]))\n", encoding="utf-8")
        return [str(py), str(helfer), str(ordner / "Programm"), str(self.symbole), *args]

    def instanz(self, ordner, zeit=60):
        frist = time.time() + zeit
        while time.time() < frist:
            for d in sorted(self.daten.glob("laeuft-*.json")):
                j = lies_json(d)
                if j and j.get("projekt") and gleich(j["projekt"], ordner / "Programm"):
                    try:
                        return j, Oberflaeche(j)
                    except (OSError, http.client.HTTPException, Stopp):
                        pass
            time.sleep(1)
        return None, None

    def zeit_um(self):
        return time.time() - T0 > ZEIT_GESAMT

    # ---------- a) Kopieren ----------
    def a_kopieren(self):
        t0 = time.time()
        dateien = self.kopieren(self.o1)
        pruefe(f"Release-Inhalt nach {self.o1} kopiert, Download-Markierung gesetzt ({len(dateien)} Dateien)",
               (self.o1 / START[ART]).is_file() and (self.o1 / "Programm" / "starter.py").is_file(), t0=t0)
        if not WIN:
            fehlt = [n for n in (START["mac"], START["linux"]) if not os.access(self.o1 / n, os.X_OK)]
            pruefe("Startdateien ausführbar (0755 wie im ZIP)", not fehlt, f"nicht ausführbar: {fehlt}")

    # ---------- b) Erster Start ----------
    def b_erster_start(self):
        if self.lokal:                                          # erst nur das frische Python (11 MB), dann der Starter
            code, text, s = self.starte(self.o1, "--status")
            pruefe("Lokal: Startdatei --status lädt das eigene Python", code == 0 and (self.daten / "python").is_dir(),
                   f"Code {code}", protokoll=text)
        code, text, s = self.starte(self.o1, "--kein-browser")
        ok = pruefe(f"Startdatei: Ersteinrichtung ohne Rückfrage, Englisch, Code 0 ({s / 60:.1f} min)",
                    code == 0 and "Setup complete" in text and "Fertig eingerichtet" not in text,
                    f"Code {code}" + ("" if "Setup complete" in text else ", kein „Setup complete“"), protokoll=text)
        if not ok:
            raise Stopp("Ersteinrichtung gescheitert")
        d, self.ui = self.instanz(self.o1)
        pruefe("Oberfläche läuft (Instanzdatei, Cookie + Token wie die Seite)", self.ui is not None,
               f"keine Instanz für {self.o1} in {self.daten}")
        if not self.ui:
            raise Stopp("keine Oberfläche")
        py = Path(d["python"])
        if WIN and py.name.lower() == "pythonw.exe":
            py = py.with_name("python.exe")
        self.python = py
        pruefe("Eigenes Python im Datenordner", gleich(py.parent, self.daten / "python")
               or str(py).startswith(str(self.daten / "python")), str(py))
        self.pakete_pruefen(py)

    def pakete_pruefen(self, py):
        """Seit 2.5: installierte Fassungen = pakete.lock (pip --require-hashes, wie beim Nutzer); im Job „neueste“ nur
        die Fassungen aufzeichnen (Spannen aus requirements.txt)."""
        code = ("import importlib.metadata as m, json, re; print(json.dumps({re.sub(r'[-_.]+', '-', d.metadata['Name'].lower()): "
                "d.version for d in m.distributions()}))")
        r = subprocess.run([str(py), "-c", code], capture_output=True, text=True, timeout=120, env=self.env)
        try:
            ist = json.loads(r.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            ist = {}
        lock = self.quelle / "Programm" / "pakete.lock"
        if self.neueste:
            pruefe("Neueste Paketfassungen (Spannen aus requirements.txt statt Lock): "
                   + ", ".join(f"{n} {ist.get(n, '?')}" for n in ("numpy", "pillow", "reportlab", "pypdfium2")),
                   all(n in ist for n in ("numpy", "pillow", "reportlab")), (r.stderr or str(ist))[-300:])
        elif not lock.is_file():
            pruefe(f"Paketfassungen: Release {self.version} ohne pakete.lock (vor 2.5) – übersprungen", True)
        else:
            soll = {re.sub(r"[-_.]+", "-", n.lower()): v for n, v in
                    re.findall(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==([^\s;\\]+)", lock.read_text(encoding="ascii"), re.M)}
            falsch = {n: (v, ist.get(n)) for n, v in soll.items() if ist.get(n) != v}
            pruefe(f"Paketfassungen genau wie pakete.lock (pip --require-hashes): "
                   + ", ".join(f"{n} {v}" for n, v in sorted(soll.items())), bool(soll) and not falsch,
                   (r.stderr or str(falsch))[-300:])

    # ---------- c) API: Status, Erstabfrage, Tools ----------
    def c_api(self):
        t0 = time.time()
        s, st = self.ui.get("/api/status")
        pruefe(f"/api/status: Version {self.version}, Englisch, Plattform {sys.platform}",
               s == 200 and st.get("version", "").split()[0] == self.version and st.get("sprache") == "en"
               and st.get("plattform") == sys.platform, f"{s} {str(st)[:200]}", t0=t0)
        t1 = time.time()                                            # „Nach neuer Version suchen“: ein echter Abruf bei GitHub
        s, nv = self.ui.post("/api/neue-version", {})
        if s == 200 and nv.get("code") == "nv_grenze":
            pruefe("Nach neuer Version suchen (echter Abruf): Abfrage-Grenze von GitHub erreicht – übersprungen", True, t0=t1)
        elif s == 404 and self.version in ("2.0", "2.1"):              # Release-Prüfung gegen ein Release vor 2.2
            pruefe(f"Nach neuer Version suchen: gibt es in {self.version} noch nicht – übersprungen", True, t0=t1)
        else:
            pruefe("Nach neuer Version suchen (echter Abruf bei api.github.com): Antwort neuer/aktuell/voraus mit Versionsnummer",
                   s == 200 and nv.get("ergebnis") in ("neuer", "aktuell", "voraus")
                   and re.fullmatch(r"\d+\.\d+(\.\d+)?", str(nv.get("version") or "")) is not None
                   and nv.get("eigene") == self.version, f"{s} {str(nv)[:200]}", t0=t1)
        s, ti = self.ui.get("/api/tools")
        nichts = s == 200 and ti.get("erstabfrage") is True and not any(t.get("installiert") for t in ti.get("tools", []))
        pruefe("Tools: nichts vorinstalliert, Erstabfrage offen", nichts, str(ti)[:200])
        s, r = self.ui.post("/api/tools-erstabfrage", {"auswahl": []})
        pruefe("Erstabfrage „ohne Tools“ gemerkt", s == 200 and r.get("erstabfrage") is False, str(r)[:200])
        s, r = self.ui.post("/api/tool", {"id": "lernen", "aktion": "installieren"})
        pruefe("Tool Karten lernen: sofort aktiv", s == 200 and not r.get("lauf") and (r.get("tool") or {}).get("installiert"),
               str(r)[:200])
        for tid, teil, name in (("sprachen", "ru", "Tool Sprachen ru (Schrift, SHA-256)"),
                                ("sprachen", "ar", "Tool Sprachen ar (Schrift + uharfbuzz per pip)"),
                                ("bildverbesserung", None, "Tool Bildverbesserung (Real-ESRGAN ×4, 64 MB)")):
            t0 = time.time()
            s, r = self.ui.post("/api/tool", dict(id=tid, aktion="installieren", **({"teil": teil} if teil else {})))
            lid = (r.get("lauf") or {}).get("id")
            st = self.ui.warte_lauf(lid, 900) if s == 200 and lid else None
            pruefe(f"{name} über die Warteschlange", st is not None and st.get("code") == 0,
                   f"{s} {str(r)[:160]}" if not st else f"Code {st.get('code')}", t0=t0,
                   protokoll="\n".join((st or {}).get("zeilen") or []))
        s, ti = self.ui.get("/api/tools")
        tools = {t["id"]: t for t in ti.get("tools", [])} if s == 200 else {}
        teile = {x["id"]: x.get("installiert") for x in (tools.get("sprachen") or {}).get("teile", [])}
        x4 = {x["id"]: x.get("installiert") for x in (tools.get("bildverbesserung") or {}).get("teile", [])}.get("x4")
        hb = any(p.name.startswith("uharfbuzz") for p in (self.daten / "sprachen" / "_pakete").glob("*"))
        pruefe("Tools installiert: lernen, sprachen (ru, ar), bildverbesserung (x4); uharfbuzz in Daten/sprachen/_pakete",
               all((tools.get(t) or {}).get("installiert") for t in ("lernen", "sprachen", "bildverbesserung"))
               and teile.get("ru") and teile.get("ar") and x4 and hb,
               f"{ {t: (tools.get(t) or {}).get('installiert') for t in tools} } ru={teile.get('ru')} ar={teile.get('ar')} "
               f"x4={x4} uharfbuzz={hb}")

    # ---------- d) Erzeugen ----------
    def d_erzeugen(self):
        prog = self.o1 / "Programm"
        # Neue Karte wie in Schritt 1 (Bild hochladen → prüfen → übernehmen): ein kleines Bild, damit Real-ESRGAN rechnet
        t0 = time.time()
        self.ui.get("/api/karten")                              # legt beim ersten Mal karten.csv + bilder/ an
        quelle = sorted((prog / "beispiel-bilder").glob("*.jpg"))[:1]
        klein = self.o1.parent / "gans-klein.jpg"
        if quelle:
            subprocess.run([str(self.python), "-c", "import sys; from PIL import Image; im = Image.open(sys.argv[1]).convert('RGB'); "
                            "im.thumbnail((260, 260)); im.save(sys.argv[2], quality=92)", str(quelle[0]), str(klein)],
                           capture_output=True, timeout=120, env=self.env)
        s, e = self.ui.post_roh("/api/entwurf?name=gans-klein.jpg", klein.read_bytes() if klein.is_file() else b"", "image/jpeg")
        s2, u = self.ui.post("/api/entwurf-uebernehmen", {"id": e.get("id"), "de": "Gans klein", "es": "pequeño"}) \
            if s == 200 else (s, e)
        neu = e.get("dateiname") or "gans-klein.jpg"
        pruefe("Neue Karte über Entwurf (Bild hochladen, prüfen, übernehmen)",
               s == 200 and s2 == 200 and (prog / "bilder" / neu).is_file(), f"{s} {str(e)[:120]} · {s2} {str(u)[:120]}", t0=t0)
        # Real-ESRGAN wirklich rechnen lassen (das kleine Bild), danach Druck mit FSRCNN (schnell auf jedem Runner)
        t0 = time.time()
        self.ui.post("/api/einstellungen", {"werte": {"ki": "realesrgan"}})
        s, r = self.ui.post("/api/lauf", {"art": "verbessern", "bilder": [neu]})
        st = self.ui.warte_lauf(r.get("id"), 1200) if s == 200 and r.get("id") else None
        cache = [lies_json(j) or {} for j in (prog / "ausgabe" / ".cache").glob("*.json")]
        pruefe("Bildverbesserung mit Real-ESRGAN ×4 (neue Karte, 260 px)", st is not None and st.get("code") == 0
               and any(str(c.get("ki", "")).startswith("realesrgan") and c.get("bild") == neu for c in cache),
               f"{s} {str(r)[:120]} · Code {(st or {}).get('code')} · {[c.get('ki') for c in cache if c.get('bild') == neu]}",
               t0=t0, protokoll="\n".join((st or {}).get("zeilen") or []))
        self.ui.post("/api/einstellungen", {"werte": {"ki": "fsrcnn"}})
        s, kd = self.ui.get("/api/karten")
        karten = kd.get("karten", []) if s == 200 else []
        gueltig = [k for k in karten if k.get("aktiv") and k.get("existiert")]
        self.karten = len(gueltig)
        for i, k in enumerate(karten):
            rs = dict(k.get("rueckseiten") or {})
            rs.update(ar=f"إوزة عجوز {i + 1}", ru=f"старый гусь {i + 1}")
            k["rueckseiten"] = rs
        self.ar_text = "إوزة عجوز 1"
        s, r = self.ui.post("/api/karten", {"karten": karten})
        csv = (prog / "karten.csv").read_text(encoding="utf-8-sig") if (prog / "karten.csv").is_file() else ""
        pruefe(f"Karten ({self.karten}) mit Rückseiten ar + ru gespeichert (karten.csv)",
               s == 200 and self.karten >= 5 and self.ar_text in csv and "старый гусь" in csv and neu in csv,
               f"{s} {str(r)[:160]}")
        aus = prog / "ausgabe"
        for code in ("es", "ar", "ru"):
            t0 = time.time()
            s, r = self.ui.post("/api/lauf", {"art": "generator", "nur": "alles", "sprache": code})
            st = self.ui.warte_lauf(r.get("id"), 900) if s == 200 and r.get("id") else None
            e = "" if code == "es" else f"_{code}"
            dr = sorted(aus.glob(f"*_Druckerei_*{e}.pdf"))
            dr = [p for p in dr if code != "es" or not re.search(r"_[a-z]{2,3}\.pdf$", p.name)]
            bo = [p for p in sorted(aus.glob(f"*_Heimdruck_*{e}.pdf"))
                  if code != "es" or not re.search(r"_[a-z]{2,3}\.pdf$", p.name)]
            pb = aus / f"{NAME}_Pruefbogen{e}.pdf"
            seiten = self.seiten([*dr[:1], *bo[:1], pb]) if dr and bo and pb.is_file() else None
            bericht = lies_json(aus / "bericht.json") or {}
            fehler = [m for m in bericht.get("meldungen", []) if isinstance(m, dict) and m.get("stufe") == "fehler"]
            ok = (st is not None and st.get("code") == 0 and seiten is not None and seiten[0] == 2 * self.karten
                  and seiten[1] > 0 and seiten[1] % 2 == 0 and seiten[2] > 0 and bericht.get("sprache") == code
                  and not fehler and bericht.get("erzeugt"))
            pruefe(f"Alles zum Drucken ({code}): Druckerei 2 Seiten je Karte, Heimdruck, Prüfbogen, bericht.json ohne Fehler",
                   ok, f"Code {(st or {}).get('code')} · Seiten {seiten} (soll {2 * self.karten}, gerade, >0) · "
                       f"Sprache {bericht.get('sprache')} · Fehler {fehler[:2]} · Dateien {[p.name for p in dr + bo]}",
                   t0=t0, protokoll="\n".join((st or {}).get("zeilen") or []))
        t0 = time.time()
        s, r = self.ui.post("/api/lauf", {"art": "generator", "nur": "digital"})
        st = self.ui.warte_lauf(r.get("id"), 600) if s == 200 and r.get("id") else None
        apkg = sorted((aus / "digital").glob("*.apkg"))
        anki = False
        if apkg:
            try:
                with zipfile.ZipFile(apkg[0]) as z:
                    anki = "collection.anki2" in z.namelist()
            except (OSError, zipfile.BadZipFile):
                pass
        pruefe("Digitale Lernkarten: .apkg ist ZIP mit collection.anki2, Lernseite da",
               st is not None and st.get("code") == 0 and anki and any((aus / "digital").glob("*_Lernseite*.html")),
               f"Code {(st or {}).get('code')} · {[p.name for p in (aus / 'digital').glob('*')][:8]}", t0=t0,
               protokoll="\n".join((st or {}).get("zeilen") or []))

    def seiten(self, pdfs):
        """Seitenzahlen über pypdfium2 des installierten Pythons."""
        r = subprocess.run([str(self.python), "-c", "import sys, pypdfium2 as p; print(*[len(p.PdfDocument(f)) for f in sys.argv[1:]])",
                            *map(str, pdfs)], capture_output=True, text=True, timeout=120, env=self.env)
        try:
            return [int(x) for x in r.stdout.split()]
        except ValueError:
            return None

    # ---------- e) Lernen ----------
    def e_lernen(self):
        s, k = self.ui.get("/api/lernen-karte")
        kid = ((k.get("karte") or {}).get("id")) if s == 200 else None
        s1, b = self.ui.post("/api/lernen-bewerten", {"id": kid, "note": 3, "dauer_ms": 1500}) if kid else (0, {})
        s2, z = self.ui.post("/api/lernen-rueckgaengig", {}) if kid else (0, {})
        s3, b2 = self.ui.post("/api/lernen-bewerten", {"id": kid, "note": 3, "dauer_ms": 1200}) if kid else (0, {})
        stand = lies_json(self.o1 / "Programm" / "lernstand.json") or {}
        self.lern_id = kid
        pruefe("Lernen: Karte bewerten, Rückgängig, erneut bewerten (lernstand.json)",
               kid and s1 == 200 and s2 == 200 and z.get("id") == kid and s3 == 200 and kid in json.dumps(stand),
               f"Karte {kid} · {s1}/{s2}/{s3} · {str(z)[:120]}")

    # ---------- f) Testreihen mit dem installierten Python ----------
    def f_tests(self, ordner):
        if self.ohne_tests:
            log("· Testreihen übersprungen (--ohne-tests)")
            return
        prog = ordner / "Programm"
        env = dict(self.env, PYTHONIOENCODING="utf-8")
        for datei, haupt in (("test_erweiterungen.py", False), ("test_gans_lernkarten.py", True)):
            rest = ZEIT_GESAMT - (time.time() - T0) - 180
            if rest < 120:
                pruefe(f"Testreihe {datei}", False, "Zeit um – übersprungen")
                continue
            t0 = time.time()
            try:
                r = subprocess.run([str(self.python), "-u", datei], cwd=str(prog), env=env, stdin=subprocess.DEVNULL,
                                   capture_output=True, timeout=min(rest, 25 * 60))
                text = (r.stdout + r.stderr).decode("utf-8", "replace")
            except subprocess.TimeoutExpired as e:
                text = ((e.stdout or b"") + (e.stderr or b"")).decode("utf-8", "replace") + "\n… Zeitlimit"
            gruen = "ALLE TESTS BESTANDEN" in text
            fehl = sorted(set(m.group(1).strip() for m in re.finditer(r"^\s*FEHLER\s{2}(.+?)(?:\s{2}\(.*)?$", text, re.M)))
            zahl = re.findall(r"(\d+) von (\d+)", text)
            bekannt = None
            if not gruen and haupt and fehl and all((self.system, f) in BEKANNT for f in fehl):
                bekannt = "; ".join(f"{f}: {BEKANNT[(self.system, f)]}" for f in fehl)
            pruefe(f"Testreihe {datei} mit dem installierten Python" + (f" ({zahl[-1][0]} von {zahl[-1][1]})" if zahl else ""),
                   gruen or bool(bekannt), "; ".join(fehl)[:500] or "kein „ALLE TESTS BESTANDEN“", t0=t0,
                   protokoll=text, bekannt=bekannt)

    # ---------- g) Zweiter Start, --status ----------
    def g_zweiter_start(self):
        code, text, s = self.starte(self.o1, "--kein-browser", zeit=120)
        pruefe(f"Zweiter Start: „läuft schon“ in {s:.1f} s (< 15 s)",
               code == 0 and "already running" in text and s < 15, f"Code {code}", protokoll=text)
        code, text, s = self.starte(self.o1, "--status", zeit=120)
        pruefe("--status auf Englisch (Programmordner, Oberfläche)",
               code == 0 and "Program folder:" in text and "Programmordner" not in text and "Interface: http" in text,
               f"Code {code}", protokoll=text)

    # ---------- h) Update in einen neuen Ordner ----------
    def h_update(self):
        t0 = time.time()
        if not self.lokal:
            self.k_vorbereiten()                                # die Oberfläche von o2 kennt dann den Release-Server
        self.kopieren(self.o2)
        code, text, s = self.starte(self.o2, "--kein-browser")
        prog = self.o2 / "Programm"
        csv = (prog / "karten.csv").read_text(encoding="utf-8-sig") if (prog / "karten.csv").is_file() else ""
        stand = (prog / "lernstand.json").read_text(encoding="utf-8") if (prog / "lernstand.json").is_file() else ""
        ort = (self.daten / "programm-ort.txt").read_text(encoding="utf-8").strip() if (self.daten / "programm-ort.txt").is_file() else ""
        pruefe("Update-Weg: neuer Ordner → Kartenübernahme (Standardantwort Ja), Karten + Lernstand + Real-ESRGAN da",
               code == 0 and "Taken over:" in text and bool(self.ar_text) and self.ar_text in csv
               and bool(self.lern_id) and self.lern_id in stand and (prog / "modelle" / "realesrgan-x4plus.npz").is_file()
               and gleich(ort, prog),
               f"Code {code} · übernommen {'Taken over:' in text} · ar {bool(self.ar_text and self.ar_text in csv)} · "
               f"Lernstand {bool(self.lern_id and self.lern_id in stand)} · Modell "
               f"{(prog / 'modelle' / 'realesrgan-x4plus.npz').is_file()} · Ort {ort}", t0=t0, protokoll=text)
        alt, _ = self.instanz(self.o1, zeit=3)
        d, self.ui = self.instanz(self.o2)
        pruefe("Nach dem Update: Oberfläche des neuen Ordners läuft, die alte ist beendet", self.ui is not None and not alt,
               f"neu {bool(self.ui)} · alt noch da {bool(alt)}")
        if not self.ui:
            raise Stopp("keine Oberfläche nach dem Update")

    # ---------- k) Update direkt im Programm (seit 2.4) ----------
    def k_vorbereiten(self):
        """Wie ein GitHub-Release v9.9 (ZIP + SHA256SUMS.txt + SHA256SUMS.txt.minisig) auf 127.0.0.1: Inhalt = dieses
        Release, nur VERSION 9.9 und eine Merkdatei. Die Oberfläche lädt dort statt bei GitHub (MGD_UPDATE_QUELLE, nur
        127.0.0.1). Seit 2.5 signiert mit einem Testschlüssel dieses Laufs (MGD_UPDATE_TESTSCHLUESSEL); v9.8 trägt die
        Signatur eines fremden Schlüssels und muss abgelehnt werden."""
        import functools
        import hashlib
        import http.server
        import threading
        ziel = Path.home() / "mgd-update"
        shutil.rmtree(ziel, ignore_errors=True)
        (ziel / "v9.9").mkdir(parents=True)
        zip_pfad = ziel / "v9.9" / f"{NAME}-9.9.zip"
        with zipfile.ZipFile(zip_pfad, "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(self.quelle.rglob("*")):
                rel = p.relative_to(self.quelle).as_posix()
                if (not p.is_file() or rel.split("/")[0] in (".git", ".github", ".gitattributes", "web-app")
                        or rel.startswith("ergebnis") or "__pycache__" in rel):
                    continue
                daten = p.read_bytes()
                if rel == "Programm/gans_lernkarten.py":
                    daten = re.sub(rb'^VERSION = "[^"]+"', b'VERSION = "9.9 (01.01.2030)"', daten, count=1, flags=re.M)
                info = zipfile.ZipInfo(f"{NAME}/{rel}", (2026, 1, 1, 0, 0, 0))
                info.create_system, info.compress_type = 3, zipfile.ZIP_DEFLATED
                info.external_attr = (0o100755 if p.suffix in (".sh", ".command") else 0o100644) << 16
                z.writestr(info, daten)
            z.writestr(f"{NAME}/Programm/update_probe.txt", "9.9\n")
        sha = hashlib.sha256(zip_pfad.read_bytes()).hexdigest()
        summen = f"{sha}  {NAME}-9.9.zip\n".encode("utf-8")
        (ziel / "v9.9" / "SHA256SUMS.txt").write_bytes(summen)
        sg = self.signatur_modul()
        self.signiert = sg is not None
        if sg:
            import secrets
            seed, sid = secrets.token_bytes(32), secrets.token_bytes(8)
            (ziel / "v9.9" / "SHA256SUMS.txt.minisig").write_bytes(sg.signiere(seed, sid, summen, sg.KOMMENTAR.format(version="9.9")))
            self.env["MGD_UPDATE_TESTSCHLUESSEL"] = sg.schluessel_text(sid, sg.ed25519_oeffentlich(seed))
            (ziel / "v9.8").mkdir()
            shutil.copyfile(zip_pfad, ziel / "v9.8" / f"{NAME}-9.8.zip")
            summen8 = f"{sha}  {NAME}-9.8.zip\n".encode("utf-8")
            (ziel / "v9.8" / "SHA256SUMS.txt").write_bytes(summen8)
            (ziel / "v9.8" / "SHA256SUMS.txt.minisig").write_bytes(
                sg.signiere(secrets.token_bytes(32), secrets.token_bytes(8), summen8, sg.KOMMENTAR.format(version="9.8")))
            if shutil.which("minisign"):
                self.k_minisign(sg, ziel / "minisign")

        class Leise(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *a):
                pass
        self.update_server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Leise, directory=str(ziel)))
        threading.Thread(target=self.update_server.serve_forever, daemon=True).start()
        self.env["MGD_UPDATE_QUELLE"] = f"http://127.0.0.1:{self.update_server.server_address[1]}"
        log(f"· Release-Server für das Update im Programm: {self.env['MGD_UPDATE_QUELLE']} (ZIP {zip_pfad.stat().st_size // 1024} KB)")

    def signatur_modul(self):
        """Programm/signatur.py dieses Releases (seit 2.5) – oder None (ältere Releases ohne Signatur)."""
        pfad = self.quelle / "Programm" / "signatur.py"
        if not pfad.is_file():
            return None
        import importlib.util
        spec = importlib.util.spec_from_file_location("signatur_frischtest", pfad)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def k_minisign(self, sg, ordner):
        """Gegenprobe mit dem echten minisign (Linux, apt): unsere Signatur prüft minisign, minisigns Signatur prüft
        signatur.py – beide Richtungen, „trusted comment“ inklusive."""
        import secrets
        import subprocess as sp
        t0 = time.time()
        ordner.mkdir(parents=True, exist_ok=True)
        datei = ordner / "SHA256SUMS.txt"
        datei.write_bytes(b"0" * 64 + f"  {NAME}-9.9.zip\n".encode("utf-8"))
        seed, sid = secrets.token_bytes(32), secrets.token_bytes(8)
        (ordner / "SHA256SUMS.txt.minisig").write_bytes(sg.signiere(seed, sid, datei.read_bytes(), "me-goos-ta-deutsch v9.9"))
        (ordner / "unser.pub").write_text(sg.pub_datei(sid, sg.ed25519_oeffentlich(seed)), encoding="utf-8")
        r1 = sp.run(["minisign", "-V", "-m", str(datei), "-p", str(ordner / "unser.pub")], capture_output=True, text=True, timeout=60)
        r2 = sp.run(["minisign", "-G", "-W", "-f", "-p", str(ordner / "ms.pub"), "-s", str(ordner / "ms.key")],
                    capture_output=True, text=True, timeout=60)
        r3 = sp.run(["minisign", "-S", "-s", str(ordner / "ms.key"), "-m", str(datei), "-x", str(ordner / "ms.minisig"),
                     "-t", "me-goos-ta-deutsch v9.9"], capture_output=True, text=True, timeout=60)
        try:
            k = sg.schluessel_lesen((ordner / "ms.pub").read_text(encoding="utf-8"))
            zurueck = sg.pruefe(datei.read_bytes(), (ordner / "ms.minisig").read_bytes(), [("minisign", *k)], "me-goos-ta-deutsch v9.9")
        except (OSError, ValueError) as f:
            zurueck = f"✗ {f}"
        pruefe("Signatur minisign-kompatibel: minisign -V prüft unsere Signatur, signatur.py prüft die von minisign",
               r1.returncode == 0 and "me-goos-ta-deutsch v9.9" in r1.stdout + r1.stderr and r2.returncode == 0
               and r3.returncode == 0 and isinstance(zurueck, dict),
               f"V {r1.returncode} {(r1.stdout + r1.stderr)[-160:]} · G {r2.returncode} {r2.stderr[-120:]} · "
               f"S {r3.returncode} {r3.stderr[-120:]} · zurück {zurueck}", t0=t0)

    def k_update_im_programm(self):
        if self.lokal or not self.update_server:
            log("· Lokal: Update im Programm entfällt (der Neustart über die Startdatei legt echte Symbole an) – E48 prüft die Teile")
            return
        t0 = time.time()
        prog = self.o2 / "Programm"
        if self.signiert:
            s0, l0 = self.ui.post("/api/update", {"aktion": "laden", "version": "9.8"})
            f0 = self.ui.warte_lauf(l0.get("id"), 300) if s0 == 200 and l0.get("id") else None
            zeilen0 = "\n".join((f0 or {}).get("zeilen", []))
            s, st = self.ui.get("/api/status")
            pruefe("Update im Programm: Release mit fremder Signatur (9.8) → abgelehnt, nichts bereit",
                   s0 == 200 and f0 and f0.get("code") != 0 and "fremder_schluessel" in zeilen0
                   and not (st.get("update") or {}).get("bereit"),
                   f"{s0} · Code {f0 and f0.get('code')} · {zeilen0[-200:]}", t0=t0)
            t0 = time.time()
        s, st = self.ui.get("/api/status")
        moeglich = (st.get("update") or {}).get("moeglich")
        s1, l = self.ui.post("/api/update", {"aktion": "laden", "version": "9.9"})
        fertig = self.ui.warte_lauf(l.get("id"), 600) if s1 == 200 and l.get("id") else None
        s, st = self.ui.get("/api/status")
        bereit = (st.get("update") or {}).get("bereit")
        ok = pruefe("Update im Programm: „Jetzt aktualisieren“ lädt 9.9 (Prüfsumme, ZIP geprüft) → bereit, im selben Ordner möglich",
                    s1 == 200 and moeglich is True and fertig and fertig.get("code") == 0 and bereit == "9.9",
                    f"{s1} {str(l)[:120]} · möglich {moeglich} · Code {fertig and fertig.get('code')} · bereit {bereit}", t0=t0,
                    protokoll="\n".join((fertig or {}).get("zeilen", [])))
        if not ok:
            return
        vorher = {n: (prog / n).read_bytes() for n in ("karten.csv", "lernstand.json", "ui_einstellungen.json") if (prog / n).is_file()}
        bilder = sorted(p.name for p in (prog / "bilder").glob("*"))
        alt, _ = self.instanz(self.o2, zeit=5)
        t1 = time.time()
        s2, r = self.ui.post("/api/update", {"aktion": "anwenden"})
        neu, ui = None, None
        frist = time.time() + 15 * 60
        while time.time() < frist:
            d, o = self.instanz(self.o2, zeit=5)
            if d and (not alt or d.get("pid") != alt.get("pid")):
                neu, ui = d, o
                break
            time.sleep(3)
        if ui:
            self.ui = ui
        s, st = self.ui.get("/api/status") if ui else (0, {})
        erg = (st.get("update") or {}).get("ergebnis") or {}
        ordner = sorted(p.name for p in self.o2.parent.iterdir() if p.is_dir())
        pruefe("… „Jetzt neu starten“: alte Oberfläche endet, Programmdateien im selben Ordner ersetzt, Neustart über die "
               "Startdatei → Version 9.9, Ergebnis „ok“ gemeldet",
               s2 == 200 and ui is not None and st.get("version", "").split()[0] == "9.9" and erg.get("ok") is True
               and (prog / "update_probe.txt").is_file() and ordner == [NAME],
               f"{s2} {str(r)[:120]} · neu {bool(ui)} · Version {st.get('version')} · Ergebnis {erg} · Ordner {ordner}", t0=t1)
        pruefe("… eigene Daten unverändert (Kartenliste, Lernstand, Einstellungen, Bilder), Zwischenstand aufgeräumt",
               all((prog / n).read_bytes() == b for n, b in vorher.items()) and sorted(p.name for p in (prog / "bilder").glob("*")) == bilder
               and not (self.daten / "update" / "neu").exists() and not (self.daten / "update" / "bereit.json").exists(),
               f"gleich {[n for n, b in vorher.items() if (prog / n).is_file() and (prog / n).read_bytes() == b]} · "
               f"Bilder {len(bilder)} · neu/ {(self.daten / 'update' / 'neu').exists()}")
        if ui:
            self.ui.post("/api/update", {"aktion": "gesehen"})

    # ---------- j) Plattform: Symbole, App, Menüeintrag ----------
    def j_plattform(self):
        ziele = self.symbol_ziele()
        if WIN:
            fehlt = [str(z) for z in ziele if not z.is_file()]
            info = ""
            if not fehlt:
                r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command",
                                    "$s = (New-Object -ComObject WScript.Shell).CreateShortcut($env:MGD_LNK); "
                                    "$s.TargetPath; $s.Arguments"], capture_output=True, text=True, timeout=60,
                                   env=dict(os.environ, MGD_LNK=str(ziele[0])))
                info = r.stdout.strip()
            ort = (self.daten / "programm-ort.txt").read_text(encoding="utf-8").strip() if (self.daten / "programm-ort.txt").is_file() else ""
            pruefe(f"Windows: Verknüpfungen ({len(ziele)}) → pythonw.exe starte.py, Ort = neuer Ordner",
                   not fehlt and len(ziele) >= 1 and "pythonw.exe" in info.lower() and "starte.py" in info
                   and gleich(ort, self.o2 / "Programm"), f"fehlt {fehlt} · {info[:200]} · Ort {ort}")
            markiert = [p.name for p in [*self.o2.glob("*.cmd"), *(self.o2 / "Programm").rglob("*.py")]
                        if os.path.exists(f"{p}:Zone.Identifier")]
            pruefe("Windows: Download-Markierung von Startdatei und Programmdateien entfernt", not markiert, str(markiert[:5]))
        elif MAC:
            app = ziele[0]
            info = app / "Contents" / "Info.plist"
            r = subprocess.run(["plutil", "-lint", str(info)], capture_output=True, text=True, timeout=60) if info.is_file() else None
            import plistlib
            try:
                with open(info, "rb") as f:
                    pl = plistlib.load(f)
            except (OSError, ValueError):
                pl = {}
            pruefe("macOS: App in ~/Applications, plutil -lint ok, Name + Version stimmen",
                   r is not None and r.returncode == 0 and pl.get("CFBundleName") == "Me Goos-ta Deutsch"
                   and str(pl.get("CFBundleShortVersionString")) == self.version.split(".")[0] + "." + self.version.split(".")[1],
                   f"{(r.stdout + r.stderr).strip()[:200] if r else 'Info.plist fehlt'} · {pl.get('CFBundleShortVersionString')}")
            r = subprocess.run(["xattr", "-lr", str(self.o2 / "Programm")], capture_output=True, text=True, timeout=120)
            pruefe("macOS: Quarantäne von den Programmdateien entfernt", "com.apple.quarantine" not in r.stdout,
                   r.stdout[:200])
        else:
            eintrag = ziele[0]
            werkzeug = shutil.which("desktop-file-validate")
            if not eintrag.is_file():
                pruefe("Linux: Menüeintrag angelegt", False, f"fehlt: {eintrag}")
            elif werkzeug:
                r = subprocess.run([werkzeug, str(eintrag)], capture_output=True, text=True, timeout=60)
                pruefe("Linux: Menüeintrag, desktop-file-validate ohne Befund", r.returncode == 0 and not r.stdout.strip(),
                       (r.stdout + r.stderr).strip()[:300])
            else:
                pruefe("Linux: Menüeintrag angelegt (desktop-file-validate nicht vorhanden – übersprungen)", True)

    # ---------- i) Deinstallieren ----------
    def i_deinstallieren(self):
        prog = self.o2 / "Programm"
        s, r = self.ui.post("/api/tool", {"id": "bildverbesserung", "aktion": "deinstallieren"})
        weg = not (prog / "modelle" / "realesrgan-x4plus.npz").exists() and not (self.daten / "modelle" / "realesrgan-x4plus.npz").exists()
        pruefe("Tool Bildverbesserung deinstallieren: Modell im Programm- und Datenordner weg", s == 200 and weg,
               f"{s} {str(r)[:160]}")
        if self.lokal:                                         # die echte Deinstallation würde echte Symbole entfernen
            s, _ = self.ui.post("/api/beenden", {})
            log("· Lokal: Programm-Deinstallation entfällt (Oberfläche beendet)")
            return
        t0 = time.time()
        ziele = self.symbol_ziele()
        s, r = self.ui.post("/api/deinstallieren", {"bestaetigt": True})
        frist, geschlossen = time.time() + 120, 0
        while time.time() < frist and (self.daten.exists() or self.o2.exists() or any(z.exists() for z in ziele)):
            geschlossen += schliesse_hinweis("Me Goos-ta Deutsch – Uninstall")   # „Nach OK dauert es noch …“
            time.sleep(2)
        pruefe("Programm deinstallieren: Datenordner, Programmordner und Symbole/App/Menüeintrag weg",
               s == 200 and not self.daten.exists() and not self.o2.exists() and not any(z.exists() for z in ziele),
               f"{s} {str(r)[:120]} · Daten {self.daten.exists()} · Ordner {self.o2.exists()} · "
               f"Symbole {[str(z) for z in ziele if z.exists()]} · Hinweisfenster geschlossen: {geschlossen}", t0=t0)

    def lauf(self):
        stufen = [("a", self.a_kopieren), ("b", self.b_erster_start), ("c", self.c_api), ("d", self.d_erzeugen),
                  ("e", self.e_lernen), ("g", self.g_zweiter_start), ("h", self.h_update), ("j", self.j_plattform),
                  ("f", lambda: self.f_tests(self.o2)), ("k", self.k_update_im_programm), ("i", self.i_deinstallieren)]
        for kurz, fn in stufen:
            if self.zeit_um():
                pruefe(f"Stufe {kurz}", False, "Zeitlimit des Frischtests erreicht – übersprungen")
                continue
            try:
                fn()
            except Stopp as e:
                pruefe(f"Stufe {kurz}", False, f"abgebrochen: {e}")
                break
            except Exception as e:  # noqa: BLE001 – jede Ausnahme wird eine benannte, gescheiterte Prüfung
                import traceback
                pruefe(f"Stufe {kurz}", False, f"{type(e).__name__}: {e}", protokoll=traceback.format_exc())
                if kurz in ("a", "b", "h"):
                    break


def main(argv):
    for strom in (sys.stdout, sys.stderr):                      # Windows-Runner schreiben sonst cp1252 (✓ ✗ → Fehler)
        try:
            strom.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    def wert(name, standard=None):
        return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else standard
    lokal = wert("--lokal")
    if lokal:
        if not WIN:
            sys.exit("✗ --lokal gibt es nur unter Windows (Lukas' Rechner).")
        quelle = Path(wert("--quelle", "")).resolve() if wert("--quelle") else None
        if not quelle or not (quelle / START["win"]).is_file():
            sys.exit("✗ --lokal braucht --quelle <Release-Ordner Me-Goos-ta-Deutsch>.")
        t = Path(lokal).resolve()
        temp = os.path.normcase(os.path.abspath(os.environ.get("TEMP", "") or "?"))
        if os.path.normcase(str(t)).startswith(temp) or len(str(t)) > 40 or t.exists() and any(t.iterdir()):
            sys.exit(f"✗ Testordner muss kurz, außerhalb von Temp und leer sein: {t}")
        system = "lokal-windows"
    else:
        if os.environ.get("GITHUB_ACTIONS") != "true":
            sys.exit("✗ Verweigert: Die echte Startdatei läuft nur auf GitHub-Rechnern (GITHUB_ACTIONS=true). "
                     "Lokal: --lokal <Testordner> --quelle <Release-Ordner>.")
        quelle = Path(__file__).resolve().parents[2]
        if "--neuestes-release" in argv:                        # Release-Prüfung: das veröffentlichte Release (Prüfsumme)
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import neuestes_release
            try:
                r = neuestes_release.laden(Path.home() / "mgd-release", neuestes_release.repo_von(quelle), quelle)
            except (OSError, ValueError) as f:
                sys.exit(f"✗ Release nicht geladen: {f}")
            log(f"Release {r['version']} geladen ({r['name']}, SHA-256 {r['sha256'][:16]}… = SHA256SUMS.txt, {r['signatur']})")
            quelle = Path(r["ordner"])
        system = wert("--system", f"{ART}-{platform.machine().lower()}")
        t = None
    ergebnis = Path(wert("--ergebnis", "ergebnis.json")).resolve()
    log(f"Frischtest {system} · {platform.platform()} · {platform.machine()} · Dirigent Python {platform.python_version()}")
    ft = Frischtest(system, quelle, lokal=t, ohne_tests="--ohne-tests" in argv, neueste="--neueste-pakete" in argv)
    try:
        ft.lauf()
    finally:
        ok = bool(ERG) and all(e["ok"] for e in ERG)
        ergebnis.write_text(json.dumps(dict(
            system=system, ok=ok, version=ft.version, plattform=platform.platform(), maschine=platform.machine(),
            kerne=os.cpu_count(), dirigent=platform.python_version(), dauer=round(time.time() - T0),
            lauf=os.environ.get("GITHUB_RUN_ID"), pruefungen=ERG), ensure_ascii=False, indent=1), encoding="utf-8")
        if t is not None and "--behalten" not in argv:
            time.sleep(2)
            shutil.rmtree(t, ignore_errors=True)
    bestanden = sum(1 for e in ERG if e["ok"])
    log(f"{'✓ FRISCHTEST BESTANDEN' if ok else '✗ FRISCHTEST NICHT BESTANDEN'} · {bestanden}/{len(ERG)} · "
        f"{(time.time() - T0) / 60:.1f} min")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
