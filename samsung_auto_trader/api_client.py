# 한국투자 API 요청을 공통 처리하는 파일

import time
from typing import Any, Dict, Optional

import requests

from config import (
    APP_KEY,
    APP_SECRET,
    MAX_RETRIES,
    REQUEST_TIMEOUT_SECONDS,
    RETRY_SLEEP_SECONDS,
)


class KisApiClient:
    def __init__(
        self,
        base_url: str,
        access_token: str,
        logger=None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.logger = logger

    # 한국투자 API 요청에 필요한 header 생성
    def _headers(self, tr_id: str, tr_cont: str = "") -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "appkey": APP_KEY,
            "appsecret": APP_SECRET,
            "tr_id": tr_id,
            "tr_cont": tr_cont,
            "custtype": "P",
        }

    # GET 방식 API 요청을 보낸다. 현재가 조회, 잔고조회 등에 사용
    def get(
        self,
        path: str,
        tr_id: str,
        params: Dict[str, Any],
        tr_cont: str = "",
    ) -> Dict[str, Any]:
        return self._request(
            method="GET",
            path=path,
            tr_id=tr_id,
            params=params,
            tr_cont=tr_cont,
        )

    # POST 방식 API 요청을 보낸다. 매수 주문, 매도 주문 등에 사용
    def post(
        self,
        path: str,
        tr_id: str,
        data: Dict[str, Any],
        tr_cont: str = "",
    ) -> Dict[str, Any]:
        return self._request(
            method="POST",
            path=path,
            tr_id=tr_id,
            json_data=data,
            tr_cont=tr_cont,
        )

    # 요청 실패 시 몇 번 재시도한다. timeout, API error, 서버 지연 등을 처리한다.
    def _request(
        self,
        method: str,
        path: str,
        tr_id: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        tr_cont: str = "",
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers = self._headers(tr_id=tr_id, tr_cont=tr_cont)

        last_error = None

        for attempt in range(1, MAX_RETRIES + 2):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )

                response.raise_for_status()
                result = response.json()

                rt_cd = result.get("rt_cd")
                if rt_cd not in (None, "0"):
                    raise RuntimeError(f"KIS API error: {result}")

                return result

            except Exception as e:
                last_error = e
                if self.logger:
                    self.logger.warning(
                        "API request failed. attempt=%s error=%s",
                        attempt,
                        e,
                    )

                if attempt <= MAX_RETRIES:
                    time.sleep(RETRY_SLEEP_SECONDS)

        raise RuntimeError(f"API request finally failed: {last_error}")
