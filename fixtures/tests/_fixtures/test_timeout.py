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

import signal
import time

import testtools
from testtools.testcase import (
    TestSkipped,
    )
from testtools.matchers import raises

import fixtures


def sample_timeout_passes():
    with fixtures.Timeout(100, gentle=True):
        pass  # Timeout shouldn't fire

def sample_long_delay_with_gentle_timeout():
    with fixtures.Timeout(1, gentle=True):
        time.sleep(100)  # Expected to be killed here.

def sample_long_delay_with_harsh_timeout():
    with fixtures.Timeout(1, gentle=False):
        time.sleep(100)  # Expected to be killed here.


class TestTimeout(testtools.TestCase, fixtures.TestWithFixtures):

    def requireUnix(self):
        if getattr(signal, 'alarm', None) is None:
            raise TestSkipped("no alarm() function")

    def test_timeout_passes(self):
        # This can pass even on Windows - the test is skipped.
        sample_timeout_passes()

    def test_timeout_gentle(self):
        self.requireUnix()
        self.assertRaises(
            fixtures.TimeoutException,
            sample_long_delay_with_gentle_timeout)

    def test_timeout_harsh(self):
        self.requireUnix()
        # This will normally kill the whole process, which would be
        # inconvenient.  Let's hook the alarm here so we can observe it.
        class GotAlarm(Exception):pass
        def sigalrm_handler(signum, frame):
            raise GotAlarm()
        old_handler = signal.signal(signal.SIGALRM, sigalrm_handler)
        self.addCleanup(signal.signal, signal.SIGALRM, old_handler)
        self.assertThat(sample_long_delay_with_harsh_timeout, raises(GotAlarm))
