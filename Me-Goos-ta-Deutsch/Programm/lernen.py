#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ME GOOS-TA DEUTSCH – Karten lernen (Tool „lernen“)                  Version 2.4 (22.10.2026)
=============================================================================================
Verteiltes Wiederholen mit aktivem Abrufen: Die Karte zeigt erst die Frage, man erinnert sich, dreht um und bewertet
(1 Nochmal · 2 Schwer · 3 Gut · 4 Einfach). Geplant wird mit FSRS-6 (Free Spaced Repetition Scheduler, Standard in
Anki) in reinem Python – Standardparameter und Formeln wie die offene Referenz open-spaced-repetition/py-fsrs 6.3
(MIT, siehe DRITTLIZENZEN.md), gewünschte Behaltensquote 90 %. Dazu wie in Anki: Lernschritte 1 + 10 Minuten für neue
Karten, Neulernschritt 10 Minuten nach einem Fehler, Tageswechsel 4 Uhr (verstrichene Tage = Lerntage), Tageslimits
für neue Karten und Wiederholungen, gestreute Intervalle (Fuzz – hier aus Karte + Lerntag statt Zufall, also
reproduzierbar und gleich der Vorschau), die andere Richtung derselben Karte erst am nächsten Tag (Geschwister),
Problemkarten ab 8 Fehlern.

