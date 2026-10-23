# Contributing to Me Goos-ta Deutsch 🪿

Thanks for wanting to help – ideas, bug reports and fixes are all goose-tastic!

## Before you start

1. **Open an issue first** (bug report or feature idea) and describe what you want to change. This avoids double work
   and lets us agree on the approach before you write code:
   https://github.com/LukasDieGans/me-goos-ta-deutsch/issues/new/choose
2. Security problems never go into a public issue – see [SECURITY.md](SECURITY.md).
3. Be kind – see the [Code of Conduct](CODE_OF_CONDUCT.md).

## Ground rules

- **Every visible text in three languages:** German (`de`), English (`en`, the default) and Spanish (`es`, as spoken in
  Mexico). A new text always gets all three at once – in `Programm/ui/index.html` in the object `TXT`, in Python via
  `L("de", "en", "es")`.
- **Friendly, positive tone**, goose puns welcome. Notes that need attention start with “Heads-up” (German
  “Achtung”, Spanish “Atención”) – never with an alarm word.
- **Nothing may disappear on Windows:** new things are added, existing behaviour stays.
- No new Python packages without a good reason; licenses must be MIT-compatible (MIT, BSD, Apache-2.0, OFL, MPL
  unchanged) and go into `Programm/requirements.txt` and `Programm/DRITTLIZENZEN.md`.
- License of contributions: MIT, like the project (`LICENSE.txt`).

## Tests

Both test suites must pass before a pull request is merged:

```text
cd Me-Goos-ta-Deutsch/Programm
python test_erweiterungen.py
python test_gans_lernkarten.py
```

- `test_gans_lernkarten.py` is the reference suite – **never change it**.
- New checks go into `test_erweiterungen.py` as a new section (`E<n>`).
- **Every pull request is tested automatically:** GitHub Actions builds the release and the web app from your branch,
  runs a quick lint (`ruff`, see `ruff.toml` – syntax errors and undefined names only), installs the program fresh on
  Windows, macOS and Linux (x64 and ARM) and tests the interface in Chromium, Firefox and WebKit. Pull requests from
  forks run with read-only rights and no secrets – nothing to set up on your side.
- GitHub Actions in workflows are pinned to a full commit SHA; Dependabot proposes updates as pull requests.

## Pull requests

- One topic per pull request, linked to its issue.
- Describe what changed and how you tested it (the template asks for it).
- Update the documentation with the change: user guides `Programm/LEITFADEN.md`, `LEITFADEN_en.md`,
  `LEITFADEN_es.md` (same content in all three) and `Programm/SPEC.md`.

## Code and specification are German

Variable names, comments and `SPEC.md` are written in German. A small glossary of the most common names:

| German | English | German | English |
| --- | --- | --- | --- |
| Gans | goose | Karte / karten | card / cards |
| Bild / bilder | image / images | Rückseite | back side |
| Vorschau | preview | Ausgabe | output |
| Einstellungen | settings | Sprache / Zielsprache | language / target (card) language |
| Übersetzer / übersetzen | translator / translate | Ideen | ideas (cards in progress) |
| Lernen / Lernstand | learn / learning progress | Werkzeug | tool (helper in the interface) |
| Lauf | run (background job) | Warteschlange | queue |
| Verlauf | history (undo/redo) | aktualisieren | update |
| prüfe / Prüfung | check / test | verarbeite | process (request) |
| Starter | launcher / first setup | Frischtest | fresh-install test |
| Datenordner | data folder | Handy | phone |

---

**Deutsch (kurz):** Bitte zuerst ein Issue öffnen, dann den Pull Request. Jeder sichtbare Text in de/en/es, positiver
Ton („Achtung“ statt Alarmwort). Beide Testreihen müssen grün sein; `test_gans_lernkarten.py` nie ändern, neue Prüfungen in
`test_erweiterungen.py`. Jeder Pull Request wird automatisch gebaut und auf allen Systemen getestet. Leitfäden (de/en/es)
und SPEC gehören zur Änderung.

**Español (breve):** Primero abre un issue y después el pull request. Cada texto visible en de/en/es, tono positivo.
Las dos series de pruebas deben pasar; nunca cambies `test_gans_lernkarten.py`, las pruebas nuevas van en
`test_erweiterungen.py`. Cada pull request se construye y se prueba automáticamente en todos los sistemas. Actualiza las guías (de/en/es) y la SPEC junto con el cambio. El código y la SPEC están en
alemán – la tabla de arriba ayuda.
