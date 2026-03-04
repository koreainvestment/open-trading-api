"use client";

import { useCallback } from "react";
import { Shield, TrendingDown, TrendingUp, Activity } from "lucide-react";
import { cn } from "@/lib/utils";
import type { RiskManagement } from "@/types/builder";

interface RiskManagerProps {
  risk: RiskManagement;
  onChange: (updates: Partial<RiskManagement>) => void;
}

export function RiskManager({ risk, onChange }: RiskManagerProps) {
  const handleStopLossToggle = useCallback(() => {
    onChange({
      stopLoss: {
        ...risk.stopLoss,
        enabled: !risk.stopLoss.enabled,
      },
    });
  }, [onChange, risk.stopLoss]);

  const handleStopLossChange = useCallback(
    (percent: number) => {
      onChange({
        stopLoss: {
          ...risk.stopLoss,
          percent,
        },
      });
    },
    [onChange, risk.stopLoss]
  );

  const handleTakeProfitToggle = useCallback(() => {
    onChange({
      takeProfit: {
        ...risk.takeProfit,
        enabled: !risk.takeProfit.enabled,
      },
    });
  }, [onChange, risk.takeProfit]);

  const handleTakeProfitChange = useCallback(
    (percent: number) => {
      onChange({
        takeProfit: {
          ...risk.takeProfit,
          percent,
        },
      });
    },
    [onChange, risk.takeProfit]
  );

  const handleTrailingStopToggle = useCallback(() => {
    onChange({
      trailingStop: {
        ...risk.trailingStop,
        enabled: !risk.trailingStop.enabled,
      },
    });
  }, [onChange, risk.trailingStop]);

  const handleTrailingStopChange = useCallback(
    (percent: number) => {
      onChange({
        trailingStop: {
          ...risk.trailingStop,
          percent,
        },
      });
    },
    [onChange, risk.trailingStop]
  );

  return (
    <div className="space-y-4">
      <RiskItem
        id="stop-loss"
        icon={<TrendingDown className="w-4 h-4" />}
        title="손절 (Stop Loss)"
        description="손실이 설정값에 도달하면 자동 청산"
        enabled={risk.stopLoss.enabled}
        percent={risk.stopLoss.percent}
        onToggle={handleStopLossToggle}
        onChange={handleStopLossChange}
        color="red"
      />

      <RiskItem
        id="take-profit"
        icon={<TrendingUp className="w-4 h-4" />}
        title="익절 (Take Profit)"
        description="수익이 설정값에 도달하면 자동 청산"
        enabled={risk.takeProfit.enabled}
        percent={risk.takeProfit.percent}
        onToggle={handleTakeProfitToggle}
        onChange={handleTakeProfitChange}
        color="green"
      />

      <RiskItem
        id="trailing-stop"
        icon={<Activity className="w-4 h-4" />}
        title="트레일링 스탑"
        description="고점 대비 설정값 하락 시 자동 청산"
        enabled={risk.trailingStop.enabled}
        percent={risk.trailingStop.percent}
        onToggle={handleTrailingStopToggle}
        onChange={handleTrailingStopChange}
        color="blue"
      />

      {/* Info */}
      <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
        <div className="flex items-start gap-2">
          <Shield className="w-4 h-4 text-slate-400 mt-0.5" aria-hidden="true" />
          <div className="text-xs text-slate-500">
            <p>리스크 관리 설정은 백테스트 시 적용됩니다.</p>
            <p className="mt-1">손절/익절은 진입가 대비 %, 트레일링 스탑은 최고점 대비 %입니다.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// Risk Item Component - Semantic HTML
// ============================================================

interface RiskItemProps {
  id: string;
  icon: React.ReactNode;
  title: string;
  description: string;
  enabled: boolean;
  percent: number;
  onToggle: () => void;
  onChange: (percent: number) => void;
  color: "red" | "green" | "blue";
}

function RiskItem({
  id,
  icon,
  title,
  description,
  enabled,
  percent,
  onToggle,
  onChange,
  color,
}: RiskItemProps) {
  const colorClasses = {
    red: {
      bg: "bg-red-50 dark:bg-red-900/20",
      border: "border-red-200 dark:border-red-800",
      icon: "text-red-500",
      toggle: "toggle-red",
      range: "range-red",
    },
    green: {
      bg: "bg-green-50 dark:bg-green-900/20",
      border: "border-green-200 dark:border-green-800",
      icon: "text-green-500",
      toggle: "toggle-green",
      range: "range-green",
    },
    blue: {
      bg: "bg-blue-50 dark:bg-blue-900/20",
      border: "border-blue-200 dark:border-blue-800",
      icon: "text-blue-500",
      toggle: "toggle-blue",
      range: "range-blue",
    },
  };

  const toggleId = `toggle-${id}`;
  const sliderId = `slider-${id}`;
  const numberId = `number-${id}`;

  return (
    <div
      className={cn(
        "p-3 rounded-lg border transition-colors",
        enabled ? colorClasses[color].bg : "bg-slate-50 dark:bg-slate-800/50",
        enabled ? colorClasses[color].border : "border-slate-200 dark:border-slate-700"
      )}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className={cn(enabled ? colorClasses[color].icon : "text-slate-400")} aria-hidden="true">
            {icon}
          </span>
          <label
            htmlFor={toggleId}
            className="font-medium text-sm text-slate-900 dark:text-white cursor-pointer"
          >
            {title}
          </label>
        </div>
        {/* Semantic toggle: checkbox with CSS styling */}
        <input
          type="checkbox"
          id={toggleId}
          checked={enabled}
          onChange={onToggle}
          className={cn("toggle-switch", colorClasses[color].toggle)}
          aria-label={`${title} ${enabled ? "활성화됨" : "비활성화됨"}`}
          role="switch"
          aria-checked={enabled}
        />
      </div>

      <p className="text-xs text-slate-500 mb-2">{description}</p>

      {enabled && (
        <div className="flex items-center gap-2">
          <label htmlFor={sliderId} className="sr-only">{title} 퍼센트 슬라이더</label>
          <input
            id={sliderId}
            type="range"
            min={1}
            max={50}
            step={0.5}
            value={percent}
            onChange={(e) => onChange(parseFloat(e.target.value))}
            className={cn("flex-1", colorClasses[color].range)}
            aria-valuemin={1}
            aria-valuemax={50}
            aria-valuenow={percent}
            aria-label={`${title} 퍼센트`}
          />
          <div className="flex items-center gap-1">
            <label htmlFor={numberId} className="sr-only">{title} 퍼센트 입력</label>
            <input
              id={numberId}
              type="number"
              min={0.1}
              max={100}
              step={0.1}
              value={percent}
              onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
              className="w-16 px-2 py-1 text-sm text-center border border-slate-200 dark:border-slate-700 rounded bg-white dark:bg-slate-800 focus-ring"
              aria-label={`${title} 퍼센트 값`}
            />
            <span className="text-sm text-slate-500" aria-hidden="true">%</span>
          </div>
        </div>
      )}
    </div>
  );
}
