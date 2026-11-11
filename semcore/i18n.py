"""Trilingual UI strings."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from .config import I18N_DIR, LOCALES
from .utils import read_json

_MISSING = object()


@lru_cache(maxsize=1)
def load_bundle() -> dict[str, dict[str, Any]]:
    bundle: dict[str, dict[str, Any]] = {}
    for locale in LOCALES:
        payload = read_json(I18N_DIR / f"{locale.lang}.json")
        if not isinstance(payload, dict):
            raise RuntimeError(f"Missing i18n file for {locale.lang}")
        bundle[locale.lang] = payload
    return bundle


def flatten(payload: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in payload.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            out.update(flatten(value, path))
        else:
            out[path] = value
    return out


def lookup(lang: str, path: str, **kwargs: Any) -> str:
    node: Any = load_bundle().get(lang, {})
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            node = _MISSING
            break
        node = node[part]
    if node is _MISSING:
        return path
    text = str(node)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return text
    return text


def bundle_for(lang: str) -> dict[str, Any]:
    return load_bundle().get(lang, {})
