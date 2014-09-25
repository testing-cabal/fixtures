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

from logging import StreamHandler, getLogger, INFO, Formatter

from testtools.compat import _u

from fixtures import Fixture
from fixtures._fixtures.streams import StringStream

__all__ = [
    'FakeLogger',
    'LoggerFixture',
    'LogHandler',
    ]


class LogHandler(Fixture):
    """Replace a logger's handlers."""

    def __init__(self, handler, name="", level=None, nuke_handlers=True):
        """Create a LogHandler fixture.

        :param handler: The handler to replace other handlers with.
            If nuke_handlers is False, then added as an extra handler.
        :param name: The name of the logger to replace. Defaults to "".
        :param level: The log level to set, defaults to not changing the level.
        :param nuke_handlers: If True remove all existing handles (prevents
            existing messages going to e.g. stdout). Defaults to True.
        """
        super(LogHandler, self).__init__()
        self.handler = handler
        self._name = name
        self._level = level
        self._nuke_handlers = nuke_handlers

    def setUp(self):
        super(LogHandler, self).setUp()
        logger = getLogger(self._name)
        if self._level:
            self.addCleanup(logger.setLevel, logger.level)
            logger.setLevel(self._level)
        if self._nuke_handlers:
            for handler in reversed(logger.handlers):
                self.addCleanup(logger.addHandler, handler)
                logger.removeHandler(handler)
        try:
            logger.addHandler(self.handler)
        finally:
            self.addCleanup(logger.removeHandler, self.handler)


class FakeLogger(Fixture):
    """Replace a logger and capture its output."""

    def __init__(self, name="", level=INFO, format=None, nuke_handlers=True):
        """Create a FakeLogger fixture.

        :param name: The name of the logger to replace. Defaults to "".
        :param level: The log level to set, defaults to INFO.
        :param format: Logging format to use. Defaults to capturing supplied
            messages verbatim.
        :param nuke_handlers: If True remove all existing handles (prevents
            existing messages going to e.g. stdout). Defaults to True.

        Example:

          def test_log(self)
              fixture = self.useFixture(LoggerFixture())
              logging.info('message')
              self.assertEqual('message', fixture.output)
        """
        super(FakeLogger, self).__init__()
        self._name = name
        self._level = level
        self._format = format
        self._nuke_handlers = nuke_handlers

    def setUp(self):
        super(FakeLogger, self).setUp()
        name = _u("pythonlogging:'%s'") % self._name
        output = self.useFixture(StringStream(name)).stream
        self._output = output
        handler = StreamHandler(output)
        if self._format:
            handler.setFormatter(Formatter(self._format))
        self.useFixture(
            LogHandler(handler, name=self._name, level=self._level,
                       nuke_handlers=self._nuke_handlers))

    @property
    def output(self):
        self._output.seek(0)
        return self._output.read()


LoggerFixture = FakeLogger
