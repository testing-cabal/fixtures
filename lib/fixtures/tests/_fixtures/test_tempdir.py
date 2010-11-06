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

import testtools

import fixtures
from fixtures import TempDir, TestWithFixtures

        
class TestTempDir(testtools.TestCase, TestWithFixtures):

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
