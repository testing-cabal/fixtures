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

__all__ = [
    'NestedTempfile',
    'TempDir',
    ]

import errno
import os
import shutil
import tempfile

import fixtures


class TempDir(fixtures.Fixture):
    """Create a temporary directory.

    :ivar path: The path of the temporary directory.
    """

    def __init__(self, rootdir=None):
        """Create a TempDir.

        :param rootdir: If supplied force the temporary directory to be a
            child of rootdir.
        """
        self.rootdir = rootdir

    def setUp(self):
        super(TempDir, self).setUp()
        self.path = tempfile.mkdtemp(dir=self.rootdir)
        self.addCleanup(shutil.rmtree, self.path, ignore_errors=True)

    def make_tree(self, shape):
        create_normal_shape(self.path, normalize_shape(shape))


class NestedTempfile(fixtures.Fixture):
    """Nest all temporary files and directories inside another directory.

    This temporarily monkey-patches the default location that the `tempfile`
    package creates temporary files and directories in to be a new temporary
    directory. This new temporary directory is removed when the fixture is torn
    down.
    """

    def setUp(self):
        super(NestedTempfile, self).setUp()
        tempdir = self.useFixture(TempDir()).path
        patch = fixtures.MonkeyPatch("tempfile.tempdir", tempdir)
        self.useFixture(patch)


def normalize_entry(entry):
    """Normalize a file shape entry.

    'Normal' entries are either ("file", "content") or ("directory/", None).

    Standalone strings get turned into 2-tuples, with files getting made-up
    contents.  Singletons are treated the same.

    If something that looks like a file has no content, or something that
    looks like a directory has content, we raise an error, as we don't know
    whether the developer really intends a file or really intends a directory.

    :return: A list of 2-tuples containing paths and contents.
    """
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
    """Normalize a shape of a file tree to create.

    Normalizes each entry and returns a sorted list of entries.
    """
    return sorted(map(normalize_entry, shape))


def create_normal_shape(base_directory, shape):
    """Create a file tree from 'shape' in 'base_directory'.

    'shape' must be a list of 2-tuples of (name, contents).  If name ends with
    '/', then contents must be None, as it will be created as a directory.
    Otherwise, contents must be provided.

    If either a file or directory is specified but the parent directory
    doesn't exist, will create the parent directory.
    """
    for name, contents in shape:
        name = os.path.join(base_directory, name)
        if name[-1] == '/':
            os.makedirs(name)
        else:
            base_dir = os.path.dirname(name)
            try:
                os.makedirs(base_dir)
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise
            f = open(name, 'w')
            f.write(contents)
            f.close()
