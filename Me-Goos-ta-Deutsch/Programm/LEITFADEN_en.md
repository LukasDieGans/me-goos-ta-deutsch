# Me Goos-ta Deutsch – Guide

Updated: 23 Oct 2026 · program and interface version 2.5 · German: `LEITFADEN.md` · Spanish: `LEITFADEN_es.md`

Great to have you here! This guide takes you from the first double-click to the finished card – step by step and without jargon. You don’t have to read it cover to cover: just jump to the part you need right now. And relax – no need to waddle along in single file; take every step at your own pace.

## Overview

Me Goos-ta Deutsch turns pictures with a “Gans …” pun into print-ready flashcards: the picture on the front, the word in {{Spanish}} on the back with a cheeky goose in the corner. Spanish here always means Spanish as spoken in Mexico – that’s why translation suggestions prefer Mexican words. (“Gans” is German for goose – and sounds just like “ganz”, which means “quite”. That’s the whole joke, and it never gets old.) New cards take four steps, all in the interface:

| Step | What happens |
| --- | --- |
| 1 Prepare images | Add one image or a whole bunch – or let **🪄 Create a goose with AI** paint a realistic goose photo from a short description (offline). The program checks format, size and sharpness, shows the front and names each file after the text on the image. You can add the {{Spanish}} word right away – typed yourself or as a suggestion (🌐) |
| 2 Label cards | Enter missing {{Spanish}} words or let the program suggest them. It checks whether they fit on the card and shows the back live |
| 3 Generate | In three small steps: choose a goal (home print, print shop, proof sheet, digital flashcards …), fine-tune, go. Images that aren’t enhanced yet get polished by AI (Real-ESRGAN) along the way |
| 4 Check & print | Look at the proof sheet, then print at home, at a print shop – or study digitally on your phone |

Always there to help you:

- **Table** – front and back of all cards side by side, ideal for checking translations.
- **Image enhancement** – enhance images in advance and compare before/after.
- **Ideas** – park half-finished ideas and finish them later at your own pace.
- **Tools** and **Help** – everything else, from phone access to the self-test.
- **Uninstall** – the last tab, in case you ever want to say goodbye (we hope not!).

Small hints appear when you point at almost any button and tell you what it does.

| Result (folder `ausgabe/`) | What for |
| --- | --- |
| `Me-Goos-ta-Deutsch_Pruefbogen.pdf` | Proof sheet: front and back of every card, texts, image sharpness |
| `Me-Goos-ta-Deutsch_Heimdruck_A4_88x63.pdf` (or `_Letter_`) | Print yourself on card stock, 8 cards per sheet, with crop marks |
| `Me-Goos-ta-Deutsch_Druckerei_88x63.pdf` | For a print shop: one page per card side, with 3 mm bleed |
| `einzelbilder/` | One PNG per card side for print shops that take images instead of PDF |
| `digital/` | Anki package, study page for the browser, screen PDF and, if you like, tables for other study apps |

The interface speaks English, German and Spanish – switch at the top right (EN · DE · ES). On the very first start it is set to English; the welcome assistant asks you for your favourite language right away. Everything before that – the guide “LIES MICH ZUERST” (read me first), the start file’s messages, the setup window and the loading screen of the phone app – starts in English too and follows your choice afterwards. The cards themselves of course stay the same.

## One-time setup

You don’t need to install anything beforehand – not even Python. On the first start the start file sets everything up by itself: its own Python in your user folder (**no administrator rights**; other Python installations stay untouched), the packages and an icon to start with. This takes 3–10 minutes and needs internet once (about 90 MB) – time for a cup of tea. Bigger extras such as the AI image enhancement are **tools**: you only download what you really want (see “Optional tools”). The file **“LIES MICH ZUERST”** (read me first) in the download shows everything again with pictures.

**Where to get it:** the download page https://lukasdiegans.github.io/me-goos-ta-deutsch/download/ has one ZIP for Windows, macOS and Linux (free, via GitHub Releases), with the steps for your system and the SHA-256 checksum. If it briefly shows only the goose symbol (an older phone app in the same browser), the old app version waddles out by itself and the page opens after a few seconds. Later you’ll also find the link in the program under **Help → “About this program”** (in the phone app: **More → “Get it for your computer”**).

**Windows 11 and 10**

1. **Unblock the ZIP** (important on Windows 11): right-click the ZIP file → “Properties” → at the bottom under “Security” tick **“Unblock”** → “OK”. Otherwise Smart App Control blocks the start file (see “Starting on Windows and Smart App Control”).
2. **Extract the ZIP:** right-click → “Extract All …”, for example into `Documents`.
3. **Double-click `Me Goos-ta Deutsch - Windows`.** A window shows the setup step by step, and a little duck swims along while something loads. Then the interface opens in your browser, and the icon **“Me Goos-ta Deutsch”** appears on the desktop (and in the Start menu).
4. From then on: double-click the desktop icon – the interface starts in seconds, without a black window.

**Mac:** double-click the ZIP to extract it, then double-click `Me Goos-ta Deutsch - Mac`. If macOS refuses to open it: from macOS 15 go to System Settings → Privacy & Security → “Open Anyway”; up to macOS 14 Control-click → “Open”. Always works: open the “Terminal” app, type `sh `, drag the file in, press Return. Afterwards “Me Goos-ta Deutsch” is in Launchpad and in the “Applications” folder of your home folder.

**Linux:** extract the ZIP, open a terminal in the folder and type `sh "Me Goos-ta Deutsch - Linux.sh"` – or right-click the file → “Run as a Program” (a terminal then opens by itself). Afterwards “Me Goos-ta Deutsch” is in your application menu. All it needs is `curl` or `wget` and `tar`, which are almost always there already.

**Welcome!** The first time you open the program, a small assistant greets you: choose your language, decide whether the program opens in the browser or in its own window, tick the tools you want (nothing is preselected), take a short tour – and off you go. “Ask later” shows it again on the next start.

**Is everything working?** Under “Tools” click “Start self-test”. At the end it says “ALLE TESTS BESTANDEN” (all tests passed) – everything in the green.

**What the start program recognises on every start:** first start → set everything up · interface already running → just open the browser · new program version or new folder → only catch up on what’s needed and offer to take over your cards from the previous folder · something missing or damaged → repair it by itself · two starts at the same time → the second waits patiently. Python, logs and settings live in `%LOCALAPPDATA%\Me-Goos-ta-Deutsch` (Mac: `~/Library/Application Support/Me-Goos-ta-Deutsch`, Linux: `~/.local/share/me-goos-ta-deutsch`), your work in the folder `Programm` (images, `karten.csv`, `ausgabe`).

The interface keeps running in the background even when the browser tab is closed; ⏻ at the top right stops it. Starting again simply reopens the browser.

## Installing a new version (update)

Your work lives in the folder `Programm`: the card list `karten.csv`, the images in `bilder/`, your ideas in `ideen/`, print files and enhanced images in `ausgabe/`, the settings in `ui_einstellungen.json` and your own goose image in `assets/`. The download of a new version contains none of this – its example cards come as `beispiel-karten.csv` and `beispiel-bilder/` and are only used in a brand-new folder. So nothing gets lost during an update.

