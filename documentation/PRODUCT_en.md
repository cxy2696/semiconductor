# Product: SiliconScope Semiconductor Intelligence Desk

Version 3.0 · 2026-11-11 · Maintainers: SiliconScope contributors

## 1. One-line positioning

**A single, public, auditable view of the global semiconductor value chain: its structure, each company's position, the state of the cycle and the underlying concepts.**

SiliconScope is not a quote terminal and not a stock-picking tool. It is a **research desk**: it helps a reader build a structural view of one stage or one company in 10–30 minutes, and makes clear how complete the data behind that view is.

## 2. Why it exists

Three characteristics of semiconductors make the industry hard to serve with a single tool:

1. **High knowledge barrier.** Equipment, materials, process, packaging and memory each have their own vocabulary; cross-market discussion loses meaning quickly.
2. **Strong cyclicality.** The same metric can mean opposite things at the top and the bottom of a cycle, and static valuation often misleads.
3. **Geopolitical exposure.** Export controls, subsidies and localisation of capacity can change a company's revenue mix quickly.

Free information is either fragmented news or quote pages that cover a single market. Readers need a **structured middle layer**: one that does not forecast prices but explains how a stage earns money, who competes in it, what state it is in and whether the data is trustworthy.

## 3. Target users and use cases

| User | Typical job to be done | What the site provides |
| --- | --- | --- |
| Students and researchers learning the value chain | "Before an interview or a report, I want to understand how equipment, materials, foundry and packaging fit together." | Value-chain page + 12 long-form topics + four-language glossary |
| Analysts and practitioners who need a global view | "Give me one table where I can see the main players and valuations by stage and region." | Company map + stage statistics + valuation-quality scatter |
| Individual investors who care about data definitions | "Where does this score come from? How much data is missing?" | Method page + data coverage + snapshot time and sources |

**Explicitly out of scope**: intraday trading, leverage and position advice, target prices, earnings forecasts, and full-text news reading.

## 4. Scope

### Covered

- **8 stages**: EDA/IP and design services, chip design (fabless), wafer fabrication (foundry / IDM), memory, equipment, materials, packaging and test, modules and systems.
- **13 headquarters regions**: mainland China, Hong Kong, Taiwan, the United States, Japan, South Korea, the Netherlands, Germany, France, Switzerland, the United Kingdom, Israel and Thailand.
- **7 listing markets**: A-shares, Hong Kong, Taiwan, the United States, Japan, Korea and Europe.
- **175 listed companies**, each with one primary listing to avoid double counting.
- **70 product tags** from a controlled vocabulary, used for filtering and company-page display.
- **52 glossary terms**, each with a definition in English, Chinese, Japanese and German.
- **Four languages**: English (default), Simplified Chinese, Japanese and German.

### Not covered

- Private companies (for example YMTC and some SMIC subsidiaries).
- Pure end-market brands and distributors, unless their revenue is mainly from semiconductors.
- Minute-level quotes, order books, options and derivatives.
- In-depth reporting beyond the aggregation of company news.
- Investment advice of any kind.

## 5. Information architecture

```text
/                          English home (default, x-default)
/zh/                       Chinese home
/ja/                       Japanese home
/de/                       German home
/companies.html            company map (filter / sort)
/companies/{id}.html       company page
/value-chain.html          value-chain panorama
/knowledge.html            knowledge index
/knowledge/{slug}.html     long-form topic
/glossary.html             glossary
/guide.html                how to use the desk
/methodology.html          method and boundaries
/status.html               data status and freshness
/about.html                purpose, sources, licence, build information
/en/...                    legacy English URLs, redirecting to /
/zh/... /ja/... /de/...    localised mirrors with the same structure
/api/snapshot.{lang}.json  localised data snapshot (en, zh, ja, de)
/latest_data.json          legacy payload for the iOS client
```

Four content layers:

