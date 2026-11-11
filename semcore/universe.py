"""Universe loader and validation.

``data/universe.csv`` is the single source of truth for company coverage.
One row per company; one primary listing per company to avoid double counting.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from .config import UNIVERSE_FILE
from .taxonomy import Taxonomy

REQUIRED_COLUMNS = (
    "id",
    "ticker",
    "exchange",
    "mic",
    "market",
    "country",
    "stage",
    "role",
    "products",
    "hq",
    "website",
    "currency",
    "name_zh",
    "name_en",
    "name_ja",
)

VALID_MARKETS = {"CN", "HK", "TW", "US", "JP", "KR", "EU"}


class UniverseError(ValueError):
    def __init__(self, problems: Iterable[str]):
        self.problems = list(problems)
        super().__init__("Universe validation failed:\n- " + "\n- ".join(self.problems))


@dataclass(frozen=True)
class Company:
    id: str
    ticker: str
    exchange: str
    mic: str
    market: str
    country: str
    stage: str
    role: str
    products: tuple[str, ...]
    hq: str
    website: str
    currency: str
    quote_venue: str
    names: dict[str, str] = field(default_factory=dict)
    notes: dict[str, str] = field(default_factory=dict)

    def name(self, lang: str) -> str:
        return self.names.get(lang) or self.names.get("en") or self.names.get("zh") or self.id

    def note(self, lang: str) -> str:
        return (self.notes.get(lang) or self.notes.get("en") or self.notes.get("zh") or "").strip()

    @property
    def symbol(self) -> str:
        return f"{self.exchange}:{self.ticker}"

    @property
    def is_priced(self) -> bool:
        return self.quote_venue != "unpriced"


def _clean(value: object) -> str:
    return str(value or "").strip()


def load_universe(path: Path | None = None, taxonomy: Taxonomy | None = None) -> list[Company]:
    path = Path(path or UNIVERSE_FILE)
    taxonomy = taxonomy or Taxonomy.load()
    if not path.exists():
        raise UniverseError([f"Universe file not found: {path}"])

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames or []
        missing = [col for col in REQUIRED_COLUMNS if col not in header]
        if missing:
            raise UniverseError([f"Missing columns: {', '.join(missing)}"])
        raw_rows = list(reader)

    problems: list[str] = []
    companies: list[Company] = []
    seen_ids: set[str] = set()
    seen_symbols: set[str] = set()

    for index, row in enumerate(raw_rows, start=2):  # line 2 is the first data row
        row = {key: _clean(value) for key, value in row.items() if key}
        cid = row.get("id", "")
        if not cid:
            problems.append(f"line {index}: empty id")
            continue
        if cid in seen_ids:
            problems.append(f"line {index}: duplicate id '{cid}'")
        seen_ids.add(cid)

        symbol = f"{row.get('exchange', '')}:{row.get('ticker', '')}"
        if symbol in seen_symbols:
            problems.append(f"line {index}: duplicate listing '{symbol}' (one primary listing per company)")
        seen_symbols.add(symbol)

        if row.get("market") not in VALID_MARKETS:
            problems.append(f"{cid}: unknown market '{row.get('market')}'")
        if row.get("stage") not in taxonomy.stage_by_id:
            problems.append(f"{cid}: unknown stage '{row.get('stage')}'")
        if row.get("role") not in taxonomy.roles:
            problems.append(f"{cid}: unknown role '{row.get('role')}'")
        if row.get("country") not in taxonomy.countries:
            problems.append(f"{cid}: unknown country '{row.get('country')}'")

        products = tuple(p for p in row.get("products", "").split("|") if p)
        unknown_products = [p for p in products if p not in taxonomy.products]
        if unknown_products:
            problems.append(f"{cid}: unknown products {unknown_products}")

        website = row.get("website", "")
        if website and not website.startswith(("http://", "https://")):
            problems.append(f"{cid}: website must start with http(s)://")

        if not row.get("name_en") or not row.get("name_zh") or not row.get("name_ja"):
            problems.append(f"{cid}: missing one of name_zh/name_en/name_ja")

        companies.append(
            Company(
                id=cid,
                ticker=row.get("ticker", ""),
                exchange=row.get("exchange", ""),
                mic=row.get("mic", ""),
                market=row.get("market", ""),
                country=row.get("country", ""),
                stage=row.get("stage", ""),
                role=row.get("role", ""),
                products=products,
                hq=row.get("hq", ""),
                website=website,
                currency=row.get("currency", "USD"),
                quote_venue=row.get("quote_venue", ""),
                names={"zh": row.get("name_zh", ""), "en": row.get("name_en", ""), "ja": row.get("name_ja", "")},
                notes={"zh": row.get("note_zh", ""), "en": row.get("note_en", ""), "ja": row.get("note_ja", "")},
            )
        )

    if problems:
        raise UniverseError(problems)
    if not companies:
        raise UniverseError(["Universe is empty"])
    return companies


def companies_by_stage(companies: Iterable[Company]) -> dict[str, list[Company]]:
    grouped: dict[str, list[Company]] = {}
    for company in companies:
        grouped.setdefault(company.stage, []).append(company)
    return grouped
