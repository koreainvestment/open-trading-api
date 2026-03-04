"use client";

import { useState, useCallback } from "react";
import {
  TrendingUp,
  TrendingDown,
  Briefcase,
  RefreshCw,
  Clock,
  X,
  Wallet,
  Loader2,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { Holding, Balance } from "@/types/account";
import type { PendingOrder, CancelOrderRequest } from "@/lib/api/orders";

interface HoldingsListProps {
  holdings: Holding[];
  pendingOrders?: PendingOrder[];
  balance?: Balance | null;
  onRefresh?: () => void;
  onCancelOrder?: (request: CancelOrderRequest) => Promise<void>;
  isLoading?: boolean;
}

type TabType = "holdings" | "pending";

export function HoldingsList({
  holdings,
  pendingOrders = [],
  balance,
  onRefresh,
  onCancelOrder,
  isLoading,
}: HoldingsListProps) {
  const [activeTab, setActiveTab] = useState<TabType>("holdings");
  const [cancellingOrderNo, setCancellingOrderNo] = useState<string | null>(null);

  const totalEval = holdings.reduce((sum, h) => sum + h.eval_amount, 0);
  const totalProfitLoss = holdings.reduce((sum, h) => sum + h.profit_loss, 0);
  const totalProfitRate =
    totalEval > 0 ? (totalProfitLoss / (totalEval - totalProfitLoss)) * 100 : 0;

  const handleCancelOrder = useCallback(
    async (order: PendingOrder) => {
      if (!onCancelOrder) return;

      setCancellingOrderNo(order.order_no);
      try {
        await onCancelOrder({
          order_no: order.order_no,
          org_no: order.org_no ?? "",
          stock_code: order.stock_code,
          qty: order.unfilled_qty,
        });
      } finally {
        setCancellingOrderNo(null);
      }
    },
    [onCancelOrder]
  );

  return (
    <div className="card p-0 overflow-hidden">
      {/* Balance Summary */}
      {balance && (
        <div className="px-4 py-3 bg-gradient-to-r from-primary/5 to-primary/10 border-b border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-2">
            <Wallet className="w-4 h-4 text-primary" />
            <span className="text-xs font-medium text-slate-600 dark:text-slate-400">
              계좌 요약
            </span>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-slate-500">예수금</p>
              <p className="text-sm font-bold text-slate-900 dark:text-white">
                {balance.deposit.toLocaleString()}원
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs text-slate-500">총 평가</p>
              <p className="text-sm font-bold text-slate-900 dark:text-white">
                {balance.total_eval.toLocaleString()}원
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Header with Tabs */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-slate-700">
        <div className="flex items-center gap-1">
          {/* Holdings Tab */}
          <button
            onClick={() => setActiveTab("holdings")}
            className={cn(
              "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors focus-ring",
              activeTab === "holdings"
                ? "bg-primary/10 text-primary"
                : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
            )}
            aria-label="보유종목 탭"
          >
            <Briefcase className="w-4 h-4" />
            <span>보유종목</span>
            <span
              className={cn(
                "text-xs px-1.5 py-0.5 rounded-full",
                activeTab === "holdings"
                  ? "bg-primary/20"
                  : "bg-slate-100 dark:bg-slate-800"
              )}
            >
              {holdings.length}
            </span>
          </button>

          {/* Pending Orders Tab */}
          <button
            onClick={() => setActiveTab("pending")}
            className={cn(
              "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors focus-ring",
              activeTab === "pending"
                ? "bg-amber-500/10 text-amber-600"
                : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
            )}
            aria-label="미체결 주문 탭"
          >
            <Clock className="w-4 h-4" />
            <span>미체결</span>
            {pendingOrders.length > 0 && (
              <span
                className={cn(
                  "text-xs px-1.5 py-0.5 rounded-full",
                  activeTab === "pending"
                    ? "bg-amber-500/20"
                    : "bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400"
                )}
              >
                {pendingOrders.length}
              </span>
            )}
          </button>
        </div>

        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors focus-ring"
            aria-label="새로고침"
          >
            <RefreshCw
              className={cn("w-4 h-4 text-slate-400", isLoading && "animate-spin")}
            />
          </button>
        )}
      </div>

      {/* Holdings Tab Content */}
      {activeTab === "holdings" && (
        <>
          {/* Holdings Summary */}
          {holdings.length > 0 && (
            <div className="grid grid-cols-2 gap-4 p-4 bg-slate-50 dark:bg-slate-800/50">
              <div>
                <p className="text-sm text-slate-500">총 평가금액</p>
                <p className="text-lg font-bold">{totalEval.toLocaleString()}원</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-slate-500">총 손익</p>
                <p
                  className={cn(
                    "text-lg font-bold",
                    totalProfitLoss >= 0 ? "text-profit" : "text-loss"
                  )}
                >
                  {totalProfitLoss >= 0 ? "+" : ""}
                  {totalProfitLoss.toLocaleString()}원
                  <span className="text-sm ml-1">
                    ({totalProfitRate >= 0 ? "+" : ""}
                    {totalProfitRate.toFixed(2)}%)
                  </span>
                </p>
              </div>
            </div>
          )}

          {/* Holdings List */}
          {holdings.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-400">
              <Briefcase className="w-12 h-12 mb-3 opacity-30" />
              <p>보유 종목이 없습니다</p>
            </div>
          ) : (
            <div className="divide-y divide-slate-200 dark:divide-slate-700">
              {holdings.map((holding) => (
                <HoldingItem key={holding.stock_code} holding={holding} />
              ))}
            </div>
          )}
        </>
      )}

      {/* Pending Orders Tab Content */}
      {activeTab === "pending" && (
        <>
          {pendingOrders.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-400">
              <Clock className="w-12 h-12 mb-3 opacity-30" />
              <p>미체결 주문이 없습니다</p>
            </div>
          ) : (
            <div className="divide-y divide-slate-200 dark:divide-slate-700">
              {pendingOrders.map((order, idx) => (
                <PendingOrderItem
                  key={order.order_no || `pending-${idx}`}
                  order={order}
                  onCancel={handleCancelOrder}
                  isCancelling={cancellingOrderNo === order.order_no}
                />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

interface HoldingItemProps {
  holding: Holding;
}

function HoldingItem({ holding }: HoldingItemProps) {
  const isProfitable = holding.profit_loss >= 0;

  return (
    <div className="flex items-center gap-4 p-4 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
      {/* Stock Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium truncate">{holding.stock_name}</span>
          <span className="text-xs text-slate-400 font-mono">
            {holding.stock_code}
          </span>
        </div>
        <div className="flex items-center gap-3 mt-1 text-sm text-slate-500">
          <span>{holding.quantity}주</span>
          <span>평균 {Math.round(holding.avg_price).toLocaleString()}원</span>
        </div>
      </div>

      {/* Current Value */}
      <div className="text-right">
        <p className="font-medium">{holding.current_price.toLocaleString()}원</p>
        <div
          className={cn(
            "flex items-center justify-end gap-1 text-sm",
            isProfitable ? "text-profit" : "text-loss"
          )}
        >
          {isProfitable ? (
            <TrendingUp className="w-4 h-4" />
          ) : (
            <TrendingDown className="w-4 h-4" />
          )}
          <span>
            {isProfitable ? "+" : ""}
            {holding.profit_rate.toFixed(2)}%
          </span>
        </div>
      </div>
    </div>
  );
}

interface PendingOrderItemProps {
  order: PendingOrder;
  onCancel: (order: PendingOrder) => void;
  isCancelling: boolean;
}

function PendingOrderItem({ order, onCancel, isCancelling }: PendingOrderItemProps) {
  const isBuy = order.order_type.includes("매수") || order.order_type === "BUY";

  return (
    <div className="flex items-center gap-4 p-4 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
      {/* Order Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span
            className={cn(
              "text-xs px-1.5 py-0.5 rounded font-medium",
              isBuy
                ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
            )}
          >
            {isBuy ? "매수" : "매도"}
          </span>
          <span className="font-medium truncate">{order.stock_name}</span>
          <span className="text-xs text-slate-400 font-mono">
            {order.stock_code}
          </span>
        </div>
        <div className="flex items-center gap-3 mt-1 text-sm text-slate-500">
          <span className="font-mono">
            {order.order_price.toLocaleString()}원
          </span>
          <span>
            {order.unfilled_qty}/{order.order_qty}주
          </span>
          <span className="text-xs">{order.order_time}</span>
        </div>
      </div>

      {/* Cancel Button */}
      <button
        onClick={() => onCancel(order)}
        disabled={isCancelling}
        className={cn(
          "px-3 py-1.5 rounded-lg text-sm font-medium transition-colors",
          isCancelling
            ? "bg-slate-100 dark:bg-slate-800 text-slate-400"
            : "bg-red-50 hover:bg-red-100 dark:bg-red-900/20 dark:hover:bg-red-900/30 text-red-500"
        )}
      >
        {isCancelling ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          "주문 취소"
        )}
      </button>
    </div>
  );
}

export default HoldingsList;
