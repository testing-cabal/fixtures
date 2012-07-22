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

import fixtures

from testtools.matchers import Mismatch


class LoggingFixture(fixtures.Fixture):

    def __init__(self, suffix='', calls=None):
        super(LoggingFixture, self).__init__()
        if calls is None:
            calls = []
        self.calls = calls
        self.suffix = suffix

    def setUp(self):
        super(LoggingFixture, self).setUp()
        self.calls.append('setUp' + self.suffix)
        self.addCleanup(self.calls.append, 'cleanUp' + self.suffix)

    def reset(self):
        self.calls.append('reset' + self.suffix)


class HasNoAttribute(object):
    """For asserting that an object does not have a particular attribute."""

    def __init__(self, attr_name):
        self._attr_name = attr_name

    def __str__(self):
        return 'HasNoAttribute(%s)' % (self._attr_name,)

    def match(self, obj):
        sentinel = object()
        value = getattr(obj, self._attr_name, sentinel)
        if value is not sentinel:
            return Mismatch(
                "%s is an attribute of %r: %r" % (
                    self._attr_name, obj, value))
