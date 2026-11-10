// stuff my agent found API (Cloudflare Worker). Static pages are served from assets; /api/* runs here.
// Endpoints: /api, /api/search?q=, /api/repo/<owner>/<name>, /api/categories
import '../site/assets/search-core.js';

let cache = null;
async function load(env, url) {
  if (cache) return cache;
  const get = p => env.ASSETS.fetch(new Request(new URL(p, url))).then(r => r.json());
  const [data, pages] = await Promise.all([get('/data/radar.json'), get('/data/pages.json')]);
  cache = { data, pages, by: new Map(data.repos.map(r => [r.n.toLowerCase(), r])) };
  return cache;
}
const H = { 'access-control-allow-origin': '*', 'cache-control': 'public, max-age=600' };
const json = (o, status = 200) => new Response(JSON.stringify(o), { status, headers: { ...H, 'content-type': 'application/json; charset=utf-8' } });
const text = (t, status = 200) => new Response(t, { status, headers: { ...H, 'content-type': 'text/plain; charset=utf-8' } });
const AREA = { frontend: 'front-end', sync: 'data-sync', novel: 'novel', runtimes: 'runtimes', agents: 'agentic-coding' };
const compact = r => ({ repo: r.n, language: r.lang || null, category: r.cat, cases: r.cs || [], area: AREA[r.fa] || null, stars: r.s, commits_12mo: r.c12, last_commit: r.lc, status: r.st, health: r.hs,
  description: r.d || null, note: r.note || null, url: 'https://github.com/' + r.n });
const full = (r, months) => ({ ...compact(r), forks: r.f, open_issues: r.oi, closed_issues: r.ci, open_prs: r.op, merged_prs: r.mp, commits_all: r.c,
  created: r.cr, latest_release: r.rel, release_date: r.rd, license: r.lic, language: r.lang, topics: r.tp, homepage: r.h || null, archived: r.ar,
  moved_to: r.mv || null, awesome_clojure_section: r.aw || null, deref_debut: r.deb || null,
  health_parts: r.hc ? Object.fromEntries(['activity', 'recency', 'issue_closure', 'issue_load', 'release', 'adoption'].map((k, i) => [k, r.hc[i]])) : null,
  monthly_commits: r.m ? Object.fromEntries(months.map((m, i) => [m.slice(0, 7), r.m[i]])) : null });
const tsvRow = r => [r.n, r.lang || '-', r.cat, (r.cs || []).join(',') || '-', r.s, r.c12, r.lc || '-', r.st, r.hs ?? '-', (r.d || '').replace(/\s+/g, ' ').slice(0, 100)].join('\t');

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (!url.pathname.startsWith('/api')) return env.ASSETS.fetch(request);
    if (request.method === 'OPTIONS') return new Response(null, { headers: { ...H, 'access-control-allow-methods': 'GET' } });
    // abuse guard: per-IP rate limit (Workers Rate Limiting binding; free on all plans)
    if (env.API_LIMITER) {
      const ip = request.headers.get('cf-connecting-ip') || 'anon';
      const { success } = await env.API_LIMITER.limit({ key: ip });
      if (!success) return json({ error: 'Rate limit: 60 requests per minute. For bulk use, download /catalog/all.tsv or /data/radar.json once.' }, 429);
    }
    const memoKey = url.pathname + url.search;
    const hit = memo.get(memoKey); if (hit) return new Response(hit.body, { status: hit.status, headers: hit.headers });
    const res = await route(request, env, url);
    if (res.status === 200 && memo.size < 2000) { const body = await res.clone().text(); memo.set(memoKey, { body, status: 200, headers: [...res.headers] }); }
    return res;
  },
};

const memo = new Map(); // per-isolate memo of identical requests (Cache API is not available on workers.dev)
async function route(request, env, url) {
    const { data, pages, by } = await load(env, url);
    const path = url.pathname.replace(/\/+$/, '');
    if (path === '/api') return json({
      name: 'stuff my agent found API', snapshot: data.generated, repos: data.repos.length,
      endpoints: {
        '/api/search?q=<words>&limit=10&format=json|tsv': 'Fuzzy search over repo names, owners, categories, topics and descriptions. Category words work: ui, frontend, db, datalog, sync, crdt, local-first, runtime, agent, css, tui, test, web, hypermedia. A language filters: clojure, typescript, lang:elixir.',
        '/api/repo/<owner>/<name>': 'Full record for one repo, including monthly commits and health breakdown.',
        '/api/categories': 'Every category with repo counts and the top repos in each.',
      },
      files: { '/llms.txt': 'Start here: how the data is organised', '/catalog/case-<slug>.tsv': 'One case file\'s shortlist (clojure, frontend-sync, agentic-frameworks)', '/catalog/curated.tsv': 'Hand-picked projects with notes', '/catalog/active.tsv': 'Every repo with a commit in the last 12 months', '/catalog/all.tsv': 'Every repo', '/catalog/categories.tsv': 'Category index' },
      fields: { status: 'thriving|active|maintained|stable|slowing|dormant|moved|archived', health: '0-100, percentile blend vs the Clojure baseline' },
    });
    if (path === '/api/search') {
      const q = (url.searchParams.get('q') || '').slice(0, 200);
      const limit = Math.min(50, Math.max(1, +url.searchParams.get('limit') || 10));
      if (!q.trim()) return json({ error: 'Pass a query, e.g. /api/search?q=datalog+sync' }, 400);
      const res = globalThis.RadarSearch.search(data, pages, q, { repos: limit, cats: 5, pages: 5 });
      if (url.searchParams.get('format') === 'tsv') return text('# repo\tlanguage\tcategory\tcases\tstars\tcommits_12mo\tlast_commit\tstatus\thealth\tdescription\n' + res.repos.map(x => tsvRow(x.r)).join('\n') + '\n');
      return json({ query: q, language_filter: res.lang || null, snapshot: data.generated,
        categories: res.cats.map(c => ({ category: c.c, repos: c.n, browse: url.origin + '/explore/?all=1&cat=' + encodeURIComponent(c.c) })),
        pages: res.pages.map(({ p }) => ({ title: p.t, kind: p.k, url: p.u.startsWith('http') ? p.u : url.origin + p.u })),
        repos: res.repos.map(x => compact(x.r)) });
    }
    const m = path.match(/^\/api\/repo\/([^/]+)\/([^/]+)$/);
    if (m) { const r = by.get((decodeURIComponent(m[1]) + '/' + decodeURIComponent(m[2])).toLowerCase()); return r ? json(full(r, data.months)) : json({ error: 'Not in the snapshot. Try /api/search?q=' + m[2] }, 404); }
    if (path === '/api/categories') {
      const g = new Map(); data.repos.forEach(r => { if (!g.has(r.cat)) g.set(r.cat, []); g.get(r.cat).push(r); });
      return json([...g].map(([c, rs]) => ({ category: c, repos: rs.length, active_12mo: rs.filter(r => r.ld != null && r.ld <= 365).length,
        top: rs.filter(r => r.hs != null).sort((a, b) => b.hs - a.hs || b.s - a.s).slice(0, 8).map(r => r.n) })).sort((a, b) => b.repos - a.repos));
    }
    return json({ error: 'Unknown endpoint. See /api' }, 404);
}
