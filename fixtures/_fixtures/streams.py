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
    "ByteStream",
    "DetailStream",
    "StringStream",
]

import io
from typing import Callable, Generic, IO, Tuple, TypeVar, Union

from fixtures import Fixture

# Type variable for the stream type
T = TypeVar("T", IO[bytes], IO[str])


class Stream(Generic[T], Fixture):
    """Expose a file-like object as a detail.

    :attr stream: The file-like object.
    """

    stream: T

    def __init__(
        self,
        detail_name: str,
        stream_factory: Callable[[], Tuple[T, Union[IO[bytes], IO[str]]]],
    ) -> None:
        """Create a ByteStream.

        :param detail_name: Use this as the name of the stream.
        :param stream_factory: Called to construct a pair of streams:
            (write_stream, content_stream).
        """
        self._detail_name = detail_name
        self._stream_factory: Callable[[], Tuple[T, Union[IO[bytes], IO[str]]]] = (
            stream_factory
        )

    def _setUp(self) -> None:
        # Available with the fixtures[streams] extra.
        from testtools.content import content_from_stream

        write_stream, read_stream = self._stream_factory()
        self.stream = write_stream
        self.addDetail(
            self._detail_name, content_from_stream(read_stream, seek_offset=0)
        )


def _byte_stream_factory() -> Tuple[IO[bytes], IO[bytes]]:
    result = io.BytesIO()
    return (result, result)


def ByteStream(detail_name: str) -> Stream[IO[bytes]]:
    """Provide a file-like object that accepts bytes and expose as a detail.

    :param detail_name: The name of the detail.
    :return: A fixture which has an attribute `stream` containing the file-like
        object.
    """
    return Stream(detail_name, _byte_stream_factory)


def _string_stream_factory() -> Tuple[IO[str], IO[bytes]]:
    lower = io.BytesIO()
    upper = io.TextIOWrapper(lower, encoding="utf8")
    # See http://bugs.python.org/issue7955
    upper._CHUNK_SIZE = 1  # type: ignore[attr-defined]
    return upper, lower


def StringStream(detail_name: str) -> Stream[IO[str]]:
    """Provide a file-like object that accepts strings and expose as a detail.

    :param detail_name: The name of the detail.
    :return: A fixture which has an attribute `stream` containing the file-like
        object.
    """
    return Stream(detail_name, _string_stream_factory)


def DetailStream(detail_name: str) -> Stream[IO[bytes]]:
    """Deprecated alias for ByteStream."""
    return ByteStream(detail_name)
