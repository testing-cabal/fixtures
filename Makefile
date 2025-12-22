PYTHON ?= python3

all: check

check:
	$(PYTHON) -m testtools.run tests.test_suite

clean:
	find . -name '*.pyc' -print0 | xargs -0 rm -f

TAGS: fixtures/*.py tests/*.py
	ctags -e -R fixtures/ tests/

tags: fixtures/*.py tests/*.py
	ctags -R fixtures/ tests/

.PHONY: all check clean
