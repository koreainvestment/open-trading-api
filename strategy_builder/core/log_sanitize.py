"""
로그 인젝션 방지용 값 축소 헬퍼

사용자 제어 값(경로 파라미터, 요청 본문 문자열 등)을 로그 포맷 인자로 그대로 넘기지 않고
안전한 형태로 축소한 뒤 남긴다.
"""

import re

_TOKEN_PATTERN = re.compile(r"[0-9A-Za-z_-]{1,20}")
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")
_TEXT_LIMIT = 40


def log_token(value) -> str:
    """식별자형 값(종목코드·주문번호 등). 허용 문자/길이를 벗어나면 길이만 남긴다."""
    text = str(value)
    if _TOKEN_PATTERN.fullmatch(text):
        return text
    return f"<invalid len={len(text)}>"


def log_text(value) -> str:
    """자유서식 문자열(종목명·응답 메시지 등). 제어문자 제거 후 길이 제한."""
    text = _CONTROL_CHARS.sub(" ", str(value))
    if len(text) > _TEXT_LIMIT:
        return f"{text[:_TEXT_LIMIT]}...(len={len(text)})"
    return text


def log_error(error: BaseException) -> str:
    """예외는 원문 대신 타입명만 남긴다."""
    return type(error).__name__
