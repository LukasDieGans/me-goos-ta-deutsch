#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Me Goos-ta Deutsch – KI-Bilder: realistische Gänse für neue Karten, offline in reinem NumPy
===========================================================================================
Bildmodell: Segmind Vega (aus SDXL destilliert, 745 Mio. Parameter) + Beschleuniger Segmind VegaRT
(LCM-LoRA, 4–6 Schritte) – beide Apache-2.0; schneller Vorschau-Decoder TAESDXL (MIT).

Das Modell (ca. 3,6 GB) liegt im Datenordner unter modelle/ki-bild – nicht im Programmordner: Es überlebt
neue Programmversionen, kommt nie in Release oder Projekt-ZIP und wird von den Selbsttests nicht kopiert.
Jede Datei hat eine feste Revision und eine Prüfsumme (SHA-256 bzw. Git-SHA-1 bei kleinen Textdateien).
Ein abgebrochener Download setzt beim nächsten Mal an derselben Stelle fort.

Gerechnet wird in reinem NumPy (Text-Encoder CLIP-L + OpenCLIP-bigG, Bildnetz UNet, LCM-Verfahren, VAE-Decoder);
elementweise Rechnungen laufen stückweise in Threads, Matrixprodukte über BLAS auf allen Kernen. Auf einem
Laptop von 2023 (i5, 16 GB) dauert ein Bild 896 × 640 gut eine Minute.

Aufruf:  python3 ki_bild.py --laden      Modell herunterladen (mit Prüfsummen)
         python3 ki_bild.py --status     zeigt, was schon da ist
         python3 ki_bild.py --erzeugen "a goose on a meadow" [--negativ "people"] [--startwert 7] [--aus gans.png]
