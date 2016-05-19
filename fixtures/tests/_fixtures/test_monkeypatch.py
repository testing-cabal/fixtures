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

import functools

import testtools
from testtools.matchers import Is

from fixtures import MonkeyPatch, TestWithFixtures

reference = 23

class C(object):
    def foo(self, arg):
        return arg
    @staticmethod
    def foo_static(): pass
    @classmethod
    def foo_cls(cls): pass

class D(object):
    def bar(self): pass
    def bar_two_args(self, arg):
        return (self, arg)
    @classmethod
    def bar_cls(cls):
        return cls
    @classmethod
    def bar_cls_args(cls, *args):
        return (cls,) + args
    @staticmethod
    def bar_static():
        pass
    @staticmethod
    def bar_static_args(*args):
        return args
    def bar_self_referential(self, *args, **kwargs):
        self.bar()

INST_C = C()

def fake(*args):
    return args
def fake2(arg): pass
def fake_no_args(): pass
def fake_no_args2(): pass
@staticmethod
def fake_static(): pass


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

    def _check_restored_static_or_class_method(self, oldmethod, oldmethod_inst,
            klass, methodname):
        restored_method = getattr(klass, methodname)
        restored_method_inst = getattr(klass(), methodname)
        self.assertEqual(oldmethod, restored_method)
        self.assertEqual(oldmethod, restored_method_inst)
        self.assertEqual(oldmethod_inst, restored_method)
        self.assertEqual(oldmethod_inst, restored_method_inst)
        restored_method()
        restored_method_inst()

    def test_patch_staticmethod_with_staticmethod(self):
        oldmethod = C.foo_static
        oldmethod_inst = C().foo_static
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo_static',
            D.bar_static)
        with fixture:
            C.foo_static()
            C().foo_static()
        self._check_restored_static_or_class_method(oldmethod, oldmethod_inst,
                C, 'foo_static')

    def test_patch_staticmethod_with_classmethod(self):
        oldmethod = C.foo_static
        oldmethod_inst = C().foo_static
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo_static',
            D.bar_cls)
        with fixture:
            C.foo_static()
            C().foo_static()
        self._check_restored_static_or_class_method(oldmethod, oldmethod_inst,
                C, 'foo_static')

    def test_patch_staticmethod_with_function(self):
        oldmethod = C.foo_static
        oldmethod_inst = C().foo_static
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo_static',
            fake_no_args)
        with fixture:
            C.foo_static()
            C().foo_static()
        self._check_restored_static_or_class_method(oldmethod, oldmethod_inst,
                C, 'foo_static')

    def test_patch_staticmethod_with_boundmethod(self):
        oldmethod = C.foo_static
        oldmethod_inst = C().foo_static
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo_static',
            D().bar)
        with fixture:
            C.foo_static()
            C().foo_static()
        self._check_restored_static_or_class_method(oldmethod, oldmethod_inst,
                C, 'foo_static')

    def test_patch_classmethod_with_staticmethod(self):
        oldmethod = C.foo_cls
        oldmethod_inst = C().foo_cls
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo_cls',
            D.bar_static_args)
        with fixture:
            (cls,) = C.foo_cls()
            self.expectThat(cls, Is(C))
            (cls,) = C().foo_cls()
            self.expectThat(cls, Is(C))
        self._check_restored_static_or_class_method(oldmethod, oldmethod_inst,
                C, 'foo_cls')

    def test_patch_classmethod_with_classmethod(self):
        oldmethod = C.foo_cls
        oldmethod_inst = C().foo_cls
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo_cls',
            D.bar_cls_args)
        with fixture:
            cls, target_class = C.foo_cls()
            self.expectThat(cls, Is(D))
            self.expectThat(target_class, Is(C))
            cls, target_class = C().foo_cls()
            self.expectThat(cls, Is(D))
            self.expectThat(target_class, Is(C))
        self._check_restored_static_or_class_method(oldmethod, oldmethod_inst,
                C, 'foo_cls')

    def test_patch_classmethod_with_function(self):
        oldmethod = C.foo_cls
        oldmethod_inst = C().foo_cls
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo_cls',
            fake)
        with fixture:
            (cls,) = C.foo_cls()
            self.expectThat(cls, Is(C))
            (cls, arg) = C().foo_cls(1)
            self.expectThat(cls, Is(C))
            self.assertEqual(1, arg)
        self._check_restored_static_or_class_method(oldmethod, oldmethod_inst,
                C, 'foo_cls')

    def test_patch_classmethod_with_boundmethod(self):
        oldmethod = C.foo_cls
        oldmethod_inst = C().foo_cls
        d = D()
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo_cls',
            d.bar_two_args)
        with fixture:
            slf, cls = C.foo_cls()
            self.expectThat(slf, Is(d))
            self.expectThat(cls, Is(C))
            slf, cls = C().foo_cls()
            self.expectThat(slf, Is(d))
            self.expectThat(cls, Is(C))
        self._check_restored_static_or_class_method(oldmethod, oldmethod_inst,
                C, 'foo_cls')

    def test_patch_function_with_staticmethod(self):
        oldmethod = fake_no_args
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.fake_no_args',
            D.bar_static)
        with fixture:
            fake_no_args()
        self.assertEqual(oldmethod, fake_no_args)

    def test_patch_function_with_classmethod(self):
        oldmethod = fake_no_args
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.fake_no_args',
            D.bar_cls)
        with fixture:
            fake_no_args()
        self.assertEqual(oldmethod, fake_no_args)

    def test_patch_function_with_function(self):
        oldmethod = fake_no_args
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.fake_no_args',
            fake_no_args2)
        with fixture:
            fake_no_args()
        self.assertEqual(oldmethod, fake_no_args)

    def test_patch_function_with_partial(self):
        oldmethod = fake_no_args
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.fake_no_args',
            functools.partial(fake, 1))
        with fixture:
            (ret,) = fake_no_args()
            self.assertEqual(1, ret)
        self.assertEqual(oldmethod, fake_no_args)

    def test_patch_function_with_boundmethod(self):
        oldmethod = fake_no_args
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.fake_no_args',
            D().bar)
        with fixture:
            fake_no_args()
        self.assertEqual(oldmethod, fake_no_args)

    def test_patch_boundmethod_with_staticmethod(self):
        oldmethod = INST_C.foo
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.INST_C.foo',
            D.bar_static)
        with fixture:
            INST_C.foo()
        self.assertEqual(oldmethod, INST_C.foo)

    def test_patch_boundmethod_with_classmethod(self):
        oldmethod = INST_C.foo
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.INST_C.foo',
            D.bar_cls)
        with fixture:
            INST_C.foo()
        self.assertEqual(oldmethod, INST_C.foo)

    def test_patch_boundmethod_with_function(self):
        oldmethod = INST_C.foo
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.INST_C.foo',
            fake_no_args)
        with fixture:
            INST_C.foo()
        self.assertEqual(oldmethod, INST_C.foo)

    def test_patch_boundmethod_with_boundmethod(self):
        oldmethod = INST_C.foo
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.INST_C.foo',
            D().bar)
        with fixture:
            INST_C.foo()
        self.assertEqual(oldmethod, INST_C.foo)
        sentinel = object()
        self.assertEqual(sentinel, INST_C.__dict__.get('foo', sentinel))

    def test_patch_unboundmethod_with_staticmethod(self):
        oldmethod = C.foo
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo',
            D.bar_static_args)
        with fixture:
            target_self, arg = INST_C.foo(1)
            self.expectThat(target_self, Is(INST_C))
            self.assertEqual(1, arg)
        self.assertEqual(oldmethod, C.foo)

    def test_patch_unboundmethod_with_classmethod(self):
        oldmethod = C.foo
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo',
            D.bar_cls_args)
        with fixture:
            c = C()
            cls, target_self, arg = c.foo(1)
            self.expectThat(cls, Is(D))
            self.expectThat(target_self, Is(c))
            self.assertEqual(1, arg)
        self.assertEqual(oldmethod, C.foo)

    def test_patch_unboundmethod_with_function(self):
        oldmethod = C.foo
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo',
            fake)
        with fixture:
            c = C()
            target_self, arg = c.foo(1)
            self.expectThat(target_self, Is(c))
            self.assertTrue(1, arg)
        self.assertEqual(oldmethod, C.foo)

    def test_patch_unboundmethod_with_boundmethod(self):
        oldmethod = C.foo
        d = D()
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo',
            d.bar_two_args)
        with fixture:
            c = C()
            slf, target_self = c.foo()
            self.expectThat(slf, Is(d))
            self.expectThat(target_self, Is(c))
        self.assertEqual(oldmethod, C.foo)

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
        oldmethod = C.foo_static
        oldmethod_inst = C().foo_static
        fixture1 = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo_static',
            fake_no_args)
        fixture2 = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo_static',
            fake_static)
        with fixture1:
            with fixture2:
                C.foo_static()
                C().foo_static()
        self._check_restored_static_or_class_method(oldmethod, oldmethod_inst,
            C, 'foo_static')

    def test_double_patch_classmethod(self):
        oldmethod = C.foo_cls
        oldmethod_inst = C().foo_cls
        fixture1 = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo_cls',
            fake)
        fixture2 = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo_cls',
            fake2)
        with fixture1:
            with fixture2:
                C.foo_cls()
                C().foo_cls()
        self._check_restored_static_or_class_method(oldmethod, oldmethod_inst,
            C, 'foo_cls')

    def test_patch_c_foo_with_instance_d_bar_self_referential(self):
        oldmethod = C.foo
        oldmethod_inst = C().foo
        fixture = MonkeyPatch(
            'fixtures.tests._fixtures.test_monkeypatch.C.foo',
            D().bar_self_referential)
        with fixture:
            C().foo()
        self.assertEqual(oldmethod, C.foo)
        # The method address changes with each instantiation of C, and method
        # equivalence just tests that. Compare the code objects instead.
        self.assertEqual(oldmethod_inst.__code__, C().foo.__code__)
