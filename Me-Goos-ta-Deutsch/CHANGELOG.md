# Changelog

All notable changes to Me Goos-ta Deutsch are listed here – the newest first. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versions are numbered *major.minor* (a fix becomes a patch
version such as 2.5.1). Updating always keeps your cards, images, ideas, settings and learning progress.

## [Unreleased]

### Security
- Releases are signed: `SHA256SUMS.txt` carries a minisign/Ed25519 signature, and “Update now” installs a new version
  only if that signature is valid (key ID `6885AC6ACBF317E0`).
- The setup installs the Python packages in exactly pinned versions with a SHA-256 checksum for every file
  (`Programm/pakete.lock`, `pip --require-hashes`).
- Every release comes from a signed tag of the source code and is immutable once published – a fix gets a new version
  number instead of replacing files.

### Added
- The repository now holds the complete source code, the build and test tools and the automatic checks; every change
  and every pull request is built and tested on Windows, macOS and Linux (x64 and ARM) and in WebKit, Firefox and Chromium.
- Screenshots, this changelog and a privacy section on the download page.

### Changed
- Phone access in your Wi-Fi: the guide says more clearly that it is meant for your own home network only.
- `LICENSE.txt` is the plain MIT text (third-party licenses: `Programm/DRITTLIZENZEN.md`).

## [2.4] – 2026-10-22

### Added
- Update right inside the program: Tools → “Keep the program up to date” (and below the version number in the menu)
  finds a new version, “⬆️ Update now” downloads and checks it, “🔄 Restart now” installs it in the same folder.
- Undo and redo everywhere: ↶ ↷ in the header or Ctrl+Z / Ctrl+Y, up to 30 steps.
- Every card needs its goose: if “Gans” is missing from the German text, saving puts it at the start with a short note;
  “Add the goose” fixes older cards in one go.

### Fixed
- Clicking with a tiny drag in the before/after comparison no longer creates a new image in “Prepare images”.

## [2.3] – 2026-10-22

### Added
- “🪄 Create with AI …” right on an idea (with the optional “AI images” tool).
- New “Image idea” field: a note on what a fitting image could look like, also used as the AI description.

### Changed
- Ideas get their image through one “🖼️ Choose image …” button (or a click on the empty image area, or dragging).

## [2.2] – 2026-10-21

### Added
- 🔊 reads the German text aloud after you reveal the answer (offline voices of your system).
- Word lists in Ideas: up to 500 ideas at once with a preview and one-click undo; “🌐 Translate all”.
- “🔎 Check for a new version” in Help → About this program – only when you click.
- Automatic tests of every version on Windows, macOS and Linux and in three browser engines.

### Fixed
- The download page no longer shows only the start screen on phones with an app from before 2.1.

## [2.1] – 2026-10-20

### Added
- One ZIP for Windows, macOS and Linux as a GitHub release, with a friendly download page (EN · DE · ES).

### Changed
- Everything before the setup starts in English; afterwards the language you pick in the program counts.
- A new goose on the back side: the word stays on a calm background while the goose paddles in a little pond.
- The “Faster ×2” button in Tools is neatly laid out.

## [2.0] – 2026-10-16

### Added
- Optional tools on demand (image enhancement, translation, AI images, languages, learning) – removable again.
- A queue for background jobs, colours & display, 15 back-side languages.
- Learn your cards with FSRS spaced repetition, like Anki.
- Phone app for Android, iPhone and Google Pixel (web app, works offline).
- Change a card’s picture in the editor; realistic AI geese offline.

### Changed
- “Spanish” everywhere (as spoken in Mexico).

### Fixed
- The specification in Help no longer loads endlessly; friendlier error messages and phone polish.

## [1.6] – 2026-10-12

### Added
- Import and export of cards, an “Ideas” tab, “GANS image designer”, a compact table view and the swimming loading duck.
- Choose how the program opens (default browser, a specific browser or its own window); uninstall with double confirmation.
- Load your own goose image for the back side; an “Image enhancement” tab with a before/after comparison; a “Table” tab
  to check translations; translation suggestions after your consent; several images at once.

### Changed
- Updating keeps your own cards: the example cards ship as `beispiel-karten.csv` and `beispiel-bilder/`.

[Unreleased]: https://github.com/lukasdiegans/me-goos-ta-deutsch/compare/v2.4...HEAD
[2.4]: https://github.com/lukasdiegans/me-goos-ta-deutsch/releases/tag/v2.4
[2.3]: https://github.com/lukasdiegans/me-goos-ta-deutsch/releases/tag/v2.3
[2.2]: https://github.com/lukasdiegans/me-goos-ta-deutsch/releases/tag/v2.2
[2.1]: https://github.com/lukasdiegans/me-goos-ta-deutsch/releases/tag/v2.1
