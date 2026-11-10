/* Clojure Radar — client components. Progressive: every page reads fine without JS; JS adds tables, radar, explorer, drawer. */
(function () {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const store = { get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };

  // ---------- theme
  const root = document.documentElement;
  const saved = store.get('radar-theme'); if (saved) root.dataset.theme = saved;
  const tbtn = $('#theme');
  const isDark = () => root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
  const label = () => { if (tbtn) tbtn.textContent = isDark() ? '[ light ]' : '[ dark ]'; };
  if (tbtn) { label(); tbtn.addEventListener('click', () => { root.dataset.theme = isDark() ? 'light' : 'dark'; store.set('radar-theme', root.dataset.theme); label(); }); }

  // ---------- helpers
  const el = (tag, attrs = {}, ...kids) => { const e = document.createElement(tag); for (const [k, v] of Object.entries(attrs)) { if (v == null || v === false) continue; if (k === 'class') e.className = v; else if (k === 'text') e.textContent = v; else if (k === 'style') e.setAttribute('style', v); else if (k.startsWith('on')) e.addEventListener(k.slice(2), v); else e.setAttribute(k, v === true ? '' : v); } for (const c of kids.flat(Infinity)) if (c != null && c !== false) e.append(c.nodeType ? c : document.createTextNode(c)); return e; };
  const NS = 'http://www.w3.org/2000/svg';
  const sv = (tag, attrs = {}) => { const e = document.createElementNS(NS, tag); for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v); return e; };
  const fmt = n => n == null ? '—' : n >= 10000 ? (n / 1000).toFixed(0) + 'k' : n >= 1000 ? (n / 1000).toFixed(1) + 'k' : String(n);
  const full = n => n == null ? '—' : n.toLocaleString('en-US');
  const ago = d => d == null ? '—' : d < 1 ? 'today' : d < 31 ? d + 'd' : d < 365 ? Math.round(d / 30.4) + 'mo' : (d / 365).toFixed(1).replace('.0', '') + 'y';
  const STATUS = {
    thriving: 'Commit in the last 90 days, and more commits this year than 75% of established Clojure repos.',
    active: 'Commit in the last 90 days.', maintained: 'Last commit 3–12 months ago.',
    stable: 'Quiet for 1–3 years with few open issues. Typical of a finished Clojure library.',
    moved: 'Archived on GitHub because development moved to another forge. Figures are frozen.',
    slowing: 'Quiet for 1–3 years while open issues pile up.', dormant: 'No commit for over 3 years.', archived: 'Archived by its owners.'
  };
  const ORDER = Object.keys(STATUS);
  const chip = s => el('span', { class: 'st st-' + s, title: STATUS[s] || '' }, ':' + s);
  const hbar = h => { if (h == null) return el('span', { class: 'dim' }, '—'); const n = Math.round(h / 10); return el('span', { class: 'hb', title: 'Health ' + h + '/100' }, el('span', { class: 't', 'aria-hidden': 'true' }, el('b', { style: 'color:' + (h >= 70 ? 'var(--good)' : h >= 45 ? 'var(--cyan)' : h >= 25 ? 'var(--warn)' : 'var(--bad)') }, '█'.repeat(n)), '░'.repeat(10 - n)), el('span', {}, String(h))); };
  const tip = el('div', { class: 'tip', hidden: true }); document.body.append(tip);
  const showTip = (e, t) => { tip.textContent = t; tip.hidden = false; tip.style.left = Math.min(e.clientX + 12, innerWidth - tip.offsetWidth - 8) + 'px'; tip.style.top = (e.clientY - 30) + 'px'; };
  const hideTip = () => { tip.hidden = true; };

  // ---------- data (lazy; shared by tables, drawer and search)
  let DATA = null, BY = null, dataP = null;
  const getData = () => dataP || (dataP = fetch('/data/radar.json').then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }).then(d => { DATA = d; BY = new Map(d.repos.map(r => [r.n.toLowerCase(), r])); return d; }));
  // sources filter (no data needed)
  $$('[data-src-filter]').forEach(bar => { const list = $(bar.dataset.srcFilter); const btns = $$('button', bar);
    btns.forEach(b => b.addEventListener('click', () => { btns.forEach(x => x.setAttribute('aria-pressed', x === b ? 'true' : 'false')); const k = b.dataset.k;
      $$('li', list).forEach(li => { li.hidden = k !== 'all' && !li.dataset.k.split(' ').includes(k); }); })); });
  // keep the active nav item visible without moving the page
  const navEl = $('nav.primary'), cur = navEl && $('[aria-current="page"]', navEl);
  if (cur && cur.offsetLeft + cur.offsetWidth > navEl.clientWidth) navEl.scrollLeft = cur.offsetLeft - 12;
  const need = $$('[data-table],[data-radar],[data-hist],[data-kv],[data-explorer],a[data-repo]').length || new URLSearchParams(location.search).get('repo');
  if (need) getData().then(boot).catch(() => {
    $$('[data-table],[data-explorer],[data-radar]').forEach(n => n.append(el('p', { class: 'dim', style: 'padding:12px 14px' }, 'Data failed to load. Refresh the page to try again.')));
  });

  function spark(m, w = 84, h = 22) {
    const s = sv('svg', { width: w, height: h, viewBox: `0 0 ${w} ${h}`, class: 'spark', role: 'img', 'aria-label': m ? 'Monthly commits: ' + m.join(', ') : 'No monthly data' });
    if (!m) { s.append(sv('line', { x1: 0, x2: w, y1: h - 1, y2: h - 1, stroke: 'var(--rule)' })); return s; }
    const mx = Math.max(1, ...m), bw = w / m.length;
    m.forEach((v, i) => { const bh = v ? Math.max(2, (h - 2) * v / mx) : 1; const r = sv('rect', { x: i * bw + .5, width: Math.max(1, bw - 1.5), y: h - bh, height: bh, fill: v ? (i === m.length - 1 ? 'var(--signal)' : 'var(--ink-2)') : 'var(--rule)' });
      r.addEventListener('mousemove', e => showTip(e, `${(DATA.months[i] || '').slice(0, 7)}: ${v} commit${v === 1 ? '' : 's'}`)); r.addEventListener('mouseleave', hideTip); s.append(r); });
    return s;
  }
  const nameCell = r => { const [o, n] = r.n.split('/'); return el('div', {}, el('span', { class: 'pname' }, el('span', { class: 'o' }, o + '/'), n), r.deb ? [' ', el('span', { class: 'tag new', title: 'Debut release in the Clojure Deref, ' + r.deb }, 'new')] : null, r.aw ? [' ', el('span', { class: 'tag aw', title: 'Listed in awesome-clojure: ' + r.aw }, 'awesome')] : null); };
  const COLS = {
    name: { h: 'Project', get: r => r.n.toLowerCase(), cell: r => el('td', {}, nameCell(r), el('div', { class: 'pdesc', title: r.d }, r.d)) },
    cat: { h: 'Category', get: r => r.cat, cls: 'hide-sm', cell: r => el('td', { class: 'hide-sm' }, el('span', { class: 'tag' }, r.cat)) },
    s: { h: 'Stars', get: r => r.s, r: 1, cell: r => el('td', { class: 'r', title: full(r.s) }, fmt(r.s)) },
    c12: { h: 'Commits 12mo', get: r => r.c12, r: 1, cell: r => el('td', { class: 'r' }, full(r.c12)) },
    m: { h: 'Monthly', nosort: 1, cls: 'hide-sm', cell: r => el('td', { class: 'hide-sm' }, spark(r.m)) },
    c: { h: 'All commits', get: r => r.c || 0, r: 1, cls: 'hide-sm', cell: r => el('td', { class: 'r hide-sm dim' }, fmt(r.c)) },
    oi: { h: 'Issues', get: r => r.oi, r: 1, cell: r => el('td', { class: 'r' }, full(r.oi)) },
    op: { h: 'PRs', get: r => r.op, r: 1, cls: 'hide-sm', cell: r => el('td', { class: 'r hide-sm' }, full(r.op)) },
    ld: { h: 'Last commit', get: r => r.ld ?? 1e9, r: 1, asc: 1, cell: r => el('td', { class: 'r', title: r.lc || '' }, ago(r.ld)) },
    rel: { h: 'Release', get: r => r.rd || '', cls: 'hide-sm', cell: r => el('td', { class: 'hide-sm dim', title: r.rd || '' }, r.rel ? r.rel.slice(0, 16) : '—') },
    hs: { h: 'Health', get: r => r.hs ?? -1, cell: r => el('td', {}, hbar(r.hs)) },
    st: { h: 'Status', get: r => ORDER.indexOf(r.st), asc: 1, cell: r => el('td', {}, chip(r.st)) },
  };
  const PRESET = { full: ['name', 'cat', 's', 'c12', 'm', 'oi', 'op', 'ld', 'rel', 'hs', 'st'], compact: ['name', 's', 'c12', 'm', 'oi', 'ld', 'hs', 'st'], explore: ['name', 'cat', 's', 'c12', 'm', 'c', 'oi', 'op', 'ld', 'rel', 'hs', 'st'] };

  function table(rows, cols, o = {}) {
    let key = o.sort || 'hs', dir = (COLS[key].asc || key === 'cat' || key === 'name') ? 1 : -1; let limit = o.limit || Infinity;
    const tbl = el('table');
    function render() {
      const sorted = [...rows].sort((a, b) => { const x = COLS[key].get(a), y = COLS[key].get(b); return (x < y ? -1 : x > y ? 1 : 0) * dir || b.s - a.s; });
      tbl.replaceChildren(el('thead', {}, el('tr', {}, cols.map(k => { const c = COLS[k]; const th = el('th', { scope: 'col', class: [c.r ? 'r' : '', c.cls || '', c.nosort ? '' : 'sortable'].join(' '), tabindex: c.nosort ? null : '0', 'aria-sort': key === k ? (dir < 0 ? 'descending' : 'ascending') : null }, c.h);
        if (!c.nosort) { const go = () => { if (key === k) dir = -dir; else { key = k; dir = (c.asc || k === 'name' || k === 'cat') ? 1 : -1; } render(); }; th.addEventListener('click', go); th.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(); } }); }
        return th; }))));
      const tb = el('tbody'); let g = null;
      sorted.slice(0, limit).forEach(r => { if (o.group && key === 'cat' && r.cat !== g) { g = r.cat; tb.append(el('tr', { class: 'grp' }, el('td', { colspan: cols.length }, '// ' + g))); }
        tb.append(el('tr', { class: 'row', tabindex: '0', onclick: () => openDrawer(r), onkeydown: e => { if (e.key === 'Enter') openDrawer(r); } }, cols.map(k => COLS[k].cell(r)))); });
      tbl.append(tb); o.onRender && o.onRender(sorted.length);
    }
    render();
    return { el: tbl, rows(n) { rows = n; render(); }, limit(n) { limit = n; render(); } };
  }

  let booted = false;
  function boot() {
    booted = true;
    const R = DATA.repos, BL = DATA.baseline;
    // tables
    $$('[data-table]').forEach(host => {
      const area = host.dataset.table; let rows;
      if (host.dataset.repos) rows = host.dataset.repos.split(',').map(s => BY.get(s.trim().toLowerCase())).filter(Boolean);
      else if (host.dataset.cat) { const seen = new Set(R.filter(r => r.fa).map(r => r.n)); const min = +(host.dataset.min || 0); rows = R.filter(r => !r.fa && r.cat === host.dataset.cat && r.ld != null && r.ld <= 365 && !r.ar && !seen.has(r.n) && r.s >= min); }
      else rows = R.filter(r => r.fa === area);
      const t = table(rows, PRESET[host.dataset.cols || 'full'], { sort: host.dataset.sort || 'hs', group: host.dataset.sort === 'cat', limit: +(host.dataset.limit || 0) || Infinity });
      const title = host.dataset.title || 'Tracked projects';
      host.replaceChildren(el('div', { class: 'panel' }, el('header', {}, el('h3', {}, title), el('p', {}, `${rows.length} repos · click a column to sort, a row for details`)), el('div', { class: 'scroll' }, t.el)));
    });
    // baseline numbers
    $$('[data-hist]').forEach(host => { const rows = host.dataset.hist === 'age' ? BL.ageHist : BL.c12Hist; const hl = host.dataset.hist === 'age' ? [0, 1] : [];
      const mx = Math.max(...rows.map(r => r[1])), tot = rows.reduce((a, r) => a + r[1], 0);
      host.replaceChildren(...rows.map(([l, c], i) => el('div', { class: 'row' + (hl.includes(i) ? ' hl' : '') }, el('span', {}, l), el('div', {}, el('div', { class: 'bar', style: `width:${100 * c / mx}%` })), el('span', { class: 'cnt' }, `${c} · ${Math.round(100 * c / tot)}%`)))); });
    // radar
    $$('[data-radar]').forEach(host => radar(host, R));
    // explorer
    const ex = $('[data-explorer]'); if (ex) explorer(ex, R);
    // repo links in prose
    $$('a[data-repo]').forEach(a => { const r = BY.get(a.dataset.repo.toLowerCase()); if (!r) return; a.href = 'https://github.com/' + r.n; a.title = `${full(r.s)}★ · ${full(r.c12)} commits in 12 mo · last commit ${ago(r.ld)} ago · :${r.st} — click for the dossier`;
      a.addEventListener('click', e => { if (e.metaKey || e.ctrlKey || e.shiftKey) return; e.preventDefault(); openDrawer(r); }); });
    const q = new URLSearchParams(location.search).get('repo'); if (q && BY.get(q.toLowerCase())) openDrawer(BY.get(q.toLowerCase()));
  }

  // ---------- radar chart: sectors = focus areas, rings = status
  function radar(host, R) {
    const SECT = [['frontend', 'Front-end'], ['sync', 'Data sync'], ['novel', 'Novel'], ['runtimes', 'Runtimes'], ['agents', 'Agents']];
    const RINGS = [['thriving', ['thriving']], ['active', ['active']], ['maintained', ['maintained']], ['quiet', ['stable', 'slowing', 'dormant', 'moved', 'archived', 'unknown']]];
    const S = 600, C = S / 2, R0 = 36, RW = (C - R0 - 30) / RINGS.length;
    const svg = sv('svg', { viewBox: `0 0 ${S} ${S}`, role: 'img', 'aria-label': 'Radar of curated Clojure projects by sector and status' });
    const defs = sv('defs'); const grad = sv('linearGradient', { id: 'sw', x1: '0', y1: '0', x2: '1', y2: '0' }); grad.append(sv('stop', { offset: '0', 'stop-color': 'var(--signal)', 'stop-opacity': '0' }), sv('stop', { offset: '1', 'stop-color': 'var(--signal)', 'stop-opacity': '.22' })); defs.append(grad); svg.append(defs);
    RINGS.forEach((rg, i) => { const r = R0 + RW * (i + 1); svg.append(sv('circle', { cx: C, cy: C, r, class: 'ring' })); const t = sv('text', { x: C + 4, y: C - r + 12, class: 'rlab' }); t.textContent = rg[0]; svg.append(t); });
    svg.append(sv('circle', { cx: C, cy: C, r: R0, class: 'ring' }));
    const ang = i => -Math.PI / 2 + i * 2 * Math.PI / SECT.length;
    SECT.forEach((s, i) => { const a = ang(i); svg.append(sv('line', { x1: C + R0 * Math.cos(a), y1: C + R0 * Math.sin(a), x2: C + (C - 24) * Math.cos(a), y2: C + (C - 24) * Math.sin(a), class: 'spoke' }));
      const mid = a + Math.PI / SECT.length, lr = C - 10; const t = sv('text', { x: C + lr * Math.cos(mid), y: C + lr * Math.sin(mid) + 4, 'text-anchor': 'middle', class: 'slab' }); t.textContent = s[1]; svg.append(t); });
    const sweep = sv('g', { class: 'sweep' }); sweep.append(sv('path', { d: `M${C},${C} L${C},${C - (C - 30)} A${C - 30},${C - 30} 0 0,1 ${C + (C - 30) * Math.sin(Math.PI / 5)},${C - (C - 30) * Math.cos(Math.PI / 5)} Z`, fill: 'url(#sw)' })); svg.append(sweep);
    const hash = s => { let h = 2166136261; for (const c of s) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return (h >>> 0) / 4294967295; };
    const lists = [];
    SECT.forEach(([key, lab], si) => {
      const items = R.filter(r => r.fa === key);
      lists.push([lab, key, items]);
      items.forEach(r => { const ri = RINGS.findIndex(rg => rg[1].includes(r.st)); const h1 = hash(r.n), h2 = hash(r.n + '#');
        const a = ang(si) + (0.08 + 0.84 * h1) * 2 * Math.PI / SECT.length; const rad = R0 + RW * ri + RW * (0.18 + 0.64 * h2);
        const size = 2.6 + Math.min(5, Math.log10(Math.max(r.s, 1)) * 1.3);
        const b = sv('circle', { cx: C + rad * Math.cos(a), cy: C + rad * Math.sin(a), r: size, class: 'blip' + (r.cd <= 365 ? ' new' : ''), tabindex: '0', role: 'button', 'aria-label': `${r.n}, ${r.st}, ${r.s} stars` });
        b.addEventListener('mousemove', e => showTip(e, `${r.n} · ${fmt(r.s)}★ · :${r.st}`)); b.addEventListener('mouseleave', hideTip);
        b.addEventListener('click', () => openDrawer(r)); b.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openDrawer(r); } });
        svg.append(b); });
    });
    const box = el('div', { class: 'radar' }); box.append(svg);
    const side = el('div', { class: 'radar-list' }, lists.map(([lab, key, items]) => el('div', {}, el('h3', {}, el('a', { href: key === 'agents' ? '/why-clojure/' : '/' + key + '/', style: 'color:inherit;text-decoration:none' }, lab + ' →')),
      el('ol', {}, items.filter(r => r.hs != null).sort((a, b) => b.hs - a.hs).slice(0, 5).map(r => el('li', {}, el('a', { href: 'https://github.com/' + r.n, onclick: e => { e.preventDefault(); openDrawer(r); } }, r.n), el('span', {}, 'health ' + r.hs)))))));
    host.replaceChildren(el('div', { class: 'radar-wrap' }, el('div', {}, box, el('div', { class: 'legend', style: 'justify-content:center;margin-top:8px' }, el('span', {}, el('span', { class: 'dot' }), 'tracked project'), el('span', {}, el('span', { class: 'dot new' }), 'created in the last 12 months'), el('span', {}, 'blip size = stars · inner ring = most active'))), side));
  }

  // ---------- explorer
  function explorer(host, R) {
    const sp = new URLSearchParams(location.search);
    const cats = [...new Set(R.map(r => r.cat))].sort();
    const q = el('input', { type: 'search', id: 'f-q', placeholder: 'search name, description, topic', 'aria-label': 'Search repositories', value: sp.get('q') || '' });
    const cat = el('select', { id: 'f-cat', 'aria-label': 'Category' }, el('option', { value: '' }, 'all categories'), cats.map(c => el('option', { value: c }, c)));
    const st = el('select', { id: 'f-st', 'aria-label': 'Status' }, el('option', { value: '' }, 'any status'), ORDER.map(s => el('option', { value: s }, ':' + s)));
    const stars = el('select', { id: 'f-stars', 'aria-label': 'Minimum stars' }, [0, 10, 50, 100, 500, 1000].map(v => el('option', { value: v }, v ? v + '+ stars' : 'any stars')));
    const act = el('input', { type: 'checkbox', id: 'f-act', checked: sp.get('all') ? null : true }), nw = el('input', { type: 'checkbox', id: 'f-new' }), aw = el('input', { type: 'checkbox', id: 'f-aw' });
    if (sp.get('cat')) cat.value = sp.get('cat'); if (sp.get('status')) st.value = sp.get('status');
    const count = el('p', {}); let lim = 100; const more = el('button', { class: 'ghost', hidden: true }, 'show 100 more');
    const t = table([], PRESET.explore, { sort: 's', limit: lim, onRender: n => { count.textContent = `${full(n)} repositories match`; more.hidden = n <= lim; } });
    const apply = () => { const s = q.value.trim().toLowerCase();
      const rows = R.filter(r => (!s || (r.n + ' ' + r.d + ' ' + r.tp.join(' ') + ' ' + (r.note || '') + ' ' + r.cat).toLowerCase().includes(s)) && (!cat.value || r.cat === cat.value) && (!st.value || r.st === st.value) && r.s >= +stars.value && (!act.checked || (r.ld != null && r.ld <= 365)) && (!nw.checked || r.cd <= 365) && (!aw.checked || r.aw));
      lim = 100; t.limit(lim); t.rows(rows); };
    [q, cat, st, stars, act, nw, aw].forEach(n => n.addEventListener('input', apply));
    more.addEventListener('click', () => { lim += 100; t.limit(lim); });
    host.replaceChildren(el('div', { class: 'panel' }, el('div', { class: 'filters' }, q, cat, st, stars, el('label', {}, act, 'active in last 12 mo'), el('label', {}, nw, 'created in last 12 mo'), el('label', {}, aw, 'in awesome-clojure')),
      el('header', {}, count, el('p', {}, 'press / or ⌘K to search everything')), el('div', { class: 'scroll' }, t.el), el('div', { class: 'more' }, more)));
    apply();
  }

  // ---------- drawer
  let last = null;
  const scrim = el('div', { class: 'scrim', hidden: true }); const dr = el('aside', { class: 'drawer', hidden: true, role: 'dialog', 'aria-modal': 'true', 'aria-labelledby': 'dr-t' });
  document.body.append(scrim, dr);
  const rank = (v, q) => !q ? '' : v >= q['0.9'] ? 'top 10% in Clojure' : v >= q['0.75'] ? 'top 25%' : v >= q['0.5'] ? 'above median' : v >= q['0.25'] ? 'below median' : 'bottom 25%';
  function openDrawer(r) {
    last = document.activeElement; const BL = DATA.baseline;
    const cr = (r.oi + r.ci) >= 5 ? Math.round(100 * r.ci / (r.oi + r.ci)) + '%' : 'n/a';
    dr.replaceChildren(
      el('button', { class: 'ghost x', onclick: closeDrawer, 'aria-label': 'Close' }, '[ esc ]'),
      el('div', { class: 'eyebrow' }, 'FILE // ' + r.cat + (r.lang ? ' // ' + r.lang : '') + (r.lic ? ' // ' + r.lic : '')),
      el('h2', { id: 'dr-t' }, r.n),
      el('div', { class: 'tags' }, chip(r.st), r.deb ? el('span', { class: 'tag new' }, 'deref debut ' + r.deb) : null, r.cd <= 365 ? el('span', { class: 'tag new' }, 'created ' + r.cr) : el('span', { class: 'tag' }, 'since ' + r.cr.slice(0, 4)), r.aw ? el('span', { class: 'tag aw' }, 'awesome: ' + r.aw) : null, r.tp.slice(0, 5).map(t => el('span', { class: 'tag' }, t))),
      r.d ? el('p', { class: 'desc' }, r.d) : null,
      r.note ? el('p', { class: 'note' }, r.note) : null,
      r.mv ? el('p', { class: 'note' }, 'Development moved to ', el('a', { href: r.mv, target: '_blank', rel: 'noopener' }, r.mv.replace('https://', '')), '. GitHub figures below are frozen and not scored.') : null,
      el('div', { class: 'mgrid' }, [[full(r.s), 'stars', rank(r.s, BL.stars)], [full(r.c12), 'commits 12mo', r.ld <= 365 ? rank(r.c12, BL.c12) : ''], [ago(r.ld), 'since last commit', r.lc || ''],
        [full(r.oi), 'open issues', (100 * r.oi / Math.max(r.s, 1)).toFixed(1) + ' per 100★'], [full(r.op), 'open PRs', full(r.mp) + ' merged'], [cr, 'issues closed', full(r.ci) + ' all-time'],
        [fmt(r.c), 'all commits', ''], [full(r.f), 'forks', ''], [r.rel ? r.rel.slice(0, 14) : '—', 'latest release', r.rd || '']].map(([v, l, p]) => el('div', {}, el('div', { class: 'v' }, v), el('div', { class: 'l' }, l), el('div', { class: 'p' }, p)))),
    );
    if (r.m) dr.append(el('h3', { class: 'eyebrow', style: 'margin:14px 0 4px' }, `commits / month · ${(DATA.months[0] || '').slice(0, 7)} → ${(DATA.months[DATA.months.length - 1] || '').slice(0, 7)} (partial)`), spark(r.m, Math.min(520, dr.clientWidth - 44), 70));
    if (r.hc) dr.append(el('h3', { class: 'eyebrow', style: 'margin:16px 0 0' }, `health ${r.hs}/100 · percentiles vs Clojure baseline`), el('div', { class: 'comp' }, ['activity (commits 12mo)', 'recency', 'issue closure', 'open-issue load', 'release cadence', 'adoption (stars)'].map((c, i) => el('div', { class: 'row' }, el('span', {}, c), el('div', { class: 't' }, el('i', { style: `width:${r.hc[i]}%` })), el('span', {}, String(r.hc[i]))))));
    dr.append(el('div', { class: 'links' }, el('a', { href: 'https://github.com/' + r.n, target: '_blank', rel: 'noopener' }, 'github ↗'), r.h ? el('a', { href: r.h, target: '_blank', rel: 'noopener' }, 'homepage ↗') : null, el('a', { href: `https://github.com/${r.n}/issues`, target: '_blank', rel: 'noopener' }, 'issues ↗'), el('a', { href: `https://github.com/${r.n}/commits`, target: '_blank', rel: 'noopener' }, 'commits ↗'), el('a', { href: `https://clojars.org/search?q=${encodeURIComponent(r.n.split('/')[1])}`, target: '_blank', rel: 'noopener' }, 'clojars ↗'), el('a', { href: '/explore/?repo=' + encodeURIComponent(r.n) }, 'permalink')));
    dr.hidden = false; scrim.hidden = false; dr.scrollTop = 0; $('.x', dr).focus();
  }
  function closeDrawer() { dr.hidden = true; scrim.hidden = true; if (last && last.focus) last.focus(); }
  scrim.addEventListener('click', closeDrawer);
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !dr.hidden) closeDrawer(); });

  // ---------- global search (fuzzy) + shortcuts
  const { synFor, fz } = globalThis.RadarSearch; const search = q => globalThis.RadarSearch.search(DATA, PAGES, q);
  function hl(text, idx) { const f = document.createDocumentFragment(); if (!idx || !idx.length) { f.append(text); return f; } const set = new Set(idx); let buf = '', on = false;
    for (let i = 0; i < text.length; i++) { const m = set.has(i); if (m !== on) { if (buf) f.append(on ? el('mark', {}, buf) : buf); buf = ''; on = m; } buf += text[i]; } if (buf) f.append(on ? el('mark', {}, buf) : buf); return f; }

  let PAGES = null; const getPages = () => PAGES ? Promise.resolve(PAGES) : fetch('/data/pages.json').then(r => r.json()).then(p => (PAGES = p));
  const pal = el('dialog', { class: 'palette', 'aria-label': 'Search Clojure Radar' });
  const pin = el('input', { type: 'search', class: 'pin', placeholder: 'search projects, categories, pages… try “ui”, “db”, “datalog”, “uix”', 'aria-label': 'Search', autocomplete: 'off', spellcheck: 'false', role: 'combobox', 'aria-expanded': 'true', 'aria-controls': 'pal-list' });
  const plist = el('div', { class: 'plist', id: 'pal-list', role: 'listbox' });
  const pstat = el('div', { class: 'pfoot' }, el('span', {}, el('span', { class: 'kbd' }, '↑↓'), ' move  ', el('span', { class: 'kbd' }, '↵'), ' open  ', el('span', { class: 'kbd' }, 'esc'), ' close'), el('span', { class: 'pcount' }, ''));
  pal.append(el('div', { class: 'phead' }, el('span', { class: 'prompt', 'aria-hidden': 'true' }, '>'), pin), plist, pstat);
  document.body.append(pal);
  let items = [], sel = 0;
  function renderPal() {
    const q = pin.value; const res = search(q); plist.replaceChildren(); items = [];
    const add = (node, go) => { const i = items.length; node.id = 'pal-' + i; node.setAttribute('role', 'option'); node.addEventListener('mousemove', () => { if (sel !== i) { sel = i; mark(); } }); node.addEventListener('click', e => go(e)); items.push({ node, go }); plist.append(node); };
    const head = t => plist.append(el('div', { class: 'pgrp', role: 'presentation' }, t));
    if (!q.trim()) {
      head('Jump to'); (PAGES || []).filter(p => p.k !== 'source').slice(0, 10).forEach(p => add(el('div', { class: 'pitem' }, el('span', { class: 'pk' }, p.k), el('span', { class: 'pt' }, p.t), el('span', { class: 'pd' }, p.d)), () => { location.href = p.u; }));
      plist.append(el('div', { class: 'phint' }, 'Fuzzy search across ' + (DATA ? DATA.repos.length.toLocaleString('en-US') : '3,000+') + ' repos, every category and every page. Category words work too: ui, frontend, db, datalog, sync, runtime, agent, css, tui, test…'));
    } else {
      const synQ = q.trim().toLowerCase().split(/\s+/).every(t => synFor(t));
      const GRP = {
        cats: () => { if (!res.cats.length) return; head('Categories'); res.cats.forEach(c => add(el('div', { class: 'pitem' }, el('span', { class: 'pk' }, 'cat'), el('span', { class: 'pt' }, hl(c.c, c.idx)), el('span', { class: 'pd' }, c.n + ' repos →')), () => { location.href = '/explore/?all=1&cat=' + encodeURIComponent(c.c); })); },
        pages: () => { if (!res.pages.length) return; head('Pages'); res.pages.forEach(({ p, idx }) => add(el('div', { class: 'pitem' }, el('span', { class: 'pk' }, p.k), el('span', { class: 'pt' }, hl(p.t, idx)), el('span', { class: 'pd' }, p.d)), e => { if (p.k === 'source' || e.metaKey || e.ctrlKey) window.open(p.u, '_blank', 'noopener'); else location.href = p.u; })); },
        repos: () => { if (!res.repos.length) return; head(synQ ? 'Top repositories' : 'Repositories'); res.repos.forEach(({ r, idx }) => add(el('div', { class: 'pitem' }, el('span', { class: 'pk st-' + r.st }, ':' + r.st), el('span', { class: 'pt' }, hl(r.n, idx)), el('span', { class: 'pd' }, fmt(r.s) + '★ · ' + r.cat)), () => { closePal(); openDrawer(r); })); },
      };
      const top = { cats: res.cats[0] ? res.cats[0].s : 0, pages: res.pages[0] ? res.pages[0].s : 0, repos: res.repos[0] ? res.repos[0].s * .55 : 0 };
      (synQ ? ['cats', 'repos', 'pages'] : Object.keys(top).sort((x, y) => top[y] - top[x])).forEach(g => GRP[g]());
      if (!items.length) plist.append(el('div', { class: 'phint' }, DATA ? 'No matches. Try fewer letters, a category word (ui, db, sync, runtime, agent) or an owner name.' : 'Loading the index…'));
    }
    pstat.querySelector('.pcount').textContent = q.trim() ? `${items.length} result${items.length === 1 ? '' : 's'}` : '';
    sel = 0; mark();
  }
  function mark() { items.forEach((it, i) => it.node.classList.toggle('on', i === sel)); const it = items[sel]; if (it) { pin.setAttribute('aria-activedescendant', it.node.id); it.node.scrollIntoView({ block: 'nearest' }); } }
  pin.addEventListener('input', renderPal);
  pin.addEventListener('keydown', e => {
    if (e.key === 'ArrowDown' || (e.ctrlKey && e.key === 'n')) { e.preventDefault(); sel = Math.min(items.length - 1, sel + 1); mark(); }
    else if (e.key === 'ArrowUp' || (e.ctrlKey && e.key === 'p')) { e.preventDefault(); sel = Math.max(0, sel - 1); mark(); }
    else if (e.key === 'Enter') { e.preventDefault(); const it = items[sel]; if (it) it.go(e); }
  });
  pal.addEventListener('click', e => { if (e.target === pal) closePal(); });
  function openPal(prefill) { if (help.open) help.close(); if (!pal.open) pal.showModal(); if (prefill != null) pin.value = prefill; pin.select(); renderPal(); Promise.all([getData(), getPages()]).then(renderPal).catch(() => {}); }
  function closePal() { if (pal.open) pal.close(); }

  const KEYS = [['⌘K / Ctrl K', 'open search'], ['/', 'open search'], ['?', 'show this help'], ['t', 'toggle light / dark'], ['esc', 'close search, help or a project file'],
    ['g b', 'go to brief'], ['g f', 'go to front-end'], ['g d', 'go to data-sync'], ['g n', 'go to novel'], ['g r', 'go to runtimes'], ['g w', 'go to why-clojure'], ['g l', 'go to blog'], ['g s', 'go to sources'], ['g e', 'go to explore'], ['g m', 'go to method'],
    ['↑ ↓ / Ctrl N P', 'move through search results'], ['↵', 'open the selected result']];
  const GO = { b: '/', f: '/frontend/', d: '/sync/', n: '/novel/', r: '/runtimes/', w: '/why-clojure/', l: '/blog/', s: '/sources/', e: '/explore/', m: '/method/' };
  const help = el('dialog', { class: 'palette help', 'aria-labelledby': 'help-t' },
    el('div', { class: 'phead' }, el('span', { class: 'prompt', 'aria-hidden': 'true' }, '$'), el('h2', { id: 'help-t' }, 'man clojure-radar'), el('button', { class: 'ghost', type: 'button', onclick: () => help.close() }, '[ esc ]')),
    el('div', { class: 'plist' }, el('p', { class: 'phint', style: 'padding-top:4px' }, 'KEYBOARD SHORTCUTS. These work anywhere except while typing in a text field.'),
      el('table', { class: 'keys' }, el('tbody', {}, KEYS.map(([k, d]) => el('tr', {}, el('td', {}, k.split(' / ').map((x, i) => [i ? ' or ' : '', ...x.split(' ').map((y, j) => [j ? ' ' : '', el('span', { class: 'kbd' }, y)])])), el('td', {}, d)))))));
  document.body.append(help);
  help.addEventListener('click', e => { if (e.target === help) help.close(); });
  $('#search-open') && $('#search-open').addEventListener('click', () => openPal(''));
  $('#help-open') && $('#help-open').addEventListener('click', () => { closePal(); help.showModal(); });
  let gPending = 0;
  document.addEventListener('keydown', e => {
    const typing = /INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName) || document.activeElement.isContentEditable;
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); pal.open ? closePal() : openPal(''); return; }
    if (e.key === '?' && pal.open && !pin.value) { e.preventDefault(); closePal(); help.showModal(); return; }
    if (typing || e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key === '/') { e.preventDefault(); openPal(''); }
    else if (e.key === '?') { e.preventDefault(); closePal(); help.open ? help.close() : help.showModal(); }
    else if (e.key === 't' && !pal.open && !help.open) { tbtn && tbtn.click(); }
    else if (e.key === 'g') { gPending = Date.now(); }
    else if (gPending && Date.now() - gPending < 1200 && GO[e.key]) { gPending = 0; location.href = GO[e.key]; }
  });
})();
