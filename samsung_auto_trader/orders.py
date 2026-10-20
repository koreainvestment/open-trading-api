"""Order placement functions."""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime

import config
from api_client import APIClient
from logger_config import logger


@dataclass
class OrderResult:
	success: bool
	message: str
	order_no: str | None = None


@dataclass
class PendingOrder:
	order_no: str
	org_no: str
	stock_code: str
	order_time: str
	unfilled_qty: int


def _to_int(value: object, default: int = 0) -> int:
	try:
		return int(str(value or default))
	except Exception:
		return default


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


def _repriced_buy_price(price: int) -> int:
	"""Move buy price one tick lower then normalize to a valid tick price."""
	if price <= 1:
		return 1
	current_tick = _krx_tick_size(price)
	next_price = max(1, price - current_tick)
	return _floor_to_tick(next_price)


def _order_payload(price: int, qty: int, stock_code: str) -> dict:
	return {
		"CANO": config.GH_ACCOUNT,
		"ACNT_PRDT_CD": config.ACNT_PRDT_CD,
		"PDNO": stock_code,
		"ORD_DVSN": config.ORD_DVSN_LIMIT,
		"ORD_QTY": str(qty),
		"ORD_UNPR": str(price),
	}


# Retry configuration for order placement
_RETRY_ERROR_CODES = {"40240000"}  # Mock trading balance not found
_TICK_ERROR_CODE = "40030000"  # Invalid tick unit price
_MAX_ORDER_RETRIES = 5
_ORDER_RETRY_DELAY_SECONDS = 2


def _execute_order_with_retry(
	client: APIClient,
	endpoint: str,
	tr_id: str,
	payload: dict,
	order_type: str,  # "Buy" or "Sell"
) -> OrderResult:
	"""Execute order with retry logic for specific error codes."""
	for attempt in range(1, _MAX_ORDER_RETRIES + 1):
		res = client.post(endpoint, tr_id, payload)
		if res.is_success():
			order_no = str((res.data.get("output") or {}).get("ODNO") or (res.data.get("output") or {}).get("odno") or "")
			return OrderResult(True, f"{order_type} order accepted", order_no or None)
		
		error_code = res.error_code()
		error_msg = res.error_message()

		if (
			order_type == "Buy"
			and error_code == _TICK_ERROR_CODE
			and attempt < _MAX_ORDER_RETRIES
		):
			old_price = _to_int(payload.get("ORD_UNPR"), 0)
			new_price = _repriced_buy_price(old_price)
			if new_price == old_price:
				logger.error(
					f"{order_type} order failed: error_code={error_code}, message={error_msg}, "
					f"price_reprice_failed={old_price}, attempt={attempt}/{_MAX_ORDER_RETRIES}"
				)
				return OrderResult(False, f"{order_type} failed: {error_msg}")

			payload["ORD_UNPR"] = str(new_price)
			logger.warning(
				f"{order_type} order tick-unit error. Repricing and retrying: "
				f"old_price={old_price}, new_price={new_price}, "
				f"attempt={attempt}/{_MAX_ORDER_RETRIES}"
			)
			continue
		
		# Check if error code warrants retry
		if error_code in _RETRY_ERROR_CODES and attempt < _MAX_ORDER_RETRIES:
			logger.warning(
				f"{order_type} order failed with error code {error_code} (mock trading balance issue). "
				f"Retrying in {_ORDER_RETRY_DELAY_SECONDS}s... (attempt {attempt}/{_MAX_ORDER_RETRIES})"
			)
			time.sleep(_ORDER_RETRY_DELAY_SECONDS)
			continue
		
		# For other errors or final retry, return failure
		logger.error(
			f"{order_type} order failed: error_code={error_code}, message={error_msg}, "
			f"attempt={attempt}/{_MAX_ORDER_RETRIES}"
		)
		return OrderResult(False, f"{order_type} failed: {error_msg}")
	
	# Should not reach here
	return OrderResult(False, f"{order_type} failed: Max retries exceeded")


