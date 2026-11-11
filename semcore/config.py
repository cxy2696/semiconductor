"""SiliconScope configuration: paths, locales and site-wide constants."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CONTENT_DIR = ROOT / "content"
TEMPLATES_DIR = ROOT / "templates"
ASSETS_DIR = ROOT / "assets"
SNAPSHOT_DIR = DATA_DIR / "snapshots"
DOCS_DIR = ROOT / "docs"

TAXONOMY_FILE = DATA_DIR / "taxonomy.json"
UNIVERSE_FILE = DATA_DIR / "universe.csv"
GLOSSARY_FILE = DATA_DIR / "glossary.json"
SYMBOLS_FILE = DATA_DIR / "symbols.json"
I18N_DIR = DATA_DIR / "i18n"

SITE_NAME = "SiliconScope"
SITE_URL = os.environ.get("SITE_URL", "https://cxy2696.github.io/semiconductor").rstrip("/")
REPO_URL = "https://github.com/cxy2696/semiconductor"
SITE_TIMEZONE = ZoneInfo("Asia/Shanghai")
SITE_TZ_LABEL = "UTC+8"

SCHEMA_VERSION = 2
SNAPSHOT_KEEP = 30

# Strategy metadata used by the product logic. Published in documentation/METHODOLOGY.md.
SITE_VERSION = "3.0.0"


@dataclass(frozen=True)
class Locale:
    code: str          # BCP 47, used in <html lang> and data attributes
    lang: str          # short key in taxonomy labels, i18n and snapshots
    slug: str          # URL segment, "" for the default locale
    name: str          # endonym shown in the language switcher
    english_name: str
    date_format: str   # strftime format for display dates
    file_suffix: str   # suffix used by markdown content and documentation


# English is the default locale and lives at the site root. Chinese, Japanese
# and German are mirrored under /zh/, /ja/ and /de/.
LOCALES: tuple[Locale, ...] = (
    Locale("en-US", "en", "", "English", "English", "%Y-%m-%d", "en"),
    Locale("zh-CN", "zh", "zh", "中文", "Chinese", "%Y-%m-%d", "cn"),
    Locale("ja-JP", "ja", "ja", "日本語", "Japanese", "%Y-%m-%d", "jp"),
    Locale("de-DE", "de", "de", "Deutsch", "German", "%Y-%m-%d", "de"),
)

DEFAULT_LOCALE = LOCALES[0]
LOCALE_BY_SUFFIX = {loc.file_suffix: loc for loc in LOCALES}
LOCALE_BY_LANG = {loc.lang: loc for loc in LOCALES}
LOCALE_BY_CODE = {loc.code: loc for loc in LOCALES}

# Pages that exist once per locale. Keys are used by templates and the linker.
PAGES = {
    "home": "index.html",
    "companies": "companies.html",
    "chain": "value-chain.html",
    "knowledge": "knowledge.html",
    "glossary": "glossary.html",
    "guide": "guide.html",
    "method": "methodology.html",
    "about": "about.html",
    "status": "status.html",
}

RSS_FEEDS = [
    {
        "id": "tomshardware",
        "name": "Tom's Hardware",
        "url": "https://www.tomshardware.com/feeds/all",
        "lang": "en",
    },
    {
        "id": "semiconductor-digest",
        "name": "Semiconductor Digest",
        "url": "https://www.semiconductor-digest.com/feed/",
        "lang": "en",
    },
    {
        "id": "eetimes",
        "name": "EE Times",
        "url": "https://www.eetimes.com/feed/",
        "lang": "en",
    },
    {
        "id": "digitimes",
        "name": "DigiTimes",
        "url": "https://www.digitimes.com/rss/daily.xml",
        "lang": "en",
    },
    {
        "id": "semiconductor-today",
        "name": "Semiconductor Today",
        "url": "https://www.semiconductor-today.com/rss/news.xml",
        "lang": "en",
    },
]

NEWS_KEYWORDS = (
    "semiconductor", "chip", "wafer", "foundry", "euv", "lithography", "hbm",
    "dram", "nand", "memory", "packaging", "advanced packaging", "cowos",
    "tsmc", "samsung", "sk hynix", "micron", "intel", "nvidia", "amd",
    "asml", "applied materials", "lam research", "kla", "arm", "qualcomm",
    "broadcom", "infineon", "stmicro", "renesas", "tokyo electron",
    "semiconductor equipment", "fab", "晶圆", "半导体", "存储",
)

NEWS_MAX_ITEMS = 24
