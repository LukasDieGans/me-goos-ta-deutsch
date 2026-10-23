#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ME GOOS-TA DEUTSCH – Signatur der Releases prüfen (Ed25519, minisign-kompatibel)     Version 2.5 (23.10.2026)
=============================================================================================
Seit 2.5 ist SHA256SUMS.txt jedes Releases mit Lukas’ Schlüssel signiert (SHA256SUMS.txt.minisig). „Jetzt
aktualisieren“ übernimmt nur ein ZIP, dessen Prüfsumme in einer gültig signierten SHA256SUMS.txt steht und deren
„trusted comment“ genau diese Version nennt – wer nur das GitHub-Konto oder ein Token übernimmt, kann so kein Update
unterschieben. Prüfbar auch mit dem Standard-Werkzeug:  minisign -Vm SHA256SUMS.txt -P <öffentlicher Schlüssel>

- Ed25519 nach RFC 8032 (Abschnitt 5.1, nachgebaut nach dem Python-Beispiel in Abschnitt 6) in reinem Python
- minisign-Format: Algorithmus „ED“ (BLAKE2b-512-Vorhash, Standard seit minisign 0.8) bzw. „Ed“ (ohne Vorhash),
  8 Byte Schlüssel-ID, „trusted comment“ mit globaler Signatur über Signatur + Kommentar
- SCHLUESSEL: Haupt- und Reserve-Schlüssel (öffentlich). Der Haupt-Schlüssel liegt privat nur auf Lukas’ Rechner
  (DPAPI, außerhalb des Repos), der Reserve-Schlüssel nur offline (Sicherung). Signiert wird mit signiere_release.py
  im Arbeitsordner; signiere() hier ist nur für Tests (Schlüssel, die nie veröffentlicht werden).
