from __future__ import annotations

from datetime import datetime, timedelta

from semcore.analytics import Analytics
from semcore.status import build_health, to_markdown
from semcore.config import SITE_TIMEZONE
from semcore.content import load_all_knowledge


def test_health_labels(companies, snapshot, taxonomy):
    analytics = Analytics.build(companies, snapshot, taxonomy)
    generated = datetime.fromisoformat(snapshot["generated_at"])
    fresh = build_health(snapshot, analytics, load_all_knowledge()["en"], now=generated + timedelta(hours=1))
    assert fresh.label == "healthy"
    assert fresh.coverage == analytics.coverage_ratio
    stale = build_health(snapshot, analytics, load_all_knowledge()["en"], now=generated + timedelta(days=5))
    assert stale.label == "stale"


def test_markdown_summary(companies, snapshot, taxonomy):
    analytics = Analytics.build(companies, snapshot, taxonomy)
    health = build_health(snapshot, analytics, load_all_knowledge()["en"])
    text = to_markdown(health)
    assert "SiliconScope data health" in text
    assert "Coverage" in text
