"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Loader2, RefreshCw, Wifi, WifiOff } from "lucide-react";
import { getOrderbook, type OrderbookData } from "@/lib/api/market";
import { cn } from "@/lib/utils";

interface OrderbookPanelProps {
  stockCode: string;
  stockName?: string;
  onPriceSelect?: (price: number) => void;
  className?: string;
  /** Enable WebSocket real-time updates */
  realtime?: boolean;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

export function OrderbookPanel({
  stockCode,
  stockName,
  onPriceSelect,
  className,
  realtime = true,
}: OrderbookPanelProps) {
  const [orderbook, setOrderbook] = useState<OrderbookData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef(true);

  // Fetch orderbook via REST API
  const fetchOrderbook = useCallback(async () => {
    if (!stockCode) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await getOrderbook(stockCode);
      // Don't update state if unmounted during async operation
      if (!isMountedRef.current) return;

      if (response.status === "success" && response.data) {
        setOrderbook(response.data);
      } else {
        setError(response.message || "호가 조회 실패");
      }
    } catch (err) {
      if (!isMountedRef.current) return;
      setError(err instanceof Error ? err.message : "호가 조회 오류");
    } finally {
      if (isMountedRef.current) {
        setIsLoading(false);
      }
    }
  }, [stockCode]);

