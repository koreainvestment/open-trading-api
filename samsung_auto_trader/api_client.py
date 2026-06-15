from __future__ import annotations

import time
from typing import Any

import requests

from samsung_auto_trader.auth import KISAuth
from samsung_auto_trader.config import config
from samsung_auto_trader.logger import logger


class KISClient:
    BASE_URL = "https://openapivts.koreainvestment.com:29443"

    def __init__(self) -> None:
        self.auth = KISAuth()
        self.token = self.auth.authenticate()

    def _get_headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "authorization": f"Bearer {self.token}",
            "appkey": config.gh_appkey,
            "appsecret": config.gh_appsecret,
        }
        if extra:
            headers.update(extra)
        return headers

    def _request(self, method: str, path: str, params: dict[str, Any] | None = None, data: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.BASE_URL}{path}"
        headers = self._get_headers()
        for attempt in range(config.max_retries + 1):
            try:
                if method == "GET":
                    response = requests.get(url, headers=headers, params=params, timeout=config.order_timeout_seconds)
                else:
                    response = requests.post(url, headers=headers, json=data, timeout=config.order_timeout_seconds)
                response.raise_for_status()
                payload = response.json()
                if payload.get("rt_cd") not in (None, "0", 0):
                    logger.warning("API returned non-zero rt_cd: %s path=%s params=%s", payload.get("rt_cd"), path, params or data)
                return payload
            except requests.Timeout:
                logger.warning("Request timeout on %s %s attempt %d.", method, url, attempt + 1)
            except requests.HTTPError as exc:
                logger.error("HTTP error for %s %s: %s", method, url, exc)
                if response.status_code == 401 and attempt == 0:
                    self.token = self.auth.authenticate()
                    headers["authorization"] = f"Bearer {self.token}"
                    continue
                raise
            except Exception as exc:
                logger.error("Request failure for %s %s: %s", method, url, exc)
            if attempt < config.max_retries:
                logger.info("Retrying %s %s after delay.", method, url)
                time.sleep(config.retry_interval_seconds)
        raise RuntimeError(f"Failed API request after retries: {path}")

    def get_price(self, symbol: str) -> dict[str, Any]:
        path = "/uapi/domestic-stock/v1/quotations/inquire-price"
        params = {
            "FID_COND_MRKT_DIV_CODE": config.market_division_code,
            "FID_INPUT_ISCD": symbol,
        }
        payload = self._request("GET", path, params=params)
        return payload

    def get_balance(self) -> dict[str, Any]:
        path = "/uapi/domestic-stock/v1/trading/inquire-balance"
        params = {
            "CANO": config.gh_account,
            "ACNT_PRDT_CD": config.gh_product_code,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "00",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "00",
        }
        payload = self._request("GET", path, params=params)
        return payload

    def place_order(self, action: str, symbol: str, quantity: int, price: int, paper_trading: bool = True) -> dict[str, Any]:
        path = "/uapi/domestic-stock/v1/trading/order-cash"
        if action == "buy":
            tr_id = "VTTC0802U" if paper_trading else "TTTC0802U"
        else:
            tr_id = "VTTC0801U" if paper_trading else "TTTC0801U"
        data = {
            "CANO": config.gh_account,
            "ACNT_PRDT_CD": config.gh_product_code,
            "PDNO": symbol,
            "ORD_DVSN": "00",
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price),
        }
        headers = {"tr_id": tr_id, "custtype": "P", "tr_cont": ""}
        url = f"{self.BASE_URL}{path}"
        response = requests.post(url, headers={**self._get_headers(), **headers}, json=data, timeout=config.order_timeout_seconds)
        response.raise_for_status()
        return response.json()
