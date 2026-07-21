
.PHONY: help install test run scrape facebook docker-build docker-up docker-down clean setup-db

# Colors for output
GREEN := \033[0;32m
RED := \033[0;31m
YELLOW := \033[0;33m
NC := \033[0m 

help:
	@echo "$(GREEN)Available commands:$(NC)"
	@echo "  $(YELLOW)make install$(NC)      - Install dependencies"
	@echo "  $(YELLOW)make test$(NC)         - Run tests"
	@echo "  $(YELLOW)make scrape$(NC)       - Run Craigslist scraper"
	@echo "  $(YELLOW)make facebook$(NC)     - Run Facebook automation"
	@echo "  $(YELLOW)make run$(NC)          - Run assessment menu"
	@echo "  $(YELLOW)make setup-db$(NC)     - Setup databases"
	@echo "  $(YELLOW)make docker-build$(NC) - Build Docker image"
	@echo "  $(YELLOW)make docker-up$(NC)    - Start Docker services"
	@echo "  $(YELLOW)make docker-down$(NC)  - Stop Docker services"
	@echo "  $(YELLOW)make clean$(NC)        - Clean data and logs"

install:
	@echo "$(GREEN)Installing dependencies...$(NC)"
	pip install -r requirements.txt
	@echo "$(GREEN) Installation complete$(NC)"

test:
	@echo "$(GREEN)Running tests...$(NC)"
	pytest tests/ -v --cov=craigslist_scraper --cov-report=html
	@echo "$(GREEN) Tests complete. Coverage report in htmlcov/$(NC)"

scrape:
	@echo "$(GREEN)Running Craigslist scraper...$(NC)"
	cd craigslist_scraper && scrapy crawl craigslist -a cities=milwaukee,columbus -o ../data/listings_$$(date +%Y%m%d_%H%M%S).json
	@echo "$(GREEN) Scraper complete. Output in data/$(NC)"

facebook:
	@echo "$(GREEN)Running Facebook automation...$(NC)"
	python -m fb_automation.facebook_api
	@echo "$(GREEN) Facebook automation complete$(NC)"

run:
	@echo "$(GREEN)Running assessment...$(NC)"
	python main.py

setup-db:
	@echo "$(GREEN)Setting up databases...$(NC)"
	python setup_database.py
	@echo "$(GREEN) Database setup complete$(NC)"

docker-build:
	@echo "$(GREEN)Building Docker image...$(NC)"
	docker-compose build
	@echo "$(GREEN) Docker build complete$(NC)"

docker-up:
	@echo "$(GREEN)Starting Docker services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN) Services started.$(NC)"
	@echo "  PostgreSQL: localhost:5432"
	@echo "  MySQL: localhost:3306"
	@echo "  MongoDB: localhost:27017"
	@echo "  phpMyAdmin: http://localhost:8080"
	@echo "  pgAdmin: http://localhost:5050"

docker-down:
	@echo "$(YELLOW)Stopping Docker services...$(NC)"
	docker-compose down
	@echo "$(GREEN) Services stopped$(NC)"

clean:
	@echo "$(YELLOW)Cleaning data and logs...$(NC)"
	rm -rf data/*.json data/*.csv
	rm -rf logs/*.log
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .pytest_cache .coverage htmlcov
	rm -rf *.pyc
	@echo "$(GREEN) Clean complete$(NC)"

format:
	@echo "$(GREEN)Formatting code...$(NC)"
	black craigslist_scraper/ fb_automation/ tests/ config/ utils/
	@echo "$(GREEN) Formatting complete$(NC)"

lint:
	@echo "$(GREEN)Linting code...$(NC)"
	flake8 craigslist_scraper/ fb_automation/ tests/ config/ utils/ --max-line-length=120
	@echo "$(GREEN) Linting complete$(NC)"