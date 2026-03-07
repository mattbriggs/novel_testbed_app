"""
LLM-based :class:`ContractInferencer` implementation.

This module provides :class:`OpenAIContractInferencer`, which uses
:class:`~novel_testbed.inference.llm_client.OpenAILLMClient` to populate
narrative contracts one module at a time.

Reader state is chained across modules so that each module's ``pre_state``
equals the previous module's ``post_state``, preserving narrative continuity.
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

    This inferencer treats the novel as a sequential state machine:

    - ``pre_state`` of module *N* equals ``post_state`` of module *N-1*.
    - ``post_state`` is inferred from the current module's text via the LLM.

    This chaining ensures that the reader's accumulating state across the
    novel is represented faithfully in the generated contracts.
    """

    def __init__(self, client: OpenAILLMClient) -> None:
        """
        Initialize the inferencer.

        :param client: An :class:`~novel_testbed.inference.llm_client.OpenAILLMClient`
                       instance used to call the LLM API.
        """
        self._client = client

    def infer(self, modules: Sequence[Module], *, novel_title: str) -> List[ModuleContract]:
        """
        Infer a full contract for a sequence of modules.

        Each module is sent to the LLM individually. The ``post_state`` returned
        by the LLM becomes the ``pre_state`` of the next module, chaining reader
        state across the entire novel.

        :param modules: Parsed modules from a :class:`~novel_testbed.models.Novel`.
        :param novel_title: Title of the novel, passed to the LLM for context.
        :return: List of fully populated :class:`~novel_testbed.models.ModuleContract`
                 objects in the same order as the input modules.
        :raises ValueError: If the LLM response is missing required keys or
                            contains invalid field values.
        """
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
        """
        Validate that an inference payload contains the required keys and types.

        :param payload: Raw dictionary returned by the LLM via
                        :meth:`~.OpenAILLMClient.infer_json`.
        :param module_id: Module identifier used in error messages.
        :raises ValueError: If any required key is missing or a field has an
                            unexpected type or out-of-range value.
        """
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
        """
        Convert a raw post-state dictionary into a :class:`~novel_testbed.models.ReaderState`.

        Uses :class:`~novel_testbed.inference.types.InferredState` as an
        intermediate validated container before building the final model.

        :param d: Dictionary with reader-state keys from the LLM response.
        :return: Populated :class:`~novel_testbed.models.ReaderState` instance.
        """
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
