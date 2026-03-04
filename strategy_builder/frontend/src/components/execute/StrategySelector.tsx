"use client";

import { useState } from "react";
import { ChevronDown, Check, Sparkles, TrendingUp, TrendingDown, Activity, FolderOpen } from "lucide-react";
import type { StrategyInfo, StrategyParam } from "@/types/signal";

interface StrategySelectorProps {
  strategies: StrategyInfo[];
  selectedStrategy: StrategyInfo | null;
  params: Record<string, number>;
  onSelect: (strategy: StrategyInfo | null) => void;
  onParamChange: (name: string, value: number) => void;
  isLoading?: boolean;
}

const CATEGORY_ICONS: Record<string, typeof TrendingUp> = {
  "추세추종": TrendingUp,
  "역추세": TrendingDown,
  "돌파매매": Activity,
  "모멘텀": Sparkles,
  "변동성": Activity,
  "패턴": Activity,
};

export function StrategySelector({
  strategies,
  selectedStrategy,
  params,
  onSelect,
  onParamChange,
  isLoading,
}: StrategySelectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  const handleSelect = (strategy: StrategyInfo) => {
    onSelect(strategy);
    setIsOpen(false);
  };

  // 로컬 전략과 백엔드 전략 분리
  const localStrategies = strategies.filter((s) => s.isLocal);
  const backendStrategies = strategies.filter((s) => !s.isLocal);

  // Group backend strategies by category
  const groupedStrategies = backendStrategies.reduce((acc, strategy) => {
    const category = strategy.category;
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(strategy);
    return acc;
  }, {} as Record<string, StrategyInfo[]>);

  return (
    <div className="space-y-4">
      {/* Strategy Dropdown */}
      <div className="relative">
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
          전략 선택
        </label>
        <button
          onClick={() => setIsOpen(!isOpen)}
          disabled={isLoading}
          className="w-full flex items-center justify-between px-4 py-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg hover:border-primary transition-colors focus-ring"
          aria-label="전략 선택"
          aria-expanded={isOpen}
        >
          <div className="flex items-center gap-3">
            {selectedStrategy ? (
              <>
                {selectedStrategy.isLocal ? (
                  <div className="w-8 h-8 rounded-lg bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                    <FolderOpen className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                    {(() => {
                      const Icon = CATEGORY_ICONS[selectedStrategy.category] || Activity;
                      return <Icon className="w-4 h-4 text-primary" />;
                    })()}
                  </div>
                )}
                <div className="text-left">
                  <p className="font-medium">{selectedStrategy.name.replace("📁 ", "")}</p>
                  <p className="text-xs text-slate-500">
                    {selectedStrategy.isLocal ? "내 전략" : selectedStrategy.category}
                  </p>
                </div>
              </>
            ) : (
              <span className="text-slate-400">전략을 선택하세요</span>
            )}
          </div>
          <ChevronDown className={`w-5 h-5 transition-transform ${isOpen ? "rotate-180" : ""}`} />
        </button>

        {isOpen && (
          <div className="absolute z-20 w-full mt-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg max-h-80 overflow-y-auto">
            {/* 기본 전략 섹션 */}
            {Object.entries(groupedStrategies).map(([category, categoryStrategies]) => (
              <div key={category}>
                <div className="px-4 py-2 bg-slate-50 dark:bg-slate-800 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  {category}
                </div>
                {categoryStrategies.map((strategy) => (
                  <button
                    key={strategy.id}
                    onClick={() => handleSelect(strategy)}
                    className="w-full flex items-center gap-3 px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                  >
                    <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                      {(() => {
                        const Icon = CATEGORY_ICONS[strategy.category] || Activity;
                        return <Icon className="w-4 h-4 text-primary" />;
                      })()}
                    </div>
                    <div className="flex-1 text-left">
                      <p className="font-medium">{strategy.name}</p>
                      <p className="text-xs text-slate-500 line-clamp-1">
                        {strategy.description}
                      </p>
                    </div>
                    {selectedStrategy?.id === strategy.id && (
                      <Check className="w-5 h-5 text-primary" />
                    )}
                  </button>
                ))}
              </div>
            ))}

            {/* 내 전략 섹션 (맨 아래) */}
            {localStrategies.length > 0 && (
              <div>
                <div className="px-4 py-2 bg-amber-50 dark:bg-amber-900/20 text-xs font-semibold text-amber-600 dark:text-amber-400 uppercase tracking-wider flex items-center gap-2">
                  <FolderOpen className="w-3.5 h-3.5" />
                  내 전략
                </div>
                {localStrategies.map((strategy) => (
                  <button
                    key={strategy.id}
                    onClick={() => handleSelect(strategy)}
                    className="w-full flex items-center gap-3 px-4 py-3 hover:bg-amber-50/50 dark:hover:bg-amber-900/10 transition-colors"
                  >
                    <div className="w-8 h-8 rounded-lg bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                      <FolderOpen className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                    </div>
                    <div className="flex-1 text-left">
                      <p className="font-medium">{strategy.name.replace("📁 ", "")}</p>
                      <p className="text-xs text-slate-500 line-clamp-1">
                        {strategy.description}
                      </p>
                    </div>
                    {selectedStrategy?.id === strategy.id && (
                      <Check className="w-5 h-5 text-amber-600" />
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Strategy Description */}
      {selectedStrategy && (
        <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
          <p className="text-sm text-slate-600 dark:text-slate-400">
            {selectedStrategy.description}
          </p>
        </div>
      )}

      {/* Parameters */}
      {selectedStrategy && selectedStrategy.params.length > 0 && (
        <div className="space-y-4">
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
            파라미터 설정
          </label>
          <div className="grid gap-4">
            {selectedStrategy.params.map((param) => (
              <ParamSlider
                key={param.name}
                param={param}
                value={params[param.name] ?? param.default}
                onChange={(value) => onParamChange(param.name, value)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

interface ParamSliderProps {
  param: StrategyParam;
  value: number;
  onChange: (value: number) => void;
}

function ParamSlider({ param, value, onChange }: ParamSliderProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm text-slate-600 dark:text-slate-400">{param.label}</span>
        <span className="text-sm font-mono font-medium tabular-nums">{value}</span>
      </div>
      <input
        type="range"
        min={param.min}
        max={param.max}
        step={param.step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-primary"
      />
      <div className="flex justify-between text-xs text-slate-400">
        <span>{param.min}</span>
        <span>{param.max}</span>
      </div>
    </div>
  );
}

export default StrategySelector;
