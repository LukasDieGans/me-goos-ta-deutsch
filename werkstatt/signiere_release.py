#!/usr/bin/env python3
"""Signiert die SHA256SUMS.txt eines Releases von Me Goos-ta Deutsch (seit 2.5, minisign-kompatibel, Ed25519).
Aufruf (nur Standardbibliothek, privater Schlüssel per Windows-DPAPI – nie im Arbeitsordner, Repo, ZIP oder Chat):
    python signiere_release.py --neu                                   Haupt- und Reserve-Schlüssel anlegen (einmal)
    python signiere_release.py --status                                welche Schlüssel liegen hier (nur IDs)
    python signiere_release.py --signiere <SHA256SUMS.txt> --version <V> [--mit-reserve <reserve.key>]
                                                                       → <SHA256SUMS.txt>.minisig
    python signiere_release.py --pruefe <SHA256SUMS.txt> --version <V> [--minisig <Datei>]
    python signiere_release.py --sicherung <Ordner>                    nur Lukas im Terminal: Passwort wählen, beide
                                                                       Schlüssel minisign-verschlüsselt (scrypt) in den
                                                                       Ordner (USB-Stick), danach Reserve vom Rechner weg
    --ordner <Ordner>   Schlüsselordner (Standard %USERPROFILE%\\MGD-Signatur; Tests: eigener Ordner)

Schlüssel: haupt.dpapi / reserve.dpapi (privat, nur für dieses Windows-Konto entschlüsselbar) + haupt.pub / reserve.pub.
Die öffentlichen Schlüssel stehen in Programm/signatur.py (SCHLUESSEL) – nur dorthin, nie die privaten.
Haupt verloren → --mit-reserve <reserve.key> (Passwort der Sicherung) signieren und mit dem nächsten Update einen neuen
Haupt-Schlüssel ausliefern. „trusted comment“ = „me-goos-ta-deutsch v<V>“ (das Programm verlangt genau diese Version)."""
import base64
import ctypes
import getpass
import hashlib
import os
import re
import secrets
import sys
from pathlib import Path

ARBEIT = Path(__file__).resolve().parent.parent                 # Wurzel des Quellbaums (Skript in werkstatt/)
sys.path.insert(0, str(ARBEIT / "Me-Goos-ta-Deutsch" / "Programm"))
import signatur  # noqa: E402

# Nicht unter %APPDATA%: aus der Claude-Desktop-App (MSIX-Paket) leitet Windows Schreibzugriffe dorthin in den Paketordner
# um – eine normale PowerShell sähe die Schlüssel nicht, und mit der App wären sie weg (Fund 23.10.2026).
STANDARD_ORDNER = Path.home() / "MGD-Signatur"
NAMEN = ("haupt", "reserve")
MARKE = b"MGD-SIG1"
ENTROPIE = b"me-goos-ta-deutsch release signing"
# minisign-Standard für verschlüsselte Schlüssel (OPSLIMIT/MEMLIMIT_SENSITIVE → scrypt N=2^20, r=8, p=1; ~1 GB kurz)
OPS, MEM = 33554432, 1073741824


def abbruch(text):
    sys.exit(f"✗ {text}")


# ---------- DPAPI (Windows): privat nur für dieses Benutzerkonto ----------
class _Blob(ctypes.Structure):
    _fields_ = [("cbData", ctypes.c_uint32), ("pbData", ctypes.POINTER(ctypes.c_char))]


