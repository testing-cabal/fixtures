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
    'PythonPackage'
    ]

import os.path

from fixtures import Fixture
from fixtures._fixtures.tempdir import TempDir


class PythonPackage(Fixture):
    """Create a temporary Python package.

    :ivar base: The path of the directory containing the module. E.g. for a
        module 'foo', the path base + '/foo/__init__.py' would be the file path
        for the module.
    """

    def __init__(self, packagename, modulelist, init=True):
        """Create a PythonPackage.

        :param packagename: The name of the package to create - e.g.
            'toplevel.subpackage.'
        :param modulelist: List of modules to include in the package.
            Each module should be a tuple with the filename and content it
            should have.
        :param init: If false, do not create a missing __init__.py. When
            True, if modulelist does not include an __init__.py, an empty
            one is created.
        """
        self.packagename = packagename
        self.modulelist = modulelist
        self.init = init

    def _setUp(self):
        self.base = self.useFixture(TempDir()).path
        base = self.base
        root = os.path.join(base, self.packagename)
        os.mkdir(root)
        init_seen = not self.init
        for modulename, contents in self.modulelist:
            stream = open(os.path.join(root, modulename), 'wb')
            try:
                stream.write(contents)
            finally:
                stream.close()
            if modulename == '__init__.py':
                init_seen = True
        if not init_seen:
            open(os.path.join(root, '__init__.py'), 'wb').close()
