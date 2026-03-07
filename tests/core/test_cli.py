"""
Tests for the Novel Testbed CLI.

These tests verify that:

- Argument parsing works correctly for all four subcommands.
- ``_require_openai_key`` raises ``SystemExit`` when the key is absent.
- The ``segment`` command writes annotated Markdown.
- The ``parse`` command writes a blank YAML contract.
- The ``infer`` command consumes annotated Markdown and writes a populated contract YAML.
- The ``assess`` command writes a JSON report.
- The ``--llm`` flag for segment invokes ``LLMSegmenter``.

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
    """Create raw Markdown for segmentation tests."""
    text = "She stepped onto the sand."
    path = tmp_path / "novel.md"
    path.write_text(text, encoding="utf-8")
    return path


def make_sample_annotated_markdown(tmp_path: Path) -> Path:
    """Create already-annotated Markdown for parse / infer tests."""
    text = """
# Chapter One
## Scene Arrival
She stepped onto the sand.
"""
    path = tmp_path / "annotated.md"
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
# segment command
# ---------------------------------------------------------------------------

def test_cli_segment_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """
    The `segment` command should write annotated Markdown.
    """
    novel_path = make_sample_markdown(tmp_path)
    out_path = tmp_path / "annotated.md"

    class DummySegmenter:
        def segment_markdown(self, text: str, title: str) -> str:
            return f"# {title}\n\n## Scene Dummy\n{text}"

    monkeypatch.setattr(cli, "ModuleSegmenter", lambda: DummySegmenter())

    code = cli.main(
        [
            "segment",
            str(novel_path),
            "-o",
            str(out_path),
        ]
    )

    assert code == 0
    assert out_path.exists()

    content = out_path.read_text(encoding="utf-8")
    assert "# novel" in content.lower()
    assert "## Scene Dummy" in content


# ---------------------------------------------------------------------------
# parse command
# ---------------------------------------------------------------------------

def test_cli_parse_command(tmp_path: Path):
    """
    The `parse` command should create a blank contract YAML from annotated Markdown.
    """
    annotated_path = make_sample_annotated_markdown(tmp_path)
    out_path = tmp_path / "contract.yaml"

    code = cli.main(
        [
            "parse",
            str(annotated_path),
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
# infer command (annotated Markdown only, fully stubbed)
# ---------------------------------------------------------------------------

def test_cli_infer_command_stubbed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """
    The `infer` command should:

        annotated Markdown → parse → infer → YAML

    No segmentation happens here.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake-key")

    annotated_path = make_sample_annotated_markdown(tmp_path)
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

    # ---- stub OpenAI client + inferencer ----
    class DummyClient:
        pass

    class DummyInferencer:
        def __init__(self, client):
            self.client = client

    monkeypatch.setattr(cli, "OpenAILLMClient", lambda config=None: DummyClient())
    monkeypatch.setattr(cli, "OpenAIContractInferencer", lambda client: DummyInferencer(client))

    code = cli.main(
        [
            "infer",
            str(annotated_path),
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
# _require_openai_key
# ---------------------------------------------------------------------------

def test_require_openai_key_raises_when_missing(monkeypatch: pytest.MonkeyPatch):
    """
    _require_openai_key must raise SystemExit when OPENAI_API_KEY is not set.
    """
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(SystemExit) as exc_info:
        cli._require_openai_key()

    assert exc_info.value.code != 0 or isinstance(exc_info.value.code, str)


def test_require_openai_key_passes_when_set(monkeypatch: pytest.MonkeyPatch):
    """
    _require_openai_key must not raise when OPENAI_API_KEY is present.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake")
    cli._require_openai_key()  # Should not raise


# ---------------------------------------------------------------------------
# build_arg_parser
# ---------------------------------------------------------------------------

def test_build_arg_parser_returns_parser():
    """
    build_arg_parser must return an ArgumentParser with prog=novel-testbed.
    """
    parser = cli.build_arg_parser()
    assert parser.prog == "novel-testbed"


def test_build_arg_parser_segment_subcommand():
    """
    The segment subcommand must accept input, -o, --title, and --llm.
    """
    parser = cli.build_arg_parser()
    args = parser.parse_args(["segment", "novel.md", "-o", "out.md", "--title", "My Novel"])

    assert args.cmd == "segment"
    assert args.input == "novel.md"
    assert args.output == "out.md"
    assert args.title == "My Novel"
    assert args.llm is False


def test_build_arg_parser_segment_llm_flag():
    """
    The --llm flag must default to False and be set to True when supplied.
    """
    parser = cli.build_arg_parser()
    args = parser.parse_args(["segment", "novel.md", "-o", "out.md", "--llm"])

    assert args.llm is True


def test_build_arg_parser_infer_default_model():
    """
    The infer subcommand must use gpt-4.1-mini as the default model.
    """
    parser = cli.build_arg_parser()
    args = parser.parse_args(["infer", "annotated.md", "-o", "contract.yaml"])

    assert args.model == "gpt-4.1-mini"


# ---------------------------------------------------------------------------
# segment --llm flag (stubbed)
# ---------------------------------------------------------------------------

def test_cli_segment_llm_flag_uses_llm_segmenter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """
    When --llm is passed, segment must instantiate LLMSegmenter with a client.

    Both OpenAILLMClient construction and LLMSegmenter are stubbed.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake")
    novel_path = make_sample_markdown(tmp_path)
    out_path = tmp_path / "annotated.md"

    annotated_text = "# Test Novel\n\n## Scene 1\nShe stepped onto the sand.\n"

    class DummyLLMClient:
        def complete(self, prompt: str) -> str:
            return annotated_text.strip()

    class DummyLLMSegmenter:
        def __init__(self, client):
            self.client = client

        def segment_markdown(self, text: str, title: str) -> str:
            return annotated_text

    monkeypatch.setattr(cli, "OpenAILLMClient", lambda config=None: DummyLLMClient())
    monkeypatch.setattr(cli, "LLMSegmenter", lambda client: DummyLLMSegmenter(client=client))

    code = cli.main(["segment", str(novel_path), "-o", str(out_path), "--llm"])

    assert code == 0
    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8")
    assert "# Test Novel" in content