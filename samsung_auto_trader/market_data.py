"""
시장 데이터 조회 - 삼성전자(005930)의 현재 주가를 가져옵니다.
"""

from typing import Optional
from logger import logger
from api_client import api_client
from auth import get_auth_token
import config
import os


def get_current_price(stock_code: str = config.TARGET_STOCK) -> Optional[int]:
    """
    삼성전자의 현재 주가를 조회합니다.
    
    Args:
        stock_code: 주식 코드 (기본값: 005930)
        
    Returns:
        현재 주가 (정수), 실패 시 None
    """
    try:
        token = get_auth_token()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        params = {
            "fid_cond_mrkt_div_code": "J",  # 국내 주식
            "fid_input_iscd": stock_code,
        }

        logger.debug(f"주가 조회: {stock_code}")
        response = api_client.get(
            config.PRICE_ENDPOINT,
            headers=headers,
            params=params
        )

        # 응답에서 현재가 추출
        # NOTE: 정확한 필드명은 API 응답 구조에 따라 조정 필요
        price = response.get('output', {}).get('stck_prpr')
        
        if price:
            price = int(price)
            logger.info(f"현재 주가: {stock_code} = {price} KRW")
            return price
        else:
            logger.warning(f"응답에서 주가를 찾을 수 없습니다: {response}")
            return None

    except Exception as e:
        logger.error(f"주가 조회 실패: {e}")
        return None
