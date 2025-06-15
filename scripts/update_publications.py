import re
import os
import yaml
from datetime import datetime
from collections import defaultdict
from pathlib import Path
from pybtex.database.input import bibtex

"""Regenerate markdown files in _publications/ using the cleaned BibTeX file.
Existing markdown files are merged so that any abstract/excerpt you wrote by
hand are preserved unless the new BibTeX supplies that data.

Usage:
    python scripts/update_publications.py files/deduped_bibtex1.bib
"""

PUB_DIR = Path(__file__).resolve().parents[1] / "_publications"

FRONT_MATTER_PATTERN = re.compile(r"^---\n(.*?)\n---\n", re.S)

def load_existing_markdown():
    """Return dict mapping slug->{data, body, filename}."""
    existing = {}
    for md_path in PUB_DIR.glob("*.md"):
        text = md_path.read_text(encoding="utf-8")
        m = FRONT_MATTER_PATTERN.match(text)
        if not m:
            continue
        meta = yaml.safe_load(m.group(1)) or {}
        slug = md_path.stem.split("-", 3)[-1]  # after date prefix
        existing[slug] = {
            "meta": meta,
            "body": text[m.end():].lstrip(),
            "path": md_path
        }
    return existing


def bib_to_markdown(entry, collection, venue_pretext=""):
    b = entry.fields
    year = b.get("year", "1900")
    month = b.get("month", "01")
    if len(month) < 3 and month.isdigit():
        month = f"{int(month):02d}"
    else:
        try:
            month = f"{datetime.strptime(month[:3], '%b').month:02d}"
        except Exception:
            month = "01"
    day = b.get("day", "01")
    date = f"{year}-{month}-{day}"

    title_clean = re.sub(r"[{}\\]", "", b["title"])
    slug_base = re.sub(r"\s+", "-", title_clean.strip())
    slug = re.sub(r"[^A-Za-z0-9_-]", "", slug_base)

    md_name = f"{date}-{slug}.md"

    # Authors list
    authors = ", ".join(" ".join(p.first_names + p.last_names) for p in entry.persons["author"])

    # Venue
    venue_key = "journal" if "journal" in b else "booktitle"
    venue = venue_pretext + b.get(venue_key, "")

    meta = {
        "title": title_clean,
        "authors": authors,
        "date": date,
        "venue": venue,
        "collection": collection,
    }
    if "url" in b:
        meta["paperurl"] = b["url"]

    # simple citation string
    citation = f"{authors}. \"{title_clean}.\" {venue}, {year}."
    meta["citation"] = citation

    return md_name, meta


def merge_meta(old, new):
    merged = new.copy()
    for k, v in old.items():
        if k not in merged or not merged[k]:
            merged[k] = v
    return merged


def write_markdown(path, meta, body=""):
    fm = yaml.safe_dump(meta, sort_keys=False).strip()
    content = f"---\n{fm}\n---\n{body.strip()}\n"
    path.write_text(content, encoding="utf-8")


def main(bib_path: Path):
    existing = load_existing_markdown()

    parser = bibtex.Parser()
    bibdata = parser.parse_file(str(bib_path))

    for key, entry in bibdata.entries.items():
        md_filename, meta = bib_to_markdown(entry, "publications")
        slug = md_filename.split("-", 3)[-1][:-3]  # remove .md

        if slug in existing:
            meta = merge_meta(existing[slug]["meta"], meta)
            body = existing[slug]["body"]
            path = existing[slug]["path"]
        else:
            body = ""
            path = PUB_DIR / md_filename
        write_markdown(path, meta, body)
        existing.pop(slug, None)

    # Optionally, remove any old files still in `existing` dict (duplicates)
    for info in existing.values():
        try:
            info["path"].unlink()
        except Exception:
            pass

    print("Publication markdown regeneration complete.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scripts/update_publications.py path/to/deduped.bib")
        sys.exit(1)
    main(Path(sys.argv[1])) 