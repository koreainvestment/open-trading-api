"use client";

import { useState, useEffect, useCallback } from "react";
import {
  X,
  AlertTriangle,
  CheckCircle,
  Loader2,
  TrendingUp,
  TrendingDown,
  Maximize2,
  Wallet,
  Package,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { OrderbookPanel } from "./OrderbookPanel";
import type { OrderRequest, OrderAction, OrderType } from "@/types/order";
import type { SignalResult } from "@/types/signal";
import type { PriceData } from "@/lib/api";
import type { BuyableInfo } from "@/types/account";

interface OrderConfirmModalProps {
  signal: SignalResult;
  priceData: PriceData | null;
  buyable?: BuyableInfo | null;
  sellableQty?: number | null;
  onConfirm: (request: OrderRequest) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

export function OrderConfirmModal({
  signal,
  priceData,
  buyable,
  sellableQty,
  onConfirm,
  onCancel,
  isLoading,
}: OrderConfirmModalProps) {
  const currentPrice = priceData?.price || 0;
  const change = priceData?.change || 0;
  const changeRate = priceData?.change_rate || 0;

  const [quantity, setQuantity] = useState(1);
  const [orderType, setOrderType] = useState<OrderType>("limit");
  const [limitPrice, setLimitPrice] = useState(signal.target_price || currentPrice);
  const [showOrderbook, setShowOrderbook] = useState(true);

  // Update limit price when current price loads (if no target_price)
  useEffect(() => {
    if (!signal.target_price && currentPrice > 0) {
      setLimitPrice(currentPrice);
    }
  }, [currentPrice, signal.target_price]);

  const action: OrderAction = signal.action === "BUY" ? "BUY" : "SELL";
  const price = orderType === "market" ? currentPrice : limitPrice;
  const estimatedAmount = price * quantity;
  const isBuy = action === "BUY";

  // Max quantity: buyable amount for BUY, holding quantity for SELL
  const maxQuantity = isBuy
    ? (buyable && limitPrice > 0 ? Math.floor(buyable.amount / limitPrice) : 0)
    : (sellableQty ?? 0);

  const handlePriceSelect = useCallback((selectedPrice: number) => {
    setLimitPrice(selectedPrice);
    setOrderType("limit");
  }, []);

  const handleMaxQuantity = useCallback(() => {
    if (maxQuantity > 0) {
      setQuantity(maxQuantity);
    }
  }, [maxQuantity]);

  const handleConfirm = async () => {
    const request: OrderRequest = {
      stock_code: signal.code,
      stock_name: signal.name,
      action,
      order_type: orderType,
      price: orderType === "limit" ? limitPrice : undefined,
      quantity,
      signal_reason: signal.reason,
    };
    await onConfirm(request);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className={cn(
        "w-full bg-white dark:bg-slate-900 rounded-2xl shadow-2xl overflow-hidden",
        showOrderbook ? "max-w-3xl" : "max-w-md"
      )}>
        {/* Header */}
        <div
          className={cn(
            "px-6 py-4 flex items-center justify-between",
            isBuy ? "bg-green-500" : "bg-red-500"
          )}
        >
          <h2 className="text-lg font-bold text-white">
            {isBuy ? "매수" : "매도"} 주문 확인
          </h2>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowOrderbook(!showOrderbook)}
              className="p-1 rounded-full hover:bg-white/20 transition-colors"
              title={showOrderbook ? "호가창 숨기기" : "호가창 표시"}
            >
              <Maximize2 className="w-5 h-5 text-white" />
            </button>
            <button
              onClick={onCancel}
              className="p-1 rounded-full hover:bg-white/20 transition-colors"
            >
              <X className="w-5 h-5 text-white" />
            </button>
          </div>
        </div>

        {/* Content - Two Column Layout */}
        <div className={cn("flex", showOrderbook ? "flex-row" : "flex-col")}>
          {/* Left Column - Orderbook */}
          {showOrderbook && (
            <div className="w-64 border-r border-slate-200 dark:border-slate-700 p-4 bg-slate-50 dark:bg-slate-800/50 max-h-[600px] overflow-auto">
              <OrderbookPanel
                stockCode={signal.code}
                stockName={signal.name}
                onPriceSelect={handlePriceSelect}
                realtime={true}
              />
            </div>
          )}

          {/* Right Column - Order Form */}
          <div className="flex-1 p-6 space-y-5 max-h-[600px] overflow-auto">
            {/* Stock Info with Price */}
            <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="font-bold text-lg">{signal.name}</p>
                  <p className="text-sm text-slate-500 font-mono">{signal.code}</p>
                </div>
                {change !== 0 && (
                  <div
                    className={cn(
                      "w-10 h-10 rounded-full flex items-center justify-center",
                      change > 0
                        ? "bg-red-100 dark:bg-red-900/30"
                        : "bg-blue-100 dark:bg-blue-900/30"
                    )}
                  >
                    {change > 0 ? (
                      <TrendingUp className="w-5 h-5 text-red-500" />
                    ) : (
                      <TrendingDown className="w-5 h-5 text-blue-500" />
                    )}
                  </div>
                )}
              </div>

              {/* Current Price */}
              <div className="flex items-baseline gap-3">
                <span
                  className={cn(
                    "text-2xl font-bold font-mono tabular-nums",
                    change > 0
                      ? "text-red-500"
                      : change < 0
                      ? "text-blue-500"
                      : "text-slate-900 dark:text-slate-100"
                  )}
                >
                  {currentPrice.toLocaleString()}
                </span>
                <span className="text-sm text-slate-500">원</span>
              </div>

              {/* Change Info */}
              {(change !== 0 || changeRate !== 0) && (
                <div
                  className={cn(
                    "mt-1 flex items-center gap-2 text-sm font-mono tabular-nums",
                    change > 0
                      ? "text-red-500"
                      : change < 0
                      ? "text-blue-500"
                      : "text-slate-500"
                  )}
                >
                  <span>
                    {change > 0 ? "▲" : change < 0 ? "▼" : ""}{" "}
                    {change > 0 ? "+" : ""}
                    {change.toLocaleString()}
                  </span>
                  <span className="opacity-70">
                    ({changeRate > 0 ? "+" : ""}
                    {changeRate.toFixed(2)}%)
                  </span>
                </div>
              )}
            </div>

            {/* Buyable Amount (for BUY orders) */}
            {isBuy && buyable && (
              <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Wallet className="w-4 h-4 text-green-600" />
                  <span className="text-sm text-green-700 dark:text-green-400">
                    매수가능금액
                  </span>
                </div>
                <span className="font-mono font-medium text-green-700 dark:text-green-400">
                  {buyable.amount.toLocaleString()}원
                </span>
              </div>
            )}

            {/* Sellable Quantity (for SELL orders) */}
            {!isBuy && sellableQty != null && (
              <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Package className="w-4 h-4 text-red-600" />
                  <span className="text-sm text-red-700 dark:text-red-400">
                    보유수량
                  </span>
                </div>
                <span className="font-mono font-medium text-red-700 dark:text-red-400">
                  {sellableQty.toLocaleString()}주
                </span>
              </div>
            )}

            {/* Order Type */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                주문 유형
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => setOrderType("limit")}
                  className={cn(
                    "px-4 py-2 rounded-lg border-2 transition-all",
                    orderType === "limit"
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-slate-200 dark:border-slate-700"
                  )}
                >
                  지정가
                </button>
                <button
                  onClick={() => setOrderType("market")}
                  className={cn(
                    "px-4 py-2 rounded-lg border-2 transition-all",
                    orderType === "market"
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-slate-200 dark:border-slate-700"
                  )}
                >
                  시장가
                </button>
              </div>
            </div>

            {/* Limit Price */}
            {orderType === "limit" && (
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  지정가
                </label>
                <div className="relative">
                  <input
                    type="number"
                    value={limitPrice}
                    onChange={(e) => setLimitPrice(Number(e.target.value))}
                    className="w-full px-4 py-3 pr-12 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900 focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                  <span className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500">
                    원
                  </span>
                </div>
                {showOrderbook && (
                  <p className="text-xs text-slate-400 mt-1">
                    호가창에서 가격을 클릭하여 선택할 수 있습니다
                  </p>
                )}
              </div>
            )}

            {/* Quantity */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
                  수량
                </label>
                {isBuy && maxQuantity > 0 && (
                  <button
                    onClick={handleMaxQuantity}
                    className="text-xs text-primary hover:underline"
                  >
                    최대 {maxQuantity}주
                  </button>
                )}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="w-10 h-10 flex items-center justify-center rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800"
                >
                  -
                </button>
                <input
                  type="number"
                  min={1}
                  value={quantity}
                  onChange={(e) => setQuantity(Math.max(1, Number(e.target.value)))}
                  className="flex-1 px-4 py-3 text-center border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900 focus:ring-2 focus:ring-primary focus:border-transparent"
                />
                <button
                  onClick={() => setQuantity(quantity + 1)}
                  className="w-10 h-10 flex items-center justify-center rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800"
                >
                  +
                </button>
              </div>
            </div>

            {/* Estimated Amount */}
            <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-slate-600 dark:text-slate-400">
                  예상 금액
                </span>
                <span className="text-xl font-bold">
                  {estimatedAmount.toLocaleString()}원
                </span>
              </div>
              {isBuy && buyable && estimatedAmount > buyable.amount && (
                <p className="text-xs text-red-500 mt-1">
                  매수가능금액을 초과했습니다
                </p>
              )}
            </div>

            {/* Warning */}
            <div className="flex items-start gap-3 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
              <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-yellow-700 dark:text-yellow-400">
                주문 실행 시 실제 체결이 이루어집니다. 주문 내용을 다시 확인해
                주세요.
              </p>
            </div>

            {/* Footer */}
            <div className="flex gap-3 pt-2">
              <button
                onClick={onCancel}
                disabled={isLoading}
                className="flex-1 px-4 py-3 border border-slate-200 dark:border-slate-700 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                취소
              </button>
              <button
                onClick={handleConfirm}
                disabled={isLoading || (isBuy && !!buyable && estimatedAmount > buyable.amount)}
                className={cn(
                  "flex-1 px-4 py-3 rounded-lg text-white font-medium transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed",
                  isBuy ? "bg-green-500 hover:bg-green-600" : "bg-red-500 hover:bg-red-600"
                )}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    주문 중...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    {isBuy ? "매수" : "매도"} 주문
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default OrderConfirmModal;
