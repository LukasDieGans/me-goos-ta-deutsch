#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ME GOOS-TA DEUTSCH – Sprachen der Kartenrückseite (Tool „Sprachen“)   Version 2.1 (20.10.2026)
=============================================================================================
Die Rückseite einer Karte ist normalerweise Spanisch (wie in Mexiko gesprochen) – immer da, nicht entfernbar. Weitere
Sprachen sind ein Tool: jede Sprache wird einzeln installiert (spart Platz) und bestimmt dann als „Zielsprache“ die
Rückseite und die Richtung der automatischen Übersetzung.

  Sprache                      Schrift        Paket (Daten/sprachen/<code>/)
  en nds fr it tr sv no pl     lateinisch     nichts zu laden – Poppins hat alle Zeichen (Installieren = aktivieren)
  ru                           kyrillisch     Noto Sans Regular + Bold (~1,3 MB)
  ja · ko · zh                 CJK / Hangul   IBM Plex Sans JP / KR / SC Regular + Bold (5 / 6 / 17 MB)
  hi                           Devanagari     Poppins hat die Zeichen; Formen der Silben über uharfbuzz (~1,6 MB)
  ar                           arabisch       IBM Plex Sans Arabic Regular + Bold + uharfbuzz (rechts nach links)

Alle Schriften: SIL Open Font License 1.1, TrueType-Konturen (ReportLab kann kein CFF), feste Download-Adresse
(Git-Revision) mit SHA-256 und Größe. uharfbuzz (Apache-2.0, enthält HarfBuzz unter MIT-Lizenz) wird per pip in
Daten/sprachen/_pakete gelegt – nicht ins eigene Python, damit es sich jederzeit wieder entfernen lässt; nur der
Druck (gans_lernkarten, ab G09) nimmt den Ordner mit `aktiviere_pakete()` in den Suchpfad. Das letzte Sprachpaket,
das ihn braucht, entfernt ihn wieder. Programmcode wird sonst nie nachgeladen.

Laden über die Warteschlange der Oberfläche: `python3 sprachen.py --laden <code>` (fortsetzbar, Prüfsummen,
Platzprüfung, Fortschritt als „  NN %“). Selbsttest: test_erweiterungen.py (Abschnitt E25).
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import uebersetzer  # noqa: E402


def L(de, en, es):
    return {"de": de, "en": en, "es": es}


MB = 1024 * 1024
STANDARD = "es"

# ---------------------------------------------------------------------------------------------
# Schriften und Pakete (feste Revisionen; Größen in Bytes)
# ---------------------------------------------------------------------------------------------
_G = "https://raw.githubusercontent.com/google/fonts/67bc647ce1910e92f461bcc82aae30f21d21a9cc/ofl/"
_N = "https://raw.githubusercontent.com/notofonts/notofonts.github.io/5c3913063bb189df4edc94b766584dfb4c04a187/fonts/NotoSans/hinted/ttf/"
_P = "https://raw.githubusercontent.com/IBM/plex/39276912b05f700ee1dd491950c35d8697214208/packages/plex-sans-sc/"
_OFL_PLEX = ("OFL.txt", 4456, "7e6b2818edbd8f6a01ae80641cc8f16a51080d08fb4e532be3a0b6f74adb07da")


def _d(name, url, groesse, sha256, stil=None):
    return dict(name=name, url=url, groesse=groesse, sha256=sha256, stil=stil)


