"""
Narrative contract assessment rules.

Each Rule inspects a ModuleContract and optionally emits a Finding.
Findings describe structural problems in narrative execution.

Rules are intentionally small, isolated, and composable.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional, Protocol

from novel_testbed.models import ModuleContract

logger = logging.getLogger(__name__)


class Rule(Protocol):
    """
    Protocol for all contract assessment rules.

    Every rule must define:
    - a human-readable name
    - an evaluate() method returning an optional Finding
    """

    name: str

    def evaluate(self, contract: ModuleContract) -> Optional["Finding"]:
        """
        Evaluate a ModuleContract.

        :param contract: ModuleContract to evaluate.
        :return: Finding if rule is violated, otherwise None.
        """
        ...


@dataclass
class Finding:
    """
    A single assessment result emitted by a Rule.

    :param rule: Name of the rule that emitted this finding.
    :param severity: PASS, WARN, or FAIL.
    :param message: Human-readable explanation.
    """

    rule: str
    severity: str  # PASS | WARN | FAIL
    message: str


def _state_is_specified(contract: ModuleContract) -> bool:
    """
    Determine whether both pre_state and post_state contain meaningful data.

    A state is considered specified if at least one meaningful attribute
    is not None in both pre_state and post_state.

    :param contract: ModuleContract to inspect.
    :return: True if states are specified, False otherwise.
    """
    logger.debug(
        "Checking whether reader state is specified for module %s",
        contract.module_id,
    )

    pre = contract.pre_state
    post = contract.post_state

    keys = [
        "genre",
        "power_balance",
        "emotional_tone",
        "dominant_fantasy_id",
        "threat_level",
        "agency_level",
    ]

    pre_ok = any(getattr(pre, key, None) is not None for key in keys)
    post_ok = any(getattr(post, key, None) is not None for key in keys)

    logger.debug(
        "State specification for module %s: pre=%s, post=%s",
        contract.module_id,
        pre_ok,
        post_ok,
    )

    return pre_ok and post_ok


class UnspecifiedStateRule:
    """
    Warn when no reader-state information has been provided.

    Without state information, no meaningful narrative assessment is possible.
    """

    name = "unspecified_state"

    def evaluate(self, contract: ModuleContract) -> Optional[Finding]:
        logger.debug("Evaluating UnspecifiedStateRule for %s", contract.module_id)

        if _state_is_specified(contract):
            return None

        logger.info(
            "Module %s has unspecified reader state.",
            contract.module_id,
        )

        return Finding(
            rule=self.name,
            severity="WARN",
            message="pre_state/post_state not specified; cannot assess.",
        )


class NoChangeRule:
    """
    Fail if expected changes are declared but:
    - state is missing, or
    - state exists but does not change.
    """

    name = "no_change"

    def evaluate(self, c: ModuleContract) -> Optional[Finding]:
        if not c.expected_changes:
            return None

        # Promised change but gave no measurable state
        if not _state_is_specified(c):
            return Finding(
                self.name,
                "FAIL",
                "expected_changes declared but pre_state/post_state are not specified.",
            )

        # Promised change but state did not change
        if c.pre_state == c.post_state:
            return Finding(
                self.name,
                "FAIL",
                "pre_state equals post_state but expected_changes declared.",
            )

        return None


class MissingExpectedChangeRule:
    """
    Warn when no narrative intent has been declared.

    expected_changes is how the author declares what the passage is supposed to do.
    """

    name = "missing_expected_change"

    def evaluate(self, contract: ModuleContract) -> Optional[Finding]:
        logger.debug(
            "Evaluating MissingExpectedChangeRule for %s",
            contract.module_id,
        )

        if contract.expected_changes:
            return None

        logger.info(
            "Module %s has no expected_changes declared.",
            contract.module_id,
        )

        return Finding(
            rule=self.name,
            severity="WARN",
            message="expected_changes is empty; consider declaring module intent.",
        )