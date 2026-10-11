"""
Centralized logging configuration for BusBidder Spain.
Configures file and stream logging to support auditing and troubleshooting.
"""

import logging
from pathlib import Path

LOG_FILE_PATH = Path(__file__).resolve().parent.parent.parent / "busbidder.log"


def configure_logger(name: str = "busbidder", level: int = logging.INFO) -> logging.Logger:
    """
    Configures and returns an application logger writing to both stdout and busbidder.log.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers if already configured
    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # File Handler (persistent audit log)
        file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Keep console clean, full detail in log file
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


logger = configure_logger()
