"use client";

import { X } from "lucide-react";
import type { Symbol } from "@/types/symbols";

interface SymbolBarProps {
  symbol: Symbol | null;
  onClear?: () => void;
  showClear?: boolean;
  className?: string;
}

export function SymbolBar({
  symbol,
  onClear,
  showClear = true,
  className = "",
}: SymbolBarProps) {
  if (!symbol) {
    return (
      <div className={`flex items-center px-3 py-2 bg-slate-100 dark:bg-slate-800 rounded-lg text-sm text-slate-500 dark:text-slate-400 ${className}`}>
        종목을 선택해주세요
      </div>
    );
  }

  const exchangeColor = symbol.exchange === "kospi"
    ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
    : "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400";

  return (
    <div className={`flex items-center justify-between px-3 py-2 bg-slate-100 dark:bg-slate-800 rounded-lg ${className}`}>
      <div className="flex items-center gap-2">
        <span className={`text-xs px-1.5 py-0.5 rounded ${exchangeColor}`}>
          {symbol.exchange_name}
        </span>
        <span className="font-mono text-sm font-medium text-slate-700 dark:text-slate-300">
          {symbol.code}
        </span>
        <span className="text-sm text-slate-600 dark:text-slate-400">
          {symbol.name}
        </span>
      </div>
      {showClear && onClear && (
        <button
          onClick={onClear}
          className="p-1 rounded hover:bg-slate-200 dark:hover:bg-slate-700"
        >
          <X className="w-4 h-4 text-slate-400" />
        </button>
      )}
    </div>
  );
}

export default SymbolBar;
