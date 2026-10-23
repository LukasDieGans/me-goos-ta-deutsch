#!/usr/bin/env python3
"""Baut den Release-Ordner (und mit --zip die ZIP-Datei) von Me Goos-ta Deutsch.
Aufruf: python bau_release.py <Quelle: Ordner Me-Goos-ta-Deutsch> <Ziel-Ordner> [--zip]

Nur ausdrücklich freigegebene Dateien kommen hinein (Positivliste): eigene Karten, Bilder, Ideen, Ausgaben,
Zwischenspeicher, Sicherungen und Einstellungen bleiben draußen. Unbekannte Dateien werden gemeldet, nicht kopiert."""
import shutil
import sys
import zipfile
from pathlib import Path

QUELLE, ZIEL = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
NAME = QUELLE.name                                             # „Me-Goos-ta-Deutsch“
OBEN = ("Me Goos-ta Deutsch - Windows.cmd", "Me Goos-ta Deutsch - Mac.command", "Me Goos-ta Deutsch - Linux.sh",
        "LIES MICH ZUERST.html", "README.md", "LICENSE.txt",
        "Me Goos-ta Deutsch - Android.html", "Me Goos-ta Deutsch - iPhone.html", "Me Goos-ta Deutsch - Google Pixel.html")
PROGRAMM_DATEIEN = {".py", ".md", ".lock"} | {"beispiel-karten.csv", "requirements.txt", "web_adresse.txt"}   # .lock: Paketfassungen (2.5)
PROGRAMM_ORDNER = ("assets", "beispiel-bilder", "modelle", "schrift", "ui", "vorlagen", "werkzeuge")
LEER = ("ausgabe",)                                            # leere Ordner, die das Programm erwartet
MAX_MODELL = 5 * 1024 * 1024                                   # großes Real-ESRGAN-Modell lädt das Programm selbst
WEG_ENDUNGEN = {".pyc", ".tmp", ".bak"}


def auswahl():
    """Liefert [(Quelle, Pfad im Release)] und die Liste der übersprungenen Dateien."""
    rein, raus = [], []
    for n in OBEN:
        rein.append((QUELLE / n, Path(n)))
    prog = QUELLE / "Programm"
    for p in sorted(prog.iterdir()):
        if p.is_file():
            (rein if (p.suffix in PROGRAMM_DATEIEN or p.name in PROGRAMM_DATEIEN) else raus).append(
                (p, Path("Programm") / p.name))
    for o in PROGRAMM_ORDNER:
        for p in sorted((prog / o).rglob("*")):
            if not p.is_file() or p.is_symlink():
                continue
            rel = p.relative_to(prog)
            weg = (p.suffix in WEG_ENDUNGEN or "__pycache__" in rel.parts
                   or (o == "modelle" and p.suffix == ".npz" and p.stat().st_size > MAX_MODELL)
                   or (o == "assets" and (p.name.startswith("gans_hintergrund.") or "_alt" in rel.parts)))  # eigenes Gänse-Bild
            (raus if weg else rein).append((p, Path("Programm") / rel))
    for o in sorted(prog.iterdir()):
        if o.is_dir() and o.name not in PROGRAMM_ORDNER:
            raus.append((o, Path("Programm") / (o.name + "/")))
    return rein, raus


def ordner(rein):
    ziel = ZIEL / NAME
    if ziel.exists():
        sys.exit(f"Zielordner gibt es schon: {ziel} – bitte erst umbenennen oder entfernen.")
    for q, rel in rein:
        z = ziel / rel
        z.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(q, z)
    for leer in LEER:
        (ziel / "Programm" / leer).mkdir(parents=True, exist_ok=True)
    return ziel


def zip_bauen(rein, version):
    pfad = ZIEL / f"{NAME}-{version}.zip"
    with zipfile.ZipFile(pfad, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for q, rel in rein:
            info = zipfile.ZipInfo.from_file(q, f"{NAME}/{rel.as_posix()}")
            info.create_system = 3                             # „Unix“ – sonst übernehmen Mac und Linux die Rechte nicht
            info.external_attr = (0o100755 if q.suffix in (".command", ".sh") else 0o100644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, q.read_bytes())
        for leer in LEER:
            info = zipfile.ZipInfo(f"{NAME}/Programm/{leer}/")
            info.create_system = 3
            info.external_attr = (0o040755 << 16) | 0x10
            z.writestr(info, b"")
    return pfad


if __name__ == "__main__":
    rein, raus = auswahl()
    fehlt = [str(q) for q, _ in rein if not q.is_file()]
    if fehlt:
        sys.exit("Fehlt: " + ", ".join(fehlt))
    ZIEL.mkdir(parents=True, exist_ok=True)
    if "--zip" in sys.argv:
        import re
        v = re.search(r'^VERSION = "([\d.]+)', (QUELLE / "Programm" / "gans_lernkarten.py").read_text("utf-8"), re.M)[1]
        p = zip_bauen(rein, v)
        print(f"✓ {p}  ({p.stat().st_size / 1e6:.1f} MB, {len(rein)} Dateien)")
    else:
        z = ordner(rein)
        groesse = sum(q.stat().st_size for q, _ in rein)
        print(f"✓ {z}  ({len(rein)} Dateien, {groesse / 1e6:.1f} MB)")
    print("Draußen gelassen:")
    for q, rel in raus:
        print("  -", rel.as_posix())
