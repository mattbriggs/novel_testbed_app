"""
End-to-end integration test for the Novel Testbed pipeline.

This test verifies that:
Markdown -> Parse -> Contract -> YAML -> Load -> Assess -> JSON
functions as a single coherent system.
"""

import json
from pathlib import Path

import yaml

from novel_testbed.parser.commonmark import CommonMarkNovelParser
from novel_testbed.contracts.contract import (
    contract_from_novel,
    dump_contract_yaml,
    load_contract_yaml,
)
from novel_testbed.contracts.assessor import assess_contract, report_to_json
from novel_testbed.models import ReaderState


def test_full_pipeline_execution(tmp_path: Path):
    # 1. Input: minimal novel
    markdown = """
# Chapter One
## Scene Arrival
She stepped onto the sand.
"""

    # 2. Parse
    parser = CommonMarkNovelParser()
    novel = parser.parse(markdown, title="Pipeline Test")
    assert len(novel.modules) == 1

    # 3. Build contract
    contracts = contract_from_novel(novel)
    assert len(contracts) == 1

    # 4. Author fills contract
    c = contracts[0]
    c.expected_changes = ["threat escalation"]
    c.pre_state = ReaderState(genre="survival", threat_level=0.1)
    c.post_state = ReaderState(genre="survival", threat_level=0.4)

    # 5. Serialize contract to YAML
    yaml_text = dump_contract_yaml(contracts)
    yaml_data = yaml.safe_load(yaml_text)
    assert "modules" in yaml_data

    # 6. Reload contract from YAML
    loaded_contracts = load_contract_yaml(yaml_text)
    assert len(loaded_contracts) == 1

    # 7. Assess
    reports = assess_contract(loaded_contracts)
    assert len(reports) == 1
    assert reports[0].severity == "PASS"

    # 8. Serialize report to JSON
    json_text = report_to_json(reports)
    json_data = json.loads(json_text)

    assert isinstance(json_data, list)
    assert json_data[0]["severity"] == "PASS"