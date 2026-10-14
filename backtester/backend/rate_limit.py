"""인증 요청 IP 단위 유량 제한

IP당 분당 5회 / 시간당 50회. 하나라도 초과하면 429 + Retry-After.
카운터는 프로세스 내 dict 에 둔다(재시작 시 초기화 — 반복 호출 속도를 늦추는 역할).
"""
import os
import threading
import time
from collections import deque
from typing import Deque, Dict, Optional, Tuple

from fastapi import Request

PER_MINUTE_LIMIT = 5
PER_HOUR_LIMIT = 50
_MINUTE = 60.0
_HOUR = 3600.0

# 리버스 프록시 뒤에 배포할 때만 켠다(X-Forwarded-For 는 위조 가능)
TRUST_PROXY_HEADERS = os.getenv("TRUST_PROXY_HEADERS", "0") == "1"


class SigninRateLimiter:
    """IP별 슬라이딩 윈도우 카운터"""

    def __init__(
        self,
        per_minute: int = PER_MINUTE_LIMIT,
        per_hour: int = PER_HOUR_LIMIT,
    ):
        self._limits: Tuple[Tuple[float, int], ...] = ((_MINUTE, per_minute), (_HOUR, per_hour))
        self._hits: Dict[str, Deque[float]] = {}
        self._lock = threading.Lock()

    def hit(self, client_ip: str, now: Optional[float] = None) -> int:
        """요청 1회를 기록한다. 허용이면 0, 초과면 재시도까지 남은 초를 반환"""
        now = time.monotonic() if now is None else now
        with self._lock:
            hits = self._hits.setdefault(client_ip, deque())
            while hits and now - hits[0] >= _HOUR:
                hits.popleft()

            retry_after = 0
            for window, limit in self._limits:
                in_window = [t for t in hits if now - t < window]
                if len(in_window) >= limit:
                    retry_after = max(retry_after, int(in_window[0] + window - now) + 1)
            if retry_after:
                return retry_after

            hits.append(now)
            return 0


def client_ip_of(http_request: Request) -> str:
    if TRUST_PROXY_HEADERS:
        forwarded = http_request.headers.get("x-forwarded-for", "")
        first = forwarded.split(",")[0].strip()
        if first:
            return first
    return http_request.client.host if http_request.client else "unknown"


signin_rate_limiter = SigninRateLimiter()
