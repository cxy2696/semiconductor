# Operations: who maintains it, how often, and what to do when it breaks

Version 3.0 · 2026-11-11

This document defines the day-to-day operation of SiliconScope: roles, cadence, SLOs, monitoring, incident handling, change management and cost. The goal is that **one person can maintain it indefinitely, and two people do not get in each other's way**.

## 1. Operating principles

1. **Automate first**: anything CI can do does not belong on a human to-do list.
2. **Make failure visible**: better to show "data is stale" than to use old data silently.
3. **Change in small steps**: commit data, content and method separately so each can be reverted.
4. **Auditable**: every conclusion can be traced to a snapshot, a field definition and a commit.
5. **Low marginal cost**: no server, no database, no paid API; adding one company changes one row.

## 2. Roles and responsibilities

| Role | Responsibility | Currently held by |
| --- | --- | --- |
| Maintainer | Merge pull requests, release, handle CI failures, own the method | Repository owner |
| Data steward | Master data, classification, symbol mapping, data-anomaly review | Maintainer, shared |
| Content editor | 12 long-form topics, glossary, method-page copy | Maintainer, shared |
| Translator / reviewer | Consistency and terminology review for Chinese, Japanese and German | Community contributors |
| Consumer | Use the site and submit data corrections | Public |

Roles may be combined, but **method changes** must be reviewed by the Maintainer, and **each non-English edition** must receive at least one non-machine review. English is the canonical source; translations must carry the same information, not a shortened version.

## 3. Cadence

| Frequency | Action | Owner | Output |
| --- | --- | --- | --- |
| 08:30 UTC+8 each trading day | CI runs `fetch + build + validate + deploy` automatically | Automation | New snapshot, site |
| Every Monday | Check coverage, error list and stale flags | Data steward | Anomaly list |
| First working day of each month | Review the 175-company sample and classification; check broken websites and delistings | Data steward | Universe-change pull request |
| Quarterly | Review method, limitations and SLOs; update the roadmap | Maintainer | Method version / changelog |
| Half-yearly | Audit the 12 topics and glossary in all four languages for terminology consistency | Content editor / translators | Content pull request |
| On demand | Data corrections, source changes, policy events | Anyone | Issue / pull request |

> Refreshes are not mandatory on non-trading days; CI still runs, but the data date does not change and the page shows `as_of`.

## 4. Service-level objectives (SLOs)

| Metric | Target | Measurement | If missed |
| --- | --- | --- | --- |
| Build success rate | ≥ 99% per month | Actions run results | Follow §6 |
| Data freshness | `as_of` ≤ 24h on trading days, ≥ 95% of the time | Snapshot `as_of` | Check upstream |
| Quote coverage | ≥ 90% | `coverage.ratio` | Check symbol mapping |
| Page availability | ≥ 99.9% per month | GitHub Pages status | Wait for platform recovery |
| Build duration | ≤ 10 minutes | Actions log | Reduce requests / concurrency |
| Page weight | HTML ≤ 400 KB (the company index is the largest page); CSS + JS ≤ 80 KB | Build check | Optimise templates |
| Tests passing | 100% | CI | Block merge |
| Four-language alignment | 100% | `validate_data()` | Block merge |

## 5. Monitoring signals

There is no separate monitoring system; the project uses **observable artefacts**:

1. **GitHub Actions**: whether the daily run succeeded, its duration and the failing step.
2. **`data/snapshots/latest.json`**: `coverage`, `errors`, `dataset` and `generated_at`.
3. **Pages**: the stale notice on the home page, the data timestamp in the footer, and the error list on the about page.
4. **`semcore validate`**: data-contract and artefact completeness.
5. **GitHub Issues**: reader-reported data errors.

Export `coverage` and `errors` once a quarter to compare trends.

## 6. Incident runbook

### 6.1 The quote source is entirely unavailable

**Symptoms**: many `fetch` errors, a sharp drop in `coverage`, old data on the page.

1. Inspect `errors` and `coverage` in `data/snapshots/latest.json`.
2. Request a known instrument directly with curl to confirm a network or upstream problem:
   ```bash
   curl -s "https://push2.eastmoney.com/api/qt/stock/get?secid=1.688981&fltt=2&fields=f43,f57,f58"
   ```
3. If the upstream is down: **do not** edit the data by hand. Keep the previous snapshot, let CI deploy it in `stale` state, and record the incident in an issue.
4. If the interface fields changed: update `QUOTE_FIELDS` and the parser, add tests, and ship a patch release.
5. After recovery, trigger `workflow_dispatch` manually and confirm that coverage is back to ≥ 90%.

### 6.2 A single instrument cannot be resolved

**Symptoms**: `<id>: symbol not resolved` appears in `errors` and on the about page.

1. Check whether `data/symbols.json` contains a `secid` for that ID.
2. Use the Eastmoney search endpoint to confirm the code and market number:
   ```bash
   curl "https://searchapi.eastmoney.com/api/suggest/get?input=NVDA&type=14&token=D43BF722C8E33BDC906FB84D85E326E8&count=5"
   ```
3. Write the `secid` into `symbols.json` by hand, recording `method: "seed"` and the `checked` date.
4. Re-fetch and verify the name, price, currency and market-cap magnitude.
5. If there is genuinely no reliable source: set `quote_venue = "unpriced"`; the page will explain this and exclude the company from statistics.

### 6.3 FX failure

**Symptoms**: `fx.status = stale/fallback`, cross-currency market caps look wrong.

