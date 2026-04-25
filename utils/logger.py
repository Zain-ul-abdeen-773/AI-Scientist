"""
Logger — Structured Logging Setup
==================================
Configures loguru for the entire application with
file + console output and rotation.
"""

import sys
from pathlib import Path
from loguru import logger


def setup_logger(log_level: str = "INFO") -> None:
    """
    Configure loguru for the application.

    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR)
    """
    # Remove default handler
    logger.remove()

    # Console output with colors
    logger.add(
        sys.stderr,
        level=log_level,
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{module}</cyan>:<cyan>{function}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # File output with rotation
    log_dir = Path(__file__).resolve().parent.parent / "data"
    log_dir.mkdir(exist_ok=True)

    logger.add(
        str(log_dir / "ai_scientist.log"),
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {module}:{function} | {message}",
        rotation="5 MB",
        retention="7 days",
        compression="zip",
    )

    logger.info("Logger initialized")
