# Me Goos-ta Deutsch – Spezifikation

**Version 2.4 · Stand 22.10.2026** · (früher „GANS LERNKARTEN“)

Diese Datei beschreibt verbindlich, **wie die Lernkarten „Me Goos-ta Deutsch“ gebaut sind**. Zusammen mit
`gans_lernkarten.py` (Generator), `ki_modelle.py` (KI-Bildverbesserung), `ki_bild.py` (KI-Bilder), `uebersetzer.py` (Übersetzungsvorschläge), `sprachen.py`
(Sprachen der Rückseite) und `karten.csv` (Kartenliste) ist sie die Rezeptur: Bild + eine CSV-Zeile → druckfertige PDFs. Den Arbeitsablauf beschreibt `LEITFADEN.md`
(Englisch: `LEITFADEN_en.md`, Spanisch: `LEITFADEN_es.md`). Diese Spezifikation gibt es nur auf Deutsch.

Neu in 2.4 (veröffentlicht am 22.10.2026): **Update direkt im Programm** – „🔎 Nach neuer Version suchen“ jetzt auch unter Werkzeuge → „Programm aktuell halten“ und unten im Menü unter der Versionsnummer; ist eine neuere Version da, lädt „⬆️ Jetzt aktualisieren“ das Release (Prüfsumme, ZIP-Prüfung), „🔄 Jetzt neu starten“ ersetzt die Programmdateien im selben Ordner und startet über die Startdatei neu – kein zweiter Ordner, eigene Daten bleiben (Abschnitt 9); **Rückgängig und Wiederholen überall** – ↶ ↷ in der Kopfzeile, Strg+Z/Strg+Y, bis zu 30 Schritte für Karten, Bilder, „Bilder vorbereiten“, Ideen, Import, Wortliste und Gänse-Bild (Abschnitt 9); **jede Karte braucht ihre Gans** – fehlt „Gans“ im deutschen Text, setzt das Speichern sie mit Hinweis an den Anfang (sie darf auch mitten im Text stehen), „Gans ergänzen“ für ältere Karten; **Fehler behoben:** Klicken mit leichtem Ziehen im Vorher/Nachher-Vergleich legte ein neues Bild in „Bilder vorbereiten“ an.
Neu in 2.3 (veröffentlicht am 22.10.2026): **Ideen bekommen ihr Bild leichter** – ein einziger Weg für Fotos und fertige Bilder („🖼️ Bild wählen …“, Klick auf die leere Bildfläche oder Hineinziehen → „GANS-Bild gestalten“ mit Vorschau: „Für diese Idee übernehmen“ mit „GANS + Wort“ oder „Bild unverändert übernehmen“; der doppelte Knopf „GANS-Bild gestalten …“ entfällt), **„🪄 Mit KI erzeugen …“** direkt an der Idee (Tool „KI-Bilder“; Wort + Bildidee vorbelegt, Ergebnis „Ohne Wort für die Idee übernehmen“ bzw. „✍️ Wort aufs Bild setzen …“) und das neue Feld **„Bildidee“** – Merkzettel, wie ein passendes Bild aussehen könnte, zugleich die Beschreibung für die KI (Abschnitt 9.2/9.3).
Neu in 2.2 (veröffentlicht am 21.10.2026): **🔊 Deutsch beim Lernen** – nach dem Aufdecken liest eine lokale Stimme (de-DE → de-AT → de-CH) auch den deutschen Text vor, ebenso auf der Lernseite; **„🔎 Nach neuer Version suchen“** (Hilfe → Über, nur per Klick, nur am Rechner, eine Anfrage an api.github.com, Abschnitt 9); **Wortliste in Ideen** – Datei oder eingefügter Text → Vorschau → bis zu 500 Ideen auf einmal, nie still gekürzt, Rückgängig je Liste (Abschnitt 9.2), dazu „🌐 Alle übersetzen“ für Ideen ohne Wort; **automatische Tests auf allen Systemen** (nur Entwickler) – jede Version läuft vor der Veröffentlichung auf GitHub-Rechnern (Windows x64/ARM, macOS Apple Silicon/Intel, Linux x64/ARM, Debian) und in WebKit, Firefox und Chromium; ein Release gibt es nur für genau den grün geprüften Inhalt, der veröffentlichte Stand wird nach jedem Push auf `main` erneut geprüft (Fix vom 21.10.2026, vorher wöchentlich; derselbe Fix holt eine Handy-App von vor 2.1, die auf der Download-Seite nur ihren Startbildschirm zeigte, von selbst auf die neue Version).
Neu in 2.1 (veröffentlicht am 20.10.2026): **Download für alle Systeme** – ein ZIP für Windows, macOS und Linux als GitHub-Release (mit `SHA256SUMS.txt`), dazu die Download-Seite `…/me-goos-ta-deutsch/download/` (EN · DE · ES, System erkannt, drei Schritte mit Skizzen, Hilfe zu SmartScreen/Gatekeeper); **Englisch vor der Installation** – LIES MICH, Startdateien, Starter-Fenster und erster Start der Handy-App starten Englisch, danach gilt die im Programm gewählte Sprache (nie die System-/Gerätesprache); **neue Gans auf der Rückseite** – Fläche hinter dem Wort einfarbig, die Gans des Programmsymbols schwimmt klein unten rechts im Teich und weicht dem Text aus; Tools-Knopf „Faster ×2“ sauber zweizeilig.
Neu in 2.0 (veröffentlicht am 16.10.2026): **Tools** – Bildverbesserung (Real-ESRGAN), Übersetzung,
KI-Bilder, Sprachen und Karten lernen sind nicht vorinstalliert; Erstabfrage beim ersten Öffnen, Download auf Nachfrage über
die Warteschlange, Deinstallieren gibt den Platz wieder frei (Abschnitt 9.4); **Warteschlange** – höchstens ein
Hintergrundprozess, alles Weitere wartet, einsehbar, umsortierbar, abbrechbar; **Spezifikation in der Hilfe** lädt nie
mehr endlos (Zeitlimit, Abbrechen, Nochmal versuchen); sichtbar nur noch **„Spanisch“** (gemeint ist immer das in Mexiko
gesprochene Spanisch); **Farben & Darstellung** – Schemata und eigene Farben, Standard unverändert; **15 Sprachen der
Rückseite** – jede einzeln ladbar, Kennzeichnung an jeder Karte, mehrere Rückseiten je Karte, Druck und Exporte je
Sprache (Schriften, Formen, rechts nach links); **Karten lernen** – FSRS-6 wie in Anki, Lernstand bleibt, Stapel,
Statistik, Zurücksetzen nach Bearbeiten mit Meldung; **Handy-App** (Web-App/PWA mit demselben Python über Pyodide, untere
App-Navigation, offline) samt Installationsdateien für Android, iPhone und Google Pixel; Fehleranalyse mit eigenem
Prüfabschnitt (E33). Enthalten ist auch die nie einzeln veröffentlichte 1.7-Arbeit: **Bild ändern** im Karten-Editor
(neues Bild für eine vorhandene Karte, geprüft wie Schritt 1, altes Bild aufgehoben, Rückgängig); Gänse-Bild-Bereich in
„Erzeugen“ bricht bei wenig Platz sauber um; **Handy-Feinschliff** (Tippflächen ≥ 44 px, Eingaben 16 px, Nur-am-Rechner-Werkzeuge über das
Handy gesperrt, Kopieren ohne Zwischenablage-Schnittstelle, HEIC-sichere Dateifelder, fester Handy-Port, Fortschritt nach
Verbindungsaussetzern); **KI-Bilder**: realistische Gänse aus Wort + kurzer Beschreibung, offline in reinem NumPy
(Segmind Vega + VegaRT, Apache-2.0; Abschnitt 9.3), in Schritt 1 und im Karten-Editor, Wort danach mit „GANS-Bild
gestalten“ daraufsetzen.
Änderungen in 1.5: **Gänse-Bild der Rückseite per Knopf** laden (geprüft, neu gespeichert ohne Metadaten,
wiederherstellbar); eigener Reiter **„Bildverbesserung“** – Karten auswählen und vorab verbessern, verbesserte Bilder
markiert, Vorher/Nachher-Vergleich (`--nur verbessern`, `--bild`); Reiter **„Tabelle“** – Vorder- und Rückseitentext
nebeneinander zum Prüfen der Übersetzung, mit Häkchen „geprüft“; **automatische Übersetzung** als Vorschlag
(Wiktionary, MyMemory, optional DeepL) nach Zustimmung, mit Schutzmaßnahmen (Abschnitt 9.1, 11); **mehrere Bilder auf
einmal** vorbereiten, gleich beschriften, übersetzen und übernehmen; Schritt 2 mit „Alle übersetzen“/„Alle speichern“;
**Update ohne Datenverlust**: Beispielkarten als `beispiel-karten.csv` und `beispiel-bilder/`, Übernahme der eigenen
Karten aus dem bisherigen Ordner (Abschnitt 10).
Erweiterungen zu 1.5 (Stand 08.10.2026, Datei `erweiterungen.py`, Abschnitt 9.2): **Lade-Ente** (kleine Ente schwimmt im
Kreis, solange etwas lädt); Tabelle mit Ansicht **„Kompakt“** (Nr., Vorderseite, Rückseite, Notiz, Prüfung – druckt eine
Zeile je Karte); **Karten importieren/exportieren** (ZIP mit `karten.csv` + `bilder/`, Vorschau mit Konflikten); Reiter
**„Ideen“** (unfertige Karten + eigene Ideen → „Als Karte aufnehmen“); **GANS-Bild gestalten** (Foto zuschneiden, Text
„GANS …“ verschieben/skalieren, Schrift wählbar, Dateiname `gans-<text>.jpg`); **Programmstart** im Standard-Browser,
in einem bestimmten Browser oder im eigenen Fenster (Frage beim ersten Öffnen, änderbar unter Werkzeuge);
**Deinstallieren** mit doppelter Bestätigung.
Abschluss für die Veröffentlichung (Stand 12.10.2026): Oberfläche standardmäßig **Englisch** (umschaltbar wie bisher);
Lade-Ente aus `duck_spinner.py` in Seite und Konsole; **Ideen exportieren/importieren**, Warnung bei Vorhandenem mit
Behalten/Ersetzen je Zeile, Wortprüfung „gibt es schon?“, Übersetzung Spanisch → Deutsch; **Deinstallieren als eigener
letzter Reiter** mit Komplettsicherung; Papier **A4 oder Letter**; **digitale Lernkarten** (`lernkarten_digital.py`:
Anki-Paket, Lernseite, Bildschirm-PDF, CSV); Erzeugen und Prüfen & drucken in Schritten; **Willkommens-Assistent**;
**Handy-Zugang im WLAN** (optional, mit PIN); Startdatei für **Linux**; KI-Vergrößerung 1,5× schneller (gleiche Bilder);
durchgehend freundlicher Ton und Hovertexte; Druckwege ohne Firmennamen (Abschnitt 5).
Änderungen in 1.4: neues **Startprogramm** – Startdatei für Windows (`.cmd`) und Mac (`.command`) bringt ein eigenes
Python mit (kein vorinstalliertes Python, keine Administratorrechte), erkennt den ersten Start und richtet dann alles
ein, sonst startet es sofort; Desktop-Symbol bzw. Mac-App; Reparatur, Doppelstart-Schutz und verständliche Meldungen
für alle gefundenen Stolpersteine (Abschnitt 10); dreisprachige Anleitung „LIES MICH ZUERST.html“; Programmdateien im
Unterordner `Programm`.
Änderungen in 1.3: neuer Name **Me Goos-ta Deutsch** mit Symbol (mexikanische Gans mit Sombrero und Sarape);
**Real-ESRGAN x4plus** als neue Bildverbesserung (Abschnitt 4, mit Modellvergleich); Oberfläche in **Deutsch, Englisch,
Spanisch**; **Schritt 1 „Bild vorbereiten“** und **Schritt 2 „Karte beschriften“** mit Prüfungen und verständlichen
Fehlermeldungen (Abschnitt 9); **Start ohne Administratorrechte** trotz Windows-„Intelligenter App-Steuerung“
(Abschnitt 10); **Sicherheitshärtung** (Abschnitt 11); Ausgabedateien heißen
`Me-Goos-ta-Deutsch_…`.
Änderungen in 1.2: Oberfläche im Browser, Kartenauswahl `--karten`, Lauf-Bericht, Karten ausschalten mit `#`.
Änderungen in 1.1: automatische Bildverbesserung, Prüfbogen, Selbsttest, Zwischenspeicher.

---

## 1. Produkt

| | |
|---|---|
| **Name** | Me Goos-ta Deutsch (Wortspiel aus „me gusta“ – „gefällt mir“ – und „goose“) |
| **Symbol** | weiße Gans mit Sombrero und bunter Sarape (`assets/me-goosta-symbol.svg`, `.png`, `.ico`) |
| **Idee** | Deutsch lernen über den Wortwitz „Gans + Wort“ („Gans alt“ klingt wie „ganz alt“) |
| **Lernende** | Muttersprache Spanisch → Rückseite auf Spanisch (gemeint ist immer das in Mexiko gesprochene Spanisch); mit dem Tool „Sprachen“ 14 weitere Sprachen für die Rückseite (Abschnitt 9.4) |
| **Ergebnis** | PDF-Dateien zum Drucken (Druckerei oder Heimdruck) plus Prüfbogen |
| **Oberfläche** | Englisch (Standard), Deutsch, Spanisch – die Karten selbst sind in allen Sprachen gleich |

## 2. Kartenaufbau (verbindlich)

**Vorderseite = das Bild.** Der Wortwitz steht bereits im Bild („Gans alt“). Dateiname = Text auf dem Bild:
`gans-<wort>.jpg` (alles klein, ä→ae, ö→oe, ü→ue, ß→ss, Leerzeichen→Bindestrich). Das Bild wird nicht beschriftet,
nur aufbereitet und verbessert (Abschnitt 4). Ganzes Bild sichtbar (`contain`); passt das Seitenverhältnis nicht,
füllt eine unscharfe Fortsetzung desselben Bildes die Restfläche. Mit `fit=cover` wird die Fläche gefüllt.

**Rückseite = das Wort auf Spanisch mit einer frechen Gans in der Ecke.** Spanisch meint im ganzen Programm immer das in
Mexiko gesprochene Spanisch (Übersetzungslogik bevorzugt mexikanische Varianten; sichtbar heißt es nur „Spanisch“). Hauptwort groß, fett, mittig
(Poppins Bold, Marineblau `#1B2D4F`); Alternativen (in der CSV mit „/“ getrennt) kleiner darunter (Poppins Medium,
`#3F5C88`). Hintergrund: ruhige, einfarbige hellblaue Fläche `#BFDDF2` – hinter dem Wort steht nichts. **Gezeichnete
Gans (seit 2.1):** die Gans des Programmsymbols (gespiegelt, ohne Sombrero/Sarape, weil die Rückseite für alle 15 Sprachen
gilt; Koordinaten wie in `assets/me-goosta-symbol.svg`) schwimmt unten rechts in einem kleinen Teich (`#A6CCE8`, Wellen
`#D6EBF9`) und schaut zum Wort: weißer Körper, Flügel `#E1EBF5`, Schnabel orange `#F6A94B`, Auge mit Glanzpunkt, Wange
`#F9CDBE`, kleiner Federschopf, Kopf leicht geneigt. Platz: `wort_boxen()` liefert die Fläche jeder Textzeile (dieselbe
Rechnung wie `zeichne_wort`, echte geformte Breite, Unterlänge der Schrift), `gans_box()` die größte Stufe von 34 % der
Innenhöhe abwärts (31, 28, 25, 22, 20 %; Seitenverhältnis 1,17), die mit 3 % der Innenhöhe Abstand zu allen Zeilen
passt – rechts und unten bündig mit der Innenfläche (auch bei rechts-nach-links-Sprachen; der Teich wird am Innenrand
abgeschnitten, nie im Beschnitt). Passt nicht einmal 20 %, bleibt die Gans weg (das Wort geht vor); Textlage und -größen
(`layout_wort`) sind unverändert. Statt der gezeichneten Gans kann ein eigenes Gänse-Bild den Hintergrund bilden (in der Oberfläche
per Knopf, Abschnitt 9; es füllt die Fläche und wird mittig zugeschnitten). Sonst nichts auf der Karte – der
Produktname steht nur im Rand der Druckbögen und im Prüfbogen.

**Rahmen (beide Seiten):** weißer Kartenrand 3,5 mm, darin die Gestaltungsfläche mit abgerundeten Ecken.
**Orientierung:** Querformat; die Rückseite steht nach dem Wenden wie eine Buchseite richtig herum.

## 3. Technische Daten

| Merkmal | Wert |
|---|---|
| Endformat | **88 × 63 mm quer** (Pokerformat 63 × 88 mm, gedreht) |
| Beschnitt | 3 mm rundum → Druckerei-Seite **94 × 69 mm** (mit `--hochkant` 69 × 94 mm) |
| Weißer Kartenrand | 3,5 mm |
| Gestaltungsfläche | 81 × 56 mm, Eckenradius 2,5 mm = **957 × 661 px bei 300 dpi** |
| Sicherer Textbereich | 75 × 50 mm |
| PDF-Boxen | TrimBox = Endformat, BleedBox = ganze Seite |
| Vorderseiten | JPEG 300 dpi, Qualität 93, ohne Farbunterabtastung, binär eingebettet |
| Rückseiten | Vektor (Text und Gans) |
| Farben | RGB (sRGB), alle Flächen deckend, keine Transparenz; die Druckerei rechnet nach CMYK um |
| Schrift | Poppins Bold / Medium aus `schrift/` (liegt bei, SIL Open Font License; Ersatz: DejaVu Sans, Liberation Sans, Arial), immer eingebettet |
| Textgröße Rückseite | automatisch: Hauptwort max. 23,5 % der Flächenhöhe, bei zwei Zeilen max. 19 %, min. 10 pt |
| Dateinamen | `Me-Goos-ta-Deutsch_Druckerei_88x63.pdf` (`…_hochkant.pdf`), `Me-Goos-ta-Deutsch_Heimdruck_A4_88x63.pdf`, `Me-Goos-ta-Deutsch_Pruefbogen.pdf`, `einzelbilder/01_vorn.png` …; andere Kartensprache (`--sprache ja`): Endung `_ja` vor `.pdf` bzw. `einzelbilder_ja/`, `digital/…_Anki_ja.apkg`, `…_Lernseite_ja.html`, `…_Bildschirm_88x63_ja.pdf`, `tabellen_ja/` – Spanisch ohne Endung (unverändert) |
| Seitenreihenfolge Druckerei-PDF | Karte 1 vorn, Karte 1 hinten, Karte 2 vorn, … |
| Einzelbilder | PNG, 300 dpi, je Kartenseite inkl. Beschnitt (≈ 1110 × 815 px), benannt nach Kartennummer |
| Lauf-Bericht | `ausgabe/bericht.json`: Zeitpunkt, Einstellungen, benutztes KI-Verfahren, je Karte Bildqualität (ppi, Bewertung, Verfahren) und Texthinweise (Text + Code), Meldungen, erzeugte Dateien |
| Heimdruck | A4 hoch, 2 × 4 Karten ohne Abstand, Schnittmarken im Rand, Rückseiten-Spalten gespiegelt (**Wenden an der langen Kante**), Druck mit **100 %** |
| Prüfbogen | A4 hoch, 5 Karten je Seite: Vorder- und Rückseite verkleinert, DE/ES-Text, Bildqualität, Hinweise (auch „ES wurde automatisch übersetzt – bitte prüfen“ bzw. „Übersetzung von Hand geprüft“), Abhak-Kästchen (immer Deutsch) |

## 4. Bildverbesserung

Jede Vorderseite durchläuft automatisch diese Schritte (Schalter `--qualitaet`, Standard `standard`; `--ki`, Standard `auto`):

| Schritt | Mit Real-ESRGAN (Standard) | Ohne Real-ESRGAN (FSRCNN/Lanczos) |
|---|---|---|
| 1. Öffnen | EXIF-Drehung anwenden, erstes Einzelbild, Transparenz auf Weiß, RGB | gleich |
| 2. Ränder entfernen | Zeilen/Spalten mit ≥ 55 % fast schwarzen Pixeln (≤ 12/255) am Rand abschneiden, +2 px | gleich |
| 3. Entrauschen | entfällt – das Netz entfernt JPEG-Blöcke und Rauschen selbst | Guided-Filter r = 2, ε = 0,03² (stark: r = 3, ε = 0,05², zweimal) |
| 4. Vergrößern | **Real-ESRGAN x4plus** ×4 auf das ganze RGB-Bild, dann Lanczos auf die Zielgröße | FSRCNN ×2/×3/×4 auf der Helligkeit, dann Lanczos |
| 5. Nachschärfen | Unscharf maskieren, Radius 1,0, 35 % (stark 60 %), Schwelle 2 | Radius 0,8 × Faktor, 60 % (stark 80 %), Schwelle 3 |
| 6. Tonwerte, Farbe | Autokontrast 0,3 % (stark 0,4 %), Sättigung × 1,06 (stark × 1,08) | gleich |

- KI wird nur beim Vergrößern um mehr als 5 % eingesetzt; größere Quellen werden mit Lanczos verkleinert.
- `--ki auto` nimmt das beste vorhandene Modell (Real-ESRGAN x4plus → x2plus → FSRCNN → Lanczos);
  `realesrgan`, `realesrgan-x2`, `fsrcnn`, `aus` wählen fest. Fehlt ein gewähltes Modell, wird das beste vorhandene
  genutzt und gemeldet. `--qualitaet aus` = nur auf Größe bringen. Der alte Schalter `--ohne-ki` wirkt wie `--ki aus`.
- **Rechenweg:** `ki_modelle.py` rechnet RRDBNet (Real-ESRGAN), SRVGGNetCompact und SwinIR in **reinem NumPy** – kein
  PyTorch, keine Grafikkarte. Kachelweise (128 px, 16 px Überlappung), große Faltungen in Streifen (≤ 96 MB je Schritt).
  Dauer x4plus: ca. 1–4 Minuten je 512-px-Bild (abhängig vom Prozessor), nur beim ersten Mal.
- **Modelle:** `modelle/realesrgan-x4plus.npz` (30 MB, float16) – nicht im Download, sondern das **Tool
  „Bildverbesserung“** (Abschnitt 9.4): Werkzeuge → Tools, Erstabfrage oder Rückfrage beim ersten Gebrauch. Das Original `RealESRGAN_x4plus.pth`
  stammt aus den offiziellen GitHub-Releases (SHA-256 `4fa0d389…d682f1`, BSD-3-Clause, `modelle/LICENSE-RealESRGAN.txt`).
  Weitere Modelle lädt `python3 ki_modelle.py --laden <id>` bzw. „Werkzeuge“ der Oberfläche – mit Prüfsumme;
  die .pth wird von einem **eingeschränkten Unpickler** gelesen (nur Tensor-Bausteine erlaubt) und als pickle-freie
  .npz gespeichert. FSRCNN-Gewichte: `modelle/fsrcnn_x2|x3|x4.npz` (Apache-2.0).
- **Schnellvorschau:** Die Oberfläche zeigt bis zum ersten Erzeugen eine Vorschau mit FSRCNN (Bruchteile einer Sekunde);
  liegt das fertige Real-ESRGAN-Ergebnis im Zwischenspeicher, wird dieses gezeigt.
