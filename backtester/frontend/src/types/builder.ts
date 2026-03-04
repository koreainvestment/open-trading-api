/**
 * Visual Strategy Builder Types
 */

// ============================================================
// Indicator Types
// ============================================================

export type IndicatorCategory =
  | "moving_average"
  | "oscillator"
  | "trend"
  | "volume"
  | "volatility"
  | "misc"
  | "candlestick";

export interface IndicatorParam {
  name: string;
  type: "number" | "string";
  default: number | string;
  min?: number;
  max?: number;
  step?: number;
  description?: string;
}

export interface IndicatorOutput {
  id: string;
  name: string;
  description?: string;
}

export interface IndicatorDefinition {
  id: string;
  name: string;
  nameKo: string;
  category: IndicatorCategory;
  description: string;
  params: IndicatorParam[];
  outputs: IndicatorOutput[];
  defaultOutput: string;
}

// ============================================================
// Builder State Types
// ============================================================

export interface BuilderIndicator {
  id: string;
  indicatorId: string;
  alias: string;
  params: Record<string, number | string>;
  output: string;
}

export type ConditionOperator =
  | "greater_than"
  | "less_than"
  | "greater_equal"
  | "less_equal"
  | "cross_above"
  | "cross_below"
  | "equals";

export type ConditionOperandType =
  | "indicator"
  | "value"
  | "price";

export interface ConditionOperand {
  type: ConditionOperandType;
  indicatorAlias?: string;
  indicatorOutput?: string;
  value?: number;
  priceField?: "close" | "open" | "high" | "low";
}

export interface BuilderCondition {
  id: string;
  left: ConditionOperand;
  operator: ConditionOperator;
  right: ConditionOperand;
  // 캔들스틱 조건용 (캔들스틱인 경우 left/operator/right 무시)
  isCandlestick?: boolean;
  candlestickAlias?: string;
  candlestickSignal?: "bullish" | "bearish" | "detected";
}

export interface BuilderConditionGroup {
  logic: "AND" | "OR";
  conditions: BuilderCondition[];
}

export interface RiskManagement {
  stopLoss: {
    enabled: boolean;
    percent: number;
  };
  takeProfit: {
    enabled: boolean;
    percent: number;
  };
  trailingStop: {
    enabled: boolean;
    percent: number;
  };
}

export interface BuilderMetadata {
  id: string;
  name: string;
  description: string;
  category: string;
  tags: string[];
  author: string;
}

export interface BuilderState {
  metadata: BuilderMetadata;
  indicators: BuilderIndicator[];
  entry: BuilderConditionGroup;
  exit: BuilderConditionGroup;
  risk: RiskManagement;
}

// ============================================================
// Storage Types
// ============================================================

export interface StoredStrategy {
  id: string;
  name: string;
  createdAt: string;
  updatedAt: string;
  state: BuilderState;
}

// ============================================================
// YAML Conversion Types
// ============================================================

export interface YamlIndicator {
  id: string;
  alias: string;
  params: Record<string, number>;
  output?: string;
}

export interface YamlCandlestick {
  id: string;
  alias: string;
}

export interface YamlCondition {
  indicator?: string;
  operator?: string;
  compare_to?: string | number;
  output?: string;
  compare_output?: string; // 오른쪽 지표의 출력 필드 (예: macd_1의 signal)
  // 캔들스틱 조건
  candlestick?: string;
  signal?: "bullish" | "bearish" | "detected";
}

export interface YamlConditionGroup {
  logic: "AND" | "OR";
  conditions: YamlCondition[];
}

export interface YamlRisk {
  stop_loss?: { enabled: boolean; percent: number };
  take_profit?: { enabled: boolean; percent: number };
  trailing_stop?: { enabled: boolean; percent: number };
}

export interface YamlStrategy {
  version: string;
  metadata: {
    name: string;
    description: string;
    author?: string;
    tags: string[];
  };
  strategy: {
    id: string;
    category: string;
    indicators: YamlIndicator[];
    candlesticks?: YamlCandlestick[];
    entry: YamlConditionGroup;
    exit: YamlConditionGroup;
  };
  risk: YamlRisk;
}

// ============================================================
// Builder Actions
// ============================================================

export type BuilderAction =
  | { type: "SET_METADATA"; payload: Partial<BuilderMetadata> }
  | { type: "ADD_INDICATOR"; payload: BuilderIndicator }
  | { type: "UPDATE_INDICATOR"; payload: { id: string; updates: Partial<BuilderIndicator> } }
  | { type: "REMOVE_INDICATOR"; payload: string }
  | { type: "ADD_ENTRY_CONDITION"; payload: BuilderCondition }
  | { type: "UPDATE_ENTRY_CONDITION"; payload: { id: string; updates: Partial<BuilderCondition> } }
  | { type: "REMOVE_ENTRY_CONDITION"; payload: string }
  | { type: "REORDER_ENTRY_CONDITIONS"; payload: BuilderCondition[] }
  | { type: "SET_ENTRY_LOGIC"; payload: "AND" | "OR" }
  | { type: "ADD_EXIT_CONDITION"; payload: BuilderCondition }
  | { type: "UPDATE_EXIT_CONDITION"; payload: { id: string; updates: Partial<BuilderCondition> } }
  | { type: "REMOVE_EXIT_CONDITION"; payload: string }
  | { type: "REORDER_EXIT_CONDITIONS"; payload: BuilderCondition[] }
  | { type: "SET_EXIT_LOGIC"; payload: "AND" | "OR" }
  | { type: "SET_RISK"; payload: Partial<RiskManagement> }
  | { type: "LOAD_STATE"; payload: BuilderState }
  | { type: "RESET" };

// ============================================================
// Operator Labels
// ============================================================

export const OPERATOR_LABELS: Record<ConditionOperator, string> = {
  greater_than: ">",
  less_than: "<",
  greater_equal: "≥",
  less_equal: "≤",
  cross_above: "상향돌파",
  cross_below: "하향돌파",
  equals: "=",
};

// 문장형 UI를 위한 한글 라벨
export const OPERATOR_SENTENCE_LABELS: Record<ConditionOperator, string> = {
  greater_than: "보다 클 때",
  less_than: "보다 작을 때",
  greater_equal: "이상일 때",
  less_equal: "이하일 때",
  cross_above: "상향돌파 할 때",
  cross_below: "하향돌파 할 때",
  equals: "와 같을 때",
};

// 교차 연산자 확인 헬퍼
export const CROSS_OPERATORS: ConditionOperator[] = ["cross_above", "cross_below"];

export const OPERATOR_OPTIONS: { value: ConditionOperator; label: string }[] = [
  { value: "greater_than", label: ">" },
  { value: "less_than", label: "<" },
  { value: "greater_equal", label: "≥" },
  { value: "less_equal", label: "≤" },
  { value: "cross_above", label: "상향돌파" },
  { value: "cross_below", label: "하향돌파" },
  { value: "equals", label: "=" },
];

// ============================================================
// Condition Templates (자주 사용되는 조건 패턴)
// ============================================================

export interface ConditionTemplate {
  id: string;
  label: string;
  description: string;
  category: "oscillator" | "crossover" | "band" | "trend";
  indicators: Array<{
    id: string;
    alias: string;
    params: Record<string, number>;
    output?: string;
  }>;
  condition: {
    leftIndicator: string;
    leftOutput?: string;
    operator: ConditionOperator;
    rightType: "indicator" | "value";
    rightIndicator?: string;
    rightOutput?: string;
    rightValue?: number;
  };
}