**Easiest: right inside the program (since 2.4).** Under **Tools → “Keep the program up to date”** – also at the bottom of the menu below the version number (“🔎 Check for updates”) and under **Help → “About this program”** – the **“🔎 Check for a new version”** button asks GitHub (api.github.com) once for the latest release: only when you click, never on its own, never in the background, with no data about you or your cards, and nothing is stored. “Goose up to date!” means you already have the newest one. If a newer goose is out:

1. **“⬆️ Update to … now”** downloads the release from GitHub, checks the signature of the published `SHA256SUMS.txt` (only genuine Me Goos-ta Deutsch releases – checked and signed, from version 2.5), compares the checksum and checks the contents – the task shows the progress. Nothing is changed yet.
2. **“🔄 Restart now and install …”:** the program closes briefly, replaces only the program files **in the same folder** and starts again by itself via the start file (which sets up Python and packages if needed, like on the first start). No second folder, no doubled disk space, the desktop icon stays as it is.
3. A message reports “Update done”. If anything goes wrong while replacing, the program puts everything back and the previous version keeps running.

Cards, images, ideas, learning progress, settings, print files and your own goose image stay untouched – they are never part of the download. The in-program update exists only on the computer (the phone app updates itself; via phone access it is blocked) and only if the program folder is writable – otherwise a link takes you to the download page.

**By hand**, the new version is always on the download page (Help → “About this program”, link “Latest version for Windows, macOS and Linux”). There are two ways.

**Safest of all:** download a full backup under **Import / export** first. You can read it back in anywhere.

**Extract into a new folder**

1. Stop the running interface (⏻ at the top right).
2. Unblock the new ZIP (Windows: Properties → “Unblock”) and extract it with “Extract All …” – Windows suggests a new folder by itself.
3. Double-click the start file in the new folder. It finds the previous folder and asks whether your cards should be taken over – answer **Yes** (in the start window simply press Enter). Cards, images, ideas, enhanced images, settings and your own goose image are copied. Python, packages and installed tools are reused – nothing needs to be downloaded again.
4. From now on the desktop icon starts the new version. The previous folder stays unchanged; delete it once everything is fine.

After the takeover, the example cards of the new version are in `Programm/_beispiele/`. With **No** the new version starts with the example cards; you can take your cards over at any time by **importing** a backup.

**Also possible: extract over the old folder.** When extracting, choose the folder that contains your previous folder and pick “Replace the files in the destination”. Only program files are replaced – card list, images, ideas, print files, settings and goose image stay as they are. Then double-click the start file once.

## Starting on Windows and Smart App Control

Windows 11 has a protection feature called **Smart App Control**. It blocks start files downloaded from the internet, such as `.cmd`, if they aren’t signed. Windows recognises “from the internet” by an invisible mark it sets when downloading and passes on to all files when extracting. Signed programs may run – including the official Python from python.org that the start file uses.

| Option | Admin needed? | Verdict |
| --- | --- | --- |
| Unblock the ZIP before extracting: Properties → “Unblock” → OK, then extract | no | **recommended** – afterwards no file carries the mark |
| Unblock only the start file: right-click `Me Goos-ta Deutsch - Windows` → Properties → “Unblock” → OK | no | fine if you already extracted – the start file then removes the mark from all program files itself |
| Desktop icon (created on the first start) | no | for every later start – it is created on your computer and carries no mark |
| “Run as administrator” | yes | not needed |
| Switching off Smart App Control | yes | not recommended – it protects you from malware |

Libraries such as Pillow and NumPy contain program parts (DLLs) that aren’t signed by Microsoft. If Smart App Control blocks one of them, the start program notices, tries older, widely used versions by itself and, if needed, explains the remaining options. If only the preview library pypdfium2 is blocked, it switches it off – the PDFs are created anyway, and the program then draws the back preview itself.

## The interface

| Area | What you do there |
| --- | --- |
| My cards | All cards with preview (a click flips the card), image quality and notes. Edit, print or pause, change the order, take off the list – every change is saved immediately |
| 🎓 Learn | Learn your cards like in Anki: cards due today and new ones, your own decks, statistics, settings (tool “Learn cards”) |
| Table | Front and back of all cards side by side: compare, edit directly, tick translations as “checked”, filter, search, print |
| Image enhancement | Enhance images in advance, status per image, before/after comparison |
| 1 Prepare images | Add new images (a whole bunch at once is fine), check, name, label right away, add; “🪄 Create a goose with AI”, “🎨 Design a GANS image” |
| 2 Label cards | Enter the {{Spanish}} word or let it be suggested, watch the back live, save |
| Ideas | Collect ideas, complete them and make them cards; continue unfinished cards |
| 3 Generate | Choose a goal, fine-tune, go – on the right, the log tells you what’s happening |
| 4 Check & print | Proof sheet and checklist, printing at home or at a print shop, studying digitally |
| Tools | Keep the program up to date (update in the same folder), optional tools (image enhancement, translation, AI images), import / export, GANS image, program start, open on your phone, translation settings, self-test, project ZIP, folders |
| Help | This guide in the selected language, the specification, program status; if loading ever takes too long, use “Cancel” or “Try again” |
| Uninstall | Back up and remove cleanly |

The numbers in the menu show what’s still open: for step 1 the images not added yet, for step 2 the cards without a word, for “Ideas” your ideas, for “Table” the automatically translated words still waiting for your look.

## Undo and redo

Almost every change can be taken back: **↶** in the header (or **Ctrl+Z**, on a Mac **⌘+Z**) undoes the last step, **↷** (or **Ctrl+Y** or **Ctrl+Shift+Z**) redoes it. This works wherever you change your own data: saving cards, editing in the table, pausing, reordering or taking cards off the list, preparing images (add, label, rotate, add as card, discard), changing an image, ideas (create, edit, image, remove, turn into a card), word lists, import, “Add the goose” and the goose image on the back. The hover text of the buttons tells you what would be undone; after each undo, a message offers the way forward again.

- Up to **30 steps** can be undone; typing in the same new image and “🌐 Translate all” count as one step.
- A new change after “Undo” replaces the way forward – just like in any text editor.
- In text fields, Ctrl+Z works on the text itself as usual; in a learning session, Ctrl+Z takes back the last rating.
- The history covers the running session and starts fresh after quitting. If a file has changed in another way meanwhile (e.g. `karten.csv` in Excel), undo changes nothing to be safe, and the history starts fresh.
- Settings (language, colors, print options) and learning progress are not part of it. If undo takes back a text change, that card’s learning progress starts over – as with every change.

## Step 1: Prepare images

Drag images into the field or click it and choose – one or a whole bunch. No fitting photo? **“🪄 Create a goose with AI”** paints one, **“🎨 Design a GANS image”** puts the pun on a photo (both further below). Each image gets a row with a small preview of the front:

