# Me Goos-ta Deutsch – Leitfaden

Stand: 20.10.2026 · Programm und Oberfläche Version 2.1 · Englisch: `LEITFADEN_en.md` · Spanisch: `LEITFADEN_es.md`

Schön, dass du da bist! Dieser Leitfaden begleitet dich vom ersten Doppelklick bis zur fertigen Karte – Schritt für Schritt und ohne Fachchinesisch. Du musst ihn nicht von vorn bis hinten lesen: Spring einfach zu dem Teil, den du gerade brauchst. Und keine Sorge – das ist hier kein Gänsemarsch, du kannst jeden Schritt in deinem Tempo gehen.

## Überblick

Me Goos-ta Deutsch macht aus Bildern mit einem „Gans …“-Wortwitz druckfertige Lernkarten: vorne das Bild, hinten das Wort auf {{Spanisch}} mit einer frechen Gans in der Ecke. Mit Spanisch ist hier immer das in Mexiko gesprochene Spanisch gemeint – die Übersetzungsvorschläge bevorzugen darum mexikanische Wörter. Neue Karten entstehen in vier Schritten, alle in der Oberfläche:

| Schritt | Was passiert |
| --- | --- |
| 1 Bilder vorbereiten | Ein Bild oder gleich viele hinzufügen – oder mit **🪄 Gans mit KI erzeugen** ein realistisches Gänse-Foto aus einer kurzen Beschreibung malen lassen (offline). Das Programm prüft Format, Größe und Schärfe, zeigt die Vorderseite und benennt jede Datei nach dem Text auf dem Bild. Das Wort auf {{Spanisch}} kann gleich mit – selbst getippt oder als Vorschlag (🌐) |
| 2 Karten beschriften | Fehlende Wörter auf {{Spanisch}} eintragen oder vorschlagen lassen. Das Programm prüft, ob sie auf die Karte passen, und zeigt die Rückseite live |
| 3 Erzeugen | In drei kleinen Schritten: Ziel wählen (Drucken zu Hause, Druckerei, Prüfbogen, digitale Lernkarten …), Feinschliff, los. Noch nicht verbesserte Bilder poliert die KI (Real-ESRGAN) dabei auf |
| 4 Prüfen & drucken | Prüfbogen ansehen, dann zu Hause, in einer Druckerei oder digital am Handy lernen |

Dazu helfen dir jederzeit:

- **Tabelle** – Vorder- und Rückseite aller Karten nebeneinander, ideal zum Prüfen der Übersetzungen.
- **Bildverbesserung** – Bilder schon vorab verbessern und Vorher/Nachher vergleichen.
- **Ideen** – halbe Ideen parken und später in Ruhe fertig machen.
- **Werkzeuge** und **Hilfe** – alles Weitere, vom Handy-Zugang bis zum Selbsttest.
- **Deinstallieren** – der letzte Reiter, falls du dich je verabschieden möchtest (wir hoffen nicht!).

Kleine Hinweise beim Draufzeigen verraten dir zu fast jedem Knopf, was er tut.

| Ergebnis (Ordner `ausgabe/`) | Wofür |
| --- | --- |
| `Me-Goos-ta-Deutsch_Pruefbogen.pdf` | Kontrolle vor dem Druck: Vorder- und Rückseite jeder Karte, Texte, Bildschärfe |
| `Me-Goos-ta-Deutsch_Heimdruck_A4_88x63.pdf` (oder `_Letter_`) | Selbst drucken auf Karton, 8 Karten je Bogen, mit Schnittmarken |
| `Me-Goos-ta-Deutsch_Druckerei_88x63.pdf` | Für eine Druckerei: eine Seite je Kartenseite, mit 3 mm Beschnitt |
| `einzelbilder/` | Eine PNG-Datei je Kartenseite für Druckereien, die Bilder statt PDF annehmen |
| `digital/` | Anki-Paket, Lernseite für den Browser, Bildschirm-PDF und auf Wunsch Tabellen für andere Lern-Apps |

Die Oberfläche spricht Englisch, Deutsch und Spanisch – Umschalten oben rechts (EN · DE · ES). Beim allerersten Start ist Englisch eingestellt; der Willkommens-Assistent fragt dich gleich nach deiner Lieblingssprache. Auch alles davor – die Anleitung „LIES MICH ZUERST“, die Meldungen der Startdatei, das Einrichtungsfenster und der Ladebildschirm der Handy-App – startet auf Englisch und folgt danach deiner Wahl. Die Karten selbst bleiben beim Umschalten natürlich gleich.

## Einmalige Einrichtung

Vorher musst du nichts installieren – auch kein Python. Die Startdatei richtet beim ersten Start alles selbst ein: ein eigenes Python im Benutzerordner (**ohne Administratorrechte**; andere Python-Installationen bleiben unberührt), die Pakete und ein Symbol zum Starten. Das dauert 3–10 Minuten und braucht einmalig Internet (ca. 90 MB) – Zeit für einen Tee. Größere Extras wie die KI-Bildverbesserung sind **Tools**: Du lädst nur, was du wirklich willst (siehe „Tools“). Die Datei **„LIES MICH ZUERST“** im Download zeigt alles noch einmal mit Bildern.

**Woher?** Die Download-Seite https://lukasdiegans.github.io/me-goos-ta-deutsch/download/ hat eine ZIP-Datei für Windows, macOS und Linux (kostenlos, über GitHub Releases), dazu die Schritte für dein System und die SHA-256-Prüfsumme. Später steht der Link auch im Programm unter **Hilfe → „Über dieses Programm“** (in der Handy-App: **Mehr → „Auch für den Rechner holen“**).

**Windows 11 und 10**

1. **ZIP freigeben** (wichtig bei Windows 11): Rechtsklick auf die ZIP-Datei → „Eigenschaften“ → unten bei „Sicherheit“ **„Zulassen“** anhaken → „OK“. Sonst blockiert die Intelligente App-Steuerung die Startdatei (siehe „Start unter Windows und Smart App Control“).
2. **ZIP entpacken:** Rechtsklick → „Alle extrahieren …“, zum Beispiel nach `Dokumente`.
3. **Doppelklick auf `Me Goos-ta Deutsch - Windows`.** Ein Fenster zeigt die Einrichtung Schritt für Schritt, und eine kleine Ente schwimmt mit, solange etwas lädt. Danach öffnet sich die Oberfläche im Browser, und auf dem Desktop (und im Startmenü) liegt das Symbol **„Me Goos-ta Deutsch“**.
4. Ab dann: Doppelklick auf das Desktop-Symbol – die Oberfläche startet in Sekunden, ohne schwarzes Fenster.

**Mac:** ZIP per Doppelklick entpacken, dann `Me Goos-ta Deutsch - Mac` doppelklicken. Verweigert macOS das Öffnen: ab macOS 15 unter Systemeinstellungen → Datenschutz & Sicherheit → „Dennoch öffnen“; bis macOS 14 mit Control-Klick → „Öffnen“. Klappt immer: im Programm „Terminal“ `sh ` tippen, die Datei hineinziehen, Eingabetaste. Danach liegt „Me Goos-ta Deutsch“ im Launchpad bzw. im Ordner „Programme“ deines Benutzerordners.

**Linux:** ZIP entpacken, im Ordner ein Terminal öffnen und `sh "Me Goos-ta Deutsch - Linux.sh"` eingeben – oder Rechtsklick auf die Datei → „Als Programm ausführen“ (dann öffnet sich das Terminal von selbst). Danach steht „Me Goos-ta Deutsch“ im Anwendungsmenü. Gebraucht werden nur `curl` oder `wget` und `tar` – die sind fast immer schon da.

**Willkommen!** Beim ersten Öffnen begrüßt dich ein kleiner Assistent: Sprache wählen, festlegen, ob sich das Programm im Browser oder in einem eigenen Fenster öffnet, die gewünschten Tools ankreuzen (nichts ist vorausgewählt) und eine kurze Tour – dann geht’s los. „Später fragen“ zeigt ihn beim nächsten Start noch einmal.

**Funktioniert alles?** Unter „Werkzeuge“ auf „Selbsttest starten“ klicken. Am Ende steht „ALLE TESTS BESTANDEN“ – alles im grünen Bereich.

**Was das Startprogramm bei jedem Start erkennt:** erster Start → alles einrichten · Oberfläche läuft schon → nur den Browser öffnen · neue Programmversion oder neuer Ordner → nur das Nötige nachholen und anbieten, deine Karten aus dem bisherigen Ordner zu übernehmen · etwas fehlt oder ist beschädigt → selbst reparieren · zwei Starts gleichzeitig → der zweite wartet geduldig. Python, Protokolle und Einstellungen liegen in `%LOCALAPPDATA%\Me-Goos-ta-Deutsch` (Mac: `~/Library/Application Support/Me-Goos-ta-Deutsch`, Linux: `~/.local/share/me-goos-ta-deutsch`), deine Arbeit im Ordner `Programm` (Bilder, `karten.csv`, `ausgabe`).

Die Oberfläche läuft im Hintergrund weiter, auch wenn der Browser-Tab geschlossen ist; ⏻ oben rechts beendet sie. Ein erneuter Start öffnet einfach wieder den Browser.

## Neue Version installieren (Update)

