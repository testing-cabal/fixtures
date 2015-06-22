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

__all__ = [
    'PythonPathEntry'
    ]

import sys

from fixtures import Fixture


class PythonPathEntry(Fixture):
    """Add a path to sys.path.
    
    If the path is already in sys.path, sys.path will not be altered.
    """

    def __init__(self, directory):
        """Create a PythonPathEntry.

        :param directory: The directory to add to sys.path.
        """
        self.directory = directory

    def _setUp(self):
        if self.directory in sys.path:
            return
        self.addCleanup(sys.path.remove, self.directory)
        sys.path.append(self.directory)
