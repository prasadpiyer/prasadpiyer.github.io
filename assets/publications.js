/* Publications section, rendered in the browser from data/publications.json.
   Replace that file (same fields) and the page updates; no code changes needed.
   Optional data/publications_extra.json adds entries Google Scholar doesn't know about.

   Entry fields: title, auth (full author list), venue, year, typ
   (journal | conference | preprint | patent | report | thesis | talk),
   optional url, doi, pdf, arxiv, abstract. */
(function () {
  "use strict";
  var root = document.getElementById("pubs");
  if (!root) return;

  var TYPES = [
    ["journal", "Journal"], ["conference", "Conference"], ["preprint", "Preprint"],
    ["patent", "Patent"], ["report", "Report"], ["thesis", "Thesis"], ["talk", "Talk"]
  ];
  var LABEL = {};
  TYPES.forEach(function (t) { LABEL[t[0]] = t[1]; });

  // Every form of the PI's name: Prasad P Iyer, Prasad P. Iyer, Prasad Iyer,
  // Prasad Padmanabha Iyer, PP Iyer, P. P. Iyer, P Iyer, P. Iyer, Iyer, P. P.
  var ME = /(Prasad\s+(?:P\.?\s*|Padmanabha\s+)?Iyer|\bP\.?\s?P\.?\s+Iyer|\bP\.?\s+Iyer|Iyer,\s*P(?:rasad)?\.?(?:\s*P(?:admanabha)?\.?)?)/g;

  var selectedTitles = [];
  try { selectedTitles = JSON.parse(root.getAttribute("data-selected") || "[]"); } catch (e) { /* none */ }
  var scholar = root.getAttribute("data-scholar") || "#";

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function norm(s) { return String(s || "").toLowerCase().replace(/[^a-z0-9]/g, ""); }
  function safeUrl(u) { return /^https?:\/\//i.test(u || "") ? u : ""; }
  function doiUrl(d) {
    d = String(d || "").trim().replace(/^https?:\/\/(dx\.)?doi\.org\//i, "").replace(/^doi:\s*/i, "");
    return d ? "https://doi.org/" + d : "";
  }
  function arxivUrl(a) {
    a = String(a || "").trim();
    if (/^https?:\/\//i.test(a)) return a;
    a = a.replace(/^arxiv:\s*/i, "");
    return a ? "https://arxiv.org/abs/" + a : "";
  }
  function authors(s) { return esc(s).replace(ME, "<strong>$1</strong>"); }

  // Scholar text sometimes carries HTML entities (&lt;sup&gt;) or inline LaTeX ($g^{(2)}(0)$).
  function decodeEntities(s) {
    var t = document.createElement("textarea");
    t.innerHTML = String(s || "");
    return t.value;
  }
  var TEX = { "\\approx": "≈", "\\sim": "~", "\\times": "×", "\\pm": "±", "\\mu": "μ", "\\Delta": "Δ",
    "\\lambda": "λ", "\\leq": "≤", "\\geq": "≥", "\\le": "≤", "\\ge": "≥", "\\%": "%", "\\cdot": "·" };
  function richText(s) {
    var h = esc(decodeEntities(s));
    // allow only <sup>/<sub> through
    h = h.replace(/&lt;(\/?)(sup|sub)&gt;/gi, "<$1$2>");
    // simple inline LaTeX: $...$
    h = h.replace(/\$([^$]{1,120})\$/g, function (_, m) {
      m = m.replace(/\\(?:text|mathrm|mathcal|mathbf|mathit)\{([^}]*)\}/g, "$1");
      Object.keys(TEX).forEach(function (k) { m = m.split(k).join(TEX[k]); });
      m = m.replace(/\^\{([^}]*)\}/g, "<sup>$1</sup>").replace(/_\{([^}]*)\}/g, "<sub>$1</sub>")
           .replace(/\^(\S)/g, "<sup>$1</sup>").replace(/_(\S)/g, "<sub>$1</sub>")
           .replace(/\\[a-zA-Z]+/g, "").replace(/[{}]/g, "");
      return m;
    });
    return h;
  }
  function cleanTitle(t) {
    return decodeEntities(t).replace(/\s*\((Conference Presentation|Presentation Recording)\)\s*$/i, "");
  }

  function entryHtml(p, i) {
    var url = safeUrl(p.url), doi = doiUrl(p.doi), pdf = safeUrl(p.pdf), ax = arxivUrl(p.arxiv);
    if (pdf && doi && pdf.toLowerCase() === doi.toLowerCase()) pdf = ""; // same page as DOI, not a PDF
    var t = cleanTitle(p.title);
    var title = url ? '<a href="' + esc(url) + '">' + esc(t) + "</a>" : esc(t);
    var chips = "";
    if (doi) chips += '<a class="chip" href="' + esc(doi) + '">DOI</a>';
    if (pdf) chips += '<a class="chip" href="' + esc(pdf) + '">PDF</a>';
    if (ax) chips += '<a class="chip" href="' + esc(ax) + '">arXiv</a>';
    var abs = p.abstract
      ? '<details class="abs"><summary>Abstract</summary><p>' + richText(p.abstract) + "</p></details>"
      : "";
    return '<div class="pub">' +
      "<b>" + title + "</b>" +
      (p.auth ? '<span class="au">' + authors(p.auth) + "</span>" : "") +
      '<span class="ven">' + (p.venue ? "<i>" + esc(decodeEntities(p.venue)) + "</i> · " : "") +
      '<span class="typ">' + esc(LABEL[p.typ] || p.typ || "") + "</span></span>" +
      (chips || abs ? '<div class="pub-actions">' + chips + abs + "</div>" : "") +
      "</div>";
  }

  function byYear(list) {
    var groups = [], idx = {};
    list.forEach(function (p) {
      var y = p.year || "Undated";
      if (!(y in idx)) { idx[y] = groups.length; groups.push([y, []]); }
      groups[idx[y]][1].push(p);
    });
    groups.sort(function (a, b) {
      if (a[0] === "Undated") return 1;
      if (b[0] === "Undated") return -1;
      return b[0] - a[0];
    });
    return groups;
  }

  function pickSelected(all) {
    var rank = { journal: 0, conference: 1, preprint: 2 };
    return selectedTitles.map(function (t) {
      var hits = all.filter(function (p) { return norm(p.title) === norm(t); });
      hits.sort(function (a, b) { return (rank[a.typ] ?? 9) - (rank[b.typ] ?? 9); });
      return hits[0];
    }).filter(Boolean);
  }

  function render(all) {
    var selected = pickSelected(all);
    var counts = {};
    all.forEach(function (p) { counts[p.typ] = (counts[p.typ] || 0) + 1; });

    var tabs = [];
    if (selected.length) tabs.push(["selected", "Selected", selected.length]);
    tabs.push(["all", "All", all.length]);
    TYPES.forEach(function (t) { if (counts[t[0]]) tabs.push([t[0], t[1], counts[t[0]]]); });

    var current = selected.length ? "selected" : "all";
    try {
      var saved = sessionStorage.getItem("pubs-tab");
      if (saved && tabs.some(function (t) { return t[0] === saved; })) current = saved;
    } catch (e) { /* storage unavailable */ }

    root.innerHTML =
      '<div class="tabs" role="tablist" aria-label="Filter publications by type">' +
      tabs.map(function (t) {
        return '<button type="button" role="tab" data-tab="' + t[0] + '">' +
          esc(t[1]) + ' <span class="n">' + t[2] + "</span></button>";
      }).join("") + "</div>" +
      '<p class="pub-count" aria-live="polite"></p>' +
      '<div class="pub-list"></div>';

    var listEl = root.querySelector(".pub-list");
    var countEl = root.querySelector(".pub-count");

    function show(tab) {
      current = tab;
      try { sessionStorage.setItem("pubs-tab", tab); } catch (e) { /* ignore */ }
      root.querySelectorAll("[data-tab]").forEach(function (b) {
        var on = b.getAttribute("data-tab") === tab;
        b.setAttribute("aria-selected", on ? "true" : "false");
        b.classList.toggle("on", on);
      });
      var items = tab === "selected" ? selected
        : tab === "all" ? all
        : all.filter(function (p) { return p.typ === tab; });
      countEl.textContent = tab === "selected"
        ? "Selected publications"
        : "Showing " + items.length + " of " + all.length + " entries";
      listEl.innerHTML = byYear(items).map(function (g) {
        return '<div class="yr">' + esc(g[0]) + "</div>" + g[1].map(entryHtml).join("");
      }).join("");
    }

    root.querySelector(".tabs").addEventListener("click", function (ev) {
      var b = ev.target.closest("[data-tab]");
      if (b) show(b.getAttribute("data-tab"));
    });
    show(current);

    var bib = document.getElementById("bib-dl");
    if (bib) {
      bib.hidden = false;
      bib.addEventListener("click", function () { downloadBib(all); });
    }
  }

  // ---- BibTeX download, generated from the same data ----
  function bibEsc(s) { return String(s || "").replace(/[{}]/g, "").replace(/&/g, "\\&").replace(/%/g, "\\%"); }
  function downloadBib(all) {
    var seen = {}, out = ["% Publications of Prasad P. Iyer · Light–Matter Information Lab", ""];
    all.forEach(function (p) {
      var names = String(p.auth || "").split(/\s*,\s*|\s+and\s+/).filter(Boolean);
      var last = names.length ? names[0].split(/\s+/).pop().toLowerCase().replace(/[^a-z]/g, "") : "iyer";
      var word = (String(p.title).toLowerCase().match(/[a-z]{4,}/) || ["work"])[0];
      var key = last + (p.year || "") + word;
      while (seen[key]) key += "b";
      seen[key] = 1;
      var type = { journal: "article", conference: "inproceedings", thesis: "phdthesis", report: "techreport" }[p.typ] || "misc";
      var f = [["title", cleanTitle(p.title)], ["author", names.join(" and ")], ["year", p.year]];
      if (type === "article") f.push(["journal", p.venue]);
      else if (type === "inproceedings") f.push(["booktitle", p.venue]);
      else if (type === "phdthesis") f.push(["school", p.venue]);
      else if (type === "techreport") f.push(["institution", p.venue]);
      else f.push(["howpublished", p.venue]);
      if (p.arxiv) f.push(["eprint", String(p.arxiv).replace(/^.*abs\//, "")], ["archivePrefix", "arXiv"]);
      var d = doiUrl(p.doi);
      if (d) f.push(["doi", d.replace("https://doi.org/", "")]);
      if (safeUrl(p.url)) f.push(["url", p.url]);
      out.push("@" + type + "{" + key + ",\n" + f.filter(function (x) { return x[1] !== "" && x[1] != null; })
        .map(function (x) { return "  " + x[0] + " = {" + bibEsc(x[1]) + "}"; }).join(",\n") + "\n}\n");
    });
    var blob = new Blob([out.join("\n")], { type: "application/x-bibtex" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "Iyer_publications.bib";
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
  }

  function load(path, optional) {
    return fetch(path, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) { if (optional) return []; throw new Error(path + " returned " + r.status); }
      return r.json();
    }).catch(function (e) { if (optional) return []; throw e; });
  }

  var src = root.getAttribute("data-src") || "data/publications.json";
  var extra = root.getAttribute("data-extra");
  Promise.all([load(src, false), extra ? load(extra, true) : Promise.resolve([])])
    .then(function (res) {
      var main = Array.isArray(res[0]) ? res[0] : [];
      var extras = Array.isArray(res[1]) ? res[1] : [];
      // 1) "patch" entries overwrite fields on matching entries (same title; same typ if given);
      //    "fill" entries only fill fields that are empty in publications.json.
      var CONTROL = ["patch", "fill", "title", "match_typ", "note", "source"];
      extras.filter(function (x) { return x.patch || x.fill; }).forEach(function (x) {
        main.forEach(function (p) {
          if (norm(cleanTitle(p.title)) !== norm(cleanTitle(x.title))) return;
          if (x.match_typ && p.typ !== x.match_typ) return;
          Object.keys(x).forEach(function (k) {
            if (CONTROL.indexOf(k) >= 0) return;
            if (x.patch || p[k] == null || String(p[k]).trim() === "") p[k] = x[k];
          });
        });
      });
      // 2) exact duplicates (same title, venue, year and type) are shown once
      var seen = {};
      main = main.filter(function (p) {
        var key = [norm(cleanTitle(p.title)), norm(p.venue), p.year, p.typ].join("|");
        if (seen[key]) return false;
        seen[key] = 1; return true;
      });
      // 3) everything else in the extras file is a new entry
      var add = extras.filter(function (x) {
        return !x.patch && !x.fill && !main.some(function (p) { return norm(p.title) === norm(x.title) && p.typ === x.typ; });
      });
      // keep the file's own order (newest first); extras slot into their year
      render(main.concat(add).map(function (p, i) { p._i = i; return p; })
        .sort(function (a, b) { return (b.year || 0) - (a.year || 0) || a._i - b._i; }));
    })
    .catch(function () {
      root.innerHTML = '<p class="pub-count">The publication list could not be loaded. ' +
        'See the full list on <a href="' + esc(scholar) + '">Google Scholar</a>.</p>';
    });
})();
