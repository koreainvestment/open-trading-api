#!/usr/bin/env python3
"""
간편 전략 입력 예제 (Rule Builder)

이 예제는 코딩 없이 매매 규칙을 정의하고 백테스트하는 방법을 보여줍니다.
RuleBuilder를 사용하여 직관적인 방식으로 전략을 구성합니다.

실행:
    uv run python examples/rule_builder.py --example basic
    uv run python examples/rule_builder.py --example indicators
    uv run python examples/rule_builder.py --example complex
    uv run python examples/rule_builder.py --example compare
"""

import sys
from datetime import date, timedelta
from pathlib import Path

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from kis_backtest import LeanClient
from kis_backtest.providers.kis import KISAuth, KISDataProvider

# 날짜 설정: 오늘 기준 1년 데이터
TODAY = date.today().strftime("%Y-%m-%d")
ONE_YEAR_AGO = (date.today() - timedelta(days=365)).strftime("%Y-%m-%d")


def create_client():
    """KIS API 인증 및 LeanClient 생성"""
    try:
        auth = KISAuth.from_env()
        data_provider = KISDataProvider(auth)
        mode_str = "모의투자" if auth.is_paper else "실전투자"
        print(f"  ✓ KIS 인증 ({mode_str})")
        return LeanClient(data_provider=data_provider)
    except Exception as e:
        print(f"  ✗ 인증 실패: {e}")
        print("    KIS API 인증 정보를 설정하세요.")
        return None


# ============================================================================
# 예제 1: 기본 사용법
# ============================================================================

