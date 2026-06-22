# 자동매매 핵심 로직
# 흐름
# 1. 현재 시간이 거래시간인지 확인
# 2. 현재가 조회
# 3. 보유수량 조회
# 4. 매도가능수량 조회
# 5. 매수가 계산
# 6. 매도가 계산
# 7. 호가단위 보정
# 8. 매수 주문
# 9. 잔고 확인
# 10. 매도가능수량이 있으면 매도 주문
# 11. 반복

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

# Codespaces는 UTC 시간이므로 한국 주식시장 기준인 KST로 시간 계산
KST = ZoneInfo("Asia/Seoul") 


class SamsungAutoTrader:
    def __init__(self, market_data, account, orders, logger):
        self.market_data = market_data
        self.account = account
        self.orders = orders
        self.logger = logger

    # 현재 시간이 09:10~15:30 사이인지 확인
    def is_trading_window(self) -> bool:
        now = datetime.now(KST).time()
        start = datetime.strptime(TRADING_START, "%H:%M").time()
        end = datetime.strptime(TRADING_END, "%H:%M").time()
        return start <= now <= end

    # 15:30 이후면 자동매매 종료
    def is_after_trading_end(self) -> bool:
        now = datetime.now(KST).time()
        end = datetime.strptime(TRADING_END, "%H:%M").time()
        return now > end

    # 가격대별 호가단위를 반환
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

    # 주문가격을 호가단위에 맞게 조정
    def adjust_price_to_tick(self, price: int, direction: str) -> int:
        tick = self.get_tick_size(price)

        # 매수는 보수적으로 아래 호가로 내림.
        if direction == "buy":
            return price - (price % tick)

        # 매도는 보수적으로 위 호가로 올림.
        if direction == "sell":
            remainder = price % tick
            if remainder == 0:
                return price
            return price + (tick - remainder)

        raise ValueError(f"Invalid direction: {direction}")

    # 자동매매를 1회 실행
    def run_once(self) -> None:
        now_kst = datetime.now(KST)

        # 현재가 조회
        current_price = self.market_data.get_current_price(SYMBOL)
        self.logger.info(f"{SYMBOL}의 현재 가격: {current_price}")

        # 현재 잔고
        available_cash = self.account.get_available_cash(SYMBOL)
        self.logger.info(f"현재 잔고: {available_cash}")
        
        # 현재 보유수량 확인.
        before_quantity = self.account.get_holding_quantity(SYMBOL)
        sellable_quantity = self.account.get_sellable_quantity(SYMBOL)

        self.logger.info(f"{SYMBOL} 주문 전 수량: {before_quantity}")
        self.logger.info(f"{SYMBOL} 주문 전 판매 가능한 수량: {sellable_quantity}")

        # 현재가 기준 주문가격 계산.
        raw_buy_price = current_price - ORDER_PRICE_GAP
        raw_sell_price = current_price + ORDER_PRICE_GAP

        # 호가단위에 맞게 보정.
        buy_price = self.adjust_price_to_tick(raw_buy_price, "buy")
        sell_price = self.adjust_price_to_tick(raw_sell_price, "sell")

        self.logger.info(f"매수 가격: {buy_price}")
        self.logger.info(f"매도 가격: {sell_price}")

        quantity = 1

        if buy_price <= 0:
            self.logger.warning(f"Invalid buy price: {buy_price}")
            return

        self.logger.info(
            f"매수 주문 제출: symbol={SYMBOL}, 수량={quantity}, 구매가격={buy_price}"
        )

        # 매수 주문 전송
        buy_result = self.orders.buy_limit(
            symbol=SYMBOL,
            quantity=quantity,
            price=buy_price,
        )

        self.logger.info(f"매수 주문 결과: {buy_result}")

        time.sleep(10)

        # 매수 후 잔고 확인
        after_available_cash = self.account.get_available_cash(SYMBOL)
        self.logger.info(f"주문 후 잔고: {after_available_cash}")
        
        # 매수 후 보유수량 확인.
        after_buy_quantity = self.account.get_holding_quantity(SYMBOL)

        self.logger.info(f"{SYMBOL} 주문 후 수량: {after_buy_quantity}")

        # 보유수량이 늘었으면 체결된 것으로 추정. 그대로면 아직 체결 확인 안 됨
        if after_buy_quantity > before_quantity:
            self.logger.info("매수 주문이 체결되었습니다.")
        else:
            self.logger.info("매수 주문이 미체결되었습니다.")

        # 매도가능수량 확인
        sellable_quantity = self.account.get_sellable_quantity(SYMBOL)
        self.logger.info(f"{SYMBOL} 주문 전 판매 가능한 수량: {sellable_quantity}")

        # 매도가능수량이 0이면 매도 주문을 넣지 않음
        if sellable_quantity <= 0:
            self.logger.info("매도가능수량이 없습니다.")
            return

        sell_quantity = min(1, sellable_quantity)

        self.logger.info(
            f"매도 주문을 제출합니다: symbol={SYMBOL}, 수량={sell_quantity}, 판매가격={sell_price}"
        )

        # 매도가능수량이 있을 때만 매도 주문.
        sell_result = self.orders.sell_limit(
            symbol=SYMBOL,
            quantity=sell_quantity,
            price=sell_price,
        )

        self.logger.info(f"매도 주문 결과: {sell_result}")

        # API 호출을 너무 자주 하지 않기 위해 대기
        time.sleep(10)

        after_sell_quantity = self.account.get_holding_quantity(SYMBOL)

        self.logger.info(f"{SYMBOL} 매도주문 후 수량: {after_sell_quantity}")

        if after_sell_quantity < after_buy_quantity:
            self.logger.info("매도 주문이 체결되었습니다.")
        else:
            self.logger.info("매도 주문이 미체결되었습니다.")

    # 거래시간 동안 run_once()를 반복 실행
    def run(self) -> None:
        self.logger.info("Samsung auto trader started.")
        self.logger.info(f"Trading window: {TRADING_START} ~ {TRADING_END} KST")

        while True:
            now_kst = datetime.now(KST)
            self.logger.info(f"현재 한국 시간: {now_kst.strftime('%Y-%m-%d %H:%M:%S')}")

            if self.is_after_trading_end():
                self.logger.info("거래시간이 끝났습니다. trader를 멈춥니다.")
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
