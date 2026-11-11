"""Build the "stuff my agent found" static site into dist/.  usage: python3 scripts/site.py"""
import json, os, re, shutil, html, datetime
from collections import Counter, defaultdict
from content import posts, sources, why_clojure, SECTORS, finding

B = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DIST = os.path.join(B, 'dist')
SITE_URL = os.environ.get('SITE_URL', 'https://stuff-my-agent-found.atd-ai.workers.dev')
REPO_URL = 'https://github.com/brancusi/stuff-my-agent-found'
BRAND = 'stuff my agent found'
d = json.load(open(os.path.join(B, 'data', 'dataset.json')))
R = {r['n'].lower(): r for r in d['repos']}
BL = d['baseline']
SNAP = d['generated']
DOC = 'SMAF-' + SNAP[:7].replace('-', '')
esc = html.escape

NAV = [('/', 'index'), ('/projects/', 'projects'), ('/approaches/', 'approaches'), ('/repos/', 'repos'), ('/practices/', 'practices'), ('/blog/', 'dispatches'), ('/sources/', 'sources'), ('/method/', 'method')]
from cases import CASES, SECTIONS, SEC
REPO_TABS = [('/repos/', 'library'), ('/for-agents/', 'api & context files')]
CASE = {c['slug']: c for c in CASES}

