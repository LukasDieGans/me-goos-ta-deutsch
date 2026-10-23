#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ME GOOS-TA DEUTSCH – Erweiterungen der Oberfläche                   Version 2.4 (22.10.2026)
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
BILD_IDEE_MAX = 300                          # Zeichen der Bildidee (= Länge der KI-Bild-Beschreibung)
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
    "wl_dateiart": L("Das sieht nach einer {art}-Datei aus – die Wortliste mag es schlicht: bitte als „CSV UTF-8“ "
                     "oder als Text (.txt) speichern und nochmal wählen.",
                     "This looks like a {art} file – the word list likes it plain: please save it as “CSV UTF-8” "
                     "or as text (.txt) and choose it again.",
                     "Esto parece un archivo {art}; la lista de palabras lo prefiere sencillo: guárdalo como "
                     "«CSV UTF-8» o como texto (.txt) y vuelve a elegirlo."),
    "wl_gross": L("Die Wortliste ist größer als {mb} MB – teil sie einfach in kleinere Listen auf.",
                  "The word list is larger than {mb} MB – just split it into smaller lists.",
                  "La lista de palabras pesa más de {mb} MB; divídela en listas más pequeñas y listo."),
    "wl_unlesbar": L("In dieser Datei steckt kein lesbarer Text – bitte als „CSV UTF-8“ oder Text (.txt) speichern.",
                     "This file holds no readable text – please save it as “CSV UTF-8” or text (.txt).",
                     "Este archivo no trae texto legible; guárdalo como «CSV UTF-8» o texto (.txt)."),
    "wl_cp1252": L("Die Liste ist nicht als UTF-8 gespeichert (als Windows-1252 gelesen) – schau in der Vorschau kurz "
                   "auf Umlaute und Akzente.",
                   "The list is not saved as UTF-8 (read as Windows-1252) – take a quick look at umlauts and accents "
                   "in the preview.",
                   "La lista no está guardada en UTF-8 (leída como Windows-1252); revisa rápido diéresis y acentos "
                   "en la vista previa."),
    "wl_leer": L("Die Wortliste ist noch leer – schreib einfach ein Wort pro Zeile.",
                 "The word list is still empty – just write one word per line.",
                 "La lista de palabras aún está vacía; escribe una palabra por línea y listo."),
    "wl_nur_kopf": L("In der Liste steht nur die Kopfzeile – darunter fehlen noch die Wörter.",
                     "The list only has the header row – the words below it are still missing.",
                     "La lista solo tiene la fila de encabezado; faltan las palabras debajo."),
    "wl_zu_viele": L("Die Liste hat {n} Wörter – höchstens {max} gehen auf einmal. Teil sie bitte in mehrere Listen auf "
                     "(abgeschnitten wird nichts).",
                     "The list has {n} words – at most {max} fit at once. Please split it into several lists "
                     "(nothing gets cut off).",
                     "La lista tiene {n} palabras; caben {max} como máximo a la vez. Divídela en varias listas "
                     "(no se recorta nada)."),
    "wl_spalten": L("{n} Spalten – höchstens 3 gehen (Deutsch, {zs}, Notiz). Alternativen bitte mit „/“ trennen.",
                    "{n} columns – at most 3 work (German, {zs}, note). Please separate alternatives with “/”.",
                    "{n} columnas; caben 3 como máximo (alemán, {zs}, nota). Separa las alternativas con «/»."),
    "wl_komma_alt": L("Einige Zeilen haben mit Komma 3 Spalten – war die 3. Spalte vielleicht eine Alternative? Dann "
                      "„/“ statt Komma nehmen oder als Trennzeichen „;“ wählen.",
                      "Some lines have 3 columns with commas – was the 3rd column maybe an alternative? Then use “/” "
                      "instead of a comma or choose “;” as separator.",
                      "Algunas líneas tienen 3 columnas con coma; ¿la 3.ª columna era quizá una alternativa? Entonces "
                      "usa «/» en vez de coma o elige «;» como separador."),
    "wl_kopf_sprache": L("Die Kopfzeile nennt {sprache}, die Karten sind gerade auf {zs} – die Spalte wird als {zs} "
                         "übernommen. Für eine andere Sprache vorher die Kartensprache wechseln.",
                         "The header names {sprache}, the cards are currently in {zs} – the column is taken as {zs}. "
                         "For another language, switch the card language first.",
                         "El encabezado dice {sprache} y las cartas están en {zs}; la columna se toma como {zs}. "
                         "Para otro idioma, cambia antes el idioma de las cartas."),
    "wl_lang": L("{feld} ist {n} Zeichen lang – höchstens {max} gehen. Bitte kürzen (still abgeschnitten wird nichts).",
                 "{feld} is {n} characters long – at most {max} fit. Please shorten it (nothing is cut off silently).",
                 "{feld} tiene {n} caracteres; caben {max} como máximo. Acórtalo, por favor (no se recorta nada "
                 "a escondidas)."),
    "wl_keine_buchstaben": L("Im deutschen Text steht noch kein Buchstabe – so wird daraus keine Karte.",
                             "The German text has no letter yet – that can’t become a card.",
                             "El texto en alemán aún no tiene letras; así no puede ser carta."),
    "wl_nur_gans": L("Nur „Gans“ ist noch kein Wort – was macht die Gans denn?",
                     "Just “Gans” isn’t a word yet – what is the goose up to?",
                     "Solo «Gans» aún no es palabra; ¿qué hace el ganso?"),
    "wl_zeichen": L("Ein paar Zeichen passen nicht zu {zs} – kurz prüfen, ob die Spalten stimmen.",
                    "A few characters don’t fit {zs} – quickly check that the columns are right.",
                    "Algunos caracteres no encajan con {zs}; revisa rápido que las columnas estén bien."),
    "wl_neu": L("Neue Idee", "New idea", "Idea nueva"),
    "wl_idee_da": L("Gibt es schon als Idee", "Already exists as an idea", "Ya existe como idea"),
    "wl_doppelt": L("Steht schon in Zeile {nr}", "Already in line {nr}", "Ya está en la línea {nr}"),
    "wl_doppelt_anders": L("Steht schon in Zeile {nr} (dort mit „{wort}“)", "Already in line {nr} (there with “{wort}”)",
                           "Ya está en la línea {nr} (allí con «{wort}»)"),
    "wl_zs_geaendert": L("Die Kartensprache wurde inzwischen gewechselt – prüf die Liste einfach noch einmal.",
                         "The card language has changed in the meantime – just check the list once more.",
                         "El idioma de las cartas cambió mientras tanto; revisa la lista otra vez y listo."),
    "wl_nichts": L("Noch keine Zeile ausgewählt – wähl mindestens ein Wort aus.",
                   "No line selected yet – pick at least one word.",
                   "Aún no hay ninguna línea elegida; elige al menos una palabra."),
    "wl_rueck_fehlt": L("Diese Wortliste ist schon ganz zurückgenommen – da gibt es nichts mehr rückgängig zu machen.",
                        "This word list has already been fully undone – nothing left to undo.",
                        "Esta lista ya se deshizo por completo; no queda nada por deshacer."),
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
    _sichere(pfad)
    os.replace(tmp, pfad)


