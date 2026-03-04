#!/usr/bin/env python3
"""
Expert Sample 10종 전략 예제

이 파일은 실전에서 많이 사용되는 10가지 핵심 전략을 사용자 스토리별로 보여줍니다.

📖 사용자 스토리:
1. 초보자: "처음 백테스트를 해보고 싶어요" → 가장 간단한 SMA 크로스오버
2. 중급자: "여러 전략을 비교해보고 싶어요" → 10가지 전략 일괄 비교
3. 연구자: "전략을 커스터마이징하고 싶어요" → 파라미터 튜닝

📌 10가지 Expert Sample 전략:
1. 단순 이동평균 골든크로스 - sma_crossover
2. 모멘텀 - momentum
3. 52주 신고가 돌파 - week52_high
4. n일 연속 상승·하락 - consecutive_moves
5. 이동평균 이격도 - ma_divergence
6. 추세 돌파 후 이탈 - false_breakout
7. 강한 종가 상승 - strong_close
8. 변동성 축소 후 확장 - volatility_breakout
9. 단기 반전 - short_term_reversal
10. 추세 필터 + 시그널 - trend_filter_signal

실행:
    uv run python examples/expert_strategies.py --story beginner
    uv run python examples/expert_strategies.py --story compare
    uv run python examples/expert_strategies.py --story research
"""

import sys
from datetime import date, timedelta
from pathlib import Path

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from kis_backtest.strategies.generator import StrategyGenerator, generate_strategy
from kis_backtest.strategies import get_strategy, get_all_strategies

# 날짜 설정: 오늘 기준 1년 데이터
TODAY = date.today().strftime("%Y-%m-%d")
ONE_YEAR_AGO = (date.today() - timedelta(days=365)).strftime("%Y-%m-%d")


# ============================================================================
# 📌 10가지 Expert Sample 전략 정의
# ============================================================================

EXPERT_STRATEGIES = [
    {
        "id": "sma_crossover",
        "name": "단순 이동평균 골든크로스",
        "description": "5일선이 20일선을 상향 돌파하면 매수, 하향 돌파하면 매도",
        "category": "trend",
        "difficulty": "beginner",
        "params": {"fast_period": 5, "slow_period": 20},
    },
    {
        "id": "momentum",
        "name": "모멘텀",
        "description": "최근 60일 수익률 기준 상위 종목 매수, 하위 종목 매도",
        "category": "momentum",
        "difficulty": "intermediate",
        "params": {"lookback": 60, "threshold": 0.0},
    },
    {
        "id": "week52_high",
        "name": "52주 신고가 돌파",
        "description": "당일 종가가 52주 최고가 갱신 → 다음날 매수",
        "category": "trend",
        "difficulty": "intermediate",
        "params": {"stop_loss_pct": 5.0},
    },
    {
        "id": "consecutive_moves",
        "name": "연속 상승·하락",
        "description": "5일 연속 종가 상승 → 매수, 5일 연속 하락 → 매도",
        "category": "momentum",
        "difficulty": "beginner",
        "params": {"up_days": 5, "down_days": 5},
    },
    {
        "id": "ma_divergence",
        "name": "이동평균 이격도",
        "description": "종가/20일선 > 1.1 차익실현, < 0.9 분할매수",
        "category": "mean_reversion",
        "difficulty": "intermediate",
        "params": {"period": 20, "buy_ratio": 0.9, "sell_ratio": 1.1},
    },
    {
        "id": "false_breakout",
        "name": "추세 돌파 후 이탈",
        "description": "전고점 돌파 후 3일 내 종가가 다시 아래로 → 손절",
        "category": "trend",
        "difficulty": "advanced",
        "params": {"lookback": 20, "exit_days": 3},
    },
    {
        "id": "strong_close",
        "name": "강한 종가 상승",
        "description": "당일 종가가 당일 범위 상위 80% 이내 → 강세 포착",
        "category": "momentum",
        "difficulty": "intermediate",
        "params": {"min_close_ratio": 0.8, "stop_loss_pct": 5.0},
    },
    {
        "id": "volatility_breakout",
        "name": "변동성 축소 후 확장",
        "description": "최근 10일 표준편차 최저 → 3% 이상 상승 시 매수",
        "category": "volatility",
        "difficulty": "advanced",
        "params": {"atr_period": 10, "breakout_pct": 3.0},
    },
    {
        "id": "short_term_reversal",
        "name": "단기 반전 (Mean Reversion)",
        "description": "종가가 5일 평균보다 3% 이상 낮으면 매수, 높으면 매도",
        "category": "mean_reversion",
        "difficulty": "intermediate",
        "params": {"period": 5, "threshold_pct": 3.0},
    },
    {
        "id": "trend_filter_signal",
        "name": "추세 필터 + 시그널",
        "description": "60일선 위에서 전일 대비 상승 → 매수, 60일선 아래에서 하락 → 매도",
        "category": "composite",
        "difficulty": "intermediate",
        "params": {"trend_period": 60},
    },
]