  // WebSocket connection for real-time updates
  const connectWebSocket = useCallback(() => {
    // Don't connect if unmounted
    if (!isMountedRef.current) return;
    if (!realtime || !stockCode) return;

    // Clean up existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    try {
      const wsUrl = `${API_BASE.replace("http", "ws")}/api/market/ws/${stockCode}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        if (!isMountedRef.current) return;
        setIsConnected(true);
        setError(null);
      };

      ws.onmessage = (event) => {
        if (!isMountedRef.current) return;
        try {
          const data = JSON.parse(event.data);
          if (data.type === "orderbook" && data.data) {
            setOrderbook(data.data);
          }
        } catch {
          // Ignore parse errors
        }
      };

      ws.onerror = () => {
        if (!isMountedRef.current) return;
        setIsConnected(false);
        // Fall back to REST API
        fetchOrderbook();
      };

      ws.onclose = () => {
        if (!isMountedRef.current) return;
        setIsConnected(false);
        // Only reconnect if still mounted and realtime is enabled
        if (realtime) {
          reconnectTimeoutRef.current = setTimeout(() => {
            if (isMountedRef.current) {
              connectWebSocket();
            }
          }, 5000);
        }
      };

      wsRef.current = ws;
    } catch {
      // WebSocket not supported, use REST API
      setIsConnected(false);
      fetchOrderbook();
    }
  }, [stockCode, realtime, fetchOrderbook]);

  // Initial fetch and WebSocket setup
  useEffect(() => {
    // Mark as mounted
    isMountedRef.current = true;

    fetchOrderbook();

    if (realtime) {
      connectWebSocket();
    }

    return () => {
      // Mark as unmounted to prevent reconnection attempts
      isMountedRef.current = false;

      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [stockCode, realtime, fetchOrderbook, connectWebSocket]);

  const handlePriceClick = (price: number) => {
    onPriceSelect?.(price);
  };

  // Calculate max volume for bar sizing
  const maxVolume = orderbook
    ? Math.max(
        ...(orderbook.ask_volumes || []),
        ...(orderbook.bid_volumes || []),
        1
      )
    : 1;

  if (isLoading && !orderbook) {
    return (
      <div className={cn("flex items-center justify-center py-8", className)}>
        <Loader2 className="w-6 h-6 animate-spin text-primary" />
      </div>
    );
  }

  if (error && !orderbook) {
    return (
      <div className={cn("text-center py-8", className)}>
        <p className="text-sm text-red-500">{error}</p>
        <button
          onClick={fetchOrderbook}
          className="mt-2 text-sm text-primary hover:underline"
        >
          다시 시도
        </button>
      </div>
    );
  }

  if (!orderbook) return null;

  return (
    <div className={cn("", className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
            호가창
          </span>
          {realtime && (
            <span
              className={cn(
                "flex items-center gap-1 text-xs",
                isConnected ? "text-green-500" : "text-slate-400"
              )}
            >
              {isConnected ? (
                <>
                  <Wifi className="w-3 h-3" />
                  <span>실시간</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-3 h-3" />
                  <span>연결 끊김</span>
                </>
              )}
            </span>
          )}
        </div>
        <button
          onClick={fetchOrderbook}
          className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-800"
        >
          <RefreshCw className="w-4 h-4 text-slate-400" />
        </button>
      </div>

      {/* Orderbook Table */}
      <div className="border border-slate-200 dark:border-slate-700 rounded-lg overflow-hidden">
        {/* Ask (Sell) Orders - Red */}
        <div className="divide-y divide-slate-100 dark:divide-slate-800">
          {(orderbook.ask_prices || []).slice().reverse().map((price, idx) => {
            const askVolumes = orderbook.ask_volumes || [];
            const volume = askVolumes[askVolumes.length - 1 - idx] || 0;
            const barWidth = (volume / maxVolume) * 100;

            return (
              <button
                key={`ask-${idx}`}
                onClick={() => handlePriceClick(price)}
                className="w-full flex items-center relative hover:bg-red-50 dark:hover:bg-red-900/10 transition-colors"
              >
                {/* Volume Bar (Background) */}
                <div
                  className="absolute right-0 top-0 bottom-0 bg-red-100 dark:bg-red-900/20"
                  style={{ width: `${barWidth}%` }}
                />
                {/* Content */}
                <div className="relative z-10 flex items-center justify-between w-full px-3 py-1.5">
                  <span className="text-xs text-slate-500 font-mono tabular-nums">
                    {volume?.toLocaleString() ?? "-"}
                  </span>
                  <span className="text-sm font-mono tabular-nums text-red-500 font-medium">
                    {price?.toLocaleString() ?? "-"}
                  </span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Current Price Divider */}
        <div className="bg-slate-100 dark:bg-slate-800 px-3 py-2 flex items-center justify-between">
          <span className="text-xs text-slate-500">현재가</span>
          <span className="font-mono font-bold text-sm">
            {orderbook.current_price?.toLocaleString() ?? "-"}원
          </span>
        </div>

        {/* Bid (Buy) Orders - Blue */}
        <div className="divide-y divide-slate-100 dark:divide-slate-800">
          {(orderbook.bid_prices || []).map((price, idx) => {
            const volume = (orderbook.bid_volumes || [])[idx] || 0;
            const barWidth = (volume / maxVolume) * 100;

            return (
              <button
                key={`bid-${idx}`}
                onClick={() => handlePriceClick(price)}
                className="w-full flex items-center relative hover:bg-blue-50 dark:hover:bg-blue-900/10 transition-colors"
              >
                {/* Volume Bar (Background) */}
                <div
                  className="absolute left-0 top-0 bottom-0 bg-blue-100 dark:bg-blue-900/20"
                  style={{ width: `${barWidth}%` }}
                />
                {/* Content */}
                <div className="relative z-10 flex items-center justify-between w-full px-3 py-1.5">
                  <span className="text-sm font-mono tabular-nums text-blue-500 font-medium">
                    {price?.toLocaleString() ?? "-"}
                  </span>
                  <span className="text-xs text-slate-500 font-mono tabular-nums">
                    {volume?.toLocaleString() ?? "-"}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Summary */}
      <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
        <div className="flex items-center gap-1">
          <span className="w-2 h-2 bg-red-400 rounded-full" />
          <span>매도 {orderbook.total_ask_volume?.toLocaleString() ?? "-"}</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-2 h-2 bg-blue-400 rounded-full" />
          <span>매수 {orderbook.total_bid_volume?.toLocaleString() ?? "-"}</span>
        </div>
      </div>
    </div>
  );
}

export default OrderbookPanel;