1. **Facts**: quotes, valuation, market capitalisation, 52-week range, data timestamp and sources.
2. **Structure**: stages, roles, regions, market-cap distribution, concentration.
3. **Judgement**: research priority, risk flags, market state, research screens.
4. **Method**: factor definitions, weights, thresholds, limitations and disclaimer.

The judgement layer can always be traced back to the facts and the method; the method is always public.

## 6. Core product logic

### 6.1 Classify first, then compare

Gross margins, capital intensity and cyclical drivers differ completely between stages, so comparing PE across stages is meaningless. Therefore:

- every factor is percentile-normalised **within its stage**;
- stages with fewer than 8 companies fall back to the full sample, and the method page says so;
- pages show absolute values and relative scores together, avoiding "the score is the conclusion".

### 6.2 Scores order reading; they do not forecast

"Research priority" answers "which company should I read first", not "which company should I buy".

- A high score means a stronger combined position on quality, valuation, momentum and size in the currently published data;
- a low score does not mean a bad company: it may simply be expensive, missing data or at the bottom of a cycle;
- no page contains "buy / sell / target price / position size".

### 6.3 Completeness is a first-class citizen

Every record has a data-coverage score (the share of 8 fields present), and every page shows the data timestamp and sources. Missing fields display `—`; the site does not guess or fill zeros. When a fetch fails, the previous snapshot is used and the page is marked as stale.

### 6.4 Four-language parity

The English, Chinese, Japanese and German editions have identical page structure, data and charts; only the interface copy and the language of the content differ. English is the canonical source, but it is not a fuller edition: all four languages carry the same information. Missing content in any language fails CI, which prevents the common failure mode in which the English site is the full version and the others are summaries.

## 7. Design principles

1. **One source of truth**: company master data lives only in `data/universe.csv`; classification labels live only in `data/taxonomy.json`.
2. **Everything at build time**: no third-party API calls from the browser, no CDN, charts rendered as SVG.
3. **Auditable**: every number can be traced to a snapshot file and a field definition.
4. **Restrained visual language**: information density first; colour is used only for direction and classification, not decorative animation.
5. **Printable and accessible**: semantic tables, keyboard access, WCAG AA contrast, and support for `prefers-reduced-motion`.
6. **Sustainable**: no server, no database, no paid API; monthly maintenance cost is close to zero.

## 8. Success metrics

The project does not chase page views. It tracks signals that show whether the desk is being used seriously:

| Type | Metric | Target |
| --- | --- | --- |
| Reliability | Build success rate | ≥ 99% per month |
| Freshness | Data timestamp ≤ 24h on trading days | ≥ 95% |
| Completeness | Quote coverage | ≥ 90% |
| Quality | Data contract / tests passing | 100% |
| Maintainability | Files to change when adding one company | 1 (`universe.csv`) |
| Maintainability | Files to change when adding one topic | 4 Markdown files |
| Consistency | Four-language alignment (interface, topics, glossary) | 100% |
| Depth of use | Company-page / knowledge-page ratio | Monitor the trend; no hard target |

## 9. Risks and compliance

- **Data delay**: quotes are delayed or closing prices; the page states this and they are not intended for trading decisions.
- **Data errors**: sources and snapshots are published and corrections are accepted; absolute accuracy is not promised.
- **Copyright**: news retains only title, source, date and link; knowledge content is original explanation with cited references.
- **Investment-advice risk**: every page repeats "research purpose, not investment advice", and the method page carries a separate disclaimer.
- **Supplier dependency**: one quote source, mitigated by snapshot fallback and audited symbol mapping; additional sources are on the roadmap.

## 10. Versioning and evolution

- Semantic versioning: a major version for information-architecture or method changes, a minor version for features and coverage expansion, a patch for data corrections.
- A method change must update `documentation/METHODOLOGY_en.md` and its `_cn` / `_jp` / `_de` translations, the methodology page copy in `data/i18n/*.json`, and `CHANGELOG.md`, with an impact note in the pull request.
- See [ROADMAP_en.md](ROADMAP_en.md) and [OPERATIONS_en.md](OPERATIONS_en.md) for the current plan and operating model.
