"""Snapshot orchestration: quotes, history, FX and news in one artifact.

A snapshot is the only input the static build needs. It is committed so the
site can always be rebuilt offline, and so a provider outage degrades into a
visible staleness flag instead of an empty page.

Quotes are fetched through Eastmoney's list endpoint, which answers for 40
symbols per request; a per-symbol loop trips the provider's rate limit and
leaves most of the universe stale. Daily history is fetched once per calendar
day and reused by the intraday refreshes.
"""

from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Iterable, Sequence

from .config import SCHEMA_VERSION, SITE_TIMEZONE, SITE_VERSION, SNAPSHOT_DIR, SNAPSHOT_KEEP, SYMBOLS_FILE
from .sources import eastmoney
from .sources.fx import fetch_fx
from .sources.news import fetch_news
from .taxonomy import Taxonomy
from .universe import Company
from .utils import read_json, to_float, write_json

# Below this share of freshly fetched quotes the previous snapshot is kept
# whole: a half-refreshed page is harder to trust than a clearly old one.
MIN_FRESH_RATIO = 0.5


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


def _chunks(items: Sequence[str], size: int) -> Iterable[Sequence[str]]:
    for start in range(0, len(items), size):
        yield items[start : start + size]


def _missing_entry(company: Company) -> dict[str, Any]:
    return {
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


def _stale_entry(previous: dict[str, Any]) -> dict[str, Any]:
    entry = dict(previous)
    entry["status"] = "stale"
    return entry


def _resolve_symbols(companies: list[Company], cache: dict[str, Any]) -> dict[str, dict[str, Any]]:
    resolved: dict[str, dict[str, Any]] = {}
    pending: list[Company] = []
    for company in companies:
        record = cache.get(company.id)
        if isinstance(record, dict):
            resolved[company.id] = record
        else:
            pending.append(company)
    if not pending:
        return resolved
    session = eastmoney.make_session()
    for company in pending:
        try:
            record = eastmoney.resolve_secid(session, company, cache)
        except Exception:
            record = None
        resolved[company.id] = record or {"secid": None}
        time.sleep(0.3)
    return resolved


def _fetch_quotes(companies: list[Company], resolved: dict[str, dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Fetch quotes for every resolvable symbol, batched by the list endpoint."""
    owner: dict[str, Company] = {}
    errors: list[str] = []
    for company in companies:
        secid = (resolved.get(company.id) or {}).get("secid")
        if secid:
            owner.setdefault(secid, company)
        elif company.is_priced:
            errors.append(f"{company.id}: no verified quote symbol")

    session = eastmoney.make_session()
    raw: dict[str, dict[str, Any]] = {}
    secids = sorted(owner)
    for batch in _chunks(secids, eastmoney.BATCH_LIMIT):
        rows = eastmoney.fetch_batch(session, list(batch))
        if not rows:
            errors.append(f"quote batch of {len(batch)} symbols returned no rows")
        raw.update(rows)
        time.sleep(0.4)

    # Second pass, one symbol at a time. A batch can fail on its own without
    # the rest of the run being unhealthy.
    for secid in [secid for secid in secids if secid not in raw]:
        quote = eastmoney.fetch_quote(session, secid)
        if quote:
            raw[secid] = quote
        else:
            errors.append(f"{secid}: empty quote response")
        time.sleep(0.2)

    quotes: dict[str, dict[str, Any]] = {}
    for secid, company in owner.items():
        if secid in raw:
            quotes[company.id] = raw[secid]
    return quotes, errors


def _reusable_history(previous: dict[str, Any] | None, today: str) -> bool:
    if not isinstance(previous, dict):
        return False
    if previous.get("status") != "ok":
        return False
    if previous.get("history_date") != today:
        return False
    if not previous.get("as_of"):
        return False
    return len(previous.get("closes") or []) >= 31


def fetch_snapshot(
    companies: Iterable[Company],
    taxonomy: Taxonomy,
    previous: dict[str, Any] | None = None,
    max_workers: int = 4,
) -> dict[str, Any]:
    companies = list(companies)
    cache_payload = load_symbol_cache()
    cache = cache_payload.setdefault("symbols", {})
    previous_quotes = (previous or {}).get("quotes") or {}
    now = datetime.now(SITE_TIMEZONE)
    today = now.date().isoformat()

    resolved = _resolve_symbols(companies, cache)
    quotes, errors = _fetch_quotes(companies, resolved)

    entries: dict[str, Any] = {}
    # The first run of the day replaces every history; later runs only retry a
    # few failures, which keeps the daily-history endpoint out of the way of the
    # intraday schedule (and out of its rate limit).
    missing_history = sum(1 for company in companies if not _reusable_history(previous_quotes.get(company.id), today))
    history_budget = max(12, missing_history)
    budget_lock = threading.Lock()

    def build(company: Company) -> tuple[str, dict[str, Any] | None]:
        nonlocal history_budget
        quote = quotes.get(company.id)
        if not quote:
            return company.id, None
        prior = previous_quotes.get(company.id)
        if _reusable_history(prior, today):
            return company.id, eastmoney.merge_quote(prior, quote, company, now)
        secid = (resolved.get(company.id) or {}).get("secid")
        if not secid:
            return company.id, None
        exhausted = False
        with budget_lock:
            if history_budget > 0:
                history_budget -= 1
            else:
                exhausted = True
        history: list[dict[str, Any]] = []
        session = None if exhausted else eastmoney.make_session()
        if session is not None:
            try:
                for attempt in range(2):
                    time.sleep(0.25)  # the daily-history endpoint throttles bursts
                    history = eastmoney.fetch_history(session, secid)
                    if history:
                        break
                    time.sleep(0.8 + attempt)
            finally:
                session.close()
        if not history:
            # Keep the last known series rather than publishing a company with
            # no chart and no 30-day return; the next run retries the history.
            if isinstance(prior, dict) and prior.get("closes"):
                entry = eastmoney.merge_quote(prior, quote, company, now)
                entry["history_stale"] = True
                return company.id, entry
            return company.id, None
        entry = eastmoney.build_market_entry(company, quote, history, now)
        entry["history_date"] = today
        entry["quote_as_of"] = today
        return company.id, entry

    if quotes:
        history_workers = max(1, min(max_workers, 2))
        with ThreadPoolExecutor(max_workers=history_workers) as executor:
            futures = {executor.submit(build, company): company for company in companies if company.id in quotes}
            for future in as_completed(futures):
                company = futures[future]
                try:
                    cid, entry = future.result()
                except Exception as exc:  # one bad symbol must not abort the batch
                    cid, entry = company.id, None
                    errors.append(f"{company.id}: request failed ({exc.__class__.__name__})")
                if entry:
                    entries[cid] = entry

    for company in companies:
        if company.id in entries:
            continue
        prior = previous_quotes.get(company.id)
        entries[company.id] = _stale_entry(prior) if isinstance(prior, dict) else _missing_entry(company)

    total = len(companies)
    priced = sum(1 for entry in entries.values() if to_float(entry.get("price")) is not None)
    fresh = sum(1 for entry in entries.values() if entry.get("status") == "ok" and entry.get("quote_as_of") == today)
    fresh_ratio = fresh / total if total else 0.0

    if previous and total and fresh_ratio < MIN_FRESH_RATIO:
        kept = dict(previous)
        notes = [f"refresh aborted: only {fresh}/{total} quotes fetched, previous snapshot kept"]
        kept["errors"] = notes + [str(item) for item in (previous.get("errors") or [])][:5]
        return kept

    write_json(
        SYMBOLS_FILE,
        {
            "schema": 1,
            "updated": now.isoformat(timespec="seconds"),
            "note": "Measured mapping from company id to Eastmoney secid. Edit only with a verified quote.",
            "symbols": cache,
        },
    )

    fx = fetch_fx((previous or {}).get("fx"))
    fx.setdefault("fetched_at", now.isoformat(timespec="seconds"))

    news, news_errors = fetch_news()
    errors.extend(news_errors)
    if not news and previous and isinstance(previous.get("news"), list):
        news = previous["news"]

    if fresh_ratio >= 0.85:
        dataset = "live"
    elif fresh_ratio >= MIN_FRESH_RATIO:
        dataset = "partial"
    else:
        dataset = "stale"

    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "site_version": SITE_VERSION,
        "generated_at": now.isoformat(timespec="seconds"),
        "dataset": dataset,
        "universe_size": total,
        "fresh_quotes": fresh,
        "stale_quotes": total - fresh,
        "coverage": {
            "priced": priced,
            "total": total,
            "ratio": round(priced / total, 4) if total else 0.0,
        },
        "fx": fx,
        "quotes": entries,
        "news": news,
        "errors": errors[:40],
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
