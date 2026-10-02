"""Account and holdings queries."""

from __future__ import annotations

import config
from api_client import APIClient
from logger_config import logger


def inquire_balance(client: APIClient) -> dict | None:
	endpoint = "/uapi/domestic-stock/v1/trading/inquire-balance"
	params = {
		"CANO": config.GH_ACCOUNT,
		"ACNT_PRDT_CD": config.ACNT_PRDT_CD,
		"AFHR_FLPR_YN": "N",
		"FNCG_AMT_AUTO_RDPT_YN": "N",
		"FUND_STTL_ICLD_YN": "N",
		"INQR_DVSN": "01",
		"OFL_YN": "N",
		"PRCS_DVSN": "01",
		"UNPR_DVSN": "01",
		"CTX_AREA_FK100": "",
		"CTX_AREA_NK100": "",
	}
	res = client.get(endpoint, config.TR_ID_INQUIRE_BALANCE, params)
	if not res.is_success():
		logger.error(f"Failed to inquire balance: {res.error_message()}")
		return None
	return res.data


def samsung_qty(balance_data: dict, stock_code: str = config.STOCK_CODE) -> int:
	for item in balance_data.get("output1", []) or []:
		if str(item.get("pdno")) == stock_code:
			return int(str(item.get("hldg_qty", "0")))
	return 0


def samsung_avg_price(balance_data: dict, stock_code: str = config.STOCK_CODE) -> int:
	for item in balance_data.get("output1", []) or []:
		if str(item.get("pdno")) != stock_code:
			continue
		for key in ("pchs_avg_pric", "pchs_avg_pricn", "pchs_unpr"):
			value = str(item.get(key, "")).strip()
			if not value:
				continue
			try:
				price = int(float(value))
				if price > 0:
					return price
			except ValueError:
				continue
	return 0


def available_cash(balance_data: dict) -> int:
	output2 = balance_data.get("output2", []) or []
	if not output2:
		return 0
	return int(str(output2[0].get("dnca_tot_amt", "0")))

