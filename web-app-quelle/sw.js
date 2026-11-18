/* Me Goos-ta Deutsch – Service Worker der Handy-App (Web-App). Gebaut von bau_webapp.py: VERSION und DATEIEN setzt der
   Bau ein. Zuerst Zwischenspeicher: nach dem ersten Laden liegen alle Dateien der App am Gerät (offline). Adressen
   /api/…, /bild/…, /datei/… beantwortet Python im Web-Worker – der Weg dorthin führt über die Seite (app.js). Eine neue
   Version lädt im Hintergrund nur geänderte Dateien und wartet, bis die Seite „neu laden“ sagt. Die Antworten tragen
   COOP/COEP, damit die Seite „cross-origin isolated“ ist (Abbrechen laufender Aufträge über SharedArrayBuffer). */
"use strict";
const VERSION = "__VERSION__";
const DATEIEN = __DATEIEN__;                                   // [[Pfad, Größe, SHA-256 (16 Zeichen)], …]
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
