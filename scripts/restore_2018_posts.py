import urllib.request
import ssl
import re
import os
from html import unescape

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

posts = [
    ('content/history/2018-06-14-221298521130.md', '221298521130'),
    ('content/history/2018-06-15-221299207592.md', '221299207592'),
    ('content/history/2018-11-07-221393836196.md', '221393836196'),
    ('content/history/2018-11-14-221398160179.md', '221398160179'),
]

for filepath, log_no in posts:
    print(f"Fetching logNo {log_no}...")
    url = f'https://blog.naver.com/PostView.naver?blogId=mythfeal&logNo={log_no}'
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
        html = res.read().decode('utf-8', errors='ignore')
    
    # Read existing frontmatter
    with open(filepath, 'r', encoding='utf-8') as f:
        existing = f.read()
    parts = existing.split('---', 2)
    header = parts[1]

    # Extract se_paragraph or se_textarea
    matches = re.findall(r'<p[^>]*class=[\"\']se_textarea[\"\'][^>]*>(.*?)</p>', html, re.DOTALL)
    if not matches:
        matches = re.findall(r'<div[^>]*class=[\"\']se_component se_paragraph[^\"\']*[\"\'][^>]*>(.*?)</div>\s*</div>\s*</div>\s*</div>\s*</div>', html, re.DOTALL)
    
    content = '\n\n'.join(matches)
    # convert <br> to newline
    content = re.sub(r'<br\s*/?>', '\n', content)
    content = re.sub(r'<[^>]+>', '', content)
    content = unescape(content)
    content = content.replace('\u200b', '')
    
    # normalize lines
    lines = [l.strip() for l in content.split('\n')]
    norm_lines = []
    prev_empty = False
    for l in lines:
        if not l:
            if not prev_empty:
                norm_lines.append('')
                prev_empty = True
        else:
            norm_lines.append(l)
            prev_empty = False
    
    clean_body = '\n\n'.join([p for p in '\n'.join(norm_lines).split('\n\n') if p.strip()])
    
    # Calculate excerpt
    first_p = ''
    for p in clean_body.split('\n\n'):
        clean_p = p.strip()
        if clean_p:
            first_p = clean_p[:120].replace('"', '\\"')
            break
    
    # Update excerpt in header
    header = re.sub(r'excerpt:\s*".*?"', f'excerpt: "{first_p}"', header)
    
    new_content = f"---{header}---\n\n{clean_body}\n"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Restored {filepath}: {len(clean_body)} characters, excerpt: '{first_p[:30]}...'")

print("All 4 posts successfully restored!")
