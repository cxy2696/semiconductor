from __future__ import annotations

from semcore.analytics import FACTOR_WEIGHTS, Analytics


def test_priority_within_bounds(companies, snapshot, taxonomy):
    analytics = Analytics.build(companies, snapshot, taxonomy)
    for row in analytics.rows:
        if row.priority is not None:
            assert 0 <= row.priority <= 100
        for value in (row.quality, row.valuation, row.momentum, row.size):
            if value is not None:
                assert 0 <= value <= 100


def test_missing_valuation_is_renormalised(companies, snapshot, taxonomy):
    analytics = Analytics.build(companies, snapshot, taxonomy)
    row = next(row for row in analytics.rows if row.priority is not None and row.valuation is None)
    assert row.factor_coverage < 1.0
    assert row.priority is not None


def test_factor_weights_sum_to_one():
    assert abs(sum(FACTOR_WEIGHTS.values()) - 1.0) < 1e-9


def test_regime_matches_thresholds(companies, snapshot, taxonomy):
    analytics = Analytics.build(companies, snapshot, taxonomy)
    regime = analytics.regime
    assert regime["label"] in {"expansion", "neutral", "contraction"}
    assert 0 <= regime["breadth"] <= 1
    if regime["label"] == "expansion":
        assert regime["breadth"] >= 0.6 and regime["median"] > 2
    if regime["label"] == "contraction":
        assert regime["breadth"] <= 0.4 and regime["median"] < -2


def test_watchlists_follow_published_rules(companies, snapshot, taxonomy):
    analytics = Analytics.build(companies, snapshot, taxonomy)
    for row in analytics.watchlists["quality"]:
        assert row.quality >= 70 and row.valuation >= 50
    for row in analytics.watchlists["value"]:
        assert row.valuation >= 70 and row.quality >= 50
    for row in analytics.watchlists["momentum"]:
        assert row.momentum >= 80 and row.ret_30d > 0


def test_stage_stats_account_for_all_companies(companies, snapshot, taxonomy):
    analytics = Analytics.build(companies, snapshot, taxonomy)
    total = sum(stat.count for stat in analytics.stage_stats.values())
    assert total == len(analytics.rows)


def test_coverage_levels(companies, snapshot, taxonomy):
    analytics = Analytics.build(companies, snapshot, taxonomy)
    for row in analytics.rows:
        assert 0 <= row.coverage <= 1
        if row.coverage >= 0.875:
            assert row.coverage_level == "high"
        elif row.coverage >= 0.625:
            assert row.coverage_level == "medium"
        else:
            assert row.coverage_level == "low"
