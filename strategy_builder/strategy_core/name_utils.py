"""전략 이름 sanitize 유틸리티"""

import re

MAX_LEN = 64


def sanitize_strategy_name(raw: str) -> str:
    """전략 이름을 안전한 Python 식별자 / 파일명으로 변환.

    1. 한글 전체 제거 (음절 + 자모 + 호환자모)
    2. 영숫자 외 → _ 치환
    3. 연속 _ 정리, 양끝 _ 제거
    4. 소문자화, 빈 문자열 fallback
    5. 숫자 시작 방지
    6. 길이 제한 (64자)
    """
    # 1. 한글 전체 제거 (음절 U+AC00-U+D7A3, 자모 U+1100-U+11FF, 호환자모 U+3130-U+318F)
    name = re.sub(r'[\uAC00-\uD7A3\u1100-\u11FF\u3130-\u318F]', '', raw)
    # 2. 영숫자 외 → _ 치환
    name = re.sub(r'[^a-zA-Z0-9]', '_', name)
    # 3. 연속 _ 정리, 양끝 _ 제거
    name = re.sub(r'_+', '_', name).strip('_')
    # 4. 소문자화, 빈 문자열 fallback
    name = name.lower() or 'builder'
    # 5. 숫자 시작 방지
    if name[0].isdigit():
        name = 'strategy_' + name
    # 6. 길이 제한
    return name[:MAX_LEN]
