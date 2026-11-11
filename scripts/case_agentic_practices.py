"""Case 005: agentic coding practices that work. Research filed 2026-11-11."""
from content import _a, finding, caveat, signal, intercept, stat, table, HIGH, MOD, LOW

REF = 'SMAF-005'
def conf_chip(c): return f'<span class="conf {c[0]}">{c[1]}</span>'
EV = {'m': ('high', 'MEASURED'), 's': ('mod', 'SURVEY'), 'p': ('mod', 'PRACTITIONER'), 'v': ('low', 'VENDOR CLAIM')}
def ev(*ks): return ' '.join(f'<span class="conf {EV[k][0]}">{EV[k][1]}</span>' for k in ks)

WORKFLOW = ['github/spec-kit', 'Fission-AI/OpenSpec', 'bmad-code-org/BMAD-METHOD', 'humanlayer/humanlayer', 'humanlayer/advanced-context-engineering-for-coding-agents',
            'gastownhall/beads', 'ghuntley/how-to-ralph-wiggum', 'wilsonzlin/fastrender']
SKILLS = ['agentsmd/agents.md', 'agentskills/agentskills', 'anthropics/skills', 'obra/superpowers', 'hesreallyhim/awesome-claude-code', 'AnswerDotAI/llms-txt']
VERIFY = ['nizos/tdd-guard', 'disler/claude-code-hooks-mastery', 'microsoft/playwright-mcp', 'ChromeDevTools/chrome-devtools-mcp', 'vercel-labs/agent-browser',
          'badlogic/terminalcp', 'bhauman/clojure-mcp', 'bhauman/clojure-mcp-light', 'laravel/boost', 'tidewave-ai/tidewave_phoenix']
AGENTS = ['anthropics/claude-code', 'anthropics/claude-code-action', 'anthropics/claude-code-security-review', 'openai/codex', 'anomalyco/opencode',
          'earendil-works/pi', 'Aider-AI/aider', 'aaif-goose/goose']
BENCH = ['benchflow-ai/skillsbench', 'pepealonso95/TDAD']

