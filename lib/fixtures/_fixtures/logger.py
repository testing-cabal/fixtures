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
from cStringIO import StringIO

from fixtures import Fixture

__all__ = [
    'LoggerFixture',
    ]


class LoggerFixture(Fixture):
    """Replace a logger and capture it's output."""

    def __init__(self, name="", level=INFO, format=None, nuke_handlers=True):
        """Create a LoggerFixture.

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
        super(LoggerFixture, self).__init__()
        self._name = name
        self._level = level
        self._format = format
        self._nuke_handlers = nuke_handlers

    def setUp(self):
        super(LoggerFixture, self).setUp()
        self._output = StringIO()
        logger = getLogger(self._name) 
        if self._level:
            self.addCleanup(logger.setLevel, logger.level)
            logger.setLevel(self._level)
        if self._nuke_handlers:
            for handler in reversed(logger.handlers):
                logger.removeHandler(handler)
                self.addCleanup(logger.addHandler, handler)
        handler = StreamHandler(self._output)
        if self._format:
            handler.setFormatter(Formatter(self._format))
        try:
            logger.addHandler(handler)
        finally:
            self.addCleanup(logger.removeHandler, handler)

    @property
    def output(self):
        return self._output.getvalue()
