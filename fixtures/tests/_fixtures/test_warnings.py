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

import warnings

import testtools

import fixtures


class TestWarningsCapture(testtools.TestCase, fixtures.TestWithFixtures):

    def test_capture_reuse(self):
        # DeprecationWarnings are hidden by default in Python 3.2+, enable them
        # https://docs.python.org/3/library/warnings.html#default-warning-filter
        self.useFixture(fixtures.WarningsFilter())
        warnings.simplefilter("always")

        w = fixtures.WarningsCapture()
        with w:
            warnings.warn("test", DeprecationWarning)
            self.assertEqual(1, len(w.captures))
        with w:
            self.assertEqual([], w.captures)

    def test_capture_message(self):
        # DeprecationWarnings are hidden by default in Python 3.2+, enable them
        # https://docs.python.org/3/library/warnings.html#default-warning-filter
        self.useFixture(fixtures.WarningsFilter())
        warnings.simplefilter("always")

        w = self.useFixture(fixtures.WarningsCapture())
        warnings.warn("hi", DeprecationWarning)
        self.assertEqual(1, len(w.captures))
        self.assertEqual("hi", str(w.captures[0].message))

    def test_capture_category(self):
        # DeprecationWarnings are hidden by default in Python 3.2+, enable them
        # https://docs.python.org/3/library/warnings.html#default-warning-filter
        self.useFixture(fixtures.WarningsFilter())
        warnings.simplefilter("always")

        w = self.useFixture(fixtures.WarningsCapture())
        categories = [
            DeprecationWarning, Warning, UserWarning,
            SyntaxWarning, RuntimeWarning,
            UnicodeWarning, FutureWarning,
        ]
        for category in categories:
            warnings.warn("test", category)
        self.assertEqual(len(categories), len(w.captures))
        for i, category in enumerate(categories):
            c = w.captures[i]
            self.assertEqual(category, c.category)


class TestWarningsFilter(testtools.TestCase, fixtures.TestWithFixtures):

    def test_filter(self):
        fixture = fixtures.WarningsFilter(
            [
                {
                    'action': 'ignore',
                    'category': DeprecationWarning,
                },
                {
                    'action': 'once',
                    'category': UserWarning,
                },
            ],
        )
        self.useFixture(fixture)
        with warnings.catch_warnings(record=True) as w:
            warnings.warn('deprecated', DeprecationWarning)
            warnings.warn('user', UserWarning)

        # only the user warning should be present, and it should only have been
        # raised once
        self.assertEqual(1, len(w))

    def test_filters_restored(self):

        class CustomWarning(Warning):
            pass

        fixture = fixtures.WarningsFilter(
            [
                {
                    'action': 'once',
                    'category': CustomWarning,
                },
            ],
        )

        # we copy the filter values rather than a reference to the containing
        # list since that can change
        old_filters = warnings.filters[:]

        # NOTE: we intentionally do not use 'self.useFixture' since we want to
        # teardown the fixture manually here before we exit this test method
        with fixture:
            new_filters = warnings.filters[:]
            self.assertEqual(len(old_filters) + 1, len(new_filters))
            self.assertNotEqual(old_filters, new_filters)

        new_filters = warnings.filters[:]
        self.assertEqual(len(old_filters), len(new_filters))
        self.assertEqual(old_filters, new_filters)
