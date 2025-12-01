# Makefile for Candlestick Predictor Application

.PHONY: help build run stop clean test lint format install dev prod logs backup

# Variables
COMPOSE_FILE = docker-compose.yml
COMPOSE_DEV_FILE = docker-compose.dev.yml
PROJECT_NAME = candlestick-predictor
PYTHON = python3
NODE = node
NPM = npm

# Default target
help:
	@echo "🔮 Candlestick Predictor - Available Commands:"
	@echo ""
	@echo "  🚀 Quick Start:"
	@echo "    make install     Install all dependencies"
	@echo "    make dev         Start development environment"
	@echo "    make prod        Start production environment"
	@echo ""
	@echo "  🐳 Docker Operations:"
	@echo "    make build       Build all Docker images"
	@echo "    make run         Run application in production mode"
	@echo "    make stop        Stop all services"
	@echo "    make restart     Restart all services"
	@echo "    make clean       Remove containers and images"
	@echo "    make logs        Show application logs"
	@echo ""
	@echo "  🔧 Development:"
	@echo "    make test        Run all tests"
	@echo "    make lint        Run linting on all code"
	@echo "    make format      Format all code"
	@echo "    make check       Run health checks"
	@echo ""
	@echo "  🔒 Maintenance:"
	@echo "    make backup      Backup application data"
	@echo "    make update      Update dependencies"
	@echo "    make security    Run security scans"
	@echo ""

# Installation
install: install-backend install-frontend install-ai
	@echo "✅ All dependencies installed successfully!"

install-backend:
	@echo "📦 Installing backend dependencies..."
	cd backend && $(PYTHON) -m pip install --upgrade pip
	cd backend && $(PYTHON) -m pip install -r requirements.txt

install-frontend:
	@echo "📦 Installing frontend dependencies..."
	cd frontend && $(NPM) install

install-ai:
	@echo "📦 Installing AI service dependencies..."
	cd ai && $(PYTHON) -m pip install --upgrade pip
	cd ai && $(PYTHON) -m pip install -r requirements.txt

# Development
dev: build-dev
	@echo "🚀 Starting development environment..."
	docker-compose -f $(COMPOSE_DEV_FILE) up -d
	@echo "✅ Development environment started!"
	@echo "🌐 Frontend: http://localhost:3000"
	@echo "🔧 Backend: http://localhost:8000"
	@echo "🤖 AI Service: http://localhost:8001"

dev-logs:
	docker-compose -f $(COMPOSE_DEV_FILE) logs -f

dev-stop:
	docker-compose -f $(COMPOSE_DEV_FILE) down

# Production
prod: build
	@echo "🚀 Starting production environment..."
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "✅ Production environment started!"

build:
	@echo "🔨 Building production Docker images..."
	docker-compose -f $(COMPOSE_FILE) build
	@echo "✅ Production images built successfully!"

build-dev:
	@echo "🔨 Building development Docker images..."
	docker-compose -f $(COMPOSE_DEV_FILE) build
	@echo "✅ Development images built successfully!"

# Operations
run:
	docker-compose -f $(COMPOSE_FILE) up -d

stop:
	docker-compose -f $(COMPOSE_FILE) down
	docker-compose -f $(COMPOSE_DEV_FILE) down

restart: stop run

logs:
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-backend:
	docker-compose -f $(COMPOSE_FILE) logs -f backend

logs-frontend:
	docker-compose -f $(COMPOSE_FILE) logs -f frontend

logs-ai:
	docker-compose -f $(COMPOSE_FILE) logs -f ai

# Health checks
check:
	@echo "🔍 Checking application health..."
	@echo "Frontend:" && curl -f http://localhost:3000 -s -o /dev/null && echo "✅ OK" || echo "❌ FAIL"
	@echo "Backend:" && curl -f http://localhost:8000/health -s -o /dev/null && echo "✅ OK" || echo "❌ FAIL"
	@echo "AI Service:" && curl -f http://localhost:8001/health -s -o /dev/null && echo "✅ OK" || echo "❌ FAIL"

status:
	docker-compose -f $(COMPOSE_FILE) ps

# Testing
test: test-backend test-frontend test-ai
	@echo "✅ All tests completed!"

test-backend:
	@echo "🧪 Running backend tests..."
	cd backend && $(PYTHON) -m pytest tests/ -v --cov=. --cov-report=html

test-frontend:
	@echo "🧪 Running frontend tests..."
	cd frontend && $(NPM) test -- --coverage --watchAll=false

test-ai:
	@echo "🧪 Running AI service tests..."
	cd ai && $(PYTHON) -m pytest tests/ -v --cov=. --cov-report=html

test-integration:
	@echo "🧪 Running integration tests..."
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Code quality
lint: lint-backend lint-frontend lint-ai

lint-backend:
	@echo "🔍 Linting backend code..."
	cd backend && $(PYTHON) -m flake8 . --max-line-length=120 --exclude=venv
	cd backend && $(PYTHON) -m bandit -r . -f json -o bandit-report.json

