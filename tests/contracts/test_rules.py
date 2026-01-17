"""
Tests for narrative contract assessment rules.
"""

from novel_testbed.contracts.rules import (
    Finding,
    MissingExpectedChangeRule,
    NoChangeRule,
    UnspecifiedStateRule,
)
from novel_testbed.models import ModuleContract, ReaderState


def make_blank_contract(module_id="M001"):
    return ModuleContract(
        module_id=module_id,
        module_title="Scene 1",
        chapter="Ch1",
    )


def test_unspecified_state_rule_warns_when_state_missing():
    rule = UnspecifiedStateRule()
    contract = make_blank_contract()

    finding = rule.evaluate(contract)

    assert isinstance(finding, Finding)
    assert finding.severity == "WARN"
    assert "not specified" in finding.message


def test_unspecified_state_rule_passes_when_state_present():
    rule = UnspecifiedStateRule()
    contract = make_blank_contract()
    contract.pre_state = ReaderState(genre="survival", threat_level=0.2)
    contract.post_state = ReaderState(genre="survival", threat_level=0.3)

    finding = rule.evaluate(contract)

    assert finding is None


def test_missing_expected_change_rule_warns_when_empty():
    rule = MissingExpectedChangeRule()
    contract = make_blank_contract()

    finding = rule.evaluate(contract)

    assert isinstance(finding, Finding)
    assert finding.severity == "WARN"


def test_missing_expected_change_rule_passes_when_present():
    rule = MissingExpectedChangeRule()
    contract = make_blank_contract()
    contract.expected_changes = ["threat escalation"]

    finding = rule.evaluate(contract)

    assert finding is None


def test_no_change_rule_fails_when_state_unchanged_and_expectations_present():
    rule = NoChangeRule()
    contract = make_blank_contract()
    contract.expected_changes = ["power shift"]

    state = ReaderState(
        genre="survival",
        power_balance="environment",
        emotional_tone="neutral",
        threat_level=0.2,
        agency_level=0.8,
    )
    contract.pre_state = state
    contract.post_state = state

    finding = rule.evaluate(contract)

    assert isinstance(finding, Finding)
    assert finding.severity == "FAIL"


def test_no_change_rule_passes_when_state_changes():
    rule = NoChangeRule()
    contract = make_blank_contract()
    contract.expected_changes = ["power shift"]

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
        emotional_tone="fear",
        threat_level=0.6,
        agency_level=0.6,
    )

    finding = rule.evaluate(contract)

    assert finding is None


def test_no_change_rule_ignores_when_state_unspecified():
    rule = NoChangeRule()
    contract = make_blank_contract()
    contract.expected_changes = ["power shift"]

    finding = rule.evaluate(contract)

    assert finding is None