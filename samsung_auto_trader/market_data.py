from typing import Any

from samsung_auto_trader.api_client import KISClient
from samsung_auto_trader.logger import logger


class MarketDataService:
    def __init__(self, client: KISClient) -> None:
        self.client = client

    def get_current_price(self, symbol: str) -> int | None:
        logger.info("Requesting current price for %s", symbol)
        payload = self.client.get_price(symbol)
        output = payload.get("output")
        if isinstance(output, list) and output:
            output = output[0]
        if not isinstance(output, dict):
            logger.error("Unexpected price payload format: %s", payload)
            return None
        price = output.get("stck_prpr") or output.get("prpr")
        if price is None:
            logger.error("Price field missing in price response: %s", output)
            return None
        try:
            return int(price)
        except (TypeError, ValueError):
            logger.error("Price conversion failed for price: %s", price)
            return None
