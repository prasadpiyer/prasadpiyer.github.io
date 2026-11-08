"""Build index.html from the files in data/.

    python build.py

Edit the YAML files in data/ (news, people, research, site text), run this,
then commit index.html together with your data changes.

The Publications section is NOT built here: assets/publications.js renders it in
the browser from data/publications.json (plus optional data/publications_extra.json),
so replacing that JSON file updates the page without rebuilding.
"""
import json
import re
from datetime import date, datetime
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parent
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def load(name):
    return yaml.safe_load((ROOT / "data" / f"{name}.yml").read_text(encoding="utf-8"))


def month(value):
    s = str(value)
    m = re.match(r"(\d{4})-(\d{1,2})", s)
    return f"{MONTHS[int(m.group(2)) - 1]} {m.group(1)}" if m else s


def initials(name):
    parts = [p for p in re.sub(r"^(Dr|Prof)\.?\s+", "", name).split() if p[0].isalpha()]
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else name[:2].upper()


def check_publications():
    """Warn (don't fail) if the publications file is missing or malformed."""
    path = ROOT / "data" / "publications.json"
    try:
        pubs = json.loads(path.read_text(encoding="utf-8"))
        missing = [i for i, p in enumerate(pubs) if not all(k in p for k in ("title", "auth", "venue", "year", "typ"))]
        if missing:
            print(f"Warning: {len(missing)} publication entries lack a required field (first index {missing[0]}).")
        return len(pubs)
    except Exception as e:  # noqa: BLE001
        print(f"Warning: could not read {path.relative_to(ROOT)}: {e}")
        return 0


def _norm(t):
    t = re.sub(r"\((conference presentation|presentation recording)\)", "", str(t or "").lower())
    return re.sub(r"[^a-z0-9]", "", t)


def load_publications():
    """publications.json with the "patch" corrections from publications_extra.json applied
    (the same rule the browser uses), so key papers show corrected venues and links."""
    try:
        pubs = json.loads((ROOT / "data" / "publications.json").read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return []
    try:
        extras = json.loads((ROOT / "data" / "publications_extra.json").read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        extras = []
    control = {"patch", "fill", "title", "match_typ", "match_venue", "note", "source"}
    for x in extras:
        if not (x.get("patch") or x.get("fill")):
            continue
        for p in pubs:
            if _norm(p.get("title")) != _norm(x.get("title")):
                continue
            if x.get("match_typ") and p.get("typ") != x["match_typ"]:
                continue
            if x.get("match_venue") and _norm(p.get("venue")) != _norm(x["match_venue"]):
                continue
            for k, v in x.items():
                if k not in control and (x.get("patch") or not str(p.get(k) or "").strip()):
                    p[k] = v
    pubs += [x for x in extras if not (x.get("patch") or x.get("fill"))]
    return pubs


def key_papers(titles, pubs):
    """Resolve the titles listed under `papers:` in research.yml to linked entries."""
    rank = {"journal": 0, "conference": 1, "preprint": 2}
    out = []
    for t in titles or []:
        hits = sorted((p for p in pubs if _norm(p.get("title")) == _norm(t)),
                      key=lambda p: rank.get(p.get("typ"), 9))
        if not hits:
            print(f"Warning: key paper not found in publications.json: {t[:70]}")
            continue
        p = hits[0]
        doi = str(p.get("doi") or "").strip()
        url = p.get("url") or (f"https://doi.org/{doi}" if doi else "")
        venue = re.sub(r"\s+\d+\s*\(.*$", "", str(p.get("venue") or "")).strip()   # drop volume/pages
        venue = re.sub(r"^arXiv preprint arXiv:.*$", "arXiv preprint", venue)
        venue = re.sub(r",\s*\d+$", "", venue)                                     # trailing article number
        venue = re.sub(r"^.*\((NeurIPS) \d{4}\)$", r"\1", venue)                  # "... (NeurIPS 2026)" -> "NeurIPS"
        out.append({"title": re.sub(r"\s*\((Conference Presentation|Presentation Recording)\)\s*$", "", p["title"]),
                    "url": url, "venue": venue, "year": p.get("year", "")})
    return out


def main():
    site, people, research = load("site"), load("people"), load("research")
    # newest first; items marked `pinned: true` stay at the top
    news = sorted(load("news"), key=lambda n: (bool(n.get("pinned")), str(n["date"])), reverse=True)
    scholar = next((l["url"] for l in site["links"] if "Scholar" in l["label"]), "#")
    site.setdefault("selected_publications", [])

    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=True,
                      undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    env.filters.update(month=month, initials=initials)
    # optional keys may be missing in the YAML; StrictUndefined would reject them
    for group in (people.get("current", []), people.get("former", []), people.get("collaborators", [])):
        for p in group:
            for k in ("photo", "role", "note"):
                p.setdefault(k, "")
    people["pi"].setdefault("cv_url", "")
    for o in people.get("openings", []):
        o.setdefault("skills", []); o.setdefault("note", "")
    for n in news:
        n.setdefault("url", "")
        n.setdefault("pinned", False)
    pubs = load_publications()
    for r in research:
        r.setdefault("image", ""); r.setdefault("alt", ""); r.setdefault("wide", False)
        r["key_papers"] = key_papers(r.get("papers"), pubs)
    for o in people.get("openings", []):
        o.setdefault("start", ""); o.setdefault("links", [])
    for f in site.setdefault("funders", []):
        f.setdefault("url", ""); f.setdefault("note", "")

    html = env.get_template("index.html.j2").render(
        site=site, people=people, research=research, news=news,
        scholar_url=scholar, year=date.today().year,
        updated=f"{MONTHS[date.today().month - 1]} {date.today().year}",
        build_id=datetime.now().strftime("%Y%m%d%H%M"),
    )
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    n = check_publications()
    print(f"Wrote index.html · {len(news)} news · {n} entries in data/publications.json")


if __name__ == "__main__":
    main()
