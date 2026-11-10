# Clojure Radar

An open dossier on the Clojure ecosystem: front-end frameworks, data sync, novel frameworks, runtimes and agentic coding, with GitHub health data for 3,000+ repositories.

**Live site:** https://clojure-radar.atd-ai.workers.dev

- **Brief:** a radar of 137 curated projects, the key findings, and what "normal" activity looks like in Clojure.
- **Sectors:** front-end, data sync, novel frameworks, runtimes. Each has hand-written notes and live tables.
- **Why Clojure for agentic coding:** the arguments, evidence, real-world wins and counterpoints.
- **Blog:** every finding written up as a dispatch, with an Atom feed.
- **Explore:** search and sort every repo by stars, commits, issues, recency and health.

Snapshot: 2026-11-10. Window: the last 12 months.

## Why "health" is calibrated to Clojure

Only about 27% of established Clojure repos (50+ stars) see a commit in a given year, and the median repo has been quiet for about 4.5 years. Most of them are finished, not abandoned. The health score ranks each repo against that baseline instead of against npm norms. See [`/method/`](https://clojure-radar.atd-ai.workers.dev/method/).

## Pipeline

Requires Python 3.12+ and an authenticated [`gh`](https://cli.github.com/) CLI.

| step | script | output |
| --- | --- | --- |
| 1. Discover repos via GitHub search | `scripts/discover.py` | `data/discovered.json` |
| 2. Fetch metrics (GraphQL) | `scripts/enrich.py <names.json> <out.json>` | `data/enriched_*.json` |
| 3. Monthly commit counts | `scripts/monthly.py <names.json> <out.json>` | `data/monthly.json` |
| 4. Parse awesome-clojure | `scripts/parse_awesome.py` | `data/awesome/entries.json` |
| 5. Merge, baseline, health scores | `scripts/build.py` | `data/dataset.json` |
| 6. Build the static site | `scripts/site.py` | `dist/` |
| 7. Deploy to Cloudflare Workers | `scripts/deploy.sh` | live site |

Curated projects and their notes are in `data/curated.json`. Editorial content (dispatches, the why-clojure brief, sources) is in `scripts/content.py`. Styles and client code are in `site/assets/`.

## Contributing

Corrections and missing projects are welcome. Open an issue or PR that edits `data/curated.json` (format: `[owner/repo, category, note]`) or `scripts/content.py`.

## License

Code: MIT. The data is derived from the public GitHub API and the sources listed on the site.
