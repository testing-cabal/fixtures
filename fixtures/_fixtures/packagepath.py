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
    'PackagePathEntry'
    ]

import sys

from fixtures import Fixture


class PackagePathEntry(Fixture):
    """Add a path to the path of a python package.

    The python package needs to be already imported.

    If this new path is already in the packages __path__ list then the __path__
    list will not be altered.
    """

    def __init__(self, packagename, directory):
        """Create a PackagePathEntry.

        :param directory: The directory to add to the package.__path__.
        """
        self.packagename = packagename
        self.directory = directory

    def _setUp(self):
        path = sys.modules[self.packagename].__path__
        if self.directory in path:
            return
        self.addCleanup(path.remove, self.directory)
        path.append(self.directory)
