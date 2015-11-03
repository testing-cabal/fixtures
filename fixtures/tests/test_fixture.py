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
from testtools.content import text_content
from testtools.testcase import skipIf

import fixtures
from fixtures.fixture import gather_details
from fixtures.tests.helpers import LoggingFixture


require_gather_details = skipIf(gather_details is None,
        "gather_details() is not available.")


# Note: the cleanup related tests are strictly speaking redundant, IFF they are
# replaced with contract tests for correct use of CallMany.
class TestFixture(testtools.TestCase):

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

    def test_reset_raises_if_cleanup_raises(self):
        class FixtureWithSetupOnly(fixtures.Fixture):
            def do_raise(self):
                raise Exception('foo')
            def setUp(self):
                super(FixtureWithSetupOnly, self).setUp()
                self.addCleanup(self.do_raise)
        fixture = FixtureWithSetupOnly()
        fixture.setUp()
        exc = self.assertRaises(Exception, fixture.reset)
        self.assertEqual(('foo',), exc.args)

    def test_cleanUp_raise_first_false_callscleanups_returns_exceptions(self):
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
        exceptions = fixture.cleanUp(raise_first=False)
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
        fixture = fixtures.Fixture()
        fixture.__enter__()
        self.assertEqual(False, fixture.__exit__(None, None, None))

    def test_exit_runs_all_raises_first_exception(self):
        calls = []
        def raise_exception1():
            calls.append('1')
            raise Exception('woo')
        def raise_exception2():
            calls.append('2')
            raise Exception('hoo')
        class FixtureWithException(fixtures.Fixture):
            def setUp(self):
                super(FixtureWithException, self).setUp()
                self.addCleanup(raise_exception2)
                self.addCleanup(raise_exception1)
        fixture = FixtureWithException()
        fixture.__enter__()
        exc = self.assertRaises(Exception, fixture.__exit__, None, None, None)
        self.assertEqual(('woo',), exc.args[0][1].args)
        self.assertEqual(('hoo',), exc.args[1][1].args)
        self.assertEqual(['1', '2'], calls)

    def test_useFixture(self):
        parent = LoggingFixture('-outer')
        nested = LoggingFixture('-inner', calls=parent.calls)
        parent.setUp()
        parent.useFixture(nested)
        parent.cleanUp()
        self.assertEqual(
            ['setUp-outer', 'setUp-inner', 'cleanUp-inner', 'cleanUp-outer'],
            parent.calls)

    @require_gather_details
    def test_useFixture_details_captured_from_setUp(self):
        # Details added during fixture set-up are gathered even if setUp()
        # fails with an unknown exception.
        class SomethingBroke(Exception): pass
        class BrokenFixture(fixtures.Fixture):
            def setUp(self):
                super(BrokenFixture, self).setUp()
                self.addDetail('content', text_content("foobar"))
                raise SomethingBroke()
        broken_fixture = BrokenFixture()
        class SimpleFixture(fixtures.Fixture):
            def setUp(self):
                super(SimpleFixture, self).setUp()
                self.useFixture(broken_fixture)
        simple_fixture = SimpleFixture()
        self.assertRaises(SomethingBroke, simple_fixture.setUp)
        self.assertEqual(
            {"content": text_content("foobar")},
            broken_fixture.getDetails())
        self.assertEqual(
            {"content": text_content("foobar")},
            simple_fixture.getDetails())

    @require_gather_details
    def test_useFixture_details_captured_from_setUp_MultipleExceptions(self):
        # Details added during fixture set-up are gathered even if setUp()
        # fails with (cleanly - with MultipleExceptions / SetupError).
        class SomethingBroke(Exception): pass
        class BrokenFixture(fixtures.Fixture):
            def _setUp(self):
                self.addDetail('content', text_content("foobar"))
                raise SomethingBroke()
        class SimpleFixture(fixtures.Fixture):
            def _setUp(self):
                self.useFixture(BrokenFixture())
        simple = SimpleFixture()
        e = self.assertRaises(fixtures.MultipleExceptions, simple.setUp)
        self.assertEqual(
            {"content": text_content("foobar")},
            e.args[-1][1].args[0])

    def test_getDetails(self):
        fixture = fixtures.Fixture()
        with fixture:
            self.assertEqual({}, fixture.getDetails())

    def test_details_from_child_fixtures_are_returned(self):
        parent = fixtures.Fixture()
        with parent:
            child = fixtures.Fixture()
            parent.useFixture(child)
            # Note that we add the detail *after* using the fixture: the parent
            # has to query just-in-time.
            child.addDetail('foo', 'content')
            self.assertEqual({'foo': 'content'}, parent.getDetails())
            # And dropping it from the child drops it from the parent.
            del child._details['foo']
            self.assertEqual({}, parent.getDetails())
            # After cleanup the child details are still gone.
            child.addDetail('foo', 'content')
        self.assertRaises(TypeError, parent.getDetails)

    def test_duplicate_details_are_disambiguated(self):
        parent = fixtures.Fixture()
        with parent:
            parent.addDetail('foo', 'parent-content')
            child = fixtures.Fixture()
            parent.useFixture(child)
            # Note that we add the detail *after* using the fixture: the parent
            # has to query just-in-time.
            child.addDetail('foo', 'child-content')
            self.assertEqual({'foo': 'parent-content',
                              'foo-1': 'child-content',}, parent.getDetails())

    def test_addDetail(self):
        fixture = fixtures.Fixture()
        with fixture:
            fixture.addDetail('foo', 'content')
            self.assertEqual({'foo': 'content'}, fixture.getDetails())
            del fixture._details['foo']
            self.assertEqual({}, fixture.getDetails())
            fixture.addDetail('foo', 'content')
        # Cleanup clears the details too.
        self.assertRaises(TypeError, fixture.getDetails)

    def test_setUp_subclassed(self):
        # Even though its no longer recommended, we need to be sure that
        # overriding setUp and calling super().setUp still works.
        class Subclass(fixtures.Fixture):
            def setUp(self):
                super(Subclass, self).setUp()
                self.fred = 1
                self.addCleanup(setattr, self, 'fred', 2)
        with Subclass() as f:
            self.assertEqual(1, f.fred)
        self.assertEqual(2, f.fred)

    def test__setUp(self):
        # _setUp is called, and cleanups can be registered by it.
        class Subclass(fixtures.Fixture):
            def _setUp(self):
                self.fred = 1
                self.addCleanup(setattr, self, 'fred', 2)
        with Subclass() as f:
            self.assertEqual(1, f.fred)
        self.assertEqual(2, f.fred)

    def test__setUp_fails(self):
        # when _setUp fails, the fixture is left ready-to-setUp, and any
        # details added during _setUp are captured.
        class Subclass(fixtures.Fixture):
            def _setUp(self):
                self.addDetail('log', text_content('stuff'))
                1/0
        f = Subclass()
        e = self.assertRaises(fixtures.MultipleExceptions, f.setUp)
        self.assertRaises(TypeError, f.cleanUp)
        self.assertIsInstance(e.args[0][1], ZeroDivisionError)
        self.assertIsInstance(e.args[1][1], fixtures.SetupError)
        self.assertEqual('stuff', e.args[1][1].args[0]['log'].as_text())

    def test__setUp_fails_cleanUp_fails(self):
        # when _setUp fails, cleanups are called, and their failure is captured
        # into the MultipleExceptions instance.
        class Subclass(fixtures.Fixture):
            def _setUp(self):
                self.addDetail('log', text_content('stuff'))
                self.addCleanup(lambda: 1/0)
                raise Exception('fred')
        f = Subclass()
        e = self.assertRaises(fixtures.MultipleExceptions, f.setUp)
        self.assertRaises(TypeError, f.cleanUp)
        self.assertEqual(Exception, e.args[0][0])
        self.assertEqual(ZeroDivisionError, e.args[1][0])
        self.assertEqual(fixtures.SetupError, e.args[2][0])
        self.assertEqual('stuff', e.args[2][1].args[0]['log'].as_text())

    def test_setup_failures_with_base_exception(self):
        # when _setUp fails with a BaseException (or subclass thereof) that
        # exception is propagated as is, but we still call cleanups etc.
        class MyBase(BaseException):pass
        log = []
        class Subclass(fixtures.Fixture):
            def _setUp(self):
                self.addDetail('log', text_content('stuff'))
                self.addCleanup(log.append, 'cleaned')
                raise MyBase('fred')
        f = Subclass()
        e = self.assertRaises(MyBase, f.setUp)
        self.assertRaises(TypeError, f.cleanUp)
        self.assertEqual(['cleaned'], log)


