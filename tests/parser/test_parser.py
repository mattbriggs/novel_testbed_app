"""
Integration tests for the CommonMark novel parser.

These tests verify chapter detection, module splitting, type inference,
and text capture across a realistic Markdown structure.
"""

from novel_testbed.parser.commonmark import CommonMarkNovelParser
from novel_testbed.models import ModuleType


def test_commonmark_parser_splits_chapters_and_modules():
    md = """# Chapter One

## Scene 1
Hello world.

## Exposition 1
Some background.

# Chapter Two

## Scene 2
More text.
"""

    parser = CommonMarkNovelParser()
    novel = parser.parse(md, title="Test")

    # Basic structure
    assert novel.title == "Test"
    assert len(novel.modules) == 3

    # Module 1
    m1 = novel.modules[0]
    assert m1.id == "M001"
    assert m1.chapter == "Chapter One"
    assert m1.title == "Scene 1"
    assert m1.module_type == ModuleType.SCENE
    assert "Hello world." in m1.text
    assert m1.start_text.startswith("Hello world")
    assert m1.end_text.endswith("world.")

    # Module 2
    m2 = novel.modules[1]
    assert m2.id == "M002"
    assert m2.chapter == "Chapter One"
    assert m2.title == "Exposition 1"
    assert m2.module_type == ModuleType.EXPOSITION
    assert "Some background." in m2.text

    # Module 3
    m3 = novel.modules[2]
    assert m3.id == "M003"
    assert m3.chapter == "Chapter Two"
    assert m3.title == "Scene 2"
    assert m3.module_type == ModuleType.SCENE
    assert "More text." in m3.text