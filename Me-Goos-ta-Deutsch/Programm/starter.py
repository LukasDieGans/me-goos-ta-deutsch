#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ME GOOS-TA DEUTSCH – Startprogramm                                   Version 2.4 (22.10.2026)
=============================================================================================
Wird aufgerufen von den Startdateien „Me Goos-ta Deutsch - Windows.cmd“ / „Me Goos-ta Deutsch - Mac.command“
oder vom Desktop-Symbol. Es erkennt selbst, ob es der erste Start ist:

  erster Start    → richtet alles ein: Pakete (Pillow, NumPy, ReportLab, pypdfium2), KI-Modell Real-ESRGAN,
                    Desktop-Symbol + Startmenü (Windows) bzw. Programme-Ordner (Mac) – dann öffnet sich die Oberfläche.
  jeder weitere   → öffnet sofort die Oberfläche; läuft sie schon, wird nur der Browser geöffnet.
  neue Version / neuer Ordner / Schäden → wird erkannt und nur das Nötige nachgeholt. Liegt eine neue Version in
                    einem neuen Ordner, bietet es an, die eigenen Karten aus dem bisherigen Ordner zu übernehmen
                    (Karten, Bilder, Gänse-Bild, Einstellungen, schon verbesserte Bilder – der alte Ordner bleibt).

Python selbst bringen die Startdateien mit – eine eigene Laufzeit im Benutzerordner, ohne Administratorrechte:
  Windows: %LOCALAPPDATA%\\Me-Goos-ta-Deutsch\\python        (offizielles „embeddable“ Python von python.org)
  macOS:   ~/Library/Application Support/Me-Goos-ta-Deutsch/python   (python-build-standalone)
  Linux:   ~/.local/share/me-goos-ta-deutsch/python
Dort liegen auch protokoll.txt (Einrichtung) und oberflaeche.txt (Meldungen der Oberfläche).

Nur Standardbibliothek – läuft, bevor irgendein Paket installiert ist.
Schalter: --einrichten (alles neu prüfen/reparieren) · --beenden · --status · --entfernen · --kein-browser
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import http.client
import json
import os
import queue
import re
import secrets
import shlex
import shutil
import subprocess
import sys
import threading
import time
import traceback
import webbrowser
from pathlib import Path

HIER = Path(__file__).resolve().parent              # …/Programm
WURZEL = HIER.parent                                 # Ordner mit den Startdateien
sys.path.insert(0, str(HIER))

VERSION = "2.4 (22.10.2026)"
PRODUKT = "Me Goos-ta Deutsch"
WIN, MAC = os.name == "nt", sys.platform == "darwin"
START_WIN = "Me Goos-ta Deutsch - Windows.cmd"
START_MAC = "Me Goos-ta Deutsch - Mac.command"
START_LINUX = "Me Goos-ta Deutsch - Linux.sh"                # ruft die Mac-Startdatei auf (die kann beides)
ANLEITUNG = "LIES MICH ZUERST.html"
STARTDATEI = START_WIN if WIN else START_MAC if MAC else START_LINUX
VORRAT_MODELLE = ("realesrgan-x4plus", "realesrgan-x2plus")   # Tool „Bildverbesserung“: Kopie im Datenordner
PFLICHT = {"PIL": "pillow", "numpy": "numpy", "reportlab": "reportlab"}
WAHL = {"pypdfium2": "pypdfium2"}                    # optional: Vorschaubilder und PNG-Export
MIN_FREI_MB = 700
# Feste Paketfassungen (seit 2.5): Lock-Dateien mit der SHA-256 jedes Rads (gebaut von bau_lock.py im Arbeitsordner),
# pip prüft jede Datei (--require-hashes). requirements.txt (Spannen) bleibt für Entwickler und den CI-Job „neueste
# Fassungen“ (MGD_PAKETE_NEUESTE=1).
LOCK = "pakete.lock"
# Nur Windows: Blockiert „Smart App Control“ eine Datei der neuesten Pakete, werden ältere, seit Langem weit
# verbreitete Fassungen probiert (Windows kennt deren Dateien eher als „vertrauenswürdig“). Spannen in bau_lock.py.
ERSATZ_SAETZE = [
    ("bewährt", "pakete-bewaehrt.lock"),       # reportlab 4.x, pillow 11.x, numpy 2.1–2.2, pypdfium2 4.30+
    ("älter", "pakete-aelter.lock"),           # reportlab 4.0–4.2, pillow 11.0, numpy 2.1, pypdfium2 4.30+
]
SPERR_CODES = {4551: "sac", 577: "sac", 1260: "richtlinie", 225: "virus"}
SPERR_WORTE = ("4551", "application control", "anwendungssteuerung", "control de aplicaciones",
               "smart app control", "intelligente app", "control inteligente")


def daten_ordner() -> Path:
    if os.environ.get("MGD_DATEN"):
        return Path(os.environ["MGD_DATEN"])
    if WIN:
        return Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "Me-Goos-ta-Deutsch"
    if MAC:
        return Path.home() / "Library" / "Application Support" / "Me-Goos-ta-Deutsch"
    return Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "me-goos-ta-deutsch"


DATEN = daten_ordner()
STEMPEL = DATEN / "eingerichtet.json"


