import time
from datetime import datetime

from api_client import ApiClient
from auth import get_access_token
from config import AppConfig
from logger import get_logger
from market_data import MarketDataService
from orders import OrderService
from account import AccountService, AccountInfo

logger = get_logger(__name__)

CYCLE_SEPARATOR = "-" * 80

SYMBOL = "005930"
PRICE_DELTA = 1000

# 주문 수량
ORDER_QUANTITY = 1

# 한 사이클 안에서 매수/매도 각각 최대 1번
MAX_BUY_ORDERS_PER_CYCLE = 1
MAX_SELL_ORDERS_PER_CYCLE = 1

# API 호출 사이 대기 시간
API_CALL_DELAY_SECONDS = 1.5


class StockTrader:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.api_client = ApiClient(config)
        self.market_data = MarketDataService(self.api_client)
        self.account_service = AccountService(self.api_client, config.account_no)
        self.order_service = OrderService(self.api_client, config.account_no)

    def _is_in_trading_window(self) -> bool:
        now = datetime.now()
        start = datetime.strptime(self.config.trading_start, "%H:%M").time()
        end = datetime.strptime(self.config.trading_end, "%H:%M").time()
        return start <= now.time() <= end

    def _sleep_until_start(self) -> None:
        now = datetime.now()
        start_time = datetime.combine(
            now.date(),
            datetime.strptime(self.config.trading_start, "%H:%M").time(),
        )

        if now < start_time:
            delta = (start_time - now).seconds
            logger.info(
                "[WAIT] Trading window not started. sleep_seconds=%s start=%s",
                delta,
                self.config.trading_start,
            )
            time.sleep(min(delta, 300))

    def _api_delay(self) -> None:
        time.sleep(API_CALL_DELAY_SECONDS)

    def _confirm_execution(self, before: AccountInfo, after: AccountInfo) -> str:
        if after.stock_quantity > before.stock_quantity:
            return "Buy execution appears to have occurred."
        if after.stock_quantity < before.stock_quantity:
            return "Sell execution appears to have occurred."
        if after.cash_available != before.cash_available:
            return "Cash changed; execution may have occurred."
        return "No clear execution change was detected."

    def run(self) -> None:
        token = get_access_token(self.config)

        logger.info(
            "[START] Samsung Auto Trader started. trading_window=%s-%s symbol=%s "
            "order_quantity=%s max_buy_per_cycle=%s max_sell_per_cycle=%s",
            self.config.trading_start,
            self.config.trading_end,
            SYMBOL,
            ORDER_QUANTITY,
            MAX_BUY_ORDERS_PER_CYCLE,
            MAX_SELL_ORDERS_PER_CYCLE,
        )

        while True:
            now = datetime.now()

            if not self._is_in_trading_window():
                if now.time() > datetime.strptime(self.config.trading_end, "%H:%M").time():
                    logger.info(
                        "[STOP] Trading window ended. end=%s",
                        self.config.trading_end,
                    )
                    break

                self._sleep_until_start()
                continue

            try:
                # 한 사이클마다 매수/매도 카운터 초기화
                buy_orders_this_cycle = 0
                sell_orders_this_cycle = 0

                logger.info(CYCLE_SEPARATOR)
                logger.info("[CYCLE_START] symbol=%s", SYMBOL)
                logger.info(CYCLE_SEPARATOR)

                current_price = self.market_data.get_current_price(
                    token=token,
                    symbol=SYMBOL,
                )

                logger.info(
                    "[MARKET] symbol=%s current_price=%s",
                    SYMBOL,
                    current_price,
                )

                self._api_delay()

                before_info = self.account_service.get_account_info(
                    token=token,
                    symbol=SYMBOL,
                )

                logger.info(
                    "[ACCOUNT_BEFORE] cash=%s holding_qty=%s",
                    before_info.cash_available,
                    before_info.stock_quantity,
                )

                buy_price = max(current_price - PRICE_DELTA, 1)
                sell_price = current_price + PRICE_DELTA

                can_buy = before_info.cash_available >= buy_price * ORDER_QUANTITY
                can_sell = before_info.stock_quantity >= ORDER_QUANTITY

                logger.info(
                    "[STRATEGY] buy_price=%s sell_price=%s order_qty=%s "
                    "can_buy=%s can_sell=%s buy_orders_this_cycle=%s sell_orders_this_cycle=%s",
                    buy_price,
                    sell_price,
                    ORDER_QUANTITY,
                    can_buy,
                    can_sell,
                    buy_orders_this_cycle,
                    sell_orders_this_cycle,
                )

                self._api_delay()

                # 매수: 한 사이클에 최대 1번
                if can_buy and buy_orders_this_cycle < MAX_BUY_ORDERS_PER_CYCLE:
                    buy_result = self.order_service.submit_limit_order(
                        token=token,
                        symbol=SYMBOL,
                        quantity=ORDER_QUANTITY,
                        price=buy_price,
                        side="buy",
                    )

                    buy_orders_this_cycle += 1

                    logger.info(
                        "[ORDER_RESULT] side=buy success=%s order_id=%s msg=%s buy_orders_this_cycle=%s",
                        buy_result.success,
                        buy_result.order_id,
                        buy_result.message,
                        buy_orders_this_cycle,
                    )
                else:
                    if not can_buy:
                        logger.info(
                            "[ORDER_SKIP] side=buy reason=insufficient_cash cash=%s required_cash=%s",
                            before_info.cash_available,
                            buy_price * ORDER_QUANTITY,
                        )
                    else:
                        logger.info(
                            "[ORDER_SKIP] side=buy reason=max_buy_orders_per_cycle_reached"
                        )

                self._api_delay()

                # 매도: 한 사이클에 최대 1번
                if can_sell and sell_orders_this_cycle < MAX_SELL_ORDERS_PER_CYCLE:
                    sell_result = self.order_service.submit_limit_order(
                        token=token,
                        symbol=SYMBOL,
                        quantity=ORDER_QUANTITY,
                        price=sell_price,
                        side="sell",
                    )

                    sell_orders_this_cycle += 1

                    logger.info(
                        "[ORDER_RESULT] side=sell success=%s order_id=%s msg=%s sell_orders_this_cycle=%s",
                        sell_result.success,
                        sell_result.order_id,
                        sell_result.message,
                        sell_orders_this_cycle,
                    )
                else:
                    if not can_sell:
                        logger.info(
                            "[ORDER_SKIP] side=sell reason=insufficient_holding holding_qty=%s required_qty=%s",
                            before_info.stock_quantity,
                            ORDER_QUANTITY,
                        )
                    else:
                        logger.info(
                            "[ORDER_SKIP] side=sell reason=max_sell_orders_per_cycle_reached"
                        )

                self._api_delay()

                after_info = self.account_service.get_account_info(
                    token=token,
                    symbol=SYMBOL,
                )

                logger.info(
                    "[ACCOUNT_AFTER] cash=%s holding_qty=%s",
                    after_info.cash_available,
                    after_info.stock_quantity,
                )

                logger.info(
                    "[EXECUTION_CHECK] result=%s",
                    self._confirm_execution(before_info, after_info),
                )

                logger.info("-" * 80)
                logger.info(
                    "[CYCLE_END] symbol=%s buy_orders=%s sell_orders=%s",
                    SYMBOL,
                    buy_orders_this_cycle,
                    sell_orders_this_cycle,
                )
                logger.info("-" * 80)

            except Exception as exc:
                logger.error("[CYCLE_ERROR] error=%s", exc)

            logger.info(
                "[SLEEP] next_cycle_after_seconds=%s",
                self.config.polling_interval_seconds,
            )
            logger.info("")
            time.sleep(self.config.polling_interval_seconds)