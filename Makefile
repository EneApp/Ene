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

.PHONY: list no_targets__ ui gql ci_setup lint test coverage

list:
	@sh -c "$(MAKE) -p no_targets__ | \
		awk -F':' '/^[a-zA-Z0-9][^\$$#\/\\t=]*:([^=]|$$)/ {\
			split(\$$1,A,/ /);for(i in A)print A[i]\
	}' | grep -v '__\$$' | grep -v 'make\[1\]' | grep -v 'Makefile' | sort"

no_targets__:

ui:
	pyside2-uic ene/resources/main_window.ui -o ene/resources/main_window_uic.py
	pyside2-uic ene/resources/settings_window.ui -o ene/resources/settings_window_uic.py


gql:
	echo -e ${graphqlconfig} > .graphqlconfig
	graphql get-schema
	tools/format_graphql_schema.py schema.graphql > tools/schema.graphqls
	rm schema.graphql
	rm .graphqlconfig
	tools/make_enums.py tools/schema.graphqls > ene/graphql/schema/enums.py

ci_setup:
	pip install -U pip
	pip install -U poetry
	poetry check
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

build:
	pyinstaller -F ene/__main__.py
