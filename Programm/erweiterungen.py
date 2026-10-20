#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ME GOOS-TA DEUTSCH – Erweiterungen der Oberfläche                   Version 2.1 (20.10.2026)
=============================================================================================
Zusätzliche Funktionen, die gans_ui.py einbindet (verbinde(gans_ui)). Fehlt diese Datei, läuft die Oberfläche
genau wie bisher – nur ohne diese Funktionen.

  • Karten exportieren / importieren: ZIP mit karten.csv + bilder/ (oder nur eine CSV). Der Import zeigt erst eine
    Vorschau mit Konflikten; Bilder werden wie in Schritt 1 geprüft (Größe, Megapixel, HEIC, lesbar), Texte wie in
    Schritt 2 (keine Excel-Formeln); ersetzte Bilder kommen nach bilder/_entfernt/.
  • Ideen: unfertige Karten (Entwürfe aus Schritt 1, offene Karten aus Schritt 2) und eigene Ideen (Bild, deutsches
    oder spanisches Wort) in ideen.json + ideen/. „Als Karte aufnehmen“ läuft über die Prüfungen von Schritt 1.
  • Programmstart: Browser (Standard oder ein bestimmter) oder eigenes Fenster (App-Fenster von Edge/Chrome) –
    gespeichert in start.json im Datenordner, gelesen vom Startprogramm (starter.py).
  • Deinstallieren: startet starter.py --deinstallieren (beendet die Oberfläche, entfernt Symbole, Datenordner und
    Programmordner).

Sicherheit: dieselben Regeln wie in gans_ui.py – nur einfache Dateinamen, Pfade bleiben in ihren Ordnern, Bilder
mit Größen- und Pixelgrenzen, Texte ohne Formelanfang, Schreiben atomar, nichts wird hart gelöscht (außer beim
ausdrücklich bestätigten Deinstallieren).
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unicodedata
import zipfile
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import gans_lernkarten as gl  # noqa: E402

L = gl.L
UI = None                                    # das Modul gans_ui (wird von verbinde() gesetzt)

MAX_IMPORT = 500 * 1024 * 1024               # Bytes je Import-Datei
MAX_IMPORT_EINTRAEGE = 5000                  # Einträge in einer Import-ZIP
MAX_IMPORT_ENTPACKT = 1500 * 1024 * 1024     # Summe der entpackten Größen (Schutz vor „ZIP-Bomben“)
MAX_CSV = 5 * 1024 * 1024
IDEEN_DATEI = HIER / "ideen.json"
IDEEN_ORDNER = HIER / "ideen"
FORMEL_ANFANG = ("=", "+", "-", "@")
_ideen_lock = threading.Lock()
_import_lock = threading.Lock()

TEXTE = {
    "import_kaputt": L("Mit dieser Datei kann der Import leider nichts anfangen – nimm eine ZIP-Datei aus „Exportieren“ "
                       "oder eine Kartenliste (CSV).",
                       "The import can’t do anything with this file – use a ZIP file from “Export” or a card "
                       "list (CSV).",
                       "La importación no puede hacer nada con este archivo; usa un ZIP de «Exportar» o una lista "
                       "de cartas (CSV)."),
    "import_gross": L("Die Datei ist größer als {mb} MB – teil sie am besten in kleinere Exporte auf.",
                      "The file is larger than {mb} MB – best split it into smaller exports.",
                      "El archivo pesa más de {mb} MB; mejor divídelo en exportaciones más pequeñas."),
    "import_ohne_csv": L("In dieser ZIP-Datei stecken weder Karten (karten.csv) noch Ideen (ideen.json) – war es "
                         "vielleicht eine andere Datei?",
                         "This ZIP file holds neither cards (karten.csv) nor ideas (ideen.json) – was it maybe a "
                         "different file?",
                         "Este ZIP no trae cartas (karten.csv) ni ideas (ideen.json); ¿quizá era otro archivo?"),
    "i_gleiches_wort": L("Gleiches Wort wie Karte {nr} ({bild})", "Same word as card {nr} ({bild})",
                         "Misma palabra que la carta {nr} ({bild})"),
    "i_idee_da": L("Diese Idee gibt es schon (anders)", "This idea already exists (different)",
                   "Esta idea ya existe (distinta)"),
    "i_idee_als_karte": L("Gibt es schon als Karte {nr} ({bild})", "Already exists as card {nr} ({bild})",
                          "Ya existe como carta {nr} ({bild})"),
    "import_bombe": L("Diese ZIP-Datei ist ungewöhnlich aufgebaut (zu viele oder zu große Einträge) – zu deiner "
                      "Sicherheit liest das Programm sie nicht.",
                      "This ZIP file is built unusually (too many or too large entries) – for your safety the "
                      "program doesn’t read it.",
                      "Este ZIP tiene una estructura inusual (demasiadas entradas o demasiado grandes); por tu "
                      "seguridad el programa no lo lee."),
    "import_fehlt": L("Dieser Import ist abgelaufen – wähl die Datei einfach noch einmal.",
                      "This import has expired – just choose the file once more.",
                      "Esta importación caducó; elige el archivo otra vez y listo."),
    "i_name": L("Bildname passt nicht", "Image name doesn’t fit", "El nombre de la imagen no encaja"),
    "i_bild_fehlt": L("Bild fehlt (weder in der Datei noch hier vorhanden)", "Image missing (neither in the file nor here)",
                      "Falta la imagen (ni en el archivo ni aquí)"),
    "i_doppelt": L("Steht doppelt in der Kartenliste", "Listed twice in the card list", "Aparece dos veces en la lista"),
    "i_neu": L("Neue Karte", "New card", "Carta nueva"),
    "i_gleich": L("Schon vorhanden (gleich)", "Already here (identical)", "Ya existe (igual)"),
    "i_anders_text": L("Schon vorhanden, Text anders", "Already here, different text", "Ya existe, texto distinto"),
    "i_anders_bild": L("Schon vorhanden, Bild anders", "Already here, different image", "Ya existe, imagen distinta"),
    "i_nur_text": L("Bild ist schon hier", "Image already here", "La imagen ya está aquí"),
    "idee_leer": L("Für eine Idee reicht schon ein Bild, ein Wort auf Deutsch oder auf {zs} – trag einfach "
                   "eins ein.",
                   "An idea only needs an image, a German or a {zs} word – just add one.",
                   "Para una idea basta una imagen, una palabra en alemán o en {zs}; agrega una y listo."),
    "idee_fehlt": L("Diese Idee gibt es nicht mehr.", "This idea no longer exists.", "Esta idea ya no existe."),
    "idee_unvollstaendig": L("Fast fertig! Für eine Karte braucht die Idee noch ein Bild, den Text auf dem Bild und das "
                             "Wort auf {zs}.",
                             "Almost done! To become a card, the idea still needs an image, the text on the image "
                             "and the {zs} word.",
                             "¡Casi lista! Para ser carta, a la idea le falta una imagen, el texto de la imagen y la "
                             "palabra en {zs}."),
    "start_gespeichert": L("Gespeichert ✓ – gilt ab dem nächsten Start.", "Saved ✓ – applies from the next start.",
                           "Guardado ✓; se aplica desde el próximo inicio."),
    "deinst_bestaetigen": L("Bitte das Deinstallieren ausdrücklich bestätigen.", "Please confirm the uninstall explicitly.",
                            "Confirma expresamente la desinstalación."),
    "deinst_ort": L("Der Programmordner sieht nicht wie ein Me-Goos-ta-Deutsch-Ordner aus – aus Sicherheitsgründen "
                    "wird nichts gelöscht.",
                    "The program folder does not look like a Me Goos-ta Deutsch folder – for safety nothing is deleted.",
                    "La carpeta del programa no parece de Me Goos-ta Deutsch; por seguridad no se borra nada."),
    "deinst_laeuft": L("Me Goos-ta Deutsch wird deinstalliert. Die Oberfläche schließt sich gleich.",
                       "Me Goos-ta Deutsch is being uninstalled. The interface will close in a moment.",
                       "Me Goos-ta Deutsch se está desinstalando. La interfaz se cerrará en un momento."),
}


