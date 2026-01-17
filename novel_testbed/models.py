"""
Core data models for the Novel Testbed.

These classes define the structural representation of:
- Parsed novels
- Fiction modules
- Reader state
- Narrative contracts

They are deliberately lightweight and side-effect free.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ModuleType(str, Enum):
    """
    Recognized fiction module types.
    """

    SCENE = "scene"
    EXPOSITION = "exposition"
    TRANSITION = "transition"
    OTHER = "other"


@dataclass
class Module:
    """
    Atomic unit of a novel.

    A module is a scene, exposition block, or transition segment that
    represents a single narrative operation.
    """

    id: str
    chapter: str
    title: str
    module_type: ModuleType
    start_line: int
    end_line: int
    text: str

    start_text: str = ""
    end_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        logger.debug(
            "Created Module %s (%s) in chapter '%s'",
            self.id,
            self.module_type.value,
            self.chapter,
        )


@dataclass
class Novel:
    """
    Parsed novel container.
    """

    title: str
    modules: List[Module] = field(default_factory=list)

    def __post_init__(self) -> None:
        logger.info(
            "Novel '%s' initialized with %d modules.",
            self.title,
            len(self.modules),
        )


@dataclass
class ReaderState:
    """
    Reader-facing narrative state.

    This describes what the reader currently believes and feels.
    """

    genre: Optional[str] = None
    power_balance: Optional[str] = None
    emotional_tone: Optional[str] = None
    dominant_fantasy_id: Optional[str] = None
    threat_level: Optional[float] = None
    agency_level: Optional[float] = None
    notes: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        logger.debug(
            "ReaderState created: genre=%s, threat=%s, agency=%s",
            self.genre,
            self.threat_level,
            self.agency_level,
        )


@dataclass
class ModuleContract:
    """
    Executable narrative contract for a single module.

    It defines:
    - What the reader state is before the passage
    - What it should be after
    - What the author claims this passage is meant to do
    """

    module_id: str
    module_title: str
    chapter: str

    page_range: Optional[str] = None
    module_type: Optional[str] = None
    fantasy_id: Optional[str] = None

    pre_state: ReaderState = field(default_factory=ReaderState)
    post_state: ReaderState = field(default_factory=ReaderState)

    expected_changes: List[str] = field(default_factory=list)
    anchors: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        logger.debug(
            "ModuleContract created for %s (%s)",
            self.module_id,
            self.module_title,
        )