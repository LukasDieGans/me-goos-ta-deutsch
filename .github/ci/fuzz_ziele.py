#!/usr/bin/env python3
"""Me Goos-ta Deutsch – Fuzzing der Eingänge, die fremde Daten lesen (seit 2.5.1 G03).

Ziele (je eines pro Aufruf): markdown (gans_ui.markdown_html: Hilfe/Leitfäden), wortliste (erweiterungen.wortliste_lesen:
eingefügte oder gewählte Wortlisten), signatur (signatur.pruefe: .minisig der Releases), update_zip
(aktualisieren.pruefe_zip: heruntergeladenes Release-ZIP), karten (gans_lernkarten.lies_karten: karten.csv).
Jedes Ziel darf nur seinen eigenen, verständlichen Fehler werfen (WortlisteFehler, SignaturFehler, UpdateFehler) –
jede andere Ausnahme ist ein Fund.

    python fuzz_ziele.py <Programm-Ordner> --ziel markdown --zeit 60      # Atheris/libFuzzer (CI, fuzz.yml, Linux x64)
    python fuzz_ziele.py <Programm-Ordner> --ziel alle --zufall 300       # ohne Atheris: zufällige Abwandlungen der Startwerte
                                                                          # (nur Standardbibliothek, fest gesät – lokal, E58)

Atheris (Apache-2.0) nur in der CI, fest per fuzz.lock; nie im Programm. Datenordner = eigener Wegwerf-Ordner."""
import io
import os
import random
import sys
import tempfile
import traceback
import zipfile
from pathlib import Path

ZIELE = ("markdown", "wortliste", "signatur", "update_zip", "karten")


def lade(programm):
    """Programm-Module mit eigenem Datenordner importieren → {ziel: (funktion(bytes), erlaubte Fehler, Startwerte)}."""
    tmp = Path(tempfile.mkdtemp(prefix="mgd-fuzz-"))
    os.environ["MGD_DATEN"] = str(tmp / "daten")
    sys.path.insert(0, str(programm))
    import aktualisieren
    import erweiterungen
    import gans_lernkarten as gl
    import gans_ui
    import signatur

    def markdown(b):
        gans_ui.markdown_html(b.decode("utf-8", "replace"))

    def wortliste(b):
        erweiterungen.wortliste_lesen(b, {"kopf": "auto"})

    def sig(b):
        teil = b.find(b"\x00")
        nachricht, minisig = (b[:teil], b[teil + 1:]) if teil >= 0 else (b"", b)
        signatur.pruefe(nachricht, minisig)

    def update_zip(b):
        aktualisieren.pruefe_zip(io.BytesIO(b), "9.9")

    bilder = tmp / "bilder"
    bilder.mkdir()
    csv = tmp / "fuzz.csv"

    def karten(b):
        csv.write_bytes(b)
        gl.lies_karten(csv, bilder)

    beispiel = (Path(programm) / "beispiel-karten.csv").read_bytes()
    w = aktualisieren.WURZEL_NAME
    roh = io.BytesIO()
    with zipfile.ZipFile(roh, "w", zipfile.ZIP_DEFLATED) as z:
        for n in aktualisieren.PFLICHT:
            z.writestr(f"{w}/{n}", b'VERSION = "9.9"\n' if n.endswith("gans_lernkarten.py") else b"#")
    sig_start = (b"untrusted comment: signature from minisign secret key\n"
                 b"RUSZ8GZ4XT2cQOPm0mR+2Y3N8kq4l6e1Jxk0QxT5o2c3vQ9e5r7t1y3u5i7o9p1a3s5d7f9g1h3j5k7l9z1x3c5v7b9n1m3==\n"
                 b"trusted comment: timestamp:1761200000\tfile:SHA256SUMS.txt\thashed\n"
                 b"Zm9vYmFyZm9vYmFyZm9vYmFyZm9vYmFyZm9vYmFyZm9vYmFyZm9vYmFyZm9vYmFyZm9vYmFyZm9vYmFy==\n")
    return {
        "markdown": (markdown, (), [(Path(programm) / "LEITFADEN.md").read_bytes()[:4000],
                                    b"# T\n\n- a **b** `c` [x](https://e.org)\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n```\nq\n```\n"]),
        "wortliste": (wortliste, (erweiterungen.WortlisteFehler,), [b"Haus;casa\nBaum;\xc3\xa1rbol\n", b"de\tes\nHund\tperro\n",
                                                                    beispiel[:2000]]),
        "signatur": (sig, (signatur.SignaturFehler,), [b"inhalt\x00" + sig_start, sig_start]),
        "update_zip": (update_zip, (aktualisieren.UpdateFehler,), [roh.getvalue()]),
        "karten": (karten, (), [beispiel, b"bild;de;es;notiz\nhaus.jpg;Haus;casa;\n"]),
    }


