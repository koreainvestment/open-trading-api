import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import requests

from config import AppConfig, TOKEN_CACHE_FILE
from logger import get_logger

logger = get_logger(__name__)


@dataclass
class TokenData:
    access_token: str
    issued_at: datetime
    expires_in: int


def load_cached_token() -> Optional[TokenData]:
    if not TOKEN_CACHE_FILE.exists():
        return None

    try:
        raw = json.loads(TOKEN_CACHE_FILE.read_text())
        issued_at = datetime.fromisoformat(raw["issued_at"])
        expires_in = int(raw.get("expires_in", 0))
        if datetime.now(timezone.utc) < issued_at + timedelta(seconds=expires_in - 30):
            logger.info("Reusing cached token from token cache.")
            return TokenData(access_token=raw["access_token"], issued_at=issued_at, expires_in=expires_in)
        logger.info("Cached token has expired or is close to expiration.")
    except (ValueError, KeyError, OSError) as exc:
        logger.warning("Unable to load token cache: %s", exc)

    return None


def save_cached_token(token: str, expires_in: int) -> None:
    payload = {
        "access_token": token,
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "expires_in": expires_in,
    }
    TOKEN_CACHE_FILE.write_text(json.dumps(payload, indent=2))
    logger.info("Saved new access token to cache.")


def request_new_token(config: AppConfig) -> TokenData:
    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "grant_type": "client_credentials",
        "appkey": config.app_key.strip(),
        "appsecret": config.app_secret.strip(),
    }

    response = requests.post(
        config.token_url,
        headers=headers,
        json=payload,
        timeout=10,
    )

    print("TOKEN URL:", config.token_url)
    print("TOKEN STATUS:", response.status_code)
    print("TOKEN RESPONSE:", response.text)

    response.raise_for_status()
    data = response.json()

    access_token = data.get("access_token") or data.get("accessToken")
    expires_in = int(data.get("expires_in", 3600))

    if not access_token:
        raise ValueError("Token response did not contain access_token")

    logger.info("Fetched a new access token from KIS Open API.")
    save_cached_token(access_token, expires_in)

    return TokenData(
        access_token=access_token,
        issued_at=datetime.now(timezone.utc),
        expires_in=expires_in,
    )


def get_access_token(config: AppConfig) -> str:
    token = load_cached_token()
    if token is not None:
        return token.access_token
    token = request_new_token(config)
    return token.access_token