SCHRIFTEN = {
    "ru": dict(name="Noto Sans", lizenz="OFL-1.1", dateien=[
        _d("NotoSans-Regular.ttf", _N + "NotoSans-Regular.ttf", 621572,
           "478c558ea716033cd60c03438f628dfa75694dcf6b5f6d505a2f05fd2b4f3823", "regular"),
        _d("NotoSans-Bold.ttf", _N + "NotoSans-Bold.ttf", 631484,
           "1df075a380fc7cb898acf64c1f7b3b4dd780de3caa860178bf929de35817a913", "bold"),
        _d("OFL.txt", _G + "notosans/OFL.txt", 4396, "cee9892f9f0cc8fe882c9e9537ee6a89621d86ee7ceaf70b02e2b2b1c25c061a")]),
    "ja": dict(name="IBM Plex Sans JP", lizenz="OFL-1.1", dateien=[
        _d("IBMPlexSansJP-Regular.ttf", _G + "ibmplexsansjp/IBMPlexSansJP-Regular.ttf", 2396484,
           "372f8bba95f386856ae435dc0e69f08db1cac29bed513d99171a0ae2d307ba2a", "regular"),
        _d("IBMPlexSansJP-Bold.ttf", _G + "ibmplexsansjp/IBMPlexSansJP-Bold.ttf", 2391376,
           "bd8a98b9b55c9ea3f0fa1ed094c15981788cc9a41b0357f4453014fd1d44da19", "bold"),
        _d(_OFL_PLEX[0], _G + "ibmplexsansjp/OFL.txt", *_OFL_PLEX[1:])]),
    "ko": dict(name="IBM Plex Sans KR", lizenz="OFL-1.1", dateien=[
        _d("IBMPlexSansKR-Regular.ttf", _G + "ibmplexsanskr/IBMPlexSansKR-Regular.ttf", 2797100,
           "53750379270312368cf7641901f43a98dd892e3d9d5798cf25cdc245c85c71c0", "regular"),
        _d("IBMPlexSansKR-Bold.ttf", _G + "ibmplexsanskr/IBMPlexSansKR-Bold.ttf", 2875584,
           "9d82a8be5330f6d7b53121262867b402baca672eb69b852928f06d185d357f7d", "bold"),
        _d(_OFL_PLEX[0], _G + "ibmplexsanskr/OFL.txt", *_OFL_PLEX[1:])]),
    "zh": dict(name="IBM Plex Sans SC", lizenz="OFL-1.1", dateien=[
        _d("IBMPlexSansSC-Regular.ttf", _P + "fonts/complete/ttf/hinted/IBMPlexSansSC-Regular.ttf", 8455892,
           "012e587c5a78d25f456057614b880fc7450b748c352573d8052245df2a71158a", "regular"),
        _d("IBMPlexSansSC-Bold.ttf", _P + "fonts/complete/ttf/hinted/IBMPlexSansSC-Bold.ttf", 8426792,
           "3e94ef1df394eae336cc1bc98f2160b58e2cab186f47d820e4c808aef1f4e28f", "bold"),
        _d(_OFL_PLEX[0], _P + "LICENSE.txt", *_OFL_PLEX[1:])]),
    "ar": dict(name="IBM Plex Sans Arabic", lizenz="OFL-1.1", dateien=[
        _d("IBMPlexSansArabic-Regular.ttf", _G + "ibmplexsansarabic/IBMPlexSansArabic-Regular.ttf", 235924,
           "6f611412270a132bbac838da9259d4c68569b4175f3b3b8fa3fa36a30b56dab9", "regular"),
        _d("IBMPlexSansArabic-Bold.ttf", _G + "ibmplexsansarabic/IBMPlexSansArabic-Bold.ttf", 246992,
           "691e0c891a38637ae6bbdb69700f8042cb0724a137bee615068ffdb92244f61f", "bold"),
        _d(_OFL_PLEX[0], _G + "ibmplexsansarabic/OFL.txt", *_OFL_PLEX[1:])]),
}

# pip-Pakete für Schriften mit Formen (Shaping). Größe: Download (Rad für Windows) und Platz nach dem Entpacken.
PAKETE = {"uharfbuzz": dict(version="0.56.3", lizenz="Apache-2.0 (HarfBuzz: MIT)", groesse=1_553_706, platz=3_445_344,
                            modul="uharfbuzz")}


# ---------------------------------------------------------------------------------------------
# Katalog: 15 Sprachen (es = Standard). Dienste: Vorlagen-Code im deutschen Wiktionary (Ü/Üt), Abschnittsname für
# die Rückrichtung, MyMemory- und DeepL-Codes (None = Dienst kann die Sprache nicht → wird übersprungen).
# ---------------------------------------------------------------------------------------------
def _s(code, name, eigen, schrift, *, richtung="ltr", umbruch="wort", zeichen="", wikt=None, abschnitt=None,
       mymemory=None, deepl=None, deepl_quelle=None, umschrift=False, pakete=()):
    return dict(code=code, name=name, eigenname=eigen, schrift=schrift, richtung=richtung, umbruch=umbruch,
                sonderzeichen=zeichen.split(), umschrift=umschrift, pakete=tuple(pakete),
                dienste=dict(wiktionary=tuple(wikt or (code,)), abschnitt=tuple(abschnitt or ()),
                             mymemory=tuple(mymemory or ()), deepl=tuple(deepl or ()), deepl_quelle=deepl_quelle))


