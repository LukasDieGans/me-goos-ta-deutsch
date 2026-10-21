#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ME GOOS-TA DEUTSCH – Oberfläche                                     Version 2.2 (21.10.2026)
=============================================================================================
Startet eine lokale Oberfläche im Browser, von der aus alles bedient wird: Meine Karten, Tabelle (Vorder- und
Rückseite nebeneinander), Bildverbesserung, Schritt 1 „Bilder vorbereiten“ (auch viele auf einmal), Schritt 2
„Karten beschriften“ (mit automatischem Übersetzungsvorschlag), Erzeugen, Prüfen & Drucken, alle Schalter des
Generators, Werkzeuge und Hilfe – in Deutsch, Englisch oder Spanisch.

Start:    Doppelklick auf „Me Goos-ta Deutsch - Windows.cmd“ bzw. „… - Mac.command“ (eine Ebene höher) oder
          auf das Desktop-Symbol – das Startprogramm (starter.py) richtet beim ersten Start alles ein.
          Für Entwickler: python3 gans_ui.py
Beenden:  in der Oberfläche oben rechts ⏻ – oder Strg+C in der Konsole

Sicherheit (Details in SPEC.md, Abschnitt „Sicherheit“):
  • nur auf diesem Rechner erreichbar (127.0.0.1), Host- und Origin-Prüfung gegen DNS-Rebinding/CSRF
  • Zugang nur mit geheimem Startschlüssel → Sitzungs-Cookie (HttpOnly, SameSite=Strict); Schreibzugriffe
    zusätzlich mit Token-Kopfzeile; strenge Content-Security-Policy mit Nonce
  • Dateizugriffe nur auf einfache Dateinamen in den Projektordnern; Ordner-Einstellungen nur im Projekt- oder
    Benutzerordner; „Öffnen“ nur für harmlose Dateitypen
  • hochgeladene Bilder (Schritt 1, Gänse-Bild) werden geprüft und das Gänse-Bild neu gespeichert (ohne Metadaten)
  • automatische Übersetzung nur nach Zustimmung, nur über den Server (die Seite selbst spricht mit keinem fremden
    Rechner), Details in uebersetzer.py
Erweitern:
  • Neuer Schalter    → in gans_lernkarten.baue_parser() eintragen; erscheint hier automatisch.
  • Neue Erzeugungsart→ neue Auswahl bei --nur; erscheint automatisch als Knopf.
  • Neues Werkzeug    → Funktion mit @werkzeug(...) unten im Abschnitt „Werkzeuge“ anlegen.
  • Neue Sprache      → in SPRACHEN (gans_lernkarten.py) ergänzen und alle L(...)-Texte + ui/index.html erweitern.
