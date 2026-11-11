# Data: sources, fields, definitions and limitations

Version 3.0 · 2026-11-11

This document is the authoritative description of the data contract. Field definitions, units and failure handling follow this document; if a page disagrees with it, this document wins and a pull request should correct the page.

## 1. Data flow

```text
Eastmoney public quote API ─┐
open.er-api.com FX ─────────┼─→ semcore fetch ─→ data/snapshots/latest.json ─→ semcore build ─→ docs/
Whitelisted media RSS ──────┘        (single input)              (static HTML / SVG / JSON)
```

- Pages do **not** call third-party APIs directly; all data is written to a snapshot at build time.
- Snapshots are committed to the repository, so the site can be built offline and every build is auditable and revertible.
- A failed fetch never empties the page: an individual company falls back to the previous snapshot and is marked `stale`; a total failure keeps the previous `latest.json` and the page shows a stale notice.

## 2. Source list

| Data | Source | Interface / method | Frequency | Licence / notes |
| --- | --- | --- | --- | --- |
| Quotes, valuation, market cap | Eastmoney | `push2.eastmoney.com/api/qt/stock/get`, `push2his.../kline/get` | At build time on each trading day | Public interface; copyright remains with the provider; displayed and cited only |
| FX | open.er-api.com | `GET /v6/latest/USD` | Daily | Free, no key |
| FX fallback | Eastmoney FX pairs | `USDCNH`, `USDJPY`, `USDKRW`, `USDEUR`, `USDHKD` | As above | Used only when the primary source fails |
| Industry news | Tom's Hardware / Semiconductor Digest / EE Times / DigiTimes / Semiconductor Today | RSS | Daily | Title, source, date and link only; each title must match a semiconductor keyword; at most 6 items per source |
| Classification and glossary | Maintained in this repository | `data/taxonomy.json`, `glossary.json` | On demand | CC BY 4.0 |

> The Eastmoney interface is undocumented and field semantics may change. CI validation and snapshot fallback reduce the risk; when something looks wrong, follow the runbook in `OPERATIONS_en.md`.

## 3. Company master data (`data/universe.csv`)

The CSV is the single source of truth for company coverage. It has **175 rows**, one per company, with one primary listing per company.

| Column | Type | Definition | Missing / fallback |
| --- | --- | --- | --- |
| `id` | string | Stable identifier used in URLs and snapshots | Required |
| `ticker` | string | Primary listing code | Required |
| `exchange` | string | Exchange code (for example `SSE`, `NASDAQ`) | Required |
| `mic` | string | ISO 10383 market identifier code | Required |
| `market` | enum | Primary listing market: CN, HK, TW, US, JP, KR, EU | Required; 7 values in total |
| `country` | enum | Headquarters region: CN, HK, TW, US, JP, KR, NL, DE, FR, CH, GB, IL, TH | Required; 13 values in total |
| `stage` | enum | One of the 8 value-chain stages | Required |
| `role` | enum | One of the 9 roles (fabless, foundry, IDM, memory, equipment, materials, OSAT, module, EDA/IP) | Required |
| `products` | string | Pipe-separated product tags from the controlled vocabulary | Empty allowed; 70 tags in total |
| `hq` | string | Headquarters city | Required |
| `website` | URL | Official site, `http(s)://` only | May be empty |
| `currency` | ISO 4217 | Trading currency | Required |
| `quote_venue` | string | Quote venue override; empty means automatic resolution, `unpriced` means the company stays in the research universe but is excluded from quote statistics | Empty or `unpriced` |
| `name_zh` | string | Chinese display name | Required |
| `name_en` | string | English display name | Required |
| `name_ja` | string | Japanese display name | Required |
| `name_de` | string | German display name | Falls back to `name_en` when blank |
| `note_zh` | string | Chinese company note | May be empty |
| `note_en` | string | English company note | May be empty |
| `note_ja` | string | Japanese company note | May be empty |
| `note_de` | string | German company note | Falls back to the English note when blank |
| `founded` | string | Year founded, four digits | Optional; shown only when present |
| `fiscal_year_end` | string | Fiscal year-end month, `01`–`12` | Optional; shown only when present |

