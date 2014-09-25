PYTHON ?= python

all: check

check:
	$(PYTHON) -m testtools.run fixtures.test_suite

clean:
	find . -name '*.pyc' -print0 | xargs -0 rm -f

TAGS: fixtures/*.py fixtures/tests/*.py
	ctags -e -R fixtures/

tags: fixtures/*.py fixtures/tests/*.py
	ctags -R fixtures/

.PHONY: all check clean