def example_basic_usage():
    """
    가장 간단한 RuleBuilder 사용 예제

    코드 대신 조건을 조합하여 전략을 만듭니다.
    """
    print("=" * 70)
    print("예제 1: 기본 RuleBuilder 사용법")
    print("=" * 70)

    from kis_backtest.dsl import RuleBuilder
    from kis_backtest.dsl.helpers import SMA

    client = create_client()
    if client is None:
        return None

    # 전략 정의: SMA 골든크로스
    print("\n전략 정의:")
    print("-" * 50)
    print("  전략명: 골든크로스")
    print("  매수 조건: 5일 이동평균 > 20일 이동평균")
    print("  매도 조건: 5일 이동평균 < 20일 이동평균")
    print("-" * 50)

    # RuleBuilder로 전략 생성
    strategy = (
        RuleBuilder("골든크로스")
        .buy_when(SMA(5) > SMA(20))
        .sell_when(SMA(5) < SMA(20))
        .build()
    )

    print("\n✅ 전략이 생성되었습니다!")
    print(f"   전략 객체: {strategy.name}")
    print(f"   사용 지표: {[ind.alias for ind in strategy.indicators]}")

    # 백테스트 실행
    print("\n🔄 백테스트 실행 중...")

    try:
        result = client.backtest_rule(
            rule=strategy,
            symbols=["005930"],  # 삼성전자
            start_date=ONE_YEAR_AGO,
            end_date=TODAY,
        )

        # 결과 출력
        print("\n" + "=" * 70)
        print("백테스트 결과")
        print("=" * 70)
        print(f"  수익률: {result.total_return_pct:+.2f}%")
        print(f"  샤프 비율: {result.sharpe_ratio:.2f}")
        print(f"  최대 낙폭: {result.max_drawdown:.2f}%")
        print(f"  총 거래: {result.total_trades}회")
        print(f"  승률: {result.win_rate:.1%}")

        return result
    except Exception as e:
        print(f"  ❌ 백테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# 예제 2: 다양한 지표 사용
# ============================================================================

def example_various_indicators():
    """
    다양한 기술적 지표를 사용하는 예제

    SMA, EMA, RSI, MACD, 볼린저밴드 등을 활용합니다.
    """
    print("=" * 70)
    print("예제 2: 다양한 지표 사용")
    print("=" * 70)

    from kis_backtest.dsl import RuleBuilder
    from kis_backtest.dsl.helpers import SMA, EMA, RSI, MACD, BB, ATR, STOCH, Price

    client = create_client()
    if client is None:
        return None

    # 전략 1: RSI 과매수/과매도
    print("\n[1] RSI 전략")
    print("   매수: RSI(14) < 30 (과매도)")
    print("   매도: RSI(14) > 70 (과매수)")

    strategy_rsi = (
        RuleBuilder("RSI 과매수/과매도")
        .buy_when(RSI(14) < 30)
        .sell_when(RSI(14) > 70)
        .stop_loss(5.0)
        .take_profit(10.0)
        .build()
    )

    # 전략 2: MACD 시그널
    print("\n[2] MACD 시그널 크로스")
    print("   매수: MACD가 시그널선 상향돌파")
    print("   매도: MACD가 시그널선 하향돌파")

    macd = MACD(12, 26, 9)
    macd_signal = MACD(12, 26, 9, output="signal")

    strategy_macd = (
        RuleBuilder("MACD 시그널")
        .buy_when(macd.crosses_above(macd_signal))
        .sell_when(macd.crosses_below(macd_signal))
        .build()
    )

    # 전략 3: 볼린저밴드 반전
    print("\n[3] 볼린저밴드 반전")
    print("   매수: 가격이 하단밴드 터치")
    print("   매도: 가격이 상단밴드 터치")

    bb = BB(20, 2.0)

    strategy_bb = (
        RuleBuilder("볼린저밴드 반전")
        .buy_when(Price.close() < bb.lower)
        .sell_when(Price.close() > bb.upper)
        .trailing_stop(3.0)
        .build()
    )

    # 전략 4: 스토캐스틱
    print("\n[4] 스토캐스틱")
    print("   매수: Stochastic K < 20")
    print("   매도: Stochastic K > 80")

    strategy_stoch = (
        RuleBuilder("스토캐스틱")
        .buy_when(STOCH(14, 3) < 20)
        .sell_when(STOCH(14, 3) > 80)
        .build()
    )

    # 백테스트 실행
    strategies = [
        ("RSI", strategy_rsi),
        ("MACD", strategy_macd),
        ("볼린저밴드", strategy_bb),
        ("스토캐스틱", strategy_stoch),
    ]

    print("\n" + "=" * 70)
    print("🔄 백테스트 실행")
    print("=" * 70)

    results = {}
    for name, strategy in strategies:
        try:
            result = client.backtest_rule(
                rule=strategy,
                symbols=["005930"],
                start_date=ONE_YEAR_AGO,
                end_date=TODAY,
            )
            results[name] = result
            print(f"  {name:15}: 수익률 {result.total_return_pct:+.2f}%, 샤프 {result.sharpe_ratio:.2f}")
        except Exception as e:
            print(f"  {name:15}: ❌ 오류 - {e}")

    return results


# ============================================================================
# 예제 3: 복합 조건
# ============================================================================

def example_complex_conditions():
    """
    AND/OR를 사용한 복합 조건 예제

    여러 조건을 조합하여 더 정교한 전략을 만듭니다.
    """
    print("=" * 70)
    print("예제 3: 복합 조건 전략")
    print("=" * 70)

    from kis_backtest.dsl import RuleBuilder
    from kis_backtest.dsl.helpers import SMA, EMA, RSI, MACD, BB, Price

    client = create_client()
    if client is None:
        return None

    # 전략 1: 골든크로스 + RSI 필터
    print("\n[1] 골든크로스 + RSI 필터")
    print("   매수: (SMA(5) > SMA(20)) AND (RSI(14) < 70)")
    print("   매도: (SMA(5) < SMA(20)) OR (RSI(14) > 80)")

    strategy1 = (
        RuleBuilder("골든크로스 + RSI")
        .buy_when(
            (SMA(5) > SMA(20)) & (RSI(14) < 70)
        )
        .sell_when(
            (SMA(5) < SMA(20)) | (RSI(14) > 80)
        )
        .stop_loss(5.0)
        .build()
    )

    # 전략 2: 추세 필터 + 시그널
    print("\n[2] 추세 필터 + 시그널")
    print("   매수: (가격 > SMA(60)) AND (SMA(5) > SMA(20)) AND (RSI(14) < 70)")
    print("   매도: (가격 < SMA(60)) OR ((SMA(5) < SMA(20)) AND (RSI(14) > 50))")

    strategy2 = (
        RuleBuilder("추세필터 복합전략")
        .buy_when(
            (Price.close() > SMA(60)) &  # 상승 추세
            (SMA(5) > SMA(20)) &          # 골든크로스
            (RSI(14) < 70)                # 과열 아님
        )
        .sell_when(
            (Price.close() < SMA(60)) |   # 추세 이탈
            ((SMA(5) < SMA(20)) & (RSI(14) > 50))  # 데드크로스 + 약세
        )
        .stop_loss(7.0)
        .take_profit(15.0)
        .build()
    )

    # 전략 3: 볼린저 + RSI 조합
    print("\n[3] 볼린저 + RSI 조합")
    print("   매수: (가격 < BB하단) AND (RSI(14) < 30)")
    print("   매도: (가격 > BB상단) OR (RSI(14) > 70)")

    bb = BB(20, 2.0)

    strategy3 = (
        RuleBuilder("볼린저 + RSI")
        .buy_when(
            (Price.close() < bb.lower) & (RSI(14) < 30)
        )
        .sell_when(
            (Price.close() > bb.upper) | (RSI(14) > 70)
        )
        .stop_loss(3.0)
        .build()
    )

    # 백테스트 실행
    print("\n" + "=" * 70)
    print("🔄 백테스트 결과")
    print("=" * 70)

    strategies = [
        ("골든크로스+RSI", strategy1),
        ("추세필터 복합", strategy2),
        ("볼린저+RSI", strategy3),
    ]

    for name, strategy in strategies:
        try:
            result = client.backtest_rule(
                rule=strategy,
                symbols=["005930"],
                start_date=ONE_YEAR_AGO,
                end_date=TODAY,
            )
            print(f"\n  {name}")
            print(f"     수익률: {result.total_return_pct:+.2f}%")
            print(f"     샤프: {result.sharpe_ratio:.2f}")
            print(f"     MDD: {result.max_drawdown:.2f}%")
            print(f"     거래수: {result.total_trades}")
        except Exception as e:
            print(f"\n  ❌ {name}: {e}")


# ============================================================================
# 예제 4: 크로스오버 이벤트
# ============================================================================

def example_crossover_events():
    """
    crosses_above, crosses_below를 사용한 크로스오버 전략

    "돌파" 시점에만 매매하는 전략입니다.
    """
    print("=" * 70)
    print("예제 4: 크로스오버 이벤트 전략")
    print("=" * 70)

    from kis_backtest.dsl import RuleBuilder
    from kis_backtest.dsl.helpers import SMA, EMA, RSI, MACD

    client = create_client()
    if client is None:
        return None

    # 전략 1: SMA 크로스오버
    print("\n[1] SMA 크로스오버")
    print("   매수: SMA(5)가 SMA(20)을 상향 돌파하는 순간")
    print("   매도: SMA(5)가 SMA(20)을 하향 돌파하는 순간")

    strategy1 = (
        RuleBuilder("SMA 크로스오버")
        .buy_when(SMA(5).crosses_above(SMA(20)))
        .sell_when(SMA(5).crosses_below(SMA(20)))
        .build()
    )

    # 전략 2: RSI 레벨 크로스
    print("\n[2] RSI 레벨 크로스")
    print("   매수: RSI(14)가 30 레벨을 상향 돌파")
    print("   매도: RSI(14)가 70 레벨을 하향 돌파")

    strategy2 = (
        RuleBuilder("RSI 레벨크로스")
        .buy_when(RSI(14).crosses_above(30))
        .sell_when(RSI(14).crosses_below(70))
        .stop_loss(5.0)
        .build()
    )

    # 전략 3: EMA 다중 크로스
    print("\n[3] EMA 삼중 크로스")
    print("   매수: EMA(5)가 EMA(10)을 돌파하고 EMA(10) > EMA(20)")
    print("   매도: EMA(5)가 EMA(10)을 하향돌파")

    strategy3 = (
        RuleBuilder("EMA 삼중크로스")
        .buy_when(
            EMA(5).crosses_above(EMA(10)) & (EMA(10) > EMA(20))
        )
        .sell_when(EMA(5).crosses_below(EMA(10)))
        .build()
    )

    # 백테스트 실행
    print("\n" + "=" * 70)
    print("🔄 백테스트 결과")
    print("=" * 70)

    strategies = [
        ("SMA 크로스", strategy1),
        ("RSI 레벨크로스", strategy2),
        ("EMA 삼중크로스", strategy3),
    ]

    for name, strategy in strategies:
        try:
            result = client.backtest_rule(
                rule=strategy,
                symbols=["005930"],
                start_date=ONE_YEAR_AGO,
                end_date=TODAY,
            )
            print(f"  {name:15}: 수익률 {result.total_return_pct:+.2f}%, 거래 {result.total_trades}회")
        except Exception as e:
            print(f"  {name:15}: ❌ {e}")


# ============================================================================
# 예제 5: 리스크 관리
# ============================================================================

def example_risk_management():
    """
    손절, 익절, 트레일링 스탑을 사용하는 예제
    """
    print("=" * 70)
    print("예제 5: 리스크 관리 전략")
    print("=" * 70)

    from kis_backtest.dsl import RuleBuilder
    from kis_backtest.dsl.helpers import SMA, RSI

    client = create_client()
    if client is None:
        return None

    # 동일한 진입/청산 조건으로 리스크 관리만 다르게 설정
    base_buy = SMA(5) > SMA(20)
    base_sell = SMA(5) < SMA(20)

    strategies = [
        # 리스크 관리 없음
        (
            "리스크관리 없음",
            RuleBuilder("무위험관리")
            .buy_when(base_buy)
            .sell_when(base_sell)
            .build()
        ),
        # 손절만
        (
            "손절 5%",
            RuleBuilder("손절만")
            .buy_when(base_buy)
            .sell_when(base_sell)
            .stop_loss(5.0)
            .build()
        ),
        # 손절 + 익절
        (
            "손절5% + 익절10%",
            RuleBuilder("손절+익절")
            .buy_when(base_buy)
            .sell_when(base_sell)
            .stop_loss(5.0)
            .take_profit(10.0)
            .build()
        ),
        # 트레일링 스탑
        (
            "트레일링 5%",
            RuleBuilder("트레일링")
            .buy_when(base_buy)
            .sell_when(base_sell)
            .trailing_stop(5.0)
            .build()
        ),
        # 복합 리스크 관리
        (
            "복합 (손절3% + 트레일링5%)",
            RuleBuilder("복합리스크")
            .buy_when(base_buy)
            .sell_when(base_sell)
            .stop_loss(3.0)
            .trailing_stop(5.0)
            .build()
        ),
    ]

    print("\n전략 설정:")
    print("   기본 매수: SMA(5) > SMA(20)")
    print("   기본 매도: SMA(5) < SMA(20)")
    print("   + 다양한 리스크 관리 옵션")

    print("\n" + "=" * 70)
    print("🔄 백테스트 결과 비교")
    print("=" * 70)

    print(f"\n  {'전략':25} {'수익률':>10} {'MDD':>10} {'승률':>8} {'거래':>6}")
    print("  " + "-" * 65)

    for name, strategy in strategies:
        try:
            result = client.backtest_rule(
                rule=strategy,
                symbols=["005930"],
                start_date=ONE_YEAR_AGO,
                end_date=TODAY,
            )
            print(f"  {name:25} {result.total_return_pct:>+9.2f}% {result.max_drawdown:>9.2f}% {result.win_rate:>7.1%} {result.total_trades:>6}")
        except Exception as e:
            print(f"  {name:25} ❌ {e}")


# ============================================================================
# 예제 6: 전략 비교
# ============================================================================

def example_compare_strategies():
    """
    여러 전략을 한번에 비교합니다.
    """
    print("=" * 70)
    print("예제 6: 전략 비교")
    print("=" * 70)

    from kis_backtest.dsl import RuleBuilder
    from kis_backtest.dsl.helpers import SMA, EMA, RSI, MACD, BB, Price

    client = create_client()
    if client is None:
        return None

    # 비교할 전략들
    strategies = {
        "SMA 골든크로스": (
            RuleBuilder("SMA")
            .buy_when(SMA(5) > SMA(20))
            .sell_when(SMA(5) < SMA(20))
            .stop_loss(5.0)
            .build()
        ),
        "EMA 크로스": (
            RuleBuilder("EMA")
            .buy_when(EMA(12).crosses_above(EMA(26)))
            .sell_when(EMA(12).crosses_below(EMA(26)))
            .stop_loss(5.0)
            .build()
        ),
        "RSI 과매수/과매도": (
            RuleBuilder("RSI")
            .buy_when(RSI(14) < 30)
            .sell_when(RSI(14) > 70)
            .stop_loss(5.0)
            .build()
        ),
        "볼린저밴드 반전": (
            RuleBuilder("BB")
            .buy_when(Price.close() < BB(20, 2).lower)
            .sell_when(Price.close() > BB(20, 2).upper)
            .stop_loss(5.0)
            .build()
        ),
        "추세+RSI 복합": (
            RuleBuilder("복합")
            .buy_when((Price.close() > SMA(60)) & (RSI(14) < 50) & (SMA(5) > SMA(20)))
            .sell_when((Price.close() < SMA(60)) | (RSI(14) > 70))
            .stop_loss(5.0)
            .take_profit(15.0)
            .build()
        ),
    }

    print("\n🔄 백테스트 실행 중...")

    results = {}
    for name, strategy in strategies.items():
        try:
            result = client.backtest_rule(
                rule=strategy,
                symbols=["005930"],
                start_date=ONE_YEAR_AGO,
                end_date=TODAY,
            )
            results[name] = result
            print(f"  ✅ {name}")
        except Exception as e:
            print(f"  ❌ {name}: {e}")

    if not results:
        print("\n  ❌ 모든 백테스트 실패")
        return None

    # 결과 정렬 및 출력
    print("\n" + "=" * 70)
    print("전략 비교 결과 (샤프 비율 순)")
    print("=" * 70)

    sorted_results = sorted(
        results.items(),
        key=lambda x: x[1].sharpe_ratio,
        reverse=True
    )

    print(f"\n  {'순위':4} {'전략':20} {'샤프':>8} {'수익률':>10} {'MDD':>10} {'승률':>8}")
    print("  " + "-" * 68)

    medals = ["1st", "2nd", "3rd", "   ", "   "]

    for i, (name, result) in enumerate(sorted_results):
        medal = medals[min(i, 4)]
        print(f"  {medal:4} {name:20} {result.sharpe_ratio:>7.2f} {result.total_return_pct:>+9.2f}% {result.max_drawdown:>9.2f}% {result.win_rate:>7.1%}")

    return results


# ============================================================================
# 메인 실행
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="간편 전략 입력 예제 (Rule Builder)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  basic      - 기본 사용법
  indicators - 다양한 지표 사용
  complex    - 복합 조건 (AND/OR)
  crossover  - 크로스오버 이벤트
  risk       - 리스크 관리
  compare    - 전략 비교

실행:
  uv run python examples/rule_builder.py --example basic
        """
    )

    parser.add_argument(
        "--example",
        choices=["basic", "indicators", "complex", "crossover", "risk", "compare", "all"],
        default="basic",
        help="실행할 예제 선택"
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("KIS Backtest - RuleBuilder 예제")
    print("=" * 70)

    examples = {
        "basic": example_basic_usage,
        "indicators": example_various_indicators,
        "complex": example_complex_conditions,
        "crossover": example_crossover_events,
        "risk": example_risk_management,
        "compare": example_compare_strategies,
    }

    if args.example == "all":
        for name, func in examples.items():
            print(f"\n{'=' * 70}")
            print(f"예제: {name}")
            print("=" * 70)
            try:
                func()
            except Exception as e:
                print(f"❌ 오류: {e}")
                import traceback
                traceback.print_exc()
            print()
    else:
        examples[args.example]()

    print("\n✅ 완료!")
