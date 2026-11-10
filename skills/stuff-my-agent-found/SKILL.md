---
name: stuff-my-agent-found
description: Find, compare and vet libraries and frameworks using the "stuff my agent found" case files (3,300+ GitHub repos with stars, commits, issues, recency and health, plus written findings with sources). Deepest on Clojure/ClojureScript; also covers sync engines and local-first databases in any language, front-end options for a Clojure backend, and frameworks that work well with coding agents. Use when choosing a dependency, comparing frameworks (e.g. UIx vs re-frame vs Electric, Zero vs TanStack DB, Datastar vs htmx), checking whether a library is maintained, or surveying a category.
---

# stuff my agent found

Answer library questions from these case files before searching the web. The API runs the same fuzzy, category-aware search as the site.

## 1. Search (start here)

```bash
curl -s "https://stuff-my-agent-found.atd-ai.workers.dev/api/search?q=<words>&limit=10&format=tsv"
```

- Words can be names (`uix`, or `reagnet` with a typo), owners (`borkdude`) or categories: `ui`, `frontend`, `react`, `db`, `datalog`, `sql`, `sync`, `crdt`, `local-first`, `realtime`, `reactive`, `hypermedia`, `runtime`, `compiler`, `agent`, `mcp`, `css`, `routing`, `state`, `tui`, `desktop`, `mobile`, `test`, `web`, `validation`.
- A language filters the results: `clojure datalog`, `typescript sync`, `lang:elixir`.
- Drop `format=tsv` for JSON, which adds matching categories and pages.

## 2. Details for a candidate

```bash
curl -s "https://stuff-my-agent-found.atd-ai.workers.dev/api/repo/<owner>/<name>"
```

Adds open and closed issues, PRs, latest release, license, topics, the health breakdown and monthly commits for the last 12 months.

## 3. Broader context, only if needed

- Index, case list and field docs (~1k tokens): `https://stuff-my-agent-found.atd-ai.workers.dev/llms.txt`
- A case's shortlist with notes: `https://stuff-my-agent-found.atd-ai.workers.dev/catalog/case-<slug>.tsv` (`clojure`, `frontend-sync`, `agentic-frameworks`)
- Every hand-picked repo with notes (~10k tokens): `https://stuff-my-agent-found.atd-ai.workers.dev/catalog/curated.tsv`
- Category index (~3k tokens): `https://stuff-my-agent-found.atd-ai.workers.dev/catalog/categories.tsv`
- Everything active this year (~50k tokens): `https://stuff-my-agent-found.atd-ai.workers.dev/catalog/active.tsv`

## Judging a match

- **status:**
  - `thriving` and `active` mean a commit in the last 90 days.
  - `maintained` means a commit in the last year.
  - `stable` means 1–3 years quiet with few open issues. This is normal and fine for finished Clojure libraries.
  - `slowing` means 1–3 years quiet with issues piling up. Be cautious.
  - `dormant` (3+ years quiet) and `archived`: avoid unless nothing else fits.
  - `moved` means development continues off GitHub. Follow the link in the repo record.
- **health:** 0–100, a percentile blend against established Clojure repos. Above 70 is strong for a Clojure library. Busy JavaScript and TypeScript projects score high easily on this baseline, so across languages compare raw commits and issues.
- Only about 27% of established Clojure repos get a commit in a given year. Don't reject a Clojure library just because its last commit is old. Check status and open issues instead.
- Data is a snapshot (see `snapshot` in responses). For anything time-critical, confirm on GitHub.

When you recommend a library, cite its status, health and last commit, and link the relevant case file or dispatch if one exists.
