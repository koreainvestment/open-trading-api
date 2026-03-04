"""종목 검색 API 라우터

종목코드/종목명으로 검색하는 API 엔드포인트
마스터파일 수집 기능 포함 (CSV 저장, 인메모리 캐시)
"""

import logging
import zipfile
from datetime import date, datetime
from io import BytesIO
from pathlib import Path
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(tags=["symbols"])

# 마스터파일 디렉토리
MASTER_DIR = Path(".master")

# 마스터파일 다운로드 URL (코스피/코스닥만 사용)
MASTER_URLS = {
    "kospi": "https://new.real.download.dws.co.kr/common/master/kospi_code.mst.zip",
    "kosdaq": "https://new.real.download.dws.co.kr/common/master/kosdaq_code.mst.zip",
    # "konex": "https://new.real.download.dws.co.kr/common/master/konex_code.mst.zip",
    # "nasdaq": "https://new.real.download.dws.co.kr/common/master/nasmst.cod.zip",
    # "nyse": "https://new.real.download.dws.co.kr/common/master/nysmst.cod.zip",
    # "amex": "https://new.real.download.dws.co.kr/common/master/amsmst.cod.zip",
}

# 인메모리 캐시
_symbol_cache: dict[str, list[dict]] = {}
_last_loaded: dict[str, datetime] = {}


# ============================================
# 응답 스키마
# ============================================


class SymbolSearchItem(BaseModel):
    """종목 검색 결과 항목"""

    code: str = Field(..., description="종목코드", example="005930")
    name: str = Field(..., description="종목명", example="삼성전자")
    exchange: str = Field(..., description="거래소 코드", example="kospi")
    exchange_name: str = Field(..., description="거래소명", example="코스피")


class SymbolSearchResponse(BaseModel):
    """종목 검색 응답"""

    status: str = "success"
    query: str = Field(..., description="검색어")
    total: int = Field(..., description="검색 결과 수")
    items: list[SymbolSearchItem] = Field(default_factory=list, description="검색 결과 목록")


class SymbolDetailResponse(BaseModel):
    """종목 상세 정보 응답"""

    status: str = "success"
    data: Optional[SymbolSearchItem] = None
    message: Optional[str] = None


class MasterStatus(BaseModel):
    """마스터파일 상태"""
    kospi_count: int = 0
    kosdaq_count: int = 0
    total_count: int = 0
    kospi_updated: Optional[str] = None
    kosdaq_updated: Optional[str] = None
    needs_update: bool = True


class CollectResult(BaseModel):
    """마스터파일 수집 결과"""
    success: bool
    kospi_count: int = 0
    kosdaq_count: int = 0
    total_count: int = 0
    errors: list[str] = []


# ============================================
# 파일 시스템 유틸리티
# ============================================


def _ensure_master_dir():
    """마스터 디렉토리 생성"""
    MASTER_DIR.mkdir(exist_ok=True)


def _get_csv_path(exchange: str) -> Path:
    """CSV 파일 경로"""
    return MASTER_DIR / f"{exchange}.csv"


def _get_file_mtime(path: Path) -> Optional[datetime]:
    """파일 수정 시간"""
    if path.exists():
        return datetime.fromtimestamp(path.stat().st_mtime)
    return None


def _load_from_csv(exchange: str) -> list[dict]:
    """CSV에서 종목 로드"""
    csv_path = _get_csv_path(exchange)
    if not csv_path.exists():
        return []

    symbols = []
    try:
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()
            for line in lines[1:]:  # 헤더 스킵
                parts = line.strip().split(",")
                if len(parts) >= 3:
                    symbols.append({
                        "code": parts[0],
                        "name": parts[1],
                        "exchange": parts[2],
                        "exchange_name": "코스피" if parts[2] == "kospi" else "코스닥",
                    })
    except Exception as e:
        logger.error(f"CSV 로드 오류 ({exchange}): {e}")

    return symbols


def _save_to_csv(exchange: str, symbols: list[dict]):
    """CSV로 종목 저장"""
    _ensure_master_dir()
    csv_path = _get_csv_path(exchange)
    
    try:
        with open(csv_path, "w", encoding="utf-8-sig") as f:
            f.write("code,name,exchange\n")
            for s in symbols:
                f.write(f"{s['code']},{s['name']},{s['exchange']}\n")
        logger.info(f"CSV 저장 완료: {csv_path} ({len(symbols)}개)")
    except Exception as e:
        logger.error(f"CSV 저장 오류 ({exchange}): {e}")


