"""Case 004: Datastar, and Stardust, the database its team is building. Research filed 2026-11-11."""
import html
from content import _a, finding, caveat, signal, intercept, stat, table, HIGH, MOD, LOW

REF = 'SMAF-004'
B = '/projects/datastar/'
def conf_chip(c): return f'<span class="conf {c[0]}">{c[1]}</span>'
code = lambda src, cap=None: (f'<figure class="codefig"><figcaption>{cap}</figcaption>' if cap else '<figure class="codefig">') + f'<pre class="code"><code>{html.escape(src.strip())}</code></pre></figure>'
def media(items):
    """items: (kind, date, title, url, who, gist)"""
    return '<ul class="media">' + ''.join(
        f'<li><span class="kd">{k}<small>{dt}</small></span><div><a href="{u}" target="_blank" rel="noopener">{html.escape(t)}</a> <span class="dim">· {html.escape(w)}</span><p>{g}</p></div></li>'
        for k, dt, t, u, w, g in items) + '</ul>'

CORE = ['starfederation/datastar', 'starfederation/datastar-clojure', 'starfederation/datastar-go', 'starfederation/datastar-python', 'starfederation/datastar-typescript',
        'starfederation/datastar-rust', 'starfederation/datastar-php', 'starfederation/datastar-dotnet', 'starfederation/datastar-ruby', 'starfederation/datastar-java',
        'starfederation/datastar-htmx', 'fsmunoz/datastar-cl']
CLJ = ['andersmurphy/hyperlith', 'jacobobryant/biff', 'starfederation/datastar-clojure', 'brianium/datastar.wow', 'dynamic-alpha/hyper', 'whamtet/simpleui',
       'ObneyAI/grain', 'realgenekim/datastar-helpers', 'outskirtslabs/datastar-expressions', 'mbolli/clj-chess', 'andersmurphy/sqlite4clj', 'onionpancakes/chassis']
OTHER = ['tokio-rs/topcoat', 'zangster300/northstar', 'romshark/datapages', 'CoreyCole/datastarui', 'stariodev/stario', 'putyourlightson/laravel-datastar',
         'cablehead/http-nu', 'StreamUI/hyperstar', 'stukennedy/irgo', 'delaneyj/realworld-datastar', 'dataSPA/dataSPA', 'addrummond/datastargostrictcsp']
AGENT = ['cbeauhilton/datastar-skills', 'danmestas/wardrobe', 'maragudk/skills', 'alvarolm/datastar-resources', 'romshark/datapages']
VS = ['starfederation/datastar', 'bigskysoftware/htmx', 'alpinejs/alpine', 'phoenixframework/phoenix_live_view', 'hyperfiddle/electric', 'bigskysoftware/idiomorph', 'stackblitz/alien-signals']
STARDUST = ['bencroker/stardust-todos', 'cablehead/stardust-todomvc', 'starfederation/tron']

HTML_EX = '''
<script type="module"
  src="https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.5/bundles/datastar.js"></script>

<div data-signals="{delay: 400}">
  <input type="number" data-bind:delay>
  <button data-on:click="@get('/hello-world')">Start</button>
  <div id="message">Hello, world!</div>
</div>'''
CLJ_EX = '''
;; deps.edn: dev.data-star.clojure/sdk + dev.data-star.clojure/http-kit {:mvn/version "1.0.0-RC13"}
(ns hello
  (:require [charred.api :as json]
            [org.httpkit.server :as hk]
            [starfederation.datastar.clojure.api :as d*]
            [starfederation.datastar.clojure.adapter.http-kit :refer [->sse-response on-open]]))

(def message "Hello, world!")

(defn hello-world [request]
  (let [delay (-> request d*/get-signals json/read-json (get "delay") int)]
    (->sse-response request
      {on-open
       (fn [sse]
         (d*/with-open-sse sse
           (dotimes [i (count message)]
             (d*/patch-elements! sse (str "<div id=\\"message\\">" (subs message 0 (inc i)) "</div>"))
             (Thread/sleep delay))))})))'''
CQRS_EX = '''
;; The CQRS shape the Tao recommends, on top of ownpurse's single write path (a sketch, untested):
(defonce conns (atom #{}))                       ; open SSE generators, one per tab

(defn stream [req]                               ; GET /stream: the one long-lived read
  (->sse-response req
    {on-open  (fn [sse] (swap! conns conj sse) (d*/patch-elements! sse (render-page req)))
     on-close (fn [sse _] (swap! conns disj sse))}))

(defn after-commit! [_tx]                        ; call from the tx hook
  (doseq [sse @conns] (d*/patch-elements! sse (render-page-for sse))))

(defn add-entry [req]                            ; POST /entries: a short write, then 204
  (submit! (entry-from (d*/get-signals req)))
  {:status 204})'''

