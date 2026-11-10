"""Editorial content for Clojure Radar: sectors, dispatches (blog), why-clojure essay, method, sources."""
import re

def _a(R, name, label=None):
    r = R[name.lower()]
    return f'<a data-repo="{r["n"]}" href="https://github.com/{r["n"]}">{label or r["n"]}</a>'

def finding(label, body): return f'<div class="callout finding"><span class="lbl">{label}</span>{body}</div>'
def caveat(body, label='Caveat'): return f'<div class="callout caveat"><span class="lbl">{label}</span>{body}</div>'
def signal(body, label='Signal'): return f'<div class="callout signal"><span class="lbl">{label}</span>{body}</div>'
def intercept(quote, cite, label='Intercept'): return f'<div class="callout intercept"><span class="lbl">{label}</span><blockquote>{quote}</blockquote><cite>{cite}</cite></div>'
def stat(big, body, label='By the numbers'): return f'<div class="callout stat"><span class="lbl">{label}</span><div class="big">{big}</div><p>{body}</p></div>'
def table(repos, title, cols='compact', sort='hs'): return f'<div data-table="list" data-repos="{",".join(repos)}" data-cols="{cols}" data-sort="{sort}" data-title="{title}"><p class="dim">Loading table…</p></div>'

HIGH, MOD, LOW = ('high', 'HIGH CONFIDENCE'), ('mod', 'MODERATE CONFIDENCE'), ('low', 'LOW CONFIDENCE')

SECTORS = [
 dict(fa='frontend', code='FE', href='/frontend/', title='Front-end frameworks', more='Front-end / UI',
      subj='React wrappers, React-free renderers, state, CSS, components, desktop and mobile UI',
      blurb='Reagent, re-frame, UIx, Helix, Replicant, shadow-grove, Reagami, BareDOM and the tools around them.',
      bluf='The React wrappers are mature and slow-moving. New energy has moved to React-free renderers, web components and server-driven UIs. For a new app in 2026: re-frame on Reagent is the safe default, UIx or Helix if you want modern React directly, Replicant for a data-first React-free stack.',
      body='''<p>Everything for building browser, desktop and mobile UIs in Clojure. Rows tagged <span class="tag new">new</span> debuted in the Clojure Deref this year. Rows tagged <span class="tag aw">awesome</span> are listed in awesome-clojure.</p>
<div class="callout signal"><span class="lbl">Choosing today</span><p><strong>re-frame + Reagent</strong>: the biggest talent pool, best docs, battle-tested. <strong>UIx / Helix</strong>: modern React hooks and the npm ecosystem with almost no wrapper. <strong>Replicant + Nexus</strong>: pure functions return hiccup, with no React and no component state. Now developed on Codeberg. <strong>Reagami / Squint</strong>: tiny bundles. <strong>Mostly server-rendered?</strong> See the <a href="/novel/">novel sector</a>.</p></div>'''),
 dict(fa='sync', code='DS', href='/sync/', title='Data sync and databases', more='Data / DB',
      subj='Client databases, sync engines, reactive dataflow and the Datalog databases behind them',
      blurb='Instant, DataScript, Datahike, Datalevin, XTDB, Electric’s runtime Missionary, and replikativ’s versioned-data stack.',
      bluf='Data sync is where Clojure ideas travel furthest. Datalog over immutable facts runs on both client and server, and Instant sells that model as a product. Datalevin, XTDB and Datahike are among the most active repos in the whole ecosystem.',
      body='''<p>The common pattern is a Datalog store on the client (DataScript or Datahike) synced with a durable store on the server (Datomic, XTDB, Datahike or Datalevin), moving data as datoms or EQL queries. replikativ is pushing toward Git-like versioned, forkable data. SQLite is quietly becoming the default app database in the hypermedia crowd.</p>'''),
 dict(fa='novel', code='NV', href='/novel/', title='Novel frameworks', more=None,
      subj='Frameworks that change the shape of an app: cross-tier compilers, hypermedia, full-stack',
      blurb='Electric, Datastar and the hypermedia wave (hyper, hyperlith, stube, ripley), plus Fulcro, Biff, Kit and Clerk.',
      bluf='Two ideas compete to replace the SPA. Electric compiles one program across client and server. Datastar-style hypermedia streams server-rendered state to the browser. Hypermedia has the momentum in 2026, with five frameworks shipping and borkdude experimenting in the same space.',
      body='<p>Frameworks that change where code runs instead of wrapping a UI library. Full-stack frameworks and notebooks are included because they are how most teams experience these ideas.</p>'),
 dict(fa='runtimes', code='RT', href='/runtimes/', title='Runtimes and compilers', more=None,
      subj='ClojureScript and its lighter siblings, native hosts, and the 2026 runtime boom',
      blurb='ClojureScript, Squint, Cherry, Scittle, nbb, babashka, jank, ClojureDart, basilisp, and new hosts on Chez, Zig, Go and QuickJS.',
      bluf='Clojure is becoming a family of languages. Besides the JVM and JavaScript, there are now serious efforts on LLVM (jank), Dart, Python, Go, Chez Scheme, Zig/Wasm and QuickJS. Several of them started in 2026 and already have thousands of commits.',
      body='<p>Ways to run Clojure beyond the JVM, from the front end (Squint, Cherry, Scittle) to native binaries (jank, babashka, cream, gloat).</p>'),
 dict(fa='agents', code='AI', href='/why-clojure/', title='Agentic coding', more=None, subj='', bluf='',
      blurb='Why REPL-connected agents do well in Clojure, and the tools that make it work: clojure-mcp, ECA, Backseat Driver, re-frame-pair.', body=''),
]

