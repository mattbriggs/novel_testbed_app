"""
Tests for the Annotated Markdown → Parse → Infer orchestration pipeline.

These tests validate that `infer_contract_from_markdown` behaves purely as an
*semantic* front-end. It must:

1. Pass annotated Markdown directly to the parser.
2. Pass parsed modules to the inferencer.
3. Return inferred ModuleContract objects.
4. Emit a warning if no modules are parsed.

Segmentation is explicitly out of scope for this function.
"""

from __future__ import annotations

from typing import List

import pytest

from novel_testbed.inference.auto_contract import infer_contract_from_markdown
from novel_testbed.models import Module, ModuleContract, ModuleType


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------

class DummyParser:
    """Fake parser that always returns a novel with one module."""

    def parse(self, text: str, *, title: str):
        return DummyNovel(title)


class DummyEmptyParser:
    """Fake parser that returns no modules (simulates malformed Markdown)."""

    def parse(self, text: str, *, title: str):
        return DummyNovel(title, modules=[])


class DummyNovel:
    """Fake Novel object."""

    def __init__(self, title: str, modules: List[Module] | None = None):
        self.title = title

        if modules is None:
            self.modules = [
                Module(
                    id="M001",
                    chapter="Chapter One",
                    title="Scene 1",
                    module_type=ModuleType.SCENE,
                    start_line=1,
                    end_line=2,
                    text="Fake module text",
                    start_text="Fake",
                    end_text="text",
                )
            ]
        else:
            self.modules = modules


class DummyInferencer:
    """Fake inferencer that deterministically creates ModuleContracts."""

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

def test_infer_pipeline_basic(monkeypatch):
    """
    The pipeline must:
    - parse annotated Markdown
    - infer contracts
    - return ModuleContract objects
    """
    from novel_testbed.inference import auto_contract

    monkeypatch.setattr(
        auto_contract,
        "CommonMarkNovelParser",
        lambda: DummyParser(),
    )

    annotated = """
# Chapter One
## Scene 1
She stepped onto the sand.
"""

    contracts = infer_contract_from_markdown(
        annotated,
        title="Test Novel",
        inferencer=DummyInferencer(),
    )

    assert isinstance(contracts, list)
    assert len(contracts) == 1
    assert isinstance(contracts[0], ModuleContract)
    assert contracts[0].module_id == "M001"


def test_infer_pipeline_warns_when_no_modules(monkeypatch, caplog):
    """
    If no modules are parsed, a warning must be emitted.
    """
    from novel_testbed.inference import auto_contract

    monkeypatch.setattr(
        auto_contract,
        "CommonMarkNovelParser",
        lambda: DummyEmptyParser(),
    )

    annotated = "# Chapter Only\n\nNo module headers here."

    with caplog.at_level("WARNING", logger="novel_testbed.inference.auto_contract"):
        contracts = infer_contract_from_markdown(
            annotated,
            title="Broken Novel",
            inferencer=DummyInferencer(),
        )

    assert "No modules were parsed" in caplog.text
    assert contracts == []


def test_pipeline_ordering_is_enforced(monkeypatch):
    """
    Enforces the conceptual ordering:

        parse → infer
    """
    calls = []

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
        "# Chapter One\n\n## Scene 1\nText.",
        title="Order Test",
        inferencer=TrackingInferencer(),
    )

    assert calls == ["parse", "infer"]