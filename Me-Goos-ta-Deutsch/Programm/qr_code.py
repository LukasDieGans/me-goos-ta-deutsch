#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ME GOOS-TA DEUTSCH – QR-Code                                        Version 2.5 (23.10.2026)
=============================================================================================
QR-Code ohne Zusatzpaket, Zeile für Zeile wie `qrMatrix()`/`qrSvg()` in ui/index.html (gleiche Matrix für denselben
Text): Byte-Modus, Fehlerkorrektur M, Version 1–6 (bis 106 Zeichen), Reed-Solomon über GF(256) mit 0x11D,
Formatbits BCH(15,5) mit 0x537 und Maske 0x5412, 8 Masken mit Strafpunkten nach der QR-Norm.
Gebraucht für die Installationsdateien der Handy-App (statisches SVG, ohne JavaScript) und deren Prüfung.
"""

from __future__ import annotations

QR_M = {1: (10, 1), 2: (16, 1), 3: (26, 1), 4: (18, 2), 5: (24, 2), 6: (16, 4)}    # Prüfwörter je Block, Blöcke
QR_GESAMT = {1: 26, 2: 44, 3: 70, 4: 100, 5: 134, 6: 172}                          # Codewörter je Version
QR_AUSRICHTUNG = {2: 18, 3: 22, 4: 26, 5: 30, 6: 34}
RAND = 4                                                                           # heller Rand in Modulen

_EXP, _LOG = [0] * 512, [0] * 256
_x = 1
for _i in range(255):
    _EXP[_i], _LOG[_x] = _x, _i
    _x <<= 1
    if _x & 256:
        _x ^= 0x11D
for _i in range(255, 512):
    _EXP[_i] = _EXP[_i - 255]

QR_MASKEN = (lambda c, r: (c + r) % 2 == 0, lambda c, r: r % 2 == 0, lambda c, r: c % 3 == 0,
             lambda c, r: (c + r) % 3 == 0, lambda c, r: (c // 3 + r // 2) % 2 == 0,
             lambda c, r: (c * r) % 2 + (c * r) % 3 == 0, lambda c, r: ((c * r) % 2 + (c * r) % 3) % 2 == 0,
             lambda c, r: ((c + r) % 2 + (c * r) % 3) % 2 == 0)


def _mal(a, b):
    return _EXP[_LOG[a] + _LOG[b]] if a and b else 0


def _rs(daten, n):
    """n Reed-Solomon-Prüfwörter."""
    gen = [1]
    for i in range(n):
        neu = [0] * (len(gen) + 1)
        for j, g in enumerate(gen):
            neu[j] ^= g
            neu[j + 1] ^= _mal(g, _EXP[i])
        gen = neu
    rest = [0] * n
    for d in daten:
        f = d ^ rest.pop(0)
        rest.append(0)
        for j in range(n):
            rest[j] ^= _mal(gen[j + 1], f)
    return rest


def _format(k, n, maske):
    """Stufe M = 00, dann 3 Bit Maske."""
    rest = maske
    for _ in range(10):
        rest = (rest << 1) ^ ((rest >> 9) * 0x537)
    bits = ((maske << 10) | rest) ^ 0x5412
    bit = lambda i: (bits >> i) & 1
    for i in range(6):
        k[i][8] = bit(i)
    k[7][8], k[8][8], k[8][7] = bit(6), bit(7), bit(8)
    for i in range(9, 15):
        k[8][14 - i] = bit(i)
    for i in range(8):
        k[8][n - 1 - i] = bit(i)
    for i in range(8, 15):
        k[n - 15 + i][8] = bit(i)
    k[n - 8][8] = 1


def _strafe(m):
    n, s = len(m), 0
    for z in [*m, *([m[r][c] for r in range(n)] for c in range(n))]:
        lauf = 1
        for i in range(1, n + 1):
            if i < n and z[i] == z[i - 1]:
                lauf += 1
            else:
                if lauf >= 5:
                    s += lauf - 2
                lauf = 1
        t = "".join(map(str, z))
        for muster in ("10111010000", "00001011101"):
            p = t.find(muster)
            while p >= 0:
                s += 40
                p = t.find(muster, p + 1)
    for r in range(n - 1):
        for c in range(n - 1):
            v = m[r][c]
            if v == m[r][c + 1] == m[r + 1][c] == m[r + 1][c + 1]:
                s += 3
    dunkel = sum(map(sum, m))
    return s + abs(dunkel * 20 - n * n * 10) // (n * n) * 10


def qr_matrix(text):
    """Matrix (Liste von Zeilen mit 0/1) für den Text – None, wenn er zu lang ist (über Version 6)."""
    daten = list(text.encode("utf-8"))
    v = 1
    while v <= 6 and len(daten) > QR_GESAMT[v] - QR_M[v][0] * QR_M[v][1] - 2:
        v += 1
    if v > 6:
        return None
    ecc, bloecke = QR_M[v]
    daten_cw = QR_GESAMT[v] - ecc * bloecke
    bits = []

    def schreib(wert, anzahl):
        bits.extend((wert >> i) & 1 for i in range(anzahl - 1, -1, -1))

    schreib(4, 4)
    schreib(len(daten), 8)
    for b in daten:
        schreib(b, 8)
    schreib(0, min(4, daten_cw * 8 - len(bits)))
    while len(bits) % 8:
        bits.append(0)
    cw = [int("".join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8)]
    p = 0
    while len(cw) < daten_cw:
        cw.append(0x11 if p % 2 else 0xEC)
        p += 1
    je = daten_cw // bloecke
    bl = [cw[b * je:(b + 1) * je] for b in range(bloecke)]
    pr = [_rs(d, ecc) for d in bl]
    folge = [d[i] for i in range(je) for d in bl] + [e[i] for i in range(ecc) for e in pr]
    n = 17 + 4 * v
    m = [[0] * n for _ in range(n)]
    fest = [[False] * n for _ in range(n)]

    def setze(r, c, d):
        m[r][c], fest[r][c] = 1 if d else 0, True

    for r0, c0 in ((0, 0), (0, n - 7), (n - 7, 0)):                       # Suchmuster + heller Rand
        for r in range(-1, 8):
            for c in range(-1, 8):
                rr, cc = r0 + r, c0 + c
                if rr < 0 or cc < 0 or rr >= n or cc >= n:
                    continue
                innen = 0 <= r <= 6 and 0 <= c <= 6
                setze(rr, cc, innen and (r in (0, 6) or c in (0, 6) or (2 <= r <= 4 and 2 <= c <= 4)))
    for i in range(8, n - 8):                                              # Taktlinien
        setze(6, i, i % 2 == 0)
        setze(i, 6, i % 2 == 0)
    if v >= 2:
        a = QR_AUSRICHTUNG[v]
        for r in range(-2, 3):
            for c in range(-2, 3):
                setze(a + r, a + c, max(abs(r), abs(c)) != 1)
    for i in range(9):                                                     # Formatbereiche freihalten
        fest[i][8] = fest[8][i] = True
    for i in range(8):
        fest[8][n - 1 - i] = fest[n - 1 - i][8] = True
    setze(n - 8, 8, True)                                                  # immer dunkel
    i, rechts = 0, n - 1
    while rechts >= 1:                                                     # Daten im Zickzack
        if rechts == 6:
            rechts = 5
        for senk in range(n):
            for j in range(2):
                c = rechts - j
                r = n - 1 - senk if ((rechts + 1) & 2) == 0 else senk
                if not fest[r][c] and i < len(folge) * 8:
                    m[r][c] = (folge[i >> 3] >> (7 - (i & 7))) & 1
                    i += 1
        rechts -= 2
    beste = None
    for maske in range(8):
        k = [z[:] for z in m]
        for r in range(n):
            for c in range(n):
                if not fest[r][c] and QR_MASKEN[maske](c, r):
                    k[r][c] ^= 1
        _format(k, n, maske)
        s = _strafe(k)
        if beste is None or s < beste[0]:
            beste = (s, k)
    return beste[1]


def qr_svg(text, titel="QR-Code", klasse="qr"):
    """Inline-SVG (schwarz auf weiß, scharfe Kanten) – derselbe Pfad wie `qrSvg()` der Oberfläche."""
    m = qr_matrix(text)
    if not m:
        return ""
    n = len(m)
    pfad = "".join(f"M{c + RAND} {r + RAND}h1v1h-1z" for r, z in enumerate(m) for c, d in enumerate(z) if d)
    titel = titel.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
    return (f'<svg class="{klasse}" viewBox="0 0 {n + 2 * RAND} {n + 2 * RAND}" role="img" aria-label="{titel}" '
            f'shape-rendering="crispEdges"><rect width="100%" height="100%" fill="#fff"/><path d="{pfad}" fill="#000"/></svg>')


def matrix_aus_svg(svg):
    """Liest die Matrix aus einem SVG von `qr_svg` zurück (für Prüfungen)."""
    import re
    groesse = re.search(r'viewBox="0 0 (\d+) \1"', svg)
    if not groesse:
        return None
    n = int(groesse.group(1)) - 2 * RAND
    m = [[0] * n for _ in range(n)]
    for c, r in re.findall(r"M(\d+) (\d+)h1v1h-1z", svg):
        m[int(r) - RAND][int(c) - RAND] = 1
    return m
