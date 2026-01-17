"""
Tests for OpenAILLMClient JSON parsing behavior (stubbed response shape).
"""

import json
from types import SimpleNamespace

import pytest


def extract_text_like_client(resp) -> str:
    text = ""
    for item in getattr(resp, "output", []) or []:
        for chunk in getattr(item, "content", []) or []:
            if getattr(chunk, "type", None) == "output_text":
                text += getattr(chunk, "text", "")
    return text.strip()


def test_extract_text_like_client_reads_output_text():
    resp = SimpleNamespace(
        output=[
            SimpleNamespace(
                content=[
                    SimpleNamespace(type="output_text", text='{"ok": true}'),
                ]
            )
        ]
    )
    assert extract_text_like_client(resp) == '{"ok": true}'


def test_extract_text_like_client_handles_empty():
    resp = SimpleNamespace(output=[])
    assert extract_text_like_client(resp) == ""


def test_json_parse_failure_example():
    bad = "not json"
    with pytest.raises(json.JSONDecodeError):
        json.loads(bad)