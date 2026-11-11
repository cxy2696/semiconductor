# Methodology: factors, scores and boundaries

Version 3.0.0 · Effective 2026-11-11 · Corresponds to the site page `/methodology.html`

This document defines how every number on the site is calculated. Any method change must update this document, the site method page, `CHANGELOG.md` and the version number together.

---

## 1. Research questions

The method answers only three questions:

1. **What state is this stage in?** (market-state readings)
2. **Which companies are worth reading first?** (research priority)
3. **Is the data behind my judgement complete?** (data coverage)

It does not answer: future returns, target prices, entry or exit timing, or position size.

## 2. Sample and classification

- **Sample**: the 175 listed companies in `data/universe.csv`.
- **One company, one listing**: prefer the primary listing; the same company is not counted in multiple markets (for example, SMIC is represented only by its A-share 688981 and Hua Hong only by its Hong Kong listing 1347).
- **Stage**: each company is assigned to one of 8 stages by its main revenue source; this is an editorial judgement and the pull request must state the basis.
- **Role**: fabless / foundry / idm / memory / equipment / materials / osat / module / eda_ip.
- **Country**: the headquarters region, one of 13. **Market**: the listing market, one of 7; the two may differ (for example, NXP is headquartered in the Netherlands and listed in the United States).
- **Product tags**: drawn from a controlled vocabulary of 70 tags in `taxonomy.json`, used for filtering and company-page display.
- **Company metadata**: `founded` (year) and `fiscal_year_end` (month) are descriptive fields and are not used in any factor.

A company may be added or removed only if it is listed, earns most of its revenue from semiconductors, has a reliable quote source, and fills a missing stage or region or is a key leader. Changes are recorded in `CHANGELOG.md`.

## 3. Data fields

| Field | Definition | Unit | Missing handling |
| --- | --- | --- | --- |
| `price` | Latest available close (delayed quote) | local currency | Display `—`; excluded from price-based factors |
| `change_pct` | Change on the most recent trading day | % | As above |
| `ret_30d` | Change over the most recent 30 **trading days** | % | As above |
| `ret_ytd` | Year-to-date change | % | Not used in scoring |
| `market_cap` | Total market capitalisation (local currency) | local currency | Excluded from the size factor |
| `market_cap_usd` | Market cap × FX rate | USD | Excluded from the size factor |
| `pe` | Static price/earnings ratio (latest annual EPS) | times | ≤ 0 or missing → valuation factor missing |
| `pb` | Price/book ratio | times | Missing does not affect other factors |
| `roe` | Return on equity | % | Missing → quality factor missing |
| `turnover` | Turnover rate | % | Display only; not scored |
| `high_52w` / `low_52w` | Highest / lowest price over the most recent 250 trading days | local currency | Missing → range position missing |
| `coverage` | Share of the 8 fields present | 0–1 | See §6 |

> The 52-week range uses 250 trading days as an approximation and is not necessarily a calendar year.

## 4. Factor definitions

Every factor is first percentile-normalised to 0–100 **within its stage**; stages with fewer than 8 companies fall back to the full sample. Percentiles use the mid-rank (ties receive the average rank).

### 4.1 Quality

```text
quality = percentile_rank(ROE, peer_group)
```

Higher ROE means a higher quality score. Missing ROE means a missing factor.

### 4.2 Valuation

```text
valuation = percentile_rank(-PE, peers_with_positive_PE)   # PE > 0
valuation = missing                                        # PE ≤ 0 or missing
```

Lower PE means a higher valuation score. Loss-making companies are not given the illusion of being "cheap"; their valuation factor is simply missing.

### 4.3 Momentum

```text
momentum = 0.6 × percentile_rank(ret_30d, peers)
         + 0.4 × percentile_rank(range_position, peers)

range_position = (price - low_52w) / (high_52w - low_52w)  ∈ [0,1]
```

If one component is missing, renormalise by the remaining weight; if both are missing, the factor is missing.

### 4.4 Size

```text
size = percentile_rank(log10(market_cap_usd), peers)
```

Size is a proxy for liquidity and resilience, not a measure of quality.

### 4.5 Research priority

