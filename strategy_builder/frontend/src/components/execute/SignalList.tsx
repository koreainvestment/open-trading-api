"use client";

import { ArrowUp, ArrowDown, Minus, AlertCircle } from "lucide-react";
import type { SignalResult, SignalAction } from "@/types/signal";

interface SignalListProps {
  signals: SignalResult[];
  onSelect?: (signal: SignalResult) => void;
  selectedCode?: string;
}

// Korean stock convention: BUY(상승)=빨강, SELL(하락)=파랑
const ACTION_STYLES: Record<SignalAction, { bg: string; text: string; icon: typeof ArrowUp }> = {
  BUY: {
    bg: "bg-red-100 dark:bg-red-900/30",
    text: "text-red-600 dark:text-red-400",
    icon: ArrowUp,
  },
  SELL: {
    bg: "bg-blue-100 dark:bg-blue-900/30",
    text: "text-blue-600 dark:text-blue-400",
    icon: ArrowDown,
  },
  HOLD: {
    bg: "bg-slate-100 dark:bg-slate-800",
    text: "text-slate-600 dark:text-slate-400",
    icon: Minus,
  },
  ERROR: {
    bg: "bg-orange-100 dark:bg-orange-900/30",
    text: "text-orange-700 dark:text-orange-400",
    icon: AlertCircle,
  },
};

const ACTION_LABELS: Record<SignalAction, string> = {
  BUY: "매수",
  SELL: "매도",
  HOLD: "관망",
  ERROR: "오류",
};

export function SignalList({ signals, onSelect, selectedCode }: SignalListProps) {
  if (signals.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-slate-400">
        <Activity className="w-12 h-12 mb-3 opacity-30" />
        <p>시그널 결과가 없습니다</p>
        <p className="text-sm">전략을 실행하면 결과가 여기에 표시됩니다</p>
      </div>
    );
  }

  // Sort: BUY first, then SELL, then others
  const sortedSignals = [...signals].sort((a, b) => {
    const order: Record<SignalAction, number> = { BUY: 0, SELL: 1, HOLD: 2, ERROR: 3 };
    return (order[a.action] ?? 4) - (order[b.action] ?? 4);
  });

  return (
    <div className="space-y-2">
      {sortedSignals.map((signal) => {
        const style = ACTION_STYLES[signal.action];
        const Icon = style.icon;
        const isSelected = selectedCode === signal.code;

        return (
          <button
            key={signal.code}
            onClick={() => onSelect?.(signal)}
            className={`w-full flex items-center gap-4 p-4 rounded-lg border transition-all focus-ring ${
              isSelected
                ? "border-primary bg-primary/5"
                : "border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600"
            }`}
            aria-label={`${signal.name} ${ACTION_LABELS[signal.action]} 시그널`}
          >
            {/* Action Badge */}
            <div className={`flex items-center gap-1 px-3 py-1.5 rounded-full ${style.bg}`}>
              <Icon className={`w-4 h-4 ${style.text}`} />
              <span className={`text-sm font-semibold ${style.text}`}>
                {ACTION_LABELS[signal.action]}
              </span>
            </div>

            {/* Stock Info */}
            <div className="flex-1 text-left">
              <div className="flex items-center gap-2">
                <span className="font-medium">{signal.name}</span>
                <span className="text-xs text-slate-400 font-mono">{signal.code}</span>
              </div>
              <p className="text-sm text-slate-500 line-clamp-1">{signal.reason}</p>
            </div>

            {/* Strength - 임시 비활성화 */}
            {/* <div className="text-right">
              <StrengthBar strength={signal.strength} action={signal.action} />
            </div> */}
          </button>
        );
      })}
    </div>
  );
}

interface StrengthBarProps {
  strength: number;
  action: SignalAction;
}

function StrengthBar({ strength, action }: StrengthBarProps) {
  const percentage = Math.round(strength * 100);
  const style = ACTION_STYLES[action];

  return (
    <div className="w-20">
      <div className="flex items-center justify-end gap-1 mb-1">
        <span className={`text-sm font-medium ${style.text}`}>{percentage}%</span>
      </div>
      <div className="h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${
            action === "BUY"
              ? "bg-red-500"
              : action === "SELL"
              ? "bg-blue-500"
              : "bg-slate-400"
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

function Activity({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
    </svg>
  );
}

export default SignalList;
