import time
from typing import Any, Dict, Optional

import requests
from requests.exceptions import RequestException, Timeout

from config import AppConfig
from logger import get_logger

logger = get_logger(__name__)


class ApiClient:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.session = requests.Session()

    def request(
        self,
        method: str,
        path: str,
        token: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        tr_id: Optional[str] = None,
        timeout: int = 10,
    ) -> Dict[str, Any]:
        url = f"{self.config.base_url}{path}"

        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {token}",
            "appkey": self.config.app_key,
            "appsecret": self.config.app_secret,
        }

        if tr_id:
            headers["tr_id"] = tr_id

        last_response = None

        try:
            for attempt in range(3):
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_body,
                    timeout=timeout,
                )

                last_response = response

                # JSON 응답 파싱 시도
                try:
                    data = response.json()
                except ValueError:
                    data = {}

                rt_cd = data.get("rt_cd")
                msg_cd = data.get("msg_cd")
                msg1 = data.get("msg1") or data.get("message")

                # 초당 거래건수 초과 처리
                if msg_cd == "EGW00201" or "EGW00201" in response.text:
                    wait_seconds = 2 + attempt
                    logger.warning(
                        "[API_RATE_LIMIT] method=%s path=%s msg=%s retry_after=%ss attempt=%s/3",
                        method,
                        path,
                        msg1 or "초당 거래건수 초과",
                        wait_seconds,
                        attempt + 1,
                    )
                    time.sleep(wait_seconds)
                    continue

                # HTTP 에러 처리
                if response.status_code >= 400:
                    logger.error(
                        "[API_HTTP_ERROR] method=%s path=%s status=%s msg_cd=%s msg=%s",
                        method,
                        path,
                        response.status_code,
                        msg_cd,
                        msg1 or response.text[:300],
                    )
                    response.raise_for_status()

                # 한국투자 업무 실패 처리: HTTP 200이어도 rt_cd가 1이면 실패
                if rt_cd == "1":
                    logger.warning(
                        "[API_BUSINESS_FAIL] method=%s path=%s tr_id=%s msg_cd=%s msg=%s",
                        method,
                        path,
                        tr_id,
                        msg_cd,
                        msg1,
                    )
                    return data

                logger.info(
                    "[API_OK] method=%s path=%s tr_id=%s",
                    method,
                    path,
                    tr_id,
                )

                return data

            # 3번 재시도 후에도 rate limit이면 실패 처리
            if last_response is not None:
                try:
                    data = last_response.json()
                except ValueError:
                    data = {}

                logger.error(
                    "[API_FAILED_AFTER_RETRY] method=%s path=%s status=%s body=%s",
                    method,
                    path,
                    last_response.status_code,
                    last_response.text[:300],
                )

                last_response.raise_for_status()
                return data

            raise RuntimeError("API request failed without a response.")

        except Timeout:
            logger.error("[API_TIMEOUT] method=%s path=%s", method, path)
            raise

        except RequestException as exc:
            body = None

            try:
                body = last_response.text if last_response is not None else None
            except Exception:
                pass

            logger.error(
                "[API_REQUEST_EXCEPTION] method=%s path=%s error=%s body=%s",
                method,
                path,
                exc,
                body[:300] if body else None,
            )
            raise