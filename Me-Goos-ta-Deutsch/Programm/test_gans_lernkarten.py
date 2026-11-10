#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ME GOOS-TA DEUTSCH – Selbsttest                                     Version 1.5 (06.10.2026)
Prüft Generator, Bildverbesserung (auch Real-ESRGAN), Prüfungen von Schritt 1 und 2, alle Ausgaben, die
Oberfläche samt Sicherheitsregeln, das Startprogramm und die Neuerungen von 1.5 (Gänse-Bild, Bildverbesserung,
Tabelle, automatische Übersetzung – ohne Internet –, mehrere Karten, Update) – in einer Kopie des Projekts mit den
Beispielkarten (deine Dateien und Einstellungen bleiben unberührt). Die großen KI-Läufe werden mit FSRCNN gerechnet, damit der Test nur etwa eine Minute dauert.

Aufruf:  python3 test_gans_lernkarten.py        (Windows: py test_gans_lernkarten.py)
Ergebnis: „ALLE TESTS BESTANDEN“ oder eine Liste der fehlgeschlagenen Prüfungen.
"""

import http.client
import io
import json
import math
import pickle
import zipfile
import os
import re
import socket
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
from PIL import Image

HIER = Path(__file__).resolve().parent
# Beispielbilder: im Download in beispiel-bilder/ (bilder/ entsteht erst beim ersten Start)
BEISPIELBILDER = HIER / "beispiel-bilder" if (HIER / "beispiel-bilder").is_dir() else HIER / "bilder"
sys.path.insert(0, str(HIER))
import gans_lernkarten as gl  # noqa: E402
import ki_modelle  # noqa: E402

MM = 72 / 25.4
ergebnisse = []


def pruefe(name, bedingung, detail=""):
    ergebnisse.append((name, bool(bedingung), detail))
    print(f"  {'OK    ' if bedingung else 'FEHLER'}  {name}" + (f"  ({detail})" if detail and not bedingung else ""))


# ---------- kleiner PDF-Leser ohne Zusatzpakete (reportlab schreibt die Seitenobjekte unkomprimiert) ----------
def pdf_info(pfad):
    roh = Path(pfad).read_bytes().decode("latin-1")
    objekte = re.findall(r"\d+ 0 obj(.*?)endobj", roh, re.S)
    seiten = [o for o in objekte if re.search(r"/Type /Page\b(?!s)", o)]

    def box(text, name):
        m = re.search(rf"/{name}\s*\[\s*([\d.\s-]+)\]", text)
        return [round(float(v) / MM, 1) for v in m.group(1).split()] if m else None

    return dict(seiten=len(seiten),
                media=[box(s, "MediaBox") for s in seiten],
                trim=[box(s, "TrimBox") for s in seiten],
                fonts_eingebettet=roh.count("/FontFile2"),
                fonts_gesamt=len(re.findall(r"/Type /Font\b", roh)),
                titel=(re.search(r"/Title \((.*?)\)", roh) or [None, ""])[1])


def lauf(projekt, *args, sprache="de"):
    t = time.time()
    r = subprocess.run([sys.executable, str(projekt / "gans_lernkarten.py"), *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=projekt,
                       env=dict(os.environ, PYTHONIOENCODING="utf-8", MGD_SPRACHE=sprache))
    return r.returncode, r.stdout + r.stderr, time.time() - t


OBERE_DATEIEN = ("Me Goos-ta Deutsch - Windows.cmd", "Me Goos-ta Deutsch - Mac.command", "LIES MICH ZUERST.html")


def kopiere_projekt(ziel):
    """Kopie im Aufbau des Downloads (Startdateien oben, alles andere in „Programm“), aber ohne die großen
    Real-ESRGAN-Modelle: „auto“ rechnet dort mit FSRCNN (schnell). Gibt den Programmordner zurück."""
    programm = Path(ziel) / "Programm"
    programm.mkdir(parents=True, exist_ok=True)
    for name in OBERE_DATEIEN:
        if (HIER.parent / name).exists():
            shutil.copy2(HIER.parent / name, Path(ziel) / name)
    for name in ("gans_lernkarten.py", "gans_ui.py", "ki_modelle.py", "uebersetzer.py", "starter.py", "beispiel-karten.csv",
                 "LEITFADEN.md", "LEITFADEN_en.md", "LEITFADEN_es.md", "SPEC.md", "test_gans_lernkarten.py",
                 "requirements.txt"):
        if (HIER / name).exists():
            shutil.copy2(HIER / name, programm / name)
    # Der Test arbeitet immer mit den Beispielkarten und -bildern – deine eigenen Karten und Bilder bleiben außen vor
    quelle = HIER / "beispiel-karten.csv" if (HIER / "beispiel-karten.csv").exists() else HIER / "karten.csv"
    shutil.copy2(quelle, programm / "karten.csv")
    if BEISPIELBILDER.is_dir():
        shutil.copytree(BEISPIELBILDER, programm / "bilder", ignore=shutil.ignore_patterns("_entfernt"))
    for ordner in ("beispiel-bilder", "modelle", "schrift", "assets", "ui", "werkzeuge"):
        if (HIER / ordner).exists():
            shutil.copytree(HIER / ordner, programm / ordner,
                            ignore=shutil.ignore_patterns("realesrgan*.npz", "_entfernt", "pakete", "_alt",
                                                          "gans_hintergrund.*"))
    return programm


# =============================================================================================
def test_bildverbesserung():
    print("\n[1] Bildverbesserung")
    # schwarzer Rand wird entfernt, dunkler Bildinhalt bleibt
    a = np.zeros((200, 300, 3), np.uint8)
    a[40:160, 20:290] = 180
    a[40:60, 20:120] = 5                        # dunkles Objekt am oberen Bildrand (soll bleiben)
    a[60:160, 20:22] = 0
    im = gl.beschneide_schwarz(Image.fromarray(a))
    pruefe("schwarze Ränder werden abgeschnitten", im.size[0] < 300 and im.size[1] < 200, f"{im.size}")
    pruefe("dunkler Bildinhalt bleibt erhalten", abs(im.size[1] - 120) <= 4, f"Höhe {im.size[1]}")

    # Guided-Filter: gleiche Größe, keine NaN, glättet Rauschen, erhält Kanten
    rng = np.random.default_rng(1)
    b = np.full((120, 160, 3), 100, np.float32)
    b[:, 80:] = 220
    b += rng.normal(0, 8, b.shape)
    bild = Image.fromarray(np.clip(b, 0, 255).astype(np.uint8))
    out = np.asarray(gl.kantenschonend_glaetten(bild, 2, 0.03 ** 2), np.float32)
    pruefe("Glätten: Größe unverändert, keine Fehlwerte", out.shape == b.shape and np.isfinite(out).all())
    pruefe("Glätten: Rauschen in Flächen reduziert", out[:, 5:70].std() < np.asarray(bild, np.float32)[:, 5:70].std() * 0.8)
    pruefe("Glätten: Kante bleibt scharf", out[:, 85:].mean() - out[:, :75].mean() > 100)

    # KI-Hochskalierung: richtige Größe und plausibles Ergebnis (nahe an bikubisch, aber nicht identisch)
    for k in (2, 3, 4):
        pruefe(f"KI-Modell ×{k} vorhanden", gl.FSRCNN.verfuegbar(k))
    quelle = Image.open(BEISPIELBILDER / sorted(p.name for p in BEISPIELBILDER.glob("*.jpg"))[0]).convert("RGB")
    klein = quelle.resize((160, 120), Image.Resampling.LANCZOS)
    t = time.time()
    gross = gl.FSRCNN.hochskalieren(klein, 2)
    dauer = time.time() - t
    bikub = np.asarray(klein.resize(gross.size, Image.Resampling.BICUBIC), np.float32)
    g = np.asarray(gross, np.float32)
    korr = np.corrcoef(g.ravel(), bikub.ravel())[0, 1]
    pruefe("KI ×2: doppelte Größe", gross.size == (320, 240), f"{gross.size}")
    pruefe("KI ×2: Ergebnis plausibel (Korrelation > 0,97)", korr > 0.97, f"{korr:.3f}")
    pruefe("KI ×2: schärfer als bikubisch", np.abs(np.diff(g, axis=1)).mean() > np.abs(np.diff(bikub, axis=1)).mean())
    pruefe("KI ×2: schnell genug (< 3 s)", dauer < 3, f"{dauer:.2f} s")

    cfg = gl.Konfig(ki="fsrcnn")
    for stufe in ("aus", "standard", "stark"):
        cfg.qualitaet = stufe
        v, methode, _ = gl.verbessere(klein, (333, 250), cfg)
        pruefe(f"Qualität „{stufe}“: Zielgröße stimmt", v.size == (333, 250), methode)

    # Real-ESRGAN (nur wenn das Modell installiert ist): kleiner Ausschnitt, damit es schnell geht
    pruefe("KI-Auswahl „aus“ = Lanczos", gl.ki_methode("aus") == "lanczos")
    if ki_modelle.verfuegbar("realesrgan-x4plus"):
        pruefe("KI-Auswahl „auto“ nimmt Real-ESRGAN", gl.ki_methode("auto") == "realesrgan-x4plus")
        stueck = quelle.crop((150, 150, 198, 198))
        t = time.time()
        g4 = ki_modelle.Hochskalierer("realesrgan-x4plus")(stueck)
        dauer = time.time() - t
        bik = np.asarray(stueck.resize(g4.size, Image.Resampling.BICUBIC), np.float32)
        a4 = np.asarray(g4, np.float32)
        korr = np.corrcoef(a4.ravel(), bik.ravel())[0, 1]
        pruefe("Real-ESRGAN ×4: vierfache Größe", g4.size == (192, 192), f"{g4.size}")
        pruefe("Real-ESRGAN ×4: Ergebnis plausibel (Korrelation > 0,9)", korr > 0.9, f"{korr:.3f}")
        pruefe("Real-ESRGAN ×4: schärfer als bikubisch",
               np.abs(np.diff(a4, axis=1)).mean() > np.abs(np.diff(bik, axis=1)).mean())
        pruefe("Real-ESRGAN ×4: rechnet in vertretbarer Zeit (< 60 s für 48 × 48 px)", dauer < 60, f"{dauer:.1f} s")
    else:
        print("          (Real-ESRGAN nicht installiert – Test übersprungen; Werkzeuge → KI-Modell laden)")

    # Modell-Dateien werden sicher gelesen: Pickle mit fremdem Code wird abgelehnt, falsche Prüfsumme ebenso
    with tempfile.TemporaryDirectory() as tmp:
        boese = Path(tmp) / "boese.pth"
        with zipfile.ZipFile(boese, "w") as z:
            z.writestr("archive/data.pkl", b"cos\nsystem\n(S'echo gehackt'\ntR.")
        try:
            ki_modelle.lies_pth(boese)
            abgelehnt = False
        except pickle.UnpicklingError:
            abgelehnt = True
        pruefe("Modell-Leser lehnt Schadcode im Pickle ab", abgelehnt)
        falsch = Path(tmp) / "falsch.pth"
        falsch.write_bytes(b"kein modell")
        try:
            ki_modelle.lade("realesrgan-x2plus", ziel_ordner=tmp, melde=lambda t: None, quelle=falsch)
            abgelehnt = False
        except ValueError:
            abgelehnt = True
        pruefe("falsche Prüfsumme → nichts installiert", abgelehnt and not (Path(tmp) / "realesrgan-x2plus.npz").exists())


def test_layout():
    print("\n[2] Textlayout der Rückseite")
    gl.registriere_schriften()
    cfg = gl.Konfig()
    _, _, iw, ih = gl._innen(0, 0, cfg.b * gl.mm, cfg.h * gl.mm, cfg)
    z, s, alt, alt_s, w = gl.layout_wort("viejo", iw, ih)
    pruefe("kurzes Wort: eine Zeile, groß", len(z) == 1 and s > 30 and not w, f"{z} {s:.1f}")
    z, s, alt, alt_s, w = gl.layout_wort("muchísima hambre / me muero de hambre", iw, ih)
    pruefe("lange Wendung: zwei Zeilen + Alternative", len(z) == 2 and alt and not w, f"{z} {alt}")
    z, *_ = gl.layout_wort("de | nada", iw, ih)
    pruefe("'|' erzwingt Umbruch", z == ["de", "nada"], f"{z}")
    *_, w = gl.layout_wort("supercalifragilisticoespialidosoextraordinariamente", iw, ih)
    pruefe("zu langes Wort wird gemeldet", bool(w))


def test_generator():
    print("\n[3] Generator – komplette Läufe")
    with tempfile.TemporaryDirectory() as tmp:
        p = kopiere_projekt(Path(tmp))
        n = sum(1 for z in (p / "karten.csv").read_text(encoding="utf-8-sig").splitlines()[1:] if z.strip() and not z.startswith("#"))

        code, log, dauer = lauf(p)
        pruefe("Standardlauf endet ohne Fehler", code == 0, log[-400:])
        pruefe("keine Python-Warnungen", "Warning" not in log and "Traceback" not in log, log[-400:])
        pruefe("Standardlauf dauert < 60 s", dauer < 60, f"{dauer:.1f} s")
        a = p / "ausgabe"
        dr = pdf_info(a / "Me-Goos-ta-Deutsch_Druckerei_88x63.pdf")
        pruefe("Druckerei-PDF: 2 Seiten je Karte", dr["seiten"] == 2 * n, f"{dr['seiten']} statt {2 * n}")
        pruefe("Druckerei-PDF: Seite 94 × 69 mm", all(m == [0.0, 0.0, 94.0, 69.0] for m in dr["media"]), f"{dr['media'][0]}")
        pruefe("Druckerei-PDF: TrimBox = Endformat 88 × 63 mm", all(t == [3.0, 3.0, 91.0, 66.0] for t in dr["trim"]), f"{dr['trim'][0]}")
        pruefe("Druckerei-PDF: alle Schriften eingebettet",
               dr["fonts_eingebettet"] >= 1 and dr["fonts_eingebettet"] == dr["fonts_gesamt"],
               f"{dr['fonts_eingebettet']}/{dr['fonts_gesamt']}")
        hd = pdf_info(a / "Me-Goos-ta-Deutsch_Heimdruck_A4_88x63.pdf")
        pruefe("Heimdruck-PDF: A4, 2 Seiten je 8 Karten",
               hd["seiten"] == 2 * math.ceil(n / 8) and hd["media"][0] == [0.0, 0.0, 210.0, 297.0], f"{hd['seiten']} {hd['media'][0]}")
        pb = pdf_info(a / "Me-Goos-ta-Deutsch_Pruefbogen.pdf")
        pruefe("Prüfbogen: 5 Karten je Seite", pb["seiten"] == math.ceil(n / 5), f"{pb['seiten']}")
        pngs = sorted((a / "einzelbilder").glob("*.png"))
        pruefe("Einzelbilder: 2 PNG je Karte", len(pngs) == 2 * n, f"{len(pngs)}")
        if pngs:
            with Image.open(pngs[0]) as im:
                pruefe("Einzelbilder: 300 dpi inkl. Beschnitt (ca. 1110 × 815 px)",
                       abs(im.size[0] - 1110) <= 1 and abs(im.size[1] - 815) <= 1, f"{im.size}")
        jpgs = list((a / ".cache").glob("*.jpg"))
        groessen = {Image.open(j).size for j in jpgs}
        pruefe("Vorderseiten in 300 dpi (957 × 661 px)", groessen == {(957, 661)}, f"{groessen}")
        for v in ("VORLAGE_Druckerei_88x63_quer.pdf", "VORLAGE_Heimdruck_A4_88x63.pdf"):
            pruefe(f"Vorlage {v} erzeugt", (p / "vorlagen" / v).exists() and pdf_info(p / "vorlagen" / v)["seiten"] == 2)

        code, log, dauer2 = lauf(p)
        pruefe("zweiter Lauf nutzt den Zwischenspeicher", code == 0 and "0 Bilder neu" in log, log[:300])
        pruefe("zweiter Lauf schneller", dauer2 < dauer, f"{dauer2:.1f} s / {dauer:.1f} s")

        code, log, _ = lauf(p, "--hochkant", "--nur", "druckerei", "--ohne-png")
        hk = pdf_info(a / "Me-Goos-ta-Deutsch_Druckerei_88x63_hochkant.pdf")
        pruefe("--hochkant: Seite 69 × 94 mm, TrimBox 63 × 88", code == 0 and hk["media"][0] == [0.0, 0.0, 69.0, 94.0]
               and hk["trim"][0] == [3.0, 3.0, 66.0, 91.0], f"{hk['media'][0]} {hk['trim'][0]}")
        for args in (["--qualitaet", "aus"], ["--qualitaet", "stark"], ["--ohne-ki"], ["--ki", "aus"], ["--rs-drehen"]):
            code, log, _ = lauf(p, *args, "--nur", "druckerei", "--ohne-png")
            pruefe(f"Schalter {' '.join(args)} funktioniert", code == 0, log[-300:])
        code, log, _ = lauf(p, "--format", "74x52", "--nur", "bogen")
        pruefe("--format 74x52: Heimdruck mit 2 × 5 Karten", code == 0 and "2 × 5 = 10" in log, log[-300:])
        code, log, _ = lauf(p, "--format", "abc")
        pruefe("ungültiges Format wird abgelehnt", code != 0)
        code, log, _ = lauf(p, "--nur", "pruefbogen", sprache="es")
        pruefe("Meldungen auf Spanisch (MGD_SPRACHE=es)", code == 0 and "cartas" in log and "Listo" in log, log[-200:])
        code, log, _ = lauf(p, "--nur", "pruefbogen", sprache="en")
        pruefe("Meldungen auf Englisch (MGD_SPRACHE=en)", code == 0 and "cards" in log and "Done" in log, log[-200:])

        # Fehlerfälle in der Kartenliste
        csv = (p / "karten.csv").read_text(encoding="utf-8-sig")
        (p / "karten.csv").write_text(csv + "gans-gibtsnicht.jpg;Gans weg;perdido;\n"
                                            "gans-alt.jpg;Gans alt;;leer\n"
                                            "#gans-alt.jpg;auskommentiert;x;\n", encoding="utf-8-sig")
        code, log, _ = lauf(p, "--nur", "pruefbogen")
        pruefe("fehlendes Bild wird gemeldet, Rest läuft", code == 0 and "gans-gibtsnicht.jpg" in log, log[-300:])
        pruefe("leere Spalte 'es' wird gemeldet", "ist leer" in log)
        (p / "karten.csv").write_text("bild;de;es\nnichts.jpg;x;y\n", encoding="utf-8")
        code, log, _ = lauf(p, "--nur", "pruefbogen")
        pruefe("ohne gültige Karten: klare Fehlermeldung", code == 1 and "keine gültigen Karten" in log, log[-300:])


def test_kartenliste():
    print("\n[4] Kartenliste, Dateinamen, Kartenauswahl")
    pruefe("Dateiname aus Text (Umlaute)", gl.dateiname_aus_text("Gans aufmüpfig") == "gans-aufmuepfig.jpg")
    pruefe("Dateiname aus Text (ß, Akzent, Sonderzeichen)", gl.dateiname_aus_text("Gans groß & café!", ".PNG") == "gans-gross-cafe.png")
    pruefe("Kartenauswahl 1,3,5-7", gl.parse_auswahl("1,3,5-7") == {1, 3, 5, 6, 7} and gl.parse_auswahl("") is None)
    with tempfile.TemporaryDirectory() as tmp:
        p = kopiere_projekt(Path(tmp))
        csv_pfad = p / "karten.csv"
        spalten, zeilen, _ = gl.lies_csv(csv_pfad)
        zeilen[1]["bild"] = "#" + zeilen[1]["bild"]
        zeilen[0]["kategorie"] = "Natur"
        gl.schreibe_csv(csv_pfad, zeilen, spalten)
        sp2, z2, _ = gl.lies_csv(csv_pfad)
        pruefe("Zusatzspalte bleibt beim Speichern erhalten", "kategorie" in sp2 and z2[0]["kategorie"] == "Natur")
        pruefe("Sicherung karten.bak.csv angelegt", (p / "karten.bak.csv").exists())
        karten, _ = gl.lies_karten(csv_pfad, p / "bilder")
        pruefe("ausgeschaltete (#) Karte wird nicht gedruckt", len(karten) == len(zeilen) - 1 and karten[1]["nr"] == 2)
        code, log, _ = lauf(p, "--karten", "2-3", "--nur", "druckerei")
        pruefe("--karten 2-3: nur zwei Karten", code == 0 and "4 Seiten" in log, log[-300:])
        bericht = json.loads((p / "ausgabe" / "bericht.json").read_text(encoding="utf-8"))
        pruefe("bericht.json mit Auswahl und Bildqualität", bericht["auswahl"] == [2, 3] and
               all("ppi" in v for v in bericht["karten"].values()))
        pngs = sorted(x.name for x in (p / "ausgabe" / "einzelbilder").glob("*.png"))
        pruefe("Einzelbilder nach Kartennummer benannt", pngs == ["02_hinten.png", "02_vorn.png", "03_hinten.png", "03_vorn.png"], f"{pngs}")
        code, log, _ = lauf(p, "--karten", "1-x")
        pruefe("ungültige Kartenauswahl wird abgelehnt", code != 0 and "nicht verstanden" in log)


def _codes(meldungen, stufe=None):
    return {m["code"] for m in meldungen if stufe is None or m["stufe"] == stufe}


def test_schritte():
    print("\n[5] Schritt 1 „Bild vorbereiten“ und Schritt 2 „Karte beschriften“ – Prüfungen")
    gl.registriere_schriften()
    gl.setze_sprache("de")
    cfg = gl.Konfig(ki="fsrcnn")
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "heic.heic").write_bytes(b"\x00\x00\x00\x18ftypheic" + b"\x00" * 64)
        a = gl.analysiere_bild(t / "heic.heic", cfg)
        pruefe("HEIC wird mit Anleitung abgelehnt", not a["ok"] and "b_heic" in _codes(a["meldungen"], "fehler"))
        (t / "text.jpg").write_text("kein Bild")
        a = gl.analysiere_bild(t / "text.jpg", cfg)
        pruefe("kaputte Datei wird abgelehnt", not a["ok"] and "b_unlesbar" in _codes(a["meldungen"], "fehler"))
        Image.new("RGB", (60, 50), "red").save(t / "winzig.png")
        a = gl.analysiere_bild(t / "winzig.png", cfg)
        pruefe("viel zu kleines Bild wird abgelehnt", not a["ok"] and "b_winzig" in _codes(a["meldungen"], "fehler"))
        quelle = Image.open(BEISPIELBILDER / "gans-alt.jpg").convert("RGB")
        hoch = Image.new("RGB", (360, 520), "black")
        hoch.paste(quelle.resize((320, 480)), (20, 20))
        hoch.save(t / "hoch.jpg", quality=90)
        a = gl.analysiere_bild(t / "hoch.jpg", cfg)
        pruefe("Hochformat + schwarze Ränder werden erkannt", a["ok"] and {"b_hochkant", "b_raender"} <= _codes(a["meldungen"]),
               f"{_codes(a['meldungen'])}")
        a90 = gl.analysiere_bild(t / "hoch.jpg", cfg, drehung=90)
        pruefe("Drehen um 90° vertauscht Breite und Höhe", a90["groesse"] == a["groesse"][::-1], f"{a90['groesse']}")
        a = gl.analysiere_bild(t / "hoch.jpg", cfg, fit="cover")
        pruefe("„Fläche füllen“ warnt vor starkem Beschnitt", "b_cover_schnitt" in _codes(a["meldungen"], "warnung"))
        Image.new("RGBA", (300, 220), (0, 0, 0, 0)).save(t / "transparent.png")
        a = gl.analysiere_bild(t / "transparent.png", cfg)
        pruefe("Transparenz und geringe Auflösung werden gemeldet",
               {"b_transparent", "b_ppi_gering"} <= _codes(a["meldungen"]), f"{_codes(a['meldungen'])}")
        Image.new("RGB", (400, 300), "blue").save(t / "bild.gif")
        a = gl.analysiere_bild(t / "bild.gif", cfg)
        pruefe("GIF wird zum Umwandeln vorgemerkt", a["ok"] and a["umwandeln"] and "b_format_umwandeln" in _codes(a["meldungen"]))
        shutil.copy2(BEISPIELBILDER / "gans-alt.jpg", t / "kopie.jpg")
        a = gl.analysiere_bild(t / "kopie.jpg", cfg, bilder_dir=BEISPIELBILDER)
        pruefe("Doppeltes Bild wird erkannt", a.get("doppelt_von") == "gans-alt.jpg")

    name, m = gl.pruefe_name("", ".jpg", set())
    pruefe("Name: leerer Text ist ein Fehler", name is None and "n_text_leer" in _codes(m, "fehler"))
    name, m = gl.pruefe_name("Gans  alt", ".jpg", {"gans-alt.jpg"})
    pruefe("Name: vorhandene Datei ist ein Fehler", name == "gans-alt.jpg" and "n_kollision" in _codes(m, "fehler"))
    name, m = gl.pruefe_name("Gans alt", ".jpg", {"gans-alt.jpg"}, ersetzen=True)
    pruefe("Name: „ersetzen“ macht daraus eine Warnung", "n_ersetzen" in _codes(m, "warnung") and not _codes(m, "fehler"))
    name, m = gl.pruefe_name("Ente alt", ".png", set())
    pruefe("Name: Tipp, wenn der Text nicht mit „Gans“ beginnt", name == "ente-alt.png" and "n_ohne_gans" in _codes(m, "info"))

    def k(es, de="Gans alt", andere=()):
        return gl.pruefe_karte(de, es, cfg, andere=andere)
    pruefe("Karte: leeres Wort ist ein Fehler", not k("")["ok"] and "k_es_leer" in _codes(k("")["meldungen"]))
    pruefe("Karte: gutes Wort passt", k("viejo")["ok"] and "k_passt" in _codes(k("viejo")["meldungen"], "ok"))
    pruefe("Karte: deutscher Umlaut wird angemahnt", "k_umlaut" in _codes(k("Gänse")["meldungen"], "warnung"))
    pruefe("Karte: spanisches ü ist erlaubt", "k_umlaut" not in _codes(k("pingüino")["meldungen"]))
    pruefe("Karte: Excel-Formel wird blockiert", not k("=HYPERLINK(1)")["ok"])
    pruefe("Karte: zu langes Wort wird gemeldet", "haupt_zu_lang" in _codes(k("supercalifragilisticoespialidosoextraordinariamente")["meldungen"]))
    pruefe("Karte: zu viele Alternativen", "k_alternativen" in _codes(k("a / b / c / d")["meldungen"]))
    pruefe("Karte: ¿ bei Fragen", "k_frage" in _codes(k("cómo estás?")["meldungen"], "info"))
    pruefe("Karte: nicht druckbares Zeichen", "k_zeichen" in _codes(k("hola 🦆")["meldungen"], "fehler"))
    pruefe("Karte: gleich wie Deutsch", "k_gleich" in _codes(k("Gans alt")["meldungen"], "warnung"))
    pruefe("Karte: doppeltes Wort als Hinweis",
           "k_doppelt" in _codes(k("viejo", andere=[{"es": "viejo / anciano", "nr": 4, "bild": "gans-alt.jpg"}])["meldungen"]))
    gl.setze_sprache("es")
    texte = " ".join(x["text"] for x in k("")["meldungen"])
    gl.setze_sprache("en")
    texte_en = " ".join(x["text"] for x in k("")["meldungen"])
    gl.setze_sprache("de")
    pruefe("Meldungen in Spanisch und Englisch", "español" in texte and "Spanish" in texte_en, texte[:80])


def _freier_port():
    with socket.socket() as so:
        so.bind(("127.0.0.1", 0))
        return so.getsockname()[1]


class Sitzung:
    """Kleiner HTTP-Client für den Test: folgt keinen Umleitungen, setzt Cookie und Token selbst."""
    def __init__(self, port):
        self.port, self.cookie, self.token, self.sprache = port, None, None, "de"

    def anfrage(self, pfad, daten=None, roh=None, methode=None, kopf=None, mit_cookie=True, mit_token=True):
        h = {"Host": f"127.0.0.1:{self.port}", "X-GL-Sprache": self.sprache}
        if mit_cookie and self.cookie:
            h["Cookie"] = self.cookie
        if mit_token and self.token:
            h["X-GL-Token"] = self.token
        body = None
        if daten is not None:
            body = json.dumps(daten).encode("utf-8")
            h["Content-Type"] = "application/json"
        elif roh is not None:
            body = roh
        h.update(kopf or {})
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=120)
        c.request(methode or ("POST" if body is not None else "GET"), pfad, body=body, headers=h)
        r = c.getresponse()
        inhalt = r.read()
        kopfzeilen = {k.lower(): v for k, v in r.getheaders()}
        c.close()
        return r.status, kopfzeilen, inhalt

    def json(self, pfad, daten=None, **kw):
        code, _, inhalt = self.anfrage(pfad, daten=daten, **kw)
        try:
            return code, json.loads(inhalt)
        except ValueError:
            return code, {}


def test_oberflaeche():
    print("\n[6] Oberfläche (gans_ui.py) und Sicherheit")
    import gans_ui
    original = gl.baue_parser

    def erweitert():
        ap = original()
        g = ap.add_argument_group("Zukunft")
        act = g.add_argument("--test-funktion", action="store_true", help="nur für den Test")
        act.ui_label = gl.L("Test-Funktion", "Test feature", "Función de prueba")
        return ap
    gl.baue_parser = erweitert
    try:
        felder = gans_ui.alle_felder()
    finally:
        gl.baue_parser = original
    pruefe("neuer Schalter erscheint automatisch in der Oberfläche", "test_funktion" in felder and felder["test_funktion"]["art"] == "schalter")
    parser_dests = {a.dest for a in gl.baue_parser()._actions if a.option_strings and a.dest not in ("help", "version", "ohne_ki")}
    pruefe("alle Schalter des Generators sind in der Oberfläche", parser_dests == set(gans_ui.alle_felder()),
           f"{parser_dests ^ set(gans_ui.alle_felder())}")
    argv = gans_ui.argv_aus({"qualitaet": "stark", "rand": "3,5", "hochkant": True, "beschnitt": "4"})
    pruefe("Werte → Befehlszeile als --schalter=wert (nur Abweichungen)",
           argv == ["--qualitaet=stark", "--beschnitt=4", "--hochkant"], f"{argv}")
    pruefe("Wert mit Minuszeichen bleibt ein Wert", gans_ui.parse(gans_ui.argv_aus({"versatz_x": "-1.5"}))[0].versatz_x == -1.5)
    pruefe("Markdown wird zu HTML", "<table>" in gans_ui.markdown_html("| a | b |\n| --- | --- |\n| 1 | 2 |") and
           "<h2>" in gans_ui.markdown_html("## Titel"))
    html_ = gans_ui.markdown_html('[x](https://a.example/"onmouseover="alert(1)) <script>alert(1)</script>')
    pruefe("Hilfe-Text kann kein Skript einschleusen", "<script>" not in html_ and 'onmouseover="' not in html_, html_)

    with tempfile.TemporaryDirectory() as tmp:
        p = kopiere_projekt(Path(tmp))
        port = _freier_port()
        proc = subprocess.Popen([sys.executable, str(p / "gans_ui.py"), "--kein-browser", "--port", str(port)], cwd=p,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        try:
            adresse = None
            for _ in range(100):
                zeile = proc.stdout.readline().decode("utf-8", "replace")
                m = re.search(r"http://127\.0\.0\.1:\d+/\?k=([A-Za-z0-9_-]+)", zeile)
                if m:
                    adresse = m.group(0)
                    break
            pruefe("Oberfläche startet und nennt die Start-Adresse", bool(adresse))
            if not adresse:
                return
            se = Sitzung(port)
            for _ in range(50):
                try:
                    code, _, _ = se.anfrage("/")
                    break
                except OSError:
                    time.sleep(0.2)
            pruefe("ohne Startschlüssel keine Oberfläche", code == 403)
            code, kopf, _ = se.anfrage("/?k=falsch")
            pruefe("falscher Startschlüssel wird abgewiesen", code == 403)
            code, kopf, _ = se.anfrage(adresse.split(str(port), 1)[1])
            keks = kopf.get("set-cookie", "")
            pruefe("Startschlüssel → Sitzungs-Cookie (HttpOnly, SameSite=Strict)",
                   code == 303 and "HttpOnly" in keks and "SameSite=Strict" in keks, keks)
            se.cookie = keks.split(";")[0]
            code, kopf, seite = se.anfrage("/")
            m = re.search(rb'const TOKEN = "([^"]+)"', seite)
            se.token = m.group(1).decode() if m else None
            csp = kopf.get("content-security-policy", "")
            pruefe("Seite mit Cookie geladen", code == 200 and bool(se.token))
            pruefe("Sicherheits-Kopfzeilen (CSP mit Nonce, kein Einbetten, kein Referrer)",
                   "nonce-" in csp and "frame-ancestors 'none'" in csp and kopf.get("x-frame-options") == "DENY"
                   and kopf.get("referrer-policy") == "no-referrer" and "Python" not in kopf.get("server", ""), csp)
            pruefe("ohne Cookie kein API-Zugriff", se.anfrage("/api/status", mit_cookie=False)[0] == 403)
            pruefe("fremde Adresse (DNS-Rebinding) wird abgewiesen",
                   se.anfrage("/api/status", kopf={"Host": f"evil.example:{port}"})[0] == 403)
            pruefe("Schreiben ohne Token wird abgewiesen",
                   se.anfrage("/api/einstellungen", daten={"werte": {}}, mit_token=False)[0] == 403)
            pruefe("Schreiben von fremder Webseite (Origin) wird abgewiesen",
                   se.anfrage("/api/einstellungen", daten={"werte": {}}, kopf={"Origin": "https://evil.example"})[0] == 403)
            code, st = se.json("/api/status")
            pruefe("Status: Version und Bildverbesserung", code == 200 and st["version"] == gl.VERSION and st["ki_methode"] == "fsrcnn",
                   f"{st.get('ki_methode')}")
            code, daten = se.json("/api/karten")
            n = len(daten["karten"])
            pruefe("Kartenliste wird geladen", code == 200 and n >= 1 and daten["karten"][0]["nr"] == 1)
            b0 = daten["karten"][0]["bild"]
            code, kopf, _ = se.anfrage(f"/api/vorschau?bild={b0}&seite=vorn")
            pruefe("Vorschau Vorderseite", code == 200 and kopf.get("content-type", "").startswith("image/"))
            code, kopf, bild = se.anfrage(f"/api/vorschau?bild={b0}&seite=hinten&es=hola")
            pruefe("Vorschau Rückseite", code == 200 and kopf.get("content-type", "").startswith("image/") and len(bild) > 1000)
            for weg in ("/datei/ausgabe/..%2Fkarten.csv", "/bild/..%5Ckarten.csv", "/bild/gans-alt.jpg:Zone.Identifier",
                        "/api/vorschau?bild=../karten.csv&seite=vorn"):
                pruefe(f"Pfad-Ausbruch abgewiesen: {weg}", se.anfrage(weg)[0] in (400, 404))
            code, r = se.json("/api/einstellungen", daten={"werte": {"qualitaet": "stark"}})
            pruefe("Einstellungen speichern → Befehl", code == 200 and "--qualitaet=stark" in r["befehl"])
            code, r = se.json("/api/einstellungen", daten={"werte": {"format": "12x"}})
            pruefe("ungültige Einstellung wird gemeldet", bool(r.get("fehler")))
            aussen = "C:/Windows/System32" if os.name == "nt" else "/etc"
            code, r = se.json("/api/einstellungen", daten={"werte": {"ausgabe": aussen}})
            pruefe("Ordner außerhalb von Projekt/Benutzerordner abgelehnt", code == 400 and "Benutzerordner" in r.get("fehler", ""))
            code, r = se.json("/api/einstellungen", daten={"werte": {"csv": str(p / "karten.txt")}})
            pruefe("Kartenliste muss .csv sein", code == 400)
            se.json("/api/einstellungen", daten={"werte": {}})
            (p / "ausgabe").mkdir(exist_ok=True)
            (p / "ausgabe" / "boese.py").write_text("print('x')")
            code, r = se.json("/api/oeffnen", daten={"ziel": "ausgabe/boese.py"})
            pruefe("„Öffnen“ startet keine Programme/Skripte", code == 400 and "Dateityp" in r.get("fehler", ""), str(r))

            # Schritt 1: Entwurf hochladen, prüfen, übernehmen
            roh = (p / "bilder" / b0).read_bytes()
            code, d = se.json("/api/entwurf?name=Gans_test-bild.jpg", roh=roh)
            pruefe("Schritt 1: Bild hochladen und prüfen", code == 200 and d["lesbar"] and d["de"] == "Gans test bild", f"{d.get('de')}")
            pruefe("Schritt 1: Doppeltes Bild wird erkannt", "b_doppelt" in _codes(d["meldungen"]))
            code, d = se.json("/api/entwurf-pruefen", daten={"id": d["id"], "de": "", "drehung": 90})
            pruefe("Schritt 1: ohne Text kein Übernehmen", code == 200 and not d["ok"] and d["drehung"] == 90)
            code, r = se.json("/api/entwurf-uebernehmen", daten={"id": d["id"], "de": ""})
            pruefe("Schritt 1: Übernehmen wird bei Fehlern verweigert", code == 400)
            code, d = se.json("/api/entwurf-pruefen", daten={"id": d["id"], "de": "Gans neu", "drehung": 0, "fit": "cover"})
            pruefe("Schritt 1: mit Text bereit", d["ok"] and d["dateiname"] == "gans-neu.jpg" and d["fit"] == "cover", f"{d.get('dateiname')}")
            code, kopf, _ = se.anfrage(f"/api/entwurf-bild?id={d['id']}&art=vorn&drehung=90&fit=cover")
            pruefe("Schritt 1: Vorschau der Vorderseite", code == 200 and kopf.get("content-type", "").startswith("image/"))
            code, r = se.json("/api/entwurf-uebernehmen", daten={"id": d["id"], "de": "Gans neu", "fit": "cover"})
            text = (p / "karten.csv").read_text(encoding="utf-8-sig")
            pruefe("Schritt 1: Bild liegt im Ordner, Zeile in karten.csv",
                   code == 200 and (p / "bilder" / "gans-neu.jpg").exists() and "gans-neu.jpg;Gans neu;;;cover" in text, text[-80:])
            pruefe("Schritt 1 → 2: neue Karte ist „offen“", any(k["bild"] == "gans-neu.jpg" and k["offen"] for k in r["karten"]["karten"]))
            code, d2 = se.json("/api/entwurf?name=gans-alt.png", roh=roh)
            code, d2 = se.json("/api/entwurf-pruefen", daten={"id": d2["id"], "de": "Gans alt"})
            pruefe("Schritt 1: gleicher Name mit anderer Endung zählt als vorhanden",
                   not d2["ok"] and d2["vorhanden"] == "gans-alt.jpg", f"{d2.get('vorhanden')}")
            se.json("/api/entwurf-weg", daten={"id": d2["id"]})
            code, d3 = se.json("/api/entwurf?name=foto.heic", roh=b"\x00\x00\x00\x18ftypheic" + b"\x00" * 64)
            pruefe("Schritt 1: HEIC → verständliche Fehlermeldung", code == 200 and not d3["ok"] and not d3["lesbar"]
                   and "iPhone" in " ".join(m["text"] for m in d3["meldungen"]))
            code, liste = se.json("/api/entwuerfe")
            pruefe("Schritt 1: offene Entwürfe bleiben erhalten", code == 200 and [x["id"] for x in liste] == [d3["id"]])
            se.json("/api/entwurf-weg", daten={"id": d3["id"]})

            # Schritt 2: beschriften
            code, r = se.json("/api/karte-pruefen", daten={"bild": "gans-neu.jpg", "de": "Gans neu", "es": ""})
            pruefe("Schritt 2: leeres Wort → Fehler", code == 200 and not r["ok"])
            code, r = se.json("/api/karte-speichern", daten={"bild": "gans-neu.jpg", "de": "Gans neu", "es": ""})
            pruefe("Schritt 2: Speichern ohne Wort verweigert", code == 400)
            code, r = se.json("/api/karte-speichern", daten={"bild": "gans-neu.jpg", "de": "Gans neu", "es": "nuevo / reciente",
                                                             "notiz": "Adjektiv", "fit": "cover"})
            text = (p / "karten.csv").read_text(encoding="utf-8-sig")
            pruefe("Schritt 2: Karte gespeichert", code == 200 and "gans-neu.jpg;Gans neu;nuevo / reciente;Adjektiv;cover" in text, text[-90:])
            code, r = se.json("/api/karte-speichern", daten={"bild": "../karten.csv", "de": "x", "es": "y"})
            pruefe("Schritt 2: ungültiger Bildname abgewiesen", code == 400)

            # Sprache
            code, r = se.json("/api/sprache", daten={"sprache": "es"})
            se.sprache = "es"
            code, o = se.json("/api/optionen")
            labels = {f["label"] for g in o["gruppen"] for f in g["felder"]}
            pruefe("Sprache Spanisch: Beschriftungen der Schalter", "Calidad" in labels and "Ampliación con IA" in labels)
            code, r = se.json("/api/karte-pruefen", daten={"bild": "gans-neu.jpg", "de": "Gans neu", "es": ""})
            pruefe("Sprache Spanisch: Prüfmeldungen", "español" in r["meldungen"][0]["text"])
            code, w = se.json("/api/werkzeuge")
            pruefe("Sprache Spanisch: Werkzeuge", any(x["titel"] == "Autoprueba" for x in w))
            se.sprache = "de"
            se.json("/api/sprache", daten={"sprache": "de"})
            code, w = se.json("/api/werkzeuge")
            pruefe("Werkzeug „KI-Modell laden“ mit Zustand", any(x["id"] == "modell-x4" and x["zustand"] for x in w))

            # Lauf, Ergebnisse, ZIP, Hilfe
            code, r = se.json("/api/lauf", daten={"art": "generator", "nur": "pruefbogen"})
            pruefe("Lauf starten", code == 200 and r["laeuft"])
            st = {}
            for _ in range(600):
                st = se.json("/api/lauf")[1]
                if not st["laeuft"]:
                    break
                time.sleep(0.2)
            pruefe("Lauf endet erfolgreich mit Protokoll", st.get("code") == 0 and any("Fertig" in z for z in st.get("zeilen", [])),
                   str(st.get("zeilen", [])[-3:]))
            code, erg = se.json("/api/ergebnisse")
            pruefe("Ergebnisse listen den Prüfbogen", any(d["titel"] == "Prüfbogen" for d in erg["dateien"]))
            code, r = se.json("/api/werkzeug", daten={"id": "zip"})
            zp = p / "ausgabe" / "Me-Goos-ta-Deutsch_Projekt.zip"
            namen = zipfile.ZipFile(zp).namelist() if zp.exists() else []
            pruefe("Werkzeug Projekt-ZIP (Startdateien oben, Programm darunter)", code == 200
                   and "Me-Goos-ta-Deutsch/Programm/gans_ui.py" in namen
                   and "Me-Goos-ta-Deutsch/Me Goos-ta Deutsch - Windows.cmd" in namen
                   and "Me-Goos-ta-Deutsch/LIES MICH ZUERST.html" in namen
                   and not any(n.endswith("ui_einstellungen.json") for n in namen), str(namen[:4]))
            code, r = se.json("/api/hilfe?doc=leitfaden")
            pruefe("Hilfe zeigt den Leitfaden", code == 200 and "<h2>" in r["html"])
            code, _ = se.json("/api/bild-weg", daten={"name": "gans-neu.jpg"})
            pruefe("Bild in den Papierkorb verschieben", code == 200 and (p / "bilder" / "_entfernt" / "gans-neu.jpg").exists())
            code, _ = se.json("/api/beenden", daten={})
            try:
                proc.wait(timeout=10)
                beendet = True
            except subprocess.TimeoutExpired:
                beendet = False
            pruefe("„Beenden“ stoppt die Oberfläche", code == 200 and beendet)
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()


def test_start():
    print("\n[7] Startprogramm und Startdateien")
    import starter
    oben = HIER.parent
    pruefe("starter.py gleiche Version wie der Generator", starter.VERSION == gl.VERSION, starter.VERSION)
    for n in ("me-goosta-symbol.svg", "me-goosta-symbol.png", "me-goosta-symbol.ico", "me-goosta-symbol-96.png",
              "me-goosta-symbol.icns"):
        pruefe(f"Symbol {n} vorhanden", (HIER / "assets" / n).exists())
    with Image.open(HIER / "assets" / "me-goosta-symbol.ico") as ico:
        pruefe("ICO enthält 16–256 px", {(16, 16), (32, 32), (256, 256)} <= set(ico.info.get("sizes", [])))
    pruefe("pip-Rad für das embeddable Python von Windows liegt bei", any((HIER / "werkzeuge").glob("pip-*-py3-none-any.whl")))
    req = (HIER / "requirements.txt").read_text()
    pruefe("requirements.txt mit Ober- und Untergrenzen", all("<" in z and ">=" in z for z in req.split()) and "pillow>=10.3" in req)

    # --- Windows-Startdatei ---
    cmd_pfad = oben / "Me Goos-ta Deutsch - Windows.cmd"
    pruefe("Windows-Startdatei vorhanden", cmd_pfad.exists())
    if cmd_pfad.exists():
        roh = cmd_pfad.read_bytes()
        text = roh.decode("ascii", "replace")
        pruefe("Windows-Startdatei: nur ASCII, nur Windows-Zeilenenden",
               all(c < 128 for c in roh) and roh.count(b"\n") == roh.count(b"\r\n"))
        sprungziele = set(re.findall(r"(?:goto|call)\s+:(\w+)", text, re.I)) - {"eof"}
        sprungziele |= {f"texte_{s}" for s in ("de", "en", "es")} if "call :texte_%SPR%" in text else set()
        sprungziele.discard("texte_")
        marken = set(re.findall(r"^:(\w+)", text, re.M))
        pruefe("Windows-Startdatei: alle Sprungziele vorhanden", sprungziele <= marken, str(sprungziele - marken))
        bloecke = re.findall(r"\(\r?\n(.*?)\r?\n\)", text, re.S)
        pruefe("Windows-Startdatei: keine Klammerblöcke mit Variablen (Pfade mit „)“ bleiben sicher)",
               all("%" not in b for b in bloecke))
        sha = re.search(r'set "PY_SHA=([0-9a-f]+)"', text)
        url = re.search(r'set "PY_URL=(https://www\.python\.org/ftp/python/(3\.\d+\.\d+)/python-\2-embed-amd64\.zip)"', text)
        ver = re.search(r'set "PY_VER=([0-9.]+)"', text)
        pruefe("Windows-Startdatei: Python-Version, Adresse und SHA-256 passen zusammen",
               bool(sha and len(sha.group(1)) == 64 and url and ver and url.group(2) == ver.group(1)))
        pruefe("Windows-Startdatei: python313._pth gibt site-packages frei",
               "echo Lib\\site-packages" in text and "echo import site" in text and ("python3%s._pth" % ver.group(1).split(".")[1]) in text)
        pruefe("Windows-Startdatei: Systemprogramme mit vollem Pfad (kein fremdes curl/tar aus PATH)",
               not re.search(r"^\s*(curl|tar|certutil|powershell)(\.exe)?\s", text, re.M | re.I))
    # --- Mac-/Linux-Startdatei ---
    sh_pfad = oben / "Me Goos-ta Deutsch - Mac.command"
    pruefe("Mac-Startdatei vorhanden", sh_pfad.exists())
    if sh_pfad.exists():
        roh = sh_pfad.read_bytes()
        pruefe("Mac-Startdatei: Unix-Zeilenenden, startet mit #!/bin/sh", b"\r" not in roh and roh.startswith(b"#!/bin/sh\n"))
        if os.name != "nt":
            pruefe("Mac-Startdatei ausführbar", os.access(sh_pfad, os.X_OK))
            if shutil.which("sh"):
                r = subprocess.run(["sh", "-n", str(sh_pfad)], capture_output=True, text=True)
                pruefe("Mac-Startdatei: Syntax in Ordnung (sh -n)", r.returncode == 0, r.stderr)
        text = roh.decode("utf-8")
        hashes = re.findall(r'^SHA_(\w+)="([0-9a-f]+)"', text, re.M)
        pruefe("Mac-Startdatei: Prüfsummen für macOS/Linux × Intel/ARM",
               len(hashes) == 4 and all(len(h) == 64 for _, h in hashes), str(hashes))
    lies = oben / "LIES MICH ZUERST.html"
    pruefe("Anleitung „LIES MICH ZUERST.html“ in drei Sprachen",
           lies.exists() and all(f'data-lang="{s}"' in lies.read_text(encoding="utf-8") for s in ("de", "en", "es")))

    # --- Startprogramm: Erkennung des ersten Starts, Sprache, Meldungen ---
    with tempfile.TemporaryDirectory() as tmp:
        alt = (starter.DATEN, starter.STEMPEL, starter.SPRACHE)
        starter.DATEN, starter.STEMPEL = Path(tmp), Path(tmp) / "eingerichtet.json"
        try:
            pruefe("Erster Start wird erkannt", starter.brauche_einrichtung() == "erst")
            st = dict(prefix=sys.prefix, python=sys.version.split()[0], pakete=starter.paket_signatur(),
                      ordner=[starter.ordner_schluessel()])
            starter.schreibe_json(starter.STEMPEL, st)
            pruefe("Eingerichteter Ordner startet direkt", starter.brauche_einrichtung() is None)
            pruefe("„Reparatur“ erzwingt die Einrichtung", starter.brauche_einrichtung(True) == "reparatur")
            starter.schreibe_json(starter.STEMPEL, dict(st, ordner=["anderer"]))
            pruefe("Neuer Programmordner wird erkannt", starter.brauche_einrichtung() == "ordner")
            starter.schreibe_json(starter.STEMPEL, dict(st, pakete="alt"))
            pruefe("Neue Paketliste wird erkannt", starter.brauche_einrichtung() == "pakete")
            starter.schreibe_json(starter.STEMPEL, dict(st, prefix="/anderes/python"))
            pruefe("Anderes Python wird erkannt", starter.brauche_einrichtung() == "python")
        finally:
            starter.DATEN, starter.STEMPEL, starter.SPRACHE = alt
    alt_env = os.environ.get("MGD_SPRACHE")
    os.environ["MGD_SPRACHE"] = "es"
    gespeichert = (HIER / "ui_einstellungen.json").exists()
    pruefe("Sprache des Startprogramms folgt MGD_SPRACHE (ohne gespeicherte Wahl)",
           gespeichert or starter.ermittle_sprache() == "es")
    if alt_env is None:
        os.environ.pop("MGD_SPRACHE", None)
    else:
        os.environ["MGD_SPRACHE"] = alt_env
    for s in ("de", "en", "es"):
        starter.SPRACHE = s
        try:
            ok = all(starter.T(k) for k in starter.TEXTE["de"]) and set(starter.TEXTE[s]) == set(starter.TEXTE["de"])
        except (KeyError, IndexError):
            ok = False
        pruefe(f"Startprogramm: alle Texte auf {s}", ok)
    starter.SPRACHE = "de"
    pruefe("pip-Fehler: kein Internet erkannt",
           starter.pip_grund("WARNING: Retrying ... NewConnectionError('Failed to establish a new connection')") == "internet")
    pruefe("pip-Fehler: voller Datenträger erkannt", starter.pip_grund("OSError: [Errno 28] No space left on device") == "platz")
    pruefe("pip-Fehler: fremdes System-Python erkannt", starter.pip_grund("error: externally-managed-environment") == "fremd")
    pruefe("pip-Ausgabe wird lesbar gekürzt",
           starter.pip_filter("Downloading numpy-2.5.3-cp313-cp313-win_amd64.whl (12.6 MB)") == "↓ numpy 2.5.3  (12.6 MB)"
           and starter.pip_filter("  Downloading numpy-2.5.3-cp313-cp313-win_amd64.whl.metadata (60 kB)") is None
           and starter.pip_filter("Requirement already satisfied: numpy") is None)
    gesperrt = {"fehler": {"PIL": "ImportError: DLL load failed"}, "blockiert": [
        {"modul": "PIL", "datei": "_imaging.cp313-win_amd64.pyd", "code": 4551, "art": "sac"}]}
    pruefe("Sperre durch Smart App Control erkannt (Fehlercode)", starter.sperr_art(gesperrt) == ("sac", "_imaging.cp313-win_amd64.pyd"))
    text_sperre = {"fehler": {"numpy": "ImportError: DLL load failed while importing _multiarray_umath: Eine "
                                       "Anwendungssteuerungsrichtlinie hat diese Datei blockiert."}, "blockiert": []}
    pruefe("Sperre durch Smart App Control erkannt (Meldungstext)", starter.sperr_art(text_sperre)[0] == "sac")
    pruefe("Nur optionales Paket defekt → kein Abbruch",
           starter.nur_wahl_fehlt({"fehler": {"pypdfium2": "OSError"}}) and not starter.nur_wahl_fehlt(gesperrt))
    alt_win, alt_hier, alt_temp = starter.WIN, starter.HIER, os.environ.get("TEMP")
    try:
        starter.WIN, starter.HIER = True, Path("C:/Users/lukas/AppData/Local/Temp/Temp1_Me-Goos-ta-Deutsch.zip/x/Programm")
        try:
            starter.pruefe_ort(None)
            erkannt = False
        except starter.Abbruch as e:
            erkannt = "ZIP" in str(e)
        pruefe("Start direkt aus der ZIP-Datei wird erkannt", erkannt)
    finally:
        starter.WIN, starter.HIER = alt_win, alt_hier
        if alt_temp is not None:
            os.environ["TEMP"] = alt_temp
    r = subprocess.run([sys.executable, str(HIER / "starter.py"), "--importtest"], capture_output=True, text=True,
                       encoding="utf-8", timeout=180)
    try:
        erg = json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        erg = {"fehler": {"?": r.stderr[-300:]}}
    pruefe("Paketprüfung des Startprogramms (lädt Pillow, NumPy, ReportLab wirklich)",
           not {k: v for k, v in erg.get("fehler", {}).items() if k != "pypdfium2"}, str(erg.get("fehler")))

    # --- Zusammenspiel mit der Oberfläche: Instanz-Datei, Wiederfinden, Beenden ---
    with tempfile.TemporaryDirectory() as tmp:
        datei = Path(tmp) / "laeuft-test.json"
        port = _freier_port()
        proc = subprocess.Popen([sys.executable, str(HIER / "gans_ui.py"), "--kein-browser", "--port", str(port),
                                 "--instanz-datei", str(datei)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                env=dict(os.environ, MGD_START_ID="test123"))
        try:
            ende = time.time() + 60
            while time.time() < ende and not datei.exists():
                time.sleep(0.2)
            d = starter.lies_json(datei) or {}
            pruefe("Oberfläche schreibt ihre Instanz-Datei", d.get("start_id") == "test123" and d.get("port") == port
                   and d.get("version") == starter.ui_version(), str(d)[:120])
            if os.name != "nt" and datei.exists():
                pruefe("Instanz-Datei nur für den eigenen Benutzer lesbar", (datei.stat().st_mode & 0o077) == 0)
            pruefe("Startprogramm erkennt die laufende Oberfläche", starter.antwortet(d))
            pruefe("Startprogramm beendet die Oberfläche höflich", starter.beende_instanz(d, warten=10))
            proc.wait(timeout=15)
            pruefe("Instanz-Datei ist danach weg", not datei.exists())
        finally:
            if proc.poll() is None:
                proc.kill()


# =============================================================================================
# [8] Neu in 1.5
# =============================================================================================
WT_PROBE = """{{Siehe auch|[[Alt]]}}
== alt ({{Sprache|Deutsch}}) ==
=== {{Wortart|Adjektiv|Deutsch}} ===
{{Bedeutungen}}
:[1] betagt
==== {{Übersetzungen}} ====
{{Ü-Tabelle|1|G=von Lebewesen: im fortgeschrittenen [[Alter]]|Ü-Liste=
*{{en}}: {{Ü|en|old}}
*{{es}}: {{Ü|es|viejo}} {{m}}, {{Ü|es|anciano}}; ''veraltet:'' {{Ü|es|añoso}}
}}
{{Ü-Tabelle|2|G=nicht neu|Ü-Liste=
*{{es}}: ''Spanien:'' {{Ü|es|vetusto}}; {{Ü|es|antiguo}}; ''Mexiko:'' {{Ü|es|ruco}}
}}
{{Ü-Tabelle|Ü-links=
*{{fr}}: [1] {{Ü|fr|vieux}}
|Ü-rechts=
*{{es}}: [3] {{Ü|es|tener}} {{Ü|es|años}}
}}
== alt ({{Sprache|Rumänisch}}) ==
{{Ü-Tabelle|1|G=anders|Ü-Liste=
*{{es}}: {{Ü|es|otro}}
}}
"""


def _falscher_dienst(aufrufe, wiktionary=None):
    """Ersetzt das Internet im Test: Wiktionary, MyMemory und DeepL antworten mit festen Daten."""
    from urllib.parse import parse_qs, urlsplit
    seiten = wiktionary if wiktionary is not None else {"alt": WT_PROBE}

    def abruf(url, daten, kopf):
        aufrufe.append((url, daten, kopf))
        q = parse_qs(urlsplit(url).query)
        if "wiktionary" in url:
            antwort = []
            for titel in q["titles"][0].split("|"):
                if titel in seiten:
                    antwort.append({"title": titel, "revisions": [{"slots": {"main": {"content": seiten[titel]}}}]})
                else:
                    antwort.append({"title": titel, "missing": True})
            return {"query": {"pages": antwort}}
        if "mymemory" in url:
            return {"responseStatus": 200, "responseData": {"translatedText": "MUCHA HAMBRE"}, "matches": [
                {"segment": q["q"][0], "translation": "=cmd|' /C calc'!A0", "match": 0.99},
                {"segment": q["q"][0], "translation": "<script>alert(1)</script>hambre", "match": 0.95},
                {"segment": q["q"][0], "translation": "hambre feroz", "match": 0.9}]}
        if "deepl" in url:
            return {"translations": [{"detected_source_language": "DE", "text": "Tengo mucha hambre."}]}
        raise AssertionError(url)
    return abruf


def test_neu_15():
    print("\n[8] Neu in 1.5: Gänse-Bild, Bildverbesserung, Tabelle, Übersetzung, mehrere Karten, Update")
    import uebersetzer as ue
    alt_daten = os.environ.get("MGD_DATEN")
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["MGD_DATEN"] = str(Path(tmp) / "daten")         # nie die echten Einstellungen anfassen
        try:
            # --- Wörterbuch lesen ---
            e = ue.wiktionary_spanisch(WT_PROBE)
            woerter = [x["text"] for x in e]
            pruefe("Übersetzung: Wiktionary-Tabellen werden gelesen (neue und alte Form, Wendungen)",
                   woerter == ["viejo", "anciano", "añoso", "vetusto", "antiguo", "ruco", "tener años"], str(woerter))
            pruefe("Übersetzung: andere Sprachen auf derselben Seite werden ignoriert", "otro" not in woerter)
            geordnet = [x["text"] for x in ue.ordne(e)]
            pruefe("Übersetzung: erste Bedeutung zuerst, Veraltetes und andere Länder nach hinten",
                   geordnet[:2] == ["viejo", "anciano"] and geordnet.index("ruco") < geordnet.index("antiguo")
                   and set(geordnet[-2:]) == {"añoso", "vetusto"}, str(geordnet))
            # --- Eingabe und Antworten bereinigen ---
            pruefe("Übersetzung: nur der Teil nach „Gans“ wird übersetzt",
                   ue.quelltext("Gans aufgeregt") == "aufgeregt" and ue.quelltext("Gans arg Hunger") == "arg Hunger")
            gesperrt = []
            for text in ("Gans lukas@example.com", "Gans https://evil.example", "Gans"):
                try:
                    ue.pruefe_quelle(ue.quelltext(text))
                except ue.UebersetzungsFehler as f:
                    gesperrt.append(f.code)
            pruefe("Übersetzung: E-Mail-/Internetadressen und leere Texte werden nicht gesendet",
                   gesperrt == ["unpassend", "unpassend", "leer"], str(gesperrt))
            boese = ["=HYPERLINK(\"x\")", "<script>alert(1)</script>viejo", "@SUMME(1)", "+1", "viejo | =1+1", "老人",
                     "x" * 80, "&lt;b&gt;viejo"]
            pruefe("Übersetzung: Formeln, HTML, fremde Zeichen und Überlanges werden verworfen",
                   all(ue.kandidaten(b, "alt") == [] for b in boese), str([ue.kandidaten(b, "alt") for b in boese]))
            pruefe("Übersetzung: unsichtbare Steuerzeichen entfernt, „/“ trennt Vorschläge, klein geschrieben",
                   ue.kandidaten("Vie" + chr(0x202e) + "jo / Anciano.", "alt") == ["viejo", "anciano"], str(ue.kandidaten("Vie" + chr(0x202e) + "jo / Anciano.", "alt")))
            abgelehnt = []
            for url in ("http://de.wiktionary.org/w/api.php", "https://evil.example/x", "https://de.wiktionary.org:8443/",
                        "https://nutzer:pw@api.mymemory.translated.net/get", "file:///etc/passwd"):
                try:
                    ue.pruefe_adresse(url)
                except ue.UebersetzungsFehler:
                    abgelehnt.append(url)
            pruefe("Übersetzung: nur HTTPS zu den fest eingetragenen Diensten", len(abgelehnt) == 5, str(abgelehnt))
            try:
                ue._KeineWeiterleitung().redirect_request(None, None, 302, "", {}, "https://evil.example/")
                umgeleitet = True
            except ue.UebersetzungsFehler:
                umgeleitet = False
            pruefe("Übersetzung: Weiterleitungen werden nicht befolgt", not umgeleitet)
            # --- Vorschläge (ohne Internet: gefälschter Dienst) ---
            aufrufe = []
            abruf = _falscher_dienst(aufrufe)
            try:
                ue.uebersetze("Gans alt", abruf=abruf, einstellungen=dict(zugestimmt=False, dienst="auto", deepl=None))
                ohne = "gesendet"
            except ue.UebersetzungsFehler as f:
                ohne = f.code
            pruefe("Übersetzung: ohne Zustimmung wird nichts gesendet", ohne == "zustimmung" and not aufrufe, ohne)
            ein = dict(zugestimmt=True, dienst="auto", deepl=None)
            r = ue.uebersetze("Gans alt", abruf=abruf, einstellungen=ein)
            pruefe("Übersetzung: Einzelwort aus dem Wörterbuch mit Alternative",
                   r["dienst"] == "wiktionary" and r["vorschlag"] == "viejo / anciano" and "titles=alt" in aufrufe[-1][0],
                   str(r)[:200])
            n = len(aufrufe)
            r2 = ue.uebersetze("Gans alt", abruf=abruf, einstellungen=ein)
            pruefe("Übersetzung: Ergebnis wird gemerkt (kein zweites Senden)", r2["aus_cache"] and len(aufrufe) == n)
            r = ue.uebersetze("Gans arg Hunger", abruf=abruf, einstellungen=ein)
            pruefe("Übersetzung: Wendung über MyMemory, schädliche Antworten gefiltert",
                   r["dienst"] == "mymemory" and r["vorschlag"] == "mucha hambre"
                   and [a["text"] for a in r["alternativen"]] == ["mucha hambre", "hambre feroz"], str(r)[:200])
            schluessel = "12345678-1234-1234-1234-123456789abc:fx"
            r = ue.uebersetze("Gans sehr Hunger haben", abruf=abruf, einstellungen=dict(ein, deepl=schluessel), cache=False)
            url, daten, kopf = aufrufe[-1]
            pruefe("Übersetzung: DeepL nur mit eigenem Schlüssel, im Kopf statt in der Adresse",
                   r["dienst"] == "deepl" and url == "https://api-free.deepl.com/v2/translate" and schluessel not in url
                   and kopf["Authorization"] == f"DeepL-Auth-Key {schluessel}" and b"ES-419" in daten, url)
            leer_abruf = _falscher_dienst([], wiktionary={})
            r = ue.uebersetze("Gans blau", abruf=leer_abruf, einstellungen=ein, cache=False)
            pruefe("Übersetzung: nicht im Wörterbuch → maschinelle Übersetzung", r["dienst"] == "mymemory", str(r)[:120])
            # --- Einstellungen und Schlüssel ---
            try:
                ue.speichere_einstellungen({"deepl": "kein-schluessel\nX-Evil: 1"})
                format_ok = False
            except ue.UebersetzungsFehler:
                format_ok = True
            ue.speichere_einstellungen({"zugestimmt": True, "deepl": schluessel, "dienst": "deepl"})
            oeff = json.dumps(ue.oeffentliche_einstellungen())
            pruefe("Übersetzung: Schlüssel wird geprüft und nie an die Seite gegeben",
                   format_ok and schluessel not in oeff and "123456789abc" not in oeff.replace("…789abc:fx", "")
                   and ue.lade_einstellungen()["deepl"] == schluessel, oeff[:120])
            pfad = ue.einstellungen_pfad()
            pruefe("Übersetzung: Einstellungen im Benutzerordner, nicht im Projekt",
                   pfad.is_file() and HIER not in pfad.parents and (os.name == "nt" or (pfad.stat().st_mode & 0o077) == 0),
                   str(pfad))
        finally:
            if alt_daten is None:
                os.environ.pop("MGD_DATEN", None)
            else:
                os.environ["MGD_DATEN"] = alt_daten

    # --- Generator: nur Bilder verbessern, Bildauswahl, Übersetzungsstatus, Beispielkarten ---
    gl.registriere_schriften()
    pruefe("Formel in der Notiz wird blockiert (Schutz für Excel)",
           not gl.pruefe_karte("Gans alt", "viejo", gl.Konfig(), notiz="=HYPERLINK(\"x\")")["ok"])
    pruefe("Spalte „uebersetzung“ versteht auch Excel-Schreibweisen",
           [gl.uebersetzung_status(x) for x in ("automatisch", "geprüft", "ja", "x", "", "egal")] ==
           ["auto", "geprueft", "geprueft", "geprueft", "", ""])
    with tempfile.TemporaryDirectory() as tmp:
        p = kopiere_projekt(Path(tmp))
        code, log, _ = lauf(p, "--nur", "verbessern", "--bild", "gans-alt.jpg")
        metas = [json.loads(j.read_text(encoding="utf-8")) for j in (p / "ausgabe" / ".cache").glob("*.json")]
        pruefe("--nur verbessern --bild: genau dieses Bild, ohne Druckdateien",
               code == 0 and len(metas) == 1 and metas[0].get("bild") == "gans-alt.jpg" and len(metas[0].get("sha1", "")) == 40
               and not list((p / "ausgabe").glob("*.pdf")), log[-300:])
        code, log, _ = lauf(p, "--bild", "../karten.csv")
        pruefe("--bild nimmt nur einfache Bild-Dateinamen", code != 0)
        code, log, _ = lauf(p, "--nur", "pruefbogen", "--bild", "gans-alt.jpg", "--bild", "gans-anders.jpg")
        bericht = json.loads((p / "ausgabe" / "bericht.json").read_text(encoding="utf-8"))
        pruefe("--bild wählt Karten auch für Druckdateien aus", code == 0 and bericht["auswahl"] == [4, 5], str(bericht.get("auswahl")))
        spalten, zeilen, _ = gl.lies_csv(p / "karten.csv")
        zeilen[0]["uebersetzung"] = "automatisch"
        gl.schreibe_csv(p / "karten.csv", zeilen, spalten)
        karten, _ = gl.lies_karten(p / "karten.csv", p / "bilder")
        kopf = (p / "karten.csv").read_text(encoding="utf-8-sig").splitlines()[0]
        pruefe("Übersetzungsstatus wird gespeichert und gelesen", kopf == "bild;de;es;notiz;uebersetzung"
               and karten[0]["uebersetzung"] == "auto", kopf)
        (p / "karten.csv").unlink()
        shutil.rmtree(p / "bilder")
        spalten, zeilen, _ = gl.lies_csv(p / "karten.csv")
        pruefe("Fehlende karten.csv wird aus den Beispielkarten angelegt (Entpacken überschreibt nie die eigene Liste)",
               (p / "karten.csv").exists() and len(zeilen) == 10)
        pruefe("Frisch entpackt: die Beispielbilder kommen aus beispiel-bilder/ nach bilder/",
               sorted(q.name for q in (p / "bilder").iterdir()) == sorted(q.name for q in (p / "beispiel-bilder").iterdir())
               and len(list((p / "bilder").iterdir())) == 10)
        (p / "karten.csv").unlink()
        (p / "bilder" / "gans-alt.jpg").write_bytes(b"eigenes Bild")
        (p / "bilder" / "gans-adelig.jpg").unlink()
        gl.lies_csv(p / "karten.csv")
        pruefe("Ein vorhandenes Bild wird nie durch ein Beispielbild ersetzt",
               (p / "bilder" / "gans-alt.jpg").read_bytes() == b"eigenes Bild" and (p / "bilder" / "gans-adelig.jpg").is_file())

    # --- Oberfläche: neue Bereiche ---
    import gans_ui
    felder = gans_ui.alle_felder()
    gruppen = {g["titel"]: g for g in gans_ui.schema()}
    pruefe("Gänse-Bild als Knopf (eigenes Bedienelement), Bildauswahl nur intern",
           felder["gans_bild"]["art"] == "gansbild" and felder["bild"]["intern"])
    pruefe("Bildverbesserung hat einen eigenen Reiter", any(g["reiter"] == "bildverbesserung" and
                                                           {f["dest"] for f in g["felder"]} >= {"qualitaet", "ki"}
                                                           for g in gruppen.values()))
    with tempfile.TemporaryDirectory() as tmp:
        p = kopiere_projekt(Path(tmp) / "projekt")
        port = _freier_port()
        proc = subprocess.Popen([sys.executable, str(p / "gans_ui.py"), "--kein-browser", "--port", str(port)], cwd=p,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                env=dict(os.environ, PYTHONIOENCODING="utf-8", MGD_DATEN=str(Path(tmp) / "daten")))
        try:
            adresse = None
            for _ in range(100):
                m = re.search(r"http://127\.0\.0\.1:\d+/\?k=[A-Za-z0-9_-]+", proc.stdout.readline().decode("utf-8", "replace"))
                if m:
                    adresse = m.group(0)
                    break
            se = Sitzung(port)
            for _ in range(50):
                try:
                    code, kopf, _ = se.anfrage(adresse.split(str(port), 1)[1])
                    break
                except OSError:
                    time.sleep(0.2)
            se.cookie = kopf.get("set-cookie", "").split(";")[0]
            se.token = re.search(rb'const TOKEN = "([^"]+)"', se.anfrage("/")[2]).group(1).decode()
            # Gänse-Bild
            puffer = io.BytesIO()
            gross = Image.new("RGB", (3000, 2100), (230, 200, 120))
            exif = gross.getexif()
            exif[0x010E] = "geheime Beschreibung"
            gross.save(puffer, "JPEG", exif=exif.tobytes())
            code, r = se.json("/api/gans-bild", roh=puffer.getvalue())
            ziel = p / "assets" / "gans_hintergrund.jpg"
            with Image.open(ziel) as im:
                ohne_meta = max(im.size) <= 2400 and not im.getexif()
            pruefe("Gänse-Bild per Knopf: geprüft, verkleinert, ohne Metadaten gespeichert",
                   code == 200 and r["quelle"] == "geladen" and ohne_meta, str(r)[:120])
            code, kopf, bild = se.anfrage("/api/rueckseite?es=hola")
            pruefe("Gänse-Bild: Vorschau der Rückseite", code == 200 and kopf.get("content-type", "").startswith("image/"))
            ergebnisse_g = []
            for roh in (b"kein bild", b"\x00\x00\x00\x18ftypheic" + b"\x00" * 64):
                ergebnisse_g.append(se.json("/api/gans-bild", roh=roh)[0])
            klein = io.BytesIO()
            Image.new("RGB", (200, 150)).save(klein, "PNG")
            ergebnisse_g.append(se.json("/api/gans-bild", roh=klein.getvalue())[0])
            pruefe("Gänse-Bild: kaputte, HEIC- und zu kleine Bilder werden abgelehnt", ergebnisse_g == [400, 400, 400],
                   str(ergebnisse_g))
            code, r = se.json("/api/gans-bild-weg", daten={})
            pruefe("Gänse-Bild entfernen → gezeichnete Gans, altes Bild aufgehoben",
                   r.get("quelle") == "gezeichnet" and not ziel.exists() and any((p / "assets" / "_alt").glob("gans_hintergrund-*")))
            code, r = se.json("/api/gans-bild-zurueck", daten={})
            pruefe("Gänse-Bild wiederherstellen", r.get("quelle") == "geladen" and ziel.exists())
            # Bildverbesserung
            code, v = se.json("/api/verbesserung")
            pruefe("Bildverbesserung: Übersicht mit Status je Karte", code == 200 and len(v["karten"]) == 10
                   and {k["status"] for k in v["karten"]} <= {"offen", "anders", "verbessert"})
            code, r = se.json("/api/lauf", daten={"art": "verbessern", "bilder": ["gans-alt.jpg"]})
            st = {}
            for _ in range(600):
                st = se.json("/api/lauf")[1]
                if not st.get("laeuft"):
                    break
                time.sleep(0.2)
            code, v = se.json("/api/verbesserung")
            status = {k["bild"]: k["status"] for k in v["karten"]}
            pruefe("Bildverbesserung: ausgewähltes Bild wird verbessert und markiert",
                   st.get("code") == 0 and status["gans-alt.jpg"] == "verbessert" and status["gans-anders.jpg"] != "verbessert",
                   str(st.get("zeilen", [])[-2:]))
            c1 = se.anfrage("/api/vergleich?bild=gans-alt.jpg&art=vorher")[0]
            c2 = se.anfrage("/api/vergleich?bild=gans-alt.jpg&art=nachher")[0]
            c3 = se.anfrage("/api/vergleich?bild=gans-anders.jpg&art=nachher")[0]
            pruefe("Bildverbesserung: Vorher/Nachher", (c1, c2, c3) == (200, 200, 404), str((c1, c2, c3)))
            pruefe("Bildverbesserung: fremde Pfade abgewiesen",
                   se.json("/api/lauf", daten={"art": "verbessern", "bilder": ["../karten.csv"]})[0] == 400
                   and se.anfrage("/api/vergleich?bild=..%2Fkarten.csv&art=vorher")[0] in (400, 404))
            # Tabelle und Prüfstatus
            code, tb = se.json("/api/tabelle")
            pruefe("Tabelle: Vorder- und Rückseitentext je Karte", code == 200 and len(tb["karten"]) == 10
                   and tb["karten"][3]["de"] == "Gans alt" and tb["karten"][3]["es"] == "viejo")
            se.json("/api/karte-status", daten={"bild": "gans-alt.jpg", "geprueft": True})
            text = (p / "karten.csv").read_text(encoding="utf-8-sig")
            pruefe("Tabelle: „geprüft“ wird in karten.csv vermerkt", "gans-alt.jpg;Gans alt;viejo;Adjektiv;geprüft" in text)
            se.json("/api/karte-speichern", daten={"bild": "gans-alt.jpg", "de": "Gans alt", "es": "anciano",
                                                   "notiz": "Adjektiv", "es_auto": "anciano"})
            text = (p / "karten.csv").read_text(encoding="utf-8-sig")
            pruefe("Übernommener Vorschlag → „automatisch“, das Häkchen verschwindet bei neuem Wort",
                   "gans-alt.jpg;Gans alt;anciano;Adjektiv;automatisch" in text)
            # Übersetzung über die Oberfläche
            code, r = se.json("/api/uebersetzen", daten={"de": "Gans alt"})
            pruefe("Übersetzung über die Oberfläche erst nach Zustimmung", code == 409 and r.get("code") == "zustimmung")
            se.json("/api/uebersetzung", daten={"deepl": "12345678-1234-1234-1234-123456789abc:fx"})
            code, kopf, roh = se.anfrage("/api/uebersetzung")
            pruefe("DeepL-Schlüssel verlässt den Server nicht", code == 200 and b"123456789abc:fx" not in roh.replace(b"\xe2\x80\xa6789abc:fx", b"")
                   and not (p / "uebersetzung.json").exists() and (Path(tmp) / "daten" / "uebersetzung.json").exists())
            # mehrere Karten: Entwurf schon mit Wort übernehmen
            fertig = []
            for i, w in enumerate(("uno", "dos")):
                puffer = io.BytesIO()
                Image.new("RGB", (900, 640), (40 + 100 * i, 90, 160)).save(puffer, "JPEG", quality=90)
                code, d = se.json(f"/api/entwurf?name=gans-test{i}.jpg", roh=puffer.getvalue())
                code, d = se.json("/api/entwurf-pruefen", daten={"id": d["id"], "es": w, "es_auto": w if i == 0 else ""})
                code, r = se.json("/api/entwurf-uebernehmen", daten={"id": d["id"], "de": d["de"], "es": w,
                                                                     "es_auto": w if i == 0 else ""})
                fertig.append(code)
            text = (p / "karten.csv").read_text(encoding="utf-8-sig")
            pruefe("Mehrere Bilder: gleich fertig beschriftet übernehmen (mit Übersetzungsstatus)",
                   fertig == [200, 200] and re.search(r"gans-test0\.jpg;Gans test0;uno;;(cover)?;automatisch", text)
                   and re.search(r"gans-test1\.jpg;Gans test1;dos;;(cover)?;\r?\n", text), text[-160:])
            (p / "assets" / "_alt").mkdir(exist_ok=True)
            (p / "assets" / "_alt" / "gans_hintergrund-20260101-000000.jpg").write_bytes(b"alt")
            code, r = se.json("/api/werkzeug", daten={"id": "zip"})
            namen = zipfile.ZipFile(p / "ausgabe" / "Me-Goos-ta-Deutsch_Projekt.zip").namelist()
            pruefe("Projekt-ZIP mit uebersetzer.py, ohne aufgehobene Gänse-Bilder",
                   "Me-Goos-ta-Deutsch/Programm/uebersetzer.py" in namen and not any("/_alt/" in n for n in namen))
            se.json("/api/beenden", daten={})
            proc.wait(timeout=15)
        finally:
            if proc.poll() is None:
                proc.kill()

    # --- Update: neue Version in neuem Ordner übernimmt die eigenen Karten ---
    import starter
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        alt, neu, daten = t / "alt" / "Programm", t / "neu" / "Programm", t / "daten"
        for o in (alt / "bilder", alt / "ausgabe" / ".cache", alt / "assets", neu / "bilder", neu / "assets", daten):
            o.mkdir(parents=True)
        (alt / "karten.csv").write_text("bild;de;es;notiz\nmeine.jpg;Gans meine;mía;\ngans-alt.jpg;Gans alt;viejo;\n",
                                        encoding="utf-8-sig")
        (neu / "beispiel-karten.csv").write_text("bild;de;es;notiz\ngans-alt.jpg;Gans alt;viejo;\n", encoding="utf-8-sig")
        shutil.copy2(neu / "beispiel-karten.csv", neu / "karten.csv")
        Image.new("RGB", (300, 200), "red").save(alt / "bilder" / "meine.jpg")
        Image.new("RGB", (300, 200), "blue").save(alt / "ausgabe" / ".cache" / "abc.jpg")
        Image.new("RGB", (900, 600), "green").save(alt / "assets" / "gans_hintergrund.jpg")
        (alt / "ui_einstellungen.json").write_text(json.dumps({"sprache": "es", "werte": {"ausgabe": str(alt / "ausgabe")}}),
                                                   encoding="utf-8")
        (daten / "programm-ort.txt").write_text(str(alt), encoding="utf-8")
        vorher = {q: q.read_bytes() for q in alt.rglob("*") if q.is_file()}
        merk = (starter.HIER, starter.DATEN, starter.SPRACHE)
        starter.HIER, starter.DATEN = neu, daten
        try:
            gefunden = starter.vorheriger_ort()
            info = starter.eigene_daten(alt)
            zahl = starter.uebernimm_daten(starter.Ausgabe(konsole=False), alt)
        finally:
            starter.HIER, starter.DATEN, starter.SPRACHE = merk
        einst = json.loads((neu / "ui_einstellungen.json").read_text(encoding="utf-8"))
        pruefe("Update: bisheriger Ordner wird erkannt", gefunden == alt and info and info["karten"] == 2 and info["gans"],
               str(info))
        pruefe("Update: Karten, Bilder, verbesserte Bilder, Gänse-Bild und Sprache übernommen",
               "meine.jpg;Gans meine" in (neu / "karten.csv").read_text(encoding="utf-8-sig")
               and (neu / "bilder" / "meine.jpg").exists() and (neu / "ausgabe" / ".cache" / "abc.jpg").exists()
               and (neu / "assets" / "gans_hintergrund.jpg").exists() and einst["sprache"] == "es" and zahl["karten"] == 2,
               str(zahl))
        pruefe("Update: Pfade in den alten Ordner zeigen danach auf den neuen", einst["werte"]["ausgabe"] == str(neu / "ausgabe"))
        pruefe("Update: Beispielkarten gesichert, alter Ordner unverändert",
               (neu / "_beispiele" / "karten.csv").exists()
               and all(q.read_bytes() == b for q, b in vorher.items()) and len(vorher) == len([q for q in alt.rglob("*") if q.is_file()]))

    # --- Update: frisch entpackt (noch ohne karten.csv und ohne Bilderordner) ---
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        alt, neu, daten = t / "alt" / "Programm", t / "neu" / "Programm", t / "daten"
        for o in (alt / "bilder", neu / "beispiel-bilder", daten):
            o.mkdir(parents=True)
        liste = "bild;de;es;notiz\ngans-alt.jpg;Gans alt;viejo;\n"
        (neu / "beispiel-karten.csv").write_text(liste, encoding="utf-8-sig")
        (alt / "karten.csv").write_text(liste, encoding="utf-8-sig")
        Image.new("RGB", (300, 200), "red").save(neu / "beispiel-bilder" / "gans-alt.jpg")
        shutil.copy2(neu / "beispiel-bilder" / "gans-alt.jpg", alt / "bilder" / "gans-alt.jpg")
        merk = (starter.HIER, starter.DATEN, starter.SPRACHE)
        starter.HIER, starter.DATEN = neu, daten
        try:
            nur_beispiele = starter.eigene_daten(alt)
            Image.new("RGB", (300, 200), "blue").save(alt / "bilder" / "meine.jpg")
            mit_eigenem = starter.eigene_daten(alt)
            zahl = starter.uebernimm_daten(starter.Ausgabe(konsole=False), alt)
        finally:
            starter.HIER, starter.DATEN, starter.SPRACHE = merk
        pruefe("Update: im bisherigen Ordner nur die Beispielkarten → keine Rückfrage", nur_beispiele is None,
               str(nur_beispiele))
        pruefe("Update: frisch entpackt – eigene Bilder werden erkannt und übernommen",
               bool(mit_eigenem) and mit_eigenem["bilder"] == 2 and (neu / "bilder" / "meine.jpg").is_file()
               and (neu / "karten.csv").is_file() and zahl["bilder"] == 2, f"{mit_eigenem} {zahl}")


def main():
    print(f"{gl.PRODUKT} – Selbsttest {gl.VERSION}")
    t = time.time()
    test_bildverbesserung()
    test_layout()
    test_generator()
    test_kartenliste()
    test_schritte()
    test_oberflaeche()
    test_start()
    test_neu_15()
    fehler = [e for e in ergebnisse if not e[1]]
    print(f"\n{len(ergebnisse) - len(fehler)} von {len(ergebnisse)} Prüfungen bestanden ({time.time() - t:.0f} s).")
    if fehler:
        print(f"{len(fehler)} TESTS FEHLGESCHLAGEN:")
        for name, _, detail in fehler:
            print(f"  - {name}  {detail}")
        return 1
    print("ALLE TESTS BESTANDEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
