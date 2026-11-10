"""Case file registry. Case 001's content lives in content.py; later cases each have a module (case_<slug>.py)
exposing pages(memo, R, d) -> [(path, title, desc, body)], posts(R, BL, d) -> [post] and sources() -> [source]."""
import importlib

CASES = [
    dict(no='001', slug='clojure', ref='SMAF-001', status='filed', opened='2026-11-10', short='Clojure ecosystem',
         title='The Clojure ecosystem, mapped from the repos up',
         q='What is alive in Clojure and ClojureScript in 2026, and where is the new energy?',
         dek='Every Clojure repo with 50+ stars, measured and scored against Clojure norms. Front-end frameworks, data sync, novel frameworks, runtimes, and why Clojure suits coding agents.',
         tabs=[('/cases/clojure/', 'brief'), ('/cases/clojure/frontend/', 'front-end'), ('/cases/clojure/sync/', 'data-sync'),
               ('/cases/clojure/novel/', 'novel'), ('/cases/clojure/runtimes/', 'runtimes'), ('/cases/clojure/agents/', 'why clojure for agents')]),
    dict(no='002', slug='frontend-sync', ref='SMAF-002', status='open', opened='2026-11-10', short='Front end for a Clojure backend',
         title='A front end for a Clojure backend, with live data sync',
         q='The backend is Clojure. What should the front end be, which systems sync data between server and client, and does ClojureScript cost me anything?',
         dek='Sync engines across every language, the Clojure options (Electric, Fulcro, re-frame, Replicant, Datastar), whether ClojureScript is a hit when agents write the code, and what fits a local-first ledger like ownpurse.',
         tabs=[('/cases/frontend-sync/', 'brief'), ('/cases/frontend-sync/landscape/', 'sync engines'), ('/cases/frontend-sync/clojure/', 'clojure options'),
               ('/cases/frontend-sync/cljs-cost/', 'does cljs cost me?'), ('/cases/frontend-sync/ownpurse/', 'for ownpurse')]),
    dict(no='003', slug='agentic-frameworks', ref='SMAF-003', status='open', opened='2026-11-10', short='Frameworks agents work well in',
         title='Frameworks that work well when agents write the code',
         q='Which app frameworks are people finding work best with coding agents, and what is the evidence?',
         dek='Rails, Phoenix with Tidewave, Laravel Boost, Next.js, SvelteKit, Convex, hypermedia and more: the claims, the measured evidence, the agent tooling each ships, and the patterns that make a framework agent-friendly.',
         tabs=[('/cases/agentic-frameworks/', 'brief'), ('/cases/agentic-frameworks/frameworks/', 'frameworks'), ('/cases/agentic-frameworks/patterns/', 'patterns')]),
]
for c in CASES: c['href'] = c['tabs'][0][0]

def _mod(c):
    if c['slug'] == 'clojure': return None
    try: return importlib.import_module('case_' + c['slug'].replace('-', '_'))
    except ModuleNotFoundError: return None

def _pending(memo, c):
    out = []
    for h, label in c['tabs']:
        body = f'''{memo(c['title'] if h == c['href'] else label.capitalize(), c['q'], 'In progress', eyebrow=f'Case {c["no"]} // {label}', ref=c['ref'])}
<div class="bluf"><p>This case is open. The agent is still in the field; the findings will be filed here.</p></div>'''
        out.append((h, label if h != c['href'] else f'Case {c["no"]}: {c["short"]}', c['dek'], body, c['slug']))
    return out

def case_pages(memo, R, d):
    out = []
    for c in CASES[1:]:
        m = _mod(c)
        out += [(p, t, ds, b, c['slug']) for p, t, ds, b in m.pages(memo, R, d)] if m else _pending(memo, c)
    return out

def case_posts(R, BL, d):
    out = []
    for c in CASES[1:]:
        m = _mod(c)
        if m:
            for p in m.posts(R, BL, d): p['case'] = c['slug']; out.append(p)
    return out

def case_sources():
    out = []
    for c in CASES[1:]:
        m = _mod(c)
        if m:
            for s in m.sources(): s['k'] = list(s.get('k', [])) + [c['slug']]; out.append(s)
    return out
