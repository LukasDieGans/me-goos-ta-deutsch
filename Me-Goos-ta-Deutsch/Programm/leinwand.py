#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ME GOOS-TA DEUTSCH – Pillow-Leinwand                                Version 2.4 (22.10.2026)
=============================================================================================
Ein kleiner Nachbau der ReportLab-Zeichenfläche (canvas) auf einem Pillow-Bild. Damit zeichnet dieselbe Routine wie
der Druck (gans_lernkarten.zeichne_rueckseite) die Rückseiten-Vorschau, wenn pypdfium2 fehlt – vor allem in der
Web-App (Pyodide), aber auch, wenn Windows die DLL von pypdfium2 sperrt.

Unterstützt genau das, was die Kartenzeichnung braucht: saveState/restoreState, translate/scale/rotate, Füll-/Linienfarbe,
Rechteck (auch abgerundet), Kreis, Ellipse, Linie, Pfade mit Bézierkurven, Ausschnitt (clipPath), Bilder und Text mit
TrueType-Schriften (Grundlinie wie in ReportLab). Gezeichnet wird 3-fach überabgetastet und dann verkleinert (weiche
Kanten). Koordinaten wie in ReportLab: Punkte (1/72 Zoll), Ursprung links unten.
"""

from __future__ import annotations

import io
import math

from PIL import Image, ImageChops, ImageDraw, ImageFont

UEBER = 3                       # Überabtastung


def _rgb(farbe):
    if hasattr(farbe, "red"):
        return tuple(max(0, min(255, round(v * 255))) for v in (farbe.red, farbe.green, farbe.blue))
    if isinstance(farbe, str):
        h = farbe.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(int(v) for v in farbe[:3])


class _Pfad:
    """Pfad wie reportlab.pdfgen.pathobject.PDFPathObject (Teilpfade als Punktlisten in Benutzer-Koordinaten;
    zu[i] = Teilpfad i ist geschlossen – offene werden als Linienzug gezeichnet, nicht als Ring)."""

    def __init__(self):
        self.teile, self.akt, self.zu = [], None, []

    def moveTo(self, x, y):
        self.akt = [(x, y)]
        self.teile.append(self.akt)
        self.zu.append(False)

    def lineTo(self, x, y):
        if self.akt is None:
            return self.moveTo(x, y)
        self.akt.append((x, y))

    def curveTo(self, x1, y1, x2, y2, x3, y3, n=16):
        x0, y0 = self.akt[-1]
        for i in range(1, n + 1):
            t = i / n
            u = 1 - t
            self.akt.append((u ** 3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t ** 3 * x3,
                             u ** 3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t ** 3 * y3))

    def close(self):
        if self.akt is not None:
            self.zu[-1] = True
        self.akt = None

    def rect(self, x, y, w, h):
        self.teile.append([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])
        self.zu.append(True)

    def roundRect(self, x, y, w, h, r, n=10):
        r = max(0.0, min(r, abs(w) / 2, abs(h) / 2))
        if r <= 0:
            return self.rect(x, y, w, h)
        punkte = []
        for cx, cy, start in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)):
            for i in range(n + 1):
                a = math.radians(start + 90 * i / n)
                punkte.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        self.teile.append(punkte)
        self.zu.append(True)

    def ellipse(self, x, y, w, h, n=48):
        cx, cy = x + w / 2, y + h / 2
        self.teile.append([(cx + w / 2 * math.cos(2 * math.pi * i / n), cy + h / 2 * math.sin(2 * math.pi * i / n))
                           for i in range(n)])
        self.zu.append(True)

    def circle(self, x, y, r):
        self.ellipse(x - r, y - r, 2 * r, 2 * r)


class _Text:
    """Textobjekt (beginText/textOut/drawText) – Text an der Grundlinie, links ausgerichtet."""

    def __init__(self, x, y, font, groesse):
        self.x, self.y, self.font, self.groesse, self.text = x, y, font, groesse, ""

    def setFont(self, font, groesse, leading=None):
        self.font, self.groesse = font, groesse

    def textOut(self, text):
        self.text += str(text)

    textLine = textOut


class Leinwand:
    """Zeichenfläche w × h Punkte, Ergebnis mit dpi Punkten je Zoll: png() bzw. bild()."""

    def __init__(self, w, h, dpi=110, ueber=UEBER):
        self.w, self.h, self.dpi, self.ueber = w, h, dpi, ueber
        self.k = dpi / 72 * ueber
        self.groesse_px = (max(1, round(w * self.k)), max(1, round(h * self.k)))
        self.bild = Image.new("RGB", self.groesse_px, (255, 255, 255))
        self.zug = ImageDraw.Draw(self.bild)
        self.z = dict(ctm=(1.0, 0.0, 0.0, 1.0, 0.0, 0.0), fuell=(0, 0, 0), linie=(0, 0, 0), breite=1.0, kappe=0,
                      font=None, schrift=10.0, maske=None, basis=None)
        self.stapel = []
        self._fonts = {}

    # ---------- Zustand ----------
    def saveState(self):
        self.stapel.append(self.z)
        self.z = dict(self.z, basis=None)

    def restoreState(self):
        if self.z["basis"] is not None:                       # Ausschnitt dieser Ebene: Außen wieder wie vorher
            self._uebernehmen()
        self.z = self.stapel.pop()

    def _uebernehmen(self):
        neu = self.z["basis"]
        neu.paste(self.bild, (0, 0), self.z["maske"])
        self._setze_bild(neu)

    def _setze_bild(self, bild):
        self.bild = bild
        self.zug = ImageDraw.Draw(self.bild)

    def translate(self, dx, dy):
        a, b, c, d, e, f = self.z["ctm"]
        self.z["ctm"] = (a, b, c, d, a * dx + c * dy + e, b * dx + d * dy + f)

    def scale(self, sx, sy):
        a, b, c, d, e, f = self.z["ctm"]
        self.z["ctm"] = (a * sx, b * sx, c * sy, d * sy, e, f)

    def rotate(self, grad):                                   # gegen den Uhrzeigersinn, wie ReportLab
        a, b, c, d, e, f = self.z["ctm"]
        co, si = math.cos(math.radians(grad)), math.sin(math.radians(grad))
        self.z["ctm"] = (a * co + c * si, b * co + d * si, c * co - a * si, d * co - b * si, e, f)

    def setFillColor(self, farbe, alpha=None):
        self.z["fuell"] = _rgb(farbe)

    def setStrokeColor(self, farbe, alpha=None):
        self.z["linie"] = _rgb(farbe)

    def setLineWidth(self, breite):
        self.z["breite"] = float(breite)

    def setLineCap(self, kappe):
        self.z["kappe"] = int(kappe)

    def setDash(self, *args, **kw):                         # gestrichelt: in der Vorschau durchgezogen
        pass

    def setFont(self, font, groesse, leading=None):
        self.z["font"], self.z["schrift"] = font, float(groesse)

    # ---------- Umrechnung ----------
    def _px(self, x, y):
        a, b, c, d, e, f = self.z["ctm"]
        ux, uy = a * x + c * y + e, b * x + d * y + f
        return ux * self.k, self.groesse_px[1] - uy * self.k

    def _mass(self):
        a, b, c, d, _, _ = self.z["ctm"]
        return math.sqrt(abs(a * d - b * c)) * self.k

    # ---------- Formen ----------
    def _polygone(self, teile, stroke, fill, zu=None):
        for i, t in enumerate(teile):
            pts = [self._px(x, y) for x, y in t]
            if len(pts) < 2:
                continue
            if fill and len(pts) >= 3:
                self.zug.polygon(pts, fill=self.z["fuell"])
            if not stroke:
                continue
            b = max(1, round(self.z["breite"] * self._mass()))
            if zu is None or zu[i]:
                self.zug.line(pts + [pts[0]], fill=self.z["linie"], width=b)
            else:                                                # offener Linienzug (z. B. Welle): runde Gelenke
                self.zug.line(pts, fill=self.z["linie"], width=b, joint="curve")
                self._kappen(pts[0], pts[-1], b)

    def _kappen(self, p1, p2, b):
        if self.z["kappe"] == 1:                                 # runde Enden
            for px, py in (p1, p2):
                self.zug.ellipse([px - b / 2, py - b / 2, px + b / 2, py + b / 2], fill=self.z["linie"])

    def beginPath(self):
        return _Pfad()

    def drawPath(self, pfad, stroke=1, fill=0, fillMode=None):
        self._polygone(pfad.teile, stroke, fill, pfad.zu)

    def rect(self, x, y, w, h, stroke=1, fill=0):
        p = _Pfad()
        p.rect(x, y, w, h)
        self._polygone(p.teile, stroke, fill)

    def roundRect(self, x, y, w, h, r, stroke=1, fill=0):
        p = _Pfad()
        p.roundRect(x, y, w, h, r)
        self._polygone(p.teile, stroke, fill)

    def ellipse(self, x1, y1, x2, y2, stroke=1, fill=0):
        p = _Pfad()
        p.ellipse(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        self._polygone(p.teile, stroke, fill)

    def circle(self, x, y, r, stroke=1, fill=0):
        self.ellipse(x - r, y - r, x + r, y + r, stroke, fill)

    def line(self, x1, y1, x2, y2):
        p1, p2 = self._px(x1, y1), self._px(x2, y2)
        b = max(1, round(self.z["breite"] * self._mass()))
        self.zug.line([p1, p2], fill=self.z["linie"], width=b)
        self._kappen(p1, p2, b)

    def clipPath(self, pfad, stroke=1, fill=0, fillMode=None):
        maske = Image.new("L", self.groesse_px, 0)
        z = ImageDraw.Draw(maske)
        for t in pfad.teile:
            pts = [self._px(x, y) for x, y in t]
            if len(pts) >= 3:
                z.polygon(pts, fill=255)
        if self.z["basis"] is not None:                       # zweiter Ausschnitt auf derselben Ebene
            self._uebernehmen()
        if self.z["maske"] is not None:
            maske = ImageChops.multiply(maske, self.z["maske"])
        self.z["maske"], self.z["basis"] = maske, self.bild.copy()
        self._polygone(pfad.teile, stroke, fill)

    # ---------- Bilder ----------
    def drawImage(self, quelle, x, y, width=None, height=None, mask=None, **kw):
        with Image.open(quelle) as im:
            im.load()
            hat_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
            im = im.convert("RGBA" if hat_alpha else "RGB")
        w, h = width or im.width, height or im.height
        (xa, ya), (xb, yb) = self._px(x, y), self._px(x + w, y + h)
        links, oben = round(min(xa, xb)), round(min(ya, yb))
        ziel = (max(1, round(abs(xb - xa))), max(1, round(abs(yb - ya))))
        im = im.resize(ziel, Image.LANCZOS)
        self.bild.paste(im, (links, oben), im if hat_alpha else None)

    # ---------- Text ----------
    def _font(self, name, groesse):
        px = max(1, round(groesse * self._mass()))
        schluessel = (name, px)
        if schluessel not in self._fonts:
            f = None
            try:
                from reportlab.pdfbase import pdfmetrics
                pfad = getattr(getattr(pdfmetrics.getFont(name), "face", None), "filename", None)
                if pfad:
                    f = ImageFont.truetype(str(pfad), px)
            except Exception:  # noqa: BLE001 – Standardschrift (Helvetica) oder kein FreeType
                f = None
            if f is None:
                try:
                    f = ImageFont.load_default(px)
                except TypeError:                                # sehr altes Pillow
                    f = ImageFont.load_default()
            self._fonts[schluessel] = f
        return self._fonts[schluessel]

    def _text(self, x, y, text, anker, font=None, groesse=None):
        f = self._font(font or self.z["font"], groesse or self.z["schrift"])
        try:
            self.zug.text(self._px(x, y), str(text), fill=self.z["fuell"], font=f, anchor=anker)
        except ValueError:                                       # Bitmap-Schrift kennt keine Anker
            self.zug.text(self._px(x, y), str(text), fill=self.z["fuell"], font=f)

    def drawString(self, x, y, text, *args, **kw):
        self._text(x, y, text, "ls")

    def drawCentredString(self, x, y, text, *args, **kw):
        self._text(x, y, text, "ms")

    def drawRightString(self, x, y, text, *args, **kw):
        self._text(x, y, text, "rs")

    def beginText(self, x=0, y=0):
        return _Text(x, y, self.z["font"], self.z["schrift"])

    def drawText(self, t):
        self._text(t.x, t.y, t.text, "ls", t.font, t.groesse)

    # ---------- Ergebnis ----------
    def showPage(self):
        pass

    def save(self):
        pass

    def bild_fertig(self):
        while self.stapel:
            self.restoreState()
        groesse = tuple(max(1, math.ceil(v * self.dpi / 72 - 1e-6)) for v in (self.w, self.h))   # wie pypdfium2
        return self.bild.resize(groesse, Image.LANCZOS)

    def png(self):
        aus = io.BytesIO()
        self.bild_fertig().save(aus, "PNG", compress_level=3)
        return aus.getvalue()
