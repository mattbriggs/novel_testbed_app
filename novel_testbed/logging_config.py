"""
Central logging configuration for the Novel Testbed package.

This module configures a single root logger for the application.
It is intentionally minimal and defensive: if logging is already
configured, it will not override existing handlers.

All other modules in the package should obtain loggers via:

    logger = logging.getLogger(__name__)
"""

from __future__ import annotations

import logging


def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure package-wide logging.

    This function initializes the root logger with a StreamHandler
    and a consistent format. If handlers are already present, the
    function exits without modifying existing configuration.

    :param level: Logging level (e.g., logging.INFO, logging.DEBUG).
    """
    root = logging.getLogger()

    if root.handlers:
        root.debug("Logging already configured; skipping reconfiguration.")
        return

    root.setLevel(level)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)

    root.info("Logging configured at level %s", logging.getLevelName(level))