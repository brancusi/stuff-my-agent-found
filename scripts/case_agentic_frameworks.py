"""Case 003: frameworks that work well when agents write the code. Research filed 2026-11-10."""
from content import _a, finding, caveat, signal, intercept, stat, table, HIGH, MOD, LOW

REF = 'SMAF-003'
def conf_chip(c): return f'<span class="conf {c[0]}">{c[1]}</span>'

FRAMEWORKS = ['phoenixframework/phoenix', 'rails/rails', 'laravel/framework', 'vercel/next.js', 'sveltejs/kit', 'convex/convex-backend', 'supabase/supabase',
              'instantdb/instant', 'shadcn-ui/ui', 'TanStack/router', 'starfederation/datastar', 'bigskysoftware/htmx', 'golang/go', 'django/django',
              'Effect-TS/effect', 'gleam-lang/gleam', 'wasp-lang/wasp', 'encoredev/encore', 'trpc/trpc', 'honojs/hono', 'elysiajs/elysia', 'redwoodjs/sdk']
TOOLING = ['tidewave-ai/tidewave_phoenix', 'tidewave-ai/tidewave_rails', 'tidewave-ai/tidewave_js', 'ash-project/usage_rules', 'laravel/boost',
           'vercel/next-devtools-mcp', 'vercel-labs/agent-browser', 'sveltejs/ai-tools', 'supabase/mcp', 'vintasoftware/django-ai-boost', 'tim-smart/effect-mcp',
           'bhauman/clojure-mcp', 'bhauman/clojure-mcp-light', 'day8/re-frame-pair', 'AnswerDotAI/llms-txt']
BENCH = ['Tencent-Hunyuan/AutoCodeBenchmark', 'multi-swe-bench/multi-swe-bench', 'vercel/next-evals-oss', 'rails/ai-evals', 'convex/fullstack-bench', 'convex/convex-evals']

