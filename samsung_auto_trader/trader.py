from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, time as dt_time
from zoneinfo import ZoneInfo

try:
    from .account import AccountService, AccountSnapshot
    from .market_data import MarketDataService, Quote
    from .orders import OrderService, OrderResult
except ImportError:  # pragma: no cover
    from account import AccountService, AccountSnapshot
    from market_data import MarketDataService, Quote
    from orders import OrderService, OrderResult


@dataclass(frozen=True)
class TradingObservation:
    quote: Quote
    before: AccountSnapshot
    after_buy: AccountSnapshot
    after_sell: AccountSnapshot
    buy_order: OrderResult
    sell_order: OrderResult


def _round_to_tick(price: int, side: str) -> int:
    if price <= 0:
        return 0

    if price < 1000:
        tick = 1
    elif price < 5000:
        tick = 5
    elif price < 10000:
        tick = 10
    elif price < 50000:
        tick = 50
    elif price < 100000:
        tick = 100
    elif price < 500000:
        tick = 500
    else:
        tick = 1000

    if side == "buy":
        return max(tick, (price // tick) * tick)
    return max(tick, ((price + tick - 1) // tick) * tick)


def _held_quantity(snapshot: AccountSnapshot, symbol: str) -> int:
    for holding in snapshot.holdings:
        if holding.symbol == symbol:
            return holding.quantity
    return 0


def _cash_value(snapshot: AccountSnapshot) -> int:
    return snapshot.available_cash or snapshot.cash


class SamsungAutoTrader:
    def __init__(
        self,
        symbol: str,
        market_code: str,
        price_offset_krw: int,
        order_quantity: int,
        poll_interval_seconds: int,
        verify_delay_seconds: int,
        trading_start: dt_time,
        trading_end: dt_time,
        market_data: MarketDataService,
        account: AccountService,
        orders: OrderService,
        logger,
    ) -> None:
        self.symbol = symbol
        self.market_code = market_code
        self.price_offset_krw = price_offset_krw
        self.order_quantity = order_quantity
        self.poll_interval_seconds = poll_interval_seconds
        self.verify_delay_seconds = verify_delay_seconds
        self.trading_start = trading_start
        self.trading_end = trading_end
        self.market_data = market_data
        self.account = account
        self.orders = orders
        self.logger = logger
        self.timezone = ZoneInfo("Asia/Seoul")

    def run(self) -> None:
        self.logger.info("trading window configured: %s - %s", self.trading_start, self.trading_end)
        self._wait_until_window()
        if datetime.now(self.timezone).time() >= self.trading_end:
            self.logger.info("trading window ended")
            return
        self.logger.info("trading window started")

        while True:
            now = datetime.now(self.timezone)
            if now.time() >= self.trading_end:
                self.logger.info("trading window ended")
                return
            if now.time() < self.trading_start:
                self._wait_until_window()
                continue

            try:
                self._run_one_cycle()
            except Exception as exc:  # pragma: no cover - defensive runtime guard
                self.logger.exception("cycle failed: %s", exc)

            sleep_seconds = self._seconds_until_next_cycle()
            if sleep_seconds <= 0:
                continue
            self.logger.info("sleeping before next poll: %ss", sleep_seconds)
            time.sleep(sleep_seconds)

    def _run_one_cycle(self) -> None:
        quote = self.market_data.get_current_price(self.symbol, self.market_code)
        before = self.account.get_snapshot()
        self._log_snapshot("holdings before order", before)

        buy_price = _round_to_tick(max(1, quote.price - self.price_offset_krw), "buy")
        sell_price = _round_to_tick(quote.price + self.price_offset_krw, "sell")

        self.logger.info(
            "buy order request: symbol=%s current=%s target=%s quantity=%s",
            self.symbol,
            f"{quote.price:,}",
            f"{buy_price:,}",
            self.order_quantity,
        )
        buy_order = self.orders.place_limit_order("buy", self.symbol, self.order_quantity, buy_price)
        time.sleep(self.verify_delay_seconds)
        after_buy = self.account.get_snapshot()
        self._log_snapshot("holdings after buy", after_buy)
        self._log_execution("buy", before, after_buy)

        self.logger.info(
            "sell order request: symbol=%s current=%s target=%s quantity=%s",
            self.symbol,
            f"{quote.price:,}",
            f"{sell_price:,}",
            self.order_quantity,
        )
        sell_order = self.orders.place_limit_order("sell", self.symbol, self.order_quantity, sell_price)
        time.sleep(self.verify_delay_seconds)
        after_sell = self.account.get_snapshot()
        self._log_snapshot("holdings after sell", after_sell)
        self._log_execution("sell", after_buy, after_sell)

        TradingObservation(
            quote=quote,
            before=before,
            after_buy=after_buy,
            after_sell=after_sell,
            buy_order=buy_order,
            sell_order=sell_order,
        )

    def _log_snapshot(self, label: str, snapshot: AccountSnapshot) -> None:
        target_qty = _held_quantity(snapshot, self.symbol)
        self.logger.info(
            "%s: symbol=%s qty=%s cash=%s available=%s total=%s",
            label,
            self.symbol,
            target_qty,
            f"{_cash_value(snapshot):,}",
            f"{snapshot.available_cash:,}",
            f"{snapshot.total_value:,}",
        )

    def _log_execution(self, side: str, before: AccountSnapshot, after: AccountSnapshot) -> None:
        before_qty = _held_quantity(before, self.symbol)
        after_qty = _held_quantity(after, self.symbol)
        before_cash = _cash_value(before)
        after_cash = _cash_value(after)

        if side == "buy":
            executed = after_qty > before_qty or after_cash < before_cash
        else:
            executed = after_qty < before_qty or after_cash > before_cash

        self.logger.info(
            "%s execution check: %s (qty %s -> %s, cash %s -> %s)",
            side,
            "executed seems likely" if executed else "no clear execution signal",
            before_qty,
            after_qty,
            f"{before_cash:,}",
            f"{after_cash:,}",
        )

    def _wait_until_window(self) -> None:
        now = datetime.now(self.timezone)
        if now.time() >= self.trading_end:
            self.logger.info("trading window already ended")
            return

        if now.time() >= self.trading_start:
            return

        target = datetime.combine(now.date(), self.trading_start, tzinfo=self.timezone)
        wait_seconds = max(0, int((target - now).total_seconds()))
        self.logger.info("waiting for trading window start: %ss", wait_seconds)
        time.sleep(wait_seconds)

    def _seconds_until_next_cycle(self) -> int:
        now = datetime.now(self.timezone)
        end_dt = datetime.combine(now.date(), self.trading_end, tzinfo=self.timezone)
        remaining = int((end_dt - now).total_seconds())
        return max(0, min(self.poll_interval_seconds, remaining))
