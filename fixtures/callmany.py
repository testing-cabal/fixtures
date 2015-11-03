#  fixtures: Fixtures with cleanups for testing and convenience.
#
# Copyright (c) 2010, Robert Collins <robertc@robertcollins.net>
#
# Licensed under either the Apache License, Version 2.0 or the BSD 3-clause
# license at the users choice. A copy of both licenses are available in the
# project source as Apache-2.0 and BSD. You may not use this file except in
# compliance with one of these two licences.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under these licenses is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# license you chose for the specific language governing permissions and
# limitations under that license.

__all__ = [
    'CallMany',
    ]

import sys

from testtools.compat import (
    reraise,
    )
from testtools.helpers import try_import


class MultipleExceptions(Exception):
    """Report multiple exc_info tuples in self.args."""

MultipleExceptions = try_import(
    "testtools.MultipleExceptions", MultipleExceptions)


class CallMany(object):
    """A stack of functions which will all be called on __call__.

    CallMany also acts as a context manager for convenience.

    Functions are called in last pushed first executed order.

    This is used by Fixture to manage its addCleanup feature.
    """

    def __init__(self):
        self._cleanups = []

    def push(self, cleanup, *args, **kwargs):
        """Add a function to be called from __call__.

        On __call__ all functions are called - see __call__ for details on how
        multiple exceptions are handled.

        :param cleanup: A callable to call during cleanUp.
        :param *args: Positional args for cleanup.
        :param kwargs: Keyword args for cleanup.
        :return: None
        """
        self._cleanups.append((cleanup, args, kwargs))

    def __call__(self, raise_errors=True):
        """Run all the registered functions.

        :param raise_errors: Deprecated parameter from before testtools gained
            MultipleExceptions. raise_errors defaults to True. When True
            if exception(s) are raised while running functions, they are
            re-raised after all the functions have run.  If multiple exceptions
            are raised, they are all wrapped into a MultipleExceptions object,
            and that is raised.

            Thus, to catch a specific exception from a function run by __call__,
            you need to catch both the exception and MultipleExceptions, and
            then check within a MultipleExceptions instance for an occurance of
            the type you wish to catch.
        :return: Either None or a list of the exc_info() for each exception
            that occured if raise_errors was False.
        """
        cleanups = reversed(self._cleanups)
        self._cleanups = []
        result = []
        for cleanup, args, kwargs in cleanups:
            try:
                cleanup(*args, **kwargs)
            except Exception:
                result.append(sys.exc_info())
        if result and raise_errors:
            if 1 == len(result):
                error = result[0]
                reraise(error[0], error[1], error[2])
            else:
                raise MultipleExceptions(*result)
        if not raise_errors:
            return result

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self()
        return False  # Propagate exceptions from the with body.
