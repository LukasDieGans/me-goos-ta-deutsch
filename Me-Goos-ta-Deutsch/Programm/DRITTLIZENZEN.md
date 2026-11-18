# Drittlizenzen · Third-party licenses · Licencias de terceros

Me Goos-ta Deutsch selbst steht unter der MIT-Lizenz (`LICENSE.txt` im Hauptordner). Dazu gehören der gesamte
Programmcode, die Oberfläche, das Programmsymbol, die gezeichnete Gans der Rückseite und die Beispielkarten mit ihren
selbst gezeichneten Bildern. Die folgenden Bestandteile stammen von anderen und behalten ihre eigenen Lizenzen.

*Me Goos-ta Deutsch itself is MIT-licensed (`LICENSE.txt`). The components below come from others and keep their own
licenses. · Me Goos-ta Deutsch tiene licencia MIT; los componentes de abajo conservan sus propias licencias.*

## Im Download enthalten · Included in the download

| Bestandteil | Ort | Lizenz | Quelle |
| --- | --- | --- | --- |
| Schrift **Poppins** (Regular, Medium, Bold) – Indian Type Foundry | `schrift/` | SIL Open Font License 1.1 (`schrift/OFL-Poppins.txt`) | https://fonts.google.com/specimen/Poppins |
| **FSRCNN**-Gewichte ×2/×3/×4 (Dong, Loy, Tang 2016; Saafke/FSRCNN_Tensorflow), umgewandelt nach NumPy | `modelle/fsrcnn_x*.npz` | Apache-2.0 (`modelle/LICENSE-FSRCNN.txt`) | https://github.com/Saafke/FSRCNN_Tensorflow |
| **pip** 26.2.1 (mit gebündelten Bibliotheken, u. a. certifi, requests, truststore) | `werkzeuge/pip-26.2.1-py3-none-any.whl` | MIT (Lizenzen der gebündelten Teile liegen im Rad bei) | https://pypi.org/project/pip/ |
| **FSRS-6** – Standardparameter und Formeln des Lernplaners nach **py-fsrs** 6.3 (Open Spaced Repetition), in `lernen.py` selbst in Python nachgebaut (kein fremder Code im Download) | `lernen.py` | MIT, Copyright (c) 2022 Open Spaced Repetition | https://github.com/open-spaced-repetition/py-fsrs |
| **Ed25519** (RFC 8032, Abschnitt 5.1; nach dem Python-Beispiel in Abschnitt 6 nachgebaut) und das Signaturformat von **minisign** (nur das Dateiformat, kein Code übernommen) – Prüfung signierter Releases | `signatur.py` | RFC 8032: Simplified BSD License, Copyright (c) 2017 IETF Trust and the persons identified as the document authors · minisign-Format: ISC | https://www.rfc-editor.org/rfc/rfc8032 · https://jedisct1.github.io/minisign/ |

## Beim ersten Start geladen · Downloaded on first start

Diese Teile lädt das Startprogramm von den offiziellen Quellen (Python mit eigener SHA-256-Prüfsumme, die Pakete über
pip von pypi.org in genau festgelegten Fassungen – seit 2.5 steht die SHA-256 jeder Datei in `pakete.lock`, pip prüft sie
mit `--require-hashes`). Sie liegen danach im Benutzerordner (nicht im Programmordner). Fassungen: `pakete.lock`
(Ersatz-Sätze für Smart App Control: `pakete-bewaehrt.lock`, `pakete-aelter.lock`).

| Bestandteil | Wofür | Lizenz | Quelle |
| --- | --- | --- | --- |
| **Python 3.13** (embeddable, Windows) | Laufzeit | PSF License 2.0 | https://www.python.org |
| **python-build-standalone** (Python 3.13, Mac/Linux) | Laufzeit | Python: PSF License 2.0; Build-Skripte: MPL-2.0; mitgelieferte Bibliotheken mit eigenen Lizenzen (im Paket) | https://github.com/astral-sh/python-build-standalone |
| **Pillow** | Bilder lesen und bearbeiten | MIT-CMU (HPND) | https://python-pillow.org |
| **NumPy** | Rechnen (KI-Vergrößerung) | BSD-3-Clause (Teile 0BSD, MIT, Zlib, CC0) | https://numpy.org |
| **ReportLab** | PDFs erzeugen | BSD-3-Clause | https://www.reportlab.com |
| **pypdfium2** mit **PDFium** | Vorschaubilder, PNG-Export | Apache-2.0 / BSD-3-Clause (PDFium: BSD-3-Clause; Lizenzen der Bauteile im Paket) | https://github.com/pypdfium2-team/pypdfium2 |
| **charset-normalizer** (Abhängigkeit von ReportLab ab 4.4) | Zeichensatz erkennen | MIT | https://github.com/jawah/charset_normalizer |
| **chardet** ≥ 7 (Abhängigkeit von ReportLab bis 4.2, nur Ersatz-Satz „älter“ unter Windows) | Zeichensatz erkennen | 0BSD (ältere Fassungen 5.x waren LGPL – darum fest ab 7) | https://github.com/chardet/chardet |