SPRACHEN = {s["code"]: s for s in [
    _s("es", L("Spanisch", "Spanish", "español"), "español", "latein", zeichen="á é í ó ú ñ ü ¿ ¡",
       abschnitt=["Spanisch"], mymemory=["es-MX", "es"], deepl=["ES-419", "ES"], deepl_quelle="ES"),
    _s("en", L("Englisch", "English", "inglés"), "English", "latein", abschnitt=["Englisch"], mymemory=["en"],
       deepl=["EN-US"], deepl_quelle="EN"),
    _s("nds", L("Plattdeutsch", "Low German", "bajo alemán"), "Plattdüütsch", "latein", zeichen="ä ö ü ß",
       abschnitt=["Niederdeutsch", "Plattdeutsch"]),
    _s("fr", L("Französisch", "French", "francés"), "français", "latein",
       zeichen="à â æ ç é è ê ë î ï ô œ ù û ü ÿ « »", abschnitt=["Französisch"], mymemory=["fr"], deepl=["FR"],
       deepl_quelle="FR"),
    _s("it", L("Italienisch", "Italian", "italiano"), "italiano", "latein", zeichen="à è é ì ò ù",
       abschnitt=["Italienisch"], mymemory=["it"], deepl=["IT"], deepl_quelle="IT"),
    _s("tr", L("Türkisch", "Turkish", "turco"), "Türkçe", "latein", zeichen="ç ğ ı İ ö ş ü", abschnitt=["Türkisch"],
       mymemory=["tr"], deepl=["TR"], deepl_quelle="TR"),
    _s("sv", L("Schwedisch", "Swedish", "sueco"), "svenska", "latein", zeichen="å ä ö", abschnitt=["Schwedisch"],
       mymemory=["sv"], deepl=["SV"], deepl_quelle="SV"),
    _s("no", L("Norwegisch", "Norwegian", "noruego"), "norsk (bokmål)", "latein", zeichen="æ ø å", wikt=["nb", "no"],
       abschnitt=["Bokmål", "Norwegisch"], mymemory=["nb", "no"], deepl=["NB"], deepl_quelle="NB"),
    _s("pl", L("Polnisch", "Polish", "polaco"), "polski", "latein", zeichen="ą ć ę ł ń ó ś ź ż",
       abschnitt=["Polnisch"], mymemory=["pl"], deepl=["PL"], deepl_quelle="PL"),
    _s("ru", L("Russisch", "Russian", "ruso"), "русский", "kyrillisch", zeichen="ё й ъ ь э ю я", umschrift=True,
       abschnitt=["Russisch"], mymemory=["ru"], deepl=["RU"], deepl_quelle="RU"),
    _s("ja", L("Japanisch", "Japanese", "japonés"), "日本語", "cjk", umbruch="zeichen", umschrift=True,
       abschnitt=["Japanisch"], mymemory=["ja"], deepl=["JA"], deepl_quelle="JA"),
    _s("zh", L("Chinesisch", "Chinese", "chino"), "中文（简体）", "cjk", umbruch="zeichen", umschrift=True,
       wikt=["zh", "cmn"], abschnitt=["Chinesisch"], mymemory=["zh-CN"], deepl=["ZH-HANS", "ZH"], deepl_quelle="ZH"),
    _s("ko", L("Koreanisch", "Korean", "coreano"), "한국어", "hangul", umschrift=True, abschnitt=["Koreanisch"],
       mymemory=["ko"], deepl=["KO"], deepl_quelle="KO"),
    _s("hi", L("Hindi", "Hindi", "hindi"), "हिन्दी", "devanagari", umschrift=True, pakete=["uharfbuzz"],
       abschnitt=["Hindi"], mymemory=["hi"]),
    _s("ar", L("Hocharabisch", "Standard Arabic", "árabe estándar"), "العربية", "arabisch", richtung="rtl",
       umschrift=True, pakete=["uharfbuzz"], abschnitt=["Arabisch"], mymemory=["ar"], deepl=["AR"], deepl_quelle="AR"),
]}