def buy_limit(client: APIClient, price: int, qty: int = config.ORDER_QUANTITY) -> OrderResult:
	endpoint = "/uapi/domestic-stock/v1/trading/order-cash"
	payload = _order_payload(price=price, qty=qty, stock_code=config.STOCK_CODE)
	logger.info(f"Buy order request: qty={qty}, price={price}")
	return _execute_order_with_retry(client, endpoint, config.TR_ID_BUY_ORDER, payload, "Buy")


def sell_limit(client: APIClient, price: int, qty: int = config.ORDER_QUANTITY) -> OrderResult:
	endpoint = "/uapi/domestic-stock/v1/trading/order-cash"
	payload = _order_payload(price=price, qty=qty, stock_code=config.STOCK_CODE)
	logger.info(f"Sell order request: qty={qty}, price={price}")
	return _execute_order_with_retry(client, endpoint, config.TR_ID_SELL_ORDER, payload, "Sell")


def inquire_pending_buy_orders(client: APIClient, stock_code: str = config.STOCK_CODE) -> list[PendingOrder]:
	endpoint = "/uapi/domestic-stock/v1/trading/inquire-daily-ccld"
	today = datetime.now(tz=config.KST).strftime("%Y%m%d")
	params = {
		"CANO": config.GH_ACCOUNT,
		"ACNT_PRDT_CD": config.ACNT_PRDT_CD,
		"INQR_STRT_DT": today,
		"INQR_END_DT": today,
		"SLL_BUY_DVSN_CD": "02",
		"INQR_DVSN": "00",
		"PDNO": stock_code,
		"CCLD_DVSN": "02",
		"ORD_GNO_BRNO": "",
		"ODNO": "",
		"INQR_DVSN_3": "00",
		"INQR_DVSN_1": "",
		"CTX_AREA_FK100": "",
		"CTX_AREA_NK100": "",
	}
	res = client.get(endpoint, config.TR_ID_INQUIRE_DAILY_CCLD, params)
	if not res.is_success():
		logger.error(f"Failed to inquire pending orders: {res.error_message()}")
		return []

	pending: list[PendingOrder] = []
	for item in (res.data.get("output1") or []):
		if str(item.get("pdno") or "") != stock_code:
			continue
		unfilled_qty = _to_int(item.get("rmn_qty"))
		if unfilled_qty <= 0:
			continue
		pending.append(
			PendingOrder(
				order_no=str(item.get("odno") or ""),
				org_no=str(item.get("ord_gno_brno") or item.get("ord_orgno") or ""),
				stock_code=str(item.get("pdno") or ""),
				order_time=str(item.get("ord_tmd") or ""),
				unfilled_qty=unfilled_qty,
			)
		)
	return pending


def cancel_order(client: APIClient, order: PendingOrder) -> OrderResult:
	endpoint = "/uapi/domestic-stock/v1/trading/order-rvsecncl"
	payload = {
		"CANO": config.GH_ACCOUNT,
		"ACNT_PRDT_CD": config.ACNT_PRDT_CD,
		"KRX_FWDG_ORD_ORGNO": order.org_no,
		"ORGN_ODNO": order.order_no,
		"ORD_DVSN": config.ORD_DVSN_LIMIT,
		"RVSE_CNCL_DVSN_CD": "02",
		"ORD_QTY": "0",
		"ORD_UNPR": "0",
		"QTY_ALL_ORD_YN": "Y",
	}
	logger.info(
		f"Cancel order request: order_no={order.order_no}, org_no={order.org_no}, "
		f"unfilled_qty={order.unfilled_qty}"
	)
	res = client.post(endpoint, config.TR_ID_ORDER_CANCEL, payload)
	if not res.is_success():
		return OrderResult(False, f"Cancel failed: {res.error_message()}", order.order_no)
	return OrderResult(True, "Cancel order accepted", order.order_no)