def posts(R, BL, d):
    a = lambda n, l=None: _a(R, n, l)
    v = lambda n, k='s': f'{R[n.lower()][k]:,}'
    pct = lambda x: f'{round(100*x)}%'
    new = [r for r in d['repos'] if r['cd'] <= 365 and not r['ar']]
    new_ai = [r for r in new if r['cat'] == 'AI / LLM']
    aw = [r for r in d['repos'] if r['aw']]
    aw_act = sum(1 for r in aw if r['ld'] is not None and r['ld'] <= 365)
    aw_dead = sum(1 for r in aw if r['st'] in ('dormant', 'archived'))
    debut = sum(1 for r in d['repos'] if r['deb'])
    P = []

    P.append(dict(slug='quiet-is-normal', kj='Quiet is normal in Clojure', conf=HIGH, tags=['ecosystem'],
      title='Quiet is normal: what a healthy Clojure project looks like',
      dek=f'Only {pct(BL["shareAct"])} of established Clojure repos changed this year. Judged by JavaScript norms that looks like decline. Judged by Clojure norms it is how finished software behaves.',
      bluf=f'Do not read a two-year-old last commit as abandonment. The median established Clojure repo has been silent for {round(BL["ldMed"]/365,1)} years, and an actively maintained library makes about {round(BL["c12"]["0.5"])} commits a year. Every health score on this site is calibrated to that baseline.',
      body=f'''{stat(pct(BL['shareAct']), f'of the {BL["n"]:,} non-archived Clojure repos with 50+ stars had a commit in the last 12 months. {pct(BL["share90"])} had one in the last 90 days.')}
<p>Clojure's culture prizes stability. The core team rarely breaks APIs, libraries are small and composable, and authors often declare a library done. A date library that handles every edge case has no reason to change. The result is an ecosystem where most of the code is quiet and much of it is still in daily use.</p>
<h2>The baseline</h2>
<p>Across the baseline, the middle half of active repos make between {round(BL['c12']['0.25'])} and {round(BL['c12']['0.75'])} commits a year. The top 10% make {round(BL['c12']['0.9'])} or more. Median open issues: {round(BL['oiMed'])}. Median share of issues closed: {pct(BL['close']['0.5'])}. {pct(BL['relShare'])} of repos publish GitHub releases or tags. The rest ship straight to Clojars.</p>
{finding('Finding', '<p><strong>A repo with 25 commits this year and a recent release is in the top half of maintained Clojure projects.</strong> In npm terms that would look sleepy.</p>')}
<h2>How to judge a library you depend on</h2>
<ul><li><strong>Recency is a weak signal on its own.</strong> Check open issues per 100 stars. The baseline median is {BL['oiPer100']['0.5']:.1f}. A quiet repo with a short issue list is <code>:stable</code>. One with a growing pile of unanswered issues is <code>:slowing</code>.</li>
<li><strong>Look at who uses it.</strong> A quiet library inside a busy app (DataScript inside Logseq, for example) is maintained by proxy.</li>
<li><strong>Check Clojars, not just GitHub.</strong> Many authors never cut GitHub releases.</li></ul>
{caveat('<p>Commits are counted on the default branch. Work on long-lived feature branches, in monorepos or off GitHub entirely (Codeberg, GitLab, private repos) does not show up here.</p>')}''',
      after='<div class="grid2"><div class="card"><h3>Time since last commit</h3><p class="sub">Baseline repos.</p><div class="hist" data-hist="age"></div></div><div class="card"><h3>Commits in the last 12 months</h3><p class="sub">Baseline repos.</p><div class="hist" data-hist="c12"></div></div></div>'))

    P.append(dict(slug='react-wrappers-2026', kj='The React wrappers are mature; re-frame is being reinvented', conf=MOD, tags=['frontend'],
      title='The React wrappers are finished, and re-frame is being reinvented',
      dek=f'Reagent and re-frame still anchor most ClojureScript apps. UIx and Helix are the modern-hooks route. Day8 has started re-frame2.',
      bluf='Pick re-frame on Reagent for a team that values documentation and hiring. Pick UIx or Helix to stay close to modern React. Watch re-frame2, because the most influential CLJS framework is being redesigned in the open.',
      body=f'''<p>{a('reagent-project/reagent','Reagent')} ({v('reagent-project/reagent')}★) and {a('day8/re-frame','re-frame')} ({v('day8/re-frame')}★) are the installed base. Reagent made {v('reagent-project/reagent','c12')} commits this year, mostly React 18/19 compatibility. re-frame made {v('day8/re-frame','c12')} and shipped {R['day8/re-frame']['rel']}.</p>
{finding('Finding', f'<p><strong>The modern-React wrappers are deliberately thin, so they change little.</strong> {a("pitch-io/uix","UIx")} ({v("pitch-io/uix")}★) and {a("lilactown/helix","Helix")} ({v("lilactown/helix")}★) add macros over React hooks and little else. When React changes, they barely need to.</p>')}
{signal(f'<p>{a("day8/re-frame2","re-frame2")} appeared in May 2026 from the re-frame team, described as "the AI first-born of re-frame". Its commit count (about {v("day8/re-frame2","c12")} in a year) is far above anything else on the radar and almost certainly reflects imported or generated history. Compare its trajectory over time, not its raw count.</p>', 'Watch')}
<h2>Around the core</h2>
<p>{a('day8/re-com','re-com')} (components) and {a('fulcrologic/statecharts','statecharts')} are thriving. {a('shipclojure/re-frame-query','re-frame-query')} brings TanStack-Query-style data fetching to re-frame. Older glue such as kee-frame and refx is dormant or stable, so check before adopting.</p>
{caveat('<p>Om, the original 2014 React wrapper, still has the most stars of any CLJS UI library. It has been dormant for six years. Stars measure history, not health.</p>')}''',
      after=table(['reagent-project/reagent','day8/re-frame','day8/re-frame2','pitch-io/uix','lilactown/helix','tonsky/rum','funcool/rumext','day8/re-com','fulcrologic/statecharts','shipclojure/re-frame-query','day8/re-frame-10x','omcljs/om'], 'React wrappers and state')))

    P.append(dict(slug='leaving-react', kj='Momentum is leaving React', conf=MOD, tags=['frontend'],
      title='The momentum is leaving React',
      dek='Replicant, Reagami, shadow-grove, solid-cljs and a new generation of web-component kits all render without React.',
      bluf='The newest ClojureScript UI work treats React as optional. Data-driven renderers (Replicant, Reagami), compiled fragments (shadow-grove), fine-grained signals (solid-cljs, signaali) and plain web components (BareDOM, tyrell) are where the commits are.',
      body=f'''<p>For a decade "ClojureScript UI" meant "React wrapper". In 2025–26 that changed. {a('cjohansen/replicant','Replicant')} showed that a pure function returning hiccup, diffed straight to the DOM, covers most apps without component state or hooks.</p>
{signal(f'<p><strong>Replicant moved to Codeberg in November 2026.</strong> Its GitHub repo is archived and points to <a href="https://codeberg.org/cjohansen/replicant">codeberg.org/cjohansen/replicant</a>. The README gives the reason as Codeberg\'s stance on protecting free software from LLM scraping. {a("cjohansen/nexus","Nexus")}, its companion action-dispatch library, moved too. Both are marked <code>:moved</code> here and are not scored.</p>', 'Relocation')}
<h2>The React-free field</h2>
<ul><li>{a('borkdude/reagami','Reagami')}: a tiny Reagent-like API with no React, for Squint and CLJS ({v('borkdude/reagami','c12')} commits this year).</li>
<li>{a('thheller/shadow-grove','shadow-grove')}: compile-time fragments, a normalized DB and events, from the author of shadow-cljs.</li>
<li>{a('roman01la/solid-cljs','solid-cljs')} and {a('metosin/signaali','signaali')}: fine-grained reactivity in the style of Solid and signals.</li>
<li>{a('avanelsas/baredom','BareDOM')} ({v('avanelsas/baredom','c12')} commits) and {a('gersak/tyrell','tyrell')}: framework-free web components, the "just the DOM" school.</li></ul>
{finding('Finding', '<p><strong>Smaller bundles, fewer abstractions and better server rendering are pulling teams off React.</strong> Squint and ClojureScript\'s new lite mode make the payoff larger: a React-free CLJS app can now ship in kilobytes.</p>')}''',
      after=table(['cjohansen/replicant','cjohansen/nexus','borkdude/reagami','thheller/shadow-grove','roman01la/solid-cljs','metosin/signaali','chr15m/eucalypt','avanelsas/baredom','gersak/tyrell','hoplon/hoplon','kushidesign/domo','cjohansen/portfolio'], 'React-free UI')))

    P.append(dict(slug='server-driven-wave', kj='Server-driven UI is the biggest new wave', conf=HIGH, tags=['frontend', 'novel'],
      title='Server-driven UI is the biggest new wave',
      dek='Datastar and a cluster of new Clojure frameworks (hyper, hyperlith, stube, ripley) stream server state to the browser and skip the SPA.',
      bluf='If your app is mostly forms, lists and dashboards, a Clojure server streaming HTML or signals over SSE is now a mainstream option with several active frameworks. It removes the client-state layer that frameworks like re-frame exist to manage.',
      body=f'''{stat(v('starfederation/datastar'), 'stars on Datastar, the hypermedia framework (SSE plus signals) with an official Clojure SDK. It has become the default wire for new server-driven Clojure frameworks.', 'Anchor')}
<p>The idea is old (Seaside, Phoenix LiveView, htmx). What is new is how many Clojure teams are building on it at once. {a('dynamic-alpha/hyper','hyper')} started in February 2026 and has {v('dynamic-alpha/hyper','c12')} commits. {a('andersmurphy/hyperlith','hyperlith')} ({v('andersmurphy/hyperlith','c12')} commits) targets real-time multiplayer apps on SQLite. {a('zekzekus/stube','stube')} brings Seaside-style components. {a('tatut/ripley','ripley')} does live components over WebSockets.</p>
{signal(f'<p>borkdude, author of babashka, Squint and Reagami, forked hyper, Datastar and sqlite4clj in September 2026. His {a("borkdude/buzz","buzz")} experiments with defining component HTML, browser code and server state together. When the ecosystem\'s most prolific toolsmith moves somewhere, others tend to follow.</p>', 'Signal')}
{finding('Finding', '<p><strong>Hypermedia suits Clojure because Clojure already renders HTML as plain data.</strong> Hiccup on the server, immutable state and a REPL into the running server make "re-render on the server and stream the diff" feel natural.</p>')}''',
      after=table(['starfederation/datastar','starfederation/datastar-clojure','dynamic-alpha/hyper','andersmurphy/hyperlith','zekzekus/stube','tatut/ripley','borkdude/buzz','outskirtslabs/datastar-expressions','andersmurphy/sqlite4clj','weavejester/capra'], 'Server-driven UI')))

    P.append(dict(slug='data-sync-export', kj='Data sync is Clojure’s strongest export', conf=HIGH, tags=['sync'],
      title='Data sync is Clojure’s strongest export',
      dek='Instant, Datalevin, XTDB and Datahike are some of the busiest repos in the ecosystem. Datalog over immutable facts has become a sync architecture.',
      bluf='The most successful Clojure products of 2026 are data infrastructure. Instant runs a local-first sync backend written in Clojure, and the Datalog databases are among the most active repos anywhere in the ecosystem.',
      body=f'''{stat(v('instantdb/instant'), f'stars on {a("instantdb/instant","Instant")}, a real-time, local-first backend in the style of Firebase. Its server is Clojure. {v("instantdb/instant","c12")} commits this year.', 'Flagship')}
<p>Why Clojure here? Sync is about facts changing over time, and Clojure's databases model exactly that. A <em>datom</em> (entity, attribute, value, transaction) can be sent, merged and queried with Datalog on either side of the wire.</p>
<h2>The engines</h2>
<ul><li>{a('datalevin/datalevin','Datalevin')}: {v('datalevin/datalevin','c12')} commits, with LMDB, full-text and vector search.</li>
<li>{a('xtdb/xtdb','XTDB')}: {v('xtdb/xtdb','c12')} commits. v2 is bitemporal and SQL-first.</li>
<li>{a('replikativ/datahike','Datahike')}: {v('replikativ/datahike','c12')} commits, surrounded by replikativ's versioned-data stack: {a('replikativ/konserve','konserve')}, {a('replikativ/stratum','stratum')}, {a('replikativ/yggdrasil','yggdrasil')}, {a('replikativ/pg-datahike','pg-datahike')}, {a('replikativ/geschichte','geschichte')} and {a('replikativ/spindel','spindel')}.</li>
<li>{a('tonsky/datascript','DataScript')}: {v('tonsky/datascript','c12')} commits. Quiet, finished and still the client database under Logseq and most CLJS apps.</li></ul>
{finding('Finding', '<p><strong>replikativ is building Git for data.</strong> Forkable runtimes (spindel), Git-compatible version control over Datahike (geschichte), columnar storage (stratum) and a Postgres wire layer (pg-datahike) all appeared in 2026.</p>')}
{signal(f'<p>SQLite is the quiet winner among app databases: {a("andersmurphy/sqlite4clj","sqlite4clj")}, {a("maxweber/dbval","dbval")} (Datomic-like on SQLite) and {a("filipesilva/sqlatom","sqlatom")}. {a("eerohele/muutos","muutos")} turns Postgres logical replication into a change feed.</p>', 'Also rising')}''',
      after=table(['instantdb/instant','datalevin/datalevin','xtdb/xtdb','replikativ/datahike','tonsky/datascript','taoensso/sente','replikativ/konserve','replikativ/stratum','replikativ/pg-datahike','replikativ/geschichte','replikativ/spindel','wilkerlucio/pathom3','eerohele/muutos','maxweber/dbval','NyanCAD/hipflask'], 'Sync engines and databases')))

    P.append(dict(slug='electric-goes-quiet', kj='Electric has gone quiet on GitHub', conf=MOD, tags=['novel', 'sync'],
      title='Electric has gone quiet on GitHub',
      dek=f'The most ambitious idea in Clojure web development made {v("hyperfiddle/electric","c12")} public commits this year, and its last one was {R["hyperfiddle/electric"]["ld"]} days ago.',
      bluf='Electric is still the boldest design on the radar: one reactive program that the compiler splits across client and server. Public activity has slowed and v3 is source-available, so treat it as a commercial product with an open core rather than a community library.',
      body=f'''<p>{a('hyperfiddle/electric','Electric')} ({v('hyperfiddle/electric')}★) lets you write a single expression that reads a database on the server and renders DOM in the browser. The compiler places each part and streams only the diffs. Nothing else in any language does it quite this way.</p>
{caveat('<p>Low public commit counts do not mean low investment. Hyperfiddle develops partly in private, and the related ' + a('hyperfiddle/hyperfiddle','hyperfiddle') + ' repo has ' + v('hyperfiddle/hyperfiddle','c12') + ' commits this year. Electric v3 is source-available with a commercial licence, which changes who contributes and where.</p>')}
<p>Its runtime, {a('leonoel/missionary','Missionary')} ({v('leonoel/missionary','c12')} commits), is steady, and an ecosystem is forming around it: {a('LeveringIT/missionary-testkit','missionary-testkit')} for deterministic tests and {a('multiplyco/quiescent','quiescent')} for structured concurrency.</p>
{finding('Finding', '<p><strong>The hypermedia wave covers much of the same ground as Electric with plainer parts.</strong> Electric is still the most capable option for UIs where every interaction needs live server data.</p>')}''',
      after=table(['hyperfiddle/electric','hyperfiddle/hyperfiddle','leonoel/missionary','LeveringIT/missionary-testkit','multiplyco/quiescent','hyperfiddle/rcf'], 'Electric and Missionary')))

    P.append(dict(slug='runtimes-multiply', kj='Clojure runtimes are multiplying', conf=HIGH, tags=['runtimes'],
      title='Runtimes are multiplying',
      dek='Chez Scheme, Zig/Wasm, Go, QuickJS, GraalVM Crema: 2026 produced more new Clojure hosts than any year before.',
      bluf='Clojure is turning into a family of languages that share syntax, data structures and the REPL habit. jank and babashka are mature enough to bet on. The 2026 newcomers are fast-moving experiments worth watching.',
      body=f'''{stat(v('jolt-lang/jolt','c12'), f'commits in five months on {a("jolt-lang/jolt","jolt")}, Clojure on Chez Scheme, created in June 2026. {a("clojurewasm/ClojureWasm","ClojureWasm")} (Zig, calls WebAssembly) has {v("clojurewasm/ClojureWasm","c12")}. Some of that is AI-assisted development at full speed.', 'Velocity')}
<h2>The established hosts</h2>
<ul><li>{a('babashka/babashka','babashka')}: {v('babashka/babashka','c12')} commits. Fast-start native scripting, now with JLine for TUIs.</li>
<li>{a('jank-lang/jank','jank')}: {v('jank-lang/jank','c12')} commits. Native Clojure on LLVM with C++ interop, developed full-time.</li>
<li>{a('Tensegritics/ClojureDart','ClojureDart')}: Flutter apps from Clojure.</li>
<li>{a('squint-cljs/squint','Squint')} ({v('squint-cljs/squint','c12')} commits) and {a('squint-cljs/cherry','Cherry')}: ClojureScript dialects that compile to small modern JavaScript.</li></ul>
<h2>The 2026 wave</h2>
<p>{a('nooga/let-go','let-go')}, {a('glojurelang/glojure','glojure')} and {a('gloathub/gloat','gloat')} (Go; gloat is funded by Clojurists Together), {a('borkdude/cream','cream')} (GraalVM Crema), {a('squint-cljs/choq','choq')} (QuickJS, about 5 MB) and {a('RegiByte/cljam','cljam')} (an interpreter with Vite and nREPL).</p>
{finding('Finding', '<p><strong>Coding agents are lowering the cost of building a language implementation.</strong> Several 2026 runtimes have commit histories that read like agent-assisted sprints. Expect more of them, and expect most of them to be short-lived.</p>')}''',
      after=table(['babashka/babashka','jank-lang/jank','clojure/clojurescript','squint-cljs/squint','squint-cljs/cherry','babashka/scittle','babashka/nbb','Tensegritics/ClojureDart','basilisp-lang/basilisp','glojurelang/glojure','nooga/let-go','jolt-lang/jolt','clojurewasm/ClojureWasm','borkdude/cream','gloathub/gloat','squint-cljs/choq'], 'Runtimes')))

    P.append(dict(slug='ai-leads-new-projects', kj='AI tooling leads new Clojure projects', conf=MOD, tags=['agents'],
      title='AI tooling leads new Clojure projects',
      dek=f'Of {len(new)} Clojure repos created this year, {len(new_ai)} are AI or agent tools, the largest named category. The most-starred new repo is an agent orchestrator.',
      bluf='New Clojure activity is dominated by agent tooling: orchestrators, MCP servers, REPL bridges and skills. Some of it is people using Clojure to build agents. More of it is people making agents better at writing Clojure.',
      body=f'''{stat(v('unclebob/swarm-forge'), f'stars on {a("unclebob/swarm-forge","swarm-forge")}, Robert C. Martin\'s multi-agent orchestrator. It is the most-starred Clojure repo created in the last 12 months.', 'Top new repo')}
<p>The tooling splits in two. One group builds agents in Clojure: {a('redplanetlabs/agent-o-rama','agent-o-rama')} on Rama, and Nubank's agent work. The other makes coding agents good at Clojure: {a('bhauman/clojure-mcp','clojure-mcp')}, {a('bhauman/clojure-mcp-light','clojure-mcp-light')}, {a('editor-code-assistant/eca','ECA')} ({v('editor-code-assistant/eca','c12')} commits), {a('BetterThanTomorrow/calva-backseat-driver','Calva Backseat Driver')} and {a('day8/re-frame-pair','re-frame-pair')}.</p>
{caveat('<p>Repos outside the curated list are categorised by keywords, so "AI / LLM" counts are approximate. Read them as an order of magnitude, not a census.</p>')}
<p>Why Clojure attracts this work is its own question, covered in <a href="/blog/why-clojure-for-agents/">DSP-009</a> and the full <a href="/why-clojure/">why-clojure brief</a>.</p>''',
      after=table(['unclebob/swarm-forge','editor-code-assistant/eca','bhauman/clojure-mcp','bhauman/clojure-mcp-light','BetterThanTomorrow/calva-backseat-driver','redplanetlabs/agent-o-rama','unclebob/empire-2025','day8/re-frame-pair','iwillig/clojure-skills','ctford/mcp-nrepl'], 'Agent tooling')))

    P.append(dict(slug='why-clojure-for-agents', kj='Agents do their best work in Clojure when wired to a REPL', conf=MOD, tags=['agents'],
      title='Agents do their best work in Clojure when wired to a REPL',
      dek='Teams at Shortcut and Metabase, and Robert C. Martin on his own projects, report the same thing. A coding agent connected to a live REPL stops guessing and starts checking.',
      bluf='The advantage comes mostly from the live REPL rather than the syntax. Connect your agent to nREPL (clojure-mcp, clojure-mcp-light or Backseat Driver), add a paren-repair hook, and tell it to evaluate before it writes. The full argument is in the why-clojure brief.',
      body=f'''{intercept('Clojure MCP fundamentally altered my belief in the ability of LLMs to write effective Clojure code.', 'Ivan Willig, Shortcut. <a href="https://www.iwillig.me/blog/one-year-of-llm-usage-with-clojure/">One year of LLM usage with Clojure</a>, Feb 2026')}
<p>Three teams report the same pattern independently. Shortcut's 250–300K-line codebase went from "a constant source of hallucinated functions" to one-shotting tasks after clojure-mcp was connected. Metabase built ten domain subagents for its 500K-line backend and tells them to step through middleware in the REPL. Robert C. Martin built a full game, {a('unclebob/empire-2025','empire-2025')}, with role-based Claude agents across about 1,300 commits.</p>
{stat('35/35', 'delimiter errors automatically fixed by a parinfer hook across 829 agent edits in Bruce Hauman\'s log. It is the only hard number in the field so far: the famous paren problem is real, small and mechanically solvable.', 'Measured')}
{caveat('<p>No controlled study exists yet. There is no Clojure-specific agent benchmark, and MultiPL-E has not published Clojure pass@1 figures. A September 2026 audit of 93 Clojure repos found agent tooling almost undeployed: 0 with MCP configured, 2 with a paren-repair hook.</p>', 'Evidence quality')}
<p><a href="/why-clojure/"><strong>Read the full brief: Why Clojure for agentic coding →</strong></a></p>'''))

    P.append(dict(slug='awesome-clojure-audit', kj='awesome-clojure has no front-end section', conf=HIGH, tags=['ecosystem', 'frontend'],
      title='Auditing awesome-clojure: strong on the JVM, silent on the front end',
      dek=f'We checked all {len(aw)} GitHub repos in the most-starred Clojure list. {pct(aw_act/len(aw))} are still active, and Reagent, re-frame, UIx, Helix, Electric and Replicant are all missing.',
      bluf='awesome-clojure is a good map of the JVM back end and a poor map of the front end. Use it for databases, HTTP and validation libraries, and use this radar for ClojureScript UI, sync and new runtimes.',
      body=f'''{stat(pct(aw_act/len(aw)), f'of the {len(aw)} GitHub repos listed in <a href="https://github.com/razum2um/awesome-clojure">razum2um/awesome-clojure</a> had a commit in the last 12 months. {aw_dead} ({pct(aw_dead/len(aw))}) are dormant or archived.', 'Audit result')}
<p>The list is organised around back-end concerns: databases, HTTP, validation, editor plugins and debugging. Those sections hold up well. The Database section has the most active entries.</p>
{finding('Gap', '<p><strong>There is no ClojureScript UI section at all.</strong> Reagent, re-frame, UIx, Helix, Electric, Replicant, Fulcro\'s UI layer and the hypermedia frameworks are missing. Only shadow-cljs and DataScript appear, filed under build tools and databases.</p>')}
<p>Its activity rate ({pct(aw_act/len(aw))}) is close to the ecosystem baseline ({pct(BL['shareAct'])}), which is a useful check: curated lists age like the code they list. Every awesome-clojure entry is tagged <span class="tag aw">awesome</span> in the <a href="/explore/">explorer</a>, and its section names are used as categories there.</p>''',
      after='<div class="prose"><p><a href="/explore/?all=1">Open the explorer</a> and tick <em>in awesome-clojure</em> to browse all entries.</p></div>'))

    P.append(dict(slug='deref-went-quiet', kj=None, conf=MOD, tags=['ecosystem'],
      title='Field note: the Deref went quiet in June',
      dek=f'The weekly Clojure Deref, the ecosystem\'s best news source, has not published since 23 June 2026. Its archive gave this dossier {debut} debut releases.',
      bluf='Discovery for July–November 2026 leans on GitHub search, Clojurists Together updates and conference programmes. If you publish Clojure libraries, announce them on ClojureVerse and r/Clojure until the Deref returns.',
      body=f'''<p>From November 2025 to June 2026 the <a href="https://clojure.org/news/news">Clojure Deref</a> listed every notable release, and its "debut" sections were the single best source of new projects for this dossier. After 23 June, clojure.org/news carries only Clojure 1.13 alpha notes and the 2026 survey. A <a href="https://clojureverse.org/c/community-center/community-building/27">ClojureVerse thread</a> from September asks for input on its future.</p>
{signal('<p>Repos tagged <span class="tag new">new</span> on this site debuted in the Deref. Projects from after June were found by GitHub search (created since Nov 2025, 5+ stars) and by reading the Clojurists Together, Clojure/Conj 2026, Dutch Clojure Days and babashka-conf programmes.</p>', 'How we compensated')}'''))

    for i, p in enumerate(P):
        p['no'] = f'{i+1:03d}'; p['date'] = d['generated']
        words = len(re.sub(r'<[^>]+>', ' ', p['body'] + p['bluf']).split())
        p['read'] = max(2, round(words / 200))
    return P

