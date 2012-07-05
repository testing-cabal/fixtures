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
        for description in self._shape:
            try:
                name, contents = description
            except ValueError:
                name = description[0]
            name = os.path.join(path, name)
            if name[-1] == '/':
                os.mkdir(name)
            else:
                f = open(name, 'w')
                f.write(contents)
                f.close()
