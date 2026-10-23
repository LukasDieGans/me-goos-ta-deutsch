#!/usr/bin/env python3
"""Zeichnet die 10 Beispielbilder von Me Goos-ta Deutsch selbst (lizenzfrei, MIT wie das Programm).
Aufruf: python zeichne_beispielbilder.py <Programm-Ordner> [Zielordner]   (Standard: <Programm>/beispiel-bilder)"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROGRAMM = Path(sys.argv[1])
ZIEL = Path(sys.argv[2]) if len(sys.argv) > 2 else PROGRAMM / "beispiel-bilder"
SCHRIFT = PROGRAMM / "schrift" / "Poppins-Bold.ttf"
B, H = 1200, 840                                              # quer, etwa wie die Karte (957 × 661)


def verlauf(w, h, oben, unten):
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / (h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(oben[i] + (unten[i] - oben[i]) * t) for i in range(3)))
    return im


def koerner(im, staerke=7, saat=1):
    """Leichtes Papierkorn – wirkt wie gedruckt und gibt der KI-Vergrößerung Struktur."""
    rnd = random.Random(saat)
    rausch = Image.effect_noise(im.size, 40).point(lambda v: 128 + (v - 128) * staerke // 40)
    rausch = rausch.filter(ImageFilter.GaussianBlur(0.6))
    return Image.blend(im, Image.merge("RGB", (rausch, rausch, rausch)), 0.06 + rnd.random() * 0.02)


def gans(d, x, y, s=1.0, koerper=(250, 250, 248), schnabel=(247, 160, 40), blick=0, wut=False, zunge=False,
         brille=False, fliege=False, krone=False, tupfen=None, schweiss=False, haare=False):
    """Gezeichnete Gans, (x, y) = Mitte des Körpers, s = Maßstab."""
    k = lambda v: int(v * s)                                   # noqa: E731
    umriss = (40, 45, 60)
    # Beine
    for dx in (-35, 25):
        d.line([(x + k(dx), y + k(85)), (x + k(dx), y + k(160))], fill=schnabel, width=k(12))
        d.polygon([(x + k(dx - 25), y + k(165)), (x + k(dx + 30), y + k(165)), (x + k(dx), y + k(150))], fill=schnabel)
    # Körper und Schwanz
    d.polygon([(x - k(175), y - k(10)), (x - k(235), y - k(70)), (x - k(150), y - k(40))], fill=koerper, outline=umriss)
    d.ellipse([x - k(190), y - k(95), x + k(150), y + k(115)], fill=koerper, outline=umriss, width=k(5))
    if tupfen:
        rnd = random.Random(3)
        for _ in range(14):
            px, py = x + rnd.randint(-k(150), k(110)), y + rnd.randint(-k(60), k(80))
            d.ellipse([px - k(14), py - k(14), px + k(14), py + k(14)], fill=tupfen)
    # Flügel
    d.chord([x - k(120), y - k(50), x + k(70), y + k(80)], 200, 360, fill=tuple(max(0, c - 18) for c in koerper),
            outline=umriss, width=k(4))
    # Hals und Kopf
    hx, hy = x + k(120), y - k(170)
    d.polygon([(x + k(70), y - k(60)), (x + k(140), y - k(55)), (hx + k(30), hy + k(10)), (hx - k(30), hy + k(5))],
              fill=koerper)
    d.line([(x + k(70), y - k(60)), (hx - k(30), hy + k(5))], fill=umriss, width=k(5))
    d.line([(x + k(140), y - k(55)), (hx + k(30), hy + k(10))], fill=umriss, width=k(5))
    d.ellipse([hx - k(55), hy - k(55), hx + k(60), hy + k(50)], fill=koerper, outline=umriss, width=k(5))
    if haare:
        for i in range(3):
            d.arc([hx - k(20) + k(12) * i, hy - k(90), hx + k(20) + k(12) * i, hy - k(45)], 180, 330,
                  fill=(150, 150, 150), width=k(5))
    # Schnabel
    d.polygon([(hx + k(45), hy - k(12)), (hx + k(120), hy + k(5)), (hx + k(45), hy + k(22))], fill=schnabel,
              outline=umriss)
    if zunge:
        d.ellipse([hx + k(70), hy + k(8), hx + k(100), hy + k(40)], fill=(225, 80, 100), outline=umriss)
    # Auge
    ax, ay = hx + k(15), hy - k(12)
    d.ellipse([ax - k(14), ay - k(14), ax + k(14), ay + k(14)], fill="white", outline=umriss, width=k(3))
    d.ellipse([ax - k(6) + k(blick), ay - k(6), ax + k(6) + k(blick), ay + k(6)], fill=umriss)
    if wut:
        d.line([(ax - k(25), ay - k(30)), (ax + k(18), ay - k(14))], fill=umriss, width=k(8))
    if brille:
        d.ellipse([ax - k(24), ay - k(24), ax + k(24), ay + k(24)], outline=(60, 60, 70), width=k(5))
        d.line([(ax - k(24), ay), (hx - k(50), hy - k(5))], fill=(60, 60, 70), width=k(4))
    if fliege:
        fy = hy + k(70)
        d.polygon([(hx - k(40), fy - k(22)), (hx, fy), (hx - k(40), fy + k(22))], fill=(200, 40, 60), outline=umriss)
        d.polygon([(hx + k(40), fy - k(22)), (hx, fy), (hx + k(40), fy + k(22))], fill=(200, 40, 60), outline=umriss)
        d.ellipse([hx - k(9), fy - k(9), hx + k(9), fy + k(9)], fill=(160, 20, 40))
    if krone:
        kx, ky = hx, hy - k(55)
        d.polygon([(kx - k(45), ky), (kx - k(45), ky - k(45)), (kx - k(22), ky - k(20)), (kx, ky - k(55)),
                   (kx + k(22), ky - k(20)), (kx + k(45), ky - k(45)), (kx + k(45), ky)], fill=(245, 196, 60),
                  outline=umriss)
        for px in (-k(30), 0, k(30)):
            d.ellipse([kx + px - k(6), ky - k(16), kx + px + k(6), ky - k(4)], fill=(210, 40, 70))
    if schweiss:
        for i, (px, py) in enumerate([(-k(80), -k(40)), (-k(95), k(5)), (k(75), -k(75))]):
            d.polygon([(hx + px, hy + py - k(18)), (hx + px - k(9), hy + py), (hx + px + k(9), hy + py)],
                      fill=(110, 180, 240))
            d.ellipse([hx + px - k(9), hy + py - k(8), hx + px + k(9), hy + py + k(10)], fill=(110, 180, 240))
    return hx, hy


def text(im, wort):
    d = ImageDraw.Draw(im)
    zeile = f"GANS {wort.upper()}"
    g = 120
    font = ImageFont.truetype(str(SCHRIFT), g)
    while d.textlength(zeile, font=font) > im.width * 0.9 and g > 40:
        g -= 4
        font = ImageFont.truetype(str(SCHRIFT), g)
    w = d.textlength(zeile, font=font)
    d.text(((im.width - w) / 2, im.height - g * 1.45), zeile, font=font, fill="white", stroke_width=max(4, g // 14),
           stroke_fill=(30, 35, 55))


def sonne(d, x, y, r, farbe):
    d.ellipse([x - r, y - r, x + r, y + r], fill=farbe)


def bild(name, wort, hinter, szene, hochkant=False):
    w, h = (H, B) if hochkant else (B, H)
    im = verlauf(w, h, *hinter)
    d = ImageDraw.Draw(im)
    szene(d, w, h)
    im = koerner(im, saat=len(name))
    text(im, wort)
    ZIEL.mkdir(parents=True, exist_ok=True)
    im.save(ZIEL / name, "JPEG", quality=90, optimize=True)
    print("✓", name, im.size)


def boden(d, w, h, farbe):
    d.ellipse([-w // 4, h * 0.62, w * 1.25, h * 1.4], fill=farbe)


def s_abendlich(d, w, h):
    sonne(d, w * 0.78, h * 0.42, 110, (255, 196, 90))
    for i in range(6):
        d.line([(0, h * 0.5 + i * 14), (w, h * 0.5 + i * 14)], fill=(250, 150 - i * 12, 90 + i * 6), width=3)
    boden(d, w, h, (70, 45, 90))
    gans(d, int(w * 0.36), int(h * 0.56), 1.05, koerper=(245, 238, 230))
    for sx, sy in [(120, 80), (260, 140), (520, 60), (640, 130), (900, 70)]:
        d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 250, 220))


def s_adelig(d, w, h):
    for i in range(0, w, 60):
        d.rectangle([i, 0, i + 30, h], fill=(120, 60, 140))
    d.rectangle([w * 0.1, h * 0.72, w * 0.9, h], fill=(170, 30, 60))
    gans(d, int(w * 0.42), int(h * 0.55), 1.0, krone=True, fliege=False)


def s_aggressiv(d, w, h):
    for i in range(12):
        a = i / 12 * 2 * math.pi
        d.line([(w * 0.5, h * 0.42), (w * 0.5 + math.cos(a) * w, h * 0.42 + math.sin(a) * w)], fill=(230, 70, 60),
               width=40)
    boden(d, w, h, (120, 40, 40))
    gans(d, int(w * 0.4), int(h * 0.54), 1.1, wut=True, blick=4)
    d.text((w * 0.72, h * 0.12), "!!", fill=(255, 240, 120), font=ImageFont.truetype(str(SCHRIFT), 150),
           stroke_width=6, stroke_fill=(60, 20, 20))


def s_alt(d, w, h):
    boden(d, w, h, (180, 160, 120))
    d.rectangle([w * 0.72, h * 0.18, w * 0.92, h * 0.5], fill=(150, 110, 70), outline=(80, 60, 40), width=6)
    d.ellipse([w * 0.775, h * 0.25, w * 0.865, h * 0.43], fill=(250, 245, 230), outline=(80, 60, 40), width=5)
    d.line([(w * 0.82, h * 0.34), (w * 0.82, h * 0.28)], fill=(40, 40, 40), width=5)
    d.line([(w * 0.82, h * 0.34), (w * 0.85, h * 0.36)], fill=(40, 40, 40), width=5)
    hx, hy = gans(d, int(w * 0.36), int(h * 0.56), 1.0, koerper=(236, 232, 226), brille=True, haare=True)
    d.line([(w * 0.5, h * 0.52), (w * 0.53, h * 0.8)], fill=(110, 70, 40), width=12)
    d.arc([w * 0.47, h * 0.47, w * 0.53, h * 0.55], 180, 360, fill=(110, 70, 40), width=12)


def s_anders(d, w, h):
    boden(d, w, h, (90, 160, 90))
    for fx in (0.12, 0.88):
        gans(d, int(w * fx), int(h * 0.62), 0.55)
    gans(d, int(w * 0.48), int(h * 0.55), 1.0, koerper=(120, 190, 250), tupfen=(250, 220, 80))


def s_anstaendig(d, w, h):
    boden(d, w, h, (200, 220, 235))
    d.rectangle([w * 0.06, h * 0.12, w * 0.24, h * 0.5], fill=(250, 250, 250), outline=(120, 130, 150), width=5)
    for i in range(4):
        d.line([(w * 0.09, h * (0.2 + i * 0.07)), (w * 0.21, h * (0.2 + i * 0.07))], fill=(150, 160, 180), width=6)
    gans(d, int(w * 0.48), int(h * 0.56), 1.0, fliege=True)


def s_antifaschistisch(d, w, h):
    boden(d, w, h, (230, 230, 230))
    hx, hy = gans(d, int(w * 0.36), int(h * 0.58), 0.95)
    sx, sy = int(w * 0.62), int(h * 0.12)
    d.line([(sx + 200, sy + 260), (sx + 200, h * 0.75)], fill=(120, 80, 50), width=14)
    d.rectangle([sx, sy, sx + 400, sy + 260], fill=(250, 250, 245), outline=(40, 45, 60), width=8)
    f = ImageFont.truetype(str(SCHRIFT), 56)
    for i, z in enumerate(("Alle", "zusammen", "♥")):
        tw = d.textlength(z, font=f) if z != "♥" else 50
        if z == "♥":
            cx, cy = sx + 200, sy + 205
            d.ellipse([cx - 44, cy - 34, cx - 2, cy + 6], fill=(220, 50, 70))
            d.ellipse([cx + 2, cy - 34, cx + 44, cy + 6], fill=(220, 50, 70))
            d.polygon([(cx - 42, cy - 6), (cx + 42, cy - 6), (cx, cy + 40)], fill=(220, 50, 70))
        else:
            d.text((sx + 200 - tw / 2, sy + 20 + i * 70), z, font=f, fill=(40, 45, 60))


def s_arg_hunger(d, w, h):
    boden(d, w, h, (240, 200, 120))
    d.ellipse([w * 0.66, h * 0.62, w * 0.9, h * 0.74], fill=(250, 250, 250), outline=(60, 60, 70), width=6)
    d.ellipse([w * 0.69, h * 0.64, w * 0.87, h * 0.71], fill=(235, 235, 240))
    gans(d, int(w * 0.38), int(h * 0.55), 1.0, blick=6)
    bx, by = w * 0.6, h * 0.1
    d.ellipse([bx, by, bx + 380, by + 180], fill="white", outline=(40, 45, 60), width=6)
    d.polygon([(bx + 60, by + 150), (bx + 20, by + 220), (bx + 110, by + 160)], fill="white", outline=(40, 45, 60))
    d.text((bx + 75, by + 48), "Mampf?", font=ImageFont.truetype(str(SCHRIFT), 60), fill=(40, 45, 60))


def s_aufgeregt(d, w, h):
    for r in range(900, 0, -90):
        d.ellipse([w / 2 - r, h * 0.45 - r, w / 2 + r, h * 0.45 + r], fill=(255, 230 - r // 12, 90 + r // 20))
    gans(d, int(w * 0.42), int(h * 0.55), 1.05, schweiss=True, blick=-4)
    f = ImageFont.truetype(str(SCHRIFT), 120)
    for x, y in [(0.08, 0.1), (0.8, 0.08), (0.86, 0.4)]:
        d.text((w * x, h * y), "!", font=f, fill=(230, 60, 60), stroke_width=5, stroke_fill="white")


def s_aufmuepfig(d, w, h):
    boden(d, w, h, (110, 180, 120))
    for i in range(7):
        d.line([(w * 0.7 + i * 25, h * 0.1), (w * 0.7 + i * 25, h * 0.55)], fill=(150, 110, 70), width=10)
    d.line([(w * 0.68, h * 0.2), (w * 0.98, h * 0.2)], fill=(150, 110, 70), width=10)
    d.line([(w * 0.68, h * 0.45), (w * 0.98, h * 0.45)], fill=(150, 110, 70), width=10)
    gans(d, int(w * 0.38), int(h * 0.55), 1.0, zunge=True, blick=5)


BILDER = [
    ("gans-abendlich.jpg", "abendlich", ((60, 40, 110), (250, 140, 90)), s_abendlich, False),
    ("gans-adelig.jpg", "adelig", ((150, 90, 170), (235, 210, 240)), s_adelig, True),
    ("gans-aggressive.jpg", "aggressiv", ((250, 120, 90), (200, 50, 50)), s_aggressiv, False),
    ("gans-alt.jpg", "alt", ((235, 225, 200), (215, 195, 160)), s_alt, False),
    ("gans-anders.jpg", "anders", ((150, 210, 250), (220, 240, 255)), s_anders, False),
    ("gans-anstaendig.jpg", "anständig", ((170, 200, 230), (235, 245, 250)), s_anstaendig, False),
    ("gans-antifaschistisch.jpg", "antifaschistisch", ((200, 230, 210), (245, 250, 245)), s_antifaschistisch, False),
    ("gans-arg-hunger.jpg", "arg Hunger", ((255, 225, 150), (250, 245, 220)), s_arg_hunger, False),
    ("gans-aufgeregt.jpg", "aufgeregt", ((255, 240, 170), (250, 200, 120)), s_aufgeregt, False),
    ("gans-aufmuepfig.jpg", "aufmüpfig", ((140, 200, 250), (220, 240, 255)), s_aufmuepfig, False),
]

if __name__ == "__main__":
    for name, wort, hinter, szene, hoch in BILDER:
        bild(name, wort, hinter, szene, hoch)