def pages(memo, R, d):
    a = lambda n, l=None: _a(R, n, l)
    M = lambda title, subj, eb: memo(title, subj, 'Open', eyebrow=f'Case 005 // {eb}', ref=REF)
    out = []
    brief = f'''{M('Agentic coding practices: what is working', 'What are people doing that actually works when coding agents write the code, and how much of it is measured?', 'brief')}
<div class="bluf"><p><strong>Agents raise output almost everywhere it's measured. The cost turns up later, in review time, incidents and instability.</strong> The practices that hold up all attack that cost by making the agent's work checkable before a person looks at it: a fast, quiet, deterministic verifier; a short hand-written context file; a plan sized to the change; context kept small; and the agent checking its own work in the running app. Rituals like generic TDD prompts and heavy spec frameworks hold up worse than their popularity suggests.</p></div>
<div class="prose">
<h2>Key judgments</h2>
<ol class="kj">
<li><div><h3>More output, paid for downstream</h3><p>METR's trial found experienced developers 19% <em>slower</em> while believing they were faster. Telemetry from 22,000 developers shows throughput up a third, but incidents per PR up 243% and review time up 442%. {conf_chip(HIGH)} <a class="more" href="/blog/output-up-stability-down/">dispatch →</a></p></div></li>
<li><div><h3>The verifier is the practice</h3><p>The most consistent factor in every success story is a deterministic check the agent can run itself: tests, types, custom lints, a REPL, a browser. Anthropic's C-compiler run: "the task verifier is nearly perfect, otherwise Claude will solve the wrong problem." {conf_chip(MOD)} <a class="more" href="/blog/the-verifier-is-the-practice/">dispatch →</a></p></div></li>
<li><div><h3>Context files help only when short and hand-written</h3><p>An ETH study found context files don't raise success on average and cost 20% more. Developer-written ones gave +4% and LLM-generated ones −3%. Practitioners converge on fewer than 100 lines, written as a map. {conf_chip(MOD)} <a class="more" href="/blog/context-files-short-and-handwritten/">dispatch →</a></p></div></li>
<li><div><h3>Give the agent the right tests, not a TDD ritual</h3><p>In the one measured study, generic "do TDD" instructions <em>raised</em> regressions to 9.94%, while a map of the relevant tests cut them 70%. A small Thoughtworks eval found TDD slightly worse. {conf_chip(LOW)} <a class="more" href="/blog/test-context-beats-tdd-ritual/">dispatch →</a></p></div></li>
<li><div><h3>Focused skills help; generated ones don't</h3><p>SkillsBench: curated skills took pass rates from 33.9% to 50.5%, and skills of three modules or fewer beat exhaustive bundles. Whether a tool is exposed through MCP or a CLI matters less than its design. {conf_chip(MOD)} <a class="more" href="/blog/focused-skills-load-on-demand/">dispatch →</a></p></div></li>
</ol>
<h2>The short version</h2>
<table class="cmp"><thead><tr><th>Practice</th><th>What people do</th><th>Evidence</th></tr></thead><tbody>
<tr><td>Verifier in the loop</td><td>Tests, types, lints with fix-it messages, REPL, browser checks; quiet output</td><td>{ev('p', 'v')} consistent everywhere</td></tr>
<tr><td>Short context file</td><td>Under ~100 lines, hand-written: commands, conventions, traps</td><td>{ev('m')} mixed; hand-written beats generated</td></tr>
<tr><td>Research → plan → implement</td><td>Written plan reviewed by a human; compact context between phases</td><td>{ev('p')} HumanLayer, Anthropic</td></tr>
<tr><td>Small context</td><td>Compact at 40–60%; subagents for search; log noise to files</td><td>{ev('m')} context rot is measured</td></tr>
<tr><td>Self-verification in the app</td><td>Playwright, DevTools MCP, log tailing, live-app MCP</td><td>{ev('p', 'v')} no controlled study</td></tr>
<tr><td>Focused skills</td><td>Small curated skills, loaded on demand</td><td>{ev('m')} SkillsBench</td></tr>
<tr><td>Parallel agents</td><td>Worktrees or fresh checkouts, background agents; review is the bottleneck</td><td>{ev('p')} no controlled study</td></tr>
<tr><td>Spec frameworks</td><td>Spec Kit, Kiro, BMAD, OpenSpec</td><td>{ev('p')} overkill for small changes</td></tr>
<tr><td>Generic TDD prompts</td><td>"Write the test first"</td><td>{ev('m')} small study: worse</td></tr>
</tbody></table>
{finding('For a Clojure developer', '<p>The REPL is the verifier these teams build by hand. An agent connected through clojure-mcp checks each form against the running program, which is the loop OpenAI wired up with DevTools and custom lints. Add clj-kondo for lint and malli for schemas, write a short AGENTS.md by hand, and you have most of the measured kit (<a href="/approaches/clojure/agents/">case 001</a>, <a href="/approaches/frontend-sync/cljs-cost/">case 002</a>).</p>')}
<h2>In this case file</h2>
<ul><li><a href="/practices/agentic-practices/playbook/">The playbook</a>: each practice, who reports it, the numbers and the counter-evidence.</li>
<li><a href="/practices/agentic-practices/evidence/">The evidence</a>: every productivity study, side by side, and the failure modes they found.</li>
<li><a href="/practices/agentic-practices/toolkit/">The toolkit</a>: the repos people use: agents, skills, hooks, verifiers, spec tools.</li></ul>
</div>'''
    out.append(('/practices/agentic-practices/', 'Case 005: agentic coding practices that work', 'What developers are doing that works with coding agents (Claude Code, Codex, Cursor): verifiers, context files, planning, skills, parallel agents, with the evidence and counter-evidence.', brief))

    pb = f'''{M('The playbook', 'Each practice: what it is, who reports it working, the numbers, and the counter-evidence', 'playbook')}
<div class="bluf"><p>Tags show how each claim is known. <span class="conf high">MEASURED</span> means a controlled study or telemetry with a comparison group. <span class="conf mod">SURVEY</span> is self-reported. <span class="conf mod">PRACTITIONER</span> is a named person or team describing their own setup. <span class="conf low">VENDOR CLAIM</span> means the seller measured itself.</p></div>
<div class="prose">
<h2 id="verify">1. Give the agent a verifier, and keep it quiet</h2>
<p>Every detailed success story has one. Nicholas Carlini's run of 16 parallel agents (about 2,000 sessions, about $20,000) produced a 100,000-line Rust C compiler. His lessons: the verifier must be "nearly perfect, otherwise Claude will solve the wrong problem", and the test harness "should not print thousands of useless bytes". Details go to a log file, because noise pollutes context (<a href="https://www.anthropic.com/engineering/building-c-compiler">Anthropic, Feb 2026</a>). {ev('v')}</p>
<p>OpenAI's harness team (3 to 7 engineers, about 1,500 PRs, about 1M lines in five months, no hand-written code) enforces architecture with custom lints: "because the lints are custom, we write the error messages to inject remediation instructions into agent context" (<a href="https://openai.com/index/harness-engineering/">Harness engineering, Feb 2026</a>). {ev('v', 'p')}</p>
{intercept('Give Claude a way to verify its work. If Claude has that feedback loop, it will 2-3x the quality of the final result.', 'Boris Cherny, creator of Claude Code, <a href="https://x.com/bcherny/status/2007179861115511237">January 2026</a>. The 2–3x is his estimate, not a measurement.')}
<p>Enforce checks with hooks or CI, not prose: Claude Code's <code>PostToolUse</code> and <code>Stop</code> hooks run formatters, linters and tests ({a('disler/claude-code-hooks-mastery', 'hook examples')}, {a('nizos/tdd-guard', 'tdd-guard')}). HumanLayer: "Never send an LLM to do a linter's job." No controlled study of hooks exists. {ev('p')}</p>

<h2 id="context">2. Write a short context file by hand</h2>
<p><a href="https://arxiv.org/abs/2602.11988">Gloaguen et al., ETH Zurich (Feb 2026)</a>: context files "do not generally improve task success rates, while increasing inference cost by over 20%"; repository overviews "are not helpful". Developer-written files gave about +4%, LLM-generated ones about −3%. {ev('m')} <a href="https://arxiv.org/abs/2601.20404">Lulla et al. (Jan 2026)</a> found an AGENTS.md cut median runtime 28.6% and output tokens 16.6% at the same completion rate. {ev('m')} Vercel's docs index took new-API tasks from 53% to 100% (<a href="/blog/agents-md-beats-skills/">dispatch</a>). {ev('v')}</p>
<p>Practitioners land in the same place. OpenAI keeps about 100 lines that act as "the table of contents", with deeper docs in <code>docs/</code> and a lint that keeps them current. HumanLayer's is under 60 lines, and they say: "Don't use <code>/init</code> or auto-generate your CLAUDE.md" (<a href="https://www.humanlayer.dev/blog/writing-a-good-claude-md">HumanLayer, Nov 2025</a>). Armin Ronacher uses his to tell the agent where the logs are and how to run services, so it can check its own work. {ev('p')}</p>
{finding('Do this', '<p>Put in only what the agent can\'t work out from the code: commands, unusual conventions, traps, where logs live. Leave out the architecture tour. Point to deeper files instead of inlining them.</p>')}

<h2 id="plan">3. Research, plan, then implement, with the plan sized to the change</h2>
<p>Dex Horthy's "frequent intentional compaction" (<a href="https://www.humanlayer.dev/blog/advanced-context-engineering">HumanLayer, Aug 2025</a>, from a 300k-line Rust codebase): keep context "in the 40%-60% range", split work into research, plan and implement, write progress back into the plan after each verified phase, and put human review on the research and plan, where a bad assumption costs most. The prompts are public in {a('humanlayer/humanlayer')}. {ev('p')}</p>
<p>Anthropic's long-running harness solves "one-shots the app" and "declares victory early": an initializer writes a JSON feature list with every item marked failing, plus a progress file, and each session takes one feature, verifies it end to end, and commits (<a href="https://www.anthropic.com/research/effective-harnesses-for-long-running-agents">Nov 2025</a>). {ev('v')}</p>
<p><strong>Counter-evidence.</strong> Birgitta Böckeler tried Kiro, Spec Kit and Tessl: Kiro turned a small bug into "4 user stories with a total of 16 acceptance criteria", and "I'd rather review code than all these markdown files" (<a href="https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html">martinfowler.com, Oct 2025</a>). Peter Steinberger runs many parallel sessions with conversational planning and calls most of the scaffolding "charade" (<a href="https://steipete.me/posts/just-talk-to-it">Just Talk To It</a>). {ev('p')}</p>

<h2 id="small">4. Keep the context small</h2>
<p>Chroma's <a href="https://www.trychroma.com/research/context-rot">Context Rot</a> study measured performance falling as input grows, in every model tested, even on simple tasks. {ev('m')} This is the reason for compaction, subagents that search in their own context, quiet test output, and tools that return terse results.</p>

<h2 id="tests">5. Tests: give the agent the right tests rather than a ritual</h2>
<p><a href="https://arxiv.org/abs/2603.17973">TDAD (Mar 2026)</a>, on SWE-bench Verified with small samples: a map from code to its tests, given as a skill, cut regressions from 6.08% to 1.82%. Generic TDD instructions without that map <em>raised</em> them to 9.94%. {ev('m')} Böckeler's small eval found "no clearly discernable difference", with TDD "slightly worse". Her guess is that test-first prompting skips up-front design, and "behaviour the agent didn't think to write a test for didn't get implemented at all" (<a href="https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html">martinfowler.com, 2026</a>). {ev('p')}</p>
<p>Kent Beck's warning still applies: watch for the agent "cheating, for example by disabling or deleting tests" (<a href="https://newsletter.kentbeck.com/p/augmented-coding-beyond-the-vibes">Augmented Coding</a>). Mitigations: hooks that protect test files, "reddening" checks that revert the code and confirm the new tests fail (<a href="https://paulhammant.com/2026/10/14/red-green-refactor-moves-into-the-harness/">Paul Hammant, Oct 2026</a>), and mutation testing.</p>

<h2 id="self">6. Let the agent check its own work in the running app</h2>
<p>OpenAI "wired the Chrome DevTools Protocol into the agent runtime", with logs, metrics and traces the agent can query for each worktree. Anthropic's harness requires a browser check before a feature is marked passing. Ronacher has the agent tail a unified log and drive Playwright. Tools: {a('microsoft/playwright-mcp')}, {a('ChromeDevTools/chrome-devtools-mcp')}, {a('vercel-labs/agent-browser')}. Frameworks now ship the same idea (<a href="/blog/agents-see-the-running-app/">dispatch</a>). {ev('p', 'v')} No controlled study exists.</p>

<h2 id="skills">7. Focused skills, loaded on demand</h2>
<p><a href="https://arxiv.org/abs/2602.12670">SkillsBench (Feb 2026)</a>: across 87 tasks and 18 model and harness setups, curated skills raised the average pass rate from 33.9% to 50.5%. "Focused Skills with at most three modules outperform larger or exhaustive bundles", and small models with skills can match large ones without them. {ev('m')} Mario Zechner benchmarked the same tool as an MCP server and as a CLI and found it "largely a wash": design and token efficiency matter more than protocol (<a href="https://mariozechner.at/posts/2025-08-15-mcp-vs-cli/">Aug 2025</a>). {ev('m')} Anthropic's code-execution approach cut one MCP workflow from 150,000 to 2,000 tokens. {ev('v')}</p>
{caveat('<p>Vercel found agents skipped an available skill 56% of the time. Knowledge the agent needs on every task belongs in the context file. Skills suit procedures it needs sometimes.</p>')}

<h2 id="parallel">8. Parallel and background agents, with review as the limit</h2>
<p>Simon Willison runs parallel agents for research, small maintenance and well-specified work, and finds the bottleneck is "how fast I can review the results" (<a href="https://simonwillison.net/2025/Oct/5/parallel-coding-agents/">Oct 2025</a>). Anthropic's 16 compiler agents coordinated without an orchestrator, by writing lock files to <code>current_tasks/</code>. Cursor found that flat self-coordination churned. Planners plus workers let hundreds of agents build a browser ({a('wilsonzlin/fastrender')}) in about a week, though the agents "occasionally run for far too long" (<a href="https://cursor.com/blog/scaling-agents">Jan 2026</a>). {ev('p', 'v')} Faros's telemetry shows the cost: more PRs merged with no review (+31%) and much larger PRs.</p>

<h2 id="loops">9. Loops and memory across sessions</h2>
<p>Geoffrey Huntley's "Ralph" loop, <code>while :; do cat PROMPT.md | claude-code ; done</code>, does one task per iteration with the AGENTS file as memory ({a('ghuntley/how-to-ralph-wiggum')}). Steve Yegge's {a('gastownhall/beads', 'Beads')} keeps a git-backed issue tracker that agents can read and write. Both are widely copied, and neither has been measured. {ev('p')}</p>
</div>'''
    out.append(('/practices/agentic-practices/playbook/', 'The agentic coding playbook', 'Each agentic coding practice with who reports it, the numbers and the counter-evidence: verifiers, context files, planning, context size, tests, self-verification, skills, parallel agents.', pb))

    evd = f'''{M('The evidence', 'Every productivity study side by side, and the failure modes they found', 'evidence')}
<div class="bluf"><p>Output goes up in nearly every set of telemetry, and stability, review load and defects get worse in most of them. Self-reports run well ahead of measurements. The one randomized trial found a slowdown, then its authors said their own follow-up design could no longer measure the effect.</p></div>
<div class="prose">
<h2>Productivity studies</h2>
<table class="cmp"><thead><tr><th>Study</th><th>Kind</th><th>Finding</th></tr></thead><tbody>
<tr><td><a href="https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/">METR RCT</a>, Jul 2025</td><td>{ev('m')} 16 devs, 246 issues</td><td>Tasks took 19% longer with AI (CI +2% to +39%). Developers expected 24% faster and afterwards believed about 20% faster.</td></tr>
<tr><td><a href="https://metr.org/blog/2026-02-24-uplift-update/">METR update</a>, Feb 2026</td><td>{ev('m')} 57 devs, 800+ tasks</td><td>Returning devs −18%, new devs −4%, but METR calls the design broken: 30–50% withheld tasks they didn't want to do without AI. Moving to new methods.</td></tr>
<tr><td><a href="https://dora.dev/dora-report-2025/">DORA 2025</a></td><td>{ev('s')} ~5,000</td><td>90% use AI; over 80% report gains. Adoption now correlates with throughput, but still negatively with delivery stability. AI "amplifies" what is there.</td></tr>
<tr><td><a href="https://www.faros.ai/research/ai-acceleration-whiplash">Faros 2026</a></td><td>{ev('v')} telemetry, 22,000 devs</td><td>Throughput +33.7%; bugs per developer +54%; incidents per PR +242.7%; median review time +441.5%; PRs merged without review +31.3%.</td></tr>
<tr><td><a href="https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report">CodeRabbit</a>, Dec 2025</td><td>{ev('v')} 470 PRs</td><td>AI co-authored PRs had about 1.7x the issues (10.83 vs 6.45 per PR).</td></tr>
<tr><td><a href="https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic">Anthropic</a>, Dec 2025</td><td>{ev('s')} 132 engineers</td><td>Self-reported +50% productivity; 27% of the work wouldn't have been done otherwise; merged PRs per engineer +67% after adoption.</td></tr>
<tr><td><a href="https://www.anthropic.com/research/employment-at-anthropic">Anthropic</a>, Oct 2026</td><td>{ev('m', 'v')} 192 vs 74 engineers</td><td>Commits per engineer about 5x within six months; "no difference" in how often agent-written code was later removed or reverted. Adoption was not random, and it is a vendor studying itself.</td></tr>
<tr><td><a href="https://survey.stackoverflow.co/2025/ai">Stack Overflow 2025</a></td><td>{ev('s')}</td><td>46% distrust AI accuracy, 33% trust it. Top frustration: "almost right, but not quite" (66%).</td></tr>
</tbody></table>
{stat('−19% vs +20%', 'Measured change in task time against what the same developers believed afterwards, in METR\'s 2025 trial. Don\'t trust your own sense of speed. Measure it.', 'The perception gap')}
<h2>Failure modes and what people do about them</h2>
<table class="cmp"><thead><tr><th>Failure</th><th>Reported by</th><th>Mitigation</th></tr></thead><tbody>
<tr><td>"Almost right" code; debugging takes longer</td><td>Stack Overflow 2025; Anthropic engineers</td><td>Delegate verifiable tasks; give the agent a verifier</td></tr>
<tr><td>Review overload; PRs merged unreviewed</td><td>Faros; Willison</td><td>Agent-to-agent review (OpenAI); smaller diffs; reviewed plans</td></tr>
<tr><td>One-shotting, declaring victory early</td><td>Anthropic harness post</td><td>Feature list marked failing; one feature per session; end-to-end check</td></tr>
<tr><td>Deleting or gaming tests</td><td>Kent Beck; Böckeler</td><td>Hooks protecting tests; reddening checks; mutation testing</td></tr>
<tr><td>Context pollution</td><td>Carlini; Chroma</td><td>Quiet tools; logs to files; compaction; subagents</td></tr>
<tr><td>Running far too long</td><td>Carlini; Cursor</td><td>Fast sampled tests; time limits; planner/worker split</td></tr>
<tr><td>Context files that cost without helping</td><td>ETH 2026</td><td>Short, hand-written, non-obvious content only</td></tr>
<tr><td>Spec ceremony</td><td>Böckeler; a BMAD trial with 312 spec files for a retro board</td><td>Size the process to the change</td></tr>
</tbody></table>
{caveat('<p>Faros, CodeRabbit, Cursor and Anthropic all sell something related to what they measured. Their numbers are real telemetry, but read them as vendor claims. No controlled studies exist for hooks, parallel agents or browser self-verification.</p>')}
</div>'''
    out.append(('/practices/agentic-practices/evidence/', 'The evidence on agentic coding', 'Every agentic coding productivity study side by side (METR, DORA, Faros, CodeRabbit, Anthropic, Stack Overflow) and the failure modes they report.', evd))

    tk = f'''{M('The toolkit', 'The repos people use for agentic coding: agents, context and skills, verifiers and hooks, workflow and spec tools', 'toolkit')}
<div class="bluf"><p>Live GitHub numbers for the tools named in the playbook. These are the tools practitioners name, not a ranking. Health uses the Clojure baseline, so busy TypeScript and Rust projects score high easily.</p></div>
{table(VERIFY, 'Verifiers, hooks and live-app tools', 'full')}
{table(SKILLS, 'Context files and skills', 'full')}
{table(WORKFLOW, 'Workflow, planning and spec tools', 'full')}
{table(AGENTS, 'Coding agents', 'full')}
{table(BENCH, 'Benchmarks', 'full')}'''
    out.append(('/practices/agentic-practices/toolkit/', 'The agentic coding toolkit', 'Repos people use for agentic coding: Claude Code, Codex, opencode, pi, Spec Kit, Superpowers, Playwright MCP, DevTools MCP, hooks and benchmarks, with live GitHub data.', tk))
    return out