- **Bewertung der Schärfe:** ppi im Druck = 300 / Vergrößerungsfaktor. ≥ 250 sehr gut · ≥ 180 gut · ≥ 120 ausreichend ·
  darunter „gering – bessere Bildquelle empfohlen“ (zusätzlich Warnung). KI kann fehlende Details nicht wirklich
  wiederherstellen; Real-ESRGAN erzeugt glaubhafte, aber teils „gemalte“ Feinstrukturen.
- **Zwischenspeicher** `ausgabe/.cache/`: Schlüssel = Inhalt der Bilddatei + Bildversion (2.0) + Format + dpi + Ausschnitt
  + Qualitätsstufe + tatsächlich benutztes Verfahren. Nur neue/geänderte Bilder werden berechnet. Zu jedem Ergebnis
  steht in `<schlüssel>.json` auch, aus welchem Bild (Name, SHA-1) es mit welchen Einstellungen wann und in welcher
  Rechenzeit entstand – daraus zeigt der Reiter „Bildverbesserung“, welche Bilder schon verbessert sind, und schätzt
  die Dauer für die übrigen.
- **Vorab verbessern:** `--nur verbessern` rechnet nur die Vorderseiten in den Zwischenspeicher (keine Druckdateien),
  auch für ausgeschaltete und noch unbeschriftete Karten; Auswahl mit `--bild NAME` (mehrfach) oder `--karten`.
  Der Reiter „Bildverbesserung“ der Oberfläche nutzt genau diesen Aufruf; beim Erzeugen kommen die Bilder dann aus
  dem Zwischenspeicher.

**Modellvergleich (Oktober 2026)** – Kriterium: bestmögliche Verbesserung kleiner, stark komprimierter Fotos mit
Schrift; kostenlos, frei zugänglich, freie Lizenz; Rechenzeit nachrangig. Getestet an `gans-alt.jpg` (512 px):

| Modell | Lizenz | Ergebnis an den Beispielbildern | Rechenzeit* | Urteil |
|---|---|---|---|---|
| FSRCNN ×2–×4 (bisher) | Apache-2.0 | vergrößert nur, JPEG-Blöcke bleiben sichtbar | < 1 s | Rückfall |
| **Real-ESRGAN x4plus** | BSD-3 | entfernt Blöcke, Federn/Augen glaubhaft scharf, Schrift sauber | ≈ 280 s | **gewählt** |
| Real-ESRGAN x2plus | BSD-3 | fast gleich, minimal weicher | ≈ 60 s | optionale schnelle Wahl |
| Real-ESRGAN general x4v3 | BSD-3 | klein und schnell, Blöcke teils sichtbar | ≈ 25 s | – |
| Real-ESRGAN anime 6B | BSD-3 | malt Fotos flächig („Comic-Look“) | ≈ 80 s | nur für Zeichnungen |
| SwinIR-L Real-World GAN | Apache-2.0 | natürlich, lässt aber mehr Blöcke und Rauschen stehen | ≈ 600 s | – |
| HAT-L Real GAN | Apache-2.0 | laut Autoren ähnlich; Gewichte nur über Google Drive/Baidu | – | nicht frei abrufbar |
| SUPIR, StableSR, DiffBIR u. a. (Diffusion) | meist nur nichtkommerziell | erfinden Details und Buchstaben, brauchen GPU | – | ungeeignet |

*Rechenzeit für 512 × 512 px auf 2 Prozessorkernen in reinem NumPy; ein üblicher Laptop ist schneller.

## 5. Druckwege (länderunabhängig)

Bei Me Goos-ta Deutsch haben **beide Seiten jeder Karte ein eigenes Motiv** – das entscheidet über die Eignung eines
Druckwegs. Das Programm nennt bewusst keine Firmen: Angebote, Preise und Vorgaben unterscheiden sich je Land und
ändern sich laufend.

| Weg | Datei | Worauf achten |
|---|---|---|
| **Heimdruck / Copyshop** | `…_Heimdruck_A4_…pdf` bzw. `…_Letter_…` | Papier A4 oder Letter (`--papier`), 100 % drucken, beidseitig an der langen Kante wenden, Karton 200–300 g/m²; Versatz (`--versatz-x/-y`) und `--rs-drehen` nach Probedruck |
| **Online-Kartendruckerei** (Suchbegriffe: „Spielkarten individuell drucken“, „custom playing cards“, „imprimir cartas personalizadas“) | `…_Druckerei_…pdf` oder `einzelbilder/` | **jede Karte mit eigener Vorder- und Rückseite** (nicht nur eine gemeinsame Rückseite); Pokerformat 63 × 88 mm passt direkt, sonst `--format`; Beschnitt meist 3 mm (im PDF enthalten, Datei 94 × 69 mm); Hochformat-Vorlage → `--hochkant`; Upload als PDF oder Einzelbilder; Mindestmenge, Kartenstärke und Versand vergleichen; Probeexemplar bestellen |
| **Vorgestanzte Kartenbögen** (Bürobedarf) | Heimdruck-PDF mit angepasstem Raster | Maße des Bogens messen und `--format`, `--spalten`, `--zeilen`, `--abstand`, `--versatz-x/-y` einstellen |
| **Digital** | `ausgabe/digital/` | Anki-Paket, Lernseite, Bildschirm-PDF, Tabellen (CSV) (`lernkarten_digital.py`, Schalter `--nur digital --digital …`) – Bedienung im Leitfaden, Abschnitt „Digital lernen“ |
| ✗ Dienste mit **einer gemeinsamen Rückseite** für alle Karten | – | ungeeignet: die Rückseite trägt hier das Wort |

Vor jeder Bestellung die aktuelle Vorlage des Dienstes laden und mit Abschnitt 3 vergleichen; Probedruck prüfen.

## 6. Vorlagen

| Datei | Inhalt | Für |
|---|---|---|
| `vorlagen/VORLAGE_Druckerei_88x63_quer.pdf` | Vorder- und Rückseite, 94 × 69 mm: Beschnitt (rot), Endformat (schwarz), Gestaltungsfläche (blau), sicherer Textbereich (grün), Pfeil „oben beim Lesen“ | Online-Kartendruckereien, eigene Gestaltung in anderen Programmen |
| `vorlagen/VORLAGE_Heimdruck_A4_88x63.pdf` | A4-Raster 2 × 4 mit Platznummern und Schnittmarken; Rückseite mit gespiegelten Plätzen | Heimdruck, Copyshop |

## 7. Datei `karten.csv`

UTF-8 (mit oder ohne BOM; Windows-1252 wird erkannt und gemeldet), Trennzeichen Semikolon (Komma/Tab werden erkannt).

| Spalte | Pflicht | Bedeutung |
|---|---|---|
| `bild` | ja | Dateiname im Ordner `bilder/` |
| `de` | nein | Text auf dem Bild (Kontrolle im Prüfbogen, nicht gedruckt) |
| `es` | ja | Rückseite: `/` trennt Hauptwort von Alternativen; `\|` erzwingt einen Zeilenumbruch im Hauptwort |
| `notiz` | nein | eigene Notiz, nicht gedruckt |
| `fit` | nein | `contain` (Standard) oder `cover` |
| `uebersetzung` | nein | `automatisch` = `es` ist ein übernommener Übersetzungsvorschlag, noch nicht geprüft · `geprüft` = im Reiter „Tabelle“ abgehakt · leer = von Hand eingetragen (auch `ja`/`x`/`ok` gelten als geprüft). Ändert sich das Wort oder der Text auf dem Bild, wird die Spalte geleert. Die Spalte entsteht erst, wenn sie gebraucht wird. |
| `en`, `nds`, `fr`, … (Sprachcode) | nein | weitere Rückseite in dieser Sprache (Tool „Sprachen“, gleicher Aufbau wie `es`); Spalte nur, wenn benutzt |
| `uebersetzung_<code>` | nein | Status wie `uebersetzung`, für die Rückseite in dieser Sprache |

Zeilenfolge = Kartenfolge; `#` vor dem Bildnamen = Karte ausgeschaltet (wird nicht gedruckt, bleibt aber in der Liste;
in der Oberfläche der Schalter „Drucken“). Schritt 1 der Oberfläche legt die Zeile mit `bild`, `de` und `fit` an,
Schritt 2 ergänzt `es` und `notiz` (Schritt 1 kann `es` schon mitgeben). Texte und Notizen, die mit `= + - @` beginnen
würden, lehnt die Oberfläche ab (Excel-Formeln). Kartennummer = Position unter den gültigen, eingeschalteten Karten.
**Beispielkarten:** Der Download enthält die Beispielliste als `beispiel-karten.csv` und die Bilder dazu in
`beispiel-bilder/` – keine `karten.csv` und keinen Ordner `bilder/`. Fehlt `karten.csv` (frisch entpackt), legt das
Programm sie beim ersten Lesen als Kopie der Beispielliste an und kopiert die Beispielbilder nach `bilder/`; ein dort
schon vorhandenes Bild wird nie ersetzt. So kann das Entpacken einer neuen Version über einen alten Ordner weder die
eigene Kartenliste noch eigene Bilder überschreiben.
Zusätzliche, eigene Spalten bleiben beim Speichern erhalten; vor jedem Speichern durch die Oberfläche wird die vorige
Fassung als `karten.bak.csv` gesichert. Gemeldet werden: fehlende Bilder, leere `es`-Spalte, doppelte Bilder,
Bilder ohne CSV-Zeile, zu lange Texte, zu geringe Bildauflösung.

### Beispielkarten (10)

| Nr. | Bild | Text auf dem Bild | Rückseite (zur Prüfung durch Muttersprachler/in) |
|---|---|---|---|
| 1 | gans-abendlich.jpg | Gans abendlich | vespertino / del atardecer |
| 2 | gans-adelig.jpg | Gans adelig | noble / aristocrático |
| 3 | gans-aggressive.jpg | Gans aggressiv | agresivo |
| 4 | gans-alt.jpg | Gans alt | viejo |
| 5 | gans-anders.jpg | Gans anders | diferente / distinto |
| 6 | gans-anstaendig.jpg | Gans anständig | decente / respetable |
| 7 | gans-antifaschistisch.jpg | Gans antifaschistisch | antifascista |
| 8 | gans-arg-hunger.jpg | Gans arg Hunger | muchísima hambre / me muero de hambre |
| 9 | gans-aufgeregt.jpg | Gans aufgeregt | emocionado / nervioso |
| 10 | gans-aufmuepfig.jpg | Gans aufmüpfig | rebelde / respondón |

## 8. Generator `gans_lernkarten.py`

Aufruf: `python3 gans_lernkarten.py` (Windows: `py gans_lernkarten.py`) – oder über die Oberfläche. Benötigt Python 3.9+,
`reportlab`, `pillow`, `numpy`, `pypdfium2` (Einzelbilder und Vorschau – ohne ihn zeichnet `leinwand.py` die
Rückseiten-Vorschau mit Pillow; `requirements.txt` mit Ober- und Untergrenzen).
Laufzeit für 10 Karten: mit FSRCNN ca. 8 s; mit Real-ESRGAN beim ersten Mal 1–5 min je Bild, danach ca. 3 s.
Sprache der Meldungen: Umgebungsvariable `MGD_SPRACHE=de|en|es` (setzt die Oberfläche automatisch); Druckdateien
und Prüfbogen bleiben immer gleich (Deutsch).

| Schalter | Wirkung |
|---|---|
| `--nur druckerei` / `bogen` / `pruefbogen` / `vorlagen` | nur einen Teil erzeugen |
| `--nur verbessern` | nur die Vorderseiten verbessern (Zwischenspeicher), keine Druckdateien – auch ausgeschaltete und unbeschriftete Karten |
| `--karten 1,3,5-8` | nur diese Kartennummern |
| `--bild gans-alt.jpg` (mehrfach) | nur die Karten mit diesen Bildern (einfache Dateinamen aus `bilder/`); in der Oberfläche intern für den Reiter „Bildverbesserung“ |
| `--qualitaet aus` / `standard` / `stark` | Stufe der Bildverbesserung |
| `--ki auto` / `realesrgan` / `realesrgan-x2` / `fsrcnn` / `aus` | KI-Vergrößerung (Abschnitt 4) |
| `--hochkant` | Druckerei-Datei im Hochformat (Vorderseite 90° links, Rückseite 90° rechts gedreht) |
| `--rs-drehen` | Rückseiten zusätzlich um 180° drehen |
| `--format 88x63` · `--beschnitt 3` · `--rand 3.5` · `--radius 2.5` · `--dpi 300` | Maße ändern (`--rand 0` = randlos) |
| `--gans-bild datei.png` | eigenes Gänse-Bild als Rückseiten-Hintergrund; Standard: `assets/gans_hintergrund.png` bzw. `.jpg`, falls vorhanden (so legt es der Knopf in der Oberfläche ab) |
| `--abstand`, `--spalten`, `--zeilen`, `--versatz-x`, `--versatz-y` | Heimdruck-Raster anpassen |
| `--ohne-png` · `--ohne-cache` | keine Einzelbilder · alles neu berechnen |
| `--csv`, `--bilder`, `--ausgabe`, `--vorlagen-ordner` | andere Pfade |

Beschriftungen der Schalter stehen dreisprachig im Parser (`L(deutsch, englisch, spanisch)`); die Oberfläche liest sie aus.
Zusätzlich im Parser: `ui_art` (eigenes Bedienelement, z. B. `gansbild` = Knopf mit Vorschau), `intern` (nur für die
Oberfläche, kein Feld – `--bild`) und je Gruppe `reiter` (`erzeugen` oder `bildverbesserung`).

## 9. Oberfläche `gans_ui.py` + `ui/index.html`

**Start:** über das Startprogramm (Abschnitt 10) oder `python3 gans_ui.py [--port 8765] [--kein-browser]`. Die
Oberfläche öffnet sich unter `http://127.0.0.1:<port>/?k=<Startschlüssel>`; der Schlüssel wird gegen ein Sitzungs-Cookie
getauscht (Abschnitt 11). Sprache oben rechts (DE · EN · ES), gespeichert in `ui_einstellungen.json`.

| Bereich | Funktion |
|---|---|
| Meine Karten | Alle Karten mit Vorschau (Klick dreht um), Nummer, Texten, Bildqualität und Hinweisen (u. a. „verbessert“, „automatisch übersetzt – prüfen“, „Übersetzung geprüft“); Bearbeiten (→ Schritt 2), Drucken an/aus, Reihenfolge, aus Liste entfernen (mit „Rückgängig“) – jede Änderung wird sofort gespeichert; Hinweis auf offene Karten |
| Tabelle | Je Karte Nummer, Bild, **Vorderseite (Deutsch) → Rückseite (Spanisch)**, Notiz und Prüfstatus nebeneinander; direkt in der Zelle ändern (gespeichert beim Verlassen des Feldes, Enter), 🌐 Übersetzungsvorschlag, Häkchen „geprüft“ (→ Spalte `uebersetzung`), Hinweise aus der Prüfung (z. B. gleich wie Deutsch, Umlaut, zu lang, doppelt); Filter (alle · noch nicht geprüft · automatisch übersetzt · ohne Übersetzung · mit Hinweisen), Suche, Sortieren, Bilder ein/aus, Drucken; auf schmalen Bildschirmen untereinander. Die Navigation zählt die automatisch übersetzten, ungeprüften Karten. |
| Bildverbesserung | Kacheln aller Karten mit Status: **verbessert** (grün, mit Verfahren, ppi und Zeitpunkt) · andere Einstellung (früher anders verbessert) · noch nicht verbessert · Bild fehlt. Auswahl einzeln oder „Alle“ / „Noch nicht verbesserte“, geschätzte Dauer (aus gemessenen Zeiten), „Ausgewählte verbessern“ (Lauf `--nur verbessern --bild …` mit Fortschrittsbalken, abbrechbar – Fertiges bleibt), Klick auf ein Bild = **Vorher/Nachher** mit Schieberegler (Vorher = nur auf Kartengröße gebracht), Einstellungen Qualität und KI-Vergrößerung (Gruppe „Bildverbesserung“) |
| 1 Bilder vorbereiten | Bilder per Ziehen oder Auswahl hochladen – **auch viele auf einmal, drei gleichzeitig**, mit Fortschritt → Entwurf in `ausgabe/.entwuerfe/` (bleibt über Neustarts, wird nach 14 Tagen gelöscht); **„🪄 Gans mit KI erzeugen“** (Abschnitt 9.3) und „🎨 GANS-Bild gestalten“ liefern ebenfalls Entwürfe. Je Entwurf eine kompakte Zeile: Vorschau der Vorderseite, „Text auf dem Bild“ (aus dem Dateinamen vorgeschlagen) → Dateiname, **Wort auf Spanisch (optional) mit 🌐**, Status, Übernehmen, Details (Original, Drehen ↺ ↻, Ausschnitt mit Empfehlung ★, vollständige Prüfliste), Verwerfen. Leiste: Zahl der Bilder/bereit/beschriftet, **„Alle übersetzen“**, **„Alle übernehmen“** (übernimmt alle fehlerfreien; mit Wort sind die Karten sofort fertig, sonst warten sie in Schritt 2) |
| 2 Karten beschriften | Alle Karten ohne Wort auf Spanisch, Bilder ohne Zeile und per „Bearbeiten“ geöffnete Karten. Felder Spanisch (mit 🌐 und Vorschlägen) / Text auf dem Bild / Notiz, Sonderzeichen-Knöpfe (á é í ó ú ñ ü ¿ ¡), Live-Rückseite, Prüfliste, „Karte speichern“ (nur ohne Fehler), „Später“, bei neuen Bildern „Bild entfernen“; Leiste mit **„Alle übersetzen“** und **„Alle speichern“**. **„Bild ändern …“** (oder Bild auf die Vorschau ziehen): Entwurf mit `karte=<bild>` (`POST /api/entwurf?name=…&karte=…`), gleiche Prüfungen wie Schritt 1 (Drehen, Ausschnitt), Name/Texte/Notiz/Status bleiben; Übernehmen legt das alte Bild nach `bilder/_entfernt/`, „Rückgängig“ über `POST /api/karte-bild-zurueck`; anderes Format → in das Format der Endung umgewandelt. **„🪄 Mit KI …“** erzeugt das neue Bild (Abschnitt 9.3) |
| 3 Erzeugen | Startknopf je Auswahl von `--nur` (außer `verbessern`), Feld `--karten`, alle übrigen Schalter in ihren Gruppen (automatisch gespeichert; „Bildverbesserung“ steht im eigenen Reiter), **Gänse-Bild der Rückseite**: Vorschau der Rückseite, „Gänse-Bild laden …“ (auch per Ziehen), „Gezeichnete Gans verwenden“, „Vorheriges Bild“; Hinweis zum KI-Verfahren mit Verweis auf den Reiter Bildverbesserung, Kommandozeile, Live-Protokoll mit Fortschritt je Bild, Abbrechen |
| 4 Prüfen & drucken | letzter Lauf aus `bericht.json` mit Meldungen, alle Dateien mit „Öffnen“ und „Im Browser ansehen“, Druckhinweise |
| Werkzeuge | Bereich **„🧰 Tools“** ganz oben (Bildverbesserung, Übersetzung, KI-Bilder: installieren, Zustand, deinstallieren; Abschnitt 9.4), Selbsttest, Projekt-ZIP (`ausgabe/Me-Goos-ta-Deutsch_Projekt.zip`, ohne große Modelle und ohne aufgehobene Gänse-Bilder), Zwischenspeicher leeren, Ordner öffnen, `karten.csv` extern öffnen; **Automatische Übersetzung**: erlauben/widerrufen, Dienst wählen, eigener DeepL-Schlüssel, „Neue Karten automatisch übersetzen“, gemerkte Übersetzungen löschen |
| Hilfe | Leitfaden in der eingestellten Sprache, diese Spezifikation, Programmstand; `GET /api/hilfe?doc=leitfaden\|spec` → `{html, datei}`, gerendert mit dem eingebauten Markdown-Umwandler (kommt garantiert zum Ende: jede Zeile, die kein Block erkennt, wird Text) und je Datei + Änderungszeit zwischengespeichert; die Seite wartet höchstens 20 s, zeigt „Abbrechen“ unter der Ente und bei Fehlern „Nochmal versuchen“; beim Reiterwechsel zählt nur die zuletzt angefragte Seite |
| ⏻ Beenden | stoppt die Oberfläche (sonst läuft sie im Hintergrund weiter; ein neuer Start öffnet dann nur den Browser) |

**Prüfungen in Schritt 1** (`gans_lernkarten.analysiere_bild`, `pruefe_name`; Stufen Fehler / Warnung / Hinweis / OK;
Fehler verhindern das Übernehmen):

| Code | Stufe | Auslöser |
|---|---|---|
| `b_heic` | Fehler | HEIC/HEIF (iPhone) – mit Anleitung zum Umstellen auf JPG |
| `b_unlesbar` | Fehler | kein lesbares Bild |
| `b_datei_gross` · `b_pixel` | Fehler | > 40 MB · > 60 Megapixel |
| `b_winzig` | Fehler | kürzere Seite < 100 px |
| `b_format_ok` · `b_format_umwandeln` | OK · Hinweis | JPG/PNG/WEBP direkt; GIF/BMP/TIFF u. a. → PNG |
| `b_animiert` · `b_cmyk` · `b_transparent` · `b_exif` | Warnung · Hinweise | erstes Einzelbild · CMYK → RGB · Transparenz → Weiß · Kamera-Drehung |
| `b_raender` | Hinweis | schwarze Ränder werden entfernt |
| `b_ppi` · `b_ppi_gering` | OK/Hinweis · Warnung | Druckauflösung; < 120 ppi mit empfohlener Mindestbreite |
| `b_hochkant` | Hinweis | Hochformat auf querer Karte (Tipp: drehen) |
| `b_cover_schnitt` · `b_contain` | Warnung · Hinweis | „Fläche füllen“ schneidet ≥ 12 % ab · Ränder werden unscharf fortgesetzt |
| `b_doppelt` | Warnung | gleiche Datei (SHA-1) liegt schon in `bilder/` |
| `b_ki` | Hinweis | welches KI-Verfahren beim Erzeugen arbeitet |
| `n_text_leer` | Fehler | kein Text → kein Dateiname |
| `n_kollision` · `n_ersetzen` | Fehler · Warnung | Name vergeben (auch gleicher Name mit anderer Endung); mit „ersetzen“: alte Datei → `bilder/_entfernt/`, Kartenzeile wird umbenannt |
| `n_entwurf_doppelt` | Fehler | zwei neue Bilder bekämen denselben Namen |
| `n_ohne_gans` · `n_lang` | Hinweis · Warnung | kein „Gans“/„Gäns…“ im Text (beim Übernehmen kommt „Gans“ an den Anfang, seit 2.4) · über 40 Zeichen |

**Prüfungen in Schritt 2** (`gans_lernkarten.pruefe_karte`):