# =============================================================================================
# Texte (Deutsch, Englisch, Spanisch)
# =============================================================================================
TEXTE = {
    "de": dict(
        kopf="Me Goos-ta Deutsch – Lernkarten zum Ausdrucken",
        einrichtung="Einrichtung – beim ersten Mal dauert das ein paar Minuten. Lass dieses Fenster einfach offen und lehn dich zurück.",
        g_erst="Erster Start erkannt – alles Nötige wird eingerichtet.",
        g_python="Neues Python erkannt – die Pakete werden angepasst.",
        g_pakete="Neue Programmversion erkannt – die Pakete werden geprüft.",
        g_ordner="Neuer Programmordner erkannt – er wird eingerichtet.",
        g_reparatur="Reparatur – alles wird neu geprüft.",
        s_ort="Ordner und Speicherplatz prüfen", s_pip="Paketverwaltung vorbereiten",
        s_pakete="Pakete laden und installieren (ca. 60 MB)", s_test="Pakete prüfen",
        s_modell="Installierte Tools übernehmen (Bildverbesserung, ohne Download)",
        s_symbole_win="Desktop-Symbol und Startmenü-Eintrag anlegen",
        s_symbole_mac="„Me Goos-ta Deutsch“ im Ordner „Programme“ anlegen",
        s_symbole_linux="Eintrag im Anwendungsmenü anlegen",
        ok="erledigt", schon_da="schon vorhanden", lade="↓ {name} {version}  ({groesse})",
        installiere="installiere: {liste}", noch="… läuft noch ({min} Min.) – gleich geschafft, danke für deine Geduld",
        neuer_versuch="Verbindung hakt – neuer Versuch …",
        ersatz="Windows blockiert {datei} – probiere ältere, weit verbreitete Fassungen ({satz}) …",
        pdfium_aus="Die Vorschau-Bibliothek wurde von Windows blockiert und abgeschaltet. Die PDFs entstehen "
                   "trotzdem; nur die Vorschaubilder fehlen.",
        w_symbol="Das Symbol ließ sich nicht anlegen ({grund}) – kein Problem: Starte künftig einfach über „{start}“.",
        w_admin="Hinweis: Das Programm wurde „Als Administrator“ gestartet. Das ist nicht nötig – ein normaler "
                "Doppelklick genügt.",
        w_fremd="Hinweis: Hier läuft nicht das eigene Python des Programms ({exe}).",
        fertig="Fertig eingerichtet – super, es kann losgehen!",
        kuenftig_win="Ab jetzt startest du über das Desktop-Symbol „Me Goos-ta Deutsch“ (oder das Startmenü).",
        kuenftig_mac="Ab jetzt startest du über „Me Goos-ta Deutsch“ im Launchpad bzw. Ordner „Programme“.",
        kuenftig_linux="Ab jetzt startest du über „Me Goos-ta Deutsch“ im Anwendungsmenü.",
        starte="Die Oberfläche startet …", warte_start="Die Oberfläche startet noch – bitte einen Moment …",
        oeffne="Die Oberfläche ist im Browser geöffnet – viel Spaß beim Kartenbasteln!",
        laeuft_schon="Me Goos-ta Deutsch läuft schon – der Browser öffnet sich gleich. Schön, dass du wieder da bist!",
        alte_version="Eine ältere Fassung der Oberfläche läuft noch – sie wird beendet.",
        adresse="Falls sich kein Browser öffnet, diese Adresse im Browser eingeben:",
        schliesst="Dieses Fenster schließt sich gleich von selbst.",
        fenster_zu="Du kannst dieses Fenster jetzt schließen. Viel Erfolg beim Lernen!",
        warte_sperre="Ein anderes Startfenster richtet gerade ein – ich warte, bis es fertig ist …",
        beendet="Die Oberfläche macht Pause – bis zum nächsten Mal!", nichts_laeuft="Die Oberfläche läuft gerade nicht.",
        entfernt="Entfernt: {was}", entfernen_fertig="Python, Pakete und Symbole wurden entfernt. Den Programmordner "
                 "mit deinen Bildern und PDFs kannst du selbst löschen oder behalten.",
        fehler_titel="Me Goos-ta Deutsch – kleiner Stolperstein",
        f_temp="Das Programm läuft aus einem temporären Ordner – vermutlich direkt aus der ZIP-Datei.\n\n"
               "Bitte die ZIP-Datei zuerst entpacken (Rechtsklick → „Alle extrahieren …“) und dann im entpackten "
               "Ordner „{start}“ doppelklicken.",
        f_schreiben="In den Programmordner kann nicht geschrieben werden:\n{ordner}\n\nSo geht es weiter: den Ordner "
                    "„{name}“ an einen anderen Ort verschieben, z. B. in „Dokumente“ oder auf den Desktop, und dort "
                    "starten.{extra}",
        f_schreiben_win="\nIst in Windows-Sicherheit der „Überwachte Ordnerzugriff“ eingeschaltet, dort Python "
                        "zulassen oder einen nicht geschützten Ordner wählen.",
        f_schreiben_mac="\nmacOS fragt evtl. nach dem Zugriff auf „Downloads“/„Dokumente“ – bitte „Erlauben“. Sonst: "
                        "Systemeinstellungen → Datenschutz & Sicherheit → Dateien und Ordner → Terminal erlauben.",
        f_daten="Der Ordner für Python und Pakete kann nicht angelegt werden:\n{ordner}\n({grund})",
        f_platz="Zu wenig freier Speicherplatz: {frei} MB frei, nötig sind etwa {noetig} MB ({ort}).\n"
                "Schaff ein wenig Platz und starte dann einfach noch einmal.",
        f_internet="Keine Verbindung zum Internet (oder sie wird blockiert).\n\nFür die Einrichtung beim ersten Start "
                   "braucht das Programm einmalig Internet (ca. 90 MB) – danach läuft alles ohne. Bitte die Verbindung "
                   "prüfen und erneut starten.",
        f_pip="Die Pakete konnten nicht installiert werden.\n\n{grund}\n\nDetails: {log}",
        f_zugriff="Zugriff verweigert – vermutlich ist das Programm noch geöffnet oder ein Virenschutz prüft gerade "
                  "Dateien. Bitte alle Fenster von Me Goos-ta Deutsch schließen und erneut starten.",
        f_sac="Windows blockiert eine Datei der Bildbibliothek: {datei}\n(„Intelligente App-Steuerung“ / Smart App "
              "Control). Ältere Fassungen wurden ebenfalls blockiert.\n\nMöglichkeiten:\n"
              "1. Intelligente App-Steuerung ausschalten: Start → „Windows-Sicherheit“ → „App- & Browsersteuerung“ → "
              "„Einstellungen für intelligente App-Steuerung“ → „Aus“. Auf aktuellen Windows-Versionen (ab dem Update vom "
              "April 2026) lässt sie sich dort später wieder einschalten, auf älteren nur durch Zurücksetzen von Windows.\n"
              "2. Das Programm auf einem anderen Rechner verwenden (Windows ohne diese Sperre oder Mac).\n\n"
              "Danach einfach erneut starten.",
        f_richtlinie="Eine Richtlinie dieses Computers (z. B. von Schule oder Firma) blockiert {datei}.\n"
                     "Bitte die zuständige IT fragen oder einen anderen Rechner verwenden.",
        f_virus="Der Virenschutz hat eine Datei gesperrt oder entfernt: {datei}\nBitte in „Windows-Sicherheit → "
                "Schutzverlauf“ nachsehen und die Datei zulassen. Danach erneut starten.",
        f_import="Die Pakete lassen sich nicht laden:\n{details}\n\nDetails: {log}",
        f_fremd="Mit diesem Python lassen sich die Pakete nicht installieren ({exe}).\nBitte über „{start}“ starten – "
                "die Startdatei bringt ihr eigenes Python mit.",
        f_server="Die Oberfläche konnte nicht starten.\n\nLetzte Meldungen:\n{text}\n\nAlle Meldungen: {log}",
        f_server_zeit="Die Oberfläche antwortet gerade nicht – starte einfach noch einmal.\nMeldungen: {log}",
        f_sperre="Ein anderes Startfenster richtet gerade ein. Warte kurz, bis es fertig ist, und starte dann noch einmal.",
        f_unerwartet="Da ist etwas Unerwartetes passiert: {fehler}\n\nDetails: {log}\nTipp: Einmal „{start}“ im Programmordner "
                     "doppelklicken – das repariert die meisten Probleme.",
        f_ordner_weg="Der Programmordner wurde verschoben oder gelöscht:\n{ort}\n\nBitte im neuen Ordner einmal "
                     "„{start}“ doppelklicken – danach funktioniert das Symbol wieder.",
        pause="Weiter mit der Eingabetaste …",
        frei_mb="{mb} MB frei",
        aus_vorrat="aus der früheren Einrichtung übernommen (kein Download nötig)",
        uebernahme_titel="Me Goos-ta Deutsch – neue Version",
        uebernahme_frage="Diese Version liegt in einem neuen Ordner. Im bisherigen Ordner\n{alt}\nliegen deine Karten "
                         "({karten} Karten, {bilder} Bilder{gans}).\n\nSollen sie übernommen werden – samt Einstellungen "
                         "und schon verbesserten Bildern? Der bisherige Ordner bleibt unverändert; die Beispielkarten "
                         "dieser Version kommen nach „Programm/_beispiele“.",
        uebernahme_gans=", eigenes Gänse-Bild", frage_jn="Übernehmen? [J/n] ", ja="Ja", nein="Nein",
        s_uebernahme="Karten aus dem bisherigen Ordner übernehmen",
        uebernommen="Übernommen: {karten} Karten, {bilder} Bilder, {cache} verbesserte Bilder{gans}.",
        nicht_uebernommen="Nicht übernommen – es geht mit den Beispielkarten los. Später übernehmen: karten.csv und den "
                          "Ordner „bilder“ aus {alt} in den neuen Ordner „Programm“ kopieren.",
        w_uebernahme="Die Übernahme ist nicht vollständig gelungen ({grund}). Der bisherige Ordner ist unverändert: {alt}",
    ),
    "en": dict(
        kopf="Me Goos-ta Deutsch – printable flashcards",
        einrichtung="Setup – the first time this takes a few minutes. Just keep this window open and sit back.",
        g_erst="First start detected – setting up everything needed.",
        g_python="New Python detected – adjusting the packages.",
        g_pakete="New program version detected – checking the packages.",
        g_ordner="New program folder detected – setting it up.",
        g_reparatur="Repair – checking everything again.",
        s_ort="Checking folder and disk space", s_pip="Preparing the package manager",
        s_pakete="Downloading and installing packages (about 60 MB)", s_test="Checking the packages",
        s_modell="Taking over installed tools (image enhancement, no download)",
        s_symbole_win="Creating desktop icon and Start menu entry",
        s_symbole_mac="Adding “Me Goos-ta Deutsch” to the Applications folder",
        s_symbole_linux="Adding an entry to the application menu",
        ok="done", schon_da="already there", lade="↓ {name} {version}  ({groesse})",
        installiere="installing: {liste}", noch="… still working ({min} min) – almost there, thanks for your patience",
        neuer_versuch="Connection hiccup – trying again …",
        ersatz="Windows blocks {datei} – trying older, widely used versions ({satz}) …",
        pdfium_aus="Windows blocked the preview library, so it was switched off. The PDFs are still created; only the "
                   "preview images are missing.",
        w_symbol="The icon couldn’t be created ({grund}) – no problem: from now on simply start with “{start}”.",
        w_admin="Note: the program was started “as administrator”. That is not necessary – a normal double-click is "
                "enough.",
        w_fremd="Note: this is not the program's own Python ({exe}).",
        fertig="Setup complete – great, off you go!",
        kuenftig_win="From now on, start with the desktop icon “Me Goos-ta Deutsch” (or the Start menu).",
        kuenftig_mac="From now on, start with “Me Goos-ta Deutsch” in Launchpad or the Applications folder.",
        kuenftig_linux="From now on, start with “Me Goos-ta Deutsch” in the application menu.",
        starte="Starting the interface …", warte_start="The interface is still starting – one moment …",
        oeffne="The interface is open in the browser – have fun making cards!",
        laeuft_schon="Me Goos-ta Deutsch is already running – the browser opens in a moment. Welcome back!",
        alte_version="An older version of the interface is still running – stopping it.",
        adresse="If no browser opens, enter this address in your browser:",
        schliesst="This window closes by itself in a moment.",
        fenster_zu="You can close this window now. Happy learning!",
        warte_sperre="Another start window is setting things up – waiting until it is finished …",
        beendet="The interface is taking a break – see you next time!", nichts_laeuft="The interface is not running.",
        entfernt="Removed: {was}", entfernen_fertig="Python, packages and icons were removed. You can delete or keep "
                 "the program folder with your images and PDFs yourself.",
        fehler_titel="Me Goos-ta Deutsch – small hiccup",
        f_temp="The program is running from a temporary folder – probably straight from the ZIP file.\n\n"
               "Please extract the ZIP file first (right-click → “Extract All …”), then double-click “{start}” in the "
               "extracted folder.",
        f_schreiben="The program folder is not writable:\n{ordner}\n\nWhat to do: move the folder “{name}” somewhere "
                    "else, e.g. to “Documents” or the desktop, and start it there.{extra}",
        f_schreiben_win="\nIf “Controlled folder access” is on in Windows Security, allow Python there or choose an "
                        "unprotected folder.",
        f_schreiben_mac="\nmacOS may ask for access to “Downloads”/“Documents” – please click “Allow”. Otherwise: "
                        "System Settings → Privacy & Security → Files and Folders → allow Terminal.",
        f_daten="The folder for Python and packages cannot be created:\n{ordner}\n({grund})",
        f_platz="Not enough free disk space: {frei} MB free, about {noetig} MB needed ({ort}).\n"
                "Free up a little space and then simply start again.",
        f_internet="No internet connection (or it is being blocked).\n\nThe first-time setup needs internet once "
                   "(about 90 MB) – afterwards everything works offline. Please check the connection and start again.",
        f_pip="The packages could not be installed.\n\n{grund}\n\nDetails: {log}",
        f_zugriff="Access denied – the program is probably still open, or an antivirus is scanning files. Please close "
                  "all Me Goos-ta Deutsch windows and start again.",
        f_sac="Windows blocks a file of the image library: {datei}\n(“Smart App Control”). Older versions were blocked "
              "as well.\n\nOptions:\n"
              "1. Turn off Smart App Control: Start → “Windows Security” → “App & browser control” → “Smart App Control "
              "settings” → “Off”. On current Windows versions (from the April 2026 update) it can be turned back on there "
              "later; on older ones only by resetting Windows.\n"
              "2. Use the program on another computer (Windows without this block, or a Mac).\n\n"
              "Then simply start again.",
        f_richtlinie="A policy on this computer (e.g. from a school or company) blocks {datei}.\n"
                     "Please ask your IT department or use another computer.",
        f_virus="The antivirus blocked or removed a file: {datei}\nPlease check “Windows Security → Protection "
                "history” and allow the file. Then start again.",
        f_import="The packages cannot be loaded:\n{details}\n\nDetails: {log}",
        f_fremd="Packages cannot be installed with this Python ({exe}).\nPlease start with “{start}” – the start file "
                "brings its own Python.",
        f_server="The interface could not start.\n\nLast messages:\n{text}\n\nAll messages: {log}",
        f_server_zeit="The interface isn’t responding right now – just start again.\nMessages: {log}",
        f_sperre="Another start window is setting things up. Wait a moment until it’s done, then start again.",
        f_unerwartet="Something unexpected happened: {fehler}\n\nDetails: {log}\nTip: double-click “{start}” in the program folder "
                     "once – that repairs most problems.",
        f_ordner_weg="The program folder was moved or deleted:\n{ort}\n\nPlease double-click “{start}” once in the new "
                     "folder – then the icon works again.",
        pause="Press Enter to continue …",
        frei_mb="{mb} MB free",
        aus_vorrat="taken over from the earlier setup (no download needed)",
        uebernahme_titel="Me Goos-ta Deutsch – new version",
        uebernahme_frage="This version is in a new folder. The previous folder\n{alt}\ncontains your cards "
                         "({karten} cards, {bilder} images{gans}).\n\nShould they be taken over – including settings and "
                         "already enhanced images? The previous folder stays unchanged; this version's example cards are "
                         "moved to “Programm/_beispiele”.",
        uebernahme_gans=", own goose image", frage_jn="Take them over? [Y/n] ", ja="Yes", nein="No",
        s_uebernahme="Taking over cards from the previous folder",
        uebernommen="Taken over: {karten} cards, {bilder} images, {cache} enhanced images{gans}.",
        nicht_uebernommen="Not taken over – you start with the example cards. To take them over later: copy karten.csv "
                          "and the folder “bilder” from {alt} into the new folder “Programm”.",
        w_uebernahme="Taking over did not fully succeed ({grund}). The previous folder is unchanged: {alt}",
    ),
    "es": dict(
        kopf="Me Goos-ta Deutsch – tarjetas para imprimir",
        einrichtung="Instalación: la primera vez tarda unos minutos. Deja esta ventana abierta y ponte cómodo.",
        g_erst="Primer inicio detectado: se instala todo lo necesario.",
        g_python="Nuevo Python detectado: se ajustan los paquetes.",
        g_pakete="Nueva versión del programa detectada: se revisan los paquetes.",
        g_ordner="Nueva carpeta del programa detectada: se prepara.",
        g_reparatur="Reparación: se revisa todo de nuevo.",
        s_ort="Revisando carpeta y espacio libre", s_pip="Preparando el gestor de paquetes",
        s_pakete="Descargando e instalando paquetes (unos 60 MB)", s_test="Revisando los paquetes",
        s_modell="Conservando las herramientas instaladas (mejora de imagen, sin descarga)",
        s_symbole_win="Creando el icono del escritorio y la entrada del menú Inicio",
        s_symbole_mac="Agregando «Me Goos-ta Deutsch» a la carpeta Aplicaciones",
        s_symbole_linux="Agregando una entrada al menú de aplicaciones",
        ok="listo", schon_da="ya existe", lade="↓ {name} {version}  ({groesse})",
        installiere="instalando: {liste}", noch="… sigue trabajando ({min} min); ya casi, gracias por tu paciencia",
        neuer_versuch="La conexión falla; intentando de nuevo …",
        ersatz="Windows bloquea {datei}; probando versiones anteriores y muy usadas ({satz}) …",
        pdfium_aus="Windows bloqueó la biblioteca de vista previa y se desactivó. Los PDF se crean igual; solo faltan "
                   "las imágenes de vista previa.",
        w_symbol="No se pudo crear el icono ({grund}); no pasa nada: a partir de ahora inicia con «{start}».",
        w_admin="Nota: el programa se inició «como administrador». No hace falta: basta con un doble clic normal.",
        w_fremd="Nota: este no es el Python propio del programa ({exe}).",
        fertig="¡Instalación terminada! Todo listo para empezar.",
        kuenftig_win="A partir de ahora inicia con el icono «Me Goos-ta Deutsch» del escritorio (o del menú Inicio).",
        kuenftig_mac="A partir de ahora inicia con «Me Goos-ta Deutsch» en Launchpad o en la carpeta Aplicaciones.",
        kuenftig_linux="A partir de ahora inicia con «Me Goos-ta Deutsch» en el menú de aplicaciones.",
        starte="Iniciando la interfaz …", warte_start="La interfaz sigue iniciando; un momento …",
        oeffne="La interfaz está abierta en el navegador. ¡Diviértete creando cartas!",
        laeuft_schon="Me Goos-ta Deutsch ya está abierto; el navegador se abre enseguida. ¡Qué bueno verte de nuevo!",
        alte_version="Todavía funciona una versión anterior de la interfaz; se cierra.",
        adresse="Si no se abre ningún navegador, escribe esta dirección en el navegador:",
        schliesst="Esta ventana se cierra sola en un momento.",
        fenster_zu="Ya puedes cerrar esta ventana. ¡Mucho éxito aprendiendo!",
        warte_sperre="Otra ventana de inicio está instalando; espero a que termine …",
        beendet="La interfaz se toma un descanso. ¡Hasta la próxima!", nichts_laeuft="La interfaz no está abierta.",
        entfernt="Eliminado: {was}", entfernen_fertig="Se eliminaron Python, los paquetes y los iconos. La carpeta del "
                 "programa con tus imágenes y PDF puedes borrarla o conservarla tú.",
        fehler_titel="Me Goos-ta Deutsch – pequeño tropiezo",
        f_temp="El programa se está ejecutando desde una carpeta temporal, probablemente directamente desde el ZIP.\n\n"
               "Primero descomprime el archivo ZIP (clic derecho → «Extraer todo …») y luego haz doble clic en "
               "«{start}» dentro de la carpeta extraída.",
        f_schreiben="No se puede escribir en la carpeta del programa:\n{ordner}\n\nQué hacer: mueve la carpeta «{name}» "
                    "a otro lugar, por ejemplo a «Documentos» o al escritorio, e inicia desde ahí.{extra}",
        f_schreiben_win="\nSi en Seguridad de Windows está activado el «Acceso controlado a carpetas», permite Python "
                        "allí o elige una carpeta no protegida.",
        f_schreiben_mac="\nmacOS puede pedir acceso a «Descargas»/«Documentos»: haz clic en «Permitir». Si no: "
                        "Configuración del Sistema → Privacidad y seguridad → Archivos y carpetas → permitir Terminal.",
        f_daten="No se puede crear la carpeta para Python y los paquetes:\n{ordner}\n({grund})",
        f_platz="No hay suficiente espacio libre: {frei} MB libres, se necesitan unos {noetig} MB ({ort}).\n"
                "Libera un poco de espacio y vuelve a iniciar.",
        f_internet="No hay conexión a internet (o está bloqueada).\n\nLa instalación del primer inicio necesita internet "
                   "una sola vez (unos 90 MB); después todo funciona sin conexión. Revisa la conexión e inicia de nuevo.",
        f_pip="No se pudieron instalar los paquetes.\n\n{grund}\n\nDetalles: {log}",
        f_zugriff="Acceso denegado: probablemente el programa sigue abierto o un antivirus está revisando archivos. "
                  "Cierra todas las ventanas de Me Goos-ta Deutsch e inicia de nuevo.",
        f_sac="Windows bloquea un archivo de la biblioteca de imágenes: {datei}\n(«Control inteligente de "
              "aplicaciones» / Smart App Control). Las versiones anteriores también se bloquearon.\n\nOpciones:\n"
              "1. Desactivar el Control inteligente de aplicaciones: Inicio → «Seguridad de Windows» → «Control de "
              "aplicaciones y navegador» → «Configuración de Control inteligente de aplicaciones» → «Desactivado». "
              "En versiones actuales de Windows (desde la actualización de abril de 2026) se puede volver a activar ahí "
              "más tarde; en versiones anteriores solo restableciendo Windows.\n"
              "2. Usar el programa en otra computadora (Windows sin este bloqueo o una Mac).\n\n"
              "Después, simplemente inicia de nuevo.",
        f_richtlinie="Una directiva de esta computadora (por ejemplo, de la escuela o la empresa) bloquea {datei}.\n"
                     "Pregunta al departamento de informática o usa otra computadora.",
        f_virus="El antivirus bloqueó o eliminó un archivo: {datei}\nRevisa «Seguridad de Windows → Historial de "
                "protección» y permite el archivo. Después inicia de nuevo.",
        f_import="No se pueden cargar los paquetes:\n{details}\n\nDetalles: {log}",
        f_fremd="Con este Python no se pueden instalar los paquetes ({exe}).\nInicia con «{start}»: el archivo de "
                "inicio trae su propio Python.",
        f_server="La interfaz no pudo iniciar.\n\nÚltimos mensajes:\n{text}\n\nTodos los mensajes: {log}",
        f_server_zeit="La interfaz no responde por ahora; vuelve a iniciar y listo.\nMensajes: {log}",
        f_sperre="Otra ventana de inicio está instalando. Espera un momento a que termine y vuelve a iniciar.",
        f_unerwartet="Pasó algo inesperado: {fehler}\n\nDetalles: {log}\nConsejo: haz doble clic una vez en «{start}» en "
                     "la carpeta del programa; eso repara la mayoría de los problemas.",
        f_ordner_weg="La carpeta del programa se movió o se borró:\n{ort}\n\nHaz doble clic una vez en «{start}» en la "
                     "carpeta nueva; después el icono vuelve a funcionar.",
        pause="Pulsa Intro para continuar …",
        frei_mb="{mb} MB libres",
        aus_vorrat="tomado de la instalación anterior (sin descarga)",
        uebernahme_titel="Me Goos-ta Deutsch – versión nueva",
        uebernahme_frage="Esta versión está en una carpeta nueva. En la carpeta anterior\n{alt}\nestán tus cartas "
                         "({karten} cartas, {bilder} imágenes{gans}).\n\n¿Las pasamos a esta versión, junto con los "
                         "ajustes y las imágenes ya mejoradas? La carpeta anterior no cambia; las cartas de ejemplo de "
                         "esta versión se guardan en «Programm/_beispiele».",
        uebernahme_gans=", imagen de ganso propia", frage_jn="¿Pasarlas? [S/n] ", ja="Sí", nein="No",
        s_uebernahme="Pasando las cartas de la carpeta anterior",
        uebernommen="Se pasaron: {karten} cartas, {bilder} imágenes, {cache} imágenes mejoradas{gans}.",
        nicht_uebernommen="No se pasaron; empiezas con las cartas de ejemplo. Para pasarlas después: copia karten.csv y "
                          "la carpeta «bilder» de {alt} a la nueva carpeta «Programm».",
        w_uebernahme="No se pudo pasar todo ({grund}). La carpeta anterior no cambió: {alt}",
    ),
}
# Texte der Erweiterungen (Programmstart im Fenster, Deinstallieren) – eigener Block, die Tabelle oben bleibt wörtlich
TEXTE["de"].update(
    banner_satz="Deutsch lernen mit Wortwitz – schön, dass du da bist!",
    arbeite="Einen Moment – die Ente schwimmt, ich arbeite",
    starte_lade="Die Oberfläche macht sich startklar",
    fenster_fehlt="Für das eigene Fenster wurde kein Edge, Chrome, Brave oder Chromium gefunden – die Oberfläche "
                  "öffnet sich im Standard-Browser.",
    deinst_titel="Me Goos-ta Deutsch – Deinstallieren",
    deinst_fertig="Me Goos-ta Deutsch wird jetzt entfernt:\n{daten}\n{ort}\n\nNach „OK“ dauert es noch ein paar Sekunden.",
    deinst_ort="Der Programmordner sieht nicht wie ein Me-Goos-ta-Deutsch-Ordner aus – aus Sicherheitsgründen wird "
               "nichts gelöscht:\n{ort}",
)
TEXTE["en"].update(
    banner_satz="Learn German with puns – great to have you here!",
    arbeite="One moment – the duck is paddling, I am on it",
    starte_lade="The interface is getting ready",
    fenster_fehlt="No Edge, Chrome, Brave or Chromium was found for the own window – the interface opens in the "
                  "default browser.",
    deinst_titel="Me Goos-ta Deutsch – Uninstall",
    deinst_fertig="Me Goos-ta Deutsch is now being removed:\n{daten}\n{ort}\n\nAfter “OK” it takes a few more seconds.",
    deinst_ort="The program folder does not look like a Me Goos-ta Deutsch folder – for safety nothing is deleted:\n{ort}",
)
TEXTE["es"].update(
    banner_satz="Aprende alemán con juegos de palabras: ¡qué bueno que estás aquí!",
    arbeite="Un momento: el pato nada y yo trabajo",
    starte_lade="La interfaz se está preparando",
    fenster_fehlt="No se encontró Edge, Chrome, Brave ni Chromium para la ventana propia; la interfaz se abre en el "
                  "navegador predeterminado.",
    deinst_titel="Me Goos-ta Deutsch – Desinstalar",
    deinst_fertig="Me Goos-ta Deutsch se está quitando:\n{daten}\n{ort}\n\nDespués de «OK» tarda unos segundos más.",
    deinst_ort="La carpeta del programa no parece de Me Goos-ta Deutsch; por seguridad no se borra nada:\n{ort}",
)
SPRACHE = "de"


