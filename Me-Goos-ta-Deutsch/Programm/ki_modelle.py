#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Me Goos-ta Deutsch – KI-Bildvergrößerung in reinem NumPy (ohne PyTorch, ohne GPU)
==================================================================================
Netze (alle mit freier Lizenz, Gewichte öffentlich auf GitHub):
  RRDBNet          Real-ESRGAN x4plus / x2plus / x4plus_anime_6B   (Wang et al. 2021, BSD-3-Clause)
  SRVGGNetCompact  Real-ESRGAN realesr-general-x4v3               (BSD-3-Clause)
  SwinIR           003_realSR_BSRGAN_DFOWMFC_s64w8_SwinIR-L_x4_GAN (Liang et al. 2021, Apache-2.0)

Die Original-Gewichte (*.pth) werden OHNE PyTorch gelesen: Eine PyTorch-Datei ist ein ZIP mit einem
Pickle. Pickle darf beliebigen Code ausführen – deshalb erlaubt der Leser hier nur eine feste Liste
harmloser Bausteine (Tensor-Wiederaufbau, OrderedDict) und lehnt alles andere ab. Zusätzlich wird jede
heruntergeladene Datei per SHA-256 mit dem bekannten Wert verglichen.

Gerechnet wird kachelweise (Standard 128 px mit 16 px Überlappung), damit der Speicher klein bleibt.
"""
from __future__ import annotations

import collections
import hashlib
import io
import math
import pickle
import zipfile
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------------------------
# Modellkatalog: Download-Adresse (offizielle GitHub-Releases), Prüfsumme, Netz, Lizenz
# ---------------------------------------------------------------------------------------------
KATALOG = {
    "realesrgan-x4plus": dict(
        titel="Real-ESRGAN x4plus", netz="rrdb", faktor=4, bloecke=23,
        datei="RealESRGAN_x4plus.pth",
        url="https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
        sha256="4fa0d38905f75ac06eb49a7951b426670021be3018265fd191d2125df9d682f1",
        lizenz="BSD-3-Clause", quelle="https://github.com/xinntao/Real-ESRGAN"),
    "realesrgan-x2plus": dict(
        titel="Real-ESRGAN x2plus", netz="rrdb", faktor=2, bloecke=23,
        datei="RealESRGAN_x2plus.pth",
        url="https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth",
        sha256="49fafd45f8fd7aa8d31ab2a22d14d91b536c34494a5cfe31eb5d89c2fa266abb",
        lizenz="BSD-3-Clause", quelle="https://github.com/xinntao/Real-ESRGAN"),
    "realesrgan-anime6b": dict(
        titel="Real-ESRGAN x4plus anime 6B", netz="rrdb", faktor=4, bloecke=6,
        datei="RealESRGAN_x4plus_anime_6B.pth",
        url="https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth",
        sha256="f872d837d3c90ed2e05227bed711af5671a6fd1c9f7d7e91c911a61f155e99da",
        lizenz="BSD-3-Clause", quelle="https://github.com/xinntao/Real-ESRGAN"),
    "realesr-general-x4v3": dict(
        titel="Real-ESRGAN general x4v3", netz="srvgg", faktor=4,
        datei="realesr-general-x4v3.pth",
        url="https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth",
        sha256="8dc7edb9ac80ccdc30c3a5dca6616509367f05fbc184ad95b731f05bece96292",
        lizenz="BSD-3-Clause", quelle="https://github.com/xinntao/Real-ESRGAN"),
    "swinir-l-real-x4": dict(
        titel="SwinIR-L Real-World x4 (GAN)", netz="swinir", faktor=4,
        datei="003_realSR_BSRGAN_DFOWMFC_s64w8_SwinIR-L_x4_GAN.pth",
        url="https://github.com/JingyunLiang/SwinIR/releases/download/v0.0/"
            "003_realSR_BSRGAN_DFOWMFC_s64w8_SwinIR-L_x4_GAN.pth",
        sha256="99adfa91350a84c99e946c1eb3d8fce34bc28f57d807b09dc8fe40a316328c0a",
        lizenz="Apache-2.0", quelle="https://github.com/JingyunLiang/SwinIR"),
}


# ---------------------------------------------------------------------------------------------
# Sicherer Leser für PyTorch-Dateien (*.pth, ZIP-Format ab PyTorch 1.6)
# ---------------------------------------------------------------------------------------------
_DTYPES = {"FloatStorage": np.float32, "HalfStorage": np.float16, "DoubleStorage": np.float64,
           "LongStorage": np.int64, "IntStorage": np.int32, "ShortStorage": np.int16,
           "ByteStorage": np.uint8, "CharStorage": np.int8, "BoolStorage": np.bool_,
           "BFloat16Storage": None}


class _Speicher:
    """Platzhalter für einen Speicher-Typ (torch.FloatStorage …) – trägt nur den NumPy-Datentyp."""
    def __init__(self, name):
        if _DTYPES.get(name) is None:
            raise pickle.UnpicklingError(f"Datentyp {name} wird nicht unterstützt")
        self.dtype = np.dtype(_DTYPES[name])


def _tensor_aus(speicher, versatz, groesse, schritte, *_rest):
    groesse, schritte = tuple(groesse), tuple(schritte)
    if not groesse:
        return np.array(speicher[versatz], copy=True)
    n = 1 + sum((g - 1) * s for g, s in zip(groesse, schritte))
    if versatz < 0 or versatz + n > speicher.size or min(schritte) < 0:
        raise pickle.UnpicklingError("Tensor zeigt außerhalb seines Speichers")
    basis = speicher[versatz:versatz + n]
    return np.lib.stride_tricks.as_strided(
        basis, shape=groesse, strides=[s * basis.itemsize for s in schritte], writeable=False).copy()


def _parameter_aus(daten, *_rest):
    return daten


class _SichererLeser(pickle.Unpickler):
    ERLAUBT = {
        ("collections", "OrderedDict"): collections.OrderedDict,
        ("torch._utils", "_rebuild_tensor_v2"): _tensor_aus,
        ("torch._utils", "_rebuild_tensor"): _tensor_aus,
        ("torch._utils", "_rebuild_parameter"): _parameter_aus,
    }

    def __init__(self, datei, archiv, praefix):
        super().__init__(datei)
        self.archiv, self.praefix, self.cache = archiv, praefix, {}

    def find_class(self, modul, name):
        if (modul, name) in self.ERLAUBT:
            return self.ERLAUBT[(modul, name)]
        if modul == "torch" and name in _DTYPES:
            return lambda *a, _n=name: _Speicher(_n)       # wird nur als Typ-Marke gebraucht
        raise pickle.UnpicklingError(f"Nicht erlaubter Inhalt in der Modelldatei: {modul}.{name}")

    def persistent_load(self, pid):
        if not (isinstance(pid, tuple) and len(pid) >= 5 and pid[0] == "storage"):
            raise pickle.UnpicklingError("Unbekannter Verweis in der Modelldatei")
        typ, schluessel = pid[1], str(pid[2])
        if not schluessel.isalnum():
            raise pickle.UnpicklingError("Ungültiger Speicher-Name")
        if callable(typ) and not isinstance(typ, _Speicher):
            typ = typ()
        if schluessel not in self.cache:
            roh = self.archiv.read(f"{self.praefix}/data/{schluessel}")
            self.cache[schluessel] = np.frombuffer(roh, dtype=typ.dtype)
        return self.cache[schluessel]


def lies_pth(pfad):
    """Liest eine PyTorch-Gewichtsdatei ohne PyTorch. Gibt {name: np.ndarray(float32)} zurück."""
    with zipfile.ZipFile(pfad) as z:
        pkl = [n for n in z.namelist() if n.endswith("/data.pkl")]
        if len(pkl) != 1:
            raise ValueError("Keine gültige PyTorch-Datei (data.pkl fehlt)")
        praefix = pkl[0][: -len("/data.pkl")]
        obj = _SichererLeser(io.BytesIO(z.read(pkl[0])), z, praefix).load()
    for schluessel in ("params_ema", "params", "state_dict", "model"):
        if isinstance(obj, dict) and schluessel in obj and isinstance(obj[schluessel], dict):
            obj = obj[schluessel]
            break
    if not isinstance(obj, dict):
        raise ValueError("Unerwarteter Inhalt der Modelldatei")
    return {k: np.asarray(v, dtype=np.float32) for k, v in obj.items()
            if isinstance(v, np.ndarray) and v.dtype.kind in "fiub"}


def sha256(pfad):
    h = hashlib.sha256()
    with open(pfad, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def pth_zu_npz(pth, npz, halb=True):
    """Wandelt *.pth in eine kompakte, pickle-freie NumPy-Datei (float16 halbiert die Größe)."""
    w = lies_pth(pth)
    daten = {k.replace(".", "__"): (v.astype(np.float16) if halb and v.dtype == np.float32
                                     and not k.endswith("relative_position_index") else v)
             for k, v in w.items() if not k.endswith("attn_mask")}
    tmp = Path(str(npz) + ".tmp.npz")
    np.savez_compressed(tmp, **daten)
    tmp.replace(npz)
    return npz


def lade_npz(npz):
    with np.load(npz, allow_pickle=False) as z:
        return {k.replace("__", "."): z[k].astype(np.float32) for k in z.files}


# ---------------------------------------------------------------------------------------------
# Grundoperationen (Bildformat: H × W × C, float32)
# ---------------------------------------------------------------------------------------------
_STREIFEN_BYTES = 48 * 1024 * 1024          # größere Faltungen werden in Streifen gerechnet (Speicherspitze wie bisher)


def gewichte_matrix(w):
    """O×C×k×k (PyTorch) → C × (k·k·O): Spalte (ky·k + kx)·O + o gehört zur Gewichts-Lage (ky, kx) von Ausgang o."""
    return np.ascontiguousarray(w.transpose(1, 2, 3, 0).reshape(w.shape[1], -1))


def polstern(x, p):
    """Bild mit Nullrand p (unten eine Zeile mehr) – Zeile für Zeile flach als ((H + 2p + 1) · (W + 2p)) × C."""
    h, wd, c = x.shape
    xp = np.zeros((h + 2 * p + 1, wd + 2 * p, c), np.float32)
    xp[p:p + h, p:p + wd] = x
    return xp.reshape(-1, c)


def falte_flach(flach, h, breit, wm, k, c=None, b=None):
    """Faltung auf dem flachen, gepolsterten Bild ohne im2col: Ein Matrixprodukt rechnet für jedes Pixel alle k·k
    Gewichts-Lagen (C × k·k·O), danach werden die k·k Teilergebnisse um ihre Verschiebung versetzt addiert –
    dieselbe Rechnung wie im2col, nur ohne die k·k-fache Kopie des Bildes. Nimmt die ersten c Kanäle, rechnet in
    Zeilenstreifen (Speicher) und gibt h × (breit − k + 1) × O zurück (mit Bias b)."""
    o, wd = wm.shape[1] // (k * k), breit - (k - 1)
    c = flach.shape[1] if c is None else c
    aus = np.empty((h, wd, o), np.float32)
    zeilen = max(1, _STREIFEN_BYTES // (breit * wm.shape[1] * 4))
    for r0 in range(0, h, zeilen):
        r1 = min(h, r0 + zeilen)
        a, n = r0 * breit, (r1 - r0) * breit
        z = flach[a:a + n + (k - 1) * (breit + 1), :c] @ wm
        teil = z[:n, :o].copy()
        for j in range(1, k * k):
            s = (j // k) * breit + j % k
            teil += z[s:s + n, j * o:(j + 1) * o]
        teil = teil.reshape(r1 - r0, breit, o)[:, :wd]       # Überhang am Zeilenende verwerfen
        if b is None:
            aus[r0:r1] = teil
        else:
            np.add(teil, b, out=aus[r0:r1])
    return aus


def conv(x, w, b=None, wm=None):
    """2D-Faltung, 'same'-Rand mit Nullen. w: O×C×k×k (PyTorch-Reihenfolge); wm = gewichte_matrix(w), falls schon
    vorbereitet."""
    h, wd, c = x.shape
    o, k = w.shape[0], w.shape[2]
    wm = gewichte_matrix(w) if wm is None else wm
    if k == 1:
        y = x.reshape(-1, c) @ wm
        if b is not None:
            y += b
        return y.reshape(h, wd, o)
    p = k // 2
    return falte_flach(polstern(x, p), h, wd + 2 * p, wm, k, b=b)


def lrelu(x, a=0.2):
    """LeakyReLU = max(x, a·x) für 0 < a < 1 (gleiches Ergebnis wie „x ≥ 0 ? x : a·x“, mit weniger Zwischenkopien)."""
    return np.maximum(x, x * np.float32(a))


def hoch2(x):
    return x.repeat(2, axis=0).repeat(2, axis=1)


def pixel_shuffle(x, r):
    h, w, c = x.shape
    return x.reshape(h, w, c // (r * r), r, r).transpose(0, 3, 1, 4, 2).reshape(h * r, w * r, c // (r * r))


def pixel_unshuffle(x, r):
    h, w, c = x.shape
    return x.reshape(h // r, r, w // r, r, c).transpose(0, 2, 4, 1, 3).reshape(h // r, w // r, c * r * r)


def layer_norm(x, g, b, eps=1e-5):
    m = x.mean(-1, keepdims=True)
    v = ((x - m) ** 2).mean(-1, keepdims=True)
    return (x - m) / np.sqrt(v + eps) * g + b


def _erf(x):
    # Abramowitz & Stegun 7.1.26 (Fehler < 1.5e-7) – genügt für GELU
    s = np.sign(x)
    a = np.abs(x)
    t = 1.0 / (1.0 + 0.3275911 * a)
    y = 1.0 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t
               + 0.254829592) * t * np.exp(-a * a)
    return s * y


def gelu(x):
    return 0.5 * x * (1.0 + _erf(x * np.float32(1 / math.sqrt(2)))).astype(np.float32)


def softmax(x):
    x = x - x.max(-1, keepdims=True)
    np.exp(x, out=x)
    x /= x.sum(-1, keepdims=True)
    return x


# ---------------------------------------------------------------------------------------------
# Netze
# ---------------------------------------------------------------------------------------------
class RRDBNet:
    """ESRGAN-Generator (Real-ESRGAN x4plus/x2plus/anime_6B)."""
    def __init__(self, w, faktor, bloecke):
        self.w, self.faktor, self.bloecke = w, faktor, bloecke
        self._wm = {}                                           # vorbereitete Gewichte je Faltung (gewichte_matrix)

    def _matrix(self, name):
        if name not in self._wm:
            self._wm[name] = gewichte_matrix(self.w[name + ".weight"])
        return self._wm[name]

    def _c(self, name, x):
        return conv(x, self.w[name + ".weight"], self.w[name + ".bias"], self._matrix(name))

    def _rdb(self, x, n):
        # dichte Verbindungen: Eingang und Zwischenergebnisse liegen nebeneinander in einem gepolsterten Puffer;
        # Faltung i liest dessen erste c Kanäle (= Faltung über die Verkettung)
        h, wd, c = x.shape
        breit, wachs = wd + 2, self.w[f"{n}.conv1.weight"].shape[0]
        puffer = np.zeros((h + 3, breit, c + 4 * wachs), np.float32)
        puffer[1:h + 1, 1:wd + 1, :c] = x
        flach = puffer.reshape(-1, puffer.shape[2])
        for i in range(1, 6):
            y = falte_flach(flach, h, breit, self._matrix(f"{n}.conv{i}"), 3, c, self.w[f"{n}.conv{i}.bias"])
            if i < 5:
                puffer[1:h + 1, 1:wd + 1, c:c + wachs] = lrelu(y)
                c += wachs
        return y * np.float32(0.2) + x

    def __call__(self, x):
        if self.faktor == 2:
            x = pixel_unshuffle(x, 2)
        elif self.faktor == 1:
            x = pixel_unshuffle(x, 4)
        f = self._c("conv_first", x)
        k = f
        for b in range(self.bloecke):
            r = k
            for j in (1, 2, 3):
                r = self._rdb(r, f"body.{b}.rdb{j}")
            k = r * np.float32(0.2) + k
        f = f + self._c("conv_body", k)
        f = lrelu(self._c("conv_up1", hoch2(f)))
        f = lrelu(self._c("conv_up2", hoch2(f)))
        return self._c("conv_last", lrelu(self._c("conv_hr", f)))


class SRVGGNetCompact:
    """Kompaktes VGG-Netz (realesr-general-x4v3): 32 Faltungen mit PReLU, dann Pixel-Shuffle."""
    def __init__(self, w, faktor=4):
        self.w, self.faktor = w, faktor
        self.n = max(int(k.split(".")[1]) for k in w if k.startswith("body.")) + 1

    def __call__(self, x):
        y = x
        i = 0
        while i < self.n:
            y = conv(y, self.w[f"body.{i}.weight"], self.w[f"body.{i}.bias"])
            if i + 1 < self.n and f"body.{i + 1}.weight" in self.w and self.w[f"body.{i + 1}.weight"].ndim == 1:
                a = self.w[f"body.{i + 1}.weight"]
                y = np.where(y >= 0, y, y * a)
                i += 2
            else:
                i += 1
        y = pixel_shuffle(y, self.faktor)
        return y + x.repeat(self.faktor, 0).repeat(self.faktor, 1)


class SwinIR:
    """SwinIR (Real-World-SR, 'nearest+conv'-Hochskalierung, 3conv-Restverbindung)."""
    MITTEL = np.array([0.4488, 0.4371, 0.4040], np.float32)

    def __init__(self, w, faktor=4, fenster=8):
        self.w, self.faktor, self.fs = w, faktor, fenster
        self.schichten = sorted({int(k.split(".")[1]) for k in w if k.startswith("layers.")})
        self.bloecke = {s: sorted({int(k.split(".")[4]) for k in w
                                   if k.startswith(f"layers.{s}.residual_group.blocks.")})
                        for s in self.schichten}
        tab = w["layers.0.residual_group.blocks.0.attn.relative_position_bias_table"]
        self.koepfe = tab.shape[1]
        fs = fenster
        ko = np.stack(np.meshgrid(np.arange(fs), np.arange(fs), indexing="ij")).reshape(2, -1)
        rel = (ko[:, :, None] - ko[:, None, :]).transpose(1, 2, 0) + (fs - 1)
        self.rel_index = (rel[..., 0] * (2 * fs - 1) + rel[..., 1]).reshape(-1)
        self._bias = {}
        self._masken = {}

    def _rel_bias(self, praefix):
        if praefix not in self._bias:
            n = self.fs * self.fs
            tab = self.w[praefix + ".attn.relative_position_bias_table"]
            self._bias[praefix] = tab[self.rel_index].reshape(n, n, -1).transpose(2, 0, 1).copy()
        return self._bias[praefix]

    def _maske(self, h, w):
        if (h, w) not in self._masken:
            fs, s = self.fs, self.fs // 2
            m = np.zeros((h, w), np.float32)
            cnt = 0
            for hs in (slice(0, -fs), slice(-fs, -s), slice(-s, None)):
                for ws in (slice(0, -fs), slice(-fs, -s), slice(-s, None)):
                    m[hs, ws] = cnt
                    cnt += 1
            mw = self._fenster(m[:, :, None]).reshape(-1, fs * fs)
            d = mw[:, None, :] - mw[:, :, None]
            self._masken[(h, w)] = np.where(d != 0, np.float32(-100.0), np.float32(0.0))
        return self._masken[(h, w)]

    def _fenster(self, x):
        h, w, c = x.shape
        fs = self.fs
        return x.reshape(h // fs, fs, w // fs, fs, c).transpose(0, 2, 1, 3, 4).reshape(-1, fs * fs, c)

    def _zurueck(self, x, h, w):
        fs = self.fs
        c = x.shape[-1]
        return x.reshape(h // fs, w // fs, fs, fs, c).transpose(0, 2, 1, 3, 4).reshape(h, w, c)

    def _lin(self, name, x):
        return x @ self.w[name + ".weight"].T + self.w[name + ".bias"]

    def _block(self, x, h, w, p, verschoben):
        c = x.shape[-1]
        nh = self.koepfe
        hd = c // nh
        s = self.fs // 2
        y = layer_norm(x, self.w[p + ".norm1.weight"], self.w[p + ".norm1.bias"]).reshape(h, w, c)
        if verschoben:
            y = np.roll(y, (-s, -s), axis=(0, 1))
        fen = self._fenster(y)                                      # nW, N, C
        nw, n, _ = fen.shape
        qkv = self._lin(p + ".attn.qkv", fen).reshape(nw, n, 3, nh, hd).transpose(2, 0, 3, 1, 4)
        q, k, v = qkv[0] * np.float32(hd ** -0.5), qkv[1], qkv[2]
        att = q @ k.transpose(0, 1, 3, 2) + self._rel_bias(p)       # nW, nh, N, N
        if verschoben:
            att += self._maske(h, w)[:, None]
        att = softmax(att)
        o = (att @ v).transpose(0, 2, 1, 3).reshape(nw, n, c)
        o = self._lin(p + ".attn.proj", o)
        o = self._zurueck(o, h, w)
        if verschoben:
            o = np.roll(o, (s, s), axis=(0, 1))
        x = x + o.reshape(h * w, c)
        z = layer_norm(x, self.w[p + ".norm2.weight"], self.w[p + ".norm2.bias"])
        z = self._lin(p + ".mlp.fc2", gelu(self._lin(p + ".mlp.fc1", z)))
        return x + z

    def _c(self, name, x):
        return conv(x, self.w[name + ".weight"], self.w[name + ".bias"])

    def _rest(self, name, x):
        """Restverbindung: eine Faltung ('1conv') oder drei Faltungen ('3conv')."""
        if name + ".weight" in self.w:
            return self._c(name, x)
        x = lrelu(self._c(name + ".0", x))
        x = lrelu(self._c(name + ".2", x))
        return self._c(name + ".4", x)

    def __call__(self, x):
        h0, w0 = x.shape[:2]
        fs = self.fs
        ph, pw = (-h0) % fs, (-w0) % fs
        if ph or pw:
            x = np.pad(x, ((0, ph), (0, pw), (0, 0)), mode="reflect")
        h, w = x.shape[:2]
        x = x - self.MITTEL
        f = self._c("conv_first", x)
        c = f.shape[-1]
        t = layer_norm(f.reshape(-1, c), self.w["patch_embed.norm.weight"], self.w["patch_embed.norm.bias"])
        for s in self.schichten:
            rest = t
            for b in self.bloecke[s]:
                t = self._block(t, h, w, f"layers.{s}.residual_group.blocks.{b}", verschoben=(b % 2 == 1))
            t = self._rest(f"layers.{s}.conv", t.reshape(h, w, c)).reshape(-1, c) + rest
        t = layer_norm(t, self.w["norm.weight"], self.w["norm.bias"]).reshape(h, w, c)
        f = self._rest("conv_after_body", t) + f
        f = lrelu(self._c("conv_before_upsample.0", f), 0.01)
        f = lrelu(self._c("conv_up1", hoch2(f)))
        if self.faktor == 4:
            f = lrelu(self._c("conv_up2", hoch2(f)))
        y = self._c("conv_last", lrelu(self._c("conv_hr", f))) + self.MITTEL
        return y[: h0 * self.faktor, : w0 * self.faktor]


def baue_netz(modell_id, gewichte):
    m = KATALOG[modell_id]
    if m["netz"] == "rrdb":
        return RRDBNet(gewichte, m["faktor"], m["bloecke"])
    if m["netz"] == "srvgg":
        return SRVGGNetCompact(gewichte, m["faktor"])
    if m["netz"] == "swinir":
        return SwinIR(gewichte, m["faktor"])
    raise ValueError(modell_id)


# ---------------------------------------------------------------------------------------------
# Kachelweise Anwendung
# ---------------------------------------------------------------------------------------------
def kachelweise(netz, bild, faktor, kachel=128, rand=16, fortschritt=None):
    """bild: H×W×3 float32 in 0..1. Rechnet in überlappenden Kacheln, gibt (H·f)×(W·f)×3 zurück."""
    h, w = bild.shape[:2]
    pad_mod = 8 if isinstance(netz, SwinIR) else (2 if faktor == 2 else 1)
    aus = np.zeros((h * faktor, w * faktor, 3), np.float32)
    ys = list(range(0, h, kachel))
    xs = list(range(0, w, kachel))
    gesamt, fertig = len(ys) * len(xs), 0
    for y0 in ys:
        for x0 in xs:
            y1, x1 = min(y0 + kachel, h), min(x0 + kachel, w)
            a0, b0 = max(y0 - rand, 0), max(x0 - rand, 0)
            a1, b1 = min(y1 + rand, h), min(x1 + rand, w)
            stueck = bild[a0:a1, b0:b1]
            ph, pw = (-stueck.shape[0]) % pad_mod, (-stueck.shape[1]) % pad_mod
            if ph or pw:
                stueck = np.pad(stueck, ((0, ph), (0, pw), (0, 0)), mode="reflect")
            erg = netz(np.ascontiguousarray(stueck))
            oy, ox = (y0 - a0) * faktor, (x0 - b0) * faktor
            aus[y0 * faktor:y1 * faktor, x0 * faktor:x1 * faktor] = \
                erg[oy:oy + (y1 - y0) * faktor, ox:ox + (x1 - x0) * faktor]
            fertig += 1
            if fortschritt:
                fortschritt(fertig, gesamt)
    return np.clip(aus, 0.0, 1.0)


# ---------------------------------------------------------------------------------------------
# Modelle verwalten: Pfade, Herunterladen (mit Prüfsumme), Umwandeln
# ---------------------------------------------------------------------------------------------
HIER = Path(__file__).resolve().parent
MODELL_ORDNER = HIER / "modelle"


def _t(de, en, es):
    import os
    s = (os.environ.get("MGD_SPRACHE") or "en")[:2].lower()
    return {"en": en, "es": es}.get(s, de)


def npz_pfad(modell_id, ordner=None):
    return Path(ordner or MODELL_ORDNER) / f"{modell_id}.npz"


def verfuegbar(modell_id, ordner=None):
    return npz_pfad(modell_id, ordner).is_file()


def ssl_kontexte():
    """Zertifikatsprüfung bleibt immer an. Reihenfolge: Standard des Systems → Zertifikatsspeicher des Betriebssystems
    über truststore (aus pip; hilft am Mac und hinter Firmen-Proxys) → Zertifikatsliste von certifi (aus pip)."""
    import ssl
    kontexte = [ssl.create_default_context()]
    try:
        from pip._vendor import truststore
        kontexte.append(truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT))
    except Exception:  # noqa: BLE001
        pass
    try:
        from pip._vendor import certifi
        kontexte.append(ssl.create_default_context(cafile=certifi.where()))
    except Exception:  # noqa: BLE001
        pass
    return kontexte


def im_browser():
    import sys
    return sys.platform == "emscripten"


class _WebAntwort(io.BytesIO):
    """Antwort eines Browser-Downloads mit dem, was lade() und sprachen._hole() von urlopen nutzen."""

    def __init__(self, daten):
        super().__init__(daten)
        self.status, self.headers = 200, {"Content-Length": str(len(daten))}


def web_oeffnen(anfrage, timeout=60):
    """Web-App (Pyodide im Web-Worker): Datei per synchronem XMLHttpRequest holen – nur Adressen mit CORS bzw. der
    eigene Ordner der App. Kopfzeilen (User-Agent, Range) setzt der Browser selbst → immer die ganze Datei."""
    import js                                                    # nur in Pyodide vorhanden
    url = getattr(anfrage, "full_url", anfrage)
    x = js.XMLHttpRequest.new()
    x.open("GET", url, False)
    x.responseType = "arraybuffer"                               # im Worker auch synchron erlaubt
    try:
        x.timeout = max(timeout, 900) * 1000
    except Exception:  # noqa: BLE001
        pass
    try:
        x.send()
    except Exception:  # noqa: BLE001 – Netz weg, CORS verweigert, Zeitlimit
        raise OSError(_t(f"Keine Verbindung zu {url} – bitte mit Internet nochmal versuchen.",
                         f"No connection to {url} – please try again with internet.",
                         f"Sin conexión con {url}; inténtalo de nuevo con internet.")) from None
    if x.status not in (200, 206):
        raise OSError(f"HTTP {x.status}: {url}")
    return _WebAntwort(x.response.to_bytes())


def _web_lade_npz(modell_id, ordner, melde):
    """Web-App: GitHub erlaubt Downloads aus dem Browser nicht (kein CORS) – die App bringt die fertige .npz im eigenen
    Ordner modelle/ mit (Größe + SHA-256 in modelle/modelle.json, von bau_webapp.py geschrieben)."""
    import json
    import os
    ziel = npz_pfad(modell_id, ordner)
    try:
        liste = json.loads(web_oeffnen("modelle/modelle.json").read().decode("utf-8"))
    except (OSError, ValueError):
        liste = {}
    m = liste.get(ziel.name) if isinstance(liste, dict) else None
    if not m:
        raise ValueError(_t(f"{KATALOG[modell_id]['titel']} gibt es nur in der Fassung am Rechner.",
                            f"{KATALOG[modell_id]['titel']} is only available in the computer version.",
                            f"{KATALOG[modell_id]['titel']} solo está en la versión de la computadora."))
    melde(_t(f"Lade {KATALOG[modell_id]['titel']} ({m['groesse'] // (1024 * 1024)} MB) …",
             f"Downloading {KATALOG[modell_id]['titel']} ({m['groesse'] // (1024 * 1024)} MB) …",
             f"Descargando {KATALOG[modell_id]['titel']} ({m['groesse'] // (1024 * 1024)} MB) …"))
    daten = web_oeffnen("modelle/" + ziel.name).read()
    if len(daten) != m["groesse"] or hashlib.sha256(daten).hexdigest() != m["sha256"]:
        raise ValueError(_t("Prüfsumme stimmt nicht – Datei beschädigt oder verändert. Nichts installiert.",
                            "Checksum mismatch – file damaged or altered. Nothing installed.",
                            "La suma de verificación no coincide: archivo dañado o alterado. No se instaló nada."))
    ziel.parent.mkdir(parents=True, exist_ok=True)
    tmp = ziel.with_name(ziel.name + ".tmp")
    tmp.write_bytes(daten)
    os.replace(tmp, ziel)
    melde(_t(f"Fertig: {ziel.name} ({len(daten) // (1024 * 1024)} MB)", f"Done: {ziel.name} ({len(daten) // (1024 * 1024)} MB)",
             f"Listo: {ziel.name} ({len(daten) // (1024 * 1024)} MB)"))
    return ziel


def oeffne_url(anfrage, timeout=60):
    if im_browser():
        return web_oeffnen(anfrage, timeout)
    import ssl
    import urllib.error
    import urllib.request
    kontexte = ssl_kontexte()
    for i, kontext in enumerate(kontexte):
        try:
            return urllib.request.urlopen(anfrage, timeout=timeout, context=kontext)
        except urllib.error.URLError as e:
            zertifikat = isinstance(getattr(e, "reason", None), ssl.SSLCertVerificationError)
            if not zertifikat or i == len(kontexte) - 1:
                raise
    raise RuntimeError("unreachable")


def lade(modell_id, ziel_ordner=None, melde=print, quelle=None):
    """Lädt die Original-Gewichte von GitHub (oder nimmt eine lokale .pth), prüft die SHA-256-Prüfsumme und
    legt eine pickle-freie .npz in modelle/ ab. Gibt den Pfad der .npz zurück."""
    import os
    import tempfile
    import urllib.request

    m = KATALOG[modell_id]
    ordner = Path(ziel_ordner or MODELL_ORDNER)
    ordner.mkdir(parents=True, exist_ok=True)
    if not quelle and im_browser():
        return _web_lade_npz(modell_id, ordner, melde)
    with tempfile.TemporaryDirectory(dir=ordner) as tmp:
        pth = Path(tmp) / m["datei"]
        if quelle:
            pth.write_bytes(Path(quelle).read_bytes())
        else:
            melde(_t(f"Lade {m['titel']} von GitHub …", f"Downloading {m['titel']} from GitHub …",
                     f"Descargando {m['titel']} desde GitHub …"))
            anfrage = urllib.request.Request(m["url"], headers={"User-Agent": "Me-Goos-ta-Deutsch"})
            with oeffne_url(anfrage) as r, open(pth, "wb") as f:
                gesamt = int(r.headers.get("Content-Length") or 0)
                if gesamt > 400 * 1024 * 1024:
                    raise ValueError("Datei unerwartet groß")
                geladen, schritt = 0, 0
                while True:
                    block = r.read(1 << 20)
                    if not block:
                        break
                    f.write(block)
                    geladen += len(block)
                    if geladen > 400 * 1024 * 1024:
                        raise ValueError("Datei unerwartet groß")
                    if gesamt and geladen * 10 // gesamt > schritt:
                        schritt = geladen * 10 // gesamt
                        melde(f"  {schritt * 10} %  ({geladen // (1024 * 1024)} / {gesamt // (1024 * 1024)} MB)")
        pruef = sha256(pth)
        if pruef != m["sha256"]:
            raise ValueError(_t("Prüfsumme stimmt nicht – Datei beschädigt oder verändert. Nichts installiert.",
                                "Checksum mismatch – file damaged or altered. Nothing installed.",
                                "La suma de verificación no coincide: archivo dañado o alterado. No se instaló nada."))
        melde(_t("Prüfsumme in Ordnung. Wandle in NumPy-Format um …", "Checksum OK. Converting to NumPy format …",
                 "Suma de verificación correcta. Convirtiendo al formato NumPy …"))
        ziel = npz_pfad(modell_id, ordner)
        pth_zu_npz(pth, ziel)
        os.chmod(ziel, 0o644)
    melde(_t(f"Fertig: {ziel.name} ({ziel.stat().st_size // (1024 * 1024)} MB)",
             f"Done: {ziel.name} ({ziel.stat().st_size // (1024 * 1024)} MB)",
             f"Listo: {ziel.name} ({ziel.stat().st_size // (1024 * 1024)} MB)"))
    return ziel


class Hochskalierer:
    """Hält ein geladenes Netz im Speicher und vergrößert Bilder damit (RGB, PIL)."""
    _netze: dict = {}

    def __init__(self, modell_id, ordner=None):
        self.id = modell_id
        self.faktor = KATALOG[modell_id]["faktor"]
        if modell_id not in self._netze:
            self._netze[modell_id] = baue_netz(modell_id, lade_npz(npz_pfad(modell_id, ordner)))
        self.netz = self._netze[modell_id]

    def __call__(self, bild, fortschritt=None, kachel=128):
        from PIL import Image
        x = np.asarray(bild.convert("RGB"), np.float32) / 255.0
        y = kachelweise(self.netz, x, self.faktor, kachel=kachel, fortschritt=fortschritt)
        return Image.fromarray((y * 255.0 + 0.5).astype(np.uint8))


def main(argv=None):
    import argparse
    import sys
    ap = argparse.ArgumentParser(description="KI-Modelle für Me Goos-ta Deutsch herunterladen und prüfen")
    ap.add_argument("--laden", choices=list(KATALOG), help="Modell von GitHub laden (mit Prüfsumme)")
    ap.add_argument("--aus-datei", metavar="PTH", help="statt Download eine vorhandene .pth-Datei umwandeln")
    ap.add_argument("--liste", action="store_true", help="Modelle und ihren Status anzeigen")
    ap.add_argument("--vorrat", metavar="ORDNER", help="zusätzlich eine Kopie dort ablegen (Datenordner: eine neue "
                                                      "Programmversion übernimmt das Modell ohne Download)")
    a = ap.parse_args(argv)
    for strom in (sys.stdout, sys.stderr):
        try:
            strom.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    if a.laden:
        try:
            ziel = lade(a.laden, quelle=a.aus_datei, melde=lambda t: print(t, flush=True))
            if a.vorrat and not im_browser():                  # Web-App: keine zweite Kopie (spart Platz am Handy)
                import os
                import shutil
                kopie = Path(a.vorrat) / ziel.name
                try:
                    kopie.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ziel, kopie.with_name(kopie.name + ".tmp"))
                    os.replace(kopie.with_name(kopie.name + ".tmp"), kopie)
                except OSError as e:                     # nur die Kopie fehlt – das Modell selbst ist da
                    print(f"({e})", flush=True)
        except Exception as e:  # noqa: BLE001
            print(_t("FEHLER: ", "ERROR: ", "ERROR: ") + str(e), flush=True)
            return 1
        return 0
    for mid, m in KATALOG.items():
        print(f"{'✓' if verfuegbar(mid) else '·'} {mid:22} {m['titel']:34} {m['lizenz']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
