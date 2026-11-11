"""Data-health summary shared by the status page, the CLI and CI."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .config import SITE_TIMEZONE
from .content import KnowledgeDoc


@dataclass
class Health:
    generated_at: str
    as_of: str
    age_hours: float | None
    coverage: float
    priced: int
    total: int
    label: str
    errors: list[str] = field(default_factory=list)
    unpriced: list[str] = field(default_factory=list)
    news_count: int = 0
    news_sources: list[str] = field(default_factory=list)
    stale_topics: list[dict[str, str]] = field(default_factory=list)
    dataset: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "as_of": self.as_of,
            "age_hours": self.age_hours,
            "coverage": self.coverage,
            "priced": self.priced,
            "total": self.total,
            "label": self.label,
            "errors": self.errors,
            "unpriced": self.unpriced,
            "news_count": self.news_count,
            "news_sources": self.news_sources,
            "stale_topics": self.stale_topics,
            "dataset": self.dataset,
        }


def build_health(snapshot: dict[str, Any], analytics: Any, knowledge: list[KnowledgeDoc], now: datetime | None = None) -> Health:
    now = now or datetime.now(SITE_TIMEZONE)
    generated_at = str(snapshot.get("generated_at") or "")
    try:
        generated = datetime.fromisoformat(generated_at)
        if generated.tzinfo is None:
            generated = generated.replace(tzinfo=SITE_TIMEZONE)
        age_hours = round((now - generated).total_seconds() / 3600, 1)
    except ValueError:
        age_hours = None

    coverage = float(analytics.coverage_ratio)
    if age_hours is None or age_hours > 72 or coverage < 0.75:
        label = "stale"
    elif age_hours > 36 or coverage < 0.9:
        label = "aging"
    else:
        label = "healthy"

    unpriced = [row.company.id for row in analytics.rows if not row.priced]
    news = snapshot.get("news") or []
    sources = sorted({str(item.get("source")) for item in news if item.get("source")})

    stale_topics: list[dict[str, str]] = []
    for doc in knowledge:
        if not doc.updated:
            continue
        try:
            updated = datetime.strptime(doc.updated, "%Y-%m-%d").date()
        except ValueError:
            continue
        if (now.date() - updated).days > 365:
            stale_topics.append({"slug": doc.slug, "title": doc.title, "updated": doc.updated})

    return Health(
        generated_at=generated_at,
        as_of=str(analytics.as_of),
        age_hours=age_hours,
        coverage=coverage,
        priced=sum(1 for row in analytics.rows if row.priced),
        total=len(analytics.rows),
        label=label,
        errors=[str(error) for error in (snapshot.get("errors") or [])],
        unpriced=unpriced,
        news_count=len(news),
        news_sources=sources,
        stale_topics=stale_topics,
        dataset=str(snapshot.get("dataset") or "unknown"),
    )


def to_markdown(health: Health) -> str:
    coverage = f"{health.coverage * 100:.1f}%"
    age = "—" if health.age_hours is None else f"{health.age_hours:.1f} h"
    lines = [
        "## SiliconScope data health",
        "",
        f"- Status: **{health.label}**",
        f"- Snapshot: `{health.generated_at}` (as of {health.as_of})",
        f"- Data age: {age}",
        f"- Coverage: {coverage} ({health.priced}/{health.total})",
        f"- Headlines: {health.news_count} from {len(health.news_sources)} sources",
    ]
    if health.unpriced:
        lines.append(f"- Unpriced: {', '.join(health.unpriced)}")
    if health.errors:
        lines.append(f"- Notes: {'; '.join(health.errors)}")
    if health.stale_topics:
        lines.append(f"- Content older than 12 months: {', '.join(item['slug'] for item in health.stale_topics)}")
    return "\n".join(lines) + "\n"
