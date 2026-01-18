"""
Unit tests for the Markdown segmenter.

These tests verify the *mechanical guarantees* of the ModuleSegmenter:

- It adds structure to raw prose.
- It preserves existing valid structure.
- It repairs invalid ordering (Scene before Chapter).
- It produces correctly ordered Markdown.
- It never returns empty or unusable output.

These are low-level, string-based correctness tests.
"""

from novel_testbed.segmentation.segmenter import ModuleSegmenter


# ---------------------------------------------------------------------------
# Test Inputs
# ---------------------------------------------------------------------------

RAW_TEXT = """This is a story.

It has no structure.

Just paragraphs.
"""


ALREADY_SEGMENTED = """# Chapter One

## Scene 1

This is already structured.
"""


INVERTED_SEGMENTATION = """## Scene 1

# Chapter One

This is backwards.
"""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_segmenter_adds_chapter_and_scene():
    """
    Raw prose must be wrapped in at least:
    - one chapter heading
    - one scene heading

    This is the minimal structural promise of the segmenter.
    """
    segmenter = ModuleSegmenter()
    result = segmenter.segment_markdown(RAW_TEXT, title="Test Novel")

    assert result.startswith("# Test Novel")
    assert "## Scene 1" in result
    assert "This is a story." in result


def test_segmenter_is_idempotent():
    """
    Already-correctly annotated Markdown must be returned unchanged.

    The segmenter must never overwrite valid author-provided structure.
    """
    segmenter = ModuleSegmenter()
    result = segmenter.segment_markdown(ALREADY_SEGMENTED, title="Ignored")

    # Segmenter always normalizes to a trailing newline
    assert result == ALREADY_SEGMENTED.strip() + "\n"


def test_segmenter_repairs_inverted_structure():
    """
    If a Scene appears before a Chapter, the structure is invalid.

    The segmenter must rebuild the document into valid order:
        Chapter → Scene → Content
    """
    segmenter = ModuleSegmenter()
    result = segmenter.segment_markdown(INVERTED_SEGMENTATION, title="Fixed Novel")

    chapter_index = result.index("#")
    scene_index = result.index("##")

    assert chapter_index < scene_index
    assert result.startswith("# Fixed Novel")
    assert "This is backwards." in result


def test_segmenter_produces_valid_ordering():
    """
    Structural order must always be:

        Chapter (#) before Scene (##)

    This protects against malformed Markdown that would break the parser.
    """
    segmenter = ModuleSegmenter()
    result = segmenter.segment_markdown(RAW_TEXT, title="Test Novel")

    chapter_index = result.index("#")
    scene_index = result.index("##")

    assert chapter_index < scene_index


def test_segmenter_never_returns_empty():
    """
    The segmenter must always return usable Markdown, even for empty input.

    An empty string is still a novel. It still gets:
    - a chapter
    - a scene
    """
    segmenter = ModuleSegmenter()
    result = segmenter.segment_markdown("", title="Empty")

    assert "# Empty" in result
    assert "## Scene 1" in result