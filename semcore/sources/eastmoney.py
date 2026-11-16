"""Eastmoney public quote adapter.

The adapter resolves one primary listing per company, then pulls a delayed
quote and a daily OHLC history from Eastmoney's public endpoints. It is the
only quote provider used by the build, which keeps field semantics consistent
across markets.

Endpoints are undocumented and can change; failures are expected and must
degrade to the last verified snapshot rather than break the build.
"""

from __future__ import annotations

import random
import time
from datetime import date, datetime
from typing import Any, Sequence

import requests

from ..config import SITE_TIMEZONE
from ..universe import Company
from ..utils import to_float

QUOTE_URL = "https://push2.eastmoney.com/api/qt/stock/get"
BATCH_URL = "https://push2.eastmoney.com/api/qt/ulist.np/get"
KLINE_URL = "https://push2his.eastmoney.com/api/qt/stock/kline/get"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://quote.eastmoney.com/",
}

QUOTE_FIELDS = ",".join(
    [
        "f43",  # latest price
        "f44",  # session high
        "f45",  # session low
        "f46",  # open
        "f47",  # volume
        "f48",  # turnover value
        "f57",  # code
        "f58",  # name
        "f59",  # decimal places
        "f60",  # previous close
        "f116",  # total market cap (local currency)
        "f164",  # static P/E
        "f167",  # P/B
        "f168",  # turnover rate (%)
        "f170",  # change (%)
        "f173",  # ROE (%)
    ]
)

KLINE_FIELDS = "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"

# The list endpoint answers for many symbols at once and carries the same fields
# under different numbers. One request per 40 symbols keeps the refresh far below
# the rate limit that a per-symbol loop runs into.
BATCH_FIELDS = "f2,f3,f5,f8,f12,f13,f18,f20,f23,f37,f115"
BATCH_LIMIT = 40


class EastmoneyError(RuntimeError):
    pass


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


def _get_json(session: requests.Session, url: str, params: dict[str, Any], retries: int = 2) -> dict[str, Any] | None:
    for attempt in range(retries + 1):
        try:
            response = session.get(url, params=params, timeout=15)
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, dict):
                return payload
        except (requests.RequestException, ValueError):
            pass
        if attempt < retries:
            time.sleep(0.6 * (attempt + 1) + random.random() * 0.3)
    return None


def _number(data: dict[str, Any], key: str) -> float | None:
    if not isinstance(data, dict):
        return None
    return to_float(data.get(key))


def _code_matches(expected: str, actual: str) -> bool:
    expected = str(expected).strip().upper()
    actual = str(actual).strip().upper()
    if expected == actual:
        return True
    if expected.isdigit() and actual.isdigit():
        return int(expected) == int(actual)
    return False


def candidate_secids(company: Company) -> list[str]:
    ticker = company.ticker.strip().upper()
    if company.market == "CN":
        preferred = [f"1.{ticker}", f"0.{ticker}"] if ticker.startswith(("6", "9")) else [f"0.{ticker}", f"1.{ticker}"]
        return preferred
    if company.market == "HK":
        return [f"116.{ticker.zfill(5)}"]
    if company.market == "TW":
        return [f"178.{ticker}", f"179.{ticker}"]
    if company.market == "US":
        return [f"105.{ticker}", f"106.{ticker}", f"107.{ticker}"]
    if company.market == "JP":
        return [f"176.{ticker}"]
    if company.market == "KR":
        return [f"177.{ticker}"]
    if company.market == "EU":
        # European venues exposed by Eastmoney use several market numbers and
        # sometimes a local-language mnemonic, so the symbol is seeded in
        # data/symbols.json and only probed here as a fallback.
        return [f"185.{ticker}", f"186.{ticker}", f"155.{ticker}"]
    return []


def resolve_secid(
    session: requests.Session,
    company: Company,
    cache: dict[str, Any],
) -> dict[str, Any] | None:
    """Resolve and verify a secid for ``company``; updates ``cache`` in place."""
    cached = cache.get(company.id)
    if isinstance(cached, dict):
        if cached.get("secid") is None:
            return None
        return cached
    if not company.is_priced:
        cache[company.id] = {
            "secid": None,
            "name": company.name("en"),
            "method": "unpriced",
            "checked": date.today().isoformat(),
        }
        return None

    for secid in candidate_secids(company):
        payload = _get_json(session, QUOTE_URL, {"secid": secid, "fltt": 2, "invt": 2, "fields": QUOTE_FIELDS})
        data = (payload or {}).get("data") or {}
        if not isinstance(data, dict) or not data:
            continue
        if _code_matches(company.ticker, data.get("f57", "")):
            record = {
                "secid": secid,
                "name": str(data.get("f58") or ""),
                "method": "probe",
                "checked": date.today().isoformat(),
            }
            cache[company.id] = record
            return record

    cache[company.id] = {
        "secid": None,
        "name": company.name("en"),
        "method": "unresolved",
        "checked": date.today().isoformat(),
    }
    return None


