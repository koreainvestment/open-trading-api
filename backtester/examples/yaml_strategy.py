#!/usr/bin/env python3
"""
YAML 기반 전략 예제

이 예제는 .kis.yaml 파일을 사용하여 전략을 정의하고 Lean 코드로 변환하는 방법을 보여줍니다.
코드 없이 YAML 파일만으로 전략을 관리할 수 있습니다.

실행:
    uv run python examples/yaml_strategy.py --example basic
    uv run python examples/yaml_strategy.py --example param_override
    uv run python examples/yaml_strategy.py --example custom_yaml
    uv run python examples/yaml_strategy.py --example export
    uv run python examples/yaml_strategy.py --example all
"""

import sys
from datetime import date, timedelta
from pathlib import Path

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

# 날짜 설정: 오늘 기준 1년 데이터
TODAY = date.today().strftime("%Y-%m-%d")
ONE_YEAR_AGO = (date.today() - timedelta(days=365)).strftime("%Y-%m-%d")


# ============================================================================
# 예제 1: 기본 YAML 로드
# ============================================================================

def example_basic_yaml_load():
    """
    .kis.yaml 파일에서 전략을 로드하는 기본 예제
    """
    print("=" * 70)
    print("📄 기본 YAML 전략 로드")
    print("=" * 70)
    
    from kis_backtest.file import StrategyFileLoader
    
    # 템플릿 디렉토리 경로
    template_dir = Path(__file__).parent.parent / "kis_backtest" / "file" / "templates"
    
    print(f"\n📁 템플릿 디렉토리: {template_dir}")
    
    # 사용 가능한 템플릿 목록
    print("\n📋 사용 가능한 템플릿:")
    print("-" * 50)
    
    templates = list(template_dir.glob("*.kis.yaml")) if template_dir.exists() else []
    
    if not templates:
        print("  템플릿이 없습니다. 예제 YAML을 생성합니다...")
        _create_example_templates(template_dir)
        templates = list(template_dir.glob("*.kis.yaml"))
    
    for template in templates:
        print(f"  - {template.name}")
    
    # RSI 과매도 전략 로드
    print("\n🔄 RSI 과매도 전략 로드 중...")
    
    rsi_template = template_dir / "rsi_oversold.kis.yaml"
    if rsi_template.exists():
        strategy_file = StrategyFileLoader.load(rsi_template)
        
        print(f"\n📊 로드된 전략 정보:")
        print("-" * 50)
        print(f"  이름: {strategy_file.metadata.name}")
        print(f"  설명: {strategy_file.metadata.description}")
        print(f"  ID: {strategy_file.strategy.id}")
        print(f"  카테고리: {strategy_file.strategy.category}")
        print(f"  지표 수: {len(strategy_file.strategy.indicators)}")
        print(f"  태그: {strategy_file.metadata.tags}")
        
        # 파라미터 정보
        if strategy_file.strategy.params:
            print("\n📋 파라미터 정의:")
            for name, config in strategy_file.strategy.params.items():
                default = config.get("default", "N/A")
                min_val = config.get("min", "N/A")
                max_val = config.get("max", "N/A")
                desc = config.get("description", "")
                print(f"    ${name}: 기본값={default}, 범위=[{min_val}, {max_val}]")
                print(f"      └ {desc}")
        
        return strategy_file
    else:
        print("  ⚠️ rsi_oversold.kis.yaml 템플릿이 없습니다.")
        return None


# ============================================================================
# 예제 2: 파라미터 오버라이드
# ============================================================================

