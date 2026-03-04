"use client";

import { useState, useCallback, useMemo, useEffect, useRef } from "react";
import {
  Upload,
  Sparkles,
  Save,
  BarChart3,
  ArrowRight,
  ArrowLeft,
  Loader2,
  Info,
  Check,
  AlertTriangle,
} from "lucide-react";
import { useToast } from "@/components/ui";
import { cn } from "@/lib/utils";
import { FileDropZone } from "@/components/file";
import {
  IndicatorSelector,
  ConditionBuilder,
  RiskManager,
  MetadataEditor,
  PreviewPanel,
  CustomStrategyList,
} from "@/components/builder";
import { useStrategyBuilder, INITIAL_STATE } from "@/hooks/useStrategyBuilder";
import { useLocalStrategies } from "@/hooks/useLocalStrategies";
import { listStrategies, previewCodeFromState } from "@/lib/api";
import { parseYamlToBuilderState } from "@/lib/builder/yamlImporter";
import type { StrategyInfo } from "@/types/signal";
import type { BuilderState } from "@/types/builder";

type BuilderTab = "indicators" | "entry" | "exit" | "risk" | "metadata";

const STEPS: readonly { id: BuilderTab; label: string; shortLabel: string; stepNum: number }[] = [
  { id: "indicators", label: "지표 선택", shortLabel: "지표", stepNum: 1 },
  { id: "entry", label: "진입 조건", shortLabel: "진입", stepNum: 2 },
  { id: "exit", label: "청산 조건", shortLabel: "청산", stepNum: 3 },
  { id: "risk", label: "리스크 관리", shortLabel: "리스크", stepNum: 4 },
  { id: "metadata", label: "전략 정보", shortLabel: "정보", stepNum: 5 },
] as const;

interface BackendPresetStrategy {
  id: string;
  name: string;
  description: string;
  category: string;
  state: BuilderState;
}