Nur Standardbibliothek. Selbsttest: test_erweiterungen.py (Abschnitt E51).
"""
from __future__ import annotations

import base64
import hashlib

# Öffentliche Schlüssel, denen Updates vertrauen: (Name, minisign-Schlüssel als Base64 „RW…“)
SCHLUESSEL = (
    ("haupt", "RWTgF/PLaqyFaOLbzuVu1f/n4Ym5ajtcWCm1zsQdvXugs6WwITJQaRz7"),       # ID 6885AC6ACBF317E0 (23.10.2026)
    ("reserve", "RWTUs203YCbJAd+AmheXqhpxK0BzN+uiWYyyxMfYAg4m/o8lL90ziYVY"),     # ID 01C92660376DB3D4 (nur offline)
)
KOMMENTAR = "me-goos-ta-deutsch v{version}"          # „trusted comment“ jedes Releases
MAX_SIGNATUR = 4096


class SignaturFehler(ValueError):
    """Signatur fehlt, ist kaputt, passt nicht oder stammt von einem fremden Schlüssel (Grund als kurzer Code)."""


# =============================================================================================
# Ed25519 (RFC 8032) – erweiterte Koordinaten
# =============================================================================================
_P = 2 ** 255 - 19
_L = 2 ** 252 + 27742317777372353535851937790883648493
_D = -121665 * pow(121666, _P - 2, _P) % _P
_WURZEL_M1 = pow(2, (_P - 1) // 4, _P)                 # √−1 mod p


def _plus(a, b):
    x1, y1, z1, t1 = a
    x2, y2, z2, t2 = b
    a_ = (y1 - x1) * (y2 - x2) % _P
    b_ = (y1 + x1) * (y2 + x2) % _P
    c_ = t1 * 2 * _D * t2 % _P
    d_ = z1 * 2 * z2 % _P
    e, f, g, h = b_ - a_, d_ - c_, d_ + c_, b_ + a_
    return e * f % _P, g * h % _P, f * g % _P, e * h % _P


def _mal(s, punkt):
    q = (0, 1, 1, 0)
    while s > 0:
        if s & 1:
            q = _plus(q, punkt)
        punkt = _plus(punkt, punkt)
        s >>= 1
    return q


def _gleich(a, b):
    return (a[0] * b[2] - b[0] * a[2]) % _P == 0 and (a[1] * b[2] - b[1] * a[2]) % _P == 0


def _x_aus(y, vorzeichen):
    if y >= _P:
        return None
    x2 = (y * y - 1) * pow(_D * y * y + 1, _P - 2, _P) % _P
    if x2 == 0:
        return None if vorzeichen else 0
    x = pow(x2, (_P + 3) // 8, _P)
    if (x * x - x2) % _P:
        x = x * _WURZEL_M1 % _P
    if (x * x - x2) % _P:
        return None
    return _P - x if (x & 1) != vorzeichen else x


_GY = 4 * pow(5, _P - 2, _P) % _P
_GX = _x_aus(_GY, 0)
_G = (_GX, _GY, 1, _GX * _GY % _P)


def _packen(punkt):
    zi = pow(punkt[2], _P - 2, _P)
    x, y = punkt[0] * zi % _P, punkt[1] * zi % _P
    return int.to_bytes(y | ((x & 1) << 255), 32, "little")


def _entpacken(s):
    if len(s) != 32:
        return None
    y = int.from_bytes(s, "little")
    x = _x_aus(y & ((1 << 255) - 1), y >> 255)
    return None if x is None else (x, y & ((1 << 255) - 1), 1, x * (y & ((1 << 255) - 1)) % _P)


def _h(*teile):
    return int.from_bytes(hashlib.sha512(b"".join(teile)).digest(), "little")


def _aus_seed(seed):
    h = hashlib.sha512(seed).digest()
    a = int.from_bytes(h[:32], "little") & ((1 << 254) - 8) | (1 << 254)
    return a, h[32:]


def ed25519_oeffentlich(seed: bytes) -> bytes:
    """Öffentlicher Schlüssel (32 Byte) zum privaten Seed (32 Byte)."""
    if len(seed) != 32:
        raise SignaturFehler("seed")
    return _packen(_mal(_aus_seed(seed)[0], _G))


def ed25519_signiere(seed: bytes, nachricht: bytes) -> bytes:
    """Signatur (64 Byte) nach RFC 8032. Nicht zeitkonstant – nur auf dem eigenen Rechner bzw. in Tests verwenden."""
    a, praefix = _aus_seed(seed)
    oeff = _packen(_mal(a, _G))
    r = _h(praefix, nachricht) % _L
    r_ = _packen(_mal(r, _G))
    s = (r + _h(r_, oeff, nachricht) % _L * a) % _L
    return r_ + int.to_bytes(s, 32, "little")


def ed25519_pruefe(oeff: bytes, nachricht: bytes, sig: bytes) -> bool:
    if len(oeff) != 32 or len(sig) != 64:
        return False
    a, r = _entpacken(oeff), _entpacken(sig[:32])
    s = int.from_bytes(sig[32:], "little")
    if a is None or r is None or s >= _L:
        return False
    k = _h(sig[:32], oeff, nachricht) % _L
    return _gleich(_mal(s, _G), _plus(r, _mal(k, a)))


# =============================================================================================
# minisign
# =============================================================================================
def _b64(text, laenge):
    try:
        roh = base64.b64decode(text.strip(), validate=True)
    except (ValueError, TypeError):
        raise SignaturFehler("base64") from None
    if len(roh) != laenge:
        raise SignaturFehler("laenge")
    return roh


def schluessel_id(sid: bytes) -> str:
    """Schlüssel-ID wie minisign sie anzeigt (16 Hex-Zeichen)."""
    return format(int.from_bytes(sid, "little"), "016X")


def schluessel_lesen(text: str):
    """minisign-Schlüssel („RW…“ bzw. Inhalt einer .pub-Datei) → (ID 8 Byte, öffentlicher Schlüssel 32 Byte)."""
    zeilen = [z.strip() for z in str(text or "").strip().splitlines() if z.strip()]
    if zeilen and zeilen[0].startswith("untrusted comment:"):
        zeilen = zeilen[1:]
    if len(zeilen) != 1:
        raise SignaturFehler("schluessel")
    roh = _b64(zeilen[0], 42)
    if roh[:2] != b"Ed":
        raise SignaturFehler("algorithmus")
    return roh[2:10], roh[10:]


def schluessel_text(sid: bytes, oeff: bytes) -> str:
    return base64.b64encode(b"Ed" + sid + oeff).decode("ascii")


def pub_datei(sid: bytes, oeff: bytes) -> str:
    """Inhalt einer minisign-.pub-Datei."""
    return f"untrusted comment: minisign public key {schluessel_id(sid)}\n{schluessel_text(sid, oeff)}\n"


def vertraut():
    """[(Name, ID, öffentlicher Schlüssel)] aus SCHLUESSEL (Platzhalter mit Nullen werden übersprungen)."""
    aus = []
    for name, text in SCHLUESSEL:
        sid, oeff = schluessel_lesen(text)
        if any(oeff):
            aus.append((name, sid, oeff))
    return aus


def signatur_lesen(daten: bytes):
    """.minisig → dict(alg, id, sig, kommentar, global_sig)."""
    if not isinstance(daten, (bytes, bytearray)) or not daten or len(daten) > MAX_SIGNATUR:
        raise SignaturFehler("groesse")
    try:
        zeilen = bytes(daten).decode("utf-8").split("\n")
    except UnicodeDecodeError:
        raise SignaturFehler("format") from None
    zeilen = [z[:-1] if z.endswith("\r") else z for z in zeilen]
    while zeilen and zeilen[-1] == "":
        zeilen.pop()
    if len(zeilen) != 4 or not zeilen[0].startswith("untrusted comment:") or not zeilen[2].startswith("trusted comment: "):
        raise SignaturFehler("format")
    roh = _b64(zeilen[1], 74)
    if roh[:2] not in (b"ED", b"Ed"):
        raise SignaturFehler("algorithmus")
    return dict(alg=roh[:2], id=roh[2:10], sig=roh[10:], kommentar=zeilen[2][len("trusted comment: "):],
                global_sig=_b64(zeilen[3], 64))


def pruefe(nachricht: bytes, minisig: bytes, schluessel=None, kommentar=None) -> dict:
    """Prüft eine minisign-Signatur. schluessel: [(Name, ID, öffentlicher Schlüssel)] (Standard: vertraut()),
    kommentar: muss genau so im „trusted comment“ stehen (None = beliebig). → dict(name, id, kommentar);
    sonst SignaturFehler (fremder Schlüssel, ungültig, falscher Kommentar)."""
    s = signatur_lesen(minisig)
    passend = [k for k in (vertraut() if schluessel is None else schluessel) if k[1] == s["id"]]
    if not passend:
        raise SignaturFehler("fremder_schluessel")
    name, sid, oeff = passend[0]
    inhalt = hashlib.blake2b(nachricht, digest_size=64).digest() if s["alg"] == b"ED" else nachricht
    if not ed25519_pruefe(oeff, inhalt, s["sig"]):
        raise SignaturFehler("ungueltig")
    if not ed25519_pruefe(oeff, s["sig"] + s["kommentar"].encode("utf-8"), s["global_sig"]):
        raise SignaturFehler("kommentar_ungueltig")
    if kommentar is not None and s["kommentar"] != kommentar:
        raise SignaturFehler("falscher_kommentar")
    return dict(name=name, id=schluessel_id(sid), kommentar=s["kommentar"])


def signiere(seed: bytes, sid: bytes, nachricht: bytes, kommentar: str,
             unvertraut="signature from Me Goos-ta Deutsch release key") -> bytes:
    """minisign-Signatur (Algorithmus ED) → Inhalt der .minisig-Datei."""
    if len(sid) != 8 or "\n" in kommentar or "\r" in kommentar or "\n" in unvertraut:
        raise SignaturFehler("eingabe")
    sig = ed25519_signiere(seed, hashlib.blake2b(nachricht, digest_size=64).digest())
    glob = ed25519_signiere(seed, sig + kommentar.encode("utf-8"))
    return (f"untrusted comment: {unvertraut}\n{base64.b64encode(b'ED' + sid + sig).decode('ascii')}\n"
            f"trusted comment: {kommentar}\n{base64.b64encode(glob).decode('ascii')}\n").encode("utf-8")