def batch_item_to_quote(item: dict[str, Any]) -> dict[str, Any]:
    """Map a list-endpoint row onto the single-quote field names."""
    return {
        "f43": item.get("f2"),   # price
        "f47": item.get("f5"),   # volume
        "f60": item.get("f18"),  # previous close
        "f116": item.get("f20"), # total market cap (local)
        "f164": item.get("f115"),# static P/E
        "f167": item.get("f23"), # P/B
        "f168": item.get("f8"),  # turnover
        "f170": item.get("f3"),  # change %
        "f173": item.get("f37"), # ROE
        "f57": item.get("f12"),
        "f58": item.get("f14"),
    }


def fetch_batch(session: requests.Session, secids: Sequence[str]) -> dict[str, dict[str, Any]]:
    """Fetch quotes for many symbols in one request, keyed by secid."""
    payload = _get_json(
        session,
        BATCH_URL,
        {"fltt": 2, "invt": 2, "secids": ",".join(secids), "fields": BATCH_FIELDS},
        retries=2,
    )
    data = (payload or {}).get("data") or {}
    rows = data.get("diff") or []
    if isinstance(rows, dict):
        rows = list(rows.values())
    quotes: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        code = str(row.get("f12") or "").strip()
        market = row.get("f13")
        if not code or market is None:
            continue
        quotes[f"{int(market)}.{code}"] = batch_item_to_quote(row)
    return quotes


def fetch_quote(session: requests.Session, secid: str) -> dict[str, Any] | None:
    payload = _get_json(
        session,
        QUOTE_URL,
        {"secid": secid, "fltt": 2, "invt": 2, "fields": QUOTE_FIELDS},
    )
    data = (payload or {}).get("data")
    return data if isinstance(data, dict) and data else None


def fetch_history(session: requests.Session, secid: str, history_days: int = 420) -> list[dict[str, Any]]:
    today = datetime.now(SITE_TIMEZONE).date()
    begin = date.fromordinal(today.toordinal() - history_days).strftime("%Y%m%d")
    payload = _get_json(
        session,
        KLINE_URL,
        {
            "secid": secid,
            "klt": 101,  # daily
            "fqt": 1,  # forward adjusted
            "beg": begin,
            "end": today.strftime("%Y%m%d"),
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": KLINE_FIELDS,
        },
        retries=3,
    )
    rows = ((payload or {}).get("data") or {}).get("klines")
    if not isinstance(rows, list):
        return []
    history: list[dict[str, Any]] = []
    for row in rows:
        parts = str(row).split(",")
        if len(parts) < 6:
            continue
        day = parts[0]
        close = to_float(parts[2])
        if close is None:
            continue
        history.append(
            {
                "date": day,
                "open": to_float(parts[1]),
                "close": close,
                "high": to_float(parts[3]),
                "low": to_float(parts[4]),
                "volume": to_float(parts[5]),
            }
        )
    return history


# Splits happen in every market, but Eastmoney's forward adjustment (fqt=1) is
# not applied on every venue. When it is missing, a 5:1 split looks like a -80%
# one-day crash and every return computed from the series is wrong.
SPLIT_FACTORS = (2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20)
SPLIT_TOLERANCE = 0.12  # a split day also moves, so the ratio is not exact
RETURN_LIMIT = 300.0  # percent; beyond this a 30-session return is not credible


