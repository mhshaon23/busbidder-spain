"""
logger.py
Logging configuration for BusBidder Spain.
Task 2 asks to record important events and errors into a log file.
Writes INFO level logs to 'busbidder.log' in the project root.
"""

import logging
from pathlib import Path

# Path to log file
LOG_FILE_PATH = Path(__file__).resolve().parent.parent.parent / "busbidder.log"


def configure_logger(name: str = "busbidder", level: int = logging.INFO) -> logging.Logger:
    """Sets up a logger that writes to busbidder.log and warnings to the console."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding multiple duplicate handlers
    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # File Handler: saves everything to busbidder.log
        file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console Handler: only shows warnings/errors in the console so it stays clean
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


logger = configure_logger()
