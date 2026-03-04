"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import {
  Loader2,
  Play,
  Calendar,
  TrendingUp,
  Target,
  Shield,
  AlertTriangle,
  BarChart3,
  Zap,
  Repeat,
  Activity,
  DollarSign,
  Percent,
  ChevronDown,
} from "lucide-react";
import { cn, formatCurrency, formatPercent } from "@/lib/utils";
import { listStrategies, runBacktest, runCustomBacktest } from "@/lib/api";
import { FileDropZone } from "@/components/file";
import { StockInput } from "@/components/symbols";
import { EquityChart } from "@/components/backtest";
import type { ChartDataPoint, TradeMarker } from "@/components/backtest";
import type { Strategy, BacktestResult, ParamDefinition } from "@/types";

// 통계 카드 컴포넌트
function StatCard({
  label,
  value,
  subValue,
  icon: Icon,
  positive,
  iconColor,
}: {
  label: string;
  value: string;
  subValue?: string;
  icon: React.ElementType;
  positive?: boolean | null;
  iconColor?: string;
}) {
  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-2">
        <Icon className={cn("w-4 h-4", iconColor || "text-slate-400")} />
        <span className="text-xs font-medium text-slate-500">{label}</span>
      </div>
      <div
        className={cn(
          "text-xl font-bold tabular-nums",
          positive === true && "text-profit",
          positive === false && "text-loss",
          positive === null && "text-slate-900 dark:text-white"
        )}
      >
        {value}
      </div>
      {subValue && <div className="text-xs text-slate-400 mt-1">{subValue}</div>}
    </div>
  );
}

// 파라미터 슬라이더 컴포넌트
function ParamSlider({
  name,
  definition,
  value,
  onChange,
}: {
  name: string;
  definition: ParamDefinition;
  value: number;
  onChange: (value: number) => void;
}) {
  const step = definition.step ?? (definition.type === "int" ? 1 : 0.1);
  const label = definition.label || name.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
  
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm text-slate-600 dark:text-slate-400">{label}</span>
        <span className="text-sm font-mono font-medium tabular-nums">{value}</span>
      </div>
      <input
        type="range"
        min={definition.min}
        max={definition.max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-primary"
      />
      <div className="flex justify-between text-xs text-slate-400">
        <span>{definition.min}</span>
        <span>{definition.max}</span>
      </div>
    </div>
  );
}

