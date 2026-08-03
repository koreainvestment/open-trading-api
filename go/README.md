# Go Module Guide

## Overview

The Go module under [`go/`](/Users/sunjinlee/workspace/open-trading-api/go) is now organized by feature while preserving the existing runtime behavior of `go run ./cmd`, current environment variables, and business-date-scoped cache/output rules.

## Structure

### Command Layer

- [`go/cmd/main.go`](/Users/sunjinlee/workspace/open-trading-api/go/cmd/main.go): thin bootstrap that loads `.env` and calls `runApp()`
- [`go/cmd/app.go`](/Users/sunjinlee/workspace/open-trading-api/go/cmd/app.go): top-level runners for domestic market, quad witching, global markets, company analysis, and domestic valuation
- [`go/cmd/config.go`](/Users/sunjinlee/workspace/open-trading-api/go/cmd/config.go): app config loading and env/default parsing
- [`go/cmd/render_*.go`](/Users/sunjinlee/workspace/open-trading-api/go/cmd): summary rendering grouped by feature
- [`go/cmd/response_helpers.go`](/Users/sunjinlee/workspace/open-trading-api/go/cmd/response_helpers.go): REST response inspection helpers
- [`go/cmd/format_helpers.go`](/Users/sunjinlee/workspace/open-trading-api/go/cmd/format_helpers.go): formatting helpers shared by renderers
- [`go/cmd/path_helpers.go`](/Users/sunjinlee/workspace/open-trading-api/go/cmd/path_helpers.go): business-date and dated JSON path resolution helpers

### Domestic Stock

- [`go/internal/domesticstock/service.go`](/Users/sunjinlee/workspace/open-trading-api/go/internal/domesticstock/service.go): shared service/types and package-level helpers
- [`go/internal/domesticstock/market_snapshot.go`](/Users/sunjinlee/workspace/open-trading-api/go/internal/domesticstock/market_snapshot.go): market snapshot APIs, VKOSPI resolution, RSI entrypoints
- [`go/internal/domesticstock/quotation_analysis.go`](/Users/sunjinlee/workspace/open-trading-api/go/internal/domesticstock/quotation_analysis.go): investor/foreign/auction quotation flows
- [`go/internal/domesticstock/kospi_master_cache.go`](/Users/sunjinlee/workspace/open-trading-api/go/internal/domesticstock/kospi_master_cache.go): dated KOSPI master cache, parsing, and JSON sidecar generation
- [`go/internal/domesticstock/pbr.go`](/Users/sunjinlee/workspace/open-trading-api/go/internal/domesticstock/pbr.go): proxy/actual PBR calculations and actual PBR cache handling
- [`go/internal/domesticstock/finance_api.go`](/Users/sunjinlee/workspace/open-trading-api/go/internal/domesticstock/finance_api.go): finance-related REST wrappers
- [`go/internal/domesticstock/dcf_types.go`](/Users/sunjinlee/workspace/open-trading-api/go/internal/domesticstock/dcf_types.go): DCF option/result/input types
- [`go/internal/domesticstock/dcf_inputs.go`](/Users/sunjinlee/workspace/open-trading-api/go/internal/domesticstock/dcf_inputs.go): DCF input bundle assembly and derived input helpers
- [`go/internal/domesticstock/dcf_readiness.go`](/Users/sunjinlee/workspace/open-trading-api/go/internal/domesticstock/dcf_readiness.go): readiness evaluation
- [`go/internal/domesticstock/dcf_valuation.go`](/Users/sunjinlee/workspace/open-trading-api/go/internal/domesticstock/dcf_valuation.go): valuation entrypoint

### Domestic Futures / Options

- [`go/internal/domesticfutureoption/service.go`](/Users/sunjinlee/workspace/open-trading-api/go/internal/domesticfutureoption/service.go): service/types/constants
- [`go/internal/domesticfutureoption/quotes.go`](/Users/sunjinlee/workspace/open-trading-api/go/internal/domesticfutureoption/quotes.go): quote and board endpoints
- [`go/internal/domesticfutureoption/contract_resolution.go`](/Users/sunjinlee/workspace/open-trading-api/go/internal/domesticfutureoption/contract_resolution.go): near-month KOSPI200 futures resolution
- [`go/internal/domesticfutureoption/master_cache.go`](/Users/sunjinlee/workspace/open-trading-api/go/internal/domesticfutureoption/master_cache.go): business-date master cache and JSON sidecar handling

