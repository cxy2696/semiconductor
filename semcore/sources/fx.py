"""FX rates, normalised to USD per unit of local currency.

Primary source: open.er-api.com (daily, no key). Fallback: Eastmoney FX pairs.
If both fail, the previous snapshot's rates are reused and flagged.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import requests

from ..config import SITE_TIMEZONE
from ..utils import to_float

PRIMARY_URL = "https://open.er-api.com/v6/latest/USD"
FALLBACK_PAIRS = {
    "USDCNH": ("CNY", "133.USDCNH"),
    "USDJPY": ("JPY", "119.USDJPY"),
    "USDKRW": ("KRW", "119.USDKRW"),
    "USDEUR": ("EUR", "119.USDEUR"),
    "USDHKD": ("HKD", "119.USDHKD"),
}
STATIC_FALLBACK = {"USD": 1.0, "CNY": 0.14, "TWD": 0.031, "JPY": 0.0064, "KRW": 0.00074, "EUR": 1.09, "HKD": 0.128}
REQUIRED = ("USD", "CNY", "TWD", "JPY", "KRW", "EUR", "HKD")


def _from_er_api() -> dict[str, Any] | None:
    try:
        response = requests.get(PRIMARY_URL, timeout=15, headers={"User-Agent": "SiliconScope/2.0"})
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError):
        return None
    rates = payload.get("rates") if isinstance(payload, dict) else None
    if not isinstance(rates, dict):
        return None
    usd_per_unit: dict[str, float] = {"USD": 1.0}
    for code in REQUIRED[1:]:
        rate = to_float(rates.get(code))  # units of local currency per USD
        if rate and rate > 0:
            usd_per_unit[code] = 1.0 / rate
    return {
        "usd_per_unit": usd_per_unit,
        "source": "open.er-api.com",
        "as_of": str(payload.get("time_last_update_utc") or "")[:25],
    }


def _from_eastmoney() -> dict[str, Any] | None:
    usd_per_unit: dict[str, float] = {"USD": 1.0}
    for pair, (code, secid) in FALLBACK_PAIRS.items():
        try:
            response = requests.get(
                "https://push2.eastmoney.com/api/qt/stock/get",
                params={"secid": secid, "fltt": 2, "fields": "f43"},
                timeout=12,
                headers={"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"},
            )
            rate = to_float(((response.json() or {}).get("data") or {}).get("f43"))
            if rate and rate > 0:
                usd_per_unit[code] = 1.0 / rate
        except (requests.RequestException, ValueError):
            continue
    if len(usd_per_unit) >= 5:
        return {
            "usd_per_unit": usd_per_unit,
            "source": "Eastmoney FX",
            "as_of": datetime.now(timezone.utc).date().isoformat(),
        }
    return None


def fetch_fx(previous: dict[str, Any] | None = None) -> dict[str, Any]:
    result = _from_er_api() or _from_eastmoney()
    if result and all(code in result["usd_per_unit"] for code in REQUIRED):
        result["status"] = "ok"
        return result

    usd_per_unit = dict(STATIC_FALLBACK)
    if previous and isinstance(previous.get("usd_per_unit"), dict):
        for code, value in previous["usd_per_unit"].items():
            rate = to_float(value)
            if rate:
                usd_per_unit[code] = rate
    return {
        "usd_per_unit": usd_per_unit,
        "source": (previous or {}).get("source", "fallback constants"),
        "as_of": (previous or {}).get("as_of", datetime.now(timezone.utc).date().isoformat()),
        "status": "stale" if previous else "fallback",
        "note": "Primary and fallback FX providers failed; previous or static rates in use.",
        "fetched_at": datetime.now(SITE_TIMEZONE).isoformat(timespec="seconds"),
    }
