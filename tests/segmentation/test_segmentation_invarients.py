"""
Tests for the Markdown segmentation stage.

The segmenter is responsible for turning raw prose into structured,
annotated Markdown that the parser can understand.

These tests verify that:

1. Raw prose becomes segmented Markdown.
2. Already-segmented Markdown is left unchanged.
3. Segmented Markdown can be parsed into modules.
"""

from pathlib import Path

from novel_testbed.segmentation.segmenter import ModuleSegmenter
from novel_testbed.parser.commonmark import CommonMarkNovelParser


# ---------------------------------------------------------------------------
# 1. Basic segmentation
# ---------------------------------------------------------------------------

def test_segmentation_basic():
    """
    Raw prose should be converted into Markdown containing at least one module.

    This is the minimal promise of the segmenter: it creates structure.
    """
    raw = "She stepped onto the sand. The wind was sharp."

    segmenter = ModuleSegmenter()
    result = segmenter.segment_markdown(raw, title="Test Novel")

    # Must create a chapter header
    assert "# Test Novel" in result

    # Must create at least one module
    assert "##" in result
    assert "## Scene" in result or "## Exposition" in result or "## Transition" in result


# ---------------------------------------------------------------------------
# 2. Idempotence
# ---------------------------------------------------------------------------

def test_segmentation_idempotent():
    """
    Already-annotated Markdown must be returned unchanged.

    The segmenter must never damage author-defined structure.
    """
    annotated = """
# Test Novel

## Scene One
She stepped onto the sand.
"""

    segmenter = ModuleSegmenter()
    result = segmenter.segment_markdown(annotated, title="Test Novel")

    # Whitespace normalization is fine, content must remain equivalent
    assert result.strip() == annotated.strip()


# ---------------------------------------------------------------------------
# 3. Round-trip integration: Segment → Parse → Modules
# ---------------------------------------------------------------------------

def test_segmentation_roundtrip():
    """
    Segmented Markdown must be consumable by the parser and produce modules.

    This proves segmentation integrates cleanly with the parsing layer.
    """
    raw = "She stepped onto the sand. The wind cut her face."

    segmenter = ModuleSegmenter()
    annotated = segmenter.segment_markdown(raw, title="Roundtrip Test")

    parser = CommonMarkNovelParser()
    novel = parser.parse(annotated, title="Roundtrip Test")

    assert len(novel.modules) >= 1