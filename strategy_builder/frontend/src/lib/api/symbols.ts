/**
 * Symbols API
 * 
 * Stock Master File Management System
 */

import { apiGet, apiPost } from "./client";
import type { Symbol, SymbolSearchResponse, MasterStatus, CollectResult } from "@/types/symbols";

interface SymbolDetailResponse {
  status: string;
  data: Symbol | null;
  message?: string;
}

/**
 * 종목 검색
 * @param query 검색어 (종목코드 또는 종목명)
 * @param limit 최대 결과 수 (기본 20)
 * @param exchange 거래소 필터 (kospi, kosdaq)
 */
export async function searchSymbols(
  query: string,
  limit: number = 20,
  exchange?: "kospi" | "kosdaq"
): Promise<SymbolSearchResponse> {
  const params = new URLSearchParams({
    q: query,
    limit: limit.toString(),
  });
  if (exchange) {
    params.append("exchange", exchange);
  }
  return apiGet<SymbolSearchResponse>(`/api/symbols/search?${params}`);
}

/**
 * 종목코드로 종목 상세 정보 조회 (마스터파일 기반)
 */
export async function getSymbolByCode(code: string): Promise<Symbol | null> {
  try {
    const response = await apiGet<SymbolDetailResponse>(`/api/symbols/${code}`);
    return response.data;
  } catch {
    return null;
  }
}

/**
 * 마스터파일 상태 조회
 */
export async function getMasterStatus(): Promise<MasterStatus> {
  return apiGet<MasterStatus>("/api/symbols/status");
}

/**
 * 마스터파일 수집 (다운로드 및 저장)
 */
export async function collectMasterFiles(): Promise<CollectResult> {
  return apiPost<CollectResult>("/api/symbols/collect");
}