The 13 headquarters regions are mainland China, Hong Kong, Taiwan, the United States, Japan, South Korea, the Netherlands, Germany, France, Switzerland, the United Kingdom, Israel and Thailand. The 7 listing markets are A-shares (CN), Hong Kong (HK), Taiwan (TW), the United States (US), Japan (JP), Korea (KR) and Europe (EU).

## 4. Snapshot field dictionary

| Field | Type | Unit | Definition | Missing value |
| --- | --- | --- | --- | --- |
| `price` | float | local currency | Latest available close or delayed price | `null` |
| `prev_close` | float | local currency | Previous trading day's close | `null` |
| `change_pct` | float | % | Change on the most recent trading day | `null` |
| `ret_30d` | float | % | Change over the most recent 30 trading days | `null` |
| `ret_ytd` | float | % | Year-to-date change | `null` |
| `volume` | float | shares | Volume on the most recent trading day | `null` |
| `market_cap` | float | local currency | Total market capitalisation (Eastmoney `f116`) | `null` |
| `market_cap_usd` | float | USD | `market_cap × usd_per_unit[currency]` | `null` |
| `pe` | float | times | Static price/earnings ratio (`f164`, latest annual EPS) | `null`; ≤ 0 means a loss |
| `pb` | float | times | Price/book ratio (`f167`) | `null` |
| `roe` | float | % | Return on equity (`f173`) | `null` |
| `turnover` | float | % | Turnover rate (`f168`) | `null` |
| `high_52w` / `low_52w` | float | local currency | Highest / lowest price over the most recent 250 trading days | `null` |
| `history` | object | local currency | OHLCV for the most recent 30 trading days | Empty arrays |
| `status` | string | — | `ok` / `stale` / `missing` | — |
| `as_of` | date | — | Most recent trading day (data date) | `null` |

### FX

`fx.usd_per_unit` means "how many US dollars one unit of local currency is worth", derived as `1 / rate(USD→local)`. USD is fixed at 1.0. A missing currency falls back to the previous snapshot and then to a static constant, with `fx.status` set to `fallback` or `stale`.

### 52-week range

The most recent 250 trading days approximate a natural year because holiday calendars differ between markets. Range position = `(price − low) / (high − low)`, clipped to `[0, 1]`.

### Quote timing

`as_of` is the date of the most recent daily bar, not the fetch time. `snapshot.generated_at` is the time the fetch completed. If the two differ by more than 48 hours, the `stale` flag takes effect.

## 5. Snapshot structure (schema v2)

The values below are illustrative and abridged; they show the shape of the contract rather than a current snapshot.

```json
{
  "schema_version": 2,
  "site_version": "3.0.0",
  "generated_at": "2026-11-11T13:06:50+08:00",
  "dataset": "live",
  "universe_size": 175,
  "coverage": { "priced": 173, "total": 175, "ratio": 0.9886 },
  "fx": {
    "usd_per_unit": { "USD": 1.0, "CNY": 0.1496, "TWD": 0.0305, "JPY": 0.0063, "KRW": 0.00074, "EUR": 1.1205, "HKD": 0.1275 },
    "source": "open.er-api.com",
    "as_of": "…",
    "status": "ok"
  },
  "quotes": {
    "tsmc": {
      "status": "ok", "price": 2285.0, "currency": "TWD",
      "change_pct": 2.24, "ret_30d": -7.11, "market_cap": 59255465450000,
      "pe": 26.49, "pb": 9.21, "roe": 21.58,
      "high_52w": 2590.0, "low_52w": 1375.0,
      "as_of": "2026-11-10", "source": "Eastmoney",
      "history": { "dates": ["…"], "open": [], "high": [], "low": [], "close": [], "volume": [] }
    }
  },
  "news": [ { "title": "…", "link": "https://…", "source": "EE Times", "published": "2026-11-10", "lang": "en" } ],
  "errors": [],
  "sources": { "quotes": "Eastmoney public quote API", "fx": "open.er-api.com", "news": "RSS: …" }
}
```

