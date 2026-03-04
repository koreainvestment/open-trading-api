#!/usr/bin/env python3
"""
전략 생성 시스템 예제

새로운 선언적 전략 시스템을 사용하여 Lean 백테스트 코드를 생성하는 방법을 보여줍니다.

실행:
    uv run python examples/strategy_generation.py
"""

import sys
from datetime import date, timedelta
from pathlib import Path

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

# 날짜 설정: 오늘 기준 1년 데이터
TODAY = date.today().strftime("%Y-%m-%d")
ONE_YEAR_AGO = (date.today() - timedelta(days=365)).strftime("%Y-%m-%d")

from kis_backtest import (
    STRATEGY_REGISTRY,
    get_strategy,
    get_all_strategies,
    PositionSizer,
    SizingMethod,
)
from kis_backtest.strategies.generator import StrategyGenerator, generate_strategy


def example_list_strategies():
    """등록된 모든 전략 목록 출력"""
    print("=" * 60)
    print("📋 등록된 전략 목록")
    print("=" * 60)
    
    strategies = get_all_strategies()
    
    for strategy in strategies:
        print(f"\n📈 {strategy['id']}")
        print(f"   이름: {strategy.get('name', 'N/A')}")
        print(f"   카테고리: {strategy.get('category', 'N/A')}")
        print(f"   난이도: {strategy.get('difficulty', 'N/A')}")
        print(f"   설명: {strategy.get('description', 'N/A')[:50]}...")
        
        indicators = strategy.get("indicators", [])
        ind_names = [ind.get("alias") or ind.get("id") for ind in indicators]
        print(f"   지표: {ind_names}")


def example_generate_builtin_strategy():
    """내장 전략의 Lean 코드 생성"""
    print("\n" + "=" * 60)
    print("🔧 SMA 크로스오버 전략 코드 생성")
    print("=" * 60)
    
    # 편의 함수를 사용한 코드 생성
    code = generate_strategy(
        strategy_id="sma_crossover",
        symbols=["005930"],  # 삼성전자
        start_date=ONE_YEAR_AGO,
        end_date=TODAY,
        initial_capital=100_000_000,  # 1억원
        market_type="krx",
        params={
            "fast_period": 10,
            "slow_period": 30,
        },
    )
    
    print("\n생성된 코드 (일부):")
    print("-" * 60)
    lines = code.split("\n")
    for line in lines[:50]:  # 처음 50줄만
        print(line)
    if len(lines) > 50:
        print(f"... ({len(lines) - 50}줄 더)")
    
    return code


def example_generate_with_risk_management():
    """리스크 관리 옵션 포함 전략 생성"""
    print("\n" + "=" * 60)
    print("🛡️ 리스크 관리 옵션 포함 전략 생성")
    print("=" * 60)
    
    # 리스크 관리 설정
    risk_config = {
        "stop_loss": {
            "enabled": True,
            "percent": 5.0,  # 5% 손절
        },
        "take_profit": {
            "enabled": True,
            "percent": 15.0,  # 15% 익절
        },
        "trailing_stop": {
            "enabled": True,
            "percent": 3.0,  # 3% 트레일링 스탑
        },
    }
    
    generator = StrategyGenerator(
        strategy_id="volatility_breakout",
        symbols=["005930", "000660"],  # 삼성전자, SK하이닉스
        start_date=ONE_YEAR_AGO,
        end_date=TODAY,
        initial_capital=50_000_000,
        market_type="krx",
        params={"atr_period": 10, "breakout_pct": 3.0},
        risk_config=risk_config,
    )

    code = generator.generate()
    
    print("\n리스크 관리 설정:")
    print(f"  손절: {risk_config['stop_loss']['percent']}%")
    print(f"  익절: {risk_config['take_profit']['percent']}%")
    print(f"  트레일링 스탑: {risk_config['trailing_stop']['percent']}%")
    
    print("\n생성된 코드 (리스크 관리 부분):")
    print("-" * 60)
    
    # 리스크 관리 코드 찾기
    in_risk_section = False
    for line in code.split("\n"):
        if "entry_prices" in line or "peak_prices" in line:
            in_risk_section = True
        if in_risk_section:
            print(line)
            if "exit_cond" in line and "=" in line:
                in_risk_section = False
    
    return code


def example_multi_symbol_strategy():
    """다중 종목 전략 생성"""
    print("\n" + "=" * 60)
    print("📊 다중 종목 모멘텀 전략 생성")
    print("=" * 60)
    
    # 코스피 대형주 10종목
    symbols = [
        "005930",  # 삼성전자
        "000660",  # SK하이닉스
        "005380",  # 현대차
        "051910",  # LG화학
        "035420",  # NAVER
        "005490",  # POSCO
        "055550",  # 신한지주
        "017670",  # SK텔레콤
        "105560",  # KB금융
        "012330",  # 현대모비스
    ]
    
    code = generate_strategy(
        strategy_id="momentum",
        symbols=symbols,
        start_date=ONE_YEAR_AGO,
        end_date=TODAY,
        initial_capital=500_000_000,  # 5억원
        market_type="krx",
        params={
            "lookback": 20,
            "threshold": 0.0,  # 양수 수익률이면 매수
        },
    )
    
    print(f"\n대상 종목: {len(symbols)}개")
    print(f"전략: 모멘텀 상위 30% 종목에 투자")
    print(f"리밸런싱: 20 거래일마다")
    
    return code


