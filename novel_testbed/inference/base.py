"""
Inference interfaces for generating narrative contracts automatically.

The inference layer converts parsed Modules into ModuleContracts that
include inferred ReaderState and module intent (expected_changes).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Sequence

from novel_testbed.models import Module, ModuleContract


class ContractInferencer(ABC):
    """
    Strategy interface for contract inference.

    Implementations may use:
    - LLM inference (OpenAI API)
    - deterministic NLP features (NLTK/spaCy + rules)
    - hybrid approaches
    """

    @abstractmethod
    def infer(self, modules: Sequence[Module], *, novel_title: str) -> List[ModuleContract]:
        """
        Infer a full contract for a set of modules.

        :param modules: Parsed modules from a Novel.
        :param novel_title: Novel title for context.
        :return: Fully populated list of ModuleContract objects.
        """
        raise NotImplementedError