// 메트릭 그룹 컴포넌트
function MetricsGroup({
  title,
  icon: Icon,
  metrics,
  badge,
}: {
  title: string;
  icon: React.ElementType;
  metrics: { label: string; value: string; highlight?: boolean; positive?: boolean | null }[];
  badge?: string;
}) {
  return (
    <div className="card">
      <h3 className="font-semibold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
        <Icon className="w-4 h-4 text-kis-blue" />
        {title}
        {badge && (
          <span className="ml-auto text-[0.625rem] font-semibold text-slate-500 bg-slate-100 border border-slate-200 rounded px-1.5 py-0.5 tracking-wide">
            {badge}
          </span>
        )}
      </h3>
      <div className="space-y-2">
        {metrics.map((m, i) => (
          <div key={i} className="flex justify-between items-center">
            <span className="text-sm text-slate-500">{m.label}</span>
            <span
              className={cn(
                "text-sm font-mono",
                m.highlight && "font-bold text-kis-blue",
                m.positive === true && "text-profit",
                m.positive === false && "text-loss",
                !m.highlight && m.positive === undefined && "text-slate-900 dark:text-white"
              )}
            >
              {m.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function BacktestPage() {
  // 데이터 (templates + strategies 합쳐서 중복 제거)
  const [allStrategies, setAllStrategies] = useState<Strategy[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [backendDown, setBackendDown] = useState(false);

  // 설정
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [importedYaml, setImportedYaml] = useState<string | null>(null);
  const [selectedStocks, setSelectedStocks] = useState<string[]>([]);
  const [startDate, setStartDate] = useState(() => {
    const d = new Date();
    d.setMonth(d.getMonth() - 6);
    return d.toISOString().split("T")[0];
  });
  const [endDate, setEndDate] = useState(() => new Date().toISOString().split("T")[0]);
  const [initialCapital, setInitialCapital] = useState(100_000_000);
  
  // 거래 비용 설정
  const [commissionRate, setCommissionRate] = useState(0.015); // 0.015%
  const [taxRate, setTaxRate] = useState(0.2); // 0.2%
  const [slippage, setSlippage] = useState(0.1); // 0.1%
  
  // 파라미터 오버라이드 (전략 파라미터 조정용)
  const [paramOverrides, setParamOverrides] = useState<Record<string, number>>({});
  
  // 선택된 전략 객체
  const selectedStrategy = useMemo(() => {
    if (!selectedId) return null;
    return allStrategies.find(s => s.id === selectedId) || null;
  }, [selectedId, allStrategies]);
  
  // 전략 선택 시 기본 파라미터로 초기화
  useEffect(() => {
    if (selectedStrategy?.params) {
      const defaults: Record<string, number> = {};
      Object.entries(selectedStrategy.params).forEach(([key, def]) => {
        defaults[key] = def.default;
      });
      setParamOverrides(defaults);
    } else {
      setParamOverrides({});
    }
  }, [selectedStrategy]);
  
  // 파라미터 변경 핸들러
  const handleParamChange = useCallback((name: string, value: number) => {
    setParamOverrides(prev => ({ ...prev, [name]: value }));
  }, []);
  
  // 결과
  const [isRunning, setIsRunning] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tradesOpen, setTradesOpen] = useState(false);

  // 로딩 단계 업데이트 (시뮬레이션)
  useEffect(() => {
    if (!isRunning) {
      setLoadingStep(0);
      return;
    }
    const interval = setInterval(() => {
      setLoadingStep((prev) => (prev < 5 ? prev + 1 : prev));
    }, 2500);
    return () => clearInterval(interval);
  }, [isRunning]);

  // 로딩 단계별 메시지
  const loadingMessages = [
    "데이터 확인 중...",
    "KOSPI 벤치마크 다운로드 중...",
    "종목 데이터 준비 중...",
    "Lean 엔진 실행 중...",
    "백테스트 진행 중...",
    "결과 분석 중...",
  ];

  // 데이터 로드 (strategies API가 14개 전체 포함)
  useEffect(() => {
    const loadData = async () => {
      try {
        const res = await listStrategies();
        setAllStrategies(res.data || []);
        setBackendDown(false);
      } catch {
        setAllStrategies([]);
        setBackendDown(true);
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, []);

  // Import 핸들러
  const handleImport = useCallback((file: File, content: string) => {
    setImportedYaml(content);
    setSelectedId(null);
  }, []);

  // 백테스트 실행
  const handleRun = useCallback(async () => {
    if (!selectedId && !importedYaml) return;
    if (selectedStocks.length === 0) return;

    setIsRunning(true);
    setError(null);
    setResult(null);

    try {
      let response;

      // 1. Import된 YAML이 있으면 커스텀 백테스트
      if (importedYaml) {
        response = await runCustomBacktest(
          importedYaml,
          selectedStocks,
          startDate,
          endDate,
          initialCapital,
          commissionRate / 100, // % → 소수점
          taxRate / 100,
          slippage / 100
        );
      }
      // 2. 전략 선택 시 프리셋 백테스트
      else if (selectedId) {
        response = await runBacktest({
          strategy_id: selectedId,
          symbols: selectedStocks,
          start_date: startDate,
          end_date: endDate,
          initial_capital: initialCapital,
          commission_rate: commissionRate / 100,
          tax_rate: taxRate / 100,
          slippage: slippage / 100,
          param_overrides: Object.keys(paramOverrides).length > 0 ? paramOverrides : undefined,
        });
      } else {
        throw new Error("전략을 선택하거나 파일을 Import하세요");
      }

      if (response.success) {
        setResult(response.data);
      } else {
        setError(response.message || "백테스트 실패");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "백테스트 실행 중 오류");
    } finally {
      setIsRunning(false);
    }
  }, [selectedId, importedYaml, selectedStocks, startDate, endDate, initialCapital, commissionRate, taxRate, slippage, paramOverrides]);

  // Y축 범위 계산 (15% 패딩)
  const yAxisDomain = useMemo((): [number, number] => {
    if (!result?.equity_curve) return [0, 100_000_000];
    const values = Object.values(result.equity_curve);
    const benchmarkValues = result.benchmark_curve
      ? Object.values(result.benchmark_curve).map(pct => initialCapital * (1 + pct / 100))
      : [];
    const allValues = [...values, ...benchmarkValues, initialCapital];
    const min = Math.min(...allValues);
    const max = Math.max(...allValues);
    const padding = (max - min) * 0.15;
    return [Math.max(0, min - padding), max + padding];
  }, [result, initialCapital]);

  // 차트 데이터 (KOSPI는 초기자본 기준 절대값으로 변환, drawdown 포함)
  const chartData: ChartDataPoint[] = useMemo(() => {
    if (!result?.equity_curve) return [];
    const entries = Object.entries(result.equity_curve);
    const benchmarkEntries = result.benchmark_curve || {};

    let peak = -Infinity;

    return entries.map(([date, value]) => {
      const benchmarkPct = benchmarkEntries[date];
      const benchmarkValue = benchmarkPct != null
        ? initialCapital * (1 + benchmarkPct / 100)
        : null;

      // Track running peak for drawdown
      peak = Math.max(peak, value);
      const drawdown = peak > 0 ? ((value - peak) / peak) * 100 : 0;

      return {
        date,
        value,
        returnPct: ((value - initialCapital) / initialCapital) * 100,
        benchmarkPct: benchmarkPct ?? null,
        benchmark: benchmarkValue,
        drawdown,
      };
    });
  }, [result, initialCapital]);

  // 거래 내역 (Buy/Sell 마커용)
  const tradeMarkers: TradeMarker[] = useMemo(() => {
    if (!result?.trades || result.trades.length === 0) return [];

    return result.trades.map((trade) => ({
      date: trade.time.split(/[T ]/)[0],
      type: trade.direction.toLowerCase() as "buy" | "sell",
      price: trade.price,
    }));
  }, [result]);

  const canRun = (selectedId || importedYaml) && selectedStocks.length > 0;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 relative">
      {/* 로딩 오버레이 */}
      {isRunning && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-2xl max-w-sm w-full mx-4">
            <div className="flex flex-col items-center">
              {/* 스피너 */}
              <div className="relative w-16 h-16 mb-6">
                <div className="absolute inset-0 border-4 border-slate-200 dark:border-slate-700 rounded-full"></div>
                <div className="absolute inset-0 border-4 border-kis-blue border-t-transparent rounded-full animate-spin"></div>
              </div>

              {/* 현재 단계 */}
              <p className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                {loadingMessages[loadingStep]}
              </p>

              {/* 진행률 바 */}
              <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 mb-4">
                <div
                  className="bg-kis-blue h-2 rounded-full transition-all duration-500"
                  style={{ width: `${((loadingStep + 1) / loadingMessages.length) * 100}%` }}
                ></div>
              </div>

              {/* 단계 표시 */}
              <p className="text-xs text-slate-500">
                {loadingStep + 1} / {loadingMessages.length}
              </p>

              {/* 안내 메시지 */}
              <p className="text-xs text-slate-400 mt-4 text-center">
                처음 실행 시 데이터 다운로드로 시간이 걸릴 수 있습니다
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 백엔드 미실행 경고 */}
      {backendDown && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-red-700 dark:text-red-400">백엔드 서버가 실행되지 않았습니다</p>
              <p className="text-sm text-red-600/80 dark:text-red-400/80 mt-1">
                백테스트를 실행하려면 먼저 백엔드 서버를 시작하세요:
              </p>
              <code className="block mt-2 px-3 py-2 bg-red-100 dark:bg-red-900/40 rounded-lg text-sm font-mono text-red-800 dark:text-red-300">
                cd backend && uv run uvicorn main:app --port 8002 --reload
              </code>
            </div>
          </div>
        </div>
      )}

      {/* 헤더 */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">백테스트</h1>
        <p className="text-slate-600 dark:text-slate-400">
          YAML 파일을 드롭하거나 전략을 선택하여 백테스트를 실행하세요
        </p>
      </div>

      {/* 2컬럼 레이아웃 */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* 왼쪽: 설정 */}
        <div className="space-y-4">
          {/* 파일 드롭존 */}
          <FileDropZone
            onFileSelect={handleImport}
            className="min-h-[120px]"
          />

          {/* 또는 전략 선택 */}
          <div className="card">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
              <Zap className="w-4 h-4 text-kis-blue" />
              전략 선택
            </h3>
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin text-slate-400 mx-auto" />
            ) : (
              <select
                value={selectedId || ""}
                onChange={(e) => {
                  setSelectedId(e.target.value || null);
                  setImportedYaml(null);
                }}
                className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-sm"
              >
                <option value="">-- 전략 선택 ({allStrategies.length}개) --</option>
                {allStrategies.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name}
                  </option>
                ))}
              </select>
            )}
            {importedYaml && (
              <div className="mt-2 px-2 py-1 bg-amber-100 text-amber-700 rounded text-xs">
                Import된 파일 사용 중
              </div>
            )}
            
            {/* 전략 설명 */}
            {selectedStrategy && (
              <p className="mt-2 text-xs text-slate-500">
                {selectedStrategy.description}
              </p>
            )}
          </div>

          {/* 파라미터 설정 (전략 선택 시만 표시) */}
          {selectedStrategy?.params && Object.keys(selectedStrategy.params).length > 0 && (
            <div className="card">
              <h3 className="font-semibold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
                <Activity className="w-4 h-4 text-kis-blue" />
                파라미터 설정
              </h3>
              <div className="space-y-4">
                {Object.entries(selectedStrategy.params).map(([name, def]) => (
                  <ParamSlider
                    key={name}
                    name={name}
                    definition={def}
                    value={paramOverrides[name] ?? def.default}
                    onChange={(value) => handleParamChange(name, value)}
                  />
                ))}
              </div>
            </div>
          )}

          {/* 종목 선택 */}
          <div className="card">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
              <Target className="w-4 h-4 text-kis-blue" />
              종목 선택
            </h3>
            <StockInput stocks={selectedStocks} onChange={setSelectedStocks} />
          </div>

          {/* 기간 설정 */}
          <div className="card">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-kis-blue" />
              기간 설정
            </h3>
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs text-slate-500 mb-1 block">시작일</label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-500 mb-1 block">종료일</label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg text-sm"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs text-slate-500 mb-1 block">초기 자본 (원)</label>
                <input
                  type="number"
                  value={initialCapital}
                  onChange={(e) => setInitialCapital(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg text-sm"
                />
              </div>
            </div>
          </div>

          {/* 거래 비용 설정 */}
          <div className="card">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
              <Percent className="w-4 h-4 text-kis-blue" />
              거래 비용
            </h3>
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs text-slate-500 mb-1 block">수수료 (%)</label>
                  <input
                    type="number"
                    step="0.001"
                    value={commissionRate}
                    onChange={(e) => setCommissionRate(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-500 mb-1 block">거래세 (%)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={taxRate}
                    onChange={(e) => setTaxRate(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg text-sm"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs text-slate-500 mb-1 block">슬리피지 (%)</label>
                <input
                  type="number"
                  step="0.01"
                  value={slippage}
                  onChange={(e) => setSlippage(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg text-sm"
                />
              </div>
              <p className="text-xs text-slate-400">
                * 수수료: 매수/매도 시 부과, 거래세: 매도 시 부과
              </p>
            </div>
          </div>

          {/* 실행 버튼 */}
          <button
            onClick={handleRun}
            disabled={!canRun || isRunning}
            className={cn(
              "w-full flex items-center justify-center gap-2 py-3 rounded-xl font-bold transition-all",
              canRun && !isRunning
                ? "bg-kis-blue hover:bg-kis-blue-dark text-white shadow-lg"
                : "bg-slate-200 text-slate-400 cursor-not-allowed"
            )}
          >
            {isRunning ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                실행 중...
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                백테스트 실행
              </>
            )}
          </button>
        </div>

        {/* 오른쪽: 결과 */}
        <div className="lg:col-span-2 space-y-4">
          {error && (
            <div className="card bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="text-red-600 dark:text-red-400 font-medium">{error}</p>
                  {/* 도움말 표시 */}
                  {error.includes("Docker") && (
                    <div className="mt-2 text-xs text-red-500/80 space-y-1">
                      <p>• Docker Desktop이 설치되어 있는지 확인하세요</p>
                      <p>• Docker Desktop을 실행한 후 재시도하세요</p>
                      <p className="font-mono bg-red-100 dark:bg-red-900/30 px-2 py-1 rounded">
                        docker pull quantconnect/lean:latest
                      </p>
                    </div>
                  )}
                  {error.includes("데이터") && (
                    <div className="mt-2 text-xs text-red-500/80 space-y-1">
                      <p>• 종목 코드가 올바른지 확인하세요 (예: 005930)</p>
                      <p>• 백테스트 기간에 거래일이 포함되어 있는지 확인하세요</p>
                      <p>• KIS API 환경설정(.env)을 확인하세요</p>
                    </div>
                  )}
                  {error.includes("지표") && (
                    <div className="mt-2 text-xs text-red-500/80 space-y-1">
                      <p>• 전략의 지표 설정을 확인하세요</p>
                      <p>• 지표 파라미터가 올바른 범위인지 확인하세요</p>
                    </div>
                  )}
                  {error.includes("시간 초과") && (
                    <div className="mt-2 text-xs text-red-500/80 space-y-1">
                      <p>• 백테스트 기간을 줄여보세요</p>
                      <p>• 복잡한 조건을 단순화해보세요</p>
                    </div>
                  )}
                  {(error.includes("인증") || error.includes("my_url") || error.includes("appkey")) && (
                    <div className="mt-2 text-sm text-red-600 dark:text-red-400 space-y-1">
                      <p className="font-medium">인증 설정 확인:</p>
                      <ul className="list-disc ml-4 space-y-1 text-xs">
                        <li>~/KIS/config/kis_devlp.yaml 파일의 appkey / appsecret을 확인해주세요</li>
                        <li>모의투자: paper_app, paper_sec / 실전투자: my_app, my_sec</li>
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {result ? (
            <>
              {/* 요약 카드 */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <StatCard
                  label="총 수익률"
                  value={formatPercent(result.net_profit_percent)}
                  subValue={formatCurrency(result.net_profit)}
                  icon={TrendingUp}
                  positive={result.net_profit >= 0}
                  iconColor="text-emerald-500"
                />
                <StatCard
                  label="CAGR"
                  value={formatPercent(result.metrics.basic.annual_return)}
                  icon={Target}
                  positive={result.metrics.basic.annual_return >= 0}
                  iconColor="text-blue-500"
                />
                <StatCard
                  label="최대 낙폭"
                  value={formatPercent(-Math.abs(result.metrics.basic.max_drawdown))}
                  icon={AlertTriangle}
                  positive={false}
                  iconColor="text-amber-500"
                />
                <StatCard
                  label="샤프 비율"
                  value={result.metrics.risk.sharpe_ratio.toFixed(2)}
                  icon={Shield}
                  positive={result.metrics.risk.sharpe_ratio > 1 ? true : result.metrics.risk.sharpe_ratio < 0.5 ? false : null}
                  iconColor="text-purple-500"
                />
              </div>

              {/* 차트 (Equity + Drawdown) */}
              {chartData.length > 0 && (
                <EquityChart
                  chartData={chartData}
                  tradeMarkers={tradeMarkers}
                  initialCapital={initialCapital}
                  yAxisDomain={yAxisDomain}
                />
              )}

              {/* 전체 통계 */}
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                <MetricsGroup
                  title="위험 대비 성과"
                  icon={Shield}
                  metrics={[
                    { label: "샤프 비율", value: result.metrics.risk.sharpe_ratio.toFixed(2), highlight: true },
                    { label: "소르티노 비율", value: result.metrics.risk.sortino_ratio.toFixed(2) },
                    { label: "확률적 샤프", value: formatPercent(result.metrics.risk.probabilistic_sharpe) },
                  ]}
                />
                <MetricsGroup
                  title="시장 민감도"
                  icon={Activity}
                  metrics={[
                    { label: "알파", value: result.metrics.greeks.alpha.toFixed(4) },
                    { label: "베타", value: result.metrics.greeks.beta.toFixed(4) },
                  ]}
                />
                <MetricsGroup
                  title="변동성"
                  icon={BarChart3}
                  metrics={[
                    { label: "연간 표준편차", value: formatPercent(result.metrics.volatility.annual_std_dev) },
                    { label: "연간 분산", value: result.metrics.volatility.annual_variance.toFixed(4) },
                  ]}
                />
                <MetricsGroup
                  title="시장 대비 성과"
                  icon={Target}
                  badge="KOSPI기준"
                  metrics={[
                    { label: "정보 비율", value: result.metrics.benchmark.information_ratio.toFixed(2) },
                    { label: "추적 오차", value: formatPercent(result.metrics.benchmark.tracking_error) },
                    { label: "트레이너 비율", value: result.metrics.benchmark.treynor_ratio !== 0 ? result.metrics.benchmark.treynor_ratio.toFixed(4) : "N/A" },
                  ]}
                />
                <MetricsGroup
                  title="매매 리포트"
                  icon={Repeat}
                  metrics={[
                    { label: "체결 거래", value: `${result.trades_count}회`, highlight: true },
                    { label: "승률", value: formatPercent(result.metrics.trading.win_rate), positive: result.metrics.trading.win_rate > 0.5 ? true : result.metrics.trading.win_rate < 0.5 ? false : null },
                    { label: "평균 수익", value: formatPercent(result.metrics.trading.avg_win), positive: true },
                    { label: "평균 손실", value: formatPercent(result.metrics.trading.avg_loss), positive: false },
                    { label: "손익비", value: result.metrics.trading.profit_loss_ratio.toFixed(2) },
                    { label: "기대값", value: result.metrics.trading.expectancy.toFixed(4) },
                  ]}
                />
                <MetricsGroup
                  title="운용 정보 및 비용"
                  icon={DollarSign}
                  metrics={[
                    { label: "총 수수료", value: formatCurrency(result.metrics.other.total_fees) },
                    { label: "회전율", value: formatPercent(result.metrics.other.portfolio_turnover) },
                    { label: "낙폭 회복", value: result.metrics.other.drawdown_recovery > 0 ? `${result.metrics.other.drawdown_recovery.toFixed(0)}일` : "-" },
                  ]}
                />
              </div>

              {/* 거래 내역 */}
              {result.trades && result.trades.length > 0 && (
                <div className="card">
                  <button
                    onClick={() => setTradesOpen((o) => !o)}
                    className="w-full flex items-center justify-between text-sm font-medium text-slate-700 dark:text-slate-300"
                  >
                    <span>거래 내역 ({result.trades.length}건)</span>
                    <ChevronDown className={cn("w-4 h-4 transition-transform", tradesOpen && "rotate-180")} />
                  </button>
                  {tradesOpen && (
                    <div className="mt-3 overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="text-left text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-700">
                            <th className="pb-2 pr-4 font-medium">시간</th>
                            <th className="pb-2 pr-4 font-medium">종목</th>
                            <th className="pb-2 pr-4 font-medium">방향</th>
                            <th className="pb-2 pr-4 text-right font-medium">수량</th>
                            <th className="pb-2 text-right font-medium">체결가</th>
                          </tr>
                        </thead>
                        <tbody>
                          {result.trades.map((trade, i) => (
                            <tr key={i} className="border-b border-slate-100 dark:border-slate-800 last:border-0">
                              <td className="py-1.5 pr-4 text-slate-500 dark:text-slate-400 text-xs">
                                {trade.time ? new Date(trade.time).toLocaleDateString("ko-KR") : "-"}
                              </td>
                              <td className="py-1.5 pr-4 font-mono">{trade.symbol}</td>
                              <td className={cn("py-1.5 pr-4 font-medium", trade.direction === "Buy" ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400")}>
                                {trade.direction === "Buy" ? "매수" : "매도"}
                              </td>
                              <td className="py-1.5 pr-4 text-right">{trade.quantity.toLocaleString()}주</td>
                              <td className="py-1.5 text-right font-mono">{Math.round(trade.price).toLocaleString()}원</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="card flex flex-col items-center justify-center py-16 text-slate-400">
              <BarChart3 className="w-16 h-16 mb-4 opacity-30" />
              <p className="text-lg font-medium">결과 없음</p>
              <p className="text-sm mt-1">백테스트를 실행하면 결과가 표시됩니다</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
