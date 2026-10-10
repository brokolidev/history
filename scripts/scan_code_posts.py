import glob
import re

files = glob.glob('/Volumes/evo/home/dev/agentic/history/content/history/*.md')

code_indicators = [
    (r'server\s*\{', 'nginx'),
    (r'location\s+[\/~]', 'nginx'),
    (r'#!\s*\/usr\/bin', 'bash/python'),
    (r'import\s+[a-zA-Z0-9_\.]+', 'python'),
    (r'from\s+[a-zA-Z0-9_\.]+\s+import', 'python'),
    (r'<\?php', 'php'),
    (r'function\s+[a-zA-Z0-9_]+\s*\(', 'js/php'),
    (r'var\s+[a-zA-Z0-9_]+\s*=', 'javascript'),
    (r'SELECT\s+.*?\s+FROM', 'sql'),
    (r'CREATE\s+TABLE', 'sql'),
    (r'sudo\s+apt-get', 'bash'),
    (r'sudo\s+yum', 'bash'),
    (r'chmod\s+[0-7]{3}', 'bash'),
    (r'chown\s+-R', 'bash'),
    (r'\$this->', 'php'),
    (r'document\.getElementById', 'javascript'),
    (r'\$\([\"\'\.]', 'javascript/jquery'),
]

detected = []
for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        content = fp.read()
    has_fences = '```' in content
    matches = []
    for pat, tag in code_indicators:
        m = re.findall(pat, content, re.IGNORECASE)
        if m:
            matches.append((tag, len(m)))
    if matches:
        detected.append((f.split('/')[-1], has_fences, matches))

print(f"Total posts with code patterns: {len(detected)}")
for fname, has_fences, matches in sorted(detected):
    print(f"{fname} (has_fences={has_fences}): {matches[:3]}")