1. Enter the **text on the image** exactly as it appears, for example “Gans ausgeschlafen”. The file name is made from it: `gans-ausgeschlafen.jpg` (lower case, ä → ae, ö → oe, ü → ue, ß → ss, space → hyphen). If the file is already called “gans-….jpg”, the text is filled in for you.
2. **{{Spanish}} word** (optional): enter it right here or let 🌐 suggest one. If you leave it empty, the word comes in step 2.
3. On the right you see the result of the check: **✓ Ready**, **! Notes** or **✕ Quick check** – in the last case the image can be added as soon as that point is sorted.
4. **“Details ▾”** shows the original and the front in large, the full check list, **rotation** (↺ ↻) and the **crop**: “Show whole image” (empty margins are softly continued) or “Fill the card” (edges are cropped). ★ marks the recommendation for this image.
5. **“Add”** creates this one card. The image goes into the folder `bilder/`, the card into the card list.

Above the list, a bar shows how many images are ready. **“🌐 Translate all”** suggests a word for every image without one; **“Add all (n)”** adds all ready images at once.

The check list shows green ticks (all good), grey notes, orange warnings and red points. As long as something is red, the image waits before being added.

| Message | Meaning | What to do |
| --- | --- | --- |
| The program can’t read HEIC/HEIF photos | iPhone format | save as JPG: iPhone → Settings → Camera → Formats → “Most Compatible”, or save as JPG in the Photos app on your computer. Uploaded from the phone via phone access, the iPhone as a rule converts to JPG by itself |
| This file can’t be read as an image | damaged file or not an image | save the image again or choose another one |
| larger than 40 MB / more than 60 megapixels | very large file | shrink it a little (e.g. to 3000 px wide) |
| too small for a card (under 100 px) | tiny image | find a larger version |
| … ppi in print | source rather small | works anyway; a larger image makes it really sharp |
| … already exists in the image folder | name taken | change the text or tick “replace existing image” – the old version goes to `bilder/_entfernt/` |
| This exact image is already in the image folder | duplicate | “Discard” if it really is the same |
| The image is portrait, the card landscape | portrait format | fine; if it’s just turned the wrong way, rotate it with ↻ |
| “Fill the card” crops … % | strong crop | check in the preview that the text is fully visible – otherwise “Show whole image” |
| Black borders / transparency / CMYK / camera orientation / GIF, BMP, TIFF | corrected or converted automatically | nothing – the program takes care of it |

What matters for image quality: the image area of a card is 957 × 661 pixels at 300 dpi. From about 960 pixels wide the image is sharp in print; smaller images are enlarged with AI. Landscape around 3 : 2 fills the card best. The pun should be nice and large in the image – it is printed at most 8.1 cm wide.

## Design a GANS image

With **“🎨 Design a GANS image”** (step 1, Ideas or Tools) you turn a goose photo into a card image with the pun – goose-bumps easy:

1. Choose a photo or drag it into the window.
2. Choose the **crop** (square, card landscape, portrait); drag the image to move it, mouse wheel or slider to zoom.
3. Type the text after **GANS** – it appears in capitals (“GANS SEHR HEISS”). Drag the text on the image to place it; size, font and colour are up to you.
4. **“As a new card (step 1)”** hands the image to step 1, **“Save as idea”** creates an idea, **“Download”** saves the file. The file name follows the card rule: `gans-sehr-heiss.jpg`.

If the image comes from **“Create a goose with AI”**, it is already in place – crop “Card landscape”, word filled in. Opened from the card editor, the main button is **“Use for this card”**: the labelled image becomes this card’s new image. From an **idea** (“🖼️ Choose image …”, a click on the empty image area or dragging) your image is also already in place, with the idea’s text filled in: **“Use for this idea”** puts the labelled image in, **“Use image unchanged”** takes the file exactly as it is – no cropping, no text, handy when the pun is already on it.

## Create a goose with AI

No fitting photo at hand? **“🪄 Create a goose with AI”** (step 1), **“🪄 With AI …”** (card editor) or **“🪄 Create with AI …”** (Ideas) paints a realistic goose photo for you – offline, right on your computer. Once, you install the **“AI images”** tool (Tools → Optional tools) with the Segmind Vega + VegaRT model (Apache-2.0 license, about 3.5 GB); after that no internet is needed.

1. Enter the **word on the card** after “GANS”, e.g. “alt”. It is not painted into the image – the model doesn’t write clean text – but put on neatly afterwards.
2. **Description in English:** how and where is the goose? For example “swimming on a lake at sunset”, “sleeping in a nest of straw”, “standing in fresh snow”. Feel free to add light, season, weather or mood (“morning fog”, “golden hour”) – and say what should be visible rather than what shouldn’t. If the interface runs in German or Spanish, **“🌐 To English”** translates your description (only with translation switched on; only this description is sent). “… of 75 tokens” shows whether everything reaches the model.
3. **“No people”** (recommended, on by default) keeps people away – through the wording and a gentle negative prompt; it costs about 20 seconds more. It can’t rule them out completely: if someone still shows up, just roll again.
4. **“🪄 Create goose”** – on a normal laptop one image takes about 1–2 minutes. After each step you see a preview; you can close the window and keep working, or **stop** at any time.
5. Like the goose? **“✍️ Put the word on the image …”** opens it in “Design a GANS image” – from there as a new card or, from the card editor or an idea, for this card or idea. **“As a new card without word”**, **“Use for this card”** or **“Use for the idea without word”** takes the image directly; it is checked like any photo. **“🎲 Roll again”** paints a new variant, **“Download”** saves the image. Same description + same seed gives the same image.

| What it does well | Where it struggles |
| --- | --- |
| one goose in a natural setting, close and sharp | text and letters in the image |
| light, season, weather and landscape | exact numbers and several animals doing something together |
| simple poses: standing, swimming, flying, sleeping, eating, looking curious | human activities (riding a bike, reading), things held in beak or feet |
| | specific breeds, the same goose on several cards, now and then a leg or neck too many – then roll again |

**Default prompt (for the curious):** “Edit default prompt …” shows the template the program uses to talk to the model: `{description}` stands for your description, `{word}` for the card’s word (not used by default). You can save your own version and get the default back any time with “Restore default”.

Good to know: generating needs about 3 GB of memory (8 GB in the computer recommended). The model lives in the data folder, survives new program versions and is removed when you uninstall. Via phone access everything works the same – the computer does the work.

**Installing/removing the tool:** If the “AI images” tool isn’t there yet, the buttons stay visible anyway. “🪄 Create goose” or “Install the “AI images” tool …” in the AI window asks first – with a heads-up if memory is tight or there isn’t enough free space –, downloads the model through the queue and then reopens the AI window with what you entered. Removing: Tools → Optional tools → “AI images” → “Uninstall …” deletes the model and the intermediate images in `ausgabe/.ki-bild`; your own prompt version stays.

## Step 2: Label cards

Here you find all cards still missing their {{Spanish}} word – and every card you open in “My cards” with “Edit”.

| Field | Content |
| --- | --- |
| Word in {{Spanish}} | Goes on the back. `/` separates the main word (large) from alternatives (small underneath), e.g. `viejo / anciano`; `\|` sets a line break in the main word. 🌐 suggests a translation |
| Text on the image (German) | For checking on the proof sheet, not printed |
| Note | Just for you, e.g. the word type – not printed |

**Every card needs its goose:** the text on the image must contain “Gans” – also in the middle of the text (“Die Gans ist alt”) or as “Gäns…” (“Gänsehaut”). If it’s missing, the check says “The goose is still missing”, and saving puts “Gans” at the start; a message lets you know. This also applies to new images from step 1, ideas that become cards, changes in the table and imported cards. Older cards without a goose are reported in “My cards” – **“Add the goose”** puts it in front of all of them at once (can be undone).

