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

from __future__ import annotations

from logging import StreamHandler, getLogger, INFO, Formatter, Handler, LogRecord
import sys
from typing import IO, Optional, Type, TYPE_CHECKING

from fixtures import Fixture
from fixtures._fixtures.streams import StringStream

# Type alias for proper typing during type checking
if TYPE_CHECKING:
    StreamHandlerStr = StreamHandler[IO[str]]
else:
    StreamHandlerStr = StreamHandler

__all__ = [
    "FakeLogger",
    "LoggerFixture",
    "LogHandler",
]


class LogHandler(Fixture):
    """Replace a logger's handlers."""

    def __init__(
        self,
        handler: Handler,
        name: str = "",
        level: Optional[int] = None,
        nuke_handlers: bool = True,
    ) -> None:
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

    def _setUp(self) -> None:
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


class StreamHandlerRaiseException(StreamHandlerStr):
    """Handler class that will raise an exception on formatting errors."""

    def handleError(self, record: LogRecord) -> None:
        _, value, tb = sys.exc_info()
        if value is not None:
            raise value.with_traceback(tb)


class FakeLogger(Fixture):
    """Replace a logger and capture its output."""

    def __init__(
        self,
        name: str = "",
        level: int = INFO,
        format: Optional[str] = None,
        datefmt: Optional[str] = None,
        nuke_handlers: bool = True,
        formatter: Optional[Type[Formatter]] = None,
    ) -> None:
        """Create a FakeLogger fixture.

        :param name: The name of the logger to replace. Defaults to "".
        :param level: The log level to set, defaults to INFO.
        :param format: Logging format to use. Defaults to capturing supplied
            messages verbatim.
        :param datefmt: Logging date format to use.
            Mirrors the datefmt used in python loggging.
        :param nuke_handlers: If True remove all existing handles (prevents
            existing messages going to e.g. stdout). Defaults to True.
        :param formatter: a custom log formatter class. Use this if you want
            to use a log Formatter other than the default one in python.

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
        self._datefmt = datefmt
        self._nuke_handlers = nuke_handlers
        self._formatter = formatter

    def _setUp(self) -> None:
        name = "pythonlogging:'%s'" % self._name
        stream_fixture = self.useFixture(StringStream(name))
        output = stream_fixture.stream
        self._output: IO[str] = output
        handler = StreamHandlerRaiseException(output)
        if self._format:
            formatter = self._formatter or Formatter
            handler.setFormatter(formatter(self._format, self._datefmt))
        self.useFixture(
            LogHandler(
                handler,
                name=self._name,
                level=self._level,
                nuke_handlers=self._nuke_handlers,
            )
        )

    @property
    def output(self) -> str:
        self._output.seek(0)
        return self._output.read()

    def reset_output(self) -> None:
        self._output.truncate(0)


LoggerFixture = FakeLogger