Deine Arbeit liegt im Ordner `Programm`: die Kartenliste `karten.csv`, die Bilder in `bilder/`, deine Ideen in `ideen/`, Druckdateien und verbesserte Bilder in `ausgabe/`, die Einstellungen in `ui_einstellungen.json` und ein eigenes Gänse-Bild in `assets/`. Der Download einer neuen Version enthält nichts davon – seine Beispielkarten liegen als `beispiel-karten.csv` und `beispiel-bilder/` bei und werden nur in einem ganz neuen Ordner verwendet. So geht beim Update nichts verloren.

**Die neue Version** gibt es immer auf der Download-Seite – im Programm unter **Hilfe → „Über dieses Programm“**, Link „Neueste Version für Windows, macOS und Linux“.

**Am sichersten:** Vorher unter **Import / Export** eine Komplettsicherung herunterladen. Die lässt sich überall wieder einlesen.

**Empfohlen: in einen neuen Ordner entpacken**

1. Die laufende Oberfläche beenden (⏻ oben rechts).
2. Die neue ZIP freigeben (Windows: Eigenschaften → „Zulassen“) und mit „Alle extrahieren …“ entpacken – Windows schlägt dafür von selbst einen neuen Ordner vor.
3. Im neuen Ordner die Startdatei doppelklicken. Sie erkennt den bisherigen Ordner und fragt, ob deine Karten übernommen werden sollen – mit **Ja** (im Startfenster einfach Enter). Kopiert werden Karten, Bilder, Ideen, verbesserte Bilder, Einstellungen und ein eigenes Gänse-Bild. Python, Pakete und installierte Tools werden weiterverwendet – nichts muss neu geladen werden.
4. Das Desktop-Symbol startet ab jetzt die neue Version. Der bisherige Ordner bleibt unverändert; du kannst ihn löschen, sobald alles passt.

Die Beispielkarten der neuen Version liegen nach der Übernahme in `Programm/_beispiele/`. Mit **Nein** startet die neue Version mit den Beispielkarten; übernehmen kannst du dann jederzeit per **Import** einer Sicherung.

**Auch möglich: über den alten Ordner entpacken.** Beim Entpacken den Ordner wählen, in dem dein bisheriger Ordner liegt, und „Dateien im Ziel ersetzen“ wählen. Ersetzt werden nur Programmdateien – Kartenliste, Bilder, Ideen, Druckdateien, Einstellungen und Gänse-Bild bleiben, wie sie sind. Danach einmal die Startdatei doppelklicken.

## Start unter Windows und Smart App Control

Windows 11 hat eine Schutzfunktion namens **Intelligente App-Steuerung** (Smart App Control). Sie blockiert aus dem Internet geladene Startdateien wie `.cmd`, wenn sie nicht signiert sind. „Aus dem Internet“ erkennt Windows an einer unsichtbaren Markierung, die es beim Herunterladen setzt und beim Entpacken an alle Dateien weitergibt. Signierte Programme dürfen dagegen laufen – dazu gehört das offizielle Python von python.org, das die Startdatei verwendet.

| Möglichkeit | Admin nötig? | Bewertung |
| --- | --- | --- |
| ZIP vor dem Entpacken freigeben: Eigenschaften → „Zulassen“ → OK, dann entpacken | nein | **empfohlen** – danach trägt keine Datei die Markierung |
| Nur die Startdatei freigeben: Rechtsklick auf `Me Goos-ta Deutsch - Windows` → Eigenschaften → „Zulassen“ → OK | nein | gut, wenn schon entpackt wurde – die Startdatei entfernt die Markierung danach selbst von allen Programmdateien |
| Desktop-Symbol (entsteht beim ersten Start) | nein | für jeden weiteren Start – es entsteht auf deinem Rechner und trägt keine Markierung |
| „Als Administrator ausführen“ | ja | nicht nötig |
| Intelligente App-Steuerung ausschalten | ja | nicht empfohlen – sie schützt vor Schadsoftware |

Bibliotheken wie Pillow und NumPy enthalten Programmteile (DLLs), die nicht von Microsoft signiert sind. Sperrt die Intelligente App-Steuerung eine davon, erkennt das Startprogramm das, probiert selbst ältere, weit verbreitete Fassungen und erklärt dir, falls nötig, die übrigen Möglichkeiten. Wird nur die Vorschau-Bibliothek pypdfium2 gesperrt, schaltet es sie ab – die PDFs entstehen trotzdem, und die Vorschau der Rückseite zeichnet das Programm dann selbst.

## Die Oberfläche

| Bereich | Was du dort machst |
| --- | --- |
| Meine Karten | Alle Karten mit Vorschau (Klick dreht die Karte um), Bildqualität und Hinweisen. Bearbeiten, drucken oder pausieren, Reihenfolge ändern, aus der Liste nehmen – jede Änderung wird sofort gespeichert |
| 🎓 Lernen | Karten lernen wie mit Anki: heute fällige und neue Karten, eigene Stapel, Statistik, Einstellungen (Tool „Karten lernen“) |
| Tabelle | Vorder- und Rückseite aller Karten nebeneinander: vergleichen, direkt ändern, Übersetzung als „geprüft“ abhaken, filtern, suchen, drucken |
| Bildverbesserung | Bilder vorab verbessern, Stand je Bild, Vorher-Nachher-Vergleich |
| 1 Bilder vorbereiten | Neue Bilder hinzufügen (gern viele auf einmal), prüfen, benennen, gleich beschriften, übernehmen; „🪄 Gans mit KI erzeugen“, „🎨 GANS-Bild gestalten“ |
| 2 Karten beschriften | Wort auf {{Spanisch}} eintragen oder vorschlagen lassen, Rückseite live ansehen, speichern |
| Ideen | Ideen sammeln, ergänzen und als Karte aufnehmen; unfertige Karten weiterbearbeiten |
| 3 Erzeugen | Ziel wählen, Feinschliff, los – rechts erzählt das Protokoll, was gerade passiert |
| 4 Prüfen & drucken | Prüfbogen und Checkliste, Drucken zu Hause oder in der Druckerei, digital lernen |
| Werkzeuge | Tools (Bildverbesserung, Übersetzung, KI-Bilder), Import / Export, GANS-Bild, Programmstart, Am Handy öffnen, Einstellungen der Übersetzung, Selbsttest, Projekt-ZIP, Ordner |
| Hilfe | Dieser Leitfaden in der eingestellten Sprache, die Spezifikation, Programmstand; dauert das Laden einmal zu lange, hilft „Abbrechen“ bzw. „Nochmal versuchen“ |
| Deinstallieren | Sichern und sauber entfernen |

Die Zahlen im Menü zeigen, was noch offen ist: bei Schritt 1 die Bilder, die noch nicht übernommen sind, bei Schritt 2 die Karten ohne Wort, bei „Ideen“ die Ideen, bei „Tabelle“ die automatisch übersetzten Wörter, die noch auf deinen Blick warten.

## Schritt 1: Bilder vorbereiten

Bilder in das Feld ziehen oder anklicken und auswählen – eins oder gleich viele. Kein passendes Foto? **„🪄 Gans mit KI erzeugen“** malt eins, **„🎨 GANS-Bild gestalten“** setzt den Wortwitz auf ein Foto (beides weiter unten). Für jedes Bild erscheint eine Zeile mit einer kleinen Vorschau der Vorderseite:

1. **Text auf dem Bild** eintragen, genau wie er auf dem Bild steht, etwa „Gans ausgeschlafen“. Daraus entsteht der Dateiname `gans-ausgeschlafen.jpg` (klein, ä → ae, ö → oe, ü → ue, ß → ss, Leerzeichen → Bindestrich). Heißt die Datei schon „gans-….jpg“, ist der Text bereits ausgefüllt.
2. **Wort auf {{Spanisch}}** (freiwillig): gleich hier eintragen oder mit 🌐 vorschlagen lassen. Bleibt das Feld leer, kommt das Wort in Schritt 2 dran.
3. Rechts steht das Ergebnis der Prüfung: **✓ Bereit**, **! Hinweise** oder **✕ Kurz prüfen** – im letzten Fall lässt sich das Bild übernehmen, sobald der Punkt erledigt ist.
4. **„Details ▾“** zeigt Original und Vorderseite groß, die vollständige Prüfliste, **Drehen** (↺ ↻) und den **Bildausschnitt**: „Ganzes Bild zeigen“ (freie Ränder werden weich fortgesetzt) oder „Fläche füllen“ (Ränder werden abgeschnitten). ★ markiert die Empfehlung für dieses Bild.
5. **„Übernehmen“** legt diese eine Karte an. Das Bild kommt in den Ordner `bilder/`, die Karte in die Kartenliste.

Über der Liste zeigt eine Leiste, wie viele Bilder bereit sind. **„🌐 Alle übersetzen“** schlägt für alle Bilder ohne Wort eines vor; **„Alle übernehmen (n)“** übernimmt alle bereiten Bilder auf einmal.

Die Prüfliste zeigt grüne Haken (alles bestens), graue Hinweise, orange Warnungen und rote Punkte. Solange etwas rot ist, wartet das Bild noch mit dem Übernehmen.