The buttons á é í ó ú ñ ü ¿ ¡ insert Spanish special characters – handy with any keyboard. The back updates as you type. “Save card” (or Enter) writes the card into `karten.csv`; “Later” lets it wait patiently. With several cards, **“🌐 Translate all”** suggests a word for all empty fields, and **“Save all (n)”** saves all ready cards at once.

**Change image:** below the previews, **“Change image …”** fetches a new image for the card – or simply drag it onto the preview. It is checked as in step 1, with rotation and crop; word, text and note stay. “Use new image” moves the previous image to `bilder/_entfernt/`, “Undo” brings it back. **“🪄 With AI …”** paints a new goose image for this card instead (see “Create a goose with AI”).

| Message | What to do |
| --- | --- |
| Only the word in {{Spanish}} is missing | enter it – without a word the card isn’t printed |
| “ä” does not exist in Spanish | a typo? Spanish has á é í ó ú ü ñ, but no ä, ö, ß |
| The main word is a bit long for the card | shorten it or break it with `\|` at a good spot |
| The alternatives are a bit long / a lot of text | shorten or drop alternatives |
| more than 2 alternatives | keep the two most important |
| Spanish questions start with “¿” | e.g. `¿cómo estás?` |
| character can’t be printed | remove emoji and rare characters |
| Text must not start with = + - @ | protection against Excel formulas (also for the note) – remove the character at the start |
| The goose is still missing | write “Gans” anywhere in the text on the image – otherwise saving puts it at the start |
| still equals the German text | time to translate! |
| is already on card … | just a note – duplicate words are allowed |

**Editing the card list by hand (for advanced users):** every card is a row in `karten.csv` (semicolon as separator, UTF-8). Columns: `bild` (required), `de`, `es` (required), `notiz`, `fit` (`contain` or `cover`) and `uebersetzung` (`automatisch`, `geprüft` or empty). A row starting with `#` is skipped. In Excel choose “CSV UTF-8” when saving, otherwise ñ, á and ü get lost; then reload the interface.

```csv
bild;de;es;notiz;uebersetzung
gans-alt.jpg;Gans alt;viejo;Adjektiv;geprüft
gans-arg-hunger.jpg;Gans arg Hunger;muchísima hambre / me muero de hambre;Wendung;automatisch
```

## Collecting ideas

Good ideas often pop up in between – here they have their place. An idea only needs **an image, a German or a {{Spanish}} word – or an image idea**; the rest can come later.

- **“+ New idea”** creates an empty idea; typing text is enough, it is saved when you leave the field. There is one way for the image: **“🖼️ Choose image …”**, a click on the empty image area or dragging opens “Design a GANS image” – there you put “GANS + word” on it or use a finished image unchanged.
- **Image idea:** your note on what a fitting image could look like. **“🪄 Create with AI …”** (“AI images” tool) uses it as the description, together with the idea’s word; the description you create with stays saved in the image idea. Then **“✍️ Put the word on the image …”** or **“Use for the idea without word”** – the image goes straight to the idea. The AI understands English best; in other languages “🌐 To English” in the AI window translates with one click.
- **Does the word already exist?** While you type, the program instantly checks whether the word already exists as a card or idea – upper and lower case, umlauts and “Gans” don’t matter. So “Gans alt” doesn’t accidentally get made twice.
- **🌐 next to the German text** turns the {{Spanish}} word into a suggestion for the text on the image (“viejo” becomes “Gans alt”). Perfect when the {{Spanish}} word comes to mind first.
- Once image, text on the image and {{Spanish}} word are there, **“Make it a card”** becomes active: the idea goes through the same checks as in steps 1 and 2 and then appears under **My cards**.
- **“Discard”** can be undone with “Undo”.
- Below are all **unfinished cards** from “New card” with “Continue →”.

**Word list: many ideas at once.** Already have a vocabulary list? **“📋 Word list …”** turns it into ideas in one go – with or without translations.

1. Choose a file (CSV, TSV or text) or drag it in – or simply paste the list into the field and press “Check”.
2. The **preview** shows every line with a status: *new*, *twice in the list*, *already an idea*, *already a card* or *has errors* (with the reason). New lines are ticked, you decide on the rest; lines with errors are fixed in the list.
3. If something looks off, the options above help: separator, first line as heading, a single column is German or {{Spanish}}, swap columns, “Gans” in front. Every change checks the list again.
4. **“Create n ideas”** – done. The message afterwards has **“Undo”**: it takes the whole list back; ideas you have changed in the meantime stay.

| In the list | Becomes |
| --- | --- |
| `alt;viejo` | Gans alt → viejo |
| `müde` | Gans müde, the {{Spanish}} word follows later |
| `German;Word;Note` (first line) | heading – sets the order of the columns |
| `rot;rojo;Farbe` | third column = note |
| `# Farben` | comment, skipped |

Separators can be semicolon, tab, comma, “ = ” or “ – ”; at most 500 words and 1 MB per list, nothing is ever shortened silently. The word always belongs to the current card language – for another language, switch the card language first.

**🌐 Translate all** appears as soon as ideas have German text but no {{Spanish}} word yet: one click fetches a suggestion for all of them (with the same consent as everywhere). Only fields that are still empty at that moment get filled, marked as “automatic – check”. If the service’s daily quota runs out, the program stops cleanly and tells you how many are done.

## Automatic translation

**How it works:** 🌐 next to the field “Word in {{Spanish}}” – in step 1, step 2, Ideas and the table – fetches a suggestion. It appears in the field; underneath you see the source and more options to click. The first time, the program asks whether it may switch on translation and explains what is sent. There you can also tick “Translate new cards automatically from now on”.

**Checking stays important:** every word you take over is marked “translated automatically – check” – in “My cards”, in the table and on the proof sheet – until you tick it as “checked” in the table. Dictionaries don’t always hit the word people say in Mexico; a quick look from someone who speaks {{Spanish}} is worth its weight in gold.

| Service | What for | Account | Operator |
| --- | --- | --- | --- |
| Wiktionary | single words: several meanings and alternatives, maintained by people | no | Wikimedia Foundation |
| MyMemory | phrases of several words (machine) | no; about 5000 characters a day | Translated srl (Italy) |
| DeepL | very good machine translation | your own free key “DeepL API Free” | DeepL SE (Germany) |

“Automatic (recommended)” asks Wiktionary first for one or two words; for longer phrases DeepL (if a key is stored) or MyMemory. Everything else under **Tools → Automatic translation**.

**Security and privacy**

- Nothing goes to the internet without your consent; you can withdraw it any time under Tools.
- Only the word or phrase without “Gans” is sent – for example “aufgeregt” –, at most 80 characters. No images, no file names, no notes, no personal data.
- Only encrypted connections (HTTPS with certificate check) to the fixed addresses of the three services; answers are filtered (no HTML, no formulas, no control characters).
- A suggestion only gets into the card list when you take it over.
- Settings and DeepL key live in your user folder, readable only by your user account – not in the project folder and never in the browser. Remembered suggestions (up to 90 days) can be deleted under Tools.

