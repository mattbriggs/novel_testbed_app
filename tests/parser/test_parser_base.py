"""
Tests for the NovelParser base interface.

These tests ensure that:
- The abstract class cannot be instantiated directly.
- Subclasses must implement parse().
"""

import pytest

from novel_testbed.parser.base import NovelParser
from novel_testbed.models import Novel


class DummyParser(NovelParser):
    """Minimal concrete implementation for testing."""

    def parse(self, text: str, *, title: str) -> Novel:
        """
        Return a minimal valid Novel instance for testing.
        """
        return Novel(title=title, modules=[])


def test_novel_parser_is_abstract():
    """
    NovelParser should not be instantiable directly.
    """
    with pytest.raises(TypeError):
        NovelParser()


def test_concrete_parser_can_be_instantiated():
    """
    A subclass implementing parse() should be instantiable.
    """
    parser = DummyParser()
    assert isinstance(parser, NovelParser)


def test_concrete_parser_returns_novel():
    """
    A concrete parser must return a Novel object.
    """
    parser = DummyParser()
    novel = parser.parse("Once upon a time", title="Test Novel")

    assert novel.title == "Test Novel"
    assert isinstance(novel.modules, list)