#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ME GOOS-TA DEUTSCH – Neue Version direkt im Programm übernehmen     Version 2.4 (22.10.2026)
=============================================================================================
Bis 2.3 hieß ein Update: ZIP laden, in einen neuen Ordner entpacken, Karten übernehmen – danach lagen zwei Ordner da
(oder der neue hatte denselben Namen wie der alte). Seit 2.4 geht es an Ort und Stelle, nur auf Klick
(Werkzeuge → „Jetzt aktualisieren“, nachdem „Nach neuer Version suchen“ eine neuere gefunden hat):

1. laden (Auftrag in der Warteschlange):  SHA256SUMS.txt und Me-Goos-ta-Deutsch-<V>.zip des GitHub-Releases v<V>
   (Adresse nur aus web_adresse.txt + Versionsnummer, nie aus einer Antwort; Weiterleitungen nur zu GitHub), Prüfsumme
   vergleichen, ZIP prüfen (nur Me-Goos-ta-Deutsch/…, keine Links/Ausbrüche, Pflichtdateien, Version = <V>, keine
   Nutzerdaten) und nach <Datenordner>/update/neu entpacken → bereit.json.
2. anwenden (eigener Prozess, nachdem sich die Oberfläche beendet hat): jede Datei des Releases ersetzt die alte
   (die alte kommt vorher nach update/alt; bei einem Fehler wird alles zurückgelegt). Karten, Bilder, Ideen, Lernstand,
   Einstellungen, Ausgaben und Modelle bleiben unberührt – sie stehen nie im Release. Danach startet die Startdatei
   den Ordner neu (sie richtet bei Bedarf Python und Pakete ein, wie beim ersten Start); update/ergebnis.json meldet
   der Oberfläche, wie es lief.
Nur Standardbibliothek (anwenden läuft ohne Pakete). Selbsttest: test_erweiterungen.py (Abschnitt E48).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import zipfile
from pathlib import Path

HIER = Path(__file__).resolve().parent                  # …/Programm
WURZEL_NAME = "Me-Goos-ta-Deutsch"
ZIP_MUSTER = "Me-Goos-ta-Deutsch-{v}.zip"
MAX_ZIP = 200 * 1024 * 1024
MAX_ENTPACKT = 500 * 1024 * 1024
MAX_DATEIEN = 5000
MAX_SUMMEN = 64 * 1024
GITHUB_HOSTS = ("github.com", "objects.githubusercontent.com", "release-assets.githubusercontent.com")
PFLICHT = ("Programm/starter.py", "Programm/gans_ui.py", "Programm/gans_lernkarten.py",
           "Me Goos-ta Deutsch - Windows.cmd", "Me Goos-ta Deutsch - Mac.command", "Me Goos-ta Deutsch - Linux.sh")
# Eigene Daten im Programmordner – stehen nie im Release und werden beim Ersetzen nie angefasst
NUTZER = re.compile(r"^Programm/(karten\.csv|karten\.bak\.csv|ui_einstellungen\.json|ideen\.json|lernstand[^/]*\.json"
                    r"|(bilder|ideen|ausgabe|_beispiele)/.*|assets/gans_hintergrund\.[^/]+|assets/_alt/.*"
                    r"|modelle/realesrgan[^/]*\.npz|.*__pycache__/.*)$", re.I)
START = {"win": "Me Goos-ta Deutsch - Windows.cmd", "mac": "Me Goos-ta Deutsch - Mac.command",
         "linux": "Me Goos-ta Deutsch - Linux.sh"}


def _t(de, en, es):
    s = (os.environ.get("MGD_SPRACHE") or "en")[:2].lower()
    return {"en": en, "es": es}.get(s, de)


class UpdateFehler(Exception):
    """Verständlicher Grund (schon übersetzt), warum es nicht geht – nichts wurde geändert."""


def version_ok(v):
    return bool(re.fullmatch(r"\d{1,4}\.\d{1,4}(\.\d{1,4})?", str(v or "")))


def ordner(daten):
    return Path(daten) / "update"


