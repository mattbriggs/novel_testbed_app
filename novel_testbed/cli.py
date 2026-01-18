"""
Command-line interface for the Novel Testbed.

This module provides four commands:

- segment:
    Segment raw Markdown into annotated Markdown with structural boundaries.

- parse:
    Parse annotated Markdown and generate a blank contract YAML.

- infer:
    Segment (if needed), parse, infer a full narrative contract using an
    LLM-backed inferencer, and write:
        - YAML contract
        - optional annotated Markdown

- assess:
    Assess a filled contract YAML and emit a JSON report.

The CLI remains intentionally thin. All domain logic lives elsewhere.
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
from pathlib import Path
from typing import List, Optional

from novel_testbed.contracts.assessor import assess_contract, report_to_json
from novel_testbed.contracts.contract import (
    contract_from_novel,
    dump_contract_yaml,
    load_contract_yaml,
)
from novel_testbed.inference.auto_contract import infer_contract_from_markdown
from novel_testbed.inference.llm_client import LLMClientConfig, OpenAILLMClient
from novel_testbed.inference.llm_inferencer import OpenAIContractInferencer
from novel_testbed.logging_config import configure_logging
from novel_testbed.parser.commonmark import CommonMarkNovelParser
from novel_testbed.segmentation.segmenter import ModuleSegmenter, LLMSegmenter
from novel_testbed.utils.source_fingerprint import build_source_metadata

logger = logging.getLogger(__name__)


def _require_openai_key() -> None:
    """
    Ensure that the OpenAI API key is available in the environment.
    """
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY is not set in the environment.")
        raise SystemExit(
            "ERROR: OPENAI_API_KEY is not set.\n\n"
            "Set your API key using:\n\n"
            "  export OPENAI_API_KEY=\"sk-...\"\n\n"
            "The API key must not be stored in the repository or passed as a CLI argument."
        )


# -------------------------------------------------------------------------
# segment command
# -------------------------------------------------------------------------


def _cmd_segment(args: argparse.Namespace) -> int:
    """
    Handle the `segment` subcommand.

    Takes raw Markdown and produces annotated Markdown with:
    - Chapter headings
    - Scene / Exposition / Transition modules
    """
    logger.info("Running segment command on %s", args.input)

    input_path = Path(args.input)
    output_path = Path(args.output)

    text = input_path.read_text(encoding="utf-8")

    if args.llm:
        _require_openai_key()
        logger.info("Using LLM-backed segmenter.")
        segmenter = LLMSegmenter()
    else:
        logger.info("Using deterministic segmenter.")
        segmenter = ModuleSegmenter()

    annotated = segmenter.segment_markdown(text, title=args.title or input_path.stem)
    output_path.write_text(annotated, encoding="utf-8")

    logger.info("Annotated Markdown written to %s", output_path)
    return 0


# -------------------------------------------------------------------------
# parse command
# -------------------------------------------------------------------------


def _cmd_parse(args: argparse.Namespace) -> int:
    """
    Handle the `parse` subcommand.

    Reads annotated Markdown, parses it into modules, and writes a blank
    narrative contract YAML file with provenance metadata.
    """
    logger.info("Running parse command on %s", args.input)

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    copied_source_path = output_dir / "source.md"
    try:
        shutil.copy2(input_path, copied_source_path)
        logger.info("Copied source Markdown to %s", copied_source_path)
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to copy source Markdown: %s", exc)

    text = input_path.read_text(encoding="utf-8")

    parser = CommonMarkNovelParser()
    novel = parser.parse(text, title=args.title or input_path.stem)

    contracts = contract_from_novel(novel)

    try:
        source_meta = build_source_metadata(
            original_path=input_path,
            copied_path=copied_source_path,
            text=text,
        )
        logger.debug("Source fingerprint computed (sha256=%s...)", source_meta["sha256"][:12])
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to build source metadata: %s", exc)
        source_meta = {}

    yaml_text = dump_contract_yaml(contracts, source=source_meta)
    output_path.write_text(yaml_text, encoding="utf-8")

    logger.info("Blank contract YAML written to %s", output_path)
    return 0


# -------------------------------------------------------------------------
# infer command (full compiler pipeline)
# -------------------------------------------------------------------------


def _cmd_infer(args: argparse.Namespace) -> int:
    """
    Handle the `infer` subcommand.

    Pipeline:
        1. Segment Markdown (deterministic or LLM)
        2. Parse annotated Markdown
        3. Infer narrative contract
        4. Write YAML contract
        5. Optionally write annotated Markdown
    """
    logger.info("Running infer command on %s", args.input)
    _require_openai_key()

    input_path = Path(args.input)
    markdown_text = input_path.read_text(encoding="utf-8")
    title = args.title or input_path.stem

    # --- Segmentation phase ---
    if args.segment_llm:
        logger.info("Segmenting using LLM.")
        segmenter = LLMSegmenter()
    else:
        logger.info("Segmenting using deterministic segmenter.")
        segmenter = ModuleSegmenter()

    annotated = segmenter.segment_markdown(markdown_text, title=title)

    if args.annotated:
        annotated_path = Path(args.annotated)
        annotated_path.write_text(annotated, encoding="utf-8")
        logger.info("Annotated Markdown written to %s", annotated_path)

    # --- Inference phase ---
    logger.debug("Initializing OpenAI LLM client with model=%s", args.model)
    client_config = LLMClientConfig(model=args.model)
    client = OpenAILLMClient(config=client_config)
    inferencer = OpenAIContractInferencer(client=client)

    logger.info("Inferring narrative contract for '%s'", title)
    contracts = infer_contract_from_markdown(
        annotated,
        title=title,
        inferencer=inferencer,
    )

    yaml_text = dump_contract_yaml(contracts)
    Path(args.output).write_text(yaml_text, encoding="utf-8")

    logger.info("Inferred contract YAML written to %s", args.output)
    return 0


# -------------------------------------------------------------------------
# assess command
# -------------------------------------------------------------------------


def _cmd_assess(args: argparse.Namespace) -> int:
    """
    Handle the `assess` subcommand.
    """
    logger.info("Running assess command on %s", args.contract)

    yaml_text = Path(args.contract).read_text(encoding="utf-8")
    contracts = load_contract_yaml(yaml_text)

    reports = assess_contract(contracts)
    json_text = report_to_json(reports)

    Path(args.output).write_text(json_text, encoding="utf-8")

    logger.info("Assessment report written to %s", args.output)
    return 0


# -------------------------------------------------------------------------
# argument parser
# -------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    """
    Build the top-level argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="novel-testbed",
        description="Narrative compiler for fiction",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR).",
    )

    subparsers = parser.add_subparsers(dest="cmd", required=True)

    # ---- segment ----
    seg_cmd = subparsers.add_parser("segment", help="Segment Markdown into annotated Markdown")
    seg_cmd.add_argument("input", help="Path to raw Markdown file")
    seg_cmd.add_argument("-o", "--output", required=True, help="Path to annotated Markdown")
    seg_cmd.add_argument("--title", default=None, help="Optional novel title")
    seg_cmd.add_argument("--llm", action="store_true", help="Use LLM-backed segmentation")
    seg_cmd.set_defaults(func=_cmd_segment)

    # ---- parse ----
    parse_cmd = subparsers.add_parser("parse", help="Parse annotated Markdown to blank contract YAML")
    parse_cmd.add_argument("input", help="Path to annotated Markdown")
    parse_cmd.add_argument("-o", "--output", required=True, help="Path to output YAML")
    parse_cmd.add_argument("--title", default=None, help="Optional novel title")
    parse_cmd.set_defaults(func=_cmd_parse)

    # ---- infer ----
    infer_cmd = subparsers.add_parser("infer", help="Full pipeline: segment → parse → infer")
    infer_cmd.add_argument("input", help="Path to raw Markdown")
    infer_cmd.add_argument("-o", "--output", required=True, help="Path to output YAML")
    infer_cmd.add_argument("--annotated", help="Optional path to write annotated Markdown")
    infer_cmd.add_argument("--segment-llm", action="store_true", help="Use LLM for segmentation")
    infer_cmd.add_argument("--title", default=None, help="Optional novel title")
    infer_cmd.add_argument("--model", default="gpt-4.1-mini", help="OpenAI model for inference")
    infer_cmd.set_defaults(func=_cmd_infer)

    # ---- assess ----
    assess_cmd = subparsers.add_parser("assess", help="Assess a contract YAML")
    assess_cmd.add_argument("contract", help="Path to YAML contract")
    assess_cmd.add_argument("-o", "--output", required=True, help="Path to JSON report")
    assess_cmd.set_defaults(func=_cmd_assess)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """
    Entry point for the CLI.
    """
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    level = getattr(logging, str(args.log_level).upper(), logging.INFO)
    configure_logging(level)

    logger.debug("Dispatching command: %s", args.cmd)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())