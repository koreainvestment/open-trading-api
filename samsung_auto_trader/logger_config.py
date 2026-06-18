"""Logging setup."""

from __future__ import annotations

from datetime import datetime
import logging
from pathlib import Path

import config


class KSTFormatter(logging.Formatter):
	"""Format log timestamp in KST regardless of server local timezone."""

	def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
		dt = datetime.fromtimestamp(record.created, tz=config.KST)
		if datefmt:
			return dt.strftime(datefmt)
		return dt.isoformat()


def get_logger(name: str = "samsung_trader") -> logging.Logger:
	logger = logging.getLogger(name)
	if logger.handlers:
		return logger

	logger.setLevel(logging.INFO)
	Path(config.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

	formatter = KSTFormatter(
		"%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
		"%Y-%m-%d %H:%M:%S",
	)

	fh = logging.FileHandler(config.LOG_FILE, encoding="utf-8")
	fh.setFormatter(formatter)
	logger.addHandler(fh)

	sh = logging.StreamHandler()
	sh.setFormatter(formatter)
	logger.addHandler(sh)

	return logger


logger = get_logger()

