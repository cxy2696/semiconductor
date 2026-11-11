"""Snapshot orchestration: quotes, history, FX and news in one artifact.

A snapshot is the only input the static build needs. It is committed so the
site can always be rebuilt offline, and so a provider outage degrades into a
visible staleness flag instead of an empty page.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Iterable

from .config import SCHEMA_VERSION, SITE_TIMEZONE, SITE_VERSION, SNAPSHOT_DIR, SNAPSHOT_KEEP, SYMBOLS_FILE
from .sources import eastmoney
from .sources.fx import fetch_fx
from .sources.news import fetch_news
from .taxonomy import Taxonomy
from .universe import Company
from .utils import read_json, to_float, write_json


def latest_path():
    return SNAPSHOT_DIR / "latest.json"


def load_snapshot(path=None) -> dict[str, Any] | None:
    payload = read_json(path or latest_path())
    return payload if isinstance(payload, dict) else None


def load_symbol_cache() -> dict[str, Any]:
    payload = read_json(SYMBOLS_FILE, default={"schema": 1, "symbols": {}})
    if not isinstance(payload, dict) or not isinstance(payload.get("symbols"), dict):
        return {"schema": 1, "symbols": {}}
    return payload


def _fetch_one(company: Company, cache: dict[str, Any]) -> tuple[str, dict[str, Any] | None, str | None, dict[str, Any] | None]:
    import requests

    session = requests.Session()
    session.headers.update(eastmoney.HEADERS)
    try:
        resolved = eastmoney.resolve_secid(session, company, cache)
        if not resolved or not resolved.get("secid"):
            return company.id, None, f"{company.id}: symbol not resolved", resolved
        secid = resolved["secid"]
        quote = eastmoney.fetch_quote(session, secid)
        if not quote:
            return company.id, None, f"{company.id}: empty quote", resolved
        history = eastmoney.fetch_history(session, secid)
        entry = eastmoney.build_market_entry(company, quote, history, datetime.now(SITE_TIMEZONE))
        entry["symbol"] = secid
        entry["venue"] = company.quote_venue or company.exchange
        entry["resolved_name"] = resolved.get("name", "")
        return company.id, entry, None, resolved
    except Exception as exc:  # defensive: one bad symbol must not abort the batch
        return company.id, None, f"{company.id}: {exc.__class__.__name__}", None
    finally:
        session.close()


def _stale_entry(previous: dict[str, Any]) -> dict[str, Any]:
    entry = dict(previous)
    entry["status"] = "stale"
    return entry


def fetch_snapshot(
    companies: Iterable[Company],
    taxonomy: Taxonomy,
    previous: dict[str, Any] | None = None,
    max_workers: int = 6,
) -> dict[str, Any]:
    companies = list(companies)
    cache_payload = load_symbol_cache()
    cache = cache_payload.setdefault("symbols", {})
    previous_quotes = (previous or {}).get("quotes") or {}

    quotes: dict[str, Any] = {}
    errors: list[str] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_fetch_one, company, cache): company for company in companies}
        for future in as_completed(futures):
            company = futures[future]
            try:
                cid, entry, error, _ = future.result()
            except Exception as exc:
                cid, entry, error = company.id, None, f"{company.id}: {exc.__class__.__name__}"
            if entry:
                quotes[cid] = entry
            else:
                if error:
                    errors.append(error)
                if isinstance(previous_quotes.get(cid), dict):
                    quotes[cid] = _stale_entry(previous_quotes[cid])
                else:
                    quotes[cid] = {
                        "status": "missing",
                        "price": None,
                        "market_cap": None,
                        "pe": None,
                        "pb": None,
                        "roe": None,
                        "change_pct": None,
                        "ret_30d": None,
                        "high_52w": None,
                        "low_52w": None,
                        "currency": company.currency,
                        "as_of": None,
                        "source": "unavailable",
                        "history": {"dates": [], "open": [], "high": [], "low": [], "close": [], "volume": []},
                        "closes": [],
                    }

    write_json(
        SYMBOLS_FILE,
        {
            "schema": 1,
            "updated": datetime.now(SITE_TIMEZONE).isoformat(timespec="seconds"),
            "note": "Measured mapping from company id to Eastmoney secid. Edit only with a verified quote.",
            "symbols": cache,
        },
    )

    fx = fetch_fx((previous or {}).get("fx"))
    fx.setdefault("fetched_at", datetime.now(SITE_TIMEZONE).isoformat(timespec="seconds"))

    news, news_errors = fetch_news()
    errors.extend(news_errors)
    if not news and previous and isinstance(previous.get("news"), list):
        news = previous["news"]

    priced = sum(1 for entry in quotes.values() if to_float(entry.get("price")) is not None)
    generated_at = datetime.now(SITE_TIMEZONE)

    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "site_version": SITE_VERSION,
        "generated_at": generated_at.isoformat(timespec="seconds"),
        "dataset": "live" if len(companies) and priced / len(companies) >= 0.6 else "partial",
        "universe_size": len(companies),
        "coverage": {
            "priced": priced,
            "total": len(companies),
            "ratio": round(priced / len(companies), 4) if companies else 0.0,
        },
        "fx": fx,
        "quotes": quotes,
        "news": news,
        "errors": errors,
        "sources": {
            "quotes": "Eastmoney public quote API",
            "fx": fx.get("source", "unknown"),
            "news": "RSS: " + ", ".join(sorted({item.get("source", "") for item in news if item.get("source")})),
        },
    }
    return snapshot


def save_snapshot(snapshot: dict[str, Any]) -> list[Any]:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = str(snapshot.get("generated_at", ""))[:10] or datetime.now(SITE_TIMEZONE).date().isoformat()
    dated = SNAPSHOT_DIR / f"{stamp}.json"
    write_json(dated, snapshot)
    write_json(latest_path(), snapshot)

    files = sorted(SNAPSHOT_DIR.glob("*.json"), key=lambda path: path.name, reverse=True)
    removed = []
    for path in files:
        if path.name == "latest.json":
            continue
        if len([p for p in files if p.name != "latest.json"]) > SNAPSHOT_KEEP:
            try:
                path.unlink()
                removed.append(path)
            except OSError:
                pass
    return removed
