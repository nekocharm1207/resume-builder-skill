"""Structured logging setup."""

import logging
import sys


def setup_logger(name: str = "resume_builder", level: int = logging.INFO) -> logging.Logger:
    """Configure a colored logger with consistent formatting."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            "[%(levelname)s] %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