def T(schluessel, **werte):
    text = TEXTE.get(SPRACHE, TEXTE["de"]).get(schluessel) or TEXTE["de"][schluessel]
    return text.format(**werte) if werte else text


def ermittle_sprache() -> str:
    """Reihenfolge: in der Oberfläche gewählte Sprache → MGD_SPRACHE → Englisch. Die Systemsprache zählt nicht:
    vor der ersten Wahl im Programm ist alles Englisch (wie LIES MICH, Startdateien und Willkommens-Assistent)."""
    try:
        s = json.loads((HIER / "ui_einstellungen.json").read_text(encoding="utf-8")).get("sprache")
        if s in TEXTE:
            return s
    except (OSError, ValueError, AttributeError):
        pass
    s = os.environ.get("MGD_SPRACHE", "")[:2].lower()
    return s if s in TEXTE else "en"


# =============================================================================================
# Ausgabe: Konsole (Startdatei) oder Dialog (Desktop-Symbol), immer zusätzlich ins Protokoll
# =============================================================================================
class Abbruch(Exception):
    """Ein Problem, das der Nutzer verstehen und beheben kann (Text ist schon übersetzt)."""


def hat_konsole() -> bool:
    if sys.stdout is None:
        return False
    if WIN:
        try:
            import ctypes
            return bool(ctypes.windll.kernel32.GetConsoleWindow())
        except Exception:  # noqa: BLE001
            return False
    try:
        return sys.stdout.isatty()
    except (AttributeError, ValueError):
        return False


class Ausgabe:
    def __init__(self, konsole: bool):
        self.konsole = konsole and sys.stdout is not None
        self.log = None
        self.ente = None                               # laufende Lade-Ente (duck_spinner.py) oder None
        self.log_pfad = DATEN / "protokoll.txt"
        for strom in (sys.stdout, sys.stderr):
            try:
                strom.reconfigure(errors="replace")
            except (AttributeError, ValueError):
                pass

    def oeffne_log(self):
        try:
            DATEN.mkdir(parents=True, exist_ok=True)
            if self.log_pfad.exists() and self.log_pfad.stat().st_size > 2_000_000:
                self.log_pfad.replace(self.log_pfad.with_name("protokoll.alt.txt"))
            self.log = open(self.log_pfad, "a", encoding="utf-8")
            self.log.write(f"\n===== {time.strftime('%Y-%m-%d %H:%M:%S')} · {PRODUKT} {VERSION} · "
                           f"{sys.executable} · {HIER} =====\n")
        except OSError:
            self.log = None

    def protokoll(self, text):
        if self.log:
            try:
                self.log.write(text.rstrip("\n") + "\n")
                self.log.flush()
            except (OSError, ValueError):
                pass

    def zeile(self, text="", nur_log=False):
        self.protokoll(text)
        if self.konsole and not nur_log:
            try:
                if self.ente is not None:              # Zeile über der Lade-Ente ausgeben, die Animation läuft weiter
                    self.ente.zeile(text)
                else:
                    print(text, flush=True)
            except (OSError, ValueError):
                pass

    @contextlib.contextmanager
    def lade(self, text):
        """Lade-Ente (duck_spinner.py) unter den Ausgaben, solange etwas Längeres läuft – nur in einer echten Konsole."""
        if not self.konsole or self.ente is not None:
            yield None
            return
        try:
            from duck_spinner import DuckSpinner
            ente = DuckSpinner("  " + text, width=34)
        except Exception:  # noqa: BLE001                 # ohne Ente geht es genauso – nur weniger hübsch
            yield None
            return
        self.ente = ente.start() if ente._animate else None
        try:
            yield ente
        finally:
            if self.ente is not None:
                self.ente = None
                ente.stop()

    def schritt(self, nr, gesamt, text):
        balken = "■" * nr + "□" * max(0, gesamt - nr)            # Fortschritt der Einrichtung auf einen Blick
        self.zeile(f"\n  [{nr}/{gesamt}] {balken}  {text}")

    def banner(self):
        """Kopf der Konsole: Name, Version, ein freundlicher Satz – und die Ente schwimmt bei langen Schritten."""
        breite = 60
        zeilen = [f"{PRODUKT}  ·  {VERSION}", T("banner_satz")]
        self.zeile("\n  ╭" + "─" * breite + "╮")
        for z in zeilen:
            self.zeile("  │  " + z[:breite - 3].ljust(breite - 3) + " │")
        self.zeile("  ╰" + "─" * breite + "╯")

    def unter(self, text):
        self.zeile(f"        {text}")

    def problem(self, text, titel=None):
        self.protokoll("PROBLEM: " + text)
        if self.konsole:
            rahmen = "  " + "─" * 66
            meldung = f"\n{rahmen}\n  ! " + text.replace("\n", "\n    ") + f"\n{rahmen}"
            if self.ente is not None:
                self.ente.zeile(meldung)
            else:
                print(meldung, flush=True)
        else:
            dialog(titel or T("fehler_titel"), text)


def dialog(titel, text, fehler=True):
    """Meldung ohne Konsole (Start über das Desktop-Symbol): Windows-Meldungsfenster, macOS-Hinweis, Linux zenity."""
    try:
        if WIN:
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, text, titel, (0x10 if fehler else 0x40) | 0x10000 | 0x40000)
        elif MAC:
            subprocess.run(["osascript", "-e", "on run argv", "-e",
                            "display alert (item 1 of argv) message (item 2 of argv)" + (" as critical" if fehler else ""),
                            "-e", "end run", titel, text], timeout=3600, capture_output=True)
        else:
            for befehl in (["zenity", "--error" if fehler else "--info", "--no-wrap", "--title", titel, "--text", text],
                           ["kdialog", "--title", titel, "--error" if fehler else "--msgbox", text],
                           ["notify-send", titel, text]):
                if shutil.which(befehl[0]):
                    subprocess.run(befehl, timeout=3600, capture_output=True)
                    break
    except Exception:  # noqa: BLE001
        pass


# =============================================================================================
# Hilfen
# =============================================================================================
def lies_json(pfad):
    try:
        daten = json.loads(Path(pfad).read_text(encoding="utf-8"))
        return daten if isinstance(daten, dict) else None
    except (OSError, ValueError):
        return None


def schreibe_json(pfad, daten):
    pfad = Path(pfad)
    tmp = pfad.with_name(pfad.name + f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(daten, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, pfad)


def ist_admin() -> bool:
    try:
        if WIN:
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        return os.geteuid() == 0
    except Exception:  # noqa: BLE001
        return False


def eigenes_python() -> bool:
    """True, wenn das Programm mit der eigenen Laufzeit der Startdatei läuft (dort darf es Pakete installieren)."""
    try:
        Path(sys.executable).resolve().relative_to((DATEN / "python").resolve())
        return True
    except (ValueError, OSError):
        return False


def umgebung(**extra):
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1", PYTHONUNBUFFERED="1",
               MGD_SPRACHE=SPRACHE, MGD_DATEN=str(DATEN), PIP_DISABLE_PIP_VERSION_CHECK="1", PIP_NO_INPUT="1",
               PIP_NO_COLOR="1", PIP_PROGRESS_BAR="off")
    for var in ("PYTHONHOME", "PYTHONPATH", "PYTHONSTARTUP", "PIP_TARGET", "PIP_PREFIX", "PIP_ROOT", "PIP_USER",
                "PIP_REQUIRE_VIRTUALENV", "PIP_SRC", "PIP_NO_INDEX", "PIP_ONLY_BINARY", "PIP_NO_BINARY"):
        env.pop(var, None)
    if eigenes_python():
        env["PIP_CONFIG_FILE"] = os.devnull       # keine fremden pip-Einstellungen (z. B. „user = true“)
        env["PYTHONNOUSERSITE"] = "1"             # keine Pakete aus dem Benutzerordner untermischen
    env.update({k: str(v) for k, v in extra.items()})
    return env


def ohne_fenster() -> dict:
    """Unter Windows keine schwarzen Fenster für Hilfsprozesse."""
    return {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)} if WIN else {}


def python_ohne_konsole() -> str:
    exe = Path(sys.executable)
    if WIN and exe.name.lower() == "python.exe" and (exe.parent / "pythonw.exe").exists():
        return str(exe.parent / "pythonw.exe")
    return str(exe)


def python_mit_konsole() -> str:
    exe = Path(sys.executable)
    if WIN and exe.name.lower() == "pythonw.exe" and (exe.parent / "python.exe").exists():
        return str(exe.parent / "python.exe")
    return str(exe)


