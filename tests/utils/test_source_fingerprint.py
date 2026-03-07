"""
Tests for source fingerprinting utilities.

These tests verify that:
- SHA-256 hashes are computed correctly for files.
- Source metadata includes all required keys.
- The SHA-256 in metadata matches a direct hash of the provided text.
- Timestamps are ISO-formatted UTC strings.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from novel_testbed.utils.source_fingerprint import build_source_metadata, compute_sha256


# ---------------------------------------------------------------------------
# compute_sha256
# ---------------------------------------------------------------------------

def test_compute_sha256_returns_hex_string(tmp_path: Path):
    """
    compute_sha256 must return a hexadecimal SHA-256 digest.
    """
    test_file = tmp_path / "sample.md"
    test_file.write_text("Hello, world!", encoding="utf-8")

    digest = compute_sha256(test_file)

    assert isinstance(digest, str)
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)


def test_compute_sha256_matches_known_hash(tmp_path: Path):
    """
    The hash returned must match a reference computed independently.
    """
    content = b"deterministic content"
    test_file = tmp_path / "deterministic.md"
    test_file.write_bytes(content)

    expected = hashlib.sha256(content).hexdigest()
    actual = compute_sha256(test_file)

    assert actual == expected


def test_compute_sha256_raises_for_missing_file(tmp_path: Path):
    """
    compute_sha256 must raise FileNotFoundError for a non-existent file.
    """
    missing = tmp_path / "does_not_exist.md"

    with pytest.raises(FileNotFoundError):
        compute_sha256(missing)


def test_compute_sha256_different_content_different_hash(tmp_path: Path):
    """
    Two files with different content must produce different hashes.
    """
    file_a = tmp_path / "a.md"
    file_b = tmp_path / "b.md"
    file_a.write_text("Content A", encoding="utf-8")
    file_b.write_text("Content B", encoding="utf-8")

    assert compute_sha256(file_a) != compute_sha256(file_b)


# ---------------------------------------------------------------------------
# build_source_metadata
# ---------------------------------------------------------------------------

def test_build_source_metadata_contains_required_keys(tmp_path: Path):
    """
    build_source_metadata must return a dict with all required provenance keys.
    """
    original = tmp_path / "novel.md"
    copied = tmp_path / "source.md"
    text = "She stepped onto the sand."
    original.write_text(text, encoding="utf-8")
    copied.write_text(text, encoding="utf-8")

    metadata = build_source_metadata(
        original_path=original,
        copied_path=copied,
        text=text,
    )

    assert "original_path" in metadata
    assert "copied_path" in metadata
    assert "sha256" in metadata
    assert "generated_at" in metadata


def test_build_source_metadata_sha256_matches_text(tmp_path: Path):
    """
    The sha256 in the metadata must match a direct hash of the text string.
    """
    original = tmp_path / "novel.md"
    copied = tmp_path / "source.md"
    text = "The island was silent."
    original.write_text(text, encoding="utf-8")
    copied.write_text(text, encoding="utf-8")

    metadata = build_source_metadata(
        original_path=original,
        copied_path=copied,
        text=text,
    )

    expected_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert metadata["sha256"] == expected_sha


def test_build_source_metadata_paths_are_strings(tmp_path: Path):
    """
    Paths in metadata must be returned as plain strings, not Path objects.
    """
    original = tmp_path / "novel.md"
    copied = tmp_path / "source.md"
    text = "Wind."
    original.write_text(text, encoding="utf-8")
    copied.write_text(text, encoding="utf-8")

    metadata = build_source_metadata(
        original_path=original,
        copied_path=copied,
        text=text,
    )

    assert isinstance(metadata["original_path"], str)
    assert isinstance(metadata["copied_path"], str)


def test_build_source_metadata_timestamp_is_utc_iso(tmp_path: Path):
    """
    generated_at must be a parseable ISO-8601 UTC timestamp string.
    """
    from datetime import datetime, timezone

    original = tmp_path / "novel.md"
    copied = tmp_path / "source.md"
    text = "She ran."
    original.write_text(text, encoding="utf-8")
    copied.write_text(text, encoding="utf-8")

    metadata = build_source_metadata(
        original_path=original,
        copied_path=copied,
        text=text,
    )

    # Must parse without error
    dt = datetime.fromisoformat(metadata["generated_at"])
    assert dt.tzinfo is not None
