"use strict";
const TOKEN = "app";
const AM_HANDY = "1" === "1";                    // über den Handy-Zugang (WLAN) geöffnet
document.documentElement.classList.toggle("am-handy", AM_HANDY);
const AM_APP = "1" === "1";                        // installierbare Handy-App (Web-App, gebaut von bau_webapp.py)
document.documentElement.classList.toggle("am-app", AM_APP);
// Untere App-Navigation: in der App bzw. am Touch-Gerät, jeweils bis 860 px Breite (sonst die Leiste links wie bisher)
const APP_NAVI = window.matchMedia ? matchMedia(AM_APP ? "(max-width: 860px)" : "(max-width: 860px) and (hover: none) and (pointer: coarse)") : null;
const appNaviSetzen = () => document.documentElement.classList.toggle("mit-app-navi", !!(APP_NAVI && APP_NAVI.matches));
appNaviSetzen(); if (APP_NAVI && APP_NAVI.addEventListener) APP_NAVI.addEventListener("change", appNaviSetzen);
// Bildtypen ausdrücklich nennen: dann wandelt das iPhone HEIC-Fotos beim Hochladen in JPG um
const BILD_ACCEPT = "image/jpeg,image/png,image/webp,image/gif,image/bmp,image/tiff,.jpg,.jpeg,.png,.webp,.gif,.bmp,.tif,.tiff";
const BILD_ACCEPT_WEB = "image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp";

/* ===================== Texte in drei Sprachen ===================== */
const TXT = {
de: {
  verbindung: "Die Verbindung ist kurz abgetaucht – keine Sorge, deine Karten sind sicher. Starte Me Goos-ta Deutsch einfach neu: über das Desktop-Symbol oder die Startdatei im Programmordner.",
  zu_karten: "Me Goos-ta Deutsch – zur Kartenübersicht", sprache: "Sprache der Oberfläche", beenden: "Beenden",
  beenden_titel: "Programm beenden", bereiche: "Bereiche",
  nav_karten: "Meine Karten", nav_neu: "Neue Karte", nav_bild: "Bilder vorbereiten", nav_beschriften: "Karten beschriften",
  nav_drucken: "Drucken", nav_erzeugen: "Erzeugen", nav_pruefen: "Prüfen & drucken", nav_werkzeuge: "Werkzeuge", nav_hilfe: "Hilfe",
  schritt1: "Schritt 1 von 4", schritt2: "Schritt 2 von 4", schritt3: "Schritt 3 von 4", schritt4: "Schritt 4 von 4",
  karten_titel: "Meine Karten", neue_karte: "+ Neue Karte",
  karten_unter: (g, a) => `${g} ${g === 1 ? "Karte ist" : "Karten sind"} bereit für den Druck${a ? `, ${a} ${a === 1 ? "macht" : "machen"} gerade Pause` : ""}. Klick auf eine Karte – schon dreht sie sich um.`,
  karten_leer_unter: "Deine Sammlung wartet auf ihre erste Karte.",
  karten_leer_titel: "Hier ist Platz für deine erste Karte", karten_leer_text: "Leg los mit Schritt 1: Füge ein Bild mit deinem „Gans …“-Wortwitz hinzu – deine erste Karte ist nur ein paar Klicks entfernt.",
  zu_schritt1: "Zu Schritt 1: Bild vorbereiten",
  banner_offen: n => `${n} ${n === 1 ? "Karte wartet" : "Karten warten"} nur noch auf das Wort auf {zs} – fast geschafft!`,
  banner_offen_knopf: "Zu Schritt 2", hinweise_liste: "Hinweise zur Kartenliste",
  umdrehen: "Klicken zum Umdrehen", karte_umdrehen: n => `Karte ${n} umdrehen`, bild_fehlt: "Bild fehlt",
  marke_bild_fehlt: "Bild fehlt im Ordner", marke_es_fehlt: "Wort kommt noch", marke_aus: "pausiert – wird nicht gedruckt",
  marke_ppi: (p, b) => `${p} ppi – ${b}`, nr_titel: "Kartennummer im Druck",
  bearbeiten: "Bearbeiten", drucken: "Drucken", drucken_titel: "Karte drucken oder vorübergehend auslassen",
  hoch: "Nach oben", runter: "Nach unten", entfernen: "Aus Liste entfernen", rueckgaengig: "Rückgängig",
  entfernt: b => `${b} aus der Liste entfernt – das Bild bleibt sicher im Ordner.`, gespeichert: "Gespeichert ✓",
  bewertung: { sehr_gut: "sehr gut", gut: "gut", ausreichend: "in Ordnung", gering: "eher knapp" },
  bild_titel: "Bilder vorbereiten",
  bild_unter: "Füge ein oder gleich viele Bilder mit deinem Wortwitz hinzu (z. B. „Gans alt“). Den Rest übernimmt das Programm: Es prüft Format, Größe und Schärfe, übernimmt den Text aus dem Dateinamen und benennt die Datei passend. Das Wort auf {zs} trägst du gleich hier ein – oder lässt es dir mit 🌐 vorschlagen.",
  ablage_titel: "Bilder hierher ziehen oder klicken", ablage_unter: "JPG, PNG oder WEBP · GIF, BMP, TIFF werden umgewandelt · bis 40 MB",
  ablage_loslassen: "Bilder loslassen", ablage_loslassen_unter: "Jedes Bild wird sorgfältig geprüft und vorbereitet.",
  nicht_hinzugefuegt: n => `Noch nicht dabei: ${n}`,
  zu_gross: (n, mb) => `${n} ist größer als ${mb} MB – etwas verkleinert passt es bestimmt.`,
  original: "Original", vorderseite: "Vorderseite", schnellvorschau: "Schnellvorschau",
  drehen_links: "90° nach links drehen", drehen_rechts: "90° nach rechts drehen",
  text_auf_bild: "Text auf dem Bild", text_auf_bild_ph: "z. B. Gans alt",
  ausschnitt: "Bildausschnitt", fit_contain: "Ganzes Bild zeigen", fit_cover: "Fläche füllen", empfohlen: "empfohlen", empfohlen_bild: "empfohlen für dieses Bild",
  ersetzen: "vorhandenes Bild ersetzen", uebernehmen: "Übernehmen und weiter →", verwerfen: "Verwerfen",
  alle_uebernehmen: "Alle übernehmen", uebernommen: n => `${n} übernommen`, jetzt_beschriften: "Jetzt beschriften →",
  ki_vorschau: m => `Das ist die schnelle Vorschau – beim Erzeugen poliert ${m} dein Bild noch richtig auf.`,
  beschriften_titel: "Karten beschriften",
  beschriften_unter: "Trag das Wort auf {zs} ein – es kommt auf die Rückseite. 🌐 schlägt dir gern eine Übersetzung vor. Mit „/“ trennst du Alternativen (z. B. „viejo / anciano“), mit „|“ setzt du einen Zeilenumbruch.",
  de_feld: "Text auf dem Bild (Deutsch)", es_feld: "Wort auf {zs}", es_ph: "Hauptwort / Alternative",
  notiz_feld: "Notiz (wird nicht gedruckt)", notiz_ph: "z. B. Adjektiv", sonderzeichen: "Sonderzeichen:",
  rueckseite: "Rückseite", karte_speichern: "Karte speichern", spaeter: "Später", bild_entfernen: "Bild entfernen",
  bild_aendern: "Bild ändern …", bild_hinzufuegen: "Bild hinzufügen …", ersatz_titel: "Neues Bild für diese Karte",
  ersatz_neu: "Neues Bild", ersatz_uebernehmen: "Neues Bild übernehmen", ersatz_ok: "Neues Bild übernommen – sieht klasse aus!",
  ersatz_zurueck_ok: "Das vorige Bild ist wieder da.", ja_starten: "Ja, starten",
  karte_gespeichert: "Karte gespeichert – stark!", neu_ohne_zeile: "neu – noch nicht in der Kartenliste",
  alles_beschriftet: "Alle Karten sind beschriftet – klasse!", alles_beschriftet_text: "Weiter geht’s mit den Druckdateien – oder du bereitest gleich noch ein Bild vor.",
  noch_ein_bild: "Noch ein Bild vorbereiten", weiter_erzeugen: "Weiter zu Schritt 3: Erzeugen",
  erzeugen_titel: "Erzeugen",
  befehl: "Entspricht dem Befehl", kopieren: "Kopieren", kopiert: "Befehl kopiert", kopieren_fehler: "Kopieren hat nicht geklappt – markiere den Text einfach selbst",
  alles_standard: "Alle Einstellungen auf Standard", standard_ok: "Alle Einstellungen stehen wieder auf Standard",
  bitte_pruefen: "Kurz prüfen: ", auswahl_ph: "alle Karten", auswahl_tipp: "Praktisch, um nur neue Karten zu drucken.",
  an: "An", aus: "Aus", standard: "Voreinstellung", leer: "leer",
  ki_hinweis_esrgan: m => `Bildverbesserung mit ${m}: beim ersten Mal 1–4 Minuten pro Bild – Zeit für einen Tee! Danach kommt es blitzschnell aus dem Zwischenspeicher. Den Fortschritt siehst du im Protokoll.`,
  ki_hinweis_fsrcnn: "Bildverbesserung mit FSRCNN (schnell). Noch schöner wird’s mit dem Modell Real-ESRGAN – zu laden unter Werkzeuge.",
  ki_hinweis_aus: "Bildverbesserung ohne KI.",
  protokoll: "Protokoll", bereit: "bereit", protokoll_leer: "Sobald ein Lauf startet, erzählt dir das Programm hier, was es gerade schafft.",
  laeuft: "läuft …", fertig_in: s => `fertig in ${s} s`, abgebrochen: "abgebrochen", fehler_code: c => `nicht geklappt (Code ${c})`,
  abbrechen: "Abbrechen", pruefbogen_oeffnen: "Prüfbogen öffnen", zu_schritt4: "Weiter zu Schritt 4",
  lauf_fertig: (t, s) => `${t}: fertig in ${s} s – super!`, lauf_fehler: t => `${t}: hat diesmal nicht ganz geklappt – im Protokoll steht, woran es lag.`,
  test_ok: "Selbsttest bestanden – alles läuft rund!", test_fehler: "Selbsttest: Ein paar Prüfungen klappen noch nicht – Details stehen im Protokoll.",
  pruefen_titel: "Prüfen & drucken", pruefen_unter: "Fast am Ziel! Ein Blick auf den Prüfbogen, dann geht’s ans Drucken. „Öffnen“ startet das passende Programm auf diesem Rechner.",
  ausgabe_oeffnen: "Ausgabeordner öffnen", nichts_erzeugt: "Hier landen gleich deine Druckdateien",
  nichts_erzeugt_text: "Starte in Schritt 3 deinen ersten Lauf – danach findest du hier Prüfbogen und Druckdateien.",
  zu_schritt3: "Zu Schritt 3: Erzeugen", letzter_lauf: "Letzter Lauf", karten: "Karten",
  ausgewaehlte: "Ausgewählte Karten", format: "Format", bildverbesserung: "Bildverbesserung", keine_hinweise: "Keine Hinweise – alles bestens!",
  oeffnen: "Öffnen", im_browser: "Im Browser ansehen", einzelbilder: "Einzelbilder",
  einzelbilder_text: n => `${n} PNG-Dateien, eine je Kartenseite – für Druckereien mit Bild-Upload`, ordner_oeffnen: "Ordner öffnen",
  vorlagen: "Leere Vorlagen",
  wird_geoeffnet: "Wird geöffnet …",
  werkzeuge_titel: "Werkzeuge", werkzeuge_unter: "Alles, was dir die Arbeit leichter macht: Tools, Selbsttest, Sicherung und Ordner.", erledigt: "Erledigt ✓",
  hilfe_titel: "Hilfe", hilfe_unter: "Der ganze Weg Schritt für Schritt – und alle technischen Angaben für Neugierige.",
  tab_leitfaden: "Leitfaden", tab_spec: "Spezifikation", tab_ueber: "Über dieses Programm",
  u_generator: "Generator", u_oberflaeche: "Oberfläche", u_python: "Python", u_projekt: "Projektordner", u_schrift: "Schrift",
  u_ki: "Bildverbesserung", u_vorschau: "Vorschau", u_vorschau_ok: "vollständig", u_vorschau_nein: "nur Vorderseite – für die Rückseiten-Vorschau „pip install pypdfium2“ ausführen",
  u_download: "Download für den Rechner", u_download_text: "Neueste Version für Windows, macOS und Linux",
  u_letzter: "Letzter Lauf", u_keiner: "noch keiner", u_erweitern: "Neue Funktionen ergänzen",
  u_erweitern_text: "Neue Schalter werden in gans_lernkarten.py in baue_parser() eingetragen und erscheinen in Schritt 3 automatisch. Eine neue Auswahl bei --nur wird automatisch zu einem Startknopf, neue Werkzeuge entstehen in gans_ui.py mit @werkzeug(…).",
  fuss_version: v => `Version ${v}`, fuss_ki: m => `KI: ${m}`, fuss_vorschau_ok: "Vorschau bereit", fuss_vorschau_nein: "Vorschau eingeschränkt",
  beendet: "Me Goos-ta Deutsch macht Pause. Du kannst dieses Fenster schließen – bis zum nächsten Mal!",
  keine_verbindung: "Gerade keine Verbindung zur Oberfläche", fehler_status: s => `Da hat etwas nicht geklappt (${s})`,
  nav_tabelle: "Tabelle", nav_verbesserung: "Bildverbesserung",
  zahl_tabelle_titel: n => `${n} automatisch übersetzte ${n === 1 ? "Karte wartet" : "Karten warten"} auf deinen prüfenden Blick`,
  tabelle_titel: "Vorderseite ↔ Rückseite",
  tabelle_unter: "Alle Texte nebeneinander – zum Vergleichen und Prüfen der Übersetzung. Zum Ändern direkt in eine Zelle klicken; gespeichert wird beim Verlassen des Feldes.",
  tabelle_drucken: "Tabelle drucken", tabelle_filter: "Filter", tabelle_suche: "Suchen …", tabelle_bilder: "Bilder zeigen",
  tabelle_fuss: "„Geprüft“ abhaken, sobald die Übersetzung stimmt – zum Beispiel nachdem jemand, der {zs} spricht, draufgeschaut hat. Automatisch übersetzte Wörter bleiben markiert, bis sie geprüft sind; ändert sich ein Wort, verschwindet das Häkchen wieder.",
  tabelle_nichts: "Keine Karte passt zu Filter und Suche – probier es mit einem anderen Begriff.",
  filter_alle: "Alle", filter_ungeprueft: "Noch nicht geprüft", filter_auto: "Automatisch übersetzt", filter_ohne: "Ohne Übersetzung", filter_hinweise: "Mit Hinweisen",
  spalte_nr: "Nr.", spalte_bild: "Bild", spalte_de: "Vorderseite (Deutsch)", spalte_es: "Rückseite ({zs})", spalte_notiz: "Notiz", spalte_status: "Prüfung",
  es_fehlt_ph: "kommt noch", geprueft: "geprüft",
  marke_auto: "automatisch übersetzt – prüfen", marke_auto_titel: "Vorschlag eines Übersetzungsdienstes, noch nicht als geprüft abgehakt (Reiter „Tabelle“)",
  marke_geprueft: "Übersetzung geprüft", marke_verbessert: "verbessert", marke_verbessert_titel: "Das Bild ist mit den jetzigen Einstellungen schon verbessert",
  verbesserung_titel: "Bildverbesserung",
  verbesserung_unter: "Wähle eine oder mehrere Karten aus und lass ihre Bilder schon vorab verbessern. Fertig verbesserte Bilder sind grün markiert; ein Klick auf ein Bild zeigt Vorher und Nachher. Beim Erzeugen werden noch fehlende Bilder ohnehin verbessert.",
  verb_fertig: "Bilder verbessert", verb_methode: "Verfahren", verb_qualitaet: "Qualität",
  verb_alle: "Alle auswählen", verb_offene: "Noch nicht verbesserte auswählen", verb_keine: "Auswahl aufheben",
  verb_start: n => `✦ Ausgewählte verbessern (${n})`,
  verb_nichts_gewaehlt: "Wähle Karten mit dem Kästchen oben links im Bild aus.",
  verb_schon_alle: "Alle ausgewählten Bilder sind schon verbessert – prima! Ein neuer Lauf nimmt sie direkt aus dem Zwischenspeicher.",
  verb_schaetzung: (n, d) => `${n} ${n === 1 ? "Bild wird" : "Bilder werden"} neu berechnet – geschätzt ${d}.`,
  verb_hinweis_esrgan: "Du kannst währenddessen weiterarbeiten; „Abbrechen“ behält alle schon fertigen Bilder.",
  verb_fortschritt: p => `${p} % geschafft`,
  verb_waehlen: "Auswählen", verb_waehlen_bild: b => `${b} auswählen`, verb_vergleich: "Vorher und Nachher vergleichen",
  band_verbessert: "verbessert", band_anders: "andere Einstellung", band_offen: "noch nicht verbessert", band_fehlt: "Bild fehlt",
  verb_frueher: m => `früher mit ${m} verbessert – mit den jetzigen Einstellungen noch nicht`,
  verb_ohne_vergr: "ohne Vergrößerung (Bild ist groß genug)",
  karte_nr: n => `Karte ${n}`,
  dauer_s: s => `etwa ${s} Sekunden`, dauer_min: m => `etwa ${m} Minuten`,
  vergleich_titel: b => `Vorher – Nachher: ${b}`, vorher: "Vorher", nachher: "Nachher", nachher_mit: m => `Nachher (${m})`,
  vergleich_regler: "Trennlinie verschieben", vergleich_hilfe: "Schieberegler bewegen oder ins Bild klicken und ziehen.",
  vergleich_fehlt: "Dieses Bild wartet noch auf seine Verbesserung. Zu sehen ist, wie es jetzt gedruckt würde – „Jetzt verbessern“ macht es noch schöner.",
  vergleich_anders: i => `Mit den jetzigen Einstellungen noch nicht verbessert (${i}). Zu sehen ist das Bild ohne Verbesserung.`,
  jetzt_verbessern: "✦ Jetzt verbessern", in_originalgroesse: "Nachher in Originalgröße", vorher_originalgroesse: "Vorher in Originalgröße",
  schliessen: "Schließen ✕", zur_verbesserung: "Zur Bildverbesserung",
  ki_hinweis_reiter: (f, n) => `${f} von ${n} Bildern sind schon verbessert → Bildverbesserung`,
  optional: "(optional)", es_spaeter_ph: "jetzt oder in Schritt 2", uebersetzen_titel: "Automatisch übersetzen (Vorschlag)",
  st_problem: "Kurz prüfen", st_hinweise: n => `Bereit, ${n} ${n === 1 ? "Hinweis" : "Hinweise"}`, st_bereit: "Bereit",
  st_mit_es: "fertig beschriftet", st_ohne_es: "Wort folgt in Schritt 2", st_auto: "automatisch übersetzt – bitte prüfen",
  uebernehmen_kurz: "Übernehmen", details: "Details ▾", details_zu: "Details ▴",
  hochladen_stand: (f, n) => `${f} von ${n} Bildern hochgeladen und geprüft …`,
  stapel_zahlen: (n, b, e) => `<b>${n}</b> ${n === 1 ? "neues Bild" : "neue Bilder"} · <b>${b}</b> bereit · <b>${e}</b> schon beschriftet`,
  alle_uebernehmen_n: n => `Alle übernehmen (${n})`, alle_uebersetzen: "🌐 Alle übersetzen",
  stapel_fertig: (n, m, o) => `${n} ${n === 1 ? "Karte" : "Karten"} angelegt${m ? ` – ${m} fertig beschriftet` : ""}${o ? `, ${o} ${o === 1 ? "wartet" : "warten"} noch auf das Wort` : ""}. Klasse!`,
  stapel_fehler: n => `${n} noch nicht übernommen – die Hinweise zeigen dir, was fehlt.`,
  karte_fertig: b => `${b}: Karte fertig – stark!`, in_tabelle_pruefen: "In der Tabelle prüfen",
  editor_zahlen: (n, b) => `<b>${n}</b> ${n === 1 ? "Karte wartet" : "Karten warten"} · <b>${b}</b> bereit zum Speichern`,
  alle_speichern: "Alle speichern", alle_speichern_n: n => `Alle speichern (${n})`, gespeichert_n: n => `${n} ${n === 1 ? "Karte" : "Karten"} gespeichert – super!`,
  zur_tabelle: "Zur Tabelle",
  vorschlag_von: (d, q) => `${d} schlägt für „${q}“ vor – kurz prüfen:`,
  chip_titel: "Klicken zum Übernehmen", kein_vorschlag: q => `Für „${q}“ hat der Dienst nichts gefunden – trag dein Wort einfach selbst ein, du kennst es am besten.`,
  uebersetze_n: (i, n) => `Übersetze ${i} von ${n} …`, uebersetzt_n: (g, n) => `${g} von ${n} Wörtern vorgeschlagen – ein kurzer prüfender Blick, und fertig.`,
  auto_fehler: m => `Die automatische Übersetzung macht gerade Pause: ${m}`,
  zust_titel: "Automatische Übersetzung einschalten?",
  zust_1: "Für einen Vorschlag schickt Me Goos-ta Deutsch das zu übersetzende Wort an einen Übersetzungsdienst im Internet.",
  zust_2: "Gesendet wird nur das Wort bzw. die Wendung ohne „Gans“ – zum Beispiel „aufgeregt“ –, beim KI-Bild auf Klick „🌐 Ins Englische“ die kurze Beschreibung. Keine Bilder, keine Dateinamen, keine persönlichen Daten.",
  zust_3: "Standard: Wiktionary (freies Wörterbuch) für einzelne Wörter, MyMemory für Wendungen – beide ohne Konto. Wahlweise DeepL mit eigenem Schlüssel.",
  zust_4: "Vorschläge kommen nur in die Kartenliste, wenn du sie übernimmst, und bleiben als „automatisch übersetzt“ markiert, bis du sie in der Tabelle als geprüft abhakst.",
  zust_5: "Nur verschlüsselte Verbindungen zu fest eingetragenen Adressen; die Antworten werden gefiltert (keine Formeln, kein HTML).",
  zust_6: "Ausschalten oder Dienst wechseln: Werkzeuge → Automatische Übersetzung.",
  zust_auto: "Neue Karten künftig gleich automatisch übersetzen", zust_ja: "Einschalten und übersetzen",
  ue_titel: "Automatische Übersetzung", ue_an: "an", ue_aus: "aus",
  ue_text: "Schlägt beim Erstellen der Karten das Wort auf {zs} vor. Gesendet wird nur das zu übersetzende Wort; jeder Vorschlag bleibt markiert, bis du ihn in der Tabelle als geprüft abhakst.",
  ue_einschalten: "Automatische Übersetzung erlauben", ue_dienst: "Übersetzungsdienst",
  ue_auto: "Automatisch (empfohlen)", ue_auto_text: "Einzelne Wörter aus dem Wörterbuch Wiktionary, Wendungen von DeepL (wenn ein Schlüssel hinterlegt ist) oder MyMemory.",
  ue_dienst_auto: "automatisch", ue_dienst_wiktionary: "Wiktionary", ue_dienst_mymemory: "MyMemory", ue_dienst_deepl: "DeepL",
  ue_deepl: "Eigener DeepL-API-Schlüssel (optional)", ue_deepl_da: e => `Schlüssel hinterlegt (${e})`,
  ue_deepl_hilfe: "Kostenlos nach Anmeldung bei DeepL („DeepL API Free“). Der Schlüssel bleibt in deinem Benutzerordner, ist nur für dich lesbar und wird nur an DeepL geschickt.",
  ue_deepl_ok: "DeepL-Schlüssel gespeichert", ue_deepl_weg: "DeepL-Schlüssel entfernt",
  ue_automatisch: "Neue Karten automatisch übersetzen (Vorschläge gleich eintragen)",
  ue_cache: "Gemerkte Übersetzungen löschen", ue_cache_ok: "Gemerkte Übersetzungen gelöscht",
  ue_datenschutz: o => `Einstellungen und gemerkte Übersetzungen liegen in ${o} – nicht im Projektordner und nicht in der Projekt-ZIP.`,
  entfernen_kurz: "Entfernen", speichern: "Speichern", u_uebersetzung: "Automatische Übersetzung", u_kartensprache: "Kartensprache", u_kartensprache_wert: "Spanisch (gemeint ist immer das in Mexiko gesprochene Spanisch)",
  gans_gezeichnet: "Gezeichnete Gans (Standard)", gans_geladen: g => `Eigenes Gänse-Bild (${g})`, gans_pfad: p => `Bild aus ${p}`,
  gans_tipp: "Tipp: ein ruhiges, eher helles Bild im Querformat, mindestens 960 × 660 Pixel – das Wort steht dunkelblau darüber. Das Bild füllt die Rückseite und wird mittig zugeschnitten.",
  gans_laden: "Gänse-Bild laden …", gans_anderes: "Anderes Bild laden …", gans_weg: "Gezeichnete Gans verwenden", gans_zurueck: "Vorheriges Bild",
  gans_ziehen: "Du kannst ein Bild auch hierher ziehen.",
  gans_hilfe: "Hintergrund aller Rückseiten. Das Bild wird geprüft, auf höchstens 2400 Pixel verkleinert und ohne Metadaten als assets/gans_hintergrund gespeichert; das alte kommt nach assets/_alt/.",
  gans_ok: "Gänse-Bild geladen – sieht klasse aus! Die Rückseiten nutzen es ab sofort.", gans_weg_ok: "Zurück zur gezeichneten Gans", gans_zurueck_ok: "Vorheriges Gänse-Bild wiederhergestellt",
  datum: "de-DE",
},
en: {
  verbindung: "The connection took a little dip – don’t worry, your cards are safe. Just restart Me Goos-ta Deutsch: with the desktop icon or the start file in the program folder.",
  zu_karten: "Me Goos-ta Deutsch – to the card overview", sprache: "Interface language", beenden: "Quit",
  beenden_titel: "Quit the program", bereiche: "Sections",
  nav_karten: "My cards", nav_neu: "New card", nav_bild: "Prepare images", nav_beschriften: "Label cards",
  nav_drucken: "Print", nav_erzeugen: "Generate", nav_pruefen: "Check & print", nav_werkzeuge: "Tools", nav_hilfe: "Help",
  schritt1: "Step 1 of 4", schritt2: "Step 2 of 4", schritt3: "Step 3 of 4", schritt4: "Step 4 of 4",
  karten_titel: "My cards", neue_karte: "+ New card",
  karten_unter: (g, a) => `${g} ${g === 1 ? "card is" : "cards are"} ready to print${a ? `, ${a} ${a === 1 ? "is" : "are"} taking a break` : ""}. Click a card and it flips right over.`,
  karten_leer_unter: "Your collection is waiting for its first card.",
  karten_leer_titel: "Room for your very first card", karten_leer_text: "Start with step 1: add an image with your “Gans …” pun – your first card is just a few clicks away.",
  zu_schritt1: "Go to step 1: Prepare image",
  banner_offen: n => `${n} ${n === 1 ? "card is" : "cards are"} only waiting for the {zs} word – almost there!`,
  banner_offen_knopf: "Go to step 2", hinweise_liste: "Notes on the card list",
  umdrehen: "Click to flip", karte_umdrehen: n => `Flip card ${n}`, bild_fehlt: "Image missing",
  marke_bild_fehlt: "Image missing in folder", marke_es_fehlt: "Word coming soon", marke_aus: "paused – not printed",
  marke_ppi: (p, b) => `${p} ppi – ${b}`, nr_titel: "Card number in print",
  bearbeiten: "Edit", drucken: "Print", drucken_titel: "Print this card or leave it out for now",
  hoch: "Move up", runter: "Move down", entfernen: "Remove from list", rueckgaengig: "Undo",
  entfernt: b => `${b} removed from the list – the image stays safe in the folder.`, gespeichert: "Saved ✓",
  bewertung: { sehr_gut: "very good", gut: "good", ausreichend: "okay", gering: "a bit low" },
  bild_titel: "Prepare images",
  bild_unter: "Add one image or a whole bunch with your pun (e.g. “Gans alt”). The program takes care of the rest: it checks format, size and sharpness, takes the text from the file name and names the file to match. Enter the {zs} word right here – or let 🌐 suggest one.",
  ablage_titel: "Drag images here or click", ablage_unter: "JPG, PNG or WEBP · GIF, BMP, TIFF are converted · up to 40 MB",
  ablage_loslassen: "Drop images", ablage_loslassen_unter: "Each image is carefully checked and prepared.",
  nicht_hinzugefuegt: n => `Not in yet: ${n}`,
  zu_gross: (n, mb) => `${n} is larger than ${mb} MB – shrink it a little and it will fit.`,
  original: "Original", vorderseite: "Front", schnellvorschau: "Quick preview",
  drehen_links: "Rotate 90° left", drehen_rechts: "Rotate 90° right",
  text_auf_bild: "Text on the image", text_auf_bild_ph: "e.g. Gans alt",
  ausschnitt: "Framing", fit_contain: "Show whole image", fit_cover: "Fill the card", empfohlen: "recommended", empfohlen_bild: "recommended for this image",
  ersetzen: "replace existing image", uebernehmen: "Add and continue →", verwerfen: "Discard",
  alle_uebernehmen: "Add all", uebernommen: n => `${n} added`, jetzt_beschriften: "Label now →",
  ki_vorschau: m => `This is the quick preview – when generating, ${m} gives your image a proper polish.`,
  beschriften_titel: "Label cards",
  beschriften_unter: "Enter the word in {zs} – it goes on the back. 🌐 is happy to suggest a translation. Use “/” to separate alternatives (e.g. “viejo / anciano”) and “|” for a line break.",
  de_feld: "Text on the image (German)", es_feld: "Word in {zs}", es_ph: "main word / alternative",
  notiz_feld: "Note (not printed)", notiz_ph: "e.g. adjective", sonderzeichen: "Special characters:",
  rueckseite: "Back", karte_speichern: "Save card", spaeter: "Later", bild_entfernen: "Remove image",
  bild_aendern: "Change image …", bild_hinzufuegen: "Add image …", ersatz_titel: "New image for this card",
  ersatz_neu: "New image", ersatz_uebernehmen: "Use new image", ersatz_ok: "New image in place – looks great!",
  ersatz_zurueck_ok: "The previous image is back.", ja_starten: "Yes, start",
  karte_gespeichert: "Card saved – nice work!", neu_ohne_zeile: "new – not yet in the card list",
  alles_beschriftet: "All cards are labelled – brilliant!", alles_beschriftet_text: "On to the print files – or prepare another image right away.",
  noch_ein_bild: "Prepare another image", weiter_erzeugen: "Continue to step 3: Generate",
  erzeugen_titel: "Generate",
  befehl: "Equivalent command", kopieren: "Copy", kopiert: "Command copied", kopieren_fehler: "Copying didn’t work – just select the text yourself",
  alles_standard: "Reset all settings", standard_ok: "All settings are back to default",
  bitte_pruefen: "Quick check: ", auswahl_ph: "all cards", auswahl_tipp: "Handy for printing only new cards.",
  an: "On", aus: "Off", standard: "Default", leer: "empty",
  ki_hinweis_esrgan: m => `Image enhancement with ${m}: the first time 1–4 minutes per image – time for a cup of tea! After that it comes straight from the cache. You can follow the progress in the log.`,
  ki_hinweis_fsrcnn: "Image enhancement with FSRCNN (fast). It gets even prettier with the Real-ESRGAN model – download it under Tools.",
  ki_hinweis_aus: "Image enhancement without AI.",
  protokoll: "Log", bereit: "ready", protokoll_leer: "As soon as a run starts, the program tells you here what it is getting done.",
  laeuft: "running …", fertig_in: s => `done in ${s} s`, abgebrochen: "cancelled", fehler_code: c => `didn’t work (code ${c})`,
  abbrechen: "Cancel", pruefbogen_oeffnen: "Open proof sheet", zu_schritt4: "Continue to step 4",
  lauf_fertig: (t, s) => `${t}: done in ${s} s – great!`, lauf_fehler: t => `${t}: didn’t quite work this time – the log says why.`,
  test_ok: "Self-test passed – everything runs smoothly!", test_fehler: "Self-test: a few checks aren’t passing yet – details are in the log.",
  pruefen_titel: "Check & print", pruefen_unter: "Almost there! A look at the proof sheet, then off to print. “Open” starts the matching program on this computer.",
  ausgabe_oeffnen: "Open output folder", nichts_erzeugt: "Your print files will land here",
  nichts_erzeugt_text: "Start your first run in step 3 – then you will find the proof sheet and print files here.",
  zu_schritt3: "Go to step 3: Generate", letzter_lauf: "Last run", karten: "Cards",
  ausgewaehlte: "Selected cards", format: "Format", bildverbesserung: "Image enhancement", keine_hinweise: "No notes – all good!",
  oeffnen: "Open", im_browser: "View in browser", einzelbilder: "Single images",
  einzelbilder_text: n => `${n} PNG files, one per card side – for print shops with image upload`, ordner_oeffnen: "Open folder",
  vorlagen: "Blank templates",
  wird_geoeffnet: "Opening …",
  werkzeuge_titel: "Tools", werkzeuge_unter: "Everything that makes your work easier: optional tools, self-test, backup and folders.", erledigt: "Done ✓",
  hilfe_titel: "Help", hilfe_unter: "The whole way step by step – plus all the technical details for the curious.",
  tab_leitfaden: "Guide", tab_spec: "Specification (German)", tab_ueber: "About this program",
  u_generator: "Generator", u_oberflaeche: "Interface", u_python: "Python", u_projekt: "Project folder", u_schrift: "Font",
  u_ki: "Image enhancement", u_vorschau: "Preview", u_vorschau_ok: "complete", u_vorschau_nein: "front only – run “pip install pypdfium2” for the back preview",
  u_download: "Download for computers", u_download_text: "Latest version for Windows, macOS and Linux",
  u_letzter: "Last run", u_keiner: "none yet", u_erweitern: "Adding new features",
  u_erweitern_text: "New switches are added in gans_lernkarten.py in baue_parser() and appear in step 3 automatically. A new choice for --nur automatically becomes a start button; new tools are created in gans_ui.py with @werkzeug(…).",
  fuss_version: v => `Version ${v}`, fuss_ki: m => `AI: ${m}`, fuss_vorschau_ok: "Preview ready", fuss_vorschau_nein: "Preview limited",
  beendet: "Me Goos-ta Deutsch is taking a break. You can close this window – see you next time!",
  keine_verbindung: "No connection to the interface right now", fehler_status: s => `Something didn’t work (${s})`,
  nav_tabelle: "Table", nav_verbesserung: "Image enhancement",
  zahl_tabelle_titel: n => `${n} automatically translated ${n === 1 ? "card is" : "cards are"} waiting for your checking eye`,
  tabelle_titel: "Front ↔ back",
  tabelle_unter: "All texts side by side – to compare and check the translation. Click into a cell to change something; it is saved when you leave the field.",
  tabelle_drucken: "Print table", tabelle_filter: "Filter", tabelle_suche: "Search …", tabelle_bilder: "Show images",
  tabelle_fuss: "Tick “checked” once the translation is right – for example after someone who speaks {zs} had a look. Automatically translated words stay marked until they are checked; if a word changes, the tick disappears again.",
  tabelle_nichts: "No card matches the filter and search – try another word.",
  filter_alle: "All", filter_ungeprueft: "Not checked yet", filter_auto: "Translated automatically", filter_ohne: "Without translation", filter_hinweise: "With notes",
  spalte_nr: "No.", spalte_bild: "Image", spalte_de: "Front (German)", spalte_es: "Back ({zs})", spalte_notiz: "Note", spalte_status: "Check",
  es_fehlt_ph: "coming soon", geprueft: "checked",
  marke_auto: "translated automatically – check", marke_auto_titel: "Suggestion from a translation service, not ticked as checked yet (Table tab)",
  marke_geprueft: "translation checked", marke_verbessert: "enhanced", marke_verbessert_titel: "The image is already enhanced with the current settings",
  verbesserung_titel: "Image enhancement",
  verbesserung_unter: "Select one or more cards and have their images enhanced in advance. Finished images are marked green; click an image to see before and after. Generating enhances any missing images anyway.",
  verb_fertig: "images enhanced", verb_methode: "Method", verb_qualitaet: "Quality",
  verb_alle: "Select all", verb_offene: "Select not yet enhanced", verb_keine: "Clear selection",
  verb_start: n => `✦ Enhance selected (${n})`,
  verb_nichts_gewaehlt: "Select cards with the box in the top left corner of the image.",
  verb_schon_alle: "All selected images are already enhanced – great! A new run takes them straight from the cache.",
  verb_schaetzung: (n, d) => `${n} ${n === 1 ? "image is" : "images are"} calculated – estimated ${d}.`,
  verb_hinweis_esrgan: "You can keep working meanwhile; “Cancel” keeps all images already finished.",
  verb_fortschritt: p => `${p} % done`,
  verb_waehlen: "Select", verb_waehlen_bild: b => `Select ${b}`, verb_vergleich: "Compare before and after",
  band_verbessert: "enhanced", band_anders: "other setting", band_offen: "not enhanced yet", band_fehlt: "image missing",
  verb_frueher: m => `enhanced earlier with ${m} – not yet with the current settings`,
  verb_ohne_vergr: "no upscaling (image is large enough)",
  karte_nr: n => `Card ${n}`,
  dauer_s: s => `about ${s} seconds`, dauer_min: m => `about ${m} minutes`,
  vergleich_titel: b => `Before – after: ${b}`, vorher: "Before", nachher: "After", nachher_mit: m => `After (${m})`,
  vergleich_regler: "Move the divider", vergleich_hilfe: "Move the slider or click and drag in the image.",
  vergleich_fehlt: "This image is still waiting for its enhancement. You see how it would be printed now – “Enhance now” makes it even nicer.",
  vergleich_anders: i => `Not yet enhanced with the current settings (${i}). You see the image without enhancement.`,
  jetzt_verbessern: "✦ Enhance now", in_originalgroesse: "After at full size", vorher_originalgroesse: "Before at full size",
  schliessen: "Close ✕", zur_verbesserung: "To image enhancement",
  ki_hinweis_reiter: (f, n) => `${f} of ${n} images are already enhanced → Image enhancement`,
  optional: "(optional)", es_spaeter_ph: "now or in step 2", uebersetzen_titel: "Translate automatically (suggestion)",
  st_problem: "Quick check", st_hinweise: n => `Ready, ${n} ${n === 1 ? "note" : "notes"}`, st_bereit: "Ready",
  st_mit_es: "fully labelled", st_ohne_es: "word follows in step 2", st_auto: "translated automatically – please check",
  uebernehmen_kurz: "Add", details: "Details ▾", details_zu: "Details ▴",
  hochladen_stand: (f, n) => `${f} of ${n} images uploaded and checked …`,
  stapel_zahlen: (n, b, e) => `<b>${n}</b> new ${n === 1 ? "image" : "images"} · <b>${b}</b> ready · <b>${e}</b> already labelled`,
  alle_uebernehmen_n: n => `Add all (${n})`, alle_uebersetzen: "🌐 Translate all",
  stapel_fertig: (n, m, o) => `${n} ${n === 1 ? "card" : "cards"} created${m ? ` – ${m} fully labelled` : ""}${o ? `, ${o} still waiting for the word` : ""}. Brilliant!`,
  stapel_fehler: n => `${n} not added yet – the notes show you what is missing.`,
  karte_fertig: b => `${b}: card finished – nice!`, in_tabelle_pruefen: "Check in the table",
  editor_zahlen: (n, b) => `<b>${n}</b> ${n === 1 ? "card is" : "cards are"} waiting · <b>${b}</b> ready to save`,
  alle_speichern: "Save all", alle_speichern_n: n => `Save all (${n})`, gespeichert_n: n => `${n} ${n === 1 ? "card" : "cards"} saved – great!`,
  zur_tabelle: "To the table",
  vorschlag_von: (d, q) => `${d} suggests for “${q}” – quick check:`,
  chip_titel: "Click to use", kein_vorschlag: q => `The service found nothing for “${q}” – just enter your word yourself, you know it best.`,
  uebersetze_n: (i, n) => `Translating ${i} of ${n} …`, uebersetzt_n: (g, n) => `${g} of ${n} words suggested – one quick look and you’re done.`,
  auto_fehler: m => `Automatic translation is taking a break right now: ${m}`,
  zust_titel: "Switch on automatic translation?",
  zust_1: "For a suggestion, Me Goos-ta Deutsch sends the word to be translated to a translation service on the internet.",
  zust_2: "Only the word or phrase without “Gans” is sent – for example “aufgeregt” – and, for AI images when you click “🌐 To English”, the short description. No images, no file names, no personal data.",
  zust_3: "Default: Wiktionary (free dictionary) for single words, MyMemory for phrases – both without an account. Optionally DeepL with your own key.",
  zust_4: "Suggestions only go into the card list when you accept them, and stay marked as “translated automatically” until you tick them as checked in the table.",
  zust_5: "Only encrypted connections to fixed addresses; answers are filtered (no formulas, no HTML).",
  zust_6: "To switch off or change the service: Tools → Automatic translation.",
  zust_auto: "Translate new cards automatically from now on", zust_ja: "Switch on and translate",
  ue_titel: "Automatic translation", ue_an: "on", ue_aus: "off",
  ue_text: "Suggests the {zs} word while you create cards. Only the word to translate is sent; every suggestion stays marked until you tick it as checked in the table.",
  ue_einschalten: "Allow automatic translation", ue_dienst: "Translation service",
  ue_auto: "Automatic (recommended)", ue_auto_text: "Single words from the Wiktionary dictionary, phrases from DeepL (if a key is stored) or MyMemory.",
  ue_dienst_auto: "automatic", ue_dienst_wiktionary: "Wiktionary", ue_dienst_mymemory: "MyMemory", ue_dienst_deepl: "DeepL",
  ue_deepl: "Your own DeepL API key (optional)", ue_deepl_da: e => `Key stored (${e})`,
  ue_deepl_hilfe: "Free after signing up with DeepL (“DeepL API Free”). The key stays in your user folder, readable only by you, and is sent only to DeepL.",
  ue_deepl_ok: "DeepL key saved", ue_deepl_weg: "DeepL key removed",
  ue_automatisch: "Translate new cards automatically (fill in suggestions right away)",
  ue_cache: "Delete remembered translations", ue_cache_ok: "Remembered translations deleted",
  ue_datenschutz: o => `Settings and remembered translations are stored in ${o} – not in the project folder and not in the project ZIP.`,
  entfernen_kurz: "Remove", speichern: "Save", u_uebersetzung: "Automatic translation", u_kartensprache: "Card language", u_kartensprache_wert: "Spanish (always meaning Spanish as spoken in Mexico)",
  gans_gezeichnet: "Drawn goose (default)", gans_geladen: g => `Own goose image (${g})`, gans_pfad: p => `Image from ${p}`,
  gans_tipp: "Tip: a calm, rather light landscape image, at least 960 × 660 pixels – the word is printed on top in dark blue. The image fills the back and is cropped centrally.",
  gans_laden: "Load goose image …", gans_anderes: "Load another image …", gans_weg: "Use the drawn goose", gans_zurueck: "Previous image",
  gans_ziehen: "You can also drag an image here.",
  gans_hilfe: "Background of all backs. The image is checked, reduced to at most 2400 pixels and saved without metadata as assets/gans_hintergrund; the old one goes to assets/_alt/.",
  gans_ok: "Goose image loaded – looks great! The backs use it from now on.", gans_weg_ok: "Back to the drawn goose", gans_zurueck_ok: "Previous goose image restored",
  datum: "en-GB",
},
es: {
  verbindung: "La conexión se tomó un respiro; no te preocupes, tus cartas están a salvo. Vuelve a iniciar Me Goos-ta Deutsch con el icono del escritorio o con el archivo de inicio de la carpeta del programa.",
  zu_karten: "Me Goos-ta Deutsch – ir al resumen de cartas", sprache: "Idioma de la interfaz", beenden: "Salir",
  beenden_titel: "Cerrar el programa", bereiche: "Secciones",
  nav_karten: "Mis cartas", nav_neu: "Carta nueva", nav_bild: "Preparar imágenes", nav_beschriften: "Rotular cartas",
  nav_drucken: "Imprimir", nav_erzeugen: "Generar", nav_pruefen: "Revisar e imprimir", nav_werkzeuge: "Herramientas", nav_hilfe: "Ayuda",
  schritt1: "Paso 1 de 4", schritt2: "Paso 2 de 4", schritt3: "Paso 3 de 4", schritt4: "Paso 4 de 4",
  karten_titel: "Mis cartas", neue_karte: "+ Carta nueva",
  karten_unter: (g, a) => `${g} ${g === 1 ? "carta está lista" : "cartas están listas"} para imprimir${a ? `, ${a} en pausa` : ""}. Haz clic en una carta y se voltea.`,
  karten_leer_unter: "Tu colección espera su primera carta.",
  karten_leer_titel: "Aquí cabe tu primera carta", karten_leer_text: "Empieza con el paso 1: agrega una imagen con tu juego de palabras «Gans …»; tu primera carta está a unos clics.",
  zu_schritt1: "Ir al paso 1: Preparar imagen",
  banner_offen: n => `${n} ${n === 1 ? "carta solo espera" : "cartas solo esperan"} la palabra en {zs}. ¡Ya casi!`,
  banner_offen_knopf: "Ir al paso 2", hinweise_liste: "Avisos sobre la lista de cartas",
  umdrehen: "Clic para voltear", karte_umdrehen: n => `Voltear la carta ${n}`, bild_fehlt: "Falta la imagen",
  marke_bild_fehlt: "Falta la imagen en la carpeta", marke_es_fehlt: "La palabra viene pronto", marke_aus: "en pausa: no se imprime",
  marke_ppi: (p, b) => `${p} ppi – ${b}`, nr_titel: "Número de carta en la impresión",
  bearbeiten: "Editar", drucken: "Imprimir", drucken_titel: "Imprimir esta carta o dejarla fuera por ahora",
  hoch: "Subir", runter: "Bajar", entfernen: "Quitar de la lista", rueckgaengig: "Deshacer",
  entfernt: b => `${b} se quitó de la lista; la imagen sigue a salvo en la carpeta.`, gespeichert: "Guardado ✓",
  bewertung: { sehr_gut: "muy buena", gut: "buena", ausreichend: "aceptable", gering: "algo justa" },
  bild_titel: "Preparar imágenes",
  bild_unter: "Agrega una imagen o muchas a la vez con tu juego de palabras (p. ej. «Gans alt»). Del resto se encarga el programa: revisa formato, tamaño y nitidez, toma el texto del nombre del archivo y lo nombra como corresponde. La palabra en {zs} la escribes aquí mismo, o deja que 🌐 te la sugiera.",
  ablage_titel: "Arrastra imágenes aquí o haz clic", ablage_unter: "JPG, PNG o WEBP · GIF, BMP y TIFF se convierten · hasta 40 MB",
  ablage_loslassen: "Suelta las imágenes", ablage_loslassen_unter: "Cada imagen se revisa y se prepara con cuidado.",
  nicht_hinzugefuegt: n => `Todavía no entró: ${n}`,
  zu_gross: (n, mb) => `${n} pesa más de ${mb} MB; un poco más pequeña y seguro que entra.`,
  original: "Original", vorderseite: "Anverso", schnellvorschau: "Vista rápida",
  drehen_links: "Girar 90° a la izquierda", drehen_rechts: "Girar 90° a la derecha",
  text_auf_bild: "Texto de la imagen", text_auf_bild_ph: "p. ej. Gans alt",
  ausschnitt: "Encuadre", fit_contain: "Mostrar imagen completa", fit_cover: "Llenar la carta", empfohlen: "recomendado", empfohlen_bild: "recomendado para esta imagen",
  ersetzen: "reemplazar la imagen existente", uebernehmen: "Agregar y continuar →", verwerfen: "Descartar",
  alle_uebernehmen: "Agregar todas", uebernommen: n => `${n} agregada`, jetzt_beschriften: "Rotular ahora →",
  ki_vorschau: m => `Esta es la vista previa rápida; al generar, ${m} le da a tu imagen un buen pulido.`,
  beschriften_titel: "Rotular cartas",
  beschriften_unter: "Escribe la palabra en {zs}; va en el reverso. 🌐 con gusto te sugiere una traducción. Con «/» separas alternativas (p. ej. «viejo / anciano») y con «|» pones un salto de línea.",
  de_feld: "Texto de la imagen (alemán)", es_feld: "Palabra en {zs}", es_ph: "palabra principal / alternativa",
  notiz_feld: "Nota (no se imprime)", notiz_ph: "p. ej. adjetivo", sonderzeichen: "Caracteres especiales:",
  rueckseite: "Reverso", karte_speichern: "Guardar carta", spaeter: "Después", bild_entfernen: "Quitar imagen",
  bild_aendern: "Cambiar imagen …", bild_hinzufuegen: "Agregar imagen …", ersatz_titel: "Imagen nueva para esta carta",
  ersatz_neu: "Imagen nueva", ersatz_uebernehmen: "Usar la imagen nueva", ersatz_ok: "¡Imagen nueva lista! Se ve genial.",
  ersatz_zurueck_ok: "La imagen anterior está de vuelta.", ja_starten: "Sí, empezar",
  karte_gespeichert: "Carta guardada. ¡Genial!", neu_ohne_zeile: "nueva: aún no está en la lista",
  alles_beschriftet: "¡Todas las cartas están rotuladas, excelente!", alles_beschriftet_text: "Sigue con los archivos de impresión, o prepara otra imagen ahora mismo.",
  noch_ein_bild: "Preparar otra imagen", weiter_erzeugen: "Continuar al paso 3: Generar",
  erzeugen_titel: "Generar",
  befehl: "Comando equivalente", kopieren: "Copiar", kopiert: "Comando copiado", kopieren_fehler: "No se pudo copiar; selecciona el texto tú mismo",
  alles_standard: "Restablecer todos los ajustes", standard_ok: "Todos los ajustes volvieron a los valores predeterminados",
  bitte_pruefen: "Revisa rápido: ", auswahl_ph: "todas las cartas", auswahl_tipp: "Útil para imprimir solo las cartas nuevas.",
  an: "Sí", aus: "No", standard: "Predeterminado", leer: "vacío",
  ki_hinweis_esrgan: m => `Mejora de imagen con ${m}: la primera vez de 1 a 4 minutos por imagen, ¡tiempo para un café! Después sale al instante de la memoria intermedia. El progreso lo ves en el registro.`,
  ki_hinweis_fsrcnn: "Mejora de imagen con FSRCNN (rápido). Queda aún más bonita con el modelo Real-ESRGAN; descárgalo en Herramientas.",
  ki_hinweis_aus: "Mejora de imagen sin IA.",
  protokoll: "Registro", bereit: "listo", protokoll_leer: "En cuanto empiece una ejecución, aquí el programa te cuenta lo que va logrando.",
  laeuft: "en curso …", fertig_in: s => `listo en ${s} s`, abgebrochen: "cancelado", fehler_code: c => `no funcionó (código ${c})`,
  abbrechen: "Cancelar", pruefbogen_oeffnen: "Abrir hoja de control", zu_schritt4: "Continuar al paso 4",
  lauf_fertig: (t, s) => `${t}: listo en ${s} s. ¡Súper!`, lauf_fehler: t => `${t}: esta vez no salió del todo; el registro dice por qué.`,
  test_ok: "Autoprueba superada: ¡todo funciona de maravilla!", test_fehler: "Autoprueba: algunas revisiones todavía no pasan; los detalles están en el registro.",
  pruefen_titel: "Revisar e imprimir", pruefen_unter: "¡Ya casi! Échale un vistazo a la hoja de control y luego a imprimir. «Abrir» inicia el programa adecuado en esta computadora.",
  ausgabe_oeffnen: "Abrir carpeta de salida", nichts_erzeugt: "Aquí llegarán tus archivos de impresión",
  nichts_erzeugt_text: "Inicia tu primera ejecución en el paso 3; después encontrarás aquí la hoja de control y los archivos de impresión.",
  zu_schritt3: "Ir al paso 3: Generar", letzter_lauf: "Última ejecución", karten: "Cartas",
  ausgewaehlte: "Cartas seleccionadas", format: "Formato", bildverbesserung: "Mejora de imagen", keine_hinweise: "Sin avisos: ¡todo perfecto!",
  oeffnen: "Abrir", im_browser: "Ver en el navegador", einzelbilder: "Imágenes individuales",
  einzelbilder_text: n => `${n} archivos PNG, uno por lado de carta, para imprentas que reciben imágenes`, ordner_oeffnen: "Abrir carpeta",
  vorlagen: "Plantillas vacías",
  wird_geoeffnet: "Abriendo …",
  werkzeuge_titel: "Herramientas", werkzeuge_unter: "Todo lo que te facilita el trabajo: herramientas opcionales, autoprueba, respaldo y carpetas.", erledigt: "Listo ✓",
  hilfe_titel: "Ayuda", hilfe_unter: "Todo el camino paso a paso, y los datos técnicos para los curiosos.",
  tab_leitfaden: "Guía", tab_spec: "Especificación (alemán)", tab_ueber: "Acerca del programa",
  u_generator: "Generador", u_oberflaeche: "Interfaz", u_python: "Python", u_projekt: "Carpeta del proyecto", u_schrift: "Fuente",
  u_ki: "Mejora de imagen", u_vorschau: "Vista previa", u_vorschau_ok: "completa", u_vorschau_nein: "solo anverso; ejecuta «pip install pypdfium2» para ver el reverso",
  u_download: "Descarga para la computadora", u_download_text: "Versión más reciente para Windows, macOS y Linux",
  u_letzter: "Última ejecución", u_keiner: "ninguna", u_erweitern: "Agregar funciones",
  u_erweitern_text: "Los interruptores nuevos se agregan en gans_lernkarten.py en baue_parser() y aparecen solos en el paso 3. Una opción nueva en --nur se convierte en un botón; las herramientas nuevas se crean en gans_ui.py con @werkzeug(…).",
  fuss_version: v => `Versión ${v}`, fuss_ki: m => `IA: ${m}`, fuss_vorschau_ok: "Vista previa lista", fuss_vorschau_nein: "Vista previa limitada",
  beendet: "Me Goos-ta Deutsch se toma un descanso. Ya puedes cerrar esta ventana. ¡Hasta la próxima!",
  keine_verbindung: "Por ahora no hay conexión con la interfaz", fehler_status: s => `Algo no funcionó (${s})`,
  nav_tabelle: "Tabla", nav_verbesserung: "Mejora de imagen",
  zahl_tabelle_titel: n => `${n} ${n === 1 ? "carta traducida automáticamente espera" : "cartas traducidas automáticamente esperan"} tu revisión`,
  tabelle_titel: "Anverso ↔ reverso",
  tabelle_unter: "Todos los textos lado a lado, para comparar y revisar la traducción. Para cambiar algo, haz clic en una celda; se guarda al salir del campo.",
  tabelle_drucken: "Imprimir tabla", tabelle_filter: "Filtro", tabelle_suche: "Buscar …", tabelle_bilder: "Mostrar imágenes",
  tabelle_fuss: "Marca «revisada» cuando la traducción sea correcta, por ejemplo después de que alguien que habla {zs} la vea. Las palabras traducidas automáticamente quedan marcadas hasta revisarlas; si una palabra cambia, la marca desaparece.",
  tabelle_nichts: "Ninguna carta coincide con el filtro y la búsqueda; prueba con otra palabra.",
  filter_alle: "Todas", filter_ungeprueft: "Sin revisar", filter_auto: "Traducidas automáticamente", filter_ohne: "Sin traducción", filter_hinweise: "Con avisos",
  spalte_nr: "N.º", spalte_bild: "Imagen", spalte_de: "Anverso (alemán)", spalte_es: "Reverso ({zs})", spalte_notiz: "Nota", spalte_status: "Revisión",
  es_fehlt_ph: "viene pronto", geprueft: "revisada",
  marke_auto: "traducida automáticamente: revisar", marke_auto_titel: "Sugerencia de un servicio de traducción, aún sin marcar como revisada (pestaña «Tabla»)",
  marke_geprueft: "traducción revisada", marke_verbessert: "mejorada", marke_verbessert_titel: "La imagen ya está mejorada con los ajustes actuales",
  verbesserung_titel: "Mejora de imagen",
  verbesserung_unter: "Elige una o varias cartas y mejora sus imágenes por adelantado. Las imágenes listas se marcan en verde; con un clic en una imagen ves el antes y el después. Al generar, las imágenes que falten se mejoran de todos modos.",
  verb_fertig: "imágenes mejoradas", verb_methode: "Método", verb_qualitaet: "Calidad",
  verb_alle: "Elegir todas", verb_offene: "Elegir las no mejoradas", verb_keine: "Quitar selección",
  verb_start: n => `✦ Mejorar seleccionadas (${n})`,
  verb_nichts_gewaehlt: "Elige cartas con la casilla de arriba a la izquierda de la imagen.",
  verb_schon_alle: "Todas las imágenes elegidas ya están mejoradas. ¡Muy bien! Una nueva ejecución las toma directo de la memoria intermedia.",
  verb_schaetzung: (n, d) => `${n === 1 ? "Se calcula 1 imagen" : `Se calculan ${n} imágenes`}; tiempo estimado: ${d}.`,
  verb_hinweis_esrgan: "Mientras tanto puedes seguir trabajando; si cancelas, se conservan las imágenes ya listas.",
  verb_fortschritt: p => `${p} % listo`,
  verb_waehlen: "Elegir", verb_waehlen_bild: b => `Elegir ${b}`, verb_vergleich: "Comparar antes y después",
  band_verbessert: "mejorada", band_anders: "otro ajuste", band_offen: "sin mejorar", band_fehlt: "falta la imagen",
  verb_frueher: m => `mejorada antes con ${m}; con los ajustes actuales todavía no`,
  verb_ohne_vergr: "sin ampliación (la imagen es suficientemente grande)",
  karte_nr: n => `Carta ${n}`,
  dauer_s: s => `unos ${s} segundos`, dauer_min: m => `unos ${m} minutos`,
  vergleich_titel: b => `Antes – después: ${b}`, vorher: "Antes", nachher: "Después", nachher_mit: m => `Después (${m})`,
  vergleich_regler: "Mover la línea divisoria", vergleich_hilfe: "Mueve el control deslizante o haz clic y arrastra en la imagen.",
  vergleich_fehlt: "Esta imagen todavía espera su mejora. Se ve cómo se imprimiría ahora; «Mejorar ahora» la deja aún más bonita.",
  vergleich_anders: i => `Aún no mejorada con los ajustes actuales (${i}). Se ve la imagen sin mejora.`,
  jetzt_verbessern: "✦ Mejorar ahora", in_originalgroesse: "Después en tamaño original", vorher_originalgroesse: "Antes en tamaño original",
  schliessen: "Cerrar ✕", zur_verbesserung: "Ir a mejora de imagen",
  ki_hinweis_reiter: (f, n) => `${f} de ${n} imágenes ya están mejoradas → Mejora de imagen`,
  optional: "(opcional)", es_spaeter_ph: "ahora o en el paso 2", uebersetzen_titel: "Traducir automáticamente (sugerencia)",
  st_problem: "Revisa rápido", st_hinweise: n => `Lista, ${n} ${n === 1 ? "aviso" : "avisos"}`, st_bereit: "Lista",
  st_mit_es: "rotulada", st_ohne_es: "la palabra va en el paso 2", st_auto: "traducida automáticamente; revísala",
  uebernehmen_kurz: "Agregar", details: "Detalles ▾", details_zu: "Detalles ▴",
  hochladen_stand: (f, n) => `${f} de ${n} imágenes subidas y revisadas …`,
  stapel_zahlen: (n, b, e) => `<b>${n}</b> ${n === 1 ? "imagen nueva" : "imágenes nuevas"} · <b>${b}</b> listas · <b>${e}</b> ya rotuladas`,
  alle_uebernehmen_n: n => `Agregar todas (${n})`, alle_uebersetzen: "🌐 Traducir todas",
  stapel_fertig: (n, m, o) => `${n} ${n === 1 ? "carta creada" : "cartas creadas"}${m ? `; ${m} ya ${m === 1 ? "rotulada" : "rotuladas"}` : ""}${o ? `, ${o} todavía ${o === 1 ? "espera" : "esperan"} la palabra` : ""}. ¡Excelente!`,
  stapel_fehler: n => `${n} todavía no se agregaron; los avisos te muestran qué falta.`,
  karte_fertig: b => `${b}: carta lista. ¡Genial!`, in_tabelle_pruefen: "Revisar en la tabla",
  editor_zahlen: (n, b) => `<b>${n}</b> ${n === 1 ? "carta espera" : "cartas esperan"} · <b>${b}</b> listas para guardar`,
  alle_speichern: "Guardar todas", alle_speichern_n: n => `Guardar todas (${n})`, gespeichert_n: n => `${n} ${n === 1 ? "carta guardada" : "cartas guardadas"}. ¡Súper!`,
  zur_tabelle: "Ir a la tabla",
  vorschlag_von: (d, q) => `${d} sugiere para «${q}»; revísala rápido:`,
  chip_titel: "Clic para usar", kein_vorschlag: q => `El servicio no encontró nada para «${q}»; escribe tu palabra, ¡tú la conoces mejor!`,
  uebersetze_n: (i, n) => `Traduciendo ${i} de ${n} …`, uebersetzt_n: (g, n) => `${g} de ${n} palabras sugeridas; un vistazo rápido y listo.`,
  auto_fehler: m => `La traducción automática está en pausa por ahora: ${m}`,
  zust_titel: "¿Activar la traducción automática?",
  zust_1: "Para una sugerencia, Me Goos-ta Deutsch envía la palabra a traducir a un servicio de traducción en internet.",
  zust_2: "Solo se envía la palabra o frase sin «Gans», por ejemplo «aufgeregt», y en la imagen IA, al hacer clic en «🌐 Al inglés», la descripción corta. Ni imágenes, ni nombres de archivo, ni datos personales.",
  zust_3: "Predeterminado: Wiktionary (diccionario libre) para palabras sueltas y MyMemory para frases, ambos sin cuenta. Opcional: DeepL con tu propia clave.",
  zust_4: "Las sugerencias solo entran en la lista si las aceptas, y quedan marcadas como «traducida automáticamente» hasta que las marques como revisadas en la tabla.",
  zust_5: "Solo conexiones cifradas a direcciones fijas; las respuestas se filtran (sin fórmulas ni HTML).",
  zust_6: "Para desactivarla o cambiar de servicio: Herramientas → Traducción automática.",
  zust_auto: "Traducir automáticamente las cartas nuevas a partir de ahora", zust_ja: "Activar y traducir",
  ue_titel: "Traducción automática", ue_an: "activada", ue_aus: "desactivada",
  ue_text: "Sugiere la palabra en {zs} al crear las cartas. Solo se envía la palabra a traducir; cada sugerencia queda marcada hasta que la marques como revisada en la tabla.",
  ue_einschalten: "Permitir la traducción automática", ue_dienst: "Servicio de traducción",
  ue_auto: "Automático (recomendado)", ue_auto_text: "Palabras sueltas del diccionario Wiktionary; frases de DeepL (si hay una clave) o de MyMemory.",
  ue_dienst_auto: "automático", ue_dienst_wiktionary: "Wiktionary", ue_dienst_mymemory: "MyMemory", ue_dienst_deepl: "DeepL",
  ue_deepl: "Tu propia clave de API de DeepL (opcional)", ue_deepl_da: e => `Clave guardada (${e})`,
  ue_deepl_hilfe: "Gratis al registrarte en DeepL («DeepL API Free»). La clave se queda en tu carpeta de usuario, solo tú puedes leerla y solo se envía a DeepL.",
  ue_deepl_ok: "Clave de DeepL guardada", ue_deepl_weg: "Clave de DeepL eliminada",
  ue_automatisch: "Traducir automáticamente las cartas nuevas (poner las sugerencias de inmediato)",
  ue_cache: "Borrar traducciones guardadas", ue_cache_ok: "Traducciones guardadas borradas",
  ue_datenschutz: o => `Los ajustes y las traducciones guardadas están en ${o}, no en la carpeta del proyecto ni en el ZIP del proyecto.`,
  entfernen_kurz: "Quitar", speichern: "Guardar", u_uebersetzung: "Traducción automática", u_kartensprache: "Idioma de las cartas", u_kartensprache_wert: "español (siempre el español que se habla en México)",
  gans_gezeichnet: "Ganso dibujado (predeterminado)", gans_geladen: g => `Imagen de ganso propia (${g})`, gans_pfad: p => `Imagen de ${p}`,
  gans_tipp: "Consejo: una imagen tranquila, más bien clara y horizontal, de al menos 960 × 660 píxeles; la palabra va encima en azul oscuro. La imagen llena el reverso y se recorta al centro.",
  gans_laden: "Cargar imagen de ganso …", gans_anderes: "Cargar otra imagen …", gans_weg: "Usar el ganso dibujado", gans_zurueck: "Imagen anterior",
  gans_ziehen: "También puedes arrastrar una imagen aquí.",
  gans_hilfe: "Fondo de todos los reversos. La imagen se revisa, se reduce a un máximo de 2400 píxeles y se guarda sin metadatos como assets/gans_hintergrund; la anterior va a assets/_alt/.",
  gans_ok: "Imagen de ganso cargada. ¡Se ve genial! Los reversos la usan desde ahora.", gans_weg_ok: "De vuelta al ganso dibujado", gans_zurueck_ok: "Imagen de ganso anterior restaurada",
  datum: "es-MX",
},
};

/* ===================== Texte der Erweiterungen (Lade-Ente, Tabelle kompakt, …) ===================== */
// Eigener Block, damit die wörtliche Texttabelle oben unverändert bleibt.
Object.assign(TXT.de, {
  laedt: "Lädt …",
  hilfe_laedt: "Die Gans blättert die Seiten auf …", hilfe_abbrechen: "Abbrechen",
  anfrage_abgebrochen: "Kein Problem – das Laden wurde abgebrochen. Die Gans wartet gern auf den nächsten Versuch.",
  anfrage_zeit: "Das dauert gerade länger als gedacht – die Gans hat nach 20 Sekunden aufgehört zu warten.",
  hilfe_nochmal: "Nochmal versuchen",
  tab_ansicht: "Ansicht der Tabelle", tab_ansicht_bearbeiten: "Bearbeiten", tab_ansicht_kompakt: "Kompakt",
  k_status_ok: "✓ geprüft", k_status_auto: "automatisch – prüfen", k_status_offen: "☐ prüfen", k_status_ohne: "– kein Wort",
  k_aus: "(wird nicht gedruckt)", k_titel: "Klicken zum Bearbeiten",
  zurueck_knopf: "Rückgängig", abbrechen_knopf: "Abbrechen",
  idee_ohne_text: "Idee ohne Text", ie_entscheid: "Behalten oder ersetzen", ie_behalten_kurz: "Behalten", ie_ersetzen_kurz: "Ersetzen",
  ie_dazu_kurz: "Zusätzlich", ie_behalten_titel: "Das Vorhandene bleibt, dieser Eintrag wird nicht importiert.",
  ie_ersetzen_titel: "Der Import ersetzt das Vorhandene (alte Bilder werden aufgehoben, nicht gelöscht).",
  ie_dazu_titel: "Das Wort gibt es schon als Karte – die Idee kommt trotzdem dazu.",
  ie_waehlen_titel: "ZIP-Datei aus „Exportieren“ oder eine karten.csv / ideen.json",
  ie_warnung_titel: n => `${n} ${n === 1 ? "Eintrag gibt" : "Einträge gibt"} es schon`,
  ie_warnung_text: "Entscheide je Zeile: Behalten (Vorhandenes bleibt) oder Ersetzen (Import gewinnt). Nichts geht verloren – ersetzte Bilder werden aufgehoben.",
  ie_alle_behalten: "Alle behalten", ie_alle_ersetzen: "Alle ersetzen", ie_karten: "Karten", ie_ideen: "Ideen", ie_was: "Was exportieren?",
  ie_nur_karten: n => `Karten (${n})`, ie_nur_ideen: n => `Ideen (${n})`, ie_alles: "Alles – Komplettsicherung",
  ie_alles_text: "Karten und Ideen in einer Datei: perfekt zum Sichern oder für den Umzug auf einen anderen Rechner.",
  ie_aktiv_titel: "Ausgeschaltete Karten (Schalter „Drucken“ aus) bleiben dann draußen.", ie_ideen_titel: "Ideen sichern, weitergeben oder einlesen",
  doppelt_titel: "Aufgepasst – das Wort kennst du schon:", doppelt_karte: (nr, de, es) => `Karte ${nr}: ${de}${es ? " → " + es : ""}`,
  doppelt_idee: x => `Idee: ${x}`, idee_de_titel: "So steht es auf dem Bild, z. B. „Gans alt“",
  idee_nach_de_titel: "Aus dem Wort auf {zs} übersetzen (Vorschlag für den Text auf dem Bild)",
  idee_es_zuerst: "Trag zuerst das Wort auf {zs} ein – dann zaubere ich den deutschen Text daraus.",
  lan_titel: "Am Handy öffnen", lan_text: "Benutze das Programm auf Handy oder Tablet im selben WLAN – zum Beispiel, um Fotos direkt vom Handy hochzuladen.",
  lan_firewall: "Findet das Handy die Adresse nicht? Beim ersten Mal fragt Windows bzw. macOS, ob Python Verbindungen annehmen darf – bitte erlauben (privates Netzwerk). Handy und Rechner müssen im selben WLAN sein; Gäste-WLANs trennen Geräte oft.",
  lan_warnung_titel: "Nur im eigenen WLAN", lan_warnung: "Die Verbindung ist im Heimnetz unverschlüsselt. Schalte den Zugang nur zu Hause ein; er geht nach 2 Stunden, nach 5 falschen PINs und beim Beenden von selbst aus.",
  lan_an: "Handy-Zugang einschalten", lan_aus: "Ausschalten", lan_kein_netz: "Kein Heimnetz gefunden – ist der Rechner mit dem WLAN verbunden?",
  lan_schritt1: "1. Mit der Handy-Kamera scannen – oder die Adresse im Browser eingeben:", lan_schritt2: "2. Diese PIN eintippen:", lan_minuten: m => `Noch ${m} Minuten an.`,
  lan_qr: "QR-Code mit der Adresse für das Handy",
  wk_titel: "Willkommen bei Me Goos-ta Deutsch!", wk_untertitel: "Die Ente hat schon mal das Wasser vorgewärmt",
  wk_text: "Hier entstehen Lernkarten mit Wortwitz: vorne ein Bild wie „Gans alt“, hinten das Wort auf {zs}. Drei kurze Fragen, dann geht’s los.",
  wk_sprache: "In welcher Sprache möchtest du das Programm benutzen?", wk_weiter: "Weiter", wk_zurueck: "Zurück", wk_los: "Los geht’s!",
  wk_tour_titel: "So einfach geht’s", wk_hilfe: "Fragen? Unter „Hilfe“ steht alles – und überall verraten dir kleine Hinweise beim Draufzeigen mehr.",
  wk_tour_1_t: "1 · Bilder vorbereiten", wk_tour_1: "Gänse-Bilder hineinziehen – oder mit „🎨 GANS-Bild gestalten“ selbst eins bauen.",
  wk_tour_2_t: "2 · Karten beschriften", wk_tour_2: "Das Wort auf {zs} eintragen; 🌐 schlägt eine Übersetzung vor.",
  wk_tour_3_t: "3 · Erzeugen", wk_tour_3: "Zum Drucken (zuhause oder in der Druckerei) – oder digital für Anki und Handy.",
  wk_tour_4_t: "Ideen sammeln", wk_tour_4: "Halbe Ideen im Reiter „Ideen“ parken und später fertig machen.",
  wk_fertig_toast: "Alles eingerichtet – viel Spaß beim Lernen!",
  nav_deinstallieren: "Deinstallieren", nav_deinstallieren_titel: "Programm sauber entfernen – vorher sichern",
  dei_titel: "Deinstallieren", dei_unter: "Schade, dass du gehst – aber alles in Ruhe: Erst sichern, dann sauber entfernen. Deine Karten kannst du jederzeit wieder einlesen.",
  dei_s1_titel: "Karten und Ideen sichern", dei_s1_text: (k, i) => `Eine Datei mit allen ${k} Karten, ${i} Ideen und ihren Bildern. Nach einer neuen Installation – auch auf einem anderen Gerät – liest „⇅ Import / Export → Importieren“ alles wieder ein.`,
  dei_sichern_knopf: "Komplettsicherung herunterladen", dei_sichern_titel: "Speichert Karten und Ideen als ZIP-Datei in deinen Downloads",
  dei_s1_hinweis: "Tipp: Leg die Datei an einen sicheren Ort, z. B. in einen Cloud-Ordner.", dei_gesichert: "Sicherung heruntergeladen – sehr vorbildlich!",
  dei_s2_titel: "Programm entfernen", dei_s2_nicht: "Nicht betroffen: deine Sicherung, Dateien außerhalb des Programmordners und andere Programme.",
  dei_knopf: "Deinstallieren …", dei_knopf_titel: "Öffnet eine Rückfrage – vorher passiert nichts",
  dei_neu: "Neu installieren geht jederzeit: Download entpacken, Startdatei doppelklicken, Sicherung importieren – fertig.",
  de_sicher: "Bist du sicher?", de_keine_sicherung: "Du hast in dieser Sitzung noch keine Sicherung heruntergeladen.", de_doch_nicht: "Nein, doch behalten",
  erzeugen_unter: "In drei kleinen Schritten zu deinen Karten – deine Einstellungen merkt sich das Programm.",
  ez_s1: "Was möchtest du erstellen?", ez_s2: "Feinschliff", ez_s2_unter: "(optional – die Voreinstellungen passen meistens)",
  ez_weitere: "Weitere Einstellungen", ez_weitere_titel: "Einstellungen, die für dein gewähltes Ziel keine Rolle spielen",
  ez_standard_titel: "Setzt alle Einstellungen dieses Reiters auf die Voreinstellung zurück", ez_s3: "Los geht’s!",
  ez_befehl: "Für Profis: Befehlszeile", ez_los: l => `${l} erzeugen`, ez_nichts_einstellen: "Hier gibt es nichts einzustellen – einfach loslegen.",
  ziel_text_alles: "Druckerei-PDF, Heimdruck, Prüfbogen und Vorlagen in einem Rutsch",
  ziel_titel_alles: "Erzeugt alle Druckdateien auf einmal – praktisch, wenn du noch nicht weißt, wie du drucken willst.",
  ziel_text_druckerei: "Eine Seite je Kartenseite – zum Hochladen bei einer Druckerei",
  ziel_titel_druckerei: "PDF mit Beschnitt und Schnittkante (TrimBox); dazu einzelne PNG-Bilder für Druckereien mit Bild-Upload.",
  ziel_text_bogen: "Mehrere Karten pro Blatt – für deinen eigenen Drucker",
  ziel_titel_bogen: "Vorderseiten und gespiegelte Rückseiten auf A4 oder Letter, mit Schnittmarken. Beidseitig drucken, an der langen Kante wenden.",
  ziel_text_pruefbogen: "Übersicht zum Kontrollieren vor dem Druck",
  ziel_titel_pruefbogen: "Jede Karte mit Vorder- und Rückseite, Texten und Bildschärfe – zum Abhaken oder Weitergeben ans Korrekturlesen.",
  ziel_text_digital: "Für Anki, Handy und Browser – Lernen ohne Papier",
  ziel_titel_digital: "Anki-Paket (auch AnkiDroid/AnkiMobile), Lernseite (offline im Browser) und Bildschirm-PDF; auf Wunsch Tabellen für Quizlet & Co.",
  ziel_text_vorlagen: "Leere Hilfslinien für eigene Gestaltung",
  ziel_titel_vorlagen: "Zeigen Beschnitt, Endformat, Rand und sicheren Bereich – nützlich, wenn du Karten in einem anderen Programm gestaltest.",
  oeffnen_titel: "Mit dem passenden Programm deines Rechners öffnen", im_browser_titel: "In einem neuen Browser-Reiter ansehen",
  speichern_unter: "Herunterladen", speichern_titel: "Datei speichern, z. B. um sie aufs Handy zu schicken",
  pr_s1: "Prüfen", pr_s1_text: "Ein kurzer Blick lohnt sich – dann wird jede Karte ein Treffer.",
  pr_kein_pruefbogen: "Noch kein Prüfbogen da – „Prüfbogen“ oder „Alles zum Drucken“ in Erzeugen zaubert dir einen.",
  pr_check_ueb: n => `${n} ${n === 1 ? "Übersetzung wartet" : "Übersetzungen warten"} noch auf dein „geprüft“`, pr_check_ueb_ok: "Alle Übersetzungen sind geprüft – super!",
  pr_zur_tabelle: "Zur Tabelle", pr_check_ppi: n => `${n} ${n === 1 ? "Bild könnte" : "Bilder könnten"} für den Druck noch etwas schärfer sein`, pr_check_ppi_ok: "Alle Bilder sind schön scharf",
  pr_check_probe: "Probedruck: eine Seite auf normalem Papier, mit 100 % – passt alles, kann’s losgehen",
  pr_s2: "Drucken", pr_zuhause: "Zuhause", pr_druckerei: "Druckerei", pr_noch_nicht: "Noch nicht erzeugt – wähle es in Erzeugen aus.",
  pr_tipps_zuhause: ["Mit 100 % bzw. „Tatsächliche Größe“ drucken – nicht „An Seite anpassen“",
    "Beidseitig, Wenden an der langen Kante. Ohne Duplex: erst Vorderseiten, Stapel wenden, dann Rückseiten",
    "Fester Karton (etwa 200–300 g/m²) macht die Karten schön griffig",
    "Papier A4 oder Letter stellst du in Erzeugen bei „Heimdruck“ ein",
    "Entlang der Schnittmarken schneiden – mit Lineal und Cutter oder einer Schneidemaschine"],
  pr_finden_titel: "So findest du eine passende Druckerei",
  pr_finden_text: "Druckereien für eigene Spiel- oder Lernkarten gibt es in vielen Ländern online. Entscheidend ist: Jede Karte braucht ihre eigene Vorder- und Rückseite.",
  pr_suchbegriffe: "Suchbegriffe:", pr_suchbegriffe_liste: "„Spielkarten individuell drucken“, „eigenes Kartenspiel drucken“, „custom playing cards“",
  pr_achten: "Darauf achten:",
  pr_achten_liste: ["Jede Karte mit eigener Vorder- und Rückseite – nicht nur eine gemeinsame Rückseite",
    "Format: Pokerkarte 63 × 88 mm passt direkt; andere Größen stellst du in Erzeugen unter „Endformat“ ein",
    "Beschnitt: meist 3 mm rundum – ist im Druckerei-PDF schon drin",
    "Verlangt die Vorlage Hochformat? Dann „Druckerei-Datei hochkant“ einschalten",
    "Upload als PDF oder Einzelbilder; Mindestmenge, Kartenstärke und Versand vergleichen",
    "Zuerst ein Probeexemplar bestellen – dann den ganzen Stapel"],
  pr_s3: "Digital lernen", pr_digital_leer: "Lust, auch am Handy oder Rechner zu lernen? Mit einem Klick werden aus deinen Karten Anki-Karten, eine Lernseite und ein Bildschirm-PDF.",
  pr_digital_knopf: "Digitale Lernkarten erzeugen",
  pr_digital_tipps: ["Anki-Paket: in Anki am Rechner öffnen – oder per Mail, Cloud oder Kabel aufs Handy und dort in AnkiDroid (Android) bzw. AnkiMobile (iPhone/iPad) importieren",
    "Lernseite: am Rechner im Browser öffnen, läuft auch offline – dein Lernstand bleibt in diesem Browser gespeichert. Am Handy klappt sie nur eingeschränkt (am iPhone startet sie aus der Dateien-App meist nicht) – dort lieber das Anki-Paket oder das Bildschirm-PDF nehmen",
    "Bildschirm-PDF: in jeder PDF-App durchblättern – Vorderseite, Rückseite, nächste Karte",
    "Für Quizlet, Brainscape, Mochi & Co. in Erzeugen das Format „Tabellen (CSV)“ wählen"],
  pr_vorlagen_text: "Leere Vorlagen mit Hilfslinien – praktisch, wenn du Karten in einem anderen Programm gestaltest.",
  // Import / Export
  ie_knopf: "⇅ Import / Export", ie_titel: "Karten & Ideen importieren / exportieren",
  ie_export_titel: "Exportieren", ie_export_text: "Packt Karten und/oder Ideen samt Bildern in eine ZIP-Datei – zum Sichern, Weitergeben oder für ein neues Gerät.",
  ie_alle: n => `Alle Karten (${n})`, ie_aktiv: n => `Nur Karten, die gedruckt werden (${n})`, ie_export_knopf: "ZIP herunterladen",
  ie_import_titel: "Importieren",
  ie_import_text: "Eine exportierte ZIP-Datei (oder eine Kartenliste als CSV) wählen oder hierher ziehen. Zuerst siehst du eine Vorschau – übernommen wird erst danach.",
  ie_waehlen: "Datei wählen …", ie_pruefe: "Datei wird geprüft …", ie_andere: "Andere Datei wählen",
  ie_vorschau: z => `${z.neu} neu · ${z.konflikt} schon da, aber anders · ${z.gleich} gleich · ${z.fehler} mit Fehler`,
  ie_s_neu: "neu", ie_s_konflikt: "anders", ie_s_gleich: "gleich", ie_s_fehler: "Fehler", ie_hier: "hier:",
  ie_behalten: "Meine behalten", ie_ersetzen: "Durch den Import ersetzen (alte Bilder kommen nach bilder/_entfernt)",
  ie_uebernehmen: n => `${n} ${n === 1 ? "Karte" : "Karten"} übernehmen`, ie_nichts: "Nichts zu übernehmen – alles ist schon da, oder die Einträge brauchen noch etwas Feinschliff.",
  ie_fertig: z => `Import geschafft: ${z.neu + z.ersetzt} Karten (${z.ersetzt} ersetzt) und ${z.ideen_neu + z.ideen_ersetzt} Ideen übernommen${z.uebersprungen ? `, ${z.uebersprungen} behalten` : ""}${z.fehler ? `, ${z.fehler} ausgelassen` : ""}. Stark!`,
  // GANS-Werkzeug
  gw_knopf: "🎨 GANS-Bild gestalten", gw_knopf_unter: "Aus einem Gänse-Foto ein Kartenbild mit „GANS + Wort“ bauen.",
  gw_titel: "GANS-Bild gestalten", gw_leer: "Gänse-Foto wählen oder hierher ziehen", gw_leer_unter: "JPG, PNG oder WEBP – danach zuschneiden und den Text setzen.",
  gw_anderes: "Anderes Foto …", gw_text: "Text nach GANS", gw_text_ph: "z. B. alt, aufgeregt, arg Hunger",
  gw_format: "Ausschnitt", gw_quadrat: "Quadrat", gw_karte: "Karte quer", gw_hoch: "Hochformat",
  gw_zoom: "Zoom", gw_groesse: "Textgröße", gw_schrift: "Schrift", gw_farbe: "Farbe",
  gw_weiss: "Weiß mit Rand", gw_schwarz: "Schwarz mit Rand", gw_gelb: "Gelb mit Rand",
  gw_hilfe: "Bild ziehen = Ausschnitt verschieben · Text ziehen = Text verschieben · Mausrad = Zoom",
  gw_datei: n => `Dateiname: ${n}`, gw_als_karte: "Als neue Karte (Schritt 1)", gw_als_idee: "Als Idee speichern",
  gw_fuer_idee: "Für diese Idee übernehmen", gw_herunterladen: "Herunterladen", gw_text_fehlt: "Noch ein Wort nach GANS – dann ist dein Bild komplett!",
  gw_ok_karte: "Tolles Bild! Es wartet in Schritt 1 – dort kurz prüfen und übernehmen.", gw_ok_idee: "Als Idee gespeichert – gute Idee!",
  gw_s_poppins: "Poppins Bold (wie die Karten)", gw_s_poppins_m: "Poppins Medium", gw_s_impact: "Impact (Meme)",
  gw_s_arial: "Arial Black", gw_s_comic: "Comic Sans", gw_s_georgia: "Georgia (Serifen)", gw_mitte: "Text mittig",
  // KI-Bild (realistische Gans, offline)
  ki_knopf: "🪄 Gans mit KI erzeugen", ki_knopf_unter: "Realistisches Gänse-Foto aus einer kurzen Beschreibung – offline auf diesem Rechner.",
  ki_titel: "Gans mit KI erzeugen", ki_editor_knopf: "🪄 Mit KI …",
  ki_intro: "Sag kurz, wie und wo die Gans zu sehen ist – das Programm malt dir ein realistisches Foto dazu. Dein Wort setzt du danach darauf.",
  ki_wort: "Wort auf der Karte", ki_wort_ph: "z. B. alt, aufgeregt, schön müde",
  ki_wort_hinweis: "Kommt nicht ins Bild – du setzt es danach sauber mit „Wort aufs Bild setzen“ darauf.",
  ki_beschreibung: "Beschreibung auf Englisch: Wie und wo ist die Gans?", ki_beschreibung_ph: "e.g. sleeping in a nest of straw, morning sun",
  ki_uebersetzen: "🌐 Ins Englische", ki_uebersetzt: "Übersetzt – schau kurz drüber, ob es passt.",
  ki_token: n => `${n} von 75 Token – passt`, ki_zu_lang: n => `Achtung: ${n} von 75 Token – das Ende liest das Modell nicht mehr. Lieber etwas kürzer.`,
  ki_ohne_menschen: "Keine Menschen (empfohlen, etwa 20 s länger)",
  ki_erzeugen: "🪄 Gans erzeugen", ki_neu_wuerfeln: "🎲 Neu würfeln",
  ki_hilfe_knopf: "So klappt’s", ki_prompt_knopf: "Standard-Prompt bearbeiten …",
  ki_hilfe_was: "Was schreibe ich?",
  ki_hilfe_was_liste: ["Kurz auf Englisch, was die Gans macht und wo sie ist – z. B. „swimming on a lake at sunset“, „sleeping in a nest of straw“, „standing in fresh snow“.",
    "Gern Licht, Jahreszeit, Wetter oder Stimmung dazu: „morning fog“, „autumn leaves“, „golden hour“.",
    "Lieber sagen, was zu sehen sein soll, statt was nicht – Menschen hält der Schalter „Keine Menschen“ fern.",
    "Kein Englisch zur Hand? Auf Deutsch schreiben und „🌐 Ins Englische“ klicken (nur mit eingeschalteter Übersetzung)."],
  ki_hilfe_gut: "Das kann es gut:",
  ki_hilfe_gut_liste: ["eine Gans in natürlicher Umgebung, nah und scharf", "Licht, Jahreszeit, Wetter und Landschaft",
    "einfache Haltungen: steht, schwimmt, fliegt, schläft, frisst, schaut neugierig"],
  ki_hilfe_schwach: "Da schwächelt es:",
  ki_hilfe_schwach_liste: ["Text und Buchstaben im Bild (darum setzt du dein Wort danach selbst darauf)",
    "genaue Anzahlen und mehrere Tiere, die etwas miteinander tun", "Menschen-Tätigkeiten (Fahrrad fahren, lesen) und Dinge in Schnabel oder Füßen",
    "bestimmte Rassen und dieselbe Gans auf mehreren Karten", "ab und zu ein Bein oder Hals zu viel – dann einfach neu würfeln"],
  ki_hilfe_zeit: "Ein Bild dauert auf einem normalen Laptop etwa 1–2 Minuten. Alles läuft offline auf diesem Rechner; du kannst das Fenster schließen und nebenbei weiterarbeiten. Gleiche Beschreibung + gleicher Startwert = gleiches Bild.",
  ki_prompt_titel: "Standard-Prompt (für Neugierige)",
  ki_prompt_text: "So spricht das Programm mit dem Modell. {description} wird durch deine Beschreibung ersetzt, {word} durch das Wort der Karte (im Standard nicht benutzt – das Modell schreibt keinen sauberen Text). Englisch wirkt am besten.",
  ki_vorlage: "Vorlage", ki_negativ: "Was nicht ins Bild soll (wirkt zusammen mit „Keine Menschen“)",
  ki_prompt_speichern: "Eigene Fassung speichern", ki_prompt_zurueck: "Standard wiederherstellen", ki_prompt_eigene: "eigene Fassung aktiv",
  ki_prompt_gespeichert: "Gespeichert – ab jetzt gilt deine Fassung.", ki_prompt_zurueck_ok: "Der Standard-Prompt ist wieder da.",
  ki_so_gehts: "So geht es ans Modell:", ki_negativ_kurz: "nicht im Bild",
  ki_platzhalter: "Hier erscheint deine Gans", ki_startet: "Die Gans wird vorbereitet …",
  ki_laeuft: p => `Die Gans entsteht … ${p} %`, ki_hintergrund: "Du kannst das Fenster schließen – es rechnet im Hintergrund weiter.",
  ki_startwert: s => `Startwert ${s} – gleiche Beschreibung + gleicher Startwert ergibt dasselbe Bild.`,
  ki_wort_setzen: "✍️ Wort aufs Bild setzen …", ki_als_karte: "Ohne Wort als neue Karte", ki_fuer_karte: "Für diese Karte übernehmen",
  ki_ok_editor: "Das neue Bild steht im Karten-Editor bereit – kurz prüfen und übernehmen.",
  ki_modell_fehlt: "Das KI-Bildmodell fehlt noch (ca. 3,5 GB, einmalig). Danach läuft alles offline.", ki_modell_laden: "Tool „KI-Bilder“ installieren …",
  ki_anderer_lauf: "Gerade läuft noch etwas anderes – deine Gans stellt sich einfach hinten an.",
  ki_beschreibung_fehlt: "Erzähl kurz, wie und wo die Gans zu sehen ist – dann geht’s los!",
  ki_fertig_toast: "Deine KI-Gans ist fertig!", ki_ansehen: "Ansehen", ki_abgebrochen: "Abgebrochen – kein Problem, einfach neu starten.",
  ki_fehler: "Das hat diesmal nicht geklappt – Details stehen im Protokoll.",
  // Ideen
  nav_ideen: "Ideen", ideen_titel: "Ideen für neue Karten",
  ideen_unter: "Eine Idee braucht nur ein Bild, ein Wort auf Deutsch oder auf {zs}. Ergänze sie nach und nach – fertig wird sie mit „Als Karte aufnehmen“ und steht dann unter Meine Karten.",
  idee_neu: "+ Neue Idee", ideen_eigene: "Meine Ideen", ideen_unfertig: "Unfertige Karten aus „Neue Karte“",
  ideen_leer: "Noch keine Ideen? Kein Problem – leg einfach eine an oder gestalte ein GANS-Bild.", ideen_unfertig_leer: "Keine unfertigen Karten – alles erledigt!",
  idee_bild_fehlt: "Noch kein Bild", idee_bild_laden: "Bild wählen …", idee_bild_gestalten: "GANS-Bild gestalten …",
  idee_de: "Text auf dem Bild (Deutsch)", idee_es: "Wort auf {zs}", idee_notiz: "Notiz", idee_de_ph: "z. B. Gans alt", idee_es_ph: "z. B. viejo",
  idee_aufnehmen: "Als Karte aufnehmen", idee_weg: "Verwerfen", idee_fehlt_noch: l => `Fast eine Karte! Es fehlt nur noch: ${l}`,
  idee_teil_bild: "Bild", idee_teil_de: "Text auf dem Bild", idee_teil_es: "Wort auf {zs}",
  idee_aufgenommen: n => `Karte ${n} angelegt – sie steht jetzt unter Meine Karten. Toll!`, idee_verworfen: "Idee verworfen – Platz für neue!",
  idee_ersetzen: "Vorhandenes Bild mit diesem Namen ersetzen",
  unfertig_entwurf: "Bild vorbereitet, noch nicht übernommen", unfertig_offen: "Wort auf {zs} kommt noch", unfertig_ohne: "Bild ohne Zeile in der Kartenliste",
  unfertig_weiter: "Weiter bearbeiten →",
  // Programmstart
  st_titel: "Wie soll sich Me Goos-ta Deutsch öffnen?", st_text: "Gilt ab dem nächsten Start. Ändern kannst du es jederzeit unter Werkzeuge → Programmstart.",
  st_standard: "Im Standard-Browser", st_standard_text: "Wie bisher – der Browser, den dein Rechner sonst nutzt.",
  st_browser: b => `In ${b}`, st_browser_text: "Immer in diesem Browser, auch wenn ein anderer Standard ist.",
  st_fenster: "In einem eigenen Fenster", st_fenster_text: b => `Eigenes Programmfenster ohne Adressleiste und Reiter (über ${b}).`,
  st_fenster_nein: "Dafür braucht es Edge, Chrome, Brave oder Chromium – im Standard-Browser klappt aber alles genauso gut.", st_speichern: "Speichern", st_spaeter: "Später fragen",
  // Deinstallieren
  de_titel: "Programm deinstallieren", de_text: "Damit wird Me Goos-ta Deutsch vollständig von diesem Rechner entfernt:",
  de_p1: "Desktop-Symbol und Startmenü-Eintrag (Mac: App, Linux: Menüeintrag)", de_p2: "das eigene Python, Einstellungen und gemerkte Übersetzungen",
  de_p3: "der Programmordner – mit allen Karten, Bildern, Ideen und Druckdateien", de_warnung: "Das lässt sich nicht rückgängig machen – sichere deine Karten also am besten vorher.",
  de_haken: "Ja, Me Goos-ta Deutsch mit allen Karten und Bildern löschen.",
  de_los: "Endgültig deinstallieren", de_ende: "Me Goos-ta Deutsch wird entfernt. Du kannst dieses Fenster schließen.",
});
Object.assign(TXT.en, {
  laedt: "Loading …",
  hilfe_laedt: "The goose is turning the pages …", hilfe_abbrechen: "Cancel",
  anfrage_abgebrochen: "No problem – loading was cancelled. The goose is happy to try again whenever you are.",
  anfrage_zeit: "This is taking longer than expected – the goose stopped waiting after 20 seconds.",
  hilfe_nochmal: "Try again",
  tab_ansicht: "Table view", tab_ansicht_bearbeiten: "Edit", tab_ansicht_kompakt: "Compact",
  k_status_ok: "✓ checked", k_status_auto: "automatic – check", k_status_offen: "☐ check", k_status_ohne: "– no word",
  k_aus: "(not printed)", k_titel: "Click to edit",
  zurueck_knopf: "Undo", abbrechen_knopf: "Cancel",
  idee_ohne_text: "Idea without text", ie_entscheid: "Keep or replace", ie_behalten_kurz: "Keep", ie_ersetzen_kurz: "Replace",
  ie_dazu_kurz: "Add anyway", ie_behalten_titel: "What you have stays; this entry is not imported.",
  ie_ersetzen_titel: "The import replaces what you have (old images are kept aside, not deleted).",
  ie_dazu_titel: "The word already exists as a card – the idea is added anyway.",
  ie_waehlen_titel: "A ZIP file from “Export” or a karten.csv / ideen.json",
  ie_warnung_titel: n => `${n} ${n === 1 ? "entry already exists" : "entries already exist"}`,
  ie_warnung_text: "Decide per row: Keep (yours stays) or Replace (the import wins). Nothing gets lost – replaced images are kept aside.",
  ie_alle_behalten: "Keep all", ie_alle_ersetzen: "Replace all", ie_karten: "Cards", ie_ideen: "Ideas", ie_was: "What to export?",
  ie_nur_karten: n => `Cards (${n})`, ie_nur_ideen: n => `Ideas (${n})`, ie_alles: "Everything – full backup",
  ie_alles_text: "Cards and ideas in one file: perfect for a backup or for moving to another computer.",
  ie_aktiv_titel: "Cards switched off (“Print” off) are left out.", ie_ideen_titel: "Back up, share or read in ideas",
  doppelt_titel: "Heads-up – you already know this word:", doppelt_karte: (nr, de, es) => `Card ${nr}: ${de}${es ? " → " + es : ""}`,
  doppelt_idee: x => `Idea: ${x}`, idee_de_titel: "Exactly as written on the image, e.g. “Gans alt”",
  idee_nach_de_titel: "Translate from the {zs} word (suggestion for the text on the image)",
  idee_es_zuerst: "Enter the {zs} word first – then I will conjure up the German text.",
  lan_titel: "Open on your phone", lan_text: "Use the program on your phone or tablet in the same Wi-Fi – for example to upload photos straight from your phone.",
  lan_firewall: "Phone can’t reach the address? The first time, Windows or macOS asks whether Python may accept connections – please allow it (private network). Phone and computer must be on the same Wi-Fi; guest networks often keep devices apart.",
  lan_warnung_titel: "Only in your own Wi-Fi", lan_warnung: "The connection inside your home network is not encrypted. Switch access on only at home; it turns itself off after 2 hours, after 5 wrong PINs and when you quit.",
  lan_an: "Switch on phone access", lan_aus: "Switch off", lan_kein_netz: "No home network found – is the computer connected to Wi-Fi?",
  lan_schritt1: "1. Scan with your phone’s camera – or type the address into its browser:", lan_schritt2: "2. Enter this PIN:", lan_minuten: m => `On for another ${m} minutes.`,
  lan_qr: "QR code with the address for your phone",
  wk_titel: "Welcome to Me Goos-ta Deutsch!", wk_untertitel: "The duck has already warmed up the water",
  wk_text: "This is where flashcards with puns come to life: a picture like “Gans alt” on the front, the {zs} word on the back. Three quick questions and off we go.",
  wk_sprache: "Which language would you like to use?", wk_weiter: "Next", wk_zurueck: "Back", wk_los: "Let’s go!",
  wk_tour_titel: "It’s this easy", wk_hilfe: "Questions? “Help” has everything – and little hints pop up wherever you hover.",
  wk_tour_1_t: "1 · Prepare images", wk_tour_1: "Drag in goose pictures – or build one yourself with “🎨 Design a GANS image”.",
  wk_tour_2_t: "2 · Label cards", wk_tour_2: "Enter the {zs} word; 🌐 suggests a translation.",
  wk_tour_3_t: "3 · Generate", wk_tour_3: "For printing (at home or at a print shop) – or digital for Anki and your phone.",
  wk_tour_4_t: "Collect ideas", wk_tour_4: "Park half-baked ideas in the “Ideas” tab and finish them later.",
  wk_fertig_toast: "All set – have fun learning!",
  nav_deinstallieren: "Uninstall", nav_deinstallieren_titel: "Take the program off cleanly – back up first",
  dei_titel: "Uninstall", dei_unter: "Sad to see you go – but no rush: back up first, then uninstall cleanly. You can read your cards back in any time.",
  dei_s1_titel: "Back up cards and ideas", dei_s1_text: (k, i) => `One file with all ${k} cards, ${i} ideas and their images. After a new installation – even on another device – “⇅ Import / export → Import” brings everything back.`,
  dei_sichern_knopf: "Download full backup", dei_sichern_titel: "Saves cards and ideas as a ZIP file in your downloads",
  dei_s1_hinweis: "Tip: keep the file somewhere safe, e.g. in a cloud folder.", dei_gesichert: "Backup downloaded – exemplary!",
  dei_s2_titel: "Uninstall the program", dei_s2_nicht: "Not affected: your backup, files outside the program folder and other programs.",
  dei_knopf: "Uninstall …", dei_knopf_titel: "Opens a confirmation – nothing happens before that",
  dei_neu: "Reinstalling works any time: unzip the download, double-click the start file, import your backup – done.",
  de_sicher: "Are you sure?", de_keine_sicherung: "You have not downloaded a backup in this session yet.", de_doch_nicht: "No, keep it",
  erzeugen_unter: "Three small steps to your cards – the program remembers your settings.",
  ez_s1: "What would you like to create?", ez_s2: "Fine-tuning", ez_s2_unter: "(optional – the defaults usually fit)",
  ez_weitere: "More settings", ez_weitere_titel: "Settings that don’t matter for the goal you picked",
  ez_standard_titel: "Resets all settings of this tab to their defaults", ez_s3: "Let’s go!",
  ez_befehl: "For pros: command line", ez_los: l => `Create ${l}`, ez_nichts_einstellen: "Nothing to set here – just go ahead.",
  ziel_text_alles: "Print-shop PDF, home print, proof sheet and templates in one go",
  ziel_titel_alles: "Creates all print files at once – handy if you haven’t decided how to print yet.",
  ziel_text_druckerei: "One page per card side – for uploading to a print shop",
  ziel_titel_druckerei: "PDF with bleed and trim box; plus single PNG images for print shops that take image uploads.",
  ziel_text_bogen: "Several cards per sheet – for your own printer",
  ziel_titel_bogen: "Fronts and mirrored backs on A4 or Letter, with crop marks. Print double-sided, flip on the long edge.",
  ziel_text_pruefbogen: "An overview to check before printing",
  ziel_titel_pruefbogen: "Every card with front and back, texts and image sharpness – for ticking off or passing on for proofreading.",
  ziel_text_digital: "For Anki, phone and browser – learning without paper",
  ziel_titel_digital: "Anki package (also AnkiDroid/AnkiMobile), study page (offline in the browser) and screen PDF; tables for Quizlet & co. on request.",
  ziel_text_vorlagen: "Blank guide lines for your own design",
  ziel_titel_vorlagen: "Show bleed, final size, border and safe area – useful when you design cards in another program.",
  oeffnen_titel: "Open with the matching program on your computer", im_browser_titel: "View it in a new browser tab",
  speichern_unter: "Download", speichern_titel: "Save the file, e.g. to send it to your phone",
  pr_s1: "Check", pr_s1_text: "A quick look pays off – then every card is a hit.",
  pr_kein_pruefbogen: "No proof sheet yet – “Proof sheet” or “Everything for print” in Generate whips one up for you.",
  pr_check_ueb: n => `${n} ${n === 1 ? "translation is" : "translations are"} still waiting for your “checked”`, pr_check_ueb_ok: "All translations are checked – great!",
  pr_zur_tabelle: "Go to the table", pr_check_ppi: n => `${n} ${n === 1 ? "image could" : "images could"} be a little sharper for print`, pr_check_ppi_ok: "All images are nice and sharp",
  pr_check_probe: "Test print: one page on plain paper at 100 % – if it all fits, off you go",
  pr_s2: "Print", pr_zuhause: "At home", pr_druckerei: "Print shop", pr_noch_nicht: "Not created yet – pick it in Generate.",
  pr_tipps_zuhause: ["Print at 100 % or “Actual size” – not “Fit to page”",
    "Double-sided, flip on the long edge. No duplex? Print the fronts, turn the stack over, then the backs",
    "Sturdy card stock (about 200–300 g/m², 80–110 lb cover) makes the cards nice to hold",
    "Choose A4 or Letter paper in Generate under “Home print”",
    "Cut along the crop marks – with a ruler and craft knife or a paper trimmer"],
  pr_finden_titel: "How to find a suitable print shop",
  pr_finden_text: "Online printers for custom playing or flash cards exist in many countries. What matters: every card needs its own front and back.",
  pr_suchbegriffe: "Search terms:", pr_suchbegriffe_liste: "“custom playing cards”, “print your own card game”, “custom flash cards printing”",
  pr_achten: "Look out for:",
  pr_achten_liste: ["Every card with its own front and back – not just one shared back",
    "Size: a poker card 63 × 88 mm fits directly; set other sizes in Generate under “Final size”",
    "Bleed: usually 3 mm all round – already included in the print-shop PDF",
    "Template asks for portrait? Then switch on “Print-shop file portrait”",
    "Upload as PDF or single images; compare minimum order, card stock and shipping",
    "Order one sample deck first – then the whole stack"],
  pr_s3: "Learn digitally", pr_digital_leer: "Fancy learning on your phone or computer too? One click turns your cards into Anki cards, a study page and a screen PDF.",
  pr_digital_knopf: "Create digital flashcards",
  pr_digital_tipps: ["Anki package: open it in Anki on your computer – or send it to your phone by mail, cloud or cable and import it in AnkiDroid (Android) or AnkiMobile (iPhone/iPad)",
    "Study page: open it in a browser on your computer, works offline too – your progress stays saved in that browser. On phones it only partly works (on the iPhone it usually won’t start from the Files app) – there, better use the Anki package or the screen PDF",
    "Screen PDF: flick through it in any PDF app – front, back, next card",
    "For Quizlet, Brainscape, Mochi & co. pick the format “Tables (CSV)” in Generate"],
  pr_vorlagen_text: "Blank templates with guide lines – handy when you design cards in another program.",
  ie_knopf: "⇅ Import / export", ie_titel: "Import / export cards & ideas",
  ie_export_titel: "Export", ie_export_text: "Packs cards and/or ideas with their images into one ZIP file – for a backup, for sharing or for a new device.",
  ie_alle: n => `All cards (${n})`, ie_aktiv: n => `Only cards that are printed (${n})`, ie_export_knopf: "Download ZIP",
  ie_import_titel: "Import",
  ie_import_text: "Choose or drop an exported ZIP file (or a card list as CSV). You see a preview first – nothing is taken over before that.",
  ie_waehlen: "Choose file …", ie_pruefe: "Checking file …", ie_andere: "Choose another file",
  ie_vorschau: z => `${z.neu} new · ${z.konflikt} already here but different · ${z.gleich} identical · ${z.fehler} with errors`,
  ie_s_neu: "new", ie_s_konflikt: "different", ie_s_gleich: "identical", ie_s_fehler: "error", ie_hier: "here:",
  ie_behalten: "Keep mine", ie_ersetzen: "Replace with the import (old images go to bilder/_entfernt)",
  ie_uebernehmen: n => `Take over ${n} ${n === 1 ? "card" : "cards"}`, ie_nichts: "Nothing to take over – everything is already here, or the entries need a little polish.",
  ie_fertig: z => `Import done: ${z.neu + z.ersetzt} cards (${z.ersetzt} replaced) and ${z.ideen_neu + z.ideen_ersetzt} ideas added${z.uebersprungen ? `, ${z.uebersprungen} kept as they were` : ""}${z.fehler ? `, ${z.fehler} left out` : ""}. Nice one!`,
  gw_knopf: "🎨 Design a GANS image", gw_knopf_unter: "Turn a goose photo into a card image with “GANS + word”.",
  gw_titel: "Design a GANS image", gw_leer: "Choose or drop a goose photo", gw_leer_unter: "JPG, PNG or WEBP – then crop it and add the text.",
  gw_anderes: "Other photo …", gw_text: "Text after GANS", gw_text_ph: "e.g. alt, aufgeregt, arg Hunger",
  gw_format: "Crop", gw_quadrat: "Square", gw_karte: "Card landscape", gw_hoch: "Portrait",
  gw_zoom: "Zoom", gw_groesse: "Text size", gw_schrift: "Font", gw_farbe: "Colour",
  gw_weiss: "White with outline", gw_schwarz: "Black with outline", gw_gelb: "Yellow with outline",
  gw_hilfe: "Drag the image = move the crop · drag the text = move the text · mouse wheel = zoom",
  gw_datei: n => `File name: ${n}`, gw_als_karte: "As a new card (step 1)", gw_als_idee: "Save as idea",
  gw_fuer_idee: "Use for this idea", gw_herunterladen: "Download", gw_text_fehlt: "One more word after GANS – then your image is complete!",
  gw_ok_karte: "Great image! It is waiting in step 1 – check it there and take it over.", gw_ok_idee: "Saved as an idea – good idea!",
  gw_s_poppins: "Poppins Bold (like the cards)", gw_s_poppins_m: "Poppins Medium", gw_s_impact: "Impact (meme)",
  gw_s_arial: "Arial Black", gw_s_comic: "Comic Sans", gw_s_georgia: "Georgia (serif)", gw_mitte: "Centre text",
  // AI image (realistic goose, offline)
  ki_knopf: "🪄 Create a goose with AI", ki_knopf_unter: "A realistic goose photo from a short description – offline on this computer.",
  ki_titel: "Create a goose with AI", ki_editor_knopf: "🪄 With AI …",
  ki_intro: "Say briefly how and where the goose should appear – the program paints a realistic photo for it. You put your word on it afterwards.",
  ki_wort: "Word on the card", ki_wort_ph: "e.g. alt, aufgeregt, schön müde",
  ki_wort_hinweis: "Not painted into the image – you add it neatly afterwards with “Put the word on the image”.",
  ki_beschreibung: "Description in English: how and where is the goose?", ki_beschreibung_ph: "e.g. sleeping in a nest of straw, morning sun",
  ki_uebersetzen: "🌐 To English", ki_uebersetzt: "Translated – take a quick look whether it fits.",
  ki_token: n => `${n} of 75 tokens – fits`, ki_zu_lang: n => `Heads-up: ${n} of 75 tokens – the model won’t read the end. Better a bit shorter.`,
  ki_ohne_menschen: "No people (recommended, about 20 s longer)",
  ki_erzeugen: "🪄 Create goose", ki_neu_wuerfeln: "🎲 Roll again",
  ki_hilfe_knopf: "How it works", ki_prompt_knopf: "Edit default prompt …",
  ki_hilfe_was: "What do I write?",
  ki_hilfe_was_liste: ["Briefly, in English, what the goose is doing and where it is – e.g. “swimming on a lake at sunset”, “sleeping in a nest of straw”, “standing in fresh snow”.",
    "Feel free to add light, season, weather or mood: “morning fog”, “autumn leaves”, “golden hour”.",
    "Say what should be visible rather than what shouldn’t – the “No people” switch keeps people away.",
    "Short and concrete works best – the model understands English best."],
  ki_hilfe_gut: "What it does well:",
  ki_hilfe_gut_liste: ["one goose in a natural setting, close and sharp", "light, season, weather and landscape",
    "simple poses: standing, swimming, flying, sleeping, eating, looking curious"],
  ki_hilfe_schwach: "Where it struggles:",
  ki_hilfe_schwach_liste: ["text and letters in the image (that’s why you add your word yourself afterwards)",
    "exact numbers and several animals doing something together", "human activities (riding a bike, reading) and holding things in beak or feet",
    "specific breeds and the same goose on several cards", "now and then a leg or neck too many – then just roll again"],
  ki_hilfe_zeit: "On a normal laptop one image takes about 1–2 minutes. Everything runs offline on this computer; you can close the window and keep working. Same description + same seed = same image.",
  ki_prompt_titel: "Default prompt (for the curious)",
  ki_prompt_text: "This is how the program talks to the model. {description} is replaced by your description, {word} by the card’s word (not used by default – the model doesn’t write clean text). English works best.",
  ki_vorlage: "Template", ki_negativ: "What should stay out of the image (works together with “No people”)",
  ki_prompt_speichern: "Save my version", ki_prompt_zurueck: "Restore default", ki_prompt_eigene: "your version is active",
  ki_prompt_gespeichert: "Saved – your version applies from now on.", ki_prompt_zurueck_ok: "The default prompt is back.",
  ki_so_gehts: "This is what the model gets:", ki_negativ_kurz: "not in the image",
  ki_platzhalter: "Your goose appears here", ki_startet: "Getting the goose ready …",
  ki_laeuft: p => `The goose is taking shape … ${p} %`, ki_hintergrund: "You can close the window – it keeps working in the background.",
  ki_startwert: s => `Seed ${s} – same description + same seed gives the same image.`,
  ki_wort_setzen: "✍️ Put the word on the image …", ki_als_karte: "As a new card without word", ki_fuer_karte: "Use for this card",
  ki_ok_editor: "The new image is waiting in the card editor – check it quickly and apply.",
  ki_modell_fehlt: "The AI image model is still missing (about 3.5 GB, one time). After that everything runs offline.", ki_modell_laden: "Install the “AI images” tool …",
  ki_anderer_lauf: "Something else is running right now – your goose simply joins the queue.",
  ki_beschreibung_fehlt: "Tell briefly how and where the goose should appear – then off we go!",
  ki_fertig_toast: "Your AI goose is ready!", ki_ansehen: "View", ki_abgebrochen: "Stopped – no problem, just start again.",
  ki_fehler: "That didn’t work this time – details are in the log.",
  nav_ideen: "Ideas", ideen_titel: "Ideas for new cards",
  ideen_unter: "An idea only needs an image, a German or a {zs} word. Complete it bit by bit – “Make it a card” finishes it and it moves to My cards.",
  idee_neu: "+ New idea", ideen_eigene: "My ideas", ideen_unfertig: "Unfinished cards from “New card”",
  ideen_leer: "No ideas yet? No problem – just add one or design a GANS image.", ideen_unfertig_leer: "No unfinished cards – all done!",
  idee_bild_fehlt: "No image yet", idee_bild_laden: "Choose image …", idee_bild_gestalten: "Design GANS image …",
  idee_de: "Text on the image (German)", idee_es: "{zs} word", idee_notiz: "Note", idee_de_ph: "e.g. Gans alt", idee_es_ph: "e.g. viejo",
  idee_aufnehmen: "Make it a card", idee_weg: "Discard", idee_fehlt_noch: l => `Almost a card! All that is missing: ${l}`,
  idee_teil_bild: "image", idee_teil_de: "text on the image", idee_teil_es: "{zs} word",
  idee_aufgenommen: n => `Card ${n} created – it is now under My cards. Awesome!`, idee_verworfen: "Idea discarded – room for new ones!",
  idee_ersetzen: "Replace the existing image with this name",
  unfertig_entwurf: "Image prepared, not taken over yet", unfertig_offen: "{zs} word coming soon", unfertig_ohne: "Image without a row in the card list",
  unfertig_weiter: "Continue →",
  st_titel: "How should Me Goos-ta Deutsch open?", st_text: "Applies from the next start. You can change it any time under Tools → Program start.",
  st_standard: "In the default browser", st_standard_text: "As before – the browser your computer normally uses.",
  st_browser: b => `In ${b}`, st_browser_text: "Always in this browser, even if another one is the default.",
  st_fenster: "In its own window", st_fenster_text: b => `Its own program window without address bar and tabs (via ${b}).`,
  st_fenster_nein: "This needs Edge, Chrome, Brave or Chromium – but everything works just as well in the default browser.", st_speichern: "Save", st_spaeter: "Ask later",
  de_titel: "Uninstall program", de_text: "This removes Me Goos-ta Deutsch completely from this computer:",
  de_p1: "Desktop icon and Start menu entry (Mac: app, Linux: menu entry)", de_p2: "its own Python, settings and remembered translations",
  de_p3: "the program folder – with all cards, images, ideas and print files", de_warnung: "This cannot be undone – so best back up your cards first.",
  de_haken: "Yes, delete Me Goos-ta Deutsch with all cards and images.",
  de_los: "Uninstall for good", de_ende: "Me Goos-ta Deutsch is being removed. You can close this window.",
});
Object.assign(TXT.es, {
  laedt: "Cargando …",
  hilfe_laedt: "La oca está pasando las páginas …", hilfe_abbrechen: "Cancelar",
  anfrage_abgebrochen: "No pasa nada – se canceló la carga. La oca lo intenta de nuevo cuando quieras.",
  anfrage_zeit: "Esto tarda más de lo esperado – la oca dejó de esperar después de 20 segundos.",
  hilfe_nochmal: "Intentar de nuevo",
  tab_ansicht: "Vista de la tabla", tab_ansicht_bearbeiten: "Editar", tab_ansicht_kompakt: "Compacta",
  k_status_ok: "✓ revisada", k_status_auto: "automática – revisar", k_status_offen: "☐ revisar", k_status_ohne: "– sin palabra",
  k_aus: "(no se imprime)", k_titel: "Clic para editar",
  zurueck_knopf: "Deshacer", abbrechen_knopf: "Cancelar",
  idee_ohne_text: "Idea sin texto", ie_entscheid: "Conservar o reemplazar", ie_behalten_kurz: "Conservar", ie_ersetzen_kurz: "Reemplazar",
  ie_dazu_kurz: "Agregar igual", ie_behalten_titel: "Lo que tienes se queda; esta entrada no se importa.",
  ie_ersetzen_titel: "La importación reemplaza lo que tienes (las imágenes viejas se guardan aparte, no se borran).",
  ie_dazu_titel: "La palabra ya existe como carta; la idea se agrega de todos modos.",
  ie_waehlen_titel: "Un ZIP de «Exportar» o un karten.csv / ideen.json",
  ie_warnung_titel: n => `${n} ${n === 1 ? "entrada ya existe" : "entradas ya existen"}`,
  ie_warnung_text: "Decide por fila: Conservar (lo tuyo se queda) o Reemplazar (gana la importación). Nada se pierde: las imágenes reemplazadas se guardan aparte.",
  ie_alle_behalten: "Conservar todo", ie_alle_ersetzen: "Reemplazar todo", ie_karten: "Cartas", ie_ideen: "Ideas", ie_was: "¿Qué exportar?",
  ie_nur_karten: n => `Cartas (${n})`, ie_nur_ideen: n => `Ideas (${n})`, ie_alles: "Todo: copia de seguridad completa",
  ie_alles_text: "Cartas e ideas en un solo archivo: perfecto para respaldar o para mudarte a otra computadora.",
  ie_aktiv_titel: "Las cartas apagadas («Imprimir» desactivado) quedan fuera.", ie_ideen_titel: "Respaldar, compartir o leer ideas",
  doppelt_titel: "Ojo: esta palabra ya la conoces:", doppelt_karte: (nr, de, es) => `Carta ${nr}: ${de}${es ? " → " + es : ""}`,
  doppelt_idee: x => `Idea: ${x}`, idee_de_titel: "Tal como está en la imagen, p. ej. «Gans alt»",
  idee_nach_de_titel: "Traducir desde la palabra en {zs} (sugerencia para el texto de la imagen)",
  idee_es_zuerst: "Primero escribe la palabra en {zs}; luego saco de ahí el texto en alemán.",
  lan_titel: "Abrir en el celular", lan_text: "Usa el programa en el celular o la tableta en el mismo wifi, por ejemplo para subir fotos directo desde el celular.",
  lan_firewall: "¿El celular no encuentra la dirección? La primera vez, Windows o macOS pregunta si Python puede aceptar conexiones: permítelo (red privada). El celular y la computadora deben estar en el mismo wifi; las redes de invitados suelen separar los dispositivos.",
  lan_warnung_titel: "Solo en tu propio wifi", lan_warnung: "Dentro de tu red doméstica la conexión no va cifrada. Actívalo solo en casa; se apaga solo después de 2 horas, tras 5 PIN incorrectos y al cerrar el programa.",
  lan_an: "Activar acceso desde el celular", lan_aus: "Apagar", lan_kein_netz: "No se encontró una red doméstica: ¿la computadora está conectada al wifi?",
  lan_schritt1: "1. Escanea con la cámara del celular, o escribe la dirección en su navegador:", lan_schritt2: "2. Escribe este PIN:", lan_minuten: m => `Activo ${m} minutos más.`,
  lan_qr: "Código QR con la dirección para el celular",
  wk_titel: "¡Bienvenido a Me Goos-ta Deutsch!", wk_untertitel: "El pato ya calentó el agua",
  wk_text: "Aquí nacen tarjetas con juegos de palabras: adelante una imagen como «Gans alt», atrás la palabra en {zs}. Tres preguntas rápidas y empezamos.",
  wk_sprache: "¿En qué idioma quieres usar el programa?", wk_weiter: "Siguiente", wk_zurueck: "Atrás", wk_los: "¡Vamos!",
  wk_tour_titel: "Así de fácil", wk_hilfe: "¿Dudas? En «Ayuda» está todo, y al pasar el ratón aparecen pistas por todas partes.",
  wk_tour_1_t: "1 · Preparar imágenes", wk_tour_1: "Arrastra imágenes de gansos, o crea una con «🎨 Diseñar imagen GANS».",
  wk_tour_2_t: "2 · Rotular cartas", wk_tour_2: "Escribe la palabra en {zs}; 🌐 sugiere una traducción.",
  wk_tour_3_t: "3 · Generar", wk_tour_3: "Para imprimir (en casa o en una imprenta) o en digital para Anki y el celular.",
  wk_tour_4_t: "Juntar ideas", wk_tour_4: "Guarda ideas a medias en la pestaña «Ideas» y termínalas después.",
  wk_fertig_toast: "¡Todo listo! Que disfrutes aprendiendo.",
  nav_deinstallieren: "Desinstalar", nav_deinstallieren_titel: "Quitar el programa limpiamente; antes, respaldar",
  dei_titel: "Desinstalar", dei_unter: "Qué pena que te vayas, pero con calma: primero respalda y luego quita todo limpiamente. Puedes volver a leer tus cartas cuando quieras.",
  dei_s1_titel: "Respaldar cartas e ideas", dei_s1_text: (k, i) => `Un archivo con tus ${k} cartas, ${i} ideas y sus imágenes. Tras una instalación nueva, incluso en otro dispositivo, «⇅ Importar / exportar → Importar» lo recupera todo.`,
  dei_sichern_knopf: "Descargar copia completa", dei_sichern_titel: "Guarda cartas e ideas como ZIP en tus descargas",
  dei_s1_hinweis: "Consejo: guarda el archivo en un lugar seguro, p. ej. una carpeta en la nube.", dei_gesichert: "Copia descargada: ¡ejemplar!",
  dei_s2_titel: "Quitar el programa", dei_s2_nicht: "No se tocan: tu copia de seguridad, los archivos fuera de la carpeta del programa ni otros programas.",
  dei_knopf: "Desinstalar …", dei_knopf_titel: "Abre una confirmación; antes no pasa nada",
  dei_neu: "Reinstalar se puede siempre: descomprime la descarga, doble clic en el archivo de inicio, importa tu copia y listo.",
  de_sicher: "¿Seguro?", de_keine_sicherung: "Aún no descargaste una copia de seguridad en esta sesión.", de_doch_nicht: "No, mejor lo conservo",
  erzeugen_unter: "Tres pasitos hasta tus cartas; el programa recuerda tus ajustes.",
  ez_s1: "¿Qué quieres crear?", ez_s2: "Ajustes finos", ez_s2_unter: "(opcional: lo predeterminado casi siempre sirve)",
  ez_weitere: "Más ajustes", ez_weitere_titel: "Ajustes que no importan para el objetivo elegido",
  ez_standard_titel: "Vuelve todos los ajustes de esta pestaña a lo predeterminado", ez_s3: "¡Vamos!",
  ez_befehl: "Para expertos: línea de comandos", ez_los: l => `Crear ${l}`, ez_nichts_einstellen: "Aquí no hay nada que ajustar: ¡adelante!",
  ziel_text_alles: "PDF de imprenta, impresión en casa, hoja de control y plantillas de una vez",
  ziel_titel_alles: "Crea todos los archivos de impresión a la vez; práctico si aún no sabes cómo vas a imprimir.",
  ziel_text_druckerei: "Una página por lado de carta, para subir a una imprenta",
  ziel_titel_druckerei: "PDF con sangrado y línea de corte; además imágenes PNG sueltas para imprentas que aceptan imágenes.",
  ziel_text_bogen: "Varias cartas por hoja, para tu propia impresora",
  ziel_titel_bogen: "Anversos y reversos espejados en A4 o Carta, con marcas de corte. Imprime a doble cara, volteo por el borde largo.",
  ziel_text_pruefbogen: "Un resumen para revisar antes de imprimir",
  ziel_titel_pruefbogen: "Cada carta con anverso y reverso, textos y nitidez; para marcar o pasarla a quien revise.",
  ziel_text_digital: "Para Anki, el celular y el navegador: aprender sin papel",
  ziel_titel_digital: "Paquete de Anki (también AnkiDroid/AnkiMobile), página de estudio (sin conexión en el navegador) y PDF de pantalla; tablas para Quizlet y más si quieres.",
  ziel_text_vorlagen: "Líneas guía vacías para tu propio diseño",
  ziel_titel_vorlagen: "Muestran sangrado, tamaño final, borde y zona segura; útil si diseñas cartas en otro programa.",
  oeffnen_titel: "Abrir con el programa adecuado de tu computadora", im_browser_titel: "Verlo en una pestaña nueva del navegador",
  speichern_unter: "Descargar", speichern_titel: "Guardar el archivo, p. ej. para enviarlo a tu celular",
  pr_s1: "Revisar", pr_s1_text: "Un vistazo rápido vale la pena: así cada carta es un acierto.",
  pr_kein_pruefbogen: "Aún no hay hoja de control: «Hoja de control» o «Todo para imprimir» en Generar te la prepara.",
  pr_check_ueb: n => `${n} ${n === 1 ? "traducción espera" : "traducciones esperan"} tu «revisada»`, pr_check_ueb_ok: "Todas las traducciones están revisadas: ¡genial!",
  pr_zur_tabelle: "Ir a la tabla", pr_check_ppi: n => `${n} ${n === 1 ? "imagen podría quedar un poco más nítida" : "imágenes podrían quedar un poco más nítidas"} para imprimir`, pr_check_ppi_ok: "Todas las imágenes están bien nítidas",
  pr_check_probe: "Prueba de impresión: una página en papel normal al 100 %; si todo cuadra, ¡adelante!",
  pr_s2: "Imprimir", pr_zuhause: "En casa", pr_druckerei: "Imprenta", pr_noch_nicht: "Aún no creado: elígelo en Generar.",
  pr_tipps_zuhause: ["Imprime al 100 % o «Tamaño real», no «Ajustar a la página»",
    "A doble cara, volteo por el borde largo. ¿Sin dúplex? Primero los anversos, voltea el montón y luego los reversos",
    "Cartulina firme (unos 200–300 g/m²) hace las cartas agradables al tacto",
    "Elige papel A4 o Carta en Generar, en «Impresión en casa»",
    "Corta siguiendo las marcas, con regla y cúter o una guillotina"],
  pr_finden_titel: "Cómo encontrar una imprenta adecuada",
  pr_finden_text: "En muchos países hay imprentas en línea de cartas o tarjetas personalizadas. Lo importante: cada carta necesita su propio anverso y reverso.",
  pr_suchbegriffe: "Para buscar:", pr_suchbegriffe_liste: "«imprimir cartas personalizadas», «barajas personalizadas», «custom playing cards»",
  pr_achten: "Fíjate en:",
  pr_achten_liste: ["Cada carta con su propio anverso y reverso, no un reverso común para todas",
    "Tamaño: la carta de póker de 63 × 88 mm sirve directo; otros tamaños se ajustan en Generar, «Tamaño final»",
    "Sangrado: normalmente 3 mm alrededor; ya viene en el PDF de imprenta",
    "¿La plantilla pide formato vertical? Activa «Archivo de imprenta vertical»",
    "Subir en PDF o imágenes sueltas; compara pedido mínimo, grosor y envío",
    "Primero pide un mazo de muestra y luego el resto"],
  pr_s3: "Aprender en digital", pr_digital_leer: "¿Quieres aprender también en el celular o la computadora? Con un clic tus cartas se vuelven tarjetas de Anki, una página de estudio y un PDF de pantalla.",
  pr_digital_knopf: "Crear tarjetas digitales",
  pr_digital_tipps: ["Paquete de Anki: ábrelo en Anki en la computadora, o envíalo al celular por correo, nube o cable e impórtalo en AnkiDroid (Android) o AnkiMobile (iPhone/iPad)",
    "Página de estudio: ábrela en el navegador de la computadora, funciona sin conexión; tu progreso se guarda en ese navegador. En el celular funciona solo a medias (en el iPhone casi nunca arranca desde la app Archivos); ahí mejor usa el paquete de Anki o el PDF de pantalla",
    "PDF de pantalla: hojéalo en cualquier app de PDF: anverso, reverso, siguiente carta",
    "Para Quizlet, Brainscape, Mochi y más, elige en Generar el formato «Tablas (CSV)»"],
  pr_vorlagen_text: "Plantillas vacías con líneas guía: prácticas si diseñas cartas en otro programa.",
  ie_knopf: "⇅ Importar / exportar", ie_titel: "Importar / exportar cartas e ideas",
  ie_export_titel: "Exportar", ie_export_text: "Empaca cartas y/o ideas con sus imágenes en un ZIP: para respaldar, compartir o pasar a otro dispositivo.",
  ie_alle: n => `Todas las cartas (${n})`, ie_aktiv: n => `Solo las cartas que se imprimen (${n})`, ie_export_knopf: "Descargar ZIP",
  ie_import_titel: "Importar",
  ie_import_text: "Elige o arrastra un ZIP exportado (o una lista de cartas en CSV). Primero ves una vista previa; nada se toma antes.",
  ie_waehlen: "Elegir archivo …", ie_pruefe: "Revisando el archivo …", ie_andere: "Elegir otro archivo",
  ie_vorschau: z => `${z.neu} nuevas · ${z.konflikt} ya existen pero distintas · ${z.gleich} iguales · ${z.fehler} con error`,
  ie_s_neu: "nueva", ie_s_konflikt: "distinta", ie_s_gleich: "igual", ie_s_fehler: "error", ie_hier: "aquí:",
  ie_behalten: "Conservar las mías", ie_ersetzen: "Reemplazar con la importación (las imágenes viejas van a bilder/_entfernt)",
  ie_uebernehmen: n => `Tomar ${n} ${n === 1 ? "carta" : "cartas"}`, ie_nichts: "Nada que tomar: todo ya está aquí, o las entradas necesitan un retoque.",
  ie_fertig: z => `¡Importación lista! ${z.neu + z.ersetzt} cartas (${z.ersetzt} reemplazadas) y ${z.ideen_neu + z.ideen_ersetzt} ideas${z.uebersprungen ? `, ${z.uebersprungen} conservadas` : ""}${z.fehler ? `, ${z.fehler} omitidas` : ""}. ¡Genial!`,
  gw_knopf: "🎨 Diseñar imagen GANS", gw_knopf_unter: "Convierte una foto de ganso en imagen de carta con «GANS + palabra».",
  gw_titel: "Diseñar imagen GANS", gw_leer: "Elige o arrastra una foto de ganso", gw_leer_unter: "JPG, PNG o WEBP; luego recorta y pon el texto.",
  gw_anderes: "Otra foto …", gw_text: "Texto después de GANS", gw_text_ph: "p. ej. alt, aufgeregt, arg Hunger",
  gw_format: "Recorte", gw_quadrat: "Cuadrado", gw_karte: "Carta horizontal", gw_hoch: "Vertical",
  gw_zoom: "Zoom", gw_groesse: "Tamaño del texto", gw_schrift: "Letra", gw_farbe: "Color",
  gw_weiss: "Blanco con borde", gw_schwarz: "Negro con borde", gw_gelb: "Amarillo con borde",
  gw_hilfe: "Arrastrar la imagen = mover el recorte · arrastrar el texto = mover el texto · rueda = zoom",
  gw_datei: n => `Nombre del archivo: ${n}`, gw_als_karte: "Como carta nueva (paso 1)", gw_als_idee: "Guardar como idea",
  gw_fuer_idee: "Usar para esta idea", gw_herunterladen: "Descargar", gw_text_fehlt: "Falta una palabra después de GANS, ¡y tu imagen queda completa!",
  gw_ok_karte: "¡Qué buena imagen! Te espera en el paso 1: revísala y tómala allí.", gw_ok_idee: "Guardada como idea. ¡Buena idea!",
  gw_s_poppins: "Poppins Bold (como las cartas)", gw_s_poppins_m: "Poppins Medium", gw_s_impact: "Impact (meme)",
  gw_s_arial: "Arial Black", gw_s_comic: "Comic Sans", gw_s_georgia: "Georgia (con serifa)", gw_mitte: "Centrar texto",
  // Imagen IA (ganso realista, sin conexión)
  ki_knopf: "🪄 Crear ganso con IA", ki_knopf_unter: "Una foto realista de ganso a partir de una descripción corta, sin conexión en esta computadora.",
  ki_titel: "Crear ganso con IA", ki_editor_knopf: "🪄 Con IA …",
  ki_intro: "Di brevemente cómo y dónde se ve el ganso; el programa te pinta una foto realista. Después le pones tu palabra.",
  ki_wort: "Palabra en la carta", ki_wort_ph: "p. ej. alt, aufgeregt, schön müde",
  ki_wort_hinweis: "No se pinta en la imagen; la pones limpia después con «Poner la palabra en la imagen».",
  ki_beschreibung: "Descripción en inglés: ¿cómo y dónde está el ganso?", ki_beschreibung_ph: "e.g. sleeping in a nest of straw, morning sun",
  ki_uebersetzen: "🌐 Al inglés", ki_uebersetzt: "Traducido; échale un ojo para ver si queda bien.",
  ki_token: n => `${n} de 75 tokens: cabe`, ki_zu_lang: n => `Atención: ${n} de 75 tokens; el modelo ya no lee el final. Mejor un poco más corto.`,
  ki_ohne_menschen: "Sin personas (recomendado, unos 20 s más)",
  ki_erzeugen: "🪄 Crear ganso", ki_neu_wuerfeln: "🎲 Otra variante",
  ki_hilfe_knopf: "Cómo funciona", ki_prompt_knopf: "Editar prompt estándar …",
  ki_hilfe_was: "¿Qué escribo?",
  ki_hilfe_was_liste: ["Breve y en inglés: qué hace el ganso y dónde está; p. ej. «swimming on a lake at sunset», «sleeping in a nest of straw», «standing in fresh snow».",
    "Puedes agregar luz, estación, clima o ambiente: «morning fog», «autumn leaves», «golden hour».",
    "Mejor di lo que debe verse y no lo que no; el interruptor «Sin personas» mantiene lejos a la gente.",
    "¿Sin inglés a la mano? Escribe en español y haz clic en «🌐 Al inglés» (solo con la traducción activada)."],
  ki_hilfe_gut: "Lo hace bien:",
  ki_hilfe_gut_liste: ["un ganso en un entorno natural, cerca y nítido", "luz, estación del año, clima y paisaje",
    "posturas sencillas: parado, nadando, volando, durmiendo, comiendo, mirando con curiosidad"],
  ki_hilfe_schwach: "Ahí le cuesta:",
  ki_hilfe_schwach_liste: ["texto y letras en la imagen (por eso tú pones la palabra después)",
    "cantidades exactas y varios animales haciendo algo juntos", "actividades humanas (andar en bici, leer) y sostener cosas con el pico o las patas",
    "razas concretas y el mismo ganso en varias cartas", "de vez en cuando una pata o un cuello de más; entonces pide otra variante"],
  ki_hilfe_zeit: "En una laptop normal, una imagen tarda unos 1–2 minutos. Todo funciona sin conexión en esta computadora; puedes cerrar la ventana y seguir trabajando. Misma descripción + misma semilla = misma imagen.",
  ki_prompt_titel: "Prompt estándar (para curiosos)",
  ki_prompt_text: "Así habla el programa con el modelo. {description} se sustituye por tu descripción y {word} por la palabra de la carta (no se usa de forma predeterminada: el modelo no escribe texto limpio). El inglés funciona mejor.",
  ki_vorlage: "Plantilla", ki_negativ: "Lo que no debe aparecer (funciona junto con «Sin personas»)",
  ki_prompt_speichern: "Guardar mi versión", ki_prompt_zurueck: "Restaurar estándar", ki_prompt_eigene: "tu versión está activa",
  ki_prompt_gespeichert: "Guardado: desde ahora se usa tu versión.", ki_prompt_zurueck_ok: "Volvió el prompt estándar.",
  ki_so_gehts: "Esto recibe el modelo:", ki_negativ_kurz: "no en la imagen",
  ki_platzhalter: "Aquí aparece tu ganso", ki_startet: "Preparando el ganso …",
  ki_laeuft: p => `El ganso va tomando forma … ${p} %`, ki_hintergrund: "Puedes cerrar la ventana; sigue trabajando en segundo plano.",
  ki_startwert: s => `Semilla ${s}: misma descripción + misma semilla da la misma imagen.`,
  ki_wort_setzen: "✍️ Poner la palabra en la imagen …", ki_als_karte: "Como carta nueva sin palabra", ki_fuer_karte: "Usar para esta carta",
  ki_ok_editor: "La imagen nueva te espera en el editor de cartas; revísala y aplícala.",
  ki_modell_fehlt: "Aún falta el modelo de imágenes IA (unos 3,5 GB, una sola vez). Después todo funciona sin conexión.", ki_modell_laden: "Instalar la herramienta «Imágenes IA» …",
  ki_anderer_lauf: "Ahora mismo se está ejecutando otra cosa; tu ganso simplemente se forma en la fila.",
  ki_beschreibung_fehlt: "Cuenta brevemente cómo y dónde se ve el ganso, ¡y listo!",
  ki_fertig_toast: "¡Tu ganso IA está listo!", ki_ansehen: "Ver", ki_abgebrochen: "Cancelado; no pasa nada, vuelve a empezar.",
  ki_fehler: "Esta vez no funcionó; los detalles están en el registro.",
  nav_ideen: "Ideas", ideen_titel: "Ideas para cartas nuevas",
  ideen_unter: "Una idea solo necesita una imagen, una palabra en alemán o en {zs}. Complétala poco a poco; con «Hacer carta» queda lista y pasa a Mis cartas.",
  idee_neu: "+ Idea nueva", ideen_eigene: "Mis ideas", ideen_unfertig: "Cartas sin terminar de «Carta nueva»",
  ideen_leer: "¿Aún no hay ideas? No pasa nada: crea una o diseña una imagen GANS.", ideen_unfertig_leer: "No hay cartas sin terminar. ¡Todo listo!",
  idee_bild_fehlt: "Aún sin imagen", idee_bild_laden: "Elegir imagen …", idee_bild_gestalten: "Diseñar imagen GANS …",
  idee_de: "Texto de la imagen (alemán)", idee_es: "Palabra en {zs}", idee_notiz: "Nota", idee_de_ph: "p. ej. Gans alt", idee_es_ph: "p. ej. viejo",
  idee_aufnehmen: "Hacer carta", idee_weg: "Descartar", idee_fehlt_noch: l => `¡Casi es una carta! Solo falta: ${l}`,
  idee_teil_bild: "imagen", idee_teil_de: "texto de la imagen", idee_teil_es: "palabra en {zs}",
  idee_aufgenommen: n => `Carta ${n} creada; ahora está en Mis cartas. ¡Bravo!`, idee_verworfen: "Idea descartada: ¡espacio para nuevas!",
  idee_ersetzen: "Reemplazar la imagen existente con este nombre",
  unfertig_entwurf: "Imagen preparada, aún no tomada", unfertig_offen: "La palabra en {zs} viene pronto", unfertig_ohne: "Imagen sin fila en la lista de cartas",
  unfertig_weiter: "Seguir →",
  st_titel: "¿Cómo debe abrirse Me Goos-ta Deutsch?", st_text: "Se aplica desde el próximo inicio. Puedes cambiarlo cuando quieras en Herramientas → Inicio.",
  st_standard: "En el navegador predeterminado", st_standard_text: "Como hasta ahora: el navegador que usa tu computadora.",
  st_browser: b => `En ${b}`, st_browser_text: "Siempre en este navegador, aunque otro sea el predeterminado.",
  st_fenster: "En una ventana propia", st_fenster_text: b => `Ventana propia del programa sin barra de direcciones ni pestañas (con ${b}).`,
  st_fenster_nein: "Para esto hace falta Edge, Chrome, Brave o Chromium; en el navegador predeterminado todo funciona igual de bien.", st_speichern: "Guardar", st_spaeter: "Preguntar después",
  de_titel: "Desinstalar programa", de_text: "Esto quita Me Goos-ta Deutsch por completo de esta computadora:",
  de_p1: "Icono del escritorio y del menú Inicio (Mac: app, Linux: entrada de menú)", de_p2: "el Python propio, los ajustes y las traducciones guardadas",
  de_p3: "la carpeta del programa, con todas las cartas, imágenes, ideas y archivos de impresión", de_warnung: "No se puede deshacer; mejor respalda antes tus cartas.",
  de_haken: "Sí, borrar Me Goos-ta Deutsch con todas las cartas e imágenes.",
  de_los: "Desinstalar definitivamente", de_ende: "Me Goos-ta Deutsch se está quitando. Puedes cerrar esta ventana.",
});

// Warteschlange: höchstens ein Hintergrundprozess, alles Weitere wartet und läuft automatisch nacheinander
Object.assign(TXT.de, {
  ws_titel: "Warteschlange", ws_jetzt: "Läuft gerade", ws_nichts: "Gerade läuft nichts – die Gänse machen Pause.",
  ws_wartend: "Wartet", ws_keine_wartend: "Niemand wartet – die Schlange ist ganz leer.", ws_platz: n => `Platz ${n}`,
  ws_zuletzt: "Zuletzt erledigt", ws_seit: s => `seit ${s}`, ws_als_naechstes: "Als Nächstes",
  ws_leeren: "Alle wartenden entfernen", ws_leeren_frage: n => `Wirklich alle ${n} wartenden Aufträge entfernen? Der laufende macht weiter.`,
  ws_leeren_ja: "Ja, entfernen", ws_leeren_nein: "Lieber nicht", ws_ansehen: "Ergebnis ansehen", ws_protokoll: "Protokoll",
  ws_ansehen_kurz: "Ansehen", ws_eingereiht: n => `In der Warteschlange – Platz ${n}. Die Gänse stehen ordentlich Schlange!`,
  ws_entfernt: "Aus der Warteschlange genommen.", ws_geleert: "Die wartenden Aufträge sind entfernt.",
  ws_danach: n => n === 1 ? "Danach wartet noch 1 Auftrag." : `Danach warten noch ${n} Aufträge.`,
  ws_knopf_label: n => `Warteschlange: ${n} ${n === 1 ? "Auftrag" : "Aufträge"}`,
  ws_beenden_frage: "Die Gänse stehen noch Schlange: Ein Auftrag läuft oder wartet. Beim Beenden wird er abgebrochen und alle wartenden fallen weg.",
  ws_beenden_ja: "Trotzdem beenden", ws_beenden_nein: "Weiterlaufen lassen", ws_raus: "Aus der Warteschlange nehmen",
  ki_wartet: n => `Deine Gans wartet – Platz ${n} in der Warteschlange`,
  ki_wartet_info: "Sobald sie dran ist, legt sie automatisch los – du kannst das Fenster ruhig schließen.",
  h_ws_knopf: "Warteschlange: was gerade läuft und was danach drankommt – umsortieren, entfernen, abbrechen",
  h_ws_hoch: "Einen Platz nach vorn", h_ws_runter: "Einen Platz nach hinten", h_ws_naechstes: "Kommt direkt nach dem laufenden Auftrag dran",
  h_ws_entfernen: "Diesen Auftrag aus der Warteschlange nehmen", h_ws_leeren: "Nimmt alle wartenden Aufträge heraus – der laufende macht weiter",
});
Object.assign(TXT.en, {
  ws_titel: "Queue", ws_jetzt: "Running now", ws_nichts: "Nothing is running – the geese are taking a break.",
  ws_wartend: "Waiting", ws_keine_wartend: "Nobody is waiting – the queue is completely empty.", ws_platz: n => `Place ${n}`,
  ws_zuletzt: "Recently done", ws_seit: s => `for ${s}`, ws_als_naechstes: "Up next",
  ws_leeren: "Remove all waiting", ws_leeren_frage: n => `Really remove all ${n} waiting tasks? The running one keeps going.`,
  ws_leeren_ja: "Yes, remove", ws_leeren_nein: "Better not", ws_ansehen: "View result", ws_protokoll: "Log",
  ws_ansehen_kurz: "View", ws_eingereiht: n => `In the queue – place ${n}. The geese are lining up nicely!`,
  ws_entfernt: "Taken out of the queue.", ws_geleert: "The waiting tasks have been removed.",
  ws_danach: n => n === 1 ? "1 more task is waiting after this." : `${n} more tasks are waiting after this.`,
  ws_knopf_label: n => `Queue: ${n} ${n === 1 ? "task" : "tasks"}`,
  ws_beenden_frage: "The geese are still lining up: a task is running or waiting. Quitting cancels it and drops everything that is waiting.",
  ws_beenden_ja: "Quit anyway", ws_beenden_nein: "Keep it running", ws_raus: "Take out of the queue",
  ki_wartet: n => `Your goose is waiting – place ${n} in the queue`,
  ki_wartet_info: "As soon as it’s its turn, it starts by itself – feel free to close this window.",
  h_ws_knopf: "Queue: what is running now and what comes next – reorder, remove, cancel",
  h_ws_hoch: "Move one place up", h_ws_runter: "Move one place down", h_ws_naechstes: "Runs right after the current task",
  h_ws_entfernen: "Take this task out of the queue", h_ws_leeren: "Removes all waiting tasks – the running one keeps going",
});
Object.assign(TXT.es, {
  ws_titel: "Fila de espera", ws_jetzt: "En curso", ws_nichts: "No hay nada en curso; los gansos están descansando.",
  ws_wartend: "En espera", ws_keine_wartend: "Nadie espera; la fila está completamente vacía.", ws_platz: n => `Lugar ${n}`,
  ws_zuletzt: "Terminado hace poco", ws_seit: s => `desde hace ${s}`, ws_als_naechstes: "Siguiente",
  ws_leeren: "Quitar todas las que esperan", ws_leeren_frage: n => `¿De verdad quitar las ${n} tareas en espera? La que está en curso sigue.`,
  ws_leeren_ja: "Sí, quitar", ws_leeren_nein: "Mejor no", ws_ansehen: "Ver resultado", ws_protokoll: "Registro",
  ws_ansehen_kurz: "Ver", ws_eingereiht: n => `En la fila de espera: lugar ${n}. ¡Los gansos hacen fila en orden!`,
  ws_entfernt: "Se quitó de la fila de espera.", ws_geleert: "Se quitaron las tareas en espera.",
  ws_danach: n => n === 1 ? "Después espera 1 tarea más." : `Después esperan ${n} tareas más.`,
  ws_knopf_label: n => `Fila de espera: ${n} ${n === 1 ? "tarea" : "tareas"}`,
  ws_beenden_frage: "Los gansos siguen en fila: hay una tarea en curso o en espera. Al salir se cancela y se descarta todo lo que espera.",
  ws_beenden_ja: "Salir de todos modos", ws_beenden_nein: "Dejar que siga", ws_raus: "Quitar de la fila de espera",
  ki_wartet: n => `Tu ganso está esperando: lugar ${n} en la fila`,
  ki_wartet_info: "En cuanto le toque, empieza solo; puedes cerrar esta ventana tranquilamente.",
  h_ws_knopf: "Fila de espera: lo que está en curso y lo que sigue; reordenar, quitar, cancelar",
  h_ws_hoch: "Subir un lugar", h_ws_runter: "Bajar un lugar", h_ws_naechstes: "Va justo después de la tarea en curso",
  h_ws_entfernen: "Quitar esta tarea de la fila de espera", h_ws_leeren: "Quita todas las tareas en espera; la que está en curso sigue",
});

// Tools: optionale Funktionen – nicht vorinstalliert, auf Wunsch geladen (über die Warteschlange), wieder deinstallierbar
Object.assign(TXT.de, {
  tools_titel: "Tools", tools_belegt: g => `Belegt: ${g}`,
  tools_unter: "Optionale Extras – installiert ist nur, was du wirklich brauchst. Fehlt eins, fragt das Programm beim ersten Gebrauch und macht danach gleich weiter.",
  tool_nicht: "nicht installiert", tool_installiert: "installiert ✓", tool_laedt: p => `lädt … ${p} %`, tool_wartet: n => `wartet (Platz ${n})`,
  tool_angefangen: p => `angefangen (${p} %)`, tool_download: g => `Download ca. ${g}`, tool_ohne_download: "kein Download", tool_belegt: g => `belegt ${g}`,
  tool_installieren: "Installieren", tool_fortsetzen: "Weiter laden", tool_deinstallieren: "Deinstallieren …",
  tool_groesse: "Größe", tool_ort: "Speicherort", tool_dauer: "Dauer", tool_quelle: "Quelle",
  tool_brauchen_text: n => `Dafür brauchst du das Tool „${n}“ – es ist noch nicht installiert.`,
  tool_brauchen_hinweis: "Der Download läuft über die Warteschlange, du kannst nebenbei weiterarbeiten. Danach geht es automatisch weiter.",
  tool_installieren_weiter: "Installieren und weitermachen", tool_ohne: "Ohne Tool weiter",
  verb_tool_titel: "Tool „Bildverbesserung“ ist noch nicht installiert", verb_tool_text: "Mit Real-ESRGAN werden deine Vorderseiten gestochen scharf. Ohne Tool vergrößert das eingebaute FSRCNN – etwas schlichter, aber gans ordentlich.",
  verb_tool_knopf: g => `Installieren (ca. ${g})`, verb_tool_x2: g => `Schneller ×2 · ca. ${g}`, verb_ohne_tool: "Einfach vergrößern (ohne Tool)",
  tool_ram_wenig: g => `Achtung: Dieser Rechner hat ${g} GB Arbeitsspeicher, empfohlen sind 8 GB. Es klappt meist trotzdem – nur gemächlicher.`,
  tool_platz_knapp: (frei, noetig) => `Achtung: Auf dem Laufwerk sind nur noch ${frei} frei, gebraucht werden etwa ${noetig}. Bitte zuerst etwas Platz schaffen.`, u_tools: "Tools",
  tool_kommt: n => `„${n}“ wird gerade geladen – danach geht es automatisch weiter.`,
  tool_laedt_los: n => `„${n}“ wird geladen – die Gänse holen es gerade ab.`,
  tool_ist_bereit: n => `Tool „${n}“ ist bereit – gans schön praktisch!`,
  tool_nicht_geklappt: n => `„${n}“ ließ sich gerade nicht laden – im Protokoll steht, warum. Einfach später noch einmal versuchen.`,
  tool_weg_titel: n => `„${n}“ deinstallieren?`, tool_weg_text: "Das gibt Speicherplatz frei. Gelöscht wird nur, was zum Tool gehört:",
  tool_weg_frei: g => `wieder frei: ca. ${g}`, tool_weg_ja: "Ja, deinstallieren", tool_weg_nein: "Behalten",
  tool_weg_bleibt: "Deine Karten, Bilder und Ideen bleiben – und das Tool lässt sich jederzeit wieder installieren.",
  tools_erst_titel: "Welche Tools möchtest du?",
  tools_erst_text: "Diese Extras sind nicht vorinstalliert – so bleibt das Programm schlank. Wähle, was gleich geladen werden soll (nichts ist vorausgewählt).",
  tools_erst_summe: g => `Zusammen: ca. ${g}`, tools_erst_spaeter_knopf: "Später",
  tools_erst_spaeter: "Alles andere installierst du jederzeit unter Werkzeuge → Tools – oder einfach dann, wenn du es zum ersten Mal brauchst.",
  tools_erst_los: n => n ? `${n} installieren` : "Ohne Tools weiter",
  tools_erst_ok: "Prima – die Tools stehen in der Warteschlange und laden nacheinander.",
  h_tool_installieren: "Lädt das Tool über die Warteschlange – du kannst nebenbei weiterarbeiten",
  h_tool_deinstallieren: "Löscht nur die Dateien dieses Tools und gibt Platz frei – deine Karten bleiben",
  h_tool_teil: "Lädt eine zusätzliche Variante dieses Tools",
});
Object.assign(TXT.en, {
  tools_titel: "Optional tools", tools_belegt: g => `In use: ${g}`,
  tools_unter: "Optional extras – only what you really need gets installed. If one is missing, the program asks the first time you use it and then carries straight on.",
  tool_nicht: "not installed", tool_installiert: "installed ✓", tool_laedt: p => `downloading … ${p} %`, tool_wartet: n => `waiting (place ${n})`,
  tool_angefangen: p => `started (${p} %)`, tool_download: g => `Download about ${g}`, tool_ohne_download: "no download", tool_belegt: g => `uses ${g}`,
  tool_installieren: "Install", tool_fortsetzen: "Continue download", tool_deinstallieren: "Uninstall …",
  tool_groesse: "Size", tool_ort: "Location", tool_dauer: "Time", tool_quelle: "Source",
  tool_brauchen_text: n => `For this you need the “${n}” tool – it isn’t installed yet.`,
  tool_brauchen_hinweis: "The download runs through the queue, so you can keep working meanwhile. Afterwards it carries on by itself.",
  tool_installieren_weiter: "Install and carry on", tool_ohne: "Continue without the tool",
  verb_tool_titel: "The “Image enhancement” tool isn’t installed yet", verb_tool_text: "With Real-ESRGAN your fronts come out razor-sharp. Without the tool, the built-in FSRCNN upscales – a little simpler, but in fine feather.",
  verb_tool_knopf: g => `Install (about ${g})`, verb_tool_x2: g => `Faster ×2 · about ${g}`, verb_ohne_tool: "Just upscale (without the tool)",
  tool_ram_wenig: g => `Heads-up: this computer has ${g} GB of memory, 8 GB are recommended. It usually works anyway – just at a gentler waddle.`,
  tool_platz_knapp: (frei, noetig) => `Heads-up: only ${frei} are free on the drive, about ${noetig} are needed. Please make some room first.`, u_tools: "Tools",
  tool_kommt: n => `“${n}” is downloading right now – afterwards it carries on by itself.`,
  tool_laedt_los: n => `“${n}” is downloading – the geese are fetching it.`,
  tool_ist_bereit: n => `Tool “${n}” is ready – honk if you like it!`,
  tool_nicht_geklappt: n => `“${n}” couldn’t be downloaded just now – the log says why. Simply try again later.`,
  tool_weg_titel: n => `Uninstall “${n}”?`, tool_weg_text: "This frees up space. Only what belongs to the tool is deleted:",
  tool_weg_frei: g => `space freed: about ${g}`, tool_weg_ja: "Yes, uninstall", tool_weg_nein: "Keep it",
  tool_weg_bleibt: "Your cards, images and ideas stay – and you can reinstall the tool any time.",
  tools_erst_titel: "Which tools would you like?",
  tools_erst_text: "These extras aren’t preinstalled – that keeps the program slim. Choose what to download right away (nothing is preselected).",
  tools_erst_summe: g => `Together: about ${g}`, tools_erst_spaeter_knopf: "Later",
  tools_erst_spaeter: "You can install everything else any time under Tools → Optional tools – or simply when you need it for the first time.",
  tools_erst_los: n => n ? `Install ${n}` : "Continue without tools",
  tools_erst_ok: "Great – the tools are in the queue and download one after another.",
  h_tool_installieren: "Downloads the tool through the queue – you can keep working meanwhile",
  h_tool_deinstallieren: "Deletes only this tool’s files and frees up space – your cards stay",
  h_tool_teil: "Downloads an extra variant of this tool",
});
Object.assign(TXT.es, {
  tools_titel: "Herramientas opcionales", tools_belegt: g => `En uso: ${g}`,
  tools_unter: "Extras opcionales: solo se instala lo que de verdad necesitas. Si falta una, el programa pregunta la primera vez que la usas y luego sigue de inmediato.",
  tool_nicht: "no instalada", tool_installiert: "instalada ✓", tool_laedt: p => `descargando … ${p} %`, tool_wartet: n => `en espera (lugar ${n})`,
  tool_angefangen: p => `empezada (${p} %)`, tool_download: g => `Descarga de unos ${g}`, tool_ohne_download: "sin descarga", tool_belegt: g => `ocupa ${g}`,
  tool_installieren: "Instalar", tool_fortsetzen: "Seguir descargando", tool_deinstallieren: "Desinstalar …",
  tool_groesse: "Tamaño", tool_ort: "Ubicación", tool_dauer: "Tiempo", tool_quelle: "Origen",
  tool_brauchen_text: n => `Para esto necesitas la herramienta «${n}»; todavía no está instalada.`,
  tool_brauchen_hinweis: "La descarga pasa por la fila de espera, así que puedes seguir trabajando. Después todo sigue solo.",
  tool_installieren_weiter: "Instalar y seguir", tool_ohne: "Seguir sin la herramienta",
  verb_tool_titel: "La herramienta «Mejora de imagen» aún no está instalada", verb_tool_text: "Con Real-ESRGAN tus anversos quedan nítidos. Sin la herramienta, el FSRCNN integrado amplía: un poco más sencillo, pero muy decente.",
  verb_tool_knopf: g => `Instalar (unos ${g})`, verb_tool_x2: g => `Más rápido ×2 · unos ${g}`, verb_ohne_tool: "Solo ampliar (sin la herramienta)",
  tool_ram_wenig: g => `Atención: esta computadora tiene ${g} GB de memoria; se recomiendan 8 GB. Casi siempre funciona igual, solo más despacio.`,
  tool_platz_knapp: (frei, noetig) => `Atención: en la unidad solo quedan ${frei} libres y hacen falta unos ${noetig}. Primero libera algo de espacio.`, u_tools: "Herramientas",
  tool_kommt: n => `«${n}» se está descargando; después todo sigue solo.`,
  tool_laedt_los: n => `«${n}» se está descargando: los gansos ya van por ella.`,
  tool_ist_bereit: n => `¡La herramienta «${n}» está lista: todo en orden en el corral!`,
  tool_nicht_geklappt: n => `«${n}» no se pudo descargar ahora; el registro dice por qué. Vuelve a intentarlo más tarde.`,
  tool_weg_titel: n => `¿Desinstalar «${n}»?`, tool_weg_text: "Así liberas espacio. Solo se borra lo que pertenece a la herramienta:",
  tool_weg_frei: g => `espacio liberado: unos ${g}`, tool_weg_ja: "Sí, desinstalar", tool_weg_nein: "Conservarla",
  tool_weg_bleibt: "Tus cartas, imágenes e ideas se quedan, y puedes volver a instalar la herramienta cuando quieras.",
  tools_erst_titel: "¿Qué herramientas quieres?",
  tools_erst_text: "Estos extras no vienen preinstalados: así el programa se mantiene ligero. Elige qué descargar ahora mismo (no hay nada preseleccionado).",
  tools_erst_summe: g => `En total: unos ${g}`, tools_erst_spaeter_knopf: "Después",
  tools_erst_spaeter: "Todo lo demás lo instalas cuando quieras en Herramientas → Herramientas opcionales, o simplemente cuando lo necesites por primera vez.",
  tools_erst_los: n => n ? `Instalar ${n}` : "Seguir sin herramientas",
  tools_erst_ok: "¡Genial! Las herramientas están en la fila de espera y se descargan una tras otra.",
  h_tool_installieren: "Descarga la herramienta por la fila de espera; mientras, puedes seguir trabajando",
  h_tool_deinstallieren: "Borra solo los archivos de esta herramienta y libera espacio; tus cartas se quedan",
  h_tool_teil: "Descarga una variante adicional de esta herramienta",
});

/* ===================== Grundlagen ===================== */
const S = { sprache: document.documentElement.lang || "en", karten: [], ohne: [], meldungen: [], gruppen: [], werte: {}, auswahl: "",
  lauf: null, laufAb: 0, entwuerfe: [], hochladen: [], status: {}, doc: "leitfaden", v: 1, extra: [], stand: {}, rueck: null,
  upl: { gesamt: 0, fertig: 0 }, ersatz: {}, offeneEntwuerfe: new Set(), vorschlaege: {}, autoVersucht: new Set(), beschaeftigt: false,
  gans: null, ue: null, verbWahl: new Set(), tabFilter: "alle", tabSuche: "", tabSort: null,
  ws: { aktiv: null, wartend: [], fertig: [] }, wsZahl: 0, wsBeenden: false, wsLeeren: false, wsProtokoll: null,
  laufBekannt: new Set(), laufGemeldet: new Set(), zeigeZs: {}, weitereOffen: new Set(), gestartet: false };
// Hovertexte (Hilfe beim Draufzeigen): Meine Karten, Neue Karte, Ideen
Object.assign(TXT.de, {
  h_nav_karten: "Alle deine Karten – umdrehen, sortieren, bearbeiten, pausieren", h_nav_tabelle: "Vorder- und Rückseite nebeneinander – ideal zum Prüfen der Übersetzungen",
  h_nav_verbesserung: "Bilder vorab verbessern und Vorher/Nachher vergleichen", h_nav_bild: "Schritt 1: neue Bilder hinzufügen – eins oder gleich viele",
  h_nav_beschriften: "Schritt 2: das Wort auf {zs} für die Rückseite eintragen", h_nav_ideen: "Halbe Ideen parken und später in Ruhe fertig machen",
  h_neue_karte: "Mit einem neuen Bild loslegen (Schritt 1)", h_ie_knopf: "Karten und Ideen sichern, weitergeben oder einlesen",
  h_bearbeiten: "Wort, Text, Notiz und Bild dieser Karte ändern", h_entfernen: "Nimmt die Karte aus der Liste – das Bild bleibt im Ordner, „Rückgängig“ holt sie zurück",
  h_marke_bild_fehlt: "Die Bilddatei liegt nicht im Ordner bilder/ – ohne Bild wird die Karte nicht gedruckt",
  h_marke_es_fehlt: "Trag in Schritt 2 das Wort auf {zs} ein – dann ist die Karte druckbereit",
  h_marke_geprueft: "Du hast diese Übersetzung in der Tabelle als geprüft abgehakt – vorbildlich!",
  h_marke_aus: "Der Schalter „Drucken“ ist aus: Die Karte bleibt in der Liste, kommt aber nicht in die Druckdateien",
  h_marke_text: "So passt das Wort noch nicht ganz auf die Rückseite – kürzer schreiben oder mit „|“ umbrechen",
  h_text_auf_bild: "Steht auf der Vorderseite und ergibt den Dateinamen", h_alle_uebernehmen: "Übernimmt alle Bilder, die bereit sind (grünes ✓)",
  h_alle_uebersetzen: "Schlägt für alle Karten ohne Wort auf {zs} eine Übersetzung vor – du prüfst danach",
  h_uebernehmen: "Legt die Karte an: Das Bild kommt nach bilder/, die Karte in die Kartenliste", h_details: "Original, Vorschau, Drehen, Bildausschnitt und alle Prüfungen",
  h_verwerfen: "Dieses neue Bild doch nicht übernehmen", h_ersetzen: "Ersetzt das vorhandene Bild gleichen Namens – die alte Fassung kommt nach bilder/_entfernt/",
  h_fit_contain: "Zeigt das ganze Bild; freie Ränder werden weich fortgesetzt", h_fit_cover: "Füllt die ganze Karte; überstehende Ränder werden abgeschnitten",
  h_de_feld: "So steht es auf dem Bild – hilft beim Prüfen und auf dem Prüfbogen", h_notiz: "Nur für dich, z. B. die Wortart – wird nicht gedruckt",
  h_zeichen: "Fügt das Zeichen an der Schreibmarke ein", h_spaeter: "Diese Karte erst einmal überspringen – sie wartet hier geduldig auf dich",
  h_karte_speichern: "Speichert Wort, Text und Notiz – klickbar, sobald alle Prüfungen passen", h_alle_speichern: "Speichert alle Karten, die bereit sind",
  h_bild_entfernen: "Nimmt das neue Bild wieder heraus (es kommt nach bilder/_entfernt/)",
  h_bild_aendern: "Ein neues Bild für diese Karte wählen – oder einfach auf die Vorschau ziehen. Wort, Text und Notiz bleiben",
  h_ki_editor: "Ein neues, realistisches Gänse-Bild für diese Karte erzeugen – offline. Wort, Text und Notiz bleiben",
  h_ki_uebersetzen: "Schickt nur diese Beschreibung an den Übersetzungsdienst (MyMemory oder DeepL) – nur mit eingeschalteter Übersetzung",
  h_ersatz_uebernehmen: "Ersetzt das Bild der Karte – das bisherige wird in bilder/_entfernt/ aufgehoben, „Rückgängig“ holt es zurück",
  h_ersatz_verwerfen: "Das neue Bild nicht verwenden – die Karte bleibt, wie sie ist",
  h_idee_neu: "Leere Idee anlegen – ein Bild oder ein Wort reicht für den Anfang", h_idee_bild: "Ein Bild für diese Idee wählen – oder einfach hierher ziehen",
  h_idee_gestalten: "Aus einem Gänse-Foto ein Bild mit „GANS + Wort“ bauen", h_idee_es: "Das Wort für die Rückseite – 🌐 schlägt eins vor", h_es_feld: "Das Wort auf Spanisch für die Rückseite – gemeint ist immer das in Mexiko gesprochene Spanisch",
  h_idee_aufnehmen: "Macht aus der fertigen Idee eine Karte unter „Meine Karten“ (braucht Bild, Text und Wort)", h_idee_weg: "Diese Idee verwerfen",
  h_unfertig_weiter: "Öffnet diese Karte genau dort, wo es weitergeht",
});
Object.assign(TXT.en, {
  h_nav_karten: "All your cards – flip, sort, edit, pause", h_nav_tabelle: "Front and back side by side – ideal for checking the translations",
  h_nav_verbesserung: "Enhance images in advance and compare before/after", h_nav_bild: "Step 1: add new images – one or a whole bunch",
  h_nav_beschriften: "Step 2: enter the {zs} word for the back", h_nav_ideen: "Park half-finished ideas and finish them later at your own pace",
  h_neue_karte: "Get started with a new image (step 1)", h_ie_knopf: "Back up, share or read in cards and ideas",
  h_bearbeiten: "Change the word, text, note and image of this card", h_entfernen: "Takes the card off the list – the image stays in the folder, “Undo” brings it back",
  h_marke_bild_fehlt: "The image file is not in the bilder/ folder – without an image the card isn’t printed",
  h_marke_es_fehlt: "Enter the {zs} word in step 2 – then the card is ready to print",
  h_marke_geprueft: "You ticked this translation as checked in the table – exemplary!",
  h_marke_aus: "The “Print” switch is off: the card stays in the list but isn’t added to the print files",
  h_marke_text: "The word doesn’t quite fit on the back yet – write it shorter or break it with “|”",
  h_text_auf_bild: "Shown on the front and used for the file name", h_alle_uebernehmen: "Takes over all images that are ready (green ✓)",
  h_alle_uebersetzen: "Suggests a translation for every card without a {zs} word – you check afterwards",
  h_uebernehmen: "Creates the card: the image goes to bilder/, the card into the card list", h_details: "Original, preview, rotation, crop and all checks",
  h_verwerfen: "Don’t take over this new image after all", h_ersetzen: "Replaces the existing image with the same name – the old version goes to bilder/_entfernt/",
  h_fit_contain: "Shows the whole image; empty margins are softly continued", h_fit_cover: "Fills the whole card; overhanging edges are cropped",
  h_de_feld: "What the image says – helps with checking and on the proof sheet", h_notiz: "Just for you, e.g. the word type – not printed",
  h_zeichen: "Inserts the character at the cursor", h_spaeter: "Skip this card for now – it waits here patiently for you",
  h_karte_speichern: "Saves word, text and note – clickable as soon as all checks pass", h_alle_speichern: "Saves all cards that are ready",
  h_bild_entfernen: "Takes the new image out again (it goes to bilder/_entfernt/)",
  h_bild_aendern: "Choose a new image for this card – or just drag it onto the preview. Word, text and note stay",
  h_ki_editor: "Create a new, realistic goose image for this card – offline. Word, text and note stay",
  h_ki_uebersetzen: "Sends only this description to the translation service (MyMemory or DeepL) – only with translation switched on",
  h_ersatz_uebernehmen: "Replaces the card’s image – the previous one is kept in bilder/_entfernt/, “Undo” brings it back",
  h_ersatz_verwerfen: "Don’t use the new image – the card stays as it is",
  h_idee_neu: "Create an empty idea – an image or a word is enough to start", h_idee_bild: "Choose an image for this idea – or just drag it here",
  h_idee_gestalten: "Turn a goose photo into an image with “GANS + word”", h_idee_es: "The word for the back – 🌐 suggests one", h_es_feld: "The word in Spanish for the back – always meaning Spanish as spoken in Mexico",
  h_idee_aufnehmen: "Turns the finished idea into a card under “My cards” (needs image, text and word)", h_idee_weg: "Discard this idea",
  h_unfertig_weiter: "Opens this card right where it continues",
});
Object.assign(TXT.es, {
  h_nav_karten: "Todas tus cartas: voltear, ordenar, editar, pausar", h_nav_tabelle: "Anverso y reverso lado a lado, ideal para revisar las traducciones",
  h_nav_verbesserung: "Mejorar imágenes por adelantado y comparar antes/después", h_nav_bild: "Paso 1: agregar imágenes nuevas, una o muchas",
  h_nav_beschriften: "Paso 2: escribir la palabra en {zs} para el reverso", h_nav_ideen: "Guardar ideas a medias y terminarlas después con calma",
  h_neue_karte: "Empezar con una imagen nueva (paso 1)", h_ie_knopf: "Respaldar, compartir o importar cartas e ideas",
  h_bearbeiten: "Cambiar la palabra, el texto, la nota y la imagen de esta carta", h_entfernen: "Quita la carta de la lista; la imagen se queda en la carpeta y «Deshacer» la devuelve",
  h_marke_bild_fehlt: "El archivo de imagen no está en la carpeta bilder/; sin imagen la carta no se imprime",
  h_marke_es_fehlt: "Escribe la palabra en {zs} en el paso 2 y la carta queda lista para imprimir",
  h_marke_geprueft: "Marcaste esta traducción como revisada en la tabla. ¡Ejemplar!",
  h_marke_aus: "El interruptor «Imprimir» está apagado: la carta sigue en la lista, pero no entra en los archivos de impresión",
  h_marke_text: "La palabra todavía no cabe del todo en el reverso; escríbela más corta o divídela con «|»",
  h_text_auf_bild: "Aparece en el anverso y da nombre al archivo", h_alle_uebernehmen: "Toma todas las imágenes listas (✓ verde)",
  h_alle_uebersetzen: "Sugiere una traducción para cada carta sin palabra en {zs}; luego tú la revisas",
  h_uebernehmen: "Crea la carta: la imagen va a bilder/ y la carta a la lista", h_details: "Original, vista previa, girar, recorte y todas las revisiones",
  h_verwerfen: "Al final no tomar esta imagen nueva", h_ersetzen: "Reemplaza la imagen existente con el mismo nombre; la versión anterior va a bilder/_entfernt/",
  h_fit_contain: "Muestra la imagen completa; los márgenes libres se continúan suavemente", h_fit_cover: "Llena toda la carta; los bordes sobrantes se recortan",
  h_de_feld: "Lo que dice la imagen; ayuda al revisar y en la hoja de control", h_notiz: "Solo para ti, p. ej. el tipo de palabra; no se imprime",
  h_zeichen: "Inserta el carácter donde está el cursor", h_spaeter: "Saltar esta carta por ahora; aquí te espera con paciencia",
  h_karte_speichern: "Guarda palabra, texto y nota; se activa cuando todas las revisiones pasan", h_alle_speichern: "Guarda todas las cartas listas",
  h_bild_entfernen: "Quita otra vez la imagen nueva (va a bilder/_entfernt/)",
  h_bild_aendern: "Elige una imagen nueva para esta carta, o simplemente arrástrala sobre la vista previa. La palabra, el texto y la nota se quedan",
  h_ki_editor: "Crear una imagen nueva y realista de ganso para esta carta, sin conexión. La palabra, el texto y la nota se quedan",
  h_ki_uebersetzen: "Envía solo esta descripción al servicio de traducción (MyMemory o DeepL), solo con la traducción activada",
  h_ersatz_uebernehmen: "Reemplaza la imagen de la carta; la anterior se guarda en bilder/_entfernt/ y «Deshacer» la devuelve",
  h_ersatz_verwerfen: "No usar la imagen nueva; la carta se queda como está",
  h_idee_neu: "Crear una idea vacía; para empezar basta una imagen o una palabra", h_idee_bild: "Elegir una imagen para esta idea, o simplemente arrastrarla aquí",
  h_idee_gestalten: "Convertir una foto de ganso en una imagen con «GANS + palabra»", h_idee_es: "La palabra para el reverso; 🌐 te sugiere una", h_es_feld: "La palabra en español para el reverso; siempre el español que se habla en México",
  h_idee_aufnehmen: "Convierte la idea terminada en una carta en «Mis cartas» (necesita imagen, texto y palabra)", h_idee_weg: "Descartar esta idea",
  h_unfertig_weiter: "Abre esta carta justo donde sigue",
});
// Hovertexte: Erzeugen, Prüfen & drucken, Werkzeuge, Hilfe, Deinstallieren
Object.assign(TXT.de, {
  h_nav_erzeugen: "Schritt 3: Druckdateien oder digitale Lernkarten erzeugen", h_nav_pruefen: "Schritt 4: Prüfbogen ansehen und drucken – fast geschafft!",
  h_nav_werkzeuge: "Tools (Bildverbesserung, Übersetzung, KI-Bilder), Selbsttest, Sicherung, Handy-Zugang und Ordner", h_nav_hilfe: "Anleitung Schritt für Schritt und technische Angaben",
  h_befehl: "Zeigt, wie dieser Lauf in der Befehlszeile aussähe – nur für Neugierige", h_kopieren: "Befehl in die Zwischenablage kopieren",
  h_ausgabe_oeffnen: "Öffnet den Ordner mit allen Druckdateien", h_lauf_stopp: "Lauf anhalten – schon fertige Bilder bleiben erhalten",
  h_pruefbogen_oeffnen: "Öffnet den Prüfbogen – ein kurzer Blick lohnt sich", h_zu_schritt4: "Weiter zum Prüfen und Drucken",
  h_zur_verbesserung: "Zur Bildverbesserung mit Vorher/Nachher-Vergleich", h_zur_tabelle: "Zur Tabelle – dort hakst du geprüfte Übersetzungen ab",
  h_einzelbilder: "Öffnet den Ordner mit einem PNG je Kartenseite – für Druckereien mit Bild-Upload",
  h_digital_knopf: "Wechselt zu Erzeugen mit dem Ziel „Digital lernen“", h_pr_finden: "Tipps, worauf du bei einer Druckerei achten solltest",
  h_lauf_details: "Was der letzte Lauf erzeugt hat – mit allen Hinweisen", h_vorlagen: "Leere Vorlagen mit Hilfslinien für eigene Gestaltung",
  h_tab_leitfaden: "Die Anleitung: vom Foto bis zur fertigen Karte", h_tab_spec: "Alle technischen Details für Profis", h_tab_ueber: "Versionen, Bildverbesserung und Ordner dieses Programms",
  h_gans_laden: "Eigenes Bild für die Rückseiten wählen", h_gans_weg: "Wieder die gezeichnete Gans verwenden", h_gans_zurueck: "Das vorige Gänse-Bild zurückholen",
  h_ue_cache: "Vergisst gemerkte Vorschläge – beim nächsten Mal wird neu gefragt", h_ue_deepl: "Schlüssel speichern – er bleibt nur auf diesem Rechner",
  h_ue_deepl_weg: "Gespeicherten DeepL-Schlüssel löschen",
  h_de_doch_nicht: "Alles bleibt, wie es ist – schön, dass du bleibst!", h_de_los: "Entfernt alles Aufgeführte – erst nach dem Häkchen klickbar",
});
Object.assign(TXT.en, {
  h_nav_erzeugen: "Step 3: generate print files or digital flashcards", h_nav_pruefen: "Step 4: look at the proof sheet and print – almost there!",
  h_nav_werkzeuge: "Optional tools (image enhancement, translation, AI images), self-test, backup, phone access and folders", h_nav_hilfe: "Step-by-step guide and technical details",
  h_befehl: "Shows what this run would look like on the command line – just for the curious", h_kopieren: "Copy the command to the clipboard",
  h_ausgabe_oeffnen: "Opens the folder with all print files", h_lauf_stopp: "Stop the run – images that are already done are kept",
  h_pruefbogen_oeffnen: "Opens the proof sheet – a quick look is worth it", h_zu_schritt4: "On to checking and printing",
  h_zur_verbesserung: "To image enhancement with before/after comparison", h_zur_tabelle: "To the table – tick off checked translations there",
  h_einzelbilder: "Opens the folder with one PNG per card side – for print shops with image upload",
  h_digital_knopf: "Switches to Generate with the goal “Learn digitally”", h_pr_finden: "Tips on what to look for in a print shop",
  h_lauf_details: "What the last run produced – with all notes", h_vorlagen: "Blank templates with guides for your own designs",
  h_tab_leitfaden: "The guide: from photo to finished card", h_tab_spec: "All technical details for pros", h_tab_ueber: "Versions, image enhancement and folders of this program",
  h_gans_laden: "Choose your own image for the backs", h_gans_weg: "Use the drawn goose again", h_gans_zurueck: "Bring back the previous goose image",
  h_ue_cache: "Forgets remembered suggestions – next time it asks again", h_ue_deepl: "Save the key – it stays on this computer only",
  h_ue_deepl_weg: "Delete the saved DeepL key",
  h_de_doch_nicht: "Everything stays as it is – glad you’re staying!", h_de_los: "Removes everything listed – clickable only after the tick",
});
Object.assign(TXT.es, {
  h_nav_erzeugen: "Paso 3: generar archivos de impresión o tarjetas digitales", h_nav_pruefen: "Paso 4: revisar la hoja de control e imprimir. ¡Ya casi!",
  h_nav_werkzeuge: "Herramientas opcionales (mejora de imagen, traducción, imágenes IA), autoprueba, respaldo, acceso desde el celular y carpetas", h_nav_hilfe: "Guía paso a paso y datos técnicos",
  h_befehl: "Muestra cómo se vería esta ejecución en la línea de comandos; solo para curiosos", h_kopieren: "Copiar el comando al portapapeles",
  h_ausgabe_oeffnen: "Abre la carpeta con todos los archivos de impresión", h_lauf_stopp: "Detener la ejecución; las imágenes ya listas se conservan",
  h_pruefbogen_oeffnen: "Abre la hoja de control; vale la pena echarle un vistazo", h_zu_schritt4: "Sigue con revisar e imprimir",
  h_zur_verbesserung: "A la mejora de imagen con comparación antes/después", h_zur_tabelle: "A la tabla; ahí marcas las traducciones revisadas",
  h_einzelbilder: "Abre la carpeta con un PNG por cada lado de carta, para imprentas que piden imágenes",
  h_digital_knopf: "Cambia a Generar con el objetivo «Aprender en digital»", h_pr_finden: "Consejos sobre qué fijarte en una imprenta",
  h_lauf_details: "Lo que generó la última ejecución, con todos los avisos", h_vorlagen: "Plantillas vacías con guías para tus propios diseños",
  h_tab_leitfaden: "La guía: de la foto a la carta terminada", h_tab_spec: "Todos los detalles técnicos para expertos", h_tab_ueber: "Versiones, mejora de imagen y carpetas de este programa",
  h_gans_laden: "Elegir una imagen propia para los reversos", h_gans_weg: "Volver a usar el ganso dibujado", h_gans_zurueck: "Recuperar la imagen de ganso anterior",
  h_ue_cache: "Olvida las sugerencias guardadas; la próxima vez pregunta de nuevo", h_ue_deepl: "Guardar la clave; se queda solo en esta computadora",
  h_ue_deepl_weg: "Borrar la clave de DeepL guardada",
  h_de_doch_nicht: "Todo se queda como está. ¡Qué bien que te quedas!", h_de_los: "Quita todo lo mencionado; solo se activa tras marcar la casilla",
});
if (!TXT[S.sprache]) S.sprache = "en";
const $ = (sel, el = document) => el.querySelector(sel);
const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];
const esc = t => String(t ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
// Karten lernen (Tool „lernen“): Reiter „🎓 Lernen“, Sitzung, Lernstand in „Meine Karten“ – Texte in allen drei Sprachen
Object.assign(TXT.de, {
  nav_lernen: "Lernen", h_nav_lernen: "Karten lernen mit verteilter Wiederholung (FSRS) – die Zahl zeigt, was heute dran ist",
  ln_titel: "Karten lernen", ln_unter: "Erst erinnern, dann umdrehen: Jede Karte kommt genau dann wieder, wenn du sie sonst bald vergessen würdest.",
  ln_aus_titel: "Karten lernen ist noch nicht aktiviert",
  ln_aus_text: "Mit dem Tool „Karten lernen“ übst du deine Karten wie mit Anki – das Programm merkt sich, wie gut du jede Karte kannst, und plant die nächste Wiederholung. Es wird nichts heruntergeladen, aktivieren genügt.",
  ln_aktivieren: "Karten lernen aktivieren",
  ln_heute: (f, n) => `Heute: ${f} ${f === 1 ? "Wiederholung" : "Wiederholungen"} · ${n} neue`,
  ln_los: "Los geht’s", ln_fertig_heute: "Für heute alles gelernt – gans stark!",
  ln_serie: n => n ? `Gänsemarsch: ${n} ${n === 1 ? "Tag" : "Tage"} in Folge` : "Gänsemarsch: Heute ist ein guter Tag zum Starten",
  ln_stapel_titel: "Stapel", ln_alle: "Alle aktiven Karten", ln_alle_text: "jede aktive Karte mit Wort in der Lernsprache",
  ln_stapel_zahlen: (f, n) => `${f} fällig · ${n} neu`, ln_lernen_knopf: "Lernen", ln_stapel_neu: "Neuer Stapel …",
  h_ln_stapel_neu: "Eigenen Stapel anlegen – nach Sprache, Notiz, Suchtext oder per Häkchen-Auswahl",
  h_ln_stapel_bearbeiten: "Stapel bearbeiten", h_ln_stapel_loeschen: "Stapel löschen (die Karten und ihr Lernstand bleiben)",
  ln_stapel_geloescht: n => `Stapel „${n}“ gelöscht.`,
  ln_stat_titel: "Statistik", ln_heute_gelernt: (n, m) => `Heute gelernt: ${n} ${n === 1 ? "Karte" : "Karten"} · ${m} Min`,
  ln_woche_titel: "Fällig in den nächsten 7 Tagen", ln_heute_kurz: "Heute", ln_zustaende: "Lernstand der Karten",
  ln_z_neu: "neu", ln_z_lernt: "lernt", ln_z_jung: "jung", ln_z_sicher: "sicher",
  h_ln_zustaende: "Neu = noch nie gelernt · lernt = in den ersten Lernschritten · jung = Abstand unter 21 Tagen · sicher = 21 Tage und mehr",
  ln_quote: (p, n) => `Behaltensquote (30 Tage): ${p} % von ${n} Wiederholungen`,
  ln_quote_leer: "Behaltensquote: noch keine Wiederholungen in den letzten 30 Tagen",
  ln_problem: n => `${n} ${n === 1 ? "Problemkarte" : "Problemkarten"} (oft vergessen)`, ln_problem_knopf: "Ansehen",
  ln_einst_titel: "Einstellungen", ln_neu_tag: "Neue Karten pro Tag", ln_wdh_tag: "Wiederholungen pro Tag (höchstens)",
  ln_quote_ziel: "Gewünschte Behaltensquote",
  ln_quote_erkl: "So sicher sollst du eine Karte noch wissen, wenn sie wiederkommt. 90 % ist der bewährte Standard – höher heißt öfter wiederholen, niedriger weniger Arbeit, aber mehr Vergessen.",
  ln_richtung: "Richtung", ln_r_vorwaerts: "Bild → Wort", ln_r_rueckwaerts: "Wort → Bild", ln_r_beide: "Beide Richtungen",
  ln_sprache: "Lernsprache", ln_sprache_auto: "Wie die Rückseite ({zs})", ln_wechsel: "Neuer Lerntag beginnt um",
  ln_speichern: "Einstellungen speichern", ln_gespeichert: "Gespeichert – die Gans plant neu.",
  ln_daten_titel: "Lernstand sichern", ln_export: "Lernstand exportieren", h_ln_export: "Lernstand als JSON-Datei speichern (z. B. für einen anderen Rechner)",
  ln_import: "Lernstand importieren …", h_ln_import: "Exportierten Lernstand dazunehmen – je Karte gilt der neuere Stand",
  ln_importiert: (k, s) => `Übernommen: ${k} Lernkarten, ${s} Stapel.`,
  ln_reset: "Alles zurücksetzen …", ln_reset_frage: "Wirklich den ganzen Lernstand löschen? Karten, Stapel und Einstellungen bleiben.",
  ln_reset_ja: "Ja, von vorn beginnen", ln_reset_nein: "Lieber nicht", ln_reset_ok: n => `Lernstand zurückgesetzt (${n} Lernkarten) – frisch wie ein Gänseküken.`,
  ln_export_vorher: "Lernstand vorher exportieren",
  ln_frage_v: name => `Wie heißt das auf ${name}?`, ln_frage_r: "Welches Bild gehört zu diesem Wort?",
  ln_zeigen: "Antwort zeigen", h_ln_zeigen: "Antwort zeigen (Leertaste oder auf die Karte tippen)",
  ln_n1: "Nochmal", ln_n2: "Schwer", ln_n3: "Gut", ln_n4: "Einfach", h_ln_noten: "Bewerten: wie gut wusstest du es? (Tasten 1–4)",
  ln_rueck: "Rückgängig", h_ln_rueck: "Letzte Bewertung zurücknehmen (Strg+Z)", ln_rueck_ok: "Zurückgenommen – die Karte kommt noch einmal.",
  ln_beenden: "Beenden", h_ln_beenden: "Lernen beenden – jede Bewertung ist schon gespeichert",
  h_ln_vorlesen: "Vorlesen (Stimme deines Systems, offline)",
  ln_zaehler: (n, l, w) => `${n} neu · ${l} lernen · ${w} wiederholen`,
  ln_tasten: "Tastatur: Leertaste = Antwort zeigen · 1–4 = bewerten · Strg+Z = rückgängig · Esc = beenden",
  ln_tasten_touch: "Karte antippen = Antwort zeigen · nach rechts wischen = Gut, nach links = Nochmal (↶ nimmt es zurück)",
  ln_problem_hinweis: "Diese Karte ist eine Problemkarte – sie wurde schon oft vergessen. Vielleicht helfen ein deutlicheres Bild oder eine Notiz?",
  ln_karte_bearbeiten: "Karte bearbeiten",
  ln_fertig_titel: "Geschafft – gans großartig!", ln_fertig_text: n => `${n} ${n === 1 ? "Bewertung" : "Bewertungen"} in dieser Runde. Alles ist gespeichert.`,
  ln_nichts_titel: "Gerade nichts zu lernen", ln_nichts_text: "In diesem Stapel ist gerade nichts fällig. Neue Karten mit Wort in der Lernsprache kommen automatisch dazu.",
  ln_morgen: n => `Morgen fällig: ${n}`, ln_naechster: m => `Nächster Lernschritt in ${m} Min – dann einfach noch einmal „Lernen“.`,
  ln_zurueck_uebersicht: "Zur Übersicht",
  ln_filter: "Nach Lernstand filtern", ln_filter_alle: "Alle", ln_filter_faellig: "Fällig", ln_filter_neu: "Neu", ln_filter_sicher: "Sicher",
  ln_filter_problem: "Problemkarten", ln_filter_leer: "Keine Karte passt zu diesem Filter.",
  ln_auswahl: "Auswählen", h_ln_auswahl: "Karten ankreuzen, um sie gleich zu lernen oder in einen Stapel zu legen",
  ln_auswahl_n: n => `${n} ausgewählt`, ln_jetzt_lernen: "Jetzt lernen", ln_zum_stapel: "Zum Stapel …", ln_auswahl_fertig: "Fertig",
  ln_auswahl_stapel: "Aktuelle Auswahl", ln_auswahl_leer: "Kreuze zuerst mindestens eine Karte an.",
  h_ln_marke: (a, tage) => a ? `${a}× gelernt, nächste Wiederholung ${tage == null || tage <= 0 ? "heute" : tage === 1 ? "morgen" : `in ${tage} Tagen`}` : "Noch nicht gelernt",
  ln_problem_kurz: "Problemkarte",
  ln_st_titel_neu: "Neuer Stapel", ln_st_titel_bearbeiten: "Stapel bearbeiten", ln_st_name: "Name", ln_st_name_ph: "z. B. Tiere am Teich",
  ln_st_ziel: "Hinzufügen zu", ln_st_ziel_neu: "einem neuen Stapel", ln_st_notiz: "Notiz enthält", ln_st_suche: "Suchtext (Deutsch oder Wort)",
  ln_st_nur: "Nur", ln_nur_: "alle Karten", ln_nur_neu: "neue Karten", ln_nur_faellig: "fällige Karten", ln_nur_problem: "Problemkarten",
  ln_st_auswahl: "Nur angekreuzte Karten", ln_st_auswahl_n: n => `${n} Karten angekreuzt`, ln_st_alle_an: "Alle", ln_st_alle_aus: "Keine",
  ln_st_speichern: "Stapel speichern", ln_st_gespeichert: n => `Stapel „${n}“ gespeichert.`,
  ln_hinweis_speichern: "Speichern setzt den Lernstand dieser Karte zurück – sie startet beim Lernen frisch.",
});
Object.assign(TXT.en, {
  nav_lernen: "Learn", h_nav_lernen: "Learn your cards with spaced repetition (FSRS) – the number shows what is due today",
  ln_titel: "Learn cards", ln_unter: "Recall first, then flip: every card comes back right before you would otherwise forget it.",
  ln_aus_titel: "Learning cards is not switched on yet",
  ln_aus_text: "With the “Learn cards” tool you practise your cards like in Anki – the program remembers how well you know each card and schedules the next review. Nothing is downloaded, switching it on is enough.",
  ln_aktivieren: "Switch on learning",
  ln_heute: (f, n) => `Today: ${f} ${f === 1 ? "review" : "reviews"} · ${n} new`,
  ln_los: "Let’s go", ln_fertig_heute: "All done for today – absolutely goose-tastic!",
  ln_serie: n => n ? `Goose march: ${n} ${n === 1 ? "day" : "days"} in a row` : "Goose march: today is a great day to start",
  ln_stapel_titel: "Decks", ln_alle: "All active cards", ln_alle_text: "every active card with a word in the learning language",
  ln_stapel_zahlen: (f, n) => `${f} due · ${n} new`, ln_lernen_knopf: "Learn", ln_stapel_neu: "New deck …",
  h_ln_stapel_neu: "Create your own deck – by language, note, search text or by ticking cards",
  h_ln_stapel_bearbeiten: "Edit deck", h_ln_stapel_loeschen: "Delete deck (the cards and their progress stay)",
  ln_stapel_geloescht: n => `Deck “${n}” deleted.`,
  ln_stat_titel: "Statistics", ln_heute_gelernt: (n, m) => `Learned today: ${n} ${n === 1 ? "card" : "cards"} · ${m} min`,
  ln_woche_titel: "Due in the next 7 days", ln_heute_kurz: "Today", ln_zustaende: "Card progress",
  ln_z_neu: "new", ln_z_lernt: "learning", ln_z_jung: "young", ln_z_sicher: "mature",
  h_ln_zustaende: "New = never learned · learning = in the first learning steps · young = interval under 21 days · mature = 21 days or more",
  ln_quote: (p, n) => `Retention (30 days): ${p} % of ${n} reviews`,
  ln_quote_leer: "Retention: no reviews in the last 30 days yet",
  ln_problem: n => `${n} ${n === 1 ? "problem card" : "problem cards"} (often forgotten)`, ln_problem_knopf: "Show",
  ln_einst_titel: "Settings", ln_neu_tag: "New cards per day", ln_wdh_tag: "Reviews per day (maximum)",
  ln_quote_ziel: "Desired retention",
  ln_quote_erkl: "How sure you should still be about a card when it comes back. 90 % is the proven default – higher means more reviews, lower means less work but more forgetting.",
  ln_richtung: "Direction", ln_r_vorwaerts: "Picture → word", ln_r_rueckwaerts: "Word → picture", ln_r_beide: "Both directions",
  ln_sprache: "Learning language", ln_sprache_auto: "Same as the back ({zs})", ln_wechsel: "A new learning day starts at",
  ln_speichern: "Save settings", ln_gespeichert: "Saved – the goose is re-planning.",
  ln_daten_titel: "Back up progress", ln_export: "Export progress", h_ln_export: "Save the learning progress as a JSON file (e.g. for another computer)",
  ln_import: "Import progress …", h_ln_import: "Add an exported progress file – for each card the newer state wins",
  ln_importiert: (k, s) => `Taken over: ${k} learning cards, ${s} decks.`,
  ln_reset: "Reset everything …", ln_reset_frage: "Really delete all learning progress? Cards, decks and settings stay.",
  ln_reset_ja: "Yes, start over", ln_reset_nein: "Better not", ln_reset_ok: n => `Progress reset (${n} learning cards) – fresh as a gosling.`,
  ln_export_vorher: "Export progress first",
  ln_frage_v: name => `What is this in ${name}?`, ln_frage_r: "Which picture goes with this word?",
  ln_zeigen: "Show answer", h_ln_zeigen: "Show the answer (space bar or tap the card)",
  ln_n1: "Again", ln_n2: "Hard", ln_n3: "Good", ln_n4: "Easy", h_ln_noten: "Rate it: how well did you know it? (keys 1–4)",
  ln_rueck: "Undo", h_ln_rueck: "Take back the last rating (Ctrl+Z)", ln_rueck_ok: "Taken back – the card comes once more.",
  ln_beenden: "Finish", h_ln_beenden: "Stop learning – every rating is already saved",
  h_ln_vorlesen: "Read aloud (your system’s voice, offline)",
  ln_zaehler: (n, l, w) => `${n} new · ${l} learning · ${w} to review`,
  ln_tasten: "Keyboard: space = show answer · 1–4 = rate · Ctrl+Z = undo · Esc = finish",
  ln_tasten_touch: "Tap the card = show answer · swipe right = Good, left = Again (↶ takes it back)",
  ln_problem_hinweis: "This is a problem card – it has been forgotten many times. Maybe a clearer picture or a note would help?",
  ln_karte_bearbeiten: "Edit card",
  ln_fertig_titel: "Done – goose-tastic work!", ln_fertig_text: n => `${n} ${n === 1 ? "rating" : "ratings"} this round. Everything is saved.`,
  ln_nichts_titel: "Nothing to learn right now", ln_nichts_text: "Nothing in this deck is due right now. New cards with a word in the learning language are added automatically.",
  ln_morgen: n => `Due tomorrow: ${n}`, ln_naechster: m => `Next learning step in ${m} min – then simply “Learn” once more.`,
  ln_zurueck_uebersicht: "Back to overview",
  ln_filter: "Filter by progress", ln_filter_alle: "All", ln_filter_faellig: "Due", ln_filter_neu: "New", ln_filter_sicher: "Mature",
  ln_filter_problem: "Problem cards", ln_filter_leer: "No card matches this filter.",
  ln_auswahl: "Select", h_ln_auswahl: "Tick cards to learn them right away or put them into a deck",
  ln_auswahl_n: n => `${n} selected`, ln_jetzt_lernen: "Learn now", ln_zum_stapel: "Add to deck …", ln_auswahl_fertig: "Done",
  ln_auswahl_stapel: "Current selection", ln_auswahl_leer: "Tick at least one card first.",
  h_ln_marke: (a, tage) => a ? `Learned ${a}×, next review ${tage == null || tage <= 0 ? "today" : tage === 1 ? "tomorrow" : `in ${tage} days`}` : "Not learned yet",
  ln_problem_kurz: "Problem card",
  ln_st_titel_neu: "New deck", ln_st_titel_bearbeiten: "Edit deck", ln_st_name: "Name", ln_st_name_ph: "e.g. Pond animals",
  ln_st_ziel: "Add to", ln_st_ziel_neu: "a new deck", ln_st_notiz: "Note contains", ln_st_suche: "Search text (German or word)",
  ln_st_nur: "Only", ln_nur_: "all cards", ln_nur_neu: "new cards", ln_nur_faellig: "due cards", ln_nur_problem: "problem cards",
  ln_st_auswahl: "Only ticked cards", ln_st_auswahl_n: n => `${n} cards ticked`, ln_st_alle_an: "All", ln_st_alle_aus: "None",
  ln_st_speichern: "Save deck", ln_st_gespeichert: n => `Deck “${n}” saved.`,
  ln_hinweis_speichern: "Saving resets the learning progress of this card – it starts fresh when learning.",
});
Object.assign(TXT.es, {
  nav_lernen: "Aprender", h_nav_lernen: "Aprende tus cartas con repaso espaciado (FSRS); el número muestra lo que toca hoy",
  ln_titel: "Aprender cartas", ln_unter: "Primero recuerda, luego voltea: cada carta vuelve justo antes de que la olvides.",
  ln_aus_titel: "Aprender cartas todavía no está activado",
  ln_aus_text: "Con la herramienta «Aprender cartas» practicas tus cartas como en Anki: el programa recuerda qué tan bien conoces cada carta y planea el siguiente repaso. No se descarga nada; basta con activarla.",
  ln_aktivieren: "Activar Aprender cartas",
  ln_heute: (f, n) => `Hoy: ${f} ${f === 1 ? "repaso" : "repasos"} · ${n} nuevas`,
  ln_los: "¡Vamos!", ln_fertig_heute: "¡Todo aprendido por hoy, ganso campeón!",
  ln_serie: n => n ? `Marcha de gansos: ${n} ${n === 1 ? "día" : "días"} seguidos` : "Marcha de gansos: hoy es un buen día para empezar",
  ln_stapel_titel: "Mazos", ln_alle: "Todas las cartas activas", ln_alle_text: "cada carta activa con palabra en el idioma de aprendizaje",
  ln_stapel_zahlen: (f, n) => `${f} pendientes · ${n} nuevas`, ln_lernen_knopf: "Aprender", ln_stapel_neu: "Nuevo mazo …",
  h_ln_stapel_neu: "Crea tu propio mazo: por idioma, nota, texto de búsqueda o marcando cartas",
  h_ln_stapel_bearbeiten: "Editar mazo", h_ln_stapel_loeschen: "Borrar mazo (las cartas y su progreso se quedan)",
  ln_stapel_geloescht: n => `Mazo «${n}» borrado.`,
  ln_stat_titel: "Estadísticas", ln_heute_gelernt: (n, m) => `Aprendido hoy: ${n} ${n === 1 ? "carta" : "cartas"} · ${m} min`,
  ln_woche_titel: "Pendientes en los próximos 7 días", ln_heute_kurz: "Hoy", ln_zustaende: "Progreso de las cartas",
  ln_z_neu: "nueva", ln_z_lernt: "aprendiendo", ln_z_jung: "joven", ln_z_sicher: "segura",
  h_ln_zustaende: "Nueva = nunca aprendida · aprendiendo = en los primeros pasos · joven = intervalo menor a 21 días · segura = 21 días o más",
  ln_quote: (p, n) => `Retención (30 días): ${p} % de ${n} repasos`,
  ln_quote_leer: "Retención: todavía no hay repasos en los últimos 30 días",
  ln_problem: n => `${n} ${n === 1 ? "carta difícil" : "cartas difíciles"} (olvidadas seguido)`, ln_problem_knopf: "Ver",
  ln_einst_titel: "Ajustes", ln_neu_tag: "Cartas nuevas por día", ln_wdh_tag: "Repasos por día (máximo)",
  ln_quote_ziel: "Retención deseada",
  ln_quote_erkl: "Qué tan seguro debes estar de una carta cuando vuelva. 90 % es el valor probado: más alto significa repasar más seguido; más bajo, menos trabajo pero más olvido.",
  ln_richtung: "Dirección", ln_r_vorwaerts: "Imagen → palabra", ln_r_rueckwaerts: "Palabra → imagen", ln_r_beide: "Ambas direcciones",
  ln_sprache: "Idioma de aprendizaje", ln_sprache_auto: "Igual que el reverso ({zs})", ln_wechsel: "El nuevo día de aprendizaje empieza a las",
  ln_speichern: "Guardar ajustes", ln_gespeichert: "Guardado: el ganso vuelve a planear.",
  ln_daten_titel: "Respaldar progreso", ln_export: "Exportar progreso", h_ln_export: "Guarda el progreso como archivo JSON (p. ej. para otra computadora)",
  ln_import: "Importar progreso …", h_ln_import: "Agrega un progreso exportado; en cada carta gana el estado más reciente",
  ln_importiert: (k, s) => `Tomado: ${k} cartas de aprendizaje, ${s} mazos.`,
  ln_reset: "Reiniciar todo …", ln_reset_frage: "¿De verdad borrar todo el progreso? Las cartas, los mazos y los ajustes se quedan.",
  ln_reset_ja: "Sí, empezar de nuevo", ln_reset_nein: "Mejor no", ln_reset_ok: n => `Progreso reiniciado (${n} cartas): fresco como un ansarino.`,
  ln_export_vorher: "Exportar el progreso antes",
  ln_frage_v: name => `¿Cómo se dice en ${name.toLowerCase()}?`, ln_frage_r: "¿Qué imagen va con esta palabra?",
  ln_zeigen: "Mostrar respuesta", h_ln_zeigen: "Mostrar la respuesta (barra espaciadora o toca la carta)",
  ln_n1: "Otra vez", ln_n2: "Difícil", ln_n3: "Bien", ln_n4: "Fácil", h_ln_noten: "Califica: ¿qué tan bien lo sabías? (teclas 1–4)",
  ln_rueck: "Deshacer", h_ln_rueck: "Deshacer la última calificación (Ctrl+Z)", ln_rueck_ok: "Deshecho: la carta vuelve una vez más.",
  ln_beenden: "Terminar", h_ln_beenden: "Terminar de aprender; cada calificación ya está guardada",
  h_ln_vorlesen: "Leer en voz alta (voz de tu sistema, sin internet)",
  ln_zaehler: (n, l, w) => `${n} nuevas · ${l} aprendiendo · ${w} por repasar`,
  ln_tasten: "Teclado: espacio = mostrar respuesta · 1–4 = calificar · Ctrl+Z = deshacer · Esc = terminar",
  ln_tasten_touch: "Toca la carta = mostrar respuesta · desliza a la derecha = Bien, a la izquierda = Otra vez (↶ lo deshace)",
  ln_problem_hinweis: "Esta es una carta difícil: ya se olvidó muchas veces. ¿Quizá ayude una imagen más clara o una nota?",
  ln_karte_bearbeiten: "Editar carta",
  ln_fertig_titel: "¡Listo, trabajo de ganso campeón!", ln_fertig_text: n => `${n} ${n === 1 ? "calificación" : "calificaciones"} en esta ronda. Todo está guardado.`,
  ln_nichts_titel: "Nada que aprender por ahora", ln_nichts_text: "En este mazo no hay nada pendiente por ahora. Las cartas nuevas con palabra en el idioma de aprendizaje se agregan solas.",
  ln_morgen: n => `Pendientes mañana: ${n}`, ln_naechster: m => `Siguiente paso de aprendizaje en ${m} min; entonces solo vuelve a «Aprender».`,
  ln_zurueck_uebersicht: "Volver al resumen",
  ln_filter: "Filtrar por progreso", ln_filter_alle: "Todas", ln_filter_faellig: "Pendientes", ln_filter_neu: "Nuevas", ln_filter_sicher: "Seguras",
  ln_filter_problem: "Cartas difíciles", ln_filter_leer: "Ninguna carta coincide con este filtro.",
  ln_auswahl: "Seleccionar", h_ln_auswahl: "Marca cartas para aprenderlas de inmediato o ponerlas en un mazo",
  ln_auswahl_n: n => `${n} seleccionadas`, ln_jetzt_lernen: "Aprender ahora", ln_zum_stapel: "Al mazo …", ln_auswahl_fertig: "Listo",
  ln_auswahl_stapel: "Selección actual", ln_auswahl_leer: "Primero marca al menos una carta.",
  h_ln_marke: (a, tage) => a ? `Aprendida ${a}×, siguiente repaso ${tage == null || tage <= 0 ? "hoy" : tage === 1 ? "mañana" : `en ${tage} días`}` : "Todavía no aprendida",
  ln_problem_kurz: "Carta difícil",
  ln_st_titel_neu: "Nuevo mazo", ln_st_titel_bearbeiten: "Editar mazo", ln_st_name: "Nombre", ln_st_name_ph: "p. ej. Animales del estanque",
  ln_st_ziel: "Agregar a", ln_st_ziel_neu: "un mazo nuevo", ln_st_notiz: "La nota contiene", ln_st_suche: "Texto de búsqueda (alemán o palabra)",
  ln_st_nur: "Solo", ln_nur_: "todas las cartas", ln_nur_neu: "cartas nuevas", ln_nur_faellig: "cartas pendientes", ln_nur_problem: "cartas difíciles",
  ln_st_auswahl: "Solo cartas marcadas", ln_st_auswahl_n: n => `${n} cartas marcadas`, ln_st_alle_an: "Todas", ln_st_alle_aus: "Ninguna",
  ln_st_speichern: "Guardar mazo", ln_st_gespeichert: n => `Mazo «${n}» guardado.`,
  ln_hinweis_speichern: "Guardar reinicia el progreso de esta carta: empezará de nuevo al aprender.",
});
// Handy & Tablet: „antippen“ statt „klicken/ziehen“ – t() nimmt automatisch „…_touch“, wenn es den Schlüssel gibt
Object.assign(TXT.de, {
  ablage_titel_touch: "Antippen, um Bilder oder Fotos auszuwählen", gans_ziehen_touch: "", umdrehen_touch: "Antippen zum Umdrehen",
  karten_unter_touch: (g, a) => TXT.de.karten_unter(g, a).replace("Klick auf eine Karte", "Tipp eine Karte an"),
  tabelle_unter_touch: "Alle Texte nebeneinander – zum Vergleichen und Prüfen der Übersetzung. Zum Ändern einfach eine Zelle antippen; gespeichert wird beim Verlassen des Feldes.",
  verbesserung_unter_touch: "Wähle eine oder mehrere Karten aus und lass ihre Bilder schon vorab verbessern. Fertig verbesserte Bilder sind grün markiert; Antippen eines Bildes zeigt Vorher und Nachher. Beim Erzeugen werden noch fehlende Bilder ohnehin verbessert.",
  vergleich_hilfe_touch: "Schieberegler bewegen oder mit dem Finger übers Bild wischen.",
  ie_import_text_touch: "Eine exportierte ZIP-Datei (oder eine Kartenliste als CSV) wählen. Zuerst siehst du eine Vorschau – übernommen wird erst danach.",
  gw_leer_touch: "Gänse-Foto wählen",
  gw_hilfe_touch: "Bild mit dem Finger ziehen = Ausschnitt verschieben · Text ziehen = Text verschieben · Regler „Zoom“ = vergrößern",
  wk_tour_1_touch: "Gänse-Bilder auswählen – oder mit „🎨 GANS-Bild gestalten“ selbst eins bauen.",
});
Object.assign(TXT.en, {
  ablage_titel_touch: "Tap to choose images or photos", gans_ziehen_touch: "", umdrehen_touch: "Tap to flip",
  karten_unter_touch: (g, a) => TXT.en.karten_unter(g, a).replace("Click a card", "Tap a card"),
  tabelle_unter_touch: "All texts side by side – to compare and check the translation. Tap a cell to change something; it is saved when you leave the field.",
  verbesserung_unter_touch: "Select one or more cards and have their images enhanced in advance. Finished images are marked green; tap an image to see before and after. Generating enhances any missing images anyway.",
  vergleich_hilfe_touch: "Move the slider or swipe across the image with your finger.",
  ie_import_text_touch: "Choose an exported ZIP file (or a card list as CSV). You see a preview first – nothing is taken over before that.",
  gw_leer_touch: "Choose a goose photo",
  gw_hilfe_touch: "Drag the image with your finger = move the crop · drag the text = move the text · “Zoom” slider = enlarge",
  wk_tour_1_touch: "Choose goose pictures – or build one yourself with “🎨 Design a GANS image”.",
});
Object.assign(TXT.es, {
  ablage_titel_touch: "Toca para elegir imágenes o fotos", gans_ziehen_touch: "", umdrehen_touch: "Toca para voltear",
  karten_unter_touch: (g, a) => TXT.es.karten_unter(g, a).replace("Haz clic en una carta", "Toca una carta"),
  tabelle_unter_touch: "Todos los textos lado a lado, para comparar y revisar la traducción. Para cambiar algo, toca una celda; se guarda al salir del campo.",
  verbesserung_unter_touch: "Elige una o varias cartas y mejora sus imágenes por adelantado. Las imágenes listas se marcan en verde; al tocar una imagen ves el antes y el después. Al generar, las imágenes que falten se mejoran de todos modos.",
  vergleich_hilfe_touch: "Mueve el control deslizante o desliza el dedo sobre la imagen.",
  ie_import_text_touch: "Elige un ZIP exportado (o una lista de cartas en CSV). Primero ves una vista previa; nada se toma antes.",
  gw_leer_touch: "Elige una foto de ganso",
  gw_hilfe_touch: "Arrastrar la imagen con el dedo = mover el recorte · arrastrar el texto = mover el texto · control «Zoom» = ampliar",
  wk_tour_1_touch: "Elige imágenes de gansos, o crea una con «🎨 Diseñar imagen GANS».",
});
Object.assign(TXT.de, {
  fa_titel: "Farben & Darstellung",
  fa_unter: "Wähle ein Farbschema oder mische deine eigenen Farben – die Seite zeigt es sofort. Gespeichert wird erst mit „Speichern“.",
  fa_himmel: "Gänsehimmel (Standard)",
  fa_nacht: "Gänsenacht (dunkel)",
  fa_wiese: "Wiese",
  fa_kontrast: "Hoher Kontrast",
  fa_system: "Wie das System (hell/dunkel)",
  fa_eigen: "Eigene Farben",
  fa_c_hintergrund: "Hintergrund",
  fa_c_flaechen: "Flächen (Karten, Fenster)",
  fa_c_text: "Text",
  fa_c_akzent: "Akzent & Knöpfe",
  fa_c_linien: "Linien",
  fa_c_erfolg: "Erfolg (grün)",
  fa_c_fehler: "Fehler (rot)",
  fa_speichern: "Speichern",
  fa_standard: "Auf Standard zurücksetzen",
  fa_gespeichert: "Farben gespeichert – gans schön bunt!",
  fa_zurueck: "Farben stehen wieder auf Standard – gans wie vorher.",
  fa_ungespeichert: "Vorschau – noch nicht gespeichert",
  fa_eigen_hinweis: "Die Farbwähler wirken sofort als Vorschau.",
  h_farben_kachel: "Dieses Farbschema ausprobieren – die Seite ändert sich sofort",
  h_farben_speichern: "Das gewählte Farbschema dauerhaft merken",
  h_farben_standard: "Zurück zu den ursprünglichen Farben (Gänsehimmel)",
  fa_lesbar: w => `Gut lesbar (Kontrast ${w} : 1).`,
  fa_schwer: w => `Achtung: schwer lesbar – Text und Hintergrund liegen zu nah beieinander (Kontrast ${w} : 1, besser ab 4,5).`,
});
Object.assign(TXT.en, {
  fa_titel: "Colors & appearance",
  fa_unter: "Pick a color scheme or mix your own colors – the page shows it right away. Nothing is kept until you press “Save”.",
  fa_himmel: "Goose sky (default)",
  fa_nacht: "Goose night (dark)",
  fa_wiese: "Meadow",
  fa_kontrast: "High contrast",
  fa_system: "Like the system (light/dark)",
  fa_eigen: "My own colors",
  fa_c_hintergrund: "Background",
  fa_c_flaechen: "Surfaces (cards, windows)",
  fa_c_text: "Text",
  fa_c_akzent: "Accent & buttons",
  fa_c_linien: "Lines",
  fa_c_erfolg: "Success (green)",
  fa_c_fehler: "Error (red)",
  fa_speichern: "Save",
  fa_standard: "Reset to default",
  fa_gespeichert: "Colors saved – goose-ously colorful!",
  fa_zurueck: "Colors are back to default – just like before.",
  fa_ungespeichert: "Preview – not saved yet",
  fa_eigen_hinweis: "The color pickers show a live preview.",
  h_farben_kachel: "Try this color scheme – the page changes right away",
  h_farben_speichern: "Keep the chosen color scheme for good",
  h_farben_standard: "Back to the original colors (Goose sky)",
  fa_lesbar: w => `Easy to read (contrast ${w} : 1).`,
  fa_schwer: w => `Heads-up: hard to read – text and background are too close (contrast ${w} : 1, 4.5 or more is better).`,
});
Object.assign(TXT.es, {
  fa_titel: "Colores y apariencia",
  fa_unter: "Elige un esquema de color o mezcla los tuyos: la página lo muestra al instante. Nada se guarda hasta pulsar «Guardar».",
  fa_himmel: "Cielo de ganso (estándar)",
  fa_nacht: "Noche de ganso (oscuro)",
  fa_wiese: "Pradera",
  fa_kontrast: "Alto contraste",
  fa_system: "Como el sistema (claro/oscuro)",
  fa_eigen: "Mis propios colores",
  fa_c_hintergrund: "Fondo",
  fa_c_flaechen: "Superficies (cartas, ventanas)",
  fa_c_text: "Texto",
  fa_c_akzent: "Acento y botones",
  fa_c_linien: "Líneas",
  fa_c_erfolg: "Éxito (verde)",
  fa_c_fehler: "Error (rojo)",
  fa_speichern: "Guardar",
  fa_standard: "Restablecer estándar",
  fa_gespeichert: "Colores guardados: ¡un ganso de mil colores!",
  fa_zurueck: "Los colores vuelven al estándar, como antes.",
  fa_ungespeichert: "Vista previa: aún sin guardar",
  fa_eigen_hinweis: "Los selectores muestran una vista previa al instante.",
  h_farben_kachel: "Probar este esquema de color: la página cambia al instante",
  h_farben_speichern: "Guardar para siempre el esquema elegido",
  h_farben_standard: "Volver a los colores originales (Cielo de ganso)",
  fa_lesbar: w => `Se lee bien (contraste ${w} : 1).`,
  fa_schwer: w => `Atención: difícil de leer; el texto y el fondo están muy cerca (contraste ${w} : 1, mejor desde 4,5).`,
});
Object.assign(TXT.de, {
  h_rs_feld: "Das Wort auf {zs} für die Rückseite", u_kartensprache_zs: "{zs}",
  zs_wahl: "Rückseite:", h_zs_wahl: "Sprache der Rückseite – wechselt Texte, Übersetzung und das große Feld in Schritt 2",
  zs_gewechselt: "Rückseiten jetzt auf {zs} – gans schön international!",
  weitere_sprachen: (n, g) => `Weitere Sprachen (${n} von ${g} ausgefüllt)`,
  h_weitere_sprachen: "Dieselbe Karte mit Rückseiten in weiteren Sprachen – 🌐 schlägt je Sprache ein Wort vor",
  rs_ph: n => `Wort auf ${n} (freiwillig)`, spalte_rs: n => `Rückseite (${n})`,
  h_sprach_chip: (n, w) => `${n}${w ? ": " + w : ""} – klicken zeigt diese Rückseite`,
  h_sprach_chip_touch: (n, w) => `${n}${w ? ": " + w : ""} – tippen zeigt diese Rückseite`,
  sprach_chip_leer: n => `${n}: noch kein Wort`, filter_fehlt: n => `fehlt auf ${n}`,
  sp_immer: "immer dabei", sp_sofort: "ohne Download", sp_aktuell: "Rückseite jetzt", sp_als_rueckseite: "Als Rückseite",
  h_sp_als_rueckseite: "Diese Sprache für die Rückseite und die Übersetzung verwenden",
  h_sp_installieren: "Diese Sprache installieren – danach steht sie für die Rückseite bereit",
  h_sp_entfernen: "Sprachpaket entfernen – deine Kartentexte in dieser Sprache bleiben",
  sp_weg_titel: n => `${n} entfernen?`,
  sp_weg_text: "Entfernt wird nur das Sprachpaket (Schrift). Deine Kartentexte in dieser Sprache bleiben in karten.csv und sind nach einer neuen Installation sofort wieder da.",
  sp_weg_ziel: "Sie ist gerade die Sprache der Rückseite – danach geht’s mit Spanisch weiter.",
  sp_zurueck: "Rückseite wieder auf Spanisch – alles im grünen Gänsebereich.",
  ez_druck_sprache: "Sprache der Rückseite", ez_druck_ziel: n => `${n} (aktuelle Kartensprache)`,
  ez_druck_alle: n => `Alle installierten (${n} Aufträge, einer je Sprache)`,
  h_druck_sprache: "In welcher Sprache die Rückseiten gedruckt bzw. exportiert werden. Andere Sprachen bekommen die Endung _<Kürzel> im Dateinamen (z. B. …_ja.pdf) – Spanisch bleibt wie immer.",
  ez_druck_eingereiht: n => `${n} Aufträge eingereiht – einer je Sprache, schön gänsemarschmäßig nacheinander.`,
});
Object.assign(TXT.en, {
  h_rs_feld: "The word in {zs} for the back", u_kartensprache_zs: "{zs}",
  zs_wahl: "Back:", h_zs_wahl: "Language of the back – switches texts, translation and the big field in step 2",
  zs_gewechselt: "Backs are now in {zs} – goose-tastically international!",
  weitere_sprachen: (n, g) => `More languages (${n} of ${g} filled in)`,
  h_weitere_sprachen: "The same card with backs in more languages – 🌐 suggests a word for each language",
  rs_ph: n => `Word in ${n} (optional)`, spalte_rs: n => `Back (${n})`,
  h_sprach_chip: (n, w) => `${n}${w ? ": " + w : ""} – click to show this back`,
  h_sprach_chip_touch: (n, w) => `${n}${w ? ": " + w : ""} – tap to show this back`,
  sprach_chip_leer: n => `${n}: no word yet`, filter_fehlt: n => `missing in ${n}`,
  sp_immer: "always included", sp_sofort: "no download", sp_aktuell: "current back", sp_als_rueckseite: "Use for back",
  h_sp_als_rueckseite: "Use this language for the back and for translation",
  h_sp_installieren: "Install this language – then it’s ready for the back",
  h_sp_entfernen: "Remove the language pack – your card texts in this language stay",
  sp_weg_titel: n => `Remove ${n}?`,
  sp_weg_text: "Only the language pack (font) is removed. Your card texts in this language stay in karten.csv and are back right away after a new installation.",
  sp_weg_ziel: "It is the language of the back right now – afterwards Spanish takes over again.",
  sp_zurueck: "Back is in Spanish again – everything’s goose-d.",
  ez_druck_sprache: "Language of the back", ez_druck_ziel: n => `${n} (current card language)`,
  ez_druck_alle: n => `All installed (${n} jobs, one per language)`,
  h_druck_sprache: "Which language the backs are printed or exported in. Other languages get the suffix _<code> in the file name (e.g. …_ja.pdf) – Spanish stays as always.",
  ez_druck_eingereiht: n => `${n} jobs queued – one per language, neatly in goose-step one after another.`,
});
Object.assign(TXT.es, {
  h_rs_feld: "La palabra en {zs} para el reverso", u_kartensprache_zs: "{zs}",
  zs_wahl: "Reverso:", h_zs_wahl: "Idioma del reverso: cambia los textos, la traducción y el campo grande del paso 2",
  zs_gewechselt: "Los reversos ahora están en {zs}: ¡un ganso muy internacional!",
  weitere_sprachen: (n, g) => `Más idiomas (${n} de ${g} con texto)`,
  h_weitere_sprachen: "La misma carta con reversos en más idiomas; 🌐 sugiere una palabra para cada idioma",
  rs_ph: n => `Palabra en ${n} (opcional)`, spalte_rs: n => `Reverso (${n})`,
  h_sprach_chip: (n, w) => `${n}${w ? ": " + w : ""}: haz clic para ver este reverso`,
  h_sprach_chip_touch: (n, w) => `${n}${w ? ": " + w : ""}: toca para ver este reverso`,
  sprach_chip_leer: n => `${n}: aún sin palabra`, filter_fehlt: n => `falta en ${n}`,
  sp_immer: "siempre incluido", sp_sofort: "sin descarga", sp_aktuell: "reverso actual", sp_als_rueckseite: "Usar en el reverso",
  h_sp_als_rueckseite: "Usar este idioma para el reverso y la traducción",
  h_sp_installieren: "Instalar este idioma; después queda listo para el reverso",
  h_sp_entfernen: "Quitar el paquete de idioma; tus textos en este idioma se quedan",
  sp_weg_titel: n => `¿Quitar ${n}?`,
  sp_weg_text: "Solo se quita el paquete de idioma (fuente). Tus textos en este idioma se quedan en karten.csv y vuelven en cuanto lo instales de nuevo.",
  sp_weg_ziel: "Ahora es el idioma del reverso; después sigue el español.",
  sp_zurueck: "El reverso vuelve al español: todo en orden en el estanque.",
  ez_druck_sprache: "Idioma del reverso", ez_druck_ziel: n => `${n} (idioma actual de las cartas)`,
  ez_druck_alle: n => `Todos los instalados (${n} tareas, una por idioma)`,
  h_druck_sprache: "En qué idioma se imprimen o exportan los reversos. Los demás idiomas llevan el sufijo _<código> en el nombre del archivo (p. ej. …_ja.pdf); el español queda como siempre.",
  ez_druck_eingereiht: n => `${n} tareas en la cola: una por idioma, en fila india como los gansos.`,
});
// Handy-App (Web-App) und untere App-Navigation – Texte in allen drei Sprachen
Object.assign(TXT.de, {
  app_karten: "Karten", app_neu: "Neu", app_lernen: "Lernen", app_drucken: "Drucken", app_mehr: "Mehr", app_mehr_titel: "Alles auf einen Blick",
  h_app_mehr: "Weitere Bereiche: Tabelle, Bildverbesserung, Ideen, Werkzeuge, Hilfe – und die App-Sachen (Installieren, Sicherung)",
  app_hinweis: "Hol dir die Gans als App: Vollbild, läuft auch offline, und deine Karten bleiben auf diesem Gerät.",
  app_installieren: "App installieren", app_spaeter: "Später", app_installiert: "Geschafft – die Gans wohnt jetzt auf deinem Startbildschirm!",
  app_install_titel: "Als App installieren",
  app_install_text: "So kommt Me Goos-ta Deutsch mit eigenem Symbol auf deinen Startbildschirm – danach startet sie wie eine richtige App, auch ohne Internet.",
  app_ios_1: "Tippe in Safari unten auf „Teilen“ (Quadrat mit Pfeil nach oben).",
  app_ios_2: "Wähle „Zum Home-Bildschirm“ – eventuell etwas nach unten scrollen.",
  app_ios_3: "Tippe oben rechts auf „Hinzufügen“ – fertig, die Gans watschelt auf deinen Home-Bildschirm!",
  app_ios_hinweis: "Wichtig am iPhone/iPad (ab iOS 16.4): Nur in der installierten App bleiben deine Daten dauerhaft – Safari löscht Website-Daten sonst nach 7 Tagen ohne Besuch.",
  app_and_1: "Öffne das Browser-Menü ⋮ (oben rechts).",
  app_and_2: "Tippe auf „App installieren“ bzw. „Zum Startbildschirm hinzufügen“.",
  app_and_3: "Bestätige mit „Installieren“ – die Gans erscheint bei deinen Apps.",
  app_and_hinweis: "Am besten mit einem aktuellen Chrome (Android, Google Pixel) – dann wird es eine echte App im App-Menü.",
  app_sicherung: "Sicherung & Speicher", app_rechner: "Auch für den Rechner holen",
  app_sicherung_text: "Deine Karten, Bilder, Ideen und der Lernstand liegen nur auf diesem Gerät. Eine Sicherung packt alles in eine Datei – zum Aufheben oder für ein neues Handy.",
  app_sichern: "Alles sichern", app_einspielen: "Sicherung einspielen",
  app_einspielen_text: "Einspielen ersetzt alles auf diesem Gerät durch den Stand der Sicherung.",
  app_einspielen_frage: n => `„${n}“ einspielen? Alles auf diesem Gerät wird durch die Sicherung ersetzt.`, app_einspielen_ja: "Ja, einspielen",
  app_vom_rechner: "Karten vom Rechner übernehmen",
  app_vom_rechner_text: "Am Rechner: Meine Karten → ⇅ Import / Export → „Alles – Komplettsicherung“ exportieren, die Datei aufs Handy schicken und hier importieren – samt Lernstand.",
  app_sicherung_tipp: "Tipp: Sichere ab und zu – vor allem vor einem Handywechsel.",
  app_belegt: mb => `Belegt: ${mb} MB`, app_dauerhaft_ja: "Dauerhaft gespeichert ✓",
  app_dauerhaft_nein: "Der Browser darf die Daten bei Platzmangel löschen – installiere die App und sichere ab und zu.",
  app_update: "Neue Gänse-Version da – neu laden?", app_update_knopf: "Neu laden",
  app_datei_text: "Fertig! Teile die Datei (zum Beispiel zum Drucken, per Mail oder in „Dateien“) oder speichere sie.",
  ie_lernstand: n => `🎓 Lernstand von ${n} ${n === 1 ? "Karte" : "Karten"} übernommen.`,
  app_teilen: "Teilen", app_speichern: "Speichern", app_oeffnen: "Teilen / Speichern",
  app_als_app: "Als App aufs Handy", app_zur_app_knopf: "Zur App",
  app_handy_hinweis: "Die Gans gibt es auch als App – sie läuft dann ganz ohne Rechner, auch offline.",
  app_zur_app_text: "Öffne diese Adresse am Handy (oder scanne den QR-Code) und installiere die App dort. Deine Karten holst du mit einer Komplettsicherung vom Rechner hinüber.",
  lan_app_text: "Ganz ohne WLAN-Zugang: Scanne den Code mit dem Handy und installiere die Gans dort als App – sie läuft dann auch ohne Rechner und offline. Deine Karten holst du mit einer Komplettsicherung hinüber.",
  app_anleitungen: "Anleitungen mit Bildern: die Dateien „Me Goos-ta Deutsch - Android / iPhone / Google Pixel.html“ neben den Startdateien.",
  pr_app_tipp: "Noch bequemer: Die Gans gibt es auch als App fürs Handy – mit Karten lernen, auch offline.",
  ki_nur_rechner: "KI-Bilder brauchen einen kräftigen Rechner (3,5 GB Modell) – am Handy klappt das über den Handy-Zugang des Rechners. Alles andere geht hier ganz gans normal!",
  verbindung_app: "Die App-Gans ist kurz eingenickt – lade die Seite einfach neu, deine Karten sind sicher.",
});
Object.assign(TXT.en, {
  app_karten: "Cards", app_neu: "New", app_lernen: "Learn", app_drucken: "Print", app_mehr: "More", app_mehr_titel: "Everything at a glance",
  h_app_mehr: "More sections: table, image enhancement, ideas, tools, help – plus the app things (install, backup)",
  app_hinweis: "Get the goose as an app: full screen, works offline, and your cards stay on this device.",
  app_installieren: "Install app", app_spaeter: "Later", app_installiert: "Done – the goose now lives on your home screen!",
  app_install_titel: "Install as an app",
  app_install_text: "This puts Me Goos-ta Deutsch on your home screen with its own icon – after that it starts like a real app, even without internet.",
  app_ios_1: "In Safari, tap “Share” at the bottom (square with an arrow pointing up).",
  app_ios_2: "Choose “Add to Home Screen” – you may need to scroll down a little.",
  app_ios_3: "Tap “Add” at the top right – done, the goose waddles onto your home screen!",
  app_ios_hinweis: "Important on iPhone/iPad (iOS 16.4 or later): your data only stays for good in the installed app – otherwise Safari deletes website data after 7 days without a visit.",
  app_and_1: "Open the browser menu ⋮ (top right).",
  app_and_2: "Tap “Install app” or “Add to Home screen”.",
  app_and_3: "Confirm with “Install” – the goose shows up with your apps.",
  app_and_hinweis: "Best with an up-to-date Chrome (Android, Google Pixel) – then it becomes a real app in your app drawer.",
  app_sicherung: "Backup & storage", app_rechner: "Get it for your computer",
  app_sicherung_text: "Your cards, images, ideas and learning progress live only on this device. A backup packs everything into one file – to keep safe or for a new phone.",
  app_sichern: "Back up everything", app_einspielen: "Restore backup",
  app_einspielen_text: "Restoring replaces everything on this device with the state of the backup.",
  app_einspielen_frage: n => `Restore “${n}”? Everything on this device will be replaced by the backup.`, app_einspielen_ja: "Yes, restore",
  app_vom_rechner: "Take over cards from the computer",
  app_vom_rechner_text: "On the computer: My cards → ⇅ Import / export → export “Everything – full backup”, send the file to your phone and import it here – learning progress included.",
  app_sicherung_tipp: "Tip: back up now and then – especially before switching phones.",
  app_belegt: mb => `In use: ${mb} MB`, app_dauerhaft_ja: "Stored persistently ✓",
  app_dauerhaft_nein: "The browser may delete the data when space runs low – install the app and back up now and then.",
  app_update: "A new goose version is here – reload?", app_update_knopf: "Reload",
  app_datei_text: "Ready! Share the file (for example to print, by email or to “Files”) or save it.",
  ie_lernstand: n => `🎓 Learning progress of ${n} ${n === 1 ? "card" : "cards"} taken over.`,
  app_teilen: "Share", app_speichern: "Save", app_oeffnen: "Share / save",
  app_als_app: "Get it as a phone app", app_zur_app_knopf: "Open the app",
  app_handy_hinweis: "The goose is also available as an app – it then runs entirely without the computer, even offline.",
  app_zur_app_text: "Open this address on your phone (or scan the QR code) and install the app there. Bring your cards over with a full backup from the computer.",
  lan_app_text: "No Wi-Fi access needed: scan the code with your phone and install the goose there as an app – it then runs without the computer and offline too. Bring your cards over with a full backup.",
  app_anleitungen: "Illustrated guides: the files “Me Goos-ta Deutsch - Android / iPhone / Google Pixel.html” next to the start files.",
  pr_app_tipp: "Even handier: the goose also comes as a phone app – with card studying, offline too.",
  ki_nur_rechner: "AI images need a powerful computer (3.5 GB model) – on a phone, use the computer’s phone access. Everything else works right here, goose-tastic as ever!",
  verbindung_app: "The app goose nodded off for a moment – just reload the page, your cards are safe.",
});
Object.assign(TXT.es, {
  app_karten: "Cartas", app_neu: "Nueva", app_lernen: "Aprender", app_drucken: "Imprimir", app_mehr: "Más", app_mehr_titel: "Todo de un vistazo",
  h_app_mehr: "Más secciones: tabla, mejora de imagen, ideas, herramientas, ayuda, y lo de la app (instalar, copia de seguridad)",
  app_hinweis: "Llévate el ganso como app: pantalla completa, funciona sin conexión y tus cartas se quedan en este dispositivo.",
  app_installieren: "Instalar app", app_spaeter: "Más tarde", app_installiert: "¡Listo! El ganso ya vive en tu pantalla de inicio.",
  app_install_titel: "Instalar como app",
  app_install_text: "Así Me Goos-ta Deutsch llega a tu pantalla de inicio con su propio icono; después se abre como una app de verdad, incluso sin internet.",
  app_ios_1: "En Safari, toca «Compartir» abajo (cuadrado con una flecha hacia arriba).",
  app_ios_2: "Elige «Agregar a pantalla de inicio»; quizá tengas que desplazarte un poco hacia abajo.",
  app_ios_3: "Toca «Agregar» arriba a la derecha y listo: ¡el ganso se va anadeando a tu pantalla de inicio!",
  app_ios_hinweis: "Importante en iPhone/iPad (desde iOS 16.4): tus datos solo se quedan para siempre en la app instalada; si no, Safari borra los datos del sitio tras 7 días sin visitarlo.",
  app_and_1: "Abre el menú del navegador ⋮ (arriba a la derecha).",
  app_and_2: "Toca «Instalar app» o «Agregar a la pantalla principal».",
  app_and_3: "Confirma con «Instalar»: el ganso aparece junto a tus apps.",
  app_and_hinweis: "Mejor con un Chrome actualizado (Android, Google Pixel): así se vuelve una app de verdad en tu menú de apps.",
  app_sicherung: "Copia y almacenamiento", app_rechner: "Descárgalo para tu computadora",
  app_sicherung_text: "Tus cartas, imágenes, ideas y tu avance de aprendizaje están solo en este dispositivo. Una copia lo guarda todo en un archivo, para conservarlo o para un celular nuevo.",
  app_sichern: "Respaldar todo", app_einspielen: "Restaurar copia",
  app_einspielen_text: "Restaurar reemplaza todo en este dispositivo con el contenido de la copia.",
  app_einspielen_frage: n => `¿Restaurar «${n}»? Todo en este dispositivo se reemplazará con la copia.`, app_einspielen_ja: "Sí, restaurar",
  app_vom_rechner: "Traer cartas de la computadora",
  app_vom_rechner_text: "En la computadora: Mis cartas → ⇅ Importar / exportar → exporta «Todo: copia de seguridad completa», envía el archivo al celular e impórtalo aquí, con tu avance de aprendizaje.",
  app_sicherung_tipp: "Consejo: respalda de vez en cuando, sobre todo antes de cambiar de celular.",
  app_belegt: mb => `En uso: ${mb} MB`, app_dauerhaft_ja: "Guardado de forma permanente ✓",
  app_dauerhaft_nein: "El navegador puede borrar los datos si falta espacio: instala la app y respalda de vez en cuando.",
  app_update: "Hay una nueva versión del ganso: ¿recargar?", app_update_knopf: "Recargar",
  app_datei_text: "¡Listo! Comparte el archivo (por ejemplo para imprimir, por correo o en «Archivos») o guárdalo.",
  ie_lernstand: n => `🎓 Se tomó el avance de aprendizaje de ${n} ${n === 1 ? "carta" : "cartas"}.`,
  app_teilen: "Compartir", app_speichern: "Guardar", app_oeffnen: "Compartir / guardar",
  app_als_app: "Como app en el celular", app_zur_app_knopf: "Abrir la app",
  app_handy_hinweis: "El ganso también existe como app: así funciona sin la computadora, incluso sin conexión.",
  app_zur_app_text: "Abre esta dirección en el celular (o escanea el código QR) e instala ahí la app. Tus cartas las pasas con una copia de seguridad completa desde la computadora.",
  lan_app_text: "Sin acceso por wifi: escanea el código con el celular e instala ahí el ganso como app; así funciona sin la computadora e incluso sin conexión. Tus cartas las pasas con una copia de seguridad completa.",
  app_anleitungen: "Guías con imágenes: los archivos «Me Goos-ta Deutsch - Android / iPhone / Google Pixel.html» junto a los archivos de inicio.",
  pr_app_tipp: "Aún más práctico: el ganso también existe como app para el celular, para estudiar tus cartas incluso sin conexión.",
  ki_nur_rechner: "Las imágenes IA necesitan una computadora potente (modelo de 3,5 GB); en el celular usa el acceso desde el celular de la computadora. ¡Todo lo demás funciona aquí de maravilla!",
  verbindung_app: "El ganso de la app se quedó dormido un momento: recarga la página y listo, tus cartas están a salvo.",
});
/* ----- Kartensprache (Tool „Sprachen“): {zs} in Texten = Name der Zielsprache in der Sprache der Oberfläche ----- */
const ZS_STANDARD = { code: "es", kurz: "ES", namen: { de: "Spanisch", en: "Spanish", es: "español" }, richtung: "ltr",
  sonderzeichen: [], installiert: ["es"], sprachen: [] };
let ZS = ZS_STANDARD;
const NUR_ES = { "h_es_feld": "h_rs_feld", "u_kartensprache_wert": "u_kartensprache_zs" };   // Erklärung „wie in Mexiko“ nur bei es
const NUR_APP = { "im_browser": "app_oeffnen" };                 // Handy-App: Ergebnisse öffnen sich als Teilen/Speichern
function zsInfo(code) {
  if (!code || code === ZS.code) return ZS;
  return (ZS.sprachen || []).find(x => x.code === code) || { code, kurz: String(code).toUpperCase(), namen: code === "es" ? ZS_STANDARD.namen : {}, richtung: "ltr" };
}
function zsName(code) { const i = zsInfo(code), n = i.namen || {}; return n[S.sprache] || n.en || i.name || i.kurz; }
const zsMehrere = () => (ZS.installiert || []).length > 1;          // Tool „Sprachen“ aktiv: Kennzeichnung + Auswahl
const zsAttr = code => `lang="${esc((code || ZS.code) === "no" ? "nb" : (code || ZS.code))}" dir="auto"`;
const BERUEHRUNG = !!(window.matchMedia && matchMedia("(hover: none) and (pointer: coarse)").matches);
function t(k, ...a) {
  if (ZS.code !== "es" && NUR_ES[k]) k = NUR_ES[k];
  if (AM_APP && NUR_APP[k]) k = NUR_APP[k];
  const l = TXT[S.sprache] || TXT.en; if (BERUEHRUNG && (k + "_touch") in l) k += "_touch";
  let v = l[k] ?? TXT.en[k] ?? TXT.de[k]; if (typeof v === "function") v = v(...a);
  if (typeof v === "string" && v.includes("{zs}")) v = v.replaceAll("{zs}", zsName());
  return v ?? k;
}
const zahl = v => S.sprache === "en" ? String(v) : String(v).replace(".", ",");
const warte = ms => new Promise(r => setTimeout(r, ms));
function entprellt(fn, ms) { let z; return (...a) => { clearTimeout(z); z = setTimeout(() => fn(...a), ms); }; }

/* ----- Lade-Ente: dieselbe Animation wie duck_spinner.py (Konsole) – die Ente schwimmt hin und her, wippt im
   Wasser und dreht an den Enden um; alle Bilder werden je Breite einmal vorberechnet, ein einziger Takt (10 Bilder/s)
   bedient alle sichtbaren Enten und hält an, sobald keine mehr da ist. ----- */
const ENTE_RECHTS = ["    __   ", "___( o)> ", "\\_____/  "];
const ENTE_WELLE_OBEN = "~~-~~~-~", ENTE_WELLE_UNTEN = "-.~-.~~ ";
const ENTE_RUHIG = !!(window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches);
const enteBilder = {};
function enteSpiegeln(sprite) {
  const tausch = { "(": ")", ")": "(", "<": ">", ">": "<", "/": "\\", "\\": "/" };
  return sprite.map(z => [...z].reverse().map(c => tausch[c] || c).join(""));
}
function baueEntenBilder(breite) {
  if (enteBilder[breite]) return enteBilder[breite];
  const ggt = (a, b) => b ? ggt(b, a % b) : a, kgv = (...n) => n.reduce((r, x) => r * x / ggt(r, x), 1);
  const sprites = [ENTE_RECHTS, enteSpiegeln(ENTE_RECHTS)], spanne = Math.max(breite - ENTE_RECHTS[0].length, 1);
  const weg = [];
  for (let x = 0; x <= spanne; x++) weg.push([x, 0]);
  for (let x = spanne; x >= 0; x--) weg.push([x, 1]);
  const gesamt = kgv(weg.length, ENTE_WELLE_OBEN.length, 2 * ENTE_WELLE_UNTEN.length, 6), wu = ENTE_WELLE_UNTEN.length;
  const klasse = c => "<>".includes(c) ? "s" : c === "o" ? "a" : "e";
  const bilder = [];
  for (let k = 0; k < gesamt; k++) {
    const [x, richtung] = weg[k % weg.length], wippen = Math.floor(k / 3) % 2;
    const zeilen = Array.from({ length: 4 }, () => Array.from({ length: breite }, () => [" ", ""]));
    for (let i = 0; i < breite; i++) {
      zeilen[2][i] = [ENTE_WELLE_OBEN[(i + k) % ENTE_WELLE_OBEN.length], "w1"];
      zeilen[3][i] = [ENTE_WELLE_UNTEN[(((i - Math.floor(k / 2)) % wu) + wu) % wu], "w2"];
    }
    sprites[richtung].forEach((zeile, r) => {                  // nur Leerzeichen am Rand sind durchsichtig
      const start = zeile.length - zeile.trimStart().length, ende = zeile.trimEnd().length;
      for (let c = start; c < ende; c++) zeilen[wippen + r][x + c] = [zeile[c], zeile[c] === " " ? "" : klasse(zeile[c])];
    });
    bilder.push(zeilen.map(z => {
      let aus = "", akt = "";
      for (const [ch, kl] of z) {
        if (kl !== akt) { if (akt) aus += "</span>"; if (kl && kl !== "e") aus += `<span class="${kl}">`; akt = kl === "e" ? "" : kl; }
        aus += ch === "<" ? "&lt;" : ch === ">" ? "&gt;" : ch;
      }
      return aus + (akt ? "</span>" : "");
    }).join("\n"));
  }
  return (enteBilder[breite] = bilder);
}
let enteTakt = null, enteSchritt = 0;
function enteTick() {
  const enten = document.querySelectorAll("pre.ente-ascii");
  if (!enten.length) { clearInterval(enteTakt); enteTakt = null; return; }
  enteSchritt++;
  enten.forEach(pre => {
    if (!pre.offsetParent) return;                               // unsichtbar: nichts zu zeichnen
    const b = baueEntenBilder(+pre.dataset.breite || 24); pre.innerHTML = b[enteSchritt % b.length];
  });
  const punkte = ".".repeat(Math.floor(enteSchritt / 3) % 4);
  document.querySelectorAll(".ente-punkte").forEach(p => { p.textContent = punkte; });
}
function enteStarten() { if (!enteTakt && !ENTE_RUHIG) enteTakt = setInterval(enteTick, 100); }
function enteHTML(text, klein = false) {
  const breite = klein ? 14 : 24, bild = baueEntenBilder(breite)[0];
  setTimeout(enteStarten, 0);
  const rein = String(text || t("laedt")).replace(/\s*(…|\.\.\.)\s*$/, "");
  return `<div class="ente-laedt${klein ? " klein" : ""}" role="status"><pre class="ente-ascii" aria-hidden="true" data-breite="${breite}">${bild}</pre>`
    + `<span>${esc(rein)}<span class="ente-punkte">${ENTE_RUHIG ? "…" : ""}</span></span></div>`;
}
let enteOffen = 0, enteUhr = null;
function enteGlobal(plus) {                        // erscheint erst nach 400 ms – schnelle Anfragen flackern nicht
  enteOffen = Math.max(0, enteOffen + plus);
  const el = $("#ente-global"); if (!el) return;
  if (enteOffen && !enteUhr && el.hidden) enteUhr = setTimeout(() => { enteUhr = null; if (enteOffen) { el.innerHTML = enteHTML("", true); el.hidden = false; } }, 400);
  if (!enteOffen) { clearTimeout(enteUhr); enteUhr = null; el.hidden = true; }
}

async function api(pfad, { methode = "GET", daten, roh, timeout, signal } = {}) {
  const opt = { method: methode, headers: { "X-GL-Token": TOKEN, "X-GL-Sprache": S.sprache }, credentials: "same-origin" };
  if (daten !== undefined) { opt.body = JSON.stringify(daten); opt.headers["Content-Type"] = "application/json"; }
  if (roh) { opt.body = roh; opt.headers["Content-Type"] = "application/octet-stream"; }
  // optional: Zeitlimit (ms) und/oder Abbruch von außen (AbortSignal); ohne beides wie bisher
  let ctrl = null, uhr = null, zeitUm = false;
  if (timeout || signal) {
    ctrl = new AbortController(); opt.signal = ctrl.signal;
    if (signal) { if (signal.aborted) ctrl.abort(); else signal.addEventListener("abort", () => ctrl.abort(), { once: true }); }
    if (timeout) uhr = setTimeout(() => { zeitUm = true; ctrl.abort(); }, timeout);
  }
  let r;
  enteGlobal(1);
  try { r = await fetch(pfad, opt); }
  catch (e) {
    enteGlobal(-1); clearTimeout(uhr);
    if (ctrl && ctrl.signal.aborted) { const f = new Error(t(zeitUm ? "anfrage_zeit" : "anfrage_abgebrochen")); f.abgebrochen = !zeitUm; f.zeitlimit = zeitUm; throw f; }
    $("#verbindung").hidden = false; throw new Error(t("keine_verbindung"));
  }
  clearTimeout(uhr);
  enteGlobal(-1);
  $("#verbindung").hidden = true;
  let j = null; try { j = await r.json(); } catch (e) { j = null; }
  if (!r.ok) { const e = new Error((j && j.fehler) || t("fehler_status", r.status)); e.status = r.status; e.daten = j; throw e; }
  if (j && j.lernstand_meldung) { toast(j.lernstand_meldung); lernSpaeter(); }    // Karte geändert → Lernstand zurückgesetzt
  return j;
}
function url(pfad, q) { return `${pfad}?${new URLSearchParams(q || {})}`; }
function toast(text, { fehler = false, aktion = null } = {}) {
  const el = document.createElement("div"); el.className = "toast" + (fehler ? " fehler" : "");
  const s = document.createElement("span"); s.textContent = text; el.append(s);
  if (aktion) { const b = document.createElement("button"); b.textContent = aktion.label; b.addEventListener("click", () => { el.remove(); aktion.fn(); }); el.append(b); }
  $("#toasts").append(el); setTimeout(() => el.remove(), aktion ? 9000 : fehler ? 7000 : 3500);
}
const fehlerToast = e => toast(e.message, { fehler: true });
function pruefliste(meldungen) {
  return `<ul class="pruefliste">${(meldungen || []).map(m => `<li class="${esc(m.stufe)}">${esc(m.text)}</li>`).join("")}</ul>`;
}

/* ===================== Sprache ===================== */
function uebersetze() {
  document.documentElement.lang = S.sprache;
  $$("[data-t]").forEach(el => { el.textContent = t(el.dataset.t); });
  $$("[data-t-attr]").forEach(el => el.dataset.tAttr.split(";").forEach(p => { const [a, k] = p.split(":"); el.setAttribute(a, t(k)); }));
  $$(".sprachwahl button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.sprache === S.sprache)));
}
$(".sprachwahl").addEventListener("click", async e => {
  const b = e.target.closest("[data-sprache]"); if (!b || b.dataset.sprache === S.sprache) return;
  S.sprache = b.dataset.sprache; uebersetze();
  try {
    await api("/api/sprache", { methode: "POST", daten: { sprache: S.sprache } });
    await Promise.all([ladeOptionen(), ladeWerkzeuge(), ladeKarten(), ladeEntwuerfe(), ladeStatus(), ladeUe(), ladeTools()]);
  } catch (err) { fehlerToast(err); }
  zeige();
});

/* ===================== Navigation ===================== */
const ANSICHTEN = ["karten", "lernen", "tabelle", "verbesserung", "bild", "beschriften", "ideen", "erzeugen", "pruefen", "werkzeuge", "hilfe", "deinstallieren"];
function ansicht() { const h = location.hash.slice(1); return ANSICHTEN.includes(h) ? h : "karten"; }
function zeige() {
  const name = ansicht();
  ANSICHTEN.forEach(a => { $("#v-" + a).hidden = a !== name; });
  $$(".navi a").forEach(a => a.dataset.ansicht === name ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current"));
  if (name === "karten") zeichneKarten();
  if (name === "lernen") zeichneLernen();
  if (name === "tabelle") ladeTabelle();
  if (name === "verbesserung") { zeichneOptionen(); ladeVerbesserung(); }
  if (name === "bild") zeichneEntwuerfe();
  if (name === "beschriften") zeichneEditoren();
  if (name === "erzeugen") { zeichneOptionen(); zeigeBefehl(); }
  if (name === "pruefen") ladeErgebnisse();
  if (name === "werkzeuge") { zeichneWerkzeuge(); ladeUe().then(zeichneUeEinstellungen); toolsAuffrischen(); }
  if (name === "hilfe") ladeHilfe();
  if (name === "ideen") ladeIdeen();
  if (name === "deinstallieren") zeichneDeinstallieren();
  zeichneZsWahl();
  zeichneLauf();
  appNaviAktuell();
  if (name === "karten") zeichneAppHinweis();
}
window.addEventListener("hashchange", () => { zeige(); window.scrollTo(0, 0); });
function zaehler() {
  const offen = offeneKarten().length;
  $("#zahl-offen").hidden = !offen; $("#zahl-offen").textContent = offen;
  $("#zahl-bild").hidden = !S.entwuerfe.length; $("#zahl-bild").textContent = S.entwuerfe.length;
  const auto = S.karten.filter(k => k.uebersetzung === "auto").length;
  $("#zahl-tabelle").hidden = !auto; $("#zahl-tabelle").textContent = auto; $("#zahl-tabelle").title = t("zahl_tabelle_titel", auto);
  const ideen = IDEEN ? IDEEN.ideen.length : 0;
  $("#zahl-ideen").hidden = !ideen; $("#zahl-ideen").textContent = ideen;
  appNaviZahlen();
}

/* ===================== Kartenliste (Übersicht) ===================== */
function uebernehmeKarten(d) { S.karten = d.karten.map(k => ({ ...k })); S.ohne = d.ohne_karte; S.meldungen = d.meldungen; zaehler(); }
async function ladeKarten() { uebernehmeKarten(await api("/api/karten")); }
/* ----- Sprach-Chips (Code groß, Hover = Name; keine Flaggen) und Auswahl der Rückseiten-Sprache ----- */
function rsText(k, code) { code = code || ZS.code; return code === ZS.code ? String(k.es || "") : String((k.rueckseiten || {})[code] || ""); }
function sprachChip(code, { aktuell = code === ZS.code, wort = null, knopf = false, gedrueckt = false } = {}) {
  const i = zsInfo(code), leer = wort !== null && !String(wort).trim();
  const titel = leer ? t("sprach_chip_leer", zsName(code)) : knopf ? t("h_sprach_chip", zsName(code), wort || "") : zsName(code) + (wort ? ": " + wort : "");
  const kl = `sprach-chip${aktuell ? " aktuell" : ""}${leer ? " leer" : ""}`;
  return knopf ? `<button type="button" class="${kl}" data-zs-zeige="${esc(code)}" aria-pressed="${gedrueckt}" title="${esc(titel)}" lang="${esc(code)}">${esc(i.kurz)}</button>`
    : `<span class="${kl}" title="${esc(titel)}">${esc(i.kurz)}</span>`;
}
function chipZs() { return zsMehrere() ? " " + sprachChip(ZS.code) : ""; }
function kartenChips(k) {
  if (!zsMehrere()) return "";
  const gezeigt = S.zeigeZs[k.bild] || ZS.code;
  return `<div class="sprach-chips">${ZS.installiert.map(c => sprachChip(c, { wort: rsText(k, c), knopf: true, gedrueckt: c === gezeigt })).join("")}</div>`;
}
function zsWahlHTML() {
  if (!zsMehrere()) return "";
  return `<label class="zs-wahl" title="${esc(t("h_zs_wahl"))}"><span>${esc(t("zs_wahl"))}</span><select data-zs-wahl>${ZS.installiert.map(c =>
    `<option value="${esc(c)}"${c === ZS.code ? " selected" : ""}>${esc(zsInfo(c).kurz)} · ${esc(zsName(c))}</option>`).join("")}</select></label>`;
}
function zeichneZsWahl() { $$("[data-zs-platz]").forEach(el => { el.innerHTML = zsWahlHTML(); }); }
function uebernehmeZs(neu) {                                  // neue Zielsprache/Installationen → Texte und Ansicht neu
  if (!neu || !neu.code) return false;
  const vorher = ZS.code + "|" + (ZS.installiert || []).join(",");
  ZS = neu;
  if (vorher === ZS.code + "|" + (ZS.installiert || []).join(",")) return false;
  if (ZS.code !== vorher.split("|")[0]) { S.zeigeZs = {}; S.vorschlaege = {}; S.autoVersucht = new Set(); TAB = { karten: [] }; }
  uebersetze(); return true;
}
async function setzeZielsprache(code) {
  let neu;
  try { neu = await api("/api/zielsprache", { methode: "POST", daten: { zielsprache: code } }); }
  catch (e) { fehlerToast(e); zeichneZsWahl(); return; }
  uebernehmeZs(neu);
  try { await Promise.all([ladeKarten(), ladeStatus(), ladeEntwuerfe()]); } catch (e) { fehlerToast(e); }
  zeige(); toast(t("zs_gewechselt"));
}
document.addEventListener("change", e => { const s = e.target.closest && e.target.closest("[data-zs-wahl]"); if (s) setzeZielsprache(s.value); });
function vorschauUrl(k, seite, es) {
  return url("/api/vorschau", { bild: k.bild, es: seite === "hinten" ? (es ?? k.es) : "", fit: k.fit || "contain", seite, v: S.v });
}
function bewertungText(code) { return (t("bewertung") || {})[code] || code; }
function marken(k) {
  const m = [lernMarke(k)];
  if (!k.existiert) m.push(`<span class="marke-q schlecht" title="${esc(t("h_marke_bild_fehlt"))}">${esc(t("marke_bild_fehlt"))}</span>`);
  if (k.existiert && !String(k.es).trim()) m.push(`<span class="marke-q schlecht" title="${esc(t("h_marke_es_fehlt"))}">${esc(t("marke_es_fehlt"))}</span>`);
  const b = k.bericht;
  if (b && b.ppi) {
    const kl = b.ppi >= 180 ? "gut" : b.ppi < 120 ? "schlecht" : "";
    const code = b.bewertung_code || (b.ppi >= 250 ? "sehr_gut" : b.ppi >= 180 ? "gut" : b.ppi >= 120 ? "ausreichend" : "gering");
    m.push(`<span class="marke-q ${kl}" title="${esc(b.methode || "")}">${esc(t("marke_ppi", b.ppi, bewertungText(code)))}</span>`);
  }
  if (b && b.text_warnung) m.push(`<span class="marke-q warn" title="${esc(t("h_marke_text"))}">${esc(b.text_warnung)}</span>`);
  if (k.uebersetzung === "auto") m.push(`<a class="marke-q auto" href="#tabelle" title="${esc(t("marke_auto_titel"))}">${esc(t("marke_auto"))}</a>`);
  if (k.uebersetzung === "geprueft") m.push(`<span class="marke-q gut" title="${esc(t("h_marke_geprueft"))}">${esc(t("marke_geprueft"))}</span>`);
  if (k.verbessert) m.push(`<span class="marke-q gut" title="${esc(t("marke_verbessert_titel"))}">✦ ${esc(t("marke_verbessert"))}</span>`);
  if (!k.aktiv) m.push(`<span class="marke-q" title="${esc(t("h_marke_aus"))}">${esc(t("marke_aus"))}</span>`);
  return m.join("");
}
function karteHTML(k, nr, seiteTexte = true) {
  return `<button class="karte" data-aktion="drehen" aria-label="${esc(t("karte_umdrehen", nr))}" aria-pressed="false" title="${esc(t("umdrehen"))}">
    <span class="innen">
      <span class="seite vorn">${k.existiert ? `<img loading="lazy" alt="" data-seite="vorn" data-bild="${esc(k.bild)}" src="${vorschauUrl(k, "vorn")}">` : `<span class="ersatz">${esc(t("bild_fehlt"))}</span>`}</span>
      <span class="seite hinten">${k.existiert && rsText(k, S.zeigeZs[k.bild]).trim() ? `<img loading="lazy" alt="" data-seite="hinten" data-bild="${esc(k.bild)}" src="${vorschauUrl(k, "hinten", rsText(k, S.zeigeZs[k.bild]))}">` : `<span class="ersatz" ${zsAttr(S.zeigeZs[k.bild])}>${esc(rsText(k, S.zeigeZs[k.bild]) || "–")}</span>`}</span>
    </span></button>`;
}
function zeileHTML(k, i) {
  const nr = k.aktiv && k.nr ? k.nr : "–";
  const wahl = S.lernAuswahl ? `<label class="lern-haken" title="${esc(t("h_ln_auswahl"))}"><input type="checkbox" data-aktion="lern-wahl"${S.lernAuswahl.has(k.bild) ? " checked" : ""} aria-label="${esc(k.de || k.bild)}"></label>` : "";
  return `<article class="zeile${k.aktiv ? "" : " aus"}${S.lernAuswahl && S.lernAuswahl.has(k.bild) ? " gewaehlt" : ""}" data-i="${i}">
    <div>${karteHTML(k, nr)}<span class="karte-hinweis">${i === 0 ? esc(t("umdrehen")) : ""}</span></div>
    <div class="kartentext">
      <div class="oben">${wahl}<span class="nr${k.aktiv && k.nr ? "" : " ohne"}" title="${esc(t("nr_titel"))}">${esc(nr)}</span><h3>${esc(k.de || k.bild)}</h3></div>
      ${(() => { const c = S.zeigeZs[k.bild] || ZS.code, w = rsText(k, c).trim();
        return `<div class="es${w ? "" : " fehlt"}"${w ? " " + zsAttr(c) : ""}>${esc(w ? rsText(k, c) : c === ZS.code ? t("marke_es_fehlt") : t("sprach_chip_leer", zsName(c)))}</div>`; })()}
      ${kartenChips(k)}
      ${k.notiz ? `<div class="notiz">${esc(k.notiz)}</div>` : ""}
      <div class="datei">${esc(k.bild)}</div>
      <div class="marken">${marken(k)}</div>
    </div>
    <div class="aktionen">
      <button class="knopf klein dunkel" data-aktion="bearbeiten" title="${esc(t("h_bearbeiten"))}">${esc(t("bearbeiten"))}</button>
      <label class="schalter" title="${esc(t("drucken_titel"))}"><input type="checkbox" data-aktion="aktiv"${k.aktiv ? " checked" : ""}><span class="spur"></span>${esc(t("drucken"))}</label>
      <div class="reihenfolge">
        <button class="knopf klein" data-aktion="hoch" aria-label="${esc(t("hoch"))}" title="${esc(t("hoch"))}"${i === 0 ? " disabled" : ""}>▲</button>
        <button class="knopf klein" data-aktion="runter" aria-label="${esc(t("runter"))}" title="${esc(t("runter"))}"${i === S.karten.length - 1 ? " disabled" : ""}>▼</button>
      </div>
      <button class="knopf klein leise gefahr" data-aktion="entfernen" title="${esc(t("h_entfernen"))}">${esc(t("entfernen"))}</button>
    </div>
  </article>`;
}
function zeichneKarten() {
  const aktiv = S.karten.filter(k => k.aktiv).length, aus = S.karten.length - aktiv;
  $("#karten-unter").textContent = S.karten.length ? t("karten_unter", aktiv, aus) : t("karten_leer_unter");
  const offen = offeneKarten().length;
  $("#karten-banner").innerHTML = offen ? `<div class="banner"><p>${esc(t("banner_offen", offen))}</p>
    <a class="knopf haupt" href="#beschriften">${esc(t("banner_offen_knopf"))}</a></div>` : "";
  const ms = S.meldungen.filter(m => m.code !== "es_leer");
  $("#karten-hinweise").innerHTML = ms.length ? `<div class="hinweise"><b>${esc(t("hinweise_liste"))}</b><ul>${ms.map(m =>
    `<li class="${m.stufe === "fehler" ? "fehler" : ""}">${esc(m.text)}</li>`).join("")}</ul></div>` : "";
  $("#karten-lernleiste").innerHTML = lernLeisteHTML();
  const liste = S.karten.map((k, i) => lernPasst(k) ? zeileHTML(k, i) : "").join("");
  zeichneAuswahlLeiste();
  $("#kartenliste").innerHTML = S.karten.length ? liste || `<div class="flaeche leer"><p>${esc(t("ln_filter_leer"))}</p></div>` : `<div class="flaeche leer"><img src="/symbol.svg" alt="">
    <h2>${esc(t("karten_leer_titel"))}</h2><p>${esc(t("karten_leer_text"))}</p>
    <div class="knopfzeile"><a class="knopf haupt gross" href="#bild">${esc(t("zu_schritt1"))}</a></div></div>`;
}
document.addEventListener("error", e => {
  const img = e.target; if (img.tagName !== "IMG" || !img.dataset.seite) return;
  if (img.dataset.seite === "vorn" && img.dataset.bild && !img.dataset.ersatz) { img.dataset.ersatz = "1"; img.src = "/bild/" + encodeURIComponent(img.dataset.bild); }
  else { const s = document.createElement("span"); s.className = "ersatz"; s.textContent = "–"; img.replaceWith(s); }
}, true);
function listeZumSpeichern(karten) {
  return karten.map(k => ({ bild: k.bild, aktiv: k.aktiv, de: k.de, es: k.es, notiz: k.notiz, fit: k.fit, uebersetzung: k.uebersetzung || "", extra: k.extra || {},
    rueckseiten: k.rueckseiten || {}, uebersetzungen: k.uebersetzungen || {} }));
}
async function speichereListe(karten) {
  uebernehmeKarten(await api("/api/karten", { methode: "POST", daten: { karten: listeZumSpeichern(karten) } }));
  S.v++; zeichneKarten();
}
$("#kartenliste").addEventListener("change", async e => {
  if (e.target.dataset.aktion === "lern-wahl") {                // Auswahl zum Lernen (nur Ansicht, nichts gespeichert)
    const z = e.target.closest(".zeile"), k = S.karten[+z.dataset.i]; if (!k || !S.lernAuswahl) return;
    e.target.checked ? S.lernAuswahl.add(k.bild) : S.lernAuswahl.delete(k.bild); z.classList.toggle("gewaehlt", e.target.checked); zeichneAuswahlLeiste(); return;
  }
  if (e.target.dataset.aktion !== "aktiv") return;
  const i = +e.target.closest(".zeile").dataset.i; const neu = S.karten.map(k => ({ ...k }));
  neu[i].aktiv = e.target.checked;
  try { await speichereListe(neu); toast(t("gespeichert")); } catch (err) { fehlerToast(err); zeichneKarten(); }
});
$("#kartenliste").addEventListener("click", async e => {
  const chip = e.target.closest("[data-zs-zeige]");
  if (chip) {                                                 // Chip: diese Rückseite zeigen (nur Ansicht)
    const k = S.karten[+chip.closest(".zeile").dataset.i]; if (!k) return;
    S.zeigeZs[k.bild] = chip.dataset.zsZeige === ZS.code ? undefined : chip.dataset.zsZeige; zeichneKarten(); return;
  }
  const b = e.target.closest("[data-aktion]"); if (!b || b.dataset.aktion === "aktiv" || b.dataset.aktion === "lern-wahl") return;
  const z = b.closest(".zeile"); const i = +z.dataset.i; const k = S.karten[i];
  const aktion = b.dataset.aktion;
  if (aktion === "drehen") { b.classList.toggle("gedreht"); b.setAttribute("aria-pressed", b.classList.contains("gedreht")); return; }
  if (aktion === "bearbeiten") { oeffneEditor(k.bild); return; }
  const vorher = S.karten.map(x => ({ ...x })); const neu = S.karten.map(x => ({ ...x }));
  if (aktion === "hoch" && i > 0) [neu[i - 1], neu[i]] = [neu[i], neu[i - 1]];
  if (aktion === "runter" && i < neu.length - 1) [neu[i + 1], neu[i]] = [neu[i], neu[i + 1]];
  if (aktion === "entfernen") neu.splice(i, 1);
  try {
    await speichereListe(neu);
    if (aktion === "entfernen") toast(t("entfernt", k.bild), { aktion: { label: t("rueckgaengig"), fn: () => speichereListe(vorher).catch(fehlerToast) } });
  } catch (err) { fehlerToast(err); }
});

/* ===================== Schritt 1: Bilder vorbereiten (auch viele auf einmal) ===================== */
async function ladeEntwuerfe() {                       // neue Bilder für vorhandene Karten zeigt der Karten-Editor
  const alle = await api("/api/entwuerfe");
  S.entwuerfe = alle.filter(d => !d.karte); S.ersatz = {}; alle.filter(d => d.karte).forEach(d => { S.ersatz[d.karte] = d; });
  zaehler();
}
function entwurfBildUrl(d, art) { return url("/api/entwurf-bild", { id: d.id, art, drehung: d.drehung || 0, fit: d.fit || "", v: S.v }); }
function entwurfStatus(d) {
  if (!d.lesbar) return "";
  const f = (d.meldungen || []).filter(m => m.stufe === "fehler"), w = (d.meldungen || []).filter(m => m.stufe === "warnung");
  if (f.length) return `<span class="fehler"><b>✕ ${esc(t("st_problem"))}</b>${esc(f[0].text)}</span>`;
  const zusatz = !String(d.es || "").trim() ? t("st_ohne_es") : d.es === d.es_auto ? t("st_auto") : t("st_mit_es");
  if (w.length) return `<span class="warn"><b>! ${esc(t("st_hinweise", w.length))}</b>${esc(w[0].text)}</span>`;
  return `<span class="ok"><b>✓ ${esc(t("st_bereit"))}</b></span>${esc(d.dateiname || "")} · ${esc(zusatz)}`;
}
function entwurfHTML(d) {
  const lesbar = d.lesbar, offen = S.offeneEntwuerfe.has(d.id), id = esc(d.id);
  const esrgan = (S.status.ki_methode || "").startsWith("realesrgan");
  const auto = !!(d.es && d.es === d.es_auto);
  const fitKnopf = (wert, label) => `<label title="${esc(t("h_fit_" + wert))}"><input type="radio" name="fit-${id}" value="${wert}" data-e="fit"${d.fit === wert ? " checked" : ""}><span>${esc(label)}${d.fit_empfehlung === wert ? `<span class="empf" title="${esc(t("empfohlen"))}">★</span>` : ""}</span></label>`;
  return `<article class="entwurf${d.ok ? " bereit" : ""}" data-id="${id}">
    <div class="entwurf-zeile">
      ${lesbar ? `<div class="mini"><img alt="" loading="lazy" data-art="vorn" src="${entwurfBildUrl(d, "vorn")}"></div>` : `<div class="mini unlesbar">${esc(d.original)}</div>`}
      ${lesbar ? `<div class="f"><label class="titel" for="de-${id}">${esc(t("text_auf_bild"))}</label>
        <input class="gross" id="de-${id}" data-e="de" value="${esc(d.de)}" placeholder="${esc(t("text_auf_bild_ph"))}" title="${esc(t("h_text_auf_bild"))}" autocomplete="off" spellcheck="false" lang="de">
        <span class="klein">${esc(d.original)}</span>
        ${d.kollision ? `<label class="klein" title="${esc(t("h_ersetzen"))}"><input type="checkbox" data-e="ersetzen"${d.ersetzen ? " checked" : ""}> ${esc(t("ersetzen"))}</label>` : ""}</div>
      <div class="f"><label class="titel" for="es-${id}">${esc(t("es_feld"))}${chipZs()} <span class="klein">${esc(t("optional"))}</span></label>
        <div class="mit-knopf"><input class="${auto ? "ist-auto" : ""}" id="es-${id}" data-e="es" ${zsAttr()} title="${esc(t("h_es_feld"))}" value="${esc(d.es || "")}" placeholder="${esc(t("es_spaeter_ph"))}" autocomplete="off">
          <button type="button" class="knopf symbolknopf" data-e-aktion="uebersetzen" title="${esc(t("uebersetzen_titel"))}" aria-label="${esc(t("uebersetzen_titel"))}">🌐</button></div>
        <div data-teil="vorschlag">${vorschlagHTML(S.vorschlaege["e:" + d.id])}</div></div>`
      : `<div class="f" style="grid-column: span 2">${pruefliste(d.meldungen)}</div>`}
      <div class="status-zelle" data-teil="status" aria-live="polite">${entwurfStatus(d)}</div>
      <div class="knoepfe-klein">
        ${lesbar ? `<button class="knopf klein haupt" data-e-aktion="uebernehmen" title="${esc(t("h_uebernehmen"))}"${d.ok ? "" : " disabled"}>${esc(t("uebernehmen_kurz"))}</button>
        <button class="knopf klein" data-e-aktion="details" aria-expanded="${offen}" title="${esc(t("h_details"))}">${esc(offen ? t("details_zu") : t("details"))}</button>` : ""}
        <button class="knopf klein leise gefahr" data-e-aktion="verwerfen" title="${esc(t("h_verwerfen"))}">${esc(t("verwerfen"))}</button>
      </div>
    </div>
    ${lesbar ? `<div class="entwurf-details" data-teil="details"${offen ? "" : " hidden"}>
      <div class="bilder">
        <div class="bildchen original"><img alt="" data-art="original" ${offen ? "src" : "data-src"}="${entwurfBildUrl(d, "original")}"><span class="etikett">${esc(t("original"))}</span></div>
        <div class="drehen"><button class="knopf klein rund" data-e-aktion="links" aria-label="${esc(t("drehen_links"))}" title="${esc(t("drehen_links"))}">↺</button>
          <button class="knopf klein rund" data-e-aktion="rechts" aria-label="${esc(t("drehen_rechts"))}" title="${esc(t("drehen_rechts"))}">↻</button></div>
        <div class="bildchen kartenform"><img alt="" data-art="vorn" ${offen ? "src" : "data-src"}="${entwurfBildUrl(d, "vorn")}"><span class="etikett">${esc(t("vorderseite"))}${esrgan ? " · " + esc(t("schnellvorschau")) : ""}</span></div>
      </div>
      <div class="felder">
        <div class="f"><span>${esc(t("ausschnitt"))}</span><div class="segmente" role="radiogroup">${fitKnopf("contain", t("fit_contain"))}${fitKnopf("cover", t("fit_cover"))}</div>
          <span class="tipp">★ = ${esc(t("empfohlen_bild"))}</span></div>
        <div data-teil="meldungen" aria-live="polite">${pruefliste(d.meldungen)}</div>
        ${esrgan ? `<p class="klein" style="margin:0">${esc(t("ki_vorschau", S.status.ki_name || "Real-ESRGAN"))}</p>` : ""}
      </div>
    </div>` : ""}
  </article>`;
}
function zeichneHochladen() {
  const fehler = S.hochladen.filter(h => h.fehler);
  let html = "";
  if (S.upl.gesamt) {
    const p = Math.round(S.upl.fertig / S.upl.gesamt * 100);
    html += `<div class="hochladen-stand">${S.upl.fertig < S.upl.gesamt ? enteHTML(t("hochladen_stand", S.upl.fertig, S.upl.gesamt), true) : `<div>${esc(t("hochladen_stand", S.upl.fertig, S.upl.gesamt))}</div>`}
      <div class="fortschritt" aria-hidden="true"><span style="width:${p}%"></span></div></div>`;
  }
  if (fehler.length) html += `<div class="laedt">${pruefliste(fehler.map(h => ({ stufe: "fehler", text: t("nicht_hinzugefuegt", h.name) + " – " + h.fehler })))}</div>`;
  $("#hochladen").innerHTML = html;
}
function zeichneStapel() {
  const n = S.entwuerfe.length, bereit = S.entwuerfe.filter(d => d.ok), mitEs = bereit.filter(d => String(d.es || "").trim()).length;
  $("#entwurf-alle").hidden = !n;
  $("#entwurf-zahlen").innerHTML = t("stapel_zahlen", n, bereit.length, mitEs);
  const b = $("#alle-uebernehmen"); b.textContent = t("alle_uebernehmen_n", bereit.length); b.disabled = !bereit.length || S.beschaeftigt;
  const u = $("#entwuerfe-uebersetzen");
  u.hidden = !S.entwuerfe.some(d => d.lesbar && String(d.de || "").trim() && !String(d.es || "").trim());
  u.disabled = S.beschaeftigt;
}
function zeichneEntwuerfe() {
  zeichneHochladen();
  $("#entwurf-liste").innerHTML = S.entwuerfe.map(entwurfHTML).join("");
  zeichneStapel(); zaehler();
}
function aktualisiereEntwurf(d, bilderNeu) {
  const i = S.entwuerfe.findIndex(x => x.id === d.id); if (i >= 0) S.entwuerfe[i] = d;
  const el = $(`.entwurf[data-id="${CSS.escape(d.id)}"]`); if (!el) return zeichneEntwuerfe();
  if (bilderNeu || !!$('[data-e="ersetzen"]', el) !== !!d.kollision) {
    const aktiv = document.activeElement, feld = aktiv && el.contains(aktiv) ? aktiv.dataset.e : null;
    const pos = feld && aktiv.selectionStart != null ? aktiv.selectionStart : null;
    el.outerHTML = entwurfHTML(d);
    if (feld) { const inp = $(`.entwurf[data-id="${CSS.escape(d.id)}"] [data-e="${feld}"]`); if (inp) { inp.focus(); try { if (pos != null) inp.setSelectionRange(pos, pos); } catch (e) { /* egal */ } } }
  } else {
    const m = $('[data-teil="meldungen"]', el); if (m) m.innerHTML = pruefliste(d.meldungen);
    $('[data-teil="status"]', el).innerHTML = entwurfStatus(d);
    const b = $('[data-e-aktion="uebernehmen"]', el); if (b) b.disabled = !d.ok;
    el.classList.toggle("bereit", !!d.ok);
  }
  zeichneStapel(); zaehler();
}
async function pruefeEntwurf(id, aenderung, bilderNeu = false) {
  try { aktualisiereEntwurf(await api("/api/entwurf-pruefen", { methode: "POST", daten: { id, ...aenderung } }), bilderNeu); }
  catch (e) { fehlerToast(e); if (e.status === 400) await ladeEntwuerfe().then(zeichneEntwuerfe).catch(() => {}); }
}
const entwurfUhren = {};
function pruefeEntwurfSpaeter(id, aenderung) {          // je Bild eigene Wartezeit – mehrere Bilder lassen sich zügig nacheinander beschriften
  clearTimeout(entwurfUhren[id]); entwurfUhren[id] = setTimeout(() => { delete entwurfUhren[id]; pruefeEntwurf(id, aenderung); }, 300);
}
const MAX_MB = 40;
async function neueBilder(dateien) {
  location.hash = "#bild";
  const liste = [...dateien]; if (!liste.length) return;
  const vorher = S.entwuerfe.length;
  S.upl.gesamt += liste.length; zeichneHochladen();
  const schlange = liste.slice();
  async function arbeiter() {
    while (schlange.length) {
      const f = schlange.shift(), h = { name: f.name };
      if (f.size > MAX_MB * 1024 * 1024) h.fehler = t("zu_gross", f.name, MAX_MB);
      else {
        try {
          const d = await api(url("/api/entwurf", { name: f.name }), { methode: "POST", roh: f });
          S.entwuerfe.push(d);
          $("#entwurf-liste").insertAdjacentHTML("beforeend", entwurfHTML(d));
          if (d.lesbar && !String(d.es || "").trim()) automatischUebersetzen("e:" + d.id, d.de, v => fuelleEntwurf(d.id, v));
        } catch (e) { h.fehler = e.message; }
      }
      if (h.fehler) S.hochladen.push(h);
      S.upl.fertig++; zeichneHochladen(); zeichneStapel(); zaehler();
    }
  }
  await Promise.all([arbeiter(), arbeiter(), arbeiter()]);          // drei Bilder gleichzeitig
  if (S.upl.fertig >= S.upl.gesamt) S.upl = { gesamt: 0, fertig: 0 };
  if (vorher === 0 && S.entwuerfe.length === 1) { S.offeneEntwuerfe.add(S.entwuerfe[0].id); zeichneEntwuerfe(); }
  zeichneHochladen();
  const leer = $$('.entwurf input[data-e="de"]').find(i => !i.value); if (leer) leer.focus();
  setTimeout(() => { S.hochladen = S.hochladen.filter(x => !x.fehler); zeichneHochladen(); }, 20000);
}
function fuelleEntwurf(id, v) {
  const d = S.entwuerfe.find(x => x.id === id); if (!d || !v || !v.vorschlag) return false;
  S.vorschlaege["e:" + id] = v;
  const el = $(`.entwurf[data-id="${CSS.escape(id)}"]`);
  if (String(d.es || "").trim()) { if (el) $('[data-teil="vorschlag"]', el).innerHTML = vorschlagHTML(v); return false; }
  d.es = v.vorschlag; d.es_auto = v.vorschlag;
  if (el) { const inp = $('[data-e="es"]', el); inp.value = d.es; inp.classList.add("ist-auto"); $('[data-teil="vorschlag"]', el).innerHTML = vorschlagHTML(v); }
  pruefeEntwurf(id, { de: d.de, es: d.es, es_auto: d.es_auto });
  return true;
}
$("#dateiwahl").addEventListener("change", e => { neueBilder(e.target.files); e.target.value = ""; });
$("#entwurf-liste").addEventListener("input", e => {
  const el = e.target.closest(".entwurf"); if (!el) return;
  const id = el.dataset.id, d = S.entwuerfe.find(x => x.id === id), f = e.target.dataset.e; if (!d || !f) return;
  if (f === "de") { d.de = e.target.value; pruefeEntwurfSpaeter(id, { de: d.de }); }
  if (f === "es") {
    d.es = e.target.value; e.target.classList.toggle("ist-auto", !!d.es_auto && d.es === d.es_auto);
    pruefeEntwurfSpaeter(id, { de: d.de, es: d.es, es_auto: d.es_auto || "" });
  }
});
$("#entwurf-liste").addEventListener("change", e => {
  const el = e.target.closest(".entwurf"); if (!el) return;
  const id = el.dataset.id, d = S.entwuerfe.find(x => x.id === id), f = e.target.dataset.e; if (!d) return;
  if (f === "fit") { d.fit = e.target.value; pruefeEntwurf(id, { de: d.de, fit: d.fit }, true); }
  if (f === "ersetzen") pruefeEntwurf(id, { de: d.de, ersetzen: e.target.checked });
  if (f === "de" && !String(d.es || "").trim()) automatischUebersetzen("e:" + id + ":" + d.de, d.de, v => fuelleEntwurf(id, v));
});
$("#entwurf-liste").addEventListener("keydown", e => {
  if (e.key === "Enter" && (e.target.dataset.e === "de" || e.target.dataset.e === "es")) {
    e.preventDefault(); const b = $('[data-e-aktion="uebernehmen"]', e.target.closest(".entwurf")); if (b && !b.disabled) b.click();
  }
});
async function uebernimm(d) {
  const r = await api("/api/entwurf-uebernehmen", { methode: "POST", daten: { id: d.id, de: d.de, es: d.es || "", es_auto: d.es_auto || "", drehung: d.drehung, fit: d.fit, ersetzen: d.ersetzen } });
  uebernehmeKarten(r.karten); S.v++;
  S.entwuerfe = S.entwuerfe.filter(x => x.id !== d.id); S.offeneEntwuerfe.delete(d.id); delete S.vorschlaege["e:" + d.id];
  if (!String(d.es || "").trim() && !S.extra.includes(r.name)) S.extra.unshift(r.name);
  return { name: r.name, beschriftet: !!String(d.es || "").trim(), auto: !!(d.es && d.es === d.es_auto) };
}
$("#entwurf-liste").addEventListener("click", async e => {
  const chip = e.target.closest("[data-chip]");
  if (chip) {
    const el = chip.closest(".entwurf"), d = S.entwuerfe.find(x => x.id === el.dataset.id); if (!d) return;
    d.es = chip.dataset.chip; d.es_auto = chip.dataset.chip;
    const inp = $('[data-e="es"]', el); inp.value = d.es; inp.classList.add("ist-auto");
    return pruefeEntwurf(d.id, { de: d.de, es: d.es, es_auto: d.es_auto });
  }
  const b = e.target.closest("[data-e-aktion]"); if (!b) return;
  const el = b.closest(".entwurf"), id = el.dataset.id, d = S.entwuerfe.find(x => x.id === id); if (!d) return;
  const a = b.dataset.eAktion;
  if (a === "links" || a === "rechts") { d.drehung = ((d.drehung || 0) + (a === "rechts" ? 90 : 270)) % 360; S.v++; return pruefeEntwurf(id, { de: d.de, drehung: d.drehung }, true); }
  if (a === "details") {
    const auf = !S.offeneEntwuerfe.has(id); auf ? S.offeneEntwuerfe.add(id) : S.offeneEntwuerfe.delete(id);
    const det = $('[data-teil="details"]', el); det.hidden = !auf;
    $$("img[data-src]", det).forEach(i => { i.src = i.dataset.src; i.removeAttribute("data-src"); });
    b.setAttribute("aria-expanded", String(auf)); b.textContent = auf ? t("details_zu") : t("details"); return;
  }
  if (a === "uebersetzen") {
    b.disabled = true;
    try {
      const v = await holeVorschlag(d.de); if (!v) return;
      S.vorschlaege["e:" + id] = v;
      if (v.vorschlag) { d.es = v.vorschlag; d.es_auto = v.vorschlag; const inp = $('[data-e="es"]', el); inp.value = d.es; inp.classList.add("ist-auto"); }
      $('[data-teil="vorschlag"]', el).innerHTML = vorschlagHTML(v);
      if (v.vorschlag) await pruefeEntwurf(id, { de: d.de, es: d.es, es_auto: d.es_auto });
    } catch (err) { $('[data-teil="vorschlag"]', el).innerHTML = vorschlagFehlerHTML(err); }
    finally { const n = $(`.entwurf[data-id="${CSS.escape(id)}"] [data-e-aktion="uebersetzen"]`); if (n) n.disabled = false; }
    return;
  }
  if (a === "verwerfen") {
    try { await api("/api/entwurf-weg", { methode: "POST", daten: { id } }); } catch (err) { /* schon weg */ }
    S.entwuerfe = S.entwuerfe.filter(x => x.id !== id); S.offeneEntwuerfe.delete(id); return zeichneEntwuerfe();
  }
  if (a === "uebernehmen") {
    b.disabled = true;
    try {
      const r = await uebernimm(d);
      if (S.entwuerfe.length) { zeichneEntwuerfe(); toast(t("uebernommen", r.name), r.beschriftet ? {} : { aktion: { label: t("jetzt_beschriften"), fn: () => oeffneEditor(r.name) } }); }
      else if (r.beschriftet) { zeichneEntwuerfe(); toast(t("karte_fertig", r.name), r.auto ? { aktion: { label: t("in_tabelle_pruefen"), fn: () => { location.hash = "#tabelle"; } } } : {}); }
      else oeffneEditor(r.name);
    } catch (err) { b.disabled = false; fehlerToast(err); }
  }
});
async function entwuerfeJetztPruefen() {           // noch wartende Prüfungen sofort erledigen
  const ids = Object.keys(entwurfUhren);
  ids.forEach(id => { clearTimeout(entwurfUhren[id]); delete entwurfUhren[id]; });
  await Promise.all(ids.map(id => { const d = S.entwuerfe.find(x => x.id === id);
    return d ? pruefeEntwurf(id, { de: d.de, es: d.es || "", es_auto: d.es_auto || "" }) : null; }));
}
$("#alle-uebernehmen").addEventListener("click", async () => {
  S.beschaeftigt = true; zeichneStapel();
  await entwuerfeJetztPruefen();
  const bereit = S.entwuerfe.filter(x => x.ok);
  if (!bereit.length) { S.beschaeftigt = false; zeichneStapel(); return; }
  let ohneEs = 0, mitEs = 0, auto = 0, fehler = 0;
  for (const d of bereit) {
    try { const r = await uebernimm(d); r.beschriftet ? mitEs++ : ohneEs++; if (r.auto) auto++; }
    catch (err) { fehler++; fehlerToast(err); }
  }
  S.beschaeftigt = false; zeichneEntwuerfe();
  toast(t("stapel_fertig", mitEs + ohneEs, mitEs, ohneEs) + (fehler ? " " + t("stapel_fehler", fehler) : ""),
    auto && !ohneEs ? { aktion: { label: t("in_tabelle_pruefen"), fn: () => { location.hash = "#tabelle"; } } } : {});
  if (ohneEs && !S.entwuerfe.length) location.hash = "#beschriften";
});
$("#entwuerfe-uebersetzen").addEventListener("click", async () => {
  const offen = S.entwuerfe.filter(d => d.lesbar && String(d.de || "").trim() && !String(d.es || "").trim());
  await alleUebersetzen($("#entwuerfe-uebersetzen"), offen.map(d => ({ de: d.de, fuellen: v => fuelleEntwurf(d.id, v) })));
  zeichneStapel();
});
let ziehZaehler = 0;
const ABLAGE_ZIELE = "[data-gansbild], .editor:not([data-neu]) .bilder";      // Gänse-Bild bzw. neues Bild einer Karte
function gansZiel(e) { return e.target && e.target.closest ? e.target.closest(ABLAGE_ZIELE) : null; }
window.addEventListener("dragenter", e => { if ([...e.dataTransfer.types].includes("Files")) { ziehZaehler++; $("#ablage").hidden = !!gansZiel(e); } });
window.addEventListener("dragleave", () => { ziehZaehler = Math.max(0, ziehZaehler - 1); if (!ziehZaehler) { $("#ablage").hidden = true; $$(ABLAGE_ZIELE).forEach(g => g.classList.remove("ziel")); } });
window.addEventListener("dragover", e => {
  e.preventDefault(); const g = gansZiel(e);
  $$(ABLAGE_ZIELE).forEach(x => x.classList.toggle("ziel", x === g));
  if (ziehZaehler) $("#ablage").hidden = !!g;
});
window.addEventListener("drop", e => {
  e.preventDefault(); ziehZaehler = 0; $("#ablage").hidden = true;
  const g = gansZiel(e); $$(ABLAGE_ZIELE).forEach(x => x.classList.remove("ziel"));
  if (!e.dataTransfer.files.length) return;
  if (g && g.matches("[data-gansbild]")) ladeGansbild(e.dataTransfer.files[0]);
  else if (g) ladeErsatz(g.closest(".editor").dataset.bild, e.dataTransfer.files[0]);
  else neueBilder(e.dataTransfer.files);
});

/* ===================== Schritt 2: Karten beschriften (auch mehrere auf einmal) ===================== */
function rateText(name) { const s = name.replace(/\.[^.]+$/, ""); return /^gans[-_ ]/i.test(s) ? "Gans " + s.slice(5).replace(/[-_]+/g, " ") : ""; }
function offeneKarten() {
  const liste = [];
  const gesehen = new Set();
  for (const b of S.extra) {
    const k = S.karten.find(x => x.bild === b);
    if (k) { liste.push({ ...k }); gesehen.add(b); }
    else if (S.ohne.includes(b)) { liste.push({ bild: b, de: rateText(b), es: "", notiz: "", fit: "contain", existiert: true, aktiv: true, neu: true }); gesehen.add(b); }
  }
  for (const k of S.karten) if (k.offen && !gesehen.has(k.bild)) { liste.push({ ...k }); gesehen.add(k.bild); }
  for (const b of S.ohne) if (!gesehen.has(b)) liste.push({ bild: b, de: rateText(b), es: "", notiz: "", fit: "contain", existiert: true, aktiv: true, neu: true });
  return liste;
}
function oeffneEditor(bild) {
  S.extra = [bild, ...S.extra.filter(b => b !== bild)];
  location.hash = "#beschriften"; zeige();
  const el = $(`.editor[data-bild="${CSS.escape(bild)}"] input[data-k="es"]`);
  if (el) { el.closest(".editor").scrollIntoView({ behavior: "smooth", block: "start" }); el.focus(); }
}
const ZEICHEN = ["á", "é", "í", "ó", "ú", "ñ", "ü", "¿", "¡", "Á", "É", "Ñ"];
const zeichenListe = (code = ZS.code) => code === "es" ? ZEICHEN : (zsInfo(code).sonderzeichen || []);   // Leiste je Sprache (Katalog)
function weitereSprachenHTML(k, id) {                      // Editor: weitere Rückseiten (ein Feld je installierter Sprache)
  if (!zsMehrere()) return "";
  const st = (S.stand[k.bild] || {}).rs || {}, codes = ZS.installiert.filter(c => c !== ZS.code);
  const wert = c => st[c] ?? (k.rueckseiten || {})[c] ?? "";
  const n = codes.filter(c => String(wert(c)).trim()).length;
  return `<details class="weitere-sprachen"${S.weitereOffen.has(k.bild) ? " open" : ""} data-weitere><summary title="${esc(t("h_weitere_sprachen"))}">${esc(t("weitere_sprachen", n, codes.length))}</summary>
    ${codes.map(c => `<div class="f rs-feld"><label class="titel" for="${id}-rs-${esc(c)}">${sprachChip(c, { aktuell: false })} ${esc(zsName(c))}</label>
      <div class="mit-knopf"><input id="${id}-rs-${esc(c)}" data-rs="${esc(c)}" data-auto="${esc(((S.stand[k.bild] || {}).rs_auto || {})[c] || "")}" value="${esc(wert(c))}" ${zsAttr(c)} autocomplete="off" placeholder="${esc(t("rs_ph", zsName(c)))}">
        <button type="button" class="knopf symbolknopf" data-k-aktion="uebersetzen-rs" data-rs-ziel="${esc(c)}" title="${esc(t("uebersetzen_titel"))}" aria-label="${esc(t("uebersetzen_titel"))}">🌐</button></div></div>`).join("")}</details>`;
}
function editorHTML(k) {
  const st = S.stand[k.bild] || {};
  const de = st.de ?? k.de ?? "", es = st.es ?? k.es ?? "", notiz = st.notiz ?? k.notiz ?? "", auto = st.es_auto || "";
  const id = "k" + Math.abs([...k.bild].reduce((h, c) => (h * 31 + c.charCodeAt(0)) | 0, 7));
  return `<article class="editor" data-bild="${esc(k.bild)}"${k.neu ? " data-neu" : ""}>
    <div class="bilder">
      <div class="bildchen kartenform">${k.existiert === false ? `<span class="fehlt-bild">${esc(t("bild_fehlt"))}</span>`
        : `<img alt="" data-seite="vorn" data-bild="${esc(k.bild)}" src="${vorschauUrl(k, "vorn")}">`}<span class="etikett">${esc(t("vorderseite"))}</span></div>
      <div class="bildchen kartenform"><img alt="" data-teil="hinten" src="${es.trim() ? vorschauUrl(k, "hinten", es) : ""}"${es.trim() ? "" : " hidden"}><span class="etikett">${esc(t("rueckseite"))}${chipZs()}</span></div>
      ${k.neu ? "" : `<button type="button" class="knopf klein" data-k-aktion="bild-aendern" title="${esc(t("h_bild_aendern"))}">${esc(t(k.existiert === false ? "bild_hinzufuegen" : "bild_aendern"))}</button>
      <input type="file" accept="${BILD_ACCEPT}" hidden data-k-datei>${!(S.status && S.status.ki_bild === false) ? `
      <button type="button" class="knopf klein" data-k-aktion="ki-bild" title="${esc(t("h_ki_editor"))}">${esc(t("ki_editor_knopf"))}</button>` : ""}`}
    </div>
    <div class="felder">
      <div class="oben"><span class="datei">${esc(k.bild)}</span>${k.neu ? ` <span class="marke-q warn">${esc(t("neu_ohne_zeile"))}</span>` : ""}</div>
      <div class="f"><label class="titel" for="${id}-es">${esc(t("es_feld"))}${chipZs()}</label>
        <div class="mit-knopf"><input class="gross${auto && auto === es ? " ist-auto" : ""}" id="${id}-es" data-k="es" data-auto="${esc(auto)}" title="${esc(t("h_es_feld"))}" value="${esc(es)}" placeholder="${esc(t("es_ph"))}" autocomplete="off" ${zsAttr()}>
          <button type="button" class="knopf symbolknopf" data-k-aktion="uebersetzen" title="${esc(t("uebersetzen_titel"))}" aria-label="${esc(t("uebersetzen_titel"))}">🌐</button></div>
        <div data-teil="vorschlag">${vorschlagHTML(S.vorschlaege["k:" + k.bild])}</div></div>
      ${zeichenListe().length ? `<div class="zeichen" aria-label="${esc(t("sonderzeichen"))}"><span class="tipp">${esc(t("sonderzeichen"))}</span>${zeichenListe().map(z => `<button type="button" data-zeichen="${esc(z)}" title="${esc(t("h_zeichen"))}">${esc(z)}</button>`).join("")}</div>` : ""}
      ${weitereSprachenHTML(k, id)}
      <div class="zwei">
        <div class="f"><label class="titel" for="${id}-de">${esc(t("de_feld"))}</label><input id="${id}-de" data-k="de" value="${esc(de)}" lang="de" autocomplete="off" title="${esc(t("h_de_feld"))}"></div>
        <div class="f"><label class="titel" for="${id}-notiz">${esc(t("notiz_feld"))}</label><input id="${id}-notiz" data-k="notiz" value="${esc(notiz)}" placeholder="${esc(t("notiz_ph"))}" autocomplete="off" title="${esc(t("h_notiz"))}"></div>
      </div>
      <div data-teil="meldungen" aria-live="polite"></div>
      ${k.lernen && k.lernen.anzahl ? `<p class="lern-hinweis" data-teil="lern-hinweis" hidden>🎓 ${esc(t("ln_hinweis_speichern"))}</p>` : ""}
      <div class="knopfzeile">${k.neu ? `<button class="knopf leise gefahr" data-k-aktion="bild-weg" title="${esc(t("h_bild_entfernen"))}">${esc(t("bild_entfernen"))}</button>` : ""}
        <div class="rechts"><button class="knopf leise" data-k-aktion="spaeter" title="${esc(t("h_spaeter"))}">${esc(t("spaeter"))}</button>
        <button class="knopf haupt" data-k-aktion="speichern" title="${esc(t("h_karte_speichern"))}" disabled>${esc(t("karte_speichern"))}</button></div></div>
    </div>
    ${S.ersatz[k.bild] ? ersatzHTML(S.ersatz[k.bild]) : ""}
  </article>`;
}
function zeichneEditorLeiste() {
  const eds = $$(".editor"), n = eds.length;
  $("#editor-leiste").hidden = n < 1;
  if (!n) return;
  const ohneEs = eds.filter(el => !$('input[data-k="es"]', el).value.trim()).length;
  const bereit = eds.filter(el => !$('[data-k-aktion="speichern"]', el).disabled).length;
  $("#editor-zahlen").innerHTML = t("editor_zahlen", n, bereit);
  $("#editoren-uebersetzen").hidden = !ohneEs; $("#editoren-uebersetzen").disabled = S.beschaeftigt;
  const s = $("#editoren-speichern"); s.textContent = t("alle_speichern_n", bereit); s.disabled = !bereit || S.beschaeftigt;
}
function zeichneEditoren() {
  const liste = offeneKarten();
  $("#editor-liste").innerHTML = liste.length ? liste.map(editorHTML).join("") : `<div class="flaeche leer"><img src="/symbol.svg" alt="">
    <h2>${esc(t("alles_beschriftet"))}</h2><p>${esc(t("alles_beschriftet_text"))}</p>
    <div class="knopfzeile"><a class="knopf" href="#bild">${esc(t("noch_ein_bild"))}</a><a class="knopf" href="#tabelle">${esc(t("zur_tabelle"))}</a><a class="knopf haupt" href="#erzeugen">${esc(t("weiter_erzeugen"))}</a></div></div>`;
  liste.forEach(k => pruefeKarte(k.bild));
  zeichneEditorLeiste(); zaehler();
  for (const k of liste) {                                    // „automatisch übersetzen“: leere Felder füllen
    const w = S.stand[k.bild]; const es = w ? w.es : k.es, de = w ? w.de : k.de;
    if (!String(es || "").trim() && String(de || "").trim()) automatischUebersetzen("k:" + k.bild + ":" + de, de, v => fuelleEditor(k.bild, v));
  }
}
function editorWerte(el) {
  const w = {}; $$("[data-k]", el).forEach(i => { w[i.dataset.k] = i.value; });
  w.es_auto = $('input[data-k="es"]', el).dataset.auto || "";
  const rs = $$("[data-rs]", el); if (rs.length) { w.rs = {}; w.rs_auto = {}; rs.forEach(i => { w.rs[i.dataset.rs] = i.value; w.rs_auto[i.dataset.rs] = i.dataset.auto || ""; }); }
  return w;
}
async function pruefeKarte(bild) {
  const el = $(`.editor[data-bild="${CSS.escape(bild)}"]`); if (!el) return;
  const w = editorWerte(el);
  try {
    const r = await api("/api/karte-pruefen", { methode: "POST", daten: { bild, ...w } });
    const jetzt = editorWerte(el); if (jetzt.es !== w.es || jetzt.de !== w.de) return;      // inzwischen weitergetippt
    $('[data-teil="meldungen"]', el).innerHTML = pruefliste(r.meldungen);
    $('[data-k-aktion="speichern"]', el).disabled = !r.ok;
    $('input[data-k="es"]', el).closest(".f").classList.toggle("fehlt", !w.es.trim());
  } catch (e) { fehlerToast(e); }
  zeichneEditorLeiste();
}
const karteUhren = {};
function pruefeKarteSpaeter(bild) { clearTimeout(karteUhren[bild]); karteUhren[bild] = setTimeout(() => { delete karteUhren[bild]; pruefeKarte(bild); }, 300); }
const rueckUhren = {};
function rueckseiteSpaeter(bild) {
  clearTimeout(rueckUhren[bild]);
  rueckUhren[bild] = setTimeout(() => {
    const el = $(`.editor[data-bild="${CSS.escape(bild)}"]`); if (!el) return;
    const es = $('input[data-k="es"]', el).value, img = $('[data-teil="hinten"]', el);
    const k = S.karten.find(x => x.bild === bild) || { bild, fit: "contain" };
    img.hidden = !es.trim(); if (es.trim()) img.src = vorschauUrl(k, "hinten", es);
  }, 450);
}
function setzeEs(el, text, auto) {
  const inp = $('input[data-k="es"]', el); inp.value = text; inp.dataset.auto = auto ? text : "";
  inp.classList.toggle("ist-auto", !!auto);
  const bild = el.dataset.bild; S.stand[bild] = editorWerte(el);
  $('[data-k-aktion="speichern"]', el).disabled = true; pruefeKarte(bild); rueckseiteSpaeter(bild);
}
function fuelleEditor(bild, v) {
  if (!v || !v.vorschlag) return false;
  S.vorschlaege["k:" + bild] = v;
  const el = $(`.editor[data-bild="${CSS.escape(bild)}"]`); if (!el) return false;
  $('[data-teil="vorschlag"]', el).innerHTML = vorschlagHTML(v);
  if ($('input[data-k="es"]', el).value.trim()) return false;
  setzeEs(el, v.vorschlag, true); return true;
}
/* ----- Karten-Editor: neues Bild für eine vorhandene Karte – geprüft wie in Schritt 1, mit „Rückgängig“ ----- */
function ersatzHTML(d) {
  const id = esc(d.id);
  const fitKnopf = (wert, label) => `<label title="${esc(t("h_fit_" + wert))}"><input type="radio" name="efit-${id}" value="${wert}" data-k-ersatz="fit"${d.fit === wert ? " checked" : ""}><span>${esc(label)}${d.fit_empfehlung === wert ? `<span class="empf" title="${esc(t("empfohlen"))}">★</span>` : ""}</span></label>`;
  return `<section class="ersatz" aria-label="${esc(t("ersatz_titel"))}">
    <div class="bilder">${d.lesbar ? `<div class="bildchen kartenform"><img alt="" src="${entwurfBildUrl(d, "vorn")}"><span class="etikett">${esc(t("ersatz_neu"))}</span></div>
      <div class="drehen"><button type="button" class="knopf klein rund" data-k-aktion="ersatz-links" aria-label="${esc(t("drehen_links"))}" title="${esc(t("drehen_links"))}">↺</button>
        <button type="button" class="knopf klein rund" data-k-aktion="ersatz-rechts" aria-label="${esc(t("drehen_rechts"))}" title="${esc(t("drehen_rechts"))}">↻</button></div>`
      : `<div class="bildchen unlesbar"><span class="fehlt-bild">${esc(d.original)}</span></div>`}</div>
    <div class="felder"><b>${esc(t("ersatz_titel"))}</b>
      ${d.lesbar ? `<div class="f"><span>${esc(t("ausschnitt"))}</span><div class="segmente" role="radiogroup" aria-label="${esc(t("ausschnitt"))}">${fitKnopf("contain", t("fit_contain"))}${fitKnopf("cover", t("fit_cover"))}</div>
        <span class="tipp">★ = ${esc(t("empfohlen_bild"))}</span></div>` : ""}
      <div aria-live="polite">${pruefliste(d.meldungen)}</div>
      <div class="knopfzeile"><button type="button" class="knopf haupt" data-k-aktion="ersatz-uebernehmen" title="${esc(t("h_ersatz_uebernehmen"))}"${d.ok ? "" : " disabled"}>${esc(t("ersatz_uebernehmen"))}</button>
        <button type="button" class="knopf leise" data-k-aktion="ersatz-verwerfen" title="${esc(t("h_ersatz_verwerfen"))}">${esc(t("verwerfen"))}</button></div>
    </div></section>`;
}
function zeichneEditor(bild) {                            // nur diesen einen Editor neu zeichnen (Getipptes steht in S.stand)
  const el = $(`.editor[data-bild="${CSS.escape(bild)}"]`); if (!el) return;
  const k = offeneKarten().find(x => x.bild === bild); if (!k) return zeichneEditoren();
  el.outerHTML = editorHTML(k); pruefeKarte(bild);
}
async function ladeErsatz(bild, f) {
  if (!f) return;
  if (f.size > MAX_MB * 1024 * 1024) { toast(t("zu_gross", f.name, MAX_MB), { fehler: true }); return; }
  const vorher = S.ersatz[bild];
  try {
    S.ersatz[bild] = await api(url("/api/entwurf", { name: f.name, karte: bild }), { methode: "POST", roh: f });
    if (vorher) api("/api/entwurf-weg", { methode: "POST", daten: { id: vorher.id } }).catch(() => {});
    zeichneEditor(bild);
    const sek = $(`.editor[data-bild="${CSS.escape(bild)}"] .ersatz`); if (sek) sek.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (e) { fehlerToast(e); }
}
async function pruefeErsatz(bild, aenderung) {
  const d = S.ersatz[bild]; if (!d) return;
  try { S.ersatz[bild] = await api("/api/entwurf-pruefen", { methode: "POST", daten: { id: d.id, ...aenderung } }); }
  catch (e) { fehlerToast(e); if (e.status === 400) delete S.ersatz[bild]; }
  zeichneEditor(bild);
}
function umbenennen(alt, neu) { if (alt !== neu) S.extra = S.extra.map(x => x === alt ? neu : x); }
async function uebernimmErsatz(bild) {
  const d = S.ersatz[bild]; if (!d) return;
  try {
    const r = await api("/api/entwurf-uebernehmen", { methode: "POST", daten: { id: d.id, drehung: d.drehung, fit: d.fit } });
    delete S.ersatz[bild]; uebernehmeKarten(r.karten); S.v++; umbenennen(bild, r.name); zeichneEditor(bild);
    toast(t("ersatz_ok"), { aktion: { label: t("rueckgaengig"), fn: async () => {
      try {
        uebernehmeKarten(await api("/api/karte-bild-zurueck", { methode: "POST", daten: r.rueckgaengig }));
        S.v++; umbenennen(r.name, bild); zeichneEditor(r.name); toast(t("ersatz_zurueck_ok"));
      } catch (e) { fehlerToast(e); }
    } } });
  } catch (e) { fehlerToast(e); pruefeErsatz(bild, {}); }
}
async function verwirfErsatz(bild) {
  const d = S.ersatz[bild]; if (!d) return;
  delete S.ersatz[bild]; zeichneEditor(bild);
  try { await api("/api/entwurf-weg", { methode: "POST", daten: { id: d.id } }); } catch (e) { /* schon weg */ }
}
$("#editor-liste").addEventListener("toggle", e => {
  const d = e.target.closest && e.target.closest("[data-weitere]"); if (!d) return;
  const bild = d.closest(".editor").dataset.bild; d.open ? S.weitereOffen.add(bild) : S.weitereOffen.delete(bild);
}, true);
$("#editor-liste").addEventListener("input", e => {
  const el = e.target.closest(".editor"); if (!el || !(e.target.dataset.k || e.target.dataset.rs)) return;
  const bild = el.dataset.bild;
  if (e.target.dataset.k === "es" || e.target.dataset.rs) e.target.classList.toggle("ist-auto", !!e.target.dataset.auto && e.target.value === e.target.dataset.auto);
  S.stand[bild] = editorWerte(el);
  $('[data-k-aktion="speichern"]', el).disabled = true;
  pruefeKarteSpaeter(bild);
  if (e.target.dataset.k === "es") rueckseiteSpaeter(bild);
});
$("#editor-liste").addEventListener("click", async e => {
  const z = e.target.closest("[data-zeichen]");
  if (z) {
    const el = z.closest(".editor"); const inp = $('input[data-k="es"]', el);
    const a = inp.selectionStart ?? inp.value.length, b = inp.selectionEnd ?? inp.value.length;
    inp.value = inp.value.slice(0, a) + z.dataset.zeichen + inp.value.slice(b); inp.focus(); inp.setSelectionRange(a + 1, a + 1);
    inp.dispatchEvent(new Event("input", { bubbles: true })); return;
  }
  const chip = e.target.closest("[data-chip]");
  if (chip) { setzeEs(chip.closest(".editor"), chip.dataset.chip, true); return; }
  const b = e.target.closest("[data-k-aktion]"); if (!b) return;
  const el = b.closest(".editor"); const bild = el.dataset.bild; const aktion = b.dataset.kAktion;
  if (aktion === "bild-aendern") { $("[data-k-datei]", el).click(); return; }
  if (aktion === "ki-bild") { const k = S.karten.find(x => x.bild === bild) || {}; const de = (S.stand[bild] && S.stand[bild].de) ?? k.de ?? "";
    oeffneKiBild({ karte: bild, wort: kiRest(de) }); return; }
  if (aktion === "ersatz-links" || aktion === "ersatz-rechts") {
    const d = S.ersatz[bild]; if (d) await pruefeErsatz(bild, { drehung: ((d.drehung || 0) + (aktion === "ersatz-rechts" ? 90 : 270)) % 360 });
    return;
  }
  if (aktion === "ersatz-uebernehmen") { b.disabled = true; await uebernimmErsatz(bild); return; }
  if (aktion === "ersatz-verwerfen") { await verwirfErsatz(bild); return; }
  if (aktion === "uebersetzen-rs") {                         // 🌐 je weiterer Sprache
    const ziel = b.dataset.rsZiel, inp = $(`[data-rs="${CSS.escape(ziel)}"]`, el); b.disabled = true;
    try {
      const v = await holeVorschlag($('input[data-k="de"]', el).value, ziel);
      if (v && v.vorschlag) { inp.value = v.vorschlag; inp.dataset.auto = v.vorschlag; inp.classList.add("ist-auto"); inp.dispatchEvent(new Event("input", { bubbles: true })); }
      else if (v) toast(t("kein_vorschlag", v.quelle || ""));
    } catch (err) { fehlerToast(err); }
    finally { b.disabled = false; }
    return;
  }
  if (aktion === "uebersetzen") {
    b.disabled = true;
    try {
      const v = await holeVorschlag($('input[data-k="de"]', el).value); if (!v) return;
      S.vorschlaege["k:" + bild] = v; $('[data-teil="vorschlag"]', el).innerHTML = vorschlagHTML(v);
      if (v.vorschlag) setzeEs(el, v.vorschlag, true);
    } catch (err) { $('[data-teil="vorschlag"]', el).innerHTML = vorschlagFehlerHTML(err); }
    finally { b.disabled = false; }
    return;
  }
  if (aktion === "spaeter") { S.extra = S.extra.filter(x => x !== bild); delete S.stand[bild];
    const k = S.karten.find(x => x.bild === bild); if (!k || k.offen || S.ohne.includes(bild)) { el.remove(); if (!$(".editor")) zeichneEditoren(); else zeichneEditorLeiste(); } else zeichneEditoren(); return; }
  if (aktion === "bild-weg") {
    try { const r = await api("/api/bild-weg", { methode: "POST", daten: { name: bild } }); toast(r.meldung); await ladeKarten(); S.extra = S.extra.filter(x => x !== bild); zeichneEditoren(); }
    catch (err) { fehlerToast(err); } return;
  }
  if (aktion === "speichern") await speichereKarte(el);
});
$("#editor-liste").addEventListener("change", e => {
  const el = e.target.closest(".editor"); if (!el) return;
  if (e.target.matches("[data-k-datei]")) { const f = e.target.files[0]; e.target.value = ""; ladeErsatz(el.dataset.bild, f); }
  else if (e.target.dataset.kErsatz === "fit") pruefeErsatz(el.dataset.bild, { fit: e.target.value });
});
$("#editor-liste").addEventListener("keydown", e => {
  if ((e.key === "Enter" && e.target.dataset.k) || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s")) {
    const el = e.target.closest(".editor"); if (!el) return; e.preventDefault();
    const b = $('[data-k-aktion="speichern"]', el); if (b && !b.disabled) speichereKarte(el); else pruefeKarte(el.dataset.bild);
  }
});
async function speichereEine(el) {
  const bild = el.dataset.bild, w = editorWerte(el), k = S.karten.find(x => x.bild === bild);
  const r = await api("/api/karte-speichern", { methode: "POST", daten: { bild, ...w, fit: k ? k.fit : "contain" } });
  S.extra = S.extra.filter(x => x !== bild); delete S.stand[bild]; delete S.vorschlaege["k:" + bild];
  return r;
}
async function speichereKarte(el) {
  const bild = el.dataset.bild, knopf = $('[data-k-aktion="speichern"]', el); knopf.disabled = true;
  try {
    const r = await speichereEine(el);
    uebernehmeKarten(r.karten); S.v++;
    toast(t("karte_gespeichert"));
    zeichneEditoren();
  } catch (err) {
    fehlerToast(err);
    if (err.daten && err.daten.meldungen) $('[data-teil="meldungen"]', el).innerHTML = pruefliste(err.daten.meldungen);
    pruefeKarte(bild);
  }
}
$("#editoren-speichern").addEventListener("click", async () => {
  S.beschaeftigt = true; zeichneEditorLeiste();
  for (const b of Object.keys(karteUhren)) { clearTimeout(karteUhren[b]); delete karteUhren[b]; }
  await Promise.all($$(".editor").map(el => pruefeKarte(el.dataset.bild)));      // gerade Getipptes erst prüfen
  const bereit = $$(".editor").filter(el => !$('[data-k-aktion="speichern"]', el).disabled);
  if (!bereit.length) { S.beschaeftigt = false; zeichneEditorLeiste(); return; }
  let n = 0, letzte = null;
  for (const el of bereit) { try { letzte = await speichereEine(el); n++; } catch (err) { fehlerToast(err); } }
  S.beschaeftigt = false;
  if (letzte) { uebernehmeKarten(letzte.karten); S.v++; }
  toast(t("gespeichert_n", n), S.karten.some(k => k.uebersetzung === "auto") ? { aktion: { label: t("in_tabelle_pruefen"), fn: () => { location.hash = "#tabelle"; } } } : {});
  zeichneEditoren();
});
$("#editoren-uebersetzen").addEventListener("click", async () => {
  const leer = $$(".editor").filter(el => !$('input[data-k="es"]', el).value.trim());
  await alleUebersetzen($("#editoren-uebersetzen"), leer.map(el => ({ de: $('input[data-k="de"]', el).value, fuellen: v => fuelleEditor(el.dataset.bild, v) })));
  zeichneEditorLeiste();
});

/* ===================== Schritt 3: Erzeugen (Einstellungen auch für den Reiter Bildverbesserung) ===================== */
const NUR_ANDERSWO = ["verbessern"];                          // eigene Knöpfe im Reiter „Bildverbesserung“
async function ladeOptionen() { const o = await api("/api/optionen"); S.gruppen = o.gruppen; S.werte = o.werte || {}; }
function feldNach(dest) { for (const g of S.gruppen) for (const f of g.felder) if (f.dest === dest) return f; return null; }
function wert(f) { return f.dest in S.werte ? S.werte[f.dest] : f.default; }
function istGeaendert(f) {
  const v = wert(f);
  if (f.art === "schalter") return !!v !== !!f.default;
  if (f.art === "zahl") return Number(String(v).replace(",", ".")) !== Number(f.default);
  if (f.art === "gansbild") return !!(S.gans && S.gans.quelle !== "gezeichnet");
  return String(v ?? "") !== String(f.default ?? "");
}
function steuerHTML(f) {
  const v = wert(f), id = "o-" + f.dest;
  if (f.art === "gansbild") return gansbildHTML();
  if (f.art === "schalter") return `<label class="schalter"><input type="checkbox" id="${id}" data-dest="${esc(f.dest)}"${v ? " checked" : ""}><span class="spur"></span><span data-anaus>${esc(v ? t("an") : t("aus"))}</span></label>`;
  if (f.art === "auswahl" && f.auswahl.length <= 3) return `<div class="segmente" role="radiogroup" aria-label="${esc(f.label)}">${f.auswahl.map(a =>
    `<label><input type="radio" name="${id}" value="${esc(a.wert)}" data-dest="${esc(f.dest)}"${String(v) === String(a.wert) ? " checked" : ""}><span>${esc(a.label)}</span></label>`).join("")}</div>`;
  if (f.art === "auswahl") return `<select class="eingabe" id="${id}" data-dest="${esc(f.dest)}">${f.auswahl.map(a =>
    `<option value="${esc(a.wert)}"${String(v) === String(a.wert) ? " selected" : ""}>${esc(a.label)}</option>`).join("")}</select>`;
  const typ = f.art === "zahl" ? `type="number" step="${f.schritt || "any"}" inputmode="decimal"` : `type="text"`;
  const eingabe = `<input class="eingabe" id="${id}" ${typ} data-dest="${esc(f.dest)}" value="${esc(v ?? "")}" placeholder="${esc(f.default ?? "")}">`;
  return f.einheit ? `<div class="mit-einheit">${eingabe}<span>${esc(f.einheit)}</span></div>` : eingabe;
}
function satz(x) { x = String(x || "").trim(); if (!x) return ""; x = x[0].toUpperCase() + x.slice(1); return /[.!?]$/.test(x) ? x : x + "."; }
function feldHTML(f) {
  if (f.art === "gansbild") return `<div class="feld breit${istGeaendert(f) ? " geaendert" : ""}" data-feld="${esc(f.dest)}">
    <span class="etikett">${esc(f.label)}</span>${steuerHTML(f)}<div class="hilfe">${esc(t("gans_hilfe"))} <code class="flagge">${esc(f.flag)}</code></div></div>`;
  const breit = (f.art === "text" && !/format/.test(f.dest)) || (f.art === "auswahl" && f.auswahl.length > 3) ? " breit" : "";
  const std = f.art === "schalter" ? (f.default ? t("an") : t("aus")) : (f.default === null || f.default === "" ? t("leer") :
    f.art === "auswahl" ? ((f.auswahl.find(a => String(a.wert) === String(f.default)) || {}).label || f.default) : zahl(f.default));
  return `<div class="feld${breit}${istGeaendert(f) ? " geaendert" : ""}" data-feld="${esc(f.dest)}">
    <label class="etikett" for="o-${esc(f.dest)}">${esc(f.label)}</label>${steuerHTML(f)}
    <div class="hilfe">${esc(satz(f.hilfe))}${f.art !== "schalter" ? ` ${esc(t("standard"))}: ${esc(std)}${f.einheit ? " " + esc(f.einheit) : ""}.` : ""}
    <code class="flagge">${esc(f.flag)}</code></div></div>`;
}
// Erzeugen in drei Schritten: 1 Ziel wählen · 2 Feinschliff (nur die Gruppen, die zum Ziel passen) · 3 Los
const ZIELE = {
  alles: { symbol: "🖨️", felder: ["format", "hochkant", "rs_drehen", "gans_bild", "papier", "ohne_png"] },
  druckerei: { symbol: "🏭", felder: ["format", "hochkant", "rs_drehen", "gans_bild", "ohne_png"] },
  bogen: { symbol: "🏠", felder: ["format", "rs_drehen", "gans_bild", "papier"] },
  pruefbogen: { symbol: "🔍", felder: ["papier", "gans_bild"] },
  digital: { symbol: "📱", felder: ["digital", "gans_bild", "format"] },
  vorlagen: { symbol: "📐", felder: ["format", "papier"] },
};
S.ziel = "alles";
try { const z = localStorage.getItem("mgd-ziel"); if (ZIELE[z]) S.ziel = z; } catch (e) { /* Standard */ }
function gruppePasst(g) {                                       // gehört die Gruppe zum gewählten Ziel?
  const z = ZIELE[S.ziel] || ZIELE.alles;
  return !g.erweitert && g.felder.some(f => z.felder.includes(f.dest));
}
function gruppenHTML(reiter, filter = () => true) {
  const ausgenommen = new Set(["nur", "karten"]);
  return S.gruppen.filter(g => (g.reiter || "erzeugen") === reiter && filter(g)).map(g => {
    const felder = g.felder.filter(f => !ausgenommen.has(f.dest) && !f.intern); if (!felder.length) return "";
    const inhalt = `<div class="feldraster">${felder.map(feldHTML).join("")}</div>`;
    const unter = g.beschreibung ? ` <small>${esc(g.beschreibung)}</small>` : "";
    return g.erweitert
      ? `<details class="flaeche gruppe abstand"><summary>${esc(g.titel)}${unter}</summary>${inhalt}</details>`
      : `<section class="flaeche gruppe abstand"><h2>${esc(g.titel)}${unter}</h2>${inhalt}</section>`;
  }).join("");
}
function zeichneOptionen() {
  const nur = feldNach("nur"), karten = feldNach("karten");
  const ziele = nur ? nur.auswahl.filter(a => !NUR_ANDERSWO.includes(a.wert)) : [];
  if (ziele.length && !ziele.some(a => a.wert === S.ziel)) S.ziel = ziele[0].wert;
  $("#ziel-raster").innerHTML = ziele.map(a => `<label class="ziel-karte" title="${esc(t("ziel_titel_" + a.wert))}">
      <input type="radio" name="ziel" value="${esc(a.wert)}"${a.wert === S.ziel ? " checked" : ""}>
      <span class="ziel-symbol" aria-hidden="true">${(ZIELE[a.wert] || {}).symbol || "✦"}</span>
      <span class="ziel-text"><b>${esc(a.label)}</b><span class="klein">${esc(t("ziel_text_" + a.wert))}</span></span></label>`).join("");
  const gewaehlt = ziele.find(a => a.wert === S.ziel);
  $("#startknoepfe").innerHTML = gewaehlt ? `<button class="knopf haupt gross" data-start="${esc(gewaehlt.wert)}" title="${esc(t("ziel_titel_" + gewaehlt.wert))}">▶ ${esc(t("ez_los", gewaehlt.label))}</button>` : "";
  $("#auswahlzeile").innerHTML = (karten ? `<label class="f"><span>${esc(karten.label)}</span>
    <input id="kartenauswahl" value="${esc(S.auswahl)}" placeholder="${esc(t("auswahl_ph"))}" title="${esc(t("auswahl_tipp"))}"></label>` : "")
    + druckSpracheHTML() + (karten ? `<p class="klein" style="margin:0 0 10px">${esc(satz(karten.hilfe))}</p>` : "");
  zeigeKiHinweis();
  $("#gruppen").innerHTML = gruppenHTML("erzeugen", gruppePasst) || `<p class="klein">${esc(t("ez_nichts_einstellen"))}</p>`;
  $("#gruppen-weitere").innerHTML = gruppenHTML("erzeugen", g => !gruppePasst(g));
  $("#weitere-box").hidden = !$("#gruppen-weitere").innerHTML.trim();
  $("#gruppen-verbesserung").innerHTML = gruppenHTML("bildverbesserung");
  zeichneLauf();
}
$("#ziel-raster").addEventListener("change", e => {
  if (e.target.name !== "ziel") return;
  S.ziel = e.target.value; try { localStorage.setItem("mgd-ziel", S.ziel); } catch (err) { /* egal */ }
  zeichneOptionen(); zeigeBefehl();
});
function zeigeKiHinweis() {
  const m = S.status.ki_methode || "";
  const da = S.karten.filter(k => k.existiert), fertig = da.filter(k => k.verbessert).length;
  $("#ki-hinweis").innerHTML = esc(m.startsWith("realesrgan") ? t("ki_hinweis_esrgan", S.status.ki_name) : m === "fsrcnn" ? t("ki_hinweis_fsrcnn") : t("ki_hinweis_aus"))
    + (da.length ? ` <a href="#verbesserung">${esc(t("ki_hinweis_reiter", fertig, da.length))}</a>` : "");
}
const speichereOptionen = entprellt(async () => {
  try {
    const r = await api("/api/einstellungen", { methode: "POST", daten: { werte: S.werte } }); S.v++; zeigeBefehl(r.fehler);
    await ladeStatus(); await ladeKarten(); zeigeKiHinweis();
    if (ansicht() === "verbesserung") ladeVerbesserung();
  } catch (e) { fehlerToast(e); zeigeBefehl(e.message); }
}, 400);
async function zeigeBefehl(fehlerVorab) {
  try {
    const r = await api(url("/api/befehl", { nur: S.ziel || "alles", karten: S.auswahl, sprache: zsMehrere() && S.druckSprache !== "alle" ? S.druckSprache : "" }));
    $("#befehl").textContent = r.befehl;
    const fehler = fehlerVorab || r.fehler;
    $("#befehl-fehler").hidden = !fehler; $("#befehl-fehler").textContent = fehler ? t("bitte_pruefen") + fehler : "";
    $$("[data-start]").forEach(b => b.disabled = !!fehler);
  } catch (e) { /* Verbindungshinweis erscheint */ }
}
function optionGeaendert(e) {
  const dest = e.target.dataset.dest; if (!dest) return;
  const f = feldNach(dest);
  S.werte[dest] = e.target.type === "checkbox" ? e.target.checked : e.target.value;
  if (e.target.type === "checkbox") $("[data-anaus]", e.target.closest(".schalter")).textContent = e.target.checked ? t("an") : t("aus");
  e.target.closest(".feld").classList.toggle("geaendert", istGeaendert(f));
  speichereOptionen();
}
$("#gruppen").addEventListener("input", optionGeaendert);
$("#gruppen-weitere").addEventListener("input", optionGeaendert);
$("#gruppen-verbesserung").addEventListener("input", optionGeaendert);
$("#auswahlzeile").addEventListener("input", entprellt(e => { if (e.target.id === "kartenauswahl") { S.auswahl = e.target.value.trim(); zeigeBefehl(); } }, 300));
$("#auswahlzeile").addEventListener("change", e => { if (e.target.id === "druck-sprache") { S.druckSprache = e.target.value; zeigeBefehl(); } });
/* Sprache der Rückseite beim Erzeugen (Tool „Sprachen“): Standard = Zielsprache, „alle“ = ein Auftrag je Sprache */
S.druckSprache = "";
function druckSpracheHTML() {
  const inst = ZS.installiert || ["es"];
  if (!zsMehrere() || S.ziel === "vorlagen") return "";
  if (S.druckSprache && S.druckSprache !== "alle" && !inst.includes(S.druckSprache)) S.druckSprache = "";
  const opt = (w, l) => `<option value="${esc(w)}"${w === S.druckSprache ? " selected" : ""}>${esc(l)}</option>`;
  return `<label class="f"><span>${esc(t("ez_druck_sprache"))}</span>
    <select id="druck-sprache" title="${esc(t("h_druck_sprache"))}">${opt("", t("ez_druck_ziel", zsName()))}
    ${inst.filter(c => c !== ZS.code).map(c => opt(c, zsName(c))).join("")}${opt("alle", t("ez_druck_alle", inst.length))}</select></label>`;
}
$("#standard").addEventListener("click", async () => {
  S.werte = {}; zeichneOptionen();
  try { const r = await api("/api/einstellungen", { methode: "POST", daten: { werte: {} } }); S.v++; zeigeBefehl(r.fehler); await ladeStatus(); await ladeKarten(); zeigeKiHinweis(); toast(t("standard_ok")); }
  catch (e) { fehlerToast(e); }
});
async function kopiere(text) {          // Handy-Zugang (HTTP): keine Zwischenablage-API → alter Weg über ein Textfeld
  try { await navigator.clipboard.writeText(text); return true; } catch (e) { /* Ersatzweg */ }
  const f = document.createElement("textarea"); f.value = text; f.setAttribute("readonly", "");
  f.style.cssText = "position:fixed;top:0;left:0;opacity:0"; document.body.append(f); f.select(); f.setSelectionRange(0, text.length);
  let ok = false; try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
  f.remove(); return ok;
}
$("#befehl-kopieren").addEventListener("click", async () => {
  if (await kopiere($("#befehl").textContent)) toast(t("kopiert")); else toast(t("kopieren_fehler"), { fehler: true });
});
$("#startknoepfe").addEventListener("click", async e => {
  const b = e.target.closest("[data-start]"); if (!b) return;
  const nur = b.dataset.start, karten = S.auswahl;
  const los = async (ohne_tool = false) => {
    const sprache = nur !== "vorlagen" && zsMehrere() ? S.druckSprache || undefined : undefined;
    try {
      const st = await api("/api/lauf", { methode: "POST", daten: { art: "generator", nur, karten, ohne_tool, sprache } });
      if (st.auftraege > 1) toast(t("ez_druck_eingereiht", st.auftraege));
      starteBeobachtung(st);
    }
    catch (err) {
      if (!ohne_tool && toolFehlt(err) && err.daten.tool === "sprachen") return toolInstallieren("sprachen", { teil: err.daten.teil, weiter: () => los() });
      if (!ohne_tool && toolFehlt(err)) return brauchtTool(err.daten.tool, () => los(), { alternativ: () => los(true), alternativText: t("verb_ohne_tool") });
      fehlerToast(err);
    }
  };
  los();
});

/* ===================== Gänse-Bild der Rückseite: per Knopf laden ===================== */
async function ladeGans() { try { S.gans = await api("/api/gans-bild"); } catch (e) { /* Verbindungshinweis erscheint */ } }
function gansbildHTML() {
  const g = S.gans || { quelle: "gezeichnet", hinweise: [] };
  const titel = g.quelle === "gezeichnet" ? t("gans_gezeichnet") : g.quelle === "pfad" ? t("gans_pfad", g.pfad || g.name || "")
    : t("gans_geladen", g.groesse ? `${g.groesse[0]} × ${g.groesse[1]} px` : g.name || "");
  const beispiel = (S.karten.find(k => k.aktiv && String(k.es).trim()) || {}).es || "";
  return `<div class="gansbild" data-gansbild>
    <div class="vorschau-karte"><img alt="${esc(t("rueckseite"))}" src="${url("/api/rueckseite", { es: beispiel, v: S.v })}"></div>
    <div class="text"><b>${esc(titel)}</b>
      <span class="klein">${esc(t("gans_tipp"))}</span>
      ${g.hinweise && g.hinweise.length ? pruefliste(g.hinweise) : ""}
      <div class="knopfzeile">
        <button type="button" class="knopf dunkel" data-g-aktion="laden" title="${esc(t("h_gans_laden"))}">${esc(g.quelle === "gezeichnet" ? t("gans_laden") : t("gans_anderes"))}</button>
        ${g.quelle !== "gezeichnet" ? `<button type="button" class="knopf leise" data-g-aktion="weg" title="${esc(t("h_gans_weg"))}">${esc(t("gans_weg"))}</button>` : ""}
        ${g.wiederherstellbar ? `<button type="button" class="knopf leise" data-g-aktion="zurueck" title="${esc(t("h_gans_zurueck"))}">${esc(t("gans_zurueck"))}</button>` : ""}
      </div>
      <span class="klein">${esc(t("gans_ziehen"))}</span>
      <input type="file" accept="${BILD_ACCEPT}" hidden data-g-datei>
    </div></div>`;
}
function zeichneGansbild() {
  $$("[data-gansbild]").forEach(el => {
    el.outerHTML = gansbildHTML();
  });
  $$('[data-feld="gans_bild"]').forEach(el => el.classList.toggle("geaendert", !!(S.gans && S.gans.quelle !== "gezeichnet")));
}
async function gansAktion(pfad, meldung) {
  try { S.gans = await api(pfad, { methode: "POST", daten: {} }); delete S.werte.gans_bild; S.v++; zeichneGansbild(); if (meldung) toast(meldung); }
  catch (e) { fehlerToast(e); }
}
async function ladeGansbild(f) {
  if (f.size > MAX_MB * 1024 * 1024) { toast(t("zu_gross", f.name, MAX_MB), { fehler: true }); return; }
  const vorher = S.gans ? S.gans.quelle : "gezeichnet";
  try {
    S.gans = await api("/api/gans-bild", { methode: "POST", roh: f });
    delete S.werte.gans_bild; S.v++; zeichneGansbild();
    toast(t("gans_ok"), { aktion: { label: t("rueckgaengig"), fn: () => gansAktion(vorher === "gezeichnet" ? "/api/gans-bild-weg" : "/api/gans-bild-zurueck") } });
  } catch (e) { fehlerToast(e); }
}
document.addEventListener("click", e => {
  const g = e.target.closest("[data-g-aktion]"); if (!g) return;
  const a = g.dataset.gAktion;
  if (a === "laden") { $("[data-g-datei]", g.closest("[data-gansbild]")).click(); return; }
  if (a === "weg") gansAktion("/api/gans-bild-weg", t("gans_weg_ok"));
  if (a === "zurueck") gansAktion("/api/gans-bild-zurueck", t("gans_zurueck_ok"));
});
document.addEventListener("change", e => {
  if (!e.target.matches || !e.target.matches("[data-g-datei]")) return;
  const f = e.target.files[0]; e.target.value = ""; if (f) ladeGansbild(f);
});

/* ===================== Läufe: Live-Protokoll ===================== */
function zeilenHTML(zeilen) {
  return zeilen.map(z => {
    const kl = /FEHLER|ERROR|Achtung:|Heads-up:|Atención:|Traceback|Error/.test(z) ? "err" : /^\s*!/.test(z) ? "warn" : /BESTANDEN|PASSED|SUPERADA|^Fertig|^Done|^Listo/.test(z) ? "gut" : "";
    return kl ? `<span class="${kl}">${esc(z)}</span>` : esc(z);
  }).join("\n");
}
function laufFortschritt(L) {
  // Zeilen wie „[2/5] gans-alt.jpg: KI-Vergrößerung 50 %“ (läuft) bzw. „[2/5] gans-alt.jpg: fertig“ (Bild fertig)
  let i = 0, n = 0, p = 0;
  for (const z of L.zeilen || []) {
    const m = z.match(/\[(\d+)\/(\d+)\]/); if (!m) continue;
    i = +m[1]; n = +m[2]; const pm = z.match(/(\d+)\s*%\s*$/); p = pm ? +pm[1] : 100;
  }
  return n ? Math.min(100, Math.round(((i - 1) + p / 100) / n * 100)) : null;
}
function zeichneLauf() {
  const L = S.lauf;
  $$("[data-lauf]").forEach(el => {
    if (el.closest(".ansicht").hidden) return;
    if (!L) { el.innerHTML = `<div class="kopfzeile"><h2 style="margin:0">${esc(t("protokoll"))}</h2><span class="pille">${esc(t("bereit"))}</span></div>
      <p class="unter klein">${esc(t("protokoll_leer"))}</p>`; return; }
    const pille = L.laeuft ? `${enteHTML(t("laeuft"), true)}` : L.code === 0
      ? `<span class="pille ok">${esc(t("fertig_in", zahl(L.dauer)))}</span>` : `<span class="pille fehler">${esc(L.code < 0 || L.abgebrochen ? t("abgebrochen") : t("fehler_code", L.code))}</span>`;
    let nachher = "";
    if (L.laeuft) nachher = `<button class="knopf klein" data-lauf-stopp title="${esc(t("h_lauf_stopp"))}">${esc(t("abbrechen"))}</button>`
      + (S.wsZahl ? ` <button type="button" class="knopf klein leise" data-ws-oeffnen title="${esc(t("h_ws_knopf"))}">⏳ ${esc(t("ws_danach", S.wsZahl))}</button>` : "");
    else if (L.art === "generator" && L.code === 0) nachher = (["alles", "pruefbogen"].includes(L.nur) && S.namen
      ? `<button class="knopf klein haupt" data-oeffnen="ausgabe/${esc(S.namen.pruefbogen)}" title="${esc(t("h_pruefbogen_oeffnen"))}">${esc(t("pruefbogen_oeffnen"))}</button>` : "")
      + `<a class="knopf klein" href="#pruefen" title="${esc(t("h_zu_schritt4"))}">${esc(t("zu_schritt4"))}</a>`;
    else if (L.art === "ki-bild" && L.code === 0 && L.ki && L.ki.fertig) nachher = `<button class="knopf klein haupt" data-ki-ansehen>${esc(t("ki_ansehen"))}</button>`;
    else if (L.art === "verbessern" && L.code === 0 && ansicht() !== "verbesserung") nachher = `<a class="knopf klein" href="#verbesserung" title="${esc(t("h_zur_verbesserung"))}">${esc(t("zur_verbesserung"))}</a>`;
    const p = L.art === "verbessern" && L.laeuft ? laufFortschritt(L) : L.art === "ki-bild" && L.laeuft && L.ki ? L.ki.prozent : null;
    const balken = p == null ? "" : `<div class="fortschritt" aria-hidden="true"><span style="width:${p}%"></span></div><p class="klein" style="margin:0 0 8px">${esc(t("verb_fortschritt", p))}</p>`;
    const alt = $(".protokoll", el); const unten = !alt || alt.scrollTop + alt.clientHeight >= alt.scrollHeight - 20;
    el.innerHTML = `<div class="kopfzeile"><h2 style="margin:0">${esc(L.titel)}</h2>${pille}</div>
      <p class="befehlszeile">${esc(L.befehl)}</p>${balken}<pre class="protokoll" tabindex="0">${zeilenHTML(L.zeilen)}</pre>
      <div class="nachher">${nachher}</div>`;
    const pre = $(".protokoll", el); if (unten) pre.scrollTop = pre.scrollHeight;
  });
  $$("[data-start]").forEach(b => b.disabled = !$("#befehl-fehler").hidden);
  zeichneVerbAuswahl();
  kiFortschritt();
}
let laufBeobachtet = false;                               // nur eine Abfrage-Schleife zur Zeit (auch für die Warteschlange)
function laufUebernehmen(n) { S.lauf = { ...n, zeilen: n.zeilen || [] }; S.laufAb = n.anzahl ?? S.lauf.zeilen.length; S.laufBekannt.add(n.id); }
function wsVermerken(st) {                                 // Auftrag wartet: sofort in die Liste + Toast mit „Ansehen“
  S.laufBekannt.add(st.id);
  if (!S.ws.wartend.some(x => x.id === st.id)) S.ws.wartend.push({ id: st.id, art: st.art, titel: st.titel, nur: st.nur, position: st.position });
  S.wsZahl = Math.max(S.wsZahl, S.ws.wartend.length);
  toast(t("ws_eingereiht", st.position), { aktion: { label: t("ws_ansehen_kurz"), fn: () => oeffneWs() } });
}
async function starteBeobachtung(st) {
  if (st && st.wartet) wsVermerken(st);
  else if (st && st.id && st.laeuft) laufUebernehmen(st);
  if (st && typeof st.warteschlange === "number") S.wsZahl = st.warteschlange;
  zeichneLauf(); zeichneWs();
  if (laufBeobachtet) return;                              // die laufende Schleife fragt mit dem neuen Stand weiter
  laufBeobachtet = true;
  let fehler = 0;
  try {
    while ((S.lauf && S.lauf.laeuft) || S.wsZahl > 0) {
      await warte(fehler ? 2000 : 500);
      try {
        const verfolgt = S.lauf && S.lauf.laeuft ? S.lauf.id : "";
        const n = await api(url("/api/lauf", verfolgt ? { ab: S.laufAb, id: verfolgt } : { ab: 0 })); fehler = 0;
        S.wsZahl = n.warteschlange || 0;
        if (verfolgt && n.id === verfolgt) {
          S.lauf = { ...n, zeilen: [...S.lauf.zeilen, ...(n.zeilen || [])] }; S.laufAb = n.anzahl;
          if (!S.lauf.laeuft) laufAbgeschlossen(S.lauf);
        } else if (verfolgt) { S.lauf.laeuft = false; break; }       // Auftrag unbekannt (Programm neu gestartet)
        else if (n.id && n.id !== (S.lauf && S.lauf.id)) {          // der nächste aus der Schlange ist dran
          laufUebernehmen(n); if (!n.laeuft) laufAbgeschlossen(S.lauf);
        }
        if (S.wsZahl || S.ws.wartend.length || wsOffen()) await ladeWs();
        zeichneLauf(); zeichneWs(); toolsNebenbei();
      } catch (e) { if (++fehler > 15) break; }          // Handy: Display aus / WLAN kurz weg – erst nach ~30 s aufgeben
    }
  } finally { laufBeobachtet = false; }
  if (S.ws.wartend.length || wsOffen()) await ladeWs();
  zeichneLauf(); zeichneWs();
}
async function laufAbgeschlossen(L) {                     // einmal je Auftrag: Toast + betroffene Ansichten auffrischen
  if (!L || !L.id || S.laufGemeldet.has(L.id)) return;
  S.laufGemeldet.add(L.id);
  if (L.art === "generator" || L.art === "verbessern") {
    L.code === 0 ? toast(t("lauf_fertig", L.titel, zahl(L.dauer))) : toast(t("lauf_fehler", L.titel), { fehler: true });
    S.v++; ladeKarten().then(() => { if (ansicht() === "karten") zeichneKarten(); zeigeKiHinweis(); }).catch(() => {});
    if (ansicht() === "pruefen") ladeErgebnisse();
    if (ansicht() === "verbesserung") ladeVerbesserung();
  } else if (L.art === "ki-bild") {
    kiLaufFertig(L);
  } else if (L.art === "test") {
    L.code === 0 ? toast(t("test_ok")) : toast(t("test_fehler"), { fehler: true });
  } else if (L.tool) {
    await toolFertig(L);
  } else {
    L.code === 0 ? toast(t("lauf_fertig", L.titel, zahl(L.dauer))) : toast(t("lauf_fehler", L.titel), { fehler: true });
    try { await ladeStatus(); await ladeWerkzeuge(); } catch (e) { /* nächste Runde */ }
    if (ansicht() === "werkzeuge") zeichneWerkzeuge();
    if (ansicht() === "verbesserung") ladeVerbesserung();
  }
}
function laufWiederaufnehmen() {
  if (!S.wsZahl && S.status && S.status.warteschlange && !(S.lauf && S.lauf.laeuft)) S.wsZahl = S.status.warteschlange;  // z. B. vom Handy gestartet
  if (!laufBeobachtet && ((S.lauf && S.lauf.laeuft) || S.wsZahl)) starteBeobachtung(null);
}

/* ===================== Warteschlange: Kopfzeile „⏳ n“ + Fenster ===================== */
function wsOffen() { return !$("#ws-fenster").hidden; }
function wsAnzahl() { return S.wsZahl + (S.lauf && S.lauf.laeuft ? 1 : 0); }
async function ladeWs() {
  try {
    S.ws = await api("/api/warteschlange"); S.wsZahl = S.ws.wartend.length;
    for (const f of S.ws.fertig) {                          // nie beobachtet (z. B. Start gescheitert): trotzdem melden
      if (S.laufBekannt.has(f.id) && !S.laufGemeldet.has(f.id) && !(S.lauf && S.lauf.id === f.id && S.lauf.laeuft))
        laufAbgeschlossen({ ...f, zeilen: [], ki: f.ki });
    }
  } catch (e) { /* nächste Runde */ }
}
function wsDauer(s) { s = Math.max(0, Math.round(s || 0)); return s < 60 ? `${s} s` : `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")} min`; }
function wsErgebnisKnopf(x) {
  if (x.code === 0 && x.art === "generator") return `<a class="knopf klein" href="#pruefen" data-zu>${esc(t("ws_ansehen"))}</a>`;
  if (x.code === 0 && x.art === "verbessern") return `<a class="knopf klein" href="#verbesserung" data-zu>${esc(t("ws_ansehen"))}</a>`;
  if (x.art === "ki-bild" && x.ki && x.ki.fertig) return `<button type="button" class="knopf klein" data-ws-ki="${esc(x.id)}">${esc(t("ws_ansehen"))}</button>`;
  return `<button type="button" class="knopf klein leise" data-ws-protokoll="${esc(x.id)}" aria-expanded="${S.wsProtokoll && S.wsProtokoll.id === x.id}">${esc(t("ws_protokoll"))}</button>`;
}
function zeichneWsKnopf() {
  const n = wsAnzahl(), k = $("#ws-knopf"); if (!k) return;
  k.hidden = !n; $("#ws-zahl").textContent = n; k.setAttribute("aria-label", t("ws_knopf_label", n));
}
function zeichneWs() {
  zeichneWsKnopf(); if (KI) kiFortschritt();
  if (!wsOffen()) return;
  const w = S.ws, a = S.lauf && S.lauf.laeuft ? S.lauf : w.aktiv;
  let h = "";
  if (S.wsBeenden) h += `<div class="ws-beenden"><span>${esc(t("ws_beenden_frage"))}</span>
    <button type="button" class="knopf klein haupt" data-ws="beenden">${esc(t("ws_beenden_ja"))}</button>
    <button type="button" class="knopf klein leise" data-ws="weiter">${esc(t("ws_beenden_nein"))}</button></div>`;
  h += `<h3>${esc(t("ws_jetzt"))}</h3>`;
  if (a) {
    const p = a.art === "verbessern" ? laufFortschritt(a) : a.art === "ki-bild" && a.ki ? a.ki.prozent || 0 : null;
    h += `<div class="ws-aktiv"><div class="ws-zeile"><span class="ws-titel"><b>${esc(a.titel)}</b> <span class="klein">· ${esc(t("ws_seit", wsDauer(a.dauer)))}</span></span>
      <button type="button" class="knopf klein" data-lauf-stopp title="${esc(t("h_lauf_stopp"))}">${esc(t("abbrechen"))}</button></div>
      ${p == null ? `<p class="klein" style="margin:6px 0 0">${esc(t("laeuft"))}</p>` : `<div class="fortschritt" aria-hidden="true"><span style="width:${p}%"></span></div><p class="klein" style="margin:0">${esc(t("verb_fortschritt", p))}</p>`}</div>`;
  } else h += `<p class="klein" style="margin:0">${esc(t("ws_nichts"))}</p>`;
  h += `<h3>${esc(t("ws_wartend"))} <span class="pille">${w.wartend.length}</span></h3>`;
  if (!w.wartend.length) h += `<p class="klein" style="margin:0">${esc(t("ws_keine_wartend"))}</p>`;
  else {
    const letzt = w.wartend.length - 1;
    h += `<ol class="ws-liste">${w.wartend.map((x, i) => `<li><span class="ws-platz">${esc(t("ws_platz", x.position))}</span><span class="ws-titel">${esc(x.titel)}</span>
      <span class="ws-knoepfe"><button type="button" class="knopf klein leise" data-ws="hoch" data-id="${esc(x.id)}" title="${esc(t("h_ws_hoch"))}" aria-label="${esc(t("h_ws_hoch"))}"${i ? "" : " disabled"}>▲</button>
        <button type="button" class="knopf klein leise" data-ws="runter" data-id="${esc(x.id)}" title="${esc(t("h_ws_runter"))}" aria-label="${esc(t("h_ws_runter"))}"${i < letzt ? "" : " disabled"}>▼</button>
        <button type="button" class="knopf klein leise" data-ws="als-naechstes" data-id="${esc(x.id)}" title="${esc(t("h_ws_naechstes"))}"${i ? "" : " disabled"}>${esc(t("ws_als_naechstes"))}</button>
        <button type="button" class="knopf klein leise" data-ws="entfernen" data-id="${esc(x.id)}" title="${esc(t("h_ws_entfernen"))}" aria-label="${esc(t("h_ws_entfernen"))}">✕</button></span></li>`).join("")}</ol>`;
    h += S.wsLeeren ? `<div class="ws-frage"><span>${esc(t("ws_leeren_frage", w.wartend.length))}</span>
        <button type="button" class="knopf klein haupt" data-ws="leeren">${esc(t("ws_leeren_ja"))}</button>
        <button type="button" class="knopf klein leise" data-ws="leeren-nein">${esc(t("ws_leeren_nein"))}</button></div>`
      : `<div class="knopfzeile" style="margin-top:10px"><button type="button" class="knopf klein leise" data-ws="leeren-frage" title="${esc(t("h_ws_leeren"))}">${esc(t("ws_leeren"))}</button></div>`;
  }
  if (w.fertig.length) h += `<h3>${esc(t("ws_zuletzt"))}</h3><ul class="ws-liste">${w.fertig.map(x => `<li><span class="ws-platz ${x.code === 0 ? "ok" : "nein"}" aria-hidden="true">${x.code === 0 ? "✓" : "✕"}</span>
      <span class="ws-titel">${esc(x.titel)} <span class="klein">· ${esc(x.code === 0 ? wsDauer(x.dauer) : x.abgebrochen || x.code < 0 ? t("abgebrochen") : t("fehler_code", x.code))}</span></span>${wsErgebnisKnopf(x)}
      ${S.wsProtokoll && S.wsProtokoll.id === x.id ? `<pre class="protokoll" tabindex="0">${zeilenHTML(S.wsProtokoll.zeilen)}</pre>` : ""}</li>`).join("")}</ul>`;
  const box = $("#ws-inhalt"), pre = $(".protokoll", box), oben = pre ? pre.scrollTop : 0;
  box.innerHTML = h;
  const neu = $(".protokoll", box); if (neu) neu.scrollTop = pre ? oben : neu.scrollHeight;
}
async function oeffneWs(beenden = false) {
  S.wsBeenden = beenden; S.wsLeeren = false; S.wsProtokoll = null;
  $("#ws-fenster").hidden = false; zeichneWs();
  await ladeWs(); zeichneWs(); laufWiederaufnehmen();
}
async function beendenJetzt() {
  try { await api("/api/beenden", { methode: "POST", daten: {} }); } catch (e) { /* Server ist schon weg */ }
  S.wsZahl = 0; S.ws.wartend = []; if (S.lauf) S.lauf.laeuft = false;      // Abfrage-Schleife endet sofort
  $("#ws-fenster").hidden = true; $("#ende-text").textContent = t("beendet"); $("#ende").hidden = false;
}
$("#ws-knopf").addEventListener("click", () => oeffneWs());
document.addEventListener("click", async e => {
  if (e.target.closest("[data-ws-oeffnen]")) { oeffneWs(); return; }
  const ki = e.target.closest("[data-ws-ki]");
  if (ki) {
    const x = S.ws.fertig.find(f => f.id === ki.dataset.wsKi); if (!x || !x.ki) return;
    const k = x.ki; KI_MERK.letzt = { id: k.id, startwert: k.startwert, karte: k.karte || "", wort: k.wort || "", beschreibung: k.beschreibung || "" };
    schliesseDialog($("#ws-fenster")); oeffneKiBild({ karte: KI_MERK.letzt.karte, ergebnis: KI_MERK.letzt }); return;
  }
  const pr = e.target.closest("[data-ws-protokoll]");
  if (pr) {
    const id = pr.dataset.wsProtokoll;
    if (S.wsProtokoll && S.wsProtokoll.id === id) { S.wsProtokoll = null; zeichneWs(); return; }
    try { const n = await api(url("/api/lauf", { id, ab: 0 })); S.wsProtokoll = { id, zeilen: n.zeilen || [] }; zeichneWs(); } catch (err) { fehlerToast(err); }
    return;
  }
  const b = e.target.closest("[data-ws]"); if (!b) return;
  const aktion = b.dataset.ws;
  if (aktion === "leeren-frage" || aktion === "leeren-nein") { S.wsLeeren = aktion === "leeren-frage"; zeichneWs(); return; }
  if (aktion === "weiter") { S.wsBeenden = false; zeichneWs(); return; }
  if (aktion === "beenden") { beendenJetzt(); return; }
  b.disabled = true;
  try {
    S.ws = await api("/api/warteschlange", { methode: "POST", daten: { aktion, id: b.dataset.id || "" } });
    S.wsZahl = S.ws.wartend.length; S.wsLeeren = false;
    if (aktion === "entfernen") toast(t("ws_entfernt")); else if (aktion === "leeren") toast(t("ws_geleert"));
  } catch (err) { fehlerToast(err); await ladeWs(); }
  zeichneLauf(); zeichneWs();
});
document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") laufWiederaufnehmen(); });
document.addEventListener("click", async e => {
  const stopp = e.target.closest("[data-lauf-stopp]");
  if (stopp) { try { await api("/api/lauf-stopp", { methode: "POST", daten: {} }); } catch (err) { fehlerToast(err); } }
  const oe = e.target.closest("[data-oeffnen]");
  if (oe) { try { await api("/api/oeffnen", { methode: "POST", daten: { ziel: oe.dataset.oeffnen } }); toast(t("wird_geoeffnet")); } catch (err) { fehlerToast(err); } }
});

/* ===================== Schritt 4: Prüfen & drucken ===================== */
const groesse = b => b > 1048576 ? zahl((b / 1048576).toFixed(1)) + " MB" : Math.max(1, Math.round(b / 1024)) + " KB";
function datum(s) { try { return new Date(s.replace(" ", "T")).toLocaleString(t("datum"), { dateStyle: "medium", timeStyle: "short" }); } catch (e) { return s; } }
async function ladeErgebnisse() {
  if (!$("#ergebnis-inhalt").children.length) $("#ergebnis-inhalt").innerHTML = enteHTML();
  let d; try { d = await api("/api/ergebnisse"); } catch (e) { fehlerToast(e); if ($("#ergebnis-inhalt .ente-laedt")) $("#ergebnis-inhalt").textContent = e.message; return; }
  S.namen = d.namen;
  const b = d.bericht || {}, alle = d.dateien;
  const haupt = alle.filter(x => x.gruppe === "ausgabe"), vorl = alle.filter(x => x.gruppe === "vorlagen"), digital = alle.filter(x => x.gruppe === "digital");
  if (!haupt.length && !digital.length && !d.einzelbilder) {
    $("#ergebnis-inhalt").innerHTML = `<div class="flaeche leer"><img src="/symbol.svg" alt=""><h2>${esc(t("nichts_erzeugt"))}</h2>
      <p>${esc(t("nichts_erzeugt_text"))}</p><div class="knopfzeile"><a class="knopf haupt gross" href="#erzeugen">${esc(t("zu_schritt3"))}</a></div>${appTipp()}</div>`; return;
  }
  const zeile = x => `<div class="ergebnis"><div><h3 style="margin:0">${esc(x.titel)}</h3>
      <div class="name">${esc(x.name)} – ${groesse(x.groesse)}, ${esc(datum(x.zeit))}</div>${x.beschreibung ? `<div class="klein">${esc(x.beschreibung)}</div>` : ""}</div>
      <div class="knoepfe"><button class="knopf klein dunkel" data-oeffnen="${esc(x.gruppe + "/" + x.name)}" title="${esc(t("oeffnen_titel"))}">${esc(t("oeffnen"))}</button>
      ${x.gruppe === "digital" && !/\.pdf$/i.test(x.name) ? `<a class="knopf klein" href="${esc(x.url)}" download title="${esc(t("speichern_titel"))}">${esc(t("speichern_unter"))}</a>`
        : `<a class="knopf klein" href="${esc(x.url)}" target="_blank" rel="noopener" title="${esc(t("im_browser_titel"))}">${esc(t("im_browser"))}</a>`}</div></div>`;
  const finde = muster => haupt.filter(x => muster.test(x.name));
  const pruefbogen = finde(/_Pruefbogen\.pdf$/), heim = finde(/_Heimdruck_/), druckerei = finde(/_Druckerei_/), sonst = haupt.filter(x => ![...pruefbogen, ...heim, ...druckerei].includes(x));
  // Checkliste aus dem, was das Programm schon weiß
  const auto = S.karten.filter(k => k.aktiv && k.uebersetzung === "auto").length;
  const ungeprueft = S.karten.filter(k => k.aktiv && String(k.es || "").trim() && k.uebersetzung !== "geprueft").length;
  const schwach = Object.values(b.karten || {}).filter(k => (k.ppi || 999) < 120).length;
  const punkt = (ok, text, link) => `<li class="${ok ? "ok" : "offen"}"><span aria-hidden="true">${ok ? "✓" : "○"}</span> ${esc(text)}${link || ""}</li>`;
  const meld = b.meldungen || [], anzahl = b.karten ? Object.keys(b.karten).length : 0;
  const lauf = b.zeit ? `<details class="lauf-details"><summary title="${esc(t("h_lauf_details"))}">${esc(t("letzter_lauf"))}: ${esc(datum(b.zeit))} · ${b.auswahl ? esc(b.auswahl.join(", ")) : anzahl} ${esc(b.auswahl ? t("ausgewaehlte") : t("karten"))}</summary>
      <div class="bericht-kopf"><div><b>${esc(b.format || "")} mm</b>${esc(t("format"))}</div>
      <div><b>${esc({ "realesrgan-x4plus": "Real-ESRGAN", "realesrgan-x2plus": "Real-ESRGAN ×2", fsrcnn: "FSRCNN", lanczos: "Lanczos" }[b.ki_methode] || b.qualitaet || "")}</b>${esc(t("bildverbesserung"))}</div></div>
      ${meld.length ? `<ul class="meldungen">${meld.map(m => `<li class="${/^(FEHLER|ERROR|Achtung|Heads-up|Atención)/.test(m) ? "fehler" : ""}">${esc(m)}</li>`).join("")}</ul>` : `<p class="klein" style="margin:8px 0 0">${esc(t("keine_hinweise"))}</p>`}</details>` : "";
  const liste = schluessel => `<ul class="tipp-liste">${t(schluessel).map(x => `<li>${esc(x)}</li>`).join("")}</ul>`;
  $("#ergebnis-inhalt").innerHTML = `
    <section class="flaeche"><h2 class="schritt-kopf"><span class="schritt-nr">1</span>${esc(t("pr_s1"))}</h2>
      <p class="klein">${esc(t("pr_s1_text"))}</p>
      ${pruefbogen.map(zeile).join("") || `<p class="klein">${esc(t("pr_kein_pruefbogen"))}</p>`}
      <ul class="check-liste">
        ${punkt(!auto && !ungeprueft, auto || ungeprueft ? t("pr_check_ueb", ungeprueft) : t("pr_check_ueb_ok"), auto || ungeprueft ? ` <a href="#tabelle" title="${esc(t("h_zur_tabelle"))}">${esc(t("pr_zur_tabelle"))}</a>` : "")}
        ${punkt(!schwach, schwach ? t("pr_check_ppi", schwach) : t("pr_check_ppi_ok"), schwach ? ` <a href="#verbesserung" title="${esc(t("h_zur_verbesserung"))}">${esc(t("zur_verbesserung"))}</a>` : "")}
        ${punkt(false, t("pr_check_probe"))}
      </ul>${lauf}</section>
    <section class="flaeche abstand"><h2 class="schritt-kopf"><span class="schritt-nr">2</span>${esc(t("pr_s2"))}</h2>
      <div class="druck-wege">
        <div class="druck-weg"><h3>🏠 ${esc(t("pr_zuhause"))}</h3>${heim.map(zeile).join("") || `<p class="klein">${esc(t("pr_noch_nicht"))}</p>`}
          ${liste("pr_tipps_zuhause")}</div>
        <div class="druck-weg"><h3>🏭 ${esc(t("pr_druckerei"))}</h3>${druckerei.map(zeile).join("") || `<p class="klein">${esc(t("pr_noch_nicht"))}</p>`}
          ${d.einzelbilder ? `<div class="ergebnis"><div><h3 style="margin:0">${esc(t("einzelbilder"))}</h3><div class="klein">${esc(t("einzelbilder_text", d.einzelbilder))}</div></div>
            <div class="knoepfe"><button class="knopf klein" data-oeffnen="einzelbilder" title="${esc(t("h_einzelbilder"))}">${esc(t("ordner_oeffnen"))}</button></div></div>` : ""}
          <details class="tipp-box"><summary title="${esc(t("h_pr_finden"))}">${esc(t("pr_finden_titel"))}</summary><p class="klein">${esc(t("pr_finden_text"))}</p>
            <p class="klein"><b>${esc(t("pr_suchbegriffe"))}</b> ${esc(t("pr_suchbegriffe_liste"))}</p>
            <p class="klein"><b>${esc(t("pr_achten"))}</b></p>${liste("pr_achten_liste")}</details></div>
      </div>${sonst.length ? `<div class="liste-zeilen abstand">${sonst.map(zeile).join("")}</div>` : ""}</section>
    <section class="flaeche abstand"><h2 class="schritt-kopf"><span class="schritt-nr">3</span>${esc(t("pr_s3"))}</h2>
      ${digital.length ? `<div class="liste-zeilen">${digital.map(zeile).join("")}</div>${liste("pr_digital_tipps")}`
        : `<p>${esc(t("pr_digital_leer"))}</p><div class="knopfzeile"><button class="knopf haupt" data-ziel-digital title="${esc(t("h_digital_knopf"))}">${esc(t("pr_digital_knopf"))}</button></div>`}
      ${appTipp()}</section>
    ${vorl.length ? `<details class="flaeche abstand"><summary title="${esc(t("h_vorlagen"))}">${esc(t("vorlagen"))}</summary><p class="klein">${esc(t("pr_vorlagen_text"))}</p><div class="liste-zeilen">${vorl.map(zeile).join("")}</div></details>` : ""}`;
}
document.addEventListener("click", e => {
  if (!e.target.closest("[data-ziel-digital]")) return;
  S.ziel = "digital"; try { localStorage.setItem("mgd-ziel", "digital"); } catch (err) { /* egal */ }
  location.hash = "#erzeugen";
});

/* ===================== Werkzeuge ===================== */
let WERKZEUGE = [];
async function ladeWerkzeuge() { WERKZEUGE = await api("/api/werkzeuge"); }
function zeichneWerkzeuge() {
  zeichneTools();
  const imToolBereich = x => x.tool && TOOLS && TOOLS.tools.some(z => z.id === x.tool);     // dort statt doppelt
  $("#werkzeug-liste").innerHTML = WERKZEUGE.filter(x => !(AM_HANDY && x.nur_rechner) && !imToolBereich(x)).map(x => `<div class="werkzeug"><div><h3 style="margin:0">${esc(x.titel)}</h3>
    <div class="klein">${esc(x.beschreibung)}</div></div><div class="knoepfe">${x.zustand ? `<span class="pille${x.aktiv ? "" : " ok"}">${esc(x.zustand)}</span>` : ""}
    <button class="knopf${x.art === "lauf" ? " dunkel" : ""}" data-werkzeug="${esc(x.id)}" data-art="${esc(x.art)}" title="${esc(x.beschreibung)}"${x.aktiv ? "" : " disabled"}>${esc(x.knopf)}</button></div></div>`).join("");
  zeichneUeEinstellungen();
  zeichneLauf();
}
async function werkzeugStarten(id, art, b) {
  if (b) b.disabled = true;
  try {
    const r = await api("/api/werkzeug", { methode: "POST", daten: { id } });
    if (art === "lauf") starteBeobachtung(r); else toast(r.meldung || t("erledigt"));
  } catch (err) { fehlerToast(err); }
  finally { if (b) b.disabled = false; }
}
$("#werkzeug-liste").addEventListener("click", e => {
  const b = e.target.closest("[data-werkzeug]"); if (!b) return;
  if (b.dataset.art === "dialog") return oeffneDialog(b.dataset.werkzeug);      // Fenster der Seite, kein Serveraufruf
  const w = WERKZEUGE.find(x => x.id === b.dataset.werkzeug);
  if (w && w.frage) return toast(w.frage, { aktion: { label: t("ja_starten"), fn: () => werkzeugStarten(w.id, w.art, b) } });  // z. B. großer Download
  werkzeugStarten(b.dataset.werkzeug, b.dataset.art, b);
});

/* ===================== Tools: optionale Funktionen (installieren, deinstallieren, Erstabfrage) ===================== */
// Reiter und Knöpfe bleiben immer sichtbar. Fehlt ein Tool, fragt brauchtTool() nach, lädt es über die Warteschlange
// und macht danach mit der ursprünglichen Aktion weiter. Server: tools.py + /api/tools, /api/tool, /api/tools-erstabfrage.
let TOOLS = null, TOOL_DLG = null, TOOL_ERST = new Set(), toolsZeit = 0;
const TOOL_WEITER = {};                                    // Tool-id → Aktionen, die nach dem Download weitergehen
async function ladeTools() {
  try { TOOLS = await api("/api/tools"); } catch (e) { if (!TOOLS) TOOLS = { tools: [], belegt: 0, erstabfrage: false }; }
  return TOOLS;
}
function toolInfo(id) { return (TOOLS && TOOLS.tools.find(x => x.id === id)) || null; }
const toolGroesse = b => b >= 1e9 ? zahl((b / 1e9).toFixed(1)) + " GB" : b >= 1048576 ? Math.round(b / 1048576) + " MB" : b > 0 ? "< 1 MB" : "0 MB";
const toolBeschaeftigt = x => x.zustand === "laeuft" || x.zustand === "wartet";
function toolPille(x) {
  if (x.zustand === "laeuft") return `<span class="pille laeuft">${esc(t("tool_laedt", x.prozent || 0))}</span>`;
  if (x.zustand === "wartet") return `<span class="pille laeuft">${esc(t("tool_wartet", x.position))}</span>`;
  if (x.zustand === "installiert") return `<span class="pille ok">${esc(t("tool_installiert"))}</span>`;
  if (x.zustand === "angefangen") return `<span class="pille">${esc(t("tool_angefangen", Math.min(99, Math.round(x.belegt * 100 / Math.max(1, x.groesse)))))}</span>`;
  return `<span class="pille">${esc(t("tool_nicht"))}</span>`;
}
function sprachListeHTML(x, besch) {                      // Tool „Sprachen“: alle 15 Sprachen einzeln
  const name = c => `${esc(zsName(c))}<small lang="${esc(c)}">${esc(zsInfo(c).eigenname || "")}</small>`;
  const alsRs = c => c === ZS.code ? `<span class="pille ok">${esc(t("sp_aktuell"))}</span>`
    : `<button class="knopf klein" type="button" data-zs-setzen="${esc(c)}" title="${esc(t("h_sp_als_rueckseite"))}">${esc(t("sp_als_rueckseite"))}</button>`;
  const zeile = (c, rechts) => `<div class="sprach-zeile">${sprachChip(c, { aktuell: c === ZS.code })}<span class="name">${name(c)}</span><div class="knopfzeile">${rechts}</div></div>`;
  return `<div class="sprach-liste">${zeile("es", `<span class="klein">${esc(t("sp_immer"))}</span>${alsRs("es")}`)}${(x.teile || []).map(p => zeile(p.id, p.installiert
    ? `${alsRs(p.id)}<button class="knopf klein leise gefahr" type="button" data-tool-aktion="teil-weg-frage" data-tool="${esc(x.id)}" data-teil="${esc(p.id)}" title="${esc(t("h_sp_entfernen"))}"${besch ? " disabled" : ""}>${esc(t("entfernen_kurz"))}</button>`
    : `<button class="knopf klein" type="button" data-tool-aktion="installieren" data-tool="${esc(x.id)}" data-teil="${esc(p.id)}" title="${esc(t("h_sp_installieren"))}"${besch ? " disabled" : ""}>${esc(t("tool_installieren"))} · ${esc(p.groesse > 0 ? toolGroesse(p.groesse) : t("sp_sofort"))}</button>`)).join("")}</div>`;
}
function toolKarte(x) {
  const besch = toolBeschaeftigt(x), groesse = x.art === "download" && x.groesse > 0 ? t("tool_download", toolGroesse(x.groesse)) : t("tool_ohne_download");
  const balken = x.zustand === "laeuft" ? `<div class="fortschritt" aria-hidden="true"><span style="width:${x.prozent || 0}%"></span></div>` : "";
  const teile = x.id === "sprachen" ? "" : x.installiert && !besch ? (x.teile || []).filter(p => !p.installiert).map(p => `<button class="knopf klein teil" data-tool-aktion="installieren"
    data-tool="${esc(x.id)}" data-teil="${esc(p.id)}" title="${esc(t("h_tool_teil"))}"><b>+ ${esc(p.titel)}</b>${p.hinweis || p.groesse > 0
      ? `<small>${esc([p.hinweis, p.groesse > 0 ? toolGroesse(p.groesse) : ""].filter(Boolean).join(" · "))}</small>` : ""}</button>`).join("") : "";
  let knoepfe = besch ? `<button class="knopf" type="button" data-ws-oeffnen title="${esc(t("h_ws_knopf"))}">⏳ ${esc(t("ws_titel"))}</button>` : "";
  if (!x.installiert && !besch && x.id !== "sprachen") knoepfe += `<button class="knopf haupt" data-tool-aktion="installieren" data-tool="${esc(x.id)}" title="${esc(t("h_tool_installieren"))}">${esc(t(x.zustand === "angefangen" ? "tool_fortsetzen" : "tool_installieren"))}</button>`;
  if ((x.installiert || x.belegt > 0) && !besch) knoepfe += `<button class="knopf leise gefahr" data-tool-aktion="deinstallieren-frage" data-tool="${esc(x.id)}" title="${esc(t("h_tool_deinstallieren"))}">${esc(t("tool_deinstallieren"))}</button>`;
  return `<div class="tool${x.installiert ? " da" : ""}" data-tool-karte="${esc(x.id)}"><div class="tool-kopf"><span class="tool-symbol" aria-hidden="true">${esc(x.symbol)}</span>
      <h3>${esc(x.titel)}</h3>${toolPille(x)}</div><p class="klein">${esc(x.nutzen)}</p>${balken}
    <div class="tool-fakten"><span>${esc(groesse)}</span>${x.belegt > 0 ? `<span>${esc(t("tool_belegt", toolGroesse(x.belegt)))}</span>` : ""}</div>
    ${teile ? `<div class="knopfzeile">${teile}</div>` : ""}${x.id === "sprachen" ? sprachListeHTML(x, besch) : ""}<div class="knopfzeile">${knoepfe}</div></div>`;
}
function zeichneTools() {
  const el = $("#tools-bereich"); if (!el) return;
  el.hidden = !(TOOLS && TOOLS.tools.length); if (el.hidden) return;
  el.innerHTML = `<div class="tools-kopf"><h2 style="margin:0">🧰 ${esc(t("tools_titel"))}</h2><span class="klein">${esc(t("tools_belegt", toolGroesse(TOOLS.belegt)))}</span></div>
    <p class="unter klein">${esc(t("tools_unter"))}</p><div class="tools-raster">${TOOLS.tools.map(toolKarte).join("")}</div>`;
}
function toolsAuffrischen() { return ladeTools().then(() => { if (ansicht() === "werkzeuge") zeichneWerkzeuge(); if (ansicht() === "verbesserung") zeichneVerbTool(); }); }
function toolsNebenbei() {                                 // Fortschritt der Tool-Karten während eines Downloads (≤ alle 1,5 s)
  if (ansicht() !== "werkzeuge" || !TOOLS || Date.now() - toolsZeit < 1500) return;
  if (!TOOLS.tools.some(toolBeschaeftigt) && !(S.lauf && S.lauf.tool && S.lauf.laeuft)) return;
  toolsZeit = Date.now(); toolsAuffrischen();
}
// Gemeinsamer Einstieg für jede Funktion, die ein Tool braucht: installiert → weiter(); sonst Rückfrage → Download
// über die Warteschlange → danach weiter() automatisch (Seite offen) bzw. Toast „Tool … ist bereit“.
async function brauchtTool(id, weiter, { alternativ = null, alternativText = null } = {}) {
  if (!toolInfo(id)) await ladeTools();
  const x = toolInfo(id);
  if (!x || x.installiert) return weiter();                 // unbekannt (z. B. ohne tools.py) oder schon da
  if (toolBeschaeftigt(x)) {                                 // lädt schon → danach weitermachen
    (TOOL_WEITER[id] = TOOL_WEITER[id] || []).push(weiter);
    return toast(t("tool_kommt", x.titel), { aktion: { label: t("ws_ansehen_kurz"), fn: () => oeffneWs() } });
  }
  if (x.zustimmung) return toolInstallieren(id, { weiter }); // Übersetzung: die Zustimmung ist die Rückfrage
  TOOL_DLG = { art: "brauchen", id, weiter, alternativ, alternativText }; zeichneToolFenster(); $("#tool-fenster").hidden = false;
}
async function toolInstallieren(id, { teil = null, knopf = null, weiter = null } = {}) {
  const x = toolInfo(id); if (!x) return false;
  if (x.zustimmung && !x.installiert && !await frageZustimmung()) return false;
  if (knopf) knopf.disabled = true;
  try {
    const r = await api("/api/tool", { methode: "POST", daten: { id, aktion: "installieren", teil } });
    if (r.lauf) {
      if (weiter) (TOOL_WEITER[id] = TOOL_WEITER[id] || []).push(weiter);
      if (!r.lauf.wartet) toast(t("tool_laedt_los", x.titel));
      starteBeobachtung(r.lauf);
    } else { toast(r.meldung || t("tool_ist_bereit", x.titel)); if (weiter) setTimeout(weiter, 0); }
    await toolsAuffrischen(); ladeStatus();
    if (id === "lernen" && !r.lauf) lernAktiviert();
    return true;
  } catch (err) { fehlerToast(err); return false; }
  finally { if (knopf) knopf.disabled = false; }
}
async function toolDeinstallieren(id, teil = null) {
  try { const r = await api("/api/tool", { methode: "POST", daten: { id, aktion: "deinstallieren", teil } }); toast(r.meldung); if (r.zielsprache_zurueck) toast(t("sp_zurueck")); }
  catch (err) { fehlerToast(err); }
  await toolsAuffrischen(); ladeStatus(); ladeWerkzeuge().catch(() => {});
  if (id === "uebersetzung") ladeUe().then(zeichneUeEinstellungen);
  if (id === "lernen" && !lernDa()) { LERN = null; LS = null; S.lernFilter = ""; S.lernAuswahl = null; lernZahl(); ladeKartenSpaeter(); if (ansicht() === "lernen") zeichneLernen(); }
}
async function toolFertig(L) {                             // Download eines Tools beendet (einmal je Auftrag)
  await ladeTools(); ladeStatus(); ladeWerkzeuge().then(() => { if (ansicht() === "werkzeuge") zeichneWerkzeuge(); }).catch(() => {});
  const x = toolInfo(L.tool), fns = TOOL_WEITER[L.tool] || []; delete TOOL_WEITER[L.tool];
  if (L.code === 0 && x && x.installiert) {
    toast(t("tool_ist_bereit", x.titel));
    for (const fn of fns) { try { await fn(); } catch (e) { fehlerToast(e); } }
  } else if (!L.abgebrochen) toast(t("tool_nicht_geklappt", x ? x.titel : L.titel), { fehler: true });
  if (ansicht() === "verbesserung") ladeVerbesserung();
}
function toolFrageHTML(x) {                                // Nutzen, Größe, Speicherort, Zeit grob
  return `<p>${esc(x.nutzen)}</p><dl class="tool-dl"><dt>${esc(t("tool_groesse"))}</dt><dd>${esc(x.art === "download" ? t("tool_download", toolGroesse(x.groesse)) : t("tool_ohne_download"))}</dd>
    <dt>${esc(t("tool_ort"))}</dt><dd>${esc(x.ort)}</dd><dt>${esc(t("tool_dauer"))}</dt><dd>${esc(x.dauer)}</dd>
    <dt>${esc(t("tool_quelle"))}</dt><dd>${esc(x.quelle)}</dd></dl>${toolHinweiseHTML(x)}`;
}
function toolHinweiseHTML(x) {                             // Arbeitsspeicher (KI-Bilder) und freier Platz vor dem Download
  const h = [];
  if (x.ram_gb && x.ram_gb < 8) h.push(t("tool_ram_wenig", zahl(String(Math.round(x.ram_gb * 10) / 10))));
  if (x.art === "download" && x.frei != null && x.frei < x.platz - (x.belegt || 0)) h.push(t("tool_platz_knapp", toolGroesse(x.frei), toolGroesse(x.platz)));
  return h.map(s => `<p class="klein"><b>${esc(s)}</b></p>`).join("");
}
const toolFehlt = e => !!(e && e.status === 409 && e.daten && e.daten.code === "tool_fehlt" && e.daten.tool);
function toolErstHTML() {                                  // Erstabfrage – gemeinsam für Willkommens-Assistent und Fenster
  const offen = (TOOLS ? TOOLS.tools : []).filter(x => !x.installiert);
  const summe = offen.filter(x => TOOL_ERST.has(x.id)).reduce((s, x) => s + x.groesse, 0);
  return `<p>${esc(t("tools_erst_text"))}</p><div class="tool-liste">${offen.map(x => `<label class="tool-wahl"><input type="checkbox" data-tool-wahl="${esc(x.id)}"${TOOL_ERST.has(x.id) ? " checked" : ""}>
      <span><b>${esc(x.symbol)} ${esc(x.titel)}</b><span class="klein">${esc(x.nutzen)}</span>
      <span class="klein">${esc(x.art === "download" ? t("tool_download", toolGroesse(x.groesse)) : t("tool_ohne_download"))} · ${esc(x.dauer)}</span></span></label>`).join("")}</div>
    <p class="klein"><b data-tool-summe>${esc(t("tools_erst_summe", toolGroesse(summe)))}</b></p><p class="klein">${esc(t("tools_erst_spaeter"))}</p>`;
}
function zeichneToolFenster() {
  const d = TOOL_DLG; if (!d) return;
  if (d.art === "erst") {
    $("#tool-titel").textContent = t("tools_erst_titel");
    $("#tool-inhalt").innerHTML = toolErstHTML() + `<div class="knopfzeile abstand"><div class="rechts">
      <button class="knopf leise" data-tool-dlg="erst-spaeter">${esc(t("tools_erst_spaeter_knopf"))}</button>
      <button class="knopf haupt" data-tool-dlg="erst-los">${esc(t("tools_erst_los", TOOL_ERST.size))}</button></div></div>`;
    return;
  }
  const x = toolInfo(d.id); if (!x) return;
  if (d.art === "brauchen") {
    $("#tool-titel").textContent = `${x.symbol} ${x.titel}`;
    $("#tool-inhalt").innerHTML = `<p><b>${esc(t("tool_brauchen_text", x.titel))}</b></p>${toolFrageHTML(x)}<p class="klein">${esc(t("tool_brauchen_hinweis"))}</p>
      <div class="knopfzeile abstand"><div class="rechts"><button class="knopf leise" data-zu>${esc(t("abbrechen"))}</button>
      ${d.alternativ ? `<button class="knopf" data-tool-dlg="ohne">${esc(d.alternativText || t("tool_ohne"))}</button>` : ""}
      <button class="knopf haupt" data-tool-dlg="installieren">${esc(t("tool_installieren_weiter"))}</button></div></div>`;
  }
  if (d.art === "weg" && d.teil) {                         // eine Sprache entfernen: Kartentexte bleiben
    $("#tool-titel").textContent = t("sp_weg_titel", zsName(d.teil));
    $("#tool-inhalt").innerHTML = `<p>${esc(t("sp_weg_text"))}</p>${d.teil === ZS.code ? `<p class="klein"><b>${esc(t("sp_weg_ziel"))}</b></p>` : ""}
      <div class="knopfzeile abstand"><div class="rechts"><button class="knopf haupt" data-zu>${esc(t("tool_weg_nein"))}</button>
      <button class="knopf gefahr-voll" data-tool-dlg="deinstallieren">${esc(t("tool_weg_ja"))}</button></div></div>`;
    return;
  }
  if (d.art === "weg") {
    $("#tool-titel").textContent = t("tool_weg_titel", x.titel);
    $("#tool-inhalt").innerHTML = `<p>${esc(t("tool_weg_text"))}</p><div class="gefahr-flaeche"><ul><li>${esc(x.loeschen)}</li>
      <li>${esc(t("tool_weg_frei", toolGroesse(x.belegt)))}</li></ul></div><p class="klein">✓ ${esc(t("tool_weg_bleibt"))}</p>
      ${x.id === "lernen" ? `<p><a class="knopf" href="/api/lernen-export" download title="${esc(t("h_ln_export"))}">⇩ ${esc(t("ln_export_vorher"))}</a></p>` : ""}
      <div class="knopfzeile abstand"><div class="rechts"><button class="knopf haupt" data-zu>${esc(t("tool_weg_nein"))}</button>
      <button class="knopf gefahr-voll" data-tool-dlg="deinstallieren">${esc(t("tool_weg_ja"))}</button></div></div>`;
  }
}
function oeffneToolErstabfrage() { TOOL_DLG = { art: "erst" }; TOOL_ERST = new Set(); zeichneToolFenster(); $("#tool-fenster").hidden = false; }
async function toolsErstabfrageSenden(auswahl) {          // leere Auswahl = „Später“ (nicht noch einmal fragen)
  try {
    TOOLS = await api("/api/tools-erstabfrage", { methode: "POST", daten: { auswahl } });
    for (const st of TOOLS.laeufe || []) starteBeobachtung(st);
    if ((TOOLS.laeufe || []).length) toast(t("tools_erst_ok"));
    for (const id of TOOLS.offen || []) await toolInstallieren(id);   // Übersetzung: erst die Zustimmung
  } catch (err) { fehlerToast(err); }
  toolsAuffrischen();
}
document.addEventListener("change", e => {
  const c = e.target.closest && e.target.closest("[data-tool-wahl]"); if (!c) return;
  c.checked ? TOOL_ERST.add(c.dataset.toolWahl) : TOOL_ERST.delete(c.dataset.toolWahl);
  const summe = (TOOLS ? TOOLS.tools : []).filter(x => TOOL_ERST.has(x.id)).reduce((s, x) => s + x.groesse, 0);
  $$("[data-tool-summe]").forEach(el => { el.textContent = t("tools_erst_summe", toolGroesse(summe)); });
  const los = $('[data-tool-dlg="erst-los"]'); if (los) los.textContent = t("tools_erst_los", TOOL_ERST.size);
});
document.addEventListener("click", e => {
  const b = e.target.closest("[data-tool-aktion]"); if (!b) return;
  const id = b.dataset.tool, a = b.dataset.toolAktion;
  if (a === "installieren") return toolInstallieren(id, { teil: b.dataset.teil || null, knopf: b });
  if (a === "deinstallieren-frage") { TOOL_DLG = { art: "weg", id }; zeichneToolFenster(); $("#tool-fenster").hidden = false; }
  if (a === "teil-weg-frage") { TOOL_DLG = { art: "weg", id, teil: b.dataset.teil }; zeichneToolFenster(); $("#tool-fenster").hidden = false; }
});
document.addEventListener("click", async e => {
  const b = e.target.closest("[data-zs-setzen]"); if (!b) return;
  b.disabled = true; await setzeZielsprache(b.dataset.zsSetzen); toolsAuffrischen();
});
$("#tool-inhalt").addEventListener("click", e => {
  const b = e.target.closest("[data-tool-dlg]"); if (!b || !TOOL_DLG) return;
  const d = TOOL_DLG, a = b.dataset.toolDlg;
  TOOL_DLG = null; $("#tool-fenster").hidden = true;
  if (a === "erst-los" || a === "erst-spaeter") return toolsErstabfrageSenden(a === "erst-los" ? [...TOOL_ERST] : []);
  if (a === "ohne" && d.alternativ) return d.alternativ();
  if (a === "installieren") return toolInstallieren(d.id, { weiter: d.weiter });
  if (a === "deinstallieren") return toolDeinstallieren(d.id, d.teil || null);
});

/* ----- Einstellungen der automatischen Übersetzung ----- */
async function ladeUe() { try { S.ue = await api("/api/uebersetzung"); } catch (e) { /* Verbindungshinweis erscheint */ } }
function zeichneUeEinstellungen() {
  const u = S.ue, el = $("#ue-einstellungen"); if (!u || !el) return;
  const getippt = $("#ue-deepl") ? $("#ue-deepl").value : "", fokus = document.activeElement && document.activeElement.id === "ue-deepl";
  const dienst = (id, titel, text, gesperrt) => `<label class="dienst"><input type="radio" name="ue-dienst" value="${esc(id)}"${u.dienst === id ? " checked" : ""}${gesperrt ? " disabled" : ""}>
    <span><b>${esc(titel)}</b><span class="klein">${esc(text)}</span></span></label>`;
  el.innerHTML = `<div class="ue-kopf"><h2 style="margin:0">${esc(t("ue_titel"))}</h2>
      <span class="pille${u.zugestimmt ? " ok" : ""}">${esc(u.zugestimmt ? t("ue_an") : t("ue_aus"))}</span></div>
    <p class="unter klein">${esc(t("ue_text"))}</p>
    <label class="schalter abstand"><input type="checkbox" data-ue="zugestimmt"${u.zugestimmt ? " checked" : ""}><span class="spur"></span><span>${esc(t("ue_einschalten"))}</span></label>
    <div class="abstand"><b>${esc(t("ue_dienst"))}</b><div class="dienste" role="radiogroup">
      ${dienst("auto", t("ue_auto"), t("ue_auto_text"), false)}
      ${(u.dienste || []).map(d => dienst(d.id, d.titel, `${d.beschreibung} (${d.adresse})`, d.konto && !u.deepl_gesetzt)).join("")}
    </div></div>
    <div class="f abstand"><label class="titel" for="ue-deepl">${esc(t("ue_deepl"))}</label>
      ${u.deepl_gesetzt ? `<div class="knopfzeile"><span>${esc(t("ue_deepl_da", u.deepl_ende))}</span>
          <button class="knopf klein leise gefahr" data-ue-aktion="deepl-weg" title="${esc(t("h_ue_deepl_weg"))}">${esc(t("entfernen_kurz"))}</button></div>`
        : `<div class="mit-knopf"><input class="eingabe" type="password" id="ue-deepl" autocomplete="off" spellcheck="false" placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:fx">
          <button class="knopf" data-ue-aktion="deepl" title="${esc(t("h_ue_deepl"))}">${esc(t("speichern"))}</button></div>
          <span class="klein">${esc(t("ue_deepl_hilfe"))} <a href="https://www.deepl.com/pro-api" target="_blank" rel="noopener noreferrer">deepl.com/pro-api</a></span>`}
    </div>
    <label class="schalter abstand"><input type="checkbox" data-ue="automatisch"${u.automatisch ? " checked" : ""}${u.zugestimmt ? "" : " disabled"}><span class="spur"></span><span>${esc(t("ue_automatisch"))}</span></label>
    <div class="knopfzeile abstand"><button class="knopf klein" data-ue-aktion="cache" title="${esc(t("h_ue_cache"))}">${esc(t("ue_cache"))}</button></div>
    <p class="klein">${esc(t("ue_datenschutz", u.ablage || ""))}</p>`;
  const feld = $("#ue-deepl"); if (feld && getippt) { feld.value = getippt; if (fokus) feld.focus(); }     // Getipptes nicht verlieren
}
async function ueSetzen(daten, meldung) {
  try { S.ue = await api("/api/uebersetzung", { methode: "POST", daten }); await ladeStatus(); if (meldung) toast(meldung); }
  catch (e) { fehlerToast(e); }
  zeichneUeEinstellungen();
}
$("#ue-einstellungen").addEventListener("change", e => {
  if (e.target.dataset.ue) {
    if (e.target.dataset.ue === "zugestimmt" && e.target.checked) { e.target.checked = false; frageZustimmung().then(() => zeichneUeEinstellungen()); return; }
    return ueSetzen({ [e.target.dataset.ue]: e.target.checked });
  }
  if (e.target.name === "ue-dienst") ueSetzen({ dienst: e.target.value });
});
$("#ue-einstellungen").addEventListener("click", e => {
  const b = e.target.closest("[data-ue-aktion]"); if (!b) return;
  const a = b.dataset.ueAktion;
  if (a === "deepl") { const f = $("#ue-deepl"); const k = f.value.trim(); f.value = ""; if (k) ueSetzen({ deepl: k }, t("ue_deepl_ok")); }
  if (a === "deepl-weg") ueSetzen({ deepl: "" }, t("ue_deepl_weg"));
  if (a === "cache") ueSetzen({ cache_leeren: true }, t("ue_cache_ok"));
});
$("#ue-einstellungen").addEventListener("keydown", e => {
  if (e.key === "Enter" && e.target.id === "ue-deepl") { e.preventDefault(); $('[data-ue-aktion="deepl"]').click(); }
});

/* ===================== Hilfe ===================== */
let hilfeAnfrage = null;                            // laufende Hilfe-Anfrage (nur die des zuletzt gewählten Reiters zählt)
async function ladeHilfe() {
  $$(".reiter button").forEach(b => b.setAttribute("aria-selected", String(b.dataset.doc === S.doc)));
  if (hilfeAnfrage) { const alt = hilfeAnfrage; hilfeAnfrage = null; alt.abort(); }
  if (S.doc === "ueber") {
    const s = S.status;
    $("#doku").innerHTML = `<h2 style="margin-top:0">${esc(t("tab_ueber"))}</h2><dl class="ueber">
      <dt>${esc(t("u_generator"))}</dt><dd>${esc(s.version)}</dd><dt>${esc(t("u_oberflaeche"))}</dt><dd>${esc(s.ui_version)}</dd>
      <dt>${esc(t("u_python"))}</dt><dd>${esc(s.python)}</dd><dt>${esc(t("u_projekt"))}</dt><dd>${esc(s.projekt)}</dd>
      <dt>${esc(t("u_schrift"))}</dt><dd>${esc(s.schrift)}</dd><dt>${esc(t("u_ki"))}</dt><dd>${esc(s.ki_name)}</dd>
      <dt>${esc(t("u_vorschau"))}</dt><dd>${esc(s.vorschau ? t("u_vorschau_ok") : t("u_vorschau_nein"))}</dd>
      <dt>${esc(t("u_uebersetzung"))}</dt><dd>${esc(s.uebersetzung && s.uebersetzung.zugestimmt ? t("ue_an") + " – " + t("ue_dienst_" + s.uebersetzung.dienst) : t("ue_aus"))}</dd>
      <dt>${esc(t("u_kartensprache"))}</dt><dd>${esc(t("u_kartensprache_wert"))}${zsMehrere() ? " · " + esc(ZS.installiert.map(c => zsInfo(c).kurz).join(" ")) : ""}</dd>
      ${s.tools && Object.keys(s.tools).length ? `<dt>${esc(t("u_tools"))}</dt><dd>${Object.entries(s.tools).map(([id, da]) =>
        esc(`${(toolInfo(id) || {}).titel || id}: ${t(da ? "tool_installiert" : "tool_nicht")}`)).join("<br>")}</dd>` : ""}
      ${downloadAdresse() ? `<dt>${esc(t("u_download"))}</dt><dd><a href="${esc(downloadAdresse())}" target="_blank" rel="noopener">${esc(t("u_download_text"))}</a></dd>` : ""}
      <dt>${esc(t("u_letzter"))}</dt><dd>${esc(s.letzter_lauf ? datum(s.letzter_lauf) : t("u_keiner"))}</dd></dl>
      <h3 style="margin-top:24px">${esc(t("u_erweitern"))}</h3><p>${esc(t("u_erweitern_text"))}</p>`;
    return;
  }
  const ctrl = new AbortController(); hilfeAnfrage = ctrl;
  $("#doku").innerHTML = enteHTML(t("hilfe_laedt"))
    + `<div class="knopfzeile"><button class="knopf" type="button" id="hilfe-abbrechen">${esc(t("hilfe_abbrechen"))}</button></div>`;
  $("#hilfe-abbrechen").addEventListener("click", () => ctrl.abort());
  try {
    const d = await api(url("/api/hilfe", { doc: S.doc }), { timeout: 20000, signal: ctrl.signal });
    if (hilfeAnfrage === ctrl) $("#doku").innerHTML = d.html;
  } catch (e) {
    if (hilfeAnfrage !== ctrl) return;                 // inzwischen anderer Reiter gewählt → alte Antwort verwerfen
    $("#doku").innerHTML = `<p>${esc(e.message)}</p><div class="knopfzeile"><button class="knopf" type="button" id="hilfe-nochmal">${esc(t("hilfe_nochmal"))}</button></div>`;
    $("#hilfe-nochmal").addEventListener("click", ladeHilfe);
  } finally { if (hilfeAnfrage === ctrl) hilfeAnfrage = null; }
}
$(".reiter").addEventListener("click", e => { const b = e.target.closest("[data-doc]"); if (b) { S.doc = b.dataset.doc; ladeHilfe(); } });

/* ===================== Automatische Übersetzung (nur Vorschläge, nur nach Zustimmung) ===================== */
// Die Seite selbst spricht mit keinem fremden Rechner: Sie fragt nur den eigenen Server (/api/uebersetzen),
// der das Wort an den gewählten Dienst schickt (Einzelheiten und Schutzmaßnahmen: uebersetzer.py).
let zustimmungFertig = null;
function frageZustimmung() {
  return new Promise(resolve => {
    $("#zustimmung-text").innerHTML = `<p>${esc(t("zust_1"))}</p><ul><li>${esc(t("zust_2"))}</li><li>${esc(t("zust_3"))}</li>
      <li>${esc(t("zust_4"))}</li><li>${esc(t("zust_5"))}</li></ul><p class="klein">${esc(t("zust_6"))}</p>`;
    $("#zustimmung-auto").checked = false;
    $("#zustimmung").hidden = false; $("#zustimmung-ja").focus();
    zustimmungFertig = async ja => {
      $("#zustimmung").hidden = true; zustimmungFertig = null;
      if (!ja) return resolve(false);
      try {
        S.ue = await api("/api/uebersetzung", { methode: "POST", daten: { zugestimmt: true, automatisch: $("#zustimmung-auto").checked } });
        await ladeStatus(); if (ansicht() === "werkzeuge") zeichneUeEinstellungen();
        resolve(true);
      } catch (e) { fehlerToast(e); resolve(false); }
    };
  });
}
async function uebersetzungsTool() {                       // 409 „zustimmung“: Zustimmung erteilen = Tool „Übersetzung“ installieren
  if (!await frageZustimmung()) return false;
  try { await api("/api/tool", { methode: "POST", daten: { id: "uebersetzung", aktion: "installieren" } }); } catch (e) { /* Zustimmung reicht */ }
  ladeTools(); return true;
}
$("#zustimmung-ja").addEventListener("click", () => zustimmungFertig && zustimmungFertig(true));
$("#zustimmung-nein").addEventListener("click", () => zustimmungFertig && zustimmungFertig(false));
async function holeVorschlag(de, ziel) {                   // ziel: andere installierte Sprache (sonst Zielsprache)
  const daten = ziel ? { de, ziel } : { de };
  try { return await api("/api/uebersetzen", { methode: "POST", daten }); }
  catch (e) {
    if (e.status === 409 && e.daten && e.daten.code === "zustimmung") {
      if (!await uebersetzungsTool()) return null;
      return await api("/api/uebersetzen", { methode: "POST", daten });
    }
    throw e;
  }
}
function vorschlagHTML(v) {
  if (!v) return "";
  if (!v.vorschlag) return `<div class="vorschlag"><span>${esc(t("kein_vorschlag", v.quelle || ""))}</span></div>`;
  const haupt = v.vorschlag.split(" / ");
  const weitere = (v.alternativen || []).filter(a => !haupt.includes(a.text)).slice(0, 6);
  const titel = a => [a.hinweis, t("chip_titel")].filter(Boolean).join(" – ");
  const erster = (v.alternativen || []).find(a => a.text === haupt[0]) || {};
  return `<div class="vorschlag">
    <span class="quelle">${esc(t("vorschlag_von", t("ue_dienst_" + v.dienst) || v.dienst_name || "", v.quelle || ""))}</span>
    <div class="chips"><button type="button" class="chip haupt" data-chip="${esc(v.vorschlag)}" title="${esc(titel(erster))}">${esc(v.vorschlag)}</button>${weitere.map(a =>
      `<button type="button" class="chip" data-chip="${esc(a.text)}" title="${esc(titel(a))}">${esc(a.text)}</button>`).join("")}</div></div>`;
}
function vorschlagFehlerHTML(e) { return `<div class="vorschlag fehler">${esc(e.message)}</div>`; }
async function alleUebersetzen(knopf, auftraege) {
  if (!auftraege.length) return;
  const alt = knopf.textContent; S.beschaeftigt = true; knopf.disabled = true;
  let n = 0, gefuellt = 0;
  try {
    for (const a of auftraege) {
      knopf.textContent = t("uebersetze_n", ++n, auftraege.length);
      if (!String(a.de || "").trim()) continue;
      const v = await holeVorschlag(a.de); if (!v) break;
      if (a.fuellen(v)) gefuellt++;
    }
    toast(t("uebersetzt_n", gefuellt, auftraege.length));
  } catch (e) { fehlerToast(e); }
  finally { S.beschaeftigt = false; knopf.disabled = false; knopf.textContent = alt; }
}
const ueSchlange = []; let ueArbeitet = false, ueFehlerGezeigt = false;
function automatischUebersetzen(schluessel, de, fuellen) {
  const u = S.status.uebersetzung || {};
  if (!u.zugestimmt || !u.automatisch || !String(de || "").trim() || S.autoVersucht.has(schluessel)) return;
  S.autoVersucht.add(schluessel); ueSchlange.push({ de, fuellen }); arbeiteUeSchlange();
}
async function arbeiteUeSchlange() {
  if (ueArbeitet) return; ueArbeitet = true;
  while (ueSchlange.length) {
    const a = ueSchlange.shift();
    try { a.fuellen(await api("/api/uebersetzen", { methode: "POST", daten: { de: a.de } })); }
    catch (e) {
      if (!ueFehlerGezeigt) { ueFehlerGezeigt = true; toast(t("auto_fehler", e.message), { fehler: true }); }
      if (e.status === 409) { ueSchlange.length = 0; break; }
    }
  }
  ueArbeitet = false;
}

/* ===================== Tabelle: Vorderseite und Rückseite nebeneinander ===================== */
let TAB = { karten: [] };
const TAB_FILTER = ["alle", "ungeprueft", "auto", "ohne", "hinweise"];
async function ladeTabelle() {
  if (!TAB.karten.length) { $("#tabelle").innerHTML = `<tbody><tr><td colspan="7">${enteHTML()}</td></tr></tbody>`; $("#tabelle-kompakt").innerHTML = `<tbody><tr><td>${enteHTML()}</td></tr></tbody>`; }
  try { TAB = await api("/api/tabelle"); }
  catch (e) {                                                // Ente nicht stehen lassen: Fehlertext statt Ladeanzeige
    fehlerToast(e);
    if ($("#tabelle .ente-laedt")) {
      $("#tabelle").innerHTML = `<tbody><tr><td colspan="7">${esc(e.message)}</td></tr></tbody>`;
      $("#tabelle-kompakt").innerHTML = `<tbody><tr><td>${esc(e.message)}</td></tr></tbody>`;
    }
    return;
  }
  zeichneTabelle();
}
const tabWeitere = () => zsMehrere() ? ZS.installiert.filter(c => c !== ZS.code) : [];
const tabFilterListe = () => TAB_FILTER.concat(tabWeitere().map(c => "fehlt:" + c));
function tabPasst(k, filter) {
  if (filter.startsWith("fehlt:")) return !rsText(k, filter.slice(6)).trim();
  const es = String(k.es || "").trim();
  if (filter === "ungeprueft") return es && k.uebersetzung !== "geprueft";
  if (filter === "auto") return k.uebersetzung === "auto";
  if (filter === "ohne") return !es;
  if (filter === "hinweise") return (k.meldungen || []).length > 0;
  return true;
}
function tabZeilen() {
  const s = S.tabSuche.toLocaleLowerCase();
  let z = TAB.karten.filter(k => tabPasst(k, S.tabFilter) && (!s || [k.de, k.es, k.notiz, k.bild].some(x => String(x || "").toLocaleLowerCase().includes(s))));
  if (S.tabSort) {
    const { spalte, ab } = S.tabSort;
    const wertVon = k => spalte === "nr" ? (k.aktiv && k.nr ? k.nr : 1e9) : String(k[spalte] || "").toLocaleLowerCase();
    z = z.slice().sort((a, b) => { const x = wertVon(a), y = wertVon(b); return (x < y ? -1 : x > y ? 1 : 0) * (ab ? -1 : 1); });
  }
  return z;
}
function tabStatusHTML(k) {
  const es = String(k.es || "").trim();
  return `${es ? `<label class="geprueft"><input type="checkbox" data-geprueft${k.uebersetzung === "geprueft" ? " checked" : ""}>${esc(t("geprueft"))}</label>` : ""}
    ${k.uebersetzung === "auto" ? `<div><span class="marke-q auto" title="${esc(t("marke_auto_titel"))}">${esc(t("marke_auto"))}</span></div>` : ""}
    ${k.aktiv ? "" : `<div class="klein">${esc(t("marke_aus"))}</div>`}`;
}
function tabHinweiseHTML(k) {
  return (k.meldungen || []).length ? `<ul class="hinweisliste">${k.meldungen.map(m => `<li class="${esc(m.stufe)}">${esc(m.text)}</li>`).join("")}</ul>` : "";
}
function tabZeileHTML(k, bilder) {
  const nr = k.aktiv && k.nr ? k.nr : "–", es = String(k.es || "");
  return `<tr data-bild="${esc(k.bild)}" class="${k.aktiv ? "" : "aus"}">
    <td class="nrz"><span class="nr${k.aktiv && k.nr ? "" : " ohne"}" title="${esc(t("nr_titel"))}">${esc(nr)}</span></td>
    ${bilder ? `<td class="bildz">${k.existiert ? `<span class="mini"><img loading="lazy" alt="" data-seite="vorn" data-bild="${esc(k.bild)}" src="${vorschauUrl(k, "vorn")}"></span>` : `<span class="klein">${esc(t("bild_fehlt"))}</span>`}</td>` : ""}
    <td data-label="${esc(t("spalte_de"))}"><textarea class="zelle-eingabe" rows="1" data-feld="de" lang="de" aria-label="${esc(t("spalte_de"))}" autocomplete="off" spellcheck="false">${esc(k.de)}</textarea>
      <div class="datei">${esc(k.bild)}</div></td>
    <td class="pfeilz" aria-hidden="true">→</td>
    <td data-label="${esc(t("spalte_es"))}"><div class="mit-knopf"><textarea class="zelle-eingabe es${es.trim() ? "" : " leer"}${k.uebersetzung === "auto" ? " ist-auto" : ""}" rows="1" data-feld="es" ${zsAttr()}
        placeholder="${esc(t("es_fehlt_ph"))}" aria-label="${esc(t("spalte_es"))}" autocomplete="off">${esc(es)}</textarea>
      <button type="button" class="knopf klein leise symbolknopf" data-tab-aktion="uebersetzen" title="${esc(t("uebersetzen_titel"))}" aria-label="${esc(t("uebersetzen_titel"))}" data-nicht-drucken>🌐</button></div>
      <div data-teil="vorschlag">${vorschlagHTML(S.vorschlaege["t:" + k.bild])}</div>
      <div data-teil="hinweise">${tabHinweiseHTML(k)}</div>
      <div class="zellen-meldung" data-teil="meldung"></div></td>
    ${tabWeitere().map(c => `<td class="rs-weitere" data-label="${esc(t("spalte_rs", zsName(c)))}"><span ${zsAttr(c)}>${esc(rsText(k, c)) || "–"}</span></td>`).join("")}
    <td data-label="${esc(t("spalte_notiz"))}"><textarea class="zelle-eingabe" rows="1" data-feld="notiz" aria-label="${esc(t("spalte_notiz"))}" autocomplete="off">${esc(k.notiz)}</textarea></td>
    <td class="statusz" data-teil="status">${tabStatusHTML(k)}</td>
  </tr>`;
}
function zeichneTabelle() {
  const zahl = f => TAB.karten.filter(k => tabPasst(k, f)).length, filter = tabFilterListe();
  if (!filter.includes(S.tabFilter)) S.tabFilter = "alle";
  $("#tabelle-filter").innerHTML = filter.map(f => `<label><input type="radio" name="tabfilter" value="${f}"${S.tabFilter === f ? " checked" : ""}><span>${esc(f.startsWith("fehlt:") ? t("filter_fehlt", zsName(f.slice(6))) : t("filter_" + f))} (${zahl(f)})</span></label>`).join("");
  const bilder = $("#tabelle-bilder").checked, zeilen = tabZeilen();
  const kopf = (spalte, text, kl = "") => `<th class="${kl}"${S.tabSort && S.tabSort.spalte === spalte ? ` aria-sort="${S.tabSort.ab ? "descending" : "ascending"}"` : ""}><button type="button" data-sort="${spalte}">${esc(text)}${S.tabSort && S.tabSort.spalte === spalte ? (S.tabSort.ab ? " ▼" : " ▲") : ""}</button></th>`;
  $("#tabelle").innerHTML = `<thead><tr>${kopf("nr", t("spalte_nr"), "nrz")}${bilder ? `<th class="bildz">${esc(t("spalte_bild"))}</th>` : ""}
    ${kopf("de", t("spalte_de"))}<th class="pfeilz"></th>${kopf("es", t("spalte_es"))}${tabWeitere().map(c => `<th class="rs-weitere">${sprachChip(c, { aktuell: false })} ${esc(zsName(c))}</th>`).join("")}${kopf("notiz", t("spalte_notiz"))}<th class="statusz">${esc(t("spalte_status"))}</th></tr></thead>
    <tbody>${zeilen.map(k => tabZeileHTML(k, bilder)).join("") || `<tr><td colspan="7" class="tabelle-leer">${esc(TAB.karten.length ? t("tabelle_nichts") : t("karten_leer_unter"))}</td></tr>`}</tbody>`;
  requestAnimationFrame(() => $$("#tabelle textarea").forEach(passeHoeheAn));
  $("#tabelle-uebersetzen").hidden = !TAB.karten.some(k => !String(k.es || "").trim() && String(k.de || "").trim());
  zeichneKompakt(zeilen);
}
/* ----- Kompakte Ansicht: nur Nr., Vorderseite, Rückseite, Notiz, Prüfung – zum Lesen und Drucken ----- */
let tabAnsicht = "bearbeiten";
try { if (localStorage.getItem("mgd-tabansicht") === "kompakt") tabAnsicht = "kompakt"; } catch (e) { /* ohne Speicher: Standard */ }
function kompaktStatus(k) {
  const es = String(k.es || "").trim();
  if (!es) return `<span class="k-status">${esc(t("k_status_ohne"))}</span>`;
  if (k.uebersetzung === "geprueft") return `<span class="k-status ok">${esc(t("k_status_ok"))}</span>`;
  if (k.uebersetzung === "auto") return `<span class="k-status auto">${esc(t("k_status_auto"))}</span>`;
  return `<span class="k-status">${esc(t("k_status_offen"))}</span>`;
}
function zeichneKompakt(zeilen) {
  const kopf = (spalte, text, kl) => `<th class="${kl}"><button type="button" data-sort="${spalte}">${esc(text)}${S.tabSort && S.tabSort.spalte === spalte ? (S.tabSort.ab ? " ▼" : " ▲") : ""}</button></th>`;
  $("#tabelle-kompakt").innerHTML = `<thead><tr>${kopf("nr", t("spalte_nr"), "k-nr")}${kopf("de", t("spalte_de"), "k-de")}${kopf("es", t("spalte_es"), "k-es")}
    ${tabWeitere().map(c => `<th class="k-es rs-weitere">${esc(zsInfo(c).kurz)}</th>`).join("")}${kopf("notiz", t("spalte_notiz"), "k-notiz")}<th class="k-pruef">${esc(t("spalte_status"))}</th></tr></thead>
    <tbody>${zeilen.map(k => `<tr data-k-bild="${esc(k.bild)}" class="${k.aktiv ? "" : "aus"}" title="${esc(t("k_titel"))}">
      <td class="k-nr">${esc(k.aktiv && k.nr ? k.nr : "–")}</td><td class="k-de">${esc(k.de || "")}</td>
      <td class="k-es" ${zsAttr()}>${esc(k.es || "")}${k.aktiv ? "" : ` <span class="klein">${esc(t("k_aus"))}</span>`}</td>
      ${tabWeitere().map(c => `<td class="k-es rs-weitere" ${zsAttr(c)}>${esc(rsText(k, c))}</td>`).join("")}<td class="k-notiz">${esc(k.notiz || "")}</td><td class="k-pruef">${kompaktStatus(k)}</td></tr>`).join("")
      || `<tr><td colspan="5" class="tabelle-leer">${esc(TAB.karten.length ? t("tabelle_nichts") : t("karten_leer_unter"))}</td></tr>`}</tbody>`;
}
function setzeTabAnsicht(a) {
  tabAnsicht = a === "kompakt" ? "kompakt" : "bearbeiten";
  try { localStorage.setItem("mgd-tabansicht", tabAnsicht); } catch (e) { /* egal */ }
  const kompakt = tabAnsicht === "kompakt";
  $("#tabelle-rahmen").hidden = kompakt; $("#kompakt-rahmen").hidden = !kompakt;
  $("#tabelle-bilder").closest("label").hidden = kompakt;
  $$('#tabelle-ansicht input').forEach(i => { i.checked = i.value === tabAnsicht; });
  if (kompakt) zeichneKompakt(tabZeilen()); else requestAnimationFrame(() => $$("#tabelle textarea").forEach(passeHoeheAn));
}
$("#tabelle-ansicht").addEventListener("change", e => setzeTabAnsicht(e.target.value));
$("#tabelle-kompakt").addEventListener("click", e => {
  const s = e.target.closest("[data-sort]");
  if (s) { const sp = s.dataset.sort; S.tabSort = S.tabSort && S.tabSort.spalte === sp ? (S.tabSort.ab ? null : { spalte: sp, ab: true }) : { spalte: sp, ab: false }; zeichneTabelle(); return; }
  const tr = e.target.closest("tr[data-k-bild]"); if (!tr) return;     // Klick auf eine Zeile → Bearbeiten an dieser Stelle
  setzeTabAnsicht("bearbeiten");
  const ziel = $(`#tabelle tr[data-bild="${CSS.escape(tr.dataset.kBild)}"]`);
  if (ziel) { ziel.scrollIntoView({ block: "center" }); const f = $('[data-feld="es"]', ziel); if (f) f.focus(); }
});
setzeTabAnsicht(tabAnsicht);
function passeHoeheAn(el) { el.style.height = "auto"; el.style.height = Math.max(38, el.scrollHeight + 2) + "px"; }
$("#tabelle").addEventListener("input", e => { if (e.target.matches("textarea")) passeHoeheAn(e.target); });
window.addEventListener("resize", entprellt(() => { if (ansicht() === "tabelle") $$("#tabelle textarea").forEach(passeHoeheAn); }, 200));
function tabAktualisiereZeile(tr, k) {
  $('[data-teil="hinweise"]', tr).innerHTML = tabHinweiseHTML(k);
  $('[data-teil="status"]', tr).innerHTML = tabStatusHTML(k);
  const es = $('[data-feld="es"]', tr);
  es.classList.toggle("leer", !String(k.es || "").trim()); es.classList.toggle("ist-auto", k.uebersetzung === "auto");
  for (const f of ["de", "es", "notiz"]) { const i = $(`[data-feld="${f}"]`, tr); if (document.activeElement !== i) i.value = k[f] || ""; passeHoeheAn(i); }
  const zahlen = TAB_FILTER.map(f => TAB.karten.filter(x => tabPasst(x, f)).length);
  $$("#tabelle-filter span").forEach((s, i) => { s.textContent = `${t("filter_" + TAB_FILTER[i])} (${zahlen[i]})`; });
}
async function tabSpeichern(tr) {
  const bild = tr.dataset.bild, k = TAB.karten.find(x => x.bild === bild); if (!k) return;
  const es = $('[data-feld="es"]', tr);
  const w = { bild, de: $('[data-feld="de"]', tr).value, es: es.value, notiz: $('[data-feld="notiz"]', tr).value, fit: k.fit, es_auto: es.dataset.auto || "" };
  if (w.de === (k.de || "") && w.es === (k.es || "") && w.notiz === (k.notiz || "") && !w.es_auto) return;
  const meld = $('[data-teil="meldung"]', tr); meld.textContent = ""; meld.className = "zellen-meldung";
  $$(".zelle-eingabe", tr).forEach(i => i.classList.remove("fehler"));
  try {
    const r = await api("/api/karte-speichern", { methode: "POST", daten: w });
    uebernehmeKarten(r.karten); S.v++;
    es.dataset.auto = "";
    TAB = await api("/api/tabelle");
    const neu = TAB.karten.find(x => x.bild === bild); if (neu) tabAktualisiereZeile(tr, neu);
    $$(".zelle-eingabe", tr).forEach(i => { i.classList.add("gespeichert"); setTimeout(() => i.classList.remove("gespeichert"), 900); });
  } catch (e) {
    let text = e.message;
    try { const p = await api("/api/karte-pruefen", { methode: "POST", daten: w }); const f = p.meldungen.filter(m => m.stufe === "fehler"); if (f.length) text = f.map(m => m.text).join(" "); } catch (x) { /* egal */ }
    meld.textContent = text; meld.classList.add("fehler");
    (w.es.trim() ? $('[data-feld="de"]', tr) : es).classList.add("fehler");
  }
}
$("#tabelle").addEventListener("change", e => {
  const tr = e.target.closest("tr[data-bild]"); if (!tr) return;
  if (e.target.matches("[data-geprueft]")) return tabGeprueft(tr, e.target);
  if (e.target.matches(".zelle-eingabe")) tabSpeichern(tr);
});
async function tabGeprueft(tr, haken) {
  try {
    const r = await api("/api/karte-status", { methode: "POST", daten: { bild: tr.dataset.bild, geprueft: haken.checked } });
    uebernehmeKarten(r);
    const k = TAB.karten.find(x => x.bild === tr.dataset.bild); if (k) k.uebersetzung = haken.checked ? "geprueft" : "";
    if (k) tabAktualisiereZeile(tr, k);
  } catch (e) { haken.checked = !haken.checked; fehlerToast(e); }
}
$("#tabelle").addEventListener("keydown", e => {
  if (e.key === "Enter" && e.target.matches(".zelle-eingabe")) { e.preventDefault(); e.target.blur(); }
  if (e.key === "Escape" && e.target.matches(".zelle-eingabe")) {
    const tr = e.target.closest("tr[data-bild]"), k = TAB.karten.find(x => x.bild === tr.dataset.bild);
    if (k) e.target.value = k[e.target.dataset.feld] || ""; e.target.blur();
  }
});
$("#tabelle").addEventListener("click", async e => {
  const s = e.target.closest("[data-sort]");
  if (s) { const sp = s.dataset.sort; S.tabSort = S.tabSort && S.tabSort.spalte === sp ? (S.tabSort.ab ? null : { spalte: sp, ab: true }) : { spalte: sp, ab: false }; zeichneTabelle(); return; }
  const tr = e.target.closest("tr[data-bild]"); if (!tr) return;
  const chip = e.target.closest("[data-chip]");
  if (chip) { const es = $('[data-feld="es"]', tr); es.value = chip.dataset.chip; es.dataset.auto = chip.dataset.chip; return tabSpeichern(tr); }
  const b = e.target.closest('[data-tab-aktion="uebersetzen"]'); if (!b) return;
  b.disabled = true;
  try {
    const v = await holeVorschlag($('[data-feld="de"]', tr).value); if (!v) return;
    S.vorschlaege["t:" + tr.dataset.bild] = v; $('[data-teil="vorschlag"]', tr).innerHTML = vorschlagHTML(v);
    if (v.vorschlag && !$('[data-feld="es"]', tr).value.trim()) {
      const es = $('[data-feld="es"]', tr); es.value = v.vorschlag; es.dataset.auto = v.vorschlag; await tabSpeichern(tr);
    }
  } catch (err) { $('[data-teil="vorschlag"]', tr).innerHTML = vorschlagFehlerHTML(err); }
  finally { b.disabled = false; }
});
$("#tabelle-filter").addEventListener("change", e => { S.tabFilter = e.target.value; zeichneTabelle(); });
$("#tabelle-suche").addEventListener("input", entprellt(e => { S.tabSuche = e.target.value.trim(); zeichneTabelle(); }, 200));
$("#tabelle-bilder").addEventListener("change", zeichneTabelle);
$("#tabelle-drucken").addEventListener("click", () => window.print());
$("#tabelle-uebersetzen").addEventListener("click", async () => {
  const leer = TAB.karten.filter(k => !String(k.es || "").trim() && String(k.de || "").trim());
  await alleUebersetzen($("#tabelle-uebersetzen"), leer.map(k => ({ de: k.de, fuellen: v => {
    if (!v || !v.vorschlag) return false;
    S.vorschlaege["t:" + k.bild] = v;
    const tr = $(`#tabelle tr[data-bild="${CSS.escape(k.bild)}"]`); if (!tr) return false;
    const es = $('[data-feld="es"]', tr); if (es.value.trim()) return false;
    es.value = v.vorschlag; es.dataset.auto = v.vorschlag; $('[data-teil="vorschlag"]', tr).innerHTML = vorschlagHTML(v);
    tabSpeichern(tr); return true;
  } })));
  await ladeTabelle();
});

/* ===================== Bildverbesserung ===================== */
let VERB = null;
async function ladeVerbesserung() {
  if (!VERB) $("#verb-liste").innerHTML = enteHTML();
  ladeTools().then(zeichneVerbTool);
  try { VERB = await api("/api/verbesserung"); } catch (e) { fehlerToast(e); if ($("#verb-liste .ente-laedt")) $("#verb-liste").textContent = e.message; return; }
  zeichneVerbesserung();
}
const KI_KURZ = { "realesrgan-x4plus": "Real-ESRGAN ×4", "realesrgan-x2plus": "Real-ESRGAN ×2", fsrcnn: "FSRCNN", lanczos: "Lanczos" };
function verbInfo(k) {
  const i = k.info; if (!i) return "";
  const name = i.ki === "keine" ? t("verb_ohne_vergr") : KI_KURZ[i.ki] || i.ki || "";
  const teile = [];
  if (k.status === "anders") teile.push(t("verb_frueher", name)); else if (name) teile.push(name);
  if (i.ppi) teile.push(t("marke_ppi", i.ppi, bewertungText(i.bewertung_code)));
  if (i.zeit && k.status === "verbessert") teile.push(datum(i.zeit));
  return teile.join(" · ");
}
function verbKarteHTML(k) {
  const gew = S.verbWahl.has(k.bild);
  const band = { verbessert: "✓ " + t("band_verbessert"), anders: t("band_anders"), offen: t("band_offen"), fehlt: t("band_fehlt") }[k.status] || "";
  return `<article class="verb-karte${gew ? " gewaehlt" : ""}${k.status === "verbessert" ? " ist-verbessert" : ""}" data-bild="${esc(k.bild)}">
    ${k.existiert ? `<label class="wahl" title="${esc(t("verb_waehlen"))}"><input type="checkbox" data-verb-haken${gew ? " checked" : ""} aria-label="${esc(t("verb_waehlen_bild", k.de || k.bild))}"></label>` : ""}
    <button type="button" class="bildflaeche" data-verb-vergleich${k.existiert ? "" : " disabled"} title="${esc(t("verb_vergleich"))}">
      ${k.existiert ? `<img loading="lazy" alt="" data-seite="vorn" data-bild="${esc(k.bild)}" src="${vorschauUrl(k, "vorn")}">` : ""}
      <span class="band ${esc(k.status)}">${esc(band)}</span></button>
    <div class="name">${esc(k.de || k.bild)}</div>
    <div class="info">${k.nr ? esc(t("karte_nr", k.nr)) + " · " : ""}${esc(k.bild)}${k.aktiv ? "" : " · " + esc(t("marke_aus"))}</div>
    ${k.info ? `<div class="info">${esc(verbInfo(k))}</div>` : ""}
  </article>`;
}
function dauerText(s) { return s < 90 ? t("dauer_s", Math.max(1, Math.round(s))) : t("dauer_min", Math.round(s / 60)); }
function zeichneVerbesserung() {
  if (!VERB) return;
  const da = VERB.karten.filter(k => k.existiert), fertig = da.filter(k => k.status === "verbessert").length;
  S.verbWahl = new Set([...S.verbWahl].filter(b => da.some(k => k.bild === b)));
  const q = feldNach("qualitaet"), ql = q ? ((q.auswahl.find(a => a.wert === VERB.qualitaet) || {}).label || VERB.qualitaet) : VERB.qualitaet;
  $("#verb-kopf").innerHTML = `<div><b>${fertig} / ${da.length}</b>${esc(t("verb_fertig"))}</div>
    <div><b>${esc(VERB.methode_name)}</b>${esc(t("verb_methode"))}</div><div><b>${esc(ql)}</b>${esc(t("verb_qualitaet"))}</div>`;
  $("#verb-balken").style.width = (da.length ? Math.round(fertig / da.length * 100) : 0) + "%";
  $("#verb-liste").innerHTML = VERB.karten.length ? VERB.karten.map(verbKarteHTML).join("") : `<div class="flaeche leer" style="grid-column:1/-1"><img src="/symbol.svg" alt="">
    <h2>${esc(t("karten_leer_titel"))}</h2><p>${esc(t("karten_leer_text"))}</p><div class="knopfzeile"><a class="knopf haupt" href="#bild">${esc(t("zu_schritt1"))}</a></div></div>`;
  zeichneVerbAuswahl();
}
function zeichneVerbTool() {                              // Tool fehlt → Kasten mit Nutzen und „Installieren“ (Reiter bleibt nutzbar)
  const el = $("#verb-tool"); if (!el) return;
  const x = toolInfo("bildverbesserung");
  el.hidden = !x || x.installiert; if (el.hidden) return;
  const x2 = (x.teile || []).find(p => p.id === "x2");
  el.innerHTML = `<div class="tool-kopf"><span class="tool-symbol" aria-hidden="true">${esc(x.symbol)}</span><h3>${esc(t("verb_tool_titel"))}</h3>${toolPille(x)}</div>
    <p class="klein">${esc(t("verb_tool_text"))}</p><div class="knopfzeile">${toolBeschaeftigt(x)
      ? `<button class="knopf" type="button" data-ws-oeffnen title="${esc(t("h_ws_knopf"))}">⏳ ${esc(t("ws_titel"))}</button>`
      : `<button class="knopf haupt" data-tool-aktion="installieren" data-tool="bildverbesserung" title="${esc(t("h_tool_installieren"))}">${esc(t("verb_tool_knopf", toolGroesse(x.groesse)))}</button>${x2
        ? `<button class="knopf" data-tool-aktion="installieren" data-tool="bildverbesserung" data-teil="x2" title="${esc(t("h_tool_teil"))}">${esc(t("verb_tool_x2", toolGroesse(x2.groesse)))}</button>` : ""}`}</div>`;
}
function verbBrauchtTool() {                               // KI-Vergrößerung gewünscht (Auto/Real-ESRGAN), aber Tool fehlt
  const x = toolInfo("bildverbesserung"), f = S.gruppen ? feldNach("ki") : null, ki = f ? wert(f) : "auto";
  return !!x && !x.installiert && !["fsrcnn", "aus"].includes(ki) && !!VERB && VERB.qualitaet !== "aus";
}
function zeichneVerbAuswahl() {
  const knopf = $("#verb-start"); if (!knopf || !VERB) return;
  const gew = VERB.karten.filter(k => S.verbWahl.has(k.bild)), zuRechnen = gew.filter(k => k.status !== "verbessert");
  knopf.textContent = t("verb_start", gew.length);
  knopf.disabled = !gew.length;
  const echt = (VERB.methode || "").startsWith("realesrgan") && VERB.qualitaet !== "aus";
  $("#verb-schaetzung").textContent = !gew.length ? t("verb_nichts_gewaehlt")
    : !zuRechnen.length ? t("verb_schon_alle")
    : t("verb_schaetzung", zuRechnen.length, dauerText(zuRechnen.length * VERB.sekunden_je_bild)) + (echt ? " " + t("verb_hinweis_esrgan") : "");
  $$("#verb-liste .verb-karte").forEach(el => { const g = S.verbWahl.has(el.dataset.bild); el.classList.toggle("gewaehlt", g); const h = $("[data-verb-haken]", el); if (h) h.checked = g; });
}
$("#verb-liste").addEventListener("change", e => {
  if (!e.target.matches("[data-verb-haken]")) return;
  const b = e.target.closest(".verb-karte").dataset.bild;
  e.target.checked ? S.verbWahl.add(b) : S.verbWahl.delete(b); zeichneVerbAuswahl();
});
$("#verb-liste").addEventListener("click", e => {
  const b = e.target.closest("[data-verb-vergleich]"); if (!b || !VERB) return;
  const k = VERB.karten.find(x => x.bild === b.closest(".verb-karte").dataset.bild); if (k) zeigeVergleich(k);
});
$$("[data-verb-wahl]").forEach(b => b.addEventListener("click", () => {
  if (!VERB) return;
  const da = VERB.karten.filter(k => k.existiert), w = b.dataset.verbWahl;
  S.verbWahl = new Set(w === "alle" ? da.map(k => k.bild) : w === "offen" ? da.filter(k => k.status !== "verbessert").map(k => k.bild) : []);
  zeichneVerbAuswahl();
}));
async function starteVerbessern(bilder, ohneTool = false) {
  const da = VERB ? VERB.karten.filter(k => k.existiert) : [];
  const alle = bilder.length > 200 && bilder.length === da.length;
  const frage = { alternativ: () => starteVerbessern(bilder, true), alternativText: t("verb_ohne_tool") };
  if (!ohneTool && verbBrauchtTool()) return brauchtTool("bildverbesserung", () => starteVerbessern(bilder), frage);
  try { starteBeobachtung(await api("/api/lauf", { methode: "POST", daten: { art: "verbessern", bilder: alle ? [] : bilder, alle, ohne_tool: ohneTool } })); }
  catch (e) { if (!ohneTool && toolFehlt(e)) return brauchtTool(e.daten.tool, () => starteVerbessern(bilder), frage); fehlerToast(e); }
}
$("#verb-start").addEventListener("click", () => { if (S.verbWahl.size) starteVerbessern([...S.verbWahl]); });
function zeigeVergleich(k) {
  const vorher = url("/api/vergleich", { bild: k.bild, art: "vorher", v: S.v }), nachher = url("/api/vergleich", { bild: k.bild, art: "nachher", v: S.v });
  $("#vergleich-titel").textContent = t("vergleich_titel", k.de || k.bild);
  const name = (k.info && (k.info.ki === "keine" ? t("verb_ohne_vergr") : KI_KURZ[k.info.ki])) || VERB.methode_name;
  $("#vergleich-inhalt").innerHTML = k.status === "verbessert" ? `<div class="vergleich-bild" data-vergleich>
      <img alt="${esc(t("vorher"))}" src="${vorher}"><img class="nachher" alt="${esc(t("nachher"))}" src="${nachher}">
      <span class="linie"></span><span class="etikett links">${esc(t("vorher"))}</span><span class="etikett rechts">${esc(t("nachher_mit", name))}</span></div>
    <input type="range" class="regler" min="0" max="100" value="50" aria-label="${esc(t("vergleich_regler"))}">
    <p class="klein">${esc(t("vergleich_hilfe"))} ${esc(verbInfo(k))}</p>
    <div class="knopfzeile"><a class="knopf klein" href="${nachher}" target="_blank" rel="noopener">${esc(t("in_originalgroesse"))}</a>
      <a class="knopf klein leise" href="${vorher}" target="_blank" rel="noopener">${esc(t("vorher_originalgroesse"))}</a></div>`
    : `<div class="vergleich-bild"><img alt="${esc(t("vorher"))}" src="${vorher}"><span class="etikett links">${esc(t("vorher"))}</span></div>
    <p>${esc(k.status === "anders" ? t("vergleich_anders", verbInfo(k)) : t("vergleich_fehlt"))}</p>
    <div class="knopfzeile"><button class="knopf haupt" data-verb-eins="${esc(k.bild)}">${esc(t("jetzt_verbessern"))}</button></div>`;
  $("#vergleich-fenster").hidden = false; $("#vergleich-fenster [data-schliessen]").focus();
}
function setzeVergleich(wert) {
  const v = Math.max(0, Math.min(100, wert)), box = $("[data-vergleich]"); if (!box) return;
  $(".nachher", box).style.clipPath = `inset(0 0 0 ${v}%)`; $(".linie", box).style.left = v + "%";
  const r = $("#vergleich-inhalt .regler"); if (r && +r.value !== Math.round(v)) r.value = Math.round(v);
}
$("#vergleich-inhalt").addEventListener("input", e => { if (e.target.matches(".regler")) setzeVergleich(+e.target.value); });
$("#vergleich-inhalt").addEventListener("pointerdown", e => {
  const box = e.target.closest("[data-vergleich]"); if (!box) return;
  const bewege = ev => { const r = box.getBoundingClientRect(); setzeVergleich((ev.clientX - r.left) / r.width * 100); };
  bewege(e); box.setPointerCapture(e.pointerId);
  const auf = () => { box.removeEventListener("pointermove", bewege); box.removeEventListener("pointerup", auf); };
  box.addEventListener("pointermove", bewege); box.addEventListener("pointerup", auf);
});
$("#vergleich-inhalt").addEventListener("click", e => {
  const b = e.target.closest("[data-verb-eins]"); if (!b) return;
  $("#vergleich-fenster").hidden = true; S.verbWahl.add(b.dataset.verbEins); zeichneVerbAuswahl(); starteVerbessern([b.dataset.verbEins]);
});
document.addEventListener("click", e => {
  if (e.target.closest("[data-schliessen]") || e.target.id === "vergleich-fenster") $("#vergleich-fenster").hidden = true;
});
document.addEventListener("keydown", e => {
  if (e.key !== "Escape") return;
  if (!$("#vergleich-fenster").hidden) $("#vergleich-fenster").hidden = true;
  if (!$("#zustimmung").hidden && zustimmungFertig) zustimmungFertig(false);
});

/* ===================== Farben & Darstellung ===================== */
// Schemata + eigene Farben. Der Server liefert die Variablen schon mit der Seite (kein Aufblitzen); das Fenster zeigt
// Änderungen sofort als Vorschau (POST /api/farben mit speichern:false) und merkt sie erst mit „Speichern“.
let FARB = null, FARB_STAND = null, farbZeit = 0;
const FARB_BASIS = ["hintergrund", "flaechen", "text", "akzent", "linien", "erfolg", "fehler"];
function farbenAnwenden(info) {
  const st = document.getElementById("farben-vars"); if (st) st.textContent = info.css || "";
  document.querySelectorAll('meta[name="theme-color"]').forEach(m => m.remove());
  document.head.insertAdjacentHTML("beforeend", info.meta || "");
}
const farbGleich = (a, b) => !!a && !!b && a.schema === b.schema && FARB_BASIS.every(k => a.eigene[k] === b.eigene[k]);
function farbenKontrast(info) {
  const schwach = info.kontrast.filter(k => !k.ok).sort((a, b) => a.wert - b.wert)[0];
  const w = zahl((schwach || info.kontrast[0]).wert);
  return `<div class="farb-pruefung${schwach ? " schwach" : ""}" role="status">${esc(schwach ? t("fa_schwer", w) : t("fa_lesbar", w))}</div>`;
}
function zeichneFarben() {
  const f = FARB; if (!f) return;
  const kacheln = f.schemata.map(s => `<button type="button" class="farb-kachel" data-farb-schema="${esc(s.id)}" aria-pressed="${f.schema === s.id}"
      title="${esc(t("h_farben_kachel"))}"><span class="farb-vorschau" aria-hidden="true">${s.farben.map(c => `<i style="background:${esc(c)}"></i>`).join("")}</span>
      <b>${esc(t("fa_" + s.id))}</b></button>`).join("");
  const eigene = f.schema === "eigen" ? `<p class="klein">${esc(t("fa_eigen_hinweis"))}</p><div class="farb-eigene">${FARB_BASIS.map(k =>
    `<label><input type="color" data-farb-eigen="${k}" value="${esc(f.eigene[k].toLowerCase())}"><span>${esc(t("fa_c_" + k))}</span></label>`).join("")}</div>` : "";
  const neuStand = !farbGleich(f, FARB_STAND);
  $("#farben-inhalt").innerHTML = `<p class="unter">${esc(t("fa_unter"))}</p><div class="farb-raster">${kacheln}</div>${eigene}
    <div id="farb-pruefung">${farbenKontrast(f)}</div>
    <div class="knopfzeile abstand"><span class="klein" id="farb-ungespeichert"${neuStand ? "" : " hidden"}>${esc(t("fa_ungespeichert"))}</span>
      <div class="rechts"><button type="button" class="knopf leise" data-farb-aktion="standard" title="${esc(t("h_farben_standard"))}">${esc(t("fa_standard"))}</button>
      <button type="button" class="knopf haupt" data-farb-aktion="speichern" title="${esc(t("h_farben_speichern"))}">${esc(t("fa_speichern"))}</button></div></div>`;
}
async function farbenVorschau() {
  const f = FARB; if (!f) return;
  try {
    const r = await api("/api/farben", { methode: "POST", daten: { schema: f.schema, eigene: f.eigene, speichern: false } });
    if (FARB !== f) return;
    f.css = r.css; f.meta = r.meta; f.kontrast = r.kontrast; f.schemata = r.schemata;
    farbenAnwenden(r);
    const p = $("#farb-pruefung"); if (p) p.innerHTML = farbenKontrast(r);
    const u = $("#farb-ungespeichert"); if (u) u.hidden = farbGleich(f, FARB_STAND);
  } catch (err) { fehlerToast(err); }
}
async function oeffneFarben() {
  try { FARB = await api("/api/farben"); } catch (e) { fehlerToast(e); return; }
  FARB_STAND = JSON.parse(JSON.stringify(FARB));
  zeichneFarben(); $("#farben-fenster").hidden = false;
}
function farbenVerwerfen() {                              // Fenster zu ohne „Speichern“ → zurück zum gespeicherten Stand
  if (FARB && FARB_STAND && !farbGleich(FARB, FARB_STAND)) farbenAnwenden(FARB_STAND);
  FARB = FARB_STAND = null;
}
$("#farben-inhalt").addEventListener("click", async e => {
  const k = e.target.closest("[data-farb-schema]");
  if (k && FARB) { FARB.schema = k.dataset.farbSchema; await farbenVorschau(); zeichneFarben(); return; }
  const a = e.target.closest("[data-farb-aktion]"); if (!a || !FARB) return;
  try {
    if (a.dataset.farbAktion === "speichern") {
      const r = await api("/api/farben", { methode: "POST", daten: { schema: FARB.schema, eigene: FARB.eigene } });
      FARB = r; FARB_STAND = JSON.parse(JSON.stringify(r)); farbenAnwenden(r); zeichneFarben(); toast(t("fa_gespeichert"));
    } else {
      const r = await api("/api/farben", { methode: "POST", daten: { zuruecksetzen: true } });
      FARB = r; FARB_STAND = JSON.parse(JSON.stringify(r)); farbenAnwenden(r); zeichneFarben(); toast(t("fa_zurueck"));
    }
  } catch (err) { fehlerToast(err); }
});
$("#farben-inhalt").addEventListener("input", e => {
  const c = e.target.closest("[data-farb-eigen]"); if (!c || !FARB) return;
  FARB.eigene[c.dataset.farbEigen] = c.value.toUpperCase();
  clearTimeout(farbZeit); farbZeit = setTimeout(farbenVorschau, 120);
});

/* ===================== Beenden ===================== */
$("#beenden").addEventListener("click", async () => {
  await ladeWs();
  if (S.ws.aktiv || S.ws.wartend.length) { oeffneWs(true); return; }    // erst nachfragen: Die Gänse stehen noch Schlange
  beendenJetzt();
});

/* ===================== Erweiterungen: Fenster (Pop-ups) ===================== */
// Import/Export, GANS-Werkzeug, Programmstart und Deinstallieren öffnen sich als Fenster über der Seite – die
// Ansichten bleiben übersichtlich. Server-Seite: erweiterungen.py (fehlt sie, antworten die Adressen mit 404).
function offenerDialog() { return $$("[data-dialogfenster]").filter(x => !x.hidden).pop() || null; }
function oeffneDialog(name, opt = {}) {
  if (name === "import-export") return oeffneImportExport(opt.vorwahl);
  if (name === "gans-werkzeug") return oeffneGansWerkzeug(opt);
  if (name === "ki-bild") return oeffneKiBild(opt);
  if (name === "programmstart") return oeffneStartWahl();
  if (name === "handy") return oeffneHandy();
  if (name === "farben") return oeffneFarben();
  if (name === "deinstallieren") return oeffneDeinstallieren();
}
function schliesseDialog(el) {
  if (!el) return;
  el.hidden = true;
  if (el.id === "gw-fenster") gwAufraeumen();
  if (el.id === "ki-fenster") KI = null;
  if (el.id === "ie-fenster") ieVerwerfen();
  if (el.id === "farben-fenster") farbenVerwerfen();
  if (el.id === "tool-fenster") { if (TOOL_DLG && TOOL_DLG.art === "erst") toolsErstabfrageSenden([]); TOOL_DLG = null; }   // zu = „Später“
}
document.addEventListener("click", e => {
  const d = e.target.closest("[data-dialog]"); if (d) { e.preventDefault(); oeffneDialog(d.dataset.dialog, { vorwahl: d.dataset.vorwahl }); return; }
  const zu = e.target.closest("[data-zu]"); if (zu) { schliesseDialog(zu.closest("[data-dialogfenster]")); return; }
  if (e.target.matches("[data-dialogfenster]") && !e.target.hasAttribute("data-fest")) schliesseDialog(e.target);
});
document.addEventListener("keydown", e => {
  if (e.key !== "Escape") return;
  const d = offenerDialog(); if (d && !d.hasAttribute("data-fest")) schliesseDialog(d);
});
// Dateien ziehen: in einem offenen Fenster bzw. auf eine Ideen-Karte gehen sie an dieses Ziel (nicht an Schritt 1)
const ZIEH_ZIELE = {};
["dragenter", "dragover", "dragleave", "drop"].forEach(typ => window.addEventListener(typ, e => {
  const zone = e.target && e.target.closest ? e.target.closest("[data-zieh]") : null;
  if (!offenerDialog() && !zone) return;                       // sonst wie bisher (Schritt 1 / Gänse-Bild)
  e.preventDefault(); e.stopPropagation();
  $$("[data-zieh]").forEach(z => z.classList.toggle("drueber", (typ === "dragenter" || typ === "dragover") && z === zone));
  if (typ === "drop" && zone && e.dataTransfer.files.length && ZIEH_ZIELE[zone.dataset.zieh]) ZIEH_ZIELE[zone.dataset.zieh](e.dataTransfer.files, zone);
}, true));
function dateiWaehlen(accept, fn) {                             // unsichtbares Dateifeld nur für diesen Klick
  const i = document.createElement("input"); i.type = "file"; i.accept = accept; i.hidden = true;
  i.addEventListener("change", () => { if (i.files.length) fn(i.files); i.remove(); });
  document.body.append(i); i.click();
}

/* ----- Karten und Ideen importieren / exportieren ----- */
let IE = null, ieStatus = "", ieInhalt = "karten", ieUmfang = "alle", ieEntscheid = {};
function oeffneImportExport(vorwahl) {
  IE = null; ieStatus = ""; ieEntscheid = {};
  if (["karten", "ideen", "alles"].includes(vorwahl)) ieInhalt = vorwahl;
  zeichneIE(); $("#ie-fenster").hidden = false;
}
function ieVerwerfen() {
  if (IE && IE.id) api("/api/import-verwerfen", { methode: "POST", daten: { id: IE.id } }).catch(() => {});
  IE = null;
}
function ieErsetzen(e) { return ieEntscheid[e.schluessel] === true; }
function ieAnzahlNehmen() {
  if (!IE) return 0;
  return [...IE.karten, ...IE.ideen].filter(e => e.status === "neu" || (e.status === "konflikt" && ieErsetzen(e))).length;
}
function ieZeileHTML(e) {
  const titel = e.art === "karte" ? e.bild : (e.de || e.es || t("idee_ohne_text"));
  const unter = e.art === "karte" ? `${e.de}${e.es ? " → " + e.es : ""}` : [e.de, e.es].filter(Boolean).join(" → ");
  let wahl = "";
  if (e.status === "konflikt") {
    const nur_dazu = e.art === "idee" && !e.ziel;                      // Wort gibt es als Karte: Idee käme zusätzlich
    wahl = `<div class="segmente klein-seg" role="radiogroup" aria-label="${esc(t("ie_entscheid"))}">
      <label title="${esc(t("ie_behalten_titel"))}"><input type="radio" name="ie-${esc(e.schluessel)}" value="0" data-ie-schluessel="${esc(e.schluessel)}"${ieErsetzen(e) ? "" : " checked"}><span>${esc(t("ie_behalten_kurz"))}</span></label>
      <label title="${esc(nur_dazu ? t("ie_dazu_titel") : t("ie_ersetzen_titel"))}"><input type="radio" name="ie-${esc(e.schluessel)}" value="1" data-ie-schluessel="${esc(e.schluessel)}"${ieErsetzen(e) ? " checked" : ""}><span>${esc(nur_dazu ? t("ie_dazu_kurz") : t("ie_ersetzen_kurz"))}</span></label></div>`;
  }
  const hier = e.hier && e.status === "konflikt" ? `<div class="klein">${esc(t("ie_hier"))} ${esc([e.hier.de, e.hier.es].filter(Boolean).join(" → "))}</div>` : "";
  return `<tr class="ie-${esc(e.status)}"><td><b>${esc(titel)}</b><div class="klein">${esc(unter)}</div></td>
    <td><span class="chip-s ${esc(e.status)}">${esc(t("ie_s_" + e.status))}</span>${["konflikt", "fehler"].includes(e.status) ? `<div class="klein">${esc(e.text)}</div>` : ""}${hier}${wahl}</td></tr>`;
}
function ieTabelleHTML(titel, liste, zahlen) {
  if (!liste.length) return "";
  return `<h4 class="ie-abschnitt">${esc(titel)} <span class="klein">${esc(t("ie_vorschau", zahlen))}</span></h4>
    <div class="ie-rollen"><table class="ie-tabelle"><tbody>${liste.map(ieZeileHTML).join("")}</tbody></table></div>`;
}
function zeichneIE() {
  const alle = S.karten.length, aktiv = S.karten.filter(k => k.aktiv).length, ideen = IDEEN ? IDEEN.ideen.length : 0;
  let imp;
  if (ieStatus === "pruefe") imp = enteHTML(t("ie_pruefe"));
  else if (!IE) imp = `<div class="ziehfeld" data-zieh="import" data-ie-aktion="waehlen" role="button" tabindex="0" title="${esc(t("ie_waehlen_titel"))}">
      <b>${esc(t("ie_waehlen"))}</b><span class="klein">${esc(t("ie_import_text"))}</span></div>`;
  else {
    const konflikte = [...IE.karten, ...IE.ideen].filter(e => e.status === "konflikt").length, nehmen = ieAnzahlNehmen();
    imp = `${konflikte ? `<div class="hinweisbox warn" role="alert"><b>${esc(t("ie_warnung_titel", konflikte))}</b><p>${esc(t("ie_warnung_text"))}</p>
        <div class="knopfzeile"><button class="knopf klein" data-ie-aktion="alle-behalten">${esc(t("ie_alle_behalten"))}</button>
        <button class="knopf klein" data-ie-aktion="alle-ersetzen">${esc(t("ie_alle_ersetzen"))}</button></div></div>` : ""}
      ${ieTabelleHTML(t("ie_karten"), IE.karten, IE.zahlen_karten)}${ieTabelleHTML(t("ie_ideen"), IE.ideen, IE.zahlen_ideen)}
      <div class="knopfzeile abstand"><button class="knopf leise" data-ie-aktion="andere">${esc(t("ie_andere"))}</button>
        <div class="rechts">${nehmen ? `<button class="knopf haupt" data-ie-aktion="uebernehmen">${esc(t("ie_uebernehmen", nehmen))}</button>` : `<span class="klein">${esc(t("ie_nichts"))}</span>`}</div></div>`;
  }
  const wahl = (name, wert, akt, titel, text) => `<label class="dienst"><input type="radio" name="${name}" value="${wert}"${wert === akt ? " checked" : ""}><span><b>${esc(titel)}</b>${text ? `<span class="klein">${esc(text)}</span>` : ""}</span></label>`;
  $("#ie-inhalt").innerHTML = `<div class="ie-spalten">
    <section><h3>${esc(t("ie_export_titel"))}</h3><p class="klein">${esc(t("ie_export_text"))}</p>
      <div class="wahl-liste" role="radiogroup" aria-label="${esc(t("ie_was"))}">
        ${wahl("ie-inhalt", "karten", ieInhalt, t("ie_nur_karten", alle), "")}
        ${wahl("ie-inhalt", "ideen", ieInhalt, t("ie_nur_ideen", ideen), "")}
        ${wahl("ie-inhalt", "alles", ieInhalt, t("ie_alles"), t("ie_alles_text"))}</div>
      <label class="schalter" ${ieInhalt === "ideen" ? "hidden" : ""} title="${esc(t("ie_aktiv_titel"))}"><input type="checkbox" id="ie-nur-aktiv"${ieUmfang === "aktiv" ? " checked" : ""}><span class="spur"></span><span>${esc(t("ie_aktiv", aktiv))}</span></label>
      <div class="abstand"><a class="knopf haupt" id="ie-export" href="${url("/api/export", { inhalt: ieInhalt, umfang: ieUmfang })}" download>${esc(t("ie_export_knopf"))}</a></div></section>
    <section><h3>${esc(t("ie_import_titel"))}</h3>${imp}</section></div>`;
}
async function ieDatei(dateien) {
  const f = dateien[0]; if (!f) return;
  ieVerwerfen(); ieEntscheid = {}; ieStatus = "pruefe"; zeichneIE();
  try { IE = await api("/api/import", { methode: "POST", roh: f }); }
  catch (e) { fehlerToast(e); IE = null; }
  ieStatus = ""; zeichneIE();
}
ZIEH_ZIELE.import = ieDatei;
$("#ie-inhalt").addEventListener("change", e => {
  if (e.target.name === "ie-inhalt") { ieInhalt = e.target.value; zeichneIE(); }
  if (e.target.id === "ie-nur-aktiv") { ieUmfang = e.target.checked ? "aktiv" : "alle"; $("#ie-export").href = url("/api/export", { inhalt: ieInhalt, umfang: ieUmfang }); }
  if (e.target.dataset.ieSchluessel) { ieEntscheid[e.target.dataset.ieSchluessel] = e.target.value === "1"; zeichneIE(); }
});
$("#ie-inhalt").addEventListener("keydown", e => { if (e.key === "Enter" && e.target.matches('[data-ie-aktion="waehlen"]')) e.target.click(); });
$("#ie-inhalt").addEventListener("click", async e => {
  const b = e.target.closest("[data-ie-aktion]"); if (!b) return;
  const a = b.dataset.ieAktion;
  if (a === "waehlen") dateiWaehlen(".zip,.csv,.json,application/zip,text/csv,application/json", ieDatei);
  if (a === "andere") { ieVerwerfen(); zeichneIE(); }
  if (a === "alle-behalten" || a === "alle-ersetzen") {
    [...IE.karten, ...IE.ideen].filter(x => x.status === "konflikt").forEach(x => { ieEntscheid[x.schluessel] = a === "alle-ersetzen"; });
    zeichneIE();
  }
  if (a === "uebernehmen") {
    b.disabled = true;
    try {
      const r = await api("/api/import-uebernehmen", { methode: "POST", daten: { id: IE.id, ersetzen: { standard: false, ...ieEntscheid } } });
      IE = null; uebernehmeKarten(r.karten); IDEEN = r; zaehler(); S.v++;
      $("#ie-fenster").hidden = true; toast(t("ie_fertig", r.zahlen) + (r.zahlen.lernstand ? " " + t("ie_lernstand", r.zahlen.lernstand) : ""));
      if (r.zahlen.lernstand) lernSpaeter();
      zeige();
    } catch (err) { fehlerToast(err); b.disabled = false; }
  }
});

/* ----- GANS-Werkzeug: Foto zuschneiden, „GANS + Wort“ daraufsetzen ----- */
const GW_SCHRIFTEN = {
  poppins: { w: 700, f: "Poppins, sans-serif" }, poppins_m: { w: 500, f: "Poppins, sans-serif" },
  impact: { w: 400, f: "Impact, 'Arial Black', sans-serif" }, arial: { w: 900, f: "'Arial Black', Arial, sans-serif" },
  comic: { w: 700, f: "'Comic Sans MS', 'Comic Neue', cursive" }, georgia: { w: 700, f: "Georgia, 'Times New Roman', serif" },
};
const GW_FARBEN = { weiss: ["#FFFFFF", "#111111"], schwarz: ["#111111", "#FFFFFF"], gelb: ["#FFD43B", "#111111"] };
const GW_FORMATE = { quadrat: [1, 1], karte: [88, 63], hoch: [63, 88] };
let GW = null;
function gwNeu(opt) {
  return { bild: null, blobUrl: "", format: GW_FORMATE[opt.format] ? opt.format : "quadrat", zoom: 1, cx: 0, cy: 0, text: opt.text || "", tx: .5, ty: .84, groesse: .13,
    schrift: "poppins", farbe: "weiss", idee: opt.idee || null, karte: opt.karte || "", ziehen: null };
}
function gwAufraeumen() { if (GW && GW.blobUrl) URL.revokeObjectURL(GW.blobUrl); GW = null; }
function oeffneGansWerkzeug(opt = {}) {
  gwAufraeumen(); GW = gwNeu(opt);
  zeichneGwFenster(); $("#gw-fenster").hidden = false;
}
function gwRest() { return GW.text.replace(/^\s*gans\b[\s,:–-]*/i, "").replace(/\s+/g, " ").trim(); }
function gwDeText() { const r = gwRest(); return "Gans " + (r === r.toUpperCase() ? r.toLowerCase() : r); }
function gwDateiname() {
  const s = gwDeText().toLowerCase().replace(/ä/g, "ae").replace(/ö/g, "oe").replace(/ü/g, "ue").replace(/ß/g, "ss")
    .normalize("NFKD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
  return (s || "gans") + ".jpg";
}
function zeichneGwFenster() {
  const opt = (obj, wert, pre) => Object.keys(obj).map(k => `<option value="${k}"${k === wert ? " selected" : ""}>${esc(t(pre + k))}</option>`).join("");
  if (!GW.bild) {
    $("#gw-inhalt").innerHTML = `<div class="ziehfeld" data-zieh="gw" data-gw-aktion="waehlen" role="button" tabindex="0" style="padding:48px 12px">
      <img src="/symbol.svg" alt="" style="width:64px;height:64px"><b>${esc(t("gw_leer"))}</b><span class="klein">${esc(t("gw_leer_unter"))}</span></div>`;
    return;
  }
  $("#gw-inhalt").innerHTML = `<div class="gw-raster">
    <div><div class="gw-buehne"><canvas id="gw-canvas" aria-label="${esc(t("gw_titel"))}"></canvas></div>
      <p class="klein" style="margin:6px 0 0">${esc(t("gw_hilfe"))}</p></div>
    <div class="gw-steuer">
      <div><label class="titel" for="gw-text">${esc(t("gw_text"))}</label>
        <div class="gw-text"><b>GANS</b><input id="gw-text" autocomplete="off" spellcheck="false" maxlength="40" placeholder="${esc(t("gw_text_ph"))}" value="${esc(gwRest())}"></div>
        <div class="klein" id="gw-datei" style="margin-top:4px"></div></div>
      <div><span class="titel" style="font-size:13px;font-weight:700">${esc(t("gw_format"))}</span>
        <div class="segmente" role="radiogroup">${Object.keys(GW_FORMATE).map(k => `<label><input type="radio" name="gw-format" value="${k}"${k === GW.format ? " checked" : ""}><span>${esc(t("gw_" + k))}</span></label>`).join("")}</div></div>
      <div><label class="titel" for="gw-zoom">${esc(t("gw_zoom"))}</label><input type="range" id="gw-zoom" min="100" max="500" value="${Math.round(GW.zoom * 100)}"></div>
      <div><label class="titel" for="gw-groesse">${esc(t("gw_groesse"))}</label><input type="range" id="gw-groesse" min="5" max="30" value="${Math.round(GW.groesse * 100)}"></div>
      <div><label class="titel" for="gw-schrift">${esc(t("gw_schrift"))}</label><select class="eingabe" id="gw-schrift">${opt(GW_SCHRIFTEN, GW.schrift, "gw_s_")}</select></div>
      <div><label class="titel" for="gw-farbe">${esc(t("gw_farbe"))}</label><select class="eingabe" id="gw-farbe">${opt(GW_FARBEN, GW.farbe, "gw_")}</select></div>
      <div class="knopfzeile"><button class="knopf klein leise" data-gw-aktion="mitte">${esc(t("gw_mitte"))}</button>
        <button class="knopf klein leise" data-gw-aktion="waehlen">${esc(t("gw_anderes"))}</button></div>
      <div class="knopfzeile">${GW.karte ? `<button class="knopf haupt" data-gw-aktion="fuer-karte">${esc(t("ki_fuer_karte"))}</button>`
        : GW.idee ? `<button class="knopf haupt" data-gw-aktion="idee">${esc(t("gw_fuer_idee"))}</button>`
        : `<button class="knopf haupt" data-gw-aktion="karte">${esc(t("gw_als_karte"))}</button><button class="knopf" data-gw-aktion="idee">${esc(t("gw_als_idee"))}</button>`}
        <button class="knopf leise" data-gw-aktion="laden">${esc(t("gw_herunterladen"))}</button></div>
    </div></div>`;
  gwCanvasEinrichten(); gwMalen();
}
function gwMasse() {                                                     // Anzeigegröße des Ausschnitts
  const [a, b] = GW_FORMATE[GW.format], W = 960, H = Math.round(W * b / a);
  return { W, H, s: Math.max(W / GW.bild.naturalWidth, H / GW.bild.naturalHeight) * GW.zoom };
}
function gwBegrenzen() {
  const { W, H, s } = gwMasse(), iw = GW.bild.naturalWidth, ih = GW.bild.naturalHeight;
  GW.cx = Math.min(iw - W / 2 / s, Math.max(W / 2 / s, GW.cx)); GW.cy = Math.min(ih - H / 2 / s, Math.max(H / 2 / s, GW.cy));
}
function gwTextZeichnen(c, W, H) {
  const rest = gwRest(); if (!rest) return null;
  const text = ("GANS " + rest).toUpperCase(), sch = GW_SCHRIFTEN[GW.schrift], [fuell, rand] = GW_FARBEN[GW.farbe];
  let g = GW.groesse * H;
  c.font = `${sch.w} ${g}px ${sch.f}`;
  const breite = c.measureText(text).width; if (breite > W * .96) { g *= W * .96 / breite; c.font = `${sch.w} ${g}px ${sch.f}`; }
  const x = GW.tx * W, y = GW.ty * H, w = c.measureText(text).width;
  c.textAlign = "center"; c.textBaseline = "middle"; c.lineJoin = "round"; c.miterLimit = 2;
  c.lineWidth = Math.max(2, g * .16); c.strokeStyle = rand; c.strokeText(text, x, y);
  c.fillStyle = fuell; c.fillText(text, x, y);
  return { x: x - w / 2, y: y - g * .6, w, h: g * 1.2 };
}
function gwBild(c, W, H, s) {
  c.imageSmoothingEnabled = true; c.imageSmoothingQuality = "high";
  c.drawImage(GW.bild, W / 2 - GW.cx * s, H / 2 - GW.cy * s, GW.bild.naturalWidth * s, GW.bild.naturalHeight * s);
}
function gwMalen() {
  const cv = $("#gw-canvas"); if (!cv || !GW || !GW.bild) return;
  const { W, H, s } = gwMasse();
  if (cv.width !== W || cv.height !== H) { cv.width = W; cv.height = H; }
  const c = cv.getContext("2d"); c.clearRect(0, 0, W, H);
  gwBild(c, W, H, s);
  GW.box = gwTextZeichnen(c, W, H);
  $("#gw-datei").textContent = gwRest() ? t("gw_datei", gwDateiname()) : "";
}
function gwCanvasEinrichten() {
  const cv = $("#gw-canvas");
  const punkt = e => { const r = cv.getBoundingClientRect(); return [(e.clientX - r.left) * cv.width / r.width, (e.clientY - r.top) * cv.height / r.height]; };
  cv.addEventListener("pointerdown", e => {
    const [x, y] = punkt(e), b = GW.box, rand = 12;
    const aufText = b && x >= b.x - rand && x <= b.x + b.w + rand && y >= b.y - rand && y <= b.y + b.h + rand;
    GW.ziehen = { art: aufText ? "text" : "bild", x, y }; cv.setPointerCapture(e.pointerId); cv.classList.add("zieht");
  });
  cv.addEventListener("pointermove", e => {
    if (!GW || !GW.ziehen) return;
    const [x, y] = punkt(e), dx = x - GW.ziehen.x, dy = y - GW.ziehen.y, { W, H, s } = gwMasse();
    if (GW.ziehen.art === "text") { GW.tx = Math.min(.97, Math.max(.03, GW.tx + dx / W)); GW.ty = Math.min(.97, Math.max(.03, GW.ty + dy / H)); }
    else { GW.cx -= dx / s; GW.cy -= dy / s; gwBegrenzen(); }
    GW.ziehen.x = x; GW.ziehen.y = y; gwMalen();
  });
  const los = () => { if (GW) GW.ziehen = null; cv.classList.remove("zieht"); };
  cv.addEventListener("pointerup", los); cv.addEventListener("pointercancel", los);
  cv.addEventListener("wheel", e => {
    e.preventDefault(); GW.zoom = Math.min(5, Math.max(1, GW.zoom * (e.deltaY < 0 ? 1.08 : 1 / 1.08)));
    gwBegrenzen(); $("#gw-zoom").value = Math.round(GW.zoom * 100); gwMalen();
  }, { passive: false });
}
async function gwFoto(dateien) {
  const f = dateien[0]; if (!f || !GW) return;
  if (f.size > MAX_MB * 1048576) return toast(t("zu_gross", f.name, MAX_MB), { fehler: true });
  const urlNeu = URL.createObjectURL(f), img = new Image();
  try { await new Promise((ok, nein) => { img.onload = ok; img.onerror = nein; img.src = urlNeu; }); }
  catch (e) { URL.revokeObjectURL(urlNeu); return toast(t("gw_leer_unter"), { fehler: true }); }
  if (GW.blobUrl) URL.revokeObjectURL(GW.blobUrl);
  GW.bild = img; GW.blobUrl = urlNeu; GW.zoom = 1; GW.cx = img.naturalWidth / 2; GW.cy = img.naturalHeight / 2;
  try { await document.fonts.load(`700 40px Poppins`); await document.fonts.load(`500 40px Poppins`); } catch (e) { /* Ersatzschrift */ }
  zeichneGwFenster(); const feld = $("#gw-text"); if (feld && !feld.value) feld.focus();
}
ZIEH_ZIELE.gw = gwFoto;
function gwErgebnis() {                                                   // fertiges JPEG in Ausgabegröße
  return new Promise(ok => {
    const { W, H, s } = gwMasse(), quelleBreite = W / s;                    // Breite des Ausschnitts in Original-Pixeln
    const f = Math.min(2400 / Math.max(W, H), Math.max(1200 / Math.max(W, H), quelleBreite / W));
    const cv = document.createElement("canvas"); cv.width = Math.round(W * f); cv.height = Math.round(H * f);
    const c = cv.getContext("2d"); c.scale(f, f); gwBild(c, W, H, s); gwTextZeichnen(c, W, H);
    cv.toBlob(b => ok(b), "image/jpeg", .93);
  });
}
$("#gw-inhalt").addEventListener("input", e => {
  if (!GW) return;
  if (e.target.id === "gw-text") GW.text = e.target.value;
  if (e.target.id === "gw-zoom") { GW.zoom = e.target.value / 100; gwBegrenzen(); }
  if (e.target.id === "gw-groesse") GW.groesse = e.target.value / 100;
  gwMalen();
});
$("#gw-inhalt").addEventListener("change", async e => {
  if (!GW) return;
  if (e.target.name === "gw-format") { GW.format = e.target.value; gwBegrenzen(); gwMalen(); }
  if (e.target.id === "gw-schrift") { GW.schrift = e.target.value; const s = GW_SCHRIFTEN[GW.schrift];
    try { await document.fonts.load(`${s.w} 40px ${s.f}`); } catch (err) { /* Ersatzschrift */ } gwMalen(); }
  if (e.target.id === "gw-farbe") { GW.farbe = e.target.value; gwMalen(); }
});
$("#gw-inhalt").addEventListener("keydown", e => { if (e.key === "Enter" && e.target.matches('[data-gw-aktion="waehlen"]')) e.target.click(); });
$("#gw-inhalt").addEventListener("click", async e => {
  const b = e.target.closest("[data-gw-aktion]"); if (!b || !GW) return;
  const a = b.dataset.gwAktion;
  if (a === "waehlen") return dateiWaehlen(BILD_ACCEPT_WEB, gwFoto);
  if (a === "mitte") { GW.tx = .5; return gwMalen(); }
  if (!gwRest()) { toast(t("gw_text_fehlt"), { fehler: true }); const f = $("#gw-text"); if (f) f.focus(); return; }
  b.disabled = true;
  try {
    const blob = await gwErgebnis();
    if (a === "laden") {
      const u = URL.createObjectURL(blob), l = document.createElement("a"); l.href = u; l.download = gwDateiname();
      document.body.append(l); l.click(); l.remove(); setTimeout(() => URL.revokeObjectURL(u), 4000);
    }
    if (a === "karte") {
      await api(url("/api/entwurf", { name: gwDeText() + ".jpg" }), { methode: "POST", roh: blob });
      await ladeEntwuerfe(); schliesseDialog($("#gw-fenster")); location.hash = "#bild"; zeige(); toast(t("gw_ok_karte"));
    }
    if (a === "fuer-karte") {                              // Bild für eine vorhandene Karte → Karten-Editor (wie „Bild ändern“)
      const karte = GW.karte, f = new File([blob], gwDateiname(), { type: "image/jpeg" });
      schliesseDialog($("#gw-fenster")); oeffneEditor(karte); await ladeErsatz(karte, f); toast(t("ki_ok_editor"));
    }
    if (a === "idee") {
      const ziel = GW.idee, alt = ziel && IDEEN ? IDEEN.ideen.find(i => i.id === ziel) : null;
      let r = await api(url("/api/idee-bild", { id: ziel || "" }), { methode: "POST", roh: blob });
      if (!alt || !alt.de) r = await api("/api/idee", { methode: "POST", daten: { id: r.id, de: gwDeText(), es: alt ? alt.es : "", notiz: alt ? alt.notiz : "" } });
      IDEEN = r; zaehler(); schliesseDialog($("#gw-fenster"));
      if (ansicht() === "ideen") zeichneIdeen(); else { location.hash = "#ideen"; }
      toast(t("gw_ok_idee"));
    }
  } catch (err) { fehlerToast(err); }
  finally { b.disabled = false; }
});

/* ----- KI-Bild: realistische Gans aus Wort + Beschreibung (ki_bild.py, offline auf diesem Rechner) ----- */
let KI = null;                                                     // offenes Fenster „Gans mit KI erzeugen“
const KI_MERK = { letzt: null, stopp: false };                     // letztes Ergebnis; Abbrechen geklickt?
function kiLauf() { return S.lauf && S.lauf.art === "ki-bild" ? S.lauf : null; }
function kiWartet() { return KI && KI.wartet ? S.ws.wartend.find(x => x.id === KI.wartet) || null : null; }
function kiMerken(k, v) { try { localStorage.setItem("mgd-ki-" + k, v); } catch (e) { /* nur Bequemlichkeit */ } }
function kiGemerkt(k) { try { return localStorage.getItem("mgd-ki-" + k) || ""; } catch (e) { return ""; } }
function kiRest(w) { return String(w ?? (KI ? KI.wort : "")).replace(/^\s*gans\b[\s,:–-]*/i, "").replace(/\s+/g, " ").trim(); }
function kiDeText(w) { const r = kiRest(w); return r ? "Gans " + (r === r.toUpperCase() ? r.toLowerCase() : r) : ""; }
function kiDateiname(e) {
  const s = (kiDeText(e && e.wort) || "gans").toLowerCase().replace(/ä/g, "ae").replace(/ö/g, "oe").replace(/ü/g, "ue").replace(/ß/g, "ss")
    .normalize("NFKD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
  return (s || "gans") + "-ki.png";
}
async function oeffneKiBild(opt = {}) {
  if (S.status && S.status.web_app) return toast(t("ki_nur_rechner"));
  KI = { karte: opt.karte || "", wort: opt.wort ?? kiGemerkt("wort"), beschreibung: opt.beschreibung ?? kiGemerkt("beschreibung"),
    ohne: true, info: null, hilfe: false, prompt: false, ergebnis: null };
  if (opt.ergebnis) KI.ergebnis = opt.ergebnis;
  else if (KI_MERK.letzt && (KI_MERK.letzt.karte || "") === KI.karte) KI.ergebnis = KI_MERK.letzt;
  $("#ki-fenster").hidden = false; zeichneKi();
  try { const i = await api("/api/ki-bild"); if (!KI) return; KI.info = i; KI.ohne = i.ohne_menschen; } catch (e) { fehlerToast(e); }
  if (KI) zeichneKi();
}
function kiZustand() {
  const w = kiWartet(); if (w) return "w:" + w.position;
  const L = kiLauf();
  if (L && L.laeuft) return "l:" + (L.ki ? L.ki.vorschau : "");
  if (KI.info && !KI.info.installiert) return "m";
  return KI.ergebnis ? "e:" + KI.ergebnis.id : "x";
}
function kiStandText(L) {
  const z = (L.zeilen || []).filter(x => x.trim() && !/^✕/.test(x)).slice(-1)[0] || "";
  return t("ki_laeuft", (L.ki && L.ki.prozent) || 0) + (z ? " · " + z.trim() : "");
}
function kiErgebnisHTML() {
  const w = kiWartet();
  if (w) return `<div class="ki-bild ki-leer">${enteHTML(t("ki_wartet", w.position))}</div>
      <div class="knopfzeile"><button type="button" class="knopf klein" data-ws="entfernen" data-id="${esc(w.id)}">${esc(t("ws_raus"))}</button>
        <button type="button" class="knopf klein leise" data-ws-oeffnen title="${esc(t("h_ws_knopf"))}">⏳ ${esc(t("ws_titel"))}</button></div>
      <p class="klein" style="margin:0">${esc(t("ki_wartet_info"))}</p>`;
  const L = kiLauf();
  if (L && L.laeuft) {
    const k = L.ki || {};
    return `<div class="ki-bild${k.vorschau ? "" : " ki-leer"}">${k.vorschau ? `<img alt="" data-ki-vorschau src="${esc(url("/api/ki-bild-bild", { id: k.id, art: "vorschau", v: k.vorschau }))}">`
        : enteHTML(t("ki_startet"))}</div>
      <div class="fortschritt" aria-hidden="true"><span style="width:${k.prozent || 0}%"></span></div>
      <p class="klein" style="margin:0" data-ki-stand>${esc(kiStandText(L))}</p>
      <div class="knopfzeile"><button type="button" class="knopf klein" data-lauf-stopp title="${esc(t("h_lauf_stopp"))}">${esc(t("abbrechen"))}</button></div>
      <p class="klein" style="margin:0">${esc(t("ki_hintergrund"))}</p>`;
  }
  if (KI.info && !KI.info.installiert) return `<div class="ki-modell"><img src="/symbol.svg" alt=""><b>${esc(t("ki_modell_fehlt"))}</b>
      <button type="button" class="knopf dunkel" data-ki="modell">${esc(t("ki_modell_laden"))}</button></div>`;
  const e = KI.ergebnis;
  if (e) {
    const bild = url("/api/ki-bild-bild", { id: e.id });
    return `<div class="ki-bild"><img alt="" src="${esc(bild)}"></div>
      <p class="klein" style="margin:0">${esc(t("ki_startwert", e.startwert))}</p>
      <div class="knopfzeile"><button type="button" class="knopf haupt" data-ki="wort-setzen">${esc(t("ki_wort_setzen"))}</button>
        ${e.karte ? `<button type="button" class="knopf" data-ki="fuer-karte">${esc(t("ki_fuer_karte"))}</button>`
          : `<button type="button" class="knopf" data-ki="als-karte">${esc(t("ki_als_karte"))}</button>`}
        <button type="button" class="knopf leise" data-ki="erzeugen">${esc(t("ki_neu_wuerfeln"))}</button>
        <a class="knopf leise" href="${esc(bild)}" download="${esc(kiDateiname(e))}">${esc(t("gw_herunterladen"))}</a></div>`;
  }
  return `<div class="ki-bild ki-leer"><img src="/symbol.svg" alt=""><span>${esc(t("ki_platzhalter"))}</span></div>`;
}
function kiHilfeHTML() {
  const liste = k => `<ul>${t(k).map(x => `<li>${esc(x)}</li>`).join("")}</ul>`;
  return `<section class="ki-hilfe"><b>${esc(t("ki_hilfe_was"))}</b>${liste("ki_hilfe_was_liste")}
    <b>${esc(t("ki_hilfe_gut"))}</b>${liste("ki_hilfe_gut_liste")}<b>${esc(t("ki_hilfe_schwach"))}</b>${liste("ki_hilfe_schwach_liste")}
    <p class="klein" style="margin:0">${esc(t("ki_hilfe_zeit"))}</p></section>`;
}
function kiPromptHTML(i) {
  return `<section class="ki-prompt"><div><b>${esc(t("ki_prompt_titel"))}</b>${i.eigene ? ` <span class="pille">${esc(t("ki_prompt_eigene"))}</span>` : ""}</div>
    <p class="klein" style="margin:0">${esc(t("ki_prompt_text"))}</p>
    <label class="titel" for="ki-vorlage">${esc(t("ki_vorlage"))}</label>
    <textarea class="eingabe" id="ki-vorlage" rows="4" maxlength="${i.max}" lang="en" spellcheck="false">${esc(KI.vorlage ?? i.vorlage)}</textarea>
    <label class="titel" for="ki-negativ">${esc(t("ki_negativ"))}</label>
    <textarea class="eingabe" id="ki-negativ" rows="3" maxlength="${i.max}" lang="en" spellcheck="false">${esc(KI.negativ ?? i.negativ)}</textarea>
    <div class="knopfzeile"><button type="button" class="knopf klein" data-ki="prompt-speichern">${esc(t("ki_prompt_speichern"))}</button>
      <button type="button" class="knopf klein leise" data-ki="prompt-zurueck"${i.eigene ? "" : " disabled"}>${esc(t("ki_prompt_zurueck"))}</button></div>
    <p class="klein ki-fertig-prompt"><b>${esc(t("ki_so_gehts"))}</b> <span id="ki-prompt-vorschau"></span></p></section>`;
}
function zeichneKi() {
  if (!KI) return;
  const i = KI.info, L = kiLauf(), laeuft = !!(L && L.laeuft) || !!kiWartet(), anderer = !!(S.lauf && S.lauf.laeuft && !(L && L.laeuft));
  $("#ki-inhalt").innerHTML = `<div class="ki-raster">
    <div class="ki-form">
      <p class="klein" style="margin:0">${esc(t("ki_intro"))}</p>
      <div><label class="titel" for="ki-wort">${esc(t("ki_wort"))}</label>
        <div class="gw-text"><b>GANS</b><input id="ki-wort" autocomplete="off" spellcheck="false" maxlength="40" placeholder="${esc(t("ki_wort_ph"))}" value="${esc(kiRest())}"></div>
        <div class="klein" style="margin-top:4px">${esc(t("ki_wort_hinweis"))}</div></div>
      <div><label class="titel" for="ki-beschreibung">${esc(t("ki_beschreibung"))}</label>
        <textarea class="eingabe" id="ki-beschreibung" rows="3" maxlength="300" lang="en" placeholder="${esc(t("ki_beschreibung_ph"))}">${esc(KI.beschreibung)}</textarea>
        <div class="knopfzeile ki-unter">${S.sprache !== "en" ? `<button type="button" class="knopf klein leise" data-ki="uebersetzen" title="${esc(t("h_ki_uebersetzen"))}">${esc(t("ki_uebersetzen"))}</button>` : "<span></span>"}
          <span class="klein" id="ki-token"></span></div></div>
      <label class="schalter"><input type="checkbox" id="ki-ohne"${KI.ohne ? " checked" : ""}><span class="spur"></span><span>${esc(t("ki_ohne_menschen"))}</span></label>
      <div class="knopfzeile"><button type="button" class="knopf haupt" data-ki="erzeugen" data-ki-start${laeuft || !i ? " disabled" : ""}>${esc(t("ki_erzeugen"))}</button>
        <button type="button" class="knopf leise" data-ki="hilfe" aria-expanded="${KI.hilfe}">${esc(t("ki_hilfe_knopf"))}</button>
        <button type="button" class="knopf leise" data-ki="prompt" aria-expanded="${KI.prompt}"${i ? "" : " disabled"}>${esc(t("ki_prompt_knopf"))}</button></div>
      <p class="klein ki-zu-lang" data-ki-anderer${anderer ? "" : " hidden"} style="margin:0">${esc(t("ki_anderer_lauf"))}</p>
      ${KI.hilfe ? kiHilfeHTML() : ""}${KI.prompt && i ? kiPromptHTML(i) : ""}
    </div>
    <div class="ki-ergebnis" id="ki-ergebnis" aria-live="polite" data-z="${esc(kiZustand())}">${kiErgebnisHTML()}</div>
  </div>`;
  kiTextSpaeter(0);
}
function kiFortschritt() {                                           // nach jeder Lauf-Abfrage: nur Ergebnis-Teil auffrischen
  if (!KI || $("#ki-fenster").hidden) return;
  const box = $("#ki-ergebnis"); if (!box) return;
  const L = kiLauf(), laeuft = !!(L && L.laeuft), z = kiZustand(), alt = box.dataset.z || "";
  const img = $("[data-ki-vorschau]", box);
  if (alt !== z && laeuft && alt.startsWith("l:") && img && L.ki && L.ki.vorschau) {      // nur neue Vorschau: weich tauschen
    const neu = new Image(), quelle = url("/api/ki-bild-bild", { id: L.ki.id, art: "vorschau", v: L.ki.vorschau });
    neu.onload = () => { img.src = quelle; }; neu.src = quelle; box.dataset.z = z;
  } else if (alt !== z) { box.dataset.z = z; box.innerHTML = kiErgebnisHTML(); }
  if (laeuft && L.ki) {
    const s = $(".fortschritt span", box); if (s) s.style.width = (L.ki.prozent || 0) + "%";
    const p = $("[data-ki-stand]", box); if (p) p.textContent = kiStandText(L);
  }
  const wartet = !!kiWartet(), anderer = !!(S.lauf && S.lauf.laeuft && !laeuft) && !wartet, k = $("[data-ki-start]");
  if (k) k.disabled = laeuft || wartet || !KI.info;
  const h = $("[data-ki-anderer]"); if (h) h.hidden = !anderer;
}
function kiLaufFertig(L) {
  const k = L.ki || {};
  if (L.code === 0 && k.fertig) {
    KI_MERK.letzt = { id: k.id, startwert: k.startwert, karte: k.karte || "", wort: k.wort || "", beschreibung: k.beschreibung || "" };
    if (KI && !$("#ki-fenster").hidden) { KI.ergebnis = KI_MERK.letzt; kiFortschritt(); toast(t("ki_fertig_toast")); }
    else toast(t("ki_fertig_toast"), { aktion: { label: t("ki_ansehen"), fn: () => oeffneKiBild({ karte: KI_MERK.letzt.karte, ergebnis: KI_MERK.letzt }) } });
  } else if (KI_MERK.stopp) toast(t("ki_abgebrochen"));
  else { const z = (L.zeilen || []).filter(x => /^✕/.test(x)).pop(); toast(z ? z.replace(/^✕\s*/, "") : t("ki_fehler"), { fehler: true }); }
  KI_MERK.stopp = false;
  if (KI) kiFortschritt();
}
let kiUhr = null;
function kiTextSpaeter(ms = 400) {                                    // Länge in Token + fertiger Prompt (Server baut ihn)
  clearTimeout(kiUhr);
  kiUhr = setTimeout(async () => {
    if (!KI || !KI.info) return;
    try {
      const r = await api("/api/ki-bild-text", { methode: "POST", daten: { beschreibung: KI.beschreibung, wort: kiDeText(), ohne_menschen: KI.ohne } });
      const tok = $("#ki-token");
      if (tok) { tok.textContent = r.token == null ? "" : r.zu_lang ? t("ki_zu_lang", r.token) : t("ki_token", r.token); tok.classList.toggle("ki-zu-lang", !!r.zu_lang); }
      const v = $("#ki-prompt-vorschau"); if (v) v.textContent = r.prompt + (r.negativ ? `  ·  ${t("ki_negativ_kurz")}: ${r.negativ}` : "");
    } catch (e) { /* nur Anzeige */ }
  }, ms);
}
async function kiToolHolen() {                            // Modell fehlt → Tool „KI-Bilder“ installieren, danach geht das Fenster mit den Eingaben wieder auf
  if (!KI) return;
  const d = { karte: KI.karte, wort: KI.wort, beschreibung: KI.beschreibung };
  await ladeTools();
  return brauchtTool("ki-bild", () => oeffneKiBild(d));
}
async function kiStarten(knopf) {
  if (!KI) return;
  if (!KI.beschreibung.trim()) { toast(t("ki_beschreibung_fehlt"), { fehler: true }); const f = $("#ki-beschreibung"); if (f) f.focus(); return; }
  if (KI.info && !KI.info.installiert) return kiToolHolen();
  if (knopf) knopf.disabled = true;
  try {
    const st = await api("/api/lauf", { methode: "POST", daten: { art: "ki-bild", beschreibung: KI.beschreibung.trim(), wort: kiDeText(),
      ohne_menschen: KI.ohne, karte: KI.karte } });
    KI.ergebnis = null; KI_MERK.stopp = false; KI.wartet = st.wartet ? st.id : null;
    starteBeobachtung(st);
    const box = $("#ki-ergebnis"); if (box && window.innerWidth < 860) box.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (e) { if (knopf) knopf.disabled = false; if (toolFehlt(e)) return kiToolHolen(); fehlerToast(e); }
}
async function kiUebersetzen(b) {
  const text = KI.beschreibung.trim(); if (!text) { toast(t("ki_beschreibung_fehlt"), { fehler: true }); return; }
  const frage = () => api("/api/ki-bild-uebersetzen", { methode: "POST", daten: { text, sprache: S.sprache } });
  b.disabled = true;
  try {
    let r;
    try { r = await frage(); }
    catch (e) { if (e.status === 409 && e.daten && e.daten.code === "zustimmung") { if (!await uebersetzungsTool()) return; r = await frage(); } else throw e; }
    if (!KI) return;
    KI.beschreibung = r.text; kiMerken("beschreibung", r.text);
    const f = $("#ki-beschreibung"); if (f) f.value = r.text;
    kiTextSpaeter(0); toast(t("ki_uebersetzt"));
  } catch (e) { fehlerToast(e); } finally { b.disabled = false; }
}
async function kiBildDatei(e) {                                      // fertiges KI-Bild als Datei (für „GANS-Bild gestalten“)
  const r = await fetch(url("/api/ki-bild-bild", { id: e.id }), { credentials: "same-origin" });
  if (!r.ok) throw new Error(t("fehler_status", r.status));
  return new File([await r.blob()], kiDateiname(e), { type: "image/png" });
}
$("#ki-inhalt").addEventListener("input", e => {
  if (!KI) return;
  if (e.target.id === "ki-wort") { KI.wort = e.target.value; kiMerken("wort", KI.wort); kiTextSpaeter(); }
  if (e.target.id === "ki-beschreibung") { KI.beschreibung = e.target.value; kiMerken("beschreibung", KI.beschreibung); kiTextSpaeter(); }
  if (e.target.id === "ki-vorlage") KI.vorlage = e.target.value;
  if (e.target.id === "ki-negativ") KI.negativ = e.target.value;
});
$("#ki-inhalt").addEventListener("change", e => {
  if (!KI || e.target.id !== "ki-ohne") return;
  KI.ohne = e.target.checked; kiTextSpaeter(0);
  api("/api/ki-bild-prompt", { methode: "POST", daten: { ohne_menschen: KI.ohne } }).then(r => { if (KI) KI.info = r; }).catch(() => {});
});
$("#ki-inhalt").addEventListener("click", async e => {
  const b = e.target.closest("[data-ki]"); if (!b || !KI) return;
  const a = b.dataset.ki, erg = KI.ergebnis;
  if (a === "erzeugen") return kiStarten(b);
  if (a === "hilfe") { KI.hilfe = !KI.hilfe; return zeichneKi(); }
  if (a === "prompt") { KI.prompt = !KI.prompt; return zeichneKi(); }
  if (a === "uebersetzen") return kiUebersetzen(b);
  if (a === "modell") return kiToolHolen();
  b.disabled = true;
  try {
    if (a === "prompt-speichern" || a === "prompt-zurueck") {
      KI.info = await api("/api/ki-bild-prompt", { methode: "POST", daten: a === "prompt-zurueck" ? { zuruecksetzen: true }
        : { vorlage: $("#ki-vorlage").value, negativ: $("#ki-negativ").value } });
      KI.vorlage = KI.negativ = undefined; zeichneKi(); toast(t(a === "prompt-zurueck" ? "ki_prompt_zurueck_ok" : "ki_prompt_gespeichert"));
    }
    if (a === "wort-setzen" && erg) {                                  // 4.7: Wort mit „GANS-Bild gestalten“ daraufsetzen
      const f = await kiBildDatei(erg), wort = kiRest(erg.wort || KI.wort);
      schliesseDialog($("#ki-fenster"));
      oeffneGansWerkzeug({ text: wort ? "GANS " + wort : "", karte: erg.karte, format: "karte" }); await gwFoto([f]);
    }
    if (a === "als-karte" && erg) {
      await api("/api/ki-bild-uebernehmen", { methode: "POST", daten: { id: erg.id } });
      await ladeEntwuerfe(); schliesseDialog($("#ki-fenster")); location.hash = "#bild"; zeige(); toast(t("gw_ok_karte"));
    }
    if (a === "fuer-karte" && erg) {
      const r = await api("/api/ki-bild-uebernehmen", { methode: "POST", daten: { id: erg.id, karte: erg.karte } });
      const vorher = S.ersatz[erg.karte]; S.ersatz[erg.karte] = r;
      if (vorher) api("/api/entwurf-weg", { methode: "POST", daten: { id: vorher.id } }).catch(() => {});
      schliesseDialog($("#ki-fenster")); oeffneEditor(erg.karte); zeichneEditor(erg.karte); toast(t("ki_ok_editor"));
    }
  } catch (err) { fehlerToast(err); }
  finally { b.disabled = false; }
});
document.addEventListener("click", e => {
  if (e.target.closest("[data-lauf-stopp]") && kiLauf()) KI_MERK.stopp = true;
  const an = e.target.closest("[data-ki-ansehen]"), L = kiLauf();
  if (an && L && L.ki) oeffneKiBild({ karte: L.ki.karte || "", ergebnis: { id: L.ki.id, startwert: L.ki.startwert, karte: L.ki.karte || "",
    wort: L.ki.wort || "", beschreibung: L.ki.beschreibung || "" } });
}, true);

/* ----- Ideen für neue Karten ----- */
let IDEEN = null, ideeEntwurf = false;
async function ladeIdeen(zeichnen = true) {
  if (zeichnen && !IDEEN) $("#ideen-inhalt").innerHTML = enteHTML();
  try { IDEEN = await api("/api/ideen"); } catch (e) { if (zeichnen) $("#ideen-inhalt").textContent = e.message; return; }
  zaehler(); if (zeichnen) zeichneIdeen();
}
function ideeFehlt(i) {
  return [!i.bild && t("idee_teil_bild"), !String(i.de || "").trim() && t("idee_teil_de"), !String(i.es || "").trim() && t("idee_teil_es")].filter(Boolean);
}
// Gleiche Wörter erkennen („Gans alt“ = „gans-alt“ = „GANS ALT“; Rückseite: Hauptwort vor „/“) – wie wort_schluessel()
function wortSchluessel(text, rueckseite = false) {
  let s = String(text || "");
  if (rueckseite) s = s.split("/")[0].replace(/\|/g, " ");
  s = s.toLowerCase().replace(/ä/g, "ae").replace(/ö/g, "oe").replace(/ü/g, "ue").replace(/ß/g, "ss")
    .normalize("NFKD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9ñ]+/g, " ").trim();
  return rueckseite ? s : s.replace(/^gans\s+/, "");
}
function ideeDoppelte(el) {
  const id = el.dataset.idee || "", de = wortSchluessel($('[data-i-feld="de"]', el).value), es = wortSchluessel($('[data-i-feld="es"]', el).value, true);
  if (!de && !es) return [];
  const passt = (d, e) => (de && wortSchluessel(d) === de) || (es && wortSchluessel(e, true) === es);
  return [...S.karten.filter(k => passt(k.de, k.es)).map(k => t("doppelt_karte", k.aktiv && k.nr ? k.nr : "–", k.de || k.bild, k.es)),
    ...(IDEEN ? IDEEN.ideen : []).filter(i => i.id !== id && passt(i.de, i.es)).map(i => t("doppelt_idee", i.de || i.es))];
}
function zeigeDoppelte(el) {
  const treffer = ideeDoppelte(el), ziel = $('[data-teil="doppelt"]', el); if (!ziel) return;
  ziel.innerHTML = treffer.length ? `<div class="doppelt-hinweis" role="status"><b>${esc(t("doppelt_titel"))}</b><ul>${treffer.slice(0, 4).map(x => `<li>${esc(x)}</li>`).join("")}</ul></div>` : "";
}
async function holeDeutsch(es) {                                // Kartensprache → „Gans …“ (gleiche Zustimmung wie 🌐)
  const frage = () => api("/api/uebersetzen-de", { methode: "POST", daten: { es } });
  try { return await frage(); }
  catch (e) {
    if (e.status === 409 && e.daten && e.daten.code === "zustimmung") { if (!await uebersetzungsTool()) return null; return await frage(); }
    throw e;
  }
}
function deVorschlagHTML(v) {
  if (!v) return "";
  if (!v.de_text) return `<div class="vorschlag"><span>${esc(t("kein_vorschlag", v.quelle || ""))}</span></div>`;
  return `<div class="vorschlag"><span class="quelle">${esc(t("vorschlag_von", t("ue_dienst_" + v.dienst) || v.dienst_name || "", v.quelle || ""))}</span>
    <div class="chips">${(v.de_alternativen || []).slice(0, 6).map((a, n) => `<button type="button" class="chip${n ? "" : " haupt"}" data-chip-de="${esc(a.text)}" title="${esc([a.hinweis, t("chip_titel")].filter(Boolean).join(" – "))}">${esc(a.text)}</button>`).join("")}</div></div>`;
}
async function ideeNachDeutsch(el, knopf, still = false) {
  const es = $('[data-i-feld="es"]', el).value.trim(), de = $('[data-i-feld="de"]', el);
  if (!es) { if (!still) toast(t("idee_es_zuerst"), { fehler: true }); return; }
  if (knopf) knopf.disabled = true;
  try {
    const v = await holeDeutsch(es); if (!v) return;
    S.vorschlaege["d:" + (el.dataset.idee || "")] = v; $('[data-teil="vorschlag-de"]', el).innerHTML = deVorschlagHTML(v);
    if (v.de_text && !de.value.trim()) { de.value = v.de_text; zeigeDoppelte(el); await ideeSpeichern(el); }
  } catch (err) { if (!still) $('[data-teil="vorschlag-de"]', el).innerHTML = vorschlagFehlerHTML(err); }
  finally { if (knopf) knopf.disabled = false; }
}
function ideeHTML(i) {
  const fehlt = ideeFehlt(i), id = i.id || "";
  return `<article class="idee${fehlt.length ? "" : " fertig"}" data-idee="${esc(id)}">
    <div class="bildfeld" data-zieh="idee">${i.bild ? `<img alt="" src="${url("/api/idee-bild", { id, v: i.v || 0 })}">` : `<span>${esc(t("idee_bild_fehlt"))}</span>`}</div>
    <div class="knopfzeile"><button class="knopf klein" data-i-aktion="bild" title="${esc(t("h_idee_bild"))}">${esc(t("idee_bild_laden"))}</button>
      <button class="knopf klein" data-i-aktion="gestalten" title="${esc(t("h_idee_gestalten"))}">${esc(t("idee_bild_gestalten"))}</button></div>
    <label class="feldname">${esc(t("idee_de"))}<span class="mit-knopf"><input class="eingabe" data-i-feld="de" lang="de" maxlength="120" autocomplete="off" placeholder="${esc(t("idee_de_ph"))}" value="${esc(i.de)}" title="${esc(t("idee_de_titel"))}">
      <button type="button" class="knopf klein leise symbolknopf" data-i-aktion="nach-de" title="${esc(t("idee_nach_de_titel"))}" aria-label="${esc(t("idee_nach_de_titel"))}">🌐</button></span></label>
    <div data-teil="vorschlag-de">${deVorschlagHTML(S.vorschlaege["d:" + id])}</div>
    <label class="feldname"><span>${esc(t("idee_es"))}${chipZs()}</span><span class="mit-knopf"><input class="eingabe${i.es && i.es === i.es_auto ? " ist-auto" : ""}" data-i-feld="es" ${zsAttr()} autocomplete="off" placeholder="${esc(t("idee_es_ph"))}" value="${esc(i.es)}" data-auto="${esc(i.es_auto || "")}" title="${esc(t("h_idee_es"))}">
      <button type="button" class="knopf klein leise symbolknopf" data-i-aktion="uebersetzen" title="${esc(t("uebersetzen_titel"))}" aria-label="${esc(t("uebersetzen_titel"))}">🌐</button></span></label>
    <div data-teil="vorschlag">${vorschlagHTML(S.vorschlaege["i:" + id])}</div>
    <div data-teil="doppelt"></div>
    <label class="feldname">${esc(t("idee_notiz"))}<input class="eingabe" data-i-feld="notiz" autocomplete="off" value="${esc(i.notiz)}" title="${esc(t("h_notiz"))}"></label>
    <div class="fehlt" data-teil="status">${fehlt.length ? esc(t("idee_fehlt_noch", fehlt.join(", "))) : ""}</div>
    <div data-teil="meldungen"></div>
    <div class="knoepfe"><button class="knopf haupt klein" data-i-aktion="aufnehmen" title="${esc(t("h_idee_aufnehmen"))}"${fehlt.length || !id ? " disabled" : ""}>${esc(t("idee_aufnehmen"))}</button>
      ${id ? `<button class="knopf klein leise" data-i-aktion="weg" title="${esc(t("h_idee_weg"))}">${esc(t("idee_weg"))}</button>` : ""}</div></article>`;
}
function zeichneIdeen() {
  if (!IDEEN) return;
  const eigene = (ideeEntwurf ? [{ id: "", de: "", es: "", notiz: "", bild: false }] : []).concat(IDEEN.ideen);
  const unfertig = [
    ...IDEEN.entwuerfe.map(d => ({ art: "entwurf", id: d.id, titel: d.de || d.original, text: t("unfertig_entwurf"), bild: url("/api/entwurf-bild", { id: d.id, art: "original", v: S.v }) })),
    ...IDEEN.offen.map(k => ({ art: "offen", id: k.bild, titel: k.de || k.bild, text: t("unfertig_offen") + (zsMehrere() ? ` (${ZS.kurz})` : ""), bild: url("/bild/" + encodeURIComponent(k.bild), { v: S.v }) })),
    ...IDEEN.ohne.map(k => ({ art: "offen", id: k.bild, titel: k.bild, text: t("unfertig_ohne"), bild: url("/bild/" + encodeURIComponent(k.bild), { v: S.v }) })),
  ];
  $("#ideen-inhalt").innerHTML = `<h2>${esc(t("ideen_eigene"))} (${IDEEN.ideen.length})</h2>
    ${eigene.length ? `<div class="ideen-raster">${eigene.map(ideeHTML).join("")}</div>` : `<div class="flaeche leer"><p>${esc(t("ideen_leer"))}</p></div>`}
    <h2>${esc(t("ideen_unfertig"))} (${unfertig.length})</h2>
    ${unfertig.length ? `<div class="unfertig-liste">${unfertig.map(u => `<div class="unfertig"><span class="mini"><img loading="lazy" alt="" src="${u.bild}"></span>
      <div class="text"><b>${esc(u.titel)}</b><span class="klein">${esc(u.text)}</span></div>
      <button class="knopf klein" data-u-art="${u.art}" data-u-id="${esc(u.id)}" title="${esc(t("h_unfertig_weiter"))}">${esc(t("unfertig_weiter"))}</button></div>`).join("")}</div>`
      : `<p class="klein">${esc(t("ideen_unfertig_leer"))}</p>`}`;
  $$("#ideen-inhalt .idee").forEach(zeigeDoppelte);
}
function ideeWerte(el) {
  const es = $('[data-i-feld="es"]', el);
  return { id: el.dataset.idee || "", de: $('[data-i-feld="de"]', el).value, es: es.value, notiz: $('[data-i-feld="notiz"]', el).value, es_auto: es.dataset.auto || "" };
}
async function ideeSpeichern(el) {
  const w = ideeWerte(el);
  if (!w.id && !w.de.trim() && !w.es.trim()) return;
  try {
    const r = await api("/api/idee", { methode: "POST", daten: w });
    IDEEN = r; zaehler();
    if (!w.id) { ideeEntwurf = false; zeichneIdeen(); return r.id; }
    const i = r.ideen.find(x => x.id === w.id); if (!i) return w.id;
    const fehlt = ideeFehlt(i);
    el.classList.toggle("fertig", !fehlt.length);
    $('[data-teil="status"]', el).textContent = fehlt.length ? t("idee_fehlt_noch", fehlt.join(", ")) : "";
    $('[data-i-aktion="aufnehmen"]', el).disabled = !!fehlt.length;
    $('[data-i-feld="es"]', el).classList.toggle("ist-auto", !!i.es && i.es === i.es_auto);
    $('[data-teil="meldungen"]', el).innerHTML = "";
    return w.id;
  } catch (e) { $('[data-teil="meldungen"]', el).innerHTML = pruefliste([{ stufe: "fehler", text: e.message }]); return null; }
}
async function ideeBild(dateien, zone) {
  const el = zone.closest(".idee"), f = dateien[0]; if (!f) return;
  if (f.size > MAX_MB * 1048576) return toast(t("zu_gross", f.name, MAX_MB), { fehler: true });
  try { IDEEN = await api(url("/api/idee-bild", { id: el.dataset.idee || "" }), { methode: "POST", roh: f }); ideeEntwurf = false; zaehler(); zeichneIdeen(); }
  catch (e) { fehlerToast(e); }
}
ZIEH_ZIELE.idee = ideeBild;
$("#idee-neu").addEventListener("click", () => {
  if (!IDEEN) return; ideeEntwurf = true; zeichneIdeen();
  const f = $('.idee[data-idee=""] [data-i-feld="de"]'); if (f) f.focus();
});
$("#ideen-inhalt").addEventListener("change", e => {
  const el = e.target.closest(".idee"); if (!el || !e.target.matches("[data-i-feld]")) return;
  ideeSpeichern(el);
  // Wort der Kartensprache eingetragen, Text auf dem Bild noch leer: mit Zustimmung + „automatisch“ gleich übersetzen
  if (e.target.dataset.iFeld === "es" && e.target.value.trim() && !$('[data-i-feld="de"]', el).value.trim()
      && S.ue && S.ue.zugestimmt && S.ue.automatisch) ideeNachDeutsch(el, null, true);
});
$("#ideen-inhalt").addEventListener("input", e => { const el = e.target.closest(".idee"); if (el && e.target.matches("[data-i-feld]")) zeigeDoppelte(el); });
$("#ideen-inhalt").addEventListener("keydown", e => { if (e.key === "Enter" && e.target.matches("[data-i-feld]")) { e.preventDefault(); e.target.blur(); } });
$("#ideen-inhalt").addEventListener("click", async e => {
  const u = e.target.closest("[data-u-art]");
  if (u) { if (u.dataset.uArt === "offen") oeffneEditor(u.dataset.uId); else { S.offeneEntwuerfe.add(u.dataset.uId); location.hash = "#bild"; } return; }
  const el = e.target.closest(".idee"); if (!el) return;
  const chip = e.target.closest("[data-chip]");
  if (chip) { const es = $('[data-i-feld="es"]', el); es.value = chip.dataset.chip; es.dataset.auto = chip.dataset.chip; zeigeDoppelte(el); return ideeSpeichern(el); }
  const chipDe = e.target.closest("[data-chip-de]");
  if (chipDe) { $('[data-i-feld="de"]', el).value = chipDe.dataset.chipDe; zeigeDoppelte(el); return ideeSpeichern(el); }
  const b = e.target.closest("[data-i-aktion]"); if (!b) return;
  const a = b.dataset.iAktion, id = el.dataset.idee;
  if (a === "nach-de") return ideeNachDeutsch(el, b);
  if (a === "bild") return dateiWaehlen(BILD_ACCEPT_WEB, d => ideeBild(d, $(".bildfeld", el)));
  if (a === "gestalten") {
    const de = $('[data-i-feld="de"]', el).value;
    return oeffneGansWerkzeug({ idee: id || (await ideeSpeichern(el)) || null, text: de });
  }
  if (a === "uebersetzen") {
    b.disabled = true;
    try {
      const v = await holeVorschlag($('[data-i-feld="de"]', el).value); if (!v) return;
      S.vorschlaege["i:" + id] = v; $('[data-teil="vorschlag"]', el).innerHTML = vorschlagHTML(v);
      const es = $('[data-i-feld="es"]', el);
      if (v.vorschlag && !es.value.trim()) { es.value = v.vorschlag; es.dataset.auto = v.vorschlag; await ideeSpeichern(el); }
    } catch (err) { $('[data-teil="vorschlag"]', el).innerHTML = vorschlagFehlerHTML(err); }
    finally { b.disabled = false; }
    return;
  }
  if (a === "weg") {
    try {
      IDEEN = await api("/api/idee-weg", { methode: "POST", daten: { id } }); zaehler(); zeichneIdeen();
      toast(t("idee_verworfen"), { aktion: { label: t("zurueck_knopf"), fn: async () => {
        try { IDEEN = await api("/api/idee-zurueck", { methode: "POST", daten: { id } }); zaehler(); if (ansicht() === "ideen") zeichneIdeen(); } catch (err) { fehlerToast(err); } } } });
    } catch (err) { fehlerToast(err); }
    return;
  }
  if (a === "aufnehmen") {
    b.disabled = true;
    const ersetzen = !!($('[data-i-ersetzen]', el) || {}).checked;
    try {
      const r = await api("/api/idee-aufnehmen", { methode: "POST", daten: { id, ersetzen } });
      if (r.ok) { IDEEN = r; uebernehmeKarten(r.karten); S.v++; zeichneIdeen(); toast(t("idee_aufgenommen", r.name)); return; }
      $('[data-teil="meldungen"]', el).innerHTML = pruefliste(r.meldungen) + (r.kollision
        ? `<label class="schalter"><input type="checkbox" data-i-ersetzen><span class="spur"></span><span>${esc(t("idee_ersetzen"))}</span></label>` : "");
    } catch (err) { $('[data-teil="meldungen"]', el).innerHTML = pruefliste([{ stufe: "fehler", text: err.message }]); }
    b.disabled = false;
  }
});

/* ----- Programmstart: Browser oder eigenes Fenster (auch Schritt 2 des Willkommens-Assistenten) ----- */
let STW = null;
function startWahlHTML(st) {
  const aktuell = st.art === "fenster" ? "fenster" : st.browser && st.browser !== "standard" ? "browser:" + st.browser : "standard";
  const fensterB = st.liste.find(b => b.fenster && b.id === st.browser) || st.liste.find(b => b.fenster);
  const zeile = (wert, titel, text, gesperrt) => `<label class="dienst"><input type="radio" name="st-wahl" value="${esc(wert)}"${wert === aktuell ? " checked" : ""}${gesperrt ? " disabled" : ""}>
    <span><b>${esc(titel)}</b><span class="klein">${esc(text)}</span></span></label>`;
  return `<p class="unter klein">${esc(t("st_text"))}</p><div class="dienste" role="radiogroup">
      ${zeile("standard", t("st_standard"), t("st_standard_text"), false)}
      ${zeile("fenster", t("st_fenster"), fensterB ? t("st_fenster_text", fensterB.name) : t("st_fenster_nein"), !fensterB)}
      ${st.liste.map(b => zeile("browser:" + b.id, t("st_browser", b.name), t("st_browser_text"), false)).join("")}</div>`;
}
function startDaten(st) {                                       // gewählte Zeile → {art, browser}
  const w = ($('input[name="st-wahl"]:checked') || {}).value || "standard";
  const fensterB = st.liste.find(x => x.fenster && x.id === st.browser) || st.liste.find(x => x.fenster);
  return w === "fenster" ? { art: "fenster", browser: fensterB ? fensterB.id : "standard" }
    : w.startsWith("browser:") ? { art: "browser", browser: w.slice(8) } : { art: "browser", browser: "standard" };
}
async function oeffneStartWahl() {
  try { STW = await api("/api/start-einstellung"); } catch (e) { fehlerToast(e); return; }
  $("#start-inhalt").innerHTML = startWahlHTML(STW) + `<div class="knopfzeile abstand"><div class="rechts">
      <button class="knopf leise" data-st="spaeter">${esc(t("abbrechen_knopf"))}</button>
      <button class="knopf haupt" data-st="speichern">${esc(t("st_speichern"))}</button></div></div>`;
  $("#start-fenster").hidden = false;
}
$("#start-inhalt").addEventListener("click", async e => {
  const b = e.target.closest("[data-st]"); if (!b) return;
  if (b.dataset.st === "spaeter") { $("#start-fenster").hidden = true; return; }
  try {
    const r = await api("/api/start-einstellung", { methode: "POST", daten: startDaten(STW) }); STW = r;
    $("#start-fenster").hidden = true; toast(r.meldung);
    await ladeWerkzeuge(); if (ansicht() === "werkzeuge") zeichneWerkzeuge();
  } catch (err) { fehlerToast(err); }
});

/* ----- QR-Code ohne Zusatzpaket (Byte-Modus, Fehlerkorrektur M, Version 1–6, also bis 106 Zeichen) – nach der
   QR-Norm: Reed-Solomon über GF(256) mit 0x11D, Formatbits BCH(15,5) mit 0x537 und Maske 0x5412, 8 Masken mit
   Strafpunkten. Für die Handy-Adresse: Kamera drauf, fertig. ----- */
const QR_M = { 1: [10, 1], 2: [16, 1], 3: [26, 1], 4: [18, 2], 5: [24, 2], 6: [16, 4] };     // Prüfwörter je Block, Blöcke
const QR_GESAMT = { 1: 26, 2: 44, 3: 70, 4: 100, 5: 134, 6: 172 };                        // Codewörter je Version
const QR_AUSRICHTUNG = { 2: 18, 3: 22, 4: 26, 5: 30, 6: 34 };
const QR_EXP = [], QR_LOG = [];
(() => { let x = 1; for (let i = 0; i < 255; i++) { QR_EXP[i] = x; QR_LOG[x] = i; x <<= 1; if (x & 256) x ^= 0x11D; }
  for (let i = 255; i < 512; i++) QR_EXP[i] = QR_EXP[i - 255]; })();
const qrMal = (a, b) => (a && b ? QR_EXP[QR_LOG[a] + QR_LOG[b]] : 0);
const QR_MASKEN = [(c, r) => (c + r) % 2 === 0, (c, r) => r % 2 === 0, c => c % 3 === 0, (c, r) => (c + r) % 3 === 0,
  (c, r) => (Math.floor(c / 3) + Math.floor(r / 2)) % 2 === 0, (c, r) => (c * r) % 2 + (c * r) % 3 === 0,
  (c, r) => ((c * r) % 2 + (c * r) % 3) % 2 === 0, (c, r) => ((c + r) % 2 + (c * r) % 3) % 2 === 0];
function qrRS(daten, n) {                                       // n Reed-Solomon-Prüfwörter
  let gen = [1];
  for (let i = 0; i < n; i++) {
    const neu = new Array(gen.length + 1).fill(0);
    gen.forEach((g, j) => { neu[j] ^= g; neu[j + 1] ^= qrMal(g, QR_EXP[i]); });
    gen = neu;
  }
  const rest = new Array(n).fill(0);
  for (const d of daten) {
    const f = d ^ rest.shift(); rest.push(0);
    for (let j = 0; j < n; j++) rest[j] ^= qrMal(gen[j + 1], f);
  }
  return rest;
}
function qrFormat(k, N, maske) {                                // Stufe M = 00, dann 3 Bit Maske
  let rest = maske;
  for (let i = 0; i < 10; i++) rest = (rest << 1) ^ ((rest >>> 9) * 0x537);
  const bits = ((maske << 10) | rest) ^ 0x5412, bit = i => (bits >>> i) & 1;
  for (let i = 0; i <= 5; i++) k[i][8] = bit(i);
  k[7][8] = bit(6); k[8][8] = bit(7); k[8][7] = bit(8);
  for (let i = 9; i < 15; i++) k[8][14 - i] = bit(i);
  for (let i = 0; i < 8; i++) k[8][N - 1 - i] = bit(i);
  for (let i = 8; i < 15; i++) k[N - 15 + i][8] = bit(i);
  k[N - 8][8] = 1;
}
function qrStrafe(m) {
  const N = m.length; let s = 0;
  for (const z of [...m, ...m[0].map((_, c) => m.map(zz => zz[c]))]) {
    let lauf = 1;
    for (let i = 1; i <= N; i++) {
      if (i < N && z[i] === z[i - 1]) lauf++;
      else { if (lauf >= 5) s += lauf - 2; lauf = 1; }
    }
    const t = z.join("");
    for (const muster of ["10111010000", "00001011101"]) for (let p = t.indexOf(muster); p >= 0; p = t.indexOf(muster, p + 1)) s += 40;
  }
  for (let r = 0; r < N - 1; r++) for (let c = 0; c < N - 1; c++) {
    const v = m[r][c]; if (v === m[r][c + 1] && v === m[r + 1][c] && v === m[r + 1][c + 1]) s += 3;
  }
  const dunkel = m.reduce((a, z) => a + z.reduce((x, y) => x + y, 0), 0);
  return s + Math.floor(Math.abs(dunkel * 20 - N * N * 10) / (N * N)) * 10;
}
function qrMatrix(text) {
  const bytes = [...new TextEncoder().encode(text)];
  let v = 1;
  while (v <= 6 && bytes.length > QR_GESAMT[v] - QR_M[v][0] * QR_M[v][1] - 2) v++;
  if (v > 6) return null;
  const [ecc, bloecke] = QR_M[v], datenCw = QR_GESAMT[v] - ecc * bloecke, bits = [];
  const schreib = (wert, n) => { for (let i = n - 1; i >= 0; i--) bits.push((wert >>> i) & 1); };
  schreib(4, 4); schreib(bytes.length, 8); bytes.forEach(b => schreib(b, 8));
  schreib(0, Math.min(4, datenCw * 8 - bits.length));
  while (bits.length % 8) bits.push(0);
  const cw = [];
  for (let i = 0; i < bits.length; i += 8) cw.push(parseInt(bits.slice(i, i + 8).join(""), 2));
  for (let p = 0; cw.length < datenCw; p++) cw.push(p % 2 ? 0x11 : 0xEC);
  const je = datenCw / bloecke, bl = [], pr = [], folge = [];
  for (let b = 0; b < bloecke; b++) { const d = cw.slice(b * je, (b + 1) * je); bl.push(d); pr.push(qrRS(d, ecc)); }
  for (let i = 0; i < je; i++) bl.forEach(d => folge.push(d[i]));
  for (let i = 0; i < ecc; i++) pr.forEach(e => folge.push(e[i]));
  const N = 17 + 4 * v, m = Array.from({ length: N }, () => new Array(N).fill(0));
  const fest = Array.from({ length: N }, () => new Array(N).fill(false));
  const setze = (r, c, d) => { m[r][c] = d ? 1 : 0; fest[r][c] = true; };
  for (const [r0, c0] of [[0, 0], [0, N - 7], [N - 7, 0]]) {          // Suchmuster + heller Rand
    for (let r = -1; r <= 7; r++) for (let c = -1; c <= 7; c++) {
      const rr = r0 + r, cc = c0 + c; if (rr < 0 || cc < 0 || rr >= N || cc >= N) continue;
      const innen = r >= 0 && r <= 6 && c >= 0 && c <= 6;
      setze(rr, cc, innen && (r === 0 || r === 6 || c === 0 || c === 6 || (r >= 2 && r <= 4 && c >= 2 && c <= 4)));
    }
  }
  for (let i = 8; i < N - 8; i++) { setze(6, i, i % 2 === 0); setze(i, 6, i % 2 === 0); }      // Taktlinien
  if (v >= 2) { const a = QR_AUSRICHTUNG[v]; for (let r = -2; r <= 2; r++) for (let c = -2; c <= 2; c++) setze(a + r, a + c, Math.max(Math.abs(r), Math.abs(c)) !== 1); }
  for (let i = 0; i <= 8; i++) { fest[i][8] = fest[8][i] = true; }                    // Formatbereiche freihalten
  for (let i = 0; i < 8; i++) { fest[8][N - 1 - i] = fest[N - 1 - i][8] = true; }
  setze(N - 8, 8, true);                                                             // immer dunkel
  let i = 0;
  for (let rechts = N - 1; rechts >= 1; rechts -= 2) {                                 // Daten im Zickzack
    if (rechts === 6) rechts = 5;
    for (let senk = 0; senk < N; senk++) for (let j = 0; j < 2; j++) {
      const c = rechts - j, r = ((rechts + 1) & 2) === 0 ? N - 1 - senk : senk;
      if (!fest[r][c] && i < folge.length * 8) { m[r][c] = (folge[i >>> 3] >>> (7 - (i & 7))) & 1; i++; }
    }
  }
  let beste = null;
  for (let maske = 0; maske < 8; maske++) {
    const k = m.map(z => z.slice());
    for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) if (!fest[r][c] && QR_MASKEN[maske](c, r)) k[r][c] ^= 1;
    qrFormat(k, N, maske);
    const s = qrStrafe(k); if (!beste || s < beste.s) beste = { s, k };
  }
  return beste.k;
}
function qrSvg(text) {
  const m = qrMatrix(text); if (!m) return "";
  const N = m.length, rand = 4; let pfad = "";
  m.forEach((z, r) => z.forEach((d, c) => { if (d) pfad += `M${c + rand} ${r + rand}h1v1h-1z`; }));
  return `<svg class="qr" viewBox="0 0 ${N + 2 * rand} ${N + 2 * rand}" role="img" aria-label="${esc(t("lan_qr"))}" shape-rendering="crispEdges">`
    + `<rect width="100%" height="100%" fill="#fff"/><path d="${pfad}" fill="#000"/></svg>`;
}

/* ----- Handy-Zugang im WLAN (optional): Adresse, QR-Code + PIN anzeigen, an/aus ----- */
async function oeffneHandy() {
  let st; try { st = await api("/api/lan"); } catch (e) { return fehlerToast(e); }
  zeichneHandy(st); $("#lan-fenster").hidden = false;
}
function zeichneHandy(st) {
  $("#lan-inhalt").innerHTML = `<p>${esc(t("lan_text"))}</p>
    <div class="hinweisbox warn"><b>${esc(t("lan_warnung_titel"))}</b><p>${esc(t("lan_warnung"))}</p></div>
    <p class="klein">${esc(t("lan_firewall"))}</p>
    ${st.an ? `<div class="lan-an"><div class="klein">${esc(t("lan_schritt1"))}</div><div class="lan-qr">${qrSvg(st.adresse)}</div><div class="lan-adresse">${esc(st.adresse)}</div>
        <div class="klein">${esc(t("lan_schritt2"))}</div><div class="lan-pin">${esc(st.pin)}</div>
        <p class="klein">${esc(t("lan_minuten", st.minuten))}</p></div>
        <div class="knopfzeile"><button class="knopf" data-lan="aus">${esc(t("lan_aus"))}</button></div>`
      : `<div class="knopfzeile"><button class="knopf haupt" data-lan="an"${st.ip_gefunden ? "" : " disabled"}>${esc(t("lan_an"))}</button></div>
        ${st.ip_gefunden ? "" : `<p class="klein">${esc(t("lan_kein_netz"))}</p>`}`}
    ${appAdresse() ? `<h3 class="abstand">📲 ${esc(t("app_als_app"))}</h3><p class="klein">${esc(t("lan_app_text"))}</p>
      <div class="lan-an" id="lan-app"><div class="lan-qr">${qrSvg(appAdresse())}</div><div class="lan-adresse lang">${esc(appAdresse())}</div></div>
      <p class="klein">${esc(t("app_anleitungen"))}</p>` : ""}`;
}
$("#lan-inhalt").addEventListener("click", async e => {
  const b = e.target.closest("[data-lan]"); if (!b) return;
  b.disabled = true;
  try { zeichneHandy(await api("/api/lan", { methode: "POST", daten: { an: b.dataset.lan === "an" } })); await ladeWerkzeuge(); if (ansicht() === "werkzeuge") zeichneWerkzeuge(); }
  catch (err) { fehlerToast(err); b.disabled = false; }
});

/* ----- Willkommens-Assistent: beim ersten Öffnen über das Startprogramm (Sprache → Startart → kurze Tour) ----- */
let WK = { schritt: 0, st: null, wahl: null, schritte: [] };
function oeffneWillkommen(st) {
  WK = { schritt: 0, st, wahl: null, schritte: ["sprache", "start", ...(TOOLS && TOOLS.erstabfrage ? ["tools"] : []), "tour"] };
  TOOL_ERST = new Set(); zeichneWillkommen(); $("#willkommen-fenster").hidden = false;
}
function zeichneWillkommen() {
  const n = WK.schritte.length, s = WK.schritt, art = WK.schritte[s], sprachen = { en: "English", de: "Deutsch", es: "Español" };
  let inhalt = "";
  if (art === "sprache") inhalt = `<div class="wk-ente">${enteHTML(t("wk_untertitel"))}</div><h2 id="wk-titel">${esc(t("wk_titel"))}</h2>
      <p>${esc(t("wk_text"))}</p><p class="klein"><b>${esc(t("wk_sprache"))}</b></p>
      <div class="knopfzeile wk-sprachen" role="group" aria-label="${esc(t("wk_sprache"))}">${Object.keys(sprachen).map(l =>
        `<button class="knopf${S.sprache === l ? " haupt" : ""}" data-wk-sprache="${l}" lang="${l}">${sprachen[l]}</button>`).join("")}</div>`;
  if (art === "start") inhalt = `<h2 id="wk-titel">${esc(t("st_titel"))}</h2>${startWahlHTML(WK.wahl ? { ...WK.st, ...WK.wahl } : WK.st)}`;
  if (art === "tools") inhalt = `<h2 id="wk-titel">🧰 ${esc(t("tools_erst_titel"))}</h2>${toolErstHTML()}`;
  if (art === "tour") inhalt = `<h2 id="wk-titel">${esc(t("wk_tour_titel"))}</h2><ol class="wk-tour">${[1, 2, 3, 4].map(n =>
      `<li><b>${esc(t("wk_tour_" + n + "_t"))}</b><span>${esc(t("wk_tour_" + n))}</span></li>`).join("")}</ol><p class="klein">${esc(t("wk_hilfe"))}</p>`;
  $("#wk-inhalt").innerHTML = inhalt + `<div class="wk-fuss"><div class="wk-punkte" aria-hidden="true">${WK.schritte.map((_, i) => `<span class="${i === s ? "an" : ""}"></span>`).join("")}</div>
    <div class="knopfzeile">${s ? `<button class="knopf leise" data-wk="zurueck">${esc(t("wk_zurueck"))}</button>` : `<button class="knopf leise" data-wk="spaeter">${esc(t("st_spaeter"))}</button>`}
    <button class="knopf haupt" data-wk="${s < n - 1 ? "weiter" : "fertig"}">${esc(s < n - 1 ? t("wk_weiter") : t("wk_los"))}</button></div></div>`;
}
$("#wk-inhalt").addEventListener("click", async e => {
  const sp = e.target.closest("[data-wk-sprache]");
  if (sp) { const knopf = $(`.sprachwahl [data-sprache="${sp.dataset.wkSprache}"]`); if (knopf) knopf.click(); setTimeout(zeichneWillkommen, 60); return; }
  const b = e.target.closest("[data-wk]"); if (!b) return;
  if (WK.schritte[WK.schritt] === "start") WK.wahl = startDaten(WK.st);
  if (b.dataset.wk === "spaeter") { $("#willkommen-fenster").hidden = true; return; }
  if (b.dataset.wk === "zurueck") { WK.schritt--; return zeichneWillkommen(); }
  if (b.dataset.wk === "weiter") { WK.schritt++; return zeichneWillkommen(); }
  b.disabled = true;
  try {
    await api("/api/start-einstellung", { methode: "POST", daten: { ...(WK.wahl || { art: "browser", browser: "standard" }), willkommen: true } });
    $("#willkommen-fenster").hidden = true; toast(t("wk_fertig_toast"));
    if (WK.schritte.includes("tools")) await toolsErstabfrageSenden([...TOOL_ERST]);   // nichts gewählt = später
    await ladeWerkzeuge(); if (ansicht() === "werkzeuge") zeichneWerkzeuge();
  } catch (err) { fehlerToast(err); b.disabled = false; }
});

/* ----- Deinstallieren: eigener, letzter Reiter – erst sichern, dann (nach Rückfrage) sauber entfernen ----- */
let gesichert = false;                                         // in dieser Sitzung schon eine Sicherung geladen?
function sicherungsLink(klasse = "knopf haupt") {
  return `<a class="${klasse}" href="${url("/api/export", { inhalt: "alles", umfang: "alle" })}" download data-sicherung title="${esc(t("dei_sichern_titel"))}">${esc(t("dei_sichern_knopf"))}</a>`;
}
function zeichneDeinstallieren() {
  const karten = S.karten.length, ideen = IDEEN ? IDEEN.ideen.length : 0;
  $("#deinst-seite").innerHTML = `
    <section class="flaeche"><h2><span class="schritt-nr">1</span> ${esc(t("dei_s1_titel"))}</h2>
      <p>${esc(t("dei_s1_text", karten, ideen))}</p>
      <div class="knopfzeile">${sicherungsLink()}<span class="klein">${esc(gesichert ? t("dei_gesichert") : t("dei_s1_hinweis"))}</span></div></section>
    <section class="flaeche"><h2><span class="schritt-nr">2</span> ${esc(t("dei_s2_titel"))}</h2>
      <p>${esc(t("de_text"))}</p>
      <ul class="dei-liste"><li>${esc(t("de_p1"))}</li><li>${esc(t("de_p2"))}</li><li><b>${esc(t("de_p3"))}</b></li></ul>
      <p class="klein">${esc(t("dei_s2_nicht"))}</p>
      <div class="knopfzeile"><button class="knopf gefahr-voll" data-dialog="deinstallieren" title="${esc(t("dei_knopf_titel"))}">${esc(t("dei_knopf"))}</button></div></section>
    <p class="klein">${esc(t("dei_neu"))}</p>`;
}
document.addEventListener("click", e => { if (e.target.closest("[data-sicherung]")) { gesichert = true; setTimeout(() => { if (ansicht() === "deinstallieren") zeichneDeinstallieren(); }, 300); } });
function oeffneDeinstallieren() {
  $("#deinst-inhalt").innerHTML = `<p class="gross-frage"><b>${esc(t("de_sicher"))}</b></p><p>${esc(t("de_text"))}</p>
    <div class="gefahr-flaeche"><ul><li>${esc(t("de_p1"))}</li><li>${esc(t("de_p2"))}</li><li><b>${esc(t("de_p3"))}</b></li></ul>
      <p style="margin:8px 0 0"><b>${esc(t("de_warnung"))}</b></p></div>
    ${gesichert ? `<p class="klein">✓ ${esc(t("dei_gesichert"))}</p>` : `<div class="hinweisbox warn"><b>${esc(t("de_keine_sicherung"))}</b><div class="knopfzeile abstand">${sicherungsLink("knopf")}</div></div>`}
    <label class="schalter abstand"><input type="checkbox" id="de-haken"><span class="spur"></span><span>${esc(t("de_haken"))}</span></label>
    <div class="knopfzeile abstand"><div class="rechts"><button class="knopf haupt" data-zu title="${esc(t("h_de_doch_nicht"))}">${esc(t("de_doch_nicht"))}</button>
      <button class="knopf gefahr-voll" data-de="los" title="${esc(t("h_de_los"))}" disabled>${esc(t("de_los"))}</button></div></div>`;
  $("#deinst-fenster").hidden = false;
}
$("#deinst-inhalt").addEventListener("change", e => { if (e.target.id === "de-haken") $('[data-de="los"]').disabled = !e.target.checked; });
$("#deinst-inhalt").addEventListener("click", async e => {
  if (e.target.closest("[data-sicherung]")) { setTimeout(oeffneDeinstallieren, 300); return; }
  const b = e.target.closest("[data-de]"); if (!b) return;
  if (!$("#de-haken").checked) return;
  b.disabled = true;
  try {
    await api("/api/deinstallieren", { methode: "POST", daten: { bestaetigt: true } });
    $("#deinst-fenster").hidden = true; $("#ende-text").textContent = t("de_ende"); $("#ende").hidden = false;
  } catch (err) { fehlerToast(err); b.disabled = false; }
});

async function nachStart() {                     // nach dem Laden: Ideen zählen; beim ersten Start nach dem Öffnen fragen
  ladeIdeen(false);
  let st = null;
  try { st = await api("/api/start-einstellung"); } catch (e) { /* ohne erweiterungen.py: nichts zu fragen */ }
  if (st && st.vom_starter && !st.willkommen) oeffneWillkommen(st);    // erster Start: Willkommens-Assistent (mit Tools)
  else if (TOOLS && TOOLS.erstabfrage && !AM_HANDY && !offenerDialog()) oeffneToolErstabfrage();   // sonst einmal fragen
}

/* ===================== Start ===================== */
async function ladeStatus() {
  try {
    S.status = await api("/api/status");
    const s = S.status;
    if (uebernehmeZs(s.zielsprache) && S.gestartet) zeige();
    $$("[data-ki-knopf]").forEach(el => { el.hidden = !s.ki_bild && !s.web_app; });   // App: Knopf bleibt, Hinweis „nur am Rechner“
    $("#statusfuss").innerHTML = `${esc(t("fuss_version", s.version))}<br>
      <span class="${(s.ki_methode || "").startsWith("realesrgan") ? "ok" : "nein"}">${esc(t("fuss_ki", s.ki_name))}</span><br>
      <span class="${s.vorschau ? "ok" : "nein"}">${esc(s.vorschau ? t("fuss_vorschau_ok") : t("fuss_vorschau_nein"))}</span>`;
  } catch (e) { /* Verbindungshinweis erscheint */ }
}
/* ===================== Karten lernen (Tool „lernen“; Server: lernen.py, /api/lernen*) =====================
   Übersicht (heute, Stapel, Statistik, Einstellungen, Sichern) und Sitzung: Vorderseite → „Antwort zeigen“ → Nochmal/
   Schwer/Gut/Einfach. Jede Bewertung speichert der Server sofort; die Antwort bringt gleich die nächste Karte mit. */
let LERN = null, LS = null, LERN_DLG = null;
S.lernFilter = ""; S.lernAuswahl = null;                    // Meine Karten: Filter nach Lernstand, Häkchen-Auswahl (Set)
const LERN_AUSWAHL_ID = "00000000";                         // Stapel „Aktuelle Auswahl“ (Jetzt lernen aus Meine Karten)
function lernDa() { const x = toolInfo("lernen"); return !!(x && x.installiert); }
async function ladeLernen(trotzdem = false) {
  if (!trotzdem && !lernDa()) { LERN = null; lernZahl(); return null; }
  try { LERN = await api("/api/lernen"); }
  catch (e) { LERN = null; if (!toolFehlt(e)) fehlerToast(e); }
  lernZahl(); return LERN;
}
const lernSpaeter = entprellt(() => { if (lernDa()) ladeLernen().then(() => { if (ansicht() === "lernen" && !LS) zeichneLernen(); }); }, 700);
function lernAlle() { return (LERN && LERN.stapel.find(s => s.id === "alle")) || null; }
function lernZahl() {
  const el = $("#zahl-lernen"); if (!el) return;
  const a = lernAlle(), n = a ? a.faellig + a.neu : 0;
  el.hidden = !n; el.textContent = n; el.title = a ? t("ln_heute", a.faellig, a.neu) : "";
  appNaviZahlen();
}
async function lernAktiviert() {                            // Tool eben aktiviert: Stand holen, Ansichten neu zeichnen
  await ladeLernen(true); await ladeKarten().catch(() => {});
  if (ansicht() === "lernen") zeichneLernen();
  if (ansicht() === "karten") zeichneKarten();
}
async function zeichneLernen() {
  const el = $("#lern-inhalt"); if (!el) return;
  if (LS) return zeichneSitzung();
  if (!lernDa() && !LERN) { el.innerHTML = lernAusHTML(); return; }
  if (!LERN) el.innerHTML = enteHTML();
  await ladeLernen();
  if (ansicht() !== "lernen" || LS) return;
  el.innerHTML = LERN ? lernUebersichtHTML() : lernAusHTML();
}
function lernAusHTML() {
  return `<section class="flaeche tool-hinweis"><h2 style="margin:0">🎓 ${esc(t("ln_aus_titel"))}</h2><p>${esc(t("ln_aus_text"))}</p>
    <div class="knopfzeile"><button class="knopf haupt" type="button" data-ln="aktivieren">${esc(t("ln_aktivieren"))}</button></div></section>`;
}
function lernStapelText(s) {
  if (s.id === "alle") return t("ln_alle_text");
  const teile = [];
  if (s.sprache) teile.push(zsName(s.sprache));
  if (s.notiz) teile.push(`${t("ln_st_notiz")}: ${s.notiz}`);
  if (s.suche) teile.push(`${t("ln_st_suche").replace(/\s*\(.*\)$/, "")}: ${s.suche}`);
  if (s.nur) teile.push(t("ln_nur_" + s.nur));
  if (s.bilder) teile.push(t("ln_st_auswahl_n", s.bilder.length));
  return teile.join(" · ");
}
function lernWocheSVG(w) {                                    // Balken „fällig in den nächsten 7 Tagen“ (Farben über CSS-Variablen)
  const max = Math.max(1, ...w), H = 110, bw = 300 / 7;
  const tag = i => i === 0 ? t("ln_heute_kurz") : new Date(Date.now() + i * 864e5).toLocaleDateString(S.sprache, { weekday: "short" });
  return `<svg class="lern-woche" viewBox="0 0 300 ${H + 36}" role="img" aria-label="${esc(t("ln_woche_titel") + ": " + w.join(", "))}">${w.map((n, i) => {
    const h = Math.max(n ? 3 : 0, Math.round(n / max * H)), x = i * bw + 5, mitte = x + (bw - 10) / 2;
    return `<rect x="${x.toFixed(1)}" y="${H - h + 14}" width="${(bw - 10).toFixed(1)}" height="${h}" rx="4"${i === 0 ? ' class="heute"' : ""}></rect>`
      + `<text x="${mitte.toFixed(1)}" y="${H - h + 10}" class="zahl">${n}</text><text x="${mitte.toFixed(1)}" y="${H + 32}">${esc(tag(i))}</text>`;
  }).join("")}</svg>`;
}
function lernZustaendeHTML(z) {
  const arten = ["neu", "lernt", "jung", "sicher"], summe = arten.reduce((s, k) => s + (z[k] || 0), 0) || 1;
  return `<div class="lern-zustaende" title="${esc(t("h_ln_zustaende"))}"><div class="balken">${arten.map(k => z[k] ? `<span class="st-${k}" style="width:${(z[k] * 100 / summe).toFixed(2)}%"></span>` : "").join("")}</div>
    <ul>${arten.map(k => `<li><i class="st-${k}"></i>${esc(t("ln_z_" + k))}: <b>${z[k] || 0}</b></li>`).join("")}</ul></div>`;
}
function lernEinstHTML() {
  const e = LERN.einstellungen, q = Math.min(95, Math.max(80, Math.round(e.behaltensquote * 100)));
  const wahl = (feld, werte, akt) => `<select data-le="${feld}">${werte.map(([v, txt]) => `<option value="${esc(v)}"${String(akt) === String(v) ? " selected" : ""}>${esc(txt)}</option>`).join("")}</select>`;
  return `<form class="lern-einst" data-ln-form="einst">
    <label class="f"><span>${esc(t("ln_neu_tag"))}</span><input type="number" min="0" max="9999" data-le="neu_pro_tag" value="${e.neu_pro_tag}"></label>
    <label class="f"><span>${esc(t("ln_wdh_tag"))}</span><input type="number" min="0" max="99999" data-le="wdh_pro_tag" value="${e.wdh_pro_tag}"></label>
    <label class="f"><span>${esc(t("ln_richtung"))}</span>${wahl("richtung", ["vorwaerts", "rueckwaerts", "beide"].map(r => [r, t("ln_r_" + r)]), e.richtung)}</label>
    ${zsMehrere() ? `<label class="f"><span>${esc(t("ln_sprache"))}</span>${wahl("sprache", [["", t("ln_sprache_auto")], ...ZS.installiert.map(c => [c, zsName(c)])], e.sprache || "")}</label>` : ""}
    <label class="f"><span>${esc(t("ln_wechsel"))}</span>${wahl("tageswechsel", Array.from({ length: 24 }, (_, h) => [h, String(h).padStart(2, "0") + ":00"]), e.tageswechsel)}</label>
    <label class="f breit"><span>${esc(t("ln_quote_ziel"))}: <b data-le-wert>${q} %</b></span><input type="range" min="80" max="95" step="1" data-le="behaltensquote" value="${q}">
      <span class="klein">${esc(t("ln_quote_erkl"))}</span></label>
    <div class="knopfzeile breit"><button class="knopf haupt" type="submit">${esc(t("ln_speichern"))}</button></div></form>`;
}
function lernUebersichtHTML() {
  const a = lernAlle() || { faellig: 0, neu: 0 }, st = LERN.statistik, heute = a.faellig + a.neu;
  const kachel = `<section class="flaeche lern-heute"><div><h2>${esc(t("ln_heute", a.faellig, a.neu))}</h2><p class="klein">${esc(t("ln_serie", st.serie))}</p></div>
    <div class="knopfzeile">${LERN.rueckgaengig ? `<button class="knopf leise" type="button" data-ln="rueck" title="${esc(t("h_ln_rueck"))}">↶ ${esc(t("ln_rueck"))}</button>` : ""}
    ${heute ? `<button class="knopf haupt gross" type="button" data-ln="lernen" data-stapel="alle">${esc(t("ln_los"))}</button>` : `<span class="pille ok">${esc(t("ln_fertig_heute"))}</span>`}</div></section>`;
  const stapel = LERN.stapel.map(s => {
    const name = s.id === "alle" ? t("ln_alle") : s.name, eigen = s.id !== "alle";
    return `<li class="lern-stapel"><div class="name"><b>${esc(name)}</b><span class="klein">${esc(lernStapelText(s))}</span></div>
      <span class="pille${s.faellig ? " laeuft" : ""}">${esc(t("ln_stapel_zahlen", s.faellig, s.neu))}</span>
      <div class="knopfzeile"><button class="knopf klein${s.faellig + s.neu ? " haupt" : ""}" type="button" data-ln="lernen" data-stapel="${esc(s.id)}">${esc(t("ln_lernen_knopf"))}</button>
      ${eigen ? `<button class="knopf klein" type="button" data-ln="stapel-bearbeiten" data-stapel="${esc(s.id)}" title="${esc(t("h_ln_stapel_bearbeiten"))}" aria-label="${esc(t("h_ln_stapel_bearbeiten"))}">✎</button>
      <button class="knopf klein leise gefahr" type="button" data-ln="stapel-loeschen" data-stapel="${esc(s.id)}" title="${esc(t("h_ln_stapel_loeschen"))}" aria-label="${esc(t("h_ln_stapel_loeschen"))}">🗑</button>` : ""}</div></li>`;
  }).join("");
  const quote = st.behaltensquote == null ? t("ln_quote_leer") : t("ln_quote", zahl(String(Math.round(st.behaltensquote * 1000) / 10)), st.behaltensquote_n);
  const statistik = `<p>${esc(t("ln_heute_gelernt", st.heute.gelernt, zahl(String(st.heute.minuten))))}</p>
    <h3 class="klein" style="margin:12px 0 0">${esc(t("ln_woche_titel"))}</h3>${lernWocheSVG(st.woche || [])}
    <h3 class="klein" style="margin:0 0 6px">${esc(t("ln_zustaende"))}</h3>${lernZustaendeHTML(st.zustaende || {})}<p>${esc(quote)}</p>
    ${st.problem ? `<p class="knopfzeile"><span>${esc(t("ln_problem", st.problem))}</span><button class="knopf klein" type="button" data-ln="problemkarten">${esc(t("ln_problem_knopf"))}</button></p>` : ""}`;
  return `${kachel}<div class="lern-raster">
    <section class="flaeche"><h2>${esc(t("ln_stapel_titel"))}</h2><ul class="lern-stapel-liste">${stapel}</ul>
      <button class="knopf" type="button" data-ln="stapel-neu" title="${esc(t("h_ln_stapel_neu"))}">＋ ${esc(t("ln_stapel_neu"))}</button></section>
    <section class="flaeche lern-stat"><h2>${esc(t("ln_stat_titel"))}</h2>${statistik}</section></div>
    <section class="flaeche lern-block"><h2>${esc(t("ln_einst_titel"))}</h2>${lernEinstHTML()}</section>
    <section class="flaeche lern-block"><h2>${esc(t("ln_daten_titel"))}</h2><div class="knopfzeile">
      <a class="knopf" href="/api/lernen-export" download title="${esc(t("h_ln_export"))}">⇩ ${esc(t("ln_export"))}</a>
      <button class="knopf" type="button" data-ln="import" title="${esc(t("h_ln_import"))}">⇧ ${esc(t("ln_import"))}</button>
      <input type="file" accept="application/json,.json" hidden data-ln-datei>
      <button class="knopf leise gefahr" type="button" data-ln="reset-frage">${esc(t("ln_reset"))}</button></div><div data-ln-reset></div></section>`;
}

/* ----- Lernsitzung ----- */
const lernRest = n => n && n.zaehler ? n.zaehler.neu + n.zaehler.lernen + n.zaehler.wiederholen : 0;
function lernStimme(code) {                                 // Vorlesen nur mit einer Stimme des Systems (offline) für die Sprache
  if (!window.speechSynthesis || !speechSynthesis.getVoices) return null;
  const ziel = code === "no" ? ["nb", "no", "nn"] : [code];
  return speechSynthesis.getVoices().find(v => v.localService !== false && ziel.includes(String(v.lang || "").toLowerCase().replace("_", "-").split("-")[0])) || null;
}
if (window.speechSynthesis && speechSynthesis.addEventListener) speechSynthesis.addEventListener("voiceschanged", () => { if (LS && LS.n.karte && ansicht() === "lernen") zeichneSitzung(); });
async function lernStart(stapel) {
  try {
    const n = await api(url("/api/lernen-karte", { stapel }));
    LS = { stapel, n, gezeigt: false, zeit: Date.now(), gelernt: 0, gesamt: lernRest(n), rueck: !!(LERN && LERN.rueckgaengig) };
    if (ansicht() !== "lernen") location.hash = "#lernen"; else zeichneSitzung();
  } catch (e) { if (toolFehlt(e)) return brauchtTool("lernen", () => lernStart(stapel)); fehlerToast(e); }
}
function lernKarteHTML(k) {
  const kk = S.karten.find(x => x.bild === k.bild) || { bild: k.bild, fit: "contain" };
  const bild = `<img class="lern-bild" alt="${esc(k.de || k.bild)}" data-seite="vorn" data-bild="${esc(k.bild)}" src="${vorschauUrl(kk, "vorn")}">`;
  const stimme = lernStimme(k.sprache) ? `<button type="button" class="knopf klein" data-ln="vorlesen" title="${esc(t("h_ln_vorlesen"))}" aria-label="${esc(t("h_ln_vorlesen"))}">🔊</button>` : "";
  const kopf = `<div class="lern-kopf-chip">${sprachChip(k.sprache, { aktuell: false })}${stimme}</div>`;
  const wort = `<div class="lern-wort" ${zsAttr(k.sprache)}>${esc(k.wort)}</div>`;
  const vorn = k.richtung === "r" ? `<p class="lern-frage">${esc(t("ln_frage_r"))}</p>${kopf}${wort}` : `<p class="lern-frage">${esc(t("ln_frage_v", zsName(k.sprache)))}</p>${bild}`;
  const zusatz = `${k.notiz ? `<div class="lern-notiz klein">${esc(k.notiz)}</div>` : ""}${k.problem ? `<div class="lern-problem"><p>${esc(t("ln_problem_hinweis"))}</p>
    <button class="knopf klein" type="button" data-ln="bearbeiten" data-bild="${esc(k.bild)}">${esc(t("ln_karte_bearbeiten"))}</button></div>` : ""}`;
  const hinten = LS.gezeigt ? (k.richtung === "r" ? `${bild}<div class="lern-de" lang="de">${esc(k.de)}</div>` : `${kopf}${wort}<div class="lern-de" lang="de">${esc(k.de)}</div>`) + zusatz : "";
  return `<div class="lern-karte${LS.gezeigt ? " gezeigt" : ""}" data-ln-karte${LS.gezeigt ? "" : ` role="button" tabindex="0" aria-label="${esc(t("ln_zeigen"))}"`}>
    <div class="lern-vorn">${vorn}</div><div class="lern-hinten" aria-live="polite">${hinten}</div></div>`;
}
function zeichneSitzung() {
  const el = $("#lern-inhalt"); if (!el || !LS) return;
  const n = LS.n, k = n.karte;
  if (!k) { el.innerHTML = lernFertigHTML(); return; }
  const rest = lernRest(n), gesamt = Math.max(LS.gesamt, LS.gelernt + rest), pro = gesamt ? Math.round(LS.gelernt * 100 / gesamt) : 0, z = n.zaehler;
  const noten = LS.gezeigt ? [1, 2, 3, 4].map(x => `<button class="knopf note n${x}" type="button" data-ln="note" data-note="${x}" title="${esc(t("h_ln_noten"))}">
      <b>${esc(t("ln_n" + x))}</b><span>${esc((k.vorschau_text || {})[x] || "")}</span><kbd>${x}</kbd></button>`).join("")
    : `<button class="knopf haupt gross" type="button" data-ln="zeigen" title="${esc(t("h_ln_zeigen"))}">${esc(t("ln_zeigen"))}</button>`;
  el.innerHTML = `<section class="lern-sitzung"><div class="lern-oben">
      <div class="fortschritt" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${pro}"><span style="width:${pro}%"></span></div>
      <span class="klein lern-zaehler">${esc(t("ln_zaehler", z.neu, z.lernen, z.wiederholen))}</span>
      <div class="knopfzeile"><button class="knopf klein" type="button" data-ln="rueck" title="${esc(t("h_ln_rueck"))}" aria-label="${esc(t("h_ln_rueck"))}"${LS.rueck ? "" : " disabled"}>↶</button>
      <button class="knopf klein leise" type="button" data-ln="beenden" title="${esc(t("h_ln_beenden"))}">✕ ${esc(t("ln_beenden"))}</button></div></div>
    ${lernKarteHTML(k)}<div class="lern-noten${LS.gezeigt ? "" : " einer"}">${noten}</div><p class="klein lern-tasten">${esc(t("ln_tasten"))}</p></section>`;
  const f = LS.gezeigt ? $('[data-note="3"]', el) : $('[data-ln="zeigen"]', el);
  if (f && !BERUEHRUNG) f.focus({ preventScroll: true });
}
function lernFertigHTML() {
  const n = LS.n, m = n.naechster_schritt ? Math.max(1, Math.ceil((n.naechster_schritt * 1000 - Date.now()) / 60000)) : 0;
  return `<section class="flaeche lern-fertig" aria-live="polite"><img src="/symbol.svg" alt=""><h2>${esc(t(LS.gelernt ? "ln_fertig_titel" : "ln_nichts_titel"))}</h2>
    <p>${esc(LS.gelernt ? t("ln_fertig_text", LS.gelernt) : t("ln_nichts_text"))}</p><p><b>${esc(t("ln_morgen", n.morgen || 0))}</b></p>
    ${m && m <= 24 * 60 ? `<p class="klein">${esc(t("ln_naechster", m))}</p>` : ""}
    <div class="knopfzeile">${LS.rueck ? `<button class="knopf leise" type="button" data-ln="rueck" title="${esc(t("h_ln_rueck"))}">↶ ${esc(t("ln_rueck"))}</button>` : ""}
    <button class="knopf haupt" type="button" data-ln="beenden">${esc(t("ln_zurueck_uebersicht"))}</button></div></section>`;
}
function lernZeigen() { if (!LS || !LS.n.karte || LS.gezeigt) return; LS.gezeigt = true; zeichneSitzung(); }
async function lernBewerten(note) {
  if (!LS || !LS.n.karte || !LS.gezeigt || LS.busy) return;
  LS.busy = true;
  const k = LS.n.karte;
  try {
    const r = await api("/api/lernen-bewerten", { methode: "POST", daten: { id: k.id, note, dauer_ms: Date.now() - LS.zeit, stapel: LS.stapel } });
    LS.gelernt++; LS.rueck = true; LS.gezeigt = false; LS.zeit = Date.now();
    LS.n = r.naechste || await api(url("/api/lernen-karte", { stapel: LS.stapel }));
  } catch (e) {
    if (toolFehlt(e)) { LS = null; return brauchtTool("lernen", lernAktiviert); }
    fehlerToast(e);
    if (e.status === 404) LS.n = await api(url("/api/lernen-karte", { stapel: "alle" })).catch(() => LS.n);
  } finally { if (LS) LS.busy = false; }
  if (ansicht() === "lernen") zeichneSitzung();
  lernSpaeter(); ladeKartenSpaeter();
}
async function lernRueck() {
  const stapel = LS ? LS.stapel : "alle";
  try {
    const r = await api("/api/lernen-rueckgaengig", { methode: "POST", daten: { stapel } });
    toast(t("ln_rueck_ok"));
    if (!LS) LS = { stapel, n: r.naechste, gezeigt: false, zeit: Date.now(), gelernt: 0, gesamt: lernRest(r.naechste), rueck: true };
    else { LS.n = r.naechste; LS.gezeigt = false; LS.zeit = Date.now(); LS.gelernt = Math.max(0, LS.gelernt - 1); }
    zeichneSitzung(); lernSpaeter(); ladeKartenSpaeter();
  } catch (e) { if (LS && e.status === 409) { LS.rueck = false; zeichneSitzung(); } fehlerToast(e); }
}
function lernBeenden() { LS = null; if (window.speechSynthesis) speechSynthesis.cancel(); zeichneLernen(); }
const ladeKartenSpaeter = entprellt(() => ladeKarten().then(() => { if (ansicht() === "karten") zeichneKarten(); }).catch(() => {}), 900);

$("#lern-inhalt").addEventListener("click", async e => {
  const karte = e.target.closest("[data-ln-karte]");
  const b = e.target.closest("[data-ln]");
  if (!b) { if (karte && LS && !LS.gezeigt) lernZeigen(); return; }
  const a = b.dataset.ln;
  if (a === "aktivieren") return brauchtTool("lernen", lernAktiviert);
  if (a === "lernen") return lernStart(b.dataset.stapel || "alle");
  if (a === "zeigen") return lernZeigen();
  if (a === "note") return lernBewerten(+b.dataset.note);
  if (a === "rueck") return lernRueck();
  if (a === "beenden") return lernBeenden();
  if (a === "bearbeiten") return oeffneEditor(b.dataset.bild);
  if (a === "vorlesen" && LS && LS.n.karte) {
    const k = LS.n.karte, v = lernStimme(k.sprache); if (!v) return;
    speechSynthesis.cancel(); const s = new SpeechSynthesisUtterance(k.wort); s.voice = v; s.lang = v.lang; speechSynthesis.speak(s); return;
  }
  if (a === "problemkarten") { S.lernFilter = "problem"; S.lernAuswahl = null; location.hash = "#karten"; return; }
  if (a === "stapel-neu") return lernStapelDialog();
  if (a === "stapel-bearbeiten") return lernStapelDialog(b.dataset.stapel);
  if (a === "stapel-loeschen") {
    const s = LERN && LERN.stapel.find(x => x.id === b.dataset.stapel); if (!s) return;
    try {
      LERN = await api("/api/lernen-stapel", { methode: "POST", daten: { aktion: "loeschen", id: s.id } }); lernZahl(); zeichneLernen();
      const kopie = { id: s.id, name: s.name, sprache: s.sprache, notiz: s.notiz, suche: s.suche, nur: s.nur, bilder: s.bilder };
      toast(t("ln_stapel_geloescht", s.name), { aktion: { label: t("rueckgaengig"), fn: () => lernStapelSpeichern(kopie).catch(fehlerToast) } });
    } catch (err) { fehlerToast(err); }
    return;
  }
  if (a === "import") return $("[data-ln-datei]").click();
  if (a === "reset-frage") {
    $("[data-ln-reset]").innerHTML = `<div class="lern-frage-reset"><p>${esc(t("ln_reset_frage"))}</p><button class="knopf haupt" type="button" data-ln="reset-nein">${esc(t("ln_reset_nein"))}</button>
      <button class="knopf gefahr-voll" type="button" data-ln="reset-ja">${esc(t("ln_reset_ja"))}</button></div>`; return;
  }
  if (a === "reset-nein") { $("[data-ln-reset]").innerHTML = ""; return; }
  if (a === "reset-ja") {
    try { const r = await api("/api/lernen-zuruecksetzen", { methode: "POST", daten: { alle: true } }); LERN = r; toast(t("ln_reset_ok", r.zurueckgesetzt)); }
    catch (err) { fehlerToast(err); }
    lernZahl(); zeichneLernen(); ladeKartenSpaeter();
  }
});
$("#lern-inhalt").addEventListener("keydown", e => {             // Karte per Tastatur umdrehen (Enter/Leertaste auf der Karte)
  if ((e.key === "Enter" || e.key === " ") && e.target.matches("[data-ln-karte]")) { e.preventDefault(); lernZeigen(); }
});
$("#lern-inhalt").addEventListener("input", e => {
  if (e.target.dataset.le === "behaltensquote") { const w = $("[data-le-wert]"); if (w) w.textContent = e.target.value + " %"; }
});
$("#lern-inhalt").addEventListener("submit", async e => {
  if (!e.target.matches('[data-ln-form="einst"]')) return;
  e.preventDefault();
  const werte = {};
  $$("[data-le]", e.target).forEach(i => { werte[i.dataset.le] = i.dataset.le === "richtung" || i.dataset.le === "sprache" ? i.value : +i.value; });
  try { LERN = await api("/api/lernen-einstellungen", { methode: "POST", daten: { werte } }); toast(t("ln_gespeichert")); lernZahl(); zeichneLernen(); ladeKartenSpaeter(); }
  catch (err) { fehlerToast(err); }
});
$("#lern-inhalt").addEventListener("change", async e => {
  if (!e.target.matches("[data-ln-datei]")) return;
  const datei = e.target.files[0]; e.target.value = ""; if (!datei) return;
  let roh = null; try { roh = JSON.parse(await datei.text()); } catch (err) { roh = null; }
  try {
    const r = await api("/api/lernen-import", { methode: "POST", daten: { lernstand: roh } });
    LERN = r; toast(t("ln_importiert", r.importiert.karten, r.importiert.stapel)); lernZahl(); zeichneLernen(); ladeKartenSpaeter();
  } catch (err) { fehlerToast(err); }
});
// Tastatur in der Sitzung: Leertaste/Enter = Antwort zeigen, 1–4 = bewerten, Strg+Z = rückgängig, Esc = beenden
document.addEventListener("keydown", e => {
  if (ansicht() !== "lernen" || !LS || offenerDialog()) return;
  const ziel = e.target.closest ? e.target.closest("input, textarea, select, [contenteditable]") : null; if (ziel) return;
  if ((e.ctrlKey || e.metaKey) && !e.altKey && e.key.toLowerCase() === "z") { e.preventDefault(); return lernRueck(); }
  if (e.ctrlKey || e.metaKey || e.altKey) return;
  if (e.key === "Escape") return lernBeenden();
  if (!LS.n.karte) return;
  const aufKnopf = e.target.closest && e.target.closest("button, a");
  if (!LS.gezeigt && (e.key === " " || e.key === "Enter") && !aufKnopf) { e.preventDefault(); return lernZeigen(); }
  if (LS.gezeigt && /^[1-4]$/.test(e.key)) { e.preventDefault(); return lernBewerten(+e.key); }
});
// Wischen (nur Touch, nur als Zusatz zu den Knöpfen; ↶ nimmt es zurück): rechts = Gut, links = Nochmal
$("#lern-inhalt").addEventListener("pointerdown", e => {
  if (e.pointerType !== "touch" || !LS || !LS.gezeigt || !e.target.closest("[data-ln-karte]")) return;
  const x0 = e.clientX, y0 = e.clientY;
  const los = ev => {
    document.removeEventListener("pointerup", los); document.removeEventListener("pointercancel", los);
    const dx = ev.clientX - x0, dy = ev.clientY - y0;
    if (ev.type === "pointerup" && Math.abs(dx) > 90 && Math.abs(dx) > 2 * Math.abs(dy)) lernBewerten(dx > 0 ? 3 : 1);
  };
  document.addEventListener("pointerup", los); document.addEventListener("pointercancel", los);
});

/* ----- Stapel anlegen/bearbeiten (Filter + Häkchen-Auswahl) ----- */
async function lernStapelSpeichern(stapel) {
  const r = await api("/api/lernen-stapel", { methode: "POST", daten: { aktion: "speichern", stapel } });
  LERN = r; lernZahl(); if (ansicht() === "lernen" && !LS) zeichneLernen();
  return r;
}
async function lernStapelDialog(sid = null, bilder = null) {
  if (!LERN) await ladeLernen(true); if (!LERN) return;
  const s = sid ? LERN.stapel.find(x => x.id === sid) : null;
  LERN_DLG = { id: s ? s.id : "", name: s ? s.name : "", sprache: s ? s.sprache : "", notiz: s ? s.notiz : "", suche: s ? s.suche : "", nur: s ? s.nur : "",
    bilder: new Set(bilder || (s && s.bilder) || []), auswahl: !!(bilder || (s && s.bilder)), vonAuswahl: bilder ? [...bilder] : null };
  zeichneStapelDialog(); $("#lern-fenster").hidden = false;
  setTimeout(() => { const i = $("#ln-st-name"); if (i) i.focus(); }, 0);
}
function zeichneStapelDialog() {
  const d = LERN_DLG; if (!d || !LERN) return;
  const eigene = LERN.stapel.filter(s => s.id !== "alle" && s.id !== LERN_AUSWAHL_ID);
  $("#lern-dlg-titel").textContent = t(d.id && !d.vonAuswahl ? "ln_st_titel_bearbeiten" : "ln_st_titel_neu");
  const karten = S.karten.filter(k => k.existiert && k.aktiv);
  const sel = (feld, werte, akt) => `<select data-ls="${feld}">${werte.map(([v, txt]) => `<option value="${esc(v)}"${String(akt) === String(v) ? " selected" : ""}>${esc(txt)}</option>`).join("")}</select>`;
  $("#lern-dlg-inhalt").innerHTML = `<form class="lern-stapel-form" data-ln-form="stapel">
    ${d.vonAuswahl && eigene.length ? `<label class="f"><span>${esc(t("ln_st_ziel"))}</span>${sel("ziel", [["", t("ln_st_ziel_neu")], ...eigene.map(s => [s.id, s.name])], d.id)}</label>` : ""}
    <label class="f"><span>${esc(t("ln_st_name"))}</span><input id="ln-st-name" data-ls="name" value="${esc(d.name)}" maxlength="60" placeholder="${esc(t("ln_st_name_ph"))}" autocomplete="off"></label>
    <div class="zwei"><label class="f"><span>${esc(t("ln_st_notiz"))}</span><input data-ls="notiz" value="${esc(d.notiz)}" maxlength="60" autocomplete="off"></label>
      <label class="f"><span>${esc(t("ln_st_suche"))}</span><input data-ls="suche" value="${esc(d.suche)}" maxlength="60" autocomplete="off"></label></div>
    <div class="zwei">${zsMehrere() ? `<label class="f"><span>${esc(t("ln_sprache"))}</span>${sel("sprache", [["", t("ln_sprache_auto")], ...ZS.installiert.map(c => [c, zsName(c)])], d.sprache)}</label>` : ""}
      <label class="f"><span>${esc(t("ln_st_nur"))}</span>${sel("nur", ["", "neu", "faellig", "problem"].map(v => [v, t("ln_nur_" + v)]), d.nur)}</label></div>
    <label class="schalter"><input type="checkbox" data-ls="auswahl"${d.auswahl ? " checked" : ""}><span class="spur"></span><span>${esc(t("ln_st_auswahl"))}</span></label>
    <div data-ls-raster${d.auswahl ? "" : " hidden"}><div class="knopfzeile"><span class="klein" data-ls-zahl>${esc(t("ln_st_auswahl_n", d.bilder.size))}</span>
      <button type="button" class="knopf klein" data-ls-alle="an">${esc(t("ln_st_alle_an"))}</button><button type="button" class="knopf klein leise" data-ls-alle="aus">${esc(t("ln_st_alle_aus"))}</button></div>
      <div class="lern-wahl-raster">${karten.map(k => `<label class="lern-wahl-karte"><input type="checkbox" data-ls-bild="${esc(k.bild)}"${d.bilder.has(k.bild) ? " checked" : ""}>
        <img loading="lazy" alt="" data-seite="vorn" data-bild="${esc(k.bild)}" src="${vorschauUrl(k, "vorn")}"><span>${esc(k.de || k.bild)}</span></label>`).join("")}</div></div>
    <div class="knopfzeile abstand"><div class="rechts"><button type="button" class="knopf leise" data-zu>${esc(t("abbrechen"))}</button>
      <button type="submit" class="knopf haupt">${esc(t("ln_st_speichern"))}</button></div></div></form>`;
}
$("#lern-dlg-inhalt").addEventListener("input", e => {
  const d = LERN_DLG, f = e.target.dataset.ls; if (!d || !f) return;
  if (["name", "notiz", "suche"].includes(f)) d[f] = e.target.value;
});
$("#lern-dlg-inhalt").addEventListener("change", e => {
  const d = LERN_DLG; if (!d) return;
  const f = e.target.dataset.ls;
  if (f === "sprache" || f === "nur") d[f] = e.target.value;
  if (f === "auswahl") { d.auswahl = e.target.checked; $("[data-ls-raster]").hidden = !d.auswahl; }
  if (f === "ziel") {                                          // zu einem vorhandenen Stapel: dessen Felder + Auswahl dazu
    const s = LERN.stapel.find(x => x.id === e.target.value);
    Object.assign(d, s ? { id: s.id, name: s.name, sprache: s.sprache, notiz: s.notiz, suche: s.suche, nur: s.nur } : { id: "", name: "" });
    d.bilder = new Set([...(d.vonAuswahl || []), ...((s && s.bilder) || [])]); d.auswahl = true;
    zeichneStapelDialog();
  }
  if (e.target.dataset.lsBild) { e.target.checked ? d.bilder.add(e.target.dataset.lsBild) : d.bilder.delete(e.target.dataset.lsBild); $("[data-ls-zahl]").textContent = t("ln_st_auswahl_n", d.bilder.size); }
});
$("#lern-dlg-inhalt").addEventListener("click", e => {
  const b = e.target.closest("[data-ls-alle]"), d = LERN_DLG; if (!b || !d) return;
  $$("[data-ls-bild]").forEach(c => { c.checked = b.dataset.lsAlle === "an"; c.checked ? d.bilder.add(c.dataset.lsBild) : d.bilder.delete(c.dataset.lsBild); });
  $("[data-ls-zahl]").textContent = t("ln_st_auswahl_n", d.bilder.size);
});
$("#lern-dlg-inhalt").addEventListener("submit", async e => {
  e.preventDefault();
  const d = LERN_DLG; if (!d) return;
  if (d.auswahl && !d.bilder.size) return toast(t("ln_auswahl_leer"), { fehler: true });
  const stapel = { name: d.name.trim(), sprache: d.sprache, notiz: d.notiz, suche: d.suche, nur: d.nur, bilder: d.auswahl ? [...d.bilder] : null };
  if (d.id) stapel.id = d.id;
  try {
    await lernStapelSpeichern(stapel);
    toast(t("ln_st_gespeichert", stapel.name)); LERN_DLG = null; $("#lern-fenster").hidden = true;
    if (d.vonAuswahl) { S.lernAuswahl = null; zeichneKarten(); }
  } catch (err) { fehlerToast(err); }
});

/* ----- Meine Karten: Lernstand je Karte, Filter, Auswahl → Jetzt lernen / Zum Stapel ----- */
const LERN_FILTER = ["", "faellig", "neu", "sicher", "problem"];
function lernPasst(k, f = S.lernFilter) {
  if (!f) return true;
  const l = k.lernen; if (!l) return false;
  if (f === "faellig") return l.zustand !== "neu" && l.faellig_in != null && l.faellig_in <= 0;
  if (f === "problem") return !!l.problem;
  return l.zustand === f;
}
function lernMarke(k) {
  const l = k.lernen; if (!l) return "";
  return `<span class="lern-marke z-${esc(l.zustand)}${l.problem ? " problem" : ""}" title="${esc(t("h_ln_marke", l.anzahl, l.faellig_in))}"><i aria-hidden="true"></i>${esc(t("ln_z_" + l.zustand))}${l.problem ? " · " + esc(t("ln_problem_kurz")) : ""}</span>`;
}
function lernLeisteHTML() {
  if (!S.karten.some(k => k.lernen)) { S.lernFilter = ""; S.lernAuswahl = null; return ""; }
  return `<div class="leiste"><div class="segmente" role="radiogroup" aria-label="${esc(t("ln_filter"))}">${LERN_FILTER.map(f => `<label><input type="radio" name="lernfilter" value="${f}"${S.lernFilter === f ? " checked" : ""}>
    <span>${esc(t("ln_filter_" + (f || "alle")))} (${S.karten.filter(k => lernPasst(k, f)).length})</span></label>`).join("")}</div>
    <button class="knopf klein${S.lernAuswahl ? " dunkel" : ""}" type="button" data-ln-k="auswahl" aria-pressed="${!!S.lernAuswahl}" title="${esc(t("h_ln_auswahl"))}">☑ ${esc(t("ln_auswahl"))}</button></div>`;
}
function zeichneAuswahlLeiste() {
  const el = $("#karten-auswahl"); if (!el) return;
  el.hidden = !S.lernAuswahl; if (!S.lernAuswahl) { el.innerHTML = ""; return; }
  el.innerHTML = `<b>${esc(t("ln_auswahl_n", S.lernAuswahl.size))}</b><button class="knopf haupt" type="button" data-ln-k="jetzt">🎓 ${esc(t("ln_jetzt_lernen"))}</button>
    <button class="knopf" type="button" data-ln-k="stapel">${esc(t("ln_zum_stapel"))}</button><button class="knopf leise" type="button" data-ln-k="fertig">${esc(t("ln_auswahl_fertig"))}</button>`;
}
$("#karten-lernleiste").addEventListener("change", e => { if (e.target.name === "lernfilter") { S.lernFilter = e.target.value; zeichneKarten(); } });
document.addEventListener("click", async e => {
  const b = e.target.closest("[data-ln-k]"); if (!b) return;
  const a = b.dataset.lnK;
  if (a === "auswahl") { S.lernAuswahl = S.lernAuswahl ? null : new Set(); return zeichneKarten(); }
  if (a === "fertig") { S.lernAuswahl = null; return zeichneKarten(); }
  if (!S.lernAuswahl || !S.lernAuswahl.size) return toast(t("ln_auswahl_leer"), { fehler: true });
  if (a === "stapel") return lernStapelDialog(null, [...S.lernAuswahl]);
  if (a === "jetzt") {
    try {
      await lernStapelSpeichern({ id: LERN_AUSWAHL_ID, name: t("ln_auswahl_stapel"), bilder: [...S.lernAuswahl] });
      S.lernAuswahl = null; zeichneAuswahlLeiste(); lernStart(LERN_AUSWAHL_ID);
    } catch (err) { if (toolFehlt(err)) return brauchtTool("lernen", lernAktiviert); fehlerToast(err); }
  }
});
// Editor und Tabelle: Hinweis, bevor eine Änderung den Lernstand einer Karte zurücksetzt (die Meldung danach kommt vom Server)
$("#editor-liste").addEventListener("input", e => {
  const el = e.target.closest(".editor"); if (!el) return;
  const h = $('[data-teil="lern-hinweis"]', el), k = S.karten.find(x => x.bild === el.dataset.bild); if (!h || !k) return;
  const wert = s => { const i = $(s, el); return i ? i.value : ""; };
  const rs = $$("input[data-rs]", el).some(i => i.value !== String((k.rueckseiten || {})[i.dataset.rs] || ""));
  h.hidden = !(wert('input[data-k="de"]') !== (k.de || "") || wert('input[data-k="es"]') !== (k.es || "") || rs);
});
$("#tabelle").addEventListener("input", e => {
  if (!e.target.matches('.zelle-eingabe[data-feld="de"], .zelle-eingabe[data-feld="es"]')) return;
  const tr = e.target.closest("tr[data-bild]"), k = tr && S.karten.find(x => x.bild === tr.dataset.bild);
  const m = tr && $('[data-teil="meldung"]', tr);
  if (!k || !k.lernen || !k.lernen.anzahl || !m || m.classList.contains("fehler")) return;
  m.textContent = "🎓 " + t("ln_hinweis_speichern"); m.className = "zellen-meldung lern";
});

/* ===================== Handy-App (Web-App) + untere App-Navigation =====================
   AM_APP: Diese Seite läuft als installierbare Web-App – Python (Pyodide) rechnet im Web-Worker, app.js leitet /api/… dorthin
   (bau_webapp.py). Die untere Navigation (Karten · Neu · Lernen · Drucken · Mehr) erscheint in der App bzw. am Touch-Gerät
   bis 860 px; „Mehr“ öffnet ein Blatt mit den übrigen Bereichen und den App-Aktionen (Installieren, Sicherung). */
const APP_GRUPPEN = { karten: ["karten"], neu: ["bild", "beschriften", "ideen"], lernen: ["lernen"], drucken: ["erzeugen", "pruefen"] };
const MEHR_ZIELE = [["tabelle", "☰", "nav_tabelle", "zahl-tabelle"], ["verbesserung", "✦", "nav_verbesserung"], ["beschriften", "2", "nav_beschriften", "zahl-offen"],
  ["ideen", "✎", "nav_ideen", "zahl-ideen"], ["pruefen", "4", "nav_pruefen"], ["werkzeuge", "⚙", "nav_werkzeuge"], ["hilfe", "?", "nav_hilfe"],
  ["deinstallieren", "⏏", "nav_deinstallieren"]];
const IOS = /iPhone|iPad|iPod/.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
const alsAppGestartet = () => !!((window.matchMedia && matchMedia("(display-mode: standalone)").matches) || navigator.standalone === true);
let INSTALL = null, APP_UPDATE = false, APP_DATEI = null, APP_URL = null, APP_NACH_ZURUECK = null;
function appNaviAktuell() {
  const name = ansicht(), gruppe = Object.keys(APP_GRUPPEN).find(g => APP_GRUPPEN[g].includes(name)) || "mehr";
  $$("#app-navi [data-app]").forEach(a => a.dataset.app === gruppe ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current"));
}
function appNaviZahlen() {
  const wert = id => { const el = $("#" + id); return el && !el.hidden ? +el.textContent || 0 : 0; };
  const setze = (id, n) => { const el = $("#" + id); if (el) { el.hidden = !n; el.textContent = n; } };
  setze("app-zahl-neu", wert("zahl-bild") + wert("zahl-offen"));
  setze("app-zahl-lernen", wert("zahl-lernen"));
  const mehr = $("#app-zahl-mehr"); if (mehr) mehr.hidden = !(APP_UPDATE || wert("zahl-tabelle") || wert("zahl-ideen"));
}
function appAdresse() { return (S.status && S.status.web_adresse) || ""; }
// Download-Seite für den Rechner (GitHub Pages, gleiche Adresse + download/), in der gewählten Sprache
function downloadAdresse() { const a = appAdresse(); return a ? a + "download/#" + S.sprache : ""; }
function appTipp() {                                            // Prüfen & drucken: Hinweis auf die Handy-App (am Rechner/Handy-Zugang)
  return !AM_APP && appAdresse() ? `<div class="knopfzeile abstand app-tipp"><span class="klein">📲 ${esc(t("pr_app_tipp"))}</span>
    <button class="knopf" type="button" data-app-aktion="zur-app">${esc(t("app_als_app"))}</button></div>` : "";
}
function appInstallierbar() { return AM_APP && !alsAppGestartet(); }
function zeichneMehr() {
  const name = ansicht();
  const liste = MEHR_ZIELE.filter(([a]) => !(a === "deinstallieren" && AM_HANDY)).map(([a, s, k, z]) => {
    const n = z && $("#" + z) && !$("#" + z).hidden ? $("#" + z).textContent : "";
    return `<a href="#${a}" data-mehr${a === name ? ' aria-current="page"' : ""}><span class="symbol" aria-hidden="true">${s}</span><span>${esc(t(k))}</span>${n ? `<span class="zahl">${esc(n)}</span>` : ""}</a>`;
  }).join("");
  const app = [];
  if (APP_UPDATE) app.push(`<button class="knopf haupt" type="button" data-app-aktion="update">🆕 ${esc(t("app_update_knopf"))}</button>`);
  if (appInstallierbar()) app.push(`<button class="knopf${APP_UPDATE ? "" : " haupt"}" type="button" data-app-aktion="installieren">📲 ${esc(t("app_installieren"))}</button>`);
  if (AM_APP) app.push(`<button class="knopf" type="button" data-app-aktion="sicherung">💾 ${esc(t("app_sicherung"))}</button>`);
  if (!AM_APP && AM_HANDY && appAdresse()) app.push(`<button class="knopf" type="button" data-app-aktion="zur-app">📲 ${esc(t("app_als_app"))}</button>`);
  if (AM_APP && downloadAdresse()) app.push(`<a class="knopf" href="${esc(downloadAdresse())}" target="_blank" rel="noopener">💻 ${esc(t("app_rechner"))}</a>`);
  $("#mehr-inhalt").innerHTML = `<nav class="mehr-liste" aria-label="${esc(t("bereiche"))}">${liste}</nav>${app.length ? `<div class="mehr-app">${app.join("")}</div>` : ""}`;
}
function oeffneMehr() { zeichneMehr(); $("#mehr-fenster").hidden = false; }
function oeffneAppFenster(titel, html) { $("#app-titel").textContent = titel; $("#app-inhalt").innerHTML = html; $("#app-fenster").hidden = false; }
function appHinweisSpaeter() { try { return +(localStorage.getItem("mgd-app-hinweis") || 0) > Date.now(); } catch (e) { return false; } }
function zeichneAppHinweis() {
  const el = $("#app-hinweis"); if (!el) return;
  let text = "", aktion = "";
  if (!appHinweisSpaeter() && appInstallierbar()) { text = t("app_hinweis"); aktion = `<button class="knopf haupt" type="button" data-app-aktion="installieren">${esc(t("app_installieren"))}</button>`; }
  else if (!appHinweisSpaeter() && !AM_APP && AM_HANDY && appAdresse()) { text = t("app_handy_hinweis"); aktion = `<button class="knopf haupt" type="button" data-app-aktion="zur-app">${esc(t("app_als_app"))}</button>`; }
  el.innerHTML = text ? `<div class="banner app-banner"><span>📲 ${esc(text)}</span><div class="knopfzeile">${aktion}
    <button class="knopf leise" type="button" data-app-aktion="spaeter">${esc(t("app_spaeter"))}</button></div></div>` : "";
}
// Gezeichnete Skizzen für die Installations-Schritte (Strichzeichnung in Schriftfarbe)
const SKIZZE_RAHMEN = '<rect x="2" y="2" width="40" height="40" rx="10" stroke-width="1.4"/>';
const skizze = innen => `<svg viewBox="0 0 44 44" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">${SKIZZE_RAHMEN}${innen}</svg>`;
const SKIZZEN = {
  teilen: skizze('<path d="M22 9v17M16 15l6-6 6 6"/><path d="M17 20h-4v14h18V20h-4"/>'),
  startseite: skizze('<rect x="12" y="12" width="20" height="20" rx="5"/><path d="M22 17v10M17 22h10"/>'),
  fertig: skizze('<path d="M13 23l6 6 12-13"/>'),
  menue: skizze('<circle cx="22" cy="13" r="1.6" fill="currentColor"/><circle cx="22" cy="22" r="1.6" fill="currentColor"/><circle cx="22" cy="31" r="1.6" fill="currentColor"/>'),
};
function appInstallHTML() {
  const schritte = IOS ? [["teilen", "app_ios_1"], ["startseite", "app_ios_2"], ["fertig", "app_ios_3"]]
    : [["menue", "app_and_1"], ["startseite", "app_and_2"], ["fertig", "app_and_3"]];
  return `<p>${esc(t("app_install_text"))}</p><ol class="app-schritte">${schritte.map(([s, k]) => `<li>${SKIZZEN[s]}<span>${esc(t(k))}</span></li>`).join("")}</ol>
    <p class="klein">${esc(t(IOS ? "app_ios_hinweis" : "app_and_hinweis"))}</p>`;
}
async function appInstallieren() {
  schliesseDialog($("#mehr-fenster"));
  const p = INSTALL || window.MGD_INSTALL;
  if (p) {                                                      // Android/Chrome: echter Installieren-Dialog
    INSTALL = window.MGD_INSTALL = null;
    try { await p.prompt(); const r = await p.userChoice; if (r && r.outcome === "accepted") toast(t("app_installiert")); }
    catch (e) { oeffneAppFenster(t("app_install_titel"), appInstallHTML()); }
    return zeichneAppHinweis();
  }
  oeffneAppFenster(t("app_install_titel"), appInstallHTML());     // iPhone/iPad bzw. ohne Angebot des Browsers: Schritte
}
function oeffneZurApp() {
  const adr = appAdresse(); if (!adr) return;
  oeffneAppFenster(t("app_als_app"), `<p>${esc(t("app_zur_app_text"))}</p><div class="lan-an"><div class="lan-qr">${qrSvg(adr)}</div><div class="lan-adresse">${esc(adr)}</div></div>
    <div class="knopfzeile abstand"><a class="knopf haupt" href="${esc(adr)}" target="_blank" rel="noopener">${esc(t("app_zur_app_knopf"))}</a></div>`);
}
function oeffneAppSicherung() {
  oeffneAppFenster(t("app_sicherung"), `<p>${esc(t("app_sicherung_text"))}</p><div class="app-speicher" id="app-speicher"></div>
    <div class="knopfzeile"><a class="knopf haupt" href="${url("/api/app-sicherung")}" download>💾 ${esc(t("app_sichern"))}</a>
      <label class="knopf">📥 ${esc(t("app_einspielen"))}<input type="file" accept=".zip,application/zip" data-app-einspielen></label></div>
    <p class="klein">${esc(t("app_einspielen_text"))}</p><div id="app-frage"></div>
    <h3>⇅ ${esc(t("app_vom_rechner"))}</h3><p class="klein">${esc(t("app_vom_rechner_text"))}</p>
    <div class="knopfzeile"><button class="knopf" type="button" data-app-aktion="vom-rechner">${esc(t("ie_knopf"))}</button></div>
    <p class="klein">${esc(t(IOS ? "app_ios_hinweis" : "app_sicherung_tipp"))}</p>`);
  appSpeicherZeigen();
}
async function appSpeicherZeigen() {
  const el = $("#app-speicher"); if (!el || !navigator.storage) return;
  try {
    const est = navigator.storage.estimate ? await navigator.storage.estimate() : null;
    const dauer = navigator.storage.persisted ? await navigator.storage.persisted() : null;
    el.innerHTML = (est && est.usage != null ? `<span>${esc(t("app_belegt", zahl((est.usage / 1048576).toFixed(1))))}</span>` : "")
      + (dauer == null ? "" : `<span>${esc(t(dauer ? "app_dauerhaft_ja" : "app_dauerhaft_nein"))}</span>`);
  } catch (e) { /* ohne Angaben */ }
}
// Ergebnisse in der App: teilen (Drucken, Mail, „Dateien“) oder speichern – app.js holt die Datei und ruft das hier auf
function appDateiAnbieten(blob, name) {
  if (APP_URL) URL.revokeObjectURL(APP_URL);
  APP_URL = URL.createObjectURL(blob);
  APP_DATEI = new File([blob], name, { type: blob.type || "application/octet-stream" });
  const teilbar = !!(navigator.canShare && navigator.canShare({ files: [APP_DATEI] }));
  oeffneAppFenster(name, `<div class="app-datei">${/^image\//.test(blob.type) ? `<img src="${APP_URL}" alt="">` : `<p>${esc(t("app_datei_text"))}</p>`}
    <div class="knopfzeile">${teilbar ? `<button class="knopf haupt" type="button" data-app-aktion="teilen">📤 ${esc(t("app_teilen"))}</button>` : ""}
      <a class="knopf${teilbar ? "" : " haupt"}" href="${APP_URL}" download="${esc(name)}">⬇ ${esc(t("app_speichern"))}</a></div></div>`);
}
function appUpdateMelden() {
  if (APP_UPDATE) return;
  APP_UPDATE = true; appNaviZahlen();
  toast(t("app_update"), { aktion: { label: t("app_update_knopf"), fn: appNeuLaden } });
}
function appNeuLaden() { if (window.MGD_NEU_LADEN) window.MGD_NEU_LADEN(); else location.reload(); }
window.addEventListener("mgd-update", appUpdateMelden);
window.addEventListener("mgd-install", () => { INSTALL = window.MGD_INSTALL || null; if (S.gestartet) zeichneAppHinweis(); });
window.addEventListener("appinstalled", () => { INSTALL = window.MGD_INSTALL = null; zeichneAppHinweis(); toast(t("app_installiert")); });
document.addEventListener("click", async e => {
  const ziel = e.target.closest("[data-mehr]");
  if (ziel) {                                                   // Bereich aus „Mehr“: Blatt zu, dann dorthin
    e.preventDefault(); const h = ziel.getAttribute("href");
    if (history.state && history.state.mgdFenster === "mehr-fenster") APP_NACH_ZURUECK = () => { location.hash = h; };
    schliesseDialog($("#mehr-fenster")); if (!APP_NACH_ZURUECK) location.hash = h;
    return;
  }
  if (e.target.closest('#app-navi [data-app="mehr"]')) return oeffneMehr();
  const b = e.target.closest("[data-app-aktion]"); if (!b) return;
  const a = b.dataset.appAktion;
  if (a === "spaeter") { try { localStorage.setItem("mgd-app-hinweis", String(Date.now() + 14 * 864e5)); } catch (err) { /* nur jetzt */ } $("#app-hinweis").innerHTML = ""; return; }
  if (a === "update") return appNeuLaden();
  if (a === "installieren") return appInstallieren();
  if (a === "sicherung") { schliesseDialog($("#mehr-fenster")); return oeffneAppSicherung(); }
  if (a === "zur-app") { schliesseDialog($("#mehr-fenster")); return oeffneZurApp(); }
  if (a === "vom-rechner") { schliesseDialog($("#app-fenster")); return oeffneDialog("import-export", { vorwahl: "alles" }); }
  if (a === "teilen" && APP_DATEI) { try { await navigator.share({ files: [APP_DATEI], title: APP_DATEI.name }); } catch (err) { if (err.name !== "AbortError") fehlerToast(err); } return; }
  if (a === "einspielen-ja" && APP_SICHERUNG) {
    b.disabled = true;
    try { const r = await api("/api/app-sicherung", { methode: "POST", roh: APP_SICHERUNG }); toast(r.meldung); setTimeout(() => location.reload(), 1500); }
    catch (err) { fehlerToast(err); b.disabled = false; }
    return;
  }
  if (a === "einspielen-nein") { APP_SICHERUNG = null; $("#app-frage").innerHTML = ""; }
});
let APP_SICHERUNG = null;
document.addEventListener("change", e => {
  const inp = e.target.closest("[data-app-einspielen]"); if (!inp || !inp.files || !inp.files[0]) return;
  APP_SICHERUNG = inp.files[0]; inp.value = "";
  $("#app-frage").innerHTML = `<div class="app-frage"><span>${esc(t("app_einspielen_frage", APP_SICHERUNG.name))}</span><div class="knopfzeile">
    <button class="knopf haupt" type="button" data-app-aktion="einspielen-ja">${esc(t("app_einspielen_ja"))}</button>
    <button class="knopf leise" type="button" data-app-aktion="einspielen-nein">${esc(t("abbrechen"))}</button></div></div>`;
});
// Zurück-Geste/-Taste (Android, App): schließt zuerst das oberste Fenster – sonst geht es wie gewohnt über den Hash-Verlauf
// zurück. Jedes geöffnete Fenster bekommt einen Verlaufseintrag; wird es in der Seite geschlossen, nimmt die Seite ihn zurück.
if (AM_APP || BERUEHRUNG) {
  let popIgnorieren = false;
  const beobachter = new MutationObserver(liste => liste.forEach(m => {
    const el = m.target, oben = history.state && history.state.mgdFenster === el.id;
    if (!el.hidden) { if (!oben) history.pushState({ mgdFenster: el.id }, ""); }
    else if (el.dataset.zurueck) delete el.dataset.zurueck;       // schon über „Zurück“ geschlossen
    else if (oben) { popIgnorieren = true; history.back(); }
  }));
  $$("[data-dialogfenster]").forEach(el => beobachter.observe(el, { attributes: true, attributeFilter: ["hidden"] }));
  window.addEventListener("popstate", () => {
    if (popIgnorieren) { popIgnorieren = false; const f = APP_NACH_ZURUECK; APP_NACH_ZURUECK = null; if (f) f(); return; }
    const d = offenerDialog(); if (!d) return;
    if (d.hasAttribute("data-fest")) { history.pushState({ mgdFenster: d.id }, ""); return; }
    d.dataset.zurueck = "1"; schliesseDialog(d);
  });
}

async function start() {
  if (AM_APP) $("#verbindung").dataset.t = "verbindung_app";
  uebersetze();
  try {
    await Promise.all([ladeOptionen(), ladeKarten(), ladeWerkzeuge(), ladeStatus(), ladeEntwuerfe(), ladeGans(), ladeUe(), ladeTools()]);
    api("/api/ergebnisse").then(d => { S.namen = d.namen; }).catch(() => {});
    const laufend = await api(url("/api/lauf", { ab: 0 }));
    if (laufend && laufend.id) { if (laufend.laeuft) starteBeobachtung(laufend); else { S.lauf = laufend; S.laufAb = laufend.anzahl; S.laufGemeldet.add(laufend.id); } }
  } catch (e) { fehlerToast(e); }
  if (lernDa()) await ladeLernen();
  zeige(); S.gestartet = true;
  nachStart();
  setInterval(() => { ladeStatus(); laufWiederaufnehmen(); }, 20000);
}
start();
