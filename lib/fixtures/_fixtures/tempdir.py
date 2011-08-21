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
    'TempDir'
    ]

import shutil
import tempfile

from fixtures import Fixture


class TempDir(Fixture):
    """Create a temporary directory.

    :ivar path: The path of the temporary directory.
    """

    def __init__(self, rootdir=None):
        """Create a TempDir.

        :param rootdir: If supplied force the tempoary directory to be a child
            of rootdir.
        """
        Fixture.setUp(self)
        self.rootdir = rootdir

    def setUp(self):
        Fixture.setUp(self)
        self.path = tempfile.mkdtemp(dir=self.rootdir)
        self.addCleanup(shutil.rmtree, self.path, ignore_errors=True)
