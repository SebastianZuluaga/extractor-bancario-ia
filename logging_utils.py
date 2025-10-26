"""Utilities for secure, centralized logging configuration.

This module exposes a helper that configures a rotating log file inside the
project's secure configuration directory.  It is purposely small so it can be
imported early by both the UI and backend modules without introducing any
heavy dependencies or causing circular imports.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Tuple


DEFAULT_LOG_NAME = "extractor_bancario"
_MAX_BYTES = 1_048_576  # 1 MiB
_BACKUP_COUNT = 5


def configurar_logger(nombre: str = DEFAULT_LOG_NAME) -> Tuple[logging.Logger, Path]:
    """Return a logger configured with a rotating file handler.

    Parameters
    ----------
    nombre:
        Name of the logger to configure.  Multiple calls with the same name
        reuse the existing logger without duplicating handlers.

    Returns
    -------
    Tuple[logging.Logger, Path]
        The configured logger instance and the path to the log file.
    """

    config_dir = Path.home() / ".extractor_bancario"
    config_dir.mkdir(mode=0o700, parents=True, exist_ok=True)

    log_path = config_dir / "extractor.log"

    logger = logging.getLogger(nombre)
    logger.setLevel(logging.INFO)

    # Avoid attaching multiple handlers when running the UI repeatedly.
    if not any(isinstance(h, RotatingFileHandler) and getattr(h, "baseFilename", None) == str(log_path)
               for h in logger.handlers):
        handler = RotatingFileHandler(
            log_path,
            maxBytes=_MAX_BYTES,
            backupCount=_BACKUP_COUNT,
            encoding="utf-8",
        )
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

    # Ensure at least console output when running via CLI (useful during
    # development).  We do not attach a console handler if one is already
    # present to prevent duplicated messages.
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(
            logging.Formatter("%(levelname)s | %(message)s")
        )
        logger.addHandler(console_handler)

    return logger, log_path


__all__ = ["configurar_logger", "DEFAULT_LOG_NAME"]

