.PHONY: clean virtualenv test docker dist dist-upload

clean:
	find . -name '*.py[co]' -delete
	rm -rf dist
	rm -rf build
	rm -rf .eggs
	rm -rf .pytest_cache
	rm -rf coverage-report
	rm .coverage
	rm -rf *.egg-info
	rm -rf tests/integration/X-Road

virtualenv:
	virtualenv --prompt '|> xrdsst <| ' env
	env/bin/pip install -r requirements-dev.txt
	env/bin/python setup.py develop
	@echo
	@echo "VirtualENV Setup Complete. Now run: source env/bin/activate"
	@echo

install:
	python setup.py install

test:
	python -m pytest \
		-v \
		--cov=xrdsst/controllers \
		--cov-report=term \
		--cov-report=html:coverage-report \
		tests/unit\

test-all:
	python -m pytest \
		-v \
		--pylint --pylint-rcfile=setup.cfg \
		--cov=xrdsst/controllers \
		--cov-report=term \
		--cov-report=html:coverage-report \
		tests\


docker: clean
	docker build -t xrdsst:latest .

dist: clean
	python setup.py sdist bdist_wheel


