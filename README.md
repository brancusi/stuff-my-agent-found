# stuff my agent found

Open case files on the tech I'm researching, built with an AI agent. Each case starts from a real decision. The agent maps the field, measures the repos from the GitHub API, reads the primary sources, and files its findings with confidence levels and citations.

**Live site:** https://stuff-my-agent-found.atd-ai.workers.dev

## Four sections

| Section | What it holds | Case files |
| --- | --- | --- |
| [Projects](https://stuff-my-agent-found.atd-ai.workers.dev/projects/) | Deep dives on one project: what it is, who builds it, how people use it | [004](https://stuff-my-agent-found.atd-ai.workers.dev/projects/datastar/) Datastar, and Stardust, the database behind it |
| [Approaches](https://stuff-my-agent-found.atd-ai.workers.dev/approaches/) | Ways to build something, compared across projects and languages | [001](https://stuff-my-agent-found.atd-ai.workers.dev/approaches/clojure/) The Clojure ecosystem (filed) · [002](https://stuff-my-agent-found.atd-ai.workers.dev/approaches/frontend-sync/) A front end for a Clojure backend, with live data sync |
| [Repos](https://stuff-my-agent-found.atd-ai.workers.dev/repos/) | The library: every repo from every case, measured from the GitHub API, searchable by language and by API | 3,400+ repos in 40+ languages |
| [Practices](https://stuff-my-agent-found.atd-ai.workers.dev/practices/) | Agentic coding practices that work, and the evidence | [003](https://stuff-my-agent-found.atd-ai.workers.dev/practices/agentic-frameworks/) Frameworks agents work well in · [005](https://stuff-my-agent-found.atd-ai.workers.dev/practices/agentic-practices/) Agentic coding practices that work |

Every repo from every case sits in one index, and language is a filter. Press `⌘K` or `/` on any page for fuzzy search (type a language like `clojure` or `lang:typescript` to filter), `?` for keyboard shortcuts, and `g 1`–`g 4` to jump between sections.

- **Dispatches:** every finding written up with data and sources, with an Atom feed.
- **For agents:** [`/llms.txt`](https://stuff-my-agent-found.atd-ai.workers.dev/llms.txt), a search API (`/api/search?q=`), per-case TSV shortlists, and a Claude Code skill in [`skills/stuff-my-agent-found`](skills/stuff-my-agent-found/SKILL.md). See [`/for-agents/`](https://stuff-my-agent-found.atd-ai.workers.dev/for-agents/).

## Health is calibrated to Clojure

Clojure has the deepest coverage: every Clojure repo with 50+ stars. Only about 27% of those see a commit in a given year, and most are finished rather than abandoned, so the health score ranks repos against that baseline. Other languages are scored on the same Clojure baseline, so busy JavaScript and TypeScript projects score high easily. Across languages, compare raw commits and issues. See [`/method/`](https://stuff-my-agent-found.atd-ai.workers.dev/method/).

## Adding a case

1. Add the case to `CASES` in `scripts/cases.py` (number, slug, `kind` = `projects`, `approaches` or `practices`, question, tabs under `/<kind>/<slug>/`).
2. List its repos in `data/cases/<slug>.json` as `[owner/repo, category, note]`.
3. Measure them: `scripts/enrich.py` and `scripts/monthly.py` (see below), merged into `data/enriched_cases.json` and `data/monthly.json`.
4. Write `scripts/case_<slug>.py` with `pages(memo, R, d)`, `posts(R, BL, d)` and `sources()`.
5. `python3 scripts/build.py && python3 scripts/site.py`.

## Pipeline

Requires Python 3.12+ and an authenticated [`gh`](https://cli.github.com/) CLI.

| step | script | output |
| --- | --- | --- |
| 1. Discover Clojure repos via GitHub search | `scripts/discover.py` | `data/discovered.json` |
| 2. Fetch metrics (GraphQL) | `scripts/enrich.py <names.json> <out.json>` | `data/enriched_*.json` |
| 3. Monthly commit counts | `scripts/monthly.py <names.json> <out.json>` | `data/monthly.json` |
| 4. Parse awesome-clojure | `scripts/parse_awesome.py` | `data/awesome/entries.json` |
| 5. Merge, baseline, health scores, case membership | `scripts/build.py` | `data/dataset.json` |
| 6. Build the static site | `scripts/site.py` | `dist/` |
| 7. Deploy to Cloudflare Workers (assets + `/api` Worker in `src/worker.js`) | `scripts/deploy.sh` | live site |

Case 001's curated projects are in `data/curated.json` and its writing in `scripts/content.py`. Later cases keep their repos in `data/cases/` and their writing in `scripts/case_<slug>.py`. Styles and client code are in `site/assets/`.

## Contributing

Corrections and missing projects are welcome. Open an issue or PR that edits a case's repo list or writing.

### Privacy scrub

Every commit runs a privacy scrub. Turn it on once per clone:

```sh
git config core.hooksPath .githooks
```

The hooks run `scripts/privacy_scrub.py`:

- `pre-commit` scans the staged lines.
- `commit-msg` scans the commit message.
- `pre-push` scans every tracked file.

A hook blocks the commit or push when it finds any of these:

- A string from your local denylist. The denylist lives in `.git/privacy-denylist` and `~/.config/privacy-scrub/denylist`, and is never committed.
- An email address that isn't a noreply address.
- A home-directory path.
- An API token or a private key.
- A Cloudflare account id.
- An author email that isn't a GitHub noreply address.

Your global git email is added to the denylist automatically. To scan the whole history, run `python3 scripts/privacy_scrub.py --history`. To let a false positive through, add `privacy-scrub: allow` to that line.

## License

Code: MIT. The data is derived from the public GitHub API and the sources listed on the site.
