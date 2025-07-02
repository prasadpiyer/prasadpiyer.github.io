#!/usr/bin/env python3
"""
Update carousel include lines in markdown files so they point to the
carousel snippet whose slug is derived from the document title (matching
what extract_figures.py now produces).

* Scans _publications/, _patents/, and _talks/ for .md files.
* Computes title‐slug (same rules as extract_figures.py).
* If _includes/carousels/<slug>-carousel.html exists, ensures the markdown
  contains `{% include carousels/<slug>-carousel.html %}` (adds or replaces).

Run:  python scripts/update_carousel_links.py
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SNIPPET_DIR = ROOT / "_includes" / "carousels"
COLLECTION_DIRS = [ROOT / "_publications", ROOT / "_patents", ROOT / "_talks"]

SLUG_PATTERN = re.compile(r"[^a-z0-9_-]")

def slugify(text: str) -> str:
    text = text.lower().replace(" ", "-").replace("_", "-")
    text = re.sub(r"-+", "-", text)
    return SLUG_PATTERN.sub("", text)

INC_REGEX = re.compile(r"{\%\s*include\s+carousels/([a-zA-Z0-9_\-]+)-carousel.html\s*%}")

changed = 0
for coll_dir in COLLECTION_DIRS:
    for md_path in coll_dir.glob("*.md"):
        txt = md_path.read_text(encoding="utf-8")
        m = re.search(r"^title:\s*\"?(.*?)\"?$", txt, re.MULTILINE)
        if not m:
            continue
        title = m.group(1).strip().strip('"').strip("'")
        slug = slugify(title)
        snippet_path = SNIPPET_DIR / f"{slug}-carousel.html"
        if not snippet_path.exists():
            continue  # nothing to update yet

        expected_include = f"{{% include carousels/{slug}-carousel.html %}}"
        if expected_include in txt:
            continue  # already correct

        if INC_REGEX.search(txt):
            new_txt = INC_REGEX.sub(expected_include, txt, count=1)
        else:
            # Insert before end (before last --- or at bottom)
            parts = txt.rsplit("---", 1)
            if len(parts) == 2:
                new_txt = parts[0] + "---\n\n" + expected_include + "\n" + parts[1]
            else:
                new_txt = txt + "\n" + expected_include + "\n"
        md_path.write_text(new_txt, encoding="utf-8")
        print(f"Updated {md_path.relative_to(ROOT)}")
        changed += 1

print(f"Done. {changed} files updated.") 