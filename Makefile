.PHONY: tests all unit integration clean dependencies tdd html purge dist

GIT_ROOT		:= $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
VENV_ROOT		:= $(GIT_ROOT)/.venv
VENV			?= $(VENV_ROOT)
BENTO_BIN		:= $(shell which bento)
BENTO_EMAIL		:= gabriel@nacaolivre.org

export VENV



all: dependencies tests

$(VENV):  # creates $(VENV) folder if does not exist
	python3 -mvenv $(VENV)
	$(VENV)/bin/pip install -U pip setuptools

$(VENV)/bin/steadymark $(VENV)/bin/sphinx-build $(VENV)/bin/twine $(VENV)/bin/nosetests $(VENV)/bin/python $(VENV)/bin/pip: # installs latest pip
	test -e $(VENV)/bin/pip || make $(VENV)
	$(VENV)/bin/pip install -r development.txt
	$(VENV)/bin/pip install -e .


tests: unit integration docs

tdd: $(VENV)/bin/nosetests  # runs all tests
	$(VENV)/bin/nosetests tests --with-watch --cover-erase

# Install dependencies
dependencies: | $(VENV)/bin/nosetests
	$(VENV)/bin/pip install -r development.txt

# runs unit tests
unit: $(VENV)/bin/nosetests  # runs only unit tests
	$(VENV)/bin/nosetests --cover-erase tests/unit

docs: $(VENV)/bin/steadymark
	$(VENV)/bin/steadymark README.md

# runs integration tests
integration: $(VENV)/bin/nosetests  # runs integration tests
	$(VENV)/bin/nosetests tests/integration


release: | clean bento unit integration tests html
	@rm -rf dist/*
	@./.release
	@make pypi

bento: | $(BENTO_BIN)
	$(BENTO_BIN) --agree --email=$(BENTO_EMAIL) check --all

dist: | clean
	$(VENV)/bin/python setup.py build sdist

pypi: dist | $(VENV)/bin/twine
	$(VENV)/bin/twine upload dist/*.tar.gz

# cleanup temp files
clean:
	rm -rf $(HTML_ROOT) build dist


# purge all virtualenv and temp files, causes everything to be rebuilt
# from scratch by other tasks
purge: clean
	rm -rf $(VENV)
