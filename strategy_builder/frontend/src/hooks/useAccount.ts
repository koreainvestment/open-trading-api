"use client";

import { useState, useCallback, useRef } from "react";
import { getAccountInfo, getHoldings, getBalance } from "@/lib/api";
import type { AccountInfo, Holding, Balance } from "@/types/account";

// Minimum interval between API calls (in milliseconds)
const MIN_FETCH_INTERVAL = 5000; // 5 seconds

interface UseAccountResult {
  info: AccountInfo | null;
  holdings: Holding[];
  balance: Balance | null;
  isLoading: boolean;
  error: string | null;
  fetchInfo: () => Promise<void>;
  fetchHoldings: () => Promise<void>;
  fetchBalance: () => Promise<void>;
  refresh: () => Promise<void>;
  resetThrottle: () => void;
}

export function useAccount(): UseAccountResult {
  const [info, setInfo] = useState<AccountInfo | null>(null);
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [balance, setBalance] = useState<Balance | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Track last fetch times to prevent excessive API calls
  const lastFetchTimes = useRef({
    info: 0,
    holdings: 0,
    balance: 0,
  });

  const fetchInfo = useCallback(async () => {
    const now = Date.now();
    if (now - lastFetchTimes.current.info < MIN_FETCH_INTERVAL) {
      return; // Skip if called too recently
    }

    setIsLoading(true);
    // Don't clear error here - preserve previous state

    try {
      const response = await getAccountInfo();
      if (response.status === "success" && response.data) {
        setInfo(response.data);
        setError(null); // Only clear error on success
        lastFetchTimes.current.info = now;
      } else {
        // Set error but DON'T clear existing data
        setError(response.message || "계좌 정보 조회 실패");
      }
    } catch (err) {
      // Set error but DON'T clear existing data
      const message = err instanceof Error ? err.message : "계좌 정보 조회 오류";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchHoldings = useCallback(async () => {
    const now = Date.now();
    if (now - lastFetchTimes.current.holdings < MIN_FETCH_INTERVAL) {
      return; // Skip if called too recently
    }

    setIsLoading(true);

    try {
      const response = await getHoldings();
      if (response.status === "success") {
        setHoldings(response.data || []);
        setError(null);
        lastFetchTimes.current.holdings = now;
      } else {
        // Set error but DON'T clear existing holdings
        setError(response.message || "보유 종목 조회 실패");
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "보유 종목 조회 오류";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchBalance = useCallback(async () => {
    const now = Date.now();
    if (now - lastFetchTimes.current.balance < MIN_FETCH_INTERVAL) {
      return; // Skip if called too recently
    }

    setIsLoading(true);

    try {
      const response = await getBalance();
      if (response.status === "success" && response.data) {
        setBalance(response.data);
        setError(null);
        lastFetchTimes.current.balance = now;
      } else {
        // Set error but DON'T clear existing balance
        setError(response.message || "예수금 조회 실패");
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "예수금 조회 오류";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const resetThrottle = useCallback(() => {
    lastFetchTimes.current = { info: 0, holdings: 0, balance: 0 };
  }, []);

  const refresh = useCallback(async () => {
    resetThrottle();

    setIsLoading(true);
    setError(null);

    try {
      await fetchInfo();
      await fetchHoldings();
      await fetchBalance();
    } catch (err) {
      const message = err instanceof Error ? err.message : "조회 오류";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [resetThrottle, fetchInfo, fetchHoldings, fetchBalance]);

  return {
    info,
    holdings,
    balance,
    isLoading,
    error,
    fetchInfo,
    fetchHoldings,
    fetchBalance,
    refresh,
    resetThrottle,
  };
}

export default useAccount;
