"""Content layer: a small Markdown renderer plus knowledge and glossary loaders.

The renderer intentionally supports a narrow subset (headings, paragraphs,
lists, quotes, fenced code, inline emphasis, links) because all content is
authored in this repository. It escapes HTML before formatting, so raw HTML in
content files is never executed.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .config import CONTENT_DIR, GLOSSARY_FILE, LOCALES
from .utils import read_json, slugify

FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
CODE_RE = re.compile(r"`([^`]+)`")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
ITALIC_RE = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")


@dataclass
class Document:
    title: str
    summary: str
    body: str
    meta: dict[str, Any] = field(default_factory=dict)
    html: str = ""
    toc: list[dict[str, Any]] = field(default_factory=list)


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    text = text.replace("\r\n", "\n")
    meta: dict[str, Any] = {}
    match = FRONT_MATTER.match(text)
    if match:
        for line in match.group(1).splitlines():
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            key, value = line.split(":", 1)
            key, value = key.strip(), value.strip()
            if value.startswith("[") and value.endswith("]"):
                meta[key] = [item.strip() for item in value[1:-1].split(",") if item.strip()]
            elif "," in value and key in {"tags", "related"}:
                meta[key] = [item.strip() for item in value.split(",") if item.strip()]
            else:
                meta[key] = value
        text = text[match.end():]
    return meta, text


def _inline(text: str) -> str:
    escaped = html.escape(text, quote=False)

    def link(match: re.Match[str]) -> str:
        label, href = match.group(1), match.group(2)
        if not re.match(r"^(https?://|/|#|\.\.?/)", href):
            return match.group(0)
        return f'<a href="{href}" rel="noopener">{label}</a>'

    escaped = LINK_RE.sub(link, escaped)
    escaped = CODE_RE.sub(lambda m: f"<code>{m.group(1)}</code>", escaped)
    escaped = BOLD_RE.sub(lambda m: f"<strong>{m.group(1)}</strong>", escaped)
    escaped = ITALIC_RE.sub(lambda m: f"<em>{m.group(1)}</em>", escaped)
    return escaped


def render_markdown(text: str) -> tuple[str, list[dict[str, Any]]]:
    lines = text.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    toc: list[dict[str, Any]] = []
    paragraph: list[str] = []
    used_ids: set[str] = set()

    def flush_paragraph() -> None:
        if not paragraph:
            return
        joined = " ".join(part.strip() for part in paragraph).strip()
        if joined:
            out.append(f"<p>{_inline(joined)}</p>")
        paragraph.clear()

    def heading(level: int, raw: str) -> None:
        flush_paragraph()
        text_value = raw.strip()
        base = slugify(text_value) or f"section-{len(toc) + 1}"
        anchor = base
        counter = 2
        while anchor in used_ids:
            anchor = f"{base}-{counter}"
            counter += 1
        used_ids.add(anchor)
        toc.append({"level": level, "id": anchor, "text": text_value})
        out.append(f'<h{level} id="{anchor}">{_inline(text_value)}</h{level}>')

    index = 0
    total = len(lines)
    while index < total:
        line = lines[index]
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            index += 1
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            index += 1
            code_lines: list[str] = []
            while index < total and not lines[index].strip().startswith("```"):
                code_lines.append(lines[index])
                index += 1
            index += 1  # closing fence
            out.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
            continue

        if stripped.startswith("### "):
            heading(3, stripped[4:])
            index += 1
            continue
        if stripped.startswith("## "):
            heading(2, stripped[3:])
            index += 1
            continue

        if stripped in {"---", "***"}:
            flush_paragraph()
            out.append("<hr>")
            index += 1
            continue

        if stripped.startswith("> "):
            flush_paragraph()
            quote_lines = []
            while index < total and lines[index].strip().startswith(">"):
                quote_lines.append(lines[index].strip()[1:].strip())
                index += 1
            out.append(f"<blockquote>{_inline(' '.join(quote_lines))}</blockquote>")
            continue

        ordered = re.match(r"^\d+\.\s+(.*)$", stripped)
        if stripped.startswith(("- ", "* ")) or ordered:
            flush_paragraph()
            tag = "ol" if ordered else "ul"
            items: list[str] = []
            while index < total:
                candidate = lines[index].strip()
                item_match = re.match(r"^\d+\.\s+(.*)$", candidate) if ordered else (
                    re.match(r"^[-*]\s+(.*)$", candidate) if candidate.startswith(("- ", "* ")) else None
                )
                if not item_match:
                    break
                items.append(f"<li>{_inline(item_match.group(1))}</li>")
                index += 1
            out.append(f"<{tag}>{''.join(items)}</{tag}>")
            continue

        paragraph.append(stripped)
        index += 1

    flush_paragraph()
    return "\n".join(out), toc


@dataclass
class KnowledgeDoc:
    slug: str
    lang: str
    title: str
    summary: str
    level: str
    minutes: int
    order: int
    tags: list[str]
    related: list[str]
    updated: str
    html: str
    toc: list[dict[str, Any]]


def knowledge_dir(lang: str) -> Path:
    return CONTENT_DIR / "knowledge" / lang


def load_knowledge(lang: str) -> list[KnowledgeDoc]:
    directory = knowledge_dir(lang)
    docs: list[KnowledgeDoc] = []
    if not directory.exists():
        return docs
    for path in sorted(directory.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        rendered, toc = render_markdown(body)
        docs.append(
            KnowledgeDoc(
                slug=path.stem,
                lang=lang,
                title=str(meta.get("title") or path.stem),
                summary=str(meta.get("summary") or ""),
                level=str(meta.get("level") or "core"),
                minutes=int(meta.get("minutes") or 5),
                order=int(meta.get("order") or 99),
                tags=list(meta.get("tags") or []),
                related=list(meta.get("related") or []),
                updated=str(meta.get("updated") or ""),
                html=rendered,
                toc=toc,
            )
        )
    docs.sort(key=lambda doc: (doc.order, doc.slug))
    return docs


def load_all_knowledge() -> dict[str, list[KnowledgeDoc]]:
    return {locale.lang: load_knowledge(locale.lang) for locale in LOCALES}


def load_glossary() -> list[dict[str, Any]]:
    payload = read_json(GLOSSARY_FILE)
    if not isinstance(payload, list) or not payload:
        raise RuntimeError(f"Glossary is missing or invalid: {GLOSSARY_FILE}")
    return payload


def glossary_categories(glossary: list[dict[str, Any]]) -> list[str]:
    seen: list[str] = []
    for term in glossary:
        category = str(term.get("category") or "process")
        if category not in seen:
            seen.append(category)
    return seen
