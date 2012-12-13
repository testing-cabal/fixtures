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

from fixtures import (
    FakeLogger,
    LogHandler,
    TestWithFixtures,
    )
from fixtures._fixtures.logger import MementoHandler


class FakeLoggerTest(TestCase, TestWithFixtures):

    def setUp(self):
        super(FakeLoggerTest, self).setUp()
        self.logger = logging.getLogger()
        self.addCleanup(self.removeHandlers, self.logger)

    def removeHandlers(self, logger):
        for handler in logger.handlers:
            logger.removeHandler(handler)

    def test_output_property_has_output(self):
        fixture = self.useFixture(FakeLogger())
        logging.info("some message")
        self.assertEqual("some message\n", fixture.output)

    def test_replace_and_restore_handlers(self):
        stream = StringIO()
        logger = logging.getLogger()
        logger.addHandler(logging.StreamHandler(stream))
        logger.setLevel(logging.INFO)
        logging.info("one")
        fixture = FakeLogger()
        with fixture:
            logging.info("two")
        logging.info("three")
        self.assertEqual("two\n", fixture.output)
        self.assertEqual("one\nthree\n", stream.getvalue())

    def test_preserving_existing_handlers(self):
        stream = StringIO()
        self.logger.addHandler(logging.StreamHandler(stream))
        self.logger.setLevel(logging.INFO)
        fixture = FakeLogger(nuke_handlers=False)
        with fixture:
            logging.info("message")
        self.assertEqual("message\n", fixture.output)
        self.assertEqual("message\n", stream.getvalue())

    def test_logging_level_restored(self):
        self.logger.setLevel(logging.DEBUG)
        fixture = FakeLogger(level=logging.WARNING)
        with fixture:
            # The fixture won't capture this, because the DEBUG level
            # is lower than the WARNING one
            logging.debug("debug message")
            self.assertEqual(logging.WARNING, self.logger.level)
        self.assertEqual("", fixture.output)
        self.assertEqual(logging.DEBUG, self.logger.level)

    def test_custom_format(self):
        fixture = FakeLogger(format="%(module)s")
        self.useFixture(fixture)
        logging.info("message")
        self.assertEqual("test_logger\n", fixture.output)

    def test_logging_output_included_in_details(self):
        fixture = FakeLogger()
        detail_name = "pythonlogging:''"
        with fixture:
            content = fixture.getDetails()[detail_name]
            # Output after getDetails is called is included.
            logging.info('some message')
            self.assertEqual("some message\n", content.as_text())
        with fixture:
            # The old content object returns the old usage
            self.assertEqual("some message\n", content.as_text())
            # A new one returns the new output:
            self.assertEqual("", fixture.getDetails()[detail_name].as_text())


class TestMementoHandler(TestCase):

    class FakeRecord(object):
        def __init__(self, **kw):
            self.__dict__.update(kw)

    def test_initialy_no_records(self):
        handler = MementoHandler()
        self.assertEqual([], handler.records)

    def test_emit_stored_in_records(self):
        handler = MementoHandler()
        marker = self.FakeRecord(foo='bar')
        handler.emit(marker)
        self.assertEqual([{'foo': 'bar'}], handler.records)

    def test_is_log_handler(self):
        handler = MementoHandler()
        self.assertIsInstance(handler, logging.Handler)


class LogHandlerTest(TestCase, TestWithFixtures):

    class CustomHandler(logging.Handler):

        def __init__(self, *args, **kwargs):
            """Create the instance, and add a records attribute."""
            logging.Handler.__init__(self, *args, **kwargs)
            self.msgs = []

        def emit(self, record):
            self.msgs.append(record.msg)

    def setUp(self):
        super(LogHandlerTest, self).setUp()
        self.logger = logging.getLogger()
        self.addCleanup(self.removeHandlers, self.logger)

    def removeHandlers(self, logger):
        for handler in logger.handlers:
            logger.removeHandler(handler)

    def test_captures_logging(self):
        fixture = self.useFixture(LogHandler(self.CustomHandler()))
        logging.info("some message")
        self.assertEqual(["some message"], fixture.handler.msgs)
