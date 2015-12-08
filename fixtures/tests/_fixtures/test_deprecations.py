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

    def test_expect_deprecations(self):
        # When expect_deprecations in a test, deprecations are not an error.
        deprecations = self.useFixture(Deprecations(MODULE))
        deprecations.expect_deprecations()
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
