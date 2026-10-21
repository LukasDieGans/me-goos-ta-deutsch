#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ME GOOS-TA DEUTSCH – Automatische Übersetzung (Vorschläge)            Version 2.2 (21.10.2026)
=============================================================================================
Schlägt für den Text einer Karte das Wort auf Spanisch vor (Deutsch → Spanisch, wie in Mexiko gesprochen) – bzw.
in der gewählten Zielsprache (sprachen.py: 15 Sprachen, Dienst-Codes im Katalog; richtung="de-<code>" / "<code>-de").
Es ist immer nur ein VORSCHLAG: Er wird erst gespeichert, wenn du ihn übernimmst, und bleibt in der
Kartenliste als „automatisch übersetzt“ markiert, bis du ihn im Reiter „Tabelle“ als geprüft abhakst.

Dienste (fest eingetragen, keine frei wählbare Adresse):
  wiktionary  de.wiktionary.org            freies Wörterbuch, ohne Konto – beste Wahl für einzelne Wörter
  mymemory    api.mymemory.translated.net  maschinelle Übersetzung, ohne Konto (ca. 5000 Zeichen am Tag)
  deepl       api-free.deepl.com           maschinelle Übersetzung (lateinamerik. Spanisch), eigener kostenloser
              bzw. api.deepl.com           API-Schlüssel nötig
  „auto“: einzelne Wörter zuerst im Wörterbuch, sonst DeepL (wenn ein Schlüssel hinterlegt ist) bzw. MyMemory.

Sicherheit und Datenschutz:
  • Nur auf Wunsch: Ohne ausdrückliche Zustimmung in der Oberfläche wird nichts gesendet; jederzeit abschaltbar.
  • Datensparsam: gesendet wird nur das zu übersetzende Wort bzw. die Wendung (ohne das vorangestellte „Gans“) –
    keine Bilder, keine Dateinamen, keine E-Mail-Adresse, keine Cookies; neutraler User-Agent. Texte, die wie eine
    E-Mail- oder Internetadresse aussehen, werden gar nicht erst gesendet.
  • Nur HTTPS mit Zertifikatsprüfung, nur zu den oben genannten Adressen, keine Weiterleitungen, kurze Zeitlimits,
    begrenzte Antwortgröße, Mindestabstand zwischen Anfragen und Höchstzahl je Minute.
  • Antworten gelten als nicht vertrauenswürdig: nur erwartete JSON-Felder, Text bereinigt (HTML, Steuerzeichen,
    unsichtbare Zeichen, Formelzeichen wie „=“ am Anfang, die Kartenzeichen „/“ und „|“), nur Buchstaben und
    übliche Satzzeichen, Länge begrenzt.
  • Ein DeepL-Schlüssel liegt außerhalb des Projektordners im Benutzerordner (nur für dieses Benutzerkonto
    lesbar), kommt nie in die Projekt-ZIP, wird nur an DeepL geschickt und der Browser-Seite nie gezeigt.
  • Ergebnisse werden im Benutzerordner zwischengespeichert, damit dasselbe Wort nicht mehrfach gesendet wird.

Nur Standardbibliothek. Selbsttest ohne Internet: test_gans_lernkarten.py (Abschnitt „Übersetzung“).
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from pathlib import Path

VERSION = "2.2 (21.10.2026)"
USER_AGENT = "Me-Goos-ta-Deutsch/2.2 (Lernkarten-Programm; privat)"
ZEITLIMIT = 10                    # Sekunden je Anfrage
MAX_ANTWORT = 1_500_000           # Bytes (eine Wiktionary-Seite hat selten mehr als 200 KB)
MAX_QUELLE = 80                   # Zeichen, die höchstens gesendet werden
MAX_VORSCHLAG = 60                # Zeichen je vorgeschlagener Übersetzung
MIN_ABSTAND = 0.35                # Sekunden zwischen zwei Anfragen an denselben Dienst
MAX_JE_MINUTE = 40                # Anfragen je Dienst und Minute
CACHE_EINTRAEGE = 3000
CACHE_TAGE = 90

DIENSTE = {
    "wiktionary": dict(
        hosts=("de.wiktionary.org",), konto=False, art="woerterbuch",
        titel={"de": "Wiktionary – freies Wörterbuch", "en": "Wiktionary – free dictionary",
               "es": "Wiktionary – diccionario libre"},
        beschreibung={
            "de": "Am besten für einzelne Wörter: mehrere Bedeutungen und Alternativen, von Menschen gepflegt. "
                  "Ohne Konto. Betreiber: Wikimedia Foundation.",
            "en": "Best for single words: several meanings and alternatives, maintained by people. No account. "
                  "Operator: Wikimedia Foundation.",
            "es": "Lo mejor para palabras sueltas: varios significados y alternativas, mantenido por personas. Sin "
                  "cuenta. Operador: Wikimedia Foundation."}),
    "mymemory": dict(
        hosts=("api.mymemory.translated.net",), konto=False, art="maschine",
        titel={"de": "MyMemory – maschinelle Übersetzung", "en": "MyMemory – machine translation",
               "es": "MyMemory – traducción automática"},
        beschreibung={
            "de": "Für Wendungen aus mehreren Wörtern. Ohne Konto, etwa 5000 Zeichen am Tag. "
                  "Betreiber: Translated srl (Italien).",
            "en": "For phrases of several words. No account, about 5000 characters a day. "
                  "Operator: Translated srl (Italy).",
            "es": "Para frases de varias palabras. Sin cuenta, unos 5000 caracteres al día. "
                  "Operador: Translated srl (Italia)."}),
    "deepl": dict(
        hosts=("api-free.deepl.com", "api.deepl.com"), konto=True, art="maschine",
        titel={"de": "DeepL – mit eigenem API-Schlüssel", "en": "DeepL – with your own API key",
               "es": "DeepL – con tu propia clave de API"},
        beschreibung={
            "de": "Sehr gute Qualität, lateinamerikanisches Spanisch. Braucht ein kostenloses Konto „DeepL API Free“ "
                  "(500 000 Zeichen im Monat). Betreiber: DeepL SE (Deutschland).",
            "en": "Very good quality, Latin American Spanish. Needs a free “DeepL API Free” account "
                  "(500,000 characters a month). Operator: DeepL SE (Germany).",
            "es": "Muy buena calidad, español latinoamericano. Necesita una cuenta gratuita «DeepL API Free» "
                  "(500 000 caracteres al mes). Operador: DeepL SE (Alemania)."}),
}
STRATEGIEN = ("auto", "wiktionary", "mymemory", "deepl")
ERLAUBTE_HOSTS = frozenset(h for d in DIENSTE.values() for h in d["hosts"])
DEEPL_SCHLUESSEL = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}(:fx)?")

