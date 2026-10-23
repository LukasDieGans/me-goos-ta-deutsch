#!/usr/bin/env python3
"""Einstellungen des öffentlichen Repositorys von Me Goos-ta Deutsch setzen (seit 2.5, G01).
Aufruf: python repo_einstellungen.py [--probe] [--stufe 1|2]

--probe    ohne Netz und ohne Anmeldung: zeigt den Plan der Stufe (Soll-Werte), ändert nichts
--stufe 1  (Standard) Topics, Wiki/Discussions aus, private Sicherheitsmeldungen, Dependabot-Warnungen, Secret
           Scanning + Push-Schutz, CodeQL (Standard-Einrichtung), Ruleset „Schutz main + gh-pages“ (Löschen und
           Force-Push verboten, keine Umgehung; Branch ci bleibt frei), Workflow „Probe“ abschalten
--stufe 2  (seit G06, scharf geschaltet in G08) Ruleset „Schutz Tags v*“ (Tags v* weder löschen noch verschieben),
           unveränderliche Releases (Assets und Tag eines veröffentlichten Releases bleiben, wie sie sind), Ruleset
           „Signierte Commits main + gh-pages“ (nur signierte Commits; ci frei). Keine Pflicht-Prüfungen vor dem Push:
           die CI prüft einen verwaisten Commit auf ci (andere SHA), die Freigabe macht die CI-Schranke im Skript.

Idempotent: jeder Schritt liest zuerst den Ist-Zustand und ändert nur, was abweicht („=“ schon richtig, „✓“ gesetzt);
danach wird erneut gelesen. Nur mit Lukas’ Erlaubnis-Satz „Einstellungen“ ohne --probe aufrufen.
Anmeldung wie veroeffentliche_webapp.py (GH_TOKEN → MGD-Release-Token; GitHub Desktop nur mit --desktop-anmeldung;
Recht Administration wird vorab gelesen; der Schlüssel wird nie ausgegeben).
Konto und Repository stammen aus Programm/web_adresse.txt. Nur Standardbibliothek."""
import json
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent                          # werkstatt/ (seit 2.5 G04)
ARBEIT = HIER.parent                                            # Wurzel des Quellbaums (Arbeitsordner)
sys.path.insert(0, str(HIER))
sys.dont_write_bytecode = True
import veroeffentliche_webapp as vw  # noqa: E402  Anmeldung, GitHub-API

WEB_ADRESSE = ARBEIT / "Me-Goos-ta-Deutsch" / "Programm" / "web_adresse.txt"
TOPICS = ["german", "learn-german", "language-learning", "flashcards", "spaced-repetition", "fsrs", "anki", "pwa",
          "python", "offline", "printable"]
RULESET = "Schutz main + gh-pages"
RULESET_SOLL = dict(name=RULESET, target="branch", enforcement="active", bypass_actors=[],
                    conditions={"ref_name": {"include": ["refs/heads/main", "refs/heads/gh-pages"], "exclude": []}},
                    rules=[{"type": "deletion"}, {"type": "non_fast_forward"}])
TAG_SOLL = dict(name="Schutz Tags v*", target="tag", enforcement="active", bypass_actors=[],
                conditions={"ref_name": {"include": ["refs/tags/v*"], "exclude": []}},
                rules=[{"type": "deletion"}, {"type": "non_fast_forward"}, {"type": "update"}])
SIGNIERT_SOLL = dict(name="Signierte Commits main + gh-pages", target="branch", enforcement="active", bypass_actors=[],
                     conditions={"ref_name": {"include": ["refs/heads/main", "refs/heads/gh-pages"], "exclude": []}},
                     rules=[{"type": "required_signatures"}])
PROBE_WORKFLOW = ".github/workflows/probe.yml"


def abbruch(text):
    sys.exit(f"✗ {text}")


def konto_repo(pfad=WEB_ADRESSE):
    zeile = pfad.read_text(encoding="utf-8").strip().splitlines()[0].strip()
    m = re.match(r"^https://([a-z0-9-]+)\.github\.io/([A-Za-z0-9._-]+)/$", zeile)
    if not m:
        abbruch(f"{pfad} nennt keine GitHub-Pages-Adresse.")
    return m.group(1), m.group(2)


