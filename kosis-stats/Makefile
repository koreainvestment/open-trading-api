DATABASE_URL ?= postgresql://sunjinlee@localhost:5432/dart?sslmode=disable
TEST_DATABASE_URL ?= postgresql://sunjinlee@localhost:5432/dart_test?sslmode=disable
MIGRATIONS_DIR ?= internal/db/migrations
CMD_DIR ?= cmd

.PHONY: run build migrate-up migrate-down migrate-create clean

run: ## Run the app: go run
	go run $(CMD_DIR)/api/main.go

run-mcp: ## Run the MCP stdio server
	go run $(CMD_DIR)/mcp/main.go

run-worker: ## Run the worker: go run
	go run $(CMD_DIR)/worker/main.go

run-worker-cli: ## Run the worker CLI: go run
	go run $(CMD_DIR)/worker-cli/main.go $(RECEIPT_NUMBER)

run-web: ## Run the web server: npm run serve
	cd web && npm run dev

build-mcp: ## Build the MCP server
	go build -o bin/kosis-mcp $(CMD_DIR)/mcp/main.go

test: ## Run the tests
	DATABASE_URL=$(TEST_DATABASE_URL) go test ./...

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

migrate-test-redo:
ifndef TEST_DATABASE_URL
	$(error TEST_DATABASE_URL is not set)
endif
	migrate -path=$(MIGRATIONS_DIR) -database "$(TEST_DATABASE_URL)" -verbose down 1
	migrate -path=$(MIGRATIONS_DIR) -database "$(TEST_DATABASE_URL)" -verbose up
