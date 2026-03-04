/**
 * YAML Import → BuilderState Converter
 *
 * Parses a .kis.yaml string and converts it into a BuilderState
 * that can be loaded directly into the visual strategy builder.
 */

import yaml from "js-yaml";
import type {
  BuilderState,
  BuilderIndicator,
  BuilderCondition,
  BuilderConditionGroup,
  ConditionOperator,
  ConditionOperand,
  RiskManagement,
} from "@/types/builder";
import type { KisStrategyFile, YamlConditionDef } from "@/types/file";
import { getIndicatorById, CANDLESTICK_PATTERNS } from "./constants";

// Candlestick pattern IDs for fast lookup
const CANDLESTICK_IDS = new Set(CANDLESTICK_PATTERNS.map((p) => p.id));

// Price fields recognized as price operands
const PRICE_FIELDS = new Set(["close", "open", "high", "low"]);

/**
 * Maps YAML operator strings (short/long forms) to BuilderState ConditionOperator.
 * Covers both abbreviated forms (gt, lt) and full names (greater_than, crosses_above).
 */
const YAML_TO_OPERATOR: Record<string, ConditionOperator> = {
  gt: "greater_than",
  lt: "less_than",
  gte: "greater_equal",
  lte: "less_equal",
  eq: "equals",
  crosses_above: "cross_above",
  crosses_below: "cross_below",
  cross_above: "cross_above",
  cross_below: "cross_below",
  greater_than: "greater_than",
  less_than: "less_than",
  greater_equal: "greater_equal",
  less_equal: "less_equal",
  equals: "equals",
};

/**
 * Parse a YAML string into a fully populated BuilderState.
 * Throws on invalid YAML or missing required fields.
 * Returns { state, warnings } — warnings contains messages about auto-corrections.
 */
export function parseYamlToBuilderState(yamlString: string): {
  state: BuilderState;
  warnings: string[];
} {
  const parsed = yaml.load(yamlString) as KisStrategyFile;

  if (!parsed || typeof parsed !== "object") {
    throw new Error("YAML 파싱 결과가 유효하지 않습니다");
  }

  if (!parsed.strategy) {
    throw new Error("strategy 섹션이 필요합니다");
  }

  const warnings: string[] = [];
  const { indicators, renamedAliases } = convertIndicators(parsed);
  if (renamedAliases.length > 0) {
    const detail = renamedAliases.map((r) => `${r.from} → ${r.to}`).join(", ");
    warnings.push(`중복 별칭 자동 보정: ${detail}`);
  }
  const indicatorAliases = new Set(indicators.map((ind) => ind.alias));
  const candlestickAliases = new Set(
    indicators.filter((ind) => CANDLESTICK_IDS.has(ind.indicatorId)).map((ind) => ind.alias)
  );

  const entry = convertConditionGroup(
    parsed.strategy.entry,
    indicatorAliases,
    candlestickAliases
  );
  const exit = convertConditionGroup(
    parsed.strategy.exit,
    indicatorAliases,
    candlestickAliases
  );
  const risk = convertRisk(parsed.risk);

  const metadata = {
    id: parsed.strategy.id || "",
    name: parsed.metadata?.name || parsed.strategy.id || "imported_strategy",
    description: parsed.metadata?.description || "",
    category: parsed.strategy.category || "custom",
    tags: parsed.metadata?.tags || [],
    author: parsed.metadata?.author || "user",
  };

  return { state: { metadata, indicators, entry, exit, risk }, warnings };
}

/**
 * Convert YAML indicators + candlesticks into BuilderIndicator[].
 * Duplicate aliases are auto-corrected with _2, _3 ... suffix.
 * Returns { indicators, renamedAliases } so callers can show toast notifications.
 */
function convertIndicators(parsed: KisStrategyFile): {
  indicators: BuilderIndicator[];
  renamedAliases: Array<{ from: string; to: string }>;
} {
  const result: BuilderIndicator[] = [];
  const seenAliases = new Set<string>();
  const aliasCounts: Record<string, number> = {};
  const renamedAliases: Array<{ from: string; to: string }> = [];

  const resolveAlias = (raw: string): string => {
    if (!seenAliases.has(raw)) {
      seenAliases.add(raw);
      return raw;
    }
    let n = 2;
    while (seenAliases.has(`${raw}_${n}`)) n++;
    const resolved = `${raw}_${n}`;
    seenAliases.add(resolved);
    renamedAliases.push({ from: raw, to: resolved });
    return resolved;
  };

  // Regular indicators
  const yamlIndicators = parsed.strategy.indicators || [];
  for (let i = 0; i < yamlIndicators.length; i++) {
    const ind = yamlIndicators[i];
    const indicatorId = ind.id;
    aliasCounts[indicatorId] = (aliasCounts[indicatorId] || 0) + 1;
    const rawAlias = ind.alias || `${indicatorId}_${aliasCounts[indicatorId]}`;
    const alias = resolveAlias(rawAlias);

    const def = getIndicatorById(indicatorId);
    const defaultOutput = def?.defaultOutput || "value";

    result.push({
      id: `${indicatorId}_${Date.now()}_${i}`,
      indicatorId,
      alias,
      // YAML에 name 필드가 있으면 displayName으로 복원
      ...((ind as { name?: string }).name ? { displayName: (ind as { name?: string }).name } : {}),
      params: ind.params || {},
      output: ind.output || defaultOutput,
    });
  }

  // Candlestick patterns
  const yamlCandlesticks = parsed.strategy.candlesticks || [];
  for (let i = 0; i < yamlCandlesticks.length; i++) {
    const cs = yamlCandlesticks[i];
    const indicatorId = cs.id;
    const rawAlias = cs.alias || `${indicatorId}_${i + 1}`;
    const alias = resolveAlias(rawAlias);

    result.push({
      id: `${indicatorId}_${Date.now()}_cs_${i}`,
      indicatorId,
      alias,
      params: {},
      output: "value",
    });
  }

  return { indicators: result, renamedAliases };
}

