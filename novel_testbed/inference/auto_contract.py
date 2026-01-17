"""
High-level helpers to infer a contract directly from Markdown.
"""

from __future__ import annotations

import logging
from typing import List

from novel_testbed.inference.base import ContractInferencer
from novel_testbed.models import ModuleContract
from novel_testbed.parser.commonmark import CommonMarkNovelParser

logger = logging.getLogger(__name__)


def infer_contract_from_markdown(
    markdown_text: str,
    *,
    title: str,
    inferencer: ContractInferencer,
) -> List[ModuleContract]:
    """
    Parse Markdown and infer a complete contract.

    :param markdown_text: Raw Markdown novel.
    :param title: Novel title.
    :param inferencer: Contract inferencer strategy.
    :return: Inferred ModuleContract list.
    """
    logger.info("Inferring contract from Markdown for '%s'.", title)

    parser = CommonMarkNovelParser()
    novel = parser.parse(markdown_text, title=title)

    return inferencer.infer(novel.modules, novel_title=novel.title)