Lernkarte = (Bild, Sprache, Richtung „v“ = Bild/Deutsch → Kartensprache, „r“ = umgekehrt), id „<bild>|<code>|<v|r>“;
jede hat ihren eigenen Stand. Speicher: lernstand.json neben karten.csv (Nutzerdaten, nie im Release) – atomar
geschrieben, die vorige Fassung bleibt als lernstand.bak.json und wird bei einer kaputten Hauptdatei genommen.
Ändert sich Deutsch-Text, Wort der Sprache oder Bild einer Karte, beginnt ihr Lernstand von vorn (abgleichen(): Bild
→ alle Sprachen, Wort → nur diese Sprache); die Notiz zählt nicht. Entfernte Karten behalten ihren Stand 90 Tage.
Die Oberfläche (gans_ui) liefert die Karten als Liste von dicts {bild, aktiv, de, notiz, rueckseiten {code: Wort},
pfad}. Selbsttest: test_erweiterungen.py (Abschnitt E28).
"""
from __future__ import annotations

import copy
import datetime
import hashlib
import json
import math
import os
import re
import secrets
import threading
import time
from pathlib import Path

# ---------- FSRS-6: Standardparameter (py-fsrs 6.3 DEFAULT_PARAMETERS) ----------
W = (0.212, 1.2931, 2.3065, 8.2956, 6.4133, 0.8334, 3.0194, 0.001, 1.8722, 0.1666, 0.796, 1.4835, 0.0614, 0.2629,
     1.6483, 0.6014, 1.8729, 0.5425, 0.0912, 0.0658, 0.1542)
DECAY = -W[20]
FACTOR = 0.9 ** (1 / DECAY) - 1
S_MIN, D_MIN, D_MAX = 0.001, 1.0, 10.0
FUZZ = ((2.5, 7.0, 0.15), (7.0, 20.0, 0.1), (20.0, math.inf, 0.05))     # (ab, bis, Anteil) wie py-fsrs

ART, VERSION = "me-goosta-lernstand", 1
DATEI, BAK = "lernstand.json", "lernstand.bak.json"
NOTEN = (1, 2, 3, 4)                                 # Nochmal · Schwer · Gut · Einfach
PROBLEM_AB = 8                                       # Fehler (Rückfälle) → Problemkarte („Leech“ in Anki)
SICHER_AB = 21                                       # Tage Intervall → „sicher“ (Anki: mature)
AUFHEBEN_TAGE = 90                                   # Stand entfernter Karten
PROTOKOLL_MAX, RUECK_MAX = 10_000, 50                # Bewertungen gesamt · davon rückgängig machbar
VORAUS_MIN = 20                                      # Lernschritte so viel früher zeigen, wenn sonst nichts fällig ist
RICHTUNGEN = {"vorwaerts": ("v",), "rueckwaerts": ("r",), "beide": ("v", "r")}
NUR = ("", "neu", "faellig", "problem")
STANDARD = dict(neu_pro_tag=20, wdh_pro_tag=200, behaltensquote=0.9, tageswechsel=4, lernschritte=[1, 10],
                neulernschritte=[10], richtung="vorwaerts", sprache="", hoechstintervall=36500)


class LernFehler(Exception):
    """Fehler mit Code für die Oberfläche (gans_ui übersetzt ihn über TEXTE: lern_<code>)."""
    def __init__(self, code, status=400):
        super().__init__(code)
        self.code, self.status = code, status


# =============================================================================================
# FSRS-6 (Formeln wie py-fsrs Scheduler; Zustände neu → lernt → wiederholung ⇄ neulernt)
# =============================================================================================
def abrufwahrscheinlichkeit(s, tage):
    """Wahrscheinlichkeit, die Karte nach „tage“ Tagen noch zu wissen (Vergessenskurve mit Stabilität s)."""
    if not s:
        return 0.0
    return (1 + FACTOR * max(0, tage) / s) ** DECAY


def _klemme_d(d):
    return min(max(d, D_MIN), D_MAX)


def _s0(note):
    return max(W[note - 1], S_MIN)


def _d0(note, klemmen=True):
    d = W[4] - math.exp(W[5] * (note - 1)) + 1
    return _klemme_d(d) if klemmen else d


def _intervall(s, quote, hoechst):
    tage = s / FACTOR * (quote ** (1 / DECAY) - 1)
    return min(max(round(tage), 1), hoechst)


def _s_kurz(s, note):
    """Wiederholung am selben Tag (Lernschritte)."""
    plus = math.exp(W[17] * (note - 3 + W[18])) * s ** -W[19]
    if note >= 2:
        plus = max(plus, 1.0)
    return max(s * plus, S_MIN)


def _d_neu(d, note):
    arg2 = d + (10.0 - d) * -(W[6] * (note - 3)) / 9.0
    return _klemme_d(W[7] * _d0(4, klemmen=False) + (1 - W[7]) * arg2)


def _s_neu(d, s, r, note):
    if note == 1:
        lang = W[11] * d ** -W[12] * ((s + 1) ** W[13] - 1) * math.exp((1 - r) * W[14])
        return max(min(lang, s / math.exp(W[17] * W[18])), S_MIN)
    hart = W[15] if note == 2 else 1
    leicht = W[16] if note == 4 else 1
    return max(s * (1 + math.exp(W[8]) * (11 - d) * s ** -W[9] * (math.exp((1 - r) * W[10]) - 1) * hart * leicht), S_MIN)


def _fuzz(tage, zufall, hoechst):
    """Intervall leicht streuen (ab 3 Tagen), damit gemeinsam gelernte Karten nicht für immer zusammen fällig sind."""
    if tage < 2.5:
        return tage
    delta = 1.0 + sum(f * max(min(float(tage), bis) - ab, 0.0) for ab, bis, f in FUZZ)
    hi = min(round(tage + delta), hoechst)
    lo = min(max(2, round(tage - delta)), hi)
    return min(lo + int(zufall * (hi - lo + 1)), hi)


def planen(k, note, e, tage=None, zufall=None):
    """Ein Bewertungsschritt (wie py-fsrs Scheduler.review_card). k = bisheriger Stand (leer = neu), e = Einstellungen,
    tage = verstrichene Lerntage seit der letzten Bewertung (None = noch nie), zufall = 0–1 für den Fuzz (None = aus).
    → (neuer Stand, Intervall in Sekunden). Zählt anzahl und – bei einem Rückfall aus der Wiederholung – fehler."""
    if note not in NOTEN:
        raise LernFehler("note")
    k = dict(k or {})
    z, s, d, schritt = k.get("zustand") or "neu", k.get("s"), k.get("d"), k.get("schritt") or 0
    if z == "neu":
        z, schritt, s, d = "lernt", 0, None, None
    if s is None or d is None:
        s, d = _s0(note), _d0(note)
    elif tage is not None and tage < 1:
        s, d = _s_kurz(s, note), _d_neu(d, note)
    else:
        s, d = _s_neu(d, s, abrufwahrscheinlichkeit(s, tage or 0), note), _d_neu(d, note)
    sek, wdh = None, False
    if z in ("lernt", "neulernt"):
        schritte = e["lernschritte"] if z == "lernt" else e["neulernschritte"]
        if not schritte or (schritt >= len(schritte) and note >= 2) or note == 4:
            wdh = True
        elif note == 1:
            schritt, sek = 0, schritte[0] * 60
        elif note == 2:
            sek = (schritte[schritt] if schritt else schritte[0] * 1.5 if len(schritte) == 1
                   else (schritte[0] + schritte[1]) / 2) * 60
        elif schritt + 1 >= len(schritte):
            wdh = True
        else:
            schritt += 1
            sek = schritte[schritt] * 60
    elif note == 1:                                  # Rückfall aus der Wiederholung
        k["fehler"] = int(k.get("fehler") or 0) + 1
        if e["neulernschritte"]:
            z, schritt, sek = "neulernt", 0, e["neulernschritte"][0] * 60
        else:
            wdh = True
    else:
        wdh = True
    if wdh:
        z, schritt = "wiederholung", None
        tage_neu = _intervall(s, e["behaltensquote"], e["hoechstintervall"])
        if zufall is not None:
            tage_neu = _fuzz(tage_neu, zufall, e["hoechstintervall"])
        sek = tage_neu * 86400
    k.update(zustand=z, s=s, d=d, schritt=schritt, anzahl=int(k.get("anzahl") or 0) + 1)
    k.setdefault("fehler", 0)
    return k, int(round(sek))


# =============================================================================================
# Zeit, Prüfwerte, Texte
# =============================================================================================
def lerntag(ts, wechsel=4):
    """Lerntag (Tageszahl) eines Zeitpunkts – der Tag beginnt um „wechsel“ Uhr Ortszeit (Anki: 4 Uhr)."""
    t = time.localtime(float(ts) - wechsel * 3600)
    return datetime.date(t.tm_year, t.tm_mon, t.tm_mday).toordinal()


def _zufall(kid, tag):
    return int.from_bytes(hashlib.sha256(f"{kid}|{tag}".encode("utf-8")).digest()[:8], "big") / 2 ** 64


def _norm(t):
    return " ".join(str(t or "").split())


_bild_cache: dict = {}


def bild_pruefsumme(pfad):
    """Kurze Prüfsumme des Bildes (zwischengespeichert je Größe + Änderungszeit); "" wenn es fehlt."""
    try:
        st = Path(pfad).stat()
    except (OSError, TypeError):
        return ""
    schl = (str(pfad), st.st_size, st.st_mtime_ns)
    if schl not in _bild_cache:
        h = hashlib.blake2b(digest_size=8)
        try:
            with open(pfad, "rb") as f:
                for stueck in iter(lambda: f.read(1 << 20), b""):
                    h.update(stueck)
        except OSError:
            return ""
        if len(_bild_cache) > 5000:
            _bild_cache.clear()
        _bild_cache[schl] = h.hexdigest()
    return _bild_cache[schl]


def pruefwert(de, wort, bildsumme):
    return hashlib.sha1(f"{_norm(de)}\x1f{_norm(wort)}\x1f{bildsumme}".encode("utf-8")).hexdigest()[:16]


DAUER = {"de": ("< 1 Min", "{n} Min", "{n} Std", "{n} Tg", "{n} Mon", "{n} J"),
         "en": ("< 1 min", "{n} min", "{n} h", "{n} d", "{n} mo", "{n} y"),
         "es": ("< 1 min", "{n} min", "{n} h", "{n} d", "{n} mes", "{n} a")}


def dauer_text(sek, sprache="en"):
    """Intervall kurz wie auf Ankis Knöpfen: „< 1 Min“, „10 Min“, „3 Tg“, „2,5 Mon“."""
    t = DAUER.get(sprache, DAUER["en"])
    sek = max(0, float(sek))

    def zahl(x):
        x = round(x, 1) if x < 10 else round(x)
        s = f"{x:g}"
        return s.replace(".", ",") if sprache != "en" else s
    if sek <= 60:                                    # erster Lernschritt (1 min) wie bei Anki „< 1 Min“
        return t[0]
    if sek < 3600:
        return t[1].format(n=round(sek / 60))
    if sek < 86400:
        return t[2].format(n=zahl(sek / 3600))
    tage = sek / 86400
    if tage < 30:
        return t[3].format(n=round(tage))
    if tage < 365:
        return t[4].format(n=zahl(tage / 30.4))
    return t[5].format(n=zahl(tage / 365))


# =============================================================================================
# Prüfen und Vereinheitlichen (Laden, Import, Einstellungen)
# =============================================================================================
def _zahl(x, unten, oben, vorgabe, ganz=True):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return vorgabe
    if not math.isfinite(x):
        return vorgabe
    x = min(max(x, unten), oben)
    return int(round(x)) if ganz else x


def _schritte(x, vorgabe):
    if not isinstance(x, (list, tuple)):
        return list(vorgabe)
    aus = [_zahl(v, 1, 1440, None, ganz=False) for v in x[:5]]
    return [round(v, 2) for v in aus if v is not None]


def _sprachcode(x):
    x = str(x or "").strip()
    return x if re.fullmatch(r"[a-z]{2,3}", x) else ""


def einstellungen_pruefen(werte, alt=None):
    """Nur bekannte Felder, Zahlen in sinnvollen Grenzen (Behaltensquote 70–97 %; die Oberfläche bietet 80–95 %)."""
    e = dict(STANDARD, **(alt or {}))
    w = werte if isinstance(werte, dict) else {}
    if "neu_pro_tag" in w:
        e["neu_pro_tag"] = _zahl(w["neu_pro_tag"], 0, 9999, e["neu_pro_tag"])
    if "wdh_pro_tag" in w:
        e["wdh_pro_tag"] = _zahl(w["wdh_pro_tag"], 0, 99999, e["wdh_pro_tag"])
    if "behaltensquote" in w:
        q = _zahl(w["behaltensquote"], 0, 100, e["behaltensquote"], ganz=False)
        e["behaltensquote"] = round(min(max(q / 100 if q > 1 else q, 0.7), 0.97), 3)
    if "tageswechsel" in w:
        e["tageswechsel"] = _zahl(w["tageswechsel"], 0, 23, e["tageswechsel"])
    if "lernschritte" in w:
        e["lernschritte"] = _schritte(w["lernschritte"], e["lernschritte"])
    if "neulernschritte" in w:
        e["neulernschritte"] = _schritte(w["neulernschritte"], e["neulernschritte"])
    if w.get("richtung") in RICHTUNGEN:
        e["richtung"] = w["richtung"]
    if "sprache" in w:
        e["sprache"] = _sprachcode(w["sprache"])
    if "hoechstintervall" in w:
        e["hoechstintervall"] = _zahl(w["hoechstintervall"], 1, 36500, e["hoechstintervall"])
    return {k: e[k] for k in STANDARD}


_ID = re.compile(r"[^|/\\\x00-\x1f]{1,200}\|[a-z]{2,3}\|[vr]")


def _karte_pruefen(k):
    if not isinstance(k, dict) or k.get("zustand") not in ("lernt", "wiederholung", "neulernt"):
        return None
    try:
        aus = dict(zustand=k["zustand"], s=max(float(k["s"]), S_MIN), d=_klemme_d(float(k["d"])),
                   faellig=float(k["faellig"]), letzte=float(k["letzte"]), anzahl=max(0, int(k.get("anzahl") or 0)),
                   fehler=max(0, int(k.get("fehler") or 0)), schritt=None if k.get("schritt") is None else
                   max(0, int(k["schritt"])), pruef=str(k.get("pruef") or "")[:32])
    except (KeyError, TypeError, ValueError):
        return None
    if aus["zustand"] != "wiederholung" and aus["schritt"] is None:
        aus["schritt"] = 0
    if k.get("entfernt"):
        try:
            aus["entfernt"] = float(k["entfernt"])
        except (TypeError, ValueError):
            pass
    return aus


def _stapel_pruefen(st):
    if not isinstance(st, dict):
        return None
    name = _norm(st.get("name"))[:60]
    if not name:
        return None
    sid = str(st.get("id") or "")
    if not re.fullmatch(r"[0-9a-f]{8}", sid):
        sid = secrets.token_hex(4)
    bilder = st.get("bilder")
    bilder = [str(b)[:200] for b in bilder[:5000] if isinstance(b, str) and b.strip()] if isinstance(bilder, list) else None
    return dict(id=sid, name=name, sprache=_sprachcode(st.get("sprache")), notiz=_norm(st.get("notiz"))[:60],
                suche=_norm(st.get("suche"))[:60], nur=st.get("nur") if st.get("nur") in NUR else "",
                bilder=bilder or None)


def _protokoll_pruefen(p):
    if not isinstance(p, dict) or not isinstance(p.get("k"), str) or p.get("n") not in NOTEN:
        return None
    try:
        aus = dict(t=float(p["t"]), k=p["k"][:210], n=int(p["n"]), ms=_zahl(p.get("ms"), 0, 600_000, 0),
                   z=p.get("z") if p.get("z") in ("neu", "lernt", "wiederholung", "neulernt") else "neu")
    except (KeyError, TypeError, ValueError):
        return None
    if "v" in p and (p["v"] is None or _karte_pruefen(p["v"])):
        aus["v"] = None if p["v"] is None else _karte_pruefen(p["v"])
    return aus


def vereinheitlichen(d):
    """Lernstand (geladen oder importiert) → gültige Form; Unbekanntes fällt weg, nichts wirft."""
    d = d if isinstance(d, dict) else {}
    karten = d.get("karten") if isinstance(d.get("karten"), dict) else {}
    prot = d.get("protokoll") if isinstance(d.get("protokoll"), list) else []
    stapel = d.get("stapel") if isinstance(d.get("stapel"), list) else []
    aus_karten = {}
    for kid, k in list(karten.items())[:200_000]:
        k2 = _karte_pruefen(k) if isinstance(kid, str) and _ID.fullmatch(kid) else None
        if k2:
            aus_karten[kid] = k2
    aus_stapel, ids = [], set()
    for st in stapel[:200]:
        st2 = _stapel_pruefen(st)
        if st2 and st2["id"] not in ids:
            ids.add(st2["id"])
            aus_stapel.append(st2)
    aus_prot = [x for x in (_protokoll_pruefen(p) for p in prot[-PROTOKOLL_MAX:]) if x]
    aus_prot.sort(key=lambda p: p["t"])
    return dict(art=ART, version=VERSION, einstellungen=einstellungen_pruefen(d.get("einstellungen")),
                karten=aus_karten, protokoll=aus_prot, stapel=aus_stapel)


# =============================================================================================
# Lernstand eines Projekts
# =============================================================================================
_lock = threading.RLock()
_cache: dict = {}


def _stempel(p):
    try:
        st = p.stat()
        return st.st_size, st.st_mtime_ns
    except OSError:
        return None


def _lesen(p):
    d = json.loads(Path(p).read_text(encoding="utf-8"))
    if not isinstance(d, dict) or d.get("art") != ART:
        raise ValueError("kein Lernstand")
    return d


def dateien(ordner):
    """Alle Dateien des Lernstands eines Projektordners (für das Deinstallieren des Tools)."""
    return [Path(ordner) / n for n in (DATEI, BAK, DATEI + ".tmp", "lernstand.kaputt.json")]


class Lernstand:
    """Lernstand im Projektordner (neben karten.csv). zielsprache = Sprache, wenn in den Einstellungen keine gewählt ist."""

    def __init__(self, ordner, zielsprache="es"):
        self.ordner = Path(ordner)
        self.pfad, self.bak = self.ordner / DATEI, self.ordner / BAK
        self.zielsprache = zielsprache or "es"
        self.wiederhergestellt = False

    # ---------- Datei ----------
    def existiert(self):
        return self.pfad.is_file() or self.bak.is_file()

    def laden(self):
        with _lock:
            st = _stempel(self.pfad)
            c = _cache.get(str(self.pfad))
            if st and c and c[0] == st:
                return c[1]
            roh = None
            if self.pfad.is_file():
                try:
                    roh = _lesen(self.pfad)
                except (OSError, ValueError, UnicodeDecodeError):
                    roh = None
            if roh is None and self.bak.is_file():           # kaputte oder fehlende Hauptdatei → vorige Fassung
                try:
                    roh = _lesen(self.bak)
                    self.wiederhergestellt = True
                except (OSError, ValueError, UnicodeDecodeError):
                    roh = None
            d = vereinheitlichen(roh)
            if self.wiederhergestellt:
                if self.pfad.is_file():                      # die kaputte Datei aufheben, nicht löschen
                    try:
                        os.replace(self.pfad, self.ordner / "lernstand.kaputt.json")
                    except OSError:
                        pass
                self._schreiben(d, sichern=False)
            elif st:
                _cache[str(self.pfad)] = (st, d)
            return d

    def _schreiben(self, d, sichern=True):
        self.ordner.mkdir(parents=True, exist_ok=True)
        tmp = self.ordner / (DATEI + ".tmp")
        tmp.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        if sichern and self.pfad.is_file():
            os.replace(self.pfad, self.bak)
        os.replace(tmp, self.pfad)
        _cache[str(self.pfad)] = (_stempel(self.pfad), d)

    def _aendern(self, fn):
        """fn(daten) ändert den Lernstand; danach wird er gespeichert. Bei einem Fehler gilt wieder die Datei."""
        with _lock:
            d = self.laden()
            try:
                erg = fn(d)
                if erg is not False:
                    self._schreiben(d)
            except BaseException:
                _cache.pop(str(self.pfad), None)
                raise
            return erg

    def loeschen(self):
        weg = []
        with _lock:
            _cache.pop(str(self.pfad), None)
            for p in dateien(self.ordner):
                if p.is_file() and not p.is_symlink():
                    p.unlink()
                    weg.append(p)
        return weg

    # ---------- Lernkarten ----------
    def _sprache(self, d, stapel=None):
        return (stapel or {}).get("sprache") or d["einstellungen"]["sprache"] or self.zielsprache

    def stapel_finden(self, d, sid):
        if not sid or sid == "alle":
            return None
        st = next((s for s in d["stapel"] if s["id"] == sid), None)
        if st is None:
            raise LernFehler("stapel_fehlt", 404)
        return st

    def lernkarten(self, karten, d, stapel=None, jetzt=None, alle_richtungen=False):
        """Lernkarten (Bild, Sprache, Richtung) eines Stapels: aktive Karten mit Bild und Wort in der Sprache."""
        e = d["einstellungen"]
        code = self._sprache(d, stapel)
        richtungen = ("v", "r") if alle_richtungen else RICHTUNGEN[e["richtung"]]
        st = stapel or {}
        auswahl = set(st["bilder"]) if st.get("bilder") else None
        notiz, suche = st.get("notiz", "").casefold(), st.get("suche", "").casefold()
        aus = []
        for nr, k in enumerate(karten):
            wort = _norm((k.get("rueckseiten") or {}).get(code))
            if not (k.get("aktiv", True) and wort and k.get("bild")):
                continue
            if auswahl is not None and k["bild"] not in auswahl:
                continue
            if notiz and notiz not in _norm(k.get("notiz")).casefold():
                continue
            if suche and suche not in (_norm(k.get("de")) + " " + wort).casefold():
                continue
            summe = bild_pruefsumme(k.get("pfad"))
            if not summe:                                    # Bild fehlt → nicht lernbar
                continue
            pw = pruefwert(k.get("de"), wort, summe)
            for r in richtungen:
                kid = f"{k['bild']}|{code}|{r}"
                zust = d["karten"].get(kid) or {}
                if zust.get("pruef") and zust["pruef"] != pw:  # Inhalt geändert, aber noch nicht abgeglichen
                    zust = {}
                aus.append(dict(id=kid, bild=k["bild"], sprache=code, richtung=r, de=_norm(k.get("de")), wort=wort,
                                notiz=_norm(k.get("notiz")), nr=nr, pruef=pw, k=zust))
        if st.get("nur"):
            heute = lerntag(jetzt or time.time(), e["tageswechsel"])
            aus = [c for c in aus if self._passt_nur(c["k"], st["nur"], heute, jetzt or time.time(), e)]
        return aus

    @staticmethod
    def _passt_nur(k, nur, heute, jetzt, e):
        z = k.get("zustand") or "neu"
        if nur == "neu":
            return z == "neu"
        if nur == "problem":
            return int(k.get("fehler") or 0) >= PROBLEM_AB
        return z != "neu" and Lernstand._faellig(k, jetzt, heute, e)          # faellig

    @staticmethod
    def _faellig(k, jetzt, heute, e, voraus=0):
        if k.get("zustand") == "wiederholung":
            return lerntag(k["faellig"], e["tageswechsel"]) <= heute
        return k.get("zustand") in ("lernt", "neulernt") and k["faellig"] <= jetzt + voraus

    def _heute(self, d, heute, e):
        """Heute schon: neue Karten eingeführt, Wiederholungen gemacht, gelernte Karten (für die Geschwister)."""
        neu = wdh = 0
        gesehen = set()
        for p in reversed(d["protokoll"]):
            if lerntag(p["t"], e["tageswechsel"]) != heute:
                break
            neu += p["z"] == "neu"
            wdh += p["z"] == "wiederholung"
            gesehen.add(p["k"])
        return neu, wdh, gesehen

    def _schlange(self, lk, d, jetzt):
        """→ (Lernschritte fällig, Wiederholungen fällig, neue, Lernschritte bald) – mit Tageslimits und Geschwistern."""
        e = d["einstellungen"]
        heute = lerntag(jetzt, e["tageswechsel"])
        neu_heute, wdh_heute, gesehen = self._heute(d, heute, e)
        familie = {k.rsplit("|", 1)[0] for k in gesehen}
        lern, wdh, neu, bald = [], [], [], []
        for c in lk:
            k = c["k"]
            z = k.get("zustand") or "neu"
            geschwister = c["id"] not in gesehen and c["id"].rsplit("|", 1)[0] in familie
            if z in ("lernt", "neulernt"):
                (lern if k["faellig"] <= jetzt else bald if k["faellig"] <= jetzt + VORAUS_MIN * 60 else []).append(c)
            elif z == "wiederholung":
                if not geschwister and lerntag(k["faellig"], e["tageswechsel"]) <= heute:
                    wdh.append(c)
            elif not geschwister:
                neu.append(c)
        lern.sort(key=lambda c: c["k"]["faellig"])
        bald.sort(key=lambda c: c["k"]["faellig"])
        wdh.sort(key=lambda c: (abrufwahrscheinlichkeit(c["k"]["s"], heute - lerntag(c["k"]["letzte"], e["tageswechsel"])),
                                c["k"]["faellig"]))
        neu.sort(key=lambda c: (c["nr"], c["richtung"] != "v"))
        return (lern, wdh[:max(0, e["wdh_pro_tag"] - wdh_heute)], neu[:max(0, e["neu_pro_tag"] - neu_heute)], bald,
                neu_heute, wdh_heute)

    def _info(self, c, d, jetzt, sprache="en"):
        """Lernkarte für die Oberfläche, mit Intervall-Vorschau je Knopf (gleiche Rechnung wie beim Bewerten)."""
        e = d["einstellungen"]
        k = c["k"]
        heute = lerntag(jetzt, e["tageswechsel"])
        tage = heute - lerntag(k["letzte"], e["tageswechsel"]) if k.get("letzte") else None
        vorschau = {n: planen(k, n, e, tage, _zufall(c["id"], heute))[1] for n in NOTEN}
        return dict(id=c["id"], bild=c["bild"], sprache=c["sprache"], richtung=c["richtung"], de=c["de"], wort=c["wort"],
                    notiz=c["notiz"], zustand=k.get("zustand") or "neu", anzahl=k.get("anzahl", 0),
                    fehler=k.get("fehler", 0), problem=k.get("fehler", 0) >= PROBLEM_AB,
                    vorschau=vorschau, vorschau_text={n: dauer_text(v, sprache) for n, v in vorschau.items()})

    # ---------- Sitzung ----------
    def naechste_karte(self, karten, stapel=None, jetzt=None, sprache="en"):
        """Nächste Karte: fällige Lernschritte → fällige Wiederholungen (niedrigste Abrufwahrscheinlichkeit zuerst),
        neue gleichmäßig dazwischen bis zum Tageslimit → Lernschritte der nächsten 20 Minuten → fertig."""
        jetzt = time.time() if jetzt is None else jetzt
        with _lock:
            d = self.laden()
            st = self.stapel_finden(d, stapel)
            lern, wdh, neu, bald, neu_heute, wdh_heute = self._schlange(self.lernkarten(karten, d, st, jetzt), d, jetzt)
            c = None
            if lern:
                c = lern[0]
            elif wdh and neu:                                  # Anteil neuer Karten ≈ ihr Anteil an der Schlange
                c = neu[0] if neu_heute * (len(wdh) + len(neu)) < (neu_heute + wdh_heute) * len(neu) else wdh[0]
            elif wdh or neu:
                c = (wdh or neu)[0]
            elif bald:
                c = bald[0]
            zaehler = dict(neu=len(neu), lernen=len(lern) + (len(bald) if c in bald else 0), wiederholen=len(wdh))
            aus = dict(karte=self._info(c, d, jetzt, sprache) if c else None, zaehler=zaehler, fertig=c is None,
                       stapel=st["id"] if st else "alle")
            if c is None:
                aus.update(self._danach(d, karten, st, jetzt))
            return aus

    def _danach(self, d, karten, st, jetzt):
        """Wenn für heute alles geschafft ist: wie viele morgen fällig sind und wann der nächste Lernschritt kommt."""
        e = d["einstellungen"]
        heute = lerntag(jetzt, e["tageswechsel"])
        lk = self.lernkarten(karten, d, st, jetzt)
        morgen = sum(1 for c in lk if c["k"].get("zustand") and lerntag(c["k"]["faellig"], e["tageswechsel"]) <= heute + 1)
        spaeter = [c["k"]["faellig"] for c in lk if c["k"].get("zustand") in ("lernt", "neulernt")]
        return dict(morgen=morgen, naechster_schritt=min(spaeter) if spaeter else None)

    def bewerten(self, karten, kid, note, dauer_ms=0, jetzt=None):
        """Bewertung speichern (sofort – die Sitzung lässt sich jederzeit beenden). → Ergebnis mit neuem Stand."""
        jetzt = time.time() if jetzt is None else jetzt
        try:
            note = int(note)
        except (TypeError, ValueError):
            raise LernFehler("note") from None
        if note not in NOTEN:
            raise LernFehler("note")

        def fn(d):
            e = d["einstellungen"]
            c = next((c for c in self.lernkarten(karten, d, None, jetzt, alle_richtungen=True) if c["id"] == kid), None)
            if c is None:
                c = next((c for c in self._alle_sprachen(karten, d, kid, jetzt) if c["id"] == kid), None)
            if c is None:
                raise LernFehler("karte_fehlt", 404)
            heute = lerntag(jetzt, e["tageswechsel"])
            alt = c["k"] or None
            tage = heute - lerntag(alt["letzte"], e["tageswechsel"]) if alt else None
            k, sek = planen(alt, note, e, tage, _zufall(kid, heute))
            k.update(faellig=jetzt + sek, letzte=jetzt, pruef=c["pruef"])
            k.pop("entfernt", None)
            d["karten"][kid] = k
            prot = d["protokoll"]
            prot.append(dict(t=jetzt, k=kid, n=note, ms=_zahl(dauer_ms, 0, 600_000, 0),
                             z=(alt or {}).get("zustand") or "neu", v=copy.deepcopy(alt)))
            if len(prot) > PROTOKOLL_MAX:
                del prot[:len(prot) - PROTOKOLL_MAX]
            for p in prot[:-RUECK_MAX]:                       # nur die letzten 50 lassen sich zurücknehmen
                p.pop("v", None)
            return dict(id=kid, bild=c["bild"], note=note, zustand=k["zustand"], intervall=sek, faellig=k["faellig"],
                        anzahl=k["anzahl"], fehler=k["fehler"], problem=k["fehler"] >= PROBLEM_AB)
        with _lock:
            return self._aendern(fn)

    def _alle_sprachen(self, karten, d, kid, jetzt):
        """Lernkarte einer anderen Sprache als der eingestellten (z. B. Stapel mit eigener Sprache)."""
        teile = kid.split("|")
        if len(teile) != 3:
            return []
        return self.lernkarten(karten, d, {"sprache": teile[1]}, jetzt, alle_richtungen=True)

    def rueckgaengig(self):
        """Letzte Bewertung zurücknehmen (bis zu 50 Schritte) → {id, bild, note}."""
        def fn(d):
            prot = d["protokoll"]
            if not prot or "v" not in prot[-1]:
                raise LernFehler("nichts_rueckgaengig", 409)
            p = prot.pop()
            if p["v"] is None:
                d["karten"].pop(p["k"], None)
            else:
                d["karten"][p["k"]] = p["v"]
            return dict(id=p["k"], bild=p["k"].split("|")[0], note=p["n"])
        return self._aendern(fn)

    # ---------- Einstellungen, Stapel, Zurücksetzen ----------
    def einstellungen_setzen(self, werte):
        return self._aendern(lambda d: d.update(einstellungen=einstellungen_pruefen(werte, d["einstellungen"])))

    def stapel_speichern(self, stapel):
        neu = _stapel_pruefen(stapel)
        if not neu:
            raise LernFehler("stapel_name")

        def fn(d):
            alt = next((i for i, s in enumerate(d["stapel"]) if s["id"] == neu["id"]), None)
            if alt is None:
                if len(d["stapel"]) >= 200:
                    raise LernFehler("ungueltig")
                d["stapel"].append(neu)
            else:
                d["stapel"][alt] = neu
            return neu
        return self._aendern(fn)

    def stapel_loeschen(self, sid):
        def fn(d):
            vorher = len(d["stapel"])
            d["stapel"] = [s for s in d["stapel"] if s["id"] != sid]
            if len(d["stapel"]) == vorher:
                raise LernFehler("stapel_fehlt", 404)
        return self._aendern(fn)

    def zuruecksetzen(self, bild=None, alle=False):
        """Eine Karte (alle Sprachen und Richtungen) oder alles von vorn. → Anzahl zurückgesetzter Lernkarten."""
        if not alle and not bild:
            raise LernFehler("ungueltig")

        def fn(d):
            if alle:
                n = len(d["karten"])
                d["karten"], d["protokoll"] = {}, []
                return n
            weg = [k for k in d["karten"] if k.split("|")[0] == bild]
            for k in weg:
                del d["karten"][k]
            _rueck_vergessen(d, set(weg))
            return len(weg)
        return self._aendern(fn)

    def umbenennen(self, alt, neu):
        """Karte bekommt einen anderen Bildnamen (Bild ändern): Stand wandert mit – abgleichen() setzt ihn danach
        zurück, weil sich das Bild geändert hat."""
        if not self.existiert() or alt == neu:
            return 0

        def fn(d):
            weg = [k for k in d["karten"] if k.split("|")[0] == alt]
            if not weg:
                return False
            for k in weg:
                ziel = neu + k[len(alt):]
                st = d["karten"].pop(k)
                d["karten"].setdefault(ziel, st)
            _rueck_vergessen(d, set(weg))
            return len(weg)
        return self._aendern(fn) or 0

    def abgleichen(self, karten, jetzt=None):
        """Inhalt geändert (Deutsch, Wort der Sprache, Bild) → Stand dieser Lernkarten zurück; entfernte Karten nach
        90 Tagen vergessen. → [{bild, de, sprachen}] der zurückgesetzten Karten (für die Meldung)."""
        if not self.existiert():
            return []
        jetzt = time.time() if jetzt is None else jetzt
        nach_bild = {k["bild"]: k for k in karten if k.get("bild")}
        zurueck, summen = {}, {}

        def fn(d):
            aendern = False
            for kid in list(d["karten"]):
                st = d["karten"][kid]
                bild, code, _ = kid.split("|")
                k = nach_bild.get(bild)
                if k is None:
                    if not st.get("entfernt"):
                        st["entfernt"], aendern = jetzt, True
                    elif jetzt - st["entfernt"] > AUFHEBEN_TAGE * 86400:
                        d["karten"].pop(kid)
                        aendern = True
                    continue
                if st.pop("entfernt", None):
                    aendern = True
                if bild not in summen:
                    summen[bild] = bild_pruefsumme(k.get("pfad"))
                if not summen[bild] or not st.get("pruef"):    # Bild fehlt gerade → nichts entscheiden
                    continue
                if pruefwert(k.get("de"), (k.get("rueckseiten") or {}).get(code), summen[bild]) != st["pruef"]:
                    d["karten"].pop(kid)
                    _rueck_vergessen(d, {kid})
                    eintrag = zurueck.setdefault(bild, dict(bild=bild, de=_norm(k.get("de")), sprachen=[]))
                    if code not in eintrag["sprachen"]:
                        eintrag["sprachen"].append(code)
                    aendern = True
            return None if aendern else False
        self._aendern(fn)
        return list(zurueck.values())

    # ---------- Übersicht, Statistik ----------
    def karten_info(self, karten, jetzt=None):
        """{bild: {zustand, faellig, faellig_in, stabilitaet, anzahl, fehler, problem}} für „Meine Karten“ – in der
        eingestellten Sprache, über die eingestellten Richtungen zusammengefasst (schwächster Stand zählt)."""
        jetzt = time.time() if jetzt is None else jetzt
        d = self.laden()
        e = d["einstellungen"]
        heute = lerntag(jetzt, e["tageswechsel"])
        rang = {"neu": 0, "lernt": 1, "jung": 2, "sicher": 3}
        aus = {}
        for c in self.lernkarten(karten, d, None, jetzt):
            k = c["k"]
            z = _stufe(k)
            alt = aus.get(c["bild"])
            faellig = k.get("faellig")
            eintrag = dict(zustand=z, faellig=faellig, faellig_in=lerntag(faellig, e["tageswechsel"]) - heute
                           if faellig else None, stabilitaet=round(k["s"], 2) if k.get("s") else None,
                           anzahl=k.get("anzahl", 0), fehler=k.get("fehler", 0))
            if alt:
                eintrag.update(zustand=min(alt["zustand"], z, key=rang.get), anzahl=alt["anzahl"] + eintrag["anzahl"],
                               fehler=alt["fehler"] + eintrag["fehler"])
                fs = [x for x in (alt["faellig"], faellig) if x]
                eintrag["faellig"] = min(fs) if fs else None
                eintrag["faellig_in"] = lerntag(eintrag["faellig"], e["tageswechsel"]) - heute if fs else None
                st = [x for x in (alt["stabilitaet"], eintrag["stabilitaet"]) if x]
                eintrag["stabilitaet"] = min(st) if st else None
            eintrag["problem"] = eintrag["fehler"] >= PROBLEM_AB
            aus[c["bild"]] = eintrag
        return aus

    def statistik(self, karten, jetzt=None):
        jetzt = time.time() if jetzt is None else jetzt
        d = self.laden()
        e = d["einstellungen"]
        w = e["tageswechsel"]
        heute = lerntag(jetzt, w)
        prot = d["protokoll"]
        heute_p = [p for p in prot if lerntag(p["t"], w) == heute]
        tage = {lerntag(p["t"], w) for p in prot}
        serie, t = 0, heute if heute in tage else heute - 1
        while t in tage:
            serie, t = serie + 1, t - 1
        lk = self.lernkarten(karten, d, None, jetzt)
        faellig_tage = [lerntag(c["k"]["faellig"], w) - heute for c in lk if c["k"].get("zustand")]
        woche = [sum(1 for x in faellig_tage if (x <= 0 if i == 0 else x == i)) for i in range(7)]
        wdh30 = [p for p in prot if p["z"] == "wiederholung" and heute - lerntag(p["t"], w) < 30]
        stufen = {"neu": 0, "lernt": 0, "jung": 0, "sicher": 0}
        for c in lk:
            stufen[_stufe(c["k"])] += 1
        return dict(heute=dict(gelernt=len(heute_p), neu=sum(p["z"] == "neu" for p in heute_p),
                               wiederholt=sum(p["z"] == "wiederholung" for p in heute_p),
                               richtig=sum(p["n"] > 1 for p in heute_p), minuten=round(sum(p["ms"] for p in heute_p) / 60000, 1)),
                    serie=serie, woche=woche, faellig_30=sum(1 for x in faellig_tage if x <= 29),
                    behaltensquote=round(sum(p["n"] > 1 for p in wdh30) / len(wdh30), 3) if wdh30 else None,
                    behaltensquote_n=len(wdh30), zustaende=stufen, karten=len(lk),
                    problem=sum(1 for c in lk if c["k"].get("fehler", 0) >= PROBLEM_AB),
                    bewertungen=len(prot))

    def uebersicht(self, karten, jetzt=None):
        """Alles für die Lern-Übersicht: Einstellungen, Stapel mit fällig/neu, Statistik."""
        jetzt = time.time() if jetzt is None else jetzt
        with _lock:
            d = self.laden()
            stapel = []
            for st in [None, *d["stapel"]]:
                lern, wdh, neu, _, _, _ = self._schlange(self.lernkarten(karten, d, st, jetzt), d, jetzt)
                stapel.append(dict(st or dict(id="alle", name="", sprache="", notiz="", suche="", nur="", bilder=None),
                                   faellig=len(lern) + len(wdh), neu=len(neu), lernen=len(lern), wiederholen=len(wdh)))
            return dict(einstellungen=d["einstellungen"], sprache=self._sprache(d), stapel=stapel,
                        statistik=self.statistik(karten, jetzt), wiederhergestellt=self.wiederhergestellt,
                        rueckgaengig=bool(d["protokoll"]) and "v" in d["protokoll"][-1])

    # ---------- Export / Import ----------
    def export(self):
        d = copy.deepcopy(self.laden())
        d["exportiert"] = time.strftime("%Y-%m-%d %H:%M:%S")
        return d

    def importieren(self, roh):
        """Lernstand aus einem Export dazunehmen: je Lernkarte gilt der neuere Stand, Protokoll und Stapel werden
        zusammengeführt, die eigenen Einstellungen bleiben. → {karten, protokoll, stapel} (Anzahl übernommen)."""
        if not isinstance(roh, dict) or roh.get("art") != ART:
            raise LernFehler("import_kaputt")
        neu = vereinheitlichen(roh)

        def fn(d):
            n_k = n_s = 0
            for kid, k in neu["karten"].items():
                alt = d["karten"].get(kid)
                if not alt or k["letzte"] > alt["letzte"]:
                    d["karten"][kid] = k
                    n_k += 1
            schon = {(p["t"], p["k"]) for p in d["protokoll"]}
            dazu = [dict(p) for p in neu["protokoll"] if (p["t"], p["k"]) not in schon]
            for p in dazu:
                p.pop("v", None)                                 # Importiertes lässt sich nicht zurücknehmen
            d["protokoll"] = sorted(d["protokoll"] + dazu, key=lambda p: p["t"])[-PROTOKOLL_MAX:]
            ids = {s["id"] for s in d["stapel"]}
            for s in neu["stapel"]:
                if s["id"] not in ids and len(d["stapel"]) < 200:
                    d["stapel"].append(s)
                    n_s += 1
            return dict(karten=n_k, protokoll=len(dazu), stapel=n_s)
        return self._aendern(fn)


def _stufe(k):
    z = k.get("zustand") or "neu"
    if z == "neu":
        return "neu"
    if z != "wiederholung":
        return "lernt"
    return "sicher" if (k["faellig"] - k["letzte"]) / 86400 >= SICHER_AB - 0.5 else "jung"


def _rueck_vergessen(d, ids):
    """Zurückgesetzte Lernkarten: ältere Bewertungen dürfen ihren Stand nicht per „Rückgängig“ zurückholen."""
    for p in d["protokoll"]:
        if p["k"] in ids:
            p.pop("v", None)


if __name__ == "__main__":
    e = einstellungen_pruefen({})
    k, t = {}, None
    for note in (3, 3, 3, 3, 3):
        k, sek = planen(k, note, e, t)
        t = sek // 86400
        print(f"Gut → {k['zustand']:13} S={k['s']:8.3f} D={k['d']:5.2f} nächste in {dauer_text(sek, 'de')}")
