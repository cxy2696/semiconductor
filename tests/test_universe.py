from __future__ import annotations

import csv
from pathlib import Path

import pytest

from semcore.universe import UniverseError, load_universe


def test_universe_is_consistent(taxonomy):
    companies = load_universe(taxonomy=taxonomy)
    assert len(companies) >= 80
    ids = [company.id for company in companies]
    assert len(ids) == len(set(ids))
    for company in companies:
        assert company.stage in taxonomy.stage_by_id
        assert company.role in taxonomy.roles
        assert company.name("zh") and company.name("en") and company.name("ja")
        assert company.currency


def test_duplicate_listing_rejected(tmp_path: Path):
    source = Path("data/universe.csv")
    rows = list(csv.DictReader(source.open(encoding="utf-8")))
    rows[1]["ticker"] = rows[0]["ticker"]
    rows[1]["exchange"] = rows[0]["exchange"]
    target = tmp_path / "universe.csv"
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(UniverseError, match="duplicate listing"):
        load_universe(target)