**Installing/removing the tool:** Your consent is at the same time the installation of the “Automatic translation” tool – at the first 🌐 or under Tools → Optional tools. “Uninstall …” withdraws the consent and deletes the settings, the DeepL key and remembered suggestions. The 🌐 buttons stay and simply ask again next time.

## Table tab: checking translations

The table shows each card in one row: number, small image, **front (German) → back ({{Spanish}})**, note and check.

- **Edit:** click a cell and type; it is saved when you leave the field (Enter = done, Esc = discard). The same checks as in step 2 apply.
- **🌐** suggests a word for this row; **“🌐 Translate all”** fills all empty backs.
- Tick **“checked”** as soon as the translation is right. If the word changes later, the tick disappears again.
- **Filter, search and sort** by clicking a column header; “Show images” shows or hides the small images.
- **“Print table”** – handy for giving it to someone to proofread. The **“Compact”** view fits every card on one line, and ☐ can be ticked on paper.

## Image enhancement tab

Every front is prepared before printing: black borders removed, enlarged with **Real-ESRGAN x4plus** (the model also removes JPEG blocks and noise), brought to print size, gently sharpened and colour-corrected. The first time this takes about **1–4 minutes per image** (depending on your processor); after that the result comes straight from the cache.

In this tab you can get it done in advance while you keep working:

1. At the top are **AI upscaling** (Auto, Real-ESRGAN, Real-ESRGAN ×2, FSRCNN, Off) and **Quality** (Off, Standard, Strong). They also apply to “Generate”.
2. Select cards with the box at the top left of the image – or “Select all” / “Select not yet enhanced”.
3. **“✦ Enhance selected (n)”** starts. Underneath you see roughly how long it takes. “Cancel” keeps all images already done.

Every image carries a band: **enhanced** · **different setting** · **not enhanced yet** · **image missing**. A click shows **before and after** on top of each other – move the dividing line with the slider. When generating, missing images are enhanced anyway; the tab just saves you waiting time.

**Installing/removing the tool:** Real-ESRGAN is the “Image enhancement” tool. If it’s missing, the tab shows a box at the top with “Install” (about 64 MB) and the faster ×2 version. If you start anyway, the program asks: “Install and carry on” or “Just upscale (without the tool)” – then the built-in FSRCNN does the work. The same applies when generating with Real-ESRGAN set explicitly. “Uninstall …” (Tools → Optional tools) deletes the models, their copy in the data folder and the images enhanced with them in the cache; finished print PDFs stay.

## Step 3: Generate

Generating takes three small steps:

1. **What would you like to create?** Choose a tile:

| Goal | Result |
| --- | --- |
| Everything for print | Print-shop PDF, home print, proof sheet and templates in one go – perfect if you haven’t decided yet |
| Print-shop PDF | One page per card side with bleed, plus single images (PNG) |
| Home print | Several cards per sheet for your own printer, A4 or Letter |
| Proof sheet | Overview to check before printing |
| Digital flashcards | Study without paper: Anki, study page, screen PDF, tables for other apps |
| Blank templates | Guides for your own designs in another program |

2. **Fine-tuning** (optional – the defaults usually fit): only the settings that belong to your goal appear, each with an explanation. Everything is saved automatically; “Reset all settings” brings back the defaults.
3. **Let’s go!** With “Only these cards” (e.g. `11-14`) only new cards are made. On the right the log shows what’s happening – at the end it says “Done … – well done!”.

**Goose image on the back** (under “Orientation and back”): the drawn goose (default) or your own image. The drawn goose swims in a little pond at the bottom right and looks at the word; with a lot of text it gets a bit smaller in its corner – the word always stands free on calm blue. **“Load goose image …”** or drag an image onto the field – ideally a calm, rather light landscape image of at least 960 × 660 pixels. The program checks it, shrinks it to at most 2400 pixels and saves it without metadata (for example without location data). **“Use the drawn goose”** switches back, **“Previous image”** brings back the last one replaced.

| Setting | When |
| --- | --- |
| Paper A4 / Letter (home print) | Letter in the USA, Canada, Mexico and parts of Latin America; also used for the proof sheet |
| AI upscaling “FSRCNN (fast)” | fast instead of best quality, e.g. for trying things out |
| AI upscaling “Real-ESRGAN ×2” | almost the same quality, about 4× faster – download it first under Tools → Optional tools → Image enhancement “+ Faster ×2” |
| Quality “Strong” | stronger colours and sharpness; “Off” switches enhancement off |
| Print-shop file portrait | the print shop’s template asks for portrait |
| Rotate back by 180° | the back is upside down in the test print |
| Final size | another card size in mm, e.g. 74 × 52 |
| White border 0 | borderless cards |
| Horizontal/vertical offset (home print) | front and back don’t line up exactly in the test print |
| Recalculate all images | e.g. after an update |

For pros: “For pros: command line” shows the matching command; without the interface `py gans_lernkarten.py` (Mac/Linux: `python3`), all switches with `--help`.

## Optional tools

Some extras need a lot of space or send something to the internet. That’s why they are **tools**: not preinstalled, downloaded on request – and gone again whenever you like. Tabs and buttons always stay visible.

| Tool | What for | Size |
| --- | --- | --- |
| ✨ Image enhancement (Real-ESRGAN) | the loveliest AI upscaling for print; without the tool, the built-in FSRCNN enhances a little more simply | about 64 MB download (plus optional “Faster ×2”) |
| 🌍 Automatic translation | suggestions for the back side (Wiktionary, MyMemory, DeepL) – installing simply means: giving consent | no download |
| 🎨 AI images | realistic goose images, offline on your computer | about 3.5 GB |
| 🗣 Languages (back side) | more languages for the back – each one on its own (see “More languages”) | 0–17 MB per language |
| 🎓 Learn cards | learn your cards like with Anki (FSRS scheduler) – installing simply means: switching it on; uninstalling deletes your learning progress (export it first if you want to keep it) | no download |

- **The first time you open the program** it asks once which tools to download right away – nothing is preselected, and “Later” is perfectly fine.
- **Tools → Optional tools** shows each tool with its state (not installed · waiting · downloading … % · installed) and the space it uses. “Install” downloads it through the **queue** – you keep working meanwhile.
- **If a tool is missing** when you need it, the program asks (benefit, size, location, time). “Install and carry on” downloads it and then continues with your action by itself.
- **“Uninstall …”** asks first and then deletes only the tool’s files to free up space. Your cards, images and ideas stay, and you can reinstall the tool any time.
- Models or a consent from an earlier version count as installed straight away. Image enhancement also keeps a copy in the data folder – a new program version takes it over without a download.

## More languages

The back doesn’t have to be Spanish. The tool **🗣 Languages (back side)** offers 14 more languages: English, Low German, French, Italian, Turkish, Swedish, Norwegian, Polish, Russian, Japanese, Chinese, Korean, Hindi and Standard Arabic. Spanish is always included.

