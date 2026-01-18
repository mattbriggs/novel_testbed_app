"""
High-level helpers to infer a narrative contract from *annotated* Markdown.
"""

from __future__ import annotations

import logging
from typing import List

from novel_testbed.inference.base import ContractInferencer
from novel_testbed.models import ModuleContract
from novel_testbed.parser.commonmark import CommonMarkNovelParser

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.propagate = True


def infer_contract_from_markdown(
    markdown_text: str,
    *,
    title: str,
    inferencer: ContractInferencer,
) -> List[ModuleContract]:
    """
    Infer a complete narrative contract from *annotated* Markdown.

    Pipeline:
        Annotated Markdown → Parse → Infer
    """
    logger.info("Starting inference pipeline for novel '%s'.", title)

    # ------------------------------------------------------------------
    # 1. Parsing
    # ------------------------------------------------------------------
    logger.debug("Parsing annotated Markdown into structural modules.")
    parser = CommonMarkNovelParser()
    novel = parser.parse(markdown_text, title=title)

    if not novel.modules:
        message = (
            "No modules were parsed from the input Markdown. "
            "This usually indicates missing or malformed chapter/module headers."
        )
        logger.warning(message)
        return []

    logger.info(
        "Parsed novel '%s' with %d modules.",
        novel.title,
        len(novel.modules),
    )

    # ------------------------------------------------------------------
    # 2. Inference
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

    return contracts