def pages(memo, R, d):
    a = lambda n, l=None: _a(R, n, l)
    r = lambda n: R[n.lower()]
    ds, dsc, hl, el = r('starfederation/datastar'), r('starfederation/datastar-clojure'), r('andersmurphy/hyperlith'), r('hyperfiddle/electric')
    M = lambda title, subj, eb: memo(title, subj, 'Open', eyebrow=f'Case 004 // {eb}', ref=REF)
    out = []

    brief = f'''{M('Datastar, and the database behind it', 'What is Datastar, who builds it, how are people using it, and what is the database its team is building?', 'brief')}
<div class="bluf"><p><strong>Datastar is a 12.5 KiB hypermedia framework where the server owns the state and streams HTML down an SSE connection.</strong> It hit 1.0 in April 2026 (now {ds['rel']}). Its strongest following is in Clojure: David Nolen rebuilt a production accounting app on it, Biff 2 made it the default, and Anders Murphy's demos run a billion checkboxes on a small VPS. The team's real goal is <strong>Stardust</strong>, a closed-source, embedded, append-only temporal database in paid alpha that pushes live query results for Datastar to stream. For a Clojure backend, Datastar is the lowest-risk way to get a live UI with no ClojureScript. Stardust is one to watch, not to adopt.</p></div>
<div class="strip" aria-label="Datastar at a glance">
  <div><div class="v">{ds['s']:,}</div><div class="l">GitHub stars</div></div>
  <div><div class="v">{ds['rel']}</div><div class="l">released 2026-11-09</div></div>
  <div><div class="v">12.5 KiB</div><div class="l">brotli, measured</div></div>
  <div><div class="v">15</div><div class="l">official SDK languages</div></div>
  <div><div class="v">{ds['c12']}</div><div class="l">commits in 12 months</div></div>
</div>
<div class="prose">
<h2>Key judgments</h2>
<ol class="kj">
<li><div><h3>The server is the source of truth, and the page is a function of it</h3><p>Two SSE events do almost everything: <code>datastar-patch-elements</code> morphs HTML into the page by id, and <code>datastar-patch-signals</code> updates small client state. The recommended shape is CQRS: one long-lived read stream re-renders on every write, and writes are short POSTs that return 204. {conf_chip(HIGH)} <a class="more" href="{B}how-it-works/">how it works →</a></p></div></li>
<li><div><h3>Clojure is where Datastar has its most serious users</h3><p>Instabooks (Nolen and Murphy) is "a full rewrite of a production application – with no regrets". Biff 2.0 ships it as the default. A Clojure/Conj 2025 talk compares a local-first ClojureScript build with the Datastar rewrite. {conf_chip(HIGH)} <a class="more" href="/blog/datastar-clojure-adopters/">dispatch →</a></p></div></li>
<li><div><h3>The database is Stardust: embedded, temporal, closed, alpha</h3><p>Delaney Gillilan's "data engine" stores facts with transaction time, answers Datalog-style queries at any past moment, and pushes live results. It is sold by BitFlip LLC from $99 and carries no format-stability promise. The site says "Stardust inspired us to create Datastar." {conf_chip(HIGH)} <a class="more" href="{B}stardust/">Stardust →</a></p></div></li>
<li><div><h3>Rough edges are real: Pro, churn, global signals</h3><p>Paid Pro plugins caused a public row in 2025. Breaking changes kept coming after the "final" beta, so tutorials and model training data use dead syntax. Signals are page-global, and the Clojure SDK is still a release candidate. {conf_chip(HIGH)} <a class="more" href="{B}critiques/">critiques →</a></p></div></li>
<li><div><h3>Agents need the docs in context</h3><p>Gillilan says models are "overfitted" to SPA patterns. Reports run both ways, from a Claude Code multiplayer game to Codex failing a simple task. The fix that works: load the single-file <code>docs.md</code> into context and keep the UI as server-rendered hiccup the agent can check with curl. {conf_chip(MOD)} <a class="more" href="/blog/datastar-and-agents/">dispatch →</a></p></div></li>
</ol>
{finding('For ownpurse', f'<p>Datastar\'s recommended architecture is the change feed case 002 already proposed: a hook on the one write path re-renders and pushes to every open stream. Spike it first. It needs no ClojureScript and no license, and it keeps the database (XTDB) unchanged. <a href="{B}for-ownpurse/">The fit, in detail →</a></p>')}
<h2>In this file</h2>
<ul><li><a href="{B}how-it-works/">How it works</a>: the mental model, a Clojure example, SDKs, releases, size and Pro.</li>
<li><a href="{B}stardust/">Stardust</a>: the team's database, what is known and what isn't.</li>
<li><a href="{B}field-reports/">Field reports</a>: who uses it for what, plus talks, videos and threads.</li>
<li><a href="{B}critiques/">Critiques</a>: the Pro row, breaking changes, limits, agents.</li>
<li><a href="{B}for-ownpurse/">For ownpurse</a>: Datastar against Electric on a Clojure + XTDB backend.</li></ul>
</div>
{table(VS, 'Datastar and its neighbours', 'full')}'''
    out.append((B, 'Case 004: Datastar and Stardust', 'Deep dive on Datastar, the 12.5 KiB SSE hypermedia framework: how it works, who uses it (Clojure especially), its critiques, and Stardust, the temporal database its team is building.', brief))

    how = f'''{M('How Datastar works', 'The mental model, a Clojure example, the SDKs, the release history, size and the Pro tier', 'how it works')}
<div class="bluf"><p>Put state on the server. Render HTML there. Hold one SSE connection open per tab and push new HTML into the page, where Datastar morphs it in by id. Use signals only for small, local, interactive state. The browser library adds <code>data-*</code> attributes and two event types; everything else is your backend.</p></div>
<div class="prose">
<h2>The model</h2>
<ul>
<li><strong>Attributes:</strong> <code>data-on:click</code>, <code>data-bind:x</code>, <code>data-text</code>, <code>data-show</code>, <code>data-signals</code>, <code>data-attr:*</code>, <code>data-class</code>, <code>data-indicator</code>, <code>data-init</code>, <code>data-effect</code>. Values are JavaScript expressions in which <code>$name</code> is a signal and <code>@get('/x')</code> is an action (<a href="https://data-star.dev/reference/attributes">reference</a>).</li>
<li><strong>Responses:</strong> plain <code>text/html</code> morphs top-level elements by id. <code>text/event-stream</code> carries any number of <code>datastar-patch-elements</code> and <code>datastar-patch-signals</code> events. JSON patches signals, and JavaScript runs (<a href="https://data-star.dev/reference/sse_events">SSE events</a>). "No SDK needed… (it's two events, people!)"</li>
<li><strong>Morphing:</strong> you can send "large chunks of the DOM tree (all the way up to the <code>html</code> tag)" and only the changed parts update. Inputs keep their focus and value.</li>
<li><strong>Signals:</strong> an in-tree reactive engine modelled on alien-signals, with no dependencies.</li>
</ul>
<h2>The Tao of Datastar</h2>
<p>The <a href="https://data-star.dev/guide/the_tao_of_datastar">Tao</a> is the opinionated part, and the part people who switch talk about most:</p>
<ul><li>"Most state should live in the backend." Use signals sparingly: "only… for user interactions… and for sending new state to the backend".</li>
<li>"In Morph We Trust": send big fragments, even the whole page ("fat morph"), and let the morph sort it out.</li>
<li>CQRS: one long-lived read stream, short write requests.</li>
<li>Compression: "ratios of 200:1 are not uncommon" with Brotli over a stream.</li>
<li>No optimistic updates. The page says optimistic UI "deceives the user". Use loading indicators instead.</li>
<li>Use <code>&lt;a&gt;</code> for navigation and leave browser history alone.</li></ul>
{code(HTML_EX, 'the page')}
{code(CLJ_EX, 'a Clojure handler, official SDK (adapted from the SDK\'s hello-httpkit example)')}
<p>Jacob O'Bryant describes Biff 2's version of the model: the page opens one SSE connection, any database commit re-renders the whole page and pushes it, POST handlers return 204, and per-tab state lives on the server. The cost: "more moving parts on the backend", and "your page rendering function needs to be fast" (<a href="https://biffweb.com/p/understanding-datastar/">Understanding Datastar</a>, Oct 2026).</p>

<h2>SDKs, and the Clojure one</h2>
<p>Official SDKs cover 15 languages: Clojure, C#, Go, Haskell, Java, Kotlin, Lean 4, PHP, Python, Ruby, Rust, Scala (ZIO HTTP), TypeScript, Unison and Zig (<a href="https://data-star.dev/reference/sdks">list</a>). The Clojure SDK is {a('starfederation/datastar-clojure')}: Clojars group <code>dev.data-star.clojure</code>, artifacts <code>sdk</code>, <code>http-kit</code>, <code>ring</code>, <code>brotli</code> and malli schemas, maintained by Jeremy Schoffen. <strong>It is still at {dsc['rel']}</strong> while the framework is at {ds['rel']}. RC12 and RC13 (Oct–Nov 2026) fixed output-stream leaks in the ring adapter when clients disconnect.</p>
{caveat(f'<p>Biff 2\'s <code>com.biffweb/datastar</code> does not use the official SDK. It is its own ring + brotli4j code in the style of {a("andersmurphy/hyperlith", "hyperlith")}, and its README warns: "I haven\'t personally used it at scale." In Clojure you are choosing among three thin layers, all young.</p>')}

<h2>Releases</h2>
<table class="cmp"><thead><tr><th>Version</th><th>Date</th><th>What changed</th></tr></thead><tbody>
<tr><td>repo created</td><td>2023-08</td><td>as <code>delaneyj/datastar</code>; moved to the starfederation org in Nov 2024</td></tr>
<tr><td>1.0.0-beta.1</td><td>2025-01-02</td><td>"made all final breaking changes to the API" (they weren't)</td></tr>
<tr><td>1.0.0-RC.1</td><td>2025-07-10</td><td><strong>Datastar Pro introduced</strong>; SSE events and every SDK changed</td></tr>
<tr><td>1.0.0-RC.6</td><td>2025-10-21</td><td>Breaking: <code>data-on-click</code> → <code>data-on:click</code>, <code>data-on-load</code> → <code>data-init</code></td></tr>
<tr><td>1.0.0</td><td>2026-04-16</td><td>"We are done. Done like dinner."</td></tr>
<tr><td>1.0.4</td><td>2026-09-21</td><td>Rocket (web components) moved from Pro to free</td></tr>
<tr><td>{ds['rel']}</td><td>2026-11-09</td><td>SSE retry and tab-visibility fixes, morph fixes</td></tr>
</tbody></table>
{stat('12,822 B', 'v1.0.5 measured on 2026-11-11: 35,673 B minified, 14,119 B gzip, 12,822 B brotli. The homepage\'s "12.52 KiB" is the brotli figure.', 'Bundle size')}

<h2>License and Pro</h2>
<p>The core is MIT. <a href="https://data-star.dev/pro">Datastar Pro</a> is a one-time lifetime license: $349 solo, $1,299 for organisations up to 25 people, enterprise by quote (it launched at $299). It adds attributes (<code>data-persist</code>, <code>data-query-string</code>, <code>data-replace-url</code>, <code>data-scroll-into-view</code>, <code>data-animate</code> and others), <code>@clipboard</code>, <code>@fit</code> and <code>@intl</code>, a bundler, the Inspector debugger and Stellar CSS. Pro code can't go in a public repo. The project is run by Star Federation, which describes itself as a US 501(c)(3) nonprofit ("No VCs"). That status is self-reported; I did not check IRS records.</p>
<h2>Who builds it</h2>
<p>Delaney Gillilan created it. Ben Croker (PutYourLightsOn) is the top committer and leads the docs. A third core member, Johnathan Stevers, is credited with the signals and morphing work. Anders Murphy is the biggest community contributor. The About page says "Every line of code is written by hand."</p>
</div>
{table(CORE, 'Core and official SDKs', 'full')}'''
    out.append((B + 'how-it-works/', 'How Datastar works', 'Datastar\'s model (server state, SSE, morphing, signals, the Tao, CQRS), a Clojure SDK example, the 15 SDKs, release history, bundle size and Datastar Pro.', how))

    sd = f'''{M('Stardust: the database the Datastar team is building', 'What Stardust is, how it works, how it relates to Datastar, and what is not known', 'stardust')}
<div class="bluf"><p><strong>Stardust is an embedded, append-only, temporal "data engine" by Delaney Gillilan, in paid alpha, closed source.</strong> It stores facts about entities with the transaction that recorded them, answers Datalog-style queries "as of" any time, and pushes live query results, which an app then streams to the browser through Datastar. "We fixed the web. Now it is time to fix data… Stardust inspired us to create Datastar… Now our focus is Stardust" (<a href="https://www.stardustdb.com/">stardustdb.com</a>).</p></div>
<div class="prose">
<h2>The facts</h2>
<table class="cmp"><tbody>
<tr><th>What</th><td>"Append-only temporal data engine… Keep every change. Question any moment." It runs in your process as a library (C ABI) and writes local database files.</td></tr>
<tr><th>Who</th><td>Delaney Gillilan builds it. It is sold by <strong>BitFlip LLC</strong>, a Nevada company, not by the Star Federation nonprofit (<a href="https://www.stardustdb.com/eula">EULA</a>, 2026-10-12). Ben Croker builds demos.</td></tr>
<tr><th>Bindings</th><td>Go, Clojure, Python, Rust, Odin. The core is reportedly written in Odin and ships as a single binary of a few megabytes (from the podcast's auto-captions, so treat as reported).</td></tr>
<tr><th>License</th><td>Proprietary perpetual licenses with a year of updates: $99 non-commercial, $199 solo, $1,499 team (up to 10 developers), enterprise. No free trial. The EULA forbids reverse engineering. There is no public repo.</td></tr>
<tr><th>Status</th><td>Alpha: "no stability or file-format compatibility guarantees… We have not set a date for general availability." First shown in public on the official podcast, 2026-09-21. The domain dates from May 2025.</td></tr>
</tbody></table>
<h2>The design</h2>
<ul>
<li><strong>Data model:</strong> entities, transactions and facts (a field value tied to an entity and a transaction). The ontology is open: entities gain fields without declaring them first, and schemas validate and project on demand, so "data can change shape without migrations".</li>
<li><strong>Time:</strong> every accepted transaction stays queryable, and temporal queries return the state at a given instant. A <code>history</code> plugin enforces retention, and <code>blackholes</code> removes chosen fields from history and backups with an audit trail.</li>
<li><strong>Queries:</strong> Datalog-style, written in its own "DUST" notation, e.g. <code>find [?name] where [[?e name ?name]]</code>. Queries, mutations and schemas are stored in the database as data and called by id. An adaptive planner learns join orders.</li>
<li><strong>Live data:</strong> subscriptions return a result and then replace it on every change. <code>reactors</code> derive mutations atomically, and <code>events</code> provides pub/sub. On the podcast the team calls this "a perfect match" for Datastar's long-lived SSE streams.</li>
<li><strong>Also built in:</strong> a content-addressed object store, typed SDK generation, generated agent skills, FUSE filesystem access, and backups to several local or S3 targets with per-target encryption.</li>
<li><strong>Not documented:</strong> the storage engine underneath, and any multi-node replication.</li>
</ul>
<h2>Named influences</h2>
<p>Datomic (immutable facts and time), Asami (open graph), Lisp and Clojure (behaviour as data), ECS game engines like Flecs, SQLite and DuckDB (embedded), and TigerBeetle's TIGER_STYLE (<a href="https://www.stardustdb.com/theory/inspirations">inspirations</a>). Casey Link's one-line summary: "SQLite + Datomic + Redis + Elasticsearch + NATS + Object Storage all in one small binary" (<a href="https://casey.link/blog/from-the-outskirts-q3-2026/">Oct 2026</a>).</p>
{finding('Why a Clojure developer should care', '<p>Stardust is Datomic and XTDB\'s ideas (immutable facts, time travel, Datalog), embedded like SQLite, with the one thing XTDB lacks: <strong>live queries that push changes</strong>. That is the gap that blocks every sync engine in front of XTDB (<a href="/blog/xtdb-has-no-change-feed/">dispatch</a>). The cost is that it is closed, alpha and owned by a small company.</p>')}
{caveat('<p>Everything here comes from the vendor\'s site, its EULA, the official podcast and a handful of demo repos. Nobody independent has published a review, benchmark or production report, and Hacker News has no thread on it. Treat it as an announcement.</p>')}
<h2>Where to see it</h2>
{media([
 ('podcast', '2026-09-21', 'Rocket breaks free; Stardust underway', 'https://www.youtube.com/watch?v=U87Vorhd0EA', 'official Datastar podcast', 'The first public walkthrough of Stardust, from the private alpha through the waitlist, live queries and the move to FUSE.'),
 ('docs', '2026-11', 'Stardust overview and theory', 'https://www.stardustdb.com/theory/overview', 'stardustdb.com', 'Entities, facts, transactions, reification, plugins and backups.'),
 ('blog', '2026-10-20', 'From the Outskirts: Q3 2026', 'https://casey.link/blog/from-the-outskirts-q3-2026/', 'Casey Link', 'A Clojure developer\'s note that Stardust is in public preview, and his one-line summary of it.'),
 ('repo', '2026-07→11', 'bencroker/stardust-todos', 'https://github.com/bencroker/stardust-todos', 'Ben Croker', 'Laravel + Datastar + Stardust todo app: as-of queries, live updates over SSE.'),
])}
</div>
{table(STARDUST, 'Public repos around Stardust (there is no Stardust repo)', 'full')}'''
    out.append((B + 'stardust/', 'Stardust: the Datastar team\'s database', 'Stardust (stardustdb.com), the embedded append-only temporal data engine from Datastar\'s creator: data model, live queries, license, status, and why it matters next to XTDB and Datomic.', sd))

    fr = f'''{M('Datastar in the field', 'Who is building what with Datastar, and the talks, videos and threads worth your time', 'field reports')}
<div class="bluf"><p>The people who move to Datastar describe the same win: update logic lives in one place, on the server, and real-time comes free. Most come from htmx plus Alpine, some from React, Svelte or re-frame. The biggest production story is Clojure: Instabooks. The pains repeat too: global signals, the attribute DSL, the Pro tier, and a server round trip per interaction.</p></div>
<div class="prose">
<h2>Production and migration stories</h2>
{media([
 ('clojure', '2026', 'Datastar: it\'s pretty good, with David Nolen', 'https://data-star.dev/essays/datastar_its_pretty_good', 'David Nolen, Anders Murphy', 'Instabooks, "a faster, more polished version of QuickBooks Online", rebuilt on Datastar: "A full rewrite of a production application – with no regrets." <a href="https://youtu.be/2ECucq-mTGg">Video</a>.'),
 ('talk', '2025-11-14', 'From Tomorrow Back to Yesterday: A Tale of Two Web Architectures', 'https://www.youtube.com/watch?v=8W6Lr1hRgXo', 'Yang, Clojure/Conj 2025', 'Compares a local-first ClojureScript build ("Web After Tomorrow") with a Datastar rewrite, with production metrics. I haven\'t watched it, so the numbers aren\'t checked.'),
 ('clojure', '2026-10-01', 'Understanding Datastar', 'https://biffweb.com/p/understanding-datastar/', 'Jacob O\'Bryant, Biff', 'Biff 2\'s model: re-render on every commit, 204 POSTs, per-tab state. "I\'m not sure I see any cases where I would use htmx again."'),
 ('clojure', '2025-04-07', 'Realtime collaborative web apps without ClojureScript', 'https://andersmurphy.com/2025/04/07/clojure-realtime-collaborative-web-apps-without-clojurescript.html', 'Anders Murphy', 'hyperlith walkthrough, and the post that put Clojure + Datastar on HN.'),
 ('clojure', '2026', 'Datastar observations', 'https://dev.to/hlship/datastar-observations-3icg', 'Howard Lewis Ship', 'Moved a side project from Svelte: "no possibility of de-synchronization" between client and server.'),
 ('clojure', '2026-11-10', 'Rendering in batches with Glimmer and Datastar', 'https://yogthos.net/posts/2026-11-10-glimmer-datastar.html', 'Dmitri Sotnikov', 'Reagent-style ratoms on the server that push patches over SSE, with batching to one render per tick.'),
 ('python', '2025-10-09', 'Why I switched from htmx to Datastar', 'https://everydaysuperpowers.dev/articles/why-i-switched-from-htmx-to-datastar/', 'Chris May', 'htmx + Alpine "fell out of step"; with Datastar "the server decides what should change". The most-discussed Datastar post (HN 315 points, 380 comments).'),
 ('typescript', '2025-11-03', 'Datastar first impressions, coming from React', 'https://threadgold.nz/writing/datastar-coming-from-react', 'threadgold.nz', 'Liked no build step and morphing that keeps input state. Hurt: no LSP inside attributes, attribute order matters, signals are global.'),
 ('go', '2025-01-15', 'Datastar: web framework for the future?', 'https://chrismalek.me/posts/data-star-first-impressions/', 'Chris Malek', 'htmx markup "became a mess" on non-trivial parts; Datastar is "HTMX and AlpineJS under a single library".'),
 ('ruby', '2026-11-04', 'A look at Datastar', 'https://noteflakes.com/articles/2026-11-04-datastar', 'noteflakes', 'Likes UI = f(state) on any backend. Cons: page-global signals, all signals sent on every action, lots of re-rendered HTML.'),
 ('rust', '2026-01-11', 'Joyus: I tried Datastar', 'https://ajmoon.com/posts/joyus-i-tried-datastar', 'Alex Moon', 'Datastar is "built for the Light DOM… built on global state". He forked it to support web components.'),
 ('elixir', '2026-03-11', 'PhoenixDatastar: a LiveView-like experience over SSE', 'https://elixirforum.com/t/phoenixdatastar-a-liveview-like-experience-for-phoenix-using-datastars-sse-signals-architecture/74600', 'Elixir Forum', 'LiveView-style callbacks over Datastar. The first reply: it\'s so close to LiveView, "maybe I should just use LiveView".'),
])}
{caveat('<p>The project\'s <a href="https://data-star.dev/gratitude">Gratitude page</a> has the biggest claims: one user cut 1.1M lines across 20 internal tools, another moved from re-frame. These are testimonials the project picked, and I haven\'t verified them.</p>')}
<h2>The demos</h2>
<p>Anders Murphy, a community member writing in Clojure, built the demos everyone cites: <a href="https://checkboxes.andersmurphy.com/">One Billion Checkboxes</a> (SQLite, virtual scroll), a multiplayer <a href="https://example.andersmurphy.com/">Game of Life</a> that pushes 2,500 divs every 200 ms over compressed SSE, and One Billion Cells. Tuning the brotli window took his compression ratio from about 30:1 to 150–250:1 and cut CPU 4–8x (<a href="https://andersmurphy.com/2025/04/15/why-you-should-use-brotli-sse.html">post</a>). He is candid that "SQLITE and JVM virtual threads are doing some heavy lifting… it\'s not really about Datastar". The hosting figures vary between sources: a "$5 VPS" in some, a 4-core ~$15 Hetzner box in his own post.</p>
<h2>Talks and videos</h2>
{media([
 ('talk', '2026-07-29', 'Put State in the Right Place', 'https://www.youtube.com/watch?v=W7Ki3aXgmZU', 'Delaney Gillilan, Software Should Work 2026', 'The most-watched Datastar talk: web standards and server-held state over dependency-heavy SPAs.'),
 ('talk', '2026-10-15', 'Datastar and Clojure', 'https://www.youtube.com/watch?v=sR0yrp2wDUU', 'Arne Brasseur, Clojure Café', 'SSE, morphing and connection-level compression; "multiplayer out of the box"; state in the DB. <a href="http://arnebrasseur.net/talks/2026-datastar/">Slides</a>.'),
 ('video', '2026', 'Serving webapps from your REPL', 'https://www.youtube.com/watch?v=k98QI-EOHJA', 'Timothy Pratley', 'A realtime chart pushed from the Clojure REPL with Clay and Datastar.'),
 ('podcast', '2026', 'Datastar: modern web dev, simplified (Talk Python #537)', 'https://talkpython.fm/episodes/show/537/datastar-modern-web-dev-simplified', 'Gillilan, Croker, Chris May', 'htmx\'s "last 10%" problem, and why LLMs struggle with Datastar.'),
 ('podcast', '2025-09-08', 'Why we\'re building the front end wrong (JavaScript Jabber 688)', 'https://www.youtube.com/watch?v=FtAuSAOMNtM', 'Delaney Gillilan', 'Game-dev and military background; the limits of SPAs and of htmx.'),
 ('podcast', '2026', 'Fast functional reactive programming with Datastar\'s creator', 'https://www.youtube.com/watch?v=CpLEVZ3r5mM', 'Software Unscripted, Richard Feldman', 'FRP and performance, with Elm\'s Richard Feldman.'),
 ('video', '2026-04', 'Datastar 1.0: it\'s finally done', 'https://youtu.be/T6uwri94ylk', 'Datastar channel', 'The v1 launch stream.'),
 ('video', 'ongoing', 'The Datastar YouTube channel', 'https://www.youtube.com/@data-star', 'core team', 'More than 30 episodes: CSP mode, Rocket, event sourcing, Idiomorph, NATS, CQRS.'),
])}
<h2>Threads</h2>
{media([
 ('forum', '2025-10-10', 'I switched from htmx to Datastar (HN, 315 points)', 'https://news.ycombinator.com/item?id=45536000', 'Hacker News', 'Dominated by the Pro tier ("the precedent this establishes isn\'t great"). Also: htmx is HTML-driven, Datastar is server-driven.'),
 ('forum', '2025-10-10', 'Datastar: lightweight hypermedia framework (HN, 306 points)', 'https://news.ycombinator.com/item?id=45536618', 'Hacker News', 'Simon Willison on the "chilling effect" of paid plugins; complaints about the attribute DSL; "a paradigm shift for the better".'),
 ('forum', '2025-04-11', 'Datastar: web framework for the future? (HN, 255 points)', 'https://news.ycombinator.com/item?id=43655914', 'Hacker News', 'Is every click a server round trip? CSP needs a hole (since fixed by CSP mode). Includes an AMA by the author.'),
 ('forum', '2026-09-10', 'Show HN: Biff 2.0', 'https://news.ycombinator.com/item?id=49647635', 'Hacker News', 'SQLite plus Datastar as Biff\'s defaults.'),
])}
</div>
{table(CLJ, 'Clojure on Datastar', 'full')}
{table(OTHER, 'Other languages, apps and forks', 'full')}'''
    out.append((B + 'field-reports/', 'Datastar in the field', 'How people use Datastar in production and side projects (Instabooks, Biff 2, hyperlith, migrations from htmx, React, Svelte and re-frame), plus the talks, videos and HN threads.', fr))

    cr = f'''{M('Datastar critiques', 'The Pro row, breaking changes, limits, and how agents cope', 'critiques')}
<div class="bluf"><p>None of these is a reason to avoid Datastar for a server-owned app. Several are reasons to pin versions, read the current docs instead of tutorials, and keep each page's signals small.</p></div>
<div class="prose">
<h2>1. The Pro tier</h2>
<p>At RC.1 (July 2025), plugins that had been free in the betas moved into paid Pro. A blogger called it a "rugpull" (<a href="https://drshapeless.com/blog/posts/htmx,-datastar,-greedy-developer.html">drshapeless</a>). On HN, Simon Willison warned of a "chilling effect" on contributions, and the author's reply, "Then fork it, it's MIT", drew a warning from the moderator. The team answered with <a href="https://data-star.dev/essays/greedy_developer">Greedy Developer?</a>: the core stays MIT, Pro plugins are new implementations, and the free version can do the same things with standard APIs. A friendly fork, {a('dataSPA/dataSPA')}, restores the removed plugins. Rocket moved back to free in 1.0.4.</p>
<h2>2. Breaking changes, and stale training data</h2>
<p>beta.1 promised "all final breaking changes". RC.1 then changed the SSE events and every SDK, and RC.6 changed the attribute syntax (<code>data-on-click</code> → <code>data-on:click</code>). Tutorials, blog posts and models trained before late 2025 use the dead syntax. The team says "No Datastar v2 is planned or necessary."</p>
<h2>3. Global signals and the attribute DSL</h2>
<p>Signals are page-global and can't be scoped, so two instances of one component share state (threadgold, noteflakes, Alex Moon). There is no LSP or type checking inside attribute expressions, attribute order matters, and modifiers like <code>data-on:input__debounce.200ms</code> divide people.</p>
<h2>4. Network and security</h2>
<ul><li>Every interaction is a server round trip, and there is no offline mode. That is a problem on high-latency links, and it rules out a local-first app. A recent official video argues offline is possible, but nothing documents it.</li>
<li>Expressions compile with <code>Function()</code>, so the default mode needs CSP <code>unsafe-eval</code>. A nonce-based CSP mode now exists, but the docs say it "does not make Datastar expressions safe to use with untrusted content". Signals are user-editable, so validate on the server (<a href="https://data-star.dev/reference/security">security</a>).</li>
<li>SSE reconnect and tab-visibility bugs were still being fixed in 1.0.5. Gene Kim's {a('realgenekim/datastar-helpers')} documents silent failures in production Clojure: frozen streams, 503s under load, scroll jumps after a fat morph.</li></ul>
<h2>5. Agents</h2>
<p>The team's position is that current models are "overfitted to React and SPA patterns", and Gillilan's advice is "if you want to vibe code something quickly, use React" (<a href="https://talkpython.fm/episodes/show/537/datastar-modern-web-dev-simplified">Talk Python #537</a>). Field reports go both ways (<a href="/blog/datastar-and-agents/">dispatch</a>).</p>
</div>'''
    out.append((B + 'critiques/', 'Datastar critiques', 'The Datastar Pro controversy, breaking changes before 1.0, global signals, CSP and SSE caveats, and how coding agents cope with Datastar.', cr))

    op = f'''{M('Datastar for ownpurse', 'Datastar against Electric for a Clojure + XTDB app with a single write path', 'for ownpurse')}
<div class="bluf"><p><strong>Spike Datastar first.</strong> Its recommended architecture (one SSE stream per tab, re-render on commit, writes as short POSTs) is the change feed <a href="/approaches/frontend-sync/ownpurse/">case 002</a> proposed, with no ClojureScript, no license and no change to XTDB. Keep Electric as the second spike, for screens that need rich client-side interaction. Watch Stardust, but don't move ledger data onto a closed alpha.</p></div>
<div class="prose">
<h2>Side by side</h2>
<table class="cmp"><thead><tr><th></th><th>Datastar</th><th>Electric v3</th></tr></thead><tbody>
<tr><td>Where the UI runs</td><td>Server-rendered hiccup; 12.5 KiB of JS in the browser</td><td>One Clojure program the compiler splits into client and server</td></tr>
<tr><td>ClojureScript</td><td>None</td><td>Required</td></tr>
<tr><td>Sync model</td><td>Re-render and morph on each write; you choose what to push</td><td>Fine-grained reactive dataflow across the network</td></tr>
<tr><td>License</td><td>MIT core; optional Pro from $349, one-time</td><td>Free for bootstrappers and non-commercial use; otherwise commercial</td></tr>
<tr><td>Maturity</td><td>1.0 since April 2026; {ds['c12']} commits in 12 months; the Clojure SDK is still an RC</td><td>{el['rel']}; last commit {el['lc']}</td></tr>
<tr><td>Offline / local-first</td><td>No</td><td>No</td></tr>
<tr><td>How an agent checks its work</td><td>curl the endpoint, or call the render fn at the REPL; it's just HTML</td><td>Needs a browser or Electric's own test tooling</td></tr>
<tr><td>Production in Clojure</td><td>Instabooks, Biff 2, hyperlith demos</td><td>Hyperfiddle and others (see <a href="/blog/electric-in-2026/">dispatch</a>)</td></tr>
</tbody></table>
{code(CQRS_EX, 'the shape, on ownpurse\'s write path')}
<h2>What to test in the spike</h2>
<ol><li>Render the busiest ledger screen as a full-page morph on every commit. Measure render time and SSE bytes with brotli on.</li>
<li>Check that inputs keep focus and value across morphs while another tab writes.</li>
<li>Kill the network mid-stream and check that reconnect resyncs cleanly (the 1.0.5 fixes are in this area).</li>
<li>Have the agent build one feature from <code>docs.md</code> alone and count how often it reaches for pre-1.0 syntax.</li></ol>
{finding('On Stardust', '<p>Stardust has what ownpurse wants from XTDB: immutable history, "as of" queries, Datalog and live results. But it is closed source, alpha, with no format-stability promise, from a small company. For financial records you may need to read in ten years, that is the wrong trade today. Re-check once it has an independent production report and a stable file format.</p>')}
{caveat('<p>The code above is a sketch that hasn\'t been run, and <code>render-page</code>, <code>submit!</code> and <code>entry-from</code> stand in for ownpurse functions. Check the SDK function names against the release you install; it is still a release candidate.</p>')}
</div>'''
    out.append((B + 'for-ownpurse/', 'Datastar for ownpurse', 'Datastar against Electric Clojure for a Clojure + XTDB app with one write path: architecture fit, maturity, licensing, agents, a spike plan, and a view on Stardust.', op))
    return out

