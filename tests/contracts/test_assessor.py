"""
Tests for the module contract assessment engine.

These tests verify that:
- Modules with no declared intent produce WARN
- Modules that declare intent but fail to change state produce FAIL
- Modules that change state correctly produce PASS
"""

from novel_testbed.contracts.assessor import assess_contract
from novel_testbed.models import ModuleContract, ReaderState


def test_assessor_warns_when_no_expected_changes():
    """
    A module with no expected changes declared should emit a WARN.

    This means the author has not stated what the passage is supposed to do.
    """
    contract = ModuleContract(
        module_id="M001",
        module_title="Scene 1",
        chapter="Ch1",
    )

    reports = assess_contract([contract])

    assert len(reports) == 1
    assert reports[0].severity == "WARN"
    assert reports[0].module_id == "M001"


def test_assessor_fails_when_expected_changes_but_state_unchanged():
    """
    A module that declares expected changes but does not alter reader state
    must FAIL. This is the core enforcement mechanism of the system.
    """
    contract = ModuleContract(
        module_id="M002",
        module_title="Scene 2",
        chapter="Ch1",
    )
    contract.expected_changes = ["power_shift"]
    contract.pre_state = ReaderState(
        genre="survival",
        power_balance="environment",
        emotional_tone="neutral",
        threat_level=0.2,
        agency_level=0.8,
    )
    contract.post_state = ReaderState(
        genre="survival",
        power_balance="environment",
        emotional_tone="neutral",
        threat_level=0.2,
        agency_level=0.8,
    )

    reports = assess_contract([contract])

    assert len(reports) == 1
    assert reports[0].severity == "FAIL"
    assert reports[0].module_id == "M002"


def test_assessor_passes_when_state_changes():
    """
    A module that declares intent and actually changes reader state should PASS.
    """
    contract = ModuleContract(
        module_id="M003",
        module_title="Scene 3",
        chapter="Ch1",
    )
    contract.expected_changes = ["threat escalation"]
    contract.pre_state = ReaderState(
        genre="survival",
        power_balance="environment",
        emotional_tone="controlled",
        threat_level=0.2,
        agency_level=0.9,
    )
    contract.post_state = ReaderState(
        genre="survival",
        power_balance="environment",
        emotional_tone="unease",
        threat_level=0.5,
        agency_level=0.85,
    )

    reports = assess_contract([contract])

    assert len(reports) == 1
    assert reports[0].severity == "PASS"
    assert reports[0].module_id == "M003"


def test_assessor_prioritizes_fail_over_warn():
    """
    If both FAIL and WARN findings exist, FAIL must dominate.
    """
    contract = ModuleContract(
        module_id="M004",
        module_title="Scene 4",
        chapter="Ch1",
    )
    contract.expected_changes = ["genre_shift"]
    # Missing pre_state/post_state triggers WARN
    # Declared change with no state change triggers FAIL

    reports = assess_contract([contract])

    assert len(reports) == 1
    assert reports[0].severity == "FAIL"


def test_assessor_handles_multiple_modules():
    """
    The assessor must handle multiple modules independently.
    """
    c1 = ModuleContract(
        module_id="M005",
        module_title="Scene 5",
        chapter="Ch1",
    )

    c2 = ModuleContract(
        module_id="M006",
        module_title="Scene 6",
        chapter="Ch1",
    )
    c2.expected_changes = ["danger"]
    c2.pre_state = ReaderState(
        genre="survival",
        power_balance="environment",
        emotional_tone="calm",
        threat_level=0.1,
        agency_level=0.9,
    )
    c2.post_state = ReaderState(
        genre="survival",
        power_balance="environment",
        emotional_tone="fear",
        threat_level=0.6,
        agency_level=0.7,
    )

    reports = assess_contract([c1, c2])

    assert len(reports) == 2
    assert reports[0].severity == "WARN"   # c1: no expected changes
    assert reports[1].severity == "PASS"   # c2: real state change