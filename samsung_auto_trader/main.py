"""Application entrypoint."""

from __future__ import annotations

import sys

import auth
import config
from api_client import APIClient
from logger_config import logger
from trader import run


def main() -> int:
	logger.info("=" * 70)
	logger.info("Samsung Auto-Trader Starting")
	logger.info("=" * 70)
	logger.info("Step 1: Validating credentials...")

	try:
		config.validate_credentials()
		logger.info("✓ Credentials validated")
	except Exception as exc:
		logger.error(f"Credential validation failed: {exc}")
		return 1

	logger.info("Step 2: Authenticating...")
	token = auth.get_token()
	if not token:
		logger.error("Authentication failed")
		return 1
	logger.info("✓ Authentication successful")

	logger.info("Step 3: Initializing API client...")
	client = APIClient(token)
	logger.info("✓ API client ready")

	now_kst = config.now_kst()
	logger.info("Step 4: Configuration Summary")
	logger.info(f"  Stock: {config.STOCK_CODE} ({config.STOCK_NAME})")
	logger.info(f"  Trading Window(KST): {config.TRADING_START.strftime('%H:%M')} - {config.TRADING_END.strftime('%H:%M')}")
	logger.info(f"  Current KST: {now_kst:%Y-%m-%d %H:%M:%S}")
	logger.info("Step 5: Starting trading loop...")

	run(client)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
