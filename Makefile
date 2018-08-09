.PHONY: ci_setup
ci_setup:
	pip install -U pip
	pip install -U poetry
	poetry install

.PHONY: lint
lint:
	python -m flake8
	python -m pylint --rcfile=.pylintrc ene

.PHONY: tests
tests: ; pytest -vvv tests
