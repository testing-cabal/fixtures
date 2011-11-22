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
        self.logger = logging.getLogger()
        self.addCleanup(self.removeHandlers, self.logger)

    def removeHandlers(self, logger):
        for handler in logger.handlers:
            logger.removeHandler(handler)

    def test_output_property_has_output(self):
        fixture = self.useFixture(LoggerFixture())
        logging.info("some message")
        self.assertEqual("some message\n", fixture.output)

    def test_replace_and_restore_handlers(self):
        stream = StringIO()
        logger = logging.getLogger()
        logger.addHandler(logging.StreamHandler(stream))
        logger.setLevel(logging.INFO)
        logging.info("one")
        fixture = LoggerFixture()
        with fixture:
            logging.info("two")
        logging.info("three")
        self.assertEqual("two\n", fixture.output)
        self.assertEqual("one\nthree\n", stream.getvalue())

    def test_preserving_existing_handlers(self):
        stream = StringIO()
        self.logger.addHandler(logging.StreamHandler(stream))
        self.logger.setLevel(logging.INFO)
        fixture = LoggerFixture(nuke_handlers=False)
        with fixture:
            logging.info("message")
        self.assertEqual("message\n", fixture.output)
        self.assertEqual("message\n", stream.getvalue())

    def test_logging_level_restored(self):
        self.logger.setLevel(logging.DEBUG)
        fixture = LoggerFixture(level=logging.WARNING)
        with fixture:
            # The fixture won't capture this, because the DEBUG level
            # is lower than the WARNING one
            logging.debug("debug message")
            self.assertEqual(logging.WARNING, self.logger.level)
        self.assertEqual("", fixture.output)
        self.assertEqual(logging.DEBUG, self.logger.level)

    def test_custom_format(self):
        fixture = LoggerFixture(format="%(module)s")
        self.useFixture(fixture)
        logging.info("message")
        self.assertEqual("test_logger\n", fixture.output)
