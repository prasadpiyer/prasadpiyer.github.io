"""Merge a Google Scholar BibTeX export into data/publications.yml.

How to get the export:
  1. Open your Google Scholar profile.
  2. Tick the checkbox at the top of the article list to select all articles.
  3. Click Export -> BibTeX and save the file (for example as scholar.bib).

Then run:
  python tools/import_scholar.py scholar.bib            # merge and save
  python tools/import_scholar.py scholar.bib --dry-run  # only show what would change

Entries already in data/publications.yml keep anything you edited by hand
(selected, url, venue). New papers are added; missing fields are filled in;
a preprint is upgraded when its published version appears.
"""
import argparse
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

import yaml
import pybtex.errors
from pybtex.database.input import bibtex

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "publications.yml"

TALK_HINTS = ("spie", "cleo", "conference", "optics infobase", "proceedings", "meeting",
              "presentation", "symposium", "workshop", "frontiers in optics")
LATEX = {r"\textendash": "–", r"\textemdash": "—", r"\&": "&", "--": "–"}


def norm(title):
    title = re.sub(r"\((conference presentation|presentation recording)\)", "", (title or "").lower())
    return re.sub(r"[^a-z0-9]", "", title)


def clean(text):
    text = text or ""
    for k, v in LATEX.items():
        text = text.replace(k, v)
    text = re.sub(r"\\[a-zA-Z]+\s*", "", text)  # drop any other LaTeX commands
    text = re.sub(r"[{}]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def person_name(p):
    first = " ".join(p.first_names + p.middle_names)
    last = " ".join(p.prelast_names + p.last_names)
    return clean(f"{first} {last}")


def classify(entry, venue):
    v = venue.lower()
    if entry.type == "patent" or "patent" in v:
        return "patent"
    if "arxiv" in v or "preprint" in v:
        return "preprint"
    # full peer-reviewed conference papers count as publications, not talks
    if any(h in v for h in ("aaai", "neurips", "neural information processing", "wacv", "computer vision", "icml", "iclr")):
        return "paper"
    if "dissertation" in v or "thesis" in v or "university of" in v:
        return "paper"
    if "sandia national laboratories" in v or "los alamos national laboratory" in v:
        return "report"  # lab technical reports are not listed on the site
    if entry.type == "inproceedings" or any(h in v for h in TALK_HINTS):
        return "talk"
    return "paper"


def from_bib(path):
    pybtex.errors.set_strict_mode(False)  # Scholar exports often repeat keys
    db = bibtex.Parser().parse_file(str(path))
    out = []
    for entry in db.entries.values():
        f = entry.fields
        title = clean(f.get("title", ""))
        if not title:
            continue
        if entry.type == "techreport":
            continue  # skip Sandia / Los Alamos technical reports
        venue = clean(f.get("journal") or f.get("booktitle") or f.get("howpublished")
                      or f.get("publisher") or f.get("note") or "")
        if entry.type == "phdthesis":
            venue = "PhD dissertation, " + clean(f.get("school", ""))
        year = f.get("year", "")
        e = {
            "title": title,
            "authors": ", ".join(person_name(p) for p in entry.persons.get("author", [])),
            "venue": venue,
            "date": f"{year}-01-01" if year.isdigit() else "",
            "year": int(year) if year.isdigit() else None,
            "kind": classify(entry, venue),
        }
        if f.get("doi"):
            e["url"] = "https://doi.org/" + f["doi"].strip()
        elif f.get("url"):
            e["url"] = f["url"].strip()
        if e["kind"] == "report":
            continue  # skip Sandia / Los Alamos technical reports
        if entry.type == "misc" and not venue:
            e["check"] = "Scholar gave no venue; confirm whether this is a paper, talk or patent"
        out.append(e)
    return out


def group(kind):
    # papers and preprints of the same work belong together; talks and patents are separate
    return "paper" if kind in ("paper", "preprint") else kind


def find(existing, new):
    """Find the same work already in the list, allowing small title differences."""
    key = norm(new["title"])
    best, best_score = None, 0.0
    for e in existing:
        score = 1.0 if norm(e["title"]) == key else SequenceMatcher(None, norm(e["title"]), key).ratio()
        if group(e.get("kind")) == group(new["kind"]):
            score += 0.01  # prefer a same-kind match when a talk and a paper share a title
        if score > best_score:
            best, best_score = e, score
    return best if best_score >= 0.88 else None


def n_authors(s):
    return len([a for a in (s or "").split(",") if a.strip()])


def merge(existing, incoming, refresh_authors=False):
    added, updated = [], []
    for new in incoming:
        old = find(existing, new)
        if old is None:
            existing.append(new)
            added.append(new)
            continue
        if group(old.get("kind")) != group(new["kind"]):
            continue  # same title as a talk/patent we already list; leave it alone
        changed = False
        # Replace an author list that was cut short ("et al.") or, on request, any list,
        # when the export has at least as many names.
        if new.get("authors") and new["authors"] != old.get("authors") and (
                refresh_authors or "et al" in (old.get("authors") or "")) and \
                n_authors(new["authors"]) >= n_authors((old.get("authors") or "").replace(" et al.", "")):
            old["authors"] = new["authors"]
            changed = True
        if old.get("kind") == "preprint" and new["kind"] == "paper":
            old["kind"], old["venue"] = "paper", new["venue"]
            if new.get("year"):
                old["year"], old["date"] = new["year"], new["date"]
            changed = True
        for k in ("authors", "venue", "url", "year", "date"):
            if not old.get(k) and new.get(k):
                old[k] = new[k]
                changed = True
        if changed:
            updated.append(old)
    existing.sort(key=lambda e: e.get("date") or "", reverse=True)
    return added, updated


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bibfile", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--refresh-authors", action="store_true",
                    help="replace author lists with the export's full names")
    args = ap.parse_args()

    text = DATA.read_text(encoding="utf-8")
    header = "".join(l for l in text.splitlines(keepends=True) if l.startswith("#"))
    existing = yaml.safe_load(text) or []
    added, updated = merge(existing, from_bib(args.bibfile), args.refresh_authors)

    for e in added:
        print(f"+ {e['kind']:8} {e.get('year') or '----'}  {e['title'][:90]}")
    for e in updated:
        print(f"~ {e['kind']:8} {e.get('year') or '----'}  {e['title'][:90]}")
    print(f"\n{len(added)} added, {len(updated)} updated, {len(existing)} total.")

    if args.dry_run:
        print("Dry run: nothing saved.")
        return
    DATA.write_text(header + yaml.safe_dump(existing, sort_keys=False, allow_unicode=True, width=1000), encoding="utf-8")
    print(f"Saved {DATA.relative_to(ROOT)}. Run `python build.py` to update the page.")


if __name__ == "__main__":
    sys.exit(main())