def tx(code, **werte):
    return gl.mit_zs(gl.text_in(TEXTE[code]), werte)


def verbinde(ui):
    """Wird am Ende von gans_ui.py aufgerufen: merkt sich das Modul und meldet die Werkzeuge an."""
    global UI
    UI = ui
    _werkzeuge_anmelden()


# =============================================================================================
# Hilfen
# =============================================================================================
def _text(wert, laenge=300):
    return " ".join(str(wert or "").split())[:laenge]


def _formel(*texte):
    return any(str(t or "").lstrip().startswith(FORMEL_ANFANG) for t in texte)


def _atomar(pfad, daten: bytes):
    pfad.parent.mkdir(parents=True, exist_ok=True)
    tmp = pfad.with_name(f"{pfad.name}.{os.getpid()}.{secrets.token_hex(3)}.tmp")
    tmp.write_bytes(daten)
    os.replace(tmp, pfad)


def bild_pruefen(daten: bytes):
    """Prüft Bild-Bytes wie Schritt 1: Größe, HEIC, lesbar, Megapixel. Gibt (Format, (w, h)) zurück oder wirft
    ValueError mit verständlichem Text."""
    from PIL import Image
    if len(daten) > gl.MAX_DATEI_MB * 1024 * 1024:
        raise ValueError(gl.pm("b_datei_gross", "fehler", mb=gl.MAX_DATEI_MB)["text"])
    if daten[4:12] in gl.HEIC_MARKEN:
        raise ValueError(gl.pm("b_heic", "fehler")["text"])
    try:
        with Image.open(io.BytesIO(daten)) as im:
            fmt, groesse = im.format, im.size
            if groesse[0] * groesse[1] > gl.MAX_MEGAPIXEL * 1_000_000:
                raise ValueError(gl.pm("b_pixel", "fehler", mp=round(groesse[0] * groesse[1] / 1e6),
                                       max=gl.MAX_MEGAPIXEL)["text"])
            im.verify()
    except ValueError:
        raise
    except Exception:  # noqa: BLE001
        raise ValueError(gl.pm("b_unlesbar", "fehler")["text"]) from None
    return fmt, groesse


def _als_kartenbild(daten: bytes, fmt):
    """JPG/PNG/WEBP bleiben unverändert; andere Formate (GIF, BMP, TIFF …) werden zu PNG."""
    if fmt == "JPEG":
        return daten, ".jpg"
    if fmt in ("PNG", "WEBP"):
        return daten, "." + fmt.lower()
    im = gl.oeffne_bild(io.BytesIO(daten))
    puffer = io.BytesIO()
    im.save(puffer, "PNG")
    return puffer.getvalue(), ".png"


# =============================================================================================
# Gleiche Wörter erkennen („Gans alt“ = „gans-alt“ = „GANS ALT“) – für Import-Warnung und Ideen-Prüfung
# =============================================================================================
def wort_schluessel(text, rueckseite=False):
    """Vergleichsschlüssel eines Worts: klein, ä→ae …, ohne Akzente/Satzzeichen, ohne vorangestelltes „Gans“.
    rueckseite=True: nur das Hauptwort vor „/“ zählt („viejo / anciano“ → „viejo“)."""
    t = str(text or "")
    if rueckseite:
        t = t.split("/")[0].replace("|", " ")
    t = t.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        t = t.replace(a, b)
    t = "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))
    t = re.sub(r"[^a-z0-9ñ]+", " ", t).strip()
    return t if rueckseite else re.sub(r"^gans\s+", "", t)


# =============================================================================================
# Exportieren: Karten, Ideen oder beides (Sicherung) – eine ZIP, die der Import wieder einliest
# =============================================================================================
def export_zip(umfang="alle", inhalt="karten"):
    """ZIP mit karten.csv + bilder/ (inhalt karten|alles) und/oder ideen.json + ideen/ (inhalt ideen|alles).
    umfang: alle | aktiv (nur Karten, die gedruckt werden)."""
    csv_pfad, bilder, _, _ = UI.pfade()
    mit_karten, mit_ideen = inhalt in ("karten", "alles"), inhalt in ("ideen", "alles")
    puffer = io.BytesIO()
    zahl_karten = zahl_ideen = 0
    with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(puffer, "w", zipfile.ZIP_DEFLATED) as z:
        if mit_karten:
            spalten, zeilen, _ = gl.lies_csv(csv_pfad)
            if umfang == "aktiv":
                zeilen = [zl for zl in zeilen if not zl.get("bild", "").startswith("#")]
            ziel_csv = Path(tmp) / "karten.csv"
            gl.schreibe_csv(ziel_csv, zeilen, spalten)
            z.write(ziel_csv, "karten.csv")
            gesehen = set()
            for zeile in zeilen:
                name = zeile.get("bild", "").lstrip("#").strip()
                if name in gesehen or not gl.sicherer_name(name):
                    continue
                gesehen.add(name)
                p = bilder / name
                if p.is_file() and not p.is_symlink():
                    z.write(p, f"bilder/{name}", compress_type=zipfile.ZIP_STORED)
            zahl_karten = len(zeilen)
        if mit_ideen:
            ideen = []
            for i in _ideen_lesen()["ideen"]:
                eintrag = {k: i.get(k, "") for k in ("id", "de", "es", "es_auto", "notiz", "bild")}
                p = _idee_bildpfad(i)
                if p and not p.is_symlink():
                    z.write(p, f"ideen/{p.name}", compress_type=zipfile.ZIP_STORED)
                else:
                    eintrag["bild"] = ""
                ideen.append(eintrag)
            z.writestr("ideen.json", json.dumps({"ideen": ideen}, ensure_ascii=False, indent=1))
            zahl_ideen = len(ideen)
        lernstand = csv_pfad.parent / "lernstand.json"
        if inhalt == "alles" and lernstand.is_file() and not lernstand.is_symlink():   # Komplettsicherung: Lernstand mit
            z.write(lernstand, "lernstand.json")       # (zurück über „Lernstand importieren“ im Lernen-Bereich)
        z.writestr("LIES_MICH.txt", "Me Goos-ta Deutsch – export / Export / exportación\r\n"
                   "Import: Me Goos-ta Deutsch → My cards / Ideas → ⇅ Import / Export\r\n"
                   f"{time.strftime('%Y-%m-%d %H:%M')} · {zahl_karten} cards · {zahl_ideen} ideas\r\n")
    art = {"karten": "Karten", "ideen": "Ideen", "alles": "Sicherung"}.get(inhalt, "Karten")
    return puffer.getvalue(), f"{gl.DATEI_PRAEFIX}_{art}_{time.strftime('%Y-%m-%d')}.zip"


# =============================================================================================
# Importieren – erst prüfen (Vorschau mit Warnungen bei Vorhandenem), dann übernehmen
# =============================================================================================
def _import_ordner():
    _, _, ausgabe, _ = UI.pfade()
    d = ausgabe / ".import"
    d.mkdir(parents=True, exist_ok=True)
    for p in d.glob("*"):                                       # alte Importe aufräumen (älter als 1 Tag)
        try:
            if time.time() - p.stat().st_mtime > 86400:
                p.unlink()
        except OSError:
            pass
    return d


def _import_pfad(iid):
    if not re.fullmatch(r"[0-9a-f]{16}", str(iid or "")):
        raise UI.Meldung("ungueltig")
    p = _import_ordner() / f"{iid}.import"
    if not p.is_file():
        raise ValueError(tx("import_fehlt"))
    return p