def why_clojure(memo, R, n):
    a = lambda name, l=None: _a(R, name, l)
    claims = [
      ('The REPL is the agent’s feedback loop', MOD, 'Agents evaluate code in the running program instead of guessing and waiting on test suites. At Shortcut a 250–300K-line codebase went from "a constant source of hallucinated functions" to one-shotting tasks once clojure-mcp was connected. Metabase tells its agents to step through query-processor middleware in the REPL.',
       'Clojure is designed to be interacted with from the REPL. This turns out to be a huge advantage when working with an LLM.', 'Ivan Willig, Shortcut', ['https://www.iwillig.me/blog/one-year-of-llm-usage-with-clojure/', 'https://www.metabase.com/blog/ten-custom-subagents']),
      ('The REPL is also live documentation', MOD, '<code>clojure.repl/dir</code>, <code>doc</code>, <code>apropos</code> and <code>source</code> let an agent explore any library on the classpath. This offsets thin training data without a skill for every library.', None, None, ['https://www.iwillig.me/blog/one-year-of-llm-usage-with-clojure/', 'https://humorless.github.io/posts-output/agent-skill']),
      ('Clojure is the most token-efficient mainstream language', MOD, 'On RosettaCode tasks solved in 19 popular languages, Clojure used the fewest tokens, about 109 per task and 2.6× fewer than C, so more of the program fits in context. The author calls it "not a scientific study", and a 500K-line backend still exhausts context.', None, None, ['https://martinalderson.com/posts/which-programming-languages-are-most-token-efficient/']),
      ('Paren errors are real, and Lisp syntax makes them mechanically fixable', HIGH, 'In Bruce Hauman’s log, 35 of 829 agent edits (4.2%) had delimiter errors and a parinfer hook fixed all 35 at no token cost. The regular syntax that causes miscounts is what makes deterministic repair possible.',
       'Current frontier models … edit Clojure reliably with the built-in editors of Claude Code and Codex, and they rarely get into delimiter trouble they can’t get out of.', 'clojure-mcp README', ['https://github.com/bhauman/clojure-mcp-light', 'https://github.com/bhauman/clojure-mcp']),
      ('Code as data suits agents', MOD, 'A NeurIPS 2026 paper introduces Spell, a Lisp whose source is the model’s context window, so the agent edits and re-evaluates its own program. Frontier models learn it in-context. In practice, form-level structural edits replace fragile string matching.',
       'the program requires a language with unusual features, as its source code doubles as the content of the model’s context window.', 'Luke J. O’Connor, arXiv 2605.06898', ['https://arxiv.org/abs/2605.06898']),
      ('Agents can inspect the running app, not just the code', MOD, 're-frame-pair lets an agent read app-db, dispatch events and hot-swap handlers in a live browser app. cljfx/plorer does the same for JavaFX, and Defold’s editor AGENTS.md requires it. Backseat Driver reaches into shadow-cljs builds.',
       'A coding agent working with just static code is working with a limited perspective.', 're-frame-pair README', ['https://github.com/day8/re-frame-pair', 'https://github.com/defold/defold/blob/ae2cf1d332be9089adfe80b727c16d3cf6a2d1b7/editor/AGENTS.md']),
      ('Immutable data and contracts keep agent changes local and checkable', LOW, 'Pure functions over plain maps limit how far a bad edit can spread. Malli and spec schemas give agents something machine-readable to check against when validation fails. empire-2025 enforces atom-free specs with boundary scripts.', None, None, ['https://news.ycombinator.com/item?id=48062091', 'https://github.com/unclebob/empire-2025']),
      ('A small, convergent ecosystem leaves fewer wrong turns', LOW, 'With one dominant router, one schema library and one build tool for CLJS, the agent has fewer plausible-but-wrong choices to make.',
       'We have projects in Python, Clojure, Java, C# and Golang. Clojure is by far the least problematic to deal with… When you give an LLM a closed loop system where it can evaluate code in a live REPL… it stops guessing and starts reasoning empirically.', 'Hacker News commenter, May 2026', ['https://news.ycombinator.com/item?id=48062091']),
    ]
    cl = ''
    for i, (t, c, body, q, who, links) in enumerate(claims):
        qh = f'<blockquote style="margin:10px 0 4px;padding-left:12px;border-left:3px solid var(--signal);color:var(--ink);font-style:italic">“{q}”</blockquote><p class="dim" style="font-size:12.5px">— {who}</p>' if q else ''
        lk = ' · '.join(f'<a href="{u}">{u.split("//")[1].split("/")[0]}</a>' for u in links)
        cl += f'<div class="callout finding"><span class="lbl">Claim {i+1:02d}</span><h3 style="margin:0 0 6px;font-size:16px">{t} <span class="conf {c[0]}">{c[1]}</span></h3><p>{body}</p>{qh}<p class="dim" style="font-size:12.5px;margin-top:8px">Sources: {lk}</p></div>'
    return f'''{memo('Why Clojure for agentic coding', 'Why REPL-driven, data-oriented Lisps suit AI coding agents, and what teams have actually seen', 'Assessment', eyebrow='Brief // AI')}
<div class="bluf"><p>The advantage comes mostly from the live REPL rather than the language on paper. An agent connected to a running nREPL can evaluate a form, inspect real data and read library source before it writes, so it checks instead of guessing. Terse syntax, immutable data and machine-checkable s-expressions add to that. The weak spots, thinner training data and paren miscounting, are real and in 2026 mostly handled by tooling. Nearly all the evidence is experience reports, not controlled studies.</p></div>
<section><h2 class="sec">The case, claim by claim</h2><div class="prose">{cl}</div></section>
<section><h2 class="sec">Real-world wins</h2><div class="prose">
{finding('Shortcut', '<p>250–300K lines of Clojure. Moved from frustrating Claude Code sessions to one-shotting tasks after clojure-mcp and a REPL-first system prompt, now open-sourced as ' + a('iwillig/clojure-system-prompt','clojure-system-prompt') + '. <a href="https://www.iwillig.me/blog/one-year-of-llm-usage-with-clojure/">Read the report</a>.</p>')}
{finding('Metabase', '<p>500K-line Clojure backend. Ten domain-expert Claude Code subagents of 2–3K tokens each, told to debug through the REPL. <a href="https://www.metabase.com/blog/ten-custom-subagents">Read the write-up</a>.</p>')}
{finding('Robert C. Martin', '<p>Built ' + a('unclebob/empire-2025','empire-2025') + ', a full wargame, with role-signed Claude agents (architect, cleaner, hardener, specifier) across about 1,340 commits, guarded by CRAP scores and mutation testing. The workflow became ' + a('unclebob/swarm-forge','swarm-forge') + ', with ' + n('unclebob/swarm-forge') + ' stars.</p>')}
{finding('Defold', '<p>The game-engine editor, written in Clojure, requires agents to drive its UI through ' + a('cljfx/plorer','cljfx/plorer') + ' in a live REPL. <a href="https://github.com/defold/defold/blob/ae2cf1d332be9089adfe80b727c16d3cf6a2d1b7/editor/AGENTS.md">See its AGENTS.md</a>.</p>')}
{finding('Clojure/Conj 2026', '<p>A ten-talk AI Tools &amp; Practices Showcase (just-in-time context, Claude and Clojure setups, self-evolving agents) and a three-hour Backseat Driver workshop. <a href="https://wal.sh/events/clojure-conj/2026/workshops">Programme notes</a>.</p>')}
{signal('<p>Nubank talks about building agents <em>in</em> Clojure (LiteLLM, libpython-clj, small models), which is a different claim from agents <em>writing</em> Clojure. <a href="https://building.nu.com/building-ai-agents-in-practice-with-clojure/">Nubank Engineering</a>.</p>', 'Adjacent')}
</div></section>
<section><h2 class="sec">Counterpoints and fixes</h2><div class="prose">
{caveat('<p><strong>Thinner training data.</strong> Models default to imperative <code>doseq</code>-plus-atom code and invent functions. <strong>Fix:</strong> REPL grounding, a REPL-first system prompt, and skills that change behaviour.</p>', 'Counterpoint 01')}
{caveat('<p><strong>Paren miscounting</strong>, which Hauman calls the "Paren Edit Death Loop". <strong>Fix:</strong> parinfer hooks (' + a('bhauman/clojure-mcp-light','clojure-mcp-light') + '), <code>paren_repair</code>, the Backseat Driver balancer. It is shrinking with frontier models.</p>', 'Counterpoint 02')}
{caveat('<p><strong>Agent habits.</strong> Agents run the full test suite after every change, debug with <code>println</code>, and run cljfmt mid-session, which breaks string-matched edits. <strong>Fix:</strong> AGENTS.md rules and skills that point the agent at the REPL.</p>', 'Counterpoint 03')}
{caveat('<p><strong>No static types.</strong> Typed languages give compile-time feedback. <strong>Fix:</strong> Malli or spec as runtime contracts the agent can check against.</p>', 'Counterpoint 04')}
{caveat('<p><strong>Weak evidence.</strong> There is no Clojure-specific agent benchmark. A September 2026 audit of 93 Clojure repos found 0 with MCP configured and 2 with a paren-repair hook. Most of the ecosystem has not tried the setup that the success stories depend on.</p>', 'Counterpoint 05')}
</div></section>
<section><h2 class="sec">A working setup in five steps</h2><div class="prose"><ol>
<li>Start an nREPL in your project and connect the agent to it: {a('bhauman/clojure-mcp','clojure-mcp')}, {a('bhauman/clojure-mcp-light','clojure-mcp-light')} (<code>clj-nrepl-eval</code>) or {a('BetterThanTomorrow/calva-backseat-driver','Calva Backseat Driver')}.</li>
<li>Install a paren-repair hook so delimiter errors are fixed before the agent sees them.</li>
<li>Write an AGENTS.md or CLAUDE.md that says: evaluate before you write, explore with <code>clojure.repl</code>, run only the tests you touched, and don't reformat mid-session. Start from {a('iwillig/clojure-system-prompt','clojure-system-prompt')}.</li>
<li>Give it the running app too: {a('day8/re-frame-pair','re-frame-pair')} for re-frame, {a('cljfx/plorer','plorer')} for cljfx.</li>
<li>Add contracts (Malli) and lint (clj-kondo) as deterministic guardrails.</li></ol></div></section>
<div data-table="agents" data-title="Agent tooling, live from GitHub"><p class="dim">Loading table…</p></div>
<div class="prose"><p>Every article behind this brief is on the <a href="/sources/">sources page</a> under <em>agentic coding</em>.</p></div>'''

