#!/usr/bin/env python3
"""
P1: 파라미터 최적화 예제

이 예제는 전략 파라미터를 자동으로 최적화하는 방법을 보여줍니다.
Grid Search와 Random Search를 사용하여 최적의 파라미터 조합을 찾습니다.

실행:
    uv run python examples/optimization.py --example basic
    uv run python examples/optimization.py --example grid
    uv run python examples/optimization.py --example random
    uv run python examples/optimization.py --example visualize

⚠️ 모의투자 계좌는 REST API 초당 호출 제한이 낮아 다수의 백테스트를
   연속 실행하는 최적화에 적합하지 않습니다. 실전투자 계좌 사용을 권장합니다.
"""

import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

# 날짜 설정: 오늘 기준 1년 데이터
TODAY = date.today().strftime("%Y-%m-%d")
ONE_YEAR_AGO = (date.today() - timedelta(days=365)).strftime("%Y-%m-%d")


# ============================================================================
# 클라이언트 생성 헬퍼
# ============================================================================

def create_client():
    """KIS API 인증 및 LeanClient 생성"""
    from kis_backtest import LeanClient
    from kis_backtest.providers.kis import KISAuth, KISDataProvider

    try:
        auth = KISAuth.from_env()
        data_provider = KISDataProvider(auth)

        mode_str = "모의투자" if auth.is_paper else "실전투자"
        print(f"  ✓ 인증 성공 ({mode_str}, 계좌: {auth.acct_masked})")

        return LeanClient(data_provider=data_provider)
    except Exception as e:
        print(f"  ✗ 인증 실패: {e}")
        print("\n💡 KIS API 인증 정보를 설정하세요.")
        return None


# ============================================================================
# 예제 1: 기본 최적화
# ============================================================================

def example_basic_optimization():
    """
    가장 간단한 파라미터 최적화 예제

    SMA 크로스오버 전략의 단기/장기 이동평균 기간을 최적화합니다.
    """
    print("=" * 70)
    print("📊 기본 파라미터 최적화 예제")
    print("=" * 70)

    print("\n[1/3] 한국투자증권 API 인증 중...")
    client = create_client()
    if client is None:
        return None
    
    # 최적화 실행
    print("\n최적화 파라미터:")
    print("  - fast_period: 5 ~ 20 (step: 5)")
    print("  - slow_period: 20 ~ 60 (step: 10)")
    print("  - 총 조합: 4 × 5 = 20개")
    print()
    
    result = client.optimize(
        strategy_id="sma_crossover",
        symbols=["005930"],  # 삼성전자
        start_date=ONE_YEAR_AGO,
        end_date=TODAY,
        parameters=[
            ("fast_period", 5, 20, 5),   # (이름, 최소, 최대, 스텝)
            ("slow_period", 20, 60, 10),
        ],
        target="sharpe_ratio",        # 최적화 목표
        target_direction="max",       # 최대화
    )
    
    # 결과 출력
    print("=" * 70)
    print("🏆 최적화 결과")
    print("=" * 70)
    print(f"  총 백테스트: {result.total_backtests}")
    print(f"  성공: {result.successful_backtests}")
    print(f"  실패: {result.failed_backtests}")
    print(f"  소요 시간: {result.elapsed_time:.1f}초")
    print()
    print(f"  📌 최적 파라미터:")
    for param, value in result.best_parameters.items():
        print(f"     - {param}: {value}")
    print()
    print(f"  📈 최적 성과:")
    print(f"     - 샤프 비율: {result.best_sharpe:.2f}")
    print(f"     - 수익률: {result.best_return:.2%}")
    print(f"     - 최대 낙폭: {result.best_drawdown:.2%}")
    
    return result


# ============================================================================
# 예제 2: Grid Search 상세
# ============================================================================

