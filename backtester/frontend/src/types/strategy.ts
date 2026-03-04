/**
 * 전략 타입 정의
 */

/**
 * 파라미터 정의 (슬라이더용)
 */
export interface ParamDefinition {
  default: number;
  min: number;
  max: number;
  step?: number;
  type?: "int" | "float";
  label?: string;
}

export interface Strategy {
  id: string;
  name: string;
  description: string;
  category: string;
  tags?: string[];
  params?: Record<string, ParamDefinition>;  // 파라미터 정의
}

export interface StrategyDetail extends Strategy {
  indicators: IndicatorConfig[];
  entry: ConditionGroup;
  exit: ConditionGroup;
  param_values: Record<string, number>;
  risk_management: RiskConfig;
}

export interface IndicatorConfig {
  id: string;
  alias?: string;
  params: Record<string, number>;
}

export interface Condition {
  indicator: string;
  operator: string;
  compare_to: string | number;
}

export interface ConditionGroup {
  logic: "AND" | "OR";
  conditions: Condition[];
}

export interface RiskConfig {
  stop_loss?: { enabled: boolean; percent: number };
  take_profit?: { enabled: boolean; percent: number };
  trailing_stop?: { enabled: boolean; percent: number };
}

export interface StrategyListResponse {
  success: boolean;
  data: Strategy[];
  total: number;
}

export interface StrategyDetailResponse {
  success: boolean;
  data: StrategyDetail;
}

export interface Category {
  id: string;
  name: string;
}

export interface CategoryListResponse {
  success: boolean;
  data: Category[];
}
