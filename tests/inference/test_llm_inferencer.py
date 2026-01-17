"""
Tests for OpenAIContractInferencer using a stubbed LLM client.
"""

from dataclasses import dataclass
from typing import Any, Dict, List

from novel_testbed.inference.llm_inferencer import OpenAIContractInferencer
from novel_testbed.models import Module, ModuleType


@dataclass
class StubClient:
    outputs: List[Dict[str, Any]]
    i: int = 0

    def infer_json(self, *, user_prompt: str) -> Dict[str, Any]:
        out = self.outputs[self.i]
        self.i += 1
        return out


def test_inferencer_builds_contracts_and_chains_state():
    modules = [
        Module(
            id="M001",
            chapter="Ch1",
            title="Scene One",
            module_type=ModuleType.SCENE,
            start_line=1,
            end_line=5,
            text="A calm beginning.",
            start_text="A calm beginning.",
            end_text="A calm beginning.",
        ),
        Module(
            id="M002",
            chapter="Ch1",
            title="Scene Two",
            module_type=ModuleType.SCENE,
            start_line=6,
            end_line=10,
            text="Threat arrives.",
            start_text="Threat arrives.",
            end_text="Threat arrives.",
        ),
    ]

    stub = StubClient(
        outputs=[
            {
                "expected_changes": ["establish baseline calm"],
                "post_state": {
                    "genre": "survival",
                    "power_balance": "environment",
                    "emotional_tone": "controlled",
                    "dominant_fantasy_id": None,
                    "threat_level": 0.1,
                    "agency_level": 0.8,
                },
                "confidence": 0.8,
                "notes": {},
            },
            {
                "expected_changes": ["escalate threat"],
                "post_state": {
                    "genre": "survival",
                    "power_balance": "environment",
                    "emotional_tone": "unease",
                    "dominant_fantasy_id": "UF_JUSTICE_EXPOSED_01",
                    "threat_level": 0.6,
                    "agency_level": 0.6,
                },
                "confidence": 0.75,
                "notes": {},
            },
        ]
    )

    inferencer = OpenAIContractInferencer(client=stub)  # type: ignore[arg-type]
    contracts = inferencer.infer(modules, novel_title="Test Novel")

    assert len(contracts) == 2

    # module 1 pre_state default
    assert contracts[0].pre_state.genre is None
    assert contracts[0].post_state.genre == "survival"

    # module 2 pre_state chained from module 1 post_state
    assert contracts[1].pre_state.threat_level == 0.1
    assert contracts[1].post_state.threat_level == 0.6
    assert contracts[1].expected_changes == ["escalate threat"]
    assert contracts[1].fantasy_id == "UF_JUSTICE_EXPOSED_01"