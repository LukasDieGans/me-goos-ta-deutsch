#!/usr/bin/env python3
"""Browser-Test von Me Goos-ta Deutsch (seit 2.2): Oberfläche, Web-App, Download-Seite und Anleitungen in echten
Browser-Engines unter Playwright – WebKit (die Engine von Safari), Firefox und Chromium, im Rechner- und im Handy-Format.
Keine Person nötig, nichts zum Anklicken. Playwright (Apache-2.0) gibt es nur hier im CI, nie im Programm/Release.

GitHub Actions (Branch ci, Job browser; Release-Ordner + web-app/ im Checkout):
    python .github/ci/browser_test.py --system browser-linux --engines chromium,firefox,webkit [--ergebnis ergebnis.json]
Nach jedem Push auf main gegen das veröffentlichte Release (release_pruefung.yml; Stufe A + B2 gegen die Live-Adressen; das Release-ZIP
wird geladen und gegen SHA256SUMS.txt geprüft – bzw. --quelle <entpacktes Release>):
    python .github/ci/browser_test.py --live --neuestes-release --engines … [--stufen A,B2]
Lokal (Fehlersuche, mit dem installierten Chrome; Playwright nur in einem Wegwerf-Ordner): --engines chromium --kanal chrome

Stufen: A statische Seiten (Download-Seite mit Sprache + Systemerkennung, Installationsseiten, LIES MICH; file://),
B1 Oberfläche am Rechner (gans_ui.py auf einer Kopie mit eigenem Datenordner), B2 Web-App (statischer Server unter
/me-goos-ta-deutsch/ wie GitHub Pages: Service Worker, Pyodide, Drucken, Lernen, Sicherung, offline). Die Abläufe stehen in
ABLAEUFE – spätere Gruppen hängen neue an. Ergebnis wie frischtest.py: ergebnis.json (Prüfungen mit Name, ok, Grund,
Dauer) und Exit-Code 0/1. Feste Wartezeiten höchstens 2 s – sonst wird auf einen Zustand der Seite gewartet."""
import base64
import functools
import hashlib
import http.server
import io
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import zipfile
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[2]                     # Checkout: Release-Ordner (+ web-app/)
UNTERORDNER = "/me-goos-ta-deutsch/"                             # wie GitHub Pages (Projektseite)
ENGINES = ("chromium", "firefox", "webkit")
INSTALLATIONSSEITEN = ("Me Goos-ta Deutsch - Android.html", "Me Goos-ta Deutsch - iPhone.html",
                       "Me Goos-ta Deutsch - Google Pixel.html")
LIES_MICH = "LIES MICH ZUERST.html"
ZEIT_APP = 300_000                                               # erster Start der Web-App (Pyodide) höchstens, ms
ZEIT = 60_000                                                    # sonst je Schritt höchstens, ms
KANAL: dict = {}                                                 # --kanal chrome|msedge: lokal ohne Playwright-Download
# Konsolenmeldungen der Stufe „error“, die kein Fehler des Programms sind: [(Regex, Grund)] – Programmfehler nie.
ERLAUBT: list = []
# Systemerkennung der Download-Seite: (User-Agent, navigator.platform, erwartet)
GERAETE_UA = {
    "Windows": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 "
                "Safari/537.36", "Win32", "win"),
    "macOS": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 "
              "Safari/605.1.15", "MacIntel", "mac"),
    "Linux": ("Mozilla/5.0 (X11; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0", "Linux x86_64", "linux"),
    "iPhone": ("Mozilla/5.0 (iPhone; CPU iPhone OS 26_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
               "Version/26.0 Mobile/15E148 Safari/604.1", "iPhone", "handy"),
    "Android": ("Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile "
                "Safari/537.36", "Linux armv81", "handy"),
}
# navigator.platform/maxTouchPoints/userAgentData passend zum User-Agent (sonst gelten die Werte des Test-Rechners –
# z. B. ein Laptop mit Touchscreen sähe mit Mac-Kennung aus wie ein iPad)
PLATTFORM_JS = ("Object.defineProperty(Navigator.prototype, 'platform', {get: () => %s, configurable: true});"
                "Object.defineProperty(Navigator.prototype, 'maxTouchPoints', {get: () => %d, configurable: true});"
                "try { Object.defineProperty(Navigator.prototype, 'userAgentData', {get: () => undefined, configurable: true}); }"
                " catch (e) { /* egal */ }")

ZEIT_GESAMT = 26 * 60                                            # Job-Zeitlimit 30 min – danach Ergebnis sichern und Ende
T0 = time.time()
ERG = []
KOPF: dict = {}                                                  # Angaben für ergebnis.json (System, Engines, …)


def log(text):
    print(text, flush=True)


def schreibe():
    """ergebnis.json nach jeder Prüfung – bleibt auch erhalten, wenn ein Browser hängt und der Job abbricht."""
    if KOPF.get("pfad"):
        ok = bool(ERG) and all(e["ok"] for e in ERG)
        Path(KOPF["pfad"]).write_text(json.dumps(dict({k: v for k, v in KOPF.items() if k != "pfad"}, ok=ok,
                                                      dauer=round(time.time() - T0), pruefungen=ERG),
                                                 ensure_ascii=False, indent=1), encoding="utf-8")


def pruefe(name, ok, grund="", t0=None, protokoll=None):
    e = dict(name=name, ok=bool(ok), grund=str(grund)[:600], dauer=round(time.time() - t0, 1) if t0 else None)
    if not ok and protokoll:
        e["protokoll"] = "\n".join(str(protokoll).splitlines()[-40:])
    ERG.append(e)
    log(f"{'✓' if ok else '✗'} {name}" + (f" ({e['dauer']:.0f} s)" if e["dauer"] else "") + ("" if ok else f" – {e['grund'][:300]}"))
    schreibe()
    return bool(ok)


def waechter():
    """Hängt ein Browser (evaluate ohne Antwort), endet der Test nach ZEIT_GESAMT mit benannter Prüfung statt ohne Ergebnis
    (läuft als threading.Timer)."""
    pruefe("Browser-Test: Zeitlimit erreicht (eine Seite antwortet nicht mehr) – übrige Abläufe entfallen", False,
           f"nach {ZEIT_GESAMT // 60} min")
    os._exit(1)


def freier_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# =============================================================================================
# Server: statisch (Web-App + Download-Seite unter /me-goos-ta-deutsch/) und die Oberfläche (gans_ui.py)
# =============================================================================================
class _Statisch(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".wasm": "application/wasm",
                      ".mjs": "text/javascript", ".js": "text/javascript", ".webmanifest": "application/manifest+json",
                      ".svg": "image/svg+xml", ".ttf": "font/ttf", ".whl": "application/zip", ".zip": "application/zip"}

    def translate_path(self, path):
        p = path.split("?", 1)[0].split("#", 1)[0]
        p = "/" + p[len(UNTERORDNER):] if p.startswith(UNTERORDNER) else "/__nicht_da__"
        return super().translate_path(p)

    def log_message(self, *a):
        pass


class StatischerServer:
    """Wie GitHub Pages: <ordner> unter http://127.0.0.1:<port>/me-goos-ta-deutsch/. Abschaltbar (= offline)."""
    def __init__(self, ordner):
        self.ordner, self.port, self.srv = Path(ordner), freier_port(), None

    @property
    def adresse(self):
        return f"http://127.0.0.1:{self.port}{UNTERORDNER}"

    def an(self):
        if not self.srv:
            http.server.ThreadingHTTPServer.allow_reuse_address = True
            self.srv = http.server.ThreadingHTTPServer(("127.0.0.1", self.port),
                                                       functools.partial(_Statisch, directory=str(self.ordner)))
            threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        return self

    def aus(self):
        if self.srv:
            self.srv.shutdown()
            self.srv.server_close()
            self.srv = None


