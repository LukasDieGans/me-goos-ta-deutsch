# Me Goos-ta Deutsch 🪿

**Learn German with goose puns – printable and digital flashcards.**
*Deutsch lernen mit Gänse-Wortwitzen · Aprende alemán con juegos de palabras de gansos*

**⬇️ Download:** https://lukasdiegans.github.io/me-goos-ta-deutsch/download/ – one package for Windows, macOS and Linux (free, MIT).

Me Goos-ta Deutsch turns pictures with a “Gans …” pun into flashcards: the picture on the front, the word in
Spanish on the back with a cheeky goose in the corner. (“Gans” – goose – sounds just like “ganz”, “quite”.)
Spanish always means Spanish as spoken in Mexico.
Print them at home, order them from a print shop, or study digitally with Anki, a study page or a screen PDF.

## Get started

1. **Extract the ZIP** (Windows 11: first right-click → Properties → tick “Unblock”).
2. **Double-click the start file** for your system:
   - Windows: `Me Goos-ta Deutsch - Windows`
   - Mac: `Me Goos-ta Deutsch - Mac`
   - Linux: `sh "Me Goos-ta Deutsch - Linux.sh"`
3. The first start sets everything up by itself (3–10 minutes, about 90 MB, **no administrator rights**, no Python
   needed beforehand). Then the interface opens in your browser and a welcome assistant greets you.

**“LIES MICH ZUERST.html” (Read me first)** explains every step with pictures – in English, with German and Spanish
one click away. Everything before and during the setup starts in English; afterwards the language you pick in the
program counts.

## New in 2.1

**Download for every system** – one ZIP for Windows, macOS and Linux as a GitHub release, with a friendly download
page (English, German, Spanish; detects your system, three illustrated steps, help for SmartScreen and Gatekeeper) ·
everything **before the setup starts in English** – afterwards the language you pick in the program counts · a **new
goose on the back side**: the word stays on a calm, plain background while the program’s goose paddles in a little pond
in the corner · the “Faster ×2” button in Tools is neatly laid out. Updating keeps your cards, settings and learning
progress.

## New in 2.0

Optional **tools** on demand (installed when you need them, removable again) · a **queue** for background jobs ·
**learn your cards** with FSRS spaced repetition · **15 back-side languages** · **colours & display** · a **phone app**
for Android, iPhone and Google Pixel · “Spanish” everywhere (as spoken in Mexico) · the specification in Help no longer
loads endlessly · change a card’s picture in the editor · realistic AI geese offline · phone polish and friendlier
error messages. Updating keeps your cards, settings and learning progress.

## What it can do

- Prepare many images at once – format, size and sharpness are checked automatically
- Label cards in Spanish, with optional translation suggestions (only after your consent)
- **Back side in 15 languages** – Spanish plus English, Low German, French, Italian, Russian, Japanese, Chinese,
  Korean, Hindi, Arabic, Turkish, Swedish, Norwegian and Polish (each one a small optional download)
- **Learn your cards** right in the program with spaced repetition (FSRS-6, like Anki) – your progress is kept
- Collect half-finished ideas, check for words you already have, import and export cards and ideas
- AI image enhancement (Real-ESRGAN, pure NumPy – no GPU needed) and realistic AI goose images, offline
- **Optional tools**: image enhancement, translation, AI images, languages and learning are only downloaded or
  switched on when you want them – and removed again just as easily
- A **queue** runs background jobs one after the other; **colours & display** with themes or your own colours
- Print files for home (A4 or Letter), for print shops (with bleed) and a proof sheet
- Digital flashcards: Anki package, offline study page, screen PDF, CSV for other apps
- Optional phone access in your own Wi-Fi (PIN-protected, off by default)
- **Phone app** for Android, iPhone/iPad and Google Pixel (web app, works offline, data stays on the phone):
  https://lukasdiegans.github.io/me-goos-ta-deutsch/
- Interface in English, German and Spanish; runs on Windows, macOS and Linux

## Documentation

| File | Content |
| --- | --- |
| `LIES MICH ZUERST.html` | Read me first: installation with pictures (EN · DE · ES) |
| `Me Goos-ta Deutsch - Android.html` · `… - iPhone.html` · `… - Google Pixel.html` | phone app: link, QR code, steps with sketches (EN · DE · ES) |
| `Programm/LEITFADEN_en.md` · `LEITFADEN.md` · `LEITFADEN_es.md` | user guide (EN · DE · ES), also under “Help” in the interface |
| `Programm/SPEC.md` | technical specification (German) |
| `Programm/DRITTLIZENZEN.md` | third-party licenses |

## Privacy and security

Everything stays on your computer. Internet is only used for the one-time setup (python.org, pypi.org, github.com –
every download is checked by checksum), for tools you install yourself (models and fonts from github.com or
huggingface.co, checked by checksum) and, only if you switch it on, for translation suggestions (only the single word
is sent). The interface is reachable only from your own computer unless you deliberately enable phone access.

## For developers

Python 3.13 with Pillow, NumPy, ReportLab and pypdfium2 (`Programm/requirements.txt`).
Self-tests: `python Programm/test_gans_lernkarten.py` and `python Programm/test_erweiterungen.py`.
Command line without the interface: `python Programm/gans_lernkarten.py --help`.

## License

MIT – see `LICENSE.txt`. Third-party components (Poppins font, FSRCNN and Real-ESRGAN weights, Python packages) keep
their own licenses – see `Programm/DRITTLIZENZEN.md`.

Have fun learning – you’re doing great! 🪿