| Meldung | Bedeutung | Was tun |
| --- | --- | --- |
| HEIC/HEIF-Fotos kann das Programm nicht lesen | iPhone-Format | als JPG speichern: iPhone → Einstellungen → Kamera → Formate → „Maximale Kompatibilität“, oder am Rechner in der Fotos-App als JPG speichern. Am Handy über den Handy-Zugang hochgeladen, wandelt das iPhone in der Regel selbst in JPG um |
| Diese Datei lässt sich nicht als Bild lesen | Datei beschädigt oder kein Bild | Bild neu speichern oder ein anderes wählen |
| größer als 40 MB / mehr als 60 Megapixel | sehr große Datei | etwas verkleinern (z. B. auf 3000 px Breite) |
| zu klein für eine Karte (unter 100 px) | winziges Bild | eine größere Fassung suchen |
| … ppi im Druck | Quelle eher klein | geht trotzdem; mit einem größeren Bild wird’s richtig scharf |
| … gibt es schon im Bilderordner | Name vergeben | Text ändern oder „vorhandenes Bild ersetzen“ anhaken – die alte Fassung landet in `bilder/_entfernt/` |
| Genau dieses Bild liegt schon im Bilderordner | doppelt | „Verwerfen“, wenn es wirklich dasselbe ist |
| Das Bild ist hochkant, die Karte quer | Hochformat | in Ordnung; liegt es nur falsch herum, mit ↻ drehen |
| „Fläche füllen“ schneidet … % ab | starker Beschnitt | in der Vorschau prüfen, ob der Text ganz zu sehen ist – sonst „Ganzes Bild zeigen“ |
| Schwarze Ränder / Transparenz / CMYK / Kamera-Ausrichtung / GIF, BMP, TIFF | wird automatisch korrigiert oder umgewandelt | nichts – das erledigt das Programm |

Worauf es bei der Bildqualität ankommt: Die Bildfläche einer Karte hat bei 300 dpi 957 × 661 Pixel. Ab etwa 960 Pixel Breite ist das Bild im Druck scharf; kleinere Bilder werden mit KI vergrößert. Querformat um 3 : 2 füllt die Karte am besten. Der Wortwitz sollte gut lesbar groß im Bild stehen – gedruckt wird das Bild höchstens 8,1 cm breit.

## GANS-Bild gestalten

Mit **„🎨 GANS-Bild gestalten“** (Schritt 1, Ideen oder Werkzeuge) baust du aus einem Gänse-Foto ein Kartenbild mit dem Wortwitz – gänsehautverdächtig einfach:

1. Foto wählen oder in das Fenster ziehen.
2. **Ausschnitt** wählen (Quadrat, Karte quer, Hochformat); Bild ziehen zum Verschieben, Mausrad oder Regler zum Zoomen.
3. Text nach **GANS** eintippen – er erscheint in Großbuchstaben („GANS SEHR HEISS“). Den Text auf dem Bild ziehen, um ihn zu platzieren; Größe, Schrift und Farbe sind wählbar.
4. **„Als neue Karte (Schritt 1)“** übergibt das Bild an Schritt 1, **„Als Idee speichern“** legt eine Idee an, **„Herunterladen“** speichert die Datei. Der Dateiname folgt der Regel der Karten: `gans-sehr-heiss.jpg`.

Kommt das Bild aus **„Gans mit KI erzeugen“**, ist es schon eingesetzt – Ausschnitt „Karte quer“, Wort vorbelegt. Aus dem Karten-Editor heißt der Hauptknopf dann **„Für diese Karte übernehmen“**: Das beschriftete Bild wird das neue Bild dieser Karte.

## Gans mit KI erzeugen

Kein passendes Foto zur Hand? **„🪄 Gans mit KI erzeugen“** (Schritt 1) bzw. **„🪄 Mit KI …“** (Karten-Editor) malt dir ein realistisches Gänse-Foto – offline, direkt auf deinem Rechner. Einmalig installierst du dafür das Tool **„KI-Bilder“** (Werkzeuge → Tools) mit dem Modell Segmind Vega + VegaRT (Lizenz Apache-2.0, ca. 3,5 GB); danach braucht es kein Internet mehr.

1. **Wort auf der Karte** nach „GANS“ eintragen, z. B. „alt“. Es kommt nicht ins Bild – das Modell schreibt keinen sauberen Text –, sondern wird danach sauber daraufgesetzt.
2. **Beschreibung auf Englisch:** Wie und wo ist die Gans? Zum Beispiel „swimming on a lake at sunset“, „sleeping in a nest of straw“, „standing in fresh snow“. Gern Licht, Jahreszeit, Wetter oder Stimmung dazu („morning fog“, „golden hour“) – und lieber sagen, was zu sehen sein soll, als was nicht. Kein Englisch zur Hand? Auf Deutsch schreiben und **„🌐 Ins Englische“** klicken (nur mit eingeschalteter Übersetzung; gesendet wird nur diese Beschreibung). „… von 75 Token“ zeigt, ob alles beim Modell ankommt.
3. **„Keine Menschen“** (empfohlen, standardmäßig an) hält Menschen fern – über die Formulierung und einen sanften Negativ-Prompt; das kostet etwa 20 Sekunden mehr. Ganz ausschließen lässt es sich nicht: Taucht doch jemand auf, einfach neu würfeln.
4. **„🪄 Gans erzeugen“** – ein Bild dauert auf einem normalen Laptop etwa 1–2 Minuten. Nach jedem Rechenschritt siehst du eine Vorschau; du kannst das Fenster schließen und weiterarbeiten oder jederzeit **abbrechen**.
5. Gefällt dir die Gans? **„✍️ Wort aufs Bild setzen …“** öffnet sie in „GANS-Bild gestalten“ – von dort als neue Karte oder, aus dem Karten-Editor, für diese Karte. **„Ohne Wort als neue Karte“** bzw. **„Für diese Karte übernehmen“** übernimmt das Bild direkt; geprüft wird es wie jedes Foto. **„🎲 Neu würfeln“** malt eine neue Variante, **„Herunterladen“** speichert das Bild. Gleiche Beschreibung + gleicher Startwert ergibt dasselbe Bild.

| Das kann es gut | Da schwächelt es |
| --- | --- |
| eine Gans in natürlicher Umgebung, nah und scharf | Text und Buchstaben im Bild |
| Licht, Jahreszeit, Wetter und Landschaft | genaue Anzahlen und mehrere Tiere, die etwas miteinander tun |
| einfache Haltungen: steht, schwimmt, fliegt, schläft, frisst, schaut neugierig | Menschen-Tätigkeiten (Fahrrad fahren, lesen), Dinge in Schnabel oder Füßen |
| | bestimmte Rassen, dieselbe Gans auf mehreren Karten, ab und zu ein Bein oder Hals zu viel – dann neu würfeln |

**Standard-Prompt (für Neugierige):** „Standard-Prompt bearbeiten …“ zeigt die Vorlage, mit der das Programm das Modell anspricht: `{description}` steht für deine Beschreibung, `{word}` für das Wort der Karte (im Standard nicht benutzt). Eine eigene Fassung lässt sich speichern und jederzeit mit „Standard wiederherstellen“ zurückholen.

Gut zu wissen: Das Rechnen braucht etwa 3 GB Arbeitsspeicher (8 GB im Rechner empfohlen). Das Modell liegt im Datenordner, bleibt bei neuen Programmversionen erhalten und wird beim Deinstallieren mit entfernt. Über den Handy-Zugang geht alles genauso – gerechnet wird am Rechner.

**Tool installieren/entfernen:** Ist das Tool „KI-Bilder“ noch nicht da, bleiben die Knöpfe trotzdem sichtbar. „🪄 Gans erzeugen“ bzw. „Tool „KI-Bilder“ installieren …“ im KI-Fenster fragt nach – mit Hinweis, falls der Arbeitsspeicher knapp oder zu wenig Platz frei ist –, lädt das Modell über die Warteschlange und öffnet danach das KI-Fenster mit deinen Eingaben wieder. Entfernen: Werkzeuge → Tools → „KI-Bilder“ → „Deinstallieren …“ löscht das Modell und die Zwischenbilder in `ausgabe/.ki-bild`; deine eigene Prompt-Fassung bleibt.

## Schritt 2: Karten beschriften

Hier stehen alle Karten, denen noch das Wort auf {{Spanisch}} fehlt – und jede Karte, die du in „Meine Karten“ mit „Bearbeiten“ öffnest.

| Feld | Inhalt |
| --- | --- |
| Wort auf {{Spanisch}} | Kommt auf die Rückseite. `/` trennt das Hauptwort (groß) von Alternativen (klein darunter), z. B. `viejo / anciano`; `\|` setzt einen Zeilenumbruch im Hauptwort. 🌐 schlägt eine Übersetzung vor |
| Text auf dem Bild (Deutsch) | Zur Kontrolle im Prüfbogen, wird nicht gedruckt |
| Notiz | Nur für dich, z. B. die Wortart – wird nicht gedruckt |

Die Knöpfe á é í ó ú ñ ü ¿ ¡ fügen spanische Sonderzeichen ein – praktisch mit deutscher Tastatur. Die Rückseite aktualisiert sich beim Tippen. „Karte speichern“ (oder Enter) schreibt die Karte in `karten.csv`; „Später“ lässt sie geduldig warten. Bei mehreren Karten schlägt **„🌐 Alle übersetzen“** für alle leeren Felder ein Wort vor, und **„Alle speichern (n)“** speichert alle bereiten Karten auf einmal.

**Bild ändern:** Unter den Vorschaubildern holt **„Bild ändern …“** ein neues Bild für die Karte – oder zieh es einfach auf die Vorschau. Es wird geprüft wie in Schritt 1, mit Drehen und Ausschnitt; Wort, Text und Notiz bleiben. „Neues Bild übernehmen“ legt das bisherige Bild in `bilder/_entfernt/`, „Rückgängig“ holt es zurück. **„🪄 Mit KI …“** malt stattdessen ein neues Gänse-Bild für diese Karte (siehe „Gans mit KI erzeugen“).