"""
from __future__ import annotations

import hashlib
import html
import json
import math
import os
import re
import shutil
import sys
import threading
from pathlib import Path

import numpy as np

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import ki_modelle as km  # noqa: E402  (Softmax, sicherer Download)
USER_AGENT = "Me-Goos-ta-Deutsch"
HF = "https://huggingface.co"

# ---------------------------------------------------------------------------------------------
# Katalog: offizielle Hugging-Face-Ablagen (ohne Konto ladbar), feste Revision, Größe, Prüfsumme
# ---------------------------------------------------------------------------------------------
_VEGA, _VEGA_REV = "segmind/Segmind-Vega", "7714c4363e5856ff974a4f4b068e8691f26d0b40"
_RT, _RT_REV = "segmind/Segmind-VegaRT", "3162e917016cef536fa040ceeeeadd9e09d93e7a"
_TAE, _TAE_REV = "madebyollin/taesdxl", "b20258aaef75ef61e659c1e0f14f251cf0ad153e"


def _d(name, repo, rev, pfad, groesse, sha256=None, git_sha1=None):
    return dict(name=name, repo=repo, rev=rev, pfad=pfad, bytes=groesse, sha256=sha256, git_sha1=git_sha1)


MODELL = dict(
    id="vega", titel="Segmind Vega + VegaRT", lizenz="Apache-2.0",
    quelle="https://huggingface.co/segmind/Segmind-Vega",
    dateien=[
        _d("unet.fp16.safetensors", _VEGA, _VEGA_REV, "unet/diffusion_pytorch_model.fp16.safetensors", 1490520736,
           sha256="8cfa375669b1222d6fecf470f41b2abb370c76a90ab9568964c4bb15b34ec8a2"),
        _d("text_encoder.fp16.safetensors", _VEGA, _VEGA_REV, "text_encoder/model.fp16.safetensors", 246144152,
           sha256="1e090d6a828fd92401be5f83e615fd7b4fb1f4a22e9af9040a38f602e839317c"),
        _d("text_encoder_2.fp16.safetensors", _VEGA, _VEGA_REV, "text_encoder_2/model.fp16.safetensors", 1389382176,
           sha256="5b98e4a57a9292eeb819d67e2d2100f66f17db723cde4ecea27a7c3741160d0c"),
        _d("vae.fp16.safetensors", _VEGA, _VEGA_REV, "vae/diffusion_pytorch_model.fp16.safetensors", 167335342,
           sha256="bcb60880a46b63dea58e9bc591abe15f8350bde47b405f9c38f4be70c6161e68"),
        _d("vegart_lora.safetensors", _RT, _RT_REV, "pytorch_lora_weights.safetensors", 239224692,
           sha256="9b6e8cd833fa205eaeeed391ca623a6f2546e447470bd1c5dcce3fa8d2f26afb"),
        _d("taesdxl_decoder.safetensors", _TAE, _TAE_REV, "taesdxl_decoder.safetensors", 4895612,
           sha256="f6013131e7eb412ef20113f1acc2ea7d3e47e53196ca0530fa65d9b61d814b61"),
        # kleine Textdateien (kein LFS) → Prüfung über die Git-Kennung (SHA-1 von „blob <Länge>\0<Inhalt>“)
        _d("tokenizer_vocab.json", _VEGA, _VEGA_REV, "tokenizer/vocab.json", 1059962,
           git_sha1="469be27c5c010538f845f518c4f5e8574c78f7c8"),
        _d("tokenizer_merges.txt", _VEGA, _VEGA_REV, "tokenizer/merges.txt", 524619,
           git_sha1="76e821f1b6f0a9709293c3b6b51ed90980b3166b"),
        _d("tokenizer_special_tokens_map.json", _VEGA, _VEGA_REV, "tokenizer/special_tokens_map.json", 588,
           git_sha1="cf0682d6de72c1547f41b4f6d7c59f62deffef94"),
        _d("tokenizer_2_special_tokens_map.json", _VEGA, _VEGA_REV, "tokenizer_2/special_tokens_map.json", 576,
           git_sha1="b3b93aa8e7fd8552501067e63e04e2958298c2b2"),
        _d("text_encoder_config.json", _VEGA, _VEGA_REV, "text_encoder/config.json", 604,
           git_sha1="2abbff533096f62f84a9ab5610e4ef02efe4eedd"),
        _d("text_encoder_2_config.json", _VEGA, _VEGA_REV, "text_encoder_2/config.json", 616,
           git_sha1="6595a69e7176d546ef8d8c941873ab8cb77a27d0"),
        _d("unet_config.json", _VEGA, _VEGA_REV, "unet/config.json", 1762,
           git_sha1="6dda1a8bc3057ebd9b60d0ba301446937e442df9"),
        _d("vae_config.json", _VEGA, _VEGA_REV, "vae/config.json", 642,
           git_sha1="0b8ef7138eabc3b49f155532d54d019931fd69bf"),
    ])
RAM_EMPFOHLEN_GB = 8


def _t(de, en, es):
    s = (os.environ.get("MGD_SPRACHE") or "en")[:2].lower()
    return {"en": en, "es": es}.get(s, de)


def _gb(b):
    return f"{b / 1e9:.1f}".replace(".", "," if (os.environ.get("MGD_SPRACHE") or "en")[:2] in ("de", "es") else ".")


# ---------------------------------------------------------------------------------------------
# Ort, Platz, Arbeitsspeicher
# ---------------------------------------------------------------------------------------------
def modell_ordner() -> Path:
    """MGD_KI_BILD (für Tests/Probe-Server), sonst <Datenordner>/modelle/ki-bild."""
    if os.environ.get("MGD_KI_BILD"):
        return Path(os.environ["MGD_KI_BILD"])
    sys.path.insert(0, str(HIER))
    import uebersetzer
    return uebersetzer.daten_ordner() / "modelle" / "ki-bild"


def platz_noetig(modell=None):
    return sum(d["bytes"] for d in (modell or MODELL)["dateien"])


def freier_platz(ordner):
    p = Path(ordner)
    while not p.exists() and p != p.parent:
        p = p.parent
    try:
        return shutil.disk_usage(p).free
    except OSError:
        return None


def arbeitsspeicher_gb():
    """Gesamter Arbeitsspeicher in GB (None, wenn unbekannt) – ohne Zusatzpakete."""
    try:
        if os.name == "nt":
            import ctypes

            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            m = MEMORYSTATUSEX()
            m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
                return m.ullTotalPhys / 1024 ** 3
            return None
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1024 ** 3
    except (OSError, ValueError, AttributeError):
        return None


# ---------------------------------------------------------------------------------------------
# Prüfen und Status (schnell: nur Größe + Merkzettel „.ok“ – die Prüfsumme wird beim Laden gerechnet)
# ---------------------------------------------------------------------------------------------
def _pruefsumme(pfad, d):
    if d.get("sha256"):
        h = hashlib.sha256()
        with open(pfad, "rb") as f:
            for block in iter(lambda: f.read(4 << 20), b""):
                h.update(block)
        return h.hexdigest() == d["sha256"]
    h = hashlib.sha1(b"blob %d\0" % Path(pfad).stat().st_size)
    with open(pfad, "rb") as f:
        for block in iter(lambda: f.read(4 << 20), b""):
            h.update(block)
    return h.hexdigest() == d["git_sha1"]


def _ok_datei(ziel):
    return ziel.with_name(ziel.name + ".ok")


def datei_ok(ordner, d):
    ziel = Path(ordner) / d["name"]
    try:
        return ziel.stat().st_size == d["bytes"] and json.loads(_ok_datei(ziel).read_text("utf-8")).get("bytes") == d["bytes"]
    except (OSError, ValueError):
        return False


def status(ordner=None, modell=None):
    modell = modell or MODELL
    ordner = Path(ordner or modell_ordner())
    fehlt, da = [], 0
    for d in modell["dateien"]:
        if datei_ok(ordner, d):
            da += d["bytes"]
        else:
            fehlt.append(d["name"])
            teil = ordner / (d["name"] + ".part")
            if teil.is_file():
                da += min(teil.stat().st_size, d["bytes"])
    return dict(installiert=not fehlt, fehlt=fehlt, bytes_da=da, bytes_gesamt=platz_noetig(modell), ordner=str(ordner),
                titel=modell["titel"], lizenz=modell["lizenz"], ram_gb=arbeitsspeicher_gb())


# ---------------------------------------------------------------------------------------------
# Herunterladen: fortsetzbar (HTTP-Range), Prüfsumme, erst danach an den endgültigen Namen
# ---------------------------------------------------------------------------------------------
def _url(d, basis=None):
    return f"{basis or HF}/{d['repo']}/resolve/{d['rev']}/{d['pfad']}"


def _unterbrochen(grund=""):
    zusatz = f" ({grund})" if grund else ""
    return _t("Download unterbrochen oder Quelle gerade nicht erreichbar" + zusatz + " – einfach später noch einmal auf "
              "„Laden“ klicken: Es geht an derselben Stelle weiter, Fertiges bleibt erhalten.",
              "Download interrupted or source not reachable right now" + zusatz + " – just click “Download” again later: "
              "it continues where it stopped, finished files stay.",
              "La descarga se interrumpió o la fuente no responde ahora" + zusatz + "; vuelve a hacer clic en "
              "«Descargar» más tarde: seguirá donde se quedó y lo terminado se conserva.")


def _lade_datei(d, ordner, melde, basis=None):
    import urllib.request
    sys.path.insert(0, str(HIER))
    import ki_modelle
    ziel = ordner / d["name"]
    teil = ziel.with_name(ziel.name + ".part")
    schon = teil.stat().st_size if teil.is_file() else 0
    if schon >= d["bytes"]:
        teil.unlink()
        schon = 0
    kopf = {"User-Agent": USER_AGENT}
    if schon:
        kopf["Range"] = f"bytes={schon}-"
    mb = d["bytes"] / (1024 * 1024)
    melde(_t(f"Lade {d['name']} ({mb:.0f} MB) …", f"Downloading {d['name']} ({mb:.0f} MB) …",
             f"Descargando {d['name']} ({mb:.0f} MB) …") if not schon else
          _t(f"Setze {d['name']} fort ab {schon / (1024 * 1024):.0f} von {mb:.0f} MB …",
             f"Resuming {d['name']} from {schon / (1024 * 1024):.0f} of {mb:.0f} MB …",
             f"Continuando {d['name']} desde {schon / (1024 * 1024):.0f} de {mb:.0f} MB …"))
    with ki_modelle.oeffne_url(urllib.request.Request(_url(d, basis), headers=kopf), timeout=60) as r:
        if schon and getattr(r, "status", 200) != 206:          # Server kann nicht fortsetzen → von vorn
            schon = 0
        geladen, schritt = schon, schon * 20 // d["bytes"]
        with open(teil, "ab" if schon else "wb") as f:
            while True:
                block = r.read(1 << 20)
                if not block:
                    break
                geladen += len(block)
                if geladen > d["bytes"]:
                    raise ValueError(_t("Datei größer als erwartet – nichts installiert.",
                                        "File larger than expected – nothing installed.",
                                        "Archivo más grande de lo esperado: no se instaló nada."))
                f.write(block)
                if d["bytes"] > 8 << 20 and geladen * 20 // d["bytes"] > schritt:
                    schritt = geladen * 20 // d["bytes"]
                    melde(f"  {schritt * 5} %  ({geladen // (1024 * 1024)} / {d['bytes'] // (1024 * 1024)} MB)")
    if teil.stat().st_size < d["bytes"]:
        raise ConnectionError(_unterbrochen())
    if not _pruefsumme(teil, d):
        teil.unlink(missing_ok=True)
        raise ValueError(_t(f"Prüfsumme von {d['name']} stimmt nicht – Datei beschädigt oder verändert. Nichts installiert.",
                            f"Checksum of {d['name']} doesn’t match – file damaged or altered. Nothing installed.",
                            f"La suma de verificación de {d['name']} no coincide: archivo dañado o alterado. "
                            "No se instaló nada."))
    os.replace(teil, ziel)
    _ok_datei(ziel).write_text(json.dumps(dict(bytes=d["bytes"], sha256=d.get("sha256"), git_sha1=d.get("git_sha1"))),
                               encoding="utf-8")


def lade(melde=print, ordner=None, modell=None, basis=None):
    """Lädt alle fehlenden Dateien des Modells. Gibt den Status zurück."""
    modell = modell or MODELL
    ordner = Path(ordner or modell_ordner())
    ordner.mkdir(parents=True, exist_ok=True)
    st = status(ordner, modell)
    if st["installiert"]:
        melde(_t("Das Bildmodell ist schon vollständig da – alles bereit.", "The image model is already complete – all set.",
                 "El modelo de imágenes ya está completo: todo listo."))
        return st
    noch = st["bytes_gesamt"] - st["bytes_da"]
    frei = freier_platz(ordner)
    if frei is not None and frei < noch + 200 * 1024 * 1024:
        raise OSError(_t(f"Zu wenig Speicherplatz: {_gb(frei)} GB frei, {_gb(noch)} GB nötig – räum ein bisschen Platz "
                         f"frei, dann klappt es.",
                         f"Not enough disk space: {_gb(frei)} GB free, {_gb(noch)} GB needed – free up a little space "
                         f"and it will work.",
                         f"No hay suficiente espacio: {_gb(frei)} GB libres, {_gb(noch)} GB necesarios; libera un poco "
                         f"de espacio y funcionará."))
    melde(_t(f"{modell['titel']} (Lizenz {modell['lizenz']}) – noch {_gb(noch)} GB, Ziel: {ordner}",
             f"{modell['titel']} ({modell['lizenz']} license) – {_gb(noch)} GB to go, target: {ordner}",
             f"{modell['titel']} (licencia {modell['lizenz']}): faltan {_gb(noch)} GB, destino: {ordner}"))
    import http.client
    for d in modell["dateien"]:
        if datei_ok(ordner, d):
            continue
        try:
            _lade_datei(d, ordner, melde, basis)
        except (ValueError, ConnectionError):
            raise
        except (OSError, http.client.HTTPException) as e:          # Zeitüberschreitung, 404, abgebrochene Leitung …
            raise ConnectionError(_unterbrochen(str(e)[:120])) from e
    st = status(ordner, modell)
    melde(_t(f"Fertig – das Bildmodell ist bereit ({_gb(st['bytes_gesamt'])} GB). Ab jetzt geht alles offline.",
             f"Done – the image model is ready ({_gb(st['bytes_gesamt'])} GB). From now on everything works offline.",
             f"Listo: el modelo de imágenes está preparado ({_gb(st['bytes_gesamt'])} GB). Desde ahora todo funciona "
             f"sin conexión."))
    return st


# ---------------------------------------------------------------------------------------------
# safetensors lesen und schreiben – ohne Zusatzpaket; Gewichte werden nur eingeblendet (np.memmap)
# und erst beim Abruf in float32 umgerechnet (Speicher bleibt klein)
# ---------------------------------------------------------------------------------------------
_ST_TYPEN = {"F16": np.float16, "F32": np.float32, "F64": np.float64, "BF16": np.uint16, "I64": np.int64,
             "I32": np.int32, "I16": np.int16, "I8": np.int8, "U8": np.uint8, "BOOL": np.bool_}


class SafeTensors:
    """Datei = 8 Byte Kopflänge (little endian) + JSON-Kopf {name: {dtype, shape, data_offsets}} + Rohdaten."""

    def __init__(self, pfad):
        self.pfad = Path(pfad)
        groesse = self.pfad.stat().st_size
        with open(self.pfad, "rb") as f:
            n = int.from_bytes(f.read(8), "little")
            if not 2 <= n <= min(100 << 20, groesse - 8):
                raise ValueError(f"{self.pfad.name}: kein gültiger safetensors-Kopf")
            kopf = json.loads(f.read(n).decode("utf-8"))
        self.meta = kopf.pop("__metadata__", None) or {}
        self.start = 8 + n
        self._kopf = {}
        for name, e in kopf.items():
            typ = _ST_TYPEN.get(e.get("dtype"))
            if typ is None:
                raise ValueError(f"{self.pfad.name}: Datentyp {e.get('dtype')} wird nicht unterstützt")
            a, b = (int(v) for v in e["data_offsets"])
            form = tuple(int(s) for s in e["shape"])
            if not 0 <= a <= b <= groesse - self.start or b - a != int(np.prod(form, dtype=np.int64)) * np.dtype(typ).itemsize:
                raise ValueError(f"{self.pfad.name}: Tensor {name} passt nicht in die Datei")
            self._kopf[name] = (e["dtype"], typ, form, a, b)
        self._mm = np.memmap(self.pfad, dtype=np.uint8, mode="r") if groesse > self.start else np.zeros(0, np.uint8)

    def keys(self):
        return self._kopf.keys()

    def __contains__(self, name):
        return name in self._kopf

    def form(self, name):
        return self._kopf[name][2]

    def roh(self, name):
        """Tensor im gespeicherten Datentyp, nur eingeblendet (keine Kopie)."""
        _, typ, form, a, b = self._kopf[name]
        return self._mm[self.start + a:self.start + b].view(typ).reshape(form)

    def f32(self, name):
        dt = self._kopf[name][0]
        x = self.roh(name)
        um = (lambda t: (t.astype(np.uint32) << 16).view(np.float32)) if dt == "BF16" else (lambda t: t.astype(np.float32))
        if x.ndim == 0 or x.size < 1 << 20:
            return um(x)
        aus = np.empty(x.shape, np.float32)                       # große Tensoren stückweise parallel umrechnen
        parallel(lambda ab: aus.__setitem__(slice(*ab), um(x[ab[0]:ab[1]])), _stuecke(len(x), x.size // len(x), 1 << 18))
        return aus

    def schliesse(self):
        """Datei freigeben (Windows sperrt eingeblendete Dateien, bis sie geschlossen sind)."""
        mm, self._mm = self._mm, None
        if isinstance(mm, np.memmap) and getattr(mm, "_mmap", None) is not None:
            try:
                mm._mmap.close()
            except BufferError:                                 # noch Ansichten in Gebrauch → zu, sobald sie weg sind
                pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.schliesse()


def speichere_safetensors(pfad, tensoren, meta=None):
    """{name: np.ndarray} → .safetensors (für Prüfungen und kleine Hilfsdateien)."""
    namen = {np.dtype(np.float16): "F16", np.dtype(np.float32): "F32", np.dtype(np.int64): "I64", np.dtype(np.uint8): "U8"}
    kopf, teile, pos = {}, [], 0
    for name, x in tensoren.items():
        x = np.asarray(x, order="C")                             # (ascontiguousarray machte aus Skalaren Form (1,))
        roh = x.tobytes()
        kopf[name] = {"dtype": namen[x.dtype], "shape": list(x.shape), "data_offsets": [pos, pos + len(roh)]}
        teile.append(roh)
        pos += len(roh)
    if meta:
        kopf["__metadata__"] = {str(k): str(v) for k, v in meta.items()}
    j = json.dumps(kopf).encode("utf-8")
    j += b" " * (-len(j) % 8)                                   # Daten auf 8 Byte ausrichten wie das Original
    with open(pfad, "wb") as f:
        f.write(len(j).to_bytes(8, "little"))
        f.write(j)
        for roh in teile:
            f.write(roh)


# ---------------------------------------------------------------------------------------------
# CLIP-Tokenizer: Byte-Pair-Encoding wie OpenAI CLIP / Hugging Face – reines Python
# ---------------------------------------------------------------------------------------------
def _bytes_zu_unicode():
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1))
    cs, n = bs[:], 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return {b: chr(c) for b, c in zip(bs, cs)}


class ClipTokenizer:
    START, ENDE = "<|startoftext|>", "<|endoftext|>"
    # wie CLIP: Kurzformen, Buchstabenfolgen, einzelne Ziffern, sonstige Zeichenfolgen (\p{L} ≈ [^\W\d_] in Python)
    MUSTER = re.compile(r"'s|'t|'re|'ve|'m|'ll|'d|[^\W\d_]+|\d|(?:[^\s\w]|_)+", re.IGNORECASE)

    def __init__(self, vocab_pfad, merges_pfad, pad=None, laenge=77):
        self.vocab = json.loads(Path(vocab_pfad).read_text(encoding="utf-8"))
        zeilen = Path(merges_pfad).read_text(encoding="utf-8").split("\n")
        if zeilen and zeilen[0].startswith("#version"):
            zeilen = zeilen[1:]
        paare = [tuple(z.split()) for z in zeilen if z.strip()]
        self.rang = {p: i for i, p in enumerate(paare) if len(p) == 2}
        self.byte_zeichen = _bytes_zu_unicode()
        self.start_id, self.ende_id = self.vocab[self.START], self.vocab[self.ENDE]
        self.pad_id = self.vocab.get(pad, self.ende_id) if pad else self.ende_id
        self.laenge = laenge
        self._cache = {}

    def _bpe(self, wort):
        if wort in self._cache:
            return self._cache[wort]
        teile = list(wort[:-1]) + [wort[-1] + "</w>"]
        while len(teile) > 1:
            kandidaten = [(self.rang[(teile[i], teile[i + 1])], i) for i in range(len(teile) - 1)
                          if (teile[i], teile[i + 1]) in self.rang]
            if not kandidaten:
                break
            _, i0 = min(kandidaten)
            a, b = teile[i0], teile[i0 + 1]
            neu, i = [], 0
            while i < len(teile):                                # alle Vorkommen des besten Paars verschmelzen
                if i < len(teile) - 1 and teile[i] == a and teile[i + 1] == b:
                    neu.append(a + b)
                    i += 2
                else:
                    neu.append(teile[i])
                    i += 1
            teile = neu
        self._cache[wort] = teile
        return teile

    def text_ids(self, text):
        """Nur die Token des Textes (ohne Start, Ende, Auffüllung, ungekürzt)."""
        text = html.unescape(html.unescape(str(text or ""))).replace("<|", " ").replace("|>", " ")
        text = " ".join(text.split()).lower()
        ids = []
        for stueck in self.MUSTER.findall(text):
            wort = "".join(self.byte_zeichen[b] for b in stueck.encode("utf-8"))
            ids.extend(self.vocab[t] for t in self._bpe(wort) if t in self.vocab)
        return ids

    def ids(self, text):
        """Text → genau `laenge` Token-IDs: Start, Text (gekürzt), Ende, Auffüllung."""
        ids = [self.start_id] + self.text_ids(text)[: self.laenge - 2] + [self.ende_id]
        return ids + [self.pad_id] * (self.laenge - len(ids))


# ---------------------------------------------------------------------------------------------
# CLIP-Text-Encoder (Transformer mit kausaler Maske) – CLIP ViT-L/14 und OpenCLIP ViT-bigG/14
# ---------------------------------------------------------------------------------------------
def linear(x, w, b=None):
    """PyTorch-Linear: y = x·Wᵀ + b."""
    y = x @ w.T
    return y + b if b is not None else y


def quick_gelu(x):
    return x * (np.float32(0.5) * (np.float32(1) + np.tanh(np.float32(0.851) * x)))    # x·sigmoid(1.702·x)


class ClipText:
    """Liefert für B × 77 Token die Ausgabe der vorletzten Schicht (für SDXL) und die letzte nach final_layer_norm.
    Mehrere Sätze (z. B. Prompt + Negativ-Prompt) laufen gemeinsam: jedes Gewicht wird nur einmal umgerechnet."""

    def __init__(self, st, cfg, praefix="text_model."):
        self.st, self.p = st, praefix
        self.d, self.schichten = cfg["hidden_size"], cfg["num_hidden_layers"]
        self.koepfe, self.eps = cfg["num_attention_heads"], cfg.get("layer_norm_eps", 1e-5)
        self.akt = quick_gelu if cfg.get("hidden_act") == "quick_gelu" else gelu

    def w(self, name):
        return self.st.f32(self.p + name)

    def _aufmerksamkeit(self, h, p, maske):
        b, n, d = h.shape
        k, dk = self.koepfe, d // self.koepfe
        q = linear(h, self.w(p + "q_proj.weight"), self.w(p + "q_proj.bias")) * np.float32(dk ** -0.5)
        kk = linear(h, self.w(p + "k_proj.weight"), self.w(p + "k_proj.bias"))
        v = linear(h, self.w(p + "v_proj.weight"), self.w(p + "v_proj.bias"))
        q, kk, v = (t.reshape(b, n, k, dk).transpose(0, 2, 1, 3) for t in (q, kk, v))
        s = km.softmax(q @ kk.transpose(0, 1, 3, 2) + maske)
        o = (s @ v).transpose(0, 2, 1, 3).reshape(b, n, d)
        return linear(o, self.w(p + "out_proj.weight"), self.w(p + "out_proj.bias"))

    def _schicht(self, x, i, maske):
        p = f"encoder.layers.{i}."
        h = layer_norm(x, self.w(p + "layer_norm1.weight"), self.w(p + "layer_norm1.bias"), self.eps)
        x = x + self._aufmerksamkeit(h, p + "self_attn.", maske)
        h = layer_norm(x, self.w(p + "layer_norm2.weight"), self.w(p + "layer_norm2.bias"), self.eps)
        h = self.akt(linear(h, self.w(p + "mlp.fc1.weight"), self.w(p + "mlp.fc1.bias")))
        return x + linear(h, self.w(p + "mlp.fc2.weight"), self.w(p + "mlp.fc2.bias"))

    def __call__(self, ids):
        ids = np.asarray(ids, np.int64)
        if ids.ndim == 1:
            ids = ids[None]
        b, n = ids.shape
        x = self.st.roh(self.p + "embeddings.token_embedding.weight")[ids.ravel()].astype(np.float32).reshape(b, n, self.d)
        x = x + self.w("embeddings.position_embedding.weight")[:n]           # oben: nur die nötigen Zeilen umgerechnet
        maske = np.triu(np.full((n, n), -np.inf, np.float32), 1)                        # nur nach links schauen
        vorletzte = x
        for i in range(self.schichten):
            if i == self.schichten - 1:
                vorletzte = x
            x = self._schicht(x, i, maske)
        letzte = layer_norm(x, self.w("final_layer_norm.weight"), self.w("final_layer_norm.bias"), self.eps)
        return vorletzte, letzte

    def gepoolt(self, letzte, ids, projektion="text_projection.weight"):
        """Satz-Einbettung (OpenCLIP mit Projektion): Ausgabe am Ende-Token (= größte ID, erstes Vorkommen)."""
        ids = np.asarray(ids)
        ids = ids[None] if ids.ndim == 1 else ids
        ende = letzte[np.arange(len(ids)), np.argmax(ids, axis=1)]
        return linear(ende, self.st.f32(projektion))


def _pad_token(pfad):
    p = json.loads(Path(pfad).read_text(encoding="utf-8")).get("pad_token")
    return p.get("content") if isinstance(p, dict) else p


class TextTeil:
    """Beide Text-Encoder wie bei SDXL: vorletzte Schichten nebeneinander (77 × 2048) + Satz-Einbettung (1280)."""

    def __init__(self, ordner):
        o = Path(ordner)
        vocab, merges = o / "tokenizer_vocab.json", o / "tokenizer_merges.txt"
        self.tok1 = ClipTokenizer(vocab, merges, _pad_token(o / "tokenizer_special_tokens_map.json"))
        self.tok2 = ClipTokenizer(vocab, merges, _pad_token(o / "tokenizer_2_special_tokens_map.json"))
        cfg = lambda n: json.loads((o / n).read_text(encoding="utf-8"))  # noqa: E731
        self.te1 = ClipText(SafeTensors(o / "text_encoder.fp16.safetensors"), cfg("text_encoder_config.json"))
        self.te2 = ClipText(SafeTensors(o / "text_encoder_2.fp16.safetensors"), cfg("text_encoder_2_config.json"))

    def __call__(self, texte):
        """Liste von Texten → (B × 77 × 2048, B × 1280)."""
        i1 = [self.tok1.ids(t) for t in texte]
        i2 = [self.tok2.ids(t) for t in texte]
        h1, _ = self.te1(i1)
        h2, l2 = self.te2(i2)
        return np.concatenate([h1, h2], axis=-1), self.te2.gepoolt(l2, i2)

    def schliesse(self):
        self.te1.st.schliesse()
        self.te2.st.schliesse()


# ---------------------------------------------------------------------------------------------
# Grundbausteine des Bildteils – Aktivierungen als B × H × W × C (float32)
# ---------------------------------------------------------------------------------------------
class Abgebrochen(Exception):
    """Das Erzeugen wurde auf Wunsch abgebrochen."""


# Matrixprodukte rechnet NumPy (BLAS) schon auf allen Kernen, elementweise Rechnungen aber nur auf einem. Darum laufen
# diese hier stückweise in Threads: NumPy gibt bei Rechnungen auf Feldern die GIL frei, und kleine Stücke bleiben im
# Cache. Ergebnis ist Wert für Wert dasselbe wie in einem Stück.
FADEN = max(1, min(8, os.cpu_count() or 1))
_pool_obj = None


def parallel(f, aufgaben):
    """f(a) für jede Aufgabe – in Threads, Fehler werden weitergereicht. Liefert die Ergebnisse in Reihenfolge.
    Innerhalb eines Threads läuft alles nacheinander (verschachtelt würde der Pool auf sich selbst warten)."""
    aufgaben = list(aufgaben)
    if FADEN == 1 or len(aufgaben) < 2 or threading.current_thread().name.startswith("ki-bild"):
        return [f(a) for a in aufgaben]
    global _pool_obj
    if _pool_obj is None:
        from concurrent.futures import ThreadPoolExecutor
        _pool_obj = ThreadPoolExecutor(FADEN, thread_name_prefix="ki-bild")
    return list(_pool_obj.map(f, aufgaben))


def _stuecke(zeilen, breite, ziel=1 << 16):
    """Zeilenbereiche mit je etwa `ziel` Werten (passt in den Cache), höchstens 64 Stück."""
    k = int(max(1, min(64, zeilen, zeilen * breite // ziel)))
    g = np.linspace(0, zeilen, k + 1).astype(np.int64)
    return [(int(a), int(e)) for a, e in zip(g[:-1], g[1:]) if e > a]


def _elementweise(f, x, *weitere):
    """aus = f(x, *weitere, aus) stückweise über die Zeilen (letzte Achse bleibt beisammen)."""
    x2 = x.reshape(-1, x.shape[-1])
    w2 = [w.reshape(-1, w.shape[-1]) for w in weitere]
    aus = np.empty(x2.shape, np.float32)
    parallel(lambda ab: f(x2[ab[0]:ab[1]], *(w[ab[0]:ab[1]] for w in w2), aus[ab[0]:ab[1]]),
             _stuecke(*x2.shape))
    return aus.reshape(x.shape)


def _silu_teil(t, o):
    np.multiply(t, np.float32(0.5), out=o)                       # x·sigmoid(x) = x·(½ + ½·tanh(x/2)), ohne Überlauf
    np.tanh(o, out=o)
    o *= np.float32(0.5)
    o += np.float32(0.5)
    o *= t


def silu(x):
    return _elementweise(_silu_teil, x)


_ERF = [np.float32(v) for v in (0.3275911, 1.061405429, -1.453152027, 1.421413741, -0.284496736, 0.254829592)]


def _gelu_teil(t, o, faktor=None):
    """o = GELU(t) (· faktor) mit erf nach Abramowitz & Stegun 7.1.26 (Fehler < 1,5e-7) – wie km.gelu, aber in place."""
    p, a1, a2, a3, a4, a5 = _ERF
    z = np.abs(t)
    z *= np.float32(1 / math.sqrt(2))
    u = z * p
    u += np.float32(1)
    np.reciprocal(u, out=u)
    np.multiply(u, a1, out=o)
    for a in (a2, a3, a4, a5):                                   # Polynom in u (Horner)
        o += a
        o *= u
    np.multiply(z, z, out=z)
    np.negative(z, out=z)
    np.exp(z, out=z)
    o *= z                                                       # erf(|x|/√2) = 1 − o
    np.subtract(np.float32(1), o, out=o)
    np.copysign(o, t, out=o)
    o += np.float32(1)
    o *= t
    o *= np.float32(0.5)
    if faktor is not None:
        o *= faktor


def gelu(x):
    return _elementweise(_gelu_teil, x)


def geglu(h):
    """GEGLU (diffusers): erste Hälfte · GELU(zweite Hälfte)."""
    i = h.shape[-1] // 2
    h2 = h.reshape(-1, 2 * i)
    return _elementweise(lambda g, a, o: _gelu_teil(g, o, a), h2[:, i:], h2[:, :i]).reshape(*h.shape[:-1], i)


def layer_norm(x, g, b, eps=1e-5):
    def teil(t, o):
        np.subtract(t, t.mean(-1, keepdims=True), out=o)
        v = np.square(o).mean(-1, keepdims=True)
        o *= np.float32(1) / np.sqrt(v + np.float32(eps))
        o *= g
        o += b
    return _elementweise(teil, x)


def group_norm(x, g, b, gruppen=32, eps=1e-5, mit_silu=False):
    """GroupNorm wie PyTorch (Mittelwert/Varianz je Bild und Kanalgruppe über alle Bildpunkte), auf Wunsch gleich mit
    SiLU. Zwei Durchgänge (Mittelwert, dann Abweichungen) in float64 – genau auch bei großem Mittelwert."""
    bn, c = x.shape[0], x.shape[-1]
    x3 = x.reshape(bn, -1, c)
    teile = [(i, a, e) for i in range(bn) for a, e in _stuecke(x3.shape[1], c, 1 << 17)]
    pro_bild = lambda werte: np.array([sum(w for (i, _, _), w in zip(teile, werte) if i == j)  # noqa: E731
                                       for j in range(bn)])
    n = x3.shape[1] * (c // gruppen)
    m = pro_bild(parallel(lambda s: x3[s[0], s[1]:s[2]].reshape(-1, gruppen, c // gruppen).sum((0, 2), np.float64),
                          teile)) / n
    mk = np.repeat(m, c // gruppen, axis=1).astype(np.float32)          # Mittelwert je Kanal
    v = pro_bild(parallel(lambda s: np.square(x3[s[0], s[1]:s[2]] - mk[s[0]]).reshape(-1, gruppen, c // gruppen)
                          .sum((0, 2), np.float64), teile)) / n
    a = (np.repeat(1 / np.sqrt(v + eps), c // gruppen, axis=1) * g).astype(np.float32)   # y = x·a + d
    d = (b - mk * a).astype(np.float32)
    aus = np.empty(x3.shape, np.float32)

    def anwenden(s):
        i, a0, e0 = s
        o = aus[i, a0:e0]
        np.multiply(x3[i, a0:e0], a[i], out=o)
        o += d[i]
        if mit_silu:
            t = o.copy()
            _silu_teil(t, o)
    parallel(anwenden, teile)
    return aus.reshape(x.shape)


_SPALTEN_BYTES = 128 * 1024 * 1024


def falte(x, wm, b=None, schritt=1):
    """k×k-Faltung mit Rand k//2 (wie PyTorch, auch Schrittweite 2) über B × H × W × C. wm = (k·k·C) × O in
    im2col-Reihenfolge (ky, kx, c); 1×1-Faltung = Matrixprodukt. Gerechnet in Zeilenstreifen (Speicher bleibt klein),
    die Spalten-Kopien laufen parallel."""
    bn, h, w, c = x.shape
    k = int(round((wm.shape[0] // c) ** 0.5))
    if k == 1:
        xs = x[:, ::schritt, ::schritt]
        y = xs.reshape(-1, c) @ wm
        if b is not None:
            y += b
        return y.reshape(*xs.shape[:3], -1)
    p = k // 2
    ho, wo = (h + 2 * p - k) // schritt + 1, (w + 2 * p - k) // schritt + 1
    xp = np.zeros((bn, h + 2 * p, w + 2 * p, c), np.float32)
    parallel(lambda s: xp.__setitem__((s[0], slice(p + s[1], p + s[2]), slice(p, p + w)), x[s[0], s[1]:s[2]]),
             [(i, a, e) for i in range(bn) for a, e in _stuecke(h, w * c, 1 << 18)])
    aus = np.empty((bn, ho, wo, wm.shape[1]), np.float32)
    zeilen = max(1, _SPALTEN_BYTES // (wo * k * k * c * 4))
    for i in range(bn):
        for r0 in range(0, ho, zeilen):
            r1 = min(ho, r0 + zeilen)
            sp = np.empty((r1 - r0, wo, k * k, c), np.float32)

            def kopie(j, i=i, r0=r0, r1=r1, sp=sp):
                ky, kx = divmod(j, k)
                sp[:, :, j] = xp[i, r0 * schritt + ky:(r1 - 1) * schritt + ky + 1:schritt,
                                 kx:(wo - 1) * schritt + kx + 1:schritt]
            parallel(kopie, range(k * k))
            y = sp.reshape(-1, k * k * c) @ wm
            if b is not None:
                y += b
            aus[i, r0:r1] = y.reshape(r1 - r0, wo, -1)
    return aus


def _softmax_zeilen(z):
    """Softmax ohne die Division (die kommt nach dem Produkt mit V, das ist kleiner): z ← exp(z − max), Rückgabe Σ."""
    summe = np.empty((z.shape[0], 1), np.float32)

    def teil(ab):
        t = z[ab[0]:ab[1]]
        t -= t.max(-1, keepdims=True)
        np.exp(t, out=t)
        summe[ab[0]:ab[1]] = t.sum(-1, keepdims=True)
    parallel(teil, _stuecke(*z.shape))
    return summe


def aufmerksamkeit(q, k, v, koepfe):
    """Skalarprodukt-Aufmerksamkeit: q B × N × C, k/v B × M × C → B × N × C (Kopf für Kopf, spart Speicher)."""
    b, n, c = q.shape
    dk = c // koepfe
    aus = np.empty((b, n, c), np.float32)
    skala = np.float32(dk ** -0.5)
    for i in range(b):
        for kopf in range(koepfe):
            s = slice(kopf * dk, (kopf + 1) * dk)
            z = (q[i, :, s] * skala) @ k[i, :, s].T
            summe = _softmax_zeilen(z)
            aus[i, :, s] = (z @ v[i, :, s]) / summe
    return aus


def zeit_einbettung(t, dim, flip=True, verschiebung=0, max_periode=10000):
    """Sinus-Einbettung eines Zeitschritts (wie diffusers get_timestep_embedding)."""
    halb = dim // 2
    expo = np.float32(-math.log(max_periode)) * np.arange(halb, dtype=np.float32) / np.float32(halb - verschiebung)
    e = np.asarray(t, np.float32).reshape(-1, 1) * np.exp(expo)[None]
    e = np.concatenate([np.sin(e), np.cos(e)], axis=-1)
    return np.concatenate([e[:, halb:], e[:, :halb]], axis=-1) if flip else e


class Zufall:
    """Normalverteilte Zufallszahlen ohne numpy.random (unter Smart App Control teils gesperrt): SplitMix64 +
    Box-Muller. Gleicher Startwert → gleiches Bild, auf jedem Rechner."""
    GOLD = np.uint64(0x9E3779B97F4A7C15)

    def __init__(self, startwert):
        self.start = np.uint64(int(startwert) % (1 << 64))
        self.zaehler = 0

    def normal(self, form):
        n = int(np.prod(form))
        m = 2 * ((n + 1) // 2)
        z = (np.arange(self.zaehler + 1, self.zaehler + m + 1, dtype=np.uint64) * self.GOLD) + self.start
        self.zaehler += m
        z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
        z ^= z >> np.uint64(31)
        u = (z >> np.uint64(11)).astype(np.float64) * 2.0 ** -53                 # gleichverteilt in [0, 1)
        r = np.sqrt(-2.0 * np.log(1.0 - u[0::2]))
        winkel = 2 * np.pi * u[1::2]
        u[0::2], u[1::2] = r * np.cos(winkel), r * np.sin(winkel)           # Paare nebeneinander → stückweise gleich
        return u[:n].astype(np.float32).reshape(form)


def _plus_mal(w, d, faktor):
    d *= faktor
    w += d


def _f32(x):
    """float16 → float32, große Felder stückweise parallel."""
    if x.size < 1 << 20:
        return x.astype(np.float32)
    aus = np.empty(x.shape, np.float32)
    parallel(lambda ab: aus.__setitem__(slice(*ab), x[ab[0]:ab[1]]), _stuecke(len(x), x.size // len(x), 1 << 18))
    return aus


def _rechenform(w, typ):
    """PyTorch-Gewicht → Matrix für x @ M: Linear (O × C) → C × O, Faltung (O × C × k × k) → (k·k·C) × O."""
    if w.ndim == 4:
        o, c, kh, kw = w.shape
        aus = np.empty((kh, kw, c, o), typ)
        parallel(lambda ab: aus.__setitem__((slice(None), slice(None), slice(*ab)), w[:, ab[0]:ab[1]].transpose(2, 3, 1, 0)),
                 _stuecke(c, o * kh * kw, 1 << 18))
        return aus.reshape(-1, o)
    aus = np.empty((w.shape[1], w.shape[0]), typ)
    parallel(lambda ab: aus.__setitem__(slice(*ab), w[:, ab[0]:ab[1]].T), _stuecke(w.shape[1], w.shape[0], 1 << 18))
    return aus


class Gewichte:
    """Gewichte eines Netzes in Rechenform: Linear → (ein × aus), Faltung → (k·k·C × O) für `falte`. Ein LoRA
    (kohya-Format: lora_down/lora_up/alpha, z. B. VegaRT) wird beim ersten Abruf fest eingerechnet. Abgelegt als float16
    (halber Speicher, Umrechnung bei jedem Abruf) oder float32 (schneller, doppelter Speicher)."""

    def __init__(self, st, lora=None, lora_faktor=1.0, halb=True):
        self.st, self.lora = st, lora
        self.typ = np.float16 if halb else np.float32
        self._fertig, self._vek, self._lora = {}, {}, {}
        if lora is not None:
            ziele = {k[:-len(".weight")].replace(".", "_"): k for k in st.keys() if k.endswith(".weight")}
            for k in lora.keys():
                if not k.endswith(".lora_down.weight"):
                    continue
                modul = k[:-len(".lora_down.weight")]
                ziel = ziele.get(modul.split("_", 2)[-1]) if modul.startswith("lora_unet_") else None
                if ziel is None:
                    raise ValueError(f"LoRA passt nicht zum Bildnetz: {modul}")
                rang = lora.form(k)[0]
                alpha = float(lora.f32(modul + ".alpha").ravel()[0]) if modul + ".alpha" in lora else rang
                self._lora[ziel] = (k, modul + ".lora_up.weight", np.float32(lora_faktor * alpha / rang))

    def hat(self, name):
        return name + ".weight" in self.st or name in self.st

    def roh32(self, name):
        """Gewicht in PyTorch-Form als float32, LoRA eingerechnet: W + Faktor · (up · down)."""
        w = self.st.f32(name)
        if name in self._lora:
            unten, oben, faktor = self._lora[name]
            d, u = self.lora.f32(unten), self.lora.f32(oben)
            delta = (u.reshape(u.shape[0], -1) @ d.reshape(d.shape[0], -1)).reshape(w.shape)
            parallel(lambda ab: _plus_mal(w[ab[0]:ab[1]], delta[ab[0]:ab[1]], faktor), _stuecke(len(w), w.size // len(w)))
        return w

    def matrix(self, name):
        m = self._fertig.get(name)
        if m is None:
            m = self._fertig[name] = _rechenform(self.roh32(name + ".weight"), self.typ)
        return m if m.dtype == np.float32 else _f32(m)

    def vektor(self, name):
        v = self._vek.get(name)
        if v is None:
            v = self._vek[name] = self.roh32(name)
        return v

    def bias(self, name):
        return self.vektor(name + ".bias") if name + ".bias" in self.st else None

    def lin(self, x, name):
        m = self.matrix(name)
        y = x.reshape(-1, x.shape[-1]) @ m                      # ein großes Matrixprodukt statt vieler kleiner
        b = self.bias(name)
        if b is not None:
            y += b
        return y.reshape(*x.shape[:-1], m.shape[1])

    def conv(self, x, name, schritt=1):
        return falte(x, self.matrix(name), self.bias(name), schritt)

    def gn(self, x, name, gruppen=32, eps=1e-5, mit_silu=False):
        return group_norm(x, self.vektor(name + ".weight"), self.vektor(name + ".bias"), gruppen, eps, mit_silu)

    def ln(self, x, name, eps=1e-5):
        return layer_norm(x, self.vektor(name + ".weight"), self.vektor(name + ".bias"), eps)

    def vorbereiten(self):
        """Alle Gewichte vorab in Rechenform bringen (LoRA einrechnen) und die Dateien freigeben."""
        for k in self.st.keys():
            if k.endswith(".weight") and len(self.st.form(k)) > 1:
                self.matrix(k[:-len(".weight")])
            else:
                self.vektor(k)
        self.st.schliesse()                                       # alles liegt jetzt im Speicher
        if self.lora is not None:
            self.lora.schliesse()
        return self


# ---------------------------------------------------------------------------------------------
# Bildnetz (UNet2DConditionModel) – Aufbau nur aus der config: SDXL/Vega (text_time, lineare Projektion) und SD 1.5
# ---------------------------------------------------------------------------------------------
class UNet:
    def __init__(self, gew, cfg, abbruch=None):
        self.g, self.cfg, self.abbruch = gew, cfg, abbruch
        self.kanaele = list(cfg["block_out_channels"])
        n = len(self.kanaele)
        liste = lambda x: list(x) if isinstance(x, (list, tuple)) else [x] * n  # noqa: E731
        self.koepfe = liste(cfg.get("num_attention_heads") or cfg.get("attention_head_dim") or 8)
        self.tiefe = liste(cfg.get("transformer_layers_per_block", 1))
        self.tiefe_auf = liste(cfg.get("reverse_transformer_layers_per_block") or self.tiefe[::-1])
        self.schichten = cfg.get("layers_per_block", 2)
        self.gruppen, self.eps = cfg.get("norm_num_groups", 32), cfg.get("norm_eps", 1e-5)
        self.ab, self.auf = cfg["down_block_types"], cfg["up_block_types"]
        self.mitte = cfg.get("mid_block_type") or "UNetMidBlock2DCrossAttn"
        self.zusatz = cfg.get("addition_embed_type")
        self.flip, self.versch = cfg.get("flip_sin_to_cos", True), cfg.get("freq_shift", 0)
        self.vielfaches = 2 ** (n - 1)
        self.takt = None                                          # takt(anteil des Durchlaufs) für feinen Fortschritt
        quer = lambda typ, d: d if "CrossAttn" in typ else 0  # noqa: E731
        self.takte = (sum(self.schichten * (1 + quer(t, d)) for t, d in zip(self.ab, self.tiefe))
                      + sum((self.schichten + 1) * (1 + quer(t, d)) for t, d in zip(self.auf, self.tiefe_auf))
                      + quer(self.mitte, self.tiefe[-1]))
        self._gezaehlt = 0

    def _pruefe(self):
        """Nach jedem Block: Abbruch abfragen, Fortschritt melden."""
        if self.abbruch and self.abbruch():
            raise Abgebrochen()
        self._gezaehlt += 1
        if self.takt:
            self.takt(min(1.0, self._gezaehlt / self.takte))

    def _resnet(self, x, emb, p):
        g = self.g
        h = g.conv(g.gn(x, p + "norm1", self.gruppen, self.eps, True), p + "conv1")
        h += g.lin(emb, p + "time_emb_proj")[:, None, None, :]
        h = g.conv(g.gn(h, p + "norm2", self.gruppen, self.eps, True), p + "conv2")
        if g.hat(p + "conv_shortcut"):
            x = g.conv(x, p + "conv_shortcut")
        return x + h

    def _attn(self, x, kontext, p, koepfe):
        g = self.g
        return g.lin(aufmerksamkeit(g.lin(x, p + "to_q"), g.lin(kontext, p + "to_k"), g.lin(kontext, p + "to_v"), koepfe),
                     p + "to_out.0")

    def _transformer(self, x, kontext, p, koepfe, tiefe):
        g = self.g
        b, h, w, c = x.shape
        t = g.lin(g.gn(x, p + "norm", self.gruppen, 1e-6).reshape(b, h * w, c), p + "proj_in")
        for i in range(tiefe):
            q = f"{p}transformer_blocks.{i}."
            n = g.ln(t, q + "norm1")
            t = t + self._attn(n, n, q + "attn1.", koepfe)
            t = t + self._attn(g.ln(t, q + "norm2"), kontext, q + "attn2.", koepfe)
            t = t + g.lin(geglu(g.lin(g.ln(t, q + "norm3"), q + "ff.net.0.proj")), q + "ff.net.2")
            self._pruefe()
        return g.lin(t, p + "proj_out").reshape(b, h, w, c) + x

    def __call__(self, x, t, kontext, gepoolt=None, zeit_ids=None):
        """x: B × h × w × 4 (Latent), t: Zeitschritt, kontext: B × 77 × D, bei SDXL dazu gepoolt (B × 1280) und
        zeit_ids (B × 6: Originalgröße, Ausschnitt oben/links, Zielgröße). Liefert das vorhergesagte Rauschen."""
        g, n = self.g, len(self.kanaele)
        if x.shape[1] % self.vielfaches or x.shape[2] % self.vielfaches:
            raise ValueError(f"Latent-Größe muss durch {self.vielfaches} teilbar sein")
        self._gezaehlt = 0
        emb = zeit_einbettung(np.full(len(x), t), self.kanaele[0], self.flip, self.versch)
        emb = g.lin(silu(g.lin(emb, "time_embedding.linear_1")), "time_embedding.linear_2")
        if self.zusatz == "text_time":
            z = zeit_einbettung(np.asarray(zeit_ids, np.float32).ravel(), self.cfg.get("addition_time_embed_dim", 256),
                                self.flip, self.versch).reshape(len(x), -1)
            z = np.concatenate([np.asarray(gepoolt, np.float32), z], axis=-1)
            emb = emb + g.lin(silu(g.lin(z, "add_embedding.linear_1")), "add_embedding.linear_2")
        emb = silu(emb)                                          # jedes ResNet nimmt silu(emb)
        h = g.conv(x, "conv_in")
        reste = [h]
        for i, typ in enumerate(self.ab):
            p = f"down_blocks.{i}."
            for j in range(self.schichten):
                h = self._resnet(h, emb, f"{p}resnets.{j}.")
                if "CrossAttn" in typ:
                    h = self._transformer(h, kontext, f"{p}attentions.{j}.", self.koepfe[i], self.tiefe[i])
                reste.append(h)
                self._pruefe()
            if i < n - 1:
                h = g.conv(h, p + "downsamplers.0.conv", schritt=2)
                reste.append(h)
        h = self._resnet(h, emb, "mid_block.resnets.0.")
        if self.mitte == "UNetMidBlock2DCrossAttn":
            h = self._transformer(h, kontext, "mid_block.attentions.0.", self.koepfe[-1], self.tiefe[-1])
            h = self._resnet(h, emb, "mid_block.resnets.1.")
        koepfe_auf = self.koepfe[::-1]
        for i, typ in enumerate(self.auf):
            p = f"up_blocks.{i}."
            for j in range(self.schichten + 1):
                h = self._resnet(np.concatenate([h, reste.pop()], axis=-1), emb, f"{p}resnets.{j}.")
                if "CrossAttn" in typ:
                    h = self._transformer(h, kontext, f"{p}attentions.{j}.", koepfe_auf[i], self.tiefe_auf[i])
                self._pruefe()
            if i < n - 1:
                h = g.conv(h.repeat(2, axis=1).repeat(2, axis=2), p + "upsamplers.0.conv")
        return g.conv(g.gn(h, "conv_norm_out", self.gruppen, self.eps, True), "conv_out")


# ---------------------------------------------------------------------------------------------
# LCM-Verfahren (Latent Consistency, wie diffusers LCMScheduler) – wenige Schritte dank VegaRT
# ---------------------------------------------------------------------------------------------
class LCM:
    def __init__(self, schritte, beta_start=0.00085, beta_ende=0.012, training=1000, original=50):
        betas = np.linspace(beta_start ** 0.5, beta_ende ** 0.5, training, dtype=np.float64) ** 2   # „scaled_linear“
        self.acp = np.cumprod(1.0 - betas)
        herkunft = (np.arange(1, original + 1) * (training // original) - 1)[::-1]
        self.zeiten = herkunft[np.floor(np.linspace(0, len(herkunft), schritte, endpoint=False)).astype(np.int64)]

    def schritt(self, i, eps, x, zufall):
        """Ein Schritt: (nächstes Latent, aktuelle Schätzung des fertigen Bildes)."""
        t = int(self.zeiten[i])
        a = self.acp[t]
        st = t * 10.0                                            # timestep_scaling = 10, sigma_data = 0,5
        c_skip, c_out = 0.25 / (st * st + 0.25), st / (st * st + 0.25) ** 0.5
        x0 = (x - np.sqrt(1 - a) * eps) / np.sqrt(a)
        fertig = (c_out * x0 + c_skip * x).astype(np.float32)
        if i == len(self.zeiten) - 1:
            return fertig, fertig
        a2 = self.acp[int(self.zeiten[i + 1])]
        return (np.sqrt(a2) * fertig + np.sqrt(1 - a2) * zufall.normal(x.shape)).astype(np.float32), fertig


# ---------------------------------------------------------------------------------------------
# Decoder: Latent → Bild. VAE (SDXL, beste Qualität) und TAESDXL (MIT, sehr schnell – für Vorschau)
# ---------------------------------------------------------------------------------------------
class VAEDecoder:
    def __init__(self, st, cfg):
        self.g, self.cfg = Gewichte(st, halb=False).vorbereiten(), cfg
        self.skala = cfg.get("scaling_factor", 0.18215)
        self.gruppen = cfg.get("norm_num_groups", 32)
        self.stufen = len(cfg["block_out_channels"])
        self.schichten = cfg.get("layers_per_block", 2) + 1

    def _resnet(self, x, p):
        g = self.g
        h = g.conv(g.gn(x, p + "norm1", self.gruppen, 1e-6, True), p + "conv1")
        h = g.conv(g.gn(h, p + "norm2", self.gruppen, 1e-6, True), p + "conv2")
        if g.hat(p + "conv_shortcut"):
            x = g.conv(x, p + "conv_shortcut")
        return x + h

    def __call__(self, z, abbruch=None, takt=None):
        """z: B × h × w × 4 (Latent wie im UNet) → B × 8h × 8w × 3 in [0, 1]. takt(anteil) meldet den Fortschritt."""
        g = self.g
        h = g.conv(g.conv(z / np.float32(self.skala), "post_quant_conv"), "decoder.conv_in")
        h = self._resnet(h, "decoder.mid_block.resnets.0.")
        b, hh, ww, c = h.shape
        p = "decoder.mid_block.attentions.0."
        t = g.gn(h, p + "group_norm", self.gruppen, 1e-6).reshape(b, hh * ww, c)
        t = g.lin(aufmerksamkeit(g.lin(t, p + "to_q"), g.lin(t, p + "to_k"), g.lin(t, p + "to_v"), 1), p + "to_out.0")
        h = self._resnet(h + t.reshape(b, hh, ww, c), "decoder.mid_block.resnets.1.")
        for i in range(self.stufen):
            for j in range(self.schichten):
                h = self._resnet(h, f"decoder.up_blocks.{i}.resnets.{j}.")
                if abbruch and abbruch():
                    raise Abgebrochen()
                if takt:                                          # die hinteren Stufen sind größer und teurer
                    takt(sum(4 ** s for s in range(i)) / sum(4 ** s for s in range(self.stufen))
                         + 4 ** i * (j + 1) / self.schichten / sum(4 ** s for s in range(self.stufen)))
            if g.hat(f"decoder.up_blocks.{i}.upsamplers.0.conv"):
                h = g.conv(h.repeat(2, axis=1).repeat(2, axis=2), f"decoder.up_blocks.{i}.upsamplers.0.conv")
        h = g.conv(g.gn(h, "decoder.conv_norm_out", self.gruppen, 1e-6, True), "decoder.conv_out")
        return np.clip(h * np.float32(0.5) + np.float32(0.5), 0, 1)


class TAEDecoder:
    """Tiny AutoEncoder (madebyollin/taesd, Aufbau „Decoder“): Clamp, Faltung, 3×(3 Blöcke + 2× hoch), Block, Faltung."""

    def __init__(self, st):
        self.g = Gewichte(st, halb=False).vorbereiten()

    def __call__(self, z, abbruch=None, takt=None):
        g = self.g
        relu = lambda x: np.maximum(x, np.float32(0))  # noqa: E731
        h = relu(g.conv(np.tanh(z / np.float32(3)) * np.float32(3), "1"))
        for i in range(3, 19):
            if g.hat(f"{i}.conv.0"):                             # Block: 3 Faltungen + Rest, dann ReLU
                r = relu(g.conv(relu(g.conv(h, f"{i}.conv.0")), f"{i}.conv.2"))
                h = relu(g.conv(r, f"{i}.conv.4") + h)
            elif g.hat(str(i)):                                  # nach dem Verdoppeln: Faltung ohne Bias
                h = g.conv(h.repeat(2, axis=1).repeat(2, axis=2), str(i))
        return np.clip(g.conv(h, "19"), 0, 1)


# ---------------------------------------------------------------------------------------------
# Prompt: Standardfassung für Lernkarten-Gänse. Im Normalfall gibt man nur das Wort/die Floskel der Karte und eine
# kurze Beschreibung (Englisch: wie und wo ist die Gans?) an; die Vorlage lässt sich – über einen eigenen Knopf –
# anpassen und zurücksetzen. Platzhalter: {description} (Beschreibung) und {word} (Wort der Karte – im Standard nicht
# benutzt, denn das Modell schreibt keinen sauberen Text; das Wort setzt danach „GANS-Bild gestalten“ aufs Bild).
# ---------------------------------------------------------------------------------------------
PROMPT_STANDARD = ("realistic wildlife photograph of a domestic goose, {description}, natural light, sharp focus on the "
                   "goose, detailed feathers, calm simple background")
NEGATIV_STANDARD = ("text, letters, words, caption, watermark, logo, cartoon, drawing, painting, illustration, 3d render, "
                    "deformed, extra legs, extra heads, blurry")
# „keine Menschen“: vor allem positiv formuliert (ein Negativ-Prompt allein vertreibt Menschen kaum, siehe 4.3b),
# dazu sanft im Negativ-Prompt. Bewusst ohne die Wörter „people/person“ im positiven Teil – die würden sie herbeirufen.
ALLEIN = "the goose is alone, empty quiet surroundings"
NEGATIV_MENSCHEN = "people, person, human, man, woman, child, face, hands, crowd"
PLATZHALTER = {"{description}": ("{beschreibung}", "{descripcion}", "{descripción}"),
               "{word}": ("{wort}", "{palabra}")}
PROMPT_MAX = 600                                   # Zeichen (CLIP liest ohnehin nur 75 Token)


def _vereinheitlichen(vorlage):
    """Platzhalter auf Deutsch/Spanisch ({beschreibung}, {palabra} …) → englische Form."""
    for ziel, andere in PLATZHALTER.items():
        for a in andere:
            vorlage = re.sub(re.escape(a), ziel, vorlage, flags=re.IGNORECASE)
    return vorlage


def _sauber(text, laenge=PROMPT_MAX):
    text = " ".join(str(text or "").replace("{", "(").replace("}", ")").split())
    return text[:laenge].strip(" ,")


def pruefe_vorlage(vorlage, negativ=None):
    """Eigene Fassung prüfen → (vorlage, negativ) bereinigt; ValueError mit freundlicher Meldung (3 Sprachen)."""
    v = " ".join(_vereinheitlichen(str(vorlage or "")).split())
    if "{description}" not in v:
        raise ValueError(_t("Die Vorlage braucht den Platzhalter {description} – dort setzt das Programm deine "
                            "Beschreibung ein.",
                            "The template needs the placeholder {description} – that’s where your description goes.",
                            "La plantilla necesita el marcador {description}: ahí va tu descripción."))
    if len(v) > PROMPT_MAX or len(str(negativ or "")) > PROMPT_MAX:
        raise ValueError(_t(f"Etwas kürzer bitte (höchstens {PROMPT_MAX} Zeichen) – das Modell liest sowieso nur den "
                            "Anfang.",
                            f"A bit shorter, please (at most {PROMPT_MAX} characters) – the model only reads the "
                            "beginning anyway.",
                            f"Un poco más corto, por favor (máximo {PROMPT_MAX} caracteres): el modelo solo lee el "
                            "principio."))
    return v, " ".join(str(negativ if negativ is not None else NEGATIV_STANDARD).split())


def baue_prompt(beschreibung, wort="", ohne_menschen=True, vorlage=None, negativ=None):
    """Beschreibung (+ Wort) in die Vorlage setzen → (prompt, negativ_prompt oder None).
    Ohne „keine Menschen“ gibt es keinen Negativ-Prompt (am schnellsten); mit wird er sanft in den ersten Schritten
    angewendet (siehe CFG/CFG_SCHRITTE)."""
    vorlage, neg = pruefe_vorlage(vorlage or PROMPT_STANDARD, negativ)
    b = _sauber(beschreibung, 300) or "standing on a green meadow"
    if ohne_menschen:
        b = f"{b}, {ALLEIN}"
    prompt = vorlage.replace("{description}", b).replace("{word}", _sauber(wort, 60))
    prompt = re.sub(r"(\s*,\s*)+", ", ", prompt).strip(" ,")             # leere Platzhalter hinterlassen keine „, ,“
    if not ohne_menschen:
        return prompt, None
    neg = ", ".join(t for t in (neg, NEGATIV_MENSCHEN) if t)
    return prompt, neg


def token_anzahl(text, ordner=None):
    """Wie viele CLIP-Token der Text belegt (ohne Start/Ende) – mehr als 75 schneidet das Modell ab. None ohne Modell."""
    o = Path(ordner or modell_ordner())
    try:
        if str(o) not in _TOKENIZER:
            _TOKENIZER[str(o)] = ClipTokenizer(o / "tokenizer_vocab.json", o / "tokenizer_merges.txt")
    except (OSError, ValueError):
        return None
    return len(_TOKENIZER[str(o)].text_ids(text))


_TOKENIZER = {}


# ---------------------------------------------------------------------------------------------
# Text → Bild: Segmind Vega + VegaRT
# ---------------------------------------------------------------------------------------------
BREITE, HOEHE = 896, 640                      # ≈ Karte 88 : 63, Vielfaches von 32
# 4 Schritte wie in der VegaRT-Anleitung. Negativ-Prompt nur sanft und nur am Anfang (CFG 1,5 in Schritt 1–2): stärker
# macht LCM-Bilder grell und fehlerhaft. Menschen hält vor allem eine positive Formulierung fern („alone, empty …“).
SCHRITTE, CFG, CFG_SCHRITTE = 4, 1.5, 2


class BildModell:
    """Erzeugt Bilder offline. Fortschritt über `melde(text)` und `fortschritt(anteil 0…1)`, Abbruch über
    `abbruch()` → True (wird zwischen den Netzblöcken abgefragt, löst `Abgebrochen` aus)."""

    def __init__(self, ordner=None, halb=None):
        self.ordner = Path(ordner or modell_ordner())
        if halb is None:              # float16: 1,4 GB weniger Speicher, dank paralleler Umrechnung kaum langsamer (gemessen)
            halb = os.environ.get("MGD_KI_HALB", "1") != "0"
        self.halb = halb

    def _json(self, name):
        return json.loads((self.ordner / name).read_text(encoding="utf-8"))

    def erzeuge(self, prompt, negativ=None, breite=BREITE, hoehe=HOEHE, schritte=SCHRITTE, cfg=CFG,
                cfg_schritte=CFG_SCHRITTE, startwert=None, decoder="vae", melde=None, fortschritt=None, abbruch=None,
                vorschau=None):
        """Ergebnis: dict(bild=PIL.Image, startwert, zeiten, latent). Ohne Negativ-Prompt (oder cfg ≤ 1) ohne Guidance –
        am schnellsten; sonst Classifier-Free-Guidance nur in den ersten `cfg_schritte` Schritten (dort entsteht der
        Bildaufbau). decoder: "vae" (beste Qualität) oder "schnell" (TAESDXL, gut 10× schneller, etwas gröber).
        `vorschau(PIL.Image)` bekommt nach jedem Schritt außer dem letzten eine schnelle Vorschau."""
        import time
        from PIL import Image
        melde = melde or (lambda t: None)
        if breite % 32 or hoehe % 32 or not (256 <= breite <= 2048 and 256 <= hoehe <= 2048):
            raise ValueError("Breite und Höhe: 256 … 2048, Vielfaches von 32")
        if not 1 <= int(schritte) <= 8:
            raise ValueError("Schritte: 1 … 8")
        if not status(self.ordner)["installiert"]:
            raise FileNotFoundError(_t("Das KI-Bildmodell ist noch nicht vollständig geladen – unter Werkzeuge → "
                                       "„KI-Bildmodell laden“ geht das in einem Rutsch.",
                                       "The AI image model isn’t fully downloaded yet – Tools → “Download AI image "
                                       "model” does it in one go.",
                                       "El modelo de imágenes IA aún no está descargado por completo; en Herramientas → "
                                       "«Descargar modelo de imágenes IA» se hace de una vez."))
        if startwert is None:
            startwert = int.from_bytes(os.urandom(4), "little")
        mit_cfg = bool(negativ) and cfg > 1 and cfg_schritte > 0
        n_cfg = min(int(cfg_schritte), int(schritte)) if mit_cfg else 0

        # Fortschritt nach geschätzten Kosten (Sekunden auf einem Laptop von 2023 – es zählt nur das Verhältnis)
        px = breite * hoehe / (896 * 640)
        k_text, k_laden, k_pass, k_pass2 = 2.5, 3.5, 7.5 * px, 11.5 * px
        k_dec, k_vor = (33 * px if decoder == "vae" else 2 * px), 2 * px
        gesamt = (k_text + k_laden + n_cfg * k_pass2 + (schritte - n_cfg) * k_pass + k_dec
                  + (schritte - 1) * k_vor * bool(vorschau))
        erledigt = [0.0]

        def fort(kosten=0.0, anteil=1.0, fertig=False):
            if fortschritt:
                fortschritt(min(1.0, (erledigt[0] + kosten * anteil) / gesamt))
            if fertig:
                erledigt[0] += kosten

        def pruefe():
            if abbruch and abbruch():
                raise Abgebrochen()

        zeiten, t0 = {}, time.time()
        melde(_t("Beschreibung verstehen …", "Reading the description …", "Leyendo la descripción …"))
        fort(0)
        text = TextTeil(self.ordner)
        try:
            emb, pool = text([negativ, prompt] if mit_cfg else [prompt])
        finally:
            text.schliesse()
        del text
        zeiten["text"] = time.time() - t0
        fort(k_text, fertig=True)
        pruefe()

        t1 = time.time()
        melde(_t("Bildnetz vorbereiten (VegaRT einrechnen) …", "Preparing the image network (merging VegaRT) …",
                 "Preparando la red de imagen (integrando VegaRT) …"))
        gew = Gewichte(SafeTensors(self.ordner / "unet.fp16.safetensors"),
                       SafeTensors(self.ordner / "vegart_lora.safetensors"), halb=self.halb).vorbereiten()
        unet = UNet(gew, self._json("unet_config.json"), abbruch)
        tae = TAEDecoder(SafeTensors(self.ordner / "taesdxl_decoder.safetensors")) if vorschau or decoder != "vae" else None
        zeiten["laden"] = time.time() - t1
        fort(k_laden, fertig=True)
        pruefe()

        t2 = time.time()
        lcm = LCM(int(schritte))
        zufall = Zufall(startwert)
        x = zufall.normal((1, hoehe // 8, breite // 8, 4))
        ids = np.array([[hoehe, breite, 0, 0, hoehe, breite]] * len(emb), np.float32)
        for i, t in enumerate(lcm.zeiten):
            melde(_t(f"Schritt {i + 1} von {schritte} …", f"Step {i + 1} of {schritte} …", f"Paso {i + 1} de {schritte} …"))
            k = k_pass2 if i < n_cfg else k_pass
            unet.takt = lambda a, k=k: fort(k, a)
            if i < n_cfg:
                e = unet(np.concatenate([x, x]), t, emb, pool, ids)
                eps = e[0:1] + np.float32(cfg) * (e[1:2] - e[0:1])
            else:
                eps = unet(x, t, emb[-1:], pool[-1:], ids[-1:])
            x, fertig = lcm.schritt(i, eps, x, zufall)
            fort(k, fertig=True)
            if vorschau and i < schritte - 1:
                vorschau(Image.fromarray(np.round(tae(fertig)[0] * 255).astype(np.uint8)))
                fort(k_vor, fertig=True)
            pruefe()
        zeiten["schritte"] = time.time() - t2
        del unet, gew                                             # Speicher frei für den Decoder

        t3 = time.time()
        melde(_t("Bild entwickeln …", "Developing the image …", "Revelando la imagen …"))
        if decoder == "vae":
            with SafeTensors(self.ordner / "vae.fp16.safetensors") as st:
                rgb = VAEDecoder(st, self._json("vae_config.json"))(fertig, abbruch, lambda a: fort(k_dec, a))[0]
        else:
            rgb = tae(fertig, abbruch)[0]
        zeiten["decoder"] = time.time() - t3
        zeiten["gesamt"] = time.time() - t0
        fort(k_dec, fertig=True)
        return dict(bild=Image.fromarray(np.round(rgb * 255).astype(np.uint8)), startwert=startwert, zeiten=zeiten,
                    latent=fertig)


# ---------------------------------------------------------------------------------------------
# Befehlszeile
# ---------------------------------------------------------------------------------------------
def _bild_erzeugen(a):
    """--erzeugen: Fortschritt als Zeilen (für das Live-Protokoll der Oberfläche), am Ende eine Ergebniszeile (JSON)."""
    import time
    ziel = Path(a.aus) if a.aus else None
    letzte = [-1]

    def fort(anteil):
        p = int(anteil * 100) // 5 * 5
        if p > letzte[0]:
            letzte[0] = p
            print(f"  {p} %", flush=True)

    def vorschau(bild):
        tmp = Path(a.vorschau).with_name(Path(a.vorschau).name + ".tmp")
        bild.convert("RGB").save(tmp, "JPEG", quality=85)
        os.replace(tmp, a.vorschau)                               # nie halb geschrieben lesen

    t0 = time.time()
    r = BildModell().erzeuge(a.erzeugen, negativ=a.negativ, breite=a.breite, hoehe=a.hoehe, schritte=a.schritte,
                             cfg=a.cfg, cfg_schritte=a.cfg_schritte, startwert=a.startwert,
                             decoder="schnell" if a.schnell else "vae", melde=lambda t: print(t, flush=True),
                             fortschritt=fort, vorschau=vorschau if a.vorschau else None)
    ziel = ziel or Path(f"ki-bild-{r['startwert']}.png")
    ziel.parent.mkdir(parents=True, exist_ok=True)
    if ziel.suffix.lower() in (".jpg", ".jpeg"):
        r["bild"].save(ziel, "JPEG", quality=95)
    else:
        r["bild"].save(ziel)
    s = round(time.time() - t0)
    print(_t(f"Fertig – deine Gans ist da: {ziel} (Startwert {r['startwert']}, {s} s).",
             f"Done – your goose is here: {ziel} (seed {r['startwert']}, {s} s).",
             f"Listo: aquí está tu ganso: {ziel} (semilla {r['startwert']}, {s} s)."), flush=True)
    print("#ergebnis " + json.dumps(dict(datei=str(ziel), startwert=r["startwert"],
                                         zeiten={k: round(v, 1) for k, v in r["zeiten"].items()})), flush=True)


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="KI-Bilder für Me Goos-ta Deutsch: Modell laden, prüfen, Bilder erzeugen")
    ap.add_argument("--laden", action="store_true", help="Bildmodell herunterladen (mit Prüfsummen, fortsetzbar)")
    ap.add_argument("--status", action="store_true", help="zeigt, was vom Bildmodell schon da ist")
    ap.add_argument("--erzeugen", metavar="BESCHREIBUNG", help="Bild aus einer (englischen) Beschreibung erzeugen")
    ap.add_argument("--negativ", metavar="TEXT", help="was nicht ins Bild soll (z. B. „people“) – kostet etwas Zeit")
    ap.add_argument("--startwert", type=int, help="gleicher Startwert → gleiches Bild")
    ap.add_argument("--schritte", type=int, default=SCHRITTE, help=f"Rechenschritte 1 … 8 (Standard {SCHRITTE})")
    ap.add_argument("--cfg", type=float, default=CFG, help=f"Stärke des Negativ-Prompts (Standard {CFG})")
    ap.add_argument("--cfg-schritte", type=int, default=CFG_SCHRITTE,
                    help=f"in wie vielen ersten Schritten der Negativ-Prompt wirkt (Standard {CFG_SCHRITTE})")
    ap.add_argument("--breite", type=int, default=BREITE, help=f"Bildbreite (Vielfaches von 32, Standard {BREITE})")
    ap.add_argument("--hoehe", type=int, default=HOEHE, help=f"Bildhöhe (Vielfaches von 32, Standard {HOEHE})")
    ap.add_argument("--schnell", action="store_true", help="schneller Decoder (TAESDXL) statt VAE – etwas gröber")
    ap.add_argument("--aus", metavar="DATEI", help="Zieldatei .png/.jpg (Standard: ki-bild-<Startwert>.png)")
    ap.add_argument("--vorschau", metavar="DATEI", help="nach jedem Schritt eine Vorschau (JPG) dorthin schreiben")
    a = ap.parse_args(argv)
    for strom in (sys.stdout, sys.stderr):
        try:
            strom.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    if a.laden or a.erzeugen:
        try:
            if a.laden:
                lade(melde=lambda t: print(t, flush=True))
            else:
                _bild_erzeugen(a)
        except Exception as e:  # noqa: BLE001
            print(f"✕ {e}", flush=True)
            return 1
        return 0
    st = status()
    print(json.dumps(st, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
