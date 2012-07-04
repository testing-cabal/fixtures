#  fixtures: Fixtures with cleanups for testing and convenience.
#
# Copyright (c) 2011, Robert Collins <robertc@robertcollins.net>
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

import sys

import testtools

from fixtures import (
    PythonPathEntry,
    TempDir,
    )


class TestPythonPathEntry(testtools.TestCase):

    def test_adds_missing_to_end_sys_path(self):
        uniquedir = self.useFixture(TempDir()).path
        fixture = PythonPathEntry(uniquedir)
        self.assertFalse(uniquedir in sys.path)
        with fixture:
            self.assertTrue(uniquedir in sys.path)
        self.assertFalse(uniquedir in sys.path)

    def test_doesnt_alter_existing_entry(self):
        existingdir = sys.path[0]
        expectedlen = len(sys.path)
        fixture = PythonPathEntry(existingdir)
        with fixture:
            self.assertTrue(existingdir in sys.path)
            self.assertEqual(expectedlen, len(sys.path))
        self.assertTrue(existingdir in sys.path)
        self.assertEqual(expectedlen, len(sys.path))
