#  fixtures: Fixtures with cleanups for testing and convenience.
#
# Copyright (c) 2010, Robert Collins <robertc@robertcollins.net>
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
    """Replace a logger and restore it upon cleanup.

    :param name: Optionally, the name of the logger to replace.
    :param level: Optionally, the log level to set.
    :param format: Optionally, the format the logger should use.
    :param nuke_handlers: Optionally, whether to nuke existing handlers.

    Example:

      def test_log(self)
          fixture = self.useFixture(LoggerFixture())
          logging.info('message')
          self.assertEqual('message', fixture.output)
    """

    def __init__(self, name="", level=INFO, format="", nuke_handlers=True):
        super(LoggerFixture, self).__init__()
        self._name = name
        self._level = level
        self._format = format
        self._nuke_handlers = nuke_handlers
        self._old_handlers = []

    def setUp(self):
        super(LoggerFixture, self).setUp()
        self._output = StringIO()
        self._handler = StreamHandler(self._output)
        self._logger = getLogger(self._name) 
        if self._nuke_handlers:
            for handler in self._logger.handlers:
                self._logger.removeHandler(handler)
                self._old_handlers.append(handler)
        self._logger.addHandler(self._handler)

        if self._format:
            self._handler.setFormatter(Formatter(self._format))

        self._old_level = self._logger.level
        if self._level:
            self._logger.setLevel(self._level)

        self.addCleanup(self._logger.removeHandler, self._handler)
        self.addCleanup(self._logger.setLevel, self._old_level)

    def cleanUp(self):
        super(LoggerFixture, self).cleanUp()
        self._logger.removeHandler(self._handler)
        self._logger.setLevel(self._old_level)
        for handler in self._old_handlers:
            self._logger.addHandler(handler)        

    @property
    def output(self):
        return self._output.getvalue()
