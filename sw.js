/* Me Goos-ta Deutsch – Service Worker der Handy-App (Web-App). Gebaut von bau_webapp.py: VERSION und DATEIEN setzt der
   Bau ein. Zuerst Zwischenspeicher: nach dem ersten Laden liegen alle Dateien der App am Gerät (offline). Adressen
   /api/…, /bild/…, /datei/… beantwortet Python im Web-Worker – der Weg dorthin führt über die Seite (app.js). Eine neue
   Version lädt im Hintergrund nur geänderte Dateien und wartet, bis die Seite „neu laden“ sagt. Die Antworten tragen
   COOP/COEP, damit die Seite „cross-origin isolated“ ist (Abbrechen laufender Aufträge über SharedArrayBuffer). */
"use strict";
const VERSION = "2.3-180e1bcc07";
const DATEIEN = [["app.js",16427,"3188bfea6e26b17f"],["favicon.ico",40985,"2cb3006f8b565df5"],["index.html",105008,"39d119e24fbc348b"],["lizenzen/DRITTLIZENZEN.md",9437,"3d005949f5cd090c"],["lizenzen/LICENSE.txt",1185,"fe55b58ad3a4a533"],["lizenzen/OFL-Poppins.txt",4332,"517d8225b8532f9b"],["lizenzen/PYODIDE.txt",518,"13e95a263de6d42a"],["manifest.webmanifest",1361,"7402d408be063279"],["modelle/modelle.json",136,"96d6d4a69f194dde"],["py/programm.zip",1680542,"cccfd95e0b397d78"],["pyodide/charset_normalizer-3.4.7-py3-none-any.whl",61958,"9e437ef92fa51f06"],["pyodide/numpy-2.4.6-cp314-cp314-pyemscripten_2026_0_wasm32.whl",2960568,"a292c1f5d7d8a220"],["pyodide/pillow-12.2.0-cp314-cp314-pyemscripten_2026_0_wasm32.whl",1037806,"e29838b7a756e4ee"],["pyodide/pyodide-lock.json",119077,"5dc2fc119108bc14"],["pyodide/pyodide.asm.mjs",1250344,"f7cdc8ece80678ce"],["pyodide/pyodide.asm.wasm",9598218,"cc36e3cab04fdfc9"],["pyodide/pyodide.mjs",17931,"6f1d60f7bf529beb"],["pyodide/python_stdlib.zip",2545637,"fa1957e5777068fc"],["pyodide/reportlab-5.0.1-py3-none-any.whl",1957258,"1c36e6bb0e71780c"],["schrift/Poppins-Bold.ttf",155996,"983676516167748b"],["schrift/Poppins-Medium.ttf",158576,"90373e7d838d3246"],["schrift/Poppins-Regular.ttf",160316,"7e65201e9b79159e"],["symbol.svg",3963,"40dbfb773a098ac0"],["symbole/apple-touch-icon.png",13539,"1ebca13522114513"],["symbole/symbol-192.png",19314,"9c14d93230b0fb4c"],["symbole/symbol-512.png",32692,"4c554ee03dc11e8f"],["symbole/symbol-maskable-512.png",45608,"4f17b9bd81143e98"],["ui.js",524725,"e15723b1220421e7"],["worker.js",4688,"95f1cb9930f5f50b"]];                                   // [[Pfad, Größe, SHA-256 (16 Zeichen)], …]
const CACHE = "mgd-app-" + VERSION;
const BASIS = new URL("./", self.location).pathname;           // z. B. /me-goos-ta-deutsch/
const APP_WEGE = /^(api|bild|datei)\//;
const EIGENE_SEITEN = /^download(\/|$)/;                       // Download-Seite (für den Rechner): nie die App, nie aus dem Vorrat
const ISOLIERT = { "Cross-Origin-Opener-Policy": "same-origin", "Cross-Origin-Embedder-Policy": "require-corp",
  "Cross-Origin-Resource-Policy": "same-origin" };
const TYPEN = { html: "text/html; charset=utf-8", js: "text/javascript; charset=utf-8", mjs: "text/javascript; charset=utf-8",
  wasm: "application/wasm", json: "application/json", webmanifest: "application/manifest+json", zip: "application/zip",
  whl: "application/zip", png: "image/png", svg: "image/svg+xml", ico: "image/x-icon", ttf: "font/ttf",
  md: "text/markdown; charset=utf-8", txt: "text/plain; charset=utf-8", css: "text/css; charset=utf-8" };
const typ = pfad => TYPEN[pfad.split(".").pop().toLowerCase()] || "application/octet-stream";
// Sprache der eigenen Meldung: Englisch, bis die Seite die im Programm gewählte meldet (im Cache gemerkt – der Service
// Worker wird zwischendurch beendet). Die Gerätesprache zählt nicht.
const SPRACHE_CACHE = "mgd-einstellungen", SPRACHE_URL = BASIS + "__mgd-sprache__";
let gewaehlt = null;
async function sprache() {
  if (!gewaehlt) {
    try { const r = await (await caches.open(SPRACHE_CACHE)).match(SPRACHE_URL); gewaehlt = r ? await r.text() : "en"; } catch (f) { gewaehlt = "en"; }
  }
  return gewaehlt;
}
const TEXT_KEIN_FENSTER = { de: "Die App startet gerade – einen Moment, dann klappt es.",
  en: "The app is just starting – give it a moment, then it works.", es: "La app está iniciando; espera un momento y funcionará." };

async function melden(daten) {
  for (const c of await self.clients.matchAll({ includeUncontrolled: true, type: "window" })) c.postMessage(daten);
}
async function pruefsumme(daten) {
  return [...new Uint8Array(await crypto.subtle.digest("SHA-256", daten))].map(b => b.toString(16).padStart(2, "0")).join("").slice(0, 16);
}

