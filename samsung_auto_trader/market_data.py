"""Market data requests."""

from __future__ import annotations

import config
from api_client import APIClient
from logger_config import logger


def _krx_tick_size(price: int) -> int:
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


def _floor_to_tick(price: int) -> int:
	tick = _krx_tick_size(price)
	return max(tick, (price // tick) * tick)


def _ceil_to_tick(price: int) -> int:
	tick = _krx_tick_size(price)
	return ((price + tick - 1) // tick) * tick


def get_current_price(client: APIClient, stock_code: str = config.STOCK_CODE) -> int | None:
	endpoint = "/uapi/domestic-stock/v1/quotations/inquire-price"
	params = {
		"FID_COND_MRKT_DIV_CODE": "J",
		"FID_INPUT_ISCD": stock_code,
	}
	res = client.get(endpoint, config.TR_ID_GET_PRICE, params)
	if not res.is_success():
		logger.error(f"Failed to get price: {res.error_message()}")
		return None
	try:
		price = int(str(res.data.get("output", {}).get("stck_prpr", "0")))
		if price <= 0:
			logger.error(f"Invalid price response: {res.data}")
			return None
		logger.info(f"Current price for {stock_code}: {price:,} KRW")
		return price
	except Exception as exc:
		logger.error(f"Price parse error: {exc}")
		return None


def calc_buy_price(current_price: int) -> int:
	raw_price = max(1, current_price - config.PRICE_OFFSET)
	return _floor_to_tick(raw_price)


def calc_sell_price(current_price: int) -> int:
	raw_price = max(1, current_price + config.PRICE_OFFSET)
	return _ceil_to_tick(raw_price)