class SprachFehler(Exception):
    """Fehler mit Code (gans_ui übersetzt ihn); werte für den Text."""
    def __init__(self, code, **werte):
        super().__init__(code)
        self.code, self.werte = code, werte


FEHLER = {
    "unbekannt": L("Diese Sprache kennt das Programm nicht.", "The program doesn’t know this language.",
                   "El programa no conoce este idioma."),
    "platz": L("Für diese Sprache fehlen noch {mb} MB freier Speicher – räum ein bisschen auf, dann klappt’s.",
               "This language still needs {mb} MB of free space – tidy up a little and it’ll work.",
               "A este idioma le faltan {mb} MB de espacio libre: libera un poco y listo."),
    "pruefsumme": L("Die Datei {name} ist unterwegs beschädigt worden (Prüfsumme). Nichts installiert – einfach "
                    "nochmal versuchen.", "The file {name} got damaged on the way (checksum). Nothing installed – just "
                    "try again.", "El archivo {name} se dañó por el camino (suma de verificación). No se instaló nada: "
                    "inténtalo de nuevo."),
    "pip": L("Das Zusatzpaket {paket} ließ sich nicht installieren: {grund}",
             "The add-on package {paket} could not be installed: {grund}",
             "No se pudo instalar el paquete adicional {paket}: {grund}"),
    "standard": L("Spanisch ist immer dabei und lässt sich nicht entfernen.", "Spanish is always included and can’t "
                  "be removed.", "El español siempre está incluido y no se puede quitar."),
}


def fehler_text(f, sprache="en"):
    return (FEHLER.get(f.code) or FEHLER["unbekannt"]).get(sprache, FEHLER["unbekannt"]["en"]).format(**f.werte)


# =============================================================================================
# Abfragen
# =============================================================================================
def _ui(sprache):
    return sprache if sprache in ("de", "en", "es") else "en"


def name(code, sprache="en"):
    """Name der Sprache in der Sprache der Oberfläche („Japanisch“ / „Japanese“ / „japonés“)."""
    s = SPRACHEN.get(code) or SPRACHEN[STANDARD]
    return s["name"][_ui(sprache)]


def ordner() -> Path:
    return uebersetzer.daten_ordner() / "sprachen"


def paket_ordner(code) -> Path:
    return ordner() / code


def pakete_ordner() -> Path:
    """pip-Pakete für das Formen der Schrift (uharfbuzz) – nur für die Sprachen, die das brauchen."""
    return ordner() / "_pakete"


def _pruefe(code):
    if code not in SPRACHEN:
        raise SprachFehler("unbekannt")


def _groesse(p):
    try:
        return p.stat().st_size if p.is_file() else 0
    except OSError:
        return 0


def dateien(code):
    return list((SCHRIFTEN.get(code) or {}).get("dateien") or [])


def noetige_pakete(code):
    """pip-Pakete einer Sprache (uharfbuzz für hi/ar). Web-App: keine – dort ohne Formen (wie ohne uharfbuzz am Rechner)."""
    return [] if sys.platform == "emscripten" else list(SPRACHEN[code]["pakete"])


def _paket_da(paket):
    ziel = pakete_ordner() / PAKETE[paket]["modul"]
    return ziel.is_dir() and any(ziel.glob("*.py"))


def installiert(code) -> bool:
    """es immer; sonst: paket.json da, alle Schriftdateien vollständig, nötige pip-Pakete da."""
    if code == STANDARD:
        return True
    if code not in SPRACHEN:
        return False
    o = paket_ordner(code)
    if not (o / "paket.json").is_file():
        return False
    return all(_groesse(o / d["name"]) == d["groesse"] for d in dateien(code)) and \
        all(_paket_da(p) for p in noetige_pakete(code))


def installierte():
    return [c for c in SPRACHEN if installiert(c)]


def weitere_installiert():
    return [c for c in installierte() if c != STANDARD]


