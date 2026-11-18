#!/usr/bin/env python3
"""Me Goos-ta Deutsch – Tool „Eigene Stimme“ (seit 2.6): eigene Audiodateien je Wort.

Ablage: <Projektordner>/stimmen/<sprache>/<schlüssel>.<endung> – sprache = "de" oder ein Code aus sprachen.SPRACHEN,
schlüssel = die ersten 16 Hex-Zeichen von SHA-256 über den normalisierten Text (NFC, Leerraum einfach, casefold).
Eine Datei je Schlüssel (eine neue ersetzt die alte, auch bei anderer Endung). Kein Index: die Ordner sind die Wahrheit.

Sicherheit: Dateien werden nie über einen Pfad aus einer Anfrage gelesen oder geschrieben, nur über Sprache (gegen den
Katalog) und Schlüssel (^[0-9a-f]{16}$). Angenommen wird nur, was die Kennbytes seines Formats trägt und höchstens
2 MB groß ist; WAV wird zusätzlich mit `wave` geöffnet (PCM, höchstens 15 s) und neu geschrieben. Nichts wird
umgewandelt (kein Codec im Programm).

Nur Standardbibliothek, keine Threads, kein Unterprozess – läuft so auch in der Handy-App (Pyodide)."""
import csv
import hashlib
import io
import re
import unicodedata
import wave
import zipfile
from pathlib import Path

try:
    import sprachen
except ImportError:                                      # Testkopie ohne sprachen.py: Deutsch + Spanisch
    sprachen = None

ORDNER_NAME = "stimmen"
ENDUNGEN = ("wav", "mp3", "ogg", "opus", "m4a", "webm")
MIME = {"wav": "audio/wav", "mp3": "audio/mpeg", "ogg": "audio/ogg", "opus": "audio/ogg", "m4a": "audio/mp4",
        "webm": "audio/webm"}
MAX_DATEI = 2 * 1024 * 1024                              # je Audiodatei
MAX_SEKUNDEN = 15                                        # WAV (bei den anderen Formaten begrenzt die Größe)
MAX_ZIP = 200 * 1024 * 1024                              # ZIP beim Einlesen (gepackt)
MAX_ZIP_DATEIEN = 20000
SCHLUESSEL_MUSTER = re.compile(r"[0-9a-f]{16}")
WORTLISTE_KOPF = ("datei", "sprache", "text", "vorhanden")


class StimmenFehler(ValueError):
    """Verständlicher Fehler mit Code: endung, gross, leer, kennbytes, wav, lang, zip, zip_gross, sprache, schluessel."""

    def __init__(self, code):
        super().__init__(code)
        self.code = code


# ---------- Schlüssel, Sprache, Ordner ----------
def normalisiere(text):
    """Gleicher Text → gleicher Schlüssel: NFC, Leerraum außen weg und innen einfach, Groß-/Kleinschreibung egal."""
    s = unicodedata.normalize("NFC", str(text or ""))
    s = " ".join(s.split()).casefold()
    return unicodedata.normalize("NFC", s)


def schluessel(text):
    """Die ersten 16 Hex-Zeichen von SHA-256 über den normalisierten Text; leerer Text → ""."""
    s = normalisiere(text)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16] if s else ""


def sprache_ok(code):
    if code == "de":
        return True
    return isinstance(code, str) and (code in sprachen.SPRACHEN if sprachen else code == "es")


def schluessel_ok(s):
    return isinstance(s, str) and SCHLUESSEL_MUSTER.fullmatch(s) is not None


def ordner(projekt):
    return Path(projekt) / ORDNER_NAME


def name_ok(name):
    """<16 hex>.<endung> – so heißen die Dateien dieses Tools."""
    stamm, _, endung = str(name or "").rpartition(".")
    return endung in ENDUNGEN and schluessel_ok(stamm)


def _eigene(datei):
    """Ist das eine Datei dieses Tools? (Name <16 hex>.<endung>, kein Link)"""
    return name_ok(datei.name) and datei.is_file() and not datei.is_symlink()


def _sprach_ordner(projekt):
    basis = ordner(projekt)
    if not basis.is_dir() or basis.is_symlink():
        return []
    return [p for p in sorted(basis.iterdir()) if p.is_dir() and not p.is_symlink() and sprache_ok(p.name)]


