"""
High-level helpers to infer a narrative contract directly from Markdown.

This module defines the semantic front-end of the system. It coordinates:

    Markdown → Segmentation → Parsing → Inference

It deliberately contains *no business logic*. Its job is orchestration:
each stage delegates to a single-responsibility component.

Pipeline:

1. Segment raw prose into structured Markdown (chapter / scene markers).
2. Parse structured Markdown into Module objects.
3. Infer ModuleContract objects from modules using an inference strategy.

This keeps structure, meaning, and orchestration cleanly separated.
"""

from __future__ import annotations

import logging
from typing import List

from novel_testbed.inference.base import ContractInferencer
from novel_testbed.models import ModuleContract
from novel_testbed.parser.commonmark import CommonMarkNovelParser
from novel_testbed.segmentation.segmenter import ModuleSegmenter

logger = logging.getLogger(__name__)


def infer_contract_from_markdown(
    markdown_text: str,
    *,
    title: str,
    inferencer: ContractInferencer,
    segmenter: ModuleSegmenter | None = None,
    return_annotated_markdown: bool = False,
) -> List[ModuleContract] | tuple[List[ModuleContract], str]:
    """
    Infer a complete narrative contract from Markdown text.

    This function represents the canonical pipeline:

        Markdown → Segment → Parse → Infer

    Segmentation is performed first to ensure the input contains explicit
    chapter and module markers. Parsing and inference operate only on
    annotated Markdown.

    :param markdown_text:
        Raw or annotated Markdown text representing a novel.
    :param title:
        Title of the novel (used for chapter creation if missing).
    :param inferencer:
        Strategy object responsible for producing ModuleContract objects.
    :param segmenter:
        Optional ModuleSegmenter implementation. If None, a default
        ModuleSegmenter is constructed.
    :param return_annotated_markdown:
        If True, return a tuple of (contracts, annotated_markdown).
        This supports CLI workflows that persist the segmented Markdown.
    :return:
        Either:
            - List[ModuleContract]
        or:
            - (List[ModuleContract], annotated_markdown)
    """
    logger.info("Starting inference pipeline for novel '%s'.", title)

    # ------------------------------------------------------------------
    # 1. Segmentation
    # ------------------------------------------------------------------
    if segmenter is None:
        segmenter = ModuleSegmenter()
        logger.debug("No segmenter provided; using default ModuleSegmenter.")

    logger.debug("Segmenting Markdown input.")
    annotated_markdown = segmenter.segment_markdown(markdown_text, title=title)

    # ------------------------------------------------------------------
    # 2. Parsing
    # ------------------------------------------------------------------
    logger.debug("Parsing annotated Markdown into structural modules.")
    parser = CommonMarkNovelParser()
    novel = parser.parse(annotated_markdown, title=title)

    logger.info(
        "Parsed novel '%s' with %d modules.",
        novel.title,
        len(novel.modules),
    )

    # ------------------------------------------------------------------
    # 3. Inference
    # ------------------------------------------------------------------
    logger.debug("Running contract inferencer on %d modules.", len(novel.modules))
    contracts = inferencer.infer(
        novel.modules,
        novel_title=novel.title,
    )

    logger.info(
        "Inference complete. Generated %d ModuleContract objects.",
        len(contracts),
    )

    # ------------------------------------------------------------------
    # Optional: return annotated Markdown for persistence
    # ------------------------------------------------------------------
    if return_annotated_markdown:
        return contracts, annotated_markdown

    return contracts