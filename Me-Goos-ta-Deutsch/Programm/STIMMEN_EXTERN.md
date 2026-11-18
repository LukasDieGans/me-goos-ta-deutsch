# Eigene Stimme mit anderen Programmen

Diese Anleitung gehört zum Tool **🎙 Eigene Stimme** von Me Goos-ta Deutsch. Sie zeigt, wie du Aufnahmen für deine Wörter mit kostenlosen Programmen erzeugst und einliest – gans ohne Abo. Me Goos-ta Deutsch startet und lädt keines dieser Programme; es liest nur die fertigen Audiodateien ein.

Stand der Angaben: November 2026. Lizenzen und Größen können sich ändern – es gilt immer die Seite des jeweiligen Projekts.

## Der Weg in drei Schritten

1. **Wortliste laden.** Werkzeuge → „Eigene Stimme“ → „Wortliste laden (CSV)“. Die Datei hat die Spalten `datei;sprache;text;vorhanden`. In `datei` steht der Name für jede Aufnahme, z. B. `es/3f2a9c0d1e4b5a67` – der Ordner ist die Sprache.
2. **Dateien erzeugen.** Für jedes Wort eine Audiodatei mit genau diesem Namen plus Endung, z. B. `es/3f2a9c0d1e4b5a67.wav`. Erlaubt sind WAV, MP3, OGG, Opus, M4A und WebM, je Datei höchstens 2 MB (WAV höchstens 15 Sekunden). Ein bis drei Sekunden je Wort sind ideal.
3. **Einlesen.** Den Ordner, die Dateien oder eine ZIP im Tool ablegen. Von da an spielt jedes 🔊 zuerst deine Datei.

Bitte nur die eigene Stimme verwenden – oder eine, für die du die Erlaubnis hast. Ehrensache unter Gänsen.

## Rezept 1: Selbst aufnehmen

Am einfachsten geht es direkt im Programm: 🎙 am Wort oder die **Aufnahme-Runde** im Tool. Wer lieber mit eigenem Gerät arbeitet:

- **Audacity** (GPL, kostenlos für jeden Zweck, etwa 40 MB): alle Wörter mit kurzen Pausen in einem Stück aufnehmen, die Wörter mit Textmarken versehen (als Name der Marke den Wert aus `datei` ohne Ordner eintragen) und über „Exportieren → Mehrere Dateien“ je Marke eine Datei schreiben. Für jede Sprache einen eigenen Ordner (`de`, `es`, …) wählen.
- **Handy-Diktiergerät**: je Wort eine Aufnahme, danach die Dateien am Rechner nach der Wortliste umbenennen. Die Formate der gängigen Geräte (M4A, MP3, WAV) passen ohne Umwandeln.

## Rezept 2: Fertige Stimme mit Piper

**Piper** ist eine Sprachausgabe, die ohne Internet auf dem eigenen Rechner läuft – ein eigenes Programm, nicht Teil von Me Goos-ta Deutsch.

- Lizenz: Programm GPL-3.0; die Stimmen haben eigene Lizenzen: Deutsch `de_DE-thorsten` (CC0), Spanisch aus Mexiko `es_MX-claude` (Apache-2.0) und `es_MX-ald` (Unlicense). Privat und kommerziell nutzbar.
- Größe: etwa 60 MB je Stimme, dazu das Programm. Läuft ohne Grafikkarte.
- Ablauf: Piper nach der Anleitung des Projekts installieren, die Stimme laden und für jede Zeile der Wortliste eine WAV-Datei erzeugen. Mit Python geht das in einer kleinen Schleife:

```
import csv, pathlib, subprocess, sys
stimmen = {"de": "de_DE-thorsten-medium", "es": "es_MX-claude-high"}
for z in csv.DictReader(open("wortliste.csv", encoding="utf-8-sig"), delimiter=";"):
    if z["sprache"] in stimmen:
        ziel = pathlib.Path("aufnahmen") / (z["datei"] + ".wav")
        ziel.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, "-m", "piper", "-m", stimmen[z["sprache"]], "-f", str(ziel), "--", z["text"].lstrip("'")], check=True)
```

