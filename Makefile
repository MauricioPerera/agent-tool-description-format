# ATDF Project Makefile

.PHONY: help build up down logs test lint format clean dev-up dev-down prod-up prod-down

# Default target
help: ## Show this help message
	@echo "ATDF Project Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development commands
dev-up: ## Start development environment
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Development environment started!"
	@echo "API: http://localhost:8000"
	@echo "pgAdmin: http://localhost:5050"
	@echo "Redis Commander: http://localhost:8081"
	@echo "Mailhog: http://localhost:8025"

dev-down: ## Stop development environment
	docker-compose -f docker-compose.dev.yml down

dev-logs: ## Show development logs
	docker-compose -f docker-compose.dev.yml logs -f

dev-restart: ## Restart development environment
	docker-compose -f docker-compose.dev.yml restart atdf-api-dev

# Production commands
prod-up: ## Start production environment
	docker-compose up -d
	@echo "Production environment started!"
	@echo "API: http://localhost:8000"
	@echo "Grafana: http://localhost:3000"
	@echo "Prometheus: http://localhost:9090"

prod-down: ## Stop production environment
	docker-compose down

prod-logs: ## Show production logs
	docker-compose logs -f

# Build commands
build: ## Build Docker images
	docker-compose build

build-dev: ## Build development Docker images
	docker-compose -f docker-compose.dev.yml build

build-no-cache: ## Build Docker images without cache
	docker-compose build --no-cache

# Database commands
db-init: ## Initialize database
	docker-compose exec postgres psql -U atdf_user -d atdf_db -f /docker-entrypoint-initdb.d/init-db.sql

db-reset: ## Reset database (WARNING: This will delete all data)
	docker-compose down -v
	docker volume rm atdf_postgres_data || true
	docker-compose up -d postgres
	sleep 10
	make db-init

db-backup: ## Backup database
	docker-compose exec postgres pg_dump -U atdf_user atdf_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

db-shell: ## Connect to database shell
	docker-compose exec postgres psql -U atdf_user -d atdf_db

# Testing commands
test: ## Run all tests
	docker-compose -f docker-compose.dev.yml exec atdf-api-dev pytest tests/ -v

test-coverage: ## Run tests with coverage
	docker-compose -f docker-compose.dev.yml exec atdf-api-dev pytest tests/ -v --cov=sdk --cov=tools --cov=examples --cov-report=html

test-integration: ## Run integration tests
	docker-compose -f docker-compose.dev.yml exec atdf-api-dev pytest tests/integration/ -v

# Code quality commands
lint: ## Run linting
	docker-compose -f docker-compose.dev.yml exec atdf-api-dev flake8 .
	docker-compose -f docker-compose.dev.yml exec atdf-api-dev mypy sdk/ tools/ examples/

format: ## Format code
	docker-compose -f docker-compose.dev.yml exec atdf-api-dev black .
	docker-compose -f docker-compose.dev.yml exec atdf-api-dev isort .

format-check: ## Check code formatting
	docker-compose -f docker-compose.dev.yml exec atdf-api-dev black --check .
	docker-compose -f docker-compose.dev.yml exec atdf-api-dev isort --check-only .

# Utility commands
logs: ## Show logs for all services
	docker-compose logs -f

shell: ## Open shell in API container
	docker-compose exec atdf-api bash

dev-shell: ## Open shell in development API container
	docker-compose -f docker-compose.dev.yml exec atdf-api-dev bash

clean: ## Clean up Docker resources
	docker-compose down -v
	docker system prune -f
	docker volume prune -f

clean-all: ## Clean up all Docker resources (WARNING: This affects all Docker containers)
	docker-compose down -v
	docker system prune -a -f
	docker volume prune -f

# Monitoring commands
metrics: ## Show Prometheus metrics
	@echo "📊 Checking application metrics..."
	@curl -s http://localhost:8000/metrics || echo "❌ Metrics endpoint not available"

health: ## Check service health
	@echo "🏥 Checking application health..."
	@curl -s http://localhost:8000/health | jq . || echo "❌ Health endpoint not available"

setup-monitoring: ## Setup monitoring infrastructure
	@echo "🔧 Setting up monitoring infrastructure..."
	@python scripts/setup_monitoring.py

test-metrics: ## Run metrics test
	@echo "🧪 Running metrics test..."
	@python examples/test_metrics.py

monitoring-status: ## Check monitoring services status
	@echo "📊 Monitoring Services Status:"
	@echo "Prometheus: http://localhost:9090"
	@curl -s http://localhost:9090/-/healthy > /dev/null && echo "✅ Prometheus: Running" || echo "❌ Prometheus: Not running"
	@echo "Grafana: http://localhost:3000"
	@curl -s http://localhost:3000/api/health > /dev/null && echo "✅ Grafana: Running" || echo "❌ Grafana: Not running"
	@echo "ATDF API: http://localhost:8000"
	@curl -s http://localhost:8000/health > /dev/null && echo "✅ ATDF API: Running" || echo "❌ ATDF API: Not running"

# Installation commands
install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt
	pre-commit install

install-hooks: ## Install pre-commit hooks
	pre-commit install
	pre-commit install --hook-type commit-msg

# Documentation commands
docs-serve: ## Serve documentation locally
	docker run --rm -it -p 8080:8080 -v ${PWD}:/docs squidfunk/mkdocs-material

# Security commands
security-scan: ## Run security scan
	docker-compose -f docker-compose.dev.yml exec atdf-api-dev safety check
	docker-compose -f docker-compose.dev.yml exec atdf-api-dev bandit -r sdk/ tools/ examples/

# Backup and restore
backup: ## Create full backup
	mkdir -p backups/$(shell date +%Y%m%d_%H%M%S)
	make db-backup
	docker-compose exec redis redis-cli --rdb /data/dump.rdb
	cp -r data/ backups/$(shell date +%Y%m%d_%H%M%S)/

# Environment setup
setup: ## Initial project setup
	@echo "Setting up ATDF project..."
	cp .env.example .env
	make install-dev
	make build-dev
	make dev-up
	sleep 30
	make db-init
	@echo "Setup complete! Visit http://localhost:8000"