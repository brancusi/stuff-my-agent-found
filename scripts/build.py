"""Merge enriched data into a compact dataset + baselines. Writes data/dataset.json"""
import json, os, re, datetime, statistics as st, glob
D = os.path.join(os.path.dirname(__file__), '..', 'data')
NOW = datetime.datetime(2026, 11, 10, tzinfo=datetime.timezone.utc)
def days(ts):
    if not ts: return None
    return (NOW - datetime.datetime.fromisoformat(ts.replace('Z', '+00:00'))).days

raw = {}
for f in ['enriched_discovered.json', 'enriched_extra.json', 'enriched_awesome.json', 'enriched_agents.json']:
    p = os.path.join(D, f)
    if os.path.exists(p): raw.update(json.load(open(p)))
disc = {x['full_name'].lower(): x['tags'] for x in json.load(open(os.path.join(D, 'discovered.json')))}
cur = {c[0].lower(): c for c in json.load(open(os.path.join(D, 'curated.json')))}
debuts = {}
for line in open(os.path.join(D, 'deref_debuts.txt')):
    m = re.match(r'(\S+)\s+([\w.-]+/[\w.-]+)', line)
    if m: debuts.setdefault(m.group(2).lower(), m.group(1).replace('/', '-'))
AW = {e['repo'].lower(): e for e in json.load(open(os.path.join(D, 'awesome', 'entries.json')))}
# repos that left GitHub: archived there, development continues elsewhere (checked 2026-11-10)
MOVED = {'cjohansen/replicant': 'https://codeberg.org/cjohansen/replicant', 'cjohansen/nexus': 'https://codeberg.org/cjohansen/nexus'}
FA_OVERRIDE = {'penpot/penpot':'frontend','logseq/logseq':'frontend','athensresearch/athens':'frontend','day8/re-frame-10x':'frontend',
  'cjohansen/portfolio':'frontend','djblue/portal':'novel','weavejester/capra':'novel'}
monthly = {}
mp = os.path.join(D, 'monthly.json')
if os.path.exists(mp): monthly = json.load(open(mp))['counts']

FOCUS = {  # curated category -> focus area
 'React wrapper': 'frontend', 'Non-React UI': 'frontend', 'State management': 'frontend', 'Routing': 'frontend',
 'CSS': 'frontend', 'Component library': 'frontend', 'HTML': 'frontend', 'Mobile': 'frontend', 'Desktop UI': 'frontend',
 'Build tooling': 'frontend',
 'Data sync / DB': 'sync', 'Reactive': 'sync',
 'Novel / reactive': 'novel', 'Hypermedia / server-driven': 'novel', 'Full-stack framework': 'novel',
 'Agent tooling': 'agents', 'Novel / runtime': 'runtimes', 'Runtime / compiler': 'runtimes',
}
RULES = [  # heuristic category for non-curated repos
 ('Front-end / UI', r'reagent|re-frame|\breact\b|frontend|front-end|\bui\b|\bdom\b|component|hiccup|\bcss\b|svg|browser|web ?app|single.page|spa\b|om\b|rum\b|fulcro|electron|javafx|swing|gui'),
 ('Data / DB', r'datalog|database|\bsql|datomic|datascript|\bdb\b|storage|postgres|jdbc|query|kafka|redis|mongo|elasticsearch|cassandra|xtdb|crux'),
 ('Web / HTTP', r'\bring\b|http|web server|router|routing|\bapi\b|rest|websocket|graphql|middleware|server'),
 ('AI / LLM', r'\bllm|\bai\b|openai|anthropic|claude|gpt|agent|mcp\b|embedding'),
 ('Data science', r'machine learning|\bml\b|dataframe|tensor|statistic|numeric|data science|notebook|plot|visuali'),
 ('Dev tooling', r'repl|nrepl|lint|emacs|vim|vscode|editor|\btest|build|deps|leiningen|lein|boot|cli\b|debug|profil|format|lsp|tool'),
 ('Language / runtime', r'compiler|interpreter|runtime|lisp|language|dialect|jvm|graal|wasm|transpil'),
 ('Concurrency / async', r'async|concurren|stream|actor|channel|reactive'),
 ('Games / art / music', r'game|music|sound|audio|art\b|generative|synth|overtone|quil'),
]
def heur(desc, topics):
    s = ((desc or '') + ' ' + ' '.join(topics)).lower()
    for name, rx in RULES:
        if re.search(rx, s): return name
    return 'Other'

