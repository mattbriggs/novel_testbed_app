"""
Types and validation helpers for inference outputs.

We keep validation lightweight and explicit to avoid introducing
heavy schema dependencies in v1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class InferredState:
    """
    Minimal inferred ReaderState payload returned by an inference backend.
    """

    genre: Optional[str]
    power_balance: Optional[str]
    emotional_tone: Optional[str]
    dominant_fantasy_id: Optional[str]
    threat_level: Optional[float]
    agency_level: Optional[float]


@dataclass(frozen=True)
class InferredModuleContract:
    """
    Inference result for a single module.
    """

    expected_changes: List[str]
    post_state: InferredState
    confidence: float = 0.5
    notes: Dict[str, Any] | None = None


def require_keys(obj: Dict[str, Any], keys: List[str]) -> None:
    """
    Require that the given dict has the specified keys.

    :param obj: Object to validate.
    :param keys: Required keys.
    :raises ValueError: if any key is missing.
    """
    missing = [k for k in keys if k not in obj]
    if missing:
        raise ValueError(f"Missing required keys: {missing}")