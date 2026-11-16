from __future__ import annotations

from semcore.config import ROOT
from semcore.validate import validate_docs


def test_all_documents_have_four_languages():
    assert validate_docs() == []


def test_english_is_the_root_readme():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "175 listed companies" in text
    assert "Quotes refresh in place" in text


def test_english_documents_do_not_drift():
    """README.md / CHANGELOG.md / CONTRIBUTING.md mirror their _en copies."""
    for name in ("README", "CHANGELOG", "CONTRIBUTING"):
        root = (ROOT / f"{name}.md").read_bytes()
        copy = (ROOT / f"{name}_en.md").read_bytes()
        assert root == copy, f"{name}.md and {name}_en.md differ"


def test_knowledge_files_use_language_suffixes():
    files = list((ROOT / "content" / "knowledge").glob("*.md"))
    assert len(files) == 48
    for suffix in ("_en.md", "_cn.md", "_jp.md", "_de.md"):
        assert len([path for path in files if path.name.endswith(suffix)]) == 12
