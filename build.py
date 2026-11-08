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


def main():
    site, people, research = load("site"), load("people"), load("research")
    news = sorted(load("news"), key=lambda n: str(n["date"]), reverse=True)
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
    for n in news:
        n.setdefault("url", "")
    for r in research:
        r.setdefault("image", ""); r.setdefault("alt", "")

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