lint-frontend:
	@echo "🔍 Linting frontend code..."
	cd frontend && $(NPM) run lint

lint-ai:
	@echo "🔍 Linting AI service code..."
	cd ai && $(PYTHON) -m flake8 . --max-line-length=120 --exclude=venv

format: format-backend format-frontend

format-backend:
	@echo "🎨 Formatting backend code..."
	cd backend && $(PYTHON) -m black .
	cd backend && $(PYTHON) -m isort .

format-frontend:
	@echo "🎨 Formatting frontend code..."
	cd frontend && $(NPM) run format

# Security
security:
	@echo "🔒 Running security scans..."
	docker run --rm -v "$(PWD)":/src owasp/dependency-check:latest --scan /src --format JSON --out /src/dependency-check-report.json
	docker run --rm -v "$(PWD)/frontend":/src -w /src node:18-alpine npm audit
	cd backend && $(PYTHON) -m bandit -r . -f json -o bandit-report.json
	@echo "✅ Security scans completed!"

# Cleanup
clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose -f $(COMPOSE_FILE) down --rmi all --volumes --remove-orphans
	docker-compose -f $(COMPOSE_DEV_FILE) down --rmi all --volumes --remove-orphans
	docker system prune -f
	@echo "✅ Cleanup completed!"

clean-data:
	docker volume rm $$(docker volume ls -q | grep $(PROJECT_NAME)) 2>/dev/null || true

# Backup and restore
backup:
	@echo "💾 Creating backup..."
	mkdir -p backups
	docker-compose exec -T backend tar -czf - /app/uploads > backups/uploads-$(shell date +%Y%m%d-%H%M%S).tar.gz
	docker-compose exec -T ai tar -czf - /app/models > backups/models-$(shell date +%Y%m%d-%H%M%S).tar.gz
	@echo "✅ Backup completed!"

restore-uploads:
	@echo "📁 Restoring uploads..."
	docker-compose exec -T backend tar -xzf - -C / < $(BACKUP_FILE)

# Update dependencies
update:
	@echo "🔄 Updating dependencies..."
	cd backend && pip-review --local --auto
	cd frontend && npm update
	cd ai && pip-review --local --auto
	@echo "✅ Dependencies updated!"

# Database operations (if using database)
db-migrate:
	docker-compose exec backend alembic upgrade head

db-seed:
	docker-compose exec backend python scripts/seed_data.py

# Monitoring
monitor:
	@echo "📊 Starting monitoring stack..."
	docker-compose -f docker-compose.monitoring.yml up -d

monitor-stop:
	docker-compose -f docker-compose.monitoring.yml down

# Deployment
deploy-staging:
	@echo "🚀 Deploying to staging..."
	ansible-playbook -i devops/ansible/inventories/staging devops/ansible/playbooks/deploy.yml

deploy-prod:
	@echo "🚀 Deploying to production..."
	ansible-playbook -i devops/ansible/inventories/production devops/ansible/playbooks/deploy.yml

# Documentation
docs:
	@echo "📚 Generating documentation..."
	cd backend && pydoc-markdown
	cd frontend && npm run docs

# Performance testing
perf-test:
	@echo "⚡ Running performance tests..."
	docker run --rm -i grafana/k6 run - < tests/performance/load-test.js

# Generate SSL certificates (development)
ssl:
	@echo "🔐 Generating SSL certificates..."
	mkdir -p ssl
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
		-keyout ssl/candlestick-dev.key \
		-out ssl/candlestick-dev.crt \
		-subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
	@echo "✅ SSL certificates generated!"

# Help for specific components
help-docker:
	@echo "🐳 Docker Commands:"
	@echo "  docker-compose logs [service]     - View service logs"
	@echo "  docker-compose exec [service] sh - Shell into service"
	@echo "  docker-compose ps                - List running services"

help-development:
	@echo "💻 Development Commands:"
	@echo "  make dev                         - Start development environment"
	@echo "  make test                        - Run all tests"
	@echo "  make lint                        - Check code quality"
	@echo "  make format                      - Format code"

# Git operations
git-setup:
	git init
	git add .
	git commit -m "Initial commit: Complete candlestick predictor application"
	@echo "✅ Git repository initialized!"

# Environment setup
env-setup:
	@echo "🔧 Setting up environment files..."
	cp backend/.env.example backend/.env
	cp frontend/.env.example frontend/.env
	cp ai/.env.example ai/.env
	@echo "✅ Environment files created! Please configure them."

# Full setup for new developers
setup: install env-setup ssl
	@echo "🎉 Complete setup finished!"
	@echo "Next steps:"
	@echo "1. Configure .env files in each service directory"
	@echo "2. Run 'make dev' to start development environment"
	@echo "3. Visit http://localhost:3000 to see the application"