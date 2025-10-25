.PHONY: help install dev test clean build deploy lint format

# Default target
help:
	@echo "ZeroTrust IAM Analyzer - Development Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  install     Install all dependencies"
	@echo "  dev         Start development environment"
	@echo ""
	@echo "Development Commands:"
	@echo "  test        Run all tests"
	@echo "  lint        Run linting checks"
	@echo "  format      Format code"
	@echo "  clean       Clean temporary files"
	@echo ""
	@echo "Build & Deploy:"
	@echo "  build       Build Docker images"
	@echo "  deploy      Deploy to production"
	@echo ""
	@echo "Database:"
	@echo "  db-migrate  Run database migrations"
	@echo "  db-reset    Reset database"
	@echo ""
	@echo "Documentation:"
	@echo "  docs        Generate documentation"

# Install dependencies
install:
	@echo "Installing backend dependencies..."
	cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements-dev.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Start development environment
dev:
	@echo "Starting development environment..."
	docker-compose up -d

# Stop development environment
stop:
	@echo "Stopping development environment..."
	docker-compose down

# Run tests
test:
	@echo "Running backend tests..."
	cd backend && source venv/bin/activate && pytest --cov=app --cov-report=html
	@echo "Running frontend tests..."
	cd frontend && npm test

# Run linting
lint:
	@echo "Linting backend..."
	cd backend && source venv/bin/activate && flake8 app/ && mypy app/
	@echo "Linting frontend..."
	cd frontend && npm run lint

# Format code
format:
	@echo "Formatting backend..."
	cd backend && source venv/bin/activate && black app/ && isort app/
	@echo "Formatting frontend..."
	cd frontend && npm run format

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	cd frontend && rm -rf node_modules/ dist/ build/
	cd backend && rm -rf .pytest_cache/ .coverage htmlcov/

# Build Docker images
build:
	@echo "Building Docker images..."
	docker build -t zerotrust-iam-analyzer-backend ./backend
	docker build -t zerotrust-iam-analyzer-frontend ./frontend

# Deploy to production
deploy:
	@echo "Deploying to production..."
	./scripts/deployment/deploy-backend.sh
	./scripts/deployment/deploy-frontend.sh

# Database migrations
db-migrate:
	@echo "Running database migrations..."
	cd backend && source venv/bin/activate && alembic upgrade head

# Reset database
db-reset:
	@echo "Resetting database..."
	cd backend && source venv/bin/activate && alembic downgrade base && alembic upgrade head

# Generate documentation
docs:
	@echo "Generating documentation..."
	cd backend && source venv/bin/activate && python -c "import app.main; print('API docs available at http://localhost:8000/docs')"

# Setup GCP environment
setup-gcp:
	@echo "Setting up GCP environment..."
	./scripts/setup/gcp-setup.sh

# Backup database
backup-db:
	@echo "Backing up database..."
	./scripts/development/backup-db.sh

# Run security checks
security:
	@echo "Running security checks..."
	cd backend && source venv/bin/activate && bandit -r app/
	cd frontend && npm audit

# Load test data
load-test-data:
	@echo "Loading test data..."
	cd backend && source venv/bin/activate && python scripts/load_test_data.py

# Watch logs
logs:
	docker-compose logs -f

# Shell access to backend
shell-backend:
	docker-compose exec backend bash

# Shell access to frontend
shell-frontend:
	docker-compose exec frontend sh

# Shell access to database
shell-db:
	docker-compose exec postgres psql -U iam_user -d iam_analyzer

# Redis CLI
redis-cli:
	docker-compose exec redis redis-cli

# Full reset (dangerous)
reset-all: clean
	@echo "WARNING: This will remove all data, containers, and images"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if echo $$REPLY | grep -q '^[Yy]$$'; then \
		docker-compose down -v --rmi all; \
		docker system prune -af; \
	fi