| Meldung | Was tun |
| --- | --- |
| Fehlt nur noch das Wort auf {{Spanisch}} | eintragen – ohne Wort kommt die Karte nicht in den Druck |
| „ä“ gibt es im Spanischen nicht | Tippfehler? Spanisch kennt á é í ó ú ü ñ, aber kein ä, ö, ß |
| Das Hauptwort ist etwas lang für die Karte | kürzen oder mit `\|` an passender Stelle umbrechen |
| Die Alternativen sind etwas lang / viel Text | Alternativen kürzen oder weglassen |
| mehr als 2 Alternativen | auf die zwei wichtigsten beschränken |
| Spanische Fragen beginnen mit „¿“ | z. B. `¿cómo estás?` |
| Zeichen kann nicht gedruckt werden | Emoji und seltene Zeichen entfernen |
| Text darf nicht mit = + - @ beginnen | Schutz vor Excel-Formeln (gilt auch für die Notiz) – Zeichen am Anfang entfernen |
| noch gleich dem deutschen Text | Zeit fürs Übersetzen! |
| steht schon auf Karte … | nur ein Hinweis – doppelte Wörter sind erlaubt |

**Kartenliste von Hand bearbeiten (für Fortgeschrittene):** Jede Karte ist eine Zeile in `karten.csv` (Semikolon als Trennzeichen, UTF-8). Spalten: `bild` (Pflicht), `de`, `es` (Pflicht), `notiz`, `fit` (`contain` oder `cover`) und `uebersetzung` (`automatisch`, `geprüft` oder leer). Eine Zeile mit `#` am Anfang wird übersprungen. In Excel beim Speichern „CSV UTF-8“ wählen, sonst gehen ñ, á und ü verloren; danach die Oberfläche neu laden.

```csv
bild;de;es;notiz;uebersetzung
gans-alt.jpg;Gans alt;viejo;Adjektiv;geprüft
gans-arg-hunger.jpg;Gans arg Hunger;muchísima hambre / me muero de hambre;Wendung;automatisch
```

## Ideen sammeln

Gute Ideen kommen oft zwischendurch – hier haben sie ihren Platz. Eine Idee braucht nur **ein Bild, ein Wort auf Deutsch oder auf {{Spanisch}}**; der Rest kann später kommen.

- **„+ Neue Idee“** legt eine leere Idee an; Text eintippen genügt, gespeichert wird beim Verlassen des Feldes. Ein Bild kommt per „Bild wählen …“, durch Ziehen auf die Bildfläche oder mit „GANS-Bild gestalten …“ dazu.
- **Gibt es das Wort schon?** Beim Tippen prüft das Programm sofort, ob es das Wort schon als Karte oder Idee gibt – Groß- und Kleinschreibung, Umlaute und „Gans“ spielen dabei keine Rolle. So entsteht „Gans alt“ nicht aus Versehen zweimal.
- **🌐 neben dem deutschen Text** macht aus dem Wort auf {{Spanisch}} einen Vorschlag für den Text auf dem Bild (aus „viejo“ wird „Gans alt“). Ideal, wenn dir zuerst das Wort auf {{Spanisch}} einfällt.
- Sind Bild, Text auf dem Bild und Wort auf {{Spanisch}} da, wird **„Als Karte aufnehmen“** aktiv: Die Idee durchläuft dieselben Prüfungen wie in Schritt 1 und 2 und steht danach unter **Meine Karten**.
- **„Verwerfen“** lässt sich mit „Rückgängig“ zurückholen.
- Darunter stehen alle **unfertigen Karten** aus „Neue Karte“ mit „Weiter bearbeiten →“.

## Automatische Übersetzung

**So geht es:** 🌐 neben dem Feld „Wort auf {{Spanisch}}“ – in Schritt 1, in Schritt 2, in den Ideen und in der Tabelle – holt einen Vorschlag. Er erscheint im Feld; darunter stehen die Quelle und weitere Möglichkeiten zum Anklicken. Beim ersten Mal fragt das Programm, ob es die Übersetzung einschalten darf, und erklärt, was gesendet wird. Dort lässt sich auch „Neue Karten künftig gleich automatisch übersetzen“ anhaken.

**Prüfen bleibt wichtig:** Jedes übernommene Wort ist als „automatisch übersetzt – prüfen“ markiert – in „Meine Karten“, in der Tabelle und im Prüfbogen –, bis du es in der Tabelle als „geprüft“ abhakst. Wörterbücher treffen nicht immer das Wort, das man in Mexiko sagt; ein kurzer Blick von jemandem, der {{Spanisch}} spricht, ist Gold wert.

| Dienst | Wofür | Konto | Betreiber |
| --- | --- | --- | --- |
| Wiktionary | einzelne Wörter: mehrere Bedeutungen und Alternativen, von Menschen gepflegt | nein | Wikimedia Foundation |
| MyMemory | Wendungen aus mehreren Wörtern (maschinell) | nein; etwa 5000 Zeichen am Tag | Translated srl (Italien) |
| DeepL | sehr gute maschinelle Übersetzung | eigener kostenloser Schlüssel „DeepL API Free“ | DeepL SE (Deutschland) |

„Automatisch (empfohlen)“ fragt bei einem oder zwei Wörtern zuerst Wiktionary; bei längeren Wendungen DeepL (wenn ein Schlüssel hinterlegt ist) oder MyMemory. Alles Weitere unter **Werkzeuge → Automatische Übersetzung**.

**Sicherheit und Datenschutz**

- Ohne deine Zustimmung geht nichts ins Internet; widerrufen kannst du sie jederzeit unter Werkzeuge.
- Gesendet wird nur das Wort bzw. die Wendung ohne „Gans“ – zum Beispiel „aufgeregt“ –, höchstens 80 Zeichen. Keine Bilder, keine Dateinamen, keine Notizen, keine persönlichen Daten.
- Nur verschlüsselte Verbindungen (HTTPS mit Zertifikatsprüfung) zu den fest eingetragenen Adressen der drei Dienste; die Antworten werden gefiltert (kein HTML, keine Formeln, keine Steuerzeichen).
- Ein Vorschlag kommt erst in die Kartenliste, wenn du ihn übernimmst.
- Einstellungen und DeepL-Schlüssel liegen in deinem Benutzerordner, nur für dein Benutzerkonto lesbar – nicht im Projektordner und nie im Browser. Gemerkte Vorschläge (bis zu 90 Tage) lassen sich unter Werkzeuge löschen.

**Tool installieren/entfernen:** Die Zustimmung ist zugleich die Installation des Tools „Automatische Übersetzung“ – beim ersten 🌐 oder unter Werkzeuge → Tools. „Deinstallieren …“ nimmt die Zustimmung zurück und löscht Einstellungen, DeepL-Schlüssel und gemerkte Vorschläge. Die 🌐-Knöpfe bleiben und fragen beim nächsten Mal einfach wieder.

## Reiter „Tabelle“: Übersetzungen prüfen

Die Tabelle zeigt jede Karte in einer Zeile: Nummer, kleines Bild, **Vorderseite (Deutsch) → Rückseite ({{Spanisch}})**, Notiz und Prüfung.

- **Ändern:** in eine Zelle klicken und tippen; gespeichert wird beim Verlassen des Feldes (Enter = fertig, Esc = verwerfen). Es gelten dieselben Prüfungen wie in Schritt 2.
- **🌐** schlägt für diese Zeile ein Wort vor; **„🌐 Alle übersetzen“** füllt alle leeren Rückseiten.
- **„geprüft“** abhaken, sobald die Übersetzung stimmt. Ändert sich das Wort später, verschwindet das Häkchen wieder.
- **Filter, Suche und Sortieren** per Klick auf eine Spaltenüberschrift; „Bilder zeigen“ blendet die kleinen Bilder ein und aus.
- **„Tabelle drucken“** – praktisch, um sie jemandem zum Gegenlesen zu geben. Die Ansicht **„Kompakt“** passt dabei jede Karte in eine Zeile, ☐ lässt sich auf Papier abhaken.

## Reiter „Bildverbesserung“

Jede Vorderseite wird vor dem Druck aufbereitet: schwarze Ränder entfernen, mit **Real-ESRGAN x4plus** vergrößern (das Modell entfernt dabei auch JPEG-Blöcke und Rauschen), auf Druckgröße bringen, behutsam nachschärfen und Farben korrigieren. Beim ersten Mal dauert das etwa **1–4 Minuten pro Bild** (je nach Prozessor); danach kommt das Ergebnis gans schnell aus dem Zwischenspeicher.

In diesem Reiter lässt du das schon vorab erledigen, während du weiterarbeitest:

1. Oben stehen **KI-Vergrößerung** (Auto, Real-ESRGAN, Real-ESRGAN ×2, FSRCNN, Aus) und **Qualität** (Aus, Standard, Stark). Sie gelten auch für „Erzeugen“.
2. Karten mit dem Kästchen oben links im Bild auswählen – oder „Alle auswählen“ bzw. „Noch nicht verbesserte auswählen“.
3. **„✦ Ausgewählte verbessern (n)“** startet. Darunter steht, wie lange es etwa dauert. „Abbrechen“ behält alle schon fertigen Bilder.

Jedes Bild trägt ein Band: **verbessert** · **andere Einstellung** · **noch nicht verbessert** · **Bild fehlt**. Ein Klick zeigt **Vorher und Nachher** übereinander – den Unterschied verschiebst du mit dem Schieberegler. Beim Erzeugen werden noch fehlende Bilder ohnehin verbessert; der Reiter spart dir nur Wartezeit.