# =============================================================================================
# 1. Laden und prüfen
# =============================================================================================
def _oeffne(url, erlaubt, timeout=60):
    """GET mit Zertifikatsprüfung; folgt Weiterleitungen nur zu erlaubten Hosts (https, bzw. http nur für 127.0.0.1)."""
    import urllib.error
    import urllib.request

    def host_ok(u):
        p = urllib.parse.urlsplit(u)
        return (p.hostname or "") in erlaubt and (p.scheme == "https" or (p.scheme == "http" and p.hostname == "127.0.0.1"))

    class Weiter(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, kopf, neu):
            if not host_ok(neu):
                raise UpdateFehler(_t(f"Unerwartete Weiterleitung zu {urllib.parse.urlsplit(neu).hostname} – abgebrochen.",
                                      f"Unexpected redirect to {urllib.parse.urlsplit(neu).hostname} – stopped.",
                                      f"Redirección inesperada a {urllib.parse.urlsplit(neu).hostname}; se detuvo."))
            return super().redirect_request(req, fp, code, msg, kopf, neu)

    if not host_ok(url):
        raise UpdateFehler(_t("Unerwartete Adresse – abgebrochen.", "Unexpected address – stopped.",
                              "Dirección inesperada; se detuvo."))
    try:
        from ki_modelle import ssl_kontexte                    # System → truststore → certifi (wie Tool-Downloads)
        kontexte = ssl_kontexte()
    except Exception:  # noqa: BLE001
        import ssl
        kontexte = [ssl.create_default_context()]
    letzter = None
    for kontext in kontexte:
        opener = urllib.request.build_opener(Weiter(), urllib.request.HTTPSHandler(context=kontext))
        try:
            return opener.open(urllib.request.Request(url, headers={"User-Agent": "Me-Goos-ta-Deutsch"}), timeout=timeout)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise UpdateFehler(_t("Dieses Release gibt es (noch) nicht auf GitHub.", "This release isn’t on GitHub (yet).",
                                      "Esta versión (todavía) no está en GitHub.")) from None
            raise UpdateFehler(f"HTTP {e.code}") from None
        except urllib.error.URLError as e:
            import ssl
            letzter = e
            if not isinstance(getattr(e, "reason", None), ssl.SSLCertVerificationError):
                break
    raise UpdateFehler(_t(f"Keine Verbindung zu GitHub ({getattr(letzter, 'reason', letzter)}) – bitte mit Internet "
                          "nochmal versuchen.",
                          f"No connection to GitHub ({getattr(letzter, 'reason', letzter)}) – please try again with internet.",
                          f"Sin conexión con GitHub ({getattr(letzter, 'reason', letzter)}); inténtalo de nuevo con internet."))


def _lies(antwort, ziel, grenze, melde=None):
    """Antwort in eine Datei schreiben (höchstens grenze Bytes) → SHA-256."""
    h, n, schritt = hashlib.sha256(), 0, 0
    gesamt = int(antwort.headers.get("Content-Length") or 0)
    with open(ziel, "wb") as f:
        for block in iter(lambda: antwort.read(1 << 20), b""):
            n += len(block)
            if n > grenze:
                raise UpdateFehler(_t("Datei unerwartet groß – abgebrochen.", "File unexpectedly large – stopped.",
                                      "Archivo inesperadamente grande; se detuvo."))
            h.update(block)
            f.write(block)
            if melde and gesamt and n * 10 // gesamt > schritt:
                schritt = n * 10 // gesamt
                melde(f"  {schritt * 10} %  ({n / 1048576:.1f} / {gesamt / 1048576:.1f} MB)")
    return h.hexdigest()


