"""
Tests for LLMSegmenter using a stubbed LLM client.

These tests verify that:
- LLMSegmenter passes the correct prompt structure to the client.
- The response from the client is returned as the segmented output.
- LLMSegmenter inherits from ModuleSegmenter.
- The stubbed client's complete() method is called (not infer_json).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from novel_testbed.segmentation.segmenter import LLMSegmenter, ModuleSegmenter


# ---------------------------------------------------------------------------
# Stub
# ---------------------------------------------------------------------------

@dataclass
class StubLLMClient:
    """
    A stub client that records calls to complete() and returns a preset response.
    """

    response: str
    calls: List[str] = field(default_factory=list)

    def complete(self, prompt: str) -> str:
        """Record the prompt and return the preset response."""
        self.calls.append(prompt)
        return self.response


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_llm_segmenter_is_subclass_of_module_segmenter():
    """
    LLMSegmenter must inherit from ModuleSegmenter.
    """
    stub = StubLLMClient(response="# Title\n\n## Scene 1\nText.\n")
    segmenter = LLMSegmenter(client=stub)

    assert isinstance(segmenter, ModuleSegmenter)


def test_llm_segmenter_calls_client_complete():
    """
    segment_markdown must invoke client.complete() exactly once.
    """
    annotated = "# Chapter\n\n## Scene 1\nShe stepped.\n"
    stub = StubLLMClient(response=annotated)
    segmenter = LLMSegmenter(client=stub)

    segmenter.segment_markdown("Raw prose.", title="Test Novel")

    assert len(stub.calls) == 1


def test_llm_segmenter_passes_title_in_prompt():
    """
    The prompt sent to the client must contain the novel title.
    """
    stub = StubLLMClient(response="# MyTitle\n\n## Scene 1\nText.\n")
    segmenter = LLMSegmenter(client=stub)

    segmenter.segment_markdown("Prose.", title="MyTitle")

    assert "MyTitle" in stub.calls[0]


def test_llm_segmenter_passes_text_in_prompt():
    """
    The prompt sent to the client must include the original text.
    """
    raw = "She heard a sound in the dark."
    stub = StubLLMClient(response="# T\n\n## Scene 1\n" + raw + "\n")
    segmenter = LLMSegmenter(client=stub)

    segmenter.segment_markdown(raw, title="Test")

    assert raw in stub.calls[0]


def test_llm_segmenter_returns_trailing_newline():
    """
    The output must always end with a single trailing newline.
    """
    response_without_newline = "# Title\n\n## Scene 1\nText."
    stub = StubLLMClient(response=response_without_newline)
    segmenter = LLMSegmenter(client=stub)

    result = segmenter.segment_markdown("Text.", title="Title")

    assert result.endswith("\n")


def test_llm_segmenter_strips_extra_whitespace_from_response():
    """
    Extra whitespace around the LLM response must be stripped before the
    trailing newline is appended.
    """
    stub = StubLLMClient(response="  # Title\n\n## Scene 1\nText.  \n\n  ")
    segmenter = LLMSegmenter(client=stub)

    result = segmenter.segment_markdown("Text.", title="Title")

    assert not result.startswith(" ")
    assert result.endswith("\n")
    assert result.count("\n\n\n") == 0  # no triple newlines from extra whitespace


def test_llm_segmenter_returns_client_response_content():
    """
    The body of the result must be the client's response (stripped + newline).
    """
    expected_body = "# Title\n\n## Scene 1\nTest content."
    stub = StubLLMClient(response=expected_body)
    segmenter = LLMSegmenter(client=stub)

    result = segmenter.segment_markdown("Test content.", title="Title")

    assert result == expected_body + "\n"
