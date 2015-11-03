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

import types

import testtools

from fixtures.callmany import CallMany


class TestCallMany(testtools.TestCase):

    def test__call__raise_errors_false_callsall_returns_exceptions(self):
        calls = []
        def raise_exception1():
            calls.append('1')
            raise Exception('woo')
        def raise_exception2():
            calls.append('2')
            raise Exception('woo')
        call = CallMany()
        call.push(raise_exception2)
        call.push(raise_exception1)
        exceptions = call(raise_errors=False)
        self.assertEqual(['1', '2'], calls)
        # There should be two exceptions
        self.assertEqual(2, len(exceptions))
        # They should be a sys.exc_info tuple.
        self.assertEqual(3, len(exceptions[0]))
        type, value, tb = exceptions[0]
        self.assertEqual(Exception, type)
        self.assertIsInstance(value, Exception)
        self.assertEqual(('woo',), value.args)
        self.assertIsInstance(tb, types.TracebackType)

    def test_exit_propagates_exceptions(self):
        call = CallMany()
        call.__enter__()
        self.assertEqual(False, call.__exit__(None, None, None))

    def test_exit_runs_all_raises_first_exception(self):
        calls = []
        def raise_exception1():
            calls.append('1')
            raise Exception('woo')
        def raise_exception2():
            calls.append('2')
            raise Exception('hoo')
        call = CallMany()
        call.push(raise_exception2)
        call.push(raise_exception1)
        call.__enter__()
        exc = self.assertRaises(Exception, call.__exit__, None, None, None)
        self.assertEqual(('woo',), exc.args[0][1].args)
        self.assertEqual(('hoo',), exc.args[1][1].args)
        self.assertEqual(['1', '2'], calls)
