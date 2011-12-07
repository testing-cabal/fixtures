PYTHONPATH:=$(shell pwd)/lib:${PYTHONPATH}
PYTHON ?= python

all: check

check:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m testtools.run \
	    fixtures.test_suite

clean:
	find . -name '*.pyc' -print0 | xargs -0 rm -f

TAGS: lib/fixtures/*.py lib/fixtures/tests/*.py
	ctags -e -R lib/fixtures/

tags: lib/fixtures/*.py lib/fixtures/tests/*.py
	ctags -R lib/fixtures/

.PHONY: all check clean
