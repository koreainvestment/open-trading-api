"use client";

import { useMemo } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  ReferenceDot,
} from "recharts";
import { cn, formatCurrency, formatPercent } from "@/lib/utils";

/* eslint-disable @typescript-eslint/no-explicit-any */

/** Chart color constants */
export const CHART_COLORS = {
  strategy: "#245bee",
  benchmark: "#f59e0b",
  buy: "#22c55e",
  sell: "#ef4444",
  drawdown: "#ef4444",
  grid: "#e2e8f0",
  reference: "#94a3b8",
} as const;

export interface ChartDataPoint {
  date: string;
  value: number;
  returnPct: number;
  benchmarkPct: number | null;
  benchmark: number | null;
  drawdown: number;
}

export interface TradeMarker {
  date: string;
  type: "buy" | "sell";
  price: number;
}

/** Grouped marker for rendering (same date trades aggregated) */
interface GroupedMarker {
  date: string;
  type: "buy" | "sell";
  count: number;
}

interface EquityChartProps {
  chartData: ChartDataPoint[];
  tradeMarkers: TradeMarker[];
  initialCapital: number;
  yAxisDomain: [number, number];
}

/** Format axis values in Korean units (억/만) */
function formatAxisValue(v: number): string {
  if (v >= 100_000_000) return `${(v / 100_000_000).toFixed(1)}억`;
  return `${Math.round(v / 10_000).toLocaleString()}만`;
}

/** Format drawdown axis (%) */
function formatDrawdownAxis(v: number): string {
  return `${v.toFixed(0)}%`;
}