/**
 * Convert a YAML condition group (entry/exit) into BuilderConditionGroup.
 */
function convertConditionGroup(
  group: KisStrategyFile["strategy"]["entry"] | undefined,
  indicatorAliases: Set<string>,
  candlestickAliases: Set<string>
): BuilderConditionGroup {
  if (!group) {
    return { logic: "AND", conditions: [] };
  }

  const conditions: BuilderCondition[] = (group.conditions || []).map(
    (cond, i) => convertCondition(cond, i, indicatorAliases, candlestickAliases)
  );

  return {
    logic: group.logic || "AND",
    conditions,
  };
}

/**
 * Convert a single YAML condition into a BuilderCondition.
 */
function convertCondition(
  cond: YamlConditionDef,
  index: number,
  indicatorAliases: Set<string>,
  candlestickAliases: Set<string>
): BuilderCondition {
  const id = `cond_${Date.now()}_${index}`;

  // Candlestick condition (explicit candlestick field)
  if (cond.candlestick) {
    return {
      id,
      left: { type: "indicator" },
      operator: "equals",
      right: { type: "value", value: 1 },
      isCandlestick: true,
      candlestickAlias: cond.candlestick,
      candlestickSignal: cond.signal || "detected",
    };
  }

  // Legacy candlestick detection: indicator alias is in the candlestick set
  if (cond.indicator && candlestickAliases.has(cond.indicator)) {
    return {
      id,
      left: { type: "indicator" },
      operator: "equals",
      right: { type: "value", value: 1 },
      isCandlestick: true,
      candlestickAlias: cond.indicator,
      candlestickSignal: "detected",
    };
  }

  // Regular indicator condition
  const operator = resolveOperator(cond.operator);
  const left = resolveLeftOperand(cond);
  const right = resolveRightOperand(cond, indicatorAliases);

  return { id, left, operator, right };
}

/**
 * Resolve a YAML operator string to a ConditionOperator.
 */
function resolveOperator(op: string | undefined): ConditionOperator {
  if (!op) return "greater_than";
  return YAML_TO_OPERATOR[op] || "greater_than";
}

/**
 * Build the left operand from a YAML condition.
 */
function resolveLeftOperand(cond: YamlConditionDef): ConditionOperand {
  const indicator = cond.indicator || "";

  if (PRICE_FIELDS.has(indicator)) {
    return {
      type: "price",
      priceField: indicator as "close" | "open" | "high" | "low",
    };
  }

  return {
    type: "indicator",
    indicatorAlias: indicator,
    indicatorOutput: cond.output || "value",
  };
}

/**
 * Build the right operand from a YAML condition's compare_to field.
 */
function resolveRightOperand(
  cond: YamlConditionDef,
  indicatorAliases: Set<string>
): ConditionOperand {
  const compareTo = cond.compare_to;

  // No compare_to → default value 0
  if (compareTo === undefined || compareTo === null) {
    return { type: "value", value: 0 };
  }

  // Numeric value
  if (typeof compareTo === "number") {
    return { type: "value", value: compareTo };
  }

  // String compare_to
  if (typeof compareTo === "string") {
    // Price field
    if (PRICE_FIELDS.has(compareTo)) {
      return {
        type: "price",
        priceField: compareTo as "close" | "open" | "high" | "low",
      };
    }

    // Known indicator alias
    if (indicatorAliases.has(compareTo)) {
      return {
        type: "indicator",
        indicatorAlias: compareTo,
        indicatorOutput: cond.compare_output || "value",
      };
    }

    // Numeric string (e.g. "30", "70.5")
    const num = parseFloat(compareTo);
    if (!isNaN(num)) {
      return { type: "value", value: num };
    }

    // Fallback: treat as indicator alias (best effort for unknown aliases)
    return {
      type: "indicator",
      indicatorAlias: compareTo,
      indicatorOutput: cond.compare_output || "value",
    };
  }

  return { type: "value", value: 0 };
}

/**
 * Convert YAML risk section into RiskManagement.
 */
function convertRisk(risk: KisStrategyFile["risk"]): RiskManagement {
  return {
    stopLoss: {
      enabled: risk?.stop_loss?.enabled ?? false,
      percent: risk?.stop_loss?.percent ?? 5,
    },
    takeProfit: {
      enabled: risk?.take_profit?.enabled ?? false,
      percent: risk?.take_profit?.percent ?? 10,
    },
    trailingStop: {
      enabled: risk?.trailing_stop?.enabled ?? false,
      percent: risk?.trailing_stop?.percent ?? 3,
    },
  };
}