# ============================================================================
# 📖 사용자 스토리 1: 초보자 - "처음 백테스트를 해보고 싶어요"
# ============================================================================

def story_beginner():
    """
    🎯 대상: 처음 주식 백테스트를 해보려는 사람
    
    가장 이해하기 쉬운 'SMA 골든크로스' 전략으로 시작합니다.
    단계별로 설명하며 코드를 생성하고, 결과물을 파일로 저장합니다.
    """
    print("=" * 70)
    print("📖 사용자 스토리: 초보자")
    print("   '처음으로 주식 백테스트를 해보고 싶어요'")
    print("=" * 70)
    
    print("\n💡 가장 간단한 전략부터 시작해볼까요?")
    print("   → '단순 이동평균 골든크로스' 전략을 추천합니다!")
    print()
    
    # Step 1: 전략 설명
    print("=" * 70)
    print("📌 Step 1: 전략 이해하기")
    print("=" * 70)
    print("""
    [단순 이동평균 골든크로스란?]
    
    • 5일 이동평균선 = 최근 5일간 종가의 평균
    • 20일 이동평균선 = 최근 20일간 종가의 평균
    
    • 골든크로스: 단기선(5일)이 장기선(20일)을 위로 돌파
      → 상승 추세 시작 신호 → 매수!
    
    • 데드크로스: 단기선(5일)이 장기선(20일)을 아래로 돌파
      → 하락 추세 시작 신호 → 매도!
    
    ┌─────────────────────────────────────────────────┐
    │  가격                                           │
    │   │                    골든크로스               │
    │   │      ╱╲    ╱╲╱╲         ╱╲    ↗ 매수      │
    │   │    ╱    ╲╱        ╲   ╱                    │
    │   │  ╱                  ╲╱        ← 5일선     │
    │   │ ─────────────────────────────  ← 20일선   │
    │   └─────────────────────────────── 시간       │
    └─────────────────────────────────────────────────┘
    """)
    
    # Step 2: 파라미터 설정
    print("=" * 70)
    print("📌 Step 2: 파라미터 설정")
    print("=" * 70)
    print("""
    오늘 사용할 설정:
    • 종목: 삼성전자 (005930)
    • 기간: 최근 1년
    • 자본금: 1억원 (100,000,000원)
    • 단기 이동평균: 5일
    • 장기 이동평균: 20일
    """)
    
    # Step 3: 코드 생성
    print("=" * 70)
    print("📌 Step 3: 전략 코드 자동 생성")
    print("=" * 70)
    
    code = generate_strategy(
        strategy_id="sma_crossover",
        symbols=["005930"],  # 삼성전자
        start_date=ONE_YEAR_AGO,
        end_date=TODAY,
        initial_capital=100_000_000,
        market_type="krx",
        params={"fast_period": 5, "slow_period": 20},
    )
    
    print(f"\n✅ 코드가 자동으로 생성되었습니다! ({len(code)} bytes)")
    
    # 핵심 부분만 보여주기
    print("\n[생성된 코드의 핵심 부분]")
    print("-" * 50)
    
    lines = code.split("\n")
    for i, line in enumerate(lines):
        if "골든크로스" in line or "데드크로스" in line:
            print(f"  {line}")
        if "def Initialize" in line or "def OnData" in line:
            print(f"\n  📍 {line}")
        if "SetHoldings" in line or "Liquidate" in line:
            print(f"  → {line}")
    
    # Step 4: 파일 저장
    print("\n" + "=" * 70)
    print("📌 Step 4: 파일 저장")
    print("=" * 70)
    
    output_dir = Path("./examples/output/beginner_example")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "main.py"
    output_file.write_text(code)
    
    print(f"\n✅ 전략 코드가 저장되었습니다!")
    print(f"   경로: {output_file}")
    
    # 다음 단계 안내
    print("\n" + "=" * 70)
    print("🎉 축하합니다! 첫 번째 전략을 만들었습니다!")
    print("=" * 70)
    print("""
    다음 단계:
    
    1. Docker Desktop이 실행 중인지 확인하세요
    
    2. 다음 명령어로 백테스트를 실행하세요:
       
       from kis_backtest import LeanClient
       client = LeanClient()
       result = client.backtest("./examples/output/beginner_example")
       
    3. 결과 리포트를 확인하세요:
       client.report(result, "report.html")
       
    더 많은 전략을 보려면:
       uv run python examples/expert_strategies.py --story compare
    """)
    
    return code


