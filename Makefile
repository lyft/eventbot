SHELL := /bin/bash

.PHONY: test # run all test suites
test: test_unit test_integration

.PHONY: test_unit
test_unit:
	mkdir -p build
	# APPLICATION_ENV=localtest causes it to not use the development database. This is useful for running tests locally
	# and not nuke your development database.
	APPLICATION_ENV=localtest \
	py.test \
	--junitxml=build/unit.xml \
	--cov=eventbot \
	--cov-report xml \
	--cov-report html \
	--cov-report term \
	--no-cov-on-fail \
	tests/unit

.PHONY: coverage # build HTML coverage report
coverage:
	mkdir -p build/coverage
	py.test --cov=eventbot --cov-report=html tests/unit

.PHONY: test_integration # run integration tests
test_integration:
	mkdir -p build
	## disabled until we add some integration tests
	#py.test --junit-xml=build/int.xml tests/integration

.PHONY: test_lint
test_lint:
	mkdir -p build
	set -o pipefail; flake8 eventbot/ | sed "s#^\./##" > build/flake8.txt || (cat build/flake8.txt && exit 1)
