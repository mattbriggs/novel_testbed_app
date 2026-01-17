"""
Novel Testbed

A narrative analysis and validation framework that treats fiction as
a testable, contract-driven system.

Public API layers:

- Parsing:
    Convert Markdown into structured fiction modules.

- Contract generation:
    Build blank or inferred narrative contracts.

- Inference:
    Automatically populate contracts using LLM or NLP backends.

- Assessment:
    Evaluate contracts against narrative rules.
"""

from __future__ import annotations

# ---- Parsing ----
from novel_testbed.parser.commonmark import CommonMarkNovelParser
from novel_testbed.parser.base import NovelParser

# ---- Contracts ----
from novel_testbed.contracts.contract import (
    contract_from_novel,
    dump_contract_yaml,
    load_contract_yaml,
)
from novel_testbed.contracts.assessor import assess_contract

# ---- Inference (Semantic Front-End) ----
from novel_testbed.inference.base import ContractInferencer
from novel_testbed.inference.auto_contract import infer_contract_from_markdown
from novel_testbed.inference.llm_client import OpenAILLMClient, LLMClientConfig
from novel_testbed.inference.llm_inferencer import OpenAIContractInferencer

# ---- Core Models ----
from novel_testbed.models import (
    Novel,
    Module,
    ModuleType,
    ModuleContract,
    ReaderState,
)

__all__ = [
    # Parsing
    "CommonMarkNovelParser",
    "NovelParser",

    # Contract generation
    "contract_from_novel",
    "dump_contract_yaml",
    "load_contract_yaml",

    # Assessment
    "assess_contract",

    # Inference
    "ContractInferencer",
    "infer_contract_from_markdown",
    "OpenAILLMClient",
    "LLMClientConfig",
    "OpenAIContractInferencer",

    # Models
    "Novel",
    "Module",
    "ModuleType",
    "ModuleContract",
    "ReaderState",
]