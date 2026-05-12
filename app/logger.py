"""
logger.py — Central logging configuration.
Import `get_logger` in every layer to keep log format consistent.
"""

import logging
import sys
from pathlib import Path

LOG_FILE = Path(__file__).parent.parent / "app.log"

def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger wired to both the console and app.log.
    Call once per module:  logger = get_logger(__name__)
    """
    logger = logging.getLogger(name)

    # Only add handlers the very first time this logger is created
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # ── Console handler ──────────────────────────────────────────────────
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # ── File handler (app.log) ───────────────────────────────────────────
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        # Prevent messages from bubbling up to the root logger
        logger.propagate = False

    return logger
