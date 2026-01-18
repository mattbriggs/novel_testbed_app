"""
Tests for the Markdown segmentation stage.

The segmenter is responsible for turning raw prose into structured,
annotated Markdown that the parser can understand.

These tests verify that:

1. Raw prose becomes segmented Markdown.
2. Already-valid Markdown is preserved (with normalization allowed).
3. Structural ordering is enforced.
4. Segmented Markdown can be parsed into modules.
"""

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
    assert any(
        marker in result
        for marker in ("## Scene", "## Exposition", "## Transition")
    )


# ---------------------------------------------------------------------------
# 2. Idempotence / normalization
# ---------------------------------------------------------------------------

def test_segmentation_idempotent():
    """
    Already-annotated Markdown must be preserved.

    The segmenter may normalize whitespace or ensure a trailing newline,
    but it must not destroy or restructure valid author-defined content.
    """
    annotated = """
# Test Novel

## Scene One
She stepped onto the sand.
"""

    segmenter = ModuleSegmenter()
    result = segmenter.segment_markdown(annotated, title="Test Novel")

    # Normalize both sides for semantic equivalence
    assert result.strip() == annotated.strip()


# ---------------------------------------------------------------------------
# 3. Structural ordering
# ---------------------------------------------------------------------------

def test_segmentation_enforces_correct_order():
    """
    Chapter headers must always appear before module headers.

    This protects the parser from malformed Markdown.
    """
    raw = "Raw prose with no structure."

    segmenter = ModuleSegmenter()
    result = segmenter.segment_markdown(raw, title="Order Test")

    chapter_index = result.index("#")
    scene_index = result.index("##")

    assert chapter_index < scene_index


# ---------------------------------------------------------------------------
# 4. Round-trip integration: Segment → Parse → Modules
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