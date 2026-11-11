"""Small, dependency-free helpers shared across the build."""

from __future__ import annotations

import json
import math
import posixpath
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, Sequence


def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def write_json(path: Path, payload: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def write_text(path: Path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def now_cn() -> datetime:
    from .config import SITE_TIMEZONE

    return datetime.now(SITE_TIMEZONE)


def slugify(value: str) -> str:
    value = re.sub(r"[^\w\s-]", "", str(value).strip().lower())
    value = re.sub(r"[\s_-]+", "-", value)
    return value.strip("-")


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def to_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def to_int(value: Any) -> int | None:
    number = to_float(value)
    return int(round(number)) if number is not None else None


def median(values: Sequence[float]) -> float | None:
    clean = sorted(v for v in values if v is not None and math.isfinite(v))
    if not clean:
        return None
    mid = len(clean) // 2
    if len(clean) % 2:
        return clean[mid]
    return (clean[mid - 1] + clean[mid]) / 2


def quantile(values: Sequence[float], q: float) -> float | None:
    clean = sorted(v for v in values if v is not None and math.isfinite(v))
    if not clean:
        return None
    if len(clean) == 1:
        return clean[0]
    pos = clamp(q, 0.0, 1.0) * (len(clean) - 1)
    low = math.floor(pos)
    high = math.ceil(pos)
    if low == high:
        return clean[int(pos)]
    return clean[low] + (clean[high] - clean[low]) * (pos - low)


def percentile_rank(values: Iterable[float | None], value: float | None) -> float | None:
    """Percentile rank (0-100) of ``value`` within ``values``; ties get the mid-rank."""
    if value is None:
        return None
    clean = [v for v in values if v is not None and math.isfinite(v)]
    if not clean:
        return None
    below = sum(1 for v in clean if v < value)
    equal = sum(1 for v in clean if v == value)
    if equal == 0:
        return None
    return round(100.0 * (below + 0.5 * equal) / len(clean), 4)


def pct_change(current: float | None, previous: float | None) -> float | None:
    if current is None or previous in (None, 0):
        return None
    return round((current - previous) / previous * 100.0, 2)


def range_position(price: float | None, low: float | None, high: float | None) -> float | None:
    if price is None or low is None or high is None or high <= low:
        return None
    return clamp((price - low) / (high - low), 0.0, 1.0)


def fmt_number(value: Any, digits: int = 2) -> str:
    number = to_float(value)
    if number is None:
        return "—"
    return f"{number:,.{digits}f}"


def fmt_pct(value: Any, digits: int = 2, signed: bool = True) -> str:
    number = to_float(value)
    if number is None:
        return "—"
    sign = "+" if signed and number > 0 else ""
    return f"{sign}{number:.{digits}f}%"


def fmt_price(value: Any, currency: str = "") -> str:
    number = to_float(value)
    if number is None:
        return "—"
    digits = 0 if currency in {"JPY", "KRW", "TWD"} else (3 if currency == "EUR" and number < 100 else 2)
    text = f"{number:,.{digits}f}"
    return f"{text} {currency}".strip()


def fmt_usd_compact(value: Any) -> str:
    number = to_float(value)
    if number is None:
        return "—"
    abs_value = abs(number)
    if abs_value >= 1e12:
        return f"${number / 1e12:,.2f}T"
    if abs_value >= 1e9:
        return f"${number / 1e9:,.1f}B"
    if abs_value >= 1e6:
        return f"${number / 1e6:,.1f}M"
    return f"${number:,.0f}"


def fmt_compact(value: Any) -> str:
    number = to_float(value)
    if number is None:
        return "—"
    abs_value = abs(number)
    if abs_value >= 1e9:
        return f"{number / 1e9:.1f}B"
    if abs_value >= 1e6:
        return f"{number / 1e6:.1f}M"
    if abs_value >= 1e3:
        return f"{number / 1e3:.1f}K"
    return f"{number:,.0f}"


def parse_iso_date(value: Any) -> date | None:
    if not value:
        return None
    text = str(value)
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(text[: len(fmt) + 6], fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def rel_href(target: str, current: str) -> str:
    """Return a POSIX relative href from the file at ``current`` to ``target``."""
    target_dir = posixpath.dirname(target)
    start = posixpath.dirname(current)
    relative = posixpath.relpath(target_dir or ".", start or ".")
    name = posixpath.basename(target)
    if relative == ".":
        return name
    return f"{relative}/{name}"


def unique(seq: Iterable[Any]) -> list[Any]:
    seen: set[Any] = set()
    out = []
    for item in seq:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def truncate(text: str, limit: int) -> str:
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def str_or_empty(value: Any) -> str:
    return "" if value is None else str(value)
