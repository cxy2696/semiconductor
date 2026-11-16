"""Quote adapter rules: split adjustment and the return sanity gate."""

from __future__ import annotations

from datetime import datetime

from semcore.config import SITE_TIMEZONE
from semcore.sources.eastmoney import build_market_entry, detect_split_events


class StubCompany:
    id = "stub"
    currency = "JPY"
    ticker = "0000"
    market = "JP"


def make_history(closes: list[float], start_day: int = 1) -> list[dict[str, float | str]]:
    history = []
    for index, close in enumerate(closes):
        day = f"2026-05-{start_day + index:02d}"
        history.append(
            {
                "date": day,
                "open": close,
                "close": close,
                "high": close * 1.01,
                "low": close * 0.99,
                "volume": 1000.0,
            }
        )
    return history


def test_split_is_detected_at_the_right_bar():
    # 40 sessions at ~100, then a 5:1 split down to ~20.
    closes = [100.0] * 40 + [20.0] * 40
    events = detect_split_events(make_history(closes))
    assert len(events) == 1
    assert events[0]["factor"] == 5
    assert events[0]["index"] == 40


def test_ordinary_drop_is_not_a_split():
    closes = [100.0] * 30 + [70.0] + [71.0] * 10  # -30% day, no round factor
    assert detect_split_events(make_history(closes)) == []


def test_return_is_computed_on_a_continuous_series():
    # 31 sessions at 100 before the split, then 5:1, then a flat 20.
    closes = [100.0] * 31 + [20.0] * 31
    history = make_history(closes)
    entry = build_market_entry(
        StubCompany(),
        {"f43": 20.0, "f60": 20.0, "f170": 0.0},
        history,
        datetime(2026, 11, 16, tzinfo=SITE_TIMEZONE),
    )
    assert entry["ret_30d"] == 0.0
    assert entry["history_adjusted"] is True
    assert entry["split_events"][0]["factor"] == 5
    # The 52-week range must be expressed in post-split prices.
    assert entry["high_52w"] < 30


def test_unadjusted_series_keeps_its_return():
    closes = [100.0 + index for index in range(60)]
    entry = build_market_entry(
        StubCompany(),
        {"f43": 159.0, "f60": 158.0, "f170": 0.63},
        make_history(closes),
        datetime(2026, 11, 16, tzinfo=SITE_TIMEZONE),
    )
    assert entry["history_adjusted"] is False
    assert entry["ret_30d"] is not None
    assert 20 < entry["ret_30d"] < 32


def test_implausible_return_is_dropped():
    closes = [100.0] * 31 + [500.0] * 30  # +400% in 30 sessions
    entry = build_market_entry(
        StubCompany(),
        {"f43": 500.0, "f60": 500.0, "f170": 0.0},
        make_history(closes),
        datetime(2026, 11, 16, tzinfo=SITE_TIMEZONE),
    )
    assert entry["ret_30d"] is None