```text
priority = 100 × Σ(w_i × factor_i) / Σ(w_i)      # sum over available factors only
w = {quality: 0.30, valuation: 0.25, momentum: 0.25, size: 0.20}
```

- Missing factors are not filled with 50; the remaining weights are **renormalised**, avoiding the distortion caused by a neutral value.
- `factor_coverage = Σ available weights / 1.0`, used to signal how much confidence the score deserves.
- The result is rounded to an integer and constrained to 0–100.

## 5. Risk flags

| Flag | Trigger | Meaning |
| --- | --- | --- |
| `loss` | `pe ≤ 0` | Loss in the latest financial year; valuation does not apply |
| `rich` | valuation score ≥ 80 | Expensive relative to its stage |
| `small` | market cap < USD 2bn | Weak scale and liquidity |
| `sharp` | `abs(ret_30d)` ≥ 25% | Large price move over the last 30 days |
| `stale` | snapshot older than 48 hours | Data may be out of date |

`risk_level`: no active flags = low; 1–2 = medium; 3 or more = high. `stale` is shown separately and does not count towards the risk level.

## 6. Data coverage

The 8 fields are `price`, `change_1d`, `ret_30d`, `market_cap_usd`, `pe`, `pb`, `roe` and `range`.

```text
coverage = available fields / 8
≥ 0.875 → high      (7–8 fields)
≥ 0.625 → medium    (5–6 fields)
< 0.625 → low       (4 or fewer fields)
```

Coverage measures whether fields are **present**, not whether the data is accurate.

## 7. Market state

For all companies with `ret_30d`:

```text
breadth    = advancing companies / valid companies
median     = median(ret_30d)
dispersion = P75(ret_30d) - P25(ret_30d)
```

Classification:

| Condition | State |
| --- | --- |
| breadth ≥ 0.60 and median > 2% | Expansion |
| breadth ≤ 0.40 and median < −2% | Contraction |
| otherwise | Neutral |

Leading / lagging stages are those with at least 3 companies and the highest / lowest median return. The state describes the current structure; it does not forecast direction.

## 8. Research screens

| Screen | Rule | Ordering |
| --- | --- | --- |
| Quality first | `quality ≥ 70` and `valuation ≥ 50` | priority descending |
| Valuation pullback | `valuation ≥ 70` and `quality ≥ 50` | valuation descending |
| Momentum leaders | `momentum ≥ 80` and `ret_30d > 0` | momentum descending |

Each screen contains at most 8 companies and only companies with a price.

## 9. Reading guide

- **Scores are relative**: the same company can score differently in another stage or on another date.
- **A high score is not a good company**: it may simply be cheap, momentum-driven, or classified into a small stage.
- **A low score is not a bad company**: it may be at the bottom of a cycle, missing data, or expensive but higher quality.
- **Do not compare scores across stages**: normalisation happens within a stage.
- **Read the score with coverage**: treat a low-coverage score as indicative only.

## 10. Known limitations

1. Quotes are delayed or closing prices and contain no order-book or intraday signals.
2. Static PE is unfriendly to high-growth companies; loss-makers have no valuation factor.
3. Revenue growth, orders, capacity utilisation and inventory data are missing, so the quality factor relies on ROE alone.
4. The 52-week range uses 250 trading days as an approximation.
5. FX rates update daily, so cross-currency comparisons carry daily error.
6. Classification contains editorial judgement; businesses change and need quarterly review.
7. The sample is weighted towards large listed companies and therefore contains survivorship bias.

## 11. Change control

1. Changing a formula or threshold → update this document + the site method page + `CHANGELOG.md`, and increment the major version.
2. Adding a factor → run an offline comparison first, record the effect on the screens, then merge.
3. Changing the sample or classification → list the companies, the reason and the affected pages in the pull request.
4. Every build recalculates the scores and does not retain historical scores; to backtest, use the historical snapshots in `data/snapshots/`.

## 12. Disclaimer

This site is for industry research and learning only and does not constitute any recommendation to buy or sell securities. Data may be delayed or incorrect; always defer to exchange filings and company announcements. Any decision made on the basis of this site is the user's own responsibility.
