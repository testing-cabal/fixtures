#  fixtures: Fixtures with cleanups for testing and convenience.
#
# Copyright (c) 2010, Canonical Ltd.
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
    'TempHomeDir',
    ]

import fixtures


class TempHomeDir(fixtures.Fixture):
    """Create a temporary directory and set it as $HOME

    :ivar path: the path of the temporary directory.
    :ivar tempdir: The TempDir fixture providing the directory.
    """

    def __init__(self, rootdir=None):
        """Create a TempDir.

        :param rootdir: If supplied force the temporary directory to be a
            child of rootdir.
        """
        self.rootdir = rootdir

    def setUp(self):
        super(TempHomeDir, self).setUp()
        self.tempdir = self.useFixture(fixtures.TempDir(rootdir=self.rootdir))
        self.useFixture(fixtures.EnvironmentVariable("HOME", self.tempdir.path))

    @property
    def path(self):
        return self.tempdir.path
