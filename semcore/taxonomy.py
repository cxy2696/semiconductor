"""Taxonomy loader: value-chain stages, roles, products and countries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config import TAXONOMY_FILE
from .utils import read_json


@dataclass(frozen=True)
class Stage:
    id: str
    order: int
    kind: str
    label: dict[str, str]
    short: dict[str, str]
    summary: dict[str, str]
    economics: dict[str, str]
    metrics: dict[str, list[str]]


class Taxonomy:
    def __init__(self, payload: dict[str, Any]):
        self.payload = payload
        self.stages: list[Stage] = []
        for item in sorted(payload.get("stages", []), key=lambda s: s.get("order", 99)):
            self.stages.append(
                Stage(
                    id=item["id"],
                    order=int(item.get("order", 99)),
                    kind=item.get("kind", "flow"),
                    label=item.get("label", {}),
                    short=item.get("short", {}),
                    summary=item.get("summary", {}),
                    economics=item.get("economics", {}),
                    metrics=item.get("metrics", {}),
                )
            )
        self.stage_by_id = {stage.id: stage for stage in self.stages}
        roles_raw = payload.get("roles", {})
        if isinstance(roles_raw, list):
            self.roles: dict[str, dict[str, Any]] = {role["id"]: role for role in roles_raw if "id" in role}
        else:
            self.roles = roles_raw
        self.products: dict[str, dict[str, str]] = payload.get("products", {})
        self.countries: dict[str, dict[str, str]] = payload.get("countries", {})
        self.markets: dict[str, dict[str, str]] = payload.get("markets", {})

    @classmethod
    def load(cls) -> "Taxonomy":
        payload = read_json(TAXONOMY_FILE)
        if not isinstance(payload, dict):
            raise RuntimeError(f"Taxonomy file is missing or invalid: {TAXONOMY_FILE}")
        return cls(payload)

    # ---- labels -------------------------------------------------------
    @staticmethod
    def _pick(mapping: dict[str, Any] | None, lang: str, fallback: str = "") -> str:
        if not mapping:
            return fallback
        return mapping.get(lang) or mapping.get("en") or fallback

    def stage_label(self, stage_id: str, lang: str, short: bool = False) -> str:
        stage = self.stage_by_id.get(stage_id)
        if not stage:
            return stage_id
        return self._pick(stage.short if short else stage.label, lang, stage_id)

    def stage_summary(self, stage_id: str, lang: str) -> str:
        stage = self.stage_by_id.get(stage_id)
        return self._pick(stage.summary, lang) if stage else ""

    def stage_economics(self, stage_id: str, lang: str) -> str:
        stage = self.stage_by_id.get(stage_id)
        return self._pick(stage.economics, lang) if stage else ""

    def stage_metrics(self, stage_id: str, lang: str) -> list[str]:
        stage = self.stage_by_id.get(stage_id)
        return list(self._pick(stage.metrics, lang) or []) if stage else []

    def role_label(self, role_id: str, lang: str) -> str:
        role = self.roles.get(role_id, {})
        return self._pick(role.get("label"), lang, role_id)

    def role_desc(self, role_id: str, lang: str) -> str:
        role = self.roles.get(role_id, {})
        return self._pick(role.get("desc"), lang)

    def product_label(self, product_id: str, lang: str) -> str:
        return self._pick(self.products.get(product_id, {}), lang, product_id)

    def country_label(self, country_id: str, lang: str) -> str:
        return self._pick(self.countries.get(country_id, {}), lang, country_id)

    def market_label(self, market_id: str, lang: str) -> str:
        return self._pick(self.markets.get(market_id, {}), lang, market_id)

    # ---- ordering -----------------------------------------------------
    @property
    def flow_stages(self) -> list[Stage]:
        return [stage for stage in self.stages if stage.kind == "flow"]

    @property
    def support_stages(self) -> list[Stage]:
        return [stage for stage in self.stages if stage.kind == "support"]

    def countries_used(self) -> list[str]:
        return sorted(self.countries)

    def markets_used(self) -> list[str]:
        return sorted(self.markets)
