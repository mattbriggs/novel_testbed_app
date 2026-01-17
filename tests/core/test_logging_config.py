"""
Tests for logging configuration.
"""

import logging

import pytest

from novel_testbed.logging_config import configure_logging


def reset_root_logger():
    """
    Remove all handlers from the root logger to allow clean testing.
    """
    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)
    root.setLevel(logging.WARNING)


def test_configure_logging_adds_handler():
    reset_root_logger()

    root = logging.getLogger()
    assert not root.handlers

    configure_logging(logging.DEBUG)

    assert len(root.handlers) == 1
    assert root.level == logging.DEBUG


def test_configure_logging_is_idempotent():
    reset_root_logger()

    configure_logging(logging.INFO)
    root = logging.getLogger()
    handler_count = len(root.handlers)

    # Second call should not add another handler
    configure_logging(logging.DEBUG)

    assert len(root.handlers) == handler_count


def test_logging_format_is_applied():
    reset_root_logger()

    configure_logging(logging.INFO)
    root = logging.getLogger()
    handler = root.handlers[0]

    fmt = handler.formatter._fmt
    assert "%(asctime)s" in fmt
    assert "%(levelname)s" in fmt
    assert "%(name)s" in fmt
    assert "%(message)s" in fmt