def posts(R, BL, d):
    a = lambda n, l=None: _a(R, n, l)
    P = []
    P.append(dict(slug='stardust-the-datastar-database', kj='The Datastar team\'s database is Stardust', conf=HIGH, tags=['sync'],
      title='Stardust: the database Datastar was built for',
      dek='Datastar\'s creator is building an embedded, append-only temporal database with Datalog-style queries and live results. It is closed source and in paid alpha.',
      bluf='Datastar started as the UI for a database. That database, Stardust, is now in a paid alpha: Datomic-style immutable facts and time travel, embedded like SQLite, with live queries that push results for Datastar to stream. It looks like what XTDB lacks. It is also closed, alpha and owned by a small company.',
      body=f'''{intercept('We fixed the web. Now it is time to fix data. Stardust inspired us to create Datastar and related web tooling… Now our focus is Stardust.', '<a href="https://www.stardustdb.com/">stardustdb.com</a>, Team section, November 2026')}
<ul><li><strong>Model:</strong> entities, facts and transactions; an open schema validated on demand; "as of" queries; Datalog-style queries in a "DUST" notation, stored in the database as data.</li>
<li><strong>Live:</strong> subscriptions and reactors push new results. The app re-renders and sends them over Datastar SSE.</li>
<li><strong>Shape:</strong> a library in your process (C ABI) with Go, Clojure, Python, Rust and Odin bindings.</li>
<li><strong>Business:</strong> sold by BitFlip LLC, from $99 for non-commercial use to $1,499 for a team. No public source; the EULA forbids reverse engineering. "No stability or file-format compatibility guarantees."</li></ul>
{finding('Why it matters', '<p>Every sync engine in <a href="/approaches/frontend-sync/">case 002</a> needed a change feed XTDB doesn\'t have. Stardust builds one in. That makes it the most interesting database idea in this space for Clojure developers, and also the hardest to depend on.</p>')}
{caveat('<p>All of this comes from the vendor and its podcast. No independent review or benchmark exists yet. <a href="/projects/datastar/stardust/">Full notes →</a></p>')}'''))
    P.append(dict(slug='datastar-clojure-adopters', kj='Clojure is where Datastar has its most serious users', conf=HIGH, tags=['frontend'],
      title='Why Clojure developers keep landing on Datastar',
      dek='David Nolen rebuilt a production app on it, Biff 2 made it the default, and a Clojure/Conj talk weighs it against local-first ClojureScript.',
      bluf='Datastar suits Clojure because it moves the whole UI to where Clojure is strongest: data on the server, rendered as hiccup, with the REPL in charge. ClojureScript, a build step and client state all go away. In exchange you get a round trip per interaction and a young SDK layer.',
      body=f'''<ul><li><strong>Instabooks:</strong> David Nolen and Anders Murphy rebuilt a faster QuickBooks Online on Datastar. Nolen: "the best tool that I've added to the web technology stuff that I do in at least 12 years" (<a href="https://data-star.dev/essays/datastar_its_pretty_good">essay</a>, <a href="https://youtu.be/2ECucq-mTGg">video</a>).</li>
<li><strong>Biff 2.0</strong> (Sep 2026): Datastar and SQLite are the defaults, through its own {a('jacobobryant/biff', 'biff.datastar')} rather than the official SDK.</li>
<li><strong>{a('andersmurphy/hyperlith', 'hyperlith')}</strong>: Anders Murphy's framework behind the billion-checkbox and Game of Life demos.</li>
<li><strong>Talks:</strong> Yang at Clojure/Conj 2025 (local-first CLJS against Datastar), Arne Brasseur's "Datastar and Clojure" (Oct 2026), Timothy Pratley serving Datastar apps from the REPL.</li>
<li><strong>Libraries:</strong> {a('brianium/datastar.wow')}, {a('dynamic-alpha/hyper')}, {a('ObneyAI/grain')}, {a('realgenekim/datastar-helpers')}, and yogthos's Glimmer.</li></ul>
{caveat('<p>The Clojure layer is young. The official SDK is still a release candidate, Biff\'s library warns it hasn\'t been used at scale, and hyperlith says its API "can change at any time".</p>')}''',
      after=table(['andersmurphy/hyperlith', 'jacobobryant/biff', 'starfederation/datastar-clojure', 'brianium/datastar.wow', 'dynamic-alpha/hyper', 'ObneyAI/grain', 'realgenekim/datastar-helpers'], 'Clojure on Datastar', 'full')))
    P.append(dict(slug='datastar-and-agents', kj='Agents need the Datastar docs in context', conf=MOD, tags=['agents', 'frontend'],
      title='Coding agents and Datastar: load the docs, keep it server-side',
      dek='The creator says models are overfitted to SPAs. Field reports are mixed. What helps: the single-file docs, skills, and a codegen or lint layer.',
      bluf='Agents get Datastar wrong in predictable ways: pre-1.0 syntax, SPA habits, and the attribute DSL. Give them https://data-star.dev/docs.md (about 195 KB, one file) or a skill. Keep logic in server-side handlers, where the agent can check output with curl or at the REPL.',
      body=f'''<ul><li><strong>Worked:</strong> a multiplayer tank game "vibed into existence with Claude Code" on Go + Datastar (<a href="https://news.ycombinator.com/item?id=43317936">HN, Mar 2025</a>); copy-to-clipboard added "in maybe 1 minute" with an agent.</li>
<li><strong>Failed:</strong> Codex "absolutely ate it" on a simple persist-on-change element, even with the Datastar manual linked from AGENTS.md (<a href="https://news.ycombinator.com/item?id=47288993">HN, Mar 2026</a>).</li>
<li><strong>Tooling response:</strong> the author of {a('romshark/datapages')} said agents "kept messing up", so he built a Go code generator and linter that own the plumbing. Agent skills exist in {a('cbeauhilton/datastar-skills')}, {a('danmestas/wardrobe')} (Tao and patterns as separate skills) and {a('maragudk/skills')}.</li>
<li><strong>The team:</strong> "if you want to vibe code something quickly, use React" (Talk Python #537). Datastar's own code is "written by hand". There is no llms.txt, but <code>docs.md</code> is the whole manual in one file.</li></ul>
{finding('The pattern', '<p>It is the same pattern as <a href="/practices/agentic-practices/">case 005</a>: what fixes agent mistakes is a verifier (a linter, a generator, curl, the REPL) plus a short pointer to the current docs. More prose instructions don\'t.</p>')}''',
      after=table(AGENT, 'Agent tooling for Datastar', 'full')))
    return P

