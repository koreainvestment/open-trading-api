/**
 * Orders API
 * 
 * Account Information and Pending Orders API:
 * - GET /account: 통합 계좌 정보 (예수금 + 보유종목)
 * - GET /pending: 미체결 주문 목록
 * - POST /cancel: 주문 취소
 * - POST /account/clear-cache: 캐시 삭제
 */

import { apiGet, apiPost, type LogEntry } from "./client";
import type { OrderRequest } from "@/types/order";

export interface OrderResponse {
  status: "success" | "error";
  message: string;
  data?: {
    order_id: string;
    status: string;
    message: string;
  };
  logs: LogEntry[];
}

export interface AccountInfo {
  deposit: {
    deposit: number;
    total_eval: number;
    purchase_amount: number;
    eval_amount: number;
    profit_loss: number;
  };
  holdings: HoldingItem[];
  holdings_count: number;
  cached_at?: string;
  stale?: boolean;
  error?: string;
}

export interface HoldingItem {
  stock_code: string;
  stock_name: string;
  quantity: number;
  avg_price: number;
  current_price: number;
  eval_amount: number;
  profit_loss: number;
  profit_rate: number;
}

export interface PendingOrder {
  order_no: string;
  org_no?: string;
  stock_code: string;
  stock_name: string;
  order_type: string;
  order_qty: number;
  order_price: number;
  filled_qty: number;
  unfilled_qty: number;
  order_time: string;
}

export interface PendingOrdersResponse {
  status: string;
  orders: PendingOrder[];
  total_count: number;
}

export interface CancelOrderRequest {
  order_no: string;
  org_no: string;
  stock_code: string;
  qty: number;
}

export interface CancelOrderResponse {
  status: string;
  success: boolean;
  order_no: string;
  message: string;
}

/**
 * 주문 실행
 */
export async function executeOrder(request: OrderRequest): Promise<OrderResponse> {
  return apiPost<OrderResponse>("/api/orders/execute", {
    stock_code: request.stock_code,
    stock_name: request.stock_name,
    action: request.action,
    order_type: request.order_type,
    price: request.price || 0,
    quantity: request.quantity,
    signal_reason: request.signal_reason || "수동 주문",
  });
}

/**
 * 통합 계좌 정보 조회 (30초 캐싱)
 * 
 * Note: 이 함수는 orders API를 통해 계좌 정보를 조회합니다.
 * account.ts의 getAccountInfo와 다른 API를 사용합니다.
 */
export async function getOrdersAccount(): Promise<AccountInfo> {
  const response = await apiGet<{ status: string } & AccountInfo>("/api/orders/account");
  return response;
}

/**
 * 계좌 정보 캐시 삭제
 */
export async function clearAccountCache(): Promise<{ status: string; message: string }> {
  return apiPost<{ status: string; message: string }>("/api/orders/account/clear-cache");
}

/**
 * 미체결 주문 목록 조회
 */
export async function getPendingOrders(): Promise<PendingOrdersResponse> {
  return apiGet<PendingOrdersResponse>("/api/orders/pending");
}

/**
 * 주문 취소
 */
export async function cancelOrder(request: CancelOrderRequest): Promise<CancelOrderResponse> {
  return apiPost<CancelOrderResponse>("/api/orders/cancel", request);
}
