"""Static site builder.

Produces a fully self-contained `docs/` tree:

    /                    Chinese (default locale)
    /en/, /ja/           English and Japanese mirrors
    /companies/          company profiles
    /knowledge/          long-form notes
    /api/                localized JSON snapshots
    /latest_data.json    legacy payload kept for the existing iOS client

No third-party CDN is used; all charts are SVG rendered at build time.
"""

from __future__ import annotations

import html
import math
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from .analytics import Analytics, Row
from .charts import STAGE_COLORS, ScatterPoint, legend, range_bar, scatter, sparkline
from .config import (
    ASSETS_DIR,
    DOCS_DIR,
    LOCALES,
    PAGES,
    SITE_NAME,
    SITE_TIMEZONE,
    SITE_URL,
    SITE_VERSION,
    TEMPLATES_DIR,
    Locale,
)
from .content import KnowledgeDoc, load_all_knowledge, load_glossary
from .i18n import bundle_for, lookup
from .market import load_snapshot
from .taxonomy import Taxonomy
from .universe import Company, load_universe
from .utils import fmt_number, fmt_pct, fmt_price, fmt_usd_compact, rel_href, slugify, truncate, write_json, write_text


def _safe_float(value: Any) -> float | None:
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


@dataclass
class PageSpec:
    key: str
    path: str
    locale: Locale
    template: str
    context: dict[str, Any]


