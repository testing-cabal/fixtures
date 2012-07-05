#  fixtures: Fixtures with cleanups for testing and convenience.
#
# Copyright (c) 2012, Robert Collins <robertc@robertcollins.net>
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

from testtools import TestCase
from testtools.matchers import (
    DirContains,
    DirExists,
    FileContains,
    Not,
    )

from fixtures import FileTree
from fixtures.tests.helpers import NotHasattr


class TestFileTree(TestCase):

    def test_no_path_at_start(self):
        # FileTree fixture doesn't create a path at the beginning.
        fixture = FileTree([])
        self.assertThat(fixture, NotHasattr('path'))

    def test_creates_directory(self):
        # It creates a temporary directory once set up.  That directory is
        # removed at cleanup.
        fixture = FileTree([])
        fixture.setUp()
        try:
            self.assertThat(fixture.path, DirExists())
        finally:
            fixture.cleanUp()
            self.assertThat(fixture.path, Not(DirExists()))

    def test_creates_files(self):
        # When given a list of file specifications, it creates those files
        # underneath the temporary directory.
        fixture = FileTree([('a', 'foo'), ('b', 'bar')])
        with fixture:
            path = fixture.path
            self.assertThat(path, DirContains(['a', 'b']))
            self.assertThat(os.path.join(path, 'a'), FileContains('foo'))
            self.assertThat(os.path.join(path, 'b'), FileContains('bar'))

    def test_creates_directories(self):
        # When given directory specifications, it creates those directories.
        fixture = FileTree([('a/', None), ('b/',)])
        with fixture:
            path = fixture.path
            self.assertThat(path, DirContains(['a', 'b']))
            self.assertThat(os.path.join(path, 'a'), DirExists())
            self.assertThat(os.path.join(path, 'b'), DirExists())

    def test_simpler_directory_syntax(self):
        # Directory specifications don't have to be tuples. They can be single
        # strings.
        fixture = FileTree(['a/'])
        with fixture:
            path = fixture.path
            self.assertThat(path, DirContains(['a']))
            self.assertThat(os.path.join(path, 'a'), DirExists())
