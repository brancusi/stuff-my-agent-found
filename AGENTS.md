# AGENTS.md

Guide for coding agents working in this repo or using its data.

## Using the data (no checkout needed)

- `https://clojure-radar.atd-ai.workers.dev/llms.txt`: index, field docs and links.
- `https://clojure-radar.atd-ai.workers.dev/api/search?q=<words>&format=tsv`: fuzzy, category-aware search.
- `https://clojure-radar.atd-ai.workers.dev/api/repo/<owner>/<name>`: one repo in full.
- `catalog/*.tsv` on the site: compact context files (curated ~6k tokens, active ~43k, all ~105k).
- Claude Code skill: copy `skills/clojure-radar/` into your project's `.claude/skills/`.

## Working on this repo

- Python 3.12+ and an authenticated `gh` are needed for the data pipeline. Node is needed for `wrangler`.
- Pipeline: `scripts/discover.py` → `enrich.py` → `monthly.py` → `build.py` (writes `data/dataset.json`) → `site.py` (writes `dist/`).
- Editorial content lives in `scripts/content.py`. Curated projects are in `data/curated.json` as `[owner/repo, category, note]`.
- Front end: `site/assets/radar.css`, `radar.js`, and `search-core.js` (shared with the Worker).
- API Worker: `src/worker.js`. Static assets are served from `dist/`, and only `/api/*` runs the Worker.
- Local preview: `python3 scripts/site.py && npx wrangler dev`. Deploy: `scripts/deploy.sh` (set `CLOUDFLARE_ACCOUNT_ID` if your login has several accounts).
- Keep numbers in prose generated from the dataset (helpers in `content.py`). Don't hard-code figures.
