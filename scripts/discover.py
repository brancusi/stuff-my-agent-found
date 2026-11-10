"""Discover Clojure repos via GitHub search API (gh CLI). Writes data/discovered.json"""
import json, subprocess, time, sys, os
OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'discovered.json')

def search(q):
    items = []
    for page in range(1, 11):
        for attempt in range(5):
            r = subprocess.run(['gh','api','-X','GET','search/repositories','-f',f'q={q}','-f','per_page=100','-f',f'page={page}','-f','sort=stars'],capture_output=True,text=True)
            if r.returncode == 0: break
            print('retry', q, page, r.stderr[:200], file=sys.stderr); time.sleep(20)
        d = json.loads(r.stdout)
        items += d['items']
        time.sleep(2.2)
        if len(d['items']) < 100 or len(items) >= d['total_count']: break
    print(f'{q}: {len(items)}', file=sys.stderr)
    return items

queries = {
  'baseline': ['language:clojure stars:>=1000','language:clojure stars:300..999','language:clojure stars:150..299',
               'language:clojure stars:100..149','language:clojure stars:75..99','language:clojure stars:50..74'],
  'active': ['language:clojure stars:20..49 pushed:>=2025-11-10'],
  'new': ['language:clojure stars:>=5 created:>=2025-11-10'],
  'cljs_other': ['topic:clojurescript stars:>=20 pushed:>=2025-11-10 -language:clojure',
                 'topic:clojure stars:>=30 pushed:>=2025-11-10 -language:clojure'],
}
repos = {}
for tag, qs in queries.items():
    for q in qs:
        for it in search(q):
            k = it['full_name']
            e = repos.setdefault(k, {'full_name': k, 'tags': []})
            if tag not in e['tags']: e['tags'].append(tag)
json.dump(list(repos.values()), open(OUT,'w'), indent=1)
print('total', len(repos), file=sys.stderr)
