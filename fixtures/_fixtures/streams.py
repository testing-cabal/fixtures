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
    'ByteStream',
    'DetailStream',
    'StringStream',
    ]

import io
import sys

from fixtures import Fixture
import testtools


class Stream(Fixture):
    """Expose a file-like object as a detail.

    :attr stream: The file-like object.
    """

    def __init__(self, detail_name, stream_factory):
        """Create a ByteStream.

        :param detail_name: Use this as the name of the stream.
        :param stream_factory: Called to construct a pair of streams:
            (write_stream, content_stream).
        """
        self._detail_name = detail_name
        self._stream_factory = stream_factory

    def _setUp(self):
        write_stream, read_stream = self._stream_factory()
        self.stream = write_stream
        self.addDetail(self._detail_name,
            testtools.content.content_from_stream(read_stream, seek_offset=0))


def _byte_stream_factory():
    result = io.BytesIO()
    return (result, result)


def ByteStream(detail_name):
    """Provide a file-like object that accepts bytes and expose as a detail.

    :param detail_name: The name of the detail.
    :return: A fixture which has an attribute `stream` containing the file-like
        object.
    """
    return Stream(detail_name, _byte_stream_factory)


def _string_stream_factory():
    lower = io.BytesIO()
    upper = io.TextIOWrapper(lower, encoding="utf8")
    # See http://bugs.python.org/issue7955
    upper._CHUNK_SIZE = 1
    # In theory, this is sufficient and correct, but on Python2,
    # upper.write(_b('foo")) will whinge louadly.
    if sys.version_info[0] < 3:
        upper_write = upper.write
        def safe_write(str_or_bytes):
            if type(str_or_bytes) is str:
                str_or_bytes = str_or_bytes.decode('utf8')
            return upper_write(str_or_bytes)
        upper.write = safe_write
    return upper, lower


def StringStream(detail_name):
    """Provide a file-like object that accepts strings and expose as a detail.

    :param detail_name: The name of the detail.
    :return: A fixture which has an attribute `stream` containing the file-like
        object.
    """
    return Stream(detail_name, _string_stream_factory)


def DetailStream(detail_name):
    """Deprecated alias for ByteStream."""
    return ByteStream(detail_name)