1. Check whether `open.er-api.com` is reachable.
2. The system automatically falls back to Eastmoney FX pairs and then to the previous snapshot.
3. If the failure persists: update `STATIC_FALLBACK` in `sources/fx.py` (record the date) and explain in an issue.
4. Never write an unverified rate by hand.

### 6.4 News fetch failure

**Symptoms**: the home-page "Industry news" section is empty or stale.

- News is a **non-critical path**: the build must not fail because of it.
- Check whether a feed URL has changed; update `config.RSS_FEEDS`.
- If a publication is unavailable for a long period, remove it from the whitelist and record why.

### 6.5 Build failure

1. Read the Actions log to locate the step: `refresh` / `validate` / `deploy`.
2. Reproduce locally:
   ```bash
   python -m semcore build
   python -m semcore validate
   python -m pytest
   ```
3. If the problem is data: fix `universe.csv`, `taxonomy.json` or a content front matter.
4. If the problem is a template: run `serve` locally, inspect the page and add a build test.
5. Roll back with `git revert` of the most recent commit, then trigger deployment again.

### 6.6 Page structure or style regression

1. Identify the scope: one page / one language / the whole site.
2. Build locally and compare screenshots.
3. After the fix, run the full test suite and `validate`.
4. If the issue is a third-party font or browser compatibility: prefer the system font stack and do not add a CDN.

### 6.7 Data error reported by a reader

1. Ask for a source (filing or exchange page).
2. Determine whether it is a **source error** or a **mapping error**:
   - source error: record it in an issue and wait for the upstream to correct it; do not override by hand;
   - mapping error: fix `symbols.json` or `universe.csv`.
3. Record the fix in `CHANGELOG.md` and reply on the issue.

### 6.8 Security incident

- The repository has no secrets, no database and no user data; the main risks are dependency vulnerabilities and malicious pull requests.
- Enable Dependabot; review workflow changes in external pull requests.
- Do not execute untrusted code with `pull_request_target` in Actions.
- If malicious content is found: revert immediately, rotate the GitHub token and audit recent deployments.

## 7. Change management

### 7.1 Change types

| Type | Impact | Requirement |
| --- | --- | --- |
| Data correction | One company / one term | Attach a source; update the snapshot or master data |
| Content addition | Long-form topic / glossary | Complete in all four languages; CI passes |
| Style / template | Site-wide visual | Screenshot comparison; check mobile and dark mode |
| Method change | Scores, screens, state | Update METHODOLOGY + site page + CHANGELOG + major version |
| Dependency upgrade | Build environment | Pin versions; run the full test suite |

### 7.2 Version numbers

- **Major**: information architecture, scoring method or data-contract changes that are not backward compatible.
- **Minor**: new pages, languages, data sources or coverage expansion.
- **Patch**: data corrections, copy and style fixes.

### 7.3 Release flow

1. Pull request → CI (`quality.yml`: tests + data validation + build).
2. Review: data changes need a source; method changes need an impact note; content changes need all four languages.
3. Merge to `main` → `pages.yml` builds and deploys.
4. Update `CHANGELOG.md` and the version number where applicable.
5. After deployment, spot-check the home page, a company page, a knowledge page and one page in each language edition.

## 8. Governance

### 8.1 Sample admission

A new company must:

- be listed and tradable;
- earn most of its revenue from semiconductors (or be explicitly labelled as an adjacent stage);
- have a reliable quote source;
- fill a stage or regional gap, or be a key leader.

Removal criteria: delisting, acquisition, business transformation, or six consecutive months without reliable data.

### 8.2 Classification disputes

- Use the main revenue source of the most recent fiscal year;
- present evidence in the pull request (segment revenue from the annual report);
- when the case is genuinely ambiguous, keep the company in "modules/systems" or "design" and explain in the company note.

### 8.3 Method governance

- Any weight adjustment requires an offline comparison (score distribution, screen changes).
- A threshold adjustment requires a stated motivation and impact.
- The method must never be changed simply to make a particular company appear in a screen.

### 8.4 Content governance

- Original explanation with cited references; do not copy copyright-protected text in full.
- All four language versions carry equivalent information; do not produce an "English full version" and shortened translations.
- Every article records its update date and difficulty level.

## 9. Cost

| Item | Usage | Cost |
| --- | --- | --- |
| GitHub Actions | One run per day × ~5 minutes + pull requests | Within the free allowance for public repositories |
| GitHub Pages | Static hosting | Free |
| Quotes / FX / RSS | Public interfaces | Free |
| Domain | Default `github.io` | 0; a custom domain is extra |

**Target: zero monthly cash cost; maintainer time ≤ 2 hours per month, excluding content creation.**

## 10. Backup and rollback

- Code and snapshots live in Git history, which is a natural backup.
- The site can be rebuilt from any commit: `git checkout <sha> && python -m semcore build`.
- Deployment rollback: revert the commit and re-run `pages.yml`.
- The most recent 30 snapshots are retained; older data can be recovered from Git history.

## 11. Dependencies and licence

- Runtime dependencies are only `jinja2` and `requests`; tests use `pytest`.
- Dependency upgrades go through a pull request and pin the major version range.
- Data and news copyright remains with the providers; the site does not resell or bulk-redistribute them.
- Code is MIT; written content is CC BY 4.0.

## 12. Retirement plan

If the project stops being maintained:

1. Mark the README and home page as "no longer updated" and state the last data date.
2. Keep the repository and `docs/` read-only; do not delete history.
3. Export `data/snapshots/latest.json` and `latest_data.json` with a description of the field definitions.
4. Remove the scheduled Actions workflow so that upstream requests stop.
