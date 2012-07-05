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

__all__ = [
    'FileTree',
    ]

import os

from fixtures import Fixture
from fixtures._fixtures.tempdir import TempDir


class FileTree(Fixture):

    def __init__(self, shape):
        super(FileTree, self).__init__()
        self._shape = shape

    def setUp(self):
        super(FileTree, self).setUp()
        tempdir = self.useFixture(TempDir())
        self.path = path = tempdir.path
        for filename, contents in self._shape:
            f = open(os.path.join(path, filename), 'w')
            f.write(contents)
            f.close()
