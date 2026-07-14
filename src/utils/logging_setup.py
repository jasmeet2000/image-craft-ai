"""Logging configuration for Image Craft AI.

Sets up console and rotating file handlers with consistent formatting.
All application modules should use ``logging.getLogger(__name__)`` —
this module configures the root logger they all inherit from.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_dir: Path, log_level: str = "INFO") -> None:
    """Configure application-wide logging with console and file output.

    Args:
        log_dir: Directory to write log files to (created if missing).
        log_level: Logging level string (DEBUG, INFO, WARNING, ERROR).
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "imagecraft.log"

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Avoid duplicate handlers on repeated calls
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
