"""Case 002: a front end for a Clojure backend, with live data sync. Research filed 2026-11-10."""
import html
from content import _a, finding, caveat, signal, intercept, stat, table, HIGH, MOD, LOW

REF = 'SMAF-002'
code = lambda src, cap=None: (f'<figure class="codefig"><figcaption>{cap}</figcaption>' if cap else '<figure class="codefig">') + f'<pre class="code"><code>{html.escape(src.strip())}</code></pre></figure>'

def conf_chip(c): return f'<span class="conf {c[0]}">{c[1]}</span>'

ENGINES = ['rocicorp/mono', 'electric-sql/electric', 'durable-streams/durable-streams', 'TanStack/db', 'livestorejs/livestore', 'pubkey/rxdb',
           'instantdb/instant', 'convex/convex-backend', 'powersync-ja/powersync-service', 'garden-co/jazz', 'aspen-cloud/triplit', 'automerge/automerge',
           'automerge/automerge-repo', 'yjs/yjs', 'jamsocket/y-sweet', 'loro-dev/loro', 'tinyplex/tinybase', 'evoluhq/evolu', 'dxos/dxos',
           'wzhudev/reverse-linear-sync-engine']
SERVER_UI = ['starfederation/datastar', 'starfederation/datastar-clojure', 'andersmurphy/hyperlith', 'bigskysoftware/htmx', 'jacobobryant/biff',
             'hotwired/turbo', 'livewire/livewire', 'phoenixframework/phoenix_live_view', 'lustre-labs/lustre']
FP_FRONT = ['elm/compiler', 'lustre-labs/lustre', 'rescript-lang/rescript', 'Effect-TS/effect', 'squint-cljs/squint', 'squint-cljs/cherry']
CLJ_OPTS = ['hyperfiddle/electric', 'hyperfiddle/electric3-starter-app', 'leonoel/missionary', 'fulcrologic/fulcro', 'fulcrologic/fulcro-rad', 'wilkerlucio/pathom3',
            'fulcrologic/statecharts', 'day8/re-frame', 'day8/re-frame2', 'day8/re-frame-pair', 'day8/re-frame-10x', 'pitch-io/uix', 'lilactown/helix',
            'cjohansen/replicant', 'cjohansen/nexus', 'starfederation/datastar-clojure', 'andersmurphy/hyperlith', 'brianium/datastar.wow', 'taoensso/sente',
            'tonsky/datascript', 'replikativ/datahike', 'replikativ/konserve-sync', 'simongray/like-minded']
AGENT_TOOLS = ['bhauman/clojure-mcp', 'bhauman/clojure-mcp-light', 'clj-kondo/clj-kondo', 'metosin/malli', 'thheller/shadow-cljs', 'day8/re-frame-pair']

TX_HOOK = r'''
(ns ownpurse.changes
  "After every write, tell connected clients what changed."
  (:require [org.httpkit.server :as http]
            [xtdb.api :as xt]))

(defonce clients (atom #{}))                         ; open SSE channels

(defn publish! [{:keys [tx-id tables]}]
  (let [msg (str "event: tx\ndata: " (pr-str {:tx-id tx-id :tables tables}) "\n\n")]
    (doseq [ch @clients] (http/send! ch msg false))))

;; The one write path that the admin, the CLI and agents all go through.
(defn submit! [node tx-ops]
  (let [{:keys [tx-id] :as tx} (xt/execute-tx node tx-ops)]
    (publish! {:tx-id tx-id :tables (into #{} (map second) tx-ops)})  ; [:put-docs :accounts {...}] -> :accounts
    tx))

;; GET /api/changes : a text/event-stream the browser, the TUI or an agent can tail
(defn changes-handler [req]
  (http/as-channel req
    {:on-open  (fn [ch]
                 (http/send! ch {:headers {"Content-Type" "text/event-stream"
                                           "Cache-Control" "no-cache"}} false)
                 (swap! clients conj ch))
     :on-close (fn [ch _] (swap! clients disj ch))}))
'''

UIX_HOOK = r'''
(ns ownpurse.admin.live
  (:require [uix.core :as uix]))

;; One EventSource for the whole page; components subscribe by table.
(defonce events (js/EventSource. "/api/changes"))

(defn use-live
  "Like the old setInterval fetch, but refetches only when a tx touches `tables`."
  [path tables]
  (let [[data set-data!] (uix/use-state nil)]
    (uix/use-effect
      (fn []
        (let [load!  #(-> (js/fetch path) (.then (fn [r] (.json r)))
                          (.then (fn [j] (set-data! (js->clj j :keywordize-keys true)))))
              on-tx  (fn [e] (let [{changed :tables} (cljs.reader/read-string (.-data e))]
                               (when (some (set tables) changed) (load!))))]
          (load!)
          (.addEventListener events "tx" on-tx)
          #(.removeEventListener events "tx" on-tx)))
      [path])
    data))

;; usage: (let [accounts (use-live "/api/accounts" [:accounts :postings])] ...)
'''

DATASTAR = r'''
(ns ownpurse.web.trial-balance
  "The view is a pure function of the database.
  The server pushes it again whenever a transaction lands."
  (:require [starfederation.datastar.clojure.api :as d*]
            [starfederation.datastar.clojure.adapter.http-kit :as hk]
            [hiccup2.core :as h]))

(defn view [rows]                                      ; view = f(state), testable at the REPL
  [:main#trial-balance
   [:table (for [{:keys [account debit credit]} rows]
             [:tr [:td account] [:td.r debit] [:td.r credit]])]])

(defn stream [req]
  (hk/->sse-response req
    {hk/on-open  (fn [sse]
                   (let [push! #(d*/patch-elements! sse (str (h/html (view (trial-balance-q)))))]
                     (push!)
                     (add-watch last-tx sse (fn [& _] (push!)))))  ; publish! bumps last-tx
     hk/on-close (fn [sse _] (remove-watch last-tx sse))}))
'''

ELECTRIC = r'''
(e/defn Accounts []
  ;; Electric v3 sketch: one expression, the compiler splits it into client and server halves.
  (e/server
    (let [tx   (e/watch !last-tx)                       ; re-runs when publish! bumps the atom
          rows (e/Offload #(accounts-q node tx))]       ; blocking XTDB query off the reactive thread
      (e/client
        (dom/ul
          (e/for [a (e/diff-by :xt/id rows)]            ; rows stream to the client as diffs
            (dom/li (dom/text (:account/name a)))))))))
'''