## Nur auf Wunsch geladen: Bildverbesserung · Downloaded only on request: image enhancement

Erst wenn du das Tool **Bildverbesserung** installierst (Werkzeuge → Tools oder auf Nachfrage beim ersten Gebrauch),
lädt das Programm das Modell von GitHub – mit SHA-256-Prüfsumme – und wandelt es in eine NumPy-Datei um
(`modelle/realesrgan-*.npz`). Deinstallieren löscht es wieder; ohne Tool verbessert das eingebaute FSRCNN.

| Bestandteil | Wofür | Lizenz | Quelle |
| --- | --- | --- | --- |
| **Real-ESRGAN x4plus** (Wang, Xie, Dong, Shan 2021), umgewandelt nach NumPy | beste Bildverbesserung | BSD-3-Clause (`modelle/LICENSE-RealESRGAN.txt`) | https://github.com/xinntao/Real-ESRGAN |
| Real-ESRGAN x2plus (optional, „Schneller ×2“) | schnellere Bildverbesserung | BSD-3-Clause | https://github.com/xinntao/Real-ESRGAN |

## Nur auf Wunsch geladen: KI-Bildmodell · Downloaded only on request: AI image model

Erst wenn du das Tool **KI-Bilder** installierst (Werkzeuge → Tools, mit Rückfrage), lädt das Programm diese Dateien von
Hugging Face – feste Revision, jede Datei mit Prüfsumme – in den Datenordner (`modelle/ki-bild`, ca. 3,5 GB). Sie sind nie Teil
des Downloads von Me Goos-ta Deutsch; gerechnet wird damit offline in reinem NumPy.

| Bestandteil | Wofür | Lizenz | Quelle |
| --- | --- | --- | --- |
| **Segmind Vega** (aus Stable Diffusion XL destilliert; Bildnetz, Text-Encoder CLIP ViT-L und OpenCLIP ViT-bigG, VAE, Tokenizer) | realistische Gänse-Bilder | Apache-2.0 | https://huggingface.co/segmind/Segmind-Vega |
| **Segmind VegaRT** (LCM-LoRA) | Bild in 4 Schritten statt 25+ | Apache-2.0 | https://huggingface.co/segmind/Segmind-VegaRT |
| **TAESDXL** (Ollin Boer Bohan) | schnelle Vorschau während des Rechnens | MIT | https://huggingface.co/madebyollin/taesdxl |

Herkunft: Segmind hat Vega aus SDXL (Stability AI) destilliert und veröffentlicht Vega und VegaRT unter Apache-2.0; die
Text-Encoder stammen ursprünglich von OpenAI CLIP und OpenCLIP/LAION (beide MIT). Die Bilder, die du damit erzeugst,
gehören dir; prüfe sie wie jedes Foto, bevor du Karten weitergibst oder druckst (KI-Bilder können Fehler enthalten,
z. B. ein Bein zu viel).

*The AI image model (Segmind Vega + VegaRT, Apache-2.0; TAESDXL, MIT) is downloaded only on request, never shipped,
and runs offline. · El modelo de imágenes IA (Segmind Vega + VegaRT, Apache-2.0; TAESDXL, MIT) se descarga solo si lo
pides, nunca viene incluido y funciona sin conexión.*

## Nur auf Wunsch geladen: Sprachpakete · Downloaded only on request: language packs

Erst wenn du im Tool **Sprachen** eine Sprache installierst, lädt das Programm ihr Paket in den Datenordner
(`sprachen/<code>`) – feste Revision, jede Datei mit SHA-256-Prüfsumme. Lateinische Sprachen und Hindi brauchen keine
eigene Schrift (Poppins hat die Zeichen). Entfernen löscht das Paket wieder.