def pruefe_zip(pfad, version):
    """Ist das ein echtes Release-ZIP dieser Version? Gibt die Liste der Dateien (ZipInfo) zurück."""
    def nein(de, en, es):
        raise UpdateFehler(_t(de, en, es))

    try:
        z = zipfile.ZipFile(pfad)
    except (zipfile.BadZipFile, OSError):
        nein("Das ZIP ist beschädigt.", "The ZIP is damaged.", "El ZIP está dañado.")
    with z:
        infos = [i for i in z.infolist() if not i.is_dir()]
        if not infos or len(infos) > MAX_DATEIEN or sum(i.file_size for i in infos) > MAX_ENTPACKT:
            nein("Das ZIP hat einen unerwarteten Umfang.", "The ZIP has an unexpected size.", "El ZIP tiene un tamaño inesperado.")
        namen = set()
        for i in infos:
            n = i.filename
            teile = n.split("/")
            if (not n.startswith(WURZEL_NAME + "/") or "\\" in n or ":" in n or any(t in ("", ".", "..") for t in teile)
                    or (i.external_attr >> 16) & 0o170000 == 0o120000):
                nein(f"Unerwarteter Eintrag im ZIP: {n[:80]}", f"Unexpected entry in the ZIP: {n[:80]}",
                     f"Entrada inesperada en el ZIP: {n[:80]}")
            rel = n[len(WURZEL_NAME) + 1:]
            if NUTZER.match(rel):
                nein(f"Das ZIP enthält eigene Daten ({rel[:60]}) – so sieht kein Release aus.",
                     f"The ZIP contains personal data ({rel[:60]}) – that’s not what a release looks like.",
                     f"El ZIP contiene datos propios ({rel[:60]}); así no es una versión publicada.")
            namen.add(rel)
        fehlt = [p for p in PFLICHT if p not in namen]
        if fehlt:
            nein(f"Im ZIP fehlt {fehlt[0]}.", f"The ZIP lacks {fehlt[0]}.", f"Al ZIP le falta {fehlt[0]}.")
        kopf = z.read(f"{WURZEL_NAME}/Programm/gans_lernkarten.py")[:20000].decode("utf-8", "replace")
        m = re.search(r'^VERSION = "([0-9.]+)[ "]', kopf, re.M)
        if not m or m.group(1) != version:
            nein(f"Das ZIP enthält Version {m.group(1) if m else '?'} statt {version}.",
                 f"The ZIP holds version {m.group(1) if m else '?'} instead of {version}.",
                 f"El ZIP trae la versión {m.group(1) if m else '?'} en lugar de {version}.")
    return infos


def entpacken(pfad, infos, ziel):
    """Nur die geprüften Einträge, jeweils unter ziel/<Me-Goos-ta-Deutsch>/…; Startdateien ausführbar."""
    shutil.rmtree(ziel, ignore_errors=True)
    with zipfile.ZipFile(pfad) as z:
        for i in infos:
            p = Path(ziel, *i.filename.split("/"))
            p.parent.mkdir(parents=True, exist_ok=True)
            with z.open(i) as q, open(p, "wb") as f:
                shutil.copyfileobj(q, f)
            if os.name != "nt":
                os.chmod(p, 0o755 if p.suffix in (".sh", ".command") or (i.external_attr >> 16) & 0o111 else 0o644)
    return Path(ziel) / WURZEL_NAME


def laden(version, quelle, daten, melde=print):
    """Release v<version> laden, prüfen, entpacken → Pfad des entpackten Ordners (update/neu/Me-Goos-ta-Deutsch).
    quelle: …/releases/download (GitHub) bzw. für Tests http://127.0.0.1:<port>/…"""
    if not version_ok(version):
        raise UpdateFehler("version")
    p = urllib.parse.urlsplit(quelle)
    erlaubt = GITHUB_HOSTS + (("127.0.0.1",) if p.hostname == "127.0.0.1" else ())
    d = ordner(daten)
    d.mkdir(parents=True, exist_ok=True)
    name = ZIP_MUSTER.format(v=version)
    basis = f"{quelle.rstrip('/')}/v{version}/"
    melde(_t(f"Frage GitHub nach Version {version} …", f"Asking GitHub for version {version} …",
             f"Consultando GitHub por la versión {version} …"))
    with _oeffne(basis + "SHA256SUMS.txt", erlaubt) as r:
        summen = r.read(MAX_SUMMEN + 1)
    if len(summen) > MAX_SUMMEN:
        raise UpdateFehler("SHA256SUMS")
    erwartet = next((z.split()[0].lower() for z in summen.decode("utf-8", "replace").splitlines()
                     if len(z.split()) == 2 and z.split()[1].lstrip("*") == name
                     and re.fullmatch(r"[0-9a-fA-F]{64}", z.split()[0])), None)
    if not erwartet:
        raise UpdateFehler(_t(f"In SHA256SUMS.txt steht keine Prüfsumme für {name}.", f"SHA256SUMS.txt has no checksum for {name}.",
                              f"SHA256SUMS.txt no tiene suma para {name}."))
    melde(_t(f"Lade {name} …", f"Downloading {name} …", f"Descargando {name} …"))
    zip_pfad = d / f"{name}.part"
    try:
        with _oeffne(basis + name, erlaubt, timeout=120) as r:
            sha = _lies(r, zip_pfad, MAX_ZIP, melde)
        if sha != erwartet:
            raise UpdateFehler(_t("Prüfsumme stimmt nicht – Datei beschädigt oder verändert. Nichts geändert.",
                                  "Checksum mismatch – file damaged or altered. Nothing changed.",
                                  "La suma de verificación no coincide: archivo dañado o alterado. No se cambió nada."))
        melde(_t("Prüfsumme in Ordnung. Prüfe den Inhalt …", "Checksum OK. Checking the contents …",
                 "Suma de verificación correcta. Revisando el contenido …"))
        infos = pruefe_zip(zip_pfad, version)
        (d / "bereit.json").unlink(missing_ok=True)           # erst jetzt: ein gescheiterter Versuch lässt die alte stehen
        neu = entpacken(zip_pfad, infos, d / "neu")
    finally:
        zip_pfad.unlink(missing_ok=True)
    (d / "bereit.json").write_text(json.dumps(dict(version=version, sha256=sha, zeit=time.time(), ordner=str(neu)),
                                              ensure_ascii=False), encoding="utf-8")
    melde(_t(f"Version {version} ist geladen und geprüft – bereit zum Übernehmen.",
             f"Version {version} is downloaded and checked – ready to install.",
             f"La versión {version} está descargada y revisada; lista para instalar."))
    return neu