class TestFunctionFixture(testtools.TestCase):

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


class TestMethodFixture(testtools.TestCase):

    def test_no_setup_cleanup(self):
        class Stub:
            pass
        fixture = fixtures.MethodFixture(Stub())
        fixture.setUp()
        fixture.reset()
        self.assertIsInstance(fixture.obj, Stub)
        fixture.cleanUp()

    def test_setup_only(self):
        class Stub:
            def setUp(self):
                self.value = 42
        fixture = fixtures.MethodFixture(Stub())
        fixture.setUp()
        self.assertEqual(42, fixture.obj.value)
        self.assertIsInstance(fixture.obj, Stub)
        fixture.cleanUp()

    def test_cleanup_only(self):
        class Stub:
            value = None
            def tearDown(self):
                self.value = 42
        fixture = fixtures.MethodFixture(Stub())
        fixture.setUp()
        self.assertEqual(None, fixture.obj.value)
        self.assertIsInstance(fixture.obj, Stub)
        fixture.cleanUp()
        self.assertEqual(42, fixture.obj.value)

    def test_cleanup(self):
        class Stub:
            def setUp(self):
                self.value = 42
            def tearDown(self):
                self.value = 84
        fixture = fixtures.MethodFixture(Stub())
        fixture.setUp()
        self.assertEqual(42, fixture.obj.value)
        self.assertIsInstance(fixture.obj, Stub)
        fixture.cleanUp()
        self.assertEqual(84, fixture.obj.value)

    def test_custom_setUp(self):
        class Stub:
            def mysetup(self):
                self.value = 42
        obj = Stub()
        fixture = fixtures.MethodFixture(obj, setup=obj.mysetup)
        fixture.setUp()
        self.assertEqual(42, fixture.obj.value)
        self.assertEqual(obj, fixture.obj)
        fixture.cleanUp()

    def test_custom_cleanUp(self):
        class Stub:
            value = 42
            def mycleanup(self):
                self.value = None
        obj = Stub()
        fixture = fixtures.MethodFixture(obj, cleanup=obj.mycleanup)
        fixture.setUp()
        self.assertEqual(42, fixture.obj.value)
        self.assertEqual(obj, fixture.obj)
        fixture.cleanUp()
        self.assertEqual(None, fixture.obj.value)

    def test_reset(self):
        class Stub:
            def setUp(self):
                self.value = 42
            def tearDown(self):
                self.value = 84
            def reset(self):
                self.value = 126
        obj = Stub()
        fixture = fixtures.MethodFixture(obj, reset=obj.reset)
        fixture.setUp()
        self.assertEqual(obj, fixture.obj)
        self.assertEqual(42, obj.value)
        fixture.reset()
        self.assertEqual(126, obj.value)
        fixture.cleanUp()
        self.assertEqual(84, obj.value)