def pages(memo, R, d):
    a = lambda n, l=None: _a(R, n, l)
    M = lambda title, subj, eb: memo(title, subj, 'Open', eyebrow=f'Case 003 // {eb}', ref=REF)
    out = []
    brief = f'''{M('Frameworks that work well when agents write the code', 'Which app frameworks are people finding work best with coding agents, and what is the evidence?', 'brief')}
<div class="bluf"><p><strong>No one has measured which framework is best for agents.</strong> The only head-to-head comparisons are run by vendors. What has been measured is the <em>mechanisms</em>: passive, version-pinned docs (Vercel: 53% to 100% on new Next.js APIs), type and compiler feedback (Convex, Svelte), a small surface area (fewer tokens), and live access to the running app. In 2025–26 every major framework shipped that last one. Pick a framework that gives the agent all four, or add them yourself.</p></div>
<div class="prose">
<h2>Key judgments</h2>
<ol class="kj">
<li><div><h3>Every major framework now lets the agent see the running app</h3><p>Tidewave (Phoenix and Rails), Laravel Boost, Next.js 16's built-in <code>/_next/mcp</code>, Supabase's MCP server, the Svelte MCP and clojure-mcp all shipped in 2025–2026. Each team built it separately, and it is the clearest trend in this field. {conf_chip(HIGH)} <a class="more" href="/blog/agents-see-the-running-app/">dispatch →</a></p></div></li>
<li><div><h3>Docs the agent always sees beat docs it has to ask for</h3><p>Vercel measured it on Next.js 16 APIs: no docs 53%, a skill 53% (it wasn't invoked in 56% of runs), a compressed docs index in AGENTS.md 100%. {conf_chip(HIGH)} <a class="more" href="/blog/agents-md-beats-skills/">dispatch →</a></p></div></li>
<li><div><h3>"Agents love framework X" is mostly anecdote</h3><p>The cross-framework numbers come from vendors (Convex, Wasp, Encore). The independent ones test languages (AutoCodeBench: Elixir first, PHP last) or context strategies, not frameworks. {conf_chip(MOD)} <a class="more" href="/blog/no-framework-benchmark/">dispatch →</a></p></div></li>
<li><div><h3>Smaller frameworks cost agents fewer tokens</h3><p>In an independent test of 19 frameworks, minimal ones took 26–29k tokens for the same app and full-featured ones up to 74k. Phoenix was the most expensive, despite Elixir's benchmark lead. {conf_chip(LOW)} <a class="more" href="/blog/small-surface-area/">dispatch →</a></p></div></li>
</ol>
<h2>At a glance</h2>
<table class="cmp"><thead><tr><th>Framework</th><th>Why agents do well (claimed)</th><th>Agent tooling</th><th>Evidence</th></tr></thead><tbody>
<tr><td>Phoenix / Elixir</td><td>Immutability, explicit data flow, stable language, introspection</td><td>Tidewave, generated AGENTS.md, usage_rules</td><td><span class="conf mod">MOD</span> language-level benchmark</td></tr>
<tr><td>Next.js</td><td>Most training data; Vercel invests in evals</td><td><code>/_next/mcp</code>, docs in node_modules, evals</td><td><span class="conf high">HIGH</span> for tooling, not for the framework</td></tr>
<tr><td>Laravel</td><td>PHP training data plus version-pinned context</td><td>Laravel Boost (15+ tools)</td><td><span class="conf mod">MOD</span> tooling, no outcome data</td></tr>
<tr><td>SvelteKit</td><td>Small; cheap in tokens</td><td>Svelte MCP with an autofixer for the loop</td><td><span class="conf mod">MOD</span></td></tr>
<tr><td>Convex</td><td>Plain TypeScript end to end, typed, reactive</td><td>MCP, rules files, model leaderboard</td><td><span class="conf mod">MOD</span> vendor benchmark</td></tr>
<tr><td>Rails 8</td><td>Conventions as a map; concise</td><td>Tidewave, official model evals</td><td><span class="conf low">LOW–MOD</span></td></tr>
<tr><td>shadcn/ui + Tailwind</td><td>Component source in your repo</td><td>Official MCP and registry</td><td><span class="conf mod">MOD</span> by adoption</td></tr>
<tr><td>Go</td><td>Explicit, little magic, fast tests</td><td>gopls</td><td><span class="conf mod">MOD</span> argued; low benchmark score</td></tr>
<tr><td>Hypermedia (htmx, Datastar)</td><td>Less client state to get wrong</td><td>Little official</td><td><span class="conf low">LOW</span> mixed reports</td></tr>
<tr><td>Clojure</td><td>REPL checks against the running program</td><td>clojure-mcp <code>:repl</code>, paren repair</td><td><span class="conf low">LOW</span> no benchmark includes it</td></tr>
</tbody></table>
{finding('What this means for a Clojure developer', '<p>Clojure already has the mechanism the field is converging on: the agent evaluating code against the running program, which is what Tidewave, Boost and <code>/_next/mcp</code> add to their frameworks. What it lacks is the rest of the kit those frameworks ship: a type checker (use clj-kondo and malli), an official AGENTS.md (write your own, compact and always loaded), and benchmarks. See <a href="/approaches/frontend-sync/cljs-cost/">case 002</a> for the setup.</p>')}
<h2>In this case file</h2>
<ul><li><a href="/practices/agentic-frameworks/frameworks/">Framework by framework</a>: the claims, the evidence, the tooling and the counterpoints.</li>
<li><a href="/practices/agentic-frameworks/patterns/">Patterns</a>: what makes a framework agent-friendly, and how much of it is measured.</li></ul>
</div>
{table(FRAMEWORKS, 'Frameworks and platforms in this case', 'full')}'''
    out.append(('/practices/agentic-frameworks/', 'Case 003: frameworks agents work well in', 'Which app frameworks work best when coding agents write the code: Rails, Phoenix and Tidewave, Laravel Boost, Next.js, SvelteKit, Convex and more, with the evidence and the patterns.', brief))

    fw = f'''{M('Framework by framework', 'The claims, the evidence, the agent tooling and the counterpoints for each framework', 'frameworks')}
<div class="bluf"><p>Every framework here has a story about why agents do well with it. Few of those stories are measured. Read the claims for which mechanism they describe (types, conventions, small surface, live introspection, pinned docs). That part transfers between frameworks; the "agents love us" part usually doesn't.</p></div>
<div class="prose">
<h2>Phoenix, Elixir and LiveView</h2>
{intercept('Elixir had the highest completion rate across models when compared among 20 different programming languages … What goes in and out is always clear, there is no spooky action at a distance.', 'José Valim, <a href="https://dashbit.co/blog/why-elixir-best-language-for-ai">Why Elixir is the best language for AI</a>, February 2026')}
<p>The measured part is <a href="https://arxiv.org/abs/2508.09101">AutoCodeBench</a>: Claude Opus 4 scored 80.3 on Elixir, the best of 20 languages, against an average of 52.4. It tests standalone functions, not Phoenix apps. Tooling: {a('tidewave-ai/tidewave_phoenix', 'Tidewave')} gives the agent the running app, and Phoenix 1.8's generator writes an AGENTS.md "containing guidelines extracted from the Phoenix.new agent" to correct "common mistakes LLMs make" (<a href="https://phoenixframework.org/blog/phoenix-1-8-released">Phoenix 1.8</a>). <strong>Counterpoint:</strong> Phoenix was the <em>most</em> token-expensive framework in Martin Alderson's 19-framework test (74k tokens).</p>
<h2>Ruby on Rails 8</h2>
<p><a href="https://rubyonrails.org/ai">rubyonrails.org/ai</a>: "Rails gives agents a map", "Less code means more context". It hosts {a('rails/ai-evals', 'an eval suite')} of 46 tasks, but it ranks models on Rails, not Rails against other frameworks. <strong>Counterpoint:</strong> practitioners report that callbacks and concerns hide behaviour from agents, the same "magic" Armin Ronacher warns about in Python.</p>
<h2>Laravel and Laravel Boost</h2>
{intercept('Large language models are surprisingly good at PHP because there is a lot of PHP training data. That helps, but it\'s not enough. Without context, they invent APIs, misuse framework idioms, or skip tests.', 'Ashley Hindle, <a href="https://laravel.com/blog/announcing-laravel-boost">Announcing Laravel Boost</a>, August 2025')}
<p>{a('laravel/boost', 'Boost')} is an MCP server with 15+ tools (Tinker, database schema, routes, last error, browser logs) plus version-specific guidelines and a docs API of 17,000+ entries. No outcome data has been published, and PHP was the lowest-scoring language on AutoCodeBench (28.1).</p>
<h2>Next.js</h2>
<p>The most extensive official tooling of any framework. The Next.js 16 dev server exposes <code>/_next/mcp</code> with <code>get_errors</code>, <code>get_routes</code>, <code>get_compilation_issues</code> and <code>compile_route</code>, and version-matched docs ship inside <code>node_modules</code> (<a href="https://nextjs.org/docs/app/guides/mcp">docs</a>). Vercel's <a href="https://nextjs.org/evals">Next.js Evals</a> are close to saturated, with several frontier model and agent pairs at 100%. <strong>Counterpoint:</strong> the docs injection exists because Next.js changes faster than training data.</p>
<h2>SvelteKit</h2>
<p>The {a('sveltejs/ai-tools', 'Svelte MCP')} includes <code>svelte-autofixer</code>, static analysis meant to be "invoked in an agentic loop by your model until all issues and suggestions are resolved" (<a href="https://svelte.dev/docs/ai/tools">docs</a>). SvelteKit was the cheapest full-featured framework in Alderson's token test (28k). The autofixer exists largely because models still write Svelte 4 instead of Svelte 5 runes.</p>
<h2>Convex, Supabase and Instant</h2>
<p>Convex: "Your database queries are pure TypeScript functions with end-to-end type safety" (<a href="https://docs.convex.dev/ai">docs</a>). Its {a('convex/fullstack-bench', 'Fullstack-Bench')} ran the same app with the same agent on three backends. On the Files task Convex passed 33/34, Supabase 16/34 and FastAPI 11/34. The conclusion: "Type safety, in particular, is an excellent guardrail for coding agents." It is vendor-run, with three tasks and one agent. Supabase ships an {a('supabase/mcp', 'official MCP server')} and is the default backend of prompt-to-app builders. Instant argues agents should ship apps with no backend code at all (<a href="https://www.instantdb.com/essays/agents">essay</a>).</p>
<h2>shadcn/ui and Tailwind</h2>
<p>"Open code for LLMs to read, understand, and improve" (<a href="https://ui.shadcn.com/docs">shadcn</a>). Components are copied into your repo instead of hidden in a package, and there is an official MCP and registry. The evidence is adoption: it is the default UI layer in AI app builders. Lovable starts new apps on TanStack Start with Tailwind and shadcn (<a href="https://docs.lovable.dev/introduction/faq">FAQ</a>).</p>
<h2>Hypermedia: htmx and Datastar</h2>
<p>The argument is that returning HTML removes a JSON API and a client state layer for the agent to keep consistent. The reports are mixed. Agents reach for <code>fetch()</code> and JSON "out of habit", and htmx 4 renamed things models had learned (<a href="https://flaviocopes.com/ahastack-update.md">Flavio Copes</a>). One Clojure developer contrasted Datastar ("basically just curl") with Electric's two runtimes (<a href="/blog/server-driven-ui-and-agents/">case 002</a>).</p>
<h2>Go, Django, Effect and Gleam</h2>
<ul>
<li><strong>Go:</strong> "if you can choose your language, I strongly recommend Go for new backend projects"; "Simple code significantly outperforms complex code in agentic contexts" (<a href="https://lucumr.pocoo.org/2025/6/12/agentic-coding/">Ronacher, June 2025</a>). But Go scored 37.2 on AutoCodeBench.</li>
<li><strong>Django:</strong> efficient among full-featured frameworks in Alderson's test, with a community MCP, {a('vintasoftware/django-ai-boost', 'django-ai-boost')}.</li>
<li><strong>Effect:</strong> typed errors as compiler feedback, but agents often invent Effect APIs. The advice is to vendor the source so agents read it.</li>
<li><strong>Gleam:</strong> "Gleam's compiler lets agents self-correct", though the team behind that post later chose Rust and TypeScript (<a href="https://curling.io/blog/21-reasons-ai-agents-love-gleam">Curling IO</a>).</li>
</ul>
<h2>Clojure</h2>
<p>{a('bhauman/clojure-mcp', 'clojure-mcp')}'s README now recommends its <code>:repl</code> profile: the agent can "explore in the REPL, check its assumptions against the running program, and test changes as it makes them". No benchmark includes Clojure; Racket, another Lisp, scored 68.9 on AutoCodeBench, which is a weak hint that the syntax isn't disqualifying. The full argument is in <a href="/approaches/clojure/agents/">case 001</a>.</p>
<h2>Vendor claims on token cost</h2>
<p>Wasp says the same feature took 38% fewer tokens than on a Next.js starter (<a href="https://wasp.sh/blog/2026/03/26/nextjs-vs-wasp-40-percent-less-tokens-same-app">Wasp</a>). Encore says NestJS took about twice the tokens (<a href="https://encore.dev/articles/nestjs-vs-encore-ai-agents">Encore</a>). Both are single-vendor and small. For tRPC, Hono, Elysia and RedwoodSDK we found no agent-specific evidence at all.</p>
</div>
{table(TOOLING, 'Agent tooling that frameworks ship', 'full')}'''
    out.append(('/practices/agentic-frameworks/frameworks/', 'Framework by framework', 'The claims, evidence, agent tooling and counterpoints for Phoenix, Rails, Laravel, Next.js, SvelteKit, Convex, Supabase, shadcn, htmx, Datastar, Go, Django, Effect, Gleam and Clojure.', fw))

    pt = f'''{M('What makes a framework agent-friendly', 'Eight patterns, how much of each is measured, and what the benchmarks actually test', 'patterns')}
<div class="bluf"><p>Four things are measured to help agents: docs that are always in context, fast type or compiler feedback, small surface area, and live access to the running app. Conventions, stability and training-data mass are argued but not measured, and the training-data argument cuts both ways.</p></div>
<div class="prose">
<h2>The patterns</h2>
<ol>
<li><strong>A fast, machine-readable check after every change.</strong> Compilers, types and linters. Convex credits type safety, Svelte runs its autofixer in a loop, and Next.js lets agents compile a single route. "Quick compilation and execution significantly boost productivity of the agent" (Ronacher).</li>
<li><strong>The running app, open to the agent.</strong> Tidewave, Boost, <code>/_next/mcp</code> and clojure-mcp all give the agent errors, logs, routes or a REPL from the live process. This is the clearest trend of 2025–26.</li>
<li><strong>Version-pinned docs, delivered passively.</strong> Vercel measured 53% → 100% with an AGENTS.md docs index. Next.js ships docs in <code>node_modules</code>; Boost ships docs for the installed version.</li>
<li><strong>Explicit over magic.</strong> "Agents struggle with Python's magic"; "making code findable through the most basic tools is great" (<a href="https://lucumr.pocoo.org/2026/2/9/a-language-for-agents/">Ronacher, February 2026</a>). Valim makes the same case for immutability.</li>
<li><strong>Small surface area.</strong> Minimal frameworks took 26–29k tokens to build the same app; full-featured ones up to 74k (<a href="https://martinalderson.com/posts/which-web-frameworks-are-most-token-efficient-for-ai-agents/">Alderson, February 2026</a>).</li>
<li><strong>Stability.</strong> Elixir 1.x has had no breaking changes since 2014. The negative examples are Next.js 16 APIs, htmx 4 attribute changes, Svelte 5 runes and Effect's major versions, each of which needed extra docs or tools.</li>
<li><strong>Conventions, written down.</strong> Rails "gives agents a map", but conventions only help once they're in a rules file: Phoenix's AGENTS.md, Laravel's guidelines, Convex's rules, <code>usage_rules</code>.</li>
<li><strong>Training-data mass, which cuts both ways.</strong> AI app builders default to React, TypeScript, Tailwind and shadcn. Yet on AutoCodeBench the high-volume languages (JavaScript 38.6, Go 37.2, PHP 28.1) scored <em>below</em> average for Opus 4, and early Multi-SWE-bench results put TypeScript and JavaScript among the lowest resolve rates.</li>
</ol>
{stat('53% → 100%', 'Vercel\'s agent success rate on Next.js 16 APIs that postdate training data. No docs: 53%. A skill: 53%, because the agent didn\'t invoke it in 56% of runs. A skill plus an explicit instruction: 79%. A compressed docs index in AGENTS.md: 100%. "Passive context currently outperforms on-demand retrieval."', 'The best-measured result')}
<h2>Hype against evidence</h2>
<table class="cmp"><thead><tr><th>Study</th><th>What it measures</th><th>What it can't tell you</th></tr></thead><tbody>
<tr><td>{a('Tencent-Hunyuan/AutoCodeBenchmark', 'AutoCodeBench')}</td><td>Single-function problems in 20 languages</td><td>Anything about frameworks; Clojure isn't included</td></tr>
<tr><td>{a('multi-swe-bench/multi-swe-bench', 'Multi-SWE-bench')}</td><td>Fixing real issues in real repos, by language</td><td>Current frontier numbers per language (not checked)</td></tr>
<tr><td>Vercel AGENTS.md study and {a('vercel/next-evals-oss', 'Next.js Evals')}</td><td>Context strategies and models within Next.js</td><td>Next.js against other frameworks</td></tr>
<tr><td>{a('rails/ai-evals', 'Rails ai-evals')}</td><td>Models on Rails tasks</td><td>Rails against other frameworks</td></tr>
<tr><td>{a('convex/fullstack-bench', 'Convex Fullstack-Bench')}</td><td>One app, one agent, three backends</td><td>Anything independent: it is vendor-run</td></tr>
<tr><td>Alderson's token test</td><td>Tokens to build one app in 19 frameworks</td><td>Quality at scale: n=1 per framework</td></tr>
</tbody></table>
{caveat('<p>"Agents love Rails", "Go is best for agents", "Gleam is optimal" and "hypermedia is easier for agents" are all anecdote or vendor claims. Treat them as hypotheses about mechanisms, not results.</p>', 'Unmeasured')}
<h2>For a Clojure backend with a functional front end</h2>
<ul>
<li>Clojure has pattern 2 natively (the REPL) and pattern 4 by culture (explicit data, immutability).</li>
<li>Add pattern 1 with clj-kondo and malli, and pattern 3 with a compact, always-loaded AGENTS.md. Vercel's result says that beats a skill the agent may not call.</li>
<li>Pattern 5 favours Datastar or a small UIx layer over a large framework.</li>
<li>Pattern 8 is the one you give up, and the evidence says it matters less than people think.</li>
</ul>
</div>
{table(BENCH, 'Benchmarks and evals', 'full')}'''
    out.append(('/practices/agentic-frameworks/patterns/', 'What makes a framework agent-friendly', 'Eight patterns that make frameworks work well with coding agents, which are measured and which are argued, and what the benchmarks actually test.', pt))
    return out

