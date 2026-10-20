/* Me Goos-ta Deutsch – Download-Seite (gebaut von bau_webapp.py). Sprache EN · DE · ES (Anker #de/#es/#en, sonst die
   gemerkte Wahl, sonst Englisch – nie die Gerätesprache) und System (Knopf + Schritte). Ohne dieses Skript zeigt die
   Seite Englisch und alle drei Systeme. Keine Anfragen, kein Tracking. */
(function () {
  "use strict";
  var h = document.documentElement, SPRACHEN = ["en", "de", "es"], SCHLUESSEL = "mgd-download-sprache";
  function gemerkt() { try { return localStorage.getItem(SCHLUESSEL); } catch (e) { return null; } }
  function merken(l) { try { localStorage.setItem(SCHLUESSEL, l); } catch (e) { /* privates Fenster: dann eben nicht */ } }
  function anker() { var a = (location.hash || "").slice(1).toLowerCase(); return SPRACHEN.indexOf(a) >= 0 ? a : null; }
  function system() {
    var ua = navigator.userAgent || "", p = (navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || "";
    if (/Android|iPhone|iPad|iPod/i.test(ua) || (/Mac/i.test(p) && navigator.maxTouchPoints > 1)) return "handy";
    if (/Win/i.test(p) || /Windows/i.test(ua)) return "win";
    if (/Mac/i.test(p) || /Mac OS X/i.test(ua)) return "mac";
    if (/Linux|X11|CrOS/i.test(p + " " + ua)) return "linux";
    return "";
  }
  function sprache(l) {
    var s = document.getElementById(l); if (!s) return;
    h.setAttribute("data-sprache", l); h.lang = l;
    document.title = s.getAttribute("data-titel") || document.title;
  }
  function os(o) {
    if (o) h.setAttribute("data-os", o); else h.removeAttribute("data-os");
    var k = document.querySelectorAll(".os-wahl [data-os-wahl]");
    for (var i = 0; i < k.length; i++) k[i].setAttribute("aria-pressed", String(k[i].getAttribute("data-os-wahl") === o));
  }
  var geraet = system(), i, liste;
  h.classList.add("js");
  var g = gemerkt();
  sprache(anker() || (SPRACHEN.indexOf(g) >= 0 ? g : "en"));
  os(geraet === "handy" ? "" : geraet);
  liste = document.querySelectorAll("[data-nur-js]");
  for (i = 0; i < liste.length; i++) liste[i].hidden = false;
  if (geraet === "handy") {
    liste = document.querySelectorAll("[data-nur-handy]");
    for (i = 0; i < liste.length; i++) liste[i].hidden = false;
  }
  document.addEventListener("click", function (e) {
    var z = e.target && e.target.closest ? e.target.closest("[data-l], [data-os-wahl]") : null;
    if (!z) return;
    if (z.hasAttribute("data-l")) {
      e.preventDefault();
      var l = z.getAttribute("data-l");
      sprache(l); merken(l);
      try { history.replaceState(null, "", "#" + l); } catch (f) { /* z. B. als Datei geöffnet */ }
      var neu = document.querySelector("#" + l + " nav [data-l='" + l + "']");
      if (neu) neu.focus();
    } else os(z.getAttribute("data-os-wahl"));
  });
  window.addEventListener("hashchange", function () { var l = anker(); if (l) { sprache(l); merken(l); } });
})();
