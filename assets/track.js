/* Event counting for GoatCounter (loaded only when site.yml sets `goatcounter`).
   Events appear in the GoatCounter dashboard under their names, e.g. "viewed-openings".
   Nothing is shown to visitors; GoatCounter sets no cookies. */
(function () {
  function count(name, title) {
    var gc = window.goatcounter;
    if (gc && gc.count) gc.count({ path: name, title: title || name, event: true });
  }

  // Sections reached: counted once per visit, when the section heading scrolls into view.
  var watch = [["res-h", "viewed-research"], ["pub-h", "viewed-publications"], ["openings", "viewed-openings"]];
  var pending = watch.slice(), ticking = false;
  function check() {
    ticking = false;
    pending = pending.filter(function (w) {
      var el = document.getElementById(w[0]);
      if (!el) return false;
      var r = el.getBoundingClientRect();
      if (r.top < window.innerHeight * 0.85 && r.bottom > 0) { count(w[1]); return false; }
      return true;
    });
    if (!pending.length) window.removeEventListener("scroll", onScroll);
  }
  function onScroll() { if (!ticking) { ticking = true; setTimeout(check, 250); } }
  window.addEventListener("scroll", onScroll, { passive: true });

  // Clicks.
  document.addEventListener("click", function (ev) {
    var a = ev.target.closest && ev.target.closest("a, button");
    if (!a) return;
    var href = a.getAttribute("href") || "";
    if (a.id === "bib-dl") return count("download-bibtex");
    if (href.indexOf("mailto:") === 0) return count("email-click");
    if (a.closest(".cv")) return count("open-cv");
    if (a.classList.contains("open-link")) return count("phd-program-link");
    if (a.tagName === "A" && a.closest("#pubs .pub")) {
      var b = a.closest(".pub").querySelector("b");
      var title = b ? b.textContent.trim().slice(0, 120) : "";
      var kind = a.classList.contains("chip") ? a.textContent.trim().toLowerCase() : "title";
      return count("paper-" + kind, title);
    }
    if (a.closest(".contact") && /^https?:/.test(href)) return count("profile-" + a.textContent.trim().toLowerCase().replace(/\s+/g, "-"));
  }, true);

  // Someone copying the email address from the "To apply" line.
  document.addEventListener("copy", function () {
    var s = String(window.getSelection ? window.getSelection() : "");
    if (s.indexOf("@") > -1) count("email-copied");
  });
})();