def posts(R, BL, d):
    a = lambda n, l=None: _a(R, n, l)
    P = []
    P.append(dict(slug='agents-see-the-running-app', kj='Every major framework now lets the agent see the running app', conf=HIGH, tags=['agents'],
      title='Every framework is giving agents a window into the running app',
      dek='Tidewave, Laravel Boost, Next.js 16\'s /_next/mcp, Supabase MCP, Svelte MCP, clojure-mcp: separate teams shipped the same idea in 2025–2026.',
      bluf='The convergent move in framework design for agents isn\'t a new syntax or a new template. It\'s an endpoint that lets the agent ask the live app what is wrong: errors, routes, logs, schema, or a REPL. Lisp developers will recognise it.',
      body=f'''<ul>
<li><strong>Tidewave</strong> for Phoenix and Rails: runtime introspection, framework traces and in-browser verification ({a('tidewave-ai/tidewave_phoenix', 'Phoenix')}, {a('tidewave-ai/tidewave_rails', 'Rails')}).</li>
<li><strong>{a('laravel/boost', 'Laravel Boost')}</strong> (August 2025): Tinker, database schema, routes, last error and browser logs over MCP.</li>
<li><strong>Next.js 16</strong>: the dev server exposes <code>/_next/mcp</code> with <code>get_errors</code>, <code>get_routes</code> and <code>get_compilation_issues</code>.</li>
<li><strong>{a('supabase/mcp', 'Supabase MCP')}</strong> (April 2025): SQL, migrations, branching, logs and type generation.</li>
<li><strong>{a('sveltejs/ai-tools', 'Svelte MCP')}</strong>: docs plus an autofixer that runs in the agent's loop.</li>
<li><strong>{a('bhauman/clojure-mcp', 'clojure-mcp')}</strong>: whose README now recommends the plain <code>:repl</code> profile over its own editing tools.</li>
</ul>
{finding('Why it works', '<p>An agent that guesses has to be right the first time. An agent that can check fixes its own mistakes before you see them. Live introspection turns the running program into the source of truth, which is the argument Clojure developers have made for the REPL for fifteen years (<a href="/approaches/clojure/agents/">case 001</a>).</p>')}
{caveat('<p>The trend is certain; the payoff is measured only indirectly. No study isolates "MCP into the dev server" as a variable.</p>')}''',
      after=table(['tidewave-ai/tidewave_phoenix', 'tidewave-ai/tidewave_rails', 'laravel/boost', 'vercel/next-devtools-mcp', 'supabase/mcp', 'sveltejs/ai-tools', 'bhauman/clojure-mcp', 'day8/re-frame-pair'], 'Live-app tooling', 'full')))
    P.append(dict(slug='agents-md-beats-skills', kj='Docs the agent always sees beat docs it has to ask for', conf=HIGH, tags=['agents'],
      title='AGENTS.md beats skills: always-on docs win, measured',
      dek='On Next.js 16 APIs that postdate training data, a compressed docs index in AGENTS.md took agents from 53% to 100%. A skill did nothing, because agents didn\'t call it.',
      bluf='If an agent needs to know something about your framework or codebase, put a compact index of it where the agent always sees it. On-demand retrieval (skills, tools, MCP docs) only helps when the agent decides to use it, and often it doesn\'t.',
      body=f'''{stat('56%', 'Of runs where a skill with the right documentation was available, the agent never invoked it. With the skill: 53%, the same as no docs. With an explicit instruction to use it: 79%. With a compressed docs index in AGENTS.md: 100%.', 'Vercel, January 2026')}
<p>Jude Gao at Vercel tested agents on Next.js 16 APIs that aren't in training data (<a href="https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals">AGENTS.md outperforms skills</a>). The conclusion: "for general framework knowledge, passive context currently outperforms on-demand retrieval."</p>
<p>Frameworks have drawn the same conclusion. Phoenix 1.8 generates an AGENTS.md, Next.js ships version-matched docs inside <code>node_modules</code>, Convex installs AI files, and Laravel Boost writes guidelines for the installed version. llms.txt is widely published, but full files are often too big. One Instant user compressed it into a 1.5k-line rules file.</p>
{finding('Applied here', '<p>This site follows the same rule: <a href="/llms.txt">/llms.txt</a> is about a thousand tokens and points to compact catalogs, and the <a href="/for-agents/">for-agents page</a> gives a short snippet for your AGENTS.md rather than a skill alone.</p>')}'''))
    P.append(dict(slug='no-framework-benchmark', kj='"Agents love framework X" is mostly anecdote', conf=MOD, tags=['agents'],
      title='Nobody has benchmarked frameworks for agents',
      dek='The cross-framework numbers are vendor-run. The independent ones test languages or context strategies. Elixir tops one; PHP and Go trail.',
      bluf='When someone says agents do best in their framework, ask which mechanism they mean. The measured results are about languages (AutoCodeBench), context (Vercel) and types (Convex, vendor-run), not about Rails against Phoenix against Next.js.',
      body=f'''<p>The measured evidence, ranked by independence:</p>
<ul>
<li><strong>{a('Tencent-Hunyuan/AutoCodeBenchmark', 'AutoCodeBench')}</strong> (Tencent, ICLR 2026): Claude Opus 4 scored Elixir 80.3, C# 74.9, Kotlin 72.5, Racket 68.9, and at the bottom JavaScript 38.6, Go 37.2 and PHP 28.1. These are single-function problems with a separate set per language, and Clojure isn't included.</li>
<li><strong>Multi-SWE-bench</strong> (ByteDance, April 2025): issue resolution on real repos. TypeScript and JavaScript had among the lowest resolve rates in early results.</li>
<li><strong>Vercel's evals</strong>: rigorous, but within Next.js only.</li>
<li><strong>Rails ai-evals</strong>: models on Rails only.</li>
<li><strong>Convex Fullstack-Bench</strong>: the only cross-backend comparison, run by Convex. Convex 33/34, Supabase 16/34 and FastAPI 11/34 on the Files task.</li>
</ul>
{caveat('<p>The training-data argument ("agents know React and PHP best") isn\'t supported by the language results, where the highest-volume languages scored below average. That doesn\'t prove the opposite either: AutoCodeBench\'s per-language problem sets aren\'t equally hard.</p>', 'Both ways')}
<p>What transfers is the mechanism: types or a compiler in the loop, docs always in context, a small surface, and the running app open to the agent.</p>''',
      after=table(BENCH, 'Benchmarks and evals', 'full')))
    P.append(dict(slug='small-surface-area', kj='Smaller frameworks cost agents fewer tokens', conf=LOW, tags=['agents'],
      title='Smaller frameworks cost agents fewer tokens',
      dek='In an informal 19-framework test, minimal frameworks took 26–29k tokens for the same app and full-featured ones up to 74k. Phoenix was the most expensive.',
      bluf='Every file an agent must read to make a change costs tokens and attention. Minimal frameworks, and languages that say more per line, leave more of the context window for your actual problem.',
      body=f'''<p>Martin Alderson built the same small app in 19 web frameworks with an agent and counted tokens (<a href="https://martinalderson.com/posts/which-web-frameworks-are-most-token-efficient-for-ai-agents/">February 2026</a>). Minimal APIs (ASP.NET Minimal API at 26k) were cheapest, SvelteKit was the cheapest full-featured framework (28k), and Phoenix the most expensive (74k). "Minimal API web frameworks are far quicker and more cost effective for agents to work with."</p>
<p>The same author found Clojure the most token-efficient of 19 languages on Rosetta Code (<a href="https://martinalderson.com/posts/which-programming-languages-are-most-token-efficient/">January 2026</a>). Vendors make similar claims for their own frameworks: Wasp says 38% fewer tokens than a Next.js starter, and Encore says half of NestJS.</p>
{caveat('<p>Low confidence: one run per framework, one app, and token cost isn\'t quality. Phoenix being the most expensive while Elixir tops AutoCodeBench is a reminder that the two measure different things.</p>')}'''))
    return P

