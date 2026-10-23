#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ME GOOS-TA DEUTSCH – Kartengenerator                                Version 2.4 (22.10.2026)
=============================================================================================
Erzeugt aus Bildern (Vorderseite) und karten.csv (Rückseite: Spanisch) druckfertige Lernkarten.

Ausgaben (Ordner ausgabe/):
  Me-Goos-ta-Deutsch_Druckerei_<Format>.pdf    eine Seite je Kartenseite, Endformat + Beschnitt, abwechselnd V/R
  Me-Goos-ta-Deutsch_Heimdruck_A4_<Format>.pdf A4-Bögen, beidseitig, Schnittmarken, Rückseiten seitenrichtig
  Me-Goos-ta-Deutsch_Pruefbogen.pdf            Kontrolle vor dem Druck: Vorder-/Rückseite, Texte, Bildqualität
  einzelbilder/                                PNG je Kartenseite (300 dpi) für Dienste mit Bild-Upload
Vorlagen (Ordner vorlagen/): leere Hilfsvorlagen mit Beschnitt-, Rand- und Sicherheitslinien.

Kartenaufbau (verbindlich):
  Vorderseite = das Bild (Dateiname = Text auf dem Bild, z. B. gans-alt.jpg) – automatisch verbessert
  Rückseite   = das Wort auf Spanisch (gemeint ist das in Mexiko gesprochene Spanisch) mit einer frechen Gans in der Ecke

Bildverbesserung (--qualitaet, Standard „standard“; --ki, Standard „auto“):
  1. schwarze Sticker-/Screenshot-Ränder entfernen
  2. KI-Vergrößerung mit Real-ESRGAN x4plus (entfernt dabei JPEG-Blöcke und Rauschen; reines NumPy, ki_modelle.py)
     – ohne dieses Modell: Guided-Filter + FSRCNN, sonst Lanczos
  3. auf Druckgröße bringen, leicht nachschärfen, Tonwerte und Farben behutsam korrigieren

Oberfläche:     Doppelklick auf „Me Goos-ta Deutsch - Windows.cmd“ / „… - Mac.command“ oder python3 gans_ui.py
Schnellstart:   python3 gans_lernkarten.py            (Windows: py gans_lernkarten.py)
Alle Optionen:  python3 gans_lernkarten.py --help
Sprache der Meldungen: Umgebungsvariable MGD_SPRACHE=de|en|es (die Oberfläche setzt sie automatisch)
Benötigt:       Python 3.9+, reportlab, pillow, numpy   (optional: pypdfium2 für Vorschau und Einzelbilder)
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from reportlab import rl_config
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas

VERSION = "2.4 (22.10.2026)"
BILD_VERSION = "2.0"                 # ändert sich nur, wenn die Bildaufbereitung anders rechnet (Cache-Schlüssel)
PRODUKT = "Me Goos-ta Deutsch"
DATEI_PRAEFIX = "Me-Goos-ta-Deutsch"
HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
Image.MAX_IMAGE_PIXELS = 80_000_000   # Schutz vor „Dekompressionsbomben“ (riesige Bilder mit kleiner Dateigröße)
A4_B, A4_H = 210.0, 297.0            # mm
# Papier für Heimdruck und Prüfbogen: A4 (fast überall) oder US-Letter (USA, Kanada, Mexiko, Teile Lateinamerikas)
PAPIER = {"a4": (210.0, 297.0, "A4"), "letter": (215.9, 279.4, "Letter")}
RES = Image.Resampling.LANCZOS
BILD_ENDUNGEN = (".jpg", ".jpeg", ".png", ".webp")
SPRACHEN = ("de", "en", "es")
KARTEN_SPALTEN = ["bild", "de", "es", "notiz", "fit", "uebersetzung"]     # bekannte Spalten in karten.csv
UEBERSETZUNG_WERT = {"auto": "automatisch", "geprueft": "geprüft"}           # Spalte „uebersetzung“ in karten.csv
rl_config.useA85 = 0                 # Bilder binär einbetten: kleinere PDFs, deutlich schneller

# Farben – alle deckend (keine Transparenz), damit Druckereien nichts verflachen müssen
PAL = dict(
    bg="#BFDDF2", bg_licht="#D6EBF9", bg_dunkel="#A6CCE8",
    text="#1B2D4F", text2="#3F5C88",
    gans="#FFFFFF", gans_schatten="#E1EBF5", wange="#F9CDBE",
    orange="#F6A94B", orange_dunkel="#DE8A2B", auge="#1F2C48",
    rot="#E5484D", blau="#2F6FDE", gruen="#1E9E5A", grau="#7C828C", hellrot="#FCE4E4",
)

# Qualitätsstufen der Bildverbesserung (radius/eps/nachglaetten/schaerfe gelten für den Weg ohne Real-ESRGAN)
QUALITAET = {
    "aus":      None,
    "standard": dict(radius=2, eps=0.03 ** 2, nachglaetten=False, schaerfe=60, kontrast=0.3, farbe=1.06, schaerfe_ki=35),
    "stark":    dict(radius=3, eps=0.05 ** 2, nachglaetten=True, schaerfe=80, kontrast=0.4, farbe=1.08, schaerfe_ki=60),
}
# KI-Vergrößerung: Auswahl → Modell in modelle/ (siehe ki_modelle.py)
KI_AUSWAHL = ["auto", "realesrgan", "realesrgan-x2", "fsrcnn", "aus"]
KI_MODELLE = {"realesrgan": "realesrgan-x4plus", "realesrgan-x2": "realesrgan-x2plus"}


@dataclass
class Konfig:
    b: float = 88.0               # Endformat Breite (mm, intern immer Querformat)
    h: float = 63.0               # Endformat Höhe (mm)
    beschnitt: float = 3.0
    rand: float = 3.5             # weißer Kartenrand
    radius: float = 2.5           # Eckenradius der Gestaltungsfläche
    dpi: int = 300
    qualitaet: str = "standard"
    ki: str = "auto"
    hochkant: bool = False
    rs_drehen: bool = False
    gans_bild: str | None = None
    abstand: float = 0.0
    spalten: int = 0
    zeilen: int = 0
    versatz_x: float = 0.0
    versatz_y: float = 0.0
    papier: str = "a4"            # Heimdruck und Prüfbogen: a4 | letter
    sprache: str = "es"           # Sprache der Rückseite (Spalte in karten.csv, Schrift, Dateinamen)
    sprachkuerzel: str = "auto"   # Sprachkürzel auf der Rückseite: auto (nur bei ≠ es) | an | aus

    @property
    def kuerzel(self):
        return f"{self.b:g}x{self.h:g}"

    @property
    def flaeche_px(self):
        """Pixelmaße der Gestaltungsfläche (Endformat minus weißer Rand) bei cfg.dpi."""
        return (round((self.b - 2 * self.rand) / 25.4 * self.dpi),
                round((self.h - 2 * self.rand) / 25.4 * self.dpi))


def farbe(c, hexwert, stroke=False):
    (c.setStrokeColor if stroke else c.setFillColor)(HexColor(hexwert))


def zahl(v):
    """Zahl mit deutschem Komma, ohne überflüssige Nachkommastellen."""
    return f"{v:g}".replace(".", ",")


# =============================================================================================
# Sprache der Meldungen (Druckdateien bleiben immer gleich – nur Texte für Bildschirm und Protokoll)
# =============================================================================================
_LOKAL = threading.local()


def setze_sprache(s):
    """Sprache für den aktuellen Thread festlegen (die Oberfläche bedient mehrere Anfragen gleichzeitig)."""
    _LOKAL.sprache = s if s in SPRACHEN else None


def sprache():
    s = getattr(_LOKAL, "sprache", None) or (os.environ.get("MGD_SPRACHE") or "en")[:2].lower()
    return s if s in SPRACHEN else "en"


def T(de, en=None, es=None):
    """Text in der eingestellten Sprache: T("Hallo", "Hello", "Hola")."""
    return {"en": en, "es": es}.get(sprache()) or de


def L(de, en, es):
    """Beschriftung in allen drei Sprachen (für die Oberfläche)."""
    return {"de": de, "en": en, "es": es}


def text_in(wert, s=None):
    """Wählt aus einem L(...)-Wörterbuch die Sprache s (Standard: eingestellte Sprache)."""
    if isinstance(wert, dict):
        return wert.get(s or sprache()) or wert.get("en") or wert.get("de") or ""
    return wert or ""


def zielsprache():
    """Sprache der Kartenrückseite (Tool „Sprachen“, sprachen.py) – ohne sprachen.py immer es."""
    try:
        import sprachen
        return sprachen.zielsprache()
    except Exception:  # noqa: BLE001
        return "es"


def zs_name(s=None, code=None):
    """Name der Kartensprache in der Sprache der Oberfläche („Spanisch“ / „Spanish“ / „español“)."""
    try:
        import sprachen
        return sprachen.name(code or zielsprache(), s or sprache())
    except Exception:  # noqa: BLE001
        return text_in(L("Spanisch", "Spanish", "español"), s)


def mit_zs(vorlage, werte):
    """format() mit {zs} = Name der Kartensprache (nur ausgerechnet, wenn die Vorlage ihn braucht)."""
    if "{zs}" in vorlage and "zs" not in werte:
        werte = dict(werte, zs=zs_name())
    return vorlage.format(**werte)


# =============================================================================================
# Schriften
# =============================================================================================
FONT_KANDIDATEN = {
    "bold": ["schrift/Poppins-Bold.ttf",
             "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
             "C:/Windows/Fonts/arialbd.ttf",
             "/Library/Fonts/Arial Bold.ttf",
             "/System/Library/Fonts/Supplemental/Arial Bold.ttf"],
    "medium": ["schrift/Poppins-Medium.ttf",
               "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf",
               "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
               "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
               "C:/Windows/Fonts/arial.ttf",
               "/Library/Fonts/Arial.ttf",
               "/System/Library/Fonts/Supplemental/Arial.ttf"],
}
F_BOLD, F_MED = "Helvetica-Bold", "Helvetica"       # werden von registriere_schriften() gesetzt


def registriere_schriften():
    """Registriert Poppins (falls vorhanden), sonst DejaVu/Liberation/Arial; Schriften werden eingebettet."""
    global F_BOLD, F_MED
    namen = {}
    for art, pfade in FONT_KANDIDATEN.items():
        for p in pfade:
            pp = Path(p) if Path(p).is_absolute() else HIER / p
            if pp.exists():
                try:
                    pdfmetrics.registerFont(_ttf(f"GL-{art}", pp))
                    namen[art] = (f"GL-{art}", pp.stem)
                    break
                except Exception:
                    continue
        else:
            namen[art] = ("Helvetica-Bold" if art == "bold" else "Helvetica", "Helvetica (nicht eingebettet)")
    F_BOLD, F_MED = namen["bold"][0], namen["medium"][0]
    return {k: v[1] for k, v in namen.items()}


def _ttf(name, pfad, formen=False):
    """TrueType-Schrift; formen=True nur für Sprachen mit Silben-/Verbindungsformen (hi, ar) – alle anderen bleiben
    ungeformt, damit sich der Druck für Spanisch & Co. nie ändert (auch nicht, wenn uharfbuzz geladen ist)."""
    try:
        return TTFont(name, str(pfad), shapable=formen)
    except TypeError:                                          # ältere ReportLab-Fassung ohne Formen
        return TTFont(name, str(pfad))


# ---------------------------------------------------------------------------------------------
# Schriftsatz der Rückseite je Sprache (G09): Schrift aus dem Sprachpaket, Formen (hi, ar), rechts-nach-links (ar),
# Umbruch zwischen Zeichen (ja, zh). Spanisch und alle Poppins-Sprachen ohne Formen laufen exakt wie bisher.
# ---------------------------------------------------------------------------------------------
_HB = {"modul": None, "versucht": False}
_SATZ = {}
_SATZ_LOCK = threading.Lock()
_ARABISCH = re.compile(r"[֐-ࣿיִ-﷿ﹰ-﻿]")
_KEIN_ZEILENANFANG = set("、。，．・：；？！ー」』）〕］｝〉》】〙〗〟’”ゝゞヽヾ々ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮヵヶ!),.:;?]}%")
_KEIN_ZEILENENDE = set("「『（〔［｛〈《【〘〖〝‘“([{")


def _harfbuzz():
    """uharfbuzz aus Daten/sprachen/_pakete (nur bei Bedarf) – None, wenn nicht ladbar."""
    if not _HB["versucht"]:
        _HB["versucht"] = True
        try:
            import sprachen
            if sprachen.aktiviere_pakete():
                import uharfbuzz
                from reportlab.pdfbase import ttfonts
                ttfonts.uharfbuzz = uharfbuzz             # ReportLab formt damit gezeichnete ShapedStr
                _HB["modul"] = uharfbuzz
        except Exception:  # noqa: BLE001 – fehlt oder DLL gesperrt → ungeformt
            _HB["modul"] = None
    return _HB["modul"]


class Satz:
    """Schriften + Regeln der Rückseite für eine Sprache. voll=False: die Schrift der Sprache ist (noch) nicht da –
    dann prüft pruefe_karte Zeichen und Platz nicht (gedruckt wird mit Poppins)."""

    def __init__(self, code):
        self.code = code if code else "es"
        try:
            import sprachen
            info = sprachen.SPRACHEN.get(self.code) or sprachen.SPRACHEN["es"]
            dateien = sprachen.schriften(self.code)
            formen = sprachen.braucht_formen(self.code)
            braucht_paket = bool(sprachen.dateien(self.code))
        except Exception:  # noqa: BLE001 – ohne sprachen.py: Spanisch
            info, dateien, formen, braucht_paket = {"richtung": "ltr", "umbruch": "wort"}, None, False, False
        self.rtl = info.get("richtung") == "rtl"
        self.zeichenweise = info.get("umbruch") == "zeichen"
        self.voll = not braucht_paket or bool(dateien)
        self.braucht_formen = formen
        self.hb = _harfbuzz() if formen else None
        self.fett, self.normal = F_BOLD, F_MED
        quelle = {}
        if dateien:
            quelle = {"bold": dateien.get("bold") or dateien.get("regular"),
                      "regular": dateien.get("regular") or dateien.get("bold")}
        elif self.hb:                                          # Hindi: Poppins, aber geformt
            quelle = {art: (Path(p) if Path(p).is_absolute() else HIER / p)
                      for art, p in (("bold", FONT_KANDIDATEN["bold"][0]), ("regular", "schrift/Poppins-Regular.ttf"))}
        for art, p in quelle.items():
            if p and Path(p).is_file():
                name = f"GL-{self.code}-{art}"
                try:
                    pdfmetrics.getFont(name)
                except KeyError:
                    pdfmetrics.registerFont(_ttf(name, p, formen=bool(self.hb)))
                if art == "bold":
                    self.fett = name
                else:
                    self.normal = name

    # --- Formen ---------------------------------------------------------------------------------
    def _forme_lauf(self, text, font, groesse):
        from reportlab.pdfbase.ttfonts import ShapedStr, ShapeData
        hb, ttf = self.hb, pdfmetrics.getFont(font)
        hbf = ttf.hbFont(groesse)
        buf = hb.Buffer()
        buf.cluster_level = hb.BufferClusterLevel.MONOTONE_CHARACTERS
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(hbf, buf, {"kern": True, "liga": True})
        zeichen, daten = "", []
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            gid = info.codepoint
            try:
                u = ttf.face.glyphToChar[gid][0]
            except (KeyError, IndexError):
                u = ttf.hbAddPrivate(hbf.glyph_to_string(gid), gid, pos.x_advance)
            zeichen += chr(u)
            daten.append(ShapeData(info.cluster, ttf.pdfScale(pos.x_advance), ttf.pdfScale(pos.y_advance),
                                   ttf.pdfScale(pos.x_offset), ttf.pdfScale(pos.y_offset), ttf.face.charWidths.get(u, 0)))
        return ShapedStr(zeichen, shapeData=daten)

    def laeufe(self, text):
        """Text in Zeichenreihenfolge der Anzeige: bei rechts-nach-links die Wörter umgedreht, Ziffern und lateinische
        Wörter (samt Leerzeichen dazwischen) als eigener Lauf von links nach rechts."""
        if not self.rtl:
            return [text]
        teile = re.findall(r" +|[^ ]+", text)
        laeufe = []
        for t in teile:
            ltr = not t.isspace() and not _ARABISCH.search(t)
            if ltr and laeufe and laeufe[-1][0] == "l":
                laeufe[-1][1] += t
            elif ltr and len(laeufe) >= 2 and laeufe[-1][1].isspace() and laeufe[-2][0] == "l":
                leer = laeufe.pop()[1]
                laeufe[-1][1] += leer + t
            else:
                laeufe.append(["l" if ltr else "r", t])
        return [t for _, t in reversed(laeufe)]

    def geformt(self, text, font, groesse):
        """(Zeichenkette zum Zeichnen, Breite in pt)."""
        if not self.hb and not self.rtl:
            return text, pdfmetrics.stringWidth(text, font, groesse)
        if not self.hb:                                        # ohne uharfbuzz: wenigstens die Wortfolge richtig
            t = "".join(self.laeufe(text))
            return t, pdfmetrics.stringWidth(t, font, groesse)
        stuecke = [self._forme_lauf(t, font, groesse) for t in self.laeufe(text) if t]
        if not stuecke:
            return text, 0.0
        aus = stuecke[0]
        for s in stuecke[1:]:
            aus = aus + s
        return aus, sum(d.x_advance for d in aus.__shapeData__) * groesse / 1000

    def breite(self, text, font, groesse):
        return self.geformt(text, font, groesse)[1]

    def zeichne_mitte(self, c, cx, y, text, font, groesse):
        """Zentriert zeichnen (die Schrift hat der Aufrufer mit c.setFont gesetzt)."""
        t, w = self.geformt(text, font, groesse)
        if not hasattr(t, "__shapeData__"):
            c.drawCentredString(cx, y, t)
            return
        to = c.beginText(cx - w / 2, y)
        to.setFont(font, groesse)
        to.textOut(t)
        c.drawText(to)

    def fehlende_zeichen(self, text):
        try:
            vorhanden = pdfmetrics.getFont(self.fett).face.charToGlyph
        except Exception:  # noqa: BLE001
            return []
        unsichtbar = {0x200C, 0x200D, 0x200E, 0x200F, 0x061C}  # Steuerzeichen (ZWJ/ZWNJ, Richtungsmarken)
        return sorted({z for z in text if z not in " |/" and ord(z) not in vorhanden and ord(z) not in unsichtbar})

    def zwei_zeilen(self, text, groesse):
        """Teilt an der Stelle, die die längere Zeile am kürzesten macht: an Leerzeichen, bei ja/zh auch zwischen
        Zeichen (nie Satzzeichen an den Zeilenanfang bzw. öffnende Klammern ans Zeilenende)."""
        worte = text.split(" ")
        if len(worte) >= 2:
            kandidaten = [[" ".join(worte[:i]), " ".join(worte[i:])] for i in range(1, len(worte))]
        elif self.zeichenweise and len(text) >= 2:
            kandidaten = [[text[:i], text[i:]] for i in range(1, len(text))
                          if text[i] not in _KEIN_ZEILENANFANG and text[i - 1] not in _KEIN_ZEILENENDE]
        else:
            kandidaten = []
        if not kandidaten:
            return [text]
        breiten = [max(self.breite(z, self.fett, groesse) for z in zz) for zz in kandidaten]
        beste = min(range(len(kandidaten)), key=breiten.__getitem__)
        if self.zeichenweise and len(worte) < 2:              # ja/zh: lieber nach einem Satzzeichen (、。) umbrechen
            nach_zeichen = [i for i, zz in enumerate(kandidaten) if zz[0][-1] in "、，。・；：！？"
                            and breiten[i] <= breiten[beste] * 1.3]
            if nach_zeichen:
                beste = min(nach_zeichen, key=breiten.__getitem__)
        return kandidaten[beste]