| Bestandteil | Wofür | Lizenz | Quelle |
| --- | --- | --- | --- |
| **Noto Sans** Regular + Bold (Google) | Russisch | SIL Open Font License 1.1 (`OFL.txt` im Paket) | https://github.com/notofonts/notofonts.github.io |
| **IBM Plex Sans JP / KR / Arabic** Regular + Bold (IBM) | Japanisch, Koreanisch, Arabisch | SIL Open Font License 1.1 (`OFL.txt` im Paket) | https://github.com/google/fonts |
| **IBM Plex Sans SC** Regular + Bold (IBM) | Chinesisch (vereinfacht) | SIL Open Font License 1.1 (`OFL.txt` im Paket) | https://github.com/IBM/plex |
| **uharfbuzz** 0.56.3 mit **HarfBuzz** (per pip nach `sprachen/_pakete`, SHA-256 aus `pakete-sprachen.lock`) | Formen der Schrift für Hindi und Arabisch im Druck | Apache-2.0 (HarfBuzz: MIT „Old MIT“) | https://pypi.org/project/uharfbuzz/ |

Im Druck werden die Schriften als Teilmenge in die PDFs eingebettet (von der OFL ausdrücklich erlaubt); die PDFs selbst
stehen nicht unter der OFL. ReportLab zeichnet die von uharfbuzz geformten Glyphen (`ShapedStr`) – kein weiterer Code.

*Language packs (OFL fonts; uharfbuzz under Apache-2.0 with HarfBuzz under MIT) are downloaded only on request. · Los
paquetes de idioma (fuentes OFL; uharfbuzz con Apache-2.0, HarfBuzz con MIT) solo se descargan si los pides.*

## Handy-App (Web-App) · Phone app (web app) · App para el celular

Die Handy-App (gebaut mit `bau_webapp.py`, gehört nicht zum Download für Windows/Mac/Linux) bringt zusätzlich mit – jede
Datei mit fester Fassung und SHA-256-Prüfsumme, unverändert im Ordner `pyodide/` bzw. `modelle/` der App:

| Bestandteil | Wofür | Lizenz | Quelle |
| --- | --- | --- | --- |
| **Pyodide** 314.0.7 (CPython 3.14 als WebAssembly) | Python im Browser | MPL-2.0 (CPython: PSF License 2.0); Quelltext unter der Quelle | https://github.com/pyodide/pyodide |
| **NumPy** 2.4.6, **Pillow** 12.2.0, **charset-normalizer** 3.4.7 (Pyodide-Räder) | Rechnen, Bilder, ReportLab | BSD-3-Clause, MIT-CMU (HPND), MIT (Lizenzen in den Rädern) | https://pyodide.org |
| **ReportLab** 5.0.1 (reines Python-Rad von PyPI) | PDFs erzeugen | BSD-3-Clause | https://pypi.org/project/reportlab/ |
| **Real-ESRGAN x4plus** als `.npz` (nur auf Wunsch geladen) | beste Bildverbesserung | BSD-3-Clause | https://github.com/xinntao/Real-ESRGAN |

*The phone app additionally ships Pyodide (MPL-2.0), NumPy, Pillow, charset-normalizer and ReportLab (BSD/MIT-style
licenses, unmodified); the license texts are in `lizenzen/` and in the wheels. · La app para el celular incluye además
Pyodide (MPL-2.0), NumPy, Pillow, charset-normalizer y ReportLab (licencias tipo BSD/MIT, sin modificar).*

## Dienste im Internet (nur nach Zustimmung) · Online services (only with consent)

Die automatische Übersetzung fragt – erst nach ausdrücklicher Zustimmung in der Oberfläche – **Wiktionary** (Inhalte
CC BY-SA, Wikimedia Foundation), **MyMemory** (Translated srl) oder mit eigenem Schlüssel **DeepL** (DeepL SE). Es gelten
die Nutzungsbedingungen dieser Dienste; gesendet wird nur das zu übersetzende Wort – beim KI-Bild auf Klick
„🌐 Ins Englische“ die kurze Beschreibung der Szene. Übernommene Vorschläge aus Wiktionary sind einzelne Wörter bzw.
kurze Wendungen.

## Hinweise

- Anki, AnkiDroid, AnkiMobile, Quizlet, Brainscape, Mochi, Windows, macOS, iPhone und andere genannte Namen sind
  Marken ihrer jeweiligen Inhaber; Me Goos-ta Deutsch ist mit ihnen nicht verbunden. Das Anki-Paket (`.apkg`) wird mit
  der Python-Standardbibliothek selbst erzeugt – es wird kein Code von Anki mitgeliefert.
- Eigene Bilder, die du in das Programm lädst, bleiben deine; achte bei fremden Fotos selbst auf die Rechte, bevor du
  Karten weitergibst oder druckst.