def posts(R, BL, d):
    a = lambda n, l=None: _a(R, n, l)
    P = []
    P.append(dict(slug='output-up-stability-down', kj='More output, paid for downstream', conf=HIGH, tags=['agents'],
      title='Agents raise output; the bill arrives in review and production',
      dek='METR measured a 19% slowdown that developers felt as a speedup. Telemetry from 22,000 developers shows throughput up a third, and incidents per PR up 243%.',
      bluf='Every large dataset shows more code shipped. Most also show the cost moving downstream: longer reviews, more incidents, worse stability. The practices that work all move checking earlier, so the agent finds its own mistakes before a person or a customer does.',
      body=f'''{stat('+33.7% / +242.7%', 'Task throughput against incidents per PR under high AI adoption, in Faros AI\'s 2026 telemetry of 22,000 developers. Median review time rose 441.5%.', 'Faros AI, 2026 (vendor)')}
<p>METR's randomized trial had 16 experienced open-source developers work on 246 issues in their own repos. Tasks took 19% longer with AI, yet afterwards the developers believed they had been about 20% faster (<a href="https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/">METR, Jul 2025</a>). The February 2026 follow-up got −18% and −4%. METR then said the design no longer works, because 30–50% of participants held back tasks they didn't want to do without AI (<a href="https://metr.org/blog/2026-02-24-uplift-update/">update</a>).</p>
<p>DORA 2025 (about 5,000 respondents) found AI adoption now correlates with throughput but still correlates <em>negatively</em> with delivery stability. Its framing: AI amplifies the strengths and weaknesses a team already has. CodeRabbit counted about 1.7x as many issues in AI co-authored PRs. Anthropic's study of its own engineers is the most positive: commits about 5x, and no difference in how often agent code was later reverted. It is a vendor studying itself, without randomization.</p>
{finding('What to do', '<p>Measure your own team instead of trusting how fast it feels. Then spend effort where the cost lands: verifiers the agent runs, smaller diffs, and reviewed plans. The <a href="/practices/agentic-practices/playbook/">playbook</a> has the specifics.</p>')}'''))
    P.append(dict(slug='the-verifier-is-the-practice', kj='The verifier is the practice', conf=MOD, tags=['agents'],
      title='The verifier is the practice',
      dek='A C compiler from 16 agents, a million lines with no hand-written code at OpenAI, a browser from Cursor\'s agents: each one rests on a check the agent runs itself.',
      bluf='Strip the big agentic success stories down and each has the same core: a fast, deterministic, quiet check that tells the agent when it is wrong. Prompts, plans and skills help at the margins. The verifier decides whether the work converges.',
      body=f'''{intercept('The task verifier is nearly perfect, otherwise Claude will solve the wrong problem.', 'Nicholas Carlini, <a href="https://www.anthropic.com/engineering/building-c-compiler">Building a C compiler with a team of parallel Claudes</a>, Anthropic, Feb 2026')}
<ul><li><strong>Anthropic's C compiler:</strong> 16 agents, about $20,000. Test output was kept terse and details went to log files, because noise eats context.</li>
<li><strong>OpenAI's harness team:</strong> custom lints whose error messages carry the fix, plus structural tests, DevTools and per-worktree observability the agent can query (<a href="https://openai.com/index/harness-engineering/">Feb 2026</a>).</li>
<li><strong>Anthropic's long-running harness:</strong> a feature only counts as passing after a browser check (<a href="https://www.anthropic.com/research/effective-harnesses-for-long-running-agents">Nov 2025</a>).</li>
<li><strong>Frameworks:</strong> Tidewave, Laravel Boost and Next.js's <code>/_next/mcp</code> give the agent the running app (<a href="/blog/agents-see-the-running-app/">dispatch</a>).</li></ul>
{finding('In Clojure', '<p>The REPL is this verifier, built into the language. Connected through {a("bhauman/clojure-mcp", "clojure-mcp")}, the agent evaluates each form against the running system before it writes it to a file.</p>')}
{caveat('<p>These are vendor and practitioner reports. No controlled study isolates the verifier, but no detailed success story goes without one.</p>')}'''))
    P.append(dict(slug='context-files-short-and-handwritten', kj='Context files help only when short and hand-written', conf=MOD, tags=['agents'],
      title='Context files: short, hand-written, or not at all',
      dek='ETH measured AGENTS.md files adding 20% to cost with no average gain. Developer-written ones helped a little; generated ones hurt.',
      bluf='Write the context file yourself, keep it under about 100 lines, and fill it with what the agent can\'t work out from the code. A generated architecture overview costs tokens and doesn\'t raise success.',
      body=f'''<p><a href="https://arxiv.org/abs/2602.11988">Gloaguen et al. (ETH Zurich, Feb 2026)</a> ran SWE-bench tasks with and without context files: no general improvement in success, over 20% more inference cost, and repository overviews "not helpful". Developer-written files averaged about +4% and LLM-generated ones about −3%. One of the authors still recommends writing an AGENTS.md "manually and targetedly". <a href="https://arxiv.org/abs/2601.20404">Lulla et al.</a> measured the efficiency side: with an AGENTS.md, runtime fell 28.6% and output tokens 16.6%, with similar completion.</p>
<p>The practitioners who publish their files agree. OpenAI's is about 100 lines used as "the table of contents"; HumanLayer's is under 60 lines, with the rule "Don't use <code>/init</code>". Vercel's 53%-to-100% result came from a compressed docs <em>index</em>, not a tour of the codebase (<a href="/blog/agents-md-beats-skills/">dispatch</a>).</p>
{finding('A template', '<p>Build and test commands. Where logs are. Conventions that differ from the language default. Traps. Pointers to deeper docs. Nothing the agent can read from the code.</p>')}'''))
    P.append(dict(slug='test-context-beats-tdd-ritual', kj='Give the agent the right tests, not a TDD ritual', conf=LOW, tags=['agents'],
      title='Telling agents to do TDD made things worse; giving them the right tests helped',
      dek='In the TDAD study, generic TDD instructions raised regressions to 9.94%. A map from code to its tests cut them 70%.',
      bluf='Point the agent at the tests that cover the code it is changing. Don\'t just tell it to work test-first. The evidence is thin (small samples, one study plus a small eval), but both lean the same way.',
      body=f'''<p><a href="https://arxiv.org/abs/2603.17973">TDAD</a> (Alonso et al., Mar 2026) gave agents a map from code to the tests that cover it, as a skill. On SWE-bench Verified, regressions fell from 6.08% to 1.82%. Generic TDD instructions without the map raised them to 9.94%, worse than no instructions at all ({a('pepealonso95/TDAD', 'code and data')}).</p>
<p>Birgitta Böckeler's own eval compared TDD, test-first and no tests and found "no clearly discernable difference", with TDD slightly worse. She has stopped telling agents to write tests first (<a href="https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html">martinfowler.com</a>).</p>
{caveat('<p>The samples are small (100 and 25 instances) and the models open-weight. Treat this as a hint. Tests are still the best verifier you have; the open question is how to instruct the agent, not whether to have tests.</p>')}'''))
    P.append(dict(slug='focused-skills-load-on-demand', kj='Focused skills help; generated ones don\'t', conf=MOD, tags=['agents'],
      title='Focused skills help; MCP versus CLI hardly matters',
      dek='SkillsBench: curated skills took pass rates from 33.9% to 50.5%. Small skills beat big bundles. A tool exposed through MCP and as a CLI scored the same.',
      bluf='Write a few small, curated skills for the procedures your agent needs now and then. Keep always-needed knowledge in the context file. Spend effort on tool design (terse output, a readable README) rather than on the protocol.',
      body=f'''<p><a href="https://arxiv.org/abs/2602.12670">SkillsBench</a> ran 87 tasks across 18 model and harness setups with deterministic checks. Curated skills raised pass rates by 16.6 points on average, and "Focused Skills with at most three modules outperform larger or exhaustive bundles" ({a('benchflow-ai/skillsbench', 'repo')}).</p>
<p>Mario Zechner exposed the same tool as an MCP server and as a CLI. Both reached 100% success at about the same cost: "largely a wash" (<a href="https://mariozechner.at/posts/2025-08-15-mcp-vs-cli/">Aug 2025</a>). His {a('earendil-works/pi', 'pi')} agent leaves out MCP entirely and reads each tool's README when it needs it.</p>
{caveat('<p>Skills only help when the agent uses them. Vercel found agents skipped an available skill 56% of the time (<a href="/blog/agents-md-beats-skills/">dispatch</a>).</p>')}'''))
    return P

