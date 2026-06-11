.PHONY: install run test clean docker-build docker-run lint

install:
	pip install -r requirements.txt

run:
	python scripts/run_pipeline.py

run-json:
	python scripts/run_pipeline.py --output-json

schedule:
	python scripts/run_pipeline.py --schedule daily

test:
	pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

test-simple:
	pytest tests/ -v

clean:
	rm -rf logs/*.log
	rm -rf logs/*.json
	rm -rf __pycache__
	rm -rf src/**/__pycache__
	rm -rf tests/__pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov

docker-build:
	docker compose build

docker-run:
	docker compose run --rm pipeline

docker-run-scheduled:
	docker compose up pipeline-scheduled -d

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff format src/ tests/
