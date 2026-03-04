/**
 * 백테스트 API
 */

import { apiPost } from "./client";
import type {
  BacktestRequest,
  CustomBacktestRequest,
  BacktestResponse,
} from "@/types";

/**
 * 백테스트 실행 (Preset 전략)
 */
export async function runBacktest(request: BacktestRequest): Promise<BacktestResponse> {
  return apiPost("/api/backtest/run", request);
}

/**
 * 커스텀 전략 백테스트 실행 (YAML)
 */
export async function runCustomBacktest(
  yamlContent: string,
  symbols: string[],
  startDate: string,
  endDate: string,
  initialCapital: number,
  commissionRate?: number,
  taxRate?: number,
  slippage?: number
): Promise<BacktestResponse> {
  const request: CustomBacktestRequest = {
    yaml_content: yamlContent,
    symbols,
    start_date: startDate,
    end_date: endDate,
    initial_capital: initialCapital,
    commission_rate: commissionRate,
    tax_rate: taxRate,
    slippage,
  };
  return apiPost("/api/backtest/run-custom", request);
}