# ---- Schritte: (id, Titel, Soll, lesen(api) → Ist, passt(ist) → bool, setzen(api)) ----------------------------------

def _repo(api):
    return api("GET", "")[1]


def _sicherheit(api):
    sa = _repo(api).get("security_and_analysis") or {}
    return {k: (sa.get(k) or {}).get("status") for k in ("secret_scanning", "secret_scanning_push_protection")}


def _ruleset(api, soll=RULESET_SOLL):
    s, liste = api("GET", "/rulesets?includes_parents=false")
    for r in liste if s == 200 and isinstance(liste, list) else []:
        if r.get("name") == soll["name"]:
            return api("GET", f"/rulesets/{r['id']}")[1]
    return None


def _ruleset_passt(ist, soll=RULESET_SOLL):
    if not ist:
        return False
    regeln = sorted(r.get("type") for r in ist.get("rules") or [])
    ref = (ist.get("conditions") or {}).get("ref_name") or {}
    return (ist.get("enforcement") == "active" and ist.get("target") == soll["target"] and not ist.get("bypass_actors")
            and regeln == sorted(r["type"] for r in soll["rules"]) and sorted(ref.get("include") or []) ==
            sorted(soll["conditions"]["ref_name"]["include"]) and not ref.get("exclude"))


def _ruleset_setzen(api, soll=RULESET_SOLL):
    ist = _ruleset(api, soll)
    return api("PUT", f"/rulesets/{ist['id']}", soll) if ist else api("POST", "/rulesets", soll)


def _ruleset_schritt(sid, titel, soll):
    return (sid, titel, {"name": soll["name"], "include": soll["conditions"]["ref_name"]["include"],
                         "regeln": [r["type"] for r in soll["rules"]], "umgehung": []},
            lambda api: _ruleset(api, soll), lambda ist: _ruleset_passt(ist, soll), lambda api: _ruleset_setzen(api, soll))


def _probe_workflow(api):
    s, r = api("GET", "/actions/workflows?per_page=100")
    for w in (r.get("workflows") or []) if s == 200 else []:
        if w.get("path") == PROBE_WORKFLOW:
            return w
    return None


def _probe_abschalten(api):
    w = _probe_workflow(api)
    return api("PUT", f"/actions/workflows/{w['id']}/disable") if w else (204, {})


STUFE_1 = [
    ("topics", "Topics (Themen auf der Startseite)", TOPICS,
     lambda api: api("GET", "/topics")[1].get("names"),
     lambda ist: sorted(ist or []) == sorted(TOPICS),
     lambda api: api("PUT", "/topics", {"names": TOPICS})),
    ("wiki_discussions", "Wiki und Discussions aus", {"has_wiki": False, "has_discussions": False},
     lambda api: {k: _repo(api).get(k) for k in ("has_wiki", "has_discussions")},
     lambda ist: ist == {"has_wiki": False, "has_discussions": False},
     lambda api: api("PATCH", "", {"has_wiki": False, "has_discussions": False})),
    ("private_meldungen", "Private Sicherheitsmeldungen („Report a vulnerability“)", True,
     lambda api: api("GET", "/private-vulnerability-reporting")[1].get("enabled"),
     lambda ist: ist is True,
     lambda api: api("PUT", "/private-vulnerability-reporting")),
    ("dependabot_warnungen", "Dependabot-Warnungen (Sicherheitslücken in Paketen)", True,
     lambda api: api("GET", "/vulnerability-alerts")[0] == 204,
     lambda ist: ist is True,
     lambda api: api("PUT", "/vulnerability-alerts")),
    ("secret_scanning", "Secret Scanning + Push-Schutz", {"secret_scanning": "enabled", "secret_scanning_push_protection": "enabled"},
     _sicherheit,
     lambda ist: ist == {"secret_scanning": "enabled", "secret_scanning_push_protection": "enabled"},
     lambda api: api("PATCH", "", {"security_and_analysis": {"secret_scanning": {"status": "enabled"},
                                                             "secret_scanning_push_protection": {"status": "enabled"}}})),
    ("codeql", "CodeQL (Standard-Einrichtung, Abfragen „default“)", "configured",
     lambda api: api("GET", "/code-scanning/default-setup")[1].get("state"),
     lambda ist: ist == "configured",
     lambda api: api("PATCH", "/code-scanning/default-setup", {"state": "configured", "query_suite": "default"})),
    ("ruleset", f"Ruleset „{RULESET}“ (Löschen + Force-Push verboten, keine Umgehung; ci frei)",
     {"include": RULESET_SOLL["conditions"]["ref_name"]["include"], "regeln": ["deletion", "non_fast_forward"],
      "umgehung": []},
     _ruleset, _ruleset_passt, _ruleset_setzen),
    ("probe_aus", "Workflow „Probe“ (probe.yml, Runner-Proben) abschalten", "aus",
     lambda api: (lambda w: w and w.get("state"))(_probe_workflow(api)),
     lambda ist: ist in (None, "disabled_manually"),
     _probe_abschalten),
]
STUFE_2 = [
    _ruleset_schritt("tags", "Ruleset „Schutz Tags v*“ (Tags weder löschen noch verschieben, keine Umgehung)", TAG_SOLL),
    ("unveraenderlich", "Unveränderliche Releases (immutable releases)", True,
     lambda api: api("GET", "/immutable-releases")[1].get("enabled"),
     lambda ist: ist is True,
     lambda api: api("PUT", "/immutable-releases")),
    _ruleset_schritt("signierte_commits", "Ruleset „Signierte Commits main + gh-pages“ (ci frei)", SIGNIERT_SOLL),
]
STUFEN = {1: STUFE_1, 2: STUFE_2}       # Stufe 2 seit G06 angelegt, angewendet erst in G08 (Release 2.5)


