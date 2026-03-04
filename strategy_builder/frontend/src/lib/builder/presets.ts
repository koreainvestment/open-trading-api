/**
 * 기본 전략 프리셋 (BuilderState 형식)
 */

import type { BuilderState } from "@/types/builder";

export interface PresetStrategy {
  id: string;
  name: string;
  description: string;
  category: string;
  state: BuilderState;
}

export const PRESET_STRATEGIES: PresetStrategy[] = [
  {
    id: "golden_cross",
    name: "골든크로스",
    description: "단기 MA가 장기 MA를 상향 돌파 시 매수",
    category: "추세추종",
    state: {
      metadata: {
        id: "golden_cross",
        name: "골든크로스",
        description: "단기 MA가 장기 MA를 상향 돌파 시 매수",
        category: "trend",
        tags: ["ma", "crossover", "trend"],
        author: "KIS",
      },
      indicators: [
        { id: "sma_1", indicatorId: "sma", alias: "sma_fast", params: { period: 5 }, output: "value" },
        { id: "sma_2", indicatorId: "sma", alias: "sma_slow", params: { period: 20 }, output: "value" },
      ],
      entry: {
        logic: "AND",
        conditions: [
          {
            id: "entry_1",
            left: { type: "indicator", indicatorAlias: "sma_fast", indicatorOutput: "value" },
            operator: "cross_above",
            right: { type: "indicator", indicatorAlias: "sma_slow", indicatorOutput: "value" },
          },
        ],
      },
      exit: {
        logic: "AND",
        conditions: [
          {
            id: "exit_1",
            left: { type: "indicator", indicatorAlias: "sma_fast", indicatorOutput: "value" },
            operator: "cross_below",
            right: { type: "indicator", indicatorAlias: "sma_slow", indicatorOutput: "value" },
          },
        ],
      },
      risk: {
        stopLoss: { enabled: true, percent: 5 },
        takeProfit: { enabled: false, percent: 10 },
        trailingStop: { enabled: false, percent: 3 },
      },
    },
  },
  {
    id: "momentum",
    name: "모멘텀",
    description: "N일 수익률 기준 매수/매도",
    category: "추세추종",
    state: {
      metadata: {
        id: "momentum",
        name: "모멘텀",
        description: "N일 수익률 기준 매수/매도",
        category: "momentum",
        tags: ["momentum", "rate_of_change"],
        author: "KIS",
      },
      indicators: [
        { id: "roc_1", indicatorId: "roc", alias: "roc_1", params: { period: 60 }, output: "value" },
      ],
      entry: {
        logic: "AND",
        conditions: [
          {
            id: "entry_1",
            left: { type: "indicator", indicatorAlias: "roc_1", indicatorOutput: "value" },
            operator: "greater_than",
            right: { type: "value", value: 30 },
          },
        ],
      },
      exit: {
        logic: "OR",
        conditions: [
          {
            id: "exit_1",
            left: { type: "indicator", indicatorAlias: "roc_1", indicatorOutput: "value" },
            operator: "less_than",
            right: { type: "value", value: -20 },
          },
        ],
      },
      risk: {
        stopLoss: { enabled: true, percent: 5 },
        takeProfit: { enabled: false, percent: 10 },
        trailingStop: { enabled: false, percent: 3 },
      },
    },
  },
  {
    id: "disparity",
    name: "이격도",
    description: "MA 대비 이격 기준 매수/매도",
    category: "역추세",
    state: {
      metadata: {
        id: "disparity",
        name: "이격도",
        description: "MA 대비 이격 기준 매수/매도",
        category: "reversal",
        tags: ["disparity", "ma", "reversal"],
        author: "KIS",
      },
      indicators: [
        { id: "sma_1", indicatorId: "sma", alias: "sma_1", params: { period: 20 }, output: "value" },
      ],
      entry: {
        logic: "AND",
        conditions: [
          {
            id: "entry_1",
            left: { type: "price", priceField: "close" },
            operator: "less_than",
            right: { type: "indicator", indicatorAlias: "sma_1", indicatorOutput: "value" },
          },
        ],
      },
      exit: {
        logic: "OR",
        conditions: [
          {
            id: "exit_1",
            left: { type: "price", priceField: "close" },
            operator: "greater_than",
            right: { type: "indicator", indicatorAlias: "sma_1", indicatorOutput: "value" },
          },
        ],
      },
      risk: {
        stopLoss: { enabled: true, percent: 5 },
        takeProfit: { enabled: true, percent: 10 },
        trailingStop: { enabled: false, percent: 3 },
      },
    },
  },
  {
    id: "mean_reversion",
    name: "평균회귀",
    description: "N일 평균 대비 이탈 시 매매",
    category: "역추세",
    state: {
      metadata: {
        id: "mean_reversion",
        name: "평균회귀",
        description: "N일 평균 대비 이탈 시 매매",
        category: "reversal",
        tags: ["mean_reversion", "reversal"],
        author: "KIS",
      },
      indicators: [
        { id: "sma_1", indicatorId: "sma", alias: "sma_1", params: { period: 5 }, output: "value" },
      ],
      entry: {
        logic: "AND",
        conditions: [
          {
            id: "entry_1",
            left: { type: "price", priceField: "close" },
            operator: "less_than",
            right: { type: "indicator", indicatorAlias: "sma_1", indicatorOutput: "value" },
          },
        ],
      },
      exit: {
        logic: "OR",
        conditions: [
          {
            id: "exit_1",
            left: { type: "price", priceField: "close" },
            operator: "greater_than",
            right: { type: "indicator", indicatorAlias: "sma_1", indicatorOutput: "value" },
          },
        ],
      },
      risk: {
        stopLoss: { enabled: true, percent: 3 },
        takeProfit: { enabled: true, percent: 3 },
        trailingStop: { enabled: false, percent: 3 },
      },
    },
  },
  {
    id: "trend_filter",
    name: "추세 필터",
    description: "MA 위/아래 추세 방향 매매",
    category: "추세추종",
    state: {
      metadata: {
        id: "trend_filter",
        name: "추세 필터",
        description: "MA 위/아래 추세 방향 매매",
        category: "trend",
        tags: ["trend", "ma", "filter"],
        author: "KIS",
      },
      indicators: [
        { id: "sma_1", indicatorId: "sma", alias: "sma_1", params: { period: 60 }, output: "value" },
      ],
      entry: {
        logic: "AND",
        conditions: [
          {
            id: "entry_1",
            left: { type: "price", priceField: "close" },
            operator: "cross_above",
            right: { type: "indicator", indicatorAlias: "sma_1", indicatorOutput: "value" },
          },
        ],
      },
      exit: {
        logic: "AND",
        conditions: [
          {
            id: "exit_1",
            left: { type: "price", priceField: "close" },
            operator: "cross_below",
            right: { type: "indicator", indicatorAlias: "sma_1", indicatorOutput: "value" },
          },
        ],
      },
      risk: {
        stopLoss: { enabled: true, percent: 5 },
        takeProfit: { enabled: false, percent: 10 },
        trailingStop: { enabled: false, percent: 3 },
      },
    },
  },
  {
    id: "volatility_breakout",
    name: "변동성 돌파",
    description: "변동성 최저에서 돌파 시 매수",
    category: "변동성",
    state: {
      metadata: {
        id: "volatility_breakout",
        name: "변동성 돌파",
        description: "변동성 최저에서 돌파 시 매수",
        category: "volatility",
        tags: ["volatility", "breakout", "atr"],
        author: "KIS",
      },
      indicators: [
        { id: "atr_1", indicatorId: "atr", alias: "atr_1", params: { period: 14 }, output: "value" },
      ],
      entry: {
        logic: "AND",
        conditions: [
          {
            id: "entry_1",
            left: { type: "price", priceField: "close" },
            operator: "greater_than",
            right: { type: "price", priceField: "open" },
          },
        ],
      },
      exit: {
        logic: "OR",
        conditions: [
          {
            id: "exit_1",
            left: { type: "price", priceField: "close" },
            operator: "less_than",
            right: { type: "price", priceField: "open" },
          },
        ],
      },
      risk: {
        stopLoss: { enabled: true, percent: 3 },
        takeProfit: { enabled: false, percent: 10 },
        trailingStop: { enabled: false, percent: 3 },
      },
    },
  },
];

export default PRESET_STRATEGIES;
