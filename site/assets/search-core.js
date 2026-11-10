/* Clojure Radar search core: fuzzy matching + category synonyms. Shared by the site (browser) and the /api/search Worker. */
(function (G) {
  'use strict';
  const STARS = r => Math.log10(r.s + 1);
  const GROUPS = {
    frontend: ['React wrapper', 'Non-React UI', 'State management', 'Routing', 'CSS', 'Component library', 'HTML', 'Mobile', 'Desktop UI', 'Front-end / UI', 'GUI', 'HTML Manipulation', 'Terminal UI'],
    db: ['Data sync / DB', 'Data / DB', 'Database', 'ORM and SQL generation', 'Connection pools', 'Structural Migrations', 'Redis', 'Database Cli'],
    sync: ['Data sync / DB', 'Reactive', 'Novel / reactive'],
    reactive: ['Reactive', 'Concurrency / async', 'Async processing', 'Novel / reactive'],
    runtime: ['Novel / runtime', 'Runtime / compiler', 'Language / runtime', 'Languages'],
    ai: ['Agent tooling', 'AI / LLM', 'Machine Learning'],
    web: ['Web / HTTP', 'HTTP', 'Web server', 'RESTful API', 'Web Framework', 'Full-stack framework', 'Hypermedia / server-driven', 'WebSocket', 'GraphQL API'],
    css: ['CSS'], routing: ['Routing'], state: ['State management'], test: ['Testing', 'Webdriver automation'],
    tooling: ['Dev tooling', 'Build tooling', 'Editor Plugins', 'Code Analysis and Linter', 'Debugging', 'Build Automation and Package management'],
    desktop: ['Desktop UI', 'GUI', 'Terminal UI'], mobile: ['Mobile'],
    data: ['Data science', 'Science and Data Analysis', 'Machine Learning', 'Data'],
    hypermedia: ['Hypermedia / server-driven'], fullstack: ['Full-stack framework', 'Web Framework'],
    games: ['Games / art / music', 'Game Development', 'Audio'], validation: ['Data Validation', 'Data'],
  };
  const SYN = {
    ui: 'frontend', frontend: 'frontend', 'front-end': 'frontend', fe: 'frontend', react: 'frontend', component: 'frontend', components: 'frontend', dom: 'frontend', view: 'frontend', spa: 'frontend', browser: 'frontend', cljs: 'frontend',
    db: 'db', database: 'db', databases: 'db', datalog: 'db', sql: 'db', storage: 'db', store: 'db', persistence: 'db', postgres: 'db', sqlite: 'db',
    sync: 'sync', realtime: 'sync', 'real-time': 'sync', 'local-first': 'sync', offline: 'sync', crdt: 'sync',
    reactive: 'reactive', frp: 'reactive', signals: 'reactive', stream: 'reactive', streams: 'reactive', async: 'reactive', dataflow: 'reactive',
    runtime: 'runtime', runtimes: 'runtime', compiler: 'runtime', language: 'runtime', lang: 'runtime', dialect: 'runtime', interpreter: 'runtime', native: 'runtime',
    ai: 'ai', llm: 'ai', agent: 'ai', agents: 'ai', agentic: 'ai', mcp: 'ai', claude: 'ai', gpt: 'ai', ml: 'ai',
    web: 'web', http: 'web', server: 'web', backend: 'web', 'back-end': 'web', api: 'web', rest: 'web', ring: 'web', websocket: 'web',
    css: 'css', style: 'css', styles: 'css', styling: 'css', router: 'routing', routing: 'routing', routes: 'routing', state: 'state',
    test: 'test', tests: 'test', testing: 'test', tool: 'tooling', tools: 'tooling', tooling: 'tooling', dev: 'tooling', devtools: 'tooling', editor: 'tooling', repl: 'tooling', lint: 'tooling', linter: 'tooling', build: 'tooling', debug: 'tooling',
    desktop: 'desktop', gui: 'desktop', tui: 'desktop', terminal: 'desktop', mobile: 'mobile', ios: 'mobile', android: 'mobile', flutter: 'mobile',
    science: 'data', stats: 'data', dataframe: 'data', notebook: 'data', hypermedia: 'hypermedia', htmx: 'hypermedia', datastar: 'hypermedia', ssr: 'hypermedia',
    fullstack: 'fullstack', 'full-stack': 'fullstack', framework: 'fullstack', game: 'games', games: 'games', music: 'games', art: 'games', schema: 'validation', validation: 'validation', spec: 'validation',
  };
  const synFor = t => { if (SYN[t]) return SYN[t]; if (t.length >= 3) { const k = Object.keys(SYN).find(k => k.length > t.length && k.startsWith(t)); if (k) return SYN[k]; } return null; };
  const BOUND = /[\s\/\-_.:]/;
  // fzf-style subsequence score; returns {s, idx} or null
  function fz(q, text) {
    if (!text) return null; const t = text.toLowerCase(); const i0 = t.indexOf(q);
    if (i0 >= 0) { const idx = []; for (let i = 0; i < q.length; i++) idx.push(i0 + i); const atB = i0 === 0 || BOUND.test(t[i0 - 1]); if (q.length <= 2 && !atB) return null;
      return { s: (atB ? 100 : 45) + q.length * (atB ? 4 : 2) + (i0 === 0 ? 30 : 0) - Math.min(20, t.length / 10), idx }; }
    if (q.length <= 3) { // short queries: initials only (e.g. "rf" -> re-frame)
      const ini = []; for (let j = 0; j < t.length; j++) if (j === 0 || BOUND.test(t[j - 1])) ini.push(j);
      let k = 0; const idx = []; for (const j of ini) { if (t[j] === q[k]) { idx.push(j); if (++k === q.length) return { s: 60 + q.length * 6, idx }; } } return null; }
    let s = 0, ti = 0, prev = -2, runs = 0; const idx = [];
    for (const ch of q) { let f = -1; for (let j = ti; j < t.length; j++) { if (t[j] === ch) { f = j; break; } } if (f < 0) return null;
      const cons = f === prev + 1; if (!cons) runs++;
      s += 2 + (cons ? 6 : 0) + (f === 0 || BOUND.test(t[f - 1]) ? 7 : 0) - Math.min(4, (f - ti) * .35); idx.push(f); prev = f; ti = f + 1; }
    return (runs <= Math.ceil(q.length / 3) && s > q.length * 4.5) ? { s, idx } : null;
  }
  const lev1 = (a, b) => { if (Math.abs(a.length - b.length) > 1) return false; let i = 0, j = 0, e = 0; while (i < a.length && j < b.length) { if (a[i] === b[j]) { i++; j++; continue; } if (++e > 1) return false;
      if (a.length > b.length) i++; else if (b.length > a.length) j++; else if (a[i + 1] === b[j] && a[i] === b[j + 1]) { i += 2; j += 2; } else { i++; j++; } } return e + (a.length - i) + (b.length - j) <= 1; };
  function search(DATA, PAGES, qraw, lim) {
    lim = lim || {};
    const q = qraw.trim().toLowerCase(); const toks = q.split(/\s+/).filter(Boolean); const out = { cats: [], pages: [], repos: [] };
    if (!toks.length) return out;
    const groups = new Set(toks.map(synFor).filter(Boolean)); const synCats = new Set([...groups].flatMap(g => GROUPS[g]));
    const synOnly = toks.every(t => synFor(t));
    if (DATA) {
      const counts = new Map(); DATA.repos.forEach(r => counts.set(r.cat, (counts.get(r.cat) || 0) + 1));
      out.cats = [...counts.keys()].map(c => { let s = 0, idx = null; for (const t of toks) { const m = c.toLowerCase().includes(t) ? fz(t, c) : null; if (m) { s += m.s; idx = toks.length === 1 ? m.idx : null; } else if (synCats.has(c)) s += 80; else return null; } return { c, s: s + Math.log10(counts.get(c)) * 8, idx, n: counts.get(c) }; })
        .filter(Boolean).sort((a, b) => b.s - a.s).slice(0, lim.cats || 5);
      out.repos = DATA.repos.map(r => {
        const [o, nm] = r.n.split('/'); let s = 0, idx = null;
        for (const t of toks) {
          const mn = fz(t, nm), mo = fz(t, o), mc = fz(t, r.cat), syn = synFor(t);
          let best = 0;
          if (mn && !synOnly) { best = Math.max(best, mn.s * 3); if (toks.length === 1) idx = mn.idx.map(i => i + o.length + 1); }
          if (mo && !synOnly) best = Math.max(best, mo.s * 1.6);
          if (syn && GROUPS[syn].includes(r.cat)) best = Math.max(best, 140);
          if (syn && r.fa && ({ frontend: 'frontend', db: 'sync', sync: 'sync', reactive: 'sync', runtime: 'runtimes', ai: 'agents', hypermedia: 'novel', fullstack: 'novel' })[syn] === r.fa) best = Math.max(best, 150);
          if (mc) best = Math.max(best, mc.s * 1.2);
          if (r.tp.some(x => x === t || (t.length > 2 && x.startsWith(t)))) best = Math.max(best, 110);
          if (!synOnly && t.length > 2 && r.d && r.d.toLowerCase().includes(t)) best = Math.max(best, 70);
          if (!synOnly && t.length >= 4 && (lev1(t, nm.toLowerCase()) || nm.toLowerCase().split(/[-_.]/).some(w => w.length >= 3 && lev1(t, w)))) best = Math.max(best, 260);
          if (!best) return null; s += best;
        }
        if (toks.length > 1) { const nl = nm.toLowerCase(); if (nl === toks.join('-') || nl === toks.join('') || nl === toks.join('.')) s += 400; else if (nl.includes(toks.join('-'))) s += 200; }
        return { r, s: s + STARS(r) * (synOnly ? 30 : 8) + (r.hs || 0) * (synOnly ? .6 : .15) + (r.fa ? (synOnly ? 40 : 15) : 0), idx };
      }).filter(Boolean).sort((a, b) => b.s - a.s).slice(0, lim.repos || 14);
    }
    if (PAGES) out.pages = PAGES.map(p => { let s = 0, idx = null; for (const t of toks) { const mt = fz(t, p.t), md = t.length > 2 && p.d && p.d.toLowerCase().includes(t);
        const syn = synFor(t); const sec = syn && p.k === 'sector' && ({ frontend: '/frontend/', db: '/sync/', sync: '/sync/', reactive: '/sync/', runtime: '/runtimes/', ai: '/why-clojure/', hypermedia: '/novel/', fullstack: '/novel/' })[syn] === p.u;
        if (mt) { s += mt.s * 1.4; if (toks.length === 1) idx = mt.idx; } else if (sec) s += 200; else if (md) s += 60; else return null; }
      return { p, s: s + (p.k === 'sector' ? 30 : p.k === 'page' ? 20 : p.k === 'dispatch' ? 10 : 0), idx }; }).filter(Boolean).sort((a, b) => b.s - a.s).slice(0, lim.pages || 6);
    return out;
  }
  G.RadarSearch = { search, synFor, fz, GROUPS, SYN };
})(typeof globalThis !== 'undefined' ? globalThis : this);
