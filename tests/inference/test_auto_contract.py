"""
Integration-ish test: Markdown -> parse -> infer -> contracts (with stub inferencer).
"""

from dataclasses import dataclass
from typing import List, Sequence

from novel_testbed.inference.auto_contract import infer_contract_from_markdown
from novel_testbed.inference.base import ContractInferencer
from novel_testbed.models import Module, ModuleContract, ReaderState


@dataclass
class StubInferencer(ContractInferencer):
    def infer(self, modules: Sequence[Module], *, novel_title: str) -> List[ModuleContract]:
        return [
            ModuleContract(
                module_id=m.id,
                module_title=m.title,
                chapter=m.chapter,
                module_type=m.module_type.value,
                pre_state=ReaderState(),
                post_state=ReaderState(genre="survival"),
                expected_changes=["stub intent"],
                anchors={"start": m.start_text, "end": m.end_text},
            )
            for m in modules
        ]


def test_infer_contract_from_markdown_produces_contracts():
    md = """# Chapter One

## Scene Arrival
She stepped onto the sand.
"""

    contracts = infer_contract_from_markdown(
        md,
        title="Auto Contract Test",
        inferencer=StubInferencer(),
    )

    assert len(contracts) == 1
    assert contracts[0].module_id == "M001"
    assert contracts[0].expected_changes == ["stub intent"]
    assert contracts[0].post_state.genre == "survival"