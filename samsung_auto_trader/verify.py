"""Quick verification script for samsung_auto_trader.

Usage:
	python verify.py
"""

from __future__ import annotations

from importlib import import_module


def check_imports() -> tuple[bool, str]:
	modules = [
		"config",
		"logger_config",
		"auth",
		"api_client",
		"market_data",
		"account",
		"orders",
		"trader",
		"main",
	]
	failed: list[str] = []
	for m in modules:
		try:
			import_module(m)
		except Exception as exc:  # pragma: no cover
			failed.append(f"{m}: {exc}")
	if failed:
		return False, "Import failed -> " + " | ".join(failed)
	return True, "All module imports OK"


def check_config() -> tuple[bool, str]:
	import config

	if config.STOCK_CODE != "005930":
		return False, f"Unexpected STOCK_CODE={config.STOCK_CODE}"
	if config.PRICE_OFFSET <= 0:
		return False, "PRICE_OFFSET must be positive"
	if not (config.TRADING_START < config.TRADING_END):
		return False, "Trading window invalid"
	now_kst = config.now_kst()
	return True, f"Config OK (KST now={now_kst:%Y-%m-%d %H:%M:%S})"


def check_credentials_presence() -> tuple[bool, str]:
	import config

	missing = []
	if not config.GH_ACCOUNT:
		missing.append("GH_ACCOUNT")
	if not config.GH_APPKEY:
		missing.append("GH_APPKEY")
	if not config.GH_APPSECRET:
		missing.append("GH_APPSECRET")

	if missing:
		return False, "Missing env vars: " + ", ".join(missing)
	return True, "Credential env vars present"


def check_log_write() -> tuple[bool, str]:
	from logger_config import logger
	import config
	from pathlib import Path

	logger.info("verify.py: logger health check")
	p = Path(config.LOG_FILE)
	if not p.exists():
		return False, f"Log file not found: {p}"
	return True, f"Log write OK ({p})"


def run_all() -> int:
	checks = [
		("imports", check_imports),
		("config", check_config),
		("credentials", check_credentials_presence),
		("logging", check_log_write),
	]

	print("=" * 68)
	print("Samsung Auto Trader Verification")
	print("=" * 68)

	failures = 0
	for name, fn in checks:
		ok, msg = fn()
		status = "PASS" if ok else "FAIL"
		print(f"[{status}] {name:<12} - {msg}")
		if not ok:
			failures += 1

	print("-" * 68)
	if failures:
		print(f"Verification finished with {failures} failure(s).")
		return 1
	print("Verification finished successfully.")
	return 0


if __name__ == "__main__":
	raise SystemExit(run_all())

