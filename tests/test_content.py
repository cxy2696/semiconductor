from __future__ import annotations

from semcore.content import load_all_knowledge, load_glossary, parse_front_matter, render_markdown


def test_front_matter_parsing():
    meta, body = parse_front_matter("---\ntitle: Test\ntags: a, b\nminutes: 7\n---\n\nHello.")
    assert meta["title"] == "Test"
    assert meta["tags"] == ["a", "b"]
    assert body.strip() == "Hello."


def test_markdown_headings_and_toc():
    html, toc = render_markdown("## First section\n\nText.\n\n### Sub section\n\n- one\n- two")
    assert 'id="first-section"' in html
    assert [item["level"] for item in toc] == [2, 3]
    assert "<ul><li>one</li><li>two</li></ul>" in html


def test_markdown_escapes_html():
    html, _ = render_markdown("<script>alert(1)</script>")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_markdown_rejects_unsafe_links():
    html, _ = render_markdown("[click](javascript:alert(1))")
    assert "<a" not in html


def test_knowledge_parity():
    docs = load_all_knowledge()
    slugs = {lang: [doc.slug for doc in items] for lang, items in docs.items()}
    assert slugs["en"] == slugs["zh"] == slugs["ja"] == slugs["de"]
    assert len(slugs["en"]) >= 12
    for doc in docs["en"]:
        assert doc.title and doc.summary and doc.html
        assert doc.toc, doc.slug


def test_glossary_trilingual():
    glossary = load_glossary()
    assert len(glossary) >= 40
    for term in glossary:
        for lang in ("zh", "en", "ja", "de"):
            assert term[lang]["term"]
            assert len(term[lang]["def"]) > 20
