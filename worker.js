/* Me Goos-ta Deutsch – Python im Web-Worker (Pyodide). Gebaut von bau_webapp.py (Platzhalter __…__ setzt der Bau ein).
   Lädt Pyodide + NumPy, Pillow, ReportLab, legt das Programm nach /mgd (IndexedDB über IDBFS: Karten, Bilder, Lernstand,
   Einstellungen bleiben am Gerät) und beantwortet jede Anfrage der Seite mit gans_ui.verarbeite() – dieselbe Logik wie am
   Rechner. Gestartete Aufträge laufen direkt nach der Antwort (gans_ui.web_weiter); ihren Fortschritt meldet Python über
   WEB_MELDER, damit die Seite ihn zeigen kann, während der Worker rechnet. */
import { loadPyodide } from "./pyodide/pyodide.mjs";

const PROGRAMM = "py/programm.zip", PROGRAMM_HASH = "54646a6042534e38", REPORTLAB = "pyodide/reportlab-5.0.1-py3-none-any.whl";
const PAKETE = ["numpy", "pillow", "charset-normalizer"];
const ORDNER = "/mgd";
let py = null, gans = null, dreckig = false, uhr = null, schreibt = Promise.resolve(), unterbrechen = null;

const melde = schritt => self.postMessage({ typ: "schritt", schritt });
const syncfs = laden => new Promise((ok, nein) => py.FS.syncfs(laden, f => (f ? nein(f) : ok())));

function sichernSpaeter() { dreckig = true; clearTimeout(uhr); uhr = setTimeout(sichern, 400); }
function sichern() {
  clearTimeout(uhr);
  if (dreckig && py) {
    dreckig = false;
    schreibt = schreibt.then(() => syncfs(false)).catch(f => self.postMessage({ typ: "speicher", text: String((f && f.message) || f) }));
  }
  return schreibt;
}

async function starten(m) {
  try {
    melde("pyodide");
    py = await loadPyodide({ indexURL: new URL("./pyodide/", self.location).href, stdout: () => {}, stderr: () => {} });
    if (m.unterbrechen) { unterbrechen = m.unterbrechen; py.setInterruptBuffer(unterbrechen); }
    melde("pakete");
    await py.loadPackage([...PAKETE, new URL(REPORTLAB, self.location).href], { messageCallback: () => {} });
    melde("daten");
    py.FS.mkdirTree(ORDNER);
    py.FS.mount(py.FS.filesystems.IDBFS, {}, ORDNER);
    await syncfs(true);
    let stand = "";
    try { stand = py.FS.readFile(ORDNER + "/.programm", { encoding: "utf8" }); } catch (f) { /* erster Start */ }
    if (stand !== PROGRAMM_HASH) {                              // neue Programmfassung: Dateien des Programms ersetzen
      const r = await fetch(PROGRAMM);
      if (!r.ok) throw new Error(`${PROGRAMM}: HTTP ${r.status}`);
      py.unpackArchive(await r.arrayBuffer(), "zip", { extractDir: ORDNER });
      py.FS.writeFile(ORDNER + "/.programm", PROGRAMM_HASH);
      await syncfs(false);
    }
    melde("python");
    py.runPython(`import os, sys
os.environ["MGD_DATEN"] = "${ORDNER}/daten"
sys.dont_write_bytecode = True
if "${ORDNER}" not in sys.path:
    sys.path.insert(0, "${ORDNER}")
os.chdir("${ORDNER}")`);
    gans = py.pyimport("gans_ui");
    gans.WEB_MELDER = text => self.postMessage({ typ: "lauf", json: text });
    let info = JSON.parse(py.runPython("import json, gans_ui; json.dumps(gans_ui.web_info())"));
    if (!info.sprache_gewaehlt && ["de", "en", "es"].includes(m.sprache)) {   // erster Start: Sprache des Geräts
      gans.speichere_sprache(m.sprache);
      info = JSON.parse(py.runPython("json.dumps(gans_ui.web_info())"));
    }
    sichernSpaeter();
    self.postMessage({ typ: "bereit", info, isoliert: !!unterbrechen });
  } catch (f) {
    self.postMessage({ typ: "fehler", text: String((f && f.message) || f) });
  }
}

function bearbeiten(m) {
  let antwort;
  try {
    const erg = gans.web_anfrage(m.methode, m.weg, m.abfrage || "", m.koerper ? new Uint8Array(m.koerper) : null,
                                 JSON.stringify(m.kopf || {}));
    const roh = erg.get(2), puffer = roh.getBuffer("u8");
    const inhalt = puffer.data.slice().buffer;
    puffer.release(); roh.destroy();
    antwort = { typ: "antwort", id: m.id, status: erg.get(0), kopf: JSON.parse(erg.get(1)), inhalt };
    erg.destroy();
  } catch (f) {
    const text = JSON.stringify({ fehler: String((f && f.message) || f).split("\n").slice(-3).join(" ") });
    antwort = { typ: "antwort", id: m.id, status: 500, kopf: { "Content-Type": "application/json; charset=utf-8" },
                inhalt: new TextEncoder().encode(text).buffer };
  }
  self.postMessage(antwort, [antwort.inhalt]);
  sichernSpaeter();
  laufen();
}

function laufen() {                                             // gestartete Aufträge jetzt rechnen (Seite sieht den Fortschritt)
  let n = 0;
  try { n = gans.web_weiter(); } catch (f) { /* Abbruch außerhalb eines Auftrags: nichts zu tun */ }
  if (unterbrechen) unterbrechen[0] = 0;
  if (n) { self.postMessage({ typ: "frei" }); sichernSpaeter(); }
}

self.onmessage = async e => {
  const m = e.data;
  if (m.typ === "start") return starten(m);
  if (m.typ === "anfrage") return bearbeiten(m);
  if (m.typ === "sichern") { dreckig = true; await sichern(); self.postMessage({ typ: "gesichert", id: m.id }); }
};
