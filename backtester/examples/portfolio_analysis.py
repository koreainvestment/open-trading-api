#!/usr/bin/env python3
"""
포트폴리오 분석 예제

이 예제는 여러 종목을 묶어 투자했을 때의 위험 분산 효과를 분석합니다.
상관관계, 분산 비율, 효율적 프론티어, 리밸런싱 효과를 확인합니다.

실행:
    uv run python examples/portfolio_analysis.py --example basic
    uv run python examples/portfolio_analysis.py --example correlation
    uv run python examples/portfolio_analysis.py --example frontier
    uv run python examples/portfolio_analysis.py --example rebalance
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
# 예제 1: 기본 포트폴리오 분석
# ============================================================================

def example_basic_analysis():
    """
    기본적인 포트폴리오 분석 예제

    5개 대형주로 구성된 포트폴리오의 분산 효과를 분석합니다.
    """
    print("=" * 70)
    print("예제 1: 기본 포트폴리오 분석")
    print("=" * 70)

    client = create_client()
    if client is None:
        return None

    # 포트폴리오 구성
    symbols = ["005930", "000660", "035420", "035720", "005380"]
    names = {
        "005930": "삼성전자",
        "000660": "SK하이닉스",
        "035420": "NAVER",
        "035720": "카카오",
        "005380": "현대차",
    }

    weights = {
        "005930": 0.30,  # 삼성전자 30%
        "000660": 0.20,  # SK하이닉스 20%
        "035420": 0.20,  # NAVER 20%
        "035720": 0.15,  # 카카오 15%
        "005380": 0.15,  # 현대차 15%
    }

    print("\n포트폴리오 구성:")
    print("-" * 40)
    for symbol, weight in weights.items():
        print(f"  {names[symbol]:12} ({symbol}): {weight:6.1%}")
    print("-" * 40)
    print(f"  {'합계':12}          : {sum(weights.values()):6.1%}")

    # 포트폴리오 분석 실행
    print("\n🔍 분석 중...")

    try:
        metrics = client.analyze_portfolio(
            symbols=symbols,
            start_date=ONE_YEAR_AGO,
            end_date=TODAY,
            weights=weights,
            risk_free_rate=0.035,  # 무위험 이자율 3.5%
        )

        # 결과 출력
        print("\n" + "=" * 70)
        print("포트폴리오 분석 결과")
        print("=" * 70)

        print("\n[수익/위험 지표]")
        print(f"  기대 수익률 (연율): {metrics.portfolio_return:+.2%}")
        print(f"  변동성 (연율):      {metrics.portfolio_volatility:.2%}")
        print(f"  샤프 비율:          {metrics.portfolio_sharpe:.2f}")

        print("\n[분산 효과]")
        print(f"  분산 비율: {metrics.diversification_ratio:.2f}")
        if metrics.diversification_ratio > 1:
            benefit = (metrics.diversification_ratio - 1) * 100
            print(f"  → 분산 투자로 위험이 {benefit:.1f}% 감소했습니다!")
        else:
            print(f"  → 분산 효과가 미미합니다.")

        print("\n[개별 종목 변동성]")
        for symbol in metrics.volatilities.index:
            name = names.get(symbol, symbol)
            vol = metrics.volatilities[symbol]
            print(f"  {name:12}: {vol:.2%}")

        print("\n[리스크 기여도]")
        total_risk = metrics.risk_contributions.sum()
        for symbol in metrics.risk_contributions.index:
            name = names.get(symbol, symbol)
            contrib = metrics.risk_contributions[symbol]
            pct = contrib / total_risk * 100 if total_risk > 0 else 0
            print(f"  {name:12}: {pct:5.1f}%")

        return metrics
    except Exception as e:
        print(f"  ❌ 분석 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# 예제 2: 상관관계 분석
# ============================================================================

def example_correlation_analysis():
    """
    종목간 상관관계를 분석하고 시각화합니다.

    상관관계가 낮을수록 분산 효과가 큽니다.
    """
    print("=" * 70)
    print("예제 2: 상관관계 분석")
    print("=" * 70)

    from kis_backtest.portfolio import PortfolioVisualizer

    client = create_client()
    if client is None:
        return None

    symbols = ["005930", "000660", "035420", "035720", "005380"]
    names = ["삼성전자", "SK하이닉스", "NAVER", "카카오", "현대차"]

    try:
        metrics = client.analyze_portfolio(
            symbols=symbols,
            start_date=ONE_YEAR_AGO,
            end_date=TODAY,
        )

        # 상관관계 매트릭스 출력
        print("\n상관관계 매트릭스:")
        print("-" * 60)

        corr = metrics.correlation_matrix
        corr.index = names
        corr.columns = names

        print(corr.round(2).to_string())

        # 해석
        print("\n해석:")

        # 가장 높은 상관관계
        max_corr = 0
        max_pair = ("", "")
        for i, sym1 in enumerate(symbols):
            for j, sym2 in enumerate(symbols):
                if i < j:
                    c = metrics.correlation_matrix.loc[sym1, sym2]
                    if c > max_corr:
                        max_corr = c
                        max_pair = (names[i], names[j])

        print(f"  가장 높은 상관관계: {max_pair[0]} ↔ {max_pair[1]} ({max_corr:.2f})")

        # 가장 낮은 상관관계
        min_corr = 1
        min_pair = ("", "")
        for i, sym1 in enumerate(symbols):
            for j, sym2 in enumerate(symbols):
                if i < j:
                    c = metrics.correlation_matrix.loc[sym1, sym2]
                    if c < min_corr:
                        min_corr = c
                        min_pair = (names[i], names[j])

        print(f"  가장 낮은 상관관계: {min_pair[0]} ↔ {min_pair[1]} ({min_corr:.2f})")

        if min_corr < 0.5:
            print(f"  → {min_pair[0]}와 {min_pair[1]}을 함께 보유하면 분산 효과가 큽니다!")

        # 히트맵 시각화
        print("\n히트맵 생성 중...")
        fig = PortfolioVisualizer.correlation_heatmap(metrics)

        output_path = Path("./examples/output/reports/correlation_heatmap.html")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output_path))
        print(f"   저장: {output_path}")

        return metrics
    except Exception as e:
        print(f"  ❌ 분석 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# 예제 3: 효율적 프론티어
# ============================================================================

def example_efficient_frontier():
    """
    효율적 프론티어를 계산하고 최적 포트폴리오를 찾습니다.
    """
    print("=" * 70)
    print("예제 3: 효율적 프론티어 분석")
    print("=" * 70)

    from kis_backtest.portfolio import PortfolioVisualizer

    client = create_client()
    if client is None:
        return None

    symbols = ["005930", "000660", "035420", "035720", "005380"]
    names = {
        "005930": "삼성전자",
        "000660": "SK하이닉스",
        "035420": "NAVER",
        "035720": "카카오",
        "005380": "현대차",
    }

    try:
        # 동일 비중 포트폴리오 분석
        metrics = client.analyze_portfolio(
            symbols=symbols,
            start_date=ONE_YEAR_AGO,
            end_date=TODAY,
        )

        # 효율적 프론티어 계산
        print("\n효율적 프론티어 계산 중...")
        frontier = metrics.efficient_frontier(n_points=50)

        print(f"   {len(frontier)}개 포인트 계산 완료")

        # 최적 비중 계산
        print("\n최적 포트폴리오 계산 중...")

        # 1. 최대 샤프 비율
        optimal_sharpe, metrics_sharpe = metrics.optimal_weights(objective="sharpe")

        # 2. 최소 분산
        optimal_minvar, metrics_minvar = metrics.optimal_weights(objective="min_variance")

        # 결과 출력
        print("\n" + "=" * 70)
        print("최적 포트폴리오")
        print("=" * 70)

        print("\n[1] 최대 샤프 비율 포트폴리오:")
        print(f"    샤프 비율: {metrics_sharpe.portfolio_sharpe:.2f}")
        print(f"    수익률: {metrics_sharpe.portfolio_return:+.2%}")
        print(f"    변동성: {metrics_sharpe.portfolio_volatility:.2%}")
        print("    비중:")
        for sym, w in optimal_sharpe.items():
            if w > 0.01:  # 1% 이상만 표시
                print(f"      {names[sym]:12}: {w:6.1%}")

        print("\n[2] 최소 분산 포트폴리오:")
        print(f"    샤프 비율: {metrics_minvar.portfolio_sharpe:.2f}")
        print(f"    수익률: {metrics_minvar.portfolio_return:+.2%}")
        print(f"    변동성: {metrics_minvar.portfolio_volatility:.2%}")
        print("    비중:")
        for sym, w in optimal_minvar.items():
            if w > 0.01:
                print(f"      {names[sym]:12}: {w:6.1%}")

        # 시각화
        print("\n효율적 프론티어 차트 생성 중...")
        fig = PortfolioVisualizer.efficient_frontier_plot(metrics, frontier)

        output_path = Path("./examples/output/reports/efficient_frontier.html")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output_path))
        print(f"   저장: {output_path}")

        return frontier, optimal_sharpe
    except Exception as e:
        print(f"  ❌ 분석 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# 예제 4: 리밸런싱 시뮬레이션
# ============================================================================

def example_rebalance_simulation():
    """
    정기 리밸런싱의 효과를 시뮬레이션합니다.
    """
    print("=" * 70)
    print("예제 4: 리밸런싱 시뮬레이션")
    print("=" * 70)

    from kis_backtest.portfolio import PortfolioVisualizer

    client = create_client()
    if client is None:
        return None

    symbols = ["005930", "000660", "035420"]
    names = {"005930": "삼성전자", "000660": "SK하이닉스", "035420": "NAVER"}

    weights = {
        "005930": 0.40,
        "000660": 0.35,
        "035420": 0.25,
    }

    print("\n목표 비중:")
    for sym, w in weights.items():
        print(f"  {names[sym]}: {w:.0%}")

    try:
        # 다양한 리밸런싱 주기 비교
        periods = ["monthly", "quarterly"]
        results = {}

        print("\n리밸런싱 시뮬레이션...")

        for period in periods:
            result = client.simulate_rebalance(
                symbols=symbols,
                start_date=ONE_YEAR_AGO,
                end_date=TODAY,
                weights=weights,
                period=period,
                initial_capital=100_000_000,
            )
            results[period] = result

            period_kr = "월간" if period == "monthly" else "분기"
            print(f"\n  [{period_kr} 리밸런싱]")
            print(f"   최종 수익률: {result.final_return:+.2%}")
            print(f"   리밸런싱 횟수: {len(result.rebalance_dates)}회")
            print(f"   총 회전율: {result.turnover:.2%}")

        # Buy & Hold 와 비교
        print("\n  [Buy & Hold (리밸런싱 없음)]")
        print(f"   최종 수익률: {results['monthly'].no_rebalance_return:+.2%}")

        # 리밸런싱 효과 분석
        print("\n" + "=" * 70)
        print("리밸런싱 효과 분석")
        print("=" * 70)

        for period, result in results.items():
            period_kr = "월간" if period == "monthly" else "분기"
            benefit = result.rebalance_benefit

            if benefit > 0:
                print(f"  {period_kr}: 리밸런싱으로 {benefit:+.2%} 추가 수익")
            else:
                print(f"  {period_kr}: 리밸런싱 비용이 효과를 상쇄 ({benefit:+.2%})")

        # 시각화
        print("\n비교 차트 생성 중...")
        fig = PortfolioVisualizer.rebalance_comparison(results["monthly"])

        output_path = Path("./examples/output/reports/rebalance_comparison.html")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output_path))
        print(f"   저장: {output_path}")

        return results
    except Exception as e:
        print(f"  ❌ 시뮬레이션 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# 예제 5: 종합 분석 리포트
# ============================================================================

def example_comprehensive_report():
    """
    포트폴리오에 대한 종합 분석 리포트를 생성합니다.
    """
    print("=" * 70)
    print("예제 5: 종합 포트폴리오 분석 리포트")
    print("=" * 70)

    client = create_client()
    if client is None:
        return None

    symbols = ["005930", "000660", "035420", "035720", "005380"]
    weights = {"005930": 0.3, "000660": 0.2, "035420": 0.2, "035720": 0.15, "005380": 0.15}

    try:
        # 분석 실행
        metrics = client.analyze_portfolio(
            symbols=symbols,
            start_date=ONE_YEAR_AGO,
            end_date=TODAY,
            weights=weights,
        )

        # 리밸런싱 시뮬레이션
        rebalance = client.simulate_rebalance(
            symbols=symbols,
            start_date=ONE_YEAR_AGO,
            end_date=TODAY,
            weights=weights,
            period="monthly",
        )

        # 리포트 생성
        print("\n리포트 생성 중...")

        symbol_names = {
            "005930": "삼성전자",
            "000660": "SK하이닉스",
            "035420": "NAVER",
            "035720": "카카오",
            "005380": "현대차",
        }

        report_path = client.portfolio_report(
            metrics=metrics,
            output_path="./examples/output/reports/portfolio_report.html",
            title=f"{date.today().year}년 포트폴리오 분석 리포트",
            rebalance_result=rebalance,
            symbol_names=symbol_names,
        )

        print(f"   저장: {report_path}")
        print("\n✅ 리포트 생성 완료!")

        return metrics, rebalance
    except Exception as e:
        print(f"  ❌ 리포트 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# 메인 실행
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="포트폴리오 분석 예제",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  basic       - 기본 포트폴리오 분석
  correlation - 상관관계 분석 및 히트맵
  frontier    - 효율적 프론티어 및 최적 비중
  rebalance   - 리밸런싱 시뮬레이션
  report      - 종합 분석 리포트

실행:
  uv run python examples/portfolio_analysis.py --example basic
        """
    )

    parser.add_argument(
        "--example",
        choices=["basic", "correlation", "frontier", "rebalance", "report", "all"],
        default="basic",
        help="실행할 예제 선택"
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("KIS Backtest - 포트폴리오 분석 예제")
    print("=" * 70)

    examples = {
        "basic": example_basic_analysis,
        "correlation": example_correlation_analysis,
        "frontier": example_efficient_frontier,
        "rebalance": example_rebalance_simulation,
        "report": example_comprehensive_report,
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
