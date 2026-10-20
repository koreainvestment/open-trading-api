"""Token auth and cache handling."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import requests

import config
from logger_config import logger


def _parse_expiry(expiry_raw: str | None) -> datetime:
	if not expiry_raw:
		return datetime.now() + timedelta(hours=23)
	# KIS format: YYYY-MM-DD HH:MM:SS
	return datetime.strptime(expiry_raw, "%Y-%m-%d %H:%M:%S")


def load_cached_token() -> str | None:
	path = Path(config.TOKEN_CACHE_FILE)
	if not path.exists():
		return None
	try:
		data = json.loads(path.read_text(encoding="utf-8"))
		token = data.get("token")
		exp = data.get("expiry")
		if not token or not exp:
			return None
		exp_dt = datetime.fromisoformat(exp)
		if datetime.now() < exp_dt - timedelta(minutes=1):
			logger.info("Token reused from cache")
			return token
	except Exception as exc:
		logger.warning(f"Token cache read failed: {exc}")
	return None


def save_cached_token(token: str, expiry: datetime) -> None:
	data: dict[str, Any] = {"token": token, "expiry": expiry.isoformat()}
	Path(config.TOKEN_CACHE_FILE).write_text(
		json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
	)
	logger.info(f"Token cached to {config.TOKEN_CACHE_FILE}")


def request_new_token() -> str | None:
	url = f"{config.API_BASE_URL}/oauth2/tokenP"
	headers = {"Content-Type": "application/json"}
	payload = {
		"grant_type": "client_credentials",
		"appkey": config.GH_APPKEY,
		"appsecret": config.GH_APPSECRET,
	}
	try:
		logger.info("Requesting new authentication token...")
		res = requests.post(url, headers=headers, json=payload, timeout=config.REQUEST_TIMEOUT)
		res.raise_for_status()
		body = res.json()
		token = body.get("access_token")
		expiry = _parse_expiry(body.get("access_token_token_expired"))
		if not token:
			logger.error("Authentication response missing access_token")
			return None
		logger.info(f"Authentication successful (token expires: {expiry:%Y-%m-%d %H:%M:%S})")
		save_cached_token(token, expiry)
		return token
	except Exception as exc:
		logger.error(f"Authentication failed: {exc}")
		return None


def get_token() -> str | None:
	config.validate_credentials()
	cached = load_cached_token()
	if cached:
		return cached
	return request_new_token()

