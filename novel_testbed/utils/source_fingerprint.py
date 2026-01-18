"""
Source fingerprinting utilities.

This module provides cryptographic and provenance utilities for tying a
generated narrative contract to a specific Markdown source file.

It ensures that contracts cannot silently drift from their originating text.

Primary responsibilities:
- Compute SHA-256 hashes of source files.
- Build provenance metadata blocks for embedding in contract YAML.
- Enable verification that a contract still matches its source.

This is the system’s integrity layer.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


def compute_sha256(path: Path) -> str:
    """
    Compute the SHA-256 hash of a file.

    The file is read in chunks to avoid loading large files into memory.

    :param path: Path to the file to hash.
    :return: Hexadecimal SHA-256 digest string.
    :raises FileNotFoundError: If the file does not exist.
    :raises IOError: If the file cannot be read.
    """
    logger.debug("Computing SHA-256 hash for file: %s", path)

    hasher = hashlib.sha256()

    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(8192), b""):
            hasher.update(chunk)

    digest = hasher.hexdigest()
    logger.debug("Computed SHA-256: %s...", digest[:12])

    return digest


def build_source_metadata(
    original_path: Path,
    copied_path: Path,
    text: str,
) -> Dict[str, str]:
    """
    Build a provenance metadata block for a Markdown source file.

    This metadata is embedded in contract YAML to guarantee that the contract
    remains bound to the exact version of the source text used to generate it.

    The metadata includes:
    - Original input path
    - Copied source path
    - SHA-256 hash of the content
    - UTC timestamp of generation

    :param original_path: Path to the user-supplied Markdown file.
    :param copied_path: Path where the canonical copy was stored.
    :param text: Full text content of the Markdown source.
    :return: Dictionary suitable for embedding under a top-level ``source`` key
             in the contract YAML.
    """
    logger.debug(
        "Building source metadata for original=%s copied=%s",
        original_path,
        copied_path,
    )

    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    generated_at = datetime.now(timezone.utc).isoformat()

    metadata = {
        "original_path": str(original_path),
        "copied_path": str(copied_path),
        "sha256": sha,
        "generated_at": generated_at,
    }

    logger.info(
        "Source metadata created (sha256=%s..., generated_at=%s)",
        sha[:12],
        generated_at,
    )

    return metadata