def _dpapi(daten, schuetzen):
    if os.name != "nt":
        abbruch("Schlüssel liegen per Windows-DPAPI – bitte unter Windows signieren.")
    from ctypes import wintypes
    crypt32, kernel32 = ctypes.windll.crypt32, ctypes.windll.kernel32
    fn = crypt32.CryptProtectData if schuetzen else crypt32.CryptUnprotectData
    fn.argtypes = [ctypes.POINTER(_Blob), ctypes.c_void_p, ctypes.POINTER(_Blob), ctypes.c_void_p, ctypes.c_void_p,
                   wintypes.DWORD, ctypes.POINTER(_Blob)]
    fn.restype = wintypes.BOOL
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    ein_p = ctypes.create_string_buffer(bytes(daten), len(daten))
    ent_p = ctypes.create_string_buffer(ENTROPIE, len(ENTROPIE))
    ein = _Blob(len(daten), ctypes.cast(ein_p, ctypes.POINTER(ctypes.c_char)))
    ent = _Blob(len(ENTROPIE), ctypes.cast(ent_p, ctypes.POINTER(ctypes.c_char)))
    aus = _Blob()
    if not fn(ctypes.byref(ein), None, ctypes.byref(ent), None, None, 0x1, ctypes.byref(aus)):   # UI_FORBIDDEN
        abbruch(f"DPAPI {'Schützen' if schuetzen else 'Entschlüsseln'} fehlgeschlagen (Fehler {ctypes.GetLastError()}).")
    try:
        return ctypes.string_at(aus.pbData, aus.cbData)
    finally:
        kernel32.LocalFree(ctypes.cast(aus.pbData, ctypes.c_void_p))


# ---------- Schlüsselordner ----------
def ordner_pruefen(ordner):
    o = Path(ordner).resolve()
    if o == ARBEIT or ARBEIT in o.parents or (o / ".git").exists():
        abbruch(f"Schlüssel nie in den Arbeitsordner oder ein Repository legen: {o}")
    return o


def schluessel_da(ordner):
    return {n: (ordner / f"{n}.dpapi").is_file() for n in NAMEN}


def oeffentlich(ordner, name):
    """(ID, öffentlicher Schlüssel) aus <name>.pub oder None."""
    p = ordner / f"{name}.pub"
    try:
        return signatur.schluessel_lesen(p.read_text(encoding="utf-8"))
    except (OSError, signatur.SignaturFehler):
        return None


def privat(ordner, name):
    """(ID, Seed) aus <name>.dpapi – prüft, dass er zur .pub passt."""
    roh = _dpapi((ordner / f"{name}.dpapi").read_bytes(), False)
    if len(roh) != len(MARKE) + 40 or not roh.startswith(MARKE):
        abbruch(f"{name}.dpapi hat ein unerwartetes Format.")
    sid, seed = roh[len(MARKE):len(MARKE) + 8], roh[len(MARKE) + 8:]
    pub = oeffentlich(ordner, name)
    if pub != (sid, signatur.ed25519_oeffentlich(seed)):
        abbruch(f"{name}.dpapi passt nicht zu {name}.pub.")
    return sid, seed


def neu(ordner):
    ordner.mkdir(parents=True, exist_ok=True)
    if any(schluessel_da(ordner).values()):
        abbruch(f"In {ordner} liegen schon Schlüssel – nie überschreiben (--status zeigt sie).")
    zeilen = []
    for n in NAMEN:
        seed, sid = secrets.token_bytes(32), secrets.token_bytes(8)
        oeff = signatur.ed25519_oeffentlich(seed)
        (ordner / f"{n}.dpapi").write_bytes(_dpapi(MARKE + sid + seed, True))
        (ordner / f"{n}.pub").write_text(signatur.pub_datei(sid, oeff), encoding="utf-8")
        if privat(ordner, n)[1] != seed:
            abbruch("DPAPI-Gegenprobe fehlgeschlagen.")
        zeilen.append(f'    ("{n}", "{signatur.schluessel_text(sid, oeff)}"),')
        print(f"✓ {n}: Schlüssel-ID {signatur.schluessel_id(sid)} ({ordner / (n + '.pub')})")
    print("Für Programm/signatur.py (nur öffentliche Schlüssel):\nSCHLUESSEL = (\n" + "\n".join(zeilen) + "\n)")


def status(ordner):
    vertraut = {signatur.schluessel_id(sid): name for name, sid, _ in signatur.vertraut()}
    print(f"Schlüsselordner {ordner}")
    for n in NAMEN:
        pub = oeffentlich(ordner, n)
        sid = signatur.schluessel_id(pub[0]) if pub else "–"
        print(f"  {n:8} privat {'ja' if (ordner / (n + '.dpapi')).is_file() else 'nein':4} · ID {sid}"
              f" · in signatur.py: {vertraut.get(sid, 'nein')}")


