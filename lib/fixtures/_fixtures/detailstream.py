#  fixtures: Fixtures with cleanups for testing and convenience.
#
# Copyright (c) 2012, Robert Collins <robertc@robertcollins.net>
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

__all__ = [
    'DetailStream'
    ]

from cStringIO import StringIO

from fixtures import Fixture
import testtools


class DetailStream(Fixture):
    """Provide a file-like object and expose it as a detail.

    :attr stream: The file-like object.
    """

    def __init__(self, detail_name):
        """Create a DetailStream.

        :param detail_name: Use this as the name of the stream.
        """
        self._detail_name = detail_name

    def setUp(self):
        super(DetailStream, self).setUp()
        self.stream = StringIO()
        self.addDetail(self._detail_name,
            testtools.content.content_from_stream(self.stream, seek_offset=0))
