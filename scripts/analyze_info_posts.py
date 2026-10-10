import glob
import os
import re

files = glob.glob('/Volumes/evo/home/dev/agentic/history/content/history/*.md')
files.sort()

tech_files = []
for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        txt = fp.read()
    if 'category: "Information"' in txt or 'category: "개발/IT"' in txt:
        tech_files.append((f, txt))

print(f"Total tech posts: {len(tech_files)}")

with_fences = []
without_fences_with_code = []
text_only = []

code_regexes = [
    r'<\?php',
    r'server\s*\{',
    r'location\s+[\/~]',
    r'#!\s*\/usr\/bin',
    r'import\s+[a-zA-Z0-9_\.]+',
    r'from\s+[a-zA-Z0-9_\.]+\s+import',
    r'function\s+[a-zA-Z0-9_]+\s*\(',
    r'var\s+[a-zA-Z0-9_]+\s*=',
    r'SELECT\s+.*?\s+FROM',
    r'CREATE\s+TABLE',
    r'DROP\s+TABLE',
    r'UPDATE\s+[a-zA-Z0-9_]+\s+SET',
    r'INSERT\s+INTO',
    r'sudo\s+apt',
    r'sudo\s+yum',
    r'chmod\s+[0-7]{3}',
    r'chown\s+-R',
    r'document\.getElementById',
    r'\$\([\"\'\.]',
    r'RewriteEngine\s+on',
    r'RewriteRule',
    r'#\s*yum\s+',
    r'#\s*apt-get\s+',
    r'\$\s*sudo\s+',
    r'mysql\s*>',
]

for f, txt in tech_files:
    fname = os.path.basename(f)
    # title
    m_title = re.search(r'title:\s*\"(.*?)\"', txt)
    title = m_title.group(1) if m_title else fname

    body = txt.split('---', 2)[-1] if '---' in txt else txt
    
    if '```' in body:
        with_fences.append((fname, title))
    else:
        found_patterns = []
        for pat in code_regexes:
            if re.search(pat, body, re.IGNORECASE):
                found_patterns.append(pat)
        if found_patterns:
            without_fences_with_code.append((fname, title, found_patterns))
        else:
            text_only.append((fname, title))

print(f"\n1. Already has fences ({len(with_fences)}):")
for fn, t in with_fences:
    print(f"   - {fn}: {t}")

print(f"\n2. Needs fences ({len(without_fences_with_code)}):")
for fn, t, pats in without_fences_with_code:
    print(f"   - {fn}: {t} (pats: {len(pats)})")

print(f"\n3. Pure text / links ({len(text_only)}):")
for fn, t in text_only[:10]:
    print(f"   - {fn}: {t}")
print(f"   ... and {len(text_only) - 10} more")