def _get_all_symbols() -> list[dict]:
    """모든 종목 로드 (캐시 사용)
    
    strategy.py에서 종목명 조회에 사용됩니다.
    """
    global _symbol_cache, _last_loaded

    all_symbols = []

    for exchange in ["kospi", "kosdaq"]:
        # 캐시 확인
        if exchange in _symbol_cache:
            all_symbols.extend(_symbol_cache[exchange])
        else:
            # CSV에서 로드
            symbols = _load_from_csv(exchange)
            if symbols:
                _symbol_cache[exchange] = symbols
                _last_loaded[exchange] = datetime.now()
                all_symbols.extend(symbols)

    return all_symbols


# ============================================
# 주요 종목 데이터 (폴백용)
# ============================================

FALLBACK_STOCKS: list[dict] = [
    {"code": "071050", "name": "한국금융지주", "exchange": "kospi", "exchange_name": "코스피"},
]


# ============================================
# 검색 로직
# ============================================


def search_symbols(query: str, limit: int = 20, exchange: Optional[str] = None) -> list[dict]:
    """종목 검색 (코드 또는 이름)

    Args:
        query: 검색어 (종목코드 또는 종목명)
        limit: 최대 결과 수
        exchange: 거래소 필터 (kospi, kosdaq)

    Returns:
        검색 결과 목록
    """
    query = query.lower().strip()
    results: list[dict] = []

    # 캐시된 종목 또는 폴백 사용
    all_symbols = _get_all_symbols() or FALLBACK_STOCKS

    for stock in all_symbols:
        # 거래소 필터
        if exchange and stock["exchange"] != exchange.lower():
            continue

        # 코드 또는 이름 매칭
        if query in stock["code"].lower() or query in stock["name"].lower():
            results.append(stock)
            if len(results) >= limit:
                break

    return results


def get_symbol_by_code(code: str) -> Optional[dict]:
    """종목코드로 종목 정보 조회

    Args:
        code: 종목코드

    Returns:
        종목 정보 또는 None
    """
    all_symbols = _get_all_symbols() or FALLBACK_STOCKS
    for stock in all_symbols:
        if stock["code"] == code:
            return stock
    return None


# ============================================
# API 엔드포인트
# ============================================


# ============================================
# 마스터파일 상태/수집 API (/{code} 보다 먼저 정의해야 함)
# ============================================


@router.get("/status", response_model=MasterStatus)
async def get_master_status() -> MasterStatus:
    """마스터파일 상태 조회
    
    현재 로드된 종목 수, 마지막 업데이트 시간, 업데이트 필요 여부를 반환합니다.
    """
    kospi_path = _get_csv_path("kospi")
    kosdaq_path = _get_csv_path("kosdaq")
    
    # 캐시에서 로드 또는 CSV에서 로드
    kospi_symbols = _symbol_cache.get("kospi", []) or _load_from_csv("kospi")
    kosdaq_symbols = _symbol_cache.get("kosdaq", []) or _load_from_csv("kosdaq")
    
    kospi_count = len(kospi_symbols)
    kosdaq_count = len(kosdaq_symbols)
    
    kospi_mtime = _get_file_mtime(kospi_path)
    kosdaq_mtime = _get_file_mtime(kosdaq_path)
    
    return MasterStatus(
        kospi_count=kospi_count,
        kosdaq_count=kosdaq_count,
        total_count=kospi_count + kosdaq_count,
        kospi_updated=kospi_mtime.isoformat() if kospi_mtime else None,
        kosdaq_updated=kosdaq_mtime.isoformat() if kosdaq_mtime else None,
        needs_update=_check_needs_update(),
    )


@router.post("/collect", response_model=CollectResult)
async def collect_master_files() -> CollectResult:
    """마스터파일 수집
    
    한국투자증권 서버에서 코스피/코스닥 마스터파일을 다운로드합니다.
    수집된 데이터는 .master/ 디렉토리에 CSV로 저장됩니다.
    """
    errors = []
    kospi_count = 0
    kosdaq_count = 0
    
    # 코스피 수집
    symbols, error = await _download_and_parse("kospi")
    if error:
        errors.append(f"kospi: {error}")
    else:
        kospi_count = len(symbols)
    
    # 코스닥 수집
    symbols, error = await _download_and_parse("kosdaq")
    if error:
        errors.append(f"kosdaq: {error}")
    else:
        kosdaq_count = len(symbols)
    
    return CollectResult(
        success=len(errors) == 0,
        kospi_count=kospi_count,
        kosdaq_count=kosdaq_count,
        total_count=kospi_count + kosdaq_count,
        errors=errors,
    )


# ============================================
# 검색 API
# ============================================


