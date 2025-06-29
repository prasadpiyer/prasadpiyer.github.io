import re
from pathlib import Path

"""Insert carousel snippet includes into markdown files for which a corresponding
_snippet exists under _includes/carousels/.

Usage:
    python scripts/insert_carousel_snippets.py

This scans _publications/, _talks/, and _patents/ for markdown files whose slug
matches a carousel snippet name. If the snippet include is not already present
in the markdown body, it appends it just before the end of the file.
"""

CAROUSEL_DIR = Path("_includes/carousels")
SECTIONS = [Path("_publications"), Path("_talks"), Path("_patents")]

# Reuse same slugify logic as extract_figures for case-insensitive matching
SLUG_PATTERN = re.compile(r"[^a-z0-9_-]")

INCLUDE_PATTERN = re.compile(r"\{\%\s*include\s+carousels/(.+?)-carousel.html\s*\%\}")


def slugify(text: str) -> str:
    text = text.lower().replace(" ", "-").replace("_", "-")
    text = re.sub(r"-+", "-", text)
    return SLUG_PATTERN.sub("", text)


def insert_snippet(md_path: Path, slug: str):
    snippet_include = f"{{% include carousels/{slug}-carousel.html %}}"

    text = md_path.read_text(encoding="utf-8")
    m = INCLUDE_PATTERN.search(text)
    if m:
        existing_slug = m.group(1)
        if existing_slug != slug:
            # Replace wrong-case slug with correct one
            text = INCLUDE_PATTERN.sub(f"{{% include carousels/{slug}-carousel.html %}}", text)
            md_path.write_text(text, encoding="utf-8")
            return True
        # Correct include already present
        return False

    # Insert before end (keeping trailing newline)
    if not text.endswith("\n"):
        text += "\n"
    text += "\n" + snippet_include + "\n"
    md_path.write_text(text, encoding="utf-8")
    return True


def main():
    added = 0
    for md_dir in SECTIONS:
        for md in md_dir.glob("*.md"):
            orig_slug = md.stem.split("-", 3)[-1]
            slug = slugify(orig_slug)
            snippet_path = CAROUSEL_DIR / f"{slug}-carousel.html"
            if snippet_path.exists():
                if insert_snippet(md, slug):
                    added += 1
    print(f"Inserted carousel includes into {added} markdown files.")


if __name__ == "__main__":
    main() 