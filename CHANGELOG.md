# Changelog

All notable changes to this project are documented here. The format follows
Keep a Changelog, and the project uses semantic versioning.

## [2.0.0] — 2026-11-11

### Added

- Trilingual site (Simplified Chinese, English, Japanese) with per-locale URLs,
  hreflang alternates and a language switcher that preserves the current page.
- Global universe: 124 companies across mainland China, Hong Kong, Taiwan, the
  US, Japan, Korea and Europe, classified into 8 value-chain stages.
- Knowledge base: 9 long-form topics × 3 languages and a 52-term trilingual
  glossary with search and category filters.
- Documented research methodology: peer-normalised factors, weights,
  data-coverage scoring, risk flags, market-state thresholds and screen rules.
- Company profile pages with 52-week range, factor breakdown and peer table.
- Snapshot-based build with stale-data fallback, quote coverage metrics and
  provenance fields.
- CI: data-contract validation, artifact validation and pytest suite.
- Documentation set: PRODUCT, ARCHITECTURE, DATA, METHODOLOGY, OPERATIONS,
  ROADMAP, CONTRIBUTING.

### Changed

- Replaced the single 1,000-line generator with the `semcore` package and a CLI
  (`fetch`, `build`, `refresh`, `validate`, `serve`, `info`).
- Replaced Tailwind and Plotly CDNs with a self-contained design system and
  build-time SVG charts.
- Replaced monthly/daily scraping of encyclopedia paragraphs with curated,
  versioned knowledge content.
- Replaced the undisclosed "investment score" with a published research
  priority score plus explicit data coverage.
- Company metadata moved to `data/universe.csv` and validated against
  `data/taxonomy.json`.

### Removed

- German locale, runtime Plotly charts, CDN dependencies, auto-committed docs,
  and the brittle workflow that failed when a scraper returned no news.

### Preserved

- `docs/latest_data.json` remains decodable by the existing iOS client
  (`DashboardPayload.swift`), including `data`, `news_pool`, `kline_data`,
  `industry_intro`, `industry_basics`, `industry_source_refs`,
  `industry_intro_source`, `global_compare_items`, `global_compare_refs`,
  `data_time` and `data_time_iso`.
- Legacy routes (`overview.html`, `charts.html`, `risk-news.html`,
  `data-center.html`) redirect to the new information architecture.
- The SwiftUI client under `ios/` is retained and remains compatible with the
  generated `latest_data.json` (verified field types and non-null OHLC arrays).
