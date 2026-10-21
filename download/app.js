/* Me Goos-ta Deutsch – Rettung der Download-Seite (gebaut von bau_webapp.py). Läuft nur, wenn ein Service Worker der
   App von vor 2.1 hier den Startbildschirm der App zeigt: neue Version übernehmen bzw. alten Service Worker abmelden,
   dann neu laden. Nutzerdaten der App bleiben. */
(function () {
  "use strict";
  var TEXT = { en: "Shooing out an old app version – the download page opens in a moment.",
    de: "Eine alte App-Version watschelt gerade hinaus – gleich öffnet sich die Download-Seite.",
    es: "Una versión antigua de la app se va contoneando – la página de descarga se abre en un momento." };
  var ZAEHLER = "mgd-download-rettung", l = (location.hash || "").slice(1).toLowerCase(), versuche = 0, fertig = false;
  if (!TEXT[l]) { try { l = localStorage.getItem("mgd-download-sprache"); } catch (e) { l = null; } }
  if (!TEXT[l]) l = "en";
  document.documentElement.lang = l;
  var feld = document.getElementById("app-start-text"), bild = document.querySelector("#app-start img");
  if (feld) feld.textContent = TEXT[l] + " 🪿";
  if (bild) bild.src = "../symbol.svg";
  try { versuche = Number(sessionStorage.getItem(ZAEHLER)) || 0; sessionStorage.setItem(ZAEHLER, String(versuche + 1)); }
  catch (e) { versuche = 0; }
  function neu() { if (!fertig && versuche < 3) { fertig = true; location.reload(); } }
  var sw = navigator.serviceWorker;
  if (!sw) return neu();
  sw.addEventListener("controllerchange", neu);
  sw.getRegistration().then(function (reg) {
    if (!reg) return neu();
    if (versuche >= 1) return reg.unregister().then(neu, neu);   // Übergabe hat nicht gereicht: alten abmelden
    function weiter(w) { if (w) w.postMessage("weiter"); }
    weiter(reg.waiting);
    reg.addEventListener("updatefound", function () {
      var w = reg.installing;
      if (w) w.addEventListener("statechange", function () { if (w.state === "installed") weiter(w); });
    });
    reg.update().catch(function () { /* offline: dann gleich abmelden */ reg.unregister().then(neu, neu); });
    setTimeout(function () { reg.unregister().then(neu, neu); }, 20000);
  }, neu);
})();