- **Tools → Optional tools → Languages** lists every language with its size. Languages with Latin script are there instantly (“no download”), the others load their font through the queue (1–17 MB).
- **“Use for back”** (or the **Back:** picker at the top of My cards, step 2 and the table – visible as soon as a language besides Spanish is installed) makes a language the **card language**. From then on it says “Word in Japanese” instead of “Word in Spanish” everywhere, 🌐 translates into the new language, and “open” counts the cards without a word in that language. This guide then talks about the chosen language, too.
- **Language chips** (“ES”, “JA”, “AR” …) show on every card in which languages a back already exists – filled = word there, dashed = still empty, dark = current card language. In My cards, clicking a chip shows the back in that language.
- **Several backs:** a card can have its own word for every language. In step 2 the field of the card language sits big at the top; below it, **“More languages”** opens one field per installed language – each with its own 🌐. The table shows one column per language and filters with “missing in …”.
- Arabic is written right to left; type Japanese, Chinese and Korean with your system’s input method. The special-character bar adapts to the language.
- **Removing** a language deletes only its language pack. Your words stay in `karten.csv` (one column per language) and are back right away after a new installation. If it was the card language, Spanish takes over again.

### Printing and exporting in other languages

- In **Step 3: Generate**, **Language of the back** sets the print language: the current card language by default, any installed language works too – and **“All installed”** queues one job per language.
- Each language prints with its own font from the language pack (Russian Noto Sans, Japanese/Korean/Chinese IBM Plex Sans, Arabic IBM Plex Sans Arabic, Latin-script languages and Hindi Poppins). Hindi and Arabic are shaped properly (joined letters, syllables), Arabic runs right to left – numbers and Latin words inside stay readable. Japanese and Chinese wrap between characters, never with a punctuation mark at the start of a line. The font size follows the real glyph widths.
- File names get the language code: `…_Druckerei_88x63_ja.pdf`, `…_Pruefbogen_ar.pdf`, `einzelbilder_ru/`, `digital/…_Anki_ja.apkg`. **Spanish stays as always** (no code) – so all languages sit peacefully side by side.
- **Print language code** (section “Orientation and back”): a small “JA”, “AR” … in the top left of the back helps when sorting mixed decks. “Auto” prints it only if the back isn’t Spanish.
- The **proof sheet** names the language (“JA: …”), and the **back preview** already shows the card language in its font.
- **Digital:** the Anki package gets its own deck per language (“Me Goos-ta Deutsch – Japanese”) and a note type with the language’s field, the study page sets language and writing direction, and `tabellen/karten_alle_sprachen.csv` holds all languages side by side (one column per language code).

## Queue

So your computer doesn’t break a sweat, only **one** task runs in the background at a time – generating, image enhancement, self-test, a tool download or an AI goose. If you start something while another task is running, it simply joins the queue (“In the queue – place 2”) and starts by itself when it’s its turn. The buttons stay free.

- **⏳ n** at the top right shows how many tasks are running or waiting. A click opens the **Queue** window.
- **Running now:** title, progress, duration and “Cancel” – afterwards the next task starts automatically.
- **Waiting:** ▲ ▼ move a task, **“Up next”** pulls it right to the front, **✕** takes it out; **“Remove all waiting”** asks first.
- **Recently done:** the last ten tasks with ✓ or ✕ and duration, plus “View result” or “Log”.
- Queuing the same task twice isn’t possible – it keeps its place. If a task can’t start (e.g. because the AI model is missing), it shows up with ✕ under “Recently done” and the queue keeps going.
- The queue only lives while the program is open. **Quit** asks first if something is still running or waiting.

## Changing colors

The interface can be as colorful as you like: **Tools → “🎨 Colors & appearance”**. The page shows every choice right away as a preview – it is only kept when you press **“Save”** (closing the window without saving puts everything back).

- **Goose sky** (default): the colors you have known from the start – unchanged.
- **Goose night** (dark), **Meadow** (fresh green) and **High contrast** (black on white, strong lines).
- **Like the system:** light or dark, depending on what your device is set to.
- **My own colors:** color pickers for background, surfaces (cards, windows), text, accent & buttons, lines, success (green) and error (red). Whatever you leave alone stays as in the default.
- The **contrast check** at the bottom shows how well text and background go together; from 4.5 : 1 it is easy to read, below that it says “Heads-up: hard to read”.
- **Reset to default** brings everything back to Goose sky. The choice also applies on your phone (phone access) and only affects the interface – the printed cards stay as they are.

## Step 4: Check & print

**Checking – a quick look is worth it, then every card is a hit.** The proof sheet shows the front and back of every card side by side, the texts and the image sharpness. The checklist next to it tells you what’s still open:

1. **Translation:** is the word right, and is that how people say it in Mexico? Most comfortable in the “Table” tab. Automatically translated words carry a note until they are ticked as checked.
2. **Image sharpness:** “… ppi in print” – from 180 ppi good, 120–179 okay, below that a bit low (a larger image helps).
3. **Test print:** print one page on plain paper at 100 % – if everything fits, off you go.

**Printing at home** (`…_Heimdruck_…pdf`, 8 cards per sheet):

- Print at 100 % or “Actual size” – not “Fit to page”.
- Double-sided, flip on the long edge. Without duplex: fronts first, flip the stack, then the backs.
- Sturdy card stock (about 200–300 g/m², 80–110 lb cover) makes the cards nice to hold.
- If front and back don’t line up exactly: set the offset in mm under “Home print” in Generate. Back upside down → “Rotate back by 180°”.
- Cut along the crop marks – with a ruler and craft knife or a paper trimmer. Round the corners if you like.

**Printing at a print shop** (`…_Druckerei_…pdf` or `einzelbilder/`): print shops for custom playing or study cards exist online in many countries – wherever you live. How to find a good one:

- **Search terms:** “custom playing cards”, “print your own card game”, “custom flashcards printing”; in German “Spielkarten individuell drucken”, in Spanish “imprimir cartas personalizadas”.
- **Important:** every card needs its **own front and back** – not just one shared back for all.
- **Size:** poker size 63 × 88 mm fits directly; other sizes can be set in Generate under “Final size”.
- **Bleed:** usually 3 mm all round – already included in the print-shop PDF (file 94 × 69 mm, final size 88 × 63 mm).
- **Orientation:** does the template ask for portrait? Then switch on “Print-shop file portrait”.
- **Upload:** as PDF or single images. Compare minimum order, card thickness, finish and shipping.
- **Check the preview:** especially the direction of the back – and order a sample first, then the whole stack.

## Learning cards

With the **“🎓 Learn cards”** tool you practise your cards right inside the program – the way learning research recommends. The first click on **“Learn”** in the menu switches it on (nothing is downloaded). The number in the menu shows how many cards are due today.

**How it works (in plain words):** You see the picture and try to recall the {{Spanish}} word – only then do you flip the card (“Show answer”). Then you say honestly how it went: **Again** (forgotten), **Hard**, **Good** or **Easy**. The **FSRS** scheduler (the same as in Anki) works out when you will only just still know the card and shows it again right then: at first after minutes, later after days, weeks and months. Each button shows when the card comes back. New cards are first learned in short steps (1 and 10 minutes).

| Area | What you find there |
| --- | --- |
| Today | how many reviews and new cards are waiting, “Let’s go” |
| Decks | “All active cards” and your own decks – by language, note, search text, only new/due/problem cards or by ticking; ✎ edit, 🗑 delete |
| Statistics | goose march (days in a row), learned today, due in the next 7 days, card progress (new · learning · young · mature), retention |
| Settings | new cards and reviews per day, desired retention (80–95 %, default 90 %), direction (picture → word, word → picture, both), learning language, start of the learning day (default 4 am) |
| Back up progress | export (JSON file), import (for each card the newer state wins), reset everything |

