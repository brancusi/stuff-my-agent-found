"""Case file registry. Case 001's content lives in content.py; later cases each have a module (case_<slug>.py)
exposing pages(memo, R, d) -> [(path, title, desc, body)], posts(R, BL, d) -> [post] and sources() -> [source]."""
import importlib

# The site has four sections. Projects, approaches and practices hold case files; repos is the measured library.
SECTIONS = [
    dict(key='projects', one='PROJECT', href='/projects/', label='projects', title='Projects',
         dek='Deep dives on single projects: what it is, who builds it, how it works, and how people use it in the field.'),
    dict(key='approaches', one='APPROACH', href='/approaches/', label='approaches', title='Approaches',
         dek='Ways to build something, compared across projects and languages: ecosystems, front-end architectures, data sync.'),
    dict(key='repos', one='REPOS', href='/repos/', label='repos', title='Repos',
         dek='The library: every repo from every case file, measured from the GitHub API. Search, filter by language, query by API.'),
    dict(key='practices', one='PRACTICE', href='/practices/', label='practices', title='Agentic coding practices',
         dek='What people are using to succeed when coding agents write the code, and how much of it is measured.'),
]
SEC = {x['key']: x for x in SECTIONS}

CASES = [
    dict(no='001', slug='clojure', kind='approaches', ref='SMAF-001', status='filed', opened='2026-11-10', short='Clojure ecosystem',
         title='The Clojure ecosystem, mapped from the repos up',
         q='What is alive in Clojure and ClojureScript in 2026, and where is the new energy?',
         dek='Every Clojure repo with 50+ stars, measured and scored against Clojure norms. Front-end frameworks, data sync, novel frameworks, runtimes, and why Clojure suits coding agents.',
         tabs=[('/approaches/clojure/', 'brief'), ('/approaches/clojure/frontend/', 'front-end'), ('/approaches/clojure/sync/', 'data-sync'),
               ('/approaches/clojure/novel/', 'novel'), ('/approaches/clojure/runtimes/', 'runtimes'), ('/approaches/clojure/agents/', 'why clojure for agents')]),
    dict(no='002', slug='frontend-sync', kind='approaches', ref='SMAF-002', status='open', opened='2026-11-10', short='Front end for a Clojure backend',
         title='A front end for a Clojure backend, with live data sync',
         q='The backend is Clojure. What should the front end be, which systems sync data between server and client, and does ClojureScript cost me anything?',
         dek='Sync engines across every language, the Clojure options (Electric, Fulcro, re-frame, Replicant, Datastar), whether ClojureScript is a hit when agents write the code, and what fits a local-first ledger like ownpurse.',
         tabs=[('/approaches/frontend-sync/', 'brief'), ('/approaches/frontend-sync/landscape/', 'sync engines'), ('/approaches/frontend-sync/clojure/', 'clojure options'),
               ('/approaches/frontend-sync/cljs-cost/', 'does cljs cost me?'), ('/approaches/frontend-sync/ownpurse/', 'for ownpurse')]),
    dict(no='003', slug='agentic-frameworks', kind='practices', ref='SMAF-003', status='open', opened='2026-11-10', short='Frameworks agents work well in',
         title='Frameworks that work well when agents write the code',
         q='Which app frameworks are people finding work best with coding agents, and what is the evidence?',
         dek='Rails, Phoenix with Tidewave, Laravel Boost, Next.js, SvelteKit, Convex, hypermedia and more: the claims, the measured evidence, the agent tooling each ships, and the patterns that make a framework agent-friendly.',
         tabs=[('/practices/agentic-frameworks/', 'brief'), ('/practices/agentic-frameworks/frameworks/', 'frameworks'), ('/practices/agentic-frameworks/patterns/', 'patterns')]),
    dict(no='004', slug='datastar', kind='projects', ref='SMAF-004', status='open', opened='2026-11-11', short='Datastar and Stardust',
         title='Datastar, and Stardust, the database behind it',
         q='What is Datastar, how are people using it, and what is the database its team is building?',
         dek='The 12.5 KiB hypermedia framework that streams server-rendered HTML over SSE: how it works, who runs it in production (Clojure especially), the Pro controversy, how agents cope, and Stardust, the closed-source temporal database its creator is building next.',
         tabs=[('/projects/datastar/', 'brief'), ('/projects/datastar/how-it-works/', 'how it works'), ('/projects/datastar/stardust/', 'stardust (the db)'),
               ('/projects/datastar/field-reports/', 'field reports'), ('/projects/datastar/critiques/', 'critiques'), ('/projects/datastar/for-ownpurse/', 'for ownpurse')]),
    dict(no='005', slug='agentic-practices', kind='practices', ref='SMAF-005', status='open', opened='2026-11-11', short='Agentic coding practices',
         title='Agentic coding practices that work, and the evidence',
         q='What are people doing that actually works when coding agents write the code, and how much of it is measured?',
         dek='Verifiers, context files, research-plan-implement, context size, tests, self-verification, skills, parallel agents and loops: who reports each one working, the measured studies (METR, DORA, ETH, SkillsBench, TDAD), and the counter-evidence.',
         tabs=[('/practices/agentic-practices/', 'brief'), ('/practices/agentic-practices/playbook/', 'playbook'),
               ('/practices/agentic-practices/evidence/', 'evidence'), ('/practices/agentic-practices/toolkit/', 'toolkit')]),
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