def mb(n):
    return max(0, int(n // (1024 * 1024)))


def laufe(aus, befehl, filter_fn=None, lebenszeichen=30, env=None, ladetext=None):
    """Startet einen Hilfsprozess, gibt seine Zeilen (gefiltert) aus und meldet sich, wenn er lange still ist.
    In der Konsole schwimmt währenddessen die Lade-Ente. Rückgabe: (Exitcode, gesamter Text)."""
    with aus.lade(ladetext or T("arbeite")):
        return _laufe(aus, befehl, filter_fn, lebenszeichen, env)


def _laufe(aus, befehl, filter_fn, lebenszeichen, env):
    aus.protokoll("$ " + " ".join(shlex.quote(str(t)) for t in befehl))
    proc = subprocess.Popen([str(t) for t in befehl], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace",
                            env=env or umgebung(), cwd=str(HIER), **ohne_fenster())
    zeilen, q = [], queue.Queue()

    def lesen():
        for z in proc.stdout:
            q.put(z.rstrip("\r\n"))
        q.put(None)

    threading.Thread(target=lesen, daemon=True).start()
    start = letzte = time.time()
    while True:
        try:
            z = q.get(timeout=1)
        except queue.Empty:
            if lebenszeichen and time.time() - letzte > lebenszeichen:
                aus.unter(T("noch", min=max(1, round((time.time() - start) / 60))))
                letzte = time.time()
            continue
        if z is None:
            break
        zeilen.append(z)
        aus.protokoll("  | " + z)
        anzeige = filter_fn(z) if filter_fn else z
        if anzeige:
            aus.unter(anzeige)
            letzte = time.time()
    return proc.wait(), "\n".join(zeilen)


# =============================================================================================
# Ort, Sperre, Erst-Start-Erkennung
# =============================================================================================
def ordner_schluessel(pfad=HIER) -> str:
    text = str(Path(pfad).resolve())
    return hashlib.sha256((text.lower() if WIN else text).encode("utf-8")).hexdigest()[:12]


def pakete_neueste() -> bool:
    return os.environ.get("MGD_PAKETE_NEUESTE") == "1"


def paket_spezifikation(satz=None):
    """pip-Argumente für die Pakete: Lock-Datei (Standard bzw. Ersatz-Satz) mit --require-hashes; nur im CI-Job
    „neueste Fassungen“ die Spannen aus requirements.txt."""
    if pakete_neueste() and satz not in dict(ERSATZ_SAETZE):
        return ["-r", str(HIER / "requirements.txt")]
    return ["--require-hashes", "-r", str(HIER / dict(ERSATZ_SAETZE).get(satz, LOCK))]


def paket_signatur() -> str:
    """Fingerabdruck der Paketfassungen: ändert sich eine Lock-Datei (neue Version), richtet der Starter neu ein."""
    roh = b"".join(n.encode() + ((HIER / n).read_bytes() if (HIER / n).exists() else b"")
                   for n in (LOCK, *dict(ERSATZ_SAETZE).values()))
    if pakete_neueste():
        roh += b"neueste" + ((HIER / "requirements.txt").read_bytes() if (HIER / "requirements.txt").exists() else b"")
    return hashlib.sha256(roh).hexdigest()[:16]


def pruefe_ort(aus):
    """Erkennt den Start aus der ZIP-Datei (Windows legt dann nur eine einzelne Datei in einen Temp-Ordner) und
    nicht beschreibbare Ordner (Programme-Ordner, „Überwachter Ordnerzugriff“, schreibgeschützte Medien)."""
    if WIN:
        pfad = str(HIER).lower()
        temps = {os.environ.get("TEMP", ""), os.environ.get("TMP", "")}
        if re.search(r"[\\/]temp\d*_[^\\/]+\.zip", pfad) or any(
                t and pfad.startswith(os.path.normcase(os.path.abspath(t)).lower() + "\\") for t in temps):
            raise Abbruch(T("f_temp", start=STARTDATEI))
    probe = HIER / f".schreibtest-{os.getpid()}"
    try:
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError:
        extra = T("f_schreiben_win") if WIN else T("f_schreiben_mac") if MAC else ""
        raise Abbruch(T("f_schreiben", ordner=HIER, name=WURZEL.name, extra=extra)) from None


def brauche_einrichtung(erzwingen=False):
    if erzwingen:
        return "reparatur"
    st = lies_json(STEMPEL)
    if not st:
        return "erst"
    if st.get("prefix") != sys.prefix or st.get("python") != sys.version.split()[0]:
        return "python"
    if st.get("pakete") != paket_signatur():
        return "pakete"
    if ordner_schluessel() not in st.get("ordner", []):
        return "ordner"
    return None


class Sperre:
    """Verhindert, dass zwei Startfenster gleichzeitig einrichten (z. B. nach einem Doppel-Doppelklick)."""

    def __init__(self, aus, warten=1800):
        self.aus, self.warten, self.datei = aus, warten, None

    def __enter__(self):
        self.datei = open(DATEN / "start.sperre", "a+")
        start, gemeldet = time.time(), False
        while True:
            try:
                if WIN:
                    import msvcrt
                    self.datei.seek(0)
                    msvcrt.locking(self.datei.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(self.datei.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except OSError:
                if not gemeldet:
                    self.aus.zeile("  " + T("warte_sperre"))
                    gemeldet = True
                if time.time() - start > self.warten:
                    raise Abbruch(T("f_sperre")) from None
                time.sleep(0.5)

    def __exit__(self, *_):
        try:
            if WIN:
                import msvcrt
                self.datei.seek(0)
                msvcrt.locking(self.datei.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.datei.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        self.datei.close()


def merke_ort():
    """Das Desktop-Symbol startet über DATEN/starte.py – das liest hier, wo der Programmordner gerade liegt."""
    try:
        alt = (DATEN / "programm-ort.txt").read_text(encoding="utf-8").strip()
    except OSError:
        alt = ""
    if alt != str(HIER):
        try:
            (DATEN / "programm-ort.txt").write_text(str(HIER), encoding="utf-8")
        except OSError:
            pass


# =============================================================================================
# Neue Version in einem neuen Ordner: eigene Karten aus dem bisherigen Ordner übernehmen
# =============================================================================================
NUTZER_DATEIEN = ("karten.csv", "karten.bak.csv", "ui_einstellungen.json", "ideen.json", "lernstand.json",
                  "lernstand.bak.json")
NUTZER_ORDNER = ("bilder", "ausgabe", "ideen")
GANS_DATEIEN = ("gans_hintergrund.png", "gans_hintergrund.jpg")


def vorheriger_ort():
    """Programmordner vom letzten Start (DATEN/programm-ort.txt) – nur, wenn es ein anderer ist und er Karten hat."""
    try:
        alt = Path((DATEN / "programm-ort.txt").read_text(encoding="utf-8").strip())
        if str(alt) and alt.is_dir() and alt.resolve() != HIER.resolve() and (alt / "karten.csv").is_file():
            return alt
    except (OSError, ValueError):
        pass
    return None


def _dateien(basis):
    basis = Path(basis)
    if not basis.is_dir() or basis.is_symlink():
        return []
    return [q for q in basis.rglob("*") if q.is_file() and not q.is_symlink() and not q.name.endswith(".tmp")]


def _gleich(a, b):
    try:
        return a.stat().st_size == b.stat().st_size and a.read_bytes() == b.read_bytes()
    except OSError:
        return False


def eigene_daten(alt):
    """Was liegt im bisherigen Ordner, das es hier noch nicht gibt? dict(karten, bilder, cache, gans) oder None."""
    hier = HIER / "karten.csv" if (HIER / "karten.csv").is_file() else HIER / "beispiel-karten.csv"
    unterschiede = 0 if _gleich(alt / "karten.csv", hier) else 1
    for ordner in NUTZER_ORDNER:
        for q in _dateien(alt / ordner):
            z = HIER / ordner / q.relative_to(alt / ordner)
            if ordner == "bilder" and not z.is_file():          # frisch entpackt: noch kein Bilderordner
                z = HIER / "beispiel-bilder" / q.relative_to(alt / ordner)
            if not z.is_file() or not _gleich(q, z):
                unterschiede += 1
    gans = [alt / "assets" / n for n in GANS_DATEIEN if (alt / "assets" / n).is_file()]
    unterschiede += sum(1 for q in gans if not _gleich(q, HIER / "assets" / q.name))
    if not unterschiede:
        return None
    try:
        zeilen = (alt / "karten.csv").read_text(encoding="utf-8-sig", errors="replace").splitlines()[1:]
        karten = sum(1 for z in zeilen if z.strip() and not z.lstrip().startswith("#"))
    except OSError:
        karten = 0
    bilder = sum(1 for q in _dateien(alt / "bilder") if "_entfernt" not in q.relative_to(alt / "bilder").parts)
    cache = sum(1 for q in _dateien(alt / "ausgabe" / ".cache") if q.suffix == ".jpg" and not q.name.startswith("vorschau-"))
    return dict(karten=karten, bilder=bilder, cache=cache, gans=bool(gans))


def frage_ja_nein(aus, titel, text):
    """Ja/Nein-Frage: in der Konsole per Eingabe (Enter = Ja), sonst als Fenster. Ohne Möglichkeit zu fragen: Ja
    (die Übernahme kopiert nur und sichert, was sie ersetzt)."""
    if aus.konsole:
        aus.zeile("\n  " + text.replace("\n", "\n  "))
        try:
            antwort = input("\n  " + T("frage_jn")).strip().lower()
        except (EOFError, OSError, RuntimeError):
            antwort = ""
        aus.protokoll(f"Antwort: {antwort!r}")
        return not antwort.startswith("n")
    try:
        if WIN:
            import ctypes
            return ctypes.windll.user32.MessageBoxW(None, text, titel, 0x04 | 0x20 | 0x10000 | 0x40000) == 6
        if MAC:
            r = subprocess.run(["osascript", "-e", "on run argv", "-e",
                                "display dialog (item 2 of argv) with title (item 1 of argv) buttons {item 3 of argv, "
                                "item 4 of argv} default button 2", "-e", "end run", titel, text, T("nein"), T("ja")],
                               capture_output=True, text=True, timeout=3600)
            return r.returncode == 0 and T("ja") in r.stdout
        if shutil.which("zenity"):
            return subprocess.run(["zenity", "--question", "--no-wrap", "--title", titel, "--text", text],
                                  timeout=3600).returncode == 0
    except Exception:  # noqa: BLE001
        pass
    return True


def uebernimm_daten(aus, alt):
    """Kopiert die eigenen Daten aus dem bisherigen Ordner hierher (der bisherige Ordner bleibt, wie er ist).
    Was hier dadurch ersetzt würde – die Beispielkarten dieser Version –, wird vorher nach _beispiele/ gesichert.
    Gibt die Zahlen für die Meldung zurück."""
    sicherung = HIER / "_beispiele"
    zahl = dict(karten=0, bilder=0, cache=0, gans="")

    def sichern(z):
        ziel = sicherung / z.relative_to(HIER)
        if not ziel.exists():
            ziel.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(z, ziel)

    def kopiere(q, z):
        if z.is_file():
            if _gleich(q, z):
                return False
            sichern(z)
        z.parent.mkdir(parents=True, exist_ok=True)
        tmp = z.with_name(f"{z.name}.{os.getpid()}.tmp")
        shutil.copy2(q, tmp)
        os.replace(tmp, z)
        return True

    for name in NUTZER_DATEIEN:
        if (alt / name).is_file():
            kopiere(alt / name, HIER / name)
    for ordner in NUTZER_ORDNER:
        for q in _dateien(alt / ordner):
            rel = q.relative_to(alt / ordner)
            if kopiere(q, HIER / ordner / rel):
                if ordner == "bilder" and "_entfernt" not in rel.parts:
                    zahl["bilder"] += 1
                elif ordner == "ausgabe" and rel.parts[0] == ".cache" and q.suffix == ".jpg" \
                        and not q.name.startswith("vorschau-"):
                    zahl["cache"] += 1
    gans = [alt / "assets" / n for n in GANS_DATEIEN if (alt / "assets" / n).is_file()]
    if gans:                                                    # es darf nur ein Gänse-Bild gelten
        for n in GANS_DATEIEN:
            z = HIER / "assets" / n
            if z.is_file() and not any(q.name == n for q in gans):
                sichern(z)
                z.unlink()
        for q in gans:
            kopiere(q, HIER / "assets" / q.name)
        zahl["gans"] = T("uebernahme_gans")
    for q in _dateien(alt / "assets" / "_alt"):
        kopiere(q, HIER / "assets" / "_alt" / q.relative_to(alt / "assets" / "_alt"))
    einst = HIER / "ui_einstellungen.json"                    # Pfade in den alten Ordner → neuer Ordner
    d = lies_json(einst)
    if d and isinstance(d.get("werte"), dict):
        vorher, geaendert = str(alt), False
        for k, v in list(d["werte"].items()):
            if isinstance(v, str) and (v == vorher or v.startswith(vorher + os.sep) or v.startswith(vorher + "/")):
                d["werte"][k] = str(HIER) + v[len(vorher):]
                geaendert = True
        if geaendert:
            schreibe_json(einst, d)
    try:
        zeilen = (HIER / "karten.csv").read_text(encoding="utf-8-sig", errors="replace").splitlines()[1:]
        zahl["karten"] = sum(1 for z in zeilen if z.strip() and not z.lstrip().startswith("#"))
    except OSError:
        pass
    return zahl


def biete_uebernahme_an(aus, alt):
    info = eigene_daten(alt)
    if not info:
        return
    gans = T("uebernahme_gans") if info["gans"] else ""
    if not frage_ja_nein(aus, T("uebernahme_titel"), T("uebernahme_frage", alt=alt, karten=info["karten"],
                                                         bilder=info["bilder"], gans=gans)):
        aus.zeile("  " + T("nicht_uebernommen", alt=alt))
        return
    aus.zeile("\n  " + T("s_uebernahme") + " …")
    beende_alle_instanzen(aus, still=True)                     # die alte Oberfläche könnte gerade speichern
    try:
        zahl = uebernimm_daten(aus, alt)
        aus.unter("✓ " + T("uebernommen", **zahl))
    except OSError as e:
        aus.protokoll(traceback.format_exc())
        aus.zeile("  ! " + T("w_uebernahme", grund=e, alt=alt))


# =============================================================================================
# Einrichtung: pip, Pakete, Prüfung (inkl. Smart App Control), KI-Modell, Symbole
# =============================================================================================
PIP_AUS_RAD = ("import runpy, sys; rad = sys.argv[1]; sys.path.insert(0, rad); sys.argv = ['pip'] + sys.argv[2:]; "
               "runpy.run_module('pip', run_name='__main__', alter_sys=True)")
NETZ_WORTE = ("newconnectionerror", "failed to establish", "getaddrinfo", "name or service not known",
              "temporary failure in name resolution", "proxyerror", "connecttimeout", "read timed out",
              "max retries exceeded", "network is unreachable", "no route to host", "sslerror", "connection refused",
              "connectionreseterror", "nodename nor servname")
PLATZ_WORTE = ("no space left", "errno 28", "winerror 112", "nicht genügend speicher", "espacio suficiente")


def pip_filter(z):
    s = z.strip()
    m = re.match(r"Downloading (\S+?)-(\d[^-\s]*)-\S*\.whl \(([^)]+)\)", s)
    if m and ".metadata" not in s:
        return T("lade", name=m.group(1), version=m.group(2), groesse=m.group(3))
    m = re.match(r"Installing collected packages: (.+)", s)
    if m:
        return T("installiere", liste=m.group(1))
    if s.startswith("Successfully installed"):
        return "✓ " + s.replace("Successfully installed", "").strip()
    if "Retrying (Retry(" in s:
        return T("neuer_versuch")
    if s.startswith("ERROR:"):
        return s
    return None


def pip_lauf(aus, args, anzeigen=True):
    return laufe(aus, [sys.executable, "-m", "pip", *args], pip_filter if anzeigen else (lambda z: None))


def pip_grund(text):
    klein = text.lower()
    if any(w in klein for w in NETZ_WORTE):
        return "internet"
    if any(w in klein for w in PLATZ_WORTE):
        return "platz"
    if "externally-managed-environment" in klein or "externally managed" in klein:
        return "fremd"
    if "winerror 5" in klein or "permission denied" in klein or "zugriff verweigert" in klein or \
            "acceso denegado" in klein:
        return "zugriff"
    return "anders"


def pip_fehler(text):
    grund = pip_grund(text)
    if grund == "internet":
        return Abbruch(T("f_internet"))
    if grund == "platz":
        frei = mb(shutil.disk_usage(DATEN).free)
        return Abbruch(T("f_platz", frei=frei, noetig=MIN_FREI_MB, ort=DATEN))
    if grund == "fremd":
        return Abbruch(T("f_fremd", exe=sys.executable, start=STARTDATEI))
    if grund == "zugriff":
        return Abbruch(T("f_zugriff"))
    letzte = [z for z in text.splitlines() if z.strip().startswith("ERROR")][-3:] or text.splitlines()[-4:]
    return Abbruch(T("f_pip", grund="\n".join(letzte)[-800:], log=aus_log()))


def aus_log():
    return str(DATEN / "protokoll.txt")


def hat_pip():
    r = subprocess.run([sys.executable, "-c", "import pip"], capture_output=True, env=umgebung(), **ohne_fenster())
    return r.returncode == 0


def bereite_pip(aus):
    """Das „embeddable“ Python von python.org kommt ohne pip – es wird aus dem mitgelieferten Rad installiert."""
    if hat_pip():
        aus.unter(T("schon_da"))
        return
    raeder = sorted((HIER / "werkzeuge").glob("pip-*.whl"))
    if not raeder:
        raise Abbruch(T("f_import", details="pip fehlt / missing", log=aus_log()))
    rad = raeder[-1]
    code, text = laufe(aus, [sys.executable, "-c", PIP_AUS_RAD, rad, "install", "--no-index", "--no-warn-script-location",
                             "--disable-pip-version-check", rad], lambda z: None)
    if code != 0 or not hat_pip():
        raise pip_fehler(text)
    aus.unter(T("ok"))


def lokale_pakete():
    """Optional: Ordner werkzeuge/pakete mit Rädern (.whl) – für Rechner ohne Internet (z. B. im Klassenzimmer).
    Füllen auf einem Rechner mit Internet:  pip download -d werkzeuge/pakete --require-hashes -r pakete.lock
                                             --only-binary=:all: --platform win_amd64 --python-version 3.13
    (die Prüfsummen der Lock-Datei gelten auch für diesen Ordner)"""
    lokal = HIER / "werkzeuge" / "pakete"
    return lokal if lokal.is_dir() and any(lokal.glob("*.whl")) else None


def installiere(aus, spezifikation, extra=()):
    args = ["install", "--only-binary=:all:", "--prefer-binary", "--no-warn-script-location", *extra]
    if not eigenes_python() and sys.prefix == sys.base_prefix:
        args.append("--user")
    lokal = lokale_pakete()
    if lokal:                                          # zuerst nur aus dem lokalen Ordner (ohne Internet)
        code, text = pip_lauf(aus, [*args, "--no-index", "--find-links", str(lokal), *spezifikation])
        if code == 0:
            return text
        args += ["--find-links", str(lokal)]
    code, text = pip_lauf(aus, [*args, *spezifikation])
    if code != 0:
        raise pip_fehler(text)
    return text


def importtest_lauf(aus):
    r = subprocess.run([sys.executable, str(HIER / "starter.py"), "--importtest"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=umgebung(), cwd=str(HIER), timeout=300, **ohne_fenster())
    aus.protokoll("importtest: " + (r.stdout.strip() or r.stderr.strip())[-3000:])
    try:
        return json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {"fehler": {"python": (r.stderr or r.stdout)[-500:] or f"Exit {r.returncode}"}, "blockiert": []}


def importtest():
    """Läuft als eigener Prozess: lädt alle Pakete wirklich (inkl. ihrer DLLs) und meldet das Ergebnis als JSON.
    Unter Windows wird bei Fehlern jede DLL einzeln geladen, um Sperren (Smart App Control, Richtlinie,
    Virenschutz) sprachunabhängig am Fehlercode zu erkennen."""
    import importlib
    import importlib.metadata as md
    erg = {"fehler": {}, "blockiert": [], "versionen": {}}
    for modul, verteilung in {**PFLICHT, **WAHL}.items():
        try:
            m = importlib.import_module(modul)
            if modul == "PIL":
                from PIL import Image
                Image.new("RGB", (8, 8), "white").resize((16, 16), Image.Resampling.LANCZOS).convert("L")
            elif modul == "numpy":
                float(m.ones((4, 4)).dot(m.ones(4)).sum())
            elif modul == "reportlab":
                importlib.import_module("reportlab.pdfgen.canvas")
            erg["versionen"][verteilung] = md.version(verteilung)
        except BaseException as e:  # noqa: BLE001 – auch SystemExit/DLL-Fehler sauber melden
            erg["fehler"][modul] = f"{type(e).__name__}: {e}"[:600]
    if WIN and erg["fehler"]:
        erg["blockiert"] = finde_gesperrte(list(erg["fehler"]))
    print(json.dumps(erg, ensure_ascii=False))
    return 0


def finde_gesperrte(module):
    import ctypes
    import importlib.util
    gefunden = []
    for modul in module:
        try:
            spec = importlib.util.find_spec(modul)
        except (ImportError, ValueError):
            spec = None
        if not spec or not spec.submodule_search_locations:
            continue
        orte = [Path(p) for p in spec.submodule_search_locations]
        for ort in list(orte):
            for nachbar in ort.parent.glob(f"{ort.name}*.libs"):
                orte.append(nachbar)
        for ort in orte:
            try:
                os.add_dll_directory(str(ort))
            except (OSError, AttributeError):
                pass
        dateien = [p for ort in orte for p in ort.rglob("*") if p.suffix.lower() in (".pyd", ".dll")][:400]
        for p in dateien:
            try:
                ctypes.WinDLL(str(p))
            except OSError as e:
                code = getattr(e, "winerror", None)
                if code in SPERR_CODES:
                    gefunden.append({"modul": modul, "datei": p.name, "code": code, "art": SPERR_CODES[code]})
                    break
    return gefunden


def sperr_art(erg):
    if erg.get("blockiert"):
        return erg["blockiert"][0]["art"], erg["blockiert"][0]["datei"]
    text = " ".join(erg.get("fehler", {}).values()).lower()
    if any(w in text for w in SPERR_WORTE):
        return "sac", next(iter(erg["fehler"]))
    return None, None


def nur_wahl_fehlt(erg):
    return bool(erg.get("fehler")) and all(m in WAHL for m in erg["fehler"])


def entferne_wahlpakete(aus):
    pip_lauf(aus, ["uninstall", "-y", *WAHL.values()], anzeigen=False)
    aus.unter(T("pdfium_aus"))


def pakete_einrichten(aus, grund, nr, gesamt):
    aus.schritt(nr, gesamt, T("s_pakete"))
    erg = importtest_lauf(aus)
    alles_da = not erg.get("fehler")
    if alles_da and grund not in ("reparatur", "pakete", "python"):
        aus.unter(T("schon_da"))
    elif alles_da and not eigenes_python():
        aus.unter(T("schon_da"))                       # fremdes Python mit allen Paketen: nichts anfassen
    else:
        if not eigenes_python():
            aus.unter(T("w_fremd", exe=sys.executable))
        extra = ["--force-reinstall"] if grund == "reparatur" and not alles_da else []
        vorher = (lies_json(STEMPEL) or {}).get("satz")
        text = installiere(aus, paket_spezifikation(vorher if WIN else None), extra)   # früher nötiger Ersatz-Satz bleibt
        if "Successfully installed" not in text:
            aus.unter(T("schon_da"))
    aus.schritt(nr + 1, gesamt, T("s_test"))
    erg = importtest_lauf(aus)
    satz = "standard"
    if erg.get("fehler") and not nur_wahl_fehlt(erg):
        art, datei = sperr_art(erg)
        if art == "sac" and WIN:
            for satz, _lock in ERSATZ_SAETZE:
                aus.unter(T("ersatz", datei=datei, satz=satz))
                betroffen = sorted({PFLICHT.get(b["modul"], WAHL.get(b["modul"], "")) for b in erg["blockiert"]} - {""})
                if betroffen:
                    pip_lauf(aus, ["uninstall", "-y", *betroffen], anzeigen=False)
                installiere(aus, paket_spezifikation(satz))
                erg = importtest_lauf(aus)
                if not erg.get("fehler") or nur_wahl_fehlt(erg):
                    break
                art, datei = sperr_art(erg) if sperr_art(erg)[0] else (art, datei)
            else:
                raise Abbruch(T("f_sac", datei=datei))
        elif art == "richtlinie":
            raise Abbruch(T("f_richtlinie", datei=datei))
        elif art == "virus":
            raise Abbruch(T("f_virus", datei=datei))
        elif not eigenes_python():
            raise Abbruch(T("f_fremd", exe=sys.executable, start=STARTDATEI))
        else:                                           # beschädigt o. Ä.: einmal vollständig neu installieren
            installiere(aus, paket_spezifikation(), ["--force-reinstall"])
            erg = importtest_lauf(aus)
    if erg.get("fehler") and not nur_wahl_fehlt(erg):
        details = "\n".join(f"• {m}: {f}" for m, f in erg["fehler"].items())
        raise Abbruch(T("f_import", details=details[-1200:], log=aus_log()))
    if nur_wahl_fehlt(erg):
        if WIN and sperr_art(erg)[0]:
            entferne_wahlpakete(aus)
        else:
            aus.protokoll("optionales Paket fehlt: " + json.dumps(erg["fehler"], ensure_ascii=False))
    v = erg.get("versionen", {})
    aus.unter("✓ " + ", ".join(f"{k} {v[k]}" for k in sorted(v)))
    return satz


def tools_im_vorrat():
    """Real-ESRGAN-Modelle, die eine frühere Einrichtung als Kopie im Datenordner hinterlegt hat und die dem
    Programmordner noch fehlen (Update auf einen neuen Ordner)."""
    return [m for m in VORRAT_MODELLE if not (HIER / "modelle" / f"{m}.npz").is_file()
            and (DATEN / "modelle" / f"{m}.npz").is_file() and (DATEN / "modelle" / f"{m}.npz").stat().st_size > 1_000_000]


def tools_uebernehmen(aus, nr, gesamt):
    """Ab Version 2.0 lädt das Startprogramm keine Tools mehr – sie werden in der Oberfläche gewählt (Erstabfrage bzw.
    beim ersten Gebrauch). War die Bildverbesserung schon installiert, wird sie aus dem Datenordner übernommen (kein
    Download). Ohne Kopie entfällt der Schritt still."""
    offen = tools_im_vorrat()
    if not offen:
        return False
    aus.schritt(nr, gesamt, T("s_modell"))
    for m in offen:
        ziel, vorrat = HIER / "modelle" / f"{m}.npz", DATEN / "modelle" / f"{m}.npz"
        try:
            ziel.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(vorrat, ziel.with_name(ziel.name + ".tmp"))
            os.replace(ziel.with_name(ziel.name + ".tmp"), ziel)
        except OSError as e:
            aus.protokoll(f"Modell aus dem Vorrat nicht kopierbar: {e}")
    aus.unter(T("aus_vorrat"))
    return True


def entferne_markierungen(aus):
    """Entfernt die Download-Markierung (Windows: „Mark of the Web“, Mac: Quarantäne) von den eigenen Dateien –
    sonst blockieren Smart App Control bzw. Gatekeeper die Startdatei beim nächsten Doppelklick erneut."""
    eigene = [WURZEL / n for n in (START_WIN, START_MAC, START_LINUX, ANLEITUNG) if (WURZEL / n).exists()]
    if WIN:
        zahl = 0
        for p in [*eigene, *HIER.rglob("*")]:
            try:
                os.remove(f"{p}:Zone.Identifier")
                zahl += 1
            except OSError:
                pass
        aus.protokoll(f"Download-Markierung entfernt: {zahl} Dateien")
    elif MAC and shutil.which("xattr"):
        for p in [*eigene, HIER]:
            subprocess.run(["xattr", "-dr", "com.apple.quarantine", str(p)], capture_output=True)
    for name in (() if WIN else (START_MAC, START_LINUX)):
        if (WURZEL / name).exists():
            try:
                os.chmod(WURZEL / name, 0o755)
            except OSError:
                pass


STARTE_PY = r'''# -*- coding: utf-8 -*-
# Me Goos-ta Deutsch – Startverknüpfung. Wird vom Startprogramm angelegt; das Desktop-Symbol (Windows), die App im
# Ordner „Programme“ (Mac) bzw. der Menüeintrag (Linux) rufen diese Datei auf. Sie startet das Programm in dem Ordner,
# der zuletzt über seine Startdatei gestartet wurde (steht in programm-ort.txt).
import os, subprocess, sys
from pathlib import Path
DATEN = Path(__file__).resolve().parent
os.environ["MGD_DATEN"] = str(DATEN)
try:
    ort = Path((DATEN / "programm-ort.txt").read_text(encoding="utf-8").strip())
except OSError:
    ort = Path("?")
if (ort / "starter.py").is_file():
    sys.argv = [str(ort / "starter.py"), *sys.argv[1:]]
    sys.path.insert(0, str(ort))
    import runpy
    runpy.run_path(str(ort / "starter.py"), run_name="__main__")
else:
    TEXT = {"de": ("Me Goos-ta Deutsch", "Der Programmordner wurde verschoben oder gelöscht:\n{0}\n\nBitte im neuen "
                   "Ordner einmal die Startdatei doppelklicken – danach funktioniert das Symbol wieder."),
            "en": ("Me Goos-ta Deutsch", "The program folder was moved or deleted:\n{0}\n\nPlease double-click the "
                   "start file in the new folder once – then the icon works again."),
            "es": ("Me Goos-ta Deutsch", "La carpeta del programa se movió o se borró:\n{0}\n\nHaz doble clic una vez "
                   "en el archivo de inicio de la carpeta nueva; después el icono vuelve a funcionar.")}
    titel, text = TEXT.get("__SPRACHE__", TEXT["en"])
    text = text.format(ort)
    try:
        if os.name == "nt":
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, text, titel, 0x10 | 0x10000 | 0x40000)
        elif sys.platform == "darwin":
            subprocess.run(["osascript", "-e", "on run argv", "-e", "display alert (item 1 of argv) message (item 2 of argv) as critical",
                            "-e", "end run", titel, text])
        else:
            subprocess.run(["zenity", "--error", "--title", titel, "--text", text])
    except Exception:
        print(text)
'''


def startskript_text():
    """starte.py mit der Sprache der Einrichtung (vor der ersten Wahl im Programm Englisch)."""
    return STARTE_PY.replace("__SPRACHE__", SPRACHE if SPRACHE in TEXTE else "en")


def schreibe_startskript():
    ziel = DATEN / "starte.py"
    text = startskript_text()
    if not ziel.exists() or ziel.read_text(encoding="utf-8") != text:
        ziel.write_text(text, encoding="utf-8")
    for name in ("me-goosta-symbol.ico", "me-goosta-symbol.png", "me-goosta-symbol.icns"):
        quelle = HIER / "assets" / name
        if quelle.exists():
            try:
                shutil.copyfile(quelle, DATEN / name)
            except OSError:
                pass
    merke_ort()
    return ziel


def _win_ordner(guid):
    import ctypes
    from ctypes import wintypes

    class GUID(ctypes.Structure):
        _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD), ("Data3", wintypes.WORD),
                    ("Data4", ctypes.c_ubyte * 8)]

    g = GUID()
    ctypes.OleDLL("ole32").CLSIDFromString(ctypes.c_wchar_p(guid), ctypes.byref(g))
    pfad = ctypes.c_wchar_p()
    if ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(g), 0, None, ctypes.byref(pfad)) != 0:
        raise OSError("SHGetKnownFolderPath")
    try:
        return Path(pfad.value)
    finally:
        ctypes.windll.ole32.CoTaskMemFree(pfad)


def win_verknuepfung(ziel, exe, argumente, ordner, symbol, beschreibung):
    """Legt eine .lnk-Datei über die Windows-Shell an (COM über ctypes, ohne Zusatzpakete)."""
    import ctypes
    from ctypes import wintypes
    ole32 = ctypes.OleDLL("ole32")
    try:
        ole32.CoInitialize(None)
    except OSError:
        pass

    class GUID(ctypes.Structure):
        _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD), ("Data3", wintypes.WORD),
                    ("Data4", ctypes.c_ubyte * 8)]

        def __init__(self, text):
            super().__init__()
            ole32.CLSIDFromString(ctypes.c_wchar_p(text), ctypes.byref(self))

    def methode(zeiger, index, *argtypen):
        tabelle = ctypes.cast(zeiger, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
        funktion = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, *argtypen)(tabelle[index])
        return lambda *a: funktion(zeiger, *a)

    link = ctypes.c_void_p()
    ole32.CoCreateInstance(ctypes.byref(GUID("{00021401-0000-0000-C000-000000000046}")), None, 1,
                           ctypes.byref(GUID("{000214F9-0000-0000-C000-000000000046}")), ctypes.byref(link))
    datei = ctypes.c_void_p()
    try:
        methode(link, 20, wintypes.LPCWSTR)(str(exe))                                 # SetPath
        methode(link, 11, wintypes.LPCWSTR)(argumente)                                # SetArguments
        methode(link, 9, wintypes.LPCWSTR)(str(ordner))                               # SetWorkingDirectory
        methode(link, 17, wintypes.LPCWSTR, ctypes.c_int)(str(symbol), 0)             # SetIconLocation
        methode(link, 7, wintypes.LPCWSTR)(beschreibung)                              # SetDescription
        methode(link, 0, ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p))(
            ctypes.byref(GUID("{0000010b-0000-0000-C000-000000000046}")), ctypes.byref(datei))  # → IPersistFile
        Path(ziel).parent.mkdir(parents=True, exist_ok=True)
        methode(datei, 6, wintypes.LPCWSTR, wintypes.BOOL)(str(ziel), True)           # Save
    finally:
        for z in (datei, link):
            if z.value:
                try:
                    methode(z, 2)()                                                     # Release
                except OSError:
                    pass
    return Path(ziel)


