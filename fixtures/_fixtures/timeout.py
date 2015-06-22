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


"""Timeout fixture."""


import signal

import fixtures

__all__ = [
    'Timeout',
    'TimeoutException',
    ]


class TimeoutException(Exception):
    """Timeout expired"""


class Timeout(fixtures.Fixture):
    """Fixture that aborts the contained code after a number of seconds.

    The interrupt can be either gentle, in which case TimeoutException is
    raised, or not gentle, in which case the process will typically be aborted
    by SIGALRM.

    Cautions:
     * This has no effect on Windows.
     * Only one Timeout can be used at any time per process.
    """

    def __init__(self, timeout_secs, gentle):
        self.timeout_secs = timeout_secs
        self.alarm_fn = getattr(signal, 'alarm', None)
        self.gentle = gentle

    def signal_handler(self, signum, frame):
        raise TimeoutException()

    def _setUp(self):
        if self.alarm_fn is None:
            return  # Can't run on Windows
        if self.gentle:
            # Install a handler for SIGARLM so we can raise an exception rather
            # than the default handler executing, which kills the process.
            old_handler = signal.signal(signal.SIGALRM, self.signal_handler)
        # We add the slarm cleanup before the cleanup for the signal handler,
        # otherwise there is a race condition where the signal handler is
        # cleaned up but the alarm still fires.
        self.addCleanup(lambda: self.alarm_fn(0))
        self.alarm_fn(self.timeout_secs)
        if self.gentle:
            self.addCleanup(lambda: signal.signal(signal.SIGALRM, old_handler))