def bereit(daten):
    """Geladene, noch nicht übernommene Version (dict aus bereit.json) oder None."""
    try:
        b = json.loads((ordner(daten) / "bereit.json").read_text(encoding="utf-8"))
        return b if version_ok(b.get("version")) and Path(b.get("ordner", "")).is_dir() else None
    except (OSError, ValueError, AttributeError):
        return None


# =============================================================================================
# 2. Anwenden (nach dem Ende der Oberfläche)
# =============================================================================================
def programm_ordner_ok(wurzel):
    """Nur einen Ordner ersetzen, der eindeutig das Programm ist – nie den Entwicklungsordner (Arbeitsordner mit
    bau_release.py daneben) oder ein Git-Verzeichnis."""
    w = Path(wurzel)
    return ((w / "Programm" / "starter.py").is_file() and (w / "Programm" / "gans_ui.py").is_file()
            and not (w.parent / "bau_release.py").exists() and not (w / ".git").exists())


def anwenden(quelle, ziel, sicherung):
    """Jede Datei aus quelle (entpacktes Release) ersetzt die in ziel; Altes vorher nach sicherung. Fehler → alles
    zurück, dann Ausnahme. Eigene Daten (NUTZER) werden nie angefasst. → Anzahl geänderter Dateien."""
    quelle, ziel, sicherung = Path(quelle), Path(ziel), Path(sicherung)
    if not programm_ordner_ok(ziel):
        raise UpdateFehler("ziel")
    shutil.rmtree(sicherung, ignore_errors=True)
    erledigt = []                                               # (Zielpfad, Sicherung oder None)
    try:
        for wurzel, _, namen in os.walk(quelle):
            for n in sorted(namen):
                q = Path(wurzel) / n
                rel = q.relative_to(quelle).as_posix()
                if NUTZER.match(rel):
                    continue
                z = ziel / rel
                if z.is_file():
                    if z.stat().st_size == q.stat().st_size and z.read_bytes() == q.read_bytes():
                        continue
                    s = sicherung / rel
                    s.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(z, s)
                else:
                    s = None
                z.parent.mkdir(parents=True, exist_ok=True)
                tmp = z.with_name(f"{z.name}.update.tmp")
                shutil.copyfile(q, tmp)
                if os.name != "nt":
                    os.chmod(tmp, 0o755 if z.suffix in (".sh", ".command") else os.stat(q).st_mode & 0o777)
                os.replace(tmp, z)
                erledigt.append((z, s))
    except Exception:
        for z, s in reversed(erledigt):
            try:
                if s is not None:
                    tmp = z.with_name(f"{z.name}.zurueck.tmp")
                    shutil.copy2(s, tmp)
                    os.replace(tmp, z)
                else:
                    z.unlink(missing_ok=True)
            except OSError:
                pass
        raise
    return len(erledigt)


def warte_auf_ende(pid, sekunden=60):
    """Wartet, bis der Prozess pid beendet ist (Windows ohne os.kill – das würde ihn beenden)."""
    if not pid:
        return True
    if os.name == "nt":
        import ctypes
        k = ctypes.windll.kernel32
        h = k.OpenProcess(0x00100000, False, int(pid))         # SYNCHRONIZE
        if not h:
            return True
        try:
            return k.WaitForSingleObject(h, int(sekunden * 1000)) == 0
        finally:
            k.CloseHandle(h)
    ende = time.time() + sekunden
    while time.time() < ende:
        if not _lebt(int(pid)):
            return True
        time.sleep(0.2)
    return False


