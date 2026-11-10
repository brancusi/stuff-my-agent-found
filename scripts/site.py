"""Build the Clojure Radar static site into dist/.  usage: python3 scripts/site.py"""
import json, os, shutil, html, datetime
from content import posts, sources, why_clojure, SECTORS

B = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DIST = os.path.join(B, 'dist')
SITE_URL = os.environ.get('SITE_URL', 'https://clojure-radar.atd-ai.workers.dev')
REPO_URL = 'https://github.com/brancusi/clojure-radar'
d = json.load(open(os.path.join(B, 'data', 'dataset.json')))
R = {r['n'].lower(): r for r in d['repos']}
BL = d['baseline']
SNAP = d['generated']
DOC = 'CLJ-RDR-' + SNAP[:7].replace('-', '')
esc = html.escape

NAV = [('/', 'brief'), ('/frontend/', 'front-end'), ('/sync/', 'data-sync'), ('/novel/', 'novel'), ('/runtimes/', 'runtimes'),
       ('/why-clojure/', 'why-clojure'), ('/blog/', 'blog'), ('/sources/', 'sources'), ('/explore/', 'explore'), ('/method/', 'method')]

def page(path, title, desc, body, crumb=None, active=None):
    active = active or path
    nav = ''.join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == active else '', l) for h, l in NAV)
    parts = [p for p in path.strip('/').split('/') if p]
    trail = '<a href="/">~/clojure-radar</a>' + ''.join(f'/<a href="/{"/".join(parts[:i+1])}/">{esc(p)}</a>' for i, p in enumerate(parts))
    full_title = title if path == '/' else f'{title} · Clojure Radar'
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
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap">
<link rel="stylesheet" href="/assets/radar.css">
<link rel="alternate" type="application/atom+xml" title="Clojure Radar blog" href="/blog/feed.xml">
<script>try{{var t=localStorage.getItem('radar-theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="banner">OSINT <span>//</span> PUBLIC RELEASE <span>//</span> {DOC} <span>//</span> SNAPSHOT {SNAP}</div>
<div class="bar"><div class="wrap">
  <a class="logo" href="/" aria-label="Clojure Radar home"><span class="mark" aria-hidden="true"></span>CLOJURE_RADAR</a>
  <nav class="primary" aria-label="Sections">{nav}</nav>
  <div class="tools"><span class="kbd" title="Press / to search">/</span><button class="ghost" id="theme" type="button">[ theme ]</button></div>
</div></div>
<div class="wrap"><div class="crumb">{trail}</div></div>
<main id="main" class="wrap"><div class="stack">
{body}
</div></main>
<footer class="foot"><div class="wrap">
  <div>CLOJURE RADAR <span>//</span> an open dossier on the Clojure ecosystem, rebuilt from the GitHub API. Snapshot {SNAP}. Analyst: <span class="redact" tabindex="0">a REPL and a lot of coffee</span>.</div>
  <div><a href="{REPO_URL}">source &amp; data on GitHub</a> · <a href="/method/">method</a> · <a href="/sources/">sources</a> · <a href="/blog/feed.xml">atom feed</a> · Not affiliated with Clojure, Cognitect or Nubank.</div>
</div></footer>
<script src="/assets/radar.js" defer></script>
</body>
</html>'''

def memo(title, subj, stamp='Public release', extra=None, eyebrow=None):
    rows = [('To', 'Clojure practitioners, tech leads, the curious'), ('From', 'Clojure Radar'), ('Date', SNAP), ('Subj', subj), ('Ref', DOC)] + (extra or [])
    dl = ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in rows)
    eb = f'<div class="eyebrow">{eyebrow}</div>' if eyebrow else ''
    return f'<header class="memo"><span class="stamp">{stamp}</span>{eb}<h1>{title}</h1><dl>{dl}</dl></header>'

def n(name, k='s'):
    v = R[name.lower()][k]
    return f'{v:,}' if isinstance(v, int) else str(v)

pct = lambda x: f'{round(100*x)}%'
act = [r for r in d['repos'] if r['ld'] is not None and r['ld'] <= 365 and not r['ar']]
new = [r for r in d['repos'] if r['cd'] <= 365 and not r['ar']]
curated = [r for r in d['repos'] if r['fa'] and r['fa'] != 'other']
POSTS = posts(R, BL, d)

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
{memo('The Clojure landscape, mapped from the repos up', 'Front-end frameworks, data sync, novel frameworks, runtimes and agentic coding in Clojure, Nov 2025 – Nov 2026', 'Open source', eyebrow='Situation report')}
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
<section aria-labelledby="sec-h"><h2 class="sec" id="sec-h">Sectors</h2><div class="sectors">{sectors}<a class="sector" href="/explore/"><span class="k">INDEX // ALL</span><h3>Explore every repo</h3><p>All {len(d['repos']):,} repositories, searchable and sortable, with filters for category, status and age.</p><span class="go">open the explorer →</span></a></div></section>
<section aria-labelledby="norm-h"><h2 class="sec" id="norm-h">What normal looks like</h2>
  <div class="grid2">
    <div class="card"><h3>Time since last commit</h3><p class="sub">{BL['n']:,} non-archived Clojure repos with 50+ stars.</p><div class="hist" data-hist="age"></div></div>
    <div class="card"><h3>Commits in the last 12 months</h3><p class="sub">Default branch only. Highlight = touched this year.</p><div class="hist" data-hist="c12"></div></div>
  </div>
  <p class="prose" style="margin-top:10px"><a href="/blog/quiet-is-normal/">Why quiet is normal in Clojure →</a></p></section>
'''
write('/', page('/', 'Clojure Radar', 'An open dossier on the Clojure ecosystem: front-end frameworks, data sync, novel frameworks, runtimes and agentic coding, with live GitHub health data for 3,000+ repos.', home))

# ---------------- sector pages
for s in SECTORS:
    if s['fa'] == 'agents': continue
    more = f'<div data-table="{s["fa"]}-more" data-cat="{s["more"]}" data-min="10" data-cols="compact" data-limit="60" data-title="Also active this year"></div>' if s.get('more') else ''
    body = f'''{memo(s['title'], s['subj'], eyebrow='Sector // ' + s['code'])}
<div class="bluf"><p>{s['bluf']}</p></div>
<div class="prose">{s['body']}</div>
<div data-table="{s['fa']}" data-sort="cat" data-title="Curated projects, by category"><p class="dim">Loading table…</p></div>
{more}
<div class="prose"><h2>Related dispatches</h2><ul>{''.join(f'<li><a href="/blog/{p["slug"]}/">{p["title"]}</a></li>' for p in POSTS if s['fa'] in p['tags'])}</ul></div>'''
    write(s['href'], page(s['href'], s['title'], s['bluf'][:155], body))

# ---------------- why clojure (agents)
write('/why-clojure/', page('/why-clojure/', 'Why Clojure for agentic coding', 'Why REPL-driven, data-oriented Clojure suits AI coding agents: the arguments, the evidence, real-world wins, counterpoints and the tooling.', why_clojure(memo, R, n)))

# ---------------- blog
items = ''.join(f'<a class="dispatch" href="/blog/{p["slug"]}/"><span class="no">DSP-{p["no"]}</span><div><h3>{p["title"]}</h3><p>{p["dek"]}</p></div><span class="meta">{p["date"]} · {p["read"]} min · <span class="conf {p["conf"][0]}">{p["conf"][1]}</span></span></a>' for p in POSTS)
write('/blog/', page('/blog/', 'Blog', 'Dispatches from the Clojure Radar: every finding from the 2026 dossier, written up with data and sources.', f'''
{memo('Dispatches', 'Every finding from the 2026 dossier, filed as a short report with data, callouts and sources', eyebrow='Blog // archive')}
<div class="prose"><p>Each dispatch takes one finding from the radar and shows the evidence: live tables from the dataset, quotes from the people building these tools, and what to do with it. Subscribe with the <a href="/blog/feed.xml">Atom feed</a>.</p></div>
<div class="dispatches">{items}</div>'''))
for i, p in enumerate(POSTS):
    prev = POSTS[i-1] if i > 0 else None; nxt = POSTS[i+1] if i + 1 < len(POSTS) else None
    pn = '<nav class="prose" aria-label="More dispatches" style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;border-top:1px solid var(--rule);padding-top:14px">' + (f'<a href="/blog/{prev["slug"]}/">← DSP-{prev["no"]} {prev["title"]}</a>' if prev else '<span></span>') + (f'<a href="/blog/{nxt["slug"]}/">DSP-{nxt["no"]} {nxt["title"]} →</a>' if nxt else '') + '</nav>'
    body = f'''{memo(p['title'], p['dek'], 'Filed', [('Confidence', f'<span class="conf {p["conf"][0]}">{p["conf"][1]}</span>'), ('Read', f'{p["read"]} min')], eyebrow=f'Dispatch // DSP-{p["no"]}')}
<div class="bluf"><p>{p['bluf']}</p></div>
<article class="prose">{p['body']}</article>
{p.get('after', '')}
{pn}'''
    write(f'/blog/{p["slug"]}/', page(f'/blog/{p["slug"]}/', p['title'], p['dek'], body, active='/blog/'))
# atom feed
entries = ''.join(f'''<entry><title>{esc(p["title"])}</title><link href="{SITE_URL}/blog/{p["slug"]}/"/><id>{SITE_URL}/blog/{p["slug"]}/</id><updated>{p["date"]}T12:00:00Z</updated><summary>{esc(p["dek"])}</summary></entry>''' for p in POSTS)
open(os.path.join(DIST, 'blog', 'feed.xml'), 'w').write(f'<?xml version="1.0" encoding="utf-8"?><feed xmlns="http://www.w3.org/2005/Atom"><title>Clojure Radar</title><link href="{SITE_URL}/blog/"/><id>{SITE_URL}/blog/</id><updated>{SNAP}T12:00:00Z</updated><author><name>Clojure Radar</name></author>{entries}</feed>')

# ---------------- sources
S = sources()
topics = [('all', 'all'), ('agents', 'agentic coding'), ('ecosystem', 'ecosystem'), ('frontend', 'front-end'), ('sync', 'data sync'), ('runtimes', 'runtimes'), ('talk', 'talks'), ('tool', 'tools'), ('paper', 'papers')]
chips = ''.join(f'<button type="button" data-k="{k}" aria-pressed="{"true" if k == "all" else "false"}">{l}</button>' for k, l in topics)
lis = ''.join(f'''<li data-k="{' '.join(s['k'] + [s['type']])}"><span class="d">{s['date']}</span><div><a class="t" href="{s['url']}" target="_blank" rel="noopener">{esc(s['title'])}</a> <span class="tag">{s['type']}</span>{' <span class="tag" title="Seen in search excerpts only; not fetched">excerpt only</span>' if not s.get('read', True) else ''}<div class="w">{esc(s['who'])}</div><p class="s">{s['sum']}</p></div></li>''' for s in sorted(S, key=lambda s: s['date'], reverse=True))
write('/sources/', page('/sources/', 'Sources', 'Every article, talk, paper, tool and dataset behind the Clojure Radar.', f'''
{memo('Sources', f'{len(S)} articles, talks, papers, tools and datasets behind this dossier', eyebrow='Reading list')}
<div class="prose"><p>Everything cited anywhere on the site, newest first. Sources tagged <span class="tag">excerpt only</span> were found in search results but could not be fetched and checked in full.</p></div>
<div class="chips" data-src-filter="#src-list" role="group" aria-label="Filter sources">{chips}</div>
<ul class="src-list" id="src-list">{lis}</ul>'''))

# ---------------- explore
write('/explore/', page('/explore/', 'Explore', f'Search and sort all {len(d["repos"]):,} Clojure repositories by stars, commits, issues, recency and health.', f'''
{memo('Explore every repository', f'All {len(d["repos"]):,} repositories in the snapshot, searchable and sortable', eyebrow='Index // all')}
<div class="prose"><p>The table starts with repos that had a commit in the last 12 months. Untick the box to include everything. Click a column header to sort and a row to open its file. Press <span class="kbd">/</span> to search from any page. Links like <code>/explore/?repo=owner/name</code> open a project directly.</p></div>
<div data-explorer><p class="dim">Loading {len(d['repos']):,} repositories…</p></div>'''))

# ---------------- method
from content import method
write('/method/', page('/method/', 'Method', 'How the Clojure Radar finds repositories, measures them and scores health against Clojure norms.', method(memo, d, BL)))

# ---------------- 404
open(os.path.join(DIST, '404.html'), 'w').write(page('/404', 'Not found', 'Page not found.', f'''{memo('404 // no such file', 'The page you asked for is not in this dossier', 'Not found')}
<div class="prose"><p>Try the <a href="/">brief</a>, the <a href="/blog/">blog</a> or <a href="/explore/">search every repo</a>.</p></div>''', active='none'))

# sitemap + robots
urls = ['/'] + [h for h, _ in NAV if h != '/'] + [f'/blog/{p["slug"]}/' for p in POSTS]
open(os.path.join(DIST, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{SITE_URL}{u}</loc><lastmod>{SNAP}</lastmod></url>' for u in urls) + '</urlset>')
open(os.path.join(DIST, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n')
print('built', DIST, len(urls), 'pages')
