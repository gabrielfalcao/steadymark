all: test

filename=steadymark-`python -c 'import steadymark;print steadymark.version'`.tar.gz

export PYTHONPATH:=  ${PWD}

test: clean
	@echo "Running code examples from README.md as tests"
	@python steadymark/__init__.py

clean:
	@printf "Cleaning up files that are already in .gitignore... "
	@for pattern in `cat .gitignore`; do rm -rf $$pattern; find . -name "$$pattern" -exec rm -rf {} \;; done
	@echo "OK!"

release: test publish
	@printf "Exporting to $(filename)... "
	@tar czf $(filename) steadymark setup.py README.md COPYING
	@echo "DONE!"

publish:
	@python setup.py sdist register upload
