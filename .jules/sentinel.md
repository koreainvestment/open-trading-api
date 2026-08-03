# Jules Sentinel Rules & Scope Guidelines

## Primary Workspace Scope

- **Target Directory**: `go/`
- **Scope Restriction**: ALL code inspection, research, file reading, and modifications MUST be restricted exclusively to the [`go/`](file:///Users/sunjinlee/workspace/open-trading-api/go) directory.

## Guidelines & Constraints

1. **Target Subdirectories**:
   - `go/cmd/` (CLI & application entrypoints)
   - `go/internal/` (Core logic, DART filing, DCF engine, domestic stock/futures modules)
   - `go/web/` (React + Vite Web Frontend)
   - `go/Makefile` & `go/README.md`
2. **Exclusion Rule**: Do NOT inspect, read, or modify files outside the `go/` directory (such as Python scripts in `examples_llm/`, `examples_user/`, `strategy_builder/`, `backtester/`, etc.) unless explicitly instructed by the user.
3. **Repository Rules & Architecture**:
   - Preserve business-date-scoped cache filenames (`.cache/kospi_code.<YYYYMMDD>.mst`, `.cache/fo_idx_code_mts.<YYYYMMDD>.mst`).
   - Preserve JSON sidecars for master cache files.
   - Maintain distinction between `exact`, `derived`, and `assumed` tiers in DCF engine calculations.
   - Ensure all Go tests (`go test ./...`) pass cleanly when modifying Go packages.
