"""
Markdown segmentation utilities.

This module is responsible for discovering and inserting structural
boundaries into raw prose Markdown so that downstream parsers can operate.

This is the first phase of the narrative compiler::

    segment → parse → infer → assess

The base :class:`ModuleSegmenter` is deterministic and conservative.
It guarantees:

- A top-level chapter header
- At least one module header
- Correct chapter → module ordering
- Idempotency when input is already well-formed

:class:`LLMSegmenter` extends this with optional LLM-based semantic
segmentation. It depends on
:class:`~novel_testbed.inference.llm_client.OpenAILLMClient` for the API
call but does **not** depend on the inference layer's contract logic.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class ModuleSegmenter:
    """
    Deterministic Markdown segmenter.

    Guarantees a structurally valid document:

    - One top-level chapter heading: ``# Title``
    - At least one module heading: ``## Scene ...``
    - Chapter must appear before any module
    - Idempotent for already-correct Markdown
    """

    _chapter_re = re.compile(r"^#\s+.+", re.MULTILINE)
    _module_re = re.compile(r"^##\s+.+", re.MULTILINE)

    def segment_markdown(self, text: str, title: str) -> str:
        """
        Segment raw Markdown into structurally annotated Markdown.

        Structural invariants enforced:

        - Chapter must come before any module
        - At least one chapter exists
        - At least one module exists

        :param text: Raw or partially annotated Markdown.
        :param title: Novel title used for synthetic chapter heading.
        :return: Valid annotated Markdown ending with a trailing newline.
        """
        logger.debug("Starting deterministic segmentation for '%s'", title)

        text = text.strip()
        lines = text.splitlines()

        chapter_match = self._chapter_re.search(text)
        module_match = self._module_re.search(text)

        has_chapter = chapter_match is not None
        has_module = module_match is not None

        # Detect inversion: module appears before chapter
        inverted = (
            has_chapter
            and has_module
            and module_match.start() < chapter_match.start()
        )

        if has_chapter and has_module and not inverted:
            logger.info("Markdown already correctly segmented; returning unchanged.")
            return text + "\n"

        logger.info("Markdown is missing or has invalid structure; rebuilding.")

        body_lines = [
            line for line in lines if not line.strip().startswith("#")
        ]

        output = []

        # Enforce chapter
        chapter_title = title or "Untitled"
        output.append(f"# {chapter_title}")
        output.append("")

        # Enforce at least one module
        output.append("## Scene 1")
        output.append("")

        output.extend(body_lines)

        segmented = "\n".join(output).strip() + "\n"

        logger.debug(
            "Segmentation complete. Chapter inserted: %s | %d chars.",
            chapter_title,
            len(segmented),
        )
        return segmented


class LLMSegmenter(ModuleSegmenter):
    """
    LLM-powered semantic segmenter.

    Uses an object with a ``complete(prompt: str) -> str`` interface —
    typically :class:`~novel_testbed.inference.llm_client.OpenAILLMClient` —
    to insert:

    - Chapter titles
    - Scene boundaries
    - Exposition blocks
    - Transition modules

    This replaces naive segmentation with semantic awareness. The LLM returns
    plain annotated Markdown (not JSON), so the ``complete`` method is used
    rather than ``infer_json``.

    If no client is supplied, a default
    :class:`~novel_testbed.inference.llm_client.OpenAILLMClient` is constructed
    automatically (requires ``OPENAI_API_KEY`` in the environment).
    """

    def __init__(self, client: Optional[object] = None) -> None:
        """
        Initialize the LLM segmenter.

        :param client: An object with a ``complete(prompt: str) -> str`` method.
                       If ``None``, a default
                       :class:`~novel_testbed.inference.llm_client.OpenAILLMClient`
                       is created automatically.
        :raises RuntimeError: If ``client`` is ``None`` and ``OPENAI_API_KEY``
                              is not set in the environment.
        """
        if client is None:
            logger.debug("Creating default OpenAILLMClient for LLMSegmenter.")
            # Local import keeps the segmentation layer independent of the
            # inference layer at module load time.
            from novel_testbed.inference.llm_client import OpenAILLMClient
            client = OpenAILLMClient()

        self._client = client

    def segment_markdown(self, text: str, title: str) -> str:
        """
        Use an LLM to infer module boundaries and return fully annotated Markdown.

        Sends a structured prompt requesting ``# Chapter`` and ``## Scene /
        Exposition / Transition`` headers be inserted at semantically appropriate
        locations.

        :param text: Raw Markdown prose.
        :param title: Novel title.
        :return: Structurally valid annotated Markdown ending with a trailing
                 newline.
        """
        logger.info("Starting LLM-based segmentation for '%s'", title)

        prompt = (
            "You are a narrative segmentation engine.\n"
            "Rewrite the following Markdown so that:\n"
            "1. A '# Chapter Title' appears before any modules.\n"
            "2. Each narrative unit starts with one of:\n"
            "   - '## Scene ...'\n"
            "   - '## Exposition ...'\n"
            "   - '## Transition ...'\n"
            "3. Ordering is strictly:\n"
            "   Chapter → Module → Content\n\n"
            "Return only valid Markdown.\n\n"
            f"TITLE: {title}\n\n"
            f"TEXT:\n{text}"
        )

        logger.debug("Sending segmentation prompt to LLM (%d chars).", len(prompt))

        response = self._client.complete(prompt)

        segmented = response.strip() + "\n"

        logger.info("LLM segmentation complete (%d characters).", len(segmented))
        return segmented
