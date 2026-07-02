"""Trading loop orchestration."""

from __future__ import annotations

import time
from datetime import datetime

import config
from account import available_cash, inquire_balance, samsung_avg_price, samsung_qty
from api_client import APIClient
from logger_config import logger
from market_data import calc_buy_price, calc_sell_price, get_current_price
from orders import PendingOrder, buy_limit, cancel_order, inquire_pending_buy_orders, sell_limit


def _wait_for_buy_execution(client: APIClient, before_qty: int) -> tuple[bool, int | None, dict | None]:
	deadline = time.time() + config.BUY_EXECUTION_WAIT_SECONDS
	last_qty = before_qty
	last_balance = None

	while time.time() <= deadline:
		balance = inquire_balance(client)
		if balance is not None:
			last_balance = balance
			last_qty = samsung_qty(balance)
			if last_qty > before_qty:
				return True, last_qty, balance
		time.sleep(config.BUY_EXECUTION_POLL_SECONDS)

	return False, last_qty, last_balance


def _pending_order_age_seconds(order: PendingOrder) -> int | None:
	if len(order.order_time) < 6 or not order.order_time.isdigit():
		return None
	now = config.now_kst()
	try:
		order_dt = datetime(
			year=now.year,
			month=now.month,
			day=now.day,
			hour=int(order.order_time[0:2]),
			minute=int(order.order_time[2:4]),
			second=int(order.order_time[4:6]),
			tzinfo=config.KST,
		)
		age = int((now - order_dt).total_seconds())
		return max(0, age)
	except ValueError:
		return None


def _handle_pending_buy_orders(client: APIClient) -> bool:
	pending_orders = inquire_pending_buy_orders(client)
	if not pending_orders:
		return False

	logger.info(f"Pending buy orders detected: count={len(pending_orders)}")
	for pending in pending_orders:
		age = _pending_order_age_seconds(pending)
		if age is not None and age >= config.PENDING_CANCEL_AFTER_SECONDS:
			cancel_res = cancel_order(client, pending)
			logger.info(
				f"Cancel result: success={cancel_res.success}, order_no={cancel_res.order_no}, "
				f"msg={cancel_res.message}"
			)
		else:
			age_text = "unknown" if age is None else str(age)
			logger.info(
				f"Pending buy order not stale yet: order_no={pending.order_no}, "
				"skipping new buy this cycle, "
				f"age_seconds={age_text}, cancel_after={config.PENDING_CANCEL_AFTER_SECONDS}"
			)

	remaining = inquire_pending_buy_orders(client)
	if remaining:
		logger.info(f"Pending buy orders remain: count={len(remaining)}. Skipping new buy this cycle.")
		return True

	return False