def sources():
    S = lambda date, title, who, url, type, k, sum: dict(date=date, title=title, who=who, url=url, type=type, k=k, sum=sum)
    return [
     S('2025-07', 'Measuring the impact of early-2025 AI on experienced open-source developer productivity', 'METR', 'https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/', 'paper', ['agents'], 'RCT: tasks took 19% longer with AI; developers believed they were ~20% faster.'),
     S('2026-02', 'We are changing our developer productivity experiment design', 'METR', 'https://metr.org/blog/2026-02-24-uplift-update/', 'paper', ['agents'], 'Follow-up got −18% and −4%, then METR declared its design unreliable.'),
     S('2025-09', 'DORA State of AI-assisted Software Development 2025', 'Google DORA', 'https://dora.dev/dora-report-2025/', 'paper', ['agents'], '90% use AI; adoption still correlates negatively with delivery stability; AI as amplifier.'),
     S('2026', 'AI Engineering Report 2026: The Acceleration Whiplash', 'Faros AI', 'https://www.faros.ai/research/ai-acceleration-whiplash', 'paper', ['agents'], 'Telemetry, 22k devs: throughput +33.7%, incidents per PR +242.7%, review time +441.5%.'),
     S('2025-12', 'State of AI vs human code generation', 'CodeRabbit', 'https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report', 'paper', ['agents'], 'AI co-authored PRs carried ~1.7x the issues.'),
     S('2025-12', 'How AI is transforming work at Anthropic', 'Anthropic', 'https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic', 'paper', ['agents'], 'Survey of 132 engineers: self-reported +50%; 27% of the work wouldn\'t have been done.'),
     S('2026-10', 'How employment is changing at Anthropic', 'Anthropic', 'https://www.anthropic.com/research/employment-at-anthropic', 'paper', ['agents'], 'Commits ~5x after adoption; no difference in later reverts of agent code.'),
     S('2025', 'Stack Overflow Developer Survey 2025: AI', 'Stack Overflow', 'https://survey.stackoverflow.co/2025/ai', 'paper', ['agents'], '"Almost right, but not quite" is the top frustration (66%).'),
     S('2026-02', 'Evaluating AGENTS.md: are repository-level context files helpful?', 'Gloaguen et al., ETH Zurich', 'https://arxiv.org/abs/2602.11988', 'paper', ['agents'], 'No general success gain, +20% cost; hand-written +4%, generated −3%.'),
     S('2026-01', 'On the impact of AGENTS.md files on the efficiency of AI coding agents', 'Lulla et al.', 'https://arxiv.org/abs/2601.20404', 'paper', ['agents'], 'Runtime −28.6%, output tokens −16.6% with an AGENTS.md.'),
     S('2026-02', 'Harness engineering: leveraging Codex in an agent-first world', 'Ryan Lopopolo, OpenAI', 'https://openai.com/index/harness-engineering/', 'article', ['agents'], '~100-line AGENTS.md as a map; custom lints with fix-it messages; DevTools in the loop; 1M lines.'),
     S('2025-11', 'Writing a good CLAUDE.md', 'HumanLayer', 'https://www.humanlayer.dev/blog/writing-a-good-claude-md', 'article', ['agents'], 'Under 60 lines; never auto-generate; don\'t do a linter\'s job.'),
     S('2025-08', 'Advanced context engineering for coding agents', 'Dex Horthy, HumanLayer', 'https://www.humanlayer.dev/blog/advanced-context-engineering', 'article', ['agents'], 'Research, plan, implement; keep context 40–60% full.'),
     S('2025-08', 'Advanced context engineering for agents (talk)', 'Dex Horthy, YC', 'https://www.youtube.com/watch?v=IS_y40zY-hc', 'talk', ['agents', 'talk'], 'The talk version of frequent intentional compaction.'),
     S('2025-11', 'Effective harnesses for long-running agents', 'Justin Young, Anthropic', 'https://www.anthropic.com/research/effective-harnesses-for-long-running-agents', 'article', ['agents'], 'Feature list marked failing, progress file, one feature per session, browser checks.'),
     S('2026-02', 'Building a C compiler with a team of parallel Claudes', 'Nicholas Carlini, Anthropic', 'https://www.anthropic.com/engineering/building-c-compiler', 'article', ['agents'], '16 agents, ~$20k; the verifier must be nearly perfect; keep test output quiet.'),
     S('2026-01', 'Scaling long-running autonomous coding', 'Wilson Lin, Cursor', 'https://cursor.com/blog/scaling-agents', 'article', ['agents'], 'Planners plus workers built a browser in a week; flat coordination churned.'),
     S('2025-11', 'Code execution with MCP', 'Anthropic', 'https://www.anthropic.com/research/code-execution-with-mcp', 'article', ['agents'], 'Tools as code APIs: one workflow from 150k to 2k tokens.'),
     S('2025-08', 'MCP vs CLI: benchmarking tools for coding agents', 'Mario Zechner', 'https://mariozechner.at/posts/2025-08-15-mcp-vs-cli/', 'paper', ['agents'], '"Largely a wash": tool design matters more than protocol.'),
     S('2025-11', 'What I learned building an opinionated and minimal coding agent', 'Mario Zechner', 'https://mariozechner.at/posts/2025-11-30-pi-coding-agent/', 'article', ['agents'], 'pi: no MCP; tools documented in READMEs read on demand.'),
     S('2026-02', 'SkillsBench', 'Li et al.', 'https://arxiv.org/abs/2602.12670', 'paper', ['agents'], 'Curated skills 33.9% → 50.5%; focused skills beat exhaustive bundles.'),
     S('2025-10', 'Understanding spec-driven development: Kiro, spec-kit and Tessl', 'Birgitta Böckeler, Thoughtworks', 'https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html', 'article', ['agents'], '"I\'d rather review code than all these markdown files."'),
     S('2026-08', 'TDD inside the agent loop: theater or actual value?', 'Birgitta Böckeler, Thoughtworks', 'https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html', 'article', ['agents'], 'Small eval: no clear difference; TDD slightly worse.'),
     S('2026-03', 'TDAD: test-driven agentic development', 'Alonso, Yovine, Braberman', 'https://arxiv.org/abs/2603.17973', 'paper', ['agents'], 'Test map cut regressions 70%; generic TDD prompts raised them to 9.94%.'),
     S('2025', 'Augmented coding: beyond the vibes', 'Kent Beck', 'https://newsletter.kentbeck.com/p/augmented-coding-beyond-the-vibes', 'article', ['agents'], 'Strict red-green-refactor; watch for the agent deleting tests.'),
     S('2026-10', 'Red-green-refactor moves into the harness', 'Paul Hammant', 'https://paulhammant.com/2026/10/14/red-green-refactor-moves-into-the-harness/', 'article', ['agents'], 'Reddening checks: revert the code, confirm the new tests fail.'),
     S('2025-07', 'Context rot', 'Chroma', 'https://www.trychroma.com/research/context-rot', 'paper', ['agents'], 'Performance degrades with input length in every model tested.'),
     S('2025-10', 'Embracing the parallel coding agent lifestyle', 'Simon Willison', 'https://simonwillison.net/2025/Oct/5/parallel-coding-agents/', 'article', ['agents'], 'Parallel agents for research and small work; review is the bottleneck.'),
     S('2025-10', 'Just talk to it', 'Peter Steinberger', 'https://steipete.me/posts/just-talk-to-it', 'article', ['agents'], 'Many parallel sessions, conversational planning, little scaffolding.'),
     S('2025-06', 'Agentic coding recommendations', 'Armin Ronacher', 'https://lucumr.pocoo.org/2025/6/12/agentic-coding/', 'article', ['agents'], 'CLAUDE.md points to logs and services so the agent can check itself.'),
     S('2026-01', 'Claude Code workflow thread', 'Boris Cherny', 'https://x.com/bcherny/status/2007179861115511237', 'article', ['agents'], 'Plan mode first; a verification loop "will 2-3x the quality" (estimate).'),
     S('2025', 'Ralph Wiggum as a "software engineer"', 'Geoffrey Huntley', 'https://ghuntley.com/ralph/', 'article', ['agents'], 'One task per loop, forever, with the AGENTS file as memory.'),
     S('2025-12', 'Agent Skills open standard', 'agentskills.io', 'https://agentskills.io/', 'doc', ['agents'], 'The open skill format, loaded by progressive disclosure.'),
    ]
