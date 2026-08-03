CMD_DIR ?= cmd
DATABASE_URL ?= postgresql://sunjinlee@localhost:5432/dart?sslmode=disable
TEST_DATABASE_URL ?= postgresql://sunjinlee@localhost:5432/dart_test?sslmode=disable
MIGRATIONS_DIR ?= internal/db/migrations

.PHONY: run build test takesnapshot creditbalance now dart-filing-cli dart-filing-cli-companies dart-filing-cli-company dart-filing-api dart-filing-worker dart-filing-web dart-filing-web-build migrate-up migrate-down migrate-create migrate-test-redo

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
CORP_CODE ?=
LIMIT ?=

dart-filing-cli: ## Run DART Filing Worker CLI dry-run: make dart-filing-cli RECEIPT_NO="20240321000725"
	@if [ -z "$(RECEIPT_NO)" ]; then \
		echo "Usage: make dart-filing-cli RECEIPT_NO=<receipt_number>"; \
		exit 1; \
	fi; \
	go run ./cmd/dart-filing-worker-cli dry-run $(RECEIPT_NO)

dart-filing-cli-companies: ## Backfill companies via DART Filing Worker CLI
	go run ./cmd/dart-filing-worker-cli companies

dart-filing-cli-company: ## Fetch disclosures for specific company via CLI: make dart-filing-cli-company CORP_CODE="00126380" LIMIT=5
	@if [ -z "$(CORP_CODE)" ]; then \
		echo "Usage: make dart-filing-cli-company CORP_CODE=<corp_code> [LIMIT=<limit>]"; \
		exit 1; \
	fi; \
	go run ./cmd/dart-filing-worker-cli company $(CORP_CODE) $(LIMIT)

dart-filing-api: ## Run DART Filing API server
	go run ./cmd/dart-filing-api

dart-filing-worker: ## Run DART Filing Worker
	go run ./cmd/dart-filing-worker

dart-filing-web: ## Run DART Filing Web Frontend dev server
	npm --prefix web run dev

dart-filing-web-build: ## Build DART Filing Web Frontend
	npm --prefix web run build

build: ## Build the app
	go build -o bin/kis-open-api ./$(CMD_DIR)

test: ## Run the tests
	go test ./...

migrate-up: ## Run all up migrations
ifndef DATABASE_URL
	$(error DATABASE_URL is not set)
endif
	migrate -path=$(MIGRATIONS_DIR) -database "$(DATABASE_URL)" -verbose up

migrate-down: ## Run last migration down
ifndef DATABASE_URL
	$(error DATABASE_URL is not set)
endif
	migrate -path=$(MIGRATIONS_DIR) -database "$(DATABASE_URL)" -verbose down 1

migrate-create: ## Create new migration files. Usage: make migrate-create NAME=your_desc
ifndef NAME
	$(error NAME is not set)
endif
	migrate create -ext sql -dir $(MIGRATIONS_DIR) -seq ${NAME}

migrate-test-up:
ifndef TEST_DATABASE_URL
	$(error TEST_DATABASE_URL is not set)
endif
	migrate -path=$(MIGRATIONS_DIR) -database "$(TEST_DATABASE_URL)" -verbose up

migrate-test-redo:
ifndef TEST_DATABASE_URL
	$(error TEST_DATABASE_URL is not set)
endif
	migrate -path=$(MIGRATIONS_DIR) -database "$(TEST_DATABASE_URL)" -verbose down 1
	migrate -path=$(MIGRATIONS_DIR) -database "$(TEST_DATABASE_URL)" -verbose up