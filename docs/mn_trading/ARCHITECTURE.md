# MN Trading Architecture (SSOT)

## Purpose
- Provide a single source of truth for the trading research and execution pipeline.
- Keep design, data flow, and entry points reproducible and auditable.

## Architecture Status and Promotion Policy

This architecture follows a two-phase lifecycle: Planned Architecture and Active Architecture.

### Planned Architecture (Current)
- The structure is a working design hypothesis.
- Directory layout, module boundaries, and responsibilities may change.
- Refactors or relocations are allowed; documentation updates remain mandatory.
- Migration requirements are minimal during this phase.

Allowed activities:
- Create, rename, or remove modules.
- Adjust data flow between strategy, LLM, and execution layers.
- Introduce or remove experimental LLM components.
- Run aggressive experiments in VPS (demo) environment.

### Promotion Criteria to Active Architecture
Promotion is allowed only when all conditions are met:
1) End-to-End Reproducibility
   - Full pipeline (data -> signals -> state -> execution routing) runs in VPS mode.
   - Re-runs produce equivalent outputs (signals, state transitions, metrics).
2) LLM Safety Validation
   - temperature=0, schema validation, invalid output => NO-OP.
   - Comparison completed: rule-only, rule+LLM gate, rule+random intervention.
   - 3-mode comparison artifacts recorded under out/mn_trading/experiments/.
   - Results recorded under out/ and summarized.
3) Operational Entry Points Defined
   - At least one CLI entry point is documented (example: run_wave_3x3.py).
   - Inputs, outputs, and side effects are described.
4) Documentation Completeness
   - This document reflects structure, responsibilities, data flow, and env switching.
   - CHANGELOG includes a promotion entry with date and rationale.

### Active Architecture (Future State)
- ARCHITECTURE.md is a strict SSOT.
- Structural changes require: documentation update first, CHANGELOG entry, code changes.
- Codex must not alter architecture implicitly.
- Any undocumented deviation is an error.

### Explicit Non-Goals
- Promotion does not imply readiness for live trading.
- Production execution is out of scope unless explicitly approved.
- Financial risk controls are evaluated independently from architecture status.

## Out of Scope
- Live trading execution and broker-side order routing logic.
- Account secrets, keys, or any sensitive identifiers.

## Directory Map
- data/: input OHLCV CSVs and derived datasets.
- out/: analysis outputs, reports, and run artifacts.
- out/mn_trading/experiments/: reproducible experiment artifacts (rule/random/llm).
- out/mn_trading/datasets/: cut-date datasets for experiments.
- tools/: CLI scripts for data fetch, analysis, and signal generation.
- docs/mn_trading/: documentation (this SSOT set).
- mn_trading/: planned package skeleton for future execution/runtime logic.
- examples_llm/: upstream sample integrations (read-only reference).

## Data Flow (Current)
1. OHLCV daily data -> indicators (BB20/50, ATR, volume stats).
2. Zones/Signals -> state machine and hypothesis tests.
3. Reports -> out/ for review and iteration.
4. Experiments -> tools/backtest_signals.py -> KPI summary (trades, win_rate, expectancy_R, max_dd).
5. KPI parsing is best-effort and records explicit notes when placeholders are used.
6. Experiments normalize backtest inputs by shifting signal dates -1 bar when signals land on the dataset last date.
7. Backtest signals normalize dates to YYYY-MM-DD to match daily CSV parsing.
8. Walk-forward experiments aggregate daily signals across N trade dates and reuse rule signals for random/llm (no extra engine runs).
9. Reuse-exp-id replays gate variants from cached rule signals and blocks engine execution.
10. --gate-mode affects mode=llm signal generation only; mode=rule/random remain unchanged.
11. LLM-gate is a wave position classifier (BB50 lower-zone filter) with row-level BUY_* calls.
12. Gate strategies include rule-gate (deterministic) and llm-gate (NO-OP fallback) via apply_gate_to_signals.
13. LLM-gate computes bb50_position/bb20_cross/wave_state from daily close (SMA20/50), not action-derived fields.
14. LLM-gate normalizes stock codes to 6-digit strings before joining daily data.
15. LLM-gate policy options (strong/A/B/C) tune block aggressiveness and log mismatch counts; default is policy C.
16. Gate layering is SRZ execution gate (zones CSV C_low/C_high) then LLM-gate (policy C).
17. Experiments can use cut-date datasets because wave_3x3_engine has no --asof support.

## Data Flow (Planned/Optional)
- Indicators/Signals -> LLM router -> executor (NO-OP fallback).

