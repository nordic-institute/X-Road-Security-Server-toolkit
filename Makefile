.PHONY: clean virtualenv test docker dist dist-upload

clean:
	find . -name '*.py[co]' -delete
	rm -rf dist
	rm -rf build
	rm -rf .eggs
	rm -rf .pytest_cache
	rm -rf coverage-report
	rm -rf .coverage
	rm -rf *.egg-info
	rm -rf tests/integration/X-Road
	rm -rf tests/end_to_end/.pytest_cache

virtualenv:
	virtualenv --prompt '|> xrdsst <| ' env
	env/bin/pip install -r requirements-dev.txt
	env/bin/python setup.py develop
	@echo
	@echo "VirtualENV Setup Complete. Now run: source env/bin/activate"
	@echo

install:
	python setup.py install

test: clean
	python -m pytest \
		-v \
		--cov=xrdsst/controllers \
		--cov-report=term \
		--cov-report=html:coverage-report \
		tests/unit\

lint: clean
	pylint --exit-zero --output-format=colorized --reports=y --rcfile=setup.cfg xrdsst tests

test-all: clean
	python -m pytest \
		-v \
		--cov=xrdsst/controllers \
		--cov-report=term \
		--cov-report=html:coverage-report \
		tests\

docker: clean
	docker build -t xrdsst:latest .

dist: clean
	python setup.py sdist bdist_wheel


