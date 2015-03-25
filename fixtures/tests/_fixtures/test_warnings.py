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


class TestWarnings(testtools.TestCase, fixtures.TestWithFixtures):

    def test_capture_reuse(self):
        w = fixtures.WarningsCapture()
        with w:
            warnings.warn("test", DeprecationWarning)
            self.assertEqual(1, len(w.captures))
        with w:
            self.assertEqual([], w.captures)

    def test_capture_message(self):
        w = self.useFixture(fixtures.WarningsCapture())
        warnings.warn("hi", DeprecationWarning)
        self.assertEqual(1, len(w.captures))
        self.assertEqual("hi", str(w.captures[0].message))

    def test_capture_category(self):
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
