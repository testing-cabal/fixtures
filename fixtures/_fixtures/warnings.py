#  fixtures: Fixtures with cleanups for testing and convenience.
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

from __future__ import absolute_import

__all__ = [
    'WarningsCapture',
    ]

import warnings

import fixtures


class WarningsCapture(fixtures.Fixture):
    """A fixture context manager that copies and restores the warnings filter
       upon exiting the fixture.
    """

    def __init__(self):
        self._captures = []

    def clear(self):
        self._captures = []

    @property
    def captures(self):
        return self._captures

    def _showwarning(self, *args, **kwargs):
        msg = warnings.WarningMessage(*args, **kwargs)
        self._captures.append(msg)

    def setUp(self):
        super(WarningsCapture, self).setUp()
        patch = fixtures.MonkeyPatch("warnings.showwarning", self._showwarning)
        self.useFixture(patch)