def sources():
    S = lambda date, title, who, url, type, k, sum: dict(date=date, title=title, who=who, url=url, type=type, k=k, sum=sum)
    F = ['frontend']
    return [
     S('2026-11', 'Datastar', 'Star Federation', 'https://data-star.dev/', 'doc', F, 'The hypermedia framework: backend reactivity like htmx, frontend reactivity like Alpine, in one 12.5 KiB file.'),
     S('2026-11', 'The Tao of Datastar', 'Star Federation', 'https://data-star.dev/guide/the_tao_of_datastar', 'doc', F, 'State on the server, few signals, fat morph, CQRS, brotli, no optimistic UI.'),
     S('2026-11', 'Datastar SSE events reference', 'Star Federation', 'https://data-star.dev/reference/sse_events', 'doc', F, 'datastar-patch-elements and datastar-patch-signals.'),
     S('2026-11', 'Datastar security reference', 'Star Federation', 'https://data-star.dev/reference/security', 'doc', F, 'CSP mode, unsafe-eval, and why signals must be validated server-side.'),
     S('2026-11', 'Datastar Pro', 'Star Federation', 'https://data-star.dev/pro', 'doc', F, '$349 solo, $1,299 team, one-time; extra attributes, Inspector, bundler, Stellar CSS.'),
     S('2026-11', 'Datastar docs in one Markdown file', 'Star Federation', 'https://data-star.dev/docs.md', 'doc', F + ['agents'], 'The full manual (~195 KB) for loading into an agent\'s context.'),
     S('2025-10', 'Greedy Developer?', 'Delaney Gillilan', 'https://data-star.dev/essays/greedy_developer', 'article', F, 'The team\'s answer to the Pro backlash: core stays MIT, Pro plugins are new code.'),
     S('2025', 'V1 and Beyond', 'Delaney Gillilan', 'https://data-star.dev/essays/v1_and_beyond', 'article', F, '"Zero reason to use htmx going forward"; the origin in a database project.'),
     S('2026-11', 'starfederation/datastar releases', 'GitHub', 'https://github.com/starfederation/datastar/releases', 'tool', F, 'From beta.1 (Jan 2025) through RC.1 Pro, RC.6 syntax change, 1.0 (Apr 2026) and 1.0.5.'),
     S('2026-11', 'Datastar Clojure SDK', 'Jeremy Schoffen', 'https://github.com/starfederation/datastar-clojure', 'tool', F, 'ring and http-kit adapters, brotli, malli schemas; still 1.0.0-RC13.'),
     S('2026-10', 'Understanding Datastar', 'Jacob O\'Bryant', 'https://biffweb.com/p/understanding-datastar/', 'article', F, 'Biff 2\'s re-render-on-commit model and its costs.'),
     S('2026', 'Datastar: it\'s pretty good', 'David Nolen, Anders Murphy', 'https://data-star.dev/essays/datastar_its_pretty_good', 'article', F, 'Instabooks rebuilt on Datastar: "no regrets".'),
     S('2026', 'Datastar: it\'s pretty good, with David Nolen (video)', 'Datastar channel', 'https://youtu.be/2ECucq-mTGg', 'talk', F + ['talk'], 'Nolen on rebuilding a fast QuickBooks Online UI.'),
     S('2025-11', 'From Tomorrow Back to Yesterday: a tale of two web architectures', 'Yang, Clojure/Conj 2025', 'https://www.youtube.com/watch?v=8W6Lr1hRgXo', 'talk', F + ['talk'], 'Local-first ClojureScript against a Datastar rewrite, with production metrics.'),
     S('2025-04', 'Realtime collaborative web apps without ClojureScript', 'Anders Murphy', 'https://andersmurphy.com/2025/04/07/clojure-realtime-collaborative-web-apps-without-clojurescript.html', 'article', F, 'hyperlith and the Datastar approach in Clojure.'),
     S('2025-04', 'Why you should use brotli compression with SSE', 'Anders Murphy', 'https://andersmurphy.com/2025/04/15/why-you-should-use-brotli-sse.html', 'article', F, 'Brotli window tuning: 30:1 to 150–250:1, CPU cut 4–8x.'),
     S('2026-10', 'Datastar and Clojure', 'Arne Brasseur', 'https://www.youtube.com/watch?v=sR0yrp2wDUU', 'talk', F + ['talk'], 'SSE, morphing and compression; multiplayer out of the box.'),
     S('2026-07', 'Put State in the Right Place', 'Delaney Gillilan, SSW 2026', 'https://www.youtube.com/watch?v=W7Ki3aXgmZU', 'talk', F + ['talk'], 'The most-watched Datastar talk.'),
     S('2026', 'Datastar: modern web dev, simplified (Talk Python #537)', 'Talk Python', 'https://talkpython.fm/episodes/show/537/datastar-modern-web-dev-simplified', 'talk', F + ['talk', 'agents'], 'htmx\'s last 10%; LLMs overfitted to SPA patterns.'),
     S('2026-11', 'Rendering in batches with Glimmer and Datastar', 'Dmitri Sotnikov', 'https://yogthos.net/posts/2026-11-10-glimmer-datastar.html', 'article', F, 'Server-side ratoms pushing patches, batched per tick.'),
     S('2026', 'Datastar observations', 'Howard Lewis Ship', 'https://dev.to/hlship/datastar-observations-3icg', 'article', F, 'From Svelte to Datastar in a Babashka tool.'),
     S('2025-10', 'Why I switched from htmx to Datastar', 'Chris May', 'https://everydaysuperpowers.dev/articles/why-i-switched-from-htmx-to-datastar/', 'article', F, 'htmx + Alpine fell out of step; the server decides what changes.'),
     S('2025-11', 'Datastar first impressions, coming from React', 'threadgold.nz', 'https://threadgold.nz/writing/datastar-coming-from-react', 'article', F, 'No build step; global signals and no LSP hurt.'),
     S('2026-11', 'A look at Datastar', 'noteflakes', 'https://noteflakes.com/articles/2026-11-04-datastar', 'article', F, 'UI = f(state); page-global signals the main con.'),
     S('2026-01', 'Joyus: I tried Datastar', 'Alex Moon', 'https://ajmoon.com/posts/joyus-i-tried-datastar', 'article', F, 'Light DOM and global state; forked for web components.'),
     S('2025-01', 'Datastar: web framework for the future?', 'Chris Malek', 'https://chrismalek.me/posts/data-star-first-impressions/', 'article', F, 'htmx and Alpine in a single library.'),
     S('2025-07', 'Htmx, Datastar, greedy developer', 'drshapeless', 'https://drshapeless.com/blog/posts/htmx,-datastar,-greedy-developer.html', 'article', F, 'The Pro "rugpull" complaint.'),
     S('2025-10', 'Datastar: lightweight hypermedia framework (HN)', 'Hacker News', 'https://news.ycombinator.com/item?id=45536618', 'forum', F, 'The Pro row; DSL complaints; "a paradigm shift for the better".'),
     S('2025-10', 'I switched from htmx to Datastar (HN)', 'Hacker News', 'https://news.ycombinator.com/item?id=45536000', 'forum', F, '315 points, 380 comments, mostly on Pro.'),
     S('2026-03', 'Codex fails a Datastar task despite the manual (HN comment)', 'Hacker News', 'https://news.ycombinator.com/item?id=47288993', 'forum', F + ['agents'], 'A negative agent data point.'),
     S('2025-01', 'Alternatives to htmx', 'Carson Gross', 'https://four.htmx.org/essays/alternatives', 'article', F, 'Datastar is smaller than htmx and began as a proposed TypeScript rewrite of it.'),
     S('2026-11', 'Stardust', 'BitFlip LLC', 'https://www.stardustdb.com/', 'doc', ['sync'], 'Append-only temporal data engine: "Keep every change. Question any moment."'),
     S('2026-11', 'Stardust theory overview', 'BitFlip LLC', 'https://www.stardustdb.com/theory/overview', 'doc', ['sync'], 'Entities, facts, transactions, reification, plugins.'),
     S('2026-11', 'Stardust inspirations', 'BitFlip LLC', 'https://www.stardustdb.com/theory/inspirations', 'doc', ['sync'], 'Datomic, Asami, Clojure, Flecs, SQLite, DuckDB, TigerBeetle.'),
     S('2026-10', 'Stardust license agreement', 'BitFlip LLC', 'https://www.stardustdb.com/eula', 'doc', ['sync'], 'Proprietary; sold by BitFlip LLC, Nevada.'),
     S('2026-09', 'Rocket breaks free; Stardust underway', 'Datastar podcast', 'https://www.youtube.com/watch?v=U87Vorhd0EA', 'talk', ['sync', 'talk'], 'First public walkthrough of Stardust.'),
     S('2026-10', 'From the Outskirts: Q3 2026', 'Casey Link', 'https://casey.link/blog/from-the-outskirts-q3-2026/', 'article', ['sync'], 'Stardust in public preview; "SQLite + Datomic + Redis + … in one small binary".'),
    ]
