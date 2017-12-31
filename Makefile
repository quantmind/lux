
PYTHON ?= python
PIP ?= pip

.PHONY: help

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'


clean:		## cleanup
	rm -fr dist/ *.egg-info *.eggs .eggs build/
	find . -name '__pycache__' | xargs rm -rf

test:		## run unittests
	flake8
	$(PYTHON) -W ignore setup.py test -q --sequential

coverage:	## run unittests with coverage
	$(PYTHON) -W ignore setup.py test --coverage -q
