SHELL := /bin/bash
define graphqlconfig
{\
  \"projects\": {\
	\"ene\": {\
	  \"schemaPath\": \"schema.graphql\",\
	  \"extensions\": {\
		\"endpoints\": {\
		  \"default\": \"https://graphql.anilist.co\"\
		}\
	  }\
	}\
  }\
}
endef

.PHONY: resources ui gql ci_setup lint test coverage

resources: ui

ui:
	pyside2-uic ene/resources/main_window.ui -o ene/resources/main_window_uic.py
	pyside2-uic ene/resources/settings_window.ui -o ene/resources/settings_window_uic.py


gql:
	echo -e ${graphqlconfig} > .graphqlconfig
	graphql get-schema
	tools/format_graphql_schema.py schema.graphql > ene/api/schema.graphqls
	rm schema.graphql
	rm .graphqlconfig
	tools/make_enums.py ene/api/schema.graphqls > ene/api/enums.py

ci_setup:
	pip install -U pip
	pip install -U poetry
	poetry install

lint:
	python -m flake8 ene
	python -m pylint --rcfile=.pylintrc ene

test:
	python -m pytest -s -vvv tests;

coverage:
	python -m pytest -vvv -s --cov=ene tests 
	pip install codecov
	codecov
