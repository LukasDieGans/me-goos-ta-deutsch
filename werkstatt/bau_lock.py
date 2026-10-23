#!/usr/bin/env python3
"""Me Goos-ta Deutsch – feste Paketfassungen mit Prüfsummen bauen (seit 2.5).

Schreibt nach Programm/ die Lock-Dateien im pip-Format (`pip install --require-hashes -r <lock>`): jede Fassung mit `==`,
je Paket die SHA-256 aller passenden Räder (Python 3.13, CPython) für Windows x64 (+ ARM, falls vorhanden), macOS Intel +
Apple Silicon und Linux x64 + ARM (glibc). Abhängigkeiten werden über `requires_dist` (mit Markern je Plattform) aufgelöst.

    python bau_lock.py [<Programm-Ordner>]                 # Fassungen der vorhandenen Locks behalten (sonst neueste)
    python bau_lock.py --neueste                           # neueste Fassungen innerhalb der Spannen (Release-Gruppe)
    python bau_lock.py --fassung numpy==2.5.4 [...]        # einzelne Fassungen festlegen
    python bau_lock.py --probe                             # offline: aus den gespeicherten Antworten neu bauen + vergleichen

Spannen: `pakete.lock` aus requirements.txt, die Ersatz-Sätze für Smart App Control (nur Windows x64) und uharfbuzz
(Sprachen hi/ar) unten in SAETZE. Die PyPI-Antworten (Fassungen, Abhängigkeiten, Dateinamen + SHA-256) landen in
bau_lock_antworten.json neben diesem Skript – `--probe` braucht kein Netz. Nur Standardbibliothek + das mit pip
mitgelieferte `packaging` (eigenes Python des Programms)."""
import json
import re
import sys
import urllib.request
from pathlib import Path

try:
    from pip._vendor.packaging.markers import Marker  # noqa: F401 – über Requirement genutzt
    from pip._vendor.packaging.requirements import Requirement
    from pip._vendor.packaging.specifiers import SpecifierSet
    from pip._vendor.packaging.utils import canonicalize_name
    from pip._vendor.packaging.version import InvalidVersion, Version
except ImportError:                                        # pragma: no cover – Python ohne pip
    from packaging.requirements import Requirement
    from packaging.specifiers import SpecifierSet
    from packaging.utils import canonicalize_name
    from packaging.version import InvalidVersion, Version

HIER = Path(__file__).resolve().parent
ANTWORTEN = HIER / "bau_lock_antworten.json"
PY_VOLL = "3.13.16"                                         # Windows-Startdatei (Mac/Linux 3.13.15 – gleiche Räder)
_UMG = dict(python_version="3.13", python_full_version=PY_VOLL, implementation_name="cpython",
            implementation_version=PY_VOLL, platform_python_implementation="CPython", platform_release="",
            platform_version="", extra="")
# Plattform: Muster des Plattform-Tags, Umgebung für Marker, Pflicht (False = nur, falls PyPI ein Rad hat)
PLATTFORMEN = {
    "win_amd64": (r"win_amd64", dict(sys_platform="win32", platform_system="Windows", platform_machine="AMD64",
                                     os_name="nt"), True),
    "win_arm64": (r"win_arm64", dict(sys_platform="win32", platform_system="Windows", platform_machine="ARM64",
                                     os_name="nt"), False),
    "macos_x86_64": (r"macosx_\d+_\d+_(x86_64|intel|universal2)", dict(sys_platform="darwin", platform_system="Darwin",
                                                                        platform_machine="x86_64", os_name="posix"), True),
    "macos_arm64": (r"macosx_\d+_\d+_(arm64|universal2)", dict(sys_platform="darwin", platform_system="Darwin",
                                                               platform_machine="arm64", os_name="posix"), True),
    "linux_x86_64": (r"(manylinux1|manylinux2010|manylinux2014|manylinux_2_\d+)_x86_64",
                     dict(sys_platform="linux", platform_system="Linux", platform_machine="x86_64", os_name="posix"), True),
    "linux_aarch64": (r"(manylinux2014|manylinux_2_\d+)_aarch64",
                      dict(sys_platform="linux", platform_system="Linux", platform_machine="aarch64", os_name="posix"), True),
}
ALLE = tuple(PLATTFORMEN)
# Lock-Datei: (Spannen – None = requirements.txt, Plattformen, Zweck für die Kopfzeile)
SAETZE = {
    "pakete.lock": (None, ALLE, "Standard (Erststart, Reparatur, neue Version)"),
    "pakete-bewaehrt.lock": (["reportlab>=4.0,<5", "pillow>=11.0,<12", "numpy>=2.1,<2.3", "pypdfium2>=4.30,<5"],
                             ("win_amd64",), "Ersatz-Satz „bewährt“ (nur Windows, wenn Smart App Control sperrt)"),
    "pakete-aelter.lock": (["reportlab>=4.0,<4.3", "pillow>=11.0,<11.1", "numpy>=2.1,<2.2", "pypdfium2>=4.30,<5",
                            "chardet>=7,<8"],                      # 0BSD erst ab 7.0 (5.x ist LGPL)
                           ("win_amd64",), "Ersatz-Satz „älter“ (nur Windows, wenn Smart App Control sperrt)"),
    "pakete-sprachen.lock": (["uharfbuzz==0.56.3"], ALLE, "Tool Sprachen: uharfbuzz für hi/ar (pip --target, ohne Abhängigkeiten)"),
}


