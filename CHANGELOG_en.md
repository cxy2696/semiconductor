# Changelog

All notable changes to this project are documented here. The format follows
Keep a Changelog, and the project uses semantic versioning.

## [3.0.0] — 2026-11-11

### Added

- English-first routing: English is the default locale at `/` and the
  `x-default`, with Chinese at `/zh/`, Japanese at `/ja/` and German at `/de/`.
- German locale across interface copy, taxonomy labels, company names and notes,
  glossary definitions, knowledge topics and documentation.
- Universe expanded to 175 companies across 13 headquarters regions and 7
  listing markets, including Chinese, Hong Kong, Taiwanese, US, Japanese,
  Korean, European and Israeli listings.
- Company detail fields `name_de`, `note_de`, `founded` and `fiscal_year_end`,
  surfaced on company pages.
- Three knowledge topics: `eda-ip`, `automotive` and `ai-datacenter`, bringing
  the knowledge base to 12 topics.
- Four-language documentation using the `_en` / `_cn` / `_jp` / `_de` suffix
  convention, and flat knowledge files
  (`content/knowledge/<slug>_<suffix>.md`).
- `/en/` redirect stubs that point old English URLs at the new root paths.
- Four-language glossary: 52 terms with definitions in English, Chinese,
  Japanese and German; the product vocabulary now holds 70 tags.
- Localised API snapshots for all four locales
  (`/api/snapshot.en.json`, `.zh.json`, `.ja.json`, `.de.json`), including the
  new German payload.
- Four-locale validation of interface keys, knowledge slugs and glossary fields
  in CI.

### Changed

- Moved the default locale from Chinese to English: the site root now serves
  English, and Chinese lives under `/zh/`.
- Rebuilt the site for four locales, with four `hreflang` alternates and
  `x-default` pointing at English.
- Renamed documentation to language-suffixed files and moved knowledge content
  from language directories to flat `<slug>_<suffix>.md` files.
- Regenerated the legacy `latest_data.json` for the 175-company universe while
  keeping the field contract unchanged.
- Bumped the site version to 3.0.0.

### Removed

- Chinese-first root routing.
- The `content/knowledge/{lang}/` directory layout.

### Preserved

- `docs/latest_data.json` remains decodable by the existing iOS client
  (`DashboardPayload.swift`), including `data`, `news_pool`, `kline_data`,
  `industry_intro`, `industry_basics`, `industry_source_refs`,
  `industry_intro_source`, `global_compare_items`, `global_compare_refs`,
  `data_time` and `data_time_iso`.
- Legacy routes (`overview.html`, `charts.html`, `risk-news.html`,
  `data-center.html`, `knowledge-old.html`) redirect to the current information
  architecture.
- The SwiftUI client under `ios/` is retained and remains compatible with the
  generated `latest_data.json` (verified field types and non-null OHLC arrays).

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
- CI: data-contract validation, artefact validation and pytest suite.
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
