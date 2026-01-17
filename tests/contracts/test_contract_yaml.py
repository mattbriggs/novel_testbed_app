"""
Tests for YAML serialization and deserialization of ModuleContract.

These tests verify that:
- A ModuleContract can be serialized to YAML
- The YAML can be loaded back into a ModuleContract
- ReaderState, expected_changes, and structural fields survive round-trip
"""

from __future__ import annotations

from novel_testbed.models import ModuleContract, ReaderState
from novel_testbed.contracts.contract import dump_contract_yaml, load_contract_yaml


def test_dump_and_load_contract_yaml_roundtrip():
    """
    dump_contract_yaml → load_contract_yaml should preserve contract data.
    """
    contract = ModuleContract(
        module_id="M001",
        module_title="Scene",
        chapter="Ch",
        module_type="scene",
        fantasy_id="UF_TEST",
        pre_state=ReaderState(
            genre="survival",
            threat_level=0.1,
        ),
        post_state=ReaderState(
            genre="thriller",
            threat_level=0.9,
        ),
        expected_changes=["genre_shift", "threat_escalation"],
        anchors={
            "start": "The scene opens.",
            "end": "The danger is clear.",
        },
    )

    yaml_text = dump_contract_yaml([contract])
    loaded = load_contract_yaml(yaml_text)

    assert len(loaded) == 1
    out = loaded[0]

    # Structural identity
    assert out.module_id == "M001"
    assert out.module_title == "Scene"
    assert out.chapter == "Ch"
    assert out.module_type == "scene"
    assert out.fantasy_id == "UF_TEST"

    # Reader state integrity
    assert out.pre_state.genre == "survival"
    assert out.pre_state.threat_level == 0.1
    assert out.post_state.genre == "thriller"
    assert out.post_state.threat_level == 0.9

    # Semantic intent preserved
    assert out.expected_changes == ["genre_shift", "threat_escalation"]

    # Anchors preserved
    assert out.anchors["start"] == "The scene opens."
    assert out.anchors["end"] == "The danger is clear."