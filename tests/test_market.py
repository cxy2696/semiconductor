"""Refresh orchestration: batching, intraday reuse and the fallback guard."""

from __future__ import annotations

from datetime import datetime

from semcore import market
from semcore.sources import eastmoney


class StubCompany:
    def __init__(self, cid: str) -> None:
        self.id = cid
        self.currency = "USD"
        self.is_priced = True
        self.ticker = cid.upper()
        self.market = "US"
        self.name = "Stub"


def make_history(count: int = 40) -> list[dict[str, float | str]]:
    return [
        {
            "date": f"2026-09-{index + 1:02d}",
            "open": 100.0 + index,
            "close": 100.0 + index,
            "high": 101.0 + index,
            "low": 99.0 + index,
            "volume": 1000.0,
        }
        for index in range(count)
    ]


def test_batch_row_maps_onto_quote_fields():
    row = {
        "f2": 106.44,
        "f3": -3.67,
        "f5": 393341,
        "f8": 1.97,
        "f12": "688981",
        "f13": 1,
        "f18": 110.5,
        "f20": 911386035899,
        "f23": 5.27,
        "f37": 4.6,
        "f115": 106.76,
    }
    quote = eastmoney.batch_item_to_quote(row)
    assert quote["f43"] == 106.44
    assert quote["f60"] == 110.5
    assert quote["f170"] == -3.67
    assert quote["f164"] == 106.76
    assert quote["f173"] == 4.6
    assert quote["f116"] == 911386035899


def test_history_is_reused_only_within_the_same_day():
    previous = {"status": "ok", "history_date": "2026-11-16", "as_of": "2026-11-15", "closes": [1.0] * 31}
    assert market._reusable_history(previous, "2026-11-16")
    assert not market._reusable_history(previous, "2026-11-17")
    stale = dict(previous, status="stale")
    assert not market._reusable_history(stale, "2026-11-16")
    assert not market._reusable_history(None, "2026-11-16")


def _patch(monkeypatch, companies, quotes, fetched_history=None):
    cache = {"symbols": {company.id: {"secid": f"105.{company.id.upper()}", "name": company.id} for company in companies}}
    monkeypatch.setattr(market, "load_symbol_cache", lambda: cache)
    monkeypatch.setattr(market, "write_json", lambda *args, **kwargs: None)
    monkeypatch.setattr(market, "fetch_fx", lambda previous: {"usd_per_unit": {"USD": 1.0}, "source": "test"})
    monkeypatch.setattr(market, "fetch_news", lambda: ([], []))
    monkeypatch.setattr(eastmoney, "fetch_batch", lambda session, secids: {secid: quotes[secid] for secid in secids if secid in quotes})
    monkeypatch.setattr(eastmoney, "fetch_quote", lambda session, secid: quotes.get(secid))
    monkeypatch.setattr(eastmoney, "fetch_history", lambda session, secid, history_days=420: fetched_history or make_history())


def test_full_refresh_builds_entries(monkeypatch):
    companies = [StubCompany(name) for name in ("aaa", "bbb")]
    quotes = {f"105.{company.id.upper()}": {"f43": 10.0, "f60": 9.0, "f170": 11.1, "f47": 100, "f116": 1e9, "f164": 20.0, "f167": 2.0, "f173": 15.0, "f168": 1.0} for company in companies}
    _patch(monkeypatch, companies, quotes)
    snapshot = market.fetch_snapshot(companies, taxonomy=None)
    assert snapshot["dataset"] == "live"
    assert snapshot["fresh_quotes"] == 2
    assert snapshot["stale_quotes"] == 0
    entry = snapshot["quotes"]["aaa"]
    assert entry["status"] == "ok"
    assert entry["price"] == 10.0
    assert entry["history_date"] == datetime.now(market.SITE_TIMEZONE).date().isoformat()
    assert entry["ret_30d"] is not None


def test_mostly_failed_refresh_keeps_the_previous_snapshot(monkeypatch):
    companies = [StubCompany(f"c{index}") for index in range(10)]
    quotes = {"105.C0": {"f43": 10.0}}
    _patch(monkeypatch, companies, quotes)
    previous = {"generated_at": "2026-11-15T08:00:00+08:00", "quotes": {c.id: {"price": 1.0} for c in companies}, "errors": []}
    snapshot = market.fetch_snapshot(companies, taxonomy=None, previous=previous)
    assert snapshot["generated_at"] == previous["generated_at"]
    assert snapshot["quotes"] == previous["quotes"]
    assert any("refresh aborted" in note for note in snapshot["errors"])


def test_failed_history_keeps_the_previous_series(monkeypatch):
    companies = [StubCompany("aaa")]
    quotes = {"105.AAA": {"f43": 12.0, "f60": 11.0, "f170": 9.1, "f47": 10, "f116": 1e9, "f164": 20.0, "f167": 2.0, "f173": 15.0, "f168": 1.0}}
    _patch(monkeypatch, companies, quotes)
    monkeypatch.setattr(eastmoney, "fetch_history", lambda session, secid, history_days=420: [])
    previous = {
        "generated_at": "2026-11-15T08:00:00+08:00",
        "quotes": {
            "aaa": {
                "status": "ok",
                "price": 11.0,
                "closes": [10.0] * 31,
                "history": {"dates": ["2026-11-14"], "open": [1], "high": [1], "low": [1], "close": [11.0], "volume": [1]},
                "history_date": "2026-11-15",
                "as_of": "2026-11-14",
            }
        },
    }
    snapshot = market.fetch_snapshot(companies, taxonomy=None, previous=previous)
    entry = snapshot["quotes"]["aaa"]
    assert entry["status"] == "ok"
    assert entry["price"] == 12.0
    assert entry["history_stale"] is True
    assert entry["closes"] == [10.0] * 31


def test_partial_refresh_is_marked(monkeypatch):
    companies = [StubCompany(f"p{index}") for index in range(10)]
    quotes = {f"105.P{index}": {"f43": 10.0} for index in range(6)}
    _patch(monkeypatch, companies, quotes)
    snapshot = market.fetch_snapshot(companies, taxonomy=None)
    assert snapshot["dataset"] == "partial"
    assert snapshot["fresh_quotes"] == 6
    assert snapshot["stale_quotes"] == 4
