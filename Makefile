.PHONY: help setup dev dev-infra dev-stop test lint fmt migrate seed build up down logs clean

# Default
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# === Development ===

setup: ## First-time setup: install deps, start infra, run migrations
	bash scripts/setup-dev.sh

dev-infra: ## Start infrastructure only (Postgres, Redis, LocalStack)
	docker compose -f infra/docker/docker-compose.yml up -d

dev-stop: ## Stop infrastructure
	docker compose -f infra/docker/docker-compose.yml down

dev: dev-infra ## Start all services for local development
	@echo "Starting gateway on :8000..."
	@cd services/gateway && uv run uvicorn gateway.main:app --reload --port 8000 &
	@echo "Starting agent consumer..."
	@cd services/agents && uv run python -m agents.consumer &
	@echo "Starting dashboard on :3000..."
	@cd apps/dashboard && pnpm dev &
	@echo "\n✅ All services starting. Gateway: http://localhost:8000/docs | Dashboard: http://localhost:3000"

# === Testing ===

test: ## Run all Python tests
	uv run pytest tests/ -v --tb=short

test-core: ## Run only core library tests
	uv run pytest tests/core/ -v

test-gateway: ## Run only gateway tests
	uv run pytest tests/gateway/ -v

test-agents: ## Run only agent tests
	uv run pytest tests/agents/ -v

test-integrations: ## Run only integration tests
	uv run pytest tests/integrations/ -v

test-cov: ## Run tests with coverage report
	uv run pytest tests/ -v --cov=. --cov-report=term-missing

# === Code Quality ===

lint: ## Run linter (ruff)
	uv run ruff check .

fmt: ## Format code (ruff)
	uv run ruff format .

# === Database ===

migrate: ## Run database migrations
	cd migrations && uv run alembic upgrade head

migrate-down: ## Rollback last migration
	cd migrations && uv run alembic downgrade -1

migrate-new: ## Create new migration (usage: make migrate-new MSG="add_foo_table")
	cd migrations && uv run alembic revision --autogenerate -m "$(MSG)"

seed: ## Seed development data
	bash scripts/seed-data.sh

# === Docker ===

build: ## Build all Docker images
	docker compose build

up: ## Start full stack with Docker Compose
	docker compose up -d
	@echo "\n✅ NeuraProp AI is running:"
	@echo "   Dashboard:  http://localhost:3000"
	@echo "   API:        http://localhost:8000"
	@echo "   API Docs:   http://localhost:8000/docs"

down: ## Stop all Docker containers
	docker compose down

logs: ## Tail logs from all services
	docker compose logs -f

logs-gateway: ## Tail gateway logs
	docker compose logs -f gateway

logs-agents: ## Tail agent consumer logs
	docker compose logs -f agents

# === Utilities ===

clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf apps/dashboard/.next
	@echo "✅ Cleaned"

gen-encryption-key: ## Generate a new AES-256 encryption key
	@python3 -c "import os,base64; print('ENCRYPTION_KEY=' + base64.b64encode(os.urandom(32)).decode())"

gen-api-key: ## Generate a test API key
	@python3 -c "import secrets; print('np_live_test_' + secrets.token_urlsafe(32))"
