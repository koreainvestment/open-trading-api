#!/usr/bin/env python3
"""KIS 마스터파일 다운로드 및 Lean symbol-properties 생성.

한국투자증권 서버에서 종목 마스터파일을 다운로드하고,
Lean 백테스트용 symbol-properties-database.csv에 추가합니다.

Usage:
    python scripts/download_master.py

인증 없이 공개 URL에서 다운로드합니다.
"""

import zipfile
from io import BytesIO
from pathlib import Path
import urllib.request
import csv

# 마스터파일 URL (KIS 공개 URL - 인증 불필요)
MASTER_URLS = {
    "kospi": "https://new.real.download.dws.co.kr/common/master/kospi_code.mst.zip",
    "kosdaq": "https://new.real.download.dws.co.kr/common/master/kosdaq_code.mst.zip",
}

# 프로젝트 경로
PROJECT_DIR = Path(__file__).parent.parent
WORKSPACE_DIR = PROJECT_DIR / ".lean-workspace"
SYMBOL_PROPS_FILE = WORKSPACE_DIR / "data" / "symbol-properties" / "symbol-properties-database.csv"


def download_and_extract(url: str) -> bytes:
    """URL에서 파일 다운로드 및 ZIP 압축 해제."""
    print(f"  다운로드 중: {url}")
    
    with urllib.request.urlopen(url, timeout=60) as response:
        content = response.read()
    
    print(f"  다운로드 완료: {len(content):,} bytes")
    
    # ZIP 압축 해제
    try:
        with zipfile.ZipFile(BytesIO(content)) as zf:
            for name in zf.namelist():
                return zf.read(name)
    except zipfile.BadZipFile:
        return content


def parse_krx_master(content: bytes, exchange: str) -> list[dict]:
    """KOSPI/KOSDAQ 마스터파일 파싱.
    
    파일 형식: EUC-KR 인코딩, 고정 폭 필드 (바이트 기준)
    - 0-8 (9바이트): 단축코드
    - 9-20 (12바이트): 표준코드
    - 21-60 (40바이트): 한글종목명
    """
    symbols = []
    lines = content.split(b"\n")
    
    for line_bytes in lines:
        if len(line_bytes) < 61:
            continue
        
        # 바이트 단위로 슬라이싱 후 디코딩
        code = line_bytes[0:9].decode("euc-kr", errors="ignore").strip()
        name = line_bytes[21:61].decode("euc-kr", errors="ignore").strip()
        
        # 실제 종목코드는 6자리
        if len(code) > 6:
            code = code[-6:]
        
        # 숫자로만 이루어진 코드만 (ETF, 우선주 등 포함)
        if code and name and code.isdigit():
            symbols.append({
                "code": code,
                "name": name,
                "exchange": exchange,
            })
    
    return symbols


def append_to_symbol_properties(symbols: list[dict]) -> int:
    """symbol-properties-database.csv에 KRX 종목 추가."""
    
    # 기존 파일 읽기
    existing_codes = set()
    if SYMBOL_PROPS_FILE.exists():
        with open(SYMBOL_PROPS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("krx,"):
                    code = line.split(",")[1]
                    existing_codes.add(code)
    
    # 새 종목만 추가
    new_symbols = [s for s in symbols if s["code"] not in existing_codes]
    
    if not new_symbols:
        print(f"  추가할 새 종목 없음 (기존 {len(existing_codes)}개)")
        return 0
    
    # 파일에 추가
    with open(SYMBOL_PROPS_FILE, "a", encoding="utf-8") as f:
        for sym in new_symbols:
            # format: market,symbol,type,description,quote_currency,contract_multiplier,
            #         minimum_price_variation,lot_size,market_ticker,minimum_order_size,
            #         price_magnifier,strike_multiplier
            line = f'krx,{sym["code"]},equity,{sym["name"]},KRW,1,1,1,{sym["code"]},1,1,1\n'
            f.write(line)
    
    return len(new_symbols)


def main():
    print("=" * 50)
    print("KIS 마스터파일 다운로드")
    print("=" * 50)
    print()
    
    # symbol-properties 파일 확인
    if not SYMBOL_PROPS_FILE.exists():
        print(f"❌ symbol-properties 파일이 없습니다: {SYMBOL_PROPS_FILE}")
        print("   먼저 setup_lean_data.sh를 실행하세요.")
        return 1
    
    total_added = 0
    
    for exchange, url in MASTER_URLS.items():
        print(f"\n[{exchange.upper()}]")
        
        try:
            # 다운로드 및 압축 해제
            content = download_and_extract(url)
            
            # 파싱
            symbols = parse_krx_master(content, exchange)
            print(f"  파싱 완료: {len(symbols)}개 종목")
            
            # symbol-properties에 추가
            added = append_to_symbol_properties(symbols)
            total_added += added
            if added > 0:
                print(f"  ✅ {added}개 종목 추가됨")
            
        except Exception as e:
            print(f"  ❌ 오류: {e}")
    
    print()
    print("=" * 50)
    print(f"완료! 총 {total_added}개 종목 추가됨")
    print(f"파일: {SYMBOL_PROPS_FILE}")
    print("=" * 50)
    
    return 0


if __name__ == "__main__":
    exit(main())
