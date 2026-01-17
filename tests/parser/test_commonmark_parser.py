"""
Tests for the CommonMarkNovelParser.

These tests verify that the parser:
- Detects chapters and modules
- Infers module types correctly
- Assigns stable module IDs
- Preserves text content
- Handles malformed or empty structures gracefully
"""

import pytest

from novel_testbed.parser.commonmark import CommonMarkNovelParser
from novel_testbed.models import ModuleType


def test_parses_single_chapter_and_scene():
    text = """
# Chapter One
## Scene Arrival
She stepped onto the sand.
The island was silent.
"""

    parser = CommonMarkNovelParser()
    novel = parser.parse(text, title="Test Novel")

    assert novel.title == "Test Novel"
    assert len(novel.modules) == 1

    module = novel.modules[0]
    assert module.chapter == "Chapter One"
    assert module.title == "Scene Arrival"
    assert module.module_type == ModuleType.SCENE
    assert "stepped onto the sand" in module.text
    assert module.start_text.startswith("She stepped")
    assert module.end_text.endswith("silent.")


def test_parses_multiple_modules_in_one_chapter():
    text = """
# Chapter One
## Scene First
One.

## Exposition History
Two.

## Transition Shift
Three.
"""

    parser = CommonMarkNovelParser()
    novel = parser.parse(text, title="Test Novel")

    assert len(novel.modules) == 3
    assert novel.modules[0].module_type == ModuleType.SCENE
    assert novel.modules[1].module_type == ModuleType.EXPOSITION
    assert novel.modules[2].module_type == ModuleType.TRANSITION


def test_assigns_module_ids_in_sequence():
    text = """
# Chapter One
## Scene One
Text.

## Scene Two
Text.
"""

    parser = CommonMarkNovelParser()
    novel = parser.parse(text, title="Test Novel")

    assert novel.modules[0].id == "M001"
    assert novel.modules[1].id == "M002"


def test_assigns_other_type_for_unknown_module_titles():
    text = """
# Chapter One
## Interlude A Strange Moment
Something happens.
"""

    parser = CommonMarkNovelParser()
    novel = parser.parse(text, title="Test Novel")

    assert len(novel.modules) == 1
    assert novel.modules[0].module_type == ModuleType.OTHER


def test_warns_but_returns_empty_when_no_modules_found():
    text = """
# Chapter One
This is text with no module headings at all.
"""

    parser = CommonMarkNovelParser()
    novel = parser.parse(text, title="Test Novel")

    assert novel.modules == []


def test_handles_multiple_chapters():
    text = """
# Chapter One
## Scene One
Text.

# Chapter Two
## Scene Two
More text.
"""

    parser = CommonMarkNovelParser()
    novel = parser.parse(text, title="Test Novel")

    assert len(novel.modules) == 2
    assert novel.modules[0].chapter == "Chapter One"
    assert novel.modules[1].chapter == "Chapter Two"


def test_module_line_numbers_are_correct():
    text = """
# Chapter One
## Scene One
Line A
Line B

## Scene Two
Line C
"""

    parser = CommonMarkNovelParser()
    novel = parser.parse(text, title="Test Novel")

    m1 = novel.modules[0]
    m2 = novel.modules[1]

    assert m1.start_line < m1.end_line
    assert m2.start_line < m2.end_line
    assert m2.start_line > m1.end_line