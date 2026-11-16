"""종목 코드 검증 (파일 경로 순회 방지).

종목 코드는 CSV 파일명·Lean 설정 등에 직접 들어가므로 영숫자 1~12자로 제한한다.
"""
import re
from typing import List

SYMBOL_RE = re.compile(r"[0-9A-Za-z]{1,12}")


def is_valid_symbol(symbol: object) -> bool:
    """허용된 종목 코드 형식인지 확인."""
    return isinstance(symbol, str) and SYMBOL_RE.fullmatch(symbol) is not None


def invalid_symbols(symbols) -> List[str]:
    """허용되지 않은 종목만 추려 반환 (없으면 빈 리스트)."""
    return [s for s in (symbols or []) if not is_valid_symbol(s)]
