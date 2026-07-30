# Project Context: KOSIS Stats

This file documents the project's technology stack, architectural decisions, and development preferences for the AI assistant.

## Tech Stack

### Backend
- **Language:** Go (v1.25)
- **Web Framework:** Gin
- **Database:** PostgreSQL
- **ORM:** GORM
- **Job Queue:** Asynq (Redis-backed)
- **Testing:** Ginkgo & Gomega
- **AI/LLM:** OpenAI API (`openai-go`)
- **HTML Parsing:** goquery

### Frontend (`web/`)
- **Language:** TypeScript
- **Type:** Vanilla Single Page Application (SPA)
- **Build Tool:** `tsc` (TypeScript Compiler)
- **Serving:** Python `http.server` (dev)

### Infrastructure & Tools
- **Containerization:** Docker Compose (PostgreSQL, Redis)
- **Migrations:** `golang-migrate`
- **Task Runner:** Makefile

## Development Preferences

### Scripting & Ad-hoc Tasks
- **Language:** Ruby
- **Use Case:** Use Ruby for writing utility scripts, data manipulation scripts, or ad-hoc automation tasks.

### Testing
- **Mocking HTTP:** Prefer using Ruby for writing external tests that need to mock HTTP interactions or simulate client behavior against the API.
- **Unit/Integration:** Continue using Go's standard testing + Ginkgo/Gomega for internal backend tests.

## Project Structure
- `cmd/`: Entry points for applications (API, MCP server, Worker).
- `internal/`: Private application code (Controllers, Models, DB, Logic).
- `web/`: Frontend source code.
- `data/`: Data storage (markdowns, receipts, etc.).
- `bin/`: Compiled binaries.
