import os
import re
import json

content_dir = '/Volumes/evo/home/dev/agentic/history/content/history'

for fname in os.listdir(content_dir):
    if not fname.endswith('.md'):
        continue
    fpath = os.path.join(content_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()

    parts = re.split(r'^---\s*$', text, maxsplit=2, flags=re.MULTILINE)
    if len(parts) < 3:
        continue

    fm_raw = parts[1]
    body = parts[2].strip()

    # Clean unclosed dangling HTML opening tags at the end of body
    body = re.sub(r'<div[^>]*$', '', body).strip()
    body = re.sub(r'<span[^>]*$', '', body).strip()
    body = re.sub(r'<\w+[^>]*$', '', body).strip()

    # Re-extract clean text excerpt
    clean_body = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    clean_body = re.sub(r'!\[.*?\]\(.*?\)', '', clean_body)
    clean_body = re.sub(r'<[^>]+>', ' ', clean_body) # Strip all HTML tags
    clean_body = re.sub(r'#+\s*', '', clean_body)
    clean_body = re.sub(r'[*_~`>]', '', clean_body)
    clean_body = re.sub(r'\s+', ' ', clean_body).strip()
    excerpt = clean_body[:100]

    # Reconstruct
    lines = fm_raw.split('\n')
    new_lines = []
    for line in lines:
        if line.startswith('excerpt:'):
            safe_excerpt = json.dumps(str(excerpt), ensure_ascii=False)
            new_lines.append(f'excerpt: {safe_excerpt}')
        else:
            new_lines.append(line)

    new_content = '---\n' + '\n'.join(new_lines) + '\n---\n\n' + body + '\n'
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(new_content)

print("✅ Sanitized all markdown files and clean excerpts.")
