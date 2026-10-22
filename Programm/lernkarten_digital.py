#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ME GOOS-TA DEUTSCH – Digitale Lernkarten                            Version 2.4 (22.10.2026)
=============================================================================================
Macht aus den fertigen Karten (verbesserte Vorderseiten aus dem Zwischenspeicher + Wort auf Spanisch) Dateien
zum digitalen Lernen – am Rechner und auf dem Handy. Aufgerufen vom Generator mit `--nur digital`.
Andere Kartensprache (`--sprache ja`, seit 2.0): eigenes Anki-Paket (Notiztyp + Stapel „… – Japanisch“, Feld mit dem
Namen der Sprache, rechts-nach-links für Arabisch), Lernseite mit lang/dir, Dateinamen mit „_ja“. Spanisch unverändert.

  apkg   Anki-Paket (.apkg) mit eingebetteten Bildern: Anki (Windows, Mac, Linux), AnkiDroid (Android),
         AnkiMobile (iPhone/iPad), außerdem RemNote und Mochi (Import „Anki“). Erneuter Import aktualisiert die
         Karten statt sie zu verdoppeln (feste IDs je Bilddatei).
  html   Lernseite: eine einzige HTML-Datei, läuft offline im Browser am Rechner (am Handy nur eingeschränkt: iPhone-Dateien-App ohne JavaScript), mit Umdrehen,
         „Gewusst/Nochmal“ (Lernkasten nach Leitner, Fortschritt bleibt im Browser gespeichert), beiden
         Richtungen und Vorlesen (🔊, wenn das Gerät eine deutsche Stimme hat).
  pdf    Bildschirm-PDF: je Karte eine Seite Vorderseite, eine Seite Rückseite im Kartenformat – zum
         Durchblättern in jedem PDF-Programm, ohne Druckränder.
  csv    Tabellen für andere Lern-Apps: Anki-Textimport (+ Bilder), Mochi-CSV (+ Bilder) und reiner Text (TSV)
         für Quizlet, Brainscape, Knowt & Co.