def method(memo, d, BL):
    return f'''{memo('Method', 'How repositories are found, measured and scored', eyebrow='Annex // A')}
<div class="prose">
<h2>Discovery</h2>
<p>GitHub search found every repo whose primary language is Clojure and that has 50+ stars: {BL['n']:,} non-archived after removing forks. That is the <strong>baseline</strong>. To it we added Clojure repos with 20–49 stars pushed since {d['since']}, repos with 5+ stars created since then, and repos tagged <code>clojure</code> or <code>clojurescript</code> that GitHub labels with another language. Then came every debut in the Clojure Deref (Nov 2025 – Jun 2026), every GitHub entry in awesome-clojure, and a hand-curated list of front-end, sync, novel, runtime and agent projects. Total: {len(d['repos']):,} repositories.</p>
<h2>Metrics</h2>
<p>From the GitHub GraphQL API on {d['generated']}: stars, forks, open and closed issues, open and merged PRs, default-branch commits (all time, last 12 months and per month), last commit date, latest release or tag, license and topics.</p>
<h2>Health score, 0–100</h2>
<p>A weighted blend of percentile ranks against the Clojure baseline:</p>
<ul><li><strong>30%</strong> activity: commits in 12 months, ranked against active repos</li><li><strong>25%</strong> recency of the last commit</li><li><strong>15%</strong> share of issues closed (neutral under 5 issues)</li><li><strong>10%</strong> open issues per star</li><li><strong>10%</strong> a release in the last year</li><li><strong>10%</strong> stars</li></ul>
<p>Archived repos are capped at 10. Repos that moved to another forge are not scored. The score is a triage aid. A finished library can be perfectly healthy with a low score, which is why the status label sits beside it.</p>
<h2>Status labels</h2>
<ul><li><code>:thriving</code> commit in 90 days and commits in the baseline's top quartile ({round(BL['c12']['0.75'])}+ a year)</li><li><code>:active</code> commit in 90 days</li><li><code>:maintained</code> commit within a year</li><li><code>:stable</code> 1–3 years quiet with few open issues</li><li><code>:slowing</code> 1–3 years quiet with issues piling up</li><li><code>:dormant</code> 3+ years quiet</li><li><code>:moved</code> development continues off GitHub</li><li><code>:archived</code> archived on GitHub</li></ul>
<h2>Categories</h2>
<p>Curated projects carry hand-written categories and notes. Other repos use their awesome-clojure section where listed, otherwise a keyword match on description and topics, which will misfile some repos.</p>
<h2>Known limits</h2>
<ul><li>Only default branches are counted, and imported histories inflate counts (re-frame2).</li><li>Off-GitHub and private development is invisible (Electric, Rama, parts of Instant, Replicant since November 2026).</li><li>Star counts reflect history as much as health.</li></ul>
<h2>Reproduce it</h2>
<p>Every script and the raw data are in the <a href="https://github.com/brancusi/clojure-radar">public repository</a>. <code>scripts/discover.py</code> → <code>enrich.py</code> → <code>monthly.py</code> → <code>build.py</code> → <code>site.py</code>.</p>
</div>'''

