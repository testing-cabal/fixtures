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
import sys
import time

import testtools
from testtools import TestCase
from testtools.compat import StringIO

from fixtures import (
    FakeLogger,
    LogHandler,
    TestWithFixtures,
    )


# A simple custom formatter that prepends Foo to all log messages, for
# testing formatter overrides.
class FooFormatter(logging.Formatter):
    def format(self, record):
        # custom formatters interface changes in python 3.2
        if sys.version_info < (3, 2):
            self._fmt = "Foo " + self._fmt
        else:
            self._style = logging.PercentStyle("Foo " + self._style._fmt)
            self._fmt = self._style._fmt
        return logging.Formatter.format(self, record)


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

    def test_custom_datefmt(self):
        fixture = FakeLogger(format="%(asctime)s %(module)s",
                             datefmt="%Y")
        self.useFixture(fixture)
        logging.info("message")
        self.assertEqual(
            time.strftime("%Y test_logger\n", time.localtime()),
            fixture.output)

    def test_custom_formatter(self):
        fixture = FakeLogger(format="%(asctime)s %(module)s",
                             formatter=FooFormatter,
                             datefmt="%Y")
        self.useFixture(fixture)
        logging.info("message")
        self.assertEqual(
            time.strftime("Foo %Y test_logger\n", time.localtime()),
            fixture.output)

    def test_logging_output_included_in_details(self):
        fixture = FakeLogger()
        detail_name = "pythonlogging:''"
        with fixture:
            content = fixture.getDetails()[detail_name]
            # Output after getDetails is called is included.
            logging.info('some message')
            self.assertEqual("some message\n", content.as_text())
        # The old content object returns the old usage after cleanUp (not
        # strictly needed but convenient). Note that no guarantee is made that
        # it will work after setUp is called again. [It does on Python 2.x, not
        # on 3.x]
        self.assertEqual("some message\n", content.as_text())
        with fixture:
            # A new one returns new output:
            self.assertEqual("", fixture.getDetails()[detail_name].as_text())
        # The original content object may either fail, or return the old
        # content (it must not have been reset..).
        try:
            self.assertEqual("some message\n", content.as_text())
        except AssertionError:
            raise
        except:
            pass

    def test_exceptionraised(self):
        with FakeLogger():
            with testtools.ExpectedException(TypeError):
                logging.info("Some message", "wrongarg")


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

    def test_replace_and_restore_handlers(self):
        stream = StringIO()
        logger = logging.getLogger()
        logger.addHandler(logging.StreamHandler(stream))
        logger.setLevel(logging.INFO)
        logging.info("one")
        fixture = LogHandler(self.CustomHandler())
        with fixture:
            logging.info("two")
        logging.info("three")
        self.assertEqual(["two"], fixture.handler.msgs)
        self.assertEqual("one\nthree\n", stream.getvalue())

    def test_preserving_existing_handlers(self):
        stream = StringIO()
        self.logger.addHandler(logging.StreamHandler(stream))
        self.logger.setLevel(logging.INFO)
        fixture = LogHandler(self.CustomHandler(), nuke_handlers=False)
        with fixture:
            logging.info("message")
        self.assertEqual(["message"], fixture.handler.msgs)
        self.assertEqual("message\n", stream.getvalue())

    def test_logging_level_restored(self):
        self.logger.setLevel(logging.DEBUG)
        fixture = LogHandler(self.CustomHandler(), level=logging.WARNING)
        with fixture:
            # The fixture won't capture this, because the DEBUG level
            # is lower than the WARNING one
            logging.debug("debug message")
            self.assertEqual(logging.WARNING, self.logger.level)
        self.assertEqual([], fixture.handler.msgs)
        self.assertEqual(logging.DEBUG, self.logger.level)
