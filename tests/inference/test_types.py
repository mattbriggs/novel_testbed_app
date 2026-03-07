"""
Tests for inference type definitions and validation helpers.

These tests verify that:
- InferredState is a frozen dataclass with the expected fields.
- require_keys raises ValueError for missing keys.
- require_keys passes silently for complete dicts.
"""

from __future__ import annotations

import pytest

from novel_testbed.inference.types import (
    InferredState,
    require_keys,
)


# ---------------------------------------------------------------------------
# InferredState
# ---------------------------------------------------------------------------

def test_inferred_state_all_fields_none():
    """
    InferredState must accept all-None fields.
    """
    state = InferredState(
        genre=None,
        power_balance=None,
        emotional_tone=None,
        dominant_fantasy_id=None,
        threat_level=None,
        agency_level=None,
    )

    assert state.genre is None
    assert state.threat_level is None


def test_inferred_state_with_values():
    """
    InferredState must store provided values.
    """
    state = InferredState(
        genre="survival",
        power_balance="environment",
        emotional_tone="unease",
        dominant_fantasy_id="UF_TEST_01",
        threat_level=0.7,
        agency_level=0.4,
    )

    assert state.genre == "survival"
    assert state.threat_level == 0.7
    assert state.dominant_fantasy_id == "UF_TEST_01"


def test_inferred_state_is_frozen():
    """
    InferredState must be immutable (frozen dataclass).
    """
    state = InferredState(
        genre="thriller",
        power_balance=None,
        emotional_tone=None,
        dominant_fantasy_id=None,
        threat_level=None,
        agency_level=None,
    )

    with pytest.raises((AttributeError, TypeError)):
        state.genre = "romance"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# require_keys
# ---------------------------------------------------------------------------

def test_require_keys_passes_for_complete_dict():
    """
    require_keys must not raise when all expected keys are present.
    """
    obj = {"a": 1, "b": 2, "c": 3}
    require_keys(obj, ["a", "b", "c"])  # Should not raise


def test_require_keys_raises_for_missing_key():
    """
    require_keys must raise ValueError listing all missing keys.
    """
    obj = {"a": 1}

    with pytest.raises(ValueError) as exc_info:
        require_keys(obj, ["a", "b", "c"])

    assert "b" in str(exc_info.value)
    assert "c" in str(exc_info.value)


def test_require_keys_raises_for_empty_dict():
    """
    require_keys must raise ValueError when the dict is empty but keys are expected.
    """
    with pytest.raises(ValueError):
        require_keys({}, ["required_key"])


def test_require_keys_passes_for_empty_key_list():
    """
    require_keys must not raise when no keys are required.
    """
    require_keys({"anything": 1}, [])  # Should not raise


def test_require_keys_value_can_be_none():
    """
    require_keys must not raise if a key is present but its value is None.

    Presence of the key is sufficient; None values are valid.
    """
    obj = {"genre": None, "threat_level": 0.5}
    require_keys(obj, ["genre", "threat_level"])  # Should not raise
