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

    # Split front-matter and body
    parts = re.split(r'^---\s*$', text, maxsplit=2, flags=re.MULTILINE)
    if len(parts) < 3:
        continue

    fm_raw = parts[1]
    body = parts[2].strip()

    # Extract fields safely using regex
    def get_field(name, default=''):
        m = re.search(rf'^{name}:\s*(.*)$', fm_raw, re.MULTILINE)
        if m:
            val = m.group(1).strip()
            if val.startswith('"') and val.endswith('"'):
                try:
                    return json.loads(val)
                except Exception:
                    return val.strip('"')
            return val
        return default

    title = get_field('title', fname.replace('.md', ''))
    slug = get_field('slug', fname.replace('.md', ''))
    date = get_field('date', '2020-01-01')
    source = get_field('source', 'naver')
    source_label = get_field('source_label', 'Naver Blog' if source == 'naver' else source.title())
    category = get_field('category', '일상')
    author = get_field('author', 'Ted Choi')

    # Media
    media_yaml = ""
    media_match = re.search(r'media:\n((?:  - type:.*?\n(?:    src:.*?\n)?)+)', fm_raw)
    if media_match:
        media_yaml = "media:\n" + media_match.group(1)

    # Compute a clean single-line excerpt from body
    # Remove markdown formatting, images, code blocks
    clean_body = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    clean_body = re.sub(r'!\[.*?\]\(.*?\)', '', clean_body)
    clean_body = re.sub(r'#+\s*', '', clean_body)
    clean_body = re.sub(r'[*_~`>]', '', clean_body)
    clean_body = re.sub(r'\s+', ' ', clean_body).strip()
    excerpt = clean_body[:100]

    # Reconstruct pristine front-matter
    safe_title = json.dumps(str(title), ensure_ascii=False)
    safe_excerpt = json.dumps(str(excerpt), ensure_ascii=False)
    safe_cat = json.dumps(str(category), ensure_ascii=False)

    new_fm = f"""---
title: {safe_title}
slug: "{slug}"
date: "{date}"
source: "{source}"
source_label: "{source_label}"
category: {safe_cat}
tags: [{safe_cat}]
excerpt: {safe_excerpt}
author: "{author}"
{media_yaml}---

{body}
"""

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(new_fm)

print("✅ Finished sanitizing all markdown files in history!")