export default function BuilderPage() {
  const [builderTab, setBuilderTab] = useState<BuilderTab>("indicators");
  const [showImport, setShowImport] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const [presetStrategies, setPresetStrategies] = useState<BackendPresetStrategy[]>([]);
  const [isLoadingStrategies, setIsLoadingStrategies] = useState(true);

  // Python preview state
  const [pythonContent, setPythonContent] = useState<string>("");
  const [pythonLoading, setPythonLoading] = useState(false);
  const [pythonError, setPythonError] = useState<string>("");
  const pythonRequestRef = useRef(0);

  const builder = useStrategyBuilder();
  const localStrategies = useLocalStrategies();
  const toast = useToast();

  useEffect(() => {
    async function loadStrategies() {
      try {
        const response = await listStrategies();
        const strategies: BackendPresetStrategy[] = (response.strategies || [])
          .filter((s: StrategyInfo) => s.builder_state)
          .map((s: StrategyInfo) => ({
            id: s.id,
            name: s.name,
            description: s.description,
            category: s.category,
            state: s.builder_state as BuilderState,
          }));
        setPresetStrategies(strategies);
      } catch {
        // silently fail - strategies will show as empty
      } finally {
        setIsLoadingStrategies(false);
      }
    }
    loadStrategies();
  }, []);

  // Reset python preview when builder state changes
  useEffect(() => {
    setPythonContent("");
    setPythonError("");
  }, [builder.state.entry, builder.state.exit, builder.state.indicators]);

  const handleImport = useCallback((_file: File, content: string) => {
    try {
      const { state: newState, warnings } = parseYamlToBuilderState(content);
      builder.loadState(newState);
      setShowImport(false);
      toast.success("전략을 불러왔습니다.");
      warnings.forEach((msg) => toast.warning(msg));
    } catch (error) {
      toast.error(
        `YAML 파싱 실패: ${error instanceof Error ? error.message : "알 수 없는 오류"}`
      );
    }
  }, [builder, toast]);

  const handleSelectCustomStrategy = useCallback(
    (strategy: { state: typeof INITIAL_STATE }) => {
      builder.loadState(strategy.state);
    },
    [builder]
  );

  const handleSelectPreset = useCallback(
    (preset: BackendPresetStrategy) => {
      builder.loadState(preset.state);
    },
    [builder]
  );

  const handleSaveCustomStrategy = useCallback(() => {
    if (!builder.isValid) {
      toast.error(builder.validationErrors.join("\n"));
      return;
    }
    localStrategies.save(builder.state);
    toast.success(`"${builder.state.metadata.name}" 전략이 저장되었습니다.`);
  }, [builder, localStrategies, toast]);

  const handleCreateNew = useCallback(() => {
    builder.reset();
    setBuilderTab("indicators");
  }, [builder]);

  // YAML export handler for PreviewPanel
  const handleExportYaml = useCallback(() => {
    const content = builder.toYamlString;
    if (!content) return;
    const filename = builder.state.metadata.name
      ? `${builder.state.metadata.name.toLowerCase().replace(/\s+/g, "_")}.kis.yaml`
      : "strategy.kis.yaml";
    const blob = new Blob([content], { type: "application/x-yaml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [builder.toYamlString, builder.state.metadata.name]);

  // Python export handler
  const handleExportPython = useCallback(() => {
    if (!pythonContent) return;
    const filename = builder.state.metadata.name
      ? `strategy_${builder.state.metadata.name.toLowerCase().replace(/\s+/g, "_")}.py`
      : "strategy.py";
    const blob = new Blob([pythonContent], { type: "text/x-python" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [pythonContent, builder.state.metadata.name]);

  // Python preview fetcher
  const handleRequestPython = useCallback(async () => {
    if (builder.state.entry.conditions.length === 0) return;

    const requestId = ++pythonRequestRef.current;
    setPythonLoading(true);
    setPythonError("");

    try {
      const response = await previewCodeFromState(builder.state);
      if (requestId !== pythonRequestRef.current) return; // stale request
      if (response.status === "success" && response.code) {
        setPythonContent(response.code);
      } else {
        setPythonError(response.message || "코드 생성 실패");
      }
    } catch (error) {
      if (requestId !== pythonRequestRef.current) return;
      setPythonError(error instanceof Error ? error.message : "API 오류");
    } finally {
      if (requestId === pythonRequestRef.current) {
        setPythonLoading(false);
      }
    }
  }, [builder.state]);

  const builderYamlContent = useMemo(() => {
    return builder.toYamlString;
  }, [builder.toYamlString]);

  // Step status computation
  const getStepStatus = useCallback((tabId: BuilderTab): "complete" | "warning" | "empty" => {
    switch (tabId) {
      case "metadata":
        return builder.state.metadata.name.trim() ? "complete" : "empty";
      case "indicators":
        return builder.state.indicators.length > 0 ? "complete" : "empty";
      case "entry":
        return builder.state.entry.conditions.length > 0 ? "complete" : "warning";
      case "exit":
        return builder.state.exit.conditions.length > 0 ? "complete" : "warning";
      case "risk":
        return builder.state.risk.stopLoss.enabled ||
               builder.state.risk.takeProfit.enabled ||
               builder.state.risk.trailingStop.enabled
               ? "complete" : "empty";
      default:
        return "empty";
    }
  }, [builder.state]);

  // Navigation
  const currentStepIndex = STEPS.findIndex(s => s.id === builderTab);

  const goToNextStep = useCallback(() => {
    const nextIndex = currentStepIndex + 1;
    if (nextIndex < STEPS.length) {
      setBuilderTab(STEPS[nextIndex].id);
    }
  }, [currentStepIndex]);

  const goToPrevStep = useCallback(() => {
    const prevIndex = currentStepIndex - 1;
    if (prevIndex >= 0) {
      setBuilderTab(STEPS[prevIndex].id);
    }
  }, [currentStepIndex]);

  // Keyboard navigation for steps
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLSelectElement) return;
      if (e.key === "ArrowRight" && e.altKey) {
        e.preventDefault();
        goToNextStep();
      } else if (e.key === "ArrowLeft" && e.altKey) {
        e.preventDefault();
        goToPrevStep();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [goToNextStep, goToPrevStep]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-display text-slate-900 dark:text-white flex items-center gap-2">
            <Sparkles className="w-7 h-7 text-primary" aria-hidden="true" />
            전략 빌더
          </h1>
          <p className="text-body text-slate-500 dark:text-slate-400 mt-1">
            기술적 지표 기반 매매 전략을 시각적으로 구성하세요
          </p>
        </div>

        {/* Mobile preview toggle */}
        <button
          onClick={() => setShowPreview(!showPreview)}
          className={cn(
            "lg:hidden flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors focus-ring",
            showPreview
              ? "bg-primary text-white"
              : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300"
          )}
          aria-label="미리보기 토글"
        >
          <Info className="w-4 h-4" aria-hidden="true" />
        </button>
      </div>

      {/* Main Layout */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left: Strategy List */}
        <div className="lg:col-span-1 space-y-4">
          {/* Preset strategies */}
          <div className="card">
            <h2 className="text-subheading text-slate-900 dark:text-white mb-4 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-primary" aria-hidden="true" />
              기본 전략
              <span className="text-caption text-slate-400 font-normal">({presetStrategies.length})</span>
            </h2>
            <div className="space-y-2 max-h-[300px] overflow-y-auto scrollbar-thin">
              {isLoadingStrategies ? (
                <div className="flex items-center justify-center py-8 text-slate-400">
                  <Loader2 className="w-5 h-5 animate-spin mr-2" aria-hidden="true" />
                  <span className="text-sm">전략 로딩 중...</span>
                </div>
              ) : presetStrategies.length === 0 ? (
                <div className="text-center py-8 text-slate-400 text-sm">
                  전략이 없습니다
                </div>
              ) : (
                presetStrategies.map((preset) => (
                  <button
                    key={preset.id}
                    onClick={() => handleSelectPreset(preset)}
                    className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-primary hover:bg-primary/5 transition-all text-left focus-ring"
                    aria-label={`${preset.name} 전략 선택`}
                  >
                    <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <BarChart3 className="w-4 h-4 text-primary" aria-hidden="true" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm text-slate-900 dark:text-white truncate">
                        {preset.name}
                      </div>
                      <div className="text-xs text-slate-500 truncate">
                        {preset.category}
                      </div>
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>

          {/* My Strategies */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-subheading text-slate-900 dark:text-white flex items-center gap-2">
                <Save className="w-4 h-4 text-primary" aria-hidden="true" />
                내 전략
              </h2>
              <button
                onClick={() => setShowImport(!showImport)}
                className={cn(
                  "flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium transition-colors focus-ring",
                  showImport
                    ? "bg-primary text-white"
                    : "text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"
                )}
                aria-label="YAML 파일 가져오기"
              >
                <Upload className="w-3.5 h-3.5" aria-hidden="true" />
                Import
              </button>
            </div>
            {showImport && (
              <div className="mb-3">
                <FileDropZone onFileSelect={handleImport} />
              </div>
            )}
            <CustomStrategyList
              strategies={localStrategies.strategies}
              selectedId={null}
              onSelect={handleSelectCustomStrategy}
              onDelete={localStrategies.remove}
              onDuplicate={localStrategies.duplicate}
              onCreateNew={handleCreateNew}
            />
          </div>
        </div>

        {/* Right: Visual Builder */}
        <div className="lg:col-span-2">
          <div className="grid lg:grid-cols-2 gap-4">
            {/* Builder Panel */}
            <div className={cn("card flex flex-col", showPreview && "hidden lg:block")} style={{ maxHeight: "calc(100vh - 180px)" }}>
              {/* Stepper Navigation - compact horizontal */}
              <nav
                className="flex items-center mb-4 overflow-x-auto scrollbar-thin"
                role="tablist"
                aria-label="전략 빌더 단계"
              >
                {STEPS.map((step, index) => {
                  const status = getStepStatus(step.id);
                  const isActive = builderTab === step.id;
                  const isPast = index < currentStepIndex;

                  return (
                    <div key={step.id} className="flex items-center flex-shrink-0">
                      <button
                        onClick={() => setBuilderTab(step.id)}
                        role="tab"
                        aria-selected={isActive}
                        aria-controls={`panel-${step.id}`}
                        id={`tab-${step.id}`}
                        className={cn(
                          "flex items-center gap-1 px-2 py-1 rounded text-[11px] font-medium transition-all whitespace-nowrap focus-ring",
                          isActive && "bg-primary text-white shadow-sm",
                          !isActive && status === "complete" && "text-emerald-600 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-900/20",
                          !isActive && status === "warning" && "text-amber-600 dark:text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-900/20",
                          !isActive && status === "empty" && "text-slate-400 dark:text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800",
                        )}
                      >
                        {/* Status icon - inline, no circle */}
                        {!isActive && status === "complete" ? (
                          <Check className="w-3 h-3 flex-shrink-0" />
                        ) : !isActive && status === "warning" ? (
                          <AlertTriangle className="w-3 h-3 flex-shrink-0" />
                        ) : (
                          <span className="w-3 text-center flex-shrink-0">{step.stepNum}</span>
                        )}
                        <span>{step.shortLabel}</span>
                      </button>
                      {/* Connector */}
                      {index < STEPS.length - 1 && (
                        <div
                          className={cn(
                            "w-3 h-px mx-0.5 flex-shrink-0",
                            isPast ? "bg-emerald-300 dark:bg-emerald-700" : "bg-slate-200 dark:bg-slate-700"
                          )}
                          aria-hidden="true"
                        />
                      )}
                    </div>
                  );
                })}
              </nav>

              {/* Tab Content - scrollable */}
              <div
                className="flex-1 overflow-y-auto min-h-0 pr-1 scrollbar-thin"
                role="tabpanel"
                id={`panel-${builderTab}`}
                aria-labelledby={`tab-${builderTab}`}
              >
                {builderTab === "metadata" && (
                  <MetadataEditor metadata={builder.state.metadata} onChange={builder.setMetadata} />
                )}

                {builderTab === "indicators" && (
                  <IndicatorSelector
                    selectedIndicators={builder.state.indicators}
                    onAddIndicator={builder.addIndicatorWithAutoConditions}
                    onUpdateIndicator={builder.updateIndicator}
                    onRemoveIndicator={builder.removeIndicator}
                    createIndicator={builder.createIndicator}
                  />
                )}

                {builderTab === "entry" && (
                  <ConditionBuilder
                    title="진입 조건"
                    conditionGroup={builder.state.entry}
                    indicators={builder.state.indicators}
                    onAddCondition={builder.addEntryCondition}
                    onAddIndicator={builder.addIndicator}
                    createIndicator={builder.createIndicator}
                    onUpdateCondition={builder.updateEntryCondition}
                    onRemoveCondition={builder.removeEntryCondition}
                    onReorderConditions={builder.reorderEntryConditions}
                    onSetLogic={builder.setEntryLogic}
                  />
                )}

                {builderTab === "exit" && (
                  <ConditionBuilder
                    title="청산 조건"
                    conditionGroup={builder.state.exit}
                    indicators={builder.state.indicators}
                    onAddCondition={builder.addExitCondition}
                    onAddIndicator={builder.addIndicator}
                    createIndicator={builder.createIndicator}
                    onUpdateCondition={builder.updateExitCondition}
                    onRemoveCondition={builder.removeExitCondition}
                    onReorderConditions={builder.reorderExitConditions}
                    onSetLogic={builder.setExitLogic}
                  />
                )}

                {builderTab === "risk" && (
                  <RiskManager risk={builder.state.risk} onChange={builder.setRisk} />
                )}
              </div>

              {/* Step Navigation Footer - always visible */}
              <div className="flex-shrink-0 mt-4 flex items-center justify-between border-t border-slate-100 dark:border-slate-700 pt-3">
                <button
                  onClick={goToPrevStep}
                  disabled={currentStepIndex === 0}
                  className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium rounded-lg transition-colors text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800 disabled:opacity-30 disabled:cursor-not-allowed focus-ring"
                  aria-label="이전 단계"
                >
                  <ArrowLeft className="w-4 h-4" aria-hidden="true" />
                  이전
                </button>

                {currentStepIndex < STEPS.length - 1 ? (
                  <button
                    onClick={goToNextStep}
                    className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-lg transition-colors bg-primary text-white hover:bg-primary-dark focus-ring"
                    aria-label="다음 단계"
                  >
                    다음
                    <ArrowRight className="w-4 h-4" aria-hidden="true" />
                  </button>
                ) : (
                  <button
                    onClick={handleSaveCustomStrategy}
                    disabled={!builder.isValid}
                    className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-lg transition-colors bg-primary text-white hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed focus-ring"
                    aria-label="전략 저장하기"
                  >
                    <Save className="w-4 h-4" aria-hidden="true" />
                    저장하기
                  </button>
                )}
              </div>
            </div>

            {/* Preview Panel */}
            <div className={cn("card", !showPreview && "hidden lg:block")}>
              {showPreview && (
                <button
                  onClick={() => setShowPreview(false)}
                  className="lg:hidden mb-3 text-sm text-slate-500 hover:text-slate-700"
                >
                  &larr; 빌더로 돌아가기
                </button>
              )}
              <PreviewPanel
                yamlContent={builderYamlContent}
                pythonContent={pythonContent}
                pythonLoading={pythonLoading}
                pythonError={pythonError}
                onExport={handleExportYaml}
                onExportPython={handleExportPython}
                onRequestPython={handleRequestPython}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