**Tool installieren/entfernen:** Real-ESRGAN ist das Tool „Bildverbesserung“. Fehlt es, zeigt der Reiter oben einen Kasten mit „Installieren“ (ca. 64 MB) und der schnelleren Variante ×2. Startest du trotzdem, fragt das Programm nach: „Installieren und weitermachen“ oder „Einfach vergrößern (ohne Tool)“ – dann rechnet das eingebaute FSRCNN. Dasselbe gilt beim Erzeugen, wenn Real-ESRGAN fest eingestellt ist. „Deinstallieren …“ (Werkzeuge → Tools) löscht die Modelle, ihre Kopie im Datenordner und die damit verbesserten Bilder im Zwischenspeicher; fertige Druck-PDFs bleiben.

## Schritt 3: Erzeugen

Erzeugen geht in drei kleinen Schritten:

1. **Was möchtest du erstellen?** Eine Kachel wählen:

| Ziel | Ergebnis |
| --- | --- |
| Alles zum Drucken | Druckerei-PDF, Heimdruck, Prüfbogen und Vorlagen in einem Rutsch – perfekt, wenn du dich noch nicht entschieden hast |
| Druckerei-PDF | Eine Seite je Kartenseite mit Beschnitt, dazu Einzelbilder (PNG) |
| Heimdruck | Mehrere Karten pro Blatt für deinen eigenen Drucker, A4 oder Letter |
| Prüfbogen | Übersicht zum Kontrollieren vor dem Druck |
| Digitale Lernkarten | Lernen ohne Papier: Anki, Lernseite, Bildschirm-PDF, Tabellen für andere Apps |
| Leere Vorlagen | Hilfslinien für eigene Gestaltung in einem anderen Programm |

2. **Feinschliff** (optional – die Voreinstellungen passen meistens): Es erscheinen nur die Einstellungen, die zu deinem Ziel gehören, jeweils mit Erklärung. Alles wird automatisch gespeichert; „Alle Einstellungen auf Standard“ setzt zurück.
3. **Los geht’s!** Mit „Nur diese Karten“ (z. B. `11-14`) entstehen nur neue Karten. Rechts zeigt das Protokoll, was passiert – am Ende steht „Fertig … – super gemacht!“.

**Gänse-Bild der Rückseite** (unter „Ausrichtung und Rückseite“): die gezeichnete Gans (Standard) oder ein eigenes Bild. Die gezeichnete Gans schwimmt unten rechts in einem kleinen Teich und schaut zum Wort; bei viel Text rückt sie etwas kleiner in die Ecke – das Wort steht immer frei auf ruhigem Blau. **„Gänse-Bild laden …“** oder ein Bild auf das Feld ziehen – am besten ein ruhiges, eher helles Bild im Querformat mit mindestens 960 × 660 Pixeln. Das Programm prüft es, verkleinert es auf höchstens 2400 Pixel und speichert es ohne Metadaten (zum Beispiel ohne Standortdaten). **„Gezeichnete Gans verwenden“** schaltet zurück, **„Vorheriges Bild“** holt das zuletzt ersetzte wieder.

| Einstellung | Wann |
| --- | --- |
| Papier A4 / Letter (Heimdruck) | Letter in den USA, Kanada, Mexiko und Teilen Lateinamerikas; gilt auch für den Prüfbogen |
| KI-Vergrößerung „FSRCNN (schnell)“ | schnell statt beste Qualität, z. B. zum Ausprobieren |
| KI-Vergrößerung „Real-ESRGAN ×2“ | fast gleiche Qualität, etwa 4× schneller – vorher unter Werkzeuge → Tools → Bildverbesserung „+ Schneller ×2“ laden |
| Qualität „Stark“ | kräftigere Farben und Schärfe; „Aus“ schaltet die Verbesserung ab |
| Druckerei-Datei hochkant | die Vorlage der Druckerei verlangt Hochformat |
| Rückseite um 180° drehen | im Probedruck steht die Rückseite kopfüber |
| Endformat | anderes Kartenformat in mm, z. B. 74 × 52 |
| Weißer Rand 0 | randlose Karten |
| Versatz waagerecht/senkrecht (Heimdruck) | Vorder- und Rückseite liegen beim Probedruck nicht genau übereinander |
| Alle Bilder neu berechnen | z. B. nach einem Update |

Für Profis: „Für Profis: Befehlszeile“ zeigt die passende Kommandozeile; ohne Oberfläche `py gans_lernkarten.py` (Mac/Linux: `python3`), alle Schalter mit `--help`.

## Tools

Manche Extras brauchen viel Platz oder schicken etwas ins Internet. Darum sind sie **Tools**: nicht vorinstalliert, auf Wunsch geladen – und jederzeit wieder weg. Reiter und Knöpfe bleiben dabei immer sichtbar.

| Tool | Wofür | Größe |
| --- | --- | --- |
| ✨ Bildverbesserung (Real-ESRGAN) | die schönste KI-Vergrößerung für den Druck; ohne Tool verbessert das eingebaute FSRCNN etwas schlichter | ca. 64 MB Download (dazu optional „Schneller ×2“) |
| 🌍 Automatische Übersetzung | Vorschläge für die Rückseite (Wiktionary, MyMemory, DeepL) – Installieren heißt hier: zustimmen | kein Download |
| 🎨 KI-Bilder | realistische Gänse-Bilder, offline auf deinem Rechner | ca. 3,5 GB |
| 🗣 Sprachen (Rückseite) | weitere Sprachen für die Rückseite – jede einzeln (siehe „Weitere Sprachen“) | 0–17 MB je Sprache |
| 🎓 Karten lernen | deine Karten lernen wie mit Anki (Planer FSRS) – Installieren heißt hier: einschalten; Deinstallieren löscht den Lernstand (vorher exportieren, wenn du ihn behalten willst) | kein Download |

- **Beim ersten Öffnen** fragt das Programm einmal, welche Tools gleich geladen werden sollen – nichts ist vorausgewählt, „Später“ ist völlig in Ordnung.
- **Werkzeuge → Tools** zeigt jedes Tool mit Zustand (nicht installiert · wartet · lädt … % · installiert) und belegtem Platz. „Installieren“ lädt es über die **Warteschlange** – du arbeitest nebenbei weiter.
- **Fehlt ein Tool**, wenn du es brauchst, fragt das Programm nach (Nutzen, Größe, Speicherort, Dauer). „Installieren und weitermachen“ lädt es und macht danach von selbst mit deiner Aktion weiter.
- **„Deinstallieren …“** löscht nach einer Rückfrage nur die Dateien des Tools und gibt den Platz frei. Deine Karten, Bilder und Ideen bleiben, und das Tool lässt sich jederzeit wieder installieren.
- Modelle bzw. eine Zustimmung aus einer früheren Version zählen gleich als installiert. Die Bildverbesserung liegt zusätzlich als Kopie im Datenordner – eine neue Programmversion übernimmt sie ohne Download.

## Weitere Sprachen

Die Rückseite muss nicht Spanisch sein. Mit dem Tool **🗣 Sprachen (Rückseite)** stehen 14 weitere Sprachen bereit: Englisch, Plattdeutsch, Französisch, Italienisch, Türkisch, Schwedisch, Norwegisch, Polnisch, Russisch, Japanisch, Chinesisch, Koreanisch, Hindi und Hocharabisch. Spanisch ist immer dabei.

- **Werkzeuge → Tools → Sprachen** listet alle Sprachen mit Größe. Sprachen mit lateinischer Schrift sind sofort da („ohne Download“), die übrigen laden ihre Schrift über die Warteschlange (1–17 MB).
- **„Als Rückseite“** (oder die Auswahl **Rückseite:** oben in Meine Karten, Schritt 2 und Tabelle – sichtbar, sobald außer Spanisch eine Sprache installiert ist) macht eine Sprache zur **Kartensprache**. Danach heißt es überall „Wort auf Japanisch“ statt „Wort auf Spanisch“, 🌐 übersetzt in die neue Sprache, und „offen“ zählt die Karten ohne Wort in dieser Sprache. Auch dieser Leitfaden spricht dann von der gewählten Sprache.
- **Sprach-Chips** („ES“, „JA“, „AR“ …) zeigen an jeder Karte, in welchen Sprachen es schon eine Rückseite gibt – ausgefüllt = Wort vorhanden, gestrichelt = noch leer, dunkel = aktuelle Kartensprache. In Meine Karten zeigt ein Klick auf einen Chip die Rückseite in dieser Sprache.
- **Mehrere Rückseiten:** Eine Karte kann für jede Sprache ein eigenes Wort haben. In Schritt 2 steht das Feld der Kartensprache groß oben, darunter klappt **„Weitere Sprachen“** je ein Feld pro installierter Sprache auf – jedes mit eigenem 🌐. Die Tabelle zeigt eine Spalte je Sprache und filtert mit „fehlt auf …“.
- Arabisch schreibt sich von rechts nach links, Japanisch, Chinesisch und Koreanisch tippst du mit der Eingabemethode deines Systems; die Sonderzeichen-Leiste passt sich der Sprache an.
- **Entfernen** einer Sprache löscht nur ihr Sprachpaket. Deine Wörter bleiben in `karten.csv` (eine Spalte je Sprache) und sind nach einer neuen Installation sofort wieder da. War es die Kartensprache, geht es mit Spanisch weiter.

### Drucken und Exportieren in anderen Sprachen

