# Copyright (c) 2015 IBM Corp.
#
# Licensed under either the Apache License, Version 2.0 or the BSD 3-clause
# license at the users choice. A copy of both licenses are available in the
# project source as Apache-2.0 and BSD. You may not use this file except in
# compliance with one of these two licences.

# Unless required by applicable law or agreed to in writing, software
# distributed under these licenses is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# license you chose for the specific language governing permissions and
# limitations under that license.

from __future__ import absolute_import

__all__ = [
    'Deprecations',
]

import contextlib
import re
import warnings  # conflicts with the local warnings module so absolute_import

import fixtures


class Deprecations(fixtures.Fixture):
    """Prevent calls to deprecated functions.

    This fixture can be added to a testcase to ensure that the code under test
    isn't calling deprecated function. It sets Python's `warnings` module for
    the module under test to "error" so that DeprecationWarning will be
    raised.

    You might want your application to not use any deprecated function.
    Deprecated function is going to be removed and sometimes is being removed
    because it's buggy and you shouldn't be using it.

    It can be difficult to tell just through code reviews that new code is
    calling deprecated function. This fixture can be used to protect you from
    developers proposing changes that use deprecated function.

    It can also be useful to be able to test if your application is still using
    some function that's been newly deprecated.

    :param str module: The name of a Python module. DeprecationWarnings emitted
                       from this module will cause an error to be raised.
    """

    def __init__(self, module):
        super(Deprecations, self).__init__()
        self._module = module

    def _setUp(self):
        module_regex = '^%s' % re.escape(self._module + '.')
        warnings.filterwarnings('error', category=DeprecationWarning,
                                module=module_regex)
        self.addCleanup(warnings.resetwarnings)

    def expect_deprecations(self):
        """Indicate that this test expects to call deprecated function.

        If you've got a test that you expect to call deprecated function and
        you don't want it to fail call this at the start of the test.
        """
        warnings.resetwarnings()

    @contextlib.contextmanager
    def expect_deprecations_here(self):
        """This section of code expects to call deprecated function.

        If you've got a test that part of it is testing deprecated function
        then wrap the part in this context manager::

            with self.deprecations.expect_deprecations_here():
                call_deprecated_function()

        """
        warnings.resetwarnings()

        yield

        module_regex = '^%s' % re.escape(self._module + '.')
        warnings.filterwarnings('error', category=DeprecationWarning,
                                module=module_regex)
