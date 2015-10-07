# Copyright 2014 IBM Corp.
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


import extras
import mock # Yes, we only test the rolling backport
import testtools

from fixtures import (
    MockPatch,
    MockPatchMultiple,
    MockPatchObject,
)


class Foo(object):
    def bar(self):
        return self


def mocking_bar(self):
    return 'mocked!'


class TestMockPatch(testtools.TestCase):
    def test_mock_patch_with_replacement(self):
        self.useFixture(MockPatch('%s.Foo.bar' % (__name__), mocking_bar))
        instance = Foo()
        self.assertEqual(instance.bar(), 'mocked!')

    def test_mock_patch_without_replacement(self):
        self.useFixture(MockPatch('%s.Foo.bar' % (__name__)))
        instance = Foo()
        self.assertIsInstance(instance.bar(), mock.MagicMock)


class TestMockMultiple(testtools.TestCase):
    def test_mock_multiple_with_replacement(self):
        self.useFixture(MockPatchMultiple('%s.Foo' % (__name__),
                                          bar=mocking_bar))
        instance = Foo()
        self.assertEqual(instance.bar(), 'mocked!')

    def test_mock_patch_without_replacement(self):
        self.useFixture(MockPatchMultiple(
            '%s.Foo' % (__name__),
            bar=MockPatchMultiple.DEFAULT))
        instance = Foo()
        self.assertIsInstance(instance.bar(), mock.MagicMock)


class TestMockPatchObject(testtools.TestCase):
    def test_mock_patch_object_with_replacement(self):
        self.useFixture(MockPatchObject(Foo, 'bar', mocking_bar))
        instance = Foo()
        self.assertEqual(instance.bar(), 'mocked!')

    def test_mock_patch_object_without_replacement(self):
        self.useFixture(MockPatchObject(Foo, 'bar'))
        instance = Foo()
        self.assertIsInstance(instance.bar(), mock.MagicMock)
