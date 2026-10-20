"""Repository-level launcher for Samsung Auto Trader."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
	project_root = Path(__file__).resolve().parent
	trader_root = project_root / "samsung_auto_trader"
	if str(trader_root) not in sys.path:
		sys.path.insert(0, str(trader_root))

	from samsung_auto_trader.main import main as trader_main

	return trader_main()


if __name__ == "__main__":
	raise SystemExit(main())