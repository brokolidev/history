import os
import re
import json
import time
import urllib.request
import urllib.parse
import ssl
from html import unescape

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://blog.naver.com/mythfeal'
}

CONTENT_DIR = '/Volumes/evo/home/dev/agentic/history/content/history'

def fetch_cat_map():
    url = 'https://blog.naver.com/WidgetListAsync.naver?blogId=mythfeal&enableWidgetKeys=category'
    req = urllib.request.Request(url, headers=HEADERS)
    cat_map = {}
    try:
        with urllib.request.urlopen(req, context=ctx) as res:
            data = res.read().decode('utf-8', errors='ignore')
        match = re.search(r'category\s*:\s*\{\s*content\s*:\s*\'(.*?)\'\s*\}', data, re.DOTALL)
        if match:
            cat_html = match.group(1)
            cats = re.findall(r'categoryNo=(\d+)[^\"]*\"[^>]*>(.*?)</a>', cat_html)
            for c_id, c_name in cats:
                cat_map[c_id] = re.sub(r'<[^>]+>', '', c_name).strip()
    except Exception:
        pass
    return cat_map

def clean_html(html_content):
    # 1. Clean script/style
    html_content = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<style.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

    # 2. Code blocks
    def replace_code_block(match):
        code_html = match.group(1)
        lang_match = re.search(r'language-([a-zA-Z0-9_\-]+)', match.group(0))
        lang = lang_match.group(1) if lang_match else ''
        if lang == 'javascript' and 'php' in code_html.lower():
            lang = 'php'
        code_text = unescape(re.sub(r'<[^>]+>', '', code_html)).strip()
        return f"\n\n```{lang}\n{code_text}\n```\n\n"

    html_content = re.sub(r'<div[^>]*class=[\"\'][^\"\']*__se_code_view[^\"\']*[\"\'][^>]*>(.*?)</div>', replace_code_block, html_content, flags=re.DOTALL)

    # 3. Headings & quotes
    html_content = re.sub(r'<h[1-3][^>]*>(.*?)</h[1-3]>', r'\n\n## \1\n\n', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<h[4-6][^>]*>(.*?)</h[4-6]>', r'\n\n### \1\n\n', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', r'\n\n> \1\n\n', html_content, flags=re.DOTALL | re.IGNORECASE)

    # 4. Images
    images = []
    def replace_img(match):
        attrs = match.group(1)
        src_match = re.search(r'(?:data-lazy-src|src)=[\"\']([^\"\']+)[\"\']', attrs)
        if src_match:
            src = src_match.group(1)
            if any(skip in src for skip in ['static.naver.net', 'emoticon', 'market.naver.net']):
                return ''
            if any(domain in src for domain in ['pstatic.net', 'naver.net', 'postfiles']):
                images.append(src)
                return f"\n\n![Image]({src})\n\n"
        return ''

    html_content = re.sub(r'<img\s+([^>]+)>', replace_img, html_content, flags=re.IGNORECASE)

    # 5. Formatting
    html_content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<p[^>]*>', '\n\n', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'</p>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<br\s*/?>', '\n', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<div[^>]*>', '\n', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'</div>', '', html_content, flags=re.IGNORECASE)

    # 6. Clean tags
    text = re.sub(r'<[^>]+>', '', html_content)
    text = unescape(text).replace('\u200b', '')

    lines = [line.strip() for line in text.split('\n')]
    normalized = []
    prev_empty = False
    for line in lines:
        if not line:
            if not prev_empty:
                normalized.append('')
                prev_empty = True
        else:
            normalized.append(line)
            prev_empty = False

    return '\n'.join(normalized).strip(), images

def repair_file(fname, cat_map):
    # Match YYYY-MM-DD-logNo.md
    m = re.match(r'^(\d{4}-\d{2}-\d{2})-(\d+)\.md$', fname)
    if not m:
        return False
    date_str, log_no = m.group(1), m.group(2)

    url = f'https://blog.naver.com/PostView.naver?blogId=mythfeal&logNo={log_no}'
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as res:
            html = res.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {log_no}: {e}")
        return False

    # Extract title from HTML
    title_match = re.search(r'<title>(.*?) : 네이버 블로그</title>', html)
    if not title_match:
        title_match = re.search(r'<meta property=[\"\']og:title[\"\'] content=[\"\'](.*?)[\"\']', html)
    raw_title = title_match.group(1).strip() if title_match else fname.replace('.md', '')
    raw_title = raw_title.replace(' : 네이버 블로그', '').strip()

    # Extract category
    cat_match = re.search(r'categoryNo=(\d+)', html)
    cat_no = cat_match.group(1) if cat_match else ''
    category = cat_map.get(cat_no, '일상생각')

    # Extract body
    idx = html.find('class="se-main-container"')
    if idx == -1:
        idx = html.find('id="postViewArea"')

    if idx != -1:
        start_tag_end = html.find('>', idx)
        if start_tag_end != -1:
            idx = start_tag_end + 1
        footer_idx = html.find('class="post_footer_contents"', idx)
        if footer_idx == -1:
            footer_idx = html.find('id="post_footer_contents"', idx)
        content_html = html[idx:footer_idx] if footer_idx != -1 else html[idx:idx+20000]
    else:
        content_html = ""

    md_body, images = clean_html(content_html)

    # Excerpt (clean text)
    clean_text = re.sub(r'```.*?```', '', md_body, flags=re.DOTALL)
    clean_text = re.sub(r'!\[.*?\]\(.*?\)', '', clean_text)
    clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
    clean_text = re.sub(r'[*_~`#>]', '', clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    excerpt = clean_text[:100]

    safe_title = json.dumps(raw_title, ensure_ascii=False)
    safe_excerpt = json.dumps(excerpt, ensure_ascii=False)
    safe_cat = json.dumps(category, ensure_ascii=False)

    fpath = os.path.join(CONTENT_DIR, fname)
    new_doc = f"""---
title: {safe_title}
slug: "{fname.replace('.md', '')}"
date: "{date_str}"
source: "naver"
source_label: "Naver Blog"
category: {safe_cat}
tags: [{safe_cat}]
excerpt: {safe_excerpt}
author: "Ted Choi"
---

{md_body}
"""

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(new_doc)

    return True

def main():
    cat_map = fetch_cat_map()
    broken_files = []
    for fname in os.listdir(CONTENT_DIR):
        if not fname.endswith('.md'): continue
        fpath = os.path.join(CONTENT_DIR, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            text = f.read()
        dashes = re.findall(r'^---\s*$', text, re.MULTILINE)
        if len(dashes) < 2:
            broken_files.append(fname)

    print(f"Repairing {len(broken_files)} broken files...")
    for idx, fname in enumerate(broken_files, 1):
        ok = repair_file(fname, cat_map)
        print(f"[{idx}/{len(broken_files)}] {'Fixed' if ok else 'Failed'}: {fname}")
        time.sleep(0.1)

    print("🎉 Repair complete!")

if __name__ == '__main__':
    main()