class Oberflaeche:
    """gans_ui.py auf einer frischen Kopie des Release-Ordners, eigener Datenordner, eigener Port, wie vom Startprogramm
    geöffnet (Willkommen). Nichts außerhalb des Temp-Ordners wird berührt."""
    def __init__(self, quelle):
        self.tmp = Path(tempfile.mkdtemp(prefix="mgd-browser-"))
        self.ordner = self.tmp / "Me-Goos-ta-Deutsch"
        shutil.copytree(quelle, self.ordner, ignore=shutil.ignore_patterns(
            ".git", ".github", ".gitattributes", "web-app", "ergebnis*.json", "__pycache__"))
        (self.tmp / "daten").mkdir()
        env = {k: v for k, v in os.environ.items() if not k.startswith(("MGD_", "PYTHON"))}
        env.update(PYTHONIOENCODING="utf-8", MGD_DATEN=str(self.tmp / "daten"), MGD_START_ID="ci")
        prog = self.ordner / "Programm"
        self.proc = subprocess.Popen([sys.executable, "-u", str(prog / "gans_ui.py"), "--kein-browser", "--port",
                                      str(freier_port())], cwd=str(prog), env=env, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
        self.zeilen, self.adresse = [], None
        threading.Thread(target=self._lesen, daemon=True).start()
        frist = time.time() + 90
        while time.time() < frist and not self.adresse and self.proc.poll() is None:
            time.sleep(0.2)

    def _lesen(self):
        for zeile in self.proc.stdout:
            self.zeilen.append(zeile.rstrip())
            m = re.search(r"http://127\.0\.0\.1:\d+/\?k=[A-Za-z0-9_-]+", zeile)
            if m and not self.adresse:
                self.adresse = m.group(0)

    def protokoll(self):
        return re.sub(r"([?&]k=)[A-Za-z0-9_\-]+", r"\1…", "\n".join(self.zeilen[-40:]))

    def ende(self):
        try:
            self.proc.terminate()
            self.proc.wait(20)
        except (OSError, subprocess.TimeoutExpired):
            self.proc.kill()
        shutil.rmtree(self.tmp, ignore_errors=True)


# =============================================================================================
# Browser-Sitzung: eine Engine, ein Profil (Rechner 1280 px oder Handy), Konsolenfehler mitschreiben
# =============================================================================================
def profil_optionen(pw, engine, profil):
    if profil == "rechner":
        return dict(viewport={"width": 1280, "height": 800})
    geraet = {"webkit": "iPhone 15", "chromium": "Pixel 7"}.get(engine)
    if not geraet:                                              # Firefox kennt kein isMobile → nur schmal (375 px)
        return dict(viewport={"width": 375, "height": 812})
    d = dict(pw.devices[geraet])
    d.pop("default_browser_type", None)
    return d


class Sitzung:
    def __init__(self, browser, pw, engine, profil, **extra):
        self.engine, self.profil = engine, profil
        self.ctx = browser.new_context(**{**profil_optionen(pw, engine, profil), **extra})
        self.ctx.set_default_timeout(ZEIT)
        self.page = self.ctx.new_page()
        self.konsole = []
        self.page.on("console", lambda m: m.type == "error" and self.konsole.append(f"console: {m.text}"[:400]))
        self.page.on("pageerror", lambda f: self.konsole.append(f"pageerror: {f}"[:400]))

    @property
    def kurz(self):
        return f"{self.engine}/{self.profil}"

    def fehler(self):
        """Konsolenfehler seit dem letzten Aufruf (ohne die erlaubten)."""
        neu = [k for k in self.konsole if not any(re.search(r, k) for r, _ in ERLAUBT)]
        self.konsole = []
        return neu

    def js(self, ausdruck, arg=None):
        return self.page.evaluate(ausdruck, arg)

    def warte(self, ausdruck, arg=None, zeit=ZEIT):
        """Wartet, bis der (auch asynchrone) Ausdruck in der Seite wahr ist – Abfrage alle 0,4 s, nie eine feste Wartezeit."""
        frist, letzter = time.time() + zeit / 1000, None
        while True:
            try:
                wert = self.page.evaluate(ausdruck, arg)
                if wert:
                    return wert
            except Exception as f:  # noqa: BLE001 – z. B. Seite lädt gerade neu
                letzter = f
            if time.time() > frist:
                raise TimeoutError(f"Zeitlimit {zeit // 1000} s: {ausdruck[:120]}" + (f" ({letzter})"[:300] if letzter else ""))
            time.sleep(0.4)

    def zu(self):
        try:
            self.ctx.close()
        except Exception:  # noqa: BLE001 – eine abgestürzte Seite darf das Aufräumen nicht aufhalten
            pass


SICHTBAR_JS = "e => !!e && e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden'"
LAYOUT_JS = """() => {
  const sichtbar = e => e.getClientRects().length > 0;
  const bilder = [...document.images].filter(sichtbar);
  return { breite: document.documentElement.scrollWidth, fenster: window.innerWidth,
           kaputt: bilder.filter(i => !(i.complete && i.naturalWidth > 0)).map(i => i.getAttribute('src').slice(0, 80)),
           bilder: bilder.length,
           sprachen: [...document.querySelectorAll('.sprache[lang]')].filter(sichtbar).map(e => e.getAttribute('lang')) };
}"""
# Tippflächen ≥ 44 px (Touch): sichtbare Bedienelemente; ein ::after mit position:absolute zählt als Tippfläche mit.
# Argument: Auswahllisten auslassen (macOS-WebKit zeichnet <select> nativ mit fester Höhe – iPhone/iPad nicht)
KLEIN_JS = """ohneSelect => {
  const aus = [];
  for (const el of document.querySelectorAll('button, a[href], input:not([type=hidden]), select, textarea, summary, [role=tab], [role=button]')) {
    if (ohneSelect && el.tagName === 'SELECT') continue;
    const r = el.getBoundingClientRect(); if (!r.width || !r.height || el.closest('[hidden]')) continue;
    const st = getComputedStyle(el); if (st.visibility === 'hidden' || st.display === 'none') continue;
    if (el.tagName === 'A' && !el.matches('.knopf, nav a') && st.display === 'inline') continue;   // Link im Fließtext
    if (el.matches('input[type=checkbox], input[type=radio]') && el.closest('label')) continue;   // Label ist die Fläche
    const a = getComputedStyle(el, '::after'), ab = a.content !== 'none' && a.position === 'absolute';
    const h = Math.max(r.height, ab ? parseFloat(a.height) || 0 : 0), w = Math.max(r.width, ab ? parseFloat(a.width) || 0 : 0);
    if (Math.min(h, w) < 43.5) aus.push(`${el.tagName.toLowerCase()}.${el.className} „${(el.textContent || el.value || '').trim().slice(0, 24)}“ ${Math.round(w)}×${Math.round(h)}`);
  }
  return aus;
}"""


# Was ragt über den rechten Rand? Die innersten Elemente (ohne überstehende Kinder) mit Klasse, Text und Breite
ZU_BREIT_JS = """() => {
  const W = window.innerWidth, aus = [];
  const raus = e => e.getClientRects().length > 0 && e.getBoundingClientRect().right > W + 1;
  for (const e of document.querySelectorAll('body *')) {
    if (!raus(e) || [...e.children].some(raus)) continue;
    const r = e.getBoundingClientRect(), st = getComputedStyle(e);
    aus.push(`${e.tagName.toLowerCase()}${e.id ? '#' + e.id : ''}.${String(e.className).slice(0, 30)} „${(e.textContent || e.value || '').trim().slice(0, 30)}“ `
      + `${Math.round(r.left)}–${Math.round(r.right)} ws=${st.whiteSpace} min=${st.minWidth}`);
    if (aus.length >= 4) break;
  }
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT), r = document.createRange();   // Text, der übersteht
  for (let n; (n = w.nextNode()) && aus.length < 6;) {
    if (!n.textContent.trim() || !n.parentElement.getClientRects().length) continue;
    r.selectNodeContents(n);
    const b = r.getBoundingClientRect();
    if (b.right > W + 1) aus.push(`Text in ${n.parentElement.tagName.toLowerCase()}.${String(n.parentElement.className).slice(0, 30)} „${n.textContent.trim().slice(0, 50)}“ bis ${Math.round(b.right)}`);
  }
  return aus;
}"""


def layout_ok(s):
    """→ (ok, Grund): kein waagerechtes Scrollen, alle sichtbaren Bilder geladen."""
    s.js("() => window.scrollTo(0, document.documentElement.scrollHeight)")
    time.sleep(0.5)
    s.js("() => window.scrollTo(0, 0)")
    lay = s.js(LAYOUT_JS)
    ok = lay["breite"] <= lay["fenster"] + 1 and not lay["kaputt"]
    return ok, f"Breite {lay['breite']}/{lay['fenster']} px · Bilder {lay['bilder']} · kaputt {lay['kaputt'][:3]}", lay


# =============================================================================================
# Stufe A – statische Seiten
# =============================================================================================
def a_download_sprachen(s, u):
    """Download-Seite: ohne Anker Englisch, #de/#es/#en, Sprachknopf, Layout, keine Konsolenfehler."""
    t0 = time.time()
    p, gruende, ok = s.page, [], True
    p.goto(u["download"])
    erst = s.js("() => document.documentElement.getAttribute('data-sprache')")
    ok &= erst == "en"
    gruende.append(f"ohne Anker {erst}")
    for l in ("de", "es", "en"):
        p.goto(u["download"] + "#" + l)
        p.reload()
        st = s.js("() => ({s: document.documentElement.getAttribute('data-sprache'), t: document.title})")
        lok, grund, lay = layout_ok(s)
        ok &= st["s"] == l and lay["sprachen"] == [l] and lok
        gruende.append(f"#{l}: {st['s']} sichtbar {lay['sprachen']} {grund}")
    p.click("#en nav [data-l='de']")
    s.warte("() => document.documentElement.getAttribute('data-sprache') === 'de'")
    fehler = s.fehler()
    pruefe(f"[{s.kurz}] A Download-Seite: Englisch zuerst, #de/#es/#en + Sprachknopf, kein waagerechtes Scrollen, Bilder "
           "geladen, keine Konsolenfehler", ok and not fehler, " · ".join(gruende) + f" · Konsole {fehler[:3]}", t0=t0)


def a_download_system(browser, pw, engine, u):
    """Download-Seite erkennt das System am User-Agent: eigener Knopf je Rechner-System, Handy-Hinweis am Handy;
    Link = Release-Asset (bzw. im Live-Lauf: lädt, Prüfsumme stimmt)."""
    t0 = time.time()
    gruende, ok = [], True
    link = None
    for name, (ua, plattform, erwartet) in GERAETE_UA.items():
        s = Sitzung(browser, pw, engine, "rechner", user_agent=ua)
        try:
            s.ctx.add_init_script(PLATTFORM_JS % (json.dumps(plattform), 5 if erwartet == "handy" else 0))
            s.page.goto(u["download"] + "#en")
            st = s.js("""() => { const sicht = e => e.getClientRects().length > 0, en = document.getElementById('en');
              return { os: document.documentElement.getAttribute('data-os') || '',
                       knoepfe: [...en.querySelectorAll('a.gross[data-os-teil]')].filter(sicht).map(a => [a.dataset.osTeil, a.href]),
                       handy: [...en.querySelectorAll('[data-nur-handy]')].some(sicht) }; }""")
            if erwartet == "handy":
                gut = st["os"] == "" and st["handy"] and len(st["knoepfe"]) == 3
            else:
                gut = st["os"] == erwartet and not st["handy"] and [k[0] for k in st["knoepfe"]] == [erwartet]
            hrefs = {k[1] for k in st["knoepfe"]}
            link = link or next(iter(hrefs), None)
            gut &= len(hrefs) == 1 and bool(re.fullmatch(u["zip_muster"], next(iter(hrefs), "")))
            ok &= gut
            gruende.append(f"{name}: {'✓' if gut else '✗'} os={st['os'] or '–'} Knöpfe={[k[0] for k in st['knoepfe']]} "
                           f"Handy={st['handy']}" + ("" if gut else f" {hrefs}"))
            fehler = s.fehler()
            if fehler:
                ok = False
                gruende.append(f"Konsole {fehler[:2]}")
        finally:
            s.zu()
    if u.get("live") and link and ok:                           # Live: Asset laden, Prüfsumme = SHA256SUMS
        try:
            daten = urllib.request.urlopen(urllib.request.Request(link, headers={"User-Agent": "me-goos-ta-deutsch"}),
                                           timeout=300).read()
            summen = urllib.request.urlopen(urllib.request.Request(link.rsplit("/", 1)[0] + "/SHA256SUMS.txt", headers={
                "User-Agent": "me-goos-ta-deutsch"}), timeout=60).read().decode("utf-8")
            sha = hashlib.sha256(daten).hexdigest()
            gut = f"{sha}  {link.rsplit('/', 1)[1]}" in summen and zipfile.is_zipfile(io.BytesIO(daten))
            ok &= gut
            gruende.append(f"Asset {len(daten) / 1e6:.1f} MB, SHA-256 {sha[:12]}… {'= SHA256SUMS' if gut else '≠ SHA256SUMS'}")
        except OSError as f:
            ok = False
            gruende.append(f"Asset nicht ladbar: {f}")
    pruefe(f"[{engine}] A Download-Seite: System erkannt (Windows/macOS/Linux eigener Knopf, iPhone/Android Handy-Hinweis), "
           "Link = Release-Asset", ok, " · ".join(gruende), t0=t0)


def a_installationsseiten(s, u):
    """Die drei Installationsseiten (file://, ohne Skript): Englisch ohne Anker, #de/#es per :target, Layout."""
    t0 = time.time()
    gruende, ok = [], True
    for name in INSTALLATIONSSEITEN:
        pfad = u["quelle"] / name
        if not pfad.is_file():
            ok = False
            gruende.append(f"fehlt: {name}")
            continue
        for l in ("", "de", "es", "en"):
            s.page.goto(pfad.as_uri() + (f"#{l}" if l else ""))
            lok, grund, lay = layout_ok(s)
            gut = lok and lay["sprachen"] == [l or "en"]
            ok &= gut
            if not gut:
                gruende.append(f"{name} #{l or '–'}: sichtbar {lay['sprachen']} {grund}")
    fehler = s.fehler()
    pruefe(f"[{s.kurz}] A Installationsseiten Android/iPhone/Pixel: Englisch zuerst, #de/#es, kein waagerechtes Scrollen, "
           "Bilder geladen, keine Konsolenfehler", ok and not fehler, " · ".join(gruende) + f" Konsole {fehler[:3]}", t0=t0)


def a_lies_mich(s, u):
    """LIES MICH ZUERST.html (file://): Englisch zuerst, Reiter DE/EN/ES und Windows/Mac/Linux, Layout."""
    t0 = time.time()
    p = s.page
    p.goto((u["quelle"] / LIES_MICH).as_uri())
    gruende, ok = [], True
    lok, grund, lay = layout_ok(s)
    ok &= lok and lay["sprachen"] == ["en"]
    gruende.append(f"Start {lay['sprachen']} {grund}")
    for l in ("de", "es", "en"):
        p.click(f"button[data-l='{l}']")
        for o in ("win", "mac", "linux"):
            p.click(f"section.sprache[lang='{l}'] button[data-os='{o}']")
            st = s.js("""([l, o]) => { const sicht = e => e.getClientRects().length > 0;
              const sek = [...document.querySelectorAll('section.sprache')].filter(sicht);
              return { sprachen: sek.map(e => e.getAttribute('lang')), lang: document.documentElement.lang,
                       os: sek.length ? [...sek[0].querySelectorAll('[data-os-inhalt]')].filter(sicht).map(e => e.dataset.osInhalt) : [] }; }""",
                        [l, o])
            gut = st["sprachen"] == [l] and st["lang"] == l and st["os"] == [o]
            ok &= gut
            if not gut:
                gruende.append(f"{l}/{o}: {st}")
        lok, grund, lay = layout_ok(s)
        ok &= lok
        if not lok:
            gruende.append(f"{l}: {grund}")
    fehler = s.fehler()
    pruefe(f"[{s.kurz}] A LIES MICH: Englisch zuerst, Reiter DE/EN/ES + Windows/Mac/Linux, kein waagerechtes Scrollen, "
           "keine Konsolenfehler", ok and not fehler, " · ".join(gruende) + f" Konsole {fehler[:3]}", t0=t0)


# =============================================================================================
# Stufe B1 – Oberfläche am Rechner (gans_ui.py)
# =============================================================================================
def _toast(s, teil):
    s.warte("t => [...document.querySelectorAll('#toasts > *')].some(x => x.textContent.includes(t))", teil)


def _ansicht(s, name):
    s.page.evaluate("n => { location.hash = '#' + n; }", name)
    s.warte("n => { const v = document.getElementById('v-' + n); return !!v && !v.hidden; }", name)


def b_willkommen(s, sprache_wechseln=True):
    """Willkommen: Englisch, Wechsel auf Deutsch, durchklicken (Tools: nichts gewählt) bis „Los geht’s!“."""
    t0 = time.time()
    s.warte("() => { const w = document.getElementById('willkommen-fenster'); return !!w && !w.hidden && !!document.getElementById('wk-titel'); }")
    erst = s.js("() => [document.documentElement.lang, document.getElementById('wk-titel').textContent]")
    if sprache_wechseln:
        s.page.click("#wk-inhalt [data-wk-sprache='de']")
        s.warte("() => document.documentElement.lang === 'de' && document.getElementById('wk-titel').textContent.includes('Willkommen')")
    schritte = 0
    while schritte < 8:
        schritte += 1
        if s.page.locator("#wk-inhalt [data-wk='fertig']").count():
            s.page.click("#wk-inhalt [data-wk='fertig']")
            break
        s.page.click("#wk-inhalt [data-wk='weiter']")
    s.warte("() => document.getElementById('willkommen-fenster').hidden")
    st = s.js("async () => (await api('/api/status')).sprache")
    return erst, st, schritte, t0


def b1_willkommen(s, u):
    erst, st, schritte, t0 = b_willkommen(s)
    _toast(s, "eingerichtet")
    pruefe(f"[{s.kurz}] B1 Willkommen: startet Englisch, Wechsel auf Deutsch, {schritte} Schritte bis „Los geht’s!“",
           erst[0] == "en" and erst[1].startswith("Welcome") and st == "de", f"Start {erst} · Sprache danach {st}", t0=t0)


def b_karten(s, n=10):
    t0 = time.time()
    _ansicht(s, "karten")
    s.warte("n => document.querySelectorAll('#kartenliste article.zeile').length === n", n)
    bilder = s.js("() => [...document.querySelectorAll('#kartenliste img[data-seite=vorn]')].length")
    return bilder, t0


def b1_karten(s, u):
    bilder, t0 = b_karten(s)
    s.page.click("#kartenliste article.zeile:first-child [data-aktion='bearbeiten']")
    s.page.fill(".editor input[data-k='notiz']", "Adjektiv · CI")
    s.page.click(".editor [data-k-aktion='speichern']")                   # wartet, bis die Prüfung den Knopf freigibt
    _toast(s, "gespeichert")
    notiz = s.js("async () => (await api('/api/karten')).karten[0].notiz")
    pruefe(f"[{s.kurz}] B1 Meine Karten: 10 Beispielkarten, Karte bearbeiten und speichern", bilder == 10 and notiz == "Adjektiv · CI",
           f"Bilder {bilder} · Notiz {notiz!r}", t0=t0)


def b_lernen(s, gelernt_vorher=0, aktivieren=True):
    """Tool „Karten lernen“ einschalten (Rückfrage → Installieren), eine Karte lernen (Antwort zeigen → Gut)."""
    t0 = time.time()
    _ansicht(s, "lernen")
    if aktivieren:
        s.page.click("#lern-inhalt [data-ln='aktivieren']")
        s.page.click("#tool-fenster [data-tool-dlg='installieren']")
    s.page.click("#lern-inhalt [data-ln='lernen']")
    s.page.click("#lern-inhalt [data-ln='zeigen']")
    s.page.click("#lern-inhalt [data-ln='note'][data-note='3']")
    s.warte("n => api('/api/lernen').then(r => r.statistik.heute.gelernt === n)", gelernt_vorher + 1)
    s.page.click("#lern-inhalt [data-ln='beenden']")
    return s.js("async () => (await api('/api/lernen')).statistik.heute.gelernt"), t0


def b1_lernen(s, u):
    gelernt, t0 = b_lernen(s)
    pruefe(f"[{s.kurz}] B1 Karten lernen: Tool einschalten (Rückfrage), eine Karte lernen (Antwort zeigen → Gut)", gelernt == 1,
           f"heute gelernt {gelernt}", t0=t0)


def b1_farben(s, u):
    t0 = time.time()
    _ansicht(s, "werkzeuge")
    vorher = s.js("() => getComputedStyle(document.body).backgroundColor")
    s.page.click("[data-werkzeug='farben']")
    s.page.click("#farben-inhalt [data-farb-schema='nacht']")
    s.warte("v => getComputedStyle(document.body).backgroundColor !== v", vorher)
    nacht = s.js("() => getComputedStyle(document.body).backgroundColor")
    s.page.click("#farben-inhalt [data-farb-aktion='speichern']")
    _toast(s, "Farben")
    schema = s.js("async () => (await api('/api/farben')).schema")
    s.page.click("#farben-inhalt [data-farb-aktion='standard']")
    s.warte("v => getComputedStyle(document.body).backgroundColor === v", vorher)
    s.page.click("#farben-fenster [data-zu]")
    zurueck = s.js("async () => (await api('/api/farben')).schema")
    pruefe(f"[{s.kurz}] B1 Farben: Schema Gänsenacht als Vorschau, gespeichert, zurück auf Standard", schema == "nacht"
           and nacht != vorher and zurueck == "himmel", f"{vorher} → {nacht} · gespeichert {schema} · danach {zurueck}", t0=t0)


def b1_hilfe(s, u):
    t0 = time.time()
    _ansicht(s, "hilfe")
    s.warte("() => { const d = document.getElementById('doku'); return d.querySelectorAll('h2').length > 5 && !d.querySelector('.ente-laedt'); }")
    titel = s.js("() => document.querySelector('#doku h1, #doku h2').textContent")
    s.page.click("#v-hilfe [data-doc='ueber']")
    s.warte("v => { const d = document.getElementById('doku'); return d.innerText.length < 8000 && d.innerText.includes(v)"
            " && !d.querySelector('.ente-laedt'); }", u["version"])
    pruefe(f"[{s.kurz}] B1 Hilfe: Leitfaden lädt, Reiter Über zeigt Version {u['version']}", "Leitfaden" in titel,
           f"Titel {titel!r}", t0=t0)


# Nachgebildete Sprachausgabe (Klang ist nie prüfbar – nur Knopf, Text, Sprache, Stimme, Abbruch)
STIMMEN_JS = """stimmen => {
  window.__sp = window.__sp || { gesagt: [], cancel: 0 };
  window.SpeechSynthesisUtterance = class { constructor(t) { this.text = t; this.lang = ""; this.voice = null; } };
  Object.defineProperty(window, "speechSynthesis", { configurable: true, value: { getVoices: () => stimmen,
    speak: x => __sp.gesagt.push({ text: x.text, lang: x.lang, stimme: x.voice && x.voice.name }), cancel: () => { __sp.cancel++; },
    addEventListener() {} } });
  zeichneSitzung();
  return document.querySelectorAll("#lern-inhalt [data-ln='vorlesen-de']").length;
}"""


def b1_aussprache(s, u):
    """🔊 Deutsch beim Lernen: ohne de-Stimme kein Knopf, nur Online-Stimme kein Knopf, lokale Stimme → Knopf erst nach dem
    Aufdecken, Klick liest genau den deutschen Text (de-DE vor de-CH), Beenden bricht ab."""
    t0 = time.time()
    _ansicht(s, "lernen")
    s.page.click("#lern-inhalt [data-ln='lernen']")
    s.page.click("#lern-inhalt [data-ln='zeigen']")
    s.warte("() => !!document.querySelector('#lern-inhalt .lern-de')")
    keine = s.js(STIMMEN_JS, [{"lang": "en-US", "localService": True, "name": "en"}])
    online = s.js(STIMMEN_JS, [{"lang": "de-DE", "localService": False, "name": "online"}])
    lokal = [{"lang": "en-US", "localService": True, "name": "en"}, {"lang": "de-CH", "localService": True, "name": "ch"},
             {"lang": "de-DE", "localService": True, "name": "de"}]
    s.js(STIMMEN_JS, lokal)
    vorher = s.js("() => { LS.gezeigt = false; zeichneSitzung(); return document.querySelectorAll(\"[data-ln='vorlesen-de']\").length; }")
    s.page.click("#lern-inhalt [data-ln='zeigen']")
    s.page.click("#lern-inhalt [data-ln='vorlesen-de']")
    gesagt = s.js("() => [__sp.gesagt.slice(-1)[0], LS.n.karte.de, __sp.cancel]")
    s.page.click("#lern-inhalt [data-ln='beenden']")
    ende = s.js("() => __sp.cancel")
    g = gesagt[0] or {}
    pruefe(f"[{s.kurz}] B1 Aussprache: 🔊 Deutsch nur mit lokaler de-Stimme und erst nach dem Aufdecken, liest den deutschen Text "
           "(de-DE), Beenden bricht ab", keine == 0 and online == 0 and vorher == 0 and g.get("text") == gesagt[1]
           and g.get("lang") == "de-DE" and g.get("stimme") == "de" and gesagt[2] >= 1 and ende > gesagt[2],
           f"ohne {keine} · online {online} · vor dem Aufdecken {vorher} · gesagt {gesagt} · cancel danach {ende}", t0=t0)


def b1_neue_version(s, u):
    """„Nach neuer Version suchen“ (Hilfe → Über): Öffnen fragt nie; nur der Klick fragt (Antwort des eigenen Servers
    nachgebildet – kein Netz): neuer → Link zur Download-Seite, aktuell, Fehlertext."""
    t0 = time.time()
    anfragen, antwort = [], {}
    s.page.route("**/api/neue-version", lambda r: (anfragen.append(r.request.method),
                                                    r.fulfill(status=200, content_type="application/json", body=json.dumps(antwort))))
    _ansicht(s, "hilfe")
    s.page.click("#v-hilfe [data-doc='ueber']")
    s.warte("() => !!document.getElementById('nv-knopf')")
    time.sleep(1)
    beim_oeffnen = len(anfragen)
    erg = []
    for a in ({"ergebnis": "neuer", "version": "9.9", "datum": "2030-01-02", "eigene": u["version"]},
              {"ergebnis": "aktuell", "version": u["version"], "datum": "", "eigene": u["version"]},
              {"ergebnis": "fehler", "code": "nv_grenze", "meldung": "Pause CI"}):
        antwort.clear()
        antwort.update(a)
        s.page.click("#nv-knopf")
        s.warte("() => { const e = document.getElementById('nv-ergebnis'); return !!e && !e.querySelector('.ente-laedt') && e.innerText.trim().length > 3"
                " && !document.getElementById('nv-knopf').disabled; }")
        erg.append(s.js("() => { const e = document.getElementById('nv-ergebnis'); const l = e.querySelector('a[href]');"
                        " return [e.innerText, l ? l.getAttribute('href') : '', e.getAttribute('aria-live')]; }"))
    s.page.unroute("**/api/neue-version")
    pruefe(f"[{s.kurz}] B1 Neue Version: Über öffnen fragt nicht, nur der Klick (je 1 POST); neuer → Download-Seite, aktuell, Fehlertext",
           beim_oeffnen == 0 and anfragen == ["POST"] * 3 and "9.9" in erg[0][0] and "/download/#" in erg[0][1]
           and erg[0][2] == "polite" and u["version"] in erg[1][0] and not erg[1][1] and "Pause CI" in erg[2][0],
           f"beim Öffnen {beim_oeffnen} · {anfragen} · {erg}", t0=t0)


WL_BEREIT = "() => !!WL && !!WL.erg && WL.status === '' && !!document.querySelector('#wl-inhalt .wl-tabelle')"


def _wl_datei(s, pfad):
    """Wortliste über das (unsichtbare) Dateifeld wählen wie eine Person: Klick auf die Fläche → Dateiauswahl."""
    with s.page.expect_file_chooser() as fc:
        s.page.click("#wl-inhalt [data-wl-aktion='waehlen']")
    fc.value.set_files(str(pfad))
    s.warte(WL_BEREIT)
    return s.js("() => ({ zahlen: WL.erg.zahlen, erkannt: WL.erg.erkannt, wahl: WL.wahl.size })")


def b_wortliste(s, u, stufe):
    """Wortliste in Ideen: UTF-16-Datei (Tab) und CSV mit „;“ über die Dateiauswahl, Vorschau-Zahlen, Option „Gans“ prüft
    neu, Text mit <img onerror> bleibt Text, anlegen → Toast → Rückgängig; am Handy kein waagerechtes Scrollen, Tippflächen."""
    t0 = time.time()
    tag = f"e2e{s.engine[:3]}{s.profil[0]}{stufe.lower()}"
    _ansicht(s, "ideen")
    s.warte("() => !!IDEEN")
    s.page.click("#v-ideen [data-dialog='wortliste']")
    s.warte("() => !document.getElementById('wl-fenster').hidden && !!document.querySelector('#wl-inhalt [data-wl-aktion=\"waehlen\"]')")
    u16 = u["tmp"] / f"wl16-{tag}.txt"
    u16.write_bytes(b"\xff\xfe" + f"{tag} eins\tuno{tag}\n{tag} zwei\tdos{tag}\n".encode("utf-16-le"))
    a = _wl_datei(s, u16)
    s.page.click("#wl-inhalt [data-wl-aktion='andere']")
    csv = u["tmp"] / f"wl-{tag}.csv"
    csv.write_text(f"Deutsch;Wort;Notiz\n{tag} müde;cansado;\n{tag} rot;;Farbe\n{tag} <img src=x onerror=\"window.__xss=1\">;x;\n"
                   f"{tag} müde;cansado2;\n=1+1;y;\n", encoding="utf-8")
    b = _wl_datei(s, csv)
    xss = s.js("() => [!!window.__xss, document.querySelectorAll('#wl-inhalt table img').length,"
               " document.querySelector('#wl-inhalt .wl-tabelle').innerText.includes('<img src=x')]")
    s.page.locator("#wl-inhalt label.schalter", has=s.page.locator("[data-wl-opt='gans']")).click()
    s.warte("() => !!WL && !!WL.erg && WL.erg.erkannt.gans === false && WL.status === ''")
    ohne_gans = s.js("() => WL.wahlZurueck === false && WL.erg.zeilen[0].de")
    s.page.locator("#wl-inhalt label.schalter", has=s.page.locator("[data-wl-opt='gans']")).click()
    s.warte("() => !!WL && !!WL.erg && WL.erg.erkannt.gans === true && WL.status === ''")
    handy = {}
    if s.profil == "handy":
        handy = s.js("() => ({ seite: document.documentElement.scrollWidth - innerWidth, fenster: (e => e.scrollWidth - e.clientWidth)"
                     "(document.getElementById('wl-inhalt')), liste: getComputedStyle(document.querySelector('.wl-tabelle tr')).display })")
        if s.js("() => matchMedia('(hover: none) and (pointer: coarse)').matches"):
            handy["klein"] = s.js(KLEIN_JS, s.engine == "webkit" and sys.platform == "darwin")[:4]
    s.page.click("#wl-inhalt [data-wl-aktion='anlegen']")
    s.warte("() => document.getElementById('wl-fenster').hidden")
    s.warte("t => !!IDEEN && IDEEN.ideen.filter(i => i.de.includes(t)).length === 3", tag)
    nachher = s.js("t => [[...document.querySelectorAll('#ideen-inhalt input[data-i-feld=de]')].some(i => i.value.includes('<img')),"
                   " !!window.__xss, !document.getElementById('ideen-uebersetzen').hidden,"
                   " [...document.querySelectorAll('#toasts .toast')].filter(x => x.querySelector('button')).length]", tag)
    s.page.click("#toasts .toast:last-child button")
    s.warte("t => !!IDEEN && IDEEN.ideen.filter(i => i.de.includes(t)).length === 0", tag)
    ok = (a["erkannt"]["kodierung"] == "utf-16-le" and a["erkannt"]["trenner"] == "tab" and a["zahlen"]["neu"] == 2
          and b["erkannt"]["trenner"] == "semikolon" and b["erkannt"]["kopf"] and b["erkannt"]["kodierung"] == "utf-8"
          and (b["zahlen"]["zeilen"], b["zahlen"]["neu"], b["zahlen"]["doppelt"], b["zahlen"]["fehler"]) == (5, 3, 1, 1) and b["wahl"] == 3
          and xss == [False, 0, True] and ohne_gans == f"{tag} müde" and nachher[:3] == [True, False, True] and nachher[3] >= 1
          and (not handy or (handy["seite"] <= 1 and handy["fenster"] <= 1 and handy["liste"] == "grid" and not handy.get("klein"))))
    pruefe(f"[{s.kurz}] {stufe} Wortliste: UTF-16 (Tab) + CSV „;“ per Dateiauswahl, Vorschau 3 neu · 1 doppelt · 1 fehlerhaft, Option prüft neu, "
           "HTML bleibt Text, anlegen → Rückgängig" + (", Handy als Liste ohne Querscrollen" if handy else ""), ok,
           f"UTF-16 {a} · CSV {b} · xss {xss} · ohne Gans {ohne_gans!r} · danach {nachher} · Handy {handy}", t0=t0)


def b1_wortliste(s, u):
    b_wortliste(s, u, "B1")


def b2_wortliste(s, u):
    b_wortliste(s, u, "B2")


def b1_touch(s, u):
    """Touch: Tippflächen ≥ 44 px und kein waagerechtes Scrollen in den Hauptansichten."""
    t0 = time.time()
    touch = s.js("() => matchMedia('(hover: none) and (pointer: coarse)').matches")
    ohne_select = s.engine == "webkit" and sys.platform == "darwin"
    befund = {}
    for v in ("karten", "lernen", "tabelle", "ideen", "erzeugen", "werkzeuge", "hilfe"):
        _ansicht(s, v)
        time.sleep(0.6)
        klein = s.js(KLEIN_JS, ohne_select)
        breite = s.js("() => [document.documentElement.scrollWidth, window.innerWidth]")
        if klein or breite[0] > breite[1] + 1:
            befund[v] = dict(klein=klein[:4], breite=breite, zu_breit=s.js(ZU_BREIT_JS) if breite[0] > breite[1] + 1 else [])
    pruefe(f"[{s.kurz}] B1 Touch: Tippflächen ≥ 44 px, kein waagerechtes Scrollen (7 Ansichten)"
           + (" – Auswahllisten ausgenommen (macOS-WebKit zeichnet sie nativ)" if ohne_select else ""), touch and not befund,
           f"Touch erkannt {touch} · {befund}", t0=t0)


def b1_konsole(s, u):
    fehler = s.fehler()
    pruefe(f"[{s.kurz}] B1 Oberfläche: keine Konsolenfehler", not fehler, str(fehler[:5]))


# =============================================================================================
# Stufe B2 – Web-App (Handy-App, PWA mit Pyodide)
# =============================================================================================
APP_BEREIT = "() => !!window.toast && !!document.getElementById('app-start') && document.getElementById('app-start').hidden"


def b2_start(s, u):
    t0 = time.time()
    s.page.goto(u["app"])
    s.warte(APP_BEREIT, zeit=ZEIT_APP)
    info = s.js("""() => ({ sw: !!(navigator.serviceWorker && navigator.serviceWorker.controller),
      isoliert: window.crossOriginIsolated, lang: document.documentElement.lang })""")
    if s.js("() => !document.getElementById('willkommen-fenster').hidden"):
        b_willkommen(s, sprache_wechseln=False)
    bilder, _ = b_karten(s)
    pruefe(f"[{s.kurz}] B2 Web-App: erster Start bis bereit (Service Worker, crossOriginIsolated, Englisch), 10 Beispielkarten",
           info["sw"] and info["isoliert"] and info["lang"] == "en" and bilder == 10, f"{info} · Karten {bilder}", t0=t0)


# Beobachter für _app_datei: welche Abrufe der Seite starten/enden und welche Toasts erscheinen (nur Lesen, die App bleibt gleich)
HOLEN_JS = """name => {
  window.__mgdAlt = APP_DATEI; window.__mgdName = name; window.__mgdHolt = []; window.__mgdToasts = window.__mgdToasts || [];
  if (!window.__mgdFetch) {
    window.__mgdFetch = window.fetch;
    window.fetch = function (...a) {
      const e = { url: decodeURIComponent(String((a[0] && a[0].url) || a[0])).slice(-100), fertig: false, t0: Date.now() };
      window.__mgdHolt.push(e);
      const p = window.__mgdFetch.apply(this, a);
      p.then(r => { e.fertig = true; e.status = r.status; e.ms = Date.now() - e.t0; },
             f => { e.fertig = true; e.fehler = String(f).slice(0, 100); });
      return p;
    };
    new MutationObserver(l => l.forEach(m => m.addedNodes.forEach(n => window.__mgdToasts.push((n.textContent || '').slice(0, 120)))))
      .observe(document.getElementById('toasts'), { childList: true });
  }
}"""
GEHOLT_JS = "() => window.__mgdHolt.filter(e => e.url.includes(window.__mgdName))"
BEFUND_JS = """() => ({ abrufe: window.__mgdHolt.filter(e => e.url.includes(window.__mgdName)),
  andere: window.__mgdHolt.filter(e => !e.fertig && !e.url.includes(window.__mgdName)).map(e => e.url).slice(-3),
  toasts: (window.__mgdToasts || []).slice(-3), fenster: !document.getElementById('app-fenster').hidden })"""


def _app_datei(s, auswahl):
    """Link anklicken → app.js holt die Datei → Fenster „Teilen / Speichern“ → (Name, Bytes). Startet der Klick keinen Abruf
    (Ansicht wurde gerade neu gezeichnet), wird einmal neu geklickt; hängt der Abruf selbst, scheitert die Prüfung mit Befund."""
    s.page.wait_for_selector(auswahl)
    name = s.page.eval_on_selector(auswahl, "a => decodeURIComponent(a.getAttribute('href')).split('?')[0].split('/').pop()")
    s.js(HOLEN_JS, name)
    for versuch in (1, 2):
        s.page.click(auswahl)
        try:
            s.warte(GEHOLT_JS + ".length", zeit=15_000)
            break
        except TimeoutError:
            if versuch == 2:
                raise TimeoutError(f"Klick auf {name} startete keinen Abruf (2 Versuche) · {s.js(BEFUND_JS)}") from None
            log(f"  · [{s.kurz}] Klick auf {name} startete keinen Abruf – neu geklickt · {s.js(BEFUND_JS)}")
    try:
        s.warte("() => !!APP_DATEI && APP_DATEI !== window.__mgdAlt && !document.getElementById('app-fenster').hidden"
                " && !!document.querySelector('#app-inhalt a[download][href^=\"blob:\"]')", zeit=ZEIT_APP)
    except TimeoutError as f:
        raise TimeoutError(f"{name} kam nicht im Fenster „Teilen / Speichern“ an · {s.js(BEFUND_JS)} · {f}") from None
    d = s.js("""async () => { const b = new Uint8Array(await APP_DATEI.arrayBuffer()); let t = '';
      for (let i = 0; i < b.length; i += 32768) t += String.fromCharCode.apply(null, b.subarray(i, i + 32768));
      return { name: APP_DATEI.name, daten: btoa(t), titel: document.getElementById('app-titel').textContent }; }""")
    s.page.click("#app-fenster [data-zu]")
    return d["name"], base64.b64decode(d["daten"]), d["titel"]


def b2_drucken(s, u):
    t0 = time.time()
    _ansicht(s, "erzeugen")
    s.page.eval_on_selector("#v-erzeugen input[name=ziel][value=bogen]", "e => e.click()")
    s.page.click("#v-erzeugen [data-start]")
    s.warte("() => api('/api/lauf').then(r => r.code !== null && r.code !== undefined)", zeit=ZEIT_APP)
    code = s.js("async () => (await api('/api/lauf')).code")
    _ansicht(s, "pruefen")
    name, daten, titel = _app_datei(s, "#v-pruefen a[href*='Heimdruck']")
    seiten = len(re.findall(rb"/Type\s*/Page(?![a-zA-Z])", daten))
    pruefe(f"[{s.kurz}] B2 Web-App: Heimdruck-PDF der 10 Karten → „Teilen / Speichern“", code == 0 and daten[:5] == b"%PDF-"
           and "Heimdruck" in name and seiten >= 2 and seiten % 2 == 0 and titel == name,
           f"Code {code} · {name} · {len(daten) // 1024} KB · {seiten} Seiten", t0=t0)


def b2_lernen_sicherung(s, u):
    t0 = time.time()
    gelernt, _ = b_lernen(s)
    pruefe(f"[{s.kurz}] B2 Web-App: Karten lernen einschalten, eine Karte lernen", gelernt == 1, f"heute gelernt {gelernt}", t0=t0)
    t0 = time.time()
    mehr = s.js("() => { const k = document.querySelector('#app-navi [data-app=\"mehr\"]'); return !!k && k.getClientRects().length > 0; }")
    if mehr:                                                    # Handy-Format: untere Navigation → Mehr → Sicherung
        s.page.click("#app-navi [data-app='mehr']")
        s.page.click("#mehr-fenster [data-app-aktion='sicherung']")
    else:
        s.js("() => oeffneAppSicherung()")
    name, daten, _ = _app_datei(s, "#app-inhalt a[download][href*='app-sicherung']")
    datei = u["tmp"] / f"sicherung-{s.engine}.zip"
    datei.write_bytes(daten)
    with zipfile.ZipFile(datei) as z:
        inhalt = z.namelist()
    nach_sicherung = b_lernen(s, gelernt_vorher=1, aktivieren=False)[0]  # danach noch eine Karte → Sicherung muss sie verwerfen
    if mehr:
        s.page.click("#app-navi [data-app='mehr']")
        s.page.click("#mehr-fenster [data-app-aktion='sicherung']")
    else:
        s.js("() => oeffneAppSicherung()")
    s.page.set_input_files("#app-inhalt input[data-app-einspielen]", str(datei))
    with s.page.expect_navigation(timeout=ZEIT_APP):              # die App lädt nach dem Einspielen neu
        s.page.click("#app-frage [data-app-aktion='einspielen-ja']")
    s.warte(APP_BEREIT, zeit=ZEIT_APP)
    zurueck = s.js("async () => (await api('/api/lernen')).statistik.heute.gelernt")
    karten = s.js("async () => (await api('/api/karten')).karten.length")
    pruefe(f"[{s.kurz}] B2 Web-App: App-Sicherung speichern und wieder einspielen (Stand von vorher zurück)",
           name.endswith(".zip") and any(n.endswith("karten.csv") for n in inhalt) and nach_sicherung == 2 and zurueck == 1
           and karten == 10, f"{name} · {len(daten) // 1024} KB · {len(inhalt)} Dateien · gelernt 2 → eingespielt {zurueck} · "
                             f"Karten {karten}", t0=t0)


def b2_offline(s, u):
    t0 = time.time()
    if u.get("live"):
        if s.engine == "webkit":                                # WebKit unter Playwright kann „offline“ nicht nachstellen
            log(f"· [{s.kurz}] B2 offline: im Live-Lauf für WebKit nicht nachstellbar (Grenze) – übersprungen")
            return
        s.ctx.set_offline(True)
    else:
        u["server"].aus()                                       # Server weg = offline (geht in jeder Engine)
    try:
        s.page.reload()
        s.warte(APP_BEREIT, zeit=ZEIT_APP)
        _, _ = b_karten(s)
        karten = s.js("async () => (await api('/api/karten')).karten.length")
        ok, grund = karten == 10, f"Karten {karten}"
    except Exception as f:  # noqa: BLE001
        ok, grund = False, f"{type(f).__name__}: {str(f)[:200]}"
    finally:
        if u.get("live"):
            s.ctx.set_offline(False)
        else:
            u["server"].an()
    pruefe(f"[{s.kurz}] B2 Web-App: Neuladen ohne Netz startet aus dem Gerätespeicher", ok, grund, t0=t0)


def b2_konsole(s, u):
    fehler = s.fehler()
    pruefe(f"[{s.kurz}] B2 Web-App: keine Konsolenfehler", not fehler, str(fehler[:5]))


# =============================================================================================
# Abläufe (erweiterbar): (Stufe, Engines, Profile, Funktion). Eine Sitzung je Stufe/Engine/Profil, Abläufe nacheinander.
# Spätere Gruppen hängen neue Abläufe an (z. B. B1 Wortliste in Ideen) – Name der Prüfung = „[engine/profil] Stufe …“.
# =============================================================================================
ALLE = ENGINES
EIGENE = None                                                   # Profil „eigene“: der Ablauf öffnet seine Sitzungen selbst
ABLAEUFE = [
    ("A", ALLE, ("rechner", "handy"), a_download_sprachen),
    ("A", ALLE, EIGENE, a_download_system),
    ("A", ALLE, ("rechner", "handy"), a_installationsseiten),
    ("A", ALLE, ("rechner", "handy"), a_lies_mich),
    ("B1", ALLE, ("rechner",), b1_willkommen),
    ("B1", ALLE, ("rechner",), b1_karten),
    ("B1", ALLE, ("rechner",), b1_lernen),
    ("B1", ALLE, ("rechner",), b1_farben),
    ("B1", ALLE, ("rechner",), b1_hilfe),
    ("B1", ALLE, ("rechner",), b1_aussprache),
    ("B1", ALLE, ("rechner",), b1_neue_version),
    ("B1", ALLE, ("rechner",), b1_wortliste),
    ("B1", ALLE, ("rechner",), b1_konsole),
    ("B1", ("webkit", "chromium"), ("handy",), b1_willkommen),
    ("B1", ("webkit", "chromium"), ("handy",), b1_lernen),
    ("B1", ("webkit", "chromium"), ("handy",), b1_wortliste),
    ("B1", ("webkit", "chromium"), ("handy",), b1_touch),
    ("B1", ("webkit", "chromium"), ("handy",), b1_konsole),
    ("B2", ALLE, ("handy",), b2_start),
    ("B2", ALLE, ("handy",), b2_drucken),
    ("B2", ALLE, ("handy",), b2_lernen_sicherung),
    ("B2", ("webkit", "chromium"), ("handy",), b2_wortliste),
    ("B2", ALLE, ("handy",), b2_offline),
    ("B2", ALLE, ("handy",), b2_konsole),
]


def gruppen(engines, stufen):
    """[(Stufe, Engine, Profil, [Abläufe])] in Reihenfolge der Liste – eine Sitzung je Gruppe (Profil None: je Ablauf)."""
    aus = []
    for stufe, eng, profile, fn in ABLAEUFE:
        if stufe not in stufen:
            continue
        for e in engines:
            if e not in eng:
                continue
            for p in profile or (None,):
                g = next((x for x in aus if x[:3] == (stufe, e, p)), None) if p else None
                if not g:
                    g = (stufe, e, p, [])
                    aus.append(g)
                g[3].append(fn)
    return aus


def lauf(engines, stufen, u):
    from playwright.sync_api import sync_playwright
    u["tmp"] = Path(tempfile.mkdtemp(prefix="mgd-bt-"))
    try:
        with sync_playwright() as pw:
            browser = {}
            for e in engines:
                t0 = time.time()
                try:
                    browser[e] = getattr(pw, e).launch(**({"channel": KANAL[e]} if KANAL.get(e) else {}))
                    pruefe(f"[{e}] Engine startet ({browser[e].version})", True, t0=t0)
                except Exception as f:  # noqa: BLE001
                    pruefe(f"[{e}] Engine startet", False, f"{type(f).__name__}: {f}")
            for stufe, e, profil, fns in gruppen([e for e in engines if e in browser], stufen):
                if profil is None:
                    for fn in fns:
                        _sicher(fn, f"[{e}] {stufe} {fn.__name__}", browser[e], pw, e, u)
                    continue
                ui = None
                if stufe == "B1":
                    ui = Oberflaeche(u["quelle"])
                    if not pruefe(f"[{e}/{profil}] B1 Oberfläche startet (gans_ui.py, eigener Datenordner)", ui.adresse,
                                  "keine Startadresse", protokoll=ui.protokoll()):
                        ui.ende()
                        continue
                s = Sitzung(browser[e], pw, e, profil)
                try:
                    if ui:
                        s.page.goto(ui.adresse)
                    for fn in fns:
                        ok = _sicher(fn, f"[{s.kurz}] {stufe} {fn.__name__}", s, u, ui=ui)
                        if not ok and fn in (b2_start, b1_willkommen):
                            break                               # ohne laufende App/Oberfläche haben die übrigen keinen Sinn
                finally:
                    s.zu()
                    if ui:
                        ui.ende()
            for b in browser.values():
                b.close()
    finally:
        shutil.rmtree(u["tmp"], ignore_errors=True)


def _sicher(fn, name, *args, ui=None):
    """Ablauf ausführen; jede Ausnahme (z. B. Zeitlimit beim Warten) wird eine benannte, gescheiterte Prüfung."""
    vorher = len(ERG)
    try:
        fn(*args)
    except Exception as f:  # noqa: BLE001
        import traceback
        pruefe(name, False, f"{type(f).__name__}: {(str(f).splitlines() or [''])[0][:400]}",
               protokoll=traceback.format_exc() + ("\n--- gans_ui.py ---\n" + ui.protokoll() if ui else ""))
    return len(ERG) > vorher and all(e["ok"] for e in ERG[vorher:])


def umgebung(live, quelle, server):
    """Adressen der Seiten: lokal (statischer Server, Release-Ordner) oder live (GitHub Pages, entpacktes Release)."""
    version = re.search(r'^VERSION = "([\d.]+)', (quelle / "Programm" / "gans_lernkarten.py").read_text("utf-8"), re.M)[1]
    adresse = (quelle / "Programm" / "web_adresse.txt").read_text(encoding="utf-8").strip().splitlines()[0].strip()
    m = re.match(r"^https://([a-z0-9-]+)\.github\.io/([A-Za-z0-9._-]+)/$", adresse)
    konto, repo = m.group(1), m.group(2)
    basis = adresse if live else server.adresse
    zip_muster = (rf"https://github\.com/{re.escape(konto)}/{re.escape(repo)}/releases/download/v{re.escape(version)}/"
                  rf"Me-Goos-ta-Deutsch-{re.escape(version)}\.zip")
    return dict(live=live, quelle=quelle, server=server, version=version, app=basis, download=basis + "download/",
                zip_muster=zip_muster)


def main(argv):
    for strom in (sys.stdout, sys.stderr):                      # Windows-Runner schreiben sonst cp1252 (✓ ✗ → Fehler)
        try:
            strom.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    def wert(name, standard=None):
        return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else standard
    live = "--live" in argv
    engines = [e for e in wert("--engines", ",".join(ENGINES)).split(",") if e]
    stufen = wert("--stufen", "A,B2" if live else "A,B1,B2").split(",")
    quelle = Path(wert("--quelle") or WURZEL).resolve()
    if "--neuestes-release" in argv:                            # Release-Prüfung: das veröffentlichte Release (Prüfsumme)
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import neuestes_release
        try:
            r = neuestes_release.laden(Path(tempfile.mkdtemp(prefix="mgd-rel-")), neuestes_release.repo_von(WURZEL))
        except (OSError, ValueError) as f:
            sys.exit(f"✗ Release nicht geladen: {f}")
        log(f"Release {r['version']} geladen ({r['name']}, SHA-256 {r['sha256'][:16]}… = SHA256SUMS.txt)")
        quelle = Path(r["ordner"])
    KANAL["chromium"] = wert("--kanal")                         # lokal: installiertes Chrome/Edge statt Playwright-Chromium
    system = wert("--system", f"browser-{platform.system().lower()}")
    ergebnis = Path(wert("--ergebnis", "ergebnis.json")).resolve()
    if any(e not in ENGINES for e in engines) or not (quelle / "Programm" / "gans_lernkarten.py").is_file():
        sys.exit(f"✗ Aufruf: --engines aus {', '.join(ENGINES)}; --quelle <Release-Ordner> (gefunden: {quelle})")
    server = None
    if not live:
        if not (WURZEL / "web-app" / "sw.js").is_file() and "B2" in stufen:
            sys.exit(f"✗ web-app/ fehlt in {WURZEL} (ci_lauf.py legt sie in den Branch ci)")
        server = StatischerServer(WURZEL / "web-app").an()
    log(f"Browser-Test {system} · {platform.platform()} · Engines {', '.join(engines)} · Stufen {', '.join(stufen)}"
        + (" · live" if live else ""))
    KOPF.update(pfad=str(ergebnis), system=system, plattform=platform.platform(), maschine=platform.machine(),
                engines=engines, stufen=stufen, live=live, lauf=os.environ.get("GITHUB_RUN_ID"))
    uhr = threading.Timer(ZEIT_GESAMT, waechter)
    uhr.daemon = True
    uhr.start()
    try:
        lauf(engines, stufen, umgebung(live, quelle, server))
    finally:
        uhr.cancel()
        if server:
            server.aus()
        schreibe()
    ok = bool(ERG) and all(e["ok"] for e in ERG)
    bestanden = sum(1 for e in ERG if e["ok"])
    log(f"{'✓ BROWSER-TEST BESTANDEN' if ok else '✗ BROWSER-TEST NICHT BESTANDEN'} · {bestanden}/{len(ERG)} · "
        f"{(time.time() - T0) / 60:.1f} min")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
