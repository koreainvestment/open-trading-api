# 한국투자 API는 요청할 때마다 access token이 필요하기에 API 접근 토큰 관리
# 모의투자 API는 호출 제한이 낮고 토큰을 매번 새로 발급하면 불필요한 API 호출 증가하기에 사용
# 한국투자 API의 토큰 발급 API를 계속 호출하지 않고 하루에 한 번만 발급받고 나머지는 token_cache.json에서 재사용하는 것

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

#token_cache.json에 저장된 토큰이 오늘 발급된 것인지 확인하고 유효하면 반환
def load_cached_token() -> Optional[str]:
    # 파일 존재 여부 확인
    if not TOKEN_CACHE_FILE.exists():
        return None

    try:
        with open(TOKEN_CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 오늘 발급 토큰인지 확인
        if data.get("created_date") == date.today().isoformat():
            return data.get("access_token")
            
        return None
    except Exception:
        return None


# 새로 발급받은 토큰을 token_cache.json에 저장
def save_token(access_token: str) -> None:
    data = {
        "access_token": access_token,
        "created_date": date.today().isoformat(),
    }

    # w = overwrite, 기존파일 덮어쓰기. indent=들여쓰기
    with open(TOKEN_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 한국투자 API에 새 access token 발급 요청
def issue_new_token() -> str:
    url = f"{MOCK_BASE_URL}{PATH_TOKEN}"

    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
    }

    # 실제 http post요청
    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json=body,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    #HTTP 오류 확인
    response.raise_for_status()

    data = response.json()
    access_token = data.get("access_token")

    if not access_token:
        raise RuntimeError(f"Token issue failed: {data}")

    save_token(access_token)
    return access_token


def get_access_token(logger=None) -> str:
    cached = load_cached_token()

    # API 호출 안 하고 토큰 재사용
    if cached:
        if logger:
            logger.info("토큰을 재사용 합니다.")
        return cached

    if logger:
        logger.info("새로운 토큰을 발급합니다.") 

    return issue_new_token()
