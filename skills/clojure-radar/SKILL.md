---
name: clojure-radar
description: Find, compare and vet Clojure/ClojureScript libraries using the Clojure Radar snapshot (3,000+ repos with stars, commits, issues, recency and Clojure-calibrated health). Use when choosing a Clojure dependency, comparing frameworks (e.g. Reagent vs UIx vs Replicant, Datahike vs Datalevin), checking whether a library is maintained, or surveying a category (UI, databases, sync, runtimes, agent tooling).
---

# Clojure Radar

Answer library questions from the radar before searching the web. The API runs the same fuzzy, category-aware search as the site.

## 1. Search (start here)

```bash
curl -s "https://clojure-radar.atd-ai.workers.dev/api/search?q=<words>&limit=10&format=tsv"
```

- Words can be names (`uix`, `reagnet` with a typo is fine), owners (`borkdude`) or categories: `ui`, `frontend`, `react`, `db`, `datalog`, `sql`, `sync`, `realtime`, `reactive`, `runtime`, `compiler`, `agent`, `mcp`, `css`, `routing`, `state`, `tui`, `desktop`, `mobile`, `test`, `web`, `http`, `hypermedia`, `validation`.
- Drop `format=tsv` for JSON, which adds matching categories and pages.

## 2. Details for a candidate

```bash
curl -s "https://clojure-radar.atd-ai.workers.dev/api/repo/<owner>/<name>"
```

Adds open and closed issues, PRs, latest release, license, topics, the health breakdown and monthly commits for the last 12 months.

## 3. Broader context, only if needed

- Curated shortlist with notes (~6k tokens): `https://clojure-radar.atd-ai.workers.dev/catalog/curated.tsv`
- Category index (~3k tokens): `https://clojure-radar.atd-ai.workers.dev/catalog/categories.tsv`
- Everything active this year (~43k tokens): `https://clojure-radar.atd-ai.workers.dev/catalog/active.tsv`
- Index and field docs: `https://clojure-radar.atd-ai.workers.dev/llms.txt`

## Judging a match

- **status:**
  - `thriving` and `active` mean a commit in the last 90 days.
  - `maintained` means a commit in the last year.
  - `stable` means 1–3 years quiet with few open issues. This is normal and fine for finished Clojure libraries.
  - `slowing` means 1–3 years quiet with issues piling up. Be cautious.
  - `dormant` (3+ years quiet) and `archived`: avoid unless nothing else fits.
  - `moved` means development continues off GitHub. Follow the link in the repo record.
- **health:** 0–100, a percentile blend against established Clojure repos. Above 70 is strong, and 45–70 is typical of a maintained library.
- Only about 27% of established Clojure repos get a commit in a given year. Don't reject a library just because its last commit is old. Check status and open issues instead.
- Data is a snapshot (see `snapshot` in responses). For anything time-critical, confirm on GitHub.

When you recommend a library, cite its status, health and last commit from the radar.