- In **Schritt 3: Erzeugen** wählst du unter **Sprache der Rückseite**, in welcher Sprache gedruckt wird: Standard ist die aktuelle Kartensprache, jede installierte Sprache geht auch – und **„Alle installierten“** reiht einen Auftrag je Sprache in die Warteschlange ein.
- Jede Sprache druckt mit ihrer eigenen Schrift aus dem Sprachpaket (Russisch Noto Sans, Japanisch/Koreanisch/Chinesisch IBM Plex Sans, Arabisch IBM Plex Sans Arabic, lateinische Sprachen und Hindi Poppins). Hindi und Arabisch werden richtig geformt (verbundene Buchstaben, Silben), Arabisch läuft von rechts nach links – Zahlen und lateinische Wörter darin bleiben lesbar. Japanisch und Chinesisch brechen zwischen Zeichen um, nie mit einem Satzzeichen am Zeilenanfang. Die Schriftgröße richtet sich nach den echten Zeichenbreiten.
- Dateinamen bekommen das Sprachkürzel: `…_Druckerei_88x63_ja.pdf`, `…_Pruefbogen_ar.pdf`, `einzelbilder_ru/`, `digital/…_Anki_ja.apkg`. **Spanisch bleibt wie immer** (ohne Kürzel) – so liegen alle Sprachen friedlich nebeneinander.
- **Sprachkürzel drucken** (Bereich „Ausrichtung und Rückseite“): ein kleines „JA“, „AR“ … oben links auf der Rückseite hilft beim Sortieren gemischter Stapel. „Auto“ druckt es nur, wenn die Rückseite nicht Spanisch ist.
- Der **Prüfbogen** nennt die Sprache („JA: …“), die **Rückseiten-Vorschau** zeigt die Kartensprache schon mit ihrer Schrift.
- **Digital:** Das Anki-Paket bekommt je Sprache einen eigenen Stapel („Me Goos-ta Deutsch – Japanisch“) und Notiztyp mit dem Feld der Sprache, die Lernseite setzt Sprache und Schreibrichtung, und `tabellen/karten_alle_sprachen.csv` enthält alle Sprachen nebeneinander (eine Spalte je Sprachcode).

## Warteschlange

Damit dein Rechner nicht ins Schwitzen kommt, arbeitet im Hintergrund immer nur **ein** Auftrag zur Zeit – Erzeugen, Bildverbesserung, Selbsttest, ein Tool laden oder eine KI-Gans. Startest du etwas, während schon etwas läuft, stellt es sich einfach hinten an („In der Warteschlange – Platz 2“) und legt von allein los, sobald es dran ist. Die Knöpfe bleiben dabei frei.

- **⏳ n** oben rechts zeigt, wie viele Aufträge laufen oder warten. Ein Klick öffnet das Fenster **Warteschlange**.
- **Läuft gerade:** Titel, Fortschritt, Dauer und „Abbrechen“ – danach startet der nächste Auftrag automatisch.
- **Wartet:** ▲ ▼ verschieben, **„Als Nächstes“** zieht einen Auftrag ganz nach vorn, **✕** nimmt ihn heraus; **„Alle wartenden entfernen“** fragt vorher nach.
- **Zuletzt erledigt:** die letzten zehn Aufträge mit ✓ oder ✕ und Dauer, dazu „Ergebnis ansehen“ bzw. „Protokoll“.
- Denselben Auftrag zweimal einzureihen geht nicht – er behält seinen Platz. Kann ein Auftrag beim Start nicht loslegen (z. B. weil das KI-Modell fehlt), steht er mit ✕ unter „Zuletzt erledigt“ und die Schlange läuft weiter.
- Die Warteschlange lebt nur, solange das Programm offen ist. **Beenden** fragt nach, wenn noch etwas läuft oder wartet.

## Farben anpassen

Die Oberfläche darf so bunt sein, wie du magst: **Werkzeuge → „🎨 Farben & Darstellung“**. Die Seite zeigt jede Wahl sofort als Vorschau – gemerkt wird sie erst mit **„Speichern“** (Fenster zu ohne Speichern = alles wieder wie zuvor).

- **Gänsehimmel** (Standard): die Farben, die du von Anfang an kennst – unverändert.
- **Gänsenacht** (dunkel), **Wiese** (frisches Grün) und **Hoher Kontrast** (schwarz auf weiß, kräftige Linien).
- **Wie das System:** hell oder dunkel, je nachdem, was dein Gerät gerade eingestellt hat.
- **Eigene Farben:** Farbwähler für Hintergrund, Flächen (Karten, Fenster), Text, Akzent & Knöpfe, Linien, Erfolg (grün) und Fehler (rot). Was du nicht änderst, bleibt wie im Standard.
- Die **Kontrastprüfung** zeigt unten, wie gut Text und Hintergrund zusammenpassen; ab 4,5 : 1 ist es gut lesbar, darunter steht „Achtung: schwer lesbar“.
- **Auf Standard zurücksetzen** bringt alles zurück zum Gänsehimmel. Die Wahl gilt auch am Handy (Handy-Zugang) und betrifft nur die Oberfläche – die gedruckten Karten bleiben, wie sie sind.

## Schritt 4: Prüfen & drucken

**Prüfen – ein kurzer Blick lohnt sich, dann wird jede Karte ein Treffer.** Der Prüfbogen zeigt je Karte Vorder- und Rückseite nebeneinander, die Texte und die Bildschärfe. Die Checkliste daneben sagt dir, was noch offen ist:

1. **Übersetzung:** Stimmt das Wort, und sagt man es so in Mexiko? Am bequemsten im Reiter „Tabelle“. Automatisch übersetzte Wörter tragen einen Vermerk, bis sie als geprüft abgehakt sind.
2. **Bildschärfe:** „… ppi im Druck“ – ab 180 ppi gut, 120–179 in Ordnung, darunter eher knapp (dann hilft ein größeres Bild).
3. **Probedruck:** eine Seite auf normalem Papier mit 100 % drucken – passt alles, kann’s losgehen.

**Zu Hause drucken** (`…_Heimdruck_…pdf`, 8 Karten je Bogen):

- Mit 100 % bzw. „Tatsächliche Größe“ drucken – nicht „An Seite anpassen“.
- Beidseitig, Wenden an der langen Kante. Ohne Duplex: erst die Vorderseiten, Stapel wenden, dann die Rückseiten.
- Fester Karton (etwa 200–300 g/m²) macht die Karten schön griffig.
- Liegen Vorder- und Rückseite nicht genau übereinander: in Erzeugen unter „Heimdruck“ den Versatz in mm einstellen. Rückseite kopfüber → „Rückseite um 180° drehen“.
- Entlang der Schnittmarken schneiden – mit Lineal und Cutter oder einer Schneidemaschine. Wer mag, rundet die Ecken ab.

**In einer Druckerei drucken** (`…_Druckerei_…pdf` oder `einzelbilder/`): Druckereien für eigene Spiel- oder Lernkarten gibt es in vielen Ländern online – egal, wo du wohnst. So findest du eine passende:

- **Suchbegriffe:** „Spielkarten individuell drucken“, „eigenes Kartenspiel drucken“, „Lernkarten drucken lassen“, auf Englisch „custom playing cards“, auf Spanisch „imprimir cartas personalizadas“.
- **Wichtig:** Jede Karte braucht ihre **eigene Vorder- und Rückseite** – nicht nur eine gemeinsame Rückseite für alle.
- **Format:** Pokerkarte 63 × 88 mm passt direkt; andere Größen stellst du in Erzeugen unter „Endformat“ ein.
- **Beschnitt:** meist 3 mm rundum – ist im Druckerei-PDF schon drin (Datei 94 × 69 mm, Endformat 88 × 63 mm).
- **Ausrichtung:** Verlangt die Vorlage Hochformat? Dann „Druckerei-Datei hochkant“ einschalten.
- **Hochladen:** als PDF oder Einzelbilder. Mindestmenge, Kartenstärke, Veredelung und Versandkosten vergleichen.
- **Vorschau prüfen:** vor allem die Richtung der Rückseite – und zuerst ein Probeexemplar bestellen, dann den ganzen Stapel.

## Karten lernen

Mit dem Tool **„🎓 Karten lernen“** übst du deine Karten direkt im Programm – so, wie es die Lernforschung empfiehlt. Beim ersten Klick auf **„Lernen“** im Menü schaltest du es ein (nichts wird heruntergeladen). Die Zahl im Menü zeigt, wie viele Karten heute dran sind.

**So funktioniert es (in einfachen Worten):** Du siehst das Bild und versuchst, dich an das Wort auf {{Spanisch}} zu erinnern – erst dann drehst du die Karte um („Antwort zeigen“). Danach sagst du ehrlich, wie gut es ging: **Nochmal** (vergessen), **Schwer**, **Gut** oder **Einfach**. Der Planer **FSRS** (derselbe wie in Anki) rechnet daraus aus, wann du die Karte gerade noch weißt, und zeigt sie genau dann wieder: anfangs nach Minuten, später nach Tagen, Wochen und Monaten. Unter jedem Knopf steht, wann die Karte wiederkommt. Neue Karten lernst du zuerst in kurzen Schritten (1 und 10 Minuten).

