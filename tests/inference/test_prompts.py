"""
Tests for prompt construction utilities.

These tests verify that:
- SYSTEM_PROMPT is a non-empty string.
- build_module_prompt includes all required fields.
- The output is valid plain text (not JSON or Markdown headers).
"""

from __future__ import annotations

from novel_testbed.inference.prompts import SYSTEM_PROMPT, build_module_prompt


def test_system_prompt_is_nonempty_string():
    """
    SYSTEM_PROMPT must be a non-empty string that instructs JSON-only output.
    """
    assert isinstance(SYSTEM_PROMPT, str)
    assert len(SYSTEM_PROMPT) > 0
    assert "JSON" in SYSTEM_PROMPT


def test_build_module_prompt_contains_novel_title():
    """
    The generated prompt must include the novel title.
    """
    prompt = build_module_prompt(
        novel_title="Hills Like White Elephants",
        chapter="Chapter One",
        module_title="Scene Arrival",
        module_text="They sat at a table.",
    )

    assert "Hills Like White Elephants" in prompt


def test_build_module_prompt_contains_chapter():
    """
    The generated prompt must include the chapter name.
    """
    prompt = build_module_prompt(
        novel_title="Test Novel",
        chapter="The Beginning",
        module_title="Scene 1",
        module_text="Text.",
    )

    assert "The Beginning" in prompt


def test_build_module_prompt_contains_module_title():
    """
    The generated prompt must include the module title.
    """
    prompt = build_module_prompt(
        novel_title="Test Novel",
        chapter="Chapter One",
        module_title="Exposition Background",
        module_text="Text.",
    )

    assert "Exposition Background" in prompt


def test_build_module_prompt_contains_module_text():
    """
    The generated prompt must include the module body text.
    """
    body = "She heard a sound in the dark."

    prompt = build_module_prompt(
        novel_title="Test Novel",
        chapter="Chapter One",
        module_title="Scene Night",
        module_text=body,
    )

    assert body in prompt


def test_build_module_prompt_requests_json_output():
    """
    The prompt must contain the JSON schema for the expected output.
    """
    prompt = build_module_prompt(
        novel_title="Test Novel",
        chapter="Chapter One",
        module_title="Scene One",
        module_text="Text.",
    )

    assert "expected_changes" in prompt
    assert "post_state" in prompt
    assert "confidence" in prompt


def test_build_module_prompt_returns_string():
    """
    build_module_prompt must return a plain string.
    """
    result = build_module_prompt(
        novel_title="N",
        chapter="C",
        module_title="M",
        module_text="T",
    )

    assert isinstance(result, str)
    assert len(result) > 0