| Code | Stufe | Auslöser |
|---|---|---|
| `k_es_leer` | Fehler | kein Wort auf Spanisch |
| `k_formel` | Fehler | Text beginnt mit `= + - @` (Schutz vor Formel-Ausführung in Excel) |
| `k_zeichen` | Fehler | Zeichen fehlt in der Kartenschrift (z. B. Emoji) |
| `k_bild_fehlt` | Fehler | Bilddatei fehlt |
| `haupt_zu_lang` · `alt_zu_lang` · `zu_viel_text` | Warnung | Text passt nicht in die Fläche (gleiche Regel wie im Generator) |
| `k_umlaut` | Warnung | ä, ö, ß im spanischen Wort (ü ist erlaubt: pingüino) |
| `k_alternativen` | Warnung | mehr als 2 Alternativen |
| `k_gleich` | Warnung | Spanisch = Deutsch |
| `k_de_leer` | Warnung | Text auf dem Bild fehlt |
| `k_frage` · `k_doppelt` · `n_ohne_gans` | Hinweis | „¿/¡“ fehlt · Wort schon auf anderer Karte · kein „Gans“ im Text (Speichern setzt es davor) |
| `k_passt` | OK | Zeilenzahl und Schriftgröße |

Alle Meldungen gibt es in drei Sprachen (`PRUEF_MELDUNGEN` in `gans_lernkarten.py`); die Oberfläche schickt ihre Sprache
in der Kopfzeile `X-GL-Sprache`, der Server antwortet in dieser Sprache (je Anfrage, thread-sicher).

**Gänse-Bild per Knopf:** `POST /api/gans-bild` (rohe Bytes): höchstens 40 MB und 60 Megapixel, kein HEIC,
`verify()`, kürzere Seite mindestens 300 px; das Bild wird gedreht (EXIF), Farben mit eingebettetem Profil nach sRGB
umgerechnet, auf höchstens 2400 px verkleinert und **neu gespeichert** – ohne Metadaten, als
`assets/gans_hintergrund.jpg` (mit Transparenz `.png`). Ein früheres Bild kommt nach `assets/_alt/` (nichts wird
gelöscht); „Gezeichnete Gans verwenden“ legt das aktuelle ebenfalls dorthin, „Vorheriges Bild“ holt das zuletzt
beiseitegelegte zurück. Ein früher eingetippter Pfad (`--gans-bild` in den Einstellungen) wird dabei geleert. Die
Vorschau berücksichtigt die Änderungszeit des Bildes.

**Aufbau:** `gans_ui.py` ist ein Webserver aus der Python-Standardbibliothek (keine Zusatzpakete). Alle Adressen
(Logik in `verarbeite()`/`Anfrage`, Ergänzungen in `erweiterungen.get/post`; E33 prüft, dass jede hier steht):
`GET /api/status|optionen|farben|karten|ergebnisse|werkzeuge|tools|lauf|warteschlange|befehl|hilfe|vorschau|entwuerfe|entwurf-bild|gans-bild|rueckseite|verbesserung|vergleich|tabelle|uebersetzung|zielsprache|ki-bild|ki-bild-bild|lernen|lernen-karte|lernen-export|app-sicherung`,
`POST /api/sprache|zielsprache|farben|einstellungen|karten|lauf|lauf-stopp|warteschlange|tool|tools-erstabfrage|oeffnen|bild-weg|werkzeug|entwurf|entwurf-pruefen|entwurf-uebernehmen|entwurf-weg|karte-pruefen|karte-speichern|karte-status|karte-bild-zurueck|gans-bild|gans-bild-weg|gans-bild-zurueck|uebersetzung|uebersetzen|ki-bild-prompt|ki-bild-text|ki-bild-uebersetzen|ki-bild-uebernehmen|lernen-bewerten|lernen-rueckgaengig|lernen-einstellungen|lernen-stapel|lernen-zuruecksetzen|lernen-import|app-sicherung|beenden`;
Ergänzungen: `GET /api/export|ideen|idee-bild|start-einstellung|lan`,
`POST /api/import|import-pruefen|import-uebernehmen|import-verwerfen|idee|idee-wort|idee-bild|idee-weg|idee-zurueck|idee-aufnehmen|wortliste-pruefen|wortliste-uebernehmen|wortliste-rueckgaengig|uebersetzen-de|start-einstellung|deinstallieren|lan`;
dazu `/bild/<Name>`, `/datei/<Gruppe>/<Name>`, `/schrift/…`, `/symbol.svg`, `/favicon.ico`, `/apple-touch-icon.png`
(`app-sicherung` nur in der Web-App; `deinstallieren`, `beenden`, `oeffnen`, `lan`, `start-einstellung` nur am Rechner).
Unerwartete Fehler antworten mit 500 und einem freundlichen Text in der Sprache der Oberfläche (technischer Grund in
Klammern); Prüffehler der Einstellungen nennen das Feld („Nur diese Karten: …“) statt des Schalters.
Läufe (Generator, Bilder verbessern, Selbsttest, Modell laden, KI-Bild erzeugen) starten als eigener Prozess mit
Live-Protokoll; immer nur einer zur Zeit, Abbrechen beendet den Prozess.

**Logik ohne HTTP (seit 2.0, für die Web-App):** Alle Adressen stehen in
`verarbeite(methode, weg, abfrage, koerper, kopf, am_handy) → (Status, Kopf, Inhalt)` (Klasse `Anfrage` mit
`_get`/`_post`; `erweiterungen.get/post` bekommen dieses Objekt). Der `Handler` ist nur noch die Hülle: Host-, Origin-,
Cookie- und Token-Prüfung, Startseite (`seite_html`), PIN-Seite des Handy-Zugangs, Sicherheits-Kopfzeilen beim Senden.
Ohne Sitzung erreichbar sind nur Symbole und Schriften (`oeffentlich(weg)`). Neue Adressen kommen nur in `Anfrage`.
`koerper` darf Bytes (Web-App; Länge ergänzt) oder ein Strom mit `Content-Length` sein (Server; große Importe bleiben
gestreamt).
**Läufe im selben Prozess:** Mit `im_prozess()` (im Browser immer, am Rechner zum Prüfen `MGD_IM_PROZESS=1`) ruft ein
Lauf `main(argv)` des Moduls aus dem Befehl direkt auf; die Ausgabe wird zeilenweise Protokoll (`_LaufAusgabe`), die
Sprache wie `MGD_SPRACHE`. Abbrechen setzt den Merker `abgebrochen` (wirkt bei der nächsten Ausgabe als `LaufAbbruch`,
in Pyodide auch `KeyboardInterrupt`). Im Browser (keine Threads) startet ein Auftrag erst nach der Antwort auf
`POST /api/lauf` (`laeuft: true` wie am Rechner): der Worker ruft danach `web_weiter()`, das ihn (und die folgenden der
Warteschlange) bis zum Ende rechnet; `WEB_MELDER` meldet währenddessen den Stand als JSON (höchstens alle 0,4 s), damit die
Seite Protokoll und Fortschritt zeigt. Warteschlange und Abschluss bleiben gleich.
**Web-App-Weichen (`im_browser()` = `sys.platform == "emscripten"`):** Rechner-Wege wie am Handy gesperrt (Ordner öffnen,
Beenden, Deinstallieren, Start-/Handy-Einstellungen, Versionsprüfung, Werkzeuge `nur_rechner` → 403 `nur_rechner`); KI-Bilder und Selbsttest
nur am Rechner (Lauf/Installieren 403, Tool-Karte `nur_rechner`, `tool_da` falsch); Übersetzung nur über Dienste mit CORS
(Wiktionary mit `origin=*`, MyMemory; DeepL → `dienst_rechner`) per synchronem `XMLHttpRequest` im Web-Worker;
Bildaufbereitung ohne Thread-Pool. `/api/status` meldet `web_app`, `vorschau_art` und `web_adresse` (Adresse der Handy-App
aus `web_adresse.txt`, eine Zeile `https://…`, leer = noch nicht veröffentlicht). In der App außerdem nur am Rechner:
Werkzeuge Selbsttest und Projekt-ZIP (`NUR_RECHNER_WERKZEUGE_WEB`); Downloads (Sprachpakete) per synchronem
`XMLHttpRequest` (`ki_modelle.web_oeffnen`, nur CORS-Adressen); Real-ESRGAN kommt als fertige `.npz` aus dem Ordner
`modelle/` der App (GitHub erlaubt keine Browser-Downloads; Größe + SHA-256 aus `modelle/modelle.json`), ohne zweite
Kopie im Datenordner; Sprachen ohne uharfbuzz (`sprachen.noetige_pakete` leer → hi/ar ohne Silbenformen);
`/api/start-einstellung` ohne Startprogramm.

**Handy-App (Web-App/PWA, seit 2.0):** `bau_webapp.py` (Arbeitsordner, Quellen in `web-app-quelle/`) baut aus dem Programm
einen statischen Ordner `web-app/`: `index.html` (dieselbe Oberfläche; Skript als `ui.js` ausgelagert, CSP ohne
eingebettete Skripte, relative Adressen, `viewport-fit=cover`, Manifest, Startbildschirm mit Lade-Ente), `app.js`, `worker.js`,
`sw.js`, `manifest.webmanifest` (standalone, Symbole 192/512 + maskable, Apple 180, Kurzbefehle Lernen/Neue Karte),
`py/programm.zip` (Module ohne Startprogramm, KI-Bilder, Tests; Beispiele, Symbole, Poppins, FSRCNN, Vorlagen, Leitfäden,
SPEC; feste Zeitstempel → gleicher Inhalt = gleiche Prüfsumme), `pyodide/` (Pyodide 314.0.7 Kern + NumPy, Pillow,
charset-normalizer aus der `pyodide-lock.json`, ReportLab 5.0.1 von PyPI – alles mit SHA-256), `schrift/`, `symbole/`,
`lizenzen/`, `modelle/` (Real-ESRGAN nur auf Wunsch). Positivliste – Nutzerdaten kommen nie hinein. Ablauf:
- **Service Worker (`sw.js`):** lädt beim ersten Mal alle Dateien der Liste (Pfad, Größe, SHA-256; ≈ 22 MB) mit
  MB-Fortschritt in den Zwischenspeicher `mgd-app-<Version>` und antwortet danach „zuerst Zwischenspeicher“ (offline).
  Eine neue Version übernimmt unveränderte Dateien aus der alten und wartet; die Seite meldet „Neue Gänse-Version da –
  neu laden?“ (Toast und „Mehr“), „Neu laden“ sichert, aktiviert und lädt neu. Adressen `/api/…`, `/bild/…`, `/datei/…`
  (auch absolut, außerhalb des Unterordners) gehen an das Fenster (`app.js`), das sie an Python weiterreicht. Alle
  Antworten tragen COOP/COEP → die Seite ist „cross-origin isolated“ (einmaliges Neuladen beim ersten Start).
- **`app.js`:** Startbildschirm (Lade-Ente, Schritte, MB), Service Worker registrieren, Web-Worker starten, Sprache und
  Farben aus Python setzen, dann `ui.js` laden. Während Python einen Auftrag rechnet, beantwortet `app.js`
  `GET /api/lauf` selbst aus der letzten `WEB_MELDER`-Meldung; „Abbrechen“ setzt den Unterbrechungs-Puffer
  (`SharedArrayBuffer` → `KeyboardInterrupt`). Download-Links und `target=_blank` auf App-Adressen öffnen in der App das
  Fenster „Teilen / Speichern“ (`navigator.share` mit Datei bzw. Download). `beforeinstallprompt` wird für „📲 App
  installieren“ aufgehoben. Daten werden beim Verlassen gesichert.
- **`worker.js`:** Pyodide + Pakete laden, `/mgd` als IDBFS (IndexedDB) einhängen und laden, bei neuer Prüfsumme
  `programm.zip` dorthin entpacken (Nutzerdaten bleiben), `MGD_DATEN=/mgd/daten`, `import gans_ui`; jede Anfrage über
  `gans_ui.web_anfrage()` (Bytes/Uint8Array → Status, Kopf-JSON, Bytes), danach `web_weiter()` und Sichern (`syncfs`,
  gebündelt nach 0,4 s). Beim ersten Start gilt Englisch (seit 2.1 nicht mehr die Sprache des Geräts); Ladebildschirm
  (`app.js`, `localStorage` `mgd-sprache`) und die Meldung des Service Workers (`sw.js`, Cache `mgd-einstellungen`)
  folgen der im Programm gewählten Sprache, sobald es eine gibt.
- **Oberfläche (`AM_APP`, Klasse `am-app`; gilt dazu `AM_HANDY`):** untere App-Navigation **Karten · Neu · Lernen ·
  Drucken · Mehr** (Klasse `mit-app-navi`: in der App bis 860 px Breite, am Rechner/Handy-Zugang nur bei Touch bis
  860 px; die linke Leiste bleibt sonst unverändert), Blatt „Mehr“ mit den übrigen Bereichen und App-Aktionen,
  kompakte Kopfzeile, sichere Ränder (`env(safe-area-inset-*)`), Zurück-Geste schließt zuerst Fenster (Verlaufseinträge je
  Fenster). Hinweis „Als App installieren“ auf Meine Karten (14 Tage „Später“), Fenster mit Schritten und Skizzen
  (iPhone: Safari → Teilen → Zum Home-Bildschirm; Android ohne Angebot: Browser-Menü), „Sicherung & Speicher“
  (belegter Platz, dauerhaft gespeichert?, Alles sichern, Sicherung einspielen, Karten vom Rechner übernehmen).
  Über den Handy-Zugang mit bekannter `web_adresse`: Hinweis + QR-Code zur App. Am Rechner: Werkzeuge → „Am Handy öffnen“
  zeigt unten „📲 Als App aufs Handy“ (QR-Code + Adresse, ohne WLAN-Zugang), Prüfen & drucken → Digital lernen einen
  Knopf dazu. KI-Bilder: Knopf bleibt, Hinweis „nur am Rechner“.
- **Veröffentlichung und Installationsdateien:** GitHub Pages, öffentliches Repository `me-goos-ta-deutsch`, Branch
  `gh-pages` = Inhalt von `web-app/`; Adresse nur in `web_adresse.txt` (`https://lukasdiegans.github.io/me-goos-ta-deutsch/`).
  `veroeffentliche_webapp.py` (Arbeitsordner) legt Repository und Pages bei Bedarf an, pusht nur Geändertes (Verlauf bleibt,
  Bytes 1:1 wegen der Prüfsummen) und wartet, bis die neue Version ausgeliefert wird. Neben den Startdateien liegen
  `Me Goos-ta Deutsch - Android.html`, `… - iPhone.html`, `… - Google Pixel.html`: statisch ohne JavaScript (Sprache über
  `:target`, Standard Englisch), großer Link, QR-Code als Inline-SVG (`qr_code.py` – dieselbe Matrix wie `qrSvg()` der
  Seite), vier Schritte mit Skizzen, Mindestversionen (iOS/iPadOS 16.4 mit Safari, Android 10 mit aktuellem Chrome),
  Datenschutz, Sicherung, Update/Entfernen; gebaut mit `bau_webapp.py <Quelle> --installationsdateien`.
- **Download für den Rechner (seit 2.1):** ein Paket für Windows, macOS und Linux (das ZIP aus `bau_release.py`) als
  **GitHub-Release** `v<Version>` im selben Repository (Assets `Me-Goos-ta-Deutsch-<Version>.zip` + `SHA256SUMS.txt` im
  Format von `sha256sum`, seit 2.5 + `SHA256SUMS.txt.minisig`, siehe „Signierte Releases“); Branch `main` = Inhalt des Release-Ordners (Standard-Branch, die Repo-Startseite zeigt die
  README; `.gitattributes` `* -text`, `.command`/`.sh` ausführbar), Pages bleibt auf `gh-pages`. Kein Installer/Store
  (ohne kostenpflichtige Signatur blockieren Smart App Control und Gatekeeper ihn genauso). **Download-Seite**
  `web_adresse.txt` + `download/` (`https://lukasdiegans.github.io/me-goos-ta-deutsch/download/`): baut `bau_webapp.py`
  nach `web-app/download/` (`index.html` + `seite.js`; mit `--release-zip <ZIP>` Direktlink auf das Asset, Größe und
  SHA-256, sonst Link auf `…/releases/latest`). Englisch Standard, EN · DE · ES (Anker `#de/#es/#en`, sonst gemerkte Wahl
  in `localStorage`, nie die Gerätesprache), erkanntes System → großer Knopf + drei Schritte mit Skizzen + Hilfe zu
  SmartScreen/Smart App Control/Gatekeeper, „Was drin ist“, Handy-Abschnitt (QR), Fragen, Fuß mit Lizenz, Quellcode,
  Versionshinweisen und SHA-256. Ohne Skript: Englisch, alle drei Systeme. Nur eigene Quellen (Schrift/Symbol relativ aus
  dem App-Ordner, CSP `connect-src 'none'`), kein Tracking. Der Service Worker der App lässt `download/` durch (sonst
  bekäme ein Gerät mit installierter App die App statt der Seite); die Seite steht nicht in der Vorrat-Liste und ändert
  die App-Version nicht. Der Service Worker der App 2.0 kannte `download/` noch nicht und zeigte dort den Startbildschirm
  der App; dessen relatives `app.js` holt er übers Netz → `download/app.js` (Rettung, seit dem Fix vom 21.10.2026) übergibt
  an die wartende neue Version („weiter“) bzw. meldet den alten Service Worker nach 20 s ab und lädt neu (höchstens dreimal;
  Nutzerdaten der App bleiben; Text „Eine alte App-Version watschelt gerade hinaus …“ in de/en/es). Links: README oben, LIES MICH (Abschnitt Update, de/en/es), Hilfe → „Über dieses Programm“,
  App-Blatt „Mehr“ („Auch für den Rechner holen“). Veröffentlichen: `veroeffentliche_release.py <Release-Ordner> <ZIP>`
  (Arbeitsordner; `--probe` = Plan ohne Netz, `--ersetzen` für ein vorhandenes Release): prüft Ordner = ZIP und keine
  Nutzerdaten, pusht `main`, setzt Standard-Branch/Homepage, legt das Release als Entwurf an, lädt die Assets hoch,
  veröffentlicht es als „Latest“ und vergleicht das heruntergeladene Asset per SHA-256 (seit 2.5 auch die Signatur).
- **Signierte Releases (seit 2.5, `signatur.py`, nur Standardbibliothek):** `SHA256SUMS.txt` jedes Releases ist mit dem
  Schlüssel von Me Goos-ta Deutsch signiert – minisign-Format (Algorithmus `ED`: Ed25519 nach RFC 8032 über den
  BLAKE2b-512-Vorhash; `Ed` ohne Vorhash wird auch geprüft), 8-Byte-Schlüssel-ID, „trusted comment“ genau
  `me-goos-ta-deutsch v<V>` mit globaler Signatur. `signatur.SCHLUESSEL` = Haupt (ID `6885AC6ACBF317E0`) + Reserve (ID
  `01C92660376DB3D4`), nur öffentliche Teile. Signiert wird im Arbeitsordner mit `signiere_release.py` (Haupt-Schlüssel
  privat per Windows-DPAPI unter `%USERPROFILE%\MGD-Signatur`, nie im Repo/ZIP; Reserve nur offline als minisign-
  verschlüsselte Sicherung, scrypt); `veroeffentliche_release.py` signiert Pflicht und prüft gegen `signatur.py` des
  Release-Ordners vor jedem Netz, lädt das Asset hoch und prüft es öffentlich. Prüfbar mit dem Standard-Werkzeug:
  `minisign -Vm SHA256SUMS.txt -P <Schlüssel>`; die Download-Seite erklärt es unter „Echtheit prüfen“ (nur bei einem
  signierten Release, `bau_webapp.py --release-zip` mit `SHA256SUMS.txt` + `.minisig` neben der ZIP). Haupt verloren →
  mit der Reserve signieren und einen neuen Haupt-Schlüssel per Update ausliefern; beide verloren → einmal von Hand
  aktualisieren (Download-Seite). Das Python der Startdateien und Tool-Downloads haben feste SHA-256 im Programm (unverändert).
- **Nach neuer Version suchen (seit 2.2):** Knopf „🔎 Nach neuer Version suchen“ unter Hilfe → „Über dieses Programm“, seit
  2.4 auch unter Werkzeuge → „Programm aktuell halten“ (`#update-bereich`) und in der Fußzeile des Menüs („🔎 Nach Updates
  suchen“ → Werkzeuge, sucht sofort); alle über `sucheNeueVersion()` (die einzige Stelle mit `/api/neue-version`), nur
  am Rechner (in App und Handy-Zugang ausgeblendet; `POST /api/neue-version` in `NUR_RECHNER_WEGE`/`LAN_GESPERRT` → 403).
  **Nur ein Klick fragt** – nie beim Start, im Hintergrund, per Zeitgeber oder im Starter; nichts wird gespeichert.
  `gans_ui.neue_version()`: Konto/Repository nur aus `web_adresse.txt` (`https://<konto>.github.io/<repo>/`, sonst 409
  `kein_release` ohne Anfrage) → `GET https://api.github.com/repos/<konto>/<repo>/releases/latest` über
  `uebersetzer.http_json(…, hosts=("api.github.com",), max_antwort=200 KB)` (eigene Host-Liste, getrennt von den
  Übersetzungsdiensten; HTTPS mit Zertifikatsprüfung, keine Weiterleitung, 10 s, nur JSON). Ausgewertet werden nur
  `tag_name` (`v?Zahl.Zahl[.Zahl]`) und `published_at` (Datum); Vergleich als Zahlen-Tupel (2.10 > 2.9) → `{ergebnis:
  neuer|aktuell|voraus, version, datum, eigene}`, Fehler → `{ergebnis: fehler, code, meldung}` (`nv_netz`, `nv_zeit`,
  `nv_grenze` bei 403/429, `nv_noch_keins` bei 404, `nv_format`). Der Link „Zur Download-Seite“ kommt aus
  `downloadAdresse()`, nie aus der Antwort; dazu der Hinweis auf den Leitfaden-Abschnitt „Neue Version installieren“.
