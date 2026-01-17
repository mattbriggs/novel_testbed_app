"""
Abstract parser interface for novel ingestion.

All novel parsers must implement the NovelParser strategy. A parser
takes raw text and converts it into a structured Novel object that
can be consumed by the contract system.

This layer isolates file format concerns from narrative logic.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from novel_testbed.models import Novel

logger = logging.getLogger(__name__)


class NovelParser(ABC):
    """
    Strategy interface for novel parsers.

    Implementations of this class define how raw text is converted into a
    structured Novel model. Different parsers can be created for:

    - CommonMark Markdown
    - HTML
    - Scrivener exports
    - Plain text

    without changing the rest of the system.
    """

    @abstractmethod
    def parse(self, text: str, *, title: str) -> Novel:
        """
        Parse raw novel text into a Novel object.

        :param text: Raw novel content.
        :param title: Title of the novel.
        :return: Parsed Novel instance.
        """
        logger.debug(
            "NovelParser.parse called with title='%s' and %d characters.",
            title,
            len(text),
        )
        raise NotImplementedError