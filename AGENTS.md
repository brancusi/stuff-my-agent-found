# AGENTS.md

Guide for coding agents working in this repo or using its data.

## Using the data (no checkout needed)

- `https://stuff-my-agent-found.atd-ai.workers.dev/llms.txt`: index, field docs and links.
- `https://stuff-my-agent-found.atd-ai.workers.dev/api/search?q=<words>&format=tsv`: fuzzy, category-aware search.
- `https://stuff-my-agent-found.atd-ai.workers.dev/api/repo/<owner>/<name>`: one repo in full.
- `catalog/*.tsv` on the site: compact context files (per-case shortlists `case-<slug>.tsv`, curated ~10k tokens, active ~50k, all ~120k).
- Claude Code skill: copy `skills/stuff-my-agent-found/` into your project's `.claude/skills/`.

## Working on this repo

- Python 3.12+ and an authenticated `gh` are needed for the data pipeline. Node is needed for `wrangler`.
- Pipeline: `scripts/discover.py` → `enrich.py` → `monthly.py` → `build.py` (writes `data/dataset.json`) → `site.py` (writes `dist/`).
- The site has four sections (projects, approaches, repos, practices), defined in `SECTIONS` in `scripts/cases.py`. Case files are registered there too, each with a `kind` that puts it in a section and URLs under `/<kind>/<slug>/`. Case 001 (Clojure) has its writing in `scripts/content.py` and its curated projects in `data/curated.json`. Later cases have their repos in `data/cases/<slug>.json` and their writing in `scripts/case_<slug>.py` (`pages`, `posts`, `sources`). All entries are `[owner/repo, category, note]`.
- Repos are measured for any language. Health is always ranked against the Clojure baseline; say so when comparing across languages.
- Front end: `site/assets/radar.css`, `radar.js`, and `search-core.js` (shared with the Worker).
- API Worker: `src/worker.js`. Static assets are served from `dist/`, and only `/api/*` runs the Worker.
- Local preview: `python3 scripts/site.py && npx wrangler dev`. Deploy: `scripts/deploy.sh` (set `CLOUDFLARE_ACCOUNT_ID` if your login has several accounts).
- Keep numbers in prose generated from the dataset (helpers in `content.py`). Don't hard-code figures.