class SiteBuilder:
    def __init__(self, snapshot: dict[str, Any] | None = None, output: Path | None = None):
        self.snapshot = snapshot or load_snapshot()
        if not self.snapshot:
            raise RuntimeError("No snapshot found. Run `python -m semcore refresh` first.")
        self.output = Path(output or DOCS_DIR)
        self.taxonomy = Taxonomy.load()
        self.companies = load_universe(taxonomy=self.taxonomy)
        self.analytics = Analytics.build(self.companies, self.snapshot, self.taxonomy)
        self.knowledge = load_all_knowledge()
        self.glossary = load_glossary()
        self.build_time = datetime.now(SITE_TIMEZONE)
        self.views: dict[str, dict[str, dict[str, Any]]] = {
            locale.lang: {} for locale in LOCALES
        }
        self.generated: list[str] = []
        self._build_views()
        self.env = self._environment()

    # ---- environment --------------------------------------------------
    def _environment(self) -> Environment:
        env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        env.filters["num"] = lambda value, digits=2: fmt_number(value, digits)
        env.filters["pct"] = lambda value, digits=2: fmt_pct(value, digits)
        env.filters["usd"] = fmt_usd_compact
        env.filters["price"] = fmt_price
        env.filters["markdownless"] = lambda value: truncate(str(value or ""), 160)
        return env

    # ---- localized views ----------------------------------------------
    def _build_views(self) -> None:
        for locale in LOCALES:
            lang = locale.lang
            for row in self.analytics.rows:
                self.views[lang][row.company.id] = self._view(row, locale)

    def _view(self, row: Row, locale: Locale) -> dict[str, Any]:
        lang = locale.lang
        company = row.company
        flags = [lookup(lang, f"flags.{flag}") for flag in row.flags]
        factor_labels = {
            "quality": {"zh": "质量", "en": "Quality", "ja": "品質"}[lang],
            "valuation": {"zh": "估值", "en": "Valuation", "ja": "バリュエーション"}[lang],
            "momentum": {"zh": "动能", "en": "Momentum", "ja": "モメンタム"}[lang],
            "size": {"zh": "规模", "en": "Size", "ja": "規模"}[lang],
        }
        products = [self.taxonomy.product_label(pid, lang) for pid in company.products]
        return {
            "id": company.id,
            "name": company.name(lang),
            "ticker": company.ticker,
            "symbol": company.symbol,
            "exchange": company.exchange,
            "market": company.market,
            "market_label": self.taxonomy.market_label(company.market, lang),
            "country": company.country,
            "country_label": self.taxonomy.country_label(company.country, lang),
            "hq": company.hq,
            "website": company.website,
            "currency": company.currency,
            "stage": company.stage,
            "stage_label": self.taxonomy.stage_label(company.stage, lang),
            "stage_short": self.taxonomy.stage_label(company.stage, lang, short=True),
            "role": company.role,
            "role_label": self.taxonomy.role_label(company.role, lang),
            "role_desc": self.taxonomy.role_desc(company.role, lang),
            "products": products,
            "product_text": "、".join(products) if lang != "en" else ", ".join(products),
            "note": company.note(lang),
            "price": row.price,
            "price_text": fmt_price(row.price, company.currency),
            "change_1d": row.change_1d,
            "ret_30d": row.ret_30d,
            "ret_ytd": row.ret_ytd,
            "mcap_usd": row.market_cap_usd,
            "mcap_text": fmt_usd_compact(row.market_cap_usd),
            "pe": row.pe,
            "pb": row.pb,
            "roe": row.roe,
            "turnover": row.turnover,
            "high_52w": row.high_52w,
            "low_52w": row.low_52w,
            "range_pos": row.range_pos,
            "priority": row.priority,
            "factors": {
                "quality": row.quality,
                "valuation": row.valuation,
                "momentum": row.momentum,
                "size": row.size,
            },
            "factor_labels": factor_labels,
            "coverage": row.coverage,
            "coverage_level": row.coverage_level,
            "coverage_label": lookup(lang, f"common.{row.coverage_level}"),
            "flags": flags,
            "risk_level": row.risk_level,
            "stale": row.stale,
            "priced": row.priced,
            "as_of": str(row.entry.get("as_of") or ""),
            "spark": Markup(
                sparkline(
                    row.closes,
                    label=f"{company.name(lang)} 30-session trend",
                )
            ),
            "range_bar": Markup(
                "" if not row.priced else range_bar(row.low_52w, row.high_52w, row.price)
            ),
            "color": STAGE_COLORS.get(company.stage, "#64748b"),
            "href": "",
        }

    # ---- links --------------------------------------------------------
    @staticmethod
    def _page_path(locale: Locale, key: str, slug: str | None = None) -> str:
        prefix = f"{locale.slug}/" if locale.slug else ""
        if key == "company":
            return f"{prefix}companies/{slug}.html"
        if key == "topic":
            return f"{prefix}knowledge/{slug}.html"
        if key not in PAGES:
            raise KeyError(f"Unknown page key: {key}")
        return f"{prefix}{PAGES[key]}"

    def href(self, current: str, locale: Locale, key: str, slug: str | None = None) -> str:
        return rel_href(self._page_path(locale, key, slug), current)

    def absolute(self, locale: Locale, key: str, slug: str | None = None) -> str:
        return f"{SITE_URL}/{self._page_path(locale, key, slug)}"

    def alternates(self, current: str, key: str, slug: str | None = None) -> list[dict[str, str]]:
        return [
            {
                "code": locale.code,
                "lang": locale.lang,
                "name": locale.name,
                "href": self.href(current, locale, key, slug),
                "absolute": self.absolute(locale, key, slug),
                "current": current == self._page_path(locale, key, slug),
            }
            for locale in LOCALES
        ]

    # ---- shared context ------------------------------------------------
    def _base_context(self, locale: Locale, key: str, path: str, title: str, description: str, slug: str | None = None) -> dict[str, Any]:
        depth = path.count("/")
        root = "../" * depth
        page_url = f"{SITE_URL}/{path}"
        published = str(self.snapshot.get("generated_at") or "")[:16].replace("T", " ")
        return {
            "lang": locale.lang,
            "locale": locale,
            "locales": LOCALES,
            "root": root,
            "path": path,
            "page_key": key,
            "t": bundle_for(locale.lang),
            "site_name": SITE_NAME,
            "site_version": SITE_VERSION,
            "page_title": title,
            "page_description": description,
            "canonical": page_url,
            "alternates": self.alternates(path, key, slug),
            "alternates_abs": self.alternates(path, key, slug),
            "build_time": self.build_time.strftime("%Y-%m-%d %H:%M"),
            "data_time": published,
            "data_time_iso": str(self.snapshot.get("generated_at") or ""),
            "is_stale": self.analytics.stale,
            "analytics": self.analytics,
            "tax": self.taxonomy,
            "snapshot": self.snapshot,
            "knowledge_docs": self.knowledge[locale.lang],
            "glossary": self.glossary,
            "year": self.build_time.year,
            "href": lambda key_, slug_=None, loc=locale, cur=path: self.href(cur, loc, key_, slug_),
            "abs": lambda key_, slug_=None, loc=locale: self.absolute(loc, key_, slug_),
            "news": (self.snapshot.get("news") or [])[:12],
        }

    # ---- pages ---------------------------------------------------------
    def build(self) -> dict[str, Any]:
        if self.output.exists():
            if self.output.resolve() == Path(DOCS_DIR).resolve():
                shutil.rmtree(self.output)
            else:
                shutil.rmtree(self.output)
        self.output.mkdir(parents=True, exist_ok=True)

        for locale in LOCALES:
            lang = locale.lang
            self._write(locale, "home", "index.html", "home.html", self._home_context(locale))
            self._write(locale, "companies", "companies.html", "companies.html", self._companies_context(locale))
            self._write(locale, "chain", "value-chain.html", "chain.html", self._chain_context(locale))
            self._write(locale, "knowledge", "knowledge.html", "knowledge.html", self._knowledge_context(locale))
            self._write(locale, "glossary", "glossary.html", "glossary.html", self._glossary_context(locale))
            self._write(locale, "method", "methodology.html", "methodology.html", self._method_context(locale))
            self._write(locale, "about", "about.html", "about.html", self._about_context(locale))
            for doc in self.knowledge[lang]:
                self._write(locale, "topic", f"knowledge/{doc.slug}.html", "topic.html", self._topic_context(locale, doc))
            for row in self.analytics.rows:
                self._write(locale, "company", f"companies/{row.company.id}.html", "company.html", self._company_context(locale, row))

        self._copy_assets()
        self._write_payloads()
        self._write_extras()
        return {
            "pages": len(self.generated),
            "files": self.generated,
            "build_time": self.build_time.isoformat(timespec="seconds"),
        }

    def _write(self, locale: Locale, key: str, relative: str, template: str, context: dict[str, Any]) -> None:
        path = f"{locale.slug}/{relative}" if locale.slug else relative
        full = self.output / path
        full.parent.mkdir(parents=True, exist_ok=True)
        template_obj = self.env.get_template(template)
        html_text = template_obj.render(**context)
        full.write_text(html_text, encoding="utf-8")
        self.generated.append(path)

    # ---- contexts ------------------------------------------------------
    def _home_context(self, locale: Locale) -> dict[str, Any]:
        lang = locale.lang
        analytics = self.analytics
        t = bundle_for(lang)
        ctx = self._base_context(
            locale,
            "home",
            f"{locale.slug + '/' if locale.slug else ''}index.html",
            f"{t['site']['name']} · {t['site']['tagline']}",
            t["site"]["description"],
        )
        stage_cards = []
        for stage in self.taxonomy.stages:
            stat = analytics.stage_stats[stage.id]
            stage_cards.append(
                {
                    "id": stage.id,
                    "label": self.taxonomy.stage_label(stage.id, lang),
                    "short": self.taxonomy.stage_label(stage.id, lang, short=True),
                    "kind": stage.kind,
                    "count": stat.count,
                    "mcap": stat.market_cap_usd,
                    "median": stat.median_ret_30d,
                    "color": STAGE_COLORS.get(stage.id, "#64748b"),
                    "href": self.href(ctx["path"], locale, "companies") + f"#stage-{stage.id}",
                }
            )

        scatter_points = []
        for row in analytics.rows:
            if row.pe is None or row.pe <= 0 or row.roe is None or not row.market_cap_usd:
                continue
            view = self.views[lang][row.company.id]
            scatter_points.append(
                ScatterPoint(
                    x=row.pe,
                    y=row.roe,
                    size=row.market_cap_usd,
                    color=STAGE_COLORS.get(row.company.stage, "#64748b"),
                    label=view["name"],
                    meta=f"PE {row.pe:.1f} · ROE {row.roe:.1f}% · {view['mcap_text']}",
                )
            )

        movers = analytics.movers(5)
        ctx.update(
            {
                "stage_cards": stage_cards,
                "flow_stages": [card for card in stage_cards if card["kind"] == "flow"],
                "support_stages": [card for card in stage_cards if card["kind"] == "support"],
                "watchlists": {
                    key: [self.views[lang][row.company.id] for row in rows]
                    for key, rows in analytics.watchlists.items()
                },
                "movers": {
                    "gainers": [self.views[lang][row.company.id] for row in movers["gainers"]],
                    "losers": [self.views[lang][row.company.id] for row in movers["losers"]],
                },
                "scatter_svg": Markup(
                    scatter(
                        scatter_points,
                        lookup(lang, "home.scatter.x"),
                        lookup(lang, "home.scatter.y"),
                        caption=lookup(lang, "home.scatter.desc"),
                    )
                ),
                "legend": Markup(
                    legend([(stage.id, self.taxonomy.stage_label(stage.id, lang, short=True)) for stage in self.taxonomy.stages])
                ),
                "featured_docs": self.knowledge[lang][:3],
                "kpis": {
                    "companies": len(self.companies),
                    "mcap": analytics.total_market_cap_usd,
                    "breadth": analytics.regime["breadth"],
                    "median": analytics.regime["median"],
                    "coverage": analytics.coverage_ratio,
                    "priced": sum(1 for row in analytics.rows if row.priced),
                },
            }
        )
        return ctx

    def _companies_context(self, locale: Locale) -> dict[str, Any]:
        lang = locale.lang
        t = bundle_for(lang)
        ctx = self._base_context(
            locale,
            "companies",
            f"{locale.slug + '/' if locale.slug else ''}companies.html",
            f"{t['companies']['title']} · {t['site']['name']}",
            t["companies"]["lede"],
        )
        rows = sorted(self.analytics.rows, key=lambda row: row.market_cap_usd or 0, reverse=True)
        ctx.update(
            {
                "rows": [self.views[lang][row.company.id] for row in rows],
                "stages": self.taxonomy.stages,
                "countries": sorted({row.company.country for row in rows}),
                "markets": sorted({row.company.market for row in rows}),
                "coverage_pct": round(self.analytics.coverage_ratio * 100, 1),
            }
        )
        return ctx

    def _company_context(self, locale: Locale, row: Row) -> dict[str, Any]:
        lang = locale.lang
        t = bundle_for(lang)
        view = self.views[lang][row.company.id]
        ctx = self._base_context(
            locale,
            "company",
            f"{locale.slug + '/' if locale.slug else ''}companies/{row.company.id}.html",
            f"{view['name']} ({view['symbol']}) · {t['site']['name']}",
            view["note"] or t["site"]["description"],
            slug=row.company.id,
        )
        related_slugs = self._related_topics(row.company.stage)
        docs = [doc for doc in self.knowledge[lang] if doc.slug in related_slugs][:3]
        peers = [self.views[lang][peer.company.id] for peer in self.analytics.peers(row, 8)]
        ctx.update(
            {
                "company": view,
                "row": row,
                "peers": peers,
                "related_docs": docs,
                "positioning": t["company"]["positioningTemplate"].format(
                    name=view["name"],
                    stage=view["stage_label"],
                    role=view["role_label"],
                    products=view["product_text"],
                ),
            }
        )
        return ctx

    def _chain_context(self, locale: Locale) -> dict[str, Any]:
        lang = locale.lang
        t = bundle_for(lang)
        ctx = self._base_context(
            locale,
            "chain",
            f"{locale.slug + '/' if locale.slug else ''}value-chain.html",
            f"{t['chain']['title']} · {t['site']['name']}",
            t["chain"]["lede"],
        )
        blocks = []
        for stage in self.taxonomy.stages:
            stat = self.analytics.stage_stats[stage.id]
            rows = [self.views[lang][row.company.id] for row in self.analytics.rows_for_stage(stage.id)]
            blocks.append(
                {
                    "id": stage.id,
                    "label": self.taxonomy.stage_label(stage.id, lang),
                    "kind": stage.kind,
                    "summary": self.taxonomy.stage_summary(stage.id, lang),
                    "economics": self.taxonomy.stage_economics(stage.id, lang),
                    "metrics": self.taxonomy.stage_metrics(stage.id, lang),
                    "stat": stat,
                    "rows": rows,
                    "color": STAGE_COLORS.get(stage.id, "#64748b"),
                    "count": stat.count,
                    "mcap": stat.market_cap_usd,
                    "median": stat.median_ret_30d,
                }
            )
        ctx.update(
            {
                "blocks": blocks,
                "flow_blocks": [block for block in blocks if block["kind"] == "flow"],
                "support_blocks": [block for block in blocks if block["kind"] == "support"],
            }
        )
        return ctx

    def _knowledge_context(self, locale: Locale) -> dict[str, Any]:
        lang = locale.lang
        t = bundle_for(lang)
        ctx = self._base_context(
            locale,
            "knowledge",
            f"{locale.slug + '/' if locale.slug else ''}knowledge.html",
            f"{t['knowledge']['title']} · {t['site']['name']}",
            t["knowledge"]["lede"],
        )
        ctx.update({"docs": self.knowledge[lang]})
        return ctx

    def _topic_context(self, locale: Locale, doc: KnowledgeDoc) -> dict[str, Any]:
        lang = locale.lang
        t = bundle_for(lang)
        ctx = self._base_context(
            locale,
            "topic",
            f"{locale.slug + '/' if locale.slug else ''}knowledge/{doc.slug}.html",
            f"{doc.title} · {t['site']['name']}",
            doc.summary,
            slug=doc.slug,
        )
        docs = self.knowledge[lang]
        index = next((i for i, item in enumerate(docs) if item.slug == doc.slug), 0)
        related = [item for item in docs if item.slug in doc.related]
        ctx.update(
            {
                "doc": doc,
                "related_docs": related,
                "prev_doc": docs[index - 1] if index > 0 else None,
                "next_doc": docs[index + 1] if index + 1 < len(docs) else None,
                "article_jsonld": {
                    "@context": "https://schema.org",
                    "@type": "Article",
                    "headline": doc.title,
                    "description": doc.summary,
                    "inLanguage": locale.code,
                    "dateModified": doc.updated or self.build_time.date().isoformat(),
                    "author": {"@type": "Organization", "name": SITE_NAME},
                },
            }
        )
        return ctx

    def _glossary_context(self, locale: Locale) -> dict[str, Any]:
        lang = locale.lang
        t = bundle_for(lang)
        ctx = self._base_context(
            locale,
            "glossary",
            f"{locale.slug + '/' if locale.slug else ''}glossary.html",
            f"{t['glossary']['title']} · {t['site']['name']}",
            t["glossary"]["lede"],
        )
        categories = []
        for term in self.glossary:
            if term["category"] not in categories:
                categories.append(term["category"])
        ctx.update({"terms": self.glossary, "categories": categories})
        return ctx

    def _method_context(self, locale: Locale) -> dict[str, Any]:
        lang = locale.lang
        t = bundle_for(lang)
        ctx = self._base_context(
            locale,
            "method",
            f"{locale.slug + '/' if locale.slug else ''}methodology.html",
            f"{t['method']['title']} · {t['site']['name']}",
            t["method"]["lede"],
        )
        ctx.update(
            {
                "factors": [
                    (t["method"]["factorNames"]["quality"], t["method"]["factorQuality"], "0.30"),
                    (t["method"]["factorNames"]["valuation"], t["method"]["factorValue"], "0.25"),
                    (t["method"]["factorNames"]["momentum"], t["method"]["factorMomentum"], "0.25"),
                    (t["method"]["factorNames"]["size"], t["method"]["factorSize"], "0.20"),
                ],
                "regime": self.analytics.regime,
                "coverage_ratio": self.analytics.coverage_ratio,
                "as_of": self.analytics.as_of,
            }
        )
        return ctx

    def _about_context(self, locale: Locale) -> dict[str, Any]:
        lang = locale.lang
        t = bundle_for(lang)
        ctx = self._base_context(
            locale,
            "about",
            f"{locale.slug + '/' if locale.slug else ''}about.html",
            f"{t['about']['title']} · {t['site']['name']}",
            t["about"]["lede"],
        )
        sources = [
            ("Eastmoney", "https://quote.eastmoney.com/", "quotes"),
            ("open.er-api.com", "https://www.exchangerate-api.com/", "fx"),
            ("Tom's Hardware", "https://www.tomshardware.com/", "news"),
            ("Semiconductor Digest", "https://www.semiconductor-digest.com/", "news"),
            ("EE Times", "https://www.eetimes.com/", "news"),
            ("DigiTimes", "https://www.digitimes.com/", "news"),
            ("Semiconductor Today", "https://www.semiconductor-today.com/", "news"),
        ]
        ctx.update(
            {
                "sources": sources,
                "snapshot": self.snapshot,
                "priced": sum(1 for row in self.analytics.rows if row.priced),
                "coverage_pct": round(self.analytics.coverage_ratio * 100, 1),
                "errors": self.snapshot.get("errors") or [],
            }
        )
        return ctx

    def _related_topics(self, stage_id: str) -> list[str]:
        mapping = {
            "eda_ip": ["value-chain", "metrics"],
            "design": ["value-chain", "metrics"],
            "manufacturing": ["process-flow", "lithography", "cycle"],
            "memory": ["memory-hbm", "cycle"],
            "equipment": ["equipment-materials", "lithography"],
            "materials": ["equipment-materials", "process-flow"],
            "packaging": ["advanced-packaging", "process-flow"],
            "module": ["memory-hbm", "cycle"],
        }
        return mapping.get(stage_id, ["value-chain"])

    # ---- payloads ------------------------------------------------------
    def _write_payloads(self) -> None:
        self._write_json_file("latest_data.json", self._legacy_payload())
        for locale in LOCALES:
            self._write_json_file(f"api/snapshot.{locale.lang}.json", self._localized_payload(locale))

    def _write_json_file(self, relative: str, payload: dict[str, Any]) -> None:
        path = self.output / relative
        write_json(path, payload)
        self.generated.append(relative)

    def _legacy_payload(self) -> dict[str, Any]:
        """Keeps the existing iOS client decodable while the web app moves to /api."""
        rows = sorted(self.analytics.rows, key=lambda row: row.market_cap_usd or 0, reverse=True)
        data = []
        kline: dict[str, Any] = {}
        for row in rows:
            company = row.company
            score = row.priority or 0
            grade = "A" if score >= 80 else "B" if score >= 65 else "C" if score >= 50 else "D"
            entry = {
                "code": company.ticker,
                "name": company.name("zh"),
                "english": company.name("en"),
                "region": company.hq,
                "business_type": self.taxonomy.stage_label(company.stage, "zh", short=True),
                "website": company.website,
                "price": row.price,
                "pe_trailing": row.pe,
                "pe_forward": None,
                "volume": row.entry.get("volume"),
                "market_cap": round(row.market_cap_local / 1e8, 2) if row.market_cap_local else None,
                "high52": row.high_52w,
                "low52": row.low_52w,
                "change_pct": row.change_1d,
                "board": company.exchange,
                "chain_segment": self.taxonomy.stage_label(company.stage, "zh"),
                "invest_score": row.priority,
                "invest_grade": grade,
                "invest_tags": ",".join(row.flags),
                "invest_reason": self._reason_zh(row),
                "is_pick": score >= 70,
            }
            data.append(entry)
            history = row.entry.get("history") or {}
            rows = [
                (d, o, h, l, c)
                for d, o, h, l, c in zip(
                    history.get("dates", []),
                    history.get("open", []),
                    history.get("high", []),
                    history.get("low", []),
                    history.get("close", []),
                )
                if None not in (o, h, l, c)
            ]
            if len(rows) >= 10 and len(kline) < 40:
                kline[f"{company.name('zh')}（{company.ticker}）"] = {
                    "code": company.ticker,
                    "market_cap": row.market_cap_local,
                    "business_type": self.taxonomy.stage_label(company.stage, "zh", short=True),
                    "chain_segment": self.taxonomy.stage_label(company.stage, "zh"),
                    "date": [item[0] for item in rows],
                    "open": [item[1] for item in rows],
                    "high": [item[2] for item in rows],
                    "low": [item[3] for item in rows],
                    "close": [item[4] for item in rows],
                    "change_30d": row.ret_30d or 0,
                }

        intro_docs = self.knowledge.get("zh", [])[:3]
        industry_intro = [f"{doc.title}：{doc.summary}" for doc in intro_docs]
        basics = [
            {"term": term["zh"]["term"], "desc": term["zh"]["def"]}
            for term in self.glossary[:9]
        ]
        news_pool = [
            {"title": item.get("title", ""), "link": item.get("link", ""), "date": item.get("published", "")}
            for item in (self.snapshot.get("news") or [])
        ]
        return {
            "schema_version": 2,
            "data": data,
            "news_pool": news_pool,
            "kline_data": kline,
            "industry_intro": industry_intro,
            "industry_basics": basics,
            "industry_source_refs": [{"name": name, "url": url} for name, url, _ in [
                ("Eastmoney", "https://quote.eastmoney.com/", "quotes"),
                ("SiliconScope methodology", f"{SITE_URL}/methodology.html", "method"),
            ]],
            "industry_intro_source": "SiliconScope knowledge base",
            "global_compare_items": [
                {
                    "source_name": item.get("source", ""),
                    "title": item.get("title", ""),
                    "summary": item.get("published", ""),
                    "url": item.get("link", ""),
                }
                for item in (self.snapshot.get("news") or [])[:6]
            ],
            "global_compare_refs": [{"name": "Eastmoney", "url": "https://quote.eastmoney.com/"}],
            "data_time": str(self.snapshot.get("generated_at") or "").replace("T", " ")[:19],
            "data_time_iso": str(self.snapshot.get("generated_at") or ""),
            "meta": {
                "generated_at": str(self.snapshot.get("generated_at") or ""),
                "coverage": self.analytics.coverage_ratio,
                "site_url": SITE_URL,
            },
        }

    @staticmethod
    def _reason_zh(row: Row) -> str:
        parts = []
        if row.quality is not None:
            parts.append(f"质量分 {row.quality:.0f}")
        if row.valuation is not None:
            parts.append(f"估值分 {row.valuation:.0f}")
        if row.momentum is not None:
            parts.append(f"动能分 {row.momentum:.0f}")
        if row.size is not None:
            parts.append(f"规模分 {row.size:.0f}")
        return "；".join(parts) if parts else "数据不足"

    def _localized_payload(self, locale: Locale) -> dict[str, Any]:
        lang = locale.lang
        return {
            "schema_version": 2,
            "locale": locale.code,
            "generated_at": self.snapshot.get("generated_at"),
            "dataset": self.snapshot.get("dataset"),
            "coverage": self.snapshot.get("coverage"),
            "fx": self.snapshot.get("fx"),
            "regime": self.analytics.regime,
            "stage_stats": {
                stage_id: {
                    "count": stat.count,
                    "market_cap_usd": stat.market_cap_usd,
                    "median_ret_30d": stat.median_ret_30d,
                    "median_pe": stat.median_pe,
                    "median_roe": stat.median_roe,
                    "breadth": stat.breadth,
                }
                for stage_id, stat in self.analytics.stage_stats.items()
            },
            "companies": [
                {
                    "id": row.company.id,
                    "name": self.views[lang][row.company.id]["name"],
                    "ticker": row.company.ticker,
                    "symbol": row.company.symbol,
                    "stage": row.company.stage,
                    "role": row.company.role,
                    "country": row.company.country,
                    "market": row.company.market,
                    "price": row.price,
                    "currency": row.company.currency,
                    "change_1d": row.change_1d,
                    "ret_30d": row.ret_30d,
                    "market_cap_usd": row.market_cap_usd,
                    "pe": row.pe,
                    "pb": row.pb,
                    "roe": row.roe,
                    "priority": row.priority,
                    "coverage": row.coverage,
                    "flags": row.flags,
                    "as_of": row.entry.get("as_of"),
                }
                for row in sorted(self.analytics.rows, key=lambda item: item.market_cap_usd or 0, reverse=True)
            ],
            "news": self.snapshot.get("news") or [],
            "errors": self.snapshot.get("errors") or [],
        }

    # ---- extras --------------------------------------------------------
    def _copy_assets(self) -> None:
        target = self.output / "assets"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(ASSETS_DIR, target)
        for path in sorted(target.rglob("*")):
            if path.is_file():
                self.generated.append(str(path.relative_to(self.output)))

    def _write_extras(self) -> None:
        write_text(self.output / ".nojekyll", "")
        self.generated.append(".nojekyll")

        specs: list[tuple[Locale, str, str | None]] = []
        for locale in LOCALES:
            for key in PAGES:
                specs.append((locale, key, None))
            for doc in self.knowledge[locale.lang]:
                specs.append((locale, "topic", doc.slug))
            for row in self.analytics.rows:
                specs.append((locale, "company", row.company.id))

        lastmod = self.build_time.date().isoformat()
        seen: set[str] = set()
        entries_list: list[str] = []
        for locale, key, slug in specs:
            path = self._page_path(locale, key, slug)
            if path in seen:
                continue
            seen.add(path)
            alternates = self.alternates(path, key, slug)
            links = "".join(
                f'<xhtml:link rel="alternate" hreflang="{alt["code"]}" href="{alt["absolute"]}"/>'
                for alt in alternates
            )
            links += f'<xhtml:link rel="alternate" hreflang="x-default" href="{alternates[0]["absolute"]}"/>'
            entries_list.append(
                f"<url><loc>{SITE_URL}/{path}</loc><lastmod>{lastmod}</lastmod>{links}</url>"
            )
        entries = "\n".join(entries_list)
        sitemap = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            f"{entries}\n</urlset>\n"
        )
        write_text(self.output / "sitemap.xml", sitemap)
        write_text(self.output / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
        self.generated.extend(["sitemap.xml", "robots.txt"])

        redirects = {
            "overview.html": "index.html",
            "charts.html": "companies.html",
            "risk-news.html": "knowledge.html",
            "data-center.html": "companies.html",
            "knowledge-old.html": "knowledge.html",
        }
        for source, target in redirects.items():
            html_text = self.env.get_template("redirect.html").render(
                lang="zh",
                t=bundle_for("zh"),
                root="",
                target=target,
                site_name=SITE_NAME,
                page_title=bundle_for("zh")["redirect"]["title"],
            )
            write_text(self.output / source, html_text)
            self.generated.append(source)

        not_found = self.env.get_template("404.html").render(
            **self._base_context(
                LOCALES[0],
                "home",
                "404.html",
                f"404 · {SITE_NAME}",
                bundle_for("zh")["notFound"]["body"],
            )
        )
        write_text(self.output / "404.html", not_found)
        self.generated.append("404.html")