# ============================================================================
# 📖 사용자 스토리 2: 중급자 - "여러 전략을 비교해보고 싶어요"
# ============================================================================

def story_compare():
    """
    🎯 대상: 여러 전략을 비교해보고 싶은 중급 트레이더
    
    10가지 Expert Sample 전략을 한눈에 비교하고,
    각각의 특징과 적합한 시장 상황을 설명합니다.
    """
    print("=" * 70)
    print("📖 사용자 스토리: 중급자")
    print("   '여러 전략을 비교해서 나에게 맞는 걸 찾고 싶어요'")
    print("=" * 70)
    
    print("\n💡 10가지 Expert Sample 전략을 비교해드릴게요!")
    print()
    
    # 전략 분류표
    print("=" * 70)
    print("📊 전략 분류표")
    print("=" * 70)
    print("""
    ┌─────────────────────────────────────────────────────────────────────┐
    │                    시장 상황별 전략 추천                              │
    ├─────────────────┬───────────────────────────────────────────────────┤
    │   상승장         │  ① SMA 골든크로스, ③ 52주 신고가, ⑩ 추세필터     │
    ├─────────────────┼───────────────────────────────────────────────────┤
    │   하락장         │  ⑤ 이격도, ⑨ 단기반전 (평균회귀)                  │
    ├─────────────────┼───────────────────────────────────────────────────┤
    │   횡보장         │  ⑧ 변동성 확장, ⑥ 가짜돌파 필터                   │
    ├─────────────────┼───────────────────────────────────────────────────┤
    │   변동성 큰 장    │  ⑦ 강한종가 상승, ④ 연속상승                      │
    ├─────────────────┼───────────────────────────────────────────────────┤
    │   다중종목       │  ② 모멘텀 랭킹                                    │
    └─────────────────┴───────────────────────────────────────────────────┘
    """)
    
    # 난이도별 분류
    print("=" * 70)
    print("📈 난이도별 전략 분류")
    print("=" * 70)
    
    by_difficulty = {"beginner": [], "intermediate": [], "advanced": []}
    for s in EXPERT_STRATEGIES:
        by_difficulty[s["difficulty"]].append(s)
    
    difficulty_labels = {
        "beginner": "🟢 초급 (처음 시작하기 좋음)",
        "intermediate": "🟡 중급 (어느정도 경험 필요)",
        "advanced": "🔴 고급 (세밀한 튜닝 필요)"
    }
    
    for level, label in difficulty_labels.items():
        print(f"\n{label}")
        print("-" * 50)
        for s in by_difficulty[level]:
            idx = EXPERT_STRATEGIES.index(s) + 1
            print(f"  {idx}. {s['name']}")
            print(f"     → {s['description']}")
    
    # 각 전략별 코드 생성
    print("\n" + "=" * 70)
    print("🔧 모든 전략 코드 일괄 생성")
    print("=" * 70)
    
    output_dir = Path("./examples/output/strategy_comparison")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for i, strategy in enumerate(EXPERT_STRATEGIES, 1):
        try:
            code = generate_strategy(
                strategy_id=strategy["id"],
                symbols=["005930"],
                start_date=ONE_YEAR_AGO,
                end_date=TODAY,
                initial_capital=100_000_000,
                market_type="krx",
                params=strategy.get("params", {}),
            )
            
            # 파일 저장
            strategy_dir = output_dir / strategy["id"]
            strategy_dir.mkdir(exist_ok=True)
            (strategy_dir / "main.py").write_text(code)
            
            results.append({
                "name": strategy["name"],
                "id": strategy["id"],
                "bytes": len(code),
                "status": "✅"
            })
            
            print(f"  {i:2}. {strategy['name']:20} → {len(code):,} bytes ✅")
            
        except Exception as e:
            results.append({
                "name": strategy["name"],
                "id": strategy["id"],
                "bytes": 0,
                "status": f"❌ {e}"
            })
            print(f"  {i:2}. {strategy['name']:20} → ❌ {e}")
    
    success_count = sum(1 for r in results if r["status"] == "✅")
    
    print(f"\n📁 저장 위치: {output_dir}")
    print(f"📊 결과: {success_count}/{len(EXPERT_STRATEGIES)} 전략 생성 완료")
    
    # 비교 사용법 안내
    print("\n" + "=" * 70)
    print("🎯 다음 단계: 전략 비교 백테스트")
    print("=" * 70)
    print("""
    각 전략을 백테스트하고 비교하려면:
    
    from kis_backtest import LeanClient
    
    client = LeanClient()
    strategies = ["sma_crossover", "momentum", "week52_high", ...]
    
    results = {}
    for strategy in strategies:
        result = client.backtest(f"./examples/output/strategy_comparison/{strategy}")
        results[strategy] = result
    
    # 수익률 비교
    for name, result in results.items():
        print(f"{name}: {result.total_return:.2%}")
    """)
    
    return results


