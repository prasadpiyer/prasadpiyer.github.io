import requests, yaml, re, os, sys
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parents[1]
TARGET = os.environ.get("TARGET_DIR")
if len(sys.argv) > 1:
    TARGET = sys.argv[1]

PUB_DIR = ROOT / TARGET if TARGET else ROOT / "_publications"
API = "https://api.semanticscholar.org/graph/v1/paper/search?query={}&limit=1&fields=title,abstract"
FRONT = re.compile(r"^---\n(.*?)\n---\n", re.S)


def fetch_abstract(title: str) -> str | None:
    try:
        resp = requests.get(API.format(quote_plus(title)), timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
        papers = data.get("data", [])
        if not papers:
            return None
        return papers[0].get("abstract")
    except Exception:
        return None


def main():
    updated = 0
    for md in PUB_DIR.glob("*.md"):
        text = md.read_text(encoding="utf-8")
        m = FRONT.match(text)
        if not m:
            continue
        meta = yaml.safe_load(m.group(1)) or {}
        if meta.get("abstract"):
            continue
        title = meta.get("title")
        if not title:
            continue
        abstract = fetch_abstract(title)
        if not abstract:
            continue
        meta["abstract"] = abstract.replace("\n", " ").strip()
        # rebuild markdown
        fm = yaml.safe_dump(meta, sort_keys=False).strip()
        new_content = f"---\n{fm}\n---\n" + text[m.end():]
        md.write_text(new_content, encoding="utf-8")
        updated += 1
        print(f"Added abstract to {md.name}")
    print(f"Updated {updated} publication files.")


if __name__ == "__main__":
    main() 