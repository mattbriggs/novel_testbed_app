"""
LLM-based ContractInferencer implementation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Sequence

from novel_testbed.inference.base import ContractInferencer
from novel_testbed.inference.llm_client import OpenAILLMClient
from novel_testbed.inference.prompts import build_module_prompt
from novel_testbed.inference.types import InferredState, require_keys
from novel_testbed.models import Module, ModuleContract, ReaderState

logger = logging.getLogger(__name__)


class OpenAIContractInferencer(ContractInferencer):
    """
    Contract inference using OpenAI LLM calls.

    This inferencer treats the novel as a sequence:
    - pre_state is the prior module's post_state
    - post_state is inferred from the current module text
    """

    def __init__(self, client: OpenAILLMClient) -> None:
        self._client = client

    def infer(self, modules: Sequence[Module], *, novel_title: str) -> List[ModuleContract]:
        logger.info("Inferring contracts for %d modules.", len(modules))

        contracts: List[ModuleContract] = []
        running_state = ReaderState()  # defaults for module 1

        for idx, module in enumerate(modules, start=1):
            logger.info("Inferring module %d/%d: %s", idx, len(modules), module.id)

            prompt = build_module_prompt(
                novel_title=novel_title,
                chapter=module.chapter,
                module_title=module.title,
                module_text=module.text,
            )

            payload = self._client.infer_json(user_prompt=prompt)
            self._validate_payload(payload, module_id=module.id)

            post_state = self._to_reader_state(payload["post_state"])
            expected_changes = list(payload["expected_changes"] or [])

            contract = ModuleContract(
                module_id=module.id,
                module_title=module.title,
                chapter=module.chapter,
                module_type=module.module_type.value,
                fantasy_id=payload["post_state"].get("dominant_fantasy_id"),
                pre_state=running_state,
                post_state=post_state,
                expected_changes=expected_changes,
                anchors={"start": module.start_text, "end": module.end_text},
            )

            contracts.append(contract)
            running_state = post_state  # chain forward

        logger.info("Inference complete.")
        return contracts

    @staticmethod
    def _validate_payload(payload: Dict[str, Any], *, module_id: str) -> None:
        logger.debug("Validating inference payload for module %s", module_id)

        require_keys(payload, ["expected_changes", "post_state", "confidence", "notes"])
        if not isinstance(payload["expected_changes"], list):
            raise ValueError("expected_changes must be a list.")

        post_state = payload["post_state"]
        if not isinstance(post_state, dict):
            raise ValueError("post_state must be an object.")
        require_keys(
            post_state,
            [
                "genre",
                "power_balance",
                "emotional_tone",
                "dominant_fantasy_id",
                "threat_level",
                "agency_level",
            ],
        )

        confidence = payload.get("confidence")
        if confidence is not None and not (0.0 <= float(confidence) <= 1.0):
            raise ValueError("confidence must be between 0 and 1.")

    @staticmethod
    def _to_reader_state(d: Dict[str, Any]) -> ReaderState:
        state = InferredState(
            genre=d.get("genre"),
            power_balance=d.get("power_balance"),
            emotional_tone=d.get("emotional_tone"),
            dominant_fantasy_id=d.get("dominant_fantasy_id"),
            threat_level=d.get("threat_level"),
            agency_level=d.get("agency_level"),
        )
        return ReaderState(
            genre=state.genre,
            power_balance=state.power_balance,
            emotional_tone=state.emotional_tone,
            dominant_fantasy_id=state.dominant_fantasy_id,
            threat_level=state.threat_level,
            agency_level=state.agency_level,
        )