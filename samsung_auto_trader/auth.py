from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import requests


@dataclass
class TokenCache:
    token: str
    issued_date: str

    @classmethod
    def from_file(cls, path: Path) -> "TokenCache | None":
        if not path.exists():
            return None

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

        token = str(payload.get("token", "")).strip()
        issued_date = str(payload.get("issued_date", "")).strip()
        if not token or not issued_date:
            return None
        return cls(token=token, issued_date=issued_date)

    def save(self, path: Path) -> None:
        path.write_text(
            json.dumps({"token": self.token, "issued_date": self.issued_date}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


class AuthManager:
    def __init__(
        self,
        base_url: str,
        appkey: str,
        appsecret: str,
        cache_path: Path,
        logger,
        timeout_seconds: int = 10,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.appkey = appkey
        self.appsecret = appsecret
        self.cache_path = cache_path
        self.logger = logger
        self.timeout_seconds = timeout_seconds
        self._session = requests.Session()
        self._cached_token = TokenCache.from_file(cache_path)

    def get_token(self) -> str:
        today = date.today().isoformat()
        if self._cached_token and self._cached_token.issued_date == today:
            self.logger.info("token reuse: cached token reused for %s", today)
            return self._cached_token.token

        self.logger.info("token refresh: requesting a new mock-trading token")
        token = self._request_new_token()
        self._cached_token = TokenCache(token=token, issued_date=today)
        self._cached_token.save(self.cache_path)
        self.logger.info("token refresh: token cached at %s", self.cache_path)
        return token

    def _request_new_token(self) -> str:
        url = f"{self.base_url}/oauth2/tokenP"
        payload: dict[str, Any] = {
            "grant_type": "client_credentials",
            "appkey": self.appkey,
            "appsecret": self.appsecret,
        }
        headers = {
            "content-type": "application/json",
            "accept": "text/plain",
            "charset": "UTF-8",
        }
        response = self._session.post(url, json=payload, headers=headers, timeout=self.timeout_seconds)
        response.raise_for_status()

        data = response.json()
        token = str(data.get("access_token", "")).strip()
        if not token:
            raise RuntimeError(f"Token response did not include access_token: {data}")
        return token