"""

from __future__ import annotations

import argparse
import hmac
import html
import io
import json
import math
import mimetypes
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import time
import webbrowser
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import gans_lernkarten as gl  # noqa: E402
import ki_modelle  # noqa: E402
import uebersetzer  # noqa: E402

try:
    import sprachen  # noqa: E402
except ImportError:                                      # Datei fehlt (Testkopie) → nur Spanisch
    sprachen = None

L, T = gl.L, gl.T
UI_VERSION = "2.2 (21.10.2026)"
EINSTELLUNGEN = HIER / "ui_einstellungen.json"
UI_DATEI = HIER / "ui" / "index.html"
MAX_BILD = gl.MAX_DATEI_MB * 1024 * 1024
MAX_JSON = 2 * 1024 * 1024
TOKEN = secrets.token_urlsafe(32)              # für Schreibzugriffe (Kopfzeile X-GL-Token) und als Cookie-Wert
START_SCHLUESSEL = secrets.token_urlsafe(24)   # steht in der Start-Adresse; tauscht sich gegen das Cookie
SICHERE_ENDUNGEN = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".csv", ".zip", ".txt", ".md"}
OBERE_DATEIEN = ("Me Goos-ta Deutsch - Windows.cmd", "Me Goos-ta Deutsch - Mac.command", "Me Goos-ta Deutsch - Linux.sh",
                 "LIES MICH ZUERST.html", "README.md", "LICENSE.txt", "Me Goos-ta Deutsch - Android.html",
                 "Me Goos-ta Deutsch - iPhone.html", "Me Goos-ta Deutsch - Google Pixel.html")
GANS_ORDNER = HIER / "assets"
GANS_NAMEN = ("gans_hintergrund.png", "gans_hintergrund.jpg")     # in dieser Reihenfolge sucht der Generator
GANS_MAX_KANTE = 2400                                          # px – reicht für 300 dpi auf der Karte, PDFs bleiben klein
PORT = 0


def im_browser():
    """Läuft das Programm als Web-App im Browser (Pyodide)? Dann ohne Unterprozesse, ohne KI-Bilder, ohne Rechner-Wege."""
    return sys.platform == "emscripten"


def im_prozess():
    """Läufe ohne Unterprozess? Im Browser immer; am Rechner zum Prüfen mit MGD_IM_PROZESS=1."""
    return im_browser() or os.environ.get("MGD_IM_PROZESS") == "1"


# =============================================================================================
# Meldungen der Oberfläche (Server-Seite) in drei Sprachen
# =============================================================================================
TEXTE = {
    "nur_lokal": L("Nur auf diesem Rechner erreichbar", "Only reachable on this computer",
                   "Solo accesible en esta computadora"),
    "sitzung": L("Die Sitzung ist abgelaufen – öffne das Programm einfach neu über das Startprogramm.",
                 "The session has expired – just reopen the program from the start program.",
                 "La sesión expiró; vuelve a abrir el programa desde el programa de inicio y listo."),
    "unbekannt": L("Unbekannte Adresse", "Unknown address", "Dirección desconocida"),
    "nur_rechner": L("Das geht nur in der Fassung am Rechner – hier in der App ist alles andere für dich da.",
                     "That one works only in the computer version – everything else is all yours here in the app.",
                     "Eso solo funciona en la versión de la computadora; todo lo demás es tuyo aquí en la app."),
    "ungueltig": L("Diese Angabe passt noch nicht ganz – bitte kurz prüfen.",
                   "This entry doesn’t quite fit yet – please have a quick look.",
                   "Este dato todavía no encaja del todo; revísalo rápido."),
    "intern": L("Hoppla, da hat sich die Gans kurz verheddert ({fehler}) – versuch es einfach noch einmal.",
                "Oops, the goose got a little tangled up ({fehler}) – just give it another try.",
                "Uy, el ganso se enredó un momento ({fehler}); inténtalo otra vez."),
    "laeuft": L("Es läuft schon ein Vorgang – einen Moment Geduld, gleich ist er fertig.",
                "A task is already running – hang on a moment, it will be done soon.",
                "Ya hay una tarea en curso; un momento de paciencia, enseguida termina."),
    "ws_weg": L("Dieser Auftrag wartet nicht mehr – vielleicht ist er schon losgewatschelt.",
                "This task isn’t waiting any more – maybe it has already waddled off.",
                "Esta tarea ya no está esperando; quizá ya salió anadeando."),
    "ws_modell_weg": L("Das KI-Bildmodell ist nicht (mehr) da – installiere das Tool „KI-Bilder“ (Werkzeuge → Tools) "
                       "und starte die Gans neu.",
                       "The AI image model isn’t there (any more) – install the “AI images” tool (Tools → Optional tools) "
                       "and start the goose again.",
                       "El modelo de imágenes IA ya no está; instala la herramienta «Imágenes IA» (Herramientas → "
                       "Herramientas opcionales) y vuelve a iniciar el ganso."),
    "datei_fehlt": L("Die Datei ist nicht (mehr) da.", "That file isn’t there (any more).", "El archivo ya no está."),
    "gibt_es_nicht": L("{name} gibt es noch nicht – erzeuge es einfach zuerst.",
                       "{name} doesn’t exist yet – just generate it first.",
                       "{name} todavía no existe; genéralo primero y listo."),
    "ordner_aussen": L("„{label}“ muss im Projektordner oder in deinem Benutzerordner liegen.",
                       "“{label}” must be inside the project folder or your user folder.",
                       "«{label}» debe estar dentro de la carpeta del proyecto o de tu carpeta de usuario."),
    "csv_endung": L("Die Kartenliste muss eine .csv-Datei sein.", "The card list must be a .csv file.",
                    "La lista de cartas debe ser un archivo .csv."),
    "bild_endung": L("Das Gänse-Bild muss ein vorhandenes JPG-, PNG- oder WEBP-Bild sein.",
                     "The goose image must be an existing JPG, PNG or WEBP image.",
                     "La imagen del ganso debe ser una imagen JPG, PNG o WEBP existente."),
    "oeffnen_typ": L("Diesen Dateityp öffnet das Programm zu deiner Sicherheit lieber nicht.",
                     "For your safety, the program prefers not to open this file type.",
                     "Por tu seguridad, el programa prefiere no abrir este tipo de archivo."),
    "kein_programm": L("Auf diesem Rechner fehlt ein Programm, das diese Datei öffnet.",
                       "This computer doesn’t have a program that opens this file yet.",
                       "En esta computadora falta un programa que abra este archivo."),
    "anfrage_gross": L("Das ist zu viel auf einmal – bitte in kleineren Portionen.",
                       "That’s a lot at once – please send it in smaller portions.",
                       "Es demasiado de una vez; mejor en porciones más pequeñas."),
    "entwurf_fehlt": L("Dieses neue Bild ist nicht mehr da – füg es einfach noch einmal hinzu.",
                       "This new image isn’t there any more – just add it again.",
                       "Esta imagen nueva ya no está; agrégala otra vez y listo."),
    "bitte_pruefen": L("Fast geschafft – kümmere dich nur noch um die rot markierten Punkte.",
                       "Almost there – just take care of the points marked in red.",
                       "¡Ya casi! Solo falta atender los puntos marcados en rojo."),
    "bild_weg": L("{name} nach bilder/_entfernt/ verschoben.", "{name} moved to bilder/_entfernt/.",
                  "{name} se movió a bilder/_entfernt/."),
    "geoeffnet": L("Geöffnet: {pfad}", "Opened: {pfad}", "Abierto: {pfad}"),
    "zip_ok": L("{name} ist fertig ({kb} KB) – super!", "{name} is ready ({kb} KB) – great!",
                "{name} está listo ({kb} KB). ¡Súper!"),
    "sicherung_ok": L("Sicherung eingespielt: {karten} Karten, {dateien} Dateien – deine Gänse sind wieder ganz da!",
                      "Backup restored: {karten} cards, {dateien} files – your geese are all back!",
                      "Copia restaurada: {karten} cartas, {dateien} archivos. ¡Tus gansos volvieron completos!"),
    "sicherung_fremd": L("Das ist keine Sicherung der Handy-App. Karten vom Rechner holst du mit „Karten vom Rechner "
                         "übernehmen“ (Import).",
                         "This isn’t a backup of the phone app. To bring cards over from your computer, use “Take over "
                         "cards from the computer” (import).",
                         "Esto no es una copia de la app del celular. Para traer cartas de la computadora usa «Traer "
                         "cartas de la computadora» (importar)."),
    "sicherung_kaputt": L("Diese Sicherung lässt sich nicht lesen – nichts wurde verändert.",
                          "This backup can’t be read – nothing was changed.",
                          "No se puede leer esta copia; no se cambió nada."),
    "sicherung_gross": L("Die Sicherung ist zu groß (höchstens {mb} MB).", "The backup is too large (at most {mb} MB).",
                         "La copia es demasiado grande (máximo {mb} MB)."),
    "cache_ok": L("{n} aufbereitete Bilder gelöscht.", "{n} prepared images deleted.", "{n} imágenes preparadas eliminadas."),
    "beendet": L("Die Oberfläche macht Feierabend. Du kannst dieses Fenster schließen – bis bald!",
                 "The interface is calling it a day. You can close this window – see you soon!",
                 "La interfaz terminó su jornada. Ya puedes cerrar esta ventana. ¡Hasta pronto!"),
    "selbsttest": L("Selbsttest", "Self-test", "Autoprueba"),
    "erzeugen": L("Erzeugen", "Generate", "Generar"),
    "modell_laden": L("KI-Modell laden: {titel}", "Download AI model: {titel}", "Descargar modelo de IA: {titel}"),
    "verbessern": L("Bilder verbessern ({n})", "Enhance images ({n})", "Mejorar imágenes ({n})"),
    "keine_auswahl": L("Wähl mindestens ein Bild aus – dann geht’s los.", "Pick at least one image – then off we go.",
                       "Elige al menos una imagen y ¡manos a la obra!"),
    "gans_heic": L("HEIC/HEIF-Fotos (iPhone) kann das Programm leider nicht lesen – als JPG oder PNG gespeichert klappt "
                   "es sofort.",
                   "The program can’t read HEIC/HEIF photos (iPhone) – saved as JPG or PNG it works right away.",
                   "El programa no puede leer fotos HEIC/HEIF (iPhone); guardada como JPG o PNG funciona al instante."),
    "gans_unlesbar": L("Diese Datei lässt sich nicht als Bild lesen – probier es mit JPG, PNG, WEBP, GIF, BMP oder TIFF.",
                       "This file can’t be read as an image – try JPG, PNG, WEBP, GIF, BMP or TIFF.",
                       "Este archivo no se puede leer como imagen; prueba con JPG, PNG, WEBP, GIF, BMP o TIFF."),
    "gans_klein": L("Mit {w} × {h} px ist das Bild etwas klein für die Rückseite – ab 300 px an der kürzeren Seite wird "
                    "es schön.",
                    "At {w} × {h} px the image is a bit small for the back – from 300 px on the shorter side it looks "
                    "lovely.",
                    "Con {w} × {h} px la imagen es algo pequeña para el reverso; desde 300 px en el lado corto queda "
                    "preciosa."),
    "gans_pixel": L("Das Bild hat {mp} Megapixel – bis {max} klappt es, verkleinere es also ein wenig.",
                    "The image has {mp} megapixels – up to {max} works, so just shrink it a little.",
                    "La imagen tiene {mp} megapíxeles; hasta {max} funciona, así que redúcela un poco."),
    "gans_gross": L("Die Datei ist größer als {mb} MB – etwas verkleinert passt sie.",
                    "The file is larger than {mb} MB – a little smaller and it fits.",
                    "El archivo pesa más de {mb} MB; un poco más pequeño y entra."),
    "gans_kein_alt": L("Es gibt kein früheres Gänse-Bild.", "There is no earlier goose image.",
                       "No hay una imagen de ganso anterior."),
    "nicht_pruefbar": L("Trag zuerst ein Wort auf {zs} ein – dann prüft das Programm es gern.",
                        "Enter a {zs} word first – then the program is happy to check it.",
                        "Primero escribe una palabra en {zs}; luego el programa la revisa con gusto."),
    "karte_unbekannt": L("Diese Karte steht nicht (mehr) in der Kartenliste.", "This card is not in the card list (any more).",
                         "Esta carta ya no está en la lista."),
    # --- Karten-Editor: neues Bild für eine vorhandene Karte ---
    "e_ersetzt": L("Neues Bild für die Karte „{name}“ – Texte und Notiz bleiben, das bisherige Bild wird in "
                   "bilder/_entfernt/ aufgehoben.",
                   "New image for the card “{name}” – texts and note stay, the previous image is kept safe in "
                   "bilder/_entfernt/.",
                   "Imagen nueva para la carta «{name}»: los textos y la nota se quedan, y la imagen anterior se "
                   "guarda en bilder/_entfernt/."),
    "e_ergaenzt": L("Die Karte „{name}“ bekommt ihr fehlendes Bild zurück – prima!",
                    "The card “{name}” gets its missing image back – great!",
                    "La carta «{name}» recupera la imagen que le faltaba. ¡Genial!"),
    "e_umwandeln": L("Format {format} – wird als {ziel} gespeichert, damit die Karte ihren Dateinamen behält",
                     "Format {format} – saved as {ziel} so the card keeps its file name",
                     "Formato {format}: se guarda como {ziel} para que la carta conserve su nombre de archivo"),
    "e_gleich": L("Das ist genau das bisherige Bild dieser Karte – es ändert sich also nichts.",
                  "That’s exactly the card’s current image – so nothing changes.",
                  "Es exactamente la imagen actual de esta carta, así que nada cambia."),
    "sprache_laden": L("Sprache laden: {name}", "Download language: {name}", "Descargar idioma: {name}"),
    "sprache_fehlt": L("{name} ist noch nicht installiert – ein Klick im Tool „Sprachen“, und los geht’s.",
                       "{name} isn’t installed yet – one click in the “Languages” tool and off we go.",
                       "{name} aún no está instalado: un clic en la herramienta «Idiomas» y listo."),
    "ki_bild_laden": L("KI-Bildmodell laden", "Downloading the AI image model", "Descargando el modelo de imágenes IA"),
    "ki_bild_erzeugen": L("KI-Gans entsteht: {text}", "AI goose in the making: {text}", "Ganso IA en camino: {text}"),
    "ki_bild_fehlt": L("Dieses KI-Bild ist nicht mehr da – einfach noch einmal erzeugen.",
                       "This AI image isn’t there any more – just create it again.",
                       "Esta imagen IA ya no está; vuelve a crearla y listo."),
    "ki_modell_fehlt": L("Erst das KI-Bildmodell als Tool „KI-Bilder“ installieren (Werkzeuge → Tools) – danach geht "
                         "alles offline.",
                         "First install the AI image model as the “AI images” tool (Tools → Optional tools) – after that "
                         "everything works offline.",
                         "Primero instala el modelo de imágenes IA como herramienta «Imágenes IA» (Herramientas → "
                         "Herramientas opcionales); después todo funciona sin conexión."),
    "sicherung_fehlt": L("Das vorige Bild liegt nicht mehr in bilder/_entfernt/ – vielleicht wurde es schon verschoben.",
                         "The previous image is no longer in bilder/_entfernt/ – maybe it was moved already.",
                         "La imagen anterior ya no está en bilder/_entfernt/; quizá ya se movió."),
    "tool_unbekannt": L("Dieses Tool kennt das Programm nicht.", "The program doesn’t know this tool.",
                        "El programa no conoce esta herramienta."),
    "tool_beschaeftigt": L("„{titel}“ ist gerade beschäftigt (ein Auftrag läuft oder wartet) – danach lässt es sich "
                           "deinstallieren.",
                           "“{titel}” is busy right now (a task is running or waiting) – you can uninstall it afterwards.",
                           "«{titel}» está ocupada ahora (hay una tarea en curso o en espera); después podrás "
                           "desinstalarla."),
    "tool_bereit": L("Tool „{titel}“ ist bereit – gans schön praktisch!", "Tool “{titel}” is ready – honk if you like it!",
                     "¡La herramienta «{titel}» está lista: todo en orden en el corral!"),
    "tool_weg": L("„{titel}“ ist deinstalliert – {menge} wieder frei. Deine Karten und Bilder bleiben, und du kannst "
                  "das Tool jederzeit wieder installieren.",
                  "“{titel}” is uninstalled – {menge} free again. Your cards and images stay, and you can reinstall "
                  "the tool any time.",
                  "«{titel}» está desinstalada: {menge} libres de nuevo. Tus cartas e imágenes se quedan y puedes "
                  "volver a instalarla cuando quieras."),
    "tool_abgemeldet": L("„{titel}“ ist abgemeldet. Die Dateien liegen außerhalb des Datenordners und bleiben deshalb "
                         "unberührt.",
                         "“{titel}” is switched off. Its files live outside the data folder, so they stay untouched.",
                         "«{titel}» quedó desactivada. Sus archivos están fuera de la carpeta de datos y no se tocan."),
    "tool_laden": L("Tool installieren: {titel}", "Installing tool: {titel}", "Instalando herramienta: {titel}"),
    "tool_fehlt": L("Dafür braucht es das Tool „{titel}“ – einmal installieren, dann geht’s gans von allein weiter.",
                    "This needs the “{titel}” tool – install it once and the rest goes like a goose on water.",
                    "Para esto hace falta la herramienta «{titel}»: instálala una vez y todo sigue solito."),
    # --- Karten lernen (lernen.py) ---
    "lern_zurueck": L("Lernstand von {namen} zurückgesetzt – die Karte wurde geändert und startet beim Lernen frisch "
                      "wie ein Gänseküken.",
                      "Learning progress of {namen} reset – the card was changed and starts fresh like a gosling.",
                      "Se reinició el progreso de {namen}: la carta cambió y empieza de nuevo como un ansarino."),
    "lern_note": L("Bitte mit 1 (Nochmal), 2 (Schwer), 3 (Gut) oder 4 (Einfach) bewerten.",
                   "Please rate with 1 (Again), 2 (Hard), 3 (Good) or 4 (Easy).",
                   "Califica con 1 (Otra vez), 2 (Difícil), 3 (Bien) o 4 (Fácil)."),
    "lern_karte_fehlt": L("Diese Lernkarte gibt es nicht (mehr) – vielleicht wurde sie gerade geändert oder deaktiviert.",
                          "This learning card doesn’t exist (any more) – maybe it was just changed or switched off.",
                          "Esta carta de estudio ya no existe; quizá se acaba de cambiar o desactivar."),
    "lern_nichts_rueckgaengig": L("Hier gibt es nichts mehr rückgängig zu machen.", "Nothing left to undo here.",
                                  "Aquí ya no hay nada que deshacer."),
    "lern_stapel_name": L("Gib dem Stapel einen Namen – dann findest du ihn gans leicht wieder.",
                          "Give the deck a name – then it’s easy to find again.",
                          "Ponle un nombre al mazo; así lo encuentras fácilmente."),
    "lern_stapel_fehlt": L("Diesen Stapel gibt es nicht mehr.", "This deck no longer exists.", "Este mazo ya no existe."),
    "lern_import_kaputt": L("Das ist kein Lernstand von Me Goos-ta Deutsch (lernstand.json aus „Lernstand exportieren“).",
                            "This is not a Me Goos-ta Deutsch learning progress file (lernstand.json from “Export progress”).",
                            "Esto no es un progreso de Me Goos-ta Deutsch (lernstand.json de «Exportar progreso»)."),
    "lern_ungueltig": L("Das hat nicht geklappt – bitte die Eingaben prüfen.", "That didn’t work – please check the input.",
                        "Eso no funcionó; revisa los datos."),
    # Nach neuer Version suchen (nur auf Klick)
    "nv_kein_release": L("Für dieses Programm ist keine Download-Adresse eingetragen – die Gans weiß nicht, wo sie nachsehen soll.",
                         "No download address is set for this program – the goose doesn’t know where to look.",
                         "Este programa no tiene una dirección de descarga; el ganso no sabe dónde buscar."),
    "nv_netz": L("Keine Verbindung zum Internet – die Gans fliegt gerade offline. Später einfach nochmal klicken.",
                 "No internet connection – the goose is flying offline right now. Just click again later.",
                 "No hay conexión a internet; el ganso vuela sin red. Vuelve a hacer clic más tarde."),
    "nv_zeit": L("GitHub antwortet gerade nicht rechtzeitig. Gleich nochmal versuchen?",
                 "GitHub didn’t answer in time. Try again in a moment?",
                 "GitHub no respondió a tiempo. ¿Lo intentas de nuevo en un momento?"),
    "nv_grenze": L("GitHub braucht eine kleine Pause (Abfrage-Grenze erreicht). In einer Stunde nochmal klicken.",
                   "GitHub needs a little break (request limit reached). Click again in an hour.",
                   "GitHub necesita un pequeño descanso (límite de consultas). Vuelve a hacer clic en una hora."),
    "nv_noch_keins": L("Es gibt noch kein veröffentlichtes Release – du hast also die neueste Gans.",
                       "There’s no published release yet – so you have the newest goose.",
                       "Todavía no hay ninguna versión publicada; tienes el ganso más nuevo."),
    "nv_format": L("Die Antwort von GitHub sah unerwartet aus – bitte später nochmal versuchen.",
                   "GitHub’s answer looked unexpected – please try again later.",
                   "La respuesta de GitHub se veía extraña; inténtalo más tarde."),
}


def tx(code, **werte):
    return gl.mit_zs(gl.text_in(TEXTE[code]), werte)


def _meldung(code, stufe, **werte):
    """Prüfmeldung wie gl.pm(), aber mit einem Text aus TEXTE (für die Prüfliste der Oberfläche)."""
    return dict(stufe=stufe, code=code, werte=werte, text=tx(code, **werte))


class Meldung(Exception):
    """Fehler mit übersetztem Text (wird als 400 an die Oberfläche geschickt). extra: weitere Felder der Antwort
    (z. B. {code: "tool_fehlt", tool} → die Oberfläche fragt über brauchtTool() nach)."""
    def __init__(self, code, status=400, extra=None, **werte):
        super().__init__(tx(code, **werte))
        self.status, self.extra = status, extra or {}


# =============================================================================================
# Schalter-Schema: wird aus dem Parser des Generators gelesen (dadurch erscheinen neue Schalter automatisch)
# =============================================================================================
def _feld(action):
    if isinstance(action, argparse._StoreTrueAction):
        art = "schalter"
    elif action.choices:
        art = "auswahl"
    elif action.type in (int, float):
        art = "zahl"
    else:
        art = "text"
    default = action.default
    if isinstance(default, tuple):                       # z. B. Format (88.0, 63.0) → "88x63"
        default = "x".join(f"{v:g}" for v in default)
    elif isinstance(default, (set, frozenset)):
        default = ",".join(map(str, sorted(default)))
    art = getattr(action, "ui_art", None) or art                  # eigenes Bedienelement, z. B. 'gansbild'
    flag = next((o for o in action.option_strings if o.startswith("--")), action.option_strings[0])
    label = gl.text_in(getattr(action, "ui_label", None)) or flag.lstrip("-").replace("-", " ").capitalize()
    labels = getattr(action, "ui_auswahl_labels", {}) or {}
    return dict(
        dest=action.dest, flag=flag, art=art, label=label, intern=bool(getattr(action, "ui_intern", False)),
        hilfe=gl.text_in(getattr(action, "ui_hilfe", None)) if hasattr(action, "ui_hilfe") else (action.help or ""),
        einheit=getattr(action, "ui_einheit", None),
        default=default,
        schritt=1 if action.type is int else 0.5 if action.type is float else None,
        auswahl=[dict(wert=c, label=gl.text_in(labels.get(c)) or str(c).capitalize()) for c in (action.choices or [])],
    )


def _sichtbar(a):
    return a.option_strings and a.help != argparse.SUPPRESS and \
        not isinstance(a, (argparse._HelpAction, argparse._VersionAction))


def schema():
    parser = gl.baue_parser()
    gruppen = []
    for g in parser._action_groups:
        felder = [_feld(a) for a in g._group_actions if _sichtbar(a)]
        if not felder:
            continue
        titel = gl.text_in(getattr(g, "ui_titel", None)) or g.title
        gruppen.append(dict(titel=titel, beschreibung=gl.text_in(getattr(g, "ui_beschreibung", None)) or "",
                            erweitert=getattr(g, "ui_erweitert", False), reiter=getattr(g, "ui_reiter", "erzeugen"),
                            felder=felder))
    return gruppen


def alle_felder():
    return {f["dest"]: f for g in schema() for f in g["felder"]}


# =============================================================================================
# Einstellungen (zuletzt verwendete Schalter + Sprache der Oberfläche)
# =============================================================================================
_einst_lock = threading.RLock()     # Lesen + Ändern + Schreiben am Stück (gleichzeitige Anfragen verlieren sonst eine Änderung)
PFAD_FELDER = {"csv", "bilder", "ausgabe", "vorlagen_ordner", "gans_bild"}
NICHT_SPEICHERN = {"nur", "karten", "bild", "sprache"}   # gelten nur für einen Lauf (Sprache: Zielsprache bzw. Auswahl)


def _lies_datei():
    with _einst_lock:                                      # nie mitten im Ersetzen lesen (Windows sperrt sonst os.replace)
        try:
            return json.loads(EINSTELLUNGEN.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}


def _schreibe_datei(daten):
    with _einst_lock:
        tmp = EINSTELLUNGEN.with_name(EINSTELLUNGEN.name + ".tmp")
        tmp.write_text(json.dumps(daten, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, EINSTELLUNGEN)


def lade_sprache():
    s = _lies_datei().get("sprache")
    return s if s in gl.SPRACHEN else "en"


def speichere_sprache(s):
    if s not in gl.SPRACHEN:
        raise Meldung("ungueltig")
    with _einst_lock:
        daten = _lies_datei()
        daten["sprache"] = s
        _schreibe_datei(daten)
    return s


def lade_einstellungen():
    werte = _lies_datei().get("werte", {}) or {}
    felder = alle_felder()
    sauber = {k: v for k, v in werte.items() if k in felder and k not in NICHT_SPEICHERN}
    for k in list(sauber):                                   # unsichere Pfade aus alten Dateien ignorieren
        if k in PFAD_FELDER:
            try:
                pruefe_pfad(k, sauber[k], felder[k]["label"])
            except Meldung:
                sauber.pop(k)
    return sauber


def _im_erlaubten_bereich(pfad):
    p = Path(pfad).expanduser()
    if not p.is_absolute():
        p = HIER / p
    p = p.resolve()
    for basis in (HIER, Path.home().resolve()):
        try:
            p.relative_to(basis)
            return p
        except ValueError:
            continue
    return None


def pruefe_pfad(dest, wert, label):
    """Ordner-/Datei-Einstellungen dürfen nur auf den Projekt- oder Benutzerordner zeigen."""
    if wert in (None, ""):
        return wert
    text = str(wert)
    if "\x00" in text or text.startswith("\\\\") or text.startswith("//"):
        raise Meldung("ordner_aussen", label=label)          # keine Netzwerkpfade
    p = _im_erlaubten_bereich(text)
    if p is None:
        raise Meldung("ordner_aussen", label=label)
    if dest == "csv" and p.suffix.lower() != ".csv":
        raise Meldung("csv_endung")
    if dest == "gans_bild" and (p.suffix.lower() not in gl.BILD_ENDUNGEN or not p.is_file()):
        raise Meldung("bild_endung")
    return wert


def speichere_einstellungen(werte):
    felder = alle_felder()
    sauber = {}
    for k, v in (werte or {}).items():
        if k not in felder or k in NICHT_SPEICHERN:
            continue
        if isinstance(v, str) and len(v) > 500:
            raise Meldung("ungueltig")
        if k in PFAD_FELDER:
            pruefe_pfad(k, v, felder[k]["label"])
        sauber[k] = v
    with _einst_lock:
        daten = _lies_datei()
        daten["werte"] = sauber
        _schreibe_datei(daten)
    return sauber


# =============================================================================================
# Zielsprache (Rückseite + Richtung der Übersetzung): sprachen.py, Standard es, nur installierte wählbar
# =============================================================================================
def zielsprache():
    if not sprachen:
        return "es"
    return sprachen.zielsprache(_lies_datei())


def zielsprache_info():
    zs = zielsprache()
    if not sprachen:
        return dict(code="es", kurz="ES", namen=L("Spanisch", "Spanish", "español"), name=gl.text_in(
            L("Spanisch", "Spanish", "español")), richtung="ltr", installiert=["es"], sprachen=[])
    i = sprachen.info(zs, gl.sprache())
    return dict(code=zs, kurz=i["kurz"], namen=i["namen"], name=i["name"], eigenname=i["eigenname"],
                richtung=i["richtung"], umbruch=i["umbruch"], sonderzeichen=i["sonderzeichen"],
                installiert=sprachen.installierte(), sprachen=sprachen.liste(gl.sprache()))


def _zielsprache_aufraeumen():
    """Sprache entfernt: war sie die Zielsprache → zurück auf es (Kartentexte bleiben in karten.csv)."""
    with _einst_lock:
        daten = _lies_datei()
        code = daten.get("zielsprache")
        if code and not (sprachen and code in sprachen.SPRACHEN and sprachen.installiert(code)):
            daten.pop("zielsprache", None)
            _schreibe_datei(daten)
            _vorschau_cache.clear()
            return True
    return False


def setze_zielsprache(code):
    """Nur eine installierte Sprache wird Zielsprache; fehlt sie → 409 tool_fehlt (Tool „Sprachen“, Teil = code)."""
    code = str(code or "")
    if code == "es" or (sprachen and code in sprachen.SPRACHEN):
        if code != "es" and not sprachen.installiert(code):
            raise Meldung("sprache_fehlt", status=409, extra=dict(code="tool_fehlt", tool="sprachen", teil=code),
                          name=sprachen.name(code, gl.sprache()))
        with _einst_lock:
            daten = _lies_datei()
            if code == "es":
                daten.pop("zielsprache", None)
            else:
                daten["zielsprache"] = code
            _schreibe_datei(daten)
        _vorschau_cache.clear()
        return zielsprache_info()
    raise Meldung("ungueltig")


# =============================================================================================
# Farben & Darstellung: Schemata + eigene Farben (Standard „Gänsehimmel“ = die festen Farben der Seite → es wird
# nichts überschrieben). Der Server setzt die Variablen schon beim Ausliefern der Seite (kein Aufblitzen).
# =============================================================================================
FARB_BASIS = ("hintergrund", "flaechen", "text", "akzent", "linien", "erfolg", "fehler")
FARB_STANDARD = dict(hintergrund="#E8F2FA", flaechen="#FFFFFF", text="#1B2D4F", akzent="#F6A94B", linien="#C9DCEB",
                     erfolg="#1E8A50", fehler="#C9383C")
FARB_SCHEMEN = {
    "nacht": dict(hintergrund="#0F1A2E", flaechen="#17243D", text="#E6EEF8", akzent="#F6A94B", linien="#2F4468",
                  erfolg="#5FD38E", fehler="#FF7A7E"),
    "wiese": dict(hintergrund="#EEF5E6", flaechen="#FFFFFF", text="#20361F", akzent="#E8A33A", linien="#C5D9B3",
                  erfolg="#1E7F3E", fehler="#C0392B"),
    "kontrast": dict(hintergrund="#FFFFFF", flaechen="#FFFFFF", text="#000000", akzent="#FFB000", linien="#000000",
                     erfolg="#006B2D", fehler="#B00020"),
}
FARB_EXTRA = {"kontrast": {"nacht-2": "#1A1A1A", "nacht-3": "#3A3A3A"}}
FARB_IDS = ("himmel", "nacht", "wiese", "kontrast", "system", "eigen")
FARB_HEX = re.compile(r"#[0-9a-fA-F]{6}")             # nur mit fullmatch()
# feste Werte der Seite (für die Kontrastprüfung des Standards)
FARB_LITERAL = {"himmel": "#E8F2FA", "feder": "#FFFFFF", "nacht": "#1B2D4F", "schnabel": "#F6A94B", "auf-schnabel": "#1B2D4F"}


def _frgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def _fhex(c):
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(x)))) for x in c)


def _fmix(a, b, w):
    """Mischung: Anteil w von a, der Rest von b."""
    ra, rb = _frgb(a), _frgb(b)
    return _fhex([ra[i] * w + rb[i] * (1 - w) for i in range(3)])


def _flum(h):
    def k(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = _frgb(h)
    return 0.2126 * k(r) + 0.7152 * k(g) + 0.0722 * k(b)


def farb_kontrast(a, b):
    la, lb = sorted((_flum(a), _flum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _fbeste(gegen, kandidaten, ziel=4.5):
    """Erste Schriftfarbe, die auf allen Flächen in `gegen` mindestens `ziel` : 1 erreicht (sonst die beste)."""
    gegen = [gegen] if isinstance(gegen, str) else list(gegen)
    wert = lambda c: min(farb_kontrast(c, g) for g in gegen)    # noqa: E731
    for c in kandidaten:
        if wert(c) >= ziel:
            return c
    return max(kandidaten, key=wert)


def farb_ableitung(p):
    """Alle Seiten-Variablen aus den 7 Grundfarben (reine Rechnung, funktioniert überall – kein color-mix nötig)."""
    bg, fl, tx, ak, li, gu, fe = (p[k] for k in FARB_BASIS)
    hell = _flum(bg) > 0.4
    sw, ws = "#000000", "#FFFFFF"
    auf_nacht = _fbeste(tx, [fl, bg, ws, sw])
    pol = sw if hell else ws                                  # Akzent als Schrift: so weit abdunkeln/aufhellen, bis es lesbar ist
    akzent_text = _fbeste(bg, [_fmix(ak, pol, w / 10) for w in range(10, -1, -1)])
    return {
        "akzent-text": akzent_text,
        "himmel": bg, "feder": fl, "nacht": tx,
        "nacht-2": _fmix(tx, bg, .78), "nacht-3": _fmix(tx, bg, .58),
        "wasser": _fmix(bg, tx, .82), "wasser-hell": _fmix(bg, fl, .5),
        "schnabel": ak, "schnabel-dunkel": _fmix(ak, sw, .9) if hell else _fmix(ak, ws, .78),
        "linie": li, "gut": gu, "gut-flaeche": _fmix(gu, fl, .13),
        "schlecht": fe, "fehler-flaeche": _fmix(fe, fl, .11),
        "warn": _fmix(ak, sw, .6) if hell else _fmix(ak, ws, .6),
        "warn-flaeche": _fmix(ak, fl, .12), "warn-chip": _fmix(ak, fl, .3), "warn-chip-2": _fmix(ak, fl, .2),
        "fehler-text": _fmix(fe, sw, .7) if hell else _fmix(fe, ws, .5),
        "flaeche-aus": _fmix(bg, fl, .4), "flaeche-leise": _fmix(bg, fl, .25), "flaeche-ablage": _fmix(ak, fl, .06),
        "spur": _fmix(li, tx, .85), "punkt": ws if hell else tx, "doku-text": _fmix(tx, bg, .92),
        "auf-nacht": auf_nacht, "auf-schnabel": _fbeste(ak, [tx, bg, sw, ws]),
        "auf-signal": _fbeste([gu, fe], [fl, ws, bg, sw]),
        "schatten": ", ".join(str(x) for x in (_frgb(tx) if hell else (0, 0, 0))),
        "glas": "rgba(%d, %d, %d, .92)" % _frgb(fl),
        "toast-rand": "rgba(%d, %d, %d, .5)" % _frgb(auf_nacht),
        "code-bg": tx if _flum(tx) < 0.3 else _fmix(bg, sw, .45),
        "farbschema": "light" if hell else "dark",
    }


def farben_pruefen(schema, eigene, streng=True):
    """Prüft Schema und eigene Farben (nur #RRGGBB). streng → Meldung „ungueltig“, sonst stilles Zurück auf Standard."""
    if schema not in FARB_IDS:
        if streng and schema not in (None, ""):
            raise Meldung("ungueltig")
        schema = "himmel"
    sauber = {}
    if isinstance(eigene, dict):
        for k, v in eigene.items():
            if k in FARB_BASIS and isinstance(v, str) and FARB_HEX.fullmatch(v):
                sauber[k] = v.upper()
            elif streng:
                raise Meldung("ungueltig")
    elif eigene not in (None, {}) and streng:
        raise Meldung("ungueltig")
    return schema, sauber


def lade_farben():
    d = _lies_datei().get("farben")
    d = d if isinstance(d, dict) else {}
    return farben_pruefen(d.get("schema"), d.get("eigene"), streng=False)


def farben_variablen(schema, eigene):
    """Variablen, die das Schema gegenüber den festen Seitenfarben überschreibt (Standard: keine)."""
    if schema in FARB_SCHEMEN:
        v = farb_ableitung(FARB_SCHEMEN[schema])
        v.update(FARB_EXTRA.get(schema, {}))
        return v
    if schema == "eigen" and eigene:
        v, d = farb_ableitung({**FARB_STANDARD, **eigene}), farb_ableitung(FARB_STANDARD)
        return {k: x for k, x in v.items() if x != d[k]}      # nur, was sich wirklich ändert → „unverändert = Standard“
    return {}


def _fcss(v):
    return "".join(f"--{k}:{x};" for k, x in v.items())


def farben_info(schema=None, eigene=None):
    if schema is None:
        schema, eigene = lade_farben()
    v = farben_variablen(schema, eigene)
    css = ":root{" + _fcss(v) + "}" if v else ""
    if schema == "system":
        css = "@media (prefers-color-scheme: dark){:root{" + _fcss(farben_variablen("nacht", {})) + "}}"
    wirksam = lambda n: v.get(n, FARB_LITERAL.get(n))                 # noqa: E731
    paare = [("text_hintergrund", "nacht", "himmel"), ("text_flaechen", "nacht", "feder"),
             ("knopf", "auf-schnabel", "schnabel")]
    kontrast = []
    for name, a, b2 in paare:
        k = farb_kontrast(wirksam(a), wirksam(b2))
        kontrast.append(dict(name=name, wert=round(k, 1), ok=k >= 4.5))
    if schema == "system":
        n = farben_variablen("nacht", {})
        for name, a, b2 in paare:
            k = farb_kontrast(n[a], n[b2])
            kontrast.append(dict(name=name + "_dunkel", wert=round(k, 1), ok=k >= 4.5))
    eig = {**FARB_STANDARD, **(eigene or {})}
    vorschau = {"himmel": FARB_STANDARD, "eigen": eig, **FARB_SCHEMEN}
    kacheln = []
    for i in FARB_IDS:
        if i == "system":
            fb = [FARB_STANDARD["hintergrund"], FARB_SCHEMEN["nacht"]["hintergrund"], FARB_STANDARD["text"],
                  FARB_SCHEMEN["nacht"]["text"]]
        else:
            q = vorschau[i]
            fb = [q["hintergrund"], q["flaechen"], q["text"], q["akzent"]]
        kacheln.append(dict(id=i, farben=fb))
    if schema == "system":
        meta = ('<meta name="theme-color" content="%s" media="(prefers-color-scheme: light)">'
                '<meta name="theme-color" content="%s" media="(prefers-color-scheme: dark)">'
                % ("#FFFFFF", farben_variablen("nacht", {})["feder"]))
    else:
        meta = '<meta name="theme-color" content="%s">' % v.get("feder", "#FFFFFF")
    return dict(schema=schema, eigene=eig, standard=FARB_STANDARD, css=css, meta=meta,
                kontrast=kontrast, schemata=kacheln)


def speichere_farben(schema, eigene):
    schema, eigene = farben_pruefen(schema, eigene)
    with _einst_lock:
        daten = _lies_datei()
        if schema == "himmel" and not eigene:
            daten.pop("farben", None)
        else:
            daten["farben"] = {"schema": schema, "eigene": eigene}
        _schreibe_datei(daten)
    return farben_info(schema, eigene)


def argv_aus(werte, extra=None):
    """Baut die Kommandozeile für den Generator aus den Werten der Oberfläche (nur bekannte Schalter).
    Werte werden als --schalter=wert übergeben, damit ein Wert nie als eigener Schalter gelesen werden kann."""
    felder = alle_felder()
    werte = dict(werte or {})
    werte.update(extra or {})
    argv = []
    for dest, f in felder.items():
        if dest not in werte:
            continue
        v = werte[dest]
        if isinstance(v, (list, tuple)):                       # mehrfach erlaubte Schalter, z. B. --bild
            argv += [f"{f['flag']}={str(x).strip()}" for x in v if str(x).strip()]
            continue
        if f["art"] == "schalter":
            if v in (True, "true", "1", 1, "on"):
                argv.append(f["flag"])
            continue
        if v is None or str(v).strip() == "" or str(v).strip() == str(f["default"] if f["default"] is not None else ""):
            continue
        if f["art"] == "zahl":
            try:
                if float(str(v).replace(",", ".")) == float(f["default"]):
                    continue
            except (TypeError, ValueError):
                pass
            v = str(v).replace(",", ".")
        argv.append(f"{f['flag']}={str(v).strip()}")
    return argv


def parse(argv):
    """Prüft die Kommandozeile mit dem echten Parser. Gibt (Namespace, Fehlertext) zurück."""
    parser = gl.baue_parser()
    parser.exit = lambda status=0, message=None: (_ for _ in ()).throw(ValueError(message or ""))
    parser.error = lambda message: (_ for _ in ()).throw(ValueError(message))
    try:
        return parser.parse_args(argv), None
    except ValueError as e:
        text = str(e).strip()
        m = re.match(r"argument (--[\w-]+): (.+)", text, re.S)          # „argument --karten: …“ → „Nur diese Karten: …“
        act = next((a for a in parser._actions if m and m.group(1) in a.option_strings), None)
        if act is not None and getattr(act, "ui_label", None):
            text = f"{gl.text_in(act.ui_label)}: {m.group(2)}"
        return None, text


def aktuelle_konfig():
    a, _ = parse(argv_aus(lade_einstellungen()))
    if a is None:
        a, _ = parse([])
    return a, gl.konfig_aus(a)


def befehlszeile(argv, skript="gans_lernkarten.py"):
    def q(t):
        return f'"{t}"' if re.search(r'[\s;&|"<>^%]', t) else t
    return " ".join(["python3", skript] + [q(t) for t in argv])


# =============================================================================================
# Pfade, sichere Dateinamen
# =============================================================================================
def pfade():
    a, _ = aktuelle_konfig()
    return Path(a.csv), Path(a.bilder), Path(a.ausgabe), Path(a.vorlagen_ordner)


def sicher_in(basis, name):
    """Datei 'name' im Ordner 'basis' – nur einfache Namen, ohne Ausbruch aus dem Ordner (auch nicht per Link)."""
    if not gl.sicherer_name(name):
        raise Meldung("ungueltig")
    basis = Path(basis).resolve()
    ziel = (basis / name).resolve()
    if ziel.parent != basis:
        raise Meldung("ungueltig")
    return ziel


# =============================================================================================
# Karten
# =============================================================================================
def lies_bericht(ausgabe):
    try:
        return json.loads((ausgabe / "bericht.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _bericht_vergessen(ausgabe, name):
    """Neues Bild → die Bildqualität aus dem letzten Lauf gilt nicht mehr (sonst zeigt „Meine Karten“ alte ppi)."""
    pfad = Path(ausgabe) / "bericht.json"
    try:
        b = json.loads(pfad.read_text(encoding="utf-8"))
        if b.get("karten", {}).pop(name, None) is not None:
            pfad.write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
    except (OSError, ValueError, AttributeError):
        pass


def _ist_verbessert(pfad, cfg, fit, methode, cache_dir):
    """Liegt die fertig verbesserte Vorderseite für die jetzigen Einstellungen im Zwischenspeicher?"""
    try:
        key = gl.cache_schluessel(pfad, cfg, fit, methode)
    except OSError:
        return False
    return (cache_dir / f"{key}.jpg").is_file() and (cache_dir / f"{key}.json").is_file()


def karten_daten():
    a, cfg = aktuelle_konfig()
    csv_pfad, bilder, ausgabe = Path(a.csv), Path(a.bilder), Path(a.ausgabe)
    methode = gl.ki_methode(cfg.ki)
    spalten, zeilen, _ = gl.lies_csv(csv_pfad)
    gueltig, meldungen = gl.lies_karten(csv_pfad, bilder, strukturiert=True)
    nr_von = {}
    for k in gueltig:
        nr_von.setdefault(k["bild"], k["nr"])
    bericht = lies_bericht(ausgabe).get("karten", {})
    liste, belegt = [], set()
    zs = zielsprache()
    codes = [c for c in (sprachen.SPRACHEN if sprachen else ["es"])]
    for z in zeilen:
        roh = z.get("bild", "")
        aktiv = not roh.startswith("#")
        bild = roh.lstrip("#").strip()
        belegt.add(bild)
        extra = {k: v for k, v in z.items() if k not in gl.KARTEN_SPALTEN}
        existiert = gl.sicherer_name(bild) and (bilder / bild).is_file()
        fit = z.get("fit", "") or "contain"
        rueckseiten = {c: z.get(c, "") for c in codes if c == "es" or z.get(c, "").strip()}
        uebersetzungen = {c: s for c in codes for s in [gl.uebersetzung_status(
            z.get("uebersetzung" if c == "es" else f"uebersetzung_{c}"))] if s}
        # „es“/„uebersetzung“ = Rückseite und Prüfstatus in der Zielsprache (bei es wie bisher); alle Sprachen in
        # „rueckseiten“/„uebersetzungen“ (beim Speichern zurück über _zeile_aus)
        liste.append(dict(bild=bild, aktiv=aktiv, de=z.get("de", ""), es=z.get(zs, ""), notiz=z.get("notiz", ""),
                          fit=fit, extra=extra, existiert=bool(existiert),
                          nr=nr_von.get(bild) if aktiv else None, bericht=bericht.get(bild),
                          rueckseiten=rueckseiten, uebersetzungen=uebersetzungen,
                          offen=bool(existiert) and not z.get(zs, "").strip(),
                          uebersetzung=uebersetzungen.get(zs),
                          verbessert=bool(existiert) and _ist_verbessert(bilder / bild, cfg, fit if fit in ("contain", "cover")
                                                                         else "contain", methode, ausgabe / ".cache")))
    ohne = sorted(p.name for p in bilder.glob("*") if p.is_file() and p.suffix.lower() in gl.BILD_ENDUNGEN
                  and p.name not in belegt) if bilder.exists() else []
    lern = _lern_karten_info(zeilen, bilder)
    if lern is not None:                                     # Tool „lernen“: Stand je Karte (sonst kein Feld)
        for k in liste:
            k["lernen"] = lern.get(k["bild"])
    return dict(spalten=spalten, karten=liste, ohne_karte=ohne, zielsprache=zs,
                meldungen=[m for m in meldungen if m["code"] != "ohne_karte"],
                csv=str(csv_pfad), bilder=str(bilder))


def _zeile_aus(k, zs=None):
    """Karte (wie karten_daten) → CSV-Zeile. „es“/„uebersetzung“ gelten für die Zielsprache zs; die übrigen
    Sprachen kommen aus „rueckseiten“/„uebersetzungen“ (zs="es": Spalten roh, z. B. beim Import)."""
    zs = zs or zielsprache()
    bild = str(k.get("bild", "")).strip().lstrip("#").strip()
    if not gl.sicherer_name(bild):
        raise Meldung("ungueltig")
    rueck = dict(k["rueckseiten"]) if isinstance(k.get("rueckseiten"), dict) else {}
    stati = dict(k["uebersetzungen"]) if isinstance(k.get("uebersetzungen"), dict) else {}
    rueck[zs], stati[zs] = k.get("es", ""), k.get("uebersetzung")
    k = dict(k, rueckseiten=rueck, uebersetzungen=stati)
    z = {"bild": ("" if k.get("aktiv", True) else "#") + bild, "de": k.get("de", ""), "es": rueck.get("es", ""),
         "notiz": k.get("notiz", "")}
    fit = (k.get("fit") or "contain").strip()
    if fit not in ("contain", "cover"):
        fit = "contain"
    if fit != "contain":
        z["fit"] = fit
    status = gl.uebersetzung_status(stati.get("es"))
    if status:
        z["uebersetzung"] = gl.UEBERSETZUNG_WERT[status]
    for sp, v in (k.get("extra") or {}).items():
        if sp not in gl.KARTEN_SPALTEN and re.fullmatch(r"[a-z0-9_ -]{1,40}", str(sp)):
            z[str(sp)] = v
    if sprachen and isinstance(k.get("rueckseiten"), dict):     # weitere Rückseiten: Spalte je Sprachcode
        for c, v in k["rueckseiten"].items():
            if c in sprachen.SPRACHEN and c != "es":         # es kommt aus dem Feld „es“
                z[c] = v
    if sprachen and isinstance(k.get("uebersetzungen"), dict):  # Status je Sprache (es: Spalte „uebersetzung“)
        for c, v in k["uebersetzungen"].items():
            if c in sprachen.SPRACHEN and c != "es":
                s = gl.uebersetzung_status(v)
                z[f"uebersetzung_{c}"] = gl.UEBERSETZUNG_WERT[s] if s else ""
    return {kk: " ".join(str(vv or "").split())[:300] for kk, vv in z.items()}


_csv_lock = threading.Lock()


def _als_karte(z, zs):
    """CSV-Zeile → Felder es/uebersetzung (Zielsprache) + rueckseiten/uebersetzungen (alle Sprachen)."""
    codes = list(sprachen.SPRACHEN) if sprachen else ["es"]
    rueck = {c: z.get(c, "") for c in codes if c == "es" or z.get(c, "").strip()}
    stati = {c: s for c in codes for s in [gl.uebersetzung_status(
        z.get("uebersetzung" if c == "es" else f"uebersetzung_{c}"))] if s}
    return dict(es=z.get(zs, ""), uebersetzung=stati.get(zs), rueckseiten=rueck, uebersetzungen=stati)


def speichere_karten(daten):
    csv_pfad, _, _, _ = pfade()
    with _csv_lock:
        spalten, _, _ = gl.lies_csv(csv_pfad)
        alt = {k["bild"]: k for k in karten_daten()["karten"]}     # fehlende Rückseiten (ältere Seite) behalten
        karten = [dict(k, **{f: alt[k["bild"]][f] for f in ("rueckseiten", "uebersetzungen")
                             if f not in k and k.get("bild") in alt}) for k in daten.get("karten", [])]
        zeilen = [_zeile_aus(k) for k in karten if str(k.get("bild", "")).strip()]
        gl.schreibe_csv(csv_pfad, zeilen, spalten)
    _vorschau_cache.clear()
    return karten_daten()


def setze_karte(bild, werte, anlegen=True):
    """Ändert oder ergänzt eine einzelne Zeile der Kartenliste (Schritt 1 und 2)."""
    csv_pfad, _, _, _ = pfade()
    with _csv_lock:
        spalten, zeilen, _ = gl.lies_csv(csv_pfad)
        zs = zielsprache()
        neu = []
        gefunden = False
        for z in zeilen:
            roh = z.get("bild", "")
            if roh.lstrip("#").strip() == bild and not gefunden:
                gefunden = True
                aktiv = not roh.startswith("#")
                k = dict(z, bild=bild, aktiv=aktiv, extra={kk: vv for kk, vv in z.items() if kk not in gl.KARTEN_SPALTEN})
                k.update(_als_karte(z, zs))
                k.update({kk: vv for kk, vv in werte.items() if vv is not None})
                neu.append(_zeile_aus(k))
            else:
                neu.append(z)
        if not gefunden and anlegen:
            neu.append(_zeile_aus(dict(bild=bild, aktiv=True, **{k: v for k, v in werte.items() if v is not None})))
        gl.schreibe_csv(csv_pfad, neu, spalten)
    _vorschau_cache.clear()
    if gefunden and lernen and werte.get("bild") and werte["bild"] != bild:      # Stand wandert mit (Bild ändern)
        _lernstand().umbenennen(bild, werte["bild"])


def _karten_zeile(bild):
    """Zeile der Kartenliste zu einem Bildnamen (oder None) – ohne die aufwendige Auswertung von karten_daten()."""
    _, zeilen, _ = gl.lies_csv(pfade()[0])
    return next((z for z in zeilen if z.get("bild", "").lstrip("#").strip() == bild), None)


# =============================================================================================
# Vorschau (Vorder-/Rückseite als Bild, mit den aktuellen Einstellungen)
# =============================================================================================
_vorschau_cache: dict = {}
_vorschau_lock = threading.Lock()


def _gans_stempel(cfg):
    """Änderungszeit des Gänse-Bildes – damit die Vorschau ein neu geladenes Bild sofort zeigt."""
    try:
        return Path(cfg.gans_bild).stat().st_mtime_ns if cfg.gans_bild else 0
    except OSError:
        return 0


BEISPIEL_WORT = {"en": "hello / hi", "nds": "moin / moin moin", "fr": "bonjour / salut", "it": "ciao / buongiorno",
                 "tr": "merhaba / selam", "sv": "hej / hallå", "no": "hei / hallo", "pl": "cześć / dzień dobry",
                 "ru": "привет / здравствуй", "ja": "こんにちは / やあ", "zh": "你好 / 您好", "ko": "안녕하세요 / 안녕",
                 "hi": "नमस्ते / हैलो", "ar": "مرحبا / أهلا"}      # Gänse-Bild-Vorschau ohne eigenes Wort


def rueckseite(es):
    """Vorschau nur der Rückseite (ohne Kartenbild) – für das Gänse-Bild in den Einstellungen."""
    a, cfg = aktuelle_konfig()
    cfg.sprache = zielsprache()
    es = " ".join(str(es or "").split())[:120] or BEISPIEL_WORT.get(cfg.sprache, "¡hola! / ¿qué tal?")
    schluessel = ("rueckseite", es, json.dumps(cfg.__dict__, sort_keys=True, default=str), _gans_stempel(cfg))
    with _vorschau_lock:
        if schluessel in _vorschau_cache:
            return _vorschau_cache[schluessel]
    gl.registriere_schriften()
    erg = gl.vorschau_png(dict(nr=0, bild="", pfad=None, de="", es=es, notiz="", fit="contain"), cfg, seite="hinten",
                          dpi=110)
    if erg:
        with _vorschau_lock:
            _vorschau_cache[schluessel] = (erg[0], erg[1], False)
        return erg[0], erg[1], False
    return None


def vorschau(bild, es, fit, seite):
    a, cfg = aktuelle_konfig()
    cfg.sprache = zielsprache()
    pfad = sicher_in(a.bilder, bild)
    if not pfad.is_file():
        return None
    schluessel = (bild, pfad.stat().st_mtime_ns, es, fit, seite, json.dumps(cfg.__dict__, sort_keys=True, default=str),
                  _gans_stempel(cfg))
    with _vorschau_lock:
        if schluessel in _vorschau_cache:
            return _vorschau_cache[schluessel]
    gl.registriere_schriften()
    karte = dict(nr=0, bild=bild, pfad=pfad, de="", es=es or " ", notiz="", fit=fit if fit in ("contain", "cover") else "contain")
    erg = gl.vorschau_png(karte, cfg, seite=seite, dpi=110, cache_dir=Path(a.ausgabe) / ".cache")
    if erg:
        erg = (erg[0], erg[1], bool(karte.get("schnellvorschau")))
    with _vorschau_lock:
        if len(_vorschau_cache) > 300:
            _vorschau_cache.clear()
        if erg and not erg[2]:
            _vorschau_cache[schluessel] = erg
    return erg


# =============================================================================================
# Schritt 1: neue Bilder („Entwürfe“) prüfen, drehen, benennen und übernehmen
# =============================================================================================
_entwurf_lock = threading.Lock()


def entwurf_ordner():
    _, _, ausgabe, _ = pfade()
    d = ausgabe / ".entwuerfe"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _entwurf_pfade(eid):
    if not re.fullmatch(r"[0-9a-f]{16}", str(eid or "")):
        raise Meldung("entwurf_fehlt")
    d = entwurf_ordner()
    bild, meta = d / f"{eid}.bild", d / f"{eid}.json"
    if not bild.is_file() or not meta.is_file():
        raise Meldung("entwurf_fehlt")
    return bild, meta


def _entwurf_meta(eid):
    _, meta = _entwurf_pfade(eid)
    return json.loads(meta.read_text(encoding="utf-8"))


_ENDUNG_FORMAT = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP"}


def _endung_fuer(fmt, original):
    if fmt == "JPEG":
        return ".jpg"
    if fmt in ("PNG", "WEBP"):
        return "." + fmt.lower()
    return ".png" if fmt else (os.path.splitext(original)[1].lower() or ".jpg")


def entwurf_anlegen(daten, original_name, karte=""):
    """Neues Bild als Entwurf. Mit „karte“ ist es das neue Bild einer vorhandenen Karte (Karten-Editor):
    gleiche Prüfungen wie in Schritt 1, aber Name, Texte und Notiz der Karte bleiben."""
    if not daten:
        raise Meldung("ungueltig")
    zeile = None
    if karte:
        sicher_in(pfade()[1], karte)
        zeile = _karten_zeile(karte)
        if not zeile:
            raise Meldung("karte_unbekannt", status=404)
    eid = secrets.token_hex(8)
    d = entwurf_ordner()
    bild = d / f"{eid}.bild"
    bild.write_bytes(daten)
    stamm = os.path.splitext(os.path.basename(str(original_name or "")))[0][:120]
    rat = ""
    if re.match(r"(?i)^gans[-_ ]", stamm):
        rat = "Gans " + re.sub(r"[-_]+", " ", stamm[5:]).strip()
    meta = dict(id=eid, original=os.path.basename(str(original_name or ""))[:160], zeit=time.time(), de=rat,
                drehung=0, fit=None, ersetzen=False, es="", es_auto="")
    if zeile:
        meta.update(karte=karte, de=zeile.get("de", ""))
    (d / f"{eid}.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    return entwurf_pruefen(eid, {})


def _alle_entwuerfe():
    d = entwurf_ordner()
    aus = []
    for m in sorted(d.glob("*.json"), key=lambda p: p.stat().st_mtime):
        try:
            meta = json.loads(m.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if time.time() - meta.get("zeit", 0) > 14 * 86400:          # alte Entwürfe aufräumen
            m.unlink(missing_ok=True)
            m.with_suffix(".bild").unlink(missing_ok=True)
            continue
        if (d / f"{meta.get('id')}.bild").is_file():
            aus.append(meta)
    return aus


def entwurf_pruefen(eid, aenderung):
    """Prüft einen Entwurf mit Text, Drehung, Bildausschnitt und Ersetzen-Wahl; speichert diese Angaben.
    Bei einem neuen Bild für eine vorhandene Karte („karte“) bleiben Dateiname und Texte der Karte."""
    bild, meta_pfad = _entwurf_pfade(eid)
    with _entwurf_lock:
        meta = json.loads(meta_pfad.read_text(encoding="utf-8"))
        karte = meta.get("karte") or ""
        if "de" in aenderung and not karte:
            meta["de"] = " ".join(str(aenderung["de"] or "").split())[:120]
        if "drehung" in aenderung:
            meta["drehung"] = int(aenderung["drehung"] or 0) % 360 // 90 * 90
        if "fit" in aenderung:
            meta["fit"] = aenderung["fit"] if aenderung["fit"] in ("contain", "cover") else None
        if "ersetzen" in aenderung and not karte:
            meta["ersetzen"] = bool(aenderung["ersetzen"])
        for feld in ("es", "es_auto"):                            # Wort auf Spanisch gleich hier (optional)
            if feld in aenderung and not karte:
                meta[feld] = " ".join(str(aenderung[feld] or "").split())[:300]
        meta_pfad.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    a, cfg = aktuelle_konfig()
    _, bilder, _, _ = pfade()
    analyse = gl.analysiere_bild(bild, cfg, fit=meta.get("fit"), drehung=meta["drehung"], bilder_dir=bilder)
    meldungen = list(analyse["meldungen"])
    name = vorhanden = None
    if karte:
        if analyse.get("groesse"):
            name = karte if Path(karte).suffix.lower() in gl.BILD_ENDUNGEN else \
                Path(karte).stem + _endung_fuer(analyse["format"], meta["original"])
            if not _karten_zeile(karte):
                kopf = [_meldung("karte_unbekannt", "fehler")]
            elif name != karte and (bilder / name).exists():
                kopf = [gl.pm("n_kollision", "fehler", name=name)]
            else:
                kopf = [_meldung("e_ersetzt" if (bilder / karte).is_file() else "e_ergaenzt", "ok", name=karte)]
            if analyse.get("doppelt_von") == karte:                  # dasselbe Bild wie bisher
                meldungen = [m for m in meldungen if m["code"] != "b_doppelt"]
                kopf.append(_meldung("e_gleich", "info"))
            ziel_format = _ENDUNG_FORMAT.get(Path(name).suffix.lower(), "PNG")
            if ziel_format != analyse.get("format"):                  # z. B. PNG für eine Karte „….jpg“
                um = _meldung("e_umwandeln", "info", format=str(analyse.get("format")).replace("JPEG", "JPG"),
                              ziel=ziel_format.replace("JPEG", "JPG"))
                meldungen = [um if m["code"] in ("b_format_ok", "b_format_umwandeln") else m for m in meldungen]
            meldungen = kopf + meldungen
    elif analyse.get("groesse"):                              # nur lesbare Bilder bekommen einen Namen
        endung = _endung_fuer(analyse["format"], meta["original"])
        # gleicher Name mit anderer Endung (gans-alt.png ↔ gans-alt.jpg) zählt auch als „gibt es schon“
        staemme = {}
        if bilder.exists():
            for p in bilder.iterdir():
                if p.is_file() and p.suffix.lower() in gl.BILD_ENDUNGEN:
                    staemme.setdefault(p.stem.lower(), p.name)
        andere = set()
        for m in _alle_entwuerfe():
            if m["id"] != eid and (m.get("karte") or m.get("de")):            # Karten-Editor: Name steht schon fest
                andere.add(m.get("karte") or gl.dateiname_aus_text(m["de"], endung))
        kandidat = gl.dateiname_aus_text(meta.get("de") or "", endung) if meta.get("de") else None
        vorhanden = staemme.get(Path(kandidat).stem.lower()) if kandidat else None
        name, nm = gl.pruefe_name(meta.get("de"), endung, {kandidat} if vorhanden else set(), andere,
                                  meta.get("ersetzen"), vorhanden=vorhanden)
        meldungen = nm + meldungen
    meta["kollision"] = bool(vorhanden)
    meta["vorhanden"] = vorhanden
    if analyse.get("groesse") and meta.get("es"):                # Beschriftung gleich mitprüfen
        gl.registriere_schriften()
        andere = [k for k in karten_daten()["karten"] if k["bild"] != name]
        pk = gl.pruefe_karte(meta.get("de"), meta["es"], cfg, andere=andere)
        meldungen += [m for m in pk["meldungen"] if m["code"] not in ("k_de_leer", "n_ohne_gans")]
    ok = not any(m["stufe"] == "fehler" for m in meldungen)
    return dict(id=eid, original=meta["original"], de=meta.get("de", ""), es=meta.get("es", ""), karte=karte,
                es_auto=meta.get("es_auto", ""), drehung=meta["drehung"],
                fit=analyse.get("fit") or meta.get("fit") or "contain", fit_empfehlung=analyse.get("fit_empfehlung"),
                ersetzen=meta.get("ersetzen", False), kollision=meta.get("kollision", False), dateiname=name,
                vorhanden=meta.get("vorhanden"),
                info={k: analyse.get(k) for k in ("format", "quelle", "groesse", "inhalt", "ppi", "bewertung_code",
                                                  "ppi_varianten", "datei_bytes", "umwandeln")},
                meldungen=meldungen, ok=ok, lesbar=bool(analyse.get("groesse")))


def entwurf_uebernehmen(eid, aenderung):
    erg = entwurf_pruefen(eid, aenderung)
    if not erg["ok"]:
        raise Meldung("bitte_pruefen")
    bild, meta_pfad = _entwurf_pfade(eid)
    _, bilder, ausgabe, _ = pfade()
    bilder.mkdir(parents=True, exist_ok=True)
    ziel = sicher_in(bilder, erg["dateiname"])
    roh = bild.read_bytes()
    endung = ziel.suffix.lower()
    if erg["drehung"] or erg["info"].get("umwandeln") or _ENDUNG_FORMAT.get(endung, "PNG") != erg["info"].get("format"):
        from PIL import Image                                  # Karten-Editor: neues Bild im Format des alten Namens
        im = gl.oeffne_bild(io.BytesIO(roh), erg["drehung"])
        with Image.open(io.BytesIO(roh)) as quelle:
            icc = quelle.info.get("icc_profile")
        puffer = io.BytesIO()
        if endung in (".jpg", ".jpeg"):
            im.save(puffer, "JPEG", quality=95, subsampling=0, icc_profile=icc)
        elif endung == ".webp":
            im.save(puffer, "WEBP", lossless=True, icc_profile=icc)
        else:
            im.save(puffer, "PNG", icc_profile=icc)
        roh = puffer.getvalue()
    if erg.get("karte"):
        fertig = _karte_bild_ersetzen(erg["karte"], ziel, roh, erg["fit"])
        bild.unlink(missing_ok=True)
        meta_pfad.unlink(missing_ok=True)
        return fertig
    alt = erg.get("vorhanden")
    if alt:
        bild_weg(alt)                                          # alte Fassung aufheben, nicht löschen
        _bericht_vergessen(ausgabe, alt)
    tmp = ziel.with_name(ziel.name + ".tmp")
    tmp.write_bytes(roh)
    os.replace(tmp, ziel)
    werte = dict(de=erg["de"], fit=erg["fit"])
    if erg.get("es"):                                           # schon beschriftet → Karte ist sofort fertig
        werte.update(es=erg["es"], uebersetzung=gl.UEBERSETZUNG_WERT["auto"]
                     if erg.get("es_auto") and erg["es_auto"] == erg["es"] else "")
    leer = {"es": "", "notiz": ""}
    if alt and alt != ziel.name:
        setze_karte(alt, dict(bild=ziel.name, **werte), anlegen=False)    # Zeile auf den neuen Namen umstellen
        if not any(k["bild"] == ziel.name for k in karten_daten()["karten"]):
            setze_karte(ziel.name, dict(leer, **werte))
    elif alt:
        setze_karte(ziel.name, werte)
    else:
        setze_karte(ziel.name, dict(leer, **werte))
    bild.unlink(missing_ok=True)
    meta_pfad.unlink(missing_ok=True)
    return dict(name=ziel.name, karten=karten_daten())


def _karte_bild_ersetzen(karte, ziel, roh, fit):
    """Neues Bild für eine vorhandene Karte (Karten-Editor): die alte Fassung kommt nach bilder/_entfernt/, die Zeile
    behält Texte, Notiz und Prüfstatus. Gibt zusätzlich alles zurück, was „Rückgängig“ braucht."""
    zeile = _karten_zeile(karte)
    if not zeile:
        raise Meldung("karte_unbekannt", status=404)
    _, bilder, ausgabe, _ = pfade()
    alt = sicher_in(bilder, karte)
    sicherung = _aufheben(alt).name if alt.is_file() else None
    tmp = ziel.with_name(ziel.name + ".tmp")
    tmp.write_bytes(roh)
    os.replace(tmp, ziel)
    setze_karte(karte, dict(bild=ziel.name, fit=fit), anlegen=False)
    _bericht_vergessen(ausgabe, karte)
    return dict(name=ziel.name, karten=karten_daten(),
                rueckgaengig=dict(bild=ziel.name, name=karte, sicherung=sicherung, fit=zeile.get("fit") or "contain"))


def karte_bild_zurueck(daten):
    """„Rückgängig“ nach „Bild ändern“: das vorige Bild kommt zurück, das neue wird ebenfalls aufgehoben."""
    _, bilder, ausgabe, _ = pfade()
    bild = str(daten.get("bild", ""))
    name = str(daten.get("name") or bild)
    jetzt, frueher = sicher_in(bilder, bild), sicher_in(bilder, name)
    if not _karten_zeile(bild):
        raise Meldung("karte_unbekannt", status=404)
    quelle = sicher_in(bilder / "_entfernt", str(daten["sicherung"])) if daten.get("sicherung") else None
    if quelle is not None and not quelle.is_file():
        raise Meldung("sicherung_fehlt")
    if frueher != jetzt and frueher.exists():
        raise Meldung("ungueltig")
    if jetzt.is_file():
        _aufheben(jetzt)
    if quelle is not None:
        shutil.move(str(quelle), str(frueher))
    fit = daten.get("fit") if daten.get("fit") in ("contain", "cover") else "contain"
    setze_karte(bild, dict(bild=name, fit=fit), anlegen=False)
    _bericht_vergessen(ausgabe, bild)
    return karten_daten()


def entwurf_weg(eid):
    bild, meta = _entwurf_pfade(eid)
    bild.unlink(missing_ok=True)
    meta.unlink(missing_ok=True)
    return {"ok": True}


def entwurf_bild(eid, art, drehung=0, fit=None):
    from PIL import Image
    bild, _ = _entwurf_pfade(eid)
    if art == "vorn":
        a, cfg = aktuelle_konfig()
        gl.registriere_schriften()
        karte = dict(nr=0, bild=bild.name, pfad=bild, de="", es=" ", notiz="",
                     fit=fit if fit in ("contain", "cover") else "contain")
        return gl.vorschau_png(karte, cfg, seite="vorn", dpi=110, cache_dir=Path(a.ausgabe) / ".cache",
                               drehung=drehung)
    im = gl.oeffne_bild(bild, drehung)
    im.thumbnail((900, 900), Image.Resampling.LANCZOS)
    puffer = io.BytesIO()
    im.save(puffer, "JPEG", quality=85)
    return puffer.getvalue(), "image/jpeg"


# =============================================================================================
# Schritt 2: Karte beschriften
# =============================================================================================
def karte_pruefen(daten):
    a, cfg = aktuelle_konfig()
    gl.registriere_schriften()
    bild = str(daten.get("bild", ""))
    andere = [k for k in karten_daten()["karten"] if k["bild"] != bild]
    return gl.pruefe_karte(daten.get("de"), daten.get("es"), cfg, bild=bild or None, bilder_dir=a.bilder, andere=andere,
                           notiz=daten.get("notiz"), ziel=zielsprache())


def _neuer_status(bild, de, es, es_auto):
    """Spalte „uebersetzung“ nach dem Speichern: 'automatisch', wenn das Wort genau der übernommene Vorschlag ist;
    ein Häkchen „geprüft“ bleibt nur, solange Wort und Bildtext unverändert sind; sonst leer (von Hand)."""
    if es and es_auto and " ".join(str(es_auto).split()) == es:
        return gl.UEBERSETZUNG_WERT["auto"]
    alt = next((k for k in karten_daten()["karten"] if k["bild"] == bild), None)
    if alt and alt.get("uebersetzung") and alt["es"] == es and alt["de"] == de:
        return gl.UEBERSETZUNG_WERT[alt["uebersetzung"]]
    return ""


def karte_speichern(daten):
    bild = str(daten.get("bild", ""))
    sicher_in(pfade()[1], bild)
    erg = karte_pruefen(daten)
    if not erg["ok"]:
        raise Meldung("bitte_pruefen")
    werte = dict(de=erg["de"], es=erg["es"], notiz=" ".join(str(daten.get("notiz") or "").split()))
    if daten.get("fit") in ("contain", "cover"):
        werte["fit"] = daten["fit"]
    werte["uebersetzung"] = _neuer_status(bild, erg["de"], erg["es"], daten.get("es_auto"))
    werte.update(_weitere_rueckseiten(bild, daten))
    setze_karte(bild, werte)
    return dict(pruefung=erg, karten=karten_daten())


def _weitere_rueckseiten(bild, daten):
    """Editor „Weitere Sprachen“: rs = {code: Wort} (außer der Zielsprache), rs_auto = übernommene Vorschläge.
    Geänderte Wörter verlieren ihr „geprüft“; ein unveränderter Vorschlag gilt als „automatisch“."""
    rs = daten.get("rs")
    if not (sprachen and isinstance(rs, dict) and rs):
        return {}
    auto = daten.get("rs_auto") if isinstance(daten.get("rs_auto"), dict) else {}
    alt = next((k for k in karten_daten()["karten"] if k["bild"] == bild), None) or {}
    rueck, stati, zs = dict(alt.get("rueckseiten") or {}), dict(alt.get("uebersetzungen") or {}), zielsprache()
    for c, v in rs.items():
        if c == zs or c not in sprachen.SPRACHEN:
            continue
        v = " ".join(str(v or "").split())[:300]
        if v != (rueck.get(c) or ""):
            stati[c] = "auto" if v and " ".join(str(auto.get(c) or "").split()) == v else None
            rueck[c] = v
    return dict(rueckseiten=rueck, uebersetzungen=stati)


def karte_status(daten):
    """Tabelle: Übersetzung als „geprüft“ abhaken (oder das Häkchen wieder entfernen)."""
    bild = str(daten.get("bild", ""))
    sicher_in(pfade()[1], bild)
    k = next((k for k in karten_daten()["karten"] if k["bild"] == bild), None)
    if not k:
        raise Meldung("karte_unbekannt", status=404)
    geprueft = daten.get("geprueft") is True
    if geprueft and not str(k["es"]).strip():
        raise Meldung("nicht_pruefbar")
    setze_karte(bild, {"uebersetzung": gl.UEBERSETZUNG_WERT["geprueft"] if geprueft else ""}, anlegen=False)
    return karten_daten()


def tabelle():
    """Reiter „Tabelle“: Vorder- und Rückseitentext je Karte mit Hinweisen zur Übersetzung."""
    _, cfg = aktuelle_konfig()
    gl.registriere_schriften()
    d = karten_daten()
    zeilen = []
    for k in d["karten"]:
        meld = []
        if str(k["es"]).strip():
            andere = [x for x in d["karten"] if x["bild"] != k["bild"]]
            pr = gl.pruefe_karte(k["de"], k["es"], cfg, andere=andere, ziel=d["zielsprache"])
            meld = [m for m in pr["meldungen"] if m["stufe"] in ("fehler", "warnung") or m["code"] == "k_doppelt"]
        zeilen.append(dict(k, meldungen=meld))
    return dict(karten=zeilen, csv=d["csv"])


# =============================================================================================
# Automatische Übersetzung (Vorschläge) – die eigentliche Arbeit und alle Schutzmaßnahmen stehen in uebersetzer.py
# =============================================================================================
def uebersetzung_info():
    return uebersetzer.oeffentliche_einstellungen(gl.sprache())


def uebersetzung_setzen(daten):
    if daten.get("cache_leeren"):
        uebersetzer.cache_leeren()
    erlaubt = {k: daten[k] for k in ("zugestimmt", "dienst", "automatisch", "deepl") if k in daten}
    if erlaubt:
        uebersetzer.speichere_einstellungen(erlaubt)
    return uebersetzung_info()


def uebersetzen(daten):
    dienst = daten.get("dienst") if daten.get("dienst") in uebersetzer.STRATEGIEN else None
    ziel = str(daten.get("ziel") or "") or zielsprache()
    if ziel != "es" and not (sprachen and sprachen.installiert(ziel)):
        ziel = zielsprache()
    erg = uebersetzer.uebersetze(str(daten.get("de") or "")[:200], dienst, richtung=f"de-{ziel}")
    erg["ziel"] = ziel
    erg["dienst_name"] = uebersetzer.dienst_titel(erg.get("dienst"), gl.sprache())
    return erg


# =============================================================================================
# Gänse-Bild der Rückseite: per Knopf laden, prüfen, sicher ablegen, entfernen, wiederherstellen
# =============================================================================================
_gans_lock = threading.Lock()


def _gans_dateien():
    return [GANS_ORDNER / n for n in GANS_NAMEN if (GANS_ORDNER / n).is_file()]


def _gans_beiseite(pfad):
    """Alte Fassung nicht löschen, sondern nach assets/_alt/ legen (lässt sich wiederherstellen)."""
    ziel = GANS_ORDNER / "_alt"
    ziel.mkdir(exist_ok=True)
    stempel = time.strftime("%Y%m%d-%H%M%S")
    neu = ziel / f"{pfad.stem}-{stempel}{pfad.suffix}"
    i = 2
    while neu.exists():
        neu = ziel / f"{pfad.stem}-{stempel}-{i}{pfad.suffix}"
        i += 1
    shutil.move(str(pfad), str(neu))
    return neu


def _einstellung_gans_leeren():
    """Ein früher eingetippter Pfad (--gans-bild) hätte Vorrang vor dem geladenen Bild – daher leeren."""
    with _einst_lock:
        werte = lade_einstellungen()
        if werte.pop("gans_bild", None) is not None:
            daten = _lies_datei()
            daten["werte"] = werte
            _schreibe_datei(daten)


def gans_bild_info():
    a, cfg = aktuelle_konfig()
    eingestellt = lade_einstellungen().get("gans_bild")
    pfad = Path(cfg.gans_bild) if cfg.gans_bild else None
    quelle = "pfad" if eingestellt else "geladen" if pfad else "gezeichnet"
    alt_ordner = GANS_ORDNER / "_alt"
    info = dict(quelle=quelle, name=pfad.name if pfad else None, pfad=str(pfad) if pfad and eingestellt else None,
                wiederherstellbar=alt_ordner.is_dir() and any(alt_ordner.glob("gans_hintergrund-*")), hinweise=[])
    if pfad and pfad.is_file():
        try:
            from PIL import Image
            with Image.open(pfad) as im:
                w, h = im.size
        except Exception:  # noqa: BLE001
            return info
        tw, th = cfg.flaeche_px
        s = max(tw / w, th / h)                                 # „füllen“ wie auf der Karte
        ppi = round(cfg.dpi / s)
        code, _ = gl.bewertung_ppi(ppi)
        info.update(groesse=[w, h], bytes=pfad.stat().st_size, ppi=ppi, bewertung_code=code,
                    zeit=time.strftime("%Y-%m-%d %H:%M", time.localtime(pfad.stat().st_mtime)))
        if ppi < 150:
            info["hinweise"].append(gl.pm("b_ppi_gering", "warnung", ppi=ppi, min_px=math.ceil(w * 220 / ppi)))
        verhaeltnis = (w / h) / (tw / th)
        if abs(verhaeltnis - 1) >= 0.12:
            sichtbar = round(100 * min(verhaeltnis, 1 / verhaeltnis))
            info["hinweise"].append(gl.pm("b_cover_schnitt", "info", prozent=100 - sichtbar))
    return info


def _nach_srgb(im):
    """Farben mit eingebettetem Profil (z. B. „Display P3“ vom Handy) nach sRGB umrechnen; sonst unverändert."""
    icc = im.info.get("icc_profile")
    if not icc:
        return im
    try:
        from PIL import ImageCms
        quelle = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        ziel = ImageCms.createProfile("sRGB")
        modus = "RGBA" if im.mode == "RGBA" else "RGB"
        return ImageCms.profileToProfile(im.convert(modus), quelle, ziel, outputMode=modus)
    except Exception:  # noqa: BLE001 – kaputtes Profil: Farben so lassen
        return im


def gans_bild_laden(daten):
    """Prüft ein hochgeladenes Bild und legt es als assets/gans_hintergrund.png bzw. .jpg ab. Das Bild wird dabei neu
    gespeichert (auf höchstens 2400 px verkleinert, ohne Metadaten) – übrig bleiben nur Bildpunkte."""
    from PIL import Image, ImageOps
    if not daten or len(daten) > MAX_BILD:
        raise Meldung("gans_gross", mb=gl.MAX_DATEI_MB)
    if daten[4:12] in gl.HEIC_MARKEN:
        raise Meldung("gans_heic")
    try:
        with Image.open(io.BytesIO(daten)) as probe:
            w0, h0 = probe.size
            if w0 * h0 > gl.MAX_MEGAPIXEL * 1_000_000:
                raise Meldung("gans_pixel", mp=round(w0 * h0 / 1e6), max=gl.MAX_MEGAPIXEL)
            probe.verify()
        with Image.open(io.BytesIO(daten)) as roh:
            roh.seek(0)
            im = ImageOps.exif_transpose(roh)
            im.load()
            if roh.info.get("icc_profile"):
                im.info["icc_profile"] = roh.info["icc_profile"]
    except Meldung:
        raise
    except Exception:  # noqa: BLE001
        raise Meldung("gans_unlesbar") from None
    if min(im.size) < 300:
        raise Meldung("gans_klein", w=im.width, h=im.height)
    transparent = im.mode in ("RGBA", "LA", "PA") or (im.mode == "P" and "transparency" in im.info)
    im = _nach_srgb(im).convert("RGBA" if transparent else "RGB")
    if max(im.size) > GANS_MAX_KANTE:
        im.thumbnail((GANS_MAX_KANTE, GANS_MAX_KANTE), Image.Resampling.LANCZOS)
    puffer = io.BytesIO()
    if transparent:
        name = "gans_hintergrund.png"
        im.save(puffer, "PNG", optimize=True)
    else:
        name = "gans_hintergrund.jpg"
        im.save(puffer, "JPEG", quality=92, subsampling=0, optimize=True)
    with _gans_lock:
        GANS_ORDNER.mkdir(exist_ok=True)
        for alt in _gans_dateien():
            _gans_beiseite(alt)
        ziel = GANS_ORDNER / name
        tmp = ziel.with_name(ziel.name + ".tmp")
        tmp.write_bytes(puffer.getvalue())
        os.replace(tmp, ziel)
        _einstellung_gans_leeren()
    _vorschau_cache.clear()
    return gans_bild_info()


def gans_bild_weg():
    """Zurück zur gezeichneten Gans: das geladene Bild kommt nach assets/_alt/, ein eingetippter Pfad wird geleert."""
    with _gans_lock:
        for alt in _gans_dateien():
            _gans_beiseite(alt)
        _einstellung_gans_leeren()
    _vorschau_cache.clear()
    return gans_bild_info()


def gans_bild_zurueck():
    """Das zuletzt beiseitegelegte Gänse-Bild wiederherstellen (das jetzige kommt dafür nach assets/_alt/)."""
    with _gans_lock:
        alte = sorted((GANS_ORDNER / "_alt").glob("gans_hintergrund-*"), key=lambda q: q.stat().st_mtime) \
            if (GANS_ORDNER / "_alt").is_dir() else []
        alte = [q for q in alte if q.suffix.lower() in (".png", ".jpg")]
        if not alte:
            raise Meldung("gans_kein_alt")
        letzte = alte[-1]
        for jetzt in _gans_dateien():
            _gans_beiseite(jetzt)
        shutil.move(str(letzte), str(GANS_ORDNER / f"gans_hintergrund{letzte.suffix.lower()}"))
        _einstellung_gans_leeren()
    _vorschau_cache.clear()
    return gans_bild_info()

# =============================================================================================
# Reiter „Bildverbesserung“: welche Bilder sind schon verbessert? Vorher/Nachher; Verbessern als Lauf
# =============================================================================================
STANDARD_DAUER = {"realesrgan-x4plus": 150.0, "realesrgan-x2plus": 40.0, "fsrcnn": 2.0, "lanczos": 1.0}


def _cache_metas(cache_dir):
    """Alle gespeicherten Angaben zu verbesserten Bildern, nach Bildinhalt (SHA-1) geordnet."""
    nach_inhalt = {}
    if not cache_dir.is_dir():
        return nach_inhalt
    for j in cache_dir.glob("*.json"):
        if j.name.startswith("vorschau-") or not j.with_suffix(".jpg").is_file():
            continue
        try:
            m = json.loads(j.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(m, dict) and m.get("sha1"):
            nach_inhalt.setdefault(m["sha1"], []).append(m)
    return nach_inhalt


def _info_kurz(m):
    return {k: m.get(k) for k in ("ki", "methode", "ppi", "bewertung_code", "qualitaet", "zeit", "dauer", "inhalt")} \
        if m else None


def verbesserung_uebersicht():
    a, cfg = aktuelle_konfig()
    csv_pfad, bilder, ausgabe = Path(a.csv), Path(a.bilder), Path(a.ausgabe)
    cache_dir = ausgabe / ".cache"
    methode = gl.ki_methode(cfg.ki)
    metas = _cache_metas(cache_dir)
    dauern = sorted(m["dauer"] for ms in metas.values() for m in ms
                    if m.get("ki") == methode and isinstance(m.get("dauer"), (int, float)) and m["dauer"] > 0)
    je_bild = dauern[len(dauern) // 2] if dauern else STANDARD_DAUER.get(methode, 60.0)
    _, zeilen, _ = gl.lies_csv(csv_pfad)
    nr_von = {}
    for k in gl.lies_karten(csv_pfad, bilder)[0]:
        nr_von.setdefault(k["bild"], k["nr"])
    karten, gesehen = [], set()
    for z in zeilen:
        roh = z.get("bild", "")
        bild = roh.lstrip("#").strip()
        if not bild or bild in gesehen:
            continue
        gesehen.add(bild)
        fit = (z.get("fit") or "contain").lower()
        fit = fit if fit in ("contain", "cover") else "contain"
        pfad = bilder / bild
        eintrag = dict(bild=bild, de=z.get("de", ""), es=z.get("es", ""), aktiv=not roh.startswith("#"), fit=fit,
                       nr=nr_von.get(bild), existiert=bool(gl.sicherer_name(bild) and pfad.is_file()), status="fehlt",
                       info=None)
        if eintrag["existiert"]:
            key = gl.cache_schluessel(pfad, cfg, fit, methode)
            meta = cache_dir / f"{key}.json"
            if meta.is_file() and meta.with_suffix(".jpg").is_file():
                try:
                    info = json.loads(meta.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    info = {}
                eintrag.update(status="verbessert", info=_info_kurz(info))
            else:
                andere = sorted(metas.get(gl.datei_hash(pfad).hexdigest(), []), key=lambda m: str(m.get("zeit", "")))
                eintrag.update(status="anders" if andere else "offen", info=_info_kurz(andere[-1]) if andere else None)
        karten.append(eintrag)
    return dict(methode=methode, methode_name=gl.METHODE_NAME.get(methode, methode), qualitaet=cfg.qualitaet,
                sekunden_je_bild=round(je_bild, 1), karten=karten,
                modelle={m: ki_modelle.verfuegbar(m) for m in ("realesrgan-x4plus", "realesrgan-x2plus")})


def vergleich_bild(bild, art):
    """Vorher (nur auf Kartengröße gebracht) bzw. Nachher (verbessert, aus dem Zwischenspeicher) als JPEG."""
    a, cfg = aktuelle_konfig()
    pfad = sicher_in(a.bilder, bild)
    if pfad.suffix.lower() not in gl.BILD_ENDUNGEN or not pfad.is_file():
        raise Meldung("datei_fehlt", status=404)
    fit = next((k["fit"] for k in karten_daten()["karten"] if k["bild"] == bild), "contain")
    fit = fit if fit in ("contain", "cover") else "contain"
    cache_dir = Path(a.ausgabe) / ".cache"
    if art == "nachher":
        jpg = cache_dir / f"{gl.cache_schluessel(pfad, cfg, fit, gl.ki_methode(cfg.ki))}.jpg"
        return jpg.read_bytes() if jpg.is_file() else None
    roh = gl.Konfig(**{**cfg.__dict__, "qualitaet": "aus"})
    jpg = cache_dir / f"vorschau-roh-{gl.cache_schluessel(pfad, roh, fit, 'lanczos')}.jpg"
    if not jpg.is_file():
        cache_dir.mkdir(parents=True, exist_ok=True)
        bild_roh, _ = gl.baue_vorderseite(pfad, roh, fit)
        tmp = jpg.with_name(f"{jpg.name}.{threading.get_ident()}.tmp")
        bild_roh.save(tmp, "JPEG", quality=92)
        os.replace(tmp, jpg)
    return jpg.read_bytes()


# =============================================================================================
# Läufe (Generator, Selbsttest, Modell laden, KI-Bild) im Hintergrund mit Live-Protokoll –
# immer höchstens einer zur Zeit, alle weiteren warten in der Warteschlange
# =============================================================================================
class LaufAbbruch(BaseException):
    """Abbruch eines Laufs im selben Prozess (BaseException: kein „except Exception“ im Modul hält ihn auf)."""


class _LaufAusgabe(io.TextIOBase):
    """Ausgabe eines Laufs im selben Prozess → Protokollzeilen (wie stdout des Unterprozesses, \\r wie \\n)."""

    def __init__(self, lauf):
        super().__init__()
        self.lauf, self.puffer = lauf, ""

    def writable(self):
        return True

    def write(self, text):
        if self.lauf.abgebrochen:
            raise LaufAbbruch()
        self.puffer += str(text).replace("\r\n", "\n").replace("\r", "\n")
        *zeilen, self.puffer = self.puffer.split("\n")
        for z in zeilen:
            self.lauf._zeile(z + "\n")
        return len(text)

    def rest(self):
        for z in self.puffer.split("\n"):
            if z:
                self.lauf._zeile(z + "\n")
        self.puffer = ""


class Lauf:
    def __init__(self, art, titel, befehl, argv_anzeige, nur=None, sprache="en"):
        self.id = secrets.token_hex(4)
        self.nur, self.sprache = nur, sprache
        self.art, self.titel, self.befehl = art, titel, befehl
        self.anzeige = argv_anzeige
        self.zeilen, self.code, self.start, self.ende = [], None, time.time(), None
        self.proc = None
        self.ki_id, self.prozent, self.ergebnis, self.ki_meta = None, 0, None, {}   # nur bei art „ki-bild“
        self.gestartet, self.abgebrochen, self.eingereiht = False, False, time.time()
        self.schluessel = None          # (Art, Befehl): derselbe Auftrag wartet nicht doppelt
        self.vor_start = None           # Prüfung direkt vor dem Start (z. B. KI-Modell noch da?)
        self.nach_ende = None           # Rückruf der Warteschlange: startet den nächsten Auftrag

    def starte(self):
        self.start, self.gestartet = time.time(), True
        if im_prozess():                                        # Web-App (Pyodide): keine Unterprozesse
            if im_browser():                                    # … und keine Threads: läuft direkt nach der Antwort
                _web_wartet.append(self)                        # (web_weiter) – so sieht die Seite den Fortschritt
                return None
            return threading.Thread(target=self._im_prozess, daemon=True).start()
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1", PYTHONUNBUFFERED="1", MGD_SPRACHE=self.sprache)
        kw = {}
        if os.name == "nt":
            kw["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        self.proc = subprocess.Popen(self.befehl, cwd=HIER, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace",
                                     env=env, **kw)
        threading.Thread(target=self._lies, daemon=True).start()

    def _lies(self):
        for zeile in self.proc.stdout:
            self._zeile(zeile)
        self._fertig(self.proc.wait())

    def _zeile(self, zeile):
        if self.ki_id:                                           # KI-Bild: Prozente und Ergebnis nicht ins Protokoll
            m = re.fullmatch(r"\s*(\d{1,3}) %\s*", zeile)
            if m:
                self.prozent = min(100, int(m.group(1)))
                return
            if zeile.startswith("#ergebnis "):
                try:
                    self.ergebnis = json.loads(zeile[len("#ergebnis "):])
                except ValueError:
                    pass
                return
        self.zeilen.append(zeile.rstrip("\n"))
        if len(self.zeilen) > 20000:
            del self.zeilen[:5000]
        if WEB_MELDER:
            _web_melden(self)

    def _fertig(self, code):
        self.code = code
        self.ende = time.time()
        _vorschau_cache.clear()
        if WEB_MELDER:
            _web_melden(self, sofort=True)
        if self.nach_ende:
            self.nach_ende(self)

    def _im_prozess(self):
        """Wie der Unterprozess, nur im selben Prozess: main(argv) des Moduls aus dem Befehl, Ausgabe zeilenweise ins
        Protokoll, Sprache wie MGD_SPRACHE. Abbruch über den Merker `abgebrochen` (greift bei der nächsten Ausgabe)
        bzw. KeyboardInterrupt (Pyodide-Unterbrechung)."""
        import contextlib
        import importlib
        import traceback
        aus = _LaufAusgabe(self)
        alt_env, alt_sprache = os.environ.get("MGD_SPRACHE"), getattr(gl._LOKAL, "sprache", None)
        code = 1
        try:
            os.environ["MGD_SPRACHE"] = self.sprache
            gl.setze_sprache(self.sprache)
            modul = importlib.import_module(Path(self.befehl[2]).stem)
            with contextlib.redirect_stdout(aus), contextlib.redirect_stderr(aus):
                erg = modul.main(list(self.befehl[3:]))
            code = erg if isinstance(erg, int) else 0
        except SystemExit as e:
            if isinstance(e.code, str):
                aus.puffer += e.code + "\n"
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        except (LaufAbbruch, KeyboardInterrupt):
            self.abgebrochen, code = True, 1
        except Exception:  # noqa: BLE001 – wie ein abgestürzter Unterprozess: Meldung ins Protokoll
            aus.puffer += traceback.format_exc()
        finally:
            aus.rest()
            if alt_env is None:
                os.environ.pop("MGD_SPRACHE", None)
            else:
                os.environ["MGD_SPRACHE"] = alt_env
            gl.setze_sprache(alt_sprache)
        self._fertig(code)

    def scheitern(self, text):
        """Start war nicht möglich → als „fertig mit Fehler“ ablegen (die Schlange läuft weiter)."""
        self.zeilen.append(f"✕ {text}")
        self.code, self.ende = 1, time.time()

    @property
    def laeuft(self):
        return self.gestartet and self.code is None

    @property
    def wartet(self):
        return not self.gestartet and self.code is None

    def status(self, ab=0):
        st = dict(id=self.id, art=self.art, nur=self.nur, titel=self.titel, befehl=self.anzeige, laeuft=self.laeuft,
                  code=self.code, zeilen=self.zeilen[ab:], anzahl=len(self.zeilen), abgebrochen=self.abgebrochen,
                  dauer=round((self.ende or time.time()) - self.start, 1) if self.gestartet else 0,
                  ende=self.ende, eingereiht=self.eingereiht, tool=_lauf_tool(self.art))
        if self.wartet:
            st.update(wartet=True, position=warteschlange.position(self))
        if self.ki_id:
            vorschau_jpg = ki_bild_ordner() / f"{self.ki_id}.jpg"
            try:
                stand = int(vorschau_jpg.stat().st_mtime * 1000)
            except OSError:
                stand = None
            st["ki"] = dict(id=self.ki_id, prozent=self.prozent, fertig=self.code == 0 and self.ergebnis is not None,
                            vorschau=stand, startwert=(self.ergebnis or {}).get("startwert"), **self.ki_meta)
        return st


class Warteschlange:
    """Höchstens ein Hintergrundprozess zur Zeit. Weitere Aufträge warten (nur im Arbeitsspeicher) und starten
    automatisch nacheinander – der nächste per Rückruf am Ende des laufenden (kein Abfrage-Thread)."""
    FERTIG_MAX = 10

    def __init__(self):
        self.lock = threading.RLock()
        self.aktiv: Lauf | None = None
        self.wartend: list[Lauf] = []
        self.fertig: list[Lauf] = []                    # neueste zuerst

    @property
    def letzter(self):
        """Laufender bzw. zuletzt beendeter Auftrag (GET /api/lauf wie bisher)."""
        with self.lock:
            return self.aktiv or (self.fertig[0] if self.fertig else None)

    def einreihen(self, lauf):
        with self.lock:
            if lauf.schluessel:
                gleich = next((w for w in self.wartend if w.schluessel == lauf.schluessel), None)
                if gleich:
                    return gleich
            lauf.nach_ende = self._beendet
            self.wartend.append(lauf)
            self._naechster()
            return lauf

    def _naechster(self):
        while self.wartend and not self.aktiv:
            lauf = self.wartend.pop(0)
            try:
                if lauf.vor_start:
                    lauf.vor_start()
                self.aktiv = lauf
                lauf.starte()
            except Exception as e:  # noqa: BLE001 – Fehler beim Start blockiert die Schlange nicht
                self.aktiv = None
                lauf.scheitern(str(e) if isinstance(e, Meldung) else f"{type(e).__name__}: {e}")
                self._ablegen(lauf)

    def _beendet(self, lauf):
        with self.lock:
            if self.aktiv is lauf:
                self.aktiv = None
            self._ablegen(lauf)
            self._naechster()

    def _ablegen(self, lauf):
        if lauf not in self.fertig:
            self.fertig.insert(0, lauf)
            del self.fertig[self.FERTIG_MAX:]

    def position(self, lauf):
        """Platz in der Schlange: der laufende Auftrag hat Platz 1, der nächste Platz 2 …"""
        with self.lock:
            return self.wartend.index(lauf) + 1 + bool(self.aktiv) if lauf in self.wartend else 0

    def finde(self, lid):
        with self.lock:
            return next((x for x in [self.aktiv, *self.wartend, *self.fertig] if x and x.id == lid), None)

    def aktion(self, aktion, lid=None):
        with self.lock:
            if aktion == "leeren":
                self.wartend.clear()
                return self.uebersicht()
            lauf = next((w for w in self.wartend if w.id == lid), None)
            if not lauf:
                raise Meldung("ws_weg", status=404)
            i = self.wartend.index(lauf)
            if aktion == "hoch" and i > 0:
                self.wartend[i - 1], self.wartend[i] = lauf, self.wartend[i - 1]
            elif aktion == "runter" and i < len(self.wartend) - 1:
                self.wartend[i + 1], self.wartend[i] = lauf, self.wartend[i + 1]
            elif aktion == "als-naechstes":
                self.wartend.insert(0, self.wartend.pop(i))
            elif aktion == "entfernen":
                self.wartend.pop(i)
            elif aktion not in ("hoch", "runter"):
                raise Meldung("ungueltig")
            return self.uebersicht()

    def stoppen(self):
        """Laufenden Auftrag abbrechen – danach startet der nächste automatisch."""
        with self.lock:
            lauf = self.aktiv
            if lauf and lauf.laeuft and (lauf.proc or im_prozess()):
                lauf.abgebrochen = True                       # im selben Prozess: Merker, greift bei der nächsten Ausgabe
                if lauf.proc:
                    lauf.proc.terminate()
                return True
        return False

    def alles_stoppen(self):
        """Beenden/Deinstallieren: wartende verwerfen, laufenden stoppen."""
        with self.lock:
            self.wartend.clear()
            self.stoppen()

    @property
    def anzahl(self):
        return len(self.wartend)

    def uebersicht(self):
        with self.lock:
            a = self.aktiv
            aktiv = None
            if a:
                aktiv = a.status(len(a.zeilen))
                del aktiv["zeilen"]
            wartend = [dict(id=w.id, art=w.art, titel=w.titel, nur=w.nur, eingereiht=w.eingereiht, position=i + 1 + bool(a))
                       for i, w in enumerate(self.wartend)]
            fertig = []
            for f in self.fertig:
                e = dict(id=f.id, art=f.art, titel=f.titel, nur=f.nur, code=f.code, abgebrochen=f.abgebrochen,
                         dauer=round((f.ende or f.start) - f.start, 1) if f.gestartet else 0, ende=f.ende,
                         tool=_lauf_tool(f.art))
                if f.ki_id:
                    e["ki"] = dict(id=f.ki_id, fertig=f.code == 0 and f.ergebnis is not None,
                                   startwert=(f.ergebnis or {}).get("startwert"), **f.ki_meta)
                fertig.append(e)
            return dict(aktiv=aktiv, wartend=wartend, fertig=fertig)


warteschlange = Warteschlange()

# Web-App: der Worker setzt WEB_MELDER (Rückruf mit dem Stand als JSON-Text); gestartete Aufträge laufen erst nach der
# Antwort auf POST /api/lauf (web_weiter), damit die Seite Protokoll und Fortschritt sieht, während Python rechnet.
WEB_MELDER = None
_web_wartet: list = []
_web_takt = [0.0]


def _web_melden(lauf, sofort=False):
    jetzt = time.monotonic()
    if WEB_MELDER is None or (not sofort and jetzt - _web_takt[0] < 0.4):
        return
    _web_takt[0] = jetzt
    try:
        a = warteschlange.aktiv
        WEB_MELDER(json.dumps(dict(lauf.status(), warteschlange=warteschlange.anzahl, aktiv=a.id if a else None),
                              ensure_ascii=False))
    except Exception:  # noqa: BLE001 – die Anzeige darf einen Auftrag nie stören
        pass


def web_weiter():
    """Web-App: gestartete Aufträge jetzt ausführen – der Worker ruft das nach jeder Antwort. Danach startet die
    Warteschlange von selbst den nächsten (wieder hier). → Anzahl der gelaufenen Aufträge."""
    n = 0
    while _web_wartet:
        lauf = _web_wartet.pop(0)
        if lauf.code is None:
            _web_melden(lauf, sofort=True)                     # die Seite weiß sofort: jetzt rechnet Python
            lauf._im_prozess()
            n += 1
    return n


def _lauf_tool(art):
    """Ist der Lauf der Download eines Tools? → dessen id (die Oberfläche macht danach mit der Aktion weiter)."""
    return next((tid for tid in tools.TOOLS if tools.gehoert(tid, art) == "laden"), None) if tools else None


NUR_RECHNER_TOOLS = {"ki-bild"}                      # Web-App: zu groß (3,5 GB Modell, ~3 GB Arbeitsspeicher)
NUR_RECHNER_LAEUFE = {"ki-bild", "ki-bild-laden", "test"}


def tool_da(tid):
    """Ist das Tool installiert (und nicht abgemeldet)? Ohne tools.py zählen wie früher nur die Dateien."""
    if tid in NUR_RECHNER_TOOLS and im_browser():
        return False
    if tools and tools.gibt_es(tid):
        return tools.installiert(tid)
    if tid == "ki-bild":
        return bool(ki_bild) and ki_bild.status()["installiert"]
    if tid == "bildverbesserung":
        return any(ki_modelle.verfuegbar(m) for m in gl.KI_MODELLE.values())
    return uebersetzer.lade_einstellungen()["zugestimmt"]


def _tool_fehlt(tid, code="tool_fehlt"):
    """409 {fehler, code: "tool_fehlt", tool} – die Oberfläche bietet dann Installieren an (brauchtTool)."""
    titel = gl.text_in(tools.TOOLS[tid]["titel"]) if tools and tools.gibt_es(tid) else tid
    raise Meldung(code, status=409, extra=dict(code="tool_fehlt", tool=tid), titel=titel)


def _ki_modell_da():
    if not tool_da("ki-bild"):
        _tool_fehlt("ki-bild", "ki_modell_fehlt")


def _bildverbesserung_pruefen(extra, ohne_tool):
    """Real-ESRGAN fest gewählt, aber Tool fehlt → 409 tool_fehlt. „Ohne Tool weiter“ rechnet mit FSRCNN (Kern)."""
    if lade_einstellungen().get("ki") in gl.KI_MODELLE and not tool_da("bildverbesserung"):
        if not ohne_tool:
            _tool_fehlt("bildverbesserung")
        extra["ki"] = "fsrcnn"
    return extra


def druck_sprachen(wahl):
    """Sprachen für einen Druck-/Export-Auftrag: None/"" = Zielsprache, "alle" = alle installierten, sonst der Code."""
    if wahl in (None, "", "ziel"):
        return [zielsprache()]
    if wahl == "alle":
        return sprachen.installierte() if sprachen else ["es"]
    if wahl == "es" or (sprachen and wahl in sprachen.SPRACHEN and sprachen.installiert(wahl)):
        return [wahl]
    if sprachen and wahl in sprachen.SPRACHEN:
        titel = gl.text_in(tools.TOOLS["sprachen"]["titel"]) if tools and tools.gibt_es("sprachen") else "sprachen"
        raise Meldung("tool_fehlt", status=409, extra=dict(code="tool_fehlt", tool="sprachen", teil=wahl), titel=titel)
    raise Meldung("ungueltig")


def starte_lauf(art, nur=None, karten=None, modell=None, bilder=None, alle=False, ki=None, ohne_tool=False, code=None,
                sprache_wahl=None):
    """Baut und prüft den Auftrag sofort (Fehler gleich zurück) und reiht ihn ein. Bei leerer Schlange startet er
    sofort (Antwort wie bisher mit „laeuft“), sonst kommt „wartet“ mit Platz zurück. Fehlt ein nötiges Tool → 409
    tool_fehlt (ohne_tool: Bildverbesserung mit dem eingebauten FSRCNN)."""
    sprache = gl.sprache()
    if art in NUR_RECHNER_LAEUFE and im_browser():
        raise Meldung("nur_rechner", status=403)
    if art == "ki-bild" and ki_bild:                        # realistische Gans aus Beschreibung (eigener Prozess)
        _ki_modell_da()
        lauf = _ki_bild_lauf(ki or {}, sprache)
        lauf.vor_start = _ki_modell_da
    elif art == "verbessern":                              # Reiter „Bildverbesserung“: nur Bilder, keine PDFs
        ordner = pfade()[1]
        namen = [] if alle else list(dict.fromkeys(str(b) for b in (bilder or [])))
        for n in namen:
            sicher_in(ordner, n)
        if not alle and not namen:
            raise Meldung("keine_auswahl")
        argv = argv_aus(lade_einstellungen(), _bildverbesserung_pruefen({"nur": "verbessern", "bild": namen}, ohne_tool))
        _, fehler = parse(argv)
        if fehler:
            raise ValueError(fehler)
        befehl = [sys.executable, "-u", str(HIER / "gans_lernkarten.py"), *argv]
        anzahl = len(namen) if namen else len(gl.bilder_der_karten(pfade()[0], ordner))
        lauf = Lauf(art, tx("verbessern", n=anzahl), befehl, befehlszeile(argv), "verbessern", sprache)
    elif art == "generator":
        if (nur or "alles") == "verbessern":
            raise Meldung("ungueltig")
        codes = druck_sprachen(sprache_wahl) if (nur or "alles") != "vorlagen" else ["es"]   # Vorlagen ohne Sprache
        if len(codes) > 1:                                 # „alle installierten“: ein Auftrag je Sprache
            stati = [starte_lauf(art, nur, karten, ohne_tool=ohne_tool, sprache_wahl=c) for c in codes]
            return dict(stati[0], auftraege=len(stati), sprachen=codes)
        extra = {"nur": nur or "alles", "karten": karten or ""}
        if (nur or "alles") != "vorlagen":
            extra["sprache"] = codes[0]
        argv = argv_aus(lade_einstellungen(), _bildverbesserung_pruefen(extra, ohne_tool))
        _, fehler = parse(argv)
        if fehler:
            raise ValueError(fehler)
        befehl = [sys.executable, "-u", str(HIER / "gans_lernkarten.py"), *argv]
        felder = alle_felder()
        titel = next((a["label"] for a in felder["nur"]["auswahl"] if a["wert"] == (nur or "alles")), tx("erzeugen"))
        if codes[0] != "es" and (nur or "alles") != "vorlagen":
            titel += f" · {sprachen.name(codes[0], sprache) if sprachen else codes[0]}"
        lauf = Lauf(art, titel, befehl, befehlszeile(argv), nur or "alles", sprache)
    elif art == "test":
        befehl = [sys.executable, "-u", str(HIER / "test_gans_lernkarten.py")]
        lauf = Lauf(art, tx("selbsttest"), befehl, "python3 test_gans_lernkarten.py", sprache=sprache)
    elif art == "modell" and modell in ki_modelle.KATALOG:          # + Kopie im Datenordner (übersteht neue Versionen)
        befehl = [sys.executable, "-u", str(HIER / "ki_modelle.py"), "--laden", modell,
                  "--vorrat", str(uebersetzer.daten_ordner() / "modelle")]
        lauf = Lauf(art, tx("modell_laden", titel=ki_modelle.KATALOG[modell]["titel"]), befehl,
                    f"python3 ki_modelle.py --laden {modell}", sprache=sprache)
    elif art == "sprache" and sprachen and code in sprachen.SPRACHEN and code != sprachen.STANDARD:
        befehl = [sys.executable, "-u", str(HIER / "sprachen.py"), "--laden", code]
        lauf = Lauf(art, tx("sprache_laden", name=sprachen.name(code, sprache)), befehl,
                    f"python3 sprachen.py --laden {code}", sprache=sprache)
    elif art == "ki-bild-laden" and ki_bild:
        befehl = [sys.executable, "-u", str(HIER / "ki_bild.py"), "--laden"]
        lauf = Lauf(art, tx("ki_bild_laden"), befehl, "python3 ki_bild.py --laden", sprache=sprache)
    else:
        raise Meldung("ungueltig")
    lauf.schluessel = (art, tuple(str(x) for x in lauf.befehl[2:]))
    return warteschlange.einreihen(lauf).status()


# =============================================================================================
# Ergebnisse
# =============================================================================================
BESCHREIBUNG = [
    (r".*_Pruefbogen(_[a-z]{2,3})?\.pdf", L("Prüfbogen", "Proof sheet", "Hoja de control"),
     L("Vor dem Druck kontrollieren: Vorder- und Rückseite, Texte, Bildschärfe",
       "Check before printing: front and back, texts, image sharpness",
       "Revisa antes de imprimir: anverso y reverso, textos, nitidez")),
    (r".*_Heimdruck_(A4|Letter)_.*\.pdf", L("Heimdruck", "Home print", "Impresión en casa"),
     L("Selbst drucken: beidseitig, Wenden an der langen Kante, 100 % („Tatsächliche Größe“)",
       "Print yourself: double-sided, flip on long edge, 100 % (“Actual size”)",
       "Imprime tú: a doble cara, volteo por el borde largo, 100 % («Tamaño real»)")),
    (r".*_Druckerei_.*_hochkant(_[a-z]{2,3})?\.pdf", L("Druckerei-PDF hochkant", "Print-shop PDF portrait", "PDF de imprenta vertical"),
     L("Für Druckereien, deren Vorlage Hochformat verlangt", "For print shops whose template requires portrait",
       "Para imprentas cuya plantilla pide formato vertical")),
    (r".*_Druckerei_.*\.pdf", L("Druckerei-PDF", "Print-shop PDF", "PDF para imprenta"),
     L("Upload bei einer Online-Kartendruckerei, eine Seite je Kartenseite",
       "Upload to an online card printer, one page per card side",
       "Para subir a una imprenta de cartas en línea, una página por lado")),
    (r".*_Projekt.*\.zip", L("Projekt-ZIP", "Project ZIP", "ZIP del proyecto"),
     L("Das ganze Projekt zum Sichern oder Weitergeben", "The whole project for backup or sharing",
       "Todo el proyecto para respaldo o para compartir")),
    (r"VORLAGE_Druckerei_.*\.pdf", L("Vorlage Druckerei", "Print-shop template", "Plantilla de imprenta"),
     L("Leere Vorlage mit Beschnitt, Rand und sicherem Bereich", "Blank template with bleed, border and safe area",
       "Plantilla vacía con sangrado, borde y zona segura")),
    (r"VORLAGE_Heimdruck_.*\.pdf", L("Vorlage Heimdruck", "Home-print template", "Plantilla para casa"),
     L("Leeres Raster mit Schnittmarken", "Blank grid with crop marks", "Cuadrícula vacía con marcas de corte")),
    (r".*_Anki(_[a-z]{2,3})?\.apkg", L("Anki-Paket", "Anki package", "Paquete de Anki"),
     L("In Anki öffnen (Windows, Mac, Linux) oder aufs Handy schicken: AnkiDroid und AnkiMobile lesen es direkt",
       "Open in Anki (Windows, Mac, Linux) or send it to your phone: AnkiDroid and AnkiMobile read it directly",
       "Ábrelo en Anki (Windows, Mac, Linux) o envíalo al celular: AnkiDroid y AnkiMobile lo leen directamente")),
    (r".*_Lernseite(_[a-z]{2,3})?\.html", L("Lernseite", "Study page", "Página de estudio"),
     L("Eine Datei, läuft offline im Browser am Rechner: umdrehen, „Gewusst/Nochmal“, Fortschritt bleibt gespeichert "
       "(am Handy nur eingeschränkt)",
       "One file, runs offline in the browser on your computer: flip, “Got it/Again”, progress is remembered "
       "(limited on phones)",
       "Un solo archivo, funciona sin conexión en el navegador de la computadora: voltear, «La sé/Otra vez», el "
       "progreso se guarda (en el celular, a medias)")),
    (r".*_Bildschirm_.*\.pdf", L("Bildschirm-PDF", "Screen PDF", "PDF de pantalla"),
     L("Zum Durchblättern am Handy oder Tablet: Vorderseite, dann Rückseite",
       "For flicking through on a phone or tablet: front, then back",
       "Para hojear en el celular o la tableta: anverso y luego reverso")),
]
DIGITAL_ENDUNGEN = {".apkg", ".html", ".pdf"}               # nur in ausgabe/digital: als Download bzw. mit dem Standardprogramm


def _mit_sprache(titel, name):
    """„Prüfbogen“ → „Prüfbogen · Japanisch“, wenn der Dateiname auf _<Sprachcode> endet."""
    m = re.search(r"_([a-z]{2,3})\.[a-z]+$", name)
    if m and sprachen and m.group(1) in sprachen.SPRACHEN and m.group(1) != "es":
        return f"{titel} · {sprachen.name(m.group(1), gl.sprache())}"
    return titel


def ergebnisse():
    _, _, ausgabe, vorlagen = pfade()
    dateien = []
    for ordner, gruppe in ((ausgabe, "ausgabe"), (vorlagen, "vorlagen")):
        if not ordner.exists():
            continue
        for p in sorted(ordner.iterdir(), key=lambda q: q.name):
            if not p.is_file() or p.is_symlink() or p.name.startswith(".") or p.suffix.lower() not in SICHERE_ENDUNGEN:
                continue
            titel, text = p.name, ""
            for muster, t, b in BESCHREIBUNG:
                if re.fullmatch(muster, p.name):
                    titel, text = _mit_sprache(gl.text_in(t), p.name), gl.text_in(b)
                    break
            st = p.stat()
            dateien.append(dict(name=p.name, gruppe=gruppe, titel=titel, beschreibung=text, groesse=st.st_size,
                                zeit=time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime)),
                                url=f"/datei/{gruppe}/{quote(p.name)}"))
    digital = ausgabe / "digital"
    if digital.is_dir():
        for p in sorted(digital.iterdir(), key=lambda q: q.name):
            if not p.is_file() or p.is_symlink() or p.name.startswith(".") or p.suffix.lower() not in DIGITAL_ENDUNGEN:
                continue
            titel, text = p.name, ""
            for muster, t, b in BESCHREIBUNG:
                if re.fullmatch(muster, p.name):
                    titel, text = _mit_sprache(gl.text_in(t), p.name), gl.text_in(b)
                    break
            st = p.stat()
            dateien.append(dict(name=p.name, gruppe="digital", titel=titel, beschreibung=text, groesse=st.st_size,
                                zeit=time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime)),
                                url=f"/datei/digital/{quote(p.name)}"))
    einzel = sorted((ausgabe / "einzelbilder").glob("*.png")) if (ausgabe / "einzelbilder").exists() else []
    _, cfg = aktuelle_konfig()
    return dict(dateien=dateien, einzelbilder=len(einzel), bericht=lies_bericht(ausgabe),
                namen=gl.ausgabe_namen(cfg))


def oeffne(ziel):
    """Öffnet eine Datei oder einen Ordner des Projekts mit dem Standardprogramm des Rechners –
    nur bekannte Ordner und nur harmlose Dateitypen (kein Start von Programmen oder Skripten)."""
    csv_pfad, bilder, ausgabe, vorlagen = pfade()
    orte = {"projekt": HIER, "bilder": bilder, "ausgabe": ausgabe, "vorlagen": vorlagen,
            "einzelbilder": ausgabe / "einzelbilder", "karten": csv_pfad, "digital": ausgabe / "digital",
            "tabellen": ausgabe / "digital" / "tabellen"}
    gruppe = ""
    if ziel in orte:
        pfad = orte[ziel]
    else:
        gruppe, _, name = str(ziel).partition("/")
        basis = {"ausgabe": ausgabe, "vorlagen": vorlagen, "einzelbilder": ausgabe / "einzelbilder",
                 "digital": ausgabe / "digital"}.get(gruppe)
        if basis is None:
            raise Meldung("ungueltig")
        pfad = sicher_in(basis, name)
    if not pfad.exists():
        if ziel in ("ausgabe", "vorlagen", "einzelbilder", "bilder", "digital"):
            pfad.mkdir(parents=True, exist_ok=True)
        else:
            raise Meldung("gibt_es_nicht", status=404, name=pfad.name)
    erlaubt = SICHERE_ENDUNGEN | (DIGITAL_ENDUNGEN if gruppe == "digital" else set())   # Lernseite/Anki nur aus „digital“
    if pfad.is_file() and pfad.suffix.lower() not in erlaubt:
        raise Meldung("oeffnen_typ")
    if os.name == "nt":
        os.startfile(str(pfad))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":                           # absoluter Pfad – „open“ kann ihn nie als Schalter lesen
        subprocess.Popen(["open", str(pfad.resolve())], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif shutil.which("xdg-open"):
        subprocess.Popen(["xdg-open", str(pfad.resolve())], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        raise Meldung("kein_programm")
    return str(pfad)


def _aufheben(quelle):
    """Verschiebt ein Bild nach bilder/_entfernt/ (nie löschen) und gibt den neuen Pfad zurück."""
    ziel_ordner = quelle.parent / "_entfernt"
    ziel_ordner.mkdir(exist_ok=True)
    ziel, n = ziel_ordner / quelle.name, 1
    while ziel.exists():
        ziel = ziel_ordner / f"{quelle.stem}-{time.strftime('%Y%m%d-%H%M%S')}{f'-{n}' if n > 1 else ''}{quelle.suffix}"
        n += 1
    shutil.move(str(quelle), str(ziel))
    _vorschau_cache.clear()
    return ziel


def bild_weg(name):
    _, bilder, _, _ = pfade()
    quelle = sicher_in(bilder, name)
    if not quelle.is_file():
        raise Meldung("gibt_es_nicht", status=404, name=name)
    _aufheben(quelle)
    return {"meldung": tx("bild_weg", name=name)}


# =============================================================================================
# Werkzeuge – neue Werkzeuge einfach mit @werkzeug(...) ergänzen; sie erscheinen automatisch in der Oberfläche
# =============================================================================================
WERKZEUGE: list = []


def werkzeug(id, titel, beschreibung, knopf, art="aktion", zustand=None, nur_rechner=False, frage=None, tool=None):
    """titel/beschreibung/knopf als L(de, en, es); zustand: optionale Funktion → (Text, aktiv);
    nur_rechner: öffnet etwas am Rechner → über den Handy-Zugang gesperrt und dort ausgeblendet;
    frage: L(…) – die Oberfläche fragt vor dem Start nach (z. B. vor einem großen Download);
    tool: gehört zu diesem Tool (tools.py) – die Oberfläche zeigt es dann im Bereich „Tools“ statt doppelt."""
    def deko(fn):
        WERKZEUGE.append(dict(id=id, titel=titel, beschreibung=beschreibung, knopf=knopf, art=art, fn=fn,
                              zustand=zustand, nur_rechner=nur_rechner, frage=frage, tool=tool))
        return fn
    return deko


NUR_RECHNER_WERKZEUGE_WEB = {"test", "zip"}     # Web-App: Selbsttest (Unterprozess) und Programm-ZIP (Ordner am Rechner)


def _werkzeug_nur_rechner(w):
    return bool(w.get("nur_rechner")) or (im_browser() and w["id"] in NUR_RECHNER_WERKZEUGE_WEB)


def werkzeuge_liste():
    aus = []
    for w in WERKZEUGE:
        e = dict(id=w["id"], art=w["art"], titel=gl.text_in(w["titel"]), beschreibung=gl.text_in(w["beschreibung"]),
                 knopf=gl.text_in(w["knopf"]), zustand=None, aktiv=True, nur_rechner=_werkzeug_nur_rechner(w),
                 frage=gl.text_in(w["frage"]) if w.get("frage") else None, tool=w.get("tool"))
        if w["zustand"]:
            text, aktiv = w["zustand"]()
            e.update(zustand=gl.text_in(text), aktiv=aktiv)
        aus.append(e)
    return aus


def _modell_zustand(mid):
    def z():
        if ki_modelle.verfuegbar(mid):
            return L("installiert ✓", "installed ✓", "instalado ✓"), False
        return L("nicht installiert", "not installed", "no instalado"), True
    return z


@werkzeug("modell-x4", L("Bestes KI-Modell laden (Real-ESRGAN x4plus)", "Download best AI model (Real-ESRGAN x4plus)",
                          "Descargar el mejor modelo de IA (Real-ESRGAN x4plus)"),
          L("Die schönste Bildverbesserung für deine Vorderseiten (64 MB von GitHub, Prüfsumme wird kontrolliert). "
            "Gehört zum Tool „Bildverbesserung“.",
            "The loveliest image enhancement for your fronts (64 MB from GitHub, checksum verified). Part of the "
            "“Image enhancement” tool.",
            "La mejora de imagen más bonita para tus anversos (64 MB desde GitHub, se verifica la suma). Forma parte "
            "de la herramienta «Mejora de imagen»."),
          L("Laden", "Download", "Descargar"), art="lauf", zustand=_modell_zustand("realesrgan-x4plus"),
          tool="bildverbesserung")
def _w_modell_x4():
    return starte_lauf("modell", modell="realesrgan-x4plus")


@werkzeug("modell-x2", L("Schnelleres KI-Modell laden (Real-ESRGAN x2plus)", "Download faster AI model (Real-ESRGAN x2plus)",
                          "Descargar modelo de IA más rápido (Real-ESRGAN x2plus)"),
          L("Fast gleiche Qualität, etwa 4× schneller. Danach im Reiter Bildverbesserung unter KI-Vergrößerung "
            "„Real-ESRGAN ×2“ wählen.",
            "Almost the same quality, about 4× faster. Then choose “Real-ESRGAN ×2” under AI upscaling in the "
            "Image enhancement tab.",
            "Casi la misma calidad, unas 4 veces más rápido. Luego elige «Real-ESRGAN ×2» en Ampliación con IA, "
            "en la pestaña Mejora de imagen."),
          L("Laden", "Download", "Descargar"), art="lauf", zustand=_modell_zustand("realesrgan-x2plus"),
          tool="bildverbesserung")
def _w_modell_x2():
    return starte_lauf("modell", modell="realesrgan-x2plus")


@werkzeug("test", L("Selbsttest", "Self-test", "Autoprueba"),
          L("Prüft Generator, Bildverbesserung, Sicherheit und Oberfläche in einer Kopie des Projekts (ca. 1 Minute) – "
            "deine Karten bleiben unberührt.",
            "Checks generator, image enhancement, security and interface in a copy of the project (about 1 minute) – "
            "your cards stay untouched.",
            "Revisa generador, mejora de imagen, seguridad e interfaz en una copia del proyecto (aprox. 1 minuto); "
            "tus cartas no se tocan."),
          L("Selbsttest starten", "Start self-test", "Iniciar autoprueba"), art="lauf")
def _w_test():
    return starte_lauf("test")


@werkzeug("zip", L("Projekt-ZIP erstellen", "Create project ZIP", "Crear ZIP del proyecto"),
          L("Packt Programm, Kartenliste, Bilder und Anleitung in eine ZIP-Datei – perfekt zum Sichern oder Weitergeben. "
            "Große KI-Modelle bleiben draußen (werden bei Bedarf neu geladen).",
            "Packs program, card list, images and guide into a ZIP file – for backup or sharing. "
            "Large AI models are left out (downloaded again when needed).",
            "Empaqueta programa, lista de cartas, imágenes y guía en un ZIP, para respaldo o para compartir. "
            "Los modelos de IA grandes quedan fuera (se descargan de nuevo si hace falta)."),
          L("ZIP erstellen", "Create ZIP", "Crear ZIP"))
def _w_zip():
    _, _, ausgabe, _ = pfade()
    ausgabe.mkdir(parents=True, exist_ok=True)
    ziel = ausgabe / f"{gl.DATEI_PRAEFIX}_Projekt.zip"
    tmp = ziel.with_name(ziel.name + ".tmp")
    weglassen = {"ausgabe", "__pycache__", ".git", "_entfernt", "_alt"}
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(HIER.rglob("*")):
            rel = p.relative_to(HIER)
            if any(t in weglassen for t in rel.parts) or p.is_symlink() or not p.is_file():
                continue
            try:
                p.resolve().relative_to(HIER)
            except ValueError:
                continue
            if p.name in ("ui_einstellungen.json", "karten.bak.csv") or p.suffix in (".tmp", ".pyc"):
                continue
            if p.parent.name == "modelle" and p.suffix == ".npz" and p.stat().st_size > 5 * 1024 * 1024:
                continue
            z.write(p, Path(gl.DATEI_PRAEFIX) / "Programm" / rel)
        z.writestr(f"{gl.DATEI_PRAEFIX}/Programm/ausgabe/", "")
        for name in OBERE_DATEIEN:                       # Startdateien + Anleitung (eine Ebene über „Programm“)
            p = HIER.parent / name
            if p.is_file():
                info = zipfile.ZipInfo.from_file(p, f"{gl.DATEI_PRAEFIX}/{name}")
                info.create_system = 3                   # „Unix“ – sonst übernehmen Mac und Linux die Rechte nicht
                info.external_attr = (0o100755 if p.suffix in (".command", ".sh") else 0o100644) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, p.read_bytes())
    os.replace(tmp, ziel)
    return dict(meldung=tx("zip_ok", name=ziel.name, kb=ziel.stat().st_size // 1024), oeffnen="ausgabe")


@werkzeug("cache", L("Zwischenspeicher leeren", "Clear cache", "Vaciar memoria intermedia"),
          L("Löscht die aufbereiteten Bilder; beim nächsten Lauf werden alle neu berechnet (mit Real-ESRGAN braucht das "
            "etwas Geduld).",
            "Deletes the prepared images; the next run recalculates all of them (with Real-ESRGAN that takes a "
            "little patience).",
            "Borra las imágenes preparadas; la próxima ejecución las recalcula todas (con Real-ESRGAN hace falta "
            "un poco de paciencia)."),
          L("Leeren", "Clear", "Vaciar"))
def _w_cache():
    _, _, ausgabe, _ = pfade()
    n = 0
    for p in (ausgabe / ".cache").glob("*.jpg"):
        p.unlink(missing_ok=True)
        p.with_suffix(".json").unlink(missing_ok=True)
        n += 1
    _vorschau_cache.clear()
    return dict(meldung=tx("cache_ok", n=n))


@werkzeug("ordner-projekt", L("Projektordner öffnen", "Open project folder", "Abrir carpeta del proyecto"),
          L("Zeigt den Ordner mit allen Dateien im Explorer bzw. Finder.", "Shows the folder with all files in Explorer or Finder.",
            "Muestra la carpeta con todos los archivos en el Explorador o Finder."),
          L("Öffnen", "Open", "Abrir"), nur_rechner=True)
def _w_projekt():
    return dict(meldung=tx("geoeffnet", pfad=oeffne("projekt")))


@werkzeug("ordner-bilder", L("Bilderordner öffnen", "Open image folder", "Abrir carpeta de imágenes"),
          L("Hier liegen die Vorderseiten-Bilder.", "This is where the front images live.", "Aquí están las imágenes del anverso."),
          L("Öffnen", "Open", "Abrir"), nur_rechner=True)
def _w_bilder():
    return dict(meldung=tx("geoeffnet", pfad=oeffne("bilder")))


@werkzeug("ordner-ausgabe", L("Ausgabeordner öffnen", "Open output folder", "Abrir carpeta de salida"),
          L("Hier liegen Druckdateien, Prüfbogen und Einzelbilder.", "Print files, proof sheet and single images are here.",
            "Aquí están los archivos de impresión, la hoja de control y las imágenes."),
          L("Öffnen", "Open", "Abrir"), nur_rechner=True)
def _w_ausgabe():
    return dict(meldung=tx("geoeffnet", pfad=oeffne("ausgabe")))


@werkzeug("csv", L("Kartenliste extern öffnen", "Open card list externally", "Abrir la lista de cartas fuera"),
          L("Öffnet karten.csv mit Excel oder dem Standardprogramm. Danach hier einfach die Seite neu laden.",
            "Opens karten.csv in Excel or the default program. Afterwards just reload this page.",
            "Abre karten.csv con Excel o el programa predeterminado. Después solo recarga esta página."),
          L("Öffnen", "Open", "Abrir"), nur_rechner=True)
def _w_csv():
    return dict(meldung=tx("geoeffnet", pfad=oeffne("karten")))


# =============================================================================================
# Hilfe: Markdown → HTML (klein, ohne Zusatzpakete; alles maskiert)
# =============================================================================================
def _inline(t):
    t = html.escape(t, quote=True).replace("\\|", "|")
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?!\w)", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\((https://[^)\s\"'<>]+)\)", r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>', t)
    return t


def markdown_html(text):
    zeilen, aus, i, vorher = text.splitlines(), [], 0, -1
    while i < len(zeilen):
        if i == vorher:  # Schutz: kein Block kam weiter → Zeile als Text übernehmen
            aus.append("<p>" + _inline(zeilen[i].strip()) + "</p>")
            i += 1
            continue
        vorher = i
        z = zeilen[i]
        if z.startswith("```"):
            j = i + 1
            while j < len(zeilen) and not zeilen[j].startswith("```"):
                j += 1
            aus.append("<pre><code>" + html.escape("\n".join(zeilen[i + 1:j])) + "</code></pre>")
            i = j + 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)", z)
        if m:
            n = len(m.group(1))
            aus.append(f"<h{n}>{_inline(m.group(2))}</h{n}>")
            i += 1
            continue
        if z.strip().startswith("|") and i + 1 < len(zeilen) and re.match(r"^\s*\|[\s:|-]+\|\s*$", zeilen[i + 1]):
            def zellen(s):
                s = s.strip().strip("|")
                return [c.strip() for c in re.split(r"(?<!\\)\|", s)]
            kopf = zellen(z)
            i += 2
            koerper = []
            while i < len(zeilen) and zeilen[i].strip().startswith("|"):
                koerper.append(zellen(zeilen[i]))
                i += 1
            aus.append("<table><thead><tr>" + "".join(f"<th>{_inline(c)}</th>" for c in kopf) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>" for r in koerper)
                       + "</tbody></table>")
            continue
        if re.match(r"^\s*([-*]|\d+\.)\s+", z):
            liste = []
            while i < len(zeilen) and (re.match(r"^\s*([-*]|\d+\.)\s+", zeilen[i]) or
                                       (zeilen[i].startswith("   ") and zeilen[i].strip())):
                liste.append(zeilen[i])
                i += 1
            aus.append(_liste(liste))
            continue
        if z.startswith(">"):
            block = []
            while i < len(zeilen) and zeilen[i].startswith(">"):
                block.append(zeilen[i].lstrip("> "))
                i += 1
            aus.append("<blockquote><p>" + _inline(" ".join(block)) + "</p></blockquote>")
            continue
        if z.strip() in ("---", "***"):
            aus.append("<hr>")
            i += 1
            continue
        if not z.strip():
            i += 1
            continue
        # Absatz: die erste Zeile gehört immer dazu (auch „|“ ohne Trennzeile) → i wächst garantiert
        absatz = [z.strip()]
        i += 1
        while i < len(zeilen) and zeilen[i].strip() and not re.match(r"^(#{1,4}\s|```|\s*([-*]|\d+\.)\s|\||>)", zeilen[i]):
            absatz.append(zeilen[i].strip())
            i += 1
        aus.append("<p>" + _inline(" ".join(absatz)) + "</p>")
    return "\n".join(aus)


def _liste(zeilen):
    def einzug(z):
        return len(z) - len(z.lstrip(" "))
    basis = einzug(zeilen[0])
    geordnet = bool(re.match(r"^\s*\d+\.", zeilen[0]))
    teile, aktuell = [], None
    for z in zeilen:
        if einzug(z) <= basis and re.match(r"^\s*([-*]|\d+\.)\s+", z):
            aktuell = [re.sub(r"^\s*([-*]|\d+\.)\s+", "", z), []]
            teile.append(aktuell)
        elif aktuell is not None:
            aktuell[1].append(z)
    tag = "ol" if geordnet else "ul"
    out = []
    for text, unter in teile:
        inhalt = _inline(text)
        if unter:
            if re.match(r"^\s*([-*]|\d+\.)\s+", unter[0]):
                inhalt += _liste(unter)
            else:
                inhalt += " " + _inline(" ".join(u.strip() for u in unter))
        out.append(f"<li>{inhalt}</li>")
    return f"<{tag}>" + "".join(out) + f"</{tag}>"


def hilfe_datei(doc, sprache):
    if doc == "spec":
        return HIER / "SPEC.md"
    p = HIER / ("LEITFADEN.md" if sprache == "de" else f"LEITFADEN_{sprache}.md")
    return p if p.exists() else HIER / "LEITFADEN.md"


_HILFE_CACHE = {}  # Pfad → (Änderungszeit, Größe, HTML)


_KARTENSPRACHE_MARKE = re.compile(r"\{\{(Spanisch|Spanish|español|Español)\}\}")
_MARKE_SPRACHE = {"Spanisch": "de", "Spanish": "en", "español": "es", "Español": "es"}


def kartensprache_text(text, zs=None):
    """Leitfäden: {{Spanisch}} / {{Spanish}} / {{español}} = Name der Kartensprache in der Sprache der Marke
    (bei es nur die Klammern weg; „{{Español}}“ am Satzanfang groß)."""
    zs = zs or zielsprache()

    def tausch(m):
        if zs == "es":
            return m.group(1)
        n = gl.zs_name(_MARKE_SPRACHE[m.group(1)], zs)
        return n[:1].upper() + n[1:] if m.group(1)[:1].isupper() else n
    return _KARTENSPRACHE_MARKE.sub(tausch, text)


def hilfe_html(pfad):
    """Gerendertes HTML einer Hilfe-Datei; je Datei + Änderungszeit + Kartensprache zwischengespeichert."""
    try:
        st = pfad.stat()
    except OSError:
        return markdown_html(f"# {pfad.name}")
    zs = zielsprache()
    schluessel = (st.st_mtime_ns, st.st_size, zs)
    eintrag = _HILFE_CACHE.get(str(pfad))
    if eintrag and eintrag[0] == schluessel:
        return eintrag[1]
    ergebnis = markdown_html(kartensprache_text(pfad.read_text(encoding="utf-8"), zs))
    _HILFE_CACHE[str(pfad)] = (schluessel, ergebnis)
    return ergebnis


# =============================================================================================
# HTTP-Server
# =============================================================================================
SPERRSEITE = """<!doctype html><html><head><meta charset="utf-8"><title>Me Goos-ta Deutsch</title>
<style>body{font-family:system-ui,sans-serif;background:#E8F2FA;color:#1B2D4F;display:grid;place-items:center;
min-height:100vh;margin:0}main{max-width:520px;padding:32px;background:#fff;border-radius:16px;text-align:center}
img{width:96px;height:96px}</style></head><body><main><img src="/symbol.svg" alt="">
<h1>Me Goos-ta Deutsch</h1>
<p>Bitte über das Desktop-Symbol „Me Goos-ta Deutsch“ oder die Startdatei im Programmordner öffnen.</p>
<p>Please open it with the “Me Goos-ta Deutsch” desktop icon or the start file in the program folder.</p>
<p>Ábrelo con el icono «Me Goos-ta Deutsch» del escritorio o con el archivo de inicio de la carpeta del programa.</p>
</main></body></html>"""


# =============================================================================================
# Anfragen: Logik ohne HTTP-Server (verarbeite, Anfrage) + dünne Hülle für den lokalen Server (Handler)
# =============================================================================================
OEFFENTLICH = {"/symbol.svg", "/favicon.ico", "/apple-touch-icon.png", "/apple-touch-icon-precomposed.png"}
# Was Handy-Zugang und Web-App nicht dürfen (POST): Beenden, Deinstallieren, am Rechner öffnen, Start-/Handy-Einstellungen,
# Versionsprüfung (betrifft nur das Programm am Rechner)
NUR_RECHNER_WEGE = {"/api/deinstallieren", "/api/beenden", "/api/oeffnen", "/api/lan", "/api/start-einstellung",
                    "/api/neue-version"}


def oeffentlich(weg):
    """Adressen ohne Sitzung (Symbole, Schriften) – alles andere braucht das Cookie."""
    return weg in OEFFENTLICH or weg.startswith("/schrift/")


class _Kopf(dict):
    """Kopfzeilen als Wörterbuch ohne Unterschied von Groß-/Kleinschreibung (wie die des HTTP-Servers)."""

    def __init__(self, kopf=None):
        super().__init__((str(k).lower(), v) for k, v in dict(kopf or {}).items())

    def get(self, k, vorgabe=None):
        return super().get(str(k).lower(), vorgabe)


def _nur_rechner_text():
    """403-Text für Wege, die nur am Rechner gehen: Handy-Zugang wie bisher, in der Web-App eigener Text."""
    if erweiterungen and not im_browser():
        return erweiterungen._lan_tx("lan_nur_rechner")
    return tx("nur_rechner")


def _fehler_antwort(a, e, post=False):
    """Ausnahme → Fehlerantwort wie bisher: Meldung mit eigenem Status, Übersetzung 409/400, Eingabefehler 400
    (bei POST auch RuntimeError), alles andere 500."""
    if isinstance(e, Meldung):
        return a._senden(e.status, {"fehler": str(e), **e.extra})
    if isinstance(e, uebersetzer.UebersetzungsFehler):
        return a._fehler(409 if e.code == "zustimmung" else 400, e.text(gl.sprache()), e.code)
    if isinstance(e, (ValueError, FileNotFoundError)) or (post and isinstance(e, RuntimeError)):
        return a._fehler(400, str(e) or tx("ungueltig"))
    return a._fehler(500, tx("intern", fehler=f"{type(e).__name__}: {e}"))


def seite_html(nonce, am_handy=False):
    """Die Oberfläche (ui/index.html) mit Token, Nonce, Sprache, Farben und Handy-Merker."""
    seite = (UI_DATEI.read_text(encoding="utf-8").replace("__GL_TOKEN__", TOKEN)
             .replace("__NONCE__", nonce).replace("__SPRACHE__", lade_sprache())
             .replace("/*__GL_FARBEN__*/", farben_info()["css"])
             .replace("__GL_HANDY__", "1" if am_handy else "0").replace("__GL_APP__", "0"))   # Web-App: bau_webapp.py
    return seite.replace('<meta name="theme-color" content="__GL_THEME__">', farben_info()["meta"])


def verarbeite(methode, weg, abfrage="", koerper=b"", kopf=None, am_handy=False):
    """Alle Adressen der Oberfläche ohne HTTP-Server → (Status, Kopf, Inhalt als Bytes). Host-, Origin-, Cookie- und
    Token-Prüfung macht der Aufrufer (Handler); die Web-App (Pyodide) ruft das direkt auf. Neue Adressen nur hier
    (bzw. in Anfrage._get/_post). abfrage: Text nach „?“ oder dict; koerper: Bytes oder Strom (Länge aus
    Content-Length); am_handy: Handy-Zugang bzw. Browser-Fassung (dann sind Rechner-Wege gesperrt)."""
    a = Anfrage(methode, kopf, koerper, am_handy or im_browser())
    _lern_lokal.liste = []
    a._sprache_setzen()
    if isinstance(abfrage, str):
        q = parse_qs(abfrage)
    else:
        q = {str(k): [str(x) for x in v] if isinstance(v, (list, tuple)) else [str(v)] for k, v in (abfrage or {}).items()}
    post = methode == "POST"
    try:
        if post and a.am_handy and weg in NUR_RECHNER_WEGE:
            a._fehler(403, _nur_rechner_text())
        elif post:
            a._post(weg, q)
        elif methode in ("GET", "HEAD"):
            a._get(weg, q)
        else:
            a._fehler(405, tx("ungueltig"))
    except Exception as e:  # noqa: BLE001
        _fehler_antwort(a, e, post)
    if a.antwort is None:
        a._fehler(404, tx("unbekannt"))
    return a.antwort


class Anfrage:
    """Eine Anfrage ohne Socket. Die Wege antworten mit self._senden(...) wie früher im Handler; das Ergebnis steht
    danach in self.antwort = (Status, Kopf, Inhalt). erweiterungen.get/post/post_roh bekommen dieses Objekt."""

    def __init__(self, methode, kopf=None, koerper=b"", am_handy=False):
        self.command = methode
        if hasattr(kopf, "get") and not isinstance(kopf, dict):     # Kopfzeilen des HTTP-Servers
            self.headers = kopf
        else:
            self.headers = _Kopf(kopf)
            if isinstance(koerper, (bytes, bytearray)) and self.headers.get("Content-Length") is None:
                self.headers["content-length"] = str(len(koerper))
        roh = koerper is None or isinstance(koerper, (bytes, bytearray))
        self.rfile = io.BytesIO(bytes(koerper or b"")) if roh else koerper
        self.am_handy = bool(am_handy)
        self.antwort = None

    # ---------- Antworten ----------
    def _senden(self, status, inhalt, mime="application/json; charset=utf-8", extra=None, nonce=None):
        zurueck = getattr(_lern_lokal, "liste", None)
        if zurueck and isinstance(inhalt, dict) and status < 400:   # Karte geändert → Lernstand zurückgesetzt
            inhalt = dict(inhalt, lernstand_zurueckgesetzt=list(zurueck), lernstand_meldung=_lern_meldung(zurueck))
            _lern_lokal.liste = []
        if isinstance(inhalt, (dict, list)):
            inhalt = json.dumps(inhalt, ensure_ascii=False).encode("utf-8")
        elif isinstance(inhalt, str):
            inhalt = inhalt.encode("utf-8")
        self.antwort = (status, {"Content-Type": mime, **(extra or {})}, inhalt)

    def _fehler(self, status, text, code=None):
        self._senden(status, {"fehler": text, "code": code} if code else {"fehler": text})

    def _json(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_JSON:
            raise Meldung("anfrage_gross", status=413)
        roh = self.rfile.read(n) if n else b""
        daten = json.loads(roh.decode("utf-8")) if roh else {}
        if not isinstance(daten, dict):
            raise Meldung("ungueltig")
        return daten

    def _datei(self, pfad, inline=True):
        if not pfad or not pfad.is_file():
            return self._fehler(404, tx("datei_fehlt"))
        mime = mimetypes.guess_type(pfad.name)[0] or "application/octet-stream"
        if pfad.suffix.lower() not in SICHERE_ENDUNGEN | {".ttf", ".svg", ".ico"}:
            inline, mime = False, "application/octet-stream"
        dispo = ("inline" if inline else "attachment") + f"; filename*=UTF-8''{quote(pfad.name)}"
        extra = {"Content-Disposition": dispo}
        if pfad.suffix.lower() in (".ttf", ".svg", ".ico"):
            extra["Cache-Control"] = "max-age=3600"
        self._senden(200, pfad.read_bytes(), mime, extra)

    def _bild_senden(self, inhalt, mime="image/jpeg"):
        if not inhalt:
            return self._fehler(404, tx("datei_fehlt"))
        return self._senden(200, inhalt, mime)

    def _sprache_setzen(self):
        s = (self.headers.get("X-GL-Sprache") or "").lower()
        gl.setze_sprache(s if s in gl.SPRACHEN else lade_sprache())

    # ---------- GET ----------
    def _get(self, weg, q):
        if weg == "/symbol.svg":
            return self._datei(HIER / "assets" / "me-goosta-symbol.svg")
        if weg == "/favicon.ico":
            return self._datei(HIER / "assets" / "me-goosta-symbol.ico")
        if weg in ("/apple-touch-icon.png", "/apple-touch-icon-precomposed.png"):     # „Zum Home-Bildschirm“
            return self._datei(HIER / "assets" / "me-goosta-symbol.png")
        if weg.startswith("/schrift/"):
            name = weg.rsplit("/", 1)[-1]
            if not re.fullmatch(r"Poppins-(Regular|Medium|Bold)\.ttf", name):
                return self._fehler(404, tx("unbekannt"))
            return self._datei(HIER / "schrift" / name)
        return self._get_api(weg, q)

    def _lernen_get(self, weg, eins):
        _lernen_pruefen()
        st = _lernstand()
        try:
            if weg == "/api/lernen":
                return self._senden(200, lernen_info())
            if weg == "/api/lernen-karte":
                return self._senden(200, st.naechste_karte(_lern_karten(), eins("stapel") or None, sprache=gl.sprache()))
            if weg == "/api/lernen-export":
                inhalt = json.dumps(st.export(), ensure_ascii=False, indent=1)
                name = f"{gl.DATEI_PRAEFIX}_Lernstand_{time.strftime('%Y-%m-%d')}.json"
                return self._senden(200, inhalt, "application/json; charset=utf-8",
                                    {"Content-Disposition": f"attachment; filename*=UTF-8''{quote(name)}"})
        except lernen.LernFehler as e:
            raise _lern_meldung_fehler(e) from None
        return self._fehler(404, tx("unbekannt"))

    def _get_api(self, weg, q):
        eins = lambda k, d="": q.get(k, [d])[0]                          # noqa: E731
        if weg == "/api/status":
            return self._senden(200, status_info())
        if weg == "/api/optionen":
            return self._senden(200, dict(gruppen=schema(), werte=lade_einstellungen()))
        if weg == "/api/farben":
            return self._senden(200, farben_info())
        if weg == "/api/app-sicherung" and im_browser():         # Web-App: ganzer Stand als ZIP („Alles sichern“)
            inhalt, name = app_sicherung()
            return self._senden(200, inhalt, "application/zip",
                                {"Content-Disposition": f"attachment; filename*=UTF-8''{quote(name)}"})
        if weg == "/api/karten":
            return self._senden(200, karten_daten())
        if weg == "/api/ergebnisse":
            return self._senden(200, ergebnisse())
        if weg == "/api/werkzeuge":
            return self._senden(200, werkzeuge_liste())
        if weg == "/api/tools" and tools:
            return self._senden(200, tools_info())
        if weg.startswith("/api/lernen") and lernen:
            return self._lernen_get(weg, eins)
        if weg == "/api/lauf":                                # laufender bzw. letzter Auftrag (oder ?id=)
            ab = int(eins("ab", "0") or 0)
            lauf = warteschlange.finde(eins("id")) if eins("id") else warteschlange.letzter
            st = lauf.status(ab) if lauf else {}
            st.update(warteschlange=warteschlange.anzahl, aktiv=warteschlange.aktiv.id if warteschlange.aktiv else None)
            return self._senden(200, st)
        if weg == "/api/warteschlange":
            return self._senden(200, warteschlange.uebersicht())
        if weg == "/api/befehl":
            extra = {"nur": eins("nur", "alles"), "karten": eins("karten")}
            if extra["nur"] != "vorlagen":                     # Rückseite in der gewählten Sprache (Standard Zielsprache)
                wahl = eins("sprache")
                extra["sprache"] = wahl if wahl and sprachen and wahl in sprachen.SPRACHEN else zielsprache()
            argv = argv_aus(lade_einstellungen(), extra)
            return self._senden(200, dict(befehl=befehlszeile(argv), fehler=parse(argv)[1]))
        if weg == "/api/hilfe":
            pfad = hilfe_datei(eins("doc", "leitfaden"), gl.sprache())
            return self._senden(200, dict(html=hilfe_html(pfad), datei=pfad.name))
        if weg == "/api/vorschau":
            erg = vorschau(eins("bild"), eins("es"), eins("fit", "contain"), eins("seite", "vorn"))
            if not erg:
                return self._fehler(404, tx("datei_fehlt"))
            return self._senden(200, erg[0], erg[1], {"X-MGD-Schnell": "1" if erg[2] else "0"})
        if weg == "/api/entwuerfe":
            return self._senden(200, [entwurf_pruefen(m["id"], {}) for m in _alle_entwuerfe()])
        if weg == "/api/gans-bild":
            return self._senden(200, gans_bild_info())
        if weg == "/api/rueckseite":
            erg = rueckseite(eins("es"))
            return self._bild_senden(erg[0] if erg else None, erg[1] if erg else "image/png")
        if weg == "/api/verbesserung":
            return self._senden(200, verbesserung_uebersicht())
        if weg == "/api/vergleich":
            art = eins("art", "nachher")
            return self._bild_senden(vergleich_bild(eins("bild"), "vorher" if art == "vorher" else "nachher"))
        if weg == "/api/tabelle":
            return self._senden(200, tabelle())
        if weg == "/api/uebersetzung":
            return self._senden(200, uebersetzung_info())
        if weg == "/api/zielsprache":
            return self._senden(200, zielsprache_info())
        if weg == "/api/ki-bild" and ki_bild:
            return self._senden(200, ki_bild_info())
        if weg == "/api/ki-bild-bild" and ki_bild:
            ki_png, ki_jpg, _ = _ki_pfade(eins("id"))
            pfad = ki_jpg if eins("art") == "vorschau" else ki_png
            if not pfad.is_file():
                return self._fehler(404, tx("ki_bild_fehlt"))
            return self._senden(200, pfad.read_bytes(), "image/jpeg" if pfad.suffix == ".jpg" else "image/png")
        if weg == "/api/entwurf-bild":
            erg = entwurf_bild(eins("id"), eins("art", "original"), int(eins("drehung", "0") or 0) % 360,
                               eins("fit") or None)
            if not erg:
                return self._fehler(404, tx("datei_fehlt"))
            return self._senden(200, erg[0], erg[1])
        if weg.startswith("/bild/"):
            _, bilder, _, _ = pfade()
            pfad = sicher_in(bilder, weg[len("/bild/"):])
            if pfad.suffix.lower() not in gl.BILD_ENDUNGEN:
                raise Meldung("ungueltig")
            return self._datei(pfad)
        if weg.startswith("/datei/"):
            _, _, ausgabe, vorlagen = pfade()
            gruppe, _, name = weg[len("/datei/"):].partition("/")
            basis = {"ausgabe": ausgabe, "vorlagen": vorlagen, "einzelbilder": ausgabe / "einzelbilder",
                     "digital": ausgabe / "digital"}.get(gruppe)
            if basis is None:
                raise Meldung("ungueltig")
            pfad = sicher_in(basis, name)
            # .zip, .apkg und die Lernseite (.html) nur als Download – die Lernseite läuft so nie unter dieser Adresse
            return self._datei(pfad, inline=pfad.suffix.lower() not in (".zip", ".apkg", ".html"))
        if erweiterungen and erweiterungen.get(self, weg, q):         # Import/Export, Ideen, Programmstart
            return
        return self._fehler(404, tx("unbekannt"))

    # ---------- POST ----------
    def _post(self, weg, q):
        if weg in ("/api/entwurf", "/api/gans-bild"):          # Bild als rohe Bytes
            n = int(self.headers.get("Content-Length") or 0)
            if n <= 0 or n > MAX_BILD:
                return self._senden(400, {"fehler": gl.pm("b_datei_gross", "fehler", mb=gl.MAX_DATEI_MB)["text"]})
            daten = self.rfile.read(n)
            if weg == "/api/gans-bild":
                return self._senden(200, gans_bild_laden(daten))
            return self._senden(200, entwurf_anlegen(daten, q.get("name", [""])[0], q.get("karte", [""])[0]))
        if weg == "/api/app-sicherung" and im_browser():         # Web-App: „Sicherung einspielen“ (ZIP als rohe Bytes)
            n = int(self.headers.get("Content-Length") or 0)
            if n > SICHERUNG_MAX:
                raise Meldung("sicherung_gross", status=413, mb=SICHERUNG_MAX // (1024 * 1024))
            return self._senden(200, app_sicherung_einspielen(self.rfile.read(n) if n else b""))
        if erweiterungen and weg in erweiterungen.ROH_WEGE and erweiterungen.post_roh(self, weg, q):
            return
        daten = self._json()
        if weg == "/api/sprache":
            s = speichere_sprache(str(daten.get("sprache", "")))
            gl.setze_sprache(s)
            return self._senden(200, {"sprache": s})
        if weg == "/api/zielsprache":
            return self._senden(200, setze_zielsprache(daten.get("zielsprache")))
        if weg == "/api/farben":
            if daten.get("zuruecksetzen") is True:
                return self._senden(200, speichere_farben("himmel", {}))
            if daten.get("speichern") is False:                # nur Vorschau (prüft, speichert nichts)
                s, e = farben_pruefen(daten.get("schema"), daten.get("eigene"))
                return self._senden(200, farben_info(s, e))
            return self._senden(200, speichere_farben(daten.get("schema"), daten.get("eigene")))
        if weg == "/api/einstellungen":
            werte = speichere_einstellungen(daten.get("werte", {}))
            argv = argv_aus(werte)
            _vorschau_cache.clear()
            return self._senden(200, dict(werte=werte, fehler=parse(argv)[1], befehl=befehlszeile(argv)))
        if weg == "/api/karten":
            return self._senden(200, speichere_karten(daten))
        if weg == "/api/lauf":
            bilder = daten.get("bilder") if isinstance(daten.get("bilder"), list) else None
            return self._senden(200, starte_lauf(str(daten.get("art", "generator")), daten.get("nur"),
                                                 daten.get("karten"), bilder=bilder, alle=daten.get("alle") is True,
                                                 ki=daten, ohne_tool=daten.get("ohne_tool") is True,
                                                 sprache_wahl=daten.get("sprache") if isinstance(daten.get("sprache"),
                                                                                                str) else None))
        if weg == "/api/ki-bild-uebernehmen" and ki_bild:
            return self._senden(200, ki_bild_uebernehmen(daten))
        if weg == "/api/lauf-stopp":
            warteschlange.stoppen()
            return self._senden(200, {"ok": True})
        if weg == "/api/warteschlange":
            return self._senden(200, warteschlange.aktion(str(daten.get("aktion", "")), str(daten.get("id", ""))))
        if weg == "/api/tool" and tools:
            return self._senden(200, tool_aktion(daten))
        if weg.startswith("/api/lernen") and lernen:
            return self._senden(200, lernen_post(weg, daten))
        if weg == "/api/tools-erstabfrage" and tools:
            return self._senden(200, tools_erstabfrage(daten))
        if weg == "/api/oeffnen":
            return self._senden(200, {"pfad": oeffne(str(daten.get("ziel", "")))})
        if weg == "/api/bild-weg":
            return self._senden(200, bild_weg(str(daten.get("name", ""))))
        if weg == "/api/werkzeug":
            w = next((w for w in WERKZEUGE if w["id"] == daten.get("id")), None)
            if not w:
                return self._fehler(404, tx("unbekannt"))
            if _werkzeug_nur_rechner(w) and self.am_handy:
                return self._fehler(403, _nur_rechner_text())
            return self._senden(200, w["fn"]() or {})
        if weg == "/api/entwurf-pruefen":
            return self._senden(200, entwurf_pruefen(daten.get("id"), daten))
        if weg == "/api/entwurf-uebernehmen":
            return self._senden(200, entwurf_uebernehmen(daten.get("id"), daten))
        if weg == "/api/entwurf-weg":
            return self._senden(200, entwurf_weg(daten.get("id")))
        if weg == "/api/karte-pruefen":
            return self._senden(200, karte_pruefen(daten))
        if weg == "/api/karte-speichern":
            return self._senden(200, karte_speichern(daten))
        if weg == "/api/karte-status":
            return self._senden(200, karte_status(daten))
        if weg == "/api/karte-bild-zurueck":
            return self._senden(200, karte_bild_zurueck(daten))
        if weg == "/api/gans-bild-weg":
            return self._senden(200, gans_bild_weg())
        if weg == "/api/gans-bild-zurueck":
            return self._senden(200, gans_bild_zurueck())
        if weg == "/api/uebersetzung":
            return self._senden(200, uebersetzung_setzen(daten))
        if weg == "/api/uebersetzen":
            return self._senden(200, uebersetzen(daten))
        if weg == "/api/neue-version":                         # nur auf Klick „Nach neuer Version suchen“
            return self._senden(200, neue_version())
        if weg == "/api/ki-bild-prompt" and ki_bild:
            return self._senden(200, ki_bild_prompt_setzen(daten))
        if weg == "/api/ki-bild-text" and ki_bild:
            return self._senden(200, ki_bild_text(daten))
        if weg == "/api/ki-bild-uebersetzen":                    # Beschreibung → Englisch (nur nach Zustimmung)
            return self._senden(200, uebersetzer.beschreibung_englisch(
                str(daten.get("text") or ""), str(daten.get("sprache") or gl.sprache())))
        if weg == "/api/beenden":
            self._senden(200, {"meldung": tx("beendet")})
            threading.Thread(target=beenden, daemon=True).start()
            return
        if erweiterungen and erweiterungen.post(self, weg, daten):
            return
        return self._fehler(404, tx("unbekannt"))


class Handler(BaseHTTPRequestHandler):
    """Hülle für den lokalen Server: prüft Host, Origin, Cookie und Token, liefert die Seite aus und reicht alles
    andere an verarbeite() weiter."""
    server_version = "MeGoostaDeutsch"
    sys_version = ""
    timeout = 120

    def log_message(self, fmt, *args):                    # ruhig in der Konsole
        pass

    # ---------- Prüfungen ----------
    def _host_ok(self):
        if erweiterungen and erweiterungen.lan_ist(self):           # Handy-Zugang: nur die eigene WLAN-Adresse
            return erweiterungen.lan_host_ok(self)
        host = (self.headers.get("Host") or "").strip().lower()
        return host in (f"127.0.0.1:{PORT}", f"localhost:{PORT}")

    def _origin_ok(self):
        if erweiterungen and erweiterungen.lan_ist(self):
            return erweiterungen.lan_origin_ok(self)
        o = self.headers.get("Origin")
        return o is None or o in (f"http://127.0.0.1:{PORT}", f"http://localhost:{PORT}")

    def _cookie_ok(self):
        roh = self.headers.get("Cookie") or ""
        for teil in roh.split(";"):
            k, _, v = teil.strip().partition("=")
            if k == f"mgd_{PORT}" and hmac.compare_digest(v.encode(), TOKEN.encode()):
                return True
        return False

    def _kopf_token_ok(self):
        return hmac.compare_digest((self.headers.get("X-GL-Token") or "").encode(), TOKEN.encode())

    def _am_handy(self):
        return bool(erweiterungen and erweiterungen.lan_ist(self))

    # ---------- Antworten ----------
    def _senden(self, status, inhalt, mime="application/json; charset=utf-8", extra=None, nonce=None):
        if isinstance(inhalt, (dict, list)):
            inhalt = json.dumps(inhalt, ensure_ascii=False).encode("utf-8")
        elif isinstance(inhalt, str):
            inhalt = inhalt.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(inhalt)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=(), usb=()")
        if mime.startswith("text/html"):                       # PDFs/Bilder ohne CSP (sonst zeigt Chrome keine PDFs)
            skript = f"'nonce-{nonce}'" if nonce else "'none'"
            self.send_header("Content-Security-Policy",
                             f"default-src 'none'; script-src {skript}; style-src 'self' 'unsafe-inline'; "
                             "img-src 'self' blob: data:; font-src 'self'; connect-src 'self'; "
                             "object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(inhalt)

    def _fehler(self, status, text, code=None):
        self._senden(status, {"fehler": text, "code": code} if code else {"fehler": text})

    def _antwort(self, erg):
        status, kopf, inhalt = erg
        kopf = dict(kopf)
        self._senden(status, inhalt, kopf.pop("Content-Type", "application/json; charset=utf-8"), kopf)

    def _sprache_setzen(self):
        s = (self.headers.get("X-GL-Sprache") or "").lower()
        gl.setze_sprache(s if s in gl.SPRACHEN else lade_sprache())

    # ---------- GET ----------
    def do_GET(self):
        _lern_lokal.liste = []
        if not self._host_ok():
            return self._fehler(403, tx("nur_lokal"))
        self._sprache_setzen()
        url = urlparse(self.path)
        weg = unquote(url.path)
        if weg in ("/", "/index.html"):
            try:
                return self._seite(parse_qs(url.query))
            except Exception as e:  # noqa: BLE001
                return _fehler_antwort(self, e)
        if not oeffentlich(weg) and not self._cookie_ok():
            return self._fehler(403, tx("sitzung"))
        return self._antwort(verarbeite(self.command, weg, url.query, None, self.headers, self._am_handy()))

    def _seite(self, q):
        schluessel = q.get("k", [""])[0]
        if schluessel and hmac.compare_digest(schluessel.encode(), START_SCHLUESSEL.encode()):
            self.send_response(303)
            self.send_header("Location", "/")
            self.send_header("Set-Cookie", f"mgd_{PORT}={TOKEN}; HttpOnly; SameSite=Strict; Path=/")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if not self._cookie_ok():
            if self._am_handy():                                 # Handy: erst die PIN
                return erweiterungen.lan_pin_seite(self)
            return self._senden(403, SPERRSEITE, "text/html; charset=utf-8")
        nonce = secrets.token_urlsafe(16)
        return self._senden(200, seite_html(nonce, self._am_handy()), "text/html; charset=utf-8", nonce=nonce)

    # ---------- POST ----------
    def do_POST(self):
        _lern_lokal.liste = []
        if not self._host_ok() or not self._origin_ok():
            return self._fehler(403, tx("nur_lokal"))
        self._sprache_setzen()
        if erweiterungen and self.path == "/lan-pin" and erweiterungen.lan_ist(self):
            return erweiterungen.lan_pin(self)
        if not (self._cookie_ok() and self._kopf_token_ok()):
            return self._fehler(403, tx("sitzung"))
        url = urlparse(self.path)
        return self._antwort(verarbeite("POST", url.path, url.query, self.rfile, self.headers, self._am_handy()))

    def do_HEAD(self):
        return self.do_GET()

    def do_OPTIONS(self):                                  # keine CORS-Freigaben
        return self._fehler(405, tx("ungueltig"))

    do_PUT = do_DELETE = do_PATCH = do_OPTIONS


_schriften = {}


def status_info():
    if not _schriften:
        _schriften.update(gl.registriere_schriften())
    schriften = _schriften
    try:
        import pypdfium2  # noqa: F401
        pdfium = True
    except Exception:  # noqa: BLE001 – ImportError, aber auch eine von Windows gesperrte DLL (OSError)
        pdfium = False
    vorschau_art = "pdfium" if pdfium else "pillow" if gl.leinwand_da() else ""   # ohne pypdfium2: Rückseite mit Pillow
    _, cfg = aktuelle_konfig()
    _, _, ausgabe, _ = pfade()
    bericht = lies_bericht(ausgabe)
    methode = gl.ki_methode(cfg.ki)
    ue = uebersetzer.lade_einstellungen()
    return dict(produkt=gl.PRODUKT, version=gl.VERSION, ui_version=UI_VERSION, python=sys.version.split()[0],
                uebersetzung=dict(zugestimmt=ue["zugestimmt"], dienst=ue["dienst"], automatisch=ue["automatisch"]),
                projekt=str(HIER), schrift=schriften.get("bold"), ki_methode=methode,
                ki_name=gl.METHODE_NAME.get(methode, methode),
                modelle={m: ki_modelle.verfuegbar(m) for m in ("realesrgan-x4plus", "realesrgan-x2plus")},
                fsrcnn=gl.FSRCNN.verfuegbar(2), vorschau=bool(vorschau_art), vorschau_art=vorschau_art,
                letzter_lauf=bericht.get("zeit"), web_app=im_browser(),
                plattform=sys.platform, sprache=lade_sprache(), lauf=bool(warteschlange.aktiv),
                warteschlange=warteschlange.anzahl + bool(warteschlange.aktiv),
                ki_bild=bool(ki_bild) and not im_browser(), tools={tid: tools.installiert(tid) for tid in tools.TOOLS} if tools else {},
                zielsprache=zielsprache_info(), web_adresse=web_adresse())


def web_adresse():
    """Adresse der Handy-App (Web-App) – steht an genau einer Stelle: web_adresse.txt (leer = noch nicht veröffentlicht)."""
    try:
        zeile = (HIER / "web_adresse.txt").read_text(encoding="utf-8").strip().splitlines()[0].strip()
    except (OSError, IndexError):
        return ""
    return zeile if re.fullmatch(r"https://[A-Za-z0-9.-]+(/[A-Za-z0-9._~/-]*)?", zeile) else ""


# =============================================================================================
# Nach neuer Version suchen – nur auf Klick (Hilfe → Über), nie beim Start oder im Hintergrund; nichts wird gespeichert
# =============================================================================================
VERSION_MAX_ANTWORT = 200_000                                 # Bytes; eine Release-Antwort von GitHub hat ~5–20 KB


def version_tupel(text):
    """„v2.10“ → (2, 10, 0); alles andere (latest, v2, HTML …) → None."""
    m = re.fullmatch(r"v?(\d{1,4})\.(\d{1,4})(?:\.(\d{1,4}))?", str(text or "").strip())
    return (int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)) if m else None


def release_quelle():
    """(Konto, Repository) nur aus web_adresse.txt (https://<konto>.github.io/<repo>/) – sonst None."""
    m = re.fullmatch(r"https://([a-z0-9](?:[a-z0-9-]{0,38}))\.github\.io/((?!\.)[A-Za-z0-9._-]{1,100})/", web_adresse())
    return (m.group(1), m.group(2)) if m else None


def neue_version(abruf=None):
    """Fragt GitHub nach dem neuesten Release. Ausgewertet werden nur tag_name und published_at (kein Text, keine Links
    aus der Antwort). abruf: Ersatz für uebersetzer.http_json (Tests)."""
    quelle = release_quelle()
    if not quelle:
        raise Meldung("nv_kein_release", 409, extra={"code": "kein_release"})
    adresse = f"https://api.github.com/repos/{quelle[0]}/{quelle[1]}/releases/latest"
    try:
        d = (abruf or uebersetzer.http_json)(adresse, kopf={"Accept": "application/vnd.github+json"},
                                             hosts=("api.github.com",), max_antwort=VERSION_MAX_ANTWORT)
    except uebersetzer.UebersetzungsFehler as e:
        status = e.werte.get("code")
        code = ("nv_grenze" if e.code == "zu_viele" or status in (403, 429) else "nv_noch_keins" if status == 404
                else "nv_zeit" if e.code == "zeit" else "nv_netz" if e.code in ("netz", "zertifikat") else "nv_format")
        return dict(ergebnis="fehler", code=code, meldung=tx(code))
    neu = version_tupel(d.get("tag_name") if isinstance(d, dict) else None)
    if not neu:
        return dict(ergebnis="fehler", code="nv_format", meldung=tx("nv_format"))
    datum = str(d.get("published_at") or "")[:10]
    datum = datum if re.fullmatch(r"\d{4}-\d{2}-\d{2}", datum) else ""
    eigene = str(gl.VERSION).split()[0]                         # „2.2 (21.10.2026)“ → „2.2“
    hier = version_tupel(eigene) or (0, 0, 0)
    version = ".".join(map(str, neu if neu[2] else neu[:2]))
    ergebnis = "neuer" if neu > hier else "aktuell" if neu == hier else "voraus"
    return dict(ergebnis=ergebnis, version=version, datum=datum, eigene=eigene)


# =============================================================================================
# Web-App (Pyodide im Web-Worker, gebaut von bau_webapp.py): Start, Anfragen, Sicherung des ganzen Stands
# =============================================================================================
def web_info():
    """Was die App vor dem Laden der Oberfläche braucht: Sprache, Farben, Version."""
    return dict(sprache=lade_sprache(), sprache_gewaehlt="sprache" in _lies_datei(), farben=farben_info(),
                version=gl.VERSION, ui_version=UI_VERSION)


def web_anfrage(methode, weg, abfrage="", koerper=None, kopf_json="{}"):
    """Eine Anfrage aus dem Worker → (Status, Kopf als JSON-Text, Inhalt als Bytes). koerper: Bytes oder ein
    JavaScript-Uint8Array (Pyodide: to_bytes())."""
    if koerper is not None and hasattr(koerper, "to_bytes"):
        koerper = koerper.to_bytes()
    try:
        kopf = json.loads(kopf_json or "{}")
    except ValueError:
        kopf = {}
    status, k, inhalt = verarbeite(str(methode), str(weg), str(abfrage or ""), bytes(koerper or b""), kopf)
    return status, json.dumps(k, ensure_ascii=False), bytes(inhalt or b"")


SICHERUNG_MARKE = "me-goos-ta-deutsch-app-sicherung.json"
SICHERUNG_MAX = 600 * 1024 * 1024
SICHERUNG_PROJEKT = ("karten.csv", "ideen.json", "lernstand.json", "lernstand.bak.json", "ui_einstellungen.json")
SICHERUNG_ORDNER = ("bilder", "ideen")
SICHERUNG_DATEN_WEG = {"modelle", "_pakete"}        # große Downloads (Real-ESRGAN, Pakete) lädt das Tool neu


def _sicherung_dateien():
    """[(Pfad, Name in der ZIP)] aller Nutzerdaten der App: Kartenliste, Bilder, Ideen, Lernstand, Einstellungen,
    Entwürfe und der Datenordner (Tools, Übersetzung, Sprachpakete) – ohne Programm, Ausgaben und Modelle."""
    aus = []
    for n in SICHERUNG_PROJEKT:
        p = HIER / n
        if p.is_file() and not p.is_symlink():
            aus.append((p, "projekt/" + n))
    _, _, ausgabe, _ = pfade()
    ordner = [(HIER / o, "projekt/" + o) for o in SICHERUNG_ORDNER] + [(ausgabe / ".entwuerfe", "projekt/entwuerfe")]
    ordner.append((uebersetzer.daten_ordner(), "daten"))
    for basis, ziel in ordner:
        if not basis.is_dir():
            continue
        for p in sorted(basis.rglob("*")):
            rel = p.relative_to(basis)
            if (p.is_file() and not p.is_symlink() and not (set(rel.parts) & SICHERUNG_DATEN_WEG)
                    and p.suffix not in (".part", ".tmp") and "_entfernt" not in rel.parts):
                aus.append((p, f"{ziel}/{rel.as_posix()}"))
    return aus


def app_sicherung():
    """„Alles sichern“ in der App: eine ZIP mit dem ganzen Stand (Sicherung einspielen liest sie wieder ein)."""
    puffer = io.BytesIO()
    dateien = _sicherung_dateien()
    karten = len(karten_daten()["karten"])
    with zipfile.ZipFile(puffer, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(SICHERUNG_MARKE, json.dumps(dict(art="app-sicherung", version=gl.VERSION, karten=karten,
                                                     zeit=time.strftime("%Y-%m-%d %H:%M:%S")), ensure_ascii=False))
        for p, name in dateien:
            z.write(p, name, compress_type=zipfile.ZIP_STORED if p.suffix.lower() in gl.BILD_ENDUNGEN else zipfile.ZIP_DEFLATED)
    return puffer.getvalue(), f"{gl.DATEI_PRAEFIX}_App-Sicherung_{time.strftime('%Y-%m-%d')}.zip"


def _sicherung_ziel(name):
    """Name in der ZIP → Pfad am Gerät (nur bekannte Orte, keine Ausbrüche) oder None."""
    teile = name.split("/")
    if not name or name.startswith("/") or any(t in ("", ".", "..") or "\\" in t or ":" in t for t in teile):
        return None
    _, _, ausgabe, _ = pfade()
    if teile[0] == "projekt" and len(teile) == 2 and teile[1] in SICHERUNG_PROJEKT:
        return HIER / teile[1]
    if teile[0] == "projekt" and len(teile) >= 3 and teile[1] in SICHERUNG_ORDNER + ("entwuerfe",):
        basis = ausgabe / ".entwuerfe" if teile[1] == "entwuerfe" else HIER / teile[1]
        return basis.joinpath(*teile[2:])
    if teile[0] == "daten" and len(teile) >= 2 and not (set(teile) & SICHERUNG_DATEN_WEG):
        return uebersetzer.daten_ordner().joinpath(*teile[1:])
    return None


def app_sicherung_einspielen(roh):
    """„Sicherung einspielen“: prüft die ZIP vollständig, ersetzt dann den ganzen Stand (Kartenliste, Bilder, Ideen,
    Lernstand, Einstellungen, Entwürfe, Datenordner ohne Modelle) und meldet, was jetzt da ist."""
    if len(roh) > SICHERUNG_MAX:
        raise Meldung("sicherung_gross", status=413, mb=SICHERUNG_MAX // (1024 * 1024))
    try:
        z = zipfile.ZipFile(io.BytesIO(roh))
        namen = z.namelist()
    except (zipfile.BadZipFile, ValueError, OSError):
        raise Meldung("sicherung_kaputt") from None
    if SICHERUNG_MARKE not in namen:
        raise Meldung("sicherung_fremd")
    infos = [i for i in z.infolist() if not i.is_dir() and i.filename != SICHERUNG_MARKE]
    if len(infos) > 50000 or sum(i.file_size for i in infos) > 4 * SICHERUNG_MAX:
        raise Meldung("sicherung_kaputt")
    ziele = [(i, _sicherung_ziel(i.filename)) for i in infos]
    if any(ziel is None for _, ziel in ziele) or not any(i.filename == "projekt/karten.csv" for i, _ in ziele):
        raise Meldung("sicherung_kaputt")
    try:
        inhalt = [(ziel, z.read(i)) for i, ziel in ziele]            # erst alles lesen (CRC geprüft), dann ersetzen
    except (zipfile.BadZipFile, ValueError, OSError):
        raise Meldung("sicherung_kaputt") from None
    for p, _ in _sicherung_dateien():
        p.unlink(missing_ok=True)
    for ziel, daten in inhalt:
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_bytes(daten)
    _vorschau_cache.clear()
    karten = len(karten_daten()["karten"])
    return dict(ok=True, karten=karten, dateien=len(inhalt), meldung=tx("sicherung_ok", karten=karten, dateien=len(inhalt)))


# =============================================================================================
# Start und Ende
# =============================================================================================
class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = os.name != "nt"                 # Windows: Port nicht mit fremden Programmen teilen

    def server_bind(self):
        if os.name == "nt" and hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


_server: Server | None = None


def finde_server(port, versuche=20):
    for p in range(port, port + versuche):
        try:
            return Server(("127.0.0.1", p), Handler), p
        except OSError:
            continue
    raise SystemExit(f"Kein freier Port zwischen {port} und {port + versuche - 1} gefunden.")


def start_adresse():
    return f"http://127.0.0.1:{PORT}/?k={START_SCHLUESSEL}"


BEENDET = threading.Event()        # das Startfenster schließt sich, sobald die Oberfläche beendet wurde


def beenden():
    time.sleep(0.3)
    BEENDET.set()
    warteschlange.alles_stoppen()
    if _server:
        _server.shutdown()


def starte(port=8765, browser=True):
    """Startet den Server im Hintergrund (für das Startfenster). Gibt die Start-Adresse zurück."""
    global _server, PORT
    _server, PORT = finde_server(port)
    threading.Thread(target=_server.serve_forever, daemon=True).start()
    if browser:
        threading.Timer(0.6, lambda: webbrowser.open(start_adresse())).start()
    return start_adresse()


def schreibe_instanz(pfad):
    """Für das Startprogramm: wo die Oberfläche läuft (nur für dieses Benutzerkonto lesbar). So öffnet ein
    zweiter Start nur den Browser, statt eine zweite Oberfläche zu starten."""
    daten = dict(pid=os.getpid(), port=PORT, schluessel=START_SCHLUESSEL, adresse=start_adresse(), projekt=str(HIER),
                 version=UI_VERSION, python=sys.executable, start_id=os.environ.get("MGD_START_ID", ""),
                 gestartet=time.strftime("%Y-%m-%d %H:%M:%S"))
    pfad = Path(pfad)
    pfad.parent.mkdir(parents=True, exist_ok=True)
    tmp = pfad.with_name(pfad.name + f".{os.getpid()}.tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(daten, f, ensure_ascii=False)
    os.replace(tmp, pfad)


def entferne_instanz(pfad):
    try:
        if json.loads(Path(pfad).read_text(encoding="utf-8")).get("pid") == os.getpid():
            Path(pfad).unlink()
    except (OSError, ValueError, AttributeError):
        pass


# =============================================================================================
# Erweiterungen (erweiterungen.py): Import/Export, Ideen, Programmstart, Deinstallieren – optional
# =============================================================================================
try:
    import ki_bild  # noqa: E402
except ImportError:                                      # Datei fehlt (z. B. in einer Testkopie) → ohne KI-Bilder
    ki_bild = None


def _ki_bild_zustand():
    st = ki_bild.status()
    zahl = lambda b, s: f"{b / 1e9:.1f}".replace(".", "," if s != "en" else ".")  # noqa: E731
    ram = st["ram_gb"]
    if st["installiert"]:
        if ram is not None and ram < ki_bild.RAM_EMPFOHLEN_GB:
            return L(f"installiert ✓ · Achtung: nur {ram:.0f} GB Arbeitsspeicher, empfohlen sind 8 GB",
                     f"installed ✓ · Heads-up: only {ram:.0f} GB of memory, 8 GB recommended",
                     f"instalado ✓ · Atención: solo {ram:.0f} GB de memoria, se recomiendan 8 GB"), False
        return L("installiert ✓", "installed ✓", "instalado ✓"), False
    if st["bytes_da"]:
        return L(f"angefangen: {zahl(st['bytes_da'], 'de')} von {zahl(st['bytes_gesamt'], 'de')} GB – „Laden“ setzt fort",
                 f"started: {zahl(st['bytes_da'], 'en')} of {zahl(st['bytes_gesamt'], 'en')} GB – “Download” continues",
                 f"empezado: {zahl(st['bytes_da'], 'es')} de {zahl(st['bytes_gesamt'], 'es')} GB; «Descargar» continúa"), True
    return L(f"nicht installiert (ca. {zahl(st['bytes_gesamt'], 'de')} GB)",
             f"not installed (about {zahl(st['bytes_gesamt'], 'en')} GB)",
             f"no instalado (unos {zahl(st['bytes_gesamt'], 'es')} GB)"), True


if ki_bild:
    @werkzeug("ki-bild", L("KI-Bildmodell laden (realistische Gänse)", "Download AI image model (realistic geese)",
                           "Descargar modelo de imágenes IA (gansos realistas)"),
              L("Damit erzeugt das Programm realistische Gänse-Bilder für neue Karten – offline, direkt auf diesem "
                "Rechner: Segmind Vega + VegaRT (Lizenz Apache-2.0), ca. 3,5 GB von Hugging Face, Prüfsummen werden "
                "kontrolliert, ein Abbruch setzt beim nächsten Mal fort. Liegt im Datenordner – auch für spätere "
                "Programmversionen.",
                "With it the program creates realistic goose images for new cards – offline, right on this computer: "
                "Segmind Vega + VegaRT (Apache-2.0 license), about 3.5 GB from Hugging Face, checksums verified, an "
                "interrupted download resumes next time. Stored in the data folder – also for later program versions.",
                "Con él, el programa crea imágenes realistas de gansos para cartas nuevas, sin conexión y en esta "
                "computadora: Segmind Vega + VegaRT (licencia Apache-2.0), unos 3,5 GB desde Hugging Face; se verifican "
                "las sumas y una descarga interrumpida continúa la próxima vez. Se guarda en la carpeta de datos, "
                "también para futuras versiones."),
              L("Laden …", "Download …", "Descargar …"), art="lauf", zustand=_ki_bild_zustand,
              frage=L("Jetzt ca. 3,5 GB laden? Quelle: Hugging Face (Segmind), Lizenz Apache-2.0. Das dauert je nach "
                      "Internet eine Weile – du kannst nebenbei weiterarbeiten.",
                      "Download about 3.5 GB now? Source: Hugging Face (Segmind), Apache-2.0 license. Depending on your "
                      "internet this takes a while – you can keep working meanwhile.",
                      "¿Descargar ahora unos 3,5 GB? Origen: Hugging Face (Segmind), licencia Apache-2.0. Según tu "
                      "internet tardará un rato; mientras, puedes seguir trabajando."), tool="ki-bild")
    def _w_ki_bild():
        return starte_lauf("ki-bild-laden")
    _i = next((i for i, w in enumerate(WERKZEUGE) if w["id"] == "modell-x2"), None)   # gleich zu den KI-Modellen
    if _i is not None:
        WERKZEUGE.insert(_i + 1, WERKZEUGE.pop())


# =============================================================================================
# Tools (tools.py): installieren über die Warteschlange, deinstallieren, Erstabfrage – optional
# =============================================================================================
try:
    import tools  # noqa: E402
except ImportError:                                      # Datei fehlt (z. B. in einer Testkopie) → ohne Tools-Bereich
    tools = None

try:
    import lernen  # noqa: E402
except ImportError:                                      # Datei fehlt (z. B. in einer Testkopie) → ohne Lernen
    lernen = None


# ---------- Karten lernen (Tool „lernen“, lernen.py): Lernstand im Projektordner neben karten.csv ----------
_lern_lokal = threading.local()                          # je Anfrage: zurückgesetzte Lernstände (für die Meldung)


def _lernstand():
    return lernen.Lernstand(pfade()[0].parent, zielsprache())


def _lern_dateien():
    return lernen.dateien(pfade()[0].parent) if lernen else []


if tools and lernen:
    tools.lernstand_dateien = _lern_dateien


def _lern_karten(zeilen=None, bilder=None):
    """Karten für lernen.py: {bild, aktiv, de, notiz, rueckseiten (alle Sprachen mit Wort), pfad}."""
    if zeilen is None:
        csv_pfad, bilder, _, _ = pfade()
        _, zeilen, _ = gl.lies_csv(csv_pfad)
    bilder = Path(bilder if bilder is not None else pfade()[1])
    codes = list(sprachen.SPRACHEN) if sprachen else ["es"]
    aus = []
    for z in zeilen:
        roh = z.get("bild", "")
        bild = roh.lstrip("#").strip()
        if not gl.sicherer_name(bild):
            continue
        aus.append(dict(bild=bild, aktiv=not roh.startswith("#"), de=z.get("de", ""), notiz=z.get("notiz", ""),
                        rueckseiten={c: z.get(c, "") for c in codes if z.get(c, "").strip()}, pfad=bilder / bild))
    return aus


def _lern_karten_info(zeilen, bilder):
    """Beim Laden der Karten: geänderte Karten abgleichen (auch nach einer Änderung der CSV von außen) und – mit
    Tool – den Lernstand je Karte liefern. Ohne Lernstand-Datei kostet das nichts."""
    if not lernen:
        return None
    try:
        karten = _lern_karten(zeilen, bilder)
        st = _lernstand()
        if st.existiert():
            zurueck = st.abgleichen(karten)
            if zurueck and isinstance(getattr(_lern_lokal, "liste", None), list):
                bekannt = {z["bild"] for z in _lern_lokal.liste}
                _lern_lokal.liste.extend(z for z in zurueck if z["bild"] not in bekannt)
        if tools and not tool_da("lernen"):
            return None
        return st.karten_info(karten)
    except (OSError, ValueError, lernen.LernFehler):
        return None


def _lern_meldung(zurueck):
    namen = ", ".join(f"„{z['de'] or z['bild']}“" if gl.sprache() == "de" else f"“{z['de'] or z['bild']}”"
                      if gl.sprache() == "en" else f"«{z['de'] or z['bild']}»" for z in zurueck[:5])
    return tx("lern_zurueck", namen=namen + (" …" if len(zurueck) > 5 else ""))


def _lernen_pruefen():
    if tools and not tool_da("lernen"):
        _tool_fehlt("lernen")


def _lern_meldung_fehler(e):
    code = "lern_" + e.code
    return Meldung(code if code in TEXTE else "lern_ungueltig", status=e.status)


def lernen_info():
    return _lernstand().uebersicht(_lern_karten())


def lernen_post(weg, daten):
    """POST /api/lernen-…: bewerten, rueckgaengig, einstellungen, stapel, zuruecksetzen, import."""
    _lernen_pruefen()
    st = _lernstand()
    try:
        if weg == "/api/lernen-bewerten":
            karten = _lern_karten()
            erg = st.bewerten(karten, str(daten.get("id") or ""), daten.get("note"), daten.get("dauer_ms") or 0)
            if "stapel" in daten:                         # gleich die nächste Karte mitschicken
                erg["naechste"] = st.naechste_karte(karten, daten.get("stapel") or None, sprache=gl.sprache())
            return erg
        if weg == "/api/lernen-rueckgaengig":
            erg = st.rueckgaengig()
            erg["naechste"] = st.naechste_karte(_lern_karten(), daten.get("stapel") or None, sprache=gl.sprache())
            return erg
        if weg == "/api/lernen-einstellungen":
            st.einstellungen_setzen(daten.get("werte") if isinstance(daten.get("werte"), dict) else daten)
            return lernen_info()
        if weg == "/api/lernen-stapel":
            aktion = daten.get("aktion")
            if aktion == "loeschen":
                st.stapel_loeschen(str(daten.get("id") or ""))
                return lernen_info()
            if aktion == "speichern":
                neu = st.stapel_speichern(daten.get("stapel"))
                return dict(lernen_info(), gespeichert=neu["id"])
            raise Meldung("ungueltig")
        if weg == "/api/lernen-zuruecksetzen":
            n = st.zuruecksetzen(bild=str(daten.get("bild") or "") or None, alle=daten.get("alle") is True)
            return dict(lernen_info(), zurueckgesetzt=n)
        if weg == "/api/lernen-import":
            roh = daten.get("lernstand", daten)
            return dict(lernen_info(), importiert=st.importieren(roh))
    except lernen.LernFehler as e:
        raise _lern_meldung_fehler(e) from None
    raise Meldung("unbekannt", status=404)


def _menge(b):
    s = gl.sprache()
    if b >= 1e9:
        return f"{b / 1e9:.1f}".replace(".", "," if s != "en" else ".") + " GB"
    return f"{round(b / (1024 * 1024))} MB" if b >= 1024 * 1024 else "< 1 MB" if b else "0 MB"


def _tool_laeufe(tid):
    """Aufträge der Warteschlange (laufend + wartend), die zum Tool gehören: [(Lauf, „laden“ | „nutzt“)]."""
    with warteschlange.lock:
        laeufe = [x for x in [warteschlange.aktiv, *warteschlange.wartend] if x]
    return [(x, g) for x in laeufe for g in [tools.gehoert(tid, x.art, x.befehl)] if g]


def _tool_eintrag(e):
    tid = e["id"]
    laden = next((x for x, g in _tool_laeufe(tid) if g == "laden"), None)
    zustand = ("laeuft" if laden.laeuft else "wartet") if laden else "installiert" if e["installiert"] else \
        "angefangen" if e["angefangen"] else "nicht"
    teil_laedt = tools.teil_aus_befehl(tid, laden.befehl) if laden else None
    texte = {k: gl.text_in(e[k]) for k in ("titel", "nutzen", "dauer", "loeschen")}
    try:                                                 # Platzprüfung für die Rückfrage (Ordner muss es noch nicht geben)
        ort = next(o for o in [Path(e["ort"]), *Path(e["ort"]).parents] if o.exists())
        texte["frei"] = shutil.disk_usage(ort).free
    except (OSError, StopIteration):
        texte["frei"] = None
    if tid == "ki-bild" and ki_bild:
        texte["ram_gb"] = ki_bild.arbeitsspeicher_gb()
    if tid in NUR_RECHNER_TOOLS and im_browser():                # Web-App: Karte zeigt „nur am Rechner“
        texte.update(nur_rechner=True, installiert=False)
        zustand = "nicht"
    if tid == "bildverbesserung" and im_browser():               # Web-App: Real-ESRGAN rechnet am Handy viel länger
        texte["nutzen"] += " " + gl.text_in(L(
            "Am Handy ist das deutlich langsamer (ein Bild kann ein paar Minuten brauchen) – das eingebaute FSRCNN ist "
            "flink und reicht für den Druck.",
            "On a phone this is much slower (one image can take a few minutes) – the built-in FSRCNN is quick and good "
            "enough for printing.",
            "En el celular es bastante más lento (una imagen puede tardar unos minutos); el FSRCNN integrado es rápido y "
            "basta para imprimir."))
    return dict(e, **texte, teile=[dict(t, titel=gl.text_in(t["titel"]), hinweis=gl.text_in(t["hinweis"]) if t.get("hinweis") else "")
                                   for t in e["teile"]], zustand=zustand,
                lauf=laden.id if laden else None, position=warteschlange.position(laden) if laden else 0,
                prozent=tools.prozent(tid, laden.zeilen) if laden and laden.laeuft else None, teil_laedt=teil_laedt)


def tools_info():
    z = tools.lade_zustand()
    aus = [_tool_eintrag(e) for e in tools.liste(z)]
    return dict(tools=aus, belegt=sum(e["belegt"] for e in aus), erstabfrage=tools.erstabfrage_noetig(z))


def tool_info(tid):
    return next((e for e in tools_info()["tools"] if e["id"] == tid), None)


def tool_aktion(daten):
    """{id, aktion: installieren | deinstallieren, teil?, zustimmung?} – Installieren reiht den Download in die
    Warteschlange ein (Antwort mit „lauf“) bzw. ist sofort fertig (Aktivierung, Dateien schon da). Deinstallieren
    wird verweigert, solange ein Auftrag des Tools läuft oder wartet."""
    tid, aktion = str(daten.get("id") or ""), str(daten.get("aktion") or "")
    teil = daten.get("teil") if isinstance(daten.get("teil"), str) and daten.get("teil") else None
    try:
        if not tools.gibt_es(tid):
            raise tools.ToolFehler("tool_unbekannt", 404)
        t = tools.TOOLS[tid]
        titel = gl.text_in(t["titel"])
        if aktion == "installieren" and tid in NUR_RECHNER_TOOLS and im_browser():
            raise Meldung("nur_rechner", status=403)
        if aktion == "installieren":
            if t.get("zustimmung") and daten.get("zustimmung") is True and not t["da"]():
                uebersetzer.speichere_einstellungen({"zugestimmt": True, "automatisch": daten.get("automatisch") is True})
            auftrag = tools.installieren(tid, teil)
            if not auftrag:
                return dict(tool=tool_info(tid), meldung=tx("tool_bereit", titel=titel))
            st = starte_lauf(**auftrag)
            return dict(tool=tool_info(tid), lauf=st)
        if aktion == "deinstallieren":
            if _tool_laeufe(tid):
                raise Meldung("tool_beschaeftigt", status=409, titel=titel)
            erg = tools.deinstalliere(tid, teil)
            if tid == "sprachen":
                erg["zielsprache_zurueck"] = _zielsprache_aufraeumen()
                if teil:                                          # Meldung nennt die entfernte Sprache
                    titel = sprachen.name(teil, gl.sprache())
            if not erg["abgemeldet"] and not (teil and tools.installiert(tid)):
                erg["frei"] += _tool_zwischenspeicher_weg(tid)
            _vorschau_cache.clear()
            meldung = tx("tool_abgemeldet", titel=titel) if erg["abgemeldet"] else \
                tx("tool_weg", titel=titel, menge=_menge(erg["frei"]))
            return dict(erg, tool=tool_info(tid), meldung=meldung)
        raise Meldung("ungueltig")
    except tools.ToolFehler as e:
        if e.code == "zustimmung":
            raise uebersetzer.UebersetzungsFehler("zustimmung") from None
        raise Meldung(e.code if e.code in TEXTE else "ungueltig", status=e.status, **e.werte) from None
    except Exception as e:
        if sprachen and isinstance(e, sprachen.SprachFehler):
            raise ValueError(sprachen.fehler_text(e, gl.sprache())) from None
        raise


def _tool_zwischenspeicher_weg(tid):
    """Bildverbesserung: KI-Einträge (Real-ESRGAN) in ausgabe/.cache · KI-Bilder: ausgabe/.ki-bild (nur eigene
    Dateiendungen, nie rekursiv). Druck-PDFs, Karten, Bilder und die eigene Prompt-Fassung bleiben. → frei (Bytes)"""
    ausgabe, frei = pfade()[2], 0

    def weg(datei):
        nonlocal frei
        try:
            if datei.is_file() and not datei.is_symlink():
                frei += datei.stat().st_size
                datei.unlink()
        except OSError:
            pass
    if tid == "bildverbesserung":
        cache = ausgabe / ".cache"
        for j in (cache.glob("*.json") if cache.is_dir() else []):
            try:
                m = json.loads(j.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if isinstance(m, dict) and str(m.get("ki") or "").startswith("realesrgan"):
                weg(j.with_suffix(".jpg"))
                weg(j)
    elif tid == "ki-bild":
        d = ausgabe / ".ki-bild"
        for datei in (d.iterdir() if d.is_dir() else []):
            if datei.suffix.lower() in (".png", ".jpg", ".json", ".tmp"):
                weg(datei)
        try:
            d.rmdir()
        except OSError:
            pass
    return frei


def tools_erstabfrage(daten):
    """Einmalige Frage beim ersten Öffnen: {auswahl: [id, …]} – nichts ist vorausgewählt, leere Auswahl = „Später“.
    Tools mit Zustimmung (Übersetzung) kommen als „offen“ zurück, die Oberfläche fragt dann ihre Zustimmung ab."""
    auswahl = daten.get("auswahl") if isinstance(daten.get("auswahl"), list) else []
    offen, laeufe = [], []
    for tid in dict.fromkeys(x for x in auswahl if isinstance(x, str) and tools.gibt_es(x)):
        if tools.installiert(tid):
            continue
        try:
            r = tool_aktion({"id": tid, "aktion": "installieren"})
            if r.get("lauf"):
                laeufe.append(r["lauf"])
        except uebersetzer.UebersetzungsFehler:
            offen.append(tid)
    tools.gefragt_setzen()
    return dict(tools_info(), offen=offen, laeufe=laeufe)


# ---------- KI-Bilder: Standard-Prompt, eigene Fassung, Schalter „keine Menschen“ (in ui_einstellungen.json) ----------
def _ki_sprache():
    os.environ["MGD_SPRACHE"] = gl.sprache()                  # Meldungen aus ki_bild in der Sprache der Oberfläche


def ki_bild_einstellungen():
    e = _lies_datei().get("ki_bild") or {}
    vorlage = e.get("vorlage") if isinstance(e.get("vorlage"), str) and e.get("vorlage").strip() else None
    negativ = e.get("negativ") if isinstance(e.get("negativ"), str) else None
    return dict(vorlage=vorlage or ki_bild.PROMPT_STANDARD,
                negativ=ki_bild.NEGATIV_STANDARD if negativ is None else negativ,
                ohne_menschen=e.get("ohne_menschen") is not False, eigene=vorlage is not None or negativ is not None,
                standard=dict(vorlage=ki_bild.PROMPT_STANDARD, negativ=ki_bild.NEGATIV_STANDARD),
                allein=ki_bild.ALLEIN, negativ_menschen=ki_bild.NEGATIV_MENSCHEN, max=ki_bild.PROMPT_MAX)


def ki_bild_info():
    st = ki_bild.status()
    return dict(ki_bild_einstellungen(), installiert=tool_da("ki-bild"), ram_gb=st["ram_gb"],
                breite=ki_bild.BREITE, hoehe=ki_bild.HOEHE, schritte=ki_bild.SCHRITTE)


def ki_bild_prompt_setzen(daten):
    """Eigene Fassung speichern ({vorlage, negativ}), auf Standard zurücksetzen ({zuruecksetzen}) oder den Schalter
    „keine Menschen“ merken. Gleich dem Standard → wird nicht als eigene Fassung gespeichert."""
    _ki_sprache()
    with _einst_lock:
        jetzt = ki_bild_einstellungen()
        alles = _lies_datei()
        e = dict(alles.get("ki_bild") or {})
        if daten.get("zuruecksetzen"):
            e.pop("vorlage", None)
            e.pop("negativ", None)
        elif "vorlage" in daten or "negativ" in daten:
            v, n = ki_bild.pruefe_vorlage(daten.get("vorlage", jetzt["vorlage"]), daten.get("negativ", jetzt["negativ"]))
            e["vorlage"] = None if v == ki_bild.PROMPT_STANDARD else v
            e["negativ"] = None if n == ki_bild.NEGATIV_STANDARD else n
        if "ohne_menschen" in daten:
            e["ohne_menschen"] = daten["ohne_menschen"] is not False
        alles["ki_bild"] = {k: v for k, v in e.items() if v is not None}
        _schreibe_datei(alles)
    return ki_bild_info()


def ki_bild_text(daten):
    """Fertiger Prompt aus Beschreibung + Wort mit der aktuellen Vorlage (zum Anzeigen und für den Lauf)."""
    _ki_sprache()
    e = ki_bild_einstellungen()
    ohne = daten.get("ohne_menschen", e["ohne_menschen"]) is not False
    prompt, negativ = ki_bild.baue_prompt(str(daten.get("beschreibung") or "")[:300], str(daten.get("wort") or "")[:60],
                                          ohne, e["vorlage"], e["negativ"])
    token = ki_bild.token_anzahl(prompt)
    return dict(prompt=prompt, negativ=negativ, ohne_menschen=ohne, token=token,
                zu_lang=token is not None and token > 75)


# ---------- KI-Bilder: Erzeugen als Hintergrund-Lauf (eigener Prozess, Abbrechen = Prozess beenden) ----------
def ki_bild_ordner():
    """Zwischenergebnisse: ausgabe/.ki-bild/<id>.png (Bild), .jpg (Vorschau je Schritt), .json (Prompt, Startwert)."""
    d = pfade()[2] / ".ki-bild"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _ki_pfade(kid):
    if not re.fullmatch(r"[0-9a-f]{16}", str(kid or "")):
        raise Meldung("ki_bild_fehlt", status=404)
    d = ki_bild_ordner()
    return d / f"{kid}.png", d / f"{kid}.jpg", d / f"{kid}.json"


def _ki_bild_aufraeumen(d, behalten=30, tage=14):
    """Nur eigene Zwischenergebnisse in ausgabe/.ki-bild: älter als 14 Tage oder mehr als 30 (wie bei den Entwürfen).
    Übernommene Bilder liegen dann längst als Karte bzw. Entwurf vor."""
    metas = sorted(d.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for i, m in enumerate(metas):
        if i >= behalten or time.time() - m.stat().st_mtime > tage * 86400:
            for endung in (".png", ".jpg", ".json", ".jpg.tmp"):
                m.with_name(m.stem + endung).unlink(missing_ok=True)


def _zahl(wert, unten, oben, vorgabe):
    try:
        w = int(wert)
    except (TypeError, ValueError):
        return vorgabe
    return w if unten <= w <= oben else vorgabe


def _ki_bild_lauf(ki, sprache):
    """Lauf für ki_bild.py --erzeugen. ki: beschreibung, wort, ohne_menschen, startwert, karte (Bild für vorhandene
    Karte), schnell (TAESDXL), für Prüfungen auch breite/hoehe/schritte."""
    _ki_modell_da()
    karte = str(ki.get("karte") or "")
    if karte:
        sicher_in(pfade()[1], karte)
        if not _karten_zeile(karte):
            raise Meldung("karte_unbekannt", status=404)
    text = ki_bild_text(ki)
    d = ki_bild_ordner()
    _ki_bild_aufraeumen(d)
    kid = secrets.token_hex(8)
    startwert = _zahl(ki.get("startwert"), 0, 2 ** 31 - 1, secrets.randbelow(2 ** 31))
    befehl = [sys.executable, "-u", str(HIER / "ki_bild.py"), f"--erzeugen={text['prompt']}",
              f"--startwert={startwert}", f"--aus={d / (kid + '.png')}", f"--vorschau={d / (kid + '.jpg')}"]
    if text["negativ"]:
        befehl.append(f"--negativ={text['negativ']}")
    if ki.get("schnell") is True:
        befehl.append("--schnell")
    for k, unten, oben in (("breite", 256, 1536), ("hoehe", 256, 1536), ("schritte", 1, 8)):
        w = _zahl(ki.get(k), unten, oben, None)
        if w is not None and (k == "schritte" or w % 32 == 0):
            befehl.append(f"--{k}={w}")
    meta = dict(id=kid, zeit=time.time(), beschreibung=str(ki.get("beschreibung") or "")[:300],
                wort=str(ki.get("wort") or "")[:60], karte=karte, startwert=startwert, **text)
    (d / f"{kid}.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    kurz = (meta["wort"] or meta["beschreibung"] or "…")[:40]
    lauf = Lauf("ki-bild", tx("ki_bild_erzeugen", text=kurz), befehl,
                f"python3 ki_bild.py --erzeugen \"{text['prompt'][:60]}…\" --startwert {startwert}", sprache=sprache)
    lauf.ki_id = kid
    lauf.ki_meta = dict(karte=karte, wort=meta["wort"], beschreibung=meta["beschreibung"])
    return lauf


def ki_bild_uebernehmen(daten):
    """Fertiges KI-Bild als Entwurf: neue Karte (Schritt 1, Text = Wort) oder – mit „karte“ – neues Bild einer vorhandenen
    Karte (wie „Bild ändern“). Gespeichert als JPG (Qualität 95); es gelten dieselben Prüfungen wie für Fotos."""
    from PIL import Image
    bild, _, meta_pfad = _ki_pfade(daten.get("id"))
    if not bild.is_file() or not meta_pfad.is_file():
        raise Meldung("ki_bild_fehlt", status=404)
    meta = json.loads(meta_pfad.read_text(encoding="utf-8"))
    karte = str(daten.get("karte", meta.get("karte")) or "")
    wort = str(daten.get("wort", meta.get("wort")) or "").strip()[:60]
    puffer = io.BytesIO()
    with Image.open(bild) as im:
        im.convert("RGB").save(puffer, "JPEG", quality=95)
    stamm = re.sub(r"[^\w\- ]+", "", wort).strip() or "gans-ki"
    erg = entwurf_anlegen(puffer.getvalue(), f"{stamm}.jpg", karte)
    if wort and not karte:                                       # Kartentext gleich vorschlagen
        erg = entwurf_pruefen(erg["id"], {"de": wort})
    return erg

try:
    import erweiterungen  # noqa: E402
    erweiterungen.verbinde(sys.modules[__name__])
except ImportError:                                      # Datei fehlt → Oberfläche wie bisher
    erweiterungen = None
except Exception as _fehler:  # noqa: BLE001              # ein Fehler dort darf die Oberfläche nie verhindern
    print(f"Erweiterungen nicht geladen: {type(_fehler).__name__}: {_fehler}", file=sys.stderr)
    erweiterungen = None


def main(argv=None):
    global _server, PORT
    ap = argparse.ArgumentParser(description=f"{gl.PRODUKT} – Oberfläche im Browser")
    ap.add_argument("--port", type=int, default=8765, help="Port (Standard 8765; belegt → nächster freier)")
    ap.add_argument("--kein-browser", action="store_true", help="Browser nicht automatisch öffnen")
    ap.add_argument("--instanz-datei", help=argparse.SUPPRESS)          # vom Startprogramm
    a = ap.parse_args(argv)
    for strom in (sys.stdout, sys.stderr):
        try:
            strom.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    _server, PORT = finde_server(a.port)
    if sprachen:                                         # übrig gebliebenes uharfbuzz (war beim Entfernen belegt)
        try:
            sprachen.pakete_aufraeumen()
        except OSError:
            pass
    print(f"{gl.PRODUKT} – Oberfläche {UI_VERSION}")
    print("  Im Browser öffnen / open in browser / abrir en el navegador:")
    print(f"  {start_adresse()}")
    print("  Beenden: Strg+C oder ⏻ in der Oberfläche.")
    if sys.stdout:                                       # ohne Konsole (pythonw) ist sys.stdout None
        sys.stdout.flush()
    if a.instanz_datei:
        schreibe_instanz(a.instanz_datei)
    if not a.kein_browser:
        threading.Timer(0.6, lambda: webbrowser.open(start_adresse())).start()
    try:
        _server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        _server.server_close()
        if a.instanz_datei:
            entferne_instanz(a.instanz_datei)
        print("Oberfläche beendet.")


if __name__ == "__main__":
    main()
