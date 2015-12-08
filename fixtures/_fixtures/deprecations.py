# Copyright 2015 IBM Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import absolute_import

import contextlib
import re
import warnings  # conflicts with the local warnings module so absolute_import

import fixtures


class Deprecations(fixtures.Fixture):
    """Prevent calls to deprecated function.

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

    :param str module: The name of the module. Deprecated function called from
                       this module will be errors.

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