def example_grid_search():
    """
    Grid Search로 모든 파라미터 조합을 탐색합니다.
    진행률 콜백을 사용하여 실시간 진행 상황을 확인합니다.
    """
    print("=" * 70)
    print("📊 Grid Search 최적화")
    print("=" * 70)

    print("\n[1/3] 한국투자증권 API 인증 중...")
    client = create_client()
    if client is None:
        return None
    
    # 진행률 콜백 정의
    def on_progress(completed: int, total: int, run):
        """각 백테스트 완료 시 호출되는 콜백"""
        pct = completed / total * 100
        
        if run.result:
            status = f"✅ Sharpe: {run.result.sharpe_ratio:+.2f}, Return: {run.result.total_return_pct:+.2%}"
        else:
            status = f"❌ Error: {run.error}"
        
        params_str = ", ".join(f"{k}={v}" for k, v in run.params.items())
        print(f"  [{completed:3}/{total}] ({pct:5.1f}%) {params_str} → {status}")
    
    print("\n최적화 실행 중...\n")
    
    result = client.optimize(
        strategy_id="sma_crossover",
        symbols=["005930"],
        start_date=ONE_YEAR_AGO,
        end_date=TODAY,
        parameters=[
            ("fast_period", 5, 15, 5),   # 3개: 5, 10, 15
            ("slow_period", 20, 40, 10),  # 3개: 20, 30, 40
        ],
        target="sharpe_ratio",
        strategy="grid",  # Grid Search
        on_progress=on_progress,
    )
    
    print("\n" + "=" * 70)
    print("📋 전체 결과 (샤프 비율 순)")
    print("=" * 70)
    
    # DataFrame으로 정렬된 결과 출력
    df = result.results_df
    if df is not None:
        df_sorted = df.sort_values("sharpe_ratio", ascending=False)
        print(df_sorted.to_string(index=False))
    
    return result


# ============================================================================
# 예제 3: Random Search
# ============================================================================

def example_random_search():
    """
    Random Search로 무작위 샘플링 탐색을 수행합니다.
    파라미터 공간이 클 때 효율적입니다.
    """
    print("=" * 70)
    print("📊 Random Search 최적화")
    print("=" * 70)

    print("\n[1/3] 한국투자증권 API 인증 중...")
    client = create_client()
    if client is None:
        return None
    
    # 넓은 파라미터 공간
    # 전체 조합: 16 × 41 × 7 = 4,592개
    # 하지만 100개만 샘플링
    
    print("\n파라미터 공간:")
    print("  - fast_period: 5 ~ 20 (step: 1) → 16개")
    print("  - slow_period: 20 ~ 60 (step: 1) → 41개")
    print("  - 전체 조합: ~4,600개")
    print("  - 샘플링: 100개 (Random Search)")
    print()
    
    result = client.optimize(
        strategy_id="sma_crossover",
        symbols=["005930"],
        start_date=ONE_YEAR_AGO,
        end_date=TODAY,
        parameters=[
            ("fast_period", 5, 20, 1),
            ("slow_period", 20, 60, 1),
        ],
        target="sharpe_ratio",
        strategy="random",   # Random Search
        max_samples=100,     # 100개만 샘플링
    )
    
    print("=" * 70)
    print("🏆 Random Search 결과")
    print("=" * 70)
    print(f"  샘플링 수: {result.total_backtests}")
    print(f"  최적 파라미터: {result.best_parameters}")
    print(f"  샤프 비율: {result.best_sharpe:.2f}")
    
    # 통계
    if result.statistics:
        print("\n📈 통계:")
        print(f"  샤프 평균: {result.statistics['sharpe_mean']:.2f}")
        print(f"  샤프 표준편차: {result.statistics['sharpe_std']:.2f}")
    
    return result


# ============================================================================
# 예제 4: 결과 시각화
# ============================================================================

