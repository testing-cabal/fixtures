#  fixtures: Fixtures with cleanups for testing and convenience.
#
# Copyright (c) 2011, Robert Collins <robertc@robertcollins.net>
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

import logging

from testtools import TestCase
from cStringIO import StringIO

from fixtures import LoggerFixture, TestWithFixtures


class LoggerFixtureTest(TestCase, TestWithFixtures):

    def setUp(self):
        super(LoggerFixtureTest, self).setUp()
        # Silence the default sysout logger
        self.handler = logging.StreamHandler(StringIO())
        self.logger = logging.getLogger()
        self.logger.addHandler(self.handler)

    def tearDown(self):
        super(LoggerFixtureTest, self).tearDown()
        # Restore the default sysout logger
        self.logger.removeHandler(self.handler)

    def test_output(self):
        """The L{LoggerFixture.output} property returns the logging output."""
        fixture = LoggerFixture()
        self.useFixture(fixture)
        logging.info("some message")
        self.assertEqual("some message\n", fixture.output)

    def test_replace_and_restore_logger(self):
        """The logger is replaced upon setup and restored upon cleanup."""
        fixture = LoggerFixture()
        logging.info("first message")
        with fixture:
            logging.info("second message")
        logging.info("third message")
        self.assertEqual("second message\n", fixture.output)

    def test_restore_level(self):
        """The original logging level is restored at cleanup."""
        self.logger.setLevel(logging.DEBUG)
        fixture = LoggerFixture(level=logging.WARNING)
        with fixture:
            # The fixture won't capture this, because the DEBUG level
            # is lower than the WARNING one
            logging.debug("debug message")
        self.assertEqual("", fixture.output)

    def test_format(self):
        """It's possible to set an alternate format for the logger."""
        fixture = LoggerFixture(format="%(module)s")
        self.useFixture(fixture)
        logging.info("message")
        self.assertEqual("test_logger\n", fixture.output)