### Company Analysis

- [`go/internal/companyanalysis/service.go`](/Users/sunjinlee/workspace/open-trading-api/go/internal/companyanalysis/service.go): service/types and analysis orchestration
- [`go/internal/companyanalysis/sec_source.go`](/Users/sunjinlee/workspace/open-trading-api/go/internal/companyanalysis/sec_source.go): SEC fetch/cache helpers
- [`go/internal/companyanalysis/sec_financials.go`](/Users/sunjinlee/workspace/open-trading-api/go/internal/companyanalysis/sec_financials.go): SEC annual record extraction
- [`go/internal/companyanalysis/market_data.go`](/Users/sunjinlee/workspace/open-trading-api/go/internal/companyanalysis/market_data.go): FRED/Stooq/Damodaran derived inputs
- [`go/internal/companyanalysis/valuation_support.go`](/Users/sunjinlee/workspace/open-trading-api/go/internal/companyanalysis/valuation_support.go): projection and key metric derivation

## Execution Flow

1. `main.go` loads `.env`.
2. `runApp()` loads config, builds dependencies, authenticates, and preserves the original execution order.
3. Business-date-sensitive exports still use market-time-derived dates when available.
4. KOSPI master, index futures master, quad witching snapshot, DCF Monte Carlo, and company analysis JSON exports keep their dated path rules.

## Agent Report CLI Commands (`cmd/agent`)

Detailed documentation for report subcommands is available in [`AGENT_CLI_GUIDE.md`](/Users/sunjinlee/workspace/open-trading-api/go/AGENT_CLI_GUIDE.md).

```bash
# Premarket vulnerability score board
go run ./cmd/agent report premarket

# RSI historical series engine with interval option (--interval 1d, 60m, 15m, 5m)
go run ./cmd/agent report rsi --symbol kospi --period 14 --interval 60m

# Real System Leverage (Credit Balance ÷ Customer Deposit) report
go run ./cmd/agent report credit-balance --ratio --days 60

# Safety Devices (Sidecar & Circuit Breaker) monitoring
go run ./cmd/agent report safety-devices
```

## DART Filing Worker CLI (`cmd/dart-filing-worker-cli`)

[DART Filing Worker CLI](cmd/dart-filing-worker-cli/main.go)는 DART 공시 데이터 수집, 기업 마스터 백필 및 특정 기업 공시 분석을 수행하는 CLI 도구입니다.

```bash
# 1. 전체 기업 마스터(companies 테이블) 백필
make dart-filing-cli-companies
# 또는
go run ./cmd/dart-filing-worker-cli companies

# 2. 특정 기업 공시 수집 및 AI 분석 저장 (예: 삼성전자 corp_code="00126380", 최근 5건 제한)
make dart-filing-cli-company CORP_CODE="00126380" LIMIT=5
# 또는
go run ./cmd/dart-filing-worker-cli company 00126380 5

# 3. 전체 최근 공시 수집 및 분석 저장
go run ./cmd/dart-filing-worker-cli reports

# 4. 단일 공시 건 AI 분석 Dry-run 테스트 (DB 미저장)
make dart-filing-cli RECEIPT_NO="20240321000725"
# 또는
go run ./cmd/dart-filing-worker-cli dry-run 20240321000725
```

## DART Filing Web Frontend (`web`)

[go/web](web) 디렉토리의 Vite + React 프론트엔드 애플리케이션을 실행하고 빌드하는 명령어입니다.

```bash
# Web 프론트엔드 개발 서버 실행 (Vite dev server)
make dart-filing-web

# Web 프론트엔드 프로덕션 빌드 (Vite build)
make dart-filing-web-build
```

## Run And Test

```bash
cd go
go test ./...
go run ./cmd
```

`go run ./cmd` still performs live network/API work, so it requires valid credentials and reachable upstream endpoints.