def satz(code="es"):
    """Schriftsatz für die Sprache (je Prozess zwischengespeichert; neu, wenn sich die Schriftdateien ändern)."""
    try:
        import sprachen
        stempel = tuple(str(p) for p in (sprachen.schriften(code) or {}).values())
    except Exception:  # noqa: BLE001
        stempel = ()
    schluessel = (code or "es", stempel, F_BOLD, F_MED)
    with _SATZ_LOCK:
        if schluessel not in _SATZ:
            _SATZ[schluessel] = Satz(code)
        return _SATZ[schluessel]


# =============================================================================================
# Bildverbesserung
# =============================================================================================
def beschneide_schwarz(im, schwelle=12, anteil=0.55):
    """Schneidet schwarze Balken (Sticker-/Screenshot-Ränder) rundum ab. Eine Zeile/Spalte gilt als Balken,
    wenn mindestens 'anteil' ihrer Pixel fast reines Schwarz sind – dunkle Bildinhalte bleiben erhalten."""
    mx = np.asarray(im.convert("RGB")).max(axis=2)
    dunkel_z = (mx <= schwelle).mean(axis=1) >= anteil        # je Zeile
    dunkel_s = (mx <= schwelle).mean(axis=0) >= anteil        # je Spalte

    def lauf(flags):
        n = np.argmin(flags) if not flags.all() else len(flags)
        return int(n)

    o, u = lauf(dunkel_z), lauf(dunkel_z[::-1])
    l, r = lauf(dunkel_s), lauf(dunkel_s[::-1])
    h, w = mx.shape
    if o + u >= h - 4 or l + r >= w - 4:
        return im
    pad = lambda n: n + 2 if n else 0                         # 2 px Sicherheit gegen JPEG-Fransen
    o, u, l, r = map(pad, (o, u, l, r))
    return im.crop((l, o, w - r, h - u))