def dateien(projekt):
    """Alle Audiodateien des Tools (nur die eigenen Namen in stimmen/<sprache>/) – für Deinstallieren und Sicherung."""
    return [p for o in _sprach_ordner(projekt) for p in sorted(o.iterdir()) if _eigene(p)]


def liste(projekt):
    """{sprache: {schlüssel: endung}} – was gerade da ist."""
    aus = {}
    for p in dateien(projekt):
        aus.setdefault(p.parent.name, {})[p.stem] = p.suffix[1:]
    return aus


def belegt(projekt):
    summe = 0
    for p in dateien(projekt):
        try:
            summe += p.stat().st_size
        except OSError:
            pass
    return summe


def pfad(projekt, sprache, schl):
    """Die Datei zu Sprache + Schlüssel oder None. Beide werden geprüft – nie ein Pfad aus der Anfrage."""
    if not sprache_ok(sprache) or not schluessel_ok(schl):
        return None
    basis = ordner(projekt) / sprache
    for e in ENDUNGEN:
        p = basis / f"{schl}.{e}"
        if p.is_file() and not p.is_symlink():
            return p
    return None


# ---------- Annahme ----------
def _art(daten):
    """Format nach den Kennbytes: wav, mp3, ogg (auch Opus), m4a, webm – oder None."""
    k = bytes(daten[:12])
    if len(k) >= 12 and k[:4] == b"RIFF" and k[8:12] == b"WAVE":
        return "wav"
    if k[:4] == b"OggS":
        return "ogg"
    if len(k) >= 8 and k[4:8] == b"ftyp":
        return "m4a"
    if k[:4] == b"\x1a\x45\xdf\xa3":
        return "webm"
    if k[:3] == b"ID3" or (len(k) >= 2 and k[0] == 0xFF and k[1] & 0xE0 == 0xE0 and k[1] & 0x06 != 0):
        return "mp3"
    return None


def _wav_neu(daten):
    """WAV öffnen (nur PCM, 1–2 Kanäle, höchstens MAX_SEKUNDEN) und frisch schreiben – ohne fremde Zusatzblöcke."""
    try:
        with wave.open(io.BytesIO(daten), "rb") as w:
            kan, breite, rate, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
            if w.getcomptype() != "NONE" or kan not in (1, 2) or breite not in (1, 2, 3, 4) or not 4000 <= rate <= 192000:
                raise StimmenFehler("wav")
            if n <= 0:
                raise StimmenFehler("leer")
            if n > rate * MAX_SEKUNDEN:
                raise StimmenFehler("lang")
            roh = w.readframes(n)
    except StimmenFehler:
        raise
    except Exception:                                    # noqa: BLE001 – wave wirft bei kaputten Dateien Verschiedenes
        raise StimmenFehler("wav") from None
    roh = roh[:len(roh) - len(roh) % (kan * breite)]
    if not roh:
        raise StimmenFehler("leer")
    aus = io.BytesIO()
    with wave.open(aus, "wb") as w:
        w.setnchannels(kan)
        w.setsampwidth(breite)
        w.setframerate(rate)
        w.writeframes(roh)
    return aus.getvalue()


def pruefe(daten, name):
    """Audiodatei prüfen → (endung, bytes). Endung aus dem Namen, muss zu den Kennbytes passen; WAV kommt neu
    geschrieben zurück. Sonst StimmenFehler(code)."""
    endung = str(name or "").rsplit(".", 1)[-1].lower() if "." in str(name or "") else ""
    if endung not in ENDUNGEN:
        raise StimmenFehler("endung")
    daten = bytes(daten or b"")
    if not daten:
        raise StimmenFehler("leer")
    if len(daten) > MAX_DATEI:
        raise StimmenFehler("gross")
    art = _art(daten)
    if art is None or art != ("ogg" if endung == "opus" else endung):
        raise StimmenFehler("kennbytes")
    if art == "wav":
        daten = _wav_neu(daten)
        if len(daten) > MAX_DATEI:
            raise StimmenFehler("gross")
    return endung, daten