Grundlage: karten_konverter.py (Lukas); das .apkg-Format (SQLite-Schema, JSON-Struktur, Medien-Liste) folgt dem
Referenzprojekt genanki (MIT-Lizenz, https://github.com/kerrickstaley/genanki) – es wird kein Code daraus
verwendet, nur das dokumentierte Dateiformat. Nur Standardbibliothek + Pillow/ReportLab (wie der Generator).
"""

from __future__ import annotations

import base64
import csv
import hashlib
import html
import io
import itertools
import json
import re
import sqlite3
import string
import tempfile
import time
import zipfile
from pathlib import Path

FORMATE = ("apkg", "html", "pdf", "csv")
AUSWAHL = {"empfohlen": ("apkg", "html", "pdf"), "apkg": ("apkg",), "html": ("html",), "pdf": ("pdf",),
           "csv": ("csv",), "alle": FORMATE}
ORDNER = "digital"


# --------------------------------------------------------------------------- Hilfen
def esc(s) -> str:
    return html.escape(str(s or ""), quote=True)


def teile(es):
    """„viejo / anciano“ → („viejo“, [„anciano“]); „|“ (Zeilenumbruch auf der Karte) wird zum Leerzeichen."""
    stuecke = [t.strip().replace("|", " ") for t in str(es or "").split("/") if t.strip()]
    return (stuecke[0] if stuecke else ""), stuecke[1:]


def bild_bytes(pfad, max_kante=800, qualitaet=85) -> bytes:
    """Verkleinerte JPEG-Fassung einer Vorderseite (kleinere Pakete, schneller am Handy)."""
    from PIL import Image
    with Image.open(pfad) as im:
        im = im.convert("RGB")
        im.thumbnail((max_kante, max_kante), Image.Resampling.LANCZOS)
        puffer = io.BytesIO()
        im.save(puffer, "JPEG", quality=qualitaet, optimize=True)
        return puffer.getvalue()


def medienname(k) -> str:
    return re.sub(r"[^\w.\-]", "_", Path(k["bild"]).stem) + ".jpg"


# --------------------------------------------------------------------------- Anki-Paket (.apkg)
_BASE91 = string.ascii_lowercase + string.ascii_uppercase + string.digits + "!#$%&()*+,-./:;<=>?@[]^_`{|}~"
SCHEMA = """
CREATE TABLE col (id integer primary key, crt integer not null, mod integer not null, scm integer not null,
    ver integer not null, dty integer not null, usn integer not null, ls integer not null, conf text not null,
    models text not null, decks text not null, dconf text not null, tags text not null);
CREATE TABLE notes (id integer primary key, guid text not null, mid integer not null, mod integer not null,
    usn integer not null, tags text not null, flds text not null, sfld integer not null, csum integer not null,
    flags integer not null, data text not null);
CREATE TABLE cards (id integer primary key, nid integer not null, did integer not null, ord integer not null,
    mod integer not null, usn integer not null, type integer not null, queue integer not null,
    due integer not null, ivl integer not null, factor integer not null, reps integer not null,
    lapses integer not null, left integer not null, odue integer not null, odid integer not null,
    flags integer not null, data text not null);
CREATE TABLE revlog (id integer primary key, cid integer not null, usn integer not null, ease integer not null,
    ivl integer not null, lastIvl integer not null, factor integer not null, time integer not null,
    type integer not null);
CREATE TABLE graves (usn integer not null, oid integer not null, type integer not null);
CREATE INDEX ix_notes_usn on notes (usn);
CREATE INDEX ix_cards_usn on cards (usn);
CREATE INDEX ix_revlog_usn on revlog (usn);
CREATE INDEX ix_cards_nid on cards (nid);
CREATE INDEX ix_cards_sched on cards (did, queue, due);
CREATE INDEX ix_revlog_cid on revlog (cid);
CREATE INDEX ix_notes_csum on notes (csum);
"""
MODELLNAME = "Me Goos-ta Deutsch (Bild → Spanisch)"
FELDER = ["Deutsch", "Bild", "Spanisch", "Alternativen", "Notiz"]   # erstes Feld = Sortier-/Duplikatfeld
QFMT = "<div class=\"bild\">{{Bild}}</div>"
AFMT = ("{{FrontSide}}<hr id=answer><div class=\"rueck\"><div class=\"es\">{{Spanisch}}</div>"
        "{{#Alternativen}}<div class=\"alt\">{{Alternativen}}</div>{{/Alternativen}}"
        "<div class=\"de\">{{Deutsch}}</div>{{#Notiz}}<div class=\"notiz\">{{Notiz}}</div>{{/Notiz}}</div>")
CSS = (".card { font-family: 'Poppins', 'Segoe UI', Arial, sans-serif; font-size: 20px; text-align: center; "
       "color: #1B2D4F; background: #FFFFFF; }\n"
       ".bild img { max-width: 100%; max-height: 62vh; border-radius: 12px; }\n"
       ".rueck { background: #BFDDF2; border-radius: 14px; padding: 18px 12px; margin-top: 8px; }\n"
       ".es { font-size: 34px; font-weight: bold; }\n.alt { font-size: 20px; color: #3F5C88; margin-top: 4px; }\n"
       ".de { font-size: 17px; margin-top: 10px; color: #3F5C88; }\n"
       ".notiz { font-size: 15px; font-style: italic; opacity: .8; margin-top: 6px; }\n"
       ".nightMode .card, .night_mode .card { background: #1B2D4F; color: #F2F6FB; }\n"
       ".nightMode .rueck, .night_mode .rueck { background: #2A4470; }\n")
LATEX_PRE = ("\\documentclass[12pt]{article}\n\\special{papersize=3in,5in}\n\\usepackage[utf8]{inputenc}\n"
             "\\usepackage{amssymb,amsmath}\n\\pagestyle{empty}\n\\setlength{\\parindent}{0in}\n\\begin{document}\n")
STANDARD_DECK = {"collapsed": False, "conf": 1, "desc": "", "dyn": 0, "extendNew": 10, "extendRev": 50, "id": 1,
                 "lrnToday": [0, 0], "mod": 1425279151, "name": "Default", "newToday": [0, 0], "revToday": [0, 0],
                 "timeToday": [0, 0], "usn": 0}
STANDARD_DCONF = {"autoplay": True, "id": 1, "lapse": {"delays": [10], "leechAction": 0, "leechFails": 8, "minInt": 1,
                                                       "mult": 0},
                  "maxTaken": 60, "mod": 0, "name": "Default",
                  "new": {"bury": True, "delays": [1, 10], "initialFactor": 2500, "ints": [1, 4, 7], "order": 1,
                          "perDay": 20, "separate": True},
                  "replayq": True,
                  "rev": {"bury": True, "ease4": 1.3, "fuzz": 0.05, "ivlFct": 1, "maxIvl": 36500, "minSpace": 1,
                          "perDay": 100},
                  "timer": 0, "usn": 0}


def stabile_id(text: str) -> int:
    """Stabile ID im üblichen Anki-Bereich: gleicher Name → gleiche ID (erneuter Import aktualisiert)."""
    return (1 << 30) + int(hashlib.sha1(text.encode()).hexdigest()[:8], 16) % (1 << 30)


def guid_fuer(text: str) -> str:
    n, aus = int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "big"), []
    while n:
        n, r = divmod(n, len(_BASE91))
        aus.append(_BASE91[r])
    return "".join(reversed(aus))


def feld_checksumme(text: str) -> int:
    return int(hashlib.sha1(text.encode()).hexdigest()[:8], 16)


def sprach_info(code="es"):
    """Name (deutsch, wie der Notiztyp), Richtung und Dateiendung der Kartensprache; es = alles wie bisher."""
    code = code or "es"
    try:
        import sprachen
        s = sprachen.SPRACHEN.get(code) or sprachen.SPRACHEN["es"]
        namen, rtl = dict(s["name"]), s["richtung"] == "rtl"
    except Exception:  # noqa: BLE001
        namen, rtl = {"de": "Spanisch", "en": "Spanish", "es": "español"}, False
    return dict(code=code, namen=namen, rtl=rtl, endung="" if code == "es" else f"_{code}")


def modell_fuer(code="es"):
    """(Modellname, Felder, Rückseiten-Vorlage, Vorlagenname, Modell-Schlüssel) – Spanisch exakt wie bisher, andere
    Sprachen mit eigenem Notiztyp (sonst würde ein erneuter Import den spanischen überschreiben)."""
    if not code or code == "es":
        return MODELLNAME, FELDER, AFMT, "Bild → Spanisch", "me-goosta-bild-v1"
    name = sprach_info(code)["namen"]["de"]
    felder = [name if f == "Spanisch" else f for f in FELDER]
    afmt = AFMT.replace("{{Spanisch}}", "{{" + name + "}}")
    return (MODELLNAME.replace("Spanisch", name), felder, afmt, f"Bild → {name}", f"me-goosta-bild-v1-{code}")


def schreibe_apkg(karten, ziel: Path, deck: str, code: str = "es") -> Path:
    jetzt = time.time()
    ms = int(jetzt * 1000)
    ids = itertools.count(ms)
    modellname, felder_namen, afmt, vorlage, modell_schluessel = modell_fuer(code)
    rtl = sprach_info(code)["rtl"]
    deck_id, modell_id = stabile_id("deck:" + deck), stabile_id(modell_schluessel)
    modell = {"css": CSS, "did": deck_id,
              "flds": [{"name": n, "ord": i, "font": "Arial", "media": [], "rtl": rtl and i == 2, "size": 20,
                        "sticky": False} for i, n in enumerate(felder_namen)],
              "id": str(modell_id), "latexPost": "\\end{document}", "latexPre": LATEX_PRE, "latexsvg": False,
              "mod": int(jetzt), "name": modellname, "req": [[0, "all", [felder_namen.index("Bild")]]], "sortf": 0,
              "tags": [], "tmpls": [{"name": vorlage, "ord": 0, "qfmt": QFMT, "afmt": afmt, "bafmt": "",
                                     "bqfmt": "", "bfont": "", "bsize": 0, "did": None}],
              "type": 0, "usn": -1, "vers": []}
    deck_json = {"collapsed": False, "conf": 1, "desc": "Me Goos-ta Deutsch", "dyn": 0, "extendNew": 0,
                 "extendRev": 50, "id": deck_id, "lrnToday": [0, 0], "mod": int(jetzt), "name": deck,
                 "newToday": [0, 0], "revToday": [0, 0], "timeToday": [0, 0], "usn": -1}
    conf = {"activeDecks": [1], "addToCur": True, "collapseTime": 1200, "curDeck": 1, "curModel": str(modell_id),
            "dueCounts": True, "estTimes": True, "newBury": True, "newSpread": 0, "nextPos": len(karten) + 1,
            "sortBackwards": False, "sortType": "noteFld", "timeLim": 0}
    notizen, kartenzeilen, medien = [], [], []
    for pos, k in enumerate(karten, 1):
        name = medienname(k)
        medien.append((name, bild_bytes(k["front_jpg"])))
        haupt, alternativen = teile(k["es"])
        felder = [esc(k["de"]), f'<img src="{esc(name)}">', esc(haupt), esc(" · ".join(alternativen)), esc(k.get("notiz"))]
        nid = next(ids)
        guid = f"me-goosta:{k['bild']}" if code == "es" else f"me-goosta:{code}:{k['bild']}"
        notizen.append((nid, guid_fuer(guid), modell_id, int(jetzt), -1, "" if code == "es" else f" {code} ",
                        "\x1f".join(felder), esc(k["de"]), feld_checksumme(esc(k["de"])), 0, ""))
        kartenzeilen.append((next(ids), nid, deck_id, 0, int(jetzt), -1, 0, 0, pos, 0, 0, 0, 0, 0, 0, 0, 0, ""))
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "collection.anki2"
        con = sqlite3.connect(db)
        con.executescript(SCHEMA)
        con.execute("INSERT INTO col VALUES(null,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (1411124400, ms, ms, 11, 0, 0, 0, json.dumps(conf), json.dumps({str(modell_id): modell}),
                     json.dumps({"1": STANDARD_DECK, str(deck_id): deck_json}), json.dumps({"1": STANDARD_DCONF}), "{}"))
        con.executemany("INSERT INTO notes VALUES(?,?,?,?,?,?,?,?,?,?,?)", notizen)
        con.executemany("INSERT INTO cards VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", kartenzeilen)
        con.commit()
        con.close()
        pfad = ziel / f"Me-Goos-ta-Deutsch_Anki{sprach_info(code)['endung']}.apkg"
        tmp = pfad.with_name(pfad.name + ".tmp")
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_STORED) as z:   # JPEG ist schon komprimiert
            z.write(db, "collection.anki2")
            z.writestr("media", json.dumps({str(i): n for i, (n, _) in enumerate(medien)}))
            for i, (_, daten) in enumerate(medien):
                z.writestr(str(i), daten)
        tmp.replace(pfad)
    return pfad


# --------------------------------------------------------------------------- Lernseite (eine HTML-Datei)
LERNSEITE_TEXTE = {
    "de": dict(titel="Lernkarten", umdrehen="Tippen zum Umdrehen", gewusst="Gewusst ✓", nochmal="Nochmal ↺",
               richtung1="Bild → Spanisch", richtung2="Spanisch → Bild", mischen="Mischen", neu="Von vorn",
               fertig="Alles gewusst – großartig! 🎉", stand="{g} von {n} sitzen schon – weiter so!", vorlesen="Deutsch vorlesen",
               neu_frage="Lernstand zurücksetzen?", tipp="Leertaste = umdrehen · → gewusst · ← nochmal"),
    "en": dict(titel="Flashcards", umdrehen="Tap to flip", gewusst="Got it ✓", nochmal="Again ↺",
               richtung1="Picture → Spanish", richtung2="Spanish → picture", mischen="Shuffle", neu="Start over",
               fertig="You know them all – brilliant! 🎉", stand="{g} of {n} mastered – keep it up!", vorlesen="Read the German aloud",
               neu_frage="Reset your progress?", tipp="Space = flip · → got it · ← again"),
    "es": dict(titel="Tarjetas", umdrehen="Toca para voltear", gewusst="¡La sé! ✓", nochmal="Otra vez ↺",
               richtung1="Imagen → español", richtung2="Español → imagen", mischen="Mezclar", neu="Empezar de nuevo",
               fertig="¡Las sabes todas, increíble! 🎉", stand="{g} de {n} dominadas. ¡Sigue así!", vorlesen="Leer el alemán en voz alta",
               neu_frage="¿Reiniciar tu progreso?", tipp="Espacio = voltear · → la sé · ← otra vez"),
}

LERNSEITE = r"""<!doctype html>
<html lang="__LANG__"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'">
<title>__TITEL__</title>
<style>
:root { --wasser: #BFDDF2; --nacht: #1B2D4F; --nacht2: #3F5C88; --himmel: #E8F2FA; --gut: #1E8A50; --schnabel: #F6A94B; }
* { box-sizing: border-box; } html, body { margin: 0; }
body { font-family: "Poppins", "Segoe UI", system-ui, -apple-system, Arial, sans-serif; background: var(--himmel); color: var(--nacht);
  min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 12px; }
header { width: min(720px, 100%); display: flex; gap: 8px; align-items: center; flex-wrap: wrap; justify-content: space-between; }
h1 { font-size: 18px; margin: 4px 0; }
.leiste { display: flex; gap: 6px; flex-wrap: wrap; }
button { font: inherit; border: 1px solid #C9DCEB; background: #fff; color: var(--nacht); border-radius: 10px; padding: 8px 12px; cursor: pointer; }
button:focus-visible { outline: 3px solid var(--schnabel); outline-offset: 2px; }
.stand { width: min(720px, 100%); margin: 8px 0; font-size: 14px; color: var(--nacht2); }
.balken { height: 8px; background: #fff; border-radius: 4px; overflow: hidden; margin-top: 4px; }
.balken span { display: block; height: 100%; background: var(--gut); width: 0; transition: width .3s; }
#buehne { width: min(720px, 100%); }
.karte { width: 100%; aspect-ratio: 88 / 63; perspective: 1400px; margin: 6px 0 12px; cursor: pointer; }
.innen { position: relative; width: 100%; height: 100%; transition: transform .45s; transform-style: preserve-3d; }
.karte.um .innen { transform: rotateY(180deg); }
.seite { position: absolute; inset: 0; backface-visibility: hidden; -webkit-backface-visibility: hidden; border-radius: 18px;
  overflow: hidden; background: #fff; box-shadow: 0 8px 28px rgba(27,45,79,.18); display: grid; place-items: center; padding: 10px; }
.seite img { width: 100%; height: 100%; object-fit: contain; border-radius: 12px; }
.hinten { transform: rotateY(180deg); background: var(--wasser); text-align: center; padding: 18px; }
.es { font-size: clamp(26px, 7vw, 46px); font-weight: 700; line-height: 1.15; }
.alt { font-size: clamp(16px, 3.6vw, 22px); color: var(--nacht2); margin-top: 6px; }
.de { font-size: clamp(15px, 3.4vw, 20px); color: var(--nacht2); margin-top: 14px; }
.notiz { font-size: 14px; font-style: italic; opacity: .8; margin-top: 6px; }
.knoepfe { display: flex; gap: 10px; width: min(720px, 100%); }
.knoepfe button { flex: 1; font-size: 17px; padding: 14px; font-weight: 700; }
.knoepfe .gut { background: var(--gut); border-color: var(--gut); color: #fff; }
.tipp { font-size: 12px; color: var(--nacht2); margin-top: 10px; text-align: center; }
.fertig { font-size: 22px; font-weight: 700; text-align: center; padding: 40px 10px; }
.hinweis { font-size: 13px; color: var(--nacht2); }
@media (prefers-color-scheme: dark) { body { background: #12203A; color: #EEF4FB; } .seite { background: #1B2D4F; }
  .hinten { background: #2A4470; } button { background: #22365C; color: #EEF4FB; border-color: #3B5582; }
  .stand, .alt, .de, .tipp { color: #BFD3EA; } }
@media (prefers-reduced-motion: reduce) { .innen { transition: none; } }
</style></head><body>
<header><h1 id="titel"></h1><div class="leiste"><button id="richtung"></button><button id="mischen"></button><button id="neu"></button></div></header>
<div class="stand"><span id="standtext"></span><div class="balken"><span id="balken"></span></div></div>
<div id="buehne"></div>
<div class="knoepfe" id="knoepfe"><button id="nochmal"></button><button id="sprechen" title=""></button><button id="gewusst" class="gut"></button></div>
<p class="tipp" id="tipp"></p>
<script type="application/json" id="daten">__DATEN__</script>
<script>
"use strict";
const D = JSON.parse(document.getElementById("daten").textContent), T = D.texte, $ = s => document.getElementById(s);
const SCHLUESSEL = "mgd-lernstand-" + D.deck_id;
let stand = {}; try { stand = JSON.parse(localStorage.getItem(SCHLUESSEL) || "{}"); } catch (e) { stand = {}; }
let rueckwaerts = false, reihe = [], aktuell = null;
const kasten = id => stand[id] || 1;
function speichern() { try { localStorage.setItem(SCHLUESSEL, JSON.stringify(stand)); } catch (e) { /* privat */ } }
function mischen(a) { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
function neueReihe() { reihe = mischen(D.karten.filter(k => kasten(k.id) < 5)).sort((a, b) => kasten(a.id) - kasten(b.id)); }
function text(el, t) { el.textContent = t; return el; }
function seiteBild(k) { const s = document.createElement("div"); s.className = "seite"; const i = new Image(); i.alt = k.de; i.src = k.bild; s.append(i); return s; }
function seiteWort(k) {
  const s = document.createElement("div"); s.className = "seite";
  const w = document.createElement("div"); w.append(text(document.createElement("div"), k.es));
  w.firstChild.className = "es"; w.lang = D.rs_lang || "es"; w.dir = D.rs_dir || "auto";
  if (k.alt) { const a = text(document.createElement("div"), k.alt); a.className = "alt"; w.append(a); }
  s.append(w); return s;
}
function zeige() {
  const n = D.karten.length, g = D.karten.filter(k => kasten(k.id) >= 5).length;
  text($("standtext"), T.stand.replace("{g}", g).replace("{n}", n)); $("balken").style.width = (n ? 100 * g / n : 0) + "%";
  const b = $("buehne"); b.innerHTML = "";
  if (!reihe.length) neueReihe();
  aktuell = reihe[0] || null;
  $("knoepfe").style.visibility = aktuell ? "visible" : "hidden";
  if (!aktuell) { b.append(text(document.createElement("div"), T.fertig)); b.firstChild.className = "fertig"; knopfStimme(); return; }
  const k = aktuell, karte = document.createElement("div"); karte.className = "karte"; karte.title = T.umdrehen;
  const innen = document.createElement("div"); innen.className = "innen";
  const vorn = rueckwaerts ? seiteWort(k) : seiteBild(k);
  const hinten = document.createElement("div"); hinten.className = "seite hinten";
  const box = document.createElement("div");
  if (rueckwaerts) { const i = new Image(); i.alt = k.de; i.src = k.bild; i.style.maxHeight = "60%"; box.append(i); }
  const es = text(document.createElement("div"), k.es); es.className = "es"; if (!rueckwaerts) box.append(es);
  es.lang = D.rs_lang || "es"; es.dir = D.rs_dir || "auto";
  if (k.alt && !rueckwaerts) { const a = text(document.createElement("div"), k.alt); a.className = "alt"; a.lang = es.lang; a.dir = es.dir; box.append(a); }
  const de = text(document.createElement("div"), k.de); de.className = "de"; box.append(de);
  if (k.notiz) { const z = text(document.createElement("div"), k.notiz); z.className = "notiz"; box.append(z); }
  hinten.append(box); innen.append(vorn, hinten); karte.append(innen); b.append(karte);
  karte.addEventListener("click", () => { karte.classList.toggle("um"); knopfStimme(); });
  knopfStimme();
}
function weiter(gewusst) {
  if (!aktuell) return;
  stand[aktuell.id] = gewusst ? Math.min(5, kasten(aktuell.id) + 1) : 1; speichern();
  reihe.shift(); if (!gewusst) reihe.splice(Math.min(3, reihe.length), 0, aktuell);
  zeige();
}
// Deutsch vorlesen: nur mit einer Stimme des Systems (offline, localService), nur nach dem Umdrehen; ohne Stimme kein Knopf
function deStimme() {
  if (!window.speechSynthesis || !speechSynthesis.getVoices) return null;
  const l = v => String(v.lang || "").toLowerCase().replace("_", "-");
  const st = speechSynthesis.getVoices().filter(v => v.localService !== false && l(v).split("-")[0] === "de");
  for (const r of ["de-de", "de-at", "de-ch"]) { const v = st.find(x => l(x) === r); if (v) return v; }
  return st[0] || null;
}
let stimme = deStimme();
function umgedreht() { const k = document.querySelector(".karte"); return !!(k && k.classList.contains("um")); }
function knopfStimme() { $("sprechen").hidden = !(stimme && aktuell && umgedreht()); }
function sprich() {
  if (!aktuell || !stimme || !umgedreht()) return;
  const u = new SpeechSynthesisUtterance(aktuell.de); u.voice = stimme; u.lang = stimme.lang; speechSynthesis.cancel(); speechSynthesis.speak(u);
}
if (window.speechSynthesis && speechSynthesis.addEventListener) speechSynthesis.addEventListener("voiceschanged", () => { stimme = deStimme(); knopfStimme(); });
text($("titel"), D.titel); document.title = D.titel;
text($("nochmal"), T.nochmal); text($("gewusst"), T.gewusst); text($("sprechen"), "🔊"); $("sprechen").title = T.vorlesen;
$("sprechen").setAttribute("aria-label", T.vorlesen); $("sprechen").hidden = true;
text($("richtung"), T.richtung1); text($("mischen"), T.mischen); text($("neu"), T.neu); text($("tipp"), T.tipp);
$("gewusst").onclick = () => weiter(true); $("nochmal").onclick = () => weiter(false); $("sprechen").onclick = sprich;
$("mischen").onclick = () => { neueReihe(); zeige(); };
$("neu").onclick = () => { if (confirm(T.neu_frage)) { stand = {}; speichern(); neueReihe(); zeige(); } };
$("richtung").onclick = () => { rueckwaerts = !rueckwaerts; text($("richtung"), rueckwaerts ? T.richtung2 : T.richtung1); zeige(); };
document.addEventListener("keydown", e => {
  if (e.key === " ") { e.preventDefault(); const k = document.querySelector(".karte"); if (k) { k.classList.toggle("um"); knopfStimme(); } }
  if (e.key === "ArrowRight") weiter(true); if (e.key === "ArrowLeft") weiter(false);
});
neueReihe(); zeige();
</script></body></html>
"""


def lernseite_texte(sprache: str, code: str = "es") -> dict:
    """Texte der Lernseite; bei einer anderen Kartensprache steht deren Name statt „Spanisch“."""
    texte = dict(LERNSEITE_TEXTE.get(sprache, LERNSEITE_TEXTE["en"]))
    if code and code != "es":
        ui = sprache if sprache in LERNSEITE_TEXTE else "en"
        name = sprach_info(code)["namen"][ui]
        alt = {"de": "Spanisch", "en": "Spanish", "es": "español"}[ui]
        for schluessel in ("richtung1", "richtung2"):
            t = texte[schluessel].replace(alt, name).replace(alt.capitalize(), name[:1].upper() + name[1:])
            texte[schluessel] = t
    return texte


def schreibe_lernseite(karten, ziel: Path, deck: str, sprache: str, code: str = "es") -> Path:
    texte = lernseite_texte(sprache, code)
    info = sprach_info(code)
    daten = dict(titel=f"{deck} · {texte['titel']}", deck_id=stabile_id("deck:" + deck), texte=texte, karten=[],
                 rs_lang=code, rs_dir="rtl" if info["rtl"] else "auto")
    for k in karten:
        haupt, alternativen = teile(k["es"])
        daten["karten"].append(dict(id=hashlib.sha1(k["bild"].encode()).hexdigest()[:10], de=k["de"], es=haupt,
                                    alt=" · ".join(alternativen), notiz=k.get("notiz") or "",
                                    bild="data:image/jpeg;base64," +
                                         base64.b64encode(bild_bytes(k["front_jpg"], 720, 80)).decode()))
    # JSON im <script type="application/json">: „<“ maskieren, damit kein Text das Skript beenden kann
    roh = json.dumps(daten, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    seite = (LERNSEITE.replace("__LANG__", sprache if sprache in LERNSEITE_TEXTE else "en")
             .replace("__TITEL__", esc(daten["titel"])).replace("__DATEN__", roh))
    pfad = ziel / f"Me-Goos-ta-Deutsch_Lernseite{info['endung']}.html"
    tmp = pfad.with_name(pfad.name + ".tmp")
    tmp.write_text(seite, encoding="utf-8")
    tmp.replace(pfad)
    return pfad


# --------------------------------------------------------------------------- Bildschirm-PDF
def schreibe_bildschirm_pdf(karten, ziel: Path, cfg, gl) -> Path:
    """Je Karte eine Seite Vorderseite und eine Seite Rückseite im Endformat (ohne Beschnitt und Marken)."""
    from reportlab.lib.units import mm
    code = getattr(cfg, "sprache", "es")
    pfad = ziel / f"Me-Goos-ta-Deutsch_Bildschirm_{cfg.kuerzel}{sprach_info(code)['endung']}.pdf"
    tmp = pfad.with_name(pfad.name + ".tmp")
    w, h = cfg.b * mm, cfg.h * mm
    c = gl.neues_pdf(tmp, (w, h), f"{gl.PRODUKT} – Bildschirm", code)
    for k in karten:
        gl.zeichne_vorderseite(c, 0, 0, w, h, k["front_jpg"], cfg)
        c.showPage()
        gl.zeichne_rueckseite(c, 0, 0, w, h, k, cfg)
        c.showPage()
    c.save()
    tmp.replace(pfad)
    return pfad


# --------------------------------------------------------------------------- Tabellen für andere Apps
def _tsv(pfad: Path, zeilen, kopf: str = "", trenner: str = "\t"):
    with open(pfad, "w", encoding="utf-8", newline="") as f:
        f.write(kopf)
        csv.writer(f, delimiter=trenner, lineterminator="\n").writerows(zeilen)


def _sicher(text) -> str:
    """Tabellenzellen nie als Formel lesbar machen (Excel & Co.)."""
    t = str(text or "").replace("\t", " ").replace("\n", " ")
    return "'" + t if t[:1] in ("=", "+", "-", "@") else t


def schreibe_tabellen(karten, ziel: Path, deck: str, code: str = "es") -> Path:
    ordner = ziel / f"tabellen{sprach_info(code)['endung']}"
    (ordner / "bilder").mkdir(parents=True, exist_ok=True)
    zeilen_anki, zeilen_mochi, zeilen_text = [], [], []
    for k in karten:
        name = medienname(k)
        (ordner / "bilder" / name).write_bytes(bild_bytes(k["front_jpg"]))
        haupt, alternativen = teile(k["es"])
        rueck = " / ".join([haupt, *alternativen])
        rueck_html = "<br>".join([f"<b>{esc(haupt)}</b>", *(esc(a) for a in alternativen), f"<i>{esc(k['de'])}</i>"]
                                 + ([esc(k["notiz"])] if k.get("notiz") else []))
        zeilen_anki.append([f'<img src="{esc(name)}">', rueck_html])
        zeilen_mochi.append([f"![]({name})", _sicher(rueck)])
        zeilen_text.append([_sicher(k["de"]), _sicher(rueck)])
    _tsv(ordner / "anki_import.txt", zeilen_anki, f"#separator:tab\n#html:true\n#notetype:Basic\n#deck:{deck}\n")
    _tsv(ordner / "mochi_import.csv", zeilen_mochi, trenner=",")
    _tsv(ordner / "karten_text.tsv", zeilen_text)
    # alle Sprachen: eine Spalte je Sprache, die bei mindestens einer Karte gefüllt ist (es immer)
    try:
        import sprachen
        reihenfolge = list(sprachen.SPRACHEN)
    except Exception:  # noqa: BLE001
        reihenfolge = ["es"]
    codes = [c for c in reihenfolge if c == "es" or any((k.get("rueckseiten") or {}).get(c) for k in karten)]
    _tsv(ordner / "karten_alle_sprachen.csv",
         [[k["bild"], _sicher(k["de"])] + [_sicher((k.get("rueckseiten") or {}).get(c, k["es"] if c == code else ""))
                                          for c in codes] + [_sicher(k.get("notiz"))] for k in karten],
         ";".join(["bild", "de", *codes, "notiz"]) + "\n", trenner=";")
    (ordner / "LIES_MICH.txt").write_text(
        "anki_import.txt  – Anki: Bilder aus „bilder“ in den Ordner collection.media kopieren, dann Datei → Importieren\n"
        "mochi_import.csv – Mochi: als CSV importieren, dabei die CSV und alle Bilder aus „bilder“ gemeinsam wählen\n"
        "karten_text.tsv  – Quizlet, Brainscape, Knowt …: Text einfügen (Trenner Tab, eine Karte je Zeile)\n"
        "karten_alle_sprachen.csv – alle Sprachen nebeneinander (Spalte je Sprachcode, Trenner Semikolon, UTF-8)\n",
        encoding="utf-8")
    return ordner


# --------------------------------------------------------------------------- Einstieg für den Generator
def erzeuge(karten, cfg, ausgabe: Path, auswahl: str, deck: str, sprache: str, gl, melde=print):
    """Schreibt die gewählten Formate nach ausgabe/digital/. Gibt die Liste der Zeilen für „Erzeugt“ zurück."""
    ziel = ausgabe / ORDNER
    ziel.mkdir(parents=True, exist_ok=True)
    deck = " ".join(str(deck or "Me Goos-ta Deutsch").split())[:80] or "Me Goos-ta Deutsch"
    code = getattr(cfg, "sprache", "es") or "es"
    if code != "es":                                       # eigener Stapel je Sprache: „Me Goos-ta Deutsch – Japanisch“
        ui = sprache if sprache in ("de", "en", "es") else "en"
        deck = f"{deck} – {sprach_info(code)['namen'][ui]}"
    mit_bild = [k for k in karten if k.get("front_jpg") and Path(k["front_jpg"]).is_file()]
    erzeugt = []
    for fmt in AUSWAHL.get(auswahl, AUSWAHL["empfohlen"]):
        if fmt == "apkg":
            p = schreibe_apkg(mit_bild, ziel, deck, code)
        elif fmt == "html":
            p = schreibe_lernseite(mit_bild, ziel, deck, sprache, code)
        elif fmt == "pdf":
            p = schreibe_bildschirm_pdf(mit_bild, ziel, cfg, gl)
        else:
            p = schreibe_tabellen(mit_bild, ziel, deck, code)
        erzeugt.append((fmt, p, len(mit_bild)))
    return erzeugt
