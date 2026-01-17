"""
OpenAI LLM client adapter for contract inference.

This module isolates API integration so the rest of the codebase
does not depend on OpenAI SDK details.
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

    Requires OPENAI_API_KEY to be set in the environment.
    """

    def __init__(self, config: Optional[LLMClientConfig] = None) -> None:
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

    def infer_json(self, *, user_prompt: str) -> Dict[str, Any]:
        """
        Call the model and return parsed JSON.

        :param user_prompt: Prompt content for the module.
        :return: Parsed JSON dict.
        :raises ValueError: if output is not valid JSON.
        """
        logger.info("Calling OpenAI for inference (%s).", self._config.model)
        logger.debug("Prompt length: %d chars", len(user_prompt))

        # Responses API: https://platform.openai.com/docs/api-reference/responses  [oai_citation:1‡OpenAI Platform](https://platform.openai.com/docs/api-reference/responses?utm_source=chatgpt.com)
        resp = self._client.responses.create(
            model=self._config.model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        # SDK shapes can vary; safest is to extract text from output entries.
        text = ""
        for item in getattr(resp, "output", []) or []:
            for chunk in getattr(item, "content", []) or []:
                if getattr(chunk, "type", None) == "output_text":
                    text += getattr(chunk, "text", "")

        text = text.strip()
        logger.debug("Raw model output: %s", text[:500])

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Model did not return valid JSON. Output was: {text[:3000]}") from exc