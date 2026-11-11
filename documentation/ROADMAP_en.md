# Roadmap

Version 3.0 · 2026-11-11

Principle: secure **auditability** and **maintainability** before expanding coverage or features. Every item states its acceptance criteria, so that "done" is verifiable rather than a matter of appearance.

## Completed (v3.0)

- [x] English-first routing: English at `/` and as `x-default`; Chinese `/zh/`, Japanese `/ja/`, German `/de/`
- [x] German locale across interface copy, taxonomy, company names and notes, glossary and documentation
- [x] 175 companies across 8 stages, 13 headquarters regions and 7 listing markets, including Chinese, Hong Kong, Taiwanese, US, Japanese, Korean, European and Israeli listings
- [x] Company detail fields: `name_de`, `note_de`, `founded` and `fiscal_year_end`
- [x] 12 knowledge topics, including the new `eda-ip`, `automotive` and `ai-datacenter` topics
- [x] 52 glossary terms in four languages and 70 product tags
- [x] Four-language documentation with `_en` / `_cn` / `_jp` / `_de` suffixes
- [x] Flat knowledge naming: `content/knowledge/<slug>_<suffix>.md`
- [x] `/en/` redirect stubs so that old English URLs keep working
- [x] Four-language validation in CI
- [x] Legacy `latest_data.json` regenerated for 175 companies, still decodable by the iOS client

## Completed (v2.0)

- [x] Global coverage: 124 companies, 8 stages, 7 listing markets
- [x] Chinese / English / Japanese with separate URLs and hreflang
- [x] 9 long-form topics + 52 trilingual glossary terms
- [x] Public method: factors, weights, coverage, risk flags, market state, screens
- [x] Snapshot fallback, coverage metrics and stale flags
- [x] Zero CDN, build-time SVG, no front-end framework
- [x] CI: tests + data contract + artefact validation
- [x] Product / architecture / data / method / operations documentation

## Near term (1–3 months)

### 1. Second quote source and cross-checking

**Problem**: a single provider (Eastmoney) leaves no reference when field semantics or availability change.

**Plan**: add an independent source (for example an official exchange end-of-day feed or Stooq), compare prices and changes within a tolerance, and flag mismatches as `source_conflict`.

**Acceptance**: at least 90% of instruments have two sources; conflict rate below 2%; the page displays a conflict flag; tests cover the comparison logic.

### 2. Fundamental-field expansion

**Problem**: the quality factor relies on ROE alone and lacks growth and cash flow.

**Plan**: add revenue growth, gross margin, operating cash flow / net income and net debt / EBITDA where sources allow, introduce a "growth" factor and redistribute the weights.

**Acceptance**: every new factor has its own definition and missing-data handling; the method page is updated; an offline comparison shows screen changes below 30%.

### 3. Structured data on company pages

**Problem**: company pages lack `Organization` / `Corporation` JSON-LD, which weakens search visibility.

**Plan**: generate JSON-LD for company pages with name, ticker, headquarters, website and sector.

**Acceptance**: the Rich Results test passes; no invalid fields are introduced.

### 4. Four-language editorial review

**Problem**: English is the canonical source, but the Chinese, Japanese and German editions still need native-language review.

**Plan**: recruit one or two reviewers per language, standardise terminology against the glossary and record the review date.

**Acceptance**: all 12 topics in all four languages reviewed; the glossary and body text agree; `CHANGELOG.md` records the review.

## Medium term (3–6 months)

### 5. Interactive value-chain map

**Plan**: add highlighting by region and role and a company bubble chart to the value-chain page, while keeping a no-JS fallback view.

**Acceptance**: keyboard operable; server-rendered content complete; usable on mobile.

### 6. Quarterly review report (generated draft)

**Plan**: generate a quarterly structural summary from historical snapshots (stage market-cap share, breadth, leaders and laggards), edit it by hand and publish it as a knowledge page.

**Acceptance**: the generator is reproducible; the draft includes data and charts; the editorial review process is documented.

### 7. Event calendar

**Plan**: maintain earnings dates, trade shows and policy effective dates in a manual JSON file, and display them on the home page and company pages.

**Acceptance**: dates are verifiable; past events are hidden automatically; labels exist in all four languages.

### 8. Data-quality panel

**Plan**: add `/status.html` showing coverage, stale instruments, parse failures, source status and the last 30 builds.

**Acceptance**: no sensitive information is exposed; the page can serve as the operations entry point.

## Long term (6–12 months)

### 9. Multi-source news and topic clustering

**Plan**: extend to Chinese, Japanese and German media sources, cluster stories by stage and company, and provide a "this week in each stage" view.

**Acceptance**: sources are configurable; de-duplication and relevance scoring; copyright compliance.

### 10. Historical series and cycle positioning

**Plan**: retain a longer history (or aggregate it weekly) and compute valuation percentiles, breadth history and stage rotation.

**Acceptance**: data volume stays manageable (< 20 MB); page performance does not regress; the method remains explainable.

### 11. iOS client upgrade

**Plan**: migrate from `latest_data.json` to `/api/snapshot.{lang}.json` and support four languages and the global company universe.

**Acceptance**: the old client can still decode the legacy payload; the new client supports language switching; TestFlight verification.

### 12. Community contribution process

**Plan**: issue templates (data corrections / content suggestions / method discussions), a pull-request template and a contributor list.

**Acceptance**: templates are usable; CI validates pull requests automatically; merge time below 7 days.

## Not planned

- Real-time Level-2 quotes, trading interfaces or position advice.
- Paywalls, advertising or user tracking.
- Automated investment conclusions without editorial review.
- Adding companies with unverifiable data just to increase coverage.

## Priority rule

Take work in this order:

1. Things that affect data trustworthiness (sources, contracts, validation)
2. Things that affect maintainability (documentation, tests, CI)
3. Things that affect depth of understanding (content, method, visualisation)
4. Things that affect breadth of coverage (new companies, new markets)

Every new feature must answer: **does it make the reader clearer, or merely give them more?**