# ============================================================================
# 📖 사용자 스토리 3: 연구자 - "전략을 커스터마이징하고 싶어요"
# ============================================================================

def story_research():
    """
    🎯 대상: 전략 파라미터를 조절하며 연구하고 싶은 사람
    
    특정 전략의 파라미터를 변경하며 여러 버전을 생성하고,
    최적의 파라미터를 찾는 방법을 보여줍니다.
    """
    print("=" * 70)
    print("📖 사용자 스토리: 연구자")
    print("   '전략 파라미터를 조절해서 최적화하고 싶어요'")
    print("=" * 70)
    
    print("\n💡 SMA 크로스오버 전략의 파라미터를 변경해가며 비교해볼게요!")
    print()
    
    # 파라미터 조합 정의
    param_sets = [
        {"fast_period": 5, "slow_period": 20, "label": "빠른반응 (5/20)"},
        {"fast_period": 10, "slow_period": 30, "label": "표준 (10/30)"},
        {"fast_period": 20, "slow_period": 60, "label": "느린반응 (20/60)"},
        {"fast_period": 5, "slow_period": 60, "label": "극단적 (5/60)"},
    ]
    
    print("=" * 70)
    print("📊 테스트할 파라미터 조합")
    print("=" * 70)
    print("""
    ┌────────────────┬───────────────┬───────────────┬─────────────────────┐
    │  조합          │ 단기선 (일)   │ 장기선 (일)   │ 특징                 │
    ├────────────────┼───────────────┼───────────────┼─────────────────────┤
    │  빠른반응      │      5        │     20        │ 민감, 잦은 거래      │
    │  표준          │     10        │     30        │ 균형잡힌 설정        │
    │  느린반응      │     20        │     60        │ 안정적, 적은 거래    │
    │  극단적        │      5        │     60        │ 장기 추세 + 빠른진입 │
    └────────────────┴───────────────┴───────────────┴─────────────────────┘
    """)
    
    # 각 조합별 코드 생성
    print("=" * 70)
    print("🔧 파라미터별 코드 생성")
    print("=" * 70)
    
    output_dir = Path("./examples/output/parameter_research")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for params in param_sets:
        label = params.pop("label")
        
        code = generate_strategy(
            strategy_id="sma_crossover",
            symbols=["005930"],
            start_date=ONE_YEAR_AGO,
            end_date=TODAY,
            initial_capital=100_000_000,
            market_type="krx",
            params=params,
        )
        
        # 파일명에 파라미터 포함
        filename = f"sma_{params['fast_period']}_{params['slow_period']}"
        strategy_dir = output_dir / filename
        strategy_dir.mkdir(exist_ok=True)
        (strategy_dir / "main.py").write_text(code)
        
        print(f"\n  📁 {label}")
        print(f"     파라미터: short={params['fast_period']}, long={params['slow_period']}")
        print(f"     저장: {strategy_dir}/main.py")
        
        params["label"] = label  # 복원
    
    # 다중 종목 테스트 예시
    print("\n" + "=" * 70)
    print("📊 다중 종목 테스트")
    print("=" * 70)
    print("""
    동일한 전략을 여러 종목에 적용해볼 수도 있습니다:
    """)
    
    symbols_sets = [
        {"symbols": ["005930"], "name": "삼성전자 단일"},
        {"symbols": ["005930", "000660"], "name": "대형 반도체 2종"},
        {"symbols": ["005930", "000660", "035420", "035720", "005380"], "name": "대형주 5종"},
    ]
    
    for ss in symbols_sets:
        code = generate_strategy(
            strategy_id="sma_crossover",
            symbols=ss["symbols"],
            start_date=ONE_YEAR_AGO,
            end_date=TODAY,
            params={"fast_period": 10, "slow_period": 30},
        )
        
        print(f"  • {ss['name']}: {len(ss['symbols'])}종목 → {len(code):,} bytes")
    
    # 연구 방법론 안내
    print("\n" + "=" * 70)
    print("🎓 연구 방법론")
    print("=" * 70)
    print("""
    [Grid Search 최적화]
    
    from kis_backtest import LeanClient
    
    client = LeanClient()
    
    # 파라미터 그리드 정의
    fast_periods = [5, 10, 15, 20]
    slow_periods = [20, 30, 40, 50, 60]
    
    best_sharpe = 0
    best_params = None
    
    for short in fast_periods:
        for long in slow_periods:
            if short >= long:
                continue  # 유효하지 않은 조합 스킵
            
            result = client.backtest_strategy(
                strategy_id="sma_crossover",
                symbols=["005930"],
                start_date=ONE_YEAR_AGO,
                end_date=TODAY,
                params={"fast_period": short, "slow_period": long}
            )
            
            if result.sharpe_ratio > best_sharpe:
                best_sharpe = result.sharpe_ratio
                best_params = {"short": short, "long": long}
    
    print(f"최적 파라미터: {best_params}")
    print(f"샤프 비율: {best_sharpe:.2f}")
    """)
    
    print("\n" + "=" * 70)
    print("✅ 연구 준비 완료!")
    print(f"📁 저장 위치: {output_dir}")
    print("=" * 70)


