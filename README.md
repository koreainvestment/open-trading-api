# KOSIS Stats

A simple Go application for KOSIS statistics.

## Overview

This project provides a basic Go application for handling KOSIS statistics data.

## Prerequisites

- Go > 1.25
- Make
- `migrate` (for database migrations)

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd kosis-stats
   ```

2. Install dependencies:

   ```bash
   go mod tidy
   ```

## Usage

Use `make` to run various components of the application.

### Run the API Server

To start the API server:

```bash
make run
```

### Run the Worker

To start the background worker:

```bash
make run-worker
```

### Run the Dry Run

To run the dry run:

```bash
RECEIPT_NUMBER=20260109900734 make run-worker-cli
```

### Run Tests

To execute the test suite:

```bash
make test
```

To verify the MCP server is running:

```bash
npx @modelcontextprotocol/inspector ./bin/kosis-mcp
```

### Run with docker compose

```bash
docker compose up
```

## Database Migrations

Ensure your `DATABASE_URL` environment variable is set before running migrations.

- Apply all up migrations:

  ```bash
  make migrate-up
  ```

- Rollback the last migration:

  ```bash
  make migrate-down
  ```

- Create a new migration:

  ```bash
  make migrate-create NAME=migration_name
  ```
