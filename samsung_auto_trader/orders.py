from typing import Any

from samsung_auto_trader.api_client import KISClient
from samsung_auto_trader.logger import logger


class OrderService:
    def __init__(self, client: KISClient, paper_trading: bool = True) -> None:
        self.client = client
        self.paper_trading = paper_trading

    def place_buy_order(self, symbol: str, quantity: int, price: int) -> dict[str, Any]:
        logger.info("Placing buy order for %s qty=%s price=%s", symbol, quantity, price)
        payload = self.client.place_order("buy", symbol, quantity, price, paper_trading=self.paper_trading)
        logger.info("Buy order response: %s", payload)
        return payload

    def place_sell_order(self, symbol: str, quantity: int, price: int) -> dict[str, Any]:
        logger.info("Placing sell order for %s qty=%s price=%s", symbol, quantity, price)
        payload = self.client.place_order("sell", symbol, quantity, price, paper_trading=self.paper_trading)
        logger.info("Sell order response: %s", payload)
        return payload
