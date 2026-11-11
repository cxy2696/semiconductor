"""Validation for data contracts and generated artifacts.

`python -m semcore validate` runs both. CI runs data-only checks on pull
requests and full checks after a build.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .config import DOCS_DIR, LOCALES, ROOT, SITE_URL
from .content import load_all_knowledge, load_glossary
from .i18n import flatten, load_bundle
from .taxonomy import Taxonomy
from .universe import UniverseError, load_universe

REQUIRED_LEGACY_KEYS = (
    "data",
    "news_pool",
    "kline_data",
    "industry_intro",
    "industry_basics",
    "industry_source_refs",
    "industry_intro_source",
    "global_compare_items",
    "global_compare_refs",
    "data_time",
    "data_time_iso",
)

ASSET_PATTERNS = (
    re.compile(r"<(?:script|img)\b[^>]*\bsrc=[\"'](?:https?:)?//", re.IGNORECASE),
    re.compile(r"<link\b[^>]*\brel=[\"'](?:stylesheet|preload|modulepreload)[\"'][^>]*\bhref=[\"'](?:https?:)?//", re.IGNORECASE),
)


def validate_data() -> list[str]:
    errors: list[str] = []
    taxonomy = Taxonomy.load()

    try:
        companies = load_universe(taxonomy=taxonomy)
    except UniverseError as exc:
        return [f"universe: {problem}" for problem in exc.problems]

    if len(companies) < 80:
        errors.append(f"universe: expected at least 80 companies, found {len(companies)}")

    bundles = load_bundle()
    base_keys = set(flatten(bundles["zh"]))
    for locale in LOCALES:
        keys = set(flatten(bundles[locale.lang]))
        missing = sorted(base_keys - keys)
        extra = sorted(keys - base_keys)
        if missing:
            errors.append(f"i18n[{locale.lang}]: missing keys {missing[:6]}")
        if extra:
            errors.append(f"i18n[{locale.lang}]: unexpected keys {extra[:6]}")

    knowledge = load_all_knowledge()
    base_slugs = [doc.slug for doc in knowledge["en"]]
    if not base_slugs:
        errors.append("knowledge: no English documents found")
    if len(base_slugs) < 12:
        errors.append(f"knowledge: expected at least 12 topics, found {len(base_slugs)}")
    for locale in LOCALES:
        slugs = [doc.slug for doc in knowledge[locale.lang]]
        if slugs != base_slugs:
            errors.append(
                f"knowledge[{locale.lang}]: slug mismatch (missing={sorted(set(base_slugs) - set(slugs))}, extra={sorted(set(slugs) - set(base_slugs))})"
            )
        for doc in knowledge[locale.lang]:
            if not doc.title or not doc.summary:
                errors.append(f"knowledge[{locale.lang}]: {doc.slug} missing title/summary")
            for related in doc.related:
                if related not in base_slugs:
                    errors.append(f"knowledge[{locale.lang}]: {doc.slug} references unknown topic '{related}'")

    glossary = load_glossary()
    if len(glossary) < 40:
        errors.append(f"glossary: expected at least 40 terms, found {len(glossary)}")
    for term in glossary:
        for key in ("zh", "en", "ja", "de"):
            if not term.get(key, {}).get("term") or not term.get(key, {}).get("def"):
                errors.append(f"glossary: {term.get('id')} missing {key} term/definition")

    return errors


DOC_BASES = ("README", "CHANGELOG", "CONTRIBUTING")
DOC_SUFFIXES = ("en", "cn", "jp", "de")


def validate_docs() -> list[str]:
    errors: list[str] = []
    for base in DOC_BASES:
        for suffix in DOC_SUFFIXES:
            path = ROOT / f"{base}_{suffix}.md"
            if not path.exists():
                errors.append(f"docs: missing {path.name}")
    for base in ("PRODUCT", "ARCHITECTURE", "DATA", "METHODOLOGY", "OPERATIONS", "ROADMAP"):
        for suffix in DOC_SUFFIXES:
            path = ROOT / "documentation" / f"{base}_{suffix}.md"
            if not path.exists():
                errors.append(f"docs: missing documentation/{path.name}")
    for suffix in DOC_SUFFIXES:
        path = ROOT / "ios" / f"README_{suffix}.md"
        if not path.exists():
            errors.append(f"docs: missing ios/{path.name}")
    return errors


def validate_artifacts(docs_dir: Path | None = None) -> list[str]:
    docs = Path(docs_dir or DOCS_DIR)
    errors: list[str] = []
    if not (docs / "index.html").exists():
        return [f"artifacts: {docs / 'index.html'} is missing (run `python -m semcore build`)"]

    required = [
        "index.html",
        "companies.html",
        "value-chain.html",
        "knowledge.html",
        "glossary.html",
        "methodology.html",
        "about.html",
        "404.html",
        "sitemap.xml",
        "robots.txt",
        "latest_data.json",
        ".nojekyll",
        "assets/css/main.css",
        "assets/js/app.js",
        "en/index.html",
        "zh/index.html",
        "ja/index.html",
        "de/index.html",
        "api/snapshot.en.json",
        "api/snapshot.zh.json",
        "api/snapshot.ja.json",
        "api/snapshot.de.json",
    ]
    for relative in required:
        if not (docs / relative).exists():
            errors.append(f"artifacts: missing {relative}")

    for locale in LOCALES:
        payload_path = docs / f"api/snapshot.{locale.lang}.json"
        if not payload_path.exists():
            errors.append(f"artifacts: missing {payload_path.relative_to(docs)}")
            continue
        try:
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"artifacts: {payload_path.name} is not valid JSON ({exc})")
            continue
        if not payload.get("companies"):
            errors.append(f"artifacts: {payload_path.name} has no companies")
        if payload.get("schema_version") != 2:
            errors.append(f"artifacts: {payload_path.name} schema_version != 2")

    legacy_path = docs / "latest_data.json"
    if legacy_path.exists():
        try:
            legacy = json.loads(legacy_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"artifacts: latest_data.json is not valid JSON ({exc})")
        else:
            missing = [key for key in REQUIRED_LEGACY_KEYS if key not in legacy]
            if missing:
                errors.append(f"artifacts: latest_data.json missing legacy keys {missing}")
            if not isinstance(legacy.get("data"), list) or not legacy["data"]:
                errors.append("artifacts: latest_data.json data is empty")
            required_stock = {"code", "name", "price", "invest_score", "is_pick"}
            for item in legacy.get("data", [])[:5]:
                missing_stock = required_stock - set(item)
                if missing_stock:
                    errors.append(f"artifacts: legacy stock missing {missing_stock}")
                    break

    sitemap_path = docs / "sitemap.xml"
    if sitemap_path.exists():
        sitemap = sitemap_path.read_text(encoding="utf-8")
        if SITE_URL not in sitemap:
            errors.append("artifacts: sitemap does not use the configured SITE_URL")
        for locale in LOCALES:
            prefix = f"{locale.slug}/" if locale.slug else ""
            if f"{SITE_URL}/{prefix}index.html" not in sitemap:
                errors.append(f"artifacts: sitemap missing {prefix}index.html")

    for locale in LOCALES:
        prefix = f"{locale.slug}/" if locale.slug else ""
        home = docs / f"{prefix}index.html"
        if not home.exists():
            continue
        html = home.read_text(encoding="utf-8")
        if any(pattern.search(html) for pattern in ASSET_PATTERNS):
            errors.append(f"artifacts: {home.relative_to(docs)} loads a third-party asset (CDN not allowed)")
        if f'lang="{locale.code}"' not in html:
            errors.append(f"artifacts: {home.relative_to(docs)} missing html lang")
        if "hreflang" not in html:
            errors.append(f"artifacts: {home.relative_to(docs)} missing hreflang alternates")

    company_dir = docs / "companies"
    if company_dir.exists():
        pages = list(company_dir.glob("*.html"))
        if len(pages) < 150:
            errors.append(f"artifacts: only {len(pages)} company pages generated")
    return errors


def validate_all(docs_dir: Path | None = None, data_only: bool = False) -> list[str]:
    errors = validate_data()
    if not data_only:
        errors.extend(validate_docs())
        errors.extend(validate_artifacts(docs_dir))
    return errors
