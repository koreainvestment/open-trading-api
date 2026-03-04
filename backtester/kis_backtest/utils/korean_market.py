"""한국 시장 유틸리티

한국 주식시장의 호가단위, 거래시간 등 처리.
"""

import math
from typing import Literal


def get_tick_size(price: float) -> int:
    """가격에 따른 호가단위 반환
    
    한국 주식시장 호가단위 (2023년 기준):
    - ~2,000원: 1원
    - 2,000~5,000원: 5원
    - 5,000~20,000원: 10원
    - 20,000~50,000원: 50원
    - 50,000~200,000원: 100원
    - 200,000~500,000원: 500원
    - 500,000원~: 1,000원
    
    Args:
        price: 현재가
    
    Returns:
        호가단위 (원)
    
    Example:
        >>> get_tick_size(50000)
        100
        >>> get_tick_size(1500)
        1
    """
    if price < 2000:
        return 1
    elif price < 5000:
        return 5
    elif price < 20000:
        return 10
    elif price < 50000:
        return 50
    elif price < 200000:
        return 100
    elif price < 500000:
        return 500
    else:
        return 1000


def round_to_tick(
    price: float,
    direction: Literal["up", "down", "nearest"] = "nearest"
) -> int:
    """가격을 호가단위로 반올림
    
    Args:
        price: 원래 가격
        direction: 반올림 방향
            - "up": 올림
            - "down": 내림
            - "nearest": 반올림
    
    Returns:
        호가단위로 조정된 가격
    
    Example:
        >>> round_to_tick(50123, "nearest")
        50100
        >>> round_to_tick(50123, "up")
        50200
    """
    tick = get_tick_size(price)
    
    if direction == "up":
        return int(math.ceil(price / tick) * tick)
    elif direction == "down":
        return int(math.floor(price / tick) * tick)
    else:
        return int(round(price / tick) * tick)



