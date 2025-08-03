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
    "WarningsCapture",
    "WarningsFilter",
]

import warnings
from typing import Any, Dict, List, Optional, cast

import fixtures
from fixtures._fixtures.monkeypatch import MonkeyPatch


class WarningsCapture(fixtures.Fixture):
    """Capture warnings.

    While ``WarningsCapture`` is active, warnings will be captured by
    the fixture (so that they can be later analyzed).

    :attribute captures: A list of warning capture ``WarningMessage`` objects.
    """

    captures: List[warnings.WarningMessage]

    def _showwarning(self, *args: Any, **kwargs: Any) -> None:
        self.captures.append(warnings.WarningMessage(*args, **kwargs))

    def _setUp(self) -> None:
        patch = MonkeyPatch("warnings.showwarning", self._showwarning)
        self.useFixture(patch)
        self.captures = []


class WarningsFilter(fixtures.Fixture):
    """Configure warnings filters.

    While ``WarningsFilter`` is active, warnings will be filtered per
    configuration.
    """

    def __init__(self, filters: Optional[List[Dict[str, Any]]] = None) -> None:
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

    def _setUp(self) -> None:
        self._original_warning_filters = list(warnings.filters)

        for filt in self.filters:
            warnings.filterwarnings(**filt)

        self.addCleanup(self._reset_warning_filters)

    def _reset_warning_filters(self) -> None:
        filters_list = cast(List[Any], warnings.filters)
        filters_list.clear()
        filters_list.extend(self._original_warning_filters)