def pages(memo, R, d):
    a = lambda n, l=None: _a(R, n, l)
    v = lambda n, k='s': f'{R[n.lower()][k]:,}'
    M = lambda title, subj, eb, stamp='Open': memo(title, subj, stamp, eyebrow=f'Case 002 // {eb}', ref=REF)
    out = []

    # ---------------- brief
    brief = f'''{M('A front end for a Clojure backend, with live data sync', 'The backend is Clojure. What should the front end be, which systems sync data between server and client, and does ClojureScript cost me anything?', 'brief')}
<div class="bluf"><p><strong>Stay in ClojureScript, and stop polling.</strong> The cost of ClojureScript when agents write the code is small and fixable with tooling. Almost every sync engine in other languages needs Postgres or its own server, so none of them can sit in front of XTDB. For ownpurse the first move is the same whatever UI wins: add a hook on the one write path that pushes "this transaction touched these tables" over server-sent events. Then spike Datastar and Electric on one screen each before committing to a rewrite.</p></div>
<div class="prose">
<h2>The question</h2>
<p>ownpurse is a local ledger in Clojure on XTDB, run from your own machine. Its clients are a web admin, a CLI, a TUI and AI agents, all over one local HTTP API. Today the admin is about 11,000 lines of UIx (React 19) on shadow-cljs that polls REST endpoints with <code>setInterval</code>. You want to stay in Clojure on the front end, because you read Clojure and can tell whether the code makes sense. You like Elm-style, functional, immutable code. You liked Electric and are curious about Fulcro. Three questions follow: which systems handle server-to-client sync, does ClojureScript cost you anything, and what works for something shaped like ownpurse.</p>
<h2>Key judgments</h2>
<ol class="kj">
<li><div><h3>No mainstream sync engine can sit in front of XTDB</h3><p>Zero needs Postgres 15+ with logical replication. ElectricSQL needs Postgres. PowerSync needs Postgres, MongoDB, MySQL, SQL Server or Convex. Instant, Convex, Jazz and Triplit bring their own servers. XTDB v2 has no outbound change feed (the request, xtdb/xtdb#2454, is still open). Your own write path is the change feed. {conf_chip(HIGH)} <a class="more" href="/blog/xtdb-has-no-change-feed/">dispatch →</a></p></div></li>
<li><div><h3>ClojureScript costs little when agents write it, if you wire up the loop</h3><p>No benchmark shows frontier models writing worse Clojure than TypeScript. The real gap is that TypeScript gives agents a type checker for free. A REPL over MCP, paren repair, clj-kondo and malli close most of it. {conf_chip(MOD)} <a class="more" href="/blog/the-clojurescript-tax/">dispatch →</a></p></div></li>
<li><div><h3>Server-driven UI gives agents the shortest feedback loop</h3><p>With Datastar the whole UI is server-side Clojure, so an agent checks its work with curl or the REPL. Biff 2.0 switched to it in September 2026. {conf_chip(MOD)} <a class="more" href="/blog/server-driven-ui-and-agents/">dispatch →</a></p></div></li>
<li><div><h3>Electric is still the boldest idea, and still not the safe bet</h3><p>v3 is in private beta under a commercial license. The team says it is "for experts", and reports of agents writing Electric are mixed. It's worth a one-screen spike, not the whole admin. {conf_chip(MOD)} <a class="more" href="/blog/electric-in-2026/">dispatch →</a></p></div></li>
<li><div><h3>Fulcro has the most agent-ready idea in Clojure front ends, and the most ceremony</h3><p>Its new headless mode runs a whole app, real remotes included, on the JVM with no browser. That is exactly the check loop agents need. The price is idents, queries and resolvers for every feature. {conf_chip(LOW)} <a class="more" href="/blog/fulcro-headless/">dispatch →</a></p></div></li>
<li><div><h3>The sync market is consolidating, so bet on protocols, not vendors</h3><p>In twelve months Electric joined Databricks and wound down its cloud, Supabase bought Triplit, and Y-Sweet's team joined Modal. Zero and Instant both reached 1.0. {conf_chip(HIGH)} <a class="more" href="/blog/sync-engines-consolidate/">dispatch →</a></p></div></li>
</ol>
<h2>Three ways forward for ownpurse</h2>
<table class="cmp"><thead><tr><th>Path</th><th>What changes</th><th>Good</th><th>Costs</th></tr></thead><tbody>
<tr><td><strong>A. Keep UIx, add push</strong><br><span class="conf high">DO FIRST</span></td><td>A tx hook publishes changes over SSE. A <code>use-live</code> hook refetches what changed.</td><td>No rewrite. The REST API stays the one contract for the UI, CLI and agents. Takes days.</td><td>React hooks are less purely functional than you'd like, and invalidation is hand-rolled.</td></tr>
<tr><td><strong>B. Datastar, server-driven</strong><br><span class="conf mod">SPIKE ONE SCREEN</span></td><td>Views become <code>.clj</code> hiccup functions of XTDB queries, pushed over SSE.</td><td>One runtime, the most readable code, and the best agent loop (curl and the REPL). Datastar is 1.0.</td><td>Rewrites the admin. Rich widgets (grids, drag and drop) live in Datastar expressions, not Clojure.</td></tr>
<tr><td><strong>C. Electric v3</strong><br><span class="conf low">SPIKE ONE SCREEN</span></td><td>The UI queries XTDB directly through Electric's compiler-split program.</td><td>No API plumbing for the UI. Reactive queries in place. Free for non-commercial use and bootstrappers.</td><td>Beta, licensed, and its UI bypasses the API the CLI and agents use. Mixed agent reports.</td></tr>
</tbody></table>
<p>Read the full reasoning, with code, on the <a href="/approaches/frontend-sync/ownpurse/">for-ownpurse page</a>.</p>
{finding('The one move every path shares', '<p>Your writes all go through one in-process Clojure server. After each <code>execute-tx</code>, publish <code>{:tx-id … :tables …}</code> on an SSE endpoint. That replaces polling today, feeds Datastar or Electric later, and gives the CLI, the TUI and agents a change feed they can tail with curl. XTDB system time doubles as the sync cursor.</p>')}
<h2>In this case file</h2>
<ul>
<li><a href="/approaches/frontend-sync/landscape/">Sync engines, every language</a>: the field in November 2026, what is pushing the boundaries, and what fits a Clojure server.</li>
<li><a href="/approaches/frontend-sync/clojure/">The Clojure options</a>: Electric, Fulcro, re-frame and re-frame2, UIx with push, Replicant, Datastar, Datahike.</li>
<li><a href="/approaches/frontend-sync/cljs-cost/">Does ClojureScript cost me?</a> Benchmarks, failure modes, the TypeScript contrast, and the agent setup that closes the gap.</li>
<li><a href="/approaches/frontend-sync/ownpurse/">For ownpurse</a>: the three architectures with code sketches, and a plan.</li>
</ul>
</div>
{table(['hyperfiddle/electric', 'fulcrologic/fulcro', 'day8/re-frame', 'pitch-io/uix', 'starfederation/datastar', 'starfederation/datastar-clojure', 'rocicorp/mono', 'TanStack/db', 'electric-sql/electric', 'instantdb/instant', 'livestorejs/livestore', 'pubkey/rxdb'], 'Shortlist: the projects this case turns on', 'full')}'''
    out.append(('/approaches/frontend-sync/', 'Case 002: a front end for a Clojure backend', 'Which front end and sync system for a Clojure/XTDB backend, whether ClojureScript costs anything when agents write the code, and what fits ownpurse.', brief))

    # ---------------- landscape
    land = f'''{M('Sync engines, every language', 'Server-to-client data sync in November 2026: what exists, how each one works, and what can sit in front of a Clojure server', 'sync engines')}
<div class="bluf"><p>App-data sync has settled on one pattern: the server stays authoritative, the client applies writes optimistically and replays them when the server answers. CRDTs are kept for text and documents. The engines that do this well (Zero, ElectricSQL, PowerSync) read Postgres's replication stream, which XTDB doesn't have. The ones that fit a Clojure server either let you implement a small backend protocol (TanStack DB, RxDB, Replicache, LiveStore) or skip the client database and stream the UI from the server (Datastar, htmx, LiveView).</p></div>
<div class="prose">
<h2>Four ways to sync</h2>
<ul>
<li><strong>Query subscription, server-authoritative.</strong> The client subscribes to queries and keeps a local cache. Mutations run optimistically and are rebased when the server answers. Zero, Replicache, Instant, Convex and TanStack DB work this way, and so do <a href="https://github.com/wzhudev/reverse-linear-sync-engine">Linear</a> and <a href="https://www.figma.com/blog/livegraph-real-time-data-at-scale/">Figma's LiveGraph</a>.</li>
<li><strong>Replicate into a client database.</strong> PowerSync and ElectricSQL stream rows into SQLite or memory on the client. Writes go up through your own API.</li>
<li><strong>Event sourcing and CRDTs.</strong> LiveStore syncs an ordered event log and builds SQLite from it. Automerge, Yjs and Loro merge concurrent edits without a referee. That suits documents, not double-entry ledgers.</li>
<li><strong>Server-rendered streaming.</strong> There is no client database at all. The server owns the state and streams HTML patches: Phoenix LiveView, Datastar, htmx, Hotwire, Lustre server components.</li>
</ul>
{stat('0 of 3', 'Of Zero, ElectricSQL and PowerSync, the three best-known engines that replicate a database to the client, none can read from XTDB. All three need a source with logical replication or CDC, and XTDB v2 has no outbound change feed (<a href="https://github.com/xtdb/xtdb/issues/2454">#2454</a>, open). XTDB speaking the Postgres wire protocol doesn\'t help, because pgwire queries aren\'t a replication stream.', 'The constraint')}
<h2>What is pushing the boundaries</h2>
<ol>
<li><strong>Sync as the substrate for AI agents.</strong> Electric now calls itself "agents on sync" and ships <a href="https://github.com/durable-streams/durable-streams">Durable Streams</a>, an open protocol for replayable HTTP streams, as "the data primitive for the agent loop". Instant pitches itself as "the best backend for AI-coded apps". SyncConf's tagline is "realtime collaboration between humans and agents". This matters for ownpurse, where agents are first-class clients.</li>
<li><strong>Query-driven partial sync with incremental view maintenance.</strong> Clients subscribe to queries instead of downloading tables. {a('TanStack/db', 'TanStack DB')} keeps live queries current with differential dataflow (d2ts), and Zero does the same with ZQL.</li>
<li><strong>Server authority plus client rebase has won for app data.</strong> Zero, Replicache, PowerSync, ElectricSQL and TanStack DB all keep the server canonical. The reverse-engineered Linear sync engine, endorsed by Linear's CTO, is the clearest write-up.</li>
<li><strong>Event sourcing on the client.</strong> LiveStore and Jazz 2 materialise state from a synced log, which is close in spirit to XTDB's immutable, bitemporal record.</li>
<li><strong>Hypermedia streaming as the sync model.</strong> Datastar 1.0 (April 2026, SDKs in a dozen languages including Clojure), htmx 4 and Lustre server components drop the client database entirely.</li>
<li><strong>Local-first auth and encryption are the open frontier.</strong> See Ink &amp; Switch's <a href="https://www.inkandswitch.com/keyhive/notebook/">Keyhive</a> (group keys and capabilities that travel with the data) and Evolu's end-to-end-encrypted relays.</li>
<li><strong>CRDTs got fast.</strong> Automerge 3 cut memory use more than 10x; Loro 1.0 brought 10–100x faster import.</li>
</ol>
{intercept('Everything we\'ve open sourced stays open source.', 'Electric, on joining Neon at Databricks, <a href="https://electric.ax/blog/2026/08/11/electric-joining-databricks">August 2026</a>. Electric Cloud is winding down; PowerSync published a <a href="https://docs.powersync.com/migration-guides/electric">migration guide</a>.')}
<h2>Fit for a Clojure and XTDB server, ranked</h2>
<ol>
<li><strong>{a('starfederation/datastar', 'Datastar')} with its <a data-repo="starfederation/datastar-clojure" href="https://github.com/starfederation/datastar-clojure">Clojure SDK</a>.</strong> Clojure renders hiccup and streams patches over SSE when a transaction touches what a view shows. This is the most inspectable option, but it replaces the UIx app.</li>
<li><strong>Your own small change feed, feeding TanStack DB or a plain UIx store.</strong> One <code>/api/changes</code> SSE endpoint. TanStack DB's Query Collection works against any REST API. This is the smallest step from polling.</li>
<li><strong>{a('pubkey/rxdb', 'RxDB')}, Replicache or {a('livestorejs/livestore', 'LiveStore')} with the backend side written in Clojure.</strong> Each documents a small server contract. Choose this if you want a real offline client database. LiveStore's event log maps best onto XTDB, but it is pre-1.0 and heavy on TypeScript and Effect.</li>
<li><strong>{a('hyperfiddle/electric', 'Electric')}.</strong> Native Clojure on the same JVM as XTDB. Commercial license for business use, and the network boundary is hidden by the compiler.</li>
<li><strong>Implement an open wire protocol</strong> (Electric's shape API or Durable Streams) in Clojure to reuse their clients. Feasible, but a lot of work.</li>
<li><strong>CRDTs</strong> for collaborative free-text fields only, never ledger entries.</li>
</ol>
{caveat('<p>Not viable without replacing XTDB: Zero, ElectricSQL sync, PowerSync, Instant, Convex, Jazz 2, Triplit, Evolu, DXOS. LiveView, Livewire and Lustre are server frameworks in other languages, but they are worth studying as designs.</p>', 'Ruled out')}
{signal('<p>The best code to read before building your own invalidator is in Clojure already. Instant\'s sync engine tails the Postgres WAL, maps changes to topics and invalidates the subscribed queries (<a href="https://www.instantdb.com/essays/architecture">architecture essay</a>, source in ' + a('instantdb/instant') + '). ownpurse can do the same thing one step earlier, at its own write path.</p>', 'Worth reading')}
</div>
{table(ENGINES, 'Sync engines, client stores and CRDTs', 'full', 'cat')}
{table(SERVER_UI, 'Server-driven UI', 'full')}
{table(FP_FRONT, 'Typed and functional front ends', 'full')}'''
    out.append(('/approaches/frontend-sync/landscape/', 'Sync engines, every language', 'Server-to-client data sync in 2026: Zero, ElectricSQL, TanStack DB, LiveStore, Instant, Convex, PowerSync, CRDTs and server-driven UI, and what can sit in front of a Clojure server.', land))

    # ---------------- clojure options
    clj = f'''{M('The Clojure options', 'Electric, Fulcro, re-frame, UIx with push, Replicant, Datastar and Datahike, judged for a local ledger with agents as clients', 'clojure options')}
<div class="bluf"><p>Every Clojure option leaves live sync to you except Electric (which streams a reactive program) and Datahike (which syncs its own store). So the choice is really about how the UI is written. Keep UIx and add push, switch to server-driven Datastar, or bet on Electric. Fulcro is the rigorous choice if you want EQL to become the public API. re-frame has the best tooling today for agents working on a running app.</p></div>
<div class="prose">
<h2>Electric v3</h2>
<p>One <code>e/defn</code> mixes client and server code, and the compiler splits it into reactive halves joined by a WebSocket. It runs on {a('leonoel/missionary', 'Missionary')}. It doesn't sync data. It streams a dataflow graph and reruns server queries when their inputs change, so you still feed it a signal from your own transactions.</p>
<ul>
<li><strong>Status:</strong> <code>v3-alpha-SNAPSHOT</code>, "private beta with commercial users". The public repo's last commit was March 2026; the {a('hyperfiddle/electric3-starter-app', 'starter app')} had commits in October 2026.</li>
<li><strong>License:</strong> source-available. Free for non-commercial use and for bootstrappers under $200k revenue or $500k funding. Otherwise $480 per developer per month, with a 33% startup discount. The license check is a login at development time only (<a href="https://tana.pub/lQwRvGRaQ7hM/electric-v3-license-change">announcement</a>).</li>
<li><strong>Offline:</strong> not supported. "Persistent server connection assumed."</li>
<li><strong>Self-reported issues (July 2026):</strong> glitches, front-end performance, and slow rendering of collections under 500 rows without virtual scroll.</li>
</ul>
{intercept('Electric is for experts … If you can build your thing in any other way, you should do that!', 'Hyperfiddle\'s mission and business document, 2025–2026')}
<p><strong>Agents:</strong> mixed. In March 2026 one user wrote that "working on electric with claude code/codex is quite painful… it struggles to understand, especially at the front/back interop" (<a href="https://clojurians-log.clojureverse.org/hyperfiddle/2026-03-07">#hyperfiddle</a>). Another noted agents need two runtimes running to check their work. Others praised a "claude + electric + rama" workflow (<a href="https://clojurians-log.clojureverse.org/hyperfiddle/2026-02-15">#hyperfiddle</a>). Hyperfiddle itself says: "Please do not ask us to debug or even look at AI slop… You are welcome to use AI."</p>
<p><strong>For ownpurse:</strong> technically a great fit, with XTDB in process and zero latency. But the Electric UI would bypass the REST API the CLI and agents use, so you would keep two access paths.</p>

<h2>Fulcro 3, RAD and Pathom 3</h2>
<p>{a('fulcrologic/fulcro', 'Fulcro')} keeps a normalized client database. Components declare EQL queries and idents next to their render code. Mutations have an optimistic part and a remote part, and Pathom answers the queries on the server. {a('fulcrologic/fulcro-rad', 'RAD')} generates forms and reports from attribute definitions.</p>
<ul>
<li><strong>Activity:</strong> 3.10.0 (September 2026), 3.10.1 (October 2026), React 19.1 in its package.json. {a('wilkerlucio/pathom3', 'Pathom 3')} is still alpha and slow (last commit January 2026).</li>
<li><strong>Agent tooling:</strong> a headless mode (December 2025) runs a full app on the JVM, real remotes included, with <code>click-on!</code> and <code>type-into!</code>. The repo ships a <code>CLAUDE.md</code>, and RAD publishes docs meant as LLM context.</li>
</ul>
{intercept('In 2025 the LLMs really crossed a line … I\'m developing three or four times more stuff than I was.', 'Tony Kay, Fulcro\'s author, <a href="https://podscan.fm/podcasts/clojurestream-podcast/episodes/e103-llm-experience-report-with-tony-kay">ClojureStream E103</a>, April 2026')}
<p><strong>The catch:</strong> to follow one feature you read the ident, query, initial state, mutation, remote and resolver, often across files. An agent that gets an ident slightly wrong produces silently missing data, not an error. That is our inference, not a measured result. Live sync isn't built in either. <strong>For ownpurse:</strong> choose it only if EQL should become the API for the CLI and agents too.</p>

<h2>re-frame, and re-frame2</h2>
<p>{a('day8/re-frame', 're-frame')} 1.4.7: pure event handlers over one immutable app-db. Sync is up to you (for example over {a('taoensso/sente', 'sente')}). Its standout is {a('day8/re-frame-pair', 're-frame-pair')}, a Claude Code skill that lets an agent read app-db, dispatch events, trace, hot-swap handlers and time-travel in the running app. {a('day8/re-frame2', 're-frame2')} is designed AI-first ("the spec is complete enough that a sufficiently capable AI can one-shot a working implementation") but is pre-alpha and unpublished.</p>

<h2>Keep UIx (or Helix) and add push</h2>
<p>{a('pitch-io/uix', 'UIx')} 1.4.9 tracks React 19.2. Add one SSE endpoint that publishes transactions, and a hook that refetches what changed (code on the <a href="/approaches/frontend-sync/ownpurse/">ownpurse page</a>). This is the least disruptive path, and React is the UI library models have seen most.</p>

<h2>Replicant and Nexus</h2>
<p>Pure <code>state → hiccup</code> rendering with event handlers as data, and the views render to strings on the JVM, so they can be tested in Clojure. This is the most Elm-like option in Clojure. Both moved to <a href="https://codeberg.org/cjohansen/replicant">Codeberg</a> on 6 November 2026 and are active there. There's no sync, so you add your own push channel. The code is easy for agents to work with, but the author is openly anti-LLM, so don't expect agent-oriented docs.</p>

<h2>Datastar, hyperlith and Biff 2</h2>
<p>{a('starfederation/datastar', 'Datastar')} 1.0.5 with an active {a('starfederation/datastar-clojure', 'Clojure SDK')}. {a('andersmurphy/hyperlith', 'hyperlith')} shows the pattern: one render function per page, re-rendered on any database change (throttled), with the whole <code>&lt;main&gt;</code> pushed over compressed SSE and morphed in the browser. <a href="https://biffweb.com/p/biff2-released/">Biff 2.0</a> (September 2026) uses Datastar by default instead of htmx.</p>
{intercept('LLM agents … need validation feedback. It is complex for the LLM to gather feedback with Electric. You have 2 environments (JS and JVM). With Datastar it is dead simple for the LLM to validate, basically just curl.', 'Hendrik, <a href="https://clojurians-log.clojureverse.org/hyperfiddle/2026-03-04">#hyperfiddle</a>, March 2026')}

<h2>Datahike: real local-first sync in Clojure</h2>
<p>{a('replikativ/datahike', 'Datahike')} is the only Clojure database with genuine browser sync: an IndexedDB store and a streaming writer built on {a('replikativ/konserve-sync', 'konserve-sync')}, both beta. A double-entry accounting product, <a href="https://stub.africa/">Stub</a>, runs on Datahike. Using it would mean replacing or mirroring XTDB, so it is worth knowing only if real offline or multi-device sync becomes a requirement.</p>

<h2>Compared</h2>
<table class="cmp"><thead><tr><th>Option</th><th>Sync</th><th>One API for UI, CLI and agents?</th><th>Learning curve</th><th>Agent loop</th></tr></thead><tbody>
<tr><td>Electric v3</td><td>Compiler-split reactive program over WebSocket</td><td>No: the UI bypasses REST</td><td>High</td><td>Mixed; needs two runtimes</td></tr>
<tr><td>Fulcro + Pathom</td><td>Normalized client DB, EQL; push is DIY</td><td>Yes, if EQL becomes the API</td><td>High</td><td>Headless JVM mode, CLAUDE.md</td></tr>
<tr><td>re-frame</td><td>Events over app-db; push is DIY</td><td>Yes</td><td>Medium</td><td>re-frame-pair on the running app</td></tr>
<tr><td>UIx + own push</td><td>SSE invalidation and refetch</td><td>Yes, unchanged</td><td>Low (you know it)</td><td>Good: React is familiar, API is curl-able</td></tr>
<tr><td>Replicant + Nexus</td><td>Pure hiccup; push is DIY</td><td>Yes</td><td>Low–medium</td><td>Simple data; author anti-LLM</td></tr>
<tr><td>Datastar</td><td>Server renders, SSE morph</td><td>Yes, same server</td><td>Low</td><td>Best: curl and the REPL</td></tr>
<tr><td>Datahike</td><td>Store sync to the browser, offline</td><td>Needs a database change</td><td>High</td><td>Unknown</td></tr>
</tbody></table>
</div>
{table(CLJ_OPTS, 'Clojure front-end and sync projects', 'full')}'''
    out.append(('/approaches/frontend-sync/clojure/', 'The Clojure options', 'Electric v3, Fulcro, re-frame and re-frame2, UIx with push, Replicant, Datastar and Datahike, judged for a local ledger whose clients include agents.', clj))

    # ---------------- does cljs cost me
    cost = f'''{M('Does ClojureScript cost me?', 'If the backend is Clojure and agents write most of the code, is a ClojureScript front end a hit compared with TypeScript, Elm or Gleam?', 'does cljs cost me?')}
<div class="bluf"><p>A small hit, mostly fixable. Frontier agents write competent Clojure, and no benchmark shows otherwise. What ClojureScript lacks is the free feedback loop TypeScript's type checker gives an agent. Give the agent a live REPL, automatic paren repair, clj-kondo and malli instead. Switch to TypeScript only if you need React Server Components or Next.js, a large hiring pool, or heavy use of TSX-first UI kits.</p></div>
<div class="prose">
<h2>The evidence on agents</h2>
<ul>
<li><strong>Benchmarks are thin.</strong> The only verified Clojure score is old: StarCoder2-15B got 23.85% pass@1 on <a href="https://github.com/nuprl/MultiPL-E/pull/136">MultiPL-E Clojure</a> (added by Alex Miller, April 2024), level with Racket's 22.4. AutoCodeBench and the ACL 2026 functional-programming study leave Clojure out.</li>
<li><strong>Indirect evidence goes against "small language, bad agent".</strong> In <a href="https://arxiv.org/html/2508.09101">AutoCodeBench</a>, Claude Opus 4 scored 80.3 on Elixir and 68.9 on Racket against 47.2 on TypeScript. Each language has its own problem set, so this is not a controlled comparison.</li>
<li><strong>Clojure is the most token-efficient</strong> of 19 languages on Rosetta Code tasks, 2.6x better than C (<a href="https://martinalderson.com/posts/which-programming-languages-are-most-token-efficient/">Alderson, January 2026</a>). More of the program fits in the agent's context, and in yours.</li>
<li><strong>Practitioners report it works.</strong> Orestis Markou ran Opus 4.5 on a ClojureScript and React front end: "decent and simple Clojure code"; "Subjectively, I'm just less tired" (<a href="https://orestis.gr/clojure-and-ai-agents-an-experience-report/">January 2026</a>).</li>
<li><strong>Few people do this yet.</strong> In the <a href="https://state-of-clojurescript.com/">State of ClojureScript 2025</a> survey (191 responses), 49% said none of their code is AI-generated. Your usage is ahead of the community's evidence.</li>
</ul>
{stat('4.2%', 'The share of agent writes with unbalanced delimiters in clojure-mcp-light\'s sample log (35 of 829). Parinfer repaired all 35. Paren errors were the classic failure mode for agents writing Lisp; with a hook on every write they stop mattering.', 'The paren problem, measured')}
<h2>Where TypeScript really is ahead</h2>
<ul>
<li><strong>The type checker is a free loop.</strong> In a PLDI 2025 study, 94% of compile errors in LLM-written TypeScript were type errors, all caught by <code>tsc</code> before runtime (<a href="https://arxiv.org/abs/2504.09246">Mündler et al.</a>). In ClojureScript those mistakes surface at the REPL, in tests or at runtime, unless you add clj-kondo and malli.</li>
<li><strong>Volume.</strong> TypeScript became GitHub's most-used language in August 2025, with more than 2.6M monthly contributors (<a href="https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/">Octoverse</a>). React, shadcn and Tailwind examples are overwhelmingly TSX, so in ClojureScript an agent translates.</li>
<li><strong>React Server Components and Next.js</strong> have no production path in ClojureScript; there is only <a href="https://romanliutikov.com/blog/towards-react-server-components-in-clojure-part-1">exploratory UIx work</a>. ESM output is shadow-cljs's admitted weak spot.</li>
</ul>
<h2>Where ClojureScript is ahead, for you</h2>
<ul>
<li><strong>Shared <code>.cljc</code>.</strong> The same malli schemas, validation and domain functions run on the server and in the browser. ownpurse already scores a line with the same function on both sides. A TypeScript front end would duplicate or generate all of that.</li>
<li><strong>EDN and Transit end to end.</strong> Keywords, sets, dates and namespaced keys survive the wire with no mapping layer.</li>
<li><strong>Immutable by default</strong>, which in TypeScript takes discipline (readonly, Immer, Effect).</li>
<li><strong>The REPL as the agent's eyes.</strong> Through clojure-mcp an agent evaluates forms against the live page, rather than rerunning a build.</li>
<li><strong>One language to read.</strong> This is your stated reason, and it is a good one: you can only judge code you can read.</li>
</ul>
<h2>The functional alternatives</h2>
<ul>
<li><strong>{a('elm/compiler', 'Elm')}:</strong> arguably the best compiler loop for agents. Ports-only JS interop, nothing shared with Clojure. 0.19.2 shipped in July 2026 as the start of a road to 1.0.</li>
<li><strong>Gleam and {a('lustre-labs/lustre', 'Lustre')}:</strong> typed, immutable, active. "Gleam's compiler lets agents self-correct", though the same team ultimately chose Rust and TypeScript (<a href="https://curling.io/blog/21-reasons-ai-agents-love-gleam">Curling IO</a>).</li>
<li><strong>{a('rescript-lang/rescript', 'ReScript')}:</strong> sound types inside React and npm, a small community, and no agent reports found.</li>
<li><strong>TypeScript with {a('Effect-TS/effect', 'Effect')}:</strong> the biggest agent advantage and full React 19, but a large API surface and opt-in immutability.</li>
<li><strong>{a('squint-cljs/squint', 'Squint')} and {a('squint-cljs/cherry', 'Cherry')}:</strong> lighter ClojureScript dialects. Good for small widgets; not worth moving a UIx app to.</li>
</ul>
<p>Every alternative gives up code sharing with the Clojure backend.</p>
<h2>The setup that closes the gap</h2>
<ol>
<li><strong>REPL in the loop:</strong> {a('bhauman/clojure-mcp', 'clojure-mcp')} in its <code>:repl</code> profile gives Claude Code, Codex and Gemini <code>clojure_eval</code> against the shadow-cljs runtime.</li>
<li><strong>Paren repair on every write:</strong> the {a('bhauman/clojure-mcp-light', 'clojure-mcp-light')} hook.</li>
<li><strong>A static gate standing in for <code>tsc</code>:</strong> {a('clj-kondo/clj-kondo', 'clj-kondo')} with unresolved-symbol and arity errors treated as failures.</li>
<li><strong>Types where they count:</strong> {a('metosin/malli', 'malli')} schemas in <code>.cljc</code> for API payloads, app state and props, with dev instrumentation.</li>
<li><strong>Tests the agent runs:</strong> a shadow-cljs node-test build for logic, plus a Playwright smoke test.</li>
<li><strong>House rules in AGENTS.md:</strong> UIx <code>$</code> and <code>defui</code> examples, how npm components are required, and "Tailwind classes as complete string literals".</li>
<li><strong>Measure the bundle once</strong> with <code>shadow.cljs.build-report</code> instead of guessing what cljs.core costs.</li>
</ol>
{finding('Hedge, don\'t rewrite', '<p>If you later need a TypeScript-native widget, keep domain logic in <code>.cljc</code> and treat the TS part as a leaf component. That costs far less than moving the whole front end.</p>')}
</div>
{table(AGENT_TOOLS, 'Agent tooling for ClojureScript', 'full')}'''
    out.append(('/approaches/frontend-sync/cljs-cost/', 'Does ClojureScript cost me?', 'Whether a ClojureScript front end is a hit compared with TypeScript, Elm or Gleam when AI agents write most of the code: benchmarks, failure modes, costs and the setup that closes the gap.', cost))

    # ---------------- ownpurse
    op = f'''{M('For ownpurse', 'Three architectures for ownpurse\'s front end, with code, and a plan', 'for ownpurse')}
<div class="bluf"><p>Build the change feed first. It is about 30 lines of Clojure, it ends polling, and every later choice uses it. Then spend a day each building the trial balance in Datastar and in Electric. Choose by which code you would rather read in a year, and which version your agent could check by itself.</p></div>
<div class="prose">
<h2>What makes ownpurse unusual</h2>
<ul>
<li><strong>The server is local.</strong> Latency is about zero, and "offline" means the process isn't running. You don't need a client-side sync engine for its own sake.</li>
<li><strong>Every write already goes through one process.</strong> The admin, the CLI, the TUI and agents all use the same API, with XTDB in process. That write path is the change feed XTDB doesn't provide.</li>
<li><strong>The record is append-only and bitemporal.</strong> Every transaction has an id and a system time, which make natural sync cursors.</li>
<li><strong>Agents are first-class clients.</strong> Whatever pushes changes to the browser should push them to agents too, through something they can tail with curl.</li>
</ul>
<h2>Step 1, for every path: a change feed</h2>
<p>Publish what each transaction touched, right after it commits. This works with any UI and with any client that can read an event stream.</p>
{code(TX_HOOK, 'Server: one write path, one SSE endpoint (sketch)')}
<p>An agent or the TUI can now tail changes with <code>curl -N localhost:7070/api/changes</code>. To catch up after a reconnect, accept <code>?since=&lt;tx-id&gt;</code> and replay from XTDB using system time.</p>
<h2>Path A: keep UIx, replace setInterval</h2>
{code(UIX_HOOK, 'Browser: refetch only what a transaction touched (sketch)')}
<p>This is a few days of work across the admin. If hand-rolled invalidation gets messy, {a('TanStack/db', 'TanStack DB')}'s Query Collection or a DataScript client store can sit behind the same hook.</p>
<h2>Path B: Datastar, the view as a function of the database</h2>
{code(DATASTAR, 'Server: views are hiccup, pushed when the data changes (sketch)')}
<p>This is the most "Elm on the server" option: <code>view = f(state)</code>, with no client state to keep consistent. An agent checks a view by calling <code>(view rows)</code> at the REPL, or by curling the stream. The cost is a rewrite of 11,000 lines, and complex widgets such as an editable grid or the xyflow design graph would stay as islands of JavaScript or ClojureScript.</p>
<h2>Path C: Electric, no API at all for the UI</h2>
{code(ELECTRIC, 'Electric v3: client and server in one expression (sketch)')}
<p>This is the shortest code of the three, and the network is invisible. That cuts both ways for someone who wants to see what the code does. ownpurse as a personal or bootstrapped project qualifies for Electric's free license. The UI would reach XTDB directly while the CLI and agents use REST, so validation must live in shared functions both paths call.</p>
{caveat('<p>These are sketches to show the shape of each approach, not tested code. Check function names against the XTDB, http-kit, Datastar SDK and Electric versions you install. Electric v3 in particular is pre-release and changes.</p>', 'Sketches')}
<h2>The plan</h2>
<ol>
<li><strong>This week:</strong> the change feed and <code>use-live</code>. Delete the <code>setInterval</code> calls. Add <code>/api/changes</code> to the OpenAPI document so agents find it.</li>
<li><strong>Agent setup:</strong> clojure-mcp against shadow-cljs, the paren-repair hook, clj-kondo as a gate, malli on API payloads (see <a href="/approaches/frontend-sync/cljs-cost/">does cljs cost me?</a>).</li>
<li><strong>Spike B:</strong> the trial balance as a Datastar page served beside the admin, driven by the same feed.</li>
<li><strong>Spike C:</strong> the same screen in Electric, under the free license.</li>
<li><strong>Decide</strong> by three tests. Which code do you understand on first read? Which one could your agent change and verify alone? Which one keeps one write path for every client?</li>
</ol>
{finding('If you only do one thing', '<p>Do step 1. It\'s the part of every option that pays off immediately, and it keeps the decision about the UI open.</p>')}
</div>'''
    out.append(('/approaches/frontend-sync/ownpurse/', 'For ownpurse', 'Three front-end architectures for ownpurse, a local Clojure/XTDB ledger, with code sketches: a change feed, UIx with push, Datastar and Electric.', op))
    return out