def abwandeln(r, b):
    b = bytearray(b)
    for _ in range(r.randint(1, 8)):
        art = r.randrange(5)
        pos = r.randrange(len(b) + 1)
        if art == 0 and b:
            b[min(pos, len(b) - 1)] ^= 1 << r.randrange(8)
        elif art == 1:
            b[pos:pos] = bytes(r.randrange(256) for _ in range(r.randint(1, 16)))
        elif art == 2 and b:
            del b[pos:pos + r.randint(1, 64)]
        elif art == 3 and b:
            stueck = b[r.randrange(len(b)):][:r.randint(1, 128)]
            b[pos:pos] = stueck * r.randint(1, 20)
        else:
            b[pos:pos] = r.choice((b"\n", b"\r\n", b";", b"\t", b"|", b"**", b"`", b"[", b"](", b"#", b"\x00", b"\xff",
                                   b"\xef\xbb\xbf", b'"', b"PK\x03\x04", b"PK\x05\x06"))
    return bytes(b)


def zufall(ziele, programm, anzahl, saat=0):
    tabelle = lade(programm)
    funde = 0
    for ziel in ziele:
        f, erlaubt, starts = tabelle[ziel]
        r = random.Random(f"{saat}-{ziel}")
        for i in range(anzahl):
            daten = starts[i % len(starts)] if i < len(starts) else abwandeln(r, r.choice(starts))
            try:
                f(daten)
            except erlaubt:
                pass
            except Exception:  # noqa: BLE001 – jeder andere Fehler ist ein Fund
                funde += 1
                print(f"✗ {ziel} #{i}: {traceback.format_exc(limit=3).strip().splitlines()[-1]}  Daten={daten[:120]!r}")
                break
        else:
            print(f"✓ {ziel}: {anzahl} Eingaben ohne Fund")
    return 1 if funde else 0


def atheris_lauf(ziel, programm, zeit):
    import atheris                                       # nur in der CI (fuzz.lock), Linux x64
    with atheris.instrument_imports(include=["gans_ui", "erweiterungen", "signatur", "aktualisieren", "gans_lernkarten"]):
        tabelle = lade(programm)
    f, erlaubt, starts = tabelle[ziel]
    korpus = Path(tempfile.mkdtemp(prefix=f"mgd-korpus-{ziel}-"))
    for i, s in enumerate(starts):
        (korpus / f"start{i}").write_bytes(s)

    def eins(daten):
        try:
            f(daten)
        except erlaubt:
            pass

    atheris.Setup([sys.argv[0], f"-max_total_time={zeit}", "-timeout=20", "-rss_limit_mb=3072", "-max_len=65536",
                   str(korpus)], eins)
    atheris.Fuzz()


def main(argv):
    if not argv or "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0 if argv else 2

    def wert(name, standard):
        return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else standard
    programm = Path(argv[0]).resolve()
    ziel = wert("--ziel", "alle")
    if not (programm / "gans_ui.py").is_file() or (ziel != "alle" and ziel not in ZIELE):
        print(f"Aufruf: fuzz_ziele.py <Programm-Ordner> --ziel {'|'.join(ZIELE)}|alle [--zeit S | --zufall N]", file=sys.stderr)
        return 2
    ziele = ZIELE if ziel == "alle" else (ziel,)
    if "--zufall" in argv:
        return zufall(ziele, programm, int(wert("--zufall", "300")), int(wert("--saat", "0")))
    if len(ziele) != 1:
        print("Atheris: genau ein --ziel je Aufruf", file=sys.stderr)
        return 2
    atheris_lauf(ziele[0], programm, int(wert("--zeit", "60")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
