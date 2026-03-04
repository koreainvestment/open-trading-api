/**
 * Strategies API
 */

import { apiGet, apiPost, type ApiResponse, type LogEntry } from "./client";
import type { Signal, ExecuteRequest, ExecuteResponse, StrategyInfo } from "@/types/signal";
import type { BuilderState } from "@/types/builder";

export interface StrategiesListResponse {
  strategies: StrategyInfo[];
}

export async function listStrategies(): Promise<StrategiesListResponse> {
  return apiGet<StrategiesListResponse>("/api/strategies");
}

export async function listCustomStrategies(): Promise<StrategiesListResponse> {
  return apiGet<StrategiesListResponse>("/api/strategies/custom");
}

export async function executeStrategy(
  strategyId: string,
  stocks: string[],
  params: Record<string, number> = {},
  builderState?: BuilderState
): Promise<ExecuteResponse> {
  const request: ExecuteRequest = {
    strategy_id: strategyId,
    stocks,
    params,
    builder_state: builderState,
  };
  return apiPost<ExecuteResponse>("/api/strategies/execute", request);
}

export interface IndicatorsResponse {
  indicators: Array<{
    name: string;
    label: string;
    params: string[];
    example: string;
  }>;
  variables: string[];
  operators: {
    comparison: string[];
    crossover: string[];
    logical: string[];
  };
}

export async function listIndicators(): Promise<IndicatorsResponse> {
  return apiGet<IndicatorsResponse>("/api/strategies/indicators");
}

export interface BuildRequest {
  name: string;
  buy_condition: string;
  sell_condition?: string;
}

export interface BuildResponse {
  status: "success" | "error";
  message: string;
  file_path?: string;
  strategy_name?: string;
}

export async function buildStrategy(request: BuildRequest): Promise<BuildResponse> {
  return apiPost<BuildResponse>("/api/strategies/build", request);
}

export interface PreviewResponse {
  status: "success" | "error";
  code?: string;
  required_days?: number;
  message?: string;
}

export async function previewStrategy(request: BuildRequest): Promise<PreviewResponse> {
  return apiPost<PreviewResponse>("/api/strategies/preview", request);
}

export interface PreviewCodeResponse {
  status: "success" | "error";
  code?: string;
  buy_dsl?: string;
  sell_dsl?: string;
  message?: string;
}

export async function previewCodeFromState(builderState: BuilderState): Promise<PreviewCodeResponse> {
  return apiPost<PreviewCodeResponse>("/api/strategies/preview-code", {
    builder_state: builderState,
  });
}