def posts(R, BL, d):
    a = lambda n, l=None: _a(R, n, l)
    v = lambda n, k='s': f'{R[n.lower()][k]:,}'
    P = []
    P.append(dict(slug='xtdb-has-no-change-feed', kj='Every sync engine wants a change feed, and XTDB doesn\'t have one', conf=HIGH, tags=['sync'],
      title='Every sync engine wants a change feed. XTDB doesn\'t have one.',
      dek='Zero, ElectricSQL and PowerSync all read a database replication stream. XTDB v2 has none, so for a Clojure/XTDB app the write path becomes the feed.',
      bluf='Don\'t look for a sync engine to put in front of XTDB. Publish your own "this transaction touched these tables" event from the one place every write goes through, and let any client (a browser, a TUI or an agent) subscribe to it.',
      body=f'''<p>The best-known sync engines share a requirement that is easy to miss on their landing pages. Zero "requires Postgres v15.0 or higher, and support for logical replication" (<a href="https://zero.rocicorp.dev/docs/connecting-to-postgres">docs</a>). ElectricSQL is a Postgres sync engine. PowerSync reads Postgres, MongoDB, MySQL, SQL Server or Convex. All of them follow the database's own change stream.</p>
{stat('#2454', 'The XTDB issue "Users can subscribe to a stream of XTDB\'s completed transactions for CDC". It is still open. XTDB v2.2 (October 2026) added inbound sources (Postgres, Kafka), but no outbound feed. v1\'s <code>xt/listen</code> has no v2 equivalent.', 'The gap')}
<p>XTDB speaks the Postgres wire protocol, so it can look like a fit. It isn't: wire compatibility covers queries, not logical replication.</p>
<h2>The fix is already in your architecture</h2>
<p>An app like ownpurse runs XTDB in process, and every write goes through its own API. That is a better place to hook than a replication stream, because at that point you still know <em>why</em> the write happened, not just which rows changed. After <code>execute-tx</code>, publish <code>{{:tx-id … :tables …}}</code> on a server-sent events endpoint. The transaction id and system time are natural cursors for catching up after a reconnect.</p>
{signal('<p>Instant does the same thing one step later: its Clojure sync engine tails the Postgres WAL, maps entries to topics and invalidates subscribed queries (<a href="https://www.instantdb.com/essays/architecture">architecture essay</a>). Read it before building your own.</p>', 'Prior art in Clojure')}
<p>The one exception is a process that writes to XTDB storage directly and skips the API. Its writes won't be seen, which is a good reason to keep one write path anyway.</p>'''))
    P.append(dict(slug='sync-engines-consolidate', kj='The sync market is consolidating: bet on protocols, not vendors', conf=HIGH, tags=['sync'],
      title='The sync engine market is consolidating',
      dek='Electric joined Databricks, Supabase bought Triplit and Y-Sweet\'s team joined Modal, while Zero and Instant both reached 1.0.',
      bluf='Two years ago "sync engine" meant a dozen startups. In 2026 the field is merging into larger platforms. Choose things you could run or reimplement yourself: an open protocol or a small backend contract, not a hosted service.',
      body=f'''<ul>
<li><strong>ElectricSQL</strong> joined Neon at Databricks in August 2026. "Everything we've open sourced stays open source", but Electric Cloud is winding down, and PowerSync published a <a href="https://docs.powersync.com/migration-guides/electric">migration guide</a> (<a href="https://electric.ax/blog/2026/08/11/electric-joining-databricks">Electric</a>).</li>
<li><strong>Triplit</strong> was acquired by Supabase (<a href="https://supabase.com/blog/triplit-joins-supabase">Supabase</a>). Its repo has been quiet since January 2026.</li>
<li><strong>Jamsocket</strong>, maker of Y-Sweet, joined Modal (<a href="https://modal.com/blog/jamsocket-is-joining-modal">Modal</a>).</li>
<li><strong>Replicache</strong> was open-sourced and made free, then superseded by <strong>Zero</strong>, which reached 1.0 in June 2026 after "more than 50 releases" (<a href="https://www.infoq.com/news/2026/06/zero-version-1/">InfoQ</a>).</li>
<li><strong>Instant</strong> reached 1.0 in April 2026.</li>
</ul>
{finding('What survives a consolidation', '<p>Protocols and small contracts. Durable Streams is an open HTTP protocol. RxDB\'s replication, Replicache\'s push and pull, and LiveStore\'s ordered event log are each a few endpoints you could serve from any backend. If a vendor disappears, your server still speaks the protocol.</p>')}
<p>The community has split too. Local-First Conf keeps the data-ownership ideals, while SyncConf is about sync for SaaS, with the tagline "realtime collaboration between humans and agents".</p>''',
      after=table(['rocicorp/mono', 'electric-sql/electric', 'aspen-cloud/triplit', 'jamsocket/y-sweet', 'instantdb/instant', 'TanStack/db', 'powersync-ja/powersync-service', 'livestorejs/livestore'], 'The engines in this story', 'full')))
    P.append(dict(slug='the-clojurescript-tax', kj='The ClojureScript tax is small, and it is the missing type checker, not the language', conf=MOD, tags=['agents', 'frontend'],
      title='The ClojureScript tax is the type checker, not the language',
      dek='No benchmark shows agents writing worse Clojure than TypeScript. What they lose is tsc. A REPL, paren repair, clj-kondo and malli give most of it back.',
      bluf='If your backend is Clojure and you read Clojure, writing the front end in ClojureScript costs little with agents, provided you build the feedback loop TypeScript gets for free. Switch only for React Server Components, a large hiring pool or TSX-first UI kits.',
      body=f'''<p>The usual worry is that agents have seen far less ClojureScript than TypeScript, so they will write it badly. The evidence doesn't bear that out. The only verified Clojure benchmark score (MultiPL-E, a small 2024 model) matches Racket. In AutoCodeBench, Claude Opus 4 scored higher on Elixir and Racket than on TypeScript, though each language had its own problem set. Practitioners using frontier models in 2026 report "decent and simple Clojure code".</p>
{stat('94%', 'The share of compile errors in LLM-written TypeScript that were type errors (PLDI 2025). Every one of them was caught by <code>tsc</code> before the code ran. That is the real advantage: not better generation, but a free check after it.', 'What TypeScript gives an agent')}
<p>In ClojureScript, the same kind of mistake surfaces at the REPL, in a test or at runtime. So give the agent equivalents:</p>
<ul><li>a live REPL through {a('bhauman/clojure-mcp', 'clojure-mcp')}</li><li>parinfer on every write through {a('bhauman/clojure-mcp-light', 'clojure-mcp-light')} (it fixed all 35 delimiter errors in 829 writes)</li><li>{a('clj-kondo/clj-kondo', 'clj-kondo')} as a gate</li><li>{a('metosin/malli', 'malli')} schemas on payloads and state</li></ul>
<p>What you keep in return is specific to a Clojure backend: shared <code>.cljc</code> validation and domain code, EDN end to end, immutability by default, and one language you can actually read.</p>
{caveat('<p>The evidence is thin in both directions. There is no frontier-model Clojure benchmark, and only 191 people answered the State of ClojureScript 2025 survey, half of whom use no AI-generated code. This judgment rests on indirect data and practitioner reports.</p>')}'''))
    P.append(dict(slug='server-driven-ui-and-agents', kj='Server-driven UI gives agents the shortest feedback loop', conf=MOD, tags=['frontend', 'agents'],
      title='Server-driven UI gives agents the shortest feedback loop',
      dek='When the UI is a function on the server, an agent checks its work with curl or one REPL call. Datastar hit 1.0 and Biff 2.0 adopted it.',
      bluf='Agents do best when they can check their own work. A server-rendered UI collapses the check to one runtime: call the view function at the REPL, or curl the page. That is why Datastar is the Clojure option with the strongest agent story, even though it isn\'t a sync engine at all.',
      body=f'''{intercept('LLM agents … need validation feedback. It is complex for the LLM to gather feedback with Electric. You have 2 environments (JS and JVM). With Datastar it is dead simple for the LLM to validate, basically just curl.', 'Hendrik, <a href="https://clojurians-log.clojureverse.org/hyperfiddle/2026-03-04">#hyperfiddle</a>, March 2026')}
<p>{a('starfederation/datastar', 'Datastar')} reached 1.0 in April 2026 and is at 1.0.5. The server streams DOM patches and small reactive signals over server-sent events, and the {a('starfederation/datastar-clojure', 'Clojure SDK')} is maintained alongside it. <a href="https://biffweb.com/p/biff2-released/">Biff 2.0</a>, the best-known batteries-included Clojure web framework, switched from htmx to Datastar in September 2026.</p>
<p>Anders Murphy's {a('andersmurphy/hyperlith', 'hyperlith')} shows the simplest version: one render function per page, re-rendered whenever the database changes, with the whole <code>&lt;main&gt;</code> pushed and morphed. There is no diffing and no missed-event logic. It looks wasteful until you remember compression and a local server.</p>
{finding('The trade', '<p>Datastar is the most Elm-like way to write a Clojure web UI (<code>view = f(state)</code>), with almost no ClojureScript. It is weakest at rich client interaction: editable grids, drag and drop, keyboard-heavy editing. Those stay as islands of client code.</p>')}''',
      after=table(['starfederation/datastar', 'starfederation/datastar-clojure', 'andersmurphy/hyperlith', 'jacobobryant/biff', 'brianium/datastar.wow', 'bigskysoftware/htmx', 'phoenixframework/phoenix_live_view'], 'Server-driven UI', 'full')))
    P.append(dict(slug='electric-in-2026', kj='Electric is still the boldest idea, and still not the safe bet', conf=MOD, tags=['novel', 'frontend'],
      title='Electric in 2026: still the boldest idea, still not the safe bet',
      dek='Private beta, a commercial license with a generous free tier, honest warnings from its own makers, and mixed reports from people using agents with it.',
      bluf='Electric v3 is the purest answer to "why is there an API between my UI and my database at all?" It is also beta, licensed per developer for businesses, unsuited to offline use, and its authors say to use something else if you can. Spike it on one screen; don\'t bet a production admin on it.',
      body=f'''<p>One <code>e/defn</code> holds client and server code together, and the compiler splits it into reactive halves joined by a WebSocket. Server queries rerun when their inputs change and stream diffs to the client. For someone who likes functional, reactive code it is beautiful, and it runs on the same JVM as XTDB.</p>
<h2>What 2026 looks like</h2>
<ul>
<li><strong>Status:</strong> <code>v3-alpha-SNAPSHOT</code>, "private beta with commercial users". The public repo's last commit was March 2026; work happens in a monorepo, and the {a('hyperfiddle/electric3-starter-app', 'starter app')} moved in October.</li>
<li><strong>License:</strong> free for non-commercial use and for bootstrappers under $200k revenue or $500k funding. Otherwise $480 per developer per month (33% off for startups), with a development-time login and no check in production.</li>
<li><strong>Known issues, in the team's own list:</strong> glitches, front-end performance, slow small collections without virtual scroll, and "we haven't yet figured out how to test Electric UIs" (a user, March 2026).</li>
<li><strong>Direction:</strong> Hyperfiddle is building a low-code platform with an "agentic coding" layer. Growing Electric adoption "is not a priority for us this year".</li>
</ul>
{intercept('working on electric with claude code/codex is quite painful… it struggles to understand, especially at the front/back interop', 'A user porting a tool, <a href="https://clojurians-log.clojureverse.org/hyperfiddle/2026-03-07">#hyperfiddle</a>, March 2026. Others in the channel described a Claude, Electric and Rama workflow as "almost unbelievable".')}
{caveat('<p>Agent reports on Electric are anecdotal and split. The structural problem is real: there is no data-only surface for an agent to curl, and checking a change means running both the JVM and the browser.</p>')}''',
      after=table(['hyperfiddle/electric', 'hyperfiddle/electric3-starter-app', 'hyperfiddle/electric-fiddle', 'leonoel/missionary'], 'Electric and its foundations', 'full')))
    P.append(dict(slug='fulcro-headless', kj='Fulcro\'s headless mode is the most agent-ready idea in Clojure front ends', conf=LOW, tags=['frontend', 'agents'],
      title='Fulcro\'s headless mode is the most agent-ready idea in Clojure front ends',
      dek='A whole Fulcro app, real remotes included, running synchronously on the JVM with click-on! and type-into!. It is the browser-free check loop agents need, at the cost of Fulcro\'s ceremony.',
      bluf='The hard part of agents writing UI is verification, because the agent can\'t see the page. Fulcro now lets an agent drive the whole app from a JVM REPL. That is a better answer than any other Clojure UI library has. Whether it outweighs idents, queries and resolvers for every feature depends on whether you want EQL as your public API anyway.',
      body=f'''<p>Since December 2025, <code>com.fulcrologic.fulcro.headless</code> runs a full {a('fulcrologic/fulcro', 'Fulcro')} application synchronously on the JVM. It renders hiccup, supports <code>click-on!</code> and <code>type-into!</code>, and loopback remotes go through your real Ring and Pathom stack (<a href="https://github.com/fulcrologic/fulcro/blob/main/fulcro-in-clj.md">fulcro-in-clj.md</a>). The repo ships a <code>CLAUDE.md</code>, and Fulcro RAD publishes documentation written as LLM context.</p>
{intercept('in 2025 the LLMs really crossed a line … I\'m developing three or four times more stuff than I was.', 'Tony Kay, <a href="https://podscan.fm/podcasts/clojurestream-podcast/episodes/e103-llm-experience-report-with-tony-kay">ClojureStream E103</a>, April 2026')}
<p>Fulcro is active (3.10.1 in October 2026, React 19.1), and its author writes stubs with docstrings and has models fill them in and write the tests. The counterweight is indirection. Following one feature means reading the ident, query, initial state, mutation, remote and resolver. An agent that gets an ident slightly wrong gets silently missing data rather than an error.</p>
{caveat('<p>Low confidence: the evidence is the feature itself, the author\'s report and a few Clojurians threads. We found no independent account of agents building a Fulcro app from scratch with headless mode.</p>')}
<p>re-frame has a different answer to the same problem: {a('day8/re-frame-pair', 're-frame-pair')}, a Claude Code skill that inspects and drives the <em>running</em> browser app.</p>''',
      after=table(['fulcrologic/fulcro', 'fulcrologic/fulcro-rad', 'wilkerlucio/pathom3', 'fulcrologic/statecharts', 'day8/re-frame', 'day8/re-frame-pair', 'day8/re-frame2'], 'Fulcro and re-frame', 'full')))
    return P

