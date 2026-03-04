/**
 * Signal Types
 */

export type SignalAction = "BUY" | "SELL" | "HOLD" | "ERROR";

export interface Signal {
  stock_code: string;
  stock_name: string;
  action: SignalAction;
  strength: number;
  reason: string;
  target_price?: number;
}

// Alias for API response
export interface SignalResult {
  code: string;
  name: string;
  action: SignalAction;
  strength: number;
  reason: string;
  target_price?: number;
}

import type { BuilderState } from "./builder";

export interface StrategyInfo {
  id: string;
  name: string;
  description: string;
  category: string;
  params: StrategyParam[];
  builder_state?: BuilderState;  // SSoT: Visual Builder용 상태
  isLocal?: boolean;  // 로컬 저장 전략 여부
}

export interface StrategyParam {
  name: string;
  label: string;
  min: number;
  max: number;
  default: number;
  step: number;
}

export interface ExecuteRequest {
  strategy_id: string;
  stocks: string[];
  params: Record<string, number>;
  builder_state?: BuilderState;  // Local strategy builder state
}

export interface ExecuteResponse {
  status: "success" | "error";
  results: SignalResult[];
  logs: LogEntry[];
  message?: string;
}

export interface LogEntry {
  type: "info" | "success" | "error" | "warning";
  message: string;
  timestamp?: string;
}
