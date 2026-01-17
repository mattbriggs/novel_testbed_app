"""
Tests for contract generation and YAML serialization.

These tests verify:
- Contract generation from a Novel
- YAML dump format
- YAML round-trip integrity
- Graceful handling of empty YAML
"""

from __future__ import annotations

import yaml

from novel_testbed.contracts.contract import (
    contract_from_novel,
    dump_contract_yaml,
    load_contract_yaml,
)
from novel_testbed.models import Module, ModuleType, Novel


def make_test_novel() -> Novel:
    """
    Create a minimal Novel object for testing.

    The Module includes all required structural fields so it matches
    the real parser output.
    """
    module = Module(
        id="M001",
        chapter="Chapter 1",
        title="Scene 1",
        module_type=ModuleType.SCENE,
        start_line=1,
        end_line=3,
        text="This is the full body of the scene.",
        start_text="This is the first line.",
        end_text="This is the last line.",
    )

    return Novel(title="Test Novel", modules=[module])


def test_contract_from_novel_creates_entries():
    """
    contract_from_novel should create one ModuleContract per Module.
    """
    novel = make_test_novel()
    contracts = contract_from_novel(novel)

    assert len(contracts) == 1
    contract = contracts[0]

    assert contract.module_id == "M001"
    assert contract.module_title == "Scene 1"
    assert contract.chapter == "Chapter 1"
    assert contract.module_type == "scene"
    assert contract.anchors["start"] == "This is the first line."
    assert contract.anchors["end"] == "This is the last line."
    assert contract.expected_changes == []
    assert contract.pre_state is not None
    assert contract.post_state is not None


def test_dump_contract_yaml_is_valid_yaml():
    """
    dump_contract_yaml should produce parseable YAML with a modules list.
    """
    novel = make_test_novel()
    contracts = contract_from_novel(novel)

    yaml_text = dump_contract_yaml(contracts)
    data = yaml.safe_load(yaml_text)

    assert "modules" in data
    assert isinstance(data["modules"], list)
    assert len(data["modules"]) == 1
    assert data["modules"][0]["module_id"] == "M001"
    assert data["modules"][0]["expected_changes"] == []


def test_load_contract_yaml_round_trip():
    """
    dump → load should preserve contract structure and values.
    """
    novel = make_test_novel()
    contracts = contract_from_novel(novel)

    yaml_text = dump_contract_yaml(contracts)
    loaded = load_contract_yaml(yaml_text)

    assert len(loaded) == 1

    original = contracts[0]
    reloaded = loaded[0]

    assert original.module_id == reloaded.module_id
    assert original.module_title == reloaded.module_title
    assert original.chapter == reloaded.chapter
    assert original.module_type == reloaded.module_type
    assert original.anchors == reloaded.anchors
    assert original.expected_changes == reloaded.expected_changes
    assert original.pre_state == reloaded.pre_state
    assert original.post_state == reloaded.post_state


def test_load_contract_yaml_handles_empty():
    """
    Empty YAML input should yield an empty contract list.
    """
    loaded = load_contract_yaml("")
    assert loaded == []