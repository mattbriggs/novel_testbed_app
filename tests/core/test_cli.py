"""
Tests for the Novel Testbed CLI.

These tests verify that:

- Argument parsing works.
- The `parse` command writes a blank YAML contract.
- The `infer` command writes a populated YAML contract (stubbed, no real LLM calls).
- The `assess` command writes a JSON report.

All LLM interaction is mocked. No network calls occur. No real API keys are used.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

import novel_testbed.cli as cli
from novel_testbed.models import ModuleContract, ReaderState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_sample_markdown(tmp_path: Path) -> Path:
    """Create a minimal Markdown novel for testing."""
    text = """
# Chapter One
## Scene Arrival
She stepped onto the sand.
"""
    path = tmp_path / "novel.md"
    path.write_text(text, encoding="utf-8")
    return path


def make_sample_contract(tmp_path: Path) -> Path:
    """Create a minimal contract YAML for testing the assess command."""
    data = {
        "modules": [
            {
                "module_id": "M001",
                "module_title": "Scene Arrival",
                "chapter": "Chapter One",
                "pre_state": {},
                "post_state": {},
                "expected_changes": [],
            }
        ]
    }
    path = tmp_path / "contract.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# parse command
# ---------------------------------------------------------------------------

def test_cli_parse_command(tmp_path: Path):
    """
    The `parse` command should create a blank contract YAML from Markdown.
    """
    novel_path = make_sample_markdown(tmp_path)
    out_path = tmp_path / "contract.yaml"

    code = cli.main(
        [
            "parse",
            str(novel_path),
            "-o",
            str(out_path),
        ]
    )

    assert code == 0
    assert out_path.exists()

    data = yaml.safe_load(out_path.read_text(encoding="utf-8"))
    assert "modules" in data
    assert len(data["modules"]) == 1
    assert data["modules"][0]["module_id"] == "M001"


# ---------------------------------------------------------------------------
# assess command
# ---------------------------------------------------------------------------

def test_cli_assess_command(tmp_path: Path):
    """
    The `assess` command should create a JSON report from a contract YAML.
    """
    contract_path = make_sample_contract(tmp_path)
    out_path = tmp_path / "report.json"

    code = cli.main(
        [
            "assess",
            str(contract_path),
            "-o",
            str(out_path),
        ]
    )

    assert code == 0
    assert out_path.exists()

    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == 1
    assert "severity" in data[0]


# ---------------------------------------------------------------------------
# infer command (fully stubbed)
# ---------------------------------------------------------------------------

def test_cli_infer_command_stubbed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """
    The `infer` command should create a populated contract YAML.

    This test stubs out:
    - The OpenAI API key check
    - The LLM client
    - The inferencer
    - The inference pipeline

    So:
    - No network calls occur
    - Output is deterministic
    - Only CLI wiring is tested
    """

    # ---- fake API key so secret validation passes ----
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake-key")

    novel_path = make_sample_markdown(tmp_path)
    out_path = tmp_path / "inferred_contract.yaml"

    # ---- stub infer_contract_from_markdown ----
    def fake_infer_contract_from_markdown(markdown_text, *, title, inferencer):
        return [
            ModuleContract(
                module_id="M001",
                module_title="Scene Arrival",
                chapter="Chapter One",
                module_type="scene",
                fantasy_id="UF_TEST",
                pre_state=ReaderState(),
                post_state=ReaderState(
                    genre="survival",
                    threat_level=0.3,
                    agency_level=0.7,
                ),
                expected_changes=["introduce survival context"],
                anchors={
                    "start": "She stepped",
                    "end": "the sand.",
                },
            )
        ]

    monkeypatch.setattr(
        cli,
        "infer_contract_from_markdown",
        fake_infer_contract_from_markdown,
    )

    # ---- stub OpenAI client and inferencer constructors ----
    class DummyClient:
        """Minimal stand-in for an LLM client."""

        pass

    class DummyInferencer:
        """Minimal stand-in for a contract inferencer."""

        def __init__(self, client):
            self.client = client

    monkeypatch.setattr(
        cli,
        "OpenAILLMClient",
        lambda config=None: DummyClient(),
    )
    monkeypatch.setattr(
        cli,
        "OpenAIContractInferencer",
        lambda client: DummyInferencer(client),
    )

    # ---- run CLI ----
    code = cli.main(
        [
            "infer",
            str(novel_path),
            "-o",
            str(out_path),
            "--model",
            "fake-model",
        ]
    )

    assert code == 0
    assert out_path.exists()

    data = yaml.safe_load(out_path.read_text(encoding="utf-8"))
    assert "modules" in data
    assert len(data["modules"]) == 1

    module = data["modules"][0]

    assert module["module_id"] == "M001"
    assert module["fantasy_id"] == "UF_TEST"
    assert module["expected_changes"] == ["introduce survival context"]
    assert module["post_state"]["genre"] == "survival"
    assert module["post_state"]["threat_level"] == 0.3