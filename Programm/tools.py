#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ME GOOS-TA DEUTSCH – Tools (optionale Funktionen)                    Version 2.3 (22.10.2026)
=============================================================================================
Ein Tool ist eine optionale Funktion, die nicht vorinstalliert ist (spart Platz). Reiter und Knöpfe bleiben immer
sichtbar; wer ein fehlendes Tool nutzen will, wird gefragt, das Tool lädt über die Warteschlange (gans_ui) und die
Aktion geht danach weiter. Deinstallieren löscht nur die Dateien des Tools – danach ist es wieder installierbar.

  bildverbesserung  Real-ESRGAN x4plus (+ x2plus als schnellere Variante)   Programm/modelle + Kopie Daten/modelle
  uebersetzung      Zustimmung + Dienstwahl (nichts Großes zu laden)        Daten/uebersetzung.json + Zwischenspeicher
  ki-bild           Segmind Vega + VegaRT (~3,5 GB)                         Daten/modelle/ki-bild
  sprachen          je Sprache ein Teil (Schriften, ggf. uharfbuzz; sprachen.py) Daten/sprachen/<code>
  lernen            Aktivierung (FSRS in reinem Python, lernen.py)           lernstand.json neben karten.csv

Download-Tools gelten über ihre Dateien als installiert (vorhandene Modelle aus 1.6 zählen also gleich mit),
Aktivierungs-Tools über tools.json im Datenordner bzw. die schon erteilte Zustimmung. tools.json merkt außerdem, ob
die Erstabfrage schon gestellt wurde, und welche Tools nur „abgemeldet“ sind (Löschschutz, siehe deinstalliere()).
Programmcode wird nie nachgeladen – nur Modelle und Daten mit Prüfsumme. Texte als L(de, en, es); die Oberfläche
(gans_ui.tools_info) wählt die Sprache. Selbsttest: test_erweiterungen.py (Abschnitt E22).
"""
from __future__ import annotations

import os
import shutil
import sys
import threading
import time
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import ki_modelle  # noqa: E402
import uebersetzer  # noqa: E402

try:
    import ki_bild  # noqa: E402
except ImportError:                                  # Testkopie ohne die Datei → ohne KI-Bilder
    ki_bild = None

try:
    import sprachen  # noqa: E402
except ImportError:                                  # Testkopie ohne die Datei → nur Spanisch
    sprachen = None


def L(de, en, es):
    return {"de": de, "en": en, "es": es}


MB = 1024 * 1024
RE_MODELLE = {"x4": "realesrgan-x4plus", "x2": "realesrgan-x2plus"}          # Teil → Modell (x4 = Standard)
RE_DOWNLOAD = {"realesrgan-x4plus": 67_040_989, "realesrgan-x2plus": 67_061_725}  # Original .pth von GitHub
RE_NPZ = {"realesrgan-x4plus": 31_124_949, "realesrgan-x2plus": 31_135_317}      # umgewandelt (float16)


class ToolFehler(Exception):
    """Fehler mit Code für die Oberfläche (gans_ui übersetzt ihn über seine TEXTE)."""
    def __init__(self, code, status=400, **werte):
        super().__init__(code)
        self.code, self.status, self.werte = code, status, werte


# =============================================================================================
# Orte und Zustand (tools.json im Datenordner)
# =============================================================================================
def daten_ordner() -> Path:
    return uebersetzer.daten_ordner()


def vorrat_ordner() -> Path:
    """Kopie der Real-ESRGAN-Modelle im Datenordner – eine neue Programmversion übernimmt sie ohne Download."""
    return daten_ordner() / "modelle"


def zustand_pfad() -> Path:
    return daten_ordner() / "tools.json"


_lock = threading.Lock()


def lade_zustand():
    d = uebersetzer._lies_json(zustand_pfad())
    aktiv = d.get("aktiv") if isinstance(d.get("aktiv"), dict) else {}
    ab = d.get("abgemeldet") if isinstance(d.get("abgemeldet"), list) else []
    return dict(gefragt=d.get("gefragt") if isinstance(d.get("gefragt"), str) else None,
                aktiv={k: str(v) for k, v in aktiv.items() if k in TOOLS},
                abgemeldet=[x for x in ab if x in TOOLS])


def _aendern(fn):
    with _lock:
        z = lade_zustand()
        fn(z)
        uebersetzer._schreibe_privat(zustand_pfad(), z)
        return z


def _jetzt():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _groesse(p):
    try:
        return p.stat().st_size if p.is_file() else 0
    except OSError:
        return 0


# =============================================================================================
# Die Tools
# =============================================================================================
def _re_dateien(teil=None):
    """[(Datei im Programm, Kopie im Datenordner)] je Real-ESRGAN-Modell (nur diese Namen werden je gelöscht)."""
    ids = [RE_MODELLE[teil]] if teil else list(RE_MODELLE.values())
    return [(ki_modelle.npz_pfad(m), vorrat_ordner() / f"{m}.npz") for m in ids]


def _re_da():
    return any(ki_modelle.verfuegbar(m) for m in RE_MODELLE.values())


def _re_belegt():
    return sum(_groesse(a) + _groesse(b) for a, b in _re_dateien())


def _re_auftrag(teil):
    """Liegt eine Kopie im Datenordner (frühere Installation), wird sie zurückgeholt – sonst Download."""
    modell = RE_MODELLE[teil or "x4"]
    ziel, kopie = ki_modelle.npz_pfad(modell), vorrat_ordner() / f"{modell}.npz"
    if not ziel.is_file() and kopie.is_file() and _groesse(kopie) > 1_000_000:
        try:
            ziel.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(kopie, ziel.with_name(ziel.name + ".tmp"))
            os.replace(ziel.with_name(ziel.name + ".tmp"), ziel)
        except OSError:
            pass
    return None if ki_modelle.verfuegbar(modell) else dict(art="modell", modell=modell)


def _re_loeschen(teil):
    """Nur die bekannten .npz-Dateien in genau diesen beiden Ordnern."""
    weg = []
    for datei in (p for paar in _re_dateien(teil) for p in paar):
        if datei.is_file() and not datei.is_symlink():
            datei.unlink()
            weg.append(datei)
    return weg


def _ue_dateien():
    return [uebersetzer.einstellungen_pfad(), daten_ordner() / "uebersetzungen.json"]


def _ue_da():
    return uebersetzer.lade_einstellungen()["zugestimmt"]


def _ue_loeschen(teil):
    weg = []
    for datei in _ue_dateien():
        if datei.is_file() and not datei.is_symlink():
            datei.unlink()
            weg.append(datei)
    return weg


def _ki_ordner():
    return ki_bild.modell_ordner() if ki_bild else daten_ordner() / "modelle" / "ki-bild"


def _ki_namen():
    if not ki_bild:
        return []
    return [n for d in ki_bild.MODELL["dateien"] for n in (d["name"], d["name"] + ".ok", d["name"] + ".part")]


def _ki_da():
    return bool(ki_bild) and ki_bild.status()["installiert"]


def _ki_belegt():
    ordner = _ki_ordner()
    return sum(_groesse(ordner / n) for n in _ki_namen())


def _ki_auftrag(teil):
    return None if _ki_da() else dict(art="ki-bild-laden")


def ki_ordner_eigen():
    """Löschschutz: Nur ein Modellordner innerhalb des Datenordners gehört dem Programm. Zeigt MGD_KI_BILD (Tests,
    Probe-Server) woandershin, wird dort nie etwas gelöscht – sonst träfe eine Probe das echte 3,5-GB-Modell."""
    try:
        return _ki_ordner().resolve().is_relative_to(daten_ordner().resolve())
    except OSError:
        return False


def _ki_loeschen(teil):
    ordner, weg = _ki_ordner(), []
    if not ki_ordner_eigen():
        return None                                  # nur abmelden
    for n in _ki_namen():
        datei = ordner / n
        if datei.is_file() and not datei.is_symlink():
            datei.unlink()
            weg.append(datei)
    try:
        ordner.rmdir()                               # nur, wenn jetzt leer (nie rekursiv)
    except OSError:
        pass
    return weg


TOOLS = {
    "bildverbesserung": dict(
        symbol="✨", art="download", standard_teil="x4",
        titel=L("Bildverbesserung (Real-ESRGAN)", "Image enhancement (Real-ESRGAN)", "Mejora de imagen (Real-ESRGAN)"),
        nutzen=L("Die schönste KI-Vergrößerung für deine Vorderseiten – gestochen scharf im Druck. Ohne Tool verbessert "
                 "das eingebaute FSRCNN die Bilder etwas schlichter.",
                 "The loveliest AI upscaling for your fronts – razor-sharp in print. Without the tool, the built-in "
                 "FSRCNN enhances images a little more simply.",
                 "La ampliación con IA más bonita para tus anversos: nítida al imprimir. Sin la herramienta, el FSRCNN "
                 "integrado mejora las imágenes de forma más sencilla."),
        # Teil-Titel kurz (Knopf „+ Titel“), die Erklärung steht in „hinweis“ (zweite Zeile des Knopfs, mit Größe)
        teile={"x4": dict(titel=L("Bestes Modell ×4", "Best model ×4", "Mejor modelo ×4"),
                          hinweis=L("die schönste Qualität für den Druck", "the loveliest quality for print",
                                    "la calidad más bonita para imprimir"),
                          groesse=RE_DOWNLOAD["realesrgan-x4plus"], platz=2 * RE_NPZ["realesrgan-x4plus"]),
               "x2": dict(titel=L("Schneller ×2", "Faster ×2", "Más rápido ×2"),
                          hinweis=L("fast gleiche Qualität, etwa 4× schneller", "almost the same quality, about 4× faster",
                                    "casi la misma calidad, unas 4 veces más rápido"),
                          groesse=RE_DOWNLOAD["realesrgan-x2plus"], platz=2 * RE_NPZ["realesrgan-x2plus"])},
        groesse=RE_DOWNLOAD["realesrgan-x4plus"], platz=2 * RE_NPZ["realesrgan-x4plus"],
        quelle="GitHub (xinntao/Real-ESRGAN), BSD-3-Clause",
        dauer=L("etwa 1 Minute", "about 1 minute", "aproximadamente 1 minuto"),
        loeschen=L("die Real-ESRGAN-Modelle im Programmordner und ihre Kopie im Datenordner",
                   "the Real-ESRGAN models in the program folder and their copy in the data folder",
                   "los modelos Real-ESRGAN de la carpeta del programa y su copia en la carpeta de datos"),
        laden=("modell",), nutzt=("verbessern", "generator"),
        ort=lambda: ki_modelle.MODELL_ORDNER, da=_re_da, belegt=_re_belegt, auftrag=_re_auftrag, entferne=_re_loeschen),
    "uebersetzung": dict(
        symbol="🌍", art="aktivierung", zustimmung=True,
        titel=L("Automatische Übersetzung", "Automatic translation", "Traducción automática"),
        nutzen=L("Schlägt für dein deutsches Wort die Übersetzung der Rückseite vor – über Wiktionary, MyMemory oder "
                 "DeepL, nur das einzelne Wort und nur mit deiner Zustimmung.",
                 "Suggests the back-side translation for your German word – via Wiktionary, MyMemory or DeepL, only "
                 "the single word and only with your consent.",
                 "Sugiere la traducción del reverso para tu palabra en alemán, con Wiktionary, MyMemory o DeepL: solo "
                 "la palabra y solo con tu permiso."),
        groesse=0, platz=200 * 1024, quelle="Wiktionary · MyMemory · DeepL",
        dauer=L("sofort", "instantly", "al instante"),
        loeschen=L("deine Zustimmung, die Einstellungen (auch ein gespeicherter DeepL-Schlüssel) und die gemerkten "
                   "Übersetzungen", "your consent, the settings (including a saved DeepL key) and the remembered "
                   "translations", "tu permiso, los ajustes (también una clave de DeepL guardada) y las traducciones "
                   "guardadas"),
        laden=(), nutzt=(),
        ort=daten_ordner, da=_ue_da, belegt=lambda: sum(_groesse(p) for p in _ue_dateien()),
        auftrag=lambda teil: None, entferne=_ue_loeschen),
    "ki-bild": dict(
        symbol="🎨", art="download", fortsetzbar=True,
        titel=L("KI-Bilder (realistische Gänse)", "AI images (realistic geese)", "Imágenes IA (gansos realistas)"),
        nutzen=L("Erzeugt realistische Gänse-Bilder für neue Karten – offline, direkt auf diesem Rechner (Segmind Vega "
                 "+ VegaRT, Lizenz Apache-2.0). Liegt im Datenordner – auch für spätere Programmversionen.",
                 "Creates realistic goose images for new cards – offline, right on this computer (Segmind Vega + "
                 "VegaRT, Apache-2.0 license). Stored in the data folder – also for later program versions.",
                 "Crea imágenes realistas de gansos para cartas nuevas, sin conexión y en esta computadora (Segmind "
                 "Vega + VegaRT, licencia Apache-2.0). Se guarda en la carpeta de datos, también para futuras versiones."),
        groesse=ki_bild.platz_noetig() if ki_bild else 3_540_000_000, quelle="Hugging Face (Segmind), Apache-2.0",
        dauer=L("je nach Internet 10–60 Minuten (ein Abbruch setzt später fort)",
                "10–60 minutes depending on your internet (an interruption resumes later)",
                "de 10 a 60 minutos según tu internet (si se corta, continúa después)"),
        loeschen=L("das KI-Bildmodell (ca. 3,5 GB) im Datenordner", "the AI image model (about 3.5 GB) in the data folder",
                   "el modelo de imágenes IA (unos 3,5 GB) en la carpeta de datos"),
        laden=("ki-bild-laden",), nutzt=("ki-bild",),
        ort=_ki_ordner, da=_ki_da, belegt=_ki_belegt, auftrag=_ki_auftrag, entferne=_ki_loeschen),
}
TOOLS["ki-bild"]["platz"] = TOOLS["ki-bild"]["groesse"]
if not ki_bild:                                      # ohne ki_bild.py gibt es das Tool nicht
    del TOOLS["ki-bild"]


def _sp_auftrag(teil):
    """Sprache ohne Dateien (lateinisch) wird sofort aktiviert; sonst Download über die Warteschlange."""
    code = teil or "en"
    if sprachen.installiert(code):
        return None
    if not sprachen.dateien(code) and not sprachen.SPRACHEN[code]["pakete"]:
        sprachen.lade(code, melde=lambda t: None)
        return None
    return dict(art="sprache", code=code)


def _sp_loeschen(teil):
    return sprachen.entferne(teil)


if sprachen:
    TOOLS["sprachen"] = dict(
        symbol="🗣", art="download", standard_teil="en",
        titel=L("Sprachen (Rückseite)", "Languages (back side)", "Idiomas (reverso)"),
        nutzen=L("Weitere Sprachen für die Rückseite deiner Karten und die automatische Übersetzung – jede Sprache "
                 "einzeln: lateinische Schriften sofort, Russisch, Japanisch, Chinesisch, Koreanisch, Hindi und "
                 "Arabisch mit eigener Schrift (1–17 MB). Spanisch ist immer dabei.",
                 "More languages for the back of your cards and for automatic translation – each language on its "
                 "own: Latin scripts instantly, Russian, Japanese, Chinese, Korean, Hindi and Arabic with their own "
                 "font (1–17 MB). Spanish is always included.",
                 "Más idiomas para el reverso de tus cartas y la traducción automática, cada uno por separado: "
                 "alfabeto latino al instante; ruso, japonés, chino, coreano, hindi y árabe con su propia fuente "
                 "(1–17 MB). El español siempre está incluido."),
        teile={c: dict(titel=s["name"], groesse=sprachen.groesse(c), platz=sprachen.platz(c))
               for c, s in sprachen.SPRACHEN.items() if c != sprachen.STANDARD},
        groesse=0, platz=0, quelle="GitHub (Google Fonts, Noto, IBM Plex), OFL-1.1 · PyPI (uharfbuzz), Apache-2.0",
        dauer=L("sofort bis wenige Minuten", "instantly to a few minutes", "de inmediato a unos minutos"),
        loeschen=L("die installierten Sprachpakete (Schriften) im Datenordner – deine Kartentexte bleiben",
                   "the installed language packs (fonts) in the data folder – your card texts stay",
                   "los paquetes de idioma instalados (fuentes) en la carpeta de datos; tus textos se quedan"),
        laden=("sprache",), nutzt=(), teil_da=sprachen.installiert,
        ort=sprachen.ordner, da=lambda: bool(sprachen.weitere_installiert()), belegt=lambda: sprachen.belegt(),
        auftrag=_sp_auftrag, entferne=_sp_loeschen)


# Karten lernen: nichts zu laden – Installieren = aktivieren, Deinstallieren löscht den Lernstand. Der liegt im
# Projektordner neben karten.csv; gans_ui setzt dafür lernstand_dateien (Funktion → [Pfade]).
lernstand_dateien = None


def _ln_dateien():
    return [Path(p) for p in (lernstand_dateien() if lernstand_dateien else [])]


def _ln_loeschen(teil):
    weg = []
    for datei in _ln_dateien():
        if datei.is_file() and not datei.is_symlink():
            datei.unlink()
            weg.append(datei)
    return weg


TOOLS["lernen"] = dict(
    symbol="🎓", art="aktivierung",
    titel=L("Karten lernen", "Learn cards", "Aprender cartas"),
    nutzen=L("Lerne deine Karten aus „Meine Karten“ wie mit Anki: erst erinnern, dann umdrehen. Der Planer FSRS zeigt "
             "jede Karte genau dann wieder, wenn du sie sonst vergessen würdest – gans schön effizient. Dein Lernstand "
             "bleibt gespeichert.",
             "Learn the cards from “My cards” just like with Anki: recall first, then flip. The FSRS scheduler shows "
             "each card again right before you would forget it – honkingly efficient. Your progress is saved.",
             "Aprende las cartas de «Mis cartas» como con Anki: primero recuerda, luego voltea. El planificador FSRS "
             "te muestra cada carta justo antes de que la olvides: ¡eficiencia de ganso! Tu progreso se guarda."),
    groesse=0, platz=1024 * 1024, quelle="FSRS-6 (open-spaced-repetition), MIT",
    dauer=L("sofort", "instantly", "al instante"),
    loeschen=L("deinen Lernstand (lernstand.json neben karten.csv) – exportiere ihn vorher, wenn du ihn behalten "
               "möchtest; deine Karten bleiben",
               "your learning progress (lernstand.json next to karten.csv) – export it first if you want to keep it; "
               "your cards stay",
               "tu progreso de aprendizaje (lernstand.json junto a karten.csv); expórtalo antes si quieres "
               "conservarlo. Tus cartas se quedan"),
    laden=(), nutzt=(),
    ort=lambda: _ln_dateien()[0].parent if _ln_dateien() else daten_ordner(), da=lambda: False,
    belegt=lambda: sum(_groesse(p) for p in _ln_dateien()), auftrag=lambda teil: None, entferne=_ln_loeschen)


# =============================================================================================
# Abfragen und Aktionen
# =============================================================================================
def gibt_es(tid):
    return tid in TOOLS


def _pruefe(tid, teil=None):
    if tid not in TOOLS:
        raise ToolFehler("tool_unbekannt", 404)
    if teil is not None and teil not in (TOOLS[tid].get("teile") or {}):
        raise ToolFehler("ungueltig")


def installiert(tid, zustand=None):
    """Download-Tools: Dateien vollständig da · Aktivierungs-Tools: aktiviert bzw. Zustimmung erteilt; jeweils nicht
    abgemeldet."""
    _pruefe(tid)
    z = zustand or lade_zustand()
    if tid in z["abgemeldet"]:
        return False
    return bool(TOOLS[tid]["da"]()) or tid in z["aktiv"]


def teile_info(tid):
    t = TOOLS[tid]
    da = t.get("teil_da") or (lambda k: ki_modelle.verfuegbar(RE_MODELLE[k]) if tid == "bildverbesserung" else False)
    return [dict(id=k, titel=v["titel"], hinweis=v.get("hinweis"), groesse=v["groesse"], platz=v["platz"], installiert=da(k))
            for k, v in (t.get("teile") or {}).items()]


def teil_aus_befehl(tid, befehl):
    """Welcher Teil lädt gerade? (aus der Befehlszeile des Laufs)"""
    befehl = [str(x) for x in befehl or []]
    if tid == "bildverbesserung":
        return next((k for k, m in RE_MODELLE.items() if m in befehl), None)
    if tid == "sprachen" and "--laden" in befehl:
        i = befehl.index("--laden")
        return befehl[i + 1] if i + 1 < len(befehl) else None
    return None


def belegt(tid, zustand=None):
    z = zustand or lade_zustand()
    return 0 if tid in z["abgemeldet"] else TOOLS[tid]["belegt"]()


def prozent(tid, zeilen):
    """Fortschritt eines laufenden Downloads (0–100) – KI-Bild über die schon geladenen Bytes, sonst „NN %“-Zeilen."""
    if tid == "ki-bild" and ki_bild:
        st = ki_bild.status()
        return min(99, int(st["bytes_da"] * 100 / max(1, st["bytes_gesamt"])))
    for z in reversed(zeilen or []):
        teile = z.strip().split(" %", 1)
        if len(teile) == 2 and teile[0].isdigit():
            return min(99, int(teile[0]))
    return 0


def gehoert(tid, art, befehl=None):
    """Gehört ein Lauf der Warteschlange zu diesem Tool? → "laden" (Download), "nutzt" (verwendet es) oder None."""
    t = TOOLS.get(tid) or {}
    if art in t.get("laden", ()):
        return "laden"
    if art in t.get("nutzt", ()):
        return "nutzt"
    return None


def liste(zustand=None):
    """Alle Tools mit Zustand (Texte noch als L(…); gans_ui.tools_info wählt die Sprache und ergänzt die Läufe)."""
    z = zustand or lade_zustand()
    aus = []
    for tid, t in TOOLS.items():
        da, b = installiert(tid, z), belegt(tid, z)
        aus.append(dict(id=tid, symbol=t["symbol"], art=t["art"], titel=t["titel"], nutzen=t["nutzen"],
                        groesse=t["groesse"], platz=t["platz"], quelle=t["quelle"], dauer=t["dauer"],
                        loeschen=t["loeschen"], zustimmung=bool(t.get("zustimmung")), installiert=da, belegt=b,
                        angefangen=bool(t.get("fortsetzbar")) and not da and b > 0, ort=str(t["ort"]()),
                        abgemeldet=tid in z["abgemeldet"], teile=teile_info(tid), aktiv_seit=z["aktiv"].get(tid)))
    return aus


def erstabfrage_noetig(zustand=None):
    """Einmalig fragen – und nur, wenn noch etwas nicht installiert ist (Update von 1.6: Vorhandenes zählt)."""
    z = zustand or lade_zustand()
    return not z["gefragt"] and any(not installiert(tid, z) for tid in TOOLS)


def gefragt_setzen():
    return _aendern(lambda z: z.update(gefragt=_jetzt()))


def installieren(tid, teil=None):
    """Meldet das Tool an. Gibt den Auftrag für die Warteschlange zurück (dict für gans_ui.starte_lauf) oder None,
    wenn nichts zu laden ist (Aktivierungs-Tool bzw. Dateien schon vollständig da)."""
    _pruefe(tid, teil)
    t = TOOLS[tid]
    if t.get("zustimmung") and not t["da"]():
        raise ToolFehler("zustimmung", 409)

    def anmelden(z):
        z["abgemeldet"] = [x for x in z["abgemeldet"] if x != tid]
        if t["art"] == "aktivierung":
            z["aktiv"][tid] = _jetzt()
    _aendern(anmelden)
    return t["auftrag"](teil or t.get("standard_teil"))


def deinstalliere(tid, teil=None):
    """Löscht nur die bekannten Dateien des Tools in den erwarteten Ordnern – nie Karten, Bilder, Ideen. Liegt das
    KI-Bildmodell außerhalb des Datenordners (MGD_KI_BILD), wird es nur abgemeldet. Gibt {geloescht, frei,
    abgemeldet} zurück."""
    _pruefe(tid, teil)
    t = TOOLS[tid]
    vorher = t["belegt"]()
    weg = t["entferne"](teil)
    nur_abmelden = weg is None
    rest_da = bool(teil) and t["da"]()               # nur ein Teil gelöscht, der andere bleibt

    def abmelden(z):
        z["aktiv"].pop(tid, None)
        if nur_abmelden and tid not in z["abgemeldet"]:
            z["abgemeldet"].append(tid)
        if not nur_abmelden and not rest_da:
            z["abgemeldet"] = [x for x in z["abgemeldet"] if x != tid]
    _aendern(abmelden)
    return dict(geloescht=[str(p) for p in (weg or [])], frei=0 if nur_abmelden else max(0, vorher - t["belegt"]()),
                abgemeldet=nur_abmelden)


if __name__ == "__main__":
    for e in liste():
        print(f"{'✓' if e['installiert'] else '·'} {e['id']:17} {e['titel']['de']:34} belegt {e['belegt'] / MB:7.1f} MB")
