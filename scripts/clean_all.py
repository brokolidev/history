import os
import re
import json

content_dir = '/Volumes/evo/home/dev/agentic/history/content/history'
fixed = 0

for fname in os.listdir(content_dir):
    if not fname.endswith('.md'):
        continue
    fpath = os.path.join(content_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()

    parts = re.split(r'^---\s*$', text, maxsplit=2, flags=re.MULTILINE)
    if len(parts) < 3:
        print('WARN: still < 3 parts:', fname)
        continue

    fm_raw = parts[1]
    body = parts[2]

    # Clean body: strip post_footer_contents and dangling tags
    body = re.sub(r'<div[^>]*post_footer_contents.*$', '', body, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r'<div[^>]*$', '', body).strip()
    body = re.sub(r'<\w+[^>]*$', '', body).strip()

    # Clean excerpt
    clean_text = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    clean_text = re.sub(r'!\[.*?\]\(.*?\)', '', clean_text)
    clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
    clean_text = re.sub(r'[*_~`#>]', '', clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    excerpt = clean_text[:100]

    lines = fm_raw.split('\n')
    new_lines = []
    for line in lines:
        if line.startswith('excerpt:'):
            safe_excerpt = json.dumps(excerpt, ensure_ascii=False)
            new_lines.append(f'excerpt: {safe_excerpt}')
        else:
            new_lines.append(line)

    new_doc = '---\n' + '\n'.join(new_lines) + '\n---\n\n' + body + '\n'
    if new_doc != text:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_doc)
        fixed += 1

print(f"✅ Fixed footer and excerpts in {fixed} files.")
