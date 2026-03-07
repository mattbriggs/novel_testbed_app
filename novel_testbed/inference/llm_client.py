"""
OpenAI LLM client adapter for contract inference and segmentation.

This module isolates API integration so the rest of the codebase
does not depend on OpenAI SDK details.

Two call patterns are supported:

- :meth:`complete` — Free-form text completion (used by segmentation).
- :meth:`infer_json` — JSON-structured inference (used by contract inference).
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from novel_testbed.inference.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LLMClientConfig:
    """
    Configuration for the LLM client.

    :param model: Model name used for inference.
    :param timeout_s: Request timeout (seconds).
    """

    model: str = "gpt-4.1-mini"
    timeout_s: int = 60


class OpenAILLMClient:
    """
    OpenAI-backed LLM client using the official Python SDK.

    Requires ``OPENAI_API_KEY`` to be set in the environment.

    This client is the single integration point with the OpenAI API.
    It supports two calling modes:

    - :meth:`complete` for raw text responses (e.g. segmentation)
    - :meth:`infer_json` for JSON-structured inference (e.g. contract inference)
    """

    def __init__(self, config: Optional[LLMClientConfig] = None) -> None:
        """
        Initialize the OpenAI client.

        :param config: Optional :class:`LLMClientConfig`. Defaults are used if
                       not provided.
        :raises RuntimeError: If ``OPENAI_API_KEY`` is not set or the OpenAI
                              SDK is not installed.
        """
        self._config = config or LLMClientConfig()

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set in the environment.")

        try:
            from openai import OpenAI  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "OpenAI SDK is not installed. Add 'openai' to requirements.txt."
            ) from exc

        self._client = OpenAI(api_key=api_key)

    def complete(self, prompt: str) -> str:
        """
        Call the model with a plain text prompt and return the raw text response.

        Use this method when the caller expects free-form text output rather than
        structured JSON — for example, in LLM-based segmentation where the model
        returns annotated Markdown prose.

        :param prompt: Full prompt string sent as the user message.
        :return: Raw text response from the model.
        """
        logger.info("Calling OpenAI for text completion (%s).", self._config.model)
        logger.debug("Prompt length: %d chars", len(prompt))

        resp = self._client.responses.create(
            model=self._config.model,
            input=[{"role": "user", "content": prompt}],
        )

        text = self._extract_text(resp)
        logger.debug("Raw model output: %s", text[:500])
        return text

    def infer_json(self, *, user_prompt: str) -> Dict[str, Any]:
        """
        Call the model and return parsed JSON.

        The system prompt instructs the model to output only valid JSON.

        :param user_prompt: Prompt content for the module.
        :return: Parsed JSON dict.
        :raises ValueError: If the model output is not valid JSON.
        """
        logger.info("Calling OpenAI for inference (%s).", self._config.model)
        logger.debug("Prompt length: %d chars", len(user_prompt))

        # Responses API: https://platform.openai.com/docs/api-reference/responses
        resp = self._client.responses.create(
            model=self._config.model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        text = self._extract_text(resp)
        logger.debug("Raw model output: %s", text[:500])

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Model did not return valid JSON. Output was: {text[:3000]}"
            ) from exc

    @staticmethod
    def _extract_text(resp: Any) -> str:
        """
        Extract the concatenated output text from an OpenAI Responses API response.

        The SDK shape can vary across versions; this method defensively walks
        ``resp.output[*].content[*]`` and collects all ``output_text`` chunks.

        :param resp: Raw response object from the Responses API.
        :return: Stripped text string.
        """
        text = ""
        for item in getattr(resp, "output", []) or []:
            for chunk in getattr(item, "content", []) or []:
                if getattr(chunk, "type", None) == "output_text":
                    text += getattr(chunk, "text", "")
        return text.strip()