def sources():
    S = lambda date, title, who, url, type, k, sum: dict(date=date, title=title, who=who, url=url, type=type, k=k, sum=sum)
    return [
     S('2026-06', 'Zero 1.0 released', 'InfoQ', 'https://www.infoq.com/news/2026/06/zero-version-1/', 'article', ['sync'], 'Rocicorp\'s Zero reaches 1.0 after nearly two years and 50+ releases.'),
     S('2026', 'Zero: connecting to Postgres', 'Rocicorp', 'https://zero.rocicorp.dev/docs/connecting-to-postgres', 'doc', ['sync'], 'Requires Postgres 15+ with logical replication.'),
     S('2026', 'Replicache', 'Rocicorp', 'https://replicache.dev/', 'doc', ['sync'], 'Open-sourced and free; push/pull against any backend.'),
     S('2025-02', 'Zero sync engine review', 'Marmelab', 'https://marmelab.com/blog/2025/02/28/zero-sync-engine.html', 'article', ['sync'], 'Independent hands-on review of Zero.'),
     S('2025-03', 'ElectricSQL 1.0 released', 'Electric', 'https://electric.ax/blog/2025/03/17/electricsql-1.0-released', 'article', ['sync'], 'Postgres read-path sync over HTTP reaches 1.0.'),
     S('2026-08', 'Electric joins Databricks', 'Electric', 'https://electric.ax/blog/2026/08/11/electric-joining-databricks', 'article', ['sync'], 'Electric joins Neon at Databricks; open source stays open, Electric Cloud winds down.'),
     S('2026', 'Migrating from Electric', 'PowerSync', 'https://docs.powersync.com/migration-guides/electric', 'doc', ['sync'], 'PowerSync\'s migration guide for Electric Cloud users.'),
     S('2025-12', 'Durable Streams 0.1.0', 'Electric', 'https://electric.ax/blog/2025/12/23/durable-streams-0.1.0', 'article', ['sync'], 'An open protocol for ordered, replayable HTTP streams with catch-up and live tailing.'),
     S('2026', 'TanStack DB 0.5: query-driven sync', 'TanStack', 'https://tanstack.com/blog/tanstack-db-0.5-query-driven-sync', 'article', ['sync'], 'Query Collection works against any REST, GraphQL or tRPC backend; live queries via differential dataflow.'),
     S('2026', 'How LiveStore works', 'LiveStore', 'https://docs.livestore.dev/overview/how-livestore-works/', 'doc', ['sync'], 'Event-sourced client SQLite; the sync backend serves an ordered event log from a cursor.'),
     S('2026', 'RxDB HTTP replication', 'RxDB', 'https://rxdb.info/replication-http.html', 'doc', ['sync'], 'Checkpoint pull/push protocol any backend can implement.'),
     S('2026', 'Instant architecture', 'InstantDB', 'https://www.instantdb.com/essays/architecture', 'article', ['sync'], 'A Clojure sync engine that tails the Postgres WAL and invalidates subscribed queries.'),
     S('2025', 'Convex goes open source', 'Convex', 'https://news.convex.dev/convex-goes-open-source/', 'article', ['sync'], 'Self-hostable reactive backend under FSL-1.1-Apache-2.0.'),
     S('2026', 'PowerSync source database setup', 'PowerSync', 'https://docs.powersync.com/configuration/source-db/setup', 'doc', ['sync'], 'Supported sources: Postgres, MongoDB, MySQL, SQL Server, Convex.'),
     S('2025', 'Triplit joins Supabase', 'Supabase', 'https://supabase.com/blog/triplit-joins-supabase', 'article', ['sync'], 'Supabase acquires the Triplit syncing database.'),
     S('2025', 'Jamsocket is joining Modal', 'Modal', 'https://modal.com/blog/jamsocket-is-joining-modal', 'article', ['sync'], 'The Y-Sweet team joins Modal.'),
     S('2025-07', 'Automerge 3', 'Automerge', 'https://automerge.org/blog/automerge-3/', 'article', ['sync'], 'Memory use cut by more than 10x.'),
     S('2026', 'Keyhive notebook', 'Ink & Switch', 'https://www.inkandswitch.com/keyhive/notebook/', 'paper', ['sync'], 'Local-first access control: group key agreement and capabilities that travel with the data.'),
     S('2026', 'Evolu', 'Evolu', 'https://www.evolu.dev/', 'tool', ['sync'], 'SQLite on each device, end-to-end-encrypted sync through self-hostable relays.'),
     S('2026', 'Datastar', 'Star Federation', 'https://data-star.dev/', 'tool', ['frontend', 'sync'], 'Hypermedia framework streaming DOM patches and signals over SSE; any backend.'),
     S('2026-09', 'Biff 2.0 released', 'Jacob O\'Bryant', 'https://biffweb.com/p/biff2-released/', 'article', ['frontend'], 'Biff switches from htmx to Datastar by default.'),
     S('2024', 'Phoenix LiveView 1.0 released', 'Phoenix', 'https://www.phoenixframework.org/blog/phoenix-liveview-1.0-released', 'article', ['frontend'], 'LiveView 1.0, six years after the first commit; the reference server-driven design.'),
     S('2026', 'Lustre server components', 'Lustre', 'https://hexdocs.pm/lustre/lustre/server_component.html', 'doc', ['frontend'], 'Elm-architecture UI on the server with a 10kb client runtime.'),
     S('2022', 'LiveGraph: real-time data at scale', 'Figma', 'https://www.figma.com/blog/livegraph-real-time-data-at-scale/', 'article', ['sync'], 'Figma tails the Postgres replication stream to drive subscriptions.'),
     S('2025', 'Reverse-engineering Linear\'s sync engine', 'wzhudev', 'https://github.com/wzhudev/reverse-linear-sync-engine', 'article', ['sync'], 'The clearest write-up of server authority plus client rebase, endorsed by Linear\'s CTO.'),
     S('2026', 'XTDB issue #2454: subscribe to completed transactions (CDC)', 'XTDB', 'https://github.com/xtdb/xtdb/issues/2454', 'doc', ['sync'], 'Open request for an outbound change feed in XTDB.'),
     S('2026', 'Electric', 'Hyperfiddle', 'https://github.com/hyperfiddle/electric', 'tool', ['frontend', 'sync'], 'Full-stack differential dataflow for UI; v3 license terms in the README.'),
     S('2024-10', 'Electric v3 license change', 'Dustin Getz', 'https://tana.pub/lQwRvGRaQ7hM/electric-v3-license-change', 'article', ['frontend'], 'Source-available business license: free for non-commercial use and bootstrappers, otherwise per-developer pricing.'),
     S('2025-07', 'Hyperfiddle mission, position and business', 'Hyperfiddle', 'https://docs.google.com/document/d/1TgExchcIyWd4BH9qwb4vjp7uaBjWyBtPWEkGqSfvlTk/', 'doc', ['frontend'], 'Status, pricing, known issues and positioning: "Electric is for experts".'),
     S('2026-03', '#hyperfiddle: agents and Electric', 'Clojurians', 'https://clojurians-log.clojureverse.org/hyperfiddle/2026-03-07', 'forum', ['frontend', 'agents'], 'A user finds Claude Code and Codex "quite painful" on Electric\'s front/back interop.'),
     S('2026-03', '#hyperfiddle: validation feedback for agents', 'Clojurians', 'https://clojurians-log.clojureverse.org/hyperfiddle/2026-03-04', 'forum', ['frontend', 'agents'], 'Two runtimes make Electric hard for agents to check; Datastar is "basically just curl".'),
     S('2026-02', '#hyperfiddle: Claude + Electric + Rama', 'Clojurians', 'https://clojurians-log.clojureverse.org/hyperfiddle/2026-02-15', 'forum', ['frontend', 'agents'], 'Positive reports of agent workflows with Electric.'),
     S('2025', 'Electric Clojure: Differential Dataflow for UI', 'Dustin Getz, reClojure 2025', 'https://www.youtube.com/watch?v=ML8cFrWkWeg', 'talk', ['frontend'], 'Getz on Electric v3\'s model.'),
     S('2026', 'Fulcro in CLJ (headless mode)', 'Fulcrologic', 'https://github.com/fulcrologic/fulcro/blob/main/fulcro-in-clj.md', 'doc', ['frontend', 'agents'], 'Run a full Fulcro app on the JVM with click-on!, type-into! and real remotes.'),
     S('2026-04', 'E103: LLM experience report with Tony Kay', 'ClojureStream', 'https://podscan.fm/podcasts/clojurestream-podcast/episodes/e103-llm-experience-report-with-tony-kay', 'talk', ['agents'], 'Fulcro\'s author on being three to four times more productive with LLMs.'),
     S('2026', 'Fulcro RAD AI documentation', 'Fulcrologic', 'https://cljdoc.org/d/com.fulcrologic/fulcro-rad/1.6.24/doc/ai-documentation-generation-summary', 'doc', ['agents'], 'RAD reference docs written as LLM context.'),
     S('2026', 're-frame-pair', 'Day8', 'https://github.com/day8/re-frame-pair', 'tool', ['frontend', 'agents'], 'Claude Code skill that inspects and drives a running re-frame app.'),
     S('2026', 're-frame2', 'Day8', 'https://github.com/day8/re-frame2', 'tool', ['frontend', 'agents'], 'Spec-first, AI-first successor to re-frame; pre-alpha.'),
     S('2026', 'Datahike distributed and browser sync', 'replikativ', 'https://github.com/replikativ/datahike/blob/main/doc/distributed.md', 'doc', ['sync'], 'IndexedDB browser store and a streaming writer for offline-capable apps (beta).'),
     S('2026-04', 'Lo-fi ClojureScript: local-first apps with c3kit Bucket', 'Clean Coders', 'https://cleancoders.com/blog/2026-04-07-lo-fi-clojurescript-making-local-first-applications-with-c3kit-bucket', 'article', ['sync'], 'A small local-first IndexedDB sync approach in ClojureScript.'),
     S('2024-04', 'MultiPL-E: add Clojure', 'Alex Miller', 'https://github.com/nuprl/MultiPL-E/pull/136', 'paper', ['agents'], 'Clojure added to MultiPL-E; StarCoder2-15B scores 23.85 pass@1, level with Racket.'),
     S('2025-08', 'AutoCodeBench', 'Tencent (ICLR 2026)', 'https://arxiv.org/abs/2508.09101', 'paper', ['agents'], '3,920 problems in 20 languages; Opus 4 scores Elixir 80.3, Racket 68.9, TypeScript 47.2 (separate problem sets).'),
     S('2025', 'Type-constrained code generation', 'Mündler et al., PLDI 2025', 'https://arxiv.org/abs/2504.09246', 'paper', ['agents'], '94% of compile errors in LLM-written TypeScript are type errors.'),
     S('2026-01', 'Which programming languages are most token-efficient?', 'Martin Alderson', 'https://martinalderson.com/posts/which-programming-languages-are-most-token-efficient/', 'article', ['agents'], 'Clojure is the most token-efficient of 19 languages on Rosetta Code.'),
     S('2026-01', 'Clojure and AI agents: an experience report', 'Orestis Markou', 'https://orestis.gr/clojure-and-ai-agents-an-experience-report/', 'article', ['agents', 'frontend'], 'Opus 4.5 on a ClojureScript/React front end: decent code, occasional paren loops.'),
     S('2026', 'clojure-mcp-light', 'Bruce Hauman', 'https://github.com/bhauman/clojure-mcp-light', 'tool', ['agents'], 'Paren-repair hooks; 35 of 829 writes had delimiter errors, all fixed by parinfer.'),
     S('2026-06', 'Teaching Claude clean, secure Clojure', 'Clean Coders', 'https://cleancoders.com/blog/2026-06-22-teaching-claude-clean-secure-clojure', 'article', ['agents'], 'Claude\'s Clojure works; the post teaches it idiom and security practice.'),
     S('2026', 'State of ClojureScript 2025', 'State of ClojureScript', 'https://state-of-clojurescript.com/', 'doc', ['ecosystem', 'frontend'], '191 responses: 49% use no AI-generated code; debugging and build tooling are the top pain points.'),
     S('2025-10', 'Octoverse: TypeScript becomes the most-used language', 'GitHub', 'https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/', 'article', ['agents'], 'TypeScript overtook Python and JavaScript in August 2025, with 2.6M+ monthly contributors.'),
     S('2025-05', 'Towards React Server Components in Clojure', 'Roman Liutikov', 'https://romanliutikov.com/blog/towards-react-server-components-in-clojure-part-1', 'article', ['frontend'], 'Exploratory RSC work for UIx; no production path yet.'),
     S('2026', 'shadow-cljs and ESM', 'Thomas Heller', 'https://github.com/thheller/shadow-cljs/blob/master/doc/esm.md', 'doc', ['frontend'], 'ESM output is the weak spot: each package bundles its own cljs.core.'),
     S('2026-03', 'Is Elm a great language for AI to code in?', 'Elm Discourse', 'https://discourse.elm-lang.org/t/is-elm-a-great-language-for-ai-to-code-in/10575', 'forum', ['agents', 'frontend'], 'Precise compiler errors help agents; scarce training data and invented functions hurt.'),
     S('2026-03', '21 reasons AI agents love Gleam', 'Curling IO', 'https://curling.io/blog/21-reasons-ai-agents-love-gleam', 'article', ['agents', 'frontend'], 'Gleam\'s compiler lets agents self-correct; the team still chose Rust and TypeScript.'),
     S('2025-12', 'ReScript 12 released', 'ReScript', 'https://rescript-lang.org/blog/release-12-0-0/', 'article', ['frontend'], 'Rewritten build system for the typed, React-first functional language.'),
    ]
