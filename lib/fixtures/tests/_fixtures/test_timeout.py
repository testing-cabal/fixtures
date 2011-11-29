#  fixtures: Fixtures with cleanups for testing and convenience.
#
# Copyright (C) 2011, Martin Pool <mbp@sourcefrog.net>
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

import os
import signal

import testtools
from testtools.testcase import (
    TestSkipped,
    )

import fixtures
from fixtures import EnvironmentVariableFixture, TestWithFixtures


class ExampleTests(testtools.TestCase, TestWithFixtures):
    """These are not intended to pass: they are sample data for the real tests"""

    def sample_timeout_passes(self):
        self.useFixture(fixtures.Timeout(100, gentle=True))
        pass  # Timeout shouldn't fire

    def sample_long_delay_with_timeout(self):
        self.useFixture(fixtures.Timeout(2, gentle=True))
        time.sleep(100)  # Expected to be killed here.

    def sample_long_delay_with_harsh_timeout(self):
        self.useFixture(fixtures.Timeout(2, gentle=False))
        time.sleep(100)  # Expected to be killed here.



class TestTimeout(testtools.TestCase, TestWithFixtures):

    def requireUnix(self):
        if getattr(signal, 'alarm', None) is None:
            raise TestSkipped("no alarm() function")

    def test_timeout_passes(self):
        # This can pass even on Windows - the test is skipped.
        test = ExampleTests('sample_timeout_passes')
        result = test.run()
        self.assertTrue(result.wasSuccessful())

    def test_timeout_gentle(self):
        self.requireUnix()
        test = ExampleTests('sample_long_delay_with_timeout')
        result = test.run()
        self.assertFalse(result.wasSuccessful())

    def test_timeout_harsh(self):
        self.requireUnix()
        test = ExampleTests('sample_long_delay_with_harsh_timeout')
        # This will normally kill the whole process, which would be
        # inconvenient.  Let's hook the alarm here so we can observe it.
        got_alarm = False
        def sigalrm_handler():
            got_alarm = True
        old_handler = signal.signal(signal.SIGALRM, sigalrm_handler)
        self.addCleanup(signal.signal, signal.SIGALRM, old_handler)
        result = test.run()
        self.assertFalse(result.wasSuccessful())
        self.assertTrue(got_alarm)