def speichere(projekt, sprache, schl, daten, name, sichere=None):
    """Geprüfte Datei ablegen → "neu" | "ersetzt". Eine vorhandene Datei desselben Schlüssels (auch mit anderer
    Endung) wird ersetzt; sichere(pfad) wird vor jedem Löschen/Überschreiben gerufen (Rückgängig)."""
    if not sprache_ok(sprache):
        raise StimmenFehler("sprache")
    if not schluessel_ok(schl):
        raise StimmenFehler("schluessel")
    endung, inhalt = pruefe(daten, name)
    basis = ordner(projekt) / sprache
    basis.mkdir(parents=True, exist_ok=True)
    ersetzt = False
    for e in ENDUNGEN:
        alt = basis / f"{schl}.{e}"
        if alt.is_file() or alt.is_symlink():
            ersetzt = True
            if sichere:
                sichere(alt)
            alt.unlink()
    (basis / f"{schl}.{endung}").write_bytes(inhalt)
    return "ersetzt" if ersetzt else "neu"


def loesche(projekt, sprache, schl, sichere=None):
    """Die Datei zu Sprache + Schlüssel löschen → True, wenn es eine gab."""
    p = pfad(projekt, sprache, schl)
    if p is None:
        return False
    if sichere:
        sichere(p)
    p.unlink()
    _leere_ordner_weg(projekt)
    return True


def _leere_ordner_weg(projekt):
    for o in _sprach_ordner(projekt) + [ordner(projekt)]:
        try:
            o.rmdir()                                    # nur, wenn leer (nie rekursiv)
        except OSError:
            pass


def loesche_alles(projekt):
    """Deinstallieren: nur die eigenen Audiodateien in stimmen/<sprache>/ und danach leere Ordner → [Pfade]."""
    weg = []
    for p in dateien(projekt):
        p.unlink()
        weg.append(p)
    _leere_ordner_weg(projekt)
    return weg


# ---------- Wortliste ----------
def woerter(karten, zielsprache=None):
    """Alle Texte, die vorgelesen werden: [(sprache, schlüssel, text)] – Deutsch und Kartensprache jeder Karte, in
    Kartenreihenfolge, ohne Doppelte. Ohne zielsprache: jede Sprache, in der die Karte ein Wort hat.
    karten: [{de, rueckseiten: {code: text}}] (wie gans_ui._lern_karten)."""
    aus, gesehen = [], set()
    for k in karten or []:
        rueck = k.get("rueckseiten") if isinstance(k.get("rueckseiten"), dict) else {}
        codes = [zielsprache] if zielsprache else sorted(rueck)
        paare = [("de", k.get("de"))] + [(c, rueck.get(c)) for c in codes if c != "de" and sprache_ok(c)]
        for code, text in paare:
            text = " ".join(str(text or "").split())
            schl = schluessel(text)
            if schl and (code, schl) not in gesehen:
                gesehen.add((code, schl))
                aus.append((code, schl, text))
    return aus


def gewuenscht(karten):
    """{sprache: {schlüssel}} aller Wörter der Karten (jede Sprache) – Grundlage für Einlesen und Aufräumen."""
    aus = {}
    for code, schl, _ in woerter(karten):
        aus.setdefault(code, set()).add(schl)
    return aus


def wortliste(karten, zielsprache, da=None):
    """Zeilen (datei, sprache, text, vorhanden) – datei = <sprache>/<schlüssel> ohne Endung, vorhanden ja/nein."""
    da = da or {}
    return [(f"{code}/{schl}", code, text, "ja" if schl in da.get(code, {}) else "nein")
            for code, schl, text in woerter(karten, zielsprache)]


def wortliste_csv(zeilen):
    """CSV mit Semikolon, UTF-8 mit BOM (öffnet in Tabellenprogrammen richtig). Texte, die wie eine Formel beginnen,
    bekommen ein Hochkomma davor."""
    puffer = io.StringIO()
    w = csv.writer(puffer, delimiter=";", lineterminator="\r\n")
    w.writerow(WORTLISTE_KOPF)
    for datei, code, text, vorhanden in zeilen:
        w.writerow((datei, code, ("'" + text) if text[:1] in "=+-@\t\r" else text, vorhanden))
    return b"\xef\xbb\xbf" + puffer.getvalue().encode("utf-8")


