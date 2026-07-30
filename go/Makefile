CMD_DIR ?= cmd

.PHONY: run build test takesnapshot creditbalance now dart-filing-cli dart-filing-api dart-filing-worker

now:
	go run ./cmd/agent report intraday-pulse


run: ## Run the app: go run
	go run ./$(CMD_DIR)

DATE ?= $(shell date +%Y%m%d)

takesnapshot:
	go run ./cmd/agent report market-snapshot --date $(DATE)

SYMBOLS ?=
WATCHLIST ?= watchlist.txt
creditbalance: ## Credit balance: make creditbalance or make creditbalance SYMBOLS="005930"
	@if [ -n "$(SYMBOLS)" ]; then \
		go run ./cmd/agent report credit-balance $(SYMBOLS); \
	else \
		go run ./cmd/agent report credit-balance --watchlist $(WATCHLIST); \
	fi

RECEIPT_NO ?=
dart-filing-cli: ## Run DART Filing Worker CLI dry-run: make dart-filing-cli RECEIPT_NO="20240321000725"
	@if [ -z "$(RECEIPT_NO)" ]; then \
		echo "Usage: make dart-filing-cli RECEIPT_NO=<receipt_number>"; \
		exit 1; \
	fi; \
	go run ./cmd/dart-filing-worker-cli $(RECEIPT_NO)

dart-filing-api: ## Run DART Filing API server
	go run ./cmd/dart-filing-api

dart-filing-worker: ## Run DART Filing Worker
	go run ./cmd/dart-filing-worker

build: ## Build the app
	go build -o bin/kis-open-api ./$(CMD_DIR)

test: ## Run the tests
	go test ./...