Danach den Ordner `aufnahmen` im Tool ablegen.

## Rezept 3: Eigene Stimme klonen

Diese Programme lesen neue Wörter mit deiner Klangfarbe vor; als Vorlage genügt eine kurze, saubere Aufnahme von dir.

- **Chatterbox Multilingual** (Programm und Modell MIT, privat und kommerziell): 23 Sprachen, darunter Deutsch und Spanisch. Etwa 3 GB, braucht PyTorch; mit Grafikkarte deutlich schneller.
- **Pocket TTS** (Programm MIT, Modell CC-BY-4.0 – Namensnennung nötig): Deutsch und Spanisch, läuft auf dem Prozessor ohne Grafikkarte. Der Download des Modells verlangt ein kostenloses Konto beim Modell-Anbieter.

Ablauf bei beiden: Vorlage aufnehmen (10 bis 30 Sekunden, ruhiger Raum), für jede Zeile der Wortliste eine Datei mit dem Namen aus `datei` erzeugen, einlesen. Hör die Ergebnisse stichprobenweise an – einzelne kurze Wörter gelingen geklonten Stimmen nicht immer; die nimmst du dann schnell selbst im Programm auf.

## Rezept 4: Eigenes Piper-Modell trainieren

Für Geduldige: eine Piper-Stimme, die ganz deine ist.

- **Piper Recording Studio** (MIT): liest dir Sätze vor, die du nachsprichst – ein bis zwei Stunden Aufnahmen sind ein guter Anfang.
- **Training** mit den Werkzeugen von Piper (GPL-3.0): ein vorhandenes Modell wird mit deinen Aufnahmen weitertrainiert. Das braucht PyTorch und eine Grafikkarte und dauert Stunden.
- Hinweis: Wer statt der eigenen Grafikkarte einen kostenlosen Rechendienst im Internet nutzt, lädt die eigene Stimme dorthin hoch – sie verlässt dann dein Gerät.

Das fertige Modell benutzt du wie in Rezept 2.

## Rezept 5: Stimmumwandlung

**RVC** und **Applio** (beide MIT) verwandeln eine fertige Sprachausgabe – etwa aus Rezept 2 – in deine Klangfarbe. Dafür brauchst du etwa zehn Minuten eigene Aufnahmen und ein Training, am besten mit Grafikkarte. Das ist der aufwendigste Weg und hier nur der Vollständigkeit halber genannt.

## Übersicht

| Programm | Lizenz | Privat / kommerziell | Größe | Braucht |
| --- | --- | --- | --- | --- |
| Audacity | GPL | ja / ja | etwa 40 MB | Mikrofon |
| Piper + Stimme | GPL-3.0, Stimmen CC0 / Apache-2.0 / Unlicense | ja / ja | etwa 60 MB je Stimme | nichts Besonderes |
| Chatterbox Multilingual | MIT | ja / ja | etwa 3 GB | PyTorch, Grafikkarte ratsam |
| Pocket TTS | MIT, Modell CC-BY-4.0 | ja / ja (mit Namensnennung) | einige hundert MB | PyTorch, kostenloses Konto für den Download |
| Piper Recording Studio + Training | MIT / GPL-3.0 | ja / ja | mehrere GB | PyTorch, Grafikkarte |
| RVC / Applio | MIT | ja / ja | mehrere GB | PyTorch, Grafikkarte ratsam |

## Wenn etwas nicht passt

- **„ohne passendes Wort“**: Der Dateiname stimmt nicht mit der Wortliste überein. Nach jeder Änderung an einem Wort die Wortliste neu laden – der Name hängt am Text.
- **„nicht angenommen“**: Die Datei ist kein erlaubtes Format, größer als 2 MB oder als WAV länger als 15 Sekunden.
- **Ein 🔊 bleibt stumm**: Dein Browser spielt das Format nicht ab; dann liest die Stimme des Systems. WAV und MP3 spielen überall.