class LockFehler(Exception):
    pass


# ---------------------------------------------------------------------------------------------
# PyPI (bzw. gespeicherte Antworten)
# ---------------------------------------------------------------------------------------------
class Quelle:
    def __init__(self, offline):
        self.offline = offline
        alt = json.loads(ANTWORTEN.read_text(encoding="utf-8")) if ANTWORTEN.is_file() else {}
        self.alt = alt if offline else {}
        self.neu = {"versionen": {}, "fassungen": {}}

    def _hole(self, url, accept="application/json"):
        anfrage = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "me-goos-ta-deutsch-bau_lock"})
        with urllib.request.urlopen(anfrage, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))

    def versionen(self, name):
        if name not in self.neu["versionen"]:
            if self.offline:
                if name not in self.alt.get("versionen", {}):
                    raise LockFehler(f"keine gespeicherte Antwort für {name} (ohne --probe neu bauen)")
                liste = self.alt["versionen"][name]
            else:
                d = self._hole(f"https://pypi.org/simple/{name}/", "application/vnd.pypi.simple.v1+json")
                liste = list(d.get("versions") or [])
            self.neu["versionen"][name] = liste
        return self.neu["versionen"][name]

    def fassung(self, name, version):
        k = f"{name}=={version}"
        if k not in self.neu["fassungen"]:
            if self.offline:
                if k not in self.alt.get("fassungen", {}):
                    raise LockFehler(f"keine gespeicherte Antwort für {k} (ohne --probe neu bauen)")
                self.neu["fassungen"][k] = self.alt["fassungen"][k]
            else:
                d = self._hole(f"https://pypi.org/pypi/{name}/{version}/json")
                self.neu["fassungen"][k] = {
                    "requires_dist": d["info"].get("requires_dist") or [],
                    "dateien": sorted([u["filename"], u["digests"]["sha256"]] for u in d.get("urls", [])
                                      if u.get("packagetype") == "bdist_wheel" and not u.get("yanked"))}
        return self.neu["fassungen"][k]

    def speichern(self, stand):
        ANTWORTEN.write_text(json.dumps(dict(self.neu, stand=stand), ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                             encoding="utf-8", newline="\n")


# ---------------------------------------------------------------------------------------------
# Räder und Auflösung
# ---------------------------------------------------------------------------------------------
def passt_python(datei):
    teile = datei[:-4].split("-")
    if len(teile) < 5:
        return False
    py, abi = teile[-3].split("."), teile[-2].split(".")
    if "abi3" in abi and any(re.fullmatch(r"cp3(\d+)", p) and 2 <= int(p[3:]) <= 13 for p in py):
        return True
    return any(p in ("py3", "py313", "cp313") for p in py) and any(a in ("none", "cp313") for a in abi)


def plattformen_von(datei):
    tags = datei[:-4].split("-")[-1].split(".")
    if "any" in tags:
        return set(ALLE)
    return {p for p, (muster, _u, _pf) in PLATTFORMEN.items() if any(re.fullmatch(muster, t) for t in tags)}


def raeder(info, plattformen):
    """[(dateiname, sha256, {plattformen})] aller passenden Räder."""
    aus = []
    for name, sha in info["dateien"]:
        if not passt_python(name):
            continue
        pf = plattformen_von(name) & set(plattformen)
        if pf:
            aus.append((name, sha, pf))
    return aus


def fehlende_plattformen(info, plattformen):
    da = set().union(*[pf for _n, _s, pf in raeder(info, plattformen)]) if raeder(info, plattformen) else set()
    return [p for p in plattformen if PLATTFORMEN[p][2] and p not in da]


def umgebung(p):
    return dict(_UMG, **PLATTFORMEN[p][1])


def waehle(quelle, name, spez, plattformen, gewuenscht=None):
    """Fassung: gewünschte (wenn in der Spanne), sonst die neueste stabile mit Rädern für alle Pflicht-Plattformen."""
    if gewuenscht and Version(gewuenscht) in spez:          # außerhalb der Spanne (anderer Satz): neueste passende
        if fehlende_plattformen(quelle.fassung(name, gewuenscht), plattformen):
            raise LockFehler(f"{name}=={gewuenscht}: keine Räder für "
                             f"{fehlende_plattformen(quelle.fassung(name, gewuenscht), plattformen)}")
        return gewuenscht
    kandidaten = []
    for s in quelle.versionen(name):
        try:
            v = Version(s)
        except InvalidVersion:
            continue
        if not v.is_prerelease and v in spez:
            kandidaten.append((v, s))
    for _v, s in sorted(kandidaten, reverse=True)[:25]:
        if not fehlende_plattformen(quelle.fassung(name, s), plattformen):
            return s
    raise LockFehler(f"keine Fassung von {name} {spez} mit Rädern für alle Plattformen")


def loese(quelle, spannen, plattformen, wuensche):
    """{name: {version, plattformen, raeder}} – einfache Auflösung ohne Zurückgehen (reicht für diese Pakete)."""
    oben = [Requirement(s) for s in spannen]
    for _runde in range(10):
        bedarf = {}                                       # name → (SpecifierSet, {plattformen})
        for r in oben:
            n = canonicalize_name(r.name)
            bedarf[n] = (r.specifier, set(plattformen))
        gewaehlt, offen = {}, list(bedarf)
        while offen:
            n = offen.pop(0)
            spez, pf = bedarf[n]
            v = waehle(quelle, n, spez, sorted(pf, key=ALLE.index), wuensche.get(n))
            gewaehlt[n] = v
            info = quelle.fassung(n, v)
            for zeile in info["requires_dist"]:
                r = Requirement(zeile)
                pf_dep = {p for p in pf if r.marker is None or r.marker.evaluate(umgebung(p))}
                if not pf_dep:
                    continue
                d = canonicalize_name(r.name)
                alt_spez, alt_pf = bedarf.get(d, (SpecifierSet(""), set()))
                neu = (alt_spez & r.specifier, alt_pf | pf_dep)
                if d not in bedarf or neu[0] != alt_spez or neu[1] != alt_pf:
                    bedarf[d] = neu
                    if d not in offen:
                        offen.append(d)
        if all(Version(gewaehlt[n]) in bedarf[n][0] for n in gewaehlt):
            return {n: dict(version=gewaehlt[n], plattformen=sorted(bedarf[n][1], key=ALLE.index),
                            raeder=raeder(quelle.fassung(n, gewaehlt[n]), bedarf[n][1])) for n in sorted(gewaehlt)}
        wuensche = {n: v for n, v in wuensche.items() if Version(v) in bedarf.get(n, (SpecifierSet(""),))[0]}
    raise LockFehler("Auflösung findet keinen festen Stand")


def marker_fuer(pf, alle):
    if set(pf) == set(alle):
        return ""
    systeme = {PLATTFORMEN[p][1]["sys_platform"] for p in pf}
    voll = {p for p in alle if PLATTFORMEN[p][1]["sys_platform"] in systeme}
    if voll != set(pf):
        raise LockFehler(f"Abhängigkeit nur auf einem Teil eines Systems ({pf}) – Marker von Hand prüfen")
    return " ; " + " or ".join(f'sys_platform == "{s}"' for s in sorted(systeme))


# ---------------------------------------------------------------------------------------------
# Lock-Dateien
# ---------------------------------------------------------------------------------------------
def lies_lock(pfad):
    """{name: version} einer vorhandenen Lock-Datei."""
    if not Path(pfad).is_file():
        return {}
    return {canonicalize_name(m.group(1)): m.group(2)
            for m in re.finditer(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==([^\s;\\]+)", Path(pfad).read_text(encoding="utf-8"), re.M)}


def spannen_aus(programm, datei):
    spannen = SAETZE[datei][0]
    if spannen is None:
        req = (Path(programm) / "requirements.txt").read_text(encoding="utf-8")
        spannen = [z.split("#")[0].strip() for z in req.splitlines() if z.split("#")[0].strip()]
    return spannen


def lock_text(datei, spannen, plattformen, stand):
    _s, _p, zweck = SAETZE[datei]
    namen = {"win_amd64": "Windows x64", "win_arm64": "Windows ARM (falls vorhanden)", "macos_x86_64": "macOS Intel",
             "macos_arm64": "macOS Apple Silicon", "linux_x86_64": "Linux x64 (glibc)", "linux_aarch64": "Linux ARM (glibc)"}
    zeilen = [f"# Me Goos-ta Deutsch – feste Paketfassungen mit SHA-256: {zweck}",
              f"# pip install --require-hashes --only-binary=:all: -r {datei}",
              f"# Gebaut von bau_lock.py (Arbeitsordner) aus: {', '.join(spannen)} · PyPI-Stand {stand}",
              f"# Python 3.13 (CPython) · {', '.join(namen[p] for p in plattformen)}",
              "# Nicht von Hand ändern – neu bauen: python bau_lock.py [--neueste]", ""]
    for n, e in loese_cache[datei].items():
        zeilen.append(f"# {n} {e['version']}: {len(e['raeder'])} Räder")
        zeilen += [f"#   {r[0]}" for r in e["raeder"]]
        zeilen.append(f"{n}=={e['version']}{marker_fuer(e['plattformen'], plattformen)} \\")
        hashes = [f"    --hash=sha256:{r[1]}" for r in e["raeder"]]
        zeilen += [h + " \\" for h in hashes[:-1]] + hashes[-1:]
        zeilen.append("")
    text = "\n".join(zeilen).translate(ASCII)                 # pip liest ohne BOM in der Sprache des Systems (cp1252 …)
    if not text.isascii():
        raise LockFehler(f"{datei}: Zeichen außerhalb von ASCII")
    return text


ASCII = str.maketrans({"–": "-", "·": "|", "„": '"', "“": '"', "→": "->", "ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae",
                       "Ö": "Oe", "Ü": "Ue", "ß": "ss"})


loese_cache = {}


def baue(programm, offline=False, neueste=False, fassungen=()):
    quelle = Quelle(offline)
    stand = quelle.alt.get("stand", "?") if offline else __import__("datetime").date.today().isoformat()
    vorgaben = {}
    for f in fassungen:
        n, _, v = f.partition("==")
        if not v:
            raise LockFehler(f"--fassung braucht name==version: {f}")
        vorgaben[canonicalize_name(n)] = v
    texte, aenderungen = {}, []
    for datei, (_sp, plattformen, _z) in SAETZE.items():
        spannen = spannen_aus(programm, datei)
        alt = lies_lock(Path(programm) / datei)
        wuensche = {} if neueste else dict(alt)
        oben = {canonicalize_name(Requirement(s).name) for s in spannen}
        wuensche.update({n: v for n, v in vorgaben.items() if n in oben or n in alt})
        ergebnis = loese(quelle, spannen, plattformen, wuensche)
        loese_cache[datei] = ergebnis
        texte[datei] = lock_text(datei, spannen, plattformen, stand)
        for n, e in ergebnis.items():
            if alt.get(n) != e["version"]:
                aenderungen.append(f"{datei}: {n} {alt.get(n, '–')} → {e['version']}")
    return quelle, stand, texte, aenderungen


def main(argv):
    if "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0
    offline, neueste = "--probe" in argv, "--neueste" in argv
    fassungen, rest, i = [], [], 0
    while i < len(argv):
        if argv[i] == "--fassung" and i + 1 < len(argv):
            fassungen.append(argv[i + 1])
            i += 2
            continue
        if not argv[i].startswith("--"):
            rest.append(argv[i])
        i += 1
    programm = Path(rest[0]) if rest else HIER.parent / "Me-Goos-ta-Deutsch" / "Programm"
    if not (programm / "requirements.txt").is_file():
        print(f"Kein Programm-Ordner (requirements.txt fehlt): {programm}", file=sys.stderr)
        return 2
    try:
        quelle, stand, texte, aenderungen = baue(programm, offline, neueste, fassungen)
    except (LockFehler, OSError, ValueError) as e:
        print(f"Abbruch: {e}", file=sys.stderr)
        return 1
    plan = {}
    for datei, text in texte.items():
        pfad = programm / datei
        e = loese_cache[datei]
        plan[datei] = {n: x["version"] for n, x in e.items()}
        gleich = pfad.is_file() and pfad.read_text(encoding="utf-8") == text
        if offline:
            print(("✓ " if gleich else "✗ ") + f"{datei}: {len(e)} Pakete, {sum(len(x['raeder']) for x in e.values())} Räder"
                  + ("" if gleich else " – weicht von den gespeicherten Antworten ab"))
        else:
            if not gleich:
                pfad.write_text(text, encoding="utf-8", newline="\n")
            print(("= " if gleich else "✓ ") + f"{datei}: " + ", ".join(f"{n} {x['version']}" for n, x in e.items()))
    for a in aenderungen:
        print("  " + a)
    print("#plan " + json.dumps(dict(stand=stand, locks=plan), ensure_ascii=False, sort_keys=True))
    if offline:
        return 0 if all((programm / d).is_file() and (programm / d).read_text(encoding="utf-8") == t
                        for d, t in texte.items()) else 1
    quelle.speichern(stand)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
