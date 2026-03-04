"use client";

import { useState, useCallback } from "react";
import { executeOrder } from "@/lib/api";
import type { OrderRequest, OrderResult } from "@/types/order";
import type { LogEntry } from "@/types/signal";

interface UseOrderResult {
  result: OrderResult | null;
  logs: LogEntry[];
  isLoading: boolean;
  error: string | null;
  execute: (request: OrderRequest) => Promise<OrderResult>;
  reset: () => void;
}

export function useOrder(): UseOrderResult {
  const [result, setResult] = useState<OrderResult | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(async (request: OrderRequest): Promise<OrderResult> => {
    setIsLoading(true);
    setError(null);
    setResult(null);
    setLogs([]);

    try {
      const response = await executeOrder(request);
      setLogs(response.logs);

      const orderResult: OrderResult = {
        status: response.status,
        order_id: response.data?.order_id,
        message: response.message,
      };

      setResult(orderResult);

      if (response.status !== "success") {
        setError(response.message);
      }

      return orderResult;
    } catch (err) {
      const message = err instanceof Error ? err.message : "주문 실행 오류";
      setError(message);
      
      const errorResult: OrderResult = {
        status: "error",
        message,
      };
      setResult(errorResult);
      return errorResult;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setLogs([]);
    setError(null);
  }, []);

  return {
    result,
    logs,
    isLoading,
    error,
    execute,
    reset,
  };
}

export default useOrder;
