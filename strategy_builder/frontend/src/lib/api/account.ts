/**
 * Account API
 */

import { apiGet, type ApiResponse } from "./client";
import type { AccountInfo, Holding, Balance, BuyableInfo } from "@/types/account";

export async function getAccountInfo(): Promise<ApiResponse<AccountInfo>> {
  return apiGet<ApiResponse<AccountInfo>>("/api/account/info");
}

export async function getHoldings(): Promise<ApiResponse<Holding[]>> {
  return apiGet<ApiResponse<Holding[]>>("/api/account/holdings");
}

export async function getBalance(): Promise<ApiResponse<Balance>> {
  return apiGet<ApiResponse<Balance>>("/api/account/balance");
}

export async function getBuyableAmount(
  stockCode: string,
  price: number = 0
): Promise<ApiResponse<BuyableInfo>> {
  const query = price > 0 ? `?price=${price}` : "";
  return apiGet<ApiResponse<BuyableInfo>>(`/api/account/buyable/${stockCode}${query}`);
}
