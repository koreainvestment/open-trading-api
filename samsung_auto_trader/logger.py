from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(level: int = logging.INFO, log_file_path: str | Path | None = None) -> logging.Logger:
    logger = logging.getLogger("samsung_auto_trader")
    logger.setLevel(level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    log_path = Path(log_file_path) if log_file_path is not None else Path(__file__).resolve().parent / "trader.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    console.setLevel(level)

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    logger.addHandler(console)
    logger.addHandler(file_handler)
    logger.propagate = False
    return logger
