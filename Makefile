.PHONY: ci_setup
ci_setup:
	pip install -U pip
	pip install -U poetry
	poetry install

.PHONY: lint
lint: ; flake8

.PHONY: tests
tests: ; pytest -vvv tests
