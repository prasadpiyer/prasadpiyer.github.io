"""Build index.html from the files in data/.

    python build.py

Edit the YAML files in data/ (news, people, research, site text), run this,
then commit index.html together with your data changes.
"""
import re
from collections import OrderedDict
from datetime import date, datetime
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup, escape

ROOT = Path(__file__).resolve().parent
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
PI_NAMES = re.compile(r"(Prasad\s+(?:P\.?\s+|Padmanabha\s+)?Iyer|P\.\s*P\.\s*Iyer|Iyer,\s*P(?:rasad)?\.?\s*P?\.?)")


def load(name):
    return yaml.safe_load((ROOT / "data" / f"{name}.yml").read_text(encoding="utf-8"))


def month(value):
    s = str(value)
    m = re.match(r"(\d{4})-(\d{1,2})", s)
    return f"{MONTHS[int(m.group(2)) - 1]} {m.group(1)}" if m else s


def bold_pi(authors):
    return Markup(PI_NAMES.sub(lambda m: f"<strong>{m.group(0)}</strong>", str(escape(authors))))


def initials(name):
    parts = [p for p in re.sub(r"^(Dr|Prof)\.?\s+", "", name).split() if p[0].isalpha()]
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else name[:2].upper()


def by_year(items):
    groups = OrderedDict()
    for p in sorted(items, key=lambda p: str(p.get("date") or ""), reverse=True):
        groups.setdefault(p.get("year") or "Undated", []).append(p)
    return list(groups.items())


def main():
    site, people, research = load("site"), load("people"), load("research")
    news = sorted(load("news"), key=lambda n: str(n["date"]), reverse=True)
    pubs = load("publications")

    papers = [p for p in pubs if p.get("kind") in ("paper", "preprint")]
    talks = [p for p in pubs if p.get("kind") == "talk"]
    patents = [p for p in pubs if p.get("kind") == "patent"]
    scholar = next((l["url"] for l in site["links"] if "Scholar" in l["label"]), "#")

    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=True,
                      undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    env.filters.update(month=month, bold_pi=bold_pi, initials=initials)
    # optional keys may be missing in the YAML; StrictUndefined would reject them
    for group in (people.get("current", []), people.get("former", []), people.get("collaborators", [])):
        for p in group:
            for k in ("photo", "role", "note"):
                p.setdefault(k, "")
    people["pi"].setdefault("cv_url", "")
    for n in news:
        n.setdefault("url", "")
    for p in pubs:
        for k in ("url", "authors", "venue", "invited"):
            p.setdefault(k, "")
    for r in research:
        r.setdefault("image", "")

    html = env.get_template("index.html.j2").render(
        site=site, people=people, research=research, news=news,
        selected=by_year([p for p in papers if p.get("selected")]),
        papers=by_year(papers), talks=by_year(talks), patents=by_year(patents),
        papers_count=len(papers), talks_count=len(talks), patents_count=len(patents),
        scholar_url=scholar, year=date.today().year,
        updated=f"{MONTHS[date.today().month - 1]} {date.today().year}",
        build_id=datetime.now().strftime("%Y%m%d%H%M"),
    )
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print(f"Wrote index.html · {len(news)} news · {len(papers)} papers · {len(talks)} talks · {len(patents)} patents")


if __name__ == "__main__":
    main()
