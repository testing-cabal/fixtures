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


def normalize_entry(entry):
    if isinstance(entry, basestring):
        if entry[-1] == '/':
            return (entry, None)
        else:
            return (entry, "The file '%s'." % (entry,))
    else:
        if len(entry) == 1:
            return normalize_entry(entry[0])
        elif len(entry) == 2:
            name, content = entry
            is_dir = (name[-1] == '/')
            if ((is_dir and content is not None)
                or (not is_dir and content is None)):
                raise ValueError(
                    "Directories must end with '/' and have no content, "
                    "files do not end with '/' and must have content, got %r"
                    % (entry,))
            return entry
        else:
            raise ValueError(
                "Invalid file or directory description: %r" % (entry,))


def normalize_shape(shape):
    normal_shape = []
    for entry in sorted(shape):
        normal_shape.append(normalize_entry(entry))
    return normal_shape


def create_normal_shape(root, shape):
    for name, contents in shape:
        name = os.path.join(root, name)
        if name[-1] == '/':
            os.mkdir(name)
        else:
            f = open(name, 'w')
            f.write(contents)
            f.close()


class FileTree(Fixture):
    """A structure of files and directories on disk."""

    def __init__(self, shape):
        """Create a ``FileTree``.

        :param shape: A list of descriptions of files and directories to make.
            Files are described as ``("filename", contents)`` and directories
            are written as ``"dirname/"``.  The trailing slash is necessary.
            Directories can also be written as ``("dirname/",)``.
        """
        super(FileTree, self).__init__()
        self._shape = normalize_shape(shape)

    def setUp(self):
        super(FileTree, self).setUp()
        tempdir = self.useFixture(TempDir())
        self.path = tempdir.path
        create_normal_shape(self.path, self._shape)