def _sichere(pfad):
    """Vor dem Überschreiben/Verschieben/Löschen: für „Rückgängig“ aufheben (gans_ui → verlauf.py, seit 2.4)."""
    if UI is not None and hasattr(UI, "_sichere"):
        UI._sichere(pfad)


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
                eintrag = {k: i.get(k, "") for k in ("id", "de", "es", "es_auto", "notiz", "bild", "bild_idee")}
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
            aus.append({k: e.get(k) if isinstance(e.get(k), str) else ""
                        for k in ("id", "de", "es", "es_auto", "notiz", "bild", "bild_idee")})
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
                     es_auto=_text(roh["es_auto"]), bild_idee=_text(roh.get("bild_idee")), bild="", status="neu",
                     text=tx("i_neu"), ziel=None, bild_neu=False)
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
            if e["status"] != "fehler" and _formel(e["de"], e["es"], e["notiz"], e["bild_idee"]):
                e.update(status="fehler", text=gl.pm("k_formel", "fehler")["text"])
            if e["status"] != "fehler" and not (e["de"] or e["es"] or e["bild"] or e["bild_idee"]):
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
                    and bool(gleich.get("bild")) == bool(e["bild"]) \
                    and (not e["bild_idee"] or gleich.get("bild_idee", "") == e["bild_idee"])   # ältere Exporte ohne Bildidee
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
                if str(e.get("de") or "").strip() and not gl.hat_gans(e["de"]):      # jede Karte braucht ihre Gans
                    e = dict(e, de=gl.mit_gans(e["de"]))
                    zahl["gans"] = zahl.get("gans", 0) + 1
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
    aus = dict(zahlen=zahl, karten=UI.karten_daten(), **ideen_liste())
    if zahl.get("gans"):
        aus["gans_hinweis"] = UI.tx("gans_davor_n", n=zahl["gans"])
    return aus


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
        if e.get("bild_idee"):                                  # ältere Exporte kennen die Bildidee nicht → vorhandene bleibt
            i["bild_idee"] = e["bild_idee"]
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
                  notiz=i.get("notiz", ""), bild_idee=i.get("bild_idee", ""), bild=bool(_idee_bildpfad(i)),
                  zeit=i.get("zeit", 0), v=i.get("v", 0)) for i in d["ideen"]]
    return dict(ideen=ideen, entwuerfe=entwuerfe, offen=offen, ohne=ohne)


