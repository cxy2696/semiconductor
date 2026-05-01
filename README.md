# China Semiconductor Investment Dashboard

China semiconductor market learning dashboard with real-time data/news aggregation, GitHub Pages automation, and a native iOS app scaffold.

## Public Links

- Website: [https://cxy2696.github.io/semiconductor/](https://cxy2696.github.io/semiconductor/)
- Repository: [https://github.com/cxy2696/semiconductor](https://github.com/cxy2696/semiconductor)

## Key Features

- Auto refresh at China market times (09:30, 12:00, 15:05 CST) via workflow schedule, plus push-triggered deploy on main dashboard code changes
- Runtime payload refresh via `latest_data.json` (data/news/charts/info all re-rendered)
- Decision-support module for score/valuation/momentum/concentration
- New modules: 涨停板观察 + 全球对比观察
- Industry knowledge retrieval combines Chinese + English accessible sources
- Multi-page module navigation (`index`, `overview`, `charts`, `knowledge`, `risk-news`, `data-center`)
- GitHub Pages artifact-based deployment (no generated docs auto-commit)

## Repository Layout

- `china_semiconductor_report.py`: main generator (data/news fetch, scoring, HTML + payload build)
- `config/company_metadata.py`: tracked company universe (source of truth)
- `html_template.html`: HTML template structure and data bindings
- `app.js` / `dashboard.js` / `styles.css`: front-end source files
- `scripts/build_dashboard.py`: canonical dashboard build entrypoint
- `scripts/refresh_dashboard.sh`: canonical refresh entrypoint (loop or `--once`)
- `.github/workflows/update-dashboard.yml`: scheduled + push-triggered GitHub Pages deployment workflow
- `docs/`: generated GitHub Pages artifacts (`index`, module pages, JS/CSS, `latest_data.json`)
- `ios/`: native SwiftUI iPhone app (MVP scaffold and feature modules)

## Local Setup (Web Dashboard)

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

## Local Auto Refresh

```bash
bash ./scripts/refresh_dashboard.sh
```

Default loop interval is `43200` seconds (12h).

Optional custom interval:

```bash
INTERVAL_SECONDS=3600 bash ./scripts/refresh_dashboard.sh
```

## GitHub 24/7 Refresh (Scheduled + Push)

Workflow: `.github/workflows/update-dashboard.yml`

- Trigger:
  - China-time schedule:
    - `09:30 CST` (`30 1 * * *` UTC)
    - `12:00 CST` (`0 4 * * *` UTC)
    - `15:05 CST` (`5 7 * * *` UTC)
  - push to `main` when dashboard/build/workflow files change
  - manual dispatch
- Action:
  - run `scripts/refresh_dashboard.sh --once`
  - validate generated `docs` artifacts
  - deploy to GitHub Pages as workflow artifact
- Concurrency policy: queued execution (`cancel-in-progress: false`)

Pages setup:

1. Open repository settings
2. Enable GitHub Pages
3. Source: `GitHub Actions`

## Native iOS App (SwiftUI, iPhone)

The repo includes a native iOS app scaffold under `ios/`, consuming:

- Remote source: `https://cxy2696.github.io/semiconductor/latest_data.json`
- Tabs: Home, Global Compare, Market, News, Settings
- Features: decision support, limit-up board, global comparison
- Data strategy: remote fetch + local cache fallback

### Generate/Open the Xcode project

```bash
brew install xcodegen
xcodegen generate --spec ios/project.yml
open ios/SemiconductorApp.xcodeproj
```

Notes:

- Building/running requires full Xcode (not only Command Line Tools).
- Update app icons in `ios/SemiconductorApp/Resources/Assets.xcassets/AppIcon.appiconset`.
- Use [`ios/IOS_RUN_CHECKLIST.md`](ios/IOS_RUN_CHECKLIST.md) for simulator/device verification.
- Use [`ios/IOS_SIGNING_TEMPLATE.md`](ios/IOS_SIGNING_TEMPLATE.md) for real-device signing setup template.
- Use [`ios/IOS_TESTFLIGHT_RELEASE_CHECKLIST.md`](ios/IOS_TESTFLIGHT_RELEASE_CHECKLIST.md) before first TestFlight release.
- Use [`ios/APPLE_STORE_SUBMISSION_GUIDE.md`](ios/APPLE_STORE_SUBMISSION_GUIDE.md) for end-to-end App Store submission steps.

## Scoring Logic Overview

- `invest_score` combines size/liquidity, valuation pressure, short-term momentum, and strategic track weighting.
- Candidate picks default to `invest_score >= 70`, with grades mapped to `A/B/C/D`.
- Risk cards use a separate adjustable weighting model (volatility/valuation/liquidity/segment/size).
- All outputs are for research only and do not constitute investment advice.

Project owner profile: [cxy2696](https://github.com/cxy2696) 自己试着玩的