self.addEventListener("install", e => {
  e.waitUntil((async () => {
    const erste = !self.registration.active;
    const neu = await caches.open(CACHE);
    const alte = [];
    for (const k of await caches.keys()) if (k.startsWith("mgd-app-") && k !== CACHE) alte.push(await caches.open(k));
    const gesamt = DATEIEN.reduce((s, d) => s + d[1], 0);
    let geladen = 0, zuletzt = 0;
    for (const [pfad, groesse, hash] of DATEIEN) {             // nacheinander: gleichmäßiger Fortschritt, kein Gedränge
      const url = BASIS + pfad;
      let da = await neu.match(url);
      if (!da || da.headers.get("x-mgd-hash") !== hash) {
        da = null;
        for (const c of alte) { const a = await c.match(url); if (a && a.headers.get("x-mgd-hash") === hash) { da = a; break; } }
        if (da) await neu.put(url, da);                        // unverändert: aus der alten Version übernehmen
        else {
          const r = await fetch(url + "?v=" + hash, { cache: "no-cache" });
          if (!r.ok) throw new Error(`${pfad}: HTTP ${r.status}`);
          const daten = await r.arrayBuffer();
          if (await pruefsumme(daten) !== hash) throw new Error(`${pfad}: SHA-256`);
          await neu.put(url, new Response(daten, { headers: { "Content-Type": typ(pfad), "x-mgd-hash": hash } }));
        }
      }
      geladen += groesse;
      if (geladen === gesamt || Date.now() - zuletzt > 150) { zuletzt = Date.now(); melden({ typ: "laden", geladen, gesamt, erste }); }
    }
    if (erste) await self.skipWaiting();                       // allererste Installation: gleich übernehmen
  })());
});

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (k.startsWith("mgd-app-") && k !== CACHE) await caches.delete(k);
    await self.clients.claim();
    melden({ typ: "aktiv", version: VERSION });
  })());
});

self.addEventListener("message", e => {
  if (e.data === "weiter") self.skipWaiting();
  if (e.data && e.data.typ === "sprache" && TEXT_KEIN_FENSTER[e.data.sprache] && e.data.sprache !== gewaehlt) {
    gewaehlt = e.data.sprache;
    e.waitUntil(caches.open(SPRACHE_CACHE).then(c => c.put(SPRACHE_URL, new Response(gewaehlt))).catch(() => {}));
  }
});

self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (url.origin !== self.location.origin) return;            // fremde Adressen (Übersetzung): wie gewohnt übers Netz
  const rel = url.pathname.startsWith(BASIS) ? url.pathname.slice(BASIS.length) : url.pathname.replace(/^\//, "");
  if (EIGENE_SEITEN.test(rel)) return;                         // wie ohne Service Worker übers Netz
  if (APP_WEGE.test(rel)) e.respondWith(anPython(e, "/" + decodeURIComponent(rel), url.search.slice(1)));
  else e.respondWith(ausCache(e.request, rel));
});

function isoliert(r) {
  const kopf = new Headers(r.headers);
  for (const [n, w] of Object.entries(ISOLIERT)) kopf.set(n, w);
  return new Response(r.body, { status: r.status, statusText: r.statusText, headers: kopf });
}

async function ausCache(anfrage, rel) {
  const cache = await caches.open(CACHE);
  let r = await cache.match(BASIS + (rel || "index.html"));
  if (!r && anfrage.mode === "navigate") r = await cache.match(BASIS + "index.html");
  if (!r) {
    try { r = await fetch(anfrage); }                          // nicht in der Liste (z. B. modelle/*.npz): übers Netz
    catch (err) { return new Response("offline", { status: 503, headers: { "Content-Type": "text/plain" } }); }
  }
  return isoliert(r);
}

function frage(client, nachricht) {
  return new Promise(fertig => {
    const kanal = new MessageChannel();
    let wache = null;
    const ende = d => { clearTimeout(uhr); clearInterval(wache); fertig(d); };
    const uhr = setTimeout(() => ende(null), 4000);            // kein „angenommen“ → nächstes Fenster versuchen
    kanal.port1.onmessage = m => {
      if (!(m.data && m.data.typ === "angenommen")) return ende(m.data);
      clearTimeout(uhr);                                       // rechnet – solange das Fenster offen ist, wird gewartet
      wache = setInterval(async () => { if (!(await self.clients.get(client.id))) ende(null); }, 2000);
    };
    client.postMessage(nachricht, [kanal.port2]);
  });
}

async function anPython(e, weg, abfrage) {
  const a = e.request;
  const koerper = a.method === "GET" || a.method === "HEAD" ? null : await a.arrayBuffer();
  const kopf = {};
  a.headers.forEach((w, n) => { kopf[n] = w; });
  const fenster = await self.clients.matchAll({ type: "window" });
  const eigenes = e.clientId ? fenster.find(c => c.id === e.clientId) : null;
  const reihe = [eigenes, ...fenster.filter(c => c !== eigenes && c.id !== e.resultingClientId)].filter(Boolean);
  for (const c of reihe) {
    const r = await frage(c, { typ: "api", methode: a.method, weg, abfrage, kopf, koerper });
    if (r) {
      const leer = a.method === "HEAD" || [204, 205, 304].includes(r.status);
      return new Response(leer ? null : r.inhalt, { status: r.status, headers: { ...r.kopf, ...ISOLIERT } });
    }
  }
  const text = TEXT_KEIN_FENSTER[await sprache()] || TEXT_KEIN_FENSTER.en;
  return new Response(JSON.stringify({ fehler: text }), { status: 503, headers: { "Content-Type": "application/json; charset=utf-8", ...ISOLIERT } });
}