def groesse(code):
    """Download in Bytes (Schriften + noch fehlende pip-Pakete)."""
    return sum(d["groesse"] for d in dateien(code)) + sum(PAKETE[p]["groesse"] for p in SPRACHEN[code]["pakete"])


def platz(code):
    return sum(d["groesse"] for d in dateien(code)) + sum(PAKETE[p]["platz"] for p in SPRACHEN[code]["pakete"])


def belegt(code=None):
    """Belegter Platz einer Sprache (ohne Code: alle Sprachpakete samt pip-Paketen)."""
    if code is None:
        return sum(belegt(c) for c in SPRACHEN if c != STANDARD) + _ordner_groesse(pakete_ordner())
    o = paket_ordner(code)
    return sum(_groesse(o / n) for n in _eigene_namen(code))


def _ordner_groesse(o):
    try:
        return sum(p.stat().st_size for p in o.rglob("*") if p.is_file() and not p.is_symlink())
    except OSError:
        return 0


def _eigene_namen(code):
    """Nur diese Dateinamen gehören einem Sprachpaket (werden je gelöscht)."""
    namen = ["paket.json"]
    for d in dateien(code):
        namen += [d["name"], d["name"] + ".part"]
    return namen


def angefangen(code):
    o = paket_ordner(code)
    return not installiert(code) and any(_groesse(o / (d["name"] + ".part")) or _groesse(o / d["name"])
                                         for d in dateien(code))


def schriften(code):
    """Schriftdateien für den Druck (G09): {"regular": Pfad, "bold": Pfad} – None = Poppins (lateinisch, hi)."""
    if not installiert(code) or not dateien(code):
        return None
    return {d["stil"]: paket_ordner(code) / d["name"] for d in dateien(code) if d["stil"]}


def braucht_formen(code):
    return "uharfbuzz" in SPRACHEN.get(code, {}).get("pakete", ())


def aktiviere_pakete():
    """Nimmt Daten/sprachen/_pakete in den Suchpfad (vor dem Import von reportlab!). True, wenn uharfbuzz ladbar ist."""
    o = str(pakete_ordner())
    if pakete_ordner().is_dir() and o not in sys.path:
        sys.path.insert(0, o)
    try:
        import uharfbuzz  # noqa: F401
        return True
    except Exception:  # noqa: BLE001 – ImportError oder eine gesperrte DLL (Smart App Control)
        return False


def zielsprache(einstellungen=None):
    """Aktuelle Zielsprache aus ui_einstellungen.json (gans_ui schreibt sie) – nur, wenn installiert, sonst es."""
    if einstellungen is None:
        einstellungen = uebersetzer._lies_json(HIER / "ui_einstellungen.json")
    code = einstellungen.get("zielsprache") if isinstance(einstellungen, dict) else None
    return code if isinstance(code, str) and code in SPRACHEN and installiert(code) else STANDARD


def info(code, sprache="en"):
    """Eintrag für die Oberfläche (Namen in allen drei Sprachen für den Austausch in G08)."""
    s = SPRACHEN[code]
    return dict(code=code, kurz=code.upper(), name=s["name"][_ui(sprache)], namen=dict(s["name"]),
                eigenname=s["eigenname"], richtung=s["richtung"], schrift=s["schrift"], umbruch=s["umbruch"],
                sonderzeichen=list(s["sonderzeichen"]), umschrift=s["umschrift"], standard=code == STANDARD,
                installiert=installiert(code), groesse=groesse(code) if code != STANDARD else 0,
                platz=platz(code) if code != STANDARD else 0,
                schrift_name=(SCHRIFTEN.get(code) or {}).get("name") or "Poppins",
                deepl=bool(s["dienste"]["deepl"]), mymemory=bool(s["dienste"]["mymemory"]))


def liste(sprache="en"):
    return [info(c, sprache) for c in SPRACHEN]


