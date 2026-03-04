"use client";

import { CheckCircle, XCircle, X, Copy, Check } from "lucide-react";
import { useState, useCallback } from "react";
import { cn } from "@/lib/utils";
import type { OrderResult, OrderAction } from "@/types/order";

interface OrderInfo {
  stock_name: string;
  stock_code: string;
  action: OrderAction;
  quantity: number;
  price: number;
}

interface OrderResultModalProps {
  result: OrderResult;
  orderInfo: OrderInfo;
  onClose: () => void;
}

export function OrderResultModal({
  result,
  orderInfo,
  onClose,
}: OrderResultModalProps) {
  const [copied, setCopied] = useState(false);
  const isSuccess = result.status === "success";
  const isBuy = orderInfo.action === "BUY";

  const handleCopyOrderId = useCallback(() => {
    if (result.order_id) {
      navigator.clipboard.writeText(result.order_id);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [result.order_id]);

  const totalAmount = orderInfo.price * orderInfo.quantity;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-md bg-white dark:bg-slate-900 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div
          className={cn(
            "px-6 py-6 flex flex-col items-center",
            isSuccess
              ? "bg-gradient-to-b from-green-500 to-green-600"
              : "bg-gradient-to-b from-red-500 to-red-600"
          )}
        >
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-1 rounded-full hover:bg-white/20 transition-colors"
          >
            <X className="w-5 h-5 text-white" />
          </button>

          {isSuccess ? (
            <CheckCircle className="w-16 h-16 text-white mb-3" />
          ) : (
            <XCircle className="w-16 h-16 text-white mb-3" />
          )}

          <h2 className="text-xl font-bold text-white">
            {isSuccess ? "주문 완료" : "주문 실패"}
          </h2>
          <p className="text-white/80 text-sm mt-1">
            {isSuccess
              ? `${isBuy ? "매수" : "매도"} 주문이 접수되었습니다`
              : "주문 처리 중 오류가 발생했습니다"}
          </p>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Order Details */}
          <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-500">종목</span>
              <span className="font-medium">
                {orderInfo.stock_name}
                <span className="ml-2 text-xs text-slate-400 font-mono">
                  {orderInfo.stock_code}
                </span>
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-500">구분</span>
              <span
                className={cn(
                  "px-2 py-0.5 rounded text-sm font-medium",
                  isBuy
                    ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                    : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                )}
              >
                {isBuy ? "매수" : "매도"}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-500">주문가격</span>
              <span className="font-mono font-medium">
                {orderInfo.price.toLocaleString()}원
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-500">주문수량</span>
              <span className="font-mono font-medium">
                {orderInfo.quantity.toLocaleString()}주
              </span>
            </div>

            <div className="pt-2 border-t border-slate-200 dark:border-slate-700 flex items-center justify-between">
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                총 주문금액
              </span>
              <span className="text-lg font-bold text-slate-900 dark:text-white">
                {totalAmount.toLocaleString()}원
              </span>
            </div>
          </div>

          {/* Order ID (Success) */}
          {isSuccess && result.order_id && (
            <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs text-green-600 dark:text-green-400">
                    주문번호
                  </span>
                  <p className="font-mono text-sm font-medium text-green-700 dark:text-green-300">
                    {result.order_id}
                  </p>
                </div>
                <button
                  onClick={handleCopyOrderId}
                  className="p-2 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors"
                >
                  {copied ? (
                    <Check className="w-4 h-4 text-green-500" />
                  ) : (
                    <Copy className="w-4 h-4 text-green-500" />
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Error Message (Failure) */}
          {!isSuccess && result.message && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
              <span className="text-xs text-red-600 dark:text-red-400">
                오류 메시지
              </span>
              <p className="text-sm text-red-700 dark:text-red-300 mt-1">
                {result.message}
              </p>
            </div>
          )}

          {/* Note */}
          {isSuccess && (
            <p className="text-xs text-slate-400 text-center">
              주문 체결 여부는 미체결 목록에서 확인하세요
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 pb-6">
          <button
            onClick={onClose}
            className={cn(
              "w-full py-3 rounded-lg font-medium transition-colors",
              isSuccess
                ? "bg-green-500 text-white hover:bg-green-600"
                : "bg-slate-200 text-slate-700 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600"
            )}
          >
            확인
          </button>
        </div>
      </div>
    </div>
  );
}

export default OrderResultModal;
