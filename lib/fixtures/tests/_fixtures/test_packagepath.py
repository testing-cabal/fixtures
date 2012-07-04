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

import testtools

import fixtures
from fixtures import (
    PackagePathEntry,
    TempDir,
    )


class TestPackagePathEntry(testtools.TestCase):

    def test_adds_missing_to_end_package_path(self):
        uniquedir = self.useFixture(TempDir()).path
        fixture = PackagePathEntry('fixtures', uniquedir)
        self.assertFalse(uniquedir in fixtures.__path__)
        with fixture:
            self.assertTrue(uniquedir in fixtures.__path__)
        self.assertFalse(uniquedir in fixtures.__path__)

    def test_doesnt_alter_existing_entry(self):
        existingdir = fixtures.__path__[0]
        expectedlen = len(fixtures.__path__)
        fixture = PackagePathEntry('fixtures', existingdir)
        with fixture:
            self.assertTrue(existingdir in fixtures.__path__)
            self.assertEqual(expectedlen, len(fixtures.__path__))
        self.assertTrue(existingdir in fixtures.__path__)
        self.assertEqual(expectedlen, len(fixtures.__path__))