def _box(a, r):
    """Mittelwertfilter (2r+1)² über die ersten beiden Achsen – Integralbild, Laufzeit unabhängig von r."""
    pad = ((r + 1, r), (r + 1, r)) + ((0, 0),) * (a.ndim - 2)
    c = np.pad(a.astype(np.float64), pad, mode="edge").cumsum(0).cumsum(1)    # float64: genau auch bei großen Bildern
    k = 2 * r + 1
    return ((c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / float(k * k)).astype(np.float32)


def kantenschonend_glaetten(im, radius=2, eps=0.03 ** 2):
    """Guided-Filter (He et al.), selbstgeführt je Farbkanal: glättet JPEG-Blöcke und Rauschen in ruhigen
    Flächen, lässt starke Kanten (Konturen, Schrift) stehen."""
    p = np.asarray(im, np.float32) / 255.0
    m = _box(p, radius)
    var = np.maximum(_box(p * p, radius) - m * m, 0.0)
    a = var / (var + eps)
    b = m - a * m
    out = _box(a, radius) * p + _box(b, radius)
    return Image.fromarray(np.clip(out * 255.0 + 0.5, 0, 255).astype(np.uint8))


class FSRCNN:
    """KI-Hochskalierung (FSRCNN, Dong et al. 2016; Gewichte: Saafke/FSRCNN_Tensorflow, Apache-2.0).
    Läuft in reinem NumPy auf dem Helligkeitskanal; Farbe wird bikubisch ergänzt."""
    _cache = {}

    @classmethod
    def verfuegbar(cls, faktor):
        return (HIER / "modelle" / f"fsrcnn_x{faktor}.npz").exists()

    @classmethod
    def _gewichte(cls, faktor):
        if faktor not in cls._cache:
            with np.load(HIER / "modelle" / f"fsrcnn_x{faktor}.npz") as z:
                cls._cache[faktor] = {k: z[k].astype(np.float32) for k in z.files}
        return cls._cache[faktor]

    @staticmethod
    def _conv(x, f, b):
        """2D-Faltung wie TensorFlow (Korrelation, padding SAME); x: H×W×C, f: kh×kw×C×K."""
        kh, kw, ci, co = f.shape
        h, w = x.shape[:2]
        if kh == 1:
            return (x.reshape(-1, ci) @ f.reshape(ci, co) + b).reshape(h, w, co)
        xp = np.pad(x, ((kh // 2, kh // 2), (kw // 2, kw // 2), (0, 0)))
        fenster = np.lib.stride_tricks.sliding_window_view(xp, (kh, kw), axis=(0, 1))    # H,W,C,kh,kw
        spalten = fenster.transpose(0, 1, 3, 4, 2).reshape(h * w, kh * kw * ci)
        return (spalten @ f.reshape(kh * kw * ci, co) + b).reshape(h, w, co)

    @classmethod
    def _netz(cls, y, faktor):
        w = cls._gewichte(faktor)
        prelu = lambda x, i, k: np.maximum(x, 0) + w[f"alpha{i}"] * (x - np.abs(x)) * w[f"mul_{k}_y"]
        x = y[:, :, None]
        for i, k in zip(range(1, 8), (1, 3, 5, 7, 9, 11, 13)):
            x = prelu(cls._conv(x, w[f"f{i}"], w[f"b{i}"]), i, k)
        x = cls._conv(x, w["f8"], np.zeros(w["f8"].shape[-1], np.float32))
        h, ww = x.shape[:2]
        x = x.reshape(h, ww, faktor, faktor).transpose(0, 2, 1, 3).reshape(h * faktor, ww * faktor)  # DepthToSpace
        return x + w["b8"][0]

    @classmethod
    def hochskalieren(cls, im, faktor):
        Y, Cb, Cr = im.convert("YCbCr").split()
        y = cls._netz(np.asarray(Y, np.float32) / 255.0, faktor)
        Yh = Image.fromarray(np.clip(y * 255.0 + 0.5, 0, 255).astype(np.uint8))
        groesse = Yh.size
        return Image.merge("YCbCr", (Yh, Cb.resize(groesse, Image.Resampling.BICUBIC),
                                     Cr.resize(groesse, Image.Resampling.BICUBIC))).convert("RGB")


def ki_methode(ki):
    """Welche Vergrößerung wird tatsächlich benutzt? 'realesrgan-x4plus' | 'realesrgan-x2plus' | 'fsrcnn' | 'lanczos'.
    'auto' nimmt das beste vorhandene Modell; fehlt ein gewähltes Modell, wird ebenfalls das beste vorhandene genutzt."""
    import ki_modelle
    if ki in (False, None, "aus"):
        return "lanczos"
    if ki in KI_MODELLE and ki_modelle.verfuegbar(KI_MODELLE[ki]):
        return KI_MODELLE[ki]
    if ki in ("auto", True) or ki in KI_MODELLE:
        for m in ("realesrgan-x4plus", "realesrgan-x2plus"):
            if ki_modelle.verfuegbar(m):
                return m
    return "fsrcnn" if FSRCNN.verfuegbar(2) else "lanczos"


METHODE_NAME = {"realesrgan-x4plus": "Real-ESRGAN x4plus", "realesrgan-x2plus": "Real-ESRGAN x2plus",
                "fsrcnn": "FSRCNN", "lanczos": "Lanczos"}


def skalieren(im, ziel, methode="fsrcnn", fortschritt=None):
    """Skaliert auf 'ziel' (w, h). Beim Vergrößern um mehr als 5 % mit dem KI-Modell, Rest per Lanczos.
    Gibt (Bild, Beschreibung, benutzte Methode) zurück."""
    s = max(ziel[0] / im.width, ziel[1] / im.height)
    if s <= 1.05 or methode == "lanczos":
        art = "Lanczos" if s > 1.05 else "verkleinert" if s < 0.95 else "1:1"
        return im.resize(ziel, RES), art, ("lanczos" if s > 1.05 else "keine")
    if methode.startswith("realesrgan"):
        import ki_modelle
        hs = ki_modelle.Hochskalierer(methode)
        gross = hs(im, fortschritt)
        return gross.resize(ziel, RES), f"{METHODE_NAME[methode]} ×{hs.faktor}", methode
    faktor = 2 if s <= 2.05 else 3 if s <= 3.05 else 4
    if not FSRCNN.verfuegbar(faktor):
        return im.resize(ziel, RES), "Lanczos (kein KI-Modell)", "lanczos"
    gross = FSRCNN.hochskalieren(im, faktor)
    if s > faktor:                                       # noch größer als ×4: Rest per Lanczos
        return gross.resize(ziel, RES), f"FSRCNN ×{faktor} + Lanczos", "fsrcnn"
    return gross.resize(ziel, RES), f"FSRCNN ×{faktor}", "fsrcnn"


def verbessere(im, ziel, cfg, fortschritt=None):
    """Bringt 'im' auf Größe 'ziel' und verbessert es gemäß cfg.qualitaet/cfg.ki.
    Gibt (Bild, Beschreibung, benutzte Methode) zurück."""
    stufe = QUALITAET.get(cfg.qualitaet)
    if stufe is None:
        return im.resize(ziel, RES), "unverändert (Lanczos)", "lanczos"
    s = max(ziel[0] / im.width, ziel[1] / im.height)
    methode = ki_methode(cfg.ki)
    if methode.startswith("realesrgan") and s > 1.05:
        # Real-ESRGAN entfernt JPEG-Blöcke und Rauschen selbst – vorheriges Glätten würde nur Details kosten
        bild, art, benutzt = skalieren(im, ziel, methode, fortschritt)
        bild = bild.filter(ImageFilter.UnsharpMask(radius=1.0, percent=stufe["schaerfe_ki"], threshold=2))
        beschreibung = f"{art} · nachgeschärft"
    else:
        bild = kantenschonend_glaetten(im, stufe["radius"], stufe["eps"])
        if stufe["nachglaetten"]:
            bild = kantenschonend_glaetten(bild, 2, 0.03 ** 2)
        bild, art, benutzt = skalieren(bild, ziel, "lanczos" if methode.startswith("realesrgan") else methode)
        bild = bild.filter(ImageFilter.UnsharpMask(radius=max(0.8, 0.8 * s), percent=stufe["schaerfe"], threshold=3))
        beschreibung = f"entrauscht · {art} · geschärft"
    bild = ImageOps.autocontrast(bild, cutoff=stufe["kontrast"])
    bild = ImageEnhance.Color(bild).enhance(stufe["farbe"])
    return bild, beschreibung, benutzt


def deckend(im, tw, th, fokus=(0.5, 0.5)):
    """Skaliert so, dass die Zielfläche komplett gefüllt ist; Überstand wird abgeschnitten."""
    s = max(tw / im.width, th / im.height)
    nw, nh = math.ceil(im.width * s), math.ceil(im.height * s)
    left, top = int((nw - tw) * fokus[0]), int((nh - th) * fokus[1])
    return im.resize((nw, nh), RES).crop((left, top, left + tw, top + th))


def bewertung_ppi(ppi):
    """Code und deutscher Text (für den Prüfbogen) zur Druckauflösung."""
    if ppi >= 250:
        return "sehr_gut", "sehr gut"
    if ppi >= 180:
        return "gut", "gut"
    if ppi >= 120:
        return "ausreichend", "ausreichend"
    return "gering", "gering – bessere Bildquelle empfohlen"


def oeffne_bild(pfad, drehung=0):
    """Öffnet ein Bild robust: EXIF-Drehung anwenden, erstes Einzelbild, Transparenz auf Weiß, RGB."""
    roh = Image.open(pfad)
    roh.seek(0)
    roh = ImageOps.exif_transpose(roh)
    if roh.mode in ("RGBA", "LA", "PA") or (roh.mode == "P" and "transparency" in roh.info):
        rgba = roh.convert("RGBA")
        weiss = Image.new("RGB", rgba.size, "white")
        weiss.paste(rgba, mask=rgba.split()[3])
        roh = weiss
    roh = roh.convert("RGB")
    if drehung % 360:
        roh = roh.rotate(-(drehung % 360), expand=True)      # positiv = im Uhrzeigersinn
    return roh


def baue_vorderseite(pfad, cfg, fit="contain", fortschritt=None, drehung=0):
    """Erzeugt die Vorderseite (Gestaltungsfläche) als RGB-Bild + Infos zur Bildqualität.
    contain = ganzes Bild sichtbar, Rest mit unscharfer Fortsetzung gefüllt; cover = Fläche füllen."""
    tw, th = cfg.flaeche_px
    roh = oeffne_bild(pfad, drehung)
    im = beschneide_schwarz(roh)
    passt_fast = abs((im.width / im.height) / (tw / th) - 1) < 0.05
    if fit == "cover" or passt_fast:
        s = max(tw / im.width, th / im.height)
        gross = (math.ceil(im.width * s), math.ceil(im.height * s))
        bild, methode, benutzt = verbessere(im, gross, cfg, fortschritt)
        left, top = (bild.width - tw) // 2, (bild.height - th) // 2
        bild = bild.crop((left, top, left + tw, top + th))
    else:
        s = min(tw / im.width, th / im.height)
        bg = deckend(im, tw, th).filter(ImageFilter.GaussianBlur(tw * 0.018))
        bild = ImageEnhance.Brightness(bg).enhance(0.92)
        vorn, methode, benutzt = verbessere(im, (max(1, round(im.width * s)), max(1, round(im.height * s))), cfg,
                                            fortschritt)
        bild.paste(vorn, ((tw - vorn.width) // 2, (th - vorn.height) // 2))
    ppi = round(cfg.dpi / s)                              # Bildpunkte der Quelle je Zoll im Druck
    code, bewertung = bewertung_ppi(ppi)
    info = dict(quelle=list(roh.size), inhalt=list(im.size), faktor=round(s, 2), ppi=ppi,
                bewertung=bewertung, bewertung_code=code, methode=methode, ki=benutzt)
    return bild, info


# =============================================================================================
# Gans der Rückseite: die Gans des Programmsymbols (ohne Sombrero – die Rückseite gilt für alle Sprachen) schwimmt
# unten rechts in einem kleinen Teich und schaut zum Wort. Sie bekommt nur Platz, der frei vom Text ist (gans_box).
# =============================================================================================
GANS_HOEHEN = (0.34, 0.31, 0.28, 0.25, 0.22, 0.20)    # Höhe der Gans-Box (Anteil der Innenhöhe), die größte freie gilt
GANS_SEITE = 1.17                                      # Breite : Höhe der Gans-Box
GANS_ABSTAND = 0.03                                    # Mindestabstand zum Text (Anteil der Innenhöhe)
_GANS_K = 2.586                                        # 1 Einheit von assets/me-goosta-symbol.svg in Gans-Einheiten


def _form(c, punkte, *kurven):
    p = c.beginPath()
    p.moveTo(*punkte)
    for k in kurven:
        (p.curveTo if len(k) == 6 else p.lineTo)(*k)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def _welle(c, x, y, b, a):
    """Kleine Welle (offener Linienzug aus zwei Bögen) der Breite b und Ausschlag a."""
    p = c.beginPath()
    p.moveTo(x, y)
    p.curveTo(x + b / 6, y + a, x + b / 3, y + a, x + b / 2, y)
    p.curveTo(x + 2 * b / 3, y - a, x + 5 * b / 6, y - a, x + b, y)
    c.drawPath(p, stroke=1, fill=0)


def zeichne_gans(c, x, y, w, h):
    """Gans in ihrer Box (x, y = links unten, w × h in pt, w = GANS_SEITE × h), rechts und unten bündig mit der
    Innenfläche; der Teich läuft über den Rand hinaus und wird vom Ausschnitt der Rückseite abgeschnitten."""
    c.saveState()
    c.translate(x + w, y)
    c.scale(h / 1000, h / 1000)                         # Gans-Einheiten: Ursprung rechts unten, Box −1170…0 × 0…1000
    c.saveState()
    k = _GANS_K
    c.translate(-30 + 44 * k, 478 * k)
    c.scale(-k, -k)                                     # Koordinaten wie im Programmsymbol (y nach unten), gespiegelt:
    farbe(c, PAL["gans"])                               # die Gans schaut nach links zum Wort
    _form(c, (84, 344), (54, 322, 38, 294, 44, 272), (72, 276, 104, 292, 128, 310))           # Schwanz
    c.ellipse(60, 272, 396, 472, stroke=0, fill=1)                                             # Körper
    _form(c, (300, 312), (292, 252, 306, 212, 332, 182), (402, 198), (382, 228, 372, 270, 380, 300),
          (386, 322, 398, 345, 396, 372), (300, 372))                                          # Hals + Brust
    farbe(c, PAL["gans_schatten"])                                                             # Flügel
    _form(c, (312, 344), (284, 312, 196, 306, 112, 330), (150, 346, 180, 358, 204, 356),
          (226, 372, 258, 374, 278, 364), (294, 370, 308, 360, 312, 344))
    c.translate(368, 184)                                                                      # Kopf leicht geneigt
    c.rotate(6)
    c.translate(-368, -184)
    farbe(c, PAL["gans"])
    c.circle(368, 184, 54, stroke=0, fill=1)                                                   # Kopf
    _form(c, (362, 134), (360, 112, 346, 100, 330, 102), (342, 110, 348, 120, 350, 136))       # Federschopf
    farbe(c, PAL["orange"])
    _form(c, (412, 170), (446, 166, 474, 176, 484, 190), (474, 204, 448, 210, 412, 204))       # Schnabel
    farbe(c, PAL["orange_dunkel"], stroke=True)
    c.setLineCap(1)
    c.setLineWidth(4)
    p = c.beginPath()
    p.moveTo(414, 190)
    p.curveTo(440, 192, 462, 192, 478, 188)
    c.drawPath(p, stroke=1, fill=0)
    farbe(c, PAL["wange"])
    c.ellipse(372, 194, 394, 206, stroke=0, fill=1)                                            # Wange
    farbe(c, PAL["auge"])
    c.circle(386, 176, 10.5, stroke=0, fill=1)                                                 # Auge mit Glanzpunkt
    farbe(c, "#FFFFFF")
    c.circle(389.5, 172.5, 3.4, stroke=0, fill=1)
    c.restoreState()
    farbe(c, PAL["bg_dunkel"])                                                                 # Teich
    _form(c, (-1170, -40), (-1140, 70, -1070, 128, -960, 140), (-700, 165, -400, 150, -150, 160),
          (0, 165, 100, 158, 200, 150), (200, -100), (-1170, -100))
    farbe(c, PAL["bg_licht"], stroke=True)
    c.setLineCap(1)
    c.setLineWidth(16)
    for wx, wy, wb in ((-1030, 70, 150), (-520, 60, 170), (-220, 95, 140)):
        _welle(c, wx, wy, wb, 15)
    c.restoreState()


# =============================================================================================
# Karten zeichnen (x, y = Endformat links unten; w, h = Endformat; alles in pt)
# =============================================================================================
def _innen(x, y, w, h, cfg):
    r = cfg.rand * mm
    return x + r, y + r, w - 2 * r, h - 2 * r


def _clip_rund(c, ix, iy, iw, ih, cfg):
    p = c.beginPath()
    p.roundRect(ix, iy, iw, ih, cfg.radius * mm if cfg.rand > 0 else 0)
    c.clipPath(p, stroke=0, fill=0)


def zeichne_vorderseite(c, x, y, w, h, jpg, cfg):
    ix, iy, iw, ih = _innen(x, y, w, h, cfg)
    c.saveState()
    _clip_rund(c, ix, iy, iw, ih, cfg)
    c.drawImage(str(jpg), ix, iy, iw, ih)
    c.restoreState()


def _breite(text, font, groesse):
    return pdfmetrics.stringWidth(text, font, groesse)


def _passend(zeilen, font, max_w, max_size, min_size, s_=None):
    """Größte Schriftgröße (Schritte 0,25 pt), bei der alle Zeilen passen – mit echten (geformten) Glyphenbreiten."""
    b = s_.breite if s_ else _breite
    s = max_size
    if s_ and (s_.hb or s_.rtl):                               # Breite wächst linear mit der Größe → direkt rechnen
        w = max(b(z, font, max_size) for z in zeilen)
        if w > max_w:
            s = max(min_size, math.floor(max_size * max_w / w * 4) / 4)
        return s
    while s > min_size and max(b(z, font, s) for z in zeilen) > max_w:
        s -= 0.25
    return s


TEXT_WARNUNG = {
    "haupt_zu_lang": L("Das Hauptwort ist etwas lang für die Karte – kürz es ein wenig oder brich es mit '|' um",
                       "The main word is a bit long for the card – shorten it a little or break it with '|'",
                       "La palabra principal es algo larga para la carta: acórtala un poco o divídela con '|'"),
    "alt_zu_lang": L("Die Alternativen sind etwas lang für die Karte – ein wenig kürzer, und alles passt",
                     "The alternatives are a bit long for the card – a little shorter and everything fits",
                     "Las alternativas son algo largas para la carta: un poco más cortas y todo cabe"),
    "zu_viel_text": L("viel Text für die Karte – kürzere Alternativen geben ihr Luft",
                      "a lot of text for the card – shorter alternatives give it room to breathe",
                      "mucho texto para la carta: alternativas más cortas le dan aire"),
}


def layout_wort(es, iw, ih, s_=None):
    """Berechnet das Textlayout der Rückseite. '/' trennt Hauptwort und Alternativen, '|' erzwingt
    einen Zeilenumbruch im Hauptwort. Gibt (Hauptzeilen, Größe, Altzeilen, Altgröße, Warnungs-Code) zurück.
    s_ = Schriftsatz der Sprache (satz(code)); ohne: Spanisch mit Poppins."""
    s_ = s_ or satz("es")
    fett, normal, b = s_.fett, s_.normal, s_.breite
    teile = [t.strip() for t in es.split("/") if t.strip()] or [" "]
    haupt, alt = teile[0], teile[1:]
    max_w, max_size, min_size = iw * 0.86, 0.235 * ih, 10.0
    warnung = None
    if "|" in haupt:
        zeilen = [z.strip() for z in haupt.split("|") if z.strip()]
        size = _passend(zeilen, fett, max_w, max_size, min_size, s_)
    else:
        s1 = _passend([haupt], fett, max_w, max_size, min_size, s_)
        z2 = s_.zwei_zeilen(haupt, max_size)
        s2 = _passend(z2, fett, max_w, max_size, min_size, s_) if len(z2) == 2 else 0
        zeilen, size = (z2, s2) if s2 >= s1 * 1.2 else ([haupt], s1)
    if len(zeilen) > 1:
        size = min(size, 0.19 * ih)                      # zweizeilig etwas kleiner: Kopf der Gans bleibt frei
    if max(b(z, fett, size) for z in zeilen) > max_w:
        warnung = "haupt_zu_lang"
    alt_zeilen, alt_size = [], 0.0
    if alt:
        alt_size = max(min(size * 0.52, 0.12 * ih), 8.0)
        einzeilig = "  ·  ".join(alt)
        alt_zeilen = [einzeilig] if b(einzeilig, normal, alt_size) <= max_w else alt
        while max(b(z, normal, alt_size) for z in alt_zeilen) > max_w and alt_size > 7:
            alt_size -= 0.25
        if max(b(z, normal, alt_size) for z in alt_zeilen) > max_w:
            warnung = "alt_zu_lang"
        if len(zeilen) * size * 1.12 + len(alt_zeilen) * alt_size * 1.2 > ih * 0.85:
            warnung = "zu_viel_text"
    return zeilen, size, alt_zeilen, alt_size, warnung


def _wort_zeilen(ix, iy, iw, ih, es, s_):
    """Zeilen der Rückseite als (Text, Schrift, Größe, Grundlinie, Farbe) + Mitte cx – eine Rechnung für zeichne_wort
    und wort_boxen (Block mittig bei 50 % der Höhe)."""
    zeilen, size, alt_zeilen, alt_size, _ = layout_wort(es, iw, ih, s_)
    lh, alt_lh = size * 1.12, alt_size * 1.2
    gap = size * 0.28 if alt_zeilen else 0
    block_h = len(zeilen) * lh + (gap + len(alt_zeilen) * alt_lh if alt_zeilen else 0)
    b = iy + ih * 0.50 + block_h / 2 - size * 0.80
    aus = []
    for z in zeilen:
        aus.append((z, s_.fett, size, b, PAL["text"]))
        b -= lh
    if alt_zeilen:
        b += lh - gap - alt_size * 0.95                       # Abstand nach der letzten Hauptzeile
        for z in alt_zeilen:
            aus.append((z, s_.normal, alt_size, b, PAL["text2"]))
            b -= alt_lh
    return ix + iw / 2, aus


def zeichne_wort(c, ix, iy, iw, ih, es, s_=None):
    s_ = s_ or satz("es")
    cx, zeilen = _wort_zeilen(ix, iy, iw, ih, es, s_)
    for z, font, size, b, ton in zeilen:
        farbe(c, ton)
        c.setFont(font, size)
        s_.zeichne_mitte(c, cx, b, z, font, size)


def wort_boxen(ix, iy, iw, ih, es, s_=None):
    """Fläche jeder Textzeile der Rückseite als (x, y, w, h) in pt: echte (geformte) Breite, oben 0,95 × Größe über
    der Grundlinie, unten die Unterlänge der Schrift (mindestens 0,3 × Größe)."""
    s_ = s_ or satz("es")
    cx, zeilen = _wort_zeilen(ix, iy, iw, ih, es, s_)
    boxen = []
    for z, font, size, b, _ in zeilen:
        w = s_.breite(z, font, size)
        unten = max(0.30, -pdfmetrics.getDescent(font, 1000) / 1000) * size
        boxen.append((cx - w / 2, b - unten, w, unten + 0.95 * size))
    return boxen


def gans_box(ix, iy, iw, ih, boxen):
    """Platz der Gans unten rechts als (x, y, w, h) in pt: die größte Stufe aus GANS_HOEHEN mit GANS_ABSTAND Luft zu
    allen Textzeilen (boxen = wort_boxen); passt nicht einmal die kleinste, None – dann keine Gans, das Wort geht vor."""
    luft = ih * GANS_ABSTAND
    for anteil in GANS_HOEHEN:
        h = ih * anteil
        w = h * GANS_SEITE
        x, y = ix + iw - w, iy
        if all(x >= bx + bw + luft or x + w <= bx - luft or y >= by + bh + luft or y + h <= by - luft
               for bx, by, bw, bh in boxen):
            return x, y, w, h
    return None


def mit_sprachkuerzel(cfg):
    """Sprachkürzel auf die Rückseite? auto = nur, wenn die Rückseite nicht Spanisch ist."""
    wahl = getattr(cfg, "sprachkuerzel", "auto")
    return wahl == "an" or (wahl == "auto" and getattr(cfg, "sprache", "es") != "es")


def zeichne_sprachkuerzel(c, ix, iy, iw, ih, code):
    """Kleines Kürzel (z. B. „JA“) oben links in einer hellen Kapsel – zeigt beim Sortieren, welche Sprache die Karte hat."""
    text = str(code or "es").upper()
    g = max(5.0, ih * 0.075)
    w = _breite(text, F_BOLD, g) + g * 0.9
    h = g * 1.45
    x, y = ix + iw * 0.045, iy + ih - ih * 0.06 - h
    farbe(c, "#FFFFFF")
    c.roundRect(x, y, w, h, h / 2, stroke=0, fill=1)
    farbe(c, PAL["text2"])
    c.setFont(F_BOLD, g)
    c.drawCentredString(x + w / 2, y + h * 0.5 - g * 0.36, text)


def zeichne_rueckseite(c, x, y, w, h, karte, cfg):
    ix, iy, iw, ih = _innen(x, y, w, h, cfg)
    code = getattr(cfg, "sprache", "es") or "es"
    s_ = satz(code)
    c.saveState()
    _clip_rund(c, ix, iy, iw, ih, cfg)
    farbe(c, PAL["bg"])                                        # ruhige, einfarbige Fläche hinter dem Wort
    c.rect(ix, iy, iw, ih, stroke=0, fill=1)
    gans_bild = Path(cfg.gans_bild) if cfg.gans_bild else None
    if gans_bild and gans_bild.exists():                      # eigenes Gänse-Hintergrundbild
        with Image.open(gans_bild) as im:
            s = max(iw / im.width, ih / im.height)
            gw, gh = im.width * s, im.height * s
        c.drawImage(str(gans_bild), ix + (iw - gw) / 2, iy + (ih - gh) / 2, gw, gh, mask="auto")
    else:                                                      # gezeichnete Gans unten rechts, nie hinter dem Text
        box = gans_box(ix, iy, iw, ih, wort_boxen(ix, iy, iw, ih, karte["es"], s_))
        if box:
            zeichne_gans(c, *box)
    zeichne_wort(c, ix, iy, iw, ih, karte["es"], s_)
    if mit_sprachkuerzel(cfg):
        zeichne_sprachkuerzel(c, ix, iy, iw, ih, code)
    c.restoreState()


# =============================================================================================
# Hilfslinien, Beschriftungen, Schnittmarken
# =============================================================================================
def beschrifte(c, text, x, y, groesse=4.6, hexwert=None, font=None, mitte=False, rechts=False):
    farbe(c, hexwert or PAL["grau"])
    c.setFont(font or F_MED, groesse)
    (c.drawCentredString if mitte else c.drawRightString if rechts else c.drawString)(x, y, text)


def _gestrichelt(c, hexwert, breite=0.5, muster=(2, 1.5)):
    farbe(c, hexwert, stroke=True)
    c.setLineWidth(breite)
    c.setDash(*muster)


def _pfeil_oben(c, cx, y0, laenge, hexwert):
    farbe(c, hexwert, stroke=True)
    farbe(c, hexwert)
    c.setLineWidth(0.8)
    c.setDash()
    c.line(cx, y0, cx, y0 + laenge)
    p = c.beginPath()
    p.moveTo(cx, y0 + laenge + 3.2)
    p.lineTo(cx - 2.2, y0 + laenge - 0.6)
    p.lineTo(cx + 2.2, y0 + laenge - 0.6)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def zeichne_vorlage_karte(c, x, y, w, h, cfg, seite, nummer=None, mit_beschnitt=True):
    """Hilfslinien für eine Karte; der Pfeil zeigt 'oben beim Lesen'."""
    b, r, s = cfg.beschnitt * mm if mit_beschnitt else 0, cfg.rand * mm, 3 * mm
    c.saveState()
    if mit_beschnitt:
        farbe(c, PAL["hellrot"])
        c.rect(x - b, y - b, w + 2 * b, h + 2 * b, stroke=0, fill=1)
    farbe(c, "#FFFFFF")
    c.rect(x, y, w, h, stroke=0, fill=1)
    ix, iy, iw, ih = x + r, y + r, w - 2 * r, h - 2 * r
    farbe(c, "#F3F7FB")
    c.roundRect(ix, iy, iw, ih, cfg.radius * mm, stroke=0, fill=1)
    _gestrichelt(c, PAL["blau"])
    c.roundRect(ix, iy, iw, ih, cfg.radius * mm, stroke=1, fill=0)
    _gestrichelt(c, PAL["gruen"])
    c.rect(ix + s, iy + s, iw - 2 * s, ih - 2 * s, stroke=1, fill=0)
    _gestrichelt(c, "#000000", 0.6, (3, 2))
    c.rect(x, y, w, h, stroke=1, fill=0)
    c.setDash()
    if mit_beschnitt:
        beschrifte(c, f"BESCHNITT {zahl(cfg.beschnitt)} mm – wird abgeschnitten (randlose Motive bis hierher anlegen)",
                   x + w / 2, y + h + b * 0.38, 4.2, PAL["rot"], mitte=True)
    beschrifte(c, f"ENDFORMAT {zahl(cfg.b)} × {zahl(cfg.h)} mm (Schnittkante)", x + 2.2 * mm, y + h - 1.9 * mm, 4.4, "#000000")
    beschrifte(c, f"weißer Kartenrand {zahl(cfg.rand)} mm", x + 2.2 * mm, y + 0.9 * mm, 4.4)
    beschrifte(c, f"GESTALTUNGSFLÄCHE {zahl(cfg.b - 2 * cfg.rand)} × {zahl(cfg.h - 2 * cfg.rand)} mm  "
                  f"(Ecken r = {zahl(cfg.radius)} mm)", ix + 1 * mm, iy + ih - 2.6 * mm, 4.4, PAL["blau"])
    beschrifte(c, f"SICHERER TEXTBEREICH {zahl(cfg.b - 2 * cfg.rand - 6)} × {zahl(cfg.h - 2 * cfg.rand - 6)} mm",
               ix + s + 1 * mm, iy + s + 1.2 * mm, 4.4, PAL["gruen"])
    titel = ("VORDERSEITE" if seite == "vorn" else "RÜCKSEITE") + (f"  {nummer}" if nummer else "")
    beschrifte(c, titel, x + w / 2, y + h / 2 - 2 * mm, 13, "#B5BCC6", F_BOLD, mitte=True)
    _pfeil_oben(c, x + w / 2, y + h / 2 + 5 * mm, 8 * mm, PAL["rot"])
    beschrifte(c, "OBEN beim Lesen", x + w / 2, y + h / 2 + 18.2 * mm, 5, PAL["rot"], F_BOLD, mitte=True)
    c.restoreState()


def schnittmarken(c, x0, y0, spalten, zeilen, cw, ch, gap, laenge=4 * mm, abstand=1.5 * mm):
    """Schnittmarken im Rand an allen Kartenkanten des Rasters (y0 = Unterkante des Rasters)."""
    farbe(c, "#000000", stroke=True)
    c.setLineWidth(0.25)
    c.setDash()
    gb, gh = spalten * cw + (spalten - 1) * gap, zeilen * ch + (zeilen - 1) * gap
    for xx in sorted({x0 + k * (cw + gap) + o for k in range(spalten) for o in (0, cw)}):
        c.line(xx, y0 + gh + abstand, xx, y0 + gh + abstand + laenge)
        c.line(xx, y0 - abstand, xx, y0 - abstand - laenge)
    for yy in sorted({y0 + k * (ch + gap) + o for k in range(zeilen) for o in (0, ch)}):
        c.line(x0 - abstand, yy, x0 - abstand - laenge, yy)
        c.line(x0 + gb + abstand, yy, x0 + gb + abstand + laenge, yy)


# =============================================================================================
# Daten laden und prüfen
# =============================================================================================
def dateiname_aus_text(text, endung=".jpg"):
    """Dateiname nach den Regeln der SPEC: 'Gans aufmüpfig' → 'gans-aufmuepfig.jpg'."""
    t = text.strip().lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        t = t.replace(a, b)
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return (t or "bild") + endung.lower()


def hat_gans(text):
    """Steckt die Gans im deutschen Text? „Gans“ bzw. „Gäns…“ irgendwo, groß oder klein („Die Gans ist alt“,
    „Gänsehaut“) – sie muss nicht vorn stehen (seit 2.4)."""
    t = str(text or "").casefold()
    return "gans" in t or "gäns" in t


def mit_gans(text):
    """Jede Karte braucht ihre Gans: fehlt sie im deutschen Text, kommt „Gans“ an den Anfang. Leerer Text bleibt leer."""
    text = " ".join(str(text or "").split())
    return text if not text or hat_gans(text) else f"Gans {text}"


MELDUNGEN = {
    "csv_fehlt": L("Die Kartenliste '{pfad}' ist nicht da – stimmt der Pfad?",
                   "The card list '{pfad}' isn’t there – is the path right?",
                   "No se encontró la lista de cartas '{pfad}'; ¿la ruta es correcta?"),
    "csv_kodierung": L("karten.csv ist nicht als UTF-8 gespeichert (als Windows-1252 gelesen) – kein Problem, beim "
                       "nächsten Speichern einfach „CSV UTF-8“ wählen",
                       "karten.csv is not saved as UTF-8 (read as Windows-1252) – no problem, just choose “CSV UTF-8” "
                       "next time you save",
                       "karten.csv no está guardado en UTF-8 (leído como Windows-1252): no pasa nada, la próxima vez "
                       "elige «CSV UTF-8» al guardar"),
    "bild_fehlt": L("Zeile {zeile}: Das Bild '{bild}' fehlt im Ordner '{ordner}/' – diese Karte setzt diesmal aus",
                    "row {zeile}: the image '{bild}' is missing in folder '{ordner}/' – this card sits this one out",
                    "fila {zeile}: falta la imagen '{bild}' en la carpeta '{ordner}/'; esta carta descansa esta vez"),
    "es_leer": L("Zeile {zeile}: Die Spalte '{spalte}' ({zs}) ist leer bei '{bild}' – trag das Wort ein, dann ist die "
                 "Karte beim nächsten Mal dabei",
                 "row {zeile}: column '{spalte}' ({zs}) is still empty for '{bild}' – add the word and the card "
                 "joins in next time",
                 "fila {zeile}: la columna '{spalte}' ({zs}) todavía está vacía en '{bild}'; escribe la palabra "
                 "y la carta entra la próxima vez"),
    "doppelt": L("Zeile {zeile}: '{bild}' steht mehrfach in der Liste – einmal reicht",
                 "row {zeile}: '{bild}' appears more than once – once is enough",
                 "fila {zeile}: '{bild}' aparece varias veces en la lista; con una basta"),
    "fit_unbekannt": L("Zeile {zeile}: fit='{fit}' unbekannt – nutze 'contain'",
                       "row {zeile}: fit='{fit}' unknown – using 'contain'",
                       "fila {zeile}: fit='{fit}' desconocido; se usa 'contain'"),
    "ohne_karte": L("'{bild}' liegt in '{ordner}/', steht aber noch nicht in der Kartenliste – unter „Karten "
                    "beschriften“ wird schnell eine Karte daraus",
                    "'{bild}' is in '{ordner}/' but not in the card list yet – “Label cards” turns it into a card in "
                    "no time",
                    "'{bild}' está en '{ordner}/' pero todavía no en la lista de cartas; en «Rotular cartas» se "
                    "convierte en carta en un momento"),
    "bild_unbekannt": L("Bild '{bild}' steht nicht in der Kartenliste oder fehlt im Ordner '{ordner}/'",
                        "image '{bild}' is not in the card list or missing in folder '{ordner}/'",
                        "la imagen '{bild}' no está en la lista de cartas o falta en la carpeta '{ordner}/'"),
    "karte_fehlt": L("Karte(n) {nummern} gibt es nicht (gültig: 1–{anzahl})",
                     "card(s) {nummern} do not exist (valid: 1–{anzahl})",
                     "la(s) carta(s) {nummern} no existe(n) (válidas: 1–{anzahl})"),
    "ppi_gering": L("Karte {nr} ({bild}): {ppi} ppi im Druck – mit einer größeren Bildquelle wird sie richtig scharf",
                    "card {nr} ({bild}): {ppi} ppi in print – a larger source image makes it really sharp",
                    "carta {nr} ({bild}): {ppi} ppi en la impresión; con una imagen más grande queda bien nítida"),
    "png_fehlt": L("Einzelbilder übersprungen (pypdfium2 installieren: pip install pypdfium2)",
                   "single images skipped (install pypdfium2: pip install pypdfium2)",
                   "imágenes individuales omitidas (instala pypdfium2: pip install pypdfium2)"),
    "schrift_fehlt": L("Die Schrift für {zs} ist noch nicht installiert – unter Tools → Sprachen kommt sie mit einem Klick "
                       "dazu; bis dahin druckt Poppins",
                       "The font for {zs} isn’t installed yet – Tools → Languages adds it with one click; until then "
                       "Poppins prints",
                       "La fuente para {zs} todavía no está instalada; en Herramientas → Idiomas se agrega con un clic; "
                       "mientras tanto imprime Poppins"),
    "formen_fehlt": L("Das Zusatzpaket zum Formen der Schrift ({zs}) ließ sich nicht laden – die Zeichen stehen noch "
                      "einzeln da. Unter Tools → Sprachen {zs} einmal neu installieren, dann sitzt alles",
                      "The add-on package for shaping the script ({zs}) could not be loaded – the letters still stand "
                      "apart. Reinstall {zs} under Tools → Languages once and everything falls into place",
                      "No se pudo cargar el paquete adicional para dar forma a la escritura ({zs}); las letras aún "
                      "aparecen sueltas. Reinstala {zs} una vez en Herramientas → Idiomas y todo queda en su sitio"),
    "ki_fehlt": L("Gewähltes KI-Modell „{gewaehlt}“ ist nicht installiert – nutze {benutzt}. Unter Werkzeuge → KI-Modell laden.",
                  "Selected AI model “{gewaehlt}” is not installed – using {benutzt}. See Tools → Download AI model.",
                  "El modelo de IA «{gewaehlt}» no está instalado; se usa {benutzt}. Ver Herramientas → Descargar modelo de IA."),
}
STUFE_WORT = {"fehler": L("Achtung", "Heads-up", "Atención"), "hinweis": L("Hinweis", "Note", "Aviso")}


def meldung(code, stufe="hinweis", **werte):
    """Meldung als Wörterbuch {stufe, code, werte, text}; text in der eingestellten Sprache mit Vorsilbe."""
    text = mit_zs(text_in(MELDUNGEN[code]), werte)
    return dict(stufe=stufe, code=code, werte=werte, text=f"{text_in(STUFE_WORT[stufe])}: {text}")


BEISPIEL_CSV = "beispiel-karten.csv"
BEISPIEL_BILDER = "beispiel-bilder"


def kartenliste_bereitstellen(csv_pfad):
    """Frisch entpackt gibt es noch keine karten.csv und keinen Bilderordner: Die Kartenliste entsteht aus
    beispiel-karten.csv, die Bilder dazu kommen aus beispiel-bilder/ nach bilder/ (beides daneben). Die Beispiele
    selbst werden nie verändert und ein vorhandenes Bild wird nie ersetzt – so kann das Entpacken einer neuen Version
    über einen alten Ordner weder die eigene Kartenliste noch eigene Bilder überschreiben."""
    p = Path(csv_pfad)
    beispiel = p.with_name(BEISPIEL_CSV)
    if p.name != "karten.csv" or p.exists() or not beispiel.is_file():
        return
    try:
        shutil.copy2(beispiel, p)
    except OSError:
        return
    quelle, ziel = p.with_name(BEISPIEL_BILDER), p.with_name("bilder")
    if not quelle.is_dir():
        return
    try:
        ziel.mkdir(exist_ok=True)
        for q in sorted(quelle.iterdir()):
            z = ziel / q.name
            if q.is_file() and not q.is_symlink() and q.suffix.lower() in BILD_ENDUNGEN and not z.exists():
                shutil.copy2(q, z)
    except OSError:
        pass


def lies_csv(csv_pfad):
    """Liest karten.csv roh, ohne zu prüfen. Gibt (spalten, zeilen, hinweise) zurück; zeilen sind Dicts mit allen
    Spalten – auch unbekannten und auskommentierten Zeilen (bild beginnt mit '#')."""
    kartenliste_bereitstellen(csv_pfad)
    pfad = Path(csv_pfad)
    if not pfad.exists():
        return list(KARTEN_SPALTEN[:4]), [], [meldung("csv_fehlt", "fehler", pfad=str(pfad))["text"]]
    roh = pfad.read_bytes()
    hinweise = []
    try:
        text = roh.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = roh.decode("cp1252")
        hinweise.append(meldung("csv_kodierung")["text"])
    kopf = text.splitlines()[0] if text.strip() else ""
    delim = max((";", ",", "\t"), key=kopf.count)
    leser = csv.DictReader(io.StringIO(text), delimiter=delim)
    spalten = [(f or "").strip().lower() for f in (leser.fieldnames or [])]
    zeilen = []
    for zeile in leser:
        z = {(k or "").strip().lower(): (v or "").strip() for k, v in zeile.items() if k is not None}
        if any(z.values()):
            zeilen.append(z)
    return spalten, zeilen, hinweise


def schreibe_csv(csv_pfad, zeilen, spalten=None):
    """Schreibt karten.csv (UTF-8 mit BOM, Semikolon, Windows-Zeilenenden). Bekannte Spalten zuerst, unbekannte
    Spalten bleiben erhalten. Die vorige Fassung wird als karten.bak.csv gesichert."""
    pfad = Path(csv_pfad)
    alle = list(KARTEN_SPALTEN[:4])
    for optional in ("fit", "uebersetzung"):                # optionale Spalten nur, wenn benutzt
        if any(z.get(optional) for z in zeilen) or (spalten and optional in spalten):
            alle.append(optional)
    for sp in list(spalten or []) + [k for z in zeilen for k in z]:
        if sp and sp not in alle:
            alle.append(sp)
    puffer = io.StringIO()
    w = csv.writer(puffer, delimiter=";", lineterminator="\r\n")
    w.writerow(alle)
    for z in zeilen:
        w.writerow([str(z.get(sp, "") or "").strip() for sp in alle])
    if pfad.exists():
        shutil.copy2(pfad, pfad.with_name(pfad.stem + ".bak.csv"))
    tmp = pfad.with_name(pfad.name + ".tmp")
    tmp.write_text(puffer.getvalue(), encoding="utf-8-sig", newline="")
    os.replace(tmp, pfad)
    return alle


def lies_karten(csv_pfad, bilder_dir, strukturiert=False, sprache="es"):
    """Liest karten.csv und prüft jede Zeile. Gibt (gültige Karten, Meldungen) zurück; Nummer = Position unter
    den gültigen, aktiven Karten. strukturiert=True: Meldungen als Wörterbücher (stufe, code, werte, text).
    sprache = Spalte der Rückseite (Standard es): Feld „es“ jeder Karte = Wort in dieser Sprache, „rueckseiten“ = alle
    gefüllten Sprachspalten, „uebersetzung“ = Status der Rückseite (Spalte uebersetzung bzw. uebersetzung_<code>)."""
    sp = sprache or "es"
    spalte_status = "uebersetzung" if sp == "es" else f"uebersetzung_{sp}"
    try:
        import sprachen
        codes = list(sprachen.SPRACHEN)
    except Exception:  # noqa: BLE001
        codes = ["es"]
    spalten, zeilen, hinweise = lies_csv(csv_pfad)
    meldungen = [dict(stufe="fehler" if not zeilen and not Path(csv_pfad).exists() else "hinweis",
                      code="csv", werte={}, text=h) for h in hinweise]
    karten, gesehen = [], set()
    ordner = Path(bilder_dir).name
    for nr, z in enumerate(zeilen, start=2):
        bild = z.get("bild", "")
        if not bild or bild.startswith("#"):
            gesehen.add(bild.lstrip("#").strip())
            continue
        bpfad = Path(bilder_dir) / bild
        if not sicherer_name(bild) or not bpfad.is_file():
            meldungen.append(meldung("bild_fehlt", "fehler", zeile=nr, bild=bild, ordner=ordner))
            continue
        if not z.get(sp):
            meldungen.append(meldung("es_leer", "fehler", zeile=nr, bild=bild, spalte=sp, zs=zs_name(code=sp)))
            continue
        if bild in gesehen:
            meldungen.append(meldung("doppelt", zeile=nr, bild=bild))
        gesehen.add(bild)
        fit = (z.get("fit") or "contain").lower()
        if fit not in ("contain", "cover"):
            meldungen.append(meldung("fit_unbekannt", zeile=nr, fit=fit))
            fit = "contain"
        karten.append(dict(nr=len(karten) + 1, bild=bild, pfad=bpfad, de=z.get("de", ""), es=z[sp],
                           notiz=z.get("notiz", ""), fit=fit, uebersetzung=uebersetzung_status(z.get(spalte_status)),
                           sprache=sp, rueckseiten={c: z[c] for c in codes if z.get(c)}))
    if Path(bilder_dir).is_dir():
        for p in sorted(Path(bilder_dir).glob("*")):
            if p.is_file() and p.suffix.lower() in BILD_ENDUNGEN and p.name not in gesehen:
                meldungen.append(meldung("ohne_karte", bild=p.name, ordner=ordner))
    return karten, (meldungen if strukturiert else [m["text"] for m in meldungen])


def uebersetzung_status(wert):
    """Spalte „uebersetzung“: 'auto' = automatisch übersetzt und noch nicht geprüft, 'geprueft' = von Hand geprüft,
    '' = von Hand eingetragen. Akzeptiert auch Schreibweisen aus Excel (ja, x, ✓, ok)."""
    w = str(wert or "").strip().lower()
    if w.startswith(("auto", "masch", "machine")):
        return "auto"
    if w.startswith(("gepr", "ja", "ok", "x", "✓", "yes", "sí", "si")):
        return "geprueft"
    return ""


def bilder_der_karten(csv_pfad, bilder_dir):
    """Alle Bilder der Kartenliste, die im Bilderordner liegen – auch ausgeschaltete und noch unbeschriftete Karten
    (für „Nur Bilder verbessern“). nr = Kartennummer wie beim Drucken, sonst None."""
    _, zeilen, _ = lies_csv(csv_pfad)
    gueltig, _ = lies_karten(csv_pfad, bilder_dir)
    nr_von = {}
    for k in gueltig:
        nr_von.setdefault(k["bild"], k["nr"])
    aus, gesehen = [], set()
    for z in zeilen:
        roh = z.get("bild", "")
        bild = roh.lstrip("#").strip()
        if not bild or bild in gesehen or not sicherer_name(bild) or not (Path(bilder_dir) / bild).is_file():
            continue
        gesehen.add(bild)
        fit = (z.get("fit") or "contain").lower()
        aus.append(dict(nr=nr_von.get(bild), bild=bild, pfad=Path(bilder_dir) / bild, de=z.get("de", ""),
                        es=z.get("es", ""), notiz=z.get("notiz", ""), fit=fit if fit in ("contain", "cover") else "contain",
                        aktiv=not roh.startswith("#")))
    return aus


def sicherer_name(name):
    """Nur einfache Dateinamen (kein Pfad, kein Laufwerk, kein Datenstrom, nicht versteckt)."""
    name = str(name or "")
    return bool(name) and not any(z in name for z in '/\\:\x00') and not name.startswith(".") and name.strip() == name \
        and len(name) <= 180


def pruefe_texte(karten, cfg):
    _, _, iw, ih = _innen(0, 0, cfg.b * mm, cfg.h * mm, cfg)
    meldungen = []
    s_ = satz(getattr(cfg, "sprache", "es"))
    for k in karten:
        code = layout_wort(k["es"], iw, ih, s_)[4]
        k["text_warnung_code"] = code
        k["text_warnung"] = text_in(TEXT_WARNUNG[code], "de") if code else None      # Prüfbogen: immer Deutsch
        if code:
            meldungen.append(T("Hinweis", "Note", "Aviso") + f" {T('Karte', 'card', 'carta')} {k['nr']} ({k['bild']}): "
                             + text_in(TEXT_WARNUNG[code]))
    return meldungen


# =============================================================================================
# Schritt 1 „Bild vorbereiten“ und Schritt 2 „Karte beschriften“: Prüfungen mit verständlichen Meldungen
# =============================================================================================
PRUEF_MELDUNGEN = {
    # --- Schritt 1: Bild ---
    "b_format_ok": L("Format {format} – wird unverändert übernommen", "Format {format} – will be used as is",
                     "Formato {format}: se usará tal cual"),
    "b_format_umwandeln": L("Format {format} – wird beim Übernehmen in PNG umgewandelt",
                            "Format {format} – will be converted to PNG when added",
                            "Formato {format}: se convertirá a PNG al agregarla"),
    "b_heic": L("HEIC/HEIF-Fotos (iPhone) kann das Programm leider nicht lesen – mit JPG klappt es sofort: am "
                "iPhone Einstellungen → Kamera → Formate → „Maximale Kompatibilität“ – oder das Foto am PC mit der "
                "Fotos-App öffnen und als JPG speichern.",
                "The program can’t read HEIC/HEIF photos (iPhone) – with JPG it works right away: on the iPhone "
                "Settings → Camera → Formats → “Most Compatible” – or open the photo on the PC in the Photos app and "
                "save it as JPG.",
                "El programa no puede leer fotos HEIC/HEIF (iPhone), pero con JPG funciona al instante: en el iPhone "
                "Ajustes → Cámara → Formatos → «Más compatible», o abre la foto en la computadora con la app Fotos y "
                "guárdala como JPG."),
    "b_unlesbar": L("Diese Datei lässt sich nicht als Bild lesen – mit JPG, PNG oder WEBP klappt es (GIF, BMP und TIFF "
                    "werden umgewandelt).",
                    "This file can’t be read as an image – JPG, PNG or WEBP work great (GIF, BMP and TIFF are "
                    "converted).",
                    "Este archivo no se puede leer como imagen; con JPG, PNG o WEBP funciona (GIF, BMP y TIFF se "
                    "convierten)."),
    "b_datei_gross": L("Die Datei ist größer als {mb} MB – etwas verkleinert passt sie bestimmt.",
                       "The file is larger than {mb} MB – a little smaller and it will fit.",
                       "El archivo pesa más de {mb} MB; un poco más pequeño y seguro que entra."),
    "b_pixel": L("Das Bild hat {mp} Megapixel – bis 60 klappt es, verkleinere es also ein wenig.",
                 "The image has {mp} megapixels – up to 60 works, so just shrink it a little.",
                 "La imagen tiene {mp} megapíxeles; hasta 60 funciona, así que redúcela un poco."),
    "b_winzig": L("Mit {w} × {h} px ist das Bild leider zu klein für eine Karte – ab 100 px an der kürzeren Seite "
                  "geht’s los.",
                  "At {w} × {h} px the image is too small for a card – from 100 px on the shorter side you’re good "
                  "to go.",
                  "Con {w} × {h} px la imagen es demasiado pequeña para una carta; desde 100 px en el lado corto ya "
                  "funciona."),
    "b_animiert": L("Animiertes Bild – nur das erste Einzelbild wird verwendet.",
                    "Animated image – only the first frame is used.",
                    "Imagen animada: solo se usa el primer cuadro."),
    "b_cmyk": L("Druckfarben (CMYK) werden in Bildschirmfarben (RGB) umgewandelt – Farben kurz prüfen.",
                "Print colours (CMYK) are converted to screen colours (RGB) – check the colours briefly.",
                "Los colores de impresión (CMYK) se convierten a RGB; revisa los colores."),
    "b_transparent": L("Transparente Bereiche werden weiß gefüllt.", "Transparent areas are filled with white.",
                       "Las zonas transparentes se rellenan de blanco."),
    "b_exif": L("Das Foto wird gemäß der Kamera-Ausrichtung automatisch gedreht.",
                "The photo is rotated automatically according to the camera orientation.",
                "La foto se gira automáticamente según la orientación de la cámara."),
    "b_raender": L("Schwarze Ränder werden automatisch entfernt ({px} px).",
                   "Black borders are removed automatically ({px} px).",
                   "Los bordes negros se quitan automáticamente ({px} px)."),
    "b_ppi": L("{w} × {h} px → im Druck {ppi} ppi: {bewertung}", "{w} × {h} px → {ppi} ppi in print: {bewertung}",
               "{w} × {h} px → {ppi} ppi en la impresión: {bewertung}"),
    "b_ppi_gering": L("{ppi} ppi im Druck – mit einem Bild ab {min_px} px Breite wird die Karte richtig scharf.",
                      "{ppi} ppi in print – with an image at least {min_px} px wide the card gets really sharp.",
                      "{ppi} ppi en la impresión; con una imagen de al menos {min_px} px de ancho la carta queda "
                      "bien nítida."),
    "b_hochkant": L("Das Bild ist hochkant, die Karte quer: Es wird ganz gezeigt und links und rechts unscharf fortgesetzt. "
                    "Liegt es nur falsch herum, mit ↻ drehen.",
                    "The image is portrait, the card landscape: it is shown in full and continued blurred on the left "
                    "and right. If it is just turned the wrong way, rotate it with ↻.",
                    "La imagen es vertical y la carta horizontal: se muestra completa y se continúa difuminada a los "
                    "lados. Si solo está girada, gírala con ↻."),
    "b_cover_schnitt": L("„Fläche füllen“ schneidet {prozent} % des Bildes ab – prüfe in der Vorschau, ob der Text noch ganz zu sehen ist.",
                         "“Fill the card” crops {prozent} % of the image – check in the preview that the text is still complete.",
                         "«Llenar la carta» recorta el {prozent} % de la imagen; revisa en la vista previa que el texto se vea completo."),
    "b_contain": L("„Ganzes Bild zeigen“: freie Ränder werden mit einer unscharfen Fortsetzung gefüllt.",
                   "“Show whole image”: empty margins are filled with a blurred continuation.",
                   "«Mostrar imagen completa»: los márgenes libres se rellenan con una continuación difuminada."),
    "b_doppelt": L("Genau dieses Bild liegt schon im Bilderordner als „{name}“ – schön, dass es dir so gefällt!",
                   "This exact image is already in the image folder as “{name}” – glad you like it so much!",
                   "Esta misma imagen ya está en la carpeta de imágenes como «{name}». ¡Qué bien que te guste tanto!"),
    "b_ki": L("Wird beim Erzeugen mit {methode} verbessert.", "Will be enhanced with {methode} when generating.",
              "Se mejorará con {methode} al generar."),
    # --- Schritt 1: Name ---
    "n_text_leer": L("Trag den Text ein, der auf dem Bild steht – daraus entsteht der Dateiname.",
                     "Enter the text shown on the image – the file name is made from it.",
                     "Escribe el texto que aparece en la imagen; de ahí sale el nombre del archivo."),
    "n_name": L("Dateiname: {name}", "File name: {name}", "Nombre del archivo: {name}"),
    "n_kollision": L("„{name}“ gibt es schon im Bilderordner. Text ändern oder „vorhandenes Bild ersetzen“ wählen.",
                     "“{name}” already exists in the image folder. Change the text or choose “replace existing image”.",
                     "«{name}» ya existe en la carpeta de imágenes. Cambia el texto o elige «reemplazar la imagen existente»."),
    "n_ersetzen": L("Das vorhandene Bild „{name}“ wird ersetzt; die alte Fassung kommt nach bilder/_entfernt/.",
                    "The existing image “{name}” will be replaced; the old version goes to bilder/_entfernt/.",
                    "La imagen existente «{name}» se reemplazará; la versión anterior va a bilder/_entfernt/."),
    "n_entwurf_doppelt": L("Ein anderes neues Bild bekommt schon den Namen „{name}“.",
                           "Another new image already gets the name “{name}”.",
                           "Otra imagen nueva ya recibe el nombre «{name}»."),
    "n_ohne_gans": L("Hier fehlt noch die Gans: Beim Speichern kommt „Gans“ an den Anfang. Sie darf auch mitten im Text "
                     "stehen, z. B. „Die Gans ist alt“.",
                     "The goose is still missing: saving puts “Gans” at the start. It may also stand anywhere in the "
                     "text, e.g. “Die Gans ist alt”.",
                     "Aquí falta el ganso: al guardar, «Gans» va al principio. También puede ir en medio del texto, "
                     "p. ej. «Die Gans ist alt»."),
    "n_lang": L("Sehr langer Text ({n} Zeichen) – stimmt er mit dem Bild überein?",
                "Very long text ({n} characters) – does it match the image?",
                "Texto muy largo ({n} caracteres): ¿coincide con la imagen?"),
    # --- Schritt 2: Karte ---
    "k_es_leer": L("Fehlt nur noch das Wort auf {zs} – es kommt auf die Rückseite.",
                   "Only the word in {zs} is missing – it goes on the back.",
                   "Solo falta la palabra en {zs}; va en el reverso."),
    "k_de_leer": L("Der Text auf dem Bild fehlt – er hilft beim Prüfen (Prüfbogen).",
                   "The text on the image is missing – it helps when checking (proof sheet).",
                   "Falta el texto de la imagen; ayuda al revisar (hoja de control)."),
    "k_gleich": L("Das Wort auf {zs} ist noch gleich dem deutschen Text – Zeit fürs Übersetzen!",
                  "The {zs} word still equals the German text – time to translate!",
                  "La palabra en {zs} todavía es igual al texto alemán: ¡hora de traducir!"),
    "k_umlaut": L("„{zeichen}“ gibt es im Spanischen nicht – Tippfehler? (Spanisch: á é í ó ú ü ñ ¿ ¡)",
                  "“{zeichen}” does not exist in Spanish – a typo? (Spanish: á é í ó ú ü ñ ¿ ¡)",
                  "«{zeichen}» no existe en español: ¿error de dedo? (español: á é í ó ú ü ñ ¿ ¡)"),
    "k_zeichen": L("Das Zeichen „{zeichen}“ kann mit der Kartenschrift nicht gedruckt werden.",
                   "The character “{zeichen}” cannot be printed with the card font.",
                   "El carácter «{zeichen}» no se puede imprimir con la fuente de la carta."),
    "k_formel": L("Text darf nicht mit = + - @ beginnen (Excel würde ihn als Formel ausführen).",
                  "Text must not start with = + - @ (Excel would run it as a formula).",
                  "El texto no puede empezar con = + - @ (Excel lo ejecutaría como fórmula)."),
    "k_alternativen": L("{n} Alternativen – mehr als 2 machen die Karte unübersichtlich.",
                        "{n} alternatives – more than 2 make the card cluttered.",
                        "{n} alternativas: más de 2 saturan la carta."),
    "k_frage": L("Spanische Fragen beginnen mit „¿“, Ausrufe mit „¡“.",
                 "Spanish questions start with “¿”, exclamations with “¡”.",
                 "En español las preguntas empiezan con «¿» y las exclamaciones con «¡»."),
    "k_doppelt": L("„{es}“ steht schon auf Karte {nr} ({bild}).", "“{es}” is already on card {nr} ({bild}).",
                   "«{es}» ya está en la carta {nr} ({bild})."),
    "k_passt": L("Passt prima auf die Karte: {zeilen} Zeile(n), Schriftgröße {pt} pt.",
                 "Fits nicely on the card: {zeilen} line(s), font size {pt} pt.",
                 "Cabe muy bien en la carta: {zeilen} línea(s), tamaño de letra {pt} pt."),
    "k_bild_fehlt": L("Das Bild „{bild}“ fehlt im Bilderordner.", "The image “{bild}” is missing in the image folder.",
                      "Falta la imagen «{bild}» en la carpeta de imágenes."),
}
BEWERTUNG = {"sehr_gut": L("sehr gut", "very good", "muy buena"), "gut": L("gut", "good", "buena"),
             "ausreichend": L("in Ordnung", "okay", "aceptable"),
             "gering": L("eher knapp", "a bit low", "algo justa")}


def pm(code, stufe, **werte):
    """Prüfmeldung {stufe: fehler|warnung|info|ok, code, werte, text} in der eingestellten Sprache."""
    if code in TEXT_WARNUNG:
        text = text_in(TEXT_WARNUNG[code])
    else:
        text = mit_zs(text_in(PRUEF_MELDUNGEN[code]), werte)
    return dict(stufe=stufe, code=code, werte=werte, text=text)


HEIC_MARKEN = (b"ftypheic", b"ftypheix", b"ftyphevc", b"ftypheim", b"ftypheis", b"ftypmif1", b"ftypmsf1")
MAX_DATEI_MB = 40
MAX_MEGAPIXEL = 60


def analysiere_bild(pfad, cfg, fit=None, drehung=0, bilder_dir=None, eigener_name=None):
    """Prüft ein neues Bild für Schritt 1. Gibt dict mit Kennzahlen, Empfehlung und Meldungen zurück.
    Meldungen mit stufe 'fehler' verhindern das Übernehmen."""
    pfad = Path(pfad)
    roh = pfad.read_bytes()
    m, info = [], dict(datei_bytes=len(roh), fit_empfehlung="contain", umwandeln=False, format=None)
    if len(roh) > MAX_DATEI_MB * 1024 * 1024:
        m.append(pm("b_datei_gross", "fehler", mb=MAX_DATEI_MB))
        return dict(info, meldungen=m, ok=False)
    if roh[4:12] in HEIC_MARKEN:
        m.append(pm("b_heic", "fehler"))
        return dict(info, format="HEIC", meldungen=m, ok=False)
    try:
        with Image.open(io.BytesIO(roh)) as probe:
            fmt, (w0, h0) = probe.format or "?", probe.size
            if w0 * h0 > MAX_MEGAPIXEL * 1_000_000:
                m.append(pm("b_pixel", "fehler", mp=round(w0 * h0 / 1e6)))
                return dict(info, format=fmt, meldungen=m, ok=False)
            probe.verify()
        with Image.open(io.BytesIO(roh)) as im:
            frames = getattr(im, "n_frames", 1)
            modus = im.mode
            transparent = modus in ("RGBA", "LA", "PA") or (modus == "P" and "transparency" in im.info)
            try:
                orientierung = im.getexif().get(0x0112, 1)
            except Exception:  # noqa: BLE001
                orientierung = 1
            bild = oeffne_bild(io.BytesIO(roh), drehung)
    except Exception:  # noqa: BLE001
        m.append(pm("b_unlesbar", "fehler"))
        return dict(info, meldungen=m, ok=False)

    info.update(format=fmt, quelle=[w0, h0], groesse=list(bild.size))
    if fmt in ("JPEG", "PNG", "WEBP"):
        m.append(pm("b_format_ok", "ok", format=fmt.replace("JPEG", "JPG")))
    else:
        info["umwandeln"] = True
        m.append(pm("b_format_umwandeln", "info", format=fmt))
    if frames > 1:
        m.append(pm("b_animiert", "warnung"))
    if modus == "CMYK":
        m.append(pm("b_cmyk", "info"))
    if transparent:
        m.append(pm("b_transparent", "info"))
    if orientierung not in (1, None):
        m.append(pm("b_exif", "info"))
    if min(bild.size) < 100:
        m.append(pm("b_winzig", "fehler", w=bild.width, h=bild.height))
        return dict(info, meldungen=m, ok=False)

    inhalt = beschneide_schwarz(bild)
    rand = (bild.width - inhalt.width) + (bild.height - inhalt.height)
    if rand:
        m.append(pm("b_raender", "info", px=rand))
    info["inhalt"] = list(inhalt.size)
    tw, th = cfg.flaeche_px
    seiten = inhalt.width / inhalt.height
    karte = tw / th
    info["fit_empfehlung"] = "cover" if abs(seiten / karte - 1) < 0.12 else "contain"
    fit = fit if fit in ("contain", "cover") else info["fit_empfehlung"]
    s_contain = min(tw / inhalt.width, th / inhalt.height)
    s_cover = max(tw / inhalt.width, th / inhalt.height)
    s = s_cover if fit == "cover" else s_contain
    ppi = round(cfg.dpi / s)
    code, _ = bewertung_ppi(ppi)
    info.update(fit=fit, ppi=ppi, bewertung_code=code,
                ppi_varianten=dict(contain=round(cfg.dpi / s_contain), cover=round(cfg.dpi / s_cover)))
    m.append(pm("b_ppi", "ok" if ppi >= 180 else "info" if ppi >= 120 else "warnung", w=inhalt.width, h=inhalt.height,
                ppi=ppi, bewertung=text_in(BEWERTUNG[code])))
    if ppi < 120:
        m.append(pm("b_ppi_gering", "warnung", ppi=ppi, min_px=math.ceil(inhalt.width * 180 / ppi)))
    if seiten < 0.87:
        m.append(pm("b_hochkant", "info"))
    if fit == "cover":
        sichtbar = (tw * th) / (inhalt.width * s_cover * inhalt.height * s_cover)
        prozent = round((1 - sichtbar) * 100)
        if prozent >= 12:
            m.append(pm("b_cover_schnitt", "warnung", prozent=prozent))
    elif abs(seiten / karte - 1) >= 0.05:
        m.append(pm("b_contain", "info"))
    sha = hashlib.sha1(roh).hexdigest()
    info["sha1"] = sha
    if bilder_dir and Path(bilder_dir).is_dir():
        for p in Path(bilder_dir).iterdir():
            if p.is_file() and p.suffix.lower() in BILD_ENDUNGEN and p.name != eigener_name \
                    and p.stat().st_size == len(roh) and hashlib.sha1(p.read_bytes()).hexdigest() == sha:
                m.append(pm("b_doppelt", "warnung", name=p.name))
                info["doppelt_von"] = p.name
                break
    if QUALITAET.get(cfg.qualitaet) is not None and s > 1.05:
        m.append(pm("b_ki", "info", methode=METHODE_NAME[ki_methode(cfg.ki)]))
    return dict(info, meldungen=m, ok=not any(x["stufe"] == "fehler" for x in m))


def pruefe_name(text, endung, belegt, andere_entwuerfe=(), ersetzen=False, vorhanden=None):
    """Prüft den Text auf dem Bild (= Dateiname) für Schritt 1. Gibt (dateiname, meldungen) zurück.
    vorhanden = Name der Datei, die schon so heißt (auch mit anderer Endung)."""
    text = " ".join(str(text or "").split())
    m = []
    if not text:
        return None, [pm("n_text_leer", "fehler")]
    name = dateiname_aus_text(text, endung)
    m.append(pm("n_name", "ok", name=name))
    if name in andere_entwuerfe:
        m.append(pm("n_entwurf_doppelt", "fehler", name=name))
    elif name in belegt:
        alt = vorhanden or name
        m.append(pm("n_ersetzen", "warnung", name=alt) if ersetzen else pm("n_kollision", "fehler", name=alt))
    if not hat_gans(text):
        m.append(pm("n_ohne_gans", "info"))
    if len(text) > 40:
        m.append(pm("n_lang", "warnung", n=len(text)))
    return name, m


def pruefe_karte(de, es, cfg, bild=None, bilder_dir=None, andere=(), notiz="", ziel=None):
    """Prüft die Beschriftung einer Karte für Schritt 2. 'andere' = übrige Karten (dicts mit es, nr, bild).
    'es' = Wort der Rückseite in der Kartensprache 'ziel' (Standard: Zielsprache); Spanisch-Regeln (ä ö ß, ¿ ¡) nur
    bei es; Schrift und Platz mit der Schrift der Sprache (nur, wenn ihr Sprachpaket da ist)."""
    ziel = ziel or zielsprache()
    s_ = satz(ziel)
    de = " ".join(str(de or "").split())
    es = " ".join(str(es or "").split())
    m = []
    if bild and bilder_dir and not (Path(bilder_dir) / bild).is_file():
        m.append(pm("k_bild_fehlt", "fehler", bild=bild))
    for t in (de, es, " ".join(str(notiz or "").split())):
        if t[:1] in ("=", "+", "-", "@"):
            m.append(pm("k_formel", "fehler"))
            break
    if not es:
        m.append(pm("k_es_leer", "fehler"))
    else:
        if de and es.casefold() == de.casefold():
            m.append(pm("k_gleich", "warnung"))
        fremd = sorted({z for z in es if z in "äöÄÖß"}) if ziel == "es" else []
        if fremd:
            m.append(pm("k_umlaut", "warnung", zeichen=" ".join(fremd)))
        fehlen = s_.fehlende_zeichen(es) if s_.voll else []
        if fehlen:
            m.append(pm("k_zeichen", "fehler", zeichen=" ".join(fehlen)))
        teile = [t for t in es.split("/") if t.strip()]
        if len(teile) > 3:
            m.append(pm("k_alternativen", "warnung", n=len(teile) - 1))
        if ziel == "es" and ((es.rstrip().endswith("?") and "¿" not in es)
                             or (es.rstrip().endswith("!") and "¡" not in es)):
            m.append(pm("k_frage", "info"))
        _, _, iw, ih = _innen(0, 0, cfg.b * mm, cfg.h * mm, cfg)
        zeilen, groesse, _, _, warnung = layout_wort(es, iw, ih, s_) if s_.voll else ([], 0, 0, 0, None)
        if warnung:
            m.append(pm(warnung, "warnung"))
        elif zeilen:
            m.append(pm("k_passt", "ok", zeilen=len(zeilen), pt=zahl(round(groesse, 1)) if sprache() == "de"
                        else f"{round(groesse, 1):g}"))
        haupt = teile[0].strip().casefold() if teile else ""
        for k in andere:
            if haupt and str(k.get("es", "")).split("/")[0].strip().casefold() == haupt:
                m.append(pm("k_doppelt", "info", es=teile[0].strip(), nr=k.get("nr") or "–", bild=k.get("bild", "")))
                break
    if not de:
        m.append(pm("k_de_leer", "warnung"))
    elif not hat_gans(de):
        m.append(pm("n_ohne_gans", "info"))
    return dict(de=de, es=es, meldungen=m, ok=not any(x["stufe"] == "fehler" for x in m))


_HASH_SPEICHER: dict = {}
_HASH_LOCK = threading.Lock()


def datei_hash(pfad):
    """SHA-1 des Dateiinhalts als hashlib-Objekt (eine Kopie). Gemerkt je Pfad, Änderungszeit und Größe – so liest
    die Übersicht der Bildverbesserung nicht bei jedem Aufruf alle Bilder neu."""
    p = Path(pfad)
    st = p.stat()
    schluessel = (str(p.resolve()), st.st_mtime_ns, st.st_size)
    with _HASH_LOCK:
        h = _HASH_SPEICHER.get(schluessel)
    if h is None:
        h = hashlib.sha1(p.read_bytes())
        with _HASH_LOCK:
            if len(_HASH_SPEICHER) > 5000:
                _HASH_SPEICHER.clear()
            _HASH_SPEICHER[schluessel] = h
    return h.copy()


def cache_schluessel(pfad, cfg, fit, methode=None):
    """Name der aufbereiteten Vorderseite im Zwischenspeicher: Bildinhalt + alle Einstellungen, die das Ergebnis
    ändern. Eine neue Einstellung oder ein neues Modell ergibt einen neuen Schlüssel."""
    h = datei_hash(pfad)
    tw, th = cfg.flaeche_px
    h.update(json.dumps([BILD_VERSION, tw, th, cfg.dpi, fit, cfg.qualitaet,
                         methode or ki_methode(cfg.ki)]).encode())
    return h.hexdigest()[:20]


def bereite_vorderseiten_vor(karten, cfg, cache_dir, cache=True, aufraeumen=True, melde=None, einzeln=False):
    """Bereitet alle Vorderseiten auf. Ergebnisse werden zwischengespeichert: Bei einem neuen Lauf werden nur neue
    oder geänderte Bilder neu berechnet. Mit Real-ESRGAN wird nacheinander gerechnet (das Modell nutzt alle
    Prozessorkerne selbst) und der Fortschritt gemeldet; sonst parallel (einzeln=True: auch dann je Bild melden).
    Zu jedem Ergebnis wird gespeichert, aus welchem Bild es mit welchen Einstellungen entstand (für die Übersicht
    „Bildverbesserung“ der Oberfläche)."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    methode = ki_methode(cfg.ki)

    def ablegen(k, key, bild, info, dauer=0.0):
        info.update(bild=k.get("bild"), sha1=datei_hash(k["pfad"]).hexdigest(), qualitaet=cfg.qualitaet,
                    fit=k["fit"], zeit=time.strftime("%Y-%m-%d %H:%M:%S"), dauer=round(dauer, 1))
        jpg, meta = cache_dir / f"{key}.jpg", cache_dir / f"{key}.json"
        tmp = jpg.with_name(f"{key}.{os.getpid()}.{id(k)}.tmp")          # atomar: parallele Aufrufe stören sich nicht
        bild.save(tmp, "JPEG", quality=93, dpi=(cfg.dpi, cfg.dpi), subsampling=0, optimize=True)
        os.replace(tmp, jpg)
        tmp_meta = meta.with_name(f"{key}.{os.getpid()}.{id(k)}.json.tmp")
        tmp_meta.write_text(json.dumps(info, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp_meta, meta)
        return jpg

    offen = []
    for k in karten:
        key = cache_schluessel(k["pfad"], cfg, k["fit"], methode)
        jpg, meta = cache_dir / f"{key}.jpg", cache_dir / f"{key}.json"
        k["_key"] = key
        if cache and jpg.exists() and meta.exists():
            try:
                k["front_jpg"], k["bild_info"] = jpg, json.loads(meta.read_text(encoding="utf-8"))
                continue
            except ValueError:
                pass
        offen.append(k)

    if methode.startswith("realesrgan") and QUALITAET.get(cfg.qualitaet) is not None:
        for i, k in enumerate(offen, start=1):
            t0 = time.time()
            stand = {"p": -1}

            def fortschritt(fertig, gesamt, k=k, i=i, stand=stand):
                p = fertig * 4 // gesamt
                if melde and p > stand["p"] and p < 4:
                    stand["p"] = p
                    melde(T(f"    [{i}/{len(offen)}] {k['bild']}: KI-Vergrößerung {p * 25} %",
                            f"    [{i}/{len(offen)}] {k['bild']}: AI upscaling {p * 25} %",
                            f"    [{i}/{len(offen)}] {k['bild']}: ampliación con IA {p * 25} %"))
            bild, info = baue_vorderseite(k["pfad"], cfg, k["fit"], fortschritt)
            k["front_jpg"], k["bild_info"] = ablegen(k, k["_key"], bild, info, time.time() - t0), info
            if melde:
                melde(T(f"    [{i}/{len(offen)}] {k['bild']}: fertig in {time.time() - t0:.0f} s",
                        f"    [{i}/{len(offen)}] {k['bild']}: done in {time.time() - t0:.0f} s",
                        f"    [{i}/{len(offen)}] {k['bild']}: listo en {time.time() - t0:.0f} s"))
    else:
        def eine(k):
            t0 = time.time()
            bild, info = baue_vorderseite(k["pfad"], cfg, k["fit"])
            return k, ablegen(k, k["_key"], bild, info, time.time() - t0), info
        arbeiter = max(1, min(4, os.cpu_count() or 1))
        pool = None if sys.platform == "emscripten" else ThreadPoolExecutor(arbeiter)   # Web-App (Pyodide): ohne Threads
        try:
            for i, (k, jpg, info) in enumerate(pool.map(eine, offen) if pool else map(eine, offen), start=1):
                k["front_jpg"], k["bild_info"] = jpg, info
                if melde and einzeln:
                    melde(T(f"    [{i}/{len(offen)}] {k['bild']}: fertig", f"    [{i}/{len(offen)}] {k['bild']}: done",
                            f"    [{i}/{len(offen)}] {k['bild']}: listo"))
        finally:
            if pool:
                pool.shutdown()

    if aufraeumen:                                       # nicht mehr benötigte Zwischenstände löschen
        genutzt = {n for k in karten for n in (f"{k['_key']}.jpg", f"{k['_key']}.json")}
        for alt in cache_dir.glob("*"):
            if alt.is_file() and alt.name not in genutzt and not alt.name.startswith("vorschau-"):
                alt.unlink(missing_ok=True)
    for k in karten:
        k.pop("_key", None)
    return len(offen)


# =============================================================================================
# Ausgaben
# =============================================================================================
def neues_pdf(pfad, seite_pt, titel, sprache="es"):
    c = rl_canvas.Canvas(str(pfad), pagesize=seite_pt, pageCompression=1, initialFontName=F_MED, initialFontSize=8)
    c.setTitle(titel)
    c.setAuthor(PRODUKT)
    c.setSubject(f"Lernkarten Deutsch – {zs_name('de', sprache or 'es')}")
    if sprache and sprache != "es":
        c.setKeywords(f"lang={sprache}")
    c.setCreator(f"gans_lernkarten.py {VERSION}")
    return c


def drehe(c, grad, cw, ch):
    """Transformation, damit ein Inhalt cw × ch (pt) um 'grad' gedreht auf die Seite passt."""
    grad %= 360
    if grad == 90:
        c.translate(ch, 0)
        c.rotate(90)
    elif grad == 180:
        c.translate(cw, ch)
        c.rotate(180)
    elif grad == 270:
        c.translate(0, cw)
        c.rotate(-90)
    elif grad != 0:
        raise ValueError("Drehung muss ein Vielfaches von 90 sein")


def rotationen(cfg):
    """(Vorderseite, Rückseite) in Grad für die Druckerei-Datei."""
    v, r = (90, 270) if cfg.hochkant else (0, 0)          # hochkant: Rückseite 180° versetzt
    return v, (r + 180) % 360 if cfg.rs_drehen else r


def baue_druckerei(cfg, karten, pfad, vorlage=False):
    cw, ch, bl = cfg.b * mm, cfg.h * mm, cfg.beschnitt * mm
    W, H = cw + 2 * bl, ch + 2 * bl
    rot_v, rot_r = rotationen(cfg)
    seite = (H, W) if cfg.hochkant else (W, H)
    c = neues_pdf(pfad, seite, f"{PRODUKT} – " + ("Vorlage Druckerei" if vorlage else "Druckdatei"), cfg.sprache)
    for k in (karten if not vorlage else [None]):
        for art, rot in (("vorn", rot_v), ("hinten", rot_r)):
            c.saveState()
            drehe(c, rot, W, H)
            if vorlage:
                zeichne_vorlage_karte(c, bl, bl, cw, ch, cfg, art)
            elif art == "vorn":
                zeichne_vorderseite(c, bl, bl, cw, ch, k["front_jpg"], cfg)
            else:
                zeichne_rueckseite(c, bl, bl, cw, ch, k, cfg)
            c.restoreState()
            trim = (bl, bl, bl + ch, bl + cw) if rot in (90, 270) else (bl, bl, bl + cw, bl + ch)
            c.setTrimBox(trim)                              # Endformat
            c.setBleedBox((0, 0, seite[0], seite[1]))       # Endformat + Beschnitt
            c.showPage()
    c.save()


def papier_mm(cfg):
    """(Breite, Höhe, Name) des Papiers für Heimdruck und Prüfbogen."""
    return PAPIER.get(getattr(cfg, "papier", "a4"), PAPIER["a4"])


def raster(cfg):
    pb, ph, _ = papier_mm(cfg)
    gap, cw, ch, rand = cfg.abstand * mm, cfg.b * mm, cfg.h * mm, 10 * mm
    sp = cfg.spalten or max(1, int((pb * mm - 2 * rand + gap) // (cw + gap)))
    ze = cfg.zeilen or max(1, int((ph * mm - 2 * rand + gap) // (ch + gap)))
    x0 = (pb * mm - (sp * cw + (sp - 1) * gap)) / 2 + cfg.versatz_x * mm
    y0 = (ph * mm - (ze * ch + (ze - 1) * gap)) / 2 + cfg.versatz_y * mm
    return sp, ze, x0, y0, gap


def baue_bogen(cfg, karten, pfad, vorlage=False):
    cw, ch = cfg.b * mm, cfg.h * mm
    sp, ze, x0, y0, gap = raster(cfg)
    pro_bogen = sp * ze
    n = len(karten) if not vorlage else pro_bogen
    boegen = math.ceil(n / pro_bogen)
    pb, ph, pname = papier_mm(cfg)
    c = neues_pdf(pfad, (pb * mm, ph * mm), f"{PRODUKT} – " + (f"Vorlage Heimdruck {pname}" if vorlage else f"Heimdruck {pname}"),
                  cfg.sprache)
    for bogen in range(boegen):
        chunk = range(bogen * pro_bogen, min((bogen + 1) * pro_bogen, n))
        for art in ("vorn", "hinten"):
            for pos, idx in enumerate(chunk):
                zeile, spalte = divmod(pos, sp)
                if art == "hinten":
                    spalte = sp - 1 - spalte                 # gespiegelt: Wenden an der langen Kante
                x, y = x0 + spalte * (cw + gap), y0 + (ze - 1 - zeile) * (ch + gap)
                if vorlage:
                    zeichne_vorlage_karte(c, x, y, cw, ch, cfg, art, nummer=idx + 1, mit_beschnitt=False)
                elif art == "vorn":
                    zeichne_vorderseite(c, x, y, cw, ch, karten[idx]["front_jpg"], cfg)
                else:
                    c.saveState()
                    if cfg.rs_drehen:
                        c.translate(x + cw / 2, y + ch / 2)
                        c.rotate(180)
                        c.translate(-(x + cw / 2), -(y + ch / 2))
                    zeichne_rueckseite(c, x, y, cw, ch, karten[idx], cfg)
                    c.restoreState()
            schnittmarken(c, x0, y0, sp, ze, cw, ch, gap)
            hinweis = (f"{PRODUKT} · Bogen {bogen + 1}/{boegen} · {'VORDERSEITEN' if art == 'vorn' else 'RÜCKSEITEN'} · "
                       f"Format {zahl(cfg.b)} × {zahl(cfg.h)} mm · Druck mit 100 % („Tatsächliche Größe“) · "
                       f"beidseitig: Wenden an der langen Kante" + (" · VORLAGE – nicht drucken" if vorlage else ""))
            beschrifte(c, hinweis, pb * mm / 2, 8 * mm, 6, mitte=True)
            c.showPage()
    c.save()


def baue_pruefbogen(cfg, karten, pfad):
    """A4-Übersicht: jede Karte mit Vorder- und Rückseite, Texten und Bildqualität – zum Prüfen vor dem Druck."""
    rand, kopf = 12 * mm, 22 * mm
    skala = 62.0 / cfg.b                                   # Karten auf 62 mm Breite verkleinert
    kw, kh = cfg.b * mm * skala, cfg.h * mm * skala
    zeile_h = kh + 4.5 * mm
    pb, ph, _ = papier_mm(cfg)
    pro_seite = max(1, int((ph * mm - 2 * rand - kopf) // zeile_h))
    seiten = math.ceil(len(karten) / pro_seite)
    code = cfg.sprache or "es"
    s_ = satz(code)
    titel = f"{PRODUKT} – Prüfbogen" + (f" ({zs_name('de', code)})" if code != "es" else "")
    c = neues_pdf(pfad, (pb * mm, ph * mm), titel, code)
    for s in range(seiten):
        oben = ph * mm - rand
        beschrifte(c, titel, rand, oben - 6 * mm, 15, PAL["text"], F_BOLD)
        beschrifte(c, f"{len(karten)} Karten · Format {zahl(cfg.b)} × {zahl(cfg.h)} mm · Bildqualität „{cfg.qualitaet}“ · "
                      f"Seite {s + 1}/{seiten} · {time.strftime('%d.%m.%Y')}", rand, oben - 12 * mm, 7.5)
        beschrifte(c, "Bitte prüfen: Übersetzung richtig? Bild scharf genug? Erst dann drucken.",
                   rand, oben - 17 * mm, 7.5, PAL["text2"])
        for pos, k in enumerate(karten[s * pro_seite:(s + 1) * pro_seite]):
            y = oben - kopf - (pos + 1) * zeile_h + 3 * mm
            for spalte, art in enumerate(("vorn", "hinten")):
                x = rand + spalte * (kw + 5 * mm)
                c.saveState()
                c.translate(x, y)
                c.scale(skala, skala)
                farbe(c, "#D5DBE3", stroke=True)
                c.setLineWidth(0.6 / skala)
                c.rect(0, 0, cfg.b * mm, cfg.h * mm, stroke=1, fill=0)
                if art == "vorn":
                    zeichne_vorderseite(c, 0, 0, cfg.b * mm, cfg.h * mm, k["front_jpg"], cfg)
                else:
                    zeichne_rueckseite(c, 0, 0, cfg.b * mm, cfg.h * mm, k, cfg)
                c.restoreState()
            tx = rand + 2 * kw + 10 * mm
            ty = y + kh - 4 * mm
            info = k["bild_info"]
            beschrifte(c, f"Karte {k['nr']}", tx, ty, 10, PAL["text"], F_BOLD)
            zeilen = [(f"DE: {k['de'] or '–'}", PAL["text"]),
                      ((f"{code.upper()}: ", k["es"]), PAL["text"]),
                      (k["bild"], PAL["grau"]),
                      (f"Bildinhalt {info['inhalt'][0]} × {info['inhalt'][1]} px · vergrößert ×{zahl(info['faktor'])}", PAL["grau"]),
                      (f"{info['ppi']} ppi im Druck: {info['bewertung']}",
                       PAL["rot"] if info["ppi"] < 120 else PAL["gruen"] if info["ppi"] >= 180 else PAL["text2"]),
                      (info["methode"], PAL["grau"])]
            if k.get("text_warnung"):
                zeilen.append(("! " + k["text_warnung"], PAL["rot"]))
            if k.get("uebersetzung") == "auto":
                zeilen.append((f"! {code.upper()} wurde automatisch übersetzt – bitte prüfen", PAL["rot"]))
            elif k.get("uebersetzung") == "geprueft":
                zeilen.append(("Übersetzung von Hand geprüft", PAL["gruen"]))
            for i, (t, col) in enumerate(zeilen):
                breite = pb * mm - rand - tx
                g = 7
                if isinstance(t, tuple):                      # Wort der Rückseite in der Schrift seiner Sprache
                    vor, wort = t
                    while _breite(vor, F_MED, g) + s_.breite(wort, s_.normal, g) > breite and g > 5:
                        g -= 0.25
                    yy = ty - 5.2 * mm - i * 3.6 * mm
                    beschrifte(c, vor, tx, yy, g, col)
                    farbe(c, col)
                    c.setFont(s_.normal, g)
                    w = s_.breite(wort, s_.normal, g)
                    s_.zeichne_mitte(c, tx + _breite(vor, F_MED, g) + w / 2, yy, wort, s_.normal, g)
                    continue
                while _breite(t, F_MED, g) > breite and g > 5:
                    g -= 0.25
                beschrifte(c, t, tx, ty - 5.2 * mm - i * 3.6 * mm, g, col)
            farbe(c, PAL["grau"], stroke=True)                # Abhak-Kästchen
            c.setLineWidth(0.6)
            c.rect(tx, y + 0.6 * mm, 3 * mm, 3 * mm, stroke=1, fill=0)
            beschrifte(c, "geprüft", tx + 4.5 * mm, y + 1.3 * mm, 7)
        c.showPage()
    c.save()


def exportiere_png(pdf_pfad, ziel, karten, dpi, alle=True):
    """Rendert jede Seite des Druckerei-PDFs als PNG, benannt nach Kartennummer (03_vorn.png, 03_hinten.png).
    alle=True: alte Einzelbilder werden vorher entfernt; sonst nur die betroffenen ersetzt."""
    ziel.mkdir(parents=True, exist_ok=True)
    namen = [f"{k['nr']:02d}_{s}.png" for k in karten for s in ("vorn", "hinten")]
    for alt in (ziel.glob("*.png") if alle else (ziel / n for n in namen)):
        alt.unlink(missing_ok=True)
    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(str(pdf_pfad))
        for i in range(len(pdf)):
            pdf[i].render(scale=dpi / 72).to_pil().convert("RGB").save(ziel / namen[i], dpi=(dpi, dpi), compress_level=6)
        pdf.close()
        return True
    except ImportError:
        pass
    except OSError:                                    # z. B. pdfium.dll von Windows gesperrt → wie „nicht installiert“
        pass
    if shutil.which("pdftoppm"):
        subprocess.run(["pdftoppm", "-r", str(dpi), "-png", str(pdf_pfad), str(ziel / "seite")], check=True)
        for i, p in enumerate(sorted(ziel.glob("seite-*.png"))):
            p.replace(ziel / namen[i])
        return True
    return False


def vorderseite_fuer_vorschau(karte, cfg, cache_dir, drehung=0):
    """Vorderseite für die Bildschirm-Vorschau: das fertige Ergebnis aus dem Zwischenspeicher, falls vorhanden –
    sonst eine Schnellvorschau ohne Real-ESRGAN (dauert nur Sekundenbruchteile). Gibt (jpg, info, schnell) zurück."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    if not drehung:
        key = cache_schluessel(karte["pfad"], cfg, karte["fit"])
        jpg, meta = cache_dir / f"{key}.jpg", cache_dir / f"{key}.json"
        if jpg.exists() and meta.exists():
            return jpg, json.loads(meta.read_text(encoding="utf-8")), False
    schnell = Konfig(**{**cfg.__dict__, "ki": "fsrcnn" if ki_methode(cfg.ki).startswith("realesrgan") else cfg.ki})
    key = "vorschau-" + cache_schluessel(karte["pfad"], schnell, karte["fit"]) + (f"-{drehung % 360}" if drehung else "")
    jpg, meta = cache_dir / f"{key}.jpg", cache_dir / f"{key}.json"
    if not (jpg.exists() and meta.exists()):
        bild, info = baue_vorderseite(karte["pfad"], schnell, karte["fit"], drehung=drehung)
        tmp = jpg.with_name(f"{key}.{os.getpid()}.{threading_id()}.tmp")
        bild.save(tmp, "JPEG", quality=88)
        os.replace(tmp, jpg)
        meta.write_text(json.dumps(info, ensure_ascii=False), encoding="utf-8")
        alte = sorted(cache_dir.glob("vorschau-*.jpg"), key=lambda q: q.stat().st_mtime)
        for alt in alte[:-200]:                                  # Vorschau-Zwischenspeicher begrenzen
            alt.unlink(missing_ok=True)
            alt.with_suffix(".json").unlink(missing_ok=True)
    info = json.loads(meta.read_text(encoding="utf-8"))
    return jpg, info, ki_methode(cfg.ki) != ki_methode(schnell.ki)


def threading_id():
    return threading.get_ident()


def leinwand_da():
    """Rückseiten-Vorschau ohne pypdfium2 möglich? (leinwand.py: dieselbe Zeichenroutine auf einem Pillow-Bild)"""
    try:
        import leinwand  # noqa: F401
        return True
    except ImportError:
        return False


def _rueckseite_pillow(karte, cfg, w, h, dpi):
    """Rückseite ohne pypdfium2 (Web-App, gesperrte DLL): zeichne_rueckseite auf der Pillow-Leinwand; ohne leinwand.py
    wie früher keine Vorschau (None)."""
    try:
        import leinwand
    except ImportError:
        return None
    c = leinwand.Leinwand(w, h, dpi)
    farbe(c, "#FFFFFF")
    c.rect(0, 0, w, h, stroke=0, fill=1)
    zeichne_rueckseite(c, 0, 0, w, h, karte, cfg)
    return c.png(), "image/png"


def vorschau_png(karte, cfg, seite="vorn", dpi=110, cache_dir=None, drehung=0):
    """Rendert eine Kartenseite (Endformat, ohne Beschnitt) als PNG für die Oberfläche.
    Gibt (bytes, mime) zurück; ohne pypdfium2 zeichnet die Pillow-Leinwand die Rückseite (None ohne leinwand.py)."""
    if seite == "vorn" and "front_jpg" not in karte:
        karte["front_jpg"], karte["bild_info"], karte["schnellvorschau"] = vorderseite_fuer_vorschau(
            karte, cfg, Path(cache_dir or HIER / "ausgabe" / ".cache"), drehung)
    w, h = cfg.b * mm, cfg.h * mm
    try:
        import pypdfium2 as pdfium
    except Exception:  # noqa: BLE001 – nicht installiert oder DLL von Windows gesperrt
        if seite == "vorn":
            return Path(karte["front_jpg"]).read_bytes(), "image/jpeg"
        return _rueckseite_pillow(karte, cfg, w, h, dpi)
    puffer = io.BytesIO()
    c = rl_canvas.Canvas(puffer, pagesize=(w, h), initialFontName=F_MED, initialFontSize=8)
    farbe(c, "#FFFFFF")
    c.rect(0, 0, w, h, stroke=0, fill=1)
    if seite == "vorn":
        zeichne_vorderseite(c, 0, 0, w, h, karte["front_jpg"], cfg)
    else:
        zeichne_rueckseite(c, 0, 0, w, h, karte, cfg)
    c.showPage()
    c.save()
    pdf = pdfium.PdfDocument(puffer.getvalue())
    bild = pdf[0].render(scale=dpi / 72).to_pil().convert("RGB")
    pdf.close()
    aus = io.BytesIO()
    bild.save(aus, "PNG", compress_level=3)
    return aus.getvalue(), "image/png"


def schreibe_bericht(ausgabe, cfg, karten, meldungen, erzeugt, auswahl=None):
    """Speichert ausgabe/bericht.json: Bildqualität und Hinweise je Karte, Meldungen und erzeugte Dateien des
    letzten Laufs. Bei einer Kartenauswahl bleiben die Einträge der übrigen Karten erhalten."""
    pfad = Path(ausgabe) / "bericht.json"
    alt = {}
    if auswahl and pfad.exists():
        try:
            alt = json.loads(pfad.read_text(encoding="utf-8")).get("karten", {})
        except (ValueError, OSError):
            alt = {}
    eintraege = dict(alt)
    for k in karten:
        eintraege[k["bild"]] = dict(nr=k["nr"], de=k["de"], es=k["es"], text_warnung=k.get("text_warnung"),
                                    text_warnung_code=k.get("text_warnung_code"), **k.get("bild_info", {}))
    bericht = dict(version=VERSION, zeit=time.strftime("%Y-%m-%d %H:%M:%S"), qualitaet=cfg.qualitaet, ki=cfg.ki,
                   sprache=getattr(cfg, "sprache", "es"),
                   ki_methode=ki_methode(cfg.ki),
                   format=cfg.kuerzel, auswahl=sorted(auswahl) if auswahl else None, karten=eintraege,
                   meldungen=meldungen, erzeugt=erzeugt)
    pfad.write_text(json.dumps(bericht, ensure_ascii=False, indent=1), encoding="utf-8")
    return pfad


# =============================================================================================
# Hauptprogramm
# =============================================================================================
def parse_format(text):
    try:
        b, h = (float(t) for t in str(text).lower().replace(",", ".").split("x"))
    except Exception:
        raise argparse.ArgumentTypeError(T("Format als BREITExHÖHE in mm angeben, z. B. 88x63",
                                           "Give the format as WIDTHxHEIGHT in mm, e.g. 88x63",
                                           "Indica el formato como ANCHOxALTO en mm, p. ej. 88x63"))
    if min(b, h) < 30 or max(b, h) > 200:
        raise argparse.ArgumentTypeError(T("Format muss zwischen 30 und 200 mm liegen",
                                           "The format must be between 30 and 200 mm",
                                           "El formato debe estar entre 30 y 200 mm"))
    return max(b, h), min(b, h)                               # intern immer Querformat


def parse_bildname(text):
    """--bild: nur ein einfacher Dateiname eines Bildes (kein Pfad)."""
    t = str(text or "").strip()
    if not sicherer_name(t) or Path(t).suffix.lower() not in BILD_ENDUNGEN:
        raise argparse.ArgumentTypeError(T(f"'{text}' ist kein Bild-Dateiname (Beispiel: gans-alt.jpg)",
                                           f"'{text}' is not an image file name (example: gans-alt.jpg)",
                                           f"'{text}' no es un nombre de archivo de imagen (ejemplo: gans-alt.jpg)"))
    return t


def parse_auswahl(text):
    """'1,3,5-8' → {1, 3, 5, 6, 7, 8}; leer → None (alle Karten)."""
    if text is None or not str(text).strip():
        return None
    nummern = set()
    for teil in str(text).replace(" ", "").split(","):
        if not teil:
            continue
        m = re.fullmatch(r"(\d+)(?:-(\d+))?", teil)
        if not m:
            raise argparse.ArgumentTypeError(T(f"Kartenauswahl '{text}' nicht verstanden – Beispiel: 1,3,5-8",
                                               f"Card selection '{text}' not understood – example: 1,3,5-8",
                                               f"No se entendió la selección de cartas '{text}'; ejemplo: 1,3,5-8"))
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        nummern.update(range(min(a, b), max(a, b) + 1))
    return nummern or None


def baue_parser():
    """Alle Schalter des Generators. Die Oberfläche (gans_ui.py) liest diese Liste aus und baut daraus ihre
    Bedienelemente – ein neuer Schalter hier erscheint dort automatisch. Gruppen = Abschnitte der Oberfläche;
    label/einheit/auswahl_labels/help sind Beschriftungen, als L(deutsch, englisch, spanisch) oder als Text."""
    beispiele = [("", L("alles erzeugen (Standard)", "generate everything (default)", "generar todo (predeterminado)")),
                 ("--nur pruefbogen", L("nur den Prüfbogen (schnelle Kontrolle)", "only the proof sheet (quick check)",
                                        "solo la hoja de control (revisión rápida)")),
                 ("--karten 11-14", L("nur die Karten 11 bis 14 (z. B. neue)", "only cards 11 to 14 (e.g. new ones)",
                                      "solo las cartas 11 a 14 (p. ej. nuevas)")),
                 ("--sprache ja", L("Rückseite auf Japanisch (Sprachpaket nötig)", "back in Japanese (language pack needed)",
                                    "reverso en japonés (requiere paquete de idioma)")),
                 ("--ki fsrcnn", L("schnelle statt beste KI-Vergrößerung", "fast instead of best AI upscaling",
                                   "ampliación con IA rápida en vez de la mejor")),
                 ("--hochkant", L("Druckerei-Datei im Hochformat (wenn die Vorlage der Druckerei das verlangt)",
                                  "print-shop file in portrait (if the print shop's template asks for it)",
                                  "archivo de imprenta en vertical (si la plantilla de la imprenta lo pide)")),
                 ("--format 74x52", L("anderes Endformat (A8 quer)", "another final size (A8 landscape)",
                                      "otro tamaño final (A8 horizontal)"))]
    ap = argparse.ArgumentParser(
        description=f"{PRODUKT} – " + T("erzeugt druckfertige Lernkarten-PDFs aus Bildern + karten.csv",
                                        "creates print-ready flashcard PDFs from images + karten.csv",
                                        "crea PDF de tarjetas listas para imprimir a partir de imágenes + karten.csv"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=T("Beispiele:", "Examples:", "Ejemplos:") + "\n"
               + "".join(f"  python3 gans_lernkarten.py {a:<20} {text_in(b)}\n" for a, b in beispiele)
               + T("Oberfläche", "Interface", "Interfaz") + ": python3 gans_ui.py   ·   "
               + T("KI-Modell laden", "Load AI model", "Cargar modelo de IA") + ": python3 ki_modelle.py --laden realesrgan-x4plus")

    def gruppe(titel, beschreibung=None, erweitert=False, reiter="erzeugen"):
        """reiter: in welchem Reiter der Oberfläche die Gruppe erscheint ('erzeugen' oder 'bildverbesserung')."""
        g = ap.add_argument_group(text_in(titel), text_in(beschreibung) if beschreibung else None)
        g.ui_titel, g.ui_beschreibung, g.ui_erweitert, g.ui_reiter = titel, beschreibung, erweitert, reiter
        return g

    def opt(g, *flags, label, einheit=None, auswahl_labels=None, help="", ui_art=None, intern=False, **kw):
        """ui_art: eigenes Bedienelement in der Oberfläche (z. B. 'gansbild' = Knopf zum Laden eines Bildes);
        intern=True: nur für die Oberfläche selbst (z. B. Bildauswahl im Reiter Bildverbesserung), kein Feld."""
        lab, hil = text_in(label), text_in(help)
        act = g.add_argument(*flags, help=f"{lab}{f' ({einheit})' if einheit else ''}: {hil}" if hil else lab, **kw)
        act.ui_label, act.ui_einheit, act.ui_hilfe = label, einheit, help
        act.ui_auswahl_labels = auswahl_labels or {}
        act.ui_art, act.ui_intern = ui_art, intern
        return act

    g = gruppe(L("Was erzeugen", "What to generate", "Qué generar"))
    opt(g, "--nur", choices=["alles", "druckerei", "bogen", "pruefbogen", "vorlagen", "verbessern", "digital"],
        default="alles", label=L("Was erzeugen", "What to generate", "Qué generar"),
        help=L("nur einen Teil erzeugen („verbessern“: nur die Bilder verbessern, ohne Druckdateien; „digital“: "
               "Lernkarten für Anki, die Lernseite und Bildschirm-PDF)",
               "generate only one part (“verbessern”: only enhance the images, no print files; “digital”: flashcards "
               "for Anki, the study page and screen PDF)",
               "generar solo una parte («verbessern»: solo mejorar las imágenes, sin archivos de impresión; «digital»: "
               "tarjetas para Anki, la página de estudio y PDF de pantalla)"),
        auswahl_labels={"alles": L("Alles zum Drucken", "Everything for print", "Todo para imprimir"),
                        "druckerei": L("Druckerei-PDF", "Print-shop PDF", "PDF para imprenta"),
                        "bogen": L("Heimdruck", "Home print", "Impresión en casa"),
                        "pruefbogen": L("Prüfbogen", "Proof sheet", "Hoja de control"),
                        "vorlagen": L("Leere Vorlagen", "Blank templates", "Plantillas vacías"),
                        "verbessern": L("Nur Bilder verbessern", "Enhance images only", "Solo mejorar imágenes"),
                        "digital": L("Digitale Lernkarten", "Digital flashcards", "Tarjetas digitales")})
    opt(g, "--karten", type=parse_auswahl, default=None, metavar="AUSWAHL",
        label=L("Nur diese Karten", "Only these cards", "Solo estas cartas"),
        help=L("Kartennummern, z. B. 1,3,5-8 – leer = alle Karten", "card numbers, e.g. 1,3,5-8 – empty = all cards",
               "números de carta, p. ej. 1,3,5-8; vacío = todas"))
    opt(g, "--bild", type=parse_bildname, action="append", default=None, metavar="DATEI", intern=True,
        label=L("Nur diese Bilder", "Only these images", "Solo estas imágenes"),
        help=L("Dateiname eines Bildes aus dem Bilderordner, mehrfach möglich (z. B. --bild gans-alt.jpg) – "
               "wählt Karten nach Bild statt nach Nummer",
               "file name of an image in the image folder, can be repeated (e.g. --bild gans-alt.jpg) – selects cards "
               "by image instead of number",
               "nombre de una imagen de la carpeta de imágenes, se puede repetir (p. ej. --bild gans-alt.jpg); "
               "elige cartas por imagen en lugar de número"))

    g = gruppe(L("Bildverbesserung", "Image enhancement", "Mejora de imagen"), reiter="bildverbesserung")
    opt(g, "--qualitaet", choices=list(QUALITAET), default="standard", label=L("Qualität", "Quality", "Calidad"),
        help=L("Aus: nur auf Größe bringen. Standard: Empfehlung. Stark: kräftigere Farben und Schärfe.",
               "Off: resize only. Standard: recommended. Strong: stronger colours and sharpness.",
               "Apagado: solo cambiar tamaño. Estándar: recomendado. Fuerte: colores y nitidez más intensos."),
        auswahl_labels={"aus": L("Aus", "Off", "Apagado"), "standard": L("Standard", "Standard", "Estándar"),
                        "stark": L("Stark", "Strong", "Fuerte")})
    opt(g, "--ki", choices=KI_AUSWAHL, default="auto", label=L("KI-Vergrößerung", "AI upscaling", "Ampliación con IA"),
        help=L("Auto: bestes vorhandenes Modell (Real-ESRGAN, sonst FSRCNN). Real-ESRGAN: beste Qualität, braucht "
               "pro Bild 1–4 Minuten (nur beim ersten Mal). FSRCNN: schnell, schwächer. Aus: ohne KI.",
               "Auto: best installed model (Real-ESRGAN, else FSRCNN). Real-ESRGAN: best quality, takes 1–4 minutes "
               "per image (first time only). FSRCNN: fast, weaker. Off: no AI.",
               "Auto: el mejor modelo instalado (Real-ESRGAN, si no FSRCNN). Real-ESRGAN: la mejor calidad, tarda "
               "1–4 minutos por imagen (solo la primera vez). FSRCNN: rápido, más débil. Apagado: sin IA."),
        auswahl_labels={"auto": L("Auto", "Auto", "Auto"), "realesrgan": L("Real-ESRGAN", "Real-ESRGAN", "Real-ESRGAN"),
                        "realesrgan-x2": L("Real-ESRGAN ×2 (schneller)", "Real-ESRGAN ×2 (faster)",
                                           "Real-ESRGAN ×2 (más rápido)"),
                        "fsrcnn": L("FSRCNN (schnell)", "FSRCNN (fast)", "FSRCNN (rápido)"),
                        "aus": L("Aus", "Off", "Apagado")})
    g.add_argument("--ohne-ki", action="store_true", help=argparse.SUPPRESS)     # alter Schalter = --ki aus

    g = gruppe(L("Kartenformat", "Card format", "Formato de carta"))
    opt(g, "--format", type=parse_format, default=(88.0, 63.0), label=L("Endformat", "Final size", "Tamaño final"),
        einheit="mm", help=L("BREITExHÖHE in mm, z. B. 88x63 (Poker) oder 74x52 (A8)",
                             "WIDTHxHEIGHT in mm, e.g. 88x63 (poker) or 74x52 (A8)",
                             "ANCHOxALTO en mm, p. ej. 88x63 (póker) o 74x52 (A8)"))
    opt(g, "--beschnitt", type=float, default=3.0, label=L("Beschnitt", "Bleed", "Sangrado"), einheit="mm",
        help=L("Zugabe rundum für die Druckerei", "extra margin all round for the print shop",
               "margen extra alrededor para la imprenta"))
    opt(g, "--rand", type=float, default=3.5, label=L("Weißer Rand", "White border", "Borde blanco"), einheit="mm",
        help=L("0 = randlose Karten", "0 = borderless cards", "0 = cartas sin borde"))
    opt(g, "--radius", type=float, default=2.5, label=L("Eckenradius", "Corner radius", "Radio de esquina"),
        einheit="mm", help=L("Ecken der Bildfläche", "corners of the image area", "esquinas del área de imagen"))
    opt(g, "--dpi", type=int, default=300, label=L("Auflösung", "Resolution", "Resolución"), einheit="dpi",
        help=L("Druckauflösung der Bilder", "print resolution of the images", "resolución de impresión de las imágenes"))

    g = gruppe(L("Ausrichtung und Rückseite", "Orientation and back", "Orientación y reverso"))
    opt(g, "--hochkant", action="store_true", label=L("Druckerei-Datei hochkant", "Print-shop file portrait",
                                                      "Archivo de imprenta vertical"),
        help=L("Hochformat-Seiten, wenn die Vorlage der Druckerei das verlangt; Inhalt gedreht, Rückseite 180° versetzt",
               "portrait pages if the print shop's template asks for it; content rotated, back offset by 180°",
               "páginas verticales si la plantilla de la imprenta lo pide; contenido girado, reverso desfasado 180°"))
    opt(g, "--rs-drehen", action="store_true", label=L("Rückseite um 180° drehen", "Rotate back by 180°",
                                                       "Girar el reverso 180°"),
        help=L("wenn der Probedruck die Rückseite kopfüber zeigt", "if the test print shows the back upside down",
               "si la prueba de impresión muestra el reverso al revés"))
    opt(g, "--gans-bild", default=None, metavar="DATEI", ui_art="gansbild",
        label=L("Gänse-Bild der Rückseite", "Goose image on the back", "Imagen del ganso en el reverso"),
        help=L("Hintergrund der Rückseite statt der gezeichneten Gans. In der Oberfläche per Knopf laden; "
               "Befehlszeile: Pfad zu einem Bild (Standard: assets/gans_hintergrund.png bzw. .jpg, falls vorhanden)",
               "background of the back instead of the drawn goose. Load it with the button in the interface; command "
               "line: path to an image (default: assets/gans_hintergrund.png or .jpg, if present)",
               "fondo del reverso en lugar del ganso dibujado. En la interfaz se carga con el botón; en la línea de "
               "comandos: ruta a una imagen (predeterminado: assets/gans_hintergrund.png o .jpg, si existe)"))

    opt(g, "--sprachkuerzel", choices=["auto", "an", "aus"], default="auto",
        label=L("Sprachkürzel drucken", "Print language code", "Imprimir código de idioma"),
        help=L("kleines Kürzel der Sprache (z. B. JA) oben links auf der Rückseite – Auto: nur, wenn die Rückseite nicht "
               "Spanisch ist", "small language code (e.g. JA) in the top left of the back – Auto: only if the back "
               "isn’t Spanish", "código pequeño del idioma (p. ej. JA) arriba a la izquierda del reverso; Auto: solo si "
               "el reverso no está en español"),
        auswahl_labels={"auto": L("Auto", "Auto", "Auto"), "an": L("An", "On", "Sí"), "aus": L("Aus", "Off", "No")})
    opt(g, "--sprache", choices=_sprach_codes(), default="es", metavar="CODE", intern=True,
        label=L("Sprache der Rückseite", "Language of the back", "Idioma del reverso"),
        help=L("Spalte der Kartenliste für die Rückseite (Standard es = Spanisch); bei einer anderen Sprache bekommen "
               "die Dateien die Endung _<code>, z. B. …_ja.pdf", "column of the card list for the back (default es = "
               "Spanish); for another language the files get the suffix _<code>, e.g. …_ja.pdf",
               "columna de la lista para el reverso (predeterminado es = español); con otro idioma los archivos "
               "llevan el sufijo _<código>, p. ej. …_ja.pdf"))

    g = gruppe(L("Digitale Lernkarten", "Digital flashcards", "Tarjetas digitales"),
               L("Für „Digitale Lernkarten“: Lernen am Rechner und am Handy", "For “Digital flashcards”: study on "
                 "computer and phone", "Para «Tarjetas digitales»: estudiar en la computadora y el celular"))
    opt(g, "--digital", choices=["empfohlen", "apkg", "html", "pdf", "csv", "alle"], default="empfohlen",
        label=L("Formate", "Formats", "Formatos"),
        help=L("Empfohlen: Anki-Paket (.apkg, auch AnkiDroid/AnkiMobile), Lernseite (HTML, offline im Browser am Rechner) "
               "und Bildschirm-PDF. CSV: Tabellen für Quizlet, Brainscape, Mochi & Co.",
               "Recommended: Anki package (.apkg, also AnkiDroid/AnkiMobile), study page (HTML, offline in the "
               "browser on your computer) and screen PDF. CSV: tables for Quizlet, Brainscape, Mochi & co.",
               "Recomendado: paquete de Anki (.apkg, también AnkiDroid/AnkiMobile), página de estudio (HTML, sin "
               "conexión en el navegador de la computadora) y PDF de pantalla. CSV: tablas para Quizlet, Brainscape, "
               "Mochi y más."),
        auswahl_labels={"empfohlen": L("Empfohlen (Anki + Lernseite + PDF)", "Recommended (Anki + study page + PDF)",
                                       "Recomendado (Anki + página + PDF)"),
                        "apkg": L("Nur Anki (.apkg)", "Anki only (.apkg)", "Solo Anki (.apkg)"),
                        "html": L("Nur Lernseite (HTML)", "Study page only (HTML)", "Solo página de estudio (HTML)"),
                        "pdf": L("Nur Bildschirm-PDF", "Screen PDF only", "Solo PDF de pantalla"),
                        "csv": L("Tabellen für andere Apps (CSV)", "Tables for other apps (CSV)",
                                 "Tablas para otras apps (CSV)"),
                        "alle": L("Alle Formate", "All formats", "Todos los formatos")})
    opt(g, "--deck", default="Me Goos-ta Deutsch", label=L("Name des Stapels", "Deck name", "Nombre del mazo"),
        help=L("So heißt der Stapel in Anki und auf der Lernseite", "the deck's name in Anki and on the study page",
               "así se llama el mazo en Anki y en la página de estudio"))

    g = gruppe(L("Heimdruck", "Home print", "Impresión en casa"),
               L("Papier und Raster für das Drucken zu Hause", "Paper and grid for printing at home",
                 "Papel y cuadrícula para imprimir en casa"))
    opt(g, "--papier", choices=list(PAPIER), default="a4", label=L("Papier", "Paper", "Papel"),
        help=L("A4 fast überall; Letter in den USA, Kanada, Mexiko und Teilen Lateinamerikas (gilt auch für den "
               "Prüfbogen)", "A4 almost everywhere; Letter in the USA, Canada, Mexico and parts of Latin America "
               "(also used for the proof sheet)", "A4 casi en todo el mundo; Carta (Letter) en EE. UU., Canadá, "
               "México y parte de Latinoamérica (también para la hoja de control)"),
        auswahl_labels={"a4": L("A4 (210 × 297 mm)", "A4 (210 × 297 mm)", "A4 (210 × 297 mm)"),
                        "letter": L("Letter (8,5 × 11 in)", "Letter (8.5 × 11 in)", "Carta (8,5 × 11 in)")})
    opt(g, "--abstand", type=float, default=0.0, label=L("Abstand zwischen Karten", "Gap between cards",
                                                         "Separación entre cartas"), einheit="mm",
        help=L("0 = Karten stoßen aneinander", "0 = cards touch each other", "0 = las cartas se tocan"))
    opt(g, "--spalten", type=int, default=0, label=L("Spalten je Bogen", "Columns per sheet", "Columnas por hoja"),
        help=L("0 = automatisch", "0 = automatic", "0 = automático"))
    opt(g, "--zeilen", type=int, default=0, label=L("Zeilen je Bogen", "Rows per sheet", "Filas por hoja"),
        help=L("0 = automatisch", "0 = automatic", "0 = automático"))
    opt(g, "--versatz-x", type=float, default=0.0, label=L("Versatz waagerecht", "Horizontal offset",
                                                           "Desplazamiento horizontal"), einheit="mm",
        help=L("gleicht Druckerversatz aus (+ = nach rechts)", "compensates printer offset (+ = to the right)",
               "compensa el desfase de la impresora (+ = a la derecha)"))
    opt(g, "--versatz-y", type=float, default=0.0, label=L("Versatz senkrecht", "Vertical offset",
                                                           "Desplazamiento vertical"), einheit="mm",
        help=L("gleicht Druckerversatz aus (+ = nach oben)", "compensates printer offset (+ = upwards)",
               "compensa el desfase de la impresora (+ = hacia arriba)"))

    g = gruppe(L("Ausgabe", "Output", "Salida"))
    opt(g, "--ohne-png", action="store_true", label=L("Keine Einzelbilder", "No single images",
                                                      "Sin imágenes individuales"),
        help=L("keine PNG-Datei je Kartenseite erzeugen", "do not create a PNG file per card side",
               "no crear un PNG por cada lado de carta"))
    opt(g, "--ohne-cache", action="store_true", label=L("Alle Bilder neu berechnen", "Recalculate all images",
                                                        "Recalcular todas las imágenes"),
        help=L("Zwischenspeicher ignorieren", "ignore the cache", "ignorar la memoria intermedia"))

    g = gruppe(L("Ordner", "Folders", "Carpetas"),
               L("Nur ändern, wenn Dateien woanders liegen sollen", "Only change if files should live elsewhere",
                 "Cámbialo solo si los archivos deben estar en otro lugar"), erweitert=True)
    opt(g, "--csv", default=str(HIER / "karten.csv"), label=L("Kartenliste", "Card list", "Lista de cartas"),
        help=L("Pfad zu karten.csv", "path to karten.csv", "ruta a karten.csv"))
    opt(g, "--bilder", default=str(HIER / "bilder"), label=L("Bilderordner", "Image folder", "Carpeta de imágenes"),
        help=L("Ordner mit den Vorderseiten-Bildern", "folder with the front images", "carpeta con las imágenes del anverso"))
    opt(g, "--ausgabe", default=str(HIER / "ausgabe"), label=L("Ausgabeordner", "Output folder", "Carpeta de salida"),
        help=L("Zielordner für PDFs und Einzelbilder", "target folder for PDFs and single images",
               "carpeta de destino para PDF e imágenes individuales"))
    opt(g, "--vorlagen-ordner", default=str(HIER / "vorlagen"), label=L("Vorlagenordner", "Template folder",
                                                                        "Carpeta de plantillas"),
        help=L("Zielordner für leere Vorlagen", "target folder for blank templates",
               "carpeta de destino para plantillas vacías"))

    ap.add_argument("--version", action="version", version=f"{PRODUKT} {VERSION}")
    return ap


def _sprach_codes():
    try:
        import sprachen
        return list(sprachen.SPRACHEN)
    except Exception:  # noqa: BLE001
        return ["es"]


def argumente(argv=None):
    return baue_parser().parse_args(argv)


def konfig_aus(a):
    """Konfig aus den geparsten Schaltern (auch von der Oberfläche genutzt)."""
    gans_bild = a.gans_bild
    if not gans_bild:
        kandidaten = [HIER / "assets" / n for n in ("gans_hintergrund.png", "gans_hintergrund.jpg")]
        gans_bild = next((str(p) for p in kandidaten if p.exists()), None)
    return Konfig(b=a.format[0], h=a.format[1], beschnitt=a.beschnitt, rand=a.rand, radius=a.radius, dpi=a.dpi,
                  qualitaet=a.qualitaet, ki="aus" if a.ohne_ki else a.ki, hochkant=a.hochkant, rs_drehen=a.rs_drehen,
                  gans_bild=gans_bild, abstand=a.abstand, spalten=a.spalten, zeilen=a.zeilen,
                  versatz_x=a.versatz_x, versatz_y=a.versatz_y, papier=getattr(a, "papier", "a4"),
                  sprache=getattr(a, "sprache", "es") or "es", sprachkuerzel=getattr(a, "sprachkuerzel", "auto") or "auto")


def nur_verbessern(a, cfg, ausgabe, melde, t0):
    """--nur verbessern: bereitet nur die Vorderseiten auf (Zwischenspeicher ausgabe/.cache), ohne Druckdateien –
    für den Reiter „Bildverbesserung“ der Oberfläche. Auch ausgeschaltete und noch unbeschriftete Karten.
    Auswahl mit --bild NAME (mehrfach) oder --karten; ohne Auswahl alle Bilder der Kartenliste."""
    karten = bilder_der_karten(a.csv, a.bilder)
    meldungen = []
    if a.bild:
        gewuenscht = list(dict.fromkeys(a.bild))
        vorhanden = {k["bild"] for k in karten}
        for b in gewuenscht:
            if b not in vorhanden:
                meldungen.append(meldung("bild_unbekannt", bild=b, ordner=Path(a.bilder).name)["text"])
        karten = [k for k in karten if k["bild"] in set(gewuenscht)]
    if a.karten:
        karten = [k for k in karten if k["nr"] in a.karten]
    if not karten:
        for m in meldungen:
            melde("  ! " + m)
        melde(T("Achtung: keine Bilder zum Verbessern gefunden – schau kurz nach Auswahl, Kartenliste und Bilderordner.",
                "Heads-up: no images to enhance found – have a quick look at the selection, the card list and the "
                "image folder.",
                "Atención: no se encontraron imágenes para mejorar; revisa rápido la selección, la lista y la carpeta "
                "de imágenes."))
        return 1
    methode = ki_methode(cfg.ki)
    if cfg.ki in KI_MODELLE and methode != KI_MODELLE[cfg.ki]:
        meldungen.append(meldung("ki_fehlt", gewaehlt=cfg.ki, benutzt=METHODE_NAME[methode])["text"])
    if QUALITAET.get(cfg.qualitaet) is None:
        name = T("nur auf Druckgröße gebracht (Qualität „Aus“)", "resized only (quality “Off”)",
                 "solo ajustadas al tamaño (calidad «Apagado»)")
    else:
        name = METHODE_NAME[methode]
    melde(T(f"  {len(karten)} Bilder werden verbessert ({name}) …", f"  Enhancing {len(karten)} images ({name}) …",
            f"  Mejorando {len(karten)} imágenes ({name}) …"))
    neu = bereite_vorderseiten_vor(karten, cfg, ausgabe / ".cache", cache=not a.ohne_cache, aufraeumen=False,
                                   melde=melde, einzeln=True)
    alt = len(karten) - neu
    melde(T(f"  {neu} Bilder neu verbessert, {alt} waren schon verbessert (Zwischenspeicher)",
            f"  {neu} images newly enhanced, {alt} were already enhanced (cache)",
            f"  {neu} imágenes mejoradas ahora, {alt} ya estaban mejoradas (memoria intermedia)"))
    for k in karten:
        if k["bild_info"]["ppi"] < 120:
            meldungen.append(meldung("ppi_gering", nr=k["nr"] or "–", bild=k["bild"], ppi=k["bild_info"]["ppi"])["text"])
    for m in meldungen:
        melde("  ! " + m)
    melde(T(f"Fertig in {time.time() - t0:.1f} s – super gemacht!", f"Done in {time.time() - t0:.1f} s – well done!",
            f"Listo en {time.time() - t0:.1f} s. ¡Bien hecho!"))
    return 0


def sprach_endung(code):
    """Dateinamen-Endung je Sprache der Rückseite: Spanisch ohne (wie immer), sonst „_<code>“."""
    return "" if not code or code == "es" else f"_{code}"


def ausgabe_namen(cfg):
    """Dateinamen der Druckdateien (auch von der Oberfläche genutzt). Spanisch unverändert, sonst mit _<code>."""
    e = sprach_endung(getattr(cfg, "sprache", "es"))
    return dict(druckerei=f"{DATEI_PRAEFIX}_Druckerei_{cfg.kuerzel}{'_hochkant' if cfg.hochkant else ''}{e}.pdf",
                bogen=f"{DATEI_PRAEFIX}_Heimdruck_{papier_mm(cfg)[2]}_{cfg.kuerzel}{e}.pdf",
                pruefbogen=f"{DATEI_PRAEFIX}_Pruefbogen{e}.pdf", einzelbilder=f"einzelbilder{e}")


def main(argv=None):
    t0 = time.time()
    for strom in (sys.stdout, sys.stderr):                # Umlaute & Sonderzeichen auch in alten Windows-Konsolen
        try:
            strom.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    a = argumente(argv)
    cfg = konfig_aus(a)
    ausgabe, vorl = Path(a.ausgabe), Path(a.vorlagen_ordner)
    ausgabe.mkdir(parents=True, exist_ok=True)
    namen = ausgabe_namen(cfg)
    melde = lambda t: print(t, flush=True)                                  # noqa: E731

    melde(f"{PRODUKT} – Generator {VERSION}")
    schriften = registriere_schriften()
    if "nicht eingebettet" in schriften["bold"]:
        melde(T("  Hinweis: keine TTF-Schrift gefunden – Poppins-Bold.ttf und Poppins-Medium.ttf in schrift/ ablegen.",
                "  Note: no TTF font found – put Poppins-Bold.ttf and Poppins-Medium.ttf into schrift/.",
                "  Aviso: no se encontró una fuente TTF; coloca Poppins-Bold.ttf y Poppins-Medium.ttf en schrift/."))
    erzeugt = []

    if a.nur in ("alles", "vorlagen"):
        vorl.mkdir(parents=True, exist_ok=True)
        p1 = vorl / f"VORLAGE_Druckerei_{cfg.kuerzel}_{'hochkant' if cfg.hochkant else 'quer'}.pdf"
        p2 = vorl / f"VORLAGE_Heimdruck_{papier_mm(cfg)[2]}_{cfg.kuerzel}.pdf"
        baue_druckerei(cfg, None, p1, vorlage=True)
        baue_bogen(cfg, None, p2, vorlage=True)
        erzeugt += [T("Vorlagen:       ", "Templates:      ", "Plantillas:     ") + f"{vorl.name}/{p1.name}, {p2.name}"]
        if a.nur == "vorlagen":
            melde("\n".join("  " + e for e in erzeugt))
            melde(T(f"Fertig in {time.time() - t0:.1f} s – super gemacht!", f"Done in {time.time() - t0:.1f} s – well done!",
                    f"Listo en {time.time() - t0:.1f} s. ¡Bien hecho!"))
            return 0

    if a.nur == "verbessern":
        return nur_verbessern(a, cfg, ausgabe, melde, t0)

    karten, meldungen = lies_karten(a.csv, a.bilder, sprache=cfg.sprache)
    if cfg.sprache != "es":
        s_ = satz(cfg.sprache)
        melde(T(f"  Rückseite auf {zs_name('de', cfg.sprache)} (Spalte „{cfg.sprache}“)",
                f"  Back in {zs_name('en', cfg.sprache)} (column “{cfg.sprache}”)",
                f"  Reverso en {zs_name('es', cfg.sprache)} (columna «{cfg.sprache}»)"))
        if not s_.voll:
            meldungen.append(meldung("schrift_fehlt", zs=zs_name(code=cfg.sprache))["text"])
        elif s_.braucht_formen and not s_.hb:
            meldungen.append(meldung("formen_fehlt", zs=zs_name(code=cfg.sprache))["text"])
    if a.karten:
        vorhanden = {k["nr"] for k in karten}
        fehlend = sorted(a.karten - vorhanden)
        if fehlend:
            meldungen.append(meldung("karte_fehlt", nummern=", ".join(map(str, fehlend)), anzahl=len(karten))["text"])
        karten = [k for k in karten if k["nr"] in a.karten]
    if a.bild:
        gewuenscht = set(a.bild)
        for b in sorted(gewuenscht - {k["bild"] for k in karten}):
            meldungen.append(meldung("bild_unbekannt", bild=b, ordner=Path(a.bilder).name)["text"])
        karten = [k for k in karten if k["bild"] in gewuenscht]
    teilauswahl = bool(a.karten or a.bild)
    if not karten:
        for m in meldungen:
            melde("  ! " + m)
        melde(T("Achtung: noch keine gültigen Karten gefunden – schau kurz nach karten.csv, Bilderordner und "
                "Kartenauswahl.",
                "Heads-up: no valid cards found yet – have a quick look at karten.csv, the image folder and the card "
                "selection.",
                "Atención: todavía no hay cartas válidas; revisa rápido karten.csv, la carpeta de imágenes y la "
                "selección."))
        return 1
    meldungen += pruefe_texte(karten, cfg)
    methode = ki_methode(cfg.ki)
    if cfg.ki in KI_MODELLE and methode != KI_MODELLE[cfg.ki]:
        meldungen.append(meldung("ki_fehlt", gewaehlt=cfg.ki, benutzt=METHODE_NAME[methode])["text"])
    melde(T(f"  {len(karten)} Karten werden aufbereitet (Bildverbesserung: {METHODE_NAME[methode]}) …",
            f"  Preparing {len(karten)} cards (image enhancement: {METHODE_NAME[methode]}) …",
            f"  Preparando {len(karten)} cartas (mejora de imagen: {METHODE_NAME[methode]}) …"))
    neu = bereite_vorderseiten_vor(karten, cfg, ausgabe / ".cache", cache=not a.ohne_cache, aufraeumen=not teilauswahl,
                                   melde=melde)
    auswahl = ", ".join(str(k["nr"]) for k in karten) if teilauswahl else ""
    melde(T(f"  {len(karten)} Karten gelesen{f' (Auswahl: {auswahl})' if auswahl else ''} · {neu} Bilder neu "
            f"aufbereitet, {len(karten) - neu} aus dem Zwischenspeicher (Qualität „{cfg.qualitaet}“)",
            f"  {len(karten)} cards read{f' (selection: {auswahl})' if auswahl else ''} · {neu} images newly "
            f"prepared, {len(karten) - neu} from the cache (quality “{cfg.qualitaet}”)",
            f"  {len(karten)} cartas leídas{f' (selección: {auswahl})' if auswahl else ''} · {neu} imágenes "
            f"preparadas, {len(karten) - neu} de la memoria intermedia (calidad «{cfg.qualitaet}»)"))
    for k in karten:
        if k["bild_info"]["ppi"] < 120:
            meldungen.append(meldung("ppi_gering", nr=k["nr"], bild=k["bild"], ppi=k["bild_info"]["ppi"])["text"])

    if a.nur == "digital":                                  # Lernkarten für Anki, Lernseite, Bildschirm-PDF, Tabellen
        import lernkarten_digital
        namen_digital = {"apkg": T("Anki (.apkg):   ", "Anki (.apkg):   ", "Anki (.apkg):   "),
                         "html": T("Lernseite:      ", "Study page:     ", "Página estudio: "),
                         "pdf": T("Bildschirm-PDF: ", "Screen PDF:     ", "PDF pantalla:   "),
                         "csv": T("Tabellen:       ", "Tables:         ", "Tablas:         ")}
        for fmt, pfad, anzahl in lernkarten_digital.erzeuge(karten, cfg, ausgabe, a.digital, a.deck, sprache(),
                                                            sys.modules[__name__]):
            erzeugt.append(namen_digital[fmt] + f"{ausgabe.name}/{lernkarten_digital.ORDNER}/{pfad.name}" +
                           T(f"  ({anzahl} Karten)", f"  ({anzahl} cards)", f"  ({anzahl} cartas)"))

    if a.nur in ("alles", "druckerei"):
        p = ausgabe / namen["druckerei"]
        baue_druckerei(cfg, karten, p)
        erzeugt.append(T("Druckerei-PDF:  ", "Print-shop PDF: ", "PDF imprenta:   ") + p.name +
                       T(f"  ({2 * len(karten)} Seiten, abwechselnd Vorder-/Rückseite)",
                         f"  ({2 * len(karten)} pages, alternating front/back)",
                         f"  ({2 * len(karten)} páginas, anverso y reverso alternados)"))
        if not a.ohne_png:
            if exportiere_png(p, ausgabe / namen["einzelbilder"], karten, cfg.dpi, alle=not teilauswahl):
                erzeugt.append(T("Einzelbilder:   ", "Single images:  ", "Imágenes:       ") +
                               f"{ausgabe.name}/{namen['einzelbilder']}/  ({2 * len(karten)} PNG, {cfg.dpi} dpi)")
            else:
                meldungen.append(meldung("png_fehlt")["text"])
    if a.nur in ("alles", "bogen"):
        p = ausgabe / namen["bogen"]
        baue_bogen(cfg, karten, p)
        sp, ze, *_ = raster(cfg)
        pname = papier_mm(cfg)[2]
        erzeugt.append(T("Heimdruck-PDF:  ", "Home-print PDF: ", "PDF casa:       ") + p.name +
                       T(f"  ({sp} × {ze} = {sp * ze} Karten je {pname}-Bogen)",
                         f"  ({sp} × {ze} = {sp * ze} cards per {pname} sheet)",
                         f"  ({sp} × {ze} = {sp * ze} cartas por hoja {pname})"))
    if a.nur in ("alles", "pruefbogen"):
        p = ausgabe / namen["pruefbogen"]
        baue_pruefbogen(cfg, karten, p)
        erzeugt.append(T("Prüfbogen:      ", "Proof sheet:    ", "Hoja control:   ") + p.name)

    schreibe_bericht(ausgabe, cfg, karten, meldungen, erzeugt, {k["nr"] for k in karten} if teilauswahl else None)
    for m in meldungen:
        melde("  ! " + m)
    melde("\n".join("  " + e for e in erzeugt))
    melde(T(f"Fertig in {time.time() - t0:.1f} s – super gemacht!", f"Done in {time.time() - t0:.1f} s – well done!",
            f"Listo en {time.time() - t0:.1f} s. ¡Bien hecho!"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