def plan(stufe):
    konto, repo = konto_repo()
    return dict(konto=konto, repo=repo, stufe=stufe,
                schritte=[dict(id=i, titel=t, soll=soll) for i, t, soll, *_ in STUFEN[stufe]])


def ausfuehren(stufe):
    p = plan(stufe)
    tok, woher = vw.token()
    s, ich = vw.api("GET", "/user", tok)
    if s != 200:
        abbruch(f"Anmeldung ({woher}) abgelehnt: {s} {ich.get('message', '')}")
    if ich["login"].lower() != p["konto"]:
        abbruch(f"Angemeldet als {ich['login']}, web_adresse.txt gehört zu {p['konto']}.")
    vw.rechte_pruefen(tok, ich["login"], p["repo"], ("administration",))
    weg = f"/repos/{ich['login']}/{p['repo']}"

    def api(methode, rest, daten=None):
        return vw.api(methode, weg + rest, tok, daten)
    print(f"Konto {ich['login']} (Anmeldung: {woher}) · Repository {p['repo']} · Stufe {stufe}")
    ergebnis, fehler = {}, 0
    for sid, titel, _soll, lesen, passt, setzen in STUFEN[stufe]:
        ist = lesen(api)
        if passt(ist):
            print(f"  = {titel}")
            ergebnis[sid] = "schon"
            continue
        s, r = setzen(api)
        if s not in (200, 201, 202, 204) or not passt(lesen(api)) and sid != "codeql":
            print(f"  ✗ {titel}: {s} {str(r.get('message', '') if isinstance(r, dict) else r)[:200]}")
            ergebnis[sid], fehler = f"fehler {s}", fehler + 1
            continue
        print(f"  ✓ {titel}" + (" (läuft im Hintergrund an)" if s == 202 else ""))
        ergebnis[sid] = "gesetzt"
    print("#ergebnis " + json.dumps(ergebnis, ensure_ascii=False))
    return 1 if fehler else 0


def main(argv):
    stufe = int(argv[argv.index("--stufe") + 1]) if "--stufe" in argv and argv.index("--stufe") + 1 < len(argv) else 1
    if stufe not in STUFEN:
        abbruch("--stufe 1 oder 2")
    if "--probe" in argv:
        p = plan(stufe)
        print(f"Plan (Probe – ohne Netz, nichts wird verändert): {p['konto']}/{p['repo']} · Stufe {stufe}")
        for s in p["schritte"]:
            print(f"  · {s['titel']}")
        print("#plan " + json.dumps(p, ensure_ascii=False))
        return 0
    return ausfuehren(stufe)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