| Bereich | Was du dort findest |
| --- | --- |
| Heute | wie viele Wiederholungen und neue Karten anstehen, „Los geht’s“ |
| Stapel | „Alle aktiven Karten“ und eigene Stapel – nach Sprache, Notiz, Suchtext, nur neue/fällige/Problemkarten oder per Häkchen; ✎ ändern, 🗑 löschen |
| Statistik | Gänsemarsch (Tage in Folge), heute gelernt, fällig in den nächsten 7 Tagen, Lernstand der Karten (neu · lernt · jung · sicher), Behaltensquote |
| Einstellungen | neue Karten und Wiederholungen pro Tag, gewünschte Behaltensquote (80–95 %, Standard 90 %), Richtung (Bild → Wort, Wort → Bild, beide), Lernsprache, Beginn des Lerntags (Standard 4 Uhr) |
| Lernstand sichern | exportieren (JSON-Datei), importieren (je Karte gilt der neuere Stand), alles zurücksetzen |

**Beim Lernen:** Leertaste = Antwort zeigen, Tasten **1–4** = bewerten, **Strg+Z** = rückgängig, **Esc** = beenden. Am Handy tippst du die Karte an; die Bewertungsknöpfe liegen unten im Daumenbereich, Wischen nach rechts heißt „Gut“, nach links „Nochmal“ (↶ nimmt es zurück). Du kannst jederzeit aufhören – jede Bewertung ist sofort gespeichert, auch wenn du das Programm schließt. Hat dein System eine Stimme für die Sprache, liest 🔊 das Wort vor.

**In „Meine Karten“** zeigt jede Karte ihren Lernstand (neu, lernt, jung, sicher; im Hover: wie oft gelernt und wann die nächste Wiederholung ist). Darüber filterst du nach fällig, neu, sicher oder Problemkarten. Mit **„☑ Auswählen“** kreuzt du Karten an und lernst sie **„Jetzt“** oder legst sie in einen Stapel.

**Karte geändert?** Änderst du Deutsch-Text, Wort oder Bild einer Karte, die du schon lernst, beginnt sie beim Lernen von vorn – der Editor sagt das vorher, danach kommt eine kurze Meldung. Eine geänderte Notiz behält den Lernstand.

**Tipps:** Lieber jeden Tag ein bisschen als selten viel. Sei beim Bewerten ehrlich – „Nochmal“ ist kein Fehler, sondern genau das, was den Planer schlau macht. Karten, die du immer wieder vergisst, werden zu **Problemkarten**: ein deutlicheres Bild oder eine Notiz (z. B. eine Eselsbrücke) hilft oft mehr als noch eine Wiederholung.

## Digital lernen

Lust, auch unterwegs zu lernen? Wähle in Erzeugen **„Digitale Lernkarten“** – das Ergebnis liegt in `ausgabe/digital/`:

| Format | So lernst du damit |
| --- | --- |
| Anki-Paket (`.apkg`) | in Anki am Rechner öffnen (Windows, Mac, Linux) – oder per Mail, Cloud oder Kabel aufs Handy und in AnkiDroid (Android) bzw. AnkiMobile (iPhone/iPad) importieren |
| Lernseite (`.html`) | eine einzige Datei, läuft offline im Browser am Rechner. Umdrehen, „Gewusst“ oder „Nochmal“; dein Lernstand bleibt in diesem Browser gespeichert. Am Handy klappt sie nur eingeschränkt (am iPhone startet sie aus der Dateien-App meist nicht) – dort lieber das Anki-Paket oder das Bildschirm-PDF |
| Bildschirm-PDF | in jeder PDF-App durchblättern: Vorderseite, Rückseite, nächste Karte |
| Tabellen (CSV) | für Quizlet, Brainscape, Mochi & Co. – im Feinschliff „Tabellen für andere Apps“ wählen |

In „Prüfen & drucken“ lädst du jede Datei mit „Herunterladen“ herunter, um sie z. B. aufs Handy zu schicken. Noch bequemer am Handy: die Handy-App (siehe „Als App aufs Handy“) – mit Karten lernen, auch offline.

## Karten und Ideen importieren und exportieren

Unter **Meine Karten → „⇅ Import / Export“** (auch in Ideen und Werkzeuge):

- **Exportieren:** Karten, Ideen oder **alles als Komplettsicherung** als ZIP-Datei herunterladen – zum Sichern, Weitergeben oder für den Umzug auf einen anderen Rechner. Bei Karten wahlweise alle oder nur die, die gedruckt werden.
- **Importieren:** eine solche ZIP-Datei (oder eine `karten.csv`) wählen oder hineinziehen. Zuerst siehst du eine **Vorschau**: neu · schon da, aber anders · gleich · fehlerhaft. Gibt es etwas schon, entscheidest du je Zeile: **Behalten** (dein Stand bleibt) oder **Ersetzen** (der Import gewinnt). Nichts geht verloren – ersetzte Bilder kommen nach `bilder/_entfernt/`. Auch ein Wort, das es unter anderem Dateinamen schon gibt, wird erkannt.
- Bilder und Texte werden dabei geprüft wie in Schritt 1 und 2; Excel-Formeln, kaputte oder HEIC-Bilder bleiben draußen.

## Am Handy öffnen (WLAN)

Fotos direkt vom Handy hochladen? Unter **Werkzeuge → „Am Handy öffnen (WLAN)“** schaltest du den Handy-Zugang ein. Er ist standardmäßig aus und funktioniert nur im eigenen WLAN:

1. „Handy-Zugang einschalten“ – es erscheinen ein QR-Code, die Adresse und eine 6-stellige PIN.
2. QR-Code mit der Handy-Kamera scannen (oder die Adresse im Handy-Browser eintippen) und die PIN eingeben.
3. Fertig – jetzt kannst du am Handy Bilder hinzufügen, KI-Gänse erzeugen, Karten beschriften und Ideen sammeln.

Die Adresse bleibt beim nächsten Einschalten gleich – ein Lesezeichen am Handy passt also weiter. Beim allerersten Mal fragt Windows bzw. macOS, ob Python Verbindungen annehmen darf: bitte erlauben (privates Netzwerk).

Zu deiner Sicherheit: Die Verbindung ist im Heimnetz unverschlüsselt, deshalb den Zugang nur zu Hause nutzen. Er schaltet sich nach 2 Stunden, nach 5 falschen PINs und beim Beenden von selbst aus. Beenden, Deinstallieren und das Öffnen von Ordnern gehen nur direkt am Rechner.

## Als App aufs Handy

Me Goos-ta Deutsch gibt es auch als **Handy-App** (Web-App) für Android, Google Pixel und iPhone/iPad – dieselbe Oberfläche, dasselbe Programm, nur ganz ohne Rechner: Python läuft direkt im Browser des Handys. Nach dem ersten Laden (gut 20 MB) startet die App auch ohne Internet.

- **Adresse und Anleitungen:** Am Rechner zeigt **Werkzeuge → „Am Handy öffnen (WLAN)“** unten den QR-Code der App (dafür braucht es keinen WLAN-Zugang), ebenso „📲 Als App aufs Handy“ unter **Prüfen & drucken → Digital lernen**. Neben den Startdateien liegen drei Anleitungen mit Skizzen: `Me Goos-ta Deutsch - Android.html`, `… - iPhone.html` und `… - Google Pixel.html` – am Rechner öffnen und den QR-Code scannen oder die Datei per Mail oder Cloud aufs Handy schicken. Sie brauchen kein JavaScript und öffnen sich daher auch in Datei-Apps.
- **Installieren:** die Adresse der App im Browser öffnen und „📲 App installieren“ tippen – mit Chrome (Android, Google Pixel) entsteht eine echte App im App-Menü. Am iPhone/iPad (ab iOS 16.4): Safari → Teilen → „Zum Home-Bildschirm“ → „Hinzufügen“. Die Schritte mit Skizzen stehen in der App unter **Mehr → App installieren**.
- **Unten** führt die App-Leiste durch alles: **Karten · Neu · Lernen · Drucken · Mehr**. „Mehr“ öffnet Tabelle, Bildverbesserung, Ideen, Werkzeuge, Hilfe und die App-Sachen. Die Zurück-Geste schließt zuerst ein offenes Fenster und geht dann einen Bereich zurück. Dieselbe Leiste erscheint auch über den Handy-Zugang auf Touch-Geräten bis 860 px Breite.
- **Deine Daten bleiben am Gerät** (im Speicher des Browsers – kein Konto, kein Upload). Unter **Mehr → Sicherung & Speicher** packt „Alles sichern“ Karten, Bilder, Ideen, Lernstand und Einstellungen in eine Datei; „Sicherung einspielen“ holt sie zurück und ersetzt dabei alles auf diesem Gerät. Am iPhone bleiben die Daten nur in der installierten App dauerhaft – Safari löscht Website-Daten sonst nach 7 Tagen ohne Besuch.
- **Karten vom Rechner übernehmen:** am Rechner unter Meine Karten → ⇅ Import / Export „Alles – Komplettsicherung“ exportieren, die Datei aufs Handy schicken (Mail, Cloud, Kabel) und in der App importieren – der Lernstand kommt mit.
- **Ergebnisse** (Druck-PDFs, Anki-Paket, Sicherung) öffnen sich zum **Teilen** (Drucken, Mail, „Dateien“) oder **Speichern**. Lange Aufträge zeigen ihren Fortschritt, „Abbrechen“ stoppt sie; alles läuft nacheinander über die Warteschlange.
- **Was am Handy anders ist:** KI-Bilder gibt es nur am Rechner (3,5-GB-Modell) – der Knopf bleibt und sagt Bescheid. Real-ESRGAN rechnet am Handy deutlich langsamer; das eingebaute FSRCNN reicht für den Druck. Die automatische Übersetzung nutzt Wiktionary und MyMemory (DeepL nur am Rechner). Hindi und Arabisch drucken ohne Silbenformen (dafür braucht es uharfbuzz am Rechner). Startprogramm, Ordner, Handy-Zugang und Deinstallieren gibt es in der App nicht.
- **Neue Version:** Die App lädt Updates von selbst im Hintergrund und meldet „Neue Gänse-Version da – neu laden?“ (auch unter Mehr).

