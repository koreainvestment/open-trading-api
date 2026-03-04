"use client";

import { useState, useCallback, useMemo, useEffect } from "react";
import { Plus, Trash2, AlertCircle, GripVertical, Sparkles, ChevronDown, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import type {
  BuilderIndicator,
  BuilderCondition,
  BuilderConditionGroup,
  ConditionOperand,
  ConditionOperator,
  ConditionTemplate,
  CandlestickTemplate,
  CandlestickSignal,
} from "@/types/builder";
import {
  OPERATOR_OPTIONS,
  OPERATOR_SENTENCE_LABELS,
  CROSS_OPERATORS,
  CONDITION_TEMPLATES,
  CANDLESTICK_TEMPLATES,
  CANDLESTICK_SIGNAL_LABELS,
  CANDLESTICK_SIGNAL_OPTIONS,
} from "@/types/builder";
import { CANDLESTICK_PATTERNS } from "@/lib/builder/constants";
import { PRICE_FIELDS, getIndicatorById } from "@/lib/builder/constants";

interface ConditionBuilderProps {
  title: string;
  conditionGroup: BuilderConditionGroup;
  indicators: BuilderIndicator[];
  onAddCondition: (condition: BuilderCondition) => void;
  onAddIndicator: (indicator: BuilderIndicator) => void;
  createIndicator: (indicatorId: string, alias?: string) => BuilderIndicator | null;
  onUpdateCondition: (id: string, updates: Partial<BuilderCondition>) => void;
  onRemoveCondition: (id: string) => void;
  onReorderConditions: (conditions: BuilderCondition[]) => void;
  onSetLogic: (logic: "AND" | "OR") => void;
}

const TEMPLATE_CATEGORY_LABELS: Record<string, string> = {
  oscillator: "오실레이터",
  crossover: "이동평균 교차",
  band: "밴드 전략",
  trend: "추세",
};

const CANDLE_CATEGORY_LABELS: Record<string, string> = {
  reversal: "반전 패턴",
  single: "단일 캔들",
  double: "이중 캔들",
  triple: "삼중 캔들",
};

export function ConditionBuilder({
  title,
  conditionGroup,
  indicators,
  onAddCondition,
  onAddIndicator,
  createIndicator,
  onUpdateCondition,
  onRemoveCondition,
  onReorderConditions,
  onSetLogic,
}: ConditionBuilderProps) {
  const [showTemplates, setShowTemplates] = useState(false);
  const [showCandlestickTemplates, setShowCandlestickTemplates] = useState(false);
  const [expandedTemplateCategory, setExpandedTemplateCategory] = useState<string | null>("oscillator");
  const [expandedCandleCategory, setExpandedCandleCategory] = useState<string | null>("reversal");
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);

  const templatesByCategory = useMemo(() => {
    const grouped: Record<string, ConditionTemplate[]> = {};
    CONDITION_TEMPLATES.forEach(t => {
      if (!grouped[t.category]) grouped[t.category] = [];
      grouped[t.category].push(t);
    });
    return grouped;
  }, []);

  const candleTemplatesByCategory = useMemo(() => {
    const grouped: Record<string, CandlestickTemplate[]> = {};
    CANDLESTICK_TEMPLATES.forEach(t => {
      if (!grouped[t.category]) grouped[t.category] = [];
      grouped[t.category].push(t);
    });
    return grouped;
  }, []);

  const handleApplyTemplate = useCallback((template: ConditionTemplate) => {
    const existingAliases = new Set(indicators.map(i => i.alias));

    template.indicators.forEach(indSpec => {
      if (!existingAliases.has(indSpec.alias)) {
        const newIndicator = createIndicator(indSpec.id, indSpec.alias);
        if (newIndicator) {
          newIndicator.params = { ...indSpec.params };
          if (indSpec.output) {
            newIndicator.output = indSpec.output;
          }
          onAddIndicator(newIndicator);
        }
      }
    });

    const cond = template.condition;
    let leftOperand: ConditionOperand;

    if (cond.leftIndicator === "close" || cond.leftIndicator === "open" ||
        cond.leftIndicator === "high" || cond.leftIndicator === "low") {
      leftOperand = {
        type: "price",
        priceField: cond.leftIndicator as "close" | "open" | "high" | "low",
      };
    } else {
      leftOperand = {
        type: "indicator",
        indicatorAlias: cond.leftIndicator,
        indicatorOutput: cond.leftOutput || "value",
      };
    }

    let rightOperand: ConditionOperand;
    if (cond.rightType === "value") {
      rightOperand = {
        type: "value",
        value: cond.rightValue ?? 0,
      };
    } else {
      rightOperand = {
        type: "indicator",
        indicatorAlias: cond.rightIndicator,
        indicatorOutput: cond.rightOutput || "value",
      };
    }

    const newCondition: BuilderCondition = {
      id: `cond_${Date.now()}`,
      left: leftOperand,
      operator: cond.operator,
      right: rightOperand,
    };

    onAddCondition(newCondition);
    setShowTemplates(false);
  }, [indicators, createIndicator, onAddIndicator, onAddCondition]);

  const handleApplyCandlestickTemplate = useCallback((template: CandlestickTemplate) => {
    const existingAliases = new Set(indicators.map(i => i.alias));
    const alias = `${template.patternId}_1`;

    if (!existingAliases.has(alias)) {
      const newIndicator = createIndicator(template.patternId, alias);
      if (newIndicator) {
        onAddIndicator(newIndicator);
      }
    }

    const newCondition: BuilderCondition = {
      id: `cond_${Date.now()}`,
      isCandlestick: true,
      candlestickAlias: alias,
      candlestickSignal: template.signal,
      left: { type: "indicator", indicatorAlias: alias, indicatorOutput: "value" },
      operator: "greater_than",
      right: { type: "value", value: 0 },
    };

    onAddCondition(newCondition);
    setShowCandlestickTemplates(false);
  }, [indicators, createIndicator, onAddIndicator, onAddCondition]);

  const handleAddEmptyCondition = useCallback(() => {
    const firstIndicator = indicators[0];
    if (!firstIndicator) return;

    const newCondition: BuilderCondition = {
      id: `cond_${Date.now()}`,
      left: {
        type: "indicator",
        indicatorAlias: firstIndicator.alias,
        indicatorOutput: firstIndicator.output,
      },
      operator: "greater_than",
      right: {
        type: "value",
        value: 0,
      },
    };
    onAddCondition(newCondition);
  }, [indicators, onAddCondition]);

  const handleDragStart = useCallback((index: number) => {
    setDraggedIndex(index);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent, index: number) => {
    e.preventDefault();
    if (draggedIndex !== null && draggedIndex !== index) {
      setDragOverIndex(index);
    }
  }, [draggedIndex]);

  const handleDragEnd = useCallback(() => {
    if (draggedIndex !== null && dragOverIndex !== null && draggedIndex !== dragOverIndex) {
      const newConditions = [...conditionGroup.conditions];
      const [removed] = newConditions.splice(draggedIndex, 1);
      newConditions.splice(dragOverIndex, 0, removed);
      onReorderConditions(newConditions);
    }
    setDraggedIndex(null);
    setDragOverIndex(null);
  }, [draggedIndex, dragOverIndex, conditionGroup.conditions, onReorderConditions]);

  const handleLeftChange = useCallback(
    (conditionId: string, operand: ConditionOperand) => {
      onUpdateCondition(conditionId, { left: operand });
    },
    [onUpdateCondition]
  );

  const handleOperatorChange = useCallback(
    (conditionId: string, operator: ConditionOperator) => {
      onUpdateCondition(conditionId, { operator });
    },
    [onUpdateCondition]
  );

  const handleRightChange = useCallback(
    (conditionId: string, operand: ConditionOperand) => {
      onUpdateCondition(conditionId, { right: operand });
    },
    [onUpdateCondition]
  );

  const hasNoIndicators = indicators.length === 0;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h4 className="text-subheading text-slate-800 dark:text-slate-200 flex items-center gap-2">
          {title}
          {conditionGroup.conditions.length > 0 && (
            <span className="px-1.5 py-0.5 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded">
              {conditionGroup.conditions.length}
            </span>
          )}
        </h4>
        <select
          value={conditionGroup.logic}
          onChange={(e) => onSetLogic(e.target.value as "AND" | "OR")}
          className="px-3 py-1.5 text-xs font-medium border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 focus-ring"
          aria-label="조건 논리 연산자"
        >
          <option value="AND">AND (모두 충족)</option>
          <option value="OR">OR (하나 충족)</option>
        </select>
      </div>

      {/* No Indicators Warning */}
      {hasNoIndicators && (
        <div className="flex items-center gap-2 px-3 py-2 text-xs text-slate-500 bg-slate-50 dark:bg-slate-800/50 rounded-lg" role="alert">
          <AlertCircle className="w-4 h-4 text-slate-400" />
          <span>지표 탭에서 먼저 지표를 추가하세요</span>
        </div>
      )}

      {/* Conditions List - Card based */}
      <div className="space-y-3">
        {conditionGroup.conditions.map((cond, index) => (
          <div key={cond.id}>
            {/* Logic connector between cards */}
            {index > 0 && (
              <div className="flex items-center gap-3 py-2" aria-hidden="true">
                <div className="flex-1 border-t border-slate-200 dark:border-slate-700" />
                <span className="px-3 py-1 text-xs font-semibold text-slate-400 bg-slate-100 dark:bg-slate-800 rounded-full">
                  {conditionGroup.logic}
                </span>
                <div className="flex-1 border-t border-slate-200 dark:border-slate-700" />
              </div>
            )}

            {/* Condition Card */}
            {cond.isCandlestick ? (
              <CandlestickConditionCard
                condition={cond}
                indicators={indicators}
                index={index}
                isDragging={draggedIndex === index}
                isDragOver={dragOverIndex === index}
                onUpdateSignal={(signal) => onUpdateCondition(cond.id, { candlestickSignal: signal })}
                onUpdateAlias={(alias) => onUpdateCondition(cond.id, { candlestickAlias: alias })}
                onRemove={() => onRemoveCondition(cond.id)}
                onDragStart={() => handleDragStart(index)}
                onDragOver={(e) => handleDragOver(e, index)}
                onDragEnd={handleDragEnd}
              />
            ) : (
              <ConditionCard
                condition={cond}
                indicators={indicators}
                index={index}
                isDragging={draggedIndex === index}
                isDragOver={dragOverIndex === index}
                onLeftChange={(op) => handleLeftChange(cond.id, op)}
                onOperatorChange={(op) => handleOperatorChange(cond.id, op)}
                onRightChange={(op) => handleRightChange(cond.id, op)}
                onRemove={() => onRemoveCondition(cond.id)}
                onDragStart={() => handleDragStart(index)}
                onDragOver={(e) => handleDragOver(e, index)}
                onDragEnd={handleDragEnd}
              />
            )}
          </div>
        ))}

        {/* Empty State */}
        {conditionGroup.conditions.length === 0 && !hasNoIndicators && (
          <div className="text-center py-8 text-slate-400 border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-lg">
            <p className="text-sm">조건이 없습니다</p>
            <p className="text-xs mt-1">아래에서 템플릿을 선택하거나 직접 추가하세요</p>
          </div>
        )}
      </div>

      {/* Add Condition Section */}
      <div className="space-y-2">
        {/* Add Buttons Row */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => { setShowTemplates(!showTemplates || showCandlestickTemplates); setShowCandlestickTemplates(false); }}
            className={cn(
              "flex-1 flex items-center justify-center gap-1.5 py-2 text-xs font-medium border rounded-lg transition-all focus-ring",
              showTemplates && !showCandlestickTemplates
                ? "border-primary bg-primary-bg text-primary"
                : "border-slate-200 dark:border-slate-700 text-slate-500 hover:border-primary hover:text-primary"
            )}
            aria-expanded={showTemplates && !showCandlestickTemplates}
            aria-label="빠른 추가 패널 토글"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>빠른 추가</span>
          </button>
          <button
            onClick={handleAddEmptyCondition}
            disabled={hasNoIndicators}
            className={cn(
              "flex-1 flex items-center justify-center gap-1.5 py-2 text-xs font-medium border rounded-lg transition-all focus-ring",
              hasNoIndicators
                ? "border-slate-200 text-slate-300 cursor-not-allowed"
                : "border-slate-200 dark:border-slate-700 text-slate-500 hover:border-blue-400 hover:text-blue-500"
            )}
            aria-label="빈 조건 직접 추가"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>직접 추가</span>
          </button>
        </div>

        {/* Unified Templates Panel with tabs */}
        {(showTemplates || showCandlestickTemplates) && (
          <div className="border border-slate-200 dark:border-slate-700 rounded-lg overflow-hidden">
            {/* Tab bar: 지표 조건 | 캔들스틱 패턴 */}
            <div className="flex border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
              <button
                onClick={() => { setShowTemplates(true); setShowCandlestickTemplates(false); }}
                className={cn(
                  "flex-1 px-3 py-2 text-xs font-medium transition-colors",
                  !showCandlestickTemplates
                    ? "bg-white dark:bg-slate-800 text-primary border-b-2 border-primary"
                    : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
                )}
              >
                지표 조건
              </button>
              <button
                onClick={() => { setShowCandlestickTemplates(true); setShowTemplates(true); }}
                className={cn(
                  "flex-1 px-3 py-2 text-xs font-medium transition-colors",
                  showCandlestickTemplates
                    ? "bg-white dark:bg-slate-800 text-rose-600 dark:text-rose-400 border-b-2 border-rose-500"
                    : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
                )}
              >
                캔들스틱 패턴
              </button>
            </div>

            {/* Indicator Templates Content */}
            {!showCandlestickTemplates && (
              <div className="p-2 space-y-1.5 max-h-[280px] overflow-y-auto scrollbar-thin">
                {hasNoIndicators && (
                  <div className="text-center py-3 text-xs text-slate-400">
                    지표 탭에서 먼저 지표를 추가하세요
                  </div>
                )}
                {!hasNoIndicators && Object.entries(templatesByCategory).map(([cat, templates]) => (
                  <div key={cat}>
                    <div className="px-2 py-1 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                      {TEMPLATE_CATEGORY_LABELS[cat] || cat}
                    </div>
                    {templates.map((template) => (
                      <button
                        key={template.id}
                        onClick={() => handleApplyTemplate(template)}
                        className="w-full flex items-center gap-2 px-3 py-2 text-left rounded-md hover:bg-primary-bg dark:hover:bg-blue-900/20 transition-colors focus-ring"
                        aria-label={`${template.label} 템플릿 적용`}
                      >
                        <Plus className="w-3.5 h-3.5 text-primary flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-xs text-slate-900 dark:text-white">{template.label}</div>
                          <div className="text-[10px] text-slate-500 truncate">{template.description}</div>
                        </div>
                      </button>
                    ))}
                  </div>
                ))}
              </div>
            )}

            {/* Candlestick Templates Content */}
            {showCandlestickTemplates && (
              <div className="p-2 space-y-1.5 max-h-[280px] overflow-y-auto scrollbar-thin">
                {Object.entries(candleTemplatesByCategory).map(([cat, templates]) => (
                  <div key={cat}>
                    <div className="px-2 py-1 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                      {CANDLE_CATEGORY_LABELS[cat] || cat}
                    </div>
                    {templates.map((template) => (
                      <button
                        key={template.id}
                        onClick={() => handleApplyCandlestickTemplate(template)}
                        className="w-full flex items-center gap-2 px-3 py-2 text-left rounded-md hover:bg-rose-50 dark:hover:bg-rose-900/20 transition-colors focus-ring"
                        aria-label={`${template.label} 캔들스틱 패턴 적용`}
                      >
                        <Plus className="w-3.5 h-3.5 text-rose-500 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-xs text-slate-900 dark:text-white flex items-center gap-1.5">
                            {template.label}
                            <span className={cn(
                              "px-1 py-0.5 text-[10px] rounded",
                              template.signal === "bullish" && "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
                              template.signal === "bearish" && "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
                              template.signal === "detected" && "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300"
                            )}>
                              {CANDLESTICK_SIGNAL_LABELS[template.signal]}
                            </span>
                          </div>
                          <div className="text-[10px] text-slate-500 truncate">{template.description}</div>
                        </div>
                      </button>
                    ))}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}

// ============================================================
// Card-based Condition Row
// ============================================================

interface ConditionCardProps {
  condition: BuilderCondition;
  indicators: BuilderIndicator[];
  index: number;
  isDragging: boolean;
  isDragOver: boolean;
  onLeftChange: (operand: ConditionOperand) => void;
  onOperatorChange: (operator: ConditionOperator) => void;
  onRightChange: (operand: ConditionOperand) => void;
  onRemove: () => void;
  onDragStart: () => void;
  onDragOver: (e: React.DragEvent) => void;
  onDragEnd: () => void;
}

function ConditionCard({
  condition,
  indicators,
  index,
  isDragging,
  isDragOver,
  onLeftChange,
  onOperatorChange,
  onRightChange,
  onRemove,
  onDragStart,
  onDragOver,
  onDragEnd,
}: ConditionCardProps) {
  return (
    <div
      draggable
      onDragStart={onDragStart}
      onDragOver={onDragOver}
      onDragEnd={onDragEnd}
      className={cn(
        "condition-card",
        isDragging && "dragging",
        isDragOver && "drag-over"
      )}
      role="listitem"
      aria-label={`조건 ${index + 1}`}
    >
      {/* Card Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div
            className="cursor-grab active:cursor-grabbing text-slate-400 hover:text-slate-600"
            aria-label="드래그하여 순서 변경"
            aria-grabbed={isDragging}
          >
            <GripVertical className="w-4 h-4" />
          </div>
          <span className="text-xs font-medium text-slate-400">조건 {index + 1}</span>
        </div>
        <div className="flex items-center gap-2">
          {/* Right operand type toggle */}
          <select
            value={condition.right.type}
            onChange={(e) => {
              const newType = e.target.value as "indicator" | "value" | "price";
              if (newType === "value") {
                onRightChange({ type: "value", value: 0 });
              } else if (newType === "indicator") {
                // 왼쪽과 다른 지표를 기본값으로 선택 (자기 자신 비교 방지)
                const leftAlias = condition.left.type === "indicator" ? condition.left.indicatorAlias : undefined;
                const preferred = indicators.find(i => i.alias !== leftAlias) || indicators[0];
                onRightChange({
                  type: "indicator",
                  indicatorAlias: preferred?.alias,
                  indicatorOutput: preferred?.output || "value",
                });
              } else {
                onRightChange({ type: "price", priceField: "close" });
              }
            }}
            className="px-2 py-1 text-xs border border-slate-200 dark:border-slate-700 rounded-md bg-slate-50 dark:bg-slate-900 focus-ring"
            aria-label="오른쪽 피연산자 타입"
          >
            <option value="value">숫자</option>
            <option value="indicator">지표</option>
            <option value="price">가격</option>
          </select>
          <button
            onClick={onRemove}
            className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors focus-ring"
            aria-label={`조건 ${index + 1} 삭제`}
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 자기 자신과 비교 경고 */}
      {condition.left.type === "indicator" &&
        condition.right.type === "indicator" &&
        condition.left.indicatorAlias &&
        condition.left.indicatorAlias === condition.right.indicatorAlias && (
          <div className="flex items-center gap-1.5 px-3 py-1.5 mb-2 text-xs text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
            <span>양쪽이 같은 지표입니다 — 조건이 절대 충족되지 않습니다. 오른쪽을 다른 지표로 변경하세요.</span>
          </div>
        )}

      {/* 3-column layout: Left | Operator | Right */}
      <div className="grid grid-cols-1 sm:grid-cols-[1fr_auto_1fr] gap-2 items-center">
        {/* Left Operand */}
        <OperandSelect
          operand={condition.left}
          indicators={indicators}
          onChange={onLeftChange}
          label="왼쪽"
        />

        {/* Operator */}
        <div className="flex justify-center">
          <select
            value={condition.operator}
            onChange={(e) => onOperatorChange(e.target.value as ConditionOperator)}
            className="px-3 py-2 text-sm font-semibold bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-800 rounded-lg cursor-pointer focus-ring"
            aria-label="비교 연산자"
          >
            {OPERATOR_OPTIONS.map((op) => (
              <option key={op.value} value={op.value}>
                {OPERATOR_SENTENCE_LABELS[op.value]}
              </option>
            ))}
          </select>
        </div>

        {/* Right Operand */}
        {condition.right.type === "value" ? (
          <div>
            <input
              type="number"
              value={condition.right.value ?? 0}
              onChange={(e) => onRightChange({ type: "value", value: parseFloat(e.target.value) || 0 })}
              className="w-full px-3 py-2 text-sm font-medium text-center bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 rounded-lg focus-ring"
              aria-label="비교 값"
            />
          </div>
        ) : (
          <OperandSelect
            operand={condition.right}
            indicators={indicators}
            onChange={onRightChange}
            label="오른쪽"
          />
        )}
      </div>
    </div>
  );
}

// ============================================================
// Operand Select (reused for left/right)
// ============================================================

interface OperandSelectProps {
  operand: ConditionOperand;
  indicators: BuilderIndicator[];
  onChange: (operand: ConditionOperand) => void;
  label: string;
}

function OperandSelect({ operand, indicators, onChange, label }: OperandSelectProps) {
  const selectedIndicator = indicators.find(i => i.alias === operand.indicatorAlias);
  const indicatorDef = selectedIndicator ? getIndicatorById(selectedIndicator.indicatorId) : null;
  const hasMultiOutput = indicatorDef && indicatorDef.outputs.length > 1;

  // 지표명 + 출력값을 포함한 표시명 생성
  const getDisplayName = (ind: typeof indicators[0]) => {
    // 사용자가 설정한 표시 이름이 있으면 우선 사용
    if (ind.displayName) return ind.displayName;

    const def = getIndicatorById(ind.indicatorId);
    if (!def) return ind.alias;

    const baseName = def.nameKo;
    const mainParam = Object.values(ind.params)[0];
    const paramStr = mainParam !== undefined ? `(${mainParam})` : "";
    return `${baseName}${paramStr}`;
  };

  // 지표 alias가 현재 목록에 없으면 첫 번째 지표로 자동 교정 (stale alias 방지)
  useEffect(() => {
    if (operand.type !== "indicator" || indicators.length === 0) return;
    const isValid = indicators.some((i) => i.alias === operand.indicatorAlias);
    if (!isValid) {
      const first = indicators[0];
      const def = getIndicatorById(first.indicatorId);
      onChange({
        type: "indicator",
        indicatorAlias: first.alias,
        indicatorOutput: def?.outputs[0]?.id || first.output || "value",
      });
    }
  }, [operand.type, operand.indicatorAlias, indicators, onChange]);

  if (operand.type === "price") {
    return (
      <select
        value={operand.priceField || "close"}
        onChange={(e) => onChange({
          type: "price",
          priceField: e.target.value as "close" | "open" | "high" | "low",
        })}
        className="w-full px-3 py-2 text-sm border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 focus-ring"
        aria-label={`${label} 가격 필드`}
      >
        {PRICE_FIELDS.map((p) => (
          <option key={p.id} value={p.id}>{p.name}</option>
        ))}
      </select>
    );
  }

  // Multi-output: 지표+출력을 하나의 select로 통합 표시
  if (hasMultiOutput) {
    // Composite key: "alias::output"
    const currentKey = `${operand.indicatorAlias}::${operand.indicatorOutput || "value"}`;

    return (
      <select
        value={currentKey}
        onChange={(e) => {
          const [alias, output] = e.target.value.split("::");
          onChange({
            type: "indicator",
            indicatorAlias: alias,
            indicatorOutput: output || "value",
          });
        }}
        className="w-full px-3 py-2 text-sm border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 focus-ring"
        aria-label={`${label} 지표 및 출력값`}
      >
        {indicators.map((ind) => {
          const def = getIndicatorById(ind.indicatorId);
          if (def && def.outputs.length > 1) {
            // 각 출력별로 옵션 생성
            return def.outputs.map((out) => (
              <option key={`${ind.alias}::${out.id}`} value={`${ind.alias}::${out.id}`}>
                {getDisplayName(ind)} {out.name}
              </option>
            ));
          }
          return (
            <option key={`${ind.alias}::value`} value={`${ind.alias}::value`}>
              {getDisplayName(ind)}
            </option>
          );
        })}
      </select>
    );
  }

  return (
    <select
      value={operand.indicatorAlias || ""}
      onChange={(e) => {
        const ind = indicators.find(i => i.alias === e.target.value);
        onChange({
          type: "indicator",
          indicatorAlias: e.target.value,
          indicatorOutput: ind?.output || "value",
        });
      }}
      className="w-full px-3 py-2 text-sm border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 focus-ring"
      aria-label={`${label} 지표`}
    >
      {indicators.map((ind) => (
        <option key={ind.alias} value={ind.alias}>
          {getDisplayName(ind)}
        </option>
      ))}
    </select>
  );
}

// ============================================================
// Candlestick Condition Card
// ============================================================

interface CandlestickConditionCardProps {
  condition: BuilderCondition;
  indicators: BuilderIndicator[];
  index: number;
  isDragging: boolean;
  isDragOver: boolean;
  onUpdateSignal: (signal: CandlestickSignal) => void;
  onUpdateAlias: (alias: string) => void;
  onRemove: () => void;
  onDragStart: () => void;
  onDragOver: (e: React.DragEvent) => void;
  onDragEnd: () => void;
}

function CandlestickConditionCard({
  condition,
  indicators,
  index,
  isDragging,
  isDragOver,
  onUpdateSignal,
  onUpdateAlias,
  onRemove,
  onDragStart,
  onDragOver,
  onDragEnd,
}: CandlestickConditionCardProps) {
  const candlestickIndicators = indicators.filter(ind =>
    CANDLESTICK_PATTERNS.some(p => p.id === ind.indicatorId)
  );

  const selectedIndicator = indicators.find(i => i.alias === condition.candlestickAlias);
  const patternDef = selectedIndicator
    ? CANDLESTICK_PATTERNS.find(p => p.id === selectedIndicator.indicatorId)
    : null;

  return (
    <div
      draggable
      onDragStart={onDragStart}
      onDragOver={onDragOver}
      onDragEnd={onDragEnd}
      className={cn(
        "condition-card border-rose-200 dark:border-rose-800 bg-rose-50/30 dark:bg-rose-900/10",
        isDragging && "dragging",
        isDragOver && "drag-over"
      )}
      role="listitem"
      aria-label={`캔들스틱 조건 ${index + 1}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div
            className="cursor-grab active:cursor-grabbing text-slate-400 hover:text-slate-600"
            aria-label="드래그하여 순서 변경"
          >
            <GripVertical className="w-4 h-4" />
          </div>
          <span className="text-xs font-medium text-rose-500" aria-hidden="true">&#x1F56F;&#xFE0F;</span>
          <span className="text-xs font-medium text-slate-400">캔들스틱 조건</span>
        </div>
        <button
          onClick={onRemove}
          className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors focus-ring"
          aria-label={`캔들스틱 조건 ${index + 1} 삭제`}
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      {/* Pattern + Signal selection */}
      <div className="grid grid-cols-1 sm:grid-cols-[1fr_auto_1fr] gap-2 items-center">
        {/* Pattern select */}
        <select
          value={condition.candlestickAlias || ""}
          onChange={(e) => onUpdateAlias(e.target.value)}
          className="w-full px-3 py-2 text-sm border border-rose-200 dark:border-rose-800 rounded-lg bg-white dark:bg-slate-800 focus-ring"
          aria-label="캔들스틱 패턴"
        >
          {candlestickIndicators.length === 0 ? (
            <option value="">패턴 없음</option>
          ) : (
            candlestickIndicators.map((ind) => {
              const def = CANDLESTICK_PATTERNS.find(p => p.id === ind.indicatorId);
              return (
                <option key={ind.alias} value={ind.alias}>
                  {def ? def.nameKo : ind.alias}
                </option>
              );
            })
          )}
        </select>

        {/* Label */}
        <span className="text-xs font-medium text-slate-400 text-center px-2">패턴이</span>

        {/* Signal select */}
        <select
          value={condition.candlestickSignal || "detected"}
          onChange={(e) => onUpdateSignal(e.target.value as CandlestickSignal)}
          className={cn(
            "w-full px-3 py-2 text-sm font-medium border rounded-lg cursor-pointer focus-ring",
            condition.candlestickSignal === "bullish" && "bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800",
            condition.candlestickSignal === "bearish" && "bg-red-50 text-red-700 border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800",
            (!condition.candlestickSignal || condition.candlestickSignal === "detected") && "bg-gray-50 text-gray-700 border-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700"
          )}
          aria-label="캔들스틱 신호"
        >
          {CANDLESTICK_SIGNAL_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* Pattern description */}
      {patternDef && (
        <p className="mt-2 text-xs text-slate-400">{patternDef.description}</p>
      )}
    </div>
  );
}