def sources():
    S = [
     # agentic coding
     dict(date='2026-02-21', title='One year of LLM usage with Clojure', who='Ivan Willig, Shortcut', url='https://www.iwillig.me/blog/one-year-of-llm-usage-with-clojure/', type='article', k=['agents'], sum='The most detailed production report: a 250–300K-line codebase before and after clojure-mcp, with the REPL used as live documentation.'),
     dict(date='2026-04-27', title='How we built ten custom subagents to tame a 500K-line Clojure codebase', who='Bryan Maass, Metabase', url='https://www.metabase.com/blog/ten-custom-subagents', type='article', k=['agents'], sum='Ten domain-expert Claude Code subagents with REPL-driven debugging instructions. Context cost was the main problem.'),
     dict(date='2025-05-27', title='Bruce Hauman Has Done It Again', who='Valtteri Harmainen, Metosin', url='https://www.metosin.fi/blog/2025-05-27-bruce-hauman-has-done-it-again', type='article', k=['agents'], sum='Frames clojure-mcp as closing the training-data gap, and is frank that LLMs produce unbalanced forms.'),
     dict(date='2026', title='clojure-mcp', who='Bruce Hauman', url='https://github.com/bhauman/clojure-mcp', type='tool', k=['agents'], sum='MCP server connecting agents to a live nREPL. Says frontier models now edit Clojure reliably with built-in editors.'),
     dict(date='2025-11', title='clojure-mcp-light', who='Bruce Hauman', url='https://github.com/bhauman/clojure-mcp-light', type='tool', k=['agents'], sum='clj-nrepl-eval plus parinfer paren-repair hooks. 35 of 35 delimiter errors fixed across 829 edits.'),
     dict(date='2026-01-08', title='Which programming languages are most token-efficient?', who='Martin Alderson', url='https://martinalderson.com/posts/which-programming-languages-are-most-token-efficient/', type='article', k=['agents'], sum='RosettaCode comparison: Clojure used the fewest tokens of 19 popular languages. Informal, as the author says.'),
     dict(date='2026-09-24', title='Building a Clojure Agent Environment', who='Jason Walsh', url='https://wal.sh/research/clojure-agent-environment/', type='article', k=['agents'], sum='Audit of 93 Clojure repos showing agent tooling is barely deployed. Argues deterministic tooling matters more than prompts.'),
     dict(date='2026-09-30', title='Clojure/Conj 2026 Workshops', who='Clojure/Conj', url='https://2026.clojure-conj.org/workshops', type='talk', k=['agents', 'ecosystem'], sum='AI Tools & Practices Showcase (Eric Dallo) and Backseat Driver workshop (Peter Strömberg).'),
     dict(date='2026', title='Clojure/Conj 2026 workshops, annotated', who='Jason Walsh', url='https://wal.sh/events/clojure-conj/2026/workshops', type='talk', k=['agents'], sum='The full ten-talk AI showcase list: just-in-time context, Claude and Clojure setups, ORC self-evolving agents and more.'),
     dict(date='2026-02-02', title='Building AI agents in practice with Clojure', who='Nubank Engineering (Marlon Silva)', url='https://building.nu.com/building-ai-agents-in-practice-with-clojure/', type='talk', k=['agents'], sum='Building agents in Clojure with LiteLLM, libpython-clj and small models. REPL-driven development for AI experiments.'),
     dict(date='2025-12', title='empire-2025', who='Robert C. Martin', url='https://github.com/unclebob/empire-2025', type='tool', k=['agents'], sum='Case study: a full Clojure game built by role-based Claude agents across about 1,340 commits, with quality guardrails.'),
     dict(date='2026-04', title='swarm-forge', who='Robert C. Martin', url='https://github.com/unclebob/swarm-forge', type='tool', k=['agents'], sum='Multi-agent orchestration in tmux and git worktrees (specifier, coder, cleaner, architect, hardener, QA).'),
     dict(date='2026', title='What is swarm-forge?', who='zentor.ai', url='https://zentor.ai/blog/what-is-swarm-forge', type='article', k=['agents'], read=False, sum='Third-party explainer of the swarm-forge workflow.'),
     dict(date='2026-02', title='crap4clj', who='Robert C. Martin', url='https://github.com/unclebob/crap4clj', type='tool', k=['agents'], read=False, sum='A Claude Code skill that computes the CRAP metric for Clojure as an agent guardrail.'),
     dict(date='2026-05', title='“Been coding in lots of languages with agentic coding…”', who='Hacker News', url='https://news.ycombinator.com/item?id=48062091', type='thread', k=['agents'], sum='Practitioners compare languages. Clojure with a REPL is rated least problematic, with paren complaints.'),
     dict(date='2026-03-04', title='#_ as a semantic block-closing marker for LLM-friendly Clojure', who='ClojureVerse', url='https://clojureverse.org/t/as-a-semantic-block-closing-marker-for-llm-friendly-clojure/14851', type='thread', k=['agents'], sum='Paren miscounting described from practice, with a proposed #_defn convention.'),
     dict(date='2025', title='Calva Backseat Driver', who='Peter Strömberg, BetterThanTomorrow', url='https://github.com/BetterThanTomorrow/calva-backseat-driver', type='tool', k=['agents'], sum='REPL eval, structural editing and a bracket balancer for Copilot, Cursor or any MCP client.'),
     dict(date='2026-05-05', title='re-frame-pair', who='Day8', url='https://github.com/day8/re-frame-pair', type='tool', k=['agents', 'frontend'], sum='Claude Code skill to inspect app-db, dispatch events and hot-swap handlers in a running re-frame app.'),
     dict(date='2025', title='ECA: Editor Code Assistant', who='Eric Dallo', url='https://eca.dev/', type='tool', k=['agents'], read=False, sum='Editor-agnostic AI pair-programming server written in Clojure and modelled on LSP.'),
     dict(date='2026-05-14', title='Expert Clojure Workflows for AI Agents: Four Skills from Production Experience', who='humorless', url='https://humorless.github.io/posts-output/agent-skill', type='article', k=['agents'], sum='clj-debug, clj-discover, clj-replace and clj-refactor skills, aimed at agent habits that fight Clojure.'),
     dict(date='2026-01', title='clojure-system-prompt', who='Ivan Willig', url='https://github.com/iwillig/clojure-system-prompt', type='tool', k=['agents'], read=False, sum='Shortcut’s REPL-first system prompt for Clojure agents, open-sourced.'),
     dict(date='2026-11-06', title='Self-Programmed Execution for Language-Model Agents', who='Luke J. O’Connor (NeurIPS 2026)', url='https://arxiv.org/abs/2605.06898', type='paper', k=['agents'], sum='Spell: a Lisp whose source is the model’s context window. Evidence for code-as-data as an agent substrate.'),
     dict(date='2024', title='MultiPL-E (v3.0, adds Clojure)', who='NuPRL, Northeastern', url='https://huggingface.co/datasets/nuprl/MultiPL-E', type='paper', k=['agents'], sum='Multi-language code benchmark. Clojure was added by Alex Miller. No Clojure pass@1 figures found.'),
     dict(date='2023-08', title='On the Impact of Language Selection for Training and Evaluating Programming Language Models', who='Katzy & Izadi', url='https://arxiv.org/abs/2308.13354', type='paper', k=['agents'], read=False, sum='Performance tracks training-data volume. The basis of the thin-training-data counterpoint.'),
     dict(date='2025-11-10', title='Writing MCP servers in Clojure with Ring and Malli', who='Latacora', url='https://www.latacora.com/blog/2025/11/10/mcp-sdk/', type='article', k=['agents'], read=False, sum='MCP servers that let agents query Datomic databases.'),
     dict(date='2025', title='My experience with Cursor and Clojure-MCP', who='Julien Bille', url='https://medium.com/@_jba/my-experience-with-cursor-and-clojure-mcp-6e323b90a6f3', type='article', k=['agents'], read=False, sum='Reports no more paren imbalance and a faster agent loop via the REPL.'),
     dict(date='2025', title='Clojure MCP demo', who='Bruce Hauman', url='https://www.youtube.com/watch?v=F61YWNapxJg', type='talk', k=['agents'], read=False, sum='Demo of clojure-mcp driving a live REPL.'),
     dict(date='2025', title='Vibe coding with Clojure-MCP', who='Gene Kim', url='https://www.youtube.com/watch?v=plMpFV5s8nY', type='talk', k=['agents'], read=False, sum='Live session building with clojure-mcp.'),
     dict(date='2025', title='Scicloj AI Meetup 8', who='Scicloj', url='https://www.youtube.com/watch?v=36hOSp83ozM', type='talk', k=['agents'], read=False, sum='Community meetup on AI tooling for Clojure.'),
     dict(date='2025-11', title='Agent-o-rama', who='Nathan Marz, Clojure/Conj 2025', url='https://www.youtube.com/watch?v=mNLWtM3Iya4', type='talk', k=['agents'], read=False, sum='Building and running LLM agents on Rama.'),
     dict(date='2025', title='ECA at London Clojurians', who='Eric Dallo', url='https://www.youtube.com/watch?v=YoYgihX4C7I', type='talk', k=['agents'], read=False, sum='Introduction to the Editor Code Assistant.'),
     dict(date='2026', title='Defold editor AGENTS.md', who='Defold', url='https://github.com/defold/defold/blob/ae2cf1d332be9089adfe80b727c16d3cf6a2d1b7/editor/AGENTS.md', type='tool', k=['agents'], read=False, sum='Requires agents to drive the editor UI through cljfx.plorer in a live REPL.'),
     # ecosystem / news
     dict(date='2026-06-23', title='Clojure Deref archive', who='clojure.org', url='https://clojure.org/news/news', type='newsletter', k=['ecosystem'], sum='Weekly ecosystem news. The source of every debut release tagged “new” on this site. Last issue 23 June 2026.'),
     dict(date='2025-12-23', title='Clojure Deref, Dec 23 2025', who='clojure.org', url='https://clojure.org/news/2025/12/23/deref', type='newsletter', k=['ecosystem', 'frontend', 'sync'], sum='Debuts include solid-cljs, distributed-scope and the UIx desktop starters.'),
     dict(date='2026-01-27', title='Clojure Deref, Jan 27 2026', who='clojure.org', url='https://clojure.org/news/2026/01/27/deref', type='newsletter', k=['ecosystem', 'frontend'], sum='charm.clj TUIs, the Datastar Pedestal adapter and the SWT desktop toolkit.'),
     dict(date='2026-03-10', title='Clojure Deref, Mar 10 2026', who='clojure.org', url='https://clojure.org/news/2026/03/10/deref', type='newsletter', k=['ecosystem', 'novel', 'runtimes', 'sync'], sum='hyper, cream, epupp, sqlatom and replikativ’s stratum.'),
     dict(date='2026-04-07', title='Clojure Deref, Apr 7 2026', who='clojure.org', url='https://clojure.org/news/2026/04/07/deref', type='newsletter', k=['ecosystem', 'frontend', 'agents'], sum='BareDOM, re-frame-query, cljfx/plorer and agent-queryable code graphs.'),
     dict(date='2026-05-19', title='Clojure Deref, May 19 2026', who='clojure.org', url='https://clojure.org/news/2026/05/19/deref', type='newsletter', k=['ecosystem', 'frontend', 'runtimes', 'sync'], sum='re-frame2, tyrell, stube, spindel, let-go and ghosttyfx.'),
     dict(date='2026-06-09', title='Clojure Deref, Jun 9 2026', who='clojure.org', url='https://clojure.org/news/2026/06/09/deref', type='newsletter', k=['ecosystem', 'runtimes'], sum='jolt (Clojure on Chez Scheme) and atomstream.'),
     dict(date='2026', title='Clojurists Together: Q2 2026 funding', who='Clojurists Together', url='https://www.clojuriststogether.org/news/q2-2026-funding-announcement/', type='article', k=['ecosystem', 'runtimes'], sum='Funded projects include gloat (Clojure to Go).'),
     dict(date='2026', title='Clojurists Together: Q3 2026 funding', who='Clojurists Together', url='https://www.clojuriststogether.org/news/q3-2026-funding-announcement/', type='article', k=['ecosystem', 'agents'], sum='Funded projects include the ECA editor assistant.'),
     dict(date='2026-09-30', title='Clojure/Conj 2026 schedule', who='Clojure/Conj', url='https://2026.clojure-conj.org/schedule', type='talk', k=['ecosystem'], sum='Conference programme, including the AI Tools & Practices Showcase.'),
     dict(date='2026', title='Dutch Clojure Days 2026', who='DCD', url='https://clojuredays.org/', type='talk', k=['ecosystem', 'sync', 'runtimes'], sum='Talks on SQLite with coffi and Squint-style async/await in ClojureScript.'),
     dict(date='2026', title='babashka-conf 2026', who='babashka', url='https://babashka.org/conf/', type='talk', k=['ecosystem', 'runtimes'], sum='Programme including charm.clj and terminal UIs.'),
     dict(date='2026', title='OSS updates May–June 2026', who='Michiel Borkent (borkdude)', url='https://blog.michielborkent.nl/oss-updates-may-jun-2026.html', type='article', k=['ecosystem', 'runtimes', 'frontend'], sum='ClojureScript lite mode, Squint async/await in CLJS, transit-cljs-lite.'),
     dict(date='2026-09', title='The future of the Clojure Deref', who='ClojureVerse', url='https://clojureverse.org/c/community-center/community-building/27', type='thread', k=['ecosystem'], sum='Community discussion after the Deref paused.'),
     dict(date='2026-09-15', title='awesome-clojure', who='razum2um', url='https://github.com/razum2um/awesome-clojure', type='dataset', k=['ecosystem'], sum='The most-starred curated Clojure list, audited in DSP-010.'),
     dict(date='2026-11-06', title='Replicant on Codeberg', who='Christian Johansen', url='https://codeberg.org/cjohansen/replicant', type='tool', k=['frontend'], sum='Replicant’s new home after it left GitHub in November 2026.'),
     dict(date='2026-11-10', title='GitHub GraphQL API', who='GitHub', url='https://docs.github.com/en/graphql', type='dataset', k=['ecosystem'], sum='Source of every metric on this site, fetched on the snapshot date.'),
    ]
    return S
