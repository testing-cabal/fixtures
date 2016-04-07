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

import testtools

from fixtures import MonkeyPatch, TestWithFixtures

reference = 23

class C(object):
    @staticmethod
    def foo(): pass
    def baz(self): pass
def bar(): pass
def qux(arg): pass
@staticmethod
def fiz(): pass


class TestMonkeyPatch(testtools.TestCase, TestWithFixtures):

    def test_patch_and_restore(self):
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.reference', 45)
        self.assertEqual(23, reference)
        fixture.setUp()
        try:
            self.assertEqual(45, reference)
        finally:
            fixture.cleanUp()
            self.assertEqual(23, reference)

    def test_patch_missing_attribute(self):
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.new_attr', True)
        self.assertFalse('new_attr' in globals())
        fixture.setUp()
        try:
            self.assertEqual(True, new_attr)
        finally:
            fixture.cleanUp()
            self.assertFalse('new_attr' in globals())

    def test_delete_existing_attribute(self):
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.reference',
            MonkeyPatch.delete)
        self.assertEqual(23, reference)
        fixture.setUp()
        try:
            self.assertFalse('reference' in globals())
        finally:
            fixture.cleanUp()
            self.assertEqual(23, reference)

    def test_delete_missing_attribute(self):
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.new_attr',
            MonkeyPatch.delete)
        self.assertFalse('new_attr' in globals())
        fixture.setUp()
        try:
            self.assertFalse('new_attr' in globals())
        finally:
            fixture.cleanUp()
            self.assertFalse('new_attr' in globals())

    def test_patch_staticmethod(self):
        oldfoo = C.foo
        oldfoo_inst = C().foo
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo',
            bar)
        with fixture:
            C.foo()
            C().foo()
        self.assertEqual(oldfoo, C.foo)
        self.assertEqual(oldfoo, C().foo)
        self.assertEqual(oldfoo_inst, C.foo)
        self.assertEqual(oldfoo_inst, C().foo)

    def test_patch_staticmethod_with_staticmethod(self):
        oldfoo = C.foo
        oldfoo_inst = C().foo
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo',
            fiz)
        with fixture:
            C.foo()
            C().foo()
        self.assertEqual(oldfoo, C.foo)
        self.assertEqual(oldfoo, C().foo)
        self.assertEqual(oldfoo_inst, C.foo)
        self.assertEqual(oldfoo_inst, C().foo)

    def test_patch_instancemethod(self):
        oldbaz = C.baz
        oldbaz_inst = C().baz
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.baz',
            qux)
        with fixture:
            C().baz()
        self.assertEqual(oldbaz, C.baz)
        # The method address changes with each instantiation of C, and method
        # equivalence just tests that. Compare the code objects instead.
        self.assertEqual(oldbaz_inst.__code__, C().baz.__code__)
