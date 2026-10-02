"""HTTP client for KIS API with retry and safe parsing."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import requests

import config
from logger_config import logger


@dataclass
class APIResponse:
	status_code: int
	data: dict[str, Any]
	raw_text: str = ""

	def is_success(self) -> bool:
		if self.status_code != 200:
			return False
		return str(self.data.get("rt_cd", "1")) == "0"

	def error_code(self) -> str:
		return str(self.data.get("msg_cd") or self.data.get("rt_cd") or "UNKNOWN")

	def error_message(self) -> str:
		if self.data.get("msg1"):
			return str(self.data["msg1"])
		if self.raw_text:
			return self.raw_text[:300]
		return "No error message"


class APIClient:
	def __init__(self, token: str):
		self.base_url = config.API_BASE_URL
		self.token = token
		self._last_request_ts = 0.0

	def _convert_tr_id_for_mock(self, tr_id: str) -> str:
		# In mock env, many trading TRs use V-prefixed ids.
		if "openapivts" in self.base_url and tr_id and tr_id[0] in ("T", "J", "C"):
			return "V" + tr_id[1:]
		return tr_id

	def _headers(self, tr_id: str) -> dict[str, str]:
		return {
			"Content-Type": "application/json",
			"Accept": "application/json",
			"authorization": f"Bearer {self.token}",
			"appkey": config.GH_APPKEY,
			"appsecret": config.GH_APPSECRET,
			"tr_id": self._convert_tr_id_for_mock(tr_id),
			"custtype": "P",
		}

	def _throttle(self) -> None:
		now = time.time()
		elapsed = now - self._last_request_ts
		if elapsed < config.API_MIN_REQUEST_INTERVAL_SECONDS:
			time.sleep(config.API_MIN_REQUEST_INTERVAL_SECONDS - elapsed)

	def _is_rate_limited(self, response: APIResponse) -> bool:
		message = response.error_message()
		return "초당 거래건수를 초과" in message or response.status_code == 429

	def _request(
		self,
		method: str,
		endpoint: str,
		tr_id: str,
		*,
		params: dict[str, Any] | None = None,
		body: dict[str, Any] | None = None,
	) -> APIResponse:
		url = f"{self.base_url}{endpoint}"
		headers = self._headers(tr_id)

		for attempt in range(1, config.MAX_RETRIES + 1):
			try:
				self._throttle()
				if method == "GET":
					res = requests.get(url, headers=headers, params=params, timeout=config.REQUEST_TIMEOUT)
				else:
					res = requests.post(url, headers=headers, json=body, timeout=config.REQUEST_TIMEOUT)
				self._last_request_ts = time.time()

				text = res.text or ""
				try:
					data = res.json()
				except Exception:
					data = {}

				response = APIResponse(status_code=res.status_code, data=data, raw_text=text)
				if response.is_success():
					return response

				logger.error(
					f"API call failed: {endpoint} | Status: {response.status_code} | "
					f"Error Code: {response.error_code()} | Message: {response.error_message()}"
				)
				if self._is_rate_limited(response):
					if attempt < config.MAX_RETRIES:
						time.sleep(config.RATE_LIMIT_BACKOFF_SECONDS)
						continue
					return response
				if response.status_code < 500 and response.status_code != 429:
					return response
			except requests.RequestException as exc:
				logger.error(f"Request error: {endpoint} | {exc}")

			if attempt < config.MAX_RETRIES:
				time.sleep(config.RETRY_BACKOFF_SECONDS)

		return APIResponse(status_code=599, data={"rt_cd": "1", "msg1": "Request failed after retries"})

	def get(self, endpoint: str, tr_id: str, params: dict[str, Any]) -> APIResponse:
		return self._request("GET", endpoint, tr_id, params=params)

	def post(self, endpoint: str, tr_id: str, body: dict[str, Any]) -> APIResponse:
		return self._request("POST", endpoint, tr_id, body=body)