## Programmstart: Browser oder eigenes Fenster

Ob sich Me Goos-ta Deutsch **im Standard-Browser**, **in einem bestimmten Browser** oder **in einem eigenen Fenster** ohne Adressleiste öffnet (dafür braucht es Edge, Chrome, Brave oder Chromium), legst du im Willkommens-Assistenten fest – ändern kannst du es jederzeit unter **Werkzeuge → Programmstart**. Es gilt ab dem nächsten Start.

## Deinstallieren

Der letzte Reiter **„Deinstallieren“** führt dich in zwei Schritten:

1. **Karten und Ideen sichern:** „Komplettsicherung herunterladen“ speichert alles als eine ZIP-Datei. Nach einer neuen Installation – auch auf einem anderen Gerät – liest „Import / Export → Importieren“ alles wieder ein.
2. **Programm entfernen:** Nach einer Rückfrage („Bist du sicher?“) und einem Häkchen entfernt das Programm Desktop-Symbol bzw. App oder Menüeintrag, das eigene Python mit Einstellungen und gemerkten Übersetzungen **und den Programmordner mit allen Karten, Bildern und Ideen**. Das lässt sich nicht rückgängig machen – deshalb gibt es Schritt 1. Deine Sicherung, Dateien außerhalb des Programmordners und andere Programme bleiben unberührt.

Neu installieren geht jederzeit: Download entpacken, Startdatei doppelklicken, Sicherung importieren – fertig.

## Bildverbesserung: welches KI-Modell?

Getestet wurden fünf frei verfügbare Modelle gegen das einfachere FSRCNN, an kleinen, stark komprimierten Fotos mit Text: Real-ESRGAN x4plus, Real-ESRGAN x2plus, Real-ESRGAN anime 6B, Real-ESRGAN general v3 und SwinIR-L. **Real-ESRGAN x4plus** liefert das beste Ergebnis: Es entfernt JPEG-Blöcke, macht Federn und Augen glaubhaft scharf und lässt die Schrift sauber. Diffusionsmodelle scheiden aus: Sie erfinden Details – auch Buchstaben. Real-ESRGAN steht unter der BSD-3-Lizenz und wird vom Programm ohne Zusatzsoftware in reinem NumPy gerechnet.

## Sicherheit

- Die Oberfläche ist nur auf deinem Rechner erreichbar und nur über das Startprogramm zu öffnen (geheimer Startschlüssel) – außer du schaltest bewusst den Handy-Zugang ein, dann zusätzlich mit PIN im eigenen WLAN.
- Andere Webseiten können sie nicht fernsteuern; Dateien werden nur in den Projektordnern gelesen und geschrieben, „Öffnen“ startet nie Programme oder Skripte.
- Die automatische Übersetzung sendet nur nach deiner Zustimmung und nur das zu übersetzende Wort (beim KI-Bild auf Klick die kurze Beschreibung), verschlüsselt an drei fest eingetragene Dienste.
- Das KI-Bildmodell rechnet vollständig auf deinem Rechner; Beschreibungen und Bilder verlassen ihn nicht.
- Texte, die in Excel als Formel gelten würden (Anfang = + - @), werden abgelehnt – auch beim Import. Bilder werden geprüft und ohne Metadaten gespeichert.
- KI-Modelle und Python werden nur von offiziellen Quellen geladen und per Prüfsumme kontrolliert; Modell-Dateien können keinen Code ausführen.
- Nichts davon braucht Administratorrechte, und die Intelligente App-Steuerung von Windows bleibt eingeschaltet.

## Fehlerbehebung

Keine Panik – für fast alles gibt es eine schnelle Lösung:

| Problem | Lösung |
| --- | --- |
| „Python was not found …“ oder Fragen nach einem Programm für `.py`-Dateien | Kein Python nötig: die Startdatei bringt ihr eigenes mit – einfach sie doppelklicken |
| „Intelligente App-Steuerung hat … blockiert“ | ZIP oder Startdatei freigeben: Eigenschaften → „Zulassen“ → OK |
| „Der Computer wurde durch Windows geschützt“ | „Weitere Informationen“ → „Trotzdem ausführen“ |
| Startfenster meldet „Keine Verbindung zum Internet“ | Nur der erste Start braucht Internet: Verbindung prüfen, erneut starten. Schon Geladenes wird weiterverwendet |
| Browser öffnet sich nicht | die Adresse aus dem Startfenster (http://127.0.0.1:…) in den Browser kopieren |
| Seite sagt „Bitte über das Desktop-Symbol … öffnen“ | über das Symbol starten – ein Lesezeichen funktioniert nach einem Neustart nicht, der Startschlüssel ist jedes Mal neu |
| „Die Verbindung ist kurz abgetaucht“ | die Oberfläche wurde beendet – über das Symbol neu starten |
| Symbol tut nichts oder meldet „Programmordner verschoben“ | einmal die Startdatei im (neuen) Programmordner doppelklicken – sie prüft und repariert alles |
| Nach dem Update fehlen meine Karten | Sicherung importieren – oder `karten.csv` und den Ordner `bilder` aus dem alten in den neuen Ordner `Programm` kopieren |
| 🌐 meldet „… noch nicht eingeschaltet“ | im Fenster „Einschalten und übersetzen“ wählen oder unter Werkzeuge erlauben |
| „Hoppla, da hat sich die Gans kurz verheddert (…)“ | ein unerwarteter Fehler – einfach noch einmal versuchen; kommt er wieder, das Programm über das Symbol neu starten (in Klammern steht der technische Grund, praktisch für Rückfragen) |
| Übersetzungsdienst antwortet nicht / Tageskontingent aufgebraucht | später noch einmal versuchen, einen eigenen DeepL-Schlüssel hinterlegen – oder das Wort selbst eintragen |
| Handy findet die Adresse nicht | Rechner und Handy müssen im selben WLAN sein; Gäste-WLANs trennen Geräte oft voneinander. Hat die Firewall von Windows bzw. macOS gefragt, ob Python Verbindungen annehmen darf? Für private Netzwerke erlauben |
| „🪄 Gans mit KI erzeugen“ meldet, das Modell fehle | Werkzeuge → Tools → KI-Bilder „Installieren“ (einmalig ca. 3,5 GB); ein abgebrochener Download setzt beim nächsten Mal fort |
| KI-Gans sieht eher wie eine Ente aus, hat ein Bein zu viel oder es sind doch Menschen im Bild | 🎲 neu würfeln; die Beschreibung konkreter machen; „Keine Menschen“ anlassen und eine ruhige Szene beschreiben („early morning“, „empty“) statt einer Menschenmenge |
| KI-Bild dauert sehr lange | 1–2 Minuten sind normal, ältere Rechner brauchen 3–5; andere große Programme schließen. „Keine Menschen“ aus spart etwa 20 Sekunden |
| Gänse-Bild wird abgelehnt | JPG, PNG oder WEBP verwenden (kein HEIC), mindestens 300 Pixel, höchstens 40 MB |
| Erzeugen dauert lange | Real-ESRGAN braucht beim ersten Mal 1–4 Minuten pro Bild; danach geht es schnell. Bilder vorab im Reiter „Bildverbesserung“ verbessern oder zum Ausprobieren „FSRCNN (schnell)“ wählen |
| Rückseiten-Vorschau zeigt nur das Wort | einmal die Startdatei doppelklicken (repariert); die PDFs sind in jedem Fall richtig |
| ñ, á oder ü erscheinen als Zeichensalat | `karten.csv` als „CSV UTF-8“ speichern |
| Rückseite steht kopfüber / Druck versetzt | „Rückseite um 180° drehen“ / „Versatz“ in Erzeugen |
| Bild ungünstig beschnitten | in Schritt 1 den Ausschnitt wechseln |

Im Zweifel: **Werkzeuge → Selbsttest**. Er prüft alles in einer Kopie mit den Beispielkarten und lässt deine Dateien unberührt.

## Spickzettel

```
 Start          Desktop-Symbol „Me Goos-ta Deutsch“
   │            (beim ersten Mal: Startdatei im Ordner)
   │
 1 Bilder       Bilder hineinziehen (gern viele) ·  <───────┐
   │            oder KI-Gans malen lassen (1–2 min) ·       │
   │            Text auf dem Bild · Wort · übernehmen       │
   │                                                        │
 2 Beschriften  fehlende Wörter („Alle übersetzen“) ·       │ nein:
   │            Rückseite ansehen · „Alle speichern“        │ in Schritt 1,
   │                                                        │ Schritt 2 oder
   Tabelle      Deutsch ↔ Spanisch · „geprüft“           │ der Tabelle
   │                                                        │ korrigieren
 3 Erzeugen     Ziel wählen · Feinschliff · los             │
   │            (neue Bilder: 1–4 min, vorab im Reiter      │
   │            „Bildverbesserung“)                         │
   │                                                        │
 4 Prüfen       Prüfbogen + Checkliste ── alles richtig? ───┘
   │ ja
   Drucken      zu Hause (100 %, lange Kante), Druckerei – oder digital lernen
```

Viel Spaß beim Lernen – du schaffst das, Gans sicher!
