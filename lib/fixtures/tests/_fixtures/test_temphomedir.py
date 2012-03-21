#  fixtures: Fixtures with cleanups for testing and convenience.
#
# Copyright (c) 2011 Canonical Ltd.
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

import testtools
from testtools.matchers import StartsWith

from fixtures import (
    TempDir,
    TempHomeDir,
    )

class TestTempDir(testtools.TestCase):

    def test_basic(self):
        fixture = TempHomeDir()
        sentinel = object()
        self.assertEqual(sentinel, getattr(fixture, 'path', sentinel))
        fixture.setUp()
        try:
            path = fixture.path
            self.assertTrue(os.path.isdir(path))
            self.assertEqual(path, os.environ.get("HOME"))
        finally:
            fixture.cleanUp()
            self.assertFalse(os.path.isdir(path))

    def test_under_dir(self):
        root = self.useFixture(TempDir()).path
        fixture = TempHomeDir(root)
        fixture.setUp()
        with fixture:
            self.assertThat(fixture.path, StartsWith(root))
