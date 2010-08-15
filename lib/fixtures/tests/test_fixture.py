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


class TestFixture(unittest.TestCase):

    def test_resetCallsSetUpCleanUp(self):
        calls = []
        class FixtureWithSetupOnly(fixtures.Fixture):
            def setUp(self):
                super(FixtureWithSetupOnly, self).setUp()
                calls.append('setUp')
                self.addCleanup(calls.append, 'cleanUp')
        fixture = FixtureWithSetupOnly()
        fixture.setUp()
        fixture.reset()
        fixture.cleanUp()
        self.assertEqual(['setUp', 'cleanUp', 'setUp', 'cleanUp'], calls)

    def test_cleanUpcallscleanups_swallows_exceptions(self):
        calls = []
        def raise_exception1():
            calls.append('1')
            raise Exception('woo')
        def raise_exception2():
            calls.append('2')
            raise Exception('woo')
        class FixtureWithException(fixtures.Fixture):
            def setUp(self):
                super(FixtureWithException, self).setUp()
                self.addCleanup(raise_exception2)
                self.addCleanup(raise_exception1)
        fixture = FixtureWithException()
        fixture.setUp()
        fixture.cleanUp()
        self.assertEqual(['1', '2'], calls)

    def test_exit_propogates_exceptions(self):
        fixture = fixtures.Fixture()
        fixture.__enter__()
        self.assertEqual(False, fixture.__exit__(None, None, None))


class TestFunctionFixture(unittest.TestCase):

    def test_setup_only(self):
        fixture = fixtures.FunctionFixture(lambda: 42)
        fixture.setUp()
        self.assertEqual(42, fixture.fn_result)
        fixture.cleanUp()
        self.assertFalse(hasattr(fixture, 'fn_result'))

    def test_cleanup(self):
        results = []
        fixture = fixtures.FunctionFixture(lambda: 84, results.append)
        fixture.setUp()
        self.assertEqual(84, fixture.fn_result)
        self.assertEqual([], results)
        fixture.cleanUp()
        self.assertEqual([84], results)

    def test_reset(self):
        results = []
        expected = [21, 7]
        def setUp():
            return expected.pop(0)
        def reset(result):
            results.append(('reset', result))
            return expected.pop(0)
        fixture = fixtures.FunctionFixture(setUp, results.append, reset)
        fixture.setUp()
        self.assertEqual([], results)
        fixture.reset()
        self.assertEqual([('reset', 21)], results)
        self.assertEqual(7, fixture.fn_result)
        fixture.cleanUp()
        self.assertEqual([('reset', 21), 7], results)
