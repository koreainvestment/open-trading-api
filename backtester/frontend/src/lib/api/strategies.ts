/**
 * 전략 API
 */

import { apiGet } from "./client";
import type {
  StrategyListResponse,
  StrategyDetailResponse,
  CategoryListResponse,
} from "@/types";

/**
 * 전략 목록 조회
 */
export async function listStrategies(category?: string): Promise<StrategyListResponse> {
  const path = category
    ? `/api/strategies?category=${encodeURIComponent(category)}`
    : "/api/strategies";
  return apiGet(path);
}

/**
 * 전략 상세 조회
 */
export async function getStrategy(id: string): Promise<StrategyDetailResponse> {
  return apiGet(`/api/strategies/${encodeURIComponent(id)}`);
}

/**
 * 카테고리 목록 조회
 */
export async function getCategories(): Promise<CategoryListResponse> {
  return apiGet("/api/strategies/categories");
}

/**
 * 전략 YAML 조회
 */
export async function getStrategyYaml(id: string): Promise<{ success: boolean; data: { id: string; name: string; yaml: string } }> {
  return apiGet(`/api/strategies/${encodeURIComponent(id)}/yaml`);
}

/**
 * 전략 Python 코드 조회
 */
export async function getStrategyPython(id: string): Promise<{ success: boolean; data: { id: string; name: string; python: string } }> {
  return apiGet(`/api/strategies/${encodeURIComponent(id)}/python`);
}

/**
 * Lean 파라미터 조회
 */
export async function getLeanParams(id: string): Promise<{ success: boolean; data: string[] }> {
  return apiGet(`/api/strategies/${encodeURIComponent(id)}/lean-params`);
}