WIN_DESKTOP = "{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}"
WIN_PROGRAMME = "{A77F5D77-2E2B-44C3-A6A2-ABA601054A51}"
MAC_APP = Path.home() / "Applications" / "Me Goos-ta Deutsch.app"
LINUX_DESKTOP = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "applications" / \
    "me-goos-ta-deutsch.desktop"


def verknuepfungen_ziele():
    if WIN:
        ziele = []
        for guid in (WIN_DESKTOP, WIN_PROGRAMME):
            try:
                ziele.append(_win_ordner(guid) / "Me Goos-ta Deutsch.lnk")
            except OSError:
                pass
        return ziele
    return [MAC_APP] if MAC else [LINUX_DESKTOP]


def symbole_anlegen(aus, nr, gesamt):
    aus.schritt(nr, gesamt, T("s_symbole_win") if WIN else T("s_symbole_mac") if MAC else T("s_symbole_linux"))
    entferne_markierungen(aus)
    try:
        skript = schreibe_startskript()
    except OSError as e:
        aus.unter(T("w_symbol", grund=e, start=STARTDATEI))
        return False
    ok = True
    if WIN:
        exe = python_ohne_konsole()
        for ziel in verknuepfungen_ziele():
            try:
                win_verknuepfung(ziel, exe, f'"{skript}"', DATEN, DATEN / "me-goosta-symbol.ico",
                                 "Me Goos-ta Deutsch – Lernkarten / flashcards / tarjetas")
                aus.unter(f"✓ {ziel}")
            except OSError as e:
                ok = False
                aus.unter(T("w_symbol", grund=e, start=STARTDATEI))
    elif MAC:
        try:
            mac_app(skript)
            aus.unter(f"✓ {MAC_APP}")
        except OSError as e:
            ok = False
            aus.unter(T("w_symbol", grund=e, start=STARTDATEI))
    else:
        try:
            linux_eintrag(skript)
            aus.unter(f"✓ {LINUX_DESKTOP}")
        except OSError as e:
            ok = False
            aus.unter(T("w_symbol", grund=e, start=STARTDATEI))
    return ok


