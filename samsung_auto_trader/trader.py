import time
from datetime import datetime, time as dt_time

from config import (
    DEFAULT_ORDER_QTY,
    ORDER_PRICE_GAP,
    POLL_INTERVAL_SECONDS,
    SYMBOL,
    TRADING_END,
    TRADING_START,
)


class SamsungAutoTrader:
    def __init__(self, market_data, account, orders, logger) -> None:
        self.market_data = market_data
        self.account = account
        self.orders = orders
        self.logger = logger

    def is_trading_window(self) -> bool:
        now = datetime.now().time()
        start = self._parse_time(TRADING_START)
        end = self._parse_time(TRADING_END)
        return start <= now <= end

    def is_after_trading_end(self) -> bool:
        now = datetime.now().time()
        end = self._parse_time(TRADING_END)
        return now > end

    def run_once(self) -> None:
        current_price = self.market_data.get_current_price(SYMBOL)

        buy_price = max(current_price - ORDER_PRICE_GAP, 1)
        sell_price = current_price + ORDER_PRICE_GAP

        before_qty = self.account.get_holding_quantity(SYMBOL)
        self.logger.info("Holdings before order. symbol=%s qty=%s", SYMBOL, before_qty)

        buy_result = self.orders.buy_limit(
            symbol=SYMBOL,
            quantity=DEFAULT_ORDER_QTY,
            price=buy_price,
        )
        self.logger.info("Buy order response: %s", buy_result)

        after_buy_qty = self.account.get_holding_quantity(SYMBOL)
        self.logger.info("Holdings after buy order. symbol=%s qty=%s", SYMBOL, after_buy_qty)

        if after_buy_qty > before_qty:
            self.logger.info("Buy execution seems to have occurred.")
        else:
            self.logger.info("Buy execution not confirmed yet.")

        sell_qty = min(DEFAULT_ORDER_QTY, after_buy_qty)

        if sell_qty <= 0:
            self.logger.info("No holdings available for sell order. Sell skipped.")
            return

        sell_result = self.orders.sell_limit(
            symbol=SYMBOL,
            quantity=sell_qty,
            price=sell_price,
        )
        self.logger.info("Sell order response: %s", sell_result)

        after_sell_qty = self.account.get_holding_quantity(SYMBOL)
        self.logger.info("Holdings after sell order. symbol=%s qty=%s", SYMBOL, after_sell_qty)

        if after_sell_qty < after_buy_qty:
            self.logger.info("Sell execution seems to have occurred.")
        else:
            self.logger.info("Sell execution not confirmed yet.")

    def run(self) -> None:
        self.logger.info("Samsung auto trader started.")

        while True:
            if self.is_after_trading_end():
                self.logger.info("Trading window ended. Program stopped.")
                break

            if not self.is_trading_window():
                self.logger.info("Outside trading window. Waiting...")
                time.sleep(POLL_INTERVAL_SECONDS)
                continue

            self.logger.info("Inside trading window. Running one trading cycle.")

            try:
                self.run_once()
            except Exception as e:
                self.logger.exception("Trading cycle failed: %s", e)

            time.sleep(POLL_INTERVAL_SECONDS)

    @staticmethod
    def _parse_time(value: str) -> dt_time:
        hour, minute = value.split(":")
        return dt_time(hour=int(hour), minute=int(minute))