`dataset`: `live` (at least 60% priced), `partial` (below the threshold), `fixture` (tests).

## 6. Compatibility payload

`docs/latest_data.json` is the legacy format retained for the existing iOS client. Field mapping:

| Legacy field | New source |
| --- | --- |
| `data[].code` | `ticker` |
| `data[].business_type` | Stage short label (Chinese, for the legacy client) |
| `data[].market_cap` | `market_cap` / 1e8 (hundred million, local currency) |
| `data[].invest_score` | `priority` |
| `data[].invest_grade` | priority ≥ 80 A / ≥ 65 B / ≥ 50 C / otherwise D |
| `data[].invest_tags` | Risk flags |
| `data[].is_pick` | priority ≥ 70 |
| `kline_data` | 30-day OHLC for the 40 largest companies by market cap |
| `news_pool` | Snapshot news (title / link / date) |
| `industry_intro` / `industry_basics` | Chinese summaries from the knowledge base and glossary |

New code should use `/api/snapshot.{lang}.json` (`en`, `zh`, `ja`, `de`), whose structure is defined by `semcore/build.py::_localized_payload`. English (`en`) is the default locale.

## 7. Quote source and symbol mapping

- `data/symbols.json` stores the **verified** company ID → Eastmoney `secid` mapping, including `method` (`seed` / `probe`), the `checked` date and the resolved name.
- Automatic resolution rules:
  - A-shares: `1.<code>` (Shanghai) / `0.<code>` (Shenzhen)
  - Hong Kong: `116.<5 digits>`
  - US: probe `105` / `106` / `107` in order
  - Japan: `176.<code>`
  - Taiwan: `178.<code>` (try `179` for OTC)
  - Korea: `177.<code>`
  - Europe: prefer the seed mapping, because European exchange numbers in the interface are not consistent with ticker codes
- A successful resolution is cached and reused on the next run. Manual edits must verify both the name and the price.
- Instruments that cannot be priced (currently only ASM International) remain in the research universe with `quote_venue = "unpriced"`; they are excluded from quote statistics and the page explains why.

## 8. Quality control

| Check | Location | Consequence of failure |
| --- | --- | --- |
| Master-data columns, enums, uniqueness, website format | `validate_data()` | CI fails |
| Four-language i18n keys aligned | `validate_data()` | CI fails |
| 12 knowledge topics with identical slugs across four locales | `validate_data()` | CI fails |
| Glossary terms complete in `zh`, `en`, `ja` and `de` | `validate_data()` | CI fails |
| Artefacts exist, JSON parses, legacy fields present | `validate_artifacts()` | CI fails |
| No third-party CDN resources | `validate_artifacts()` | CI fails |
| Coverage and error list | About page / build log | Manual review |

## 9. Known limitations

1. Quotes are delayed or closing data and are unsuitable for intraday decisions.
2. Static PE is unfriendly to high-growth and loss-making companies; loss-makers have no valuation factor.
3. Fundamental fields such as revenue growth, orders and capacity utilisation are missing.
4. Eastmoney coverage of some European and OTC instruments is incomplete; prices may come from a secondary listing or ADR.
5. FX rates are daily reference rates, so cross-currency comparisons carry error.
6. Adjusted prices cannot fully remove step changes from spin-offs, carve-outs and other corporate actions; extreme one-day moves need manual review.
7. News is filtered by title keywords and de-duplicated, not fact-checked; borderline headlines may remain.
8. Classification is an editorial judgement, and changing businesses need quarterly review.

## 10. Retention and cleanup

- `data/snapshots/` keeps the most recent 30 snapshots (`SNAPSHOT_KEEP`), cleaned automatically by `save_snapshot()`.
- The `docs/` output is rebuilt in full on every build; historical pages are not retained.
- Historical scores are not archived separately; to backtest, rebuild from the snapshot for the relevant date.

## 11. Licence and citation

- Quote and news copyright remains with the original providers; this site only cites, links and displays limited excerpts.
- Original text and classification data are released under CC BY 4.0.
- Citation format: `SiliconScope, <page title>, <URL>, accessed <YYYY-MM-DD>`.
