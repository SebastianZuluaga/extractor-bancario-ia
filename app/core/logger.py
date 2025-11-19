"""Utilities for secure, centralized logging configuration.

This module exposes a helper that configures a rotating log file inside the
project's secure configuration directory.  It is purposely small so it can be
imported early by both the UI and backend modules without introducing any
heavy dependencies or causing circular imports.
"""

from __future__ import annotations

import logging
import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Tuple


DEFAULT_LOG_NAME = "extractor_bancario"
_MAX_BYTES = 1_048_576  # 1 MiB
_BACKUP_COUNT = 5


def setup_logger(name: str = DEFAULT_LOG_NAME) -> Tuple[logging.Logger, Path]:
    """Return a logger configured with a rotating file handler.

    Parameters
    ----------
    name:
        Name of the logger to configure.  Multiple calls with the same name
        reuse the existing logger without duplicating handlers.

    Returns
    -------
    Tuple[logging.Logger, Path]
        The configured logger instance and the path to the log file.
    """

    # Crear directorio de logs si no existe
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    log_file = log_dir / f"app_{timestamp}.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid attaching multiple handlers when running the UI repeatedly.
    if not any(isinstance(h, RotatingFileHandler) and getattr(h, "baseFilename", None) == str(log_file)
               for h in logger.handlers):
        try:
            handler = RotatingFileHandler(
                log_file,
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
        except (PermissionError, OSError) as e:
            # Si no se puede crear el archivo de log, solo usar consola
            print(f"⚠️ No se pudo crear archivo de log: {e}")
            pass

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

    return logger, log_file


__all__ = ["setup_logger", "DEFAULT_LOG_NAME"]

