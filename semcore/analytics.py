"""Analytics: peer-normalised factors, research priority, risk flags, market state.

All formulas are documented in ``documentation/METHODOLOGY.md`` and mirrored on
the site's method page. Nothing here is a recommendation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Iterable

from .config import SITE_TIMEZONE
from .taxonomy import Taxonomy
from .universe import Company
from .utils import clamp, median, percentile_rank, quantile, to_float

FACTOR_WEIGHTS = {"quality": 0.30, "valuation": 0.25, "momentum": 0.25, "size": 0.20}
COVERAGE_FIELDS = ("price", "change_1d", "ret_30d", "market_cap_usd", "pe", "pb", "roe", "range")
STALE_HOURS = 48


@dataclass
class Row:
    company: Company
    entry: dict[str, Any]
    price: float | None
    change_1d: float | None
    ret_30d: float | None
    ret_ytd: float | None
    market_cap_usd: float | None
    market_cap_local: float | None
    pe: float | None
    pb: float | None
    roe: float | None
    turnover: float | None
    high_52w: float | None
    low_52w: float | None
    range_pos: float | None
    coverage: float
    coverage_level: str
    quality: float | None = None
    valuation: float | None = None
    momentum: float | None = None
    size: float | None = None
    priority: int | None = None
    factor_coverage: float = 0.0
    flags: list[str] = field(default_factory=list)
    risk_level: str = "low"
    stale: bool = False
    closes: list[float] = field(default_factory=list)

    @property
    def priced(self) -> bool:
        return self.price is not None

    @property
    def score_parts(self) -> list[tuple[str, float | None, float]]:
        return [
            ("quality", self.quality, FACTOR_WEIGHTS["quality"]),
            ("valuation", self.valuation, FACTOR_WEIGHTS["valuation"]),
            ("momentum", self.momentum, FACTOR_WEIGHTS["momentum"]),
            ("size", self.size, FACTOR_WEIGHTS["size"]),
        ]


@dataclass
class StageStat:
    stage_id: str
    count: int
    priced: int
    market_cap_usd: float
    median_ret_30d: float | None
    median_pe: float | None
    median_roe: float | None
    breadth: float | None
    top_company: str | None


class Analytics:
    def __init__(self, rows: list[Row], snapshot: dict[str, Any], taxonomy: Taxonomy):
        self.rows = rows
        self.snapshot = snapshot
        self.taxonomy = taxonomy
        self.by_id = {row.company.id: row for row in rows}
        self.generated_at = str(snapshot.get("generated_at") or "")
        self.as_of = max((str(row.entry.get("as_of") or "") for row in rows), default="")
        self.coverage_ratio = (sum(1 for row in rows if row.priced) / len(rows)) if rows else 0.0
        self.total_market_cap_usd = sum(row.market_cap_usd or 0.0 for row in rows)
        self.stale = self._is_stale()
        self.stage_stats = self._stage_stats()
        self.country_stats = self._group_stats("country")
        self.market_stats = self._group_stats("market")
        self.regime = self._regime()
        self.watchlists = self._watchlists()

    # ---- construction -------------------------------------------------
    @classmethod
    def build(
        cls,
        companies: Iterable[Company],
        snapshot: dict[str, Any],
        taxonomy: Taxonomy,
    ) -> "Analytics":
        fx = ((snapshot.get("fx") or {}).get("usd_per_unit") or {})
        quotes = snapshot.get("quotes") or {}
        rows: list[Row] = []

        for company in companies:
            entry = quotes.get(company.id) or {}
            price = to_float(entry.get("price"))
            local_cap = to_float(entry.get("market_cap"))
            rate = to_float(fx.get(company.currency)) or (1.0 if company.currency == "USD" else None)
            mcap_usd = local_cap * rate if local_cap is not None and rate else None
            high_52w = to_float(entry.get("high_52w"))
            low_52w = to_float(entry.get("low_52w"))
            range_pos = None
            if price is not None and high_52w is not None and low_52w is not None and high_52w > low_52w:
                range_pos = clamp((price - low_52w) / (high_52w - low_52w), 0.0, 1.0)

            pe = to_float(entry.get("pe"))
            row = Row(
                company=company,
                entry=entry,
                price=price,
                change_1d=to_float(entry.get("change_pct")),
                ret_30d=to_float(entry.get("ret_30d")),
                ret_ytd=to_float(entry.get("ret_ytd")),
                market_cap_usd=mcap_usd,
                market_cap_local=local_cap,
                pe=pe,
                pb=to_float(entry.get("pb")),
                roe=to_float(entry.get("roe")),
                turnover=to_float(entry.get("turnover")),
                high_52w=high_52w,
                low_52w=low_52w,
                range_pos=range_pos,
                coverage=0.0,
                coverage_level="low",
                stale=entry.get("status") == "stale",
                closes=[value for value in (to_float(v) for v in (entry.get("closes") or [])) if value is not None][-30:],
            )
            present = [
                row.price,
                row.change_1d,
                row.ret_30d,
                row.market_cap_usd,
                row.pe,
                row.pb,
                row.roe,
                row.range_pos,
            ]
            row.coverage = round(sum(1 for value in present if value is not None) / 8.0, 4)
            row.coverage_level = (
                "high" if row.coverage >= 0.875 else "medium" if row.coverage >= 0.625 else "low"
            )
            rows.append(row)

        analytics = cls(rows, snapshot, taxonomy)
        analytics._compute_factors()
        return analytics

    # ---- factors ------------------------------------------------------
    def _compute_factors(self) -> None:
        groups: dict[str, list[Row]] = {}
        for row in self.rows:
            groups.setdefault(row.company.stage, []).append(row)

        for _stage, group in groups.items():
            peer = group if len(group) >= 8 else self.rows
            roe_values = [row.roe for row in peer]
            pe_values = [row.pe for row in peer if row.pe is not None and row.pe > 0]
            ret_values = [row.ret_30d for row in peer]
            range_values = [row.range_pos for row in peer]
            cap_values = [math.log10(row.market_cap_usd) for row in peer if row.market_cap_usd and row.market_cap_usd > 0]

            for row in group:
                row.quality = percentile_rank(roe_values, row.roe)

                if row.pe is not None and row.pe > 0:
                    row.valuation = percentile_rank([-value for value in pe_values], -row.pe)
                else:
                    row.valuation = None

                momentum_parts: list[tuple[float, float]] = []
                if row.ret_30d is not None:
                    pct = percentile_rank(ret_values, row.ret_30d)
                    if pct is not None:
                        momentum_parts.append((pct, 0.6))
                if row.range_pos is not None:
                    pct = percentile_rank(range_values, row.range_pos)
                    if pct is not None:
                        momentum_parts.append((pct, 0.4))
                if momentum_parts:
                    total_weight = sum(weight for _, weight in momentum_parts)
                    row.momentum = round(sum(value * weight for value, weight in momentum_parts) / total_weight, 4)

                if row.market_cap_usd and row.market_cap_usd > 0:
                    row.size = percentile_rank(cap_values, math.log10(row.market_cap_usd))

                available = [(value, weight) for _, value, weight in row.score_parts if value is not None]
                if available:
                    total_weight = sum(weight for _, weight in available)
                    row.priority = int(round(clamp(sum(value * weight for value, weight in available) / total_weight, 0, 100)))
                    row.factor_coverage = round(total_weight / sum(FACTOR_WEIGHTS.values()), 3)
                self._apply_flags(row)

    @staticmethod
    def _apply_flags(row: Row) -> None:
        flags: list[str] = []
        if row.pe is not None and row.pe <= 0:
            flags.append("loss")
        if row.valuation is not None and row.valuation >= 80:
            flags.append("rich")
        if row.market_cap_usd is not None and row.market_cap_usd < 2_000_000_000:
            flags.append("small")
        if row.ret_30d is not None and abs(row.ret_30d) >= 25:
            flags.append("sharp")
        if row.stale:
            flags.append("stale")
        row.flags = flags
        significant = [flag for flag in flags if flag != "stale"]
        row.risk_level = "high" if len(significant) >= 3 else "medium" if significant else "low"

    # ---- aggregates ---------------------------------------------------
    def _stage_stats(self) -> dict[str, StageStat]:
        stats: dict[str, StageStat] = {}
        for stage in self.taxonomy.stages:
            rows = [row for row in self.rows if row.company.stage == stage.id]
            priced = [row for row in rows if row.priced]
            top = max(rows, key=lambda row: row.market_cap_usd or 0, default=None)
            stats[stage.id] = StageStat(
                stage_id=stage.id,
                count=len(rows),
                priced=len(priced),
                market_cap_usd=sum(row.market_cap_usd or 0.0 for row in rows),
                median_ret_30d=median([row.ret_30d for row in rows]),
                median_pe=median([row.pe for row in rows if row.pe is not None and row.pe > 0]),
                median_roe=median([row.roe for row in rows]),
                breadth=(
                    sum(1 for row in rows if (row.ret_30d or 0) > 0) / len([row for row in rows if row.ret_30d is not None])
                    if any(row.ret_30d is not None for row in rows)
                    else None
                ),
                top_company=top.company.id if top else None,
            )
        return stats

    def _group_stats(self, attr: str) -> dict[str, dict[str, Any]]:
        groups: dict[str, list[Row]] = {}
        for row in self.rows:
            key = getattr(row.company, attr)
            groups.setdefault(key, []).append(row)
        out: dict[str, dict[str, Any]] = {}
        for key, rows in groups.items():
            out[key] = {
                "count": len(rows),
                "market_cap_usd": sum(row.market_cap_usd or 0.0 for row in rows),
                "median_ret_30d": median([row.ret_30d for row in rows]),
                "priced": sum(1 for row in rows if row.priced),
            }
        return out

    def _regime(self) -> dict[str, Any]:
        rets = [row.ret_30d for row in self.rows if row.ret_30d is not None]
        breadth = (sum(1 for value in rets if value > 0) / len(rets)) if rets else None
        middle = median(rets)
        dispersion = None
        if rets:
            p75, p25 = quantile(rets, 0.75), quantile(rets, 0.25)
            if p75 is not None and p25 is not None:
                dispersion = p75 - p25

        label = "neutral"
        if breadth is not None and middle is not None:
            if breadth >= 0.6 and middle > 2:
                label = "expansion"
            elif breadth <= 0.4 and middle < -2:
                label = "contraction"

        stage_returns = {
            stage_id: stat.median_ret_30d
            for stage_id, stat in self.stage_stats.items()
            if stat.count >= 3 and stat.median_ret_30d is not None
        }
        leader = max(stage_returns, key=stage_returns.get) if stage_returns else None
        laggard = min(stage_returns, key=stage_returns.get) if stage_returns else None

        return {
            "label": label,
            "breadth": round(breadth, 4) if breadth is not None else None,
            "median": round(middle, 2) if middle is not None else None,
            "dispersion": round(dispersion, 2) if dispersion is not None else None,
            "leader": leader,
            "laggard": laggard,
            "sample": len(rets),
        }

    # ---- lists --------------------------------------------------------
    def _watchlists(self) -> dict[str, list[Row]]:
        priced = [row for row in self.rows if row.priced]

        quality = [
            row for row in priced if (row.quality or 0) >= 70 and (row.valuation or 0) >= 50
        ]
        quality.sort(key=lambda row: (row.priority or 0), reverse=True)

        value = [row for row in priced if (row.valuation or 0) >= 70 and (row.quality or 0) >= 50]
        value.sort(key=lambda row: (row.valuation or 0), reverse=True)

        momentum = [row for row in priced if (row.momentum or 0) >= 80 and (row.ret_30d or 0) > 0]
        momentum.sort(key=lambda row: (row.momentum or 0), reverse=True)

        return {
            "quality": quality[:8],
            "value": value[:8],
            "momentum": momentum[:8],
        }

    def movers(self, limit: int = 5) -> dict[str, list[Row]]:
        priced = [row for row in self.rows if row.ret_30d is not None]
        ordered = sorted(priced, key=lambda row: row.ret_30d or 0, reverse=True)
        return {"gainers": ordered[:limit], "losers": list(reversed(ordered[-limit:]))}

    def rows_for_stage(self, stage_id: str) -> list[Row]:
        rows = [row for row in self.rows if row.company.stage == stage_id]
        return sorted(rows, key=lambda row: row.market_cap_usd or 0, reverse=True)

    def peers(self, row: Row, limit: int = 6) -> list[Row]:
        peers = [other for other in self.rows_for_stage(row.company.stage) if other.company.id != row.company.id]
        return peers[:limit]

    # ---- metadata -----------------------------------------------------
    def _is_stale(self) -> bool:
        try:
            generated = datetime.fromisoformat(self.generated_at)
        except ValueError:
            return True
        if generated.tzinfo is None:
            generated = generated.replace(tzinfo=SITE_TIMEZONE)
        return datetime.now(SITE_TIMEZONE) - generated > timedelta(hours=STALE_HOURS)