def example_visualize_results():
    """
    최적화 결과를 시각화합니다.
    파라미터별 성과 히트맵을 생성합니다.
    """
    print("=" * 70)
    print("📊 최적화 결과 시각화")
    print("=" * 70)

    print("\n[1/3] 한국투자증권 API 인증 중...")
    client = create_client()
    if client is None:
        return None

    import plotly.express as px
    import plotly.graph_objects as go
    
    # 최적화 실행
    result = client.optimize(
        strategy_id="sma_crossover",
        symbols=["005930"],
        start_date=ONE_YEAR_AGO,
        end_date=TODAY,
        parameters=[
            ("fast_period", 5, 20, 5),
            ("slow_period", 20, 60, 10),
        ],
        target="sharpe_ratio",
    )
    
    df = result.results_df
    
    if df is None or df.empty:
        print("결과 데이터가 없습니다.")
        return
    
    # 1. 샤프 비율 히트맵
    pivot = df.pivot(index="fast_period", columns="slow_period", values="sharpe_ratio")
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale="RdYlGn",
        text=pivot.round(2).values,
        texttemplate="%{text}",
        textfont={"size": 14},
    ))
    
    fig.update_layout(
        title="파라미터별 샤프 비율",
        xaxis_title="Long Window",
        yaxis_title="Short Window",
        width=600,
        height=500,
    )
    
    # HTML 파일로 저장
    output_path = Path("./examples/output/reports/optimization_heatmap.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path))
    print(f"\n히트맵 저장: {output_path}")
    
    # 2. 산점도 (수익률 vs 변동성)
    if "total_return_pct" in df.columns and "max_drawdown" in df.columns:
        fig2 = px.scatter(
            df,
            x="max_drawdown",
            y="total_return_pct",
            color="sharpe_ratio",
            size="sharpe_ratio",
            hover_data=["fast_period", "slow_period"],
            title="수익률 vs 최대낙폭",
            labels={
                "max_drawdown": "최대 낙폭 (%)",
                "total_return_pct": "총 수익률 (%)",
                "sharpe_ratio": "샤프 비율",
            },
        )
        
        output_path2 = Path("./examples/output/reports/optimization_scatter.html")
        fig2.write_html(str(output_path2))
        print(f"산점도 저장: {output_path2}")
    
    return result


# ============================================================================
# 예제 5: 다중 전략 비교 최적화
# ============================================================================

def example_multi_strategy_optimization():
    """
    여러 전략을 동시에 최적화하고 비교합니다.
    """
    print("=" * 70)
    print("📊 다중 전략 비교 최적화")
    print("=" * 70)

    print("\n[1/3] 한국투자증권 API 인증 중...")
    client = create_client()
    if client is None:
        return None
    
    strategies = [
        {
            "id": "sma_crossover",
            "name": "SMA 골든크로스",
            "params": [("fast_period", 5, 20, 5), ("slow_period", 20, 60, 20)],
        },
        {
            "id": "rsi",
            "name": "RSI 과매수/과매도",
            "params": [("period", 7, 21, 7), ("oversold", 20, 30, 5), ("overbought", 70, 80, 5)],
        },
        {
            "id": "bollinger",
            "name": "볼린저 밴드",
            "params": [("period", 10, 30, 10), ("std", 1.5, 2.5, 0.5)],
        },
    ]
    
    results = {}
    
    for strategy in strategies:
        print(f"\n🔄 {strategy['name']} 최적화 중...")
        
        result = client.optimize(
            strategy_id=strategy["id"],
            symbols=["005930"],
            start_date=ONE_YEAR_AGO,
            end_date=TODAY,
            parameters=strategy["params"],
            target="sharpe_ratio",
        )
        
        results[strategy["name"]] = {
            "best_sharpe": result.best_sharpe,
            "best_return": result.best_return,
            "best_params": result.best_parameters,
        }
        
        print(f"   최적 샤프: {result.best_sharpe:.2f}")
    
    # 결과 비교
    print("\n" + "=" * 70)
    print("🏆 전략 비교 결과 (샤프 비율 순)")
    print("=" * 70)
    
    sorted_results = sorted(results.items(), key=lambda x: x[1]["best_sharpe"], reverse=True)
    
    for rank, (name, data) in enumerate(sorted_results, 1):
        medal = "🥇" if rank == 1 else ("🥈" if rank == 2 else "🥉")
        print(f"\n{medal} {rank}위: {name}")
        print(f"   샤프 비율: {data['best_sharpe']:.2f}")
        print(f"   수익률: {data['best_return']:.2%}")
        print(f"   파라미터: {data['best_params']}")
    
    return results


# ============================================================================
# 메인 실행
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="P1: 파라미터 최적화 예제",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  basic     - 기본 최적화 예제
  grid      - Grid Search 상세 예제
  random    - Random Search 예제
  visualize - 결과 시각화 예제
  multi     - 다중 전략 비교

실행:
  uv run python examples/optimization.py --example basic
        """
    )
    
    parser.add_argument(
        "--example",
        choices=["basic", "grid", "random", "visualize", "multi", "all"],
        default="basic",
        help="실행할 예제 선택"
    )
    
    args = parser.parse_args()
    
    examples = {
        "basic": example_basic_optimization,
        "grid": example_grid_search,
        "random": example_random_search,
        "visualize": example_visualize_results,
        "multi": example_multi_strategy_optimization,
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
            print()
    else:
        examples[args.example]()
    
    print("\n✅ 완료!")
