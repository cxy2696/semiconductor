"""Shared test fixtures: a deterministic snapshot for offline builds."""

from __future__ import annotations

import random
from typing import Any

import pytest

from semcore.taxonomy import Taxonomy
from semcore.universe import load_universe

FX = {"USD": 1.0, "CNY": 0.14, "TWD": 0.031, "JPY": 0.0064, "KRW": 0.00074, "EUR": 1.09, "HKD": 0.128}


def make_snapshot(companies, seed: int = 11) -> dict[str, Any]:
    rng = random.Random(seed)
    quotes: dict[str, Any] = {}
    for index, company in enumerate(companies):
        base_cap = 10 ** (9 + (index % 6) * 0.35) * (1 + rng.random())
        price = round(5 + rng.random() * 900, 2)
        change = round(rng.uniform(-6, 6), 2)
        ret_30d = round(rng.uniform(-35, 45), 2)
        high = round(price * (1.1 + rng.random() * 0.4), 2)
        low = round(price * (0.55 + rng.random() * 0.25), 2)
        closes = [price * (1 + rng.uniform(-0.05, 0.05)) for _ in range(30)]
        closes[-1] = price
        quotes[company.id] = {
            "status": "ok",
            "price": price,
            "prev_close": round(price / (1 + change / 100), 2),
            "change_pct": change,
            "volume": rng.randint(10_000, 50_000_000),
            "market_cap": base_cap,
            "pe": round(rng.uniform(-10, 90), 2),
            "pb": round(rng.uniform(0.4, 18), 2),
            "roe": round(rng.uniform(-25, 45), 2),
            "turnover": round(rng.uniform(0.05, 6), 2),
            "high_52w": high,
            "low_52w": low,
            "ret_30d": ret_30d,
            "ret_ytd": round(rng.uniform(-40, 70), 2),
            "currency": company.currency,
            "as_of": "2026-11-10",
            "source": "fixture",
            "closes": closes,
            "history": {
                "dates": [f"2026-10-{day:02d}" for day in range(1, 31)],
                "open": closes,
                "high": [value * 1.01 for value in closes],
                "low": [value * 0.99 for value in closes],
                "close": closes,
                "volume": [1_000_000] * 30,
            },
        }
    return {
        "schema_version": 2,
        "site_version": "2.0.0",
        "generated_at": "2026-11-11T08:00:00+08:00",
        "dataset": "fixture",
        "universe_size": len(companies),
        "coverage": {
            "priced": len(companies),
            "total": len(companies),
            "ratio": 1.0,
        },
        "fx": {"usd_per_unit": FX, "source": "fixture", "as_of": "2026-11-10", "status": "ok"},
        "quotes": quotes,
        "news": [
            {
                "title": "Fixture headline about advanced packaging",
                "link": "https://example.com/a",
                "source": "Fixture Wire",
                "published": "2026-11-10",
                "lang": "en",
                "summary": "Fixture summary",
            }
        ],
        "errors": [],
        "sources": {"quotes": "fixture", "fx": "fixture", "news": "fixture"},
    }


@pytest.fixture(scope="session")
def taxonomy() -> Taxonomy:
    return Taxonomy.load()


@pytest.fixture(scope="session")
def companies(taxonomy):
    return load_universe(taxonomy=taxonomy)


@pytest.fixture(scope="session")
def snapshot(companies):
    return make_snapshot(companies)
