#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ME GOOS-TA DEUTSCH – Selbsttest der Erweiterungen                   Version 2.5 (23.10.2026)
Prüft Import/Export, Ideen, Programmstart-Wahl, die Schutzregeln des Deinstallierens und die Hilfe – wie der Selbsttest in
einer Kopie des Projekts mit den Beispielkarten und einem eigenen Datenordner (nichts Eigenes wird berührt, nichts
wird wirklich deinstalliert, kein Browser wird geöffnet). Ergänzt test_gans_lernkarten.py (der bleibt unverändert).

Aufruf:  python3 test_erweiterungen.py
"""

import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

from PIL import Image

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import test_gans_lernkarten as tg  # noqa: E402  (Hilfen: Kopie, Sitzung, freier Port, pruefe)

pruefe = tg.pruefe


def jpg(farbe=(200, 120, 40), groesse=(640, 480)):
    puffer = io.BytesIO()
    Image.new("RGB", groesse, farbe).save(puffer, "JPEG", quality=90)
    return puffer.getvalue()


def starte_server(p, daten):
    port = tg._freier_port()
    proc = subprocess.Popen([sys.executable, str(p / "gans_ui.py"), "--kein-browser", "--port", str(port)], cwd=p,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            env=dict(os.environ, PYTHONIOENCODING="utf-8", MGD_DATEN=str(daten), MGD_START_ID="test"))
    adresse = None
    for _ in range(100):
        m = re.search(r"http://127\.0\.0\.1:\d+/\?k=[A-Za-z0-9_-]+", proc.stdout.readline().decode("utf-8", "replace"))
        if m:
            adresse = m.group(0)
            break
    se = tg.Sitzung(port)
    for _ in range(50):
        try:
            code, kopf, _ = se.anfrage(adresse.split(str(port), 1)[1])
            break
        except OSError:
            time.sleep(0.2)
    se.cookie = kopf.get("set-cookie", "").split(";")[0]
    se.token = re.search(rb'const TOKEN = "([^"]+)"', se.anfrage("/")[2]).group(1).decode()
    return proc, se


def test_server(p, daten):
    print("\n[E1] Import / Export")
    proc, se = starte_server(p, daten)
    try:
        code, kopf, inhalt = se.anfrage("/api/export?umfang=alle")
        z = zipfile.ZipFile(io.BytesIO(inhalt)) if code == 200 else None
        namen = z.namelist() if z else []
        pruefe("Export: ZIP mit karten.csv und Bildern", code == 200 and "karten.csv" in namen
               and sum(n.startswith("bilder/") for n in namen) == 10, str(namen[:3]))
        pruefe("Export: als Download", "attachment" in kopf.get("content-disposition", ""))
        code, _, _ = se.anfrage("/api/export", mit_cookie=False)
        pruefe("Export nur mit Sitzung", code == 403)

        # Import-Datei bauen: neue Karte, geänderte Karte, Formel, kaputtes Bild, Pfad-Ausbruch, HEIC
        csv = ("\ufeffbild;de;es;notiz\r\n"
               "gans-neu.jpg;Gans neu;nuevo;\r\n"
               "gans-alt.jpg;Gans alt;anciano;\r\n"
               "gans-formel.jpg;Gans x;=HYPERLINK(1);\r\n"
               "gans-kaputt.jpg;Gans kaputt;roto;\r\n"
               "gans-heic.jpg;Gans heic;heic;\r\n"
               "../boese.jpg;Gans böse;malo;\r\n")
        puffer = io.BytesIO()
        with zipfile.ZipFile(puffer, "w") as zz:
            zz.writestr("export/karten.csv", csv.encode("utf-8"))
            zz.writestr("export/bilder/gans-neu.jpg", jpg())
            zz.writestr("export/bilder/gans-formel.jpg", jpg())
            zz.writestr("export/bilder/gans-kaputt.jpg", b"kein Bild")
            zz.writestr("export/bilder/gans-heic.jpg", b"\x00\x00\x00\x18ftypheic" + b"\x00" * 64)
            zz.writestr("export/bilder/../boese.jpg", jpg())
        code, r = se.json("/api/import", roh=puffer.getvalue())
        status = {k["bild"]: k["status"] for k in r.get("karten", [])}
        pruefe("Import: Vorschau erkennt neu und anders", status.get("gans-neu.jpg") == "neu"
               and status.get("gans-alt.jpg") == "konflikt", str(status))
        pruefe("Import: Formel, kaputtes Bild, HEIC, Pfad-Ausbruch abgelehnt",
               all(status.get(n) == "fehler" for n in ("gans-formel.jpg", "gans-kaputt.jpg", "gans-heic.jpg", "../boese.jpg")),
               str(status))
        pruefe("Import: Vorschau ändert noch nichts", not (p / "bilder" / "gans-neu.jpg").exists())
        iid = r.get("id")
        code, r2 = se.json("/api/import-uebernehmen", {"id": iid, "ersetzen": False})
        karten = {k["bild"]: k for k in r2.get("karten", {}).get("karten", [])}
        pruefe("Import: neue Karte übernommen, Konflikt übersprungen", code == 200 and "gans-neu.jpg" in karten
               and karten["gans-alt.jpg"]["es"] != "anciano" and r2["zahlen"]["neu"] == 1, str(r2.get("zahlen")))
        pruefe("Import: kein Ausbruch aus dem Bilderordner", not (p / "boese.jpg").exists() and not (p.parent / "boese.jpg").exists())
        code, _ = se.json("/api/import-uebernehmen", {"id": iid, "ersetzen": True})
        pruefe("Import: verbrauchte Vorschau abgelehnt", code == 400)
        code, r = se.json("/api/import", roh=puffer.getvalue())
        code, r2 = se.json("/api/import-uebernehmen", {"id": r["id"], "ersetzen": True})
        karten = {k["bild"]: k for k in r2.get("karten", {}).get("karten", [])}
        pruefe("Import: „ersetzen“ übernimmt den neuen Text", karten.get("gans-alt.jpg", {}).get("es") == "anciano")
        pruefe("Import: Sicherung karten.bak.csv", (p / "karten.bak.csv").is_file())
        code, r = se.json("/api/import", roh=b"\x00\x01kein zip und keine csv")
        pruefe("Import: unlesbare Datei → verständlicher Fehler", code == 400 and r.get("fehler"))
        code, r = se.json("/api/import", roh=inhalt)                       # eigener Export → alles gleich
        pruefe("Import des eigenen Exports: nichts Neues", code == 200 and r["zahlen"]["neu"] == 0
               and r["zahlen"]["fehler"] == 0, str(r.get("zahlen")))

        print("\n[E2] Ideen")
        code, r = se.json("/api/idee", {"de": "Gans flauschig", "es": ""})
        iid = r.get("id")
        pruefe("Idee mit deutschem Wort angelegt", code == 200 and any(i["id"] == iid for i in r["ideen"]))
        code, r = se.json("/api/idee", {"de": "", "es": ""})
        pruefe("Leere Idee abgelehnt", code == 400)
        code, r = se.json("/api/idee", {"id": iid, "de": "=1+1", "es": ""})
        pruefe("Formel in einer Idee abgelehnt", code == 400)
        code, r = se.json(f"/api/idee-bild?id={iid}", roh=jpg((90, 140, 200)))
        idee = next((i for i in r.get("ideen", []) if i["id"] == iid), {})
        pruefe("Bild zur Idee gespeichert", code == 200 and idee.get("bild") is True)
        code, kopf, _ = se.anfrage(f"/api/idee-bild?id={iid}")
        pruefe("Bild der Idee abrufbar", code == 200 and kopf.get("content-type") == "image/jpeg")
        code, r = se.json(f"/api/idee-bild?id={iid}", roh=b"kein Bild")
        pruefe("Kaputtes Bild für eine Idee abgelehnt", code == 400)
        code, r = se.json("/api/idee-aufnehmen", {"id": iid})
        pruefe("Unvollständige Idee wird keine Karte", code == 400)
        se.json("/api/idee", {"id": iid, "de": "Gans flauschig", "es": "esponjoso", "notiz": "aus Ideen"})
        code, r = se.json("/api/idee-aufnehmen", {"id": iid})
        karten = {k["bild"]: k for k in r.get("karten", {}).get("karten", [])}
        pruefe("Fertige Idee → Karte in Meine Karten", code == 200 and r.get("ok") and r.get("name") == "gans-flauschig.jpg"
               and karten.get("gans-flauschig.jpg", {}).get("es") == "esponjoso"
               and karten["gans-flauschig.jpg"].get("notiz") == "aus Ideen", str(r)[:200])
        pruefe("Aufgenommene Idee verschwindet aus den Ideen", not any(i["id"] == iid for i in r.get("ideen", [])))
        # Namenskonflikt: zweite Idee mit gleichem Text
        code, r = se.json("/api/idee", {"de": "Gans flauschig", "es": "suave"})
        iid2 = r["id"]
        se.json(f"/api/idee-bild?id={iid2}", roh=jpg((10, 200, 10)))
        code, r = se.json("/api/idee-aufnehmen", {"id": iid2})
        pruefe("Namenskonflikt wird gemeldet statt überschrieben", code == 200 and r.get("ok") is False and r.get("kollision"))
        code, r = se.json("/api/idee-weg", {"id": iid2})
        pruefe("Idee verwerfen", code == 200 and not any(i["id"] == iid2 for i in r["ideen"]))
        code, r = se.json("/api/idee-zurueck", {"id": iid2})
        pruefe("Verworfene Idee wiederherstellen (mit Bild)", code == 200 and any(i["id"] == iid2 and i["bild"] for i in r["ideen"]))
        code, r = se.json("/api/ideen")
        pruefe("Unfertige Karten erscheinen bei den Ideen", code == 200 and {"entwuerfe", "offen", "ohne"} <= set(r))
        code, r = se.json("/api/idee-bild?id=../../x", roh=jpg())
        pruefe("Ungültige Ideen-ID abgewiesen", code == 400)

        print("\n[E3] Programmstart und Deinstallieren")
        code, r = se.json("/api/start-einstellung")
        pruefe("Programmstart: noch nicht gewählt, Frage vom Startprogramm", code == 200 and not r["gewaehlt"] and r["vom_starter"])
        code, r = se.json("/api/start-einstellung", {"art": "fenster", "browser": "unbekannt; rm -rf"})
        gespeichert = json.loads((daten / "start.json").read_text(encoding="utf-8"))
        pruefe("Programmstart gespeichert, unbekannter Browser → Standard", code == 200 and r["gewaehlt"]
               and gespeichert["art"] == "fenster" and gespeichert["browser"] == "standard")
        code, r = se.json("/api/deinstallieren", {})
        pruefe("Deinstallieren ohne Bestätigung abgelehnt", code == 400)
        code, _ = se.json("/api/deinstallieren", {"bestaetigt": True}, mit_token=False)
        pruefe("Deinstallieren ohne Token abgewiesen", code == 403)
        print("\n[E5] Ideen exportieren/importieren, Warnung bei Vorhandenem")
        code, r = se.json("/api/idee", {"de": "Gans fröhlich", "es": "alegre"})
        iid3 = r["id"]
        se.json(f"/api/idee-bild?id={iid3}", roh=jpg((250, 200, 30)))
        code, _, inhalt = se.anfrage("/api/export?inhalt=ideen")
        zi = zipfile.ZipFile(io.BytesIO(inhalt))
        ideen_json = json.loads(zi.read("ideen.json"))
        pruefe("Export Ideen: ideen.json mit Bildern", code == 200 and any(i["id"] == iid3 for i in ideen_json["ideen"])
               and any(n.startswith("ideen/") for n in zi.namelist()) and "karten.csv" not in zi.namelist())
        code, _, alles = se.anfrage("/api/export?inhalt=alles")
        namen = zipfile.ZipFile(io.BytesIO(alles)).namelist()
        pruefe("Komplettsicherung: Karten und Ideen in einer Datei", "karten.csv" in namen and "ideen.json" in namen)
        code, r = se.json("/api/import", roh=inhalt)
        status = {e["id"]: e["status"] for e in r.get("ideen", [])}
        pruefe("Eigener Ideen-Export: alles „gleich“", code == 200 and status.get(iid3) == "gleich" and r["zahlen"]["neu"] == 0,
               str(r.get("zahlen")))
        geaendert = [dict(i) for i in ideen_json["ideen"] if i["id"] == iid3]
        geaendert[0]["es"] = "contento"
        neue = [*geaendert, {"id": "", "de": "Gans neugierig", "es": "curioso", "notiz": "", "bild": "", "es_auto": ""},
                {"id": "", "de": "Gans alt", "es": "", "notiz": "", "bild": "", "es_auto": ""},
                {"id": "", "de": "=SUMME(1)", "es": "", "notiz": "", "bild": "", "es_auto": ""}]
        puffer = io.BytesIO()
        with zipfile.ZipFile(puffer, "w") as zz:
            zz.writestr("ideen.json", json.dumps({"ideen": neue}))
        code, r = se.json("/api/import", roh=puffer.getvalue())
        st = [e["status"] for e in r.get("ideen", [])]
        pruefe("Ideen-Import: geändert → Warnung, neu, Wort als Karte → Warnung, Formel → Fehler",
               st == ["konflikt", "neu", "konflikt", "fehler"], str(st))
        code, r2 = se.json("/api/import-uebernehmen", {"id": r["id"], "ersetzen": {"standard": False, "i:0": True}})
        ideen = {i["id"]: i for i in r2.get("ideen", [])}
        pruefe("Ideen-Import: „Ersetzen“ je Zeile, „Behalten“ für den Rest",
               code == 200 and ideen.get(iid3, {}).get("es") == "contento"
               and any(i["de"] == "Gans neugierig" for i in ideen.values())
               and not any(i["de"] == "Gans alt" for i in ideen.values()), str(r2.get("zahlen")))
        # gleiche Karte unter anderem Dateinamen
        csv2 = "﻿bild;de;es;notiz\r\ngans-alt-2.jpg;Gans alt;anciano;\r\n"
        puffer = io.BytesIO()
        with zipfile.ZipFile(puffer, "w") as zz:
            zz.writestr("karten.csv", csv2.encode("utf-8"))
            zz.writestr("bilder/gans-alt-2.jpg", jpg((5, 5, 200)))
        code, r = se.json("/api/import", roh=puffer.getvalue())
        k0 = (r.get("karten") or [{}])[0]
        pruefe("Gleiches Wort unter anderem Namen → Warnung", k0.get("status") == "konflikt" and k0.get("statt") == "gans-alt.jpg",
               str(k0)[:160])
        code, r2 = se.json("/api/import-uebernehmen", {"id": r["id"], "ersetzen": {"k:gans-alt-2.jpg": True}})
        namen = [k["bild"] for k in r2.get("karten", {}).get("karten", [])]
        pruefe("„Ersetzen“: neue Karte statt der alten, altes Bild aufgehoben",
               "gans-alt-2.jpg" in namen and "gans-alt.jpg" not in namen and (p / "bilder" / "_entfernt" / "gans-alt.jpg").is_file())
        code, r = se.json("/api/uebersetzen-de", {"es": "viejo"})
        pruefe("Spanisch → Deutsch nur mit Zustimmung", code == 409)
        code, _ = se.json("/api/werkzeug", {"id": "zip"})
        zp = p / "ausgabe" / "Me-Goos-ta-Deutsch_Projekt.zip"
        rechte = {i.filename.split("/", 1)[1]: (i.create_system, (i.external_attr >> 16) & 0o777)
                  for i in (zipfile.ZipFile(zp).infolist() if code == 200 and zp.exists() else []) if i.filename.count("/") == 1}
        pruefe("Projekt-ZIP: Mac- und Linux-Startdatei ausführbar (auch unter Windows gepackt)",
               rechte.get("Me Goos-ta Deutsch - Mac.command") == (3, 0o755)
               and rechte.get("Me Goos-ta Deutsch - Linux.sh") == (3, 0o755)
               and rechte.get("LIES MICH ZUERST.html") == (3, 0o644), str(rechte))

        test_bild_aendern(p, se)
        test_handy_feinschliff(p, se)
        _, liste = se.json("/api/werkzeuge")
        kb = next((w for w in liste if w["id"] == "ki-bild"), {})
        pruefe("[E13] Werkzeug „KI-Bildmodell laden“: Lauf mit Rückfrage, bei den KI-Modellen",
               kb.get("art") == "lauf" and "3,5 GB" in (kb.get("frage") or "") and
               [w["id"] for w in liste].index("ki-bild") == [w["id"] for w in liste].index("modell-x2") + 1, str(kb)[:160])
        test_ki_bild_prompt_server(p, se)
        test_ki_bild_lauf(p, se)

        print("\n[E7] Handy-Zugang im WLAN (mit E12-Prüfungen)")
        test_lan(se, daten)

        code, r = se.json("/api/werkzeuge")
        ids = [w["id"] for w in r]
        pruefe("Neue Werkzeuge erscheinen (Deinstallieren hat einen eigenen Reiter)",
               {"import-export", "gans-werkzeug", "programmstart"} <= set(ids) and "deinstallieren" not in ids
               and all(w["art"] == "dialog" for w in r if w["id"] in ("import-export", "programmstart")))
    finally:
        proc.terminate()
        proc.wait(10)


def test_ki_bild_prompt_server(p, se):
    """E16 (Server): Standard-Prompt anzeigen, eigene Fassung speichern/zurücksetzen, Schalter „keine Menschen“ merken."""
    print("\n[E16] KI-Bilder: Standard-Prompt über den Server")
    code, info = se.json("/api/ki-bild")
    code2, t = se.json("/api/ki-bild-text", {"beschreibung": "swimming on a lake at sunset", "wort": "Gans alt"})
    pruefe("Standard: Vorlage + Schalter „keine Menschen“ an; Beschreibung eingesetzt, „alone“ dazu, Menschen im Negativ",
           code == 200 and code2 == 200 and info["vorlage"] == info["standard"]["vorlage"] and info["ohne_menschen"] is True
           and not info["eigene"] and info["installiert"] is ECHT_DA and "swimming on a lake at sunset" in t["prompt"]
           and "alone" in t["prompt"] and "people" in t["negativ"] and "Gans alt" not in t["prompt"], str(t)[:200])
    code, r = se.json("/api/ki-bild-prompt", {"vorlage": "photo of a goose, {Beschreibung}, {wort}", "negativ": "blurry"})
    _, t = se.json("/api/ki-bild-text", {"beschreibung": "on ice", "wort": "Gans glatt", "ohne_menschen": False})
    _, t2 = se.json("/api/ki-bild-text", {"beschreibung": "on ice", "wort": ""})
    pruefe("Eigene Fassung (deutsche Platzhalter erlaubt) gilt sofort; ohne Schalter kein Negativ-Prompt; leeres Wort sauber",
           code == 200 and r["eigene"] and r["vorlage"] == "photo of a goose, {description}, {word}"
           and t["prompt"] == "photo of a goose, on ice, Gans glatt" and t["negativ"] is None
           and t2["prompt"] == f"photo of a goose, on ice, {r['allein']}" and t2["negativ"].startswith("blurry, people"),
           f"{t['prompt']} | {t2['prompt']}")
    code, f = se.json("/api/ki-bild-prompt", {"vorlage": "a goose without placeholder"})
    se.json("/api/ki-bild-prompt", {"ohne_menschen": False})
    _, r = se.json("/api/ki-bild")
    gemerkt = json.loads((p / "ui_einstellungen.json").read_text(encoding="utf-8")).get("ki_bild")
    pruefe("Vorlage ohne {description} → freundliche Meldung; Schalter wird gemerkt (ui_einstellungen.json)",
           code == 400 and "{description}" in f.get("fehler", "") and r["ohne_menschen"] is False and r["eigene"]
           and gemerkt == {"vorlage": "photo of a goose, {description}, {word}", "negativ": "blurry",
                           "ohne_menschen": False}, f"{f} {gemerkt}")
    _, r = se.json("/api/ki-bild-prompt", {"zuruecksetzen": True, "ohne_menschen": True})
    _, r2 = se.json("/api/ki-bild-prompt", {"vorlage": r["standard"]["vorlage"], "negativ": r["standard"]["negativ"]})
    html = (p / "ui" / "index.html").read_text(encoding="utf-8")
    schluessel = set(re.findall(r"\b((?:h_)?ki_[a-z0-9_]+):", html))
    anzahl = lambda k: len(re.findall(r"(?<!\w)" + k + ":", html))  # noqa: E731
    _, st = se.json("/api/status")
    pruefe("Oberfläche: Fenster + Knöpfe (Schritt 1, Karten-Editor, GANS-Werkzeug „Für diese Karte“), alle KI-Texte de/en/es",
           'id="ki-fenster"' in html and 'data-dialog="ki-bild"' in html and 'data-k-aktion="ki-bild"' in html
           and 'data-gw-aktion="fuer-karte"' in html and st.get("ki_bild") is True and len(schluessel) >= 55
           and all(anzahl(k) == 3 for k in schluessel), str(sorted(k for k in schluessel if anzahl(k) != 3)))
    pruefe("„Standard wiederherstellen“ und Standard-Text gespeichert = keine eigene Fassung",
           not r["eigene"] and r["vorlage"] == r["standard"]["vorlage"] and r["ohne_menschen"] and not r2["eigene"]
           and json.loads((p / "ui_einstellungen.json").read_text(encoding="utf-8")).get("ki_bild") == {"ohne_menschen": True})


def _warte_lauf(se, sekunden=180):
    st = {}
    for _ in range(int(sekunden * 4)):
        _, st = se.json("/api/lauf")
        if not st.get("laeuft"):
            break
        time.sleep(0.25)
    return st


def test_ki_bild_lauf(p, se):
    """E17: KI-Bild im Hintergrund erzeugen (eigener Prozess), Vorschau, Übernehmen als Entwurf, Abbrechen."""
    print("\n[E17] KI-Bilder: Erzeugen im Hintergrund")
    code, r = se.json("/api/lauf", {"art": "ki-bild", "beschreibung": "on a meadow", "karte": "../boese.jpg"})
    pruefe("Lauf „ki-bild“ prüft vorher: Modell da? Karte im Bilder-Ordner?", code in (400, 404, 409) and r.get("fehler")
           and (ECHT_DA or "KI-Bildmodell" in r["fehler"]), str(r)[:120])
    if not ECHT_DA:
        print("          (Bildmodell nicht geladen – echte Läufe übersprungen)")
        return
    code, st = se.json("/api/lauf", {"art": "ki-bild", "beschreibung": "standing on a green meadow", "wort": "Gans alt",
                                     "ohne_menschen": False, "startwert": 7, "breite": 384, "hoehe": 256, "schritte": 2,
                                     "schnell": True})
    st = _warte_lauf(se)
    ki = st.get("ki") or {}
    code_b, _, inhalt = se.anfrage(f"/api/ki-bild-bild?id={ki.get('id')}")
    code_v, kopf_v, _ = se.anfrage(f"/api/ki-bild-bild?id={ki.get('id')}&art=vorschau")
    groesse = Image.open(io.BytesIO(inhalt)).size if code_b == 200 else None
    meta = json.loads((p / "ausgabe" / ".ki-bild" / f"{ki.get('id')}.json").read_text(encoding="utf-8")) if ki else {}
    pruefe("Lauf fertig: Bild 384×256 + Vorschau, Startwert gemerkt, Prozente/Ergebniszeile nicht im Protokoll",
           code == 200 and st.get("code") == 0 and ki.get("fertig") and ki.get("startwert") == 7 and ki.get("prozent") == 100
           and groesse == (384, 256) and code_v == 200 and kopf_v.get("content-type") == "image/jpeg"
           and ki.get("vorschau") and meta.get("negativ") is None and "standing on a green meadow" in meta.get("prompt", "")
           and not any("#ergebnis" in z or z.strip().endswith("%") for z in st.get("zeilen", [])),
           f"{st.get('code')} {groesse} {st.get('zeilen', [])[-2:]}")
    code, e = se.json("/api/ki-bild-uebernehmen", {"id": ki.get("id")})
    _, karten = se.json("/api/karten")
    karte = next(k["bild"] for k in karten["karten"] if (p / "bilder" / k["bild"]).is_file())
    code2, e2 = se.json("/api/ki-bild-uebernehmen", {"id": ki.get("id"), "karte": karte})
    pruefe("Übernehmen: Entwurf für neue Karte (Text = Wort) und als neues Bild einer vorhandenen Karte",
           code == 200 and e.get("de") == "Gans alt" and code2 == 200 and e2.get("karte") == karte
           and e2.get("id") != e.get("id"), f"{str(e)[:120]} | {str(e2)[:120]}")
    for x in (e, e2):
        se.json("/api/entwurf-weg", {"id": x.get("id")})
    se.json("/api/lauf", {"art": "ki-bild", "beschreibung": "swimming", "breite": 896, "hoehe": 640})
    time.sleep(1.5)
    code, _ = se.json("/api/lauf-stopp", {})
    st = _warte_lauf(se, 20)
    pruefe("Abbrechen beendet den KI-Lauf sofort (kein Ergebnis)",
           code == 200 and not st.get("laeuft") and st.get("code") != 0 and not (st.get("ki") or {}).get("fertig"))


def test_ki_bild_prompt(echt):
    """E16: Prompt-Bau ohne Server – Platzhalter, Bereinigung, Schalter, Grenzen, Länge in CLIP-Token."""
    print("\n[E16] KI-Bilder: Standard-Prompt (Bausteine)")
    import ki_bild as kb
    p, n = kb.baue_prompt("  sleeping   in a cozy nest  ", wort="GANS müde")
    p2, n2 = kb.baue_prompt("", ohne_menschen=False)
    p3, _ = kb.baue_prompt("a {word} goose", wort="X", vorlage="goose, {word}, {DESCRIPCIÓN}", ohne_menschen=False)
    pruefe("Prompt: Beschreibung bereinigt eingesetzt, „alone“ + Menschen im Negativ; ohne Schalter kein Negativ",
           "domestic goose, sleeping in a cozy nest, " + kb.ALLEIN in p and n.endswith(kb.NEGATIV_MENSCHEN)
           and n.startswith(kb.NEGATIV_STANDARD) and n2 is None and "green meadow" in p2 and kb.ALLEIN not in p2
           and "GANS" not in p and p3 == "goose, X, a (word) goose", p3)
    pruefe("Positiver Standard-Prompt nennt keine Menschen (die würden sonst erst herbeigerufen)",
           not re.search(r"\b(people|person|human|man|woman|child|crowd)\b", kb.PROMPT_STANDARD + " " + kb.ALLEIN))
    alt = os.environ.get("MGD_SPRACHE")
    meldungen = []
    for s in ("de", "en", "es"):
        os.environ["MGD_SPRACHE"] = s
        for falsch in ("no placeholder", "{description} " + "x" * kb.PROMPT_MAX):
            try:
                kb.pruefe_vorlage(falsch)
            except ValueError as e:
                meldungen.append(str(e))
    if alt is None:
        os.environ.pop("MGD_SPRACHE", None)
    else:
        os.environ["MGD_SPRACHE"] = alt
    pruefe("Vorlage ohne Platzhalter oder zu lang → Meldung in de/en/es", len(meldungen) == 6
           and "Beschreibung" in meldungen[0] and "description goes" in meldungen[2] and "descripción" in meldungen[4]
           and "kürzer" in meldungen[1], str(meldungen[:2]))
    if not (echt and kb.status(echt)["installiert"]):
        return
    lang = kb.baue_prompt("standing on an old wooden jetty by a misty lake in autumn, looking at the water")[0]
    pruefe("Standard-Prompt mit typischer Beschreibung passt in 75 CLIP-Token", kb.token_anzahl(lang, echt) <= 75,
           f"{kb.token_anzahl(lang, echt)} Token")


def test_ki_bild_plattform():
    """E18: KI-Bild auf Windows, macOS und Linux – nur Standardbibliothek + NumPy, Arbeitsspeicher auch über sysconf,
    sparsamer Weg bei wenig Speicher, Threads ohne Hängenbleiben, Befehlszeile ohne Modell freundlich."""
    print("\n[E18] KI-Bilder: Windows, macOS, Linux")
    import ast
    import threading
    import ki_bild as kb
    oben = set()
    for knoten in ast.parse((HIER / "ki_bild.py").read_text(encoding="utf-8")).body:
        if isinstance(knoten, ast.Import):
            oben |= {a.name.split(".")[0] for a in knoten.names}
        elif isinstance(knoten, ast.ImportFrom):
            oben.add((knoten.module or "").split(".")[0])
    erlaubt = {"__future__", "hashlib", "html", "json", "math", "os", "re", "shutil", "sys", "threading", "pathlib",
               "numpy", "ki_modelle"}
    pruefe("ki_bild.py lädt oben nur Standardbibliothek + NumPy (keine Windows-DLL, kein Zusatzpaket)", oben <= erlaubt,
           str(sorted(oben - erlaubt)))
    alt_name, alt_sc, alt_ram, alt_halb = os.name, getattr(os, "sysconf", None), kb.arbeitsspeicher_gb, os.environ.pop("MGD_KI_HALB", None)
    werte, halb = {}, []
    try:
        os.name = "posix"                                          # wie unter macOS/Linux: Speicher über sysconf
        os.sysconf = lambda k: {"SC_PAGE_SIZE": 4096, "SC_PHYS_PAGES": 4 * 1024 ** 2}[k]          # 16 GiB
        werte["posix"] = kb.arbeitsspeicher_gb()
        os.sysconf = lambda k: (_ for _ in ()).throw(ValueError(k))
        werte["unbekannt"] = kb.arbeitsspeicher_gb()
        os.name = alt_name
        for ram in (64, 4, None):                                  # sparsam (float16) unabhängig vom Speicher
            kb.arbeitsspeicher_gb = lambda r=ram: r
            halb.append(kb.BildModell("x").halb)
        os.environ["MGD_KI_HALB"] = "0"                            # float32 nur ausdrücklich
        halb.append(kb.BildModell("x").halb)
    finally:
        os.name, kb.arbeitsspeicher_gb = alt_name, alt_ram
        if alt_sc is None:
            del os.sysconf
        else:
            os.sysconf = alt_sc
        os.environ.pop("MGD_KI_HALB", None)
        if alt_halb is not None:
            os.environ["MGD_KI_HALB"] = alt_halb
    pruefe("Arbeitsspeicher unter macOS/Linux (sysconf) erkannt; Gewichte immer sparsam (float16), float32 nur auf Wunsch",
           abs(werte["posix"] - 16) < 1e-6 and werte["unbekannt"] is None and halb == [True, True, True, False], f"{werte} {halb}")
    erg = kb.parallel(lambda i: kb.parallel(lambda j: (i, j, threading.current_thread().name.startswith("ki-bild")),
                                            range(3)), range(4))
    pruefe("Threads: verschachtelt läuft innen nacheinander (kein Hängenbleiben), Ergebnisse in Reihenfolge",
           erg == [[(i, j, kb.FADEN > 1) for j in range(3)] for i in range(4)], str(erg[:1]))
    with tempfile.TemporaryDirectory() as leer:
        r = subprocess.run([sys.executable, str(HIER / "ki_bild.py"), "--erzeugen=a goose on a meadow"], capture_output=True,
                           env=dict(os.environ, MGD_KI_BILD=leer, MGD_SPRACHE="en", PYTHONIOENCODING="utf-8"), timeout=120)
    aus = r.stdout.decode("utf-8", "replace")
    pruefe("Befehlszeile ohne Modell: freundlicher Hinweis statt Absturz (Rückgabe 1)",
           r.returncode == 1 and "Download AI image model" in aus and "Traceback" not in aus + r.stderr.decode("utf-8", "replace"),
           aus[-160:])


def test_bild_aendern(p, se):
    """Karten-Editor: neues Bild für eine vorhandene Karte – Prüfung wie in Schritt 1, Sicherung, Rückgängig."""
    print("\n[E11] Karte bearbeiten: Bild ändern")
    from urllib.parse import quote
    bilder = p / "bilder"

    def bildinfo(f):                                                 # mit „with“: Windows hält offene Dateien fest
        with Image.open(f) as im:
            return im.size, im.format


    _, kd = se.json("/api/karten")
    k = next(k for k in kd["karten"] if k["existiert"] and k["es"].strip() and k["bild"].endswith(".jpg"))
    name, alt = k["bild"], (bilder / k["bild"]).read_bytes()
    puffer = io.BytesIO()
    Image.new("RGB", (640, 900), (30, 160, 90)).save(puffer, "PNG")
    code, d = se.json(f"/api/entwurf?name=neu.png&karte={quote(name)}", roh=puffer.getvalue())
    pruefe("Bild ändern: Entwurf für die Karte, gleicher Dateiname, Hinweis aufs Aufheben",
           code == 200 and d.get("karte") == name and d.get("dateiname") == name and d.get("ok")
           and (d.get("meldungen") or [{}])[0].get("code") == "e_ersetzt"
           and "e_umwandeln" in [m["code"] for m in d["meldungen"]], str(d)[:200])
    _, liste = se.json("/api/entwuerfe")
    _, ideen = se.json("/api/ideen")
    pruefe("Bild ändern: Entwurf trägt die Karte, erscheint nicht bei den Ideen",
           any(e["id"] == d.get("id") and e["karte"] == name for e in liste)
           and not any(e["id"] == d.get("id") for e in ideen.get("entwuerfe", [])))
    c1, _ = se.json("/api/entwurf?name=a.jpg&karte=gibt-es-nicht.jpg", roh=jpg())
    c2, _ = se.json("/api/entwurf?name=a.jpg&karte=..%2Fkarten.csv", roh=jpg())
    pruefe("Bild ändern: unbekannte Karte und Pfad-Ausbruch abgewiesen", c1 == 404 and c2 == 400, f"{c1}, {c2}")
    _, d1 = se.json("/api/entwurf-pruefen", {"id": d.get("id"), "de": "Gans anders", "es": "otro", "drehung": 90})
    pruefe("Bild ändern: Texte der Karte lassen sich dabei nicht überschreiben",
           d1.get("de") == k["de"] and d1.get("es") == "" and d1.get("drehung") == 90, str(d1)[:160])
    code, r = se.json("/api/entwurf-uebernehmen", {"id": d.get("id"), "de": "Gans anders", "es": "otro", "drehung": 90,
                                                    "fit": "contain"})
    karte = next((x for x in r.get("karten", {}).get("karten", []) if x["bild"] == name), {})
    groesse, fmt = bildinfo(bilder / name)
    pruefe("Bild ändern: übernommen – gedreht, als JPG unter altem Namen, Texte/Notiz/Status gleich",
           code == 200 and r.get("name") == name and fmt == "JPEG" and groesse == (900, 640)
           and all(karte.get(f) == k[f] for f in ("de", "es", "notiz", "uebersetzung", "aktiv")), str(r)[:200])
    gesichert = (r.get("rueckgaengig") or {}).get("sicherung")
    pruefe("Bild ändern: alte Fassung in bilder/_entfernt aufgehoben",
           bool(gesichert) and (bilder / "_entfernt" / gesichert).read_bytes() == alt, str(gesichert))
    code, _ = se.json("/api/karte-bild-zurueck", r.get("rueckgaengig") or {})
    aufgehoben = [f for f in (bilder / "_entfernt").glob(Path(name).stem + "*") if bildinfo(f)[0] == (900, 640)]
    pruefe("Rückgängig: altes Bild wieder da, das neue bleibt aufgehoben",
           code == 200 and (bilder / name).read_bytes() == alt and len(aufgehoben) == 1, str(code))
    c1, _ = se.json("/api/karte-bild-zurueck", {"bild": name, "sicherung": "../karten.csv"})
    c2, _ = se.json("/api/karte-bild-zurueck", {"bild": name, "sicherung": "gibt-es-nicht.jpg"})
    pruefe("Rückgängig: nur mit einer Sicherung aus bilder/_entfernt", c1 == 400 and c2 == 400, f"{c1}, {c2}")
    code, d2 = se.json(f"/api/entwurf?name=gleich.jpg&karte={quote(name)}", roh=alt)
    codes = [m["code"] for m in d2.get("meldungen", [])]
    pruefe("Bild ändern: dasselbe Bild wird freundlich erkannt", "e_gleich" in codes and "b_doppelt" not in codes,
           str(codes))
    se.json("/api/entwurf-weg", {"id": d2.get("id")})
    _, kd = se.json("/api/karten")
    se.json("/api/karten", {"karten": kd["karten"] + [dict(bild="gans-ohne-bild.jpg", aktiv=True, de="Gans ohne Bild",
                                                           es="sin imagen", notiz="", fit="contain")]})
    puffer = io.BytesIO()
    Image.new("RGB", (880, 630), (200, 60, 60)).save(puffer, "WEBP")
    _, d3 = se.json("/api/entwurf?name=x.webp&karte=gans-ohne-bild.jpg", roh=puffer.getvalue())
    code, r3 = se.json("/api/entwurf-uebernehmen", {"id": d3.get("id")})
    ok = (bilder / "gans-ohne-bild.jpg").is_file() and bildinfo(bilder / "gans-ohne-bild.jpg")[1] == "JPEG"
    pruefe("Bild ändern: fehlendes Bild einer Karte ergänzt (WEBP → JPG)",
           (d3.get("meldungen") or [{}])[0].get("code") == "e_ergaenzt" and code == 200 and ok
           and (r3.get("rueckgaengig") or {}).get("sicherung", "x") is None, str(r3)[:160])


def test_handy_feinschliff(p, se):
    """E12: was am Handy anders sein muss – ohne WLAN prüfbar (Seite, Werkzeugliste, Dateifelder, Texte)."""
    print("\n[E12] Handy: Kennung, Nur-am-Rechner-Werkzeuge, HEIC-sichere Dateifelder, Touch-Texte")
    _, _, seite = se.anfrage("/")
    pruefe("Am Rechner: Seite weiß, dass sie nicht am Handy läuft", b'const AM_HANDY = "0" === "1"' in seite)
    _, liste = se.json("/api/werkzeuge")
    nur = {w["id"] for w in liste if w.get("nur_rechner")}
    pruefe("Werkzeugliste markiert, was nur am Rechner geht",
           nur == {"ordner-projekt", "ordner-bilder", "ordner-ausgabe", "csv", "programmstart", "handy"}, str(sorted(nur)))
    html = (p / "ui" / "index.html").read_text(encoding="utf-8")
    pruefe("Datei-Felder nennen Bildtypen (iPhone wandelt HEIC dann in JPG)",
           'accept="image/*' not in html and 'dateiWaehlen("image/*' not in html
           and 'const BILD_ACCEPT = "image/jpeg,' in html)
    schluessel = set(re.findall(r"\b([a-z0-9_]+_touch):", html))
    pruefe("Handy-Texte (…_touch) gibt es in allen drei Sprachen",
           len(schluessel) >= 10 and all(html.count(k + ":") == 3 for k in schluessel), str(sorted(schluessel)))


def test_ki_bild_laden(ordner):
    """E13: Bildmodell laden – Katalog fest, Download fortsetzbar, Prüfsumme, Platz; mit kleinem Testserver."""
    print("\n[E13] KI-Bilder: Modell laden (Katalog, Fortsetzen, Prüfsummen)")
    import hashlib
    import http.server
    import threading
    import ki_bild as kb
    m = kb.MODELL
    pruefe("Katalog: feste Revisionen, Prüfsummen, ~3,6 GB, nur huggingface.co",
           all(re.fullmatch(r"[0-9a-f]{40}", d["rev"]) and (re.fullmatch(r"[0-9a-f]{64}", d["sha256"] or "")
               or re.fullmatch(r"[0-9a-f]{40}", d["git_sha1"] or "")) for d in m["dateien"])
           and 3.4e9 < kb.platz_noetig() < 3.7e9 and kb._url(m["dateien"][0]).startswith("https://huggingface.co/")
           and len({d["name"] for d in m["dateien"]}) == len(m["dateien"]), f"{kb.platz_noetig():,}")
    inhalt = {"a/gross.bin": bytes(range(256)) * 40000, "b/klein.txt": b"gans\n" * 1000}   # 10 MB + 5 KB
    abrufe = []

    class Bote(http.server.BaseHTTPRequestHandler):            # kann Range – wie Hugging Face
        def do_GET(self):
            pfad = self.path.split("/resolve/x/", 1)[-1]
            daten = inhalt.get(pfad)
            abrufe.append((pfad, self.headers.get("Range")))
            if daten is None:
                self.send_response(404)
                self.end_headers()
                return
            ab = int(re.match(r"bytes=(\d+)-", self.headers["Range"]).group(1)) if self.headers.get("Range") else 0
            self.send_response(206 if ab else 200)
            self.send_header("Content-Length", str(len(daten) - ab))
            self.end_headers()
            self.wfile.write(daten[ab:])

        def log_message(self, *a):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Bote)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    basis = f"http://127.0.0.1:{server.server_address[1]}"
    git = lambda b: hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()  # noqa: E731
    probe = dict(id="probe", titel="Probe", lizenz="MIT", dateien=[
        kb._d("gross.bin", "r", "x", "a/gross.bin", len(inhalt["a/gross.bin"]),
              sha256=hashlib.sha256(inhalt["a/gross.bin"]).hexdigest()),
        kb._d("klein.txt", "r", "x", "b/klein.txt", len(inhalt["b/klein.txt"]), git_sha1=git(inhalt["b/klein.txt"]))])
    try:
        ordner.mkdir(parents=True)
        (ordner / "gross.bin.part").write_bytes(inhalt["a/gross.bin"][:3_000_000])      # abgebrochener Download
        st = kb.lade(melde=lambda t: None, ordner=ordner, modell=probe, basis=basis)
        pruefe("Download setzt fort (Range) und prüft SHA-256 bzw. Git-SHA-1",
               st["installiert"] and ("a/gross.bin", "bytes=3000000-") in abrufe
               and (ordner / "gross.bin").read_bytes() == inhalt["a/gross.bin"]
               and not (ordner / "gross.bin.part").exists(), str(abrufe))
        abrufe.clear()
        kb.lade(melde=lambda t: None, ordner=ordner, modell=probe, basis=basis)
        pruefe("Schon vollständig → nichts wird erneut geladen", abrufe == [] and kb.status(ordner, probe)["installiert"])
        falsch = dict(probe, dateien=[dict(probe["dateien"][1], name="falsch.txt", git_sha1="0" * 40)])
        try:
            kb.lade(melde=lambda t: None, ordner=ordner, modell=falsch, basis=basis)
            ok = False
        except ValueError:
            ok = True
        pruefe("Falsche Prüfsumme → nichts installiert, Teildatei weg",
               ok and not (ordner / "falsch.txt").exists() and not (ordner / "falsch.txt.part").exists())
        fehlt = dict(probe, dateien=[dict(probe["dateien"][1], name="fehlt.txt", pfad="gibt/es-nicht.txt")])
        try:
            kb.lade(melde=lambda t: None, ordner=ordner, modell=fehlt, basis=basis)
            ok = False
        except ConnectionError as e:
            ok = "noch einmal" in str(e) or "again" in str(e) or "vuelve" in str(e)
        pruefe("Quelle nicht erreichbar → freundliche Meldung zum Fortsetzen", ok)
        riesig = dict(probe, dateien=[dict(probe["dateien"][0], name="riesig.bin", bytes=10 ** 15)])
        try:
            kb.lade(melde=lambda t: None, ordner=ordner, modell=riesig, basis=basis)
            ok = False
        except OSError as e:
            ok = not isinstance(e, ConnectionError) and "GB" in str(e)
        pruefe("Zu wenig Platz → klare Meldung vor dem Download", ok and not (ordner / "riesig.bin.part").exists())
        ram = kb.arbeitsspeicher_gb()
        pruefe("Arbeitsspeicher wird erkannt (ohne Zusatzpaket)", ram is None or 0.5 < ram < 4096, str(ram))
    finally:
        server.shutdown()


def test_ki_bild_text(echt):
    """E14: Text-Teil des Bildmodells – safetensors-Leser, CLIP-Tokenizer, Text-Encoder (Mini-Gewichte + echtes Modell)."""
    print("\n[E14] KI-Bilder: safetensors, Tokenizer, Text-Encoder")
    import numpy as np
    import ki_bild as kb
    import ki_modelle as km
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        a = (np.arange(24, dtype=np.float32).reshape(2, 3, 4) - 7) / 3
        kb.speichere_safetensors(tmp / "t.safetensors", {"a": a.astype(np.float16), "b": a, "i": np.arange(5)}, {"x": 1})
        st = kb.SafeTensors(tmp / "t.safetensors")
        bf = (a.view(np.uint32) >> 16).astype(np.uint16)                      # bfloat16 = obere 16 Bit von float32
        j = json.dumps({"c": {"dtype": "BF16", "shape": [2, 3, 4], "data_offsets": [0, bf.nbytes]}}).encode()
        (tmp / "bf.safetensors").write_bytes(len(j).to_bytes(8, "little") + j + bf.tobytes())
        bfwert = kb.SafeTensors(tmp / "bf.safetensors").f32("c")
        kaputt = bytearray((tmp / "t.safetensors").read_bytes()[:-8])           # Datei zu kurz → abgelehnt
        (tmp / "kaputt.safetensors").write_bytes(bytes(kaputt))
        try:
            kb.SafeTensors(tmp / "kaputt.safetensors")
            abgelehnt = False
        except ValueError:
            abgelehnt = True
        pruefe("safetensors: F16/F32/I64/BF16 lesen (eingeblendet), kaputte Datei abgelehnt",
               np.abs(st.f32("a") - a).max() < 2e-3 and np.array_equal(st.f32("b"), a) and st.roh("i").tolist() == [0, 1, 2, 3, 4]
               and st.meta == {"x": "1"} and np.abs(bfwert - a).max() < 0.05 and abgelehnt)   # bfloat16: 7 Bit Mantisse
        st.schliesse()

        vocab = {"<|startoftext|>": 0, "<|endoftext|>": 1, "!": 2, "g": 3, "o": 4, "s": 5, "e</w>": 6, "go": 7, "goo": 8,
                 "se</w>": 9, "goose</w>": 10, ",</w>": 11, "!</w>": 12, "ente</w>": 13}
        (tmp / "v.json").write_text(json.dumps(vocab), encoding="utf-8")
        (tmp / "m.txt").write_text("#version: 0.2\ng o\ngo o\ns e</w>\ngoo se</w>\n", encoding="utf-8")
        tok = kb.ClipTokenizer(tmp / "v.json", tmp / "m.txt", pad="!", laenge=8)
        pruefe("Tokenizer: Byte-Pair-Encoding, Kürzen mit Ende-Token, Auffüllen",
               tok.ids("Goose, GOOSE!") == [0, 10, 11, 10, 12, 1, 2, 2]
               and tok.ids("goose " * 20)[-1] == 1 and len(tok.ids("goose " * 20)) == 8, str(tok.ids("Goose, GOOSE!")))

        werte = iter(np.sin(np.arange(1, 20000, dtype=np.float64) * 12.9898) * 0.5)
        zuf = lambda *form: np.array([next(werte) for _ in range(int(np.prod(form)))], np.float32).reshape(form)  # noqa: E731
        d, schichten, koepfe, inner, nv = 8, 2, 2, 16, 14
        w = {"text_model.embeddings.token_embedding.weight": zuf(nv, d),
             "text_model.embeddings.position_embedding.weight": zuf(77, d),
             "text_model.final_layer_norm.weight": 1 + zuf(d), "text_model.final_layer_norm.bias": zuf(d),
             "text_projection.weight": zuf(6, d)}
        for i in range(schichten):
            p = f"text_model.encoder.layers.{i}."
            for n in ("q_proj", "k_proj", "v_proj", "out_proj"):
                w[p + f"self_attn.{n}.weight"], w[p + f"self_attn.{n}.bias"] = zuf(d, d), zuf(d)
            for n in ("layer_norm1", "layer_norm2"):
                w[p + n + ".weight"], w[p + n + ".bias"] = 1 + zuf(d), zuf(d)
            w[p + "mlp.fc1.weight"], w[p + "mlp.fc1.bias"] = zuf(inner, d), zuf(inner)
            w[p + "mlp.fc2.weight"], w[p + "mlp.fc2.bias"] = zuf(d, inner), zuf(d)
        kb.speichere_safetensors(tmp / "te.safetensors", {k: v.astype(np.float32) for k, v in w.items()})
        ids = [0, 5, 3, 9, 13, 2, 2]                                           # 13 = größte ID = Ende-Token

        def referenz(akt):                                    # Lehrbuch-Fassung: Schleifen über Köpfe und Token
            ln = lambda x, n: km.layer_norm(x, w[n + ".weight"], w[n + ".bias"])  # noqa: E731
            x = w["text_model.embeddings.token_embedding.weight"][ids] + w["text_model.embeddings.position_embedding.weight"][:len(ids)]
            zust = [x]
            for i in range(schichten):
                p = f"text_model.encoder.layers.{i}."
                h = ln(x, p + "layer_norm1")
                q, k, v = (h @ w[p + f"self_attn.{n}.weight"].T + w[p + f"self_attn.{n}.bias"] for n in ("q_proj", "k_proj", "v_proj"))
                o = np.zeros_like(h)
                dk = d // koepfe
                for kopf in range(koepfe):
                    s = slice(kopf * dk, (kopf + 1) * dk)
                    for tt in range(len(ids)):
                        z = np.array([q[tt, s] @ k[u, s] / np.sqrt(dk) for u in range(tt + 1)])
                        z = np.exp(z - z.max())
                        z /= z.sum()
                        o[tt, s] = sum(z[u] * v[u, s] for u in range(tt + 1))
                x = x + o @ w[p + "self_attn.out_proj.weight"].T + w[p + "self_attn.out_proj.bias"]
                h = akt(ln(x, p + "layer_norm2") @ w[p + "mlp.fc1.weight"].T + w[p + "mlp.fc1.bias"])
                x = x + h @ w[p + "mlp.fc2.weight"].T + w[p + "mlp.fc2.bias"]
                zust.append(x)
            return zust[-2], ln(x, "text_model.final_layer_norm")

        abw = 0.0
        for akt_name, akt in (("quick_gelu", lambda x: x / (1 + np.exp(-1.702 * x))), ("gelu", km.gelu)):
            te = kb.ClipText(kb.SafeTensors(tmp / "te.safetensors"), dict(hidden_size=d, num_hidden_layers=schichten,
                                                                          num_attention_heads=koepfe, hidden_act=akt_name))
            v1, l1 = (x[0] for x in te(ids))
            v2, l2 = referenz(akt)
            pool = te.gepoolt(l1[None], ids)[0]
            abw = max(abw, float(np.abs(v1 - v2).max()), float(np.abs(l1 - l2).max()),
                      float(np.abs(pool - l2[4] @ w["text_projection.weight"].T).max()))
            te.st.schliesse()
        pruefe("Text-Encoder (CLIP-Aufbau) = Lehrbuch-Fassung, vorletzte Schicht und Satz-Einbettung", abw < 1e-4, f"{abw:.1e}")

    if not (echt and kb.status(echt)["installiert"]):
        print("          (Bildmodell nicht geladen – Prüfungen mit dem echten Modell übersprungen; Werkzeuge → KI-Bildmodell laden)")
        return
    teil = kb.TextTeil(echt)
    pruefe("Echter Tokenizer: „a photo of a cat“ → bekannte CLIP-IDs, Auffüllen wie SDXL",
           teil.tok1.ids("a photo of a cat")[:8] == [49406, 320, 1125, 539, 320, 2368, 49407, 49407]
           and teil.tok2.ids("a photo of a cat")[7] == teil.tok2.pad_id != 49407, str(teil.tok1.ids("a photo of a cat")[:8]))
    t0 = time.time()
    saetze = ("a photo of a goose", "a photo of a duck", "a red sports car")
    emb, pool = teil(list(saetze))
    dauer = time.time() - t0
    cos = lambda a, b: float(a @ b / np.linalg.norm(a) / np.linalg.norm(b))  # noqa: E731
    g, e, auto = pool
    pruefe("Echte Text-Encoder: Form 77×2048 + 1280, Gans näher an Ente als an Sportwagen",
           emb.shape == (3, 77, 2048) and g.shape == (1280,) and cos(g, e) > cos(g, auto) + 0.05
           and np.isfinite(emb).all(), f"{cos(g, e):.2f} / {cos(g, auto):.2f}")
    pruefe("Echte Text-Encoder: schnell genug (< 8 s für drei Sätze)", dauer < 8, f"{dauer:.1f} s")


def test_ki_bild_netz(echt):
    """E15: Bildteil – Bausteine, VegaRT-Einrechnung, UNet (Vega/SDXL- und SD-1.5-Aufbau), LCM, Decoder. Mini-Gewichte
    gegen eine Lehrbuch-Fassung (float64, Schleifen, LoRA als eigener Zweig), die die Gewichte nach Name und Form selbst
    anlegt – passt ein Name, eine Form oder die Reihenfolge nicht, weicht das Ergebnis ab. Dazu ein echter Probelauf."""
    print("\n[E15] KI-Bilder: Bildnetz, VegaRT, LCM-Verfahren, Decoder")
    import numpy as np
    import ki_bild as kb
    vorrat = np.sin(np.arange(1, 2000001, dtype=np.float64) * 12.9898) * 0.5         # ohne numpy.random
    pos = [0]

    def zuf(*form):
        n = int(np.prod(form))
        pos[0] = 0 if pos[0] + n > len(vorrat) else pos[0]
        pos[0] += n
        return vorrat[pos[0] - n:pos[0]].reshape(form)

    def l_conv(x, w, b=None, schritt=1):                     # Faltung als Summe über die Gewichts-Lagen
        bn, h, wd, _ = x.shape
        k = w.shape[2]
        xp = np.pad(x, ((0, 0), (k // 2, k // 2), (k // 2, k // 2), (0, 0)))
        y = sum(np.einsum("bhwc,oc->bhwo", xp[:, ky:ky + h, kx:kx + wd], w[:, :, ky, kx]) for ky in range(k) for kx in range(k))
        y = y[:, ::schritt, ::schritt]
        return y + b if b is not None else y

    def l_gn(x, g, b, gruppen, eps):
        y, k = np.empty_like(x), x.shape[-1] // gruppen
        for i in range(x.shape[0]):
            for j in range(gruppen):
                t = x[i, ..., j * k:(j + 1) * k]
                y[i, ..., j * k:(j + 1) * k] = (t - t.mean()) / np.sqrt(t.var() + eps)
        return y * g + b

    l_silu = lambda x: x / (1 + np.exp(-x))  # noqa: E731
    l_gelu = np.vectorize(lambda v: 0.5 * v * (1 + math.erf(v / math.sqrt(2))))
    l_ln = lambda x, g, b: (x - x.mean(-1, keepdims=True)) / np.sqrt(x.var(-1, keepdims=True) + 1e-5) * g + b  # noqa: E731

    def l_attn(q, k, v, koepfe):
        o, d = np.zeros_like(q), q.shape[-1] // koepfe
        for i in range(q.shape[0]):
            for h in range(koepfe):
                s = slice(h * d, (h + 1) * d)
                z = q[i, :, s] @ k[i, :, s].T / math.sqrt(d)
                z = np.exp(z - z.max(-1, keepdims=True))
                o[i, :, s] = (z / z.sum(-1, keepdims=True)) @ v[i, :, s]
        return o

    def l_zeit(t, dim):                                      # flip_sin_to_cos: erst cos, dann sin
        e = np.asarray(t, np.float64).reshape(-1, 1) * np.exp(-math.log(10000) * np.arange(dim // 2) / (dim // 2))
        return np.concatenate([np.cos(e), np.sin(e)], -1)

    class Fabrik:
        """Gewichte nach Name + Form, beim ersten Abruf angelegt. Mit LoRA: jede Schicht außer Zeit-/Zusatz-Einbettung und
        conv_in/conv_out bekommt einen Zweig Rang 2, alpha 1 (Faktor ½) – gerechnet getrennt, nicht eingerechnet."""
        AUSNAHMEN = ("time_embedding", "add_embedding", "conv_in", "conv_out")

        def __init__(self, lora=False, skala=1.7):
            self.w, self.lora, self.skala = {}, ({} if lora else None), skala

        def __call__(self, name, *form):
            if name not in self.w:
                if len(form) == 1:
                    self.w[name] = 1 + 0.2 * zuf(*form) if "norm" in name and name.endswith("weight") else 0.2 * zuf(*form)
                else:
                    self.w[name] = zuf(*form) * self.skala / math.sqrt(np.prod(form[1:]))
            return self.w[name]

        def _zweig(self, name, o, c, k):
            if self.lora is None or name.startswith(self.AUSNAHMEN):
                return None
            s = "lora_unet_" + name.replace(".", "_")
            if s + ".alpha" not in self.lora:
                self.lora[s + ".lora_down.weight"] = zuf(2, c, k, k) / math.sqrt(c * k * k) if k else zuf(2, c) / math.sqrt(c)
                self.lora[s + ".lora_up.weight"] = zuf(o, 2, 1, 1) if k else zuf(o, 2)
                self.lora[s + ".alpha"] = np.array(1.0)
            return self.lora[s + ".lora_down.weight"], self.lora[s + ".lora_up.weight"]

        def lin(self, x, name, o, c, bias=True):
            y = x @ self(name + ".weight", o, c).T + (self(name + ".bias", o) if bias else 0)
            z = self._zweig(name, o, c, 0)
            return y if z is None else y + 0.5 * (x @ z[0].T) @ z[1].T

        def conv(self, x, name, o, c, k, schritt=1, bias=True):
            y = l_conv(x, self(name + ".weight", o, c, k, k), self(name + ".bias", o) if bias else None, schritt)
            z = self._zweig(name, o, c, k)
            return y if z is None else y + 0.5 * l_conv(l_conv(x, z[0], None, schritt), z[1])

        def gn(self, x, name, gruppen, eps=1e-5):
            c = x.shape[-1]
            return l_gn(x, self(name + ".weight", c), self(name + ".bias", c), gruppen, eps)

        def ln(self, x, name):
            c = x.shape[-1]
            return l_ln(x, self(name + ".weight", c), self(name + ".bias", c))

    def l_unet(F, cfg, x, t, ctx, pool=None, ids=None):
        ch, n, gr, lpb = cfg["block_out_channels"], len(cfg["block_out_channels"]), cfg["norm_num_groups"], cfg["layers_per_block"]
        liste = lambda v: list(v) if isinstance(v, list) else [v] * n  # noqa: E731
        koepfe, tiefe = liste(cfg["attention_head_dim"]), liste(cfg.get("transformer_layers_per_block", 1))
        e = F.lin(l_silu(F.lin(l_zeit([t] * len(x), ch[0]), "time_embedding.linear_1", 4 * ch[0], ch[0])),
                  "time_embedding.linear_2", 4 * ch[0], 4 * ch[0])
        if cfg.get("addition_embed_type") == "text_time":
            a = np.concatenate([pool, l_zeit(ids.ravel(), cfg["addition_time_embed_dim"]).reshape(len(x), -1)], -1)
            e = e + F.lin(l_silu(F.lin(a, "add_embedding.linear_1", 4 * ch[0], a.shape[1])), "add_embedding.linear_2",
                          4 * ch[0], 4 * ch[0])

        def resnet(h, p, o):
            c = h.shape[-1]
            r = F.conv(l_silu(F.gn(h, p + "norm1", gr)), p + "conv1", o, c, 3)
            r = r + F.lin(l_silu(e), p + "time_emb_proj", o, 4 * ch[0])[:, None, None, :]
            r = F.conv(l_silu(F.gn(r, p + "norm2", gr)), p + "conv2", o, o, 3)
            return (F.conv(h, p + "conv_shortcut", o, c, 1) if c != o else h) + r

        def transformer(h, p, k, d):
            b, hh, ww, c = h.shape
            s = F.gn(h, p + "norm", gr, 1e-6).reshape(b, hh * ww, c)
            linear = cfg["use_linear_projection"]
            s = F.lin(s, p + "proj_in", c, c) if linear else F.conv(s[:, :, None], p + "proj_in", c, c, 1)[:, :, 0]
            for i in range(d):
                q = f"{p}transformer_blocks.{i}."
                for nr, kv, kd in (("1", None, c), ("2", ctx, ctx.shape[-1])):
                    m = F.ln(s, q + "norm" + nr)
                    kv = m if kv is None else kv
                    a = l_attn(F.lin(m, q + f"attn{nr}.to_q", c, c, False), F.lin(kv, q + f"attn{nr}.to_k", c, kd, False),
                               F.lin(kv, q + f"attn{nr}.to_v", c, kd, False), k)
                    s = s + F.lin(a, q + f"attn{nr}.to_out.0", c, c)
                f = F.lin(F.ln(s, q + "norm3"), q + "ff.net.0.proj", 8 * c, c)
                s = s + F.lin(f[..., :4 * c] * l_gelu(f[..., 4 * c:]), q + "ff.net.2", c, 4 * c)
            s = F.lin(s, p + "proj_out", c, c) if linear else F.conv(s[:, :, None], p + "proj_out", c, c, 1)[:, :, 0]
            return s.reshape(b, hh, ww, c) + h

        h = F.conv(x, "conv_in", ch[0], x.shape[-1], 3)
        reste = [h]
        for i, typ in enumerate(cfg["down_block_types"]):
            for j in range(lpb):
                h = resnet(h, f"down_blocks.{i}.resnets.{j}.", ch[i])
                if "CrossAttn" in typ:
                    h = transformer(h, f"down_blocks.{i}.attentions.{j}.", koepfe[i], tiefe[i])
                reste.append(h)
            if i < n - 1:
                h = F.conv(h, f"down_blocks.{i}.downsamplers.0.conv", ch[i], ch[i], 3, 2)
                reste.append(h)
        h = resnet(h, "mid_block.resnets.0.", ch[-1])
        if cfg["mid_block_type"] == "UNetMidBlock2DCrossAttn":
            h = resnet(transformer(h, "mid_block.attentions.0.", koepfe[-1], tiefe[-1]), "mid_block.resnets.1.", ch[-1])
        for i, typ in enumerate(cfg["up_block_types"]):
            for j in range(lpb + 1):
                h = resnet(np.concatenate([h, reste.pop()], -1), f"up_blocks.{i}.resnets.{j}.", ch[::-1][i])
                if "CrossAttn" in typ:
                    h = transformer(h, f"up_blocks.{i}.attentions.{j}.", koepfe[::-1][i], tiefe[::-1][i])
            if i < n - 1:
                h = F.conv(h.repeat(2, 1).repeat(2, 2), f"up_blocks.{i}.upsamplers.0.conv", h.shape[-1], h.shape[-1], 3)
        return F.conv(l_silu(F.gn(h, "conv_norm_out", gr)), "conv_out", 4, ch[0], 3)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        speichern = lambda name, d: kb.speichere_safetensors(tmp / name, {k: np.asarray(v, np.float32) for k, v in d.items()})  # noqa: E731
        abw = lambda a, b: float(np.abs(np.asarray(a, np.float64) - b).max() / (np.abs(b).max() + 1e-12))  # noqa: E731
        f32 = lambda a: np.asarray(a, np.float32)  # noqa: E731

        # Bausteine einzeln (Batch 2, Schrittweite 1/2, 1×1 und 3×3; Werte groß genug für mehrere Thread-Stücke)
        x = zuf(2, 96, 96, 24) * 3
        w3, w1, b = zuf(16, 24, 3, 3) / 8, zuf(16, 24, 1, 1) / 4, zuf(16)
        g, bb = 1 + zuf(24) * 0.3, zuf(24)
        q, k, v = zuf(2, 3000, 32), zuf(2, 100, 32), zuf(2, 100, 32)
        h = zuf(4, 1000, 160) * 4
        fehler = max(abw(kb.falte(f32(x), kb._rechenform(f32(w3), np.float32), f32(b)), l_conv(x, w3, b)),
                     abw(kb.falte(f32(x), kb._rechenform(f32(w3), np.float32), f32(b), 2), l_conv(x, w3, b, 2)),
                     abw(kb.falte(f32(x), kb._rechenform(f32(w1), np.float32)), l_conv(x, w1)),
                     abw(kb.group_norm(f32(x + 5), f32(g), f32(bb), 4, 1e-6), l_gn(x + 5, g, bb, 4, 1e-6)),
                     abw(kb.group_norm(f32(x), f32(g), f32(bb), 8, 1e-5, True), l_silu(l_gn(x, g, bb, 8, 1e-5))),
                     abw(kb.layer_norm(f32(x), f32(g), f32(bb)), l_ln(x, g, bb)),
                     abw(kb.geglu(f32(h)), h[..., :80] * l_gelu(h[..., 80:])),
                     abw(kb.silu(f32(h)), l_silu(h)),
                     abw(kb.aufmerksamkeit(f32(q), f32(k), f32(v), 4), l_attn(q, k, v, 4)))
        pruefe("Bausteine = Lehrbuch: Faltung (3×3, 1×1, Schrittweite 2), GroupNorm (+SiLU), LayerNorm, GEGLU, Attention",
               fehler < 2e-5, f"{fehler:.1e}")

        # UNet im Vega/SDXL-Aufbau (text_time, lineare Projektion, Mitte ohne Attention) mit LoRA, und im SD-1.5-Aufbau
        cfg_xl = dict(block_out_channels=[8, 16, 16], layers_per_block=2, norm_num_groups=4, attention_head_dim=[1, 2, 2],
                      transformer_layers_per_block=[1, 1, 2], down_block_types=["DownBlock2D", "CrossAttnDownBlock2D",
                      "CrossAttnDownBlock2D"], up_block_types=["CrossAttnUpBlock2D", "CrossAttnUpBlock2D", "UpBlock2D"],
                      mid_block_type="UNetMidBlock2D", use_linear_projection=True, addition_embed_type="text_time",
                      addition_time_embed_dim=4, flip_sin_to_cos=True, freq_shift=0)
        cfg_15 = dict(block_out_channels=[8, 16, 16], layers_per_block=1, norm_num_groups=4, attention_head_dim=2,
                      down_block_types=["CrossAttnDownBlock2D", "CrossAttnDownBlock2D", "DownBlock2D"],
                      up_block_types=["UpBlock2D", "CrossAttnUpBlock2D", "CrossAttnUpBlock2D"],
                      mid_block_type="UNetMidBlock2DCrossAttn", use_linear_projection=False)
        x, ctx, pool = zuf(2, 8, 12, 4), zuf(2, 5, 12), zuf(2, 6)
        ids = np.array([[64, 96, 0, 0, 64, 96], [48, 64, 8, 4, 64, 96]], np.float64)
        F = Fabrik(lora=True)
        ref = l_unet(F, cfg_xl, x, 500, ctx, pool, ids)
        speichern("u.safetensors", F.w)
        speichern("l.safetensors", F.lora)
        ergebnisse, takte = {}, []
        for halb in (False, True):
            gw = kb.Gewichte(kb.SafeTensors(tmp / "u.safetensors"), kb.SafeTensors(tmp / "l.safetensors"), halb=halb).vorbereiten()
            un = kb.UNet(gw, cfg_xl)
            un.takt = takte.append
            ergebnisse[halb] = abw(un(f32(x), 500, f32(ctx), f32(pool), f32(ids)), ref)
        pruefe("UNet Vega/SDXL-Aufbau mit eingerechnetem LoRA (VegaRT-Art) = Lehrbuch mit LoRA-Zweig (float32 und float16)",
               ergebnisse[False] < 1e-4 and ergebnisse[True] < 3e-2 and len(F.lora) // 3 == len(gw._lora) > 200,   # fp16-Rundung
               f"{ergebnisse[False]:.1e} / {ergebnisse[True]:.1e}, {len(gw._lora)} LoRA-Module")
        F15 = Fabrik()
        ref15 = l_unet(F15, cfg_15, x[:1], 999, ctx[:1])
        speichern("u15.safetensors", F15.w)
        un15 = kb.UNet(kb.Gewichte(kb.SafeTensors(tmp / "u15.safetensors"), halb=False).vorbereiten(), cfg_15)
        e15 = abw(un15(f32(x[:1]), 999, f32(ctx[:1])), ref15)
        pruefe("UNet SD-1.5-Aufbau (Projektion als 1×1-Faltung, Mitte mit Attention, gleiche Köpfe) = Lehrbuch",
               e15 < 1e-4, f"{e15:.1e}")

        zaehler = [0]
        un.abbruch = lambda: (zaehler.__setitem__(0, zaehler[0] + 1), zaehler[0] >= 4)[1]
        try:
            un(f32(x), 500, f32(ctx), f32(pool), f32(ids))
            abgebrochen = False
        except kb.Abgebrochen:
            abgebrochen = True
        falsch = {"lora_unet_gibt_es_nicht.lora_down.weight": np.zeros((2, 4)), "lora_unet_gibt_es_nicht.lora_up.weight":
                  np.zeros((4, 2)), "lora_unet_gibt_es_nicht.alpha": np.array(1.0)}
        speichern("falsch.safetensors", falsch)
        try:
            kb.Gewichte(kb.SafeTensors(tmp / "u.safetensors"), kb.SafeTensors(tmp / "falsch.safetensors"))
            lora_abgelehnt = False
        except ValueError:
            lora_abgelehnt = True
        pruefe("Fortschritt je Block bis 100 %, Abbruch mitten im Netz, fremdes LoRA abgelehnt",
               takte[:un.takte] == sorted(takte[:un.takte]) and takte[un.takte - 1] == 1.0 and abgebrochen
               and zaehler[0] == 4 and lora_abgelehnt, f"{un.takte} Takte, {zaehler[0]} Abfragen")

        lcm4, lcm6 = kb.LCM(4), kb.LCM(6)
        x0, rauschen = zuf(1, 4, 6, 4), zuf(1, 4, 6, 4) * 2
        a = lcm4.acp[999]
        rueck = lcm4.schritt(3 - 3, rauschen, np.sqrt(a) * x0 + np.sqrt(1 - a) * rauschen, kb.Zufall(1))[1]
        letzt = lcm4.schritt(3, zuf(1, 4, 6, 4), x0, kb.Zufall(1))
        pruefe("LCM-Verfahren: Zeitschritte wie diffusers (4: 999 759 499 259), Rauschen weg → Bild, letzter Schritt ohne Zufall",
               lcm4.zeiten.tolist() == [999, 759, 499, 259] and lcm6.zeiten.tolist() == [999, 839, 679, 499, 339, 179]
               and abs(a - 0.00466) < 1e-4 and abw(rueck, x0) < 1e-3 and letzt[0] is letzt[1],
               str(lcm4.zeiten.tolist()))

        z1, z2 = kb.Zufall(42).normal((200, 501)), kb.Zufall(42)
        z2a, z2b = z2.normal((100, 501)), z2.normal((100, 501))
        quelle = (HIER / "ki_bild.py").read_text(encoding="utf-8")
        pruefe("Zufall ohne numpy.random: gleicher Startwert → gleiche Werte (auch stückweise), Mittel 0, Streuung 1",
               np.array_equal(z1, np.concatenate([z2a, z2b])) and abs(z1.mean()) < 0.01 and abs(z1.std() - 1) < 0.01
               and not np.array_equal(z1[:5], kb.Zufall(43).normal((5, 501))) and "np.random" not in quelle,
               f"{z1.mean():.3f} / {z1.std():.3f}")

        # Decoder: VAE (SDXL-Aufbau, verkleinert) und TAESDXL (Aufbau „Decoder“, 8 statt 64 Kanäle)
        cfg_vae = dict(block_out_channels=[4, 8], layers_per_block=1, norm_num_groups=2, scaling_factor=0.5)
        FV = Fabrik()

        def l_vae(z):
            def res(h, p, o):
                c = h.shape[-1]
                r = FV.conv(l_silu(FV.gn(h, p + "norm1", 2, 1e-6)), p + "conv1", o, c, 3)
                r = FV.conv(l_silu(FV.gn(r, p + "norm2", 2, 1e-6)), p + "conv2", o, o, 3)
                return (FV.conv(h, p + "conv_shortcut", o, c, 1) if c != o else h) + r
            h = FV.conv(FV.conv(z / 0.5, "post_quant_conv", 4, 4, 1), "decoder.conv_in", 8, 4, 3)
            h = res(h, "decoder.mid_block.resnets.0.", 8)
            p = "decoder.mid_block.attentions.0."
            t = FV.gn(h, p + "group_norm", 2, 1e-6).reshape(len(h), -1, 8)
            t = FV.lin(l_attn(*(FV.lin(t, p + n, 8, 8) for n in ("to_q", "to_k", "to_v")), 1), p + "to_out.0", 8, 8)
            h = res(h + t.reshape(h.shape), "decoder.mid_block.resnets.1.", 8)
            for i, o in enumerate((8, 4)):
                for j in range(2):
                    h = res(h, f"decoder.up_blocks.{i}.resnets.{j}.", o)
                if i == 0:
                    h = FV.conv(h.repeat(2, 1).repeat(2, 2), "decoder.up_blocks.0.upsamplers.0.conv", o, o, 3)
            return FV.conv(l_silu(FV.gn(h, "decoder.conv_norm_out", 2, 1e-6)), "decoder.conv_out", 3, 4, 3)

        FT = Fabrik(skala=4.5)                                                  # ReLU-Kette: größere Gewichte
        relu = lambda t: np.maximum(t, 0)  # noqa: E731

        def l_tae(z):
            def block(h, i):
                r = relu(FT.conv(relu(FT.conv(h, f"{i}.conv.0", 8, 8, 3)), f"{i}.conv.2", 8, 8, 3))
                return relu(FT.conv(r, f"{i}.conv.4", 8, 8, 3) + h)
            h = relu(FT.conv(np.tanh(z / 3) * 3, "1", 8, 4, 3))
            for teil in ((3, 4, 5, 7), (8, 9, 10, 12), (13, 14, 15, 17)):
                for i in teil[:3]:
                    h = block(h, i)
                h = FT.conv(h.repeat(2, 1).repeat(2, 2), str(teil[3]), 8, 8, 3, bias=False)
            return FT.conv(block(h, 18), "19", 3, 8, 3)

        z = zuf(1, 4, 6, 4) * 2
        for fab, funk in ((FV, l_vae), (FT, l_tae)):
            funk(z)
            if fab is FV:                                                       # kaum Werte am Rand 0/1
                fab.w["decoder.conv_out.weight"] = fab.w["decoder.conv_out.weight"] * 0.3
            else:
                fab.w["19.bias"] = fab.w["19.bias"] + 0.5
        rv, rt = np.clip(l_vae(z) / 2 + 0.5, 0, 1), np.clip(l_tae(z), 0, 1)
        speichern("vae.safetensors", FV.w)
        speichern("tae.safetensors", FT.w)
        vtakte = []
        with kb.SafeTensors(tmp / "vae.safetensors") as st:
            ev = abw(kb.VAEDecoder(st, cfg_vae)(f32(z), takt=vtakte.append), rv)
        et = abw(kb.TAEDecoder(kb.SafeTensors(tmp / "tae.safetensors"))(f32(z)), rt)
        pruefe("Decoder VAE (SDXL-Aufbau) und TAESDXL = Lehrbuch, Fortschritt im VAE bis 100 %",
               ev < 1e-4 and et < 1e-4 and 0.02 < rv.std() and 0.02 < rt.std() and vtakte == sorted(vtakte)
               and abs(vtakte[-1] - 1) < 1e-9, f"{ev:.1e} / {et:.1e}, Streuung {rv.std():.2f} / {rt.std():.2f}")

    if not (echt and kb.status(echt)["installiert"]):
        print("          (Bildmodell nicht geladen – Probelauf mit dem echten Modell übersprungen)")
        return
    anteile, gefragt = [], [0]
    t0 = time.time()
    r = kb.BildModell(echt).erzeuge("a realistic photo of a white goose standing on a green meadow, natural light",
                                    breite=384, hoehe=256, schritte=3, startwert=7, fortschritt=anteile.append,
                                    abbruch=lambda: gefragt.__setitem__(0, gefragt[0] + 1))
    dauer = time.time() - t0
    bild = np.asarray(r["bild"], np.float64)
    grau = bild.mean(-1)
    nachbar = float(np.corrcoef(grau[:, :-1].ravel(), grau[:, 1:].ravel())[0, 1])
    tae = kb.TAEDecoder(kb.SafeTensors(Path(echt) / "taesdxl_decoder.safetensors"))(r["latent"])[0]
    gleich = float(np.corrcoef(tae.mean(-1).ravel(), grau.ravel())[0, 1])
    pruefe("Echtes Bildmodell (Vega + VegaRT): Bild 384×256 in 3 Schritten, kein Rauschen, VAE ≈ TAESDXL",
           r["bild"].size == (384, 256) and grau.std() > 8 and nachbar > 0.8 and gleich > 0.9,
           f"Nachbarn {nachbar:.2f}, VAE~TAE {gleich:.2f}, Streuung {grau.std():.0f}")
    pruefe("Echtes Bildmodell: Fortschritt steigt bis 100 %, Abbruch wird laufend abgefragt, flott (< 60 s)",
           anteile == sorted(anteile) and anteile[-1] == 1.0 and gefragt[0] >= 50 and dauer < 60,
           f"{len(anteile)} Meldungen, {gefragt[0]} Abfragen, {dauer:.0f} s")


def test_lan(se, daten):
    """Handy-Zugang direkt per http.client gegen die WLAN-Adresse (ohne Browser). Ohne Heimnetz: nur Grundprüfung."""
    import http.client
    code, r = se.json("/api/lan")
    pruefe("Handy-Zugang: standardmäßig aus", code == 200 and r["an"] is False)
    if not r.get("ip_gefunden"):
        print("  (kein Heimnetz – weitere Handy-Prüfungen übersprungen)")
        return
    gemerkt = tg._freier_port()
    (Path(daten) / "handy-port.txt").write_text(str(gemerkt), encoding="utf-8")
    code, r = se.json("/api/lan", {"an": True})
    pruefe("Handy-Zugang: einschalten liefert Adresse und PIN", code == 200 and r["an"] and re.fullmatch(r"\d{6}", r["pin"] or ""))
    ip, port = r["adresse"][7:].rsplit(":", 1)
    pruefe("Handy: gleicher Port wie beim letzten Mal (Lesezeichen bleiben gültig)", port == str(gemerkt), f"{port} ≠ {gemerkt}")
    pin = r["pin"]

    def anfrage(methode, weg, daten=None, kopf=None, host=None):
        c = http.client.HTTPConnection(ip, int(port), timeout=10)
        try:
            k = {"Host": host or f"{ip}:{port}", **(kopf or {})}
            roh = json.dumps(daten).encode() if daten is not None else None
            if roh is not None:
                k["Content-Type"] = "application/json"
            c.request(methode, weg, body=roh, headers=k)
            a = c.getresponse()
            return a.status, {x.lower(): y for x, y in a.getheaders()}, a.read()
        finally:
            c.close()

    try:
        code, _, inhalt = anfrage("GET", "/")
        pruefe("Handy: ohne Cookie erst die PIN-Seite", code == 200 and b"/lan-pin" in inhalt and se.token.encode() not in inhalt)
        code, _, _ = anfrage("GET", "/", host=f"127.0.0.1:{port}")
        pruefe("Handy: fremder Host-Kopf abgewiesen", code == 403)
        code, _, _ = anfrage("GET", "/api/karten")
        pruefe("Handy: Daten nur mit Sitzung", code == 403)
        code, _, _ = anfrage("POST", "/lan-pin", {"pin": "x"}, {"Origin": "http://boese.example"})
        pruefe("Handy: PIN von fremder Seite abgewiesen", code == 403)
        code, kopf, _ = anfrage("POST", "/lan-pin", {"pin": pin})
        keks = kopf.get("set-cookie", "").split(";")[0]
        pruefe("Handy: richtige PIN → Sitzung", code == 200 and keks.startswith("mgd_"))
        code, _, inhalt = anfrage("GET", "/", kopf={"Cookie": keks})
        pruefe("Handy: Oberfläche nach der PIN", code == 200 and b"const TOKEN" in inhalt)
        pruefe("Handy: Seite weiß, dass sie am Handy läuft", b'const AM_HANDY = "1" === "1"' in inhalt)
        code, _, _ = anfrage("GET", "/api/karten", kopf={"Cookie": keks})
        pruefe("Handy: Karten lesen", code == 200)
        mit = {"Cookie": keks, "X-GL-Token": se.token}
        ergebnisse = [anfrage("POST", w, {"bestaetigt": True}, mit)[0] for w in ("/api/deinstallieren", "/api/beenden", "/api/lan")]
        pruefe("Handy: Beenden, Deinstallieren, Handy-Schalter gesperrt", ergebnisse == [403, 403, 403], str(ergebnisse))
        code, _, _ = anfrage("POST", "/api/werkzeug", {"id": "ordner-ausgabe"}, mit)
        pruefe("Handy: Ordner öffnen am Rechner gesperrt", code == 403, str(code))
        code, _, _ = anfrage("GET", "/api/ki-bild", kopf={"Cookie": keks})
        code2, _, _ = anfrage("POST", "/api/ki-bild-text", {"beschreibung": "on a meadow"}, mit)
        pruefe("Handy: KI-Bild-Fenster nutzbar (gerechnet wird am Rechner)", code == 200 and code2 == 200, f"{code} {code2}")
        for _ in range(5):
            anfrage("POST", "/lan-pin", {"pin": "000000" if pin != "000000" else "111111"})
        code, r = se.json("/api/lan")
        pruefe("Handy: nach 5 falschen PINs aus", code == 200 and r["an"] is False)
    finally:
        se.json("/api/lan", {"an": False})


def test_starter(p, daten):
    print("\n[E4] Startprogramm: Fenster-Start und Schutz beim Deinstallieren")
    os.environ["MGD_DATEN"] = str(daten)
    sys.path.insert(0, str(p))
    import importlib
    import starter
    importlib.reload(starter)
    aufrufe = []

    class Falsch:
        def __init__(self, befehl, **kw):
            aufrufe.append(befehl)

    alt, echt = starter.subprocess.Popen, starter.finde_browser
    starter.subprocess.Popen = Falsch
    try:
        starter.finde_browser = lambda: [dict(id="edge", name="Microsoft Edge", pfad="C:/edge.exe", fenster=True)]
        starter.schreibe_start_wahl(dict(art="fenster", browser="edge"))
        ok = starter.oeffne_nach_wahl("http://127.0.0.1:1/?k=x")
        pruefe("Eigenes Fenster: Browser mit --app", ok and aufrufe and "--app=http://127.0.0.1:1/?k=x" in aufrufe[-1])
        starter.schreibe_start_wahl(dict(art="browser", browser="standard"))
        pruefe("Standard-Browser: nichts Eigenes gestartet", starter.oeffne_nach_wahl("http://x") is False)
        starter.finde_browser = lambda: []
        starter.schreibe_start_wahl(dict(art="fenster", browser="edge"))
        pruefe("Ohne passenden Browser: Rückfall auf Standard", starter.oeffne_nach_wahl("http://x") is False)
    finally:
        starter.subprocess.Popen, starter.finde_browser = alt, echt
    pruefe("Deinstallieren erlaubt im echten Programmordner", starter.deinstallation_erlaubt())
    alt_wurzel = starter.WURZEL
    try:
        starter.WURZEL = Path.home()
        pruefe("Deinstallieren verweigert für den Benutzerordner", not starter.deinstallation_erlaubt())
        starter.WURZEL = Path(Path.home().anchor)
        pruefe("Deinstallieren verweigert für ein Laufwerk", not starter.deinstallation_erlaubt())
    finally:
        starter.WURZEL = alt_wurzel
    pruefe("Startprogramm: neue Texte in allen Sprachen", all(set(starter.TEXTE[s]) == set(starter.TEXTE["de"])
                                                              for s in ("en", "es")))
    pruefe("Update übernimmt auch Ideen", "ideen.json" in starter.NUTZER_DATEIEN and "ideen" in starter.NUTZER_ORDNER)


def test_mac(tmp):
    """Mac-Teile des Startprogramms ohne Mac: osacompile/codesign/xattr werden nur aufgezeichnet."""
    print("\n[E8] Mac: App im Ordner „Programme“ und Browser im Benutzerordner")
    import platform
    import plistlib
    import shlex
    import starter
    tmp = Path(tmp)
    app = tmp / "Applications" / "Me Goos-ta Deutsch.app"
    skript = tmp / "Daten \"mit\" 'Zeichen'; $HOME" / "starte.py"
    python = "/Users/ana maría/Library/Application Support/Me-Goos-ta-Deutsch/python/bin/python3"
    befehle = []

    def lauf(befehl, **kw):
        befehle.append([str(t) for t in befehl])
        if befehl[0] == "osacompile":                                    # so legt macOS ein Applet an
            inhalt = Path(befehl[2]) / "Contents"
            (inhalt / "MacOS").mkdir(parents=True)
            (inhalt / "Resources").mkdir()
            (inhalt / "MacOS" / "applet").write_bytes(b"\xcf\xfa\xed\xfe")
            (inhalt / "Resources" / "Assets.car").write_bytes(b"x")
            (inhalt / "Info.plist").write_bytes(plistlib.dumps({"CFBundleExecutable": "applet", "CFBundleIconName": "applet",
                                                                  "CFBundleIdentifier": "com.apple.ScriptEditor.id.x"}))
        return subprocess.CompletedProcess(befehl, 0, b"", b"")

    def aufruf_aus(teile):
        """Python, starte.py und --app als ganze Wörter direkt hintereinander?"""
        return python in teile and teile[teile.index(python) + 1:teile.index(python) + 3] == [str(skript), "--app"]

    alt = (starter.MAC_APP, subprocess.run, shutil.which, sys.executable, platform.machine)
    starter.MAC_APP = app
    subprocess.run = lauf
    shutil.which = lambda n: f"/usr/bin/{n}" if n in ("osacompile", "codesign") else None
    sys.executable = python
    try:
        starter.mac_app(skript)
        info = plistlib.loads((app / "Contents" / "Info.plist").read_bytes())
        pruefe("Mac: App als Applet (echtes Programm für Intel und Apple-Chips)",
               any(b[0] == "osacompile" for b in befehle) and info.get("CFBundleExecutable") == "applet"
               and info.get("CFBundleIdentifier") == "de.me-goos-ta-deutsch.app" and info.get("CFBundleName") == starter.PRODUKT
               and info.get("LSUIElement") is True, str(info))
        osa = next((b for b in befehle if b[0] == "osacompile"), [])
        quelle = osa[osa.index("-e") + 1] if "-e" in osa else ""
        m = re.fullmatch(r'do shell script "((?:[^"\\]|\\.)*)"', quelle)
        text = re.sub(r"\\(.)", r"\1", m.group(1)) if m else ""
        pruefe("Mac: Applet startet Python + starte.py --app im Hintergrund (Sonderzeichen sicher)",
               bool(m) and aufruf_aus(shlex.split(text)) and text.endswith(" &") and "PYTHONNOUSERSITE=1" in text, quelle[:200])
        symbol = (starter.HIER / "assets" / "me-goosta-symbol.icns").stat().st_size
        pruefe("Mac: eigenes Symbol, Skript-Symbol entfernt, neu signiert",
               (app / "Contents" / "Resources" / "applet.icns").stat().st_size == symbol
               and not (app / "Contents" / "Resources" / "Assets.car").exists() and "CFBundleIconName" not in info
               and any(b[:2] == ["codesign", "--force"] for b in befehle))
        shutil.which = lambda n: None                                    # ohne osacompile → Rückfall
        platform.machine = lambda: "arm64"
        starter.mac_app(skript)
        info = plistlib.loads((app / "Contents" / "Info.plist").read_bytes())
        start = (app / "Contents" / "MacOS" / "me-goosta").read_text(encoding="utf-8")
        letzte = start.strip().splitlines()[-1]
        pruefe("Mac: Rückfall Skript-App ersetzt die alte, mit Architektur arm64 zuerst",
               not (app / "Contents" / "MacOS" / "applet").exists() and info.get("CFBundleExecutable") == "me-goosta"
               and info.get("LSArchitecturePriority") == ["arm64", "x86_64"] and start.startswith("#!/bin/sh\n")
               and letzte.startswith("exec ") and aufruf_aus(shlex.split(letzte)), letzte[:200])
    finally:
        starter.MAC_APP, subprocess.run, shutil.which, sys.executable, platform.machine = alt
    # Name, den es systemweit nicht gibt – auf einem echten Mac (CI) liegt Chrome sonst schon in /Applications
    chrome = tmp / "Applications" / "MGD Test Chrome.app" / "Contents" / "MacOS" / "Google Chrome"
    chrome.parent.mkdir(parents=True)
    chrome.write_bytes(b"")
    alt = (starter.WIN, starter.MAC, Path.__dict__.get("home"), starter.BROWSER)
    starter.WIN, starter.MAC = False, True
    starter.BROWSER = [("chrome", "Google Chrome", True,
                        dict(win=[], mac=["/Applications/MGD Test Chrome.app/Contents/MacOS/Google Chrome"], linux=[]))]
    Path.home = staticmethod(lambda: tmp)
    try:
        gefunden = {b["id"]: b["pfad"] for b in starter.finde_browser()}
    finally:
        starter.WIN, starter.MAC, starter.BROWSER = alt[0], alt[1], alt[3]
        if alt[2] is None:
            del Path.home
        else:
            Path.home = alt[2]
    pruefe("Mac: Browser auch in ~/Applications gefunden", gefunden.get("chrome") == str(tmp) + "/Applications/MGD Test Chrome.app"
           "/Contents/MacOS/Google Chrome", str(gefunden))


def exec_zerlegen(zeile):
    """Exec= einer .desktop-Datei so lesen, wie es die Desktop Entry Specification vorschreibt (Gegenprobe)."""
    roh = re.sub(r"\\(.)", lambda m: {"s": " ", "n": "\n", "t": "\t", "r": "\r"}.get(m.group(1), m.group(1)), zeile)
    teile = re.findall(r'"((?:[^"\\]|\\.)*)"|(\S+)', roh)
    return [re.sub(r"\\([\"`$\\])", r"\1", a).replace("%%", "%") if a else b for a, b in teile]


def test_linux(p, tmp):
    """Linux-Teile ohne Linux: Startdatei, Menüeintrag, Terminal, Schutz beim Deinstallieren."""
    print("\n[E9] Linux: Startdatei, Menüeintrag, Terminal, Schutz beim Deinstallieren")
    import shlex
    import starter
    tmp = Path(tmp)
    sh = p.parent / starter.START_LINUX
    roh = sh.read_bytes() if sh.exists() else b""
    liste = re.search(r"^\s*for t in ([\w\- ]+); do", roh.decode("utf-8"), re.M)
    pruefe("Linux-Startdatei: Unix-Zeilenenden, #!/bin/sh, ruft die Mac-Startdatei auf, gleiche Terminal-Liste",
           roh.startswith(b"#!/bin/sh\n") and b"\r" not in roh and starter.START_MAC.encode() in roh
           and liste is not None and liste.group(1).split() == [n for n, _ in starter.LINUX_TERMINALS])
    python = "/home/ana maría/.local/share/me-goos-ta-deutsch/python/bin/python3"
    skript = tmp / 'Daten "50 %" $HOME `x` \\ ok' / "starte.py"
    alt = (starter.LINUX_DESKTOP, sys.executable, shutil.which, subprocess.run)
    starter.LINUX_DESKTOP = tmp / "applications" / "me-goos-ta-deutsch.desktop"
    sys.executable = python
    aufrufe = []
    shutil.which = lambda n: f"/usr/bin/{n}" if n == "update-desktop-database" else None
    subprocess.run = lambda befehl, **kw: aufrufe.append(befehl) or subprocess.CompletedProcess(befehl, 0, b"", b"")
    try:
        starter.linux_eintrag(skript)
        text = starter.LINUX_DESKTOP.read_text(encoding="utf-8")
    finally:
        starter.LINUX_DESKTOP, sys.executable, shutil.which, subprocess.run = alt
    exec_zeile = next((z[5:] for z in text.splitlines() if z.startswith("Exec=")), "")
    pruefe("Linux-Menüeintrag: Exec liest sich zurück als Python + starte.py --app (Sonderzeichen sicher)",
           text.startswith("[Desktop Entry]\n") and exec_zerlegen(exec_zeile) == [python, str(skript), "--app"]
           and "Terminal=false" in text and "Categories=Education;" in text and aufrufe, exec_zeile)

    def terminal(nur):
        alt_which = shutil.which
        shutil.which = lambda n: f"/usr/bin/{n}" if n == nur else None
        try:
            return starter.linux_terminal(["/py thon", "/s/starter.py", "--konsole"])
        finally:
            shutil.which = alt_which

    pruefe("Linux-Terminal: je Programm die richtige Art, Befehl und Argumente zu übergeben",
           terminal("gnome-terminal") == ["/usr/bin/gnome-terminal", "--", "/py thon", "/s/starter.py", "--konsole"]
           and terminal("xfce4-terminal")[1] == "-x" and terminal("konsole")[1] == "-e"
           and terminal("kitty") == ["/usr/bin/kitty", "/py thon", "/s/starter.py", "--konsole"]
           and terminal("kgx")[1:] == ["-e", shlex.join(["/py thon", "/s/starter.py", "--konsole"])]
           and terminal("gibt-es-nicht") is None)
    heim = tmp / "heim"
    (heim / ".config").mkdir(parents=True)
    (heim / ".config" / "user-dirs.dirs").write_text('XDG_DOWNLOAD_DIR="$HOME/Mis descargas"\n', encoding="utf-8")
    ordner = {n: heim / n for n in ("Descargas", "Mis descargas", "Spiele")}
    ordner["Unterordner"] = heim / "Descargas" / "Me-Goos-ta-Deutsch"
    for o in ordner.values():
        o.mkdir(parents=True, exist_ok=True)
        (o / starter.START_LINUX).write_text("#!/bin/sh\n", encoding="utf-8")
    alt = (starter.WURZEL, starter.WIN, Path.__dict__.get("home"), os.environ.get("XDG_CONFIG_HOME"))
    erlaubt = {}
    starter.WIN = False
    Path.home = staticmethod(lambda: heim)
    os.environ["XDG_CONFIG_HOME"] = str(heim / ".config")
    try:
        for name, o in ordner.items():
            starter.WURZEL = o
            erlaubt[name] = starter.deinstallation_erlaubt()
    finally:
        starter.WURZEL, starter.WIN = alt[:2]
        if alt[2] is None:
            del Path.home
        else:
            Path.home = alt[2]
        if alt[3] is None:
            os.environ.pop("XDG_CONFIG_HOME", None)
        else:
            os.environ["XDG_CONFIG_HOME"] = alt[3]
    pruefe("Deinstallieren: nie „Descargas“ oder den Download-Ordner aus user-dirs.dirs, aber ein Unterordner",
           erlaubt == {"Descargas": False, "Mis descargas": False, "Spiele": True, "Unterordner": True}, str(erlaubt))


def test_ki_faltung():
    """Die schnelle Faltung (ohne im2col) und der Puffer der dichten Blöcke rechnen wie die Lehrbuch-Fassung."""
    print("\n[E10] KI-Vergrößerung: schnelle Faltung rechnet wie die einfache")
    import numpy as np
    import ki_modelle as km
    import random

    class Zufall:                       # ohne numpy.random: dessen DLLs sperrt Smart App Control bei ganz neuen Fassungen
        def __init__(self, saat):
            self.r = random.Random(saat)

        def standard_normal(self, form):
            form = form if isinstance(form, tuple) else (form,)
            return np.array([self.r.gauss(0, 1) for _ in range(math.prod(form))]).reshape(form)

        def random(self, form):
            return np.array([self.r.random() for _ in range(math.prod(form))]).reshape(form)

    rng = Zufall(7)

    def einfach(x, w, b=None):                                       # im2col, 'same' mit Nullrand
        o, _, k, _ = w.shape
        p = k // 2
        xp = np.pad(x, ((p, p), (p, p), (0, 0)))
        f = np.lib.stride_tricks.sliding_window_view(xp, (k, k), axis=(0, 1)).reshape(x.shape[0] * x.shape[1], -1)
        return (f @ w.reshape(o, -1).T + (0 if b is None else b)).reshape(x.shape[0], x.shape[1], o)

    abw, alt = 0.0, km._STREIFEN_BYTES
    try:
        for h, wd, c, o, k, streifen in ((13, 21, 3, 16, 3, alt), (30, 9, 24, 5, 3, alt), (8, 8, 6, 6, 1, alt),
                                         (11, 7, 4, 3, 5, alt), (40, 130, 8, 16, 3, 50_000)):
            km._STREIFEN_BYTES = streifen                                # klein = viele Streifen
            x = rng.standard_normal((h, wd, c)).astype(np.float32)
            w = (rng.standard_normal((o, c, k, k)) * 0.2).astype(np.float32)
            b = rng.standard_normal(o).astype(np.float32)
            abw = max(abw, float(np.abs(km.conv(x, w, b) - einfach(x, w, b)).max()))
    finally:
        km._STREIFEN_BYTES = alt
    pruefe("Faltung ohne im2col = einfache Faltung (auch in Streifen, 1×1 und 5×5)", abw < 1e-4, f"{abw:.1e}")

    gewichte, feat, wachs = {}, 8, 4
    formen = {"conv_first": (feat, 3), "conv_body": (feat, feat), "conv_up1": (feat, feat), "conv_up2": (feat, feat),
              "conv_hr": (feat, feat), "conv_last": (3, feat)}
    for j in (1, 2, 3):
        for i in range(1, 6):
            formen[f"body.0.rdb{j}.conv{i}"] = (feat if i == 5 else wachs, feat + (i - 1) * wachs)
    for name, (o, c) in formen.items():
        gewichte[name + ".weight"] = (rng.standard_normal((o, c, 3, 3)) * 0.15).astype(np.float32)
        gewichte[name + ".bias"] = (rng.standard_normal(o) * 0.1).astype(np.float32)
    netz = km.RRDBNet(gewichte, 4, 1)

    def referenz(x):
        c = lambda n, x: einfach(x, gewichte[n + ".weight"], gewichte[n + ".bias"])   # noqa: E731
        lr = lambda x: np.where(x >= 0, x, np.float32(0.2) * x)                          # noqa: E731
        f = k = c("conv_first", x)
        r = k
        for j in (1, 2, 3):
            teile = [r]
            for i in range(1, 6):
                y = c(f"body.0.rdb{j}.conv{i}", np.concatenate(teile, axis=2))
                if i < 5:
                    teile.append(lr(y))
            r = y * np.float32(0.2) + r
        k = r * np.float32(0.2) + k
        f = f + c("conv_body", k)
        f = lr(c("conv_up1", f.repeat(2, 0).repeat(2, 1)))
        f = lr(c("conv_up2", f.repeat(2, 0).repeat(2, 1)))
        return c("conv_last", lr(c("conv_hr", f)))

    x = rng.random((12, 10, 3)).astype(np.float32)
    a, b = netz(x), referenz(x)
    pruefe("Real-ESRGAN-Netz (dichte Blöcke im Puffer) = Lehrbuch-Fassung", a.shape == (48, 40, 3)
           and float(np.abs(a - b).max()) < 1e-4, f"{float(np.abs(a - b).max()):.1e}")


WT_VIEJO = """== viejo ({{Sprache|Spanisch}}) ==
=== {{Wortart|Adjektiv|Spanisch}} ===
{{Bedeutungen}}
:[1] {{K|Person}} [[alt]], [[betagt]]
:[2] [[alt]] (nicht neu); [[gebraucht]]

{{Herkunft}}
:von lateinisch ''vetulus''
== viejo ({{Sprache|Portugiesisch}}) ==
{{Bedeutungen}}
:[1] [[falsch]]
"""


def test_woerter():
    print("\n[E6] Gleiche Wörter und Übersetzung Spanisch → Deutsch")
    import erweiterungen as er
    import uebersetzer as ue
    pruefe("Wortvergleich: Groß/klein, Umlaute, Bindestriche, „Gans“",
           er.wort_schluessel("Gans Müde") == er.wort_schluessel("gans-muede") == er.wort_schluessel("GANS MÜDE") == "muede")
    pruefe("Wortvergleich Spanisch: Hauptwort vor „/“, Akzente",
           er.wort_schluessel("Viejo / anciano", True) == er.wort_schluessel("viéjo", True) == "viejo")
    e = ue.wiktionary_deutsch(WT_VIEJO)
    pruefe("Wiktionary: deutsche Bedeutungen aus dem spanischen Abschnitt", [x["text"] for x in e] == ["alt", "betagt", "alt", "gebraucht"],
           str([x["text"] for x in e]))
    aufrufe = []

    def abruf(url, daten, kopf):
        aufrufe.append(url)
        return {"query": {"pages": [{"title": "viejo", "revisions": [{"slots": {"main": {"content": WT_VIEJO}}}]}]}}

    erg = ue.uebersetze("¿viejo?", richtung="es-de", abruf=abruf, einstellungen={"zugestimmt": True, "dienst": "auto"},
                        cache=False)
    pruefe("Übersetzung ES→DE: Vorschlag „alt“, nur das Wort gesendet", erg["alternativen"][0]["text"] == "alt"
           and "titles=viejo" in aufrufe[0] and "%C2%BF" not in aufrufe[0], str(erg)[:160])
    try:
        ue.uebersetze("viejo", richtung="es-de", abruf=abruf, einstellungen={"zugestimmt": False}, cache=False)
        ok = False
    except ue.UebersetzungsFehler as f:
        ok = f.code == "zustimmung"
    pruefe("Übersetzung ES→DE ohne Zustimmung: nichts gesendet", ok and len(aufrufe) == 1)


ECHTES_KI_BILD = None
ECHT_DA = False


def test_hilfe_markdown(p, daten):
    """E19: Markdown-Renderer der Hilfe kommt immer zum Ende (auch bei „|“ ohne Trennzeile, „#####“, Tabelle mit
    Leerzeile), jede mitgelieferte .md in < 2 s; /api/hilfe?doc=spec antwortet schnell; Oberfläche mit Zeitlimit/Abbrechen."""
    print("\n[E19] Hilfe: Markdown-Renderer und Spezifikation")
    import threading
    import gans_ui

    def mit_zeitlimit(fn, sekunden):
        erg = {}
        th = threading.Thread(target=lambda: erg.setdefault("wert", fn()), daemon=True)
        t0 = time.time()
        th.start()
        th.join(sekunden)
        return (None if th.is_alive() else erg.get("wert")), time.time() - t0

    faelle = [("Zeile „|“ ohne Trennzeile", "| ohne Trennzeile\nweiter", "| ohne Trennzeile"),
              ("Überschrift „#####“", "##### fünf\nText", "##### fünf"),
              ("Tabelle mit Leerzeile", "| a | b |\n|---|---|\n| 1 | 2 |\n\n| 3 | 4 |", "| 3 | 4 |"),
              ("Liste und Tabelle gemischt", "- eins\n| x | y |\n1. zwei\n| a |\n|---|\n| b |", "<td>b</td>")]
    for name, text, erwartet in faelle:
        html_, _ = mit_zeitlimit(lambda: gans_ui.markdown_html(text), 2)
        pruefe(f"Markdown kommt zum Ende: {name}", html_ is not None and erwartet in html_, str(html_)[:120])
    for pfad in sorted(HIER.glob("*.md")) + [HIER.parent / "README.md"]:
        text = pfad.read_text(encoding="utf-8")
        html_, dauer = mit_zeitlimit(lambda: gans_ui.markdown_html(text), 2)
        pruefe(f"{pfad.name} wird in < 2 s gerendert", html_ is not None and dauer < 2, f"{dauer:.2f} s")
    proc, se = starte_server(p, daten)
    try:
        erg, dauer = mit_zeitlimit(lambda: se.json("/api/hilfe?doc=spec"), 5)
        code, d = erg or (None, {})
        pruefe("/api/hilfe?doc=spec → 200 in < 5 s mit Handy-Zugang in der Tabelle",
               code == 200 and dauer < 5 and "<td>Handy-Zugang</td>" in d.get("html", ""), f"{code} {dauer:.2f} s")
        code2, d2 = se.json("/api/hilfe?doc=spec")
        pruefe("Spezifikation zwischengespeichert (gleiches HTML beim zweiten Aufruf)", code2 == 200 and d2 == d)
        code3, d3 = se.json("/api/hilfe?doc=leitfaden")
        pruefe("/api/hilfe?doc=leitfaden behält die Form {html, datei}",
               code3 == 200 and set(d3) == {"html", "datei"} and d3["datei"].startswith("LEITFADEN"), str(set(d3)))
    finally:
        proc.terminate()
        proc.wait(10)
    ui = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    lade = ui[ui.index("async function ladeHilfe"):][:4000]
    pruefe("Hilfe-Seite: Zeitlimit, Abbrechen, Nochmal versuchen (de/en/es)",
           "timeout: 20000" in lade and "hilfe-abbrechen" in lade and "hilfe-nochmal" in lade
           and all(ui.count(k + ":") == 3 for k in ("hilfe_abbrechen", "hilfe_nochmal", "anfrage_zeit", "anfrage_abgebrochen")))


def test_spanisch():
    """E20: Sichtbar heißt die Kartensprache nur „Spanisch / Spanish / español“; dass damit das in Mexiko gesprochene
    Spanisch gemeint ist, steht zentral (Über, Hover des Rückseitenfelds, Leitfäden, SPEC, README, LIES MICH)."""
    print("\n[E20] „Mexikanisch“ → „Spanisch“")
    import erweiterungen as er
    import gans_lernkarten as gl
    import gans_ui
    import lernkarten_digital as ld
    mexiko = re.compile(r"[Mm]exik|[Mm]exic|[Mm]éxic")
    erlaubt = {"u_kartensprache_wert", "h_es_feld"}            # Erklärungssätze „wie in Mexiko gesprochen“
    ui = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    paare = re.findall(r"\b([a-z][a-z0-9_]*): (\"(?:[^\"\\]|\\.)*\"|`[^`]*`)", ui)
    falsch = sorted({k for k, v in paare if mexiko.search(v) and k not in erlaubt})
    pruefe("Oberfläche: kein „Mexik…“ in sichtbaren Texten (außer Erklärung)", len(paare) > 500 and not falsch, falsch)
    pruefe("Oberfläche: Erklärung in Über + Hover (de/en/es)",
           all(ui.count(k + ":") == 3 for k in erlaubt | {"u_kartensprache"}) and 'title="${esc(t("h_es_feld"))}"' in ui
           and 'esc(t("u_kartensprache_wert"))' in ui)
    pruefe("Oberfläche: „Wort auf {zs} / Word in {zs} / Palabra en {zs}“ (ab G08 = Name der Kartensprache)",
           'es_feld: "Wort auf {zs}"' in ui and 'es_feld: "Word in {zs}"' in ui and 'es_feld: "Palabra en {zs}"' in ui)

    def werte(x):
        if isinstance(x, dict):
            for v in x.values():
                yield from werte(v)
        elif isinstance(x, str):
            yield x
    py_texte = [gl.MELDUNGEN, gl.PRUEF_MELDUNGEN, er.TEXTE, gans_ui.TEXTE, ld.LERNSEITE_TEXTE]
    falsch = [w[:60] for d in py_texte for w in werte(d) if mexiko.search(w)]
    pruefe("Python-Texte (MELDUNGEN, TEXTE, Lernseite): kein „Mexik…“", not falsch, falsch)
    quellen = ["gans_lernkarten.py", "erweiterungen.py", "gans_ui.py", "starter.py", "lernkarten_digital.py", "uebersetzer.py"]
    falsch = [q for q in quellen if re.search(r"Mexikanisch(?!/Lateinamerikanisch)|Mexican Spanish|español de México", (HIER / q).read_text(encoding="utf-8"))]
    pruefe("Quelltexte ohne „Mexikanisch / Mexican Spanish / español de México“", not falsch, falsch)
    pruefe("Anki-Felder und Lernseite: Spanisch", "Spanisch" in ld.FELDER and "Spanisch" in ld.MODELLNAME
           and ld.LERNSEITE_TEXTE["de"]["richtung1"] == "Bild → Spanisch")
    erklaerung = {"LEITFADEN.md": "in Mexiko gesprochene Spanisch", "LEITFADEN_en.md": "Spanish as spoken in Mexico",
                  "LEITFADEN_es.md": "español que se habla en México", "SPEC.md": "Mexiko gesprochene Spanisch"}
    fehlt = [d for d, s in erklaerung.items() if s not in (HIER / d).read_text(encoding="utf-8")]
    pruefe("Erklärungssatz in Leitfäden de/en/es und SPEC", not fehlt, fehlt)
    readme = (HIER.parent / "README.md").read_text(encoding="utf-8")
    lies = (HIER.parent / "LIES MICH ZUERST.html").read_text(encoding="utf-8")
    pruefe("Erklärungssatz in README und LIES MICH (de/en/es)", "Spanish as spoken in Mexico" in readme
           and all(s in lies for s in ("in Mexiko gesprochene Spanisch", "Spanish as spoken in Mexico",
                                        "español que se habla en México")))


def test_warteschlange(p, daten):
    """E21: Höchstens ein Hintergrundprozess; weitere Aufträge warten, starten automatisch nacheinander, lassen sich
    umsortieren/entfernen/leeren, Abbrechen startet den nächsten, Fehler beim Start blockiert nichts; /api/lauf bleibt
    rückwärtskompatibel."""
    print("\n[E21] Warteschlange")
    import threading
    import gans_ui
    ws = gans_ui.warteschlange

    def lauf(name, sekunden=0.3, vor_start=None):
        x = gans_ui.Lauf("schlaf", name, [sys.executable, "-c", f"import time; time.sleep({sekunden})"], "schlaf")
        x.vor_start = vor_start
        return x

    def warte_bis(fn, sekunden=20):
        ende = time.time() + sekunden
        while time.time() < ende:
            if fn():
                return True
            time.sleep(0.02)
        return False

    alle, hoechstens = [], [0]
    halt = threading.Event()

    def zaehler():                                   # zählt gleichzeitig laufende Prozesse
        while not halt.is_set():
            hoechstens[0] = max(hoechstens[0], sum(1 for x in list(alle) if x.laeuft))
            time.sleep(0.005)
    threading.Thread(target=zaehler, daemon=True).start()
    try:
        a, b, c, d = (lauf(n) for n in "ABCD")
        alle += [a, b, c, d]
        for x in (a, b, c, d):
            ws.einreihen(x)
        st_a, st_b = a.status(), b.status()
        pruefe("Erster Auftrag läuft sofort, zweiter wartet auf Platz 2",
               st_a["laeuft"] and st_b.get("wartet") and st_b["position"] == 2 and not st_b["laeuft"], str(st_b)[:120])
        b.schluessel = ("schlaf", "B")
        doppelt = lauf("B2")
        doppelt.schluessel = ("schlaf", "B")
        pruefe("Gleicher Auftrag wartet nicht doppelt", ws.einreihen(doppelt) is b and len(ws.wartend) == 3)
        reihe = lambda: "".join(x.titel for x in ws.wartend)    # noqa: E731
        ws.aktion("runter", b.id)
        r1 = reihe()
        ws.aktion("hoch", d.id)
        r2 = reihe()
        ws.aktion("als-naechstes", b.id)
        r3 = reihe()
        u = ws.aktion("entfernen", c.id)
        pruefe("runter / hoch / als-nächstes / entfernen", (r1, r2, r3, reihe()) == ("CBD", "CDB", "BCD", "BD")
               and [w["position"] for w in u["wartend"]] == [2, 3], f"{r1} {r2} {r3} {reihe()}")
        try:
            ws.aktion("entfernen", "gibt-es-nicht")
            unbekannt = False
        except gans_ui.Meldung as e:
            unbekannt = e.status == 404
        pruefe("Unbekannter Auftrag → 404", unbekannt)
        fertig = warte_bis(lambda: not ws.aktiv and not ws.wartend)
        pruefe("Schlange arbeitet alles automatisch ab (A, B, D; C entfernt)",
               fertig and [a.code, b.code, d.code] == [0, 0, 0] and c.wartet and c not in ws.fertig)
        pruefe("Nacheinander: jeder startet erst nach dem Ende des vorigen",
               a.ende <= b.start and b.ende <= d.start, f"{a.ende} {b.start} {b.ende} {d.start}")

        def kaputt():
            raise gans_ui.Meldung("ws_modell_weg")
        g, e_, f = lauf("G"), lauf("E", vor_start=kaputt), lauf("F")
        alle += [g, e_, f]
        for x in (g, e_, f):
            ws.einreihen(x)
        warte_bis(lambda: not ws.aktiv and not ws.wartend)
        pruefe("Fehler beim Start → „fertig mit Fehler“, Schlange läuft weiter",
               e_.code == 1 and e_.zeilen and e_.zeilen[-1].startswith("✕") and f.code == 0 and e_ in ws.fertig)
        h, i = lauf("H", 30), lauf("I")
        alle += [h, i]
        ws.einreihen(h)
        ws.einreihen(i)
        warte_bis(lambda: h.laeuft)
        ws.stoppen()
        pruefe("Abbrechen → nächster startet automatisch",
               warte_bis(lambda: i.code == 0) and h.abgebrochen and h.code not in (None, 0))
        j, k, l_ = lauf("J", 30), lauf("K"), lauf("L")
        alle += [j, k, l_]
        for x in (j, k, l_):
            ws.einreihen(x)
        u = ws.aktion("leeren")
        pruefe("Leeren entfernt alle wartenden, der laufende bleibt", not u["wartend"] and u["aktiv"]["id"] == j.id)
        ws.alles_stoppen()
        warte_bis(lambda: not ws.aktiv)
        pruefe("Nie zwei Prozesse gleichzeitig", hoechstens[0] == 1, str(hoechstens[0]))
        pruefe("„Zuletzt erledigt“ höchstens 10, neueste zuerst", len(ws.uebersicht()["fertig"]) <= 10
               and ws.uebersicht()["fertig"][0]["id"] == j.id)
    finally:
        halt.set()
        ws.alles_stoppen()

    proc, se = starte_server(p, daten)
    try:
        code, r1 = se.json("/api/lauf", daten={"art": "generator", "nur": "pruefbogen"})
        code2, r2 = se.json("/api/lauf", daten={"art": "generator", "nur": "vorlagen"})
        code3, r3 = se.json("/api/lauf", daten={"art": "generator", "nur": "vorlagen"})
        pruefe("HTTP: leere Schlange → laeuft wie bisher, danach „wartet“ mit Platz",
               code == 200 and r1.get("laeuft") and code2 == 200 and r2.get("wartet") and r2.get("position") == 2,
               str(r2)[:120])
        pruefe("HTTP: gleicher Auftrag → derselbe Platz", code3 == 200 and r3.get("id") == r2.get("id"))
        _, st = se.json("/api/lauf")
        _, ws_ = se.json("/api/warteschlange")
        _, einer = se.json(f"/api/lauf?id={r2.get('id')}")
        _, status = se.json("/api/status")
        pruefe("HTTP: /api/lauf (aktueller + Anzahl), ?id=, /api/warteschlange, /api/status",
               st.get("id") == r1.get("id") and st.get("warteschlange") == 1 and einer.get("wartet")
               and [w["id"] for w in ws_.get("wartend", [])] == [r2.get("id")] and ws_["aktiv"]["id"] == r1.get("id")
               and status.get("warteschlange") == 2, str(st)[:80])
        code, u = se.json("/api/warteschlange", daten={"aktion": "entfernen", "id": r2.get("id")})
        code4, _ = se.json("/api/warteschlange", daten={"aktion": "entfernen", "id": r2.get("id")})
        pruefe("HTTP: entfernen, danach 404", code == 200 and not u["wartend"] and code4 == 404)
        st = _warte_lauf(se, 120)
        pruefe("HTTP: laufender Auftrag endet normal", st.get("id") == r1.get("id") and st.get("code") == 0)
    finally:
        proc.terminate()
        proc.wait(10)
    ui = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    schluessel = ("ws_titel", "ws_eingereiht", "ws_leeren_frage", "ws_beenden_frage", "ki_wartet", "h_ws_knopf",
                  "h_ws_hoch", "h_ws_runter", "h_ws_naechstes", "h_ws_entfernen", "h_ws_leeren")
    pruefe("Oberfläche: Kopfzeile ⏳, Fenster, Texte de/en/es, Beenden fragt nach, Startknöpfe nicht gesperrt",
           'id="ws-knopf"' in ui and 'id="ws-fenster"' in ui and all(ui.count(k + ":") == 3 for k in schluessel)
           and "oeffneWs(true)" in ui and "S.lauf && S.lauf.laeuft) || !$(\"#befehl-fehler\")" not in ui
           and 'b.disabled = !$("#befehl-fehler").hidden' in ui)


E22_PROZESS = r'''
import json, os, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import tools, ki_modelle, ki_bild, uebersetzer
p, daten, fremd = Path(sys.argv[1]), Path(os.environ["MGD_DATEN"]), Path(os.environ["MGD_KI_BILD"])
e = {}
x2, x4 = p / "modelle" / "realesrgan-x2plus.npz", p / "modelle" / "realesrgan-x4plus.npz"
vorrat = daten / "modelle"
def fehler(fn):
    try:
        fn()
    except tools.ToolFehler as f:
        return [f.code, f.status]
    return None
liste = {t["id"]: t for t in tools.liste()}
e["katalog"] = sorted(liste) == ["bildverbesserung", "ki-bild", "lernen", "sprachen", "uebersetzung"] and \
    60e6 < liste["bildverbesserung"]["groesse"] < 70e6 and 3.4e9 < liste["ki-bild"]["groesse"] < 3.7e9 and \
    liste["uebersetzung"]["groesse"] == 0 and all(set(t["titel"]) == {"de", "en", "es"} and set(t["nutzen"]) == {"de", "en", "es"}
                                                  for t in liste.values())
e["frisch"] = not any(t["installiert"] for t in liste.values()) and tools.erstabfrage_noetig()
x2.write_bytes(b"x2" * 600_000)
uebersetzer.speichere_einstellungen({"zugestimmt": True})
e["uebernahme"] = tools.installiert("bildverbesserung") and tools.installiert("uebersetzung") and not tools.installiert("ki-bild")
e["auftrag"] = [tools.installieren("bildverbesserung"), tools.installieren("bildverbesserung", "x2")]
vorrat.mkdir(parents=True, exist_ok=True)
(vorrat / "realesrgan-x4plus.npz").write_bytes(b"x4" * 600_000)
e["vorrat_zurueck"] = tools.installieren("bildverbesserung") is None and x4.is_file()
fsrcnn = sorted(q.name for q in (p / "modelle").glob("fsrcnn_*.npz"))
r = tools.deinstalliere("bildverbesserung", "x2")
e["teil_weg"] = not x2.exists() and x4.is_file() and tools.installiert("bildverbesserung") and len(r["geloescht"]) == 1
r = tools.deinstalliere("bildverbesserung")
e["alles_weg"] = not x4.exists() and not (vorrat / "realesrgan-x4plus.npz").exists() and r["frei"] >= 2_400_000 and \
    not tools.installiert("bildverbesserung") and sorted(q.name for q in (p / "modelle").glob("fsrcnn_*.npz")) == fsrcnn and \
    len(fsrcnn) == 3 and (p / "karten.csv").is_file() and any((p / "bilder").iterdir())
namen = [d["name"] for d in ki_bild.MODELL["dateien"][:2]]
for n in namen:
    (fremd / n).write_bytes(b"gans")
    (fremd / (n + ".ok")).write_text("{}", encoding="utf-8")
r = tools.deinstalliere("ki-bild")
e["schutz"] = r["abgemeldet"] and not tools.ki_ordner_eigen() and all((fremd / n).is_file() for n in namen) and \
    "ki-bild" in tools.lade_zustand()["abgemeldet"] and not tools.installiert("ki-bild")
e["wieder"] = tools.installieren("ki-bild") == {"art": "ki-bild-laden"} and "ki-bild" not in tools.lade_zustand()["abgemeldet"]
eigen = daten / "modelle" / "ki-bild"
eigen.mkdir(parents=True)
for n in namen:
    (eigen / n).write_bytes(b"gans")
    (eigen / (n + ".part")).write_bytes(b"ga")
(eigen / "eigene-notiz.txt").write_text("bleibt", encoding="utf-8")
os.environ["MGD_KI_BILD"] = str(eigen)
r = tools.deinstalliere("ki-bild")
e["eigen_weg"] = tools.ki_ordner_eigen() and not r["abgemeldet"] and len(r["geloescht"]) == 4 and \
    sorted(q.name for q in eigen.iterdir()) == ["eigene-notiz.txt"]
r = tools.deinstalliere("uebersetzung")
e["ue_weg"] = not uebersetzer.einstellungen_pfad().exists() and not uebersetzer.lade_einstellungen()["zugestimmt"] and \
    not tools.installiert("uebersetzung")
e["ue_zustimmung"] = fehler(lambda: tools.installieren("uebersetzung"))
e["unbekannt"] = fehler(lambda: tools.installieren("gibt-es-nicht"))
vorher = tools.erstabfrage_noetig()
tools.gefragt_setzen()
e["erstabfrage"] = vorher and not tools.erstabfrage_noetig() and (daten / "tools.json").is_file()
print("#e22 " + json.dumps(e))
'''


def test_tools(p, tmp):
    """E22: Tool-Grundgerüst – Katalog, Zustand (Übernahme alter Installationen), Installieren über die Warteschlange,
    Deinstallieren nur der Tool-Dateien, Löschschutz MGD_KI_BILD, Wiederinstallieren, Sperre während eines Laufs,
    Erstabfrage, Starter-Schritt ohne Download. Nie mit dem echten KI-Modell oder echten Downloads."""
    print("\n[E22] Tools: installieren, deinstallieren, Löschschutz, Erstabfrage")
    daten, fremd = tmp / "daten-tools", tmp / "fremd-ki"
    for o in (daten, fremd):
        o.mkdir()
    # 1) Bausteine in einem eigenen Prozess: Module aus der Testkopie, eigener Datenordner, Modellordner außerhalb
    env = dict(os.environ, PYTHONIOENCODING="utf-8", MGD_DATEN=str(daten), MGD_KI_BILD=str(fremd))
    r = subprocess.run([sys.executable, "-c", E22_PROZESS, str(p)], cwd=p, env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=120)
    m = re.search(r"^#e22 (.*)$", r.stdout, re.M)
    e = json.loads(m.group(1)) if m else {}
    if not m:
        print((r.stdout + r.stderr)[-1500:])
    pruefe("Katalog: 5 Tools, Größen aus den Katalogen, Texte de/en/es", e.get("katalog"))
    pruefe("Frisch: nichts installiert → Erstabfrage nötig", e.get("frisch"))
    pruefe("Übernahme: vorhandenes Modell bzw. erteilte Zustimmung zählen als installiert", e.get("uebernahme"))
    pruefe("Installieren liefert den Download-Auftrag (bzw. nichts, wenn schon da)",
           e.get("auftrag") == [{"art": "modell", "modell": "realesrgan-x4plus"}, None], str(e.get("auftrag")))
    pruefe("Kopie im Datenordner → ohne Download zurückgeholt", e.get("vorrat_zurueck"))
    pruefe("Deinstallieren eines Teils (×2) lässt ×4 stehen", e.get("teil_weg"))
    pruefe("Deinstallieren löscht nur Tool-Dateien (FSRCNN, Karten, Bilder bleiben)", e.get("alles_weg"))
    pruefe("Löschschutz: MGD_KI_BILD außerhalb des Datenordners → nur abgemeldet, nichts gelöscht", e.get("schutz"))
    pruefe("Wiederinstallieren nach dem Abmelden", e.get("wieder"))
    pruefe("Eigener Modellordner: nur bekannte Dateien gelöscht, Fremdes bleibt", e.get("eigen_weg"))
    pruefe("Übersetzung deinstallieren: Zustimmung + Einstellungen weg", e.get("ue_weg"))
    pruefe("Übersetzung installieren nur mit Zustimmung (409), unbekanntes Tool → 404",
           e.get("ue_zustimmung") == ["zustimmung", 409] and e.get("unbekannt") == ["tool_unbekannt", 404])
    pruefe("Erstabfrage wird einmal gemerkt (tools.json)", e.get("erstabfrage"))

    # 2) Startprogramm: kein automatischer Download mehr, Kopie aus dem Datenordner wird übernommen
    import importlib.util
    alt_daten = os.environ.get("MGD_DATEN")
    os.environ["MGD_DATEN"] = str(tmp / "daten-starter")
    try:
        spec = importlib.util.spec_from_file_location("starter_e22", p / "starter.py")
        st = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(st)
    finally:
        if alt_daten is None:
            os.environ.pop("MGD_DATEN", None)
        else:
            os.environ["MGD_DATEN"] = alt_daten
    st.DATEN = tmp / "daten-starter"
    schritte, laeufe = [], []

    class Aus:
        def schritt(self, nr, gesamt, text):
            schritte.append((nr, gesamt))

        def unter(self, text):
            pass

        zeile = protokoll = unter
    st.laufe = lambda *a, **k: laeufe.append(a) or (0, [])
    leer = st.tools_uebernehmen(Aus(), 5, 6)
    (st.DATEN / "modelle").mkdir(parents=True)
    (st.DATEN / "modelle" / "realesrgan-x2plus.npz").write_bytes(b"x2" * 600_000)
    voll = st.tools_uebernehmen(Aus(), 5, 6)
    kopie = p / "modelle" / "realesrgan-x2plus.npz"
    quelltext = (p / "starter.py").read_text(encoding="utf-8")
    pruefe("Starter: ohne Kopie still übersprungen, mit Kopie übernommen – nie ein Download",
           leer is False and voll is True and schritte == [(5, 6)] and kopie.is_file() and not laeufe
           and '"--laden"' not in quelltext and "tools_uebernehmen(aus, gesamt - 1, gesamt)" in quelltext, str(schritte))
    kopie.unlink()

    # 3) Über HTTP: Zustand, Warteschlange, Sperre, Deinstallieren, Zustimmung, Erstabfrage
    daten_http = tmp / "daten-tools-http"
    daten_http.mkdir()
    alt_ki = os.environ.get("MGD_KI_BILD")
    os.environ["MGD_KI_BILD"] = str(fremd)                  # der Test-Server sieht nie das echte KI-Modell
    try:
        proc, se = starte_server(p, daten_http)
    finally:
        if alt_ki is None:
            os.environ.pop("MGD_KI_BILD", None)
        else:
            os.environ["MGD_KI_BILD"] = alt_ki
    try:
        code, ti = se.json("/api/tools")
        ids = [x["id"] for x in ti.get("tools", [])]
        pruefe("HTTP: /api/tools mit Zustand, Größe, Ort, Texten in der Sprache der Seite",
               code == 200 and ids == ["bildverbesserung", "uebersetzung", "ki-bild", "sprachen", "lernen"] and ti.get("erstabfrage") is True
               and all(x["zustand"] == "nicht" and x["ort"] and x["dauer"] for x in ti["tools"]
                       if x["id"] != "ki-bild") and ti["tools"][0]["titel"].startswith("Bildverbesserung"), str(ti)[:200])
        _, wz = se.json("/api/werkzeuge")
        pruefe("Alte Werkzeuge bleiben in der API, gehören zu ihrem Tool",
               {w["id"]: w.get("tool") for w in wz if w["id"] in ("modell-x4", "modell-x2", "ki-bild")}
               == {"modell-x4": "bildverbesserung", "modell-x2": "bildverbesserung", "ki-bild": "ki-bild"})
        code1, r1 = se.json("/api/lauf", daten={"art": "generator", "nur": "pruefbogen"})
        code2, r2 = se.json("/api/tool", daten={"id": "bildverbesserung", "aktion": "installieren"})
        lauf = r2.get("lauf") or {}
        _, ti = se.json("/api/tools")
        bv = next((x for x in ti.get("tools", []) if x["id"] == "bildverbesserung"), {})
        code3, r3 = se.json("/api/tool", daten={"id": "bildverbesserung", "aktion": "deinstallieren"})
        pruefe("Installieren reiht den Download in die Warteschlange ein (Tool zeigt „wartet“, Platz 2)",
               code1 == 200 and r1.get("laeuft") and code2 == 200 and lauf.get("wartet") and lauf.get("position") == 2
               and lauf.get("tool") == "bildverbesserung" and bv.get("zustand") == "wartet" and bv.get("position") == 2
               and bv.get("lauf") == lauf.get("id"), str(r2)[:160])
        pruefe("Deinstallieren gesperrt, solange ein Auftrag des Tools wartet oder läuft (409)", code3 == 409, str(r3)[:120])
        se.json("/api/warteschlange", daten={"aktion": "entfernen", "id": lauf.get("id", "")})
        _warte_lauf(se, 120)
        _, ti = se.json("/api/tools")
        bv = next((x for x in ti.get("tools", []) if x["id"] == "bildverbesserung"), {})
        pruefe("Download aus der Schlange genommen → Tool wieder „nicht installiert“", bv.get("zustand") == "nicht")
        x2, kopie = p / "modelle" / "realesrgan-x2plus.npz", daten_http / "modelle" / "realesrgan-x2plus.npz"
        kopie.parent.mkdir(parents=True, exist_ok=True)
        x2.write_bytes(b"x2" * 600_000)
        kopie.write_bytes(b"x2" * 600_000)
        karten_vorher, bilder_vorher = (p / "karten.csv").read_bytes(), sorted(q.name for q in (p / "bilder").iterdir())
        code, r = se.json("/api/tool", daten={"id": "bildverbesserung", "aktion": "deinstallieren"})
        pruefe("HTTP: Deinstallieren löscht Modell + Kopie, Karten und Bilder bleiben, Meldung nennt den Platz",
               code == 200 and not x2.exists() and not kopie.exists() and "MB" in r.get("meldung", "")
               and (p / "karten.csv").read_bytes() == karten_vorher
               and sorted(q.name for q in (p / "bilder").iterdir()) == bilder_vorher
               and r.get("tool", {}).get("installiert") is False, str(r)[:160])
        kopie.write_bytes(b"x2" * 600_000)
        code, r = se.json("/api/tool", daten={"id": "bildverbesserung", "aktion": "installieren", "teil": "x2"})
        pruefe("HTTP: wieder installierbar (Kopie im Datenordner → sofort bereit, ohne Lauf)",
               code == 200 and "lauf" not in r and x2.is_file() and r.get("tool", {}).get("installiert") is True, str(r)[:160])
        x2.unlink()
        kopie.unlink()
        for d in [d["name"] for d in __import__("ki_bild").MODELL["dateien"][:1]]:
            (fremd / d).write_bytes(b"gans")
        code, r = se.json("/api/tool", daten={"id": "ki-bild", "aktion": "deinstallieren"})
        pruefe("HTTP: KI-Bildmodell außerhalb des Datenordners → nur abgemeldet",
               code == 200 and r.get("abgemeldet") is True and any(fremd.iterdir())
               and r.get("tool", {}).get("abgemeldet") is True, str(r)[:160])
        code, r = se.json("/api/tool", daten={"id": "uebersetzung", "aktion": "installieren"})
        code2, r2 = se.json("/api/tool", daten={"id": "uebersetzung", "aktion": "installieren", "zustimmung": True})
        _, status = se.json("/api/status")
        code3, _ = se.json("/api/tool", daten={"id": "uebersetzung", "aktion": "deinstallieren"})
        _, ue = se.json("/api/uebersetzung")
        pruefe("HTTP: Übersetzung = Zustimmung (409 ohne, mit Zustimmung installiert, Deinstallieren nimmt sie zurück)",
               code == 409 and r.get("code") == "zustimmung" and code2 == 200 and r2["tool"]["installiert"]
               and status["uebersetzung"]["zugestimmt"] and code3 == 200 and ue.get("zugestimmt") is False, str(r)[:120])
        code, r = se.json("/api/tools-erstabfrage", daten={"auswahl": ["uebersetzung", "gibt-es-nicht"]})
        _, ti = se.json("/api/tools")
        code2, _ = se.json("/api/tool", daten={"id": "gibt-es-nicht", "aktion": "installieren"})
        pruefe("HTTP: Erstabfrage merkt sich die Antwort, Zustimmungs-Tools kommen als „offen“ zurück, unbekannt → 404",
               code == 200 and r.get("offen") == ["uebersetzung"] and not r.get("laeufe") and ti.get("erstabfrage") is False
               and code2 == 404, str(r)[:160])
    finally:
        proc.terminate()
        proc.wait(10)
    ui = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    schluessel = ("tools_titel", "tools_unter", "tool_brauchen_text", "tool_weg_bleibt", "tools_erst_titel", "tools_erst_los",
                  "tool_ist_bereit", "h_tool_installieren", "h_tool_deinstallieren", "h_tool_teil")
    pruefe("Oberfläche: Tools-Bereich, Fenster, brauchtTool, Erstabfrage im Assistenten, Texte de/en/es",
           'id="tools-bereich"' in ui and 'id="tool-fenster"' in ui and "async function brauchtTool(id, weiter" in ui
           and '"tools"] : []), "tour"]' in ui and "oeffneToolErstabfrage()" in ui and "imToolBereich" in ui
           and all(ui.count(k + ":") == 3 for k in schluessel))


def test_tools_anbinden(p, tmp):
    """E23: Bildverbesserung, Übersetzung und KI-Bilder als Tools – ohne Installation 409 {code: "tool_fehlt", tool}
    (Übersetzung weiter „zustimmung“), mit Installation normal, Deinstallieren räumt auch die Zwischenergebnisse des
    Tools auf. Nur Attrappen-Dateien; der Test-Server sieht nie das echte KI-Modell."""
    print("\n[E23] Tools anbinden: Rückfrage statt Fehler, Aufräumen beim Deinstallieren")
    daten = tmp / "daten-e23"
    daten.mkdir()
    for m in (p / "modelle").glob("realesrgan-*.npz"):        # Testkopie: Bildverbesserung sicher nicht installiert
        m.unlink()
    alt_ki = os.environ.pop("MGD_KI_BILD", None)             # KI-Modellordner = daten/modelle/ki-bild (leer, eigener)
    try:
        proc, se = starte_server(p, daten)
    finally:
        if alt_ki is not None:
            os.environ["MGD_KI_BILD"] = alt_ki
    try:
        _, opt = se.json("/api/optionen")
        werte_alt = dict(opt.get("werte") or {})
        se.json("/api/einstellungen", daten={"werte": dict(werte_alt, ki="realesrgan")})
        _, vb = se.json("/api/verbesserung")
        bild = next(k["bild"] for k in vb["karten"] if k["existiert"])
        _, st = se.json("/api/status")
        pruefe("Status: Feld „tools“ (installiert je id), alte Felder bleiben",
               st.get("tools") == {"bildverbesserung": False, "uebersetzung": False, "ki-bild": False, "sprachen": False,
                                   "lernen": False}
               and "modelle" in st and "ki_bild" in st, str(st.get("tools")))
        code, r = se.json("/api/lauf", daten={"art": "verbessern", "bilder": [bild]})
        pruefe("Verbessern mit Real-ESRGAN ohne Tool → 409 tool_fehlt (bildverbesserung)",
               code == 409 and r.get("code") == "tool_fehlt" and r.get("tool") == "bildverbesserung" and r.get("fehler"),
               str(r)[:140])
        code, r = se.json("/api/lauf", daten={"art": "generator", "nur": "pruefbogen"})
        pruefe("Erzeugen mit fest gewähltem Real-ESRGAN ohne Tool → 409 tool_fehlt",
               code == 409 and r.get("tool") == "bildverbesserung", str(r)[:140])
        code, r = se.json("/api/lauf", daten={"art": "verbessern", "bilder": [bild], "ohne_tool": True})
        fertig = _warte_lauf(se, 120)
        pruefe("„Einfach vergrößern (ohne Tool)“ läuft mit dem eingebauten FSRCNN",
               code == 200 and (r.get("laeuft") or r.get("wartet")) and fertig.get("code") == 0
               and "fsrcnn" in str(fertig.get("befehl")), str(fertig)[:160])
        code, r = se.json("/api/lauf", daten={"art": "ki-bild", "beschreibung": "on a meadow"})
        _, ki = se.json("/api/ki-bild")
        pruefe("KI-Bild ohne Tool → 409 tool_fehlt (ki-bild), /api/ki-bild meldet „nicht installiert“",
               code == 409 and r.get("code") == "tool_fehlt" and r.get("tool") == "ki-bild" and ki.get("installiert") is False,
               str(r)[:140])
        code, r = se.json("/api/uebersetzen", daten={"de": "Haus"})
        pruefe("Übersetzung ohne Tool → weiter 409 „zustimmung“", code == 409 and r.get("code") == "zustimmung", str(r)[:120])
        _, ti = se.json("/api/tools")
        t = {x["id"]: x for x in ti.get("tools", [])}
        pruefe("Rückfrage kennt freien Platz (alle) und Arbeitsspeicher (KI-Bilder)",
               all(isinstance(x.get("frei"), int) and x["frei"] > 0 for x in t.values()) and "ram_gb" in t.get("ki-bild", {}))
        # Bildverbesserung „installiert“ (Attrappe) → normal; Deinstallieren räumt KI-Einträge im Zwischenspeicher auf
        x4, kopie = p / "modelle" / "realesrgan-x4plus.npz", daten / "modelle" / "realesrgan-x4plus.npz"
        kopie.parent.mkdir(parents=True, exist_ok=True)
        x4.write_bytes(b"x4" * 600_000)
        kopie.write_bytes(b"x4" * 600_000)
        code, r = se.json("/api/lauf", daten={"art": "verbessern", "bilder": [bild]})
        _warte_lauf(se, 120)
        _, st = se.json("/api/status")
        pruefe("Mit installiertem Tool läuft Verbessern normal (kein 409)",
               code == 200 and st["tools"]["bildverbesserung"] is True, str(r)[:120])
        cache, ausgabe = p / "ausgabe" / ".cache", p / "ausgabe"
        cache.mkdir(parents=True, exist_ok=True)
        for name, methode in (("e23ki", "realesrgan-x4plus"), ("e23fs", "fsrcnn")):
            (cache / f"{name}.json").write_text(json.dumps({"ki": methode, "sha1": name}), encoding="utf-8")
            (cache / f"{name}.jpg").write_bytes(jpg())
        (ausgabe / "e23-druck.pdf").write_bytes(b"%PDF-1.4 gans")
        code, r = se.json("/api/tool", daten={"id": "bildverbesserung", "aktion": "deinstallieren"})
        pruefe("Deinstallieren: Modelle + Kopie + Real-ESRGAN-Zwischenspeicher weg; FSRCNN-Einträge, PDFs bleiben",
               code == 200 and not x4.exists() and not kopie.exists() and not (cache / "e23ki.jpg").exists()
               and not (cache / "e23ki.json").exists() and (cache / "e23fs.jpg").is_file()
               and (ausgabe / "e23-druck.pdf").is_file(), str(r)[:160])
        (ausgabe / "e23-druck.pdf").unlink()
        for name in ("e23fs.json", "e23fs.jpg"):
            (cache / name).unlink()
        # KI-Bilder im eigenen Datenordner: Deinstallieren löscht Modell-Dateien + ausgabe/.ki-bild, Prompt-Fassung bleibt
        import ki_bild
        modell = daten / "modelle" / "ki-bild"
        modell.mkdir(parents=True)
        erste = ki_bild.MODELL["dateien"][0]["name"]
        (modell / erste).write_bytes(b"gans")
        kb = ausgabe / ".ki-bild"
        kb.mkdir(parents=True, exist_ok=True)
        (kb / "0123456789abcdef.png").write_bytes(b"png")
        (kb / "0123456789abcdef.json").write_text("{}", encoding="utf-8")
        se.json("/api/ki-bild-prompt", daten={"ohne_menschen": False})
        code, r = se.json("/api/tool", daten={"id": "ki-bild", "aktion": "deinstallieren"})
        _, ki = se.json("/api/ki-bild")
        pruefe("KI-Bilder deinstallieren: Modell-Dateien + ausgabe/.ki-bild weg, eigene Einstellung bleibt",
               code == 200 and not r.get("abgemeldet") and not (modell / erste).exists() and not kb.exists()
               and ki.get("ohne_menschen") is False, str(r)[:160])
        se.json("/api/ki-bild-prompt", daten={"ohne_menschen": True})
        se.json("/api/einstellungen", daten={"werte": werte_alt})
    finally:
        proc.terminate()
        proc.wait(10)
    ui = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    schluessel = ("verb_tool_titel", "verb_tool_text", "verb_tool_knopf", "verb_tool_x2", "verb_ohne_tool", "tool_ram_wenig",
                  "tool_platz_knapp", "u_tools")
    pruefe("Oberfläche: KI-Knöpfe immer im HTML, Hinweis-Kasten Bildverbesserung, Rückfragen über brauchtTool, Texte de/en/es",
           "data-ki-knopf>" in ui and "data-ki-knopf hidden" not in ui and 'data-k-aktion="ki-bild"' in ui
           and 'id="verb-tool"' in ui and "function zeichneVerbTool()" in ui and "kiToolHolen()" in ui
           and 'brauchtTool("bildverbesserung"' in ui and "uebersetzungsTool()" in ui and "toolFehlt(e)" in ui
           and all(ui.count(k + ":") == 3 for k in schluessel))


def test_farben(p, tmp):
    """E24: Farben & Darstellung – Schemata, eigene Farben (nur #RRGGBB), Speichern/Zurücksetzen, Variablen schon in der
    ausgelieferten Seite, Standard unverändert, keine festen Farben mehr im CSS außerhalb von :root."""
    print("\n[E24] Farben & Darstellung")
    daten = tmp / "daten-e24"
    daten.mkdir()
    proc, se = starte_server(p, daten)
    datei = p / "ui_einstellungen.json"
    try:
        def seite():
            return se.anfrage("/")[2].decode("utf-8")

        code, f = se.json("/api/farben")
        pruefe("Standard „Gänsehimmel“: keine überschriebenen Variablen, 6 Schemata, Eigene = heutige Farben",
               code == 200 and f["schema"] == "himmel" and f["css"] == "" and len(f["schemata"]) == 6
               and f["eigene"]["hintergrund"] == "#E8F2FA" and f["eigene"]["text"] == "#1B2D4F", str(f)[:160])
        s = seite()
        pruefe("Seite: Platzhalter ersetzt, <style id=farben-vars> leer, theme-color weiß",
               '<style id="farben-vars"></style>' in s and "__GL_" not in s.replace("__GL_TOKEN__", "")
               and '<meta name="theme-color" content="#FFFFFF">' in s)
        code, r = se.json("/api/farben", daten={"schema": "nacht", "eigene": {}})
        s = seite()
        gespeichert = json.loads(datei.read_text(encoding="utf-8")).get("farben")
        pruefe("Gänsenacht speichern: Variablen sofort in der Seite (kein Aufblitzen), in ui_einstellungen.json",
               code == 200 and "--himmel:#0F1A2E" in r["css"] and re.search(r'<style id="farben-vars">:root\{[^}]*--himmel:#0F1A2E', s)
               and "--farbschema:dark" in s and gespeichert == {"schema": "nacht", "eigene": {}}, str(gespeichert))
        pruefe("Kontrastprüfung: Gänsenacht, Wiese und Hoher Kontrast ≥ 4,5 : 1",
               all(se.json("/api/farben", daten={"schema": i, "eigene": {}, "speichern": False})[1]["kontrast"][0]["ok"]
                   for i in ("nacht", "wiese", "kontrast", "himmel")))
        code, r = se.json("/api/farben", daten={"schema": "eigen", "eigene": {"text": "#112233", "akzent": "#00aa55"}})
        pruefe("Eigene Farben: nur geänderte Töne werden überschrieben, Eingaben in Großbuchstaben",
               code == 200 and "--nacht:#112233" in r["css"] and "--schnabel:#00AA55" in r["css"]
               and "--himmel" not in r["css"] and r["eigene"]["akzent"] == "#00AA55", r["css"][:140])
        code, r = se.json("/api/farben", daten={"schema": "eigen", "eigene": dict(r["standard"])})
        pruefe("Eigene Farben unverändert = Standard (keine Variablen)", code == 200 and r["css"] == "")
        code, r = se.json("/api/farben", daten={"schema": "eigen", "eigene": {"text": "#E8F2FA"}, "speichern": False})
        pruefe("Text so hell wie der Hintergrund → Achtung „schwer lesbar“ (ok = False)",
               code == 200 and not r["kontrast"][0]["ok"] and r["kontrast"][0]["wert"] < 2)
        vorher = datei.read_text(encoding="utf-8")
        se.json("/api/farben", daten={"schema": "wiese", "eigene": {}, "speichern": False})
        pruefe("Vorschau (speichern:false) schreibt nichts", datei.read_text(encoding="utf-8") == vorher)
        schlecht = [{"schema": "gruen"}, {"schema": "eigen", "eigene": {"text": "red"}},
                    {"schema": "eigen", "eigene": {"text": "#12345"}}, {"schema": "eigen", "eigene": {"unbekannt": "#112233"}},
                    {"schema": "eigen", "eigene": {"text": "#112233;}</style><script>"}}, {"schema": "eigen", "eigene": "x"}]
        codes = [se.json("/api/farben", daten=d)[0] for d in schlecht]
        pruefe("Ungültige Werte werden abgewiesen (Schema, Farbformat, unbekannter Schlüssel, Einschleusen)",
               all(c == 400 for c in codes) and datei.read_text(encoding="utf-8") == vorher, str(codes))
        code, r = se.json("/api/farben", daten={"schema": "system", "eigene": {}})
        s = seite()
        pruefe("„Wie das System“: dunkle Werte nur unter prefers-color-scheme, zwei theme-color-Angaben",
               code == 200 and r["css"].startswith("@media (prefers-color-scheme: dark)") and s.count('<meta name="theme-color"') == 2
               and any(k["name"].endswith("_dunkel") for k in r["kontrast"]))
        code, r = se.json("/api/farben", daten={"zuruecksetzen": True})
        pruefe("Zurücksetzen: Standard, Eintrag aus ui_einstellungen.json entfernt",
               code == 200 and r["schema"] == "himmel" and r["css"] == ""
               and "farben" not in json.loads(datei.read_text(encoding="utf-8")))
        _, w = se.json("/api/werkzeuge")
        pruefe("Werkzeug „Farben & Darstellung“ öffnet das Fenster der Seite",
               any(x["id"] == "farben" and x["art"] == "dialog" for x in w))
    finally:
        proc.terminate()
        proc.wait(10)
    ui = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    css = ui[ui.index("<style>"):ui.index("</style>")]
    ohne_root = re.sub(r":root \{[^}]*\}", "", css)
    ohne_druck = ohne_root.replace(".rahmen { display: block; } main { padding: 0; } body { background: #fff; }", "")
    feste = re.findall(r"#[0-9a-fA-F]{3,8}\b|rgba?\((?!var\()", ohne_druck)
    pruefe("CSS: keine festen Farben mehr außerhalb von :root (Ausnahme: weißer Druck)", not feste, str(feste[:6]))
    schluessel = ("fa_titel", "fa_unter", "fa_himmel", "fa_nacht", "fa_wiese", "fa_kontrast", "fa_system", "fa_eigen",
                  "fa_speichern", "fa_standard", "fa_lesbar", "fa_schwer", "h_farben_kachel", "h_farben_speichern")
    pruefe("Oberfläche: Fenster, Vorschau-Funktionen, Texte de/en/es",
           'id="farben-fenster"' in ui and "async function oeffneFarben()" in ui and "function farbenVerwerfen()" in ui
           and 'id="farben-vars"' in ui and "__GL_FARBEN__" in ui and all(ui.count(k + ":") == 3 for k in schluessel))


def test_sprachen(p, tmp):
    """E25: Sprachen 1 – Katalog (15 Sprachen), Sprachpakete laden/prüfen/entfernen, Tool „sprachen“, Zielsprache,
    karten.csv mit Spalte je Sprache, Übersetzung in andere Sprachen (Wiktionary-Parser, Zeichen, Dienst-Codes)."""
    print("\n[E25] Sprachen 1: Katalog, Pakete, Daten, Übersetzung")
    import hashlib
    import sprachen as sp
    import uebersetzer as ue
    from reportlab.pdfbase.ttfonts import TTFont
    erwartet = ["es", "en", "nds", "fr", "it", "tr", "sv", "no", "pl", "ru", "ja", "zh", "ko", "hi", "ar"]
    kat = sp.SPRACHEN
    pruefe("Katalog: 15 Sprachen, es Standard, Namen de/en/es, ar rechts-nach-links, CJK zeichenweise",
           list(kat) == erwartet and sp.STANDARD == "es" and all(set(s["name"]) == {"de", "en", "es"} and all(s["name"].values())
                                                               for s in kat.values())
           and kat["ja"]["name"]["de"] == "Japanisch" and kat["ja"]["name"]["es"] == "japonés"
           and kat["ar"]["richtung"] == "rtl" and sum(s["richtung"] == "rtl" for s in kat.values()) == 1
           and {c for c, s in kat.items() if s["umbruch"] == "zeichen"} == {"ja", "zh"})
    dateien = [d for s in sp.SCHRIFTEN.values() for d in s["dateien"]]
    pruefe("Schriften: feste Revision (40 Zeichen), SHA-256, Größe, TrueType + OFL je Paket",
           set(sp.SCHRIFTEN) == {"ru", "ja", "ko", "zh", "ar"} and all(
               re.search(r"/[0-9a-f]{40}/", d["url"]) and re.fullmatch(r"[0-9a-f]{64}", d["sha256"]) and d["groesse"] > 1000
               and d["url"].startswith("https://raw.githubusercontent.com/") for d in dateien)
           and all({x["stil"] for x in s["dateien"]} >= {"regular", "bold"} and any(x["name"] == "OFL.txt" for x in s["dateien"])
                   and s["lizenz"] == "OFL-1.1" for s in sp.SCHRIFTEN.values()))
    pop = TTFont("PopE25", str(p / "schrift" / "Poppins-Regular.ttf")).face.charToGlyph
    popb = TTFont("PopE25b", str(p / "schrift" / "Poppins-Bold.ttf")).face.charToGlyph
    latein = [c for c, s in kat.items() if s["schrift"] == "latein"]
    fehlt = [z for c in latein for z in "".join(kat[c]["sonderzeichen"]) if ord(z) not in pop or ord(z) not in popb]
    deva = [ord(z) for z in "हिन्दी हंस बूढ़ा क्षत्रिय"]
    pruefe("Poppins deckt alle lateinischen Sprachen und Devanagari ab (Regular + Bold) → kein Schrift-Download",
           not fehlt and all(z in pop and z in popb for z in deva if z != 32) and not sp.dateien("fr")
           and not sp.dateien("hi") and sp.SPRACHEN["hi"]["pakete"] == ("uharfbuzz",), str(fehlt))
    pruefe("Pakete: uharfbuzz (Apache-2.0) mit fester Fassung nur für hi + ar",
           sp.PAKETE["uharfbuzz"]["version"].count(".") == 2 and "Apache-2.0" in sp.PAKETE["uharfbuzz"]["lizenz"]
           and [c for c in kat if sp.braucht_formen(c)] == ["hi", "ar"])

    # Laden / Prüfsumme / Entfernen (eigener Datenordner, Dateien aus einem Ordner statt Download)
    daten = tmp / "daten-e25"
    quelle = tmp / "quelle-e25"
    quelle.mkdir()
    alt_daten, alt_ru = os.environ.get("MGD_DATEN"), sp.SCHRIFTEN["ru"]["dateien"]
    os.environ["MGD_DATEN"] = str(daten)
    try:
        neu = []
        for d in alt_ru:
            inhalt = (d["name"] * 50).encode()
            (quelle / d["name"]).write_bytes(inhalt)
            neu.append(dict(d, groesse=len(inhalt), sha256=hashlib.sha256(inhalt).hexdigest()))
        sp.SCHRIFTEN["ru"]["dateien"] = neu
        frisch = sp.installierte() == ["es"] and not sp.installiert("ru") and sp.zielsprache({"zielsprache": "ru"}) == "es"
        meldungen = []
        sp.lade("ru", melde=meldungen.append, quelle=quelle, pip=False)
        o = daten / "sprachen" / "ru"
        pruefe("Laden: Dateien geprüft und abgelegt, paket.json, Fortschritt „NN %“, Schriften für den Druck",
               frisch and sp.installiert("ru") and (o / "paket.json").is_file() and any(m.strip().endswith("MB)") and "%" in m
                                                                                          for m in meldungen)
               and sp.schriften("ru")["bold"].name == "NotoSans-Bold.ttf" and sp.belegt("ru") > sum(d["groesse"] for d in neu)
               and sp.zielsprache({"zielsprache": "ru"}) == "ru", str(meldungen[-2:]))
        sp.lade("fr", melde=lambda t: None)
        pruefe("Lateinische Sprache: sofort aktiviert, keine Datei außer paket.json",
               sp.installiert("fr") and sorted(q.name for q in (daten / "sprachen" / "fr").iterdir()) == ["paket.json"])
        sp.lade("hi", melde=lambda t: None, pip=False)
        pruefe("Hindi ohne uharfbuzz gilt nicht als installiert (Paket fehlt)", not sp.installiert("hi"))
        sp.entferne("hi")
        (quelle / neu[0]["name"]).write_bytes(b"kaputt")
        sp.entferne("ru")
        try:
            sp.lade("ru", melde=lambda t: None, quelle=quelle, pip=False)
            code = None
        except sp.SprachFehler as f:
            code = f.code
        pruefe("Falsche Prüfsumme: nichts installiert, keine halbe Datei bleibt liegen",
               code == "pruefsumme" and not sp.installiert("ru") and not any(o.glob("*.part"))
               and not (o / neu[0]["name"]).exists() and "Prüfsumme" in sp.fehler_text(sp.SprachFehler(code, name="x"), "de"))
        (quelle / neu[0]["name"]).write_bytes((neu[0]["name"] * 50).encode())
        sp.lade("ru", melde=lambda t: None, quelle=quelle, pip=False)
        (o / "fremd.txt").write_text("bleibt")
        weg = sp.entferne("ru")
        try:
            sp.entferne("es")
            standard = None
        except sp.SprachFehler as f:
            standard = f.code
        pruefe("Entfernen: nur bekannte Dateien, fremde bleiben; Spanisch nicht entfernbar",
               (o / "fremd.txt").is_file() and not any(x.name.endswith(".ttf") for x in o.iterdir()) and len(weg) >= 1
               and standard == "standard" and sp.installiert("es"))
        (o / "fremd.txt").unlink()
        import tools as tl
        t = tl.TOOLS["sprachen"]
        auftrag = tl.installieren("sprachen", "ru")
        sofort = tl.installieren("sprachen", "it")
        pruefe("Tool „sprachen“: 14 Teile (alle außer es), lateinisch sofort, sonst Auftrag für die Warteschlange",
               sorted(t["teile"]) == sorted(erwartet[1:]) and auftrag == {"art": "sprache", "code": "ru"} and sofort is None
               and tl.installiert("sprachen") and next(x for x in tl.teile_info("sprachen") if x["id"] == "it")["installiert"]
               and tl.teil_aus_befehl("sprachen", ["py", "-u", "sprachen.py", "--laden", "ja"]) == "ja"
               and tl.gehoert("sprachen", "sprache") == "laden")
        r = tl.deinstalliere("sprachen")
        pruefe("Tool deinstallieren: alle Sprachpakete weg, wieder installierbar",
               not tl.installiert("sprachen") and not sp.weitere_installiert() and not (daten / "sprachen").exists()
               and len(r["geloescht"]) >= 2)
    finally:
        sp.SCHRIFTEN["ru"]["dateien"] = alt_ru
        if alt_daten is None:
            os.environ.pop("MGD_DATEN", None)
        else:
            os.environ["MGD_DATEN"] = alt_daten

    # Übersetzung: Wiktionary-Parser je Schriftsystem, Zeichen, Dienst-Codes
    seite = ("== Gans ({{Sprache|Deutsch}}) ==\n{{Ü-Tabelle|1|G=Vogel|Ü-Liste=\n"
             "*{{ru}}: [1] {{Üt|ru|гусь|gusʹ}} {{m}}\n*{{ja}}: [1] {{Üt|ja|鵞鳥|がちょう, gachō}}\n"
             "*{{ar}}: [1] {{Üt|ar|إوزة|iwazza}} {{f}}\n*{{nds}}: [1] {{Ü|nds|Goos}} {{f}}\n"
             "*{{nb}}: [1] {{Ü|nb|gås}}\n*{{zh}}: [1] {{Üt|zh|鹅|é}}\n*{{es}}: [1] {{Ü|es|ganso}}\n}}\n")
    ru, ja, ar = ue.wiktionary_ziel(seite, "ru"), ue.wiktionary_ziel(seite, "ja"), ue.wiktionary_ziel(seite, "ar")
    pruefe("Wiktionary: Üt mit Umschrift (ru, ja, ar, zh), Ü (nds, nb für Norwegisch), es unverändert",
           ru[0]["text"] == "гусь" and ru[0]["umschrift"] == "gusʹ" and ja[0]["text"] == "鵞鳥" and ar[0]["text"] == "إوزة"
           and ar[0]["umschrift"] == "iwazza" and ue.wiktionary_ziel(seite, "nds")[0]["text"] == "Goos"
           and ue.wiktionary_ziel(seite, "no")[0]["text"] == "gås" and ue.wiktionary_ziel(seite, "zh")[0]["umschrift"] == "é"
           and [e["text"] for e in ue.wiktionary_spanisch(seite)] == ["ganso"], str(ru)[:120])

    urls = []

    def abruf(url, daten_, kopf):
        urls.append((url, daten_))
        if "wiktionary" in url:
            if "titles=%D0%B3%D1%83%D1%81%D1%8C" in url:                   # Rückrichtung „гусь“
                return {"query": {"pages": [{"title": "гусь", "revisions": [{"slots": {"main": {"content":
                        "== гусь ({{Sprache|Russisch}}) ==\n{{Bedeutungen}}\n:[1] Gans\n\n"}}}]}]}}
            return {"query": {"pages": [{"title": "Gans", "revisions": [{"slots": {"main": {"content": seite}}}]}]}}
        if "mymemory" in url:
            return {"responseStatus": 200, "responseData": {"translatedText": "ガチョウ"}}
        return {"translations": [{"text": "鹅"}]}
    ein = {"zugestimmt": True, "dienst": "auto", "deepl": None}
    r1 = ue.uebersetze("Gans Gans", abruf=abruf, einstellungen=ein, cache=False, richtung="de-ru")
    r2 = ue.uebersetze("гусь", abruf=abruf, einstellungen=ein, cache=False, richtung="ru-de")
    r3 = ue.uebersetze("Gans sehr alt hier", abruf=abruf, einstellungen=ein, cache=False, richtung="de-ja")
    schluessel = "12345678-1234-1234-1234-123456789abc:fx"
    r4 = ue.uebersetze("Gans sehr alt hier", abruf=abruf, einstellungen=dict(ein, deepl=schluessel), cache=False,
                       richtung="de-zh")
    pruefe("uebersetze: de-ru → „гусь|gusʹ“ (Umschrift 2. Zeile), ru-de → Gans, MyMemory de|ja, DeepL ZH-HANS",
           r1["vorschlag"] == "гусь|gusʹ" and r2["vorschlag"].startswith("Gans") and r3["vorschlag"] == "ガチョウ"
           and r4["vorschlag"] == "鹅" and any("langpair=de%7Cja" in u for u, _ in urls)
           and any(b and b"ZH-HANS" in b for _, b in urls), str((r1["vorschlag"], r2["vorschlag"], r3, r4))[:200])
    ok = [("гусь", "ru"), ("ガチョウ", "ja"), ("鹅", "zh"), ("거위", "ko"), ("हंस", "hi"), ("إوزة", "ar"), ("gås", "no"),
          ("kaz", "tr"), ("ğ ı İ ş", "tr"), ("gęś", "pl"), ("lǎo é", "zh"), ("ganso", "es")]
    schlecht = [("=1+1", "ru"), ("<b>гусь</b>", "ru"), ("a{b}", "ja"), ("гусь;DROP", "ru"), ("@x", "ar"), ("老人", "es"),
                ("гусь", "fr"), ("거위", "ja"), ("إوزة", "hi")]
    pruefe("Zeichenprüfung: Schrift der Kartensprache erlaubt, fremde Schrift/Formeln/HTML weiter verworfen",
           all(ue.kandidaten(w, code=c) == [w] for w, c in ok) and not any(ue.kandidaten(w, code=c) for w, c in schlecht)
           and ue.kandidaten("гусь", deutsch=True, code="ru") == [],
           str([w for w, c in ok if ue.kandidaten(w, code=c) != [w]] + [w for w, c in schlecht if ue.kandidaten(w, code=c)]))
    fehler = []
    for d, c in (("deepl", "hi"), ("deepl", "nds"), ("mymemory", "nds")):
        try:
            ue.reihenfolge(d, "alt", schluessel, c)
        except ue.UebersetzungsFehler as f:
            fehler.append(f.code)
    try:
        ue.uebersetze("Gans", abruf=abruf, einstellungen=ein, cache=False, richtung="de-xx")
    except ue.UebersetzungsFehler as f:
        fehler.append(f.code)
    pruefe("Dienst-Codes: DeepL ohne hi/nds, MyMemory ohne nds → übersprungen bzw. Hinweis; unbekannte Sprache abgewiesen",
           ue.reihenfolge("auto", "alt", schluessel, "hi") == ["wiktionary", "mymemory"]
           and ue.reihenfolge("auto", "alt", schluessel, "nds") == ["wiktionary"]
           and ue.reihenfolge("auto", "alt", schluessel, "es") == ["wiktionary", "deepl"]
           and fehler == ["sprache_dienst"] * 3 + ["sprache_unbekannt"]
           and all(set(ue.FEHLER_TEXTE[k]) == {"de", "en", "es"} for k in ("sprache_dienst", "sprache_unbekannt")), str(fehler))

    # Über HTTP: Tool, Zielsprache, Karten mit mehreren Rückseiten, Download über die Warteschlange
    daten_http = tmp / "daten-e25-http"
    daten_http.mkdir()
    proc, se = starte_server(p, daten_http)
    try:
        _, st = se.json("/api/status")
        _, ti = se.json("/api/tools")
        spt = next((x for x in ti.get("tools", []) if x["id"] == "sprachen"), {})
        pruefe("HTTP: Zielsprache es im Status, Tool „Sprachen“ mit 14 Teilen",
               st.get("zielsprache", {}).get("code") == "es" and st["zielsprache"]["namen"]["en"] == "Spanish"
               and len(st["zielsprache"]["sprachen"]) == 15 and len(spt.get("teile", [])) == 14, str(st.get("zielsprache"))[:120])
        code, r = se.json("/api/zielsprache", daten={"zielsprache": "ja"})
        pruefe("Zielsprache nicht installiert → 409 tool_fehlt (Tool sprachen, Teil ja)",
               code == 409 and r.get("code") == "tool_fehlt" and r.get("tool") == "sprachen" and r.get("teil") == "ja", str(r))
        code, r = se.json("/api/tool", daten={"id": "sprachen", "aktion": "installieren", "teil": "fr"})
        code2, z = se.json("/api/zielsprache", daten={"zielsprache": "fr"})
        _, st = se.json("/api/status")
        pruefe("Französisch installieren (sofort) und als Zielsprache wählen → Status mit Namen und Richtung",
               code == 200 and "lauf" not in r and code2 == 200 and z["code"] == "fr" and st["zielsprache"]["code"] == "fr"
               and st["zielsprache"]["namen"]["de"] == "Französisch" and st["zielsprache"]["richtung"] == "ltr", str(z)[:120])
        _, kd = se.json("/api/karten")
        karten = kd["karten"]                             # ab G08: Feld „es“ = Rückseite in der Zielsprache (fr)
        es0 = karten[0]["rueckseiten"]["es"]
        karten[0]["es"], karten[0]["uebersetzung"] = "oie", "auto"
        karten[1]["extra"] = dict(karten[1].get("extra") or {}, eigene_spalte="bleibt")
        code, kd = se.json("/api/karten", daten={"karten": karten})
        kopf = (p / "karten.csv").read_text(encoding="utf-8-sig").splitlines()[0].split(";")
        k0, k1 = kd["karten"][0], kd["karten"][1]
        offen_fr = sum(k["offen"] for k in kd["karten"])
        pruefe("karten.csv: Spalten fr + uebersetzung_fr nur wenn benutzt, es bleibt Pflicht, fremde Spalte bleibt",
               code == 200 and kopf[:4] == ["bild", "de", "es", "notiz"] and "fr" in kopf and "uebersetzung_fr" in kopf
               and "eigene_spalte" in kopf and "en" not in kopf and k0["rueckseiten"]["es"] == es0 and k0["es"] == "oie"
               and k0["rueckseiten"]["fr"] == "oie"
               and k0["uebersetzungen"].get("fr") == "auto" and k1["extra"].get("eigene_spalte") == "bleibt", str(kopf))
        se.json("/api/zielsprache", daten={"zielsprache": "es"})
        _, kd2 = se.json("/api/karten")
        pruefe("„offen“ zählt die Zielsprache (fr: alle außer einer offen, es: wie vorher)",
               kd["zielsprache"] == "fr" and not k0["offen"] and offen_fr == sum(k["existiert"] for k in kd["karten"]) - 1
               and kd2["zielsprache"] == "es" and sum(k["offen"] for k in kd2["karten"]) < offen_fr, str(offen_fr))
        se.json("/api/lauf", daten={"art": "generator", "nur": "pruefbogen"})
        code, r = se.json("/api/tool", daten={"id": "sprachen", "aktion": "installieren", "teil": "ru"})
        lauf = r.get("lauf") or {}
        _, ws_ = se.json("/api/warteschlange")
        warten = next((w for w in ws_.get("wartend", []) if w.get("id") == lauf.get("id")), {})
        _, ti = se.json("/api/tools")
        spt = next((x for x in ti.get("tools", []) if x["id"] == "sprachen"), {})
        pruefe("Sprache mit Schrift: Download über die Warteschlange (wartet, Teil ru, gehört zum Tool)",
               code == 200 and lauf.get("wartet") and lauf.get("tool") == "sprachen" and spt.get("teil_laedt") == "ru"
               and "Russ" in str(warten.get("titel", "")) + str(lauf), str(r)[:160])
        se.json("/api/warteschlange", daten={"aktion": "entfernen", "id": lauf.get("id", "")})
        _warte_lauf(se, 120)
        se.json("/api/zielsprache", daten={"zielsprache": "fr"})
        code, r = se.json("/api/tool", daten={"id": "sprachen", "aktion": "deinstallieren", "teil": "fr"})
        _, st = se.json("/api/status")
        pruefe("Sprache entfernen: Kartentexte bleiben, Zielsprache fällt auf es zurück",
               code == 200 and st["zielsprache"]["code"] == "es" and "oie" in (p / "karten.csv").read_text(encoding="utf-8-sig"))
    finally:
        proc.terminate()
        proc.wait(10)
        try:
            einst = json.loads((p / "ui_einstellungen.json").read_text(encoding="utf-8"))
            einst.pop("zielsprache", None)
            (p / "ui_einstellungen.json").write_text(json.dumps(einst), encoding="utf-8")
        except (OSError, ValueError):
            pass


ZS_SCHLUESSEL = ["bild_unter", "beschriften_unter", "es_feld", "spalte_es", "ue_text", "banner_offen", "tabelle_fuss",
                 "idee_nach_de_titel", "idee_es_zuerst", "wk_text", "wk_tour_2", "ideen_unter", "idee_es", "idee_teil_es",
                 "unfertig_offen", "h_nav_beschriften", "h_marke_es_fehlt", "h_alle_uebersetzen"]


def test_sprachen_oberflaeche(p, tmp):
    """E26: Sprachen 2 – {zs} in Texten (Seite, Python, Leitfäden), Prüfregeln je Kartensprache, Zielsprache wechseln,
    Karte mit mehreren Rückseiten speichern/laden, „offen“ je Zielsprache, Sprache entfernen → zurück auf es."""
    print("\n[E26] Sprachen 2: Oberfläche, Kennzeichnung, mehrere Rückseiten")
    import erweiterungen as er
    import gans_lernkarten as gl
    import gans_ui
    ui = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    werte = {k: re.findall(r"\b" + k + r": (\"(?:[^\"\\]|\\.)*\"|[a-z, ()]+=> `[^`]*`)", ui) for k in ZS_SCHLUESSEL}
    falsch = [k for k, v in werte.items() if len(v) != 3 or not all("{zs}" in x for x in v)]
    pruefe("Oberfläche: 18 Kartensprache-Schlüssel mit {zs} in de/en/es", not falsch, falsch)
    reste = [k for k, v in werte.items() if any(re.search(r"Spanisch|Spanish|español", x) for x in v)]
    pruefe("Oberfläche: keine „Spanisch/Spanish/español“-Reste in Kartensprache-Schlüsseln", not reste, reste)
    pruefe("t() setzt {zs} ein, Erklärung „wie in Mexiko“ nur bei es (h_rs_feld, u_kartensprache_zs in 3 Sprachen)",
           'v.replaceAll("{zs}", zsName())' in ui and "NUR_ES[k]" in ui
           and all(len(re.findall(r"\b" + k + ":", ui)) == 3 for k in ("h_rs_feld", "u_kartensprache_zs", "zs_gewechselt", "filter_fehlt",
                                                     "weitere_sprachen", "sp_weg_text", "spalte_rs")))
    pruefe("Seite: Sprach-Chips, Auswahl der Rückseite, „Weitere Sprachen“, dir=auto + lang an Rückseitenfeldern",
           all(s in ui for s in ("function sprachChip", "data-zs-wahl", "data-zs-platz", "function weitereSprachenHTML",
                                 'dir="auto"', "data-rs=", "zeichenListe()", "function sprachListeHTML", '"fehlt:"'))
           and 'data-k="es" data-auto="${esc(auto)}" title="${esc(t("h_es_feld"))}" value="${esc(es)}" placeholder="${esc(t("es_ph"))}" autocomplete="off" ${zsAttr()}' in ui)

    alt = gl.zielsprache
    try:
        gl.zielsprache = lambda: "ja"
        gl.setze_sprache("de")
        de = gl.pm("k_es_leer", "fehler")["text"], er.tx("idee_leer"), gans_ui.tx("nicht_pruefbar")
        gl.setze_sprache("es")
        es = gl.pm("k_gleich", "warnung")["text"]
    finally:
        gl.zielsprache = alt
        gl.setze_sprache(None)
    gl.setze_sprache("en")
    en = gl.pm("k_es_leer", "fehler")["text"]
    gl.setze_sprache(None)
    pruefe("Python-Texte mit {zs}: Japanisch (de), japonés (es); bei es weiter „Spanish“",
           all("Japanisch" in x for x in de) and "japonés" in es and "Spanish" in en and "{zs}" not in "".join(de), str(de)[:160])
    cfg = gl.Konfig()
    gl.registriere_schriften()
    codes = lambda r: [m["code"] for m in r["meldungen"]]
    ja = gl.pruefe_karte("Gans alt", "年寄り", cfg, ziel="ja")
    fr = gl.pruefe_karte("Gans alt", "vieille oie ä?", cfg, ziel="fr")
    es_ = gl.pruefe_karte("Gans alt", "vieja ä?", cfg, ziel="es")
    pruefe("Prüfregeln je Kartensprache: ja ohne Schrift-Fehler, Spanisch-Regeln (ä, ¿) nur bei es",
           ja["ok"] and "k_zeichen" not in codes(ja) and "k_umlaut" not in codes(fr) and "k_frage" not in codes(fr)
           and "k_umlaut" in codes(es_) and "k_frage" in codes(es_), str((codes(ja), codes(fr), codes(es_))))
    kt = gans_ui.kartensprache_text
    pruefe("Leitfaden-Marken: {{Spanisch}}/{{Spanish}}/{{español}} → Name der Kartensprache, bei es nur ohne Klammern",
           kt("auf {{Spanisch}}", "ja") == "auf Japanisch" and kt("the {{Spanish}} word", "ar") == "the Standard Arabic word"
           and kt("en {{español}}", "fr") == "en francés" and kt("{{Español}} y", "fr") == "Francés y"
           and kt("auf {{Spanisch}} / {{español}}", "es") == "auf Spanisch / español")
    marken = {d: (HIER / d).read_text(encoding="utf-8").count("{{") for d in ("LEITFADEN.md", "LEITFADEN_en.md", "LEITFADEN_es.md")}
    pruefe("Leitfäden de/en/es markieren die Kartensprache (je ≥ 10 Stellen)", all(n >= 10 for n in marken.values()), str(marken))

    daten_http = tmp / "daten-e26-http"
    daten_http.mkdir()
    proc, se = starte_server(p, daten_http)
    try:
        se.json("/api/tool", daten={"id": "sprachen", "aktion": "installieren", "teil": "fr"})
        se.json("/api/tool", daten={"id": "sprachen", "aktion": "installieren", "teil": "it"})
        code, z = se.json("/api/zielsprache", daten={"zielsprache": "fr"})
        _, kd = se.json("/api/karten")
        k0 = next(k for k in kd["karten"] if k["existiert"] and k["de"])
        es_echt = k0["rueckseiten"]["es"]
        code2, r = se.json("/api/karte-speichern", daten={"bild": k0["bild"], "de": k0["de"], "es": "vieille oie",
                                                          "notiz": k0["notiz"], "rs": {"it": "oca", "fr": "x"},
                                                          "rs_auto": {"it": "oca"}})
        _, kd = se.json("/api/karten")
        k = next(x for x in kd["karten"] if x["bild"] == k0["bild"])
        offen_fr = sum(x["offen"] for x in kd["karten"])
        pruefe("Zielsprache fr: Feld „es“ = Rückseite fr, weitere Sprache it gespeichert (automatisch), es unverändert",
               code == 200 and z["code"] == "fr" and code2 == 200 and k["es"] == "vieille oie"
               and k["rueckseiten"].get("fr") == "vieille oie" and k["rueckseiten"].get("it") == "oca"
               and k["rueckseiten"].get("es") == es_echt and k["uebersetzungen"].get("it") == "auto" and not k["offen"],
               str(k.get("rueckseiten")))
        code, h = se.json("/api/hilfe?doc=leitfaden")
        pruefe("Hilfe: Leitfaden zeigt die Kartensprache (French) statt der Marken", code == 200
               and any(n in h.get("html", "") for n in ("French", "Französisch", "francés")) and "{{" not in h.get("html", ""))
        se.json("/api/zielsprache", daten={"zielsprache": "es"})
        _, kd2 = se.json("/api/karten")
        k2 = next(x for x in kd2["karten"] if x["bild"] == k0["bild"])
        pruefe("Zurück auf es: Feld „es“ wieder Spanisch, fr/it bleiben, „offen“ zählt wieder es",
               k2["es"] == es_echt and k2["rueckseiten"].get("fr") == "vieille oie" and k2["rueckseiten"].get("it") == "oca"
               and sum(x["offen"] for x in kd2["karten"]) < offen_fr, str(k2.get("rueckseiten")))
        liste = kd2["karten"]
        code, kd3 = se.json("/api/karten", daten={"karten": [{kk: v for kk, v in x.items() if kk not in ("rueckseiten", "uebersetzungen")}
                                                              for x in liste]})
        k3 = next(x for x in kd3["karten"] if x["bild"] == k0["bild"])
        pruefe("Liste speichern ohne rueckseiten (ältere Seite): weitere Rückseiten bleiben erhalten",
               code == 200 and k3["rueckseiten"].get("fr") == "vieille oie" and k3["rueckseiten"].get("it") == "oca")
        se.json("/api/zielsprache", daten={"zielsprache": "it"})
        code, r = se.json("/api/tool", daten={"id": "sprachen", "aktion": "deinstallieren", "teil": "it"})
        _, st = se.json("/api/status")
        pruefe("Zielsprache entfernen: Antwort zielsprache_zurueck, Status wieder es, Text „oca“ bleibt in karten.csv",
               code == 200 and r.get("zielsprache_zurueck") is True and st["zielsprache"]["code"] == "es"
               and "oca" in (p / "karten.csv").read_text(encoding="utf-8-sig"), str(r)[:120])
    finally:
        proc.terminate()
        proc.wait(10)
        try:
            einst = json.loads((p / "ui_einstellungen.json").read_text(encoding="utf-8"))
            einst.pop("zielsprache", None)
            (p / "ui_einstellungen.json").write_text(json.dumps(einst), encoding="utf-8")
        except (OSError, ValueError):
            pass


def _sprachpakete_e27():
    """Echte Sprachpakete (ru, ja, ar, hi + uharfbuzz) in einem dauerhaften Test-Zwischenspeicher (Temp-Ordner, einmal
    ~10 MB laden; danach nur Prüfsummen). Ohne Netz → None (dann entfallen die Prüfungen mit echten Schriften)."""
    import sprachen as sp
    cache = Path(tempfile.gettempdir()) / "mgd-e27-sprachen"
    alt = os.environ.get("MGD_DATEN")
    os.environ["MGD_DATEN"] = str(cache)
    try:
        for c in ("ru", "ja", "ar", "hi"):
            if not sp.installiert(c):
                sp.lade(c, melde=lambda t: None)
        return cache if all(sp.installiert(c) for c in ("ru", "ja", "ar", "hi")) else None
    except Exception as e:  # noqa: BLE001 – offline, Proxy …
        print(f"  (E27: Sprachpakete nicht ladbar – Prüfungen mit echten Schriften entfallen: {str(e)[:80]})")
        return None
    finally:
        if alt is None:
            os.environ.pop("MGD_DATEN", None)
        else:
            os.environ["MGD_DATEN"] = alt


def test_sprachen_druck(p, tmp):
    """E27: Sprachen 3 – Druck in anderen Sprachen: Schalter --sprache, Dateinamen mit _<code> (es unverändert),
    Schriften der Sprachpakete, Formen (hi, ar), rechts-nach-links, CJK-Umbruch, Sprachkürzel, Exporte je Sprache."""
    print("\n[E27] Sprachen 3: Druck, Schriften, Exporte")
    import sqlite3
    from urllib.parse import quote
    import gans_lernkarten as gl
    import lernkarten_digital as ld
    gl.registriere_schriften()
    parser = gl.baue_parser()
    a_es, a_ja = parser.parse_args([]), parser.parse_args(["--sprache", "ja", "--format", "74x52"])
    n_es, n_ja = gl.ausgabe_namen(gl.konfig_aus(a_es)), gl.ausgabe_namen(gl.konfig_aus(a_ja))
    pruefe("Schalter --sprache (Standard es, intern) + --sprachkuerzel; Dateinamen bei es unverändert, sonst _<code>",
           a_es.sprache == "es" and a_es.sprachkuerzel == "auto"
           and n_es == dict(druckerei="Me-Goos-ta-Deutsch_Druckerei_88x63.pdf", bogen="Me-Goos-ta-Deutsch_Heimdruck_A4_88x63.pdf",
                            pruefbogen="Me-Goos-ta-Deutsch_Pruefbogen.pdf", einzelbilder="einzelbilder")
           and n_ja["druckerei"] == "Me-Goos-ta-Deutsch_Druckerei_74x52_ja.pdf" and n_ja["pruefbogen"].endswith("_Pruefbogen_ja.pdf")
           and n_ja["einzelbilder"] == "einzelbilder_ja", str(n_ja))
    karte = dict(nr=0, bild="", pfad=None, de="", es="viejo / anciano", notiz="", fit="contain")
    png = lambda cfg, k=karte: gl.vorschau_png(dict(k), cfg, seite="hinten", dpi=60)[0]      # noqa: E731
    es_auto, es_aus, es_an = (png(gl.Konfig(sprachkuerzel=w)) for w in ("auto", "aus", "an"))
    en_auto, en_aus = png(gl.Konfig(sprache="en", sprachkuerzel="auto")), png(gl.Konfig(sprache="en", sprachkuerzel="aus"))
    pruefe("Spanisch unverändert (Auto = ohne Kürzel), Kürzel bei anderer Sprache an, abschaltbar",
           es_auto == es_aus and es_an != es_aus and en_auto != en_aus and en_aus == es_aus
           and gl.layout_wort("viejo", 220, 160) == gl.layout_wort("viejo", 220, 160, gl.satz("es")))
    pruefe("Modelle der Exporte: Spanisch exakt wie bisher, andere Sprache mit eigenem Notiztyp und Namen",
           ld.modell_fuer("es") == (ld.MODELLNAME, ld.FELDER, ld.AFMT, "Bild → Spanisch", "me-goosta-bild-v1")
           and ld.modell_fuer("ja")[1][2] == "Japanisch" and "{{Japanisch}}" in ld.modell_fuer("ja")[2]
           and ld.lernseite_texte("en", "ar")["richtung1"] == "Picture → Standard Arabic"
           and ld.lernseite_texte("es", "es") == ld.LERNSEITE_TEXTE["es"])

    cache = _sprachpakete_e27()
    if not cache:
        return
    alt = os.environ.get("MGD_DATEN")
    os.environ["MGD_DATEN"] = str(cache)
    try:
        import pypdfium2 as pdfium
        ja, ar, hi, ru = (gl.satz(c) for c in ("ja", "ar", "hi", "ru"))
        pruefe("Schriften aus den Sprachpaketen: ja/ar/ru eigene Schrift, hi Poppins geformt, ar rechts-nach-links",
               ja.voll and ja.fett == "GL-ja-bold" and ar.fett == "GL-ar-bold" and ru.fett == "GL-ru-bold" and ar.rtl
               and hi.hb is not None and ar.hb is not None and ja.hb is None and not ja.fehlende_zeichen("年寄りのガチョウ")
               and not ar.fehlende_zeichen("إوزة عجوز") and not ru.fehlende_zeichen("старый"))
        geformt, breite = ar.geformt("مرحبا", ar.fett, 20)
        roh = "".join(chr(c) for c in map(ord, "مرحبا"))
        deva, _ = hi.geformt("क्षत्रिय", hi.fett, 20)
        pruefe("Arabisch verbunden geformt (andere Glyphen als die Buchstaben), Devanagari-Konjunkte geformt",
               hasattr(geformt, "__shapeData__") and str(geformt) not in (roh, roh[::-1]) and breite > 0
               and str(deva) != "क्षत्रिय" and len(str(deva)) < len("क्षत्रिय"), repr(str(geformt)))
        lauf = ar.laeufe("إوزة 12 abc def عجوز")
        pruefe("Rechts-nach-links: Wortfolge umgedreht, Zahlen und lateinische Wörter bleiben links-nach-rechts",
               lauf == ["عجوز", " ", "12 abc def", " ", "إوزة"] and ar.laeufe("abc عجوز def") == ["def", " ", "عجوز", " ", "abc"],
               str(lauf))
        z, *_ = gl.layout_wort("年寄りのガチョウ、とても古い", 220, 160, ja)
        z2, *_ = gl.layout_wort("ガチョウ。", 60, 160, ja)
        pruefe("CJK: zweizeilig zwischen Zeichen, bevorzugt nach „、“, nie ein Satzzeichen am Zeilenanfang",
               z == ["年寄りのガチョウ、", "とても古い"] and all(zz[:1] not in "、。" for zz in z2), str((z, z2)))
        meldungen = [m["code"] for m in gl.pruefe_karte("Gans alt", "年寄り🦆", gl.Konfig(), ziel="ja")["meldungen"]]
        lang = [m["code"] for m in gl.pruefe_karte("Gans alt", "年寄り" * 20, gl.Konfig(), ziel="ja")["meldungen"]]
        kurz = [m["code"] for m in gl.pruefe_karte("Gans alt", "年寄り", gl.Konfig(), ziel="ja")["meldungen"]]
        pruefe("Prüfung je Sprache: Zeichen außerhalb der Schrift (ja) gemeldet, Platz mit echter Schrift (zu lang / passt)",
               "k_zeichen" in meldungen and "haupt_zu_lang" in lang and "k_passt" in kurz, str((meldungen, lang, kurz)))

        # Generator mit Kartenliste in fünf Sprachen (zwei Karten, schnelle Bildverbesserung)
        bilder = sorted((p / "bilder").glob("*.jpg"))[:2]
        csv_e27 = tmp / "karten-e27.csv"
        csv_e27.write_text("bild;de;es;en;ru;ja;ar;hi\n" + "\n".join(
            f"{b.name};Gans {i};viejo {i};old {i};старый {i};年寄り{i};عجوز {i};बूढ़ा {i}" for i, b in enumerate(bilder)),
            encoding="utf-8-sig")
        aus = tmp / "ausgabe-e27"
        umg = dict(os.environ, PYTHONIOENCODING="utf-8", MGD_DATEN=str(cache), MGD_SPRACHE="de")

        def gen(*argv):
            r = subprocess.run([sys.executable, str(p / "gans_lernkarten.py"), "--csv", str(csv_e27), "--bilder",
                                str(p / "bilder"), "--ausgabe", str(aus), "--ki", "fsrcnn", "--ohne-png", *argv],
                               capture_output=True, text=True, encoding="utf-8", errors="replace", env=umg, timeout=300)
            return r.returncode, r.stdout + r.stderr

        def seiten(pdf_pfad, nur_hinten=True):
            pdf = pdfium.PdfDocument(str(pdf_pfad))
            texte, dunkel = [], []
            for i in range(len(pdf)):
                if nur_hinten and i % 2 == 0:
                    continue
                texte.append(pdf[i].get_textpage().get_text_range())
                bild = pdf[i].render(scale=1).to_pil().convert("L")
                dunkel.append(sum(1 for v in bild.getdata() if v < 90))
            info = pdf.get_metadata_dict()
            pdf.close()
            return texte, dunkel, info

        ergebnisse = {}
        for code in ("en", "ru", "ja", "ar", "hi"):
            r, log = gen("--nur", "druckerei", "--sprache", code)
            pfad = aus / f"Me-Goos-ta-Deutsch_Druckerei_88x63_{code}.pdf"
            ergebnisse[code] = (r, log, pfad, seiten(pfad) if pfad.is_file() else ([], [], {}))
        wort = {"en": "old", "ru": "старый", "ja": "年寄り"}
        pruefe("Druckerei-PDF je Sprache (en, ru, ja, ar, hi): Datei mit _<code>, Rückseiten mit Text bzw. sichtbaren Glyphen",
               all(e[0] == 0 and e[2].is_file() for e in ergebnisse.values())
               and all(wort[c] in " ".join(ergebnisse[c][3][0]) for c in wort)
               and all(min(ergebnisse[c][3][1] or [0]) > 150 for c in ergebnisse)
               and "Japanisch" in ergebnisse["ja"][3][2].get("Subject", ""),
               str({c: (e[0], e[3][1][:1], e[1][-120:] if e[0] else "") for c, e in ergebnisse.items()}))
        r, log = gen("--nur", "pruefbogen", "--sprache", "ja")
        texte, _, _ = seiten(aus / "Me-Goos-ta-Deutsch_Pruefbogen_ja.pdf", nur_hinten=False) \
            if (aus / "Me-Goos-ta-Deutsch_Pruefbogen_ja.pdf").is_file() else ([], [], {})
        r2, log2 = gen("--nur", "druckerei", "--karten", "1")
        pruefe("Prüfbogen nennt die Sprache (JA: …, „Japanisch“), Meldung „Rückseite auf Japanisch“; es-Lauf ohne Endung",
               r == 0 and "JA:" in " ".join(texte) and "Japanisch" in " ".join(texte) and "Rückseite auf Japanisch" in log
               and r2 == 0 and (aus / "Me-Goos-ta-Deutsch_Druckerei_88x63.pdf").is_file(), log[-200:])
        (csv_e27).write_text("bild;de;es;ja\n" + "\n".join(f"{b.name};Gans;viejo;" for b in bilder), encoding="utf-8-sig")
        r, log = gen("--nur", "pruefbogen", "--sprache", "ja")
        pruefe("Leere Spalte der Sprache: Meldung nennt Spalte und Sprache, Karte setzt aus", r == 1
               and "Spalte 'ja' (Japanisch) ist leer" in log, log[-200:])
        csv_e27.write_text("bild;de;es;ja;ar\n" + "\n".join(f"{b.name};Gans {i};viejo {i};年寄り{i};عجوز {i}"
                                                           for i, b in enumerate(bilder)), encoding="utf-8-sig")
        umg["MGD_SPRACHE"] = "en"
        r, log = gen("--nur", "digital", "--digital", "alle", "--sprache", "ja")
        dig = aus / "digital"
        apkg = dig / "Me-Goos-ta-Deutsch_Anki_ja.apkg"
        modell = deck = ""
        if apkg.is_file():
            with zipfile.ZipFile(apkg) as z:
                db = tmp / "e27.anki2"
                db.write_bytes(z.read("collection.anki2"))
            con = sqlite3.connect(db)
            m, d = con.execute("SELECT models, decks FROM col").fetchone()
            felder = con.execute("SELECT flds FROM notes").fetchall()
            con.close()
            modell, deck = json.loads(m), json.loads(d)
        m1 = next(iter(modell.values())) if modell else {}
        pruefe("Anki-Paket je Sprache: eigener Notiztyp (Feld „Japanisch“), Stapel „… – Japanese“, Wörter drin",
               r == 0 and m1.get("name") == "Me Goos-ta Deutsch (Bild → Japanisch)"
               and [f["name"] for f in m1.get("flds", [])][2] == "Japanisch"
               and any(v.get("name") == "Me Goos-ta Deutsch – Japanese" for v in deck.values())
               and any("年寄り" in f[0] for f in felder), log[-200:])
        seite = (dig / "Me-Goos-ta-Deutsch_Lernseite_ja.html").read_text(encoding="utf-8") \
            if (dig / "Me-Goos-ta-Deutsch_Lernseite_ja.html").is_file() else ""
        alle = (dig / "tabellen_ja" / "karten_alle_sprachen.csv").read_text(encoding="utf-8") \
            if (dig / "tabellen_ja" / "karten_alle_sprachen.csv").is_file() else ""
        pruefe("Lernseite (lang ja, „Picture → Japanese“), Bildschirm-PDF und Tabellen mit Endung _ja, CSV mit allen Sprachspalten",
               '"rs_lang": "ja"' in seite and "Picture → Japanese" in seite
               and (dig / "Me-Goos-ta-Deutsch_Bildschirm_88x63_ja.pdf").is_file()
               and alle.splitlines()[0] == "bild;de;es;ja;ar;notiz" and "عجوز 0" in alle, alle[:80])
    finally:
        if alt is None:
            os.environ.pop("MGD_DATEN", None)
        else:
            os.environ["MGD_DATEN"] = alt

    # Oberfläche: Sprachwahl beim Erzeugen (ein Auftrag je Sprache), Vorschau in der Zielsprache
    daten_http = tmp / "daten-e27-http"
    shutil.copytree(cache / "sprachen", daten_http / "sprachen")
    proc, se = starte_server(p, daten_http)
    try:
        code, r = se.json("/api/lauf", daten={"art": "generator", "nur": "pruefbogen", "sprache": "ko"})
        pruefe("Erzeugen in nicht installierter Sprache → 409 tool_fehlt (sprachen, teil ko)",
               code == 409 and r.get("code") == "tool_fehlt" and r.get("tool") == "sprachen" and r.get("teil") == "ko", str(r)[:120])
        se.json("/api/warteschlange", daten={"aktion": "leeren"})
        code, r = se.json("/api/lauf", daten={"art": "generator", "nur": "pruefbogen", "sprache": "alle"})
        _, w = se.json("/api/warteschlange")
        befehle = json.dumps(w, ensure_ascii=False)
        pruefe("„Alle installierten“: ein Auftrag je Sprache (es, ru, ja, hi, ar) über die Warteschlange",
               code == 200 and r.get("auftraege") == 5 and sorted(r.get("sprachen", [])) == ["ar", "es", "hi", "ja", "ru"]
               and befehle.count("Japan") == 1 and befehle.count("Russ") == 1,
               str((code, r.get("auftraege"), r.get("sprachen"))) + befehle[300:700])
        se.json("/api/warteschlange", daten={"aktion": "leeren"})
        _, _, bild_es = se.anfrage("/api/rueckseite?es=" + quote("年寄り"))
        se.json("/api/zielsprache", daten={"zielsprache": "ja"})
        code, kopf, bild_ja = se.anfrage("/api/rueckseite?es=" + quote("年寄り"))
        pruefe("Rückseiten-Vorschau in der Zielsprache (ja: andere Schrift als Poppins-Tofu)",
               code == 200 and bild_ja[:4] == b"\x89PNG" and bild_ja != bild_es)
    finally:
        try:
            se.json("/api/lauf-stopp", daten={})               # gestartete Prüfbögen beenden (Ordner frei)
            for _ in range(50):
                if not se.json("/api/lauf")[1].get("laeuft"):
                    break
                time.sleep(0.1)
        except Exception:  # noqa: BLE001
            pass
        proc.terminate()
        proc.wait(10)
        try:
            einst = json.loads((p / "ui_einstellungen.json").read_text(encoding="utf-8"))
            einst.pop("zielsprache", None)
            (p / "ui_einstellungen.json").write_text(json.dumps(einst), encoding="utf-8")
        except (OSError, ValueError):
            pass


def test_lernen(p, tmp):
    """E28: Karten lernen 1 – FSRS-6 gegen Referenzwerte von py-fsrs, Lernschritte, Tageswechsel, Tageslimits, Fuzz
    (reproduzierbar), Geschwister, Rückgängig, Stapel-Filter, Export/Import, .bak-Wiederherstellung, Zurücksetzen bei
    geänderter Karte über alle Speicherwege (nicht bei der Notiz), Sperre ohne Tool, Deinstallieren löscht den Stand."""
    print("\n[E28] Karten lernen 1: FSRS-Kern, Lernstand, API")
    from urllib.parse import quote
    import gans_lernkarten as gl
    import lernen as ln
    e = ln.einstellungen_pruefen({})

    def folge(noten, verzug=None):
        k, letzte, t, aus = {}, None, 0.0, []
        for i, n in enumerate(noten):
            k, sek = ln.planen(k, n, e, None if letzte is None else int((t - letzte) // 86400))
            aus.append((sek // 86400 if sek >= 86400 else f"{sek // 60}m", round(k["s"], 4), round(k["d"], 4)))
            letzte, t = t, t + sek + (verzug[i] * 86400 if verzug else 0)
        return aus
    # Referenzwerte: py-fsrs 6.3.2 (MIT, open-spaced-repetition) mit Scheduler(enable_fuzzing=False) und den
    # Standardparametern; jede Bewertung genau zur Fälligkeit (Folge c: 5 bzw. 20 Tage zu spät). Am 15.10.2026 mit der
    # Bibliothek selbst berechnet – „10m“ = Lernschritt in Minuten, sonst Tage.
    a = folge([3, 3, 3, 3, 3, 3, 1, 1, 3, 3, 3, 3, 3])
    pruefe("FSRS-6: Intervalle wie py-fsrs (Gut ×6, Nochmal ×2, Gut ×5)",
           [x[0] for x in a] == ["10m", 2, 11, 46, 163, 498, "10m", "10m", 2, 4, 7, 12, 21], str(a))
    pruefe("FSRS-6: Stabilität und Schwierigkeit wie py-fsrs (4 Nachkommastellen)",
           a[0][1:] == (2.3065, 2.1181) and a[5][1:] == (497.8766, 2.0837) and a[6][1:] == (6.8904, 7.3832)
           and a[7][1:] == (2.1546, 9.1251) and a[12][1:] == (20.7704, 9.0558), str(a[5:8]))
    b, c = folge([4, 3, 2, 3, 1, 3, 4]), folge([1, 2, 3, 3, 3], [0, 0, 0, 5, 20])
    pruefe("FSRS-6: Einfach/Schwer und verspätete Wiederholung wie py-fsrs",
           [x[0] for x in b] == [8, 39, 108, 294, "10m", 6, 19] and b[2][1:] == (107.5218, 4.0106)
           and b[6][1:] == (18.9009, 7.3181) and [x[0] for x in c] == ["1m", "5m", "10m", 1, 3]
           and c[4][1:] == (3.0192, 7.5671), str((b, c)))
    pruefe("Abrufwahrscheinlichkeit (S = 2,3065) nach 0/1/3/10/100 Tagen wie py-fsrs",
           [round(ln.abrufwahrscheinlichkeit(2.3065, t), 4) for t in (0, 1, 3, 10, 100)]
           == [1.0, 0.9468, 0.8809, 0.7744, 0.5589])
    erste = [ln.planen({}, n, e)[1] for n in (1, 2, 3, 4)]
    wdh = ln.planen({}, 4, e)[0]
    rueck, sek = ln.planen(wdh, 1, e, 8)
    kurz = ln.einstellungen_pruefen({"lernschritte": [2]})
    pruefe("Lernschritte wie Anki: 1 min · 5,5 min · 10 min · Einfach 8 Tage; Rückfall → 10 min neu lernen, Fehler gezählt",
           erste == [60, 330, 600, 8 * 86400] and rueck["zustand"] == "neulernt" and sek == 600 and rueck["fehler"] == 1
           and ln.planen({}, 2, kurz)[1] == 180 and ln.planen({}, 3, kurz)[0]["zustand"] == "wiederholung", str(erste))

    mk = lambda tag, std, minute=0: time.mktime((2026, 3, tag, std, minute, 0, 0, 0, -1))      # noqa: E731
    pruefe("Tageswechsel 4 Uhr: 3:59 gehört zum Vortag, 4:00 ist ein neuer Lerntag (einstellbar)",
           ln.lerntag(mk(10, 3, 59)) == ln.lerntag(mk(9, 12)) and ln.lerntag(mk(10, 4)) == ln.lerntag(mk(9, 12)) + 1
           and ln.lerntag(mk(10, 3, 59), 0) == ln.lerntag(mk(10, 4), 0))
    werte = {ln._fuzz(10, i / 100, 36500) for i in range(100)}
    pruefe("Fuzz: 10 Tage → 8–12 (wie py-fsrs), unter 3 Tagen keiner, Zufall aus Karte + Tag reproduzierbar",
           werte == {8, 9, 10, 11, 12} and ln._fuzz(2, 0.99, 36500) == 2
           and ln._zufall("a.jpg|es|v", 5) == ln._zufall("a.jpg|es|v", 5) != ln._zufall("a.jpg|es|v", 6), str(werte))

    # ---------- Lernstände in eigenen Ordnern (6 Karten mit echten Bildern, es + en) ----------
    basis = tmp / "e28"
    bilder = basis / "bilder"
    bilder.mkdir(parents=True)
    karten = []
    for i in range(6):
        (bilder / f"g{i}.jpg").write_bytes(jpg((40 * i, 90, 200 - 30 * i), (64, 48)))
        karten.append(dict(bild=f"g{i}.jpg", aktiv=True, de=f"Gans {i}", notiz="Tier am Teich" if i < 3 else "",
                           rueckseiten={"es": f"ganso {i}", "en": f"goose {i}"}, pfad=bilder / f"g{i}.jpg"))
    karten.append(dict(bild="aus.jpg", aktiv=False, de="Aus", notiz="", rueckseiten={"es": "no"}, pfad=bilder / "g0.jpg"))
    karten.append(dict(bild="leer.jpg", aktiv=True, de="Leer", notiz="", rueckseiten={}, pfad=bilder / "g0.jpg"))
    T = mk(10, 12)
    st = ln.Lernstand(basis / "a")
    st.einstellungen_setzen({"neu_pro_tag": 3, "behaltensquote": 95})
    gezeigt = []
    for _ in range(3):
        n = st.naechste_karte(karten, None, T)
        gezeigt.append(n["karte"]["id"])
        st.bewerten(karten, n["karte"]["id"], 4, 3000, T)
    fertig, morgen = st.naechste_karte(karten, None, T), st.naechste_karte(karten, None, T + 86400)
    pruefe("Tageslimit neue Karten (3): Reihenfolge der Kartenliste, danach „fertig“; am nächsten Tag wieder neue",
           gezeigt == ["g0.jpg|es|v", "g1.jpg|es|v", "g2.jpg|es|v"] and fertig["fertig"] and fertig["zaehler"]["neu"] == 0
           and morgen["karte"]["id"] == "g3.jpg|es|v" and morgen["zaehler"]["neu"] == 3
           and st.laden()["einstellungen"]["behaltensquote"] == 0.95, str((gezeigt, fertig.get("zaehler"))))
    spaeter = T + 40 * 86400
    st.einstellungen_setzen({"wdh_pro_tag": 2, "neu_pro_tag": 0})
    n = st.naechste_karte(karten, None, spaeter)
    pruefe("Tageslimit Wiederholungen (2 von 3 fälligen), inaktive Karten und Karten ohne Wort zählen nicht",
           n["zaehler"] == {"neu": 0, "lernen": 0, "wiederholen": 2}
           and len(st.lernkarten(karten, st.laden())) == 6, str(n["zaehler"]))
    vorschau = n["karte"]["vorschau"]
    erg = st.bewerten(karten, n["karte"]["id"], 3, 0, spaeter)
    pruefe("Vorschau je Knopf = tatsächliches Intervall (gleicher Fuzz), Texte wie „10 Min“/„3 Tg“",
           vorschau[3] == erg["intervall"] and vorschau[1] == 600 and ln.dauer_text(600, "de") == "10 Min"
           and ln.dauer_text(3 * 86400, "en") == "3 d" and ln.dauer_text(75 * 86400, "es") == "2,5 mes"
           and ln.dauer_text(60, "de") == "< 1 Min" and ln.dauer_text(330, "en") == "6 min", str((vorschau, erg.get("intervall"))))

    st_b = ln.Lernstand(basis / "b")
    n1 = st_b.naechste_karte(karten, None, T)["karte"]["id"]
    st_b.bewerten(karten, n1, 1, 0, T)
    frueh, spaet = st_b.naechste_karte(karten, None, T + 5), st_b.naechste_karte(karten, None, T + 61)
    pruefe("Sitzung: fälliger Lernschritt kommt zuerst, vorher geht es mit neuen Karten weiter",
           frueh["karte"]["id"] != n1 and spaet["karte"]["id"] == n1 and spaet["zaehler"]["lernen"] == 1,
           str((frueh["karte"]["id"], spaet["karte"]["id"])))
    st_c = ln.Lernstand(basis / "c")
    st_c.einstellungen_setzen({"neu_pro_tag": 1})
    st_c.bewerten(karten, "g0.jpg|es|v", 3, 0, T)
    vor = st_c.naechste_karte(karten, None, T + 30)
    pruefe("Nichts mehr fällig: Lernschritt der nächsten 20 Minuten wird vorgezogen",
           not vor["fertig"] and vor["karte"]["id"] == "g0.jpg|es|v", str(vor)[:120])
    st_d = ln.Lernstand(basis / "d")
    st_d.einstellungen_setzen({"richtung": "beide"})
    st_d.bewerten(karten, "g0.jpg|es|v", 4, 0, T)
    nd = st_d.naechste_karte(karten, None, T)
    pruefe("Beide Richtungen: eigener Stand je Richtung, die Rückrichtung derselben Karte erst morgen",
           nd["karte"]["id"] == "g1.jpg|es|v" and len(st_d.lernkarten(karten, st_d.laden())) == 12
           and st_d.naechste_karte(karten, None, T + 86400)["karte"]["id"] == "g0.jpg|es|r", str(nd["karte"]["id"]))

    for note in (3, 3):
        st_b.bewerten(karten, n1, note, 0, T + 120)
    vorher = dict(st_b.laden()["karten"][n1])
    st_b.bewerten(karten, n1, 1, 0, T + 200)
    r1 = st_b.rueckgaengig()
    gleich = st_b.laden()["karten"][n1] == vorher
    for _ in range(3):
        st_b.rueckgaengig()
    try:
        st_b.rueckgaengig()
        leer = None
    except ln.LernFehler as f:
        leer = f.code
    pruefe("Rückgängig: letzte Bewertung zurück (Stand wie vorher), bis zur neuen Karte, dann „nichts mehr“",
           r1["id"] == n1 and r1["note"] == 1 and gleich and n1 not in st_b.laden()["karten"] and leer == "nichts_rueckgaengig")

    tiere = st.stapel_speichern({"name": " Tiere ", "notiz": "teich"})
    s2 = st.stapel_speichern({"name": "Eine", "bilder": ["g5.jpg"], "sprache": "en"})
    d = st.laden()
    zahl = lambda s: len(st.lernkarten(karten, d, s, spaeter))                                 # noqa: E731
    wahl = st.lernkarten(karten, d, s2)
    try:
        st.stapel_speichern({"name": "  "})
        ohne_name = None
    except ln.LernFehler as f:
        ohne_name = f.code
    pruefe("Stapel: Filter Notiz/Suche/Auswahl/nur neu/fällig/Problem, eigene Sprache, Name nötig",
           zahl(tiere) == 3 and zahl({"suche": "ganso 4"}) == 1 and zahl({"nur": "neu"}) == 3
           and zahl({"nur": "faellig"}) == 2 and zahl({"nur": "problem"}) == 0 and wahl[0]["wort"] == "goose 5"
           and len(wahl) == 1 and tiere["name"] == "Tiere" and ohne_name == "stapel_name"
           and [x["id"] for x in st.uebersicht(karten, spaeter)["stapel"]] == ["alle", tiere["id"], s2["id"]])
    st_e = ln.Lernstand(basis / "e")
    imp = st_e.importieren(json.loads(json.dumps(st.export())))
    nochmal = st_e.importieren(st.export())
    try:
        st_e.importieren({"karten": {}})
        kaputt = None
    except ln.LernFehler as f:
        kaputt = f.code
    pruefe("Export/Import: Stand, Protokoll und Stapel übernommen, zweimal = nichts doppelt, Fremdes abgewiesen",
           st_e.laden()["karten"] == st.laden()["karten"] and imp["karten"] == len(st.laden()["karten"]) and imp["stapel"] == 2
           and nochmal == {"karten": 0, "protokoll": 0, "stapel": 0} and kaputt == "import_kaputt", str(imp))
    stand_bak = json.loads((basis / "a" / "lernstand.bak.json").read_text(encoding="utf-8"))
    (basis / "a" / "lernstand.json").write_text("{kaputt", encoding="utf-8")
    st_neu = ln.Lernstand(basis / "a")
    pruefe(".bak-Wiederherstellung: kaputte Hauptdatei → vorige Fassung, kaputte Datei aufgehoben",
           st_neu.laden()["karten"] == ln.vereinheitlichen(stand_bak)["karten"] and st_neu.wiederhergestellt
           and (basis / "a" / "lernstand.kaputt.json").is_file()
           and json.loads((basis / "a" / "lernstand.json").read_text(encoding="utf-8"))["art"] == ln.ART)

    st_f = ln.Lernstand(basis / "f")
    for kid in ("g0.jpg|es|v", "g0.jpg|en|v", "g1.jpg|es|v", "g1.jpg|en|v", "g2.jpg|es|v", "g3.jpg|es|v", "g4.jpg|es|v"):
        st_f.bewerten(karten, kid, 3, 0, T)
    geaendert = [dict(k) for k in karten]
    geaendert[0] = dict(geaendert[0], rueckseiten={"es": "ganso viejo", "en": "goose 0"}, notiz="neu")
    geaendert[4] = dict(geaendert[4], notiz="nur die Notiz")
    z1 = st_f.abgleichen(geaendert, T)
    (bilder / "g1.jpg").write_bytes(jpg((1, 2, 3), (64, 48)))
    z2 = st_f.abgleichen(geaendert, T)
    ks = st_f.laden()["karten"]
    pruefe("Zurücksetzen: Wort geändert → nur diese Sprache, Bild geändert → alle Sprachen, Notiz → nichts",
           z1 == [{"bild": "g0.jpg", "de": "Gans 0", "sprachen": ["es"]}] and "g0.jpg|en|v" in ks and "g0.jpg|es|v" not in ks
           and z2 == [{"bild": "g1.jpg", "de": "Gans 1", "sprachen": ["es", "en"]}] and "g4.jpg|es|v" in ks
           and not any(k.startswith("g1.jpg") for k in ks), str((z1, z2)))
    ohne2 = [k for k in geaendert if k["bild"] != "g2.jpg"]
    st_f.abgleichen(ohne2, T)
    noch_da = "g2.jpg|es|v" in st_f.laden()["karten"]
    st_f.abgleichen(ohne2, T + 91 * 86400)
    shutil.copy2(bilder / "g0.jpg", bilder / "g3b.jpg")
    st_f.umbenennen("g3.jpg", "g3b.jpg")
    umbenannt = [dict(k, bild="g3b.jpg", pfad=bilder / "g3b.jpg") if k["bild"] == "g3.jpg" else k for k in ohne2]
    z3 = st_f.abgleichen(umbenannt, T + 91 * 86400)
    pruefe("Entfernte Karte: Stand 90 Tage aufgehoben, dann vergessen; Umbenennen + neues Bild → zurückgesetzt",
           noch_da and "g2.jpg|es|v" not in st_f.laden()["karten"] and z3 and z3[0]["bild"] == "g3b.jpg"
           and not any(k.startswith("g3") for k in st_f.laden()["karten"]), str(z3))

    # ---------- Über HTTP: Sperre ohne Tool, Ablauf, alle Speicherwege, Deinstallieren ----------
    daten_http = tmp / "daten-e28-http"
    daten_http.mkdir()
    proc, se = starte_server(p, daten_http)
    try:
        c1, r1 = se.json("/api/lernen")
        c2, r2 = se.json("/api/lernen-bewerten", daten={"id": "x|es|v", "note": 3})
        _, kd = se.json("/api/karten")
        pruefe("Ohne Tool „lernen“: 409 tool_fehlt (lesen und bewerten), Karten ohne Lernfeld",
               c1 == 409 and r1.get("code") == "tool_fehlt" and r1.get("tool") == "lernen" and c2 == 409
               and "lernen" not in kd["karten"][0], str(r1)[:120])
        code, r = se.json("/api/tool", daten={"id": "lernen", "aktion": "installieren"})
        _, u = se.json("/api/lernen")
        _, n = se.json("/api/lernen-karte")
        karte = n.get("karte") or {}
        pruefe("Installieren = aktivieren (ohne Lauf); Übersicht mit Stapel „alle“, nächste Karte mit Vorschau je Knopf",
               code == 200 and r["tool"]["installiert"] and "lauf" not in r and u["stapel"][0]["id"] == "alle"
               and u["stapel"][0]["neu"] > 0 and set(karte.get("vorschau", {})) == {"1", "2", "3", "4"}
               and karte.get("sprache") == "es" and karte.get("wort"), str(n)[:160])
        kid, bild = karte.get("id", ""), karte.get("bild", "")
        code, b = se.json("/api/lernen-bewerten", daten={"id": kid, "note": 3, "dauer_ms": 4200, "stapel": "alle"})
        _, kd = se.json("/api/karten")
        k0 = next(x for x in kd["karten"] if x["bild"] == bild)
        pruefe("Bewerten speichert sofort, liefert die nächste Karte; „Meine Karten“ zeigt den Lernstand",
               code == 200 and b.get("zustand") == "lernt" and b.get("intervall") == 600
               and (b.get("naechste") or {}).get("karte", {}).get("id") != kid and (k0.get("lernen") or {}).get("anzahl") == 1
               and (p / "lernstand.json").is_file(), str(b)[:160])
        code, r = se.json("/api/karte-speichern", daten={"bild": bild, "de": k0["de"], "es": k0["es"], "notiz": k0["notiz"] + " Teich"})
        k1 = next(x for x in r.get("karten", {}).get("karten", []) if x["bild"] == bild)
        code2, r2 = se.json("/api/karte-speichern", daten={"bild": bild, "de": k0["de"], "es": k0["es"] + "s", "notiz": k0["notiz"]})
        k2 = next(x for x in r2.get("karten", {}).get("karten", []) if x["bild"] == bild)
        pruefe("Editor: Notiz ändern behält den Lernstand, neues Wort setzt ihn zurück (Antwort + Meldung)",
               code == 200 and "lernstand_zurueckgesetzt" not in r and k1["lernen"]["anzahl"] == 1 and code2 == 200
               and [z["bild"] for z in r2.get("lernstand_zurueckgesetzt", [])] == [bild] and k0["de"] in r2.get("lernstand_meldung", "")
               and k2["lernen"]["zustand"] == "neu" and k2["lernen"]["anzahl"] == 0, str(r2)[:200])
        wege = {}
        se.json("/api/lernen-bewerten", daten={"id": kid, "note": 3})
        _, kd = se.json("/api/karten")
        liste = [dict(x, de=x["de"] + " groß") if x["bild"] == bild else x for x in kd["karten"]]
        _, r = se.json("/api/karten", daten={"karten": liste})
        wege["tabelle"] = [z["bild"] for z in r.get("lernstand_zurueckgesetzt", [])] == [bild]
        se.json("/api/lernen-bewerten", daten={"id": kid, "note": 3})
        puffer = io.BytesIO()
        Image.new("RGB", (640, 900), (30, 160, 90)).save(puffer, "PNG")
        _, ent = se.json(f"/api/entwurf?name=neu.png&karte={quote(bild)}", roh=puffer.getvalue())
        _, r = se.json("/api/entwurf-uebernehmen", {"id": ent.get("id"), "fit": "contain"})
        wege["bild"] = [z["bild"] for z in r.get("lernstand_zurueckgesetzt", [])] == [bild]
        se.json("/api/lernen-bewerten", daten={"id": kid, "note": 3})
        _, r = se.json("/api/karte-bild-zurueck", r.get("rueckgaengig") or {})
        wege["rueckgaengig"] = [z["bild"] for z in r.get("lernstand_zurueckgesetzt", [])] == [bild]
        se.json("/api/lernen-bewerten", daten={"id": kid, "note": 3})
        spalten, zeilen, _ = gl.lies_csv(p / "karten.csv")
        for z in zeilen:
            if z.get("bild", "").lstrip("#").strip() == bild:
                z["de"] = z["de"] + " außen"
        gl.schreibe_csv(p / "karten.csv", zeilen, spalten)
        _, r = se.json("/api/karten")
        wege["csv_aussen"] = [z["bild"] for z in r.get("lernstand_zurueckgesetzt", [])] == [bild]
        pruefe("Zurücksetzen über alle Speicherwege: Tabelle, Bild ändern, Rückgängig, CSV von außen", all(wege.values()), str(wege))
        se.json("/api/lernen-bewerten", daten={"id": kid, "note": 4})
        c_r, rr = se.json("/api/lernen-rueckgaengig", daten={"stapel": "alle"})
        c_e, ue = se.json("/api/lernen-einstellungen", daten={"werte": {"neu_pro_tag": 7, "richtung": "beide", "quatsch": 1}})
        c_s, us = se.json("/api/lernen-stapel", daten={"aktion": "speichern", "stapel": {"name": "Teich", "suche": "Gans"}})
        c_l, ul = se.json("/api/lernen-stapel", daten={"aktion": "loeschen", "id": us.get("gespeichert", "")})
        c_n, un = se.json("/api/lernen-bewerten", daten={"id": kid, "note": 9})
        pruefe("HTTP: Rückgängig zeigt die Karte wieder, Einstellungen/Stapel speichern, falsche Note → 400",
               c_r == 200 and rr["id"] == kid and (rr.get("naechste") or {}).get("karte", {}).get("id") == kid and c_e == 200
               and ue["einstellungen"]["neu_pro_tag"] == 7 and ue["einstellungen"]["richtung"] == "beide"
               and "quatsch" not in ue["einstellungen"] and c_s == 200 and len(us["stapel"]) == 2 and c_l == 200
               and len(ul["stapel"]) == 1 and c_n == 400 and un.get("fehler"), str((c_r, c_e, c_s, c_l, c_n)))
        se.json("/api/lernen-bewerten", daten={"id": kid, "note": 3})
        code, kopf, roh = se.anfrage("/api/lernen-export")
        export = json.loads(roh) if code == 200 else {}
        _, sicherung = se.anfrage("/api/export?inhalt=alles")[::2]
        in_zip = "lernstand.json" in zipfile.ZipFile(io.BytesIO(sicherung)).namelist()
        c_z, uz = se.json("/api/lernen-zuruecksetzen", daten={"alle": True})
        c_i, ui_ = se.json("/api/lernen-import", daten={"lernstand": export})
        pruefe("Export als Download, Komplettsicherung enthält lernstand.json, alles zurücksetzen, Import holt es zurück",
               code == 200 and "attachment" in kopf.get("content-disposition", "") and export.get("art") == ln.ART
               and in_zip and c_z == 200 and uz["zurueckgesetzt"] >= 1 and uz["statistik"]["karten"] > 0 and c_i == 200
               and ui_["importiert"]["karten"] >= 1, str((code, c_z, c_i)))
        st_text = (p / "starter.py").read_text(encoding="utf-8")
        code, r = se.json("/api/tool", daten={"id": "lernen", "aktion": "deinstallieren"})
        c_n, rn = se.json("/api/lernen")
        pruefe("Deinstallieren löscht den Lernstand (+ .bak), Karten bleiben; danach wieder gesperrt; Update übernimmt ihn",
               code == 200 and not (p / "lernstand.json").exists() and not (p / "lernstand.bak.json").exists()
               and (p / "karten.csv").is_file() and c_n == 409 and rn.get("tool") == "lernen"
               and '"lernstand.json"' in st_text and '"lernstand.bak.json"' in st_text, str(r)[:160])
    finally:
        proc.terminate()
        proc.wait(10)
        for n in ("lernstand.json", "lernstand.bak.json", "lernstand.json.tmp"):
            (p / n).unlink(missing_ok=True)


def test_lernen_oberflaeche(p, tmp):
    """E29: Karten lernen 2 – Reiter „Lernen“, Sitzung (Tasten, Rückgängig, Vorlesen nur mit Systemstimme), Stapel aus der
    Auswahl in „Meine Karten“, Lernstand je Karte, Hinweis vor dem Zurücksetzen; Texte vollständig in de/en/es; der Ablauf
    der Seite über die API (5 Bewertungen, Rückgängig, Auswahl-Stapel, Einstellungen, kaputter Import)."""
    print("\n[E29] Karten lernen 2: Oberfläche")
    ui = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    pruefe("Navigation: „🎓 Lernen“ direkt unter „Meine Karten“, Ansicht #lernen mit Zahl „heute dran“",
           re.search(r'data-ansicht="karten".*?</a>\s*<a href="#lernen" data-ansicht="lernen"', ui) is not None
           and 'const ANSICHTEN = ["karten", "lernen",' in ui and 'id="v-lernen"' in ui and 'id="zahl-lernen"' in ui
           and 'if (name === "lernen") zeichneLernen();' in ui)
    start = ui.index("Object.assign(TXT.de, {\n  nav_lernen")
    bloecke = ui[start:ui.index("// Handy & Tablet", start)].split("Object.assign(TXT.")[1:]
    schluessel = [set(re.findall(r"\b((?:h_)?(?:ln_[a-z0-9_]*|nav_lernen)):", b)) for b in bloecke]
    pruefe("Texte: gleiche Lern-Schlüssel in de/en/es (≥ 100), Hover-Texte dabei",
           len(bloecke) == 3 and schluessel[0] == schluessel[1] == schluessel[2] and len(schluessel[0]) >= 100
           and {"h_nav_lernen", "h_ln_zeigen", "h_ln_noten", "h_ln_rueck"} <= schluessel[0],
           str([sorted(schluessel[0] ^ s)[:6] for s in schluessel[1:]]))
    benutzt = set(re.findall(r'\bt\("((?:h_)?ln_[a-z0-9_]+)"\s*[,)]', ui))
    familien = {f"ln_n{i}" for i in range(1, 5)} | {"ln_z_" + z for z in ("neu", "lernt", "jung", "sicher")} \
        | {"ln_r_" + r for r in ("vorwaerts", "rueckwaerts", "beide")} | {"ln_nur_" + n for n in ("", "neu", "faellig", "problem")} \
        | {"ln_filter_" + f for f in ("alle", "faellig", "neu", "sicher", "problem")}
    fehlt = (benutzt | familien) - schluessel[0]
    texte = "".join(bloecke)
    pruefe("Jeder benutzte Lern-Text existiert, positiver Ton (kein „Warnung/Warning“), Gänse-Wortwitz in 3 Sprachen",
           not fehlt and not re.search(r"Warnung|Warning|Advertencia", texte) and texte.count("gans") + texte.count("goose") >= 4
           and "ganso" in bloecke[2], str(sorted(fehlt)))
    pruefe("Sitzung: Antwort zeigen (Leertaste/Tippen), Tasten 1–4, Strg+Z, Esc, aria-live, Fortschritt, Wischen nur Touch",
           all(s in ui for s in ('data-ln="zeigen"', "/^[1-4]$/.test(e.key)", 'e.key.toLowerCase() === "z"', 'e.key === "Escape") return lernBeenden()',
                                 'class="lern-hinten" aria-live="polite"', 'role="progressbar"', 'e.pointerType !== "touch"',
                                 "vorschau_text", 'data-ln="bearbeiten"', "ln_problem_hinweis")))
    pruefe("Vorlesen nur mit Systemstimme (offline) für die Sprache, sonst kein Knopf",
           "speechSynthesis.getVoices().find(v => v.localService !== false" in ui and "lernStimme(k.sprache) ?" in ui)
    pruefe("Übersicht: Heute-Kachel, Stapel ✎/🗑, Woche als SVG mit Farb-Variablen, Einstellungen 80–95 %, Export/Import/Zurücksetzen",
           all(s in ui for s in ("function lernWocheSVG", ".lern-woche rect { fill: var(--wasser); }", 'type="range" min="80" max="95"',
                                 'href="/api/lernen-export"', "/api/lernen-import", "/api/lernen-zuruecksetzen", 'data-ln="stapel-loeschen"',
                                 '"/api/lernen-stapel"', "ln_quote_erkl", 'wahl("tageswechsel"', 'wahl("richtung"')))
    pruefe("Meine Karten: Lernstand-Marke, Filter fällig/neu/sicher/Problem, Auswahl → Jetzt lernen / Zum Stapel",
           all(s in ui for s in ("const m = [lernMarke(k)];", 'id="karten-lernleiste"', 'data-aktion="lern-wahl"', 'data-ln-k="jetzt"',
                                 'data-ln-k="stapel"', "lernPasst(k) ? zeileHTML(k, i)")))
    pruefe("Editor/Tabelle: Hinweis vor dem Speichern, Toast mit lernstand_meldung, Export-Knopf beim Deinstallieren",
           'data-teil="lern-hinweis" hidden' in ui and "j.lernstand_meldung) { toast(j.lernstand_meldung)" in ui
           and 'zellen-meldung lern' in ui and 'x.id === "lernen" ? `<p><a class="knopf" href="/api/lernen-export"' in ui)
    pruefe("Handy: Bewertungsleiste klebt unten (Daumenzone), Tippflächen ≥ 44 px",
           re.search(r"@media screen and \(hover: none\) and \(pointer: coarse\) \{\s*\.lern-noten \{ position: sticky; bottom: 0;", ui)
           is not None and ".lern-haken { min-width: 44px; min-height: 44px; }" in ui)

    daten_http = tmp / "daten-e29-http"
    daten_http.mkdir()
    proc, se = starte_server(p, daten_http)
    try:
        seite = se.anfrage("/")[2].decode("utf-8")
        se.json("/api/tool", daten={"id": "lernen", "aktion": "installieren"})
        _, n = se.json("/api/lernen-karte?stapel=alle")
        gesehen, noten = [], [3, 1, 4, 2, 3]
        for note in noten:
            k = n["karte"]
            gesehen.append(k["id"])
            _, r = se.json("/api/lernen-bewerten", daten={"id": k["id"], "note": note, "dauer_ms": 2500, "stapel": "alle"})
            n = r["naechste"]
        _, u = se.json("/api/lernen")
        c_r, rr = se.json("/api/lernen-rueckgaengig", daten={"stapel": "alle"})
        _, u2 = se.json("/api/lernen")
        pruefe("Seite enthält den Reiter; 5 Bewertungen wie in der Sitzung (nächste Karte kommt mit), Rückgängig zeigt die letzte wieder",
               'id="v-lernen"' in seite and len(set(gesehen)) == 5 and u["statistik"]["heute"]["gelernt"] == 5
               and c_r == 200 and rr["id"] == gesehen[-1] and rr["naechste"]["karte"]["id"] == gesehen[-1]
               and u2["statistik"]["heute"]["gelernt"] == 4, str((gesehen, c_r)))
        bilder = [g.split("|")[0] for g in gesehen[:2]]
        c_s, us = se.json("/api/lernen-stapel", daten={"aktion": "speichern", "stapel": {"id": "00000000", "name": "Aktuelle Auswahl",
                                                                                          "bilder": bilder}})
        ids = set()
        for _ in range(6):                                      # Lernschritte kommen wieder: nur Karten der Auswahl
            _, m = se.json("/api/lernen-karte?stapel=00000000")
            if not m.get("karte"):
                break
            ids.add(m["karte"]["bild"])
            se.json("/api/lernen-bewerten", daten={"id": m["karte"]["id"], "note": 4})
        _, kd = se.json("/api/karten")
        mit = [k for k in kd["karten"] if k.get("lernen")]
        pruefe("„Jetzt lernen“ aus der Auswahl: Stapel 00000000 enthält nur die angekreuzten Karten; Karten tragen den Lernstand",
               c_s == 200 and us.get("gespeichert") == "00000000" and ids and ids <= set(bilder)
               and any(k["lernen"]["anzahl"] > 0 for k in mit), str((ids, bilder)))
        c_e, ue = se.json("/api/lernen-einstellungen", daten={"werte": {"behaltensquote": 85, "tageswechsel": 3, "neu_pro_tag": 5}})
        c_i, ui_ = se.json("/api/lernen-import", daten={"lernstand": None})
        pruefe("Einstellungen aus dem Formular (85 % → 0,85), kaputte Import-Datei → 400 mit freundlichem Text",
               c_e == 200 and ue["einstellungen"]["behaltensquote"] == 0.85 and ue["einstellungen"]["tageswechsel"] == 3
               and c_i == 400 and "lernstand.json" in ui_.get("fehler", ""), str((c_e, c_i, ui_)))
    finally:
        proc.terminate()
        proc.wait(10)
        for n in ("lernstand.json", "lernstand.bak.json", "lernstand.json.tmp"):
            (p / n).unlink(missing_ok=True)


E30_PROZESS = r'''
import io, json, os, re, sys, time, urllib.error, urllib.request
from pathlib import Path
sys.path.insert(0, sys.argv[1])
os.environ.pop("MGD_IM_PROZESS", None)
import gans_ui as ui, gans_lernkarten as gl, uebersetzer
from PIL import Image, ImageChops, ImageStat
p, port = Path(sys.argv[1]), int(sys.argv[2])
ui.starte(port, browser=False)
gl.setze_sprache("de")
e = {}
oeffner = urllib.request.build_opener(urllib.request.ProxyHandler({}))
def http(methode, weg, koerper=None, cookie=True, token=True):
    kopf = {"X-GL-Sprache": "de"}
    if cookie:
        kopf["Cookie"] = f"mgd_{ui.PORT}={ui.TOKEN}"
    if token:
        kopf["X-GL-Token"] = ui.TOKEN
    if koerper is not None:
        kopf["Content-Type"] = "application/json"
    a = urllib.request.Request(f"http://127.0.0.1:{ui.PORT}{weg}", data=koerper, method=methode, headers=kopf)
    try:
        with oeffner.open(a, timeout=120) as r:
            return r.status, r.headers.get("Content-Type"), r.read()
    except urllib.error.HTTPError as f:
        return f.code, f.headers.get("Content-Type"), f.read()
def direkt(methode, weg, koerper=b"", kopf=None):
    pfad, _, abfrage = weg.partition("?")
    s, k, i = ui.verarbeite(methode, pfad, abfrage, koerper, dict({"X-GL-Sprache": "de"}, **(kopf or {})))
    return s, k.get("Content-Type"), i
def ohne_frei(x):                       # freier Speicherplatz („frei“) ändert sich zwischen zwei Abfragen (CI-Rechner)
    if isinstance(x, dict):
        return {k: ohne_frei(v) for k, v in x.items() if k != "frei"}
    return [ohne_frei(v) for v in x] if isinstance(x, list) else x
def inhalt(a):
    try:
        return a[0], a[1], ohne_frei(json.loads(a[2]))
    except ValueError:
        return a
ui.setze_zielsprache("es")
bild = ui.karten_daten()["karten"][0]["bild"]                          # eine echte Karte (frühere Tests legen Dateien ab)
wege =[("GET", w, None) for w in ("/api/status", "/api/optionen", "/api/karten", "/api/werkzeuge", "/api/tools",
                                   "/api/zielsprache", "/api/farben", "/api/uebersetzung", "/api/warteschlange",
                                   "/api/hilfe?doc=leitfaden", "/api/ideen", "/api/lernen", "/api/gans-bild",
                                   f"/api/vorschau?bild={bild}&es=hola&seite=hinten", f"/bild/{bild}", "/symbol.svg",
                                   "/api/gibt-es-nicht")]
wege += [("POST", "/api/karte-pruefen", json.dumps({"bild": bild, "de": "Gans alt", "es": "viejo"}).encode()),
         ("POST", "/api/uebersetzen", json.dumps({"de": "Gans alt"}).encode()),
         ("POST", "/api/werkzeug", json.dumps({"id": "gibt-es-nicht"}).encode())]
ungleich = []
for m, w, k in wege:
    a, b = inhalt(http(m, w, k)), inhalt(direkt(m, w, k if k is not None else b""))
    if a != b:
        ungleich.append([w, str(a)[:120], str(b)[:120]])
e["gleich"] = [len(wege), ungleich]
e["huelle"] = [http("GET", "/api/karten", cookie=False)[0], http("POST", "/api/karte-pruefen", b"{}", token=False)[0],
               http("GET", "/symbol.svg", cookie=False)[0]]
puffer = io.BytesIO()
Image.new("RGB", (640, 480), (200, 120, 40)).save(puffer, "JPEG")
s, _, r = direkt("POST", "/api/entwurf?name=gans-web.jpg", puffer.getvalue())
r = json.loads(r)
e["roh"] = s == 200 and bool(r.get("id"))
if r.get("id"):
    direkt("POST", "/api/entwurf-weg", json.dumps({"id": r["id"]}).encode())

def warte(lid, sekunden=180):
    ende = time.time() + sekunden
    while time.time() < ende:
        l = ui.warteschlange.finde(lid)
        if l and l.code is not None:
            return l
        time.sleep(0.2)
    return ui.warteschlange.finde(lid)
def normal(zeilen):
    return [re.sub(r"\d+[.,]\d+ s", "# s", z) for z in zeilen]
ausgabe = ui.pfade()[2]
warte(ui.starte_lauf("generator", "pruefbogen")["id"])                  # Zwischenspeicher füllen (gleiche Ausgangslage)
l1 = warte(ui.starte_lauf("generator", "pruefbogen")["id"])
pdf = sorted(ausgabe.glob("*_Pruefbogen*.pdf"))
g1 = pdf[0].stat().st_size if pdf else 0
os.environ["MGD_IM_PROZESS"] = "1"
st = ui.starte_lauf("generator", "pruefbogen")
l2 = warte(st["id"])
g2 = pdf[0].stat().st_size if pdf else 0
e["im_prozess"] = [l1.code, l2.code, l2.proc is None, normal(l1.zeilen) == normal(l2.zeilen), g1, g2,
                   (normal(l1.zeilen)[-3:], normal(l2.zeilen)[-3:]) if normal(l1.zeilen) != normal(l2.zeilen) else None]
a = ui.starte_lauf("generator", "alles")
b = ui.starte_lauf("generator", "pruefbogen")
for _ in range(100):
    if ui.warteschlange.aktiv and ui.warteschlange.aktiv.zeilen:
        break
    time.sleep(0.05)
gestoppt = ui.warteschlange.stoppen()
la, lb = warte(a["id"]), warte(b["id"])
e["abbruch"] = [gestoppt, la.abgebrochen, la.code, lb.code, b.get("wartet")]
os.environ.pop("MGD_IM_PROZESS")

wahl = next(w["id"] for w in ui.WERKZEUGE if w.get("nur_rechner"))
s_vorn = direkt("GET", f"/api/vorschau?bild={bild}&es=hola&seite=hinten")
alt_plattform = sys.platform
sys.platform = "emscripten"
try:
    j = lambda x: json.dumps(x).encode()
    e["browser"] = [ui.im_browser(), ui.im_prozess(), direkt("POST", "/api/oeffnen", j({"ziel": "ausgabe"}))[0],
                    direkt("POST", "/api/beenden", j({}))[0], direkt("POST", "/api/deinstallieren", j({}))[0],
                    direkt("POST", "/api/werkzeug", j({"id": wahl}))[0]]
    kb = json.loads(direkt("GET", "/api/tools")[2])
    kb = next(t for t in kb["tools"] if t["id"] == "ki-bild")
    status = json.loads(direkt("GET", "/api/status")[2])
    e["ki_bild"] = [direkt("POST", "/api/lauf", j({"art": "ki-bild", "beschreibung": "Gans"}))[0],
                    direkt("POST", "/api/lauf", j({"art": "test"}))[0],
                    direkt("POST", "/api/tool", j({"id": "ki-bild", "aktion": "installieren"}))[0],
                    kb.get("nur_rechner"), kb.get("installiert"), status.get("web_app"), status.get("ki_bild")]
    urls = []
    def abruf(url, daten, kopf):
        urls.append(url)
        return {"query": {"pages": []}}
    try:
        uebersetzer.reihenfolge("deepl", "Gans", "abc:fx", "es")
        deepl = None
    except uebersetzer.UebersetzungsFehler as f:
        deepl = f.code
    uebersetzer.uebersetze("Gans alt", "wiktionary", abruf=abruf, einstellungen={"zugestimmt": True}, cache=False)
    oe = uebersetzer.oeffentliche_einstellungen("de")
    e["uebersetzung"] = [uebersetzer.reihenfolge("auto", "Gans", "abc:fx", "es"), deepl,
                         bool(urls) and "origin=%2A" in urls[0],
                         [d["id"] for d in oe["dienste"] if d.get("nur_rechner")]]
    s, _, r = direkt("POST", "/api/lauf", j({"art": "generator", "nur": "pruefbogen"}))
    r = json.loads(r)
    meldungen = []
    ui.WEB_MELDER = meldungen.append                       # wie der Worker: Fortschritt als JSON-Text
    n = ui.web_weiter()
    ui.WEB_MELDER = None
    l = ui.warteschlange.finde(r.get("id"))
    e["sofort"] = [s, r.get("code"), r.get("laeuft"), n, l.code if l else None, not ui.warteschlange.aktiv,
                   len(meldungen) >= 2 and json.loads(meldungen[-1]).get("code") == 0]
    sys.modules["pypdfium2"] = None
    ui._vorschau_cache.clear()
    s_pil = direkt("GET", f"/api/vorschau?bild={bild}&es=hola&seite=hinten")
    status = json.loads(direkt("GET", "/api/status")[2])
    try:
        a1 = Image.open(io.BytesIO(s_vorn[2])).convert("RGB")
        a2 = Image.open(io.BytesIO(s_pil[2])).convert("RGB")
        diff = max(ImageStat.Stat(ImageChops.difference(a1, a2)).mean) if a1.size == a2.size else 999
        e["pillow"] = [s_pil[0], s_pil[1], a1.size == a2.size, round(diff, 2), status.get("vorschau_art"), status.get("vorschau")]
    except Exception as f:
        e["pillow"] = [s_vorn[0], s_pil[0], str(s_vorn[2][:200]), str(s_pil[2][:200]), str(f), None]
finally:
    sys.platform = alt_plattform
print("#e30 " + json.dumps(e, ensure_ascii=False))
'''


def test_web_logik(p, tmp):
    """E30: Handy 1 – Logik ohne HTTP-Server (verarbeite), Läufe im selben Prozess, Plattform-Weichen der Web-App
    (nachgebildetes sys.platform = "emscripten"), Rückseiten-Vorschau ohne pypdfium2 mit der Pillow-Leinwand."""
    print("\n[E30] Handy 1: Logik-Trennung, Läufe im Prozess, Web-App-Weichen")
    shutil.copy2(HIER / "leinwand.py", p / "leinwand.py")
    daten = tmp / "daten-e30"
    daten.mkdir()
    env = dict(os.environ, PYTHONIOENCODING="utf-8", MGD_DATEN=str(daten))
    env.pop("MGD_IM_PROZESS", None)
    r = subprocess.run([sys.executable, "-c", E30_PROZESS, str(p), str(tg._freier_port())], cwd=p, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    m = re.search(r"^#e30 (.*)$", r.stdout, re.M)
    e = json.loads(m.group(1)) if m else {}
    if not m:
        print((r.stdout + r.stderr)[-2000:])
    gleich = e.get("gleich") or [0, ["?"]]
    pruefe(f"verarbeite() ohne Socket: {gleich[0]} Wege (GET, POST, Dateien, Fehler) antworten gleich wie über HTTP",
           gleich[0] >= 18 and not gleich[1], str(gleich[1])[:400])
    pruefe("Handler bleibt die Hülle: ohne Cookie 403, POST ohne Token 403, Symbol ohne Sitzung 200",
           e.get("huelle") == [403, 403, 200], str(e.get("huelle")))
    pruefe("Rohe Bytes ohne Content-Length (Web-App) → Entwurf angelegt", e.get("roh") is True)
    ip = e.get("im_prozess") or [None] * 7
    pruefe("Lauf im selben Prozess (Prüfbogen): Code 0, kein Unterprozess, gleiches Protokoll, PDF gleich groß (±1 %)",
           ip[0] == 0 and ip[1] == 0 and ip[2] is True and ip[3] is True and ip[4] > 0 and abs(ip[4] - ip[5]) <= ip[4] * 0.01,
           str(ip))
    ab = e.get("abbruch") or []
    pruefe("Abbruch im selben Prozess über den Merker; der nächste Auftrag startet danach automatisch",
           ab[:4] == [True, True, 1, 0] and ab[4] is True, str(ab))
    pruefe("Web-App: Ordner öffnen, Beenden, Deinstallieren und Rechner-Werkzeuge gesperrt (403)",
           e.get("browser") == [True, True, 403, 403, 403, 403], str(e.get("browser")))
    pruefe("Web-App: KI-Bilder und Selbsttest nur am Rechner (Lauf/Installieren 403, Tool-Karte „nur_rechner“)",
           e.get("ki_bild") == [403, 403, 403, True, False, True, False], str(e.get("ki_bild")))
    pruefe("Web-App: Übersetzung nur mit CORS-Diensten (Wiktionary mit origin=*, MyMemory; DeepL aus)",
           e.get("uebersetzung") == [["wiktionary", "mymemory"], "dienst_rechner", True, ["deepl"]], str(e.get("uebersetzung")))
    pruefe("Web-App: Auftrag startet nach der Antwort (web_weiter, ohne Thread), läuft bis zum Ende, Fortschritt über WEB_MELDER",
           e.get("sofort") == [200, None, True, 1, 0, True, True], str(e.get("sofort")))
    pil = e.get("pillow") or [None] * 6
    pruefe("Ohne pypdfium2: Rückseiten-Vorschau mit derselben Zeichenroutine auf Pillow (gleiche Größe, Abweichung < 4)",
           pil[0] == 200 and pil[1] == "image/png" and pil[2] is True and pil[3] < 4 and pil[4] == "pillow" and pil[5] is True,
           str(pil))
    ui = (HIER / "gans_ui.py").read_text(encoding="utf-8")
    huelle = ui[ui.index("class Handler(BaseHTTPRequestHandler):"):ui.index("do_PUT = do_DELETE = do_PATCH = do_OPTIONS")]
    pruefe("Neue Adressen nur in verarbeite(): der Handler kennt keine /api/-Wege mehr",
           "/api/" not in huelle and huelle.count("self._antwort(verarbeite(") == 2)


E31_PROZESS = r"""
import io, json, os, sys, types, zipfile
from pathlib import Path
sys.path.insert(0, sys.argv[1])
os.environ.pop("MGD_IM_PROZESS", None)
import gans_ui as ui, gans_lernkarten as gl, ki_modelle, sprachen
p, web = Path(sys.argv[1]), Path(sys.argv[2])
gl.setze_sprache("de")
e = {}
def direkt(methode, weg, koerper=b"", kopf=None):
    pfad, _, abfrage = weg.partition("?")
    return ui.verarbeite(methode, pfad, abfrage, koerper, dict({"X-GL-Sprache": "de"}, **(kopf or {})))
j = lambda x: json.dumps(x).encode()
# Adresse der Handy-App: genau eine Stelle (web_adresse.txt), nur https
wa = p / "web_adresse.txt"
werte = [ui.web_adresse()]
wa.write_text("https://gans.github.io/me-goos-ta-deutsch/" + chr(10), encoding="utf-8")
werte += [ui.web_adresse(), json.loads(direkt("GET", "/api/status")[2]).get("web_adresse")]
wa.write_text("javascript:alert(1)", encoding="utf-8")
werte.append(ui.web_adresse())
wa.unlink()
e["adresse"] = werte
# am Rechner: keine App-Sicherung, Seite ohne App-Modus, aber mit der App-Navigation für Touch bis 860 px
seite = ui.seite_html("n")
e["rechner"] = [direkt("GET", "/api/app-sicherung")[0], direkt("POST", "/api/app-sicherung", b"{}")[0],
                'const AM_APP = "0" === "1"' in seite, 'id="app-navi"' in seite and "(max-width: 860px) and (hover: none)" in seite]
# Schnittstelle des Workers: Bytes bzw. Uint8Array (to_bytes) hinein, (Status, Kopf-JSON, Bytes) heraus
class U8:
    def __init__(self, b):
        self.b = b
    def to_bytes(self):
        return self.b
s1, k1, i1 = ui.web_anfrage("GET", "/api/karten", "", None, "{}")
s2, k2, i2 = ui.web_anfrage("POST", "/api/karte-pruefen", "", U8(j({"bild": "x.jpg", "de": "Gans alt", "es": "viejo"})), "{}")
e["anfrage"] = [s1, json.loads(k1)["Content-Type"].startswith("application/json"), isinstance(i1, bytes),
                len(json.loads(i1)["karten"]) > 0, s2, isinstance(json.loads(i2), dict)]
# Komplettsicherung vom Rechner nimmt den Lernstand mit (Tool „lernen“ aktiv, je Karte gilt der neuere Stand)
direkt("POST", "/api/tool", j({"id": "lernen", "aktion": "installieren"}))
k = json.loads(direkt("GET", "/api/lernen-karte")[2])["karte"]
direkt("POST", "/api/lernen-bewerten", j({"id": k["id"], "note": 3}))
_, _, sicherung = direkt("GET", "/api/export?inhalt=alles&umfang=alle")
direkt("POST", "/api/lernen-zuruecksetzen", j({"alle": True}))
leer = json.loads(direkt("GET", "/api/lernen")[2])
imp = json.loads(direkt("POST", "/api/import", sicherung, {"Content-Type": "application/octet-stream"})[2])
r = json.loads(direkt("POST", "/api/import-uebernehmen", j({"id": imp.get("id"), "ersetzen": False}))[2])
voll = json.loads(direkt("GET", "/api/lernen")[2])
e["lernstand"] = [r.get("zahlen", {}).get("lernstand", 0) >= 1, json.dumps(leer) != json.dumps(voll)]
alt = sys.platform
sys.platform = "emscripten"
try:
    # App-Sicherung: ganzer Stand als ZIP, Einspielen stellt ihn wieder her
    karten_vorher = len(ui.karten_daten()["karten"])
    st, kopf, zip_roh = direkt("GET", "/api/app-sicherung")
    namen = zipfile.ZipFile(io.BytesIO(zip_roh)).namelist()
    csv = p / "karten.csv"
    vorher = csv.read_bytes()
    csv.write_bytes(b"bild;de;es;notiz" + bytes([10]))
    s, _, r = direkt("POST", "/api/app-sicherung", zip_roh)
    r = json.loads(r)
    e["sicherung"] = [st, "attachment" in kopf.get("Content-Disposition", ""), ui.SICHERUNG_MARKE in namen,
                      "projekt/karten.csv" in namen, "projekt/lernstand.json" in namen,
                      any(n.startswith("projekt/bilder/") for n in namen),
                      not any(n.endswith(".py") or "ausgabe" in n or "/modelle/" in n for n in namen),
                      s, r.get("karten") == karten_vorher, csv.read_bytes() == vorher]
    boese = io.BytesIO()
    with zipfile.ZipFile(boese, "w") as z:
        z.writestr(ui.SICHERUNG_MARKE, "{}")
        z.writestr("projekt/karten.csv", "bild;de;es;notiz")
        z.writestr("projekt/../../boese.txt", "x")
    fremd = direkt("POST", "/api/app-sicherung", sicherung)
    e["abgelehnt"] = [fremd[0], "Handy-App" in json.loads(fremd[2]).get("fehler", ""), direkt("POST", "/api/app-sicherung", b"kein zip")[0],
                      direkt("POST", "/api/app-sicherung", boese.getvalue())[0], csv.read_bytes() == vorher,
                      not (p.parent / "boese.txt").exists() and not (p / "boese.txt").exists()]
    w = {x["id"]: x for x in json.loads(direkt("GET", "/api/werkzeuge")[2])}
    bv = next(x for x in json.loads(direkt("GET", "/api/tools")[2])["tools"] if x["id"] == "bildverbesserung")
    se = json.loads(direkt("GET", "/api/start-einstellung")[2])
    e["weichen"] = [w["test"]["nur_rechner"], w["zip"]["nur_rechner"], direkt("POST", "/api/werkzeug", j({"id": "zip"}))[0],
                    "langsamer" in bv["nutzen"], se.get("vom_starter"), se.get("gewaehlt"), sprachen.noetige_pakete("ar")]
finally:
    sys.platform = alt
e["weichen"].append(sprachen.noetige_pakete("ar"))
# Real-ESRGAN in der App: aus dem eigenen Ordner modelle/ (GitHub erlaubt keinen Download aus dem Browser), Prüfsumme
class XHR:
    @classmethod
    def new(cls):
        return cls()
    def open(self, methode, url, sync):
        self.url = url
    def send(self):
        q = web / self.url
        self.status = 200 if q.is_file() else 404
        self.response = types.SimpleNamespace(to_bytes=lambda: q.read_bytes())
sys.modules["js"] = types.SimpleNamespace(XMLHttpRequest=XHR)
ziel = p.parent / "e31-modelle"
sys.platform = "emscripten"
try:
    geladen = ki_modelle.lade("realesrgan-x4plus", ziel_ordner=ziel, melde=lambda t: None).name
    gleich = (ziel / "realesrgan-x4plus.npz").read_bytes() == (web / "modelle" / "realesrgan-x4plus.npz").read_bytes()
    try:
        ki_modelle.lade("realesrgan-x2plus", ziel_ordner=ziel, melde=lambda t: None)
        x2 = "geladen"
    except ValueError as f:
        x2 = "computer" in str(f) or "Rechner" in str(f)
    (web / "modelle" / "realesrgan-x4plus.npz").write_bytes(b"veraendert")
    (ziel / "realesrgan-x4plus.npz").unlink()
    try:
        ki_modelle.lade("realesrgan-x4plus", ziel_ordner=ziel, melde=lambda t: None)
        falsch = "geladen"
    except ValueError:
        falsch = not (ziel / "realesrgan-x4plus.npz").exists()
finally:
    sys.platform = alt
e["modell"] = [geladen, gleich, x2, falsch]
print("#e31 " + json.dumps(e, ensure_ascii=False))
"""


def test_web_app(p, tmp):
    """E31: Handy 2 – die Web-App (PWA): Bau mit bau_webapp.py (Positivliste, keine Nutzerdaten, Manifest, Symbole,
    vollständige Liste im Service Worker, AM_APP-Weichen), App-Sicherung, Worker-Schnittstelle, Modelle aus dem
    eigenen Ordner, Lernstand beim Import. Ohne bau_webapp.py (liegt nur im Arbeitsordner) entfallen die Bau-Prüfungen."""
    print("\n[E31] Handy 2: Web-App (PWA)")
    import hashlib
    from PIL import Image
    web = tmp / "e31-web"
    (web / "modelle").mkdir(parents=True)
    npz = b"NPZ-Probe" * 1000
    (web / "modelle" / "realesrgan-x4plus.npz").write_bytes(npz)
    (web / "modelle" / "modelle.json").write_text(json.dumps({"realesrgan-x4plus.npz": dict(
        groesse=len(npz), sha256=hashlib.sha256(npz).hexdigest())}), encoding="utf-8")
    daten = tmp / "daten-e31"
    daten.mkdir()
    env = dict(os.environ, PYTHONIOENCODING="utf-8", MGD_DATEN=str(daten))
    env.pop("MGD_IM_PROZESS", None)
    r = subprocess.run([sys.executable, "-c", E31_PROZESS, str(p), str(web)], cwd=p, env=env, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=600)
    m = re.search(r"^#e31 (.*)$", r.stdout, re.M)
    e = json.loads(m.group(1)) if m else {}
    if not m:
        print((r.stdout + r.stderr)[-2000:])
    pruefe("App-Adresse nur aus web_adresse.txt (leer = noch nicht veröffentlicht, nur https), auch in /api/status",
           e.get("adresse") == ["", "https://gans.github.io/me-goos-ta-deutsch/", "https://gans.github.io/me-goos-ta-deutsch/", ""],
           str(e.get("adresse")))
    pruefe("Am Rechner: keine App-Sicherung (404), Seite mit AM_APP aus, App-Navigation nur für Touch bis 860 px",
           e.get("rechner") == [404, 404, True, True], str(e.get("rechner")))
    pruefe("Worker-Schnittstelle web_anfrage: Bytes bzw. Uint8Array hinein, Status + Kopf-JSON + Bytes heraus",
           e.get("anfrage") == [200, True, True, True, 200, True], str(e.get("anfrage")))
    pruefe("Komplettsicherung vom Rechner importiert: Lernstand kommt mit (je Karte der neuere Stand)",
           e.get("lernstand") == [True, True], str(e.get("lernstand")))
    pruefe("App-Sicherung: ganzer Stand als ZIP (Karten, Bilder, Lernstand; kein Programm, keine Ausgaben/Modelle), Einspielen stellt ihn her",
           e.get("sicherung") == [200, True, True, True, True, True, True, 200, True, True], str(e.get("sicherung")))
    pruefe("Sicherung einspielen lehnt fremde ZIP (mit Hinweis), Kaputtes und Pfad-Ausbruch ab – nichts verändert",
           e.get("abgelehnt") == [400, True, 400, 400, True, True], str(e.get("abgelehnt")))
    pruefe("Web-App-Weichen: Selbsttest/Projekt-ZIP nur am Rechner, Real-ESRGAN mit „langsam“-Hinweis, kein Startprogramm, hi/ar ohne uharfbuzz",
           e.get("weichen") == [True, True, 403, True, False, True, [], ["uharfbuzz"]], str(e.get("weichen")))
    pruefe("Real-ESRGAN in der App aus dem eigenen Ordner (Größe + SHA-256), fehlendes Modell = „nur am Rechner“, Fälschung abgelehnt",
           e.get("modell") == ["realesrgan-x4plus.npz", True, True, True], str(e.get("modell")))
    bau = HIER.parent.parent / "werkstatt" / "bau_webapp.py"
    if not bau.is_file():
        print("  (werkstatt/bau_webapp.py liegt nur im Quellbaum – Bau-Prüfungen entfallen)")
        return
    ziel = tmp / "e31-bau"
    erst = subprocess.run([sys.executable, str(bau), str(HIER.parent), str(ziel), "--ohne-pyodide"], env=env,
                          capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    out = ziel / "web-app"
    pruefe("bau_webapp.py baut den Ordner web-app/", erst.returncode == 0 and (out / "sw.js").is_file(), (erst.stdout + erst.stderr)[-600:])
    if erst.returncode:
        return
    sw = (out / "sw.js").read_text(encoding="utf-8")
    liste = json.loads(re.search(r"^const DATEIEN = (\[.*?\]);", sw, re.M).group(1))
    gelistet = {x[0]: x for x in liste}
    da = sorted(q.relative_to(out).as_posix() for q in out.rglob("*") if q.is_file())
    offline = [n for n in da if n not in ("sw.js", ".nojekyll") and not n.endswith(".npz") and not n.startswith("download/")]
    stimmt = all(gelistet.get(n) == [n, (out / n).stat().st_size, hashlib.sha256((out / n).read_bytes()).hexdigest()[:16]] for n in offline)
    pruefe("Service Worker kennt jede Datei der App (Größe + SHA-256), große Modelle nur auf Wunsch (nicht offline)",
           stimmt and sorted(gelistet) == offline and "modelle/modelle.json" in gelistet
           and not any(n.endswith(".npz") for n in gelistet), f"{len(offline)} / {len(gelistet)}")
    with zipfile.ZipFile(out / "py" / "programm.zip") as z:
        namen = z.namelist()
    nutzer = re.compile(r"(^|/)(karten(\.bak)?\.csv|ideen\.json|lernstand|ui_einstellungen|tools\.json|bilder/|ideen/|ausgabe/|__pycache__)")
    pflicht = {"gans_ui.py", "gans_lernkarten.py", "lernen.py", "leinwand.py", "sprachen.py", "tools.py", "erweiterungen.py",
               "lernkarten_digital.py", "beispiel-karten.csv", "schrift/Poppins-Bold.ttf", "modelle/fsrcnn_x2.npz", "LEITFADEN.md"}
    pruefe("Positivliste: Programm-Paket ohne Nutzerdaten, Startprogramm, KI-Bilder und Tests – alles Nötige dabei",
           pflicht <= set(namen) and not any(nutzer.search(n) or n.startswith("test_") or n in ("starter.py", "ki_bild.py") for n in namen)
           and not any(nutzer.search(n) for n in da), str([n for n in namen if nutzer.search(n)])[:300])
    mf = json.loads((out / "manifest.webmanifest").read_text(encoding="utf-8"))
    symbole = {s["src"]: s for s in mf.get("icons", [])}
    pruefe("Manifest: Name, Kurzname, Start/Scope ./, standalone, Farben, Symbole 192/512 + maskable",
           mf.get("name") == "Me Goos-ta Deutsch" and mf.get("short_name") and mf.get("start_url") == "./" and mf.get("scope") == "./"
           and mf.get("display") == "standalone" and mf.get("background_color") and mf.get("theme_color")
           and symbole.get("symbole/symbol-192.png", {}).get("sizes") == "192x192"
           and symbole.get("symbole/symbol-maskable-512.png", {}).get("purpose") == "maskable", str(mf)[:300])
    groessen = {n: Image.open(out / n).size for n in ("symbole/symbol-192.png", "symbole/symbol-512.png",
                                                       "symbole/symbol-maskable-512.png", "symbole/apple-touch-icon.png")}
    pruefe("Symbole in der richtigen Größe (Apple 180 ohne Transparenz)",
           list(groessen.values()) == [(192, 192), (512, 512), (512, 512), (180, 180)]
           and Image.open(out / "symbole/apple-touch-icon.png").mode == "RGB", str(groessen))
    index = (out / "index.html").read_text(encoding="utf-8")
    ui_js = (out / "ui.js").read_text(encoding="utf-8")
    worker = (out / "worker.js").read_text(encoding="utf-8")
    pruefe("AM_APP-Weichen: Seite ohne eingebettetes Skript (CSP), App-Modus an, relative Adressen, Manifest, viewport-fit=cover",
           not re.search(r"<script(?![^>]*\bsrc=)[^>]*>", index) and "script-src 'self';" in index
           and 'const AM_APP = "1" === "1"' in ui_js and 'const AM_HANDY = "1" === "1"' in ui_js and "__GL_" not in index + ui_js
           and 'url("schrift/' in index and 'url("/schrift/' not in index and 'rel="manifest"' in index and "viewport-fit=cover" in index)
    with open(out / "py" / "programm.zip", "rb") as f:
        zh = hashlib.sha256(f.read()).hexdigest()[:16]
    zweit = subprocess.run([sys.executable, str(bau), str(HIER.parent), str(ziel), "--ohne-pyodide", "--ohne-modelle"], env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    with open(out / "py" / "programm.zip", "rb") as f:
        zh2 = hashlib.sha256(f.read()).hexdigest()[:16]
    pruefe("Worker kennt Programm-Paket (Prüfsumme) und Pakete; gleicher Inhalt = gleiches Paket (neuer Bau lädt nichts unnötig)",
           f'PROGRAMM_HASH = "{zh}"' in worker and not re.search(r"__(PROGRAMM|REPORTLAB|PAKETE)\w*__", worker)
           and zweit.returncode == 0 and zh == zh2, f"{zh} / {zh2}")


def qr_lesen(m):
    """Unabhängiger kleiner QR-Leser (nach der Norm, nicht nach qr_code.py): Formatbits, Maske, Zickzack, Blöcke,
    Reed-Solomon-Syndrome, Byte-Modus. Liefert (Text, Stufe M, Syndrome alle 0, beide Formatkopien gleich)."""
    n = len(m)
    v = (n - 17) // 4
    pos1 = [(i, 8) for i in range(6)] + [(7, 8), (8, 8), (8, 7)] + [(8, 14 - i) for i in range(9, 15)]
    pos2 = [(8, n - 1 - i) for i in range(8)] + [(n - 15 + i, 8) for i in range(8, 15)]
    f1 = sum(m[r][c] << i for i, (r, c) in enumerate(pos1))
    f2 = sum(m[r][c] << i for i, (r, c) in enumerate(pos2))
    fmt = f1 ^ 0x5412
    stufe, maske = fmt >> 13, (fmt >> 10) & 7
    masken = [lambda r, c: (r + c) % 2 == 0, lambda r, c: r % 2 == 0, lambda r, c: c % 3 == 0,
              lambda r, c: (r + c) % 3 == 0, lambda r, c: (r // 2 + c // 3) % 2 == 0,
              lambda r, c: (r * c) % 2 + (r * c) % 3 == 0, lambda r, c: ((r * c) % 2 + (r * c) % 3) % 2 == 0,
              lambda r, c: ((r + c) % 2 + (r * c) % 3) % 2 == 0]
    a = {2: 18, 3: 22, 4: 26, 5: 30, 6: 34}.get(v)
    def funktion(r, c):
        return ((r < 9 and c < 9) or (r < 9 and c >= n - 8) or (r >= n - 8 and c < 9) or r == 6 or c == 6
                or (a is not None and abs(r - a) <= 2 and abs(c - a) <= 2))
    bits, hoch, rechts = [], True, n - 1
    while rechts >= 1:
        if rechts == 6:
            rechts = 5
        for r in (range(n - 1, -1, -1) if hoch else range(n)):
            for c in (rechts, rechts - 1):
                if not funktion(r, c):
                    bits.append(m[r][c] ^ (1 if masken[maske](r, c) else 0))
        hoch, rechts = not hoch, rechts - 2
    ecc, bloecke, gesamt = {1: (10, 1, 26), 2: (16, 1, 44), 3: (26, 1, 70), 4: (18, 2, 100), 5: (24, 2, 134),
                            6: (16, 4, 172)}[v]
    cw = [int("".join(map(str, bits[i * 8:i * 8 + 8])), 2) for i in range(gesamt)]
    je = (gesamt - ecc * bloecke) // bloecke
    daten = [[cw[k * bloecke + b] for k in range(je)] for b in range(bloecke)]
    pruef = [[cw[je * bloecke + k * bloecke + b] for k in range(ecc)] for b in range(bloecke)]
    exp, log, x = [0] * 512, [0] * 256, 1
    for i in range(255):
        exp[i], log[x] = x, i
        x = (x << 1) ^ (0x11D if x & 128 else 0)
    for i in range(255, 512):
        exp[i] = exp[i - 255]
    mal = lambda p, q: exp[log[p] + log[q]] if p and q else 0      # noqa: E731
    syndrome_null = True
    for b in range(bloecke):
        for i in range(ecc):
            s = 0
            for wort in daten[b] + pruef[b]:
                s = mal(s, exp[i]) ^ wort
            syndrome_null = syndrome_null and s == 0
    strom = "".join(f"{w:08b}" for d in daten for w in d)
    if strom[:4] != "0100":
        return None, stufe == 0, syndrome_null, f1 == f2
    laenge = int(strom[4:12], 2)
    roh = bytes(int(strom[12 + 8 * i:20 + 8 * i], 2) for i in range(laenge))
    return roh.decode("utf-8", "replace"), stufe == 0, syndrome_null, f1 == f2


def test_installationsdateien():
    """E32: Handy 3 – Installationsdateien Android/iPhone/Google Pixel neben den Startdateien: vorhanden, ohne Skript
    nutzbar, Adresse = web_adresse.txt, QR-Code = neu erzeugte Matrix derselben Adresse (und lesbar), drei Sprachen;
    QR-Erzeuger für alle Versionen geprüft; Release-Listen und Oberfläche („Als App aufs Handy“)."""
    print("\n[E32] Handy 3: Installationsdateien")
    import qr_code
    import gans_ui as ui
    oben = HIER.parent
    namen = {"android": "Me Goos-ta Deutsch - Android.html", "iphone": "Me Goos-ta Deutsch - iPhone.html",
             "pixel": "Me Goos-ta Deutsch - Google Pixel.html"}
    texte = {g: (oben / n).read_text(encoding="utf-8") if (oben / n).is_file() else "" for g, n in namen.items()}
    pruefe("Drei Installationsdateien neben den Startdateien (Android, iPhone, Google Pixel)",
           all(len(t) > 5000 for t in texte.values()), str({g: len(t) for g, t in texte.items()}))
    pruefe("Ohne JavaScript nutzbar: kein Skript, keine Ereignis-Attribute, nichts von außen geladen (alles eingebettet)",
           all("<script" not in t.lower() and not re.search(r"\son[a-z]+\s*=", t) and "<link" not in t
               and not re.search(r'\ssrc="', t) and "@import" not in t for t in texte.values()))
    wa = (HIER / "web_adresse.txt").read_text(encoding="utf-8").strip() if (HIER / "web_adresse.txt").is_file() else ""
    links = {g: set(re.findall(r'href="(https?://[^"]*)"', t)) for g, t in texte.items()}
    pruefe("Adresse überall = web_adresse.txt (https), großer Knopf in jeder Sprache",
           wa.startswith("https://") and (Path(ui.__file__).resolve().parent != HIER.resolve() or wa == ui.web_adresse())
           and all(l == {wa} and t.count(f'class="gross" href="{wa}"') == 3 for (g, t), l in zip(texte.items(), links.values())),
           f"{wa} {links}")
    soll = qr_code.qr_matrix(wa) if wa else None
    qr_alle = [qr_code.matrix_aus_svg(s) for t in texte.values() for s in re.findall(r"<svg class=\"qr\".*?</svg>", t, re.S)]
    pruefe("QR-Code in jeder Sprache = neu erzeugte Matrix derselben Adresse",
           soll is not None and len(qr_alle) == 9 and all(q == soll for q in qr_alle), f"{len(qr_alle)} QR-Codes")
    gelesen = qr_lesen(qr_alle[0]) if qr_alle else (None,)
    pruefe("QR-Code lesbar (eigener Leser nach Norm): Adresse, Stufe M, Reed-Solomon stimmt, Formatkopien gleich",
           tuple(gelesen) == (wa, True, True, True), str(gelesen))
    proben = ["Gans", "https://gans.github.io/x/", "G" * 40, "w" * 60, "https://beispiel.example/" + "g" * 50, "x" * 84,
              "Ünïcödé-Gänse 🪿 " * 4, "y" * 106]
    ergebnis = []
    for s in proben:
        m = qr_code.qr_matrix(s)
        ergebnis.append(qr_lesen(m) == (s, True, True, True) and qr_code.matrix_aus_svg(qr_code.qr_svg(s)) == m)
    pruefe("QR-Erzeuger: Versionen 1–6 (auch mehrere Blöcke, UTF-8) lesbar, zu lang → nichts",
           all(ergebnis) and sorted({(len(qr_code.qr_matrix(s)) - 17) // 4 for s in proben}) == [1, 2, 3, 4, 5, 6]
           and qr_code.qr_matrix("z" * 107) is None and qr_code.qr_svg("z" * 107) == "", str(ergebnis))
    sprachen_ok = all(all(f'id="{l}" lang="{l}"' in t and f'href="#{l}"' in t for l in ("de", "en", "es"))
                      and t.index('id="en"') > t.index('id="de"') and t.index('id="en"') > t.index('id="es"')
                      and ".sprache:target ~ #en" in t for t in texte.values())
    inhalt = (all(k in texte["iphone"] for k in ("16.4", "Safari", "Zum Home-Bildschirm", "Add to Home Screen",
                                                 "Agregar a pantalla de inicio", "7 Tagen"))
              and all(k in texte["android"] for k in ("Chrome", "App installieren", "Install app", "Instalar app"))
              and all(k in texte["pixel"] for k in ("Pixel", "Zum Startbildschirm hinzufügen", "Add to Home screen",
                                                    "Agregar a la pantalla principal"))
              and all(t.count('<svg class="skizze"') == 12 and "Eine Gans namens Lukas" in t and "Warnung" not in t
                      and "Warning" not in t and "QR" in t for t in texte.values()))
    pruefe("Drei Sprachen (de/en/es, Standard Englisch ohne Skript), Schritte mit Skizzen, Mindestversionen, Gerätenamen",
           sprachen_ok and inhalt)
    bau = HIER.parent.parent / "werkstatt" / "bau_release.py"
    rel = bau.read_text(encoding="utf-8") if bau.is_file() else ""
    seite = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    lies = (oben / "LIES MICH ZUERST.html").read_text(encoding="utf-8")
    readme = (oben / "README.md").read_text(encoding="utf-8")
    pruefe("Release und Projekt-ZIP nehmen die drei Dateien (+ web_adresse.txt) mit; LIES MICH (3 Sprachen) und README "
           "nennen dieselbe Adresse; Oberfläche: QR zur App bei „Am Handy öffnen“ und Hinweis bei „Digital lernen“",
           all(n in ui.OBERE_DATEIEN for n in namen.values())
           and lies.count(f'href="{wa}"') == 3 and lies.count("Google%20Pixel.html#") == 3
           and {u.split("#")[0] for u in re.findall(r"https://[a-z0-9.-]+\.github\.io/[^\s)\"<]*", lies + readme)} == {wa, wa + "download/"}
           and (not rel or (all(n in rel for n in namen.values()) and '"web_adresse.txt"' in rel))
           and "qrSvg(appAdresse())" in seite and seite.count("lan_app_text:") == 3 and seite.count("pr_app_tipp:") == 3
           and 't("pr_app_tipp")' in seite and seite.count("${appTipp()}") == 2 and seite.count("app_anleitungen:") == 3)


def _js_ende(s, i, zu=None):
    """Ende eines JS-Strings/einer Vorlage ab s[i] (zu=None) bzw. eines ${…}-Ausdrucks (zu="}")."""
    if zu is None and s[i] in "\"'":
        j = i + 1
        while s[j] != s[i]:
            j += 2 if s[j] == "\\" else 1
        return j + 1
    if zu is None:                                   # Vorlage `…${…}…`
        j = i + 1
        while s[j] != "`":
            j = _js_ende(s, j + 2, "}") if s.startswith("${", j) else j + (2 if s[j] == "\\" else 1)
        return j + 1
    tiefe = 0
    while True:
        c = s[i]
        if c in "\"'`":
            i = _js_ende(s, i)
            continue
        if c == "{":
            tiefe += 1
        elif c == "}":
            if tiefe == 0:
                return i + 1
            tiefe -= 1
        i += 1


def js_schluessel(s, start):
    """Schlüssel eines JS-Objekts ab s[start] == "{" (Werte dürfen Strings, Vorlagen, Funktionen sein)."""
    i, aus = start + 1, []
    while True:
        i = re.compile(r"(?:[\s,]+|//[^\n]*|/\*.*?\*/)*", re.S).match(s, i).end()
        if s[i] == "}":
            return aus
        m = re.compile(r"""(?:"([^"]+)"|'([^']+)'|([A-Za-z_$][\w$]*))\s*:""").match(s, i)
        aus.append(m.group(1) or m.group(2) or m.group(3))
        i, tiefe = m.end(), 0
        while not (s[i] in ",)]}" and tiefe == 0):
            if s[i] in "\"'`":
                i = _js_ende(s, i)
                continue
            if s.startswith("//", i) or s.startswith("/*", i):
                i = s.index("\n", i) if s[i + 1] == "/" else s.index("*/", i) + 2
                continue
            tiefe += (s[i] in "([{") - (s[i] in ")]}")
            i += 1


def test_fehleranalyse(tmp):
    """E33: Fehleranalyse 2.0 – Texte der Oberfläche vollständig in drei Sprachen (TXT, data-t, t(), L()/T()),
    Adressen in SPEC, Leitfäden gleich gegliedert, Einstellungen ohne verlorene Änderungen bei gleichzeitigen Anfragen,
    Prüffehler/unerwartete Fehler freundlich und dreisprachig, Generator-Hilfe in einer Sprache, Touch-Tippflächen."""
    print("\n[E33] Fehleranalyse und Doku-Prüfung")
    import ast
    import threading
    import gans_lernkarten as gl
    import gans_ui as ui
    seite = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    txt, doppelt = {"de": [], "en": [], "es": []}, []
    a = seite.index("const TXT = {")
    for m in re.finditer(r"\n(de|en|es)\s*:\s*\{", seite[a:seite.index("\n};", a)]):
        txt[m.group(1)] += js_schluessel(seite, a + m.end() - 1)
    for m in re.finditer(r"Object\.assign\(TXT\.(de|en|es),\s*\{", seite):
        txt[m.group(1)] += js_schluessel(seite, m.end() - 1)
    for s, liste in txt.items():
        doppelt += [f"{s}.{k}" for k in set(liste) if liste.count(k) > 1]
    rest = seite[:a] + seite[seite.index("\n};", a):]
    benutzt = set(re.findall(r'data-t="([^"$]+)"', rest))
    benutzt |= {t.split(":", 1)[1] for v in re.findall(r'data-t-attr="([^"$]+)"', rest) for t in v.split(";") if ":" in t}
    benutzt |= set(re.findall(r"""\bt\(\s*["'`]([A-Za-z0-9_]+)["'`]\s*[,)]""", rest))
    alle = set(txt["de"])
    fehlt = sorted(benutzt - alle) + [f"{s}≠de" for s in ("en", "es") if set(txt[s]) != alle]
    pruefe("Oberflächen-Texte: de/en/es gleiche Schlüssel (auch h_*, _touch), keiner doppelt, jedes data-t/t(…) vorhanden",
           len(alle) > 900 and not fehlt and not doppelt and sum(k.startswith("h_") for k in alle) >= 100,
           f"fehlt {fehlt[:6]} doppelt {doppelt[:6]}")
    falsch = []
    for f in sorted(HIER.glob("*.py")):
        if f.name.startswith("test_"):
            continue
        for n in ast.walk(ast.parse(f.read_text(encoding="utf-8"))):
            if isinstance(n, ast.Call) and getattr(n.func, "id", getattr(n.func, "attr", "")) in ("L", "T") \
                    and not (f.name == "starter.py" and getattr(n.func, "id", "") == "T"):
                texte = list(n.args) + [k.value for k in n.keywords]
                konst = [x.value for x in texte if isinstance(x, ast.Constant) and isinstance(x.value, str)]
                if len(texte) != 3 or (len(konst) == 3 and (not all(c.strip() for c in konst) or len(
                        {tuple(sorted(set(re.findall(r"\{(\w+)\}", c)))) for c in konst}) > 1)):
                    falsch.append(f"{f.name}:{n.lineno}")
    pruefe("Python-Texte: L(…)/T(…) immer mit drei nicht leeren Texten und gleichen Platzhaltern", not falsch, str(falsch[:6]))
    code = (HIER / "gans_ui.py").read_text(encoding="utf-8") + (HIER / "erweiterungen.py").read_text(encoding="utf-8")
    spec = (HIER / "SPEC.md").read_text(encoding="utf-8")
    in_spec = {"/api/" + t for g in re.findall(r"/api/([a-z0-9-]+(?:\|[a-z0-9-]+)*)", spec) for t in g.split("|")}
    ohne = sorted(set(re.findall(r'"(/api/[a-z0-9-]+)"', code)) - in_spec)
    pruefe("Jede Adresse aus verarbeite()/erweiterungen steht in SPEC.md", not ohne, str(ohne))

    def gliederung(t):
        teile, im_code = [[0, 0]], False
        for z in t.splitlines():
            im_code ^= z.startswith("```")
            if not im_code and re.match(r"#{1,6} ", z):
                teile.append([len(z) - len(z.lstrip("#")), 0])
            teile[-1][1] += len(re.findall(r"\{\{[^}]+\}\}", z))
        return teile
    lf = [gliederung((HIER / n).read_text(encoding="utf-8")) for n in ("LEITFADEN.md", "LEITFADEN_en.md", "LEITFADEN_es.md")]
    pruefe("Leitfäden de/en/es gleich gegliedert, gleich viele Kartensprache-Marken je Abschnitt",
           lf[0] == lf[1] == lf[2] and len(lf[0]) > 25, str([len(x) for x in lf]))
    alt, fehler = ui.EINSTELLUNGEN, []
    ui.EINSTELLUNGEN = Path(tmp) / "e33_ui_einstellungen.json"
    try:
        def schreiber(i):
            try:
                for _ in range(12):
                    [lambda: ui.speichere_sprache("de" if i % 2 else "es"), lambda: ui.speichere_farben("nacht", {}),
                     lambda: ui.speichere_einstellungen({"qualitaet": "stark"})][i % 3]()
            except Exception as e:  # noqa: BLE001
                fehler.append(repr(e))
        faeden = [threading.Thread(target=schreiber, args=(i,)) for i in range(9)]
        for f in faeden:
            f.start()
        for f in faeden:
            f.join(60)
        d = json.loads(ui.EINSTELLUNGEN.read_text(encoding="utf-8"))
    finally:
        ui.EINSTELLUNGEN = alt
    pruefe("Einstellungen: gleichzeitige Änderungen (Sprache, Farben, Schalter) gehen nicht verloren",
           not fehler and d.get("sprache") in ("de", "es") and (d.get("farben") or {}).get("schema") == "nacht"
           and (d.get("werte") or {}).get("qualitaet") == "stark", f"{fehler[:2]} {d}")
    meld = {}
    for s in ("de", "en", "es"):
        gl.setze_sprache(s)
        anf = ui.Anfrage("GET")
        ui._fehler_antwort(anf, KeyError("gans"))
        meld[s] = (ui.parse(["--karten", "1-x"])[1], anf.antwort[0], json.loads(anf.antwort[2])["fehler"])
    gl.setze_sprache(None)
    try:
        ui.farben_pruefen("eigen", {"akzent": "#AABBCC\n"})
        farbe_ab = False
    except ui.Meldung:
        farbe_ab = True
    pruefe("Prüffehler mit Feldnamen in der Sprache der Oberfläche, unerwarteter Fehler freundlich (3 Sprachen), "
           "Farbwert nur genau #RRGGBB",
           meld["de"][0].startswith("Nur diese Karten: Kartenauswahl") and meld["en"][0].startswith("Only these cards: Card")
           and meld["es"][0].startswith("Solo estas cartas: No se entendió") and farbe_ab
           and all(m[1] == 500 and "(KeyError: 'gans')" in m[2] and not m[2].startswith("KeyError") for m in meld.values())
           and len({m[2] for m in meld.values()}) == 3, str(meld))
    hilfe = {}
    for s in ("de", "en", "es"):
        gl.setze_sprache(s)
        hilfe[s] = gl.baue_parser().format_help()
    gl.setze_sprache(None)
    pruefe("Generator-Hilfe (--help) ganz in der eingestellten Sprache (Gruppen, Beschreibung, Beispiele)",
           "Was erzeugen:" in hilfe["de"] and "Beispiele:" in hilfe["de"] and "What to generate:" in hilfe["en"]
           and "Examples:" in hilfe["en"] and "Ejemplos:" in hilfe["es"] and "Qué generar:" in hilfe["es"]
           and not any(w in hilfe["en"] + hilfe["es"] for w in ("Beispiele", "Was erzeugen", "erzeugt druckfertige")))
    touch = seite[seite.index("/* ---------- Touch (Handy, Tablet)"):seite.index("@media (prefers-reduced-motion")]
    pruefe("Oberfläche: Tabelle zeigt bei Fehler Text statt Ente; Touch-Tippflächen ≥ 44 px (Kopfzeile, Eingaben, "
           "Aufklapper, Sprach-Chips)",
           'if ($("#tabelle .ente-laedt"))' in seite and ".sprachwahl button { min-height: 44px; min-width: 44px; }" in touch
           and ".marke { min-width: 44px; min-height: 44px; }" in touch and "details > summary { min-height: 44px;" in touch
           and ".f select, .eingabe { min-height: 44px; }" in touch and "button.sprach-chip::after" in touch)


def test_englisch_vorab(p, tmp):
    """E34 (2.1): Alles vor der Installation startet auf Englisch – LIES MICH, Startdateien, Startprogramm, Ladebildschirm
    der Handy-App; danach gilt die im Programm gewählte Sprache (nie die Systemsprache). Tools-Teil-Knopf sauber:
    kurzer Titel, Erklärung + Größe in einer zweiten Zeile."""
    print("\n[E34] Englisch vor der Installation, Teil-Knopf im Tools-Fenster")
    oben = HIER.parent
    lies = (oben / "LIES MICH ZUERST.html").read_text(encoding="utf-8")
    skript = lies[lies.rindex("<script>"):]
    pruefe("LIES MICH: startet Englisch (ohne navigator.language), Sprache nur per Knopf oder Anker #de/#es/#en",
           "navigator.language" not in lies and 'sprache = "en"' in skript and "location.hash" in skript
           and "hashchange" in skript and '<body class="en win">' in lies
           and "<title>Me Goos-ta Deutsch – Read me first</title>" in lies)
    cmd = (oben / "Me Goos-ta Deutsch - Windows.cmd").read_bytes().decode("ascii", "replace")
    pruefe("Windows.cmd: ohne Regionseinstellung, SPR=en, gewählte Sprache aus Programm\\ui_einstellungen.json",
           not re.search(r"LocaleName|MGD_SYS_SPRACHE|International", cmd) and 'set "SPR=en"' in cmd
           and cmd.count("Programm\\ui_einstellungen.json") == 2 and "rem  Me Goos-ta Deutsch - start for Windows" in cmd)
    if os.name == "nt":                                  # Block echt ausführen: Ordner mit Leerzeichen, Klammern und „&“
        block = re.search(r'set "SPR=en"\r\n.*?(?=call :texte_%SPR%)', cmd, re.S).group(0)
        ordner = tmp / "e34 cmd (a&b)"
        (ordner / "Programm").mkdir(parents=True)
        probe = ordner / "probe.cmd"
        probe.write_bytes(('@echo off\r\nset "SYS32=%SystemRoot%\\System32"\r\n' + block + "echo SPR=%SPR%\r\n").encode("ascii"))
        ergebnis = {}
        for wahl in (None, "de", "es", "en"):
            einst = ordner / "Programm" / "ui_einstellungen.json"
            if wahl:
                einst.write_text(json.dumps({"zielsprache": "de", "sprache": wahl}, ensure_ascii=False, indent=1), encoding="utf-8")
            r = subprocess.run('cmd /s /c ""%s""' % probe, capture_output=True, text=True, timeout=30)
            ergebnis[wahl] = (re.findall(r"SPR=(\w+)", r.stdout) or ["?"])[0]
        pruefe("Windows.cmd: ohne Wahl en, sonst die gewählte Sprache (de/es/en)",
               ergebnis == {None: "en", "de": "de", "es": "es", "en": "en"}, str(ergebnis))
    mac = (oben / "Me Goos-ta Deutsch - Mac.command").read_text(encoding="utf-8")
    linux = (oben / "Me Goos-ta Deutsch - Linux.sh").read_text(encoding="utf-8")
    pruefe("Mac.command/Linux.sh: SPR=en, gewählte Sprache per grep aus Programm/ui_einstellungen.json, kein LANG/AppleLocale",
           all("SPR=en\n" in s and "ui_einstellungen.json" in s and """grep -q '"sprache": "de"'""" in s
               and not re.search(r"AppleLocale|MGD_SYS_SPRACHE|\$\{LC_ALL|\$\{LANG", s) for s in (mac, linux))
           and "\nde)\n" in mac and "\n*)\n" not in mac[mac.index('case "$SPR" in'):mac.index("fehler() {")]
           and "start for macOS" in mac and "start for Linux" in linux)
    import starter
    alt = (starter.HIER, starter.SPRACHE, {k: os.environ.get(k) for k in ("MGD_SPRACHE", "MGD_SYS_SPRACHE", "LANG", "LC_ALL")})
    leer = tmp / "e34-starter"
    leer.mkdir()
    try:
        starter.HIER = leer
        os.environ.pop("MGD_SPRACHE", None)
        os.environ.update(MGD_SYS_SPRACHE="de", LANG="de_DE.UTF-8", LC_ALL="de_DE.UTF-8")   # „deutsches System“
        ohne = starter.ermittle_sprache()
        os.environ["MGD_SPRACHE"] = "es"
        umgebung = starter.ermittle_sprache()
        (leer / "ui_einstellungen.json").write_text(json.dumps({"sprache": "de"}, indent=1), encoding="utf-8")
        gewaehlt = starter.ermittle_sprache()
        starter.SPRACHE = "es"
        stub_es = starter.startskript_text()
        starter.SPRACHE = "xx"
        stub_xx = starter.startskript_text()
    finally:
        starter.HIER, starter.SPRACHE = alt[0], alt[1]
        for k, v in alt[2].items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    pruefe("Startprogramm: deutsches System ohne Wahl → en, MGD_SPRACHE=es → es, gespeicherte Wahl de → de",
           (ohne, umgebung, gewaehlt) == ("en", "es", "de") and not hasattr(starter, "system_sprache"),
           str((ohne, umgebung, gewaehlt)))
    pruefe("starte.py („Programmordner verschoben“) mit der Sprache der Einrichtung, ohne Systemsprache",
           'TEXT.get("es", TEXT["en"])' in stub_es and 'TEXT.get("en", TEXT["en"])' in stub_xx
           and "GetUserDefaultUILanguage" not in stub_es and '"LANG"' not in stub_es)
    quelle = HIER.parent.parent / "web-app-quelle"
    if (quelle / "app.js").is_file():
        app, sw, worker = ((quelle / n).read_text(encoding="utf-8") for n in ("app.js", "sw.js", "worker.js"))
        pruefe("Handy-App: Ladebildschirm, Service Worker und erster Start ohne Gerätesprache (Englisch bis zur Wahl)",
               "navigator.language" not in app + sw + worker and "speichere_sprache" not in worker
               and 'TEXTE[merke("mgd-sprache")] ? merke("mgd-sprache") : "en"' in app and 'typ: "sprache"' in app
               and 'e.data.typ === "sprache"' in sw)
    import gans_lernkarten as gl
    import tools as tl
    teile = tl.TOOLS["bildverbesserung"]["teile"]
    pruefe("Tools-Teile: kurze Titel ohne Klammern, Erklärung im Feld „hinweis“ (de/en/es)",
           gl.text_in(teile["x2"]["titel"], "en") == "Faster ×2"
           and all("(" not in v["titel"][s] and v["hinweis"][s].strip() for v in teile.values() for s in ("de", "en", "es"))
           and gl.text_in(teile["x2"]["hinweis"], "en") == "almost the same quality, about 4× faster")
    daten = tmp / "daten-e34"
    daten.mkdir()
    proc, se = starte_server(p, daten)
    try:
        _, ti = se.json("/api/tools")
    finally:
        proc.terminate()
        proc.wait(10)
    bv = next((x for x in ti.get("tools", []) if x["id"] == "bildverbesserung"), {})
    x2 = next((x for x in bv.get("teile", []) if x["id"] == "x2"), {})
    pruefe("/api/tools liefert je Teil „hinweis“ in der Sprache der Oberfläche",
           (x2.get("titel"), x2.get("hinweis")) in {(teile["x2"]["titel"][s], teile["x2"]["hinweis"][s]) for s in ("de", "en", "es")}
           and all(isinstance(t.get("hinweis"), str) for x in ti.get("tools", []) for t in x.get("teile", [])), str(x2))
    seite = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    karte = seite[seite.index("function toolKarte("):seite.index("function zeichneTools(")]
    css = re.search(r"\.knopf\.teil \{([^}]*)\}", seite)
    x2_texte = re.findall(r"verb_tool_x2: g => `([^`]*)`", seite)
    pruefe("Teil-Knopf: Klasse „teil“, zweizeilig (fett „+ Titel“, klein „Hinweis · Größe“), bricht in der Karte um",
           'class="knopf klein teil"' in karte and "<b>+ ${esc(p.titel)}</b>" in karte and "<small>" in karte
           and ") (" not in karte and css and "white-space: normal" in css.group(1) and "max-width: 100%" in css.group(1)
           and len(x2_texte) == 3 and all(re.fullmatch(r"[^(]+ · [^(]+\$\{g\}", x) for x in x2_texte), str(x2_texte))


def test_rueckseite_gans(tmp):
    """E35 (2.1): Neue Gans der Rückseite – schwimmt unten rechts im freien Platz (gans_box aus wort_boxen), nie hinter dem
    Text, stufenweise kleiner bis 20 %, sonst keine Gans; Wort und Textgrößen wie in 2.0; Leinwand = pdfium; Druck sauber
    am Innenrand angeschnitten; eigenes Gänse-Bild unverändert."""
    print("\n[E35] Neue Gans auf der Rückseite")
    import numpy as np
    import pypdfium2 as pdfium
    from reportlab.lib.units import mm
    import gans_lernkarten as gl
    import leinwand
    gl.registriere_schriften()
    cfg = gl.Konfig()
    iw, ih = (cfg.b - 2 * cfg.rand) * mm, (cfg.h - 2 * cfg.rand) * mm
    erwartet = {"viejo": (["viejo"], 37.3039, [], 0.0, None),
                "el anciano / el viejo": (["el anciano"], 36.5539, ["el viejo"], 19.008, None),
                "muchísima hambre / me muero de hambre": (["muchísima", "hambre"], 30.1606, ["me muero de hambre"], 15.6835, None),
                "desafortunadamente": (["desafortunadamente"], 17.5539, [], 0.0, None)}
    rund = lambda e: (e[0], round(e[1], 4), e[2], round(e[3], 4), e[4])      # noqa: E731
    pruefe("Textgrößen der Rückseite wie in 2.0 (layout_wort, Stichproben fest im Test)",
           all(rund(gl.layout_wort(w, iw, ih)) == e for w, e in erwartet.items()),
           str([rund(gl.layout_wort(w, iw, ih)) for w in erwartet]))

    cache = _sprachpakete_e27()                          # echte Schriften für ja/ar/hi, wenn vorhanden (sonst Poppins)
    alt = os.environ.get("MGD_DATEN")
    if cache:
        os.environ["MGD_DATEN"] = str(cache)
    try:
        woerter = [("es", "viejo"), ("es", "el anciano / el viejo"), ("es", "¡hola! / ¿qué tal?"),
                   ("es", "muchísima hambre / me muero de hambre"), ("es", "desafortunadamente"),
                   ("es", "electroencefalografista / desoxirribonucleico"),
                   ("es", "a / " + " / ".join(c * 22 for c in "bcd")), ("ja", "こんにちは / やあ"),
                   ("ar", "مرحبا / أهلا"), ("hi", "नमस्ते / राम राम"), ("es", " ")]
        fehler, hoehen = [], {}
        for code, w in woerter:
            boxen = gl.wort_boxen(0, 0, iw, ih, w, gl.satz(code))
            b = gl.gans_box(0, 0, iw, ih, boxen)
            if not b:
                fehler.append((code, w, "keine Gans"))
                continue
            x, y, bw, bh = b
            hoehen[w] = bh / ih
            luft = gl.GANS_ABSTAND * ih - 1e-6
            frei = all(x >= tx + tw + luft or x + bw <= tx - luft or y >= ty + th + luft or y + bh <= ty - luft
                       for tx, ty, tw, th in boxen)
            if not (frei and abs(x + bw - iw) < 1e-6 and y == 0 and x >= 0 and bh <= ih and abs(bw - gl.GANS_SEITE * bh) < 1e-6):
                fehler.append((code, w, [round(v, 1) for v in b]))
        pruefe("Gans-Box unten rechts in der Innenfläche, mit Abstand zu jeder Textzeile (es, ja, ar rechts-nach-links, hi; "
               "1–2 Zeilen ± Alternative, langes Wort)", not fehler, str(fehler))
        voll = "uno|dos|tres / " + " / ".join(c * 20 for c in "efgh")
        pruefe("Größe adaptiv: Standard 34 % der Innenhöhe, bei viel Text kleiner (nie unter 20 %), ohne Platz keine Gans",
               round(hoehen.get("viejo", 0), 2) == 0.34 and 0.20 <= min(hoehen.values())
               and hoehen.get("muchísima hambre / me muero de hambre", 1) < 0.34
               and gl.gans_box(0, 0, iw, ih, gl.wort_boxen(0, 0, iw, ih, voll)) is None, str(hoehen))
    finally:
        if alt is None:
            os.environ.pop("MGD_DATEN", None)
        else:
            os.environ["MGD_DATEN"] = alt

    dpi, k = 100, 100 / 72
    bg = np.array([0xBF, 0xDD, 0xF2])

    def pixel(png):
        return np.asarray(Image.open(io.BytesIO(png)).convert("RGB")).astype(int)

    def bereich(a, x0, y0, x1, y1):                      # pt, links unten → rechts oben
        h = a.shape[0]
        return a[round(h - y1 * k):round(h - y0 * k), round(x0 * k):round(x1 * k)]

    def karte(w):
        return dict(nr=0, bild="", pfad=None, de="", es=w, notiz="", fit="contain")

    ix = iy = cfg.rand * mm
    r = cfg.radius * mm
    leer = pixel(gl.vorschau_png(karte(" "), cfg, seite="hinten", dpi=dpi)[0])
    gx, gy, gw, gh = gl.gans_box(ix, iy, iw, ih, gl.wort_boxen(ix, iy, iw, ih, " "))
    maske = np.zeros(leer.shape[:2], bool)
    h_px = leer.shape[0]
    maske[round(h_px - (iy + ih - r) * k):round(h_px - (iy + r) * k), round((ix + r) * k):round((ix + iw - r) * k)] = True
    maske[round(h_px - (gy + gh) * k) - 2:, round(gx * k) - 2:] = False
    box = bereich(leer, gx, gy, gx + gw, gy + gh)
    weiss = (np.abs(box - 255).max(axis=2) <= 2).sum()
    orange = (np.abs(box - np.array([0xF6, 0xA9, 0x4B])).max(axis=2) <= 6).sum()
    pruefe("Rückseite ohne Wort: Fläche außerhalb der Gans-Box nur Hintergrundfarbe (kein Kreis, kein Streifen); "
           "in der Box eine weiße Gans mit orangem Schnabel",
           int(np.abs(leer[maske] - bg).max()) <= 3 and weiss > 200 and orange > 10, f"{weiss} {orange}")

    fehlt = "uno|dos|tres / " + " / ".join(c * 20 for c in "efgh")
    ohne = pixel(gl.vorschau_png(karte(fehlt), cfg, seite="hinten", dpi=dpi)[0])
    ecke = bereich(ohne, ix + 0.94 * iw, iy + r, ix + iw - r, iy + 0.30 * ih)      # rechts neben dem Text
    eigen = tmp / "e35-gans.png"
    Image.new("RGB", (300, 200), (40, 160, 60)).save(eigen)
    mit_bild = pixel(gl.vorschau_png(karte("viejo"), gl.Konfig(gans_bild=str(eigen)), seite="hinten", dpi=dpi)[0])
    gruen = bereich(mit_bild, gx, gy + r, gx + gw - r, gy + gh)
    pruefe("Kein Platz → keine Gans (Ecke bleibt Hintergrund); eigenes Gänse-Bild deckt wie bisher alles, ohne gezeichnete Gans",
           int(np.abs(ecke - bg).max()) <= 3 and int(np.abs(gruen - np.array([40, 160, 60])).max()) <= 6)

    abw = []
    for code, w in (("es", "viejo"), ("es", "muchísima hambre / me muero de hambre")):
        c2 = gl.Konfig(sprache=code)
        a = pixel(gl.vorschau_png(karte(w), c2, seite="hinten", dpi=dpi)[0])
        b = pixel(gl._rueckseite_pillow(karte(w), c2, c2.b * mm, c2.h * mm, dpi)[0])
        abw.append(round(float(np.abs(a - b).mean()), 2) if a.shape == b.shape else 99)
    lw = leinwand.Leinwand(20, 20, dpi=72, ueber=1)
    lw.saveState()
    lw.rotate(90)
    gedreht = lw._px(1, 0)
    lw.restoreState()
    lw.setStrokeColor("#000000")
    lw.setLineWidth(1)
    p = lw.beginPath()
    p.moveTo(2, 2)
    p.lineTo(10, 18)
    p.lineTo(18, 2)
    lw.drawPath(p, stroke=1, fill=0)
    offen = lw.bild.getpixel((10, 18))                  # hier läge die Schlusslinie eines geschlossenen Pfads
    pruefe("Rückseite mit Leinwand (ohne pypdfium2) = pdfium (Abweichung < 4); Leinwand kann rotate, offene Linienzüge bleiben offen",
           max(abw) < 4 and abs(gedreht[0]) < 1e-9 and abs(gedreht[1] - 19) < 1e-9 and offen == (255, 255, 255), f"{abw} {gedreht} {offen}")

    vorn = tmp / "e35-vorn.jpg"
    vorn.write_bytes(jpg())
    pdf_pfad = tmp / "e35-druckerei.pdf"
    gl.baue_druckerei(cfg, [dict(karte("viejo"), front_jpg=vorn)], pdf_pfad)
    pdf = pdfium.PdfDocument(str(pdf_pfad))
    seite = np.asarray(pdf[1].render(scale=k).to_pil().convert("RGB")).astype(int)
    pdf.close()
    bl = cfg.beschnitt * mm
    rand_unten = bereich(seite, 0, 0, cfg.b * mm + 2 * bl, bl + cfg.rand * mm - 1)
    rand_rechts = bereich(seite, bl + cfg.b * mm - cfg.rand * mm + 1, 0, cfg.b * mm + 2 * bl, cfg.h * mm + 2 * bl)
    gans_druck = bereich(seite, bl + gx, bl + gy, bl + gx + gw, bl + gy + gh)
    pruefe("Druckerei mit Beschnitt: Gans und Teich enden sauber am Innenrand (Rand, Beschnitt, Schnittbereich weiß), Gans im Druck",
           int(rand_unten.min()) >= 250 and int(rand_rechts.min()) >= 250
           and (np.abs(gans_druck - np.array([0xF6, 0xA9, 0x4B])).max(axis=2) <= 8).sum() > 10)


def test_download_seite(tmp):
    """E36 (2.1): Download-Seite für den Rechner (…/download/ auf GitHub Pages) und Release-Werkzeug: Seite baut mit einer
    Release-ZIP (Link, Größe, SHA-256) bzw. ohne (neuestes Release), drei Sprachen mit gleichen Abschnitten, ohne Skript
    Englisch und alle Systeme, nur eigene Quellen, Service Worker lässt download/ durch; veroeffentliche_release.py --probe
    nennt Tag, Assets und SHA256SUMS.txt richtig und lehnt Nutzerdaten, falsche Version und abweichende ZIP ab; Links in
    README, LIES MICH und Oberfläche. Ohne die Skripte des Arbeitsordners entfallen die Bau-Prüfungen (11)."""
    print("\n[E36] Download-Seite + Release-Werkzeug")
    import hashlib
    from urllib.parse import urlparse
    import qr_code
    oben, arbeit = HIER.parent, HIER.parent.parent
    wa = (HIER / "web_adresse.txt").read_text(encoding="utf-8").strip()
    dl = wa + "download/"
    seite = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    lies = (oben / "LIES MICH ZUERST.html").read_text(encoding="utf-8")
    readme = (oben / "README.md").read_text(encoding="utf-8")
    leit = "".join((HIER / n).read_text(encoding="utf-8") for n in ("LEITFADEN.md", "LEITFADEN_en.md", "LEITFADEN_es.md"))
    pruefe("Download-Adresse = web_adresse.txt + download/: README, LIES MICH (de/en/es beim Update), Leitfäden, „Über“ und App-Blatt „Mehr“",
           wa.startswith("https://") and f"**⬇️ Download:** {dl}" in readme and leit.count(dl) == 3
           and set(re.findall(r"https://[a-z0-9.-]+\.github\.io/[^\s)\"<]*", leit)) == {dl}
           and all(lies.count(f'href="{dl}#{l}"') == 1 for l in ("de", "en", "es"))
           and 'return a ? a + "download/#" + S.sprache : "";' in seite and seite.count("${esc(downloadAdresse())}") == 2
           and all(seite.count(k + ":") == 3 for k in ("u_download", "u_download_text", "app_rechner")))
    bau, rel_bau, rel_skript = arbeit / "werkstatt" / "bau_webapp.py", arbeit / "werkstatt" / "bau_release.py", arbeit / "werkstatt" / "veroeffentliche_release.py"
    if not all(x.is_file() for x in (bau, rel_bau, rel_skript, arbeit / "web-app-quelle" / "sw.js")):
        print("  (werkstatt/ und web-app-quelle/ liegen nur im Quellbaum – Bau-Prüfungen entfallen)")
        return
    env = dict(os.environ, PYTHONIOENCODING="utf-8")

    def lauf(*args):
        return subprocess.run([sys.executable, *map(str, args)], env=env, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=600)
    version = re.search(r'^VERSION = "([\d.]+)', (HIER / "gans_lernkarten.py").read_text(encoding="utf-8"), re.M)[1]
    konto, repo = re.match(r"^https://([a-z0-9-]+)\.github\.io/([^/]+)/$", wa).groups()
    rel = tmp / "e36-release"
    r1, r2 = lauf(rel_bau, oben, rel), lauf(rel_bau, oben, rel, "--zip")
    zip_pfad, ordner = rel / f"Me-Goos-ta-Deutsch-{version}.zip", rel / "Me-Goos-ta-Deutsch"
    pruefe("bau_release.py baut Release-Ordner und ZIP (Grundlage für Release und Download-Seite)",
           r1.returncode == 0 and r2.returncode == 0 and zip_pfad.is_file(), (r1.stdout + r1.stderr + r2.stdout + r2.stderr)[-600:])
    if not zip_pfad.is_file():
        return
    zdaten = zip_pfad.read_bytes()
    zsha = hashlib.sha256(zdaten).hexdigest()
    asset = f"https://github.com/{konto}/{repo}/releases/download/v{version}/{zip_pfad.name}"
    ziel = tmp / "e36-web"
    b = lauf(bau, oben, ziel, "--ohne-pyodide", "--ohne-modelle", "--release-zip", zip_pfad)
    out = ziel / "web-app"
    html = (out / "download" / "index.html").read_text(encoding="utf-8") if (out / "download" / "index.html").is_file() else ""
    js = (out / "download" / "seite.js").read_text(encoding="utf-8") if (out / "download" / "seite.js").is_file() else ""
    pruefe("bau_webapp.py --release-zip baut die Download-Seite web-app/download/ (index.html + seite.js)",
           b.returncode == 0 and len(html) > 20000 and len(js) > 1000, (b.stdout + b.stderr)[-600:])
    if not html or not js:
        return
    anfaenge = sorted((html.index(f'<div class="sprache" id="{l}" lang="{l}"'), l) for l in ("de", "en", "es"))
    teil = {l: html[s:(anfaenge[i + 1][0] if i + 1 < len(anfaenge) else html.index("</body>"))] for i, (s, l) in enumerate(anfaenge)}
    zahlen = {l: [len(re.findall(m, x)) for m in ("<h2", "<h3", "<h4", "<li", "<details", '<svg class="skizze pc"', "<article",
                                                  'class="gross"', "data-os-teil=", "data-nur-js hidden", "data-nur-handy hidden")]
              for l, x in teil.items()}
    pruefe("Drei Sprachen mit gleichen Abschnitten: je System drei Schritte mit Skizze + Hilfe, 6× „Was drin ist“, 5 Fragen",
           zahlen["de"] == zahlen["en"] == zahlen["es"] and zahlen["en"][3] >= 9 and zahlen["en"][4] == 5
           and zahlen["en"][5] == 9 and zahlen["en"][6] == 6, str(zahlen))
    pruefe("Ohne Skript: <html lang=\"en\">, Englisch zuletzt und sichtbar (#de/#es per :target), alle drei Systeme; Skript nur als Datei",
           html.startswith('<!doctype html>\n<html lang="en">') and anfaenge[-1][1] == "en"
           and ".sprache:target, #en { display:block; }" in html and ".sprache:target ~ #en { display:none; }" in html
           and not re.search(r"<script(?![^>]*\bsrc=)[^>]*>", html) and '<script src="seite.js" defer></script>' in html
           and not re.search(r"\son[a-z]+\s*=", html) and "html[data-os=win] [data-os-teil]" in html
           and all(x.count('data-os-teil="win"') == x.count('data-os-teil="mac"') == x.count('data-os-teil="linux"') == 2
                   for x in teil.values()))
    mb = f"{len(zdaten) / 1e6:.1f} MB"
    pruefe("Download-Knopf je System = Release-Asset der Test-ZIP; Version, Größe und SHA-256 stimmen (je Sprache)",
           all(x.count(f'href="{asset}"') == 3 and zsha in x and f"{version} · " in x for x in teil.values())
           and mb.replace(".", ",") in teil["de"] and mb in teil["en"] and mb in teil["es"]
           and teil["en"].count(f'href="https://github.com/{konto}/{repo}/releases/download/v{version}/SHA256SUMS.txt"') == 1)
    refs = re.findall(r'(?:src|href)="(\.\./[^"#]+)"', html) + re.findall(r'url\("(\.\./[^"]+)"\)', html)
    hosts = {urlparse(u).netloc for u in re.findall(r"https?://[^\s\"'<>)]+", html + js)}
    pruefe("Nur eigene Quellen: Links nur zu github.com und zur App-Adresse, Schrift/Symbol aus dem App-Ordner, CSP, kein „Warning“",
           hosts <= {"github.com", urlparse(wa).netloc} and len(refs) >= 6
           and all((out / "download" / r).resolve().is_file() for r in refs)
           and "connect-src 'none'" in html and not re.search(r"warning|warnung", html + js, re.I)
           and "fetch(" not in js and "XMLHttpRequest" not in js
           and "try { return localStorage.getItem" in js and "try { localStorage.setItem" in js, f"{hosts} {refs}")
    soll = qr_code.qr_matrix(wa)
    qrs = [qr_code.matrix_aus_svg(s) for s in re.findall(r'<svg class="qr".*?</svg>', html, re.S)]
    pruefe("Handy-Abschnitt: QR-Code in jeder Sprache = Matrix der App-Adresse, Knöpfe zur App",
           len(qrs) == 3 and all(q == soll for q in qrs) and all(x.count(f'href="{wa}"') == 2 for x in teil.values()))
    sw = (out / "sw.js").read_text(encoding="utf-8")
    liste = json.loads(re.search(r"^const DATEIEN = (\[.*?\]);", sw, re.M).group(1))
    v1 = json.loads((out / "manifest.webmanifest").read_text(encoding="utf-8"))["x_version"]
    b2 = lauf(bau, oben, ziel, "--ohne-pyodide", "--ohne-modelle")
    html2 = (out / "download" / "index.html").read_text(encoding="utf-8") if b2.returncode == 0 else ""
    v2 = json.loads((out / "manifest.webmanifest").read_text(encoding="utf-8"))["x_version"] if b2.returncode == 0 else ""
    pruefe("Service Worker lässt download/ durch (vor App-Wegen und Vorrat), nicht in der Vorrat-Liste, App-Version bleibt gleich",
           "const EIGENE_SEITEN = /^download(\\/|$)/;" in sw
           and sw.index("if (EIGENE_SEITEN.test(rel)) return;") < sw.index("if (APP_WEGE.test(rel))")
           and not any(x[0].startswith("download") for x in liste) and v1 == v2 and v1.startswith(version + "-"), f"{v1} / {v2}")
    pruefe("Ohne --release-zip: Knöpfe führen zum neuesten Release, ohne Größe und Prüfsumme",
           html2.count(f'href="https://github.com/{konto}/{repo}/releases/latest"') == 9 and zsha not in html2
           and "SHA256SUMS" not in html2, (b2.stdout + b2.stderr)[-400:])
    OHNE_CI = "E36 prüft nur den Plan (CI-Schranke: E39)"
    pr = lauf(rel_skript, ordner, zip_pfad, "--probe", "--ohne-ci", OHNE_CI)
    m = re.search(r"^#plan (.*)$", pr.stdout, re.M)
    plan = json.loads(m.group(1)) if m else {}
    pruefe("veroeffentliche_release.py --probe: Tag v<Version>, Assets ZIP + SHA256SUMS.txt (Format sha256sum) + .minisig, main, Latest, Adressen, Notizen EN/DE/ES",
           pr.returncode == 0 and plan.get("tag") == f"v{version}"
           and plan.get("assets") == [zip_pfad.name, "SHA256SUMS.txt", "SHA256SUMS.txt.minisig"]
           and plan.get("summen") == f"{zsha}  {zip_pfad.name}\n" and plan.get("branch") == "main" and plan.get("latest") is True
           and plan.get("download") == asset and plan.get("seite") == dl and plan.get("titel") == f"Me Goos-ta Deutsch {version}"
           and set(plan.get("ausfuehrbar", [])) == {"Me Goos-ta Deutsch - Mac.command", "Me Goos-ta Deutsch - Linux.sh"}
           and all(k in pr.stdout for k in ("**Deutsch:**", "**Español:**", f"{dl}#de", "Eine Gans namens Lukas")),
           (pr.stdout + pr.stderr)[-600:])
    karten = ordner / "Programm" / "karten.csv"
    karten.write_text("bild;de;es;notiz\n", encoding="utf-8")
    nd = lauf(rel_skript, ordner, zip_pfad, "--probe", "--ohne-ci", OHNE_CI)
    karten.unlink()
    falsch = rel / "Me-Goos-ta-Deutsch-9.9.zip"
    shutil.copyfile(zip_pfad, falsch)
    fv = lauf(rel_skript, ordner, falsch, "--probe", "--ohne-ci", OHNE_CI)
    lm = ordner / "README.md"
    alt = lm.read_bytes()
    lm.write_bytes(alt + b"\n")
    zm = lauf(rel_skript, ordner, zip_pfad, "--probe", "--ohne-ci", OHNE_CI)
    lm.write_bytes(alt)
    pruefe("--probe lehnt ab: Nutzerdaten im Ordner, falsche Version, ZIP ≠ Ordner – kein Plan",
           nd.returncode != 0 and "karten.csv" in nd.stderr and fv.returncode != 0 and zm.returncode != 0
           and "#plan" not in nd.stdout + fv.stdout + zm.stdout, (nd.stderr + fv.stderr + zm.stderr)[-400:])


def test_status_englisch(tmp):
    """E37 (2.1): `--status` des Startprogramms folgt der Sprache wie alles vor der Installation – ohne Wahl im Programm
    Englisch (auch auf einem deutschen System), sonst die gewählte Sprache."""
    print("\n[E37] Status des Startprogramms")
    import contextlib
    import io
    import starter
    alt = (starter.HIER, starter.SPRACHE, os.environ.get("MGD_SPRACHE"))
    leer = tmp / "e37-starter"
    leer.mkdir()
    aus = {}
    try:
        starter.HIER = leer
        os.environ.pop("MGD_SPRACHE", None)
        for wahl in (None, "de", "es"):
            if wahl:
                (leer / "ui_einstellungen.json").write_text(json.dumps({"sprache": wahl}), encoding="utf-8")
            starter.SPRACHE = starter.ermittle_sprache()
            puffer = io.StringIO()
            with contextlib.redirect_stdout(puffer):
                starter.zeige_status(None)
            aus[wahl or "ohne"] = puffer.getvalue()
    finally:
        starter.HIER, starter.SPRACHE = alt[0], alt[1]
        if alt[2] is None:
            os.environ.pop("MGD_SPRACHE", None)
        else:
            os.environ["MGD_SPRACHE"] = alt[2]
    pruefe("--status: ohne Wahl Englisch (Program folder, Set up), Wahl de → Programmordner, Wahl es → Carpeta del programa",
           "Program folder:" in aus["ohne"] and "Set up:" in aus["ohne"] and "Programmordner" not in aus["ohne"]
           and "Programmordner:" in aus["de"] and "Carpeta del programa:" in aus["es"]
           and all(z.count("\n") == 7 for z in aus.values()), {k: v.splitlines()[1:2] for k, v in aus.items()})


def test_ci(tmp):
    """E38 (2.2): Automatische Tests auf GitHub-Rechnern – ci_lauf.py --probe zeigt den Plan (Branch ci, Release-Inhalt +
    .github, Prüfsumme) ohne Netz und schreibt nichts, verweigert jeden anderen Branch; frischtest.py verweigert die echte
    Startdatei ohne GITHUB_ACTIONS; tests.yml statisch (Actions per SHA, nur Lesen, pull_request nur auf main und nie
    pull_request_target – seit 2.5 G05, Zeitlimit, fail-fast aus); Release-ZIP ohne .github. Ohne die Dateien des
    Arbeitsordners (ci_lauf.py, .github/) entfallen alle 5."""
    print("\n[E38] Automatische Tests auf allen Systemen (CI)")
    import hashlib
    import importlib.util
    arbeit = HIER.parent.parent
    ci_lauf, frisch = arbeit / "werkstatt" / "ci_lauf.py", arbeit / ".github" / "ci" / "frischtest.py"
    wf, rel_bau = arbeit / ".github" / "workflows" / "tests.yml", arbeit / "werkstatt" / "bau_release.py"
    if not all(x.is_file() for x in (ci_lauf, frisch, wf, rel_bau, arbeit / "werkstatt" / "veroeffentliche_webapp.py")):
        print("  (werkstatt/ci_lauf.py und .github/ liegen nur im Quellbaum – CI-Prüfungen entfallen)")
        return
    env = dict(os.environ, PYTHONIOENCODING="utf-8", GH_TOKEN="", HTTPS_PROXY="http://127.0.0.1:9",
               HTTP_PROXY="http://127.0.0.1:9")                  # kein Netz: jede Anfrage liefe ins Leere
    env.pop("GITHUB_ACTIONS", None)

    def lauf(*args):
        return subprocess.run([sys.executable, *map(str, args)], env=env, cwd=str(tmp), capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=600)
    vorher = sorted((p.name, p.stat().st_mtime) for p in arbeit.iterdir() if p.is_file())
    pr = lauf(ci_lauf, HIER.parent, "--probe")
    nachher = sorted((p.name, p.stat().st_mtime) for p in arbeit.iterdir() if p.is_file())
    m = re.search(r"^#plan (.*)$", pr.stdout, re.M)
    plan = json.loads(m.group(1)) if m else {}
    spec = importlib.util.spec_from_file_location("ci_lauf_e38", ci_lauf)
    cl = importlib.util.module_from_spec(spec)
    vorher_bc = sys.dont_write_bytecode
    sys.dont_write_bytecode = True                              # kein __pycache__ im Arbeitsordner
    try:
        spec.loader.exec_module(cl)
    finally:
        sys.dont_write_bytecode = vorher_bc
    rel = tmp / "e38-release"
    subprocess.run([sys.executable, str(rel_bau), str(HIER.parent), str(rel)], env=env, capture_output=True, timeout=300)
    summe = cl.inhalt_pruefsumme(rel / HIER.parent.name) if (rel / HIER.parent.name).is_dir() else ""
    pruefe("ci_lauf.py --probe: Plan für Branch ci (Release-Inhalt + tests.yml + frischtest.py, Prüfsumme = Release-Ordner), ohne Netz, schreibt nichts",
           pr.returncode == 0 and plan.get("branch") == "ci" and plan.get("workflows") == ["release_pruefung.yml", "scorecard.yml", "tests.yml"]
           and {".github/workflows/tests.yml", ".github/ci/frischtest.py", ".github/ci/bau.py"} <= set(plan.get("github", []))
           and plan.get("pruefsumme") == summe and len(summe) == 64 and plan.get("dateien", 0) > 60 and vorher == nachher,
           (pr.stdout + pr.stderr)[-500:])
    b1, b2 = lauf(ci_lauf, HIER.parent, "--probe", "--branch", "main"), lauf(ci_lauf, HIER.parent, "--branch", "gh-pages")
    quelle = ci_lauf.read_text(encoding="utf-8")
    pruefe("ci_lauf.py verweigert jeden anderen Branch (main, gh-pages) vor jedem Netz; Force-Push nur nach refs/heads/ci",
           all(b.returncode != 0 and "verweigert" in b.stderr and "#plan" not in b.stdout for b in (b1, b2))
           and "ziel_ref = pruefe_branch(branch)" in quelle and quelle.count('"--force"') == 1
           and 'f"HEAD:{ziel_ref}"' in quelle and 'return f"refs/heads/{BRANCH}"' in quelle, (b1.stderr + b2.stderr)[-300:])
    f1 = lauf(frisch, "--system", "e38", "--ergebnis", tmp / "e38-ergebnis.json")
    f2 = lauf(frisch, "--lokal", tmp / "e38-lokal", "--quelle", HIER.parent)
    pruefe("frischtest.py verweigert die echte Startdatei ohne GITHUB_ACTIONS=true (kein Ergebnis) und --lokal in Temp",
           f1.returncode != 0 and "GITHUB_ACTIONS" in f1.stderr and not (tmp / "e38-ergebnis.json").exists()
           and "Frischtest" not in f1.stdout and f2.returncode != 0 and not (tmp / "e38-lokal").exists(),
           (f1.stdout + f1.stderr + f2.stderr)[-300:])
    y = wf.read_text(encoding="utf-8")
    uses = re.findall(r"^\s*-?\s*uses:\s*(\S+)", y, re.M)
    jobs = re.findall(r"^  ([a-z][a-z0-9_-]*):\s*$", y.split("\njobs:", 1)[1], re.M) if "\njobs:" in y else []
    zeiten = [int(z) for z in re.findall(r"^\s+timeout-minutes:\s*(\d+)", y, re.M)]
    pruefe("tests.yml: Actions per Commit-SHA, nur contents: read, Auslöser push auf ci + main, pull_request auf main (nie "
           "pull_request_target), workflow_dispatch, Zeitlimit je Job, fail-fast aus, keine Secrets",
           uses and all(re.fullmatch(r"actions/[a-z-]+@[0-9a-f]{40}", u) for u in uses)
           and re.search(r"^permissions:\n  contents: read\n\n", y, re.M) and "write" not in y and "pull_request_target" not in y
           and re.search(r"^on:\n  push:\n    branches: \[ci, main\]\n  pull_request:\n    branches: \[main\]\n"
                         r"  workflow_dispatch:\n\n", y, re.M) and "schedule" not in y
           and len(jobs) >= 2 and len(zeiten) == len(jobs) and all(0 < z <= 45 for z in zeiten)
           and "fail-fast: false" in y and "secrets." not in y
           and y.count("persist-credentials: false") == sum(1 for u in uses if u.startswith("actions/checkout@"))
           and all(s in y for s in ("windows-latest", "windows-11-arm", "os: macos-15 }", "macos-15-intel", "ubuntu-latest",
                                    "ubuntu-24.04-arm", "debian:stable-slim")) and "os: macos-14" not in y, f"{uses} {jobs} {zeiten}")
    version = re.search(r'^VERSION = "([\d.]+)', (HIER / "gans_lernkarten.py").read_text(encoding="utf-8"), re.M)[1]
    zip_pfad = tmp / "e36-release" / f"Me-Goos-ta-Deutsch-{version}.zip"
    if not zip_pfad.is_file():
        subprocess.run([sys.executable, str(rel_bau), str(HIER.parent), str(tmp / "e38-zip"), "--zip"], env=env,
                       capture_output=True, timeout=300)
        zip_pfad = tmp / "e38-zip" / f"Me-Goos-ta-Deutsch-{version}.zip"
    namen = zipfile.ZipFile(zip_pfad).namelist() if zip_pfad.is_file() else []
    oben = {p.relative_to(rel / HIER.parent.name).parts[0] for p in (rel / HIER.parent.name).rglob("*")} if summe else set()
    pruefe("Release-ZIP und -Ordner ohne .github/.gitattributes (CI-Dateien nur im Branch ci)",
           len(namen) > 60 and not any(".github" in n or ".gitattributes" in n for n in namen)
           and not any(o.startswith(".") for o in oben) and hashlib.sha256(b"").hexdigest() != summe, str(sorted(oben))[:200])


def test_ci_browser(tmp):
    """E39 (2.2): Browser-Test, Release-Prüfung und Release-Schranke – browser_test.py statisch (Abläufe A/B1/B2 in drei
    Engines, keine festen Wartezeiten > 30 s, keine Schlüssel, Playwright nie im Programm), release_pruefung.yml (nach jedem
    Push auf main, seit dem Fix vom 21.10.2026 statt wöchentlich) und Browser-Job in tests.yml statisch, ci_lauf.py legt
    web-app/ bzw. (--release-pruefung) nur diesen Workflow mit push-Auslöser auf ci in den Branch ci, veroeffentliche_release.py --probe nur mit grünem CI-Ergebnis für genau diesen Inhalt (.github/ im Plan, im
    Ordner ignoriert, --ohne-ci nur mit Begründung), gleiche Prüfsumme wie ci_lauf.py, neuestes_release.py ohne Netz sauber.
    Ohne die Dateien des Arbeitsordners entfallen alle 7."""
    print("\n[E39] Browser-Test, Release-Prüfung, Release-Schranke (CI)")
    import importlib.util
    arbeit = HIER.parent.parent
    ci = arbeit / ".github"
    bt, nr, woche, wf = ci / "ci" / "browser_test.py", ci / "ci" / "neuestes_release.py", ci / "workflows" / "release_pruefung.yml", \
        ci / "workflows" / "tests.yml"
    ci_lauf, vr, rel_bau = arbeit / "werkstatt" / "ci_lauf.py", arbeit / "werkstatt" / "veroeffentliche_release.py", arbeit / "werkstatt" / "bau_release.py"
    if not all(x.is_file() for x in (bt, nr, woche, wf, ci_lauf, vr, rel_bau, arbeit / "werkstatt" / "bau_webapp.py")):
        print("  (werkstatt/ und .github/ liegen nur im Quellbaum – Prüfungen entfallen)")
        return
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1", GH_TOKEN="",
               HTTPS_PROXY="http://127.0.0.1:9", HTTP_PROXY="http://127.0.0.1:9")     # kein Netz
    env.pop("GITHUB_ACTIONS", None)

    def lauf(*args):
        return subprocess.run([sys.executable, *map(str, args)], env=env, cwd=str(tmp), capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=600)

    def modul(pfad, name):
        spec = importlib.util.spec_from_file_location(name, pfad)
        m = importlib.util.module_from_spec(spec)
        vorher = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        try:
            spec.loader.exec_module(m)
        finally:
            sys.dont_write_bytecode = vorher
        return m
    # 1) browser_test.py statisch + Aufruf ohne Playwright
    q = bt.read_text(encoding="utf-8")
    m = modul(bt, "browser_test_e39")
    stufen = {(a[0], e) for a in m.ABLAEUFE for e in a[1]}
    warten = [float(x) for x in re.findall(r"time\.sleep\(\s*([\d.]+)", q)] + \
        [float(x.replace("_", "")) / 1000 for x in re.findall(r"wait_for_timeout\(\s*([\d_]+)", q)]
    schluessel = re.findall(r"(ghp_[A-Za-z0-9]{20,}|github_pat_\w{20,}|gho_\w{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY)", q)
    imp = [f.name for f in HIER.glob("*.py") if re.search(r"^\s*(import|from)\s+playwright", f.read_text(encoding="utf-8"), re.M)]
    req = (HIER / "requirements.txt").read_text(encoding="utf-8") + (HIER / "DRITTLIZENZEN.md").read_text(encoding="utf-8")
    falsch = lauf(bt, "--engines", "netscape")
    pruefe("browser_test.py: Abläufe A/B1/B2 in Chromium, Firefox und WebKit, keine feste Wartezeit > 30 s, keine Schlüssel, "
           "Playwright nur im CI (nicht im Programm), falscher Aufruf endet sauber",
           {(s, e) for s in ("A", "B1", "B2") for e in ("chromium", "firefox", "webkit")} <= stufen and len(m.ABLAEUFE) >= 15
           and all(w <= 30 for w in warten) and m.ZEIT_GESAMT <= 28 * 60 and not schluessel and not imp
           and "playwright" not in req.lower() and falsch.returncode != 0 and "Traceback" not in falsch.stderr
           and m.UNTERORDNER == "/me-goos-ta-deutsch/", f"{sorted(stufen)} {warten} {schluessel} {imp} {falsch.stderr[-200:]}")
    # 2) release_pruefung.yml statisch
    y = woche.read_text(encoding="utf-8")
    uses = re.findall(r"^\s*-?\s*uses:\s*(\S+)", y, re.M)
    jobs = re.findall(r"^  ([a-z][a-z0-9_-]*):\s*$", y.split("\njobs:", 1)[1], re.M) if "\njobs:" in y else []
    zeiten = [int(z) for z in re.findall(r"^\s+timeout-minutes:\s*(\d+)", y, re.M)]
    pruefe("release_pruefung.yml: beim Veröffentlichen eines Releases + workflow_dispatch (kein Push, kein Zeitplan, kein "
           "pull_request), nur Lesen, Actions per SHA, Prüfsummen-Schritt wartet beim Release auf das passende Release (--passend), Frischtest mit dem "
           "veröffentlichten Release auf 7 Systemen, Job „neueste“ (Spannen statt Lock) auf 3 Systemen, Browser live, "
           "Playwright-Download mit Wiederholung",
           re.search(r'^on:\n  release:\n    types: \[published\]\n  workflow_dispatch:\n\n', y, re.M)
           and "schedule" not in y and "cron" not in y and "pull_request" not in y and "push:" not in y
           and "${{ github.event_name == 'release' && '--passend 40' || '' }}" in y
           and y.count("for i in 1 2 3; do python -m playwright install") == 1
           and re.search(r"^permissions:\n  contents: read\n", y, re.M)
           and "write" not in y and "secrets." not in y and uses and all(re.fullmatch(r"actions/[a-z-]+@[0-9a-f]{40}", u) for u in uses)
           and re.search(r"name: Prüfsumme[^\n]*SHA256SUMS[^\n]*\n\s+run: python \.github/ci/neuestes_release\.py", y)
           and y.count("frischtest.py --neuestes-release") == 3 and "browser_test.py --live --neuestes-release" in y
           and y.count("--neuestes-release --neueste-pakete") == 1 and y.count("name: neueste-") == 3
           and all(s in y for s in ("windows-latest", "windows-11-arm", "os: macos-15 }", "macos-15-intel", "ubuntu-latest",
                                    "ubuntu-24.04-arm", "debian:stable-slim")) and "os: macos-14" not in y
           and len(jobs) == 5 and "neueste" in jobs and len(zeiten) == len(jobs) and all(0 < z <= 45 for z in zeiten)
           and y.count("persist-credentials: false") == len(jobs) and y.count("needs: release") == 4, f"{jobs} {zeiten} {uses[:2]}")
    # 3) tests.yml: Browser-Job
    t2 = wf.read_text(encoding="utf-8")
    job = t2.split("\n  browser:\n", 1)[1] if "\n  browser:\n" in t2 else ""
    pruefe("tests.yml: Job browser (Ubuntu: Chromium, Firefox, WebKit · macOS: WebKit), Playwright fest 1.63.0, Ergebnis als Artefakt",
           "browser-linux, os: ubuntu-latest, engines: \"chromium,firefox,webkit\"" in job
           and "browser-macos, os: macos-15-intel, engines: \"webkit\"" in job and "playwright==1.63.0" in job
           and "python baum/.github/ci/browser_test.py --system ${{ matrix.name }}" in job and "name: ergebnis-${{ matrix.name }}" in job
           and "--live" not in job and "for i in 1 2 3; do python -m playwright install" in job, job[:200])
    # 4) ci_lauf.py: web-app/ im Branch ci; --release-pruefung nur die Release-Prüfung mit push-Auslöser auf ci
    cl = modul(ci_lauf, "ci_lauf_e39")
    pr = lauf(ci_lauf, HIER.parent, "--probe")
    mp = re.search(r"^#plan (.*)$", pr.stdout, re.M)
    plan = json.loads(mp.group(1)) if mp else {}
    rel = tmp / "e39-rel"
    subprocess.run([sys.executable, str(rel_bau), str(HIER.parent), str(rel)], env=env, capture_output=True, timeout=300)
    subprocess.run([sys.executable, str(rel_bau), str(HIER.parent), str(rel), "--zip"], env=env, capture_output=True, timeout=300)
    ordner = rel / HIER.parent.name
    zips = sorted(rel.glob("Me-Goos-ta-Deutsch-*.zip"))
    w = tmp / "e39-woche"
    liste = cl.branch_inhalt(ordner, w, release_pruefung=True) if ordner.is_dir() else []
    wy = (w / ".github" / "workflows" / "release_pruefung.yml").read_text(encoding="utf-8") if liste else ""
    pruefe("ci_lauf.py: Branch ci mit web-app/ (Handy-App + Download-Seite); --release-pruefung: nur release_pruefung.yml, "
           "Auslöser push auf ci statt auf main, ohne web-app/",
           pr.returncode == 0 and plan.get("web_app", 0) >= 10 and plan.get("release_pruefung") is False
           and ".github/ci/browser_test.py" in plan.get("github", []) and liste
           and not (w / ".github" / "workflows" / "tests.yml").exists() and not (w / "web-app").exists()
           and wy.startswith(y.split("\non:", 1)[0]) and cl.RP_PROBE in wy and cl.RP_AUSLOESER not in wy
           and "branches: [main]" not in wy,
           f"{(pr.stdout + pr.stderr)[-300:]} · {len(liste)}")
    # 5) veroeffentliche_release.py --probe: CI-Schranke
    vrm = modul(vr, "veroeffentliche_release_e39")
    summe = cl.inhalt_pruefsumme(ordner) if ordner.is_dir() else ""
    version = re.search(r'^VERSION = "([\d.]+)', (HIER / "gans_lernkarten.py").read_text(encoding="utf-8"), re.M)[1]
    gruen = dict(version=version, pruefsumme=summe, ok=True, lauf="https://example.invalid/lauf", zeit="jetzt",
                 systeme={"linux-x64": {"ok": True}, "browser-linux": {"ok": True}})
    (tmp / "e39-gruen.json").write_text(json.dumps(gruen), encoding="utf-8")
    (tmp / "e39-anders.json").write_text(json.dumps(dict(gruen, pruefsumme="0" * 64)), encoding="utf-8")
    (tmp / "e39-rot.json").write_text(json.dumps(dict(gruen, ok=False)), encoding="utf-8")
    (ordner / ".github").mkdir(exist_ok=True)
    (ordner / ".github" / "zufall.txt").write_text("liegt nur im Ordner", encoding="utf-8")   # Ordner = ZIP trotz .github/
    z = zips[0] if zips else tmp / "fehlt.zip"
    ohne, anders, rot, gut = (lauf(vr, ordner, z, "--probe", "--ci-ergebnis", tmp / n) for n in
                              ("e39-fehlt.json", "e39-anders.json", "e39-rot.json", "e39-gruen.json"))
    mg = re.search(r"^#plan (.*)$", gut.stdout, re.M)
    pg = json.loads(mg.group(1)) if mg else {}
    pruefe("veroeffentliche_release.py --probe: ohne / roter / fremder CI-Lauf → Abbruch vor dem Plan; grün für genau diesen "
           "Inhalt → Plan mit .github/ (Workflows), Ordner = ZIP trotz .github/ im Ordner",
           all(x.returncode != 0 and "CI-Schranke" in x.stderr and "#plan" not in x.stdout for x in (ohne, anders, rot))
           and gut.returncode == 0 and ".github/workflows/release_pruefung.yml" in pg.get("github", [])
           and ".github/ci/browser_test.py" in pg.get("github", []) and pg.get("ci", {}).get("pruefsumme") == summe
           and "zufall.txt" not in gut.stdout, (ohne.stderr + anders.stderr + rot.stderr + gut.stderr)[-400:])
    leer = lauf(vr, ordner, z, "--probe", "--ci-ergebnis", tmp / "e39-fehlt.json", "--ohne-ci", "kurz")
    grund = "GitHub Actions gestört, e39 geprüft"
    mit = lauf(vr, ordner, z, "--probe", "--ci-ergebnis", tmp / "e39-fehlt.json", "--ohne-ci", grund)
    notizen = mit.stdout.split("--- Release-Notizen ---", 1)[1] if "--- Release-Notizen ---" in mit.stdout else "?"
    pruefe("veroeffentliche_release.py --ohne-ci: ohne echte Begründung Abbruch; mit Begründung im Protokoll (Achtung + #plan), "
           "nie in den Release-Notizen",
           leer.returncode != 0 and "Begründung" in leer.stderr and mit.returncode == 0 and f"Achtung: Release ohne grünen CI-Lauf – Begründung: {grund}" in mit.stdout
           and grund in (re.search(r"^#plan (.*)$", mit.stdout, re.M) or [""])[0] and grund not in notizen and "Warnung" not in mit.stdout,
           (leer.stderr + mit.stderr)[-300:])
    # 6) gleiche Prüfsumme in beiden Skripten; neuestes_release.py ohne Netz
    shutil.rmtree(ordner / ".github", ignore_errors=True)
    nrl = lauf(nr, "--ziel", tmp / "e39-neu", "--repo", "beispiel/repo")
    pruefe("Inhalts-Prüfsumme: veroeffentliche_release.py = ci_lauf.py; neuestes_release.py ohne Netz → sauber „nicht geladen“ (Exit 1)",
           bool(summe) and vrm.inhalt_pruefsumme(ordner, vrm.dateien(ordner)) == summe and nrl.returncode == 1
           and "nicht geladen" in nrl.stdout and "Traceback" not in nrl.stderr, nrl.stdout[-200:] + nrl.stderr[-200:])


def test_aussprache(tmp):
    """E40 (2.2): Deutsche Aussprache beim Lernen – 🔊 neben dem deutschen Text erst nach dem Aufdecken, nur mit lokaler
    de-Stimme (de-DE → de-AT → de-CH → andere de), gemeinsamer Weg vorlesen(), Beenden bricht ab; Lernseite ebenso (Stimme
    beim Laden + voiceschanged, Knopf nur umgedreht); keine neue Taste, kein {{tts}} im Anki-Paket. Den Klick mit
    nachgebildeter speechSynthesis prüft browser_test.py (B1, alle Engines)."""
    print("\n[E40] Deutsche Aussprache beim Lernen")
    ui = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    i = ui.index("function lernStimme(code)")
    stimme = ui[i:ui.index("\n}\n", i)]
    j = ui.index("function lernKarteHTML(k)")
    karte = ui[j:ui.index("\n}\n", j)]
    k = ui.index('$("#lern-inhalt").addEventListener("click"')
    klick = ui[k:ui.index("\n});\n", k)]
    pruefe("Stimme für Deutsch: nur lokal (localService), Reihenfolge de-DE → de-AT → de-CH → andere de",
           stimme.count("localService !== false") == 2 and '["de-de", "de-at", "de-ch"]' in stimme
           and 'ziel.includes(lang(v).split("-")[0])' in stimme, stimme[:200])
    pruefe("🔊 Deutsch nur nach dem Aufdecken (beide Richtungen), nur mit Stimme, mit aria-label; Text bleibt lang=\"de\"",
           karte.count('data-ln="vorlesen-de"') == 1 and 'LS.gezeigt && k.de && lernStimme("de") ?' in karte
           and 'aria-label="${esc(t("h_ln_vorlesen_de"))}"' in karte and '<span lang="de">${esc(k.de)}</span>' in karte
           and karte.count("${deZeile}") == 2 and "deZeile" not in karte.split("const vorn", 1)[1].split("\n", 1)[0])
    pruefe("Klick liest genau den deutschen Text über vorlesen() (cancel, Stimme, lang); Beenden ruft cancel",
           'if (a === "vorlesen-de" && LS && LS.n.karte && LS.gezeigt) { vorlesen(LS.n.karte.de, lernStimme("de")); return; }' in klick
           and "vorlesen(k.wort, lernStimme(k.sprache))" in klick and "speechSynthesis.cancel(); const s = new SpeechSynthesisUtterance(text); s.voice = stimme; s.lang = stimme.lang;" in ui
           and "function lernBeenden() { LS = null; if (window.speechSynthesis) speechSynthesis.cancel();" in ui)
    import lernkarten_digital as ld
    ls = ld.LERNSEITE
    pruefe("Lernseite: Stimme beim Laden + voiceschanged, nur lokal, Knopf nur umgedreht und mit Stimme, Texte de/en/es",
           "function deStimme()" in ls and "localService !== false" in ls and 'speechSynthesis.addEventListener("voiceschanged"' in ls
           and '$("sprechen").hidden = !(stimme && aktuell && umgedreht());' in ls and "if (!aktuell || !stimme || !umgedreht()) return;" in ls
           and 'u.lang = "de-DE"' not in ls and all("Deutsch" in ld.LERNSEITE_TEXTE[s]["vorlesen"] or "German" in ld.LERNSEITE_TEXTE[s]["vorlesen"]
                                                     or "alemán" in ld.LERNSEITE_TEXTE[s]["vorlesen"] for s in ("de", "en", "es")))
    tasten = re.search(r'ln_tasten: "([^"]*)"', ui)
    pruefe("Keine neue Taste (Belegung 1–4/Leertaste/Strg+Z/Esc unverändert), kein {{tts}} im Anki-Paket, Hover-Text in de/en/es",
           tasten and "1" in tasten.group(1) and "{{tts" not in (HIER / "lernkarten_digital.py").read_text(encoding="utf-8")
           and ui.count("h_ln_vorlesen_de:") == 3 and "vorlesen-de" not in ui[ui.index('document.addEventListener("keydown"'):][:4000])


E41_PROZESS = r"""
import json, os, socket, sys, urllib.error, urllib.request
from pathlib import Path
sys.path.insert(0, sys.argv[1])
os.environ.pop("MGD_IM_PROZESS", None)
p, port = Path(sys.argv[1]), int(sys.argv[2])
netz = []                                           # jeder Versuch, einen fremden Rechner zu erreichen
LOKAL = {"127.0.0.1", "localhost", "::1", None}
_gai, _conn = socket.getaddrinfo, socket.socket.connect
def gai(host, *a, **k):
    if host not in LOKAL:
        netz.append(("dns", host))
    return _gai(host, *a, **k)
def conn(self, adr):
    if isinstance(adr, tuple) and adr[0] not in LOKAL:
        netz.append(("connect", adr[0]))
    return _conn(self, adr)
socket.getaddrinfo, socket.socket.connect = gai, conn
import gans_ui as ui, gans_lernkarten as gl, uebersetzer as ue
e = {}
abrufe = []
SZ = {"f": None}
class Antwort:
    def __init__(s, roh, art):
        s.roh, s.headers = roh, {"Content-Type": art}
    def read(s, n=-1):
        return s.roh[:n] if n >= 0 else s.roh
    def __enter__(s):
        return s
    def __exit__(s, *a):
        return False
class Oeffner:
    def __init__(s, handler):
        s.handler = handler
    def open(s, anfrage, timeout=None):
        abrufe.append(dict(url=anfrage.full_url, methode=anfrage.get_method(), timeout=timeout, daten=anfrage.data,
                           weiter=any(isinstance(h, ue._KeineWeiterleitung) for h in s.handler),
                           kopf={k.lower(): v for k, v in anfrage.header_items()}))
        return SZ["f"](anfrage)
echter_oeffner = urllib.request.build_opener
ue.urllib.request.build_opener = lambda *h: Oeffner(h)
def j(d):
    return lambda a: Antwort(json.dumps(d).encode(), "application/json; charset=utf-8")
def fehler(code):
    def f(a):
        raise urllib.error.HTTPError(a.full_url, code, "x", {}, None)
    return f
def wirf(x):
    def f(a):
        raise x
    return f
def umleiten(a):
    ue._KeineWeiterleitung().redirect_request(a, None, 302, "", {}, "https://evil.example/")
def direkt(methode, weg, koerper=b"{}", am_handy=False):
    s, k, i = ui.verarbeite(methode, weg, "", koerper, {"X-GL-Sprache": "de", "Content-Type": "application/json"}, am_handy=am_handy)
    try:
        return s, json.loads(i)
    except ValueError:
        return s, {}
gl.setze_sprache("de")
wa = p / "web_adresse.txt"
wa.write_text("https://lukasdiegans.github.io/me-goos-ta-deutsch/" + chr(10), encoding="utf-8")
def frage(f):
    SZ["f"] = f
    return direkt("POST", "/api/neue-version")
eigene = gl.VERSION.split()[0]
alt_version = gl.VERSION
v = [int(x) for x in eigene.split(".")]
hoeher, tiefer = f"v{v[0]}.{v[1] + 1}", f"{v[0]}.{max(0, v[1] - 1)}" if v[1] else f"{v[0] - 1}.9"
r = {}
r["neuer"] = frage(j({"tag_name": hoeher, "published_at": "2026-11-02T10:00:00Z", "html_url": "https://evil.example/",
                      "body": "<script>x</script>", "assets": [{"browser_download_url": "https://evil.example/x.zip"}]}))
r["gleich"] = frage(j({"tag_name": eigene, "published_at": "2026-10-20T08:00:00Z"}))
r["gleich_v"] = frage(j({"tag_name": "v" + eigene}))
r["aelter"] = frage(j({"tag_name": tiefer, "published_at": "javascript:alert(1)"}))
anfrage = abrufe[0] if abrufe else {}
gl.VERSION = "2.9 (1.1.2027)"
r["zehn"] = frage(j({"tag_name": "v2.10"}))
gl.VERSION = alt_version
for n, tag in (("latest", "latest"), ("v2", "v2"), ("html", "<b>2.3</b>"), ("leer", None)):
    r["tag_" + n] = frage(j({"tag_name": tag}))
r["html_antwort"] = frage(lambda a: Antwort(b"<html>2.9</html>", "text/html"))
r["gross"] = frage(lambda a: Antwort(json.dumps({"tag_name": "v9.9", "x": "a" * 200_001}).encode(), "application/json"))
r["kein_dict"] = frage(lambda a: Antwort(b"[1, 2]", "application/json"))
for n, f in (("403", fehler(403)), ("429", fehler(429)), ("404", fehler(404)), ("500", fehler(500)),
             ("zeit", wirf(TimeoutError("timed out"))), ("netz", wirf(urllib.error.URLError(OSError("getaddrinfo failed")))),
             ("umleitung", umleiten)):
    r[n] = frage(f)
e["r"] = {k: [s, d.get("ergebnis"), d.get("code"), d.get("version"), d.get("datum"), sorted(d)] for k, (s, d) in r.items()}
e["anfrage"] = anfrage
e["meldungen"] = {k: d.get("meldung") or d.get("fehler") for k, (s, d) in r.items()}
# manipulierte web_adresse.txt → keine Anfrage
vorher = len(abrufe)
falsch = []
for zeile in ("https://evil.example/me-goos-ta-deutsch/", "https://gans.github.io/../", "http://gans.github.io/repo/",
              "https://gans.github.io/repo/?x=1", "https://gans.github.io.evil.example/repo/", "javascript:alert(1)", ""):
    wa.write_text(zeile, encoding="utf-8")
    falsch.append(frage(j({"tag_name": "v9.9"})))
e["falsch"] = [[s, d.get("code")] for s, d in falsch] + [len(abrufe) - vorher]
wa.write_text("https://lukasdiegans.github.io/me-goos-ta-deutsch/", encoding="utf-8")
# Host-Sperre: Übersetzung nicht an api.github.com, Versionsprüfung nur dort
sperre = []
for url, hosts in (("https://api.github.com/repos/a/b/releases/latest", None), ("https://de.wiktionary.org/w/api.php", ("api.github.com",)),
                   ("https://api.mymemory.translated.net/get", ("api.github.com",)), ("http://api.github.com/x", ("api.github.com",))):
    try:
        ue.pruefe_adresse(url, hosts)
        sperre.append(False)
    except ue.UebersetzungsFehler:
        sperre.append(True)
sperre.append(ue.pruefe_adresse("https://api.github.com/repos/a/b/releases/latest", ("api.github.com",)) == "api.github.com")
sperre.append("api.github.com" in ue.ERLAUBTE_HOSTS)
e["sperre"] = sperre
# Handy-Zugang und Web-App: 403
vorher = len(abrufe)
SZ["f"] = j({"tag_name": "v9.9"})
h = direkt("POST", "/api/neue-version", am_handy=True)
ui.im_browser = lambda: True
w = direkt("POST", "/api/neue-version")
ui.im_browser = lambda: False
e["handy"] = [h[0], w[0], ui.tx("nur_rechner") == w[1].get("fehler"), len(abrufe) - vorher]
# kein automatischer Abruf: Server starten und alles laden, was die Seite beim Start und in Hilfe/Über lädt
netz.clear()
ui.starte(port, browser=False)
oeffner = echter_oeffner(urllib.request.ProxyHandler({}))
codes = []
vorher = len(abrufe)
for weg in ("/", "/api/status", "/api/karten", "/api/ideen", "/api/werkzeuge", "/api/tools", "/api/hilfe?doc=leitfaden",
            "/api/hilfe?doc=spec", "/api/status"):
    a = urllib.request.Request(f"http://127.0.0.1:{ui.PORT}{weg}", headers={"Cookie": f"mgd_{ui.PORT}={ui.TOKEN}", "X-GL-Token": ui.TOKEN})
    try:
        with oeffner.open(a, timeout=60) as x:
            codes.append(x.status)
    except urllib.error.HTTPError as f:
        codes.append(f.code)
e["start"] = [codes, len(abrufe) - vorher, list(netz)]
wa.unlink()
print("#e41 " + json.dumps(e, ensure_ascii=False, default=str))
"""


def test_neue_version(p, tmp):
    """E41 (2.2): Nach neuer Version suchen – Antworten von GitHub nachgebildet (neuer/gleich/älter, v-Präfix, 2.10 > 2.9,
    kaputte Tags, zu groß, falscher Inhaltstyp, 403/429, 404, Zeitlimit, Weiterleitung), manipulierte web_adresse.txt →
    keine Anfrage, getrennte Host-Listen, Handy/Web-App 403, kein automatischer Abruf (Server mit Netz-Mitschnitt), statisch:
    die Adresse genau einmal in der Seite und nur im Klick-Handler, api.github.com nur in gans_ui.neue_version()."""
    print("\n[E41] Nach neuer Version suchen (nur auf Klick)")
    daten = tmp / "daten-e41"
    daten.mkdir()
    env = dict(os.environ, PYTHONIOENCODING="utf-8", MGD_DATEN=str(daten), MGD_START_ID="test")
    env.pop("MGD_IM_PROZESS", None)
    r = subprocess.run([sys.executable, "-c", E41_PROZESS, str(p), str(tg._freier_port())], cwd=p, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    m = re.search(r"^#e41 (.*)$", r.stdout, re.M)
    e = json.loads(m.group(1)) if m else {}
    if not m:
        print((r.stdout + r.stderr)[-2000:])
    x = e.get("r") or {}
    ok = ["datum", "eigene", "ergebnis", "version"]
    pruefe("Neuer / gleich (mit und ohne v) / älter: neuer · aktuell · voraus; nur Version + Datum aus der Antwort (keine Links, kein Text)",
           (x.get("neuer") or [0])[:2] == [200, "neuer"] and x["neuer"][4] == "2026-11-02" and x["neuer"][5] == ok
           and x.get("gleich", [0])[1] == "aktuell" and x.get("gleich_v", [0])[1] == "aktuell"
           and x.get("aelter", [0])[1] == "voraus" and x["aelter"][4] == "" and "evil" not in json.dumps(e.get("r")), str(x)[:600])
    pruefe("Versionen als Zahlen: 2.10 ist neuer als 2.9", (x.get("zehn") or [0, 0, 0, 0])[1:4] == ["neuer", None, "2.10"], str(x.get("zehn")))
    kaputt = ["tag_latest", "tag_v2", "tag_html", "tag_leer", "html_antwort", "gross", "kein_dict", "500", "umleitung"]
    pruefe("Kaputter Tag (latest, v2, HTML, fehlt), HTML-Antwort, zu groß (> 200 KB), kein Objekt, 500, Weiterleitung → freundlich „unerwartet“",
           all((x.get(n) or [0])[:3] == [200, "fehler", "nv_format"] for n in kaputt), str({n: x.get(n) for n in kaputt})[:600])
    me = e.get("meldungen") or {}
    pruefe("403/429 → Abfrage-Grenze („in einer Stunde“), 404 → noch kein Release, Zeitlimit, offline – Texte positiv, nie „Warnung“",
           [(x.get(n) or [0, 0, 0])[2] for n in ("403", "429", "404", "zeit", "netz")] == ["nv_grenze", "nv_grenze", "nv_noch_keins", "nv_zeit", "nv_netz"]
           and "Stunde" in (me.get("403") or "") and all(me.get(n) and "Warnung" not in me[n] for n in ("403", "404", "zeit", "netz")), str(me)[:400])
    a = e.get("anfrage") or {}
    pruefe("Anfrage: GET https://api.github.com/repos/<konto>/<repo>/releases/latest aus web_adresse.txt, ohne Daten/Cookie, 10 s, "
           "ohne Weiterleitung",
           a.get("url") == "https://api.github.com/repos/lukasdiegans/me-goos-ta-deutsch/releases/latest" and a.get("methode") == "GET"
           and a.get("daten") is None and a.get("timeout") == 10 and a.get("weiter") is True
           and "cookie" not in (a.get("kopf") or {}) and "Me-Goos-ta-Deutsch" in (a.get("kopf") or {}).get("user-agent", ""), str(a)[:300])
    f = e.get("falsch") or []
    pruefe("Manipulierte oder fehlende web_adresse.txt → 409 kein_release, keine einzige Anfrage",
           len(f) == 8 and all(z == [409, "kein_release"] for z in f[:7]) and f[7] == 0, str(f))
    pruefe("Host-Listen getrennt: Übersetzung kommt nicht an api.github.com, Versionsprüfung an keinen anderen Host, nur HTTPS",
           e.get("sperre") == [True, True, True, True, True, False], str(e.get("sperre")))
    pruefe("Über den Handy-Zugang und in der Web-App gesperrt (403 nur_rechner), ohne Anfrage",
           e.get("handy") == [403, 403, True, 0], str(e.get("handy")))
    st = e.get("start") or [[], -1, ["?"]]
    pruefe("Kein automatischer Abruf: Start, Seite, Status, Karten, Ideen, Werkzeuge, Tools, Hilfe → 0 Anfragen ins Netz",
           len(st[0]) == 9 and st[0][0] == 200 and st[1] == 0 and st[2] == [], str(st)[:400])
    ui = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    i = ui.find("async function sucheNeueVersion(b) {")             # seit 2.4: Werkzeuge, Über und Fußzeile teilen sie
    handler = ui[i:ui.index("\n}\n", i)] if i >= 0 else ""
    fremd = {}
    for d in HIER.glob("*.py"):
        if d.name.startswith("test_"):
            continue
        q = d.read_text(encoding="utf-8")
        if "api.github.com" in q:
            fremd[d.name] = q.count("api.github.com")
    g = (HIER / "gans_ui.py").read_text(encoding="utf-8")
    k = g.find("def neue_version(")
    fn = g[k:g.index("\n\n\n", k)] if k >= 0 else ""
    pruefe("Statisch: /api/neue-version genau einmal in der Seite, nur im Klick-Handler (nicht am Handy/in der App); "
           "api.github.com nur in gans_ui.neue_version()",
           ui.count("/api/neue-version") == 1 and "/api/neue-version" in handler and "AM_HANDY || AM_APP" in handler
           and "setInterval" not in handler and "setTimeout" not in handler
           and list(fremd) == ["gans_ui.py"] and fremd["gans_ui.py"] == fn.count("api.github.com") >= 1
           and "!AM_HANDY && !AM_APP ?" in ui, str(fremd))


E42_PROZESS = r'''
import json, os, random, sys, threading, time, unicodedata, urllib.error, urllib.request
from pathlib import Path
sys.path.insert(0, sys.argv[1])
os.environ.pop("MGD_IM_PROZESS", None)
p, tmp, port = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3])
import gans_ui as ui, gans_lernkarten as gl, erweiterungen as erw
gl.setze_sprache("de")
erw.IDEEN_DATEI, erw.IDEEN_ORDNER = tmp / "ideen.json", tmp / "ideen"      # eigene Ideen, nichts im Programmordner
E = []
def ok(name, gut, detail=""):
    E.append([name, bool(gut), str(detail)[:700]])
def lies(roh, **o):
    try:
        return erw.wortliste_lesen(roh, o)
    except erw.WortlisteFehler as f:
        return {"fehler": f.code, "text": str(f)}
def zl(r):
    return [(z["nr"], z["de"], z["wort"], z["notiz"], z["status"]) for z in r.get("zeilen", [])]
def paare(r):
    return [(z["de"], z["wort"]) for z in r.get("zeilen", [])]
# ---------- Stufe 1–2: Dateiart und Kodierung ----------
text = "müde;cansado\nalt;viejo"
soll = [("Gans müde", "cansado"), ("Gans alt", "viejo")]
faelle = [("utf-8", text.encode()), ("utf-8", b"\xef\xbb\xbf" + text.encode()), ("utf-16-le", b"\xff\xfe" + text.encode("utf-16-le")),
          ("utf-16-be", b"\xfe\xff" + text.encode("utf-16-be")), ("utf-16-le", text.encode("utf-16-le")), ("utf-16-be", text.encode("utf-16-be"))]
erg = [(k, lies(b)) for k, b in faelle]
ok("Kodierung: UTF-8 mit/ohne BOM, UTF-16 LE/BE mit BOM (Excel „Unicode-Text“) und ohne BOM → gleiche Wörter",
   all(paare(r) == soll and r["erkannt"]["kodierung"] == k and not r["hinweise"] for k, r in erg), [(k, r.get("erkannt"), paare(r)) for k, r in erg])
r = lies("Müdigkeit;cansancio\nniño;Kind".encode("cp1252"))
ok("Windows-1252 („Müdigkeit;cansancio“, „ñ“) → richtig gelesen + freundlicher Hinweis oben",
   paare(r) == [("Gans Müdigkeit", "cansancio"), ("Gans niño", "Kind")] and r["erkannt"]["kodierung"] == "cp1252"
   and len(r["hinweise"]) == 1 and "Windows-1252" in r["hinweise"][0], r)
arten = {n: lies(b) for n, b in (("xlsx", b"PK\x03\x04\x14\x00rest"), ("pdf", b"%PDF-1.7\n..."), ("png", b"\x89PNG\r\n\x1a\nxx"),
                                  ("jpg", b"\xff\xd8\xff\xe0xx"), ("xls", b"\xd0\xcf\x11\xe0\xa1\xb1"), ("rtf", b"{\\rtf1 alt"),
                                  ("webp", b"RIFF1234WEBPVP8 "))}
ok("Excel/ZIP, PDF, PNG, JPG, altes Excel/Word, RTF, WEBP → „bitte als CSV UTF-8 oder Text speichern“ (nichts angelegt)",
   all(r.get("fehler") == "wl_dateiart" and "CSV UTF-8" in r["text"] for r in arten.values()), arten)
binaer = lies(bytes(range(256)) * 4)
ok("Binärdaten mit NUL-Bytes, leere Datei, nur Leerzeilen → kein lesbarer Text bzw. „noch leer“",
   binaer.get("fehler") == "wl_unlesbar" and lies(b"").get("fehler") == "wl_leer" and lies(b" \n\r\n\t\n").get("fehler") == "wl_leer"
   and lies(b"\xef\xbb\xbf").get("fehler") == "wl_leer" and lies("# nur Kommentar".encode()).get("fehler") == "wl_leer", binaer)
# ---------- Stufe 3–4: Bereinigen, Zeilen ----------
r = lies("Müde;cansado\nmüde;otro".encode())
ok("NFD (macOS) → NFC: „Müde“ wird zusammengesetzt und als doppelt zu „müde“ erkannt",
   r["zeilen"][0]["de"] == "Gans Müde" and unicodedata.is_normalized("NFC", r["zeilen"][0]["de"]) and r["zeilen"][1]["status"] == "doppelt_liste", zl(r))
r = lies("alt;viejo\r\nmüde;cansado\rneu;nuevo rot;rojo\u0085blau;azul\ngrün;verde".encode())
ok("Zeilenenden CRLF, CR, LF, U+2028, NEL → 6 Zeilen mit den Zeilennummern der Datei",
   [z[0] for z in zl(r)] == [1, 2, 3, 4, 5, 6] and paare(r)[5] == ("Gans grün", "verde"), zl(r))
r = lies("alt ; vie​jo\nmü­de;can⁠sado　\n﻿rot;ro\x07jo".encode())
ok("Geschützte Leerzeichen, Nullbreiten, weiches Trennzeichen, BOM mitten im Text, Steuerzeichen → saubere Wörter",
   paare(r) == [("Gans alt", "viejo"), ("Gans müde", "cansado"), ("Gans rot", "rojo")], paare(r))
r = lies("# Farben\n- alt\n* müde\n• rot\n– blau\n1. grün\n2) gelb\n\n-los".encode())
ok("Kommentare (#) gezählt, Listenzeichen (- * • – 1. 2)) entfernt, „-los“ bleibt (Formel-Schutz statt still „los“)",
   [z[1] for z in zl(r)][:6] == ["Gans alt", "Gans müde", "Gans rot", "Gans blau", "Gans grün", "Gans gelb"]
   and zl(r)[6][4] == "fehler" and "Gans -los" == zl(r)[6][1] and r["zahlen"]["kommentare"] == 1 and r["zahlen"]["leer"] == 1
   and [z[0] for z in zl(r)] == [2, 3, 4, 5, 6, 7, 9], zl(r))
# ---------- Stufe 5: Trennzeichen ----------
tr = {n: lies(b) for n, b in (("tab", "alt\tviejo\nmüde\tcansado".encode()), ("semikolon", "alt;viejo\nmüde;cansado".encode()),
                               ("komma", 'alt,"viejo, anciano"\nmüde,cansado'.encode()), ("gleich", "alt = viejo\nmüde = cansado".encode()),
                               ("strich", "alt - viejo\nmüde – cansado".encode()), ("keiner", "alt\nmüde".encode()))}
ok("Trenner automatisch: Tab, Semikolon, Komma mit Anführungszeichen, „ = “, „ - “/„ – “, keiner (einspaltig)",
   all(r["erkannt"]["trenner"] == n for n, r in tr.items()) and paare(tr["komma"])[0] == ("Gans alt", "viejo, anciano")
   and paare(tr["strich"]) == [("Gans alt", "viejo"), ("Gans müde", "cansado")] and paare(tr["keiner"])[0] == ("Gans alt", ""),
   {n: (r.get("erkannt", {}).get("trenner"), paare(r)) for n, r in tr.items()})
r1 = lies("Rot-Weiß;rojo y blanco\nalt;viejo".encode())
r2 = lies("alt,viejo,anciano\nmüde,cansado".encode())
r3 = lies("alt;viejo;;\nmüde;cansado;".encode())
r4 = lies("alt;viejo\nmüde;cansado".encode(), trenner="keiner")
ok("„Rot-Weiß“ wird nicht am Strich geteilt; Komma mit 3 Spalten → Hinweis „Alternative?“; leere Zellen am Ende weg; Wahl „keiner“ gilt",
   paare(r1)[0] == ("Gans Rot-Weiß", "rojo y blanco") and r2["hinweise"] and "Alternative" in r2["hinweise"][0]
   and zl(r2)[0][3] == "anciano" and paare(r3) == [("Gans alt", "viejo"), ("Gans müde", "cansado")]
   and paare(r4)[0] == ("Gans alt;viejo", ""), (paare(r1), r2["hinweise"], paare(r3), paare(r4)))
# ---------- Stufe 6–7: Kopfzeile, Spalten ----------
k1 = lies("Deutsch;Spanisch\nalt;viejo".encode())
k2 = lies("Spanish;German\nviejo;alt".encode())
k3 = lies("Haus;casa\nalt;viejo".encode())
k4 = lies("Haus;casa\nalt;viejo".encode(), kopf="ja")
k5 = lies("Deutsch;Spanisch\nalt;viejo".encode(), kopf="nein")
k6 = lies("alemán;español;nota\nalt;viejo;ojo".encode())
ok("Kopfzeile: „Deutsch;Spanisch“ erkannt, „Spanish;German“ → getauscht, unbekannter Kopf = Wort, Schalter ja/nein, es-Namen + Notiz",
   k1["erkannt"]["kopf"] and zl(k1) == [(2, "Gans alt", "viejo", "", "neu")] and k2["erkannt"]["getauscht"]
   and paare(k2) == [("Gans alt", "viejo")] and not k3["erkannt"]["kopf"] and len(k3["zeilen"]) == 2
   and paare(k4) == [("Gans alt", "viejo")] and len(k5["zeilen"]) == 2 and zl(k6) == [(2, "Gans alt", "viejo", "ojo", "neu")],
   [zl(k) for k in (k1, k2, k3, k4, k5, k6)])
k7 = lies("Deutsch;Französisch\nalt;vieux".encode())
k8 = lies("Deutsch;Russisch\nalt;старый".encode(), zs="ru")
ok("Kopf nennt eine andere Sprache als die Kartensprache → Hinweis oben (Spalte gilt als Kartensprache), passende Sprache → kein Hinweis",
   k7["erkannt"]["kopf_sprache"] == "fr" and "Französisch" in k7["hinweise"][0] and paare(k7) == [("Gans alt", "vieux")]
   and not k8["hinweise"] and paare(k8) == [("Gans alt", "старый")], (k7["hinweise"], k8["hinweise"]))
e1 = lies("alt\nmüde".encode())
e2 = lies("viejo\ncansado".encode(), einspaltig="zs")
e3 = lies("alt;viejo;Notiz".encode())
e4 = lies("alt;viejo;Notiz;mehr".encode())
e5 = lies("viejo;alt".encode(), tauschen="1")
ok("Einspaltig Deutsch / einspaltig Kartensprache, 3 Spalten = Notiz, 4 Spalten → Zeile fehlerhaft („/“), „tauschen“ tauscht",
   paare(e1) == [("Gans alt", ""), ("Gans müde", "")] and paare(e2) == [("", "viejo"), ("", "cansado")]
   and zl(e3) == [(1, "Gans alt", "viejo", "Notiz", "neu")] and e4["zeilen"][0]["status"] == "fehler" and "/" in e4["zeilen"][0]["text"]
   and not e4["zeilen"][0]["wahl"] and paare(e5) == [("Gans alt", "viejo")], [zl(e) for e in (e1, e2, e3, e4, e5)])
# ---------- Stufe 8–10: Felder, „Gans“, Prüfen ----------
r = lies("„alt“;«viejo»\n\"müde\";'cansado'\n  viel    zu   weit ; muy   lejos ".encode())
ok("Typografische Anführungszeichen außen weg, Leerraum zusammengefasst; „/“ und „|“ bleiben",
   paare(r) == [("Gans alt", "viejo"), ("Gans müde", "cansado"), ("Gans viel zu weit", "muy lejos")]
   and paare(lies("alt;viejo / anciano | x".encode()))[0][1] == "viejo / anciano | x", paare(r))
r = lies("Gans;x\nganz alt;viejo\nGANS müde;cansado\nGans  rot;rojo\nblau;azul".encode())
r0 = lies("alt;viejo\nGans müde;cansado".encode(), gans="0")
ok("„Gans“ davor: „ganz alt“/„GANS müde“/„alt“ → „Gans …“, nur „Gans“ → fehlerhaft; Schalter aus lässt alles, wie es ist",
   [z[1] for z in zl(r)] == ["Gans", "Gans alt", "Gans müde", "Gans rot", "Gans blau"] and zl(r)[0][4] == "fehler"
   and "Gans" in r["zeilen"][0]["text"] and paare(r0) == [("alt", "viejo"), ("Gans müde", "cansado")], zl(r))
r = lies("=SUMME(A1);x\n+49;y\n@a;b\nalt;=1+1\nmüde;cansado;-x".encode())
ok("Formel-Anfang (= + - @) in jeder Spalte → fehlerhaft (k_formel), nicht wählbar",
   all(z["status"] == "fehler" and "Formel" in z["text"] and not z["wahl"] for z in r["zeilen"]), zl(r))
lang = lies(("a" * 116 + ";x\nalt;" + "b" * 301 + "\nmüde;c;" + "n" * 301 + "\nrot;" + "w" * 300).encode())
ok("Überlänge (Deutsch > 120, Wort > 300, Notiz > 300) → fehlerhaft mit Zahl, nichts still gekürzt; genau 300 geht",
   [z["status"] for z in lang["zeilen"]] == ["fehler", "fehler", "fehler", "neu"] and "121" in lang["zeilen"][0]["text"]
   and len(lang["zeilen"][0]["de"]) == 121 and len(lang["zeilen"][1]["wort"]) == 301 and len(lang["zeilen"][3]["wort"]) == 300,
   [(z["status"], z["text"][:60]) for z in lang["zeilen"]])
r = lies("123;x\n🦢;cisne\nalt;🦢\nalt2;老人\ngroß;größe\nrot;<script>alert(1)</script>".encode())
st = [(z["status"], len(z["hinweise"])) for z in r["zeilen"]]
ok("Nur Ziffern / nur Emoji → fehlerhaft; Emoji, Japanisch, ä/ö/ß im Wort bei es → nur Hinweis; HTML bleibt reiner Text",
   st[:5] == [("fehler", 0), ("fehler", 0), ("neu", 1), ("neu", 1), ("neu", 1)] and "Spanisch" in r["zeilen"][3]["hinweise"][0]
   and "ö" in r["zeilen"][4]["hinweise"][0]
   and r["zeilen"][5]["wort"] == "<script>alert(1)</script>", st)
r = lies("müde;müde".encode(), zs="es")
ok("Umlaut-Hinweis nur bei ä/ö/ß (ü gibt es im Spanischen); andere Kartensprache (de-ähnlich) ohne es-Hinweis",
   not r["zeilen"][0]["hinweise"] and lies("alt;größer".encode())["zeilen"][0]["hinweise"]
   and not lies("alt;größer".encode(), zs="nds")["zeilen"][0]["hinweise"], zl(r))
# ---------- Stufe 11: doppelt ----------
r = lies("alt;viejo\nALT;viejo\nGans alt;anciano\nÄlter;x\naelter;y\nneu;viejo".encode())
ok("Doppelt in der Liste: Groß/Klein, „Gans“ davor, ä = ae, gleiche Übersetzung – spätere Zeile nicht vorausgewählt, nennt Zeile + andere Übersetzung",
   [z[4] for z in zl(r)] == ["neu", "doppelt_liste", "doppelt_liste", "neu", "doppelt_liste", "doppelt_liste"]
   and r["zeilen"][2]["text"].endswith("(dort mit „viejo“)") and "Zeile 1" in r["zeilen"][1]["text"] and "dort" not in r["zeilen"][1]["text"]
   and [z["wahl"] for z in r["zeilen"]] == [True, False, False, True, False, False] and r["zahlen"]["doppelt"] == 4, zl(r))
vorhanden = dict(ideen=[dict(de="Gans rot", es="rojo")], karten=[dict(de="Gans blau", es="azul", nr=3, bild="blau.jpg")])
r = lies("rot;x\nx2;rojo\ngrün;azul\nblau;y\nneu;nuevo".encode(), vorhanden=vorhanden)
ok("Gegen vorhandene Ideen (Deutsch oder Wort) und Karten (mit Nummer + Bild) → idee_da / karte_da, wählbar, nicht vorausgewählt",
   [z[4] for z in zl(r)] == ["idee_da", "idee_da", "karte_da", "karte_da", "neu"] and "3" in r["zeilen"][2]["text"]
   and "blau.jpg" in r["zeilen"][2]["text"] and [z["wahl"] for z in r["zeilen"]] == [False, False, False, False, True], zl(r))
ja = lies("alt;老人\nalt2;老人\nalt3;ﾛｳｼﾞﾝ\nalt4;ロウジン".encode(), zs="ja")
ru = lies("alt;старый\nalt2;СТАРЫЙ\nalt3;старый!".encode(), zs="ru")
ok("Japanisch/Russisch: gleiche Wörter werden erkannt (NFKC, Groß/Klein, Satzzeichen), nicht alle „leer“; wort_schluessel unverändert",
   [z[4] for z in zl(ja)] == ["neu", "doppelt_liste", "neu", "doppelt_liste"] and [z[4] for z in zl(ru)] == ["neu", "doppelt_liste", "doppelt_liste"]
   and "dort" not in ru["zeilen"][1]["text"] and erw.wort_schluessel("老人", True) == "" and erw.wort_schluessel_zs("老人", "ja") == "老人"
   and erw.wort_schluessel("Gans Müde") == "muede" and erw.wort_schluessel_zs("Viejo / anciano", "es") == "viejo", (zl(ja), zl(ru)))
# ---------- Grenzen und Robustheit ----------
z500 = "\n".join(f"wort{i};palabra{i}" for i in range(500)).encode()
t0 = time.time(); r500 = lies(z500, vorhanden=dict(ideen=[dict(de=f"Gans x{i}", es=f"y{i}") for i in range(300)])); dauer = time.time() - t0
r501 = lies(("Deutsch;Spanisch\n" + "\n".join(f"wort{i};palabra{i}" for i in range(501))).encode())
gross = lies(b"alt;viejo\n" * 120_000)
ok("Grenzen: 500 Wörter gehen (< 2 s), 501 → „bitte teilen“ mit Zahl (nichts abgeschnitten), > 1 MB → ablehnen, nur Kopf → Hinweis",
   len(r500.get("zeilen", [])) == 500 and r500["zahlen"]["neu"] == 500 and dauer < 2 and r501.get("fehler") == "wl_zu_viele"
   and "501" in r501["text"] and gross.get("fehler") == "wl_gross" and lies("Deutsch;Spanisch\n\n".encode()).get("fehler") == "wl_nur_kopf",
   (round(dauer, 2), r501, gross.get("fehler")))
zufall = random.Random(42)
schlecht, langsam = [], 0.0
for n in range(200):
    if n % 2:
        roh = bytes(zufall.randrange(256) for _ in range(zufall.randrange(1, 3000)))
    else:
        roh = "".join(zufall.choice("aäß;,\t=- \n\r#\"„“1.•🦢老ж​ \x00 ") for _ in range(zufall.randrange(1, 800))).encode(
            zufall.choice(["utf-8", "utf-16-le", "utf-16"]), "surrogatepass")
    t0 = time.time()
    try:
        r = erw.wortliste_lesen(roh, {"zs": zufall.choice(["es", "ja", "ru", "ar"]), "trenner": zufall.choice(erw.WL_TRENNER),
                                      "kopf": zufall.choice(["auto", "ja", "nein"])})
        json.dumps(r)
        assert all(z["status"] in ("neu", "fehler", "doppelt_liste", "idee_da", "karte_da") for z in r["zeilen"])
    except erw.WortlisteFehler:
        pass
    except Exception as f:
        schlecht.append((n, type(f).__name__, str(f)[:80]))
    langsam = max(langsam, time.time() - t0)
ok("200 Zufalls-Byte-Folgen (random.Random(42)): nie ein unbehandelter Fehler, jede < 1 s", not schlecht and langsam < 1, (schlecht[:3], round(langsam, 2)))
# ---------- API ----------
def direkt(methode, weg, koerper=b"", abfrage="", am_handy=False):
    kopf = {"X-GL-Sprache": "de", "Content-Type": "application/json" if weg != "/api/wortliste-pruefen" else "application/octet-stream"}
    if isinstance(koerper, (dict, list)):
        koerper = json.dumps(koerper).encode()
    s, k, i = ui.verarbeite(methode, weg, abfrage, koerper, kopf, am_handy=am_handy)
    try:
        return s, json.loads(i)
    except ValueError:
        return s, {}
def ideen():
    return json.loads(erw.IDEEN_DATEI.read_text(encoding="utf-8"))["ideen"] if erw.IDEEN_DATEI.exists() else []
karte = ui.karten_daten()["karten"][0]
s1, v = direkt("POST", "/api/wortliste-pruefen", f"Deutsch;Spanisch\nquer;transversal\nmüde;cansado\nrot;rojo\n{karte['de']};x".encode(), "trenner=auto&gans=1")
ok("POST /api/wortliste-pruefen (Rohdaten, Optionen in der Abfrage) → Vorschau mit erkannt, zs und Karte als „schon Karte“",
   s1 == 200 and v.get("zs") == "es" and v["erkannt"]["kopf"] and [z["status"] for z in v["zeilen"]] == ["neu", "neu", "neu", "karte_da"]
   and v.get("zs_name") == "Spanisch", (s1, str(v)[:300]))
s0, leer = direkt("POST", "/api/wortliste-pruefen", b"")
sg, gr = direkt("POST", "/api/wortliste-pruefen", b"a;b\n" * 300_000)
sx, xl = direkt("POST", "/api/wortliste-pruefen", b"PK\x03\x04xxxx")
ok("Leere Liste, > 1 MB, Excel-Datei → 400 mit freundlichem Text (keine 500)",
   (s0, sg, sx) == (400, 400, 400) and "leer" in leer.get("fehler", "") and "MB" in gr.get("fehler", "") and "CSV UTF-8" in xl.get("fehler", ""),
   (s0, sg, sx, leer, gr, xl))
vorher = len(ideen())
sr, ir = direkt("POST", "/api/idee", {"de": "Gans rot", "es": "rojo"})          # dazwischen angelegt → Vorschau veraltet
zeilen = [dict(nr=z["nr"], de=z["de"], wort=z["wort"], notiz=z["notiz"]) for z in v["zeilen"] if z["wahl"]]
s2, u = direkt("POST", "/api/wortliste-uebernehmen", {"zs": "es", "zeilen": zeilen})
neu = ideen()
ok("Übernehmen: alle in einem Schreibvorgang, Reihenfolge wie in der Liste oben; veraltete Vorschau → „rot“ übersprungen (schon Idee)",
   s2 == 200 and u["angelegt"] == 2 and [x["status"] for x in u["uebersprungen"]] == ["idee_da"] and u["uebersprungen"][0]["nr"] == 4
   and [x["de"] for x in neu[:2]] == ["Gans quer", "Gans müde"] and len(neu) == vorher + 3 and all(x.get("wl") == u["wl"] and x["es_auto"] == ""
   for x in neu[:2]) and len(u.get("ideen", [])) == len(neu), (s2, str(u)[:400]))
s3, z3 = direkt("POST", "/api/wortliste-uebernehmen", {"zs": "ru", "zeilen": zeilen})
s4, z4 = direkt("POST", "/api/wortliste-uebernehmen", {"zs": "es", "zeilen": [dict(de="=1+1", wort="x"), dict(de="Gans", wort="y"),
                                                                               dict(de="a" * 130, wort="z"), dict(de="Gans quer4", wort="transversal4")]})
s5, z5 = direkt("POST", "/api/wortliste-uebernehmen", {"zs": "es", "zeilen": "kaputt"})
s6, z6 = direkt("POST", "/api/wortliste-uebernehmen", {"zs": "es", "zeilen": []})
ok("Kartensprache gewechselt → 409 zs_geaendert; jede Zeile wird beim Anlegen erneut geprüft (Formel, nur Gans, Länge); kaputte Daten → 400",
   s3 == 409 and z3.get("code") == "zs_geaendert" and "Kartensprache" in z3.get("fehler", "")
   and s4 == 200 and z4["angelegt"] == 1 and [x["status"] for x in z4["uebersprungen"]] == ["fehler"] * 3
   and s5 == 400 and s6 == 400 and "ausgewählt" in z6.get("fehler", ""), (s3, z3, s4, str(z4)[:300], s5, s6))
# zwei gleichzeitige Übernahmen derselben Liste + zwei verschiedene Listen
vorher = len(ideen())
gleich = [dict(de=f"Gans gleich{i}", wort=f"igual{i}") for i in range(40)]
antworten = []
def los(z):
    antworten.append(direkt("POST", "/api/wortliste-uebernehmen", {"zs": "es", "zeilen": z}))
fs = [threading.Thread(target=los, args=(gleich,)) for _ in range(2)]
fs += [threading.Thread(target=los, args=([dict(de=f"Gans liste{k}x{i}", wort=f"lista{k}x{i}") for i in range(30)],)) for k in range(2)]
[f.start() for f in fs]; [f.join() for f in fs]
nachher = ideen()
schl = [erw.wort_schluessel(x["de"]) for x in nachher]
ok("Zwei gleichzeitige Übernahmen (Threads): keine Doppelten, nichts verloren (40 + 30 + 30), ideen.json bleibt gültiges JSON",
   len(nachher) == vorher + 100 and len(schl) == len(set(schl)) and sorted(a[1]["angelegt"] for a in antworten) == [0, 30, 30, 40]
   and all(a[0] == 200 for a in antworten), (len(nachher) - vorher, sorted(a[1].get("angelegt") for a in antworten)))
# Rückgängig
liste = direkt("POST", "/api/wortliste-uebernehmen", {"zs": "es", "zeilen": [dict(de=f"Gans rueck{i}", wort=f"atras{i}") for i in range(4)]})[1]
vorher_ids = [x["id"] for x in ideen() if x.get("wl") != liste["wl"]]
eigene = [x for x in ideen() if x.get("wl") == liste["wl"]]
direkt("POST", "/api/idee", {"id": eigene[0]["id"], "de": eigene[0]["de"], "es": "atras geändert", "notiz": ""})
direkt("POST", "/api/idee-weg", {"id": eigene[1]["id"]})
s7, r7 = direkt("POST", "/api/wortliste-rueckgaengig", {"wl": liste["wl"]})
rest = ideen()
s8, r8 = direkt("POST", "/api/wortliste-rueckgaengig", {"wl": liste["wl"]})
s9, r9 = direkt("POST", "/api/wortliste-rueckgaengig", {"wl": "../x"})
s10, r10 = direkt("POST", "/api/wortliste-rueckgaengig", {"wl": "0123456789ab"})
ok("Rückgängig: entfernt nur unveränderte Ideen der Liste, geänderte bleiben, weggenommene zählen als „nicht mehr da“; Rest unberührt",
   s7 == 200 and (r7["entfernt"], r7["geaendert"], r7["schon_karte"]) == (2, 1, 1) and [x["id"] for x in rest if x["id"] != eigene[0]["id"]] == vorher_ids
   and any(x["id"] == eigene[0]["id"] for x in rest) and s8 == 200 and (r8["entfernt"], r8["geaendert"], r8["schon_karte"]) == (0, 1, 0)
   and s9 == 400 and s10 == 400 and "rückgängig" in r10.get("fehler", ""), (s7, r7.get("entfernt"), r7.get("geaendert"), r7.get("schon_karte"), s8, s9, s10))
try:
    json.loads(erw.IDEEN_DATEI.read_text(encoding="utf-8")); gueltig = True
except ValueError:
    gueltig = False
# Handy-Zugang, Web-App, echter HTTP-Server
sh, vh = direkt("POST", "/api/wortliste-pruefen", "alt;viejo".encode(), am_handy=True)
ui.im_browser = lambda: True
sw, vw = direkt("POST", "/api/wortliste-pruefen", "alt;viejo".encode())
sw2, uw = direkt("POST", "/api/wortliste-uebernehmen", {"zs": "es", "zeilen": [dict(de="Gans webapp", wort="aplicación")]})
ui.im_browser = lambda: False
ui.starte(port, browser=False)
a = urllib.request.Request(f"http://127.0.0.1:{ui.PORT}/api/wortliste-pruefen?trenner=semikolon", data="alt;viejo".encode("utf-16"), method="POST",
                           headers={"Cookie": f"mgd_{ui.PORT}={ui.TOKEN}", "X-GL-Token": ui.TOKEN, "X-GL-Sprache": "de",
                                    "Content-Type": "application/octet-stream"})
try:
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(a, timeout=60) as x:
        sh2, vh2 = x.status, json.loads(x.read())
except urllib.error.HTTPError as f:
    sh2, vh2 = f.code, {}
ok("Über den Handy-Zugang, in der Web-App (verarbeite) und über HTTP wie am Rechner; ideen.json gültig",
   gueltig and sh == 200 and sw == 200 and paare(vh) == paare(vw) == [("Gans alt", "viejo")] and sw2 == 200 and uw["angelegt"] == 1
   and sh2 == 200 and paare(vh2) == [("Gans alt", "viejo")] and vh2["erkannt"]["kodierung"] == "utf-16-le", (sh, sw, sw2, sh2, str(vh2)[:200]))
print("#e42 " + json.dumps(E, ensure_ascii=False))
'''


def test_wortliste(p, tmp):
    """E42 (2.2): Wortliste in Ideen – Einlesen in Stufen (Dateiart, Kodierung, Bereinigen, Zeilen, Trenner, Kopf, Spalten,
    Felder, „Gans“, Prüfen, Doppelt), Grenzen, 200 Zufalls-Byte-Folgen; API prüfen → übernehmen (erneut geprüft, 409 bei
    gewechselter Kartensprache, gleichzeitig ohne Doppelte) → rückgängig; Handy-Zugang, Web-App und HTTP."""
    print("\n[E42] Wortliste: Einlesen, Prüfen, Anlegen, Rückgängig")
    daten = tmp / "daten-e42"
    ideen = tmp / "ideen-e42"
    daten.mkdir()
    ideen.mkdir()
    env = dict(os.environ, PYTHONIOENCODING="utf-8", MGD_DATEN=str(daten), MGD_START_ID="test")
    env.pop("MGD_IM_PROZESS", None)
    r = subprocess.run([sys.executable, "-c", E42_PROZESS, str(p), str(ideen), str(tg._freier_port())], cwd=p, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    m = re.search(r"^#e42 (.*)$", r.stdout, re.M)
    if not m:
        print((r.stdout + r.stderr)[-3000:])
        pruefe("E42-Prozess lief durch", False, (r.stdout + r.stderr)[-600:])
        return
    for name, gut, detail in json.loads(m.group(1)):
        pruefe(name, gut, detail)


E43_PROZESS = r'''
import json, os, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
os.environ.pop("MGD_IM_PROZESS", None)
p, tmp = Path(sys.argv[1]), Path(sys.argv[2])
import gans_ui as ui, gans_lernkarten as gl, erweiterungen as erw, uebersetzer
gl.setze_sprache("de")
erw.IDEEN_DATEI, erw.IDEEN_ORDNER = tmp / "ideen.json", tmp / "ideen"
E = []
def ok(name, gut, detail=""):
    E.append([name, bool(gut), str(detail)[:700]])
def direkt(methode, weg, koerper=b"", am_handy=False):
    kopf = {"X-GL-Sprache": "de", "Content-Type": "application/json" if weg != "/api/wortliste-pruefen" else "application/octet-stream"}
    if isinstance(koerper, (dict, list)):
        koerper = json.dumps(koerper).encode()
    s, k, i = ui.verarbeite(methode, weg, "", koerper, kopf, am_handy=am_handy)
    try:
        return s, json.loads(i)
    except ValueError:
        return s, {}
def ideen():
    return json.loads(erw.IDEEN_DATEI.read_text(encoding="utf-8"))["ideen"] if erw.IDEEN_DATEI.exists() else []
# nachgebildeter Dienst: 3 Wörter, danach Tageskontingent erschöpft
aufrufe = []
def falsch_uebersetze(de, dienst=None, richtung="de-es", **k):
    aufrufe.append(de)
    if len(aufrufe) > 3:
        raise uebersetzer.UebersetzungsFehler("kontingent")
    w = "auto" + de.split()[-1]
    return dict(quelle=de, dienst="wiktionary", vorschlag=w, alternativen=[dict(text=w, hinweis="")], aus_cache=False)
uebersetzer.uebersetze = falsch_uebersetze
s1, v = direkt("POST", "/api/wortliste-pruefen", "\n".join(f"e43wort{i}" for i in range(1, 7)).encode())
zeilen = [dict(nr=z["nr"], de=z["de"], wort=z["wort"], notiz=z["notiz"]) for z in v.get("zeilen", []) if z["wahl"]]
s2, u = direkt("POST", "/api/wortliste-uebernehmen", {"zs": "es", "zeilen": zeilen})
ok("Wortliste ohne Übersetzung (einspaltig) → 6 Ideen mit „Gans …“, ohne Wort",
   s1 == 200 and s2 == 200 and u.get("angelegt") == 6 and all(x["de"].startswith("Gans e43wort") and not x["es"] for x in ideen()[:6]), (s1, s2, str(u)[:300]))
# wie die Seite: Liste der Ideen ohne Wort, je Idee /api/uebersetzen → /api/idee-wort, Abbruch beim ersten Fehler
offen = [i for i in ideen() if i["de"].strip() and not i["es"].strip()]
gefuellt, meldung, status = 0, "", 200
for i in offen:
    s, r = direkt("POST", "/api/uebersetzen", {"de": i["de"]})
    if s != 200:
        status, meldung = s, r.get("fehler", "")
        break
    s, r = direkt("POST", "/api/idee-wort", {"id": i["id"], "es": r["vorschlag"]})
    gefuellt += bool(s == 200 and r.get("gefuellt"))
nachher = {i["id"]: i for i in ideen()}
voll = [nachher[i["id"]] for i in offen[:3]]
leer = [nachher[i["id"]] for i in offen[3:]]
ok("Alle übersetzen mit nachgebildetem Dienst: Kontingent nach 3 erschöpft → 3 gefüllt (als „automatisch – prüfen“), Rest leer, freundliche Meldung",
   len(offen) == 6 and gefuellt == 3 and len(aufrufe) == 4 and all(x["es"] == x["es_auto"] == "auto" + x["de"].split()[-1] for x in voll)
   and all(not x["es"] and not x["es_auto"] for x in leer) and status == 400 and "Tageskontingent" in meldung, (gefuellt, len(aufrufe), status, meldung))
# nur füllen, wenn das Feld beim Speichern noch leer ist
ziel = leer[0]
direkt("POST", "/api/idee", {"id": ziel["id"], "de": ziel["de"], "es": "eigenes", "notiz": ""})
s3, r3 = direkt("POST", "/api/idee-wort", {"id": ziel["id"], "es": "vorschlag"})
jetzt = {i["id"]: i for i in ideen()}[ziel["id"]]
s4, r4 = direkt("POST", "/api/idee-wort", {"id": leer[1]["id"], "es": "=1+1"})
s5, r5 = direkt("POST", "/api/idee-wort", {"id": "../x", "es": "x"})
s6, r6 = direkt("POST", "/api/idee-wort", {"id": leer[1]["id"], "es": "  "})
ok("/api/idee-wort: eigenes Wort bleibt (gefuellt false), Formel → 400, ungültige id/leeres Wort → 400",
   s3 == 200 and r3.get("gefuellt") is False and jetzt["es"] == "eigenes" and not jetzt["es_auto"] and len(r3.get("ideen", [])) == len(ideen())
   and (s4, s5, s6) == (400, 400, 400), (s3, r3.get("gefuellt"), jetzt.get("es"), s4, s5, s6))
# Rückgängig: automatisch gefüllte Ideen gelten weiter als unverändert, von Hand geänderte bleiben
s7, r7 = direkt("POST", "/api/wortliste-rueckgaengig", {"wl": u["wl"]})
ok("Rückgängig nach „Alle übersetzen“: automatisch gefüllte zählen als unverändert (5 entfernt), die von Hand geänderte bleibt",
   s7 == 200 and (r7.get("entfernt"), r7.get("geaendert")) == (5, 1) and [i["id"] for i in ideen()] == [ziel["id"]], (s7, r7.get("entfernt"), r7.get("geaendert")))
leer2 = ideen()[0]
direkt("POST", "/api/idee", {"id": leer2["id"], "de": leer2["de"], "es": "", "notiz": ""})
sh, rh = direkt("POST", "/api/idee-wort", {"id": leer2["id"], "es": "handy"}, am_handy=True)
ok("/api/idee-wort auch über den Handy-Zugang (und damit in der Web-App) erlaubt", sh == 200 and rh.get("gefuellt") is True, (sh, rh.get("fehler")))
print("#e43 " + json.dumps(E, ensure_ascii=False))
'''


def test_wortliste_oberflaeche(p, tmp):
    """E43 (2.2): Wortliste in der Oberfläche – Texte de/en/es (auch dynamische Schlüssel und _touch), esc() in der
    Vorschau, accept-Liste, Dialog im Reiter Ideen, „Alle übersetzen“ über alleUebersetzen + /api/idee-wort; API-Ablauf
    „Liste ohne Übersetzung → Alle übersetzen“ mit nachgebildetem Dienst (Kontingent nach 3), Rückgängig, Handy."""
    print("\n[E43] Wortliste: Oberfläche und „Alle übersetzen“")
    seite = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    txt = {"de": [], "en": [], "es": []}
    a = seite.index("const TXT = {")
    for m in re.finditer(r"\n(de|en|es)\s*:\s*\{", seite[a:seite.index("\n};", a)]):
        txt[m.group(1)] += js_schluessel(seite, a + m.end() - 1)
    for m in re.finditer(r"Object\.assign\(TXT\.(de|en|es),\s*\{", seite):
        txt[m.group(1)] += js_schluessel(seite, m.end() - 1)
    noetig = ["wl_trenner_" + w for w in ("auto", "tab", "semikolon", "komma", "gleich", "strich", "keiner")]
    noetig += ["wl_kopf_" + w for w in ("auto", "ja", "nein")] + ["wl_einspaltig_de", "wl_einspaltig_zs"]
    noetig += [f"{v}_{w}" for w in ("trenner", "kopf", "einspaltig", "tauschen", "gans") for v in ("wl_o", "h_wl")]
    noetig += ["wl_s_" + s for s in ("neu", "doppelt_liste", "idee_da", "karte_da", "fehler")]
    noetig += [f"wl_bsp_{i}{e}" for i in range(1, 6) for e in ("", "_text")]
    noetig += [k + "_touch" for k in ("wl_waehlen", "wl_waehlen_text", "h_wl_datei")]
    fehlt = [f"{s}.{k}" for s in txt for k in noetig if k not in txt[s]]
    import erweiterungen as erw
    pruefe("Texte der Wortliste in de/en/es – auch die dynamischen Schlüssel (Trenner, Kopf, Status, Beispiele) und _touch-Varianten",
           not fehlt and tuple(erw.WL_TRENNER) == ("auto", "tab", "semikolon", "komma", "gleich", "strich", "keiner"), fehlt[:8])
    def funktion(name):
        i = seite.index(f"function {name}(")
        return seite[i:seite.index("\n}", i)]
    zeile, wl = funktion("wlZeileHTML"), funktion("zeichneWL")
    pruefe("Vorschau: jedes Feld der Zeile über esc() (de, wort, notiz, text, roh, Hinweise), kein ${z.…} ungeschützt",
           not re.search(r"\$\{\s*z\.(de|wort|notiz|text|roh|nr|status)\s*\}", zeile) and all(f"esc({x})" in zeile for x in ("z.de", "z.wort", "z.notiz", "z.text", "z.roh", "z.nr", "h"))
           and "esc(h)" in wl and "innerHTML" not in zeile, zeile[:200])
    pruefe("Dateifeld: accept nur Text/CSV/TSV, Dialog im Reiter Ideen, Ziehfläche + Einfügen, ≤ 1 MB schon in der Seite",
           'const WL_ACCEPT = ".txt,.csv,.tsv,text/plain,text/csv,text/tab-separated-values"' in seite
           and 'data-dialog="wortliste"' in seite[seite.index('id="v-ideen"'):seite.index('id="ideen-inhalt"')]
           and 'data-zieh="wortliste"' in wl and 'id="wl-text"' in wl and "WL_MAX_BYTES = 1024 * 1024" in seite
           and "dateiWaehlen(WL_ACCEPT, wlDatei)" in seite, "")
    anlegen = funktion("wlAnlegen")
    pruefe("Anlegen: Doppelklick-Sperre, 409 zs_geaendert → Vorschau neu, Toast mit Rückgängig über /api/wortliste-rueckgaengig",
           "WL.status)" in anlegen and '"zs_geaendert"' in anlegen and "wlPruefen()" in anlegen and "wlRueckgaengig(r.wl)" in anlegen
           and '"/api/wortliste-rueckgaengig"' in funktion("wlRueckgaengig"), "")
    i = seite.index('$("#ideen-uebersetzen").addEventListener')
    knopf = seite[i:seite.index("\n});", i)]
    alle = funktion("alleUebersetzen")
    pruefe("„🌐 Alle übersetzen“ in Ideen: nutzt alleUebersetzen + /api/idee-wort, sichtbar nur mit Ideen ohne Wort; Abbruch meldet „n von m“",
           "alleUebersetzen(knopf" in knopf and '"/api/idee-wort"' in knopf and "await a.fuellen(v)" in alle
           and alle.count('t("uebersetzt_n"') == 2 and '$("#ideen-uebersetzen").hidden = !IDEEN.ideen.some(ideeOhneWort)' in funktion("zeichneIdeen"), "")
    ideen = tmp / "ideen-e43"
    daten = tmp / "daten-e43"
    ideen.mkdir()
    daten.mkdir()
    env = dict(os.environ, PYTHONIOENCODING="utf-8", MGD_DATEN=str(daten), MGD_START_ID="test")
    env.pop("MGD_IM_PROZESS", None)
    r = subprocess.run([sys.executable, "-c", E43_PROZESS, str(p), str(ideen)], cwd=p, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    m = re.search(r"^#e43 (.*)$", r.stdout, re.M)
    if not m:
        print((r.stdout + r.stderr)[-3000:])
        pruefe("E43-Prozess lief durch", False, (r.stdout + r.stderr)[-600:])
        return
    for name, gut, detail in json.loads(m.group(1)):
        pruefe(name, gut, detail)


E45_PROZESS = r'''
import hashlib, io, json, os, sys, zipfile
from pathlib import Path
sys.path.insert(0, sys.argv[1])
os.environ.pop("MGD_IM_PROZESS", None)
p, tmp = Path(sys.argv[1]), Path(sys.argv[2])
import gans_ui as ui, gans_lernkarten as gl, erweiterungen as erw
from PIL import Image
gl.setze_sprache("de")
erw.IDEEN_DATEI, erw.IDEEN_ORDNER = tmp / "ideen.json", tmp / "ideen"
E = []
def ok(name, gut, detail=""):
    E.append([name, bool(gut), str(detail)[:700]])
def direkt(weg, daten, am_handy=False, methode="POST"):
    s, k, i = ui.verarbeite(methode, weg, "", json.dumps(daten).encode() if methode == "POST" else b"",
                            {"X-GL-Sprache": "de", "Content-Type": "application/json"}, am_handy=am_handy)
    try:
        return s, json.loads(i)
    except ValueError:
        return s, {}
def idee(iid):
    return next((i for i in json.loads(erw.IDEEN_DATEI.read_text(encoding="utf-8"))["ideen"] if i["id"] == iid), {})
def png(farbe=(90, 160, 60)):
    b = io.BytesIO(); Image.new("RGB", (448, 320), farbe).save(b, "PNG"); return b.getvalue()
# --- Bildidee: eigenes Feld, nur geändert, wenn mitgeschickt ---
s1, r1 = direkt("/api/idee", {"de": "", "es": "", "bild_idee": "  goose   on a\nred bike  "})
iid = r1.get("id", "")
s2, r2 = direkt("/api/idee", {"id": iid, "de": "Gans klar", "es": "claro", "notiz": "n"})
s3, r3 = direkt("/api/ideen", {}, methode="GET")
liste = next((i for i in r3.get("ideen", []) if i["id"] == iid), {}) if s3 == 200 else {}
ok("Bildidee allein legt eine Idee an (Leerraum zusammengefasst), Speichern ohne bild_idee behält sie, /api/ideen liefert sie",
   s1 == 200 and s2 == 200 and idee(iid).get("bild_idee") == "goose on a red bike" and liste.get("bild_idee") == "goose on a red bike"
   and (idee(iid)["de"], idee(iid)["es"]) == ("Gans klar", "claro"), (s1, s2, idee(iid), liste))
s4, _ = direkt("/api/idee", {"id": iid, "de": "Gans klar", "es": "claro", "notiz": "n", "bild_idee": "x" * 400})
lang = idee(iid).get("bild_idee", "")
s5, r5 = direkt("/api/idee", {"id": iid, "de": "Gans klar", "es": "claro", "notiz": "n", "bild_idee": "=HYPERLINK(1)"})
s6, _ = direkt("/api/idee", {"id": iid, "de": "Gans klar", "es": "claro", "notiz": "n", "bild_idee": ""})
ok("Bildidee: höchstens 300 Zeichen (= KI-Beschreibung), Formel → 400, leer = gelöscht",
   s4 == 200 and len(lang) == erw.BILD_IDEE_MAX == 300 and s5 == 400 and r5.get("fehler") and s6 == 200 and idee(iid).get("bild_idee") == "",
   (s4, len(lang), s5, s6))
direkt("/api/idee", {"id": iid, "de": "Gans klar", "es": "claro", "notiz": "n", "bild_idee": "goose wearing sunglasses"})
# --- Export/Import: Bildidee reist mit; ältere Exporte ohne Feld lassen die vorhandene stehen ---
z, _ = erw.export_zip(inhalt="ideen")
ex = json.loads(zipfile.ZipFile(io.BytesIO(z)).read("ideen.json"))["ideen"]
def importiere(ideen, ersetzen):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as zz:
        zz.writestr("ideen.json", json.dumps({"ideen": ideen}))
    roh = b.getvalue()
    v = erw.import_speichern(io.BytesIO(roh).read, len(roh))
    st = [e["status"] for e in v["ideen"]]
    if ersetzen is not None:
        erw.import_uebernehmen({"id": v["id"], "ersetzen": ersetzen})
    return st
eigen = next(i for i in ex if i["id"] == iid)
st_gleich = importiere([eigen], None)
st_anders = importiere([dict(eigen, bild_idee="goose on a sled")], {"standard": True})
nach_import = idee(iid).get("bild_idee")
alt = {k: v for k, v in eigen.items() if k != "bild_idee"}
st_alt = importiere([dict(alt, es="evidente")], {"standard": True})
ok("Export enthält bild_idee; eigener Export „gleich“, andere Bildidee → Konflikt + Ersetzen; älterer Export ohne Feld behält sie",
   eigen.get("bild_idee") == "goose wearing sunglasses" and st_gleich == ["gleich"] and st_anders == ["konflikt"]
   and nach_import == "goose on a sled" and st_alt == ["konflikt"] and idee(iid).get("es") == "evidente"
   and idee(iid).get("bild_idee") == "goose on a sled", (st_gleich, st_anders, nach_import, st_alt, idee(iid)))
# --- Wortliste: Fingerabdruck ohne Bildidee wie vor 2.3, mit Bildidee = von Hand geändert ---
w = {"de": "Gans a", "es": "b", "notiz": "", "bild": ""}
vorher = hashlib.sha1(json.dumps(["Gans a", "b", "", ""], ensure_ascii=False).encode("utf-8")).hexdigest()[:16]
ok("Wortliste: Fingerabdruck ohne Bildidee unverändert (Rückgängig wie bisher), mit Bildidee anders",
   erw._wl_fingerabdruck(w) == vorher and erw._wl_fingerabdruck(dict(w, bild_idee="x")) != vorher)
# --- KI-Bild für eine Idee: Lauf merkt sich die Ziel-Idee ---
ui._ki_modell_da = lambda: None
lauf = ui._ki_bild_lauf({"beschreibung": "goose wearing sunglasses", "wort": "Gans klar", "idee": iid}, "de")
meta = json.loads((ui.ki_bild_ordner() / f"{lauf.ki_id}.json").read_text(encoding="utf-8"))
ohne = ui._ki_bild_lauf({"beschreibung": "x", "wort": ""}, "de")
karte = next(k["bild"] for k in ui.karten_daten()["karten"])
mit_karte = ui._ki_bild_lauf({"beschreibung": "x", "karte": karte, "idee": iid}, "de")
fehler = []
for falsch in ("../x", "ABCDEF123456", 12, "0" * 13):
    try:
        ui._ki_bild_lauf({"beschreibung": "x", "idee": falsch}, "de")
    except ui.Meldung as m:
        fehler.append(m.status)
ok("KI-Lauf: Ziel-Idee in Meta + Lauf-Status (ki_meta), ohne → None, Karte geht vor, ungültige id → 400",
   lauf.ki_meta.get("idee") == iid and meta.get("idee") == iid and ohne.ki_meta.get("idee") is None
   and mit_karte.ki_meta.get("idee") is None and mit_karte.ki_meta.get("karte") == karte and fehler == [400] * 4,
   (lauf.ki_meta, meta.get("idee"), ohne.ki_meta, mit_karte.ki_meta, fehler))
# --- Übernehmen „ohne Wort für die Idee“ ---
kid = lauf.ki_id
(ui.ki_bild_ordner() / f"{kid}.png").write_bytes(png())
s7, r7 = direkt("/api/ki-bild-uebernehmen", {"id": kid, "idee": iid})
n_vorher = len(json.loads(erw.IDEEN_DATEI.read_text(encoding="utf-8"))["ideen"])
s8, r8 = direkt("/api/ki-bild-uebernehmen", {"id": kid, "idee": ""})
neu = idee(r8.get("id", ""))
s9, _ = direkt("/api/ki-bild-uebernehmen", {"id": kid, "idee": "../boese"})
s10, r10 = direkt("/api/ki-bild-uebernehmen", {"id": kid})
sh, rh = direkt("/api/ki-bild-uebernehmen", {"id": kid, "idee": iid}, am_handy=True)
ok("KI-Bild → Idee: Bild gesetzt (Text bleibt), \"\" = neue Idee mit Text = Wort, ungültige id → 400, ohne idee wie bisher Entwurf, Handy-Zugang erlaubt",
   s7 == 200 and idee(iid).get("bild") and idee(iid).get("de") == "Gans klar" and r7.get("id") == iid
   and s8 == 200 and neu.get("bild") and neu.get("de") == "Gans klar" and len(r8.get("ideen", [])) == n_vorher + 1
   and s9 == 400 and s10 == 200 and r10.get("de") == "Gans klar" and "ideen" not in r10 and sh == 200,
   (s7, idee(iid), s8, neu, s9, s10, str(r10)[:120], sh))
direkt("/api/entwurf-weg", {"id": r10.get("id")})
# --- Bild für eine Idee ohne Text: Wort wird Text (Formel nie) ---
leer = direkt("/api/idee", {"bild_idee": "just a pond"})[1]["id"]
erw.idee_bild_setzen(leer, png((10, 10, 200)), de="=1+1")
formel = idee(leer).get("de")
erw.idee_bild_setzen(leer, png((10, 200, 10)), de="Gans nass")
ok("idee_bild_setzen(de=…): Text nur, wenn die Idee keinen hat; Formel wird nie Text",
   formel == "" and idee(leer).get("de") == "Gans nass" and idee(leer).get("bild_idee") == "just a pond", (formel, idee(leer)))
print("#e45 " + json.dumps(E, ensure_ascii=False))
'''


def test_bild_ki_ideen(p, tmp):
    """E45 (2.3): Ideen – ein Bild-Knopf (Foto/fertiges Bild → GANS-Werkzeug mit „GANS + Wort“ oder unverändert), KI-Bild
    für die Idee (Ziel im Lauf, „ohne Wort für die Idee übernehmen“) und das Feld „Bildidee“ (Merkzettel/KI-Beschreibung:
    API, Export/Import, Wortliste-Rückgängig); Texte de/en/es + Hover."""
    print("\n[E45] Ideen: Bild wählen, KI-Bild für die Idee, Bildidee")
    seite = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    txt = {"de": [], "en": [], "es": []}
    a = seite.index("const TXT = {")
    for m in re.finditer(r"\n(de|en|es)\s*:\s*\{", seite[a:seite.index("\n};", a)]):
        txt[m.group(1)] += js_schluessel(seite, a + m.end() - 1)
    for m in re.finditer(r"Object\.assign\(TXT\.(de|en|es),\s*\{", seite):
        txt[m.group(1)] += js_schluessel(seite, m.end() - 1)
    noetig = ["idee_bild_laden", "idee_bild_ki", "idee_bild_tipp", "idee_bild_tipp_touch", "idee_bild_idee", "idee_bild_idee_ph",
              "h_idee_bild", "h_idee_ki", "h_idee_bild_idee", "gw_unveraendert", "h_gw_unveraendert", "ki_fuer_idee", "ki_ok_idee",
              "ki_idee_info"]
    fehlt = [f"{s}.{k}" for s in txt for k in noetig if k not in txt[s]]
    pruefe("Texte de/en/es: Bild wählen, Mit KI erzeugen, Bildidee (+ Hover, _touch), unverändert, für die Idee; alter Knopf weg",
           not fehlt and "idee_bild_gestalten" not in seite and "h_idee_gestalten" not in seite
           and 'data-i-aktion="gestalten"' not in seite, fehlt[:8])

    def funktion(name):
        i = seite.index(f"function {name}(")
        return seite[i:seite.index("\n}", i)]
    import erweiterungen as erw
    karte = funktion("ideeHTML")
    pruefe("Ideen-Karte: ein Knopf „Bild wählen“ (+ leeres Bildfeld klickbar), „Mit KI erzeugen“ wie im Editor, Feld Bildidee (300)",
           karte.count('data-i-aktion="bild"') == 2 and 'data-i-aktion="ki"' in karte and 'role="button" tabindex="0"' in karte
           and f'data-i-feld="bild_idee" rows="2" maxlength="{erw.BILD_IDEE_MAX}"' in karte and "S.status.ki_bild === false" in karte
           and karte.index('data-i-feld="bild_idee"') < karte.index('data-i-aktion="ki"') < karte.index('data-i-feld="de"')
           and "bild_idee:" in funktion("ideeWerte") and "!w.bild_idee.trim()" in funktion("ideeSpeichern"), "")
    bild, ki_idee = funktion("ideeBild"), funktion("ideeKi")
    pruefe("Jedes Bild (Knopf, Klick, Hineinziehen) → GANS-Werkzeug mit Vorschau (Kartenformat, Text der Idee); KI mit Wort + Bildidee",
           "ZIEH_ZIELE.idee = ideeBild;" in seite and 'oeffneGansWerkzeug({ idee: ziel, text: de, format: "karte" }); await gwFoto([f]);' in bild
           and "MAX_MB" in bild and "dateiWaehlen(BILD_ACCEPT_WEB, d => ideeBild(d, el))" in seite
           and "oeffneKiBild({ idee: ziel, wort: kiRest(w.de), beschreibung: w.bild_idee.trim() })" in ki_idee, "")
    gw = funktion("zeichneGwFenster")
    pruefe("GANS-Werkzeug: für eine Idee „Für diese Idee übernehmen“ + „Bild unverändert übernehmen“ (Originaldatei, ohne Text-Pflicht)",
           "GW.idee !== null" in gw and 'data-gw-aktion="unveraendert"' in gw and "GW.datei = f;" in funktion("gwFoto")
           and "gwFuerIdee(GW.datei, false)" in funktion("gwUnveraendert") and "idee: opt.idee ?? null" in funktion("gwNeu")
           and seite.index('if (a === "unveraendert") return gwUnveraendert(b);') < seite.index("if (!gwRest()) { toast(t(\"gw_text_fehlt\")"), "")
    erg, start = funktion("kiErgebnisHTML"), funktion("kiStarten")
    i = seite.index('if (a === "fuer-idee" && erg)')
    pruefe("KI-Fenster: Ziel-Idee beim Start mitgeschickt + als Bildidee gemerkt, Ergebnis „Ohne Wort für die Idee übernehmen“",
           "{ idee: KI.idee }" in start and "kiIdeeMerken()" in start and 'data-ki="fuer-idee"' in erg
           and '"/api/ki-bild-uebernehmen", { methode: "POST", daten: { id: erg.id, idee: erg.idee || "" } }' in seite[i:i + 300]
           and 'idee: erg.karte ? null : erg.idee ?? null, format: "karte"' in seite and "idee: KI.idee," in funktion("kiToolHolen")
           and seite.count("idee: KI_MERK.letzt.idee") == 2 and 'ki_idee_info' in funktion("zeichneKi"), "")
    ideen, daten = tmp / "ideen-e45", tmp / "daten-e45"
    ideen.mkdir()
    daten.mkdir()
    env = dict(os.environ, PYTHONIOENCODING="utf-8", MGD_DATEN=str(daten), MGD_START_ID="test")
    env.pop("MGD_IM_PROZESS", None)
    r = subprocess.run([sys.executable, "-c", E45_PROZESS, str(p), str(ideen)], cwd=p, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    m = re.search(r"^#e45 (.*)$", r.stdout, re.M)
    if not m:
        print((r.stdout + r.stderr)[-3000:])
        pruefe("E45-Prozess lief durch", False, (r.stdout + r.stderr)[-600:])
        return
    for name, gut, detail in json.loads(m.group(1)):
        pruefe(name, gut, detail)


def test_fix_download_release(tmp):
    """E44 (Fix 2.2, 21.10.2026): Download-Seite bei alter App – ein Service Worker der App 2.0 kennt download/ nicht und
    liefert dort den Startbildschirm der App, dessen relatives app.js er übers Netz holt → download/app.js (Rettung:
    neue Version übernehmen bzw. alten abmelden, neu laden; Texte de/en/es, nie Gerätesprache, keine Endlosschleife);
    Release-Prüfung: neuestes_release.abweichungen() erkennt gleich/anders/fehlt/zu viel. Ohne die Dateien des
    Arbeitsordners entfallen alle 3."""
    print("\n[E44] Fix 2.2: Download-Seite bei alter App, Release-Prüfung nach Push auf main")
    import importlib.util
    from urllib.parse import urljoin
    oben, arbeit = HIER.parent, HIER.parent.parent
    bau, sw_q, nr = arbeit / "werkstatt" / "bau_webapp.py", arbeit / "web-app-quelle" / "sw.js", arbeit / ".github" / "ci" / "neuestes_release.py"
    if not all(x.is_file() for x in (bau, sw_q, nr)):
        print("  (werkstatt/, web-app-quelle/ und .github/ liegen nur im Quellbaum – Prüfungen entfallen)")
        return
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    ziel = tmp / "e44-web"
    b = subprocess.run([sys.executable, str(bau), str(oben), str(ziel), "--ohne-pyodide", "--ohne-modelle"], env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    out = ziel / "web-app"
    lies = lambda p: p.read_text(encoding="utf-8") if p.is_file() else ""   # noqa: E731
    app_index, sw, ret = lies(out / "index.html"), lies(out / "sw.js"), lies(out / "download" / "app.js")
    seite, seite_js = lies(out / "download" / "index.html"), lies(out / "download" / "seite.js")
    texte = re.search(r"var TEXT = \{ en: \"([^\"]+)\",\s*de: \"([^\"]+)\",\s*es: \"([^\"]+)\" \};", ret)
    pruefe("Download-Seite: download/app.js rettet eine App von vor 2.1 – übergibt an den wartenden Service Worker "
           "(„weiter“), sonst abmelden + neu laden (höchstens 3-mal), Texte de/en/es positiv, Sprache = Anker/Wahl/Englisch",
           b.returncode == 0 and texte and all(texte.groups()) and len(set(texte.groups())) == 3
           and 'w.postMessage("weiter")' in ret and 'if (e.data === "weiter") self.skipWaiting();' in sw
           and ret.count("reg.unregister()") >= 2 and '"controllerchange"' in ret and "versuche < 3" in ret
           and 'localStorage.getItem("mgd-download-sprache")' in ret and "navigator.language" not in ret
           and not re.search(r"\bfetch\(|XMLHttpRequest|Warn|Warning", ret) and 'bild.src = "../symbol.svg"' in ret
           and 'sessionStorage.removeItem("mgd-download-rettung")' in seite_js and '"mgd-download-rettung"' in ret
           and "app.js" not in seite, (b.stdout + b.stderr)[-300:])
    # Weg wie der Service Worker 2.0 (ohne EIGENE_SEITEN): Navigation download/ → index.html der App aus dem Vorrat; dessen
    # Skript relativ → download/app.js, nicht im Vorrat → Netz → diese Datei. Elemente, die die Rettung braucht, gibt es dort.
    liste = {x[0] for x in json.loads(re.search(r"^const DATEIEN = (\[.*?\]);", sw, re.M).group(1))} if sw else set()
    basis = "https://beispiel.github.io/me-goos-ta-deutsch/"
    skripte = re.findall(r'<script src="([^"]+)"', app_index)
    weg = [urljoin(basis + "download/", s)[len(basis):] for s in skripte]
    pruefe("Weg der alten App: Startbildschirm unter download/ lädt download/app.js übers Netz (nicht im Vorrat), "
           "#app-start-text und Symbol vorhanden; die neue App lässt download/ durch",
           skripte == ["app.js"] and weg == ["download/app.js"] and "download/app.js" not in liste and "index.html" in liste
           and (out / "download" / "app.js").is_file() and 'id="app-start-text"' in app_index
           and '<img src="symbol.svg" alt="">' in app_index and "if (EIGENE_SEITEN.test(rel)) return;" in sw, f"{skripte} {weg}")
    # neuestes_release.abweichungen: Release-ZIP gegen den Checkout von main
    spec = importlib.util.spec_from_file_location("neuestes_release_e44", nr)
    m = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode, vorher = True, sys.dont_write_bytecode
    try:
        spec.loader.exec_module(m)
    finally:
        sys.dont_write_bytecode = vorher
    co = tmp / "e44-main"
    for n, d in (("README.md", b"Gans"), ("Programm/a.py", b"x = 1\r\n"), (".github/workflows/w.yml", b"on: push"),
                 (".gitattributes", b"* -text\n"), ("release/alt.zip", b"egal")):
        (co / n).parent.mkdir(parents=True, exist_ok=True)
        (co / n).write_bytes(d)

    def zip_mit(name, inhalt):
        z = tmp / name
        with zipfile.ZipFile(z, "w") as f:
            for n, d in inhalt.items():
                f.writestr("Me-Goos-ta-Deutsch/" + n, d)
        return z
    gleich = m.abweichungen(zip_mit("e44-g.zip", {"README.md": b"Gans", "Programm/a.py": b"x = 1\r\n"}), co, ohne=[co / "release"])
    anders = m.abweichungen(zip_mit("e44-a.zip", {"README.md": b"Gans", "Programm/a.py": b"x = 1\n"}), co, ohne=[co / "release"])
    fehlt = m.abweichungen(zip_mit("e44-f.zip", {"README.md": b"Gans"}), co, ohne=[co / "release"])
    mehr = m.abweichungen(zip_mit("e44-m.zip", {"README.md": b"Gans", "Programm/a.py": b"x = 1\r\n", "neu.txt": b"!"}), co,
                          ohne=[co / "release"])
    pruefe("Release-Prüfung: Release-ZIP = main Datei für Datei (Bytes, auch Zeilenenden), .github/ + .gitattributes + "
           "Zielordner zählen nicht; anders / fehlt / zu viel werden genannt",
           gleich == [] and anders == ["anders: Programm/a.py"] and fehlt == ["nur im Checkout: Programm/a.py"]
           and mehr == ["nur im Release: neu.txt"], f"{gleich} {anders} {fehlt} {mehr}")


E46_PROZESS = r'''
import io, json, os, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
os.environ.pop("MGD_IM_PROZESS", None)
p, tmp = Path(sys.argv[1]), Path(sys.argv[2])
import gans_ui as ui, gans_lernkarten as gl, erweiterungen as erw
from PIL import Image
gl.setze_sprache("de")
erw.IDEEN_DATEI, erw.IDEEN_ORDNER = tmp / "ideen.json", tmp / "ideen"
E = []
def ok(name, gut, detail=""):
    E.append([name, bool(gut), str(detail)[:700]])
def direkt(weg, daten=None, roh=None, abfrage="", methode="POST"):
    koerper = roh if roh is not None else json.dumps(daten or {}).encode()
    s, k, i = ui.verarbeite(methode, weg, abfrage, koerper if methode == "POST" else b"",
                            {"X-GL-Sprache": "de", "Content-Type": "application/json"})
    try:
        return s, json.loads(i)
    except ValueError:
        return s, {}
def jpg(farbe):
    b = io.BytesIO(); Image.new("RGB", (900, 640), farbe).save(b, "JPEG", quality=90); return b.getvalue()
def karte(bild):
    return next((k for k in ui.karten_daten()["karten"] if k["bild"] == bild), {})
codes = lambda m: [x["code"] for x in m]
# --- Regel: „Gans“ irgendwo (auch „Gäns…“), sonst „Gans“ vorn; leer bleibt leer ---
faelle = {"Gans alt": "Gans alt", "Die Gans ist alt": "Die Gans ist alt", "Gänsehaut pur": "Gänsehaut pur", "GANS!": "GANS!",
          "Ente  alt": "Gans Ente alt", "ganz alt": "Gans ganz alt", "": "", "   ": ""}
erg = {k: gl.mit_gans(k) for k in faelle}
ok("mit_gans: Gans darf überall stehen (auch Gäns…), sonst „Gans“ vorn; leer bleibt leer", erg == faelle, erg)
cfg = ui.aktuelle_konfig()[1]
m1 = codes(gl.pruefe_karte("Die Gans ist alt", "viejo", cfg)["meldungen"])
m2 = codes(gl.pruefe_karte("Ente alt", "viejo", cfg)["meldungen"])
_, m3 = gl.pruefe_name("Die Gans schwimmt", ".jpg", set())
ok("Prüfung: Hinweis n_ohne_gans nur ohne Gans (nicht mehr, wenn sie mitten im Text steht)",
   "n_ohne_gans" not in m1 and "n_ohne_gans" in m2 and "n_ohne_gans" not in codes(m3), (m1, m2, codes(m3)))
# --- Schritt 1: übernehmen setzt Gans davor (Dateiname mit Gans), mitten im Text bleibt so ---
s, d = direkt("/api/entwurf", roh=jpg((40, 90, 160)), abfrage="name=ente.jpg")
s1, r1 = direkt("/api/entwurf-uebernehmen", {"id": d["id"], "de": "Ente schwimmt", "es": "nada"})
s, d2 = direkt("/api/entwurf", roh=jpg((90, 40, 160)), abfrage="name=x.jpg")
s2, r2 = direkt("/api/entwurf-uebernehmen", {"id": d2["id"], "de": "Die Gans fliegt", "es": "vuela"})
ok("Neue Karte: ohne Gans → „Gans Ente schwimmt“ (gans-ente-schwimmt.jpg) + Hinweis; „Die Gans fliegt“ bleibt (ohne Hinweis)",
   s1 == 200 and r1.get("name") == "gans-ente-schwimmt.jpg" and karte("gans-ente-schwimmt.jpg").get("de") == "Gans Ente schwimmt"
   and "Gans Ente schwimmt" in r1.get("gans_hinweis", "") and s2 == 200 and r2.get("name") == "die-gans-fliegt.jpg"
   and karte("die-gans-fliegt.jpg").get("de") == "Die Gans fliegt" and "gans_hinweis" not in r2, (s1, str(r1)[:200], s2, r2.get("name")))
# --- Schritt 2 / Editor ---
s3, r3 = direkt("/api/karte-speichern", {"bild": "die-gans-fliegt.jpg", "de": "Vogel fliegt", "es": "vuela"})
s4, r4 = direkt("/api/karte-speichern", {"bild": "die-gans-fliegt.jpg", "de": "Mein Gänseblümchen", "es": "margarita"})
ok("Editor: ohne Gans gespeichert → „Gans Vogel fliegt“ + Hinweis; „Mein Gänseblümchen“ bleibt",
   s3 == 200 and "gans_hinweis" in r3 and s4 == 200 and "gans_hinweis" not in r4
   and karte("die-gans-fliegt.jpg").get("de") == "Mein Gänseblümchen", (s3, r3.get("gans_hinweis"), s4, karte("die-gans-fliegt.jpg")))
# --- Tabelle/Kartenliste: nur geänderte Texte; alte Karte ohne Gans bleibt, bis „Gans ergänzen“ ---
csv = ui.pfade()[0]
spalten, zeilen, _ = gl.lies_csv(csv)
for z in zeilen:
    if z["bild"].lstrip("#") == "gans-ente-schwimmt.jpg":
        z["de"] = "Nur Ente"                                    # wie eine alte Karte von vor 2.4
gl.schreibe_csv(csv, zeilen, spalten)
kd = ui.karten_daten()
liste = [dict(k) for k in kd["karten"]]
for k in liste:
    if k["bild"] == "die-gans-fliegt.jpg":
        k["de"] = "Katze"
s5, r5 = direkt("/api/karten", {"karten": liste})
hinweis = next((m for m in r5.get("meldungen", []) if m["code"] == "k_ohne_gans"), {})
ok("Kartenliste speichern: geänderter Text ohne Gans → „Gans Katze“ + Hinweis; unveränderte alte Karte bleibt, Meine Karten meldet sie",
   s5 == 200 and karte("die-gans-fliegt.jpg").get("de") == "Gans Katze" and karte("gans-ente-schwimmt.jpg").get("de") == "Nur Ente"
   and "1" in r5.get("gans_hinweis", "") and hinweis.get("anzahl") == 1 and hinweis.get("stufe") == "info", (s5, r5.get("gans_hinweis"), hinweis))
s6, r6 = direkt("/api/gans-ergaenzen", {})
ok("„Gans ergänzen“: alte Karte → „Gans Nur Ente“, Meldung, danach kein Hinweis mehr",
   s6 == 200 and r6.get("anzahl") == 1 and karte("gans-ente-schwimmt.jpg").get("de") == "Gans Nur Ente"
   and not [m for m in r6["karten"]["meldungen"] if m["code"] == "k_ohne_gans"] and r6.get("meldung"), (s6, r6.get("anzahl"), r6.get("meldung")))
# --- Idee → Karte, Import ---
s, ri = direkt("/api/idee", {"de": "Katze klein", "es": "gatito"})
erw.idee_bild_setzen(ri["id"], jpg((200, 90, 10)))
s7, r7 = direkt("/api/idee-aufnehmen", {"id": ri["id"]})
ok("Idee als Karte: „Katze klein“ → „Gans Katze klein“ + Hinweis",
   s7 == 200 and r7.get("ok") and karte(r7.get("name", "")).get("de") == "Gans Katze klein" and "gans_hinweis" in r7, (s7, str(r7)[:200]))
import zipfile
b = io.BytesIO()
with zipfile.ZipFile(b, "w") as zz:
    zz.writestr("karten.csv", "bild;de;es;notiz\nhund.jpg;Hund;perro;\ngans-pferd.jpg;Gans Pferd;caballo;\n")
    zz.writestr("bilder/hund.jpg", jpg((1, 2, 3)))
    zz.writestr("bilder/gans-pferd.jpg", jpg((3, 2, 1)))
roh = b.getvalue()
v = erw.import_speichern(io.BytesIO(roh).read, len(roh))
r8 = erw.import_uebernehmen({"id": v["id"], "ersetzen": True})
ok("Import: Karte ohne Gans → „Gans Hund“ (Hinweis mit Anzahl), mit Gans unverändert",
   karte("hund.jpg").get("de") == "Gans Hund" and karte("gans-pferd.jpg").get("de") == "Gans Pferd"
   and r8["zahlen"].get("gans") == 1 and "1" in r8.get("gans_hinweis", ""), (karte("hund.jpg"), r8["zahlen"]))
def lies(roh, **o):
    return erw.wortliste_lesen(roh, o)
wl = [z["de"] for z in lies("Die Gans ist alt;viejo\nalt;anciano\nganz neu;nuevo".encode())["zeilen"]]
ok("Wortliste: „Die Gans ist alt“ bleibt, „alt“ → „Gans alt“, „ganz neu“ → „Gans neu“ (wie bisher)",
   wl == ["Die Gans ist alt", "Gans alt", "Gans neu"], wl)
print("#e46 " + json.dumps(E, ensure_ascii=False))
'''


def test_gans_pruefung(p, tmp):
    """E46 (2.4): Jede Karte braucht ihre Gans – „Gans“ (oder „Gäns…“) irgendwo im deutschen Text, sonst setzt das Speichern
    „Gans“ an den Anfang und meldet es (neue Karte, Editor, Kartenliste, Idee → Karte, Import); alte Karten ohne Gans
    meldet „Meine Karten“ mit „Gans ergänzen“; Texte de/en/es."""
    print("\n[E46] Jede Karte braucht ihre Gans")
    import gans_lernkarten as gl
    m = gl.PRUEF_MELDUNGEN["n_ohne_gans"]
    werte = [m.get(s, "") for s in ("de", "en", "es")] if isinstance(m, dict) else [str(m)]
    seite = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    pruefe("Texte: n_ohne_gans erklärt die neue Regel (de/en/es); Knopf „Gans ergänzen“ nur beim Hinweis k_ohne_gans",
           len(werte) == 3 and all("Gans" in w and ("Anfang" in w or "start" in w or "principio" in w) for w in werte)
           and seite.count("data-gans-ergaenzen") == 2 and 'm.code === "k_ohne_gans"' in seite
           and "if (j && j.gans_hinweis) toast(j.gans_hinweis);" in seite, werte)
    ideen, daten = tmp / "ideen-e46", tmp / "daten-e46"
    ideen.mkdir()
    daten.mkdir()
    env = dict(os.environ, PYTHONIOENCODING="utf-8", MGD_DATEN=str(daten), MGD_START_ID="test")
    env.pop("MGD_IM_PROZESS", None)
    r = subprocess.run([sys.executable, "-c", E46_PROZESS, str(p), str(ideen)], cwd=p, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    m = re.search(r"^#e46 (.*)$", r.stdout, re.M)
    if not m:
        print((r.stdout + r.stderr)[-3000:])
        pruefe("E46-Prozess lief durch", False, (r.stdout + r.stderr)[-600:])
        return
    for name, gut, detail in json.loads(m.group(1)):
        pruefe(name, gut, detail)


E47_PROZESS = r'''
import hashlib, io, json, os, sys, time
from pathlib import Path
sys.path.insert(0, sys.argv[1])
os.environ.pop("MGD_IM_PROZESS", None)
p, tmp = Path(sys.argv[1]), Path(sys.argv[2])
import gans_ui as ui, gans_lernkarten as gl, erweiterungen as erw, verlauf
from PIL import Image
gl.setze_sprache("de")
erw.IDEEN_DATEI, erw.IDEEN_ORDNER = tmp / "ideen.json", tmp / "ideen"
E = []
def ok(name, gut, detail=""):
    E.append([name, bool(gut), str(detail)[:700]])
KOPF = {}
def direkt(weg, daten=None, roh=None, abfrage="", methode="POST", gruppe=""):
    global KOPF
    koerper = roh if roh is not None else json.dumps(daten or {}).encode()
    k = {"X-GL-Sprache": "de", "Content-Type": "application/json"}
    if gruppe:
        k["X-GL-Gruppe"] = gruppe
    s, KOPF, i = ui.verarbeite(methode, weg, abfrage, koerper if methode == "POST" else b"", k)
    try:
        return s, json.loads(i)
    except ValueError:
        return s, {}
def stand():
    return json.loads(KOPF.get("X-MGD-Verlauf", "{}"))
def jpg(farbe):
    b = io.BytesIO(); Image.new("RGB", (900, 640), farbe).save(b, "JPEG", quality=90); return b.getvalue()
def sha(pfad):
    return hashlib.sha256(Path(pfad).read_bytes()).hexdigest() if Path(pfad).is_file() else None
def bild_stand():
    b = ui.pfade()[1]
    return {str(q.relative_to(b)): sha(q) for q in sorted(b.rglob("*")) if q.is_file()}
csv, bilder = ui.pfade()[0], ui.pfade()[1]
direkt("/api/status", methode="GET")
ok("Ohne Änderung: Kopfzeile X-MGD-Verlauf mit 0/0", stand() == {"z": 0, "w": 0, "za": "", "wa": ""}, stand())
# --- Karte speichern → zurück → vor ---
k0 = ui.karten_daten()["karten"][0]
v0 = csv.read_bytes()
s1, _ = direkt("/api/karte-speichern", {"bild": k0["bild"], "de": k0["de"] + " neu", "es": "nuevo"})
v1, st1 = csv.read_bytes(), stand()
s2, r2 = direkt("/api/rueckgaengig")
v2, st2 = csv.read_bytes(), stand()
s3, r3 = direkt("/api/wiederholen")
v3 = csv.read_bytes()
ok("Karte speichern → Rückgängig = Kartenliste Byte für Byte wie vorher, Wiederholen = wie nachher; Art „karte“, Zähler stimmen",
   s1 == s2 == s3 == 200 and v1 != v0 and v2 == v0 and v3 == v1 and st1["z"] == 1 and st1["za"] == "karte"
   and st2 == {"z": 0, "w": 1, "za": "", "wa": "karte"} and r2.get("art") == "karte" and r3.get("verlauf", {}).get("z") == 1
   and "karten" in r2, (s1, s2, s3, st1, st2))
# --- Karte aus der Liste + Bild weg (zwei Schritte) → zweimal zurück → alles da, _entfernt leer ---
vorher_bilder, vorher_csv = bild_stand(), csv.read_bytes()
liste = [k for k in ui.karten_daten()["karten"] if k["bild"] != k0["bild"]]
direkt("/api/karten", {"karten": liste})
s4, _ = direkt("/api/bild-weg", {"name": k0["bild"]})
nachher_bilder = bild_stand()
direkt("/api/rueckgaengig"); direkt("/api/rueckgaengig")
ok("Karte entfernen + Bild nach _entfernt: zweimal Rückgängig → Kartenliste und Bilder genau wie vorher (auch _entfernt)",
   s4 == 200 and nachher_bilder != vorher_bilder and bild_stand() == vorher_bilder and csv.read_bytes() == vorher_csv,
   (s4, sorted(set(nachher_bilder) ^ set(vorher_bilder)), sorted(set(bild_stand()) ^ set(vorher_bilder))))
direkt("/api/wiederholen"); direkt("/api/wiederholen")
ok("… und zweimal Wiederholen → wieder ohne Karte, Bild in _entfernt", bild_stand() == nachher_bilder
   and not any(k["bild"] == k0["bild"] for k in ui.karten_daten()["karten"]), sorted(bild_stand())[:6])
direkt("/api/rueckgaengig"); direkt("/api/rueckgaengig")
# --- Bilder vorbereiten: hinzufügen, Tippen (Gruppe), übernehmen → zurück holt den Entwurf wieder ---
ent = ui.entwurf_ordner()
s, d = direkt("/api/entwurf", roh=jpg((30, 160, 90)), abfrage="name=gans-wiese.jpg")
eid = d["id"]
z_vorher = stand()["z"]
direkt("/api/entwurf-pruefen", {"id": eid, "de": "Gans W", "es": ""}, gruppe=f"entwurf-{eid}")
direkt("/api/entwurf-pruefen", {"id": eid, "de": "Gans Wi", "es": ""}, gruppe=f"entwurf-{eid}")
direkt("/api/entwurf-pruefen", {"id": eid, "de": "Gans Wiese", "es": "prado"}, gruppe=f"entwurf-{eid}")
ok("Tippen im selben Entwurf (gleiche Gruppe) = ein Schritt", stand()["z"] == z_vorher + 1, (z_vorher, stand()))
s5, r5 = direkt("/api/entwurf-uebernehmen", {"id": eid, "de": "Gans Wiese", "es": "prado"})
neu = bilder / r5.get("name", "?")
da_nach = neu.is_file() and not (ent / f"{eid}.bild").exists()
direkt("/api/rueckgaengig")
zurueck = not neu.exists() and (ent / f"{eid}.bild").is_file() and json.loads((ent / f"{eid}.json").read_text(encoding="utf-8"))["de"] == "Gans Wiese"
direkt("/api/rueckgaengig")
getippt = json.loads((ent / f"{eid}.json").read_text(encoding="utf-8")).get("de")
direkt("/api/rueckgaengig")
ok("Karte übernehmen → Rückgängig: Karte + Bild weg, Entwurf wieder da (Text „Gans Wiese“); weiter zurück: Tippen, dann Hinzufügen",
   s5 == 200 and da_nach and zurueck and getippt == "Gans wiese" and not (ent / f"{eid}.bild").exists(), (s5, da_nach, zurueck, getippt))
direkt("/api/wiederholen"); direkt("/api/wiederholen"); direkt("/api/wiederholen")
ok("… dreimal Wiederholen → Karte wieder da", neu.is_file() and not (ent / f"{eid}.bild").exists(), neu.name)
# --- Ideen: anlegen, löschen → zurück ---
s, ri = direkt("/api/idee", {"de": "Gans Idee", "es": "idea"})
iid = ri.get("id")
erw.idee_bild_setzen  # vorhanden
s6, _ = direkt("/api/idee-bild", roh=jpg((250, 200, 0)), abfrage=f"id={iid}")
bild_idee = erw._idee_bildpfad(next(i for i in erw._ideen_lesen()["ideen"] if i["id"] == iid))
direkt("/api/idee-weg", {"id": iid})
weg = not any(i["id"] == iid for i in erw._ideen_lesen()["ideen"])
direkt("/api/rueckgaengig")
wieder = next((i for i in erw._ideen_lesen()["ideen"] if i["id"] == iid), None)
ok("Idee mit Bild löschen → Rückgängig: Idee samt Bild zurück", s6 == 200 and bool(bild_idee) and weg and bool(wieder)
   and bool(erw._idee_bildpfad(wieder)), (s6, bild_idee, weg, wieder))
# --- Gänse-Bild ---
gans = ui.GANS_ORDNER
s7, _ = direkt("/api/gans-bild", roh=jpg((255, 255, 255)))
da = any((gans / n).is_file() for n in ui.GANS_NAMEN)
direkt("/api/rueckgaengig")
ok("Gänse-Bild laden → Rückgängig: wieder die gezeichnete Gans", s7 == 200 and da and not any((gans / n).is_file() for n in ui.GANS_NAMEN), (s7, da))
# --- Konflikt: Datei inzwischen anders → nichts geändert, Verlauf leer ---
k1 = ui.karten_daten()["karten"][1]
direkt("/api/karte-speichern", {"bild": k1["bild"], "de": k1["de"], "es": "otro"})
fremd = csv.read_bytes() + b"\n"
csv.write_bytes(fremd)
s8, r8 = direkt("/api/rueckgaengig")
ok("Konflikt (Kartenliste von außen geändert): 409, nichts überschrieben, Verlauf geleert",
   s8 == 409 and csv.read_bytes() == fremd and stand()["z"] == 0 and stand()["w"] == 0 and r8.get("fehler"), (s8, r8, stand()))
s9, r9 = direkt("/api/rueckgaengig")
s10, _ = direkt("/api/wiederholen")
ok("Nichts im Verlauf: 409 mit freundlichem Text", s9 == 409 and s10 == 409 and r9.get("fehler"), (s9, r9))
# --- Grenze: höchstens MAX_SCHRITTE ---
for i in range(verlauf.MAX_SCHRITTE + 5):
    direkt("/api/karte-status", {"bild": k1["bild"], "geprueft": i % 2 == 0})
ok(f"Begrenzt: höchstens {verlauf.MAX_SCHRITTE} Schritte", stand()["z"] == verlauf.MAX_SCHRITTE == 30, stand())
# --- neuer Schritt nach Rückgängig löscht Wiederholen ---
direkt("/api/rueckgaengig")
w1 = stand()["w"]
direkt("/api/karte-status", {"bild": k1["bild"], "geprueft": False})
direkt("/api/karte-status", {"bild": k1["bild"], "geprueft": True})
ok("Neue Änderung nach Rückgängig: Wiederholen verfällt", w1 == 1 and stand()["w"] == 0, (w1, stand()))
# --- ohne Sicherung gelöscht → Verlauf geleert (nie halb zurück) ---
v = ui._verlauf()
opfer = next(q for q in bilder.glob("*.jpg"))
roh = opfer.read_bytes()
with v.schritt("test"):
    opfer.unlink()
ok("Datei ohne Sicherung gelöscht → Verlauf geleert (nie halb zurück)", v.info()["z"] == 0 and v.unvollstaendig == 1, v.info())
opfer.write_bytes(roh)
# --- Lesen ändert nichts am Verlauf; Lernen/Einstellungen sind keine Schritte ---
direkt("/api/karte-status", {"bild": k1["bild"], "geprueft": False})
z = stand()["z"]
direkt("/api/karten", methode="GET"); direkt("/api/sprache", {"sprache": "de"})
ok("Lesen und Spracheinstellung sind keine Schritte", stand()["z"] == z == 1, (z, stand()))
# --- Speicher: nur Kopien der geänderten Dateien; Beenden räumt auf ---
ordner = ui.pfade()[2] / ".verlauf"
groesse = sum(q.stat().st_size for q in ordner.rglob("*") if q.is_file())
v.leeren()
ok("Kopien im Ausgabeordner (.verlauf), leeren räumt alles weg", groesse > 0 and not ordner.exists(), groesse)
print("#e47 " + json.dumps(E, ensure_ascii=False))
'''


def test_rueckgaengig(p, tmp):
    """E47 (2.4): Rückgängig und Wiederholen überall – jede ändernde Anfrage (Karten, Bilder, Bilder vorbereiten, Ideen,
    Gänse-Bild) ist ein Schritt; Rückgängig/Wiederholen stellen die Dateien Byte für Byte her, Gruppen fassen Tippen
    zusammen, Konflikte ändern nichts, höchstens 30 Schritte; Oberfläche: ↶ ↷ in der Kopfzeile, Strg+Z/Strg+Y."""
    print("\n[E47] Rückgängig und Wiederholen")
    seite = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    g = (HIER / "gans_ui.py").read_text(encoding="utf-8")
    import ast
    wege = re.findall(r'"(/api/[a-z-]+)": "[a-z_]+"', g[g.index("VERLAUF_WEGE = {"):g.index("}", g.index("VERLAUF_WEGE = {"))])
    arten = set(re.findall(r'": "([a-z_]+)"', g[g.index("VERLAUF_WEGE = {"):g.index("}", g.index("VERLAUF_WEGE = {"))]))
    fehlt = [a for a in sorted(arten) if seite.count(f"vl_art_{a}:") != 3]
    pruefe("Kopfzeile ↶ ↷ (deaktiviert ohne Schritt), Strg+Z/Strg+Y nicht in Textfeldern/Fenstern/Lernsitzung, Stand aus jeder Antwort",
           'id="vl-zurueck"' in seite and 'id="vl-vor"' in seite and "verlaufAusKopf(r);" in seite
           and 'if (e.target.closest && e.target.closest("input, textarea, select, [contenteditable]")) return;' in seite
           and 'if (offenerDialog() || (ansicht() === "lernen" && LS)) return;' in seite
           and seite.count('"X-GL-Gruppe"') == 1 and 'S.vlGruppe = "alle-" + Date.now();' in seite, "")
    pruefe("Jede Schritt-Art hat einen Text in de/en/es; Wege mit eigenen Daten sind Schritte (Karten, Entwürfe, Ideen, Import, Wortliste)",
           not fehlt and seite.count("vl_art_aenderung:") == 3 and {"/api/karten", "/api/karte-speichern", "/api/entwurf",
                                                                   "/api/entwurf-uebernehmen", "/api/idee", "/api/idee-weg",
                                                                   "/api/import-uebernehmen", "/api/wortliste-uebernehmen",
                                                                   "/api/gans-bild", "/api/bild-weg"} <= set(wege)
           and "/api/lernen-bewerten" not in wege and "/api/einstellungen" not in wege, fehlt)
    baum = ast.parse((HIER / "verlauf.py").read_text(encoding="utf-8"))
    importe = {(n.names[0].name if isinstance(n, ast.Import) else n.module).split(".")[0] for n in ast.walk(baum)
               if isinstance(n, (ast.Import, ast.ImportFrom))}
    pruefe("verlauf.py nur Standardbibliothek (läuft auch in der Web-App)", importe <= {"__future__", "contextlib", "hashlib", "os",
                                                                                     "secrets", "shutil", "threading", "time", "pathlib"}, importe)
    ideen, daten = tmp / "ideen-e47", tmp / "daten-e47"
    ideen.mkdir()
    daten.mkdir()
    env = dict(os.environ, PYTHONIOENCODING="utf-8", MGD_DATEN=str(daten), MGD_START_ID="test")
    env.pop("MGD_IM_PROZESS", None)
    r = subprocess.run([sys.executable, "-c", E47_PROZESS, str(p), str(ideen)], cwd=p, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    m = re.search(r"^#e47 (.*)$", r.stdout, re.M)
    if not m:
        print((r.stdout + r.stderr)[-3000:])
        pruefe("E47-Prozess lief durch", False, (r.stdout + r.stderr)[-600:])
        return
    for name, gut, detail in json.loads(m.group(1)):
        pruefe(name, gut, detail)


E48_PROZESS = r'''
import hashlib, http.server, io, json, os, shutil, stat, sys, threading, time, zipfile
from pathlib import Path
sys.path.insert(0, sys.argv[1])
os.environ.pop("MGD_IM_PROZESS", None)
p, tmp = Path(sys.argv[1]), Path(sys.argv[2])
import aktualisieren as ak
E = []
def ok(name, gut, detail=""):
    E.append([name, bool(gut), str(detail)[:700]])
W = "Me-Goos-ta-Deutsch/"
def release(version, extra=None, weg=(), roh=None):
    dateien = {"Programm/starter.py": b"# starter\n", "Programm/gans_ui.py": b"# ui neu\n", "Programm/neu.py": b"x = 1\n",
               "Programm/gans_lernkarten.py": f'VERSION = "{version} (01.01.2030)"\n'.encode(),
               "Me Goos-ta Deutsch - Windows.cmd": b"@echo off\r\n", "Me Goos-ta Deutsch - Mac.command": b"#!/bin/bash\n",
               "Me Goos-ta Deutsch - Linux.sh": b"#!/bin/sh\n", "README.md": b"# neu\n"}
    dateien.update(extra or {})
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        for n, d in dateien.items():
            if n in weg:
                continue
            i = zipfile.ZipInfo((roh or W) + n)
            i.external_attr = (0o100755 if n.endswith((".sh", ".command")) else 0o100644) << 16
            z.writestr(i, d)
    return b.getvalue()
# --- Server wie GitHub-Releases (…/download/v<V>/…), auch mit Weiterleitung ---
DATEIEN = {}
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path.startswith("/weiter/"):
            self.send_response(302); self.send_header("Location", "http://boese.example/x.zip"); self.end_headers(); return
        d = DATEIEN.get(self.path)
        if d is None:
            self.send_response(404); self.end_headers(); return
        self.send_response(200); self.send_header("Content-Length", str(len(d))); self.end_headers(); self.wfile.write(d)
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
quelle = f"http://127.0.0.1:{srv.server_address[1]}/dl"
import signatur                                   # seit 2.5: SHA256SUMS.txt signiert – hier mit einem Testschlüssel
SEED, SID = bytes(range(32)), bytes(range(8))
os.environ["MGD_UPDATE_QUELLE"] = quelle
os.environ["MGD_UPDATE_TESTSCHLUESSEL"] = signatur.schluessel_text(SID, signatur.ed25519_oeffentlich(SEED))
def anbieten(version, z, summe=None):
    DATEIEN[f"/dl/v{version}/Me-Goos-ta-Deutsch-{version}.zip"] = z
    s = summe or hashlib.sha256(z).hexdigest()
    DATEIEN[f"/dl/v{version}/SHA256SUMS.txt"] = f"{s}  Me-Goos-ta-Deutsch-{version}.zip\n".encode()
    DATEIEN[f"/dl/v{version}/SHA256SUMS.txt.minisig"] = signatur.signiere(SEED, SID, DATEIEN[f"/dl/v{version}/SHA256SUMS.txt"],
                                                                           f"me-goos-ta-deutsch v{version}")
daten = tmp / "daten"
anbieten("9.9", release("9.9"))
meldungen = []
neu = ak.laden("9.9", quelle, daten, melde=meldungen.append)
b = ak.bereit(daten)
ok("Laden: SHA256SUMS + ZIP, Prüfsumme, entpackt nach update/neu, bereit.json mit Version", neu.is_dir() and (neu / "Programm" / "neu.py").is_file()
   and bool(b) and b["version"] == "9.9" and not list((daten / "update").glob("*.part")), (neu, b, meldungen[-2:]))
def fehler(fn):
    try:
        fn()
        return ""
    except ak.UpdateFehler as e:
        return str(e) or "?"
anbieten("9.8", release("9.8"), summe="0" * 64)
f_summe = fehler(lambda: ak.laden("9.8", quelle, daten, melde=lambda t: None))
f_404 = fehler(lambda: ak.laden("9.7", quelle, daten, melde=lambda t: None))
f_host = fehler(lambda: ak.laden("9.9", "https://boese.example/dl", daten))
f_weiter = fehler(lambda: ak._oeffne(f"http://127.0.0.1:{srv.server_address[1]}/weiter/x", ("127.0.0.1",)))
ok("Falsche Prüfsumme, fehlendes Release, fremder Host, Weiterleitung zu fremdem Host → abgelehnt; die schon geladene Version bleibt bereit",
   f_summe and f_404 and f_host and "boese.example" in f_weiter and (ak.bereit(daten) or {}).get("version") == "9.9", (f_summe, f_404, f_host, f_weiter))
def zip_pruefen(z, v="9.9"):
    pfad = tmp / "probe.zip"
    pfad.write_bytes(z)
    return fehler(lambda: ak.pruefe_zip(pfad, v))
proben = {"Ausbruch": release("9.9", {"../boese.py": b"x"}), "fremde Wurzel": release("9.9", roh="Anders/"),
          "Nutzerdaten": release("9.9", {"Programm/karten.csv": b"bild;de"}), "Bilder": release("9.9", {"Programm/bilder/a.jpg": b"j"}),
          "falsche Version": release("9.9"), "Pflicht fehlt": release("9.9", weg=("Programm/starter.py",))}
erg = {k: zip_pruefen(z, "9.6" if k == "falsche Version" else "9.9") for k, z in proben.items()}
b2 = io.BytesIO()
with zipfile.ZipFile(b2, "w") as z:
    i = zipfile.ZipInfo(W + "Programm/link"); i.external_attr = 0o120777 << 16; z.writestr(i, "/etc/passwd")
erg["Link"] = zip_pruefen(b2.getvalue())
ok("ZIP-Prüfung: Ausbruch, fremde Wurzel, Nutzerdaten, Bilder, falsche Version, fehlende Pflichtdatei, symbolischer Link → abgelehnt",
   all(erg.values()) and zip_pruefen(release("9.9")) == "", erg)
# --- Anwenden: ersetzt Programmdateien, eigene Daten bleiben ---
ziel = tmp / "installiert" / "Me-Goos-ta-Deutsch"
alt = {"Programm/starter.py": b"# starter alt\n", "Programm/gans_ui.py": b"# ui alt\n", "Programm/gans_lernkarten.py": b'VERSION = "2.4 (x)"\n',
       "Programm/alt_nur.py": b"y = 2\n", "README.md": b"# alt\n"}
nutzer = {"Programm/karten.csv": b"bild;de;es;notiz\na.jpg;Gans a;b;\n", "Programm/bilder/a.jpg": b"bild", "Programm/ideen.json": b"{}",
          "Programm/ui_einstellungen.json": b'{"sprache": "de"}', "Programm/lernstand.json": b"{}", "Programm/ausgabe/x.pdf": b"%PDF",
          "Programm/assets/gans_hintergrund.jpg": b"gans"}
for n, d in {**alt, **nutzer}.items():
    (ziel / n).parent.mkdir(parents=True, exist_ok=True)
    (ziel / n).write_bytes(d)
n_geaendert = ak.anwenden(neu, ziel, daten / "update" / "alt")
ok("Anwenden: Programmdateien ersetzt, neue dazu, alte Zusatzdatei bleibt, eigene Daten Byte für Byte unverändert",
   (ziel / "Programm" / "gans_ui.py").read_bytes() == b"# ui neu\n" and (ziel / "Programm" / "neu.py").is_file()
   and (ziel / "Programm" / "alt_nur.py").read_bytes() == b"y = 2\n" and (ziel / "Me Goos-ta Deutsch - Linux.sh").is_file()
   and all((ziel / n).read_bytes() == d for n, d in nutzer.items()) and n_geaendert == 8, n_geaendert)
if os.name != "nt":
    ok("Startdateien danach ausführbar (0755)", all(os.stat(ziel / n).st_mode & 0o111 for n in ("Me Goos-ta Deutsch - Linux.sh", "Me Goos-ta Deutsch - Mac.command")))
# --- Fehler mitten drin → alles zurück ---
ziel2 = tmp / "installiert2" / "Me-Goos-ta-Deutsch"
for n, d in {**alt, **nutzer}.items():
    (ziel2 / n).parent.mkdir(parents=True, exist_ok=True)
    (ziel2 / n).write_bytes(d)
vorher = {str(q.relative_to(ziel2)): q.read_bytes() for q in ziel2.rglob("*") if q.is_file()}
echt, zahl = shutil.copyfile, [0]
def kaputt(a, b, *x, **y):
    zahl[0] += 1
    if zahl[0] == 4:
        raise OSError("Platte voll (Test)")
    return echt(a, b, *x, **y)
ak.shutil.copyfile = kaputt
try:
    f_halb = ""
    ak.anwenden(neu, ziel2, tmp / "sich2")
except OSError as e:
    f_halb = str(e)
finally:
    ak.shutil.copyfile = echt
nachher = {str(q.relative_to(ziel2)): q.read_bytes() for q in ziel2.rglob("*") if q.is_file() and not q.name.endswith(".tmp")}
ok("Fehler mitten im Ersetzen → alles wie vorher (neue Dateien wieder weg)", f_halb and nachher == vorher, (f_halb, sorted(set(nachher) ^ set(vorher))))
# --- Nie den Entwicklungsordner oder ein Git-Verzeichnis ---
dev = tmp / "arbeit" / "Me-Goos-ta-Deutsch"
(dev / "Programm").mkdir(parents=True)
for n in ("starter.py", "gans_ui.py"):
    (dev / "Programm" / n).write_text("#", encoding="utf-8")
ok_dev1 = ak.programm_ordner_ok(dev)
(dev.parent / "bau_release.py").write_text("#", encoding="utf-8")
ok_dev2 = ak.programm_ordner_ok(dev)
(dev.parent / "bau_release.py").unlink()
(dev / ".git").mkdir()
ok_dev3 = ak.programm_ordner_ok(dev)
f_dev = fehler(lambda: ak.anwenden(neu, dev, tmp / "sich3"))
ok("Programmordner-Schutz: Entwicklungsordner (bau_release.py daneben) und Git-Verzeichnis werden nie ersetzt",
   ok_dev1 and not ok_dev2 and not ok_dev3 and f_dev == "ziel", (ok_dev1, ok_dev2, ok_dev3, f_dev))
# --- Ablauf nach „Jetzt neu starten“ (ohne echten Start) ---
ziel3 = tmp / "installiert3" / "Me-Goos-ta-Deutsch"
for n, d in {**alt, **nutzer}.items():
    (ziel3 / n).parent.mkdir(parents=True, exist_ok=True)
    (ziel3 / n).write_bytes(d)
e1 = ak.anwenden_und_starten(daten, ziel3, 0, starten=False)
gespeichert = json.loads((daten / "update" / "ergebnis.json").read_text(encoding="utf-8"))
e2 = ak.anwenden_und_starten(daten, ziel3, 0, starten=False)
ok("Ablauf: ersetzt, ergebnis.json (ok, Version), räumt neu/alt/bereit auf; ohne bereite Version → Fehler im Ergebnis",
   e1["ok"] and e1["version"] == "9.9" and gespeichert["ok"] and not (daten / "update" / "neu").exists()
   and not (daten / "update" / "bereit.json").exists() and not e2["ok"] and e2["fehler"]
   and (ziel3 / "Programm" / "gans_lernkarten.py").read_bytes().startswith(b'VERSION = "9.9'), (e1, e2))
ok("Startdatei je System; Warten auf eine beendete Prozess-ID kehrt sofort zurück",
   ak.startdatei(ziel3).name.startswith("Me Goos-ta Deutsch - ") and ak.warte_auf_ende(0) and ak.warte_auf_ende(999999, 2), ak.startdatei(ziel3).name)
if os.name != "nt":
    import subprocess as sp
    zombie = sp.Popen(["true"])
    time.sleep(0.5)
    ok("Beendeter, nicht abgeholter Prozess (Zombie, z. B. Container ohne Init) zählt als beendet; der eigene lebt",
       not ak._lebt(zombie.pid) and ak._lebt(os.getpid()), zombie.pid)
    zombie.wait()
srv.shutdown()
# --- Oberfläche: /api/update ---
import gans_ui as ui, gans_lernkarten as gl
gl.setze_sprache("de")
def direkt(daten_, am_handy=False):
    s, k, i = ui.verarbeite("POST", "/api/update", "", json.dumps(daten_).encode(), {"X-GL-Sprache": "de", "Content-Type": "application/json"}, am_handy=am_handy)
    return s, json.loads(i)
info = ui.status_info()["update"]
h = direkt({"aktion": "laden", "version": "9.9"}, am_handy=True)
k = direkt({"aktion": "laden", "version": "1.0"})
x = direkt({"aktion": "laden", "version": "9.9; rm"})
a = direkt({"aktion": "anwenden"})
(ui.uebersetzer.daten_ordner() / "update").mkdir(parents=True, exist_ok=True)
(ui.uebersetzer.daten_ordner() / "update" / "ergebnis.json").write_text(json.dumps({"ok": True, "version": "9.9"}), encoding="utf-8")
mit = ui.status_info()["update"]["ergebnis"]
g = direkt({"aktion": "gesehen"})
ui.im_browser = lambda: True
app = ui.update_info()
ok("/api/update: Handy-Zugang 403, nicht neuer → 409, ungültige Version → 400, anwenden ohne Download → 409; Status meldet Ergebnis einmal; Web-App: nicht möglich",
   info["moeglich"] is True and info["bereit"] == "" and h[0] == 403 and k[0] == 409 and x[0] == 400 and a[0] == 409
   and mit and mit["ok"] and mit["version"] == "9.9" and g[0] == 200 and g[1]["ergebnis"] is None and app["moeglich"] is False,
   (info, h[0], k, x[0], a, mit, g[1], app))
print("#e48 " + json.dumps(E, ensure_ascii=False))
'''


def test_update(p, tmp):
    """E48 (2.4): neue Version direkt im Programm – laden (nur GitHub bzw. Test-Server, Prüfsumme, ZIP-Prüfung), anwenden
    (ersetzt Programmdateien im selben Ordner, eigene Daten bleiben, Fehler → alles zurück, nie Entwicklungsordner),
    /api/update nur am Rechner; Knöpfe in Werkzeuge, Über und Fußzeile."""
    print("\n[E48] Update direkt im Programm")
    seite = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    import ast
    baum = ast.parse((HIER / "aktualisieren.py").read_text(encoding="utf-8"))
    oben = {(n.names[0].name if isinstance(n, ast.Import) else n.module).split(".")[0] for n in baum.body
            if isinstance(n, (ast.Import, ast.ImportFrom))}
    bau = HIER.parent.parent / "werkstatt" / "bau_webapp.py"                      # nur im Arbeitsordner: die App braucht das Modul nicht
    pruefe("aktualisieren.py: oben nur Standardbibliothek (anwenden läuft ohne Pakete), kein api.github.com; nicht in der Web-App",
           oben <= {"__future__", "argparse", "hashlib", "json", "os", "re", "shutil", "subprocess", "sys", "time", "urllib", "zipfile", "pathlib"}
           and "api.github.com" not in (HIER / "aktualisieren.py").read_text(encoding="utf-8")
           and (not bau.is_file() or '"aktualisieren.py", "signatur.py"}' in bau.read_text(encoding="utf-8")), oben)
    pruefe("Oberfläche: „Nach neuer Version suchen“ in Werkzeuge, Über und Fußzeile (nur am Rechner); „Jetzt aktualisieren“ nur, wenn möglich",
           seite.count("data-nv-knopf") >= 3 and 'id="update-bereich"' in seite and "data-nv-fuss" in seite
           and "${!AM_HANDY && !AM_APP ? `<br><button type=\"button\"" in seite and "u.moeglich ? `<p class=\"knopfzeile\"><button class=\"knopf haupt\"" in seite
           and 'L.art === "update"' in seite and 'id="update-fenster"' in seite, "")
    daten = tmp / "daten-e48"
    daten.mkdir()
    arbeit = tmp / "e48"
    arbeit.mkdir()
    env = dict(os.environ, PYTHONIOENCODING="utf-8", MGD_DATEN=str(daten), MGD_START_ID="test")
    env.pop("MGD_IM_PROZESS", None)
    r = subprocess.run([sys.executable, "-c", E48_PROZESS, str(p), str(arbeit)], cwd=p, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    m = re.search(r"^#e48 (.*)$", r.stdout, re.M)
    if not m:
        print((r.stdout + r.stderr)[-3000:])
        pruefe("E48-Prozess lief durch", False, (r.stdout + r.stderr)[-600:])
        return
    for name, gut, detail in json.loads(m.group(1)):
        pruefe(name, gut, detail)


def test_oberflaeche_24():
    """E49 (2.4): Vorher/Nachher-Vergleich legt beim Klicken mit leichtem Ziehen kein Bild mehr an (Fund 2.3) – Bilder dort
    nicht ziehbar, alles aus der Seite selbst Gezogene ist nie eine neue Datei; neue Texte in de/en/es."""
    print("\n[E49] Oberfläche 2.4: Vergleich ohne Bild-Anlegen, Texte")
    seite = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    i = seite.index("function zeigeVergleich(k) {")
    vergleich = seite[i:seite.index("\n}\n", i)]
    j = seite.index("let innenZieh = false;")
    schutz = seite[j:seite.index("let ziehZaehler = 0;", j)]
    pruefe("Vergleich: Bilder draggable=false + ohne Zeiger-Ereignisse, dragstart verhindert, Regler mit pointercancel",
           vergleich.count('draggable="false"') == 3 and '$("#vergleich-inhalt").addEventListener("dragstart", e => e.preventDefault());' in seite
           and "pointer-events: none; }" in seite[seite.index(".vergleich-bild img {"):][:200] and 'box.addEventListener("pointercancel", auf);' in seite, "")
    pruefe("Ziehen aus der Seite selbst ist nie eine neue Datei: Schutz vor Ablage und Zieh-Zielen (erste Zuhörer, stoppt sofort)",
           'document.addEventListener("dragstart", e => { innenZieh = !e.defaultPrevented; });' in schutz
           and "e.stopImmediatePropagation();" in schutz and 'if (typ === "dragover" || typ === "drop") { e.preventDefault();' in schutz
           and j < seite.index("const ZIEH_ZIELE = {};") and j < seite.index('window.addEventListener("drop", e => {'), "")
    txt = {"de": [], "en": [], "es": []}
    a = seite.index("const TXT = {")
    for m in re.finditer(r"\n(de|en|es)\s*:\s*\{", seite[a:seite.index("\n};", a)]):
        txt[m.group(1)] += js_schluessel(seite, a + m.end() - 1)
    for m in re.finditer(r"Object\.assign\(TXT\.(de|en|es),\s*\{", seite):
        txt[m.group(1)] += js_schluessel(seite, m.end() - 1)
    noetig = ["nv_fuss", "h_nv_fuss", "up_titel", "up_unter", "up_jetzt", "up_erklaerung", "up_laedt", "up_geladen", "up_bereit_text",
              "up_neustart", "up_neustart_kurz", "up_zieht_um_titel", "up_zieht_um", "up_ok", "up_fehler", "up_nicht_moeglich",
              "vl_gruppe", "vl_zurueck_kurz", "vl_vor_kurz", "h_vl_zurueck", "h_vl_vor", "h_vl_zurueck_was", "h_vl_vor_was",
              "vl_zurueck", "vl_vor", "vl_zurueck_ok", "vl_vor_ok", "gans_ergaenzen_knopf", "h_gans_ergaenzen"]
    fehlt = [f"{s}.{k}" for s in txt for k in noetig if k not in txt[s]]
    pruefe("Neue Texte (Update, Rückgängig, Gans ergänzen) in de/en/es", not fehlt, fehlt[:8])


def test_github_auftritt(tmp):
    """E50 (2.5): Community-Dateien für GitHub (`ci/github/` → `.github/`): SECURITY, CONTRIBUTING, CODE_OF_CONDUCT, Issue-
    Formulare, PR-Vorlage vorhanden und nicht leer, mit deutscher und spanischer Kurzfassung; Links nur auf dieses Repo bzw.
    web_adresse.txt (Namensnennung des Contributor Covenant ausgenommen); keine E-Mail-Adressen, nirgends „Warning“;
    repo_einstellungen.py --probe liefert Stufe 1 vollständig ohne Netz. Ohne die Dateien des Arbeitsordners entfallen alle 5."""
    print("\n[E50] GitHub: Community-Dateien und Repo-Einstellungen")
    arbeit = HIER.parent.parent
    ci = arbeit / ".github"
    skript = arbeit / "werkstatt" / "repo_einstellungen.py"
    md = {n: ci / n for n in ("SECURITY.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "PULL_REQUEST_TEMPLATE.md")}
    formulare = {n: ci / "ISSUE_TEMPLATE" / n for n in ("bug_report.yml", "feature_request.yml", "config.yml")}
    if not (ci / "workflows").is_dir() or not skript.is_file():
        print("  (.github/ und werkstatt/repo_einstellungen.py liegen nur im Quellbaum – Prüfungen entfallen)")
        return
    texte = {n: (p.read_text(encoding="utf-8") if p.is_file() else "") for n, p in {**md, **formulare}.items()}
    leer = [n for n, t in texte.items() if len(t.strip()) < 200]
    ohne_kurz = [n for n in ("SECURITY.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md")
                 if "**Deutsch (kurz):**" not in texte[n] or "**Español (breve):**" not in texte[n]]
    pruefe("Community-Dateien vorhanden und nicht leer (SECURITY, CONTRIBUTING, CODE_OF_CONDUCT, PR-Vorlage, 3 Issue-Dateien), "
           "Kurzfassung de/es", not leer and not ohne_kurz, f"{leer} {ohne_kurz}")
    adresse = (HIER / "web_adresse.txt").read_text(encoding="utf-8").strip().splitlines()[0].strip()
    m = re.match(r"^https://([a-z0-9-]+)\.github\.io/([A-Za-z0-9._-]+)/$", adresse)
    konto, repo = m.group(1), m.group(2)
    fremd = []
    for n, t in texte.items():
        for url in re.findall(r"https?://[^\s)>\]\"'`]+", t):
            eigen = (url.lower().startswith(f"https://github.com/{konto}/{repo}/".lower()) or url.startswith(adresse))
            nennung = n == "CODE_OF_CONDUCT.md" and re.match(r"https://(www\.contributor-covenant\.org|creativecommons\.org)/", url)
            if not (eigen or nennung):
                fremd.append(f"{n}: {url}")
    sicherheit = texte["SECURITY.md"] + texte["config.yml"]
    pruefe("Links nur auf dieses Repository bzw. web_adresse.txt; Meldeweg „Report a vulnerability“ (security/advisories/new)",
           not fremd and f"github.com/{konto}/{repo}/security/advisories/new".lower() in sicherheit.lower()
           and "Report a vulnerability" in texte["SECURITY.md"], fremd[:5])
    mails = [f"{n}: {x}" for n, t in texte.items() for x in re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", t)]
    warn = [n for n, t in texte.items() if re.search(r"(?i)\bwarn(ing|ung)\b", t)]
    pruefe("Keine E-Mail-Adressen und nirgends „Warning/Warnung“ in den Community-Dateien", not mails and not warn, f"{mails[:3]} {warn}")
    form_fehler = []
    for n in ("bug_report.yml", "feature_request.yml"):
        t = texte[n]
        if not (re.search(r"^name: \S", t, re.M) and re.search(r"^description: \S", t, re.M) and re.search(r"^body:\n", t, re.M)
                and len(re.findall(r"^  - type: (markdown|input|textarea|dropdown|checkboxes)$", t, re.M)) >= 3
                and re.search(r"^    validations:\n      required: true$", t, re.M) and "\t" not in t and "\r" not in t):
            form_fehler.append(n)
    c = texte["config.yml"]
    if not (re.search(r"^blank_issues_enabled: false$", c, re.M) and c.count("  - name: ") == 3 and c.count("    url: ") == 3
            and c.count("    about: ") == 3):
        form_fehler.append("config.yml")
    pruefe("Issue-Formulare mit name, description, body (≥ 3 Felder, Pflichtfelder); config.yml: leere Issues aus, 3 Links",
           not form_fehler, form_fehler)
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1", GH_TOKEN="",
               HTTPS_PROXY="http://127.0.0.1:9", HTTP_PROXY="http://127.0.0.1:9")     # kein Netz
    vorher = sorted((p.name, p.stat().st_mtime) for p in arbeit.iterdir())
    r1 = subprocess.run([sys.executable, str(skript), "--probe"], env=env, cwd=str(tmp), capture_output=True, text=True,
                        encoding="utf-8", errors="replace", timeout=120)
    r2 = subprocess.run([sys.executable, str(skript), "--probe", "--stufe", "2"], env=env, cwd=str(tmp), capture_output=True,
                        text=True, encoding="utf-8", errors="replace", timeout=120)
    nachher = sorted((p.name, p.stat().st_mtime) for p in arbeit.iterdir())
    mp = re.search(r"^#plan (.*)$", r1.stdout, re.M)
    plan = json.loads(mp.group(1)) if mp else {}
    schritte = {s["id"]: s["soll"] for s in plan.get("schritte", [])}
    regel = schritte.get("ruleset") or {}
    mp2 = re.search(r"^#plan (.*)$", r2.stdout, re.M)
    s2 = {s["id"]: s["soll"] for s in (json.loads(mp2.group(1)) if mp2 else {}).get("schritte", [])}
    pruefe("repo_einstellungen.py --probe: Stufe 1 vollständig (Topics, Sicherheitsmeldungen, Dependabot, Secret Scanning, CodeQL, "
           "Ruleset main + gh-pages ohne ci und ohne Umgehung, Probe aus), ohne Netz, schreibt nichts; Stufe 2 (seit G06): Tags v* "
           "nicht löschen/verschieben, unveränderliche Releases, signierte Commits auf main + gh-pages (ci frei), ohne Umgehung",
           r1.returncode == 0 and plan.get("konto") == konto and plan.get("stufe") == 1
           and set(schritte) == {"topics", "wiki_discussions", "private_meldungen", "dependabot_warnungen", "secret_scanning",
                                 "codeql", "ruleset", "probe_aus"}
           and {"german", "flashcards", "spaced-repetition", "anki", "pwa", "python", "offline"} <= set(schritte.get("topics", []))
           and len(schritte.get("topics", [])) <= 20 and all(re.fullmatch(r"[a-z0-9][a-z0-9-]{0,49}", t) for t in schritte.get("topics", []))
           and sorted(regel.get("include", [])) == ["refs/heads/gh-pages", "refs/heads/main"] and regel.get("umgehung") == []
           and sorted(regel.get("regeln", [])) == ["deletion", "non_fast_forward"]
           and r2.returncode == 0 and set(s2) == {"tags", "unveraenderlich", "signierte_commits"} and s2["unveraenderlich"] is True
           and s2["tags"]["include"] == ["refs/tags/v*"] and sorted(s2["tags"]["regeln"]) == ["deletion", "non_fast_forward", "update"]
           and sorted(s2["signierte_commits"]["include"]) == ["refs/heads/gh-pages", "refs/heads/main"]
           and s2["signierte_commits"]["regeln"] == ["required_signatures"]
           and all(x["umgehung"] == [] for x in (s2["tags"], s2["signierte_commits"])) and vorher == nachher,
           (r1.stdout + r1.stderr + r2.stderr)[-400:])


E51_SEED_TEXT = b"mgd-e51-testschluessel"                     # fester Testschlüssel – nie für echte Releases
E51_PUB = "RWRNR0RURVNUMVWdV7pIrbUszVhp4/CfwIKp9n8kJklndqMXDIeh10vE"
E51_MINISIG = ("untrusted comment: signature from E51 test key\nRURNR0RURVNUMUREQIK5g/61YToRyu4lf6616jFNlvM4vwDdDoWyeJVbdQKUnGRnGp+gYZtH+04H+"
               "enwqrq4NGPOgci7Af88xAg=\ntrusted comment: me-goos-ta-deutsch v9.9\n02apr68183z/JONsDjllgwWDkN0M2tL9Lu1H8pTyxSI/0xpZvkZllGmtUFrQ"
               "Lgaij8tz3wo69OmWsCBJqYZYAQ==\n")


def test_signatur(tmp):
    """E51 (2.5): Signierte Releases und Updates – Ed25519 nach RFC 8032 (Testvektoren 1–3), minisign-Format mit festem
    Testschlüssel, Ablehnung von geänderten Summen/Signaturen/Kommentaren, fremdem Schlüssel, falscher Version; laden()
    nur mit gültiger Signatur (Testschlüssel nur mit 127.0.0.1); signiere_release.py, veroeffentliche_release.py
    (Signatur Pflicht, vor jedem Netz) und „Echtheit prüfen“ auf der Download-Seite (ohne Arbeitsordner entfallen 4)."""
    print("\n[E51] Signierte Releases und Updates")
    import base64
    import hashlib
    import http.server
    import threading
    import signatur as sg
    vektoren = [("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
                 "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a", "",
                 "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"),
                ("4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb",
                 "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c", "72",
                 "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00"),
                ("c5aa8df43f9f837bedb7442f31dcb7b166d38535076f094b85ce3a2e0b4458f7",
                 "fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025", "af82",
                 "6291d657deec24024827e69c3abe01a30ce548a284743a445e3680d7db5ac3ac18ff9b538d16f290ae67f760984dc6594a7c15e9716ed28dc027beceea1ec40a")]
    t0 = time.time()
    rfc = [(sg.ed25519_oeffentlich(bytes.fromhex(sk)).hex() == pk, sg.ed25519_signiere(bytes.fromhex(sk), bytes.fromhex(m)).hex() == s,
            sg.ed25519_pruefe(bytes.fromhex(pk), bytes.fromhex(m), bytes.fromhex(s)),
            not sg.ed25519_pruefe(bytes.fromhex(pk), bytes.fromhex(m) + b"!", bytes.fromhex(s))) for sk, pk, m, s in vektoren]
    pruefe("Ed25519 = RFC 8032 Testvektoren 1–3 (öffentlicher Schlüssel, Signatur, Prüfung; veränderte Nachricht abgelehnt)",
           all(all(r) for r in rfc), rfc)
    seed, sid = hashlib.sha256(E51_SEED_TEXT).digest(), b"MGDTEST1"
    summen = b"0" * 64 + b"  Me-Goos-ta-Deutsch-9.9.zip\n"
    test_k = [("test", *sg.schluessel_lesen(E51_PUB))]
    fest = E51_MINISIG.encode("utf-8")
    ok_fest = sg.pruefe(summen, fest, test_k, "me-goos-ta-deutsch v9.9")
    pruefe("minisign-Format: fester Testschlüssel (.pub „RW…“, ID) und feste .minisig (ED + trusted comment) gültig, Signieren deterministisch",
           sg.signiere(seed, sid, summen, "me-goos-ta-deutsch v9.9", "signature from E51 test key") == fest
           and sg.schluessel_text(sid, sg.ed25519_oeffentlich(seed)) == E51_PUB and ok_fest["id"] == sg.schluessel_id(sid)
           and sg.pub_datei(sid, sg.ed25519_oeffentlich(seed)).startswith(f"untrusted comment: minisign public key {sg.schluessel_id(sid)}\n"),
           ok_fest)

    def grund(daten, ms, k=test_k, kommentar="me-goos-ta-deutsch v9.9"):
        try:
            sg.pruefe(daten, ms, k, kommentar)
            return ""
        except sg.SignaturFehler as f:
            return str(f) or "?"
    z = fest.decode("utf-8").split("\n")
    sig_roh = bytearray(base64.b64decode(z[1]))
    sig_roh[20] ^= 1
    anders_sig = "\n".join([z[0], base64.b64encode(bytes(sig_roh)).decode(), *z[2:]]).encode()
    anders_kom = "\n".join([z[0], z[1], "trusted comment: me-goos-ta-deutsch v9.99", *z[3:]]).encode()
    fremd = [("fremd", b"MGDTEST2", sg.ed25519_oeffentlich(hashlib.sha256(b"fremd").digest()))]
    roh = sg.signiere(seed, sid, summen, "me-goos-ta-deutsch v9.9").replace(b"RUR", b"RWR", 1)       # „Ed“ ohne Vorhash
    s_ed = sg.ed25519_signiere(seed, summen)                    # älteres minisign: „Ed“ ohne Vorhash
    legacy = (f"untrusted comment: alt\n{base64.b64encode(b'Ed' + sid + s_ed).decode()}\ntrusted comment: x\n"
              f"{base64.b64encode(sg.ed25519_signiere(seed, s_ed + b'x')).decode()}\n").encode()
    abgelehnt = {"Summen geändert": grund(summen.replace(b"0", b"1", 1), fest), "Signatur geändert": grund(summen, anders_sig),
                 "Kommentar geändert": grund(summen, anders_kom), "fremder Schlüssel": grund(summen, fest, fremd),
                 "falsche Version": grund(summen, fest, kommentar="me-goos-ta-deutsch v9.8"), "leer": grund(summen, b""),
                 "kein minisign": grund(summen, b"hallo\n"), "Algorithmus Ed mit ED-Signatur": grund(summen, roh)}
    pruefe("Abgelehnt: geänderte Summen, Signatur, trusted comment; fremder Schlüssel; falsche Version; leer/kaputt; falscher "
           "Algorithmus (älteres „Ed“ ohne Vorhash gültig)",
           all(abgelehnt.values()) and abgelehnt["fremder Schlüssel"] == "fremder_schluessel"
           and abgelehnt["falsche Version"] == "falscher_kommentar" and abgelehnt["Kommentar geändert"] == "kommentar_ungueltig"
           and grund(summen, legacy, kommentar="x") == "", abgelehnt)
    v = sg.vertraut()
    quelltext = (HIER / "signatur.py").read_text(encoding="utf-8")
    import ast
    oben = {(n.names[0].name if isinstance(n, ast.Import) else n.module).split(".")[0] for n in ast.parse(quelltext).body
            if isinstance(n, (ast.Import, ast.ImportFrom))}
    pruefe("Vertraute Schlüssel: Haupt + Reserve (verschiedene IDs, echte Schlüssel), trusted comment „me-goos-ta-deutsch v<V>“, "
           "nur Standardbibliothek, kein privater Schlüssel im Quelltext",
           [k[0] for k in v] == ["haupt", "reserve"] and v[0][1] != v[1][1] and all(len(k[2]) == 32 for k in v)
           and sg.KOMMENTAR.format(version="2.5") == "me-goos-ta-deutsch v2.5" and oben <= {"__future__", "base64", "hashlib"}
           and "secret key" not in quelltext.lower() and not re.search(r"[0-9a-fA-F]{64}", quelltext), (v, oben))
    # --- laden(): nur mit gültiger Signatur ---
    import aktualisieren as ak
    dateien = {}

    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            d = dateien.get(self.path)
            self.send_response(200 if d is not None else 404)
            self.send_header("Content-Length", str(len(d or b"")))
            self.end_headers()
            self.wfile.write(d or b"")
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    quelle = f"http://127.0.0.1:{srv.server_address[1]}/dl"
    import io
    import zipfile

    def release(v_, signatur="eigen"):
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w") as zz:
            for n, d in {"Programm/starter.py": b"#", "Programm/gans_ui.py": b"#", "Me Goos-ta Deutsch - Windows.cmd": b"@echo off\r\n",
                         "Programm/gans_lernkarten.py": f'VERSION = "{v_} (01.01.2030)"\n'.encode(),
                         "Me Goos-ta Deutsch - Mac.command": b"#!/bin/bash\n", "Me Goos-ta Deutsch - Linux.sh": b"#!/bin/sh\n"}.items():
                zz.writestr("Me-Goos-ta-Deutsch/" + n, d)
        zd = b.getvalue()
        s_ = f"{hashlib.sha256(zd).hexdigest()}  Me-Goos-ta-Deutsch-{v_}.zip\n".encode()
        dateien[f"/dl/v{v_}/Me-Goos-ta-Deutsch-{v_}.zip"] = zd
        dateien[f"/dl/v{v_}/SHA256SUMS.txt"] = s_
        if signatur == "eigen":
            dateien[f"/dl/v{v_}/SHA256SUMS.txt.minisig"] = sg.signiere(seed, sid, s_, f"me-goos-ta-deutsch v{v_}")
        elif signatur == "fremd":
            dateien[f"/dl/v{v_}/SHA256SUMS.txt.minisig"] = sg.signiere(hashlib.sha256(b"fremd").digest(), b"MGDTEST2", s_,
                                                                       f"me-goos-ta-deutsch v{v_}")
        elif signatur == "alt":                                 # gültig signiert, aber für eine andere Version
            dateien[f"/dl/v{v_}/SHA256SUMS.txt.minisig"] = sg.signiere(seed, sid, s_, "me-goos-ta-deutsch v8.0")
    for v_, art in (("9.1", "eigen"), ("9.2", "keine"), ("9.3", "fremd"), ("9.4", "alt")):
        release(v_, art)
    alt_env = {k: os.environ.get(k) for k in ("MGD_UPDATE_QUELLE", "MGD_UPDATE_TESTSCHLUESSEL", "MGD_SPRACHE")}

    def laden(v_, mit_quelle=True):
        os.environ["MGD_UPDATE_TESTSCHLUESSEL"] = E51_PUB
        os.environ["MGD_SPRACHE"] = "de"
        if mit_quelle:
            os.environ["MGD_UPDATE_QUELLE"] = quelle
        else:
            os.environ.pop("MGD_UPDATE_QUELLE", None)
        try:
            ak.laden(v_, quelle, tmp / f"e51-daten-{v_}-{mit_quelle}", melde=lambda t: None)
            return ""
        except ak.UpdateFehler as f:
            return str(f) or "?"
    try:
        f_ok = laden("9.1")
        f_ohne, f_fremd, f_alt = laden("9.2"), laden("9.3"), laden("9.4")
        f_test_ohne = laden("9.1", mit_quelle=False)
        f_aelter = laden("1.0")
        env_p = dict(os.environ, PYTHONIOENCODING="utf-8", MGD_UPDATE_QUELLE=quelle, MGD_UPDATE_TESTSCHLUESSEL=E51_PUB,
                     MGD_SPRACHE="de")
        als_prozess = subprocess.run([sys.executable, "-u", str(HIER / "aktualisieren.py"), "--laden", "9.1", "--quelle", quelle,
                                      "--daten", str(tmp / "e51-prozess")], cwd=str(tmp), env=env_p, capture_output=True, text=True,
                                     encoding="utf-8", errors="replace", timeout=120)
    finally:
        for k, w in alt_env.items():
            if w is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = w
        srv.shutdown()
    pruefe("laden(): gültig signiert → bereit; ohne .minisig, fremder Schlüssel, Signatur einer anderen Version → abgelehnt (Achtung …)",
           f_ok == "" and (ak.bereit(tmp / "e51-daten-9.1-True") or {}).get("version") == "9.1" and "SHA256SUMS.txt.minisig" in f_ohne
           and "fremder_schluessel" in f_fremd and "falscher_kommentar" in f_alt
           and all(x.startswith("Achtung") for x in (f_ohne, f_fremd, f_alt)) and not (tmp / "e51-daten-9.3-True" / "update" / "neu").exists(),
           (f_ok, f_ohne, f_fremd, f_alt))
    pruefe("Testschlüssel gilt nur mit MGD_UPDATE_QUELLE=http://127.0.0.1:… (sonst nur die echten Schlüssel); nur neuere Version als diese",
           "fremder_schluessel" in f_test_ohne and "nicht neuer" in f_aelter
           and len(ak.schluessel_fuer("https://github.com/x/y/releases/download")) == 2, (f_test_ohne, f_aelter))
    pruefe("aktualisieren.py --laden als eigener Prozess (wie aus der Oberfläche; eingebettetes Python mit ._pth) findet signatur.py",
           als_prozess.returncode == 0 and "Signatur in Ordnung" in als_prozess.stdout
           and (ak.bereit(tmp / "e51-prozess") or {}).get("version") == "9.1", (als_prozess.stdout + als_prozess.stderr)[-400:])
    # --- Werkzeuge im Arbeitsordner ---
    arbeit = HIER.parent.parent
    sr_pfad, vr_pfad, bau = arbeit / "werkstatt" / "signiere_release.py", arbeit / "werkstatt" / "veroeffentliche_release.py", arbeit / "werkstatt" / "bau_webapp.py"
    if not all(x.is_file() for x in (sr_pfad, vr_pfad, bau)) or os.name != "nt":
        print("  (werkstatt/signiere_release.py, veroeffentliche_release.py, bau_webapp.py liegen nur im Quellbaum; DPAPI nur unter Windows – 4 Prüfungen entfallen)")
        print(f"  E51 Kern {time.time() - t0:.1f} s")
        return
    env = dict(os.environ, PYTHONIOENCODING="utf-8", GH_TOKEN="", HTTPS_PROXY="http://127.0.0.1:9", HTTP_PROXY="http://127.0.0.1:9")

    def lauf(*args):
        return subprocess.run([sys.executable, *map(str, args)], env=env, cwd=str(tmp), capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=600)
    ko = tmp / "e51-schluessel"
    datei = tmp / "e51-SHA256SUMS.txt"
    datei.write_bytes(summen)
    n1 = lauf(sr_pfad, "--neu", "--ordner", ko)
    n2 = lauf(sr_pfad, "--neu", "--ordner", ko)
    s1 = lauf(sr_pfad, "--signiere", datei, "--version", "9.9", "--ordner", ko)
    p1 = lauf(sr_pfad, "--pruefe", datei, "--version", "9.9", "--ordner", ko)
    p2 = lauf(sr_pfad, "--pruefe", datei, "--version", "9.9")
    p3 = lauf(sr_pfad, "--pruefe", datei, "--version", "9.8", "--ordner", ko)
    innen = lauf(sr_pfad, "--status", "--ordner", arbeit / "e51-nie")
    ms = Path(str(datei) + ".minisig")
    pub = (ko / "haupt.pub").read_text(encoding="utf-8") if (ko / "haupt.pub").is_file() else ""
    pruefe("signiere_release.py (Testordner): --neu legt Haupt + Reserve an (DPAPI + .pub, nie überschreiben), --signiere → .minisig, "
           "--pruefe gültig mit eigenem .pub, ohne (nicht vertraut) und falsche Version → Abbruch; nie im Arbeitsordner",
           n1.returncode == 0 and n2.returncode != 0 and s1.returncode == 0 and ms.is_file() and p1.returncode == 0
           and p2.returncode != 0 and "fremder_schluessel" in p2.stderr and p3.returncode != 0 and innen.returncode != 0
           and not (arbeit / "e51-nie").exists() and sorted(x.name for x in ko.iterdir()) == ["haupt.dpapi", "haupt.pub", "reserve.dpapi", "reserve.pub"]
           and sg.pruefe(summen, ms.read_bytes(), [("t", *sg.schluessel_lesen(pub))], "me-goos-ta-deutsch v9.9")
           and len(n1.stdout) < 2000,
           (n1.stdout + n1.stderr + n2.stderr + s1.stderr + p2.stderr + innen.stderr)[-500:])
    import importlib.util
    spec = importlib.util.spec_from_file_location("signiere_release_e51", sr_pfad)
    srm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(srm)
    srm.sicherung(ko, tmp / "e51-usb", "ein-langes-test-passwort", ops=1048576, mem=16777216)
    usb = tmp / "e51-usb" / "me-goos-ta-deutsch-reserve.key"
    zurueck = srm.schluessel_entschluesseln(usb.read_text(encoding="utf-8"), "ein-langes-test-passwort") if usb.is_file() else None
    try:
        srm.schluessel_entschluesseln(usb.read_text(encoding="utf-8"), "falsch-falsch-falsch")
        falsch = False
    except SystemExit:
        falsch = True
    ms_r, sid_r = srm.signieren(summen, "9.9", reserve_datei=usb, passwort="ein-langes-test-passwort")
    pruefe("Sicherung: minisign-verschlüsselt (scrypt), Gegenprobe, Reserve danach vom Rechner entfernt; falsches Passwort → Abbruch; "
           "Signieren mit der Reserve aus der Sicherung",
           zurueck is not None and not (ko / "reserve.dpapi").exists() and (ko / "reserve.pub").is_file() and falsch
           and usb.read_text(encoding="utf-8").startswith("untrusted comment: minisign encrypted secret key\n")
           and base64.b64decode(usb.read_text(encoding="utf-8").splitlines()[1])[:6] == b"EdScB2"
           and srm.pruefen(summen, ms_r, "9.9", ko)["name"].startswith("reserve"), (sid_r, falsch))
    # --- veroeffentliche_release.py: Signatur Pflicht, vor jedem Netz ---
    rel = tmp / "e36-release"
    ordner = rel / "Me-Goos-ta-Deutsch"
    zips = sorted(rel.glob("Me-Goos-ta-Deutsch-*.zip"))
    if not ordner.is_dir() or not zips:
        pruefe("E51: Release-Ordner aus E36 vorhanden", False, str(rel))
        return
    grund_ci = "E51 prüft nur die Signatur-Schranke"
    v1 = lauf(vr_pfad, ordner, zips[0], "--ohne-ci", grund_ci, "--signatur-ordner", tmp / "e51-leer")
    v2 = lauf(vr_pfad, ordner, zips[0], "--ohne-ci", grund_ci, "--signatur-ordner", ko)
    v3 = lauf(vr_pfad, ordner, zips[0], "--probe", "--ohne-ci", grund_ci, "--signatur-ordner", ko)
    mp = re.search(r"^#plan (.*)$", v3.stdout, re.M)
    plan = json.loads(mp.group(1)) if mp else {}
    pruefe("veroeffentliche_release.py: ohne Schlüssel bzw. mit nicht vertrautem Schlüssel Abbruch vor jedem Netz (nichts neben die ZIP); "
           "--probe nennt Schlüssel + „nicht vertraut“; Notizen mit minisign-Befehl und Haupt-Schlüssel",
           v1.returncode != 0 and "Haupt-Schlüssel" in v1.stderr and v2.returncode != 0 and "nicht vertraut" in v2.stderr
           and "Konto " not in v1.stdout + v2.stdout and not (rel / "SHA256SUMS.txt.minisig").exists()
           and v3.returncode == 0 and plan.get("signatur", {}).get("vertraut") is False
           and plan.get("signatur", {}).get("schluessel") == sg.schluessel_id(sg.schluessel_lesen(pub)[0])
           and f"minisign -Vm SHA256SUMS.txt -P {sg.SCHLUESSEL[0][1]}" in v3.stdout,
           (v1.stderr + v2.stderr + v3.stderr)[-500:])
    # --- Download-Seite: „Echtheit prüfen“ nur bei signiertem Release ---
    srel = tmp / "e51-rel"
    srel.mkdir()
    zp = srel / zips[0].name
    shutil.copyfile(zips[0], zp)
    (srel / "SHA256SUMS.txt").write_text(f"{hashlib.sha256(zp.read_bytes()).hexdigest()}  {zp.name}\n", encoding="utf-8")
    (srel / "SHA256SUMS.txt.minisig").write_bytes(fest)
    b = lauf(bau, HIER.parent, tmp / "e51-web", "--ohne-pyodide", "--ohne-modelle", "--release-zip", zp)
    html = (tmp / "e51-web" / "web-app" / "download" / "index.html").read_text(encoding="utf-8") if b.returncode == 0 else ""
    befehl = f"<code>minisign -Vm SHA256SUMS.txt -P {sg.SCHLUESSEL[0][1]}</code>"
    pruefe("Download-Seite: „Echtheit prüfen“ (de/en/es) mit minisign-Befehl, Schlüssel-ID und Link auf .minisig nur bei signiertem Release",
           all(f'<details id="{l}-echtheit">' in html for l in ("de", "en", "es")) and html.count(befehl) == 3
           and html.count("SHA256SUMS.txt.minisig</a>") == 3 and html.count(sg.schluessel_id(sg.vertraut()[0][1])) == 3,
           (b.stdout + b.stderr)[-400:])
    print(f"  E51 {time.time() - t0:.1f} s")


E52_LOCKS = {"pakete.lock": "alle", "pakete-bewaehrt.lock": "win", "pakete-aelter.lock": "win", "pakete-sprachen.lock": "alle"}
E52_PLATTFORMEN = {"win_amd64": r"win_amd64", "macos_x86_64": r"macosx_\d+_\d+_(x86_64|universal2)",
                   "macos_arm64": r"macosx_\d+_\d+_(arm64|universal2)", "linux_x86_64": r"manylinux[\w]*?_x86_64",
                   "linux_aarch64": r"manylinux[\w]*?_aarch64"}


def _e52_name(s):
    return re.sub(r"[-_.]+", "-", s).lower()


def _e52_lock(text):
    """[(name, operator, version, [hashes], [dateien])] einer Lock-Datei im Format von bau_lock.py."""
    eintraege, dateien, zeilen, i = [], [], text.splitlines(), 0
    while i < len(zeilen):
        z = zeilen[i]
        if z.startswith("#   "):
            dateien.append(z[4:].strip())
        m = re.match(r"^([A-Za-z0-9][A-Za-z0-9._-]*)\s*(==|===|>=|<=|~=|!=|<|>)?\s*([^\s;\\]*)", z) \
            if z.strip() and not z.startswith(("#", " ")) else None
        if m:
            hashes, i = [], i + 1
            while i < len(zeilen) and zeilen[i].startswith("    --hash="):
                hashes.append(zeilen[i].split("=", 1)[1].rstrip(" \\"))
                i += 1
            eintraege.append((m.group(1), m.group(2), m.group(3), hashes, dateien))
            dateien = []
            continue
        i += 1
    return eintraege


def test_paket_fassungen(tmp):
    """E52 (2.5): Feste Paketfassungen mit Prüfsummen – Lock-Dateien vollständig (==, SHA-256, Räder je Plattform,
    Abhängigkeiten), Starter und Sprachen-Tool rufen pip mit --require-hashes und Lock, Fingerabdruck folgt dem Lock,
    bau_lock.py --probe (entfällt ohne Arbeitsordner), echter pip-Lauf gegen die Locks (entfällt ohne Internet)."""
    print("\n[E52] Feste Paketfassungen mit Prüfsummen")
    import importlib.metadata as md
    import sprachen as sp
    import starter
    t0 = time.time()
    locks = {n: (HIER / n).read_text(encoding="ascii") if (HIER / n).is_file() else "" for n in E52_LOCKS}
    befund = []
    for n, art in E52_LOCKS.items():
        eintraege = _e52_lock(locks[n])
        if not eintraege or not locks[n].isascii():
            befund.append(f"{n}: leer/fehlt")
        pflicht = ["win_amd64"] if art == "win" else list(E52_PLATTFORMEN)
        for name, op, version, hashes, dateien in eintraege:
            if op != "==" or not re.fullmatch(r"\d+(\.\d+)*", version):
                befund.append(f"{n}: {name} ohne ==")
            if not hashes or len(hashes) != len(dateien) or len(set(hashes)) != len(hashes) \
                    or not all(re.fullmatch(r"sha256:[0-9a-f]{64}", h) for h in hashes):
                befund.append(f"{n}: {name} Prüfsummen")
            if not all(d.endswith(".whl") and re.search(r"-(cp313-cp313|cp3\d+-abi3|py3-none)-", d) for d in dateien):
                befund.append(f"{n}: {name} Rad passt nicht zu Python 3.13")
            for p in pflicht:
                if not any(d.endswith("-any.whl") or any(re.fullmatch(E52_PLATTFORMEN[p], t) for t in d[:-4].split("-")[-1].split("."))
                           for d in dateien):
                    befund.append(f"{n}: {name} ohne Rad für {p}")
    pruefe("Lock-Dateien (Standard, 2 Ersatz-Sätze, Sprachen): nur ==, je Rad sha256 mit 64 Hex-Zeichen, Räder für Python 3.13; "
           "Standard + Sprachen für Windows x64, macOS Intel/Apple Silicon, Linux x64/ARM, Ersatz-Sätze für Windows x64",
           not befund, befund[:6])
    # --- vollständig: requirements.txt + Abhängigkeiten der installierten (gleichen) Fassungen ---
    try:
        from pip._vendor.packaging.requirements import Requirement
    except ImportError:                                       # Python ohne pip: nur die Oberpakete
        Requirement = None
    haupt = {_e52_name(e[0]): e[2] for e in _e52_lock(locks["pakete.lock"])}
    oben = [_e52_name(re.split(r"[<>=!~;\s]", z.strip())[0]) for z in (HIER / "requirements.txt").read_text(encoding="utf-8").splitlines()
            if z.strip() and not z.startswith("#")]
    fehlt, geprueft = [n for n in oben if n not in haupt], []
    for n, v in haupt.items():
        try:
            d = md.distribution(n)
        except md.PackageNotFoundError:
            continue
        if d.version != v or Requirement is None:
            continue
        geprueft.append(n)
        for r in d.requires or []:
            req = Requirement(r)
            if (req.marker is None or req.marker.evaluate({"extra": ""})) and _e52_name(req.name) not in haupt:
                fehlt.append(f"{n} → {req.name}")
    sprach = {_e52_name(e[0]): e[2] for e in _e52_lock(locks["pakete-sprachen.lock"])}
    pruefe(f"pakete.lock vollständig: alle Pakete aus requirements.txt + jede Abhängigkeit (geprüft an {len(geprueft)} installierten "
           "gleichen Fassungen); pakete-sprachen.lock = uharfbuzz in der Fassung von sprachen.PAKETE",
           not fehlt and len(oben) >= 4 and sprach.get("uharfbuzz") == sp.PAKETE["uharfbuzz"]["version"], (fehlt, geprueft, sprach))
    # --- Starter: pip mit --require-hashes und Lock (Ersatz-Satz, lokaler Ordner, MGD_PAKETE_NEUESTE nur Spannen) ---
    alt_env = os.environ.pop("MGD_PAKETE_NEUESTE", None)
    aufrufe = []
    alt_pip, alt_lokal = starter.pip_lauf, starter.lokale_pakete
    try:
        starter.pip_lauf = lambda aus, args, anzeigen=True: (aufrufe.append(list(args)), (0, "Successfully installed x"))[1]
        spez_std, spez_b = starter.paket_spezifikation(), starter.paket_spezifikation("bewährt")
        starter.installiere(None, starter.paket_spezifikation())
        starter.lokale_pakete = lambda: tmp
        starter.installiere(None, starter.paket_spezifikation("älter"))
        os.environ["MGD_PAKETE_NEUESTE"] = "1"
        spez_neu, spez_neu_b = starter.paket_spezifikation(), starter.paket_spezifikation("bewährt")
    finally:
        starter.pip_lauf, starter.lokale_pakete = alt_pip, alt_lokal
        os.environ.pop("MGD_PAKETE_NEUESTE", None)
        if alt_env is not None:
            os.environ["MGD_PAKETE_NEUESTE"] = alt_env
    hs = str(starter.HIER)
    pruefe("Starter: pip install --only-binary=:all: --require-hashes -r pakete.lock (Ersatz-Sätze mit eigener Lock-Datei, auch aus "
           "werkzeuge/pakete); nur MGD_PAKETE_NEUESTE=1 nimmt die Spannen aus requirements.txt",
           spez_std == ["--require-hashes", "-r", str(Path(hs) / "pakete.lock")]
           and spez_b == ["--require-hashes", "-r", str(Path(hs) / "pakete-bewaehrt.lock")]
           and len(aufrufe) == 2 and "--only-binary=:all:" in aufrufe[0] and aufrufe[0][-3:] == spez_std
           and "--no-index" in aufrufe[1] and aufrufe[1][-3:] == ["--require-hashes", "-r", str(Path(hs) / "pakete-aelter.lock")]
           and spez_neu == ["-r", str(Path(hs) / "requirements.txt")] and spez_neu_b == spez_b
           and dict(starter.ERSATZ_SAETZE) == {"bewährt": "pakete-bewaehrt.lock", "älter": "pakete-aelter.lock"},
           (spez_std, aufrufe, spez_neu))
    # --- Fingerabdruck folgt den Lock-Dateien ---
    kopie = tmp / "e52-hier"
    kopie.mkdir()
    for n in (*E52_LOCKS, "requirements.txt"):
        if (HIER / n).is_file():
            shutil.copy2(HIER / n, kopie / n)
    alt_hier = starter.HIER                                   # starter kann aus der Testkopie stammen (ohne Locks)
    try:
        starter.HIER = HIER
        echt = starter.paket_signatur()
        starter.HIER = kopie
        s1 = starter.paket_signatur()
        (kopie / "pakete-aelter.lock").write_text(locks["pakete-aelter.lock"] + "# geaendert\n", encoding="ascii")
        s2 = starter.paket_signatur()
        (kopie / "requirements.txt").write_text("numpy>=1,<9\n", encoding="utf-8")
        s3 = starter.paket_signatur()
        os.environ["MGD_PAKETE_NEUESTE"] = "1"
        s4 = starter.paket_signatur()
    finally:
        starter.HIER = alt_hier
        os.environ.pop("MGD_PAKETE_NEUESTE", None)
        if alt_env is not None:
            os.environ["MGD_PAKETE_NEUESTE"] = alt_env
    pruefe("Fingerabdruck der Pakete = Lock-Dateien (gleich in jedem Ordner, neue Lock-Datei → Einrichtung „pakete“; "
           "requirements.txt zählt nur im Job „neueste“)", echt == s1 and s2 != s1 and s3 == s2 and s4 != s3, (echt, s1, s2, s3, s4))
    # --- Sprachen-Tool: uharfbuzz mit Hash ---
    befehle = []

    class _R:
        returncode, stdout, stderr = 0, "", ""
    alt_run, alt_daten, alt_lock = sp.subprocess.run, os.environ.get("MGD_DATEN"), sp.PAKETE_LOCK
    echt_lock = HIER / "pakete-sprachen.lock"                 # sprachen kann aus der Testkopie stammen (ohne Locks)
    os.environ["MGD_DATEN"] = str(tmp / "e52-daten")
    fehler = []
    try:
        sp.subprocess.run = lambda befehl, **kw: (befehle.append([str(b) for b in befehl]), _R())[1]
        for lock in (echt_lock, tmp / "e52-fehlt.lock"):
            sp.PAKETE_LOCK = lock
            try:
                sp.installiere_paket("uharfbuzz")
            except sp.SprachFehler as e:
                fehler.append(str(e))
    finally:
        sp.subprocess.run, sp.PAKETE_LOCK = alt_run, alt_lock
        if alt_daten is None:
            os.environ.pop("MGD_DATEN", None)
        else:
            os.environ["MGD_DATEN"] = alt_daten
    b = befehle[0] if befehle else []
    pruefe("Sprachen-Tool: uharfbuzz per pip --require-hashes -r pakete-sprachen.lock (--no-deps, --target, nur Räder); "
           "fehlt der Eintrag im Lock → Fehler vor jedem pip-Aufruf",
           len(befehle) == 1 and all(x in b for x in ("--require-hashes", "--no-deps", "--only-binary=:all:", "--target"))
           and b[-2:] == ["-r", str(echt_lock)] and not any(x.startswith("uharfbuzz==") for x in b) and len(fehler) == 2,
           (befehle, fehler))
    # --- bau_lock.py --probe (Arbeitsordner) + Release enthält die Locks ---
    arbeit = HIER.parent.parent
    bl = arbeit / "werkstatt" / "bau_lock.py"
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PIP_CONFIG_FILE=os.devnull)
    env.pop("MGD_PAKETE_NEUESTE", None)

    def lauf(*args, t=600):
        return subprocess.run([sys.executable, *map(str, args)], env=env, cwd=str(tmp), capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=t)
    if bl.is_file() and (arbeit / "werkstatt" / "bau_lock_antworten.json").is_file():
        p1 = lauf(bl, HIER, "--probe")
        mp = re.search(r"^#plan (.*)$", p1.stdout, re.M)
        plan = json.loads(mp.group(1)) if mp else {}
        falsch = tmp / "e52-prog"
        shutil.copytree(kopie, falsch)
        (falsch / "requirements.txt").write_bytes((HIER / "requirements.txt").read_bytes())
        (falsch / "pakete.lock").write_text(re.sub(r"sha256:[0-9a-f]{4}", "sha256:0000", locks["pakete.lock"], count=1), encoding="ascii")
        p2 = lauf(bl, falsch, "--probe")
        rel = tmp / "e36-release" / "Me-Goos-ta-Deutsch" / "Programm"
        im_release = all((rel / n).is_file() for n in E52_LOCKS) if rel.is_dir() else None
        pruefe("bau_lock.py --probe (offline, gespeicherte PyPI-Antworten): baut alle Locks gleich nach; geänderte Prüfsumme → Abweichung; "
               "Release-Ordner (bau_release.py) enthält alle Lock-Dateien",
               p1.returncode == 0 and p1.stdout.count("✓ ") == len(E52_LOCKS) and "✗" not in p1.stdout
               and plan.get("locks", {}).get("pakete.lock") == haupt and p2.returncode == 1 and "✗ pakete.lock" in p2.stdout
               and im_release is not False, (p1.stdout + p1.stderr)[-400:] + (p2.stdout + p2.stderr)[-200:])
    else:
        print("  (werkstatt/bau_lock.py + bau_lock_antworten.json liegen nur im Quellbaum – 1 Prüfung entfällt)")
    # --- echter pip-Lauf: Locks installierbar, falsche Prüfsumme wird abgelehnt ---
    pip = [sys.executable, "-m", "pip", "install", "--dry-run", "--ignore-installed", "--disable-pip-version-check",
           "--no-input", "--require-hashes", "--only-binary=:all:", "-q"]
    namen = ["pakete.lock", "pakete-sprachen.lock"] + (["pakete-bewaehrt.lock", "pakete-aelter.lock"] if os.name == "nt" else [])
    laeufe = {n: subprocess.run(pip + (["--no-deps"] if n == "pakete-sprachen.lock" else []) + ["-r", str(HIER / n)], env=env,
                                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900) for n in namen}
    rl = next(e for e in _e52_lock(locks["pakete.lock"]) if e[0] == "reportlab")
    (tmp / "e52-falsch.lock").write_text(f"reportlab=={rl[2]} \\\n    --hash=sha256:{'0' * 64}\n", encoding="ascii")
    falsch_lauf = subprocess.run(pip + ["--no-deps", "-r", str(tmp / "e52-falsch.lock")], env=env, capture_output=True, text=True,
                                 encoding="utf-8", errors="replace", timeout=600)
    alles = " ".join(r.stdout + r.stderr for r in [*laeufe.values(), falsch_lauf]).lower()
    if any(w in alles for w in ("newconnectionerror", "failed to establish", "getaddrinfo", "temporary failure in name resolution",
                                "max retries exceeded", "proxyerror", "network is unreachable")):
        print("  (E52: kein Internet – der echte pip-Lauf entfällt)")
    else:
        pruefe(f"Echter pip-Lauf (--dry-run --require-hashes) gegen {', '.join(namen)}: installierbar; falsche Prüfsumme → abgelehnt",
               all(r.returncode == 0 for r in laeufe.values()) and falsch_lauf.returncode != 0
               and "do not match the hashes" in (falsch_lauf.stdout + falsch_lauf.stderr).lower(),
               {n: (r.returncode, (r.stderr or r.stdout)[-200:]) for n, r in laeufe.items()} | {"falsch": falsch_lauf.stderr[-200:]})
    print(f"  E52 {time.time() - t0:.1f} s")


def test_quellbaum(tmp):
    """E53 (2.5): Arbeitsordner = Git-Quellbaum – Update ersetzt nie einen Quellbaum (werkstatt/bau_release.py bzw. .git
    daneben); werkstatt/quellbaum.py --pruefen: Nutzerdaten (wie aktualisieren.NUTZER) und private Notizen ignoriert, keine
    Datei > 20 MB, keine Schlüssel/Tokens, Startdateien ausführbar, alle Release-Dateien versioniert; Commits signiert.
    Ohne Quellbaum (werkstatt/quellbaum.py + .git, z. B. auf den CI-Rechnern) entfallen 4 der 5 Prüfungen."""
    print("\n[E53] Arbeitsordner als Git-Quellbaum")
    import importlib.util
    import aktualisieren as ak
    t0 = time.time()
    # --- Update-Schutz für den neuen Aufbau (immer) ---
    qb = tmp / "e53-quellbaum"
    prog = qb / "Me-Goos-ta-Deutsch"
    (prog / "Programm").mkdir(parents=True)
    for n in ("starter.py", "gans_ui.py"):
        (prog / "Programm" / n).write_text("#", encoding="utf-8")
    frei = ak.programm_ordner_ok(prog)
    (qb / "werkstatt").mkdir()
    (qb / "werkstatt" / "bau_release.py").write_text("#", encoding="utf-8")
    mit_werkstatt = ak.programm_ordner_ok(prog)
    (qb / "werkstatt" / "bau_release.py").unlink()
    (qb / ".git").mkdir()
    mit_git = ak.programm_ordner_ok(prog)
    pruefe("Update ersetzt nie den Quellbaum: werkstatt/bau_release.py oder .git neben Me-Goos-ta-Deutsch → Programmordner gesperrt",
           frei and not mit_werkstatt and not mit_git, (frei, mit_werkstatt, mit_git))
    arbeit = HIER.parent.parent
    skript = arbeit / "werkstatt" / "quellbaum.py"
    if not (skript.is_file() and (arbeit / ".git").is_dir()):
        print("  (werkstatt/quellbaum.py + .git gibt es nur im Quellbaum – 4 Prüfungen entfallen)")
        return
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, str(skript), "--pruefen"], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env, timeout=120)
    m = re.search(r"^#pruefung (\{.*\})$", r.stdout, re.M)
    b = json.loads(m.group(1)) if m else {}
    spec = importlib.util.spec_from_file_location("quellbaum_e53", skript)
    q = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(q)
    programm_nie = [p[len("Me-Goos-ta-Deutsch/"):] for p in q.NIE if p.startswith("Me-Goos-ta-Deutsch/Programm/")]
    pruefe("Nicht im Repo: private Notizen, Archive/Releases/Proben/ci_ergebnis.json und jedes Nutzerdaten-Muster (alle Beispiele "
           "passen zu aktualisieren.NUTZER)",
           m is not None and b.get("nicht_ignoriert") == [] and b.get("ignoriert_geprueft", 0) >= 25
           and all(n in q.NIE for n in ("UEBERGABE.md", "ARBEITSSTAND.md", "PROMPT_NEUER_CHAT.txt", "ci_ergebnis.json"))
           and len(programm_nie) >= 15 and all(ak.NUTZER.match(p) for p in programm_nie),
           (b.get("nicht_ignoriert"), [p for p in programm_nie if not ak.NUTZER.match(p)], r.stderr[-300:]))
    falsch = b"ghp_" + b"A1" * 18 + b"\n-----BEGIN OPENSSH " + b"PRIVATE KEY-----\n" + b"b3BlbnNzaC1rZXk" * 4
    pruefe("Im Repo keine Datei > 20 MB, keine Schlüssel/Tokens (Muster erkennt echte Werte, nicht ihre Erwähnung); "
           "Startdateien Mac/Linux ausführbar (100755)",
           b.get("gross") == [] and b.get("geheim") == [] and b.get("nicht_ausfuehrbar") == []
           and len(q.GEHEIM.findall(falsch)) == 2 and not q.GEHEIM.search(b"ghp_ github_pat_ PRIVATE KEY minisign encrypted secret key"),
           {k: b.get(k) for k in ("gross", "geheim", "nicht_ausfuehrbar")})
    alt = [n for n in ("ci", "bau_release.py", "bau_webapp.py", "ci_lauf.py", "veroeffentliche_release.py") if (arbeit / n).exists()]
    pruefe("Aufbau: .github/, werkstatt/ (alle Skripte), web-app-quelle/, Me-Goos-ta-Deutsch/ – jede Release-Datei versioniert, "
           "nichts mehr am alten Ort",
           r.returncode == 0 and b.get("fehlt") == [] and b.get("release", 0) >= 60 and not alt,
           (b.get("fehlt"), alt, r.stdout[-300:]))
    konf = {k: q.git("config", "--get", k, pruefen=False).strip() for k in
            ("core.autocrlf", "gpg.format", "commit.gpgsign", "tag.gpgsign", "push.default", "user.email", "user.signingkey")}
    signiert = q.git("log", "-1", "--format=%G?", pruefen=False).strip()
    pruefe("Git: signierte Commits (SSH, Schlüssel außerhalb des Repos, letzter Commit gültig), noreply-Adresse, autocrlf aus, "
           "push.default nothing",
           konf["core.autocrlf"] == "false" and konf["gpg.format"] == "ssh" and konf["commit.gpgsign"] == "true"
           and konf["tag.gpgsign"] == "true" and konf["push.default"] == "nothing"
           and konf["user.email"].endswith("@users.noreply.github.com")
           and arbeit.resolve() not in Path(konf["user.signingkey"] or arbeit).resolve().parents and signiert == "G",
           (konf, signiert))
    print(f"  E53 {time.time() - t0:.1f} s")


def test_ci_quellbaum(tmp):
    """E54 (2.5): CI baut aus dem Quellbaum – alle Workflows mit Actions per 40-stelligem SHA, nirgends
    pull_request_target, oben nur contents: read, Schreibrechte nur im Scorecard-Job; tests.yml: Job bau (bau.py → baum.tar)
    + lint, Testjobs ohne Checkout aus dem Artefakt; ruff.toml + lint.lock (fest, mit Hash); dependabot.yml nur
    github-actions; ci_lauf.py pusht den Quellbaum (gleiche Prüfsumme wie der Arbeitsordner), bau.py setzt die Rechte im
    tar; Kopfzeilen ohne CR/LF (CodeQL). Ohne .github/ bzw. werkstatt/ entfallen 5 der 6 Prüfungen."""
    print("\n[E54] CI baut aus dem Quellbaum")
    import importlib.util
    import inspect
    import tarfile
    import gans_ui
    t0 = time.time()
    boese = gans_ui.kopf_sauber("datei.pdf\r\nSet-Cookie: x=1\n\x00")
    quelle = inspect.getsource(gans_ui.Handler._senden)
    pruefe("Kopfzeilen ohne CR/LF/NUL (Antwort-Aufspaltung): kopf_sauber für Content-Type und jede Zusatz-Kopfzeile",
           "\r" not in boese and "\n" not in boese and "\x00" not in boese and boese.startswith("datei.pdf")
           and "kopf_sauber(mime)" in quelle and "self.send_header(kopf_sauber(k), kopf_sauber(v))" in quelle, boese)
    arbeit = HIER.parent.parent
    gh = arbeit / ".github"
    wfs = {n: gh / "workflows" / n for n in ("tests.yml", "release_pruefung.yml", "scorecard.yml")}
    bau, ci_lauf = gh / "ci" / "bau.py", arbeit / "werkstatt" / "ci_lauf.py"
    if not all(x.is_file() for x in (*wfs.values(), bau, ci_lauf, gh / "dependabot.yml", arbeit / "ruff.toml")):
        print("  (.github/, werkstatt/ und ruff.toml liegen nur im Quellbaum – 5 Prüfungen entfallen)")
        return
    y = {n: w.read_text(encoding="utf-8") for n, w in wfs.items()}
    fehler = []
    for n, txt in y.items():
        uses = re.findall(r"^\s*-?\s*uses:\s*(\S+)", txt, re.M)
        if not uses or not all(re.fullmatch(r"[a-z0-9-]+/[a-z0-9_./-]+@[0-9a-f]{40}", u) for u in uses):
            fehler.append(f"{n}: uses {uses}")
        if "pull_request_target" in txt or "secrets." in txt or not re.search(r"^permissions:\n  contents: read\n\n", txt, re.M):
            fehler.append(f"{n}: Auslöser/Rechte")
        if re.search(r"^\s+(- )?(run|name): (?![|>])[^\n]*: ", txt, re.M):     # „: “ in einfacher Zeile = YAML-Fehler (Fund G05)
            fehler.append(f"{n}: run/name-Zeile mit „: “ – Block (|) nehmen")
        schreib = re.findall(r"^( +)([a-z-]+): write$", txt, re.M)
        if n != "scorecard.yml" and ("write" in txt or schreib):
            fehler.append(f"{n}: write")
        if n == "scorecard.yml" and (sorted(s[1] for s in schreib) != ["id-token", "security-events"]
                                     or any(len(s[0]) != 6 for s in schreib) or "publish_results: true" not in txt
                                     or not re.search(r"^on:\n  push:\n    branches: \[main\]\n  workflow_dispatch:\n\n", txt, re.M)):
            fehler.append(f"{n}: Schreibrechte nur im Job (security-events, id-token), nur main")
        jobs = re.findall(r"^  ([a-z][a-z0-9_-]*):\s*$", txt.split("\njobs:", 1)[1], re.M) if "\njobs:" in txt else []
        zeiten = re.findall(r"^\s+timeout-minutes:\s*(\d+)", txt, re.M)
        if len(zeiten) != len(jobs) or txt.count("persist-credentials: false") != sum(1 for u in uses if u.startswith("actions/checkout@")):
            fehler.append(f"{n}: Zeitlimit/persist-credentials")
    pruefe("Alle Workflows: Actions per 40-stelligem SHA, nie pull_request_target, keine Secrets, oben nur contents: read, "
           "Schreibrechte nur im Scorecard-Job (security-events + id-token, nur main), Zeitlimit je Job", not fehler, fehler)
    tt = y["tests.yml"]
    teile = {}
    for j in ("bau", "lint", "frischtest", "debian", "browser"):
        rest = tt.split(f"\n  {j}:\n", 1)[1] if f"\n  {j}:\n" in tt else ""
        teile[j] = re.split(r"\n  [a-z][a-z0-9_-]*:\n", rest, maxsplit=1)[0]
    test_jobs = [teile[j] for j in ("frischtest", "debian", "browser")]
    pruefe("tests.yml: Job bau (bau.py aus dem Quellbaum, Pakete per pakete.lock mit Hashes, Pyodide-Cache, Artefakt baum.tar) "
           "und Job lint; Testjobs needs: bau, ohne Checkout, packen baum.tar aus und starten baum/.github/ci/…",
           "python .github/ci/bau.py --ergebnis ergebnis.json --tar baum.tar --cache" in teile["bau"]
           and "--require-hashes --only-binary=:all: -r Me-Goos-ta-Deutsch/Programm/pakete.lock" in teile["bau"]
           and "uses: actions/cache@" in teile["bau"] and "name: baum\n" in teile["bau"] and "path: baum.tar" in teile["bau"]
           and "name: ergebnis-bau" in teile["bau"] and "ruff check" in teile["lint"] and "-r .github/ci/lint.lock" in teile["lint"]
           and all("needs: bau" in j and "actions/checkout@" not in j and "actions/download-artifact@" in j
                   and "tar -xf baum.tar" in j and "baum/.github/ci/" in j for j in test_jobs),
           {k: len(v) for k, v in teile.items()})
    ruff = (arbeit / "ruff.toml").read_text(encoding="utf-8")
    lock = (gh / "ci" / "lint.lock").read_text(encoding="utf-8") if (gh / "ci" / "lint.lock").is_file() else ""
    hashes = re.findall(r"--hash=sha256:([0-9a-f]+)", lock)
    pruefe("Lint: ruff.toml mit kleinem Regelsatz (E9, F63, F7, F82), Referenz-Testreihe ausgenommen; lint.lock = eine feste "
           "ruff-Fassung mit SHA-256 je Rad, nur ASCII",
           re.search(r'^select = \["E9", "F63", "F7", "F82"\]$', ruff, re.M) is not None
           and '"Me-Goos-ta-Deutsch/Programm/test_gans_lernkarten.py"' in ruff and "[format]" not in ruff
           and re.search(r"^ruff==\d+\.\d+\.\d+ \\$", lock, re.M) is not None and len(re.findall(r"^[a-z]", lock, re.M)) == 1
           and hashes and all(len(h) == 64 for h in hashes) and lock.isascii(), (ruff[:120], hashes))
    dep = (gh / "dependabot.yml").read_text(encoding="utf-8")
    pruefe("dependabot.yml: Version 2, nur github-actions (Python-Pakete über bau_lock.py), wöchentlich",
           re.search(r"^version: 2$", dep, re.M) is not None and dep.count("package-ecosystem:") == 1
           and "package-ecosystem: github-actions" in dep and "interval: weekly" in dep, dep[-200:])
    # ci_lauf.py --probe: Quellbaum + bau.py: Rechte im tar
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1", GH_TOKEN="",
               HTTPS_PROXY="http://127.0.0.1:9", HTTP_PROXY="http://127.0.0.1:9")     # kein Netz
    env.pop("GITHUB_ACTIONS", None)
    pr = subprocess.run([sys.executable, str(ci_lauf), str(HIER.parent), "--probe"], env=env, cwd=str(tmp), capture_output=True,
                        text=True, encoding="utf-8", errors="replace", timeout=600)
    mp = re.search(r"^#plan (.*)$", pr.stdout, re.M)
    q = (json.loads(mp.group(1)) if mp else {}).get("quellbaum") or {}
    spec = importlib.util.spec_from_file_location("bau_e54", bau)
    b = importlib.util.module_from_spec(spec)
    vorher = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(b)
    finally:
        sys.dont_write_bytecode = vorher
    baum = tmp / "e54-baum"
    for n in ("Me Goos-ta Deutsch - Mac.command", "Me Goos-ta Deutsch - Linux.sh", "README.md", "Programm/x.sh"):
        (baum / n).parent.mkdir(parents=True, exist_ok=True)
        (baum / n).write_text("#", encoding="utf-8")
    b.tar_bauen(baum, tmp / "e54.tar")
    with tarfile.open(tmp / "e54.tar") as tf:
        modi = {m.name: m.mode for m in tf.getmembers() if m.isfile()}
    git_ok = (arbeit / ".git").is_dir()
    pruefe("ci_lauf.py --probe: Branch ci = Quellbaum (quellbaum.py-Prüfung ✓, baut dasselbe Release wie der Arbeitsordner, "
           "3 Workflows); bau.py: Startdateien oben 0755, sonst 0644 im tar",
           pr.returncode == 0 and (not git_ok or (q.get("pruefung_ok") and q.get("pruefsumme_gleich") and q.get("dateien", 0) >= 90
                                                  and q.get("workflows") == ["release_pruefung.yml", "scorecard.yml", "tests.yml"]))
           and modi.get("baum/Me Goos-ta Deutsch - Mac.command") == 0o755 and modi.get("baum/Me Goos-ta Deutsch - Linux.sh") == 0o755
           and modi.get("baum/README.md") == 0o644 and modi.get("baum/Programm/x.sh") == 0o644,
           (q, modi, (pr.stdout + pr.stderr)[-300:]))
    print(f"  E54 {time.time() - t0:.1f} s")


def test_veroeffentlichung(tmp):
    """E55 (2.5): Veröffentlichung neu – Token-Reihenfolge (GH_TOKEN → Anmeldeinformation MGD-Release-Token → nur mit
    --desktop-anmeldung GitHub CLI/Desktop, sonst Anleitung) und Rechte-Prüfung mit nachgebildeter Anmeldung (ohne Netz);
    kein --ersetzen, kein Force; Release-Schritte Entwurf → Prüfen → Veröffentlichen gegen eine nachgebildete API;
    Trockenlauf gegen ein lokales Bare-Repo (signierter annotierter Tag, Fast-Forward, nie Force); --probe zeigt den ganzen
    Plan; Release-Prüfung findet das Programm im Quellbaum (Me-Goos-ta-Deutsch/). Ohne werkstatt/ entfallen alle 5."""
    print("\n[E55] Veröffentlichung: Token, signierter Tag, unveränderliche Releases")
    import contextlib
    import hashlib
    import importlib.util
    import io
    import types
    import zipfile
    import signatur as sg
    t0 = time.time()
    arbeit = HIER.parent.parent
    vw_pfad, vr_pfad = arbeit / "werkstatt" / "veroeffentliche_webapp.py", arbeit / "werkstatt" / "veroeffentliche_release.py"
    nr_pfad = arbeit / ".github" / "ci" / "neuestes_release.py"
    if not (vw_pfad.is_file() and vr_pfad.is_file() and nr_pfad.is_file()):
        print("  (werkstatt/ und .github/ liegen nur im Quellbaum – Prüfungen entfallen)")
        return

    def modul(pfad, name):
        spec = importlib.util.spec_from_file_location(name, pfad)
        m = importlib.util.module_from_spec(spec)
        sys.dont_write_bytecode, vorher = True, sys.dont_write_bytecode
        try:
            spec.loader.exec_module(m)
        finally:
            sys.dont_write_bytecode = vorher
        return m

    def ende(f, *a, **k):
        """→ (Ergebnis oder None, Abbruch-Text oder None, Ausgabe)"""
        aus = io.StringIO()
        try:
            with contextlib.redirect_stdout(aus):
                return f(*a, **k), None, aus.getvalue()
        except SystemExit as e:
            return None, str(e.code), aus.getvalue()
    # 1) Token-Reihenfolge + Rechte (nachgebildet)
    vw = modul(vw_pfad, "vw_e55")
    gerufen = []
    vw.sys = types.SimpleNamespace(platform="win32", argv=[], exit=sys.exit)
    vw._gh_cli = lambda: gerufen.append("gh") or "tok-gh"
    vw._github_desktop = lambda: gerufen.append("desktop") or "tok-desktop"
    alt_env = {n: os.environ.pop(n, None) for n in ("GH_TOKEN", "GITHUB_TOKEN")}
    try:
        os.environ["GH_TOKEN"] = "tok-env"
        vw._anmeldeinformation = lambda ziel: "tok-cred" if ziel == "MGD-Release-Token" else None
        a = ende(vw.token)
        os.environ.pop("GH_TOKEN")
        b = ende(vw.token)
        d = ende(vw.token, desktop=True)                      # ausdrücklich: breite Anmeldung statt des eigenen Tokens
        vw._anmeldeinformation = lambda ziel: None
        c = ende(vw.token)
    finally:
        for n, v in alt_env.items():
            os.environ.pop(n, None)
            if v is not None:
                os.environ[n] = v
    antworten = {"/repos/k/r": 200, "/repos/k/r/commits?per_page=1": 200, "/repos/k/r/actions/permissions": 403}
    vw.api = lambda m, weg, tok, daten=None, ok=(): (antworten.get(weg, 200), {})
    r_ok = ende(vw.rechte_pruefen, "t", "k", "r", ("contents",))
    r_fehlt = ende(vw.rechte_pruefen, "t", "k", "r", ("contents", "administration"))
    antworten["/repos/k/r"] = 404
    r_repo = ende(vw.rechte_pruefen, "t", "k", "r", ("contents",))
    pruefe("Token: GH_TOKEN → Anmeldeinformation MGD-Release-Token → ohne Token Abbruch mit Anleitung (GitHub CLI/Desktop "
           "unberührt); nur ausdrücklich mit --desktop-anmeldung die breite Anmeldung mit „Achtung: breiter Zugriff“; Rechte-Prüfung "
           "nennt das fehlende Token-Recht",
           a[0] == ("tok-env", "GH_TOKEN") and b[0] == ("tok-cred", "Windows-Anmeldeinformation MGD-Release-Token")
           and c[0] is None and "MGD-Release-Token" in c[1] and "Fine-grained" in c[1] and gerufen == ["gh"]
           and d[0] == ("tok-gh", "GitHub CLI (breiter Zugriff)") and "Achtung: breiter Zugriff" in d[2]
           and r_ok[0] is True and r_fehlt[1] and "Administration (Read and write)" in r_fehlt[1]
           and r_repo[1] and "Repository access" in r_repo[1] and not re.search(r"(?i)\bwarn(ing|ung)\b", c[1] + d[2]),
           (a, b, c[1], d, gerufen, r_fehlt[1], r_repo[1]))
    # 2) kein --ersetzen, kein Force
    vr = modul(vr_pfad, "vr_e55")
    q = vr_pfad.read_text(encoding="utf-8")
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1", GH_TOKEN="",
               HTTPS_PROXY="http://127.0.0.1:9", HTTP_PROXY="http://127.0.0.1:9")
    ers = subprocess.run([sys.executable, str(vr_pfad), "a", "b.zip", "--ersetzen"], env=env, capture_output=True, text=True,
                         encoding="utf-8", errors="replace", timeout=120)
    pruefe("Kein --ersetzen und kein Force: Aufruf mit --ersetzen endet mit Hinweis „neue Patch-Version“; kein main_pushen, "
           "kein Tag-Verschieben, kein --force im Skript",
           ers.returncode != 0 and "Patch-Version" in ers.stderr and "Traceback" not in ers.stderr
           and not hasattr(vr, "main_pushen") and '"--force"' not in q and "force=True" not in q and "git/refs/tags" not in q
           and '"push", "--atomic"' in q, ers.stderr[-300:])
    # 3) Entwurf → Prüfen → Veröffentlichen gegen eine nachgebildete API
    seed, sid = hashlib.sha256(b"mgd-e55-testschluessel").digest(), b"MGDTEST5"
    test_mod = types.SimpleNamespace(KOMMENTAR=sg.KOMMENTAR, pruefe=lambda n, m, s, k: sg.pruefe(
        n, m, [("test", sid, sg.ed25519_oeffentlich(seed))], k))
    daten = b"PK-e55-zip"
    summen = f"{hashlib.sha256(daten).hexdigest()}  Me-Goos-ta-Deutsch-9.9.zip\n"
    ms = sg.signiere(seed, sid, summen.encode(), "me-goos-ta-deutsch v9.9")
    p = dict(version="9.9", tag="v9.9", titel="Me Goos-ta Deutsch 9.9", notizen="n", summen=summen, sha256=hashlib.sha256(daten).hexdigest(),
             assets=["Me-Goos-ta-Deutsch-9.9.zip", "SHA256SUMS.txt", "SHA256SUMS.txt.minisig"],
             download="https://github.com/k/r/releases/download/v9.9/Me-Goos-ta-Deutsch-9.9.zip")

    class Nachbildung:
        def __init__(self, kaputt=None):
            self.log, self.kaputt, self.ablage = [], kaputt, {}

        def api(self, m, rest, d=None):
            self.log.append((m, rest, dict(d or {}).get("draft")))
            return (201 if m == "POST" else 200), {"id": 7, "upload_url": "u{?name}", "html_url": "h"}

        def hochladen(self, rel, name, d, typ):
            self.log.append(("hoch", name, None))
            self.ablage[name] = d
            return {"url": name}

        def asset(self, a):
            self.log.append(("asset", a["url"], None))
            return b"falsch" if a["url"] == self.kaputt else self.ablage[a["url"]]

        def oeffentlich(self, url, versuche=12):
            self.log.append(("oeffentlich", url.rsplit("/", 1)[1], None))
            return self.ablage[url.rsplit("/", 1)[1]]
    gut, schlecht = Nachbildung(), Nachbildung(kaputt="Me-Goos-ta-Deutsch-9.9.zip")
    g1 = ende(vr.release_schritte, gut, p, daten, ms, test_mod)
    g2 = ende(vr.release_schritte, schlecht, p, daten, ms, test_mod)
    arten = [x[0] if x[0] in ("hoch", "asset", "oeffentlich") else f"{x[0]} {x[1]} {x[2]}" for x in gut.log]
    soll = ["POST /releases True", "hoch", "hoch", "hoch", "asset", "asset", "asset", "PATCH /releases/7 False",
            "oeffentlich", "oeffentlich", "oeffentlich"]
    pruefe("Release-Schritte (nachgebildete API): Entwurf → 3 Assets hoch → angemeldet laden + Signatur prüfen → erst dann "
           "veröffentlichen → öffentlich prüfen; falsches Asset im Entwurf → Entwurf gelöscht, nie veröffentlicht",
           g1[1] is None and arten == soll and g2[1] and "nichts veröffentlicht" in g2[1]
           and ("DELETE", "/releases/7", None) in schlecht.log and not any(x[0] == "PATCH" for x in schlecht.log)
           and list(vr.REIHENFOLGE).index("angemeldet pruefen") < list(vr.REIHENFOLGE).index("veroeffentlichen"),
           (arten, g1[1], g2[1], schlecht.log[-3:]))
    # 4) Trockenlauf gegen ein lokales Bare-Repo
    import veroeffentliche_webapp as vw_echt
    git = vw_echt.git_exe()
    kg = next((str(k) for k in (Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "OpenSSH" / "ssh-keygen.exe",
                                Path(shutil.which("ssh-keygen") or "-")) if Path(k).is_file()), None)
    befund = {}
    if kg:
        w, bare, kd = tmp / "e55-werk", tmp / "e55-bare.git", tmp / "e55-key"
        kd.mkdir()
        subprocess.run([kg, "-q", "-t", "ed25519", "-N", "", "-C", "e55", "-f", str(kd / "k")], capture_output=True)
        (kd / "erlaubt").write_text(f"e55@users.noreply.github.com {(kd / 'k.pub').read_text().strip()}\n", encoding="ascii")

        def g(*a, cwd=w):
            return subprocess.run([git, *a], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        w.mkdir()
        g("init", "-q", "-b", "main")
        for k, v in (("user.name", "E55"), ("user.email", "e55@users.noreply.github.com"), ("gpg.format", "ssh"),
                     ("user.signingkey", str(kd / "k.pub")), ("gpg.ssh.program", kg), ("core.autocrlf", "false"),
                     ("gpg.ssh.allowedSignersFile", str(kd / "erlaubt")), ("commit.gpgsign", "true"), ("tag.gpgsign", "true")):
            g("config", "--local", k, v)
        (w / "Me-Goos-ta-Deutsch").mkdir()
        (w / "Me-Goos-ta-Deutsch" / "a.txt").write_bytes(b"eins\r\n")
        g("add", "-A")
        g("commit", "-q", "-m", "eins")
        g("init", "-q", "--bare", str(bare), cwd=tmp)
        g("push", "-q", str(bare), "HEAD:refs/heads/main")
        (w / "Me-Goos-ta-Deutsch" / "b.txt").write_bytes(b"zwei\n")
        g("add", "-A")
        g("commit", "-q", "-m", "zwei")
        head = g("rev-parse", "HEAD").stdout.strip()
        rel = tmp / "e55-rel"
        rel.mkdir()
        for n in ("a.txt", "b.txt"):
            shutil.copyfile(w / "Me-Goos-ta-Deutsch" / n, rel / n)
        st_gut = vr.quellbaum_stand(rel, ["a.txt", "b.txt"], "9.9", w)
        r1 = ende(vr.tag_und_pushen, w, str(bare), head, "9.9", None, "Me Goos-ta Deutsch 9.9")
        r2 = ende(vr.tag_und_pushen, w, str(bare), head, "9.9", None, "Me Goos-ta Deutsch 9.9")
        tag_obj = g("cat-file", "-p", "refs/tags/v9.9", cwd=bare).stdout
        befund.update(stand=st_gut["hindernisse"], r1=r1[1], r2=(r2[0] or [None, None])[1],
                      main=g("rev-parse", "refs/heads/main", cwd=bare).stdout.strip() == head,
                      signiert="-----BEGIN SSH SIGNATURE-----" in tag_obj and tag_obj.startswith(f"object {head}"))
        # fremder Stand auf dem Server: main dort weiter als HEAD → kein Fast-Forward → Abbruch, Server unverändert
        anders = tmp / "e55-anders"
        g("clone", "-q", "-b", "main", str(bare), str(anders), cwd=tmp)
        for k, v in (("user.name", "E55"), ("user.email", "e55@users.noreply.github.com"), ("commit.gpgsign", "false")):
            g("config", "--local", k, v, cwd=anders)
        (anders / "c.txt").write_text("drei", encoding="utf-8")
        g("add", "-A", cwd=anders)
        g("commit", "-q", "-m", "drei", cwd=anders)
        g("push", "-q", "origin", "HEAD:refs/heads/main", cwd=anders)
        server = g("rev-parse", "refs/heads/main", cwd=bare).stdout.strip()
        (w / "Me-Goos-ta-Deutsch" / "b.txt").write_bytes(b"zwei!\n")
        st_offen = vr.quellbaum_stand(rel, ["a.txt", "b.txt", "c.txt"], "9.9", w)
        g("add", "-A")
        g("commit", "-q", "-m", "vier")
        r3 = ende(vr.tag_und_pushen, w, str(bare), g("rev-parse", "HEAD").stdout.strip(), "9.10", None, "9.10")
        befund.update(r3=r3[1], unveraendert=g("rev-parse", "refs/heads/main", cwd=bare).stdout.strip() == server,
                      kein_tag=g("rev-parse", "-q", "--verify", "refs/tags/v9.10", cwd=bare).returncode != 0,
                      offen=st_offen["hindernisse"])
    pruefe("Trockenlauf Bare-Repo: signierter annotierter Tag auf HEAD, main per Fast-Forward + Tag in einem Push, zweiter Lauf "
           "pusht nichts; main auf dem Server weiter → Abbruch ohne Push (kein Force); Quellbaum-Stand erkennt sauber/geändert",
           bool(kg) and befund.get("stand") == [] and befund.get("r1") is None and befund.get("main") and befund.get("signiert")
           and befund.get("r2") == [] and befund.get("r3") and "Fast-Forward" in befund["r3"] and befund.get("unveraendert")
           and befund.get("kein_tag") and any("nicht sauber" in h for h in befund.get("offen", []))
           and any("≠" in h for h in befund.get("offen", [])), befund)
    # 5) --probe: ganzer Plan; Release-Prüfung im Quellbaum-Layout
    rel36 = tmp / "e36-release"
    zips = sorted(rel36.glob("Me-Goos-ta-Deutsch-*.zip"))
    pr = subprocess.run([sys.executable, str(vr_pfad), str(rel36 / "Me-Goos-ta-Deutsch"), str(zips[0] if zips else "x.zip"),
                         "--probe", "--ohne-ci", "E55 prüft nur den Plan"], env=env, capture_output=True, text=True,
                        encoding="utf-8", errors="replace", timeout=300)
    mp = re.search(r"^#plan (.*)$", pr.stdout, re.M)
    plan = json.loads(mp.group(1)) if mp else {}
    nr = modul(nr_pfad, "nr_e55")
    co = tmp / "e55-checkout"
    for n, d in (("Me-Goos-ta-Deutsch/README.md", b"Gans"), ("Me-Goos-ta-Deutsch/Programm/a.py", b"x"),
                 ("Me-Goos-ta-Deutsch/Programm/__pycache__/a.pyc", b"!"), ("werkstatt/w.py", b"w"), (".github/x.yml", b"y")):
        (co / n).parent.mkdir(parents=True, exist_ok=True)
        (co / n).write_bytes(d)
    z = tmp / "e55.zip"
    with zipfile.ZipFile(z, "w") as f:
        f.writestr("Me-Goos-ta-Deutsch/README.md", b"Gans")
        f.writestr("Me-Goos-ta-Deutsch/Programm/a.py", b"x")
    wf = (arbeit / ".github" / "workflows" / "release_pruefung.yml").read_text(encoding="utf-8")
    pruefe("--probe zeigt den ganzen Plan (Quellbaum-HEAD, signierter Tag, Fast-Forward ohne Force, Reihenfolge Entwurf → Prüfen → "
           "Veröffentlichen, unveränderlich, Hindernisse); Release-Prüfung am Release (release: published) findet Programm/ unter "
           "Me-Goos-ta-Deutsch/ und ignoriert __pycache__",
           pr.returncode == 0 and plan.get("reihenfolge") == list(vr.REIHENFOLGE) and plan.get("unveraenderlich") is True
           and plan.get("push", {}).get("force") is False and re.fullmatch(r"[0-9a-f]{40}", str(plan.get("quellbaum", {}).get("head")))
           and isinstance(plan.get("hindernisse"), list) and "signiert + annotiert" in pr.stdout
           and nr.programm_wurzel(co) == co / "Me-Goos-ta-Deutsch" and nr.programm_wurzel(co / "Me-Goos-ta-Deutsch") == co / "Me-Goos-ta-Deutsch"
           and nr.abweichungen(z, co) == [] and "  release:\n    types: [published]\n" in wf,
           ((pr.stdout + pr.stderr)[-400:], nr.abweichungen(z, co) if z.is_file() else None))
    print(f"  E55 {time.time() - t0:.1f} s")


E56_MIT = ("Permission is hereby granted, free of charge, to any person obtaining a copy", "THE SOFTWARE IS PROVIDED \"AS IS\"",
           "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.\n")


def test_auftritt(tmp):
    """E56 (2.5): Auftritt und Doku – LICENSE.txt = reiner MIT-Text (GitHub erkennt MIT), Wurzel-LICENSE gleich; Wurzel-README
    mit Bildern (vorhanden, je < 300 KB, Alt-Text), Badges und Links nur auf dieses Repo bzw. web_adresse.txt (Bilder der
    Badges von GitHub, shields.io, securityscorecards.dev – jeweils für dieses Repo); CHANGELOG.md (Keep a Changelog) mit
    einem Abschnitt je Version, im Release; ZIP-README nur „New in“ der neuesten Version; Datenschutz-Abschnitt der
    Download-Seite in de/en/es gleich gegliedert; Handy-Zugang „nie in öffentlichen Netzen“ in Hover, Hinweis und
    Leitfäden. Ohne Quellbaum (README/LICENSE an der Wurzel, werkstatt/) entfallen 3 der 5 Prüfungen."""
    print("\n[E56] Auftritt: README, Bilder, CHANGELOG, Lizenz, Datenschutz")
    import gans_lernkarten as gl
    t0 = time.time()
    oben = HIER.parent
    arbeit = oben.parent
    lic = (oben / "LICENSE.txt").read_bytes()
    lt = lic.decode("utf-8")
    pruefe("LICENSE.txt = reiner MIT-Text (nur Titel, Copyright „Eine Gans namens Lukas“, Erlaubnis, Haftung) – ohne Zusatzzeilen",
           lt.startswith("MIT License\n\nCopyright (c) 2026 Eine Gans namens Lukas\n\n") and all(s in lt for s in E56_MIT)
           and lt.endswith(E56_MIT[2]) and len(lt.split("\n\n")) == 5 and "\r" not in lt and "DRITTLIZENZEN" not in lt, lt[-200:])
    cl = (oben / "CHANGELOG.md").read_text(encoding="utf-8")
    abschnitte = re.findall(r"^## \[([^\]]+)\](.*)$", cl, re.M)
    versionen = [v for v, _ in abschnitte]
    kategorien = set(re.findall(r"^### (.+)$", cl, re.M))
    readme_zip = (oben / "README.md").read_text(encoding="utf-8")
    rel_liste = (arbeit / "werkstatt" / "bau_release.py").read_text(encoding="utf-8") if (arbeit / "werkstatt").is_dir() else '"CHANGELOG.md"'
    pruefe("CHANGELOG.md (Keep a Changelog): [Unreleased] zuerst, je Version ein Abschnitt mit Datum (1.6 … aktuelle Version), nur "
           "Standard-Kategorien, Links nur auf dieses Repo; im Release; ZIP-README nur „New in“ der neuesten Version + Verweis",
           versionen[:1] == ["Unreleased"] and {"1.6", "2.0", "2.1", "2.2", "2.3", "2.4", gl.VERSION.split()[0]} <= set(versionen)
           and all(re.fullmatch(r" – \d{4}-\d{2}-\d{2}", d) for v, d in abschnitte if v != "Unreleased")
           and len(versionen) == len(set(versionen)) and kategorien <= {"Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"}
           and all(u.startswith("https://github.com/lukasdiegans/me-goos-ta-deutsch/") or u.startswith("https://keepachangelog.com/")
                   for u in re.findall(r"https?://[^\s)>\]]+", cl))
           and '"CHANGELOG.md"' in rel_liste and len(re.findall(r"^## New in ", readme_zip, re.M)) == 1 and "CHANGELOG.md" in readme_zip,
           (versionen, kategorien))
    readme = arbeit / "README.md"
    if not (readme.is_file() and (arbeit / "LICENSE").is_file() and (arbeit / "werkstatt" / "bau_webapp.py").is_file()):
        print("  (README/LICENSE an der Wurzel und werkstatt/ gibt es nur im Quellbaum – 3 Prüfungen entfallen)")
        return
    rt = readme.read_text(encoding="utf-8")
    wa = (HIER / "web_adresse.txt").read_text(encoding="utf-8").strip().splitlines()[0].strip()
    m = re.match(r"^https://([a-z0-9-]+)\.github\.io/([A-Za-z0-9._-]+)/$", wa)
    repo = f"https://github.com/{m.group(1)}/{m.group(2)}/"
    bilder = re.findall(r"!\[([^\]]*)\]\(([^)\s]+)\)", rt) + [(a, s) for s, a in re.findall(r'<img src="([^"]+)"[^>]*alt="([^"]*)"', rt)]
    lokal = [(a, s) for a, s in bilder if not s.startswith("https://")]
    gross = [s for _, s in lokal if not (arbeit / s).is_file() or (arbeit / s).stat().st_size >= 300 * 1024]
    from PIL import Image
    sp = arbeit / "docs" / "social-preview.png"
    with Image.open(sp) as b:
        sp_mass = b.size
    pruefe("Wurzel-README: Bilder (Start, Karte, Lernen, Druck, Handy) vorhanden, je < 300 KB, mit Alt-Text; docs/social-preview.png "
           "1280×640 < 1 MB; LICENSE an der Wurzel = LICENSE.txt",
           len(lokal) >= 6 and not gross and all(a.strip() for a, _ in lokal)
           and {f"docs/bilder/{n}.png" for n in ("start", "karte", "lernen", "druck", "handy")} <= {s for _, s in lokal}
           and sp_mass == (1280, 640) and sp.stat().st_size < 1024 * 1024 and (arbeit / "LICENSE").read_bytes() == lic,
           (gross, sp_mass, [s for _, s in lokal]))
    links = re.findall(r'href="([^"]+)"', rt) + re.findall(r"\]\((https?://[^)\s]+)\)", rt) + re.findall(r"(?<![\"(])(https://[^\s)<\"]+)", rt)
    quellen = [s for s in re.findall(r'src="(https://[^"]+)"', rt)]
    eigen = lambda u: u.startswith(repo) or u.startswith(wa)                       # noqa: E731
    badge = lambda u: (u.startswith(repo + "actions/workflows/") or u.startswith(f"https://img.shields.io/github/v/release/{m.group(1)}/{m.group(2)}")
                       or u.startswith("https://img.shields.io/badge/license-MIT")
                       or u == f"https://api.securityscorecards.dev/projects/github.com/{m.group(1)}/{m.group(2)}/badge")  # noqa: E731
    fremd = [u for u in links if u.startswith("http") and not eigen(u) and not badge(u)] + [u for u in quellen if not badge(u)]
    pruefe("Wurzel-README: Badges (Release, Lizenz, Tests, Release-Prüfung, Scorecard) und alle Links nur auf dieses Repository "
           "bzw. web_adresse.txt; Download-Knopf, Datenschutz, Entwickler-Teil, Kurzfassung de/es",
           not fremd and len(quellen) == 5 and f'href="{wa}download/"' in rt and "## Privacy and security" in rt
           and "## For developers" in rt and "## Deutsch (kurz)" in rt and "## Español (breve)" in rt
           and not re.search(r"(?i)\bwarn(ing|ung)\b", rt), fremd[:5])
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    b = subprocess.run([sys.executable, str(arbeit / "werkstatt" / "bau_webapp.py"), str(oben), str(tmp / "e56-web"), "--ohne-pyodide",
                        "--ohne-modelle"], env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    html = (tmp / "e56-web" / "web-app" / "download" / "index.html").read_text(encoding="utf-8") if b.returncode == 0 else ""
    teile = {l: (re.search(rf'<section class="abschnitt hell datenschutz" id="{l}-datenschutz">(.*?)</section>', html, re.S) or [None, ""])[1]
             for l in ("de", "en", "es")}
    seite = (HIER / "ui" / "index.html").read_text(encoding="utf-8")
    leit = {n: (HIER / n).read_text(encoding="utf-8") for n in ("LEITFADEN.md", "LEITFADEN_en.md", "LEITFADEN_es.md")}
    erw = (HIER / "erweiterungen.py").read_text(encoding="utf-8")
    pruefe("Datenschutz auf der Download-Seite (de/en/es gleich gegliedert: Titel, Einleitung, 4 Punkte mit GitHub Pages/IP, "
           "Übersetzung, Handy-Zugang); Handy-Zugang „nie in öffentlichen Netzen“ in Hinweis, Werkzeug und Leitfäden; Leitfäden nennen GitHub Pages",
           all(x.count("<li>") == 4 and x.count("<h2>") == 1 and "GitHub Pages" in x and "IP" in x for x in teile.values())
           and all(re.search(p, seite) for p in (r"lan_warnung: \"[^\"]*nie in öffentlichen", r"lan_warnung: \"[^\"]*never in public",
                                                 r"lan_warnung: \"[^\"]*nunca en redes wifi públicas"))
           and all(s in erw for s in ("nie in öffentlichen WLANs", "never in public Wi-Fi", "nunca en wifi públicas"))
           and "nie in öffentlichen oder fremden Netzen" in leit["LEITFADEN.md"] and "Never switch it on in public" in leit["LEITFADEN_en.md"]
           and "Nunca lo actives en redes públicas" in leit["LEITFADEN_es.md"] and all("GitHub Pages" in t for t in leit.values()),
           ({l: x.count("<li>") for l, x in teile.items()}, (b.stdout + b.stderr)[-300:]))
    print(f"  E56 {time.time() - t0:.1f} s")


def main():
    global ECHTES_KI_BILD, ECHT_DA
    t0 = time.time()
    import ki_bild
    ECHTES_KI_BILD = ki_bild.modell_ordner()          # vor den Tests, die MGD_DATEN umstellen
    ECHT_DA = ki_bild.status(ECHTES_KI_BILD)["installiert"]
    if ECHT_DA:                                       # Test-Server und seine Läufe finden das echte Modell
        os.environ["MGD_KI_BILD"] = str(ECHTES_KI_BILD)
    with tempfile.TemporaryDirectory() as tmp:
        p = tg.kopiere_projekt(Path(tmp) / "projekt")
        shutil.copy2(HIER / "erweiterungen.py", p / "erweiterungen.py")
        shutil.copy2(HIER / "ki_bild.py", p / "ki_bild.py")
        shutil.copy2(HIER / "tools.py", p / "tools.py")
        shutil.copy2(HIER / "sprachen.py", p / "sprachen.py")
        shutil.copy2(HIER / "lernkarten_digital.py", p / "lernkarten_digital.py")
        shutil.copy2(HIER / "lernen.py", p / "lernen.py")
        shutil.copy2(HIER / "verlauf.py", p / "verlauf.py")
        shutil.copy2(HIER / "aktualisieren.py", p / "aktualisieren.py")
        shutil.copy2(HIER / "signatur.py", p / "signatur.py")
        shutil.copy2(HIER.parent / "Me Goos-ta Deutsch - Linux.sh", p.parent / "Me Goos-ta Deutsch - Linux.sh")
        daten = Path(tmp) / "daten"
        daten.mkdir()
        test_server(p, daten)
        test_starter(p, daten)
        test_mac(Path(tmp) / "mac")
        test_linux(p, Path(tmp) / "linux")
        test_woerter()
        test_ki_faltung()
        test_ki_bild_laden(Path(tmp) / "ki-bild")
        test_ki_bild_text(ECHTES_KI_BILD)
        test_ki_bild_netz(ECHTES_KI_BILD)
        test_ki_bild_prompt(ECHTES_KI_BILD)
        test_ki_bild_plattform()
        test_hilfe_markdown(p, daten)
        test_spanisch()
        test_warteschlange(p, daten)
        test_tools(p, Path(tmp))
        test_tools_anbinden(p, Path(tmp))
        test_farben(p, Path(tmp))
        test_sprachen(p, Path(tmp))
        test_sprachen_oberflaeche(p, Path(tmp))
        test_sprachen_druck(p, Path(tmp))
        test_lernen(p, Path(tmp))
        test_lernen_oberflaeche(p, Path(tmp))
        test_web_logik(p, Path(tmp))
        test_web_app(p, Path(tmp))
        test_installationsdateien()
        test_fehleranalyse(Path(tmp))
        test_englisch_vorab(p, Path(tmp))
        test_rueckseite_gans(Path(tmp))
        test_download_seite(Path(tmp))
        test_status_englisch(Path(tmp))
        test_ci(Path(tmp))
        test_ci_browser(Path(tmp))
        test_aussprache(Path(tmp))
        test_neue_version(p, Path(tmp))
        test_wortliste(p, Path(tmp))
        test_wortliste_oberflaeche(p, Path(tmp))
        test_fix_download_release(Path(tmp))
        test_bild_ki_ideen(p, Path(tmp))
        test_gans_pruefung(p, Path(tmp))
        test_rueckgaengig(p, Path(tmp))
        test_update(p, Path(tmp))
        test_oberflaeche_24()
        test_github_auftritt(Path(tmp))
        test_signatur(Path(tmp))
        test_paket_fassungen(Path(tmp))
        test_quellbaum(Path(tmp))
        test_ci_quellbaum(Path(tmp))
        test_veroeffentlichung(Path(tmp))
        test_auftritt(Path(tmp))
    ok =sum(1 for e in tg.ergebnisse if e[1])
    print(f"\n{ok} von {len(tg.ergebnisse)} Prüfungen bestanden ({time.time() - t0:.0f} s).")
    if ok == len(tg.ergebnisse):
        print("ALLE TESTS BESTANDEN")
        return 0
    for name, gut, detail in tg.ergebnisse:
        if not gut:
            print(f"  FEHLER  {name}  {detail}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