def page(path, title, desc, body, crumb=None, active=None, case=None, tabs_=None):
    active = active or (SEC[CASE[case]['kind']]['href'] if case else path)
    nav = ''.join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == active else '', l) for h, l in NAV)
    parts = [p for p in path.strip('/').split('/') if p]
    trail = '<a href="/">~/stuff-my-agent-found</a>' + ''.join(f'/<a href="/{"/".join(parts[:i+1])}/">{esc(p)}</a>' for i, p in enumerate(parts))
    full_title = title if path == '/' else f'{title} · {BRAND}'
    tabs = ''
    if case: c = CASE[case]; tabs_ = (f'Case {c["no"]} pages', f'{SEC[c["kind"]]["one"]} // CASE {c["no"]}', c['tabs'])
    if tabs_:
        tabs = '<div class="wrap"><nav class="casetabs" aria-label="%s"><span class="cno">%s</span>%s</nav></div>' % (tabs_[0], tabs_[1], ''.join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == path else '', l) for h, l in tabs_[2]))
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(full_title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{SITE_URL}{path}">
<meta name="twitter:card" content="summary">
<link rel="canonical" href="{SITE_URL}{path}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/plex-mono-400-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/plex-mono-600-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/plex-mono-700-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/fonts/fonts.css">
<link rel="stylesheet" href="/assets/radar.css">
<link rel="alternate" type="text/plain" title="LLM index" href="/llms.txt">
<link rel="alternate" type="application/atom+xml" title="stuff my agent found: dispatches" href="/blog/feed.xml">
<script>try{{var t=localStorage.getItem('radar-theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="banner">OSINT <span>//</span> PUBLIC RELEASE <span>//</span> FIELD NOTES FROM AN AGENT <span>//</span> SNAPSHOT {SNAP}</div>
<div class="bar"><div class="wrap">
  <a class="logo" href="/" aria-label="stuff my agent found: home"><span class="mark" aria-hidden="true"></span>STUFF_MY_AGENT_FOUND</a>
  <nav class="primary" aria-label="Sections">{nav}</nav>
  <div class="tools"><button class="ghost search-btn" id="search-open" type="button" aria-label="Search (Ctrl K or /)" aria-keyshortcuts="Control+K Meta+K /"><span aria-hidden="true">⌕</span> search <span class="kbd" aria-hidden="true">⌘K</span></button><button class="ghost" id="help-open" type="button" aria-label="Keyboard shortcuts (?)" aria-keyshortcuts="?">?</button><button class="ghost" id="theme" type="button">[ theme ]</button></div>
</div></div>
<div class="wrap"><div class="crumb">{trail}</div></div>{tabs}
<main id="main" class="wrap"><div class="stack">
{body}
</div></main>
<footer class="foot"><div class="wrap">
  <div>STUFF MY AGENT FOUND <span>//</span> open case files on the tech I'm researching, built with an AI agent from the GitHub API and primary sources. Snapshot {SNAP}. Field agent: <span class="redact" tabindex="0">a language model with a library card</span>.</div>
  <div><a href="{REPO_URL}">source &amp; data on GitHub</a> · <a href="/method/">method</a> · <a href="/sources/">sources</a> · <a href="/blog/feed.xml">atom feed</a> · <a href="/llms.txt">llms.txt</a> · <a href="/api">api</a> · Not affiliated with any project listed.</div>
</div></footer>
<script src="/assets/search-core.js" defer></script>
<script src="/assets/radar.js" defer></script>
</body>
</html>'''

def memo(title, subj, stamp='Public release', extra=None, eyebrow=None, ref=None):
    rows = [('To', 'Builders, tech leads, the curious'), ('From', BRAND), ('Date', SNAP), ('Subj', subj), ('Ref', ref or DOC)] + (extra or [])
    dl = ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in rows)
    eb = f'<div class="eyebrow">{eyebrow}</div>' if eyebrow else ''
    return f'<header class="memo"><span class="stamp">{stamp}</span>{eb}<h1>{title}</h1><dl>{dl}</dl></header>'

def n(name, k='s'):
    v = R[name.lower()][k]
    return f'{v:,}' if isinstance(v, int) else str(v)

pct = lambda x: f'{round(100*x)}%'
act = [r for r in d['repos'] if r['ld'] is not None and r['ld'] <= 365 and not r['ar']]
new = [r for r in d['repos'] if r['cd'] <= 365 and not r['ar']]
curated = [r for r in d['repos'] if r['fa'] and r['fa'] not in ('other', 'case')]
POSTS = posts(R, BL, d)
for _p in POSTS: _p.setdefault('case', 'clojure')

def write(path, content):
    p = os.path.join(DIST, path.strip('/'), 'index.html') if path.endswith('/') else os.path.join(DIST, path.lstrip('/'))
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w').write(content)

shutil.rmtree(DIST, ignore_errors=True)
shutil.copytree(os.path.join(B, 'site', 'assets'), os.path.join(DIST, 'assets'))
for f in os.listdir(os.path.join(B, 'site', 'static')): shutil.copy(os.path.join(B, 'site', 'static', f), DIST)
os.makedirs(os.path.join(DIST, 'data'))
json.dump(d, open(os.path.join(DIST, 'data', 'radar.json'), 'w'), separators=(',', ':'))

# ---------------- brief (home)
kj = ''.join(f'<li><div><h3>{p["kj"]}</h3><p>{p["dek"]} <span class="conf {p["conf"][0]}">{p["conf"][1]}</span> <a class="more" href="/blog/{p["slug"]}/">read dispatch {p["no"]} →</a></p></div></li>' for p in POSTS if p.get('kj'))
sectors = ''.join(f'<a class="sector" href="{s["href"]}"><span class="k">SECTOR // {s["code"]}</span><h3>{s["title"]}</h3><p>{s["blurb"]}</p><span class="go">{len([r for r in curated if r["fa"] == s["fa"]])} tracked projects →</span></a>' for s in SECTORS)
home = f'''
{memo('The Clojure landscape, mapped from the repos up', 'Front-end frameworks, data sync, novel frameworks, runtimes and agentic coding in Clojure, Nov 2025 – Nov 2026', 'Filed', eyebrow='Case 001 // situation report', ref=CASE['clojure']['ref'])}
<div class="bluf"><p>Clojure is small, quiet and unusually productive. Only {pct(BL['shareAct'])} of established repos changed this year, and that is normal for a language whose libraries tend to get finished. The energy is in four places: React-free and server-driven UIs, Datalog-based data sync, a burst of new runtimes, and REPL-connected AI agents, which suit Clojure better than almost any other language.</p></div>
<div class="strip" aria-label="Snapshot totals">
  <div><div class="v">{len(d['repos']):,}</div><div class="l">repos tracked</div></div>
  <div><div class="v">{len(act):,}</div><div class="l">active in 12 months</div></div>
  <div><div class="v">{len(new):,}</div><div class="l">created in 12 months</div></div>
  <div><div class="v">{len(curated)}</div><div class="l">curated projects</div></div>
  <div><div class="v">{len(POSTS)}</div><div class="l">dispatches filed</div></div>
</div>
<section aria-labelledby="radar-h"><h2 class="sec" id="radar-h">The radar</h2>
  <p class="prose dim" style="margin:0 0 10px">Every curated project, placed by sector and by how active it is. Inner rings are busier. Click a blip to open its file.</p>
  <div data-radar><p class="dim">Loading radar…</p></div></section>
<section aria-labelledby="kj-h"><h2 class="sec" id="kj-h">Key judgments</h2><ol class="kj">{kj}</ol>
  <p class="dim" style="font-size:12.5px;max-width:var(--measure)">Confidence follows intelligence-analysis convention. <span class="conf high">HIGH</span> means several independent sources agree and the numbers back it. <span class="conf mod">MODERATE</span> means consistent reports with limited measurement. <span class="conf low">LOW</span> means plausible but mostly argued.</p></section>
<section aria-labelledby="sec-h"><h2 class="sec" id="sec-h">Sectors</h2><div class="sectors">{sectors}<a class="sector" href="/repos/?lang=Clojure"><span class="k">INDEX // CLOJURE</span><h3>Explore every Clojure repo</h3><p>All {sum(1 for r in d['repos'] if r['lang'] == 'Clojure'):,} Clojure repositories, searchable and sortable, with filters for category, status and age.</p><span class="go">open the explorer →</span></a></div></section>
<section aria-labelledby="norm-h"><h2 class="sec" id="norm-h">What normal looks like</h2>
  <div class="grid2">
    <div class="card"><h3>Time since last commit</h3><p class="sub">{BL['n']:,} non-archived Clojure repos with 50+ stars.</p><div class="hist" data-hist="age"></div></div>
    <div class="card"><h3>Commits in the last 12 months</h3><p class="sub">Default branch only. Highlight = touched this year.</p><div class="hist" data-hist="c12"></div></div>
  </div>
  <p class="prose" style="margin-top:10px"><a href="/blog/quiet-is-normal/">Why quiet is normal in Clojure →</a></p></section>
'''
write('/approaches/clojure/', page('/approaches/clojure/', 'Case 001: the Clojure ecosystem', 'The Clojure ecosystem mapped from the repos up: front-end frameworks, data sync, novel frameworks, runtimes and agentic coding, with live GitHub health data.', home, case='clojure'))

# ---------------- sector pages
for s in SECTORS:
    if s['fa'] == 'agents': continue
    more = f'<div data-table="{s["fa"]}-more" data-cat="{s["more"]}" data-min="10" data-cols="compact" data-limit="60" data-title="Also active this year"></div>' if s.get('more') else ''
    body = f'''{memo(s['title'], s['subj'], eyebrow='Case 001 // sector // ' + s['code'], ref=CASE['clojure']['ref'])}
<div class="bluf"><p>{s['bluf']}</p></div>
<div class="prose">{s['body']}</div>
<div data-table="{s['fa']}" data-sort="cat" data-title="Curated projects, by category"><p class="dim">Loading table…</p></div>
{more}
<div class="prose"><h2>Related dispatches</h2><ul>{''.join(f'<li><a href="/blog/{p["slug"]}/">{p["title"]}</a></li>' for p in POSTS if s['fa'] in p['tags'])}</ul></div>'''
    write(s['href'], page(s['href'], s['title'], s['bluf'][:155], body, case='clojure'))

# ---------------- why clojure (agents)
from functools import partial
write('/approaches/clojure/agents/', page('/approaches/clojure/agents/', 'Why Clojure for agentic coding', 'Why REPL-driven, data-oriented Clojure suits AI coding agents: the arguments, the evidence, real-world wins, counterpoints and the tooling.', why_clojure(partial(memo, ref=CASE['clojure']['ref']), R, n), case='clojure'))

# ---------------- other case files (pages, dispatches, sources)
from cases import case_pages, case_posts, case_sources
POSTS = POSTS + case_posts(R, BL, d)
for i, p_ in enumerate(POSTS):
    p_.setdefault('no', f'{i+1:03d}'); p_.setdefault('date', d['generated']); p_.setdefault('kj', None)
    p_.setdefault('read', max(2, round(len(re.sub(r'<[^>]+>', ' ', p_['body'] + p_['bluf']).split()) / 200)))
for path, title, desc, body, slug in case_pages(memo, R, d):
    write(path, page(path, title, desc, body, case=slug))
strip_tags = lambda t: re.sub(r'<[^>]+>', '', t)

# ---------------- index (home) and case list
LANGS = Counter(r['lang'] for r in d['repos'] if r['lang'])
S = sources() + case_sources()
by_case_no = sorted(CASES, key=lambda c: c['no'], reverse=True)

def case_card(c):
    np = sum(1 for p in POSTS if p['case'] == c['slug'])
    st = '<span class="cst open">open</span>' if c['status'] == 'open' else '<span class="cst">filed</span>'
    return (f'<a class="case" href="{c["href"]}"><span class="k">{SEC[c["kind"]]["one"]} // CASE {c["no"]} {st}</span><h3>{c["title"]}</h3>'
            f'<p class="q">{c["q"]}</p><p>{c["dek"]}</p><span class="go">opened {c["opened"]} · {np} dispatches · open the file →</span></a>')

def dispatch_item(p, show_case=True):
    meta = (f'case {CASE[p["case"]]["no"]} · ' if show_case else '') + f'{p["date"]} · {p["read"]} min · <span class="conf {p["conf"][0]}">{p["conf"][1]}</span>'
    return f'<a class="dispatch" href="/blog/{p["slug"]}/"><span class="no">DSP-{p["no"]}</span><div><h3>{p["title"]}</h3><p>{p["dek"]}</p></div><span class="meta">{meta}</span></a>'

langchips = ''.join(f'<a class="lchip" href="/repos/?lang={esc(l)}">{esc(l)} <span>{c:,}</span></a>' for l, c in LANGS.most_common(14))
latest = ''.join(dispatch_item(p) for p in sorted(POSTS, key=lambda p: (p['date'], p['no']), reverse=True)[:6])
def sec_cases(k): return [c for c in by_case_no if c['kind'] == k]
def sec_block(x, h='h2'):
    cs = sec_cases(x['key'])
    cards = ''.join(case_card(c) for c in cs) or '<p class="dim">Nothing filed here yet.</p>'
    return (f'<section aria-labelledby="s-{x["key"]}"><{h} class="sec" id="s-{x["key"]}"><a href="{x["href"]}">{x["title"]}</a></{h}>'
            f'<p class="prose dim" style="margin:0 0 10px">{x["dek"]}</p><div class="cases">{cards}</div></section>')
home = f"""
<header class="memo hero"><span class="stamp">Open files</span><div class="eyebrow">Index // four sections</div><h1>stuff my agent found</h1>
<p class="lede">I research the tech I'm about to build on with an AI agent. This is where it files what it finds, in four sections: <a href="/projects/">projects</a> it took apart, <a href="/approaches/">approaches</a> it compared, the <a href="/repos/">repos</a> it measured, and the <a href="/practices/">agentic coding practices</a> that are working. Every claim has a confidence level and a source.</p></header>
<div class="strip" aria-label="Totals">
  <div><div class="v">{len(CASES)}</div><div class="l">case files</div></div>
  <div><div class="v">{len(d['repos']):,}</div><div class="l">repos measured</div></div>
  <div><div class="v">{len(LANGS)}</div><div class="l">languages</div></div>
  <div><div class="v">{len(POSTS)}</div><div class="l">dispatches filed</div></div>
  <div><div class="v">{len(S)}</div><div class="l">sources read</div></div>
</div>
<nav class="secmap" aria-label="Sections">{''.join(f'<a href="{x["href"]}"><span class="k">0{i+1} // {x["label"]}</span><strong>{x["title"]}</strong><span>{x["dek"]}</span></a>' for i, x in enumerate(SECTIONS))}</nav>
{sec_block(SEC['projects'])}
{sec_block(SEC['approaches'])}
<section aria-labelledby="lang-h"><h2 class="sec" id="lang-h"><a href="/repos/">Repos</a></h2>
  <p class="prose dim" style="margin:0 0 10px">{SEC['repos']['dek']} Press <span class="kbd">⌘K</span> and type a language, a category word like <em>sync</em> or <em>ui</em>, or a project name.</p>
  <div class="lchips">{langchips}<a class="lchip" href="/repos/?all=1">all languages <span>{len(d['repos']):,}</span></a></div></section>
{sec_block(SEC['practices'])}
<section aria-labelledby="dsp-h"><h2 class="sec" id="dsp-h">Latest dispatches</h2><div class="dispatches">{latest}</div><p class="prose"><a href="/blog/">All {len(POSTS)} dispatches →</a></p></section>
"""
write('/', page('/', BRAND, 'Field notes on the tech I research with an AI agent: projects taken apart, approaches compared, repos measured from the GitHub API, and agentic coding practices that work.', home))
SEC_EXTRA = {
  'projects': '',
  'approaches': '',
  'practices': '<div class="prose"><p>Related: <a href="/approaches/clojure/agents/">why Clojure suits coding agents</a> (case 001), <a href="/approaches/frontend-sync/cljs-cost/">does ClojureScript cost you when agents write it?</a> (case 002), and <a href="/for-agents/">how to point your own agent at this site</a>.</p></div>',
}
for x in SECTIONS:
    if x['key'] == 'repos': continue
    cs = sec_cases(x['key'])
    np_ = sum(1 for p in POSTS if CASE[p['case']]['kind'] == x['key'])
    write(x['href'], page(x['href'], x['title'], x['dek'], f"""
{memo(x['title'], x['dek'], 'Index', eyebrow=f"Section // {x['label']}")}
<div class="cases">{''.join(case_card(c) for c in cs)}</div>
{SEC_EXTRA[x['key']]}
<section><h2 class="sec">Dispatches in {x['label']}</h2><div class="dispatches">{''.join(dispatch_item(p) for p in POSTS if CASE[p['case']]['kind'] == x['key'])}</div><p class="dim">{np_} dispatches.</p></section>"""))

# ---------------- dispatches (blog)
groups = ''.join(f'<h2 class="sec">Case {c["no"]} // {c["short"]}</h2><div class="dispatches">{"".join(dispatch_item(p, False) for p in POSTS if p["case"] == c["slug"])}</div>'
                 for c in by_case_no if any(p['case'] == c['slug'] for p in POSTS))
write('/blog/', page('/blog/', 'Dispatches', 'Every finding from every case file, written up with data and sources.', f'''
{memo('Dispatches', 'Every finding from every case file, filed as a short report with data, callouts and sources', eyebrow='Dispatches // archive')}
<div class="prose"><p>Each dispatch takes one finding and shows the evidence: live tables from the dataset, quotes from the people building these tools, and what to do with it. Subscribe with the <a href="/blog/feed.xml">Atom feed</a>.</p></div>
{groups}'''))
for c in CASES:
    cp = [p for p in POSTS if p['case'] == c['slug']]
    for i, p in enumerate(cp):
        prev = cp[i-1] if i > 0 else None; nxt = cp[i+1] if i + 1 < len(cp) else None
        pn = ('<nav class="prose" aria-label="More dispatches" style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;border-top:1px solid var(--rule);padding-top:14px">'
              + (f'<a href="/blog/{prev["slug"]}/">← DSP-{prev["no"]} {prev["title"]}</a>' if prev else '<span></span>')
              + (f'<a href="/blog/{nxt["slug"]}/">DSP-{nxt["no"]} {nxt["title"]} →</a>' if nxt else '') + '</nav>')
        extra = [('Case', f'<a href="{c["href"]}">{c["no"]} · {c["short"]}</a>'), ('Confidence', f'<span class="conf {p["conf"][0]}">{p["conf"][1]}</span>'), ('Read', f'{p["read"]} min')]
        body = f'''{memo(p['title'], p['dek'], 'Filed', extra, eyebrow=f'Dispatch // DSP-{p["no"]}', ref=c['ref'])}
<div class="bluf"><p>{p['bluf']}</p></div>
<article class="prose">{p['body']}</article>
{p.get('after', '')}
{pn}'''
        write(f'/blog/{p["slug"]}/', page(f'/blog/{p["slug"]}/', strip_tags(p['title']), strip_tags(p['dek']), body, active='/blog/'))
entries = ''.join(f'<entry><title>{esc(strip_tags(p["title"]))}</title><link href="{SITE_URL}/blog/{p["slug"]}/"/><id>{SITE_URL}/blog/{p["slug"]}/</id><updated>{p["date"]}T12:00:00Z</updated><summary>{esc(strip_tags(p["dek"]))}</summary></entry>'
                  for p in sorted(POSTS, key=lambda p: p['date'], reverse=True))
open(os.path.join(DIST, 'blog', 'feed.xml'), 'w').write(f'<?xml version="1.0" encoding="utf-8"?><feed xmlns="http://www.w3.org/2005/Atom"><title>stuff my agent found</title><link href="{SITE_URL}/blog/"/><id>{SITE_URL}/blog/</id><updated>{SNAP}T12:00:00Z</updated><author><name>stuff my agent found</name></author>{entries}</feed>')

# ---------------- sources
for x in S:
    if not any(c['slug'] in x['k'] for c in CASES): x['k'] = list(x['k']) + ['clojure']
topics = [('all', 'all')] + [(c['slug'], 'case ' + c['no']) for c in sorted(CASES, key=lambda c: c['no'])] + [('agents', 'agentic coding'), ('ecosystem', 'ecosystem'), ('frontend', 'front-end'), ('sync', 'data sync'), ('runtimes', 'runtimes'), ('talk', 'talks'), ('tool', 'tools'), ('paper', 'papers')]
chips = ''.join(f'<button type="button" data-k="{k}" aria-pressed="{"true" if k == "all" else "false"}">{l}</button>' for k, l in topics)
def src_li(s):
    ex_only = ' <span class="tag" title="Seen in search excerpts only; not fetched">excerpt only</span>' if not s.get('read', True) else ''
    return (f'<li data-k="{" ".join(s["k"] + [s["type"]])}"><span class="d">{s["date"]}</span><div><a class="t" href="{s["url"]}" target="_blank" rel="noopener">{esc(s["title"])}</a> '
            f'<span class="tag">{s["type"]}</span>{ex_only}<div class="w">{esc(s["who"])}</div><p class="s">{s["sum"]}</p></div></li>')
lis = ''.join(src_li(s) for s in sorted(S, key=lambda s: s['date'], reverse=True))
write('/sources/', page('/sources/', 'Sources', 'Every article, talk, paper, tool and dataset behind every case file.', f'''
{memo('Sources', f'{len(S)} articles, talks, papers, tools and datasets behind the case files', eyebrow='Reading list')}
<div class="prose"><p>Everything cited anywhere on the site, newest first. Filter by case or topic. Sources tagged <span class="tag">excerpt only</span> were found in search results but could not be fetched and checked in full.</p></div>
<div class="chips" data-src-filter="#src-list" role="group" aria-label="Filter sources">{chips}</div>
<ul class="src-list" id="src-list">{lis}</ul>'''))

# ---------------- repos (the library)
write('/repos/', page('/repos/', 'Repos', f'The library: search and sort all {len(d["repos"]):,} repositories from every case file by language, stars, commits, issues, recency and health.', f'''
{memo('Repos: the library', f'All {len(d["repos"]):,} repositories from every case file, in {len(LANGS)} languages', 'Index', eyebrow='Section // repos')}
<div class="prose"><p>One index for every case file, measured from the GitHub API. Filter by language, category and status; click a row for its file. The table starts with repos that had a commit in the last 12 months; untick the box to include everything. Links like <code>/repos/?lang=TypeScript</code> or <code>/repos/?repo=owner/name</code> work, and so does the <a href="/for-agents/">search API</a>: <code>/api/search?q=clojure+sync</code>.</p></div>
<div class="lchips" style="margin-bottom:14px">{langchips}</div>
<div data-explorer><p class="dim">Loading {len(d['repos']):,} repositories…</p></div>''', tabs_=('Repos pages', 'REPOS // LIBRARY', REPO_TABS)))

# ---------------- method
from content import method
write('/method/', page('/method/', 'Method', 'How repositories are found, measured and scored, and how the case files are researched.', method(memo, d, BL)))

# ---------------- 404 and redirects from the old Clojure-only paths
open(os.path.join(DIST, '404.html'), 'w').write(page('/404', 'Not found', 'Page not found.', f'''{memo('404 // no such file', 'The page you asked for is not in these files', 'Not found')}
<div class="prose"><p>Try the <a href="/">index</a>, <a href="/projects/">projects</a>, <a href="/approaches/">approaches</a>, <a href="/practices/">practices</a> or <a href="/repos/">search every repo</a>.</p></div>''', active='none'))
OLD = [('/frontend', '/approaches/clojure/frontend/'), ('/sync', '/approaches/clojure/sync/'), ('/novel', '/approaches/clojure/novel/'), ('/runtimes', '/approaches/clojure/runtimes/'), ('/why-clojure', '/approaches/clojure/agents/')]
OLD += [('/cases', '/'), ('/explore', '/repos/')]
MOVED = [('/cases/clojure', '/approaches/clojure'), ('/cases/frontend-sync', '/approaches/frontend-sync'), ('/cases/agentic-frameworks', '/practices/agentic-frameworks')]
open(os.path.join(DIST, '_redirects'), 'w').write(''.join(f'{a}/ {b} 301\n{a} {b} 301\n' for a, b in OLD) + ''.join(f'{a} {b}/ 301\n{a}/* {b}/:splat 301\n' for a, b in MOVED))

# ---------------- agent-friendly catalogs: llms.txt, TSVs, /for-agents/
clean = lambda t, n=100: re.sub(r'\s+', ' ', (t or '')).strip()[:n]
hs_ = lambda r: r['hs'] if r['hs'] is not None else '-'
cs_ = lambda r: ','.join(r.get('cs') or []) or '-'
COLS = '# repo\tlanguage\tcategory\tcases\tstars\tcommits_12mo\tlast_commit\tstatus\thealth\tdescription'
row = lambda r: '\t'.join(str(x) for x in [r['n'], r['lang'] or '-', r['cat'], cs_(r), r['s'], r['c12'], r['lc'] or '-', r['st'], hs_(r), clean(r['d'])])
os.makedirs(os.path.join(DIST, 'catalog'), exist_ok=True)
by_stars = sorted(d['repos'], key=lambda r: -r['s'])
pick = sorted([r for r in d['repos'] if r['note']], key=lambda r: (cs_(r), r['cat'], -r['s']))
PCOLS = '# repo\tlanguage\tcases\tcategory\tstars\tcommits_12mo\tlast_commit\tstatus\thealth\tnote'
prow = lambda r: '\t'.join(str(x) for x in [r['n'], r['lang'] or '-', cs_(r), r['cat'], r['s'], r['c12'], r['lc'] or '-', r['st'], hs_(r), clean(r['note'] or r['d'], 260)])
cat_tsv = PCOLS + '\n' + '\n'.join(prow(r) for r in pick) + '\n'
act_tsv = COLS + '\n' + '\n'.join(row(r) for r in by_stars if r['ld'] is not None and r['ld'] <= 365 and not r['ar']) + '\n'
all_tsv = COLS + '\n' + '\n'.join(row(r) for r in by_stars) + '\n'
cg = defaultdict(list)
for r in d['repos']: cg[r['cat']].append(r)
cats_tsv = '# category\trepos\tactive_12mo\ttop_repos_by_health\n' + '\n'.join(f"{c}\t{len(rs)}\t{sum(1 for r in rs if r['ld'] is not None and r['ld'] <= 365)}\t{', '.join(r['n'] for r in sorted([r for r in rs if r['hs'] is not None], key=lambda r: (-r['hs'], -r['s']))[:8])}" for c, rs in sorted(cg.items(), key=lambda kv: -len(kv[1]))) + '\n'
files = {'curated.tsv': cat_tsv, 'active.tsv': act_tsv, 'all.tsv': all_tsv, 'categories.tsv': cats_tsv}
for c in CASES:
    files[f'case-{c["slug"]}.tsv'] = PCOLS + '\n' + '\n'.join(prow(r) for r in pick if c['slug'] in (r.get('cs') or [])) + '\n'
for f, t in files.items(): open(os.path.join(DIST, 'catalog', f), 'w').write(t)
tok = lambda t: f'~{round(len(t) / 3.6 / 1000)}k tokens' if len(t) > 3600 else f'~{round(len(t) / 3.6)} tokens'
case_lines = '\n'.join(f"\n### {x['title']} ({SITE_URL}{x['href']})\n{x['dek']}\n" + '\n'.join(f"- Case {c['no']} ({c['status']}): {strip_tags(c['title'])}. {strip_tags(c['q'])} {SITE_URL}{c['href']}\n  Shortlist: {SITE_URL}/catalog/case-{c['slug']}.tsv ({tok(files['case-' + c['slug'] + '.tsv'])})" for c in sorted(CASES, key=lambda c: c['no']) if c['kind'] == x['key']) for x in SECTIONS if x['key'] != 'repos')
findings = '\n'.join(f"- [case {CASE[p['case']]['no']}] {strip_tags(p.get('kj') or p['title'])} ({p['conf'][1].lower()}): {SITE_URL}/blog/{p['slug']}/" for p in POSTS)
LLMS = f'''# stuff my agent found

> Open case files on technology choices, researched by an AI agent, snapshot {SNAP}: {len(d['repos']):,} GitHub repositories in {len(LANGS)} languages with stars, commits, issues, recency and a health score, plus written findings with confidence levels and sources. Clojure has the deepest coverage (every Clojure repo with 50+ stars); other languages are covered where a case needed them.

Use this file to find and compare libraries without searching the web. Pick the smallest source that answers the question:

1. Search API (best for a specific need): {SITE_URL}/api/search?q=<words>&limit=10
   Fuzzy over names, owners, categories, topics and descriptions. Category words work: ui, frontend, react, db, datalog, sql, sync, crdt, local-first, realtime, reactive, hypermedia, runtime, compiler, agent, mcp, css, routing, state, tui, desktop, mobile, test, web, validation.
   Language is a filter: include a language in the query (clojure, typescript, rust, elixir, ...) or write lang:<name>. Add &format=tsv for a compact table.
   One repo in full: {SITE_URL}/api/repo/<owner>/<name> (adds monthly commits, issues, release, license).
2. Case shortlists: hand-picked repos with notes, one file per case (below).
3. All hand-picked repos ({len(pick)} with notes, {tok(cat_tsv)}): {SITE_URL}/catalog/curated.tsv
4. Category index ({len(cg)} categories with top repos, {tok(cats_tsv)}): {SITE_URL}/catalog/categories.tsv
5. Active repos (commit in the last 12 months, {len(act):,} rows, {tok(act_tsv)}): {SITE_URL}/catalog/active.tsv
6. Everything ({len(d['repos']):,} rows, {tok(all_tsv)}): {SITE_URL}/catalog/all.tsv  (also {SITE_URL}/llms-full.txt)
7. Raw JSON (all fields): {SITE_URL}/data/radar.json

## Case files, by section
The site has four sections: projects (deep dives on one project), approaches (ways to build, compared), repos (the measured library this file indexes) and practices (agentic coding practices that work).
{case_lines}

## Fields
- status: thriving (commit <90 days and top-quartile activity) | active (<90 days) | maintained (<1 year) | stable (1-3 years quiet, few open issues) | slowing (1-3 years quiet, issues piling up) | dormant (3+ years) | moved (development left GitHub) | archived
- health: 0-100 blend of percentiles against {BL['n']:,} established Clojure repos (activity 30%, recency 25%, issue closure 15%, issue load 10%, release 10%, stars 10%). The baseline is Clojure for every language, so busy JavaScript and TypeScript projects score high easily. Across languages, compare raw commits and issues.
- cases: the case files a repo belongs to.

## How to judge a match
- Quiet is normal in Clojure: only {pct(BL['shareAct'])} of established Clojure repos had a commit this year, and the median has been silent {round(BL['ldMed']/365, 1)} years. A 'stable' Clojure library with few open issues is usually fine to depend on.
- An actively maintained Clojure library makes about {round(BL['c12']['0.5'])} commits a year (middle half {round(BL['c12']['0.25'])}-{round(BL['c12']['0.75'])}).
- Replicant and Nexus moved to Codeberg (status 'moved').

## Findings
{findings}

## Pages
- Index: {SITE_URL}/
- Projects: {SITE_URL}/projects/
- Approaches: {SITE_URL}/approaches/
- Repos (the library): {SITE_URL}/repos/
- Agentic coding practices: {SITE_URL}/practices/
- Dispatches: {SITE_URL}/blog/
- Sources ({len(S)} articles, talks, papers): {SITE_URL}/sources/
- Method: {SITE_URL}/method/
- Source code and data: {REPO_URL}
'''
open(os.path.join(DIST, 'llms.txt'), 'w').write(LLMS)
open(os.path.join(DIST, 'llms-full.txt'), 'w').write(LLMS + '\n## Full catalog (tab-separated)\n' + all_tsv)
sizes = {f: tok(t) for f, t in files.items()}
ex = lambda u: f'<pre class="code"><code>{esc(u)}</code></pre>'
case_files_li = ''.join(f'<li><a href="/catalog/case-{c["slug"]}.tsv">/catalog/case-{c["slug"]}.tsv</a>: the case {c["no"]} shortlist ({esc(c["short"])}), {sizes["case-" + c["slug"] + ".tsv"]}.</li>' for c in sorted(CASES, key=lambda c: c['no']))
snippet = f'''## Choosing libraries
Before adding a dependency, check stuff my agent found instead of searching the web:
- Search: {SITE_URL}/api/search?q=<need>&format=tsv  (add a language word to filter, e.g. "clojure")
- Hand-picked shortlist with notes: {SITE_URL}/catalog/curated.tsv
Status 'stable' is normal for finished Clojure libraries. Avoid 'slowing', 'dormant' and 'archived' unless there is no alternative.'''
fa_body = f'''{memo('For agents', 'Let coding agents find and compare libraries from these case files without crawling the web', eyebrow='Interface // machine-readable')}
<div class="bluf"><p>Point your agent at <a href="/llms.txt">/llms.txt</a>. It explains the data in about a thousand tokens and links to a search API and compact catalogs, so the agent can pull exactly as much context as it needs: one search call, a case shortlist, or the full table.</p></div>
<div class="prose">
<h2>1. Search API</h2>
<p>The same fuzzy, category-aware search as the site's <span class="kbd">⌘K</span> box, returned as compact JSON or TSV. Works with <code>curl</code>, WebFetch or any HTTP tool. Open CORS, no key.</p>
{ex(f'curl "{SITE_URL}/api/search?q=sync&limit=5&format=tsv"')}
{ex(f'curl "{SITE_URL}/api/search?q=clojure+datalog&format=tsv"')}
{ex(f'curl "{SITE_URL}/api/repo/hyperfiddle/electric"')}
<p>Category words map to groups of categories, so <code>q=ui</code>, <code>q=db</code> or <code>q=crdt</code> return the strongest projects in that space. A language word filters: <code>q=typescript sync</code>, <code>q=lang:elixir</code>. Names tolerate typos: <code>reagnet</code> finds Reagent.</p>
<h2>2. Context files</h2>
<p>Tab-separated, one repo per line. Sizes are approximate token counts.</p>
<ul>
{case_files_li}
<li><a href="/catalog/curated.tsv">/catalog/curated.tsv</a>: every hand-picked repo with notes, {sizes['curated.tsv']}. <strong>Best default to load.</strong></li>
<li><a href="/catalog/categories.tsv">/catalog/categories.tsv</a>: every category with counts and its top repos, {sizes['categories.tsv']}.</li>
<li><a href="/catalog/active.tsv">/catalog/active.tsv</a>: every repo with a commit in the last 12 months, {sizes['active.tsv']}.</li>
<li><a href="/catalog/all.tsv">/catalog/all.tsv</a> and <a href="/llms-full.txt">/llms-full.txt</a>: everything, {sizes['all.tsv']}.</li>
<li><a href="/data/radar.json">/data/radar.json</a>: raw data with every field, including monthly commits.</li>
</ul>
<h2>3. In your repo</h2>
<p>Add this to <code>AGENTS.md</code> or <code>CLAUDE.md</code>:</p>
{ex(snippet)}
<p>Using Claude Code? Copy <a href="{REPO_URL}/tree/main/skills/stuff-my-agent-found">skills/stuff-my-agent-found</a> into <code>.claude/skills/</code>, and Claude will query these files whenever you ask it to pick or compare libraries.</p>
{finding('Why this matters', '<p>The <a href="/approaches/clojure/agents/">case 001 brief on agents</a> found that agents do best when they check facts against something real instead of guessing. The REPL does that for code. This does it for the ecosystem: the agent asks which library is alive before it writes the dependency.</p>')}
</div>'''
write('/for-agents/', page('/for-agents/', 'For agents', 'llms.txt, a search API and compact catalogs so coding agents can discover and compare libraries without crawling the web.', fa_body, active='/repos/', tabs_=('Repos pages', 'REPOS // LIBRARY', REPO_TABS)))

# search index of pages
PIDX = ([dict(t='Index', u='/', k='page', d='Case files, languages and latest dispatches'), ] + [dict(t=x['title'], u=x['href'], k='page', d=x['dek']) for x in SECTIONS]
        + [dict(t=f"Case {c['no']}: {strip_tags(c['title'])}", u=c['href'], k='case', d=strip_tags(c['q'])) for c in CASES]
        + [dict(t=t, u=h, k='sector', d=f"Case {c['no']} · {c['short']}", case=c['slug']) for c in CASES for h, t in c['tabs'][1:]]
        + [dict(t='Dispatches', u='/blog/', k='page', d='All dispatches'), dict(t='Sources', u='/sources/', k='page', d='Every article, talk and paper'),
           dict(t='Repos: search every repo', u='/repos/', k='page', d='The library: search and sort all repositories by language'), dict(t='Method', u='/method/', k='page', d='How repos are found and scored'),
           dict(t='For agents', u='/for-agents/', k='page', d='llms.txt, search API and compact catalogs for coding agents')]
        + [dict(t=strip_tags(p['title']), u=f"/blog/{p['slug']}/", k='dispatch', d='DSP-' + p['no'] + ' · ' + strip_tags(p['dek'])) for p in POSTS]
        + [dict(t=x['title'], u=x['url'], k='source', d=x['who']) for x in S])
json.dump(PIDX, open(os.path.join(DIST, 'data', 'pages.json'), 'w'), separators=(',', ':'))
open(os.path.join(DIST, '_headers'), 'w').write("/assets/fonts/*\n  Cache-Control: public, max-age=31536000, immutable\n/data/*\n  Cache-Control: public, max-age=3600\n")

# sitemap + robots
urls = ['/'] + [h for h, _ in NAV if h != '/'] + [h for c in CASES for h, _ in c['tabs']] + [f'/blog/{p["slug"]}/' for p in POSTS]
open(os.path.join(DIST, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{SITE_URL}{u}</loc><lastmod>{SNAP}</lastmod></url>' for u in urls) + '</urlset>')
open(os.path.join(DIST, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n')
print('built', DIST, len(urls), 'pages')