# =============================================================================================
# Laden und Entfernen
# =============================================================================================
def _sha256(pfad):
    h = hashlib.sha256()
    with open(pfad, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _hole(d, ziel, melde, quelle=None, fortschritt=None):
    """Eine Datei laden (fortsetzbar über .part + Range), Größe und SHA-256 prüfen, dann umbenennen."""
    if _groesse(ziel) == d["groesse"] and _sha256(ziel) == d["sha256"]:
        fortschritt(d["groesse"])
        return
    part = ziel.with_name(ziel.name + ".part")
    if quelle:                                             # Selbsttest / Offline: Datei aus einem Ordner nehmen
        shutil.copyfile(Path(quelle) / d["name"], part)
        fortschritt(_groesse(part))
    else:
        schon = _groesse(part) if _groesse(part) < d["groesse"] else 0
        kopf = {"User-Agent": "Me-Goos-ta-Deutsch"}
        if schon:
            kopf["Range"] = f"bytes={schon}-"
        import ki_modelle
        with ki_modelle.oeffne_url(urllib.request.Request(d["url"], headers=kopf)) as r:
            if schon and getattr(r, "status", 200) != 206:     # Server kann nicht fortsetzen → von vorn
                schon = 0
            with open(part, "ab" if schon else "wb") as f:
                fortschritt(schon)
                geladen = schon
                while True:
                    block = r.read(1 << 18)
                    if not block:
                        break
                    geladen += len(block)
                    if geladen > d["groesse"]:
                        raise SprachFehler("pruefsumme", name=d["name"])
                    f.write(block)
                    fortschritt(len(block))
    if _groesse(part) != d["groesse"] or _sha256(part) != d["sha256"]:
        part.unlink(missing_ok=True)
        raise SprachFehler("pruefsumme", name=d["name"])
    os.replace(part, ziel)


def installiere_paket(paket, melde=print):
    """pip install --target Daten/sprachen/_pakete (nur Binär-Räder, feste Fassung, ohne Abhängigkeiten)."""
    p = PAKETE[paket]
    ziel = pakete_ordner()
    ziel.mkdir(parents=True, exist_ok=True)
    befehl = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "--no-input", "--no-deps",
              "--only-binary=:all:", "--upgrade", "--target", str(ziel), f"{paket}=={p['version']}"]
    r = subprocess.run(befehl, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    if r.returncode != 0 or not _paket_da(paket):
        grund = (r.stderr or r.stdout or "").strip().splitlines()[-1:] or ["?"]
        raise SprachFehler("pip", paket=paket, grund=grund[0][:200])


def lade(code, melde=print, quelle=None, pip=True):
    """Installiert ein Sprachpaket: Schriften laden + prüfen, nötige pip-Pakete, dann paket.json. Gibt den Ordner
    zurück. quelle: Ordner mit den Dateien statt Download (Selbsttest). pip=False: Pakete nicht installieren."""
    _pruefe(code)
    if code == STANDARD:
        return paket_ordner(code)
    o = paket_ordner(code)
    o.mkdir(parents=True, exist_ok=True)
    noetig = sum(d["groesse"] - _groesse(o / d["name"]) for d in dateien(code) if _groesse(o / d["name"]) != d["groesse"])
    if pip:
        noetig += sum(PAKETE[p]["platz"] for p in noetige_pakete(code) if not _paket_da(p))
    try:
        frei = shutil.disk_usage(o).free
    except OSError:
        frei = None
    if frei is not None and noetig and frei < noetig + 20 * MB:
        raise SprachFehler("platz", mb=max(1, round((noetig + 20 * MB - frei) / MB)))
    gesamt = max(1, sum(d["groesse"] for d in dateien(code)))
    stand = {"bytes": 0, "schritt": -1}

    def fortschritt(n):
        stand["bytes"] += n
        schritt = min(9, stand["bytes"] * 10 // gesamt)
        if schritt > stand["schritt"]:
            stand["schritt"] = schritt
            melde(f"  {schritt * 10} %  ({stand['bytes'] / MB:.1f} / {gesamt / MB:.1f} MB)")
    if dateien(code):
        melde(uebersetzer_text(L(f"Lade die Schrift {SCHRIFTEN[code]['name']} …", f"Downloading the font "
                                 f"{SCHRIFTEN[code]['name']} …", f"Descargando la fuente {SCHRIFTEN[code]['name']} …")))
    for d in dateien(code):
        _hole(d, o / d["name"], melde, quelle, fortschritt)
    if pip:
        for p in noetige_pakete(code):
            if not _paket_da(p):
                melde(uebersetzer_text(L(f"Installiere das Zusatzpaket {p} …", f"Installing the add-on package {p} …",
                                         f"Instalando el paquete adicional {p} …")))
                installiere_paket(p, melde)
    uebersetzer._schreibe_privat(o / "paket.json", dict(code=code, zeit=time.strftime("%Y-%m-%d %H:%M:%S"),
                                                         dateien=[d["name"] for d in dateien(code)],
                                                         pakete=list(SPRACHEN[code]["pakete"])))
    melde(uebersetzer_text(L(f"Fertig: {name(code, 'de')} ist bereit.", f"Done: {name(code, 'en')} is ready.",
                             f"Listo: {name(code, 'es')} está listo.")))
    return o


def uebersetzer_text(t):
    s = (os.environ.get("MGD_SPRACHE") or "en")[:2].lower()
    return t.get(s) or t["en"]


def _sicher_eigen(pfad):
    try:
        return pfad.resolve().is_relative_to(uebersetzer.daten_ordner().resolve()) and not pfad.is_symlink()
    except OSError:
        return False


def entferne(code=None):
    """Löscht nur die bekannten Dateien eines Sprachpakets (ohne Code: aller Pakete). Kartentexte in karten.csv
    bleiben. Braucht keine installierte Sprache mehr uharfbuzz, geht auch Daten/sprachen/_pakete. → [gelöschte Pfade]"""
    if code is not None:
        _pruefe(code)
        if code == STANDARD:
            raise SprachFehler("standard")
    weg = []
    for c in ([code] if code else [c for c in SPRACHEN if c != STANDARD]):
        o = paket_ordner(c)
        for n in _eigene_namen(c):
            datei = o / n
            if datei.is_file() and not datei.is_symlink():
                datei.unlink()
                weg.append(datei)
        try:
            o.rmdir()                                      # nur, wenn jetzt leer (nie rekursiv)
        except OSError:
            pass
    weg += pakete_aufraeumen()
    return weg


def pakete_aufraeumen():
    """Entfernt Daten/sprachen/_pakete, wenn keine installierte Sprache uharfbuzz mehr braucht (auch beim Start der
    Oberfläche: unter Windows kann das Paket beim Entfernen noch von einer Vorschau belegt gewesen sein)."""
    weg = []
    if not any(braucht_formen(c) for c in weitere_installiert()) and pakete_ordner().is_dir() \
            and _sicher_eigen(pakete_ordner()):
        try:
            shutil.rmtree(pakete_ordner())
            weg.append(pakete_ordner())
        except OSError:                                    # unter Windows evtl. von einem laufenden Druck belegt
            pass
    try:
        ordner().rmdir()
    except OSError:
        pass
    return weg


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Sprachen der Kartenrückseite für Me Goos-ta Deutsch")
    ap.add_argument("--laden", choices=[c for c in SPRACHEN if c != STANDARD], help="Sprachpaket installieren")
    ap.add_argument("--entfernen", choices=[c for c in SPRACHEN if c != STANDARD], help="Sprachpaket entfernen")
    ap.add_argument("--aus-ordner", metavar="ORDNER", help="Dateien aus diesem Ordner statt Download (Test)")
    a = ap.parse_args(argv)
    for strom in (sys.stdout, sys.stderr):
        try:
            strom.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    try:
        if a.laden:
            lade(a.laden, melde=lambda t: print(t, flush=True),
                 quelle=a.aus_ordner or os.environ.get("MGD_SPRACHEN_QUELLE") or None)
            return 0
        if a.entfernen:
            print(len(entferne(a.entfernen)), "Dateien entfernt")
            return 0
    except SprachFehler as e:
        print(uebersetzer_text(L("FEHLER: ", "ERROR: ", "ERROR: ")) + fehler_text(e, uebersetzer_text(
            {"de": "de", "en": "en", "es": "es"})), flush=True)
        return 1
    except Exception as e:  # noqa: BLE001
        print(uebersetzer_text(L("FEHLER: ", "ERROR: ", "ERROR: ")) + str(e), flush=True)
        return 1
    for e in liste("de"):
        print(f"{'✓' if e['installiert'] else '·'} {e['code']:4} {e['name']:14} {e['eigenname']:16} "
              f"{e['schrift_name']:22} {e['groesse'] / MB:5.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
