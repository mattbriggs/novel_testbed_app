"""
Tests for the Markdown → Segment → Parse → Infer orchestration pipeline.

These tests validate that `infer_contract_from_markdown` behaves purely as an
orchestrator. It must:

1. Call the segmenter.
2. Pass segmented Markdown to the parser.
3. Pass parsed modules to the inferencer.
4. Return contracts.
5. Optionally return annotated Markdown.

No semantic logic lives here. No real LLMs. No real parsing. Everything is stubbed.
"""

from __future__ import annotations

from typing import List

import pytest

from novel_testbed.inference.auto_contract import infer_contract_from_markdown
from novel_testbed.models import Module, ModuleContract, ModuleType


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------

class DummySegmenter:
    """Fake segmenter that marks text as segmented."""

    def segment_markdown(self, text: str, title: str) -> str:
        return f"# {title}\n\n## Scene 1\n{text}"


class DummyParser:
    """Fake parser that always returns a single module."""

    def __init__(self):
        self.last_text = None

    def parse(self, text: str, *, title: str):
        self.last_text = text
        return DummyNovel(title=title)


class DummyNovel:
    """Fake Novel object with one module."""

    def __init__(self, title: str):
        self.title = title
        self.modules = [
            Module(
                id="M001",
                chapter="Test Chapter",
                title="Scene 1",
                module_type=ModuleType.SCENE,
                start_line=1,
                end_line=2,
                text="Fake module text",
                start_text="Fake",
                end_text="text",
            )
        ]


class DummyInferencer:
    """Fake inferencer that converts modules into contracts deterministically."""

    def infer(self, modules: List[Module], *, novel_title: str):
        return [
            ModuleContract(
                module_id=m.id,
                module_title=m.title,
                chapter=m.chapter,
                module_type=m.module_type.value,
                pre_state=None,
                post_state=None,
                expected_changes=[],
                anchors={},
            )
            for m in modules
        ]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_infer_pipeline_basic():
    """
    The pipeline must:
    - segment
    - parse
    - infer
    - return contracts
    """
    raw = "She stepped onto the sand."
    title = "Test Novel"

    contracts = infer_contract_from_markdown(
        raw,
        title=title,
        inferencer=DummyInferencer(),
        segmenter=DummySegmenter(),
    )

    assert isinstance(contracts, list)
    assert len(contracts) == 1
    assert isinstance(contracts[0], ModuleContract)
    assert contracts[0].module_id == "M001"


def test_infer_pipeline_returns_annotated_markdown():
    """
    When return_annotated_markdown=True, the pipeline must return:

        (contracts, annotated_markdown)
    """
    raw = "She stepped onto the sand."
    title = "Test Novel"

    contracts, annotated = infer_contract_from_markdown(
        raw,
        title=title,
        inferencer=DummyInferencer(),
        segmenter=DummySegmenter(),
        return_annotated_markdown=True,
    )

    assert isinstance(contracts, list)
    assert isinstance(annotated, str)
    assert annotated.startswith("# Test Novel")
    assert "## Scene 1" in annotated


def test_infer_pipeline_uses_default_segmenter_when_missing(monkeypatch):
    """
    If no segmenter is provided, the function must construct one internally.
    """

    class FakeDefaultSegmenter:
        def segment_markdown(self, text: str, title: str) -> str:
            return f"# {title}\n\n## Scene Auto\n{text}"

    from novel_testbed.inference import auto_contract

    monkeypatch.setattr(
        auto_contract,
        "ModuleSegmenter",
        lambda: FakeDefaultSegmenter(),
    )

    raw = "Raw text."
    title = "Auto Segment"

    contracts, annotated = infer_contract_from_markdown(
        raw,
        title=title,
        inferencer=DummyInferencer(),
        return_annotated_markdown=True,
    )

    assert "# Auto Segment" in annotated
    assert "## Scene Auto" in annotated
    assert len(contracts) == 1


def test_pipeline_ordering_is_enforced(monkeypatch):
    """
    This test enforces the conceptual ordering:

        segment → parse → infer
    """
    calls = []

    class TrackingSegmenter:
        def segment_markdown(self, text: str, title: str) -> str:
            calls.append("segment")
            return f"# {title}\n\n## Scene 1\n{text}"

    class TrackingParser:
        def parse(self, text: str, *, title: str):
            calls.append("parse")
            return DummyNovel(title)

    class TrackingInferencer:
        def infer(self, modules, *, novel_title):
            calls.append("infer")
            return []

    from novel_testbed.inference import auto_contract

    monkeypatch.setattr(
        auto_contract,
        "CommonMarkNovelParser",
        lambda: TrackingParser(),
    )

    infer_contract_from_markdown(
        "text",
        title="Order Test",
        inferencer=TrackingInferencer(),
        segmenter=TrackingSegmenter(),
    )

    assert calls == ["segment", "parse", "infer"]