def detect_split_events(history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return day-over-day drops that match a split factor rather than a fall.

    A one-day move only counts as a split when the ratio lands within 12% of a
    common factor (2, 3, 5, 10 ...). Genuine crashes are rarely that close to a
    round factor, so the rule stays conservative on purpose.
    """
    events: list[dict[str, Any]] = []
    for index in range(1, len(history)):
        previous = history[index - 1].get("close")
        current = history[index].get("close")
        if not previous or not current or current <= 0:
            continue
        ratio = previous / current
        if ratio < SPLIT_FACTORS[0] * (1 - SPLIT_TOLERANCE):
            continue
        for factor in SPLIT_FACTORS:
            if abs(ratio - factor) <= factor * SPLIT_TOLERANCE:
                events.append({"index": index, "factor": factor, "date": history[index].get("date")})
                break
    return events


def _split_scales(length: int, events: list[dict[str, Any]]) -> list[float]:
    """Multiplier per bar that makes a split series continuous again.

    Prices before a 5:1 split are divided by five, so the whole series reads in
    today's share terms — the same basis as the live quote.
    """
    by_index = {int(event["index"]): float(event["factor"]) for event in events}
    scales = [1.0] * length
    running = 1.0
    for index in range(length - 1, -1, -1):
        scales[index] = running
        if index in by_index:
            running /= by_index[index]
    return scales


def _continuous_series(history: list[dict[str, Any]], events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not events:
        return history
    scales = _split_scales(len(history), events)
    adjusted: list[dict[str, Any]] = []
    for index, row in enumerate(history):
        scale = scales[index]
        adjusted.append(
            {
                **row,
                "open": row["open"] * scale if row.get("open") is not None else None,
                "close": row["close"] * scale if row.get("close") is not None else None,
                "high": row["high"] * scale if row.get("high") is not None else None,
                "low": row["low"] * scale if row.get("low") is not None else None,
            }
        )
    return adjusted


def build_market_entry(
    company: Company,
    quote: dict[str, Any],
    history: list[dict[str, Any]],
    fetched_at: datetime,
) -> dict[str, Any]:
    price = _number(quote, "f43")
    prev_close = _number(quote, "f60")
    change = _number(quote, "f170")
    if change is None and price is not None and prev_close:
        change = (price - prev_close) / prev_close * 100.0

    splits = detect_split_events(history)
    series = _continuous_series(history, splits)

    closes = [row["close"] for row in series if row.get("close") is not None]
    window = series[-250:]
    high_52w = max((row["high"] for row in window if row.get("high") is not None), default=None)
    low_52w = min((row["low"] for row in window if row.get("low") is not None), default=None)

    ret_30d = None
    if len(closes) >= 31 and closes[-31]:
        ret_30d = (closes[-1] / closes[-31] - 1.0) * 100.0
    if ret_30d is not None and abs(ret_30d) > RETURN_LIMIT:
        ret_30d = None

    ret_ytd = None
    current_year = datetime.now(SITE_TIMEZONE).year
    prior = [row for row in series if row["date"] < f"{current_year}-01-01"]
    if prior and prior[-1].get("close"):
        ret_ytd = (closes[-1] / prior[-1]["close"] - 1.0) * 100.0

    recent = series[-30:]
    as_of = recent[-1]["date"] if recent else fetched_at.date().isoformat()

    return {
        "status": "ok",
        "price": price,
        "prev_close": prev_close,
        "change_pct": round(change, 2) if change is not None else None,
        "volume": _number(quote, "f47"),
        "market_cap": _number(quote, "f116"),
        "pe": _number(quote, "f164"),
        "pb": _number(quote, "f167"),
        "roe": _number(quote, "f173"),
        "turnover": _number(quote, "f168"),
        "high_52w": high_52w,
        "low_52w": low_52w,
        "ret_30d": round(ret_30d, 2) if ret_30d is not None else None,
        "ret_ytd": round(ret_ytd, 2) if ret_ytd is not None else None,
        "currency": company.currency,
        "as_of": as_of,
        "source": "Eastmoney",
        "split_events": [{"date": item["date"], "factor": item["factor"]} for item in splits],
        "history_adjusted": bool(splits),
        "quote_as_of": fetched_at.date().isoformat(),
        "history": {
            "dates": [row["date"] for row in recent],
            "open": [row["open"] for row in recent],
            "high": [row["high"] for row in recent],
            "low": [row["low"] for row in recent],
            "close": [row["close"] for row in recent],
            "volume": [row["volume"] for row in recent],
        },
        "closes": closes[-60:],
    }


def merge_quote(previous: dict[str, Any], quote: dict[str, Any], company: Company, fetched_at: datetime) -> dict[str, Any]:
    """Apply a fresh quote to a previous entry, keeping its daily history.

    Used for intraday refreshes: price, one-day change, market cap and the
    fundamentals carried by the quote move; returns, 52-week range and the
    stored history stay on the last completed daily bar.
    """
    price = _number(quote, "f43")
    prev_close = _number(quote, "f60")
    change = _number(quote, "f170")
    if change is None and price is not None and prev_close:
        change = (price - prev_close) / prev_close * 100.0
    entry = dict(previous)
    entry.update(
        {
            "status": "ok",
            "price": price,
            "prev_close": prev_close,
            "change_pct": round(change, 2) if change is not None else None,
            "volume": _number(quote, "f47"),
            "market_cap": _number(quote, "f116"),
            "pe": _number(quote, "f164"),
            "pb": _number(quote, "f167"),
            "roe": _number(quote, "f173"),
            "turnover": _number(quote, "f168"),
            "currency": company.currency,
            "quote_as_of": fetched_at.date().isoformat(),
        }
    )
    return entry
