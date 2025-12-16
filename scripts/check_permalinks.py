import os
import re

ROOT_DIR = "/Users/prasadpiyer/github_repos/prasadpiyer.science"

def main():
    permalinks = {}
    
    for dirpath, _, filenames in os.walk(ROOT_DIR):
        if "_site" in dirpath or ".git" in dirpath:
            continue
            
        for f in filenames:
            if f.endswith(".md") or f.endswith(".html"):
                path = os.path.join(dirpath, f)
                try:
                    with open(path, 'r') as file:
                        content = file.read()
                        match = re.search(r'^permalink:\s*(.+)$', content, re.MULTILINE)
                        if match:
                            perm = match.group(1).strip()
                            if perm in permalinks:
                                print(f"Duplicate permalink '{perm}' found in:")
                                print(f"  - {permalinks[perm]}")
                                print(f"  - {path}")
                            else:
                                permalinks[perm] = path
                except Exception as e:
                    pass

if __name__ == "__main__":
    main()