@router.get("/search", response_model=SymbolSearchResponse)
async def search_symbols_api(
    q: str = Query(..., min_length=1, max_length=50, description="검색어 (종목코드 또는 종목명)"),
    limit: int = Query(default=20, ge=1, le=50, description="최대 결과 수"),
    exchange: Optional[str] = Query(default=None, description="거래소 필터 (kospi, kosdaq)"),
) -> SymbolSearchResponse:
    """종목 검색

    종목코드 또는 종목명으로 검색합니다.

    Args:
        q: 검색어 (종목코드 또는 종목명)
        limit: 최대 결과 수 (1-50, 기본 20)
        exchange: 거래소 필터 (kospi, kosdaq)

    Returns:
        검색 결과

    Examples:
        - GET /api/symbols/search?q=삼성
        - GET /api/symbols/search?q=005930
        - GET /api/symbols/search?q=에코&exchange=kosdaq
    """
    # 거래소 필터 검증
    if exchange and exchange.lower() not in ("kospi", "kosdaq"):
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 거래소입니다: {exchange}. 'kospi' 또는 'kosdaq'만 지원합니다.",
        )

    results = search_symbols(q, limit=limit, exchange=exchange)

    return SymbolSearchResponse(
        query=q,
        total=len(results),
        items=[SymbolSearchItem(**stock) for stock in results],
    )


@router.get("/{code}", response_model=SymbolDetailResponse)
async def get_symbol_detail(
    code: str,
) -> SymbolDetailResponse:
    """종목 상세 정보 조회

    종목코드로 상세 정보를 조회합니다.

    Args:
        code: 종목코드 (예: 005930)

    Returns:
        종목 상세 정보

    Examples:
        - GET /api/symbols/005930
    """
    stock = get_symbol_by_code(code)

    if stock is None:
        raise HTTPException(
            status_code=404,
            detail=f"종목을 찾을 수 없습니다: {code}",
        )

    return SymbolDetailResponse(
        data=SymbolSearchItem(**stock),
    )


# ============================================
# 마스터파일 수집 API
# ============================================


def _parse_kospi_kosdaq_mst(content: bytes, exchange: str) -> list[dict]:
    """KOSPI/KOSDAQ 마스터파일 파싱
    
    파일 형식: EUC-KR 인코딩, 고정 폭 필드 (바이트 기준)
    - 0-8 (9바이트): 단축코드
    - 9-20 (12바이트): 표준코드
    - 21-60 (40바이트): 한글종목명
    """
    symbols = []
    try:
        lines = content.split(b"\n")
        for line_bytes in lines:
            if len(line_bytes) < 61:
                continue
            
            code = line_bytes[0:9].decode("euc-kr", errors="ignore").strip()
            name = line_bytes[21:61].decode("euc-kr", errors="ignore").strip()
            
            # 실제 종목코드는 6자리
            if len(code) > 6:
                code = code[-6:]
            
            if code and name:
                symbols.append({
                    "code": code,
                    "name": name,
                    "exchange": exchange,
                    "exchange_name": "코스피" if exchange == "kospi" else "코스닥",
                })
    except Exception as e:
        logger.error(f"마스터파일 파싱 오류 ({exchange}): {e}")
    
    return symbols


async def _download_and_parse(exchange: str, timeout: float = 60.0) -> tuple[list[dict], Optional[str]]:
    """마스터파일 다운로드 및 파싱"""
    global _symbol_cache, _last_loaded
    
    url = MASTER_URLS.get(exchange)
    if not url:
        return [], f"알 수 없는 거래소: {exchange}"
    
    try:
        logger.info(f"마스터파일 다운로드 시작: {exchange}")
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
        
        content = response.content
        
        # ZIP 압축 해제
        try:
            with zipfile.ZipFile(BytesIO(content)) as zf:
                for name in zf.namelist():
                    extracted = zf.read(name)
                    break
        except zipfile.BadZipFile:
            extracted = content
        
        # 파싱
        symbols = _parse_kospi_kosdaq_mst(extracted, exchange)
        
        if symbols:
            # CSV 저장
            _save_to_csv(exchange, symbols)
            # 캐시 업데이트
            _symbol_cache[exchange] = symbols
            _last_loaded[exchange] = datetime.now()
            logger.info(f"마스터파일 수집 완료: {exchange} - {len(symbols)}개 종목")
        
        return symbols, None
        
    except httpx.HTTPStatusError as e:
        error = f"HTTP {e.response.status_code}"
        logger.error(f"HTTP 오류 ({exchange}): {error}")
        return [], error
    except Exception as e:
        logger.error(f"수집 실패 ({exchange}): {e}")
        return [], str(e)


def _check_needs_update() -> bool:
    """오늘 업데이트가 필요한지 확인"""
    for exchange in ["kospi", "kosdaq"]:
        csv_path = _get_csv_path(exchange)
        if not csv_path.exists():
            return True
        mtime = _get_file_mtime(csv_path)
        if mtime and mtime.date() < date.today():
            return True
    return False
