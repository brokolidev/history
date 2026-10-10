import re

with open('content/history/2011-07-14-130113275185.md', 'r', encoding='utf-8') as f:
    content = f.read()

parts = content.split('---', 2)
header = parts[1]
body = parts[2]

# Remove duplicated title
body = re.sub(r'^(\s*## SQL문 정리\s*)+', '', body, flags=re.MULTILINE)

# Fix concatenated words before SQL keywords like S_EMPWHERE -> S_EMP\nWHERE, NAMEFROM -> NAME\nFROM
keywords = ['FROM', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY', 'SET', 'VALUES', 'AND', 'OR', 'REFERENCES', 'CONSTRAINT']
for kw in keywords:
    body = re.sub(r'([a-zA-Z0-9_\'\"])\s*(' + kw + r')\b', r'\1\n\2', body)

# Clean up multiple newlines inside sql code blocks if any
full_output = f"---{header}---\n\n## SQL문 정리\n\n{body.strip()}\n"

with open('content/history/2011-07-14-130113275185.md', 'w', encoding='utf-8') as f:
    f.write(full_output)

print("Updated 2011-07-14-130113275185.md successfully.")
