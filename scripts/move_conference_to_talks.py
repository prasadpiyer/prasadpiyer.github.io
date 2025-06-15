import re
import yaml
from pathlib import Path

KEYWORDS = ["conference", "proceedings", "cleo","presentation"]

ROOT = Path(__file__).resolve().parents[1]
PUB_DIR = ROOT / "_publications"
TALK_DIR = ROOT / "_talks"
TALK_DIR.mkdir(exist_ok=True)

FRONT_MATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)


def is_conference(meta):
    venue = (meta.get("venue") or "").lower()
    title = (meta.get("title") or "").lower()
    combined = venue + " " + title
    return any(k in combined for k in KEYWORDS)


def main():
    for md_file in PUB_DIR.glob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        m = FRONT_MATTER.match(text)
        if not m:
            continue
        meta = yaml.safe_load(m.group(1)) or {}
        if not is_conference(meta):
            continue
        # update collection
        meta["collection"] = "talks"
        # build new content
        new_fm = yaml.safe_dump(meta, sort_keys=False).strip()
        new_content = f"---\n{new_fm}\n---\n" + text[m.end():]
        new_path = TALK_DIR / md_file.name
        new_path.write_text(new_content, encoding="utf-8")
        md_file.unlink()
        print(f"Moved {md_file.name} -> _talks/")

    print("Conference entries moved.")


if __name__ == "__main__":
    main() 