/** Custom tooltip for the equity chart */
function EquityTooltipInner({
  active,
  payload,
  tradeMarkers,
}: {
  active?: boolean;
  payload?: readonly any[];
  tradeMarkers: TradeMarker[];
}) {
  if (!active || !payload?.length) return null;

  const data = payload[0].payload as ChartDataPoint;
  const trades = tradeMarkers.filter((t) => t.date === data.date);
  const excessReturn =
    data.benchmarkPct !== null ? data.returnPct - data.benchmarkPct : null;

  return (
    <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-3 shadow-lg min-w-[200px]">
      <p className="text-xs text-slate-500 font-medium mb-2 border-b border-slate-100 dark:border-slate-700 pb-1">
        {data.date}
      </p>

      {/* Strategy */}
      <div className="flex items-center gap-2 mb-1">
        <span
          className="w-2 h-2 rounded-full flex-shrink-0"
          style={{ backgroundColor: CHART_COLORS.strategy }}
        />
        <span className="text-xs text-slate-500">전략</span>
        <span className="text-xs font-semibold text-slate-900 dark:text-white ml-auto tabular-nums">
          {formatCurrency(data.value)}
        </span>
      </div>

      {/* Benchmark */}
      {data.benchmark !== null && (
        <div className="flex items-center gap-2 mb-1">
          <span
            className="w-2 h-2 rounded-full flex-shrink-0"
            style={{ backgroundColor: CHART_COLORS.benchmark }}
          />
          <span className="text-xs text-slate-500">KOSPI</span>
          <span className="text-xs font-semibold text-slate-900 dark:text-white ml-auto tabular-nums">
            {formatCurrency(data.benchmark)}
          </span>
        </div>
      )}

      {/* Returns */}
      <div className="mt-2 pt-1.5 border-t border-slate-100 dark:border-slate-700 space-y-0.5">
        <div className="flex justify-between">
          <span className="text-xs text-slate-500">수익률</span>
          <span
            className={cn(
              "text-xs font-medium tabular-nums",
              data.returnPct >= 0 ? "text-profit" : "text-loss"
            )}
          >
            {formatPercent(data.returnPct)}
          </span>
        </div>
        {data.benchmarkPct !== null && (
          <div className="flex justify-between">
            <span className="text-xs text-slate-500">KOSPI</span>
            <span className="text-xs text-slate-400 tabular-nums">
              {formatPercent(data.benchmarkPct)}
            </span>
          </div>
        )}
        {excessReturn !== null && (
          <div className="flex justify-between">
            <span className="text-xs text-slate-500">초과수익</span>
            <span
              className={cn(
                "text-xs font-bold tabular-nums",
                excessReturn >= 0 ? "text-profit" : "text-loss"
              )}
            >
              {formatPercent(excessReturn)}
            </span>
          </div>
        )}
        {data.drawdown < 0 && (
          <div className="flex justify-between">
            <span className="text-xs text-slate-500">낙폭</span>
            <span className="text-xs text-loss tabular-nums">
              {data.drawdown.toFixed(2)}%
            </span>
          </div>
        )}
      </div>

      {/* Trade markers */}
      {trades.length > 0 && (
        <div className="mt-2 pt-1.5 border-t border-slate-100 dark:border-slate-700">
          {trades.map((trade, i) => (
            <div key={i} className="flex items-center gap-1.5">
              <span
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{
                  backgroundColor:
                    trade.type === "buy"
                      ? CHART_COLORS.buy
                      : CHART_COLORS.sell,
                }}
              />
              <span className="text-xs font-medium">
                {trade.type === "buy" ? "매수" : "매도"}
              </span>
              <span className="text-xs text-slate-400 ml-auto tabular-nums">
                {formatCurrency(trade.price)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/** Drawdown tooltip */
function DrawdownTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: readonly any[];
}) {
  if (!active || !payload?.length) return null;
  const data = payload[0].payload as ChartDataPoint;

  return (
    <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-2 shadow-lg">
      <p className="text-xs text-slate-500">{data.date}</p>
      <p className="text-sm font-semibold text-loss tabular-nums">
        {data.drawdown.toFixed(2)}%
      </p>
    </div>
  );
}

/** Chart legend */
function ChartLegend({
  hasBenchmark,
  hasTrades,
}: {
  hasBenchmark: boolean;
  hasTrades: boolean;
}) {
  return (
    <div className="flex items-center gap-4 flex-wrap">
      <div className="flex items-center gap-1.5">
        <span
          className="w-3 h-0.5 rounded-full"
          style={{ backgroundColor: CHART_COLORS.strategy }}
        />
        <span className="text-xs text-slate-500">전략</span>
      </div>
      {hasBenchmark && (
        <div className="flex items-center gap-1.5">
          <span
            className="w-3 h-0.5 rounded-full"
            style={{ backgroundColor: CHART_COLORS.benchmark }}
          />
          <span className="text-xs text-slate-500">KOSPI</span>
        </div>
      )}
      {hasTrades && (
        <>
          <div className="flex items-center gap-1.5">
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: CHART_COLORS.buy }}
            />
            <span className="text-xs text-slate-500">매수</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: CHART_COLORS.sell }}
            />
            <span className="text-xs text-slate-500">매도</span>
          </div>
        </>
      )}
    </div>
  );
}

export function EquityChart({
  chartData,
  tradeMarkers,
  initialCapital,
  yAxisDomain,
}: EquityChartProps) {
  const hasBenchmark = useMemo(
    () => chartData.some((d) => d.benchmark !== null),
    [chartData]
  );
  const hasTrades = tradeMarkers.length > 0;

  // Group markers by (date, type) → count per group, split buy/sell on same date
  const groupedMarkers: GroupedMarker[] = useMemo(() => {
    const map = new Map<string, number>();
    for (const m of tradeMarkers) {
      const key = `${m.date}|${m.type}`;
      map.set(key, (map.get(key) || 0) + 1);
    }
    return Array.from(map.entries()).map(([key, count]) => {
      const [date, type] = key.split("|");
      return { date, type: type as "buy" | "sell", count };
    });
  }, [tradeMarkers]);

  const xInterval = useMemo(
    () => Math.max(0, Math.floor(chartData.length / 8) - 1),
    [chartData.length]
  );

  /** Drawdown Y-axis domain (always negative) */
  const drawdownDomain = useMemo(() => {
    const minDD = Math.min(...chartData.map((d) => d.drawdown));
    const padding = Math.abs(minDD) * 0.15;
    return [minDD - padding, 0];
  }, [chartData]);

  // Stable tooltip component that captures tradeMarkers via closure
  const EquityTooltip = useMemo(() => {
    const Comp = (props: any) => (
      <EquityTooltipInner {...props} tradeMarkers={tradeMarkers} />
    );
    Comp.displayName = "EquityTooltip";
    return Comp;
  }, [tradeMarkers]);

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-slate-900 dark:text-white">
          자산 추이
        </h3>
        <ChartLegend hasBenchmark={hasBenchmark} hasTrades={hasTrades} />
      </div>

      {/* Main equity chart */}
      <div className="h-[380px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={chartData}
            margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient id="gradStrategy" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor={CHART_COLORS.strategy}
                  stopOpacity={0.3}
                />
                <stop
                  offset="95%"
                  stopColor={CHART_COLORS.strategy}
                  stopOpacity={0}
                />
              </linearGradient>
              <linearGradient id="gradBenchmark" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor={CHART_COLORS.benchmark}
                  stopOpacity={0.2}
                />
                <stop
                  offset="95%"
                  stopColor={CHART_COLORS.benchmark}
                  stopOpacity={0}
                />
              </linearGradient>
            </defs>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke={CHART_COLORS.grid}
            />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 10 }}
              tickFormatter={(v: string) => v.slice(5)}
              interval={xInterval}
            />
            <YAxis
              tick={{ fontSize: 10 }}
              tickFormatter={formatAxisValue}
              domain={yAxisDomain}
              width={70}
            />
            <Tooltip content={EquityTooltip} />
            <ReferenceLine
              y={initialCapital}
              stroke={CHART_COLORS.reference}
              strokeDasharray="3 3"
              label={{
                value: "초기자본",
                position: "insideTopRight",
                fontSize: 10,
                fill: CHART_COLORS.reference,
              }}
            />
            {/* KOSPI benchmark (behind) */}
            {hasBenchmark && (
              <Area
                type="monotone"
                dataKey="benchmark"
                stroke={CHART_COLORS.benchmark}
                fill="url(#gradBenchmark)"
                name="KOSPI"
                connectNulls
              />
            )}
            {/* Strategy equity (front) */}
            <Area
              type="monotone"
              dataKey="value"
              stroke={CHART_COLORS.strategy}
              fill="url(#gradStrategy)"
              name="전략"
            />
            {/* Buy/Sell markers (grouped by date+type) */}
            {groupedMarkers.map((marker, idx) => {
              const point = chartData.find((d) => d.date === marker.date);
              if (!point) return null;

              // Check if both buy and sell exist on the same date
              const hasBoth = groupedMarkers.some(
                (m) => m.date === marker.date && m.type !== marker.type
              );
              // Offset y when both types on same date (buy slightly above, sell slightly below)
              const yRange = yAxisDomain[1] - yAxisDomain[0];
              const yOffset = hasBoth
                ? (marker.type === "buy" ? -1 : 1) * yRange * 0.02
                : 0;
              // Scale dot size by trade count (5 base, +1.5 per extra, max 10)
              const r = Math.min(5 + (marker.count - 1) * 1.5, 10);

              return (
                <ReferenceDot
                  key={`${marker.date}-${marker.type}-${idx}`}
                  x={marker.date}
                  y={point.value + yOffset}
                  r={r}
                  fill={
                    marker.type === "buy"
                      ? CHART_COLORS.buy
                      : CHART_COLORS.sell
                  }
                  stroke="#fff"
                  strokeWidth={2}
                  label={
                    marker.count > 1
                      ? {
                          value: `${marker.count}`,
                          position: "top",
                          fontSize: 9,
                          fontWeight: 600,
                          fill:
                            marker.type === "buy"
                              ? CHART_COLORS.buy
                              : CHART_COLORS.sell,
                        }
                      : undefined
                  }
                />
              );
            })}
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Drawdown subchart */}
      {chartData.some((d) => d.drawdown < 0) && (
        <>
          <div className="flex items-center justify-between mt-4 mb-2">
            <h4 className="text-xs font-medium text-slate-500">Drawdown</h4>
          </div>
          <div className="h-[120px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={chartData}
                margin={{ top: 0, right: 10, left: 0, bottom: 0 }}
              >
                <defs>
                  <linearGradient
                    id="gradDrawdown"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop
                      offset="5%"
                      stopColor={CHART_COLORS.drawdown}
                      stopOpacity={0.4}
                    />
                    <stop
                      offset="95%"
                      stopColor={CHART_COLORS.drawdown}
                      stopOpacity={0.05}
                    />
                  </linearGradient>
                </defs>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke={CHART_COLORS.grid}
                  vertical={false}
                />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 9 }}
                  tickFormatter={(v: string) => v.slice(5)}
                  interval={xInterval}
                />
                <YAxis
                  tick={{ fontSize: 9 }}
                  tickFormatter={formatDrawdownAxis}
                  domain={drawdownDomain}
                  width={50}
                />
                <Tooltip content={DrawdownTooltip} />
                <ReferenceLine y={0} stroke={CHART_COLORS.grid} />
                <Area
                  type="monotone"
                  dataKey="drawdown"
                  stroke={CHART_COLORS.drawdown}
                  fill="url(#gradDrawdown)"
                  strokeWidth={1.5}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
}
