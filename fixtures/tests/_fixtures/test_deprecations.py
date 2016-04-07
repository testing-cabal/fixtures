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

import warnings

import testtools

from fixtures import Deprecations


MODULE = 'fixtures'


class TestDeprecations(testtools.TestCase):
    def test_enabled_raises(self):
        # When the Deprecations fixture is active, calling deprecated function
        # is an error.
        self.useFixture(Deprecations(MODULE))
        self.assertRaises(
            DeprecationWarning,
            lambda: warnings.warn('message ignored', DeprecationWarning))

    def test_ignore_deprecations(self):
        # When ignore_deprecations() in a test, deprecations are not an error.
        deprecations = self.useFixture(Deprecations(MODULE))
        deprecations.ignore_deprecations()
        warnings.warn('message ignored', DeprecationWarning)

    def test_expect_deprecations_here(self):
        # While in the expect_deprecations_here() context, deprecations are not
        # errors, and afterwards deprecations are errors.
        deprecations = self.useFixture(Deprecations(MODULE))
        with deprecations.expect_deprecations_here():
            warnings.warn('message ignored', DeprecationWarning)
        self.assertRaises(
            DeprecationWarning,
            lambda: warnings.warn('message ignored', DeprecationWarning))

    def test_other_module(self):
        # When the Deprecations fixture is active, deprecations from other
        # modules are ignored.
        self.useFixture(Deprecations('different_module'))
        warnings.warn('message ignored', DeprecationWarning)

    def test_null_case(self):
        # When the Deprecations fixture isn't used then deprecations are not
        # errors. This shows that python works as expected.
        warnings.warn('message ignored', DeprecationWarning)

    def test_restore_warnings(self):
        # When the test is done using the Deprecations fixture, the original
        # warning settings are restored to whatever they were before.
        warnings.filterwarnings('always', category=DeprecationWarning,
                                module=r'^%s\.' % MODULE)

        # Define a function so the warning always comes from the same line.
        def f():
            warnings.warn('deprecation warning', DeprecationWarning)

        f()
        with Deprecations(MODULE):
            self.assertRaises(DeprecationWarning, f)
        f()
