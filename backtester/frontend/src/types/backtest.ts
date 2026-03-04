/**
 * 백테스트 타입 정의 - Lean 전체 통계 반영
 */

export interface BacktestRequest {
  strategy_id: string;
  symbols: string[];
  start_date: string;
  end_date: string;
  initial_capital: number;
  commission_rate?: number;
  tax_rate?: number;
  slippage?: number;
  param_overrides?: Record<string, number>;
}

export interface CustomBacktestRequest {
  yaml_content: string;
  symbols: string[];
  start_date: string;
  end_date: string;
  initial_capital: number;
  commission_rate?: number;
  tax_rate?: number;
  slippage?: number;
}

/**
 * Lean 전체 통계 - 카테고리별 그룹화
 */
export interface PerformanceMetrics {
  basic: {
    total_return: number;
    annual_return: number;
    max_drawdown: number;
    start_equity: number;
    end_equity: number;
  };
  risk: {
    sharpe_ratio: number;
    sortino_ratio: number;
    probabilistic_sharpe: number;
  };
  greeks: {
    alpha: number;
    beta: number;
  };
  volatility: {
    annual_std_dev: number;
    annual_variance: number;
  };
  benchmark: {
    information_ratio: number;
    tracking_error: number;
    treynor_ratio: number;
  };
  trading: {
    total_orders: number;
    win_rate: number;
    loss_rate: number;
    avg_win: number;
    avg_loss: number;
    profit_loss_ratio: number;
    expectancy: number;
  };
  other: {
    total_fees: number;
    portfolio_turnover: number;
    estimated_capacity: number;
    drawdown_recovery: number;
  };
}

export interface TradeInfo {
  symbol: string;
  direction: "Buy" | "Sell";
  quantity: number;
  price: number;
  time: string;
  profit?: number;
  profit_percent?: number;
}

export interface BacktestResult {
  run_id: string;
  strategy_name: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_capital: number;
  net_profit: number;
  net_profit_percent: number;
  metrics: PerformanceMetrics;
  equity_curve: Record<string, number>;
  benchmark_curve?: Record<string, number>;  // KOSPI 수익률 커브 (%)
  trades_count: number;
  trades?: TradeInfo[];  // 거래 내역
}

export interface BacktestResponse {
  success: boolean;
  data: BacktestResult;
  message?: string;
}

/**
 * 차트 데이터 포인트
 */
export interface EquityDataPoint {
  date: string;
  value: number;
}

export interface DrawdownDataPoint {
  date: string;
  drawdown: number;
}
