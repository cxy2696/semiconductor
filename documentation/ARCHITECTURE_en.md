# Architecture

Version 3.0 · 2026-11-11

## 1. System context

```text
┌────────────────────┐        ┌──────────────────────────┐
│ Eastmoney quotes   │        │ open.er-api.com FX       │
└─────────┬──────────┘        └────────────┬─────────────┘
          │                                │
┌─────────▼──────────┐        ┌────────────▼─────────────┐
│ Whitelisted RSS    │        │ data/symbols.json mapping│
└─────────┬──────────┘        └────────────┬─────────────┘
          └──────────────┬─────────────────┘
                         ▼
              semcore fetch (may fail; never blocks the build)
                         ▼
        data/snapshots/latest.json (single input, committed)
                         ▼
   semcore analytics → semcore build (Jinja2 + SVG)
                         ▼
      docs/ (HTML / CSS / JS / JSON / sitemap)
                         ▼
              GitHub Pages (static hosting)
```

Design constraints:

- **No server, no database**: the site is a purely static artefact.
- **Data fetched at build time**: the browser never calls a third-party API, avoiding CORS, rate limits and privacy issues.
- **Degradable**: a failed fetch uses the previous snapshot, and the page shows the data timestamp and a stale marker.
- **Single source of truth**: company master data, classification, interface copy and content each exist in exactly one place.

## 2. Directories and responsibilities

| Path | Responsibility | What does not belong here |
| --- | --- | --- |
| `data/universe.csv` | Master data for 175 companies, including four-language names and notes, `founded` and `fiscal_year_end` | Quotes, scores |
| `data/taxonomy.json` | Stage / role / product / country / market labels in four languages; 70 product tags | Company list |
| `data/i18n/*.json` | Interface copy for `en`, `zh`, `ja`, `de` | Long-form content |
| `content/knowledge/*.md` | Flat long-form files: `<slug>_<suffix>.md` (12 topics × 4 languages) | Interface copy |
| `data/glossary.json` | 52 terms with definitions in four languages | Company data |
| `data/snapshots/` | Market snapshots (build input) | Hand-edited corrections |
| `semcore/sources/` | External adapters | Business rules |
| `semcore/analytics.py` | Factors, scores, risk, market state | HTML |
| `semcore/build.py` | Page orchestration and context | Data fetching |
| `templates/` | HTML structure | Inline data calculations |
| `assets/` | Design system and progressive-enhancement JS | Business data |
| `docs/` | Generated site (built by CI, not committed) | Hand edits |
| `documentation/` | Product / architecture / data / method / operations / roadmap, in four languages | User-visible pages |

## 3. Build pipeline

1. **Load configuration**: `config.py` resolves paths, the four locales and the site URL.
2. **Load master data**: `universe.load_universe()` reads the CSV and validates enumerations, uniqueness and website format against `taxonomy`.
3. **Read the snapshot**: `market.load_snapshot()` reads `latest.json`; if it is missing, the build fails with a request to run `fetch` first.
4. **Compute analytics**: `Analytics.build()` merges companies, quotes and FX, then calculates factors, scores, risk flags, stage statistics, market state and research screens.
5. **Load content**: `content.load_all_knowledge()` parses front matter and Markdown for every locale; `load_glossary()` reads the terms.
6. **Render pages**: for each of the four locales, render 7 fixed pages + 12 knowledge pages + 175 company pages, and copy assets.
7. **Write auxiliary files**: `sitemap.xml`, `robots.txt`, `.nojekyll`, `latest_data.json`, `api/snapshot.{en,zh,ja,de}.json`, legacy-route redirects, `/en/` redirect stubs and `404.html`.
8. **Validate**: `validate_artifacts()` checks required files, JSON contracts, legacy fields and the absence of CDNs.

## 4. Module boundaries

### sources/eastmoney.py

- `resolve_secid()`: builds candidate `secid` values by market rule, verifies each code match and writes the result to the cache.
- `fetch_quote()` / `fetch_history()`: HTTP requests with retries and a 15-second timeout.
- `build_market_entry()`: normalises raw fields into a snapshot entry (price, change, market cap, PE/PB/ROE, 52-week range, 30-day return, 30-day OHLC).
- Returns `None` on failure; `market.py` decides the fallback.

### sources/news.py

- `fetch_feed()` fetches feeds concurrently; one failing feed does not affect the others.
- `parse_feed()` supports both RSS 2.0 and Atom.
- `_relevant()` filters by keyword, de-duplicates and keeps the first 24 items.

### market.py

- Thread pool (default 6) fetches 175 companies.
- On failure it prefers the previous snapshot entry and marks it `status="stale"`.
- Merges FX and news, then writes `latest.json` and a dated snapshot, retaining the most recent 30.

### analytics.py

- Pure computation, no I/O, easy to test.
- `Row` is the intermediate representation used by templates and JSON.
- Percentiles are grouped by stage; groups with fewer than 8 companies fall back to the full sample.
- `Analytics` aggregates stage statistics, country and market statistics, regime, screens and momentum extremes.