def idee_speichern(daten):
    """Texte einer Idee speichern (ohne id: neue Idee). „bild_idee“ (Merkzettel, wie das Bild aussehen könnte – auch
    Beschreibung für ein KI-Bild) ändert sich nur, wenn es mitgeschickt wird."""
    de, es, notiz = _text(daten.get("de"), 120), _text(daten.get("es")), _text(daten.get("notiz"))
    bild_idee = _text(daten.get("bild_idee"), BILD_IDEE_MAX) if "bild_idee" in daten else None
    if _formel(de, es, notiz, bild_idee):
        raise ValueError(gl.pm("k_formel", "fehler")["text"])
    with _ideen_lock:
        d = _ideen_lesen()
        if daten.get("id"):
            i = _idee_finden(d, daten["id"])
        else:
            if not (de or es or bild_idee):
                raise ValueError(tx("idee_leer"))
            i = dict(id=secrets.token_hex(6), zeit=time.time(), bild="")
            d["ideen"].insert(0, i)
        es_auto = _text(daten.get("es_auto")) if "es_auto" in daten else i.get("es_auto", "")
        i.update(de=de, es=es, notiz=notiz, es_auto=es_auto if es_auto and es_auto == es else "")
        if bild_idee is not None:
            i["bild_idee"] = bild_idee
        _ideen_schreiben(d)
    return dict(id=i["id"], **ideen_liste())


def idee_wort_fuellen(daten):
    """„🌐 Alle übersetzen“ in Ideen: Wort der Kartensprache nur eintragen, wenn es beim Speichern noch leer ist (die
    Person kann inzwischen selbst etwas eingetragen haben) – als „automatisch – prüfen“ (es_auto). Eine unveränderte
    Wortlisten-Idee bleibt dabei unverändert im Sinne von Rückgängig (Fingerabdruck wird mitgeführt)."""
    es = _text(daten.get("es"))
    if not es:
        raise UI.Meldung("ungueltig")
    if _formel(es):
        raise ValueError(gl.pm("k_formel", "fehler")["text"])
    with _ideen_lock:
        d = _ideen_lesen()
        i = _idee_finden(d, daten.get("id"))
        gefuellt = not i.get("es")
        if gefuellt:
            unveraendert = bool(i.get("wl")) and i.get("fp") == _wl_fingerabdruck(i)
            i.update(es=es, es_auto=es)
            if unveraendert:
                i["fp"] = _wl_fingerabdruck(i)
            _ideen_schreiben(d)
    return dict(id=i["id"], gefuellt=gefuellt, **ideen_liste())


