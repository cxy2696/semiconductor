"""Allowlisted RSS aggregation.

Only headlines, sources, dates and links are retained. Full text is never
copied. Feed failures are non-fatal: the build keeps the previous snapshot's
news and records the error.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import timezone
from email.utils import parsedate_to_datetime
from typing import Any

import requests

from ..config import NEWS_KEYWORDS, NEWS_MAX_ITEMS, RSS_FEEDS
from ..utils import truncate

WORD_PATTERNS = [
    re.compile(
        rf"(?<![a-z0-9]){re.escape(keyword.lower())}(?:s|es)?(?![a-z0-9])"
        if keyword.isascii()
        else re.escape(keyword)
    )
    for keyword in NEWS_KEYWORDS
]

TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")


@dataclass
class NewsItem:
    title: str
    link: str
    source: str
    published: str
    lang: str
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "link": self.link,
            "source": self.source,
            "published": self.published,
            "lang": self.lang,
            "summary": self.summary,
        }


def _clean(text: str) -> str:
    return SPACE_RE.sub(" ", TAG_RE.sub(" ", text or "")).strip()


def _text(node: ET.Element, *names: str) -> str:
    for name in names:
        child = node.find(name)
        if child is not None and (child.text or "").strip():
            return _clean(child.text or "")
    return ""


def _link(node: ET.Element) -> str:
    link = node.find("link")
    if link is not None:
        href = (link.text or "").strip()
        if href:
            return href
        if link.get("href"):
            return link.get("href", "")
    guid = node.find("guid")
    if guid is not None and (guid.text or "").startswith("http"):
        return _clean(guid.text or "")
    return ""


def _published(node: ET.Element) -> str:
    for tag in ("pubDate", "published", "updated", "dc:date"):
        child = node.find(tag)
        if child is None and ":" in tag:
            child = node.find(tag.split(":", 1)[1])
        if child is None or not (child.text or "").strip():
            continue
        raw = child.text.strip()
        try:
            parsed = parsedate_to_datetime(raw)
        except (TypeError, ValueError):
            try:
                from datetime import datetime

                parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            except ValueError:
                continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).date().isoformat()
    return ""


def parse_feed(xml_text: str, source: str, lang: str) -> list[NewsItem]:
    try:
        root = ET.fromstring(xml_text.encode("utf-8"))
    except ET.ParseError:
        return []

    items: list[NewsItem] = []
    nodes = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")
    for node in nodes:
        title = _text(node, "title")
        link = _link(node)
        if not title or not link.startswith(("http://", "https://")):
            continue
        summary = _text(node, "description", "summary", "{http://www.w3.org/2005/Atom}summary")
        items.append(
            NewsItem(
                title=truncate(title, 180),
                link=link,
                source=source,
                published=_published(node),
                lang=lang,
                summary=truncate(summary, 220),
            )
        )
    return items


def _relevant(item: NewsItem) -> bool:
    """Require a semiconductor keyword in the headline.

    Matching uses word boundaries for ASCII keywords so that "Farm" does not
    match "arm" and "Intelligence" does not match "intel". Summary-only matches
    produced too much noise, so the rule is deliberately strict.
    """
    title = item.title.lower()
    return any(pattern.search(title) for pattern in WORD_PATTERNS)


def _near_duplicate(a: str, b: str) -> bool:
    tokens_a = set(re.findall(r"[a-z0-9]{3,}", a.lower()))
    tokens_b = set(re.findall(r"[a-z0-9]{3,}", b.lower()))
    if not tokens_a or not tokens_b:
        return False
    overlap = len(tokens_a & tokens_b) / len(tokens_a | tokens_b)
    return overlap >= 0.6


def fetch_feed(feed: dict[str, str]) -> tuple[list[NewsItem], str | None]:
    try:
        response = requests.get(
            feed["url"],
            timeout=15,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
                ),
                "Accept": "application/rss+xml,application/xml,text/xml,*/*",
            },
        )
        response.raise_for_status()
        return parse_feed(response.text, feed["name"], feed["lang"]), None
    except requests.RequestException as exc:
        return [], f"{feed['name']}: {exc.__class__.__name__}"


def fetch_news(feeds: list[dict[str, str]] | None = None, limit: int = NEWS_MAX_ITEMS) -> tuple[list[dict[str, Any]], list[str]]:
    feeds = feeds or RSS_FEEDS
    items: list[NewsItem] = []
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(fetch_feed, feed): feed for feed in feeds}
        for future in as_completed(futures):
            rows, error = future.result()
            items.extend(rows)
            if error:
                errors.append(error)

    seen: set[str] = set()
    selected: list[NewsItem] = []
    per_source_cap = 6
    source_counts: dict[str, int] = {}

    ordered = sorted(items, key=lambda row: row.published or "", reverse=True)
    for item in ordered:
        key = re.sub(r"[^a-z0-9]+", "", item.title.lower())[:80]
        if not key or key in seen:
            continue
        if not _relevant(item):
            continue
        if source_counts.get(item.source, 0) >= per_source_cap:
            continue
        if any(_near_duplicate(item.title, chosen.title) for chosen in selected):
            continue
        seen.add(key)
        source_counts[item.source] = source_counts.get(item.source, 0) + 1
        selected.append(item)
        if len(selected) >= limit:
            break

    return [item.to_dict() for item in selected], errors