def sources():
    S = lambda date, title, who, url, type, k, sum: dict(date=date, title=title, who=who, url=url, type=type, k=k, sum=sum)
    return [
     S('2026-02', 'Why Elixir is the best language for AI', 'José Valim, Dashbit', 'https://dashbit.co/blog/why-elixir-best-language-for-ai', 'article', ['agents'], 'AutoCodeBench results, immutability, stable APIs and runtime introspection as reasons agents do well in Elixir.'),
     S('2025', 'Phoenix 1.8 released', 'Phoenix', 'https://phoenixframework.org/blog/phoenix-1-8-released', 'article', ['agents'], 'phx.new generates an AGENTS.md of guidelines that correct common LLM mistakes.'),
     S('2026', 'Tidewave', 'Tidewave', 'https://tidewave.ai/', 'tool', ['agents'], 'Connects agents to the running Phoenix or Rails app: runtime intelligence, traces, in-browser verification.'),
     S('2026', 'Rails and AI', 'Ruby on Rails', 'https://rubyonrails.org/ai', 'doc', ['agents'], '"Rails gives agents a map"; hosts a 46-task model benchmark on Rails.'),
     S('2025-08', 'Announcing Laravel Boost', 'Ashley Hindle, Laravel', 'https://laravel.com/blog/announcing-laravel-boost', 'article', ['agents'], 'MCP with 15+ tools and version-specific guidelines; "without context, they invent APIs".'),
     S('2026', 'Next.js MCP guide', 'Vercel', 'https://nextjs.org/docs/app/guides/mcp', 'doc', ['agents'], 'The Next.js 16 dev server exposes /_next/mcp: errors, routes, logs, compilation issues.'),
     S('2026', 'Next.js Evals', 'Vercel', 'https://nextjs.org/evals', 'paper', ['agents'], 'Pass@4 per model and agent on Next.js tasks; several frontier pairs at 100%.'),
     S('2026-01', 'AGENTS.md outperforms skills in our agent evals', 'Jude Gao, Vercel', 'https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals', 'paper', ['agents'], 'No docs 53%, skill 53%, skill + instruction 79%, AGENTS.md docs index 100%.'),
     S('2026', 'Svelte AI tools', 'Svelte', 'https://svelte.dev/docs/ai/tools', 'doc', ['agents'], 'Official MCP with svelte-autofixer for use in the agent loop.'),
     S('2026', 'Convex and AI', 'Convex', 'https://docs.convex.dev/ai', 'doc', ['agents'], 'Pure TypeScript queries with end-to-end types; rules files, MCP and a model leaderboard.'),
     S('2025', 'Introducing Fullstack-Bench', 'Convex', 'https://stack.convex.dev/introducing-fullstack-bench', 'paper', ['agents'], 'Same app and agent on Convex, Supabase and FastAPI; vendor-run.'),
     S('2025-04', 'Supabase MCP server', 'Supabase', 'https://supabase.com/blog/mcp-server', 'article', ['agents'], 'Official MCP: SQL, migrations, branching, logs, type generation.'),
     S('2026', 'How and where will agents ship software?', 'InstantDB', 'https://www.instantdb.com/essays/agents', 'article', ['agents'], 'Instant\'s case that agents should ship apps with no backend code.'),
     S('2026', 'shadcn/ui docs', 'shadcn', 'https://ui.shadcn.com/docs', 'doc', ['agents', 'frontend'], '"Open code for LLMs to read, understand, and improve"; official MCP and registry.'),
     S('2026', 'Lovable FAQ', 'Lovable', 'https://docs.lovable.dev/introduction/faq', 'doc', ['agents'], 'New apps start on TanStack Start since May 2026.'),
     S('2026', 'The AHA stack, updated', 'Flavio Copes', 'https://flaviocopes.com/ahastack-update.md', 'article', ['agents', 'frontend'], 'Agents reach for fetch and JSON by habit; htmx 4 changes trip up models.'),
     S('2025', 'Getting AI coding agents to use htmx', 'r/htmx', 'https://www.reddit.com/r/htmx/comments/1kveih9/getting_ai_coding_agents_to_use_htmx/', 'forum', ['agents'], 'Models often stumble on htmx even with docs.'),
     S('2025-06', 'Agentic coding recommendations', 'Armin Ronacher', 'https://lucumr.pocoo.org/2025/6/12/agentic-coding/', 'article', ['agents'], 'Prefer Go, plain SQL and simple code; agents struggle with magic.'),
     S('2026-02', 'A language for agents', 'Armin Ronacher', 'https://lucumr.pocoo.org/2026/2/9/a-language-for-agents/', 'article', ['agents'], 'Code that is findable with basic tools is good for agents.'),
     S('2026-08', 'Why Go is an ideal language for AI-assisted software engineering', 'Google Developers Blog', 'https://developers.googleblog.com/en/why-go-is-an-ideal-language-for-ai-assisted-software-engineering/', 'article', ['agents'], 'Google\'s case for Go with agents (title and date verified only).'),
     S('2026', 'django-ai-boost', 'Vinta Software', 'https://www.vintasoftware.com/blog/django-ai-boost-productivity', 'article', ['agents'], 'A read-only Django MCP inspired by Laravel Boost.'),
     S('2026-05', 'This week in Effect', 'Effect', 'https://effect.website/blog/this-week-in-effect/2026/05/15/', 'article', ['agents'], 'Vendor Effect\'s source so agents read it instead of stale docs.'),
     S('2026-02', 'Which web frameworks are most token-efficient for AI agents?', 'Martin Alderson', 'https://martinalderson.com/posts/which-web-frameworks-are-most-token-efficient-for-ai-agents/', 'article', ['agents'], 'Minimal frameworks 26–29k tokens, full-featured up to 74k; Phoenix the most expensive.'),
     S('2026-03', 'Next.js vs Wasp: 40% fewer tokens', 'Wasp', 'https://wasp.sh/blog/2026/03/26/nextjs-vs-wasp-40-percent-less-tokens-same-app', 'article', ['agents'], 'Vendor study: the same feature in fewer tokens.'),
     S('2026', 'NestJS vs Encore for AI agents', 'Encore', 'https://encore.dev/articles/nestjs-vs-encore-ai-agents', 'article', ['agents'], 'Vendor study: about half the tokens of NestJS.'),
     S('2025-04', 'Multi-SWE-bench', 'ByteDance', 'https://arxiv.org/abs/2504.02605', 'paper', ['agents'], 'Multilingual issue resolution; TS/JS among the lowest resolve rates in early results.'),
     S('2024-09', 'The /llms.txt file', 'Jeremy Howard, Answer.AI', 'https://www.answer.ai/posts/2024-09-03-llmstxt', 'article', ['agents'], 'The llms.txt proposal.'),
    ]