## Modules and Responsibilities
- Data fetch: tools/fetch_daily_ohlcv.py
- Signal generation: tools/signal_bb_volume.py, tools/zone_abc_from_volume_wave.py
- State machine/analysis: tools/bb_state_machine.py, tools/analyze_state_2ndbattery.py
- Backtests/hypothesis: tools/backtest_signals.py, tools/bb50_brake_test.py, tools/bb50_brake_compare.py
- Regime/volume/wave: tools/regime_shift_proof.py, tools/vp_wave_accum_report.py, tools/bb50_nontouch_regime.py
- Execution signals: tools/wave_3x3_engine.py
- Sweep/compare: tools/zone_abc_sweep_runs.py, tools/zone_abc_compare_runs.py
- mn_trading adapter layer: mn_trading/src/mn_trading/strategy/wave_3x3 (subprocess wrapper for tools/wave_3x3_engine.py)
- mn_trading experiments: mn_trading/src/mn_trading/experiments (rule/random/llm runs + metrics)
- experiments backtest adapter: mn_trading/src/mn_trading/experiments/backtest_adapter.py (subprocess tools/backtest_signals.py)
- gate strategies: mn_trading/src/mn_trading/gates (rule-gate vs llm-gate)

## Entry Points
- Data: python tools/fetch_daily_ohlcv.py --code <CODE> --start YYYYMMDD --end YYYYMMDD
- Signals: python tools/zone_abc_from_volume_wave.py --codes <CODES>
- State: python tools/analyze_state_2ndbattery.py --demo --codes <CODES>
- 3x3 engine: python tools/wave_3x3_engine.py --codes <CODES> --zones-csv <PATH>
- Placeholder CLI: python mn_trading/src/mn_trading/cli/run_wave_3x3.py --codes <CODES>
- mn_trading CLI: PYTHONPATH=mn_trading/src python mn_trading/src/mn_trading/cli/run_wave_3x3.py --codes <CODES> --zones-csv <PATH> [--dry-run]
- experiments CLI: PYTHONPATH=mn_trading/src python mn_trading/src/mn_trading/cli/run_experiments.py --codes <CODES> --zones-csv <PATH>
- examples_llm_trading chk: python examples_llm_trading/trading_system/wave_3x3_run/chk_wave_3x3_run.py --codes <CODES> --zones-csv <PATH>
- examples_llm_trading scripts add repo root to sys.path for direct execution.

## LLM Policy
- temperature=0, schema enforced, invalid output => NO-OP.
- Never store secrets in prompts or outputs.

## Implementation Constraints
- Upstream samples (examples_llm, examples_user, kis_auth.py) are read-only; use wrappers/adapters.
- import * is forbidden; type hints are required.
- LLM output must conform to a JSON schema; schema failure => NO-OP.
- Environment switching (vps/prod) must go through a single settings gate.

## Environment Switch
- kis_devlp.yaml is demo-only (vps/demo). Production keys remain empty unless explicitly enabled.

## Output Conventions
- data/{code}_daily.csv for raw OHLCV.
- out/<tool>/<run>/ for derived reports and artifacts.
- out/mn_trading/run_wave_3x3/<timestamp>/engine_out/ for per-run engine outputs.
- out/mn_trading/experiments/<exp_id>/<mode>/<run_id>/ for experiment artifacts.
- out/mn_trading/experiments/<exp_id>/summary.csv for KPI aggregation.
- out/mn_trading/experiments/<exp_id>/<mode>/<run_id>/signals/aggregated_signals.csv for walk-forward signals.
- out/mn_trading/datasets/cut_<YYYYMMDD>/ for cut-date OHLCV inputs.

## Default Execution Mode
- Default operation uses a 2-layer gate:
  1) SRZ Execution Gate
  2) LLM-gate (policy C)
- The goal is exposure control while maintaining or improving expectancy, not profit maximization.
- This mode is the long-horizon validation baseline.

## Operating Guidance
- Policy changes are made only when performance degrades.
- Always compare before/after using the same reuse-exp-id baseline.
- Any change that weakens default policy C + SRZ must stay on an experimental branch.

## Standard Console Output (chk_wave_3x3_run)
- chk_wave_3x3_run.py outputs four fixed blocks in order:
  1) Run Summary
  2) Artifacts
  3) Signal Summary
  4) Signal Table
- This format is a standard for operations/debugging/audit and counts as an architectural change if modified.
- Codes are normalized as 6-digit strings (leading zeros preserved).

## Documentation Rule
- Any code or configuration change must update this document and CHANGELOG.md in the same task.
