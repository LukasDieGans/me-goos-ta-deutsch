/* Me Goos-ta Deutsch – Start der Handy-App (Web-App). Gebaut von bau_webapp.py. Ablauf: Startbildschirm mit Lade-Ente →
   Service Worker (sw.js) holt beim ersten Mal alle Dateien aufs Gerät (MB-Fortschritt) → Python startet im Web-Worker
   (worker.js) → Sprache und Farben setzen → die Oberfläche (ui.js = dieselbe Seite wie am Rechner) lädt. Danach reicht diese
   Datei jede Anfrage /api/…, /bild/…, /datei/…, die der Service Worker abfängt, an Python weiter, zeigt den Fortschritt
   laufender Aufträge, bietet Ergebnisse zum Teilen/Speichern an und meldet neue Versionen. */
"use strict";
(() => {
  const TEXTE = {
    de: { start: "Die Gans macht sich startklar", laden: (g, s) => `Lade die App aufs Gerät: ${g} von ${s} MB (nur beim ersten Mal)`,
      pyodide: "Python wird geweckt", pakete: "Werkzeuge auspacken", daten: "Deine Karten holen", python: "Fast gans fertig",
      alt: "Dieser Browser kann die App leider nicht ausführen. Nimm bitte ein aktuelles Chrome, Safari (ab iOS 16.4), Edge oder Firefox – über https.",
      fehler: t => `Die Gans ist gestolpert: ${t}`, nochmal: "Nochmal versuchen",
      zweites: "Die Gans ist schon in einem anderen Fenster offen – damit nichts durcheinanderkommt, watschelt sie immer nur in einem.",
      hier: "Hier weitermachen", umgezogen: "Die Gans ist in ein anderes Fenster umgezogen – dieses hier kannst du schließen.",
      speicher: "Speichern am Gerät klappt gerade nicht – ist der Speicher voll? Sichere am besten gleich (Mehr → Sicherung)." },
    en: { start: "The goose is getting ready", laden: (g, s) => `Loading the app onto your device: ${g} of ${s} MB (first time only)`,
      pyodide: "Waking up Python", pakete: "Unpacking the tools", daten: "Fetching your cards", python: "Almost there",
      alt: "Sorry, this browser can’t run the app. Please use an up-to-date Chrome, Safari (iOS 16.4 or later), Edge or Firefox – via https.",
      fehler: t => `The goose tripped: ${t}`, nochmal: "Try again",
      zweites: "The goose is already open in another window – to keep everything in order, it only waddles in one at a time.",
      hier: "Continue here", umgezogen: "The goose has moved to another window – you can close this one.",
      speicher: "Saving on this device isn’t working right now – is the storage full? Best make a backup right away (More → Backup)." },
    es: { start: "El ganso se está preparando", laden: (g, s) => `Cargando la app en tu dispositivo: ${g} de ${s} MB (solo la primera vez)`,
      pyodide: "Despertando a Python", pakete: "Desempacando las herramientas", daten: "Trayendo tus cartas", python: "Ya casi",
      alt: "Este navegador no puede ejecutar la app. Usa un Chrome, Safari (desde iOS 16.4), Edge o Firefox actualizado, por https.",
      fehler: t => `El ganso se tropezó: ${t}`, nochmal: "Intentar de nuevo",
      zweites: "El ganso ya está abierto en otra ventana; para que nada se revuelva, solo anadea en una a la vez.",
      hier: "Continuar aquí", umgezogen: "El ganso se mudó a otra ventana; puedes cerrar esta.",
      speicher: "Guardar en el dispositivo no funciona ahora: ¿está lleno el almacenamiento? Mejor haz una copia ya (Más → Copia)." },
  };
  const merke = (k, v) => { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (f) { /* privat */ } return null; };
  let sprache = merke("mgd-sprache") || (navigator.languages || [navigator.language || "en"]).map(l => String(l).slice(0, 2).toLowerCase())
    .find(l => TEXTE[l]) || "en";
  const tt = (k, ...a) => { const v = (TEXTE[sprache] || TEXTE.en)[k]; return typeof v === "function" ? v(...a) : v; };
  const $ = id => document.getElementById(id);
  const mb = n => (n / 1048576).toFixed(1).replace(".", sprache === "en" ? "." : ",");
  document.documentElement.lang = sprache;
  const farben = merke("mgd-farben");                           // letzte Farben sofort (kein Aufblitzen), Python bestätigt
  if (farben) $("farben-vars").textContent = farben;

  /* ----- Startbildschirm mit Lade-Ente (dieselbe Ente wie in der Oberfläche und in der Konsole) ----- */
  const ENTE = ["    __   ", "___( o)> ", "\\_____/  "], W1 = "~~-~~~-~", W2 = "-.~-.~~ ", BREITE = 24;
  const spiegel = s => s.map(z => [...z].reverse().map(c => ({ "(": ")", ")": "(", "<": ">", ">": "<", "/": "\\", "\\": "/" }[c] || c)).join(""));
  const sprites = [ENTE, spiegel(ENTE)], spanne = BREITE - ENTE[0].length, weg = [];
  for (let x = 0; x <= spanne; x++) weg.push([x, 0]);
  for (let x = spanne; x >= 0; x--) weg.push([x, 1]);
  let schritt = 0, takt = null;
  const htmlZeichen = c => (c === "<" ? "&lt;" : c === ">" ? "&gt;" : c === "&" ? "&amp;" : c);
  function enteBild(k) {
    const [x, r] = weg[k % weg.length], wippen = Math.floor(k / 3) % 2;
    const z = Array.from({ length: 4 }, () => Array.from({ length: BREITE }, () => [" ", ""]));
    for (let i = 0; i < BREITE; i++) { z[2][i] = [W1[(i + k) % W1.length], "w1"]; z[3][i] = [W2[(((i - Math.floor(k / 2)) % W2.length) + W2.length) % W2.length], "w2"]; }
    sprites[r].forEach((zeile, j) => {
      const a = zeile.length - zeile.trimStart().length, e = zeile.trimEnd().length;
      for (let c = a; c < e; c++) z[wippen + j][x + c] = [zeile[c], zeile[c] === " " ? "" : "<>".includes(zeile[c]) ? "s" : zeile[c] === "o" ? "a" : ""];
    });
    return z.map(zl => zl.map(([c, k2]) => (k2 ? `<span class="${k2}">${htmlZeichen(c)}</span>` : htmlZeichen(c))).join("")).join("\n");
  }
  const ruhig = !!(window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches);
  function enteLos() { $("app-start-ente").innerHTML = enteBild(0); if (!ruhig && !takt) takt = setInterval(() => { $("app-start-ente").innerHTML = enteBild(++schritt); }, 100); }
  function status(text, anteil) {
    $("app-start-text").textContent = text + (anteil == null ? " …" : "");
    const b = $("app-start-balken");
    b.parentElement.hidden = anteil == null;
    if (anteil != null) b.style.width = Math.round(anteil * 100) + "%";
  }
  function fehler(text) {
    clearInterval(takt); takt = null;
    $("app-start").hidden = false; $("app-start").classList.remove("weg");
    $("app-start-text").textContent = text;
    $("app-start-balken").parentElement.hidden = true;
    const k = $("app-start-nochmal"); k.textContent = tt("nochmal"); k.hidden = false; k.onclick = () => location.reload();
  }
  enteLos(); status(tt("start"));

  /* ----- Verbindung zu Python (Web-Worker) ----- */
  let worker = null, bereitFertig, laufAktiv = false, laufStand = null, naechsteId = 1, uiGeladen = false, updateDa = false;
  const bereit = new Promise(r => { bereitFertig = r; });
  const offen = new Map(), gesichert = new Map();
  const unterbrechen = window.crossOriginIsolated && typeof SharedArrayBuffer === "function" ? new Uint8Array(new SharedArrayBuffer(1)) : null;
  const json = (status, daten) => ({ status, kopf: { "Content-Type": "application/json; charset=utf-8" },
    inhalt: new TextEncoder().encode(JSON.stringify(daten)).buffer });

  function anPython(m) {
    if (!worker) return Promise.resolve(json(503, { fehler: tt("umgezogen") }));
    return new Promise(fertig => { const id = naechsteId++; offen.set(id, fertig); worker.postMessage({ ...m, typ: "anfrage", id }); });
  }
  function sichern() {
    if (!worker) return Promise.resolve();
    return new Promise(fertig => { const id = naechsteId++; gesichert.set(id, fertig); worker.postMessage({ typ: "sichern", id }); setTimeout(fertig, 8000); });
  }
  function laufAntwort(abfrage) {                               // während Python rechnet: Fortschritt aus der letzten Meldung
    const q = new URLSearchParams(abfrage), id = q.get("id"), ab = +q.get("ab") || 0;
    if (!laufStand || (id && id !== laufStand.id)) return null;
    return json(200, { ...laufStand, zeilen: (laufStand.zeilen || []).slice(ab) });
  }
  async function beantworten(m, port) {
    port.postMessage({ typ: "angenommen" });
    let a = null;
    if (laufAktiv && m.methode === "GET" && m.weg === "/api/lauf") a = laufAntwort(m.abfrage);
    if (laufAktiv && m.methode === "POST" && m.weg === "/api/lauf-stopp") {
      if (unterbrechen) unterbrechen[0] = 2;                     // KeyboardInterrupt in Python → Auftrag abgebrochen
      a = json(200, { ok: !!unterbrechen });
    }
    if (!a) { await bereit; a = await anPython(m); }
    if (m.methode === "POST" && m.weg === "/api/sprache" && a.status === 200) {
      try { sprache = JSON.parse(new TextDecoder().decode(a.inhalt)).sprache || sprache; merke("mgd-sprache", sprache); } catch (f) { /* egal */ }
    }
    if (m.methode === "POST" && m.weg === "/api/farben" && a.status === 200) {
      try { const d = JSON.parse(new TextDecoder().decode(a.inhalt)); if (d.css != null) merke("mgd-farben", d.css); } catch (f) { /* egal */ }
    }
    port.postMessage(a, [a.inhalt]);
  }
  function workerNachricht(e) {
    const m = e.data;
    if (m.typ === "antwort") { const f = offen.get(m.id); offen.delete(m.id); if (f) f(m); return; }
    if (m.typ === "lauf") { try { laufStand = JSON.parse(m.json); laufAktiv = laufStand.code == null; } catch (f) { /* egal */ } return; }
    if (m.typ === "frei") { laufAktiv = false; return; }
    if (m.typ === "gesichert") { const f = gesichert.get(m.id); gesichert.delete(m.id); if (f) f(); return; }
    if (m.typ === "schritt") { status(tt(m.schritt)); return; }
    if (m.typ === "speicher") { if (window.toast) window.toast(tt("speicher"), { fehler: true }); return; }
    if (m.typ === "fehler") { fehler(tt("fehler", m.text)); return; }
    if (m.typ === "bereit") oberflaeche(m.info);
  }
  function oberflaeche(info) {
    sprache = info.sprache || sprache; merke("mgd-sprache", sprache);
    document.documentElement.lang = sprache;
    $("farben-vars").textContent = info.farben.css || ""; merke("mgd-farben", info.farben.css || "");
    document.querySelectorAll('meta[name="theme-color"]').forEach(x => x.remove());
    document.head.insertAdjacentHTML("beforeend", info.farben.meta || "");
    bereitFertig();
    const s = document.createElement("script");
    s.src = "ui.js";
    s.onload = () => {
      uiGeladen = true;
      clearInterval(takt); takt = null;
      $("app-start").classList.add("weg"); setTimeout(() => { $("app-start").hidden = true; }, 400);
      if (updateDa) window.dispatchEvent(new Event("mgd-update"));
      if (window.MGD_INSTALL) window.dispatchEvent(new Event("mgd-install"));
    };
    s.onerror = () => fehler(tt("fehler", "ui.js"));
    document.body.append(s);
    if (navigator.storage && navigator.storage.persist) navigator.storage.persist().catch(() => {});
  }

  /* ----- Ergebnisse in der App: Download-Links → Teilen/Speichern (iPhone-App kann keine neuen Tabs) ----- */
  const APP_ADRESSE = /^\/?((?:api|bild|datei)\/.*)$/;
  function dateiname(kopf, rel) {
    const m = /filename\*=UTF-8''([^;]+)/i.exec(kopf || "");
    if (m) { try { return decodeURIComponent(m[1]); } catch (f) { /* weiter */ } }
    return decodeURIComponent(rel.split("?")[0].split("/").pop() || "datei");
  }
  async function dateiHolen(rel, name) {
    if (window.enteGlobal) window.enteGlobal(1);
    try {
      const r = await fetch(rel);
      if (!r.ok) { let j = null; try { j = await r.json(); } catch (f) { /* kein JSON */ } throw new Error((j && j.fehler) || `HTTP ${r.status}`); }
      const blob = await r.blob();
      window.appDateiAnbieten(blob, name || dateiname(r.headers.get("content-disposition"), rel));
    } catch (f) { if (window.toast) window.toast(f.message, { fehler: true }); }
    finally { if (window.enteGlobal) window.enteGlobal(-1); }
  }
  document.addEventListener("click", e => {
    const a = e.target.closest && e.target.closest("a[href]"); if (!a || !uiGeladen) return;
    const m = APP_ADRESSE.exec(a.getAttribute("href") || ""); if (!m) return;
    if (!a.hasAttribute("download") && a.target !== "_blank") { a.setAttribute("href", m[1]); return; }   // innerhalb der App
    e.preventDefault();
    dateiHolen(m[1], a.getAttribute("download") || "");
  }, true);
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") sichern(); });
  window.addEventListener("pagehide", () => { sichern(); });
  window.addEventListener("beforeinstallprompt", e => {        // Android/Chrome: „App installieren“ selbst anbieten
    e.preventDefault(); window.MGD_INSTALL = e;
    if (uiGeladen) window.dispatchEvent(new Event("mgd-install"));
  });

  /* ----- Service Worker: Dateien aufs Gerät, Updates ----- */
  async function los() {
    if (!("serviceWorker" in navigator) || !window.isSecureContext || typeof WebAssembly !== "object") return fehler(tt("alt"));
    let reg;
    try { reg = await navigator.serviceWorker.register("sw.js", { scope: "./" }); }
    catch (f) { return fehler(tt("fehler", f.message || f)); }
    navigator.serviceWorker.addEventListener("message", e => {
      const m = e.data || {};
      if (m.typ === "api" && e.ports[0]) return beantworten(m, e.ports[0]);
      if (m.typ === "laden" && m.erste) status(tt("laden", mb(m.geladen), mb(m.gesamt)), m.gesamt ? m.geladen / m.gesamt : 0);
    });
    const meldeUpdate = () => {
      if (!navigator.serviceWorker.controller) return;
      updateDa = true; window.MGD_UPDATE = true;
      if (uiGeladen) window.dispatchEvent(new Event("mgd-update"));
    };
    window.MGD_NEU_LADEN = async () => {
      await sichern();
      if (reg.waiting) {
        navigator.serviceWorker.addEventListener("controllerchange", () => location.reload(), { once: true });
        reg.waiting.postMessage("weiter");
      } else location.reload();
    };
    reg.addEventListener("updatefound", () => {
      const neu = reg.installing; if (!neu) return;
      neu.addEventListener("statechange", () => { if (neu.state === "installed") meldeUpdate(); });
    });
    if (reg.waiting) meldeUpdate();
    if (!navigator.serviceWorker.controller) {                 // allererster Start: warten, bis alles am Gerät liegt
      await new Promise(r => navigator.serviceWorker.addEventListener("controllerchange", r, { once: true }));
      if (!window.crossOriginIsolated && !sessionStorage.getItem("mgd-neu")) {   // einmal neu laden → isoliert (Abbrechen)
        sessionStorage.setItem("mgd-neu", "1");
        return location.reload();
      }
    }
    setInterval(() => { if (document.visibilityState === "visible") reg.update().catch(() => {}); }, 30 * 60 * 1000);
    if (!(await sperren(false))) {                             // schon in einem anderen Fenster offen: nur eins rechnet
      clearInterval(takt); takt = null;
      $("app-start-text").textContent = tt("zweites");
      const k = $("app-start-nochmal"); k.textContent = tt("hier"); k.hidden = false;
      await new Promise(r => { k.onclick = r; });
      k.hidden = true; enteLos(); status(tt("start"));
      await sperren(true);
      await new Promise(r => setTimeout(r, 1200));             // das andere Fenster sichert noch
    }
    starteWorker();
  }
  /* Nur ein Fenster arbeitet mit den Daten (sonst überschreiben sich zwei Stände in IndexedDB) */
  function sperren(holen) {
    if (!navigator.locks) return Promise.resolve(true);
    return new Promise(ok => {
      navigator.locks.request("mgd-app", holen ? { steal: true } : { ifAvailable: true }, sperre => {
        if (!sperre) { ok(false); return null; }
        ok(true);
        return new Promise(() => {});                          // halten, solange das Fenster offen ist
      }).catch(() => umgezogen());                             // ein anderes Fenster hat übernommen
    });
  }
  async function umgezogen() {
    if (worker) { await sichern(); worker.terminate(); worker = null; }
    fehler(tt("umgezogen"));
    $("app-start-nochmal").textContent = tt("hier");
  }
  function starteWorker() {
    worker = new Worker("worker.js", { type: "module" });
    worker.onmessage = workerNachricht;
    worker.onerror = e => fehler(tt("fehler", (e && e.message) || "worker.js"));
    worker.postMessage({ typ: "start", unterbrechen, sprache });
  }
  los();
})();
