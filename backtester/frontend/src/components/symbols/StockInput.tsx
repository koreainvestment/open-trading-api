"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { X, Search, Loader2, AlertTriangle } from "lucide-react";
import { searchSymbols, getSymbolByCode, getMasterStatus } from "@/lib/api/symbols";
import type { Symbol } from "@/types/symbols";

const STORAGE_KEY = "kis_backtest_stocks";

interface StockWithName {
  code: string;
  name: string;
}

interface StockInputProps {
  stocks: string[];
  onChange: (stocks: string[]) => void;
}

// 빠른 선택용 코드 목록 (이름은 마스터파일에서 조회)
const POPULAR_CODES = ["005930", "000660", "035720", "005380", "051910", "035420"];

export function StockInput({ stocks, onChange }: StockInputProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Symbol[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [highlightIndex, setHighlightIndex] = useState(-1);
  const [stockNames, setStockNames] = useState<Record<string, string>>({});
  const [popularStocks, setPopularStocks] = useState<StockWithName[]>([]);
  const [needsCollection, setNeedsCollection] = useState(false);

  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);
  const isInitialLoadRef = useRef(true);

  // 마스터파일에서 종목명 조회 (코드 → 이름)
  const resolveStockName = useCallback(async (code: string): Promise<string | null> => {
    try {
      const symbol = await getSymbolByCode(code);
      return symbol?.name ?? null;
    } catch {
      return null;
    }
  }, []);

  // 여러 종목 이름 일괄 조회
  const resolveMultipleNames = useCallback(async (codes: string[]) => {
    const resolved: Record<string, string> = {};
    // 순차 호출 (rate limit 준수)
    for (const code of codes) {
      const name = await resolveStockName(code);
      if (name) {
        resolved[code] = name;
      }
    }
    return resolved;
  }, [resolveStockName]);

  // 마스터파일 수집 여부 확인 (마운트 + 수집 완료 이벤트 시)
  useEffect(() => {
    const check = () =>
      getMasterStatus()
        .then((s) => setNeedsCollection(s.needs_update))
        .catch(() => {});
    check();
    window.addEventListener("symbols-collected", check);
    return () => window.removeEventListener("symbols-collected", check);
  }, []);

  // 빠른 선택 종목 로드 (마스터파일에서 개별 조회)
  useEffect(() => {
    let cancelled = false;
    async function loadPopular() {
      try {
        const resolved: StockWithName[] = [];
        for (const code of POPULAR_CODES) {
          if (cancelled) return;
          const name = await resolveStockName(code);
          if (name) resolved.push({ code, name });
        }
        if (!cancelled) setPopularStocks(resolved);
      } catch {
        // 마스터파일 미수집 시 빈 배열 유지
      }
    }
    loadPopular();
    return () => { cancelled = true; };
  }, [resolveStockName]);

  // Load saved stocks and names from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved) as StockWithName[];
        if (Array.isArray(parsed) && parsed.length > 0) {
          const codes = parsed.map((s) => s.code);
          const names = parsed.reduce((acc, s) => {
            // 코드와 이름이 같으면 이름 누락된 것 → 빈 문자열로 저장
            if (s.name && s.name !== s.code) {
              acc[s.code] = s.name;
            }
            return acc;
          }, {} as Record<string, string>);
          onChange(codes);
          setStockNames(names);

          // 이름이 누락된 종목은 마스터파일에서 조회
          const missingNameCodes = codes.filter((c) => !names[c]);
          if (missingNameCodes.length > 0) {
            resolveMultipleNames(missingNameCodes).then((resolved) => {
              if (Object.keys(resolved).length > 0) {
                setStockNames((prev) => ({ ...prev, ...resolved }));
              }
            });
          }
        }
      }
    } catch {
      // Ignore localStorage errors
    }
    // 초기 로드 완료 후 save effect 활성화
    requestAnimationFrame(() => {
      isInitialLoadRef.current = false;
    });
  }, []);

  // Save to localStorage when stocks change (초기 로드 시 skip)
  useEffect(() => {
    if (isInitialLoadRef.current) return;
    if (stocks.length > 0) {
      const stocksToSave: StockWithName[] = stocks.map((code) => ({
        code,
        name: stockNames[code] || "",
      }));
      localStorage.setItem(STORAGE_KEY, JSON.stringify(stocksToSave));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, [stocks, stockNames]);

  // Debounced search
  const doSearch = useCallback(async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([]);
      setIsOpen(false);
      return;
    }

    setIsLoading(true);
    try {
      const response = await searchSymbols(searchQuery, 8);
      setResults(response.items);
      setIsOpen(response.items.length > 0);
      setHighlightIndex(-1);
      if (response.items.length > 0) setNeedsCollection(false);
    } catch {
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      doSearch(query);
    }, 200);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [query, doSearch]);

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        listRef.current &&
        !listRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = useCallback(
    (symbol: Symbol) => {
      if (!stocks.includes(symbol.code)) {
        onChange([...stocks, symbol.code]);
        setStockNames((prev) => ({
          ...prev,
          [symbol.code]: symbol.name,
        }));
      }
      setQuery("");
      setResults([]);
      setIsOpen(false);
    },
    [stocks, onChange]
  );

  const addStockByCode = useCallback(
    async (code: string, name?: string) => {
      const trimmed = code.trim();
      if (trimmed.length === 6 && /^\d+$/.test(trimmed) && !stocks.includes(trimmed)) {
        onChange([...stocks, trimmed]);
        if (name) {
          setStockNames((prev) => ({
            ...prev,
            [trimmed]: name,
          }));
        } else {
          // 이름 없으면 마스터파일에서 조회
          const resolved = await resolveStockName(trimmed);
          if (resolved) {
            setStockNames((prev) => ({
              ...prev,
              [trimmed]: resolved,
            }));
          }
        }
        setQuery("");
      }
    },
    [stocks, onChange, resolveStockName]
  );

  const removeStock = useCallback(
    (code: string) => {
      onChange(stocks.filter((s) => s !== code));
      setStockNames((prev) => {
        const updated = { ...prev };
        delete updated[code];
        return updated;
      });
    },
    [stocks, onChange]
  );

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (isOpen && results.length > 0) {
      switch (e.key) {
        case "ArrowDown":
          e.preventDefault();
          setHighlightIndex((prev) => Math.min(prev + 1, results.length - 1));
          break;
        case "ArrowUp":
          e.preventDefault();
          setHighlightIndex((prev) => Math.max(prev - 1, 0));
          break;
        case "Enter":
          e.preventDefault();
          if (highlightIndex >= 0 && highlightIndex < results.length) {
            handleSelect(results[highlightIndex]);
          } else if (query.length === 6 && /^\d+$/.test(query)) {
            addStockByCode(query);
          }
          break;
        case "Escape":
          setIsOpen(false);
          break;
      }
    } else if (e.key === "Enter" && query.length === 6 && /^\d+$/.test(query)) {
      e.preventDefault();
      addStockByCode(query);
    }
  };

  const handlePaste = useCallback(
    (e: React.ClipboardEvent) => {
      e.preventDefault();
      const pastedText = e.clipboardData.getData("text");
      const codes = pastedText
        .split(/[,\s]+/)
        .filter((c) => c.trim().length === 6 && /^\d+$/.test(c.trim()))
        .map((c) => c.trim());
      const newCodes = codes.filter((c) => !stocks.includes(c));
      if (newCodes.length === 0) return;

      const uniqueCodes = [...new Set([...stocks, ...newCodes])];
      onChange(uniqueCodes);

      // 붙여넣기한 종목 이름 조회
      resolveMultipleNames(newCodes).then((resolved) => {
        if (Object.keys(resolved).length > 0) {
          setStockNames((prev) => ({ ...prev, ...resolved }));
        }
      });
    },
    [stocks, onChange, resolveMultipleNames]
  );

  const getStockName = (code: string): string => {
    return stockNames[code] || "";
  };

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
        종목 검색
      </label>

      {/* 마스터파일 미수집 안내 */}
      {needsCollection && (
        <div className="flex items-center gap-2 px-3 py-2 text-xs text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
          <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
          종목 데이터가 없습니다. 우측 상단 ⚙ 설정에서 마스터파일을 수집해 주세요.
        </div>
      )}

      {/* Search Input with Autocomplete */}
      <div className="relative">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            onPaste={handlePaste}
            onFocus={() => query && results.length > 0 && setIsOpen(true)}
            placeholder="종목명 또는 코드 검색 (예: 삼성전자, 005930)"
            className="w-full pl-10 pr-10 py-3 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900 focus:ring-2 focus:ring-primary focus:border-transparent"
          />
          {query && !isLoading && (
            <button
              onClick={() => {
                setQuery("");
                setResults([]);
                setIsOpen(false);
              }}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-0.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700"
            >
              <X className="w-4 h-4 text-slate-400" />
            </button>
          )}
          {isLoading && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              <Loader2 className="w-4 h-4 text-primary animate-spin" />
            </div>
          )}
        </div>

        {/* Dropdown Results */}
        {isOpen && results.length > 0 && (
          <div
            ref={listRef}
            className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto"
          >
            {results.map((symbol, index) => (
              <button
                key={symbol.code}
                onClick={() => handleSelect(symbol)}
                className={`w-full flex items-center justify-between px-3 py-2.5 text-left hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors ${
                  index === highlightIndex ? "bg-slate-100 dark:bg-slate-800" : ""
                } ${stocks.includes(symbol.code) ? "opacity-50" : ""}`}
                disabled={stocks.includes(symbol.code)}
              >
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm font-medium text-slate-700 dark:text-slate-300 w-16">
                    {symbol.code}
                  </span>
                  <span className="text-sm text-slate-900 dark:text-white">
                    {symbol.name}
                  </span>
                </div>
                <span
                  className={`text-xs px-1.5 py-0.5 rounded ${
                    symbol.exchange === "kospi"
                      ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                      : "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400"
                  }`}
                >
                  {symbol.exchange_name}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Selected Stocks */}
      {stocks.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {stocks.map((code) => {
            const name = getStockName(code);
            return (
              <span
                key={code}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 text-primary rounded-full text-sm"
              >
                <span className="font-mono font-medium">{code}</span>
                {name && <span className="text-primary/70">{name}</span>}
                <button
                  onClick={() => removeStock(code)}
                  className="ml-0.5 p-0.5 hover:bg-primary/20 rounded-full transition-colors"
                  aria-label={`${name || code} 제거`}
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </span>
            );
          })}
        </div>
      )}

      {/* Quick Select (마스터파일 기반) */}
      {popularStocks.length > 0 && (
        <div className="pt-2">
          <p className="text-xs text-slate-500 mb-2">빠른 선택</p>
          <div className="flex flex-wrap gap-2">
            {popularStocks.filter((s) => !stocks.includes(s.code)).map((stock) => (
              <button
                key={stock.code}
                onClick={() => addStockByCode(stock.code, stock.name)}
                className="px-3 py-1 text-sm border border-slate-200 dark:border-slate-700 rounded-full hover:border-primary hover:text-primary transition-colors"
              >
                {stock.name}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default StockInput;
