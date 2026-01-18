"""
Markdown segmentation utilities.

This module is responsible for discovering and inserting structural
boundaries into raw prose Markdown so that downstream parsers can operate.

This is the first phase of the narrative compiler:

    segment → parse → infer → assess

The base ModuleSegmenter is deterministic and conservative. It guarantees:
- A top-level chapter header
- At least one module header
- Idempotency when input is already annotated

The LLMSegmenter extends this with semantic segmentation using an LLM.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

from novel_testbed.inference.llm_client import OpenAILLMClient
from novel_testbed.inference.llm_inferencer import OpenAIContractInferencer

logger = logging.getLogger(__name__)


class ModuleSegmenter:
    """
    Deterministic Markdown segmenter.

    Inserts minimal structural markup when missing:
    - A single chapter heading
    - One Scene module wrapping the entire text

    If the text already contains module headings, it is returned unchanged.
    """

    _chapter_re = re.compile(r"^#\s+.+", re.MULTILINE)
    _module_re = re.compile(r"^##\s+.+", re.MULTILINE)

    def segment_markdown(self, text: str, title: str) -> str:
        """
        Segment raw Markdown into structurally annotated Markdown.

        This guarantees:
        - A top-level ``#`` chapter heading
        - At least one ``## Scene`` module

        If segmentation is already present, input is returned unchanged.

        :param text: Raw Markdown prose.
        :param title: Novel title used for synthetic chapter heading.
        :return: Annotated Markdown.
        """
        logger.debug("Starting deterministic segmentation for '%s'", title)

        has_chapter = bool(self._chapter_re.search(text))
        has_module = bool(self._module_re.search(text))

        if has_chapter and has_module:
            logger.info("Markdown already segmented; returning unchanged.")
            return text

        logger.info("Markdown not segmented; applying minimal structural markup.")

        lines = text.strip().splitlines()

        output = []

        # Ensure chapter
        if not has_chapter:
            chapter_title = title or "Untitled"
            output.append(f"# {chapter_title}")
            output.append("")

        # Ensure at least one module
        output.append("## Scene 1")
        output.append("")

        output.extend(lines)

        segmented = "\n".join(output).strip() + "\n"

        logger.debug("Segmentation complete (%d characters).", len(segmented))
        return segmented


class LLMSegmenter(ModuleSegmenter):
    """
    LLM-powered semantic segmenter.

    Uses an OpenAI-backed inferencer to classify and insert:
    - Scene
    - Exposition
    - Transition

    headings based on narrative flow.

    This is the narrative equivalent of a real lexer/parser front-end.
    """

    def __init__(
        self,
        inferencer: Optional[OpenAIContractInferencer] = None,
    ) -> None:
        """
        Initialize the LLM-backed segmenter.

        :param inferencer: Optional preconfigured inferencer instance.
        """
        if inferencer is None:
            logger.debug("Creating default OpenAI inferencer for LLMSegmenter.")
            client = OpenAILLMClient()
            inferencer = OpenAIContractInferencer(client=client)

        self.inferencer = inferencer

    def segment_markdown(self, text: str, title: str) -> str:
        """
        Use an LLM to infer module boundaries and return fully annotated Markdown.

        :param text: Raw Markdown prose.
        :param title: Novel title.
        :return: Annotated Markdown with semantic modules.
        """
        logger.info("Starting LLM-based segmentation for '%s'", title)

        prompt = (
            "You are a narrative segmentation engine.\n"
            "Rewrite the following Markdown by inserting:\n"
            "- '# Chapter Title'\n"
            "- '## Scene ...'\n"
            "- '## Exposition ...'\n"
            "- '## Transition ...'\n"
            "where appropriate.\n\n"
            "Return only valid Markdown.\n\n"
            f"TITLE: {title}\n\n"
            f"TEXT:\n{text}"
        )

        logger.debug("Sending segmentation prompt to LLM (%d chars).", len(prompt))

        response = self.inferencer.client.complete(prompt)

        segmented = response.strip() + "\n"

        logger.info("LLM segmentation complete (%d characters).", len(segmented))
        return segmented