"""
End-to-end integration test for the Novel Testbed pipeline.

This test verifies that:

Raw Markdown
→ Segmentation
→ Parsing
→ Contract generation
→ YAML serialization
→ YAML loading
→ Assessment
→ JSON serialization

functions as a single coherent system.
"""

import json
from pathlib import Path

import yaml

from novel_testbed.segmentation.segmenter import ModuleSegmenter
from novel_testbed.parser.commonmark import CommonMarkNovelParser
from novel_testbed.contracts.contract import (
    contract_from_novel,
    dump_contract_yaml,
    load_contract_yaml,
)
from novel_testbed.contracts.assessor import assess_contract, report_to_json
from novel_testbed.models import ReaderState


def test_full_pipeline_execution(tmp_path: Path):
    # 1. Raw input: unstructured prose Markdown
    raw_markdown = """
She stepped onto the sand. The wind cut against her face.
"""

    # 2. Segment
    segmenter = ModuleSegmenter()
    annotated_markdown = segmenter.segment_markdown(
        raw_markdown,
        title="Pipeline Test",
    )

    assert "# Pipeline Test" in annotated_markdown
    assert "##" in annotated_markdown  # Must contain module boundaries

    # 3. Parse annotated Markdown
    parser = CommonMarkNovelParser()
    novel = parser.parse(annotated_markdown, title="Pipeline Test")
    assert len(novel.modules) == 1

    # 4. Build contract
    contracts = contract_from_novel(novel)
    assert len(contracts) == 1

    # 5. Author fills contract
    c = contracts[0]
    c.expected_changes = ["threat escalation"]
    c.pre_state = ReaderState(genre="survival", threat_level=0.1)
    c.post_state = ReaderState(genre="survival", threat_level=0.4)

    # 6. Serialize contract to YAML
    yaml_text = dump_contract_yaml(contracts)
    yaml_data = yaml.safe_load(yaml_text)
    assert "modules" in yaml_data

    # 7. Reload contract from YAML
    loaded_contracts = load_contract_yaml(yaml_text)
    assert len(loaded_contracts) == 1

    # 8. Assess
    reports = assess_contract(loaded_contracts)
    assert len(reports) == 1
    assert reports[0].severity == "PASS"

    # 9. Serialize report to JSON
    json_text = report_to_json(reports)
    json_data = json.loads(json_text)

    assert isinstance(json_data, list)
    assert json_data[0]["severity"] == "PASS"