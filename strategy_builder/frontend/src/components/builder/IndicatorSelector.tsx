"use client";

import { useState, useMemo, useCallback } from "react";
import { Search, Plus, ChevronDown, ChevronRight, X, Settings2, Sparkles, Check, Lock, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { BuilderIndicator, IndicatorCategory, IndicatorDefinition } from "@/types/builder";
import { POPULAR_INDICATORS } from "@/types/builder";
import {
  CATEGORY_LABELS,
  CATEGORY_ORDER,
  getIndicatorsByCategory,
  searchIndicators,
  getIndicatorById,
} from "@/lib/builder/constants";

interface IndicatorSelectorProps {
  selectedIndicators: BuilderIndicator[];
  onAddIndicator: (indicator: BuilderIndicator) => void;
  onUpdateIndicator: (id: string, updates: Partial<BuilderIndicator>) => void;
  onRemoveIndicator: (id: string) => void;
  createIndicator: (indicatorId: string, alias?: string) => BuilderIndicator | null;
}

// 카테고리 아이콘
const CATEGORY_ICONS: Record<IndicatorCategory, string> = {
  moving_average: "📈",
  oscillator: "📊",
  trend: "📉",
  volume: "📦",
  volatility: "⚡",
  misc: "🔧",
  candlestick: "🕯️",
};

export function IndicatorSelector({
  selectedIndicators,
  onAddIndicator,
  onUpdateIndicator,
  onRemoveIndicator,
  createIndicator,
}: IndicatorSelectorProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedIndicator, setExpandedIndicator] = useState<string | null>(null);
  const [showAddPanel, setShowAddPanel] = useState(false);
  const [expandedCategories, setExpandedCategories] = useState<Set<IndicatorCategory>>(new Set(["moving_average"]));
  const [recentlyAdded, setRecentlyAdded] = useState<string | null>(null);
  // alias 편집 중인 로컬 값 (커밋 전 입력 중 상태)
  const [pendingAliases, setPendingAliases] = useState<Record<string, string>>({});

  // 이미 추가된 지표 ID 목록
  const addedIndicatorIds = useMemo(() => {
    return new Set(selectedIndicators.map(ind => ind.indicatorId));
  }, [selectedIndicators]);

  // 인기 지표 정의들
  const popularIndicatorDefs = useMemo(() => {
    return POPULAR_INDICATORS
      .map(id => getIndicatorById(id))
      .filter((def): def is IndicatorDefinition => def !== undefined);
  }, []);

  // Filtered indicators for search
  const filteredIndicators = useMemo(() => {
    if (searchQuery.trim()) {
      return searchIndicators(searchQuery);
    }
    return [];
  }, [searchQuery]);

  // Handle add indicator - 패널은 열어둔 채로 계속 추가 가능
  const handleAddIndicator = useCallback(
    (def: IndicatorDefinition) => {
      const newIndicator = createIndicator(def.id);
      if (newIndicator) {
        onAddIndicator(newIndicator);
        // 추가됨 피드백 표시
        setRecentlyAdded(def.id);
        setTimeout(() => setRecentlyAdded(null), 1500);
        // 패널은 닫지 않음 - 여러 개 연속 추가 가능
        setSearchQuery("");
      }
    },
    [createIndicator, onAddIndicator]
  );

  // Handle param change
  const handleParamChange = useCallback(
    (indicatorId: string, paramName: string, value: number | string) => {
      onUpdateIndicator(indicatorId, {
        params: {
          ...selectedIndicators.find((i) => i.id === indicatorId)?.params,
          [paramName]: value,
        },
      });
    },
    [onUpdateIndicator, selectedIndicators]
  );

  // Handle output change
  const handleOutputChange = useCallback(
    (indicatorId: string, output: string) => {
      onUpdateIndicator(indicatorId, { output });
    },
    [onUpdateIndicator]
  );

  // displayName 변경 핸들러 — alias(내부 key)는 건드리지 않음
  const handleDisplayNameChange = useCallback(
    (indicatorId: string, value: string) => {
      setPendingAliases((prev) => ({ ...prev, [indicatorId]: value }));
    },
    []
  );

  const handleDisplayNameBlur = useCallback(
    (indicatorId: string) => {
      const pending = pendingAliases[indicatorId];
      if (pending === undefined) return;
      onUpdateIndicator(indicatorId, { displayName: pending.trim() || undefined });
      setPendingAliases((prev) => {
        const { [indicatorId]: _, ...rest } = prev;
        return rest;
      });
    },
    [pendingAliases, onUpdateIndicator]
  );

  // Toggle category accordion
  const toggleCategory = useCallback((cat: IndicatorCategory) => {
    setExpandedCategories(prev => {
      const next = new Set(prev);
      if (next.has(cat)) {
        next.delete(cat);
      } else {
        next.add(cat);
      }
      return next;
    });
  }, []);

  return (
    <div className="space-y-4">
      {/* Selected Indicators - Show First */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
            사용 중인 지표
            {selectedIndicators.length > 0 && (
              <span className="ml-2 px-1.5 py-0.5 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded">
                {selectedIndicators.length}
              </span>
            )}
          </h4>
          <button
            onClick={() => setShowAddPanel(!showAddPanel)}
            className={cn(
              "flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-colors",
              showAddPanel
                ? "bg-blue-500 text-white"
                : "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 hover:bg-blue-100"
            )}
          >
            <Plus className="w-3.5 h-3.5" />
            지표 추가
          </button>
        </div>

        {/* Selected Indicators List */}
        {selectedIndicators.length > 0 ? (
          <div className="space-y-2">
            {selectedIndicators.map((ind) => {
              const def = getIndicatorById(ind.indicatorId);
              if (!def) return null;

              const isExpanded = expandedIndicator === ind.id;

              return (
                <div
                  key={ind.id}
                  className="border border-slate-200 dark:border-slate-700 rounded-lg overflow-hidden bg-white dark:bg-slate-800"
                >
                  {/* Header */}
                  <div
                    className="flex items-center justify-between px-3 py-2.5 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
                    onClick={() => setExpandedIndicator(isExpanded ? null : ind.id)}
                  >
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-700">
                        {isExpanded ? (
                          <ChevronDown className="w-4 h-4 text-slate-500" />
                        ) : (
                          <ChevronRight className="w-4 h-4 text-slate-500" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-sm text-slate-900 dark:text-white flex items-center gap-1.5">
                          {def.nameKo}
                          {def.leanUnsupported && (
                            <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 text-[10px] font-medium bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 rounded" title="Lean 백테스트 미지원 (p1 실행만 가능)">
                              <AlertTriangle className="w-3 h-3" />
                              백테스트 미지원
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-slate-500 flex items-center gap-2">
                          <span className="font-mono">{ind.alias}</span>
                          {Object.keys(ind.params).length > 0 && (
                            <span className="text-slate-400">
                              ({Object.entries(ind.params).map(([k, v]) => `${k}=${v}`).join(", ")})
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onRemoveIndicator(ind.id);
                      }}
                      className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors focus-ring"
                      aria-label={`${def.nameKo} 지표 삭제`}
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Expanded Content */}
                  {isExpanded && (
                    <div className="px-3 py-3 space-y-3 border-t border-slate-100 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/50">
                      {/* Display Name + internal alias badge */}
                      <div>
                        <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1.5">
                          표시 이름
                        </label>
                        <input
                          type="text"
                          value={pendingAliases[ind.id] ?? (ind.displayName ?? "")}
                          placeholder={ind.alias}
                          onChange={(e) => handleDisplayNameChange(ind.id, e.target.value)}
                          onBlur={() => handleDisplayNameBlur(ind.id)}
                          className="w-full px-3 py-2 text-sm border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                        <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">
                          내부 키: <span className="font-mono text-slate-500 dark:text-slate-400">{ind.alias}</span>
                        </p>
                      </div>


                      {/* Parameters */}
                      {def.params.length > 0 && (
                        <div>
                          <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1.5">
                            파라미터
                          </label>
                          <div className="grid grid-cols-2 gap-2">
                            {def.params.map((param) => (
                              <div key={param.name}>
                                <label className="block text-xs text-slate-500 mb-1">
                                  {param.name}
                                </label>
                                {param.type === "string" ? (
                                  // String 타입: select 또는 text input
                                  param.name === "direction" ? (
                                    <select
                                      value={ind.params[param.name] ?? param.default}
                                      onChange={(e) =>
                                        handleParamChange(ind.id, param.name, e.target.value)
                                      }
                                      className="w-full px-3 py-2 text-sm border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800"
                                    >
                                      <option value="up">up (상승)</option>
                                      <option value="down">down (하락)</option>
                                    </select>
                                  ) : (
                                    <input
                                      type="text"
                                      value={ind.params[param.name] ?? param.default}
                                      onChange={(e) =>
                                        handleParamChange(ind.id, param.name, e.target.value)
                                      }
                                      className="w-full px-3 py-2 text-sm border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800"
                                    />
                                  )
                                ) : (
                                  // Number 타입
                                  <input
                                    type="number"
                                    value={
                                      !isNaN(ind.params[param.name] as number) && ind.params[param.name] !== undefined
                                        ? (ind.params[param.name] as number)
                                        : (param.default as number)
                                    }
                                    onChange={(e) => {
                                      const v = parseFloat(e.target.value);
                                      if (!isNaN(v)) handleParamChange(ind.id, param.name, v);
                                    }}
                                    min={param.min}
                                    max={param.max}
                                    step={param.step ?? 1}
                                    className="w-full px-3 py-2 text-sm border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800"
                                  />
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Output Selection (for multi-output indicators) */}
                      {def.outputs.length > 1 && (
                        <div>
                          <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1.5">
                            출력값
                          </label>
                          <select
                            value={ind.output}
                            onChange={(e) => handleOutputChange(ind.id, e.target.value)}
                            className="w-full px-3 py-2 text-sm border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800"
                          >
                            {def.outputs.map((out) => (
                              <option key={out.id} value={out.id}>
                                {out.name}
                              </option>
                            ))}
                          </select>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-8 border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-lg">
            <Settings2 className="w-8 h-8 text-slate-300 dark:text-slate-600 mx-auto mb-2" />
            <p className="text-sm text-slate-500">추가된 지표가 없습니다</p>
            <p className="text-xs text-slate-400 mt-1">위 버튼을 눌러 지표를 추가하세요</p>
          </div>
        )}
      </div>

      {/* Add Indicator Panel */}
      {showAddPanel && (
        <div className="border border-blue-200 dark:border-blue-800 rounded-lg bg-blue-50/50 dark:bg-blue-900/10 p-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
              지표 선택
              <span className="ml-2 text-xs font-normal text-slate-500">여러 개 추가 가능</span>
            </h4>
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  setShowAddPanel(false);
                  setSearchQuery("");
                }}
                className="px-3 py-1 text-xs font-medium bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                완료
              </button>
              <button
                onClick={() => {
                  setShowAddPanel(false);
                  setSearchQuery("");
                }}
                className="p-1 text-slate-400 hover:text-slate-600"
                aria-label="지표 선택 패널 닫기"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Search */}
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="지표 검색..."
              className="w-full pl-10 pr-4 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              autoFocus
              aria-label="지표 검색"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Search Results */}
          {searchQuery.trim() && (
            <div className="space-y-1 max-h-48 overflow-y-auto mb-4">
              {filteredIndicators.slice(0, 20).map((def) => {
                const isAdded = addedIndicatorIds.has(def.id);
                const isJustAdded = recentlyAdded === def.id;
                const isUnimplemented = def.implemented === false;

                return (
                  <button
                    key={def.id}
                    onClick={() => !isUnimplemented && handleAddIndicator(def)}
                    disabled={isUnimplemented}
                    className={cn(
                      "w-full flex items-center gap-3 px-3 py-2 text-left rounded-lg border transition-all",
                      isUnimplemented
                        ? "bg-slate-50 dark:bg-slate-800/30 border-slate-200 dark:border-slate-700 opacity-50 cursor-not-allowed"
                        : isJustAdded
                        ? "bg-green-50 dark:bg-green-900/20 border-green-400"
                        : isAdded
                        ? "bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700"
                        : "bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 hover:border-blue-400 hover:bg-blue-50/50 dark:hover:bg-blue-900/20"
                    )}
                  >
                    {isUnimplemented ? (
                      <Lock className="w-4 h-4 text-slate-400 flex-shrink-0" />
                    ) : isJustAdded ? (
                      <Check className="w-4 h-4 text-green-500 flex-shrink-0" />
                    ) : (
                      <Plus className="w-4 h-4 text-blue-500 flex-shrink-0" />
                    )}
                    <div className="flex-1 min-w-0">
                      <div className={cn(
                        "font-medium text-sm",
                        isUnimplemented ? "text-slate-400 dark:text-slate-500" : isJustAdded ? "text-green-700 dark:text-green-400" : "text-slate-900 dark:text-white"
                      )}>
                        {def.nameKo}
                        {isJustAdded && <span className="ml-2 text-xs">추가됨!</span>}
                      </div>
                      <div className="text-xs text-slate-500">{def.name}</div>
                    </div>
                    {isUnimplemented ? (
                      <span className="text-xs text-slate-400">지원 예정</span>
                    ) : def.leanUnsupported ? (
                      <span className="flex items-center gap-1 text-xs text-amber-500" title="Lean 백테스트 미지원 (p1 실행만 가능)">
                        <AlertTriangle className="w-3 h-3" />
                        백테스트 미지원
                      </span>
                    ) : isAdded && !isJustAdded ? (
                      <span className="text-xs text-slate-400">+1 더 추가</span>
                    ) : null}
                  </button>
                );
              })}
              {filteredIndicators.length === 0 && (
                <p className="text-sm text-slate-500 text-center py-4">
                  검색 결과가 없습니다
                </p>
              )}
            </div>
          )}

          {/* Popular Indicators Grid (when not searching) */}
          {!searchQuery.trim() && (
            <>
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="w-4 h-4 text-amber-500" />
                  <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">인기 지표</span>
                  <span className="text-xs text-slate-400">(클릭하면 추가)</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {popularIndicatorDefs.map((def) => {
                    const isAdded = addedIndicatorIds.has(def.id);
                    const isJustAdded = recentlyAdded === def.id;

                    return (
                      <button
                        key={def.id}
                        onClick={() => handleAddIndicator(def)}
                        className={cn(
                          "flex flex-col items-center justify-center gap-1 p-3 rounded-lg border transition-all group relative",
                          isJustAdded
                            ? "bg-green-50 dark:bg-green-900/20 border-green-400"
                            : isAdded
                            ? "bg-blue-50/50 dark:bg-blue-900/10 border-blue-200 dark:border-blue-800"
                            : "bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 hover:border-blue-400 hover:bg-blue-50/50 dark:hover:bg-blue-900/20"
                        )}
                      >
                        {isJustAdded && (
                          <span className="absolute -top-1 -right-1 w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                            <Check className="w-3 h-3 text-white" />
                          </span>
                        )}
                        {isAdded && !isJustAdded && (
                          <span className="absolute -top-1 -right-1 w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center text-[10px] text-white font-bold">
                            {selectedIndicators.filter(i => i.indicatorId === def.id).length}
                          </span>
                        )}
                        <span className={cn(
                          "text-sm font-medium group-hover:text-blue-600",
                          isJustAdded ? "text-green-700 dark:text-green-400" : "text-slate-900 dark:text-white"
                        )}>
                          {def.nameKo}
                        </span>
                        <span className="text-xs text-slate-400">{def.name}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Category Accordion */}
              <div className="space-y-1 max-h-64 overflow-y-auto">
                {CATEGORY_ORDER.map((cat) => {
                  const categoryIndicators = getIndicatorsByCategory(cat);
                  const isExpanded = expandedCategories.has(cat);

                  return (
                    <div key={cat} className="border border-slate-200 dark:border-slate-700 rounded-lg overflow-hidden">
                      <button
                        onClick={() => toggleCategory(cat)}
                        className="w-full flex items-center justify-between px-3 py-2.5 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
                      >
                        <div className="flex items-center gap-2">
                          <span>{CATEGORY_ICONS[cat]}</span>
                          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                            {CATEGORY_LABELS[cat]}
                          </span>
                          <span className="px-1.5 py-0.5 text-xs bg-slate-100 dark:bg-slate-700 text-slate-500 rounded">
                            {categoryIndicators.length}
                          </span>
                        </div>
                        {isExpanded ? (
                          <ChevronDown className="w-4 h-4 text-slate-400" />
                        ) : (
                          <ChevronRight className="w-4 h-4 text-slate-400" />
                        )}
                      </button>

                      {isExpanded && (
                        <div className="p-2 bg-slate-50 dark:bg-slate-900/50 space-y-1 max-h-40 overflow-y-auto">
                          {categoryIndicators.map((def) => {
                            const isAdded = addedIndicatorIds.has(def.id);
                            const isJustAdded = recentlyAdded === def.id;
                            const count = selectedIndicators.filter(i => i.indicatorId === def.id).length;
                            const isUnimplemented = def.implemented === false;

                            return (
                              <button
                                key={def.id}
                                onClick={() => !isUnimplemented && handleAddIndicator(def)}
                                disabled={isUnimplemented}
                                className={cn(
                                  "w-full flex items-center gap-2 px-2 py-1.5 text-left rounded transition-colors",
                                  isUnimplemented
                                    ? "opacity-50 cursor-not-allowed"
                                    : isJustAdded
                                    ? "bg-green-100 dark:bg-green-900/30"
                                    : "hover:bg-white dark:hover:bg-slate-800"
                                )}
                              >
                                {isUnimplemented ? (
                                  <Lock className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                                ) : isJustAdded ? (
                                  <Check className="w-3.5 h-3.5 text-green-500 flex-shrink-0" />
                                ) : (
                                  <Plus className="w-3.5 h-3.5 text-blue-500 flex-shrink-0" />
                                )}
                                <span className={cn(
                                  "text-sm",
                                  isUnimplemented ? "text-slate-400 dark:text-slate-500" : isJustAdded ? "text-green-700 dark:text-green-400 font-medium" : "text-slate-700 dark:text-slate-300"
                                )}>
                                  {def.nameKo}
                                </span>
                                {isUnimplemented ? (
                                  <span className="text-[10px] text-slate-400 ml-auto">지원 예정</span>
                                ) : def.leanUnsupported ? (
                                  <span className="flex items-center gap-0.5 text-[10px] text-amber-500 ml-auto" title="Lean 백테스트 미지원">
                                    <AlertTriangle className="w-3 h-3" />
                                  </span>
                                ) : isAdded && !isJustAdded ? (
                                  <span className="px-1.5 py-0.5 text-[10px] bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded">
                                    {count}개
                                  </span>
                                ) : null}
                                {!isUnimplemented && (
                                  <span className="text-xs text-slate-400 ml-auto">{def.name}</span>
                                )}
                              </button>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