# ---------- Signieren / Prüfen ----------
def kommentar(version):
    if not re.fullmatch(r"\d{1,4}\.\d{1,4}(\.\d{1,4})?", str(version or "")):
        abbruch(f"Ungültige Version: {version!r}")
    return signatur.KOMMENTAR.format(version=version)


def signieren(summen, version, ordner=STANDARD_ORDNER, reserve_datei=None, passwort=None):
    """SHA256SUMS-Bytes → (minisig-Bytes, Schlüssel-ID). Mit reserve_datei: Reserve aus der Sicherung (Passwort)."""
    if reserve_datei:
        sid, seed = schluessel_entschluesseln(Path(reserve_datei).read_text(encoding="utf-8"),
                                              passwort if passwort is not None else getpass.getpass("Passwort der Sicherung: "))
    else:
        ordner = ordner_pruefen(ordner)
        if not (ordner / "haupt.dpapi").is_file():
            abbruch(f"Kein Haupt-Schlüssel in {ordner} – einmal „python signiere_release.py --neu“ (oder --mit-reserve).")
        sid, seed = privat(ordner, "haupt")
    ms = signatur.signiere(seed, sid, summen, kommentar(version))
    signatur.pruefe(summen, ms, [("eigen", sid, signatur.ed25519_oeffentlich(seed))], kommentar(version))
    return ms, signatur.schluessel_id(sid)


def pruefen(summen, ms, version, ordner=None):
    """Gegen die Schlüssel in signatur.py (und mit ordner zusätzlich dessen .pub) → dict; sonst SignaturFehler."""
    schluessel = list(signatur.vertraut())
    if ordner:
        schluessel += [(f"{n} ({ordner})", *p) for n in NAMEN if (p := oeffentlich(Path(ordner), n))]
    return signatur.pruefe(summen, ms, schluessel, kommentar(version))


