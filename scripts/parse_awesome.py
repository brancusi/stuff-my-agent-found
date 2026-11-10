"""Parse awesome-clojure README into [{repo, section, label, desc}] -> data/awesome/entries.json"""
import re, json, os
D = os.path.join(os.path.dirname(__file__), '..', 'data', 'awesome')
sec = None; out = {}; top = None
for line in open(os.path.join(D, 'README.md')):
    m = re.match(r'^##+\s+(.*)', line)
    if m: sec = m.group(1).strip(); continue
    m = re.match(r'^- \[(Awesome products|Awesome SaaS|Languages written)', line)
    if m: top = {'Awesome products':'Products','Awesome SaaS':'Products','Languages written':'Languages'}[m.group(1)]; continue
    if line.startswith('- ['): top = None
    s = sec or top
    if not s or s in ('Guides','Video tutorials','YouTube','Websites','Twitter','Exercises'): continue
    for lab, url in re.findall(r'\[([^\]]+)\]\((https://github\.com/[^)\s]+)\)', line):
        mm = re.match(r'https://github\.com/([\w.-]+)/([\w.-]+)', url)
        if not mm: continue
        repo = f'{mm.group(1)}/{mm.group(2).removesuffix(".git")}'
        desc = re.sub(r'.*?\)\s*[:\-–]?\s*', '', line.strip(), count=1).strip()
        out.setdefault(repo.lower(), {'repo': repo, 'section': s, 'label': lab, 'desc': desc[:200]})
json.dump(list(out.values()), open(os.path.join(D, 'entries.json'), 'w'), indent=1)
from collections import Counter
print(len(out)); print(Counter(e['section'] for e in out.values()).most_common(60))
