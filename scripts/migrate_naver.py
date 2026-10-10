import os
import sys
import ssl
import json
import time
import re
import urllib.request
import urllib.parse
from html import unescape

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://blog.naver.com/mythfeal'
}

BASE_DIR = '/Volumes/evo/home/dev/agentic/history'
CONTENT_DIR = os.path.join(BASE_DIR, 'content', 'history')
IMG_BASE_DIR = os.path.join(BASE_DIR, 'public', 'img', 'history', 'naver')

os.makedirs(CONTENT_DIR, exist_ok=True)
os.makedirs(IMG_BASE_DIR, exist_ok=True)

def fetch_category_map(blog_id):
    """Fetch categoryNo -> categoryName mapping."""
    url = f'https://blog.naver.com/WidgetListAsync.naver?blogId={blog_id}&enableWidgetKeys=category'
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
                clean_name = re.sub(r'<[^>]+>', '', c_name).strip()
                cat_map[c_id] = clean_name
    except Exception as e:
        print(f"⚠️ Failed to fetch category map: {e}")
    return cat_map

def fetch_all_posts_metadata(blog_id):
    """Fetch all posts metadata across all pages."""
    posts = []
    page = 1
    count_per_page = 30
    total_count = None

    print(f"🔍 Fetching post list for {blog_id}...")

    while True:
        url = f'https://blog.naver.com/PostTitleListAsync.naver?blogId={blog_id}&viewdate=&currentPage={page}&categoryNo=0&parentCategoryNo=&countPerPage={count_per_page}'
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, context=ctx) as res:
                data = res.read().decode('utf-8', errors='ignore').replace(r"\'", "'")
            d = json.loads(data)
            
            if total_count is None:
                total_count = int(d.get('totalCount', 0))
                print(f"📊 Total posts registered in Naver blog: {total_count}")

            p_list = d.get('postList', [])
            if not p_list:
                break

            for p in p_list:
                log_no = p.get('logNo')
                title = urllib.parse.unquote_plus(p.get('title', ''))
                add_date = p.get('addDate', '') # e.g. "2020. 1. 15."
                cat_no = p.get('categoryNo', '')

                # Parse date to YYYY-MM-DD
                m_date = re.match(r'(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\.', add_date)
                if m_date:
                    formatted_date = f"{m_date.group(1)}-{int(m_date.group(2)):02d}-{int(m_date.group(3)):02d}"
                    year = m_date.group(1)
                else:
                    formatted_date = "2020-01-01"
                    year = "2020"

                posts.append({
                    'logNo': log_no,
                    'title': title,
                    'rawDate': add_date,
                    'date': formatted_date,
                    'year': year,
                    'categoryNo': cat_no,
                })

            if len(posts) >= total_count or len(p_list) < count_per_page:
                break

            page += 1
            time.sleep(0.2)
        except Exception as e:
            print(f"❌ Error fetching page {page}: {e}")
            break

    print(f"✅ Collected metadata for {len(posts)} posts.")
    return posts

