#!/usr/bin/env python3
"""Baut die Handy-App (Web-App, PWA) von Me Goos-ta Deutsch als statischen Ordner <Ziel>/web-app/.
Aufruf: python bau_webapp.py <Quelle: Ordner Me-Goos-ta-Deutsch> <Ziel-Ordner> [--ohne-pyodide] [--ohne-modelle]
                             [--cache <Ordner für Downloads>] [--release-zip <Me-Goos-ta-Deutsch-<Version>.zip>]
        python bau_webapp.py <Quelle> --installationsdateien   → „Me Goos-ta Deutsch - Android/iPhone/Google Pixel.html“
                             neben den Startdateien (statisch, ohne JavaScript, QR-Code der Adresse aus web_adresse.txt)

Inhalt (Positivliste): index.html + ui.js (dieselbe Oberfläche wie am Rechner, Modus AM_APP), app.js, worker.js, sw.js
(Quellen in web-app-quelle/ an der Wurzel des Quellbaums), manifest.webmanifest, Symbole, Poppins, py/programm.zip (Module ohne
Startprogramm, KI-Bilder und Tests + Beispiele, FSRCNN, Vorlagen, Leitfäden), pyodide/ (feste Fassung, nur nötige Pakete,
SHA-256 geprüft), lizenzen/, modelle/ (Real-ESRGAN als .npz – nur auf Wunsch geladen, nicht im Offline-Paket), download/ (Download-Seite
für den Rechner – nicht im Offline-Paket; mit --release-zip Direktlink, Größe und SHA-256 des GitHub-Release-Assets,
sonst Link auf das neueste Release; download/app.js holt eine App von vor 2.1 auf den neuen Service Worker).
Nutzerdaten (karten.csv, bilder/, ideen, lernstand, Einstellungen, ausgabe/) kommen nie hinein.
Pyodide-Downloads landen im Zwischenspeicher (Standard: %TEMP%/mgd-webapp-cache) und werden wiederverwendet."""
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

HIER = Path(__file__).resolve().parent
QUELLE_WEB = HIER.parent / "web-app-quelle"                    # Wurzel des Quellbaums
PYODIDE = "314.0.7"
PYODIDE_KERN = (f"https://github.com/pyodide/pyodide/releases/download/{PYODIDE}/pyodide-core-{PYODIDE}.tar.bz2",
                "2abdcc2e35208af406e07724cffa85bc582ced97e9028383ecf5462541393f95")