def _lebt(pid):
    """Läuft der Prozess noch? Ein beendeter, aber nicht abgeholter Prozess (Zombie – z. B. in einem Container ohne
    Init-Prozess) zählt als beendet."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    try:
        with open(f"/proc/{pid}/stat", "rb") as f:                # Linux: Zustand nach dem Programmnamen in Klammern
            return f.read().rsplit(b")", 1)[-1].split()[0] != b"Z"
    except (OSError, IndexError):
        pass
    try:                                                        # macOS (kein /proc)
        r = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True, timeout=5)
        return r.returncode == 0 and not r.stdout.strip().startswith("Z")
    except (OSError, subprocess.SubprocessError):
        return True


def startdatei(wurzel):
    system = "win" if os.name == "nt" else "mac" if sys.platform == "darwin" else "linux"
    return Path(wurzel) / START[system]


def neu_starten(wurzel):
    """Startet das Programm über seine Startdatei – wie ein Doppelklick (Windows mit eigenem Fenster)."""
    datei = startdatei(wurzel)
    args = ["--kein-browser"] if os.environ.get("MGD_KEIN_BROWSER") == "1" else []     # nur automatische Tests (CI)
    kw = dict(cwd=str(wurzel), stdin=subprocess.DEVNULL, env=dict(os.environ, MGD_KEIN_TERMINAL="1"))
    if os.name == "nt":                                         # /s: äußere Anführungszeichen weg, Pfad bleibt geschützt
        subprocess.Popen(f'cmd.exe /d /s /c ""{datei}" {" ".join(args)}"', creationflags=0x00000010 | 0x00000200, **kw)
    else:
        kw.update(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        subprocess.Popen((["sh", str(datei)] if datei.suffix == ".sh" else [str(datei)]) + args, **kw)


def anwenden_und_starten(daten, wurzel, pid, starten=True):
    """Ablauf nach „Jetzt neu starten“: auf das Ende der Oberfläche warten, ersetzen, Ergebnis merken, neu starten."""
    d = ordner(daten)
    b = bereit(daten)
    erg = dict(zeit=time.time(), version=(b or {}).get("version", ""), ok=False, fehler="", dateien=0)
    try:
        if not b:
            raise UpdateFehler(_t("Es liegt keine geladene Version bereit.", "No downloaded version is waiting.",
                                  "No hay ninguna versión descargada esperando."))
        if not warte_auf_ende(pid):
            raise UpdateFehler(_t("Das Programm hat sich nicht rechtzeitig beendet – nichts geändert.",
                                  "The program didn’t close in time – nothing changed.",
                                  "El programa no se cerró a tiempo; no se cambió nada."))
        time.sleep(0.5)
        erg["dateien"] = anwenden(b["ordner"], wurzel, d / "alt")
        erg["ok"] = True
        shutil.rmtree(d / "neu", ignore_errors=True)
        shutil.rmtree(d / "alt", ignore_errors=True)
        (d / "bereit.json").unlink(missing_ok=True)
    except Exception as e:  # noqa: BLE001 – alles zurückgelegt; die alte Version startet wieder
        erg["fehler"] = str(e) or type(e).__name__
    d.mkdir(parents=True, exist_ok=True)
    (d / "ergebnis.json").write_text(json.dumps(erg, ensure_ascii=False), encoding="utf-8")
    if starten:
        neu_starten(wurzel)
    return erg


def main(argv=None):
    ap = argparse.ArgumentParser(description="Me Goos-ta Deutsch: neue Version laden bzw. übernehmen")
    ap.add_argument("--laden", metavar="VERSION")
    ap.add_argument("--quelle", default="")
    ap.add_argument("--anwenden", action="store_true")
    ap.add_argument("--daten", required=True)
    ap.add_argument("--wurzel", default=str(HIER.parent))
    ap.add_argument("--pid", type=int, default=0)
    ap.add_argument("--ohne-start", action="store_true")
    a = ap.parse_args(argv)
    if a.laden:
        try:
            laden(a.laden, a.quelle, a.daten, melde=lambda t: print(t, flush=True))
        except UpdateFehler as e:
            print(f"✕ {e}", flush=True)
            return 1
        return 0
    if a.anwenden:
        return 0 if anwenden_und_starten(a.daten, a.wurzel, a.pid, starten=not a.ohne_start)["ok"] else 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
