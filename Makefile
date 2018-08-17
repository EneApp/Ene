.PHONY: resources
resources: ui rcc

.PHONY: ui
ui:
	pyside2-uic ene/resources/main_window.ui -o ene/resources/main_window_uic.py
	pyside2-uic ene/resources/settings_window.ui -o ene/resources/settings_window_uic.py

.PHONY: rcc
rcc:
	pyside2-rcc -py3 ene/resources/style.qrc -o ene/resources/style_rc.py

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
