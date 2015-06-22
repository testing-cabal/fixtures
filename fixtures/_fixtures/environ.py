#  fixtures: Fixtures with cleanups for testing and convenience.
#
# Copyright (c) 2010, 2011, Robert Collins <robertc@robertcollins.net>
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
    'EnvironmentVariable',
    'EnvironmentVariableFixture'
    ]

import os

from fixtures import Fixture


class EnvironmentVariable(Fixture):
    """Isolate a specific environment variable."""

    def __init__(self, varname, newvalue=None):
        """Create an EnvironmentVariable fixture.

        :param varname: the name of the variable to isolate.
        :param newvalue: A value to set the variable to. If None, the variable
            will be deleted.

        During setup the variable will be deleted or assigned the requested
        value, and this will be restored in cleanUp.
        """
        super(EnvironmentVariable, self).__init__()
        self.varname = varname
        self.newvalue = newvalue

    def _setUp(self):
        varname = self.varname
        orig_value = os.environ.get(varname)
        if orig_value is not None:
            self.addCleanup(os.environ.__setitem__, varname, orig_value)
            del os.environ[varname]
        else:
            self.addCleanup(os.environ.pop, varname, '')
        if self.newvalue is not None:
            os.environ[varname] = self.newvalue
        else:
            os.environ.pop(varname, '')


EnvironmentVariableFixture = EnvironmentVariable
