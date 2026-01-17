"""
Tests for core data models.
"""

from novel_testbed.models import (
    Module,
    ModuleContract,
    ModuleType,
    Novel,
    ReaderState,
)


def test_module_creation():
    module = Module(
        id="M001",
        chapter="Ch1",
        title="Scene One",
        module_type=ModuleType.SCENE,
        start_line=1,
        end_line=10,
        text="Some narrative text.",
    )

    assert module.id == "M001"
    assert module.module_type == ModuleType.SCENE
    assert module.start_text == ""
    assert module.metadata == {}


def test_novel_creation():
    novel = Novel(title="Test Novel")

    assert novel.title == "Test Novel"
    assert novel.modules == []


def test_reader_state_defaults():
    state = ReaderState()

    assert state.genre is None
    assert state.threat_level is None
    assert state.notes == {}


def test_module_contract_defaults():
    contract = ModuleContract(
        module_id="M001",
        module_title="Scene One",
        chapter="Ch1",
    )

    assert contract.pre_state is not None
    assert contract.post_state is not None
    assert contract.expected_changes == []
    assert contract.anchors == {}


def test_module_contract_accepts_state_and_changes():
    pre = ReaderState(genre="survival", threat_level=0.2)
    post = ReaderState(genre="survival", threat_level=0.5)

    contract = ModuleContract(
        module_id="M002",
        module_title="Scene Two",
        chapter="Ch1",
        pre_state=pre,
        post_state=post,
        expected_changes=["threat escalation"],
    )

    assert contract.pre_state.threat_level == 0.2
    assert contract.post_state.threat_level == 0.5
    assert contract.expected_changes == ["threat escalation"]


def test_module_type_enum_values():
    assert ModuleType.SCENE.value == "scene"
    assert ModuleType.EXPOSITION.value == "exposition"
    assert ModuleType.TRANSITION.value == "transition"
    assert ModuleType.OTHER.value == "other"