- **Update direkt im Programm (seit 2.4, `aktualisieren.py`, nur Standardbibliothek):** bis 2.3 hieß ein Update „ZIP in
  einen neuen Ordner entpacken + Karten übernehmen“ – danach lagen zwei Ordner da (bzw. derselbe Name). Jetzt, nur auf
  Klick und nur am Rechner (`/api/update` in `NUR_RECHNER_WEGE`/`LAN_GESPERRT`, Lauf-Art `update` in `NUR_RECHNER_LAEUFE`):
  ① „⬆️ Jetzt auf <V> aktualisieren“ (erscheint, wenn die Suche „neuer“ meldet und `update.moeglich`) → `POST /api/update
  {aktion: laden, version}` (Version `\d+.\d+[.\d+]`, muss neuer sein, sonst 409 `update_kein_neuer`) → Auftrag
  `aktualisieren.py --laden <V> --quelle https://github.com/<konto>/<repo>/releases/download --daten <Datenordner>`
  (Konto/Repo aus `web_adresse.txt`, nie aus einer Antwort; Weiterleitungen nur zu github.com,
  objects/release-assets.githubusercontent.com; nur eine neuere Version als die laufende): `SHA256SUMS.txt` (≤ 64 KB) →
  seit 2.5 `SHA256SUMS.txt.minisig` (≤ 4 KB, fehlt/ungültig/fremder Schlüssel/anderer „trusted comment“ → „Achtung …“, nichts
  geändert; Testschlüssel `MGD_UPDATE_TESTSCHLUESSEL` gilt nur mit `MGD_UPDATE_QUELLE=http://127.0.0.1:…`) →
  `v<V>/Me-Goos-ta-Deutsch-<V>.zip`
  (≤ 200 MB) → SHA-256 vergleichen → ZIP prüfen (jeder Eintrag unter `Me-Goos-ta-Deutsch/`, keine `..`/`\`/`:`/Links,
  ≤ 5000 Dateien / 500 MB, Pflichtdateien Startdateien + starter/gans_ui/gans_lernkarten, `VERSION` = <V>, keine
  Nutzerdaten) → nach `<Datenordner>/update/neu` entpacken → `bereit.json`. Ein gescheiterter Versuch lässt eine schon
  geladene Version stehen. ② „🔄 Jetzt neu starten und <V> übernehmen“ → `POST /api/update {aktion: anwenden}` (nur mit
  `bereit`, nur ohne laufenden/wartenden Auftrag, sonst 409) → eigener Prozess `aktualisieren.py --anwenden --daten …
  --wurzel <Programmordner> --pid <Oberfläche>` (gelöst wie beim Deinstallieren), dann beendet sich die Oberfläche. Der
  Prozess wartet auf ihr Ende (≤ 60 s; Windows über `WaitForSingleObject`), ersetzt jede Datei des Releases (alte Fassung
  vorher nach `update/alt`, jede Datei über `.tmp` + `os.replace`, Startdateien 0755; Fehler → alles zurück, neue
  Dateien wieder weg), schreibt `update/ergebnis.json` und startet die **Startdatei** (Windows eigenes Konsolenfenster,
  macOS/Linux ohne Terminal) – sie richtet bei Bedarf Python/Pakete ein wie beim ersten Start. Nie angefasst:
  `karten.csv`, `karten.bak.csv`, `ui_einstellungen.json`, `ideen.json`, `lernstand*.json`, `bilder/`, `ideen/`,
  `ausgabe/`, `_beispiele/`, eigenes Gänse-Bild, `modelle/realesrgan*.npz`. Nur in einem Programmordner
  (`programm_ordner_ok`: Startprogramm + Oberfläche, kein `.git`, kein `bau_release.py` daneben = Arbeitsordner) und nur
  beschreibbar, sonst `update.moeglich = false` und nur der Link zur Download-Seite. `/api/status.update` = `{moeglich,
  bereit, ergebnis}`; das Ergebnis meldet die Seite einmal („Update geklappt – willkommen in Version …“ bzw. Fehler +
  „die bisherige Version läuft weiter“) und quittiert mit `{aktion: gesehen}`. Der Web-App fehlt das Modul (sie
  aktualisiert sich über ihren Service Worker). Tests: `MGD_UPDATE_QUELLE` (nur `http://127.0.0.1:<port>`),
  `MGD_KEIN_BROWSER=1` (Neustart mit `--kein-browser`).
- **Rückgängig und Wiederholen (seit 2.4, `verlauf.py`, nur Standardbibliothek):** Jede Anfrage aus `VERLAUF_WEGE`
  (Kartenliste, Karte speichern/abhaken, Bild ändern/weg/zurück, Entwurf hinzufügen/prüfen/übernehmen/verwerfen,
  Gänse-Bild, KI-Bild übernehmen, Gans ergänzen, Werkzeuge, Ideen samt Bild/Wort/Aufnehmen, Wortliste, Import) läuft in
  `verarbeite()` als Schritt: vorher `.csv`/`.json` der eigenen Daten als Bytes, sonst Größe + Zeit; Dateien, die die
  Anfrage löschen, verschieben oder überschreiben will, sichert der Code vorher mit `_sichere(pfad)` (in `_aufheben`,
  `_gans_beiseite`, `_atomar`, `_beiseite`, beim Übernehmen/Verwerfen von Entwürfen …). Danach bekommt jede geänderte
  Datei Inhalt vorher/nachher (SHA-256, Kopie in `ausgabe/.verlauf/blobs`). Bereich: `karten.csv`, `bilder/` (mit
  `_entfernt`), `ausgabe/.entwuerfe`, `ideen.json` + `ideen/`, `assets/gans_hintergrund.*` + `assets/_alt`. `POST
  /api/rueckgaengig` bzw. `/api/wiederholen` → `{art, verlauf, karten}`; nur wenn jede betroffene Datei noch genau
  den erwarteten Inhalt hat, sonst 409 `vl_konflikt` und der Verlauf beginnt neu (nichts überschrieben); halb
  geschafft → alles zurück. Fehlt für eine geänderte Datei die Sicherung, wird der Verlauf geleert (nie halb zurück).
  Höchstens 30 Schritte bzw. 400 MB Kopien; die Kopfzeile `X-MGD-Verlauf` jeder `/api/`-Antwort trägt `{z, w, za,
  wa}`; `GET /api/verlauf` dasselbe. Gruppen (`X-GL-Gruppe`, ≤ 10 min, nur ohne Wiederholen-Schritte) fassen Tippen im
  selben Entwurf und „🌐 Alle übersetzen“ zu einem Schritt zusammen. Nicht dabei: Einstellungen, Sprache, Farben,
  Lernstand (eigene Rückgängig-Taste der Sitzung), Läufe; die App-Sicherung leert den Verlauf. Verlauf je Sitzung
  (beim Start und Beenden leer). Seite: ↶ ↷ in der Kopfzeile (Hover = was zurückgenommen würde), Strg/⌘+Z,
  Strg+Y/Strg+Umschalt+Z – nicht in Textfeldern, Fenstern oder der Lernsitzung; danach Karten, Entwürfe, Gänse-Bild und
  Ideen neu laden, Toast mit dem Gegenweg.
- **Jede Karte braucht ihre Gans (seit 2.4):** `gl.hat_gans()` = „gans“ oder „gäns“ irgendwo (casefold), `gl.mit_gans()`
  setzt sonst „Gans “ davor (leer bleibt leer). Angewandt beim Übernehmen eines Entwurfs (vor dem Dateinamen →
  `gans-…`), Speichern im Editor, Speichern der Kartenliste (nur geänderte Texte), Idee → Karte und Import; die
  Antwort trägt dann `gans_hinweis` (Toast). `karten_daten().meldungen` meldet ältere Karten ohne Gans (`k_ohne_gans`,
  `anzahl`) mit Knopf „Gans ergänzen“ → `POST /api/gans-ergaenzen` (ein Schritt, rückgängig machbar). Wortliste:
  „Die Gans ist alt“ bleibt, sonst wie bisher „Gans“ davor.
- **Vorher/Nachher-Vergleich (Fix 2.4):** Klicken mit leichtem Ziehen auf das Bild legte über das native Ziehen eines
  `<img>` ein neues Bild in „Bilder vorbereiten“ an. Jetzt: Bilder dort `draggable="false"` ohne Zeiger-Ereignisse,
  `dragstart` verhindert, Regler mit `pointercancel`; allgemein ist alles, was aus der Seite selbst gezogen wird
  (`innenZieh`), nie eine neue Datei – nur Dateien von außen landen in Schritt 1 bzw. an einem Ablage-Ziel.
- **App-Sicherung:** `GET /api/app-sicherung` (nur in der App) → ZIP mit Marke `me-goos-ta-deutsch-app-sicherung.json`,
  `projekt/` (karten.csv, bilder/, ideen/, ideen.json, lernstand*.json, ui_einstellungen.json, entwuerfe/) und `daten/`
  (Datenordner ohne Modelle und Pakete); `POST /api/app-sicherung` (rohe Bytes, ≤ 600 MB) prüft alles vorab (Marke,
  bekannte Orte, keine Ausbrüche, CRC) und ersetzt dann den ganzen Stand. Fremde ZIPs → Hinweis auf den Import.
- **Import einer Komplettsicherung** (auch am Rechner): liegt `lernstand.json` neben `karten.csv` und ist das Tool
  „Karten lernen“ aktiv, wird der Lernstand dazugenommen (je Lernkarte der neuere; `zahlen.lernstand`).
**Rückseiten-Vorschau ohne pypdfium2:** `leinwand.py` bildet die benötigten ReportLab-Zeichenbefehle auf einem Pillow-Bild
nach (3-fach überabgetastet; seit 2.1 auch `rotate` und offene Linienzüge mit runden Gelenken für die Gans);
`zeichne_rueckseite` läuft unverändert darauf (Abweichung zum pdfium-Bild im Mittel ≈ 1/255).
Ohne `leinwand.py` wie früher keine Rückseiten-Vorschau.

### 9.1 Automatische Übersetzung (`uebersetzer.py`)

Schlägt für den Text auf dem Bild das Wort auf Spanisch vor. Übersetzt wird der Teil nach „Gans“
(„Gans aufgeregt“ → „aufgeregt“). Es bleibt immer ein **Vorschlag**: Er landet nur in der Kartenliste, wenn er übernommen
wird (Feld, „Alle übernehmen“, „Speichern“; in der Tabelle mit 🌐), und ist dort als `uebersetzung=automatisch` markiert,
bis er im Reiter „Tabelle“ als geprüft abgehakt wird.

| Dienst | Adresse (fest) | Konto | Wofür |
|---|---|---|---|
| Wiktionary | `de.wiktionary.org/w/api.php` (MediaWiki-API, `action=query`, Seitentext) | nein | Einzelwörter: liest im deutschen Abschnitt die Übersetzungstabellen (`{{Ü-Tabelle}}`, `{{Ü\|es\|…}}`, auch alte Form mit `Ü-links/Ü-rechts`, Wendungen aus mehreren `{{Ü}}`, Merkmale wie „Mexiko“, „veraltet“); flektierte Formen über `{{Grundformverweis}}`; Reihenfolge der Bedeutungen, innerhalb einer Bedeutung Mexiko/Lateinamerika zuerst, andere Länder, Veraltetes und Unsicheres (`{{Ü?}}`) nach hinten; Vorschlag = die ersten zwei („viejo / anciano“), weitere als Auswahl mit Bedeutung |
| MyMemory | `api.mymemory.translated.net/get` (`langpair=de\|es-MX`, Rückfall `de\|es`) | nein (ca. 5000 Zeichen/Tag) | Wendungen und Wörter, die das Wörterbuch nicht kennt; Treffer mit Übereinstimmung ≥ 0,85 als Alternativen |
| DeepL | `api-free.deepl.com` bzw. `api.deepl.com` `/v2/translate` (`target_lang=ES-419`, Rückfall `ES`) | eigener kostenloser Schlüssel | beste maschinelle Übersetzung; Schlüssel im Kopf `Authorization: DeepL-Auth-Key …`, nie in der Adresse |

„Automatisch“ (Standard): bis zwei Wörter zuerst Wiktionary, sonst bzw. ohne Treffer DeepL (wenn ein Schlüssel
hinterlegt ist) oder MyMemory; Fehler eines Dienstes führen zum nächsten. Ergebnisse (auch „nichts gefunden“, 7 Tage)
werden 90 Tage im Benutzerordner gemerkt (`uebersetzungen.json`, höchstens 3000 Einträge). Schutzmaßnahmen siehe
Abschnitt 11. Einstellungen: `uebersetzung.json` im Datenordner (Zustimmung, Dienst, „automatisch“, DeepL-Schlüssel).
Option „Neue Karten automatisch übersetzen“: Neue Bilder (Schritt 1) und offene Karten (Schritt 2) bekommen den
Vorschlag gleich ins Feld – nacheinander, je Wort nur einmal.

**Erweitern – neue Funktionen erscheinen automatisch:**

| Was | Wo | Ergebnis in der Oberfläche |
|---|---|---|
| Neuer Schalter | `gans_lernkarten.baue_parser()`: `opt(gruppe, "--name", label=L(de, en, es), einheit="mm", help=L(…), …)`, in `konfig_aus()`/`main()` verwenden | Feld in der passenden Gruppe unter „Erzeugen“ (Ein/Aus, Auswahl, Zahl oder Text); neue Gruppe = neuer Abschnitt; mit `gruppe(…, reiter="bildverbesserung")` im Reiter Bildverbesserung |
| Neue Erzeugungsart | neue Auswahl bei `--nur` (mit `auswahl_labels`) und in `main()` behandeln | eigener Startknopf (Ausnahmen in `NUR_ANDERSWO` der Seite) |
| Neuer Übersetzungsdienst | `uebersetzer.DIENSTE` (feste Adressen) + Abruf-Funktion; `reihenfolge()` | erscheint unter Werkzeuge → Automatische Übersetzung |
| Neues Werkzeug | `gans_ui.py`: Funktion mit `@werkzeug(id, L(titel), L(beschreibung), L(knopf), art, zustand, tool=…)` | neue Zeile unter „Werkzeuge“ (mit `tool` im Tools-Bereich statt doppelt) |
| Neues Tool | `tools.TOOLS`: Texte `L(…)`, `da`, `belegt`, `auftrag` (→ `starte_lauf`), `entferne`, `laden`/`nutzt` | Karte im Tools-Bereich, Erstabfrage, `brauchtTool()` |
| Neue Prüfung | Code + `L(…)`-Text in `PRUEF_MELDUNGEN`, in `analysiere_bild`/`pruefe_karte` melden | erscheint in der Prüfliste |
| Neue Sprache | `SPRACHEN` ergänzen, alle `L(…)`-Texte, `TXT` in `ui/index.html`, `LEITFADEN_<xx>.md` | Knopf in der Sprachwahl |
| Neues KI-Modell | Eintrag in `ki_modelle.KATALOG` (URL, SHA-256, Netz) | Laden per Kommandozeile/Werkzeug |

### 9.2 Erweiterungen (`erweiterungen.py`, eingebunden von `gans_ui.py`)

Fehlt `erweiterungen.py`, läuft die Oberfläche wie in 1.5 (die Adressen unten antworten dann mit 404, die Seite blendet
die Fenster einfach nicht ein). Alles erscheint ohne zusätzliche Fläche auf den Seiten: Fenster (Pop-ups) über der
Ansicht, ein Reiter „Ideen“ unter „Neue Karte“ und vier Zeilen unter „Werkzeuge“ (Art `dialog`).

| Funktion | Bedienung | Server | Regeln |
|---|---|---|---|
| Lade-Ente | erscheint unten links, wenn eine Anfrage länger als 400 ms dauert; in Tabelle, Bildverbesserung, Ideen, Hilfe, Schritt 4 und beim Hochladen an Stelle des Inhalts; im laufenden Protokoll statt „läuft“ | – | SVG + CSS-Animation, ohne Bewegung bei `prefers-reduced-motion`, nicht im Druck |
| Tabelle „Kompakt“ | Umschalter Bearbeiten/Kompakt (gemerkt im Browser); Spalten Nr., Vorderseite (Deutsch), Rückseite (Spanisch), Notiz, Prüfung (✓ geprüft · automatisch – prüfen · ☐ prüfen · – kein Wort); Klick auf Zeile → Bearbeiten | `GET /api/tabelle` | Filter, Suche, Sortieren gelten mit; Druck: feste Spaltenbreiten, eine Zeile je Karte, Kopf auf jeder Seite |
| Export | Meine Karten → „⇅ Import / Export“: alle oder nur gedruckte Karten | `GET /api/export?umfang=alle\|aktiv` → ZIP (`karten.csv` wie im Projekt, `bilder/`, `LIES_MICH.txt`) | nur mit Sitzung; nur einfache Bildnamen, keine Links |
| Import | Datei wählen/ziehen → Vorschau (neu · anders · gleich · Fehler) → „Meine behalten“ oder „Durch den Import ersetzen“ | `POST /api/import` (rohe Bytes, ≤ 500 MB, in `ausgabe/.import/`, 1 Tag), `POST /api/import-uebernehmen {id, ersetzen}`, `POST /api/import-verwerfen` | ZIP: ≤ 5000 Einträge, entpackt ≤ 1,5 GB, CSV ≤ 5 MB; nur `bilder/<einfacher Name>` mit Bildendung; Bilder wie Schritt 1 (≤ 40 MB, ≤ 60 MP, kein HEIC, `verify()`); Texte ohne `= + - @`; ersetzte Bilder → `bilder/_entfernt/`; CSV über die normale Speicherung (`karten.bak.csv`, atomar) |
| Ideen | Reiter „Ideen“: eigene Ideen (Bild, Wort und/oder Bildidee) + unfertige Karten (Entwürfe, offene Karten, Bilder ohne Zeile); „Als Karte aufnehmen“. Je Idee: Bildfläche (leer = klickbar), Feld **„Bildidee“** (≤ 300 Zeichen, gespeichert beim Verlassen), „🖼️ Bild wählen …“ (wie Klick/Hineinziehen → GANS-Bild gestalten, Format Karte quer, Text der Idee) und „🪄 Mit KI erzeugen …“ (KI-Fenster mit Ziel-Idee, Wort und Bildidee; ohne `ki_bild.py` ausgeblendet, ohne Tool Rückfrage) | `GET /api/ideen` (je Idee auch `bild_idee`), `POST /api/idee {id?, de, es, notiz, es_auto?, bild_idee?}` (`bild_idee` ändert sich nur, wenn mitgeschickt; eine Bildidee allein reicht für eine neue Idee), `GET/POST /api/idee-bild?id=`, `POST /api/idee-weg\|idee-zurueck\|idee-aufnehmen` | Ablage `ideen.json` + `ideen/` (wie `karten.csv` eigene Daten, beim Update übernommen); Aufnehmen = Entwurf anlegen + alle Prüfungen von Schritt 1/2 + übernehmen; Namenskonflikt → Frage „ersetzen“; Verwerfen mit Rückgängig (`ideen/_entfernt/`); `bild_idee` wie alle Texte ohne `= + - @`, Leerraum zusammengefasst, reist mit Export/Import (ältere Exporte ohne Feld lassen die vorhandene stehen) und zählt für Wortlisten-Rückgängig als eigene Änderung (Fingerabdruck sonst wie vor 2.3) |
| GANS-Bild gestalten | Fenster: Foto, Ausschnitt (Quadrat/Karte quer/Hochformat), Ziehen = verschieben, Mausrad/Regler = Zoom; Text „GANS “ + Eingabe, immer GROSS, verschiebbar, Größe, Schrift (Standard Poppins Bold), Farbe (Standard weiß mit dunklem Rand) | Ergebnis (JPEG 93 %, lange Seite 1200–2400 px) über `POST /api/entwurf?name=Gans <text>.jpg` (→ Schritt 1) oder `POST /api/idee-bild`; geöffnet mit `karte` (aus dem KI-Fenster im Karten-Editor) heißt der Hauptknopf „Für diese Karte übernehmen“ → Entwurf mit `karte=` wie „Bild ändern“; geöffnet aus einer Idee (`idee` = id, "" = neue Idee): „Für diese Idee übernehmen“ + „Bild unverändert übernehmen“ (die gewählte Datei ohne Zuschnitt und Text, ohne Text-Pflicht) → `POST /api/idee-bild`; Text der Idee nur, wenn sie noch keinen hat | Bearbeitung nur im Browser (Canvas, keine fremden Adressen); Dateiname = `dateiname_aus_text("Gans <text>")`, z. B. `gans-sehr-heiss.jpg` |
| Wortliste (seit 2.2) | Reiter „Ideen“ → „📋 Wortliste …“ (Fenster): Datei wählen/ziehen (`accept` .txt/.csv/.tsv – der Server verlässt sich nie darauf) oder Text einfügen + „Prüfen“, Format-Beispiele aufklappbar; ≤ 1 MB schon in der Seite → Vorschau: „Erkannt: UTF-16 · Semikolon · mit Kopfzeile“, Optionen (Trennzeichen, erste Zeile, eine Spalte = Deutsch/Kartensprache, Spalten tauschen, „Gans“ davor – jede Änderung prüft entprellt neu, Häkchen gehen dann sichtbar auf den Vorschlag zurück), Zahlen (neu · schon da · fehlerhaft · mit Hinweis), Tabelle Nr. · Text auf dem Bild · Wort · Notiz · Status-Chip (neu · doppelt in der Liste · schon Idee · schon Karte · fehlerhaft, dazu Text und Hinweise) · Häkchen (fehlerhafte nicht wählbar), am Handy (≤ 600 px) als Liste; jeder Text über `esc()` → „n Ideen anlegen“ (Doppelklick-Sperre; 409 → Vorschau neu) → Toast „n neue Ideen – ein schöner Fang!“ mit „Rückgängig“ (9 s) und Tipp „🌐 Alle übersetzen“. **„🌐 Alle übersetzen“** in der Titelzeile (nur sichtbar, wenn eine Idee Deutsch, aber kein Wort hat): `alleUebersetzen` mit derselben Zustimmung wie überall, je Idee `POST /api/idee-wort {id, es}` → `{gefuellt, …ideen}` (trägt nur ein, wenn das Wort beim Speichern noch leer ist, als „automatisch – prüfen“ `es_auto`; unveränderte Wortlisten-Ideen behalten ihren Fingerabdruck), Abbruch bei Fehler/Tageskontingent mit „n von m“ | `POST /api/wortliste-pruefen?trenner=&kopf=&tauschen=&einspaltig=&gans=` (rohe Bytes ≤ 1 MB) → `{zeilen:[{nr, roh, de, wort, notiz, status, text, hinweise, wahl}], erkannt:{kodierung, trenner, kopf, getauscht, kopf_sprache …}, hinweise, zahlen, zs, zs_name}`; `POST /api/wortliste-uebernehmen {zs, zeilen:[{nr, de, wort, notiz}]}` → `{angelegt, uebersprungen, wl, …ideen}`; `POST /api/wortliste-rueckgaengig {wl}` → `{entfernt, geaendert, schon_karte, …ideen}` | `erweiterungen.wortliste_lesen()` in Stufen: ① Dateiart (ZIP/xlsx, PDF, altes Office, RTF, Bilder → „als CSV UTF-8 oder .txt speichern“) ② Kodierung (BOM UTF-8/UTF-16 LE/BE, UTF-16 ohne BOM am NUL-Muster, UTF-8 streng, sonst Windows-1252 + Hinweis, Binärdaten → „kein lesbarer Text“) ③ NFC, alle Zeilenenden, Nullbreiten/weiches Trennzeichen weg, besondere Leerzeichen → Leerzeichen, Steuerzeichen weg ④ leere Zeilen, `#`-Kommentare, Listenzeichen nur mit Leerzeichen danach („-los“ bleibt) ⑤ Trenner auto (Tab > `;` > ` = ` > ` - `/` – ` > `,`, ≥ 60 % der Zeilen; `csv` für Tab/`;`/`,`) oder gewählt ⑥ Kopfzeile (alle Zellen bekannte Namen: Deutsch/Notiz/Sprachnamen und Codes aus `sprachen.SPRACHEN`; Reihenfolge aus dem Kopf, andere Sprache als die Kartensprache → Hinweis) ⑦ 1 Spalte = Deutsch (oder Kartensprache), 2 = + Wort, 3 = + Notiz, mehr → fehlerhaft; „tauschen“ ⑧ trimmen, typografische Anführungszeichen außen weg ⑨ „Gans“ davor („ganz alt“ → „Gans alt“, nur „Gans“ → fehlerhaft) ⑩ Prüfen (`= + - @`, Längen 120/300/300 → fehlerhaft statt kürzen, Deutsch ohne Buchstaben → fehlerhaft, fremde Zeichen bzw. ä/ö/ß bei es → Hinweis) ⑪ doppelt (Deutsch über `wort_schluessel`, Wort über `wort_schluessel_zs` – nicht-lateinisch NFKC + casefold) gegen frühere Zeilen, Ideen und Karten → nicht vorausgewählt. Wort = Kartensprache (andere Sprache: vorher die Kartensprache wechseln). Grenzen 1 MB / 500 Wortzeilen → Meldung, nie abschneiden. Übernehmen ist zustandslos: jede Zeile erneut ⑩–⑪ gegen den Stand jetzt, `zs` ≠ Kartensprache → 409 `zs_geaendert`, alles in einem Schreibvorgang unter `_ideen_lock` (gleichzeitige Übernahmen ohne Doppelte), Ideen mit `wl` + Fingerabdruck `fp`, `es_auto` leer, Reihenfolge der Liste oben; `ideen.json` → `wortlisten` (letzte 20). Rückgängig entfernt nur unveränderte Ideen ohne Bild (Fingerabdruck gleich); auch über den Handy-Zugang und in der Web-App |
| Programmstart | Frage beim ersten Öffnen (nur wenn vom Startprogramm gestartet), änderbar unter Werkzeuge: Standard-Browser · bestimmter Browser · eigenes Fenster | `GET/POST /api/start-einstellung` → `start.json` im Datenordner; `starter.oeffne_browser` liest sie | nur fest bekannte Browser an festen Orten; eigenes Fenster = Chromium-Browser mit `--app=<Adresse>`; nicht vorhanden → Standard-Browser |
| Deinstallieren | letzter Reiter „Deinstallieren“: ① Komplettsicherung herunterladen ② „Deinstallieren …“ → Fenster „Bist du sicher?“ mit Warnung, Häkchen, dann „Endgültig deinstallieren“ | `POST /api/deinstallieren {bestaetigt: true}` → `starter.py --deinstallieren` | beendet die Oberfläche, entfernt Symbole, danach Datenordner und Programmordner; verweigert, wenn der Ordner nicht eindeutig das Programm ist (Startdatei + `Programm/starter.py`, nicht Benutzer-, Download-, Desktop-, Dokumente-Ordner – auch lokalisiert, aus `user-dirs.dirs` bzw. den Windows-Known-Folders – oder Laufwerk) |
| Handy-Zugang | Werkzeuge → „Am Handy öffnen (WLAN)“: Schalter, QR-Code, Adresse, 6-stellige PIN, Restzeit | zweiter Server auf der privaten WLAN-Adresse, Port gemerkt in `handy-port.txt` (Datenordner; belegt → anderer freier Port); `GET/POST /api/lan`, `POST /lan-pin` | standardmäßig aus; nur Host `<ip>:<port>`; ohne Cookie PIN-Seite; aus nach 120 min, 5 falschen PINs oder beim Beenden; über das Handy gesperrt: beenden, deinstallieren, öffnen, Start- und Handy-Schalter sowie Werkzeuge mit `nur_rechner` (Ordner öffnen, CSV extern, Programmstart) – die Seite (`AM_HANDY`, Klasse `am-handy`) blendet sie aus; Touch-Regeln (Tippflächen ≥ 44 px, Eingaben 16 px, `…_touch`-Texte); Datei-Felder mit konkreten Bildtypen (iPhone wandelt HEIC dann in der Regel in JPG); Kopieren ohne Zwischenablage-Schnittstelle; die Lauf-Anzeige übersteht ~30 s Verbindungsaussetzer und holt nach Display-Sperre auf |
| Warteschlange | Höchstens **ein** Hintergrundprozess (Erzeugen, Bildverbesserung, Selbsttest, Tool laden, KI-Bild); weitere Aufträge warten und starten automatisch nacheinander (nur im Arbeitsspeicher). Kopfzeile „⏳ n“ → Fenster: laufender Auftrag (Fortschritt, Dauer, Abbrechen), wartende mit Platz, ▲ ▼ „Als Nächstes“ ✕, „Alle wartenden entfernen“ (Rückfrage), „Zuletzt erledigt“ (10, ✓/✕, Ergebnis/Protokoll). Startknöpfe bleiben frei → Toast „In der Warteschlange – Platz n“; KI-Fenster zeigt „wartet (Platz n)“. Gleicher Auftrag (Art + Befehl) wird nicht doppelt eingereiht; scheitert der Start (z. B. KI-Modell fehlt), landet er als ✕ unter „Zuletzt erledigt“. Beenden fragt nach, Beenden/Deinstallieren verwerfen wartende und stoppen den laufenden | `gans_ui.Warteschlange` (Start des nächsten per Rückruf am Ende von `Lauf._lies`); `POST /api/lauf` → bei leerer Schlange wie bisher `laeuft: true`, sonst `{wartet, position, id, titel, art}`; `GET /api/lauf[?id=]` (laufender bzw. letzter Auftrag + `warteschlange`, `aktiv`); `GET /api/warteschlange` → `{aktiv, wartend, fertig}`; `POST /api/warteschlange {aktion: hoch\|runter\|als-naechstes\|entfernen\|leeren, id}`; `POST /api/lauf-stopp` bricht den laufenden ab; `/api/status` → `warteschlange` |

Selbsttest der Erweiterungen: `python3 test_erweiterungen.py` (534 Prüfungen in den Abschnitten E1–E52, in einer Kopie,
ohne Internet, ohne echten Browserstart, ohne echtes Deinstallieren; mit Mac-, Linux- und Handy-Prüfungen, der
KI-Faltung und den KI-Bildern: Rechenkern gegen eine Lehrbuch-Fassung, Prompt, Server-Lauf, Oberfläche, Plattformen;
der Hilfe: Markdown-Umwandler mit Sonderfällen, jede mitgelieferte `.md` in < 2 s, Spezifikation über den Server;
der Sprachbezeichnung: sichtbar nur „Spanisch“, Erklärung „wie in Mexiko gesprochen“ an den zentralen Stellen; der Warteschlange: Reihenfolge, Umsortieren, Abbrechen, nie zwei Prozesse gleichzeitig, Fehler beim Start, `/api/lauf` rückwärtskompatibel; der Tools: Katalog, Übernahme, Installieren über die Warteschlange, Deinstallieren nur der Tool-Dateien, Löschschutz, Sperre, Erstabfrage, Starter ohne Download; der Sprachen: Katalog, Schriften mit Prüfsumme, Laden/Entfernen,
Zielsprache, Spalten je Sprache, Wiktionary je Schriftsystem, Zeichenprüfung, Dienst-Codes, `{zs}` in Seite/Python/Leitfäden, Prüfregeln je Kartensprache, mehrere Rückseiten, Zielsprache entfernen; des Lernens: FSRS-6 gegen py-fsrs, Lernschritte, Tageswechsel, Limits, Fuzz, Rückgängig, Stapel, Export/Import, `.bak`, Zurücksetzen über alle Speicherwege, Lern-Oberfläche und Sitzungsablauf; der Web-App-Grundlage:
`verarbeite()` gleich wie über HTTP, Läufe im selben Prozess samt Abbruch, Weichen mit nachgebildetem `sys.platform`,
Rückseiten-Vorschau mit der Pillow-Leinwand; der Handy-App: App-Adresse, Worker-Schnittstelle, App-Sicherung, Weichen, Real-ESRGAN aus dem App-Ordner, Lernstand beim Import, Bau mit `bau_webapp.py` (Positivliste, Manifest, Symbole, Liste des Service Workers, `AM_APP`); der Installationsdateien: vorhanden, ohne Skript, Adresse = `web_adresse.txt`, QR-Code = neu erzeugte Matrix und mit eigenem Leser nach Norm lesbar (Versionen 1–6), drei Sprachen; der Fehleranalyse: Oberflächen- und Python-Texte vollständig in drei Sprachen, jede Adresse in dieser Spezifikation, Leitfäden gleich gegliedert, Einstellungen bei gleichzeitigen Anfragen, freundliche Fehlertexte, Generator-Hilfe in einer Sprache, Touch-Tippflächen; Englisch vor der Installation und Tools-Teil-Knopf (E34); der
Rückseiten-Gans (E35): Platz unten rechts frei vom Text in allen Schriftsystemen, Größenstufen, ruhige Fläche hinter dem
Wort, Textgrößen wie 2.0, Leinwand = pdfium, sauberer Anschnitt im Druck mit Beschnitt; Download-Seite + Release-Werkzeug (E36); `--status` des Startprogramms ohne Wahl Englisch (E37); Werkzeuge der automatischen Tests auf GitHub-Rechnern (E38: `ci_lauf.py --probe` ohne Netz, Sperre auf Branch `ci`, `frischtest.py` nur auf GitHub-Rechnern, `tests.yml` statisch, Release-ZIP ohne `.github`); Browser-Test, Release-Prüfung und Release-Schranke (E39: `browser_test.py` mit Abläufen in Chromium, Firefox und WebKit ohne feste lange Wartezeiten, `release_pruefung.yml` (Push auf `main`, wartet auf das passende Release) und Browser-Job statisch, Playwright-Download mit Wiederholung, `ci_lauf.py` mit `web-app/` bzw. Probe der Release-Prüfung, `veroeffentliche_release.py --probe` nur mit grünem CI-Lauf für genau diesen Inhalt, `--ohne-ci` nur mit Begründung); der Wortliste (E42: jede Stufe mit eigenen Fällen – Kodierungen, NFD, Zeilenenden, Trenner, Kopf, Spalten, „Gans“, Formeln, Längen, Doppelt auch in nicht-lateinischen Schriften –, Grenzen, 200 Zufalls-Byte-Folgen, API prüfen → übernehmen → rückgängig, veraltete Vorschau, gewechselte Kartensprache, gleichzeitige Übernahmen); der Wortlisten-Oberfläche (E43: Texte de/en/es samt dynamischen Schlüsseln und `_touch`, `esc()` in der Vorschau, `accept`-Liste, „Alle übersetzen“ über `alleUebersetzen` + `/api/idee-wort` mit nachgebildetem Dienst – Kontingent nach 3 → 3 gefüllt, Rest leer, eigenes Wort bleibt, Rückgängig danach); des Fixes 2.2 (E44: Rettung `download/app.js` für eine App von vor 2.1 – Weg über den alten Service Worker, Übergabe/Abmelden, Texte de/en/es; Release-ZIP gegen `main` Datei für Datei); der Ideen-Bilder (E45: ein Bild-Knopf → GANS-Werkzeug mit „unverändert“, KI-Bild mit Ziel-Idee – Lauf-Meta, Übernehmen in eine vorhandene/neue Idee, ungültige id, Handy-Zugang –, Feld „Bildidee“ über API, Export/Import und Wortlisten-Fingerabdruck, Texte de/en/es); des GitHub-Auftritts (E50: Community-Dateien für `.github/` – Sicherheitsrichtlinie, Mitmachen, Verhaltenskodex, Issue-Formulare, PR-Vorlage – vorhanden, mit Kurzfassung de/es, Links nur auf das eigene Repository bzw. `web_adresse.txt`, ohne E-Mail-Adressen; `repo_einstellungen.py --probe` mit vollständiger Stufe 1 ohne Netz); der signierten Releases (E51: Ed25519 gegen die Testvektoren 1–3 aus RFC 8032, minisign-Format mit festem Testschlüssel, Ablehnung geänderter Summen/Signaturen/Kommentare, fremder Schlüssel und falscher Versionen, `laden()` nur mit gültiger Signatur, Testschlüssel nur mit 127.0.0.1; im Arbeitsordner `signiere_release.py` samt Sicherung, Signatur-Pflicht in `veroeffentliche_release.py`, „Echtheit prüfen“ auf der Download-Seite – ohne Arbeitsordner bzw. außerhalb von Windows entfallen diese 4); der festen Paketfassungen (E52: Lock-Dateien nur mit `==` und SHA-256 je Rad, Räder für alle Plattformen, Abhängigkeiten vollständig, Starter und Sprachen-Tool rufen pip mit `--require-hashes` und Lock, Fingerabdruck folgt dem Lock, `bau_lock.py --probe` offline – entfällt ohne Arbeitsordner –, echter `pip --dry-run` gegen die Locks und eine falsche Prüfsumme wird abgelehnt – entfällt ohne Internet); ohne geladenes KI-Bildmodell entfallen 9 Prüfungen mit dem echten Modell, ohne Heimnetz die WLAN-Prüfungen, ohne Internet beim ersten Lauf die 13 Prüfungen mit echten Sprachpaketen, ohne `bau_webapp.py` (nur im Arbeitsordner) die 7 Bau-Prüfungen in E31 und (auch ohne `bau_release.py`/`veroeffentliche_release.py`) die 11 in E36, ohne `web-app-quelle\` 1 Prüfung in E34, ohne `ci_lauf.py`/`ci\` (nur im Arbeitsordner) die 5 in E38, die 7 in E39, die 3 in E44 und die 5 in E50).

### 9.3 KI-Bilder (`ki_bild.py`, optional eingebunden von `gans_ui.py`)

Erzeugt realistische Gänse-Bilder für neue Karten oder als neues Bild einer vorhandenen Karte – offline, in reinem NumPy
(keine Zusatzpakete, keine neuen DLLs). Fehlt die Datei, fehlen nur die KI-Knöpfe (`/api/status` → `ki_bild: false`).

**Modell** (Tool „KI-Bilder“ unter Werkzeuge → Tools, `python3 ki_bild.py --laden`): Segmind Vega (SDXL-Destillat, 745 Mio.
Parameter) + VegaRT (LCM-LoRA), beide Apache-2.0, dazu TAESDXL (MIT) für die Vorschau – 14 Dateien, 3 539 092 079 Byte,
von Hugging Face mit **fester Revision**, je Datei SHA-256 (bzw. Git-SHA-1 für kleine Textdateien); fortsetzbar (HTTP-Range
auf `.part`), Platzprüfung, erst nach Prüfsumme an den endgültigen Namen. Ort: `<Datenordner>/modelle/ki-bild`
(Umgebungsvariable `MGD_KI_BILD` für Tests); nie im Programmordner, Release oder Projekt-ZIP.

**Rechenweg:** `SafeTensors` (Kopf geprüft, Daten nur eingeblendet) → CLIP-Tokenizer (BPE) → Text-Encoder CLIP ViT-L +
OpenCLIP ViT-bigG (vorletzte Schichten 77 × 2048, Satz-Einbettung 1280) → UNet (Aufbau nur aus `unet_config.json`;
SDXL/Vega mit `text_time`, SD 1.5 ebenfalls) mit **fest eingerechnetem VegaRT** (W + α/r · up·down, Gewichte als float16
im Speicher, beim Rechnen float32) → **LCM-Verfahren**, 4 Schritte (Zeitschritte 999/759/499/259 wie diffusers) →
VAE-Decoder (SDXL, beste Qualität) bzw. TAESDXL (Vorschau je Schritt). Ausgabe 896 × 640 px (≈ Karte 88 : 63).
Elementweise Rechnungen laufen stückweise in Threads (höchstens 8), Faltungen als im2col-Matrixprodukte in Streifen
(128 MB); Zufall ohne `numpy.random` (SplitMix64 + Box-Muller, gleicher Startwert = gleiches Bild).
Gemessen (i5-1334U, 16 GB): ca. 70 s je Bild (Text 2 s, Vorbereiten 4 s, Schritte 30 s, VAE 33 s), Spitze 3,1 GB.

**Prompt:** Vorlage `PROMPT_STANDARD` („realistic wildlife photograph of a domestic goose, {description}, natural
light, sharp focus on the goose, detailed feathers, calm simple background“); `{description}` = Beschreibung (≤ 300
Zeichen, `{}` neutralisiert), `{word}` = Wort der Karte (im Standard nicht benutzt – das Wort setzt danach „GANS-Bild
gestalten“). Schalter **„Keine Menschen“** (Standard an): positiver Zusatz „the goose is alone, empty quiet
surroundings“ (ohne die Wörter people/person) + Negativ-Prompt (Text, Zeichnung, Verformungen + Menschen) mit
Classifier-Free-Guidance 1,5 nur in Schritt 1–2 (stärker wird LCM grell und fehlerhaft). Eigene Fassung (Vorlage +
Negativ, ≤ 600 Zeichen, muss `{description}` enthalten; auch deutsche/spanische Platzhalter) und der Schalter liegen in
`ui_einstellungen.json` → `ki_bild`. CLIP liest 75 Token; die Oberfläche zeigt die Länge.

**Server:** `GET /api/ki-bild` (Zustand, Einstellungen, Standard), `POST /api/ki-bild-prompt` (`{vorlage, negativ}`,
`{zuruecksetzen}`, `{ohne_menschen}`), `POST /api/ki-bild-text` (fertiger Prompt + Token), `POST /api/lauf
{art: "ki-bild", beschreibung, wort, ohne_menschen, karte?, idee?, startwert?}` (`idee`: id einer Idee oder "" = neue Idee, nur gemerkt – in der Meta-Datei und im Lauf-Status `ki.idee`; `karte` geht vor; ungültig → 400) → Prozess `ki_bild.py --erzeugen=<prompt>
[--negativ=…] --startwert=… --aus=ausgabe/.ki-bild/<id>.png --vorschau=<id>.jpg`; der Lauf-Status enthält `ki` (Prozent
aus den Zeilen „  NN %“, Vorschau-Stand, Startwert, fertig – beide Zeilenarten erscheinen nicht im Protokoll).
`GET /api/ki-bild-bild?id=&art=vorschau`, `POST /api/ki-bild-uebernehmen {id, karte?, idee?}` → JPEG 95 % → Entwurf (neue Karte
mit Text = Wort oder Bild-Ersatz für `karte`); mit `idee` (nur ausdrücklich) direkt das Bild dieser Idee bzw. einer neuen (`erweiterungen.idee_bild_setzen`, Text = Wort nur, wenn die Idee keinen hat) → `{id, …ideen}`. `ausgabe/.ki-bild/` räumt sich selbst auf (> 14 Tage oder mehr als 30).
`POST /api/ki-bild-uebersetzen {text}`: Beschreibung → Englisch (`uebersetzer.beschreibung_englisch`, nur nach
Zustimmung, MyMemory bzw. DeepL). Über den Handy-Zugang ist alles erlaubt; gerechnet wird am Rechner.

**Oberfläche:** Fenster „Gans mit KI erzeugen“ (Schritt 1, Karten-Editor „🪄 Mit KI …“, Ideen „🪄 Mit KI erzeugen …“ – dann mit Hinweis „Für deine Idee …“; beim Start wird die Beschreibung als Bildidee der Idee gemerkt): GANS + Wort, Beschreibung
(Englisch, „🌐 Ins Englische“), Schalter, Hilfe „So klappt’s“, „Standard-Prompt bearbeiten …“; rechts Vorschau mit
Fortschritt und Abbrechen, danach „✍️ Wort aufs Bild setzen …“ (→ GANS-Bild gestalten, Format Karte quer), „Ohne Wort
als neue Karte“, „Für diese Karte übernehmen“ bzw. „Ohne Wort für die Idee übernehmen“, „🎲 Neu würfeln“, Herunterladen. Das Ziel (Karte/Idee) bleibt beim Schließen erhalten (Toast „Ansehen“, Warteschlange „Zuletzt erledigt“).

**Befehlszeile:** `python3 ki_bild.py --erzeugen "<englische Beschreibung>" [--negativ …] [--startwert N] [--schritte 4]
[--cfg 1.5] [--cfg-schritte 2] [--breite 896] [--hoehe 640] [--schnell] [--aus datei.png] [--vorschau datei.jpg]`;
`--status`, `--laden`. `MGD_KI_HALB=0` erzwingt float32-Gewichte (gleich schnell, 4,4 GB).

### 9.4 Tools (`tools.py`, optional eingebunden von `gans_ui.py`)

Ein **Tool** ist eine optionale Funktion, die nicht vorinstalliert ist (spart Platz). Reiter und Knöpfe bleiben immer
sichtbar; will man ein fehlendes Tool nutzen, fragt die Oberfläche nach (Nutzen, Größe, Speicherort, Dauer), lädt es über
die Warteschlange und macht danach mit der ursprünglichen Aktion weiter. Deinstallieren löscht nur die Dateien des Tools,
danach ist es wieder installierbar. Programmcode wird nie nachgeladen – nur Modelle und Daten mit Prüfsumme.

| id | Tool | Installieren | Größe | Ort | installiert, wenn |
|---|---|---|---|---|---|
| `bildverbesserung` | Real-ESRGAN (Teile `x4` = Standard, `x2` = schneller) | Lauf `ki_modelle.py --laden <id> --vorrat <Daten>/modelle`; liegt dort schon eine Kopie, wird sie ohne Download zurückgeholt | ca. 64 MB Download, 2 × 30 MB belegt | `Programm/modelle/` + Kopie `Daten/modelle/` | eine `realesrgan-*.npz` da |
| `uebersetzung` | Automatische Übersetzung (9.1) | Zustimmung (sonst 409 `zustimmung`), Eintrag in `tools.json` | kein Download | `Daten/uebersetzung.json`, `uebersetzungen.json` | Zustimmung erteilt oder aktiviert |
| `ki-bild` | KI-Bilder (9.3) | Lauf `ki_bild.py --laden` (fortsetzbar) | ca. 3,5 GB | `Daten/modelle/ki-bild` | alle 14 Dateien geprüft |
| `sprachen` | Rückseiten-Sprachen (Teil je Sprache, Standard-Teil `en`) | lateinisch sofort; sonst Lauf `sprachen.py --laden <code>` (fortsetzbar) | 0–17 MB je Sprache | `Daten/sprachen/<code>`, `Daten/sprachen/_pakete` | mindestens eine weitere Sprache vollständig |
| `lernen` | Karten lernen (FSRS, `lernen.py`) | Eintrag in `tools.json` (Aktivierung) | kein Download | `lernstand.json` neben `karten.csv` | aktiviert |
Ohne Tool bleibt der Kern vollständig (FSRCNN/Lanczos, Druck wie bisher). Vorhandene Modelle und eine erteilte Zustimmung
aus 1.6 zählen sofort als installiert. **Erstabfrage:** einmalig, nur wenn noch etwas fehlt – im Willkommens-Assistenten
als Schritt „Tools“, sonst als Fenster beim Öffnen (nicht über den Handy-Zugang); nichts vorausgewählt, „Später“ bzw.
Schließen merkt die Antwort ebenso. **Löschschutz:** nur bekannte Dateinamen in genau diesen Ordnern, nie rekursiv, nie
Karten/Bilder/Ideen; liegt das KI-Bildmodell außerhalb des Datenordners (`MGD_KI_BILD` in Tests/Probe), wird es nur
abgemeldet (`tools.json` → `abgemeldet`), nicht gelöscht. Deinstallieren wird verweigert (409), solange ein Auftrag des
Tools läuft oder wartet (Download bzw. Verbesserung/Erzeugen bzw. KI-Bild).

**API:** `GET /api/tools` → `{tools: [{id, symbol, titel, nutzen, art: download|aktivierung, groesse, platz, belegt,
installiert, zustand: nicht|angefangen|wartet|laeuft|installiert, position, prozent, lauf, teile, ort, dauer, quelle,
loeschen, zustimmung, abgemeldet}], belegt, erstabfrage}`; `POST /api/tool {id, aktion: installieren|deinstallieren,
teil?, zustimmung?}` → `{tool, lauf}` (Download eingereiht) bzw. `{tool, meldung}`; `POST /api/tools-erstabfrage
{auswahl: [id, …]}` → wie `GET` + `offen` (brauchen erst die Zustimmung) + `laeufe`. Über den Handy-Zugang erlaubt.
Läufe eines Tool-Downloads tragen `tool` (Status, Warteschlange). Die alten Werkzeuge `modell-x4`, `modell-x2`, `ki-bild`
bleiben in `/api/werkzeuge` (mit `tool`), die Seite zeigt sie im Tools-Bereich statt doppelt.

**Anbindung:** Fehlt ein Tool, antwortet der Server **409 `{fehler, code: "tool_fehlt", tool}`** statt eines
Fehlers: `POST /api/lauf` mit `art: ki-bild` (auch `vor_start` in der Warteschlange) und `art: verbessern`/`generator`,
wenn Real-ESRGAN fest eingestellt ist (`ki: realesrgan|realesrgan-x2`; „Auto“ nimmt ohne Tool still FSRCNN).
`ohne_tool: true` rechnet dann mit FSRCNN („Einfach vergrößern (ohne Tool)“). Die Übersetzung antwortet weiter 409
`zustimmung`; die Seite erteilt sie über `uebersetzungsTool()` (= Tool installieren). `GET /api/ki-bild` → `installiert`
und `/api/status` → `tools: {id: installiert}` folgen `tools.installiert` (abgemeldet zählt als fehlend); `/api/tools`
liefert je Tool `frei` (freier Platz am Ziel) und bei KI-Bildern `ram_gb` für Hinweise in der Rückfrage.
**Deinstallieren räumt mit auf:** Bildverbesserung → KI-Einträge (Real-ESRGAN) in `ausgabe/.cache`, KI-Bilder →
`ausgabe/.ki-bild`; Druck-PDFs, FSRCNN-Einträge und die eigene Prompt-Fassung bleiben. **Oberfläche:** Reiter
Bildverbesserung zeigt ohne Tool oben einen Kasten (`#verb-tool`: Nutzen, „Installieren“, „Schnellere Variante ×2“);
„Verbessern“ fragt bei Auto/Real-ESRGAN ohne Tool über `brauchtTool(…, {alternativ, alternativText})`; KI-Knöpfe
(Schritt 1, Editor, „🪄 Gans erzeugen“) sind immer da, ohne Modell → `kiToolHolen()` → nach dem Download öffnet sich
das KI-Fenster mit den Eingaben wieder. Reiter „Über“ listet die Tools. Prüfungen: E23.

**Farben & Darstellung (Prüfungen E24).** Werkzeug „🎨 Farben & Darstellung“ (`art=dialog`, Fenster `#farben-fenster`). Schemata: `himmel`
(Standard = die festen Werte im `:root` von `index.html`, es wird nichts überschrieben), `nacht`, `wiese`, `kontrast`, `system`
(dunkle Werte nur unter `@media (prefers-color-scheme: dark)`), `eigen` (7 Grundfarben `hintergrund, flaechen, text, akzent, linien,
erfolg, fehler`, nur `#RRGGBB`; es werden nur die Variablen überschrieben, deren abgeleiteter Wert sich gegenüber dem Standard
ändert). Alle übrigen Töne (`--nacht-2`, `--wasser`, Flächen, Chips, Schrift auf Knöpfen `--auf-*` …) rechnet `gans_ui.farb_ableitung()`
aus den 7 Grundfarben – reine Rechnung im Server, kein `color-mix()` nötig. Gespeichert in `ui_einstellungen.json` → `farben`
`{schema, eigene}` (Standard = Eintrag fehlt). Der Server setzt die Variablen beim Ausliefern der Seite in
`<style id="farben-vars">` (Platzhalter `/*__GL_FARBEN__*/`) und den `theme-color`-Meta-Tag (`__GL_THEME__`) → kein Aufblitzen;
gilt auch über den Handy-Zugang. API: `GET /api/farben` → `{schema, eigene, standard, css, meta, kontrast, schemata}`;
`POST /api/farben {schema, eigene}` speichert (ungültige Werte → 400), `{…, speichern: false}` ist nur Vorschau,
`{zuruecksetzen: true}` löscht den Eintrag. Kontrastprüfung (Text/Hintergrund, Text/Flächen, Schrift auf Knopf; ≥ 4,5 : 1).
**Regel:** neue Farben im CSS nur über Variablen (E24 prüft, dass außerhalb von `:root` keine festen Farben stehen).

**Sprachen (Prüfungen E25; `sprachen.py`, optional eingebunden).** Kartensprache = Rückseite + Richtung der
Übersetzung; `es` (Spanisch wie in Mexiko gesprochen) ist Standard und immer da. Weitere 14 Sprachen sind Teile des
Tools `sprachen` (je Sprache einzeln): `en nds fr it tr sv no pl` (lateinisch – Poppins hat alle Zeichen, Installieren =
aktivieren), `ru` (Noto Sans), `ja`/`ko`/`zh` (IBM Plex Sans JP/KR/SC, CJK zeichenweise umbrechen), `hi` (Poppins hat
Devanagari, braucht uharfbuzz zum Formen), `ar` (IBM Plex Sans Arabic + uharfbuzz, rechts nach links). Katalog
`sprachen.SPRACHEN`: Namen de/en/es, Eigenname, Richtung, Schrift, Umbruch, Sonderzeichen, Umschrift ja/nein, Dienst-Codes
(Wiktionary-Vorlage, Abschnittsname, MyMemory, DeepL; `None` = Dienst entfällt: DeepL ohne hi/nds, MyMemory ohne nds).
Schriften `sprachen.SCHRIFTEN`: Regular + Bold + OFL, TrueType, feste Git-Revision, SHA-256, Größe. Pakete liegen in
`Daten/sprachen/<code>/` (`paket.json` + Dateien); uharfbuzz (fest 0.56.3) per `pip --target` in `Daten/sprachen/_pakete`
(nicht ins eigene Python – so bleibt es entfernbar; `sprachen.aktiviere_pakete()` nimmt es vor ReportLab in den Suchpfad),
das letzte Paket, das es braucht, entfernt es. Laden = Lauf-Art `sprache` (`python3 sprachen.py --laden <code>`,
fortsetzbar über `.part` + Range, Platzprüfung, „NN %“). **Zielsprache:** `ui_einstellungen.json` → `zielsprache`
(fehlt = es; nur installierte gelten, sonst es); `GET/POST /api/zielsprache {zielsprache}` (nicht installiert → 409
`tool_fehlt`, `tool: sprachen`, `teil: <code>`); `/api/status.zielsprache` = `{code, kurz, namen, name, eigenname,
richtung, umbruch, sonderzeichen, installiert, sprachen}`. **Karten:** `/api/karten` liefert je Karte `rueckseiten
{code: text}` (es immer, andere nur wenn gefüllt) und `uebersetzungen {code: status}`, `offen` = Text der Zielsprache
fehlt. **Seit 2.0 gilt:** die Felder `es`/`uebersetzung` einer Karte sind Rückseite und Prüfstatus **in der Zielsprache**
(bei es wie bisher); `_zeile_aus(k, zs)` schreibt `es` in die Spalte der Zielsprache und die übrigen Sprachen aus
`rueckseiten`/`uebersetzungen` (Import: `zs="es"`, Spalten roh); `POST /api/karten` ohne `rueckseiten` (ältere Seite)
behält die vorhandenen. `POST /api/karte-speichern` nimmt zusätzlich `rs {code: Wort}` + `rs_auto` (Editor „Weitere
Sprachen“; geändert → Status leer, übernommener Vorschlag → automatisch). **Übersetzung:**
`uebersetze(…, richtung="de-<code>" | "<code>-de")`, `POST /api/uebersetzen {de, ziel?}` (Standard: Zielsprache);
Wiktionary liest `{{Ü|code|…}}`/`{{Üt|code|Wort|Umschrift}}` (Umschrift → Vorschlag „Wort|Umschrift“, zweite Zeile der
Karte), Regionsordnung nur für es; Zeichenprüfung lässt außer Lateinisch nur die Schrift der Kartensprache zu;
Zwischenspeicher-Schlüssel mit Sprache (es wie bisher). **Oberfläche (Prüfungen E26):** Texte der Kartensprache
tragen `{zs}` (Seite: `t()` setzt `zsName()` ein; Python: `gl.mit_zs()` in `meldung`/`pm`/`tx`, Name über
`gl.zs_name()`); Erklärungen „wie in Mexiko“ nur bei es (`NUR_ES`: `h_es_feld` → `h_rs_feld`, `u_kartensprache_wert` →
`u_kartensprache_zs`). Leitfäden markieren die Kartensprache mit doppelten geschweiften Klammern um „Spanisch“ / „Spanish“ / „español“
(„Español“ am Satzanfang); `gans_ui.kartensprache_text()` ersetzt sie vor dem Rendern (bei es nur die Klammern weg, Zwischenspeicher
je Zielsprache). Prüfregeln `pruefe_karte(…, ziel)`: ä/ö/ß und ¿/¡ nur bei es, Zeichen- und Platzprüfung mit der Schrift
der Sprache (fehlt ihr Sprachpaket noch, entfallen beide). Sobald außer es eine Sprache installiert ist: Auswahl „Rückseite:“ (Meine Karten, Schritt 2,
Tabelle; `POST /api/zielsprache`), Sprach-Chips (Code groß, Hover = Name, gestrichelt = leer, dunkel = Zielsprache; in
Meine Karten wechselt ein Klick die angezeigte Rückseite), Editor „Weitere Sprachen“ (Feld + 🌐 je Sprache), Tabelle mit
Spalte je Sprache und Filter „fehlt auf …“, Chip an Feldern in Schritt 1/Ideen. Rückseitenfelder `lang` + `dir="auto"`,
Sonderzeichen-Leiste aus dem Katalog. Tool-Karte „Sprachen“ listet alle 15 (Installieren/Entfernen/„Als Rückseite“);
Entfernen der Zielsprache → zurück auf es (`zielsprache_zurueck` in der Antwort), Kartentexte bleiben.

**Druck in anderen Sprachen (Prüfungen E27).** Generator-Schalter `--sprache <code>` (intern, Standard `es`):
Rückseite aus der Spalte `<code>` (leer → Meldung `es_leer` mit Spalte + Sprache, Karte setzt aus), Status aus
`uebersetzung_<code>`, Karten tragen zusätzlich `rueckseiten` (alle gefüllten Sprachspalten). Dateinamen
`gl.ausgabe_namen(cfg)` mit Endung `_<code>` (`gl.sprach_endung`), es unverändert; PDF-Betreff „Lernkarten Deutsch –
<Sprache>“, `bericht.json` mit `sprache`. `--sprachkuerzel auto|an|aus` (sichtbar in „Ausrichtung und Rückseite“): Kürzel
oben links auf der Rückseite, auto = nur bei ≠ es. **Schriftsatz** `gl.satz(code)` → `Satz` (je Prozess zwischengespeichert):
Fett/Normal aus `sprachen.schriften(code)` (Medium → Regular), sonst Poppins; `voll` = Schrift da (sonst druckt Poppins,
Meldung `schrift_fehlt`, Prüfungen entfallen). hi/ar: uharfbuzz erst bei Bedarf (`sprachen.aktiviere_pakete()`, dann
`ttfonts.uharfbuzz` gesetzt), eigene Schriftnamen `GL-<code>-bold|regular` mit `shapable=True`; geformt wird je Lauf mit
uharfbuzz → `ShapedStr` (gezeichnet über `beginText/textOut`, Breite = Summe `x_advance`) – alle übrigen Schriften
`shapable=False`, der Druck für es bleibt Byte-für-Byte gleich gerechnet. Rechts-nach-links (ar): `Satz.laeufe()` dreht die
Wortfolge um, Ziffern/lateinische Wörter (samt Leerzeichen dazwischen) bleiben ein LTR-Lauf (HarfBuzz ordnet nur innerhalb
eines Laufs). ja/zh: `zwei_zeilen` teilt zwischen Zeichen, nie Satzzeichen/kleine Kana an den Zeilenanfang bzw. öffnende
Klammern ans Ende, bevorzugt nach „、。“. Schriftgröße mit echten (geformten) Breiten (`_passend`). Fehlt uharfbuzz (z. B.
gesperrte DLL) → ungeformt + Meldung `formen_fehlt`. Prüfbogen: Titel mit Sprache, Zeile `<CODE>: Wort` in der Schrift der
Sprache. **Oberfläche:** Vorschau (`/api/vorschau`, `/api/rueckseite`) in der Zielsprache (Gänse-Bild-Vorschau mit
Beispielwort je Sprache); Schritt 3 „Sprache der Rückseite“ (nur bei mehreren Sprachen): Zielsprache (Standard), jede
installierte oder „alle installierten“ → `POST /api/lauf {art: generator, sprache}` reiht je Sprache einen Auftrag ein
(`{…, auftraege, sprachen}`; Vorlagen ohne Sprache; nicht installiert → 409 `tool_fehlt`, `teil`); `GET /api/befehl?sprache=`.
Ein beim Entfernen noch belegtes `_pakete` räumt `sprachen.pakete_aufraeumen()` beim nächsten Start der Oberfläche weg.
**Exporte** (`lernkarten_digital.py`): es exakt wie bisher; andere Sprache: Notiztyp `me-goosta-bild-v1-<code>` („Bild →
Japanisch“, Feld „Japanisch“, `rtl` für ar), Stapel „<Name> – <Sprache>“, Schlagwort `<code>`, eigene GUIDs; Lernseite mit
`rs_lang`/`rs_dir` und Richtungstexten der Sprache; `tabellen*/karten_alle_sprachen.csv` (Semikolon, Spalte je gefüllter
Sprache, es immer).

**Karten lernen (Prüfungen E28; `lernen.py`, optional eingebunden).** Tool `lernen` (Aktivierung, kein Download;
Deinstallieren löscht `lernstand.json`, `.bak` und eine aufgehobene `lernstand.kaputt.json` im Projektordner). Grundlage:
verteiltes Wiederholen + aktives Abrufen (erst erinnern, dann umdrehen) + Planung mit **FSRS-6** in reinem Python –
Standardparameter (21 Gewichte) und Formeln wie `open-spaced-repetition/py-fsrs` 6.3 (MIT; E28 vergleicht drei
Bewertungsfolgen mit Werten, die mit py-fsrs 6.3.2 berechnet wurden). Bewertung 1 Nochmal · 2 Schwer · 3 Gut · 4 Einfach;
Zustände neu → lernt → wiederholung ⇄ neulernt; Lernschritte 1 + 10 min (Schwer beim ersten Schritt = Mittel 5,5 min),
Neulernschritt 10 min, Intervall aus der gewünschten Behaltensquote (Standard 90 %, erlaubt 70–97 %), Höchstintervall
36 500 Tage, Fuzz ab 3 Tagen wie py-fsrs, aber reproduzierbar (Zufall aus Karte + Lerntag → Vorschau = Ergebnis).
Verstrichene Tage = **Lerntage** (Tageswechsel 4 Uhr Ortszeit, einstellbar); Wiederholungen sind ab ihrem Lerntag
fällig, Lernschritte zur Uhrzeit (bis 20 min früher, wenn sonst nichts fällig ist). **Lernkarte** = (Bild, Sprache,
Richtung `v` Bild/Deutsch → Kartensprache, `r` umgekehrt), id `<bild>|<code>|<v|r>`, je eigener Stand; die Sprache kommt
aus `rueckseiten` (Einstellung „Sprache“ leer = Zielsprache, ein Stapel kann eine eigene haben). Lernbar = aktive Karte mit
Bild und Wort in der Sprache. **Sitzung** (`naechste_karte`): fällige Lernschritte → fällige Wiederholungen (niedrigste
Abrufwahrscheinlichkeit zuerst) → neue Karten in der Reihenfolge der Kartenliste, gleichmäßig zwischen die Wiederholungen
gemischt; Tageslimits neue Karten (20) und Wiederholungen (200) über das Protokoll des Lerntags; die andere Richtung
derselben Karte erst am nächsten Tag; fertig → `morgen`, `naechster_schritt`. Fehler = Rückfälle aus der Wiederholung,
**Problemkarte** ab 8. **Speicher** `lernstand.json` neben `karten.csv` (Nutzerdaten: nie im Release, Update übernimmt
sie über `starter.NUTZER_DATEIEN`, Komplettsicherung enthält sie): `{art: "me-goosta-lernstand", version, einstellungen
{neu_pro_tag, wdh_pro_tag, behaltensquote, tageswechsel, lernschritte, neulernschritte, richtung: vorwaerts|rueckwaerts|beide,
sprache, hoechstintervall}, karten {id: {zustand, s, d, faellig, letzte, anzahl, fehler, schritt, pruef, entfernt?}},
protokoll [{t, k, n, ms, z, v?}] (letzte 10 000; `v` = Stand davor für „Rückgängig“, die letzten 50), stapel [{id, name,
sprache, notiz, suche, nur: ""|neu|faellig|problem, bilder}]}`. Atomar geschrieben (`.tmp` → Ersetzen), die vorige Fassung
bleibt `lernstand.bak.json`; ist die Hauptdatei kaputt, gilt die `.bak` (die kaputte wird als `lernstand.kaputt.json`
aufgehoben). **Zurücksetzen bei Bearbeitung:** Prüfwert je Lernkarte aus Deutsch-Text + Wort der Sprache + Bild-Prüfsumme;
`abgleichen()` läuft bei jedem Laden der Karten (`karten_daten`, also nach Editor, Tabelle, Bild ändern, Rückgängig, Import
und nach Änderungen der CSV von außen): Bild geändert → alle Sprachen, Wort → nur diese Sprache, Notiz/`fit` → nichts; Bild
fehlt gerade → keine Entscheidung. Umbenennen (`setze_karte` mit neuem `bild`) nimmt den Stand mit. Jede Antwort der Anfrage
trägt dann `lernstand_zurueckgesetzt [{bild, de, sprachen}]` + `lernstand_meldung` (Text in der Sprache der Seite).
Entfernte Karten behalten ihren Stand 90 Tage. **API** (ohne Tool 409 `tool_fehlt`, `tool: lernen`): `GET /api/lernen` →
`{einstellungen, sprache, stapel [{…, faellig, neu, lernen, wiederholen}] (erst „alle“), statistik {heute {gelernt, neu,
wiederholt, richtig, minuten}, serie, woche [7 Tage fällig, Tag 0 inkl. überfällig], faellig_30, behaltensquote (30 Tage,
Wiederholungen mit Note > 1), zustaende {neu, lernt, jung, sicher (≥ 21 Tage)}, problem, karten}, rueckgaengig}`;
`GET /api/lernen-karte?stapel=` → `{karte {id, bild, sprache, richtung, de, wort, notiz, zustand, anzahl, fehler, problem,
vorschau {1–4: Sekunden}, vorschau_text}, zaehler {neu, lernen, wiederholen}, fertig, morgen?}`; `POST /api/lernen-bewerten
{id, note, dauer_ms, stapel?}` → neuer Stand (+ `naechste`, wenn `stapel` mitkommt); `POST /api/lernen-rueckgaengig
{stapel?}` → `{id, bild, note, naechste}`; `POST /api/lernen-einstellungen {werte}`, `POST /api/lernen-stapel {aktion:
speichern, stapel} | {aktion: loeschen, id}`, `POST /api/lernen-zuruecksetzen {bild} | {alle: true}`, `GET /api/lernen-export`
(Download `…_Lernstand_<Datum>.json`), `POST /api/lernen-import {lernstand}` (je Lernkarte gilt der neuere Stand, Protokoll
und Stapel zusammengeführt, Einstellungen bleiben). `/api/karten` liefert mit Tool je Karte `lernen {zustand: neu|lernt|jung|
sicher, faellig, faellig_in (Lerntage), stabilitaet, anzahl, fehler, problem}` (eingestellte Sprache, schwächste Richtung).
**Oberfläche (Prüfungen E29):** Reiter „🎓 Lernen“ (#lernen) direkt unter „Meine Karten“, immer sichtbar; Zahl =
heute fällig + neu (Stapel „alle“). Ohne Tool Hinweis + „Karten lernen aktivieren“ (rauchtTool("lernen")). Übersicht:
Kachel „Heute: n Wiederholungen · m neue“ + „Los geht’s“ (+ „Rückgängig“), Stapel (fällig/neu, Lernen, ✎, 🗑 mit Rückgängig im
Toast), „Neuer Stapel …“ (Fenster: Name, Notiz enthält, Suchtext, Sprache, Nur, Häkchen-Auswahl im Kartenraster), Statistik
(Gänsemarsch = Serie, heute gelernt, Balken der nächsten 7 Tage als Inline-SVG mit Farb-Variablen, Zustände, Behaltensquote,
Problemkarten → „Meine Karten“ gefiltert), Einstellungen (neue/Tag, Wiederholungen/Tag, Behaltensquote 80–95 % mit Erklärung,
Richtung, Lernsprache, Tageswechsel), Lernstand exportieren/importieren/alles zurücksetzen (Rückfrage in der Seite).
Sitzung: Vorderseite (Kartenbild bzw. Wort bei Richtung ), „Antwort zeigen“ (Leertaste/Enter/Tippen), Rückseite mit
ria-live (Wort groß mit Sprach-Chip, Deutsch, Notiz; Problemkarte → Hinweis + „Karte bearbeiten“), Knöpfe Nochmal/Schwer/
Gut/Einfach mit orschau_text, Tasten 1–4, Strg+Z, Esc = beenden, Fortschrittsbalken, Abschluss mit Lob + „Morgen fällig“
+ nächster Lernschritt. 🔊 nur, wenn speechSynthesis eine lokale Stimme der Sprache hat; seit 2.2 nach dem Aufdecken (beide
Richtungen, nie vorher) zusätzlich 🔊 neben dem deutschen Text (`data-ln="vorlesen-de"`, liest `de` mit einer lokalen
Stimme de-DE → de-AT → de-CH → andere de; ohne Stimme kein Knopf; gemeinsamer Weg `vorlesen(text, stimme)`, Beenden ruft
`cancel`). Keine neue Taste; die Lernseite liest nach dem Umdrehen ebenso Deutsch (Stimme beim Laden + `voiceschanged`),
das Anki-Paket bleibt ohne `{{tts}}`. Touch: Bewertungsleiste klebt unten,
Wischen rechts = Gut, links = Nochmal (nur Touch, Rückgängig über ↶). „Meine Karten“: Lernstand-Marke je Karte (Ring neu ·
lernt · jung · sicher, Hover „n× gelernt, nächste Wiederholung …“), Filter alle/fällig/neu/sicher/Problemkarten, „☑ Auswählen“
→ „Jetzt lernen“ (Stapel `00000000` „Aktuelle Auswahl“) bzw. „Zum Stapel …“ (neu oder zu vorhandenem). Editor zeigt vor dem
Speichern „Speichern setzt den Lernstand dieser Karte zurück“, die Tabelle denselben Hinweis in der Zeile; pi() zeigt
jede lernstand_meldung als Toast. Rückfrage beim Deinstallieren des Tools bietet „Lernstand vorher exportieren“.

**Oberfläche:** Werkzeuge → Bereich „🧰 Tools“ ganz oben: Karte je Tool (Symbol, Name, Nutzen, Größe, Zustand mit
Fortschritt, „Installieren“ bzw. Teil-Knopf `.knopf.teil` zweizeilig: fett „+ Schneller ×2“, klein „fast gleiche
Qualität, etwa 4× schneller · 64 MB“ – Teil-Titel kurz, Erklärung im Feld `hinweis` je Teil, von `/api/tools`
mitgeliefert –, „Deinstallieren …“ mit Rückfrage: was gelöscht wird, wie viel frei
wird, Karten bleiben), Summe belegt. `brauchtTool(id, weiter, {alternativ})` in `index.html` ist der gemeinsame Einstieg
für alle Stellen, die ein Tool brauchen (installiert → `weiter()`; sonst Fenster „Installieren und weitermachen“ / „Ohne
Tool weiter“ / „Abbrechen“; bei der Übersetzung ist die Zustimmung die Rückfrage); nach dem Download ruft
`laufAbgeschlossen` die wartenden Aktionen auf und meldet „Tool … ist bereit“. **Neues Tool:** Eintrag in
`tools.TOOLS` (Texte `L(…)`, `da`, `belegt`, `auftrag`, `entferne`, `laden`/`nutzt` = Lauf-Arten) – erscheint automatisch.

## 10. Start und Installation (ohne vorinstalliertes Python, ohne Administratorrechte)

**Ausgangslage:** Version 1.3 setzte ein installiertes Python voraus. Ohne Python hat `.pyw` keine Dateizuordnung – der
Doppelklick führt ins Leere („Wie möchten Sie diese Datei öffnen?“) –, und Windows 11 „Intelligente App-Steuerung“
(Smart App Control) blockiert unsignierte Startdateien mit „Mark of the Web“ (`.bat .cmd .ps1 .vbs .js .lnk .url`; die
Markierung setzt der Browser beim Download, das Entpacken vererbt sie). Signierte Programme wie das offizielle
`python.exe`/`pythonw.exe` der Python Software Foundation laufen dagegen. Seit dem April-Update 2026 (KB5083769) lässt sich
Smart App Control ohne Neuinstallation wieder einschalten; abschalten bleibt trotzdem nicht empfohlen.

**Aufbau ab 1.4:**

| Datei | Zweck |
|---|---|
| `Me Goos-ta Deutsch - Windows.cmd` | Startdatei für Windows. Prüft „entpackt?“ und 64 Bit, sucht das eigene Python in `%LOCALAPPDATA%\Me-Goos-ta-Deutsch\python`; fehlt es oder startet es nicht: lädt das offizielle **embeddable Python 3.13.16** (amd64, signiert, 11 MB) von python.org mit `curl.exe` (Rückfall: PowerShell `Invoke-WebRequest`, nutzt auch die Proxy-Einstellungen von Windows), prüft **SHA-256** mit `certutil` (Rückfall `Get-FileHash`), entpackt mit `tar.exe` (Rückfall `Expand-Archive`) in einen Neben-Ordner, schreibt `python313._pth` (gibt `Lib\site-packages` frei), testet es und benennt erst dann um (scheitert das kurz, weil der Virenscanner das frische Python noch prüft – auf Windows-ARM-Rechnern beobachtet –, bis zu 15 Versuche im Abstand von 2 s, seit 2.2). Danach `starter.py`. Nur ASCII, CRLF, Systemprogramme mit vollem Pfad, keine Klammerblöcke mit Pfaden, Meldungen auf Englisch; erst wenn im Programm eine Sprache gewählt ist, auf Deutsch bzw. Spanisch (`findstr` nach `"sprache": "de"`/`"es"` in `Programm\ui_einstellungen.json`; die Regionseinstellung zählt nicht). |
| `Me Goos-ta Deutsch - Linux.sh` | Startdatei für Linux: ruft die Mac-/Linux-Startdatei auf; ohne Terminal öffnet sie eines (x-terminal-emulator, gnome-terminal, ptyxis, kgx, konsole, xfce4-terminal …). Sprache der Meldung wie bei der Mac-/Linux-Startdatei. |
| `Me Goos-ta Deutsch - Mac.command` | Startdatei für macOS und Linux. Lädt **python-build-standalone 3.13.15** (`install_only_stripped`, 20260924) für Apple Silicon/Intel bzw. Linux x86-64/ARM64 von GitHub, prüft SHA-256 (`shasum`/`sha256sum`), entfernt die Quarantäne der eigenen Dateien, startet `starter.py`. POSIX-`sh`, alle Pfade in Anführungszeichen. Meldungen auf Englisch bzw. in der im Programm gewählten Sprache (`grep` in `Programm/ui_einstellungen.json`; `LANG`/`AppleLocale` zählen nicht). |
| `Programm/starter.py` | **Startprogramm** (nur Standardbibliothek). Erkennt den ersten Start, richtet ein, startet oder findet die Oberfläche, repariert. Einzelheiten unten. |
| `Programm/werkzeuge/pip-26.2.1-py3-none-any.whl` | pip für das embeddable Python (das ohne pip kommt); wird direkt aus dem Rad installiert (MIT-Lizenz, im Rad enthalten). Optional `Programm/werkzeuge/pakete/*.whl` für Rechner ohne Internet. |
| `LIES MICH ZUERST.html` | Anleitung mit Bildern (Deutsch, Englisch, Spanisch; Windows/Mac/Linux), funktioniert offline per Doppelklick. Startet immer auf **Englisch** (Titel „Read me first“); Deutsch/Spanisch per Knopf oder Anker `#de`/`#es`/`#en` (z. B. aus Links); das Betriebssystem wird erkannt |
| Desktop-Symbol / Startmenü (Windows), `~/Applications/Me Goos-ta Deutsch.app` (Mac, als AppleScript-Applet für Intel und Apple-Chips), Menüeintrag `~/.local/share/applications/me-goos-ta-deutsch.desktop` (Linux) | entstehen beim ersten Start lokal (ohne Download-Markierung); starten `pythonw.exe` bzw. `python3` mit `starte.py` im Datenordner, das den zuletzt gestarteten Programmordner aus `programm-ort.txt` liest – ohne Konsolenfenster |

**Ablauf des ersten Starts** (Fenster zeigt jeden Schritt, Protokoll in `protokoll.txt` im Datenordner; Sprache des
Fensters nach `starter.ermittle_sprache()`: im Programm gewählte → `MGD_SPRACHE` → Englisch, nie die Systemsprache;
`starte.py` im Datenordner bekommt die Sprache der Einrichtung für seine Meldung „Programmordner verschoben“):
1. Ordner prüfen: beschreibbar? (sonst Hinweis auf Verschieben bzw. „Überwachter Ordnerzugriff“/macOS-Datenschutz), aus
   einem Temp-/ZIP-Ordner gestartet? (dann „bitte entpacken“), genug Platz (≥ 700 MB)?
2. pip vorbereiten (embeddable: aus dem mitgelieferten Rad).
3. Pakete installieren: `pip install --only-binary=:all: --require-hashes -r pakete.lock` (nie kompilieren; seit 2.5
   feste Fassungen mit der SHA-256 jedes Rads – eine Datei, deren Prüfsumme nicht passt, installiert pip nicht), lesbar
   gekürzte Ausgabe („↓ numpy 2.5.4 (12,6 MB)“), Lebenszeichen bei langer Stille, eigene pip-Konfiguration
   (`PIP_CONFIG_FILE`=leer, `PYTHONNOUSERSITE`), damit fremde Einstellungen nicht stören. Ein Ordner
   `werkzeuge/pakete/` (Rechner ohne Internet) wird zuerst genutzt – die Prüfsummen gelten auch dort.
4. Pakete prüfen: eigener Prozess lädt Pillow, NumPy, ReportLab, pypdfium2 wirklich (inkl. DLLs). Unter Windows wird bei
   Fehlern jede DLL einzeln geladen und der Fehlercode ausgewertet: 4551/577 = Smart App Control → ältere, weit
   verbreitete Fassungen („bewährt“ = `pakete-bewaehrt.lock`, „älter“ = `pakete-aelter.lock`, ebenfalls mit Prüfsummen)
   probieren; 1260 = Richtlinie; 225 = Virenschutz; sonst einmal neu
   installieren. Nur pypdfium2 gesperrt → abschalten (PDFs entstehen trotzdem). Ein nötiger Ersatz-Satz wird gemerkt.
5. Installierte Tools übernehmen: liegt im Datenordner eine Kopie der Bildverbesserung (`modelle/realesrgan-*.npz`) und
   fehlt sie im Programmordner, wird sie kopiert – **nie ein Download**. Ohne Kopie entfällt der Schritt still (dann
   5 statt 6 Schritte). Tools wählt man in der Oberfläche (Abschnitt 9.4).
6. Download-Markierung (`:Zone.Identifier` bzw. `com.apple.quarantine`) von den eigenen Dateien entfernen, Symbole anlegen.
7. Stempel `eingerichtet.json` schreiben, Oberfläche starten, Browser öffnen; das Fenster schließt sich (Windows).

**Erkennung bei jedem Start** (Stempel = Python-Präfix + Version, Paketliste, eingerichtete Ordner):

| Zustand | Reaktion |
|---|---|
| kein Stempel | erster Start → alles einrichten (5 Schritte, mit Tools-Übernahme 6) |
| anderes Python / neue Lock-Datei (`pakete*.lock`, z. B. nach einem Update) | Pakete anpassen (genau die Fassungen des Locks) |
| neuer Programmordner (neue Version entpackt, Ordner kopiert) | liegen im bisherigen Ordner (`programm-ort.txt`) eigene Karten, die hier fehlen: **Frage „Übernehmen? [J/n]“** (ohne Konsole als Ja/Nein-Fenster) → kopiert `karten.csv`, `karten.bak.csv`, `ui_einstellungen.json` (Pfade in den alten Ordner werden umgestellt), `bilder/` (auch `_entfernt/`), `ausgabe/` (samt verbesserten Bildern im Zwischenspeicher und Entwürfen), Gänse-Bild und `assets/_alt/`; was dabei hier ersetzt würde, kommt nach `Programm/_beispiele/`; der bisherige Ordner bleibt unverändert; eine laufende alte Oberfläche wird vorher beendet. Danach nur installierte Tools (aus dem Datenordner), Markierungen, Symbole |
| Oberfläche dieses Ordners läuft schon (Instanz-Datei + Antwort auf den Startschlüssel) | nur Browser öffnen |
| Oberfläche läuft, aber ältere Version | höflich beenden (`/api/beenden`), neu starten |
| Oberfläche bricht beim Start mit Import-/DLL-Fehler ab | automatisch reparieren (Neuinstallation), noch einmal starten |
| zweiter Start während der Einrichtung | wartet (Datei-Sperre), öffnet danach nur den Browser |
| Start über das Desktop-Symbol, aber Einrichtung nötig | öffnet dafür ein sichtbares Fenster (Windows: neue Konsole, Mac: Terminal) |

Schalter für Fachleute: `starter.py --status`, `--einrichten` (Reparatur), `--beenden`, `--entfernen` (Python, Pakete,
Symbole löschen; der Programmordner bleibt), `--deinstallieren` (wie `--entfernen`, zusätzlich der Programmordner mit
allen Karten – nicht rückgängig zu machen), `--kein-browser`.

**Stolpersteine und Gegenmaßnahmen** (gesucht und behoben für 1.4):

| Stolperstein | Gegenmaßnahme |
|---|---|
| Kein Python installiert, nur der Microsoft-Store-Platzhalter („Python was not found“) | eigenes Python wird mitgeladen; die Startdateien nutzen nie ein Python aus `PATH` |
| Smart App Control blockiert die heruntergeladene Startdatei | Anleitung „Zulassen“ (ZIP oder Startdatei, mit Bild); danach entfernt das Startprogramm die Markierung von allen eigenen Dateien; Desktop-Symbol entsteht lokal ohne Markierung und startet das signierte `pythonw.exe` |
| Smart App Control sperrt unsignierte Paket-DLLs (Pillow, NumPy, pdfium) | Erkennung am Fehlercode, ältere Fassungen probieren, pypdfium2 notfalls abschalten, sonst klare Optionen |
| SmartScreen „Der Computer wurde durch Windows geschützt“ | Hinweis „Weitere Informationen → Trotzdem ausführen“ in Anleitung und Leitfaden |
| Startdatei direkt in der ZIP doppelgeklickt (Windows entpackt nur diese eine Datei in einen Temp-Ordner) | `Programm` fehlt bzw. Temp-Pfad → Meldung „bitte zuerst entpacken“ mit Anleitung |
| Ordnernamen mit Leerzeichen, Klammern, `&`, `%`, `!`, Umlauten („Me-Goos-ta-Deutsch (1)“) | `.cmd` ohne verzögerte Erweiterung, ohne Klammerblöcke mit Pfaden, ohne `call` mit Pfaden, alles in Anführungszeichen; Python übernimmt alles Weitere |
| fremdes `curl`/`tar` (z. B. Git für Windows) zuerst in `PATH` | Systemprogramme immer mit vollem Pfad `%SystemRoot%\System32\…` |
| Proxy/Firmennetz | Rückfall auf PowerShell (nutzt Windows-Proxy), pip nutzt Systemeinstellungen; Zertifikate über den Windows-Speicher bzw. truststore |
| Abgebrochener oder beschädigter Download | `.part`-Datei, SHA-256-Prüfung, Entpacken in Neben-Ordner, erst nach erfolgreichem Test umbenennen; bereits Geladenes wird wiederverwendet |
| Kein Internet | verständliche Meldung („nur der erste Start braucht Internet“); offline möglich mit `werkzeuge/pakete` |
| Zu wenig Speicherplatz | Prüfung vor der Einrichtung, Meldung mit freiem/benötigtem Platz |
| Programmordner schreibgeschützt (z. B. `C:\Programme`, „Überwachter Ordnerzugriff“, macOS-Datenschutz) | Schreibtest vor dem Start, Meldung mit Lösung |
| Klick in das Konsolenfenster hält alles an (QuickEdit) | QuickEdit wird für das Startfenster abgeschaltet; die Oberfläche läuft ohnehin ohne Konsole (`pythonw.exe`) |
| Start „Als Administrator“ | Hinweis, dass es nicht nötig ist; Browser wird dann über den Explorer ohne Administratorrechte geöffnet |
| 32-Bit-Windows / Windows auf ARM | 32 Bit: klare Meldung; ARM: x64-Python über die eingebaute Emulation |
| Zwei Doppelklicke kurz hintereinander | Datei-Sperre; der zweite Start wartet und öffnet dann nur den Browser |
| Oberfläche läuft schon / Port 8765 belegt | Instanz-Datei je Programmordner (nur für den eigenen Benutzer lesbar), sonst nächster freier Port |
| Laufende Oberfläche hält DLLs fest, Pakete sollen ersetzt werden | wird vor der Paket-Installation höflich beendet |
| Programmordner verschoben oder neue Version entpackt | Symbol liest den Ort aus `programm-ort.txt`; fehlt der Ordner → Meldung; neuer Ordner → kurze Einrichtung ohne neuen Download und Angebot, die eigenen Karten zu übernehmen |
| Neue Version **über** den alten Ordner entpackt („Dateien ersetzen“) | der Download enthält keine `karten.csv` und keinen Ordner `bilder/` (nur `beispiel-karten.csv` und `beispiel-bilder/`), keine Druckdateien und keine Einstellungen – eigene Karten, Bilder, PDFs, Einstellungen und das Gänse-Bild bleiben erhalten |
| Fremde pip-Einstellungen (`user = true`, `PIP_TARGET`, `PYTHONPATH`, Pakete im Benutzerordner) | für das eigene Python ausgeschaltet bzw. aus der Umgebung entfernt |
| Kein Konsolenfenster (Start über Symbol) | Meldungen als Windows-Meldungsfenster bzw. macOS-Hinweis; Adresse zum Abtippen, falls kein Browser aufgeht |
| macOS Gatekeeper / fehlendes Ausführungsrecht | Anleitung („Dennoch öffnen“, Control-Klick, `sh` + Datei ins Terminal ziehen); Quarantäne der eigenen Dateien wird entfernt, Ausführungsrecht gesetzt |
| macOS fragt nach Zugriff auf Downloads/Dokumente | Hinweis „Erlauben“; ohne Zugriff klare Meldung statt „bitte entpacken“ |
| macOS: Python ohne Zertifikate (SSL-Fehler beim Modell-Download) | `ki_modelle` versucht nacheinander System, truststore (Zertifikatsspeicher des Betriebssystems) und certifi – Prüfung bleibt immer an |
| Kaputtes Paket nach Absturz oder Virenschutz-Eingriff | Oberfläche startet nicht → automatische Reparatur und zweiter Versuch |

## 11. Sicherheit

| Bedrohung | Maßnahme |
|---|---|
| Zugriff aus dem Netzwerk | Server nur an `127.0.0.1`; unter Windows `SO_EXCLUSIVEADDRUSE` (kein Port-Teilen mit fremden Programmen) |
| Andere Benutzer/Programme auf demselben Rechner | Zugang nur mit geheimem **Startschlüssel** (32 Zeichen, je Start neu) aus dem Startprogramm → Sitzungs-Cookie `HttpOnly; SameSite=Strict`; ohne Cookie nur eine Hinweisseite |
| Fremde Webseiten (CSRF, DNS-Rebinding) | Host-Kopfzeile muss `127.0.0.1:<port>`/`localhost:<port>` sein; Schreibzugriffe brauchen zusätzlich die Token-Kopfzeile `X-GL-Token` (Vergleich mit `hmac.compare_digest`) und eine passende `Origin`; keine CORS-Freigaben (OPTIONS/PUT/DELETE → 405) |
| Eingeschleuster Code in der Seite (XSS) | alle Texte maskiert; Hilfe-Markdown maskiert (auch Anführungszeichen, nur `https`-Links); **Content-Security-Policy** mit Nonce (`default-src 'none'`, keine Inline-Ereignisse), `X-Frame-Options: DENY`, `frame-ancestors 'none'`, `nosniff`, `Referrer-Policy: no-referrer`, COOP/CORP, `Permissions-Policy` |
| Pfad-Ausbruch | nur einfache Dateinamen (kein `/ \ :`, kein NUL, nicht versteckt), aufgelöster Pfad muss im Zielordner liegen (auch bei Verknüpfungen); Ordner-Einstellungen nur im Projekt- oder Benutzerordner, keine Netzwerkpfade; `--csv` muss `.csv` sein, Gänse-Bild ein vorhandenes Bild |
| Starten von Programmen | „Öffnen“ nur für bekannte Ordner und harmlose Typen (`.pdf .png .jpg .webp .csv .zip .txt .md`); andere Dateien werden nur als Download ausgeliefert |
| Kommandozeilen-Einschleusung | Generator-Aufruf ohne Shell, Werte als `--schalter=wert` (ein Wert kann kein Schalter werden), Prüfung mit dem echten Parser |
| Bösartige Bilder | Größe ≤ 40 MB, ≤ 60 MP vor dem Dekodieren, `Image.MAX_IMAGE_PIXELS` = 80 MP, `verify()`; Pillow ≥ 10.3 |
| Bösartige Modell-Dateien | Download nur von festen GitHub-Adressen über HTTPS, **SHA-256-Prüfung** vor der Nutzung, eingeschränkter Unpickler (nur Tensor-Bausteine), Speicherung als pickle-freie `.npz` (`allow_pickle=False`). KI-Bildmodell: feste Hugging-Face-Revision, Prüfsumme je Datei vor dem Umbenennen, nur `.safetensors` (reine Zahlen, Kopf und Grenzen geprüft – kein Code) und JSON/Text |
| KI-Bild: Eingaben | Beschreibung/Wort begrenzt und bereinigt; Unterprozess ohne Shell mit Werten als `--name=wert`; Bild-Kennungen nur 16 Hex-Zeichen; Ergebnis läuft wie jedes Foto durch die Prüfungen von Schritt 1 |
| CSV-/Formel-Einschleusung | Text, Wort und Notiz mit `= + - @` am Anfang werden abgelehnt; Zeilenumbrüche entfernt; Länge begrenzt |
| Hochgeladenes Gänse-Bild | gleiche Grenzen wie Schritt 1 (40 MB, 60 MP, `verify()`, kein HEIC), fester Dateiname, **neu kodiert** (nur Bildpunkte, keine Metadaten, max. 2400 px), atomar geschrieben, alte Fassung aufgehoben |
| Automatische Übersetzung: Datenschutz | nur nach **ausdrücklicher Zustimmung** (Fenster in der Oberfläche; ohne Zustimmung lehnt der Server mit 409 ab, ohne etwas zu senden); gesendet wird **nur das Wort** ohne „Gans“ (höchstens 80 Zeichen, ohne Steuerzeichen) bzw. beim KI-Bild auf Klick **nur die Beschreibung** (höchstens 300 Zeichen) – keine Bilder, Dateinamen, E-Mail-Adresse, Cookies; neutraler User-Agent; Texte, die wie E-Mail- oder Internetadressen aussehen, werden nicht gesendet; die Browser-Seite selbst spricht mit keinem fremden Rechner (CSP `connect-src 'self'` bleibt) |
| Automatische Übersetzung: Verbindung | nur `https` zu den fest eingetragenen Hosts (Port 443, keine Zugangsdaten in der Adresse), **Zertifikatsprüfung immer an** (System → truststore → certifi), **keine Weiterleitungen**, Zeitlimit 10 s, Antwort ≤ 1,5 MB und nur JSON, Mindestabstand 0,35 s und höchstens 40 Anfragen je Dienst und Minute |
| Automatische Übersetzung: Antworten | gelten als nicht vertrauenswürdig: nur erwartete JSON-Felder; Antworten mit HTML/Skript, Formelanfang (`= + @`) oder fremden Zeichen werden **ganz** verworfen (nicht in harmlos aussehende Stücke zerlegt); Steuer- und unsichtbare Zeichen (z. B. Richtungswechsel U+202E) entfernt, NFC, nur Buchstaben/Ziffern/übliche Satzzeichen, höchstens 60 Zeichen je Vorschlag; „/“ trennt Vorschläge; Anzeige immer maskiert; gespeichert erst nach Übernahme und mit Markierung |
| Automatische Übersetzung: Schlüssel | DeepL-Schlüssel nur in der Form `xxxxxxxx-…-xxxxxxxxxxxx(:fx)`, gespeichert in `uebersetzung.json` im Datenordner (0600; unter Windows im Benutzerprofil), nie im Projektordner oder in der Projekt-ZIP, nie an die Seite (nur „…abc:fx“), nur an DeepL im Kopf `Authorization` |
| Nach neuer Version suchen | nur auf Klick, eine `GET`-Anfrage an `api.github.com` (eigene Host-Liste, HTTPS, Zertifikatsprüfung, keine Weiterleitung, 10 s, ≤ 200 KB, nur JSON), ohne Cookies oder Daten über Person/Karten; Konto/Repository nur aus `web_adresse.txt`; aus der Antwort nur Versionsnummer + Datum, Link immer aus `web_adresse.txt`; nichts wird gespeichert; nur am Rechner |
| Vorlesen (🔊) | nur Stimmen mit `localService` (offline) – kein Text verlässt dafür den Rechner bzw. das Gerät |
| Große Anfragen | JSON ≤ 2 MB, Bilder ≤ 40 MB, Socket-Zeitlimit 120 s |
| Datenverlust | kein Löschen: Bilder → `bilder/_entfernt/`, vorige `karten.csv` → `karten.bak.csv`, Schreiben atomar |
| Informationsabfluss | Server-Kopfzeile ohne Python-Version; Projekt-ZIP ohne `ui_einstellungen.json`, Verknüpfungen und große Modelle |
| Paket-Lieferkette | seit 2.5 feste Fassungen mit SHA-256 je Rad (`pakete.lock`, Ersatz-Sätze, `pakete-sprachen.lock` für uharfbuzz; gebaut aus `requirements.txt` + PyPI für Windows, macOS und Linux je x64/ARM) und `pip --require-hashes` – auch eine neue Fassung auf PyPI oder ein manipulierter Spiegel ändert nichts; nur fertige Räder (`--only-binary=:all:`, nie Kompilieren); Installation nur aus PyPI über HTTPS. `requirements.txt` (Spannen) dient nur Entwicklern und dem CI-Job „neueste Fassungen“ (`MGD_PAKETE_NEUESTE=1`, Frühwarnung) |
| Manipulierter Python-Download | nur offizielle Quellen (python.org, python-build-standalone auf GitHub) über HTTPS; **SHA-256 fest in den Startdateien**, Prüfung vor dem Entpacken; Windows-Python ist von der PSF signiert |
| Untergeschobene Programme | Systemprogramme mit vollem Pfad (kein `curl.exe`/`tar.exe` aus dem aktuellen Ordner oder `PATH`); `PYTHONHOME`/`PYTHONPATH`/`PYTHONSTARTUP` werden geleert; Windows-Python läuft isoliert (`._pth`) |
| Startschlüssel auf der Platte | Instanz-Datei nur für den eigenen Benutzer lesbar (0600), wird beim Beenden gelöscht; verwaiste Dateien werden erkannt und entfernt |

Nicht nötig: Administratorrechte, ein vorinstalliertes Python, Abschalten von Smart App Control, Öffnen von Ports in der Firewall.

## 12. Selbsttest `test_gans_lernkarten.py`

Prüft in einer temporären Kopie des Projekts mit den Beispielkarten (239 Prüfungen, ohne installiertes Real-ESRGAN 234;
ca. 1–2 min; die Kopie rechnet mit FSRCNN, Real-ESRGAN wird an einem kleinen Ausschnitt geprüft; die eigene
`karten.csv`, die eigenen Bilder und die eigenen Einstellungen bleiben außen vor, der Test sendet nie etwas ins Internet): Bildverbesserung (Ränder, Guided-Filter, FSRCNN, Real-ESRGAN, Qualitätsstufen,
sicherer Modell-Leser, Prüfsumme), Textlayout, komplette Läufe (Seiten, Maße, TrimBox, Schriften, 300 dpi,
Einzelbilder, Vorlagen, Zwischenspeicher, Schalter, CSV-Fehler, Meldungen in drei Sprachen), Kartenliste, alle Prüfungen
von Schritt 1 und 2, die Oberfläche (Startschlüssel, Cookie, Sicherheits-Kopfzeilen, Host/Origin/Token, Pfad-Ausbrüche,
Ordner-Grenzen, „Öffnen“-Sperre, Schritt 1 und 2 komplett über die Schnittstelle, Sprachen, Läufe, ZIP, Hilfe, Beenden)
und das Startprogramm (Startdateien: ASCII/CRLF, Sprungziele, Klammerblöcke, Prüfsummen, `sh -n`; Erkennung des ersten
Starts, Sprachen, pip-Fehlerarten, Smart-App-Control-Erkennung, Start aus der ZIP, Paketprüfung, Instanz-Datei,
Wiederfinden und Beenden der Oberfläche) sowie die Neuerungen von 1.5 (Wiktionary-Leser, Reihenfolge, Bereinigung
bösartiger Antworten, Adress-Sperre, Weiterleitungen, Zustimmung, Dienst-Reihenfolge, Zwischenspeicher, Schlüssel
außerhalb des Projekts; `--nur verbessern`, `--bild`, Übersetzungsstatus, Beispielkarten und -bilder ohne Überschreiben; Gänse-Bild per Schnittstelle
inkl. Metadaten-Entfernung und Ablehnungen; Bildverbesserung mit Status und Vorher/Nachher; Tabelle und „geprüft“;
Entwürfe mit Wort; Projekt-ZIP; Übernahme der eigenen Karten bei neuem Ordner, auch frisch entpackt). Start: `python3 test_gans_lernkarten.py`
oder „Werkzeuge → Selbsttest“. Vor der Auslieferung zusätzlich ein Browser-Test (Playwright) aller neuen Abläufe mit
gefälschtem Übersetzungsdienst, auch in Englisch, Spanisch und in Handy-Breite.
Zusätzlich vor der Auslieferung: kompletter Erst-Start mit der Mac-/Linux-Startdatei in einem leeren Benutzerordner
(Python-Download, Prüfsumme, Pakete, Modell, Menüeintrag, Oberfläche), zweiter Start, Beenden, verschobener Ordner,
neuer Ordner, pip aus dem Rad, beschädigtes NumPy mit automatischer Reparatur, zwei gleichzeitige Starts.

## 13. Checkliste vor dem Druck

- [ ] Prüfbogen ansehen; Übersetzungen von einer Muttersprachlerin / einem Muttersprachler prüfen lassen – im Reiter
      „Tabelle“ abhaken; „automatisch übersetzt“ darf vor dem Druck nicht mehr vorkommen.
- [ ] Rote Hinweise (Bildauflösung, Textlänge) klären.
- [ ] Probedruck bzw. Testbogen; Rückseite richtig herum? Sonst `--rs-drehen`.
- [ ] Heimdruck: 100 % („Tatsächliche Größe“), beidseitig, Wenden an der langen Kante.
- [ ] Druckerei: Maße mit Abschnitt 3 vergleichen (Endformat, Beschnitt, Hochformat-Pflicht).
- [ ] Bildrechte: Die Bilder stammen aus dem Internet – für private Lernkarten unkritisch, vor Weitergabe oder Verkauf klären.

## 14. Annahmen und Grenzen

- Signierte Updates (seit 2.5): die Signaturprüfung schützt erst Updates **ab** 2.5 – das Update von 2.4 auf 2.5 prüft noch nur die Prüfsumme aus demselben Release (2.4 kennt die Signatur nicht). Ed25519 ist in reinem Python nicht zeitkonstant; geprüft wird nur Öffentliches, signiert nur auf Lukas’ Rechner. Wer den Haupt-Schlüssel (DPAPI, Windows-Konto) **und** das GitHub-Konto übernimmt, könnte weiterhin ein Update ausliefern – darum Reserve offline. minisign-Kompatibilität prüft der Frischtest unter Linux mit dem echten `minisign` (beide Richtungen).
- Die Beispiele sind Adjektive/Adverbien und eine Wendung („arg Hunger“), keine Verben; die Vorlage funktioniert für jede Wortart.
- „Spanisch“ meint immer das in Mexiko gesprochene Spanisch (Übersetzungsvorschläge bevorzugen mexikanische Varianten). Die Übersetzungen sind Vorschläge zur Prüfung – auch die automatischen:
  Wörterbücher und Übersetzungsdienste kennen den Wortwitz nicht und treffen bei mehrdeutigen Wörtern nicht immer die
  gemeinte Bedeutung.
- Die Übersetzungsdienste konnten beim Bau nur mit nachgebildeten Antworten geprüft werden (die Bauumgebung erreicht
  sie nicht); ändert ein Dienst sein Antwortformat, meldet das Programm „Unerwartete Antwort“ und nimmt den nächsten.
- Die Gans auf der Rückseite ist gezeichnet (Vektor) und mit `--gans-bild` austauschbar; das Programmsymbol (Gans mit
  Sombrero und Sarape) erscheint nur in Oberfläche, Anleitung und Verknüpfung, nicht auf den Karten.
- Real-ESRGAN erfindet in der Regel keine Buchstaben, kann aber feine Strukturen „malerisch“ glätten; der Prüfbogen zeigt das Ergebnis.
- Release 1.6 wurde am 12.10.2026 auf Windows 11 mit eingeschalteter Smart App Control aus der ZIP-Datei frisch
  eingerichtet (Startdatei, Python-Download mit Prüfsumme, Pakete, Real-ESRGAN, Verknüpfungen: 27 s) und hat alle
  Druck- und Digitaldateien erzeugt. Seit 2.2 laufen Installation über die Startdatei, Oberfläche (per API), Tools,
  Druck in drei Schriftsystemen, beide Testreihen, Update und Deinstallation automatisch auf GitHub-Rechnern mit Windows
  (x64, ARM), macOS (Apple Silicon, Intel) und Linux (x64, ARM, schlankes Debian nur mit wget) – ohne echte Geräte,
  ohne Doppelklick und ohne Systemdialoge (SmartScreen, Smart App Control, Gatekeeper). Dazu ein Browser-Test unter
  Playwright (nur im CI): Download-Seite (Sprache, Systemerkennung, Link), Installationsseiten und LIES MICH in Chromium,
  Firefox und WebKit (Safaris Engine) am Rechner- und Handy-Format, die Oberfläche (Willkommen, Karten bearbeiten, Lernen,
  Farben, Hilfe, Tippflächen) und die Handy-App (Service Worker, Pyodide, Heimdruck-PDF, Lernen, Sicherung, offline).
  WebKit unter Playwright ist nicht dasselbe wie ein iPhone (kein „Zum Home-Bildschirm“, keine 7-Tage-Löschung, keine
  echte Kamera/Teilen-Leiste). Ein Release wird nur nach grünem Lauf für genau diesen Inhalt veröffentlicht; nach jedem Push
  auf `main` prüft die Release-Prüfung das veröffentlichte Release erneut (sobald ZIP und Download-Seite zu `main` passen;
  frisch installiert mit den dann neuesten Paketfassungen) und die Live-Adressen.
- Ob Smart App Control die Paket-DLLs zulässt, hängt von deren Ruf bei Microsoft ab und kann sich ändern; das
  Startprogramm erkennt eine Sperre und reagiert, kann sie aber nicht umgehen. Beim Test von 1.6 waren bei der ganz
  neuen NumPy 2.5.4 nur die Teile von `numpy.random` gesperrt, die das Programm nicht braucht; der Selbsttest
  `test_gans_lernkarten.py` nutzt sie und läuft dann erst, wenn Windows die Fassung kennt (`test_erweiterungen.py`
  kommt ohne aus).
- Die Drehrichtung der Rückseite hängt vom Dienst ab – immer den Probedruck prüfen.
- KI-Bilder: Das Modell versteht praktisch nur Englisch, schreibt keinen sauberen Text, kennt keine genauen Anzahlen,
  tut sich mit Menschen-Tätigkeiten, Gegenständen in Schnabel/Füßen und bestimmten Rassen schwer und malt ab und zu
  ein Bein oder einen Hals zu viel (→ neu würfeln). „Keine Menschen“ ist ein Versuch, kein Versprechen. Ein Bild dauert
  auf einem Laptop von 2023 gut eine Minute (ältere Rechner länger), braucht ca. 3 GB Arbeitsspeicher; auf dem Handy
  selbst wird nicht gerechnet. Geprüft auf Windows 11 mit dem echten Modell; macOS und Linux nach denselben Regeln
  und mit Tests (das 3,5-GB-Modell auch nicht in den automatischen Tests auf GitHub-Rechnern).
- Handy: geprüft mit Handy-Emulation (375 px, Touch), nicht auf echten Geräten. Die Handy-App (Web-App) wurde im
  eingebauten Browser (Chromium) unter einem lokalen Server mit Unterordner geprüft – Installation, Offline-Start,
  Update, Sicherung, Lernen, Druck-PDF, Abbrechen; seit 2.2 automatisch auch in WebKit und Firefox (Browser-Test,
  Abschnitt oben) – echte iPhones/Android-Geräte bleiben ungeprüft. Am Handy rechnet Python als
  WebAssembly langsamer als am Rechner; KI-Bilder gibt es dort nicht. Website-Daten können ohne Installation (iPhone:
  nach 7 Tagen) oder bei Platzmangel gelöscht werden → App installieren, ab und zu sichern.
- Karten lernen: FSRS-6 mit den Standardparametern (keine persönliche Optimierung der Gewichte wie in Anki); die
  Intervalle sind deshalb anfangs „durchschnittlich“ statt auf dich zugeschnitten.
- Sprachpakete: Schriften kommen mit fester Revision und SHA-256, uharfbuzz (nur Hindi/Arabisch) per pip in fester
  Fassung mit eigener SHA-256 je Rad (`pakete-sprachen.lock`, seit 2.5).
- Feste Paketfassungen (seit 2.5): die Lock-Dateien enthalten Räder für Python 3.13 unter Windows x64 (+ ARM, falls
  vorhanden), macOS Intel/Apple Silicon und Linux x64/ARM mit glibc; andere Umgebungen (z. B. Linux mit musl, ein
  fremdes Python ≠ 3.13) bekommen keine passende Datei. Neue Fassungen kommen nur mit einer neuen Programmversion
  (`bau_lock.py --neueste` in der Release-Gruppe, CI auf allen Systemen); der Job „neueste Fassungen“ der
  Release-Prüfung warnt vorher, wenn neue Fassungen etwas kaputt machen.
- Update im Programm (seit 2.4): die Prüfsumme stammt vom selben GitHub-Release wie das ZIP – sie schützt vor kaputten
  oder unterwegs veränderten Downloads, ersetzt aber keine Signatur (wie beim Download über die Seite). Dateien, die ein
  neues Release nicht mehr enthält, bleiben im Ordner liegen (nie wird geraten, was eigene Daten sein könnten). Der
  echte Neustart über die Startdatei läuft in den automatischen Tests auf allen GitHub-Rechnern (Stufe k des
  Frischtests mit einem Release-Server auf 127.0.0.1), lokal unter Windows nur in Teilen (sonst entstünden echte Symbole).
- Rückgängig (seit 2.4) gilt nur für die laufende Sitzung und nur für die eigenen Daten des Programms; was außerhalb
  geändert wird (z. B. `karten.csv` in Excel), bricht den Verlauf zur Sicherheit ab. Der Lernstand einer Karte, deren Text
  zurückgenommen wird, beginnt wie bei jeder Änderung von vorn.

## 15. Ordner und Dateien

```
Me-Goos-ta-Deutsch/
├─ Me Goos-ta Deutsch - Windows.cmd   Startdatei Windows (erster Start: richtet alles ein)
├─ Me Goos-ta Deutsch - Mac.command   Startdatei Mac (und Linux)
├─ Me Goos-ta Deutsch - Linux.sh      Startdatei Linux (ruft die Mac-/Linux-Startdatei auf)
├─ LIES MICH ZUERST.html              Anleitung mit Bildern (Deutsch, Englisch, Spanisch)
├─ Me Goos-ta Deutsch - Android.html  Handy-App installieren: Link, QR-Code, Schritte (auch … - iPhone / - Google Pixel)
└─ Programm/
   ├─ starter.py                Startprogramm: Erkennung, Einrichtung, Start, Reparatur
   ├─ LEITFADEN.md              Ablauf Schritt für Schritt (…_en.md Englisch, …_es.md Spanisch)
   ├─ SPEC.md                   diese Spezifikation
   ├─ gans_lernkarten.py        Generator, Prüfungen von Schritt 1 und 2
   ├─ ki_modelle.py             KI-Bildvergrößerung in NumPy, Modell-Download mit Prüfsumme
   ├─ ki_bild.py                KI-Bilder (Segmind Vega + VegaRT) in NumPy, Modell-Download mit Prüfsummen (9.3)
   ├─ tools.py                  Tools: Katalog, Zustand, installieren (Auftrag für die Warteschlange), deinstallieren (9.4)
   ├─ sprachen.py               Sprachen der Rückseite: Katalog (15), Sprachpakete laden/prüfen/entfernen (9.4)
   ├─ lernen.py                 Karten lernen: FSRS-6, Lernstand, Sitzung, Stapel, Statistik (9.4)
   ├─ verlauf.py                Rückgängig/Wiederholen der eigenen Daten (Schritte, Kopien in ausgabe/.verlauf) (9)
   ├─ aktualisieren.py          Update im Programm: Release laden/prüfen, im selben Ordner ersetzen, neu starten (9)
   ├─ signatur.py               Signatur der Releases prüfen: Ed25519 (RFC 8032), minisign-Format, vertraute Schlüssel (9)
   ├─ DRITTLIZENZEN.md          Lizenzen der Bestandteile von anderen (inkl. KI-Modelle)
   ├─ uebersetzer.py            Übersetzungsvorschläge (Wiktionary, MyMemory, DeepL) mit Schutzmaßnahmen
   ├─ gans_ui.py                Oberfläche: Logik aller Adressen (verarbeite) + lokaler Server als Hülle
   ├─ leinwand.py               Pillow-Leinwand: Rückseiten-Vorschau ohne pypdfium2 (Web-App)
   ├─ qr_code.py                QR-Code ohne Zusatzpaket (wie qrSvg() der Seite) für die Installationsdateien
   ├─ web_adresse.txt           Adresse der Handy-App (eine Zeile https://…; leer = nicht veröffentlicht)
   ├─ erweiterungen.py          Import/Export, Ideen, Programmstart, Deinstallieren, Handy-Zugang (von gans_ui.py eingebunden)
   ├─ lernkarten_digital.py     digitale Lernkarten: Anki-Paket, Lernseite, Bildschirm-PDF, CSV
   ├─ duck_spinner.py           Lade-Ente für die Konsole
   ├─ test_erweiterungen.py     Selbsttest der Erweiterungen
   ├─ ideen.json, ideen/        eigene Ideen für künftige Karten (entstehen beim ersten Anlegen)
   ├─ lernstand.json            Lernstand (Tool „Karten lernen“); lernstand.bak.json = vorige Fassung
   ├─ ui/index.html             Seite der Oberfläche (drei Sprachen)
   ├─ test_gans_lernkarten.py   Selbsttest
   ├─ beispiel-karten.csv       die 10 Beispielkarten (Vorlage für eine fehlende karten.csv)
   ├─ beispiel-bilder/          die Bilder der Beispielkarten (werden mit der Beispielliste nach bilder/ kopiert)
   ├─ karten.csv                eigene Kartenliste (entsteht beim ersten Start); karten.bak.csv = vorige Fassung
   ├─ requirements.txt          benötigte Python-Pakete (Spannen, für Entwickler)
   ├─ pakete.lock               feste Fassungen mit SHA-256 (Erststart); pakete-bewaehrt|-aelter.lock = Ersatz-Sätze
   │                            (Smart App Control), pakete-sprachen.lock = uharfbuzz (gebaut von bau_lock.py)
   ├─ ui_einstellungen.json     Einstellungen und Sprache der Oberfläche (entsteht automatisch)
   ├─ bilder/                   Vorderseiten-Bilder (entsteht beim ersten Start); _entfernt/ = Papierkorb
   ├─ modelle/                  fsrcnn_x2|x3|x4.npz, Lizenzen, README; realesrgan-*.npz nur mit dem Tool Bildverbesserung
   ├─ assets/                   Programmsymbol (SVG, PNG, ICO, ICNS); eigenes Gänse-Bild gans_hintergrund.jpg|png,
   │                            _alt/ = frühere Gänse-Bilder
   ├─ werkzeuge/                pip-Rad für Windows; optional pakete/ für Rechner ohne Internet
   ├─ schrift/                  Poppins (Regular, Medium, Bold) + Lizenz
   ├─ vorlagen/                 leere Vorlagen (Druckerei, Heimdruck)
   ├─ ausgabe/                  PDFs, Prüfbogen, einzelbilder/, bericht.json, .cache/, .entwuerfe/, .ki-bild/
   └─ _beispiele/               nur nach einer Übernahme: die dabei ersetzten Beispieldateien dieser Version

Datenordner (entsteht beim ersten Start):  Windows %LOCALAPPDATA%\Me-Goos-ta-Deutsch · Mac ~/Library/Application
Support/Me-Goos-ta-Deutsch · Linux ~/.local/share/me-goos-ta-deutsch
   python/  eigenes Python mit Paketen · modelle/  Kopie der Bildverbesserung, modelle/ki-bild/  KI-Bildmodell (3,5 GB)
   starte.py  Ziel des Desktop-Symbols · handy-port.txt  gemerkter Port des Handy-Zugangs
   eingerichtet.json  Stempel · programm-ort.txt · laeuft-<ordner>.json  laufende Oberfläche
   protokoll.txt  Einrichtung · oberflaeche.txt  Meldungen der Oberfläche
   uebersetzung.json  Zustimmung, Dienst, DeepL-Schlüssel (0600) · uebersetzungen.json  gemerkte Vorschläge
   start.json  Programmstart (Browser oder eigenes Fenster) · tools.json  Tools: Erstabfrage, Aktivierungen, abgemeldete
```

## 16. Quellen (gelesen im Oktober 2026)

- Smart App Control, gesperrte Dateitypen: https://support.microsoft.com/en-us/topic/smart-app-control-has-blocked-an-app-with-a-dangerous-file-extension-60343058-66f2-4548-b978-e484e13abe89
- Smart App Control und Mark of the Web: https://www.bleepingcomputer.com/news/microsoft/windows-11-smart-app-control-blocks-files-used-to-push-malware/ · https://textslashplain.com/2026/04/28/smart-app-control/
- Wiedereinschalten ohne Neuinstallation (KB5083769): https://blog-en.topedia.com/2026/04/smart-app-control-in-windows-11-can-now-be-re-enabled-without-reinstalling/
- Skript-Hosts in App Control: https://learn.microsoft.com/windows/security/application-security/application-control/app-control-for-business/design/script-enforcement
- Python unter Windows / Install Manager: https://docs.python.org/3/using/windows.html · https://www.python.org/downloads/release/pymanager-263/ · https://peps.python.org/pep-0773/
- Embeddable Python 3.13.16 (SHA-256 aus der Release-Seite): https://www.python.org/downloads/release/python-31316/ · https://docs.python.org/3/using/windows.html#the-embeddable-package
- python-build-standalone 20260924 (SHA256SUMS): https://github.com/astral-sh/python-build-standalone/releases/tag/20260924
- Real-ESRGAN: https://github.com/xinntao/Real-ESRGAN · SwinIR: https://github.com/JingyunLiang/SwinIR · HAT: https://github.com/chxy95/HAT
- FSRCNN-Gewichte: https://github.com/Saafke/FSRCNN_Tensorflow
- DeepL-API, Sprachen (u. a. `ES-419`): https://developers.deepl.com/docs/getting-started/supported-languages
- MyMemory-API (Grenzen ohne Konto, Parameter): https://mymemory.translated.net/doc/spec.php · https://lilting.ch/en/articles/mymemory-api
- Wiktionary-Übersetzungstabellen (`Ü-Tabelle`, `Ü`): https://de.wiktionary.org/wiki/Vorlage:%C3%9C-Tabelle · Format nachvollzogen an den
  Testdaten von wiktextract: https://github.com/tatuylonen/wiktextract (tests/test_de_translation.py)
