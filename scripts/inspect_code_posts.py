import glob
import re

files = glob.glob('/Volumes/evo/home/dev/agentic/history/content/history/*.md')
files.sort()

results = []
for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
    content = ''.join(lines)
    if '```' in content:
        continue
    
    title = ''
    for line in lines[:15]:
        if line.startswith('title:'):
            title = line.strip()
    
    snippets = []
    for i, line in enumerate(lines):
        line_clean = line.strip()
        if re.search(r'^(server\s*\{|location\s+[\/~]|#!\s*\/usr\/bin|import\s+[a-zA-Z0-9_\.]+|from\s+[a-zA-Z0-9_\.]+\s+import|<\?php|function\s+[a-zA-Z0-9_]+\s*\(|SELECT\s+.*?\s+FROM|CREATE\s+TABLE|DROP\s+TABLE|ALTER\s+TABLE|UPDATE\s+[a-zA-Z0-9_]+\s+SET|INSERT\s+INTO|sudo\s+apt|sudo\s+yum|chmod\s+[0-7]{3}|chown\s+-R|\$\([\"\'][\.#a-zA-Z0-9_]+[\"\']\)|document\.getElementById)', line_clean, re.IGNORECASE):
            snippets.append((i + 1, line_clean))
            
    if snippets:
        fname = f.split('/')[-1]
        results.append((fname, title, snippets))

print(f"Total matching posts: {len(results)}")
for fname, title, snips in results:
    print(f"\n=== {fname} | {title} ===")
    for lineno, snip in snips[:6]:
        print(f"   L{lineno}: {snip[:80]}")
