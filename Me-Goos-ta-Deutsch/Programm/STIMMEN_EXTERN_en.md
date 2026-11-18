# Your own voice with other programs

This guide belongs to the tool **🎙 Your own voice** of Me Goos-ta Deutsch. It shows how to create recordings for your words with free programs and import them – no subscription, just goose spirit. Me Goos-ta Deutsch neither starts nor downloads any of these programs; it only imports the finished audio files.

Information as of November 2026. Licences and sizes may change – the page of the respective project always applies.

## The way in three steps

1. **Get the word list.** Tools → “Your own voice” → “Get the word list (CSV)”. The file has the columns `datei;sprache;text;vorhanden`. `datei` holds the name for each recording, e.g. `es/3f2a9c0d1e4b5a67` – the folder is the language.
2. **Create the files.** One audio file per word with exactly this name plus extension, e.g. `es/3f2a9c0d1e4b5a67.wav`. Allowed are WAV, MP3, OGG, Opus, M4A and WebM, at most 2 MB per file (WAV at most 15 seconds). One to three seconds per word are ideal.
3. **Import.** Drop the folder, the files or a ZIP in the tool. From then on every 🔊 plays your file first.

Please use only your own voice – or one you have permission for. A matter of honour among geese.

## Recipe 1: Record it yourself

The easiest way is right inside the program: 🎙 next to the word or the **recording round** in the tool. If you prefer your own gear:

- **Audacity** (GPL, free for any purpose, about 40 MB): record all words in one go with short pauses, mark the words with labels (use the value from `datei` without the folder as the label name) and write one file per label via “Export → Multiple files”. Choose a separate folder for each language (`de`, `es`, …).
- **Phone voice recorder**: one recording per word, then rename the files on the computer following the word list. The formats of common devices (M4A, MP3, WAV) fit without converting.

## Recipe 2: A ready-made voice with Piper

**Piper** is a speech synthesiser that runs on your own computer without the internet – a program of its own, not part of Me Goos-ta Deutsch.

- Licence: program GPL-3.0; the voices have their own licences: German `de_DE-thorsten` (CC0), Mexican Spanish `es_MX-claude` (Apache-2.0) and `es_MX-ald` (Unlicense). Usable privately and commercially.
- Size: about 60 MB per voice, plus the program. Runs without a graphics card.
- Steps: install Piper following the project’s instructions, download the voice and create a WAV file for each line of the word list. With Python a small loop does it:

```
import csv, pathlib, subprocess, sys
stimmen = {"de": "de_DE-thorsten-medium", "es": "es_MX-claude-high"}
for z in csv.DictReader(open("wortliste.csv", encoding="utf-8-sig"), delimiter=";"):
    if z["sprache"] in stimmen:
        ziel = pathlib.Path("aufnahmen") / (z["datei"] + ".wav")
        ziel.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, "-m", "piper", "-m", stimmen[z["sprache"]], "-f", str(ziel), "--", z["text"].lstrip("'")], check=True)
```

Then drop the folder `aufnahmen` in the tool.

## Recipe 3: Clone your own voice

These programs read new words in your timbre; a short, clean recording of you is enough as a reference.

- **Chatterbox Multilingual** (program and model MIT, private and commercial use): 23 languages, including German and Spanish. About 3 GB, needs PyTorch; much faster with a graphics card.
- **Pocket TTS** (program MIT, model CC-BY-4.0 – attribution required): German and Spanish, runs on the processor without a graphics card. Downloading the model requires a free account with the model host.

Steps for both: record the reference (10 to 30 seconds, quiet room), create one file per line of the word list named as in `datei`, import. Listen to a sample of the results – cloned voices don’t always get single short words right; those you quickly record yourself in the program.

## Recipe 4: Train your own Piper model

For the patient: a Piper voice that is entirely yours.

- **Piper Recording Studio** (MIT): reads sentences to you that you repeat – one to two hours of recordings are a good start.
- **Training** with Piper’s tools (GPL-3.0): an existing model is trained further with your recordings. This needs PyTorch and a graphics card and takes hours.
- Note: if you use a free computing service on the internet instead of your own graphics card, you upload your voice there – it then leaves your device.

You use the finished model as in recipe 2.

## Recipe 5: Voice conversion

**RVC** and **Applio** (both MIT) turn finished speech output – for example from recipe 2 – into your timbre. You need about ten minutes of your own recordings and a training run, ideally with a graphics card. This is the most laborious way and is mentioned here only for completeness.

## Overview

| Program | Licence | Private / commercial | Size | Needs |
| --- | --- | --- | --- | --- |
| Audacity | GPL | yes / yes | about 40 MB | microphone |
| Piper + voice | GPL-3.0, voices CC0 / Apache-2.0 / Unlicense | yes / yes | about 60 MB per voice | nothing special |
| Chatterbox Multilingual | MIT | yes / yes | about 3 GB | PyTorch, graphics card advisable |
| Pocket TTS | MIT, model CC-BY-4.0 | yes / yes (with attribution) | a few hundred MB | PyTorch, free account for the download |
| Piper Recording Studio + training | MIT / GPL-3.0 | yes / yes | several GB | PyTorch, graphics card |
| RVC / Applio | MIT | yes / yes | several GB | PyTorch, graphics card advisable |

## If something doesn’t fit

- **“without a matching word”**: the file name doesn’t match the word list. Get the word list again after every change to a word – the name depends on the text.
- **“not accepted”**: the file isn’t an allowed format, is larger than 2 MB, or is a WAV longer than 15 seconds.
- **A 🔊 stays silent**: your browser can’t play the format; the system voice reads instead. WAV and MP3 play everywhere.