def import_speichern(lese, laenge):
    """Liest den Anfragekörper in Stücken in eine Datei (ausgabe/.import/<id>.import) und prüft sie."""
    if laenge <= 0 or laenge > MAX_IMPORT:
        raise ValueError(tx("import_gross", mb=MAX_IMPORT // (1024 * 1024)))
    iid = secrets.token_hex(8)
    ziel = _import_ordner() / f"{iid}.import"
    rest = laenge
    with open(ziel, "wb") as f:
        while rest > 0:
            stueck = lese(min(rest, 1024 * 1024))
            if not stueck:
                break
            f.write(stueck)
            rest -= len(stueck)
    try:
        return dict(id=iid, **_import_vorschau(_import_lesen(ziel), ziel))
    except Exception:
        ziel.unlink(missing_ok=True)
        raise


def _medien(infos, basis, ordner):
    """{einfacher Bildname: (Name in der ZIP, Größe)} für <basis><ordner>/<name>."""
    aus = {}
    for i in infos:
        if i.is_dir() or not i.filename.startswith(basis + ordner + "/"):
            continue
        name = i.filename[len(basis + ordner + "/"):]
        if gl.sicherer_name(name) and "/" not in name and Path(name).suffix.lower() in gl.BILD_ENDUNGEN:
            aus[name] = (i.filename, i.file_size)
    return aus


def _ideen_aus_json(roh):
    """Ideen aus einer importierten ideen.json – nur erwartete Felder, nur Texte."""
    try:
        d = json.loads(roh.decode("utf-8-sig"))
    except (UnicodeDecodeError, ValueError):
        raise ValueError(tx("import_kaputt")) from None
    liste = d.get("ideen") if isinstance(d, dict) else None
    if not isinstance(liste, list):
        raise ValueError(tx("import_kaputt"))
    aus = []
    for e in liste[:MAX_IMPORT_EINTRAEGE]:
        if isinstance(e, dict):
            aus.append({k: e.get(k) if isinstance(e.get(k), str) else "" for k in ("id", "de", "es", "es_auto", "notiz", "bild")})
    return aus


def _import_lesen(pfad):
    """→ dict(zeilen, spalten, bilder, ideen, ideen_bilder, zip). Karten und/oder Ideen."""
    zeilen, spalten, ideen, bilder, ideen_bilder, csv_bytes = [], [], [], {}, {}, None
    if zipfile.is_zipfile(pfad):
        with zipfile.ZipFile(pfad) as z:
            infos = z.infolist()
            if len(infos) > MAX_IMPORT_EINTRAEGE or sum(i.file_size for i in infos) > MAX_IMPORT_ENTPACKT:
                raise ValueError(tx("import_bombe"))
            nutzbar = [i for i in infos if not i.is_dir() and i.filename.count("/") <= 2 and "__MACOSX" not in i.filename]
            csvs = sorted((i for i in nutzbar if i.filename.lower().endswith(".csv")),
                          key=lambda i: (i.filename.lower().rsplit("/", 1)[-1] != "karten.csv", i.filename.count("/")))
            jsons = sorted((i for i in nutzbar if i.filename.lower().rsplit("/", 1)[-1] == "ideen.json"),
                           key=lambda i: i.filename.count("/"))
            if not csvs and not jsons:
                raise ValueError(tx("import_ohne_csv"))
            for info in csvs[:1] + jsons[:1]:
                if info.file_size > MAX_CSV:
                    raise ValueError(tx("import_bombe"))
            if csvs:
                info = csvs[0]
                basis = info.filename.rsplit("/", 1)[0] + "/" if "/" in info.filename else ""
                bilder, csv_bytes = _medien(infos, basis, "bilder"), z.read(info)
            if jsons:
                info = jsons[0]
                basis = info.filename.rsplit("/", 1)[0] + "/" if "/" in info.filename else ""
                ideen_bilder, ideen = _medien(infos, basis, "ideen"), _ideen_aus_json(z.read(info))
        ist_zip = True
    else:
        if pfad.stat().st_size > MAX_CSV:
            raise ValueError(tx("import_kaputt"))
        roh, ist_zip = pfad.read_bytes(), False
        if b"\x00" in roh[:4096]:
            raise ValueError(tx("import_kaputt"))
        if roh.lstrip()[:1] in (b"{", b"\xef"):                  # ideen.json allein (ohne Bilder)
            try:
                ideen = _ideen_aus_json(roh)
            except ValueError:
                csv_bytes = roh
        else:
            csv_bytes = roh
    if csv_bytes is not None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "karten.csv"
            p.write_bytes(csv_bytes)
            spalten, zeilen, _ = gl.lies_csv(p)
        if "bild" not in spalten:
            raise ValueError(tx("import_kaputt"))
    return dict(zeilen=zeilen, spalten=spalten, bilder=bilder, ideen=ideen, ideen_bilder=ideen_bilder, zip=ist_zip)


def _sha1_datei(p):
    try:
        return gl.datei_hash(p).hexdigest()
    except OSError:
        return None


def _import_bewerten(erg, pfad=None):
    """Bewertet jede Karte gegen das Projekt: neu | gleich | konflikt | fehler (+ text). Konflikte entstehen bei
    gleichem Bildnamen und – neu – bei gleichem Wort unter anderem Namen („doppelt“)."""
    _, bilder, _, _ = UI.pfade()
    hier_karten = UI.karten_daten()["karten"]
    hier = {k["bild"]: k for k in hier_karten}
    nach_wort = {}
    for k in hier_karten:
        if wort_schluessel(k["de"]):
            nach_wort.setdefault(wort_schluessel(k["de"]), k)
    gesehen, aus = set(), []
    z = zipfile.ZipFile(pfad) if erg["zip"] and pfad and erg["bilder"] else None
    try:
        for zeile in erg["zeilen"]:
            roh = zeile.get("bild", "")
            name = roh.lstrip("#").strip()
            e = dict(art="karte", schluessel="k:" + name, bild=name, aktiv=not roh.startswith("#"),
                     de=_text(zeile.get("de"), 120), es=_text(zeile.get("es")), notiz=_text(zeile.get("notiz")),
                     fit=zeile.get("fit", "") or "contain", uebersetzung=gl.uebersetzung_status(zeile.get("uebersetzung")),
                     extra={k: _text(v) for k, v in zeile.items() if k not in gl.KARTEN_SPALTEN
                            and re.fullmatch(r"[a-z0-9_ -]{1,40}", str(k))},
                     status="neu", text=tx("i_neu"), bild_neu=False, statt=None)
            if not name or not gl.sicherer_name(name) or Path(name).suffix.lower() not in gl.BILD_ENDUNGEN:
                e.update(status="fehler", text=tx("i_name"))
            elif name in gesehen:
                e.update(status="fehler", text=tx("i_doppelt"))
            elif _formel(e["de"], e["es"], e["notiz"]):
                e.update(status="fehler", text=gl.pm("k_formel", "fehler")["text"])
            gesehen.add(name)
            if e["status"] == "fehler":
                aus.append(e)
                continue
            lokal = bilder / name
            if name in erg["bilder"]:
                zname, groesse = erg["bilder"][name]
                if groesse > gl.MAX_DATEI_MB * 1024 * 1024:
                    e.update(status="fehler", text=gl.pm("b_datei_gross", "fehler", mb=gl.MAX_DATEI_MB)["text"])
                    aus.append(e)
                    continue
                if z is not None:
                    daten = z.read(zname)
                    try:
                        bild_pruefen(daten)
                    except ValueError as f:
                        e.update(status="fehler", text=str(f))
                        aus.append(e)
                        continue
                    e["bild_neu"] = not (lokal.is_file() and _sha1_datei(lokal) == hashlib.sha1(daten).hexdigest())
            elif not lokal.is_file():
                e.update(status="fehler", text=tx("i_bild_fehlt"))
                aus.append(e)
                continue
            k = hier.get(name)
            gleiches_wort = nach_wort.get(wort_schluessel(e["de"])) if wort_schluessel(e["de"]) else None
            if k:
                gleich_text = (k["de"], k["es"], k["notiz"], k["aktiv"]) == (e["de"], e["es"], e["notiz"], e["aktiv"])
                if gleich_text and not e["bild_neu"]:
                    e.update(status="gleich", text=tx("i_gleich"))
                else:
                    e.update(status="konflikt", text=tx("i_anders_bild") if e["bild_neu"] else tx("i_anders_text"),
                             hier=dict(de=k["de"], es=k["es"], notiz=k["notiz"], nr=k.get("nr"), bild=k["bild"]))
            elif gleiches_wort is not None:
                e.update(status="konflikt", text=tx("i_gleiches_wort", nr=gleiches_wort.get("nr") or "–",
                                                    bild=gleiches_wort["bild"]),
                         statt=gleiches_wort["bild"], hier=dict(de=gleiches_wort["de"], es=gleiches_wort["es"],
                                                               notiz=gleiches_wort["notiz"], nr=gleiches_wort.get("nr"),
                                                               bild=gleiches_wort["bild"]))
            elif lokal.is_file() and e["bild_neu"]:
                e.update(status="konflikt", text=tx("i_anders_bild"))
            elif lokal.is_file():
                e.update(text=tx("i_nur_text"))
            aus.append(e)
    finally:
        if z is not None:
            z.close()
    return aus


def _ideen_bewerten(erg, pfad=None):
    """Bewertet jede importierte Idee: neu | gleich | konflikt (gleiche Idee oder gleiches Wort als Idee/Karte) |
    fehler. Ersetzen überschreibt die vorhandene Idee; gibt es das Wort nur als Karte, kommt die Idee zusätzlich."""
    vorhanden = _ideen_lesen()["ideen"]
    nach_id = {i.get("id"): i for i in vorhanden}
    worte = {}
    for i in vorhanden:
        for s in (wort_schluessel(i.get("de")), wort_schluessel(i.get("es"), True)):
            if s:
                worte.setdefault(s, i)
    karten_worte = {}
    for k in UI.karten_daten()["karten"]:
        for s in (wort_schluessel(k["de"]), wort_schluessel(k["es"], True)):
            if s:
                karten_worte.setdefault(s, k)
    z = zipfile.ZipFile(pfad) if erg["zip"] and pfad and erg["ideen_bilder"] else None
    aus = []
    try:
        for n, roh in enumerate(erg["ideen"]):
            e = dict(art="idee", schluessel=f"i:{n}", id=roh["id"] if re.fullmatch(r"[0-9a-f]{12}", roh["id"] or "") else "",
                     de=_text(roh["de"], 120), es=_text(roh["es"]), notiz=_text(roh["notiz"]),
                     es_auto=_text(roh["es_auto"]), bild="", status="neu", text=tx("i_neu"), ziel=None, bild_neu=False)
            name = roh["bild"] if gl.sicherer_name(roh["bild"] or "") else ""
            if name and name in erg["ideen_bilder"] and z is not None:
                zname, groesse = erg["ideen_bilder"][name]
                try:
                    if groesse > gl.MAX_DATEI_MB * 1024 * 1024:
                        raise ValueError(gl.pm("b_datei_gross", "fehler", mb=gl.MAX_DATEI_MB)["text"])
                    bild_pruefen(z.read(zname))
                    e["bild"] = name
                except ValueError as f:
                    e.update(status="fehler", text=str(f))
            if e["status"] != "fehler" and _formel(e["de"], e["es"], e["notiz"]):
                e.update(status="fehler", text=gl.pm("k_formel", "fehler")["text"])
            if e["status"] != "fehler" and not (e["de"] or e["es"] or e["bild"]):
                e.update(status="fehler", text=tx("idee_leer"))
            if e["status"] == "fehler":
                aus.append(e)
                continue
            gleich = nach_id.get(e["id"]) if e["id"] else None
            if gleich is None:
                for s in (wort_schluessel(e["de"]), wort_schluessel(e["es"], True)):
                    if s and s in worte:
                        gleich = worte[s]
                        break
            if gleich is not None:
                identisch = (gleich.get("de", ""), gleich.get("es", ""), gleich.get("notiz", "")) == (e["de"], e["es"], e["notiz"]) \
                    and bool(gleich.get("bild")) == bool(e["bild"])
                e.update(ziel=gleich["id"], hier=dict(de=gleich.get("de", ""), es=gleich.get("es", "")))
                if identisch:
                    e.update(status="gleich", text=tx("i_gleich"))
                else:
                    e.update(status="konflikt", text=tx("i_idee_da"))
            else:
                karte = next((karten_worte[s] for s in (wort_schluessel(e["de"]), wort_schluessel(e["es"], True))
                              if s and s in karten_worte), None)
                if karte is not None:
                    e.update(status="konflikt", text=tx("i_idee_als_karte", nr=karte.get("nr") or "–", bild=karte["bild"]),
                             hier=dict(de=karte["de"], es=karte["es"], bild=karte["bild"]))
            aus.append(e)
    finally:
        if z is not None:
            z.close()
    return aus


def _import_vorschau(erg, pfad=None):
    karten, ideen = _import_bewerten(erg, pfad), _ideen_bewerten(erg, pfad)
    zaehle = lambda liste: {s: sum(1 for k in liste if k["status"] == s) for s in ("neu", "konflikt", "gleich", "fehler")}  # noqa: E731
    gesamt = zaehle(karten + ideen)
    return dict(karten=[{k: v for k, v in e.items() if k != "extra"} for e in karten], ideen=ideen,
                zahlen=gesamt, zahlen_karten=zaehle(karten), zahlen_ideen=zaehle(ideen), zip=erg["zip"])


def import_pruefen(iid):
    p = _import_pfad(iid)
    return dict(id=iid, **_import_vorschau(_import_lesen(p), p))


def _entscheidung(daten):
    """ersetzen: True/False für alle oder {schluessel: True/False} je Eintrag (+ „standard“)."""
    e = daten.get("ersetzen")
    if isinstance(e, dict):
        standard = e.get("standard") is True
        return lambda s: e.get(s, standard) is True
    return lambda s: e is True


def import_uebernehmen(daten):
    """Übernimmt neue Einträge; vorhandene (Konflikte) nur dort, wo „ersetzen“ gewählt ist. Ersetzte Bilder kommen
    nach bilder/_entfernt/ bzw. ideen/_entfernt/ – nichts wird hart gelöscht."""
    p = _import_pfad(daten.get("id"))
    ersetzen = _entscheidung(daten)
    with _import_lock:
        erg = _import_lesen(p)
        karten, ideen = _import_bewerten(erg, p), _ideen_bewerten(erg, p)
        zahl = dict(neu=0, ersetzt=0, uebersprungen=0, fehler=0, ideen_neu=0, ideen_ersetzt=0)
        csv_pfad, bilder, _, _ = UI.pfade()
        nehmen, weg_zeilen = [], set()
        with zipfile.ZipFile(p) if erg["zip"] else _Leer() as z:
            for e in karten:
                if e["status"] == "fehler":
                    zahl["fehler"] += 1
                    continue
                if e["status"] == "gleich" or (e["status"] == "konflikt" and not ersetzen(e["schluessel"])):
                    zahl["uebersprungen"] += 1
                    continue
                bilder.mkdir(parents=True, exist_ok=True)
                if e.get("statt") and e["statt"] != e["bild"]:          # gleiches Wort unter anderem Namen ersetzen
                    if (bilder / e["statt"]).is_file():
                        UI.bild_weg(e["statt"])
                    weg_zeilen.add(e["statt"])
                if e["bild_neu"] and z is not None and e["bild"] in erg["bilder"]:
                    ziel = UI.sicher_in(bilder, e["bild"])
                    if ziel.is_file():
                        UI.bild_weg(e["bild"])                    # alte Fassung aufheben, nicht löschen
                    _atomar(ziel, z.read(erg["bilder"][e["bild"]][0]))
                zahl["ersetzt" if e["status"] == "konflikt" else "neu"] += 1
                nehmen.append(e)
            for e in ideen:
                if e["status"] == "fehler":
                    zahl["fehler"] += 1
                    continue
                if e["status"] == "gleich" or (e["status"] == "konflikt" and not ersetzen(e["schluessel"])):
                    zahl["uebersprungen"] += 1
                    continue
                bild = z.read(erg["ideen_bilder"][e["bild"]][0]) if (e["bild"] and z is not None) else None
                _idee_importieren(e, bild)
                zahl["ideen_ersetzt" if e["status"] == "konflikt" and e.get("ziel") else "ideen_neu"] += 1
            stand = _lernstand_aus(z) if z is not None and UI.lernen and UI.tool_da("lernen") else None
        if stand is not None:                     # Komplettsicherung vom Rechner: Lernstand dazu (je Karte gilt der neuere)
            try:
                zahl["lernstand"] = UI._lernstand().importieren(stand).get("karten", 0)
            except (UI.lernen.LernFehler, ValueError, OSError):
                pass
        if nehmen or weg_zeilen:
            with UI._csv_lock:
                spalten, zeilen, _ = gl.lies_csv(csv_pfad)
                nach_name = {e["bild"]: e for e in nehmen}
                neu = []
                for zl in zeilen:
                    name = zl.get("bild", "").lstrip("#").strip()
                    if name in nach_name:
                        neu.append(UI._zeile_aus(nach_name.pop(name), zs="es"))     # Import: Spalten roh
                    elif name not in weg_zeilen:
                        neu.append(zl)
                neu += [UI._zeile_aus(e, zs="es") for e in nehmen if e["bild"] in nach_name]
                extra_spalten = [s for s in erg["spalten"] if s not in spalten and re.fullmatch(r"[a-z0-9_ -]{1,40}", s)]
                gl.schreibe_csv(csv_pfad, neu, spalten + extra_spalten)
        UI._vorschau_cache.clear()
    p.unlink(missing_ok=True)
    return dict(zahlen=zahl, karten=UI.karten_daten(), **ideen_liste())


def _lernstand_aus(z):
    """lernstand.json aus einer Komplettsicherung (neben karten.csv, höchstens zwei Ordner tief) → dict oder None."""
    infos = sorted((i for i in z.infolist() if not i.is_dir() and i.filename.rsplit("/", 1)[-1] == "lernstand.json"
                    and i.filename.count("/") <= 2 and "__MACOSX" not in i.filename), key=lambda i: i.filename.count("/"))
    if not infos or infos[0].file_size > MAX_CSV * 4:
        return None
    try:
        d = json.loads(z.read(infos[0]).decode("utf-8"))
    except (ValueError, UnicodeDecodeError, zipfile.BadZipFile):
        return None
    return d if isinstance(d, dict) else None


def _idee_importieren(e, bild_bytes):
    """Legt eine importierte Idee an oder überschreibt die vorhandene (e["ziel"]); ein neues Bild wird wie beim
    Hochladen geprüft und gespeichert, das alte kommt nach ideen/_entfernt/."""
    with _ideen_lock:
        d = _ideen_lesen()
        i = next((x for x in d["ideen"] if x.get("id") == e.get("ziel")), None) if e.get("ziel") else None
        if i is None:
            vorhandene_ids = {x.get("id") for x in d["ideen"]}
            neue_id = e["id"] if e["id"] and e["id"] not in vorhandene_ids else secrets.token_hex(6)
            i = dict(id=neue_id, zeit=time.time(), bild="")
            d["ideen"].insert(0, i)
        i.update(de=e["de"], es=e["es"], notiz=e["notiz"], es_auto=e["es_auto"] if e["es_auto"] == e["es"] else "")
        if bild_bytes:
            fmt, _ = bild_pruefen(bild_bytes)
            roh, endung = _als_kartenbild(bild_bytes, fmt)
            alt = _idee_bildpfad(i)
            name = f"{i['id']}-{secrets.token_hex(3)}{endung}"
            _atomar(IDEEN_ORDNER / name, roh)
            if alt:
                _beiseite(alt)
            i["bild"], i["v"] = name, int(i.get("v", 0)) + 1
        _ideen_schreiben(d)


class _Leer:
    """Platzhalter für „keine ZIP-Datei“ im with-Block."""
    def __enter__(self):
        return None

    def __exit__(self, *_):
        return False


def import_verwerfen(daten):
    try:
        _import_pfad(daten.get("id")).unlink(missing_ok=True)
    except (ValueError, UI.Meldung):
        pass
    return {"ok": True}


# =============================================================================================
# Ideen für zukünftige Karten
# =============================================================================================
def _ideen_lesen():
    try:
        d = json.loads(IDEEN_DATEI.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) and isinstance(d.get("ideen"), list) else {"ideen": [], "entfernt": []}
    except (OSError, ValueError):
        return {"ideen": [], "entfernt": []}


def _ideen_schreiben(d):
    _atomar(IDEEN_DATEI, json.dumps(d, ensure_ascii=False, indent=1).encode("utf-8"))


def _idee_finden(d, iid):
    if not re.fullmatch(r"[0-9a-f]{12}", str(iid or "")):
        raise UI.Meldung("ungueltig")
    for i in d["ideen"]:
        if i.get("id") == iid:
            return i
    raise ValueError(tx("idee_fehlt"))


def _idee_bildpfad(i):
    name = i.get("bild") or ""
    if not name or not gl.sicherer_name(name):
        return None
    p = IDEEN_ORDNER / name
    return p if p.is_file() else None


def ideen_liste():
    d = _ideen_lesen()
    kd = UI.karten_daten()
    entwuerfe = [dict(id=m["id"], de=m.get("de", ""), es=m.get("es", ""), original=m.get("original", ""))
                 for m in UI._alle_entwuerfe() if not m.get("karte")]     # neues Bild einer Karte ist keine Idee
    offen = [dict(bild=k["bild"], de=k["de"], notiz=k["notiz"]) for k in kd["karten"] if k["offen"]]
    ohne = [dict(bild=n) for n in kd["ohne_karte"]]
    ideen = [dict(id=i["id"], de=i.get("de", ""), es=i.get("es", ""), es_auto=i.get("es_auto", ""),
                  notiz=i.get("notiz", ""), bild=bool(_idee_bildpfad(i)), zeit=i.get("zeit", 0),
                  v=i.get("v", 0)) for i in d["ideen"]]
    return dict(ideen=ideen, entwuerfe=entwuerfe, offen=offen, ohne=ohne)


def idee_speichern(daten):
    de, es, notiz = _text(daten.get("de"), 120), _text(daten.get("es")), _text(daten.get("notiz"))
    if _formel(de, es, notiz):
        raise ValueError(gl.pm("k_formel", "fehler")["text"])
    with _ideen_lock:
        d = _ideen_lesen()
        if daten.get("id"):
            i = _idee_finden(d, daten["id"])
        else:
            if not (de or es):
                raise ValueError(tx("idee_leer"))
            i = dict(id=secrets.token_hex(6), zeit=time.time(), bild="")
            d["ideen"].insert(0, i)
        es_auto = _text(daten.get("es_auto")) if "es_auto" in daten else i.get("es_auto", "")
        i.update(de=de, es=es, notiz=notiz, es_auto=es_auto if es_auto and es_auto == es else "")
        _ideen_schreiben(d)
    return dict(id=i["id"], **ideen_liste())


def idee_bild_setzen(iid, daten: bytes):
    """Bild einer Idee setzen (ohne id: neue Idee mit diesem Bild)."""
    fmt, _ = bild_pruefen(daten)
    roh, endung = _als_kartenbild(daten, fmt)
    with _ideen_lock:
        d = _ideen_lesen()
        if iid:
            i = _idee_finden(d, iid)
        else:
            i = dict(id=secrets.token_hex(6), zeit=time.time(), de="", es="", notiz="", bild="")
            d["ideen"].insert(0, i)
        alt = _idee_bildpfad(i)
        name = f"{i['id']}-{secrets.token_hex(3)}{endung}"
        _atomar(IDEEN_ORDNER / name, roh)
        if alt:
            _beiseite(alt)
        i["bild"], i["v"] = name, int(i.get("v", 0)) + 1
        _ideen_schreiben(d)
    return dict(id=i["id"], **ideen_liste())


def _beiseite(p):
    ziel = IDEEN_ORDNER / "_entfernt"
    ziel.mkdir(parents=True, exist_ok=True)
    try:
        shutil.move(str(p), str(ziel / p.name))
    except OSError:
        pass


def idee_bild(iid):
    from PIL import Image
    i = _idee_finden(_ideen_lesen(), iid)
    p = _idee_bildpfad(i)
    if not p:
        return None
    im = gl.oeffne_bild(p)
    im.thumbnail((900, 900), Image.Resampling.LANCZOS)
    puffer = io.BytesIO()
    im.save(puffer, "JPEG", quality=86)
    return puffer.getvalue()


def idee_weg(daten):
    with _ideen_lock:
        d = _ideen_lesen()
        i = _idee_finden(d, daten.get("id"))
        d["ideen"].remove(i)
        p = _idee_bildpfad(i)
        if p:
            _beiseite(p)
        d.setdefault("entfernt", []).insert(0, i)                # für „Rückgängig“ aufheben
        d["entfernt"] = d["entfernt"][:50]
        _ideen_schreiben(d)
    return ideen_liste()


def idee_zurueck(daten):
    with _ideen_lock:
        d = _ideen_lesen()
        for i in d.get("entfernt", []):
            if i.get("id") == daten.get("id"):
                d["entfernt"].remove(i)
                if i.get("bild") and gl.sicherer_name(i["bild"]) and (IDEEN_ORDNER / "_entfernt" / i["bild"]).is_file():
                    shutil.move(str(IDEEN_ORDNER / "_entfernt" / i["bild"]), str(IDEEN_ORDNER / i["bild"]))
                d["ideen"].insert(0, i)
                _ideen_schreiben(d)
                break
        else:
            raise ValueError(tx("idee_fehlt"))
    return ideen_liste()


def idee_aufnehmen(daten):
    """Idee → offizielle Karte: legt einen Entwurf an und übernimmt ihn mit allen Prüfungen von Schritt 1."""
    d = _ideen_lesen()
    i = _idee_finden(d, daten.get("id"))
    p = _idee_bildpfad(i)
    if not (p and i.get("de") and i.get("es")):
        raise ValueError(tx("idee_unvollstaendig"))
    erg = UI.entwurf_anlegen(p.read_bytes(), "idee" + p.suffix)
    eid = erg["id"]
    try:
        erg = UI.entwurf_pruefen(eid, dict(de=i["de"], es=i["es"], es_auto=i.get("es_auto", ""),
                                           ersetzen=bool(daten.get("ersetzen"))))
        if not erg["ok"]:
            UI.entwurf_weg(eid)
            return dict(ok=False, meldungen=[m for m in erg["meldungen"] if m["stufe"] in ("fehler", "warnung")],
                        kollision=erg.get("kollision", False))
        fertig = UI.entwurf_uebernehmen(eid, {})
    except Exception:
        try:
            UI.entwurf_weg(eid)
        except Exception:  # noqa: BLE001
            pass
        raise
    if i.get("notiz"):
        UI.setze_karte(fertig["name"], {"notiz": i["notiz"]}, anlegen=False)
    with _ideen_lock:
        d = _ideen_lesen()
        d["ideen"] = [x for x in d["ideen"] if x.get("id") != i["id"]]
        _ideen_schreiben(d)
    p.unlink(missing_ok=True)
    return dict(ok=True, name=fertig["name"], karten=UI.karten_daten(), **ideen_liste())


# =============================================================================================
# Programmstart: Browser oder eigenes Fenster (gelesen vom Startprogramm)
# =============================================================================================
def _starter():
    import starter                                         # nur Standardbibliothek, ohne Nebenwirkungen beim Import
    return starter


def start_einstellung():
    if UI.im_browser():                                    # Web-App: kein Startprogramm, nichts zu wählen
        return dict(gewaehlt=True, willkommen=True, art="browser", browser="standard", liste=[], fenster_moeglich=False,
                    vom_starter=False)
    st = _starter()
    wahl = st.lies_start_wahl()
    browser = [dict(id=b["id"], name=b["name"], fenster=b["fenster"]) for b in st.finde_browser()]
    return dict(gewaehlt=bool(wahl), willkommen=bool(wahl and wahl.get("willkommen")),
                art=(wahl or {}).get("art", "browser"), browser=(wahl or {}).get("browser", "standard"),
                liste=browser, fenster_moeglich=any(b["fenster"] for b in browser),
                vom_starter=bool(os.environ.get("MGD_START_ID")))


def start_setzen(daten):
    st = _starter()
    art = "fenster" if daten.get("art") == "fenster" else "browser"
    ids = {b["id"] for b in st.finde_browser()}
    browser = daten.get("browser") if daten.get("browser") in ids else "standard"
    alt = st.lies_start_wahl() or {}
    st.schreibe_start_wahl(dict(art=art, browser=browser, willkommen=daten.get("willkommen") is True or alt.get("willkommen") is True))
    return dict(start_einstellung(), meldung=tx("start_gespeichert"))


# =============================================================================================
# Deinstallieren
# =============================================================================================
def deinstallieren(daten):
    if daten.get("bestaetigt") is not True:
        raise ValueError(tx("deinst_bestaetigen"))
    st = _starter()
    if not st.deinstallation_erlaubt():
        raise ValueError(tx("deinst_ort"))
    if getattr(UI, "warteschlange", None):                    # wartende Aufträge verwerfen, laufenden stoppen
        UI.warteschlange.alles_stoppen()
    befehl =[sys.executable, str(HIER / "starter.py"), "--deinstallieren", "--app"]
    kw = dict(stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=str(Path.home()),
              env=dict(os.environ, MGD_SPRACHE=gl.sprache()), close_fds=True)
    if os.name == "nt":
        flags = 0x00000200 | 0x08000000                       # CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW
        try:
            subprocess.Popen(befehl, creationflags=flags | 0x01000000, **kw)   # vom Job der Oberfläche lösen
        except OSError:
            subprocess.Popen(befehl, creationflags=flags, **kw)
    else:
        subprocess.Popen(befehl, start_new_session=True, **kw)
    return dict(meldung=tx("deinst_laeuft"))


# =============================================================================================
# Werkzeuge (Zeilen unter „Werkzeuge“; art="dialog" öffnet ein Fenster der Seite)
# =============================================================================================
def _werkzeuge_anmelden():
    if any(w["id"] == "import-export" for w in UI.WERKZEUGE):
        return

    @UI.werkzeug("import-export", L("Karten importieren / exportieren", "Import / export cards",
                                    "Importar / exportar cartas"),
                 L("Karten mit Bildern als ZIP sichern oder weitergeben – und solche ZIP-Dateien (oder eine CSV) "
                   "wieder einlesen. Vor dem Import siehst du, was neu ist und was schon da ist.",
                   "Save or share cards with images as a ZIP – and read such ZIP files (or a CSV) back in. Before "
                   "importing you see what is new and what already exists.",
                   "Guarda o comparte cartas con imágenes como ZIP, y vuelve a leer esos ZIP (o un CSV). Antes de "
                   "importar ves qué es nuevo y qué ya existe."),
                 L("Öffnen …", "Open …", "Abrir …"), art="dialog")
    def _w_import_export():
        return {"dialog": "import-export"}

    @UI.werkzeug("gans-werkzeug", L("GANS-Bild gestalten", "Design a GANS image", "Diseñar imagen GANS"),
                 L("Aus einem Gänse-Foto ein Kartenbild mit dem Wortwitz „GANS + Wort“ bauen: zuschneiden, Text "
                   "setzen, verschieben, Größe und Schrift wählen.",
                   "Turn a goose photo into a card image with the pun “GANS + word”: crop, add text, move it, "
                   "choose size and font.",
                   "Convierte una foto de ganso en imagen de carta con el juego «GANS + palabra»: recorta, pon el "
                   "texto, muévelo, elige tamaño y letra."),
                 L("Öffnen …", "Open …", "Abrir …"), art="dialog")
    def _w_gans_werkzeug():
        return {"dialog": "gans-werkzeug"}

    @UI.werkzeug("farben", L("🎨 Farben & Darstellung", "🎨 Colors & appearance", "🎨 Colores y apariencia"),
                 L("Hintergrund und Farben der Oberfläche ändern: fertige Schemata (hell, dunkel, Wiese, hoher Kontrast, "
                   "wie das System) oder eigene Farben. Der Standard bleibt, wie er ist.",
                   "Change the background and colors of the interface: ready-made schemes (light, dark, meadow, high "
                   "contrast, like the system) or your own colors. The default stays as it is.",
                   "Cambia el fondo y los colores de la interfaz: esquemas listos (claro, oscuro, pradera, alto "
                   "contraste, como el sistema) o tus propios colores. El estándar sigue igual."),
                 L("Öffnen …", "Open …", "Abrir …"), art="dialog")
    def _w_farben():
        return {"dialog": "farben"}

    @UI.werkzeug("programmstart", L("Programmstart: Browser oder eigenes Fenster", "Program start: browser or own window",
                                    "Inicio: navegador o ventana propia"),
                 L("Wählen, ob sich die Oberfläche im Standard-Browser, in einem bestimmten Browser oder in einem "
                   "eigenen Fenster ohne Adressleiste öffnet.",
                   "Choose whether the interface opens in the default browser, a specific browser or its own window "
                   "without an address bar.",
                   "Elige si la interfaz se abre en el navegador predeterminado, en uno concreto o en una ventana "
                   "propia sin barra de direcciones."),
                 L("Ändern …", "Change …", "Cambiar …"), art="dialog", zustand=_start_zustand, nur_rechner=True)
    def _w_programmstart():
        return {"dialog": "programmstart"}
    # Deinstallieren hat einen eigenen, letzten Reiter („Deinstallieren“) – nicht mehr unter den Werkzeugen.

    @UI.werkzeug("handy", L("Am Handy öffnen (WLAN)", "Open on your phone (Wi-Fi)", "Abrir en el celular (wifi)"),
                 L("Die Oberfläche im eigenen WLAN auf Handy oder Tablet benutzen – z. B. um Fotos direkt vom Handy "
                   "hochzuladen. Zugang nur mit PIN, schaltet sich nach 2 Stunden von selbst ab. Oder die Gans als App "
                   "aufs Handy holen (QR-Code).",
                   "Use the interface on your phone or tablet in your own Wi-Fi – e.g. to upload photos straight from "
                   "your phone. Access only with a PIN; switches itself off after 2 hours. Or get the goose onto your "
                   "phone as an app (QR code).",
                   "Usa la interfaz en el celular o la tableta dentro de tu wifi, p. ej. para subir fotos directo del "
                   "celular. Acceso solo con PIN; se apaga solo después de 2 horas. O llévate el ganso al celular como "
                   "app (código QR)."),
                 L("Einrichten …", "Set up …", "Configurar …"), art="dialog", zustand=_lan_zustand, nur_rechner=True)
    def _w_handy():
        return {"dialog": "handy"}


def _lan_zustand():
    return (L("an", "on", "activado"), True) if _LAN["an"] else (L("aus", "off", "apagado"), True)


def _start_zustand():
    try:
        wahl = _starter().lies_start_wahl()
    except Exception:  # noqa: BLE001
        wahl = None
    if not wahl:
        return L("Standard-Browser", "Default browser", "Navegador predeterminado"), True
    if wahl.get("art") == "fenster":
        return L("eigenes Fenster", "own window", "ventana propia"), True
    if wahl.get("browser", "standard") != "standard":
        return L(wahl["browser"].capitalize(), wahl["browser"].capitalize(), wahl["browser"].capitalize()), True
    return L("Standard-Browser", "Default browser", "Navegador predeterminado"), True


# =============================================================================================
# Handy-Zugang im WLAN (optional, standardmäßig aus): zweiter Server auf der Adresse im Heimnetz, Zugang nur mit
# 6-stelliger PIN; aus nach 120 Minuten, nach 5 falschen PINs oder beim Beenden. Unverschlüsselt (HTTP) – daher nur
# im eigenen WLAN und nur, solange es gebraucht wird.
# =============================================================================================
LAN_MINUTEN = 120
LAN_VERSUCHE = 5
_LAN = dict(an=False, ip=None, port=None, pin=None, server=None, bis=0.0, fehlversuche=0)
_lan_lock = threading.Lock()

LAN_TEXTE = {
    "lan_kein_netz": L("Kein Heimnetz gefunden – ist der Rechner mit dem WLAN verbunden?",
                       "No home network found – is the computer connected to Wi-Fi?",
                       "No se encontró una red doméstica: ¿la computadora está conectada al wifi?"),
    "lan_pin_falsch": L("Die PIN stimmt noch nicht – schau noch einmal auf den Rechner.",
                        "That PIN isn’t right yet – have another look at the computer.",
                        "El PIN todavía no es correcto; vuelve a mirar la computadora."),
    "lan_titel": L("Me Goos-ta Deutsch am Handy", "Me Goos-ta Deutsch on your phone", "Me Goos-ta Deutsch en el celular"),
    "lan_text": L("Gib die 6-stellige PIN ein, die auf dem Rechner unter Werkzeuge → „Am Handy öffnen“ steht.",
                  "Enter the 6-digit PIN shown on the computer under Tools → “Open on your phone”.",
                  "Escribe el PIN de 6 dígitos que aparece en la computadora en Herramientas → «Abrir en el celular»."),
    "lan_knopf": L("Verbinden", "Connect", "Conectar"),
    "lan_nur_rechner": L("Das geht nur direkt am Rechner – am Handy ist alles andere für dich da.",
                         "That one works only on the computer itself – everything else is all yours on the phone.",
                         "Eso solo funciona en la computadora; todo lo demás es tuyo en el celular."),
}
# Was das Handy nicht darf: Programm beenden/deinstallieren, Dinge am Rechner öffnen, Start- und Handy-Einstellungen.
LAN_GESPERRT = {"/api/deinstallieren", "/api/beenden", "/api/oeffnen", "/api/lan", "/api/start-einstellung"}


def lan_gesperrt(h, weg):
    return lan_ist(h) and weg in LAN_GESPERRT


def _lan_tx(code):
    return gl.text_in(LAN_TEXTE[code])


def lan_ip():
    """Adresse dieses Rechners im Heimnetz (nur private Bereiche) – ohne etwas zu senden (UDP-connect)."""
    import ipaddress
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
    except OSError:
        return None
    finally:
        s.close()
    try:
        a = ipaddress.ip_address(ip)
    except ValueError:
        return None
    return ip if a.is_private and not a.is_loopback and not a.is_link_local else None


def lan_status():
    an = _LAN["an"]
    return dict(an=an, adresse=f"http://{_LAN['ip']}:{_LAN['port']}" if an else "", pin=_LAN["pin"] if an else "",
                minuten=max(0, int((_LAN["bis"] - time.time()) // 60)) if an else 0, ip_gefunden=bool(lan_ip()))


def _lan_port_datei():
    import uebersetzer
    return uebersetzer.daten_ordner() / "handy-port.txt"


def _lan_server(ip):
    """Gleicher Port wie beim letzten Mal (Lesezeichen und Gespeichertes am Handy bleiben gültig), sonst ein freier."""
    try:
        alt = int(_lan_port_datei().read_text(encoding="utf-8").strip())
        if 1024 <= alt <= 65535:
            return UI.Server((ip, alt), UI.Handler)
    except (OSError, ValueError):
        pass
    server = UI.Server((ip, 0), UI.Handler)
    try:
        _lan_port_datei().parent.mkdir(parents=True, exist_ok=True)
        _lan_port_datei().write_text(str(server.server_address[1]), encoding="utf-8")
    except OSError:
        pass
    return server


def lan_starten():
    with _lan_lock:
        if _LAN["an"]:
            return lan_status()
        ip = lan_ip()
        if not ip:
            raise ValueError(_lan_tx("lan_kein_netz"))
        server = _lan_server(ip)
        _LAN.update(an=True, ip=ip, port=server.server_address[1], pin=f"{secrets.randbelow(10 ** 6):06d}",
                    server=server, bis=time.time() + LAN_MINUTEN * 60, fehlversuche=0)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        threading.Thread(target=_lan_wache, args=(server,), daemon=True).start()
    return lan_status()


def lan_stoppen():
    with _lan_lock:
        server = _LAN.get("server")
        _LAN.update(an=False, pin=None, server=None)
    if server is not None:
        threading.Thread(target=lambda: (server.shutdown(), server.server_close()), daemon=True).start()
    return lan_status()


def _lan_wache(server):
    while _LAN["server"] is server:
        if time.time() > _LAN["bis"]:
            lan_stoppen()
            return
        time.sleep(5)


def lan_ist(h):
    """Kommt die Anfrage über den Handy-Server?"""
    return _LAN["server"] is not None and h.server is _LAN["server"]


def lan_host_ok(h):
    host = (h.headers.get("Host") or "").strip().lower()
    return lan_ist(h) and _LAN["an"] and host == f"{_LAN['ip']}:{_LAN['port']}"


def lan_origin_ok(h):
    o = h.headers.get("Origin")
    return o is None or o == f"http://{_LAN['ip']}:{_LAN['port']}"


LAN_SEITE = """<!doctype html><html lang="__LANG__"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>__TITEL__</title>
<style>body{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;background:#E8F2FA;color:#1B2D4F;display:grid;
place-items:center;min-height:100vh;margin:0;padding:16px;box-sizing:border-box}main{background:#fff;border-radius:16px;
padding:24px;max-width:380px;width:100%;text-align:center;box-shadow:0 8px 28px rgba(27,45,79,.15)}
input{font-size:28px;letter-spacing:6px;text-align:center;width:100%;padding:10px;border:2px solid #C9DCEB;
border-radius:10px;box-sizing:border-box}button{margin-top:14px;width:100%;font-size:18px;padding:12px;border:0;
border-radius:10px;background:#F6A94B;color:#1B2D4F;font-weight:700}p.f{color:#C9383C;min-height:1.2em}</style></head>
<body><main><h1>__TITEL__</h1><p>__TEXT__</p><input id="pin" inputmode="numeric" autocomplete="one-time-code"
maxlength="6" pattern="[0-9]*" aria-label="PIN"><button id="los">__KNOPF__</button><p class="f" id="f"></p></main>
<script nonce="__NONCE__">
document.getElementById("los").addEventListener("click", async () => {
  const r = await fetch("/lan-pin", { method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pin: document.getElementById("pin").value.trim() }), credentials: "same-origin" });
  if (r.ok) location.href = "/"; else { const d = await r.json().catch(() => ({})); document.getElementById("f").textContent = d.fehler || "?"; }
});
document.getElementById("pin").addEventListener("keydown", e => { if (e.key === "Enter") document.getElementById("los").click(); });
</script></body></html>"""


def lan_pin_seite(h):
    nonce = secrets.token_urlsafe(16)
    seite = (LAN_SEITE.replace("__LANG__", gl.sprache()).replace("__TITEL__", html_esc(_lan_tx("lan_titel")))
             .replace("__TEXT__", html_esc(_lan_tx("lan_text"))).replace("__KNOPF__", html_esc(_lan_tx("lan_knopf")))
             .replace("__NONCE__", nonce))
    h._senden(200, seite, "text/html; charset=utf-8", nonce=nonce)


def lan_pin(h):
    """POST /lan-pin {pin}: richtige PIN → Sitzungs-Cookie; nach 5 falschen PINs schaltet sich der Zugang ab."""
    n = int(h.headers.get("Content-Length") or 0)
    roh = h.rfile.read(min(n, 1024)) if n else b""
    try:
        pin = str(json.loads(roh.decode("utf-8") or "{}").get("pin", ""))
    except (ValueError, AttributeError):
        pin = ""
    import hmac
    if _LAN["an"] and _LAN["pin"] and hmac.compare_digest(pin.encode(), _LAN["pin"].encode()):
        h.send_response(200)
        h.send_header("Set-Cookie", f"mgd_{UI.PORT}={UI.TOKEN}; HttpOnly; SameSite=Strict; Path=/")
        h.send_header("Content-Type", "application/json; charset=utf-8")
        h.send_header("Cache-Control", "no-store")
        h.send_header("Content-Length", "11")
        h.end_headers()
        h.wfile.write(b'{"ok":true}')
        return
    _LAN["fehlversuche"] += 1
    if _LAN["fehlversuche"] >= LAN_VERSUCHE:
        lan_stoppen()
    h._fehler(403, _lan_tx("lan_pin_falsch"))


def html_esc(t):
    import html
    return html.escape(str(t), quote=True)


# =============================================================================================
# HTTP-Anbindung (von gans_ui.Handler aufgerufen; True = erledigt)
# =============================================================================================
def get(h, weg, q):
    eins = lambda k, d="": q.get(k, [d])[0]                          # noqa: E731
    if weg == "/api/export":
        art = eins("inhalt", "karten")
        inhalt, name = export_zip("aktiv" if eins("umfang") == "aktiv" else "alle",
                                  art if art in ("karten", "ideen", "alles") else "karten")
        from urllib.parse import quote
        h._senden(200, inhalt, "application/zip", {"Content-Disposition": f"attachment; filename*=UTF-8''{quote(name)}"})
        return True
    if weg == "/api/ideen":
        h._senden(200, ideen_liste())
        return True
    if weg == "/api/idee-bild":
        inhalt = idee_bild(eins("id"))
        if not inhalt:
            h._fehler(404, UI.tx("datei_fehlt"))
        else:
            h._senden(200, inhalt, "image/jpeg")
        return True
    if weg == "/api/start-einstellung":
        h._senden(200, start_einstellung())
        return True
    if weg == "/api/lan":
        h._senden(200, lan_status())
        return True
    return False


ROH_WEGE = ("/api/import", "/api/idee-bild")


def post_roh(h, weg, q):
    """POST mit rohen Bytes (Datei). True = erledigt."""
    n = int(h.headers.get("Content-Length") or 0)
    if weg == "/api/import":
        h._senden(200, import_speichern(h.rfile.read, n))
        return True
    if weg == "/api/idee-bild":
        if n <= 0 or n > UI.MAX_BILD:
            h._senden(400, {"fehler": gl.pm("b_datei_gross", "fehler", mb=gl.MAX_DATEI_MB)["text"]})
            return True
        h._senden(200, idee_bild_setzen(q.get("id", [""])[0], h.rfile.read(n)))
        return True
    return False


POST_WEGE = {
    "/api/import-pruefen": lambda d: import_pruefen(d.get("id")),
    "/api/import-uebernehmen": import_uebernehmen,
    "/api/import-verwerfen": import_verwerfen,
    "/api/idee": idee_speichern,
    "/api/idee-weg": idee_weg,
    "/api/idee-zurueck": idee_zurueck,
    "/api/idee-aufnehmen": idee_aufnehmen,
    "/api/start-einstellung": start_setzen,
    "/api/deinstallieren": deinstallieren,
    "/api/uebersetzen-de": lambda d: uebersetzen_de(d),
    "/api/lan": lambda d: lan_starten() if d.get("an") is True else lan_stoppen(),
}


def uebersetzen_de(daten):
    """Ideen: Wort in der Kartensprache → Vorschlag für den „Text auf dem Bild“ („viejo“ → „Gans alt“). Gleiche Regeln
    wie die Übersetzung in die Kartensprache (Zustimmung, nur das Wort, feste Dienste) – siehe uebersetzer.py."""
    import uebersetzer
    dienst = daten.get("dienst") if daten.get("dienst") in uebersetzer.STRATEGIEN else None
    erg = uebersetzer.uebersetze(str(daten.get("es") or "")[:200], dienst, richtung=f"{UI.zielsprache()}-de")
    texte = [a["text"] for a in erg.get("alternativen") or []]
    return dict(erg, dienst_name=uebersetzer.dienst_titel(erg.get("dienst"), gl.sprache()),
                de_text=("Gans " + texte[0]) if texte else "",
                de_alternativen=[dict(text="Gans " + a["text"], hinweis=a.get("hinweis", "")) for a in erg.get("alternativen") or []])


def post(h, weg, daten):
    fn = POST_WEGE.get(weg)
    if not fn:
        return False
    h._senden(200, fn(daten))
    return True