# ---------- Sicherung: minisign-verschlüsselte Schlüsseldatei (scrypt + XOR, Prüfsumme BLAKE2b-256) ----------
def _scrypt_werte(ops, mem):
    """libsodium pickparams (crypto_pwhash_scryptsalsa208sha256) → (N, r, p) – wie minisign."""
    ops = max(ops, 32768)
    r = 8
    if ops < mem // 32:
        p, max_n = 1, ops // (r * 4)
    else:
        max_n = mem // (r * 128)
    n_log2 = 1
    while n_log2 < 63 and (1 << n_log2) <= max_n // 2:
        n_log2 += 1
    if not ops < mem // 32:
        p = min((ops // 4) // (1 << n_log2), 0x3fffffff) // r
    return 1 << n_log2, r, max(p, 1)


def _strom(passwort, salz, ops, mem):
    n, r, p = _scrypt_werte(ops, mem)
    return hashlib.scrypt(passwort.encode("utf-8"), salt=salz, n=n, r=r, p=p, maxmem=2 ** 31 - 1, dklen=104)


def schluessel_verschluesseln(sid, seed, passwort, ops=OPS, mem=MEM):
    """→ Inhalt einer minisign-Datei „encrypted secret key“ (lässt sich mit minisign -s … benutzen)."""
    sk = seed + signatur.ed25519_oeffentlich(seed)
    chk = hashlib.blake2b(b"Ed" + sid + sk, digest_size=32).digest()
    salz = secrets.token_bytes(32)
    klar = sid + sk + chk
    geheim = bytes(a ^ b for a, b in zip(klar, _strom(passwort, salz, ops, mem)))
    roh = b"Ed" + b"Sc" + b"B2" + salz + ops.to_bytes(8, "little") + mem.to_bytes(8, "little") + geheim
    return f"untrusted comment: minisign encrypted secret key\n{base64.b64encode(roh).decode('ascii')}\n"


def schluessel_entschluesseln(text, passwort):
    zeilen = [z.strip() for z in text.strip().splitlines() if z.strip()]
    try:
        roh = base64.b64decode(zeilen[-1], validate=True)
    except (ValueError, IndexError):
        abbruch("Schlüsseldatei unlesbar.")
    if len(roh) != 158 or roh[:2] != b"Ed" or roh[4:6] != b"B2" or roh[2:4] not in (b"Sc", b"\0\0"):
        abbruch("Keine minisign-Schlüsseldatei (Ed25519).")
    salz, ops, mem = roh[6:38], int.from_bytes(roh[38:46], "little"), int.from_bytes(roh[46:54], "little")
    teil = roh[54:]
    if roh[2:4] == b"Sc":
        teil = bytes(a ^ b for a, b in zip(teil, _strom(passwort, salz, ops, mem)))
    sid, sk, chk = teil[:8], teil[8:72], teil[72:]
    if hashlib.blake2b(b"Ed" + sid + sk, digest_size=32).digest() != chk:
        abbruch("Falsches Passwort oder beschädigte Schlüsseldatei.")
    if signatur.ed25519_oeffentlich(sk[:32]) != sk[32:]:
        abbruch("Schlüsseldatei beschädigt.")
    return sid, sk[:32]


def sicherung(ordner, ziel, passwort, ops=OPS, mem=MEM):
    """Beide Schlüssel verschlüsselt nach ziel (+ .pub), Gegenprobe, danach reserve.dpapi vom Rechner entfernen."""
    ordner, ziel = ordner_pruefen(ordner), Path(ziel)
    if not all(schluessel_da(ordner).values()):
        abbruch("Für die Sicherung müssen Haupt- und Reserve-Schlüssel hier liegen (Reserve schon gesichert?).")
    if len(passwort) < 12:
        abbruch("Bitte ein Passwort mit mindestens 12 Zeichen.")
    ziel.mkdir(parents=True, exist_ok=True)
    for n in NAMEN:
        sid, seed = privat(ordner, n)
        datei = ziel / f"me-goos-ta-deutsch-{n}.key"
        datei.write_text(schluessel_verschluesseln(sid, seed, passwort, ops, mem), encoding="utf-8")
        (ziel / f"me-goos-ta-deutsch-{n}.pub").write_text(signatur.pub_datei(sid, signatur.ed25519_oeffentlich(seed)),
                                                       encoding="utf-8")
        if schluessel_entschluesseln(datei.read_text(encoding="utf-8"), passwort) != (sid, seed):
            abbruch(f"Gegenprobe der Sicherung {datei.name} fehlgeschlagen – nichts entfernt.")
        print(f"✓ {datei}")
    (ordner / "reserve.dpapi").unlink()
    print("✓ Reserve-Schlüssel vom Rechner entfernt (öffentlicher Teil bleibt). Die zwei .key-Dateien gehören auf einen "
          "USB-Stick an einen sicheren Ort – Passwort nie in einen Chat schreiben.")


def main(argv):
    def wert(n):
        return argv[argv.index(n) + 1] if n in argv and argv.index(n) + 1 < len(argv) else None
    ordner = Path(wert("--ordner") or STANDARD_ORDNER)
    if "--neu" in argv:
        neu(ordner_pruefen(ordner))
    elif "--status" in argv:
        status(ordner_pruefen(ordner))
    elif wert("--signiere"):
        summen_pfad = Path(wert("--signiere"))
        ms, sid = signieren(summen_pfad.read_bytes(), wert("--version"), ordner, wert("--mit-reserve"))
        Path(str(summen_pfad) + ".minisig").write_bytes(ms)
        print(f"✓ {summen_pfad}.minisig (Schlüssel {sid}, „{kommentar(wert('--version'))}“)")
    elif wert("--pruefe"):
        summen_pfad = Path(wert("--pruefe"))
        ms_pfad = Path(wert("--minisig") or str(summen_pfad) + ".minisig")
        try:
            r = pruefen(summen_pfad.read_bytes(), ms_pfad.read_bytes(), wert("--version"),
                        ordner if wert("--ordner") else None)
        except (OSError, signatur.SignaturFehler) as f:
            abbruch(f"Signatur nicht gültig: {f}")
        print(f"✓ gültig: Schlüssel {r['id']} ({r['name']}), „{r['kommentar']}“")
    elif wert("--sicherung"):
        p1 = getpass.getpass("Neues Passwort für die Sicherung (mind. 12 Zeichen): ")
        if getpass.getpass("Noch einmal: ") != p1:
            abbruch("Die Passwörter sind verschieden – nichts geändert.")
        sicherung(ordner, wert("--sicherung"), p1)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
