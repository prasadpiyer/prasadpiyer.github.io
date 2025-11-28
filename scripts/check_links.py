import os
import re
import sys

# Configuration
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
COLLECTIONS = {
    '_projects': '/projects/',
    '_publications': '/publication/',
    '_talks': '/talks/',
    '_patents': '/patents/',
    '_lab_capabilities': '/lab_capabilities/',
    '_posts': '/',
    '_pages': '/',
}

def parse_frontmatter(content):
    """
    Parses Jekyll frontmatter manually.
    Returns a dict of frontmatter and the remaining content.
    """
    fm = {}
    remaining_content = content
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            remaining_content = parts[2]
            
            # Simple line-by-line parsing
            for line in fm_text.split('\n'):
                line = line.strip()
                if ':' in line:
                    key, val = line.split(':', 1)
                    key = key.strip()
                    val = val.strip()
                    # Remove quotes
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1]
                    fm[key] = val
                    
    return fm, remaining_content

def build_url_map(root_dir):
    """
    Scans the site to build a set of valid URLs.
    """
    valid_urls = set()
    
    # 1. Scan collections and pages for permalinks
    for dir_name, url_prefix in COLLECTIONS.items():
        dir_path = os.path.join(root_dir, dir_name)
        if not os.path.exists(dir_path):
            continue
            
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.md') or file.endswith('.html'):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        fm, _ = parse_frontmatter(content)
                        
                        # Check explicit permalink
                        if 'permalink' in fm:
                            valid_urls.add(fm['permalink'])
                        else:
                            # Default behavior
                            name = os.path.splitext(file)[0]
                            if 'slug' in fm:
                                name = fm['slug']
                            
                            if dir_name == '_posts':
                                pass
                            elif dir_name == '_pages':
                                if name == 'index':
                                    valid_urls.add('/')
                                else:
                                    valid_urls.add(f'/{name}/')
                                    valid_urls.add(f'/{name}')
                            else:
                                # Collections
                                coll_name = dir_name[1:] # remove _
                                valid_urls.add(f'/{coll_name}/{name}')
                                valid_urls.add(f'/{coll_name}/{name}/')

    # 2. Scan static files (images, pdfs, etc)
    static_dirs = ['images', 'assets', 'files', 'pdfs']
    for d in static_dirs:
        path = os.path.join(root_dir, d)
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), root_dir)
                    valid_urls.add(f'/{rel_path}')
    
    return valid_urls

def find_broken_links(root_dir, valid_urls):
    """
    Scans markdown files for broken links.
    """
    broken_links = []
    
    dirs_to_scan = list(COLLECTIONS.keys())
    
    for dir_name in dirs_to_scan:
        dir_path = os.path.join(root_dir, dir_name)
        if not os.path.exists(dir_path):
            continue
            
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    # Regex for markdown links [text](url)
                    md_links = re.findall(r'\[.*?\]\((.*?)\)', content)
                    
                    # Regex for HTML links href="url"
                    html_links = re.findall(r'href=[\'"](.*?)[\'"]', content)
                    
                    all_links = md_links + html_links
                    
                    for link in all_links:
                        link = link.strip()
                        if not link:
                            continue
                        
                        # Ignore external links, mailto, etc.
                        if link.startswith(('http', 'mailto:', '#', '{{')):
                            continue
                            
                        # Handle anchors
                        url_path = link.split('#')[0]
                        if not url_path:
                            continue
                            
                        # Check if valid
                        if url_path not in valid_urls:
                            # Try adding/removing trailing slash
                            if url_path + '/' in valid_urls:
                                continue
                            if url_path.endswith('/') and url_path[:-1] in valid_urls:
                                continue
                            
                            broken_links.append({
                                'file': filepath,
                                'link': link,
                                'url_path': url_path
                            })
                            
    return broken_links

def main():
    print("Building URL map...")
    valid_urls = build_url_map(ROOT_DIR)
    print(f"Found {len(valid_urls)} valid URLs.")
    
    print("Scanning for broken links...")
    broken = find_broken_links(ROOT_DIR, valid_urls)
    
    if broken:
        print(f"Found {len(broken)} broken links:")
        for item in broken:
            print(f"File: {os.path.relpath(item['file'], ROOT_DIR)}")
            print(f"  Link: {item['link']}")
            print("-" * 20)
    else:
        print("No broken links found!")

if __name__ == '__main__':
    main()