repos = []; seen = set()
for k, r in raw.items():
    if r.get('isFork') and k not in cur: continue
    if r['nameWithOwner'].lower() in seen: continue
    seen.add(r['nameWithOwner'].lower())
    aw = AW.get(k) or AW.get(r['nameWithOwner'].lower())
    t = (r.get('defaultBranchRef') or {}).get('target') or {}
    allh = t.get('all') or {}
    last = (allh.get('nodes') or [{}])[0].get('committedDate') if allh.get('nodes') else None
    rel = (r.get('releases') or {}).get('nodes') or []
    tags = (r.get('refs') or {}).get('nodes') or []
    topics = [n['topic']['name'] for n in (r.get('repositoryTopics') or {}).get('nodes', [])]
    c = cur.get(k)
    oi, ci = r['openIssues']['totalCount'], r['closedIssues']['totalCount']
    o = {
     'n': r['nameWithOwner'], 'd': (r.get('description') or '').strip()[:240], 'h': r.get('homepageUrl') or '',
     's': r['stargazerCount'], 'f': r['forkCount'], 'w': r['watchers']['totalCount'],
     'oi': oi, 'ci': ci, 'op': r['openPRs']['totalCount'], 'mp': r['mergedPRs']['totalCount'],
     'c': allh.get('totalCount'), 'c12': (t.get('recent') or {}).get('totalCount', 0),
     'lc': last[:10] if last else None, 'ld': days(last), 'cr': r['createdAt'][:10], 'cd': days(r['createdAt']),
     'pu': r['pushedAt'][:10] if r.get('pushedAt') else None,
     'rel': rel[0]['tagName'] if rel else (tags[0]['name'] if tags else None),
     'rd': rel[0]['publishedAt'][:10] if rel and rel[0].get('publishedAt') else None,
     'lang': (r.get('primaryLanguage') or {}).get('name'), 'lic': (r.get('licenseInfo') or {}).get('spdxId'),
     'ar': r['isArchived'], 'tp': topics[:8],
     'cat': c[1] if c else (aw['section'] if aw else heur(r.get('description'), topics)),
     'fa': FA_OVERRIDE.get(k) or (FOCUS.get(c[1], 'other') if c else None), 'note': c[2] if c else None,
     'aw': aw['section'] if aw else None, 'mv': MOVED.get(k),
     'deb': debuts.get(k), 'src': disc.get(k, ['curated' if c else 'deref']),
     'm': monthly.get(k),
    }
    repos.append(o)

# ---- Clojure baseline: language:clojure, >=50 stars, not archived (from search 'baseline' tag)
base = [x for x in repos if 'baseline' in x['src'] and not x['ar'] and x['ld'] is not None]
def pct(vals, q):
    v = sorted(vals); i = (len(v) - 1) * q; lo = int(i); hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (i - lo)
act = [x for x in base if x['ld'] <= 365]
def ratio(x):
    t = x['oi'] + x['ci']
    return x['ci'] / t if t >= 5 else None