export const CONDITION_TEMPLATES: ConditionTemplate[] = [
  // 오실레이터 조건
  {
    id: "rsi_oversold",
    label: "RSI 과매도",
    description: "RSI가 30 아래로 떨어질 때",
    category: "oscillator",
    indicators: [{ id: "rsi", alias: "rsi_1", params: { period: 14 } }],
    condition: {
      leftIndicator: "rsi_1",
      operator: "less_than",
      rightType: "value",
      rightValue: 30,
    },
  },
  {
    id: "rsi_overbought",
    label: "RSI 과매수",
    description: "RSI가 70 위로 올라갈 때",
    category: "oscillator",
    indicators: [{ id: "rsi", alias: "rsi_1", params: { period: 14 } }],
    condition: {
      leftIndicator: "rsi_1",
      operator: "greater_than",
      rightType: "value",
      rightValue: 70,
    },
  },
  // 이동평균 교차
  {
    id: "golden_cross",
    label: "골든크로스",
    description: "단기 이평선이 장기 이평선 상향돌파",
    category: "crossover",
    indicators: [
      { id: "sma", alias: "sma_fast", params: { period: 5 } },
      { id: "sma", alias: "sma_slow", params: { period: 20 } },
    ],
    condition: {
      leftIndicator: "sma_fast",
      operator: "cross_above",
      rightType: "indicator",
      rightIndicator: "sma_slow",
    },
  },
  {
    id: "dead_cross",
    label: "데드크로스",
    description: "단기 이평선이 장기 이평선 하향돌파",
    category: "crossover",
    indicators: [
      { id: "sma", alias: "sma_fast", params: { period: 5 } },
      { id: "sma", alias: "sma_slow", params: { period: 20 } },
    ],
    condition: {
      leftIndicator: "sma_fast",
      operator: "cross_below",
      rightType: "indicator",
      rightIndicator: "sma_slow",
    },
  },
  // MACD 시그널
  {
    id: "macd_bull",
    label: "MACD 매수 시그널",
    description: "MACD가 시그널선 상향돌파",
    category: "crossover",
    indicators: [
      { id: "macd", alias: "macd_1", params: { fast: 12, slow: 26, signal: 9 }, output: "value" },
      { id: "macd", alias: "macd_1_sig", params: { fast: 12, slow: 26, signal: 9 }, output: "signal" },
    ],
    condition: {
      leftIndicator: "macd_1",
      leftOutput: "value",
      operator: "cross_above",
      rightType: "indicator",
      rightIndicator: "macd_1_sig",
      rightOutput: "signal",
    },
  },
  {
    id: "macd_bear",
    label: "MACD 매도 시그널",
    description: "MACD가 시그널선 하향돌파",
    category: "crossover",
    indicators: [
      { id: "macd", alias: "macd_1", params: { fast: 12, slow: 26, signal: 9 }, output: "value" },
      { id: "macd", alias: "macd_1_sig", params: { fast: 12, slow: 26, signal: 9 }, output: "signal" },
    ],
    condition: {
      leftIndicator: "macd_1",
      leftOutput: "value",
      operator: "cross_below",
      rightType: "indicator",
      rightIndicator: "macd_1_sig",
      rightOutput: "signal",
    },
  },
  // 볼린저 밴드
  {
    id: "bb_lower_touch",
    label: "볼린저 하단 터치",
    description: "종가가 볼린저밴드 하단 이하",
    category: "band",
    indicators: [{ id: "bollinger", alias: "bb_1", params: { period: 20, std: 2 }, output: "lower" }],
    condition: {
      leftIndicator: "close",
      operator: "less_equal",
      rightType: "indicator",
      rightIndicator: "bb_1",
      rightOutput: "lower",
    },
  },
  {
    id: "bb_upper_touch",
    label: "볼린저 상단 터치",
    description: "종가가 볼린저밴드 상단 이상",
    category: "band",
    indicators: [{ id: "bollinger", alias: "bb_1", params: { period: 20, std: 2 }, output: "upper" }],
    condition: {
      leftIndicator: "close",
      operator: "greater_equal",
      rightType: "indicator",
      rightIndicator: "bb_1",
      rightOutput: "upper",
    },
  },
  // 스토캐스틱
  {
    id: "stoch_oversold",
    label: "스토캐스틱 과매도",
    description: "%K가 20 아래일 때",
    category: "oscillator",
    indicators: [{ id: "stochastic", alias: "stoch_1", params: { k_period: 14, d_period: 3 }, output: "k" }],
    condition: {
      leftIndicator: "stoch_1",
      leftOutput: "k",
      operator: "less_than",
      rightType: "value",
      rightValue: 20,
    },
  },
  {
    id: "stoch_overbought",
    label: "스토캐스틱 과매수",
    description: "%K가 80 위일 때",
    category: "oscillator",
    indicators: [{ id: "stochastic", alias: "stoch_1", params: { k_period: 14, d_period: 3 }, output: "k" }],
    condition: {
      leftIndicator: "stoch_1",
      leftOutput: "k",
      operator: "greater_than",
      rightType: "value",
      rightValue: 80,
    },
  },
];

// 인기 지표 (지표 선택 UI 상단에 표시)
export const POPULAR_INDICATORS = ["rsi", "sma", "ema", "macd", "bollinger", "stochastic"];

// ============================================================
// Candlestick Signal Types
// ============================================================

export type CandlestickSignal = "bullish" | "bearish" | "detected";

export const CANDLESTICK_SIGNAL_LABELS: Record<CandlestickSignal, string> = {
  bullish: "강세 신호",
  bearish: "약세 신호",
  detected: "감지",
};

