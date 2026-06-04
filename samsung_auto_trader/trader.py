import time
from datetime import datetime
from zoneinfo import ZoneInfo

from config import (
    SYMBOL,
    TRADING_START,
    TRADING_END,
    POLL_INTERVAL_SECONDS,
    ORDER_PRICE_GAP,
)

KST = ZoneInfo("Asia/Seoul")


class SamsungAutoTrader:
    def __init__(self, market_data, account, orders, logger):
        self.market_data = market_data
        self.account = account
        self.orders = orders
        self.logger = logger

    def is_trading_window(self) -> bool:
        now = datetime.now(KST).time()
        start = datetime.strptime(TRADING_START, "%H:%M").time()
        end = datetime.strptime(TRADING_END, "%H:%M").time()
        return start <= now <= end

    def is_after_trading_end(self) -> bool:
        now = datetime.now(KST).time()
        end = datetime.strptime(TRADING_END, "%H:%M").time()
        return now > end

    def get_tick_size(self, price: int) -> int:
        if price < 2_000:
            return 1
        if price < 5_000:
            return 5
        if price < 20_000:
            return 10
        if price < 50_000:
            return 50
        if price < 200_000:
            return 100
        if price < 500_000:
            return 500
        return 1_000

    def adjust_price_to_tick(self, price: int, direction: str) -> int:
        tick = self.get_tick_size(price)

        if direction == "buy":
            return price - (price % tick)

        if direction == "sell":
            remainder = price % tick
            if remainder == 0:
                return price
            return price + (tick - remainder)

        raise ValueError(f"Invalid direction: {direction}")

    def run_once(self) -> None:
        now_kst = datetime.now(KST)
        self.logger.info(f"Current KST time: {now_kst.strftime('%Y-%m-%d %H:%M:%S')}")

        current_price = self.market_data.get_current_price(SYMBOL)
        self.logger.info(f"Current price of {SYMBOL}: {current_price}")

        before_quantity = self.account.get_holding_quantity(SYMBOL)
        sellable_quantity = self.account.get_sellable_quantity(SYMBOL)

        self.logger.info(f"{SYMBOL} holding quantity before order: {before_quantity}")
        self.logger.info(f"{SYMBOL} sellable quantity before order: {sellable_quantity}")

        raw_buy_price = current_price - ORDER_PRICE_GAP
        raw_sell_price = current_price + ORDER_PRICE_GAP

        buy_price = self.adjust_price_to_tick(raw_buy_price, "buy")
        sell_price = self.adjust_price_to_tick(raw_sell_price, "sell")

        self.logger.info(f"Raw buy price: {raw_buy_price}, adjusted buy price: {buy_price}")
        self.logger.info(f"Raw sell price: {raw_sell_price}, adjusted sell price: {sell_price}")

        quantity = 1

        if buy_price <= 0:
            self.logger.warning(f"Invalid buy price: {buy_price}")
            return

        self.logger.info(
            f"Submitting buy order: symbol={SYMBOL}, quantity={quantity}, price={buy_price}"
        )

        buy_result = self.orders.buy_limit(
            symbol=SYMBOL,
            quantity=quantity,
            price=buy_price,
        )

        self.logger.info(f"Buy order result: {buy_result}")

        time.sleep(10)

        after_buy_quantity = self.account.get_holding_quantity(SYMBOL)

        self.logger.info(f"{SYMBOL} quantity after buy order: {after_buy_quantity}")

        if after_buy_quantity > before_quantity:
            self.logger.info("Buy execution seems to have occurred.")
        else:
            self.logger.info("Buy execution not confirmed yet.")

        sellable_quantity = self.account.get_sellable_quantity(SYMBOL)
        self.logger.info(f"{SYMBOL} sellable quantity before sell order: {sellable_quantity}")

        if sellable_quantity <= 0:
            self.logger.info("No sellable quantity. Skipping sell order.")
            return

        sell_quantity = min(1, sellable_quantity)

        self.logger.info(
            f"Submitting sell order: symbol={SYMBOL}, quantity={sell_quantity}, price={sell_price}"
        )

        sell_result = self.orders.sell_limit(
            symbol=SYMBOL,
            quantity=sell_quantity,
            price=sell_price,
        )

        self.logger.info(f"Sell order result: {sell_result}")

        time.sleep(10)

        after_sell_quantity = self.account.get_holding_quantity(SYMBOL)

        self.logger.info(f"{SYMBOL} quantity after sell order: {after_sell_quantity}")

        if after_sell_quantity < after_buy_quantity:
            self.logger.info("Sell execution seems to have occurred.")
        else:
            self.logger.info("Sell execution not confirmed yet.")

    def run(self) -> None:
        self.logger.info("Samsung auto trader started.")
        self.logger.info(f"Trading window: {TRADING_START} ~ {TRADING_END} KST")

        while True:
            now_kst = datetime.now(KST)
            self.logger.info(f"Current KST time: {now_kst.strftime('%Y-%m-%d %H:%M:%S')}")

            if self.is_after_trading_end():
                self.logger.info("Trading window ended. Stopping trader.")
                break

            if not self.is_trading_window():
                self.logger.info("Outside trading window. Waiting...")
                time.sleep(POLL_INTERVAL_SECONDS)
                continue

            try:
                self.run_once()
            except Exception as e:
                self.logger.exception(f"Unexpected error during trading loop: {e}")

            self.logger.info(f"Sleeping for {POLL_INTERVAL_SECONDS} seconds.")
            time.sleep(POLL_INTERVAL_SECONDS)