**While learning:** space = show answer, keys **1–4** = rate, **Ctrl+Z** = undo, **Esc** = finish. On a phone you tap the card; the rating buttons sit at the bottom in thumb reach, swiping right means “Good”, left “Again” (↶ takes it back). You can stop at any time – every rating is saved immediately, even if you close the program. If your system has a voice for the language, 🔊 reads the word aloud. After “Show answer” there is also a 🔊 next to the German text: it reads the German aloud exactly as it appears on the picture – in both directions, but only after revealing (otherwise it would give the answer away). It only uses a voice of your system that works without the internet (German from Germany first, then Austria, then Switzerland); without one there is no button. On Windows you can add a German voice in Settings under “Time & language → Language”.

**In “My cards”** each card shows its progress (new, learning, young, mature; the hover says how often it was learned and when the next review is). Above the list you filter by due, new, mature or problem cards. With **“☑ Select”** you tick cards and **“Learn now”** or put them into a deck.

**Changed a card?** If you change the German text, the word or the picture of a card you are already learning, it starts over when learning – the editor tells you beforehand, and a short message follows. A changed note keeps the progress.

**Tips:** A little every day beats a lot now and then. Be honest when rating – “Again” is not a mistake, it is exactly what makes the scheduler smart. Cards you keep forgetting become **problem cards**: a clearer picture or a note (e.g. a memory hook) often helps more than yet another review.

## Studying digitally

Fancy studying on the go? Choose **“Digital flashcards”** in Generate – the result is in `ausgabe/digital/`:

| Format | How to study with it |
| --- | --- |
| Anki package (`.apkg`) | open it in Anki on your computer (Windows, Mac, Linux) – or send it to your phone by mail, cloud or cable and import it in AnkiDroid (Android) or AnkiMobile (iPhone/iPad) |
| Study page (`.html`) | a single file that runs offline in the browser on your computer. Flip, “Got it” or “Again”; after flipping, 🔊 reads the German text aloud (only with an offline voice of your system, otherwise no button); your progress stays saved in that browser. On phones it only partly works (on the iPhone it usually won’t start from the Files app) – there, better use the Anki package or the screen PDF |
| Screen PDF | flip through in any PDF app: front, back, next card |
| Tables (CSV) | for Quizlet, Brainscape, Mochi & co. – choose “Tables for other apps” in fine-tuning |

In “Check & print” you get every file with “Download”, e.g. to send it to your phone. Even handier on the phone: the phone app (see “Get it as a phone app”) – with card studying, offline too.

## Importing and exporting cards and ideas

Under **My cards → “⇅ Import / export”** (also in Ideas and Tools):

- **Export:** download cards, ideas or **everything as a full backup** as a ZIP file – to back up, share or move to another computer. For cards, either all of them or only those that are printed.
- **Import:** choose or drag in such a ZIP file (or a `karten.csv`). First you see a **preview**: new · already here, but different · identical · faulty. If something already exists, you decide per row: **Keep** (your version stays) or **Replace** (the import wins). Nothing gets lost – replaced images go to `bilder/_entfernt/`. A word that already exists under another file name is recognised too.
- Images and texts are checked as in steps 1 and 2; Excel formulas, broken or HEIC images stay out.

## Open on your phone (Wi-Fi)

Upload photos straight from your phone? Under **Tools → “Open on your phone (Wi-Fi)”** you switch on phone access. It is off by default and only works in your own Wi-Fi:

1. “Switch on phone access” – a QR code, the address and a 6-digit PIN appear.
2. Scan the QR code with your phone camera (or type the address into the phone’s browser) and enter the PIN.
3. Done – now you can add images, create AI geese, label cards and collect ideas on your phone.

The address stays the same the next time you switch it on – so a bookmark on your phone keeps working. The very first time, Windows or macOS asks whether Python may accept connections: please allow it (private network).

For your safety: phone access is meant for your own home network only – the connection in the Wi-Fi is unencrypted. Never switch it on in public or other people’s networks (café, hotel, school, guest Wi-Fi). It switches itself off after 2 hours, after 5 wrong PINs and when the program stops. Stopping, uninstalling and opening folders only work directly on the computer.

## Get it as a phone app

Me Goos-ta Deutsch is also available as a **phone app** (web app) for Android, Google Pixel and iPhone/iPad – the same interface and the same program, just without the computer: Python runs right inside the phone’s browser. After the first load (a little over 20 MB) the app also starts without internet.

- **Address and guides:** on the computer, **Tools → “Open on your phone (Wi-Fi)”** shows the app’s QR code at the bottom (no Wi-Fi access needed for that), and so does “📲 Get it as a phone app” under **Check & print → Learn digitally**. Next to the start files there are three illustrated guides: `Me Goos-ta Deutsch - Android.html`, `… - iPhone.html` and `… - Google Pixel.html` – open one on the computer and scan the QR code, or send the file to your phone by e-mail or cloud. They need no JavaScript, so they open in file apps too.
- **Install:** open the app’s address in the browser and tap “📲 Install app” – with Chrome (Android, Google Pixel) it becomes a real app in your app drawer. On iPhone/iPad (iOS 16.4 or later): Safari → Share → “Add to Home Screen” → “Add”. The steps with sketches are in the app under **More → Install app**.
- **At the bottom** the app bar takes you everywhere: **Cards · New · Learn · Print · More**. “More” opens table, image enhancement, ideas, tools, help and the app things. The back gesture first closes an open window and then goes back one section. The same bar also appears via phone access on touch devices up to 860 px wide.
- **Your data stays on the device** (in the browser’s storage – no account, no upload). Under **More → Backup & storage**, “Back up everything” packs cards, images, ideas, learning progress and settings into one file; “Restore backup” brings them back and replaces everything on this device. On iPhone the data only stays for good in the installed app – otherwise Safari deletes website data after 7 days without a visit.
- **Take over cards from the computer:** on the computer, under My cards → ⇅ Import / export, export “Everything – full backup”, send the file to your phone (email, cloud, cable) and import it in the app – learning progress included.
- **Results** (print PDFs, Anki package, backup) open for **sharing** (print, email, “Files”) or **saving**. Long tasks show their progress, “Cancel” stops them; everything runs one after another through the queue.
- **What is different on a phone:** AI images are only available on the computer (3.5 GB model) – the button stays and lets you know. Real-ESRGAN is much slower on a phone; the built-in FSRCNN is good enough for printing. Automatic translation uses Wiktionary and MyMemory (DeepL only on the computer). Hindi and Arabic print without syllable shaping (that needs uharfbuzz on the computer). Start program, folders, phone access and uninstall don’t exist in the app.
- **New version:** the app fetches updates by itself in the background and says “A new goose version is here – reload?” (also under More).

## Program start: browser or own window

Whether Me Goos-ta Deutsch opens **in the default browser**, **in a specific browser** or **in its own window** without an address bar (this needs Edge, Chrome, Brave or Chromium) is decided in the welcome assistant – change it any time under **Tools → Program start**. It applies from the next start.

