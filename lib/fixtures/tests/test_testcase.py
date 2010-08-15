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

import unittest
import testtools

import fixtures
from fixtures.tests.helpers import LoggingFixture


class TestTestWithFixtures(unittest.TestCase):

    def test_useFixture(self):
        fixture = LoggingFixture()
        class SimpleTest(testtools.TestCase, fixtures.TestWithFixtures):
            def test_foo(self):
                self.useFixture(fixture)
        result = unittest.TestResult()
        SimpleTest('test_foo').run(result)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(['setUp', 'cleanUp'], fixture.calls)
