"""
Module contract assessment engine.

This module evaluates narrative module contracts using a configurable
set of rule objects. Each rule inspects a ModuleContract and may emit
a Finding describing a structural problem in the narrative.

The assessment process mirrors a unit-test runner:
- Each module is evaluated independently.
- Findings are collected.
- A severity (PASS, WARN, FAIL) is assigned.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import List, Sequence

from novel_testbed.contracts.rules import (
    Finding,
    MissingExpectedChangeRule,
    NoChangeRule,
    Rule,
    UnspecifiedStateRule,
)
from novel_testbed.models import ModuleContract

logger = logging.getLogger(__name__)


@dataclass
class ModuleReport:
    """
    Report describing the assessment outcome of a single narrative module.

    :param module_id: Unique identifier of the module.
    :param title: Title of the module.
    :param chapter: Chapter in which the module appears.
    :param severity: Overall severity (PASS, WARN, FAIL).
    :param findings: List of findings emitted by rule evaluation.
    """

    module_id: str
    title: str
    chapter: str
    severity: str
    findings: List[Finding]


def assess_contract(
    contracts: Sequence[ModuleContract],
    rules: Sequence[Rule] | None = None,
) -> List[ModuleReport]:
    """
    Assess a sequence of ModuleContracts using a set of narrative rules.

    Each module is evaluated independently. The resulting ModuleReport
    aggregates all findings and determines the highest severity:

    - FAIL if any rule emits a FAIL finding
    - WARN if no FAIL but at least one WARN
    - PASS otherwise

    :param contracts: Sequence of ModuleContract objects to assess.
    :param rules: Optional sequence of Rule objects. If not provided,
                  the default rule set is used.
    :return: List of ModuleReport entries.
    """
    logger.info("Starting contract assessment for %d modules.", len(contracts))

    if rules is None:
        rules = [
            UnspecifiedStateRule(),
            MissingExpectedChangeRule(),
            NoChangeRule(),
        ]
        logger.debug(
            "Using default rules: %s",
            [r.__class__.__name__ for r in rules],
        )
    else:
        logger.debug(
            "Using custom rules: %s",
            [r.__class__.__name__ for r in rules],
        )

    reports: List[ModuleReport] = []

    for contract in contracts:
        logger.debug(
            "Assessing module %s (%s)",
            contract.module_id,
            contract.module_title,
        )

        findings: List[Finding] = []

        for rule in rules:
            finding = rule.evaluate(contract)
            if finding is not None:
                logger.debug(
                    "Rule %s emitted finding: %s",
                    rule.__class__.__name__,
                    finding.severity,
                )
                findings.append(finding)

        severity = "PASS"
        if any(f.severity == "FAIL" for f in findings):
            severity = "FAIL"
        elif any(f.severity == "WARN" for f in findings):
            severity = "WARN"

        logger.info(
            "Module %s result: %s (%d findings)",
            contract.module_id,
            severity,
            len(findings),
        )

        reports.append(
            ModuleReport(
                module_id=contract.module_id,
                title=contract.module_title,
                chapter=contract.chapter,
                severity=severity,
                findings=findings,
            )
        )

    logger.info("Assessment complete.")
    return reports


def report_to_json(reports: Sequence[ModuleReport]) -> str:
    """
    Serialize a list of ModuleReport objects to a formatted JSON string.

    :param reports: Sequence of ModuleReport objects.
    :return: JSON string representation.
    """

    def convert(obj):
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return str(obj)

    logger.debug("Serializing %d module reports to JSON.", len(reports))
    return json.dumps([convert(r) for r in reports], indent=2) + "\n"