def download_image(img_url, dest_path):
    """Download image safely with headers."""
    try:
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        req = urllib.request.Request(img_url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as res:
            with open(dest_path, 'wb') as f:
                f.write(res.read())
        return True
    except Exception as e:
        return False

def clean_html_to_markdown(html_content, post_slug, year):
    """Convert HTML content into clean Markdown and extract local images."""
    html_content = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<style.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

    # 1. Code blocks
    def replace_code_block(match):
        code_html = match.group(1)
        lang_match = re.search(r'language-([a-zA-Z0-9_\-]+)', match.group(0))
        lang = lang_match.group(1) if lang_match else ''
        if lang == 'javascript' and 'php' in code_html.lower():
            lang = 'php'
        code_text = unescape(re.sub(r'<[^>]+>', '', code_html)).strip()
        return f"\n\n```{lang}\n{code_text}\n```\n\n"

    html_content = re.sub(r'<div[^>]*class=[\"\'][^\"\']*__se_code_view[^\"\']*[\"\'][^>]*>(.*?)</div>', replace_code_block, html_content, flags=re.DOTALL)

    # 2. Headings & quotes
    html_content = re.sub(r'<h[1-3][^>]*>(.*?)</h[1-3]>', r'\n\n## \1\n\n', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<h[4-6][^>]*>(.*?)</h[4-6]>', r'\n\n### \1\n\n', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', r'\n\n> \1\n\n', html_content, flags=re.DOTALL | re.IGNORECASE)

    # 3. Images download & local replacement
    downloaded_images = []
    img_counter = [1]

    def replace_img(match):
        attrs = match.group(1)
        src_match = re.search(r'(?:data-lazy-src|src)=[\"\']([^\"\']+)[\"\']', attrs)
        if src_match:
            src = src_match.group(1)
            if any(skip in src for skip in ['static.naver.net', 'emoticon', 'market.naver.net']):
                return ''
            if any(domain in src for domain in ['pstatic.net', 'naver.net', 'postfiles']):
                ext = 'jpg'
                if '.png' in src.lower(): ext = 'png'
                elif '.gif' in src.lower(): ext = 'gif'
                
                filename = f"photo_{img_counter[0]:02d}.{ext}"
                img_counter[0] += 1

                local_fs_path = os.path.join(IMG_BASE_DIR, year, post_slug, filename)
                web_path = f"/img/history/naver/{year}/{post_slug}/{filename}"

                # Download image
                if download_image(src, local_fs_path):
                    downloaded_images.append({'src': web_path, 'caption': ''})
                    return f"\n\n![Image]({web_path})\n\n"
        return ''

    html_content = re.sub(r'<img\s+([^>]+)>', replace_img, html_content, flags=re.IGNORECASE)

    # 4. Paragraphs, formatting
    html_content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<p[^>]*>', '\n\n', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'</p>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<br\s*/?>', '\n', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<div[^>]*>', '\n', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'</div>', '', html_content, flags=re.IGNORECASE)

    # 5. Clean tags and special chars
    text = re.sub(r'<[^>]+>', '', html_content)
    text = unescape(text)
    text = text.replace('\u200b', '')

    # 6. Normalize empty lines
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

    return '\n'.join(normalized).strip(), downloaded_images

def fetch_and_convert_post(blog_id, post_meta, cat_map):
    """Fetch post HTML, convert to Markdown, and save to disk."""
    log_no = post_meta['logNo']
    title = post_meta['title']
    date = post_meta['date']
    year = post_meta['year']
    cat_no = post_meta['categoryNo']
    category = cat_map.get(cat_no, '일상')

    # Slug: YYYY-MM-DD-logNo
    slug = f"{date}-{log_no}"
    target_file = os.path.join(CONTENT_DIR, f"{slug}.md")

    # Skip if already exists
    if os.path.exists(target_file):
        return True

    url = f'https://blog.naver.com/PostView.naver?blogId={blog_id}&logNo={log_no}'
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
            html = res.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"❌ Failed to fetch post {log_no}: {e}")
        return False

    idx = html.find('class="se-main-container"')
    if idx == -1:
        idx = html.find('id="postViewArea"')

    if idx != -1:
        # Move past the opening tag
        start_tag_end = html.find('>', idx)
        if start_tag_end != -1:
            idx = start_tag_end + 1

        footer_idx = html.find('class="post_footer_contents"', idx)
        if footer_idx == -1:
            footer_idx = html.find('id="post_footer_contents"', idx)
        
        content_html = html[idx:footer_idx] if footer_idx != -1 else html[idx:idx+30000]
    else:
        content_html = ""

    md_body, media_items = clean_html_to_markdown(content_html, slug, year)

    # Excerpt (first 120 chars)
    first_paragraph = ''
    for p in md_body.split('\n\n'):
        clean_p = p.replace('**', '').replace('#', '').strip()
        if clean_p and not clean_p.startswith('!['):
            first_paragraph = clean_p[:120]
            break

    # Build Front-matter
    safe_title = title.replace('"', '\\"')
    safe_excerpt = first_paragraph.replace('"', '\\"')

    media_yaml = ""
    if media_items:
        media_yaml = "media:\n" + "\n".join([f'  - type: "image"\n    src: "{m["src"]}"' for m in media_items]) + "\n"

    md_document = f"""---
title: "{safe_title}"
slug: "{slug}"
date: "{date}"
source: "naver"
source_label: "Naver Blog"
category: "{category}"
tags: ["{category}"]
excerpt: "{safe_excerpt}"
author: "Ted Choi"
{media_yaml}---

{md_body}
"""

    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(md_document)

    return True

def main():
    blog_id = 'mythfeal'
    print(f"🚀 Starting migration for Naver Blog: https://blog.naver.com/{blog_id}")
    
    cat_map = fetch_category_map(blog_id)
    print("📁 Categories found:")
    for cid, cname in cat_map.items():
        print(f"  [{cid}] {cname}")

    posts_meta = fetch_all_posts_metadata(blog_id)
    total = len(posts_meta)

    success_count = 0
    print(f"\n📦 Starting batch processing for {total} posts...")
    for idx, p in enumerate(posts_meta, 1):
        ok = fetch_and_convert_post(blog_id, p, cat_map)
        if ok:
            success_count += 1
        
        if idx % 10 == 0 or idx == total:
            print(f"  [{idx}/{total}] Processed ({success_count} success)...")
        time.sleep(0.1)

    print(f"\n🎉 Migration finished! {success_count}/{total} posts converted to Markdown.")

if __name__ == '__main__':
    main()
