# China Semiconductor Investment Dashboard

China semiconductor market learning dashboard with real-time data/news aggregation and GitHub-ready automation.

## Public Links

- Website: [https://cxy2696.github.io/semiconductor/](https://cxy2696.github.io/semiconductor/)

## Key Features

- Auto refresh every hour via workflow schedule (plus push-triggered deploy on main dashboard code changes)
- Latest-news-first rendering (freshest records prioritized)
- Runtime payload refresh via `latest_data.json` (data/news/figures/info all re-rendered)
- Top 6 market-cap K-line cards with runtime refresh
- Industry knowledge/source blocks are refreshed from direct website scraping payloads (non-API)
- Quick-search now drives all major modules (cards/charts/table/news/K-line/industry tips)
- Decision-support module highlights score/valuation/momentum/concentration signals for faster stock shortlisting
- Multi-page course modules with top menu (`index`, `overview`, `charts`, `knowledge`, `risk-news`, `data-center`)
- GitHub Actions schedule for continuous 24/7 refresh attempt every hour
- Workflow includes artifact validation checks before GitHub Pages deploy (guards unattended runs)
- GitHub Pages output in `docs/index.html`
- Optimized CI pipeline with dependency cache (`actions/setup-python` pip cache)

## Repository Layout

- `china_semiconductor_report.py`: main generator (data/news fetch, scoring, HTML + payload build)
- `config/company_metadata.py`: tracked company universe (source of truth)
- `html_template.html`: HTML template structure and data bindings
- `app.js` / `dashboard.js` / `styles.css`: front-end source files
- `scripts/build_dashboard.py`: canonical dashboard build entrypoint
- `scripts/refresh_dashboard.sh`: canonical refresh entrypoint (loop or `--once`)
- `.github/workflows/update-dashboard.yml`: scheduled hourly auto-refresh workflow
- `docs/index.html`: GitHub Pages entrypoint (generated)
- `docs/overview.html` / `docs/charts.html` / `docs/knowledge.html` / `docs/risk-news.html` / `docs/data-center.html`: generated course module pages
- `docs/latest_data.json`: live runtime payload used by auto-refresh
- `docs/app.js` / `docs/dashboard.js` / `docs/styles.css`: static assets for GitHub Pages

## Local Setup (Recommended)

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
bash ./scripts/refresh_dashboard.sh --once
```

Generated outputs:

- `中国半导体行业报告.xlsx` (data source export)
- `中国半导体行业报告.html` (local report)
- `docs/index.html` (GitHub Pages report)

## Local 24/7 Refresh (Every Hour)

```bash
bash ./scripts/refresh_dashboard.sh
```

This loop regenerates data/news/charts every 3600 seconds by default.  
The report page itself also auto-refreshes every hour.

Optional custom interval:

```bash
INTERVAL_SECONDS=1800 bash ./scripts/refresh_dashboard.sh
```

## GitHub 24/7 Refresh (Scheduled)

Workflow: `.github/workflows/update-dashboard.yml` (fully automatic, no manual refresh needed)

- Trigger:
  - hourly schedule: `0 * * * *`
  - push to `main` when dashboard/build/workflow files change
  - manual dispatch
- Action: run `scripts/refresh_dashboard.sh --once`, retry transient failures automatically, validate `docs` artifacts, then deploy to GitHub Pages as a workflow artifact (no bot commit)
- Concurrency policy: queued execution (`cancel-in-progress: false`) to avoid canceling long data-refresh runs

After pushing this repository:

1. Open repository settings
2. Enable GitHub Pages
3. Source: `GitHub Actions`


## Scoring Logic Overview

- `invest_score` combines size/liquidity, valuation pressure, short-term momentum, and strategic track weighting.
- Candidate picks default to `invest_score >= 70`, with grades mapped to `A/B/C/D`.
- Risk cards use a separate adjustable weighting model (volatility/valuation/liquidity/segment/size) for follow-up review.
- All outputs are for research only and do not constitute investment advice.

Project owner profile: [cxy2696](https://github.com/cxy2696)