FEHLER_TEXTE = {
    "zustimmung": {"de": "Die automatische Übersetzung ist noch nicht eingeschaltet.",
                   "en": "Automatic translation is not switched on yet.",
                   "es": "La traducción automática aún no está activada."},
    "leer": {"de": "Es gibt keinen Text zum Übersetzen – erst den Text auf dem Bild eintragen.",
             "en": "There is no text to translate – enter the text on the image first.",
             "es": "No hay texto para traducir; primero escribe el texto de la imagen."},
    "unpassend": {"de": "Dieser Text wird nicht gesendet (sieht aus wie eine E-Mail- oder Internetadresse).",
                  "en": "This text is not sent (it looks like an e-mail or web address).",
                  "es": "Este texto no se envía (parece una dirección de correo o de internet)."},
    "netz": {"de": "Keine Verbindung zum Übersetzungsdienst – Internet prüfen.",
             "en": "No connection to the translation service – check the internet connection.",
             "es": "Sin conexión con el servicio de traducción; revisa la conexión a internet."},
    "zertifikat": {"de": "Die Verbindung zum Übersetzungsdienst ist nicht vertrauenswürdig (Zertifikat) – abgebrochen.",
                   "en": "The connection to the translation service is not trustworthy (certificate) – cancelled.",
                   "es": "La conexión con el servicio de traducción no es de confianza (certificado); se canceló."},
    "zeit": {"de": "Der Übersetzungsdienst antwortet nicht – später noch einmal versuchen.",
             "en": "The translation service is not responding – try again later.",
             "es": "El servicio de traducción no responde; inténtalo más tarde."},
    "zu_viele": {"de": "Zu viele Anfragen in kurzer Zeit – bitte eine Minute warten.",
                 "en": "Too many requests in a short time – please wait a minute.",
                 "es": "Demasiadas solicitudes en poco tiempo; espera un minuto."},
    "kontingent": {"de": "Das kostenlose Tageskontingent des Dienstes ist aufgebraucht – morgen wieder, oder in den "
                         "Werkzeugen einen anderen Dienst wählen.",
                   "en": "The service's free daily quota is used up – try again tomorrow or choose another service "
                         "under Tools.",
                   "es": "Se agotó la cuota gratuita del servicio por hoy; vuelve mañana o elige otro servicio en "
                         "Herramientas."},
    "schluessel": {"de": "Der DeepL-Schlüssel wurde abgelehnt – in den Werkzeugen prüfen.",
                   "en": "The DeepL key was rejected – check it under Tools.",
                   "es": "DeepL rechazó la clave; revísala en Herramientas."},
    "kein_schluessel": {"de": "Für DeepL fehlt der eigene API-Schlüssel (Werkzeuge → Automatische Übersetzung).",
                        "en": "DeepL needs your own API key (Tools → Automatic translation).",
                        "es": "DeepL necesita tu propia clave de API (Herramientas → Traducción automática)."},
    "schluessel_format": {"de": "Das sieht nicht wie ein DeepL-API-Schlüssel aus (Form: xxxxxxxx-xxxx-xxxx-xxxx-"
                                "xxxxxxxxxxxx:fx).",
                          "en": "That does not look like a DeepL API key (form: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:fx).",
                          "es": "Eso no parece una clave de API de DeepL (forma: xxxxxxxx-xxxx-xxxx-xxxx-"
                                "xxxxxxxxxxxx:fx)."},
    "weiterleitung": {"de": "Der Dienst wollte auf eine andere Adresse umleiten – aus Sicherheitsgründen abgebrochen.",
                      "en": "The service tried to redirect to another address – cancelled for security reasons.",
                      "es": "El servicio intentó redirigir a otra dirección; se canceló por seguridad."},
    "adresse": {"de": "Unzulässige Adresse – es werden nur die fest eingetragenen Dienste benutzt.",
                "en": "Address not allowed – only the built-in services are used.",
                "es": "Dirección no permitida; solo se usan los servicios integrados."},
    "format": {"de": "Unerwartete Antwort des Übersetzungsdienstes – verworfen.",
               "en": "Unexpected answer from the translation service – discarded.",
               "es": "Respuesta inesperada del servicio de traducción; se descartó."},
    "dienst": {"de": "Der Übersetzungsdienst meldet einen Fehler ({code}).",
               "en": "The translation service reports an error ({code}).",
               "es": "El servicio de traducción indica un error ({code})."},
    "unbekannt": {"de": "Unbekannter Übersetzungsdienst.", "en": "Unknown translation service.",
                  "es": "Servicio de traducción desconocido."},
    "dienst_rechner": {"de": "DeepL geht nur in der Fassung am Rechner – hier in der App übersetzen Wiktionary und "
                             "MyMemory, „Automatisch“ nimmt den passenden.",
                       "en": "DeepL works only in the computer version – here in the app Wiktionary and MyMemory "
                             "translate, “Automatic” picks the right one.",
                       "es": "DeepL solo funciona en la versión de la computadora; aquí en la app traducen Wiktionary y "
                             "MyMemory, «Automático» elige el adecuado."},
    "sprache_dienst": {"de": "Dieser Dienst kennt die gewählte Sprache leider nicht – „Automatisch“ nimmt einen, der "
                             "sie kann.",
                       "en": "Sorry, this service doesn’t know the chosen language – “Automatic” picks one that does.",
                       "es": "Este servicio no conoce el idioma elegido; «Automático» elige uno que sí lo conoce."},
    "sprache_unbekannt": {"de": "Diese Sprache kennt das Programm nicht.", "en": "The program doesn’t know this "
                                "language.", "es": "El programa no conoce este idioma."},
}


class UebersetzungsFehler(Exception):
    def __init__(self, fehler_code, /, **werte):           # werte darf selbst „code“ (HTTP-Status) enthalten
        super().__init__(fehler_code)
        self.code, self.werte = fehler_code, werte

    def text(self, sprache="en"):
        t = FEHLER_TEXTE.get(self.code, FEHLER_TEXTE["format"])
        return (t.get(sprache) or t["de"]).format(code=self.werte.get("code", "?"))


# =============================================================================================
# Ablage im Benutzerordner (nicht im Projekt, nicht in der Projekt-ZIP)
# =============================================================================================
def daten_ordner() -> Path:
    """Gleicher Ordner wie beim Startprogramm (starter.py)."""
    if os.environ.get("MGD_DATEN"):
        return Path(os.environ["MGD_DATEN"])
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "Me-Goos-ta-Deutsch"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Me-Goos-ta-Deutsch"
    return Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "me-goos-ta-deutsch"


_datei_lock = threading.Lock()


