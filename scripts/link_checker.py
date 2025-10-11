import os
import re
import requests
import sys
from urllib.parse import urlparse

# Regular expressions to find links in markdown and html files
MD_LINK_RE = re.compile(r'\[.*?\]\((?!#)(.*?)\)')
HTML_LINK_RE = re.compile(r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"')
IMG_MD_LINK_RE = re.compile(r'!\[.*?\]\((?!#)(.*?)\)')
IMG_HTML_LINK_RE = re.compile(r'<img\s+(?:[^>]*?\s+)?src="([^"]*)"')


# Directory to scan
ROOT_DIR = '.'

# Files to scan
FILE_EXTENSIONS = ('.md', '.html')

# Directories to ignore
IGNORE_DIRS = ('_site', '.git', 'venv', 'node_modules')

# Store broken links
broken_links = {}

def check_link(link, file_path, line_num):
    """Checks a single link."""
    if not link or link.startswith('#') or link.startswith('mailto:') or link.startswith('tel:'):
        return

    parsed_url = urlparse(link)

    if parsed_url.scheme in ('http', 'https'):
        # External link
        try:
            # Using a session for potential connection reuse
            with requests.Session() as s:
                s.headers['User-Agent'] = 'Mozilla/5.0 (compatible; LinkChecker/1.0; +http://prasadpiyer.science)'
                response = s.head(link, allow_redirects=True, timeout=10)
                if not response.ok:
                    add_broken_link(file_path, line_num, link, f"HTTP {response.status_code}")
        except requests.RequestException as e:
            add_broken_link(file_path, line_num, link, str(e))
    else:
        # Internal link
        # Normalize the link path
        if link.startswith('/'):
            abs_path = os.path.join(ROOT_DIR, link.lstrip('/'))
        else:
            abs_path = os.path.join(os.path.dirname(file_path), link)
        
        abs_path = os.path.normpath(abs_path)

        # Jekyll specific check: if it's a link to a page, it might not have an extension
        # e.g. /about/ might point to /about.md or /about.html
        if not os.path.exists(abs_path):
            if os.path.exists(abs_path + '.md'):
                return
            if os.path.exists(abs_path + '.html'):
                 return
            if os.path.isdir(abs_path) and os.path.exists(os.path.join(abs_path, 'index.html')):
                 return
            if os.path.isdir(abs_path) and os.path.exists(os.path.join(abs_path, 'index.md')):
                 return

            add_broken_link(file_path, line_num, link, "File not found")


def add_broken_link(file_path, line_num, link, reason):
    """Adds a broken link to the report."""
    if file_path not in broken_links:
        broken_links[file_path] = []
    broken_links[file_path].append({'line': line_num, 'link': link, 'reason': reason})

def main():
    """Main function to scan files and check links."""
    for root, dirs, files in os.walk(ROOT_DIR):
        # Exclude ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if file.endswith(FILE_EXTENSIONS):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        # Find all links in the line
                        md_links = MD_LINK_RE.findall(line)
                        html_links = HTML_LINK_RE.findall(line)
                        md_img_links = IMG_MD_LINK_RE.findall(line)
                        html_img_links = IMG_HTML_LINK_RE.findall(line)
                        
                        all_links = md_links + html_links + md_img_links + html_img_links

                        for link in all_links:
                            check_link(link.strip(), file_path, line_num)

    if broken_links:
        print("Found broken links:")
        for file_path, errors in broken_links.items():
            print(f"\nIn file: {file_path}")
            for error in errors:
                print(f"  - Line {error['line']}: {error['link']} ({error['reason']})")
        sys.exit(1)
    else:
        print("No broken links found.")
        sys.exit(0)

if __name__ == "__main__":
    main()