def example_param_override():
    """
    $param_name 참조를 오버라이드하여 전략을 커스터마이징하는 예제
    """
    print("=" * 70)
    print("🔧 파라미터 오버라이드 예제")
    print("=" * 70)
    
    from kis_backtest.file import StrategyFileLoader
    
    # RSI 전략 YAML 문자열 (인라인 정의)
    yaml_content = """
version: "1.0"

metadata:
  name: "RSI 과매도 반전"
  description: "RSI가 과매도 영역 진입 후 반등 시 매수"
  author: "example"
  tags: [oscillator, rsi]

strategy:
  id: rsi_oversold
  category: oscillator

  params:
    period:
      default: 14
      min: 2
      max: 100
      type: int
      description: "RSI 기간"
    oversold:
      default: 30
      min: 0
      max: 50
      type: float
      description: "과매도 기준"
    overbought:
      default: 70
      min: 50
      max: 100
      type: float
      description: "과매수 기준"

  indicators:
    - id: rsi
      alias: rsi
      params:
        period: $period

  entry:
    logic: AND
    conditions:
      - indicator: rsi
        operator: cross_above
        value: $oversold

  exit:
    logic: OR
    conditions:
      - indicator: rsi
        operator: cross_below
        value: $overbought

risk:
  stop_loss:
    enabled: true
    percent: 5.0
"""
    
    print("\n[1] 기본값으로 로드")
    print("-" * 50)
    
    # 기본값으로 스키마 로드
    schema_default = StrategyFileLoader.load_schema_from_string(yaml_content)
    
    print(f"  RSI 기간: 14 (기본값)")
    print(f"  과매도: 30 (기본값)")
    print(f"  과매수: 70 (기본값)")
    
    print("\n[2] 파라미터 오버라이드")
    print("-" * 50)
    
    # 파라미터 오버라이드하여 로드
    schema_custom = StrategyFileLoader.load_schema_with_params(
        yaml_content,
        param_overrides={
            "period": 21,
            "oversold": 25,
            "overbought": 75,
        }
    )
    
    print(f"  RSI 기간: 21 (오버라이드)")
    print(f"  과매도: 25 (오버라이드)")
    print(f"  과매수: 75 (오버라이드)")
    
    print("\n[3] 스키마 비교")
    print("-" * 50)
    print(f"  기본 스키마 ID: {schema_default.id}")
    print(f"  커스텀 스키마 ID: {schema_custom.id}")
    
    # 지표 파라미터 비교
    for ind in schema_default.indicators:
        print(f"  기본 {ind.alias} params: {ind.params}")
    
    for ind in schema_custom.indicators:
        print(f"  커스텀 {ind.alias} params: {ind.params}")
    
    return schema_default, schema_custom


# ============================================================================
# 예제 3: 커스텀 YAML 작성
# ============================================================================

def example_custom_yaml():
    """
    직접 YAML을 작성하여 커스텀 전략을 만드는 예제
    """
    print("=" * 70)
    print("✏️ 커스텀 YAML 전략 작성")
    print("=" * 70)
    
    from kis_backtest.file import StrategyFileLoader
    
    # 커스텀 전략: 골든크로스 + RSI 필터
    custom_yaml = """
version: "1.0"

metadata:
  name: "골든크로스 + RSI 필터"
  description: "SMA 골든크로스가 발생하고 RSI가 과열되지 않은 경우 매수"
  author: "user"
  tags:
    - trend
    - sma
    - rsi
    - composite

strategy:
  id: golden_cross_rsi_filter
  category: composite

  params:
    fast_period:
      default: 5
      min: 2
      max: 50
      type: int
      description: "단기 SMA 기간"
    slow_period:
      default: 20
      min: 10
      max: 200
      type: int
      description: "장기 SMA 기간"
    rsi_period:
      default: 14
      min: 2
      max: 50
      type: int
      description: "RSI 기간"
    rsi_threshold:
      default: 70
      min: 50
      max: 90
      type: float
      description: "RSI 과열 기준"

  indicators:
    - id: sma
      alias: fast
      params:
        period: $fast_period
    - id: sma
      alias: slow
      params:
        period: $slow_period
    - id: rsi
      alias: rsi
      params:
        period: $rsi_period

  entry:
    logic: AND
    conditions:
      - indicator: fast
        operator: cross_above
        compare_to: slow
      - indicator: rsi
        operator: less_than
        value: $rsi_threshold

  exit:
    logic: OR
    conditions:
      - indicator: fast
        operator: cross_below
        compare_to: slow
      - indicator: rsi
        operator: greater_than
        value: 80

risk:
  stop_loss:
    enabled: true
    percent: 5.0
  take_profit:
    enabled: true
    percent: 15.0
  trailing_stop:
    enabled: true
    percent: 3.0
"""
    
    print("\n📋 커스텀 전략 YAML:")
    print("-" * 50)
    print(custom_yaml[:500] + "...\n")
    
    # 스키마로 로드
    print("🔄 스키마로 변환 중...")
    schema = StrategyFileLoader.load_schema_from_string(custom_yaml)
    
    print(f"\n✅ 전략 로드 성공!")
    print(f"  ID: {schema.id}")
    print(f"  이름: {schema.name}")
    print(f"  지표 수: {len(schema.indicators)}")
    print(f"  카테고리: {schema.category}")
    
    # 조건 표시
    print("\n📋 진입 조건:")
    _print_condition(schema.entry, "  ")
    
    print("\n📋 청산 조건:")
    _print_condition(schema.exit, "  ")
    
    # 리스크 관리
    if schema.risk:
        print("\n🛡️ 리스크 관리:")
        if schema.risk.stop_loss_pct:
            print(f"  손절: {schema.risk.stop_loss_pct}%")
        if schema.risk.take_profit_pct:
            print(f"  익절: {schema.risk.take_profit_pct}%")
        if schema.risk.trailing_stop_pct:
            print(f"  트레일링 스탑: {schema.risk.trailing_stop_pct}%")
    
    return schema


