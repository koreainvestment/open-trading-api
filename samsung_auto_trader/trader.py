import argparse
import sys
import time
from datetime import datetime
from typing import Any

from samsung_auto_trader.account import AccountService
from samsung_auto_trader.config import config
from samsung_auto_trader.logger import logger
from samsung_auto_trader.market_data import MarketDataService
from samsung_auto_trader.orders import OrderService
from samsung_auto_trader.api_client import KISClient


class SamsungTrader:
    def __init__(self, offset: int | None = None, dry_run: bool | None = None, paper_trading: bool | None = None) -> None:
        self.offset = offset if offset is not None else config.order_offset_krw
        self.dry_run = config.dry_run if dry_run is None else dry_run
        self.paper_trading = config.paper_trading if paper_trading is None else paper_trading
        self.client = KISClient()
        self.market_data = MarketDataService(self.client)
        self.account_service = AccountService(self.client)
        self.order_service = OrderService(self.client, paper_trading=self.paper_trading)

    def _is_within_trading_window(self) -> bool:
        now = datetime.now()
        start = datetime.strptime(config.start_time_str, "%H:%M").time()
        end = datetime.strptime(config.end_time_str, "%H:%M").time()
        return start <= now.time() <= end

    def _print_window_status(self) -> None:
        if self._is_within_trading_window():
            logger.info("Trading window is open.")
        else:
            logger.info("Trading window is closed.")

    def _determine_quantity(self, available_cash: int, price: int) -> int:
        if price <= 0:
            return 0
        max_qty = available_cash // price
        return max_qty if max_qty > 0 else 0

    def _record_execution(self, before: dict[str, Any], after: dict[str, Any]) -> bool:
        before_qty = len(before["holdings"])
        after_qty = len(after["holdings"])
        if before_qty != after_qty:
            return True
        return before["available_cash"] != after["available_cash"]

    def run_cycle(self, once: bool = False) -> None:
        logger.info("Starting Samsung Electronics auto trader. dry_run=%s paper_trading=%s offset=%s", self.dry_run, self.paper_trading, self.offset)
        if not self._is_within_trading_window():
            logger.info("Exiting because current time is outside the trading window.")
            return

        current_price = self.market_data.get_current_price(config.symbol)
        if current_price is None:
            logger.error("Could not read current price. Aborting cycle.")
            return
        logger.info("Current Samsung price: %s KRW", current_price)

        before_snapshot = self.account_service.get_account_snapshot()
        logger.info("Holdings before order: %s", before_snapshot["holdings"])

        order_price_buy = current_price - self.offset
        order_price_sell = current_price + self.offset
        quantity = self._determine_quantity(before_snapshot["available_cash"], order_price_buy)

        if quantity <= 0:
            logger.info("Not enough available cash to place a buy order at %s KRW.", order_price_buy)
        else:
            if self.dry_run:
                logger.info("DRY_RUN enabled, skipping actual buy order. buy_price=%s qty=%s", order_price_buy, quantity)
            else:
                self.order_service.place_buy_order(config.symbol, quantity, order_price_buy)

        if self.dry_run:
            logger.info("DRY_RUN enabled, skipping actual sell order.")
        else:
            self.order_service.place_sell_order(config.symbol, 1, order_price_sell)

        time.sleep(config.polling_interval_seconds)
        after_snapshot = self.account_service.get_account_snapshot()
        logger.info("Holdings after order: %s", after_snapshot["holdings"])
        execution_happened = self._record_execution(before_snapshot, after_snapshot)
        logger.info("Execution observed from snapshots: %s", execution_happened)

        if once:
            logger.info("One-cycle mode complete. Exiting.")
            return

        while True:
            if not self._is_within_trading_window():
                logger.info("Trading window ended. Stopping trader.")
                break
            logger.info("Waiting for next check after %s seconds.", config.polling_interval_seconds)
            time.sleep(config.polling_interval_seconds)
            self.run_cycle(once=True)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Samsung Electronics auto trader for mock KIS REST API.")
    parser.add_argument("--once", action="store_true", help="Run a single polling cycle and exit.")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", help="Enable dry run mode without sending orders.")
    parser.add_argument("--no-dry-run", dest="dry_run", action="store_false", help="Disable dry run mode.")
    parser.add_argument("--paper-trading", dest="paper_trading", action="store_true", help="Enable paper trading mode.")
    parser.add_argument("--no-paper-trading", dest="paper_trading", action="store_false", help="Disable paper trading mode.")
    parser.add_argument("--offset", type=int, help="ORDER_OFFSET_KRW to use for buy/sell levels.")
    parser.set_defaults(dry_run=True, paper_trading=True)
    return parser


def run_from_cli(argv: list[str] | None = None) -> None:
    parser = create_parser()
    args = parser.parse_args(argv)
    trader = SamsungTrader(offset=args.offset, dry_run=args.dry_run, paper_trading=args.paper_trading)
    trader.run_cycle(once=args.once)


if __name__ == "__main__":
    run_from_cli()