def idee_bild_setzen(iid, daten: bytes, de=""):
    """Bild einer Idee setzen (ohne id: neue Idee mit diesem Bild). de: Text auf dem Bild, nur falls die Idee noch
    keinen hat (KI-Bild „ohne Wort für die Idee“)."""
    fmt, _ = bild_pruefen(daten)
    roh, endung = _als_kartenbild(daten, fmt)
    de = _text(de, 120)
    if _formel(de):
        de = ""
    with _ideen_lock:
        d = _ideen_lesen()
        if iid:
            i = _idee_finden(d, iid)
        else:
            i = dict(id=secrets.token_hex(6), zeit=time.time(), de="", es="", notiz="", bild="")
            d["ideen"].insert(0, i)
        if de and not i.get("de"):
            i["de"] = de
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
    _sichere(p)
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
                    _sichere(IDEEN_ORDNER / "_entfernt" / i["bild"])
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
    de = gl.mit_gans(i["de"])                                  # jede Karte braucht ihre Gans (seit 2.4)
    try:
        erg = UI.entwurf_pruefen(eid, dict(de=de, es=i["es"], es_auto=i.get("es_auto", ""),
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
    _sichere(p)
    p.unlink(missing_ok=True)
    aus = dict(ok=True, name=fertig["name"], karten=UI.karten_daten(), **ideen_liste())
    if de != " ".join(str(i["de"]).split()):
        aus["gans_hinweis"] = UI.tx("gans_davor", de=de)
    return aus


# =============================================================================================
# Wortliste: viele Ideen auf einmal (Datei oder eingefügter Text → Vorschau je Zeile → Anlegen → Rückgängig).
# Grundsatz: nie still etwas Falsches anlegen – nichts wird gekürzt oder abgeschnitten, jede Zeile hat einen Status,
# das Anlegen prüft jede Zeile erneut (die Vorschau kann veraltet sein).
# =============================================================================================
WL_MAX_BYTES = 1024 * 1024
WL_MAX_ZEILEN = 500
WL_LAENGE = dict(de=120, wort=300, notiz=300)
WL_TRENNER = ("auto", "tab", "semikolon", "komma", "gleich", "strich", "keiner")
_WL_DATEIARTEN = ((b"PK\x03\x04", "Excel/ZIP"), (b"%PDF", "PDF"), (b"\xD0\xCF\x11\xE0", "Excel/Word"),
                  (b"{\\rtf", "RTF"), (b"\x89PNG", "PNG"), (b"\xFF\xD8\xFF", "JPG"), (b"GIF8", "GIF"))
_WL_NULLBREITE = dict.fromkeys(map(ord, "​‌‍⁠﻿­"))
_WL_LISTENZEICHEN = re.compile(r"^(?:[-*•–—·]|\d{1,3}[.)])\s+")
_WL_STRICH = re.compile(r"\s+[-–—]\s+")
_WL_GANS = re.compile(r"^(?:gans|ganz)(?:\s+|$)", re.I)
_WL_ANFUEHRUNG = "„“”‚‘’«»‹›\"'"
_WL_DE_NAMEN = {"deutsch", "german", "aleman", "de", "deu", "ger", "text", "textaufdembild"}
_WL_NOTIZ_NAMEN = {"notiz", "notizen", "note", "notes", "nota", "notas", "anmerkung", "comment", "comentario"}
_WL_ZS_NAMEN = {"ubersetzung", "uebersetzung", "translation", "traduccion", "wort", "word", "palabra"}


class WortlisteFehler(ValueError):
    """Die ganze Liste lässt sich nicht einlesen (Dateiart, Kodierung, Größe, leer) – Text für die Oberfläche."""
    def __init__(self, code, **werte):
        super().__init__(tx(code, **werte))
        self.code = code


def _wl_dateiart(roh: bytes):
    """Stufe 1: Tabellen, PDF, Bilder … erkennen (Signatur am Anfang) → Name der Dateiart, sonst None."""
    for kopf, art in _WL_DATEIARTEN:
        if roh.startswith(kopf):
            return art
    if roh[:4] == b"RIFF" and roh[8:12] == b"WEBP":
        return "WEBP"
    if roh[4:12] in gl.HEIC_MARKEN:
        return "HEIC"
    return None


def _wl_dekodieren(roh: bytes):
    """Stufe 2: BOM (UTF-8, UTF-16 LE/BE – Excel „Unicode-Text“) → NUL-Muster (UTF-16 ohne BOM) → UTF-8 streng →
    Windows-1252 mit Hinweis. → (Text, Kodierung, Hinweise)."""
    if roh.startswith(b"\xef\xbb\xbf"):
        kandidaten = [("utf-8", roh[3:])]
    elif roh.startswith((b"\xff\xfe", b"\xfe\xff")):
        kandidaten = [("utf-16-le" if roh[0] == 0xFF else "utf-16-be", roh[2:])]
    else:
        kandidaten = []
        paare = len(roh) // 2
        if paare and b"\x00" in roh:
            ungerade, gerade = roh[1::2].count(0), roh[0::2].count(0)
            if ungerade >= 0.3 * paare and gerade < 0.05 * paare:
                kandidaten.append(("utf-16-le", roh))
            elif gerade >= 0.3 * paare and ungerade < 0.05 * paare:
                kandidaten.append(("utf-16-be", roh))
        if b"\x00" not in roh:
            kandidaten += [("utf-8", roh), ("cp1252", roh)]
    for kodierung, daten in kandidaten:
        try:
            text = daten.decode(kodierung)
        except UnicodeDecodeError:
            continue
        steuer = sum(1 for c in text if unicodedata.category(c) == "Cc" and c not in "\t\r\n")
        if steuer > max(2, len(text) // 20):                   # Binärdaten, die zufällig dekodierbar sind
            continue
        return text, kodierung, ([tx("wl_cp1252")] if kodierung == "cp1252" else [])
    raise WortlisteFehler("wl_unlesbar")


def _wl_bereinigen(text):
    """Stufe 3: NFC (macOS liefert NFD), alle Zeilenenden → \\n, Nullbreiten/weiches Trennzeichen weg, besondere
    Leerzeichen → Leerzeichen, Steuerzeichen außer Tab weg."""
    for alt in ("\r\n", "\r", " ", " ", "\x85"):
        text = text.replace(alt, "\n")
    text = text.translate(_WL_NULLBREITE)
    aus = []
    for c in text:
        kat = unicodedata.category(c)
        if c in "\t\n":
            aus.append(c)
        elif kat == "Zs":
            aus.append(" ")
        elif kat != "Cc":
            aus.append(c)
    return unicodedata.normalize("NFC", "".join(aus))


def _wl_feld(wert):
    """Stufe 8: trimmen, Leerraum zusammenfassen, typografische Anführungszeichen außen weg (/ und | bleiben)."""
    t = " ".join(_wl_bereinigen(str(wert or "")).split())
    while len(t) >= 2 and t[0] in _WL_ANFUEHRUNG and t[-1] in _WL_ANFUEHRUNG:
        t = t[1:-1].strip()
    return t


def _wl_trenner_waehlen(zeilen):
    """Stufe 5 (auto): Tab > ; > „ = “ > „ – “/„ - “ > , – das erste Zeichen, das in ≥ 60 % der Zeilen steht."""
    pruefen = (("tab", lambda z: "\t" in z), ("semikolon", lambda z: ";" in z), ("gleich", lambda z: " = " in z),
               ("strich", lambda z: bool(_WL_STRICH.search(z))), ("komma", lambda z: "," in z))
    for name, hat in pruefen:
        if zeilen and sum(1 for z in zeilen if hat(z)) >= 0.6 * len(zeilen):
            return name
    return "keiner"


def _wl_zellen(zeile, trenner):
    import csv
    if trenner in ("tab", "semikolon", "komma"):
        zeichen = {"tab": "\t", "semikolon": ";", "komma": ","}[trenner]
        try:
            zellen = next(csv.reader([zeile], delimiter=zeichen, skipinitialspace=True), [])
        except csv.Error:
            zellen = zeile.split(zeichen)
    elif trenner == "gleich":
        zellen = re.split(r"\s*=\s*", zeile, maxsplit=1)
    elif trenner == "strich":
        zellen = _WL_STRICH.split(zeile, maxsplit=1)
    else:
        zellen = [zeile]
    zellen = [_wl_feld(z) for z in zellen]
    while len(zellen) > 1 and not zellen[-1]:                       # „alt;viejo;;“
        zellen.pop()
    return zellen


def _wl_name(t):
    t = "".join(c for c in unicodedata.normalize("NFKD", str(t).casefold()) if not unicodedata.combining(c))
    return re.sub(r"[\W_]+", "", t)


def _wl_kopf_rolle(zelle):
    """Stufe 6: Rolle einer Kopfzelle → "de" | "notiz" | ("zs", Code oder None) | None (kein bekannter Name)."""
    n = _wl_name(zelle)
    if not n:
        return None
    if n in _WL_DE_NAMEN:
        return "de"
    if n in _WL_NOTIZ_NAMEN:
        return "notiz"
    if n in _WL_ZS_NAMEN:
        return ("zs", None)
    try:
        import sprachen
        katalog = sprachen.SPRACHEN
    except ImportError:
        katalog = {"es": dict(name=L("Spanisch", "Spanish", "español"), eigenname="español")}
    for code, s in katalog.items():
        namen = {_wl_name(v) for v in s["name"].values()} | {_wl_name(s.get("eigenname", "")), _wl_name(code)}
        if n in namen:
            return ("zs", code)
    if n in ("mexikanisch", "mexican", "mexicano"):
        return ("zs", "es")
    return None


def wort_schluessel_zs(text, code="es"):
    """Vergleichsschlüssel eines Worts der Kartensprache: lateinische Sprachen wie wort_schluessel(…, True), andere
    Schriften NFKC + casefold ohne Satzzeichen/Symbole (sonst wären alle japanischen/russischen Wörter „leer“)."""
    try:
        import sprachen
        schrift = sprachen.SPRACHEN.get(code, {}).get("schrift", "latein")
    except ImportError:
        schrift = "latein"
    if schrift == "latein":
        return wort_schluessel(text, True)
    t = unicodedata.normalize("NFKC", str(text or "").split("/")[0].replace("|", " ")).casefold()
    t = "".join(c if not unicodedata.category(c).startswith(("P", "S")) else " " for c in t)
    return " ".join(t.split())


def _wl_pruefe(de, wort, notiz, zs, roh_de=None):
    """Stufe 10: Prüfen je Zeile (auch beim Anlegen). → (Fehlertext oder None, Hinweise)."""
    import uebersetzer
    zs_text = gl.zs_name(code=zs)
    if _formel(roh_de if roh_de is not None else de, de, wort, notiz):
        return gl.pm("k_formel", "fehler")["text"], []
    for feld, wert, name in (("de", de, gl.text_in(L("Deutsch", "German", "Alemán"))), ("wort", wort, zs_text),
                             ("notiz", notiz, gl.text_in(L("Notiz", "Note", "Nota")))):
        if len(wert) > WL_LAENGE[feld]:
            return tx("wl_lang", feld=name, n=len(wert), max=WL_LAENGE[feld]), []
    if not (de or wort):
        return tx("idee_leer", zs=zs_text), []
    if de and _WL_GANS.sub("", de) == "":
        return tx("wl_nur_gans"), []
    if de and not any(c.isalpha() for c in _WL_GANS.sub("", de)):
        return tx("wl_keine_buchstaben"), []
    hinweise = []
    if wort:
        ohne = re.sub(r"[/|;:]", " ", wort)
        if not uebersetzer.erlaubt(zs).fullmatch(ohne):
            hinweise.append(tx("wl_zeichen", zs=zs_text))
        fremd = sorted({c for c in wort if c in "äöÄÖß"})
        if zs == "es" and fremd:
            hinweise.append(gl.pm("k_umlaut", "warnung", zeichen=" ".join(fremd))["text"])
    return None, hinweise


def _wl_vorhanden_schluessel(vorhanden, zs):
    """Schlüssel der vorhandenen Ideen und Karten (Deutsch + Wort der Kartensprache) → {schlüssel: Eintrag}."""
    ideen, karten = {}, {}
    for i in vorhanden.get("ideen") or []:
        for s in (("de", wort_schluessel(i.get("de"))), ("zs", wort_schluessel_zs(i.get("es"), zs))):
            if s[1]:
                ideen.setdefault(s, i)
    for k in vorhanden.get("karten") or []:
        for s in (("de", wort_schluessel(k.get("de"))), ("zs", wort_schluessel_zs(k.get("es"), zs))):
            if s[1]:
                karten.setdefault(s, k)
    return ideen, karten


def _wl_doppelt(z, zs, ideen, karten, liste):
    """Stufe 11: Status doppelt_liste | idee_da | karte_da (nicht vorausgewählt, aber wählbar) – merkt die Zeile in
    liste ({schlüssel: Zeile}), damit spätere Zeilen sie finden."""
    schluessel = [s for s in (("de", wort_schluessel(z["de"])), ("zs", wort_schluessel_zs(z["wort"], zs))) if s[1]]
    karte = next((karten[s] for s in schluessel if s in karten), None)
    idee = next((ideen[s] for s in schluessel if s in ideen), None)
    frueher = next((liste[s] for s in schluessel if s in liste), None)
    for s in schluessel:
        liste.setdefault(s, z)
    if karte is not None:
        z.update(status="karte_da", text=tx("i_idee_als_karte", nr=karte.get("nr") or "–", bild=karte.get("bild", "")))
    elif idee is not None:
        z.update(status="idee_da", text=tx("wl_idee_da"))
    elif frueher is not None:
        anders = frueher["wort"] if frueher["wort"] and wort_schluessel_zs(frueher["wort"], zs) \
            != wort_schluessel_zs(z["wort"], zs) else ""
        z.update(status="doppelt_liste", text=tx("wl_doppelt_anders", nr=frueher["nr"], wort=anders) if anders
                 else tx("wl_doppelt", nr=frueher["nr"]))
    return z


def wortliste_lesen(roh: bytes, optionen=None):
    """Wortliste (Datei-Bytes oder eingefügter Text als UTF-8) → dict(zeilen, erkannt, hinweise, zahlen, zs).
    optionen: trenner (WL_TRENNER), kopf (auto|ja|nein), tauschen, einspaltig (de|zs), gans (Standard an), zs
    (Kartensprache), vorhanden={ideen, karten} für die Doppelt-Prüfung. Ganze Liste unbrauchbar → WortlisteFehler."""
    o = dict(optionen or {})
    zs = o.get("zs") or "es"
    zs_text = gl.zs_name(code=zs)
    roh = bytes(roh or b"")
    if len(roh) > WL_MAX_BYTES:
        raise WortlisteFehler("wl_gross", mb=WL_MAX_BYTES // (1024 * 1024))
    if not roh.strip():
        raise WortlisteFehler("wl_leer")
    art = _wl_dateiart(roh)
    if art:
        raise WortlisteFehler("wl_dateiart", art=art)
    text, kodierung, hinweise = _wl_dekodieren(roh)
    text = _wl_bereinigen(text)
    kommentare = leer = 0
    inhalt = []                                                    # (Zeilennummer der Datei, Text)
    for nr, zeile in enumerate(text.split("\n"), 1):
        zeile = zeile.strip(" ")
        if not zeile.strip():
            leer += 1
        elif zeile.lstrip().startswith("#"):
            kommentare += 1
        else:
            inhalt.append((nr, _WL_LISTENZEICHEN.sub("", zeile.strip())))
    if not inhalt:
        raise WortlisteFehler("wl_leer")
    trenner = o.get("trenner") if o.get("trenner") in WL_TRENNER else "auto"
    if trenner == "auto":
        trenner = _wl_trenner_waehlen([z for _, z in inhalt])
    zellen = [(nr, _wl_zellen(z, trenner)) for nr, z in inhalt]
    # Kopfzeile
    kopf_wahl = o.get("kopf") if o.get("kopf") in ("ja", "nein") else "auto"
    rollen = [_wl_kopf_rolle(c) for c in zellen[0][1]]
    ist_kopf = kopf_wahl == "ja" or (kopf_wahl == "auto" and all(rollen) and any(zellen[0][1]))
    einspaltig = "zs" if o.get("einspaltig") == "zs" else "de"
    ordnung, kopf_sprache = None, None
    if ist_kopf:
        zellen = zellen[1:]
        if all(rollen):
            ordnung = ["de" if r == "de" else "notiz" if r == "notiz" else "wort" for r in rollen]
            if len(set(ordnung)) != len(ordnung):
                ordnung = None
            codes = [r[1] for r in rollen if isinstance(r, tuple) and r[1]]
            if codes and codes[0] != zs:
                kopf_sprache = codes[0]
        if not zellen:
            raise WortlisteFehler("wl_nur_kopf")
    if len(zellen) > WL_MAX_ZEILEN:
        raise WortlisteFehler("wl_zu_viele", n=len(zellen), max=WL_MAX_ZEILEN)
    getauscht = bool(ordnung and "wort" in ordnung and "de" in ordnung and ordnung.index("wort") < ordnung.index("de"))
    if kopf_sprache:
        hinweise.append(tx("wl_kopf_sprache", sprache=gl.zs_name(code=kopf_sprache), zs=zs_text))
    tauschen = str(o.get("tauschen") or "") in ("1", "true", "ja")
    gans = str(o.get("gans", "1")) not in ("0", "false", "nein")
    ideen, karten = _wl_vorhanden_schluessel(o.get("vorhanden") or {}, zs)
    liste, zeilen, komma3 = {}, [], 0
    for nr, c in zellen:
        z = dict(nr=nr, roh=" | ".join(c)[:300], de="", wort="", notiz="", status="neu", text=tx("wl_neu"),
                 hinweise=[], wahl=True)
        if len(c) > 3:
            z.update(status="fehler", text=tx("wl_spalten", n=len(c), zs=zs_text), wahl=False)
            zeilen.append(z)
            continue
        if trenner == "komma" and len(c) == 3:
            komma3 += 1
        if ordnung:
            felder = ordnung + [f for f in ("de", "wort", "notiz") if f not in ordnung]
        else:
            felder = ["de" if einspaltig == "de" else "wort"] if len(c) == 1 else ["de", "wort", "notiz"]
        werte = dict(zip(felder, c))
        if tauschen:
            werte["de"], werte["wort"] = werte.get("wort", ""), werte.get("de", "")
        roh_de = werte.get("de", "")
        de = roh_de
        if gans and de and (_WL_GANS.match(de) or not gl.hat_gans(de)):     # „Die Gans ist alt“ bleibt so (seit 2.4)
            de = _WL_GANS.sub("", de)
            de = f"Gans {de}" if de else "Gans"
        z.update(de=de, wort=werte.get("wort", ""), notiz=werte.get("notiz", ""))
        fehler, z["hinweise"] = _wl_pruefe(z["de"], z["wort"], z["notiz"], zs, roh_de)
        if fehler:
            z.update(status="fehler", text=fehler, wahl=False)
        else:
            _wl_doppelt(z, zs, ideen, karten, liste)
            z["wahl"] = z["status"] == "neu"
        zeilen.append(z)
    if komma3:
        hinweise.append(tx("wl_komma_alt"))
    zahlen = dict(zeilen=len(zeilen), neu=sum(1 for z in zeilen if z["status"] == "neu"),
                  doppelt=sum(1 for z in zeilen if z["status"] in ("doppelt_liste", "idee_da", "karte_da")),
                  fehler=sum(1 for z in zeilen if z["status"] == "fehler"),
                  hinweise=sum(1 for z in zeilen if z["hinweise"]), kommentare=kommentare, leer=leer)
    erkannt = dict(kodierung=kodierung, trenner=trenner, kopf=ist_kopf, getauscht=getauscht, tauschen=tauschen,
                   einspaltig=einspaltig, gans=gans, kopf_sprache=kopf_sprache)
    return dict(zeilen=zeilen, erkannt=erkannt, hinweise=hinweise, zahlen=zahlen, zs=zs, zs_name=zs_text)


def _wl_vorhanden():
    return dict(ideen=_ideen_lesen()["ideen"], karten=UI.karten_daten()["karten"])


def wortliste_pruefen(roh: bytes, q):
    eins = lambda k, d="": (q.get(k) or [d])[0]                     # noqa: E731
    optionen = {k: eins(k) for k in ("trenner", "kopf", "tauschen", "einspaltig") if eins(k)}
    optionen.update(gans=eins("gans", "1"), zs=UI.zielsprache(), vorhanden=_wl_vorhanden())
    return wortliste_lesen(roh, optionen)


def _wl_fingerabdruck(i):
    teile = [i.get("de", ""), i.get("es", ""), i.get("notiz", ""), i.get("bild", "")]
    if i.get("bild_idee"):                         # eigene Bildidee = von Hand geändert (ohne sie: Wert wie vor 2.3)
        teile.append(i["bild_idee"])
    roh = json.dumps(teile, ensure_ascii=False)
    return hashlib.sha1(roh.encode("utf-8")).hexdigest()[:16]


def wortliste_uebernehmen(daten):
    """Ausgewählte Zeilen als Ideen anlegen – zustandslos: jede Zeile wird erneut geprüft (Stufe 10–11, gegen den
    Stand jetzt), alles in einem Schreibvorgang unter _ideen_lock. Kartensprache gewechselt → 409."""
    zs = UI.zielsprache()
    if daten.get("zs") != zs:
        e = UI.Meldung("ungueltig", status=409, extra={"code": "zs_geaendert"})
        e.args = (tx("wl_zs_geaendert"),)
        raise e
    roh_zeilen = daten.get("zeilen")
    if not isinstance(roh_zeilen, list) or len(roh_zeilen) > WL_MAX_ZEILEN \
            or not all(isinstance(z, dict) for z in roh_zeilen):
        raise UI.Meldung("ungueltig")
    if not roh_zeilen:
        raise ValueError(tx("wl_nichts"))
    angelegt, uebersprungen = [], []
    with _ideen_lock:
        d = _ideen_lesen()
        ideen, karten = _wl_vorhanden_schluessel(dict(ideen=d["ideen"], karten=UI.karten_daten()["karten"]), zs)
        liste, wl, jetzt = {}, secrets.token_hex(6), time.time()
        for n, r in enumerate(roh_zeilen):
            nr = r.get("nr") if isinstance(r.get("nr"), int) else n + 1
            z = dict(nr=nr, de=_wl_feld(r.get("de")), wort=_wl_feld(r.get("wort")), notiz=_wl_feld(r.get("notiz")),
                     status="neu")
            fehler, _ = _wl_pruefe(z["de"], z["wort"], z["notiz"], zs)
            if not fehler:
                _wl_doppelt(z, zs, ideen, karten, liste)
            if fehler or z["status"] != "neu":
                uebersprungen.append(dict(nr=nr, de=z["de"], wort=z["wort"], status=z["status"] if not fehler else "fehler",
                                          text=fehler or z["text"]))
                continue
            i = dict(id=secrets.token_hex(6), zeit=jetzt - len(angelegt) * 0.001, bild="", de=z["de"], es=z["wort"],
                     notiz=z["notiz"], es_auto="", wl=wl)
            i["fp"] = _wl_fingerabdruck(i)
            angelegt.append(i)
        if angelegt:
            d["ideen"][0:0] = angelegt                           # Reihenfolge wie in der Liste, ganz oben
            d.setdefault("wortlisten", []).insert(0, dict(wl=wl, n=len(angelegt), zeit=jetzt))
            d["wortlisten"] = d["wortlisten"][:20]
            _ideen_schreiben(d)
    return dict(angelegt=len(angelegt), uebersprungen=uebersprungen, wl=wl if angelegt else "", **ideen_liste())


def wortliste_rueckgaengig(daten):
    """Entfernt nur unveränderte Ideen dieser Wortliste (Fingerabdruck gleich, kein Bild); geänderte bleiben stehen,
    inzwischen als Karte aufgenommene zählen als „schon Karte“."""
    wl = str(daten.get("wl") or "")
    if not re.fullmatch(r"[0-9a-f]{12}", wl):
        raise UI.Meldung("ungueltig")
    with _ideen_lock:
        d = _ideen_lesen()
        eintrag = next((w for w in d.get("wortlisten", []) if w.get("wl") == wl), None)
        eigene = [i for i in d["ideen"] if i.get("wl") == wl]
        if eintrag is None and not eigene:
            raise ValueError(tx("wl_rueck_fehlt"))
        weg = [i for i in eigene if not i.get("bild") and i.get("fp") == _wl_fingerabdruck(i)]
        geblieben = len(eigene) - len(weg)
        schon_karte = max(0, int((eintrag or {}).get("n", 0)) - len(eigene))
        ids = {i["id"] for i in weg}
        d["ideen"] = [i for i in d["ideen"] if i.get("id") not in ids]
        if not geblieben:
            d["wortlisten"] = [w for w in d.get("wortlisten", []) if w.get("wl") != wl]
        elif eintrag is not None:
            eintrag["n"] = geblieben
        _ideen_schreiben(d)
    return dict(entfernt=len(weg), geaendert=geblieben, schon_karte=schon_karte, **ideen_liste())


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
                   "hochzuladen. Nur fürs eigene Heimnetz (Verbindung unverschlüsselt, nie in öffentlichen WLANs), Zugang nur mit "
                   "PIN, schaltet sich nach 2 Stunden von selbst ab. Oder die Gans als App "
                   "aufs Handy holen (QR-Code).",
                   "Use the interface on your phone or tablet in your own Wi-Fi – e.g. to upload photos straight from "
                   "your phone. Only for your own home network (the connection is unencrypted – never in public Wi-Fi); "
                   "access only with a PIN; switches itself off after 2 hours. Or get the goose onto your "
                   "phone as an app (QR code).",
                   "Usa la interfaz en el celular o la tableta dentro de tu wifi, p. ej. para subir fotos directo del "
                   "celular. Solo para tu propia red de casa (la conexión no va cifrada; nunca en wifi públicas); acceso "
                   "solo con PIN; se apaga solo después de 2 horas. O llévate el ganso al celular como "
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
LAN_GESPERRT = {"/api/deinstallieren", "/api/beenden", "/api/oeffnen", "/api/lan", "/api/start-einstellung",
                "/api/neue-version", "/api/update"}


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


ROH_WEGE = ("/api/import", "/api/idee-bild", "/api/wortliste-pruefen")


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
    if weg == "/api/wortliste-pruefen":
        if n > WL_MAX_BYTES:
            raise WortlisteFehler("wl_gross", mb=WL_MAX_BYTES // (1024 * 1024))
        h._senden(200, wortliste_pruefen(h.rfile.read(n) if n > 0 else b"", q))
        return True
    return False


POST_WEGE = {
    "/api/import-pruefen": lambda d: import_pruefen(d.get("id")),
    "/api/import-uebernehmen": import_uebernehmen,
    "/api/import-verwerfen": import_verwerfen,
    "/api/idee": idee_speichern,
    "/api/idee-wort": idee_wort_fuellen,
    "/api/idee-weg": idee_weg,
    "/api/idee-zurueck": idee_zurueck,
    "/api/idee-aufnehmen": idee_aufnehmen,
    "/api/wortliste-uebernehmen": wortliste_uebernehmen,
    "/api/wortliste-rueckgaengig": wortliste_rueckgaengig,
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
