.PHONY: ci_setup
ci_setup:
	pip install -U pip
	pip install poetry
	poetry install
	pip install --index-url=http://download.qt.io/snapshots/ci/pyside/5.9/latest/ pyside2 --trusted-host download.qt.io

.PHONY: lint
lint: ; flake8

.PHONY: tests
tests: ; pytest -vvv tests
