"""
Korea Investment Open API와 통신하기 위한 저수준 HTTP 클라이언트.
에러 처리 및 재시도 로직을 포함합니다.
"""

import requests
from typing import Dict, Optional
from logger import logger
import config


class APIClient:
    """Korea Investment Open API를 호출하는 HTTP 클라이언트."""

    def __init__(self):
        self.base_url = config.KIS_VIRTUAL_BASE_URL  # Mock trading 사용
        self.timeout = config.REQUEST_TIMEOUT_SECONDS
        self.max_retries = config.MAX_RETRIES

    def post(
        self,
        endpoint: str,
        headers: Dict,
        json_body: Optional[Dict] = None,
    ) -> Dict:
        """
        POST 요청을 보내고 응답을 반환합니다.
        
        Args:
            endpoint: API 엔드포인트 (예: /oauth2/tokenP)
            headers: HTTP 헤더
            json_body: JSON 요청 본문
            
        Returns:
            API 응답 JSON 딕셔너리
            
        Raises:
            requests.RequestException: 네트워크 오류
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"POST 요청: {url}")

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=json_body,
                    timeout=self.timeout,
                    verify=False  # 테스트 환경에서 SSL 검증 비활성화
                )
                response.raise_for_status()

                logger.debug(f"응답 상태: {response.status_code}")
                return response.json()

            except requests.Timeout as e:
                logger.warning(f"타임아웃 (시도 {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"최대 재시도 횟수 초과: {url}")
                    raise

            except requests.RequestException as e:
                logger.warning(f"요청 실패 (시도 {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"API 요청 최종 실패: {url}")
                    raise

    def get(
        self,
        endpoint: str,
        headers: Dict,
        params: Optional[Dict] = None,
    ) -> Dict:
        """
        GET 요청을 보내고 응답을 반환합니다.
        
        Args:
            endpoint: API 엔드포인트
            headers: HTTP 헤더
            params: 쿼리 파라미터
            
        Returns:
            API 응답 JSON 딕셔너리
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"GET 요청: {url}")

        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=self.timeout,
                    verify=False
                )
                response.raise_for_status()

                logger.debug(f"응답 상태: {response.status_code}")
                return response.json()

            except requests.Timeout as e:
                logger.warning(f"타임아웃 (시도 {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"최대 재시도 횟수 초과: {url}")
                    raise

            except requests.RequestException as e:
                logger.warning(f"요청 실패 (시도 {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"API 요청 최종 실패: {url}")
                    raise


# 글로벌 API 클라이언트 인스턴스
api_client = APIClient()
