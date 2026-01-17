"""
Command-line interface for the Novel Testbed.

This module provides three commands:

- parse:
    Parse a Markdown novel and generate a blank contract YAML.

- infer:
    Parse a Markdown novel, infer a full narrative contract using an
    LLM-backed inferencer, and write the populated contract YAML.

- assess:
    Assess a filled contract YAML and emit a JSON report.

The CLI is intentionally thin. All real logic lives in the domain modules.
"""

from __future__ import annotations

import argparse
import logging
import os
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

logger = logging.getLogger(__name__)


def _require_openai_key() -> None:
    """
    Ensure that the OpenAI API key is available in the environment.

    The key must be provided via the OPENAI_API_KEY environment variable.
    It must never be passed on the command line or stored in project files.
    """
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY is not set in the environment.")
        raise SystemExit(
            "ERROR: OPENAI_API_KEY is not set.\n\n"
            "Set your API key using:\n\n"
            "  export OPENAI_API_KEY=\"sk-...\"\n\n"
            "The API key must not be stored in the repository or passed as a CLI argument."
        )


def _cmd_parse(args: argparse.Namespace) -> int:
    """
    Handle the `parse` subcommand.

    Reads a Markdown novel, parses it into modules, and writes a blank
    narrative contract YAML file.

    :param args: Parsed argparse namespace.
    :return: Exit status code.
    """
    logger.info("Running parse command on %s", args.input)

    text = Path(args.input).read_text(encoding="utf-8")

    parser = CommonMarkNovelParser()
    novel = parser.parse(text, title=args.title or Path(args.input).stem)

    contracts = contract_from_novel(novel)
    yaml_text = dump_contract_yaml(contracts)

    Path(args.output).write_text(yaml_text, encoding="utf-8")

    logger.info("Blank contract YAML written to %s", args.output)
    return 0


def _cmd_infer(args: argparse.Namespace) -> int:
    """
    Handle the `infer` subcommand.

    Reads a Markdown novel, infers a full contract using an LLM-based
    inferencer, and writes the populated contract YAML file.

    This is the semantic front-end of the system: the novel is both parsed
    and interpreted without manual author intervention.

    :param args: Parsed argparse namespace.
    :return: Exit status code.
    """
    logger.info("Running infer command on %s", args.input)

    _require_openai_key()

    markdown_text = Path(args.input).read_text(encoding="utf-8")
    title = args.title or Path(args.input).stem

    logger.debug("Initializing OpenAI LLM client with model=%s", args.model)
    client_config = LLMClientConfig(model=args.model)
    client = OpenAILLMClient(config=client_config)
    inferencer = OpenAIContractInferencer(client=client)

    logger.info("Inferring narrative contract for novel: %s", title)
    contracts = infer_contract_from_markdown(
        markdown_text,
        title=title,
        inferencer=inferencer,
    )

    yaml_text = dump_contract_yaml(contracts)
    Path(args.output).write_text(yaml_text, encoding="utf-8")

    logger.info("Inferred contract YAML written to %s", args.output)
    return 0


def _cmd_assess(args: argparse.Namespace) -> int:
    """
    Handle the `assess` subcommand.

    Reads a contract YAML file, evaluates it using assessment rules,
    and writes a JSON report.

    :param args: Parsed argparse namespace.
    :return: Exit status code.
    """
    logger.info("Running assess command on %s", args.contract)

    yaml_text = Path(args.contract).read_text(encoding="utf-8")
    contracts = load_contract_yaml(yaml_text)

    reports = assess_contract(contracts)
    json_text = report_to_json(reports)

    Path(args.output).write_text(json_text, encoding="utf-8")

    logger.info("Assessment report written to %s", args.output)
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    """
    Build the top-level argument parser.

    :return: Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="novel-testbed",
        description="Novel test harness with narrative contract inference",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR).",
    )

    subparsers = parser.add_subparsers(dest="cmd", required=True)

    # ---- parse ----
    parse_cmd = subparsers.add_parser(
        "parse",
        help="Parse Markdown and create blank contract YAML",
    )
    parse_cmd.add_argument("input", help="Path to Markdown novel file.")
    parse_cmd.add_argument(
        "-o",
        "--output",
        required=True,
        help="Path to output YAML contract file.",
    )
    parse_cmd.add_argument(
        "--title",
        default=None,
        help="Optional novel title override.",
    )
    parse_cmd.set_defaults(func=_cmd_parse)

    # ---- infer ----
    infer_cmd = subparsers.add_parser(
        "infer",
        help="Parse Markdown, infer a full contract via LLM, and write YAML",
    )
    infer_cmd.add_argument("input", help="Path to Markdown novel file.")
    infer_cmd.add_argument(
        "-o",
        "--output",
        required=True,
        help="Path to output YAML contract file.",
    )
    infer_cmd.add_argument(
        "--title",
        default=None,
        help="Optional novel title override.",
    )
    infer_cmd.add_argument(
        "--model",
        default="gpt-4.1-mini",
        help="OpenAI model to use for inference.",
    )
    infer_cmd.set_defaults(func=_cmd_infer)

    # ---- assess ----
    assess_cmd = subparsers.add_parser(
        "assess",
        help="Assess a contract YAML and emit report JSON",
    )
    assess_cmd.add_argument(
        "contract",
        help="Path to YAML contract file.",
    )
    assess_cmd.add_argument(
        "-o",
        "--output",
        required=True,
        help="Path to output JSON report file.",
    )
    assess_cmd.set_defaults(func=_cmd_assess)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """
    Entry point for the CLI.

    :param argv: Optional argument vector (used for testing).
    :return: Exit status code.
    """
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    level = getattr(logging, str(args.log_level).upper(), logging.INFO)
    configure_logging(level)

    logger.debug("Dispatching command: %s", args.cmd)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())