### build.py

- `SiteBuilder` owns the view dictionaries (localised views for each locale), URL calculation, page contexts, template rendering and output writing.
- Every page context contains `t` (copy), `href()`, `alternates`, `analytics`, `tax` and `snapshot`.
- `_legacy_payload()` produces `latest_data.json` for iOS compatibility.
- `_localized_payload()` produces `api/snapshot.{lang}.json` for the four locales.

### validate.py

- `validate_data()`: master data, i18n, knowledge and glossary.
- `validate_artifacts()`: pages, JSON, sitemap, CDN checks and hreflang.
- CI runs the data checks before the build and the full checks after it.

## 5. Four-language architecture

| Layer | Mechanism |
| --- | --- |
| URL | English at the root, Chinese `/zh/`, Japanese `/ja/`, German `/de/`; every page has absolute alternates |
| Legacy URLs | `/en/...` redirect stubs point at the corresponding root pages |
| Interface copy | `data/i18n/{en,zh,ja,de}.json`, keys fully aligned and CI-checked |
| Data labels | `label` objects in `taxonomy.json` with `{zh, en, ja, de}` values |
| Long-form content | Flat files `content/knowledge/<slug>_<suffix>.md`; slugs are identical across languages |
| Glossary | A single file with four language fields; the page renders the active language and exposes the other three in a comparison block |
| Numbers | Consistent thousands separators and decimal places; currency suffixes keep ISO codes |
| Dates | The site uses Asia/Shanghai (UTC+8); data dates follow the source |

**Why not switch languages in the browser?** Separate URLs are better for sharing, SEO, caching and no-JS environments; the language switch is generated at build time and does not depend on a runtime dictionary. The cost is four times the pages, which static hosting absorbs without difficulty.

## 6. Link model

- `SiteBuilder._page_path(locale, key, slug)` is the only path-generation function.
- Templates obtain links only through functions such as `href('company', id)`, avoiding hard-coded relative paths.
- `rel_href()` computes the relative path from the current page to the target page, so the site also works when opened directly from `file://`.
- Assets use `root + 'assets/...'`, where `root` is derived from the page depth.

## 7. Rendering and performance

- **Zero third-party assets**: no Tailwind, no Plotly, no font CDN.
- Charts are generated as SVG in Python: scatter, sparkline and 52-week range bars.
- CSS is about 30 KB and JS about 8 KB (uncompressed). Most pages are 30–120 KB of HTML; the company index is larger because it server-renders 175 rows.
- The company table is rendered server-side; filtering and sorting use native JS, with no virtual list.
- No blocking scripts above the fold; a small inline theme script in `<head>` prevents a flash of the wrong theme.

## 8. Accessibility and SEO

- Semantic `header/nav/main/footer`, `aria-current`, `aria-sort` and skip links.
- Tables have a `thead` and keyboard-operable sortable headers.
- Charts carry `role="img"`, `aria-label` and `<title>`.
- `prefers-reduced-motion` disables animation; contrast meets AA.
- Every page has a canonical URL, `hreflang` alternates and OG tags; knowledge pages carry Article JSON-LD; the sitemap covers every page.

## 9. Extension points

| Need | Change |
| --- | --- |
| Add a company | Add one row to `universe.csv` and run fetch to generate the symbol mapping |
| Add a stage | Add an entry to `stages` in `taxonomy.json` and update the controlled product vocabulary |
| Add a language | `config.LOCALES` + `data/i18n/<lang>.json` + knowledge files with the new suffix + translated documentation |
| Add a data source | Add an adapter under `sources/` and merge it in `market.fetch_snapshot()` |
| Add a page | New template in `templates/` + `PAGES` + `SiteBuilder` method + navigation |
| Add a chart | Add a pure function in `charts.py` and pass `Markup` through the context |
| Change the method | Update `analytics.py` + `METHODOLOGY_en.md` and its translations + the site method page + the major version |

## 10. Test strategy

| Layer | Tests |
| --- | --- |
| Data | `test_universe.py`: enumerations, duplicate listings, required fields |
| Content | `test_content.py`: front matter, Markdown escaping, 12 topics aligned across four locales |
| Copy | `test_i18n.py`: key alignment, no empty values, formatting |
| Analytics | `test_analytics.py`: score bounds, missing-factor renormalisation, regime thresholds, screen rules |
| Build | `test_build.py`: full build, legacy contract, no CDN |
| Artefacts | `semcore validate`: files, JSON, sitemap, hreflang |

## 11. Known technical debt

1. A single quote source (Eastmoney), with no second source for cross-checking.
2. European `secid` values depend on seed mappings; new listings may require manual probing.
3. Factors are recomputed in full on every build with no cache; at 175 companies this is not a performance problem.
4. The news keyword list is hard-coded in English, so coverage of Chinese, Japanese and German media is limited.
5. Company pages do not emit structured `Corporation` data; SEO still leans on articles.
