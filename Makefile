.PHONY: help build test test-cov lint fmt clean profile install

PY ?= python

help:
	@echo "Available targets:"
	@echo "  install     Install the package + dev dependencies (pip)"
	@echo "  build       Run the pipeline (data/raw → data/processed)"
	@echo "  test        Run unit + contract tests"
	@echo "  test-cov    Run tests with coverage report"
	@echo "  lint        Lint with ruff"
	@echo "  fmt         Auto-format with ruff"
	@echo "  profile     Print schema + null counts of data/processed/"
	@echo "  clean       Remove derived files and caches"

install:
	$(PY) -m pip install -r requirements.txt

build:
	$(PY) -m src.pipeline

test:
	$(PY) -m pytest -q

test-cov:
	$(PY) -m pytest --cov=src --cov-report=term-missing

lint:
	$(PY) -m ruff check src tests

fmt:
	$(PY) -m ruff format src tests

profile:
	$(PY) -m src.profile

clean:
	rm -rf data/interim/* data/processed/*.csv
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
