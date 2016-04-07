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
    def foo(self): pass
    @staticmethod
    def foo_staticmethod(): pass
    @classmethod
    def foo_classmethod(cls): pass

def fake(arg): pass
def fake2(arg): pass
def fake_no_args(): pass
@staticmethod
def fake_staticmethod(): pass
@classmethod
def fake_classmethod(cls): pass


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

    def _check_static_or_class_method(self, name, new_method):
        oldmethod = getattr(C, name)
        oldmethod_inst = getattr(C(), name)
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.%s' % name,
            new_method)
        with fixture:
            getattr(C, name)()
            getattr(C(), name)()

        restored_method = getattr(C, name)
        restored_method_inst = getattr(C(), name)
        self.assertEqual(oldmethod, restored_method)
        self.assertEqual(oldmethod, restored_method_inst)
        self.assertEqual(oldmethod_inst, restored_method)
        self.assertEqual(oldmethod_inst, restored_method_inst)
        restored_method()
        restored_method_inst()

    def test_patch_staticmethod(self):
        self._check_static_or_class_method('foo_staticmethod', fake_no_args)

    def test_patch_staticmethod_with_staticmethod(self):
        self._check_static_or_class_method('foo_staticmethod',
                fake_staticmethod)

    def test_patch_classmethod(self):
        self._check_static_or_class_method('foo_classmethod', fake)

    def test_patch_classmethod_with_classmethod(self):
        self._check_static_or_class_method('foo_classmethod', fake_classmethod)

    def test_patch_instancemethod(self):
        oldmethod = C.foo
        oldmethod_inst = C().foo
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo',
            fake)
        with fixture:
            C().foo()

        self.assertEqual(oldmethod, C.foo)
        # The method address changes with each instantiation of C, and method
        # equivalence just tests that. Compare the code objects instead.
        self.assertEqual(oldmethod_inst.__code__, C().foo.__code__)

    def test_double_patch_instancemethod(self):
        oldmethod = C.foo
        oldmethod_inst = C().foo
        fixture1 = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo',
            fake)
        fixture2 = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo',
            fake2)
        with fixture1:
            with fixture2:
                C().foo()

        self.assertEqual(oldmethod, C.foo)
        # The method address changes with each instantiation of C, and method
        # equivalence just tests that. Compare the code objects instead.
        self.assertEqual(oldmethod_inst.__code__, C().foo.__code__)

    def test_double_patch_staticmethod(self):
        oldmethod = C.foo_staticmethod
        oldmethod_inst = C().foo_staticmethod
        fixture1 = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo_staticmethod',
            fake_no_args)
        fixture2 = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo_staticmethod',
            fake_staticmethod)
        with fixture1:
            with fixture2:
                C.foo_staticmethod()
                C().foo_staticmethod()

        restored_method = C.foo_staticmethod
        restored_method_inst = C().foo_staticmethod
        self.assertEqual(oldmethod, restored_method)
        self.assertEqual(oldmethod, restored_method_inst)
        self.assertEqual(oldmethod_inst, restored_method)
        self.assertEqual(oldmethod_inst, restored_method_inst)
        restored_method()
        restored_method_inst()

    def test_double_patch_classmethod(self):
        oldmethod = C.foo_classmethod
        oldmethod_inst = C().foo_classmethod
        fixture1 = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo_classmethod',
            fake)
        fixture2 = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo_classmethod',
            fake_classmethod)
        with fixture1:
            with fixture2:
                C.foo_classmethod()
                C().foo_classmethod()

        restored_method = C.foo_classmethod
        restored_method_inst = C().foo_classmethod
        self.assertEqual(oldmethod, restored_method)
        self.assertEqual(oldmethod, restored_method_inst)
        self.assertEqual(oldmethod_inst, restored_method)
        self.assertEqual(oldmethod_inst, restored_method_inst)
        restored_method()
        restored_method_inst()