# ============================================================================
# 예제 4: Python DSL ↔ YAML 변환
# ============================================================================

def example_export_import():
    """
    Python DSL 전략을 YAML로 내보내고, 다시 불러오는 예제
    """
    print("=" * 70)
    print("🔄 Python DSL ↔ YAML 변환")
    print("=" * 70)
    
    from kis_backtest.dsl import RuleBuilder, SMA, RSI
    from kis_backtest.file import StrategyFileSaver, StrategyFileLoader
    
    print("\n[1] Python DSL로 전략 정의")
    print("-" * 50)
    
    # RuleBuilder로 전략 생성
    strategy = (
        RuleBuilder("나의 골든크로스")
        .description("5일선이 20일선 상향 돌파 + RSI 필터")
        .category("composite")
        .buy_when(SMA(5).crosses_above(SMA(20)) & (RSI(14) < 70))
        .sell_when(SMA(5).crosses_below(SMA(20)) | (RSI(14) > 80))
        .stop_loss(5.0)
        .take_profit(15.0)
        .build()
    )
    
    print(f"  전략 이름: {strategy.name}")
    print(f"  전략 카테고리: {strategy.category}")
    
    print("\n[2] YAML로 내보내기")
    print("-" * 50)

    # StrategyRule → StrategyDefinition 변환
    strategy_def = strategy.to_strategy_definition()

    # YAML 문자열로 변환
    yaml_str = StrategyFileSaver.to_yaml_string(strategy_def)

    print("  생성된 YAML (처음 30줄):")
    for line in yaml_str.split("\n")[:30]:
        print(f"    {line}")

    # 파일로 저장
    output_path = Path("./examples/output/my_golden_cross.kis.yaml")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    StrategyFileSaver.save_definition(
        strategy_def,
        output_path,
        author="example_user",
        tags=["trend", "sma", "rsi", "custom"],
    )
    print(f"\n  저장: {output_path}")
    
    print("\n[3] YAML에서 다시 로드")
    print("-" * 50)
    
    # 다시 로드
    loaded = StrategyFileLoader.load(output_path)
    
    print(f"  로드된 전략: {loaded.metadata.name}")
    print(f"  작성자: {loaded.metadata.author}")
    print(f"  태그: {loaded.metadata.tags}")
    
    return strategy, loaded


# ============================================================================
# 예제 5: 볼린저밴드 YAML
# ============================================================================

def example_bollinger_yaml():
    """
    멀티 아웃풋 지표(볼린저밴드)를 사용하는 YAML 예제
    """
    print("=" * 70)
    print("📊 볼린저밴드 YAML 전략")
    print("=" * 70)
    
    from kis_backtest.file import StrategyFileLoader
    
    yaml_content = """
version: "1.0"

metadata:
  name: "볼린저밴드 반전"
  description: "가격이 하단 밴드 터치 시 매수, 상단 밴드 터치 시 매도"
  author: "example"
  tags: [volatility, bollinger, mean_reversion]

strategy:
  id: bollinger_band
  category: volatility

  params:
    period:
      default: 20
      min: 10
      max: 50
      type: int
      description: "볼린저밴드 기간"
    std_dev:
      default: 2.0
      min: 1.5
      max: 3.0
      type: float
      description: "표준편차 배수"

  indicators:
    - id: bollinger
      alias: bb
      params:
        period: $period
        std: $std_dev

  entry:
    logic: AND
    conditions:
      - indicator: close
        operator: less_than
        compare_to: bb
        compare_output: lower

  exit:
    logic: OR
    conditions:
      - indicator: close
        operator: greater_than
        compare_to: bb
        compare_output: upper

risk:
  stop_loss:
    enabled: true
    percent: 5.0
  take_profit:
    enabled: true
    percent: 10.0
  trailing_stop:
    enabled: true
    percent: 3.0
"""
    
    print("\n📋 볼린저밴드 전략 특징:")
    print("-" * 50)
    print("  - 멀티 아웃풋 지표 사용 (upper, middle, lower)")
    print("  - compare_output으로 특정 출력값 지정")
    print("  - 평균 회귀 전략")
    
    schema = StrategyFileLoader.load_schema_from_string(yaml_content)
    
    print(f"\n✅ 로드 성공!")
    print(f"  전략: {schema.name}")
    print(f"  지표: {[ind.alias for ind in schema.indicators]}")
    
    # 조건 상세
    print("\n📋 진입 조건:")
    _print_condition(schema.entry, "  ")
    
    print("\n📋 청산 조건:")
    _print_condition(schema.exit, "  ")
    
    return schema


