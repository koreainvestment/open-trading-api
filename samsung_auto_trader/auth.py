"""
Korea Investment Open API 인증 및 토큰 캐싱.
토큰은 같은 날 내에 재사용하여 API 호출을 최소화합니다.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict
from logger import logger
from api_client import api_client
import config


class TokenManager:
    """토큰 캐싱 및 재사용을 관리합니다."""

    def __init__(self):
        self.cache_file = config.TOKEN_CACHE_FILE
        self.cache_expiry_minutes = config.TOKEN_CACHE_EXPIRY_MINUTES

    def _load_cached_token(self) -> Optional[Dict]:
        """
        캐시된 토큰을 로드합니다.
        유효한 경우 반환, 없거나 만료된 경우 None을 반환합니다.
        """
        if not os.path.exists(self.cache_file):
            logger.debug("토큰 캐시 파일이 없습니다")
            return None

        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)

            # 토큰 만료 시간 확인
            created_at = datetime.fromisoformat(cache_data.get('created_at', ''))
            expiry_time = created_at + timedelta(minutes=self.cache_expiry_minutes)

            if datetime.now() < expiry_time:
                logger.info("캐시된 토큰을 재사용합니다")
                return cache_data['token']
            else:
                logger.info("캐시된 토큰이 만료되었습니다")
                return None

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"토큰 캐시 읽기 실패: {e}")
            return None

    def _save_token_to_cache(self, token: Dict) -> None:
        """새로운 토큰을 캐시에 저장합니다."""
        cache_data = {
            'token': token,
            'created_at': datetime.now().isoformat()
        }

        try:
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            logger.info("토큰이 캐시에 저장되었습니다")
        except Exception as e:
            logger.error(f"토큰 캐시 저장 실패: {e}")

    def get_token(self) -> str:
        """
        토큰을 반환합니다.
        캐시된 토큰이 있으면 재사용하고, 없으면 새로 발급합니다.
        
        Returns:
            인증 토큰 문자열
        """
        # 캐시된 토큰 확인
        cached_token = self._load_cached_token()
        if cached_token:
            return cached_token['access_token']

        # 새로운 토큰 발급
        logger.info("새 토큰을 발급받습니다")
        token = self._request_new_token()
        self._save_token_to_cache(token)

        return token['access_token']

    def _request_new_token(self) -> Dict:
        """
        Korea Investment Open API에서 새로운 토큰을 발급받습니다.
        
        Returns:
            토큰 정보 딕셔너리 (access_token, token_type 등)
        """
        app_key = os.getenv('GH_APPKEY')
        app_secret = os.getenv('GH_APPSECRET')

        if not app_key or not app_secret:
            raise ValueError(
                "환경변수 GH_APPKEY, GH_APPSECRET를 설정해야 합니다.\n"
                "GitHub Codespaces에서: Settings > Secrets and variables > Codespaces\n"
                "로컬 환경에서: .env 파일에 설정 필요"
            )

        headers = {
            "Content-Type": "application/json",
        }

        body = {
            "grant_type": "client_credentials",
            "appkey": app_key,
            "appsecret": app_secret
        }

        try:
            response = api_client.post(
                config.AUTH_ENDPOINT,
                headers=headers,
                json_body=body
            )
            logger.info("토큰 발급 성공")
            return response
        except Exception as e:
            logger.error(f"토큰 발급 실패: {e}")
            raise


# 글로벌 토큰 관리자 인스턴스
token_manager = TokenManager()


def get_auth_token() -> str:
    """
    인증 토큰을 반환합니다.
    캐시된 토큰을 재사용하거나 새로 발급합니다.
    """
    return token_manager.get_token()
