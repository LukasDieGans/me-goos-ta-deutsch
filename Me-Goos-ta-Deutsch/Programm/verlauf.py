#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ME GOOS-TA DEUTSCH – Rückgängig und Wiederholen                     Version 2.5 (23.10.2026)
=============================================================================================
Jede Anfrage, die eigene Daten ändert (Karten, Bilder, „Bilder vorbereiten“, Ideen, Gänse-Bild), wird ein Schritt:

* vorher: kleine Dateien (Kartenliste, ideen.json, Angaben der Entwürfe – Endung .csv/.json) werden als Bytes gemerkt,
  von allen anderen nur Größe und Änderungszeit. Bilder, die die Anfrage löschen, verschieben oder überschreiben will,
  sichert sie vorher mit sichere(pfad) (Kopie im Verlauf).
* nachher: jede geänderte Datei bekommt ihren Inhalt vorher und nachher (SHA-256, Kopie unter <ordner>/blobs).

Rückgängig schreibt den Stand vorher zurück, Wiederholen den Stand nachher – aber nur, wenn alle betroffenen Dateien
noch genau so sind, wie der Schritt sie hinterlassen hat; sonst ändert es nichts und leert den Verlauf (Konflikt).
Fehlt für eine geänderte Datei der Inhalt vorher (nicht gesichert), lässt sich hinter diesen Schritt nicht zurück –
der Verlauf wird geleert. Begrenzt auf MAX_SCHRITTE Schritte bzw. MAX_BYTES Kopien (die ältesten fallen weg); der
Verlauf gilt für die laufende Sitzung (beim Start leer). Nur Standardbibliothek, ohne eigene Threads (Web-App).
Gruppen: Schritte mit derselben Gruppe (z. B. „Alle übersetzen“, Tippen im selben Feld) werden zu einem zusammengefasst.
Selbsttest: test_erweiterungen.py (Abschnitt E47).
"""
from __future__ import annotations

import contextlib
import hashlib
import os
import secrets
import shutil
import threading
import time
from pathlib import Path

MAX_SCHRITTE = 30                       # so viele Schritte lassen sich zurücknehmen (Lukas: „nur eine begrenzte Anzahl“)
MAX_BYTES = 400 * 1024 * 1024           # Kopien im Verlauf zusammen; darüber fallen die ältesten Schritte weg
KLEIN = (".csv", ".json")               # wird vor jedem Schritt ganz gemerkt (ändert sich auch an Ort und Stelle)
KLEIN_MAX = 8 * 1024 * 1024
GRUPPE_SEKUNDEN = 600                   # Schritte derselben Gruppe verschmelzen nur, solange sie so nah beieinander liegen

_lokal = threading.local()


class Konflikt(Exception):
    """Die Daten sind inzwischen anders, als der Schritt sie hinterlassen hat – nichts geändert, Verlauf geleert."""


def sichere(pfad):
    """Vor dem Löschen, Verschieben oder Überschreiben einer Datei aufrufen: hebt ihren Inhalt für „Rückgängig“ auf.
    Außerhalb eines Schritts (Hintergrund, Lesen) oder für Dateien außerhalb der eigenen Daten wirkungslos."""
    s = getattr(_lokal, "schritt", None)
    if s is not None:
        s.sichere(pfad)


def _schluessel(pfad):
    return os.path.abspath(str(pfad))


def _sha_datei(pfad):
    h = hashlib.sha256()
    with open(pfad, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


class _Schritt:
    """Ein laufender Schritt: Stand vorher und gesicherte Dateien."""

    def __init__(self, verlauf, art, gruppe):
        self.verlauf, self.art, self.gruppe = verlauf, art, gruppe
        self.stat0 = verlauf._zustand()
        self.klein0 = {}
        for p, (groesse, _) in self.stat0.items():
            if p.lower().endswith(KLEIN) and groesse <= KLEIN_MAX:
                try:
                    with open(p, "rb") as f:
                        self.klein0[p] = f.read()
                except OSError:
                    pass
        self.gesichert = {}                                     # Pfad → Blob-SHA des Inhalts vorher

    def sichere(self, pfad):
        p = _schluessel(pfad)
        if p not in self.stat0 or p in self.klein0 or p in self.gesichert or not os.path.isfile(p):
            return
        try:
            self.gesichert[p] = self.verlauf._blob_aus_datei(p)
        except OSError:
            pass


class Verlauf:
    """Rückgängig/Wiederholen für die Dateien aus bereich() → (einzelne Dateien, Ordner mit allen Unterordnern)."""

    def __init__(self, ordner, bereich):
        self.ordner, self.bereich = Path(ordner), bereich
        self.lock = threading.RLock()
        self.zurueck_liste, self.vor_liste = [], []
        self.groessen = {}                                      # Blob-SHA → Bytes
        self.unvollstaendig = 0                                 # wie oft ein Schritt ohne Sicherung geleert hat
        self.leeren()

    # ---------- Speicher ----------
    def leeren(self):
        with self.lock:
            self.zurueck_liste, self.vor_liste, self.groessen = [], [], {}
            shutil.rmtree(self.ordner, ignore_errors=True)

    def _blobs(self):
        d = self.ordner / "blobs"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _blob_aus_bytes(self, inhalt):
        sha = hashlib.sha256(inhalt).hexdigest()
        ziel = self._blobs() / sha
        if not ziel.is_file():
            tmp = ziel.with_name(f"{sha}.{secrets.token_hex(3)}.tmp")
            tmp.write_bytes(inhalt)
            os.replace(tmp, ziel)
        self.groessen[sha] = len(inhalt)
        return sha

    def _blob_aus_datei(self, pfad):
        tmp = self._blobs() / f"neu.{secrets.token_hex(4)}.tmp"
        h, n = hashlib.sha256(), 0
        try:
            with open(pfad, "rb") as q, open(tmp, "wb") as z:
                for block in iter(lambda: q.read(1 << 20), b""):
                    h.update(block)
                    z.write(block)
                    n += len(block)
            sha = h.hexdigest()
            ziel = tmp.with_name(sha)
            if ziel.is_file():
                tmp.unlink()
            else:
                os.replace(tmp, ziel)
        except OSError:
            with contextlib.suppress(OSError):
                tmp.unlink()
            raise
        self.groessen[sha] = n
        return sha

    def _aufraeumen(self):
        """Blobs, die kein Schritt mehr braucht, löschen; danach die Grenzen einhalten (älteste Schritte zuerst)."""
        while True:
            benutzt = {sha for s in self.zurueck_liste + self.vor_liste for paar in s["dateien"].values() for sha in paar if sha}
            gesamt = sum(self.groessen.get(sha, 0) for sha in benutzt)
            if (len(self.zurueck_liste) > MAX_SCHRITTE or gesamt > MAX_BYTES) and self.zurueck_liste:
                self.zurueck_liste.pop(0)
                continue
            break
        for sha in list(self.groessen):
            if sha not in benutzt:
                self.groessen.pop(sha, None)
                with contextlib.suppress(OSError):
                    (self.ordner / "blobs" / sha).unlink()

    # ---------- Stand der eigenen Daten ----------
    def _zustand(self):
        dateien, ordner = self.bereich()
        aus = {}
        for p in dateien:
            p = _schluessel(p)
            try:
                st = os.stat(p)
            except OSError:
                continue
            aus[p] = (st.st_size, st.st_mtime_ns)
        for basis in ordner:
            basis = _schluessel(basis)
            if not os.path.isdir(basis):
                continue
            for wurzel, _, namen in os.walk(basis):
                for n in namen:
                    if n.endswith(".tmp"):
                        continue
                    p = os.path.join(wurzel, n)
                    try:
                        st = os.stat(p)
                    except OSError:
                        continue
                    aus[p] = (st.st_size, st.st_mtime_ns)
        return aus

    # ---------- Schritt ----------
    @contextlib.contextmanager
    def schritt(self, art, gruppe=""):
        """Rahmen um eine ändernde Anfrage. Auch wenn sie mit einem Fehler endet, zählt, was sie schon geändert hat."""
        with self.lock:
            s = _Schritt(self, art, str(gruppe or "")[:80])
            _lokal.schritt = s
            try:
                yield s
            finally:
                _lokal.schritt = None
                self._abschliessen(s)

    def _abschliessen(self, s):
        stat1 = self._zustand()
        geaendert = {p for p in set(s.stat0) | set(stat1) if s.stat0.get(p) != stat1.get(p)}
        for p, inhalt in s.klein0.items():                     # gleiche Zeit/Größe, anderer Inhalt (grobe Uhr)
            if p in stat1 and p not in geaendert:
                try:
                    with open(p, "rb") as f:
                        if f.read() != inhalt:
                            geaendert.add(p)
                except OSError:
                    geaendert.add(p)
        dateien, fehlt = {}, []
        for p in sorted(geaendert):
            if p not in s.stat0:
                vorher = None
            elif p in s.klein0:
                vorher = self._blob_aus_bytes(s.klein0[p])
            elif p in s.gesichert:
                vorher = s.gesichert[p]
            else:
                fehlt.append(p)
                continue
            try:
                nachher = self._blob_aus_datei(p) if p in stat1 else None
            except OSError:
                fehlt.append(p)
                continue
            if vorher != nachher:
                dateien[p] = (vorher, nachher)
        if fehlt:                                               # dahinter geht es nicht mehr sicher zurück
            self.unvollstaendig += 1
            self.leeren()
            return
        if not dateien:
            self._aufraeumen()
            return
        jetzt = time.time()
        oben = self.zurueck_liste[-1] if self.zurueck_liste else None
        if (s.gruppe and oben and oben["gruppe"] == s.gruppe and not self.vor_liste
                and jetzt - oben["zeit"] < GRUPPE_SEKUNDEN):
            for p, (v, n) in dateien.items():
                oben["dateien"][p] = (oben["dateien"][p][0], n) if p in oben["dateien"] else (v, n)
            oben["dateien"] = {p: vn for p, vn in oben["dateien"].items() if vn[0] != vn[1]}
            oben["zeit"] = jetzt
            if not oben["dateien"]:
                self.zurueck_liste.pop()
        else:
            self.zurueck_liste.append(dict(id=secrets.token_hex(4), art=s.art, gruppe=s.gruppe, zeit=jetzt,
                                           dateien=dateien))
        self.vor_liste = []
        self._aufraeumen()

    # ---------- Zurück und vor ----------
    def _sha_jetzt(self, p):
        try:
            return _sha_datei(p) if os.path.isfile(p) else None
        except OSError:
            return "?"

    def _setze(self, p, sha):
        if sha is None:
            if os.path.isfile(p):
                os.unlink(p)
            return
        os.makedirs(os.path.dirname(p), exist_ok=True)
        tmp = f"{p}.{secrets.token_hex(3)}.tmp"
        shutil.copyfile(self.ordner / "blobs" / sha, tmp)
        os.replace(tmp, p)

    def _anwenden(self, schritt, zurueck):
        ziel = {p: (vn[0] if zurueck else vn[1]) for p, vn in schritt["dateien"].items()}
        erwartet = {p: (vn[1] if zurueck else vn[0]) for p, vn in schritt["dateien"].items()}
        if any(self._sha_jetzt(p) != sha for p, sha in erwartet.items()):
            self.leeren()
            raise Konflikt()
        erledigt = []
        try:
            for p, sha in ziel.items():
                self._setze(p, sha)
                erledigt.append(p)
        except OSError:
            for p in erledigt:                                  # halb geschafft → alles wie vorher
                with contextlib.suppress(OSError):
                    self._setze(p, erwartet[p])
            self.leeren()
            raise

    def rueckgaengig(self):
        """Letzten Schritt zurücknehmen → seine Art (oder None, wenn es nichts gibt)."""
        with self.lock:
            if not self.zurueck_liste:
                return None
            s = self.zurueck_liste[-1]
            self._anwenden(s, zurueck=True)
            self.zurueck_liste.pop()
            self.vor_liste.append(s)
            return s["art"]

    def wiederholen(self):
        """Zuletzt zurückgenommenen Schritt wieder ausführen → seine Art (oder None)."""
        with self.lock:
            if not self.vor_liste:
                return None
            s = self.vor_liste[-1]
            self._anwenden(s, zurueck=False)
            self.vor_liste.pop()
            self.zurueck_liste.append(s)
            return s["art"]

    def info(self):
        """Für die Seite: Anzahl und Art des nächsten Schritts zurück bzw. vor."""
        return dict(z=len(self.zurueck_liste), w=len(self.vor_liste),
                    za=self.zurueck_liste[-1]["art"] if self.zurueck_liste else "",
                    wa=self.vor_liste[-1]["art"] if self.vor_liste else "")
