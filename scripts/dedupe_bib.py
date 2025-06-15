import sys, re, pathlib
from collections import defaultdict

"""Usage: python scripts/dedupe_bib.py path/to/input.bib [output.bib]
Creates a copy of the BibTeX file with duplicate keys renamed by appending
"_2", "_3", … so that tools like pybtex will not fail on repeated keys.
If output filename is omitted, "deduped_" + original name is used.
"""

def dedupe_bib(source: pathlib.Path, dest: pathlib.Path):
    key_counts = defaultdict(int)
    key_pattern = re.compile(r'^@\w+\{([^,]+),')
    with source.open('r', encoding='utf-8') as f_in, dest.open('w', encoding='utf-8') as f_out:
        for line in f_in:
            match = key_pattern.match(line)
            if match:
                key = match.group(1).strip()
                key_counts[key] += 1
                if key_counts[key] > 1:
                    new_key = f"{key}_{key_counts[key]}"
                    line = line.replace(key, new_key, 1)
            f_out.write(line)
    print(f"Written deduplicated BibTeX to {dest}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    src = pathlib.Path(sys.argv[1]).expanduser()
    if not src.exists():
        print(f"File not found: {src}")
        sys.exit(1)
    out = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_name(f"deduped_{src.name}")
    dedupe_bib(src, out)

if __name__ == "__main__":
    main() 