def _lies_json(pfad):
    try:
        d = json.loads(Path(pfad).read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def _schreibe_privat(pfad, daten):
    """Schreibt JSON atomar und nur für das eigene Benutzerkonto lesbar (0600; unter Windows schützt der
    Benutzerordner %LOCALAPPDATA% über seine Zugriffsrechte)."""
    pfad = Path(pfad)
    pfad.parent.mkdir(parents=True, exist_ok=True)
    tmp = pfad.with_name(f"{pfad.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(daten, f, ensure_ascii=False)
    os.replace(tmp, pfad)
    try:
        os.chmod(pfad, 0o600)
    except OSError:
        pass


def einstellungen_pfad():
    return daten_ordner() / "uebersetzung.json"


def lade_einstellungen():
    d = _lies_json(einstellungen_pfad())
    schluessel = d.get("deepl") if isinstance(d.get("deepl"), str) and DEEPL_SCHLUESSEL.fullmatch(d.get("deepl")) else None
    return dict(zugestimmt=d.get("zugestimmt") is True,
                dienst=d.get("dienst") if d.get("dienst") in STRATEGIEN else "auto",
                automatisch=d.get("automatisch") is True,
                deepl=schluessel)


def speichere_einstellungen(aenderung):
    """Übernimmt nur bekannte Felder mit gültigen Werten. deepl: neuer Schlüssel, '' = löschen, None = unverändert."""
    with _datei_lock:
        e = lade_einstellungen()
        if "zugestimmt" in aenderung:
            e["zugestimmt"] = aenderung["zugestimmt"] is True
        if "dienst" in aenderung:
            if aenderung["dienst"] not in STRATEGIEN:
                raise UebersetzungsFehler("unbekannt")
            e["dienst"] = aenderung["dienst"]
        if "automatisch" in aenderung:
            e["automatisch"] = aenderung["automatisch"] is True
        if aenderung.get("deepl") is not None:
            neu = str(aenderung["deepl"]).strip()
            if neu and not DEEPL_SCHLUESSEL.fullmatch(neu):
                raise UebersetzungsFehler("schluessel_format")
            e["deepl"] = neu or None
        if e["dienst"] == "deepl" and not e["deepl"]:
            e["dienst"] = "auto"
        _schreibe_privat(einstellungen_pfad(), e)
    return e


def oeffentliche_einstellungen(sprache="en"):
    """Für die Browser-Seite: alles außer dem Schlüssel selbst (nur ob einer da ist und seine letzten Zeichen)."""
    e = lade_einstellungen()
    k = e["deepl"]
    return dict(zugestimmt=e["zugestimmt"], dienst=e["dienst"], automatisch=e["automatisch"],
                deepl_gesetzt=bool(k), deepl_ende=("…" + k[-6:]) if k else "",
                dienste=[dict(id=i, titel=d["titel"].get(sprache, d["titel"]["de"]),
                              beschreibung=d["beschreibung"].get(sprache, d["beschreibung"]["de"]),
                              adresse=d["hosts"][0], konto=d["konto"], art=d["art"],
                              **({"nur_rechner": True} if i == "deepl" and im_browser() else {}))
                         for i, d in DIENSTE.items()],
                ablage=str(einstellungen_pfad().parent))


# =============================================================================================
# Text vorbereiten und Antworten bereinigen
# =============================================================================================
# Erlaubt sind lateinische Buchstaben (inkl. Erweiterungen für Türkisch, Polnisch, Pinyin-Töne, Umschriften) und nur
# die Schrift der jeweiligen Kartensprache (Kyrillisch, Arabisch, Devanagari, Kana/CJK, Hangul samt ihren Satzzeichen)
# – eine Antwort in einer fremden Schrift wird verworfen; weiterhin keine Formel-, Steuer- oder Auszeichnungszeichen.
_LATEIN_ZEICHEN = "0-9A-Za-zÀ-ÖØ-öø-ÿĀ-žƀ-ɏʹʼʾʿḀ-ỿ' ’,()¿?¡!.\\-"
SCHRIFT_ZEICHEN = {
    "kyrillisch": "\u0400-\u04FF",
    "arabisch": "\u0600-\u06FF\u0750-\u077F",
    "devanagari": "\u0900-\u097F",
    "cjk": "\u3001\u3002\u3040-\u30FF\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\uFF01\uFF0C\uFF1F",
    "hangul": "\u1100-\u11FF\u3130-\u318F\uAC00-\uD7AF\u3001\u3002\uFF01\uFF0C\uFF1F",
}
_ERLAUBT = re.compile("[" + _LATEIN_ZEICHEN + "]+")
_ERLAUBT_JE = {s: re.compile("[" + _LATEIN_ZEICHEN + z + "]+") for s, z in SCHRIFT_ZEICHEN.items()}


def erlaubt(code="es"):
    """Zeichenprüfung für die Kartensprache code (Spanisch und lateinische Sprachen: nur lateinisch)."""
    try:
        import sprachen
        schrift = sprachen.SPRACHEN[code]["schrift"] if code in sprachen.SPRACHEN else "latein"
    except ImportError:
        schrift = "latein"
    return _ERLAUBT_JE.get(schrift, _ERLAUBT)


_LATEIN = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿĀ-žƀ-ɏʹʼʾʿḀ-ỿ' ’.\-]+")


_ES_CODES = dict(wiktionary=("es",), abschnitt=("Spanisch",), mymemory=("es-MX", "es"), deepl=("ES-419", "ES"),
                 deepl_quelle="ES")


def sprach_codes(code):
    """Dienst-Codes einer Kartensprache aus sprachen.py (Spanisch geht auch ohne die Datei)."""
    try:
        import sprachen
    except ImportError:
        sprachen = None
    if sprachen and code in sprachen.SPRACHEN:
        return dict(sprachen.SPRACHEN[code]["dienste"], umschrift=sprachen.SPRACHEN[code]["umschrift"])
    if code == "es":
        return dict(_ES_CODES, umschrift=False)
    raise UebersetzungsFehler("sprache_unbekannt")
_GEFAEHRLICH_ANFANG = ("=", "+", "-", "@", "\t", "\r")


def quelltext(de):
    """Der Teil der Karte, der übersetzt wird: der Text auf dem Bild ohne das vorangestellte „Gans“
    („Gans aufgeregt“ → „aufgeregt“). Gibt '' zurück, wenn nichts übrig bleibt."""
    t = "".join(c for c in str(de or "") if unicodedata.category(c)[0] != "C")
    t = " ".join(t.split())
    t = re.sub(r"(?i)^gans\b[\s,:–-]*", "", t).strip()
    return t[:MAX_QUELLE].strip()


def pruefe_quelle(text):
    if not text:
        raise UebersetzungsFehler("leer")
    if re.search(r"@|https?:|www\.|\.(com|de|net|org|mx)\b", text, re.I):
        raise UebersetzungsFehler("unpassend")
    return text


_ZEILENTRENNER = (chr(0x2028), chr(0x2029))


def _vorreinigen(text):
    """HTML, Wiki-Auszeichnung, Steuer- und unsichtbare Zeichen entfernen (Unicode NFC)."""
    if not isinstance(text, str):
        return ""
    t = html.unescape(text[:500])
    t = re.sub(r"<[^>]{0,300}>", " ", t)                                  # HTML-Reste
    t = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", t)              # Wiki-Verweise
    t = re.sub(r"\{\{[^{}]*\}\}", " ", t).replace("''", "")              # Wiki-Vorlagen und Kursivzeichen
    t = unicodedata.normalize("NFC", t)
    t = "".join(c for c in t if unicodedata.category(c)[0] != "C" and c not in _ZEILENTRENNER)
    return " ".join(t.split())


def kandidaten(text, quelle="", deutsch=False, code="es"):
    """Zerlegt eine Antwort in sichere Kartentexte. Eine Antwort, die wie eine Formel beginnt oder fremde Zeichen
    enthält, wird ganz verworfen (nicht in harmlos aussehende Stücke zerlegt). „a / b“ ergibt zwei Vorschläge.
    deutsch=True: Rückrichtung Spanisch → Deutsch (Großschreibung deutscher Wörter bleibt)."""
    if not isinstance(text, str) or re.search(r"<\s*[A-Za-z/!?]", html.unescape(text[:500])):
        return []                                                         # HTML/Skript in der Antwort → verwerfen
    t = _vorreinigen(text).lstrip(" -–•*")
    muster = _ERLAUBT if deutsch else erlaubt(code)
    if not t or t[0] in _GEFAEHRLICH_ANFANG or not muster.fullmatch(t.replace("/", "")):
        return []
    return [b for b in (bereinige(teil, quelle, deutsch, code) for teil in t.split("/")) if b]


def bereinige(text, quelle="", deutsch=False, code="es"):
    """Macht aus einem einzelnen Vorschlag einen sicheren Kartentext – oder '' (verworfen)."""
    t = _vorreinigen(text).strip(" .;:,")
    if not t or t[0] in _GEFAEHRLICH_ANFANG:                              # nie als Excel-Formel lesbar
        return ""
    if len(t) > MAX_VORSCHLAG or not (_ERLAUBT if deutsch else erlaubt(code)).fullmatch(t) \
            or not re.search(r"[^\W\d_]", t):
        return ""
    if t.isupper() and len(t) > 3 and not str(quelle).isupper():          # „VIEJO“ → „viejo“
        t = t.lower()
    erster = t.split(" ")[0]
    if not deutsch and erster[:1].isupper() and erster[1:].islower():
        t = t[0].lower() + t[1:]                                          # Kartenwörter klein: „Viejo“ → „viejo“
    if quelle and t.casefold() == str(quelle).casefold():
        return ""                                                         # nicht übersetzt
    return t


def _eindeutig(texte, n=8):
    gesehen, aus = set(), []
    for t in texte:
        k = t.casefold()
        if t and k not in gesehen:
            gesehen.add(k)
            aus.append(t)
        if len(aus) >= n:
            break
    return aus


# =============================================================================================
# Netzwerk: nur HTTPS, nur feste Adressen, keine Weiterleitungen, begrenzt
# =============================================================================================
class _KeineWeiterleitung(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        raise UebersetzungsFehler("weiterleitung")


def _ssl_kontexte():
    """Zertifikatsprüfung bleibt immer an: Standard des Systems → Zertifikatsspeicher des Betriebssystems
    (truststore aus pip) → Zertifikatsliste von certifi (aus pip). Wie beim Laden der KI-Modelle."""
    import ssl
    kontexte = [ssl.create_default_context()]
    try:
        from pip._vendor import truststore
        kontexte.append(truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT))
    except Exception:  # noqa: BLE001
        pass
    try:
        from pip._vendor import certifi
        kontexte.append(ssl.create_default_context(cafile=certifi.where()))
    except Exception:  # noqa: BLE001
        pass
    return kontexte


_takt_lock = threading.Lock()
_letzte: dict = {}


def _takt(host):
    """Mindestabstand und Höchstzahl je Minute – schont die freien Dienste und verhindert Endlosschleifen."""
    with _takt_lock:
        jetzt = time.monotonic()
        verlauf = _letzte.setdefault(host, deque())
        while verlauf and jetzt - verlauf[0] > 60:
            verlauf.popleft()
        if len(verlauf) >= MAX_JE_MINUTE:
            raise UebersetzungsFehler("zu_viele")
        warten = MIN_ABSTAND - (jetzt - verlauf[-1]) if verlauf else 0
        verlauf.append(jetzt + max(0.0, warten))
    if warten > 0:
        time.sleep(warten)


def pruefe_adresse(url, hosts=None):
    """hosts: eigene Liste erlaubter Hosts (z. B. Versionsprüfung) – sonst nur die Übersetzungsdienste."""
    teile = urllib.parse.urlsplit(url)
    if teile.scheme != "https" or teile.hostname not in (ERLAUBTE_HOSTS if hosts is None else frozenset(hosts)) or teile.port not in (None, 443) \
            or teile.username or teile.password or teile.fragment:
        raise UebersetzungsFehler("adresse")
    return teile.hostname


def im_browser():
    """Web-App (Pyodide): kein Socket, nur Dienste, die Anfragen aus dem Browser erlauben (CORS) – DeepL nicht."""
    return sys.platform == "emscripten"


def _json_pruefen(roh, art, max_antwort=MAX_ANTWORT):
    if len(roh) > max_antwort or "json" not in (art or "").lower():
        raise UebersetzungsFehler("format")
    try:
        d = json.loads(roh.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise UebersetzungsFehler("format") from None
    if not isinstance(d, dict):
        raise UebersetzungsFehler("format")
    return d


def _http_json_browser(url, daten=None):
    """Web-App: synchrones XMLHttpRequest des Browsers (läuft im Web-Worker), nur GET; gleiche Fehler-Codes."""
    if daten is not None:
        raise UebersetzungsFehler("dienst_rechner")
    import js                                                   # nur in Pyodide vorhanden
    x = js.XMLHttpRequest.new()
    x.open("GET", url, False)
    try:
        x.timeout = ZEITLIMIT * 1000                            # im Worker erlaubt
    except Exception:  # noqa: BLE001
        pass
    x.setRequestHeader("Accept", "application/json")
    try:
        x.send()
    except Exception:  # noqa: BLE001 – Netz weg, CORS verweigert, Zeitlimit
        raise UebersetzungsFehler("netz") from None
    if x.status == 429:
        raise UebersetzungsFehler("zu_viele")
    if x.status != 200:
        raise UebersetzungsFehler("dienst" if x.status else "netz", code=x.status)
    return _json_pruefen(str(x.responseText).encode("utf-8"), x.getResponseHeader("Content-Type"))


def http_json(url, daten=None, kopf=None, hosts=None, max_antwort=MAX_ANTWORT):
    """Holt JSON von einem der fest eingetragenen Dienste (bzw. von `hosts`, getrennt von den Übersetzungsdiensten).
    Wirft UebersetzungsFehler."""
    host = pruefe_adresse(url, hosts)
    _takt(host)
    if im_browser():
        return _http_json_browser(url, daten)
    import ssl
    k = {"User-Agent": USER_AGENT, "Accept": "application/json", "Accept-Encoding": "identity"}
    k.update(kopf or {})
    anfrage = urllib.request.Request(url, data=daten, headers=k, method="POST" if daten is not None else "GET")
    kontexte = _ssl_kontexte()
    for i, kontext in enumerate(kontexte):
        oeffner = urllib.request.build_opener(urllib.request.HTTPSHandler(context=kontext), _KeineWeiterleitung())
        try:
            with oeffner.open(anfrage, timeout=ZEITLIMIT) as r:
                return _json_pruefen(r.read(max_antwort + 1), r.headers.get("Content-Type"), max_antwort)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise UebersetzungsFehler("schluessel" if "deepl" in host else "dienst", code=e.code) from None
            if e.code == 429:
                raise UebersetzungsFehler("zu_viele") from None
            if e.code == 456:
                raise UebersetzungsFehler("kontingent") from None
            raise UebersetzungsFehler("dienst", code=e.code) from None
        except urllib.error.URLError as e:
            grund = getattr(e, "reason", None)
            if isinstance(grund, UebersetzungsFehler):
                raise grund from None
            if isinstance(grund, ssl.SSLCertVerificationError):
                if i < len(kontexte) - 1:
                    continue
                raise UebersetzungsFehler("zertifikat") from None
            if isinstance(grund, TimeoutError) or "timed out" in str(grund):
                raise UebersetzungsFehler("zeit") from None
            raise UebersetzungsFehler("netz") from None
        except (TimeoutError, OSError) as e:
            if isinstance(e, ssl.SSLCertVerificationError):
                if i < len(kontexte) - 1:
                    continue
                raise UebersetzungsFehler("zertifikat") from None
            raise UebersetzungsFehler("zeit" if isinstance(e, TimeoutError) else "netz") from None
    raise UebersetzungsFehler("netz")


# =============================================================================================
# Wiktionary: Übersetzungstabellen der deutschen Einträge lesen
# =============================================================================================
UE_VORLAGEN = {"Ü", "Ü?", "Üt", "Üt?", "Üxx4", "Üxx4?"}
_GENUS = {"m", "f", "n", "mf", "fm", "nm", "mn", "Pl.", "Sg.", "u", "c", "m.", "f.", "n."}


def _vorlage_ende(text, start):
    """Index hinter der Vorlage, die bei text[start] mit '{{' beginnt (verschachtelte Vorlagen werden mitgezählt)."""
    tiefe, i = 0, start
    while i < len(text) - 1:
        if text.startswith("{{", i):
            tiefe += 1
            i += 2
        elif text.startswith("}}", i):
            tiefe -= 1
            i += 2
            if tiefe == 0:
                return i
        else:
            i += 1
    return len(text)


def _teile(inhalt):
    """Teilt den Inhalt einer Vorlage an den '|' der obersten Ebene."""
    teile, tiefe, start, i = [], 0, 0, 0
    while i < len(inhalt):
        if inhalt.startswith("{{", i) or inhalt.startswith("[[", i):
            tiefe += 1
            i += 2
            continue
        if inhalt.startswith("}}", i) or inhalt.startswith("]]", i):
            tiefe = max(0, tiefe - 1)
            i += 2
            continue
        if inhalt[i] == "|" and tiefe == 0:
            teile.append(inhalt[start:i])
            start = i + 1
        i += 1
    teile.append(inhalt[start:])
    return teile


def _vorlagen(text, name):
    """Alle Vorlagen {{name|…}} in text → Liste (positionale Werte, benannte Werte)."""
    aus, i = [], 0
    while True:
        i = text.find("{{" + name, i)
        if i < 0:
            return aus
        nach = text[i + 2 + len(name): i + 3 + len(name)]
        if nach not in ("|", "}", "\n", " "):
            i += 2
            continue
        ende = _vorlage_ende(text, i)
        teile = _teile(text[i + 2: ende - 2])[1:]
        pos, benannt = [], {}
        for t in teile:
            m = re.match(r"\s*([^=|{}\[\]]{1,40}?)\s*=(.*)\Z", t, re.S)
            if m:
                benannt[m.group(1).strip()] = m.group(2)
            else:
                pos.append(t)
        aus.append((pos, benannt))
        i = ende


def _sauber(t):
    t = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", str(t or ""))
    t = re.sub(r"\{\{[^{}]*\}\}", "", t).replace("'''", "").replace("''", "")
    t = re.sub(r"<[^>]{0,200}>", "", t)
    return " ".join(html.unescape(t).split())


def _deutscher_abschnitt(wikitext):
    """Nur der Abschnitt „== Wort ({{Sprache|Deutsch}}) ==“ – andere Sprachen auf derselben Seite zählen nicht."""
    m = re.search(r"^==[^=\n].*\{\{Sprache\|Deutsch\}\}.*==\s*$", wikitext, re.M)
    if not m:
        return ""
    rest = wikitext[m.end():]
    n = re.search(r"^==[^=\n].*==\s*$", rest, re.M)
    return rest[: n.start()] if n else rest


def _zeile_lesen(zeile, nr, bedeutung, codes=("es",)):
    """Liest die Übersetzungen in die Sprache(n) codes aus einer Zeile einer Übersetzungstabelle. Bei {{Üt|…}} kommt
    die Umschrift (3. Wert) als „umschrift“ mit."""
    bausteine, i, text = [], 0, ""

    def text_weg():
        nonlocal text
        if text.strip():
            bausteine.append(("text", text))
        text = ""
    while i < len(zeile):
        if zeile.startswith("{{", i):
            text_weg()
            ende = _vorlage_ende(zeile, i)
            teile = _teile(zeile[i + 2: ende - 2])
            bausteine.append(("vorlage", teile[0].strip(), teile[1:]))
            i = ende
        elif zeile.startswith("''", i):
            text_weg()
            ende = zeile.find("''", i + 2)
            ende = len(zeile) if ende < 0 else ende
            bausteine.append(("kursiv", zeile[i + 2: ende].strip("'")))
            i = ende + 2
        elif zeile.startswith("[[", i):
            ende = zeile.find("]]", i)
            ende = len(zeile) if ende < 0 else ende
            text += _sauber(zeile[i: ende + 2])
            i = ende + 2
        elif zeile[i] == "[":
            m = re.match(r"\[([0-9a-z,\s–\-]{1,20})\]", zeile[i:])
            if m:
                text_weg()
                bausteine.append(("nr", m.group(1).strip()))
                i += m.end()
            else:
                text += zeile[i]
                i += 1
        elif zeile[i] in ",;":
            text_weg()
            bausteine.append(("trenner", zeile[i]))
            i += 1
        else:
            text += zeile[i]
            i += 1
    text_weg()

    eintraege, aktuell, merkmale, zwischen, nr_jetzt = [], None, [], "", nr
    for b in bausteine:
        art = b[0]
        if art == "nr":
            nr_jetzt = b[1]
        elif art == "kursiv":
            merkmale += [m.strip(" :") for m in re.split(r",\s*", _sauber(b[1])) if m.strip(" :")]
        elif art == "trenner":
            if aktuell:
                eintraege.append(aktuell)
            aktuell, zwischen = None, ""
        elif art == "text":
            if aktuell:
                zwischen = _sauber(b[1]).strip(" :")
        elif art == "vorlage":
            name, werte = b[1], b[2]
            if name in UE_VORLAGEN:
                if not werte or werte[0].strip() not in codes:
                    continue
                ziel = _sauber(werte[1]) if len(werte) > 1 else ""
                umschrift = ""
                if name.rstrip("?") == "Üt":                         # {{Üt|ru|гусь|gusʹ|Anzeige}}
                    anzeige = _sauber(werte[3]) if len(werte) > 3 else ""
                    umschrift = _sauber(werte[2]) if len(werte) > 2 else ""
                else:
                    anzeige = _sauber(werte[2]) if len(werte) > 2 and name.rstrip("?") == "Ü" else ""
                wort = anzeige or ziel
                if not wort:
                    continue
                if aktuell:                                         # „{{Ü|es|tener}} {{Ü|es|hambre}}“ = eine Wendung
                    aktuell["text"] += " " + (zwischen + " " if zwischen else "") + wort
                    if umschrift and aktuell.get("umschrift"):
                        aktuell["umschrift"] += " " + umschrift
                else:
                    aktuell = dict(text=wort, nr=nr_jetzt or "", bedeutung=bedeutung, merkmale=merkmale,
                                   unsicher=name.endswith("?"), umschrift=umschrift)
                    merkmale = []
                zwischen = ""
            elif name not in _GENUS and name.lower() not in codes:
                if 0 < len(name) <= 30 and not name.startswith("Ü"):
                    merkmale.append(name.rstrip(":"))
    if aktuell:
        eintraege.append(aktuell)
    return eintraege


def wiktionary_ziel(wikitext, code="es"):
    """Übersetzungen in die Kartensprache code aus dem deutschen Abschnitt einer Wiktionary-Seite →
    Liste von dict(text, nr, bedeutung, merkmale, unsicher, umschrift) in der Reihenfolge der Bedeutungen."""
    codes = sprach_codes(code)["wiktionary"]
    muster = re.compile(r"\{\{Ü[^|{}]*\|\s*(?:" + "|".join(re.escape(c) for c in codes) + r")\s*\|")
    abschnitt = _deutscher_abschnitt(str(wikitext or ""))
    eintraege = []
    for pos, benannt in _vorlagen(abschnitt, "Ü-Tabelle"):
        nr = _sauber(pos[0]) if pos else ""
        bedeutung = _sauber(benannt.get("G", ""))
        for feld in ("Ü-Liste", "Ü-links", "Ü-rechts"):
            for zeile in str(benannt.get(feld, "")).splitlines():
                if muster.search(zeile):
                    eintraege += _zeile_lesen(zeile.lstrip("*: "), nr, bedeutung, codes)
    return eintraege


def wiktionary_spanisch(wikitext):
    """Spanische Übersetzungen (wie bisher) – siehe wiktionary_ziel."""
    return wiktionary_ziel(wikitext, "es")


_REGION_GUT = ("mexik", "lateinamerik", "amerik")
_REGION_ANDERE = ("spanien", "argentin", "chile", "kolumb", "peru", "venez", "kuba", "nicaragua", "urug", "parag",
                  "bolivi", "ecuador", "guatem", "hondur", "salvador", "costa rica", "panam", "puerto", "dominik",
                  "philipp", "rioplat", "karib", "andalus", "kanar")
_STIL_SELTEN = ("veraltet", "selten", "gehoben", "dicht", "poet", "fachspr", "abwert", "vulg", "derb", "pejor")


def ordne(eintraege, code="es"):
    """Reihenfolge der Bedeutungen wie im Wörterbuch (die erste ist meist die gemeinte). Innerhalb einer Bedeutung:
    Mexikanisch/Lateinamerikanisch zuerst, Wörter anderer Länder, veraltete und unsichere nach hinten – stark
    abweichende (andere Länder, veraltet, unsicher) kommen ganz ans Ende."""
    bedeutungen = []
    for e in eintraege:
        if e.get("nr", "") not in bedeutungen:
            bedeutungen.append(e.get("nr", ""))

    def wert(paar):
        i, e = paar
        m = " ".join(e.get("merkmale") or []).lower()
        punkte = 0
        if code == "es" and any(w in m for w in _REGION_GUT):   # Regionsordnung nur für Spanisch (Mexiko zuerst)
            punkte -= 1
        if code == "es" and any(w in m for w in _REGION_ANDERE):
            punkte += 3
        if any(w in m for w in _STIL_SELTEN):
            punkte += 2
        if e.get("unsicher"):
            punkte += 4
        return (1 if punkte >= 2 else 0), bedeutungen.index(e.get("nr", "")), punkte, i
    return [e for _, e in sorted(enumerate(eintraege), key=wert)]


def _wiki_url(titel):
    werte = dict(action="query", prop="revisions", rvprop="content", rvslots="main", format="json", formatversion="2",
                 redirects="1", titles="|".join(titel))
    if im_browser():                                 # Web-App: anonyme CORS-Anfrage (sonst verweigert der Browser)
        werte["origin"] = "*"
    return "https://de.wiktionary.org/w/api.php?" + urllib.parse.urlencode(werte)


def _wiktionary(quelle, abruf, tiefe=0, code="es"):
    if len(quelle.split()) > 2:
        return []
    titel = [quelle]
    if quelle[:1].islower():
        titel.append(quelle[:1].upper() + quelle[1:])
    elif quelle[:1].isupper():
        titel.append(quelle[:1].lower() + quelle[1:])
    d = abruf(_wiki_url(titel), None, None)
    seiten = ((d.get("query") or {}).get("pages")) if isinstance(d.get("query"), dict) else None
    if not isinstance(seiten, list):
        raise UebersetzungsFehler("format")
    texte = {}
    for s in seiten:
        if not isinstance(s, dict) or s.get("missing") or not isinstance(s.get("revisions"), list) or not s["revisions"]:
            continue
        inhalt = (((s["revisions"][0] or {}).get("slots") or {}).get("main") or {}).get("content")
        if isinstance(inhalt, str) and isinstance(s.get("title"), str):
            texte[s["title"]] = inhalt
    for t in titel + [x for x in texte if x not in titel]:          # zuerst wie geschrieben, dann Weiterleitungsziel
        wikitext = texte.get(t)
        if not wikitext:
            continue
        eintraege = wiktionary_ziel(wikitext, code)
        if eintraege:
            return ordne(eintraege, code)
        grund = re.search(r"\{\{Grundformverweis[^|}]*\|([^|}\n]{1,60})", _deutscher_abschnitt(wikitext))
        if grund and tiefe == 0:                             # flektierte Form → Grundform nachschlagen
            g = _sauber(grund.group(1))
            if g and g != quelle:
                return _wiktionary(g, abruf, 1, code)
    return []


# =============================================================================================
# MyMemory und DeepL
# =============================================================================================
def _mymemory(quelle, abruf, code="es"):
    paare = [f"de|{c}" for c in sprach_codes(code)["mymemory"]]   # es: mexikanisch, sonst allgemeines Spanisch
    if not paare:
        raise UebersetzungsFehler("sprache_dienst")
    for paar in paare:
        url = "https://api.mymemory.translated.net/get?" + urllib.parse.urlencode({"q": quelle, "langpair": paar})
        d = abruf(url, None, None)
        status = d.get("responseStatus")
        try:
            status = int(status)
        except (TypeError, ValueError):
            status = 0
        if status == 403 and "invalid" in str(d.get("responseDetails", "")).lower() and paar != paare[-1]:
            continue
        break
    if d.get("quotaFinished") is True or status == 429:
        raise UebersetzungsFehler("kontingent")
    if status != 200:
        raise UebersetzungsFehler("dienst", code=status or "?")
    kandidaten = []
    haupt = (d.get("responseData") or {}).get("translatedText") if isinstance(d.get("responseData"), dict) else None
    if isinstance(haupt, str):
        kandidaten.append(dict(text=haupt, nr="", bedeutung="", merkmale=[], unsicher=False))
    for m in (d.get("matches") if isinstance(d.get("matches"), list) else [])[:10]:
        if not isinstance(m, dict):
            continue
        guete = m.get("match")
        if isinstance(m.get("translation"), str) and isinstance(guete, (int, float)) and guete >= 0.85 \
                and str(m.get("segment", "")).strip().casefold() == quelle.casefold():
            kandidaten.append(dict(text=m["translation"], nr="", bedeutung="", merkmale=[], unsicher=False))
    return kandidaten


def _deepl(quelle, abruf, schluessel, code="es"):
    ziele = sprach_codes(code)["deepl"]                        # es: lateinamerikanisch, sonst allgemeines Spanisch
    if not ziele:
        raise UebersetzungsFehler("sprache_dienst")
    if not schluessel or not DEEPL_SCHLUESSEL.fullmatch(schluessel):
        raise UebersetzungsFehler("kein_schluessel")
    host = "api-free.deepl.com" if schluessel.endswith(":fx") else "api.deepl.com"
    kopf = {"Authorization": f"DeepL-Auth-Key {schluessel}", "Content-Type": "application/json"}
    for ziel in ziele:
        body = json.dumps({"text": [quelle], "source_lang": "DE", "target_lang": ziel})
        try:
            d = abruf(f"https://{host}/v2/translate", body.encode("utf-8"), kopf)
        except UebersetzungsFehler as e:
            if e.code == "dienst" and e.werte.get("code") == 400 and ziel != ziele[-1]:
                continue
            raise
        liste = d.get("translations")
        if not isinstance(liste, list) or not liste or not isinstance(liste[0], dict):
            raise UebersetzungsFehler("format")
        return [dict(text=liste[0].get("text"), nr="", bedeutung="", merkmale=[], unsicher=False)]
    return []


# =============================================================================================
# Rückrichtung Spanisch → Deutsch (Reiter „Ideen“: Wort auf Spanisch → „Text auf dem Bild“)
# Gleiche Schutzregeln wie oben: nur nach Zustimmung, nur das Wort, nur feste Dienste, Antworten bereinigt.
# =============================================================================================
def quelltext_es(es):
    """Das Wort auf Spanisch, das übersetzt wird: das Hauptwort vor „/“, ohne ¿ ¡ ? ! und Steuerzeichen."""
    t = "".join(c for c in str(es or "") if unicodedata.category(c)[0] != "C")
    t = re.sub(r"[¿¡?!？！؟。、]", " ", t.split("/")[0].split("|")[0])
    return " ".join(t.split())[:MAX_QUELLE].strip()


def quelltext_ziel(text, code="es"):
    """Wort in der Kartensprache für die Rückrichtung (nur das Hauptwort, ohne Umschrift nach „|“)."""
    return quelltext_es(text)


def _spanischer_abschnitt(wikitext, namen=("Spanisch",)):
    """Nur der Abschnitt „== Wort ({{Sprache|Spanisch}}) ==“ (bzw. der Sprache namen) einer Seite des deutschen
    Wiktionarys."""
    m = None
    for n in namen:
        m = re.search(r"^==[^=\n].*\{\{Sprache\|" + re.escape(n) + r"\}\}.*==\s*$", wikitext, re.M)
        if m:
            break
    if not m:
        return ""
    rest = wikitext[m.end():]
    n = re.search(r"^==[^=\n].*==\s*$", rest, re.M)
    return rest[: n.start()] if n else rest


def wiktionary_deutsch(wikitext, code="es"):
    """Deutsche Bedeutungen eines spanischen Worts: Liste „{{Bedeutungen}}“ im spanischen Abschnitt
    („:[1] alt, betagt“) → dict(text, nr, bedeutung, merkmale, unsicher) in der Reihenfolge der Bedeutungen."""
    abschnitt = _spanischer_abschnitt(wikitext, sprach_codes(code)["abschnitt"] or ("Spanisch",))
    m = re.search(r"\{\{Bedeutungen\}\}[ \t]*\n(.*?)(?:\n[ \t]*\n|\n\{\{|\Z)", abschnitt, re.S)
    if not m:
        return []
    eintraege = []
    for zeile in m.group(1).splitlines():
        z = re.match(r"\s*:+\s*\[([0-9a-z,\s–-]{1,20})\]\s*(.*)", zeile)
        if not z:
            continue
        merkmale = [_sauber(x) for x in re.findall(r"\{\{K\|([^{}]{1,80})\}\}", z.group(2))]
        text = _sauber(re.sub(r"\{\{K\|[^{}]*\}\}", "", z.group(2)))
        text = re.sub(r"\([^)]{0,80}\)", "", text)                         # Erklärungen in Klammern weglassen
        for teil in re.split(r"[;,]", text):
            teil = teil.strip(" .:")
            if teil and len(teil) <= 40:
                eintraege.append(dict(text=teil, nr=z.group(1).strip(), bedeutung="", merkmale=merkmale,
                                      unsicher=False))
    return eintraege


def _wiktionary_es_de(quelle, abruf, code="es"):
    if len(quelle.split()) > 2:
        return []
    if not sprach_codes(code)["abschnitt"]:
        raise UebersetzungsFehler("sprache_dienst")
    titel = [quelle] + ([quelle[:1].lower() + quelle[1:]] if quelle[:1].isupper() else [])
    d = abruf(_wiki_url(titel), None, None)
    seiten = ((d.get("query") or {}).get("pages")) if isinstance(d.get("query"), dict) else None
    if not isinstance(seiten, list):
        raise UebersetzungsFehler("format")
    for s in seiten:
        if not isinstance(s, dict) or s.get("missing") or not isinstance(s.get("revisions"), list) or not s["revisions"]:
            continue
        inhalt = (((s["revisions"][0] or {}).get("slots") or {}).get("main") or {}).get("content")
        if isinstance(inhalt, str):
            eintraege = wiktionary_deutsch(inhalt, code)
            if eintraege:
                return eintraege
    return []


def _mymemory_es_de(quelle, abruf, code="es"):
    paare = [f"{c}|de" for c in sprach_codes(code)["mymemory"]]
    if not paare:
        raise UebersetzungsFehler("sprache_dienst")
    for paar in paare:
        url = "https://api.mymemory.translated.net/get?" + urllib.parse.urlencode({"q": quelle, "langpair": paar})
        d = abruf(url, None, None)
        try:
            status = int(d.get("responseStatus"))
        except (TypeError, ValueError):
            status = 0
        if status == 403 and "invalid" in str(d.get("responseDetails", "")).lower() and paar != paare[-1]:
            continue
        break
    if d.get("quotaFinished") is True or status == 429:
        raise UebersetzungsFehler("kontingent")
    if status != 200:
        raise UebersetzungsFehler("dienst", code=status or "?")
    haupt = (d.get("responseData") or {}).get("translatedText") if isinstance(d.get("responseData"), dict) else None
    return [dict(text=haupt, nr="", bedeutung="", merkmale=[], unsicher=False)] if isinstance(haupt, str) else []


def _deepl_es_de(quelle, abruf, schluessel, code="es"):
    von = sprach_codes(code)["deepl_quelle"]
    if not von:
        raise UebersetzungsFehler("sprache_dienst")
    if not schluessel or not DEEPL_SCHLUESSEL.fullmatch(schluessel):
        raise UebersetzungsFehler("kein_schluessel")
    host = "api-free.deepl.com" if schluessel.endswith(":fx") else "api.deepl.com"
    kopf = {"Authorization": f"DeepL-Auth-Key {schluessel}", "Content-Type": "application/json"}
    body = json.dumps({"text": [quelle], "source_lang": von, "target_lang": "DE"})
    d = abruf(f"https://{host}/v2/translate", body.encode("utf-8"), kopf)
    liste = d.get("translations")
    if not isinstance(liste, list) or not liste or not isinstance(liste[0], dict):
        raise UebersetzungsFehler("format")
    return [dict(text=liste[0].get("text"), nr="", bedeutung="", merkmale=[], unsicher=False)]


# =============================================================================================
# KI-Bilder: Beschreibung der Szene ins Englische (das Bildmodell versteht praktisch nur Englisch).
# Gleiche Schutzregeln: nur nach Zustimmung, nur diese Beschreibung (≤ 300 Zeichen), nur MyMemory bzw. DeepL.
# =============================================================================================
MAX_BESCHREIBUNG = 300


def beschreibung_englisch(text, sprache="de", abruf=None, einstellungen=None, cache=True):
    """Beschreibung (Deutsch oder Spanisch) → Englisch. Gibt dict(text, dienst, aus_cache) zurück."""
    e = einstellungen or lade_einstellungen()
    if not e.get("zugestimmt"):
        raise UebersetzungsFehler("zustimmung")
    quelle = pruefe_quelle(_vorreinigen(str(text or ""))[:MAX_BESCHREIBUNG].strip())
    von = "es" if str(sprache).startswith("es") else "de"
    abruf = abruf or http_json
    dienst = "deepl" if e.get("deepl") and e.get("dienst") in ("auto", "deepl", None) and not im_browser() else "mymemory"
    schluessel = f"{dienst}|{von}-en|{quelle}"
    if cache:
        alt = _cache_holen(schluessel)
        if alt and alt.get("vorschlag"):
            return dict(text=alt["vorschlag"], dienst=dienst, aus_cache=True)
    if dienst == "deepl":
        if not DEEPL_SCHLUESSEL.fullmatch(e["deepl"]):
            raise UebersetzungsFehler("kein_schluessel")
        host = "api-free.deepl.com" if e["deepl"].endswith(":fx") else "api.deepl.com"
        d = abruf(f"https://{host}/v2/translate",
                  json.dumps({"text": [quelle], "source_lang": von.upper(), "target_lang": "EN-US"}).encode("utf-8"),
                  {"Authorization": f"DeepL-Auth-Key {e['deepl']}", "Content-Type": "application/json"})
        liste = d.get("translations")
        roh = liste[0].get("text") if isinstance(liste, list) and liste and isinstance(liste[0], dict) else None
    else:
        d = abruf("https://api.mymemory.translated.net/get?" + urllib.parse.urlencode({"q": quelle,
                                                                                       "langpair": f"{von}|en"}),
                  None, None)
        try:
            status = int(d.get("responseStatus"))
        except (TypeError, ValueError):
            status = 0
        if d.get("quotaFinished") is True or status == 429:
            raise UebersetzungsFehler("kontingent")
        if status != 200:
            raise UebersetzungsFehler("dienst", code=status or "?")
        roh = (d.get("responseData") or {}).get("translatedText") if isinstance(d.get("responseData"), dict) else None
    if not isinstance(roh, str) or re.search(r"<\s*[A-Za-z/!?]", html.unescape(roh[:600])):
        raise UebersetzungsFehler("format")                              # HTML/Skript in der Antwort → verwerfen
    englisch = _vorreinigen(roh).replace("{", "(").replace("}", ")")[:MAX_BESCHREIBUNG].strip()
    if not englisch:
        raise UebersetzungsFehler("format")
    if cache:
        _cache_ablegen(schluessel, dict(quelle=quelle, dienst=dienst, vorschlag=englisch, alternativen=[]))
    return dict(text=englisch, dienst=dienst, aus_cache=False)


# =============================================================================================
# Zwischenspeicher der Ergebnisse (im Benutzerordner)
# =============================================================================================
_cache_lock = threading.Lock()


def _cache_pfad():
    return daten_ordner() / "uebersetzungen.json"


def _cache_holen(schluessel):
    """Gemerktes Ergebnis oder None. Auch „nichts gefunden“ wird gemerkt (eine Woche), damit dasselbe Wort nicht
    immer wieder gesendet wird."""
    with _cache_lock:
        e = _lies_json(_cache_pfad()).get(schluessel)
    if not isinstance(e, dict) or not isinstance(e.get("ergebnis"), dict):
        return None
    try:
        alter = time.time() - float(e.get("zeit", 0))
    except (TypeError, ValueError):
        return None
    if alter < (CACHE_TAGE if e["ergebnis"].get("vorschlag") else 7) * 86400:
        return e["ergebnis"]
    return None


def _cache_ablegen(schluessel, ergebnis):
    with _cache_lock:
        d = _lies_json(_cache_pfad())
        d[schluessel] = dict(zeit=time.time(), ergebnis=ergebnis)
        if len(d) > CACHE_EINTRAEGE:
            for k in sorted(d, key=lambda x: d[x].get("zeit", 0) if isinstance(d[x], dict) else 0)[:len(d) - CACHE_EINTRAEGE]:
                d.pop(k, None)
        try:
            _schreibe_privat(_cache_pfad(), d)
        except OSError:
            pass


def cache_leeren():
    with _cache_lock:
        try:
            _cache_pfad().unlink()
            return True
        except OSError:
            return False


# =============================================================================================
# Haupteinstieg
# =============================================================================================
def _kann(dienst, codes, rueck=False):
    if dienst == "wiktionary":
        return bool(codes["abschnitt"] if rueck else codes["wiktionary"])
    if dienst == "deepl":
        return not im_browser() and bool(codes["deepl_quelle"] if rueck else codes["deepl"])
    return bool(codes["mymemory"])


def reihenfolge(dienst, quelle, schluessel, code="es", rueck=False):
    """Dienste in dieser Reihenfolge; einer, der die Sprache nicht kann (DeepL: kein Hindi/Plattdeutsch), entfällt."""
    codes = sprach_codes(code)
    if dienst == "auto":
        folge = ["wiktionary"] if len(quelle.split()) <= 2 else []
        if schluessel and _kann("deepl", codes, rueck):
            folge.append("deepl")
        elif _kann("mymemory", codes, rueck):
            folge.append("mymemory")
        folge = [d for d in folge if _kann(d, codes, rueck)] or (["wiktionary"] if _kann("wiktionary", codes, rueck)
                                                                 else [])
        if not folge:
            raise UebersetzungsFehler("sprache_dienst")
        return folge
    if dienst not in DIENSTE:
        raise UebersetzungsFehler("unbekannt")
    if dienst == "deepl" and im_browser():
        raise UebersetzungsFehler("dienst_rechner")
    if not _kann(dienst, codes, rueck):
        raise UebersetzungsFehler("sprache_dienst")
    return [dienst]


def _richtung(richtung):
    """"de-ja" → ("ja", False) · "ja-de" → ("ja", True)."""
    teile = str(richtung or "de-es").split("-")
    if len(teile) != 2 or "de" not in teile or teile[0] == teile[1]:
        raise UebersetzungsFehler("sprache_unbekannt")
    code, rueck = (teile[1], False) if teile[0] == "de" else (teile[0], True)
    sprach_codes(code)                                         # unbekannte Sprache → Fehler
    return code, rueck


def uebersetze(de, dienst=None, abruf=None, einstellungen=None, cache=True, richtung="de-es"):
    """Vorschlag für den Text einer Karte. Gibt dict(quelle, dienst, vorschlag, alternativen[{text, hinweis}],
    aus_cache) zurück; vorschlag = '' wenn kein Dienst etwas gefunden hat. Wirft UebersetzungsFehler.
    richtung="es-de": „de“ ist dann das Wort auf Spanisch, der Vorschlag deutsch (Reiter „Ideen“).
    richtung="de-ja" / "ja-de": andere Kartensprache (sprachen.py). Mit Umschrift (Üt) heißt der Vorschlag „Wort|Umschrift“.
    abruf(url, daten, kopf) → dict: nur für den Selbsttest ersetzbar (Standard: http_json)."""
    e = einstellungen or lade_einstellungen()
    if not e.get("zugestimmt"):
        raise UebersetzungsFehler("zustimmung")
    code, rueck = _richtung(richtung)
    quelle = pruefe_quelle(quelltext_ziel(de, code) if rueck else quelltext(de))
    abruf = abruf or http_json
    folge = reihenfolge(dienst or e.get("dienst") or "auto", quelle, e.get("deepl"), code, rueck)
    fehler = []
    for d in folge:
        if code == "es":                                       # Schlüssel wie bisher (gemerkte Ergebnisse bleiben gültig)
            cs = f"{d}|es-de|{quelle}" if rueck else f"{d}|{quelle}"
        else:
            cs = f"{d}|{code}-de|{quelle}" if rueck else f"{d}|de-{code}|{quelle}"
        if cache:
            alt = _cache_holen(cs)
            if alt and alt.get("vorschlag"):
                return dict(alt, aus_cache=True)
            if alt is not None:                                    # kürzlich nichts gefunden → nächster Dienst
                continue
        try:
            if d == "wiktionary":
                roh = _wiktionary_es_de(quelle, abruf, code) if rueck else _wiktionary(quelle, abruf, 0, code)
            elif d == "mymemory":
                roh = _mymemory_es_de(quelle, abruf, code) if rueck else _mymemory(quelle, abruf, code)
            else:
                roh = _deepl_es_de(quelle, abruf, e.get("deepl"), code) if rueck else \
                    _deepl(quelle, abruf, e.get("deepl"), code)
        except UebersetzungsFehler as f:
            fehler.append(f)
            continue
        sauber = []
        for r in roh:
            for t in kandidaten(r.get("text"), quelle, deutsch=rueck, code=code):    # „viejo / anciano“ = zwei Vorschläge
                hinweis = ", ".join(x for x in [(f"[{r['nr']}] " if r.get("nr") else "") + (r.get("bedeutung") or ""),
                                                *(r.get("merkmale") or [])] if x and x.strip())
                eintrag = dict(text=t, hinweis=_sauber(hinweis)[:120])
                um = _vorreinigen(r.get("umschrift") or "").strip(" .;:,")
                if um and not rueck and len(um) <= MAX_VORSCHLAG and _LATEIN.fullmatch(um) \
                        and um[0] not in _GEFAEHRLICH_ANFANG:
                    eintrag["umschrift"] = um
                sauber.append(eintrag)
        texte = _eindeutig([s["text"] for s in sauber])
        if not texte:
            if cache:
                _cache_ablegen(cs, dict(quelle=quelle, dienst=d, vorschlag="", alternativen=[]))
            continue
        alternativen = []
        for t in texte:
            alternativen.append(next(s for s in sauber if s["text"].casefold() == t.casefold()))
        vorschlag = " / ".join(texte[:2]) if DIENSTE[d]["art"] == "woerterbuch" else texte[0]
        if alternativen[0].get("umschrift"):                   # zweite Zeile der Karte: Umschrift („гусь|gusʹ“)
            vorschlag = f"{alternativen[0]['text']}|{alternativen[0]['umschrift']}"
        ergebnis = dict(quelle=quelle, dienst=d, vorschlag=vorschlag, alternativen=alternativen)
        if cache:
            _cache_ablegen(cs, ergebnis)
        return dict(ergebnis, aus_cache=False)
    if fehler and len(fehler) == len(folge):
        raise fehler[0]
    return dict(quelle=quelle, dienst=folge[-1] if folge else None, vorschlag="", alternativen=[], aus_cache=False)


def dienst_titel(dienst, sprache="en"):
    d = DIENSTE.get(dienst)
    return (d["titel"].get(sprache) or d["titel"]["de"]) if d else ""


if __name__ == "__main__":                                   # kleiner Test von Hand: python3 uebersetzer.py alt
    import argparse
    ap = argparse.ArgumentParser(description="Me Goos-ta Deutsch – Übersetzungsvorschlag (sendet ins Internet!)")
    ap.add_argument("text")
    ap.add_argument("--dienst", choices=STRATEGIEN, default="auto")
    a = ap.parse_args()
    try:
        print(json.dumps(uebersetze(a.text, a.dienst, einstellungen=dict(lade_einstellungen(), zugestimmt=True),
                                    cache=False), ensure_ascii=False, indent=1))
    except UebersetzungsFehler as fe:
        print(fe.text(), file=sys.stderr)
        sys.exit(1)
