from __future__ import annotations

from semcore.config import LOCALES
from semcore.i18n import flatten, load_bundle, lookup


def test_all_locales_have_same_keys():
    bundles = load_bundle()
    base = set(flatten(bundles["zh"]))
    for locale in LOCALES:
        assert set(flatten(bundles[locale.lang])) == base


def test_lookup_falls_back_to_path():
    assert lookup("en", "nav.home") == "Home"
    assert lookup("en", "missing.key") == "missing.key"
    assert lookup("ja", "knowledge.readingTime", minutes=5).startswith("約")


def test_no_empty_strings():
    for locale in LOCALES:
        for key, value in flatten(load_bundle()[locale.lang]).items():
            assert str(value).strip(), f"{locale.lang}:{key} is empty"
