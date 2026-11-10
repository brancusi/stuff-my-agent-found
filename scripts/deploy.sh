#!/usr/bin/env bash
# Build the site and deploy it to Cloudflare Workers (static assets).
# Requires: python3.12+, node, `npx wrangler login`, and CLOUDFLARE_ACCOUNT_ID if your login has several accounts.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/site.py
npx --yes wrangler@latest deploy
