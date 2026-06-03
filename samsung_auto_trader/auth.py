import json
from datetime import date
from typing import Optional

import requests

from config import (
    APP_KEY,
    APP_SECRET,
    MOCK_BASE_URL,
    PATH_TOKEN,
    TOKEN_CACHE_FILE,
    REQUEST_TIMEOUT_SECONDS,
)


def load_cached_token() -> Optional[str]:
    if not TOKEN_CACHE_FILE.exists():
        return None

    try:
        with open(TOKEN_CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if data.get("created_date") == date.today().isoformat():
            return data.get("access_token")

        return None
    except Exception:
        return None


def save_token(access_token: str) -> None:
    data = {
        "access_token": access_token,
        "created_date": date.today().isoformat(),
    }

    with open(TOKEN_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def issue_new_token() -> str:
    url = f"{MOCK_BASE_URL}{PATH_TOKEN}"

    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
    }

    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json=body,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    data = response.json()
    access_token = data.get("access_token")

    if not access_token:
        raise RuntimeError(f"Token issue failed: {data}")

    save_token(access_token)
    return access_token


def get_access_token(logger=None) -> str:
    cached = load_cached_token()

    if cached:
        if logger:
            logger.info("Reusing cached access token for today.")
        return cached

    if logger:
        logger.info("No valid cached token. Issuing new access token.")

    return issue_new_token()