def desktop_argument(text):
    """Ein Argument für Exec= einer .desktop-Datei (Desktop Entry Specification): in Anführungszeichen, \\ " ` $
    maskiert, % verdoppelt – danach verdoppelt die Regel für Zeichenketten jeden Backslash noch einmal."""
    t = re.sub(r'([\\"`$])', r"\\\1", str(text)).replace("%", "%%")
    return '"' + t.replace("\\", "\\\\") + '"'


def linux_eintrag(skript):
    """Eintrag im Anwendungsmenü (~/.local/share/applications) – GNOME, KDE, Xfce & Co. lesen ihn von selbst."""
    LINUX_DESKTOP.parent.mkdir(parents=True, exist_ok=True)
    symbol = str(DATEN / "me-goosta-symbol.png").replace("\\", "\\\\")
    LINUX_DESKTOP.write_text(
        "[Desktop Entry]\nType=Application\nName=Me Goos-ta Deutsch\n"
        "GenericName=Flashcards\nGenericName[de]=Lernkarten\nGenericName[es]=Tarjetas de estudio\n"
        "Comment=Printable flashcards with goose puns\nComment[de]=Lernkarten zum Ausdrucken – mit Gänse-Wortspielen\n"
        "Comment[es]=Tarjetas para imprimir con juegos de palabras de gansos\n"
        f"Exec={desktop_argument(sys.executable)} {desktop_argument(skript)} --app\nIcon={symbol}\n"
        "Terminal=false\nStartupNotify=false\nCategories=Education;Languages;\n"
        "Keywords=flashcards;Lernkarten;tarjetas;German;Deutsch;Spanish;Español;\n", encoding="utf-8")
    os.chmod(LINUX_DESKTOP, 0o755)
    hilfe = shutil.which("update-desktop-database")             # manche Menüs merken neue Einträge erst danach
    if hilfe:
        try:
            subprocess.run([hilfe, str(LINUX_DESKTOP.parent)], capture_output=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            pass


MAC_INFO = {"CFBundleName": PRODUKT, "CFBundleDisplayName": PRODUKT, "CFBundleIdentifier": "de.me-goos-ta-deutsch.app",
            "CFBundleVersion": "2.4", "CFBundleShortVersionString": "2.4", "NSHighResolutionCapable": True,
            "LSUIElement": True}


def mac_app(skript):
    """Kleine App in ~/Applications (Launchpad, Spotlight, Dock). Lokal angelegt → keine Gatekeeper-Rückfrage.
    Am liebsten als AppleScript-Applet (osacompile gehört zu macOS): dessen Startdatei ist ein echtes Programm für
    Intel- und Apple-Chips. Eine App, die nur aus einem Shell-Skript besteht, hält macOS auf Apple-Chips für eine
    Intel-App und bietet an, „Rosetta“ zu installieren – sie bleibt deshalb nur der Rückfall."""
    aufruf = f"{shlex.quote(sys.executable)} {shlex.quote(str(skript))} --app"
    if MAC_APP.exists():
        shutil.rmtree(MAC_APP)
    MAC_APP.parent.mkdir(parents=True, exist_ok=True)
    if not mac_applet(aufruf):
        mac_skript_app(aufruf)
    subprocess.run(["xattr", "-dr", "com.apple.quarantine", str(MAC_APP)], capture_output=True)
    lsregister = ("/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/"
                  "lsregister")
    if os.path.exists(lsregister):
        subprocess.run([lsregister, "-f", str(MAC_APP)], capture_output=True)
    os.utime(MAC_APP, None)


def mac_applet(aufruf) -> bool:
    """App über osacompile: ein Applet, das das Programm im Hintergrund startet und sich gleich wieder beendet.
    Danach Name, Kennung und Symbol eintragen und neu (ad hoc) signieren. False = nicht möglich → Rückfall."""
    import plistlib
    if not shutil.which("osacompile"):
        return False
    # ohne Ausgabe und im Hintergrund – sonst wartet „do shell script“, bis das Programm endet
    text = f"export PYTHONNOUSERSITE=1; unset PYTHONHOME PYTHONPATH; {aufruf} >/dev/null 2>&1 &"
    quelle = 'do shell script "' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    inhalt = MAC_APP / "Contents"
    try:
        r = subprocess.run(["osacompile", "-o", str(MAC_APP), "-e", quelle], capture_output=True, timeout=120)
        if r.returncode != 0 or not (inhalt / "Info.plist").is_file() or not any((inhalt / "MacOS").iterdir()):
            raise OSError(r.stderr)
    except (OSError, subprocess.SubprocessError):
        shutil.rmtree(MAC_APP, ignore_errors=True)
        return False
    try:
        with open(inhalt / "Info.plist", "rb") as f:
            info = plistlib.load(f)
        info.update(MAC_INFO)
        info.pop("CFBundleIconName", None)                     # sonst nimmt macOS das Skript-Symbol aus Assets.car
        info["CFBundleIconFile"] = "applet"
        with open(inhalt / "Info.plist", "wb") as f:
            plistlib.dump(info, f)
        symbol = HIER / "assets" / "me-goosta-symbol.icns"
        if symbol.exists():
            shutil.copyfile(symbol, inhalt / "Resources" / "applet.icns")
            (inhalt / "Resources" / "Assets.car").unlink(missing_ok=True)
    except (OSError, ValueError):
        pass                                                   # das Applet startet auch mit Standardname und -symbol
    if shutil.which("codesign"):                               # Info.plist geändert → Siegel erneuern (ad hoc, lokal)
        try:
            subprocess.run(["codesign", "--force", "--sign", "-", str(MAC_APP)], capture_output=True, timeout=120)
        except (OSError, subprocess.SubprocessError):
            pass
    return True


def mac_skript_app(aufruf):
    """Rückfall ohne osacompile: App aus einem Shell-Skript (wie bis Version 1.5). Auf Apple-Chips soll
    LSArchitecturePriority verhindern, dass macOS nach Rosetta fragt."""
    import platform
    import plistlib
    inhalt = MAC_APP / "Contents"
    (inhalt / "MacOS").mkdir(parents=True, exist_ok=True)
    (inhalt / "Resources").mkdir(parents=True, exist_ok=True)
    info = dict(MAC_INFO, CFBundleExecutable="me-goosta", CFBundleIconFile="AppIcon", CFBundlePackageType="APPL",
                LSMinimumSystemVersion="10.13")
    if platform.machine() == "arm64":
        info["LSArchitecturePriority"] = ["arm64", "x86_64"]
    with open(inhalt / "Info.plist", "wb") as f:
        plistlib.dump(info, f)
    start = inhalt / "MacOS" / "me-goosta"
    start.write_text("#!/bin/sh\n# Me Goos-ta Deutsch – startet das Programm (angelegt vom Startprogramm)\n"
                     f"export PYTHONNOUSERSITE=1\nunset PYTHONHOME PYTHONPATH\nexec {aufruf}\n", encoding="utf-8")
    os.chmod(start, 0o755)
    if (HIER / "assets" / "me-goosta-symbol.icns").exists():
        shutil.copyfile(HIER / "assets" / "me-goosta-symbol.icns", inhalt / "Resources" / "AppIcon.icns")


def einrichten(aus, grund):
    aus.zeile("\n  " + T("einrichtung"))
    aus.zeile("  " + T({"erst": "g_erst", "python": "g_python", "pakete": "g_pakete", "ordner": "g_ordner"}
                       .get(grund, "g_reparatur")))
    if ist_admin() and WIN:
        aus.zeile("  " + T("w_admin"))
    pakete = grund in ("erst", "python", "pakete", "reparatur")
    gesamt = (5 if pakete else 2) + bool(tools_im_vorrat())      # Tools-Schritt nur, wenn etwas zu übernehmen ist
    aus.schritt(1, gesamt, T("s_ort"))
    frei = mb(shutil.disk_usage(DATEN).free)
    if pakete and frei < MIN_FREI_MB:
        raise Abbruch(T("f_platz", frei=frei, noetig=MIN_FREI_MB, ort=DATEN))
    aus.unter(f"✓ {HIER}")
    aus.unter(f"✓ {DATEN}  ({T('frei_mb', mb=frei)})")
    satz = None
    if pakete:
        beende_alle_instanzen(aus, still=True)       # eine laufende Oberfläche hält die DLLs fest → vorher beenden
        aus.schritt(2, gesamt, T("s_pip"))
        bereite_pip(aus)
        satz = pakete_einrichten(aus, grund, 3, gesamt)
    tools_uebernehmen(aus, gesamt - 1, gesamt)
    symbole_anlegen(aus, gesamt, gesamt)
    st = lies_json(STEMPEL) or {}
    st.update(version=VERSION, python=sys.version.split()[0], prefix=sys.prefix, exe=sys.executable,
              pakete=paket_signatur(),
              zeit=time.strftime("%Y-%m-%d %H:%M:%S"))
    if satz:
        st["satz"] = satz
    st["ordner"] = sorted(set(st.get("ordner", [])) | {ordner_schluessel()})[-50:]
    schreibe_json(STEMPEL, st)
    aus.zeile("\n  ✓ " + T("fertig") + "  " +
              (T("kuenftig_win") if WIN else T("kuenftig_mac") if MAC else T("kuenftig_linux")))


# =============================================================================================
# Oberfläche starten, wiederfinden, beenden
# =============================================================================================
def instanz_datei(pfad=HIER):
    return DATEN / f"laeuft-{ordner_schluessel(pfad)}.json"


def ui_version():
    try:
        m = re.search(r'^UI_VERSION = "([^"]+)"', (HIER / "gans_ui.py").read_text(encoding="utf-8"), re.M)
        return m.group(1) if m else ""
    except OSError:
        return ""


def _anfrage(port, methode, weg, kopf=None, koerper=None, zeit=3):
    c = http.client.HTTPConnection("127.0.0.1", int(port), timeout=zeit)
    try:
        c.request(methode, weg, body=koerper, headers=kopf or {})
        r = c.getresponse()
        r.read()
        return r
    finally:
        c.close()


def antwortet(d) -> bool:
    try:
        return _anfrage(d["port"], "GET", "/?k=" + d["schluessel"]).status == 303
    except (OSError, KeyError, ValueError, TypeError, http.client.HTTPException):
        return False


def lies_instanz(pfad=None):
    datei = Path(pfad) if pfad else instanz_datei()
    d = lies_json(datei)
    if d and antwortet(d):
        return d
    if d:
        try:
            datei.unlink()                              # verwaist (z. B. nach Absturz oder Neustart des Rechners)
        except OSError:
            pass
    return None


def beende_instanz(d, warten=8) -> bool:
    """Bittet die Oberfläche höflich um ihr Ende (wie der ⏻-Knopf); hilft das nicht, wird der Prozess beendet."""
    port = int(d["port"])
    try:
        r = _anfrage(port, "GET", "/?k=" + d["schluessel"])
        keks = (r.getheader("Set-Cookie") or "").split(";")[0]
        token = keks.partition("=")[2]
        _anfrage(port, "POST", "/api/beenden", {"Cookie": keks, "X-GL-Token": token, "Content-Type": "application/json",
                                                 "Origin": f"http://127.0.0.1:{port}"}, b"{}")
    except (OSError, ValueError, http.client.HTTPException):
        pass
    ende = time.time() + warten
    while time.time() < ende:
        if not antwortet(d):
            return True
        time.sleep(0.25)
    try:
        if WIN:
            subprocess.run(["taskkill", "/PID", str(int(d["pid"])), "/T", "/F"], capture_output=True, **ohne_fenster())
        else:
            os.kill(int(d["pid"]), 15)
    except (OSError, ValueError, KeyError):
        pass
    time.sleep(1)
    return not antwortet(d)


def beende_alle_instanzen(aus, still=False):
    zahl = 0
    for datei in sorted(DATEN.glob("laeuft-*.json")):
        d = lies_instanz(datei)
        if d:
            beende_instanz(d)
            zahl += 1
    if not still:
        aus.zeile("  " + (T("beendet") if zahl else T("nichts_laeuft")))
    return zahl


def oeffne_browser(adresse) -> bool:
    try:
        if WIN and ist_admin():                         # nicht als Administrator surfen: Explorer öffnet normal
            subprocess.Popen(["explorer.exe", adresse])
            return True
        if oeffne_nach_wahl(adresse):                   # gewählter Browser oder eigenes Fenster (Werkzeuge)
            return True
        return bool(webbrowser.open(adresse, new=2))
    except Exception:  # noqa: BLE001
        return False


# =============================================================================================
# Programmstart: Browser oder eigenes Fenster (Wahl in der Oberfläche → DATEN/start.json)
# =============================================================================================
START_WAHL = DATEN / "start.json"
# (id, Name, eigenes Fenster möglich (Chromium: --app), Kandidaten je System)
BROWSER = [
    ("edge", "Microsoft Edge", True,
     dict(win=[r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe", r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"],
          mac=["/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"], linux=["microsoft-edge", "microsoft-edge-stable"])),
    ("chrome", "Google Chrome", True,
     dict(win=[r"%ProgramFiles%\Google\Chrome\Application\chrome.exe", r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe",
               r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"],
          mac=["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"], linux=["google-chrome", "google-chrome-stable"])),
    ("brave", "Brave", True,
     dict(win=[r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe",
               r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"],
          mac=["/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"], linux=["brave-browser"])),
    ("chromium", "Chromium", True, dict(win=[], mac=["/Applications/Chromium.app/Contents/MacOS/Chromium"],
                                        linux=["chromium", "chromium-browser"])),
    ("firefox", "Firefox", False,
     dict(win=[r"%ProgramFiles%\Mozilla Firefox\firefox.exe", r"%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe"],
          mac=["/Applications/Firefox.app/Contents/MacOS/firefox"], linux=["firefox"])),
    ("opera", "Opera", False, dict(win=[r"%LOCALAPPDATA%\Programs\Opera\opera.exe"],
                                   mac=["/Applications/Opera.app/Contents/MacOS/Opera"], linux=["opera"])),
    ("safari", "Safari", False, dict(win=[], mac=["/Applications/Safari.app/Contents/MacOS/Safari"], linux=[])),
]


def finde_browser():
    """Installierte Browser → [dict(id, name, pfad, fenster)] (nur bekannte Programme an festen Orten)."""
    system = "win" if WIN else "mac" if MAC else "linux"
    gefunden = []
    for bid, name, fenster, orte in BROWSER:
        kandidaten = orte[system]
        if MAC:                                         # auch nur für dieses Benutzerkonto installiert (~/Applications)
            kandidaten = [*kandidaten, *(str(Path.home()) + o for o in kandidaten)]
        for ort in kandidaten:
            pfad = os.path.expandvars(ort) if WIN else (ort if os.path.isabs(ort) else shutil.which(ort))
            if pfad and "%" not in pfad and Path(pfad).is_file():
                gefunden.append(dict(id=bid, name=name, pfad=str(pfad), fenster=fenster))
                break
    return gefunden


def lies_start_wahl():
    """{art: browser|fenster, browser: standard|<id>} oder None (noch nicht gewählt)."""
    d = lies_json(START_WAHL)
    if not d or d.get("art") not in ("browser", "fenster"):
        return None
    return dict(art=d["art"], browser=str(d.get("browser") or "standard"), willkommen=d.get("willkommen") is True)


def schreibe_start_wahl(wahl):
    DATEN.mkdir(parents=True, exist_ok=True)
    schreibe_json(START_WAHL, dict(art=wahl.get("art", "browser"), browser=wahl.get("browser", "standard"),
                                   willkommen=wahl.get("willkommen") is True, zeit=time.strftime("%Y-%m-%d %H:%M:%S")))


def oeffne_nach_wahl(adresse) -> bool:
    """Öffnet nach der gespeicherten Wahl. False = nichts gewählt bzw. nicht möglich (→ Standard-Browser)."""
    wahl = lies_start_wahl()
    if not wahl or (wahl["art"] == "browser" and wahl["browser"] == "standard"):
        return False
    liste = finde_browser()
    if wahl["art"] == "fenster":
        kandidaten = [b for b in liste if b["fenster"]]
        bevorzugt = [b for b in kandidaten if b["id"] == wahl["browser"]]
        b = (bevorzugt or kandidaten or [None])[0]
        if not b:
            return False
        befehl = [b["pfad"], f"--app={adresse}", "--window-size=1320,900", "--new-window"]
    else:
        b = next((x for x in liste if x["id"] == wahl["browser"]), None)
        if not b:
            return False
        befehl = [b["pfad"], adresse]
        if MAC:
            befehl = ["open", "-a", str(Path(b["pfad"]).parents[2]), adresse]
    kw = dict(stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
    if WIN:
        subprocess.Popen(befehl, creationflags=0x00000200 | 0x00000008, **kw)    # neue Gruppe, vom Fenster gelöst
    else:
        subprocess.Popen(befehl, start_new_session=True, **kw)
    return True


def starte_server(aus, start_id):
    log_pfad = DATEN / "oberflaeche.txt"
    try:
        if log_pfad.exists() and log_pfad.stat().st_size > 2_000_000:
            log_pfad.replace(DATEN / "oberflaeche.alt.txt")
    except OSError:
        pass
    log = open(log_pfad, "a", encoding="utf-8")
    log.write(f"\n===== {time.strftime('%Y-%m-%d %H:%M:%S')} · {PRODUKT} {VERSION} · {HIER} =====\n")
    log.flush()
    befehl = [python_ohne_konsole(), "-u", str(HIER / "gans_ui.py"), "--kein-browser",
              "--instanz-datei", str(instanz_datei())]
    kw = dict(stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, cwd=str(HIER),
              env=umgebung(MGD_START_ID=start_id))
    aus.protokoll("$ " + " ".join(befehl))
    if WIN:
        flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x200)
        if befehl[0].lower().endswith("python.exe"):
            flags |= getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        try:                                            # vom Startfenster lösen, damit es sich schließen darf
            proc = subprocess.Popen(befehl, creationflags=flags | 0x01000000, **kw)   # CREATE_BREAKAWAY_FROM_JOB
        except OSError:
            proc = subprocess.Popen(befehl, creationflags=flags, **kw)
    else:
        proc = subprocess.Popen(befehl, start_new_session=True, **kw)
    log.close()
    return proc, log_pfad


def log_ende(pfad, zeilen=12):
    try:
        text = Path(pfad).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    teil = text.rsplit("=====", 1)[-1].strip().splitlines()
    return "\n".join(teil[-zeilen:])


def zeige_adresse(aus, adresse, browser=True, immer=False):
    """Öffnet den Browser. Klappt das nicht (oder direkt nach der Einrichtung), steht die Adresse zum Abtippen da –
    ohne Konsole (Desktop-Symbol) in einem Hinweisfenster."""
    geoeffnet = browser and oeffne_browser(adresse)
    if geoeffnet:
        aus.zeile("  " + T("oeffne"))
    if not browser or not geoeffnet or immer:
        aus.zeile("  " + T("adresse") + "\n    " + adresse)
        if browser and not geoeffnet and not aus.konsole:
            dialog(PRODUKT, T("adresse") + "\n\n" + adresse, fehler=False)


def starte_oberflaeche(aus, browser=True, nach_einrichtung=False, versuch=1):
    d = lies_instanz()
    if d and d.get("version") != ui_version():
        aus.zeile("  " + T("alte_version"))
        beende_instanz(d)
        d = None
    if d:
        aus.zeile("\n  " + T("laeuft_schon"))
        zeige_adresse(aus, d["adresse"], browser)
        if aus.konsole and not WIN:
            aus.zeile("\n  " + T("fenster_zu"))
        return 0
    aus.zeile("\n  " + T("starte"))
    start_id = secrets.token_hex(8)
    proc, log_pfad = starte_server(aus, start_id)
    ende, gemeldet = time.time() + 90, False
    with aus.lade(T("starte_lade")):
        while True:
            d = lies_json(instanz_datei())
            if d and d.get("start_id") == start_id and antwortet(d):
                break
            if proc.poll() is not None:
                ganz = log_ende(log_pfad, zeilen=400)
                aus.protokoll("Oberfläche beendet sich sofort:\n" + ganz)
                if versuch == 1 and re.search(r"ImportError|ModuleNotFoundError|No module named|DLL load failed|"
                                              r"\[WinError (4551|1260|225|126|193)\]", ganz):
                    einrichten(aus, "reparatur")
                    return starte_oberflaeche(aus, browser, True, versuch=2)
                raise Abbruch(T("f_server", text=log_ende(log_pfad)[-1500:] or "–", log=log_pfad))
            if time.time() > ende:
                raise Abbruch(T("f_server_zeit", log=log_pfad))
            if not gemeldet and time.time() > ende - 80:
                aus.zeile("  " + T("warte_start"))
                gemeldet = True
            time.sleep(0.2)
    zeige_adresse(aus, d["adresse"], browser, immer=nach_einrichtung)
    if nach_einrichtung and aus.konsole and WIN:
        aus.zeile("\n  " + T("schliesst"))
        time.sleep(8)
    if aus.konsole and not WIN:
        aus.zeile("\n  " + T("fenster_zu"))
    return 0


# =============================================================================================
# Weitere Schalter: Status, Entfernen, Neustart in einer Konsole
# =============================================================================================
def zeige_status(aus):
    st = lies_json(STEMPEL) or {}
    d = lies_instanz()
    w = {"de": ("Programmordner", "Laufzeit/Daten", "eigenes", "Eingerichtet", "Paketsatz", "nötig",
                "Bildverbesserung (Tool)", "Oberfläche"),
         "en": ("Program folder", "Runtime/data", "own", "Set up", "Package set", "needed",
                "Image enhancement (tool)", "Interface"),
         "es": ("Carpeta del programa", "Entorno/datos", "propio", "Configurado", "Paquetes", "necesario",
                "Mejora de imagen (herramienta)", "Interfaz")}
    w = w.get(SPRACHE, w["en"])                       # wie alle Texte vor der Installation: Englisch, bis gewählt
    zeilen = [f"{PRODUKT} {VERSION}", f"{w[0]}: {HIER}", f"{w[1]}: {DATEN}",
              f"Python: {sys.version.split()[0]} ({sys.executable}) – {w[2]}: {eigenes_python()}",
              f"{w[3]}: {st.get('zeit', '–')} · {w[4]}: {st.get('satz', '–')} · {w[5]}: {brauche_einrichtung()}",
              f"{w[6]}: {any((HIER / 'modelle' / f'{m}.npz').is_file() for m in VORRAT_MODELLE)}",
              f"{w[7]}: {d['adresse'] if d else '–'}"]
    for z in zeilen:
        print(z)
    return 0


def entfernen(aus):
    beende_alle_instanzen(aus, still=True)
    for ziel in verknuepfungen_ziele():
        try:
            if ziel.is_dir():
                shutil.rmtree(ziel)
            elif ziel.exists():
                ziel.unlink()
            else:
                continue
            aus.zeile("  " + T("entfernt", was=ziel))
        except OSError as e:
            aus.zeile(f"  ! {ziel}: {e}")
    aus.log = None
    if WIN:                                           # das laufende python.exe liegt im Ordner → kurz danach löschen
        subprocess.Popen(f'cmd.exe /c "ping -n 4 127.0.0.1 >nul & rd /s /q "{DATEN}""',
                         **ohne_fenster(), close_fds=True)
    else:
        shutil.rmtree(DATEN, ignore_errors=True)
    aus.zeile("  " + T("entfernt", was=DATEN))
    aus.zeile("\n  " + T("entfernen_fertig"))
    return 0


# Ordner, die nie als Programmordner gelöscht werden (wurde die ZIP-Datei direkt hinein entpackt): englisch, deutsch,
# spanisch – unter Linux heißen sie auf der Platte so –, dazu die echten Orte aus dem System (Windows: bekannte
# Ordner, auch wenn OneDrive sie verschoben hat; Linux: ~/.config/user-dirs.dirs).
GESCHUETZT = ("Downloads", "Desktop", "Documents", "Dokumente", "Schreibtisch", "Pictures", "Bilder", "Music", "Musik",
              "Videos", "Movies", "Filme", "Public", "Öffentlich", "Templates", "Vorlagen", "Descargas", "Escritorio",
              "Documentos", "Imágenes", "Música", "Vídeos", "Público", "Plantillas", "Applications", "Library",
              "OneDrive")
WIN_GESCHUETZT = (WIN_DESKTOP, "{FDD39AD0-238F-46AF-ADB4-6C85480369C7}", "{374DE290-123F-4565-9164-39C4925E467B}",
                  "{33E28130-4E1E-4676-835A-98395C3BC3BB}", "{4BD8D571-6D19-48D3-BE97-422220080E43}",
                  "{18989B1D-99B5-455B-841C-AB7C74E4DDFC}")      # Desktop, Dokumente, Downloads, Bilder, Musik, Videos


def system_ordner():
    """Die echten Orte von Desktop, Dokumenten, Downloads & Co. dieses Benutzers."""
    ordner = set()
    if WIN:
        for guid in WIN_GESCHUETZT:
            try:
                ordner.add(_win_ordner(guid))
            except Exception:  # noqa: BLE001
                pass
        return ordner
    heim = Path.home()
    try:
        text = (Path(os.environ.get("XDG_CONFIG_HOME") or heim / ".config") / "user-dirs.dirs").read_text(encoding="utf-8")
    except OSError:
        return ordner
    for zeile in text.splitlines():                  # z. B. XDG_DOWNLOAD_DIR="$HOME/Descargas"
        m = re.match(r'\s*XDG_\w+_DIR\s*=\s*"(.+)"\s*$', zeile)
        if m:
            ordner.add(Path(m.group(1).replace("$HOME", str(heim))))
    return ordner


def deinstallation_erlaubt() -> bool:
    """Nur einen Ordner löschen, der eindeutig das Programm ist: Startdatei + Programm/starter.py, nicht der
    Benutzer-, Download- oder Laufwerksordner."""
    try:
        w = WURZEL.resolve()
        heim = Path.home().resolve()
        verboten = ({heim, heim.parent, Path(w.anchor)} | {heim / n for n in GESCHUETZT}
                    | {p.resolve() for p in system_ordner()})
        return (HIER.name == "Programm" and (HIER / "starter.py").is_file() and (HIER / "gans_ui.py").is_file()
                and any((w / n).is_file() for n in (START_WIN, START_MAC, START_LINUX))
                and w not in verboten and len(w.parts) >= 3 and DATEN.resolve() != w)
    except OSError:
        return False


def deinstallieren(aus):
    """Wie --entfernen, zusätzlich wird der Programmordner (mit Karten und Bildern) gelöscht – kurz nach dem Ende
    dieses Prozesses, denn das laufende Python liegt im Datenordner."""
    if not deinstallation_erlaubt():
        aus.problem(T("deinst_ort", ort=WURZEL), titel=T("deinst_titel"))
        return 1
    beende_alle_instanzen(aus, still=True)
    for ziel in verknuepfungen_ziele():
        try:
            if ziel.is_dir():
                shutil.rmtree(ziel)
            elif ziel.exists():
                ziel.unlink()
        except OSError as e:
            aus.zeile(f"  ! {ziel}: {e}")
    text = T("deinst_fertig", daten=DATEN, ort=WURZEL)
    aus.zeile("  " + text)
    if not aus.konsole:
        dialog(T("deinst_titel"), text, fehler=False)
    aus.log = None
    heim = str(Path.home())
    if WIN:                                           # wie bei --entfernen: Befehlszeile als Unicode, nach kurzer Pause
        subprocess.Popen(f'cmd.exe /c "ping -n 4 127.0.0.1 >nul & rd /s /q "{DATEN}" & rd /s /q "{WURZEL}""',
                         cwd=heim, close_fds=True, **ohne_fenster())
    else:
        subprocess.Popen(["/bin/sh", "-c", 'sleep 2; rm -rf -- "$1" "$2"', "sh", str(DATEN), str(WURZEL)],
                         cwd=heim, start_new_session=True, close_fds=True)
    return 0


def neu_in_konsole(argv) -> bool:
    """Start ohne Konsole (Desktop-Symbol), aber es muss eingerichtet werden → sichtbar in einer Konsole weiter."""
    try:
        if WIN:
            subprocess.Popen([python_mit_konsole(), str(HIER / "starter.py"), "--konsole", *argv],
                             creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0x10), cwd=str(HIER),
                             env=umgebung())
            return True
        if MAC and (WURZEL / START_MAC).exists():
            subprocess.Popen(["open", "-a", "Terminal", str(WURZEL / START_MAC)])
            return True
        befehl = linux_terminal([sys.executable, str(HIER / "starter.py"), "--konsole", *argv])
        if befehl:
            subprocess.Popen(befehl, env=umgebung(), start_new_session=True)
            return True
    except OSError:
        pass
    return False


# Linux-Terminals in der Reihenfolge des Vorrangs – und wie jedes einen Befehl mit Argumenten startet:
# "-e"/"-x"/"--" = Schalter vor dem Befehl, "" = Befehl direkt, "-e1" = Befehl als eine Zeichenkette (GNOME Console).
# Gleiche Liste in „Me Goos-ta Deutsch - Linux.sh“.
LINUX_TERMINALS = [("x-terminal-emulator", "-e"), ("gnome-terminal", "--"), ("ptyxis", "--"), ("kgx", "-e1"),
                   ("konsole", "-e"), ("xfce4-terminal", "-x"), ("mate-terminal", "-x"), ("terminator", "-x"),
                   ("alacritty", "-e"), ("kitty", ""), ("xterm", "-e")]


def linux_terminal(befehl):
    """Befehlszeile, die `befehl` in einem neuen Terminalfenster startet – oder None ohne bekanntes Terminal."""
    for name, art in LINUX_TERMINALS:
        pfad = shutil.which(name)
        if pfad:
            if art == "-e1":
                return [pfad, "-e", shlex.join(str(t) for t in befehl)]
            return [pfad, *([art] if art else []), *(str(t) for t in befehl)]
    return None


def quickedit_aus():
    """Windows-Konsole: „QuickEdit“ aus – ein versehentlicher Klick ins Fenster würde die Einrichtung anhalten."""
    if not WIN:
        return
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetConsoleTitleW("Me Goos-ta Deutsch")
        h = k.GetStdHandle(-10)
        modus = ctypes.c_uint32()
        if k.GetConsoleMode(h, ctypes.byref(modus)):
            k.SetConsoleMode(h, (modus.value & ~0x0040) | 0x0080)
    except Exception:  # noqa: BLE001
        pass


def parse(argv):
    ap = argparse.ArgumentParser(description=f"{PRODUKT} – Startprogramm (richtet beim ersten Start alles ein)")
    ap.add_argument("--einrichten", action="store_true", help="alles neu prüfen und reparieren")
    ap.add_argument("--beenden", action="store_true", help="laufende Oberfläche beenden")
    ap.add_argument("--status", action="store_true", help="Zustand anzeigen")
    ap.add_argument("--entfernen", action="store_true", help="eigenes Python, Pakete und Symbole entfernen")
    ap.add_argument("--deinstallieren", action="store_true",
                    help="alles entfernen – auch den Programmordner mit Karten und Bildern (nicht rückgängig zu machen)")
    ap.add_argument("--kein-browser", action="store_true", help="Browser nicht öffnen")
    ap.add_argument("--konsole", action="store_true", help=argparse.SUPPRESS)      # von den Startdateien
    ap.add_argument("--app", action="store_true", help=argparse.SUPPRESS)          # vom Desktop-Symbol / der App
    ap.add_argument("--importtest", action="store_true", help=argparse.SUPPRESS)   # intern
    return ap.parse_args(argv)


def main(argv=None):
    global SPRACHE
    argv = list(sys.argv[1:] if argv is None else argv)
    a = parse(argv)
    if a.importtest:
        return importtest()
    SPRACHE = ermittle_sprache()
    aus = Ausgabe(konsole=(a.konsole or hat_konsole()) and not a.app)
    if aus.konsole:
        quickedit_aus()
        aus.banner()
    try:
        try:
            DATEN.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise Abbruch(T("f_daten", ordner=DATEN, grund=e)) from None
        aus.oeffne_log()
        if a.status:
            return zeige_status(aus)
        if a.beenden:
            beende_alle_instanzen(aus)
            return 0
        if a.entfernen:
            return entfernen(aus)
        if a.deinstallieren:
            return deinstallieren(aus)
        pruefe_ort(aus)
        grund = brauche_einrichtung(a.einrichten)
        if grund and not aus.konsole and neu_in_konsole([x for x in argv if x not in ("--app", "--konsole")]):
            return 0                                   # das Konsolenfenster macht weiter (und merkt sich den Ort)
        st = lies_json(STEMPEL) or {}
        alt = vorheriger_ort() if st and ordner_schluessel() not in st.get("ordner", []) else None
        merke_ort()
        with Sperre(aus):
            grund = brauche_einrichtung(a.einrichten)   # evtl. hat ein anderes Fenster inzwischen eingerichtet
            if grund:
                if alt:
                    biete_uebernahme_an(aus, alt)      # neue Version in neuem Ordner: eigene Karten mitnehmen
                einrichten(aus, grund)
            return starte_oberflaeche(aus, browser=not a.kein_browser, nach_einrichtung=bool(grund))
    except Abbruch as e:
        aus.problem(str(e))
        return 1
    except KeyboardInterrupt:
        return 1
    except Exception as e:  # noqa: BLE001
        aus.protokoll(traceback.format_exc())
        aus.problem(T("f_unerwartet", fehler=f"{type(e).__name__}: {e}", log=aus.log_pfad, start=STARTDATEI))
        return 1


if __name__ == "__main__":
    sys.exit(main())
