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
- GitHub Actions schedule for continuous 24/7 refresh attempt every 10 minutes
- GitHub Pages output in `docs/index.html`
- Optimized CI pipeline with dependency cache (`actions/setup-python` pip cache)

## Repository Layout

- `china_semiconductor_report.py`: data + news fetch, scoring, chart payload generation, HTML build
- `html_template.html`: HTML template structure and data bindings
- `styles.css`: external stylesheet for website layout and visual format
- `app.js`: front-end JavaScript enhancement layer (mobile/tablet/desktop UX)
- `dashboard.js`: externalized dashboard runtime logic (filters/charts/news/table/refresh)
- `company_metadata`: tracked company universe
- `refresh_report_every_5m.sh`: shared refresh entrypoint (local loop + GitHub bot single-run mode)
- `requirements.txt`: Python dependencies
- `.github/workflows/update-dashboard.yml`: scheduled auto-refresh workflow
- `docs/index.html`: GitHub Pages entrypoint (generated/updated by script)
- `docs/styles.css`: stylesheet served by GitHub Pages
- `docs/app.js`: front-end JavaScript served by GitHub Pages
- `docs/dashboard.js`: dashboard runtime logic served by GitHub Pages
- `docs/latest_data.json`: live runtime payload used by auto-refresh

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
./refresh_report_every_5m.sh
```

This loop regenerates data/news/charts every 600 seconds.  
The report page itself also auto-refreshes every 10 minutes and supports immediate refresh.

## GitHub 24/7 Refresh (Scheduled)

Workflow: `.github/workflows/update-dashboard.yml`

- Trigger: `*/10 * * * *` plus manual dispatch
- Action: run `refresh_report_every_5m.sh --once`, update `docs/index.html`, commit changes automatically with GitHub Actions bot
- Concurrency policy: queued execution (`cancel-in-progress: false`) to avoid canceling long data-refresh runs

After pushing this repository:

1. Open repository settings
2. Enable GitHub Pages
3. Source: `Deploy from a branch`
4. Branch: default branch, folder `/docs`

Your dashboard URL will be:

`https://<your-github-username>.github.io/<repo-name>/`

## Notes

- GitHub scheduled workflows run continuously but are best-effort; exact second-level timing is not guaranteed by GitHub.
- If one refresh cycle exceeds 10 minutes, the next run is queued (not canceled) to keep updates reliable.
- Runtime refresh failures no longer force hard page reload; current data stays visible and the next cycle retries automatically.
- Data freshness depends on upstream data/news source availability.
- Front-end is implemented with JavaScript and optimized for mobile/tablet/desktop responsive behavior.

Project owner profile: [cxy2696](https://github.com/cxy2696)
