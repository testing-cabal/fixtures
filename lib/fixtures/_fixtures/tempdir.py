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
