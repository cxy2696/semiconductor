from __future__ import annotations

from semcore.config import ROOT
from semcore.validate import validate_docs


def test_all_documents_have_four_languages():
    assert validate_docs() == []


def test_english_is_the_root_readme():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "A four-language research desk" in text
    assert "175" in text


def test_knowledge_files_use_language_suffixes():
    files = list((ROOT / "content" / "knowledge").glob("*.md"))
    assert len(files) == 48
    for suffix in ("_en.md", "_cn.md", "_jp.md", "_de.md"):
        assert len([path for path in files if path.name.endswith(suffix)]) == 12
