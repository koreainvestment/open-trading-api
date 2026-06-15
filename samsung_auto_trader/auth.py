import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from requests import RequestException, post

from samsung_auto_trader.config import config
from samsung_auto_trader.logger import logger


class TokenCache:
    def __init__(self, path: str):
        self.path = Path(path)

    def load(self) -> dict[str, Any] | None:
        if not self.path.exists():
            return None
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if raw.get("date") == datetime.now().strftime("%Y-%m-%d"):
                logger.info("Token cache loaded for today.")
                return raw
            logger.info("Token cache expired for today.")
            return None
        except Exception as exc:
            logger.warning("Failed to read token cache: %s", exc)
            return None

    def save(self, access_token: str) -> None:
        self.path.write_text(
            json.dumps({"date": datetime.now().strftime("%Y-%m-%d"), "access_token": access_token}),
            encoding="utf-8",
        )
        logger.info("Saved token cache for today.")


class KISAuth:
    TOKEN_PATH = config.token_cache_file
    TOKEN_URL = "https://openapivts.koreainvestment.com:29443/oauth2/tokenP"

    def __init__(self) -> None:
        self.cache = TokenCache(self.TOKEN_PATH)
        self.access_token = None

    def authenticate(self) -> str:
        saved = self.cache.load()
        if saved and saved.get("access_token"):
            self.access_token = saved["access_token"]
            logger.info("Reusing cached token for same day.")
            return self.access_token

        env_token = os.getenv("VTS_TOKEN") or os.getenv("GH_ACCESS_TOKEN")
        if env_token:
            self.access_token = env_token.strip()
            if self.access_token:
                logger.info("Using existing environment token.")
                self.cache.save(self.access_token)
                return self.access_token

        app_key = config.gh_appkey
        app_secret = config.gh_appsecret
        if not app_key or not app_secret:
            raise RuntimeError("Missing GH_APPKEY or GH_APPSECRET in environment variables.")

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "grant_type": "client_credentials",
            "appkey": app_key,
            "appsecret": app_secret,
        }

        try:
            response = post(self.TOKEN_URL, json=payload, timeout=15, headers=headers)
            try:
                response.raise_for_status()
            except RequestException:
                body = response.text.strip()
                sanitized_body = body if len(body) < 1000 else body[:1000] + "..."
                logger.error(
                    "Authentication tokenP request failed: status=%s body=%s",
                    response.status_code,
                    sanitized_body,
                )
                raise

            data = response.json()
            token = data.get("access_token")
            if not token:
                raise RuntimeError("Token response missing access_token.")
            self.access_token = token
            self.cache.save(token)
            logger.info("Authenticated and cached new token.")
            return token
        except RequestException as exc:
            logger.error("Authentication failed without leaking credentials: %s", exc)
            raise
