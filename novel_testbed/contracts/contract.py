"""
Contract generation and serialization utilities.

This module is responsible for:
- Creating a blank narrative contract from a parsed Novel.
- Serializing that contract to YAML.
- Loading a contract back from YAML.

The contract is the executable specification of narrative intent.
"""

from __future__ import annotations

import logging
from dataclasses import asdict
from typing import List

import yaml

from novel_testbed.models import ModuleContract, Novel, ReaderState

logger = logging.getLogger(__name__)


def contract_from_novel(novel: Novel) -> List[ModuleContract]:
    """
    Build a blank narrative contract from a parsed Novel.

    Each module in the novel becomes a ModuleContract with:
    - structural metadata
    - text anchors
    - empty reader states
    - no declared expectations

    The resulting contract is syntactically complete but semantically empty.
    It is intended to be filled either manually or by an inference engine.

    :param novel: Parsed Novel object.
    :return: List of ModuleContract instances.
    """
    logger.info("Building contract from novel with %d modules.", len(novel.modules))

    contracts: List[ModuleContract] = []

    for module in novel.modules:
        logger.debug(
            "Creating contract entry for module %s (%s)",
            module.id,
            module.title,
        )

        contracts.append(
            ModuleContract(
                module_id=module.id,
                module_title=module.title,
                chapter=module.chapter,
                module_type=module.module_type.value,
                anchors={
                    "start": module.start_text,
                    "end": module.end_text,
                },
                pre_state=ReaderState(),
                post_state=ReaderState(),
                expected_changes=[],
            )
        )

    logger.info("Contract generation complete.")
    return contracts


def dump_contract_yaml(
    contracts: List[ModuleContract],
    *,
    source: dict | None = None,
) -> str:
    """
    Serialize a list of ModuleContract objects to YAML.

    The YAML output is the canonical external representation of a narrative
    contract. It is both human-editable and machine-consumable.

    Optionally embeds source provenance metadata so that:
    - The exact Markdown input can be identified
    - Contract drift can be detected
    - Reproducibility is preserved

    :param contracts: List of ModuleContract entries.
    :param source: Optional source metadata dictionary (fingerprint, paths, timestamps).
    :return: YAML string.
    """
    logger.debug("Serializing %d contracts to YAML.", len(contracts))

    payload = {
        "source": source or {},
        "modules": [asdict(contract) for contract in contracts],
    }

    text = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)

    logger.debug("YAML serialization complete (%d characters).", len(text))
    return text


def load_contract_yaml(text: str) -> List[ModuleContract]:
    """
    Load ModuleContract objects from YAML text.

    The YAML must define a top-level ``modules`` list, where each entry
    corresponds to one ModuleContract specification.

    The ``expected_changes`` field is always normalized to ``List[str]``,
    even if missing or null in the source YAML.

    :param text: YAML string.
    :return: List of ModuleContract entries.
    """
    logger.debug("Loading contracts from YAML.")

    data = yaml.safe_load(text) or {}
    modules = data.get("modules", [])

    logger.info("Found %d modules in YAML contract.", len(modules))

    contracts: List[ModuleContract] = []

    for entry in modules:
        module_id = entry.get("module_id")
        logger.debug("Loading contract for module %s", module_id)

        pre_state_data = entry.get("pre_state") or {}
        post_state_data = entry.get("post_state") or {}

        pre_state = ReaderState(**pre_state_data)
        post_state = ReaderState(**post_state_data)

        expected_changes = entry.get("expected_changes") or []
        if not isinstance(expected_changes, list):
            raise ValueError(
                f"expected_changes must be a list of strings for module {module_id}"
            )

        contracts.append(
            ModuleContract(
                module_id=entry["module_id"],
                module_title=entry.get("module_title", ""),
                chapter=entry.get("chapter", ""),
                page_range=entry.get("page_range"),
                module_type=entry.get("module_type"),
                fantasy_id=entry.get("fantasy_id"),
                pre_state=pre_state,
                post_state=post_state,
                expected_changes=list(expected_changes),
                anchors=dict(entry.get("anchors") or {}),
            )
        )

    logger.info("Contract loading complete.")
    return contracts