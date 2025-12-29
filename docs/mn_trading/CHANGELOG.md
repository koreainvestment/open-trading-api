# Change Log

## 2025-12-28 KST
- Changed: Normalize backtest inputs by shifting signal date -1 bar when signals land on dataset last date (enables idx+1 entry)
- Fixed: Normalize backtest signals to YYYY-MM-DD date strings for correct matching
- Added: Walk-forward experiments aggregate daily signals before backtest KPI
- Changed: Walk-forward optimized to reuse rule signals for random/llm (no extra engine runs)
- Changed: Walk-forward requires --runs 1 with an explicit guard message to prevent excess engine calls
- Added: Rule-gate baseline aligned with llm-gate interface for experiments
- Added: Gate-only rerun mode via --reuse-exp-id (no engine execution)
- Fixed: reuse-exp-id backtest uses source data directory when cut datasets are absent
- Changed: Clarified gate_mode semantics to only affect mode=llm; rule/random unaffected
- Fixed: reuse-exp-id walk-forward branch indentation to prevent runtime failure
- Changed: LLM-gate simplified schema and row-level calls to reduce noop_fallback
- Changed: LLM-gate fixed to Wave Position Classifier (BB50 lower zone filter)
- Fixed: LLM-gate now uses indicator-derived position features and removes entry_stage guardrail that nullified BLOCK
- Fixed: Normalize codes to 6-digit strings for LLM-gate joins with daily data
- Added: LLM gate policy switch (strong/A/B/C) to tune block aggressiveness
- Added: SRZ execution gate layered above policy C to block BUY_* outside long-term zones
- Added: Default execution mode fixed to policy C with SRZ execution gate
- Changed: strong/A/B policies marked as experimental only
- Risk/Impact: Metrics evaluation only
- Migration: None

## 2025-12-26 KST
- Added: docs/mn_trading/ARCHITECTURE.md
- Added: docs/mn_trading/CHANGELOG.md
- Added: docs/mn_trading/TODO.md
- Added: Architecture status lifecycle (Planned -> Active promotion policy)
- Added: Implementation constraints and TODO Now rules
- Added: mn_trading minimal package skeleton (settings + placeholder CLI)
- Added: mn_trading wave_3x3 adapter (subprocess wrapper around tools/wave_3x3_engine.py)
- Changed: run_wave_3x3 CLI can execute engine and record outputs in run.json
- Changed: run_wave_3x3 CLI passes zones CSV to engine adapter
- Changed: wave_3x3 engine outputs are scoped per run under engine_out
- Added: examples_llm_trading wave_3x3 run + chk (validation + summary printing)
- Changed: Standardized chk_wave_3x3_run console output to include run directory and artifact paths (Option B)
- Changed: examples_llm_trading wave_3x3 scripts ensure repo root on sys.path for direct execution
- Fixed: Preserve leading zeros in stock codes in chk_wave_3x3_run output (dtype + zfill)
- Added: experiment runner for rule/random/llm (placeholder) with reproducible artifacts
- Added: backtest integration for experiments (subprocess tools/backtest_signals.py) to populate KPI
- Changed: Hardened backtest stdout parsing (kv/table/heuristic) and improved placeholder notes
- Added: cut-date dataset generator and experiments support via --data-dir
- Fixed: backtest_adapter indentation to prevent experiment runner failure
- Risk/Impact: Research scaffolding only (no broker orders)
- Migration: None
