from __future__ import annotations

import json
from pathlib import Path

from semcore.build import SiteBuilder
from semcore.validate import validate_artifacts


def test_build_all_locales(tmp_path: Path, snapshot):
    builder = SiteBuilder(snapshot=snapshot, output=tmp_path / "site")
    manifest = builder.build()
    site = tmp_path / "site"
    assert manifest["pages"] > 600
    for relative in (
        "index.html",
        "zh/index.html",
        "ja/index.html",
        "de/index.html",
        "companies.html",
        "value-chain.html",
        "methodology.html",
        "guide.html",
        "status.html",
        "en/index.html",
    ):
        assert (site / relative).exists(), relative
    company_pages = list((site / "companies").glob("*.html"))
    assert len(company_pages) >= 150
    for prefix in ("zh", "ja", "de"):
        assert len(list((site / prefix / "companies").glob("*.html"))) >= 150
    topic_pages = list((site / "knowledge").glob("*.html"))
    assert len(topic_pages) >= 12
    legacy = json.loads((site / "latest_data.json").read_text(encoding="utf-8"))
    for key in ("data", "news_pool", "kline_data", "industry_basics", "data_time_iso"):
        assert key in legacy
    assert (site / "sitemap.xml").exists()
    search_index = json.loads((site / "api/search.en.json").read_text(encoding="utf-8"))
    assert len(search_index["entries"]) > 200
    assert {entry["type"] for entry in search_index["entries"]} >= {"company", "topic", "term", "page"}
    live = json.loads((site / "api/quotes.json").read_text(encoding="utf-8"))
    assert live["generated_at"]
    assert live["priced"] > 0
    assert len(live["quotes"]) == live["priced"]
    sample = next(iter(live["quotes"].values()))
    assert {"price", "change", "currency", "market_cap_usd", "as_of"} <= set(sample)
    assert not validate_artifacts(site)


def test_pages_expose_live_quote_hooks(tmp_path: Path, snapshot):
    builder = SiteBuilder(snapshot=snapshot, output=tmp_path / "site")
    builder.build()
    site = tmp_path / "site"
    companies = (site / "companies.html").read_text(encoding="utf-8")
    assert "api/quotes.json" in companies
    assert "data-quote=" in companies
    assert "data-live-price" in companies
    assert "data-live-change" in companies
    home = (site / "index.html").read_text(encoding="utf-8")
    assert "data-live-total-mcap" in home
    assert 'id="theme-color"' in home


def test_no_external_assets(tmp_path: Path, snapshot):
    builder = SiteBuilder(snapshot=snapshot, output=tmp_path / "site")
    builder.build()
    for path in (tmp_path / "site").rglob("*.html"):
        html = path.read_text(encoding="utf-8")
        assert "<script src=\"http" not in html
        assert "<link rel=\"stylesheet\" href=\"http" not in html