def example_macd_strategy():
    """추세 필터 전략 생성"""
    print("\n" + "=" * 60)
    print("📈 추세 필터 + 시그널 전략 생성")
    print("=" * 60)

    code = generate_strategy(
        strategy_id="trend_filter_signal",
        symbols=["005930", "000660", "035420"],  # 삼성전자, SK하이닉스, NAVER
        start_date=ONE_YEAR_AGO,
        end_date=TODAY,
        initial_capital=100_000_000,  # 1억원
        market_type="krx",
        params={
            "trend_period": 60,
        },
    )

    print("\n생성된 코드 헤더:")
    print("-" * 60)
    for line in code.split("\n")[:30]:
        print(line)

    return code


def example_position_sizing():
    """포지션 사이징 옵션 데모"""
    print("\n" + "=" * 60)
    print("⚖️ 포지션 사이징 방법 비교")
    print("=" * 60)
    
    sizing_methods = [
        SizingMethod.EQUAL_WEIGHT,
        SizingMethod.INVERSE_VOLATILITY,
        SizingMethod.ATR_BASED,
        SizingMethod.KELLY,
    ]
    
    for method in sizing_methods:
        sizer = PositionSizer(method=method)
        
        print(f"\n📊 {method.value}:")
        
        init_code = sizer.generate_init()
        sizing_code = sizer.generate_sizing()
        
        print(f"   Init 코드: {'있음' if init_code.strip() else '없음'}")
        print(f"   Sizing 코드: {'있음' if sizing_code.strip() else '없음'}")
        
        if init_code.strip():
            print("   --- Init 코드 일부 ---")
            for line in init_code.strip().split("\n")[:3]:
                print(f"   {line}")


def example_strategy_categories():
    """카테고리별 전략 분류"""
    print("\n" + "=" * 60)
    print("📁 카테고리별 전략 분류")
    print("=" * 60)
    
    strategies = get_all_strategies()
    categories = {}
    
    for strategy in strategies:
        cat = strategy.get("category", "unknown")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(strategy)
    
    for category, strats in sorted(categories.items()):
        print(f"\n📂 {category.upper()}:")
        for s in strats:
            desc = s.get("description", "")[:40]
            print(f"   - {s['id']}: {desc}...")


def example_parameter_validation():
    """파라미터 검증 데모"""
    print("\n" + "=" * 60)
    print("✅ 파라미터 검증 데모")
    print("=" * 60)
    
    # 올바른 파라미터
    print("\n1. 올바른 파라미터:")
    try:
        code = generate_strategy(
            strategy_id="sma_crossover",
            symbols=["005930"],
            start_date=ONE_YEAR_AGO,
            end_date=TODAY,
            params={"fast_period": 10, "slow_period": 30},
        )
        print("   ✓ 성공: fast_period(10) < slow_period(30)")
    except ValueError as e:
        print(f"   ✗ 실패: {e}")
    
    # 잘못된 파라미터 (short >= long)
    print("\n2. 잘못된 파라미터:")
    try:
        code = generate_strategy(
            strategy_id="sma_crossover",
            symbols=["005930"],
            start_date=ONE_YEAR_AGO,
            end_date=TODAY,
            params={"fast_period": 50, "slow_period": 30},  # 잘못됨!
        )
        print("   ✓ 성공")
    except ValueError as e:
        print(f"   ✗ 검증 실패 (예상됨): {e}")
    
    # 범위 밖 파라미터
    print("\n3. 범위 밖 파라미터:")
    try:
        code = generate_strategy(
            strategy_id="sma_crossover",
            symbols=["005930"],
            start_date=ONE_YEAR_AGO,
            end_date=TODAY,
            params={"fast_period": 1, "slow_period": 500},  # 범위 초과
        )
        print("   ✓ 성공")
    except ValueError as e:
        print(f"   ✗ 검증 실패 (예상됨): {e}")


if __name__ == "__main__":
    # 1. 등록된 전략 목록
    example_list_strategies()
    
    # 2. 내장 전략 코드 생성
    example_generate_builtin_strategy()
    
    # 3. 리스크 관리 포함 전략 생성
    example_generate_with_risk_management()
    
    # 4. 다중 종목 전략
    example_multi_symbol_strategy()
    
    # 5. MACD 전략
    example_macd_strategy()
    
    # 6. 포지션 사이징 옵션
    example_position_sizing()
    
    # 7. 카테고리별 분류
    example_strategy_categories()
    
    # 8. 파라미터 검증
    example_parameter_validation()
    
    print("\n" + "=" * 60)
    print("✅ 모든 예제 완료!")
    print("=" * 60)