export const CANDLESTICK_SIGNAL_OPTIONS: { value: CandlestickSignal; label: string; description: string }[] = [
  { value: "bullish", label: "강세 신호", description: "패턴 값 > 0 (양수)" },
  { value: "bearish", label: "약세 신호", description: "패턴 값 < 0 (음수)" },
  { value: "detected", label: "감지", description: "패턴 값 ≠ 0 (강세/약세 무관)" },
];

// ============================================================
// Candlestick Condition Templates
// ============================================================

export interface CandlestickTemplate {
  id: string;
  label: string;
  description: string;
  category: "single" | "double" | "triple" | "reversal";
  patternId: string;
  signal: CandlestickSignal;
}

export const CANDLESTICK_TEMPLATES: CandlestickTemplate[] = [
  // 반전 패턴 (Reversal)
  {
    id: "hammer_reversal",
    label: "망치형 반전",
    description: "망치형 패턴 강세 신호 (하락 후 상승 반전)",
    category: "reversal",
    patternId: "hammer",
    signal: "bullish",
  },
  {
    id: "engulfing_bullish",
    label: "장악형 매수",
    description: "장악형 패턴 강세 신호 (강한 상승 반전)",
    category: "reversal",
    patternId: "engulfing",
    signal: "bullish",
  },
  {
    id: "engulfing_bearish",
    label: "장악형 매도",
    description: "장악형 패턴 약세 신호 (강한 하락 반전)",
    category: "reversal",
    patternId: "engulfing",
    signal: "bearish",
  },
  {
    id: "morning_star_buy",
    label: "샛별형 매수",
    description: "샛별형 패턴 강세 신호 (강한 상승 반전)",
    category: "triple",
    patternId: "morning_star",
    signal: "bullish",
  },
  {
    id: "evening_star_sell",
    label: "저녁별형 매도",
    description: "저녁별형 패턴 약세 신호 (강한 하락 반전)",
    category: "triple",
    patternId: "evening_star",
    signal: "bearish",
  },
  // 단일 캔들 패턴
  {
    id: "doji_detect",
    label: "도지 감지",
    description: "도지 패턴 감지 (우유부단, 추세 전환 가능)",
    category: "single",
    patternId: "doji",
    signal: "detected",
  },
  {
    id: "shooting_star_sell",
    label: "유성형 매도",
    description: "유성형 패턴 약세 신호 (상승 후 하락 반전)",
    category: "single",
    patternId: "shooting_star",
    signal: "bearish",
  },
  // 이중 캔들 패턴
  {
    id: "harami_bullish",
    label: "잉태형 매수",
    description: "잉태형 패턴 강세 신호",
    category: "double",
    patternId: "harami",
    signal: "bullish",
  },
  {
    id: "piercing_buy",
    label: "관통형 매수",
    description: "관통형 패턴 강세 신호 (상승 반전)",
    category: "double",
    patternId: "piercing",
    signal: "bullish",
  },
  {
    id: "dark_cloud_sell",
    label: "먹구름형 매도",
    description: "먹구름형 패턴 약세 신호 (하락 반전)",
    category: "double",
    patternId: "dark_cloud_cover",
    signal: "bearish",
  },
  // 삼중 캔들 패턴
  {
    id: "three_white_soldiers_buy",
    label: "적삼병 매수",
    description: "적삼병 패턴 강세 신호 (강한 상승 추세)",
    category: "triple",
    patternId: "three_white_soldiers",
    signal: "bullish",
  },
  {
    id: "three_black_crows_sell",
    label: "흑삼병 매도",
    description: "흑삼병 패턴 약세 신호 (강한 하락 추세)",
    category: "triple",
    patternId: "three_black_crows",
    signal: "bearish",
  },
];

// 캔들스틱 템플릿 카테고리 라벨
export const CANDLESTICK_TEMPLATE_CATEGORY_LABELS: Record<CandlestickTemplate["category"], string> = {
  reversal: "반전 패턴",
  single: "단일 캔들",
  double: "이중 캔들",
  triple: "삼중 캔들",
};

// 인기 캔들스틱 패턴 (빠른 선택용)
export const POPULAR_CANDLESTICK_PATTERNS = [
  "hammer",
  "engulfing",
  "morning_star",
  "doji",
  "three_white_soldiers",
  "shooting_star",
];