closes = [ratio(x) for x in base if ratio(x) is not None]
bl = {
 'n': len(base), 'nAct': len(act), 'shareAct': len(act) / len(base),
 'share90': sum(1 for x in base if x['ld'] <= 90) / len(base),
 'share2y': sum(1 for x in base if x['ld'] <= 730) / len(base),
 'ldMed': pct([x['ld'] for x in base], .5),
 'c12': {q: pct([x['c12'] for x in act], q) for q in (.25, .5, .75, .9)},
 'c12all': {q: pct([x['c12'] for x in base], q) for q in (.25, .5, .75, .9)},
 'stars': {q: pct([x['s'] for x in base], q) for q in (.25, .5, .75, .9)},
 'close': {q: pct(closes, q) for q in (.25, .5, .75)},
 'oiPer100': {q: pct([100 * x['oi'] / max(x['s'], 1) for x in base], q) for q in (.25, .5, .75)},
 'oiMed': pct([x['oi'] for x in base], .5),
 'relShare': sum(1 for x in base if x['rel']) / len(base),
}
# histogram of years since last commit
bins = [(0, 90, '<3 mo'), (91, 365, '3–12 mo'), (366, 730, '1–2 yr'), (731, 1095, '2–3 yr'), (1096, 1825, '3–5 yr'), (1826, 99999, '5+ yr')]
bl['ageHist'] = [[lab, sum(1 for x in base if a <= x['ld'] <= b)] for a, b, lab in bins]
c12bins = [(0, 0, '0'), (1, 5, '1–5'), (6, 20, '6–20'), (21, 50, '21–50'), (51, 150, '51–150'), (151, 10**9, '150+')]
bl['c12Hist'] = [[lab, sum(1 for x in base if a <= x['c12'] <= b)] for a, b, lab in c12bins]

# ---- health score: percentile ranks against the Clojure baseline
import bisect
sc12 = sorted(x['c12'] for x in act); sld = sorted(x['ld'] for x in base); scl = sorted(closes)
sst = sorted(x['s'] for x in base)
def prank(sv, v): return (bisect.bisect_left(sv, v) + bisect.bisect_right(sv, v)) / 2 / len(sv)
for x in repos:
    if x['ld'] is None: x['hs'] = None; x['st'] = 'unknown'; continue
    act_ = prank(sc12, x['c12']) if x['c12'] > 0 else 0.0
    rec = 1 - prank(sld, x['ld'])
    r_ = ratio(x); hyg = prank(scl, r_) if r_ is not None else 0.5
    # open-issue load relative to stars: fewer per star is better
    load = 1 - min(1, (100 * x['oi'] / max(x['s'], 1)) / (bl['oiPer100'][.75] * 2 or 1))
    rel = 1.0 if x['rd'] and days(x['rd'] + 'T00:00:00Z') <= 365 else (0.5 if x['rel'] else 0.2)
    pop = prank(sst, x['s'])
    hs = 100 * (.30 * act_ + .25 * rec + .15 * hyg + .10 * load + .10 * rel + .10 * pop)
    if x['ar'] and not x.get('mv'): hs = min(hs, 10)
    if x.get('mv'): hs = None
    x['hs'] = round(hs) if hs is not None else None
    x['hc'] = [round(100 * v) for v in (act_, rec, hyg, load, rel, pop)]
    # Clojure-aware status
    if x.get('mv'): s = 'moved'
    elif x['ar']: s = 'archived'
    elif x['ld'] <= 90 and x['c12'] >= bl['c12'][.75]: s = 'thriving'
    elif x['ld'] <= 90: s = 'active'
    elif x['ld'] <= 365: s = 'maintained'
    elif x['ld'] <= 1095 and x['oi'] <= max(bl['oiMed'] * 2, 5): s = 'stable'
    elif x['ld'] <= 1095: s = 'slowing'
    else: s = 'dormant'
    x['st'] = s

repos.sort(key=lambda x: -x['s'])
out = {'generated': NOW.date().isoformat(), 'since': '2025-11-10', 'baseline': bl, 'repos': repos,
       'months': json.load(open(mp))['months'] if os.path.exists(mp) else []}
json.dump(out, open(os.path.join(D, 'dataset.json'), 'w'), separators=(',', ':'))
print(len(repos), 'repos;', 'baseline', bl['n'], 'active', bl['nAct'])
print(json.dumps({k: v for k, v in bl.items() if k not in ('ageHist','c12Hist')}, default=str)[:900])
