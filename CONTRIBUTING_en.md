# Contributing

Thank you for improving SiliconScope. The project prioritises **auditability**, **maintainability** and **consistency across four languages**. Please follow the process below.

## Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m semcore build      # build from the committed snapshot
python -m semcore serve      # http://127.0.0.1:8000
python -m pytest
python -m semcore validate
```

## Common changes

### Add or correct a company

1. Edit `data/universe.csv`; one row per company. Column definitions are in `documentation/DATA_en.md`.
2. Keep one primary listing per company; do not add the same company twice for different markets.
3. Include a source in the pull request (exchange page or annual report) and explain the classification.
4. Run `python -m semcore validate --data-only`.
5. If the new company's quote cannot be resolved automatically, run `python -m semcore fetch` to generate the `data/symbols.json` mapping. If it still fails, note it in the pull request or set `quote_venue = "unpriced"`.

The company master data is four-language. v3 adds these columns:

| Column | Required | Meaning |
| --- | --- | --- |
| `name_de` | Optional | German display name; blank falls back to `name_en` |
| `note_de` | Optional | German company note; blank falls back to the English note |
| `founded` | Optional | Year founded, four digits |
| `fiscal_year_end` | Optional | Fiscal year-end month, `01`–`12` |

Fill the German name and note where possible. Leave `founded` and `fiscal_year_end` blank when they cannot be verified; the fields are displayed only when present.

### Add a glossary term

1. Edit `data/glossary.json`; provide `term` and `def` for **all four** languages: `en`, `zh`, `ja` and `de`.
2. Use an existing `category` (process / equipment / material / packaging / memory / design / business / economics / policy).
3. Keep definitions to 2–4 sentences and avoid circular definitions.
4. Run `python -m pytest tests/test_content.py`.

### Add a knowledge topic

1. Create flat files under `content/knowledge/` named `<slug>_en.md`, `<slug>_cn.md`, `<slug>_jp.md` and `<slug>_de.md`. Use a lowercase hyphenated slug.
2. Required front matter: `title`, `summary`, `level` (foundation/core/advanced), `minutes`, `order`, `tags`, `related`, `updated`.
3. `related` may only reference existing slugs. The slug and `order` must be identical in all four languages.
4. The knowledge base currently has 12 topics: `advanced-packaging`, `ai-datacenter`, `automotive`, `cycle`, `eda-ip`, `equipment-materials`, `lithography`, `memory-hbm`, `metrics`, `policy`, `process-flow` and `value-chain`.
5. Use the supported Markdown subset: `##`, `###`, paragraphs, lists, quotes, fenced code blocks, bold and links. **Raw HTML is not supported.**
6. List verifiable references at the end.
7. Carry equivalent information in all four languages; do not publish an "English full version" with shortened translations.

### Change the method or scoring

1. Open an issue first, explaining the motivation and expected impact.
2. Change `semcore/analytics.py` and add tests.
3. Update `documentation/METHODOLOGY_en.md` and its `_cn` / `_jp` / `_de` translations, plus the site copy in `data/i18n/*.json`.
4. Record the change in `CHANGELOG.md` and increment the major version.
5. Include an offline comparison in the pull request: score distribution, screen changes and affected pages.

### Change styles or templates

- Design tokens live in the `:root` and `[data-theme="dark"]` blocks at the top of `assets/css/main.css`.
- Keep the site free of CDNs, frameworks and external fonts.
- Check widths 1440 / 1024 / 390, light and dark themes, and keyboard access.
- Do not introduce autoplay animation; respect `prefers-reduced-motion`.

## Code style

- Python 3.11+, type hints preferred, avoid side-effectful global state.
- Module responsibilities are described in `documentation/ARCHITECTURE_en.md`; keep fetching, analytics and rendering separate.
- Templates display only; do not perform complex calculations in them.
- Use native JS APIs and avoid dependencies; every interaction must degrade when JS is unavailable.

## Pull-request checklist

- [ ] `python -m pytest` passes
- [ ] `python -m semcore validate` passes
- [ ] Interface keys, knowledge slugs and glossary fields align across all four languages
- [ ] Documentation changes include the `_en` / `_cn` / `_jp` / `_de` versions
- [ ] New data includes a source
- [ ] Mobile and dark mode checked
- [ ] `CHANGELOG.md` updated where applicable
- [ ] No large files committed outside `docs/`

## Commit messages

Use a concise imperative style, for example:

```text
data: add Toyota Industries to automotive coverage
fix: hide the P/B column below 1500px to avoid table overflow
docs: clarify that the 30-day return uses trading sessions
content: add the ai-datacenter topic in four languages
```

## Code of conduct

- Discuss evidence and method, not people.
- Do not submit unverified data or sources.
- Do not present the site's content as investment advice.