# ---------- Einlesen ----------
def aus_zip(roh):
    """ZIP → [(name, bytes | None)] (None = Eintrag zu groß). Wie beim Update: kein Pfad nach außen, Obergrenzen;
    Ordner, Punkt-Dateien und __MACOSX werden übersprungen. Sonst StimmenFehler("zip" | "zip_gross")."""
    roh = bytes(roh or b"")
    if len(roh) > MAX_ZIP:
        raise StimmenFehler("zip_gross")
    try:
        z = zipfile.ZipFile(io.BytesIO(roh))
        infos = z.infolist()
    except Exception:                                    # noqa: BLE001 – kaputte ZIPs werfen Verschiedenes
        raise StimmenFehler("zip") from None
    if len(infos) > MAX_ZIP_DATEIEN:
        raise StimmenFehler("zip_gross")
    aus = []
    with z:
        for i in infos:
            name = i.filename
            teile = name.split("/")
            if (name.startswith("/") or "\\" in name or ":" in name or "\x00" in name
                    or any(t in (".", "..") for t in teile)):
                raise StimmenFehler("zip")
            if i.is_dir() or not teile[-1] or teile[-1].startswith(".") or "__MACOSX" in teile:
                continue
            if i.file_size > MAX_DATEI:
                aus.append((name, None))
                continue
            try:
                with z.open(i) as f:
                    daten = f.read(MAX_DATEI + 1)
            except Exception:                            # noqa: BLE001 – CRC, Verschlüsselung, unbekannte Packart
                raise StimmenFehler("zip") from None
            aus.append((name, daten if len(daten) <= MAX_DATEI else None))
    return aus


def _zuordnung(name, erlaubt):
    """Dateiname → (sprache, schlüssel) oder None: Name ohne Endung = Schlüssel, Ordner darüber = Sprache. Ohne
    Ordner zählt die Sprache, in deren Wortliste der Schlüssel als einziger steht."""
    teile = [t for t in str(name or "").replace("\\", "/").split("/") if t]
    if not teile:
        return None
    schl = teile[-1].rsplit(".", 1)[0].lower()
    if not schluessel_ok(schl):
        return None
    code = teile[-2].lower() if len(teile) >= 2 else ""
    if not sprache_ok(code):
        treffer = [c for c, menge in erlaubt.items() if schl in menge]
        if len(treffer) != 1:
            return None
        code = treffer[0]
    return (code, schl) if schl in erlaubt.get(code, ()) else None


def importiere(projekt, quelle, erlaubt, sichere=None):
    """Audiodateien einlesen. quelle: ZIP als Bytes oder [(name, bytes)]; erlaubt: {sprache: {schlüssel}} der
    Wortliste. → {neu, ersetzt, unbekannt, abgelehnt} (Zahlen) + gruende {code: n}. Vorhandene Dateien werden ersetzt."""
    eintraege = aus_zip(quelle) if isinstance(quelle, (bytes, bytearray)) else list(quelle or [])
    erg = dict(neu=0, ersetzt=0, unbekannt=0, abgelehnt=0, gruende={})

    def ablehnen(code):
        erg["abgelehnt"] += 1
        erg["gruende"][code] = erg["gruende"].get(code, 0) + 1

    for name, daten in eintraege:
        ziel = _zuordnung(name, erlaubt or {})
        if ziel is None:
            erg["unbekannt"] += 1
            continue
        if daten is None:
            ablehnen("gross")
            continue
        try:
            erg[speichere(projekt, ziel[0], ziel[1], daten, str(name), sichere)] += 1
        except StimmenFehler as e:
            ablehnen(e.code)
    return erg


def aufraeumen(projekt, erlaubt, sichere=None):
    """Verwaiste Dateien löschen (kein Wort der Wortliste gehört mehr dazu) → Anzahl."""
    n = 0
    for p in dateien(projekt):
        if p.stem not in (erlaubt or {}).get(p.parent.name, ()):
            if sichere:
                sichere(p)
            p.unlink()
            n += 1
    _leere_ordner_weg(projekt)
    return n


if __name__ == "__main__":
    import sys
    for wort in sys.argv[1:]:
        print(schluessel(wort), wort)
