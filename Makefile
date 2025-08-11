.PHONY: help install test test-unit test-integration test-e2e coverage lint format clean docker-build docker-run

# Default target
help:
	@echo "VIN Decoder Bot - Available Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  make install      - Install dependencies"
	@echo "  make install-dev  - Install dev dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests"
	@echo "  make test-unit    - Run unit tests"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-e2e     - Run e2e tests"
	@echo "  make coverage     - Run with coverage"
	@echo ""
	@echo "Quality:"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build - Build image"
	@echo "  make docker-run   - Run container"
	@echo ""
	@echo "Development:"
	@echo "  make run          - Run locally"
	@echo "  make clean        - Clean files"

run:
	python -m src.main

install:
	pip install -r requirements.txt

install-dev: install
	pip install -r requirements-test.txt

# Testing
test:
	python run_tests.py --type all

test-unit:
	python run_tests.py --type unit

test-integration:
	python run_tests.py --type integration

test-e2e:
	python run_tests.py --type e2e

coverage:
	python run_tests.py --coverage

# Code quality
lint:
	flake8 src --max-line-length=120
	mypy src --ignore-missing-imports

format:
	black src
	isort src

# Docker
docker-build:
	docker build -t vin-bot .

docker-run:
	docker run --rm --env-file .env vin-bot

# Cleanup
clean:
	rm -rf __pycache__ src/**/__pycache__ .venv
	rm -rf htmlcov .coverage .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