# ============================================================================
# 헬퍼 함수
# ============================================================================

def _print_condition(cond, indent=""):
    """조건 스키마를 읽기 좋게 출력"""
    from kis_backtest.core.schema import CompositeConditionSchema, ConditionSchema
    
    if isinstance(cond, CompositeConditionSchema):
        print(f"{indent}논리: {cond.logic}")
        for i, sub in enumerate(cond.conditions):
            print(f"{indent}조건 {i+1}:")
            _print_condition(sub, indent + "  ")
    elif isinstance(cond, ConditionSchema):
        if cond.candlestick:
            print(f"{indent}캔들스틱: {cond.candlestick} ({cond.signal})")
        else:
            right = cond.value if cond.value is not None else cond.compare_to
            print(f"{indent}{cond.indicator} {cond.operator.value} {right}")
    else:
        print(f"{indent}조건: {cond}")


def _create_example_templates(template_dir: Path):
    """예제 템플릿 생성"""
    template_dir.mkdir(parents=True, exist_ok=True)
    
    # RSI 과매도 템플릿
    rsi_yaml = """version: "1.0"

metadata:
  name: "RSI 과매도 반전"
  description: "RSI가 과매도 영역 진입 후 반등 시 매수"
  author: "kis2"
  tags: [oscillator, rsi, mean_reversion]

strategy:
  id: rsi_oversold
  category: oscillator

  params:
    period:
      default: 14
      min: 2
      max: 100
      type: int
      description: "RSI 기간"
    oversold:
      default: 30
      min: 0
      max: 50
      type: float
      description: "과매도 기준"
    overbought:
      default: 70
      min: 50
      max: 100
      type: float
      description: "과매수 기준"

  indicators:
    - id: rsi
      alias: rsi
      params:
        period: $period

  entry:
    logic: AND
    conditions:
      - indicator: rsi
        operator: cross_above
        value: $oversold

  exit:
    logic: OR
    conditions:
      - indicator: rsi
        operator: cross_below
        value: $overbought

risk:
  stop_loss:
    enabled: true
    percent: 5.0
  take_profit:
    enabled: true
    percent: 10.0
"""
    
    (template_dir / "rsi_oversold.kis.yaml").write_text(rsi_yaml)
    print(f"  ✅ 생성: {template_dir / 'rsi_oversold.kis.yaml'}")


# ============================================================================
# 메인 실행
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="YAML 기반 전략 예제",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  basic          - 기본 YAML 로드
  param_override - 파라미터 오버라이드
  custom_yaml    - 커스텀 YAML 작성
  export         - Python DSL ↔ YAML 변환
  bollinger      - 볼린저밴드 멀티 아웃풋

실행:
  uv run python examples/yaml_strategy.py --example basic
        """
    )
    
    parser.add_argument(
        "--example",
        choices=["basic", "param_override", "custom_yaml", "export", "bollinger", "all"],
        default="basic",
        help="실행할 예제 선택"
    )
    
    args = parser.parse_args()
    
    examples = {
        "basic": example_basic_yaml_load,
        "param_override": example_param_override,
        "custom_yaml": example_custom_yaml,
        "export": example_export_import,
        "bollinger": example_bollinger_yaml,
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
        try:
            examples[args.example]()
        except Exception as e:
            print(f"❌ 오류: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n✅ 완료!")