def run(client: APIClient) -> None:
	logger.info(f"Starting trading loop for {config.STOCK_CODE}")
	logger.info(
		f"Trading window (KST): {config.TRADING_START.strftime('%H:%M')} - {config.TRADING_END.strftime('%H:%M')}"
	)
	logger.info(f"Polling interval: {config.POLLING_INTERVAL} seconds")
	logger.info(
		"Pending-order guard enabled: "
		f"cancel_after={config.PENDING_CANCEL_AFTER_SECONDS}s"
	)
	logger.info(
		"Risk guard enabled: "
		f"max_holdings={config.MAX_HOLDINGS_QTY}, "
		f"consecutive_buy_limit={config.CONSECUTIVE_BUY_LIMIT}, "
		f"buy_pause={config.BUY_PAUSE_SECONDS}s"
	)
	local_pending_buy_since: float | None = None
	consecutive_buy_exec_count = 0
	buy_pause_until = 0.0
	last_verified_qty = 0

	while True:
		now = config.now_kst()
		if now.time() > config.TRADING_END:
			logger.info("Trading window ended. Stopping trader.")
			return

		if not config.is_within_trading_window(now):
			time.sleep(20)
			continue

		before = inquire_balance(client)
		if before is None:
			logger.error("Failed to fetch holdings before order")
			time.sleep(config.POLLING_INTERVAL)
			continue
		before_qty = samsung_qty(before)
		last_verified_qty = before_qty
		avg_price = samsung_avg_price(before)
		logger.info(f"Holdings before order: samsung_qty={before_qty}, cash={available_cash(before):,}")

		current = get_current_price(client)
		if current is None:
			logger.error("Failed to get current price, skipping iteration")
			time.sleep(config.POLLING_INTERVAL)
			continue

		if before_qty > 0 and avg_price > 0:
			target_sell_price = calc_sell_price(avg_price)
			if current >= target_sell_price:
				sell_qty_now = min(config.ORDER_QUANTITY, before_qty)
				logger.info(
					f"Take-profit condition met: current={current:,}, "
					f"avg_price={avg_price:,}, target={target_sell_price:,}, qty={sell_qty_now}"
				)
				sell_res_now = sell_limit(client, target_sell_price, qty=sell_qty_now)
				logger.info(
					f"Sell result: success={sell_res_now.success}, "
					f"order_no={sell_res_now.order_no}, msg={sell_res_now.message}"
				)
				if sell_res_now.success:
					updated_balance = inquire_balance(client)
					if updated_balance is not None:
						before = updated_balance
						before_qty = samsung_qty(updated_balance)
						avg_price = samsung_avg_price(updated_balance)
						last_verified_qty = before_qty
				time.sleep(1)

		now_ts = time.time()
		if now_ts < buy_pause_until:
			remaining = int(buy_pause_until - now_ts)
			logger.info(
				"Consecutive-buy cooldown active. "
				f"Skipping new buy this cycle, remaining={remaining}s"
			)
			time.sleep(config.POLLING_INTERVAL)
			continue

		if before_qty >= config.MAX_HOLDINGS_QTY:
			logger.info(
				f"Max holdings reached: samsung_qty={before_qty}, "
				f"limit={config.MAX_HOLDINGS_QTY}. Skipping new buy this cycle."
			)
			time.sleep(config.POLLING_INTERVAL)
			continue

		if local_pending_buy_since is not None:
			elapsed = int(time.time() - local_pending_buy_since)
			if elapsed < config.PENDING_CANCEL_AFTER_SECONDS:
				logger.info(
					"Local pending-buy cooldown active. "
					f"Skipping new buy this cycle, elapsed={elapsed}s, "
					f"cooldown={config.PENDING_CANCEL_AFTER_SECONDS}s"
				)
				time.sleep(config.POLLING_INTERVAL)
				continue
			local_pending_buy_since = None

		if _handle_pending_buy_orders(client):
			time.sleep(config.POLLING_INTERVAL)
			continue

		# Re-verify holdings immediately before buy order to prevent race conditions
		pre_buy_check = inquire_balance(client)
		if pre_buy_check is None:
			logger.warning("Failed to verify holdings before buy order, skipping this cycle")
			time.sleep(config.POLLING_INTERVAL)
			continue
		pre_buy_qty = samsung_qty(pre_buy_check)
		if pre_buy_qty != before_qty:
			logger.warning(
				f"Holdings changed since loop start: was {before_qty}, now {pre_buy_qty}. "
				"Restarting loop iteration for safety."
			)
			continue
		if pre_buy_qty >= config.MAX_HOLDINGS_QTY:
			logger.warning(
				f"Holdings at limit before buy order: samsung_qty={pre_buy_qty}, "
				f"limit={config.MAX_HOLDINGS_QTY}. Skipping new buy this cycle."
			)
			time.sleep(config.POLLING_INTERVAL)
			continue

		buy_price = calc_buy_price(current)
		sell_price = calc_sell_price(current)
		logger.info(
			f"Computed order prices: current={current:,}, buy_price={buy_price}, sell_price={sell_price}"
		)

		buy_res = buy_limit(client, buy_price)
		logger.info(f"Buy result: success={buy_res.success}, order_no={buy_res.order_no}, msg={buy_res.message}")
		if not buy_res.success:
			consecutive_buy_exec_count = 0
			time.sleep(config.POLLING_INTERVAL)
			continue
		local_pending_buy_since = time.time()

		executed, mid_qty, mid_balance = _wait_for_buy_execution(client, before_qty)
		if mid_qty is None:
			logger.info("Holdings after buy: samsung_qty=unknown, executed=False")
		else:
			logger.info(f"Holdings after buy: samsung_qty={mid_qty}, executed={executed}")

		if not executed:
			consecutive_buy_exec_count = 0
			logger.info("Buy order not executed within wait window. Skipping sell order this cycle.")
			time.sleep(config.POLLING_INTERVAL)
			continue
		
		# CRITICAL: Verify limit after execution to ensure we don't exceed MAX_HOLDINGS_QTY
		if mid_qty is not None and mid_qty > config.MAX_HOLDINGS_QTY:
			logger.error(
				f"CRITICAL: Holdings exceed limit after buy execution! "
				f"samsung_qty={mid_qty}, limit={config.MAX_HOLDINGS_QTY}. "
				f"This indicates either API race condition, stale balance data, or external order. "
				f"Attempting emergency sell."
			)
			# Attempt to reduce down to limit by selling excess
			excess_qty = mid_qty - config.MAX_HOLDINGS_QTY
			sell_to_limit = max(0, min(config.ORDER_QUANTITY, excess_qty))
			if sell_to_limit > 0:
				logger.warning(f"Emergency sell to reduce excess: qty={sell_to_limit}")
				current_market_price = get_current_price(client)
				if current_market_price is not None:
					emergency_sell_res = sell_limit(client, current_market_price, qty=sell_to_limit)
					logger.info(
						f"Emergency sell result: success={emergency_sell_res.success}, "
						f"order_no={emergency_sell_res.order_no}, msg={emergency_sell_res.message}"
					)
					time.sleep(1)
			consecutive_buy_exec_count = 0
			time.sleep(config.POLLING_INTERVAL)
			continue
		
		local_pending_buy_since = None
		consecutive_buy_exec_count += 1
		if consecutive_buy_exec_count >= config.CONSECUTIVE_BUY_LIMIT:
			buy_pause_until = time.time() + config.BUY_PAUSE_SECONDS
			logger.info(
				"Consecutive buy limit reached. "
				f"Pausing new buys for {config.BUY_PAUSE_SECONDS}s"
			)
			consecutive_buy_exec_count = 0

		sell_qty = max(0, (mid_qty or 0) - before_qty)
		if sell_qty <= 0:
			consecutive_buy_exec_count = 0
			logger.info("No newly bought quantity available for sell. Skipping sell order this cycle.")
			time.sleep(config.POLLING_INTERVAL)
			continue

		sell_res = sell_limit(client, sell_price, qty=sell_qty)
		logger.info(f"Sell result: success={sell_res.success}, order_no={sell_res.order_no}, msg={sell_res.message}")
		time.sleep(1)

		after = inquire_balance(client)
		if after is None:
			after = mid_balance
		if after is not None:
			after_qty = samsung_qty(after)
			logger.info(f"Holdings after sell: samsung_qty={after_qty}, cash={available_cash(after):,}")

		time.sleep(config.POLLING_INTERVAL)

