# China Semiconductor Dashboard

China semiconductor market dashboard with real-time data/news aggregation and GitHub-ready automation.

## Public Links

- Website: [https://cxy2696.github.io/semiconductor/](https://cxy2696.github.io/semiconductor/)
- Repository: [https://github.com/cxy2696/semiconductor](https://github.com/cxy2696/semiconductor)

## Key Features

- Auto refresh every 10 minutes (default in UI)
- Immediate refresh button (`立即刷新 / Refresh now`)
- Locale + timezone profiles:
  - Chinese + China time (`zh-CN` + `Asia/Shanghai`) default
  - English + EST/EDT (`en-US` + `America/New_York`)
  - German + CET/CEST (`de-DE` + `Europe/Berlin`)
- Latest-news-first rendering (freshest records prioritized)
- Runtime payload refresh via `latest_data.json` (data/news/figures/info all re-rendered)
- Top 6 market-cap K-line cards with runtime refresh
- Industry knowledge/source blocks are refreshed from scraping payloads
- GitHub Actions schedule for continuous 24/7 refresh attempt every 10 minutes
- GitHub Pages output in `docs/index.html`
- Optimized CI pipeline with dependency cache (`actions/setup-python` pip cache)

## Repository Layout

- `china_semiconductor_report.py`: main generator (data/news fetch, scoring, HTML + payload build)
- `config/company_metadata.py`: tracked company universe (source of truth)
- `html_template.html`: HTML template structure and data bindings
- `app.js` / `dashboard.js` / `styles.css`: front-end source files
- `scripts/build_dashboard.py`: canonical dashboard build entrypoint
- `scripts/refresh_dashboard.sh`: canonical refresh entrypoint (loop or `--once`)
- `.github/workflows/update-dashboard.yml`: scheduled 10-minute auto-refresh workflow
- `docs/index.html`: GitHub Pages entrypoint (generated)
- `docs/latest_data.json`: live runtime payload used by auto-refresh
- `docs/app.js` / `docs/dashboard.js` / `docs/styles.css`: static assets for GitHub Pages

## Local Setup

```bash
python -m pip install -r requirements.txt
python china_semiconductor_report.py
```

Generated outputs:

- `中国半导体行业报告.xlsx` (data source export)
- `中国半导体行业报告.html` (local report)
- `docs/index.html` (GitHub Pages report)

## Local 24/7 Refresh (Every 10 Minutes)

```bash
bash ./scripts/refresh_dashboard.sh
```

This loop regenerates data/news/charts every 600 seconds.  
The report page itself also auto-refreshes every 10 minutes and supports immediate refresh.

## GitHub 24/7 Refresh (Scheduled)

Workflow: `.github/workflows/update-dashboard.yml` (fully automatic, no manual refresh needed)

- Trigger: `*/10 * * * *` plus manual dispatch
- Action: run `scripts/refresh_dashboard.sh --once`, retry transient failures automatically, update `docs` artifacts, and commit with GitHub Actions bot
- Concurrency policy: queued execution (`cancel-in-progress: false`) to avoid canceling long data-refresh runs

After pushing this repository:

1. Open repository settings
2. Enable GitHub Pages
3. Source: `Deploy from a branch`
4. Branch: default branch, folder `/docs`

Your dashboard URL will be:

`https://<your-github-username>.github.io/<repo-name>/`

## Notes

- GitHub scheduled workflows run continuously and automatically every 10 minutes. Exact second-level timing is best-effort on GitHub-hosted runners.
- If one refresh cycle exceeds 10 minutes, the next run is queued (not canceled) to keep updates reliable.
- Runtime refresh failures no longer force hard page reload; current data stays visible and the next cycle retries automatically.
- Data freshness depends on upstream data/news source availability.
- Auto-refresh updates data, news, candidate picks, industry knowledge blocks, and risk panels from the latest generated payload.
- Front-end is implemented with JavaScript and optimized for mobile/tablet/desktop responsive behavior.

Project owner profile: [cxy2696](https://github.com/cxy2696)
