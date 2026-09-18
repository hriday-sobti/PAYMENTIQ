"""
PAYMENTIQ Structured Logging Utility
Provides consistent, formatted logging across all pipeline modules.
"""
import logging
import os
import sys
from typing import Optional

def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Configures and returns a logger instance with standardized formatting."""
    log_level = level or os.getenv("LOG_LEVEL", "INFO").upper()
    numeric_level = getattr(logging, log_level, logging.INFO)

    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(numeric_level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(numeric_level)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | %(name)-24s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    return logger