## Uninstall

The last tab **“Uninstall”** guides you in two steps:

1. **Back up cards and ideas:** “Download full backup” saves everything as one ZIP file. After a new installation – even on another device – “Import / export → Import” reads it all back in.
2. **Uninstall the program:** after a question (“Are you sure?”) and a tick, the program removes the desktop icon or app or menu entry, its own Python with settings and remembered translations **and the program folder with all cards, images and ideas**. This cannot be undone – that’s why step 1 exists. Your backup, files outside the program folder and other programs stay untouched.

Reinstalling works any time: extract the download, double-click the start file, import your backup – done.

## Image enhancement: which AI model?

Five freely available models were tested against the simpler FSRCNN on small, heavily compressed photos with text: Real-ESRGAN x4plus, Real-ESRGAN x2plus, Real-ESRGAN anime 6B, Real-ESRGAN general v3 and SwinIR-L. **Real-ESRGAN x4plus** gives the best result: it removes JPEG blocks, makes feathers and eyes convincingly sharp and keeps the lettering clean. Diffusion models are out: they invent details – letters included. Real-ESRGAN is licensed under BSD-3 and runs inside the program in pure NumPy, without extra software.

## Security

- The interface can only be reached on your computer and only opened via the start program (secret start key) – unless you deliberately switch on phone access, then additionally with a PIN in your own Wi-Fi.
- Other websites can’t remote-control it; files are only read and written in the project folders, and “Open” never starts programs or scripts.
- Automatic translation only sends after your consent and only the word to translate (for AI images, on click, the short description), encrypted to three fixed services.
- “Check for a new version” only asks when you click the button: one request to api.github.com, with no data about you or your cards. The program never looks for updates on its own.
- The download page and the phone app are hosted on GitHub Pages: like every web server, GitHub logs technical data such as the IP address. The project itself uses no trackers, no ads and no statistics; your cards never leave your device.
- Read aloud (🔊) only uses voices of your system that work offline – no text goes to the internet for it.
- The AI image model runs entirely on your computer; descriptions and images never leave it.
- Texts that Excel would treat as a formula (starting with = + - @) are rejected – also on import. Images are checked and saved without metadata.
- AI models and Python are only downloaded from official sources and verified by checksum; model files can’t run code.
- The goose installs an update in the program only if the release’s `SHA256SUMS.txt` is signed with the Me Goos-ta Deutsch key and names exactly this version (minisign, Ed25519) – a foreign or unsigned package is refused and nothing changes. Check it yourself: download page → “Check it’s genuine”.
- None of this needs administrator rights, and Windows Smart App Control stays switched on.

## Troubleshooting

Don’t worry – almost everything has a quick fix:

| Problem | Solution |
| --- | --- |
| “Python was not found …” or Windows asks for a program for `.py` files | No Python needed: the start file brings its own – just double-click it |
| “Smart App Control blocked …” | Unblock the ZIP or start file: Properties → “Unblock” → OK |
| “Windows protected your PC” | “More info” → “Run anyway” |
| Start window says “No internet connection” | Only the first start needs internet: check the connection and start again. What was already downloaded is reused |
| Start window says “The packages could not be installed” with “do not match the hashes” | A file arrived incomplete or altered on the way (e.g. proxy, company network, interrupted download). Every package file has a fixed checksum – if it doesn’t match, the program won’t install it. Simply start again; if that doesn’t help, try another network. Better safe than goose-sorry |
| The browser doesn’t open | Copy the address from the start window (http://127.0.0.1:…) into your browser |
| The page says “Please open it with the desktop icon …” | Start via the icon – a bookmark doesn’t work after a restart, the start key is new every time |
| “The connection took a little dip” | The interface was stopped – start it again via the icon |
| The icon does nothing or says “program folder moved” | Double-click the start file in the (new) program folder once – it checks and repairs everything |
| My cards are missing after an update | Import your backup – or copy `karten.csv` and the folder `bilder` from the old into the new `Programm` folder |
| 🌐 says “… not switched on yet” | Choose “Switch on and translate” in the window or allow it under Tools |
| “Oops, the goose got a little tangled up (…)” | an unexpected error – just try again; if it comes back, restart the program from its icon (the technical reason is in brackets, handy if you ask for help) |
| Translation service doesn’t answer / daily quota used up | Try again later, store your own DeepL key – or just type the word yourself |
| The phone can’t reach the address | Computer and phone must be in the same Wi-Fi; guest networks often keep devices apart. Did the Windows or macOS firewall ask whether Python may accept connections? Allow it for private networks |
| “🪄 Create a goose with AI” says the model is missing | Tools → Optional tools → AI images “Install” (about 3.5 GB, once); an interrupted download resumes next time |
| The AI goose looks more like a duck, has a leg too many, or there are people after all | 🎲 roll again; make the description more concrete; keep “No people” on and describe a quiet scene (“early morning”, “empty”) instead of a crowd |
| The AI image takes very long | 1–2 minutes are normal, older computers need 3–5; close other big programs. Switching “No people” off saves about 20 seconds |
| Goose image is rejected | Use JPG, PNG or WEBP (no HEIC), at least 300 pixels, at most 40 MB |
| Generating takes long | Real-ESRGAN needs 1–4 minutes per image the first time; after that it’s quick. Enhance images in advance in the “Image enhancement” tab or choose “FSRCNN (fast)” for trying things out |
| Back preview only shows the word | Double-click the start file once (repairs it); the PDFs are correct in any case |
| Word list: “looks like an Excel file” | in Excel “Save as” → “CSV UTF-8 (comma delimited)” – or copy the cells and paste them into the word list field |
| Word list shows gibberish (Ã¤ instead of ä) | save as “CSV UTF-8” or as UTF-8 text; the preview names the detected encoding at the top |
| Word list: “list too long – please split it” | at most 500 words and 1 MB per list: split it into several files and create them one after another |
| ñ, á or ü show up as gibberish | Save `karten.csv` as “CSV UTF-8” |
| Back upside down / print offset | “Rotate back by 180°” / “offset” in Generate |
| Image cropped awkwardly | Switch the crop in step 1 |

When in doubt: **Tools → Self-test**. It checks everything in a copy with the example cards and leaves your files untouched.

## Cheat sheet

```
 Start          desktop icon “Me Goos-ta Deutsch”
   │            (first time: start file in the folder)
   │
 1 Images       drag images in (a bunch is fine) ·  <───────┐
   │            or let AI paint a goose (1–2 min) ·         │
   │            text on the image · word · add              │
   │                                                        │
 2 Label        missing words (“Translate all”) ·           │ no:
   │            look at the back · “Save all”               │ fix in
   │                                                        │ step 1,
   Table        German ↔ Spanish · “checked”        │ step 2 or
   │                                                        │ the table
 3 Generate     choose goal · fine-tune · go                │
   │            (new images: 1–4 min, in advance in the     │
   │            “Image enhancement” tab)                    │
   │                                                        │
 4 Check        proof sheet + checklist ── all right? ──────┘
   │ yes
   Print        at home (100 %, long edge), print shop – or study digitally
```

Have fun learning – you’re doing great, and that’s Gans true!
