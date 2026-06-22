from typing import Dict, Optional

from api_client import ApiClient
from config import ENDPOINTS
from logger import get_logger

logger = get_logger(__name__)


def parse_price_response(response: Dict[str, object]) -> Optional[int]:
    output = response.get("output")
    if isinstance(output, dict):
        return int(output.get("stck_prpr", 0) or 0)
    if isinstance(output, list) and output:
        item = output[0]
        if isinstance(item, dict):
            return int(item.get("stck_prpr", 0) or 0)
    return None


class MarketDataService:
    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def get_current_price(self, token: str, symbol: str) -> int:
        logger.info("Fetching current price for %s", symbol)
        params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": symbol}
        response = self.api_client.request(
            method="GET",
            path=ENDPOINTS["price_inquiry"],
            token=token,
            params=params,
            tr_id="FHKST01010100",
            )
        price = parse_price_response(response)
        if price is None or price <= 0:
            raise ValueError("Failed to parse market price for symbol %s" % symbol)

        logger.info("Current price for %s is %s KRW", symbol, price)
        return price