PYODIDE_CDN = f"https://cdn.jsdelivr.net/pyodide/v{PYODIDE}/full/"
KERN_DATEIEN = ("pyodide.mjs", "pyodide.asm.mjs", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json")
PAKETE = ("numpy", "pillow", "charset-normalizer")               # + Abhängigkeiten laut pyodide-lock.json
REPORTLAB = ("reportlab", "5.0.1", "1c36e6bb0e71780c72331eba60da7f602e8d4389a8723825af71342e49d791e8")
# Programm-Paket (py/programm.zip): alle Module außer diesen, dazu die Ordner/Dateien unten
MODULE_WEG = {"starter.py", "ki_bild.py", "aktualisieren.py", "signatur.py"}   # App aktualisiert sich über ihren Service Worker
PROGRAMM_ORDNER = ("assets", "beispiel-bilder", "schrift", "vorlagen")
PROGRAMM_DATEIEN = ("beispiel-karten.csv", "LEITFADEN.md", "LEITFADEN_en.md", "LEITFADEN_es.md", "SPEC.md", "DRITTLIZENZEN.md",
                    "web_adresse.txt")
MODELL_KLEIN = 5 * 1024 * 1024                                  # FSRCNN (Kern) ins Programm, Real-ESRGAN nach modelle/
NUTZERDATEN = re.compile(r"(^|/)(karten(\.bak)?\.csv|ideen\.json|lernstand[^/]*\.json|ui_einstellungen\.json|tools\.json|"
                         r"uebersetzung(en)?\.json|bilder/|ideen/|ausgabe/|__pycache__/|_alt/|gans_hintergrund\.)")
ZEIT = (2026, 1, 1, 0, 0, 0)                                    # feste Zeit in der ZIP → gleicher Inhalt = gleiche Prüfsumme
HINTERGRUND, VORDERGRUND = "#E8F2FA", "#FFFFFF"                  # Standard-Farben (Gänsehimmel): Startbildschirm, Kopfzeile


def sha(daten):
    return hashlib.sha256(daten).hexdigest()


def hole(url, sha256, cache, name=None):
    """Datei aus dem Zwischenspeicher bzw. herunterladen; SHA-256 muss stimmen."""
    ziel = cache / (name or url.rsplit("/", 1)[-1])
    if ziel.is_file() and sha(ziel.read_bytes()) == sha256:
        return ziel.read_bytes()
    sys.path.insert(0, str(QUELLE / "Programm"))
    import urllib.request
    import ki_modelle                                           # gleiche Zertifikatsprüfung wie das Programm
    print(f"  lade {url}")
    with ki_modelle.oeffne_url(urllib.request.Request(url, headers={"User-Agent": "Me-Goos-ta-Deutsch"}), timeout=120) as r:
        daten = r.read()
    if sha(daten) != sha256:
        sys.exit(f"Prüfsumme stimmt nicht: {url}")
    cache.mkdir(parents=True, exist_ok=True)
    ziel.write_bytes(daten)
    return daten


def pyodide_dateien(cache):
    """{Pfad in pyodide/: Bytes} – Kern (fester Release + SHA-256) und die Räder aus pyodide-lock.json, dazu ReportLab."""
    kern = hole(*PYODIDE_KERN, cache)
    aus = {}
    with tarfile.open(fileobj=io.BytesIO(kern)) as t:
        for n in KERN_DATEIEN:
            aus[n] = t.extractfile(f"pyodide/{n}").read()
    lock = json.loads(aus["pyodide-lock.json"])["packages"]
    namen, offen = [], list(PAKETE)
    while offen:
        n = offen.pop(0)
        if n not in namen:
            namen.append(n)
            offen += lock[n].get("depends", [])
    for n in namen:
        e = lock[n]
        aus[e["file_name"]] = hole(PYODIDE_CDN + e["file_name"], e["sha256"], cache)
    rl, version, rl_sha = REPORTLAB
    datei = f"{rl}-{version}-py3-none-any.whl"
    if not (cache / datei).is_file():
        import urllib.request
        sys.path.insert(0, str(QUELLE / "Programm"))
        import ki_modelle
        with ki_modelle.oeffne_url(urllib.request.Request(f"https://pypi.org/pypi/{rl}/{version}/json")) as r:
            info = json.loads(r.read().decode("utf-8"))
        url = next(u["url"] for u in info["urls"] if u["filename"] == datei)
        hole(url, rl_sha, cache, datei)
    aus[datei] = hole("", rl_sha, cache, datei)
    return aus, namen, datei


def programm_zip():
    """py/programm.zip: Module (ohne Startprogramm, KI-Bilder, Tests) + Beispiele, Symbole, Schriften, Vorlagen, FSRCNN,
    Leitfäden, SPEC. Feste Zeitstempel und Reihenfolge – gleicher Inhalt ergibt dieselbe Prüfsumme."""
    prog = QUELLE / "Programm"
    dateien = []
    for p in sorted(prog.glob("*.py")):
        if p.name not in MODULE_WEG and not p.name.startswith("test_"):
            dateien.append(p)
    dateien += [prog / n for n in PROGRAMM_DATEIEN if (prog / n).is_file()]
    for o in PROGRAMM_ORDNER:
        dateien += [p for p in sorted((prog / o).rglob("*")) if p.is_file() and not p.is_symlink()]
    dateien += [p for p in sorted((prog / "modelle").glob("*"))
                if p.is_file() and (p.suffix != ".npz" or p.stat().st_size <= MODELL_KLEIN)]
    puffer = io.BytesIO()
    namen = []
    with zipfile.ZipFile(puffer, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in dateien:
            rel = p.relative_to(prog).as_posix()
            if NUTZERDATEN.search(rel) or p.suffix in (".pyc", ".tmp", ".bak", ".icns"):
                continue
            info = zipfile.ZipInfo(rel, ZEIT)
            info.compress_type = zipfile.ZIP_STORED if p.suffix.lower() in (".jpg", ".png", ".npz") else zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, p.read_bytes())
            namen.append(rel)
    return puffer.getvalue(), namen


def oberflaeche():
    """ui/index.html → index.html (Startbildschirm, Manifest, CSP, relative Adressen) + ui.js (das Skript der Seite)."""
    html = (QUELLE / "Programm" / "ui" / "index.html").read_text(encoding="utf-8")
    m = re.search(r'<script nonce="__NONCE__">\n(.*?)</script>', html, re.S)
    skript = m.group(1)
    for alt, neu in (('const TOKEN = "__GL_TOKEN__";', 'const TOKEN = "app";'),
                     ('const AM_HANDY = "__GL_HANDY__" === "1";', 'const AM_HANDY = "1" === "1";'),
                     ('const AM_APP = "__GL_APP__" === "1";', 'const AM_APP = "1" === "1";')):
        assert skript.count(alt) == 1, alt
        skript = skript.replace(alt, neu)
    kopf = f'''<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data:; font-src 'self'; connect-src 'self'; worker-src 'self'; manifest-src 'self'; media-src 'self' blob:; object-src 'none'; base-uri 'none'; form-action 'none'">
<meta name="description" content="Picture flash cards with goose puns: make, print and learn them – also offline. Bildkarten mit Gänse-Wortwitz. Tarjetas con juegos de palabras de gansos.">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Goos-ta">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<link rel="manifest" href="manifest.webmanifest">'''
    start_css = '''<style>
.app-start { position: fixed; inset: 0; z-index: 200; display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 10px; padding: 24px; background: var(--himmel); color: var(--nacht); text-align: center; font-family: var(--schrift); transition: opacity .3s; }
.app-start.weg { opacity: 0; pointer-events: none; }
.app-start img { width: 104px; height: 104px; }
.app-start b { font-size: 22px; }
.app-start-ente { margin: 6px 0 0; font: 15px/1.15 ui-monospace, Menlo, Consolas, monospace; color: var(--nacht-2); white-space: pre; }
.app-start-ente .s { color: var(--schnabel-dunkel); font-weight: 700; }
.app-start-ente .w1 { color: var(--nacht-3); }
.app-start-ente .w2 { color: var(--wasser); }
.app-start-balken { width: min(320px, 80vw); height: 8px; border-radius: 4px; background: var(--wasser-hell); overflow: hidden; }
.app-start-balken > div { width: 0; height: 100%; background: var(--schnabel); transition: width .2s; }
#app-start-text { max-width: 420px; }
</style>'''
    start = '''<div class="app-start" id="app-start" role="status" aria-live="polite">
  <img src="symbol.svg" alt=""><b>Me Goos-ta Deutsch</b>
  <pre class="app-start-ente" id="app-start-ente" aria-hidden="true"></pre>
  <span id="app-start-text"></span>
  <div class="app-start-balken" hidden><div id="app-start-balken"></div></div>
  <button class="knopf" type="button" id="app-start-nochmal" hidden></button>
</div>
'''
    ersatz = (('<html lang="__SPRACHE__">', '<html lang="en">'),
              ('<meta name="viewport" content="width=device-width, initial-scale=1">', kopf),
              ('<meta name="theme-color" content="__GL_THEME__">', f'<meta name="theme-color" content="{VORDERGRUND}">'),
              ('<link rel="icon" href="/favicon.ico">', '<link rel="icon" href="favicon.ico">\n<link rel="icon" type="image/svg+xml" href="symbol.svg">'),
              ('<link rel="apple-touch-icon" href="/apple-touch-icon.png">', '<link rel="apple-touch-icon" href="symbole/apple-touch-icon.png">'),
              ('<style id="farben-vars">/*__GL_FARBEN__*/</style>\n</head>', '<style id="farben-vars"></style>\n' + start_css + '\n</head>'),
              ('<body>\n', '<body>\n' + start),
              (m.group(0), '<script src="app.js"></script>'))
    for alt, neu in ersatz:
        assert html.count(alt) == 1, alt
        html = html.replace(alt, neu)
    html = html.replace('url("/schrift/', 'url("schrift/').replace('src="/symbol.svg"', 'src="symbol.svg"')
    assert "__GL_" not in html and "__NONCE__" not in html and "__SPRACHE__" not in html
    return html, skript


def symbole():
    """Symbole aus assets/me-goosta-symbol.*: 192/512 (any), 512 maskable (Sicherheitszone), Apple 180 (ohne Transparenz)."""
    from PIL import Image
    a = QUELLE / "Programm" / "assets"
    gross = Image.open(a / "me-goosta-symbol.png").convert("RGBA")          # 512 × 512
    def png(im):
        b = io.BytesIO()
        im.save(b, "PNG", optimize=True)
        return b.getvalue()
    def auf_grund(kante, anteil, farbe):
        im = Image.new("RGBA", (kante, kante), farbe)
        s = round(kante * anteil)
        klein = gross.resize((s, s), Image.LANCZOS)
        im.alpha_composite(klein, ((kante - s) // 2, (kante - s) // 2))
        return im
    return {"symbole/symbol-192.png": png(gross.resize((192, 192), Image.LANCZOS)),
            "symbole/symbol-512.png": png(gross.resize((512, 512), Image.LANCZOS)),
            "symbole/symbol-maskable-512.png": png(auf_grund(512, 0.78, HINTERGRUND)),
            "symbole/apple-touch-icon.png": png(auf_grund(180, 0.9, HINTERGRUND).convert("RGB")),
            "symbol.svg": (a / "me-goosta-symbol.svg").read_bytes(),
            "favicon.ico": (a / "me-goosta-symbol.ico").read_bytes()}


def manifest(version):
    symbol = lambda q, g, z="any": {"src": q, "sizes": g, "type": "image/png", "purpose": z}   # noqa: E731
    return json.dumps({
        "id": "./", "name": "Me Goos-ta Deutsch", "short_name": "Goos-ta",
        "description": "Picture flash cards with goose puns: make, print and learn them – also offline.",
        "lang": "en", "dir": "ltr", "start_url": "./", "scope": "./", "display": "standalone",
        "orientation": "any", "background_color": HINTERGRUND, "theme_color": VORDERGRUND,
        "categories": ["education", "productivity"],
        "icons": [symbol("symbole/symbol-192.png", "192x192"), symbol("symbole/symbol-512.png", "512x512"),
                  symbol("symbole/symbol-maskable-512.png", "512x512", "maskable"),
                  {"src": "symbol.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any"}],
        "shortcuts": [{"name": "Learn cards", "short_name": "Learn", "url": "./#lernen",
                       "icons": [symbol("symbole/symbol-192.png", "192x192")]},
                      {"name": "New card", "short_name": "New", "url": "./#bild",
                       "icons": [symbol("symbole/symbol-192.png", "192x192")]}],
        "x_version": version}, ensure_ascii=False, indent=1)


PYODIDE_LIZENZ = """Pyodide {v} – Python für den Browser (WebAssembly)
Lizenz: Mozilla Public License 2.0 (MPL-2.0) – https://www.mozilla.org/MPL/2.0/
Quelltext: https://github.com/pyodide/pyodide (Tag {v}); unverändert mitgeliefert (pyodide/).
Enthält CPython (Python Software Foundation License) und Pakete mit eigenen Lizenzen, die jeweils in ihren Rädern
(*.whl → *.dist-info) mitgeliefert werden: NumPy (BSD-3-Clause), Pillow (MIT-CMU), charset-normalizer (MIT), ReportLab (BSD).
Weitere Angaben: DRITTLIZENZEN.md.
"""


def programm_version():
    return re.search(r'^VERSION = "([\d.]+)', (QUELLE / "Programm" / "gans_lernkarten.py").read_text(encoding="utf-8"), re.M)[1]


def bauen(ziel, ohne_pyodide=False, ohne_modelle=False, cache=None, release_zip=None):
    out = ziel / "web-app"
    version = programm_version()
    zip_info = release_info(release_zip, version) if release_zip else None   # vor dem Löschen prüfen
    if out.exists():
        if not (out / "sw.js").is_file():
            sys.exit(f"{out} gibt es schon und ist keine Web-App – bitte erst umbenennen oder entfernen.")
        shutil.rmtree(out)
    dateien = {}                                                # Pfad → Bytes (Offline-Paket, im Service Worker gelistet)
    index, ui = oberflaeche()
    dateien["index.html"], dateien["ui.js"] = index.encode("utf-8"), ui.encode("utf-8")
    dateien["app.js"] = (QUELLE_WEB / "app.js").read_bytes()
    dateien.update(symbole())
    for n in ("Poppins-Regular.ttf", "Poppins-Medium.ttf", "Poppins-Bold.ttf"):
        dateien[f"schrift/{n}"] = (QUELLE / "Programm" / "schrift" / n).read_bytes()
    zip_daten, zip_namen = programm_zip()
    programm_hash = sha(zip_daten)[:16]
    dateien["py/programm.zip"] = zip_daten
    dateien["lizenzen/LICENSE.txt"] = (QUELLE / "LICENSE.txt").read_bytes()
    dateien["lizenzen/DRITTLIZENZEN.md"] = (QUELLE / "Programm" / "DRITTLIZENZEN.md").read_bytes()
    dateien["lizenzen/OFL-Poppins.txt"] = (QUELLE / "Programm" / "schrift" / "OFL-Poppins.txt").read_bytes()
    dateien["lizenzen/PYODIDE.txt"] = PYODIDE_LIZENZ.format(v=PYODIDE).encode("utf-8")
    pakete, reportlab = [], f"{REPORTLAB[0]}-{REPORTLAB[1]}-py3-none-any.whl"
    if not ohne_pyodide:
        pyo, pakete, reportlab = pyodide_dateien(Path(cache or Path(tempfile.gettempdir()) / "mgd-webapp-cache"))
        for n, d in pyo.items():
            dateien[f"pyodide/{n}"] = d
    modelle = {}
    if not ohne_modelle:
        for p in sorted((QUELLE / "Programm" / "modelle").glob("realesrgan-*.npz")):
            d = p.read_bytes()
            modelle[p.name] = (d, dict(groesse=len(d), sha256=sha(d)))
    dateien["modelle/modelle.json"] = json.dumps({n: m for n, (_, m) in modelle.items()}, indent=1).encode("utf-8")
    worker = (QUELLE_WEB / "worker.js").read_text(encoding="utf-8")
    for alt, neu in (("__PROGRAMM__", "py/programm.zip"), ("__PROGRAMM_HASH__", programm_hash),
                     ("__REPORTLAB__", f"pyodide/{reportlab}"), ("__PAKETE__", json.dumps(pakete))):
        assert worker.count(alt) == 1, alt
        worker = worker.replace(alt, neu)
    dateien["worker.js"] = worker.encode("utf-8")
    sw = (QUELLE_WEB / "sw.js").read_text(encoding="utf-8")
    inhalt = hashlib.sha256(sw.encode("utf-8"))                 # Version = Inhalt aller Dateien + Service Worker
    for n in sorted(dateien):
        inhalt.update(n.encode() + b"\0" + hashlib.sha256(dateien[n]).digest())
    app_version = f"{version}-{inhalt.hexdigest()[:10]}"
    dateien["manifest.webmanifest"] = manifest(app_version).encode("utf-8")
    liste = [[n, len(d), sha(d)[:16]] for n, d in sorted(dateien.items())]
    sw = sw.replace('"__VERSION__"', json.dumps(app_version)).replace("__DATEIEN__", json.dumps(liste, separators=(",", ":")))
    for n, d in dateien.items():
        z = out / n
        z.parent.mkdir(parents=True, exist_ok=True)
        z.write_bytes(d)
    (out / "sw.js").write_text(sw, encoding="utf-8")
    (out / ".nojekyll").write_bytes(b"")                       # GitHub Pages: Dateien unverändert ausliefern
    for n, (d, _) in modelle.items():
        (out / "modelle" / n).write_bytes(d)
    seite = downloadseite_schreiben(out, version, zip_info, release_zip is not None)   # nicht in der Liste des Service Workers
    return out, app_version, liste, zip_namen, modelle, seite


# ---------- Installationsdateien Android / iPhone / Google Pixel (statisch, ohne JavaScript, de/en/es) ----------
INSTALL_DATEIEN = {"android": "Me Goos-ta Deutsch - Android.html", "iphone": "Me Goos-ta Deutsch - iPhone.html",
                   "pixel": "Me Goos-ta Deutsch - Google Pixel.html"}

IT = {   # gemeinsame Texte (dürfen <b> enthalten; {adresse}/{host} werden eingesetzt)
    "de": dict(
        sprache="Deutsch", knopf="App öffnen", qr_aria="QR-Code mit der Adresse der App",
        lead="Die Gans zum Mitnehmen: Lernkarten anlegen, drucken und lernen – als echte App auf deinem Handy, auch "
             "ganz ohne Internet. Kostenlos, ohne Konto, ohne Werbung.",
        qr_text="Am Rechner? Halte die Handy-Kamera auf den Code und tippe auf den Link.",
        weg_titel="Wie kommt diese Datei aufs Handy?",
        weg=["<b>Am einfachsten gar nicht:</b> Öffne diese Datei am Rechner (Doppelklick) und scanne den QR-Code mit "
             "der Handy-Kamera.",
             "<b>Oder schick sie dir selbst</b> – per E-Mail, Messenger oder Cloud – und öffne sie am Handy. Dann "
             "einfach auf „App öffnen“ tippen.",
             "<b>Oder tippe die Adresse ab:</b> <span class=\"pfad\">{adresse}</span>"],
        schritte_titel="In vier Schritten zur App", brauchst_titel="Was du brauchst",
        platz="Etwa 100 MB freien Speicher (die App selbst hat gut 20 MB, dazu kommen deine Karten und Bilder).",
        netz="Internet nur beim ersten Start und für Updates – danach watschelt alles auch offline.",
        kann_titel="Was die App kann",
        kann="Fast alles wie am Rechner: Karten anlegen und bearbeiten, Bilder verbessern, Druck-PDFs und Prüfbogen, "
             "digitale Lernkarten, Karten lernen, weitere Sprachen. Nur die KI-Bilder (großes Modell) und das Öffnen "
             "von Ordnern gibt es ausschließlich am Rechner.",
        daten_titel="Deine Daten bleiben bei dir",
        daten="Die App holt nur ihre Programmdateien von <b>{host}</b> (GitHub Pages). Deine Karten, Bilder, Ideen und "
              "dein Lernstand liegen nur auf deinem Gerät – kein Konto, keine Cloud, keine Werbung, kein Tracking. Nur "
              "wenn du die automatische Übersetzung einschaltest, geht das einzelne Wort an den gewählten Dienst.",
        sicherung_titel="Sichern und Karten vom Rechner holen",
        sicherung=["<b>Sichern:</b> In der App „Mehr“ → „💾 Sicherung & Speicher“ → „Alles sichern“. Das ergibt eine "
                   "Datei mit allem – zum Aufheben oder für ein neues Handy („Sicherung einspielen“).",
                   "<b>Karten vom Rechner:</b> Am Rechner „Meine Karten“ → „⇅ Import / Export“ → „Alles – "
                   "Komplettsicherung“ exportieren, die Datei aufs Handy schicken und in der App unter „💾 Sicherung & "
                   "Speicher“ → „Karten vom Rechner übernehmen“ importieren – samt Lernstand."],
        update_titel="Updates und Entfernen",
        update="Updates kommen von selbst: Ist eine neue Gänse-Version da, fragt die App „Neu laden?“ – deine Daten "
               "bleiben, wo sie sind.",
        auch="Dieselbe Anleitung für", rechner="Am Rechner",
        fuss="Me Goos-ta Deutsch · MIT-Lizenz · © Eine Gans namens Lukas"),
    "en": dict(
        sprache="English", knopf="Open the app", qr_aria="QR code with the app’s address",
        lead="The take-away goose: create, print and study your flash cards – as a real app on your phone, even "
             "completely offline. Free, no account, no ads.",
        qr_text="On a computer? Point your phone’s camera at the code and tap the link.",
        weg_titel="How does this file get onto your phone?",
        weg=["<b>Easiest: it doesn’t have to.</b> Open this file on your computer (double-click) and scan the QR code "
             "with your phone’s camera.",
             "<b>Or send it to yourself</b> – by e-mail, messenger or cloud – and open it on your phone. Then simply "
             "tap “Open the app”.",
             "<b>Or type in the address:</b> <span class=\"pfad\">{adresse}</span>"],
        schritte_titel="Four steps to the app", brauchst_titel="What you need",
        platz="About 100 MB of free storage (the app itself is just over 20 MB, plus your cards and pictures).",
        netz="Internet only for the first start and for updates – after that everything waddles along offline too.",
        kann_titel="What the app can do",
        kann="Almost everything the computer version does: create and edit cards, enhance pictures, print PDFs and "
             "check sheets, digital flash cards, studying cards, more languages. Only the AI pictures (big model) and "
             "opening folders are computer-only.",
        daten_titel="Your data stays with you",
        daten="The app only fetches its program files from <b>{host}</b> (GitHub Pages). Your cards, pictures, ideas "
              "and learning progress live only on your device – no account, no cloud, no ads, no tracking. Only if you "
              "switch on automatic translation does the single word go to the service you chose.",
        sicherung_titel="Backups and cards from the computer",
        sicherung=["<b>Back up:</b> in the app, “More” → “💾 Backup & storage” → “Back up everything”. That gives you "
                   "one file with everything – to keep, or for a new phone (“Restore backup”).",
                   "<b>Cards from the computer:</b> on the computer, “My cards” → “⇅ Import / export” → export "
                   "“Everything – full backup”, send the file to your phone and import it in the app under “💾 Backup & "
                   "storage” → “Take over cards from the computer” – learning progress included."],
        update_titel="Updates and removing",
        update="Updates arrive by themselves: when a new goose version is here, the app asks “Reload?” – your data "
               "stays where it is.",
        auch="The same guide for", rechner="On the computer",
        fuss="Me Goos-ta Deutsch · MIT License · © Eine Gans namens Lukas"),
    "es": dict(
        sprache="Español", knopf="Abrir la app", qr_aria="Código QR con la dirección de la app",
        lead="El ganso para llevar: crea, imprime y estudia tus cartas, como app de verdad en tu celular, incluso sin "
             "internet. Gratis, sin cuenta y sin anuncios.",
        qr_text="¿Estás en la computadora? Apunta la cámara del celular al código y toca el enlace.",
        weg_titel="¿Cómo llega este archivo a tu celular?",
        weg=["<b>Lo más fácil: ni hace falta.</b> Abre este archivo en la computadora (doble clic) y escanea el código "
             "QR con la cámara del celular.",
             "<b>O envíatelo a ti mismo</b> (por correo, mensajería o la nube) y ábrelo en el celular. Luego solo toca "
             "«Abrir la app».",
             "<b>O escribe la dirección:</b> <span class=\"pfad\">{adresse}</span>"],
        schritte_titel="La app en cuatro pasos", brauchst_titel="Lo que necesitas",
        platz="Unos 100 MB libres (la app ocupa poco más de 20 MB, más tus cartas e imágenes).",
        netz="Internet solo la primera vez y para actualizaciones; después todo funciona también sin conexión.",
        kann_titel="Lo que puede hacer la app",
        kann="Casi todo lo de la computadora: crear y editar cartas, mejorar imágenes, PDF para imprimir y hojas de "
             "revisión, tarjetas digitales, estudiar cartas, más idiomas. Solo las imágenes con IA (modelo grande) y "
             "abrir carpetas son exclusivas de la computadora.",
        daten_titel="Tus datos se quedan contigo",
        daten="La app solo descarga sus archivos de programa desde <b>{host}</b> (GitHub Pages). Tus cartas, imágenes, "
              "ideas y tu avance de aprendizaje están solo en tu dispositivo: sin cuenta, sin nube, sin anuncios, sin "
              "rastreo. Solo si activas la traducción automática, la palabra suelta va al servicio que elegiste.",
        sicherung_titel="Copias de seguridad y cartas de la computadora",
        sicherung=["<b>Respaldar:</b> en la app, «Más» → «💾 Copia y almacenamiento» → «Respaldar todo». Así tienes un "
                   "archivo con todo, para guardarlo o para un celular nuevo («Restaurar copia»).",
                   "<b>Cartas de la computadora:</b> en la computadora, «Mis cartas» → «⇅ Importar / exportar» → exporta "
                   "«Todo: copia de seguridad completa», envía el archivo al celular e impórtalo en la app en «💾 Copia "
                   "y almacenamiento» → «Traer cartas de la computadora», con tu avance de aprendizaje."],
        update_titel="Actualizaciones y desinstalar",
        update="Las actualizaciones llegan solas: cuando hay una nueva versión del ganso, la app pregunta «¿Recargar?» "
               "y tus datos se quedan donde están.",
        auch="La misma guía para", rechner="En la computadora",
        fuss="Me Goos-ta Deutsch · Licencia MIT · © Eine Gans namens Lukas"),
}

# je Gerät: Name, Überschrift, vier Schritte (Titel, Text, Skizze, Beschriftungen der Skizze), Voraussetzung, Entfernen
IG = {
    "android": {
        "de": dict(name="Android", h1="Me Goos-ta Deutsch auf deinem Android-Handy", schritte=[
            ("Adresse öffnen", "Tippe oben auf „App öffnen“ oder scanne den QR-Code und tippe auf den Link – am besten "
             "in <b>Chrome</b>. Beim ersten Start lädt die Gans gut 20 MB: kurz durchschnaufen.", "kamera"),
            ("Menü ⋮ öffnen", "Tippe in Chrome oben rechts auf die drei Punkte <b>⋮</b>. Zeigt die Gans unten schon "
             "„Als App installieren“, geht es auch direkt dort.", "punkte"),
            ("„App installieren“", "Tippe auf <b>„App installieren“</b> (manche Chrome-Versionen sagen „Zum "
             "Startbildschirm hinzufügen“) und bestätige mit <b>„Installieren“</b>.", "menue", "App installieren"),
            ("Fertig!", "Die Gans erscheint auf dem Startbildschirm und bei deinen Apps – ab jetzt startet sie wie jede "
             "andere App, im Vollbild und auch offline.", "start")],
            brauchst="Android 10 oder neuer mit aktuellem <b>Chrome</b>. Andere Browser (z. B. Samsung Internet, Edge) "
                     "können es meist auch – mit Chrome klappt es am sichersten.",
            entfernen="Entfernen: App-Symbol lange drücken → „Deinstallieren“ (bzw. „App-Info“ → „Deinstallieren“). "
                      "Dabei gehen auch die Daten der App – vorher sichern."),
        "en": dict(name="Android", h1="Me Goos-ta Deutsch on your Android phone", schritte=[
            ("Open the address", "Tap “Open the app” above or scan the QR code and tap the link – ideally in "
             "<b>Chrome</b>. On the first start the goose loads just over 20 MB: time for a short breather.", "kamera"),
            ("Open the ⋮ menu", "In Chrome, tap the three dots <b>⋮</b> at the top right. If the goose already shows "
             "“Install as an app” at the bottom, you can do it right there.", "punkte"),
            ("“Install app”", "Tap <b>“Install app”</b> (some Chrome versions say “Add to Home screen”) and confirm "
             "with <b>“Install”</b>.", "menue", "Install app"),
            ("Done!", "The goose appears on your home screen and with your apps – from now on it starts like any other "
             "app, full screen and offline too.", "start")],
            brauchst="Android 10 or later with an up-to-date <b>Chrome</b>. Other browsers (e.g. Samsung Internet, "
                     "Edge) can usually do it too – Chrome is the safest bet.",
            entfernen="Removing: press and hold the app icon → “Uninstall” (or “App info” → “Uninstall”). This also "
                      "removes the app’s data – back up first."),
        "es": dict(name="Android", h1="Me Goos-ta Deutsch en tu celular Android", schritte=[
            ("Abre la dirección", "Toca «Abrir la app» arriba o escanea el código QR y toca el enlace, mejor en "
             "<b>Chrome</b>. La primera vez el ganso descarga poco más de 20 MB: dale un momento.", "kamera"),
            ("Abre el menú ⋮", "En Chrome, toca los tres puntos <b>⋮</b> arriba a la derecha. Si el ganso ya muestra "
             "«Instalar como app» abajo, también puedes hacerlo ahí.", "punkte"),
            ("«Instalar app»", "Toca <b>«Instalar app»</b> (algunas versiones de Chrome dicen «Agregar a la pantalla "
             "principal») y confirma con <b>«Instalar»</b>.", "menue", "Instalar app"),
            ("¡Listo!", "El ganso aparece en tu pantalla principal y junto a tus apps: desde ahora abre como cualquier "
             "otra app, en pantalla completa e incluso sin conexión.", "start")],
            brauchst="Android 10 o posterior con <b>Chrome</b> actualizado. Otros navegadores (p. ej. Samsung Internet, "
                     "Edge) suelen poder también; con Chrome es lo más seguro.",
            entfernen="Desinstalar: mantén presionado el ícono de la app → «Desinstalar» (o «Información de la app» → "
                      "«Desinstalar»). Así también se borran los datos de la app: respalda antes."),
    },
    "iphone": {
        "de": dict(name="iPhone & iPad", h1="Me Goos-ta Deutsch auf deinem iPhone oder iPad", schritte=[
            ("Adresse in Safari öffnen", "Tippe oben auf „App öffnen“ oder scanne den QR-Code mit der Kamera-App und "
             "tippe auf den Link – in <b>Safari</b>. Beim ersten Start lädt die Gans gut 20 MB: kurz durchschnaufen.",
             "kamera"),
            ("„Teilen“ antippen", "Tippe in Safari auf <b>„Teilen“</b> (Quadrat mit Pfeil nach oben) – unten in der "
             "Leiste; bei neueren iOS-Versionen zuerst auf <b>„⋯“</b>.", "teilen"),
            ("„Zum Home-Bildschirm“", "Wähle <b>„Zum Home-Bildschirm“</b> – eventuell etwas nach unten scrollen. Steht "
             "dort „Als Web-App öffnen“: eingeschaltet lassen.", "liste", "Zum Home-Bildschirm"),
            ("„Hinzufügen“ – fertig!", "Tippe oben rechts auf <b>„Hinzufügen“</b>. Die Gans watschelt auf deinen "
             "Home-Bildschirm und startet ab jetzt wie eine richtige App, auch offline.", "hinzufuegen",
             "Hinzufügen", "Als Web-App öffnen")],
            brauchst="iPhone oder iPad mit <b>iOS bzw. iPadOS 16.4</b> oder neuer, am besten mit <b>Safari</b>.",
            hinweis="Wichtig am iPhone/iPad: Nur in der installierten App bleiben deine Daten dauerhaft – Safari "
                    "löscht Website-Daten sonst nach 7 Tagen ohne Besuch. Also erst installieren, dann loslegen.",
            entfernen="Entfernen: App-Symbol lange drücken → „App entfernen“. Dabei gehen auch die Daten der App – "
                      "vorher sichern."),
        "en": dict(name="iPhone & iPad", h1="Me Goos-ta Deutsch on your iPhone or iPad", schritte=[
            ("Open the address in Safari", "Tap “Open the app” above or scan the QR code with the Camera app and tap "
             "the link – in <b>Safari</b>. On the first start the goose loads just over 20 MB: time for a short breather.",
             "kamera"),
            ("Tap “Share”", "In Safari, tap <b>“Share”</b> (square with an arrow pointing up) – in the bar at the "
             "bottom; on newer iOS versions tap <b>“⋯”</b> first.", "teilen"),
            ("“Add to Home Screen”", "Choose <b>“Add to Home Screen”</b> – you may need to scroll down a little. If you "
             "see “Open as Web App”: leave it switched on.", "liste", "Add to Home Screen"),
            ("“Add” – done!", "Tap <b>“Add”</b> at the top right. The goose waddles onto your home screen and from now "
             "on starts like a real app, offline too.", "hinzufuegen", "Add", "Open as Web App")],
            brauchst="iPhone or iPad with <b>iOS or iPadOS 16.4</b> or later, ideally with <b>Safari</b>.",
            hinweis="Important on iPhone/iPad: your data only stays for good in the installed app – otherwise Safari "
                    "deletes website data after 7 days without a visit. So install first, then get going.",
            entfernen="Removing: press and hold the app icon → “Remove App”. This also removes the app’s data – back "
                      "up first."),
        "es": dict(name="iPhone y iPad", h1="Me Goos-ta Deutsch en tu iPhone o iPad", schritte=[
            ("Abre la dirección en Safari", "Toca «Abrir la app» arriba o escanea el código QR con la app Cámara y "
             "toca el enlace, en <b>Safari</b>. La primera vez el ganso descarga poco más de 20 MB: dale un momento.",
             "kamera"),
            ("Toca «Compartir»", "En Safari, toca <b>«Compartir»</b> (cuadrado con una flecha hacia arriba) en la "
             "barra de abajo; en versiones nuevas de iOS, primero toca <b>«⋯»</b>.", "teilen"),
            ("«Agregar a pantalla de inicio»", "Elige <b>«Agregar a pantalla de inicio»</b>; quizá tengas que "
             "desplazarte un poco. Si aparece «Abrir como app web», déjalo activado.", "liste",
             "Agregar a inicio"),
            ("«Agregar»: ¡listo!", "Toca <b>«Agregar»</b> arriba a la derecha. El ganso se va anadeando a tu pantalla "
             "de inicio y desde ahora abre como una app de verdad, incluso sin conexión.", "hinzufuegen",
             "Agregar", "Abrir como app web")],
            brauchst="iPhone o iPad con <b>iOS o iPadOS 16.4</b> o posterior, mejor con <b>Safari</b>.",
            hinweis="Importante en iPhone/iPad: tus datos solo se quedan para siempre en la app instalada; si no, "
                    "Safari borra los datos del sitio tras 7 días sin visitarlo. Así que primero instala y luego empieza.",
            entfernen="Desinstalar: mantén presionado el ícono de la app → «Eliminar app». Así también se borran los "
                      "datos de la app: respalda antes."),
    },
    "pixel": {
        "de": dict(name="Google Pixel", h1="Me Goos-ta Deutsch auf deinem Google Pixel", schritte=[
            ("Adresse in Chrome öffnen", "Tippe oben auf „App öffnen“ oder halte die Pixel-Kamera auf den QR-Code und "
             "tippe auf den Link. <b>Chrome</b> ist auf jedem Pixel schon dabei. Beim ersten Start lädt die Gans gut "
             "20 MB.", "kamera"),
            ("Menü ⋮ öffnen", "Tippe oben rechts auf die drei Punkte <b>⋮</b>. Zeigt die Gans unten schon „Als App "
             "installieren“, geht es auch direkt dort.", "punkte"),
            ("„Zum Startbildschirm hinzufügen“", "Tippe auf <b>„Zum Startbildschirm hinzufügen“</b> (bzw. „App "
             "installieren“) und dann auf <b>„Installieren“</b>.", "menue", "Zum Startbildschirm"),
            ("Fertig!", "Die Gans sitzt auf dem Startbildschirm. In der App-Übersicht findest du sie, wenn du vom "
             "unteren Rand nach oben wischst – sie startet wie jede andere App, auch offline.", "uebersicht")],
            brauchst="Jedes Google Pixel mit aktuellem Android. <b>Chrome</b> ist vorinstalliert – bitte aktuell halten "
                     "(Play Store → Profilbild → „Apps und Gerät verwalten“ → Updates).",
            entfernen="Entfernen: App-Symbol lange drücken → „App-Info“ → „Deinstallieren“. Dabei gehen auch die Daten "
                      "der App – vorher sichern."),
        "en": dict(name="Google Pixel", h1="Me Goos-ta Deutsch on your Google Pixel", schritte=[
            ("Open the address in Chrome", "Tap “Open the app” above or point the Pixel camera at the QR code and tap "
             "the link. <b>Chrome</b> comes with every Pixel. On the first start the goose loads just over 20 MB.",
             "kamera"),
            ("Open the ⋮ menu", "Tap the three dots <b>⋮</b> at the top right. If the goose already shows “Install as "
             "an app” at the bottom, you can do it right there.", "punkte"),
            ("“Add to Home screen”", "Tap <b>“Add to Home screen”</b> (or “Install app”) and then <b>“Install”</b>.",
             "menue", "Add to Home screen"),
            ("Done!", "The goose sits on your home screen. You’ll find it in the app drawer by swiping up from the "
             "bottom edge – it starts like any other app, offline too.", "uebersicht")],
            brauchst="Any Google Pixel with current Android. <b>Chrome</b> is preinstalled – please keep it up to date "
                     "(Play Store → profile picture → “Manage apps & device” → updates).",
            entfernen="Removing: press and hold the app icon → “App info” → “Uninstall”. This also removes the app’s "
                      "data – back up first."),
        "es": dict(name="Google Pixel", h1="Me Goos-ta Deutsch en tu Google Pixel", schritte=[
            ("Abre la dirección en Chrome", "Toca «Abrir la app» arriba o apunta la cámara del Pixel al código QR y "
             "toca el enlace. <b>Chrome</b> ya viene en todos los Pixel. La primera vez el ganso descarga poco más de 20 MB.",
             "kamera"),
            ("Abre el menú ⋮", "Toca los tres puntos <b>⋮</b> arriba a la derecha. Si el ganso ya muestra «Instalar "
             "como app» abajo, también puedes hacerlo ahí.", "punkte"),
            ("«Agregar a la pantalla principal»", "Toca <b>«Agregar a la pantalla principal»</b> (o «Instalar app») y "
             "luego <b>«Instalar»</b>.", "menue", "Agregar a pantalla"),
            ("¡Listo!", "El ganso está en tu pantalla principal. En el panel de apps lo encuentras deslizando hacia "
             "arriba desde el borde inferior; abre como cualquier otra app, incluso sin conexión.", "uebersicht")],
            brauchst="Cualquier Google Pixel con Android actual. <b>Chrome</b> viene instalado; mantenlo actualizado "
                     "(Play Store → foto de perfil → «Administrar apps y dispositivo» → actualizaciones).",
            entfernen="Desinstalar: mantén presionado el ícono de la app → «Información de la app» → «Desinstalar». "
                      "Así también se borran los datos de la app: respalda antes."),
    },
}

# Skizzen: Strichzeichnung eines Handys (Schriftfarbe), das Wichtige in Akzentfarbe (Klasse hl)
_GERAET = ('<rect x="3" y="3" width="114" height="194" rx="16"/><rect class="d" x="9" y="14" width="102" height="172" '
           'rx="5"/><path class="d" d="M50 8.5h20"/>')
_GANS = ('<rect class="hl" x="{x}" y="{y}" width="22" height="22" rx="6"/><circle class="f" cx="{cx}" cy="{cy}" r="4.5"/>'
         '<path class="f s" d="M{bx} {by}l6 1.5-6 1.5z"/>')


def _gans(x, y):
    return _GANS.format(x=x, y=y, cx=x + 10, cy=y + 10, bx=x + 14, by=y + 8.5)


def _beschriftung(text, x, y, mitte=False, klasse="hl"):
    g = 7 if len(text) <= 16 else 6 if len(text) <= 20 else 5.2
    a = ' text-anchor="middle"' if mitte else ""
    return f'<text class="{klasse}" x="{x}" y="{y}" font-size="{g}"{a}>{html_esc(text)}</text>'


def _icons(zeilen, ausser=None):
    teile = []
    for r in range(zeilen):
        for c in range(4):
            if (r, c) != ausser:
                teile.append(f'<rect class="d" x="{17 + c * 23}" y="{34 + r * 26}" width="18" height="18" rx="5"/>')
    return "".join(teile)


def skizze(art, beschriftung=(), titel=""):
    b = list(beschriftung) + ["", ""]
    if art == "kamera":            # Kamera auf dem QR-Code, Link antippen
        innen = ('<path d="M28 58V46h12M80 46h12v12M92 106v12H80M40 118H28v-12"/>'
                 '<rect class="f" x="38" y="56" width="14" height="14"/><rect class="f" x="68" y="56" width="14" height="14"/>'
                 '<rect class="f" x="38" y="94" width="14" height="14"/><rect class="f" x="58" y="76" width="6" height="6"/>'
                 '<rect class="f" x="70" y="86" width="6" height="6"/><rect class="f" x="62" y="98" width="8" height="8"/>'
                 '<rect class="f" x="76" y="100" width="6" height="6"/>'
                 '<rect class="hl" x="18" y="138" width="84" height="18" rx="9"/>'
                 '<path class="hl" d="M60 166v10M55 171l5 5 5-5" transform="rotate(180 60 171)"/>'
                 + _beschriftung("github.io", 60, 150, True))
    elif art == "punkte":          # Chrome: Adressleiste, ⋮ oben rechts
        innen = ('<rect x="14" y="20" width="74" height="14" rx="7"/><text class="t" x="22" y="30" font-size="7">github.io</text>'
                 '<circle class="f" cx="100" cy="23" r="1.6"/><circle class="f" cx="100" cy="27" r="1.6"/>'
                 '<circle class="f" cx="100" cy="31" r="1.6"/><circle class="hl" cx="100" cy="27" r="8"/>'
                 '<rect class="d" x="22" y="48" width="76" height="56" rx="6"/>' + _gans(49, 65)
                 + '<path class="d" d="M22 118h76M22 130h56M22 142h66M22 154h44"/>')
    elif art == "menue":           # Chrome-Menü mit hervorgehobenem Eintrag
        innen = ('<rect class="d" x="14" y="20" width="74" height="14" rx="7"/>'
                 '<rect x="28" y="22" width="80" height="104" rx="4"/>'
                 '<path class="d" d="M36 36h40M36 50h52M36 64h34"/>'
                 '<rect class="hl" x="31" y="73" width="74" height="16" rx="3"/>' + _beschriftung(b[0], 36, 84)
                 + '<path class="d" d="M36 100h46M36 114h30"/>')
    elif art == "start":           # Startbildschirm mit der Gans
        innen = _icons(4, ausser=(2, 1)) + _gans(38, 84) + '<rect class="d" x="16" y="160" width="88" height="20" rx="8"/>'
    elif art == "uebersicht":      # Pixel: App-Übersicht durch Wischen nach oben
        innen = (_icons(4, ausser=(1, 2)) + _gans(61, 58)
                 + '<path class="hl" d="M60 178v-26M51 160l9-9 9 9"/>')
    elif art == "teilen":          # Safari: Leiste unten, Teilen-Symbol
        innen = ('<rect class="d" x="22" y="26" width="76" height="56" rx="6"/>' + _gans(49, 43)
                 + '<path class="d" d="M22 96h76M22 108h56M22 120h66"/>'
                 '<rect x="14" y="156" width="92" height="22" rx="11"/>'
                 '<path d="M28 162l-5 5 5 5M40 162l5 5-5 5"/>'
                 '<path class="hl" d="M60 159v10M56 163l4-4 4 4M56 165h-3v9h14v-9h-3"/><circle class="hl" cx="60" cy="167" r="10"/>'
                 '<circle class="f" cx="88" cy="167" r="1.4"/><circle class="f" cx="92" cy="167" r="1.4"/><circle class="f" cx="96" cy="167" r="1.4"/>')
    elif art == "liste":           # iPhone: Teilen-Menü mit „Zum Home-Bildschirm“
        innen = ('<rect class="d" x="22" y="24" width="76" height="40" rx="6"/>'
                 '<rect x="12" y="76" width="96" height="106" rx="8"/>'
                 '<path class="d" d="M20 92h60M20 108h48"/>'
                 '<rect class="hl" x="15" y="118" width="90" height="18" rx="4"/>'
                 '<rect class="hl" x="91" y="121" width="11" height="11" rx="3"/><path class="hl" d="M96.5 123.5v6M93.5 126.5h6"/>'
                 + _beschriftung(b[0], 20, 130) + '<path class="d" d="M20 150h54M20 166h40"/>')
    elif art == "hinzufuegen":     # iPhone: „Hinzufügen“ oben rechts, Schalter „Als Web-App öffnen“
        innen = ('<path class="d" d="M16 28h20"/>' + _beschriftung(b[0], 104, 31, klasse="hl").replace('x="104"', 'x="104" text-anchor="end"')
                 + '<rect class="hl" x="66" y="20" width="42" height="16" rx="8"/>'
                 + _gans(18, 48).replace('class="hl" x="18"', 'class="d" x="18"') + '<path class="d" d="M48 54h46M48 64h30"/>'
                 '<rect class="d" x="14" y="84" width="92" height="22" rx="6"/>' + _beschriftung(b[1], 19, 98, klasse="t")
                 + '<rect class="f" x="86" y="90" width="16" height="10" rx="5"/><circle class="w" cx="97" cy="95" r="3.6"/>'
                 '<path class="d" d="M14 122h92M14 134h70"/>')
    else:
        raise ValueError(art)
    return (f'<svg class="skizze" viewBox="0 0 120 200" role="img" aria-label="{html_esc(titel)}">{_GERAET}{innen}</svg>')


def html_esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


INSTALL_CSS = """:root { --grund:#E8F2FA; --karte:#FFFFFF; --text:#1B2D4F; --leise:#4A6488; --rand:#C9DCEB; --akzent:#D7263D;
  --auf-akzent:#FFFFFF; --leiste:#F3F6FA; --kasten:#FFF6E5; --kastenrand:#F6A94B; }
@media (prefers-color-scheme: dark) {
  :root { --grund:#0F1B2E; --karte:#16243A; --text:#E6EEF8; --leise:#A9BCD6; --rand:#2C4262; --akzent:#FF5C70;
    --auf-akzent:#0F1B2E; --leiste:#22344F; --kasten:#2B2416; --kastenrand:#B98234; } }
* { box-sizing:border-box; }
html { scroll-behavior:smooth; }
body { margin:0; background:var(--grund); color:var(--text); font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; }
header { max-width:860px; margin:0 auto; padding:20px 16px 0; display:flex; align-items:center; gap:14px; flex-wrap:wrap; }
header svg { width:56px; height:56px; flex:none; }
header .name { font-weight:700; font-size:20px; flex:1; min-width:180px; }
nav.sprachen { display:flex; gap:6px; flex-wrap:wrap; }
nav.sprachen a { color:var(--text); text-decoration:none; border:1px solid var(--rand); background:var(--karte);
  padding:6px 12px; border-radius:999px; }
main { max-width:860px; margin:0 auto; padding:8px 16px 40px; }
.sprache { display:none; background:var(--karte); border:1px solid var(--rand); border-radius:16px; padding:8px 24px 20px; }
.sprache:target, #en { display:block; }
.sprache:target ~ #en { display:none; }
h1 { font-size:28px; line-height:1.2; margin:18px 0 8px; }
h2 { font-size:20px; margin:28px 0 8px; }
h3 { font-size:18px; margin:0 0 4px; }
.lead { color:var(--leise); font-size:17px; margin-top:0; }
.start { display:flex; gap:24px; align-items:center; flex-wrap:wrap; margin:18px 0 6px; }
.start .links { flex:1 1 260px; }
a.gross { display:inline-block; background:var(--akzent); color:var(--auf-akzent); font-weight:700; font-size:20px;
  text-decoration:none; padding:16px 28px; border-radius:16px; min-height:44px; }
.qr-box { flex:none; text-align:center; width:220px; max-width:100%; }
.qr-box svg { width:200px; height:200px; display:block; margin:0 auto; border-radius:8px; border:1px solid var(--rand); }
.klein { font-size:14px; color:var(--leise); }
.pfad { font-family:ui-monospace,Consolas,Menlo,monospace; font-size:14px; overflow-wrap:anywhere; }
ol.schritte { list-style:none; counter-reset:s; padding:0; margin:12px 0; }
ol.schritte > li { counter-increment:s; position:relative; padding:14px 0 14px 54px; border-top:1px solid var(--rand);
  display:flex; gap:16px; align-items:center; justify-content:space-between; }
ol.schritte > li::before { content:counter(s); position:absolute; left:0; top:14px; width:38px; height:38px; border-radius:50%;
  background:var(--akzent); color:var(--auf-akzent); font-weight:700; display:grid; place-items:center; font-size:18px; }
ol.schritte > li > div { flex:1; }
svg.skizze { width:132px; height:auto; flex:none; color:var(--text); }
svg.skizze * { fill:none; stroke:currentColor; stroke-width:2; stroke-linecap:round; stroke-linejoin:round; }
svg.skizze .d { stroke-width:1.4; opacity:.55; }
svg.skizze .hl { stroke:var(--akzent); stroke-width:2.6; }
svg.skizze .f { fill:currentColor; stroke:none; }
svg.skizze .f.s { fill:var(--kastenrand); }
svg.skizze .w { fill:var(--karte); stroke:none; }
svg.skizze text { stroke:none; fill:currentColor; font-family:system-ui,-apple-system,"Segoe UI",sans-serif; font-weight:600; }
svg.skizze text.hl { fill:var(--akzent); stroke:none; }
ul.liste { padding-left:20px; } ul.liste li { margin:4px 0; }
.kasten { background:var(--kasten); border:1px solid var(--kastenrand); border-radius:12px; padding:12px 16px; margin:10px 0; }
footer { margin-top:28px; border-top:1px solid var(--rand); padding-top:12px; }
footer a { color:var(--text); }
@media (max-width:600px) { .sprache { padding:4px 14px 16px; } h1 { font-size:23px; }
  ol.schritte > li { padding-left:48px; gap:10px; } svg.skizze { width:96px; } .start { gap:16px; } }
@media print { nav.sprachen { display:none; } .sprache { display:block !important; break-after:page; } }"""


def installationsseite(geraet, adresse):
    """Eine Installationsdatei (statisches HTML, ohne JavaScript): Abschnitte de/en/es, Standard Englisch."""
    sys.path.insert(0, str(QUELLE / "Programm"))
    import qr_code
    from urllib.parse import quote, urlparse
    host = urlparse(adresse).netloc
    a = html_esc(adresse)
    logo = (QUELLE / "Programm" / "assets" / "me-goosta-symbol.svg").read_text(encoding="utf-8")
    logo = re.sub(r"<title>.*?</title>\s*", "", logo, flags=re.S).replace('role="img" aria-label="Me Goos-ta Deutsch"',
                                                                         'aria-hidden="true"', 1).strip()
    abschnitte = []
    for l in ("de", "es", "en"):                 # Englisch zuletzt: ohne #de/#es sichtbar (CSS :target, kein Skript)
        t, g = IT[l], IG[geraet][l]
        fuell = lambda s: s.replace("{adresse}", a).replace("{host}", html_esc(host))   # noqa: E731
        schritte = "".join(
            f'<li><div><h3>{s[0]}</h3><p>{fuell(s[1])}</p></div>{skizze(s[2], s[3:], titel=re.sub("<[^>]+>", "", s[0]))}</li>'
            for s in g["schritte"])
        andere = " · ".join(f'<a href="{quote(INSTALL_DATEIEN[x])}#{l}">{html_esc(IG[x][l]["name"])}</a>' for x in INSTALL_DATEIEN if x != geraet)
        abschnitte.append(f"""<section class="sprache" id="{l}" lang="{l}">
<h1>{g["h1"]}</h1>
<p class="lead">{t["lead"]}</p>
<div class="start"><div class="links"><p><a class="gross" href="{a}">📲 {t["knopf"]}</a></p>
<p class="pfad">{a}</p></div>
<div class="qr-box">{qr_code.qr_svg(adresse, titel=t["qr_aria"])}<p class="klein">{t["qr_text"]}</p></div></div>
<h2>{t["weg_titel"]}</h2>
<ul class="liste">{"".join(f"<li>{fuell(x)}</li>" for x in t["weg"])}</ul>
<h2>{t["schritte_titel"]}</h2>
<ol class="schritte">{schritte}</ol>
{f'<div class="kasten">{g["hinweis"]}</div>' if g.get("hinweis") else ""}
<h2>{t["brauchst_titel"]}</h2>
<ul class="liste"><li>{g["brauchst"]}</li><li>{t["platz"]}</li><li>{t["netz"]}</li></ul>
<h2>{t["kann_titel"]}</h2>
<p>{t["kann"]}</p>
<h2>{t["daten_titel"]}</h2>
<p>{fuell(t["daten"])}</p>
<h2>{t["sicherung_titel"]}</h2>
<ul class="liste">{"".join(f"<li>{x}</li>" for x in t["sicherung"])}</ul>
<h2>{t["update_titel"]}</h2>
<p>{t["update"]}</p>
<p>{g["entfernen"]}</p>
<footer class="klein"><p>{t["auch"]}: {andere} · {t["rechner"]}: <a href="{quote("LIES MICH ZUERST.html")}#{l}">LIES MICH ZUERST.html</a></p><p>{t["fuss"]}</p></footer>
</section>""")
    titel = f"Me Goos-ta Deutsch – {IG[geraet]['en']['name']}"
    nav = " ".join(f'<a href="#{l}" hreflang="{l}" lang="{l}">{IT[l]["sprache"]}</a>' for l in ("de", "en", "es"))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{html_esc(titel)}</title>
<style>
{INSTALL_CSS}
</style>
</head>
<body>
<header>{logo}
<div class="name">Me Goos-ta Deutsch · {html_esc(IG[geraet]["en"]["name"])}</div>
<nav class="sprachen" aria-label="Sprache / Language / Idioma">{nav}</nav>
</header>
<main>
{chr(10).join(abschnitte)}
</main>
</body>
</html>
"""


def installationsdateien(quelle):
    """Schreibt die drei Installationsdateien neben die Startdateien (Adresse aus Programm/web_adresse.txt)."""
    pfad = quelle / "Programm" / "web_adresse.txt"
    adresse = pfad.read_text(encoding="utf-8").strip().splitlines()[0].strip() if pfad.is_file() else ""
    if not adresse.startswith("https://"):
        sys.exit(f"Keine Adresse in {pfad} – erst veröffentlichen, dann die Installationsdateien bauen.")
    for geraet, name in INSTALL_DATEIEN.items():
        (quelle / name).write_bytes(installationsseite(geraet, adresse).encode("utf-8"))
    return adresse


# ---------- Download-Seite …/download/ (seit 2.1): ein Paket für Windows, macOS und Linux als GitHub-Release ----------
# Liegt im selben Pages-Projekt wie die Handy-App, aber nicht in deren Offline-Liste (sw.js lässt download/ durch).
# Ohne JavaScript: Englisch, alle drei Systeme sichtbar (#de/#es per CSS :target). Mit seite.js: System erkannt, Sprache
# EN · DE · ES (gemerkt in localStorage, Anker #de/#es/#en zuerst), kein Netzverkehr, kein Tracking.
ZIP_NAME = re.compile(r"^Me-Goos-ta-Deutsch-(\d+(?:\.\d+)+)\.zip$")
SYSTEME = (("win", "Windows"), ("mac", "macOS"), ("linux", "Linux"))
LINUX_BEFEHL = 'sh "Me Goos-ta Deutsch - Linux.sh"'


def github_ort(adresse):
    """(Konto, Repository) aus der Pages-Adresse https://<konto>.github.io/<repo>/."""
    m = re.match(r"^https://([a-z0-9-]+)\.github\.io/([A-Za-z0-9._-]+)/$", adresse)
    if not m:
        sys.exit(f"{adresse!r} ist keine GitHub-Pages-Projektadresse (https://<konto>.github.io/<repo>/).")
    return m.group(1), m.group(2)


def release_info(zip_pfad, version):
    """Name, Größe und SHA-256 der Release-ZIP; der Name muss zur Programmversion passen."""
    p = Path(zip_pfad)
    m = ZIP_NAME.match(p.name)
    if not p.is_file() or not m:
        sys.exit(f"Release-ZIP {p} fehlt oder heißt nicht Me-Goos-ta-Deutsch-<Version>.zip.")
    if m.group(1) != version:
        sys.exit(f"Release-ZIP {p.name} passt nicht zur Programmversion {version}.")
    daten = p.read_bytes()
    info = dict(name=p.name, groesse=len(daten), sha256=sha(daten), signiert=False)
    summen, minisig = p.parent / "SHA256SUMS.txt", p.parent / "SHA256SUMS.txt.minisig"     # seit 2.5 neben der ZIP
    if minisig.is_file() and summen.is_file() and f"{info['sha256']}  {p.name}" in summen.read_text(encoding="utf-8"):
        info["signiert"] = True                                  # geprüft hat veroeffentliche_release.py
    return info


def download_adressen(adresse, version, zip_info):
    konto, repo = github_ort(adresse)
    basis = f"https://github.com/{konto}/{repo}"
    if zip_info:
        tag = f"{basis}/releases/download/v{version}/"
        return dict(repo=basis, zip=tag + zip_info["name"], notizen=f"{basis}/releases/tag/v{version}",
                    summen=tag + "SHA256SUMS.txt", signatur=tag + "SHA256SUMS.txt.minisig", seite=adresse + "download/")
    return dict(repo=basis, zip=f"{basis}/releases/latest", notizen=f"{basis}/releases", summen="", seite=adresse + "download/")


DT = {   # Texte der Download-Seite (dürfen <b>/<code> enthalten); gleiche Schlüssel und Längen in de/en/es
    "de": dict(
        titel="Me Goos-ta Deutsch – Download",
        beschreibung="Deutsch lernen mit Gänse-Wortwitz: Bild-Lernkarten zum Drucken und Lernen, für Windows, macOS und "
                     "Linux. Kostenlos, offline, Open Source.",
        springen="Zum Inhalt springen", oben="Kostenlos · Open Source · Läuft offline",
        h1="Deutsch lernen mit Gänse-Wortwitz",
        lead="Me Goos-ta Deutsch macht aus deinen Gänse-Wortspiel-Bildern Lernkarten – zum Ausdrucken oder zum Lernen am "
             "Bildschirm, mit Wiederholung nach FSRS und Rückseiten in 15 Sprachen. Alles läuft auf deinem eigenen Rechner.",
        knopf="Download für {os}", meta="Version {version} · {groesse} · kostenlos (MIT)",
        meta_ohne="Version {version} · kostenlos (MIT)",
        paket="Ein Paket für Windows, macOS und Linux – eine ZIP-Datei, kein Installer, kein Konto.",
        auch="Auch für", handy="Am Handy? Spar dir den Download – die Handy-App läuft direkt im Browser.",
        handy_knopf="Handy-App öffnen", karte_aria="Beispielkarte: vorne das Bild „Gans alt“, hinten „viejo“",
        karte_unter="„Gans alt“ klingt wie „ganz alt“ – hinten steht „viejo“.",
        schritte_titel="Gans einfach: in drei Schritten startklar",
        schritte_lead="Laden, entpacken, doppelklicken – den Rest erledigt die Gans.", os_wahl="Schritte für",
        win=[("ZIP-Datei freigeben", "Rechtsklick auf die heruntergeladene ZIP-Datei → <b>Eigenschaften</b> → unten "
              "<b>Zulassen</b> anhaken → <b>OK</b>. So lässt die Intelligente App-Steuerung (Smart App Control) die "
              "Startdatei durch. Kein Kästchen da? Dann einfach weiter.", "freigeben", "Zulassen"),
             ("Entpacken", "Rechtsklick auf die ZIP-Datei → <b>Alle extrahieren …</b> → <b>Extrahieren</b>, zum Beispiel "
              "nach „Dokumente“. Der Ordner wird deine Gänse-Werkstatt für Bilder und PDFs.", "entpacken", "Alle extrahieren"),
             ("Doppelklick und los", "Doppelklick auf <b>Me Goos-ta Deutsch - Windows</b>. Der erste Start richtet alles "
              "selbst ein (3–10 Minuten, ca. 90 MB, ohne Administratorrechte), dann öffnet sich das Programm im Browser. "
              "Ab dann startet es in Sekunden über das Desktop-Symbol.", "doppelklick", "… - Windows")],
        win_hilfe=("Windows ist besonders vorsichtig?", "<b>„Der Computer wurde durch Windows geschützt“</b> → <b>Weitere "
                   "Informationen</b> → <b>Trotzdem ausführen</b>.<br><b>„Intelligente App-Steuerung … blockiert“</b> → "
                   "Schritt 1 wurde ausgelassen: Rechtsklick auf <b>Me Goos-ta Deutsch - Windows</b> → Eigenschaften → "
                   "<b>Zulassen</b> → OK, dann erneut doppelklicken."),
        mac=[("Entpacken", "Doppelklick auf die ZIP-Datei – Safari entpackt sie oft schon selbst. Den Ordner dann nach "
              "„Dokumente“ ziehen.", "entpacken", "Doppelklick"),
             ("Starten", "Doppelklick auf <b>Me Goos-ta Deutsch - Mac</b>. Kann macOS den Entwickler nicht überprüfen: ab "
              "<b>macOS 15</b> Systemeinstellungen → <b>Datenschutz &amp; Sicherheit</b> → <b>Dennoch öffnen</b>; bis "
              "macOS 14 Control-Klick auf die Datei → <b>Öffnen</b>.", "dennoch", "Dennoch öffnen"),
             ("Erster Start und danach", "Alles richtet sich selbst ein (Terminal-Fenster offen lassen, 3–10 Minuten, ca. "
              "90 MB), dann öffnet sich das Programm im Browser. Danach findest du <b>Me Goos-ta Deutsch</b> im Launchpad "
              "– gern ins Dock ziehen.", "dock", "")],
        mac_hilfe=("Gatekeeper sagt Nein?", "Apple winkt nur Apps von kostenpflichtigen Entwicklerkonten einfach durch. Me "
                   "Goos-ta Deutsch ist kostenlos und Open Source, darum fragt macOS einmal nach. <b>Klappt immer:</b> "
                   "Programm „Terminal“ öffnen, <code>sh</code> und ein Leerzeichen tippen, die Startdatei ins Fenster "
                   "ziehen, Eingabetaste. Fragt macOS nach Zugriff auf „Downloads“ oder „Dokumente“: <b>Erlauben</b>."),
        linux=[("Entpacken", "Die ZIP-Datei im Dateimanager entpacken (Rechtsklick → <b>Hier entpacken</b>) und den Ordner "
                "nach „Dokumente“ legen.", "entpacken", "Hier entpacken"),
               ("Starten", "Im Ordner ein Terminal öffnen (Rechtsklick → <b>Im Terminal öffnen</b>) und "
                "<code>{befehl}</code> eingeben – oder Rechtsklick auf die Datei → <b>Als Programm ausführen</b>.",
                "terminal", LINUX_BEFEHL),
               ("Erster Start und danach", "Alles richtet sich selbst ein (Terminal offen lassen, 3–10 Minuten, ca. 90 MB), "
                "dann öffnet sich das Programm im Browser. Danach steht es im Anwendungsmenü.", "menue", "")],
        linux_hilfe=("Gut zu wissen", "Läuft auf den üblichen Systemen (Ubuntu, Debian, Mint, Fedora, openSUSE, Arch …) mit "
                     "Intel/AMD- oder ARM-Prozessor. Gebraucht werden nur <code>curl</code> oder <code>wget</code> und "
                     "<code>tar</code> – die sind fast immer schon da."),
        drin_titel="Gans schön viel drin",
        drin=[("drucken", "Druckfertig", "PDFs für zu Hause (A4 oder Letter) und für die Druckerei mit Beschnitt – dazu ein "
               "Prüfbogen vor dem Drucken."),
              ("lernen", "Lernen mit FSRS", "Üben direkt im Programm mit Wiederholung nach FSRS-6 (wie Anki). Dein Lernstand "
               "bleibt."),
              ("sprachen", "15 Sprachen", "Hinten Spanisch – oder Englisch, Französisch, Japanisch, Arabisch und zehn weitere, "
               "jede ein kleiner Download nach Wunsch."),
              ("tools", "Tools nach Bedarf", "Bildverbesserung, Übersetzungsvorschläge und KI-Gänse offline – geladen nur, "
               "wenn du sie willst."),
              ("handy", "Handy-App", "Android, iPhone und Google Pixel: dasselbe Programm als App, die auch offline läuft."),
              ("schutz", "Deine Daten bleiben daheim", "Kein Konto, keine Werbung, kein Tracking. Karten und Bilder verlassen "
               "deinen Rechner nie.")],
        handy_titel="Auch aufs Handy",
        handy_text="Die Handy-App ist dasselbe Programm für Android, iPhone/iPad (ab iOS 16.4) und Google Pixel – direkt aus "
                   "dem Browser installiert, ohne App-Store, auch offline.",
        handy_qr="Mit der Handy-Kamera scannen", qr_aria="QR-Code mit der Adresse der Handy-App",
        faq_titel="Fragen? Antworten!",
        faq=[("Ist das sicher?", "Gans sicher. Me Goos-ta Deutsch ist Open Source unter der MIT-Lizenz – jede Zeile steht auf "
              "GitHub. Die ZIP-Datei enthält keinen Installer und keine versteckten Extras. Beim ersten Start lädt sie nur "
              "Python und Pakete aus den offiziellen Quellen (python.org, pypi.org, github.com) und prüft jede Datei per "
              "Prüfsumme. Die SHA-256 der ZIP-Datei kannst du mit dem Wert unten vergleichen."),
             ("Warum warnt mein Computer?", "Windows und macOS sind vorsichtig bei Programmen aus dem Internet, die kein "
              "kostenpflichtiges Entwicklerzertifikat tragen. Eine gute Gewohnheit – und hier kein Grund zur Sorge: einmal "
              "zulassen (Windows) bzw. „Dennoch öffnen“ (macOS), und die Gans watschelt los."),
             ("Was brauche ich?", "Windows 10 oder 11 (64 Bit, auch auf ARM), macOS auf Intel oder Apple Silicon oder ein "
              "übliches Linux auf Intel/AMD oder ARM. Etwa 700 MB freien Platz und einmal Internet für die Einrichtung "
              "(ca. 90 MB). Keine Administratorrechte, kein vorinstalliertes Python."),
             ("Wie mache ich ein Update?", "Ab Version 2.4 direkt im Programm: Werkzeuge → „Programm aktuell halten“ → "
              "„Nach neuer Version suchen“ (nur wenn du klickst, eine Anfrage an api.github.com, ohne Daten über dich oder "
              "deine Karten) → „Jetzt aktualisieren“ → „Jetzt neu starten“ – die neue Version kommt in denselben Ordner, "
              "Karten, Bilder, Einstellungen und Lernstand bleiben. Von älteren Versionen aus: neue ZIP-Datei laden, in "
              "einen neuen Ordner entpacken und die Startdatei doppelklicken – sie bietet an, alles zu übernehmen."),
             ("Wie deinstalliere ich?", "Im Programm erledigt der letzte Reiter <b>Deinstallieren</b> alles – und bietet "
              "vorher eine Sicherung deiner Karten an. Die Handy-App entfernst du wie jede andere App.")],
        lizenz="MIT-Lizenz", quelle="Quellcode auf GitHub", notizen="Versionshinweise", sha_titel="SHA-256 der ZIP-Datei",
        sha_ohne="Prüfsummen (SHA-256) gibt es zu jedem Release.", gruss="Viel Spaß beim Lernen – du machst das großartig!",
        echt_titel="Echtheit prüfen (für Vorsichtige)",
        echt_text="Die Datei {summen} ist mit dem Schlüssel von Me Goos-ta Deutsch signiert ({minisig}, Schlüssel-ID "
                  "<code>{id}</code>). Mit dem freien Werkzeug minisign prüfst du sie so: {befehl} – danach die SHA-256 der "
                  "ZIP-Datei mit dem Wert in SHA256SUMS.txt vergleichen (Windows: <code>certutil -hashfile {zip} SHA256</code>, "
                  "macOS/Linux: <code>shasum -a 256 {zip}</code>). Das Programm prüft die Signatur vor jedem Update von selbst "
                  "– Gans automatisch."),
    "en": dict(
        titel="Me Goos-ta Deutsch – Download",
        beschreibung="Learn German with goose puns: picture flash cards to print and to study, for Windows, macOS and Linux. "
                     "Free, offline, open source.",
        springen="Skip to content", oben="Free · Open source · Works offline",
        h1="Learn German with goose puns",
        lead="Me Goos-ta Deutsch turns your goose-pun pictures into flash cards – ready to print or to study on screen, with "
             "spaced repetition and back sides in 15 languages. Everything runs on your own computer.",
        knopf="Download for {os}", meta="Version {version} · {groesse} · free (MIT)", meta_ohne="Version {version} · free (MIT)",
        paket="One package for Windows, macOS and Linux – a ZIP file, no installer, no account.",
        auch="Also for", handy="On your phone? Skip the download – the phone app runs right in your browser.",
        handy_knopf="Open the phone app", karte_aria="Example card: the picture “Gans alt” on the front, “viejo” on the back",
        karte_unter="“Gans alt” sounds like “ganz alt” – very old. The back says “viejo”.",
        schritte_titel="Ready in three steps",
        schritte_lead="Download, extract, double-click – the goose does the rest.", os_wahl="Steps for",
        win=[("Unblock the ZIP", "Right-click the downloaded ZIP → <b>Properties</b> → tick <b>Unblock</b> at the bottom → "
              "<b>OK</b>. That way Smart App Control lets the start file through. No box there? Then just carry on.",
              "freigeben", "Unblock"),
             ("Extract", "Right-click the ZIP → <b>Extract All …</b> → <b>Extract</b>, for example into “Documents”. This "
              "folder becomes your goose workshop for pictures and PDFs.", "entpacken", "Extract All"),
             ("Double-click and go", "Double-click <b>Me Goos-ta Deutsch - Windows</b>. The first start sets everything up by "
              "itself (3–10 minutes, about 90 MB, no administrator rights), then the program opens in your browser. From "
              "then on the desktop icon starts it in seconds.", "doppelklick", "… - Windows")],
        win_hilfe=("Windows being extra careful?", "<b>“Windows protected your PC”</b> → <b>More info</b> → <b>Run anyway</b>."
                   "<br><b>“Smart App Control blocked …”</b> → step 1 was skipped: right-click <b>Me Goos-ta Deutsch - "
                   "Windows</b> → Properties → <b>Unblock</b> → OK, then double-click again."),
        mac=[("Extract", "Double-click the ZIP – Safari often extracts it for you. Then move the folder to “Documents”.",
              "entpacken", "Double-click"),
             ("Start", "Double-click <b>Me Goos-ta Deutsch - Mac</b>. If macOS can’t verify the developer: on <b>macOS 15 and "
              "later</b> go to System Settings → <b>Privacy &amp; Security</b> → <b>Open Anyway</b>; up to macOS 14 "
              "Control-click the file → <b>Open</b>.", "dennoch", "Open Anyway"),
             ("First start and beyond", "Everything sets itself up (keep the Terminal window open, 3–10 minutes, about "
              "90 MB), then the program opens in your browser. Afterwards you’ll find <b>Me Goos-ta Deutsch</b> in "
              "Launchpad – feel free to drag it into the Dock.", "dock", "")],
        mac_hilfe=("Gatekeeper says no?", "Apple only waves through apps from paid developer accounts. Me Goos-ta Deutsch is "
                   "free and open source, so macOS asks once. <b>Always works:</b> open the Terminal app, type "
                   "<code>sh</code> and a space, drag the start file into the window and press Return. If macOS asks for "
                   "access to “Downloads” or “Documents”: <b>Allow</b>."),
        linux=[("Extract", "Extract the ZIP in your file manager (right-click → <b>Extract Here</b>) and move the folder to "
                "“Documents”.", "entpacken", "Extract Here"),
               ("Start", "Open a terminal in the folder (right-click → <b>Open in Terminal</b>) and type "
                "<code>{befehl}</code> – or right-click the file → <b>Run as a Program</b>.", "terminal", LINUX_BEFEHL),
               ("First start and beyond", "Everything sets itself up (keep the terminal open, 3–10 minutes, about 90 MB), "
                "then the program opens in your browser. Afterwards it’s in your application menu.", "menue", "")],
        linux_hilfe=("Good to know", "Runs on the usual distributions (Ubuntu, Debian, Mint, Fedora, openSUSE, Arch …) with "
                     "Intel/AMD or ARM processors. All it needs is <code>curl</code> or <code>wget</code> and "
                     "<code>tar</code> – almost always there already."),
        drin_titel="Take a gander at what’s inside",
        drin=[("drucken", "Print-ready", "PDFs for home (A4 or Letter) and for print shops with bleed – plus a proof sheet "
               "before you press print."),
              ("lernen", "Learn with FSRS", "Study right in the program with spaced repetition (FSRS-6, like Anki). Your "
               "progress is kept."),
              ("sprachen", "15 languages", "Spanish on the back – or English, French, Japanese, Arabic and ten more, each a "
               "small optional download."),
              ("tools", "Tools on demand", "Image enhancement, translation suggestions and offline AI geese – downloaded only "
               "when you want them."),
              ("handy", "Phone app", "Android, iPhone and Google Pixel: the same program as an app that works offline."),
              ("schutz", "Your data stays home", "No account, no ads, no tracking. Your cards and pictures never leave your "
               "computer.")],
        handy_titel="On your phone too",
        handy_text="The phone app is the same program for Android, iPhone/iPad (iOS 16.4 or later) and Google Pixel – "
                   "installed straight from the browser, no app store, works offline.",
        handy_qr="Scan with your phone’s camera", qr_aria="QR code with the address of the phone app",
        faq_titel="Questions? Answers!",
        faq=[("Is it safe?", "Yes. Me Goos-ta Deutsch is open source under the MIT license – every line is on GitHub. The ZIP "
              "holds no installer and no hidden extras. On the first start it only fetches Python and packages from the "
              "official sources (python.org, pypi.org, github.com) and checks every file by checksum. You can compare the "
              "ZIP’s SHA-256 with the value below."),
             ("Why does my computer warn me?", "Windows and macOS are cautious with programs from the internet that don’t "
              "carry a paid developer certificate. A good habit – and no reason to worry here: unblock once (Windows) or "
              "choose “Open Anyway” (macOS), and the goose is on its way."),
             ("What do I need?", "Windows 10 or 11 (64-bit, also on ARM), macOS on Intel or Apple silicon, or a common Linux "
              "on Intel/AMD or ARM. About 700 MB of free space and internet once for the setup (about 90 MB). No "
              "administrator rights and no Python needed beforehand."),
             ("How do I update?", "From version 2.4 on, right inside the program: Tools → “Keep the program up to date” → "
              "“Check for a new version” (only when you click, one request to api.github.com, with no data about you or your "
              "cards) → “Update now” → “Restart now” – the new version goes into the same folder, and your cards, pictures, "
              "settings and learning progress stay. From older versions: download the new ZIP, extract it into a new folder "
              "and double-click the start file – it offers to take everything over."),
             ("How do I uninstall?", "In the program, the last tab <b>Uninstall</b> does it all – and offers to back up your "
              "cards first. The phone app goes like any other app.")],
        lizenz="MIT License", quelle="Source code on GitHub", notizen="Release notes", sha_titel="SHA-256 of the ZIP",
        sha_ohne="Checksums (SHA-256) come with every release.", gruss="Have fun learning – you’re doing great!",
        echt_titel="Check it’s genuine (for the careful)",
        echt_text="The file {summen} is signed with the Me Goos-ta Deutsch key ({minisig}, key ID <code>{id}</code>). With "
                  "the free tool minisign you check it like this: {befehl} – then compare the SHA-256 of the ZIP with the value "
                  "in SHA256SUMS.txt (Windows: <code>certutil -hashfile {zip} SHA256</code>, macOS/Linux: <code>shasum -a 256 "
                  "{zip}</code>). The program checks the signature by itself before every update – no extra step needed."),
    "es": dict(
        titel="Me Goos-ta Deutsch – Descargar",
        beschreibung="Aprende alemán con juegos de palabras de gansos: tarjetas con imágenes para imprimir y estudiar, para "
                     "Windows, macOS y Linux. Gratis, sin conexión, de código abierto.",
        springen="Saltar al contenido", oben="Gratis · Código abierto · Funciona sin conexión",
        h1="Aprende alemán con juegos de palabras de gansos",
        lead="Me Goos-ta Deutsch convierte tus imágenes con juegos de palabras de gansos en tarjetas: para imprimir o estudiar "
             "en pantalla, con repaso espaciado y reversos en 15 idiomas. Todo funciona en tu propia computadora.",
        knopf="Descargar para {os}", meta="Versión {version} · {groesse} · gratis (MIT)",
        meta_ohne="Versión {version} · gratis (MIT)",
        paket="Un solo paquete para Windows, macOS y Linux: un archivo ZIP, sin instalador y sin cuenta.",
        auch="También para", handy="¿Estás en el celular? No hace falta descargar nada: la app para celular funciona directo "
                                   "en el navegador.",
        handy_knopf="Abrir la app para celular", karte_aria="Carta de ejemplo: al frente la imagen «Gans alt», atrás «viejo»",
        karte_unter="«Gans alt» suena como «ganz alt»: muy viejo. Atrás dice «viejo».",
        schritte_titel="¿Con ganas de empezar? Listo en tres pasos",
        schritte_lead="Descarga, descomprime, doble clic: el ganso hace el resto.", os_wahl="Pasos para",
        win=[("Desbloquear el ZIP", "Clic derecho en el ZIP descargado → <b>Propiedades</b> → abajo marca <b>Desbloquear</b> "
              "→ <b>Aceptar</b>. Así el Control inteligente de aplicaciones (Smart App Control) deja pasar el archivo de "
              "inicio. ¿No aparece la casilla? Entonces sigue adelante.", "freigeben", "Desbloquear"),
             ("Descomprimir", "Clic derecho en el ZIP → <b>Extraer todo …</b> → <b>Extraer</b>, por ejemplo en "
              "«Documentos». Esa carpeta será tu taller de gansos para imágenes y PDF.", "entpacken", "Extraer todo"),
             ("Doble clic y listo", "Doble clic en <b>Me Goos-ta Deutsch - Windows</b>. El primer inicio instala todo solo "
              "(3–10 minutos, unos 90 MB, sin permisos de administrador) y luego el programa se abre en el navegador. Desde "
              "entonces arranca en segundos con el icono del escritorio.", "doppelklick", "… - Windows")],
        win_hilfe=("¿Windows se pone muy precavido?", "<b>«Windows protegió su PC»</b> → <b>Más información</b> → "
                   "<b>Ejecutar de todas formas</b>.<br><b>«Control inteligente de aplicaciones … bloqueó»</b> → se omitió "
                   "el paso 1: clic derecho en <b>Me Goos-ta Deutsch - Windows</b> → Propiedades → <b>Desbloquear</b> → "
                   "Aceptar, y vuelve a hacer doble clic."),
        mac=[("Descomprimir", "Doble clic en el ZIP; Safari a menudo lo descomprime solo. Luego mueve la carpeta a "
              "«Documentos».", "entpacken", "Doble clic"),
             ("Iniciar", "Doble clic en <b>Me Goos-ta Deutsch - Mac</b>. Si macOS no puede verificar al desarrollador: desde "
              "<b>macOS 15</b> ve a Configuración del Sistema → <b>Privacidad y seguridad</b> → <b>Abrir igualmente</b>; "
              "hasta macOS 14, Control-clic en el archivo → <b>Abrir</b>.", "dennoch", "Abrir igualmente"),
             ("Primer inicio y después", "Todo se instala solo (deja abierta la ventana de Terminal, 3–10 minutos, unos "
              "90 MB) y luego el programa se abre en el navegador. Después encontrarás <b>Me Goos-ta Deutsch</b> en "
              "Launchpad; puedes arrastrarlo al Dock.", "dock", "")],
        mac_hilfe=("¿Gatekeeper dice que no?", "Apple solo deja pasar sin preguntar las apps de cuentas de desarrollador de "
                   "pago. Me Goos-ta Deutsch es gratis y de código abierto, por eso macOS pregunta una vez. <b>Siempre "
                   "funciona:</b> abre la app «Terminal», escribe <code>sh</code> y un espacio, arrastra el archivo de inicio "
                   "a la ventana y pulsa Intro. Si macOS pide acceso a «Descargas» o «Documentos»: <b>Permitir</b>."),
        linux=[("Descomprimir", "Descomprime el ZIP en el administrador de archivos (clic derecho → <b>Extraer aquí</b>) y "
                "mueve la carpeta a «Documentos».", "entpacken", "Extraer aquí"),
               ("Iniciar", "Abre una terminal en la carpeta (clic derecho → <b>Abrir en una terminal</b>) y escribe "
                "<code>{befehl}</code>, o clic derecho en el archivo → <b>Ejecutar como un programa</b>.", "terminal",
                LINUX_BEFEHL),
               ("Primer inicio y después", "Todo se instala solo (deja la terminal abierta, 3–10 minutos, unos 90 MB) y "
                "luego el programa se abre en el navegador. Después está en tu menú de aplicaciones.", "menue", "")],
        linux_hilfe=("Bueno saberlo", "Funciona en las distribuciones habituales (Ubuntu, Debian, Mint, Fedora, openSUSE, "
                     "Arch …) con procesador Intel/AMD o ARM. Solo necesita <code>curl</code> o <code>wget</code> y "
                     "<code>tar</code>, que casi siempre ya están."),
        drin_titel="Lo que trae este ganso",
        drin=[("drucken", "Listo para imprimir", "PDF para casa (A4 o carta) y para imprenta con sangrado, más una hoja de "
               "revisión antes de imprimir."),
              ("lernen", "Aprender con FSRS", "Estudia en el programa con repaso espaciado FSRS-6 (como Anki). Tu avance se "
               "guarda."),
              ("sprachen", "15 idiomas", "Español en el reverso, o inglés, francés, japonés, árabe y diez más; cada uno es "
               "una pequeña descarga opcional."),
              ("tools", "Herramientas a tu medida", "Mejora de imagen, sugerencias de traducción y gansos con IA sin "
               "conexión: se descargan solo si los quieres."),
              ("handy", "App para el celular", "Android, iPhone y Google Pixel: el mismo programa como app que funciona sin "
               "conexión."),
              ("schutz", "Tus datos se quedan en casa", "Sin cuenta, sin anuncios, sin rastreo. Tus cartas e imágenes nunca "
               "salen de tu computadora.")],
        handy_titel="También en el celular",
        handy_text="La app para celular es el mismo programa para Android, iPhone/iPad (desde iOS 16.4) y Google Pixel: se "
                   "instala desde el navegador, sin tienda de apps, y funciona sin conexión.",
        handy_qr="Escanéalo con la cámara del celular", qr_aria="Código QR con la dirección de la app para celular",
        faq_titel="¿Preguntas? ¡Respuestas!",
        faq=[("¿Es seguro?", "Sí. Me Goos-ta Deutsch es de código abierto con licencia MIT: cada línea está en GitHub. El ZIP "
              "no trae instalador ni extras ocultos. En el primer inicio solo descarga Python y paquetes de las fuentes "
              "oficiales (python.org, pypi.org, github.com) y revisa cada archivo con su suma de verificación. Puedes "
              "comparar el SHA-256 del ZIP con el valor de abajo."),
             ("¿Por qué mi computadora muestra un aviso?", "Windows y macOS son precavidos con programas de internet que "
              "no traen un certificado de desarrollador de pago. Es una buena costumbre, y aquí no hay de qué preocuparse: "
              "desbloquéalo una vez (Windows) o elige «Abrir igualmente» (macOS) y el ganso echa a andar."),
             ("¿Qué necesito?", "Windows 10 u 11 (64 bits, también en ARM), macOS en Intel o Apple silicon, o un Linux común "
              "en Intel/AMD o ARM. Unos 700 MB libres e internet una vez para la instalación (unos 90 MB). Sin permisos de "
              "administrador y sin Python instalado antes."),
             ("¿Cómo actualizo?", "Desde la versión 2.4, dentro del programa: Herramientas → «Mantener el programa al día» "
              "→ «Buscar una versión nueva» (solo al hacer clic, una consulta a api.github.com, sin datos sobre ti ni tus "
              "cartas) → «Actualizar ahora» → «Reiniciar ahora»: la versión nueva va a la misma carpeta y tus cartas, "
              "imágenes, ajustes y avance se quedan. Desde versiones anteriores: descarga el ZIP nuevo, descomprímelo en una "
              "carpeta nueva y haz doble clic en el archivo de inicio; ofrece pasarlo todo."),
             ("¿Cómo desinstalo?", "En el programa, la última pestaña <b>Desinstalar</b> lo hace todo y antes te ofrece "
              "respaldar tus cartas. La app para celular se quita como cualquier otra app.")],
        lizenz="Licencia MIT", quelle="Código fuente en GitHub", notizen="Notas de la versión", sha_titel="SHA-256 del ZIP",
        sha_ohne="Cada versión trae sus sumas de verificación (SHA-256).",
        gruss="¡Que te diviertas aprendiendo, lo estás haciendo muy bien!",
        echt_titel="Comprobar que es auténtico (para los precavidos)",
        echt_text="El archivo {summen} está firmado con la clave de Me Goos-ta Deutsch ({minisig}, ID de clave "
                  "<code>{id}</code>). Con la herramienta gratuita minisign lo compruebas así: {befehl}; después compara el "
                  "SHA-256 del ZIP con el valor de SHA256SUMS.txt (Windows: <code>certutil -hashfile {zip} SHA256</code>, "
                  "macOS/Linux: <code>shasum -a 256 {zip}</code>). El programa revisa la firma solo, antes de cada "
                  "actualización."),
}

# kleine Linien-Symbole (24 × 24) für „Was drin ist“
DRIN_SYMBOLE = {
    "drucken": '<path d="M7 9V3h10v6"/><rect x="3" y="9" width="18" height="8" rx="2"/><path d="M7 14h10v7H7z"/>',
    "lernen": '<rect x="3" y="6" width="14" height="14" rx="2"/><path d="M7 3h12a2 2 0 0 1 2 2v12"/><path d="M6.5 13l3 3 5-6"/>',
    "sprachen": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3.2 3.6 3.2 14.4 0 18M12 3c-3.2 3.6-3.2 14.4 0 18"/>',
    "tools": '<path d="M14.5 6.5a4 4 0 0 0 5 5l-9 9a2.1 2.1 0 0 1-3-3l9-9a4 4 0 0 1-2-2z"/><path d="M15 3.5l2.5 2.5"/>',
    "handy": '<rect x="7" y="2" width="10" height="20" rx="2.5"/><path d="M11 18.5h2"/>',
    "schutz": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/><path d="M12 15v2"/>',
}
PFEIL = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M5 20h14" fill="none" stroke="currentColor" '
         'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')

# Skizzen am Rechner: Fenster als Strichzeichnung (Stil wie skizze(): Schriftfarbe, das Wichtige in Akzentfarbe)
_FENSTER = ('<rect x="3" y="3" width="194" height="124" rx="10"/><path class="d" d="M3 19h194"/>'
            '<circle class="f" cx="14" cy="11" r="2.2"/><circle class="f" cx="22" cy="11" r="2.2"/><circle class="f" cx="30" cy="11" r="2.2"/>')


def _pc_text(text, x, y, mitte=False, klasse="hl", groesse=None):
    g = groesse or (11 if len(text) <= 13 else 10 if len(text) <= 18 else 8)
    a = ' text-anchor="middle"' if mitte else ""
    return f'<text class="{klasse}" x="{x}" y="{y}" font-size="{g}"{a}>{html_esc(text)}</text>'


def pc_skizze(art, b="", titel=""):
    if art == "freigeben":       # Eigenschaften: Häkchen „Zulassen“, dann OK
        innen = ('<path class="d" d="M18 34h64M18 46h120M18 58h96"/>'
                 '<rect class="hl" x="14" y="70" width="112" height="24" rx="12"/>'
                 '<rect class="f" x="24" y="77" width="10" height="10" rx="2"/><path class="wl" d="M26.3 82l2.2 2.2 3.6-4.4"/>'
                 + _pc_text(b, 40, 85.5) +
                 '<rect class="d" x="98" y="104" width="40" height="15" rx="4"/><rect x="144" y="104" width="40" height="15" rx="4"/>'
                 '<text x="164" y="114.6" font-size="8" text-anchor="middle">OK</text>')
    elif art == "entpacken":     # ZIP → Ordner
        innen = ('<path d="M36 30h28l12 12v50H36z"/><path class="d" d="M64 30v12h12"/>'
                 '<path class="d" d="M50 34v4M54 40v4M50 46v4M54 52v4"/><rect class="d" x="47" y="58" width="10" height="10" rx="2"/>'
                 '<path class="hl" d="M88 62h26M106 54l8 8-8 8"/>'
                 '<path d="M126 40h20l6 7h28v45h-54z"/><path class="d" d="M126 54h54"/>' + _pc_text(b, 100, 114, mitte=True))
    elif art == "doppelklick":   # Startdatei mit der Gans, Doppelklick
        innen = ('<path d="M76 26h30l12 12v52H76z"/><path class="d" d="M106 26v12h12"/>' + _gans(86, 50)
                 + '<path class="hl" d="M124 76l-5-5M130 72v-7M136 76l5-5"/>'
                 '<path class="f" d="M127 81v19l5-5 4 8.5 3.6-1.8-4-8.4h7z"/>' + _pc_text(b, 100, 116, mitte=True))
    elif art == "dennoch":       # macOS: Datenschutz & Sicherheit → „Dennoch öffnen“
        innen = ('<rect class="d" x="12" y="27" width="46" height="92" rx="5"/><path class="d" d="M20 40h30M20 52h24M20 64h28M20 76h20"/>'
                 '<path class="d" d="M70 34h80M70 46h110"/><rect x="68" y="58" width="118" height="54" rx="6"/>'
                 '<path class="d" d="M78 70h76"/><rect class="hl" x="80" y="83" width="100" height="20" rx="10"/>'
                 + _pc_text(b, 130, 96.3, mitte=True, groesse=9))
    elif art == "dock":          # macOS: Gans im Dock
        innen = ('<rect class="d" x="18" y="28" width="98" height="54" rx="5"/><path class="d" d="M26 40h62M26 52h78M26 64h50"/>'
                 '<rect x="34" y="94" width="132" height="26" rx="9"/>'
                 + "".join(f'<rect class="d" x="{x}" y="98" width="18" height="18" rx="5"/>' for x in (42, 66, 90, 144))
                 + _gans(113, 96))
    elif art == "terminal":      # Linux: Befehl im Terminal
        innen = ('<text class="t mono" x="12" y="40" font-size="8">$</text>'
                 + _pc_text(b, 21, 40, klasse="hl mono", groesse=7)
                 + '<path class="d" d="M12 54h96M12 66h130M12 78h80"/><rect class="hl" x="12" y="90" width="6" height="11"/>')
    elif art == "menue":         # Linux: Anwendungsmenü mit der Gans
        teile = ['<rect class="d" x="40" y="27" width="120" height="14" rx="7"/>']
        for r in range(3):
            for c in range(5):
                if (r, c) != (1, 2):
                    teile.append(f'<rect class="d" x="{48 + c * 24}" y="{50 + r * 25}" width="18" height="18" rx="5"/>')
        innen = "".join(teile) + _gans(94, 73)
    else:
        raise ValueError(art)
    return f'<svg class="skizze pc" viewBox="0 0 200 130" role="img" aria-label="{html_esc(titel)}">{_FENSTER}{innen}</svg>'


DOWNLOAD_CSS = """@font-face { font-family:"Poppins"; src:url("../schrift/Poppins-Regular.ttf") format("truetype"); font-weight:400; font-display:swap; }
@font-face { font-family:"Poppins"; src:url("../schrift/Poppins-Medium.ttf") format("truetype"); font-weight:500 600; font-display:swap; }
@font-face { font-family:"Poppins"; src:url("../schrift/Poppins-Bold.ttf") format("truetype"); font-weight:700; font-display:swap; }
:root { --grund:#F4F8FC; --flaeche:#E8F2FA; --karte:#FFFFFF; --text:#1B2D4F; --leise:#45607F; --rand:#C9DCEB; --akzent:#D7263D;
  --akzent-2:#B51E31; --auf-akzent:#FFFFFF; --schnabel:#F6A94B; --kasten:#FFF6E5; --kastenrand:#F6A94B; --fokus:#1F6FEB;
  --schatten:27,45,79; --qr-grund:#FFFFFF; --qr-text:#1B2D4F; color-scheme:light; }
@media (prefers-color-scheme: dark) {
  :root { --grund:#0B1626; --flaeche:#11203A; --karte:#16243A; --text:#E6EEF8; --leise:#A9BCD6; --rand:#2C4262; --akzent:#FF5C70;
    --akzent-2:#FF8293; --auf-akzent:#0F1B2E; --kasten:#2B2416; --kastenrand:#B98234; --fokus:#7AB8FF; --schatten:0,0,0;
    color-scheme:dark; } }
* { box-sizing:border-box; }
[hidden] { display:none !important; }
html { scroll-behavior:smooth; -webkit-text-size-adjust:100%; }
body { margin:0; background:var(--grund); color:var(--text); font:16px/1.6 "Poppins",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  overflow-wrap:break-word; }
a { color:inherit; text-underline-offset:3px; }
:focus-visible { outline:3px solid var(--fokus); outline-offset:3px; border-radius:8px; }
code, .pfad { font-family:ui-monospace,Consolas,Menlo,monospace; font-size:.88em; overflow-wrap:anywhere; }
code { background:var(--flaeche); border:1px solid var(--rand); border-radius:6px; padding:1px 5px; }
.breit { max-width:1120px; margin:0 auto; padding:0 20px; }
.sprache { display:none; }
.sprache:target, #en { display:block; }
.sprache:target ~ #en { display:none; }
html[data-sprache] .sprache { display:none !important; }
html[data-sprache=de] #de, html[data-sprache=en] #en, html[data-sprache=es] #es { display:block !important; }
html[data-os=win] [data-os-teil]:not([data-os-teil=win]), html[data-os=mac] [data-os-teil]:not([data-os-teil=mac]),
html[data-os=linux] [data-os-teil]:not([data-os-teil=linux]),
html[data-os=win] .auch [data-os-wahl=win], html[data-os=mac] .auch [data-os-wahl=mac], html[data-os=linux] .auch [data-os-wahl=linux],
html.js:not([data-os]) .auch, html[data-os] .os-block > h3 { display:none; }
.springen { position:absolute; left:12px; top:-80px; z-index:5; background:var(--karte); color:var(--text); padding:10px 16px;
  border-radius:10px; border:1px solid var(--rand); }
.springen:focus { top:12px; }
.kopf { max-width:1120px; margin:0 auto; padding:14px 20px; display:flex; align-items:center; gap:12px; }
.kopf .marke { display:flex; align-items:center; gap:10px; font-weight:700; font-size:18px; text-decoration:none; flex:1; min-width:0; }
.kopf .marke img { width:40px; height:40px; flex:none; }
nav.sprachen { display:flex; gap:2px; background:var(--karte); border:1px solid var(--rand); border-radius:999px; padding:3px; flex:none; }
nav.sprachen a { text-decoration:none; font-weight:600; font-size:14px; min-width:44px; min-height:38px; padding:0 10px;
  border-radius:999px; display:grid; place-items:center; }
nav.sprachen a:hover { background:var(--flaeche); }
nav.sprachen a[aria-current=true] { background:var(--text); color:var(--karte); }
.hero { background:linear-gradient(180deg, var(--flaeche), var(--grund)); }
.hero .breit { display:grid; grid-template-columns:minmax(0, 1.2fr) minmax(0, .8fr); gap:40px; align-items:center; padding-top:24px; padding-bottom:64px; }
.oben { display:inline-block; font-size:14px; font-weight:500; color:var(--leise); background:var(--karte); border:1px solid var(--rand);
  border-radius:999px; padding:4px 14px; margin:0 0 16px; }
h1 { font-size:clamp(34px, 5.2vw, 56px); line-height:1.08; letter-spacing:-.015em; margin:0 0 18px; }
h2 { font-size:clamp(25px, 3.4vw, 36px); line-height:1.2; letter-spacing:-.01em; margin:0 0 8px; }
h3 { font-size:19px; line-height:1.3; margin:0 0 6px; }
h4 { font-size:17px; line-height:1.35; margin:0; }
.lead { font-size:clamp(17px, 2vw, 19px); color:var(--leise); margin:0 0 28px; max-width:36em; }
.laden { display:flex; flex-wrap:wrap; gap:12px; }
a.gross { display:inline-flex; align-items:center; gap:12px; background:var(--akzent); color:var(--auf-akzent); text-decoration:none;
  font-weight:700; font-size:18px; line-height:1.25; padding:15px 26px; border-radius:14px; min-height:56px;
  box-shadow:0 8px 22px rgba(var(--schatten), .18); transition:background .15s, transform .15s; }
a.gross:hover { background:var(--akzent-2); transform:translateY(-1px); }
a.gross svg { width:22px; height:22px; flex:none; }
a.gross.leicht { font-size:16px; min-height:48px; padding:11px 20px; box-shadow:none; }
.meta { color:var(--text); font-weight:500; font-size:15px; margin:14px 0 2px; }
.paket { color:var(--leise); font-size:14px; margin:0; }
.auch { display:flex; flex-wrap:wrap; gap:8px; align-items:center; color:var(--leise); font-size:14px; margin:16px 0 0; }
button.chip { font:inherit; font-size:14px; font-weight:600; color:var(--text); background:var(--karte); border:1px solid var(--rand);
  border-radius:999px; padding:6px 16px; min-height:40px; cursor:pointer; }
button.chip:hover { border-color:var(--text); }
button.chip[aria-pressed=true] { background:var(--text); color:var(--karte); border-color:var(--text); }
.handy-hinweis { display:flex; flex-wrap:wrap; gap:10px 14px; align-items:center; background:var(--kasten); border:1px solid var(--kastenrand);
  border-radius:14px; padding:12px 16px; margin:0 0 20px; }
a.knopf2 { display:inline-flex; align-items:center; min-height:44px; padding:8px 18px; border-radius:12px; border:2px solid var(--text);
  text-decoration:none; font-weight:600; }
figure.bild { margin:0; position:relative; height:360px; }
.bsp { position:absolute; width:206px; height:280px; border-radius:18px; background:var(--karte); border:1px solid var(--rand);
  box-shadow:0 18px 40px rgba(var(--schatten), .16); display:flex; flex-direction:column; align-items:center; justify-content:center; gap:14px; }
.bsp.vorne { left:2%; top:34px; transform:rotate(-6deg); z-index:1; }
.bsp.vorne img { width:132px; height:132px; }
.bsp.vorne span { font-weight:700; font-size:22px; }
.bsp.hinten { right:2%; top:0; transform:rotate(5deg); background:#FDF3E1; color:#1B2D4F; }
.bsp.hinten .wort { font-weight:700; font-size:34px; }
.bsp.hinten .kuerzel { position:absolute; left:14px; top:12px; font-size:12px; font-weight:700; background:#FFFFFF; border-radius:999px; padding:1px 9px; }
.bsp.hinten svg { position:absolute; right:12px; bottom:12px; width:64px; height:48px; }
figure.bild figcaption { position:absolute; left:0; right:0; bottom:0; text-align:center; font-size:14px; color:var(--leise); }
.abschnitt { padding:64px 0; }
.abschnitt.hell { background:var(--karte); border-top:1px solid var(--rand); border-bottom:1px solid var(--rand); }
.unter { color:var(--leise); font-size:17px; margin:0 0 24px; max-width:40em; }
.os-wahl { display:flex; flex-wrap:wrap; gap:8px; margin:0 0 22px; }
.os-block { margin:0 0 36px; }
.os-block:last-child { margin-bottom:0; }
ol.schritte { list-style:none; counter-reset:s; margin:12px 0 18px; padding:0; display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:18px; }
ol.schritte > li { counter-increment:s; background:var(--grund); border:1px solid var(--rand); border-radius:18px; padding:20px;
  display:flex; flex-direction:column; gap:12px; }
ol.schritte h4 { display:flex; align-items:center; gap:10px; }
ol.schritte h4::before { content:counter(s); flex:none; width:32px; height:32px; border-radius:50%; background:var(--akzent);
  color:var(--auf-akzent); display:grid; place-items:center; font-size:16px; }
ol.schritte p { margin:0; color:var(--leise); }
ol.schritte b { color:var(--text); }
svg.skizze { display:block; width:100%; max-width:230px; height:auto; margin:0 auto 4px; color:var(--text); }
svg.skizze * { fill:none; stroke:currentColor; stroke-width:2; stroke-linecap:round; stroke-linejoin:round; }
svg.skizze .d { stroke-width:1.4; opacity:.55; }
svg.skizze .hl { stroke:var(--akzent); stroke-width:2.6; }
svg.skizze .f { fill:currentColor; stroke:none; }
svg.skizze .f.s { fill:var(--schnabel); }
svg.skizze .wl { stroke:var(--karte); stroke-width:1.8; }
svg.skizze text { stroke:none; fill:currentColor; font-family:"Poppins",system-ui,-apple-system,"Segoe UI",sans-serif; font-weight:600; }
svg.skizze text.hl { fill:var(--akzent); stroke:none; }
svg.skizze text.mono { font-family:ui-monospace,Consolas,Menlo,monospace; font-weight:600; }
.kasten { background:var(--kasten); border:1px solid var(--kastenrand); border-radius:14px; padding:14px 18px; }
.kasten h4 { margin-bottom:4px; }
.kasten p { margin:0; }
.drin { display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:18px; margin-top:26px; }
.drin article { background:var(--karte); border:1px solid var(--rand); border-radius:18px; padding:22px; }
.drin .symbol { width:46px; height:46px; border-radius:12px; background:var(--flaeche); color:var(--akzent); display:grid; place-items:center; margin-bottom:14px; }
.drin .symbol svg { width:24px; height:24px; fill:none; stroke:currentColor; stroke-width:2; stroke-linecap:round; stroke-linejoin:round; }
.drin p { margin:0; color:var(--leise); }
.handy { display:grid; grid-template-columns:minmax(0, 1fr) auto; gap:36px; align-items:center; }
.handy p { max-width:36em; }
.qr-box { background:var(--qr-grund); border:1px solid var(--rand); border-radius:18px; padding:14px; text-align:center; width:224px; }
.qr-box svg { width:194px; height:194px; display:block; margin:0 auto; }
.qr-box p { margin:6px 0 0; font-size:13px; color:var(--qr-text); }
.faq .breit > * { max-width:820px; }
.faq details { background:var(--karte); border:1px solid var(--rand); border-radius:14px; margin:0 0 10px; }
.faq summary { cursor:pointer; font-weight:600; padding:15px 52px 15px 18px; list-style:none; position:relative; min-height:44px; }
.faq summary::-webkit-details-marker { display:none; }
.faq summary::after { content:"+"; position:absolute; right:18px; top:9px; font-size:24px; font-weight:500; color:var(--akzent); }
.faq details[open] summary::after { content:"–"; }
.faq details p { margin:0; padding:0 18px 16px; color:var(--leise); }
.faq details p.echt code { overflow-wrap:anywhere; word-break:break-all; }
footer { border-top:1px solid var(--rand); padding:28px 0 44px; font-size:14px; color:var(--leise); }
footer p { margin:0 0 8px; }
footer .zeile { display:flex; flex-wrap:wrap; gap:4px 18px; }
footer code { font-size:12.5px; word-break:break-all; }
@media (max-width:900px) {
  .hero .breit { grid-template-columns:1fr; gap:12px; padding-bottom:48px; }
  figure.bild { height:300px; max-width:440px; width:100%; margin:0 auto; }
  .bsp { width:168px; height:228px; } .bsp.vorne img { width:104px; height:104px; } .bsp.hinten .wort { font-size:28px; }
  ol.schritte { grid-template-columns:1fr; }
  ol.schritte > li { display:grid; grid-template-columns:minmax(0, 1fr) 150px; grid-template-areas:"t s" "p s"; align-items:start; gap:8px 16px; }
  ol.schritte > li > h4 { grid-area:t; } ol.schritte > li > p { grid-area:p; } ol.schritte > li > svg { grid-area:s; align-self:center; }
  .drin { grid-template-columns:repeat(2, minmax(0, 1fr)); }
  .handy { grid-template-columns:1fr; } .qr-box { margin:0 auto; } }
@media (max-width:620px) {
  .breit, .kopf { padding-left:16px; padding-right:16px; }
  .kopf .marke span { font-size:16px; }
  .abschnitt { padding:44px 0; }
  a.gross { width:100%; justify-content:center; }
  ol.schritte > li { grid-template-columns:1fr; grid-template-areas:"s" "t" "p"; padding:16px; }
  svg.skizze { max-width:200px; }
  .drin { grid-template-columns:1fr; } }
@media (pointer: coarse) { nav.sprachen a, button.chip { min-height:44px; } }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior:auto; } a.gross { transition:none; } a.gross:hover { transform:none; } }
@media print { nav.sprachen, .os-wahl, .auch, .springen { display:none !important; } .hero { background:none; } }"""

DOWNLOAD_JS = """/* Me Goos-ta Deutsch – Download-Seite (gebaut von bau_webapp.py). Sprache EN · DE · ES (Anker #de/#es/#en, sonst die
   gemerkte Wahl, sonst Englisch – nie die Gerätesprache) und System (Knopf + Schritte). Ohne dieses Skript zeigt die
   Seite Englisch und alle drei Systeme. Keine Anfragen, kein Tracking. */
(function () {
  "use strict";
  var h = document.documentElement, SPRACHEN = ["en", "de", "es"], SCHLUESSEL = "mgd-download-sprache";
  function gemerkt() { try { return localStorage.getItem(SCHLUESSEL); } catch (e) { return null; } }
  function merken(l) { try { localStorage.setItem(SCHLUESSEL, l); } catch (e) { /* privates Fenster: dann eben nicht */ } }
  function anker() { var a = (location.hash || "").slice(1).toLowerCase(); return SPRACHEN.indexOf(a) >= 0 ? a : null; }
  function system() {
    var ua = navigator.userAgent || "", p = (navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || "";
    if (/Android|iPhone|iPad|iPod/i.test(ua) || (/Mac/i.test(p) && navigator.maxTouchPoints > 1)) return "handy";
    if (/Win/i.test(p) || /Windows/i.test(ua)) return "win";
    if (/Mac/i.test(p) || /Mac OS X/i.test(ua)) return "mac";
    if (/Linux|X11|CrOS/i.test(p + " " + ua)) return "linux";
    return "";
  }
  function sprache(l) {
    var s = document.getElementById(l); if (!s) return;
    h.setAttribute("data-sprache", l); h.lang = l;
    document.title = s.getAttribute("data-titel") || document.title;
  }
  function os(o) {
    if (o) h.setAttribute("data-os", o); else h.removeAttribute("data-os");
    var k = document.querySelectorAll(".os-wahl [data-os-wahl]");
    for (var i = 0; i < k.length; i++) k[i].setAttribute("aria-pressed", String(k[i].getAttribute("data-os-wahl") === o));
  }
  var geraet = system(), i, liste;
  h.classList.add("js");
  var g = gemerkt();
  sprache(anker() || (SPRACHEN.indexOf(g) >= 0 ? g : "en"));
  os(geraet === "handy" ? "" : geraet);
  liste = document.querySelectorAll("[data-nur-js]");
  for (i = 0; i < liste.length; i++) liste[i].hidden = false;
  if (geraet === "handy") {
    liste = document.querySelectorAll("[data-nur-handy]");
    for (i = 0; i < liste.length; i++) liste[i].hidden = false;
  }
  document.addEventListener("click", function (e) {
    var z = e.target && e.target.closest ? e.target.closest("[data-l], [data-os-wahl]") : null;
    if (!z) return;
    if (z.hasAttribute("data-l")) {
      e.preventDefault();
      var l = z.getAttribute("data-l");
      sprache(l); merken(l);
      try { history.replaceState(null, "", "#" + l); } catch (f) { /* z. B. als Datei geöffnet */ }
      var neu = document.querySelector("#" + l + " nav [data-l='" + l + "']");
      if (neu) neu.focus();
    } else os(z.getAttribute("data-os-wahl"));
  });
  window.addEventListener("hashchange", function () { var l = anker(); if (l) { sprache(l); merken(l); } });
  try { sessionStorage.removeItem("mgd-download-rettung"); } catch (e) { /* egal */ }   // Seite ist da: Rettung fertig
})();
"""

# Rettung (Fix 2.2, 21.10.2026): Der Service Worker der App 2.0 kannte die Download-Seite noch nicht und liefert für
# download/ den gespeicherten Startbildschirm der App (Symbol + Name, sonst nichts). Dessen Skript „app.js“ liegt relativ
# unter download/ – das holt der alte Service Worker übers Netz, also kommt diese Datei. Sie übergibt an die wartende neue
# Version (die lässt download/ durch, „weiter“ wie in app.js) oder meldet den alten Service Worker ab und lädt neu.
# Nutzerdaten der App (IndexedDB) bleiben, der Vorrat (caches) auch. Sprache wie die Seite: Anker, gemerkte Wahl, Englisch.
RETTUNG_JS = """/* Me Goos-ta Deutsch – Rettung der Download-Seite (gebaut von bau_webapp.py). Läuft nur, wenn ein Service Worker der
   App von vor 2.1 hier den Startbildschirm der App zeigt: neue Version übernehmen bzw. alten Service Worker abmelden,
   dann neu laden. Nutzerdaten der App bleiben. */
(function () {
  "use strict";
  var TEXT = { en: "Shooing out an old app version – the download page opens in a moment.",
    de: "Eine alte App-Version watschelt gerade hinaus – gleich öffnet sich die Download-Seite.",
    es: "Una versión antigua de la app se va contoneando – la página de descarga se abre en un momento." };
  var ZAEHLER = "mgd-download-rettung", l = (location.hash || "").slice(1).toLowerCase(), versuche = 0, fertig = false;
  if (!TEXT[l]) { try { l = localStorage.getItem("mgd-download-sprache"); } catch (e) { l = null; } }
  if (!TEXT[l]) l = "en";
  document.documentElement.lang = l;
  var feld = document.getElementById("app-start-text"), bild = document.querySelector("#app-start img");
  if (feld) feld.textContent = TEXT[l] + " 🪿";
  if (bild) bild.src = "../symbol.svg";
  try { versuche = Number(sessionStorage.getItem(ZAEHLER)) || 0; sessionStorage.setItem(ZAEHLER, String(versuche + 1)); }
  catch (e) { versuche = 0; }
  function neu() { if (!fertig && versuche < 3) { fertig = true; location.reload(); } }
  var sw = navigator.serviceWorker;
  if (!sw) return neu();
  sw.addEventListener("controllerchange", neu);
  sw.getRegistration().then(function (reg) {
    if (!reg) return neu();
    if (versuche >= 1) return reg.unregister().then(neu, neu);   // Übergabe hat nicht gereicht: alten abmelden
    function weiter(w) { if (w) w.postMessage("weiter"); }
    weiter(reg.waiting);
    reg.addEventListener("updatefound", function () {
      var w = reg.installing;
      if (w) w.addEventListener("statechange", function () { if (w.state === "installed") weiter(w); });
    });
    reg.update().catch(function () { /* offline: dann gleich abmelden */ reg.unregister().then(neu, neu); });
    setTimeout(function () { reg.unregister().then(neu, neu); }, 20000);
  }, neu);
})();
"""


def _mb(groesse, l):
    s = f"{groesse / 1e6:.1f} MB"
    return s.replace(".", ",") if l == "de" else s


def downloadseite(version, zip_info, adresse):
    """(index.html, seite.js) der Download-Seite: Abschnitte de/es/en (Englisch zuletzt = Standard ohne Skript)."""
    sys.path.insert(0, str(QUELLE / "Programm"))
    import qr_code
    ad = download_adressen(adresse, version, zip_info)
    e = html_esc
    haupt = None
    if zip_info and zip_info.get("signiert"):                   # „Echtheit prüfen“ nur bei signiertem Release (seit 2.5)
        import signatur
        haupt = next((k for k in signatur.vertraut() if k[0] == "haupt"), None)
        if not haupt:
            sys.exit("Signiertes Release, aber Programm/signatur.py nennt keinen Haupt-Schlüssel.")
    teile = []
    for l in ("de", "es", "en"):
        t = DT[l]
        nav = "".join(f'<a href="#{x}" data-l="{x}" hreflang="{x}" lang="{x}"{aktuell}>{x.upper()}</a>'
                      for x, aktuell in ((x, ' aria-current="true"' if x == l else "") for x in ("en", "de", "es")))
        knoepfe = "".join(f'<a class="gross" data-os-teil="{o}" href="{e(ad["zip"])}">{PFEIL}<span>{e(t["knopf"].format(os=n))}</span></a>'
                          for o, n in SYSTEME)
        meta = (t["meta"].format(version=version, groesse=_mb(zip_info["groesse"], l)) if zip_info
                else t["meta_ohne"].format(version=version))
        chips = "".join(f'<button type="button" class="chip" data-os-wahl="{o}">{n}</button>' for o, n in SYSTEME)
        bloecke = []
        for o, n in SYSTEME:
            schritte = "".join(
                f'<li>{pc_skizze(s[2], s[3], titel=s[0])}<h4>{e(s[0])}</h4><p>{s[1].replace("{befehl}", e(LINUX_BEFEHL))}</p></li>'
                for s in t[o])
            hilfe = t[o + "_hilfe"]
            bloecke.append(f'<div class="os-block" data-os-teil="{o}"><h3>{n}</h3><ol class="schritte">{schritte}</ol>'
                           f'<div class="kasten"><h4>{e(hilfe[0])}</h4><p>{hilfe[1]}</p></div></div>')
        drin = "".join(f'<article><div class="symbol" aria-hidden="true"><svg viewBox="0 0 24 24">{DRIN_SYMBOLE[s]}</svg></div>'
                       f'<h3>{e(k)}</h3><p>{e(x)}</p></article>' for s, k, x in t["drin"])
        fragen = "".join(f"<details><summary>{e(q)}</summary><p>{a}</p></details>" for q, a in t["faq"])
        if haupt:
            fragen += (f'<details id="{l}-echtheit"><summary>{e(t["echt_titel"])}</summary><p class="echt">' + t["echt_text"].format(
                summen=f'<a href="{e(ad["summen"])}">SHA256SUMS.txt</a>',
                minisig=f'<a href="{e(ad["signatur"])}">SHA256SUMS.txt.minisig</a>', id=e(signatur.schluessel_id(haupt[1])),
                befehl=f"<code>minisign -Vm SHA256SUMS.txt -P {e(signatur.schluessel_text(haupt[1], haupt[2]))}</code>",
                zip=e(zip_info["name"])) + "</p></details>")
        sha_zeile = (f'<p>{e(t["sha_titel"])}: <code>{zip_info["sha256"]}</code> · <a href="{e(ad["summen"])}">SHA256SUMS.txt</a></p>'
                     if zip_info else f'<p>{e(t["sha_ohne"])}</p>')
        teile.append(f"""<div class="sprache" id="{l}" lang="{l}" data-titel="{e(t["titel"])}">
<a class="springen" href="#{l}-inhalt">{e(t["springen"])}</a>
<header class="kopf"><a class="marke" href="#{l}"><img src="../symbol.svg" alt="" width="40" height="40"><span>Me Goos-ta Deutsch</span></a>
<nav class="sprachen" aria-label="Language · Sprache · Idioma">{nav}</nav></header>
<main id="{l}-inhalt">
<section class="hero"><div class="breit"><div>
<div class="handy-hinweis" data-nur-handy hidden><span>📲 {e(t["handy"])}</span><a class="knopf2" href="{e(adresse)}">{e(t["handy_knopf"])}</a></div>
<p class="oben">{e(t["oben"])}</p>
<h1>{e(t["h1"])}</h1>
<p class="lead">{e(t["lead"])}</p>
<div class="laden">{knoepfe}</div>
<p class="meta">{e(meta)}</p>
<p class="paket">{e(t["paket"])}</p>
<div class="auch" data-nur-js hidden><span>{e(t["auch"])}</span>{chips}</div>
</div>
<figure class="bild" role="img" aria-label="{e(t["karte_aria"])}">
<div class="bsp vorne" aria-hidden="true"><img src="../symbol.svg" alt=""><span>Gans alt</span></div>
<div class="bsp hinten" aria-hidden="true"><span class="kuerzel">ES</span><span class="wort" lang="es">viejo</span>{TEICH_GANS}</div>
<figcaption aria-hidden="true">{e(t["karte_unter"])}</figcaption>
</figure></div></section>
<section class="abschnitt hell" id="{l}-schritte"><div class="breit">
<h2>{e(t["schritte_titel"])}</h2>
<p class="unter">{e(t["schritte_lead"])}</p>
<div class="os-wahl" data-nur-js hidden role="group" aria-label="{e(t["os_wahl"])}">{chips}</div>
{"".join(bloecke)}
</div></section>
<section class="abschnitt" id="{l}-drin"><div class="breit">
<h2>{e(t["drin_titel"])}</h2>
<div class="drin">{drin}</div>
</div></section>
<section class="abschnitt hell" id="{l}-handy"><div class="breit handy"><div>
<h2>{e(t["handy_titel"])}</h2>
<p>{e(t["handy_text"])}</p>
<p><a class="gross leicht" href="{e(adresse)}">📲 {e(t["handy_knopf"])}</a></p>
<p class="pfad">{e(adresse)}</p></div>
<div class="qr-box">{qr_code.qr_svg(adresse, titel=t["qr_aria"])}<p>{e(t["handy_qr"])}</p></div>
</div></section>
<section class="abschnitt faq" id="{l}-fragen"><div class="breit">
<h2>{e(t["faq_titel"])}</h2>
{fragen}
</div></section>
</main>
<footer><div class="breit">
<p class="zeile"><span>Me Goos-ta Deutsch {e(version)}</span><span>{e(t["lizenz"])} · © Eine Gans namens Lukas</span>
<a href="{e(ad["repo"])}">{e(t["quelle"])}</a><a href="{e(ad["notizen"])}">{e(t["notizen"])}</a></p>
{sha_zeile}
<p>{e(t["gruss"])} 🪿</p>
</div></footer>
</div>""")
    en = DT["en"]
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'none'; base-uri 'none'; form-action 'none'">
<title>{e(en["titel"])}</title>
<meta name="description" content="{e(en["beschreibung"])}">
<link rel="canonical" href="{e(ad["seite"])}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(en["titel"])}">
<meta property="og:description" content="{e(en["beschreibung"])}">
<meta property="og:url" content="{e(ad["seite"])}">
<meta property="og:image" content="{e(adresse)}symbole/symbol-512.png">
<meta name="theme-color" content="{HINTERGRUND}">
<link rel="icon" href="../favicon.ico" sizes="any">
<link rel="icon" href="../symbol.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="../symbole/apple-touch-icon.png">
<style>
{DOWNLOAD_CSS}
</style>
<script src="seite.js" defer></script>
</head>
<body>
{chr(10).join(teile)}
</body>
</html>
"""
    return html, DOWNLOAD_JS


# kleine Teich-Gans für die Beispiel-Rückseite (wie auf den Karten unten rechts, vereinfacht)
TEICH_GANS = ('<svg viewBox="0 0 64 48" aria-hidden="true"><ellipse cx="32" cy="40" rx="30" ry="7" fill="#BFDDF2"/>'
              '<ellipse cx="30" cy="33" rx="17" ry="9" fill="#FFFFFF" stroke="#C9DCEB"/>'
              '<path d="M38 30c-2-8 0-15 6-18" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round" fill="none"/>'
              '<circle cx="45" cy="12" r="6" fill="#FFFFFF"/><path d="M50 10l9 2-9 3z" fill="#F6A94B"/>'
              '<circle cx="46" cy="11" r="1.6" fill="#1B2D4F"/></svg>')


def downloadseite_schreiben(out, version, zip_info, gefordert=False):
    """Schreibt web-app/download/ (index.html + seite.js + app.js = Rettung bei alter App); ohne Adresse in web_adresse.txt
    entfällt die Seite."""
    pfad = QUELLE / "Programm" / "web_adresse.txt"
    zeilen = pfad.read_text(encoding="utf-8").strip().splitlines() if pfad.is_file() else []
    adresse = zeilen[0].strip() if zeilen else ""
    if not adresse.startswith("https://"):
        if gefordert:
            sys.exit(f"Keine Adresse in {pfad} – ohne sie gibt es keine Download-Seite.")
        return None
    html, js = downloadseite(version, zip_info, adresse)
    ziel = out / "download"
    ziel.mkdir(parents=True, exist_ok=True)
    (ziel / "index.html").write_bytes(html.encode("utf-8"))
    (ziel / "seite.js").write_bytes(js.encode("utf-8"))
    (ziel / "app.js").write_bytes(RETTUNG_JS.encode("utf-8"))   # nur für den Startbildschirm einer App von vor 2.1
    return dict(pfad=ziel, adresse=adresse + "download/", info=zip_info, **{"zip": download_adressen(adresse, version, zip_info)["zip"]})


if __name__ == "__main__" and "--installationsdateien" in sys.argv:
    QUELLE = Path(sys.argv[1]).resolve()
    adr = installationsdateien(QUELLE)
    print(f"✓ {', '.join(INSTALL_DATEIEN.values())} → {QUELLE}  ({adr})")
elif __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    QUELLE, ZIEL = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    cache = sys.argv[sys.argv.index("--cache") + 1] if "--cache" in sys.argv else None
    rzip = sys.argv[sys.argv.index("--release-zip") + 1] if "--release-zip" in sys.argv else None
    out, v, liste, namen, modelle, seite = bauen(ZIEL, "--ohne-pyodide" in sys.argv, "--ohne-modelle" in sys.argv, cache, rzip)
    offline = sum(x[1] for x in liste)
    print(f"✓ {out}  (Version {v}, {len(liste)} Dateien offline, {offline / 1e6:.1f} MB; Programm-Paket {len(namen)} Dateien"
          + (f"; Modelle auf Wunsch: {', '.join(modelle)} {sum(m['groesse'] for _, m in modelle.values()) / 1e6:.0f} MB" if modelle else "")
          + ")")
    if seite:
        print(f"✓ Download-Seite {seite['adresse']}  → {seite['zip']}"
              + (f"  ({seite['info']['groesse'] / 1e6:.1f} MB, SHA-256 {seite['info']['sha256'][:16]}…)" if seite["info"] else
                 "  (ohne --release-zip: Link auf das neueste Release)"))
    else:
        print("  (keine Adresse in web_adresse.txt – Download-Seite entfällt)")
else:
    QUELLE = Path(os.environ.get("MGD_QUELLE", HIER.parent / "Me-Goos-ta-Deutsch")).resolve()
