# KIS Backtest 예제

이 폴더는 `kis_backtest` 라이브러리 사용 예제를 포함합니다.

## 사전 준비

### 1. 패키지 설치

```bash
cd backtester
uv sync
```

### 2. Docker 설치

백테스트 실행을 위해 Docker가 필요합니다:
- [Docker Desktop 설치](https://www.docker.com/products/docker-desktop)

---

## 예제 목록

| 파일 | 설명 | 명령어 | API 필요 |
|------|------|--------|----------|
| `yaml_strategy.py` | YAML 전략 파싱/변환 | `--example all` | X |
| `strategy_generation.py` | 프리셋 전략 코드 생성 | (인자 없음) | X |
| `expert_strategies.py` | Expert 10종 전략 | `--story catalog` | X |
| `basic_backtest.py` | 기본 백테스트 | `--example basic` | O (Docker) |
| `rule_builder.py` | RuleBuilder DSL 백테스트 | `--example basic` | O (Docker) |
| `portfolio_analysis.py` | 포트폴리오 분석 | `--example basic` | O |
| `optimization.py` | 파라미터 최적화 | `--example basic` | O (실전 권장) |
| `live_trading.py` | 실시간 매매 | `--example position` | O |

---

## 실행 결과 (2026-02-25 검증)

### basic_backtest.py — SMA 크로스오버 백테스트

```bash
uv run python examples/basic_backtest.py --example basic
```

```
[1/4] 한국투자증권 API 인증 중...
  ✓ 인증 성공 (모의투자)

[2/4] 백테스트 설정...
  - 전략: sma_crossover (단기MA 10일, 장기MA 30일)
  - 종목: 005930 (삼성전자)
  - 기간: 2025-02-25 ~ 2026-02-25
  - 초기자본: 1억원

[3/4] 백테스트 실행 중...

[4/4] 백테스트 결과
----------------------------------------
  총 수익률: 1.75%
  연간 수익률 (CAGR): 1.77%
  샤프 비율: 3.75
  소르티노 비율: 4.71
  최대 낙폭: 0.18%
  총 거래 수: 9
  승률: 75.0%
  수익/손실 비율: 5.93
  실행 시간: 5.0초
----------------------------------------
```

### rule_builder.py — RuleBuilder DSL 백테스트

```bash
uv run python examples/rule_builder.py --example basic
```

```
  ✓ KIS 인증 (모의투자)

전략 정의:
  전략명: 골든크로스
  매수 조건: 5일 이동평균 > 20일 이동평균
  매도 조건: 5일 이동평균 < 20일 이동평균

✅ 전략이 생성되었습니다!
   전략 객체: 골든크로스
   사용 지표: ['sma_5', 'sma_20']

백테스트 결과
======================================================================
  수익률: +1.74%
  샤프 비율: 3.79
  최대 낙폭: 0.16%
  총 거래: 13회
  승률: 33.0%
```

### portfolio_analysis.py — 포트폴리오 분산 효과

```bash
uv run python examples/portfolio_analysis.py --example basic
```

```
포트폴리오 구성:
  삼성전자         (005930):  30.0%
  SK하이닉스       (000660):  20.0%
  NAVER        (035420):  20.0%
  카카오          (035720):  15.0%
  현대차          (005380):  15.0%

포트폴리오 분석 결과
======================================================================

[수익/위험 지표]
  기대 수익률 (연율): +151.86%
  변동성 (연율):      31.70%
  샤프 비율:          4.68

[분산 효과]
  분산 비율: 1.47
  → 분산 투자로 위험이 47.1% 감소했습니다!

[개별 종목 변동성]
  삼성전자        : 40.05%
  SK하이닉스      : 54.90%
  NAVER       : 45.55%
  현대차         : 50.17%

[리스크 기여도]
  삼성전자        :  36.6%
  SK하이닉스      :  31.7%
  NAVER       :  17.7%
  현대차         :  14.0%
```

### yaml_strategy.py — YAML 전략 파싱 (API 불필요)

```bash
uv run python examples/yaml_strategy.py --example all
```

5개 예제 전체 통과:
- `basic` — 템플릿 로드 (10개 프리셋)
- `param_override` — $param 오버라이드 (RSI 14→21)
- `custom_yaml` — 골든크로스+RSI 복합 YAML 파싱
- `export` — Python DSL ↔ YAML 양방향 변환
- `bollinger` — 멀티 아웃풋 지표 (upper/lower)

### strategy_generation.py — 전략 코드 생성 (API 불필요)

```bash
uv run python examples/strategy_generation.py
```

8개 섹션 전체 통과:
- 10개 등록 전략 목록 출력
- SMA 크로스오버 Lean 코드 생성 (5,984 bytes)
- 리스크 관리 포함 (변동성 확장 전략)
- 다중 종목 10개 모멘텀 전략
- 추세 필터 전략 코드 생성
- 포지션 사이징 4종 비교
- 카테고리별 분류 (5개 카테고리)
- 파라미터 검증 (정상/잘못된/범위초과)

### expert_strategies.py — 10종 Expert 전략

```bash
uv run python examples/expert_strategies.py --story catalog
```

```
📚 Expert Sample 10종 전략 카탈로그

  1. 단순 이동평균 골든크로스  | sma_crossover      | trend
  2. 모멘텀               | momentum           | momentum
  3. 52주 신고가 돌파       | week52_high        | trend
  4. 연속 상승·하락         | consecutive_moves  | momentum
  5. 이동평균 이격도        | ma_divergence      | mean_reversion
  6. 추세 돌파 후 이탈      | false_breakout     | trend
  7. 강한 종가 상승         | strong_close       | momentum
  8. 변동성 축소 후 확장     | volatility_breakout| volatility
  9. 단기 반전             | short_term_reversal| mean_reversion
 10. 추세 필터 + 시그널     | trend_filter_signal| composite
```

`--story compare`: 8/10 전략 Lean 코드 생성 성공
(`ma_divergence`, `short_term_reversal`은 파생값 조건으로 StrategyGenerator 변환 미지원)

### live_trading.py — 포지션 조회

```bash
uv run python examples/live_trading.py --example position
```

```
  ✓ 인증 성공 (모의투자)

[포지션] 현재 보유 포지션:
  [000660]  20주  평균 852,100원 → 현재 1,012,000원  +18.77%
  [005380]  15주  평균 469,800원 → 현재 565,000원    +20.26%
  [005930]  10주  평균 153,300원 → 현재 201,500원    +31.44%
  [035420]  50주  평균 256,000원 → 현재 252,500원    -1.37%
  [051910]  16주  평균 335,281원 → 현재 365,500원    +9.01%
```

---

## YAML 전략

### .kis.yaml 파일 형식

코드 없이 YAML로 전략을 정의할 수 있습니다:

```yaml
version: "1.0"

metadata:
  name: "RSI 과매도 반전"
  description: "RSI가 과매도 영역 진입 후 반등 시 매수"
  author: "user"
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
        value: 70

risk:
  stop_loss:
    enabled: true
    percent: 5.0
```

### YAML 예제 실행

```bash
uv run python examples/yaml_strategy.py --example basic
uv run python examples/yaml_strategy.py --example param_override
uv run python examples/yaml_strategy.py --example custom_yaml
uv run python examples/yaml_strategy.py --example export
uv run python examples/yaml_strategy.py --example bollinger
uv run python examples/yaml_strategy.py --example all
```

### 주요 기능

| 기능 | 설명 |
|------|------|
| `$param_name` 참조 | 파라미터를 동적으로 바인딩 |
| `param_overrides` | 런타임에 파라미터 값 오버라이드 |
| 멀티 아웃풋 | 볼린저밴드 upper/lower, MACD signal 등 |
| 캔들스틱 패턴 | doji, engulfing 등 패턴 지원 |
| YAML ↔ DSL 변환 | 양방향 변환 지원 |

### 프로그래밍 예제

```python
from kis_backtest.file import StrategyFileLoader, StrategyFileSaver

# 1. YAML 파일에서 스키마 로드
schema = StrategyFileLoader.load_as_schema("my_strategy.kis.yaml")

# 2. 파라미터 오버라이드
schema = StrategyFileLoader.load_schema_with_params(
    "my_strategy.kis.yaml",
    param_overrides={"period": 21, "oversold": 25}
)

# 3. YAML 문자열에서 로드
schema = StrategyFileLoader.load_schema_from_string(yaml_content)

# 4. Lean 코드 생성
from kis_backtest.codegen import LeanCodeGenerator

generator = LeanCodeGenerator(schema)
code = generator.generate(
    symbols=["005930"],
    start_date="2025-01-01",
    end_date="2025-12-31",
)

# 5. Python DSL을 YAML로 내보내기
from kis_backtest.dsl import RuleBuilder, SMA

strategy = RuleBuilder("my_strategy").buy_when(SMA(5) > SMA(20)).build()
StrategyFileSaver.save_definition(strategy, "my_strategy.kis.yaml")
```

---

## 디렉토리 구조

```
examples/
├── README.md                    # 이 파일
├── basic_backtest.py            # 기본 백테스트
├── rule_builder.py              # RuleBuilder DSL
├── yaml_strategy.py             # YAML 전략
├── strategy_generation.py       # 프리셋 전략
├── portfolio_analysis.py        # 포트폴리오
├── optimization.py              # 최적화 (실전투자 계좌 권장)
├── expert_strategies.py         # Expert 전략
├── live_trading.py              # 실시간 매매
└── output/                      # 실행 결과
    └─── reports/                 # HTML 리포트 예시
```

---

## 문제 해결

### 인증 오류

```
AuthenticationError: 토큰 발급 실패
```

1. KIS API 인증 설정 확인
2. 한국투자증권 API 신청 상태 확인
3. IP 화이트리스트 설정 확인

### Docker 오류

```
DockerError: Docker daemon not running
```

1. Docker Desktop 실행
2. `docker info` 명령어로 상태 확인

### 초당 거래건수 초과

```
EGW00201: 초당 거래건수를 초과하였습니다.
```

모의투자 계좌는 REST API 초당 호출 제한이 낮습니다.
- 단일 백테스트/조회: 모의투자 사용 가능
- 최적화(다수 백테스트 연속): 실전투자 계좌 권장

### YAML 파싱 오류

```
ValueError: Invalid YAML format
```

1. YAML 문법 확인 (들여쓰기, 콜론 뒤 공백)
2. `$param_name` 참조가 `params:` 섹션에 정의되어 있는지 확인
