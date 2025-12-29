# TODO

## Now
- [x] Architecture lifecycle policy documented (Planned -> Active).
- [ ] Enforce Architecture Status and Promotion Policy as a mandatory working rule.
- [ ] Treat mn_trading as Planned Architecture until promotion criteria are met.
- [ ] Allow structural refactoring only under Planned status.
- [ ] Require documentation update (ARCHITECTURE.md + CHANGELOG.md) for any structural or execution-flow change.
- [ ] Ongoing rule: keep SSOT docs in sync with code and execution-flow changes.
- [x] Wire mn_trading adapter to tools/wave_3x3_engine.py and persist outputs in run.json
- [x] Scope wave_3x3 engine outputs per run (engine_out) and require zones-csv in CLI
- [x] Add examples_llm_trading wave_3x3 run + chk entry points and validations
- [x] Harden backtest stdout parser and note reasons for placeholder metrics

## Next
- [ ] Decide whether to enforce the doc-first rule in agent instructions.
- [ ] Run 3-mode experiment set (rule/random/llm-noop) for N runs and capture artifacts.
- [ ] Implement real KPI via backtest_signals integration (if not done).
- [ ] Validate KPI population for rule/random/llm-noop runs (N=10) and review distributions.
- [ ] Run experiments with cut-date (e.g., 5 trading days before last) and validate KPI non-zero.
- [ ] Run walk-forward N=200 and review mode distributions (rule vs random vs llm-noop).
- [ ] Run walk-forward 200 bars with runs=1 and confirm summary.csv is generated within time limits.
- [ ] Compare rule(no gate) vs rule-gate vs llm-gate on walk-forward-bars=200.
- [ ] Re-run gate-only experiments with --reuse-exp-id and confirm runtime < 2 minutes.
- [ ] Verify gate_mode=rule changes only llm row metrics; rule/random rows remain identical across gate modes.
- [ ] Verify llm_gate valid decision rate >= 80% on reuse-exp-id experiments.
- [ ] Evaluate BB50 lower-zone LLM-gate impact on expectancy_R and max_dd.
- [ ] Confirm buy_rows_bb50_above > 0 yields llm_decision_block > 0 and changes llm row KPIs.
- [ ] Sweep llm_gate_policy (strong/A/B/C) and compare trades vs max_dd vs expectancy_R.
- [ ] Validate SRZ+policy C reduces false trades without increasing max_dd.
- [ ] Expand validation to 10+ symbols with reuse-exp-id flow.
- [ ] Run multi-period walk-forward (>= 600 bars) under default mode.
- [ ] Track rolling max_dd stability vs baseline.
- [ ] Monitor expectancy_R drift with increasing trade count.

## Blocked
- (none)

## Decisions Needed
- (none)
