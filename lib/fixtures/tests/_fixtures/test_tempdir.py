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

import os
import tempfile

import testtools
from testtools.matchers import StartsWith

from fixtures import (
    NestedTempfile,
    TempDir,
    )


class TestTempDir(testtools.TestCase):

    def test_basic(self):
        fixture = TempDir()
        sentinel = object()
        self.assertEqual(sentinel, getattr(fixture, 'path', sentinel))
        fixture.setUp()
        try:
            path = fixture.path
            self.assertTrue(os.path.isdir(path))
        finally:
            fixture.cleanUp()
            self.assertFalse(os.path.isdir(path))

    def test_under_dir(self):
        root = self.useFixture(TempDir()).path
        fixture = TempDir(root)
        fixture.setUp()
        with fixture:
            self.assertThat(fixture.path, StartsWith(root))

    def test_join(self):
        temp_dir = self.useFixture(TempDir())
        root = temp_dir.path
        relpath = 'foo/bar/baz'
        self.assertEqual(
            os.path.join(root, relpath), temp_dir.join(relpath))

    def test_join_multiple_children(self):
        temp_dir = self.useFixture(TempDir())
        root = temp_dir.path
        self.assertEqual(
            os.path.join(root, 'foo', 'bar', 'baz'),
            temp_dir.join('foo', 'bar', 'baz'))

    def test_join_naughty_children(self):
        temp_dir = self.useFixture(TempDir())
        root = temp_dir.path
        self.assertEqual(
            os.path.abspath(os.path.join(root, '..', 'bar', 'baz')),
            temp_dir.join('..', 'bar', 'baz'))


class NestedTempfileTest(testtools.TestCase):
    """Tests for `NestedTempfile`."""

    def test_normal(self):
        # The temp directory is removed when the context is exited.
        starting_tempdir = tempfile.gettempdir()
        with NestedTempfile():
            self.assertEqual(tempfile.tempdir, tempfile.gettempdir())
            self.assertNotEqual(starting_tempdir, tempfile.tempdir)
            self.assertTrue(os.path.isdir(tempfile.tempdir))
            nested_tempdir = tempfile.tempdir
        self.assertEqual(tempfile.tempdir, tempfile.gettempdir())
        self.assertEqual(starting_tempdir, tempfile.tempdir)
        self.assertFalse(os.path.isdir(nested_tempdir))

    def test_exception(self):
        # The temp directory is removed when the context is exited, even if
        # the code running in context raises an exception.
        class ContrivedException(Exception):
            pass
        try:
            with NestedTempfile():
                nested_tempdir = tempfile.tempdir
                raise ContrivedException
        except ContrivedException:
            self.assertFalse(os.path.isdir(nested_tempdir))
