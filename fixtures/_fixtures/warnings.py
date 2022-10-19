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

__all__ = [
    'WarningsCapture',
    'WarningsFilter',
]

import warnings

import fixtures


class WarningsCapture(fixtures.Fixture):
    """Capture warnings.

    While ``WarningsCapture`` is active, warnings will be captured by
    the fixture (so that they can be later analyzed).

    :attribute captures: A list of warning capture ``WarningMessage`` objects.
    """

    def _showwarning(self, *args, **kwargs):
        self.captures.append(warnings.WarningMessage(*args, **kwargs))

    def _setUp(self):
        patch = fixtures.MonkeyPatch("warnings.showwarning", self._showwarning)
        self.useFixture(patch)
        self.captures = []


class WarningsFilter(fixtures.Fixture):
    """Configure warnings filters.

    While ``WarningsFilter`` is active, warnings will be filtered per
    configuration.
    """

    def __init__(self, filters=None):
        """Create a WarningsFilter fixture.

        :param filters: An optional list of dictionaries with arguments
            corresponding to the arguments to
            :py:func:`warnings.filterwarnings`. For example::

                [
                    {
                        'action': 'ignore',
                        'message': 'foo',
                        'category': DeprecationWarning,
                    },
                ]

            Order is important: entries closer to the front of the list
            override entries later in the list, if both match a particular
            warning.

            Alternatively, you can configure warnings within the context of the
            fixture.

            See `the Python documentation`__ for more information.

        __: https://docs.python.org/3/library/warnings.html#the-warnings-filter
        """
        super().__init__()
        self.filters = filters or []

    def _setUp(self):
        self._original_warning_filters = warnings.filters[:]

        for filt in self.filters:
            warnings.filterwarnings(**filt)

        self.addCleanup(self._reset_warning_filters)

    def _reset_warning_filters(self):
        warnings.filters[:] = self._original_warning_filters