# ============================================================================
# 📖 사용자 스토리 4: 전략 카탈로그
# ============================================================================

def show_catalog():
    """모든 전략의 카탈로그 출력"""
    from kis_backtest.strategies.registry import StrategyRegistry

    print("=" * 70)
    print("📚 Expert Sample 10종 전략 카탈로그")
    print("=" * 70)

    for i, strategy in enumerate(EXPERT_STRATEGIES, 1):
        strategy_cls = get_strategy(strategy["id"])

        print(f"\n{'─' * 70}")
        print(f"  {i}. {strategy['name']}")
        print(f"{'─' * 70}")
        print(f"  전략 ID: {strategy['id']}")
        print(f"  카테고리: {strategy['category']}")
        print(f"  난이도: {strategy['difficulty']}")
        print(f"  설명: {strategy['description']}")

        if strategy_cls:
            # StrategyDefinition 빌드해서 딕셔너리로 변환
            try:
                definition = strategy_cls().build()
                s = definition.to_dict()

                # 지표 정보
                indicators = s.get("indicators", [])
                if indicators:
                    ind_names = [ind.get("alias") or ind.get("id") for ind in indicators]
                    print(f"  사용 지표: {', '.join(ind_names)}")

                # 파라미터 정보
                params = StrategyRegistry.get_param_definitions(strategy["id"])
                if params:
                    print("  파라미터:")
                    for key, config in params.items():
                        default = config.get("default", "N/A")
                        label = config.get("description", key)
                        print(f"    • {key}: 기본값 {default}")
            except Exception as e:
                print(f"  ⚠️ 전략 정보 로드 실패: {e}")
    
    print(f"\n{'=' * 70}")
    print(f"총 {len(EXPERT_STRATEGIES)}개 전략")
    print("=" * 70)


# ============================================================================
# 메인 실행
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Expert Sample 10종 전략 예제",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용자 스토리:
  beginner  - 처음 백테스트를 해보는 초보자
  compare   - 여러 전략을 비교하고 싶은 중급자
  research  - 파라미터 최적화를 연구하는 연구자
  catalog   - 전체 전략 카탈로그 보기

예시:
  uv run python examples/expert_strategies.py --story beginner
  uv run python examples/expert_strategies.py --story compare
  uv run python examples/expert_strategies.py --story research
  uv run python examples/expert_strategies.py --story catalog
        """
    )
    parser.add_argument(
        "--story",
        choices=["beginner", "compare", "research", "catalog", "all"],
        default="catalog",
        help="실행할 사용자 스토리"
    )
    args = parser.parse_args()
    
    if args.story == "beginner":
        story_beginner()
    elif args.story == "compare":
        story_compare()
    elif args.story == "research":
        story_research()
    elif args.story == "catalog":
        show_catalog()
    elif args.story == "all":
        show_catalog()
        print("\n\n")
        story_beginner()
        print("\n\n")
        story_compare()
        print("\n\n")
        story_research()
    
    print("\n✅ 완료!")
