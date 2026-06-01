from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

import requests

try:
    from .auth import AuthManager
except ImportError:  # pragma: no cover
    from auth import AuthManager


@dataclass
class KISResult:
    status_code: int
    data: dict[str, Any]

    @property
    def ok(self) -> bool:
        rt_cd = str(self.data.get("rt_cd", "0"))
        return self.status_code == 200 and rt_cd == "0"


class KISApiClient:
    def __init__(
        self,
        base_url: str,
        appkey: str,
        appsecret: str,
        auth_manager: AuthManager,
        logger,
        timeout_seconds: int = 10,
        retry_count: int = 2,
        retry_backoff_seconds: float = 2.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.appkey = appkey
        self.appsecret = appsecret
        self.auth_manager = auth_manager
        self.logger = logger
        self.timeout_seconds = timeout_seconds
        self.retry_count = retry_count
        self.retry_backoff_seconds = retry_backoff_seconds
        self._session = requests.Session()

    def get(self, path: str, tr_id: str, params: dict[str, Any], tr_cont: str = "") -> dict[str, Any]:
        return self._request("GET", path, tr_id, params=params, tr_cont=tr_cont)

    def post(
        self,
        path: str,
        tr_id: str,
        body: dict[str, Any],
        tr_cont: str = "",
        use_hashkey: bool = True,
    ) -> dict[str, Any]:
        return self._request("POST", path, tr_id, body=body, tr_cont=tr_cont, use_hashkey=use_hashkey)

    def get_hashkey(self, body: dict[str, Any]) -> str:
        url = f"{self.base_url}/uapi/hashkey"
        headers = {
            "content-type": "application/json",
            "accept": "text/plain",
            "charset": "UTF-8",
            "appkey": self.appkey,
            "appsecret": self.appsecret,
        }
        response = self._session.post(url, json=body, headers=headers, timeout=self.timeout_seconds)
        response.raise_for_status()
        payload = response.json()
        hashkey = str(payload.get("HASH", "")).strip()
        if not hashkey:
            raise RuntimeError(f"Hashkey response did not include HASH: {payload}")
        return hashkey

    def _request(
        self,
        method: str,
        path: str,
        tr_id: str,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        tr_cont: str = "",
        use_hashkey: bool = False,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        token = self.auth_manager.get_token()
        headers: dict[str, str] = {
            "content-type": "application/json",
            "accept": "text/plain",
            "charset": "UTF-8",
            "authorization": f"Bearer {token}",
            "appkey": self.appkey,
            "appsecret": self.appsecret,
            "tr_id": tr_id,
            "custtype": "P",
            "tr_cont": tr_cont,
        }

        request_kwargs: dict[str, Any] = {"headers": headers, "timeout": self.timeout_seconds}
        if method == "GET":
            request_kwargs["params"] = params or {}
        else:
            request_kwargs["json"] = body or {}
            if use_hashkey:
                headers["hashkey"] = self.get_hashkey(body or {})

        last_error: Exception | None = None
        for attempt in range(self.retry_count + 1):
            try:
                response = self._session.request(method, url, **request_kwargs)
                if response.status_code == 429 or response.status_code >= 500:
                    raise requests.HTTPError(f"retryable HTTP {response.status_code}", response=response)
                response.raise_for_status()
                payload = response.json()
                if str(payload.get("rt_cd", "0")) != "0":
                    raise RuntimeError(
                        f"KIS API error: rt_cd={payload.get('rt_cd')} msg_cd={payload.get('msg_cd')} msg1={payload.get('msg1')}"
                    )
                return payload
            except (requests.Timeout, requests.ConnectionError, json.JSONDecodeError, RuntimeError, requests.HTTPError) as exc:
                last_error = exc
                status_code = getattr(getattr(exc, "response", None), "status_code", None)
                retryable = isinstance(exc, (requests.Timeout, requests.ConnectionError, json.JSONDecodeError, RuntimeError)) or status_code in {
                    429,
                } or (status_code is not None and status_code >= 500)
                is_last_attempt = attempt >= self.retry_count
                self.logger.error(
                    "api error: method=%s path=%s attempt=%s/%s error=%s",
                    method,
                    path,
                    attempt + 1,
                    self.retry_count + 1,
                    exc,
                )
                if is_last_attempt or not retryable:
                    break
                time.sleep(self.retry_backoff_seconds * (attempt + 1))

        raise RuntimeError(f"Request failed after retries: {method} {path}") from last_error
