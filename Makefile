.PHONY: help install install-dev test lint format run docker-up docker-down clean

help: ## Показать эту справку
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	pip install -r requirements.txt

install-dev: ## Установить зависимости для разработки
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test: ## Запустить тесты
	pytest

test-cov: ## Запустить тесты с покрытием
	pytest --cov=src --cov-report=html --cov-report=term

lint: ## Проверить код линтерами
	flake8 src/
	mypy src/

format: ## Форматировать код
	black src/ tests/
	isort src/ tests/

run: ## Запустить приложение локально
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

docker-up: ## Запустить через docker-compose
	docker-compose up --build

docker-down: ## Остановить docker-compose
	docker-compose down

clean: ## Очистить временные файлы
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete

